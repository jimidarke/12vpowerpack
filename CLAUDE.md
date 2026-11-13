# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A design-brief repository for a 12 V in-vehicle UPS PCB (12 V AGM battery, pass-through 12 V output, 5 V USB output). There is no code, build, lint or test step. The schematic and layout live in Flux (project `jimidarke/12v-power-manager`, reached through the `flux` MCP server); this folder holds the research and the messages sent to the Flux agent.

The remote is named `12vpowerpack`; the local folder is `powerBoard`.

## Working method

Research here, capture in Flux. Messaging the Flux agent costs credits; reading the project does not. Earlier runs spent about 11 credits on datasheet lookups and captured nothing, which is why the briefs exist.

- Before messaging Flux, read `flux-log.md` for the next pending block and the credit state.
- Send one block per message, on the root thread named in `flux-log.md` (not the agent's sub-thread). The block file is the message; `architecture.md` and any datasheet excerpt go in the attachment field.
- State which facts are already verified so the agent does not re-research them.
- After each run, check the result with the free reads (`get_components`, `get_nets`, `get_bom`) against the block's "Done when" section before sending the next block. Corrections go on the same thread and name designators.
- Never chain schematic capture, layout and export in one message.
- Record every message in `flux-log.md`: what was sent, what came back, credits used.

## How the documents fit together

- `requirements.md` is the spec (v3, vehicle-only). The Flux documents still describe v2 until they are replaced (see `flux-log.md`).
- `architecture.md` is the single source for net names, resistor values, the power-control scheme, the ESP32 pin map, connectors and fuses. Block briefs refer to it and must stay consistent with it.
- `blocks/NN-name.md` is one Flux message each, sent in numeric order: goal, parts with MPN and Flux library UID, verified datasheet facts, connections, "Done when", open items. `blocks/retired/` holds the v2 briefs (lithium, charger, PD, 12 V converter); do not send them.
- `netlist.md` is the pin-by-pin net table the owner draws the schematic from by hand in Flux; it must stay consistent with `architecture.md`. Check the drawn schematic against it with the free reads.
- `datasheets/*.txt` are text extracts of the part datasheets. They are large (100–370 KB each), so search them instead of reading them whole.
- `plan.md` holds the part-choice reasoning, cost estimate, capture plan and bench verification plan.

Values in `architecture.md` carry a status tag: **[DS]** read in a datasheet extract, **[calc]** arithmetic from datasheet values, **[TBC]** to confirm before capture. Keep the tags when editing, cite the datasheet section or table for any new **[DS]** value, and resolve **[TBC]** items against `datasheets/` before the block that depends on them is sent.

## Design invariants

- One build: vehicle-only, 12 V sealed AGM. No lithium variant, no charger IC, no USB-C PD input, no 12 V converter, no display. The v2 two-build design is in git at tag `v0.2.1`.
- Safety never depends on the ESP32. Fuses, the charge-limit resistor, reverse-polarity and backfeed blocking and the low-voltage cutoff are hardware; the socketed XIAO ESP32-C6 (ESPHome) only times the ignition-off hold-up (a firmware setting), reports voltages, temperature and power in/out, and can switch the 12 V output off.
- The battery never feeds back into the car input, and the input is a vehicle charging system only (no mains adapters: there is no charge regulation).
- The low-voltage cutoff covers both outputs and latches off until the ignition returns.
- All parts must be rated −40 to 85 °C or better. The one accepted exception is the barrel jack (PJ-063AH, −25 °C).
- Target is ≤ C$110 per board at a batch of about 12. Quote prices in CAD. The price checkpoint is applied after the whole-schematic check.

## Related project

The board's first use is the carNet in-car UPS, a separate project at `/home/jimi/code/carNet`.

## Versioning

`VERSION.txt` holds the version on its first line followed by a changelog. Commits are tagged `vX.Y.Z`.
