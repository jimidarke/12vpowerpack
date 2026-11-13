# Flux log

Project: https://www.flux.ai/jimidarke/4s-12v-battery-pack~zn
Root thread ("4x18650 Battery Pack"): https://www.flux.ai/jimidarke/4s-12v-battery-pack~zn?thread=cf30e89b-018d-407f-9f30-a2736a6d9810
(The "4S BMS Schematic" thread is the agent's own sub-thread; message the root thread.)

## Rules
- One block per message; the block file is the message, `architecture.md` and any datasheet excerpt go in the attachment field.
- Tell the agent which facts are already verified so it does not re-research them.
- After each run, verify with the free reads (`get_components`, `get_nets`, `get_bom`) against the block's "Done when" before sending the next.
- Corrections go on the same thread, naming designators.

## History
| Date | Thread | Sent | Result | Credits |
|---|---|---|---|---|
| 2026-10-01 | root | initial requirements chat, spec v1 | `project-specification` written | 2.2 |
| 2026-10-01, 2026-11-12 | sub-thread | BMS capture (two attempts) | research only, `bms-capture-handoff`; 0 components | 9.1 |

## Pending (blocked on credits)
- [ ] Block 0 — spec update
- [ ] Block 1 — lithium protector
- [ ] Block 2 — inputs
- [ ] Block 3 — charger
- [ ] Block 4 — 12 V rail
- [ ] Block 5 — 5 V and USB
- [ ] Block 6 — controller and UI
- [ ] Block 7 — check and price checkpoint
- [ ] Block 8 — layout
- [ ] Block 9 — cell board
