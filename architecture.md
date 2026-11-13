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

Lithium rule: `B-` and `GND` are different nets, joined only through the sense resistor and protection FETs. Nothing else may connect to `B-`.

## Build variants

| Item | Lithium | Lead-acid |
|---|---|---|
| U_CHG | BQ25750 | BQ25751 (pin-identical, 36-VQFN) **[DS: pin tables match]** |
| FB divider, RTOP 249 kΩ **[DS §9.2 uses 249 kΩ]** | RBOT 24.9 kΩ + 499 Ω → 16.59 V (4.15 V/cell, under the protector's 4.20 V trip with tolerance) **[calc]** | RBOT 32.4 kΩ → float 13.34 V, absorb 109.1 % = 14.55 V at 25 °C **[DS Table 7-3, calc]** |
| RICHG (KICHG = 50 A·kΩ, 5 mΩ sense) **[DS]** | 33.2 kΩ → 1.5 A | 49.9 kΩ → 1.0 A (raise for batteries ≥ 7 Ah) |
| Temperature | TS: JEITA window with 103AT | TS: 103AT on the battery; −3 mV/°C/cell compensation; charge suspended below T1 (0 °C with the standard network) **[DS §7.3.4.5.1, EC table]** |
| Protector section (BQ77915, 2 FETs, shunt, cell filters) | fitted | DNP; 0 Ω link `B-`→`GND` |
| Battery connector | XT30 + JST-XH-5 + JST-XH-2 (NTC) | fused screw terminal or XT60 + JST-XH-2 (NTC) |

**[TBC]** BQ25751 cold cutoff for the car: T1 is a ratio of REGN (73.25 %), so the TS divider can move it below 0 °C; check the effect on compensation accuracy, or accept "no charge below 0 °C until the trunk warms". Decide in block 3.
**[TBC]** Whether temperature compensation is on by default with no I2C host (Table 7-3 lists it under default settings; confirm the register reset value).

## Input window (both builds) **[calc from DS §9.2.1.2.1: VREF_ACUV 1.1 V, VREF_ACOV 1.2 V]**
RAC1 1 MΩ, RAC2 52.3 kΩ, RAC3 53.6 kΩ →
- input disconnect (falling) 11.5 V, charge throttles to hold input ≥ 12.5 V, over-voltage cutoff 24.8 V.
- Effect: charges only from a running alternator (≥ 12.5 V) or USB-C 20 V; cranking dips hand over to the battery.

Input current limit: RILIM 16.5 kΩ → 3.0 A (KILIM = 50 A·kΩ) **[DS]**. Fits a 65 W USB-C source at 20 V. **[TBC]** sense-resistor value that KILIM assumes (2 mΩ in the EC table).

## Rails
- **12 V:** TPS552882, VREF 1.2 V **[DS]**; FB 180 kΩ / 20 kΩ → 12.0 V **[calc]**. EN/UVLO threshold 1.15 V with 5 µA hysteresis current **[DS]**: set falling ≈ 11.0 V, rising ≈ 12.0 V on `SYS` (lead-acid low-voltage cutoff). Buck-side FETs are external (DR1H/DR1L) **[DS]**. Soft-start fixed 4 ms **[DS]**.
- **5 V:** LMR33630 from `SYS`.
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
| D0 (ADC) | `VIN` sense via divider (ignition / input voltage) |
| D1 | charger INT |
| D2 | charger PG (input present) |
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
| J_NTC | JST-XH 2-pin | 103AT on the cells / battery |
| J_SLA | fused terminal | lead-acid build |
| J_OLED | 4-pin header: GND, 3V3, SCL, SDA | check module pin order before ordering |

## Cell board (separate Flux project)
Four PCB-mount 18650 holders in series, pack fuse (10 A) in B+, a 1 kΩ-class series element or fuse in each tap **[TBC: effect on the 33 Ω balance filter]**, 103AT NTC against the cells, XT30 + JST-XH-5 + JST-XH-2. Holder current rating **[TBC]**.
