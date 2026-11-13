# Block 4 — 12 V output rail

**Goal:** `SYS` (9–25 V) → regulated 12.0 V, 5 A continuous, on a barrel jack, correct with no ESP32. Capture only.

## Parts
| Function | Part | Note |
|---|---|---|
| Converter | TI TPS552882 (VQFN-HR) | boost-side FETs internal; **buck-side FETs external** on DR1H/DR1L [DS] |
| Buck-side FETs | 2× N-FET ≥ 40 V, low gate charge | per the datasheet's selection guidance |
| Monitor | INA226 at 0x40, shunt 10 mΩ 1 % (8 A full scale within ±81.92 mV) | high side on `12V_OUT` |
| Protection | F_OUT 7.5 A fuse or resettable; output TVS | |
| Jack | Same Sky PJ-063AH (8 A) | |

## Verified datasheet facts (TPS552882)
- Input 2.7–36 V, output 0.8–22 V; FB reference 1.2 V ±1 %; fixed 4 ms soft-start; average inductor current limit programmable to 16 A via RILIM; switching frequency set by RFSW; EN/UVLO threshold 1.15 V with 5 µA hysteresis current.

## Values
- FB: 180 kΩ / 20 kΩ → 12.0 V.
- EN/UVLO divider on `SYS`: output off below ≈ 11.0 V falling, on above ≈ 12.0 V rising (this is the lead-acid low-voltage cutoff). Compute from the datasheet's UVLO equations.
- An open-drain net `12V_EN_N` from the ESP32 can pull EN low; default (ESP32 absent) = enabled.
- Average inductor limit sized for 6 A output at 11 V input (≈ 7.5 A inductor current) with margin; frequency and inductor per the datasheet design procedure.
- Keep input capacitance on `SYS` modest and report the total, for the protector inrush check.

## Done when
12.0 V rail captured with monitor, fuse and jack; reply gives RILIM, RFSW, inductor, FETs chosen and the computed UVLO thresholds.
