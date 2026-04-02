# ABOUTME: Generates overnight heating performance report from CSV log data.
# ABOUTME: Analyzes compressor cycles, Hz profiles, COP, and AA mode breakdown.

import csv
import sys
from datetime import datetime, timedelta
from collections import defaultdict

CSV_PATH = "/opt/ecodan/data/ecodan_log.csv"

COL = {}  # populated from CSV header at load time


def parse_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, IndexError):
        return default


def parse_int(val, default=0):
    try:
        return int(float(val))
    except (ValueError, IndexError):
        return default


def load_period(csv_path, start_dt, end_dt):
    """Load CSV rows within the given time window."""
    rows = []
    start_str = start_dt.strftime("%Y-%m-%d %H:")
    end_str = end_dt.strftime("%Y-%m-%d %H:")
    # Pre-filter by date strings to avoid parsing every row
    date_prefixes = set()
    d = start_dt.date()
    end_d = end_dt.date()
    while d <= end_d:
        date_prefixes.add(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)

    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header and not COL:
            for i, name in enumerate(header):
                COL[name.strip()] = i
        for row in reader:
            if not row or len(row) < 45:
                continue
            ts_str = row[0]
            if ts_str[:10] not in date_prefixes:
                continue
            try:
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if start_dt <= ts <= end_dt:
                rows.append(row)
    return rows


def analyze_night(rows):
    """Break rows into compressor cycles and compute per-cycle stats."""
    cycles = []
    current_cycle = None
    prev_comp = None

    for row in rows:
        comp_on = parse_int(row[COL["compressor_on"]])
        dhw = parse_int(row[COL["3way_valve_dhw"]])
        hz = parse_float(row[COL["compressor_hz"]])
        feed = parse_float(row[COL["feed_temp"]])
        ret = parse_float(row[COL["return_temp"]])
        target = parse_float(row[COL["flow_target_temp"]])
        ot = parse_float(row[COL["outside_temp"]])
        cop = parse_float(row[COL["estimated_cop"]])
        power_in = parse_float(row[COL["estimated_power_kw"]])
        aa_mode = parse_float(row[COL["aa_control_mode"]])
        room = parse_float(row[COL["room_temp"]])
        ts_str = row[0]

        if prev_comp is not None and comp_on == 1 and prev_comp == 0:
            # Compressor start — new cycle
            current_cycle = {
                "start": ts_str, "end": None,
                "hz_values": [], "cop_values": [], "power_values": [],
                "feed_values": [], "target_values": [],
                "mode_minutes": defaultdict(int),
                "ot_values": [], "room_start": room, "room_end": room,
                "is_dhw": False, "samples": 0,
            }
            cycles.append(current_cycle)

        if current_cycle is not None and comp_on == 1:
            current_cycle["samples"] += 1
            current_cycle["end"] = ts_str
            current_cycle["room_end"] = room
            if hz > 0:
                current_cycle["hz_values"].append(hz)
            if cop > 0 and power_in > 0:
                current_cycle["cop_values"].append(cop)
            if power_in > 0:
                current_cycle["power_values"].append(power_in)
            current_cycle["feed_values"].append(feed)
            current_cycle["target_values"].append(target)
            current_cycle["ot_values"].append(ot)
            mode_key = int(round(aa_mode))
            current_cycle["mode_minutes"][mode_key] += 1
            if dhw:
                current_cycle["is_dhw"] = True

        if prev_comp is not None and comp_on == 0 and prev_comp == 1:
            if current_cycle is not None:
                current_cycle["end"] = ts_str
            current_cycle = None

        prev_comp = comp_on

    return cycles


def cycle_duration_min(cycle):
    try:
        t1 = datetime.strptime(cycle["start"], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(cycle["end"], "%Y-%m-%d %H:%M:%S")
        return (t2 - t1).total_seconds() / 60
    except (ValueError, TypeError):
        return 0


def print_report(date_str, cycles):
    heating_cycles = [c for c in cycles if not c["is_dhw"]]
    dhw_cycles = [c for c in cycles if c["is_dhw"]]

    print(f"{'=' * 100}")
    print(f"  OVERNIGHT REPORT: {date_str}  (22:00 - 08:00)")
    print(f"{'=' * 100}")

    # Summary
    durations = [cycle_duration_min(c) for c in heating_cycles if cycle_duration_min(c) > 0]
    all_hz = [h for c in heating_cycles for h in c["hz_values"]]
    all_cop = [v for c in heating_cycles for v in c["cop_values"]]
    all_ot = [v for c in heating_cycles for v in c["ot_values"]]
    mode_totals = defaultdict(int)
    for c in heating_cycles:
        for mode, mins in c["mode_minutes"].items():
            mode_totals[mode] += mins

    print(f"\n  Heating cycles: {len(heating_cycles)}    DHW cycles: {len(dhw_cycles)}")
    if durations:
        print(f"  Run duration:   min {min(durations):.0f} min, max {max(durations):.0f} min, avg {sum(durations)/len(durations):.0f} min, total {sum(durations):.0f} min")
    if all_hz:
        print(f"  Compressor Hz:  min {min(all_hz):.0f}, max {max(all_hz):.0f}, avg {sum(all_hz)/len(all_hz):.0f}")
    if all_cop:
        print(f"  Estimated COP:  min {min(all_cop):.1f}, max {max(all_cop):.1f}, avg {sum(all_cop)/len(all_cop):.1f}")
    if all_ot:
        print(f"  Outside temp:   min {min(all_ot):.0f}, max {max(all_ot):.0f}, avg {sum(all_ot)/len(all_ot):.0f} C")

    # AA Mode breakdown
    mode_names = {0: "Off", 1: "Mode 1 (heat)", 2: "Mode 2 (above target)", 3: "Mode 3 (suppress)",
                  4: "Mode 4 (defrost ramp)", 5: "Mode 5 (suppress ramp)", 6: "Mode 6 (startup ramp)"}
    if mode_totals:
        total_mins = sum(mode_totals.values())
        print(f"\n  AA Mode Breakdown ({total_mins} min total):")
        for mode in sorted(mode_totals.keys()):
            mins = mode_totals[mode]
            pct = 100 * mins / total_mins if total_mins > 0 else 0
            name = mode_names.get(mode, f"Mode {mode}")
            print(f"    {name:<30s} {mins:>4d} min  ({pct:>4.0f}%)")

    # Per-cycle detail
    print(f"\n  {'─' * 96}")
    print(f"  {'#':>2}  {'Start':<20} {'Dur':>5} {'AvgHz':>5} {'MaxHz':>5} {'AvgCOP':>6} {'Feed':>5} {'SP':>5} {'OT':>4} {'Room':>5}  Modes")
    print(f"  {'─' * 96}")

    for i, c in enumerate(heating_cycles):
        dur = cycle_duration_min(c)
        avg_hz = sum(c["hz_values"]) / len(c["hz_values"]) if c["hz_values"] else 0
        max_hz = max(c["hz_values"]) if c["hz_values"] else 0
        avg_cop = sum(c["cop_values"]) / len(c["cop_values"]) if c["cop_values"] else 0
        avg_feed = sum(c["feed_values"]) / len(c["feed_values"]) if c["feed_values"] else 0
        avg_target = sum(c["target_values"]) / len(c["target_values"]) if c["target_values"] else 0
        avg_ot = sum(c["ot_values"]) / len(c["ot_values"]) if c["ot_values"] else 0
        modes_str = " ".join(f"M{m}:{n}m" for m, n in sorted(c["mode_minutes"].items()))
        print(f"  {i+1:>2}  {c['start']:<20} {dur:>4.0f}m {avg_hz:>5.0f} {max_hz:>5.0f} {avg_cop:>6.1f} {avg_feed:>5.1f} {avg_target:>5.1f} {avg_ot:>4.0f} {c['room_end']:>5.1f}  {modes_str}")

    if dhw_cycles:
        print(f"\n  DHW Cycles:")
        for i, c in enumerate(dhw_cycles):
            dur = cycle_duration_min(c)
            avg_hz = sum(c["hz_values"]) / len(c["hz_values"]) if c["hz_values"] else 0
            print(f"    {c['start']} - {dur:.0f} min, avg Hz {avg_hz:.0f}")

    print(f"\n{'=' * 100}")


def main():
    # Default: last night (yesterday 22:00 to today 08:00)
    if len(sys.argv) > 1:
        try:
            ref_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        except ValueError:
            print(f"Usage: {sys.argv[0]} [YYYY-MM-DD]  (date of the evening start)")
            sys.exit(1)
    else:
        now = datetime.now()
        if now.hour < 12:
            ref_date = now - timedelta(days=1)
        else:
            ref_date = now
        ref_date = ref_date.replace(hour=0, minute=0, second=0, microsecond=0)

    start_dt = ref_date.replace(hour=22, minute=0, second=0)
    end_dt = (ref_date + timedelta(days=1)).replace(hour=8, minute=0, second=0)
    date_str = f"{start_dt.strftime('%Y-%m-%d')} 22:00 → {end_dt.strftime('%Y-%m-%d')} 08:00"

    rows = load_period(CSV_PATH, start_dt, end_dt)
    if not rows:
        print(f"No data found for {date_str}")
        sys.exit(1)

    cycles = analyze_night(rows)
    print_report(date_str, cycles)

    # If previous night data exists, show comparison
    prev_start = start_dt - timedelta(days=1)
    prev_end = end_dt - timedelta(days=1)
    prev_rows = load_period(CSV_PATH, prev_start, prev_end)
    if prev_rows:
        prev_cycles = analyze_night(prev_rows)
        prev_heating = [c for c in prev_cycles if not c["is_dhw"]]
        curr_heating = [c for c in cycles if not c["is_dhw"]]

        prev_durations = [cycle_duration_min(c) for c in prev_heating if cycle_duration_min(c) > 0]
        curr_durations = [cycle_duration_min(c) for c in curr_heating if cycle_duration_min(c) > 0]

        prev_hz = [h for c in prev_heating for h in c["hz_values"]]
        curr_hz = [h for c in curr_heating for h in c["hz_values"]]

        prev_cop = [v for c in prev_heating for v in c["cop_values"]]
        curr_cop = [v for c in curr_heating for v in c["cop_values"]]

        print(f"\n  COMPARISON vs previous night ({prev_start.strftime('%Y-%m-%d')})")
        print(f"  {'─' * 60}")
        print(f"  {'Metric':<25} {'Previous':>12} {'Current':>12} {'Change':>12}")
        print(f"  {'─' * 60}")

        def fmt_cmp(label, prev_val, curr_val, fmt_str=".0f", lower_is_better=False):
            if prev_val is None or curr_val is None:
                return
            diff = curr_val - prev_val
            arrow = "▼" if diff < 0 else "▲" if diff > 0 else "="
            good = (diff < 0) if lower_is_better else (diff > 0)
            marker = " ✓" if good and abs(diff) > 0.1 else ""
            print(f"  {label:<25} {prev_val:>12{fmt_str}} {curr_val:>12{fmt_str}} {arrow}{abs(diff):>10{fmt_str}}{marker}")

        fmt_cmp("Heating cycles", len(prev_heating), len(curr_heating), "d", lower_is_better=True)
        if prev_durations and curr_durations:
            fmt_cmp("Avg run (min)", sum(prev_durations)/len(prev_durations), sum(curr_durations)/len(curr_durations), ".0f")
        if prev_hz and curr_hz:
            fmt_cmp("Avg Hz", sum(prev_hz)/len(prev_hz), sum(curr_hz)/len(curr_hz), ".0f", lower_is_better=True)
            fmt_cmp("Max Hz", max(prev_hz), max(curr_hz), ".0f", lower_is_better=True)
        if prev_cop and curr_cop:
            fmt_cmp("Avg COP", sum(prev_cop)/len(prev_cop), sum(curr_cop)/len(curr_cop), ".1f")

        print(f"  {'─' * 60}")
        print()


if __name__ == "__main__":
    main()
