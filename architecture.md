# Power board — architecture (v3)

Status key: **[DS]** read in the datasheet extract in `datasheets/`; **[calc]** my arithmetic from DS values; **[TBC]** still to confirm (before layout or ordering, as noted).

The schematic was captured in Flux on 2026-11-13. The cost trim of 2026-11-14 (v3.1: USB without a controller IC, two plain LEDs, 3557-2 fuse holders) was captured and verified against `netlist.md` the same day; see "Capture status" at the end.

v3 is the vehicle-only design: one build, 12 V AGM, no charger IC, no USB-C PD input, no 12 V converter, no display. The v2 architecture is in git at tag `v0.2.1`.

## Block diagram

```
J_CAR ─ F_IN ─ TVS ─ VIN_CAR ─ U_OR1 (LM74700-Q1 + Q_OR1) ─ SYS_IN ─ R_SNS_IN ─ SYS

SYS ─┬─ R_SNS_OUT ─ LOAD ─┬─ Q_OUT (P-FET) ─ F_OUT ─ J_12V barrel
     │                    └─ U_5V LMR33630 ─ 5V ─┬─ J_USBA (D+ tied to D−)
     │                                           └─ D ─ XIAO 5V pin
     ├─ F_CHG ─ R_CHG ──────────────┐   (charge)
     └─ U_OR2 (LM74700-Q1 + Q_OR2) ─┤   (discharge: anode VBAT, cathode SYS)
                                  VBAT ─ F_BAT ─ J_SLA
```

- Ignition on: `SYS` follows the car feed. The loads run from the car; the battery charges through R_CHG.
- Ignition off: U_OR1 blocks, `SYS` falls to the battery voltage and U_OR2 conducts. The loads run from the battery.
- The car feed and the battery can share a load if the feed sags under it. Nothing needs them kept apart.

## Net names
Main nets: `VIN_CAR` (after F_IN and the TVS, car side of U_OR1), `SYS_IN` (U_OR1 output, before the input shunt), `SYS`, `LOAD` (after the output shunt), `VBAT`, `12V_OUT`, `5V`, `3V3` (from the XIAO), `XIAO_5V`, `EN_SRC`, `EN_5V`, `OUT_EN`, `OUT_OFF`, `HOLD`, `VCAR_SENSE`, `VBAT_SENSE`, `TEMP_DQ`, `LED_G`, `LED_R`, `SDA`, `SCL`, `GND`. The full list, including the local nets, is the "Nets" table in `netlist.md`.

## Input protection
- F_IN 10 A automotive blade fuse (ATO/ATC) in a Keystone 3557-2 "2 in 1" through-hole holder: Nylon 46 body, 30 A UL, −50 to 145 °C, four Ø1.6 mm holes **[DS Keystone 3557]**. F_BAT and F_OUT use the same holder. It replaced the Keystone 3560 (same ratings **[DS Keystone blade holders]**, C$4.16 against about C$1.92 each) on 2026-11-14. Car-feed current is about 5 A continuous and 7 A at the output peak (requirements, sizing figures) **[calc]**.
- TVS on `VIN_CAR`: bidirectional, 18 V stand-off, clamp ≤ 36 V at its rated surge current (owner's decision 2026-11-13: lower clamp, keep it simple). Part: SMCJ18CA, 1500 W. Order the Diodes Inc. SMCJ18CA-13-F, the part in the datasheet extract (LCSC C135149); the automotive SMCJ18CAQ-13-F has the same footprint and also serves. The Liown version in the Flux library is flagged not recommended for new designs: stand-off 18.0 V, breakdown 20.0–22.1 V, clamps at 29.2 V at 51.4 A, −55 to 150 °C **[DS SMCJ electrical table]**. The limit comes from the parts on `SYS`: LMR33630 36 V operating, 38 V absolute maximum **[DS LMR33630 §7.1, §7.3]**; INA226 36 V operating, 40 V absolute maximum **[DS INA226 §5.1]**.
  - Bidirectional so that reverse polarity (to −16 V) does not conduct through it; U_OR1 blocks the reverse voltage.
  - Accepted consequence: this is below the LM74700-Q1 datasheet's advice to stand off a 24 V jump start and a 35 V suppressed load dump **[DS LM74700-Q1 §10.1.1.3]**. Either event makes the TVS conduct and blows F_IN, or the TVS itself fails short. Nothing downstream is damaged; the unit needs a new fuse or TVS.
- U_OR1, LM74700-Q1 with an external N-FET (VCAP capacitor ≥ 0.1 µF and at least 10 × the FET's CISS; ≥ 100 nF on the cathode **[DS LM74700-Q1 §10.1.1.2.3]**): blocks reverse polarity on J_CAR and stops the battery feeding the car. 3.2–65 V input, −65 V reverse rating, 20 mV regulated forward drop **[DS LM74700-Q1 features, §6.1]**. Q_OR1: TI CSD18543Q3A, 60 V, ±20 V gate, 8.1 mΩ at 10 V, CISS 1150 pF max (so the 0.1 µF VCAP minimum applies), 3.3 mm SON, −55 to 150 °C **[DS CSD18543Q3A]**. At 7 A it dissipates about 0.4 W **[calc]**.

## Battery path
- **Discharge:** U_OR2, a second LM74700-Q1 with Q_OR2, anode on `VBAT`, cathode on `SYS`. Carries up to 4 A continuous, 6 A peak **[calc]**. An ideal diode instead of a Schottky so the 12 V output does not lose 0.4 V and nothing runs hot. Q_OR2 is the same part as Q_OR1; about 0.3 W at 6 A **[calc]**.
- **Charge:** F_CHG then R_CHG from `SYS` to `VBAT`. R_CHG 3.3 Ω **[calc]**:

| Battery voltage (feed at 14.4 V) | Charge current | Power in R_CHG |
|---|---|---|
| 12.6 V (after a normal stop) | 0.55 A | 1.0 W |
| 11.0 V (at the low-voltage cutoff) | 1.0 A | 3.5 W |
| 10.5 V (one shorted cell) | 1.2 A | 4.6 W |

- R_CHG: Vishay AC10, 3.3 Ω, 10 W at 40 °C and 8.4 W at 70 °C, climatic category −55/200, body 44 × 8 mm, kinked-lead pitch 52 mm **[DS Vishay AC]**. Axial; stand it off the board. Out of stock at LCSC (2026-11-14); buy from DigiKey Canada.
- F_CHG: Schurter UMT 250, 1.6 A time-lag, −55 to 125 °C; it carries 1.25 × rated current for at least 60 min and opens within 120 s at 2 × **[DS Schurter UMT 250]**. Normal charging peaks at 1.16 A (14.8 V feed, battery at the cutoff) **[calc]**.
- What F_CHG covers **[calc]**: a reversed battery (about 8 A) and a battery near 0 V (4.4 A) open it within seconds to two minutes. At exactly 1.6 A (battery at 9.1 V) R_CHG dissipates 8.4 W, its 70 °C rating.
- What it does not cover: a battery sitting between about 4 V and 9 V draws 1.6–3.2 A, which the fuse may carry for many minutes while R_CHG dissipates 8–34 W. That needs a battery with several shorted cells; it is the reason R_CHG stands off the board. The XIAO can report it (`VBAT_SENSE` low with the ignition on) but cannot stop it.
- F_BAT 10 A at the battery connector.
- Charge current tapers to zero as the battery reaches the feed voltage; there is no absorb/float staging and no temperature compensation (accepted in requirements v3).
- Recharge is slow: replacing a 3 Ah discharge takes several hours of driving. Lower R_CHG (and raise F_CHG and the resistor rating to match) if a unit is used that way; 3.3 Ω suits 2–12 Ah batteries on the carNet duty.

## Rails
- **12 V output:** `LOAD` through Q_OUT (P-channel FET, high side) and F_OUT 7.5 A to J_12V. Unregulated, about 10.9–14.8 V. Q_OUT: Diodes DMP4015SK3, −40 V, ±25 V gate, 11 mΩ max at −10 V, TO-252, −55 to 150 °C **[DS DMP4015SK3]**; about 0.1 W at 3 A and 0.3 W at 5 A **[calc]**. Gate network: 100 kΩ gate to source, 47 kΩ from the gate to the driver FET, so the gate sees 68 % of the rail: 7.5 V at 11 V and 10.1 V at 14.8 V **[calc]**. A BZT52C12 (11.4–12.7 V, −65 to 150 °C **[DS BZT52C]**) across gate-source clamps it when the rail rises toward the 29 V clamp level. 47 nF gate to source slows the switch: about 1.5 ms on, 4.7 ms off **[calc]**. Overcurrent protection is F_OUT alone; there is no electronic current limit.
- **5 V:** LMR33630ADDA (400 kHz) from `LOAD`, 3.8–36 V in **[DS]**. Inductor: Bourns SRP6540-8R2M, 8.2 µH, 50.5 mΩ, 4.5 A rms, 5 A saturation, −55 to 125 °C **[DS SRP6540]**, against a high-side current limit of 4.5 A typical, 5.05 A maximum **[DS LMR33630 EC table, ISC]**. Values for 5 V at 400 kHz: L 8 µH, COUT 4 × 22 µF, RFBT 100 kΩ, RFBB 24.9 kΩ, CIN 10 µF + 220 nF, CBOOT 100 nF, CVCC 1 µF, no feed-forward capacitor **[DS LMR33630 Table 9-2]**. Feeds the USB-A port and the XIAO.
- **USB-A:** VBUS on `5V`, D+ and D− tied together on net `USB_D` (the BC1.2 dedicated-charger signature) with no controller IC. The port is for loads that draw current regardless of the signature (owner's decision 2026-11-14). Most Android phones also charge at full rate on a shorted pair; some Apple devices limit themselves to about 0.5–1 A.

## Power control
One threshold, set at the LMR33630's precision enable, controls everything. No comparator or logic IC.

```
VIN_CAR ─ D_IGN (Schottky) ─┐
                            ├─ EN_SRC ─ 887 kΩ ─ EN_5V (LMR33630 EN) ─ 102 kΩ ─ GND
SYS ─ Q_HOLD (BSS84) ───────┘
        gate ← N-FET ← HOLD (XIAO GPIO, 100 kΩ pull-down)     JP_HOLD solder jumper across Q_HOLD

LMR33630 PG ─ OUT_EN ─ 100 kΩ pull-up to 5V ─ N-FET gate ─ pulls Q_OUT gate low (12 V output on)
                 └─ D_OEN (BAT46W) ─ OUT_OFF ─ XIAO GPIO: drive low to switch the 12 V output off
```

- **Small parts:** Q_HOLD is a BSS84 (−50 V, ±20 V gate, −55 to 150 °C **[DS BSS84]**) with the same 12 V Zener clamp and a 1 MΩ / 470 kΩ gate divider (about 9 µA while holding **[calc]**); the two driver N-FETs are 2N7002 (60 V, threshold 1.0–2.5 V, −55 to 150 °C **[DS 2N7002]**); D_IGN is a BAT46W (100 V, 0.25 V at 0.1 mA, −55 to 125 °C **[DS BAT46W]**). 100 V on D_IGN covers a reversed car input with `EN_SRC` held at `SYS`.
- **Thresholds:** EN rising 1.231 V, 100 mV hysteresis **[DS LMR33630 EC table, VEN-H / VEN-HYS]**. With 887 kΩ / 102 kΩ: on above 11.94 V, off below 10.97 V at `EN_SRC` **[calc]**. On the ignition path D_IGN adds up to 0.25 V at the divider's 12 µA, so the board starts at about 12.2 V on the car feed **[calc]**.
- **Ignition on:** `EN_SRC` is fed from `VIN_CAR`, the 5 V rail starts, the XIAO boots and drives `HOLD` high, which connects `EN_SRC` to `SYS` as well.
- **Ignition off, hold-up:** `EN_SRC` stays on `SYS` (the battery) through Q_HOLD. The XIAO sees `VCAR_SENSE` fall and starts its timer.
- **Timer expires:** the hold-up time is an ESPHome setting, adjustable from Home Assistant and stored in flash (default 30 min, minimum 1 min). When it expires the XIAO releases `HOLD`. A setting of 0 disables the timer: `HOLD` stays high and the board runs until the hardware low-voltage cutoff. `EN_SRC` falls to zero, the 5 V rail and the XIAO switch off, and nothing can turn back on until the car feed returns.
- **Low-voltage cutoff (hardware):** during hold-up the same divider is watching the battery. Below 10.97 V the 5 V rail switches off, the XIAO loses power, `HOLD` drops and the board latches off until the ignition returns. This needs no firmware.
- **12 V output follows the 5 V rail:** PG is an open-drain flag, high when the output is in regulation and forced low when EN is low **[DS LMR33630 pin table, §8.3.1]**; pull-up 100 kΩ to VOUT as the datasheet suggests **[DS §8.3.1]**. D_OEN keeps the 5 V pull-up off the XIAO's 3.3 V pin; with the pin low `OUT_EN` sits at about 0.3–0.45 V, under the 2N7002's 1.0 V minimum threshold **[DS 2N7002, BAT46W]**. So the 12 V output has the same cutoff as the 5 V rail and comes on about 4 ms after it **[DS §8.3.1]**. Side effect: an overload that pulls the 5 V rail out of regulation also switches the 12 V output off.
- **Soft cutoff (firmware):** 10.97 V is close to empty for a lightly loaded AGM, and a discharged lead-acid battery freezes at roughly −10 °C while a full one survives below −40 °C (published freeze-point figures disagree in detail; take the battery maker's table where there is one) **[TBC]**. So the firmware releases `HOLD` earlier, at a battery voltage that rises as `TEMP_DQ` falls. Starting values to confirm on the bench with the real battery **[TBC]**: 11.9 V above 0 °C, 12.2 V from 0 to −20 °C, 12.4 V below −20 °C, measured under load and filtered over a few seconds. The hardware cutoff stays as the backstop when the firmware is missing or wrong.
- **XIAO faults:** stuck with `HOLD` high, the outputs run until the hardware cutoff. Stuck low, removed or not fitted, the outputs follow the ignition.
- **The latch needs the XIAO to lose power.** The low-voltage latch works because the XIAO dies with the 5 V rail and `HOLD` drops. If the XIAO is powered from anywhere else (a USB-C cable on the bench, a LiPo on its BAT pads), it keeps `HOLD` high: at 10.97 V the 5 V rail stops, the unloaded battery recovers above 11.94 V and the board restarts, cycling the battery down. So: no LiPo on the XIAO (owner's decision 2026-11-14; it would also be charged below 0 °C by the XIAO's charger, which has no temperature cutoff, and the BAT pads are not reachable through the socket), and unplug USB-C before testing the cutoff on a battery.
- **"Last gasp" report (firmware):** before releasing `HOLD` at the soft cutoff or timer expiry, the XIAO publishes battery voltage, temperature, energy used since ignition-off and the reason for shutdown. This gives the shutdown telemetry without a backup battery.
- **JP_HOLD** (open by default): closed, it replaces the XIAO's hold, so a board without a controller stays on until the low-voltage cutoff and restarts when the battery recovers above 11.94 V.

## Standby drain (everything off, ignition off) **[calc]**
| Item | Current |
|---|---|
| U_OR2, powered from `VBAT` | 80 µA typ, 130 µA max **[DS LM74700-Q1 EC table, I(Q)]** |
| LMR33630 in shutdown | 5 µA typ, 10 µA max **[DS ISD]** |
| `VBAT_SENSE` divider | 21 µA |
| Two INA226 VBUS inputs, 830 kΩ each **[DS INA226 EC table]** | about 30 µA, assuming the input divider stays connected with the supply off **[TBC, bench]** |
| Total | about 0.14 mA, or 0.1 Ah per month |

A 7 Ah AGM loses more than that to self-discharge. For long storage, pull F_BAT.

## Sensing (XIAO)
- `VCAR_SENSE`: divider on `VIN_CAR`, 560 kΩ / 100 kΩ with 100 nF. Ignition detect and car-feed voltage. With the ignition off and `EN_SRC` held at `SYS`, D_IGN's reverse leakage in a hot trunk flows into `VIN_CAR`; if the car side is open (no other load on the ignition circuit), the divider can float a few volts. A firmware ignition threshold of about 9 V ignores it **[TBC, bench at 85 °C]**. No clamp diode: a Schottky clamp's leakage at 85 °C would spoil the reading, and the 560 kΩ limits pin current to about 45 µA at the 29 V clamp level and −25 µA with the input reversed **[calc]**. The ESP32-C6's tolerance for that injected current is **[TBC]**.
- `VBAT_SENSE`: divider on `VBAT`, 560 kΩ / 100 kΩ with 100 nF → 3.03 V at 20 V, 2.27 V at 15 V **[calc]**. Accuracy is that of the ESP32 ADC; calibrate in ESPHome.
- **Current monitors:** two INA226 on I2C, powered from `3V3`, so they are off when the board is off.
  - U_MON_IN (0x40) across R_SNS_IN, between `SYS_IN` and `SYS`; VBUS on `SYS`. Power in from the car feed.
  - U_MON_OUT (0x41) across R_SNS_OUT, between `SYS` and `LOAD`; VBUS on `LOAD`. Power out to the 12 V output and the 5 V rail together, including the XIAO's own draw.
  - Battery current is in minus out: positive while charging, and equal to the output current with the ignition off.
  - Both shunts 5 mΩ 1 %, 2512. Input peak 7 A → 35 mV, 0.25 W; output peak 6 A → 30 mV, 0.18 W **[calc]**. The INA226 shunt range is ±81.92 mV **[DS INA226 EC table]**, so the resolution is 2.5 µV, or 0.5 mA **[calc]**.
  - Both shunts sit behind U_OR1, so reverse polarity on J_CAR never reaches the INA226 inputs (−0.3 V minimum, 40 V absolute maximum, 36 V operating **[DS INA226 §5.1, §5.3]**). The TVS clamp limit of 36 V covers them.
  - Addresses: U_MON_IN A1 = GND, A0 = GND → 0x40; U_MON_OUT A1 = GND, A0 = VS → 0x41 **[DS INA226 address table]**. Pull-ups 4.7 kΩ on `SDA` / `SCL` to `3V3`.
- `TEMP_DQ`: DS18B20 probe on the battery through J_TEMP, 4.7 kΩ pull-up to `3V3`. Reporting only; nothing in hardware acts on it. −55 to 125 °C, 3.0–5.5 V supply, ±0.5 °C from −10 to 85 °C and ±2 °C over the full range **[DS DS18B20]**. ESPHome component **[TBC]**.

## Status LEDs
- Two plain 0603 LEDs, each driven high by its own XIAO pin through a 1 kΩ resistor to the anode, cathode to `GND`: D_GRN (green) on `LED_G` (D10, GPIO18) and D_RED (red) on `LED_R` (D9, GPIO20). About 1.1–1.3 mA each at a 2.0–2.2 V forward drop **[calc]**: dim but visible through a light pipe or a hole in the case. Exact LCSC parts and their −40 °C rating are in the LCSC part table in `netlist.md`.
- They replace the SK6812 RGB LED, its 1N4148W supply diode, C_LED and R_LED (owner's decision 2026-11-14). That removes three distinct parts and the open question of the SK6812's 3.4 V data threshold at −40 °C.
- Both pins are off when the module is removed or the board is off. Any low-battery warning comes from a firmware threshold above the hardware cutoff, because at the cutoff the XIAO loses power with everything else.
- Behaviour is firmware only; nothing depends on it.

## ESP32 socket (Seeed XIAO ESP32-C6, 2×7, 2.54 mm)
Pin-to-GPIO map and the −40 to 85 °C rating are from Seeed's getting-started page (read 2026-11-13). The Flux symbol in use is "Seeed Studio XIAO ESP32C6 SMD No-DrillHole", a surface-mount footprint; the socket footprint and row spacing are **[TBC]** before layout.
| XIAO pin | Use |
|---|---|
| D0, GPIO0 (ADC) | `VCAR_SENSE` |
| D1, GPIO1 (ADC) | `VBAT_SENSE` |
| D2, GPIO2 | `TEMP_DQ` (1-Wire) |
| D4, GPIO22 / D5, GPIO23 | `SDA` / `SCL` (INA226 ×2) |
| D3, GPIO21 | `OUT_OFF`: drive low to switch the 12 V output off (through D_OEN); high or floating = on |
| D10, GPIO18 | `LED_G` (green status LED) |
| D9, GPIO20 | `LED_R` (red status LED). Not a strapping pin |
| D8, GPIO19 | `HOLD`: high keeps the board on after ignition-off. Not a strapping pin: the ESP32-C6 strapping pins are GPIO4, GPIO5, GPIO8, GPIO9 and GPIO15 (Espressif ESP32-C6-DevKitC-1 user guide, read 2026-11-14). Not the UART pins (D6/D7) or the antenna-switch pins (GPIO3, GPIO14). Whether it glitches high during boot is still a bench check **[TBC]**; R_HOLD holds it low until the firmware drives it |
| 5V | from the `5V` rail through D_5V, a B5819W (40 V, 1 A, SOD-123, −55 to 125 °C from the LCSC listing; datasheet extract to add **[TBC]**), so the module's USB cannot backfeed the rail. It replaced the B140B (SMB) in v3.1 because it carries no feeder fee |
| 3V3 | INA226 supply, I2C and `TEMP_DQ` pull-ups |

Every ESP32-driven line leaves the board in its defined state with the module removed: `HOLD` is pulled low by R_HOLD, and `OUT_EN` is pulled high by R_PG because D_OEN isolates the unconnected `OUT_OFF` pin. D6 and D7 (UART) are unused, so serial logging stays available.

## Connectors and fuses
| Ref | Part | Notes |
|---|---|---|
| J_CAR | 2-pin screw terminal, ≥ 10 A: Phoenix Contact MKDS 1,5/2 (1715022), 5.0 mm, 15 A, −40 to 105 °C (family rating, LCSC listing). Captured as XY301V-A-5.0-2P, which has no temperature rating; change the footprint at layout | fused at the car end as well |
| J_SLA | same part as J_CAR | battery; F_BAT 10 A beside it |
| J_12V | Same Sky PJ-063AH, 24 V, 8 A, 2.0 mm centre pin (for 5.5 × 2.1 mm plugs) | rated −25 to 85 °C **[DS PJ-063AH]**. Accepted as the one exception to the −40 °C rule (owner's decision, 2026-11-13). Pin size must match the plugs in use |
| J_USBA | USB-A receptacle, D+ tied to D−. Würth 61400416021 (no shell pin on the symbol) | −40 to 105 °C (LCSC listing) |
| J_TEMP | 3-way PCB screw terminal: GND, DQ, 3V3. Phoenix Contact MKDS 1,5/3 (1715035), −40 to 105 °C (LCSC listing) | DS18B20 probe on the battery. Not JST-XH (−25 °C) or the KF301 (−30 °C). Captured as a 1×3 jumper symbol as a placeholder; replace before layout |
| F_IN / F_BAT / F_OUT | 10 A / 10 A / 7.5 A blade fuses | Keystone 3557-2 holders, hand-soldered. Captured as generic fuse symbols; the holder footprint is set at layout |
| F_CHG | 1.6 A time-lag, Schurter UMT 250 | SMD. Captured as a generic fuse symbol |

## Capture status (2026-11-14: KiCad)
The schematic and board moved to KiCad 10 on 2026-11-14 (`kicad/`, see `kicad/README.md`). The schematic is generated from `netlist.md`: ERC clean, every pin matches the table, and every net matches the Flux capture except one Flux error (Q_OR2's gate not wired). The Flux-specific items below (symbols, LCSC numbers on Flux parts, the 90 Ω tag) no longer apply; in KiCad the BSS84 symbol is G 1, S 2, D 3 as in the datasheet, L1 carries C2041807, J_CAR/J_SLA/J_TEMP use the Phoenix MKDS 1,5 footprints, and R_CHG and F_CHG have their footprints.

### Flux capture (history, 2026-11-13)
The schematic is in Flux: 80 parts, every net checked against `netlist.md` with the free reads. The owner wired it by hand; the Flux agent only placed the parts.

Differences between the captured schematic and this document, to settle before layout or ordering:
0. **v3.1 changes (2026-11-14): done and verified.** 77 parts, 41 nets. Left over: Flux's inherited 90 Ω controlled-impedance tag on `USB_D` and `5V`, to clear before routing.
1. **Packages:** done 2026-11-14 from the LCSC part table (0603 / 0805 / 1206 / 2512). Only R_CHG is left: it is still a generic 0603 symbol and needs the axial AC10 footprint.
2. ~~J_TEMP~~ done 2026-11-14: KF301-5.0-3P footprint; order the Phoenix MKDS 1,5/3 (1715035, −40 °C) for it.
3. **Q_HOLD:** the library symbol BSS84LT1G numbers drain as pin 2 and source as pin 3, but the onsemi datasheet (SOT-23 case 318, style 21) gives gate 1, source 2, drain 3 **[DS onsemi BSS84LT1/D, read 2026-11-14]**. As wired by name, the body diode would hold `EN_SRC` at `SYS` permanently and break the timer and the latch-off. **To fix before layout:** wire symbol pin 2 (named D) to `SYS` and pin 3 (named S) to `EN_SRC`. The 2N7002s (G 1, S 2, D 3) and Q_OUT (G 1, D 2, S 3) match their packages.
4. ~~D_TVS~~ done 2026-11-14: Diodes SMCJ18CAQ-13-F.
5. **L1** shows 8.2 µH and SRP6540-8R2M but carries the 4.7 µH part's LCSC number (C1329351); the 8.2 µH part is C2041807.
6. ~~F_BAT~~ done 2026-11-14: 10 A.
6a. ~~D_5V~~ done 2026-11-14: B5819W (SOD-123, LCSC C64885).
6b. **J_CAR, J_SLA** are XY301V symbols; v3.1 uses the Phoenix MKDS 1,5/2 (same 5.0 mm pitch; check the footprint).
7. **Fuses, J_XIAO:** done 2026-11-14: F_IN/F_BAT/F_OUT are Keystone 3557-2 parts (confirm at layout that pads 1 and 3 share a clip) and J_XIAO is the through-hole XIAO ESP32C6 part. Still open: F_CHG (Schurter UMT 250) and R_CHG (axial, 52 mm) footprints, and the stackup, which is set to 4-layer instead of 2-layer 1 oz.
8. **Test points** (`VIN_CAR`, `SYS`, `LOAD`, `VBAT`, `5V`, `3V3`, `EN_5V`, `GND`) are not placed.

## Open items
1. Price checkpoint for the batch of 5 (`plan.md`), with the LCSC part table in `netlist.md`.
2. The capture differences above.
3. J_12V: confirm the plugs in use are 5.5 × 2.1 mm.
4. Temperature rating of the CJ 2N7002 (blank in its LCSC listing), and the effective capacitance of the 1206 X5R capacitors on the buck (LCSC part table in `netlist.md`).
5. GPIO19 glitch at boot (bench); the ESP32-C6's tolerance for the sense dividers' injected current.
6. ESPHome: DS18B20, INA226 ×2, two LEDs, the hold-up timer, and the soft cutoff with its cold steps.
7. Soft-cutoff voltages: confirm against the battery maker's state-of-charge and freeze-point data.
8. Bench: the ignition-off handover with a 5 A load, F_CHG and R_CHG with a deeply discharged battery, the 12 V output's turn-on into a capacitive load, standby drain, `VCAR_SENSE` with the ignition off at 85 °C (D_IGN leakage), and the feed voltage of each car the unit goes into.
