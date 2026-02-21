# ABOUTME: Polls ESP32 Ecodan heat pump sensors via SSE and logs to CSV for COP diagnostics.
# ABOUTME: Run with: python scripts/monitor.py (logs to data/ecodan_log.csv)

import csv
import json
import os
import sys
import time
import urllib.request
from datetime import datetime

ESP32_URL = "http://192.168.1.230/events"
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LOG_FILE = os.path.join(LOG_DIR, "ecodan_log.csv")
POLL_INTERVAL = 60  # seconds

# Sensors to log (ESP32 name_id → CSV column name)
SENSORS = {
    "sensor-outside_temp": "outside_temp",
    "sensor-feed_temp": "feed_temp",
    "sensor-return_temp": "return_temp",
    "sensor-dhw_current_temp": "dhw_temp",
    "sensor-compressor_frequency": "compressor_hz",
    "sensor-output_power": "output_power_kw",
    "sensor-estimated_output_power": "estimated_power_kw",
    "sensor-estimated_cop": "estimated_cop",
    "sensor-heating_cop": "heating_cop",
    "sensor-dhw_cop": "dhw_cop",
    "sensor-flow_rate": "flow_rate_lmin",
    "sensor-pump_speed": "pump_speed",
    "sensor-pump_consumption": "pump_watts",
    "sensor-fan_speed": "fan_rpm",
    "sensor-heating_consumed": "heating_consumed_kwh",
    "sensor-heating_delivered": "heating_delivered_kwh",
    "sensor-dhw_consumed": "dhw_consumed_kwh",
    "sensor-dhw_delivered": "dhw_delivered_kwh",
    "sensor-reported_total_daily_energy_consumption": "daily_consumed_kwh",
    "sensor-estimated_total_daily_energy_produced": "daily_produced_kwh",
    "sensor-accumulated_compressor_starts": "compressor_starts",
    "sensor-operating_runtime": "operating_hours",
    "sensor-discharge_temp": "discharge_temp",
    "sensor-refrigerant_liquid_temp": "refrigerant_temp",
    "sensor-refrigerant_condensing_temp": "condensing_temp",
    "sensor-zone_1_setpoint_value": "flow_target_temp",
}

BINARY_SENSORS = {
    "binary_sensor-compressor": "compressor_on",
    "binary_sensor-defrost": "defrost",
    "binary_sensor-3-way_valve": "3way_valve_dhw",
    "binary_sensor-booster_heater": "booster_heater",
    "binary_sensor-water_pump_status": "water_pump",
    "binary_sensor-water_pump_2_status": "water_pump_2",
    "binary_sensor-dhw_eco": "dhw_eco",
}

# Optional sensors logged if present but not required for completion
OPTIONAL_BINARY_SENSORS = {
    "binary_sensor-short-cycle__lockout": "sc_lockout",
    "binary_sensor-short-cycle__predictive_boost_active": "sc_predictive_boost",
}

ALL_BINARY = {**BINARY_SENSORS, **OPTIONAL_BINARY_SENSORS}

CSV_COLUMNS = ["timestamp"] + list(SENSORS.values()) + list(BINARY_SENSORS.values()) + list(OPTIONAL_BINARY_SENSORS.values()) + ["delta_t"]


def fetch_snapshot():
    """Connect to ESP32 SSE endpoint, collect all initial state, return sensor dict."""
    sensors = {}
    all_ids = {**SENSORS, **ALL_BINARY}
    required = set(SENSORS.values()) | set(BINARY_SENSORS.values())
    try:
        req = urllib.request.Request(ESP32_URL)
        with urllib.request.urlopen(req, timeout=10) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not (line.startswith("data: ") and "{" in line):
                    continue
                try:
                    data = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue

                sensor_id = data.get("id", "")
                if sensor_id in SENSORS:
                    sensors[SENSORS[sensor_id]] = data.get("value")
                elif sensor_id in ALL_BINARY:
                    sensors[ALL_BINARY[sensor_id]] = 1 if data.get("value") else 0

                # Stop once we have all required sensors (optional may or may not arrive)
                if required.issubset(sensors.keys()):
                    break

    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] Connection error: {e}")
        return None

    if not sensors:
        return None

    # Calculate delta T
    feed = sensors.get("feed_temp")
    ret = sensors.get("return_temp")
    if feed is not None and ret is not None:
        sensors["delta_t"] = round(feed - ret, 1)

    return sensors


def init_csv():
    """Create CSV file with headers if it doesn't exist, or rotate if columns changed."""
    os.makedirs(LOG_DIR, exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            reader = csv.reader(f)
            existing_cols = next(reader, None)
        if existing_cols != CSV_COLUMNS:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated = LOG_FILE.replace(".csv", f"_{ts}.csv")
            os.rename(LOG_FILE, rotated)
            print(f"Column change detected, rotated old log to {rotated}")
        else:
            print(f"Appending to {LOG_FILE}")
            return
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)
    print(f"Created {LOG_FILE}")


def write_row(sensors):
    """Append one row to CSV."""
    row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    for col in CSV_COLUMNS[1:]:  # skip timestamp
        row.append(sensors.get(col, ""))
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def print_status(sensors):
    """Print a one-line status to console."""
    parts = [
        f"Out:{sensors.get('outside_temp', '?')}C",
        f"Tgt:{sensors.get('flow_target_temp', '?')}C",
        f"Feed:{sensors.get('feed_temp', '?')}C",
        f"Ret:{sensors.get('return_temp', '?')}C",
        f"dT:{sensors.get('delta_t', '?')}C",
        f"Hz:{sensors.get('compressor_hz', '?')}",
        f"COP:{sensors.get('estimated_cop', '?')}",
        f"hCOP:{sensors.get('heating_cop', '?')}",
        f"Flow:{sensors.get('flow_rate_lmin', '?')}L/m",
        f"Comp:{'ON' if sensors.get('compressor_on') else 'OFF'}",
        f"DHW:{'ON' if sensors.get('3way_valve_dhw') else 'HTG'}",
        f"SC:{'LOCK' if sensors.get('sc_lockout') else 'BOOST' if sensors.get('sc_predictive_boost') else 'ok'}",
    ]
    print(f"[{datetime.now():%H:%M:%S}] {' | '.join(parts)}")


def discover_ids():
    """Connect to ESP32 SSE, print all entity IDs once, then stop."""
    print(f"Connecting to {ESP32_URL} to discover entity IDs...\n")
    known = set(SENSORS.keys()) | set(ALL_BINARY.keys())
    seen = set()
    try:
        req = urllib.request.Request(ESP32_URL)
        with urllib.request.urlopen(req, timeout=10) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not (line.startswith("data: ") and "{" in line):
                    continue
                try:
                    data = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
                sid = data.get("id", "")
                if not sid:
                    continue
                if sid in seen:
                    break
                seen.add(sid)
                val = data.get("value", "")
                state = data.get("state", "")
                marker = "  " if sid in known else "? "
                print(f"  {marker}{sid:55s} value={val}  state={state}")
    except Exception as e:
        print(f"Connection ended: {e}")
    print(f"\nFound {len(seen)} entities ({len(seen) - len(known & seen)} unknown)")


def main():
    if "--discover" in sys.argv:
        discover_ids()
        return

    print("Ecodan Heat Pump Monitor")
    print(f"Polling {ESP32_URL} every {POLL_INTERVAL}s")
    print(f"Logging to {LOG_FILE}")
    print("Press Ctrl+C to stop\n")

    init_csv()

    while True:
        sensors = fetch_snapshot()
        if sensors:
            write_row(sensors)
            print_status(sensors)
        else:
            print(f"[{datetime.now():%H:%M:%S}] No data received")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
