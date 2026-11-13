# Net table for hand capture (v3)

Draw from this file; `architecture.md` explains why each value is what it is. Every part here is rated −40 °C or colder except the barrel jack (−25 °C, accepted by the owner).

- Pin numbers marked **(DS)** were read from the part's datasheet extract in `datasheets/`. Pin numbers marked **(std)** are the usual numbering for that package and were not in the text extract: check them against the Flux library symbol before wiring.
- Capacitors are X7R ceramic unless stated. Resistors are 1 %, 0603, unless stated.
- Suggested order: block A, then B, then C. After each block, tell me and I will check it against this table with the free Flux reads.

## Nets

| Net | What it is |
|---|---|
| `J_CAR_P` | car feed at the connector, before F_IN |
| `VIN_CAR` | car feed after F_IN and the TVS |
| `SYS_IN` | output of the input ideal diode, before the input shunt |
| `SYS` | main rail: car feed when the ignition is on, battery when it is off |
| `LOAD` | `SYS` after the output shunt; feeds the 12 V switch and the 5 V buck |
| `VBAT` | battery positive, board side of F_BAT |
| `J_SLA_P` | battery positive at the connector |
| `CHG_F` | between F_CHG and R_CHG |
| `12V_SW`, `12V_OUT` | 12 V output before and after F_OUT |
| `5V`, `3V3`, `XIAO_5V`, `LED_VDD` | 5 V rail; XIAO's 3.3 V output; XIAO 5 V pin; LED supply |
| `EN_SRC`, `EN_5V` | enable source; LMR33630 EN pin |
| `OUT_EN`, `OUT_OFF` | 12 V switch enable (LMR33630 PG); XIAO's switch-off line |
| `HOLD` | XIAO's hold-on line |
| `VCAR_SENSE`, `VBAT_SENSE`, `TEMP_DQ`, `LED_DIN`, `SDA`, `SCL` | XIAO signals |
| `OR1_GATE`, `OR1_VCAP`, `OR2_GATE`, `OR2_VCAP`, `G_HOLD`, `HOLD_D`, `G_OUT`, `OUT_D`, `SW_5V`, `BOOT_5V`, `VCC_5V`, `FB_5V`, `USB_DP`, `USB_DM`, `LED_DIN_R` | local nets |
| `GND` | single ground |

## Block A — input, battery path, current monitors

### Parts
| Ref | Part | Value / note |
|---|---|---|
| J_CAR | 2-way PCB screw terminal, 5.08 mm, ≥ 10 A | part open |
| F_IN | ATO/ATC blade fuse in Keystone 3560 PC-mount holder | 10 A |
| D_TVS | SMCJ18CA (SMC) | bidirectional, no polarity |
| U_OR1, U_OR2 | TI LM74700QDBVRQ1 (SOT-23-6) | |
| Q_OR1, Q_OR2 | TI CSD18543Q3A (SON 3.3 mm) | |
| C_OR1, C_OR2 | 100 nF, 25 V | charge-pump capacitors |
| C_VIN | 100 nF, 50 V | |
| C_SYSIN | 100 nF, 50 V | |
| C_SYS1, C_SYS2 | 10 µF, 50 V, 1210 | |
| R_SNS_IN, R_SNS_OUT | 5 mΩ, 1 %, 2512, ≥ 1 W, metal strip | part open |
| U_MON_IN, U_MON_OUT | TI INA226AIDGSR (VSSOP-10) | from LCSC |
| C_MON1, C_MON2 | 100 nF, 16 V | |
| F_CHG | Schurter UMT 250, 1.6 A time-lag (3403.0168.xx) | SMD |
| R_CHG | Vishay AC10, 3.3 Ω, 10 W, 5 %, axial | stand it off the board |
| F_BAT | ATO/ATC blade fuse in Keystone 3560 holder | 10 A |
| J_SLA | 2-way PCB screw terminal, 5.08 mm, ≥ 10 A | part open |
| R_VB1 / R_VB2 | 560 kΩ / 100 kΩ | battery sense divider |
| R_VC1 / R_VC2 | 560 kΩ / 100 kΩ | car sense divider |
| C_VB, C_VC | 100 nF, 16 V | |

### Connections
| Part | Pin | Net |
|---|---|---|
| J_CAR | 1 | `J_CAR_P` |
| J_CAR | 2 | `GND` |
| F_IN | 1 / 2 | `J_CAR_P` / `VIN_CAR` |
| D_TVS | 1 / 2 | `VIN_CAR` / `GND` |
| C_VIN | 1 / 2 | `VIN_CAR` / `GND` |
| U_OR1 | 1 VCAP (DS) | `OR1_VCAP` |
| U_OR1 | 2 GND (DS) | `GND` |
| U_OR1 | 3 EN (DS) | `VIN_CAR` |
| U_OR1 | 4 CATHODE (DS) | `SYS_IN` |
| U_OR1 | 5 GATE (DS) | `OR1_GATE` |
| U_OR1 | 6 ANODE (DS) | `VIN_CAR` |
| C_OR1 | 1 / 2 | `OR1_VCAP` / `VIN_CAR` |
| Q_OR1 | source 1, 2, 3 (std) | `VIN_CAR` |
| Q_OR1 | gate 4 (std) | `OR1_GATE` |
| Q_OR1 | drain 5–8 (std) | `SYS_IN` |
| C_SYSIN | 1 / 2 | `SYS_IN` / `GND` |
| R_SNS_IN | 1 / 2 | `SYS_IN` / `SYS` |
| U_MON_IN | 10 IN+ (DS) | `SYS_IN` (Kelvin, at the shunt pad) |
| U_MON_IN | 9 IN− (DS) | `SYS` (Kelvin, at the shunt pad) |
| U_MON_IN | 8 VBUS (DS) | `SYS` |
| U_MON_IN | 6 VS (DS) | `3V3` |
| U_MON_IN | 7 GND (DS) | `GND` |
| U_MON_IN | 1 A1, 2 A0 (DS) | `GND`, `GND` → address 0x40 |
| U_MON_IN | 3 Alert (DS) | not connected |
| U_MON_IN | 4 SDA, 5 SCL (DS) | `SDA`, `SCL` |
| C_MON1 | 1 / 2 | `3V3` / `GND` |
| C_SYS1, C_SYS2 | 1 / 2 | `SYS` / `GND` |
| F_CHG | 1 / 2 | `SYS` / `CHG_F` |
| R_CHG | 1 / 2 | `CHG_F` / `VBAT` |
| U_OR2 | 1 VCAP | `OR2_VCAP` |
| U_OR2 | 2 GND | `GND` |
| U_OR2 | 3 EN | `VBAT` |
| U_OR2 | 4 CATHODE | `SYS` |
| U_OR2 | 5 GATE | `OR2_GATE` |
| U_OR2 | 6 ANODE | `VBAT` |
| C_OR2 | 1 / 2 | `OR2_VCAP` / `VBAT` |
| Q_OR2 | source 1, 2, 3 | `VBAT` |
| Q_OR2 | gate 4 | `OR2_GATE` |
| Q_OR2 | drain 5–8 | `SYS` |
| F_BAT | 1 / 2 | `VBAT` / `J_SLA_P` |
| J_SLA | 1 | `J_SLA_P` |
| J_SLA | 2 | `GND` |
| R_VB1 | 1 / 2 | `VBAT` / `VBAT_SENSE` |
| R_VB2, C_VB | 1 / 2 | `VBAT_SENSE` / `GND` |
| R_VC1 | 1 / 2 | `VIN_CAR` / `VCAR_SENSE` |
| R_VC2, C_VC | 1 / 2 | `VCAR_SENSE` / `GND` |

Checks for this block: nothing but F_IN touches `J_CAR_P`; the only paths from `SYS` to `VBAT` are F_CHG + R_CHG and Q_OR2; both ideal-diode FETs have their source on the anode side.

## Block B — 5 V rail, power control, 12 V output, USB, LED

### Parts
| Ref | Part | Value / note |
|---|---|---|
| U_MON_OUT, C_MON2, R_SNS_OUT | listed in block A | |
| U_5V | TI LMR33630ADDAR (HSOIC-8, PowerPAD) | 400 kHz |
| C_IN5 | 10 µF, 50 V, 1210 | |
| C_HF5 | 220 nF, 50 V | at the VIN pin |
| C_BOOT | 100 nF, 16 V | |
| C_VCC | 1 µF, 16 V | |
| L1 | Bourns SRP6540-8R2M | 8.2 µH, 5 A saturation |
| C_O1–C_O4 | 22 µF, 16 V, 1210 | |
| R_FBT / R_FBB | 100 kΩ / 24.9 kΩ | 5.0 V |
| D_IGN, D_OEN | BAT46W (SOD-123) | |
| R_EN1 / R_EN2 | 887 kΩ / 102 kΩ | cutoff thresholds |
| C_EN | 10 nF, 16 V | |
| Q_HOLD | BSS84 (SOT-23) | |
| Q_HOLDDRV, Q_OUTDRV | 2N7002 (SOT-23) | |
| D_ZH, D_ZO | BZT52C12 (SOD-123), 12 V | gate clamps |
| R_HG1 / R_HG2 | 1 MΩ / 470 kΩ | |
| R_HOLD | 100 kΩ | pull-down |
| JP_HOLD | solder jumper, open | |
| Q_OUT | Diodes DMP4015SK3 (TO-252) | |
| R_OG1 / R_OG2 | 100 kΩ / 47 kΩ | |
| C_OG | 47 nF, 50 V | slows the 12 V switch |
| R_PG | 100 kΩ | |
| F_OUT | ATO/ATC blade fuse in Keystone 3560 holder | 7.5 A |
| J_12V | Same Sky PJ-063AH | 2.0 mm centre pin; −25 °C rating accepted |
| C_12V | 100 nF, 50 V | |
| U_USB | TI TPS2514ADBVR (SOT-23-6) | |
| C_USB | 100 nF, 16 V | |
| J_USBA | USB-A receptacle, through-hole | part open |
| D_STAT | SK6812 (5050) | |
| D_LED | 1N4148W (SOD-123) | |
| C_LED | 100 nF, 16 V | |
| R_LED | 330 Ω | |

### Connections
| Part | Pin | Net |
|---|---|---|
| R_SNS_OUT | 1 / 2 | `SYS` / `LOAD` |
| U_MON_OUT | 10 IN+ | `SYS` (Kelvin) |
| U_MON_OUT | 9 IN− | `LOAD` (Kelvin) |
| U_MON_OUT | 8 VBUS | `LOAD` |
| U_MON_OUT | 6 VS, 7 GND | `3V3`, `GND` |
| U_MON_OUT | 1 A1, 2 A0 | `GND`, `3V3` → address 0x41 |
| U_MON_OUT | 3 Alert | not connected |
| U_MON_OUT | 4 SDA, 5 SCL | `SDA`, `SCL` |
| C_MON2 | 1 / 2 | `3V3` / `GND` |
| U_5V | 1 PGND (DS) | `GND` |
| U_5V | 2 VIN (DS) | `LOAD` |
| U_5V | 3 EN (DS) | `EN_5V` |
| U_5V | 4 PG (DS) | `OUT_EN` |
| U_5V | 5 FB (DS) | `FB_5V` |
| U_5V | 6 VCC (DS) | `VCC_5V` |
| U_5V | 7 BOOT (DS) | `BOOT_5V` |
| U_5V | 8 SW (DS) | `SW_5V` |
| U_5V | thermal pad (DS) | `GND` |
| C_IN5, C_HF5 | 1 / 2 | `LOAD` / `GND` |
| C_VCC | 1 / 2 | `VCC_5V` / `GND` |
| C_BOOT | 1 / 2 | `BOOT_5V` / `SW_5V` |
| L1 | 1 / 2 | `SW_5V` / `5V` |
| C_O1–C_O4 | 1 / 2 | `5V` / `GND` |
| R_FBT | 1 / 2 | `5V` / `FB_5V` |
| R_FBB | 1 / 2 | `FB_5V` / `GND` |
| D_IGN | anode / cathode | `VIN_CAR` / `EN_SRC` |
| R_EN1 | 1 / 2 | `EN_SRC` / `EN_5V` |
| R_EN2, C_EN | 1 / 2 | `EN_5V` / `GND` |
| Q_HOLD | source 2 (std) | `SYS` |
| Q_HOLD | drain 3 (std) | `EN_SRC` |
| Q_HOLD | gate 1 (std) | `G_HOLD` |
| R_HG1 | 1 / 2 | `SYS` / `G_HOLD` |
| D_ZH | cathode / anode | `SYS` / `G_HOLD` |
| R_HG2 | 1 / 2 | `G_HOLD` / `HOLD_D` |
| Q_HOLDDRV | drain 3 / source 2 / gate 1 (std) | `HOLD_D` / `GND` / `HOLD` |
| R_HOLD | 1 / 2 | `HOLD` / `GND` |
| JP_HOLD | 1 / 2 | `SYS` / `EN_SRC` |
| Q_OUT | source 3 (std) | `LOAD` |
| Q_OUT | drain 2 and tab (std) | `12V_SW` |
| Q_OUT | gate 1 (std) | `G_OUT` |
| R_OG1, C_OG | 1 / 2 | `LOAD` / `G_OUT` |
| D_ZO | cathode / anode | `LOAD` / `G_OUT` |
| R_OG2 | 1 / 2 | `G_OUT` / `OUT_D` |
| Q_OUTDRV | drain 3 / source 2 / gate 1 (std) | `OUT_D` / `GND` / `OUT_EN` |
| R_PG | 1 / 2 | `5V` / `OUT_EN` |
| D_OEN | anode / cathode | `OUT_EN` / `OUT_OFF` |
| F_OUT | 1 / 2 | `12V_SW` / `12V_OUT` |
| J_12V | centre pin | `12V_OUT` |
| J_12V | sleeve (and switch pin, if any) | `GND` |
| C_12V | 1 / 2 | `12V_OUT` / `GND` |
| U_USB | 1 DP1 (DS) | `USB_DP` |
| U_USB | 2 GND (DS) | `GND` |
| U_USB | 3, 4 N/C (DS) | not connected |
| U_USB | 5 IN (DS) | `5V` |
| U_USB | 6 DM1 (DS) | `USB_DM` |
| C_USB | 1 / 2 | `5V` / `GND` |
| J_USBA | VBUS / D− / D+ / GND / shell | `5V` / `USB_DM` / `USB_DP` / `GND` / `GND` |
| D_LED | anode / cathode | `5V` / `LED_VDD` |
| D_STAT | 1 VSS (DS) | `GND` |
| D_STAT | 2 DIN (DS) | `LED_DIN_R` |
| D_STAT | 3 VDD (DS) | `LED_VDD` |
| D_STAT | 4 DOUT (DS) | not connected |
| C_LED | 1 / 2 | `LED_VDD` / `GND` |
| R_LED | 1 / 2 | `LED_DIN` / `LED_DIN_R` |

Checks for this block: `EN_SRC` has exactly three feeds (D_IGN, Q_HOLD, JP_HOLD) and one load (R_EN1); both Zeners have their cathode on the FET's source; `OUT_EN` connects only to U_5V PG, R_PG, Q_OUTDRV gate and D_OEN.

## Block C — controller socket and sensors

### Parts
| Ref | Part | Value / note |
|---|---|---|
| J_XIAO | 2 × 1×7 female header, 2.54 mm | Seeed XIAO ESP32-C6; use the Flux library footprint |
| D_5V | B140 (SMA), 40 V 1 A Schottky | |
| C_X5 | 10 µF, 16 V | |
| C_X3 | 1 µF, 16 V | |
| R_SDA, R_SCL, R_DQ | 4.7 kΩ | pull-ups |
| J_TEMP | 3-way PCB screw terminal, 3.5 mm | DS18B20 probe; part open |
| TP1–TP8 | test points | `VIN_CAR`, `SYS`, `LOAD`, `VBAT`, `5V`, `3V3`, `EN_5V`, `GND` |

### Connections
| XIAO pin | GPIO | Net |
|---|---|---|
| D0 | GPIO0 | `VCAR_SENSE` |
| D1 | GPIO1 | `VBAT_SENSE` |
| D2 | GPIO2 | `TEMP_DQ` |
| D3 | GPIO21 | `OUT_OFF` |
| D4 | GPIO22 | `SDA` |
| D5 | GPIO23 | `SCL` |
| D6 | GPIO16 | not connected (UART TX, left free for debugging) |
| D7 | GPIO17 | not connected |
| D8 | GPIO19 | `HOLD` |
| D9 | GPIO20 | not connected |
| D10 | GPIO18 | `LED_DIN` |
| 5V | | `XIAO_5V` |
| GND | | `GND` |
| 3V3 | | `3V3` |

| Part | Pin | Net |
|---|---|---|
| D_5V | anode / cathode | `5V` / `XIAO_5V` |
| C_X5 | 1 / 2 | `XIAO_5V` / `GND` |
| C_X3 | 1 / 2 | `3V3` / `GND` |
| R_SDA | 1 / 2 | `3V3` / `SDA` |
| R_SCL | 1 / 2 | `3V3` / `SCL` |
| R_DQ | 1 / 2 | `3V3` / `TEMP_DQ` |
| J_TEMP | 1 / 2 / 3 | `GND` / `TEMP_DQ` / `3V3` |

Checks for this block: `3V3` comes only from the XIAO and feeds only the two INA226, the three pull-ups and J_TEMP; nothing drives `5V` back from `XIAO_5V`.

## Open
1. **Barrel jack:** the PJ-063AH takes a 2.0 mm centre pin; check it against your plugs.
2. **Parts without a chosen MPN:** the screw terminals, the USB-A receptacle and the 5 mΩ shunts. Any part meeting the value, package and −40 °C rating will do.
3. **(std) pin numbers:** Q_OR1/Q_OR2, Q_OUT, Q_HOLD, the two 2N7002 and the diodes' anode/cathode pin numbers must be read off the Flux symbols.
4. **XIAO footprint:** use the Flux library part for the XIAO ESP32-C6 so the row spacing is right.
