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
| 2026-11-13 11:21 CST | root | Block 1 resume (wiring only, brief attached) | **Refused, not delivered:** usage rate limit, resets 2026-11-13 13:41 CST (19:41:11 UTC). Design unchanged: 4 parts, 0 nets, all threads idle. Not retried | 0 |
| 2026-11-13 13:45 CST | root → new sub-thread "Li Protector Schematic Capture" (`33ff301e-6d55-4a23-86d6-d37222c746e3`) | Block 1 resume (wiring only, brief attached, no doc edits) | **Partial; stopped again when credits ran out (`rate_limited`).** 27 parts added with metadata (31 placed in total): R_SNS, J_PACK (XT30PW-M), J_BAL (B5B-XH-A), J_NTC_BMS (B2B-XH-A), R_VC5/3/2/1/0, C_VC5/3/2/1/0, R_VDD, C_VDD, C_AVDD, R_VTB, R_OCDP, R_PRES, R_LD, R_DSG (4.53 kΩ), RGS_DSG, R_CHG, RGS_CHG, D_CHG (1N4148W-13-F), DZ_CHG (BZT52C16-7-F). **Still 0 nets.** Roles of U_BMS, Q_DSG, Q_CHG, RT_BMS not normalised. Documents untouched. Agent's open points below | 4.3 (root 0.4, sub 3.9) |

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

## Block 1 open points after the 13:45 run (2026-11-13)
Root thread total is now 20.9 credits. Block 1 has cost 9.1 credits over two runs and nothing is wired.
1. **D_CHG / DZ_CHG polarity:** the library SOD-123 symbols expose only pins 1 and 2. The agent proposes pin 1 = cathode and wants confirmation before wiring.
2. **`PACK_EN`:** no pull-up source in block 1. The agent proposes leaving it single-ended into R_PRES; the pack on/ship switch has to be assigned to a later block.
3. **Cell-filter capacitor returns:** the agent read VC0's CIN as returning to VSS and set all five to `B-`, but its own check marked the other four as unsupported. The text extract in `datasheets/bq77915.txt` does not settle it; Figure 9-12 has to be read from the PDF.
4. **SRP / SRN:** the brief lists no filter; the agent plans direct Kelvin connections and asks for confirmation against Figure 9-12.
5. Planned net `BMS_SNS_N` (R_SNS pack side, SRN, Q_DSG source) is the agent's name; check it against `architecture.md`.
6. New parts carry Roles outside the three named in the brief (Connector, Power Filtering, Decoupling, Pull Up / Down). R_DSG is 4.53 kΩ (E96) rather than 4.5 kΩ.

## Scope change to v3 (owner's decision, 2026-11-13)
The design was cut back to a vehicle-only AGM unit with no charger IC, no USB-C PD input, no 12 V converter and no display (`requirements.md` v3, `architecture.md` v3). Nothing has been sent to Flux about this yet.

State of the Flux project against v3:
- The 31 placed parts are all lithium protector parts (Functional Group `Li Protector`) and are no longer wanted. The two CSD18540Q5B FETs (`Q_DSG`, `Q_CHG`) could be reused as the ideal-diode FETs if that part is chosen.
- The Flux documents `power-board-requirements-v2`, `power-board-architecture`, `bms-capture-handoff` and `block-1-capture-status` describe v2 and need replacing or marking superseded.
- The block 1 open points above are closed by the scope change.
- Credits spent to date on the root thread and its sub-threads: 20.9.

## Pending (v3)
Capture is by hand in the Flux editor from `netlist.md` (owner's decision, 2026-11-13); no agent messages are planned until a final review. The v2 briefs are in `blocks/retired/`.
- [ ] Owner: delete the 31 lithium parts and mark the v2 Flux documents superseded
- [ ] Block A — input, battery path, current monitors (drawn by hand, checked with free reads)
- [ ] Block B — 5 V rail, power control, 12 V output, USB, LED
- [ ] Block C — controller socket and sensors
- [ ] Whole-schematic check against `netlist.md` and price checkpoint
- [ ] Optional: one agent review of the finished schematic
- [ ] Layout
