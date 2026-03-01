# ABOUTME: Compares current vs proposed cold_factor across full OT range.
# ABOUTME: Also analyzes actual warm weather behavior from CSV logs.
import csv
import sys
from collections import defaultdict
from datetime import datetime

CSV_FILE = sys.argv[1] if len(sys.argv) > 1 else "/tmp/full_log.csv"

# ============================================================
# PART 1: Theoretical comparison across full OT range
# ============================================================
print("=" * 110)
print("  THEORETICAL: CURRENT vs PROPOSED cold_factor across full OT range")
print("  UFH profile: base_min_delta=1.0, min_delta_cold_limit=6.0, max_delta=6.5")
print("=" * 110)
print(f"  {'OT':>4}  |  {'raw cf':>6}  {'CURRENT':>10}  {'dyn_min':>7}  {'tgt(r=29)':>9}  |"
      f"  {'PROPOSED':>10}  {'dyn_min':>7}  {'tgt(r=29)':>9}  {'diff':>5}")
print("  " + "-" * 100)

for ot in range(20, -11, -1):
    clamped = max(-5, min(15, ot))
    raw_cf = (15 - clamped) / 20.0

    # Current: quadratic * 0.5
    cf_current = raw_cf * raw_cf * 0.5
    dyn_min_current = 1.0 + cf_current * (6.0 - 1.0)

    # Proposed: linear (no quadratic)
    cf_proposed = raw_cf
    dyn_min_proposed = 1.0 + cf_proposed * (6.0 - 1.0)

    # Approximate target with return=29 (typical saturated UFH)
    ret = 29.0 if ot >= 0 else 29.0 + (0 - ot) * 0.3  # return rises in very cold
    tgt_current = ret + dyn_min_current
    tgt_proposed = ret + dyn_min_proposed
    diff = tgt_proposed - tgt_current

    marker = ""
    if 30 <= tgt_current <= 32:
        marker = " <-- CYCLING ZONE"
    if ot >= 10:
        marker = " <-- warm weather"

    print(f"  {ot:>3}°C  |  {raw_cf:>6.3f}  {cf_current:>10.4f}  {dyn_min_current:>7.2f}  {tgt_current:>9.1f}  |"
          f"  {cf_proposed:>10.4f}  {dyn_min_proposed:>7.2f}  {tgt_proposed:>9.1f}  {diff:>+5.1f}{marker}")

# ============================================================
# PART 2: What happens with suppression in warm weather?
# ============================================================
print()
print("=" * 110)
print("  SUPPRESSION ANALYSIS: what happens when room > target?")
print("  error < -0.5: suppress to min (25°C)")
print("  -0.5 <= error < 0: reduced_delta = max(0, dynamic_min + error)")
print("=" * 110)
print(f"  {'OT':>4}  {'room':>5}  {'r_tgt':>5}  {'error':>6}  |  {'CUR dyn_min':>11}  {'CUR reduced':>11}  {'CUR target':>10}  |"
      f"  {'NEW dyn_min':>11}  {'NEW reduced':>11}  {'NEW target':>10}  {'action':>12}")
print("  " + "-" * 120)

for ot, room in [(15, 23.0), (13, 22.8), (13, 23.0), (13, 23.2),
                  (10, 22.8), (10, 23.0), (10, 23.2),
                  (8, 22.6), (8, 22.8), (8, 23.0),
                  (5, 22.5), (5, 22.6), (5, 22.8), (5, 23.0),
                  (3, 22.5), (3, 22.6),
                  (0, 22.5), (0, 22.3)]:
    room_target = 22.5
    error = room_target - room
    ret = 28.0 if ot >= 10 else 29.0 if ot >= 0 else 30.0

    clamped = max(-5, min(15, ot))
    raw_cf = (15 - clamped) / 20.0

    cf_cur = raw_cf * raw_cf * 0.5
    cf_new = raw_cf
    dyn_min_cur = 1.0 + cf_cur * 5.0
    dyn_min_new = 1.0 + cf_new * 5.0

    if error < -0.5:
        action = "SUPPRESS"
        tgt_cur = 25.0
        tgt_new = 25.0
        red_cur = "n/a"
        red_new = "n/a"
    elif error < 0:
        action = "reduced"
        red_cur_v = max(0, dyn_min_cur + error)
        red_new_v = max(0, dyn_min_new + error)
        tgt_cur = ret + red_cur_v
        tgt_new = ret + red_new_v
        red_cur = f"{red_cur_v:.2f}"
        red_new = f"{red_new_v:.2f}"
    else:
        action = "full delta"
        tgt_cur = ret + dyn_min_cur
        tgt_new = ret + dyn_min_new
        red_cur = f"{dyn_min_cur:.2f}"
        red_new = f"{dyn_min_new:.2f}"

    diff_marker = ""
    if isinstance(tgt_cur, float) and isinstance(tgt_new, float):
        d = tgt_new - tgt_cur
        if d > 0.1:
            diff_marker = f" (+{d:.1f})"

    print(f"  {ot:>3}°C  {room:>5.1f}  {room_target:>5.1f}  {error:>+6.2f}  |"
          f"  {dyn_min_cur:>11.2f}  {red_cur:>11}  {tgt_cur:>10.1f}  |"
          f"  {dyn_min_new:>11.2f}  {red_new:>11}  {tgt_new:>10.1f}  {action}{diff_marker}")

# ============================================================
# PART 3: Actual warm weather data from logs
# ============================================================
print()
print("=" * 110)
print("  ACTUAL WARM WEATHER DATA FROM LOGS (OT >= 8°C)")
print("=" * 110)

rows = []
with open(CSV_FILE, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            row["_ts"] = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            for k in row:
                if k in ("timestamp", "_ts"):
                    continue
                try:
                    row[k] = float(row[k])
                except:
                    row[k] = None
            rows.append(row)
        except:
            pass

warm = [r for r in rows if r["outside_temp"] is not None and r["outside_temp"] >= 8]
if warm:
    print(f"\n  Total warm readings (OT>=8°C): {len(warm)}")

    # By OT bucket
    ot_buckets = defaultdict(list)
    for r in warm:
        bucket = int(r["outside_temp"] // 2) * 2
        ot_buckets[bucket].append(r)

    print(f"\n  {'OT':>6}  {'Count':>6}  {'Comp%':>6}  {'Target':>12}  {'Feed':>12}  {'Room':>12}  {'Hz avg':>6}  {'COP avg':>7}")
    print("  " + "-" * 90)

    for bucket in sorted(ot_buckets.keys()):
        data = ot_buckets[bucket]
        comp_on = [r for r in data if r["compressor_on"] == 1]
        comp_pct = len(comp_on) / len(data) * 100
        targets = [r["flow_target_temp"] for r in data if r["flow_target_temp"] is not None]
        feeds = [r["feed_temp"] for r in data if r["feed_temp"] is not None]
        rooms = [r["room_temp"] for r in data if r["room_temp"] is not None]
        hzs = [r["compressor_hz"] for r in comp_on if r["compressor_hz"] and r["compressor_hz"] > 0]
        cops = [r["estimated_cop"] for r in comp_on if r["estimated_cop"] and r["estimated_cop"] > 0.5]

        tgt_str = f"{min(targets):.0f}-{max(targets):.0f}" if targets else "n/a"
        feed_str = f"{min(feeds):.0f}-{max(feeds):.0f}" if feeds else "n/a"
        room_str = f"{min(rooms):.1f}-{max(rooms):.1f}" if rooms else "n/a"
        hz_str = f"{sum(hzs)/len(hzs):.0f}" if hzs else "n/a"
        cop_str = f"{sum(cops)/len(cops):.2f}" if cops else "n/a"

        print(f"  {bucket:>3}-{bucket+2:>2}°C  {len(data):>6}  {comp_pct:>5.0f}%  {tgt_str:>12}  {feed_str:>12}  {room_str:>12}  {hz_str:>6}  {cop_str:>7}")

    # How much time is spent suppressed vs active in warm weather
    warm_comp_off = [r for r in warm if r["compressor_on"] == 0 and r.get("3way_valve_dhw") == 0]
    warm_min_target = [r for r in warm if r["flow_target_temp"] is not None and r["flow_target_temp"] <= 25.5]
    print(f"\n  Suppressed readings (target<=25.5): {len(warm_min_target)} / {len(warm)} ({len(warm_min_target)/len(warm)*100:.0f}%)")
    print(f"  Compressor OFF (non-DHW): {len(warm_comp_off)} / {len(warm)} ({len(warm_comp_off)/len(warm)*100:.0f}%)")

    # Room temp distribution in warm weather
    warm_rooms = [r["room_temp"] for r in warm if r["room_temp"] is not None]
    if warm_rooms:
        above_target = [t for t in warm_rooms if t > 22.5]
        above_05 = [t for t in warm_rooms if t > 23.0]
        print(f"\n  Room temp in warm weather:")
        print(f"    Above target (>22.5): {len(above_target)}/{len(warm_rooms)} ({len(above_target)/len(warm_rooms)*100:.0f}%)")
        print(f"    Above target+0.5 (>23.0, suppression): {len(above_05)}/{len(warm_rooms)} ({len(above_05)/len(warm_rooms)*100:.0f}%)")
        print(f"    Range: {min(warm_rooms):.1f} - {max(warm_rooms):.1f}, avg: {sum(warm_rooms)/len(warm_rooms):.1f}")
