# Net table (v3)

This is the pin-by-pin definition of the schematic; `architecture.md` explains why each value is what it is. Every part is rated −40 °C or colder except the barrel jack (−25 °C, accepted by the owner).

**KiCad (2026-11-14):** this table is now the source of the KiCad schematic. `kicad/gen/gen_sch.py` reads the module tables (Connect column) and the LCSC part tables (LCSC, MPN and Fit fields) and writes `kicad/powerpack.kicad_sch`; `kicad/gen/check_sch.py` compares KiCad's netlist with this table pin by pin. Keep the Connect column in the forms the generator reads: `` `A` to `B` `` for two-pin parts, otherwise `pin spec `NET`` items separated by semicolons, with "open" for unconnected pins. In KiCad the 3557-2 holders use pads 1+2 for the first net and 3+4 for the second (the footprint's real clip pairs), and TP1–TP8 are placed. The Flux notes below are history.

**Flux status (history):** captured in Flux and verified against this table on 2026-11-13 (80 parts, all nets). The owner wired it by hand, module by module; the Flux agent placed the parts. Use this table to re-check the schematic after any later edit.

**v3.1 (2026-11-14), captured and verified the same day:** module 4 lost U_USB (D+ and D− tied on `USB_D`), module 6 swapped the SK6812 status LED for two plain LEDs, D_TVS became the Diodes SMCJ18CAQ-13-F and D_5V a B5819W. The owner did the edits by hand; the agent placed the six new parts. The schematic has 77 parts and every net matches this table (`GND` 47 pins). The empty net labels were deleted the same day (41 nets), and every SMT part now carries the package, MPN and LCSC number from the LCSC part table below (checked with `get_bom`).

The schematic is split into eight modules. Each stands alone and joins the others only through the net labels named in `code`.

| # | Module | Parts | Difficulty |
|---|---|---|---|
| 1 | Car input | 8 | easy: one small IC, one FET |
| 2 | Battery and charge path | 9 | easy: same IC and FET again |
| 3 | Current monitors | 6 | easy: two identical ICs |
| 4 | USB-A port | 2 | easy |
| 5 | 5 V buck | 13 | medium: one IC, all values given |
| 6 | Controller, sensors, LED | 20 | medium: many small parts, one module |
| 7 | 12 V output switch | 11 | fiddly: FET and diode directions matter |
| 8 | Enable and hold | 11 | fiddly: FET and diode directions matter |

Conventions:
- Pin numbers marked **(DS)** were read from the datasheet extract in `datasheets/`. Where a pin is given by name only (source, gate, drain, anode, cathode), use the name on the Flux symbol; the number depends on the symbol.
- Capacitors are X7R ceramic unless stated. Resistors are 1 %, 0603, unless stated.
- To check the schematic against this table, read it back with the free Flux reads (`get_nets`, `get_components`).

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
| `5V`, `3V3`, `XIAO_5V` | 5 V rail; XIAO's 3.3 V output; XIAO 5 V pin |
| `EN_SRC`, `EN_5V` | enable source; LMR33630 EN pin |
| `OUT_EN`, `OUT_OFF` | 12 V switch enable (LMR33630 PG); XIAO's switch-off line |
| `HOLD` | XIAO's hold-on line |
| `VCAR_SENSE`, `VBAT_SENSE`, `TEMP_DQ`, `LED_G`, `LED_R`, `SDA`, `SCL` | XIAO signals |
| `OR1_GATE`, `OR1_VCAP`, `OR2_GATE`, `OR2_VCAP`, `G_HOLD`, `HOLD_D`, `G_OUT`, `OUT_D`, `SW_5V`, `BOOT_5V`, `VCC_5V`, `FB_5V`, `USB_D`, `LED_G_A`, `LED_R_A` | local nets |
| `GND` | single ground |

## Flux library parts

Looked up with the free project search on 2026-11-13.

| Used for | Flux library part |
|---|---|
| U_OR1, U_OR2 | https://www.flux.ai/silicon-yard/lm74700qdbvrq1~gr |
| Q_OR1, Q_OR2 | https://www.flux.ai/kicad-part-library/csd18543q3a~ots (the `lcsc` entry of the same name could not be placed) |
| U_MON_IN, U_MON_OUT | https://www.flux.ai/adrian95/ina226aidgsr~u2n |
| D_TVS | https://www.flux.ai/lcsc/smcj18caq-13-f~qsgb (Diodes Inc. SMCJ18CAQ-13-F; the Liown entry first placed is not recommended for new designs) |
| J_CAR, J_SLA | https://www.flux.ai/jharwinbarrozo/xy301v-a-50-2p~u6 (5 mm, 15 A screw terminal; temperature rating not checked) |
| U_5V | https://www.flux.ai/lcsc/lmr33630addar~jgsz |
| L1 | https://www.flux.ai/lcsc/srp6540-4r7m~ar8j (same package; set MPN SRP6540-8R2M and 8.2 µH) |
| Q_OUT | https://www.flux.ai/lcsc/dmp4015sk3-13~94bh |
| Q_HOLD | https://www.flux.ai/adrian95/bss84lt1g~kww |
| Q_HOLDDRV, Q_OUTDRV | https://www.flux.ai/jecstronic/2n7002h6327xtsa2~wyr |
| D_IGN, D_OEN | https://www.flux.ai/jselfridge/bat46w-7-f~x5 |
| D_ZH, D_ZO | https://www.flux.ai/lcsc/bzt52c12-7-f~p7ye |
| D_GRN, D_RED | 0603 LEDs; the LCSC parts are in the LCSC part table below. Library links still to look up |
| J_12V | https://www.flux.ai/vasy_skral/pj-063ah~753 |
| D_5V | https://www.flux.ai/lcsc/b140b-13-f~owsk (SMB) as captured; change to a B5819W SOD-123 part (LCSC C64885) and rewire by pin name |
| J_XIAO | "Seeed Studio XIAO ESP32C6 SMD No-DrillHole" (pins named `D0`–`D10`; socket footprint to settle at layout). The "SMD Version" entry labels its pins with ESP32-C3 GPIO numbers; avoid it |
| All resistors, shunts, R_CHG | Generic Resistor |
| All capacitors | Generic Capacitor |
| Fuses | generic "Fuse"; F_IN, F_BAT and F_OUT get the Keystone 3557-2 footprint at layout |
| JP_HOLD | "Jumper 2 Open" |
| J_USBA | "USB type A_61400416021" (Würth) |
| J_TEMP | placeholder "Jumper 1x3 open"; a 3-way terminal is still to choose |
| Test points | not placed |

## As captured in Flux

All 80 parts are placed and wired. The Flux agent placed them in three place-only runs on 2026-11-13; the wiring is the owner's.

Still to tidy in the Flux project:
- **F_BAT:** set the current rating to 10 A (it is at the symbol's 5 A default). F_IN is 10 A, F_OUT 7.5 A and F_CHG 1.6 A, as intended.
- **D_TVS:** the placed part (Liown SMCJ18CA, LCSC C2925539) is flagged "not recommended for new designs". Replace it with https://www.flux.ai/lcsc/smcj18caq-13-f~qsgb (Diodes Inc. SMCJ18CAQ-13-F, the automotive-grade version of the datasheet in `datasheets/smcj.txt`).
- **L1:** MPN and 8.2 µH are set, but it still carries the 4.7 µH part's LCSC number (C1329351).
- **Spares and empty nets:** delete R1 and C1, and the empty nets `Net 1`, `J_12V` and `C_SYSIN`.
- **Test points:** not placed.

To fix before layout (they do not affect the schematic):
- Every generic resistor and capacitor was placed with an 0603 package. The shunts (2512), R_CHG (axial), the 10 µF and 22 µF capacitors (1210) need their package set.
- J_TEMP is a "Jumper 1x3 open" symbol with pins A, C, B, wired A `GND`, C `3V3`, B `TEMP_DQ`. Swap it for a 3-way terminal with the pin order in module 6.
- J_USBA is a Würth 61400416021 with pins GND 1, D− 2, D+ 3, VBUS 4 and no shell pin.
- The fuses are generic 2-pin symbols; F_IN, F_BAT and F_OUT need the Keystone 3557-2 holder footprint (`datasheets/keystone-3557.txt`) and F_CHG the Schurter UMT 250 footprint.

What the placed symbols look like, read back from Flux:

| Part | Symbol pins | Note |
|---|---|---|
| J_XIAO | Library part "Seeed Studio XIAO ESP32C6" (through-hole, placed 2026-11-14): pins 1–11 are D0–D10 with long names (e.g. `SDIO-DATA1_GPIO21_D3`, `D8_SCK_GPIO19_SDIO-CLK`), 12 `3V3`, 13 `GND`, 14 `5V`, 15–25 bottom pads | Footprint checked: 14 plated holes of 1.1 mm, rows 15.24 mm apart, 2.54 mm pitch (Seeed: 15.25 mm, 1.0 mm). The footprint also carries the bottom SMD pads (BAT+, BAT−, GND_PAD, JTAG): leave them unconnected and keep traces clear. Leave every bottom pad open; no LiPo |
| Q_HOLD (BSS84LT1G symbol, ordered as LRC LBSS84LT1G) | G 1, D 2, S 3 | **Symbol is wrong (confirmed 2026-11-14).** The onsemi BSS84LT1 datasheet (SOT-23 case 318, style 21) gives gate 1, **source 2, drain 3**; the LRC part is a pin-compatible second source. Wired by name, pad 2 would put `EN_SRC` on the physical source and pad 3 `SYS` on the drain, so the body diode would feed `EN_SRC` from the battery permanently and the board could never time out or latch off. Fix: wire by pin number, so symbol pin **D (2) goes to `SYS`** and symbol pin **S (3) goes to `EN_SRC`**, with a note on the canvas. No corrected Flux library part was found |
| Q_OUTDRV (2N7002) | G 1, S 2, D 3 | as expected |
| Q_OUT (DMP4015SK3) | G 1, D 2, S 3 | as expected; no separate tab pin |
| Q_OR1, Q_OR2 (CSD18543Q3A, `kicad-part-library` entry) | S 1, 2, 3; G 4; D 5 | all three source pins join the same net |
| F_IN, F_BAT, F_OUT (Keystone 3557-2, placed 2026-11-14) | 1, 2, 3, 4 | Wired 1+3 to the supply side and 2+4 to the load side. **Check at layout that pads 1 and 3 are the two legs of the same clip;** if 1 and 2 share a clip this wiring shorts across the fuse |
| F_CHG (generic "Fuse") | P1, P2 | footprint still to set |
| J_TEMP (KF301-5.0-3P, C474882) | 1, 2, 3 | pin 1 `GND`, 2 `TEMP_DQ`, 3 `3V3`. The KF301 is rated only to −30 °C; order the Phoenix MKDS 1,5/3 (1715035), which fits the same 5.0 mm footprint |
| JP_HOLD ("Jumper 2 Open") | A 1, B 2 | |
| D_IGN, D_ZO, D_5V | C 1, A 2 | cathode and anode are named |
| D_TVS | 1, 2 | no polarity |
| J_12V (PJ-063AH) | Center Pin 1, Terminal 2, MountPin MP1, MP2 | centre `12V_OUT`; Terminal and both mount pins `GND` |
| L1 | 1, 2 | MPN and 8.2 µH are set, but the part still carries the 4.7 µH part's LCSC number (C1329351): clear or replace it before ordering |

## Module 1 — car input

| Ref | Part | Connect |
|---|---|---|
| J_CAR | 2-way screw terminal, ≥ 10 A | pin 1 `J_CAR_P`; pin 2 `GND` |
| F_IN | 10 A ATO/ATC blade fuse, Keystone 3557-2 holder (hand-soldered) | `J_CAR_P` to `VIN_CAR` |
| D_TVS | SMCJ18CA (SMC), bidirectional | `VIN_CAR` to `GND` |
| C_VIN | 100 nF, 50 V | `VIN_CAR` to `GND` |
| U_OR1 | LM74700QDBVRQ1 (SOT-23-6) | 1 VCAP `OR1_VCAP`; 2 GND `GND`; 3 EN `VIN_CAR`; 4 CATHODE `SYS_IN`; 5 GATE `OR1_GATE`; 6 ANODE `VIN_CAR` (DS) |
| C_OR1 | 100 nF, 25 V | `OR1_VCAP` to `VIN_CAR` |
| Q_OR1 | CSD18543Q3A | source `VIN_CAR`; gate `OR1_GATE`; drain `SYS_IN` |
| C_SYSIN | 100 nF, 50 V | `SYS_IN` to `GND` |

Leaves the module: `VIN_CAR`, `SYS_IN`. Check: only F_IN touches `J_CAR_P`; Q_OR1's source is on `VIN_CAR`.

## Module 2 — battery and charge path

| Ref | Part | Connect |
|---|---|---|
| J_SLA | 2-way screw terminal, ≥ 10 A | pin 1 `J_SLA_P`; pin 2 `GND` |
| F_BAT | 10 A ATO/ATC blade fuse, Keystone 3557-2 holder (hand-soldered) | `J_SLA_P` to `VBAT` |
| U_OR2 | LM74700QDBVRQ1 | 1 VCAP `OR2_VCAP`; 2 GND `GND`; 3 EN `VBAT`; 4 CATHODE `SYS`; 5 GATE `OR2_GATE`; 6 ANODE `VBAT` (DS) |
| C_OR2 | 100 nF, 25 V | `OR2_VCAP` to `VBAT` |
| Q_OR2 | CSD18543Q3A | source `VBAT`; gate `OR2_GATE`; drain `SYS` |
| F_CHG | Schurter UMT 250, 1.6 A time-lag (3403.0168.xx), SMD | `SYS` to `CHG_F` |
| R_CHG | Vishay AC10, 3.3 Ω, 10 W, 5 %, axial | `CHG_F` to `VBAT` |
| C_SYS1, C_SYS2 | 10 µF, 50 V, 1210 (two) | `SYS` to `GND` |

Leaves the module: `SYS`, `VBAT`. Check: the only paths from `SYS` to `VBAT` are F_CHG + R_CHG and Q_OR2; Q_OR2's source is on `VBAT`.

## Module 3 — current monitors

| Ref | Part | Connect |
|---|---|---|
| R_SNS_IN | 5 mΩ, 1 %, 2512, ≥ 1 W | `SYS_IN` to `SYS` |
| U_MON_IN | INA226AIDGSR (VSSOP-10) | 10 IN+ `SYS_IN`; 9 IN− `SYS`; 8 VBUS `SYS`; 6 VS `3V3`; 7 GND `GND`; 1 A1 `GND`; 2 A0 `GND`; 3 Alert open; 4 SDA `SDA`; 5 SCL `SCL` (DS) |
| C_MON1 | 100 nF, 16 V | `3V3` to `GND` |
| R_SNS_OUT | 5 mΩ, 1 %, 2512, ≥ 1 W | `SYS` to `LOAD` |
| U_MON_OUT | INA226AIDGSR | 10 IN+ `SYS`; 9 IN− `LOAD`; 8 VBUS `LOAD`; 6 VS `3V3`; 7 GND `GND`; 1 A1 `GND`; 2 A0 `3V3`; 3 Alert open; 4 SDA `SDA`; 5 SCL `SCL` |
| C_MON2 | 100 nF, 16 V | `3V3` to `GND` |

Leaves the module: `LOAD`, `3V3`, `SDA`, `SCL`. Check: the two ICs differ only at pin 2 (A0): `GND` gives address 0x40, `3V3` gives 0x41. IN+ and IN− connect at the shunt pads (Kelvin) at layout.

## Module 4 — USB-A port

| Ref | Part | Connect |
|---|---|---|
| C_USB | 100 nF, 50 V | `5V` to `GND` |
| J_USBA | USB-A receptacle, through-hole | VBUS `5V`; D− `USB_D`; D+ `USB_D`; GND and shell `GND` |

Leaves the module: `5V`. Check: `USB_D` has exactly two pins, J_USBA D+ and D−, and nothing else (the BC1.2 dedicated-charger short). U_USB (TPS2514A) was removed in v3.1.

## Module 5 — 5 V buck

| Ref | Part | Connect |
|---|---|---|
| U_5V | LMR33630ADDAR (HSOIC-8, PowerPAD) | 1 PGND `GND`; 2 VIN `LOAD`; 3 EN `EN_5V`; 4 PG `OUT_EN`; 5 FB `FB_5V`; 6 VCC `VCC_5V`; 7 BOOT `BOOT_5V`; 8 SW `SW_5V`; thermal pad `GND` (DS) |
| C_IN5 | 10 µF, 50 V, 1210 | `LOAD` to `GND` |
| C_HF5 | 220 nF, 50 V | `LOAD` to `GND` |
| C_VCC | 1 µF, 16 V | `VCC_5V` to `GND` |
| C_BOOT | 100 nF, 16 V | `BOOT_5V` to `SW_5V` |
| L1 | Bourns SRP6540-8R2M, 8.2 µH | `SW_5V` to `5V` |
| C_O1–C_O4 | 22 µF, 16 V, 1210 (four) | `5V` to `GND` |
| R_FBT | 100 kΩ | `5V` to `FB_5V` |
| R_FBB | 24.9 kΩ | `FB_5V` to `GND` |

Leaves the module: `LOAD`, `5V`, `EN_5V` (to module 8), `OUT_EN` (to module 7).

## Module 6 — controller, sensors, status LED

| Ref | Part | Connect |
|---|---|---|
| J_XIAO | Seeed XIAO ESP32-C6 | D0 `VCAR_SENSE`; D1 `VBAT_SENSE`; D2 `TEMP_DQ`; D3 `OUT_OFF`; D4 `SDA`; D5 `SCL`; D8 `HOLD`; D9 `LED_R`; D10 `LED_G`; D6, D7 open; `5V` `XIAO_5V`; `3V3` (pin 12) `3V3`; `GND` (pin 13) `GND`; all bottom pads open |
| D_5V | B5819W (SOD-123), 40 V 1 A Schottky (replaced the B140B in v3.1) | anode `5V`; cathode `XIAO_5V` |
| C_X5 | 10 µF, 16 V | `XIAO_5V` to `GND` |
| C_X3 | 1 µF, 16 V | `3V3` to `GND` |
| R_SDA | 4.7 kΩ | `3V3` to `SDA` |
| R_SCL | 4.7 kΩ | `3V3` to `SCL` |
| R_DQ | 4.7 kΩ | `3V3` to `TEMP_DQ` |
| J_TEMP | 3-way screw terminal (DS18B20 probe) | pin 1 `GND`; pin 2 `TEMP_DQ`; pin 3 `3V3` |
| R_VB1 | 560 kΩ | `VBAT` to `VBAT_SENSE` |
| R_VB2 | 100 kΩ | `VBAT_SENSE` to `GND` |
| C_VB | 100 nF, 16 V | `VBAT_SENSE` to `GND` |
| R_VC1 | 560 kΩ | `VIN_CAR` to `VCAR_SENSE` |
| R_VC2 | 100 kΩ | `VCAR_SENSE` to `GND` |
| C_VC | 100 nF, 16 V | `VCAR_SENSE` to `GND` |
| R_LG | 1 kΩ | `LED_G` to `LED_G_A` |
| D_GRN | green LED, 0603 | anode `LED_G_A`; cathode `GND` |
| R_LR | 1 kΩ | `LED_R` to `LED_R_A` |
| D_RED | red LED, 0603 | anode `LED_R_A`; cathode `GND` |
| TP1–TP8 | test points | `VIN_CAR`, `SYS`, `LOAD`, `VBAT`, `5V`, `3V3`, `EN_5V`, `GND` |

XIAO ESP32-C6 GPIO numbers, for the firmware (from Seeed's page, re-read 2026-11-14, not from the Flux symbol): D0 GPIO0, D1 GPIO1, D2 GPIO2, D3 GPIO21, D4 GPIO22, D5 GPIO23, D8 GPIO19, D9 GPIO20, D10 GPIO18.

Leaves the module: `HOLD` (to module 8), `OUT_OFF` (to module 7). Check: `3V3` comes only from the XIAO and feeds only the two INA226, the three pull-ups and J_TEMP; `XIAO_5V` is fed only through D_5V.

## Module 7 — 12 V output switch

| Ref | Part | Connect |
|---|---|---|
| Q_OUT | DMP4015SK3 (TO-252), P-channel | source `LOAD`; drain and tab `12V_SW`; gate `G_OUT` |
| R_OG1 | 100 kΩ | `LOAD` to `G_OUT` |
| C_OG | 47 nF, 50 V | `LOAD` to `G_OUT` |
| D_ZO | BZT52C12 (SOD-123), 12 V Zener | cathode `LOAD`; anode `G_OUT` |
| R_OG2 | 47 kΩ | `G_OUT` to `OUT_D` |
| Q_OUTDRV | 2N7002 (SOT-23) | drain `OUT_D`; source `GND`; gate `OUT_EN` |
| R_PG | 100 kΩ | `5V` to `OUT_EN` |
| D_OEN | BAT46W (SOD-123) | anode `OUT_EN`; cathode `OUT_OFF` |
| F_OUT | 7.5 A ATO/ATC blade fuse, Keystone 3557-2 holder (hand-soldered) | `12V_SW` to `12V_OUT` |
| J_12V | Same Sky PJ-063AH (for 5.5 × 2.1 mm plugs) | Center Pin `12V_OUT`; Terminal and both mount pins `GND` |
| C_12V | 100 nF, 50 V | `12V_OUT` to `GND` |

Check: Q_OUT's source is on `LOAD` (the supply side); D_ZO's cathode is on `LOAD`; `OUT_EN` connects only to U_5V pin 4, R_PG, Q_OUTDRV's gate and D_OEN's anode.

## Module 8 — enable and hold

| Ref | Part | Connect |
|---|---|---|
| D_IGN | BAT46W (SOD-123) | anode `VIN_CAR`; cathode `EN_SRC` |
| R_EN1 | 887 kΩ | `EN_SRC` to `EN_5V` |
| R_EN2 | 102 kΩ | `EN_5V` to `GND` |
| C_EN | 10 nF, 16 V | `EN_5V` to `GND` |
| Q_HOLD | BSS84 (SOT-23), P-channel | physical source (pad 2) `SYS`; physical drain (pad 3) `EN_SRC`; gate (pad 1) `G_HOLD`. On the Flux symbol, whose names are swapped, that is pin **D (2) to `SYS`**, pin **S (3) to `EN_SRC`** |
| R_HG1 | 1 MΩ | `SYS` to `G_HOLD` |
| D_ZH | BZT52C12 (SOD-123), 12 V Zener | cathode `SYS`; anode `G_HOLD` |
| R_HG2 | 470 kΩ | `G_HOLD` to `HOLD_D` |
| Q_HOLDDRV | 2N7002 (SOT-23) | drain `HOLD_D`; source `GND`; gate `HOLD` |
| R_HOLD | 100 kΩ | `HOLD` to `GND` |
| JP_HOLD | solder jumper, normally open | `SYS` to `EN_SRC` |

Check: `EN_SRC` has exactly three feeds (D_IGN, Q_HOLD, JP_HOLD) and one load (R_EN1); Q_HOLD's source is on `SYS`; D_ZH's cathode is on `SYS`.

## LCSC part table (v3.1, batch of 5)

This is the BOM for ordering. It was read live from the JLCPCB parts library on 2026-11-14; prices are in USD at qty 10–50. Library type: **B** Basic and **PE** Preferred Extended carry no feeder fee on JLCPCB Economic PCBA, while **E** Extended carries US$3.07 per part type per order (JLCPCB assembly price page, updated 2026-10-22). "Fit" says who solders the part:
- **fab:** JLCPCB fits it.
- **hand:** the owner hand-solders it. Order these from LCSC with the JLCPCB order so they ship together.
- **DK:** the owner hand-solders it. Order these from DigiKey Canada, because they are out of stock at LCSC or are through-hole parts better bought in CAD.

Rule: the fab fits every B and PE part plus the four fine-pitch or thermal-pad IC types; every other E part is hand-soldered. Moving one more E type to the fab costs about C$0.85 per board at a batch of 5.

### Fitted by JLCPCB

| Part | Designators | Qty | LCSC | Lib | USD each | Temp | Note |
|---|---|---|---|---|---|---|---|
| TI LM74700QDBVRQ1 | U_OR1, U_OR2 | 2 | C2941042 | E | 2.456 | −40 to 150 | |
| TI CSD18543Q3A | Q_OR1, Q_OR2 | 2 | C840100 | E | 1.154 | −55 to 150 | |
| TI INA226AIDGSR | U_MON_IN, U_MON_OUT | 2 | C49851 | E | 0.560 | −40 to 125 | |
| TI LMR33630ADDAR | U_5V | 1 | C841384 | E | 0.525 | −40 to 125 (TJ) | listed as "ESOP-8" |
| LRC LBSS84LT1G | Q_HOLD | 1 | C8492 | PE | 0.028 | −55 to 150 | −50 V; no Basic BSS84 exists. Check the pin numbering against its SOT-23 drawing (part C of `blocks/02-v31-schematic-edits.md`) |
| CJ 2N7002 | Q_HOLDDRV, Q_OUTDRV | 2 | C8545 | B | 0.016 | **[TBC]** (blank in the listing) | Nexperia 2N7002,215 (C65189, E, −65 to 150) if the CJ rating cannot be confirmed |
| MDD B5819W | D_5V | 1 | C64885 | PE | 0.020 | −55 to 125 (listing) | replaces the B140B (SMB): 40 V, 1 A, SOD-123 |
| KENTO KT-0603R, red | D_RED | 1 | C2286 | B | 0.008 | −40 to 85 | 1.8–2.4 V |
| Yageo CC0603KRX7R9BB104, 100 nF 50 V X7R 0603 | C_VIN, C_OR1, C_SYSIN, C_OR2, C_MON1, C_MON2, C_USB, C_BOOT, C_VB, C_VC, C_12V | 11 | C14663 | B | 0.010 | X7R | one part for every 100 nF |
| Samsung CL10A105KB8NNNC, 1 µF 50 V X5R 0603 | C_VCC, C_X3 | 2 | C15849 | B | 0.008 | X5R | |
| Samsung CL31A106KBHNNNE, 10 µF 50 V X5R 1206 | C_SYS1, C_SYS2, C_IN5 | 3 | C13585 | B | 0.121 | X5R | DC bias leaves about a third to a half at 14 V **[TBC]**; the three sit on `SYS`/`LOAD`, one shunt apart, so they add. X7R 1210 option: C138687, E |
| Samsung CL21A106KAYNNNE, 10 µF 25 V X5R 0805 | C_X5 | 1 | C15850 | B | 0.031 | X5R | |
| Samsung CL31A226KAHNNNE, 22 µF 25 V X5R 1206 | C_O1–C_O4 | 4 | C12891 | B | 0.103 | X5R | 1206 instead of 1210 (the 1210 is out of stock). Check the effective capacitance at 5 V against LMR33630 Table 9-2; leave room for a fifth **[TBC]** |
| Samsung CL21B224KBFNNNE, 220 nF 50 V X7R **0805** | C_HF5 | 1 | C5378 | B | 0.014 | X7R | the Basic 0603 220 nF is only 25 V |
| Samsung CL10B473KB8NNNC, 47 nF 50 V X7R 0603 | C_OG | 1 | C1622 | B | 0.006 | X7R | |
| FH 0603B103K500NT, 10 nF 50 V X7R 0603 | C_EN | 1 | C57112 | B | 0.010 | X7R | |
| UNI-ROYAL 0603WAF1003T5E, 100 kΩ | R_FBT, R_OG1, R_PG, R_HOLD, R_VB2, R_VC2 | 6 | C25803 | B | 0.002 | −55 to 155 | |
| UNI-ROYAL 4.7 kΩ | R_SDA, R_SCL, R_DQ | 3 | C23162 | B | 0.002 | | |
| UNI-ROYAL 1 MΩ | R_HG1 | 1 | C22935 | B | 0.002 | | |
| UNI-ROYAL 470 kΩ | R_HG2 | 1 | C23178 | B | 0.002 | | |
| UNI-ROYAL 47 kΩ | R_OG2 | 1 | C25819 | B | 0.002 | | |
| UNI-ROYAL 1 kΩ | R_LG, R_LR | 2 | C21190 | B | 0.002 | | |
| UNI-ROYAL 560 kΩ | R_VB1, R_VC1 | 2 | C23203 | PE | 0.002 | | |

### Hand-soldered, from LCSC

| Part | Designators | Qty | LCSC | USD each | Temp | Note |
|---|---|---|---|---|---|---|
| Diodes DMP4015SK3-13 | Q_OUT | 1 | C513222 | 0.992 | −55 to 150 | TO-252 |
| Diodes SMCJ18CA-13-F | D_TVS | 1 | C135149 | 0.275 | −55 to 150 | the part in `datasheets/smcj.txt` (that extract is the non-Q datasheet). The automotive SMCJ18CAQ-13-F (C1975830, US$1.28, 20 in stock) has the same footprint; either will do |
| Bourns SRP6540-8R2M | L1 | 1 | **C2041807** | 1.352 | −55 to 125 **[DS SRP6540]** | the Flux part carries C1329351, which is the 4.7 µH SRP6540-4R7M |
| RALEC LR2512-22R005F4, 5 mΩ 1 % 2 W | R_SNS_IN, R_SNS_OUT | 2 | C108931 | 0.127 | −55 to 170 | 2512 |
| CJ BZT52C12 | D_ZH, D_ZO | 2 | C43491 | 0.021 | −55 to 150 | no Basic BZT52C12 exists |
| Diodes BAT46W-7-F | D_IGN, D_OEN | 2 | C83152 | 0.129 | −55 to 125 | the part in `datasheets/bat46w.txt`; no Basic Schottky ≥ 100 V exists |
| KENTO KT-0603YG, yellow-green | D_GRN | 1 | C2289 | 0.011 | −40 to 85 | 2.0–2.2 V. No Basic 0603 green exists; the KT-0603G (C12624) is 3.1 V |
| RALEC RTT038873FTP, 887 kΩ | R_EN1 | 1 | C103858 | ~0.002 | | sets the low-voltage cutoff; keep the exact value |
| UNI-ROYAL 102 kΩ | R_EN2 | 1 | C22858 | ~0.002 | | as above |
| UNI-ROYAL 24.9 kΩ | R_FBB | 1 | C25962 | ~0.002 | | sets 5.0 V; the nearest Basic value (24 kΩ) would give 5.17 V |

### Hand-soldered, from DigiKey Canada (through-hole, plus F_CHG)

| Part | Designators | Qty | Note |
|---|---|---|---|
| Keystone 3557-2 | F_IN, F_BAT, F_OUT | 3 | 30 A, −50 to 145 °C **[DS Keystone 3557]**. LCSC C352820 has only 22 in stock (15 needed) |
| Vishay AC10, 3.3 Ω 10 W, kinked "EK" leads | R_CHG | 1 | out of stock at LCSC. The in-stock LCSC alternative, TE SBCHE153R3K (C1367870, 17 W, ±10 %), is a different body; only use it with a matching footprint |
| Schurter UMT 250, 1.6 A time-lag (3403.0168.11) | F_CHG | 1 | out of stock at LCSC. The LCSC alternative, SETsafe SCT1032T1.6A250V (C19712561), has no DC rating stated, so it is not used |
| Phoenix Contact MKDS 1,5/2 (1715022), 2-way, 5.0 mm | J_CAR, J_SLA | 2 | 15 A; the family is rated −40 to 105 °C (LCSC C3817933; the 2-way listing leaves it blank, the 3-way states it). Replaces the XY301V, which has no temperature rating. Same 5.0 mm pitch as the placed XY301V symbol; check the hole size at layout |
| Phoenix Contact MKDS 1,5/3 (1715035), 3-way, 5.0 mm | J_TEMP | 1 | −40 to 105 °C (LCSC C6787349). Replaces the jumper placeholder |
| Same Sky PJ-063AH | J_12V | 1 | −25 °C, the accepted exception (LCSC C22434582 has 37 in stock) |
| Würth 61400416021 | J_USBA | 1 | −40 to 105 °C (LCSC C6264900 listing) |
| 1×7 female header, 2.54 mm, about 8.5 mm tall | J_XIAO socket | 2 | e.g. HCTL PM254-1-07-Z-8.5 (LCSC C2897370, −40 to 105 °C) |
| Seeed XIAO ESP32-C6 | J_XIAO | 1 | |
| ATO/ATC blade fuses 10 A, 10 A, 7.5 A | in the 3557-2 holders | 3 | |
| DS18B20 probe, 1 m | on J_TEMP | 1 | |

## Open
1. **Barrel jack:** the PJ-063AH has a 2.0 mm centre pin, which is the size for 5.5 × 2.1 mm plugs (the 2.5 mm version is the PJ-063BH). Check your plugs are 2.1 mm.
2. **Ratings still [TBC]:** CJ 2N7002 temperature (blank in the listing), and the effective capacitance of the 1206 X5R parts on the buck input and output.
3. **BSS84LT1G symbol:** confirmed swapped (onsemi datasheet, style 21: G 1, S 2, D 3). Rewire Q_HOLD by pin number as in module 8 before layout.
4. **XIAO footprint:** the library part is a surface-mount version; the socket footprint is settled at layout.
5. The tidy and before-layout lists under "As captured in Flux".
