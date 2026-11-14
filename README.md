# 12 V power pack

A small in-vehicle UPS on one PCB: a 12 V sealed AGM battery floated on the car's charging voltage, a pass-through 12 V output and a 5 V USB-A output that keep running from the battery for a set time after the ignition goes off.

## Status

Design phase. The requirements and architecture were cut back to this vehicle-only design (v3) on 2026-11-13; the schematic is captured in Flux and checked against the net table (2026-11-13), but the board is not laid out and nothing has been built or tested. Values marked **[TBC]** in `architecture.md` are still to be confirmed. The earlier two-chemistry design (v2) is in git at tag `v0.2.1`.

## Specification

- **Input:** ignition-switched car 12 V (11–14.8 V), reverse-polarity and transient protected. The battery never feeds back into the car. Not for mains adapters.
- **Battery:** 12 V sealed AGM, 2–12 Ah, charged from the car feed through a current-limiting resistor. There is no charger IC.
- **12 V output:** unregulated, about 10.9–14.8 V, 3 A continuous with 5 A peaks, 5.5 mm barrel jack.
- **5 V output:** 2 A USB-A with charging-port signature.
- **Power control:** outputs stay on for an adjustable time after ignition-off (a firmware setting, default 30 min; 0 = no timeout), then everything switches off until the ignition returns. A hardware low-voltage cutoff near 11.0 V protects the battery.
- **Monitoring:** socketed Seeed XIAO ESP32-C6 running ESPHome, reporting car voltage, battery voltage, battery temperature, and power in and out from two INA226 current monitors. One RGB status LED. No display.
- **Safety:** fuses, the charge limit, reverse-polarity blocking and the low-voltage cutoff are hardware. The board stays safe with the ESP32 removed.
- **Environment:** parts rated −40 to 85 °C.

Full details are in [`requirements.md`](requirements.md).

## Block diagram

```
Car 12 V in ─ fuse ─ TVS ─ ideal diode ─ SYS ─┬─ switch ─ fuse ─ 12 V barrel jack
                                              ├─ 5 V buck ─ USB-A, ESP32
                                              ├─ fuse ─ charge resistor ─┐
                                              └─ ideal diode ────────────┴─ fuse ─ AGM battery
```

## Main parts

| Function | Part |
|---|---|
| Input and battery ideal diodes | TI LM74700-Q1 ×2 with CSD18543Q3A FETs |
| Surge clamp | SMCJ18CA |
| 12 V output switch | Diodes DMP4015SK3 |
| 5 V rail and low-voltage cutoff | TI LMR33630 |
| USB-A port controller | TI TPS2514A |
| Current monitors | TI INA226 ×2 |
| Controller | Seeed XIAO ESP32-C6 |
| Battery temperature | DS18B20 probe |

## Repository layout

| Path | Contents |
|---|---|
| [`requirements.md`](requirements.md) | What the board must do |
| [`architecture.md`](architecture.md) | Block diagram, net names, values, power control, ESP32 pin map, connectors |
| [`netlist.md`](netlist.md) | Pin-by-pin net table the schematic was drawn from and is checked against |
| [`plan.md`](plan.md) | Status, part-choice reasoning, cost estimate, how the capture was done, bench test plan |
| [`blocks/`](blocks) | Messages sent to the Flux agent and their templates; `retired/` holds the v2 briefs |
| [`datasheets/`](datasheets) | Text extracts of the datasheets the values were taken from |
| [`flux-log.md`](flux-log.md) | Log of Flux agent runs, credits and the capture checklist |

The schematic is in [Flux](https://www.flux.ai/jimidarke/12v-power-manager~zn), and the layout will be done there. This repository holds the research and the net table that work is checked against.

## Cost target

≤ C$110 per board at a batch of about 12, excluding battery and enclosure. The current rough estimate is C$55–75; it is checked after schematic capture.
