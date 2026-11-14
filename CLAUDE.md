# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A design-brief repository for a 12 V in-vehicle UPS PCB (12 V AGM battery, pass-through 12 V output, 5 V USB output). The schematic and board are a KiCad 10 project in `kicad/` (moved from Flux on 2026-11-14); this folder also holds the research and the net table the schematic is generated from.

The GitHub repository is `jimidarke/12vpowerpack`.

## Working method

Research here, generate and check here, lay out on the owner's laptop. This box is headless: it runs `kicad-cli` and the `pcbnew` Python module (KiCad 10.0.8, PPA `kicad/kicad-10.0-releases`); the owner runs the KiCad GUI on a Windows laptop. Files move by git push and pull. `kicad/README.md` has the commands and the file ownership.

- `netlist.md` is the source of the schematic. To change the schematic, edit `netlist.md` and run `python3 kicad/gen/gen_sch.py` then `python3 kicad/gen/check_sch.py` (ERC, and KiCad's netlist compared pin by pin with `netlist.md`). Never edit `kicad/powerpack.kicad_sch` by hand.
- The board (`kicad/powerpack.kicad_pcb`) belongs to the owner. Read it, run DRC on it, render it; do not write it unless the owner hands it over for a specific change. Schematic changes reach it through "Update PCB from Schematic" on the laptop.
- On the owner's laptop the session runs in WSL, which has no Linux KiCad. Use the Windows KiCad 10 binaries from WSL instead: `"/mnt/c/Program Files/KiCad/10.0/bin/python.exe"` for scripts that import `pcbnew` and `kicad-cli.exe` beside it (see `kicad/README.md`). The repository is then the same folder KiCad has open, so the owner closes the board before anything writes it.
- `kicad/gen/place_pcb.py` is the placement pass (table of positions, label placement, checks). It only runs on an unrouted board and only when the owner asks for a placement pass.
- When the owner says "check": `git pull`, then `check_sch.py` and `kicad-cli pcb drc --schematic-parity`, and report by designator and pin.
- Render images with `kicad-cli ... export svg` and `rsvg-convert` and look at them before reporting layout or schematic changes.
- Use stock KiCad 10 symbols and footprints where they exist; parts from LCSC come in through `easyeda2kicad` (venv `~/.venvs/kicad-tools`) and `kicad/gen/build_lib.py`. Check every pin number against the datasheet before use.
- Flux (project `jimidarke/12v-power-manager`, `flux` MCP server) is archived. Free reads are fine for comparison; do not message its agent (it costs credits). `flux-log.md` holds the history.

## How the documents fit together

- `requirements.md` is the spec (v3, vehicle-only). The Flux project carries a short copy, `power-board-specification-v3`; its other documents are marked superseded.
- `architecture.md` is the single source for net names, resistor values, the power-control scheme, the ESP32 pin map, connectors and fuses, and it lists how the captured schematic differs from it ("Capture status").
- `blocks/00-reset-v3.md` is the message that reset the Flux project to v3 (sent). `blocks/01-agent-capture.md` holds the templates for agent messages. `blocks/02-v31-schematic-edits.md` lists the v3.1 edits to make in Flux (hand edits, plus a properties-only agent draft, not sent). `blocks/03-layout-brief.md` is the board and placement brief (draft, not sent). `blocks/retired/` holds the v2 briefs (lithium, charger, PD, 12 V converter); do not send them.
- `netlist.md` is the pin-by-pin net table, in eight modules, and the LCSC part table that is the BOM for the fab. `kicad/gen/gen_sch.py` generates the KiCad schematic from it (module tables for the connections, the LCSC tables for the LCSC, MPN and Fit fields). It must stay consistent with `architecture.md`. Its notes on the Flux symbols are history.
- `kicad/` is the KiCad project: generated schematic, owner's board, project library, and the generator and check scripts in `kicad/gen/`. `blocks/04-placement-gen.py` is the placement plan the board was first placed from.
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
- Target is ≤ C$110 per board at a batch of 5 (a DIY build for the owner, friends and family, in a 3D-printed case; not for sale). Quote prices in CAD. JLCPCB fits the SMT parts; the owner hand-solders the through-hole parts and any easy SMT part whose per-order feeder fee is not worth paying. The price checkpoint is in `plan.md`.

## Related project

The board's first use is the carNet in-car UPS, a separate project at `/home/jimi/code/carNet`.

## Versioning

`VERSION.txt` holds the version on its first line followed by a changelog. Commits are tagged `vX.Y.Z`.
