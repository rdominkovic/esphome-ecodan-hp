# ABOUTME: Compares heat pump performance before and after pump speed change.
# ABOUTME: Run with: python scripts/analyze_periods.py

import csv
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ecodan_log.csv")


def load_data():
    rows = []
    seen = set()
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["timestamp"] in seen:
                continue
            seen.add(row["timestamp"])
            row["_ts"] = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            for k in row:
                if k in ("timestamp", "_ts"):
                    continue
                try:
                    row[k] = float(row[k])
                except (ValueError, TypeError):
                    row[k] = None
            rows.append(row)
    rows.sort(key=lambda r: r["_ts"])
    return rows


def count_cycles(rows):
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
            cycles.append({"state": "ON" if current_state else "OFF", "duration_min": round(duration, 1)})
            current_state = state
            state_start = r["_ts"]
    if state_start and rows:
        duration = (rows[-1]["_ts"] - state_start).total_seconds() / 60
        cycles.append({"state": "ON" if current_state else "OFF", "duration_min": round(duration, 1)})
    return cycles


def analyze_period(rows, label):
    if not rows:
        print(f"  No data for {label}")
        return

    hours = (rows[-1]["_ts"] - rows[0]["_ts"]).total_seconds() / 3600
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  {rows[0]['timestamp']} to {rows[-1]['timestamp']} ({hours:.1f}h, {len(rows)} readings)")
    print(f"{'='*60}")

    # Temps
    def stat(key):
        vals = [r[key] for r in rows if r[key] is not None]
        if not vals:
            return "N/A"
        return f"min={min(vals):.1f}  avg={sum(vals)/len(vals):.1f}  max={max(vals):.1f}"

    print(f"\n  Outside:    {stat('outside_temp')}")
    print(f"  Feed:       {stat('feed_temp')}")
    print(f"  Return:     {stat('return_temp')}")
    print(f"  Delta T:    {stat('delta_t')}")
    print(f"  DHW tank:   {stat('dhw_temp')}")

    # Pump
    pump_speeds = [r["pump_speed"] for r in rows if r["pump_speed"] is not None]
    pump_watts = [r["pump_watts"] for r in rows if r["pump_watts"] is not None]
    flows = [r["flow_rate_lmin"] for r in rows if r["flow_rate_lmin"] is not None]
    print(f"\n  Pump speed: {stat('pump_speed')}")
    print(f"  Pump watts: {stat('pump_watts')}")
    print(f"  Flow rate:  {stat('flow_rate_lmin')}")

    # Compressor
    on_rows = [r for r in rows if r["compressor_on"] == 1]
    hz_on = [r["compressor_hz"] for r in on_rows if r["compressor_hz"] and r["compressor_hz"] > 0]
    pct = len(on_rows) / len(rows) * 100
    print(f"\n  Compressor ON: {pct:.0f}% of time")
    if hz_on:
        print(f"  Frequency (ON): min={min(hz_on):.0f}  avg={sum(hz_on)/len(hz_on):.0f}  max={max(hz_on):.0f} Hz")

    cycles = count_cycles(rows)
    on_cycles = [c for c in cycles if c["state"] == "ON"]
    off_cycles = [c for c in cycles if c["state"] == "OFF"]
    print(f"  ON cycles: {len(on_cycles)}", end="")
    if on_cycles:
        durs = [c["duration_min"] for c in on_cycles]
        print(f"  (min={min(durs):.0f}  avg={sum(durs)/len(durs):.0f}  max={max(durs):.0f} min)")
    else:
        print()
    print(f"  OFF cycles: {len(off_cycles)}", end="")
    if off_cycles:
        durs = [c["duration_min"] for c in off_cycles]
        print(f"  (min={min(durs):.0f}  avg={sum(durs)/len(durs):.0f}  max={max(durs):.0f} min)")
    else:
        print()

    if hours > 0:
        print(f"  Starts/hour: {len(on_cycles)/hours:.2f}")

    # Estimated heat delivery
    dt_vals = [r["delta_t"] for r in on_rows if r["delta_t"] is not None and r["delta_t"] > 0]
    flow_on = [r["flow_rate_lmin"] for r in on_rows if r["flow_rate_lmin"] is not None]
    if dt_vals and flow_on:
        avg_dt = sum(dt_vals) / len(dt_vals)
        avg_flow = sum(flow_on) / len(flow_on)
        heat_kw = avg_flow * 4.186 * avg_dt / 60
        print(f"\n  Avg heat delivery (when ON): {heat_kw:.1f} kW")
        print(f"    (flow {avg_flow:.0f} L/min x dT {avg_dt:.1f}°C)")

    # COP
    cop_vals = [r["estimated_cop"] for r in rows if r["estimated_cop"] is not None and r["estimated_cop"] > 0]
    hcop_vals = [r["heating_cop"] for r in rows if r["heating_cop"] is not None and r["heating_cop"] > 0]
    if cop_vals:
        print(f"\n  Instantaneous COP: min={min(cop_vals):.2f}  avg={sum(cop_vals)/len(cop_vals):.2f}  max={max(cop_vals):.2f}")
    if hcop_vals:
        print(f"  Heating COP (cum): {hcop_vals[0]:.2f} -> {hcop_vals[-1]:.2f}")


def main():
    rows = load_data()

    # Split at pump speed change (05:51 on Feb 20)
    cutoff = datetime(2026, 2, 20, 5, 51, 0)

    speed5 = [r for r in rows if r["_ts"] < cutoff]
    speed4 = [r for r in rows if r["_ts"] >= cutoff]

    print("COMPARISON: Pump Speed 5 vs Speed 4")

    analyze_period(speed5, "PUMP SPEED 5 (overnight)")
    analyze_period(speed4, "PUMP SPEED 4 (after change)")

    # Also split speed 4 into night vs day by outside temp
    if speed4:
        morning = [r for r in speed4 if r["_ts"] < datetime(2026, 2, 20, 9, 0, 0)]
        daytime = [r for r in speed4 if r["_ts"] >= datetime(2026, 2, 20, 9, 0, 0)]
        if morning:
            analyze_period(morning, "SPEED 4 - Early morning (05:51-09:00)")
        if daytime:
            analyze_period(daytime, "SPEED 4 - Daytime (09:00+, colder outside)")


if __name__ == "__main__":
    main()
