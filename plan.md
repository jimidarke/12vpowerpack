# Power board: plan (v3)

## Context

v1 was a 4S lithium pack with 12 V out. v2 grew into a two-chemistry power manager with a buck-boost charger, USB-C PD input, a regulated 12 V converter, current monitors and a display; its ten most expensive parts alone came to about C$73 per board, and two Flux capture runs (9.1 credits) placed 31 lithium-protector parts with no wiring.

On 2026-11-13 the scope was cut back to what the first real use needs: a vehicle-only UPS for carNet. The v2 plan, architecture and briefs are in git at tag `v0.2.1`; the v2 briefs are also in `blocks/retired/`.

## Requirements (as agreed, v3)

- Vehicle only: ignition-switched car feed in, about 14 V when running.
- 12 V sealed AGM battery, charged straight from the car feed through a current-limiting resistor. No charger IC.
- 12 V output passed through unregulated (about 10.9–14.8 V), 3 A continuous, 5 A peak, barrel jack.
- 5 V 2 A USB-A from a buck converter, for loads that need no charger signature (D+ tied to D−).
- Socketed XIAO ESP32-C6 (ESPHome): ignition-off timer (a firmware setting: default 30 min, minimum 1 min, 0 = no timeout, run to the low-voltage cutoff), car and battery voltage, battery temperature, power in and power out. No display.
- Batch of 5 (changed from ~12 on 2026-11-14: a DIY build for the owner, friends and family, in a 3D-printed case), ≤ C$110 per board excluding battery and enclosure.
- Environment: trunk, −40 °C winters.

## Design rule

**The board must be safe with the ESP32 unplugged, crashed or mid-update.** Fuses, the charge limit, backfeed and reverse-polarity blocking and the low-voltage cutoff are hardware. The ESP32 only times the hold-up, reports, and can switch the 12 V output off.

## Part choices

| Function | Choice | Why | Status |
|---|---|---|---|
| Car input diode | TI LM74700-Q1 + CSD18543Q3A (60 V, 8.1 mΩ) | reverse polarity, no backfeed to the car, 20 mV drop | datasheet read |
| Battery discharge diode | second LM74700-Q1 + CSD18543Q3A | same part; no 0.4 V loss or heat at 4–6 A | datasheet read |
| Charge limit | Vishay AC10 3.3 Ω 10 W (straight leads, from Mouser Canada) + Schurter UMT 250 1.6 A time-lag fuse | about 1 A into a flat battery; the fuse covers a reversed or dead-short battery | datasheets read |
| Fuses | ATO/ATC blade fuses in Keystone 3557-2 holders (changed from 3560 on 2026-11-14) | user-replaceable, 30 A, −50 to 145 °C, about C$1.92 against C$4.16 | datasheet read |
| 5 V inductor | Bourns SRP6540-8R2M | 8.2 µH, 5 A saturation | datasheet read |
| 5 V rail and low-voltage cutoff | TI LMR33630 | 36 V in, precision enable sets the cutoff, power-good drives the 12 V switch | datasheet read |
| Surge clamp | SMCJ18CA, ordered as Diodes Inc. SMCJ18CAQ-13-F (bidirectional, 18 V stand-off, 29.2 V clamp) | keeps the rail under the 36 V parts; a jump start or load dump blows the fuse (owner's decision) | datasheet read |
| 12 V output switch | Diodes DMP4015SK3 (−40 V, 11 mΩ) with a 7.5 A fuse | simplest switch that follows the 5 V rail's power-good | datasheet read |
| Power-control small parts | BSS84, 2N7002 ×2, BAT46W | hold switch, gate drivers, ignition diode | datasheets read |
| USB-A port | D+ tied to D− (dedicated-charger signature); TPS2514A removed 2026-11-14 | the loads are a Pi, router or camera, not phones | no part |
| Controller | Seeed XIAO ESP32-C6, socketed 2×7 | carried over from v2; −40 to 85 °C | pin map read; socket footprint to choose at layout |
| Current monitors | TI INA226 ×2 with 5 mΩ shunts: car input and total load | power in and out; battery current by difference; ESPHome native. Sourced from LCSC with the assembly order (owner's decision), two only | datasheet read |
| Temperature | DS18B20 probe on the battery, 3-way screw terminal | −55 to 125 °C, ±2 °C over the full range; ESPHome native | datasheet read |
| Status LEDs | red and green 0603 LEDs, 1 kΩ each, on D9 and D10 (replaced the SK6812 on 2026-11-14) | fab stock parts with no feeder fee; no 3.3 V-data-into-5 V-LED question at −40 °C | parts in the LCSC table |
| Barrel jack | Same Sky PJ-063AH (8 A, 2.0 mm pin, for 5.5 × 2.1 mm plugs) | carried over | rated only to −25 °C; accepted by the owner |

The ideal-diode FETs are CSD18543Q3A rather than the CSD18540Q5B of the v2 design (about C$5 each); the smaller part does the job at 7 A. It is US$1.15 at JLCPCB (2026-11-14).

Considered and not chosen:
- **BQ25751 charger:** proper three-stage charging with cold compensation and mains-adapter input, at about C$25–30 per board with its FETs and inductor. Dropped by the owner's decision; the cost is undercharging in deep cold.
- **eFuse for the 12 V output:** adds an electronic current limit, but the ones I know are rated near 23 V, below the surge clamp level. Revisit if the fuse-only protection proves a nuisance.
- **Hardware timer instead of the ESP32:** cheaper, but fixed and with no reporting.

## Price checkpoint, batch of 5 (2026-11-14, second pass)

This replaces the 2026-11-13 checkpoint, which priced a batch of 12 from DigiKey and Mouser snapshots at about C$85–95 per board (it is in git history).

Basis: per board, at a batch of 5, in CAD at 1.39 CAD/USD, excluding battery, enclosure, wiring, tax, duty and brokerage. The fab-fitted and LCSC parts are priced from the JLCPCB and LCSC APIs, read live on 2026-11-14 (USD, at the quantity for 5 boards; the LCSC line includes LCSC's minimum quantities). JLCPCB fees are from its assembly price page (updated 2026-10-22, re-read 2026-11-14). DigiKey Canada lines were read live on 2026-11-14. The AC10 line is from aggregator listings of the Mouser part (Mouser blocks automated reads). "est." marks a line with no price found.

| Item | Per board (C$) | Source |
|---|---|---|
| Fab-fitted parts (4 E IC types, plus every Basic and Preferred Extended part) | 13.98 | JLCPCB library, live (LMR33630 up from US$0.53 to 0.63) |
| JLCPCB Economic PCBA fees: setup US$8.18, stencil US$1.53, 4 feeder fees × US$3.07, placement check US$0.45, about 900 joints × US$0.0016; US$23.88 per order | 6.64 | JLCPCB price page, re-read 2026-11-14 (unchanged) |
| PCB, 5 × 2-layer 1 oz ≤ 100 × 100 mm, and shipping to Canada | 5.56–8.34 | est.: board US$2–5, shipping US$15–25 (economy to DHL) |
| Hand-soldered SMT from LCSC (DMP4015, SMCJ18CA, SRP6540, shunts ×2, BZT52C12 ×2, BAT46W ×2, green LED, 887 k, 102 k, 24.9 k), with LCSC minimum quantities | 5.63 | LCSC, live (DMP4015 and SRP6540 up about 20 %) |
| Keystone 3557-2 ×3 | 4.70 | DigiKey Canada, live (C$1.566 at 10+) |
| Seeed XIAO ESP32-C6 | 8.52 | DigiKey Canada, live |
| Vishay AC10 3.3 Ω | 4.14 | US$2.98 at 1–9, aggregator listings of the Mouser part; Mouser shipping not included |
| Schurter UMT 250 1.6 A | 2.36 | DigiKey Canada, live (C$2.356 at 5+) |
| PJ-063AH | 2.42 | DigiKey Canada, live |
| Phoenix MKDS 1,5 terminals: 2-way ×2, 3-way ×1 | 2.11 | LCSC, live (DigiKey Canada would be 5.98) |
| Würth USB-A | 1.49 | DigiKey Canada, live |
| 1×7 headers ×2 | 0.40 | LCSC, live (HCTL PM254-1-07-Z-8.5) |
| DS18B20 probe | 2.69 | Universal Solder, 3–9 price (any source) |
| Blade fuses ×3 | 1.95 | DigiKey Canada reference price (any source) |
| LCSC minimum-quantity extras and the LCSC share of shipping | about 3 | est. |
| **Total** | **about 66–68** | target ≤ 110 |

Result: about C$66–68 per board before tax (second pass, 2026-11-14), against C$85–95 for the batch-of-12 checkpoint. The PCB and shipping line was not re-quoted. The fixed costs (fab fees, board and shipping) are about C$12–15 of that. Expect GST/HST on the imports, and DHL brokerage if Express is chosen.

Where the saving came from:
- Fuse holders, from the 3560 to the 3557-2: about C$6.70.
- Fab-fitted and LCSC parts at JLCPCB prices instead of DigiKey snapshots. For example, the LMR33630 is US$0.53 against C$4.50, and the INA226 US$0.56.
- TPS2514A and the SK6812 network removed: about C$1.50, plus two part types.
- Hand-soldering eleven E part types instead of paying their feeder fees: about C$9.40 per board. Paying them instead puts the total at about C$75–80.

Footprint and stock points this created (all in `netlist.md`, LCSC part table):
- The Schurter UMT 250 is out of stock at LCSC; buy it from DigiKey Canada.
- The Vishay AC10 is out of stock at LCSC, and DigiKey Canada lists it only at 3,000 minimum; buy the straight-lead AC10000003308JAB00 from Mouser Canada and bend the leads to 52 mm. Mouser Canada ships free only over C$100 (not confirmed), so a five-resistor order likely pays shipping.
- The Keystone 3557-2 has none at LCSC; buy it from DigiKey Canada.
- The Phoenix terminals and the XIAO headers come from LCSC with the JLCPCB order (moved from DigiKey on 2026-11-14).
- Low stock at LCSC (2026-11-14): SRP6540-8R2M 58 and SMCJ18CA-13-F 62, against 5 needed. Order early; the inductor's fallback is DigiKey Canada (C$1.84).
- Blade fuses and the DS18B20 probe are common parts from any source (Amazon, AliExpress, a car-parts store).
- The SRP6540-8R2M is C2041807; the Flux part's C1329351 is the 4.7 µH value.

Options looked at and not taken:
- The MX74700T (Maxinmicro) for the LM74700-Q1, at US$0.41 against US$2.46: not a drop-in, since its quiescent current is 300 µA against 80 µA, which would roughly triple the standby drain.
- Replacing 887 k / 102 k / 24.9 k with Basic values: the low-voltage cutoff and the 5 V setpoint would move by more than 0.5 %. Hand-soldering three 0603 resistors is cheaper than the error.
- An SMD fuse for F_IN, F_BAT and F_OUT: the 3557-2 is already cheap and keeps the fuses user-replaceable.

## Status (2026-11-14)

- Requirements, architecture and part choices: v3.1 (cost trim for a batch of 5).
- Schematic: moved to KiCad 10 on 2026-11-14 (`kicad/`), generated from `netlist.md`, ERC clean, every pin checked. The Flux capture is archived; comparing it net by net found Q_OR2's gate unwired there.
- Board: 100 × 70 mm outline, 4 × M3, every part placed; first routing pass done on 2026-11-14 (power pours by `kicad/gen/route_pcb.py`, signal nets by Freerouting; DRC clean, 0 unconnected). Thermal vias, fiducials and hand tidying are still to do. First placed from `blocks/04-placement-gen.py` at 100 × 80 mm, then re-placed by `kicad/gen/place_pcb.py` on 2026-11-14 so the parts are spread out and every silkscreen label is readable. The owner lays it out in KiCad on the laptop.
- Price checkpoint: about C$66–68 per board at a batch of 5 (second pass 2026-11-14, table above).
- Next: the laptop checks in `kicad/README.md` (terminal-block wire entry, datasheet-drawn footprints), then routing in KiCad by the owner, DRC here, then the JLCPCB export.
- Not started: routing, firmware, bench tests.

## Next steps

From 2026-11-14 the work is in KiCad (`kicad/README.md`): routing by the owner on the laptop, then DRC and the JLCPCB files (Gerbers, BOM and pick-and-place filtered on the `Fit` field) generated here with `kicad-cli`. The Flux steps below are history.

### Flux steps (history)

1. ~~v3.1 schematic edits~~ done and checked 2026-11-14. Leftovers: delete the six empty net labels.
2. **Part properties:** package, MPN and LCSC number from the LCSC part table, by hand or with the properties-only agent draft (part B; about 1 credit; send only on the owner's go).
3. **Footprints** (part C): the 3557-2 holders, F_CHG, J_TEMP and the screw terminals, the BSS84 pin check, the XIAO socket, R_CHG.
4. **Board outline and mounting holes** (owner, by hand): ≤ 100 × 100 mm, 2 layers, 1 oz, 4 × M3. Size it to the case.
5. **Placement:** agent message 1 in `blocks/03-layout-brief.md` (one objective; verify with `get_layout` and the layout image; refine by hand).
6. **Routing**, then **DRC**, then the **manufacturing export** for JLCPCB: one message each, never chained.
7. In parallel: ESPHome configuration (hold-up timer, soft cutoff with cold steps, INA226 ×2, DS18B20, two LEDs) and the bench plan below.

## Open items

1. Footprints in Flux (next step 3). Part properties were done 2026-11-14.
2. Live prices for the DigiKey Canada lines and a real PCB and shipping quote at order time.
3. CJ 2N7002 temperature rating; the effective capacitance of the 1206 X5R parts on the buck (`netlist.md`).
4. GPIO19 glitch at boot (bench); ESP32-C6 tolerance for the sense dividers' injected current.
5. ESPHome: a "last gasp" report before releasing `HOLD` (no LiPo backup; owner's decision 2026-11-14); the hold-up timer as an adjustable, stored setting (0 = no timeout, otherwise 1 min or more); the soft-cutoff voltages per temperature (`architecture.md`, power control); Wi-Fi/MQTT (as carNet does) or BLE. ESPHome's BLE server support needs checking before relying on it.
6. Confirm the barrel plugs in use are 5.5 × 2.1 mm; battery size per unit; each car's running feed voltage.

## Working method with KiCad (from 2026-11-14)

The owner found Flux's layout cumbersome, so capture moved to KiCad 10 before layout started. `netlist.md` stays the source: `kicad/gen/gen_sch.py` writes the schematic from it and `kicad/gen/check_sch.py` proves it pin by pin, at no cost and in seconds. The owner owns the board and lays it out in the KiCad GUI on the laptop; this box (headless) runs DRC, renders and the fab exports with `kicad-cli`. Git carries the files both ways. Details in `kicad/README.md`.

## Working method with Flux (history)

**Principle:** research here, capture there, check with the free reads.

How the v3 schematic was captured, and what it cost:
- The owner wired the schematic by hand in the Flux editor from `netlist.md`, one module at a time. Wiring by hand costs no credits. After each module the result was read back with `get_nets` and compared with the table; the errors found that way were three shifted XIAO pins, a monitor wired as a copy of the other, one mislabelled net, and a ground net that lost about 40 pins during an edit.
- The Flux agent was used only to reset the project and to place parts, unwired: 3.8 credits for the reset and three place-only runs (80 parts). One further credit went on restoring a part deleted by accident.
- By comparison, the two v2 runs that asked the agent to place and wire a block cost 8.7 credits and wired nothing.

What worked with the agent:
- Place-only messages with the exact library link or part UID for each designator, values included, and "set no other properties".
- One edit for the whole batch; "if an edit fails, do not retry: stop and report".
- Watching the run and sending a stop message when it begins retrying a failed edit.

What to avoid:
- Asking it to wire, research, write part notes or run the electrical check.
- Relying on undo in the editor: a deleted part does not come back with its wires.
- Library entries that would not place (`lcsc/csd18543q3a`) or that mislabel pins (the XIAO "SMD Version" entry carries ESP32-C3 GPIO numbers).

Order of work from here: tidy the capture differences, the price checkpoint, then layout (placement, then routing, then manufacturing files). Never chain capture, layout and export in one agent message.

## Verification

- After any edit to the schematic: `get_components`, `get_nets`, `get_bom` (free) compared against `netlist.md`. Done for the whole schematic on 2026-11-13.
- Before layout: Flux's electrical check clean, and the capture differences settled.
- Bench, before it goes in the car:
  - reverse polarity on the car input and on the battery connector;
  - no current back into the car input with the battery connected;
  - ignition-off handover with a 5 A load on the 12 V output;
  - low-voltage cutoff near 11.0 V and restart only when the car feed returns, with the ESP32 removed and with it fitted;
  - hold-up timer expiry switching everything off;
  - charge current into a battery at 11 V, and F_CHG opening on a 9 V supply standing in for a failed battery;
  - standby drain with everything off;
  - the soft cutoff stepping up with a cold battery (DS18B20 in a freezer);
  - `VCAR_SENSE` with the ignition off and the board at 85 °C (D_IGN leakage);
  - each car's feed voltage with the engine running, before relying on it to charge.
