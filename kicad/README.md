# KiCad project

KiCad 10 project for the board: `powerpack.kicad_pro`. Open it in KiCad 10.0.x; the Linux box that generates and checks the files runs 10.0.8, so keep both machines on the same major version.

## Files

| File | Who edits it | What it is |
|---|---|---|
| `powerpack.kicad_sch` | generated: `gen/gen_sch.py` | Schematic, one A2 sheet, one dashed box per module. Every pin carries a net label; there are no wires between parts. **Edit `../netlist.md`, not this file.** |
| `powerpack.kicad_pcb` | the owner, in KiCad | Board. Written once by `gen/gen_pcb.py`, then re-placed on 2026-11-14 by `gen/place_pcb.py` at the owner's request (100 × 70 mm, parts spread out, every label in a clear spot). Edited by hand from here on; `place_pcb.py` refuses to run once the board has tracks. |
| `powerpack.kicad_pro` | KiCad, plus `gen_pcb.py` once | Project settings, net classes (`Power`: 1.5 mm, 0.3 mm clearance, on the power path and GND; `Default`: 0.25 mm, 0.13 mm clearance) and JLCPCB minimums. |
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
```

`place_pcb.py` holds the placement table (courtyard centres in mm from the bottom-left corner, y up). It fails without writing if courtyards overlap, a part leaves the board or enters a mounting-hole keep-out, a label has no clear spot, or a neighbour rule is broken (ideal-diode controller by its FET, INA226 by its shunt, buck parts by U_5V, R_CHG 10 mm from the XIAO, the INA226s and the capacitor banks). Add `--dry-run` to check without writing.

### On the laptop (WSL)

The laptop's WSL has no Linux KiCad. The Windows KiCad 10 binaries run from WSL and do the same job; use them in place of `python3` and `kicad-cli` above for anything that needs `pcbnew` or KiCad itself:

```
K="/mnt/c/Program Files/KiCad/10.0/bin"
"$K/python.exe" kicad/gen/place_pcb.py --dry-run
"$K/kicad-cli.exe" pcb drc --schematic-parity --severity-all -o kicad/out/drc.rpt kicad/powerpack.kicad_pcb
"$K/kicad-cli.exe" pcb render --side top --perspective --rotate "-50,0,0" -o "$(wslpath -w /tmp/3d.png)" kicad/powerpack.kicad_pcb
```

Close the board in KiCad before running anything that writes it. Output paths outside the repository go through `wslpath -w`. `rsvg-convert` is not installed here; `python3 -c "import cairosvg; ..."` converts the exported SVG to PNG.

`gen_sch.py` refuses to write a schematic if a row in `netlist.md` cannot be read, if a pin number and pin name in the table disagree with the KiCad symbol, or if any pin is left without a net or an explicit "open". `check_sch.py` exits non-zero unless every pin matches.

## State on 2026-11-14

- Schematic: 77 parts plus TP1–TP8, H1–H4 and six PWR_FLAGs; 41 nets. ERC clean; netlist matches `netlist.md` pin for pin. Cross-checked net by net against the Flux schematic: identical except that Flux leaves Q_OR2's gate unconnected (see `../flux-log.md`).
- Board: 100 × 70 mm, 2 layers, 4 × M3 at (4, 4), (96, 4), (4, 66), (96, 66), every part placed, unrouted. DRC: 0 parity errors, 0 shorts, 0 courtyard overlaps, 0 silkscreen overlaps; 183 unconnected pads; 13 "silkscreen clipped by board edge" warnings, all from connector outlines that are meant to reach the edge (J_USBA's shell, and the pin-1 arrows of the three terminal blocks).

## To check on the laptop

1. **Terminal blocks:** J_CAR, J_SLA and J_TEMP are turned 180° so the wire entries face the top edge (seen in a `kicad-cli pcb render`). Pin 1 is now on the right: J_CAR + right, GND left; J_TEMP GND right, DQ middle, 3V3 left. Confirm in the 3D viewer.
2. **Footprints drawn from datasheets** (no vendor file): AC10 (52 mm pitch, 1.2 mm holes for 0.8 mm leads), SRP6540 (pads 2.0 × 3.7 mm at ±2.7 mm, read from Bourns' recommended layout), XIAO sockets (rows 15.24 mm apart). Compare with the parts in hand before ordering.
3. **3557-2 holes** are 1.8 mm (from the LCSC footprint); Keystone recommends 1.60 mm. Check against the holder's legs.
4. **J_USBA** overhangs the bottom edge by 4.2 mm, as the generator placed it. Check against the Würth drawing and the case wall whether the shell should stick out that far.
