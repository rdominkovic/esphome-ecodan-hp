# Ecodan Heat Pump System

## Equipment

| Component    | Model                  | Qty |
| ------------ | ---------------------- | --- |
| Outdoor unit | Mitsubishi SUZ-SWM80VA | 1   |
| Hydrobox     | Mitsubishi ERSD-VM2D   | 1   |

### Official Documentation

- Outdoor unit engineering manual: `SUZ-SWM80VA2.pdf`
- Hydrobox service manual: `EHST-D(C)-MHCW_SM.pdf`
- DHW storage tank technical data: `neotherm-acu-akumulacijski-spremnici-tehnicki-poda_5d660bcfcaaee.pdf`
- House floor plan: `Dominković - idejno konačno.pdf`
- Mechanical engineering project: `Mapa 5_ glavni strojarski projekt.pdf`

## Building

### General

- **Location**: Belišće, Slavonia, Croatia
- **Address**: Ivana Frana Gundulića 6
- **Type**: Single-family house, single storey (ground floor only)
- **Total area**: ~147 m² (including garage 32.2 m²)
- **Living area**: ~115 m² (excluding garage)

### Room Layout (from floor plan)

| Room                 | Area (m²) |
| -------------------- | --------- |
| Living room + Dining | 32.2      |
| Garage               | 32.2      |
| Hallway              | 14.2      |
| Bedroom              | 14.8      |
| Children's room 1    | 11.0      |
| Kitchen              | 10.3      |
| Children's room 2    | 10.2      |
| WC / Laundry         | 6.2       |
| Bathroom             | 5.6       |
| Storage              | 5.2       |
| Entrance             | 5.0       |

### Insulation

Project calculated with lower insulation values. Actual installed insulation is better:

| Element     | Project value | Actual installed |
| ----------- | ------------- | ---------------- |
| Walls (EPS) | 10 cm         | **15 cm**        |
| Floor (XPS) | 2 cm          | **8 cm**         |
| Attic       | 20 cm         | 20 cm            |

The actual heat losses are significantly lower than calculated due to thicker wall and floor insulation.

### Heat Loss Calculations (from project - conservative, based on thinner insulation)

Design conditions: indoor 23 C (24 C bathroom), outdoor design temperature per Croatian norms (Slavonia).

| Room               | Area (m²) | Heat loss Qn (W) | Transmission (W) | Ventilation (W) | Installed capacity (W) | W/m² |
| ------------------ | --------- | ---------------- | ---------------- | --------------- | ---------------------- | ---- |
| Entrance + Hallway | 19        | 932              | 579              | 353             | 1,410                  | 73   |
| Bedroom            | 14        | 944              | 672              | 272             | 1,034                  | 69   |
| Children's room 1  | 10        | 705              | 517              | 188             | 723                    | 70   |
| Children's room 2  | 11        | 593              | 391              | 202             | 779                    | 70   |
| Living + Dining    | 32        | 2,024            | 1,431            | 593             | 2,259                  | 70   |
| Kitchen            | 10        | 709              | 519              | 190             | 802                    | 77   |
| WC                 | 6         | 306              | 192              | 114             | 481                    | 77   |
| Bathroom           | 5         | 498              | 181              | 317             | 631                    | 112  |
| Garage             | 32        | 2,192            | 1,521            | 671             | 2,197                  | 68   |
| **Total**          |           | **8,903**        | **6,003**        | **2,900**       | **10,316**             |      |

With actual 15cm EPS walls and 8cm XPS floor, real heat losses are estimated to be 20-30% lower than above.

### Cooling Load (from project)

| Room            | Cooling load (W) |
| --------------- | ---------------- |
| Living + Dining | 2,585            |
| Kitchen         | 589              |
| **Total**       | **3,174**        |

## Outdoor Unit - SUZ-SWM80VA2

### Specifications

| Parameter             | Value                           |
| --------------------- | ------------------------------- |
| Power supply          | 1ph, 230V, 50Hz                 |
| Max current           | 17.3A                           |
| Breaker size          | 20A                             |
| Compressor            | Hermetic twin rotary (inverter) |
| Compressor model      | SVB220FUAM2T                    |
| Motor output          | 1.5 kW                          |
| Refrigerant           | R32                             |
| Refrigerant charge    | 1.1 kg                          |
| Max refrigerant       | 1.7 kg                          |
| Defrost method        | Reverse cycle                   |
| Noise (heating)       | 46 dBA                          |
| Dimensions            | 840 x 330 x 880 mm (W x D x H)  |
| Weight                | 53 kg                           |
| Pipe liquid           | 6.35 mm (1/4") flared           |
| Pipe gas              | 12.7 mm (1/2") flared           |
| Max piping length     | 46m                             |
| Max height difference | 30m                             |

### Operating Range

| Mode                       | Outdoor temperature |
| -------------------------- | ------------------- |
| Heating                    | -25 to +24 C        |
| DHW                        | -25 to +35 C        |
| Cooling                    | +10 to +46 C        |
| Max outlet water (heating) | +60 C               |
| Min outlet water (cooling) | +5 C                |
| Water flow rate            | 10.9 - 21.5 L/min   |

### Nominal Performance (EN14511)

| Condition       | Capacity | COP  | Power input | Flow rate  |
| --------------- | -------- | ---- | ----------- | ---------- |
| Heating A7/W35  | 6.00 kW  | 5.10 | 1.18 kW     | 17.2 L/min |
| Heating A2/W35  | 7.50 kW  | 3.50 | 2.14 kW     | 21.5 L/min |
| Cooling A35/W7  | 6.70 kW  | 3.20 | 2.09 kW     | 19.2 L/min |
| Cooling A35/W18 | 6.70 kW  | 5.06 | 1.32 kW     | 19.2 L/min |

### Detailed Performance Table (Max Capacity)

Capacity in kW, COP values at various outdoor and water outlet temperatures.

| Outdoor | W25 cap | W25 COP | W35 cap | W35 COP | W40 cap | W40 COP | W45 cap | W45 COP | W50 cap | W50 COP | W55 cap | W55 COP | W60 cap | W60 COP |
| ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| -25 C   | -       | -       | 4.8     | 1.81    | 4.4     | 1.64    | -       | -       | -       | -       | -       | -       | -       | -       |
| -20 C   | -       | -       | 6.0     | 1.94    | 5.6     | 1.81    | 5.2     | 1.67    | -       | -       | -       | -       | -       | -       |
| -15 C   | -       | -       | 7.0     | 2.26    | 6.6     | 2.05    | 6.1     | 1.83    | 6.0     | 1.67    | 5.9     | 1.50    | -       | -       |
| -10 C   | 8.6     | 2.82    | 8.0     | 2.36    | 7.3     | 2.20    | 7.0     | 1.90    | 6.7     | 1.73    | 6.3     | 1.56    | -       | -       |
| -7 C    | 9.0     | 3.30    | 8.0     | 2.63    | 7.7     | 2.30    | 7.4     | 1.96    | 7.0     | 1.78    | 6.6     | 1.59    | -       | -       |
| 2 C     | 8.8     | 3.78    | 8.4     | 3.15    | 8.2     | 2.84    | 8.0     | 2.52    | 7.8     | 2.33    | 7.5     | 2.13    | 6.5     | 1.94    |
| 7 C     | 10.4    | 4.58    | 10.1    | 3.79    | 10.0    | 3.40    | 9.8     | 3.00    | 9.0     | 2.77    | 8.2     | 2.54    | 6.0     | 2.31    |
| 12 C    | 10.5    | 5.90    | 10.1    | 4.79    | 9.9     | 4.24    | 9.7     | 3.68    | 9.0     | 3.36    | 8.2     | 3.03    | 6.0     | 2.71    |
| 15 C    | 11.5    | 6.41    | 11.0    | 5.19    | 10.8    | 4.58    | 10.5    | 3.97    | 9.4     | 3.67    | 8.2     | 3.36    | 6.0     | 3.06    |
| 20 C    | 13.2    | 6.94    | 12.7    | 5.87    | 12.5    | 5.16    | 12.2    | 4.44    | 10.2    | 4.18    | 8.2     | 3.92    | 6.0     | 3.66    |

### Nominal Capacity Table

| Outdoor | W25 cap | W25 COP | W35 cap | W35 COP | W40 cap | W40 COP | W45 cap | W45 COP | W50 cap | W50 COP | W55 cap | W55 COP | W60 cap | W60 COP |
| ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| -25 C   | -       | -       | 4.8     | 1.81    | 4.4     | 1.64    | -       | -       | -       | -       | -       | -       | -       | -       |
| -20 C   | -       | -       | 6.0     | 1.94    | 5.6     | 1.81    | 5.2     | 1.67    | -       | -       | -       | -       | -       | -       |
| -15 C   | -       | -       | 7.0     | 2.26    | 6.6     | 2.05    | 6.1     | 1.83    | 6.0     | 1.67    | 5.9     | 1.50    | -       | -       |
| -10 C   | 7.0     | 2.80    | 7.0     | 2.35    | 7.0     | 2.13    | 7.0     | 1.90    | 6.7     | 1.73    | 6.3     | 1.56    | -       | -       |
| -7 C    | 7.0     | 3.79    | 7.0     | 2.90    | 7.0     | 2.46    | 7.0     | 2.01    | 7.0     | 1.78    | 6.6     | 1.59    | -       | -       |
| 2 C     | 7.5     | 4.39    | 7.5     | 3.50    | 7.5     | 3.06    | 7.5     | 2.61    | 7.8     | 2.33    | 7.5     | 2.17    | 6.5     | 1.94    |
| 7 C     | 6.0     | 6.63    | 6.0     | 5.10    | 6.0     | 4.34    | 6.0     | 3.57    | 6.0     | 3.29    | 6.0     | 3.00    | 6.0     | 2.31    |
| 12 C    | 7.5     | 7.01    | 7.5     | 5.54    | 7.5     | 4.81    | 7.5     | 4.07    | 7.5     | 3.60    | 7.5     | 3.12    | 6.0     | 2.71    |
| 15 C    | 7.5     | 8.12    | 7.5     | 6.34    | 7.5     | 5.45    | 7.5     | 4.56    | 7.5     | 4.02    | 7.5     | 3.47    | 6.0     | 3.06    |
| 20 C    | 7.5     | 9.79    | 7.5     | 7.88    | 7.5     | 6.67    | 7.5     | 5.45    | 7.5     | 4.74    | 7.5     | 4.03    | 6.0     | 3.66    |

## Hydrobox - ERSD-VM2D

### Specifications (from service manual)

| Parameter                        | Value                           |
| -------------------------------- | ------------------------------- |
| DHW tank                         | 200L                            |
| Dimensions                       | 1600 x 595 x 680 mm (H x W x D) |
| Primary circuit pump             | Grundfos UPM2 15 70-130         |
| Sanitary circuit pump            | Grundfos UPSO 15-60 130 CIL2    |
| Primary connections              | 28mm compression                |
| DHW connections                  | 22mm compression                |
| Pressure relief valve (primary)  | 3 bar                           |
| Pressure relief valve (DHW)      | 10 bar                          |
| Flow sensor min                  | 5.0 L/min                       |
| Flow temp target range (heating) | 25 - 60 C                       |
| Room temp target range (heating) | 10 - 30 C                       |
| Max DHW temperature              | 70 C                            |
| DHW heat-up time 15-65 C         | 22.75 min                       |
| DHW reheat 70% to 65 C           | 17.17 min                       |

## DHW Storage Tank - NeoTHERM Acu 200L (Dual Coil)

### Specifications (from technical data sheet)

| Parameter                         | Value                                             |
| --------------------------------- | ------------------------------------------------- |
| Model                             | NeoTHERM Acu 200L Solar Duo (dual heat exchanger) |
| Net capacity                      | 187 L                                             |
| Outer diameter                    | 600 mm                                            |
| Inner diameter                    | 500 mm                                            |
| Height                            | 1230 mm                                           |
| Empty weight                      | 88 kg                                             |
| Insulation                        | 50 mm                                             |
| Standing heat loss (ΔT 45K)       | 1.4 kWh/24h                                       |
| Energy class                      | B                                                 |
| Max working temperature           | 95 C                                              |
| Max working pressure (tank)       | 8 bar                                             |
| Max working pressure (exchangers) | 6 bar                                             |

### Heat Exchangers

| Exchanger         | Surface area | Volume | Power (60-80 C) | Flow rate (60-80 C) |
| ----------------- | ------------ | ------ | --------------- | ------------------- |
| C1 (lower, HP)    | 0.85 m²      | 5.10 L | 26 kW           | 520 L/h             |
| C2 (upper, solar) | 0.62 m²      | 3.83 L | 16 kW           | 440 L/h             |

### Connections (160-500L models)

| Connection          | Size   |
| ------------------- | ------ |
| Cold water inlet    | F 1"   |
| Hot water outlet    | F 1"   |
| Exchanger C1 in/out | F 1"   |
| Exchanger C2 in/out | F 1"   |
| Electric heater     | F 1½"  |
| Recirculation       | F 3/4" |
| Thermometer         | F 1/2" |
| Sensor ports        | F 1/2" |
| Manhole             | Ø180   |

### Tank Heat Loss Estimate (actual conditions)

- Tank at 43 C, garage ambient 16.4 C → ΔT = 26.6 K
- Scaled heat loss: 1.4 × (26.6/45) ≈ **0.83 kWh/day** ≈ **303 kWh/year**
- With only 50mm insulation in a 16.4 C garage, tank standing losses are non-trivial

## Installation - Hydraulics

### Piping

- **Primary circuit pipes**: 28mm (from heat pump to manifold)
- **DHW pipes**: 22mm
- **Buffer tank**: 100L
- **Mixing valve**: NOT installed (SW2-6 OFF, confirmed Invalid in controller)
- **System type**: 1-zone, weather compensation only, no room thermostat connected to FTC

### Underfloor Heating Design (from project - conservative)

Project design values (actual system differs in number of circuits):

| Parameter                   | Value                    |
| --------------------------- | ------------------------ |
| Design flow temperature     | 45 C                     |
| Design return temperature   | 39.2 C                   |
| Design delta T              | 5.8 C                    |
| Total pipe length (project) | 1,119.8 m                |
| Total installed capacity    | 10,135 W (floor)         |
| Total with radiator         | 11,498 W                 |
| Total water volume          | 148.63 L                 |
| Total flow rate             | 1,700 kg/h (~28.3 L/min) |
| Max pressure drop           | 24.67 kPa                |
| Pipe material               | PEXc d16x2.0mm           |

### Actual Heating Circuits

Total: 11 circuits (actual installation differs from project's 14)

| Circuit | Length | Room                      | Thermostat                                     |
| ------- | ------ | ------------------------- | ---------------------------------------------- |
| 1       | 110m   | Garage                    | Always OFF                                     |
| 2       | 51m    | Bathroom                  | Own thermostat                                 |
| 3       | 52m    | WC / Laundry              | Own thermostat                                 |
| 4       | 100m   | Kitchen                   | Shared (circuits 4-7)                          |
| 5       | 92m    | Dining room               | Shared (circuits 4-7)                          |
| 6       | 90m    | Living room               | Shared (circuits 4-7)                          |
| 7       | 100m   | Living room (window side) | Shared (circuits 4-7)                          |
| 8       | 97m    | Children's room 1         | Own thermostat                                 |
| 9       | 96m    | Children's room 2         | Own thermostat                                 |
| 10      | 80m    | Bedroom                   | Shared (circuits 10-11), thermostat in bedroom |
| 11      | -      | Bedroom / Hallway         | Shared (circuits 10-11), thermostat in bedroom |

**Total active pipe length**: ~858m (excluding garage)

### Thermostat Zones

| Zone | Rooms                          | Thermostat location        |
| ---- | ------------------------------ | -------------------------- |
| -    | Garage                         | Always OFF                 |
| 1    | Bathroom                       | Bathroom                   |
| 2    | WC / Laundry                   | WC / Laundry               |
| 3    | Kitchen + Dining + Living room | Kitchen/Dining/Living area |
| 4    | Children's room 1              | Children's room 1          |
| 5    | Children's room 2              | Children's room 2          |
| 6    | Bedroom + Hallway              | Bedroom                    |

### Pipe Heat Loss Analysis

All pipes between outdoor unit, hydrobox, buffer tank, and manifold run through the garage (ambient ~16.4 C with floor heating circuit OFF).

| Pipe                            | Diameter | Length | Insulation |
| ------------------------------- | -------- | ------ | ---------- |
| Primary circuit (HP ↔ manifold) | 28 mm    | 17.5 m | **None**   |
| DHW circuit                     | 22 mm    | 7.0 m  | **None**   |

#### Heat Loss Calculations (uninsulated copper pipe)

Natural convection from bare copper pipe, using standard heat transfer coefficients.

**Heating mode** (flow ~32 C, garage 16.4 C, ΔT ≈ 15.6 K):

| Pipe         | Loss per meter | Total loss |
| ------------ | -------------- | ---------- |
| 28mm × 17.5m | ~14 W/m        | ~245 W     |
| 22mm × 7.0m  | ~10 W/m        | ~70 W      |
| **Total**    |                | **~316 W** |

**DHW mode** (flow ~45 C, garage 16.4 C, ΔT ≈ 28.6 K):

| Pipe         | Loss per meter | Total loss |
| ------------ | -------------- | ---------- |
| 28mm × 17.5m | ~26 W/m        | ~455 W     |
| 22mm × 7.0m  | ~18 W/m        | ~126 W     |
| **Total**    |                | **~578 W** |

#### Seasonal Impact Estimate

- Heating runs ~5,000 hours/season → 316W × 5,000h ≈ **1,580 kWh lost** (raw estimate)
- Realistic estimate with cycling: **~800 kWh/season** lost to uninsulated pipes
- This is a massive loss — nearly half of the total heating delivered (1,063 kWh as of Feb 18)

#### Insulation Effectiveness

| Insulation thickness | Loss reduction | Estimated savings |
| -------------------- | -------------- | ----------------- |
| 9 mm foam            | ~55%           | ~440 kWh/season   |
| 13 mm foam           | ~68%           | ~545 kWh/season   |

**Pipe insulation is the highest-priority, most cost-effective optimization.**

## Current Settings

### Weather Compensation Curve (Heating)

| Outdoor temp | Flow water temp |
| ------------ | --------------- |
| -10 C        | 40 C            |
| +15 C        | 28 C            |

Linear interpolation between these two points. Offset: **+1 C** (actual flow temp is 1C above curve value).

### DHW (Domestic Hot Water)

- **Target temperature**: 43 C
- **Schedule**: 19:00 - 23:00 and 05:00 - 07:00 (OFF outside these windows)
- **Mode**: Eco
- **Legionella prevention**: 60 C (periodic)

### Other Settings

- **Bypass valve**: Disabled (closed)
- **Zone 1 flow setpoint**: 31 C (from weather compensation at current outdoor temp)
- **Buffer tank**: 100 L (installed to prevent short cycling)

## ESP32 Monitoring

ESP32-WROOM-32D connected via CN105 connector to hydrobox.
ESPHome firmware: gekkekoe/esphome-ecodan-hp
Device IP: 192.168.1.230 (WiFi "HOME" network)

### Configuration

- **Board**: ESP32-WROOM-32D (not S3)
- **UART**: RX GPIO17, TX GPIO16 (CN105 protocol)
- **Packages**: base, energy, cpu-monitoring, request-codes, auto-adaptive, esp32, zone1, server-control-z1, ecodan-labels-en, debug, wifi
- **Web server**: Enabled (port 80)
- **API**: Enabled (for Home Assistant)
- **OTA**: Enabled

### Available Sensors (60+ total)

Key sensors from the ecodan-hp integration:

**Efficiency**: estimated_cop, heating_cop, dhw_cop, cooling_cop
**Temperatures**: hp_feed_temp, hp_return_temp, z1_feed_temp, z1_return_temp, dhw_temp, outside_temp, refrigerant_temp, discharge_temp, internal_add_up_temp
**Energy**: energy_consumed_heating, energy_consumed_dhw, energy_delivered_heating, energy_delivered_dhw, daily_energy_consumed, daily_energy_produced
**Compressor**: compressor_frequency, compressor_starts, operating_hours
**Flow**: flow_rate, pump_speed, pump_duty
**System**: fan_speed, defrost_status, booster_heater, 3_way_valve

## Energy Data (Season 2024-2025)

### Cumulative Totals (as of February 18, 2025)

| Category  | Consumed (kWh) | Delivered (kWh) | COP      |
| --------- | -------------- | --------------- | -------- |
| Heating   | 470            | 1,063           | 2.26     |
| DHW       | 71             | 139             | 1.96     |
| **Total** | **542**        | **1,203**       | **2.22** |

### Expected COP vs Actual

Based on the outdoor unit performance tables and the weather compensation curve settings:

| Outdoor temp | Flow temp (curve+offset) | Expected COP (from specs) | Actual COP |
| ------------ | ------------------------ | ------------------------- | ---------- |
| +15 C        | 29 C (~W25-W35)          | 5.2 - 6.3                 | ~2.5       |
| +12 C        | 30 C (~W25-W35)          | 4.8 - 5.9                 | ~2.3       |
| +7 C         | 32 C (~W35)              | 3.8 - 5.1                 | ~2.0       |
| +2 C         | 34 C (~W35)              | 3.2 - 3.5                 | ~1.8       |
| -7 C         | 38 C (~W40)              | 2.3                       | TBD        |
| -10 C        | 41 C (~W40-W45)          | 1.9 - 2.2                 | TBD        |

The actual COP is roughly **40-60% of the expected COP** across all outdoor temperatures.

## COP Diagnostics

### Sensor Validity

THW6 (Zone1 flow), THW7 (Zone1 return), THWB1 (Boiler flow), THWB2 (Boiler return) are **NOT installed** (confirmed blank on controller Thermistor reading screen). The following ESP32 readings are therefore INVALID and should be ignored:

| ESP32 sensor name  | Reads | Actual status         |
| ------------------ | ----- | --------------------- |
| Z1 Feed Temp       | 25 C  | Invalid (THW6 absent) |
| Z1 Return Temp     | 25 C  | Invalid (THW7 absent) |
| Boiler Flow Temp   | 25 C  | Invalid (THWB1 absent)|
| Boiler Return Temp | 25 C  | Invalid (THWB2 absent)|
| Mixing Tank Temp   | 25 C  | Invalid (no mixing tank configured) |
| Mixing Valve Step  | 124   | Invalid (no mixing valve, code 177 = 0) |

Valid sensors are THW1 (Feed Temp), THW2 (Return Temp), THW5 (DHW tank), TH7 (Outside).

### FTC DIP Switch Configuration (verified)

| Switch | Setting | Meaning                              |
| ------ | ------- | ------------------------------------ |
| SW2-3  | ON      | Booster heater capacity restriction  |
| SW2-4  | ON      | Cooling mode active                  |
| SW2-6  | OFF     | No mixing tank                       |
| SW2-7  | OFF     | 2-zone inactive (1-zone only)        |
| SW2-8  | ON      | Flow sensor present                  |

DIP SW1 code: 0026, DIP SW2 code: 008C.

### FTC Operation Settings

| Parameter | Value | Default | Range | Notes |
| --------- | ----- | ------- | ----- | ----- |
| Pump speed (heating) | **5** | 5 | 1-5 | Tested 5 → 4 → 3 → reverted to 5 (see changelog) |
| Pump speed (DHW) | **5** | 5 | 1-5 | Unchanged, max flow for DHW heat exchanger |
| Thermo diff. lower limit | **-7 C** | -5 | -9 to -1 | Controls restart threshold below target flow temp |
| Thermo diff. upper limit | +5 C | +5 | +3 to +5 | Controls shutdown threshold above target flow temp |
| Thermo diff. interval | 10 min | 10 | 1-60 | FTC recalculation interval |
| Minimum flow temperature | 30 C | 30 | 25-45 | Minimum target flow temp |
| Maximum flow temperature | 50 C | 50 | 35-60 | Maximum target flow temp |

### Short-Cycle Protection (ESPHome auto-adaptive)

Software-based protection in the ESPHome ecodan-hp integration (package `confs/auto-adaptive.yaml`).

**Reactive lockout**: If compressor runs shorter than minimum on-time, blocks restart for lockout duration.

**Predictive prevention**: Monitors flow temp overshoot. If actual flow exceeds requested flow by threshold for longer than duration, applies +0.5 C boost to extend compressor runtime.

| Parameter | Value | Default | Range | Notes |
| --------- | ----- | ------- | ----- | ----- |
| SC: Lockout Duration | **0 min** | 0 | 0, 15, 30, 45, 60 | 0 = disabled |
| SC: Minimum On Time | 5 min | 5 | 1-20 | Compressor run shorter than this triggers lockout |
| SC: Predictive Prevention | **OFF** | OFF | ON/OFF | Enables predictive flow temp boost |
| SC: High Delta Threshold | 1.0 C | 1.0 | 1.0-3.0 | Overshoot above requested flow temp to trigger timer |
| SC: High Delta Duration | 4.0 min | 4.0 | 1.0-5.0 | How long overshoot must persist before boost |

Configuration via ESPHome web UI at `http://192.168.1.230/` or Home Assistant.

### Sensor Snapshots

**Feb 19, 21:30 — outdoor 11 C, pump speed 5 (before changes)**

| Sensor                   | Value           |
| ------------------------ | --------------- |
| Outside temperature      | 11 C            |
| HP feed temperature      | 32 C            |
| HP return temperature    | 30.5 C          |
| HP delta T               | **1.5 C**       |
| Zone 1 setpoint          | 31 C            |
| Compressor frequency     | 30 Hz (near minimum) |
| Estimated output         | 1.878 kW        |
| Flow rate                | 18 L/min        |
| Pump speed               | 5 (max)         |
| Pump consumption         | 59 W            |
| Fan speed                | 650 RPM         |
| Estimated COP            | 2.22            |
| Heating COP (cumulative) | 2.02            |
| DHW COP (cumulative)     | 1.55            |
| Compressor starts        | 15,100          |
| Operating hours          | 7,968           |

**Feb 20, 20:14 — outdoor ~0 C, pump speed 3 (after changes)**

| Sensor                   | Value           |
| ------------------------ | --------------- |
| Outside temperature      | ~0 C (sensor reads -4, offset suspected) |
| HP feed temperature      | 36.5 C          |
| HP return temperature    | 31 C            |
| HP delta T               | **5.5 C**       |
| Compressor frequency     | 98 Hz (near max)|
| Estimated output         | 4.97 kW         |
| Flow rate                | 13 L/min        |
| Pump speed               | 3               |
| Pump consumption         | 25 W            |
| Fan speed                | 840 RPM         |
| Compressor starts        | 15,100          |
| Operating hours          | 7,989           |

### Monitoring Data (Feb 19-20, 2026)

24h monitoring via `scripts/monitor.py` (polls ESP32 SSE endpoint every 60s, logs to `data/ecodan_log.csv`).

**Pump Speed Comparison (measured)**

| Metric | Speed 5 (7-11 C out) | Speed 4 (1-8 C out) | Speed 3 (~0 C out) |
| ------ | -------------------- | -------------------- | ------------------- |
| Flow rate | 18 L/min | 16 L/min | 13 L/min |
| Pump watts | 59 W | 39 W | 23-25 W |
| Delta T | 1.8 C avg | 2.2 C avg | 3.5-5.5 C |
| Heat delivery | 2.4 kW | 2.8 kW | ~5 kW |
| Comp Hz (avg) | 35 | 47 | 54-98 |
| Comp behavior | Smooth 30 Hz | More cycling | Sawtooth 0↔98 Hz |
| ON cycle avg | 69 min | 30 min | 25 min |
| OFF cycle avg | 5 min | 4 min | 3 min |
| Starts/hour | 0.81 | 1.75 | 2.14 |
| Inst. COP avg | 2.38 | 2.06 | 1.49 |

Notes: Speed 4 and 3 data collected during colder weather — COP and cycling differences are partly due to outdoor temperature, not only pump speed. Outdoor temp sensor may read 3-4 C lower than actual.

**DHW Cycle** (Feb 20, 05:00-05:14): 14 minutes, 1 cycle in 24h. DHW temp: 37-45 C.

**Defrost**: No defrost cycles detected in 21 hours of monitoring.

### Identified Issues

#### 1. Uninsulated Pipes (CRITICAL)

17.5m of 28mm + 7m of 22mm pipes running through ~16.4 C garage with zero insulation.
Estimated ~316W continuous loss during heating, ~578W during DHW.
Annual loss: ~800 kWh for heating alone.
This loss is counted as "delivered" energy by the heat pump but never reaches the living space.

**Impact**: Inflates apparent delivery while wasting ~40% of heating energy.

#### 2. Low Delta T at Heat Pump (PARTIALLY ADDRESSED)

Previously at pump speed 5: feed 32 C, return 30.5 C → ΔT = 1.5 C. With 18 L/min flow rate, barely loading.

After pump speed reduction to 3: delta T improved to 3.5-5.5 C range, approaching design value of 5.8 C. Still monitoring for long-term data.

#### 3. Short Cycling Risk

15,100 starts in 7,968 hours = **1.9 starts per hour average**. This is above ideal (<1 start/hour) and indicates the system is oversized for the actual load, especially at mild outdoor temperatures. The 100L buffer tank helps but may not fully prevent it.

#### 4. DHW Efficiency Below Expected

DHW COP of 1.96 (target 43 C) is below the expected 2.5-3.0 range. Possible causes:

- Uninsulated DHW pipes (22mm × 7m) losing ~126W during DHW cycles
- Tank standing losses: ~0.83 kWh/day through 50mm insulation
- Legionella cycles (60 C) severely reduce COP
- DHW schedule (4h evening + 2h morning = 6h/day) means the tank cools between windows

#### 5. Garage Heating as Side Effect

Garage is at 16.4 C with floor heating circuit permanently OFF. This heat is coming entirely from uninsulated pipes — the garage is being heated by waste heat. After insulating pipes, garage temperature will drop.

#### 6. Pump Speed Optimization (RESOLVED)

Tested pump speeds 5, 4, and 3. Speed 3 improved delta T (3.5-5.5 C) and cut pump watts (25W) but caused severe compressor short-cycling: sawtooth 0↔98 Hz oscillations, 2.14 starts/hour, and COP dropped to 1.49. Speed 5 maintains smooth compressor modulation at ~30 Hz with 0.81 starts/hour and COP ~2.38. The 34W pump power saving at speed 3 is negligible compared to COP loss from cycling. **Reverted to speed 5 on Feb 21.** DHW pump speed remains at 5.

#### 7. Manifold Flow Meters Not Balanced

All 11 circuit flow meters (topometers) are set to the same value regardless of circuit length. Shorter circuits (bathroom 51m) get the same flow as longer ones (kitchen 100m), causing uneven heat distribution. To be addressed after pump speed optimization is validated.

#### 8. Outside Temperature Sensor Offset

Outside temp sensor reads approximately 3-4 C lower than actual. At actual ~0 C, sensor reads -3 to -4 C. Impact on weather compensation curve: system targets slightly higher flow temps than necessary, reducing COP.

### Eliminated Suspects

- **Mixing valve**: No mixing valve installed (SW2-6 OFF, code 177 = 0, menu shows "Invalid"). The 25 C readings on Z1 Feed/Return were from unconnected optional thermistors (THW6/THW7 absent).
- **Bypass valve**: Disabled.
- **Zone 2**: Not configured (SW2-7 OFF).
- **Pump speed**: Tested speeds 5, 4, and 3. Speed 3 improved delta T (3.5-5.5 C) but caused severe compressor cycling (0↔98 Hz sawtooth). Speed 5 gives stable compressor modulation at ~30 Hz and best overall COP. Reverted to speed 5.

### Recommendations (Priority Order)

1. **Insulate all pipes** — 13mm foam insulation on all 28mm and 22mm pipes in the garage. Estimated cost: ~30-50 EUR. Estimated savings: ~545 kWh/season. Potential COP improvement from 2.2 → 2.8-3.0.

2. ~~**Monitor 24h+ data**~~ — DONE. Monitor script running since Feb 19. Collecting data in `data/ecodan_log.csv`.

3. ~~**Test pump speed**~~ — DONE. Tested speeds 5, 4, 3. Speed 3 caused compressor cycling (COP 1.49). Speed 5 gives best overall efficiency with smooth compressor modulation. Reverted to speed 5.

4. **Validate thermo diff. lower limit change** — Changed from -5 to -7 C. Monitor cycling patterns to confirm longer OFF periods and fewer compressor starts.

5. **Balance manifold flow meters** — Adjust topometers proportional to circuit length (longer circuits get more flow). Currently all set equally.

6. **Investigate outside temp sensor offset** — Reads ~3-4 C low. Consider applying offset in weather compensation curve or ESPHome config.

7. **Review DHW schedule** — Consider whether a single longer window (e.g., 19:00-07:00) might reduce reheating losses vs two separate windows.

8. **Install THW6/THW7 thermistors** — Optional but recommended. Installing zone thermistors (PAC-TH011-E) would give real zone flow/return data for monitoring actual heat delivery to the underfloor circuits.

## Change Log

| Date | Time | Change | Details |
| ---- | ---- | ------ | ------- |
| Feb 19 | 22:26 | Monitoring started | `scripts/monitor.py` logging to `data/ecodan_log.csv`, polling every 60s |
| Feb 20 | 05:51 | Pump speed heating 5 → 4 | Flow: 18 → 16 L/min, pump watts: 59 → 39 W, delta T: 1.8 → 2.2 C |
| Feb 20 | 19:05 | Pump speed heating 4 → 3 | Flow: 16 → 13 L/min, pump watts: 39 → 25 W, delta T: 2.2 → 3.5-5.5 C |
| Feb 20 | ~20:18 | Thermo diff. lower limit -5 → -7 | FTC deadband increased to reduce compressor cycling frequency |
| Feb 21 | 08:32 | Pump speed heating 3 → 5 | Reverted to speed 5 after overnight data showed speed 3 causes compressor cycling (0↔98 Hz sawtooth, 2.14 starts/hr, COP 1.49) |
