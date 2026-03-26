# ABOUTME: Subscribes to MQTT topics from ESP32 Ecodan heat pump and logs to CSV.
# ABOUTME: Detects state transitions, tracks tariff-period COP from CN105 counters, publishes to HA via MQTT.

import csv
import json
import os
import threading
import time
import urllib.request
from datetime import datetime, date, timedelta

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
TRANSITION_FILE = os.path.join(LOG_DIR, "ecodan_transitions.csv")
COP_STATE_FILE = os.path.join(LOG_DIR, "period_cop_state.json")
HISTORICAL_FILE = os.path.join(LOG_DIR, "historical_energy.json")
WRITE_INTERVAL = 60  # seconds

# MQTT client reference for publishing (set in main)
mqtt_client = None

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
    # auto-adaptive diagnostic sensors
    "aa_cold_factor": "aa_cold_factor",
    "aa_target_delta_t": "aa_target_delta_t",
    "aa_dynamic_min_delta": "aa_dynamic_min_delta",
    "aa_room_error": "aa_room_error",
    "aa_control_mode": "aa_control_mode",
    "aa_error_factor": "aa_error_factor",
    "aa_smart_boost": "aa_smart_boost",
    "aa_calculated_flow": "aa_calculated_flow",
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
    + ["delta_t", "room_temp", "cop_per_hz"]
)

TRANSITION_COLUMNS = [
    "timestamp", "event", "from_state", "to_state", "duration_min",
    "outside_temp", "feed_temp", "return_temp", "flow_target_temp", "delta_t",
    "compressor_hz", "compressor_on", "defrost", "dhw_valve",
    "aa_mode", "aa_room_error", "aa_calculated_flow", "room_temp", "estimated_cop",
]

# Tracked fields and their event name prefixes
TRANSITION_FIELDS = {
    "compressor_on": "COMP",
    "3way_valve_dhw": "DHW",
    "defrost": "DEFROST",
    "sc_lockout": "SC_LOCKOUT",
    "aa_control_mode": "AA_MODE",
}

# Thread-safe storage for latest sensor values
latest = {}
lock = threading.Lock()

# Transition detection state (guarded by lock)
prev_state = {}
state_start_times = {}

# --- Tariff-period COP tracking ---
# Croatian electricity tariffs: summer NT 22-08, winter NT 21-07
# DST switch: last Sunday of March (to summer) / last Sunday of October (to winter)

def is_summer_time(d):
    """Check if date falls in EU summer time (last Sun of Mar to last Sun of Oct)."""
    year = d.year
    # Last Sunday of March
    mar31 = date(year, 3, 31)
    dst_start = mar31.toordinal() - (mar31.weekday() + 1) % 7
    # Last Sunday of October
    oct31 = date(year, 10, 31)
    dst_end = oct31.toordinal() - (oct31.weekday() + 1) % 7
    return date.fromordinal(dst_start) <= d <= date.fromordinal(dst_end)


def get_tariff_period(now):
    """Return 'NT' (cheap/night) or 'VT' (expensive/day) for given datetime."""
    hour = now.hour
    if is_summer_time(now.date()):
        return "NT" if (hour >= 22 or hour < 8) else "VT"
    else:
        return "NT" if (hour >= 21 or hour < 7) else "VT"


def tariff_label(period, now):
    """Human-readable label for current tariff period."""
    if period == "NT":
        return "Night (NT)"
    return "Day (VT)"


# Period COP state: tracks energy counter deltas within each tariff period
period_cop = {
    "current_tariff": None,     # "NT" or "VT"
    "period_start": None,       # ISO timestamp
    "consumed_prev": None,      # previous daily_consumed_kwh reading
    "produced_prev": None,      # previous daily_produced_kwh reading
    "period_consumed": 0.0,     # accumulated kWh consumed in current period
    "period_produced": 0.0,     # accumulated kWh produced in current period
    "history": [],              # completed periods: [{tariff, start, end, consumed, produced, cop}]
}
MAX_COP_HISTORY = 10


def save_cop_state():
    """Persist period COP history to disk for service restart recovery."""
    try:
        state = {
            "history": period_cop["history"],
            "current_tariff": period_cop["current_tariff"],
            "period_start": period_cop["period_start"],
            "period_consumed": period_cop["period_consumed"],
            "period_produced": period_cop["period_produced"],
        }
        with open(COP_STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] Failed to save COP state: {e}")


def load_cop_state():
    """Restore period COP state from disk after service restart."""
    try:
        with open(COP_STATE_FILE) as f:
            state = json.load(f)
        period_cop["history"] = state.get("history", [])[-MAX_COP_HISTORY:]
        period_cop["current_tariff"] = state.get("current_tariff")
        period_cop["period_start"] = state.get("period_start")
        period_cop["period_consumed"] = state.get("period_consumed", 0.0)
        period_cop["period_produced"] = state.get("period_produced", 0.0)
        print(f"[{datetime.now():%H:%M:%S}] Restored COP state: {len(period_cop['history'])} history entries")
    except (FileNotFoundError, json.JSONDecodeError):
        pass


def finalize_period(end_time):
    """Close the current tariff period and add to history."""
    consumed = period_cop["period_consumed"]
    produced = period_cop["period_produced"]
    cop = round(produced / consumed, 2) if consumed > 0.1 else 0.0

    entry = {
        "tariff": period_cop["current_tariff"],
        "start": period_cop["period_start"],
        "end": end_time.strftime("%Y-%m-%d %H:%M"),
        "consumed": round(consumed, 2),
        "produced": round(produced, 2),
        "cop": cop,
    }
    period_cop["history"].append(entry)
    period_cop["history"] = period_cop["history"][-MAX_COP_HISTORY:]

    print(f"[{end_time:%H:%M:%S}] >>> TARIFF {entry['tariff']} ended: "
          f"{consumed:.2f} kWh in, {produced:.2f} kWh out, COP={cop:.2f}")

    publish_cop_to_mqtt()
    save_cop_state()


def update_period_cop(snapshot):
    """Track energy counter deltas and detect tariff period transitions."""
    now = datetime.now()
    tariff = get_tariff_period(now)

    consumed = snapshot.get("daily_consumed_kwh")
    produced = snapshot.get("daily_produced_kwh")
    if consumed is None or produced is None:
        return
    if not isinstance(consumed, (int, float)) or not isinstance(produced, (int, float)):
        return

    # First run or after restart: initialize without accumulating
    if period_cop["current_tariff"] is None:
        period_cop["current_tariff"] = tariff
        period_cop["period_start"] = now.strftime("%Y-%m-%d %H:%M")
        period_cop["consumed_prev"] = consumed
        period_cop["produced_prev"] = produced
        return

    # Accumulate deltas (ignore negative = daily counter reset at midnight)
    if period_cop["consumed_prev"] is not None:
        dc = consumed - period_cop["consumed_prev"]
        dp = produced - period_cop["produced_prev"]
        if dc >= 0:
            period_cop["period_consumed"] += dc
        else:
            # Midnight reset detected — refresh yesterday's and monthly data
            publish_energy_summary()
            publish_monthly_energy()
        if dp >= 0:
            period_cop["period_produced"] += dp

    period_cop["consumed_prev"] = consumed
    period_cop["produced_prev"] = produced

    # Tariff period transition
    if tariff != period_cop["current_tariff"]:
        finalize_period(now)
        period_cop["current_tariff"] = tariff
        period_cop["period_start"] = now.strftime("%Y-%m-%d %H:%M")
        period_cop["period_consumed"] = 0.0
        period_cop["period_produced"] = 0.0
    else:
        # Publish updated current-period COP every cycle
        publish_cop_to_mqtt()


def compute_daily_energy_from_log():
    """Read all daily energy totals from all CSV logs in data dir."""
    from collections import defaultdict
    import glob
    daily = defaultdict(lambda: {"consumed": [], "produced": []})
    try:
        for f in sorted(glob.glob(os.path.join(LOG_DIR, "ecodan_log*.csv"))):
            with open(f) as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    d = row["timestamp"][:10]
                    c = float(row.get("daily_consumed_kwh") or "0")
                    p = float(row.get("daily_produced_kwh") or "0")
                    if c > 0:
                        daily[d]["consumed"].append(c)
                    if p > 0:
                        daily[d]["produced"].append(p)
    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] Failed to read energy log: {e}")
        return None
    result = {}
    for d in sorted(daily.keys()):
        c = max(daily[d]["consumed"]) if daily[d]["consumed"] else 0
        p = max(daily[d]["produced"]) if daily[d]["produced"] else 0
        result[d] = {"consumed": round(c, 1), "produced": round(p, 1),
                     "cop": round(p / c, 2) if c > 0.1 else 0.0}
    return result


def publish_energy_summary():
    """Publish yesterday + log totals to MQTT for HA display."""
    if mqtt_client is None:
        return
    all_days = compute_daily_energy_from_log()
    if not all_days:
        return

    days_sorted = sorted(all_days.keys())
    yesterday_key = (datetime.now().date() - timedelta(days=1)).isoformat()

    # Yesterday data
    yd = all_days.get(yesterday_key, {"consumed": 0, "produced": 0, "cop": 0})
    yd["date"] = yesterday_key
    mqtt_client.publish("ecodan-logger/yesterday/state", str(yd["cop"]), retain=True)
    mqtt_client.publish("ecodan-logger/yesterday/attributes", json.dumps(yd), retain=True)

    # Log totals (all days we have data for)
    total_c = sum(v["consumed"] for v in all_days.values())
    total_p = sum(v["produced"] for v in all_days.values())
    total_cop = round(total_p / total_c, 2) if total_c > 0.1 else 0.0
    totals = {
        "consumed": round(total_c, 1),
        "produced": round(total_p, 1),
        "cop": total_cop,
        "days": len(all_days),
        "from": days_sorted[0] if days_sorted else "?",
        "to": days_sorted[-1] if days_sorted else "?",
    }
    mqtt_client.publish("ecodan-logger/log_totals/state", str(total_cop), retain=True)
    mqtt_client.publish("ecodan-logger/log_totals/attributes", json.dumps(totals), retain=True)

    print(f"[{datetime.now():%H:%M:%S}] Yesterday ({yesterday_key}): "
          f"{yd['consumed']} kWh in, {yd['produced']} kWh out, COP={yd['cop']}")
    print(f"[{datetime.now():%H:%M:%S}] Log totals ({totals['from']} to {totals['to']}, {totals['days']} days): "
          f"{total_c:.1f} kWh in, {total_p:.1f} kWh out, COP={total_cop}")


def publish_monthly_energy():
    """Publish monthly energy breakdown combining historical records and CSV logs."""
    if mqtt_client is None:
        return
    try:
        # Load historical data (manually recorded months)
        with open(HISTORICAL_FILE) as f:
            historical = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[{datetime.now():%H:%M:%S}] Failed to load historical energy: {e}")
        return

    # Compute current month from CSV daily counters
    all_days = compute_daily_energy_from_log()
    if not all_days:
        return

    now = datetime.now()
    current_month_key = now.strftime("%Y-%m")
    current_month_consumed = 0.0
    current_month_produced = 0.0
    today_str = now.date().isoformat()
    for d, vals in all_days.items():
        if d.startswith(current_month_key) and d < today_str:
            current_month_consumed += vals["consumed"]
            current_month_produced += vals["produced"]

    # Build monthly rows: historical + current month from CSV
    months = []
    year_htg_con = 0
    year_dhw_con = 0
    year_htg_del = 0
    year_dhw_del = 0
    year_total_con = 0
    year_total_del = 0

    for month_key in sorted(historical.keys()):
        h = historical[month_key]
        if month_key.startswith("_"):
            continue
        htg_con = h.get("htg_consumed_kwh", 0)
        dhw_con = h.get("dhw_consumed_kwh", 0)
        htg_del = h.get("htg_delivered_kwh", 0)
        dhw_del = h.get("dhw_delivered_kwh", 0)
        total_con = h.get("consumed_kwh", htg_con + dhw_con)
        total_del = h.get("delivered_kwh", htg_del + dhw_del)
        total_cop = round(total_del / total_con, 2) if total_con > 0 else 0
        htg_cop = round(htg_del / htg_con, 2) if htg_con > 0 else 0
        dhw_cop = round(dhw_del / dhw_con, 2) if dhw_con > 0 else 0

        entry = {
            "month": month_key,
            "htg_con": htg_con, "htg_del": htg_del, "htg_cop": htg_cop,
            "dhw_con": dhw_con, "dhw_del": dhw_del, "dhw_cop": dhw_cop,
            "total_con": total_con, "total_del": total_del, "cop": total_cop,
        }
        months.append(entry)
        year_htg_con += htg_con
        year_dhw_con += dhw_con
        year_htg_del += htg_del
        year_dhw_del += dhw_del
        year_total_con += total_con
        year_total_del += total_del

    # Add current month partial (today not included since day is not complete)
    if current_month_consumed > 0 and current_month_key not in historical:
        current_cop = round(current_month_produced / current_month_consumed, 2) if current_month_consumed > 0 else 0
        entry = {
            "month": current_month_key,
            "htg_con": 0, "htg_del": 0, "htg_cop": 0,
            "dhw_con": 0, "dhw_del": 0, "dhw_cop": 0,
            "total_con": round(current_month_consumed, 1),
            "total_del": round(current_month_produced, 1),
            "cop": current_cop,
            "partial": True,
        }
        months.append(entry)
        year_total_con += current_month_consumed
        year_total_del += current_month_produced

    year_cop = round(year_total_del / year_total_con, 2) if year_total_con > 0 else 0

    year_totals = {
        "htg_con": year_htg_con, "htg_del": year_htg_del,
        "htg_cop": round(year_htg_del / year_htg_con, 2) if year_htg_con > 0 else 0,
        "dhw_con": year_dhw_con, "dhw_del": year_dhw_del,
        "dhw_cop": round(year_dhw_del / year_dhw_con, 2) if year_dhw_con > 0 else 0,
        "total_con": round(year_total_con, 1), "total_del": round(year_total_del, 1),
        "cop": year_cop,
    }

    attrs = {"months": months, "year": year_totals}
    mqtt_client.publish("ecodan-logger/monthly_energy/state", str(year_cop), retain=True)
    mqtt_client.publish("ecodan-logger/monthly_energy/attributes", json.dumps(attrs), retain=True)

    print(f"[{datetime.now():%H:%M:%S}] Monthly energy: {len(months)} months, "
          f"year COP={year_cop}, consumed={year_total_con:.0f}, delivered={year_total_del:.0f}")


def publish_cop_discovery():
    """Publish HA MQTT auto-discovery config for the period COP sensor."""
    if mqtt_client is None:
        return
    config = {
        "name": "Ecodan Period COP",
        "unique_id": "ecodan_period_cop",
        "state_topic": "ecodan-logger/period_cop/state",
        "json_attributes_topic": "ecodan-logger/period_cop/attributes",
        "unit_of_measurement": "",
        "icon": "mdi:heat-pump-outline",
        "device": {
            "identifiers": ["ecodan_logger"],
            "name": "Ecodan Logger",
            "manufacturer": "Custom",
        },
    }
    mqtt_client.publish(
        "homeassistant/sensor/ecodan_period_cop/config",
        json.dumps(config),
        retain=True,
    )

    # Live daily COP sensor
    daily_config = {
        "name": "Ecodan Daily COP",
        "unique_id": "ecodan_daily_cop",
        "state_topic": "ecodan-logger/daily_cop/state",
        "unit_of_measurement": "",
        "icon": "mdi:heat-pump-outline",
        "device": {
            "identifiers": ["ecodan_logger"],
            "name": "Ecodan Logger",
            "manufacturer": "Custom",
        },
    }
    mqtt_client.publish(
        "homeassistant/sensor/ecodan_daily_cop/config",
        json.dumps(daily_config),
        retain=True,
    )
    # Log totals sensor
    totals_config = {
        "name": "Ecodan Log Totals",
        "unique_id": "ecodan_log_totals",
        "state_topic": "ecodan-logger/log_totals/state",
        "json_attributes_topic": "ecodan-logger/log_totals/attributes",
        "icon": "mdi:sigma",
        "device": {
            "identifiers": ["ecodan_logger"],
            "name": "Ecodan Logger",
            "manufacturer": "Custom",
        },
    }
    mqtt_client.publish(
        "homeassistant/sensor/ecodan_log_totals/config",
        json.dumps(totals_config),
        retain=True,
    )

    # Yesterday energy sensor
    yesterday_config = {
        "name": "Ecodan Yesterday",
        "unique_id": "ecodan_yesterday",
        "state_topic": "ecodan-logger/yesterday/state",
        "json_attributes_topic": "ecodan-logger/yesterday/attributes",
        "icon": "mdi:calendar-arrow-left",
        "device": {
            "identifiers": ["ecodan_logger"],
            "name": "Ecodan Logger",
            "manufacturer": "Custom",
        },
    }
    mqtt_client.publish(
        "homeassistant/sensor/ecodan_yesterday/config",
        json.dumps(yesterday_config),
        retain=True,
    )
    # Monthly energy sensor
    monthly_config = {
        "name": "Ecodan Monthly Energy",
        "unique_id": "ecodan_monthly_energy",
        "state_topic": "ecodan-logger/monthly_energy/state",
        "json_attributes_topic": "ecodan-logger/monthly_energy/attributes",
        "icon": "mdi:calendar-month",
        "device": {
            "identifiers": ["ecodan_logger"],
            "name": "Ecodan Logger",
            "manufacturer": "Custom",
        },
    }
    mqtt_client.publish(
        "homeassistant/sensor/ecodan_monthly_energy/config",
        json.dumps(monthly_config),
        retain=True,
    )
    print(f"[{datetime.now():%H:%M:%S}] Published HA MQTT discovery for COP sensors")
    publish_energy_summary()
    publish_monthly_energy()


def publish_cop_to_mqtt():
    """Publish current + historical period COP data to MQTT."""
    if mqtt_client is None:
        return

    # State = last completed period's COP
    history = period_cop["history"]
    state = str(history[-1]["cop"]) if history else "0"
    mqtt_client.publish("ecodan-logger/period_cop/state", state, retain=True)

    # Build table data: current period + history
    current = {
        "tariff": period_cop["current_tariff"] or "?",
        "start": period_cop["period_start"] or "?",
        "end": "now",
        "consumed": round(period_cop["period_consumed"], 2),
        "produced": round(period_cop["period_produced"], 2),
        "cop": round(
            period_cop["period_produced"] / period_cop["period_consumed"], 2
        ) if period_cop["period_consumed"] > 0.1 else 0.0,
    }

    attrs = {
        "current_period": current,
        "history": list(reversed(history)),
    }
    mqtt_client.publish(
        "ecodan-logger/period_cop/attributes",
        json.dumps(attrs),
        retain=True,
    )

    # Daily COP from counters
    with lock:
        dc = latest.get("daily_consumed_kwh")
        dp = latest.get("daily_produced_kwh")
    if dc and dp and dc > 0:
        daily_cop = round(dp / dc, 2)
        mqtt_client.publish("ecodan-logger/daily_cop/state", str(daily_cop), retain=True)


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
    publish_cop_discovery()


def event_name(field, old_val, new_val):
    """Generate event name from field and transition direction."""
    prefix = TRANSITION_FIELDS[field]
    if field == "aa_control_mode":
        return "AA_MODE"
    if new_val == 1:
        suffixes = {
            "compressor_on": "ON",
            "3way_valve_dhw": "START",
            "defrost": "START",
            "sc_lockout": "ON",
        }
        return f"{prefix}_{suffixes[field]}"
    else:
        suffixes = {
            "compressor_on": "OFF",
            "3way_valve_dhw": "END",
            "defrost": "END",
            "sc_lockout": "OFF",
        }
        return f"{prefix}_{suffixes[field]}"


def get_context_snapshot():
    """Build a context dict from current latest values for transition logging."""
    feed = latest.get("feed_temp")
    ret = latest.get("return_temp")
    delta_t = round(feed - ret, 1) if feed is not None and ret is not None else ""
    return {
        "outside_temp": latest.get("outside_temp", ""),
        "feed_temp": latest.get("feed_temp", ""),
        "return_temp": latest.get("return_temp", ""),
        "flow_target_temp": latest.get("flow_target_temp", ""),
        "delta_t": delta_t,
        "compressor_hz": latest.get("compressor_hz", ""),
        "compressor_on": latest.get("compressor_on", ""),
        "defrost": latest.get("defrost", ""),
        "dhw_valve": latest.get("3way_valve_dhw", ""),
        "aa_mode": latest.get("aa_control_mode", ""),
        "aa_room_error": latest.get("aa_room_error", ""),
        "aa_calculated_flow": latest.get("aa_calculated_flow", ""),
        "room_temp": latest.get("room_temp", ""),
        "estimated_cop": latest.get("estimated_cop", ""),
    }


def write_transition(event, from_val, to_val, duration_min, ctx):
    """Write a transition row to the transition CSV file."""
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        event,
        from_val,
        to_val,
        duration_min,
    ]
    for col in TRANSITION_COLUMNS[5:]:
        row.append(ctx.get(col, ""))
    with open(TRANSITION_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def print_transition(event, duration_min, ctx):
    """Print a human-readable transition line to stdout."""
    def fmt(val, decimals=1):
        if isinstance(val, (int, float)):
            return f"{val:.{decimals}f}"
        return "?"

    duration_str = f"{duration_min:.1f}min" if duration_min != "" else "?min"

    # Choose label based on event type
    if event.endswith("_ON") or event.endswith("_START"):
        dur_label = "off"
    elif event.endswith("_OFF") or event.endswith("_END"):
        dur_label = "on"
    elif event == "AA_MODE":
        dur_label = "prev"
    else:
        dur_label = "dur"

    parts = [
        f"{dur_label}={duration_str}",
        f"OT={fmt(ctx.get('outside_temp', ''))}",
        f"Feed={fmt(ctx.get('feed_temp', ''))}",
        f"Tgt={fmt(ctx.get('flow_target_temp', ''))}",
        f"Hz={fmt(ctx.get('compressor_hz', ''), 0)}",
        f"AA:{fmt(ctx.get('aa_mode', ''), 0)}",
        f"Room={fmt(ctx.get('room_temp', ''))}",
    ]
    print(f"[{datetime.now():%H:%M:%S}] >>> {event:<16s} {' | '.join(parts)}")


def check_transitions(field, new_val):
    """Check for state transition and log if detected. Must be called with lock held."""
    now = time.monotonic()

    if field not in prev_state:
        # First value seen — initialize without logging
        prev_state[field] = new_val
        state_start_times[field] = now
        return

    old_val = prev_state[field]
    if old_val == new_val:
        return

    # Transition detected
    start_time = state_start_times.get(field, now)
    duration_sec = now - start_time
    duration_min = round(duration_sec / 60, 1)

    evt = event_name(field, old_val, new_val)
    ctx = get_context_snapshot()

    write_transition(evt, old_val, new_val, duration_min, ctx)
    print_transition(evt, duration_min, ctx)

    prev_state[field] = new_val
    state_start_times[field] = now


def on_message(client, userdata, msg):
    topic_parts = msg.topic.split("/")
    if len(topic_parts) != 4:
        return

    component_type = topic_parts[1]  # "sensor" or "binary_sensor"
    object_id = topic_parts[2]
    value_str = msg.payload.decode("utf-8", errors="replace")

    with lock:
        if component_type == "sensor" and object_id in SENSORS:
            csv_name = SENSORS[object_id]
            try:
                val = float(value_str)
            except ValueError:
                val = value_str
            latest[csv_name] = val
            # Check aa_control_mode transitions (compare as rounded int)
            if csv_name == "aa_control_mode" and isinstance(val, (int, float)):
                check_transitions(csv_name, int(round(val)))
        elif component_type == "binary_sensor" and object_id in ALL_BINARY:
            csv_name = ALL_BINARY[object_id]
            val = 1 if value_str == "ON" else 0
            latest[csv_name] = val
            # Check binary transition fields
            if csv_name in TRANSITION_FIELDS:
                check_transitions(csv_name, val)


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


def init_transition_csv():
    if os.path.exists(TRANSITION_FILE):
        with open(TRANSITION_FILE, "r") as f:
            reader = csv.reader(f)
            existing_cols = next(reader, None)
        if existing_cols == TRANSITION_COLUMNS:
            print(f"Appending to {TRANSITION_FILE}")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated = TRANSITION_FILE.replace(".csv", f"_{ts}.csv")
        os.rename(TRANSITION_FILE, rotated)
        print(f"Transition column change detected, rotated to {rotated}")
    with open(TRANSITION_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(TRANSITION_COLUMNS)
    print(f"Created {TRANSITION_FILE}")


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
        f"Mode:{fmt(sensors.get('aa_control_mode'), 0)}",
        f"Flow:{fmt(sensors.get('aa_calculated_flow'))}C",
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
            # Also store in latest so transitions can reference it
            with lock:
                latest["room_temp"] = room

        # COP/Hz efficiency ratio (COP per 10 Hz)
        cop = snapshot.get("estimated_cop")
        hz = snapshot.get("compressor_hz")
        if cop and hz and hz > 0 and cop > 0:
            snapshot["cop_per_hz"] = round(cop / hz * 10, 3)

        # Track tariff-period COP from energy counters
        update_period_cop(snapshot)

        write_row(snapshot)
        print_status(snapshot)


def main():
    print("Ecodan MQTT Logger")
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Logging to {LOG_FILE}")
    print(f"Transitions to {TRANSITION_FILE}")

    mqtt_pass = load_mqtt_password()
    ha_token = load_ha_token()
    if ha_token:
        print("HA token loaded, room temp will be logged")
    else:
        print("No HA token found, room temp will be skipped")

    init_csv()
    init_transition_csv()
    load_cop_state()

    # MQTT client (must be created before writer thread starts)
    global mqtt_client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, mqtt_pass)
    client.on_connect = on_connect
    client.on_message = on_message
    mqtt_client = client

    # Start CSV writer thread
    writer_thread = threading.Thread(target=csv_writer_loop, args=(ha_token,), daemon=True)
    writer_thread.start()

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
