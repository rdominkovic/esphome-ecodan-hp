# Oracle Cloud Migration Design

## Goal

Move heat pump monitoring infrastructure from Robert's laptop to Oracle Cloud
Free Tier so nothing depends on the laptop being on. ESP32 communicates directly
with cloud via MQTT. Home Assistant remains the dashboard/automation layer.

## Architecture

```
┌─────────────────┐          ┌──────────────────────────────────────┐
│   Home          │          │   Oracle Cloud (ARM VM, Ubuntu)      │
│                 │          │                                      │
│  ┌───────────┐  │  MQTT    │  ┌────────────┐    ┌─────────────┐  │
│  │  ESP32    │──┼──outbound──>│ Mosquitto  │<──>│    Home      │  │
│  │  CN105    │<─┼──────────┼──│ MQTT broker│    │  Assistant   │  │
│  └───────────┘  │ TLS:8883 │  └────────────┘    └──────┬──────┘  │
│                 │          │                           │         │
│  ┌───────────┐  │          │                    ┌──────┴──────┐  │
│  │ Tuya      │──┼──Tuya Cloud API──────────────>│   Tuya      │  │
│  │ thermostats│ │          │                    │ integration │  │
│  └───────────┘  │          │                    └─────────────┘  │
└─────────────────┘          │                                      │
                             │  ┌─────────────┐  ┌──────────────┐  │
                             │  │ CSV logger  │  │ daily_energy │  │
                             │  │ (MQTT sub)  │  │   cron job   │  │
                             │  └─────────────┘  └──────────────┘  │
                             │                                      │
                             │  Nginx reverse proxy (HTTPS:443)     │
                             │  SSH access (port 22)                │
                             └──────────────────────────────────────┘
```

## Data flow

1. ESP32 publishes all sensor data to MQTT broker (outbound, port 8883 TLS)
2. HA discovers entities via MQTT autodiscovery
3. HA reads Tuya thermostats via Tuya Cloud API (works from anywhere)
4. HA automation: averages 3 thermostat temps → publishes to MQTT → ESP32 receives
5. CSV logger (Python systemd service): subscribes to MQTT, writes 1-min CSV log
6. Cron: daily_energy.py generates energy reports from CSV

## Oracle Cloud VM

- Shape: VM.Standard.A1.Flex (ARM, Always Free)
- Config: 2 OCPU, 12 GB RAM (within free tier limits)
- OS: Ubuntu 22.04 ARM64 (Canonical image)
- Storage: 100 GB boot volume (free tier allows up to 200 GB)
- Region: eu-turin-1

## Software stack

| Component | Install method | Purpose |
|-----------|---------------|---------|
| Mosquitto | apt | MQTT broker with TLS on port 8883 |
| Home Assistant | Docker | Dashboard, Tuya integration, automations |
| Nginx | apt | Reverse proxy, HTTPS for HA |
| CSV logger | Python + systemd | Subscribe MQTT, write CSV every minute |
| daily_energy.py | cron (4x/day) | Energy reports |
| certbot (optional) | apt | TLS certs (self-signed without domain) |

## Open ports (Oracle security list + VM firewall)

- 22/tcp: SSH (admin, Claude Code access)
- 443/tcp: HTTPS (HA dashboard via Nginx)
- 8883/tcp: MQTTS (ESP32 connection, TLS encrypted)

## ESP32 changes

Add `mqtt:` component to `ecodan-esphome.yaml`:

```yaml
mqtt:
  broker: <oracle-vm-public-ip>
  port: 8883
  username: "ecodan"
  password: "<generated>"
  certificate_authority: <ca-cert>
```

Keep `ota:` component for local firmware updates from laptop.

## Security

- MQTT: TLS encryption + username/password authentication
- HA: Behind Nginx with HTTPS (self-signed cert, IP access)
- SSH: Key-based auth only, password auth disabled
- Oracle Cloud: Security list restricts to ports 22, 443, 8883 only

## Failure modes

- **Cloud VM down**: ESP32 continues operating with last known settings.
  Auto-adaptive algorithm runs on ESP32 firmware, not cloud. Heat pump
  keeps heating. No data logging until VM recovers.
- **Internet down at home**: Same as above. ESP32 loses MQTT connection,
  continues with last room temp value. Reconnects automatically when
  internet returns.
- **Tuya cloud down**: Room temp updates stop. ESP32 uses last value.
  Heating continues normally.

## Migration path

No downtime needed. We can set up cloud infrastructure first, test it in
parallel with existing local setup, then switch ESP32 to cloud MQTT once
everything is verified.

## Implementation steps

1. Create Oracle Cloud ARM VM instance
2. Install and configure Mosquitto MQTT broker (TLS + auth)
3. Install Docker and Home Assistant container
4. Install and configure Nginx reverse proxy
5. Configure HA: MQTT integration + Tuya integration
6. Migrate HA automations (room temp averaging)
7. Write and deploy CSV logger service
8. Migrate daily_energy.py + set up cron
9. Flash ESP32 with MQTT config (OTA from laptop)
10. End-to-end testing
11. Set up SSH key for Claude Code access
