# Net table (v3)

This is the pin-by-pin definition of the schematic; `architecture.md` explains why each value is what it is. Every part is rated −40 °C or colder except the barrel jack (−25 °C, accepted by the owner).

**Status:** captured in Flux and verified against this table on 2026-11-13 (80 parts, all nets). The owner wired it by hand, module by module; the Flux agent placed the parts. Use this table to re-check the schematic after any later edit.

The schematic is split into eight modules. Each stands alone and joins the others only through the net labels named in `code`.

| # | Module | Parts | Difficulty |
|---|---|---|---|
| 1 | Car input | 8 | easy: one small IC, one FET |
| 2 | Battery and charge path | 9 | easy: same IC and FET again |
| 3 | Current monitors | 6 | easy: two identical ICs |
| 4 | USB-A port | 3 | easy |
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
| `5V`, `3V3`, `XIAO_5V`, `LED_VDD` | 5 V rail; XIAO's 3.3 V output; XIAO 5 V pin; LED supply |
| `EN_SRC`, `EN_5V` | enable source; LMR33630 EN pin |
| `OUT_EN`, `OUT_OFF` | 12 V switch enable (LMR33630 PG); XIAO's switch-off line |
| `HOLD` | XIAO's hold-on line |
| `VCAR_SENSE`, `VBAT_SENSE`, `TEMP_DQ`, `LED_DIN`, `SDA`, `SCL` | XIAO signals |
| `OR1_GATE`, `OR1_VCAP`, `OR2_GATE`, `OR2_VCAP`, `G_HOLD`, `HOLD_D`, `G_OUT`, `OUT_D`, `SW_5V`, `BOOT_5V`, `VCC_5V`, `FB_5V`, `USB_DP`, `USB_DM`, `LED_DIN_R` | local nets |
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
| U_USB | https://www.flux.ai/lcsc/tps2514adbvr~iq2o |
| D_STAT | https://www.flux.ai/kicad-part-library/sk6812~yls |
| D_LED | 1N4148W-13-F (search the library by that name) |
| J_12V | https://www.flux.ai/vasy_skral/pj-063ah~753 |
| D_5V | https://www.flux.ai/lcsc/b140b-13-f~owsk (SMB package) |
| J_XIAO | "Seeed Studio XIAO ESP32C6 SMD No-DrillHole" (pins named `D0`–`D10`; socket footprint to settle at layout). The "SMD Version" entry labels its pins with ESP32-C3 GPIO numbers; avoid it |
| All resistors, shunts, R_CHG | Generic Resistor |
| All capacitors | Generic Capacitor |
| Fuses | generic "Fuse" |
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
- The fuses are generic 2-pin symbols; F_IN, F_BAT and F_OUT need the Keystone 3560 holder footprint and F_CHG the Schurter UMT 250 footprint.

What the placed symbols look like, read back from Flux:

| Part | Symbol pins | Note |
|---|---|---|
| J_XIAO | `D0` … `D10`, `5V`, `3V3`, `GND`, plus bottom pads (`3V3_1`, `GND_1`, `GND_PAD`, `BAT +`, `BAT -`, `MTDO`, `MTDI`, `MTCK`, `MTMS`, `EN`, `BOOT`) | Replaced on 2026-11-13 with the library part "Seeed Studio XIAO ESP32C6 SMD No-DrillHole" after the first one was deleted by accident. Its pin names are plain D-numbers, which is clearer than the first symbol. Leave every bottom pad open |
| Q_HOLD (BSS84LT1G) | G 1, D 2, S 3 | **Suspect symbol.** The usual SOT-23 numbering is gate 1, source 2, drain 3. Wiring by name is right for the schematic, but check the footprint against the onsemi datasheet before layout, or swap to another BSS84 library part |
| Q_OUTDRV (2N7002) | G 1, S 2, D 3 | as expected |
| Q_OUT (DMP4015SK3) | G 1, D 2, S 3 | as expected; no separate tab pin |
| Q_OR1, Q_OR2 (CSD18543Q3A, `kicad-part-library` entry) | S 1, 2, 3; G 4; D 5 | all three source pins join the same net |
| F_IN, F_BAT, F_OUT, F_CHG (generic "Fuse") | P1, P2 | |
| JP_HOLD ("Jumper 2 Open") | A 1, B 2 | |
| D_IGN, D_ZO, D_5V | C 1, A 2 | cathode and anode are named |
| D_LED (1N4148W) | 1, 2 | not named; pin 1 is the cathode, as on the other SOD-123 diodes here |
| D_TVS | 1, 2 | no polarity |
| J_12V (PJ-063AH) | Center Pin 1, Terminal 2, MountPin MP1, MP2 | centre `12V_OUT`; Terminal and both mount pins `GND` |
| L1 | 1, 2 | MPN and 8.2 µH are set, but the part still carries the 4.7 µH part's LCSC number (C1329351): clear or replace it before ordering |

## Module 1 — car input

| Ref | Part | Connect |
|---|---|---|
| J_CAR | 2-way screw terminal, ≥ 10 A | pin 1 `J_CAR_P`; pin 2 `GND` |
| F_IN | 10 A ATO/ATC blade fuse, Keystone 3560 holder | `J_CAR_P` to `VIN_CAR` |
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
| F_BAT | 10 A ATO/ATC blade fuse, Keystone 3560 holder | `J_SLA_P` to `VBAT` |
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
| U_USB | TPS2514ADBVR (SOT-23-6) | 1 DP1 `USB_DP`; 2 GND `GND`; 3, 4 N/C open; 5 IN `5V`; 6 DM1 `USB_DM` (DS) |
| C_USB | 100 nF, 16 V | `5V` to `GND` |
| J_USBA | USB-A receptacle, through-hole | VBUS `5V`; D− `USB_DM`; D+ `USB_DP`; GND and shell `GND` |

Leaves the module: `5V`.

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
| J_XIAO | Seeed XIAO ESP32-C6 | D0 `VCAR_SENSE`; D1 `VBAT_SENSE`; D2 `TEMP_DQ`; D3 `OUT_OFF`; D4 `SDA`; D5 `SCL`; D8 `HOLD`; D10 `LED_DIN`; D6, D7, D9 open; `5V` `XIAO_5V`; `3V3` (pin 12) `3V3`; `GND` (pin 13) `GND`; all bottom pads open |
| D_5V | B140B (SMB), 40 V 1 A Schottky | anode `5V`; cathode `XIAO_5V` |
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
| D_LED | 1N4148W (SOD-123) | anode `5V`; cathode `LED_VDD` |
| D_STAT | SK6812 (5050) | 1 VSS `GND`; 2 DIN `LED_DIN_R`; 3 VDD `LED_VDD`; 4 DOUT open (DS) |
| C_LED | 100 nF, 16 V | `LED_VDD` to `GND` |
| R_LED | 330 Ω | `LED_DIN` to `LED_DIN_R` |
| TP1–TP8 | test points | `VIN_CAR`, `SYS`, `LOAD`, `VBAT`, `5V`, `3V3`, `EN_5V`, `GND` |

XIAO ESP32-C6 GPIO numbers, for the firmware (from Seeed's page, not from the Flux symbol): D0 GPIO0, D1 GPIO1, D2 GPIO2, D3 GPIO21, D4 GPIO22, D5 GPIO23, D8 GPIO19, D10 GPIO18.

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
| F_OUT | 7.5 A ATO/ATC blade fuse, Keystone 3560 holder | `12V_SW` to `12V_OUT` |
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
| Q_HOLD | BSS84 (SOT-23), P-channel | source `SYS`; drain `EN_SRC`; gate `G_HOLD` |
| R_HG1 | 1 MΩ | `SYS` to `G_HOLD` |
| D_ZH | BZT52C12 (SOD-123), 12 V Zener | cathode `SYS`; anode `G_HOLD` |
| R_HG2 | 470 kΩ | `G_HOLD` to `HOLD_D` |
| Q_HOLDDRV | 2N7002 (SOT-23) | drain `HOLD_D`; source `GND`; gate `HOLD` |
| R_HOLD | 100 kΩ | `HOLD` to `GND` |
| JP_HOLD | solder jumper, normally open | `SYS` to `EN_SRC` |

Check: `EN_SRC` has exactly three feeds (D_IGN, Q_HOLD, JP_HOLD) and one load (R_EN1); Q_HOLD's source is on `SYS`; D_ZH's cathode is on `SYS`.

## Open
1. **Barrel jack:** the PJ-063AH has a 2.0 mm centre pin, which is the size for 5.5 × 2.1 mm plugs (the 2.5 mm version is the PJ-063BH). Check your plugs are 2.1 mm.
2. **Parts without a chosen MPN:** the 5 mΩ shunts and the J_TEMP terminal. The screw terminals and USB-A receptacle have library parts but unchecked temperature ratings.
3. **BSS84LT1G symbol:** its drain and source pin numbers look swapped against the usual SOT-23 numbering; settle before layout.
4. **XIAO footprint:** the library part is a surface-mount version; the socket footprint is settled at layout.
5. The tidy and before-layout lists under "As captured in Flux".
