# KiCad project

KiCad 10 project for the board: `powerpack.kicad_pro`. Open it in KiCad 10.0.x; the Linux box that generates and checks the files runs 10.0.8, so keep both machines on the same major version.

## Files

| File | Who edits it | What it is |
|---|---|---|
| `powerpack.kicad_sch` | generated: `gen/gen_sch.py` | Schematic, one A2 sheet, one dashed box per module. Every pin carries a net label; there are no wires between parts. **Edit `../netlist.md`, not this file.** |
| `powerpack.kicad_pcb` | the owner, in KiCad | Board. Written once by `gen/gen_pcb.py` with every part pre-placed from `../blocks/04-placement-gen.py`; from then on it is edited by hand only. |
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
```

`gen_sch.py` refuses to write a schematic if a row in `netlist.md` cannot be read, if a pin number and pin name in the table disagree with the KiCad symbol, or if any pin is left without a net or an explicit "open". `check_sch.py` exits non-zero unless every pin matches.

## State on 2026-11-14

- Schematic: 77 parts plus TP1–TP8, H1–H4 and six PWR_FLAGs; 41 nets. ERC clean; netlist matches `netlist.md` pin for pin. Cross-checked net by net against the Flux schematic: identical except that Flux leaves Q_OR2's gate unconnected (see `../flux-log.md`).
- Board: 100 × 80 mm, 2 layers, 4 × M3, every part placed, unrouted. DRC: 0 parity errors, 0 shorts, 0 courtyard overlaps; 183 unconnected pads and silkscreen warnings.

## To check on the laptop

1. **Terminal blocks:** in the 3D viewer, check that the wire entries of J_CAR, J_SLA and J_TEMP face the top edge. If not, turn them 180°.
2. **Footprints drawn from datasheets** (no vendor file): AC10 (52 mm pitch, 1.2 mm holes for 0.8 mm leads), SRP6540 (pads 2.0 × 3.7 mm at ±2.7 mm, read from Bourns' recommended layout), XIAO sockets (rows 15.24 mm apart). Compare with the parts in hand before ordering.
3. **3557-2 holes** are 1.8 mm (from the LCSC footprint); Keystone recommends 1.60 mm. Check against the holder's legs.
