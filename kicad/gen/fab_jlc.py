#!/usr/bin/env python3
"""JLCPCB fabrication files: Gerbers and drill files (zipped), BOM and CPL.

Reads the schematic and the board; writes only into kicad/out/jlcpcb/.

- Gerbers: the nine layers of a 2-layer board, Protel extensions, drill files in mm
  (PTH and NPTH separate, oval holes in the alternate mode), zipped for upload.
- BOM: the symbols whose Fit field is "fab", grouped by LCSC number, in JLCPCB's
  columns (Comment, Designator, Footprint, LCSC Part #).
- CPL: the placement file filtered to the BOM designators, in JLCPCB's columns
  (Designator, Mid X, Mid Y, Layer, Rotation), in mm.

Rotations are KiCad's. When JLCPCB's placement preview shows a part turned, add the
correction to ROT_OFFSET (degrees added to KiCad's angle, by designator) and run again.

Runs with the Linux kicad-cli if it is on PATH, otherwise with the Windows KiCad 10
binary from WSL. Paths given to kicad-cli are relative to the repository, so both work.

    python3 kicad/gen/fab_jlc.py
"""
import csv
import os
import shutil
import subprocess
import sys
import zipfile
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCH = "kicad/powerpack.kicad_sch"
PCB = "kicad/powerpack.kicad_pcb"
OUT = "kicad/out/jlcpcb"

LAYERS = "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"

# Degrees added to KiCad's rotation for JLCPCB, by designator. Empty until JLCPCB's
# preview has been checked; record what it showed and the order it was seen on.
ROT_OFFSET = {}

WIN_CLI = "/mnt/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"


def cli():
    if shutil.which("kicad-cli"):
        return "kicad-cli"
    if os.path.exists(WIN_CLI):
        return WIN_CLI
    raise SystemExit("no kicad-cli found (Linux or Windows KiCad 10)")


def run(*args):
    r = subprocess.run([cli(), *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit(f"failed: kicad-cli {' '.join(args)}")
    return r


def ref(s):
    # KiCad shows a reference with no trailing number as unannotated ("D_GRN?").
    return s.rstrip("?")


def main():
    out = os.path.join(ROOT, OUT)
    if os.path.isdir(out):
        shutil.rmtree(out)
    gdir = os.path.join(out, "gerbers")
    os.makedirs(gdir)

    # Gerbers and drill files
    run("pcb", "export", "gerbers", "--layers", LAYERS, "--no-x2", "-o", f"{OUT}/gerbers/", PCB)
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm",
        "--excellon-separate-th", "--excellon-oval-format", "alternate",
        "--generate-map", "--map-format", "gerberx2", "-o", f"{OUT}/gerbers/", PCB)
    zpath = os.path.join(out, "powerpack-gerbers.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(gdir)):
            z.write(os.path.join(gdir, f), f)
    gerbers = sorted(os.listdir(gdir))

    # BOM from the schematic, one row per symbol
    raw = os.path.join(out, "bom_raw.csv")
    run("sch", "export", "bom", "--fields", "Reference,Value,Footprint,LCSC,MPN,Fit",
        "--labels", "Ref,Value,Footprint,LCSC,MPN,Fit", "--ref-range-delimiter", "",
        "-o", f"{OUT}/bom_raw.csv", SCH)
    rows = list(csv.DictReader(open(raw, encoding="utf-8")))
    os.remove(raw)
    fab = [r for r in rows if r["Fit"] == "fab"]
    bad = [ref(r["Ref"]) for r in fab if not r["LCSC"].startswith("C")]
    if bad:
        raise SystemExit(f"fab parts without an LCSC number: {', '.join(bad)}")

    # One line per LCSC number. The schematic value can differ between symbols that
    # share a part (100nF 16V and 100nF 50V are both C14663); then the comment is the MPN.
    groups = OrderedDict()
    for r in sorted(fab, key=lambda r: (r["LCSC"], ref(r["Ref"]))):
        groups.setdefault(r["LCSC"], []).append(r)
    with open(os.path.join(out, "powerpack-bom.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for lcsc, rs in groups.items():
            fps = {r["Footprint"].split(":")[-1] for r in rs}
            if len(fps) > 1:
                raise SystemExit(f"{lcsc} on more than one footprint: {', '.join(sorted(fps))}")
            values = {r["Value"] for r in rs}
            comment = rs[0]["Value"] if len(values) == 1 else (rs[0]["MPN"] or " / ".join(sorted(values)))
            w.writerow([comment, ",".join(ref(r["Ref"]) for r in rs), fps.pop(), lcsc])
    bom_refs = {ref(r["Ref"]) for r in fab}

    # CPL from the board, filtered to the BOM
    pos = os.path.join(out, "pos_raw.csv")
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
        "-o", f"{OUT}/pos_raw.csv", PCB)
    prow = {r["Ref"]: r for r in csv.DictReader(open(pos, encoding="utf-8"))}
    os.remove(pos)
    missing = sorted(bom_refs - prow.keys())
    if missing:
        raise SystemExit(f"BOM parts not on the board: {', '.join(missing)}")
    bottom = sorted(r for r in bom_refs if prow[r]["Side"] != "top")
    if bottom:
        raise SystemExit(f"fab parts on the bottom side: {', '.join(bottom)}")
    unknown = sorted(set(ROT_OFFSET) - bom_refs)
    if unknown:
        raise SystemExit(f"ROT_OFFSET names parts not in the BOM: {', '.join(unknown)}")
    with open(os.path.join(out, "powerpack-cpl.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in sorted(bom_refs):
            p = prow[r]
            rot = (float(p["Rot"]) + ROT_OFFSET.get(r, 0)) % 360
            w.writerow([r, f"{float(p['PosX']):.4f}mm", f"{float(p['PosY']):.4f}mm",
                        "Top", f"{rot:g}"])

    print(f"gerbers: {len(gerbers)} files -> {OUT}/powerpack-gerbers.zip")
    print(f"BOM: {len(groups)} lines, {len(fab)} parts -> {OUT}/powerpack-bom.csv")
    print(f"CPL: {len(bom_refs)} parts -> {OUT}/powerpack-cpl.csv")
    other = sorted(ref(r["Ref"]) for r in rows if r["Fit"] != "fab")
    print(f"not fitted by JLCPCB ({len(other)}): {', '.join(other)}")


if __name__ == "__main__":
    sys.exit(main())
