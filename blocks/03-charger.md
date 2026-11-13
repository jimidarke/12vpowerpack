# Block 3 — charger and power path (BQ25750 / BQ25751)

**Goal:** capture the buck-boost charger with direct power path: `VIN` → `SYS` (loads) and `VBAT` (battery). One footprint, two build variants. Capture only.

## Parts
| Ref | Lithium build | Lead-acid build |
|---|---|---|
| U_CHG | TI BQ25750 | TI BQ25751 |
| Package | 36-pin VQFN (RRV) 6×5 mm, identical pinout | same |

Shared: 4 switching N-FETs + inductor, 2 input FETs (ACDRV), 2 battery FETs (BATDRV), RAC_SNS, RBAT_SNS 5 mΩ. All FETs ≥ 40 V (bus never exceeds 25 V in operation; TVS clamps transients) — choose from the datasheet's guidance scaled to 6 A.

## Verified datasheet facts — use these, do not re-research
- Pinout identical across BQ25750 and BQ25751 (pin tables compared): 1 SCL … 8 TS, 9 ICHG, 10 ILIM_HIZ, 11 FBG, 12 FB, 13 SRN, 14 SRP, 15 BATDRV, 16 BATSRC, 17 PGND, 18 SW2, 19 HIDRV2, 20 BTST2, 21 LODRV2, 22 PGND, 23 DRV_SUP, 24 REGN, 25 LODRV1, 26 BTST1, 27 HIDRV1, 28 SW1, 29 ACN, 30 ACP, 31 ACDRV, 32 SYS, 33 VAC, 34 ACUV, 35 ACOV, 36 FSW_SYNC. Read pins 2 and 7 from the datasheet.
- Standalone operation: FB pin sets voltage, ICHG pin sets charge current, ILIM_HIZ sets input current. I2C address 0x6B.
- FB reference 1.536 V; top resistor 249 kΩ; bottom resistor returns to **FBG**, not ground (BQ25750 §9.2.1.2.2).
- ICHG = 50 A·kΩ / RICHG with RBAT_SNS = 5 mΩ. ILIM = 50 A·kΩ / RILIM.
- Input window: ACUV reference 1.1 V (falling), ACOV 1.2 V (rising), divider from VAC with 1 MΩ top (§9.2.1.2.1). ACUV pin also regulates input voltage at 1.2 V.
- CE pin must be tied high or low, never floating. ICHG, ILIM_HIZ, FSW_SYNC must not float.
- BQ25751 defaults (Table 7-3): CC → absorb → float; FB sets the **float** voltage; absorb = 109.1 % of it; termination 10 % of ICHG; 5 h absorb timer; −3 mV/°C/cell compensation with a 103AT; T1 cold threshold 73.25 % of REGN (0 °C with the standard network), T5 hot 34.4 % (60 °C).

## Values
| Item | Lithium | Lead-acid |
|---|---|---|
| FB: RTOP 249 kΩ 0.1 % | RBOT 24.9 kΩ + 499 Ω → 16.59 V | RBOT 32.4 kΩ → 13.34 V float / 14.55 V absorb |
| RICHG | 33.2 kΩ → 1.5 A | 49.9 kΩ → 1.0 A |
| RILIM | 16.5 kΩ → 3.0 A | same |
| Input window | RAC1 1 MΩ, RAC2 52.3 kΩ, RAC3 53.6 kΩ → off below 11.5 V, throttle at 12.5 V, off above 24.8 V | same |
| Switching frequency | 350–500 kHz per Table 8-2 | same |
| TS network | 103AT via J_NTC, datasheet JEITA network | 103AT on the battery, datasheet network |

Place both RBOT options and both RICHG options as separate, labelled parts with DNP notes so one board serves either build.

## Connections
- `VIN` → RAC_SNS → input FETs (ACDRV) → `SYS`; buck-boost stage between the input side and the battery side; RBAT_SNS and battery FETs (BATDRV/BATSRC) between `SYS` and `VBAT` — follow BQ25750 Figure 9-1 exactly, scaled to these voltages.
- CE tied low through a resistor (charging enabled by hardware); the ESP32 net `CHG_INHIBIT` can pull it high.
- INT, PG, STAT1, STAT2: 10 kΩ pull-ups to `3V3`; PG and INT to the ESP32 socket nets; STAT1/STAT2 to two LEDs.
- SDA/SCL to the I2C bus.
- TI reference designs to copy from: PMP41100 / PMP41062 (lithium family), PMP31190 / PMP31276 (BQ25751).

## Questions to answer in the reply (read only these sections)
1. BQ25751: is temperature-compensated charging active at reset with no I2C host (EN_VREG_TEMP_COMP reset value)?
2. BQ25751: can the TS divider move the T1 cold cutoff to about −20 °C, and what does that do to compensation accuracy?
3. RAC_SNS value that the ILIM_HIZ constant assumes, and the FET/inductor ratings chosen.

## Done when
Charger placed and wired with both variant resistor sets; electrical check clean on power pins; reply gives a pin-by-pin net list for U_CHG and answers the three questions.
