# 12 V power pack

A small in-vehicle UPS on one PCB: a 12 V sealed AGM battery floated on the car's charging voltage, a pass-through 12 V output and a 5 V USB-A output that keep running from the battery for a set time after the ignition goes off.

## Status

Design phase. The requirements and architecture were cut back to this vehicle-only design (v3) on 2026-11-13, and the schematic was captured in Flux and checked against the net table that day. On 2026-11-14 the parts were trimmed for a DIY batch of 5 (v3.1), and the schematic was updated and re-checked (77 parts). Later that day capture moved to KiCad 10: the schematic is generated from the net table, and the 100 × 70 mm board is placed, has its first routing pass (power pours and autorouted signals, DRC clean) and carries its silkscreen labels. The routing fixes from the first review, thermal vias and fiducials are in; the checks against parts in hand are still to do (`kicad/README.md`). Nothing has been built or tested. Values marked **[TBC]** in `architecture.md` are still to be confirmed. The earlier two-chemistry design (v2) is in git at tag `v0.2.1`.

## Specification

- **Input:** ignition-switched car 12 V, 13.8–14.4 V nominal with the engine running and 11–14.8 V working. The board starts at about 12.1 V (11.5–12.7 V across part tolerances); once running, the battery carries it through dips and cranking. It is reverse-polarity protected, clamped above 18 V, and the input fuse blows on a sustained 20–22 V. About 5 A continuous and 7 A peak. The battery never feeds back into the car. Not for mains adapters.
- **Battery:** 12 V sealed AGM, 2–12 Ah, charged from the car feed through a current-limiting resistor. There is no charger IC.
- **12 V output:** unregulated: the car feed or the battery less 0.1–0.5 V, so about 10.8–14.8 V (9.9 V worst case at a 5 A peak near the cutoff). 3 A continuous with 5 A peaks, 5.5 mm barrel jack. A car-side fault passes through, up to about 22 V (29 V during a clamped surge).
- **5 V output:** 5.02 V (4.86–5.17 V worst case), 2 A USB-A for loads such as a Pi, router or camera (D+ tied to D−, no charging-port IC).
- **Power control:** outputs stay on for an adjustable time after ignition-off (a firmware setting, default 30 min; 0 = no timeout), then everything switches off until the ignition returns. A hardware low-voltage cutoff near 11.0 V (10.5–11.45 V across part tolerances) protects the battery.

The full voltage and power budget is in [`architecture.md`](architecture.md#voltage-and-power-budget-calc).
- **Monitoring:** socketed Seeed XIAO ESP32-C6 running ESPHome, reporting car voltage, battery voltage, battery temperature, and power in and out from two INA226 current monitors. Red and green status LEDs. No display.
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
| Current monitors | TI INA226 ×2 |
| Controller | Seeed XIAO ESP32-C6 |
| Battery temperature | DS18B20 probe |

## Repository layout

| Path | Contents |
|---|---|
| [`requirements.md`](requirements.md) | What the board must do |
| [`architecture.md`](architecture.md) | Block diagram, net names, values, power control, voltage and power budget, ESP32 pin map, connectors |
| [`netlist.md`](netlist.md) | Pin-by-pin net table the KiCad schematic is generated from and checked against |
| [`kicad/`](kicad) | KiCad 10 project: generated schematic, board, project library, generator and check scripts ([README](kicad/README.md)) |
| [`plan.md`](plan.md) | Status, part-choice reasoning, cost estimate, how the capture was done, bench test plan |
| [`blocks/`](blocks) | Placement plan (`04-placement*`), layout brief, and the Flux messages and edit lists (history); `retired/` holds the v2 briefs |
| [`datasheets/`](datasheets) | Text extracts of the datasheets the values were taken from |
| [`flux-log.md`](flux-log.md) | Log of the Flux agent runs and credits (Flux archived 2026-11-14) |

The schematic and board are in KiCad 10 (`kicad/`). The earlier Flux capture ([project](https://www.flux.ai/jimidarke/12v-power-manager~zn)) is archived.

## Cost target

≤ C$110 per board at a batch of 5, excluding battery and enclosure. The current price checkpoint is in [`plan.md`](plan.md): the fab fits the SMT parts and the owner hand-solders the through-hole parts and a few easy SMT ones.
