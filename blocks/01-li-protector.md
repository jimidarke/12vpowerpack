# Block 1 — lithium protector (BQ7791502)

**Goal:** capture the standalone 4S protection and balancing block. Lithium build only; every part in this block carries a "DNP in lead-acid build" note. Schematic capture only — no layout.

## Parts
| Ref | Part | Note |
|---|---|---|
| U_BMS | TI BQ7791502PWR (TSSOP-24) | Flux library UID 605cbf43-2e29-4acf-b76a-1b69c672d5a5 |
| Q_DSG, Q_CHG | TI CSD18540Q5B, 60 V | UID dc203c36-44a9-47f5-9f97-78e2de862306; source 1–3, gate 4, drain 5–8 |
| R_SNS | 8 mΩ 1 %, 2512, ≥ 1 W, Kelvin-connected | replaces the 5 mΩ candidate |
| RT_BMS | 103AT-2 on the cell board, via J_NTC_BMS; returns to `B-` (VSS). Separate from the charger's thermistor on J_NTC, which returns to `GND` and belongs to block 3 | UID 7c0ef3ab-aacd-4554-3a50-82912d9abb5e |
| J_PACK, J_BAL, J_NTC_BMS | XT30; JST-XH-5; JST-XH-2 | see architecture |

## Verified datasheet facts (BQ77915, SLUSCU0L) — use these, do not re-research
- Thresholds (Table 6-1/6-2, BQ7791502): OV 4.200 V / 1 s / 200 mV hyst; UV 2.900 V / 1 s / 400 mV hyst, load-removal recovery; OCD1 70 mV / 180 ms; OCD2 70 mV / 180 ms; SCD 120 mV / 0.96 ms; OCC 70 mV; OTD 65 °C, OTC 45 °C, UTD −10 °C, UTC 0 °C; balancing starts at 3.8 V.
- Current thresholds are ±20 % (EC table, VCCAH). With 8 mΩ: OCD 8.75 A (7.0–10.5 A), SCD 15 A (12–18 A), OCC 8.75 A.
- 4-cell configuration: **CCFG to AVDD** (Table 9-7). Unused cell input shorted per Figure 9-12 / §11.
- Pins (Table 7-1): 1 VDD, 2 AVDD (capacitor only), 3–8 VC5…VC0, 9 VSS, 10 SRP (battery side of R_SNS), 11 SRN (pack side), 12 DSG, 13 CHG, 14 LD, 15 LPWR (float), 16 CBI, 17 OCDP, 18 TS, 19 VTB, 20 CCFG, 21 CBO (float), 22 PRES, 23 CTRC, 24 CTRD (CHG and DSG override inputs, each through 10 MΩ per the recommended components).
- Recommended components (§8.3): cell input filter for internal balancing **33 Ω + 1 µF** per cell; VDD filter 1 kΩ + 1 µF; thermistor 103AT from TS to VSS with 10 kΩ 1 % from VTB to TS; gate-source resistors 1 MΩ; DSG gate resistor 4.5 kΩ; CHG gate resistor 1 kΩ (or 1 MΩ with the extra CHG-protection parts — follow Figure 9-12); LD resistor 470 kΩ; CTRC/CTRD via 10 MΩ.
- **CBI to VSS** enables balancing (§9.3.4); max 50 mA; only while charging.
- OCDP: 100 kΩ 1 % to VSS selects the factory delays (Table 9-3).
- PRES must be > 1.5 V for NORMAL mode; floating = HIBERNATE after 4.5 s (§9.3.5). Wire PRES through the recommended resistor to a net `PACK_EN` that the power switch pulls up; this is the pack's on/ship switch.
- Gate drive 11–14 V at VDD ≥ 12 V (EC table).

## Connections
- Follow **Figure 9-12** (4-series, internal balancing, HIBERNATE enabled) pin for pin.
- Low-side protection: `B-` → R_SNS → Q_DSG / Q_CHG back-to-back → `GND` (PACK−). Besides that path, `B-` connects only to J_PACK, J_BAL pin 1 and U_BMS's own VSS-referenced pins, filters and thermistor (J_NTC_BMS). No load, charger, converter or other connector return may use `B-`.
- J_BAL pin order: B−, C1, C2, C3, B+. J_PACK: B+ (= `VBAT`), B−.
- `VBAT` leaves the block to the charger block; do not connect anything else to it here.

## Done when
All parts placed with Role / Role Details metadata; nets named as in the architecture; electrical check shows no unconnected power pins; reply lists every pin of U_BMS with its net. Stop there — no charger, no converters.

## Open (report, do not solve)
- Inrush: the 12 V converter's input capacitance on `SYS` versus the 12–18 A / 0.96 ms short-circuit window.
