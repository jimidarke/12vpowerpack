# Power board: plan (v3)

## Context

v1 was a 4S lithium pack with 12 V out. v2 grew into a two-chemistry power manager with a buck-boost charger, USB-C PD input, a regulated 12 V converter, current monitors and a display; its ten most expensive parts alone came to about C$73 per board, and two Flux capture runs (9.1 credits) placed 31 lithium-protector parts with no wiring.

On 2026-11-13 the scope was cut back to what the first real use needs: a vehicle-only UPS for carNet. The v2 plan, architecture and briefs are in git at tag `v0.2.1`; the v2 briefs are also in `blocks/retired/`.

## Requirements (as agreed, v3)

- Vehicle only: ignition-switched car feed in, about 14 V when running.
- 12 V sealed AGM battery, charged straight from the car feed through a current-limiting resistor. No charger IC.
- 12 V output passed through unregulated (about 10.9–14.8 V), 3 A continuous, 5 A peak, barrel jack.
- 5 V 2 A USB-A from a buck converter.
- Socketed XIAO ESP32-C6 (ESPHome): ignition-off timer (a firmware setting: default 30 min, minimum 1 min, 0 = no timeout, run to the low-voltage cutoff), car and battery voltage, battery temperature, power in and power out. No display.
- Batch of ~12, ≤ C$110 per board excluding battery and enclosure.
- Environment: trunk, −40 °C winters.

## Design rule

**The board must be safe with the ESP32 unplugged, crashed or mid-update.** Fuses, the charge limit, backfeed and reverse-polarity blocking and the low-voltage cutoff are hardware. The ESP32 only times the hold-up, reports, and can switch the 12 V output off.

## Part choices

| Function | Choice | Why | Status |
|---|---|---|---|
| Car input diode | TI LM74700-Q1 + CSD18543Q3A (60 V, 8.1 mΩ) | reverse polarity, no backfeed to the car, 20 mV drop | datasheet read |
| Battery discharge diode | second LM74700-Q1 + CSD18543Q3A | same part; no 0.4 V loss or heat at 4–6 A | datasheet read |
| Charge limit | Vishay AC10 3.3 Ω 10 W + Schurter UMT 250 1.6 A time-lag fuse | about 1 A into a flat battery; the fuse covers a reversed or dead-short battery | datasheets read |
| Fuses | ATO/ATC blade fuses in Keystone 3560 holders | user-replaceable, −50 °C rated holder | datasheet read |
| 5 V inductor | Bourns SRP6540-8R2M | 8.2 µH, 5 A saturation | datasheet read |
| 5 V rail and low-voltage cutoff | TI LMR33630 | 36 V in, precision enable sets the cutoff, power-good drives the 12 V switch | datasheet read |
| Surge clamp | SMCJ18CA, ordered as Diodes Inc. SMCJ18CAQ-13-F (bidirectional, 18 V stand-off, 29.2 V clamp) | keeps the rail under the 36 V parts; a jump start or load dump blows the fuse (owner's decision) | datasheet read |
| 12 V output switch | Diodes DMP4015SK3 (−40 V, 11 mΩ) with a 7.5 A fuse | simplest switch that follows the 5 V rail's power-good | datasheet read |
| Power-control small parts | BSS84, 2N7002 ×2, BAT46W | hold switch, gate drivers, ignition diode | datasheets read |
| USB-A port | TI TPS2514A | charging-port signature | datasheet read |
| Controller | Seeed XIAO ESP32-C6, socketed 2×7 | carried over from v2; −40 to 85 °C | pin map read; socket footprint to choose at layout |
| Current monitors | TI INA226 ×2 with 5 mΩ shunts: car input and total load | power in and out; battery current by difference; ESPHome native. Sourced from LCSC with the assembly order (owner's decision), two only | datasheet read |
| Temperature | DS18B20 probe on the battery, 3-way screw terminal | −55 to 125 °C, ±2 °C over the full range; ESPHome native | datasheet read |
| Status LED | SK6812 addressable RGB, one, on a single pin | WS2812B is only rated to −25 °C; SK6812 to −40 °C | datasheet read; logic level to bench-check |
| Barrel jack | Same Sky PJ-063AH (8 A, 2.0 mm pin, for 5.5 × 2.1 mm plugs) | carried over | rated only to −25 °C; accepted by the owner |

The ideal-diode FETs are CSD18543Q3A rather than the CSD18540Q5B of the v2 design (about C$5 each); the smaller part does the job at 7 A. Its price is not checked yet.

Considered and not chosen:
- **BQ25751 charger:** proper three-stage charging with cold compensation and mains-adapter input, at about C$25–30 per board with its FETs and inductor. Dropped by the owner's decision; the cost is undercharging in deep cold.
- **eFuse for the 12 V output:** adds an electronic current limit, but the ones I know are rated near 23 V, below the surge clamp level. Revisit if the fuse-only protection proves a nuisance.
- **Hardware timer instead of the ESP32:** cheaper, but fixed and with no reporting.

## Cost estimate

About C$55–75 per board assembled, at a batch of 12, excluding battery and enclosure. The LCSC price for the INA226 is converted from US$0.62–0.86; DigiKey Canada lists it at C$4.47. This is my rough estimate from the CAD snapshot prices collected on 2026-11-13 (LM74700-Q1 C$2.59, LMR33630 about C$4.50, XIAO C$8.29, INA226 about C$1 from LCSC, PJ-063AH about C$2.20) plus guesses for the parts not yet priced; it is not a costed BOM. The schematic is captured, so the price checkpoint is the next step.

## Status (2026-11-13)

- Requirements, architecture and part choices: done, at v3.
- Schematic: captured in Flux, 80 parts, every net verified against `netlist.md`.
- Next: tidy the capture differences listed in `architecture.md`, run the price checkpoint, then layout.
- Not started: layout, firmware, bench tests.

## Open items

1. Price checkpoint: a costed BOM in CAD against the C$110 target.
2. Capture differences to settle before layout (`architecture.md`, "Capture status"): part packages, the J_TEMP placeholder, the BSS84LT1G symbol's pin numbers, the D_TVS and L1 order numbers, the F_BAT rating, test points.
3. Footprints at layout: Keystone 3560 fuse holders, the Schurter fuse, the XIAO socket.
4. MPNs for the 5 mΩ shunts; temperature ratings of the screw terminals and USB-A receptacle.
5. GPIO19 behaviour at boot; ESP32-C6 tolerance for the sense dividers' injected current.
6. ESPHome: the hold-up timer as an adjustable, stored setting (0 = no timeout, otherwise 1 min or more), and whether to report over Wi-Fi/MQTT (as carNet does) or BLE. ESPHome's BLE server support needs checking before relying on it.
7. Confirm the barrel plugs in use are 5.5 × 2.1 mm; battery size per unit.

## Working method with Flux

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
  - standby drain with everything off.
