# Block 5 — 5 V rail and USB

**Goal:** `SYS` (9–25 V) → 5 V, 3 A; USB-A charging port; optional non-PD USB-C source port. Capture only.

## Parts
| Function | Part | Note |
|---|---|---|
| Buck | TI LMR33630 (HSOIC-8 variant), 36 V in, 3 A | [DS in `datasheets/lmr33630.txt`] |
| Monitor | INA226 at 0x41, shunt 20 mΩ 1 % | high side on `5V` before the ports |
| USB-A | receptacle + TI TPS2514A on D+/D− | charging-port signature |
| USB-C out (optional, mark "cut-list item") | receptacle + TI TPS25810 | advertises 3 A, switches VBUS on attach |
| ESP32 feed | Schottky diode from `5V` to the XIAO 5V pin | prevents backfeed from the module's USB |

## Values
- Output 5.1 V at the regulator (cable drop). Feedback divider and inductor per the LMR33630 design procedure for 400 kHz-class operation.
- EN divider from `SYS`: 887 kΩ top, 102 kΩ bottom. With the precision enable (rising 1.231 V, 100 mV hysteresis, verified in the EC table) this gives off below 10.97 V falling and on above 11.94 V rising, the same window as the 12 V rail. This is the low-voltage cutoff for the 5 V rail in both builds; the ESP32 is fed from `5V` and powers down with it. Do not tie EN to `VIN`/`SYS` directly.

## Done when
5 V rail and USB-A captured; USB-C source captured as a clearly separable group; reply lists the feedback divider, the EN divider with its computed thresholds, the inductor and the port current limits.
