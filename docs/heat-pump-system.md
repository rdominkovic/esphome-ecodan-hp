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

### Flow Temperature Control

**Active mode: Auto-Adaptive Control** (re-enabled Mar 3 evening after HA weather comp trial)

Auto-Adaptive (AA) manages flow temperature setpoint dynamically using `flow = return + delta_T`, where delta_T adapts to outdoor temperature (cold_factor) and room temperature error. This keeps the setpoint close to current water temperature, enabling low Hz continuous operation. The HA weather compensation automation is disabled (it produced worse daytime COP: 3.0 vs AA's 3.5-5.3).

| Parameter | Value | Notes |
| --------- | ----- | ----- |
| Operating mode | Heat Flow Temperature | AA manages setpoint via optimizer |
| Auto-Adaptive Control | **ON** | Re-enabled Mar 3 evening |
| Room temp target | 22.5 C | Desired indoor temperature |
| Room temp source | 3 Tuya thermostats | Avg of dnevna soba, ured, kupatilo (Tuya values / 2) |
| Max flow temperature | 40 C | AA upper limit |
| Heating system type | UFH | Underfloor heating profile |
| HA weather comp automation | **OFF** | Disabled — conflicts with AA |

### Weather Compensation Automation

HA automation `weather_compensation_flow_setpoint` on the cloud VM, fires every 5 minutes. Pauses during DHW and defrost (3-way valve ON or defrost sensor ON).

**Formula:**

```
base    = clamp(42.0 − 0.68 × (OT + 10), 25, 40)
error   = room_target(22.5) − room_actual
corr    = clamp(4.0 × error, −5, +8)
raw     = base + curve_offset + corr

# Rate limiting (prevents compressor halt on fast setpoint drop):
safe_floor = max(feed_temp − 1.5, 25.0)
new_sp  = clamp(max(raw, prev_setpoint − 1.0, safe_floor), 25, 40)
new_sp  = round to nearest 0.5 C
```

**Curve examples (offset=0, error=0):**

| OT    | Setpoint | Notes |
|-------|----------|-------|
| +15 C | 25.0 C   | Minimum clamp |
| +10 C | 28.6 C   | |
| +7 C  | 30.4 C   | |
| +5 C  | 31.8 C   | Was 40 C with AA at OT=5 |
| 0 C   | 35.2 C   | |
| −5 C  | 38.6 C   | |
| −10 C | 40.0 C   | Maximum clamp |

**Tuning (no file editing):**

| Parameter | Where | Default | Effect |
|-----------|-------|---------|--------|
| `curve_offset` | HA input_number slider | 0.0 C | Shifts entire curve ±5 C |
| `room_target` | automation variable | 22.5 C | Indoor temperature target |
| `Kp` | automation variable `room_correction` | 4.0 | Room correction gain |

- House too cold → increase `curve_offset` by +0.5 C increments
- House too warm → decrease `curve_offset`
- Room temp oscillates → decrease Kp (try 3.0 or 2.5)
- Room temp slow to recover → increase Kp (try 5.0)

**Rollback:** turn AA back ON (`switch.ecodan_heatpump_auto_adaptive_control → ON`). The automation will continue running but AA will override its setpoints immediately, so no harm done. Alternatively disable the automation in HA.

**Known limitation:** no explicit shutoff when room is above target at high OT. At OT=+15 C, setpoint clamps to 25 C (minimum) and the heat pump will run at minimum Hz or stop naturally when feed reaches setpoint. If this proves to be a problem, add a condition to skip updates when room > 23 C and OT > 10 C.

---

### Firmware Modifications (local fork)

**Status:** Auto-Adaptive is ON. All firmware modifications below are active.

Using local components instead of GitHub source. Four key changes to the optimizer:

**1. Reduced UFH base minimum delta_T** (`optimizer.cpp`)
- Changed from 2.0 C to 1.0 C for UFH profile
- At mild outdoor temps (10-15 C), original 2.0 C forced unnecessarily high flow targets
- Cold weather behavior unchanged (both converge to 4.0 C via cold_factor)

**2. Proportional delta_T reduction when room above target** (`optimizer.cpp`)
- Original: when room > target, delta_T = base_min (fixed floor of 1.0 C)
- Modified: delta_T = max(0, dynamic_min_delta_t + error), where error is negative when room > target
- Uses dynamic_min_delta_t (accounts for cold_factor) instead of base_min_delta_t (fixed 1.0 C)
- This prevents the flow target from dropping too low in cold weather, avoiding compressor cycling
- At OT 3 C: dynamic_min = 4.0, so room +0.3 above target gives delta_T = 3.7 (enough headroom)
- At OT 13 C: dynamic_min = 1.5, so room +0.3 above target gives delta_T = 1.2 (minimal warm weather impact)
- Suppression deadband (room > target + 0.5 C) still sets flow to minimum, unchanged

**3. Linear cold_factor scaling** (`optimizer.cpp`)
- Upstream: `cold_factor *= cold_factor * 1.5` (quadratic, aggressive at cold temps)
- First attempt (Feb 26): `cold_factor *= cold_factor * 0.5` (quadratic, reduced multiplier)
- Final (Mar 1): removed quadratic dampening entirely, cold_factor is linear `(15 - OT) / 20`
- Root cause: quadratic scaling dampened cold_factor too much at OT 3-8 C, producing flow targets in the 30-32 C "dead zone" where the outdoor unit trips on +2 C overshoot
- COP data confirmed: target 31-32 C has worst COP (2.44-2.68), while 34-35 C has best (3.24)
- Cycling vs continuous overnight: COP 2.07 (Hz avg 50) vs COP 2.88 (Hz avg 35) — 39% COP penalty from cycling
- See "COP Analysis by Flow Target" section below for full data

| OT | Quadratic (old) | Linear (new) | dynamic_min_delta old | new | Flow target old (ret=29) | new |
|----|-----------------|-------------|----------------------|-----|------------------------|-----|
| 15 C | 0.000 | 0.000 | 1.0 | 1.0 | 30.0 | 30.0 |
| 13 C | 0.005 | 0.100 | 1.0 | 1.5 | 30.0 | 30.5 |
| 10 C | 0.031 | 0.250 | 1.2 | 2.2 | 30.2 | 31.2 |
| 7 C | 0.080 | 0.400 | 1.4 | 3.0 | 30.4 | 32.0 |
| 5 C | 0.125 | 0.500 | 1.6 | 3.5 | 30.6 | 32.5 |
| 3 C | 0.180 | 0.600 | 1.9 | 4.0 | 30.9 | 33.0 |
| 0 C | 0.281 | 0.750 | 2.4 | 4.8 | 31.4 | 33.8 |
| -5 C | 0.500 | 1.000 | 3.5 | 6.0 | 34.0 | 36.5 |

Warm weather safety: at OT >= 15 C no change. At OT 10-14 C, room is above target 91% of time so reduced_delta and suppression deadband dominate behavior. Suppression threshold (error < -0.5 C) unchanged.

**4. Relaxed enforce_step_down protection** (`events.cpp`)
- MAX_FEED_STEP_DOWN: 1.0 C → 1.8 C (threshold before protection activates)
- MAX_FEED_STEP_DOWN_ADJUSTMENT: 0.5 C → 1.0 C (adjustment when triggered)
- Original values created a circular dependency: high target → high feed → high return → high target
- Relaxed values allow faster convergence to equilibrium while maintaining compressor protection

### COP Analysis by Flow Target (data from Feb 21 - Mar 1)

Analysis of 2121 heating-only readings (compressor ON, no DHW, no defrost).

**COP by flow target temperature (1 C buckets):**

| Target | Readings | COP avg | Hz avg | Notes |
|--------|----------|---------|--------|-------|
| 28 C | 13 | 3.85 | 26 | Small sample |
| 30 C | 185 | 3.19 | 31 | Good when stable, rare |
| 31 C | 260 | **2.68** | 43 | **Dead zone - cycling** |
| 32 C | 372 | **2.44** | 40 | **Dead zone - cycling** |
| 33 C | 666 | 2.81 | 35 | Transition |
| 34 C | 399 | **3.24** | 37 | **Sweet spot** |
| 35 C | 123 | **3.24** | 42 | **Sweet spot** |
| 36 C | 35 | 3.12 | 40 | Good |

**COP by compressor frequency:**

| Hz range | Readings | COP avg | Notes |
|----------|----------|---------|-------|
| 20-30 | 431 | **3.80** | Best efficiency |
| 30-40 | 826 | 3.03 | Good |
| 40-50 | 602 | 2.27 | Poor |
| 50-60 | 208 | 2.30 | Poor |
| 60-70 | 37 | 2.01 | Bad |
| 70-80 | 17 | 1.88 | Worst |

**Cycling vs continuous (overnight periods):**

| Mode | Readings | COP avg | Hz avg |
|------|----------|---------|--------|
| Continuous (>60 min) | 537 | **2.88** | 35 |
| Cycling (<60 min) | 446 | **2.07** | 50 |

Key insight: target 34-35 C has BETTER COP than 30-31 C despite higher feed temperature. The COP benefit of lower Hz (30-37 vs 40-56) and continuous operation outweighs the penalty of slightly higher flow temperature.

**Original ESP32 Weather Compensation Curve (inactive, for reference):**

| Outdoor temp | Flow water temp |
| ------------ | --------------- |
| -10 C        | 40 C            |
| +15 C        | 29 C            |

Linear interpolation, offset 0 C. Replaced Feb 26 by Auto-Adaptive because static setpoints caused outdoor unit compressor halt at +2 C overshoot, producing 28 min ON / 4 min OFF cycling at 60+ Hz.

After 5 weeks of AA tuning (see changelog and Firmware Modifications section), replaced Mar 3 by external HA automation weather compensation — see "Weather Compensation Automation" section above. Same concept but formula runs in HA (not ESP32 firmware), uses a gentler slope calibrated for our UFH system, and adds room temperature P-correction.

### DHW (Domestic Hot Water)

- **Target temperature**: 50 C (raised from 43 C on Feb 23)
- **Restart threshold**: -10 C (restarts when tank drops to 40 C)
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
**AA Diagnostics** (added Mar 3): aa_cold_factor, aa_target_delta_t, aa_dynamic_min_delta, aa_room_error, aa_control_mode, aa_error_factor, aa_smart_boost, aa_calculated_flow

## Data Collection

### CSV Logger (`/opt/ecodan/scripts/mqtt_logger.py`)

MQTT subscriber on the VM that logs all sensor values every 60 seconds to `/opt/ecodan/data/ecodan_log.csv`. Runs as systemd service `ecodan-logger`. Also fetches room temperature from HA (Tuya thermostat average) every write cycle.

Derived columns computed at write time:
- `delta_t`: feed_temp − return_temp
- `room_temp`: average of 3 Tuya thermostats (dnevna/ured/kupatilo), with /2 Tuya scaling correction
- `cop_per_hz`: estimated_cop / compressor_hz × 10 (COP per 10 Hz, efficiency ratio)

#### Tariff-period COP tracking

Tracks energy consumption per Croatian electricity tariff period (VT=day, NT=night). Uses delta accumulation from CN105 `daily_consumed`/`daily_produced` counters every 60s, split at tariff boundaries. Winter: NT 21:00-07:00, Summer: NT 22:00-08:00 (auto-detects DST). Handles midnight counter reset (consumed at 23:59, produced at 00:00). State persisted to `period_cop_state.json` for service restart recovery. Publishes to HA via MQTT with last 10 completed periods as history.

#### HA sensors published via MQTT

| HA Entity | MQTT Topic | Description |
|-----------|-----------|-------------|
| `sensor.ecodan_logger_ecodan_daily_cop` | `ecodan-logger/daily_cop/state` | Live daily COP from daily counters |
| `sensor.ecodan_logger_ecodan_period_cop` | `ecodan-logger/period_cop/*` | Current + historical tariff period COP (attributes: current_period, history[]) |
| `sensor.ecodan_logger_ecodan_yesterday` | `ecodan-logger/yesterday/*` | Yesterday's consumed/produced/COP |
| `sensor.ecodan_logger_ecodan_log_totals` | `ecodan-logger/log_totals/*` | Totals across all CSV log files (consumed, produced, COP, date range, days) |
| `sensor.ecodan_logger_ecodan_monthly_energy` | `ecodan-logger/monthly_energy/*` | Monthly energy breakdown with heating/DHW split from `historical_energy.json` + CSV logs |

All sensors use MQTT auto-discovery (`homeassistant/sensor/*/config`) under the "Ecodan Logger" device.

#### HA Dashboard (`lovelace.dashboard_ecodan`)

The Ecodan dashboard displays:
- **Daily summary**: today and yesterday consumed/delivered/COP
- **Tariff COP table**: completed VT/NT periods with energy and COP per period
- **Monthly energy table**: per-month breakdown with heating delivered, heating COP, DHW (PTV) delivered, DHW COP, and total COP. Data from `historical_energy.json` (manual FTC readings) combined with current month from CSV daily counters. Year total row at bottom.
- **History graphs**: COP, Hz, compressor state, temperatures, DHW, setpoint

### Transition Log (`/opt/ecodan/data/ecodan_transitions.csv`)

Real-time state change detection in the MQTT `on_message` handler. Writes immediately on edge detection — not buffered to the 60s write interval. Captures transitions that would be invisible at 1-minute CSV resolution.

Tracked events:

| Event | Trigger | Key context |
|-------|---------|-------------|
| `COMP_ON` | compressor 0→1 | off_duration, Hz, feed, target, OT, aa_mode, room |
| `COMP_OFF` | compressor 1→0 | on_duration, Hz at stop, feed, target, OT, aa_mode |
| `DHW_START` | 3way_valve 0→1 | dhw_temp, feed, comp_on |
| `DHW_END` | 3way_valve 1→0 | dhw_temp, feed, duration |
| `DEFROST_START` | defrost 0→1 | OT, feed |
| `DEFROST_END` | defrost 1→0 | OT, feed, duration |
| `AA_MODE` | aa_control_mode changes | old→new, room_error, calc_flow |
| `SC_LOCKOUT_ON` | sc_lockout 0→1 | — |
| `SC_LOCKOUT_OFF` | sc_lockout 1→0 | duration |

Each row includes full context: timestamp, event, from/to state, duration of previous state (minutes), plus 14 context columns (OT, feed, return, target, delta_t, Hz, compressor, defrost, DHW valve, AA mode, room error, calculated flow, room temp, COP).

Transitions also print to stdout (visible in `journalctl -u ecodan-logger -f`).

### Analysis Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `analyze_overnight.py` | Overnight cycle analysis with statistical summaries and timeline |
| `analyze_last_overnight.py` | 8-section report: cycles, temps, Hz distribution, COP, energy, timeline, stability |
| `analyze_today.py` | Quick daily summary with real-time progress |
| `daily_report.py` | Comprehensive daily report: gaps, cycles, hourly breakdown, energy by mode |
| `check_cycles.py` | Simple compressor cycle count diagnostic |
| `investigate_cycles.py` | Detailed cycle analysis with duration and mode tracking |
| `compare_pump_speed.py` | A/B comparison for pump speed changes |
| `analyze_periods.py` | Period comparison for configuration A/B testing |

## Energy Data

### Season 2025-2026 (Jan 1 - Mar 25, from FTC panel readings)

| Month     | Htg Con (kWh) | Htg Del (kWh) | Htg COP | DHW Con (kWh) | DHW Del (kWh) | DHW COP | Total Con | Total Del | COP  |
|-----------|---------------|---------------|---------|---------------|---------------|---------|-----------|-----------|------|
| Jan 2026  | 1,106         | 2,240         | 2.03    | 175           | 315           | 1.80    | 1,282     | 2,556     | 1.99 |
| Feb 2026  | 679           | 1,568         | 2.31    | 115           | 226           | 1.97    | 794       | 1,794     | 2.26 |
| Mar 1-25  | 308           | 1,042         | 3.38    | 92            | 185           | 2.01    | 400       | 1,228     | 3.07 |
| **Total** | **2,093**     | **4,850**     | **2.32**| **382**       | **726**       | **1.90**| **2,476** | **5,578** |**2.25**|

Data sources:
- Jan and Feb 1-25: manual FTC panel readings stored in `data/historical_energy.json`
- Feb 26 onwards: CSV daily counters (`daily_consumed_kwh`/`daily_produced_kwh`) from MQTT logger
- Heating/DHW split for Feb 26+ from FTC panel readings at month boundaries
- Note: CN105 `daily_produced` counter undercounts delivered by ~5% vs FTC panel

### Season 2024-2025 (as of February 18, 2025)

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
| Pump speed (heating) | **5** | 5 | 1-5 | Tested 5 → 4 → 3 → all reverted to 5. Speed 4: marginal delta-T gain, 3x cycling. Speed 3: severe cycling. Speed 5 confirmed optimal. |
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
| SC: Lockout Duration | **15 min** | 0 | 0, 15, 30, 45, 60 | Reduced from 45 min Feb 24 |
| SC: Minimum On Time | **20 min** | 5 | 1-60 | Reduced from 40 min Feb 24 |
| SC: Predictive Prevention | **OFF** | OFF | ON/OFF | Disabled Feb 26. Conflicts with AA mode: boost has no restore path when AA is active, causing runaway target increase. |
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
| Outside temperature      | ~0 C                |
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

Notes: Speed 4 and 3 data collected during colder weather — COP and cycling differences are partly due to outdoor temperature, not only pump speed.

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

6. **Review DHW schedule** — Consider whether a single longer window (e.g., 19:00-07:00) might reduce reheating losses vs two separate windows.

8. **Install THW6/THW7 thermistors** — Optional but recommended. Installing zone thermistors (PAC-TH011-E) would give real zone flow/return data for monitoring actual heat delivery to the underfloor circuits.

## Change Log

| Date | Time | Change | Details |
| ---- | ---- | ------ | ------- |
| Feb 19 | 22:26 | Monitoring started | `scripts/monitor.py` logging to `data/ecodan_log.csv`, polling every 60s |
| Feb 20 | 05:51 | Pump speed heating 5 → 4 | Flow: 18 → 16 L/min, pump watts: 59 → 39 W, delta T: 1.8 → 2.2 C |
| Feb 20 | 19:05 | Pump speed heating 4 → 3 | Flow: 16 → 13 L/min, pump watts: 39 → 25 W, delta T: 2.2 → 3.5-5.5 C |
| Feb 20 | ~20:18 | Thermo diff. lower limit -5 → -7 | FTC deadband increased to reduce compressor cycling frequency |
| Feb 21 | 08:32 | Pump speed heating 3 → 5 | Reverted to speed 5 after overnight data showed speed 3 causes compressor cycling (0↔98 Hz sawtooth, 2.14 starts/hr, COP 1.49) |
| Feb 21 | ~08:47 | SC lockout 0 → 15 min | Enabled short-cycle lockout protection via ESPHome web UI |
| Feb 21 | ~08:47 | SC predictive prevention OFF → ON | Enabled predictive flow temp boost (+0.5 C) to prevent short cycles |
| Feb 22 | 10:45 | SC limits increased & strategy update | Increased `Minimum On-Time` limit to 60m in YAML. Set `Minimum On-Time` to 40m and `Lockout Duration` to 45m in HA to force longer cycles. |
| Feb 22 | 11:15 | Thermo diff. lower limit -7 → -9 | Maximized FTC deadband to further extend compressor OFF periods and improve stability. |
| Feb 23 | ~16:30 | Weather comp. offset +1 → 0 | Removed +1 C flow temp offset to slightly lower flow targets across all outdoor temps, aiming to extend compressor ON cycles. |
| Feb 23 | ~20:30 | DHW target 43 → 50 C, restart threshold -10 C | DHW was stopping at 40 C (unexplained early cutoff at 19:17). Raised target to 50 C and set restart threshold to -10 C. DHW successfully heated to 50.5 C in 42 min (20:42-21:24). |
| Feb 24 | ~07:12 | SC Lockout 45 → 15 min, Minimum On-Time 40 → 20 min | Aggressive lockout was causing cold floor at restart → high-Hz cold starts → overshoot → stop. Shorter lockout keeps floor warmer, targeting stable 30-40 Hz operation. |
| Feb 24 | ~10:30 | Weather comp warm end 28 → 30 C (offset stays 0) | Rooms were cooler with offset 0 on old curve. Raising warm end to 30 C raises flow target by ~1.6 C at +10 C outdoor, ~1.4 C at +7 C, without changing cold-weather behaviour. |
| Feb 25 | 21:32 | Pump speed heating 5 → 4 | Testing lower pump speed again. Previous speed 4 test (Feb 20) showed flow 18→16 L/min, pump watts 59→39 W, delta T 1.8→2.2 C. Current baseline at speed 5: delta T avg 1.8 C, COP 2.34, 0.84 starts/hr. Watching for compressor stability. |
| Feb 26 | ~07:00 | Pump speed heating 4 → 5 | Reverted after overnight test. Speed 4 results: delta-T only +0.2 C (2.3→2.5), but cycling nearly tripled (0.59→1.54 starts/hr), COP dropped (2.19→2.06). Pump watt savings (17W) not worth the cycling penalty. Speed 5 confirmed optimal. |
| Feb 26 | ~09:30 | Weather comp warm end 30 → 29 C | House was getting too warm at +15 C outdoor. |
| Feb 26 | ~09:45 | Tuya Smart Life integration added to HA | Connected MOES BHT-002 thermostats and Tuya temp sensor. Thermostat temps need /2 correction (Tuya scaling bug). Created HA automation to push avg room temp (dnevna+ured+kupatilo)/2/3 to ESP32 every 5 min. |
| Feb 26 | ~11:15 | Switched to Auto-Adaptive mode | Changed operating mode from Heat Target Temperature to Heat Flow Temperature. Enabled Auto-Adaptive Control. Set room target 24 C, max flow 40 C, heating system type UFH, room temp source HA/REST API. Immediate result: compressor running continuously at 24-38 Hz with optimizer-managed flow target, vs previous 60+ Hz cycling. |
| Feb 26 | ~11:30 | Room target 24 → 23 C | Robert prefers 23 C |
| Feb 26 | ~11:57 | SC Predictive Prevention ON → OFF | Predictive boost conflicts with AA mode: boost pushes target up but has no restore path (stand_alone_predictive_active=false when AA enabled), causing runaway target increase and high pressure cutout at 60 C condensing. |
| Feb 26 | ~12:55 | Switched to local components | Changed ecodan-esphome.yaml external_components from GitHub to local path for firmware customization. |
| Feb 26 | ~13:00 | UFH base_min_delta_t 2.0 → 1.0 | Hardcoded in optimizer.cpp. Original 2.0 C forced target too high at mild outdoor temps (34 C target at 12 C outdoor vs ideal 28-30 C). Cold weather unchanged. |
| Feb 26 | ~13:25 | enforce_step_down relaxed | MAX_FEED_STEP_DOWN 1.0→1.8, adjustment 0.5→1.0. Original values created circular dependency keeping system at high equilibrium. |
| Feb 26 | ~14:44 | Proportional delta_T when room > target | delta_T = max(0, base_min + error) instead of fixed base_min. Enables gradual Hz reduction as room exceeds target. At +0.3 C: Hz drops from 34 to 26. At +1.0 C: compressor stops. |
| Feb 26 | ~23:45 | cold_factor multiplier 1.5 → 0.5 | Evening cycling at OT 4-7 C: cold_factor squared × 1.5 produced delta_T 2.88 at OT=5 C, pushing condensing to 52 C → outdoor unit protection halt. Reduced multiplier to 0.5 gives delta_T 1.63 at OT=5 C. |
| Feb 26 | ~23:45 | min_delta_cold_limit 4.0 → 6.0 (UFH) | Restored upstream default. Previous reduction to 4.0 was unnecessarily aggressive with the new 0.5 multiplier. |
| Feb 27 | ~07:20 | Daily energy reporting script added | `scripts/daily_energy.py` generates Excel report from CSV logs with daily COP, consumed/delivered breakdown. Uses daily_max() to handle midnight counter reset race condition. |
| Feb 27 | ~19:00 | Room target 23 → 22.5 C | 23 C was too warm in mild weather (OT 10+ C) |
| Feb 28 | ~09:15 | reduced_delta: base_min → dynamic_min | **Root cause fix for overnight cycling.** Feb 28 00:00-08:00: 9 cycles (37 min ON / 4 min OFF, Hz 40-50), vs stable 23:00-01:50 run at 26-30 Hz. Problem: when room (22.8) > target (22.5), reduced_delta used base_min_delta_t (1.0) ignoring cold_factor. At OT 3 C, delta_T = max(0, 1.0-0.3) = 0.7 → flow target 32.2 C → only 2.0 C headroom before outdoor unit +2 C protection → compressor shutdown after ~35 min. Fix: use dynamic_min_delta_t (1.9 at OT 3 C) → delta_T = 1.6 → flow target 33.1 C → 4.0 C headroom → continuous operation. At warm OT (12-13 C), dynamic_min ≈ 1.0-1.1, so behavior is unchanged. |
| Mar 1 | ~09:15 | cold_factor: quadratic → linear | **Eliminated the 30-32 C dead zone.** Overnight Mar 1: 11 compressor starts (1.1/h), 30 min ON / 4 min OFF cycling at OT 3-5 C. Root cause: quadratic dampening (`cold_factor *= cold_factor * 0.5`) suppressed cold_factor too aggressively at moderate cold — OT 5 C gave cf=0.125, dynamic_min=1.6, target=30.6 C. At this target, compressor overshoots by 2 C within 30 min, triggering outdoor unit protection. After defrost when OT dropped to 1-2 C, target naturally rose to 33-35 C and compressor ran 160 min continuously at 30-36 Hz. COP analysis of 2121 readings confirmed: target 31-32 C has worst COP (2.44-2.68, Hz 40-43), while 34-35 C has best COP (3.24, Hz 37-42). Cycling periods show COP 2.07 vs continuous 2.88 (39% penalty). Fix: removed quadratic, cold_factor is now linear `(15 - OT) / 20`. At OT 5 C: cf=0.50, dynamic_min=3.5, target=32.5 C. At OT 3 C: cf=0.60, dynamic_min=4.0, target=33.0 C — directly into the optimal COP zone. Warm weather impact minimal: at OT >= 15 C no change, at OT 10-14 C targets +1 C higher but room is above target 91% of the time so suppression dominates. |
| Mar 2 | ~08:00 | reduced_delta suppression boundary: < → <= | Attempt #3. Fixed exact boundary case where room=23.0 was not entering suppression (< vs <=). Result: only fixed the exact room=target+0.5 edge case. Room at 22.8 C (−0.3 error) still cycled at OT 7-9 C. Not the root cause. |
| Mar 2 | ~18:30 | reduced_delta: proportional scaling | Attempt #4. Formula: `dynamic_min × (1 + error/0.5)`. At error=−0.3, OT=5 C: delta_T = 3.5 × 0.4 = 1.4 C → target 33.4 C. At OT=3 C: delta_T = 4.0 × 0.4 = 1.6 C → target 31.6 C. Result: Hz 48-54, still cycling. The problem is not the absolute target value — it's the Hz level. At Hz 26-30, even target 30-32 C works fine (no overshoot). At Hz 50+, even 35 C causes overshoot. |
| Mar 2 | ~20:30 | reduced_delta: fixed 1.0 C | Attempt #5 (final AA tuning attempt). When room above target, always use delta_T=1.0 C regardless of cold_factor. At OT=5 C: target ~33 C. At OT=3 C: target ~31 C. Goal: keep Hz low at all outdoor temps. Deployed during active DHW cycle. |
| Mar 3 | ~08:30 | Switched to external weather compensation HA automation | Turned AA OFF, deployed HA automation `weather_compensation_flow_setpoint` with curve formula + P-correction + rate limiting. See "Weather Compensation Automation" section for full formula. |
| Mar 3 | ~22:40 | Added 8 AA diagnostic sensors to firmware | Exposed optimizer internal values (aa_cold_factor, aa_target_delta_t, aa_dynamic_min_delta, aa_room_error, aa_control_mode, aa_error_factor, aa_smart_boost, aa_calculated_flow) as ESPHome sensors via MQTT. Added to CSV logger and labels. |
| Mar 3 | ~23:00 | Added COP/Hz efficiency ratio to CSV logger | `cop_per_hz` = estimated_cop / compressor_hz × 10. Tracks efficiency per unit of compressor effort. |
| Mar 4 | ~06:30 | Added transition logging to MQTT logger | Real-time state change detection for compressor, DHW, defrost, AA mode, SC lockout. Writes to separate `ecodan_transitions.csv` with full context. Added `PYTHONUNBUFFERED=1` to systemd service for live journalctl output. |
| Mar 3 | ~22:30 | **Re-enabled Auto-Adaptive, disabled HA weather comp** | **Reverted to AA after analyzing full day of HA weather comp data.** HA weather comp produced COP 3.0 overall vs AA's 3.5. Key comparison: AA daytime COP 4.0-5.3 (long continuous runs at Hz 24-40) vs HA WC daytime COP 3.1 (short cycling, Hz 39+). AA's only weakness is overnight cycling at OT < 5 C (Hz 45-50, COP 2.0), but with cheaper night electricity this is acceptable. HA weather comp also had bugs: post-DHW safety floor held SP at 40 C for 30+ min causing Hz 82, and no warm-weather cutoff caused 7 pointless midday cycles. Conclusion: AA's tracking approach (setpoint close to current water temp) is fundamentally better for low-Hz operation than a fixed weather curve. |
| Mar 7 | ~10:40 | Suppression recovery ramp (Mode 5) | Attempt #6. After suppression (Mode 3) ends, ramp delta_T from base_min to target over 20 min instead of jumping immediately. Prevents Hz 60-70 spikes on restart. Result: 19 activations in 10 days, moderate help (Hz 30-68 instead of 60-70), but 8/19 hit dead compressor (no benefit). Marginal overall impact. |
| Mar 21 | ~22:00 | **DHW target 45 → 42 C** | **COP optimization.** Analysis of Mar 17-21 data showed DHW COP 1.71 as single biggest daily COP drag. Mitsubishi rates SUZ-SWM80VA2 at W50/OT9: COP 2.77-3.29, but our actual DHW COP was 1.71. Three improvements from lower target: (1) lower feed temp needed (~49 C vs ~52 C) means better compressor COP per Mitsubishi performance table (W50 COP 2.77 vs W55 COP 2.54 at OT7); (2) reduced premature shutdown — FTC stops DHW when feed exceeds SP+2 C, lower SP means lower absolute feed cutoff; (3) fewer DHW cycles since tank cools slower from lower starting temp. DHW hysteresis (temp drop) stays at 5 C (read-only via CN105, changeable only on FTC panel), so tank now swings 37-42 C instead of 40-45 C. 42 C at tap is comfortable for all household use. Changed via HA API call to climate.ecodan_heatpump_dhw_climate entity. |
| Mar 26 | ~09:00 | Added tariff-period COP and monthly energy to HA | MQTT logger publishes 6 new HA sensors: daily COP, period COP (VT/NT tracking), yesterday summary, log totals, and monthly energy breakdown. Monthly sensor combines manual FTC readings from `historical_energy.json` with current month from CSV logs. Ecodan HA dashboard redesigned with daily summary, tariff COP table, and monthly energy table (heating/PTV split with per-month COP). All values formatted to 2 decimal places. |
| Mar 17 | ~22:50 | **Suppress cooldown hysteresis** | **Attempt #7. Root cause fix for Mode 3→5→3 cycling trap.** 11-day analysis (Mar 7-17) revealed COP 3.0 at OT 9-13 C, well below Mitsubishi spec ~4.5. Primary loss: cycling. Mar 12 vs Mar 13 at identical OT (13 C): 9 starts COP 3.73 vs 20 starts COP 2.71. Root cause: after Mode 5 recovery (20 min), system re-checks error — room still >= 23.0 C (UFH thermal mass prevents cooling in 35 min) → immediate re-suppress → SP drops to 25 C → outdoor unit shuts comp in 10 min → 15 min lockout → repeat. Fix: after Mode 5 completes, set `suppress_cooldown_active_` flag blocking re-entry into Mode 3 until room error > -0.2 (room cools to 22.7 C). System stays in Mode 2 (fixed delta 1.0) with continuous low-Hz operation instead of cycling. |
| Mar 23 | ~19:28 | **Cooldown timeout + Mode 2 flow cap** | **Attempt #8.** Two fixes: (1) Cooldown expires after 60 min (was indefinite if error stayed below -0.2). (2) Mode 2 flow cap: `zone_min + dynamic_min + 3.0` prevents return-tracking SP trap at mild weather. At OT 15 C: cap = 29 C (was 40+ C). At OT 7 C: cap = 31 C. At OT 0 C: cap = 32.75 C. Fixes indefinite mild-weather heating trap from Attempt #7 without reverting anti-cycling benefit. One-week monitoring (Mar 23-30) confirmed: no heating SP > 35 C at OT > 10 C, SC lockouts dropped from 5-8/day to 0-2/day, room temp stable 22.6-22.8 C. |
| Mar 30 | ~22:00 | **Tariff-based room target (Opcija D)** | **Day/night COP optimization.** Analysis revealed COP 4+ at night (02:00-05:00) vs COP 2.0 during day, same OT 6-7 C. Root cause: (1) night had ONE 331-min continuous run at SP 34.5 C, Hz 26, dT 2-3.5 C; (2) day had 6 short cycles at SP 31 C (Mode 2 cap), dT 1 C, Hz 28-42 — floor saturated, minimal heat transfer. Night SP was higher because step-down rate limiter slowly ramped from Mode 1's uncapped SP. During day, room never dropped to target so Mode 1 never triggered. Fix: HA automation `tariff_based_room_target` — NT (22:00-08:00) target 23.0 C → Mode 1 (uncapped SP, long continuous runs, COP 4+, cheap electricity); VT (08:00-22:00) target 22.0 C → Mode 3 suppress, coast on UFH thermal mass ~23→22 C. Zero firmware risk. Evaluated 6 options: (A) lower suppress threshold — risky, Tuya ±0.5 C; (B) raise reduced_delta — reverts Attempt #2 failure; (C) raise Mode 2 cap — alone only +0.5 C; (D) tariff target — selected, lowest risk; (E) accept economics — partial; (F) combined B+C — risk of Hz 70+ regression. |
| Mar 30 | ~22:15 | DST clock reminder automation | FTC controller clock stuck on CET (winter time) after Mar 29 DST change. Clock cannot be set via CN105 — manual panel adjustment required. Added HA automation `dst_clock_change_reminder_for_ftc_panel` that sends persistent notification on last Sunday of March and October at 10:00. |
| Mar 31 | ~09:00 | **Tariff fix: max_heating_flow 40 → 36 C** | **Night of Mar 30-31 was a disaster.** Target 23 C put room below target → Mode 1 (uncapped) → SP calculated to 40+ C at OT 5 C → feed 42 C → outdoor unit protection halt every 25 min → 9 cycles, COP 1.6-2.3 avg, Hz 48 avg. Previous night's COP 4+ was NOT from Mode 1 — it was from Mode 2 with step-down ramp accidentally passing through sweet spot (34-36 C). Root cause: Mode 1's full delta_T at cold OT produces SP 40+ C which exceeds outdoor unit's +2 C protection. Fix: lowered `max_heating_flow_temperature` from 40 to 36 C via HA entity. This clamps Mode 1's SP at 36 C — the proven sweet spot where compressor runs at Hz 26-30 with COP 3.5-5.0. At mild OT (15 C), calculated SP is ~32 C (below cap, unaffected). Tariff targets kept at NT 23.0 C / VT 22.0 C. Daytime suppress behavior (08:00 target 22 C, room 23 C → Mode 3, coast) confirmed working perfectly on Mar 31 morning. |
| Apr 2 | ~08:15 | **Mode 1 startup ramp (Mode 6)** | **Attempt #9.** Night of Apr 1-2: 14 compressor cycles (25 min ON / 4 min OFF), Hz 50-76, COP 1.5-2.0 at OT 6-8 C. Root cause: Mode 1 sets SP = return + delta_T immediately on restart, creating 3 C gap → outdoor unit ramps Hz to 50-76 → feed overshoots SP+2 C in 25 min → protection halt. All 8 previous attempts changed SP magnitude; none changed SP ramp speed. The one night with COP 4+ (Mar 29-30, 331 min run) was from gradual step-down ramp accidentally passing through sweet spot. Fix: after each compressor STOP→START, ramp target_delta_t from base_min (1.0 C) to full calculated value over 15 min (Mode 6). At t=0: SP = return+1.0 (gap ~1 C, Hz ~26). At t=15 min: SP = full Mode 1 value. Outdoor unit never sees large gap → Hz stays low → no overshoot → continuous operation. Uses same ramp formula as Mode 5. Post-DHW runs unaffected (no STOP→START transition). Also changed VT room target from 22.0 to 22.5 C (HA automation). |
