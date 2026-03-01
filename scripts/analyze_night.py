# ABOUTME: Analyzes a specific night's compressor cycling from cloud CSV data.
# ABOUTME: Configurable date range, outputs cycling events and summary stats.
import csv
import sys
from datetime import datetime

CSV_FILE = sys.argv[1] if len(sys.argv) > 1 else "/tmp/overnight_analysis.csv"

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
                except (ValueError, TypeError):
                    row[k] = None
            rows.append(row)
        except Exception:
            pass

rows.sort(key=lambda r: r["_ts"])
hours = (rows[-1]["_ts"] - rows[0]["_ts"]).total_seconds() / 3600

print("=" * 100)
print(f'  OVERNIGHT ANALYSIS: {rows[0]["timestamp"]} -> {rows[-1]["timestamp"]} ({hours:.1f}h, {len(rows)} readings)')
print("=" * 100)

for key, name in [
    ("outside_temp", "Outside"),
    ("feed_temp", "Feed"),
    ("return_temp", "Return"),
    ("flow_target_temp", "Target"),
    ("delta_t", "Delta T"),
    ("room_temp", "Room"),
]:
    vals = [r[key] for r in rows if r[key] is not None]
    if vals:
        print(f"  {name:12s}: {min(vals):5.1f} / {sum(vals)/len(vals):5.1f} / {max(vals):5.1f}  (min/avg/max)")

on_rows = [r for r in rows if r["compressor_on"] == 1]
pct = len(on_rows) / len(rows) * 100
hz_on = [r["compressor_hz"] for r in on_rows if r["compressor_hz"] and r["compressor_hz"] > 0]
print(f"\n  Compressor ON: {pct:.0f}% of time")
if hz_on:
    print(f"  Frequency:  {min(hz_on):.0f} / {sum(hz_on)/len(hz_on):.0f} / {max(hz_on):.0f} Hz (min/avg/max)")

ecop = [r["estimated_cop"] for r in rows if r["estimated_cop"] and r["estimated_cop"] > 0]
if ecop:
    print(f"  Est. COP:   {min(ecop):.2f} / {sum(ecop)/len(ecop):.2f} / {max(ecop):.2f}")

# Cycling analysis
on_cycles = []
off_cycles = []
current_state = None
state_start = None
start_data = None
for r in rows:
    state = int(r["compressor_on"]) if r["compressor_on"] is not None else 0
    if current_state is None:
        current_state = state
        state_start = r["_ts"]
        start_data = r
        continue
    if state != current_state:
        duration = (r["_ts"] - state_start).total_seconds() / 60
        entry = {
            "start": state_start,
            "end": r["_ts"],
            "duration_min": round(duration, 1),
            "feed_start": start_data["feed_temp"],
            "feed_end": r["feed_temp"],
            "ret_start": start_data["return_temp"],
            "ret_end": r["return_temp"],
            "target_start": start_data["flow_target_temp"],
            "target_end": r["flow_target_temp"],
            "ot": r["outside_temp"],
            "hz_start": start_data["compressor_hz"],
            "hz_end": r["compressor_hz"],
            "room": r["room_temp"],
            "dt": r["delta_t"],
        }
        if current_state:
            on_cycles.append(entry)
        else:
            off_cycles.append(entry)
        current_state = state
        state_start = r["_ts"]
        start_data = r

if state_start and rows:
    duration = (rows[-1]["_ts"] - state_start).total_seconds() / 60
    entry = {
        "start": state_start,
        "end": rows[-1]["_ts"],
        "duration_min": round(duration, 1),
        "feed_start": start_data["feed_temp"],
        "feed_end": rows[-1]["feed_temp"],
        "ret_start": start_data["return_temp"],
        "ret_end": rows[-1]["return_temp"],
        "target_start": start_data["flow_target_temp"],
        "target_end": rows[-1]["flow_target_temp"],
        "ot": rows[-1]["outside_temp"],
        "hz_start": start_data["compressor_hz"],
        "hz_end": rows[-1]["compressor_hz"],
        "room": rows[-1]["room_temp"],
        "dt": rows[-1]["delta_t"],
    }
    if current_state:
        on_cycles.append(entry)
    else:
        off_cycles.append(entry)

print(f"\n  Compressor starts: {len(on_cycles)} ({len(on_cycles)/hours:.2f}/h)")

on_durations = [c["duration_min"] for c in on_cycles]
off_durations = [c["duration_min"] for c in off_cycles]
if on_durations:
    print(f"  ON  durations: {min(on_durations):.0f} / {sum(on_durations)/len(on_durations):.0f} / {max(on_durations):.0f} min (min/avg/max)")
if off_durations:
    print(f"  OFF durations: {min(off_durations):.0f} / {sum(off_durations)/len(off_durations):.0f} / {max(off_durations):.0f} min (min/avg/max)")

print(f'\n  {"State":<5} {"Start":>5}-{"End":>5}  {"Dur":>6}  {"Hz":>6}  {"Feed":>10}  {"Return":>10}  {"Target":>10}  {"OT":>4}  {"Room":>4}')
print("  " + "-" * 90)

all_events = []
for c in on_cycles:
    c["state"] = "ON"
    all_events.append(c)
for c in off_cycles:
    c["state"] = "OFF"
    all_events.append(c)
all_events.sort(key=lambda e: e["start"])

for c in all_events:
    hz_str = f'{c["hz_start"]:.0f}' if c["state"] == "ON" else ""
    print(
        f'  {c["state"]:<5} {c["start"].strftime("%H:%M"):>5}-{c["end"].strftime("%H:%M"):>5}'
        f'  {c["duration_min"]:5.1f}m  {hz_str:>6}'
        f'  {c["feed_start"]:4.1f}->{c["feed_end"]:4.1f}'
        f'  {c["ret_start"]:4.1f}->{c["ret_end"]:4.1f}'
        f'  {c["target_start"]:4.1f}->{c["target_end"]:4.1f}'
        f'  {c["ot"]:4.1f}  {c["room"]:4.1f}'
    )

# Feed vs Target timeline (every 10 min)
print(f"\n{'=' * 100}")
print("  FEED vs TARGET TIMELINE (every 10 min)")
print("=" * 100)
print(f'  {"Time":<20} {"Hz":>4} {"Feed":>5} {"Tgt":>5} {"F-T":>5} {"Ret":>5} {"OT":>4} {"Room":>5} {"dT":>4} {"Comp":>4}')
print("  " + "-" * 80)

for i, r in enumerate(rows):
    if i % 10 == 0:
        comp = "ON" if r["compressor_on"] == 1 else "OFF"
        hz = r["compressor_hz"] if r["compressor_hz"] else 0
        feed = r["feed_temp"] if r["feed_temp"] else 0
        target = r["flow_target_temp"] if r["flow_target_temp"] else 0
        diff = feed - target
        ret = r["return_temp"] if r["return_temp"] else 0
        ot = r["outside_temp"] if r["outside_temp"] else 0
        room = r["room_temp"] if r["room_temp"] else 0
        dt = r["delta_t"] if r["delta_t"] else 0
        print(
            f'  {r["timestamp"]:<20} {hz:4.0f} {feed:5.1f} {target:5.1f} {diff:+5.1f}'
            f" {ret:5.1f} {ot:4.1f} {room:5.1f} {dt:4.1f} {comp:>4}"
        )
