# ABOUTME: Subscribes to MQTT topics from ESP32 Ecodan heat pump and logs to CSV.
# ABOUTME: Cloud replacement for monitor.py (SSE-based). Run as systemd service.

import csv
import json
import os
import threading
import time
import urllib.request
from datetime import datetime

import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_USER = "ecodan"
MQTT_PASS_FILE = "/etc/mosquitto/ecodan_password.txt"
TOPIC_PREFIX = "ecodan-heatpump"

HA_URL = "http://127.0.0.1:8123"
HA_TOKEN_FILE = "/opt/ecodan/ha-token.txt"

LOG_DIR = "/opt/ecodan/data"
LOG_FILE = os.path.join(LOG_DIR, "ecodan_log.csv")
WRITE_INTERVAL = 60  # seconds

# ESPHome MQTT object_id → CSV column name
SENSORS = {
    "outside_temp": "outside_temp",
    "feed_temp": "feed_temp",
    "return_temp": "return_temp",
    "dhw_current_temp": "dhw_temp",
    "compressor_frequency": "compressor_hz",
    "output_power": "output_power_kw",
    "estimated_output_power": "estimated_power_kw",
    "estimated_cop": "estimated_cop",
    "heating_cop": "heating_cop",
    "dhw_cop": "dhw_cop",
    "flow_rate": "flow_rate_lmin",
    "pump_speed": "pump_speed",
    "pump_consumption": "pump_watts",
    "fan_speed": "fan_rpm",
    "heating_consumed": "heating_consumed_kwh",
    "heating_delivered": "heating_delivered_kwh",
    "dhw_consumed": "dhw_consumed_kwh",
    "dhw_delivered": "dhw_delivered_kwh",
    "reported_total_daily_energy_consumption": "daily_consumed_kwh",
    "estimated_total_daily_energy_produced": "daily_produced_kwh",
    "accumulated_compressor_starts": "compressor_starts",
    "operating_runtime": "operating_hours",
    "discharge_temp": "discharge_temp",
    "refrigerant_liquid_temp": "refrigerant_temp",
    "refrigerant_condensing_temp": "condensing_temp",
    "zone_1_setpoint_value": "flow_target_temp",
}

BINARY_SENSORS = {
    "compressor": "compressor_on",
    "defrost": "defrost",
    "3-way_valve": "3way_valve_dhw",
    "booster_heater": "booster_heater",
    "water_pump_status": "water_pump",
    "water_pump_2_status": "water_pump_2",
    "dhw_eco": "dhw_eco",
}

OPTIONAL_BINARY_SENSORS = {
    "short-cycle__lockout": "sc_lockout",
    "short-cycle__predictive_boost_active": "sc_predictive_boost",
}

ALL_BINARY = {**BINARY_SENSORS, **OPTIONAL_BINARY_SENSORS}

CSV_COLUMNS = (
    ["timestamp"]
    + list(SENSORS.values())
    + list(BINARY_SENSORS.values())
    + list(OPTIONAL_BINARY_SENSORS.values())
    + ["delta_t", "room_temp"]
)

# Thread-safe storage for latest sensor values
latest = {}
lock = threading.Lock()


def load_mqtt_password():
    with open(MQTT_PASS_FILE) as f:
        return f.read().strip()


def load_ha_token():
    try:
        with open(HA_TOKEN_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def fetch_room_temp(ha_token):
    """Fetch averaged room temperature from HA Tuya thermostats."""
    if not ha_token:
        return None
    entities = [
        "climate.dnevna_soba",
        "climate.ured",
        "climate.kupatilo",
    ]
    temps = []
    for entity in entities:
        try:
            url = f"{HA_URL}/api/states/{entity}"
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {ha_token}",
                "Content-Type": "application/json",
            })
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                raw = float(data["attributes"]["current_temperature"])
                temps.append(raw / 2)  # Tuya reports 2x actual
        except Exception:
            continue
    if temps:
        return round(sum(temps) / len(temps), 1)
    return None


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[{datetime.now():%H:%M:%S}] MQTT connected (rc={reason_code})")
    client.subscribe(f"{TOPIC_PREFIX}/sensor/+/state")
    client.subscribe(f"{TOPIC_PREFIX}/binary_sensor/+/state")
    print(f"[{datetime.now():%H:%M:%S}] Subscribed to {TOPIC_PREFIX}/+/+/state")


def on_message(client, userdata, msg):
    topic_parts = msg.topic.split("/")
    if len(topic_parts) != 4:
        return

    component_type = topic_parts[1]  # "sensor" or "binary_sensor"
    object_id = topic_parts[2]
    value_str = msg.payload.decode("utf-8", errors="replace")

    with lock:
        if component_type == "sensor" and object_id in SENSORS:
            try:
                latest[SENSORS[object_id]] = float(value_str)
            except ValueError:
                latest[SENSORS[object_id]] = value_str
        elif component_type == "binary_sensor" and object_id in ALL_BINARY:
            latest[ALL_BINARY[object_id]] = 1 if value_str == "ON" else 0


def init_csv():
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
    row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    for col in CSV_COLUMNS[1:]:
        row.append(sensors.get(col, ""))
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def print_status(sensors):
    def fmt(val, decimals=1):
        return f"{val:.{decimals}f}" if isinstance(val, (int, float)) else "?"

    parts = [
        f"Out:{fmt(sensors.get('outside_temp'))}C",
        f"Tgt:{fmt(sensors.get('flow_target_temp'))}C",
        f"Feed:{fmt(sensors.get('feed_temp'))}C",
        f"Ret:{fmt(sensors.get('return_temp'))}C",
        f"dT:{fmt(sensors.get('delta_t'))}C",
        f"Hz:{fmt(sensors.get('compressor_hz'), 0)}",
        f"COP:{fmt(sensors.get('estimated_cop'))}",
        f"Room:{fmt(sensors.get('room_temp'))}C",
    ]
    print(f"[{datetime.now():%H:%M:%S}] {' | '.join(parts)}")


def csv_writer_loop(ha_token):
    """Periodically write latest sensor values to CSV."""
    while True:
        time.sleep(WRITE_INTERVAL)
        with lock:
            if not latest:
                print(f"[{datetime.now():%H:%M:%S}] No data received yet")
                continue
            snapshot = dict(latest)

        # Calculate delta_t
        feed = snapshot.get("feed_temp")
        ret = snapshot.get("return_temp")
        if feed is not None and ret is not None:
            snapshot["delta_t"] = round(feed - ret, 1)

        # Fetch room temp from HA
        room = fetch_room_temp(ha_token)
        if room is not None:
            snapshot["room_temp"] = room

        write_row(snapshot)
        print_status(snapshot)


def main():
    print("Ecodan MQTT Logger")
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Logging to {LOG_FILE}")

    mqtt_pass = load_mqtt_password()
    ha_token = load_ha_token()
    if ha_token:
        print("HA token loaded, room temp will be logged")
    else:
        print("No HA token found, room temp will be skipped")

    init_csv()

    # Start CSV writer thread
    writer_thread = threading.Thread(target=csv_writer_loop, args=(ha_token,), daemon=True)
    writer_thread.start()

    # MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, mqtt_pass)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
