# Power board — architecture

Status key: **[DS]** read in the datasheet extract in `datasheets/`; **[calc]** my arithmetic from DS values; **[TBC]** to confirm before capture.

## Block diagram

```
J_CAR ─ F1 ─ TVS ─ ideal diode (LM74700-Q1) ─┐
                                             ├─ VIN ─ ACFETs ─┬─ SYS ─┬─ U_12V TPS552882 ─ INA226 ─ F_OUT ─ J_12V barrel
J_USBC_IN ─ TPS25730 (20 V) ─ ideal diode ───┘                │       └─ U_5V LMR33630 ─ INA226 ─ TPS2514A ─ J_USBA
                                              buck-boost stage (4 FETs, L)        └─ D ─ XIAO 5V pin
                                                              │
                                                    RBAT_SNS ─ BATFETs ─ VBAT
   Lithium build:  VBAT = PACK+ ; PACK− ─ CHG/DSG FETs ─ RSNS ─ B− ; BQ77915 on cell taps
   Lead-acid build: VBAT = SLA+ via fuse ; SLA− = GND ; protector section DNP
```

## Net names
`VIN_CAR`, `VIN_PD`, `VIN` (OR'ed, charger VAC), `SYS`, `VBAT`, `B-` (lithium cell-stack negative), `GND` (= PACK−), `C1` `C2` `C3` (cell taps), `B+`, `12V_OUT`, `5V`, `3V3` (from the XIAO), `SDA`, `SCL`, `NTC_BAT`.

Lithium rule: `B-` and `GND` are different nets, joined only through the sense resistor and protection FETs. `B-` connects only to the cell-stack negative (J_PACK, J_BAL pin 1), the sense resistor, and the BQ77915's own VSS-referenced pins, filters and thermistor. No load, charger, converter, monitor or connector return may use `B-`.

## Build variants

| Item | Lithium | Lead-acid |
|---|---|---|
| U_CHG | BQ25750 | BQ25751 (pin-identical, 36-VQFN) **[DS: pin tables match]** |
| FB divider, RTOP 249 kΩ **[DS §9.2 uses 249 kΩ]** | RBOT 24.9 kΩ + 499 Ω → 16.59 V (4.15 V/cell, under the protector's 4.20 V trip with tolerance) **[calc]** | RBOT 32.4 kΩ → float 13.34 V, absorb 109.1 % = 14.55 V at 25 °C **[DS Table 7-3, calc]** |
| RICHG (KICHG = 50 A·kΩ, 5 mΩ sense) **[DS]** | 33.2 kΩ → 1.5 A | 49.9 kΩ → 1.0 A (raise for batteries ≥ 7 Ah) |
| Temperature | Charger TS: JEITA window with 103AT to `GND` (J_NTC). Protector TS: a second 103AT to `B-` (J_NTC_BMS) **[DS BQ77915 Table 6-1 note 1: thermistor from TS to VSS]**; the two cannot share one thermistor because `B-` and `GND` are different nets | TS: 103AT on the battery; −3 mV/°C/cell compensation; charge suspended below T1 (0 °C with the standard network) **[DS §7.3.4.5.1, EC table]** |
| Protector section (BQ77915, 2 FETs, shunt, cell filters) | fitted | DNP; 0 Ω link `B-`→`GND` |
| Battery connector | XT30 + JST-XH-5 + 2× JST-XH-2 (charger NTC, protector NTC) | fused screw terminal or XT60 + JST-XH-2 (NTC) |

**[TBC]** BQ25751 cold cutoff for the car: T1 is a ratio of REGN (73.25 %), so the TS divider can move it below 0 °C; check the effect on compensation accuracy, or accept "no charge below 0 °C until the trunk warms". Decide in block 3.
**[TBC]** Whether temperature compensation is on by default with no I2C host (Table 7-3 lists it under default settings; confirm the register reset value).

## Input window (both builds) **[calc from DS §9.2.1.2.1: VREF_ACUV 1.1 V, VREF_ACOV 1.2 V]**
RAC1 1 MΩ, RAC2 52.3 kΩ, RAC3 53.6 kΩ →
- input disconnect (falling) 11.5 V, charge throttles to hold input ≥ 12.5 V, over-voltage cutoff 24.8 V.
- Effect: charges only from a running alternator (≥ 12.5 V) or USB-C 20 V; cranking dips hand over to the battery.

Input current limit, one value for both sources and both builds: RAC_SNS 5 mΩ, RILIM 6.65 kΩ → 3.0 A. KILIM = 50 A·kΩ is defined for a 2 mΩ sense resistor and scales by 2/RAC_SNS, so 50 × 2/5 / 6.65 = 3.01 A **[DS BQ25750 §9.2.1.2.7, calc]**. 5 mΩ is chosen over 2 mΩ for accuracy at this current (15 mV sense at 3 A); it dissipates 0.125 W at 5 A **[calc]**. Fits a 65 W USB-C source at 20 V.

What the limit does **[DS BQ25750 §8.3.5.1, BQ25751 §7.3.5.1]**:
- It throttles charging only. When input current reaches 3 A the charger reduces charge current, down to zero. It cannot limit the load, because `SYS` is connected straight to the input through the ACFETs.
- A load above the limit is not interrupted; the input simply carries more than 3 A with charging at zero.
- If the source sags below the 11.5 V disconnect, the charger stops and the battery powers `SYS`. Input and battery never supply the load together.
- Effect on the car feed (13.5 V, 40 W at the limit) **[calc]**: lithium charges at full rate up to about 12 W of load and not at all near 36 W; lead-acid charges at full rate up to about 22 W of load. carNet (5 W) is unaffected.
- Effect on USB-C (20 V, 60 W at the limit) **[calc]**: about 20 W is left for charging at a 36 W load. A 5 A output peak needs about 3.3 A, just over a 65 W source's 3.25 A; if the source trips, the battery carries the peak.
- **[TBC, bench]** how cleanly the input-to-battery handover behaves under a 5 A peak.

## Rails
- **12 V:** 3 A continuous, 5 A peak for several seconds. Thermal design is for 3 A; current limit, fuse and jack are sized for the 5 A peak. TPS552882, VREF 1.2 V **[DS]**; FB 180 kΩ / 20 kΩ → 12.0 V **[calc]**. EN/UVLO threshold 1.15 V with 5 µA hysteresis current **[DS]**: set falling ≈ 11.0 V, rising ≈ 12.0 V on `SYS` (lead-acid low-voltage cutoff). Buck-side FETs are external (DR1H/DR1L) **[DS]**. Soft-start fixed 4 ms **[DS]**.
- **5 V:** LMR33630 from `SYS`. Precision enable: rising 1.231 V, 100 mV hysteresis **[DS LMR33630 EC table, VEN-H / VEN-HYS]**. EN divider from `SYS` 887 kΩ / 102 kΩ → off below 10.97 V falling, on above 11.94 V rising **[calc]**, matching the 12 V rail so the low-voltage cutoff covers both rails. The XIAO is fed from `5V` and powers down with it. Both builds; in the lithium build the protector's 2.9 V/cell trip (11.6 V) normally acts first.
- ESP32 can pull the 12 V converter's enable low (router off after ignition-off).

## I2C map
| Device | Address |
|---|---|
| BQ25750 / BQ25751 | 0x6B **[DS family table]** |
| INA226 (12 V out) | 0x40 |
| INA226 (5 V out) | 0x41 |
| SSD1306 OLED | 0x3C |

Pull-ups 4.7 kΩ to `3V3`.

## ESP32 socket (Seeed XIAO ESP32-C6, 2×7, 2.54 mm) — provisional, **[TBC]** against Seeed's pinout and footprint
| XIAO pin | Use |
|---|---|
| D4 / D5 | SDA / SCL |
| D0 (ADC) | `VCAR_SENSE`: `VIN_CAR` via divider (ignition). Total input voltage is read from the charger ADC over I2C |
| D1 | charger INT |
| D2 | charger PG (any input present, car or USB-C) |
| D3 | 12 V output enable (open-drain, default enabled) |
| D6 | user button |
| D7 | charger CE override (default: charging allowed by hardware) |
| 5V | from `5V` rail through a Schottky diode (no backfeed from the module's USB) |
| 3V3 | powers OLED, INA226 logic, I2C pull-ups |

## Connectors
| Ref | Part | Notes |
|---|---|---|
| J_CAR | 2-pin, ≥ 10 A | fused at the car end as well |
| J_USBC_IN | USB-C receptacle | sink only |
| J_12V | Same Sky PJ-063AH, 8 A | **[TBC]** pin diameter vs the plugs in use (2.0 / 2.1 / 2.5 mm) |
| J_USBA | USB-A receptacle | |
| J_PACK | XT30 (PACK+/B−) | lithium build |
| J_BAL | JST-XH 5-pin: B−, C1, C2, C3, B+ | lithium build; taps only, never pack current |
| J_NTC | JST-XH 2-pin | charger 103AT on the cells / battery, returns to `GND`; both builds |
| J_NTC_BMS | JST-XH 2-pin | protector 103AT on the cells, returns to `B-`; lithium build only |
| J_SLA | fused terminal | lead-acid build |
| J_OLED | 4-pin header: GND, 3V3, SCL, SDA | check module pin order before ordering |

## Cell board (separate Flux project)
Four PCB-mount 18650 holders in series, pack fuse (10 A) in B+, a 1 kΩ-class series element or fuse in each tap **[TBC: effect on the 33 Ω balance filter]**, two 103AT NTCs against the cells (one for the charger, one for the protector, electrically separate), XT30 + JST-XH-5 + 2× JST-XH-2. Holder current rating **[TBC]**.
