# Suppression Recovery Ramp Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prevent compressor Hz spikes and short cycling when resuming heating after suppression mode (Mode 3) by ramping the setpoint gradually over 20 minutes.

**Architecture:** Reuse the proven defrost recovery ramp pattern (Mode 4) for post-suppression restarts. Track suppression state entry/exit, and when transitioning to active heating, apply a linear delta_t ramp from base_min to target over 20 minutes. Published as Mode 5 for diagnostics.

**Tech Stack:** C++ (ESP32/ESPHome firmware), compiled via `esphome compile`, deployed via OTA flash

---

## Problem

After the AA optimizer suppresses heating (Mode 3, setpoint=25°C), the compressor stops
and return temperature drops to ~29°C over 1-3 hours. When room temp falls below target
and heating demand resumes, the AA loop immediately calculates a full setpoint based on
cold_factor (e.g., return 29°C + delta_t 3.5-8°C = setpoint 33-37°C). This 4-8°C gap
between current feed and target forces the compressor to Hz 60-70, which overshoots the
setpoint. The outdoor unit trips the compressor (feed > setpoint + ~2°C), causing a 3-4
minute OFF pause followed by restart — classic short cycling.

### Evidence from Mar 4-7 data

- Mode 0 (system hands-off/startup) averages Hz 64-70, COP 0.7-2.2
- Mar 7 04:04-04:27: 23 min run at Hz 66, COP 0.7, then 3 min OFF, then proper restart
- 3-9 compressor cycles per night, with multiple <10 min OFF pauses
- Pattern repeats every night at OT 3-7°C

### Root cause

No ramp-up logic exists for the suppression→active heating transition. The defrost→active
transition has a ramp (Mode 4, recovery_ratio over 35 min for UFH), but suppression
recovery has no equivalent protection.

## Solution: Suppression Recovery Ramp (Mode 5)

Reuse the proven defrost recovery ramp pattern for post-suppression restarts.

### Mechanism

1. Track when the optimizer enters suppression mode (Mode 3, error <= -0.5)
2. When the compressor restarts after suppression, record `suppression_end_time_`
3. In `process_adaptive_zone_`, check if we are within the recovery window
4. Apply linear ramp from `base_min_delta_t` to `target_delta_t` over 20 minutes
5. Publish Mode 5 to diagnostic sensor for monitoring

### Recovery formula (identical to defrost ramp)

```
recovery_ratio = elapsed_ms / SUPPRESSION_RECOVERY_MS   // 0.0 → 1.0 over 20 min
delta_gap = max(target_delta_t - base_min_delta_t, 0)
ramped_delta_t = base_min_delta_t + (delta_gap * recovery_ratio)
calculated_flow = actual_return_temp + ramped_delta_t
```

### Expected behavior with ramp (Mar 7 scenario)

```
Before (no ramp):
  04:04  SP = 29 + 3.5 = 32.5  → Hz 66, COP 0.7, trip after 23 min

After (with ramp):
  04:04  SP = 29 + 1.0 = 30.0  → Hz ~20-25, COP 3.0+
  04:09  SP = 29 + 1.6 = 30.6  → Hz ~22-28
  04:14  SP = 30 + 2.2 = 32.2  → Hz ~25-30
  04:19  SP = 30 + 2.9 = 32.9  → Hz ~28-32
  04:24  SP = 31 + 3.5 = 34.5  → Hz ~30-35, full power, no trip
```

### Recovery window: 20 minutes

- Defrost recovery is 35 min (more severe thermal event)
- Suppression recovery is gentler — 20 min is sufficient
- Can be increased to 25-30 min if monitoring shows it's needed
- Hardcoded constant (not user-configurable) to keep it simple

## Code changes

### optimizer.h

Add two new member variables:
```cpp
uint32_t suppression_end_time_ = 0;
bool was_suppressing_ = false;
```

### optimizer.cpp — process_adaptive_zone_

In the heating active branch (line ~299-318), add a new check before the existing
error-based mode selection. The suppression recovery check sits between the defrost
recovery block and the normal mode selection:

```cpp
// After defrost recovery block (line 298), before normal mode selection:

const uint32_t SUPPRESSION_RECOVERY_MS = 20 * 60 * 1000UL;  // 20 minutes

if (this->was_suppressing_ && this->suppression_end_time_ > 0)
{
    uint32_t elapsed_ms = current_ms - this->suppression_end_time_;

    if (elapsed_ms < SUPPRESSION_RECOVERY_MS)
    {
        float recovery_ratio = (float)elapsed_ms / (float)SUPPRESSION_RECOVERY_MS;
        recovery_ratio = std::clamp(recovery_ratio, 0.0f, 1.0f);
        float delta_gap = fmax(target_delta_t - base_min_delta_t, 0.0f);
        float ramped_delta_t = base_min_delta_t + (delta_gap * recovery_ratio);

        calculated_flow = actual_return_temp + ramped_delta_t;
        calculated_flow = this->round_nearest(calculated_flow);
        if (i == 0) {
            if (this->state_.aa_mode) this->state_.aa_mode->publish_state(5.0f);
            if (this->state_.aa_calculated_flow)
                this->state_.aa_calculated_flow->publish_state(calculated_flow);
        }
        ESP_LOGW(OPTIMIZER_TAG,
            "Z%d Suppression Recovery: %.0f%% done. Ramp Delta: %.2f "
            "(Min: %.2f, Target: %.2f). Flow: %.2f",
            (i + 1), (recovery_ratio * 100.0f), ramped_delta_t,
            base_min_delta_t, target_delta_t, calculated_flow);
    }
    else
    {
        // Recovery complete, clear state
        this->was_suppressing_ = false;
        this->suppression_end_time_ = 0;
    }
}
else
{
    // Existing mode selection (suppress / maintain / track)
    // ... existing code ...
}
```

Track suppression state entry/exit within the existing mode selection:
```cpp
if (error <= -0.5f) {
    // ... existing suppress code ...
    this->was_suppressing_ = true;    // NEW: mark that we entered suppression
} else {
    if (this->was_suppressing_ && this->suppression_end_time_ == 0) {
        // Transition from suppress to active — start recovery timer
        this->suppression_end_time_ = millis();
    }
    // ... rest of existing maintain/track code ...
}
```

## Diagnostic visibility

- Mode 5 published to `aa_mode` sensor during recovery
- Recovery percentage logged via ESP_LOGW
- CSV logger and transition logger will capture Mode 5 automatically
- Existing analysis scripts will show Mode 5 in hourly breakdowns

## Testing plan

1. Compile and flash firmware via OTA
2. Wait for natural suppression→restart cycle (typically overnight)
3. Check logs for "Suppression Recovery" messages
4. Verify Mode 5 appears in CSV log
5. Compare Hz and COP during recovery vs previous nights
6. If 20 min is insufficient (still see Hz spikes at end of ramp), increase to 25-30 min

## Risk assessment

- **Low risk**: Uses identical pattern to proven defrost recovery ramp
- **No impact on normal operation**: Only activates after suppression→restart
- **Reversible**: Can be disabled by removing `was_suppressing_` flag check
- **Observable**: Mode 5 in diagnostics makes behavior fully transparent

---

## Implementation Tasks

### Task 1: Add suppression state members to optimizer.h

**Files:** Modify `components/optimizer/optimizer.h:119` (after `last_defrost_time_`)

Add after `uint32_t last_defrost_time_ = 0;`:
```cpp
      uint32_t suppression_end_time_ = 0;
      bool was_suppressing_ = false;
```

Compile: `esphome compile ecodan-esphome.yaml`
Commit: `"Add suppression recovery state tracking members"`

### Task 2: Track suppression entry + implement recovery ramp in optimizer.cpp

**Files:** Modify `components/optimizer/optimizer.cpp` in `process_adaptive_zone_`

Two changes in the heating-active else branch (lines 299-339):

1. Insert suppression recovery ramp between defrost recovery and normal mode selection
2. Track `was_suppressing_` flag when entering Mode 3, and set `suppression_end_time_` on exit
3. When recovery window expires, clear state and fall through to normal mode

See "Code changes" section above for exact code.

Compile: `esphome compile ecodan-esphome.yaml`
Commit: `"Implement suppression recovery ramp (Mode 5, 20 min)"`

### Task 3: Compile and flash

Prerequisite: Laptop on HOME WiFi, ping 192.168.1.230.

```bash
esphome compile ecodan-esphome.yaml
esphome upload ecodan-esphome.yaml --device 192.168.1.230
```

Verify: `ssh ecodan "sudo journalctl -u ecodan-logger --no-pager -n 10"`
Commit design doc: `"Add suppression recovery ramp design document"`

### Task 4: Monitor and verify overnight

Next morning, check for Mode 5 in logs and compare Hz/COP vs previous nights.
