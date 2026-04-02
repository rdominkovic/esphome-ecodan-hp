# ABOUTME: Generates overnight heating performance report from CSV log data.
# ABOUTME: Analyzes compressor cycles, Hz profiles, true COP, heat loss, and AA mode breakdown.

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
        aa_mode = parse_float(row[COL["aa_control_mode"]])
        room = parse_float(row[COL["room_temp"]])
        consumed = parse_float(row[COL["daily_consumed_kwh"]])
        produced = parse_float(row[COL["daily_produced_kwh"]])
        ts_str = row[0]

        if prev_comp is not None and comp_on == 1 and prev_comp == 0:
            current_cycle = {
                "start": ts_str, "end": None,
                "hz_values": [], "feed_values": [], "target_values": [],
                "mode_minutes": defaultdict(int),
                "ot_values": [], "room_start": room, "room_end": room,
                "is_dhw": False, "samples": 0,
                "energy_start_consumed": consumed,
                "energy_start_produced": produced,
                "energy_end_consumed": consumed,
                "energy_end_produced": produced,
            }
            cycles.append(current_cycle)

        if current_cycle is not None and comp_on == 1:
            current_cycle["samples"] += 1
            current_cycle["end"] = ts_str
            current_cycle["room_end"] = room
            current_cycle["energy_end_consumed"] = consumed
            current_cycle["energy_end_produced"] = produced
            if hz > 0:
                current_cycle["hz_values"].append(hz)
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
                current_cycle["energy_end_consumed"] = consumed
                current_cycle["energy_end_produced"] = produced
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


def cycle_cop(cycle):
    """True COP from FTC energy counter deltas. Returns 0 if data spans midnight reset."""
    dc = cycle["energy_end_consumed"] - cycle["energy_start_consumed"]
    dp = cycle["energy_end_produced"] - cycle["energy_start_produced"]
    if dc < 0 or dp < 0:
        return 0.0  # midnight counter reset — skip
    if dc > 0.01:
        return dp / dc
    return 0.0


def analyze_heat_loss(rows, heating_cycles):
    """Estimate heat loss from total energy balance.

    Uses energy balance: almost all delivered heat compensates for heat loss
    since room temp barely changes overnight. This is more reliable than
    measuring room drop during 4-min OFF periods (UFH thermal mass too large).
    """
    if not rows or not heating_cycles:
        return None

    # Total hours in the period
    try:
        t_start = datetime.strptime(rows[0][0], "%Y-%m-%d %H:%M:%S")
        t_end = datetime.strptime(rows[-1][0], "%Y-%m-%d %H:%M:%S")
        total_hours = (t_end - t_start).total_seconds() / 3600
    except (ValueError, IndexError):
        return None
    if total_hours < 1:
        return None

    # Total energy delivered (only valid cycles, skip midnight-reset ones)
    total_produced = 0
    for c in heating_cycles:
        dp = c["energy_end_produced"] - c["energy_start_produced"]
        if dp > 0:
            total_produced += dp

    # Average temperatures
    all_ot = [parse_float(r[COL["outside_temp"]]) for r in rows]
    all_room = [parse_float(r[COL["room_temp"]]) for r in rows if parse_float(r[COL["room_temp"]]) > 0]
    avg_ot = sum(all_ot) / len(all_ot) if all_ot else 0
    avg_room = sum(all_room) / len(all_room) if all_room else 0
    temp_diff = avg_room - avg_ot

    avg_demand_kw = total_produced / total_hours if total_hours > 0 else 0
    loss_per_degree = avg_demand_kw / temp_diff if temp_diff > 1 else 0

    return {
        "total_hours": total_hours,
        "total_produced_kwh": total_produced,
        "avg_demand_kw": avg_demand_kw,
        "avg_ot": avg_ot,
        "avg_room": avg_room,
        "temp_diff": temp_diff,
        "loss_per_degree_kw": loss_per_degree,
    }


def print_report(date_str, cycles, rows):
    heating_cycles = [c for c in cycles if not c["is_dhw"]]
    dhw_cycles = [c for c in cycles if c["is_dhw"]]

    print(f"{'=' * 105}")
    print(f"  OVERNIGHT REPORT: {date_str}  (22:00 - 08:00)")
    print(f"{'=' * 105}")

    # Summary
    durations = [cycle_duration_min(c) for c in heating_cycles if cycle_duration_min(c) > 0]
    all_hz = [h for c in heating_cycles for h in c["hz_values"]]
    all_ot = [v for c in heating_cycles for v in c["ot_values"]]
    cops = [cycle_cop(c) for c in heating_cycles if cycle_cop(c) > 0]
    mode_totals = defaultdict(int)
    for c in heating_cycles:
        for mode, mins in c["mode_minutes"].items():
            mode_totals[mode] += mins

    # Overall COP from total energy delta
    if heating_cycles:
        total_consumed = sum(c["energy_end_consumed"] - c["energy_start_consumed"] for c in heating_cycles)
        total_produced = sum(c["energy_end_produced"] - c["energy_start_produced"] for c in heating_cycles)
        overall_cop = total_produced / total_consumed if total_consumed > 0.01 else 0
    else:
        total_consumed, total_produced, overall_cop = 0, 0, 0

    print(f"\n  Heating cycles: {len(heating_cycles)}    DHW cycles: {len(dhw_cycles)}")
    if durations:
        print(f"  Run duration:   min {min(durations):.0f} min, max {max(durations):.0f} min, avg {sum(durations)/len(durations):.0f} min, total {sum(durations):.0f} min")
    if all_hz:
        print(f"  Compressor Hz:  min {min(all_hz):.0f}, max {max(all_hz):.0f}, avg {sum(all_hz)/len(all_hz):.0f}")
    if total_consumed > 0:
        print(f"  Energy:         consumed {total_consumed:.2f} kWh, produced {total_produced:.2f} kWh")
        print(f"  TRUE COP:       {overall_cop:.2f} overall", end="")
        if cops:
            print(f"  (per-cycle: min {min(cops):.2f}, max {max(cops):.2f}, avg {sum(cops)/len(cops):.2f})")
        else:
            print()
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
    print(f"\n  {'─' * 101}")
    print(f"  {'#':>2}  {'Start':<20} {'Dur':>5} {'AvgHz':>5} {'MaxHz':>5} {'COP':>5} {'kWh▼':>5} {'kWh▲':>5} {'Feed':>5} {'SP':>5} {'OT':>4} {'Room':>5}  Modes")
    print(f"  {'─' * 101}")

    for i, c in enumerate(heating_cycles):
        dur = cycle_duration_min(c)
        avg_hz = sum(c["hz_values"]) / len(c["hz_values"]) if c["hz_values"] else 0
        max_hz = max(c["hz_values"]) if c["hz_values"] else 0
        cop = cycle_cop(c)
        dc = c["energy_end_consumed"] - c["energy_start_consumed"]
        dp = c["energy_end_produced"] - c["energy_start_produced"]
        avg_feed = sum(c["feed_values"]) / len(c["feed_values"]) if c["feed_values"] else 0
        avg_target = sum(c["target_values"]) / len(c["target_values"]) if c["target_values"] else 0
        avg_ot = sum(c["ot_values"]) / len(c["ot_values"]) if c["ot_values"] else 0
        modes_str = " ".join(f"M{m}:{n}m" for m, n in sorted(c["mode_minutes"].items()))
        print(f"  {i+1:>2}  {c['start']:<20} {dur:>4.0f}m {avg_hz:>5.0f} {max_hz:>5.0f} {cop:>5.2f} {dc:>5.2f} {dp:>5.2f} {avg_feed:>5.1f} {avg_target:>5.1f} {avg_ot:>4.0f} {c['room_end']:>5.1f}  {modes_str}")

    if dhw_cycles:
        print(f"\n  DHW Cycles:")
        for i, c in enumerate(dhw_cycles):
            dur = cycle_duration_min(c)
            avg_hz = sum(c["hz_values"]) / len(c["hz_values"]) if c["hz_values"] else 0
            cop = cycle_cop(c)
            print(f"    {c['start']} - {dur:.0f} min, avg Hz {avg_hz:.0f}, COP {cop:.2f}")

    # Heat loss analysis
    hl = analyze_heat_loss(rows, heating_cycles)
    if hl and hl["total_produced_kwh"] > 0:
        print(f"\n  {'─' * 101}")
        print(f"  HEAT LOSS ESTIMATE (energy balance method)")
        print(f"  {'─' * 101}")
        print(f"  Period: {hl['total_hours']:.1f} hours, total heat delivered: {hl['total_produced_kwh']:.2f} kWh")
        print(f"  Avg room: {hl['avg_room']:.1f} C, avg outside: {hl['avg_ot']:.0f} C, diff: {hl['temp_diff']:.0f} C")
        print(f"  Avg heat demand: {hl['avg_demand_kw']:.2f} kW")
        print(f"  Loss coefficient: {hl['loss_per_degree_kw']:.3f} kW per C of room-outside diff")
        print(f"\n  Heat demand at different outdoor temps (room {hl['avg_room']:.0f} C):")
        for sample_ot in [-5, 0, 3, 5, 7, 10, 15]:
            diff = hl["avg_room"] - sample_ot
            demand = hl["loss_per_degree_kw"] * diff
            print(f"    OT {sample_ot:>3d} C → {demand:.1f} kW")

    # OT-COP breakdown
    if heating_cycles:
        print(f"\n  {'─' * 101}")
        print(f"  COP BY OUTSIDE TEMPERATURE")
        print(f"  {'─' * 101}")
        ot_buckets = defaultdict(lambda: {"consumed": 0, "produced": 0, "hz": [], "cycles": 0, "durations": []})
        for c in heating_cycles:
            avg_ot = sum(c["ot_values"]) / len(c["ot_values"]) if c["ot_values"] else 0
            bucket = int(avg_ot // 2) * 2  # 2-degree buckets
            dc = c["energy_end_consumed"] - c["energy_start_consumed"]
            dp = c["energy_end_produced"] - c["energy_start_produced"]
            if dc < 0 or dp < 0:
                continue  # skip midnight counter reset cycle
            ot_buckets[bucket]["consumed"] += dc
            ot_buckets[bucket]["produced"] += dp
            ot_buckets[bucket]["hz"].extend(c["hz_values"])
            ot_buckets[bucket]["cycles"] += 1
            ot_buckets[bucket]["durations"].append(cycle_duration_min(c))

        print(f"  {'OT range':<12} {'Cycles':>6} {'AvgRun':>6} {'AvgHz':>5} {'Consumed':>8} {'Produced':>8} {'COP':>6}")
        print(f"  {'─' * 60}")
        for bucket in sorted(ot_buckets.keys()):
            b = ot_buckets[bucket]
            cop = b["produced"] / b["consumed"] if b["consumed"] > 0.01 else 0
            avg_hz = sum(b["hz"]) / len(b["hz"]) if b["hz"] else 0
            avg_dur = sum(b["durations"]) / len(b["durations"]) if b["durations"] else 0
            print(f"  {bucket:>3d}-{bucket+2:<3d} C    {b['cycles']:>5}  {avg_dur:>5.0f}m {avg_hz:>5.0f} {b['consumed']:>7.2f}  {b['produced']:>7.2f}  {cop:>5.2f}")

    print(f"\n{'=' * 105}")


def get_summary_stats(cycles):
    """Return key stats for comparison."""
    heating = [c for c in cycles if not c["is_dhw"]]
    durations = [cycle_duration_min(c) for c in heating if cycle_duration_min(c) > 0]
    all_hz = [h for c in heating for h in c["hz_values"]]
    total_consumed = sum(c["energy_end_consumed"] - c["energy_start_consumed"] for c in heating)
    total_produced = sum(c["energy_end_produced"] - c["energy_start_produced"] for c in heating)
    overall_cop = total_produced / total_consumed if total_consumed > 0.01 else None
    return {
        "n_cycles": len(heating),
        "avg_duration": sum(durations) / len(durations) if durations else None,
        "avg_hz": sum(all_hz) / len(all_hz) if all_hz else None,
        "max_hz": max(all_hz) if all_hz else None,
        "cop": overall_cop,
    }


def print_comparison(prev_cycles, curr_cycles, prev_date_str):
    prev = get_summary_stats(prev_cycles)
    curr = get_summary_stats(curr_cycles)

    print(f"\n  COMPARISON vs previous night ({prev_date_str})")
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

    fmt_cmp("Heating cycles", prev["n_cycles"], curr["n_cycles"], "d", lower_is_better=True)
    fmt_cmp("Avg run (min)", prev["avg_duration"], curr["avg_duration"], ".0f")
    fmt_cmp("Avg Hz", prev["avg_hz"], curr["avg_hz"], ".0f", lower_is_better=True)
    fmt_cmp("Max Hz", prev["max_hz"], curr["max_hz"], ".0f", lower_is_better=True)
    fmt_cmp("TRUE COP", prev["cop"], curr["cop"], ".2f")

    print(f"  {'─' * 60}")
    print()


def main():
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
    print_report(date_str, cycles, rows)

    # Comparison with previous night
    prev_start = start_dt - timedelta(days=1)
    prev_end = end_dt - timedelta(days=1)
    prev_rows = load_period(CSV_PATH, prev_start, prev_end)
    if prev_rows:
        prev_cycles = analyze_night(prev_rows)
        print_comparison(prev_cycles, cycles, prev_start.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    main()
