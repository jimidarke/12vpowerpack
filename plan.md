# Power board: research foundation and Flux working method

## Context

The Flux project `jimidarke/4s-12v-battery-pack` has an empty schematic and two research documents; ~11 credits were spent with nothing captured, mostly on datasheet lookups. The scope has since grown from "4S pack with 12 V out" to a 12 V power manager for lithium or lead-acid. This plan records the architecture and part choices from research done here (free), and sets up a way of briefing the Flux agent so its credits go to schematic capture instead of research.

Flux currently has no credits; every step that messages the agent waits for a top-up. Until then the work is local brief-writing only.

## Requirements (as agreed)

- One PCB design, built as **either** a lithium unit (4S1P, four 18650 on a separate cell board) **or** a lead-acid unit (small 12 V AGM). Chemistry is fixed at build time by which charger chip and resistors are fitted.
- Charge from an ignition-switched car feed (11–14.8 V) and from USB-C PD at 20 V (65 W laptop charger).
- Outputs: regulated 12 V, 3 A continuous and 5 A peak, barrel jack; 5 V 2 A USB-A (non-PD USB-C optional).
- Battery temperature sensing; OLED showing volts/amps at input, battery and each output.
- Socketed ESP32 dev board running ESPHome (MQTT to Home Assistant, as carNet does).
- Batch of ~12; fab-assembled where it pays, hot-air at home otherwise. Full-featured first, then cut on price.
- Uses: carNet in-car UPS (lead-acid build; ~5 W load, ~30 min after ignition off; in the trunk under an interior flap; winters to −40 °C, warming slowly while driving) and a portable lithium pack.
- Decision: build custom rather than buy.

## Design rule

**The board must be safe with the ESP32 unplugged, crashed or mid-update.** Charge voltage, current limits, protection and the 12 V setpoint are set in hardware. The ESP32 only monitors, displays and trims.

## Architecture

```
Car 12 V in ─ fuse ─ TVS ─ ideal diode ─┐
                                        ├─ charger (buck-boost, power path) ─ SYS ─┬─ 12 V buck-boost ─ limit/fuse ─ barrel jack
USB-C PD sink (20 V) ─ ideal diode ─────┘        │                                 └─ 5 V buck ─ USB-A (+ optional USB-C)
                                              battery
   Lithium build: BQ25750 + BQ77915 protector/FETs; pack on XT30 + JST-XH balance + NTC
   Lead-acid build: BQ25751; battery on a fused terminal; protector section not fitted; NTC on the battery
XIAO ESP32-C6 (socketed) ── I2C ── charger ADC (0x6B), INA226 ×2, OLED (0x3C), PD sink
```

The charger's power path feeds the loads from the car/USB-C input while charging, and from the battery otherwise.

## Part choices (research result)

| Function | Choice | Why | Fallback |
|---|---|---|---|
| Charger, lithium build | TI BQ25750 | Li-ion profile, voltage set by resistor divider, standalone, 4.4–70 V input, power path, 16-bit ADC | BQ25756 (same family, no power path; datasheet read) |
| Charger, lead-acid build | TI BQ25751 | Native bulk/absorb/float, built-in cold compensation of charge voltage via the battery NTC, same package and family | — |
| Li protector | TI BQ7791502 | Verified: 4.20 / 2.90 V, standalone, internal balancing | — |
| 12 V rail | TI TPS552882 (resistor-set) | 16 A switch limit; setpoint needs no firmware | LM5176 |
| 5 V rail | TI LMR33630 | 36 V in, 3 A, 25 µA standby, hand-solderable | TPS54302 |
| USB-A port | TPS2514A | Charging-port signature | — |
| USB-C out (optional) | TPS25810 | Correct non-PD 3 A port | drop the port |
| USB-C PD input | TPS25730 (pin-strapped to 20 V); TI pairs it with this charger family in PMP41100 | Works without the ESP32 | STUSB4500, CH224K |
| Car input protection | Fuse + TVS + LM74700-Q1 ideal diode (also on the PD input, to OR the two) | Charger tolerates 70 V | add LTC4368 cutoff |
| Output monitors | INA226 ×2 (12 V out, 5 V out) | ESPHome native | INA238 |
| Display | SSD1306 0.96" I2C module on a header | ESPHome native | SH1106 1.3" |
| Controller | Genuine Seeed XIAO ESP32-C6, socketed 2×7; buy 15 | 85 °C rating, external-antenna option, fixed footprint; cheap SuperMini clones have a known antenna fault | XIAO ESP32-C3 (same socket) |
| Barrel jack | Same Sky PJ-063AH (8 A) | Most jacks are 2–5 A | XT30 |
| Pack cabling | XT30 for pack current, JST-XH 5-pin for taps, two 2-pin NTCs (charger to `GND`, protector to `B-`) | Ribbon is acceptable for taps only | — |

Carried over from the validation: BQ77915 shunt 7–8 mΩ (trip ≈ 9–10 A); CCFG to AVDD; cell filters 33 Ω / 1 µF; CBI to VSS; PRES as the pack's on/ship switch.

## Competitive check and price target

- **Closest product:** Mini-Box OpenUPS, ~$119 (unconfirmed): both chemistries, 6–30 V in, 12 V 6 A out. Lacks USB-C input, 5 V USB, display, car-transient protection.
- **Module stack:** ~$70–80, but no transient or reverse protection, two chargers to switch, poor monitoring.
- **Custom board estimate at qty 12:** $75–110 per board (parts $55–80, PCB + assembly $15–25), excluding cells, cell board and enclosure; allow one re-spin at $300–500. This is an estimate from snippet prices, not quotes.
- **To reuse:** TI reference designs PMP41100 / PMP41062 (this charger family with a PD controller) and PMP31190 / PMP31276 (BQ25751) as schematic starting points for Flux; ignition-sense with a shutdown delay; the watchdog/re-apply patterns from `JohnNeville/esphome-bq-drivers` for the ESPHome side.
- **Cut list if the price is too high:** USB-C output port, second INA226, PD input (use a barrel-jack laptop brick instead), fab assembly of the easy parts.

## Open items (checked in the block briefs before capture)

1. Confirm BQ25750 and BQ25751 are pin-for-pin compatible (BQ25751 and BQ25756 match on all shared pins; BQ25750 not yet read) and list the resistor differences between builds.
2. BQ25751 cold behaviour: datasheet shows −2 to −3 mV/°C/cell compensation and a selectable cold cutoff (−10/−20 °C). Decide the cutoff and what happens below it (battery still powers the load; charging resumes as the trunk warms). NTC goes on the battery.
3. Lead-acid low-voltage cutoff (~11 V, on both the 12 V and the 5 V rail through their enable pins) and a hard off switch so nothing drains either battery.
4. Inrush into the 12 V converter versus the BQ77915 short-circuit trip.
5. ESPHome: no existing component for this charger family; needs a small custom one (read-only monitoring is enough).
6. Before ordering: XIAO row spacing and temperature rating from Seeed's documents; 18650 holder current ratings; exact barrel plug size.

## Working method with Flux

**Principle:** research here, capture there. Each message to the agent is one block, carries the verified facts as an attachment, and is checked afterwards with the free reads.

Local brief folder `/home/jimi/code/powerBoard/`:
- `requirements.md` — the spec above (replaces Flux's `project-specification`).
- `architecture.md` — block diagram, net names, connector pinouts, I2C address map, ESP32 pin map, build-variant table.
- `blocks/NN-name.md` — one file per Flux message: goal, parts (MPN), pin-by-pin connections, values with datasheet section references, done criteria.
- `datasheets/` — text extracts, so facts can be re-checked.
- `flux-log.md` — what was sent, what came back, credits per message.

Steps:
1. Write the brief folder (no credits): requirements, architecture, and the block briefs, resolving the open items against the datasheets.
2. After a credit top-up, send blocks in order on the existing root thread ("4x18650 Battery Pack"), each verified before the next:
   0. Replace the project specification with v2; no capture.
   1. Li protector block (BQ77915, FETs, shunt, pack connectors).
   2. Inputs: car protection, USB-C PD sink, ideal-diode OR.
   3. Charger and power path, with the build-variant parts.
   4. 12 V rail and output protection.
   5. 5 V rail and USB ports.
   6. ESP32 socket, monitors, OLED, switch and button.
   7. Whole-schematic electrical check and BOM → **price checkpoint; apply the cut list here**.
   8. Layout: placement, then routing, then manufacturing files.
   9. Cell board as a second, small Flux project.

Rules: one objective per message; parts by designator; outcomes with constraints attached; never chain capture, layout and export.

## Verification

- After each Flux run: `get_components`, `get_nets`, `get_bom` (free) compared pin-by-pin against the block brief and datasheet extract; mismatches go back as a correction on the same thread.
- After block 7: Flux's electrical check clean, plus an independent review here of the full netlist.
- Bench, before real batteries: current-limited supply as a cell simulator; tap order, over/under-voltage, temperature trips, overcurrent and short-circuit; charger voltage in each build with the ESP32 removed; a 5 A output peak on each input (car feed at 12.5 V, a 65 W USB-C source) to see the charge throttle and the input-to-battery handover without a 12 V dropout; both rails switching off at the low-voltage cutoff.
