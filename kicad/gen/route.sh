#!/bin/bash
# First routing pass: zones -> dsn -> Freerouting -> ses -> DRC summary.
# Run from the repository root (WSL on the laptop) on a placed, unrouted board, with KiCad closed.
# Needs kicad/out/route/freerouting-1.9.0.jar (github.com/freerouting/freerouting, release v1.9.0) and Java 17+.
# Freerouting opens a window while it runs (about 30 s) and closes it itself. -da turns its analytics off.
set -e
K="/mnt/c/Program Files/KiCad/10.0/bin"
"$K/python.exe" kicad/gen/route_pcb.py zones 2>&1 | tail -1
"$K/python.exe" kicad/gen/route_pcb.py dsn 2>&1 | tail -1
(cd kicad/out/route && rm -f powerpack.ses && timeout 560 "/mnt/c/Program Files/Java/jdk-20/bin/java.exe" -jar freerouting-1.9.0.jar -de powerpack.dsn -do powerpack.ses -mp 40 -inc Skip -da -dct 0 > fr.log 2>&1)
"$K/python.exe" kicad/gen/route_pcb.py ses 2>&1 | grep -v "image handler" | tail -1
"$K/kicad-cli.exe" pcb drc --schematic-parity --severity-all -o kicad/out/drc.rpt kicad/powerpack.kicad_pcb 2>&1 | tail -3 | head -2
grep -E "^\[" kicad/out/drc.rpt | sed -E 's/^\[([a-z_]+)\].*/\1/' | sort | uniq -c
grep -A3 -E "^\[(unconnected|clearance|shorting|tracks_cross|zones|hole|copper_edge|via|track)" kicad/out/drc.rpt | grep -E "@" | sed -E 's/^ +@\(([0-9.]+) mm, ([0-9.]+) mm\): /\1,\2 /' | paste - - | cut -c1-170
