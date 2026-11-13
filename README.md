# 12 V power pack

A 12 V power manager on one PCB: it charges a battery from a car feed or a USB-C laptop charger and supplies regulated 12 V and 5 V, switching to the battery when the input goes away.

The same board is assembled as one of two builds:

| | Lithium build | Lead-acid build |
|---|---|---|
| Battery | 4S1P Li-ion, four 18650 on a separate cell board | 12 V sealed AGM, 2–12 Ah |
| Charger | TI BQ25750 | TI BQ25751 |
| Protection | BQ7791502 protector and FETs | fused battery terminal, low-voltage cutoff |
| Use | portable pack | in-car UPS |

## Status

Design phase. The requirements, architecture and per-block capture briefs are written; no schematic has been captured yet and nothing has been built or tested. Values marked **[TBC]** in `architecture.md` are still to be confirmed.

## Specification

- **Inputs:** ignition-switched car 12 V (11–14.8 V, reverse-polarity and transient protected) and USB-C PD sink at 20 V. The input is used only above about 12.5 V and dropped below about 11.5 V, so a parked car's battery is not drained.
- **12 V output:** regulated, 5 A continuous, 5.5 mm barrel jack.
- **5 V output:** 2 A USB-A with charging-port signature.
- **Monitoring:** socketed Seeed XIAO ESP32-C6 running ESPHome, reporting over MQTT to Home Assistant, with an SSD1306 OLED showing volts and amps at the input, battery and each output.
- **Safety:** charge voltage, current limits, protection and the 12 V setpoint are set by resistors. The board stays safe with the ESP32 removed.
- **Environment:** the lead-acid build is specified for −40 to 85 °C parts; the lithium build does not charge below 0 °C.

Full details are in [`requirements.md`](requirements.md).

## Block diagram

```
Car 12 V in ─ fuse ─ TVS ─ ideal diode ─┐
                                        ├─ charger (buck-boost, power path) ─ SYS ─┬─ 12 V buck-boost ─ barrel jack
USB-C PD sink (20 V) ─ ideal diode ─────┘        │                                 └─ 5 V buck ─ USB-A
                                              battery
```

## Main parts

| Function | Part |
|---|---|
| Charger and power path | TI BQ25750 (lithium) / BQ25751 (lead-acid), pin-compatible |
| Lithium protector and balancing | TI BQ7791502 |
| 12 V rail | TI TPS552882 |
| 5 V rail | TI LMR33630 |
| USB-C PD sink | TI TPS25730 |
| Input OR-ing and reverse protection | TI LM74700-Q1 |
| Output monitors | TI INA226 ×2 |
| USB-A port controller | TI TPS2514A |
| Controller | Seeed XIAO ESP32-C6 |

## Repository layout

| Path | Contents |
|---|---|
| [`requirements.md`](requirements.md) | What the board must do |
| [`architecture.md`](architecture.md) | Block diagram, net names, build-variant values, I2C map, ESP32 pin map, connectors |
| [`plan.md`](plan.md) | Part-choice reasoning, fallbacks, price target, cut list, bench test plan |
| [`blocks/`](blocks) | One capture brief per schematic block, in build order |
| [`datasheets/`](datasheets) | Text extracts of the datasheets the values were taken from |
| [`flux-log.md`](flux-log.md) | Log of schematic-capture runs |

The schematic and layout are being done in [Flux](https://www.flux.ai/jimidarke/4s-12v-battery-pack~zn). This repository holds the research and briefs that drive that work.

## Cost target

≤ $110 per board at a batch of about 12, excluding cells, cell board and enclosure. This is an estimate, not a quote; it is checked after schematic capture.
