"""Re-place the footprints already on kicad/powerpack.kicad_pcb and give every reference label a clear spot.

    <KiCad python> kicad/gen/place_pcb.py [--dry-run]

Moves existing footprints only: nets, schematic links, fields and the project file are untouched.
Refuses to run while KiCad has the board open (lock file) or once the board has tracks or zones,
so it cannot disturb a routed board. Use it for placement passes before routing; after that the
board is edited by hand only.

PLACE gives each part's courtyard centre in mm from the board's bottom-left corner (y up), its
rotation (KiCad degrees) and, optionally, the order in which label positions are tried:
  T B R L   horizontal text above / below / right / left of the courtyard
  VR VL     text turned 90 degrees, right / left of the courtyard
  C         centred inside the courtyard (only where no pad is in the way)
The first position that touches no other courtyard, pad, label or the board edge wins.
The run fails (and nothing is written) if any check below fails.
"""
import math, os, sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_pcb import BW, BH, X0, Y0, HOLES, PCB, kpos

MM, NM = pcbnew.ToMM, pcbnew.FromMM
TEXT_H, TEXT_T = 1.0, 0.15   # label height and stroke, mm (JLCPCB minimum is 1.0 / 0.15)
INK = 1.3                    # height of a label's ink, mm
GAP = 0.3                    # label to its own courtyard
CLEAR = 0.15                 # label to anything else
DEFAULT_ORDER = "T B R L VR VL C"

# ref: (cx, cy, rotation[, label order])
PLACE = {
    # mounting holes (labels hidden)
    "H1": (4, 4, 0), "H2": (96, 4, 0), "H3": (4, 66, 0), "H4": (96, 66, 0),
    # top edge: wiring in. Rotation 180 puts the wire entries at the board edge (checked in a 3D render)
    "J_CAR": (13.5, 64.55, 180, "VR"),
    "J_TEMP": (50, 64.55, 180, "VL"),
    "J_SLA": (84.5, 64.55, 180, "VL"),
    # module 1: car input
    "F_IN": (12, 53.8, 0, "T"),
    "C_VIN": (23.6, 60.6, 0, "T"),
    "TP1": (23.6, 66.2, 0, "T"),
    "D_TVS": (31.5, 63.3, 0, "T"),
    "Q_OR1": (28, 54.5, 0, "T"),
    "U_OR1": (28, 49.0, 0, "B"),
    "C_OR1": (23.5, 49.3, 180, "L"),
    "C_SYSIN": (33.5, 50.6, 0, "B"),
    # module 3: monitors
    "R_SNS_IN": (38.5, 54.5, 0, "T"),
    "U_MON_IN": (40, 48, 0, "T"),
    "C_MON1": (46.3, 47.2, 0, "R"),
    "R_SNS_OUT": (52, 41, 270, "VR"),
    "U_MON_OUT": (44.5, 40.5, 0, "T"),
    "C_MON2": (44.5, 36.3, 0, "B"),
    # module 2: battery and charge
    "C_SYS1": (47, 55.8, 0, "R"),
    "C_SYS2": (47, 52.3, 0, "R"),
    "Q_OR2": (59.5, 54.5, 180, "T"),
    "U_OR2": (59.5, 49.5, 0, "B"),
    "C_OR2": (54.6, 49.6, 180, "L B"),
    "F_BAT": (78, 53.8, 180, "T"),
    "F_CHG": (79, 47.3, 0, "R C"),
    "R_CHG": (95, 35, 270, "VL C"),
    # module 6: controller, sense dividers, LEDs
    "J_XIAO": (14, 30, 270, "B C"),
    "C_VC": (6.5, 45.3, 0, "T"), "R_VC2": (12.5, 45.3, 0, "T"), "R_VC1": (18.5, 45.3, 0, "T"),
    "C_VB": (6.5, 41.3, 0, "T"), "R_VB2": (12.5, 41.3, 0, "T"), "R_VB1": (18.5, 41.3, 0, "T"),
    "R_SDA": (30, 23.4, 0, "T"), "R_SCL": (36, 23.4, 0, "T"),
    "R_DQ": (62.5, 62.5, 0, "T"),
    "D_GRN": (4.5, 16.5, 0, "T"), "R_LG": (10.5, 16.5, 0, "T"),
    "D_RED": (4.5, 12, 0, "T"), "R_LR": (10.5, 12, 0, "T"),
    "C_X3": (16, 16.5, 0, "T"), "C_X5": (21, 16.5, 0, "T"), "D_5V": (18.5, 12, 0, "T"),
    # module 8: enable and hold
    "D_IGN": (30, 42.5, 180, "T"), "JP_HOLD": (37.5, 44, 0, "B"),
    "Q_HOLD": (30, 37.5, 0, "T"), "R_HG1": (37.5, 37.5, 0, "T"),
    "D_ZH": (30, 32.5, 0, "T"), "R_HG2": (37.5, 32.5, 0, "T"),
    "Q_HOLDDRV": (30.5, 27.6, 0, "T"), "R_HOLD": (38.2, 27.6, 0, "T"),
    "R_EN1": (34.5, 21.3, 0, "B"), "R_EN2": (41, 21.3, 0, "B"), "C_EN": (46.3, 21.3, 0, "B"),
    # module 5: 5 V buck
    "U_5V": (51.5, 26, 0, "T"),
    "C_HF5": (46.1, 27.2, 90, "T+"),
    "C_IN5": (43.3, 27.2, 90, "B"),
    "C_BOOT": (56.7, 27.3, 90, "T"),
    "R_FBB": (51.5, 21.3, 180, "B"),
    "C_VCC": (57, 22.9, 0, "B"),
    "R_FBT": (51.5, 17.5, 0, "B"),
    "L1": (64, 26.5, 0, "T C"),
    "C_O1": (48, 10.8, 270, "T"), "C_O2": (52.6, 10.8, 270, "T"),
    "C_O3": (57.2, 10.8, 270, "T"), "C_O4": (61.8, 10.8, 270, "T"),
    # module 4: USB-A (bottom edge)
    "J_USBA": (30, 2.8, 0, "T"),
    "C_USB": (30, 12.8, 0, "T"),
    # module 7: 12 V output
    "R_PG": (47, 17.5, 0, "B"), "D_OEN": (40.5, 17.5, 0, "B"),
    "Q_OUT": (74.5, 29, 270, "VL"),
    "R_OG1": (63.5, 37.5, 0, "T"), "C_OG": (69.5, 37.5, 0, "T"),
    "D_ZO": (76, 37.5, 0, "T"), "R_OG2": (83, 37.5, 0, "T"),
    "Q_OUTDRV": (82.5, 33.2, 0, "T"),
    "F_OUT": (83.5, 20, 270, "VR"),
    "J_12V": (72, 7.5, 0, "VR"),
    "C_12V": (72, 17.5, 0, "T"),
    # test points, each on or beside its own net's copper (TP1 VIN_CAR is with module 1)
    "TP2": (57, 45.6, 0, "B"),      # SYS, on the pour's leg to F_CHG
    "TP3": (57, 33.7, 0, "T"),      # LOAD, on the pour
    "TP4": (66, 53.6, 0, "B"),      # VBAT, on the pour
    "TP5": (67.3, 20, 0, "B"),      # 5V, on the pour below L1
    "TP6": (25, 17, 0, "T"),        # 3V3, beside the XIAO
    "TP7": (35.5, 17.3, 0, "B"),    # EN_5V, beside the enable divider
    "TP8": (84.3, 41.8, 0, "T"),    # GND
}

HIDE = {"H1", "H2", "H3", "H4"}  # no silkscreen label
EDGE_PARTS = {"J_USBA", "J_12V"}  # connectors that may overhang the bottom edge
NEAR = [  # (a, b, maximum centre distance in mm): parts that must stay together
    ("U_OR1", "Q_OR1", 7), ("C_OR1", "U_OR1", 6), ("U_OR2", "Q_OR2", 7), ("C_OR2", "U_OR2", 6),
    ("U_MON_IN", "R_SNS_IN", 10), ("C_MON1", "U_MON_IN", 8), ("U_MON_OUT", "R_SNS_OUT", 10),
    ("C_MON2", "U_MON_OUT", 8), ("C_IN5", "U_5V", 9), ("C_HF5", "U_5V", 7), ("C_BOOT", "U_5V", 7),
    ("C_VCC", "U_5V", 8.5), ("R_FBB", "U_5V", 7), ("L1", "U_5V", 14), ("C_EN", "U_5V", 8),
    ("F_IN", "J_CAR", 15), ("F_BAT", "J_SLA", 15), ("F_OUT", "J_12V", 20), ("C_USB", "J_USBA", 12),
]
HOT = ("R_CHG", 10, ["J_XIAO", "U_MON_IN", "U_MON_OUT", "C_SYS1", "C_SYS2", "C_IN5", "C_O1", "C_O2", "C_O3", "C_O4"])


def box(b):
    """KiCad BOX2I -> (x0, y0, x1, y1) in mm, board coordinates, y up."""
    return (MM(b.GetLeft()) - X0, Y0 + BH - MM(b.GetBottom()), MM(b.GetRight()) - X0, Y0 + BH - MM(b.GetTop()))


def crt(fp):
    fp.BuildCourtyardCaches()
    poly = fp.GetCourtyard(pcbnew.F_CrtYd)
    return box(poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False))


def hit(a, b, m=0.0):
    return a[0] - m < b[2] and b[0] - m < a[2] and a[1] - m < b[3] and b[1] - m < a[3]


def gap(a, b):
    dx = max(a[0] - b[2], b[0] - a[2], 0)
    dy = max(a[1] - b[3], b[1] - a[3], 0)
    return math.hypot(dx, dy)


def main():
    dry = "--dry-run" in sys.argv
    lock = os.path.join(os.path.dirname(PCB), "~" + os.path.basename(PCB) + ".lck")
    if os.path.exists(lock):
        raise SystemExit("KiCad has the board open (lock file). Save and close it first.")
    board = pcbnew.LoadBoard(PCB)
    if len(board.GetTracks()) or board.GetAreaCount():
        raise SystemExit("The board has tracks or zones: it is routed. Edit placement by hand in KiCad.")
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    errors = [f"not on the board: {r}" for r in PLACE if r not in fps] + \
             [f"no placement for: {r}" for r in fps if r not in PLACE]
    if errors:
        raise SystemExit("\n".join(errors))
    before = {r: crt(f) for r, f in fps.items()}

    # --- move the parts
    for ref, spec in PLACE.items():
        fp = fps[ref]
        fp.SetOrientationDegrees(spec[2])
        c = crt(fp)
        dx, dy = spec[0] - (c[0] + c[2]) / 2, spec[1] - (c[1] + c[3]) / 2
        fp.Move(pcbnew.VECTOR2I(NM(dx), NM(-dy)))
    cy = {r: crt(f) for r, f in fps.items()}
    pads = {r: [box(p.GetBoundingBox()) for p in f.Pads()] for r, f in fps.items()}

    # --- outline
    # (the four existing Edge.Cuts lines are re-used: removing board items through SWIG is unreliable)
    edges = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    if len(edges) != 4:
        raise SystemExit(f"expected 4 outline segments on Edge.Cuts, found {len(edges)}")
    pts = [(0, 0), (BW, 0), (BW, BH), (0, BH)]
    for i, seg in enumerate(edges):
        seg.SetStart(kpos(*pts[i]))
        seg.SetEnd(kpos(*pts[(i + 1) % 4]))

    # --- checks on the parts
    refs = sorted(fps)
    for i, a in enumerate(refs):
        A = cy[a]
        if a not in EDGE_PARTS and (A[0] < -0.01 or A[1] < -0.01 or A[2] > BW + 0.01 or A[3] > BH + 0.01):
            errors.append(f"{a}: courtyard leaves the board ({A[0]:.2f}, {A[1]:.2f}, {A[2]:.2f}, {A[3]:.2f})")
        if not a.startswith("H"):
            for h, (hx, hy) in HOLES.items():
                nx, ny = min(max(hx, A[0]), A[2]), min(max(hy, A[1]), A[3])
                if math.hypot(nx - hx, ny - hy) < 3.25:
                    errors.append(f"{a}: inside the keep-out of {h}")
        for b in refs[i + 1:]:
            if hit(A, cy[b]):
                errors.append(f"courtyards overlap: {a} / {b}")
    for a, b, lim in NEAR:
        d = math.hypot((cy[a][0] + cy[a][2] - cy[b][0] - cy[b][2]) / 2, (cy[a][1] + cy[a][3] - cy[b][1] - cy[b][3]) / 2)
        if d > lim:
            errors.append(f"{a} is {d:.1f} mm from {b} (limit {lim})")
    for r in HOT[2]:
        d = gap(cy[HOT[0]], cy[r])
        if d < HOT[1]:
            errors.append(f"{r} is {d:.1f} mm from {HOT[0]} (keep {HOT[1]})")

    # --- labels
    placed = {}
    chosen = {}
    for ref in PLACE:
        fp, C = fps[ref], cy[ref]
        t = fp.Reference()
        if ref in HIDE:
            t.SetVisible(False)
            continue
        t.SetVisible(True)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(NM(TEXT_H), NM(TEXT_H)))
        t.SetTextThickness(NM(TEXT_T))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        t.SetKeepUpright(True)
        order = (PLACE[ref][3] if len(PLACE[ref]) > 3 else DEFAULT_ORDER).replace("+", "").split()
        order += [s for s in DEFAULT_ORDER.split() if s not in order]
        mx, my = (C[0] + C[2]) / 2, (C[1] + C[3]) / 2
        for side, extra in [(s, e) for e in (0, 0.5, 1.0) for s in order if e == 0 or s != "C"]:
            vert = side in ("VR", "VL")
            t.SetTextAngleDegrees(90 if vert else 0)
            t.SetPosition(kpos(mx, my))
            b = box(t.GetBoundingBox())
            # KiCad's text box is 1.7 x the text height; the ink (with the underscore) is about 1.3
            w, h = (INK, b[3] - b[1]) if vert else (b[2] - b[0], INK)
            d = GAP + extra
            x, y = {"T": (mx, C[3] + d + h / 2), "B": (mx, C[1] - d - h / 2),
                    "R": (C[2] + d + w / 2, my), "VR": (C[2] + d + w / 2, my),
                    "L": (C[0] - d - w / 2, my), "VL": (C[0] - d - w / 2, my), "C": (mx, my)}[side]
            t.SetPosition(kpos(x, y))
            L = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            ok = L[0] >= 0.5 and L[1] >= 0.5 and L[2] <= BW - 0.5 and L[3] <= BH - 0.5
            ok = ok and not any(hit(L, cy[o], CLEAR) for o in cy if o != ref)
            ok = ok and not any(hit(L, p, CLEAR) for o in pads for p in pads[o] if o == ref or side == "C")
            ok = ok and not any(hit(L, q, CLEAR) for q in placed.values())
            if ok:
                placed[ref], chosen[ref] = L, side + ("+" if extra else "")
                break
        else:
            errors.append(f"{ref}: no clear spot for its label (tried {' '.join(order)})")

    moved = sorted(((math.hypot((cy[r][0] + cy[r][2] - before[r][0] - before[r][2]) / 2,
                                (cy[r][1] + cy[r][3] - before[r][1] - before[r][3]) / 2), r) for r in fps), reverse=True)
    print(f"{len(fps)} parts placed on {BW:g} x {BH:g} mm; {sum(1 for d, _ in moved if d > 0.05)} moved")
    want = {r: PLACE[r][3].split()[0] for r in chosen if len(PLACE[r]) > 3}  # "T+": T, one step further out
    off = [f"{r}:{s}" for r, s in sorted(chosen.items()) if s != want.get(r, "T")]
    print("labels not in their first-choice spot:", " ".join(off) or "none")
    if errors:
        print(f"\n{len(errors)} problem(s); board not written:")
        for e in errors:
            print("  " + e)
        if "--force" not in sys.argv:
            raise SystemExit(1)
    if dry:
        print("dry run: board not written")
        return
    pcbnew.SaveBoard(PCB, board, True)
    print("wrote", PCB)


if __name__ == "__main__":
    main()
