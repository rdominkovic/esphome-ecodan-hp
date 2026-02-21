# ABOUTME: Analyzes overnight data from speed 3 period for COP and cycling comparison.
# ABOUTME: Run with: python scripts/analyze_overnight.py

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
    on_cycles = []
    off_cycles = []
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
            entry = {"start": state_start, "end": r["_ts"], "duration_min": round(duration, 1)}
            if current_state:
                on_cycles.append(entry)
            else:
                off_cycles.append(entry)
            current_state = state
            state_start = r["_ts"]
    if state_start and rows:
        duration = (rows[-1]["_ts"] - state_start).total_seconds() / 60
        entry = {"start": state_start, "end": rows[-1]["_ts"], "duration_min": round(duration, 1)}
        if current_state:
            on_cycles.append(entry)
        else:
            off_cycles.append(entry)
    return on_cycles, off_cycles


def stat(rows, key):
    vals = [r[key] for r in rows if r[key] is not None]
    if not vals:
        return None, None, None
    return min(vals), sum(vals) / len(vals), max(vals)


def analyze(rows, label):
    if not rows:
        return
    hours = (rows[-1]["_ts"] - rows[0]["_ts"]).total_seconds() / 3600

    print(f"\n{'=' * 65}")
    print(f"  {label}")
    print(f"  {rows[0]['timestamp']} -> {rows[-1]['timestamp']} ({hours:.1f}h, {len(rows)} readings)")
    print(f"{'=' * 65}")

    # Temps
    for key, name in [("outside_temp", "Outside"), ("feed_temp", "Feed"), ("return_temp", "Return"),
                       ("delta_t", "Delta T"), ("dhw_temp", "DHW tank")]:
        lo, avg, hi = stat(rows, key)
        if lo is not None:
            print(f"  {name:12s}: {lo:5.1f} / {avg:5.1f} / {hi:5.1f}  (min/avg/max)")

    # Pump & flow
    print()
    for key, name in [("pump_speed", "Pump speed"), ("pump_watts", "Pump watts"), ("flow_rate_lmin", "Flow rate")]:
        lo, avg, hi = stat(rows, key)
        if lo is not None:
            print(f"  {name:12s}: {lo:5.1f} / {avg:5.1f} / {hi:5.1f}")

    # Compressor
    on_rows = [r for r in rows if r["compressor_on"] == 1]
    pct = len(on_rows) / len(rows) * 100
    hz_on = [r["compressor_hz"] for r in on_rows if r["compressor_hz"] and r["compressor_hz"] > 0]
    print(f"\n  Compressor ON: {pct:.0f}%")
    if hz_on:
        print(f"  Frequency:  {min(hz_on):.0f} / {sum(hz_on)/len(hz_on):.0f} / {max(hz_on):.0f} Hz")

    on_cycles, off_cycles = count_cycles(rows)
    print(f"  ON cycles:  {len(on_cycles)}", end="")
    if on_cycles:
        durs = [c["duration_min"] for c in on_cycles]
        print(f"  ({min(durs):.0f} / {sum(durs)/len(durs):.0f} / {max(durs):.0f} min)")
        for c in on_cycles:
            print(f"    {c['start'].strftime('%H:%M')} - {c['end'].strftime('%H:%M')} ({c['duration_min']:.0f} min)")
    else:
        print()
    print(f"  OFF cycles: {len(off_cycles)}", end="")
    if off_cycles:
        durs = [c["duration_min"] for c in off_cycles]
        print(f"  ({min(durs):.0f} / {sum(durs)/len(durs):.0f} / {max(durs):.0f} min)")
        for c in off_cycles:
            print(f"    {c['start'].strftime('%H:%M')} - {c['end'].strftime('%H:%M')} ({c['duration_min']:.0f} min)")
    else:
        print()
    if hours > 0:
        print(f"  Starts/hour: {len(on_cycles) / hours:.2f}")

    # Heat delivery
    dt_on = [r["delta_t"] for r in on_rows if r["delta_t"] is not None and r["delta_t"] > 0]
    flow_on = [r["flow_rate_lmin"] for r in on_rows if r["flow_rate_lmin"] is not None]
    if dt_on and flow_on:
        avg_dt = sum(dt_on) / len(dt_on)
        avg_flow = sum(flow_on) / len(flow_on)
        kw = avg_flow * 4.186 * avg_dt / 60
        print(f"\n  Heat delivery: {kw:.1f} kW (flow {avg_flow:.0f} L/min x dT {avg_dt:.1f} C)")

    # COP
    print()
    ecop = [r["estimated_cop"] for r in rows if r["estimated_cop"] and r["estimated_cop"] > 0]
    if ecop:
        print(f"  Instant COP: {min(ecop):.2f} / {sum(ecop)/len(ecop):.2f} / {max(ecop):.2f}  ({len(ecop)} readings, {len(rows)-len(ecop)} zeros)")
    hcop_first = rows[0].get("heating_cop")
    hcop_last = rows[-1].get("heating_cop")
    dcop_first = rows[0].get("dhw_cop")
    dcop_last = rows[-1].get("dhw_cop")
    if hcop_first and hcop_last:
        print(f"  Heating COP: {hcop_first:.2f} -> {hcop_last:.2f}")
    if dcop_first and dcop_last:
        print(f"  DHW COP:     {dcop_first:.2f} -> {dcop_last:.2f}")

    # Energy from daily counters
    first, last = rows[0], rows[-1]
    hc0, hc1 = first.get("heating_consumed_kwh"), last.get("heating_consumed_kwh")
    hd0, hd1 = first.get("heating_delivered_kwh"), last.get("heating_delivered_kwh")
    dc0, dc1 = first.get("daily_consumed_kwh"), last.get("daily_consumed_kwh")
    dp0, dp1 = first.get("daily_produced_kwh"), last.get("daily_produced_kwh")
    if dc0 is not None and dc1 is not None:
        print(f"\n  Daily consumed:  {dc0:.1f} -> {dc1:.1f} kWh (delta: {dc1 - dc0:+.1f})")
    if dp0 is not None and dp1 is not None:
        print(f"  Daily produced:  {dp0:.1f} -> {dp1:.1f} kWh (delta: {dp1 - dp0:+.1f})")
        delta_c = dc1 - dc0
        delta_p = dp1 - dp0
        if delta_c > 0:
            print(f"  Period COP:      {delta_p / delta_c:.2f}")

    # DHW
    dhw_rows = [r for r in rows if r.get("3way_valve_dhw") == 1]
    if dhw_rows:
        print(f"\n  DHW active: {len(dhw_rows)} readings")


def main():
    rows = load_data()

    # Night 1: Speed 5, Feb 19 22:26 - Feb 20 05:51
    night1 = [r for r in rows if r["_ts"] >= datetime(2026, 2, 19, 22, 26) and r["_ts"] < datetime(2026, 2, 20, 5, 51)]

    # Night 2: Speed 3, Feb 20 22:00 - Feb 21 current
    night2 = [r for r in rows if r["_ts"] >= datetime(2026, 2, 20, 22, 0)]

    # Full day speed 3: Feb 20 19:05 onwards
    speed3_full = [r for r in rows if r["_ts"] >= datetime(2026, 2, 20, 19, 5)]

    # Today only (after midnight reset)
    today = [r for r in rows if r["_ts"] >= datetime(2026, 2, 21, 0, 0)]

    analyze(night1, "NIGHT 1: Speed 5 (Feb 19-20, baseline)")
    analyze(night2, "NIGHT 2: Speed 3 + thermo diff -7 (Feb 20-21)")

    if today:
        analyze(today, "TODAY Feb 21 (speed 3, clean daily counters)")

    # Side by side comparison
    print("\n" + "=" * 65)
    print("  OVERNIGHT COMPARISON: Speed 5 vs Speed 3")
    print("=" * 65)
    for label, n in [("Night 1 (Speed 5)", night1), ("Night 2 (Speed 3)", night2)]:
        if not n:
            continue
        hours = (n[-1]["_ts"] - n[0]["_ts"]).total_seconds() / 3600
        on_c, off_c = count_cycles(n)
        _, avg_out, _ = stat(n, "outside_temp")
        _, avg_dt, _ = stat(n, "delta_t")
        _, avg_pump, _ = stat(n, "pump_watts")
        _, avg_flow, _ = stat(n, "flow_rate_lmin")
        on_rows = [r for r in n if r["compressor_on"] == 1]
        hz_on = [r["compressor_hz"] for r in on_rows if r["compressor_hz"] and r["compressor_hz"] > 0]
        avg_hz = sum(hz_on) / len(hz_on) if hz_on else 0
        ecop = [r["estimated_cop"] for r in n if r["estimated_cop"] and r["estimated_cop"] > 0]
        avg_cop = sum(ecop) / len(ecop) if ecop else 0
        on_durs = [c["duration_min"] for c in on_c] if on_c else [0]
        off_durs = [c["duration_min"] for c in off_c] if off_c else [0]

        print(f"\n  {label} ({hours:.1f}h):")
        print(f"    Outside avg:  {avg_out:.0f} C")
        print(f"    Flow:         {avg_flow:.0f} L/min")
        print(f"    Pump watts:   {avg_pump:.0f} W")
        print(f"    Delta T avg:  {avg_dt:.1f} C")
        print(f"    Comp Hz avg:  {avg_hz:.0f}")
        print(f"    ON cycles:    {len(on_c)} (avg {sum(on_durs)/len(on_durs):.0f} min)")
        print(f"    OFF cycles:   {len(off_c)} (avg {sum(off_durs)/len(off_durs):.0f} min)")
        print(f"    Starts/hour:  {len(on_c)/hours:.2f}")
        print(f"    Inst COP avg: {avg_cop:.2f}")


if __name__ == "__main__":
    main()
