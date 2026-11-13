# Block 2 — inputs: car feed, USB-C PD sink, OR-ing

**Goal:** produce one protected net `VIN` (9–25 V working, survives car transients) from either source. Capture only.

## Parts
| Function | Part | Note |
|---|---|---|
| Car connector | J_CAR, 2-pin ≥ 10 A | |
| Fuse | F1, 7.5–10 A, ≥ 32 V DC | |
| Clamp | TVS, bidirectional or uni, stand-off ≥ 24 V, clamp < 60 V at the surge current | downstream parts tolerate 65–70 V |
| Reverse / OR diode, car | LM74700-Q1 + N-FET ≥ 60 V | [DS in `datasheets/lm74700-q1.txt`] |
| USB-C receptacle | J_USBC_IN | sink only; CC1/CC2 to the PD controller |
| PD sink controller | TI TPS25730 (D variant with internal switch, or S + external FET) | pin-strapped via ADCIN pins to request **20 V**, fall back to 15 V; no firmware [DS in `datasheets/tps25730.txt`] |
| OR diode, PD | LM74700-Q1 + N-FET | so 20 V never reaches the car connector |

## Requirements
- `VIN_CAR` and `VIN_PD` each pass through their own ideal diode into `VIN`. The higher source wins; neither can backfeed the other.
- Reverse polarity on J_CAR must do no damage.
- PD negotiation must work with no ESP32 present. If the source cannot give 15 V or 20 V, the port stays off (5 V is below the charger's input window).
- Start from TI reference design **PMP41100** (BQ25756E + TPS25730, sink-only) for the PD-controller wiring.
- Add a test point on `VIN` and a divider to the ESP32 ADC net `VIN_SENSE` (scale 25 V → ≤ 3.0 V).

## Design values to take from the datasheets (agent reads these two only)
- TPS25730: the ADCIN1–4 resistor-divider codes for min/max voltage and current.
- LM74700-Q1: charge-pump capacitor, FET gate/anode/cathode wiring from the typical application.

## Done when
`VIN` exists with both sources OR'ed; reply lists the ADCIN strap values chosen and the TVS part with its clamp voltage; no connection to the charger yet beyond the `VIN` net label.
