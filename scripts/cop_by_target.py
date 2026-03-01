# ABOUTME: Analyzes COP vs flow target temperature to find optimal operating points.
# ABOUTME: Groups readings by target temp bucket and shows COP, Hz, and stability.
import csv
import sys
from collections import defaultdict

CSV_FILE = sys.argv[1] if len(sys.argv) > 1 else "/tmp/full_log.csv"

rows = []
with open(CSV_FILE, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            for k in row:
                if k == "timestamp":
                    continue
                try:
                    row[k] = float(row[k])
                except (ValueError, TypeError):
                    row[k] = None
            rows.append(row)
        except Exception:
            pass

# Only heating rows: compressor on, no DHW, no defrost, COP > 0
heating = [
    r for r in rows
    if r["compressor_on"] == 1
    and r.get("3way_valve_dhw") == 0
    and r.get("defrost") == 0
    and r["estimated_cop"] is not None
    and r["estimated_cop"] > 0.5
    and r["flow_target_temp"] is not None
    and r["flow_target_temp"] >= 25
    and r["compressor_hz"] is not None
    and r["compressor_hz"] > 0
]

print(f"Total heating readings: {len(heating)}")
print()

# Group by target temp (1°C buckets)
buckets = defaultdict(list)
for r in heating:
    bucket = round(r["flow_target_temp"])
    buckets[bucket].append(r)

print("=" * 95)
print("  COP BY FLOW TARGET TEMPERATURE (1°C buckets, heating only)")
print("=" * 95)
print(f"  {'Target':>6}  {'Count':>6}  {'COP min':>7}  {'COP avg':>7}  {'COP max':>7}  {'Hz avg':>6}  {'Hz min':>6}  {'OT avg':>6}  {'Feed avg':>8}")
print("  " + "-" * 85)

for bucket in sorted(buckets.keys()):
    data = buckets[bucket]
    if len(data) < 5:
        continue
    cops = [r["estimated_cop"] for r in data]
    hzs = [r["compressor_hz"] for r in data]
    ots = [r["outside_temp"] for r in data if r["outside_temp"] is not None]
    feeds = [r["feed_temp"] for r in data if r["feed_temp"] is not None]
    avg_cop = sum(cops) / len(cops)
    avg_hz = sum(hzs) / len(hzs)
    avg_ot = sum(ots) / len(ots) if ots else 0
    avg_feed = sum(feeds) / len(feeds) if feeds else 0
    print(
        f"  {bucket:>5.0f}°C  {len(data):>6}  {min(cops):>7.2f}  {avg_cop:>7.2f}  {max(cops):>7.2f}"
        f"  {avg_hz:>6.0f}  {min(hzs):>6.0f}  {avg_ot:>6.1f}  {avg_feed:>8.1f}"
    )

# Group by 2°C buckets for smoother view
print()
print("=" * 95)
print("  COP BY FLOW TARGET (2°C buckets)")
print("=" * 95)
print(f"  {'Target':>8}  {'Count':>6}  {'COP avg':>7}  {'COP p25':>7}  {'COP p75':>7}  {'Hz avg':>6}  {'OT avg':>6}  {'dT avg':>6}")
print("  " + "-" * 85)

buckets2 = defaultdict(list)
for r in heating:
    bucket = int(r["flow_target_temp"] // 2) * 2
    buckets2[bucket].append(r)

for bucket in sorted(buckets2.keys()):
    data = buckets2[bucket]
    if len(data) < 5:
        continue
    cops = sorted([r["estimated_cop"] for r in data])
    hzs = [r["compressor_hz"] for r in data]
    ots = [r["outside_temp"] for r in data if r["outside_temp"] is not None]
    dts = [r["delta_t"] for r in data if r["delta_t"] is not None]
    avg_cop = sum(cops) / len(cops)
    p25 = cops[len(cops) // 4]
    p75 = cops[3 * len(cops) // 4]
    avg_hz = sum(hzs) / len(hzs)
    avg_ot = sum(ots) / len(ots) if ots else 0
    avg_dt = sum(dts) / len(dts) if dts else 0
    print(
        f"  {bucket:>3}-{bucket+2:>2}°C  {len(data):>6}  {avg_cop:>7.2f}  {p25:>7.2f}  {p75:>7.2f}"
        f"  {avg_hz:>6.0f}  {avg_ot:>6.1f}  {avg_dt:>6.1f}"
    )

# COP vs Hz analysis
print()
print("=" * 95)
print("  COP BY COMPRESSOR FREQUENCY (10 Hz buckets)")
print("=" * 95)
print(f"  {'Hz':>8}  {'Count':>6}  {'COP avg':>7}  {'COP min':>7}  {'COP max':>7}  {'Target avg':>10}  {'OT avg':>6}")
print("  " + "-" * 70)

hz_buckets = defaultdict(list)
for r in heating:
    bucket = int(r["compressor_hz"] // 10) * 10
    hz_buckets[bucket].append(r)

for bucket in sorted(hz_buckets.keys()):
    data = hz_buckets[bucket]
    if len(data) < 3:
        continue
    cops = [r["estimated_cop"] for r in data]
    targets = [r["flow_target_temp"] for r in data]
    ots = [r["outside_temp"] for r in data if r["outside_temp"] is not None]
    avg_cop = sum(cops) / len(cops)
    avg_tgt = sum(targets) / len(targets)
    avg_ot = sum(ots) / len(ots) if ots else 0
    print(
        f"  {bucket:>3}-{bucket+10:>2} Hz  {len(data):>6}  {avg_cop:>7.2f}  {min(cops):>7.2f}  {max(cops):>7.2f}"
        f"  {avg_tgt:>10.1f}  {avg_ot:>6.1f}"
    )

# Stability analysis: cycling vs continuous
print()
print("=" * 95)
print("  COP: CYCLING vs CONTINUOUS PERIODS (overnight only, 22:00-07:00)")
print("=" * 95)

from datetime import datetime

night_rows = []
for r in rows:
    try:
        ts = datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S")
        h = ts.hour
        if h >= 22 or h < 7:
            r["_ts"] = ts
            night_rows.append(r)
    except:
        pass

night_rows.sort(key=lambda r: r["_ts"])

# Find continuous runs vs cycling periods
# A "continuous" period = compressor ON for >60 min
# A "cycling" period = multiple ON/OFF within 60 min
if night_rows:
    on_streak = 0
    continuous_rows = []
    cycling_rows = []
    streak_start = None

    for i, r in enumerate(night_rows):
        comp = r["compressor_on"] == 1
        if comp:
            if on_streak == 0:
                streak_start = i
            on_streak += 1
        else:
            if on_streak > 0 and on_streak >= 60:  # 60+ readings = 60+ min continuous
                continuous_rows.extend(night_rows[streak_start:i])
            elif on_streak > 0 and on_streak < 60:
                cycling_rows.extend(night_rows[streak_start:i])
            on_streak = 0

    for label, data in [("CONTINUOUS (>60 min runs)", continuous_rows), ("CYCLING (<60 min runs)", cycling_rows)]:
        hdata = [r for r in data if r["compressor_on"] == 1 and r.get("3way_valve_dhw") == 0
                 and r.get("defrost") == 0 and r["estimated_cop"] and r["estimated_cop"] > 0.5
                 and r["compressor_hz"] and r["compressor_hz"] > 0]
        if not hdata:
            print(f"\n  {label}: no data")
            continue
        cops = [r["estimated_cop"] for r in hdata]
        hzs = [r["compressor_hz"] for r in hdata]
        tgts = [r["flow_target_temp"] for r in hdata if r["flow_target_temp"]]
        ots = [r["outside_temp"] for r in hdata if r["outside_temp"] is not None]
        print(f"\n  {label} ({len(hdata)} readings):")
        print(f"    COP:    {min(cops):.2f} / {sum(cops)/len(cops):.2f} / {max(cops):.2f}")
        print(f"    Hz:     {min(hzs):.0f} / {sum(hzs)/len(hzs):.0f} / {max(hzs):.0f}")
        if tgts:
            print(f"    Target: {min(tgts):.1f} / {sum(tgts)/len(tgts):.1f} / {max(tgts):.1f}")
        if ots:
            print(f"    OT:     {min(ots):.1f} / {sum(ots)/len(ots):.1f} / {max(ots):.1f}")
