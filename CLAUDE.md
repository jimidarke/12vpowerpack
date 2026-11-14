# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A design-brief repository for a 12 V in-vehicle UPS PCB (12 V AGM battery, pass-through 12 V output, 5 V USB output). There is no code, build, lint or test step. The schematic and layout live in Flux (project `jimidarke/12v-power-manager`, reached through the `flux` MCP server); this folder holds the research, the net table the schematic is checked against, and the messages sent to the Flux agent.

The GitHub repository is `jimidarke/12vpowerpack`.

## Working method

Research here, capture in Flux. Messaging the Flux agent costs credits; reading the project does not. The owner wires the schematic by hand in the Flux editor (free) and asks for a check; the agent is used sparingly, mainly to place parts. Earlier runs that asked the agent to research or wire spent about 20 credits and wired nothing.

- When the owner says "check", read the schematic back with the free reads (`get_nets`, `get_components`, `get_project`) and compare it pin by pin with `netlist.md`. Report mismatches by designator and pin.
- Message the Flux agent only when the owner asks for it. Before messaging, read `flux-log.md` for the state and the credits spent.
- One objective per message, on the root thread named in `flux-log.md` (not the agent's sub-thread). Bulk tables go in the attachment field.
- Prefer place-only messages: exact library link or part UID per designator, values included, no other properties, no wiring, no research, no electrical check, "if an edit fails, stop and report". Watch the run and send a stop message if it starts retrying. The template is `blocks/01-agent-capture.md`.
- After each run, verify with the free reads before anything else.
- Never chain schematic capture, layout and export in one message.
- Record every message in `flux-log.md`: what was sent, what came back, credits used.

## How the documents fit together

- `requirements.md` is the spec (v3, vehicle-only). The Flux project carries a short copy, `power-board-specification-v3`; its other documents are marked superseded.
- `architecture.md` is the single source for net names, resistor values, the power-control scheme, the ESP32 pin map, connectors and fuses, and it lists how the captured schematic differs from it ("Capture status").
- `blocks/00-reset-v3.md` is the message that reset the Flux project to v3 (sent). `blocks/01-agent-capture.md` holds the templates for agent messages. `blocks/retired/` holds the v2 briefs (lithium, charger, PD, 12 V converter); do not send them.
- `netlist.md` is the pin-by-pin net table, in eight modules, with the Flux library part for each designator and notes on the symbols as placed. The schematic in Flux was drawn from it and verified against it on 2026-11-13; it must stay consistent with `architecture.md`.
- `datasheets/*.txt` are text extracts of the part datasheets. They are large (100–370 KB each), so search them instead of reading them whole.
- `plan.md` holds the status, part-choice reasoning, cost estimate, what was learned about using the Flux agent, and the bench verification plan.
- `flux-log.md` records every agent message, its result and credits, and the checklist of what is done.

Values in `architecture.md` carry a status tag: **[DS]** read in a datasheet extract, **[calc]** arithmetic from datasheet values, **[TBC]** still to confirm. Keep the tags when editing, cite the datasheet section or table for any new **[DS]** value, and resolve **[TBC]** items before layout or ordering, as each one says.

## Design invariants

- One build: vehicle-only, 12 V sealed AGM. No lithium variant, no charger IC, no USB-C PD input, no 12 V converter, no display. The v2 two-build design is in git at tag `v0.2.1`.
- Safety never depends on the ESP32. Fuses, the charge-limit resistor, reverse-polarity and backfeed blocking and the low-voltage cutoff are hardware; the socketed XIAO ESP32-C6 (ESPHome) only times the ignition-off hold-up (a firmware setting), reports voltages, temperature and power in/out, and can switch the 12 V output off.
- The battery never feeds back into the car input, and the input is a vehicle charging system only (no mains adapters: there is no charge regulation).
- The low-voltage cutoff covers both outputs and latches off until the ignition returns.
- All parts must be rated −40 to 85 °C or better. The one accepted exception is the barrel jack (PJ-063AH, −25 °C).
- Target is ≤ C$110 per board at a batch of about 12. Quote prices in CAD. The price checkpoint is the next step now that the schematic is captured.

## Related project

The board's first use is the carNet in-car UPS, a separate project at `/home/jimi/code/carNet`.

## Versioning

`VERSION.txt` holds the version on its first line followed by a changelog. Commits are tagged `vX.Y.Z`.
