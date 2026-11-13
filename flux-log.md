# Flux log

Project: https://www.flux.ai/jimidarke/12v-power-manager~zn
Root thread ("4x18650 Battery Pack"): https://www.flux.ai/jimidarke/12v-power-manager~zn?thread=cf30e89b-018d-407f-9f30-a2736a6d9810
(Project renamed "12V Power Manager" by block 0 on 2026-11-13; the slug changed from `4s-12v-battery-pack` to `12v-power-manager`. The spec document slug is now `power-board-requirements-v2`, short id `1d`.)
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
| 2026-11-13 | root | Block 0 — spec update; `requirements.md` + `architecture.md` attached; shunt stated as 8 mΩ. First attempt 02:36 CST refused (usage rate limit, reset 02:40); resent 02:42 | Verified: spec replaced (slug now `power-board-requirements-v2`), `architecture` created, `bms-capture-handoff` marked superseded with 8 mΩ shunt, project renamed; 0 components, 0 nets. Agent raised four conflicts (below) | 0.6 |
| 2026-11-13 | root → new sub-thread "4S Battery Protector Capture" | Block 1 — lithium protector; brief + updated `architecture.md` + `requirements.md` attached | **Partial; stopped when credits ran out.** Docs replaced (architecture slug now `power-board-architecture`). Placed, unwired: U_BMS, Q_DSG, Q_CHG, RT_BMS; 0 nets. Missing: R_SNS, connectors, all passives. Agent asked for the AVDD capacitor value, the CTRC/CTRD connection and the CHG gate network; all three now answered from the datasheet in `blocks/01-li-protector.md` | 4.8 (root 0.8, sub 4.0) |

## Conflicts raised by the agent in block 0 (resolved locally 2026-11-13; see below)
1. Input current limit 3 A (RILIM) cannot supply 60 W continuous 12 V out from the car feed without battery assist; at 20 V it leaves no margin for losses, the 5 V rail or charging at full load.
2. Low-voltage cutoff is applied only to the 12 V converter (EN/UVLO); the 5 V rail can still discharge the AGM battery.
3. Input-present from combined `VIN` / charger PG cannot tell car ignition from USB-C power.
4. "Nothing else may connect to `B-`" conflicts literally with the cell-tap and protector connections; reword to separate sensing connections from protection-bypass paths.

Resolution (owner's decisions, 2026-11-13), applied to `requirements.md`, `architecture.md`, blocks 1–5 and `plan.md`:
1. 12 V output is now 3 A continuous, 5 A peak. One 3 A input limit for both sources (RAC_SNS 5 mΩ, RILIM 6.65 kΩ); the limit throttles charging only, loads have priority.
2. LMR33630 EN divider from `SYS` (887 kΩ / 102 kΩ) gives the 5 V rail the same cutoff window as the 12 V rail.
3. Ignition is sensed on `VIN_CAR` (`VCAR_SENSE`); charger PG means any input.
4. `B-` rule reworded. Also found: the protector's thermistor returns to `B-` and the charger's to `GND`, so the lithium build has two thermistors (J_NTC and new J_NTC_BMS).

The Flux documents `power-board-architecture` and `power-board-requirements-v2` were replaced with these versions during block 1.

## Pending
- [x] Block 0 — spec update (2026-11-13)
- [ ] Block 1 — lithium protector (partial; resume on the root thread with the three answers once credits are back, wiring only, no doc changes)
- [ ] Block 2 — inputs
- [ ] Block 3 — charger
- [ ] Block 4 — 12 V rail
- [ ] Block 5 — 5 V and USB
- [ ] Block 6 — controller and UI
- [ ] Block 7 — check and price checkpoint
- [ ] Block 8 — layout
- [ ] Block 9 — cell board
