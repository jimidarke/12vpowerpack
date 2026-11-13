# Power board — architecture (v3)

Status key: **[DS]** read in the datasheet extract in `datasheets/`; **[calc]** my arithmetic from DS values; **[TBC]** to confirm before capture.

v3 is the vehicle-only design: one build, 12 V AGM, no charger IC, no USB-C PD input, no 12 V converter, no display. The v2 architecture is in git at tag `v0.2.1`.

## Block diagram

```
J_CAR ─ F_IN ─ TVS ─ VIN_CAR ─ U_OR1 (LM74700-Q1 + Q_OR1) ─ SYS_IN ─ R_SNS_IN ─ SYS

SYS ─┬─ R_SNS_OUT ─ LOAD ─┬─ Q_OUT (P-FET) ─ F_OUT ─ J_12V barrel
     │                    └─ U_5V LMR33630 ─ 5V ─┬─ TPS2514A ─ J_USBA
     │                                           └─ D ─ XIAO 5V pin
     ├─ F_CHG ─ R_CHG ──────────────┐   (charge)
     └─ U_OR2 (LM74700-Q1 + Q_OR2) ─┤   (discharge: anode VBAT, cathode SYS)
                                  VBAT ─ F_BAT ─ J_SLA
```

- Ignition on: `SYS` follows the car feed. The loads run from the car; the battery charges through R_CHG.
- Ignition off: U_OR1 blocks, `SYS` falls to the battery voltage and U_OR2 conducts. The loads run from the battery.
- The car feed and the battery can share a load if the feed sags under it. Nothing needs them kept apart.

## Net names
`VIN_CAR` (after F_IN and the TVS, car side of U_OR1), `SYS_IN` (U_OR1 output, before the input shunt), `SYS`, `LOAD` (after the output shunt), `VBAT`, `12V_OUT`, `5V`, `3V3` (from the XIAO), `EN_SRC`, `EN_5V`, `OUT_EN`, `HOLD`, `VCAR_SENSE`, `VBAT_SENSE`, `TEMP_DQ`, `SDA`, `SCL`, `GND`.

## Input protection
- F_IN 10 A, ≥ 32 V DC. Car-feed current is about 5 A continuous and 7 A at the output peak (requirements, sizing figures) **[calc]**.
- TVS on `VIN_CAR`: stand-off ≥ 16 V, clamp ≤ 36 V at the surge current. 36 V is the LMR33630's operating maximum and 38 V its absolute maximum **[DS LMR33630 §7.1, §7.3]**. Part **[TBC]**.
- U_OR1, LM74700-Q1 with an external N-FET: blocks reverse polarity on J_CAR and stops the battery feeding the car. 3.2–65 V input, −65 V reverse rating, 20 mV regulated forward drop **[DS LM74700-Q1 features, §6.1]**. Q_OR1 ≥ 40 V, ≤ 10 mΩ **[TBC part]**.

## Battery path
- **Discharge:** U_OR2, a second LM74700-Q1 with Q_OR2, anode on `VBAT`, cathode on `SYS`. Carries up to 4 A continuous, 6 A peak **[calc]**. An ideal diode instead of a Schottky so the 12 V output does not lose 0.4 V and nothing runs hot. Q_OR2 as Q_OR1.
- **Charge:** F_CHG then R_CHG from `SYS` to `VBAT`. R_CHG 3.3 Ω **[calc]**:

| Battery voltage (feed at 14.4 V) | Charge current | Power in R_CHG |
|---|---|---|
| 12.6 V (after a normal stop) | 0.55 A | 1.0 W |
| 11.0 V (at the low-voltage cutoff) | 1.0 A | 3.5 W |
| 10.5 V (one shorted cell) | 1.2 A | 4.6 W |

- F_CHG 1.5 A slow-blow bounds the fault cases **[calc]**: it opens when the battery is below about 9.4 V (current above 1.5 A), so R_CHG never sees more than about 7.4 W continuously. R_CHG rated ≥ 7 W; part and mounting **[TBC]**. A reversed battery puts about 26 V across R_CHG and blows F_CHG.
- F_BAT 10 A at the battery connector.
- Charge current tapers to zero as the battery reaches the feed voltage; there is no absorb/float staging and no temperature compensation (accepted in requirements v3).
- Recharge is slow: replacing a 3 Ah discharge takes several hours of driving. Lower R_CHG (and raise F_CHG and the resistor rating to match) if a unit is used that way; 3.3 Ω suits 2–12 Ah batteries on the carNet duty.

## Rails
- **12 V output:** `LOAD` through Q_OUT (P-channel FET, high side) and F_OUT 7.5 A to J_12V. Unregulated, about 10.9–14.8 V. Q_OUT ≥ 40 V, ≤ 20 mΩ, gate-source clamp and a slowed turn-on for capacitive loads; part **[TBC]**. Overcurrent protection is F_OUT alone; there is no electronic current limit.
- **5 V:** LMR33630 from `LOAD`, 3.8–36 V in **[DS]**. Feeds the TPS2514A USB-A port and the XIAO.

## Power control
One threshold, set at the LMR33630's precision enable, controls everything. No comparator or logic IC.

```
VIN_CAR ─ D_IGN (Schottky) ─┐
                            ├─ EN_SRC ─ 887 kΩ ─ EN_5V (LMR33630 EN) ─ 102 kΩ ─ GND
SYS ─ Q_HOLD (P-FET) ───────┘
        gate ← N-FET ← HOLD (XIAO GPIO, 100 kΩ pull-down)     JP_HOLD solder jumper across Q_HOLD

LMR33630 PG ─ OUT_EN ─ 100 kΩ pull-up to 5V ─ N-FET gate ─ pulls Q_OUT gate low (12 V output on)
                 └─ XIAO GPIO, open-drain: pull low to switch the 12 V output off
```

- **Thresholds:** EN rising 1.231 V, 100 mV hysteresis **[DS LMR33630 EC table, VEN-H / VEN-HYS]**. With 887 kΩ / 102 kΩ: on above 11.94 V, off below 10.97 V at `EN_SRC` **[calc]**. On the ignition path D_IGN adds about 0.2 V, so the board starts at about 12.1–12.2 V on the car feed **[calc]**.
- **Ignition on:** `EN_SRC` is fed from `VIN_CAR`, the 5 V rail starts, the XIAO boots and drives `HOLD` high, which connects `EN_SRC` to `SYS` as well.
- **Ignition off, hold-up:** `EN_SRC` stays on `SYS` (the battery) through Q_HOLD. The XIAO sees `VCAR_SENSE` fall and starts its timer.
- **Timer expires:** the hold-up time is an ESPHome setting, adjustable from Home Assistant and stored in flash (default 30 min, minimum 1 min). When it expires the XIAO releases `HOLD`. A setting of 0 disables the timer: `HOLD` stays high and the board runs until the hardware low-voltage cutoff. `EN_SRC` falls to zero, the 5 V rail and the XIAO switch off, and nothing can turn back on until the car feed returns.
- **Low-voltage cutoff (hardware):** during hold-up the same divider is watching the battery. Below 10.97 V the 5 V rail switches off, the XIAO loses power, `HOLD` drops and the board latches off until the ignition returns. This needs no firmware.
- **12 V output follows the 5 V rail:** PG is an open-drain flag, high when the output is in regulation and forced low when EN is low **[DS LMR33630 pin table, §8.3.1]**; pull-up 100 kΩ to VOUT as the datasheet suggests **[DS §8.3.1]**. So the 12 V output has the same cutoff as the 5 V rail and comes on about 4 ms after it **[DS §8.3.1]**. Side effect: an overload that pulls the 5 V rail out of regulation also switches the 12 V output off.
- **XIAO faults:** stuck with `HOLD` high, the outputs run until the hardware cutoff. Stuck low, removed or not fitted, the outputs follow the ignition.
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
- `VCAR_SENSE`: divider on `VIN_CAR`, top resistor ≥ 100 kΩ plus a clamp so reverse polarity or a transient cannot harm the pin. Ignition detect and car-feed voltage.
- `VBAT_SENSE`: divider on `VBAT`, 560 kΩ / 100 kΩ with a clamp → 3.03 V at 20 V, 2.27 V at 15 V **[calc]**. Accuracy is that of the ESP32 ADC; calibrate in ESPHome.
- **Current monitors:** two INA226 on I2C, powered from `3V3`, so they are off when the board is off.
  - U_MON_IN (0x40) across R_SNS_IN, between `SYS_IN` and `SYS`; VBUS on `SYS`. Power in from the car feed.
  - U_MON_OUT (0x41) across R_SNS_OUT, between `SYS` and `LOAD`; VBUS on `LOAD`. Power out to the 12 V output and the 5 V rail together, including the XIAO's own draw.
  - Battery current is in minus out: positive while charging, and equal to the output current with the ignition off.
  - Both shunts 5 mΩ 1 %, 2512. Input peak 7 A → 35 mV, 0.25 W; output peak 6 A → 30 mV, 0.18 W **[calc]**. The INA226 shunt range is ±81.92 mV **[DS INA226 EC table]**, so the resolution is 2.5 µV, or 0.5 mA **[calc]**.
  - Both shunts sit behind U_OR1, so reverse polarity on J_CAR never reaches the INA226 inputs (−0.3 V minimum, 40 V absolute maximum, 36 V operating **[DS INA226 §5.1, §5.3]**). The TVS clamp limit of 36 V covers them.
  - Address pins and pull-ups: 4.7 kΩ on `SDA` / `SCL` to `3V3`; address strapping **[TBC from the datasheet's address table]**.
- `TEMP_DQ`: DS18B20 probe on the battery through J_TEMP, 4.7 kΩ pull-up to `3V3`. Reporting only; nothing in hardware acts on it. Temperature range and ESPHome support **[TBC]**.

## ESP32 socket (Seeed XIAO ESP32-C6, 2×7, 2.54 mm) — provisional, **[TBC]** against Seeed's pinout and footprint
| XIAO pin | Use |
|---|---|
| D0 (ADC) | `VCAR_SENSE` |
| D1 (ADC) | `VBAT_SENSE` |
| D2 | `TEMP_DQ` (1-Wire) |
| D4 / D5 | `SDA` / `SCL` (INA226 ×2) |
| D3 | `OUT_EN`, open-drain: low switches the 12 V output off; released = on |
| D8 | `HOLD`: high keeps the board on after ignition-off. Must not be a strapping pin or one that pulses at boot **[TBC]** |
| 5V | from the `5V` rail through a Schottky diode (no backfeed from the module's USB) |
| 3V3 | INA226 supply, I2C and `TEMP_DQ` pull-ups |

Every ESP32-driven line has a pull resistor that leaves the board in its defined state with the module removed: `HOLD` low, `OUT_EN` high.

## Connectors and fuses
| Ref | Part | Notes |
|---|---|---|
| J_CAR | 2-pin, ≥ 10 A | fused at the car end as well |
| J_SLA | 2-pin, ≥ 10 A (screw terminal or XT60) | battery; F_BAT 10 A beside it |
| J_12V | Same Sky PJ-063AH, 8 A | **[TBC]** pin diameter vs the plugs in use (2.0 / 2.1 / 2.5 mm) |
| J_USBA | USB-A receptacle | |
| J_TEMP | JST-XH 3-pin: GND, DQ, 3V3 | DS18B20 probe on the battery |
| F_IN / F_BAT / F_OUT / F_CHG | 10 A / 10 A / 7.5 A / 1.5 A slow | holder or SMD type **[TBC]**; all ≥ 32 V DC |

## Open items before capture
1. Parts for Q_OR1/Q_OR2, Q_OUT, Q_HOLD, the TVS, R_CHG and the fuses, each with a −40 to 85 °C rating and a datasheet extract in `datasheets/`.
2. XIAO ESP32-C6 pinout, strapping pins, row spacing and temperature rating from Seeed's documents.
3. LMR33630 output stage values (inductor, capacitors, feedback divider) from the datasheet's 5 V example.
4. DS18B20 probe: operating range at −40 °C and the ESPHome component.
5. Bench: the ignition-off handover with a 5 A load, F_CHG behaviour with a deeply discharged battery, and the 12 V output's turn-on into a capacitive load.
