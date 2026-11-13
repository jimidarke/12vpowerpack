# Block 6 — ESP32 socket, display, controls

**Goal:** socket for the controller module, I2C bus, OLED header, switch, button, LEDs. Capture only.

## Parts
| Function | Part | Note |
|---|---|---|
| Controller socket | 2× 1×7 female headers, 2.54 mm pitch, for Seeed XIAO ESP32-C6 | **confirm row spacing from Seeed's footprint before layout**; keep copper clear under the antenna end; USB-C end overhangs the board edge |
| OLED | 4-pin header for an SSD1306 0.96" I2C module (0x3C) | pin order GND, VCC, SCL, SDA — confirm against the module bought |
| I2C | 4.7 kΩ pull-ups to `3V3` | `3V3` comes from the XIAO's regulator |
| Power switch | slide or rocker, low current | lithium: pulls `PACK_EN` (BQ77915 PRES) high; lead-acid: enables the converters |
| Button | tactile, to the ESP32 with pull-up | display page / wake |
| LEDs | charger STAT1, STAT2; 12 V good | |

## Pin map
Use the table in `architecture.md` ("ESP32 socket"). Every ESP32-driven control line must have a pull resistor that leaves the board in its safe, working state with the module removed: charging enabled, 12 V enabled.

## Done when
Socket and UI captured; a table of XIAO pin → net in the reply; electrical check clean.
