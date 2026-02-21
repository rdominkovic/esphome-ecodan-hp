# ABOUTME: Analyzes ecodan_log.csv to extract COP diagnostics, cycling patterns, and operating statistics.
# ABOUTME: Run with: python scripts/analyze_log.py

import csv
import os
from datetime import datetime, timedelta

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ecodan_log.csv")


def load_data():
    rows = []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_ts"] = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            for k in row:
                if k in ("timestamp", "_ts"):
                    continue
                try:
                    row[k] = float(row[k])
                except (ValueError, TypeError):
                    row[k] = None
            rows.append(row)
    return rows


def deduplicate(rows):
    """Remove duplicate entries from overlapping script instances."""
    seen = set()
    clean = []
    for r in rows:
        ts = r["timestamp"]
        if ts not in seen:
            seen.add(ts)
            clean.append(r)
    return clean


def analyze_cycles(rows):
    """Analyze compressor on/off cycles."""
    cycles = []
    current_state = None
    state_start = None

    for r in rows:
        state = int(r["compressor_on"]) if r["compressor_on"] is not None else 0
        if current_state is None:
            current_state = state
            state_start = r["_ts"]
            continue
        if state != current_state:
            duration = (r["_ts"] - state_start).total_seconds() / 60
            cycles.append({
                "state": "ON" if current_state else "OFF",
                "start": state_start,
                "end": r["_ts"],
                "duration_min": round(duration, 1),
            })
            current_state = state
            state_start = r["_ts"]

    # Close last cycle
    if state_start and rows:
        duration = (rows[-1]["_ts"] - state_start).total_seconds() / 60
        cycles.append({
            "state": "ON" if current_state else "OFF",
            "start": state_start,
            "end": rows[-1]["_ts"],
            "duration_min": round(duration, 1),
        })

    return cycles


def analyze_dhw(rows):
    """Analyze DHW (3-way valve) activity."""
    dhw_periods = []
    current_state = None
    state_start = None

    for r in rows:
        state = int(r["3way_valve_dhw"]) if r["3way_valve_dhw"] is not None else 0
        if current_state is None:
            current_state = state
            state_start = r["_ts"]
            continue
        if state != current_state:
            if current_state == 1:
                duration = (r["_ts"] - state_start).total_seconds() / 60
                dhw_periods.append({
                    "start": state_start,
                    "end": r["_ts"],
                    "duration_min": round(duration, 1),
                })
            current_state = state
            state_start = r["_ts"]

    return dhw_periods


def analyze_defrost(rows):
    """Analyze defrost cycles."""
    defrost_periods = []
    current_state = None
    state_start = None

    for r in rows:
        state = int(r["defrost"]) if r["defrost"] is not None else 0
        if current_state is None:
            current_state = state
            state_start = r["_ts"]
            continue
        if state != current_state:
            if current_state == 1:
                duration = (r["_ts"] - state_start).total_seconds() / 60
                defrost_periods.append({
                    "start": state_start,
                    "end": r["_ts"],
                    "duration_min": round(duration, 1),
                })
            current_state = state
            state_start = r["_ts"]

    return defrost_periods


def print_report(rows):
    rows = deduplicate(rows)
    rows.sort(key=lambda r: r["_ts"])

    total_hours = (rows[-1]["_ts"] - rows[0]["_ts"]).total_seconds() / 3600

    print("=" * 70)
    print("ECODAN HEAT PUMP LOG ANALYSIS")
    print("=" * 70)
    print(f"Period: {rows[0]['timestamp']} to {rows[-1]['timestamp']}")
    print(f"Duration: {total_hours:.1f} hours ({len(rows)} readings)")
    print()

    # Temperature summary
    print("-" * 70)
    print("TEMPERATURE SUMMARY")
    print("-" * 70)
    temps = {
        "outside_temp": "Outside",
        "feed_temp": "Feed",
        "return_temp": "Return",
        "dhw_temp": "DHW Tank",
        "delta_t": "Delta T",
        "discharge_temp": "Discharge",
        "condensing_temp": "Condensing",
    }
    for key, label in temps.items():
        vals = [r[key] for r in rows if r[key] is not None]
        if vals:
            print(f"  {label:15s}: min={min(vals):6.1f}  avg={sum(vals)/len(vals):6.1f}  max={max(vals):6.1f}")
    print()

    # Compressor stats
    print("-" * 70)
    print("COMPRESSOR STATISTICS")
    print("-" * 70)
    on_rows = [r for r in rows if r["compressor_on"] == 1]
    off_rows = [r for r in rows if r["compressor_on"] == 0]
    hz_vals = [r["compressor_hz"] for r in on_rows if r["compressor_hz"] is not None and r["compressor_hz"] > 0]

    pct_on = len(on_rows) / len(rows) * 100 if rows else 0
    print(f"  Compressor ON:  {len(on_rows)} readings ({pct_on:.0f}% of time)")
    print(f"  Compressor OFF: {len(off_rows)} readings ({100-pct_on:.0f}% of time)")
    if hz_vals:
        print(f"  Frequency (when ON): min={min(hz_vals):.0f} Hz  avg={sum(hz_vals)/len(hz_vals):.0f} Hz  max={max(hz_vals):.0f} Hz")

    # Cycles
    cycles = analyze_cycles(rows)
    on_cycles = [c for c in cycles if c["state"] == "ON"]
    off_cycles = [c for c in cycles if c["state"] == "OFF"]
    print(f"\n  ON cycles:  {len(on_cycles)}")
    for c in on_cycles:
        print(f"    {c['start'].strftime('%H:%M')} - {c['end'].strftime('%H:%M')} ({c['duration_min']:.0f} min)")
    print(f"\n  OFF cycles: {len(off_cycles)}")
    for c in off_cycles:
        print(f"    {c['start'].strftime('%H:%M')} - {c['end'].strftime('%H:%M')} ({c['duration_min']:.0f} min)")

    if on_cycles:
        on_durations = [c["duration_min"] for c in on_cycles]
        print(f"\n  ON cycle duration:  min={min(on_durations):.0f} min  avg={sum(on_durations)/len(on_durations):.0f} min  max={max(on_durations):.0f} min")
    if off_cycles:
        off_durations = [c["duration_min"] for c in off_cycles]
        print(f"  OFF cycle duration: min={min(off_durations):.0f} min  avg={sum(off_durations)/len(off_durations):.0f} min  max={max(off_durations):.0f} min")

    starts_per_hour = len(on_cycles) / total_hours if total_hours > 0 else 0
    print(f"  Starts per hour: {starts_per_hour:.2f}")
    print()

    # DHW
    print("-" * 70)
    print("DHW (DOMESTIC HOT WATER)")
    print("-" * 70)
    dhw_periods = analyze_dhw(rows)
    dhw_rows = [r for r in rows if r["3way_valve_dhw"] == 1]
    pct_dhw = len(dhw_rows) / len(rows) * 100 if rows else 0
    print(f"  DHW mode: {len(dhw_rows)} readings ({pct_dhw:.0f}% of time)")
    print(f"  DHW cycles: {len(dhw_periods)}")
    for p in dhw_periods:
        print(f"    {p['start'].strftime('%H:%M')} - {p['end'].strftime('%H:%M')} ({p['duration_min']:.0f} min)")
    dhw_temps = [r["dhw_temp"] for r in rows if r["dhw_temp"] is not None]
    if dhw_temps:
        print(f"  DHW temp: min={min(dhw_temps):.1f}  avg={sum(dhw_temps)/len(dhw_temps):.1f}  max={max(dhw_temps):.1f}")
    print()

    # Defrost
    print("-" * 70)
    print("DEFROST")
    print("-" * 70)
    defrost_periods = analyze_defrost(rows)
    defrost_rows = [r for r in rows if r["defrost"] == 1]
    print(f"  Defrost events: {len(defrost_periods)}")
    for p in defrost_periods:
        print(f"    {p['start'].strftime('%H:%M')} - {p['end'].strftime('%H:%M')} ({p['duration_min']:.0f} min)")
    if not defrost_periods:
        print(f"  No defrost cycles detected")
    print()

    # Energy
    print("-" * 70)
    print("ENERGY (cumulative counters)")
    print("-" * 70)
    first, last = rows[0], rows[-1]
    energy_keys = [
        ("heating_consumed_kwh", "Heating consumed"),
        ("heating_delivered_kwh", "Heating delivered"),
        ("dhw_consumed_kwh", "DHW consumed"),
        ("dhw_delivered_kwh", "DHW delivered"),
        ("daily_consumed_kwh", "Daily consumed"),
        ("daily_produced_kwh", "Daily produced"),
    ]
    for key, label in energy_keys:
        v0 = first[key]
        v1 = last[key]
        if v0 is not None and v1 is not None:
            delta = v1 - v0
            print(f"  {label:20s}: {v0:8.2f} -> {v1:8.2f}  (delta: {delta:+.2f} kWh)")

    # COP from energy deltas
    htg_consumed = (last["heating_consumed_kwh"] or 0) - (first["heating_consumed_kwh"] or 0)
    htg_delivered = (last["heating_delivered_kwh"] or 0) - (first["heating_delivered_kwh"] or 0)
    dhw_consumed = (last["dhw_consumed_kwh"] or 0) - (first["dhw_consumed_kwh"] or 0)
    dhw_delivered = (last["dhw_delivered_kwh"] or 0) - (first["dhw_delivered_kwh"] or 0)

    print()
    if htg_consumed > 0:
        print(f"  Heating COP (this period): {htg_delivered / htg_consumed:.2f}")
    if dhw_consumed > 0:
        print(f"  DHW COP (this period):     {dhw_delivered / dhw_consumed:.2f}")
    total_consumed = htg_consumed + dhw_consumed
    total_delivered = htg_delivered + dhw_delivered
    if total_consumed > 0:
        print(f"  Overall COP (this period): {total_delivered / total_consumed:.2f}")
    print()

    # COP sensor values
    print("-" * 70)
    print("COP SENSOR VALUES")
    print("-" * 70)
    cop_keys = [
        ("estimated_cop", "Instantaneous COP"),
        ("heating_cop", "Heating COP (cumulative)"),
        ("dhw_cop", "DHW COP (cumulative)"),
    ]
    for key, label in cop_keys:
        vals = [r[key] for r in rows if r[key] is not None]
        if vals:
            nonzero = [v for v in vals if v > 0]
            if nonzero:
                print(f"  {label:30s}: min={min(nonzero):6.2f}  avg={sum(nonzero)/len(nonzero):6.2f}  max={max(nonzero):6.2f}  (zero readings: {len(vals)-len(nonzero)})")
            else:
                print(f"  {label:30s}: all zero ({len(vals)} readings)")
    print()

    # Flow rate and power
    print("-" * 70)
    print("FLOW & POWER")
    print("-" * 70)
    flow_vals = [r["flow_rate_lmin"] for r in rows if r["flow_rate_lmin"] is not None]
    if flow_vals:
        print(f"  Flow rate: min={min(flow_vals):.0f}  avg={sum(flow_vals)/len(flow_vals):.0f}  max={max(flow_vals):.0f} L/min")
    power_vals = [r["output_power_kw"] for r in on_rows if r["output_power_kw"] is not None and r["output_power_kw"] > 0]
    if power_vals:
        print(f"  Output power (when ON): min={min(power_vals):.1f}  avg={sum(power_vals)/len(power_vals):.1f}  max={max(power_vals):.1f} kW")
    est_power = [r["estimated_power_kw"] for r in on_rows if r["estimated_power_kw"] is not None and r["estimated_power_kw"] > 0]
    if est_power:
        print(f"  Est. power (when ON):   min={min(est_power):.1f}  avg={sum(est_power)/len(est_power):.1f}  max={max(est_power):.1f} kW")
    pump_watts = [r["pump_watts"] for r in rows if r["pump_watts"] is not None]
    if pump_watts:
        print(f"  Pump consumption: min={min(pump_watts):.0f}  avg={sum(pump_watts)/len(pump_watts):.0f}  max={max(pump_watts):.0f} W")
    print()

    # Compressor starts counter
    print("-" * 70)
    print("LIFETIME COUNTERS")
    print("-" * 70)
    starts_first = first.get("compressor_starts")
    starts_last = last.get("compressor_starts")
    hours_first = first.get("operating_hours")
    hours_last = last.get("operating_hours")
    if starts_first is not None and starts_last is not None:
        print(f"  Compressor starts: {starts_first:.0f} -> {starts_last:.0f}  (delta: {starts_last-starts_first:+.0f})")
    if hours_first is not None and hours_last is not None:
        print(f"  Operating hours:   {hours_first:.0f} -> {hours_last:.0f}  (delta: {hours_last-hours_first:+.0f})")
    if starts_last and hours_last:
        print(f"  Lifetime avg: {starts_last/hours_last:.2f} starts/hour")
    print()


if __name__ == "__main__":
    rows = load_data()
    print_report(rows)
