# KiCad project

KiCad 10 project for the board: `powerpack.kicad_pro`. Open it in KiCad 10.0.x; the Linux box that generates and checks the files runs 10.0.8, so keep both machines on the same major version.

## Files

| File | Who edits it | What it is |
|---|---|---|
| `powerpack.kicad_sch` | generated: `gen/gen_sch.py` | Schematic, one A2 sheet, one dashed box per module. Every pin carries a net label; there are no wires between parts. **Edit `../netlist.md`, not this file.** |
| `powerpack.kicad_pcb` | the owner, in KiCad | Board. Written once by `gen/gen_pcb.py`, then re-placed on 2026-11-14 by `gen/place_pcb.py` at the owner's request (100 × 70 mm, parts spread out, every label in a clear spot). First routing pass and silkscreen pass (`gen/silk_pcb.py`) on 2026-11-14. Edited by hand from here on, except the silkscreen labels, which come from `silk_pcb.py`; `place_pcb.py` refuses to run once the board has tracks. |
| `powerpack.kicad_pro` | KiCad, plus `gen_pcb.py` once | Project settings, net classes (`Power`: 1.5 mm tracks and 0.8/0.4 mm vias on the power path and GND; `Default`: 0.25 mm; both 0.13 mm clearance, the pours 0.3 mm) and JLCPCB minimums. |
| `sym-lib-table`, `fp-lib-table` | fixed | Add the project library `pwrpack` with `${KIPRJMOD}` paths, so it works on Windows and Linux. |
| `lib/pwrpack.*` | generated: `gen/build_lib.py` | Project symbols (XIAO ESP32-C6, Keystone 3557-2 holder, DMP4015SK3) and footprints (XIAO on two 1×7 sockets, AC10 52 mm, SRP6540, 3557-2, Würth USB-A), with 3D models. |
| `lib/lcsc.*` | `easyeda2kicad` | Raw LCSC downloads that `build_lib.py` converts. The 3D folder is not in git. |
| `out/` | generated, not in git | `expected.json`, KiCad netlist, ERC and DRC reports. |

Every other part uses the stock KiCad 10 libraries.

## Working together over git

- One editor per file. The Linux side regenerates the schematic; the owner owns the board. Don't edit `powerpack.kicad_sch` by hand: the next regeneration overwrites it.
- Close KiCad before `git pull`, reopen after.
- A schematic change: edit `../netlist.md`, run the two scripts below, push. On the laptop: pull, open the board, **Tools → Update PCB from Schematic**. The footprints carry the schematic symbol IDs, so placement and routing are kept.
- `*.kicad_prl` (per-user view state), backups and lock files are in `.gitignore`. `.gitattributes` keeps the KiCad files on LF line endings.

## Commands (Linux box)

```
python3 kicad/gen/gen_sch.py      # netlist.md -> powerpack.kicad_sch
python3 kicad/gen/check_sch.py    # upgrade to the native format, ERC, compare KiCad's netlist with netlist.md
kicad-cli pcb drc --schematic-parity -o kicad/out/drc.rpt kicad/powerpack.kicad_pcb
python3 kicad/gen/build_lib.py    # only when the project library changes
python3 kicad/gen/gen_pcb.py      # only for a fresh board; refuses to overwrite one
python3 kicad/gen/place_pcb.py    # placement pass on an unrouted board: moves parts and labels from its table, checks, writes
python3 kicad/gen/silk_pcb.py     # silkscreen pass: reference label size and the functional labels from its table; text only, safe on a routed board
```

`place_pcb.py` holds the placement table (courtyard centres in mm from the bottom-left corner, y up). It fails without writing if courtyards overlap, a part leaves the board or enters a mounting-hole keep-out, a label has no clear spot, or a neighbour rule is broken (ideal-diode controller by its FET, INA226 by its shunt, buck parts by U_5V, R_CHG 10 mm from the XIAO, the INA226s and the capacitor banks). Add `--dry-run` to check without writing.

### Silkscreen pass

`gen/silk_pcb.py` sets every reference label to 0.8 mm, moves the three in its `MOVE_REF` table (F_IN, F_BAT, D_TVS) and adds the functional labels in its `LABELS` table (polarity and names at the connectors, fuse ratings, output ratings, test-point net names, notes) as board text in a group named `silk_labels`. The functional labels are 1.0 mm or more, JLCPCB's stated minimum height (0.15 mm line width); the reference labels are below it by the owner's choice, to make room, and may print soft. Each label goes to the free spot nearest its wanted position, clear of pads, courtyards, silkscreen lines and other text; the script fails without writing if there is none. It changes only F.Silkscreen text, so it can run on the routed board, and running it again replaces the group. Add `--dry-run` to check without writing. Labels moved by hand in KiCad are overwritten by the next run, so change the table instead.

### First routing pass

`gen/route.sh` routes a placed, unrouted board (done on 2026-11-14):

1. `gen/route_pcb.py zones` draws the power path as top-layer copper zones (J_CAR_P, VIN_CAR, SYS_IN, SYS, LOAD, VBAT, 12V_SW, 12V_OUT, 5V, SW_5V), a GND zone over the whole bottom layer, J_SLA_P as a bottom zone under J_SLA and F_BAT, and a no-copper rule area under the XIAO antenna.
2. `gen/route_pcb.py dsn` exports a copy for the autorouter with finer net classes and track keep-outs over the necks of the pours, so signal tracks cross them on the bottom layer instead of cutting them. The keep-outs are not in the board.
3. Freerouting 1.9.0 routes the signal nets (0.2 mm tracks; 0.6 mm on 5V, XIAO_5V).
4. `gen/route_pcb.py ses` imports the result, adds the tracks in its `MANUAL` list (CHG_F on the bottom at 1.0 mm, the Q_OR2 gate hop, the INA226 Kelvin sense lines, the links under U_OR1 and U_OR2, the G_OUT bus) and refills the zones.

To redo it after a placement change: restore the unrouted board (`git checkout v0.6.0 -- kicad/powerpack.kicad_pcb` or your own unrouted copy), run `place_pcb.py`, then `bash kicad/gen/route.sh`. Run `silk_pcb.py` last: `place_pcb.py` puts the reference labels back at 1.0 mm and the functional labels are not in the v0.6.0 board. From here on, route by hand in KiCad; these scripts refuse a board that already has tracks.

### On the laptop (WSL)

The laptop's WSL has no Linux KiCad. The Windows KiCad 10 binaries run from WSL and do the same job; use them in place of `python3` and `kicad-cli` above for anything that needs `pcbnew` or KiCad itself:

```
K="/mnt/c/Program Files/KiCad/10.0/bin"
"$K/python.exe" kicad/gen/place_pcb.py --dry-run
"$K/python.exe" kicad/gen/silk_pcb.py --dry-run
"$K/kicad-cli.exe" pcb drc --schematic-parity --severity-all -o kicad/out/drc.rpt kicad/powerpack.kicad_pcb
"$K/kicad-cli.exe" pcb render --side top --perspective --rotate "-50,0,0" -o "$(wslpath -w /tmp/3d.png)" kicad/powerpack.kicad_pcb
```

Close the board in KiCad before running anything that writes it. Output paths outside the repository go through `wslpath -w`. `rsvg-convert` is not installed here; `python3 -c "import cairosvg; ..."` converts the exported SVG to PNG.

`gen_sch.py` refuses to write a schematic if a row in `netlist.md` cannot be read, if a pin number and pin name in the table disagree with the KiCad symbol, or if any pin is left without a net or an explicit "open". `check_sch.py` exits non-zero unless every pin matches.

## State on 2026-11-14

- Schematic: 77 parts plus TP1–TP8, H1–H4 and six PWR_FLAGs; 41 nets. ERC clean; netlist matches `netlist.md` pin for pin. Cross-checked net by net against the Flux schematic: identical except that Flux leaves Q_OR2's gate unconnected (see `../flux-log.md`).
- Board: 100 × 70 mm, 2 layers, 4 × M3 at (4, 4), (96, 4), (4, 66), (96, 66), every part placed, first routing pass done (369 track segments, 60 vias, 12 zones), silkscreen pass done (reference labels 0.8 mm, 32 functional labels). DRC: 0 unconnected, 0 shorts, 0 clearance errors, 0 parity errors, 0 courtyard overlaps; 13 "silkscreen clipped by board edge" warnings, all from connector outlines that are meant to reach the edge (J_USBA's shell, and the pin-1 arrows of the three terminal blocks).

## To check on the laptop

1. **Terminal blocks:** J_CAR, J_SLA and J_TEMP are turned 180° so the wire entries face the top edge (seen in a `kicad-cli pcb render`). Pin 1 is now on the right: J_CAR + right, GND left; J_TEMP GND right, DQ middle, 3V3 left. The silkscreen polarity marks under them (`- CAR +`, `- BATT +`, `3V3 DQ GND`) follow these pad nets. Confirm in the 3D viewer, and with a meter on the first board, before trusting the marks.
2. **Footprints drawn from datasheets** (no vendor file): AC10 (52 mm pitch, 1.2 mm holes for 0.8 mm leads), SRP6540 (pads 2.0 × 3.7 mm at ±2.7 mm, read from Bourns' recommended layout), XIAO sockets (rows 15.24 mm apart). Compare with the parts in hand before ordering.
3. **3557-2 holes** are 1.8 mm (from the LCSC footprint); Keystone recommends 1.60 mm. Check against the holder's legs.
4. **J_USBA** overhangs the bottom edge by 4.2 mm, as the generator placed it. Check against the Würth drawing and the case wall whether the shell should stick out that far.
5. **Routing fixes found on review (2026-11-14):** the bottom GND plane narrows to about 1.7 mm on the way to J_CAR pin 2, because the `TEMP_DQ` track crosses the plane from J_TEMP to the XIAO (move it to the top layer, or cross in one short hop); D_TVS pin 2 has a single GND via on a 0.2 mm track (give it a copper patch and 4–6 vias); C_IN5, C_HF5 and C_O1–C_O4 have one or two GND vias each (add two or three at C_IN5 and C_HF5).
6. **Routing, still to do by hand:** thermal vias under Q_OR1, Q_OR2, Q_OUT and U_5V (none yet; U_5V has the footprint's 8); a top-layer GND fill with stitching vias if wanted; fiducials for JLCPCB assembly; tidy the autorouted signal tracks. The power pours follow `blocks/03-layout-brief.md` except where a part's own pads are narrower (the LOAD feed to the buck is 1.6 mm; the VBAT charge leg over F_BAT is 2.1 mm).
