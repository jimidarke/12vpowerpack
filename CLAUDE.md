# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A design-brief repository for a 12 V power manager PCB. There is no code, build, lint or test step. The schematic and layout live in Flux (project `jimidarke/4s-12v-battery-pack`, reached through the `flux` MCP server); this folder holds the research and the messages sent to the Flux agent.

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

- `requirements.md` is the spec (v2). It replaces the Flux document `project-specification`.
- `architecture.md` is the single source for net names, the build-variant table, resistor values, the I2C map, the ESP32 pin map and connectors. Block briefs refer to it and must stay consistent with it.
- `blocks/NN-name.md` is one Flux message each, sent in numeric order: goal, parts with MPN and Flux library UID, verified datasheet facts, connections, "Done when", open items.
- `datasheets/*.txt` are text extracts of the TI datasheets. They are large (100–370 KB each), so search them instead of reading them whole.
- `plan.md` holds the part-choice reasoning, fallbacks, price target, cut list and bench verification plan.

Values in `architecture.md` carry a status tag: **[DS]** read in a datasheet extract, **[calc]** arithmetic from datasheet values, **[TBC]** to confirm before capture. Keep the tags when editing, cite the datasheet section or table for any new **[DS]** value, and resolve **[TBC]** items against `datasheets/` before the block that depends on them is sent.

## Design invariants

- One PCB, two builds fixed at assembly: lithium (4S1P, BQ25750, BQ7791502 protector fitted) or lead-acid (12 V AGM, BQ25751, protector section DNP with a 0 Ω link `B-` to `GND`). Any change must state its effect on both builds.
- Safety never depends on the ESP32. Charge voltage, current limits, protection and the 12 V setpoint are resistor-set; the socketed XIAO ESP32-C6 (ESPHome) only monitors, displays and switches the 12 V output.
- In the lithium build `B-` and `GND` are different nets, joined only through the sense resistor and protection FETs. Nothing else connects to `B-`.
- Lead-acid build parts must be rated −40 to 85 °C or better. The lithium build does not charge below 0 °C.
- Target is ≤ $110 per board at a batch of about 12. The price checkpoint and cut list are applied after block 7.

## Related project

The lead-acid build's first use is the carNet in-car UPS, a separate project at `/home/jimi/code/carNet`.

## Versioning

`VERSION.txt` holds the version on its first line followed by a changelog. Commits are tagged `vX.Y.Z`.
