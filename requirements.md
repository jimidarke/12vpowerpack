# Power board — requirements (v2)

Replaces the Flux document `project-specification` (v1, 4S-only).

## Product
A 12 V-nominal power manager on one PCB design, populated at build time as one of two variants:

| | Lithium build | Lead-acid build |
|---|---|---|
| Battery | 4S1P Li-ion, four 18650 on a separate cell board | 12 V sealed AGM, 2–12 Ah |
| Charger IC | BQ25750 | BQ25751 |
| Protector | BQ7791502 + FETs fitted | not fitted; fused battery terminal |
| Use | portable / camping pack | carNet in-car UPS (trunk, under interior flap) |

A board is never switched between chemistries in the field.

## Inputs
- **Car feed:** ignition-switched 12 V socket or fuse tap, 11–14.8 V, automotive transients, reverse polarity possible.
- **USB-C PD:** sink only, requests 20 V (65 W laptop charger class).
- Input is used only above ~12.5 V and disconnected below ~11.5 V, so a parked car's battery is never drained.

## Outputs
- **12 V regulated**, 5 A continuous, barrel jack (5.5 mm), in both builds. Must be correct with no ESP32 fitted.
- **5 V**, 2 A minimum on USB-A with charging-port signature. Non-PD USB-C source port is optional (first item on the cut list).

## Battery and protection
- Lithium: per-cell over/under-voltage, overcurrent, short-circuit, cell balancing, charge/discharge temperature limits — all in hardware (BQ77915). Pack fuse on the cell board.
- Lead-acid: three-stage charge with temperature-compensated voltage, battery fuse, low-voltage cutoff ≈ 11.0–11.5 V, NTC on the battery.
- Loads run from the input while it is present, from the battery otherwise (charger power path).

## Monitoring and control
- Socketed Seeed XIAO ESP32-C6 running ESPHome; MQTT to Home Assistant.
- I2C: charger ADC (input V/I, battery V/I, temperature), INA226 on 12 V out, INA226 on 5 V out, SSD1306 OLED.
- ESP32 can switch the 12 V output off and senses input-present (ignition).
- **Safety never depends on the ESP32.** Charge voltage, current limits, protection and the 12 V setpoint are resistor-set.

## Environment
- Lead-acid build: −40 °C winters (cold-soaked start, warms slowly while driving), trunk summer heat. Parts rated −40 to 85 °C or better.
- Lithium build: no charging below 0 °C.

## Build
- Batch of ~12. Fab assembly where it is economical; hot-air rework at home is acceptable. QFN packages allowed.
- Target ≤ $110 per board excluding cells, cell board and enclosure. Price checkpoint after schematic capture.

## Sizing figures
- 12 V × 5 A = 60 W out; at 90 % efficiency ≈ 6.1 A from an 11 V source.
- Lithium runtime at 30 W: roughly 60–70 min with new 3 Ah cells.
- carNet load ≈ 5 W for 30 min ≈ 2.5 Wh.
