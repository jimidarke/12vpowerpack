"""Create kicad/powerpack.kicad_pcb: outline, mounting holes and every footprint pre-placed.

    python3 kicad/gen/gen_pcb.py [--force]

Run once, after gen_sch.py and check_sch.py (it reads kicad/out/powerpack.net). The board then
belongs to the owner: this refuses to overwrite an existing board unless --force is given.
Later schematic changes reach the board through "Update PCB from Schematic" in KiCad; the
footprints carry the schematic symbol IDs, so that keeps placement and routing.

Positions come from blocks/04-placement-gen.py (part centres, mm from the board's bottom-left
corner, y up). Each footprint is centred on its outline (pads and graphics, not text).
"""
import os, re, runpy, sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexpr
from sexpr import find, findall

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(KICAD, ".."))
PCB = os.path.join(KICAD, "powerpack.kicad_pcb")
STOCK_FP = "/usr/share/kicad/footprints"
BW, BH = 100.0, 80.0
X0, Y0 = 50.0, 50.0  # board top-left on the KiCad page

# Rotations (degrees, KiCad: positive = counter-clockwise on screen) from the placement notes.
ROT = {
    "J_XIAO": 270,     # USB-C end to the right, antenna end at the left edge
    "R_CHG": 270,      # pad 1 (CHG_F) at the top, pad 2 (VBAT) at the bottom
    "F_OUT": 270,      # 12V_SW clip at the top, 12V_OUT clip at the bottom
    "R_SNS_OUT": 270,  # SYS at the top, LOAD at the bottom
    "Q_OUT": 270,      # drain tab toward the bottom (F_OUT)
    "F_BAT": 180,      # J_SLA_P clip on the right (toward J_SLA), VBAT clip on the left
    "D_IGN": 180,      # anode (VIN_CAR) on the left
    "D_TVS": 90,       # pads along y: the 9 mm gap between F_IN and Q_OR1 is too narrow lengthways
    "C_SYSIN": 90,     # in the 2.5 mm gap between Q_OR1 and R_SNS_IN
}
# Parts not in the placement plan.
EXTRA = {f"TP{i + 1}": (80 + 4 * (i % 2), 50 - 4 * (i // 2)) for i in range(8)}
HOLES = {"H1": (4, 4), "H2": (96, 4), "H3": (4, 76), "H4": (96, 76)}
NOT_PLACED = re.compile(r"^(TP\d+|JP_.*|H\d+)$")  # no pick-and-place, no BOM line

POWER_NETS = ["J_CAR_P", "VIN_CAR", "SYS_IN", "SYS", "LOAD", "J_SLA_P", "VBAT", "12V_SW", "12V_OUT", "GND"]


def placement():
    """Run the placement generator's table without writing its outputs."""
    src = open(os.path.join(REPO, "blocks", "04-placement-gen.py"), encoding="utf-8").read()
    src = src.split("# --- overlap check")[0].replace("OUT_SVG, OUT_MD = sys.argv[1], sys.argv[2]", "")
    ns = {}
    exec(compile(src, "04-placement-gen.py", "exec"), ns)
    return {p[0]: (p[1], p[2]) for p in ns["P"]}


def kpos(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(X0 + x), pcbnew.FromMM(Y0 + BH - y))


def load_fp(fpid):
    lib, name = fpid.split(":", 1)
    local = os.path.join(KICAD, "lib", lib + ".pretty")
    path = local if os.path.isdir(local) else os.path.join(STOCK_FP, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise SystemExit(f"footprint not found: {fpid}")
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def body_centre(fp):
    """Centre of pads and graphics (not text), in board units."""
    box = None
    for item in list(fp.Pads()) + [g for g in fp.GraphicalItems() if g.GetClass() != "PCB_TEXT"]:
        if item.GetClass() == "PCB_SHAPE" and item.GetLayerName() not in ("F.Fab", "F.CrtYd", "F.SilkS"):
            continue
        b = item.GetBoundingBox()
        if box is None:
            box = b
        else:
            box.Merge(b)
    return box.GetCenter()


# Parts that stay exactly where the placement plan puts them; everything else may be nudged.
FIXED = re.compile(r"^(J_.*|F_.*|R_CHG|R_SNS_.*|Q_OUT|Q_OR\d|U_.*|L1|H\d+)$")
GAP = pcbnew.FromMM(0.2)


def courtyard(fp):
    fp.BuildCourtyardCaches()
    poly = fp.GetCourtyard(pcbnew.F_CrtYd)
    b = poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False)
    return b.GetLeft() - GAP // 2, b.GetTop() - GAP // 2, b.GetRight() + GAP // 2, b.GetBottom() + GAP // 2


def nudge(board):
    """Push movable parts off any courtyard they overlap, along the shorter way out."""
    fps = [f for f in board.GetFootprints()]
    start = {f.GetReference(): f.GetPosition() for f in fps}
    for _ in range(1000):
        changed = False
        boxes = {f.GetReference(): courtyard(f) for f in fps}
        for i, a in enumerate(fps):
            for b in fps[i + 1:]:
                ra, rb = a.GetReference(), b.GetReference()
                A, B = boxes[ra], boxes[rb]
                ox = min(A[2], B[2]) - max(A[0], B[0])
                oy = min(A[3], B[3]) - max(A[1], B[1])
                if ox <= 0 or oy <= 0:
                    continue
                fa, fb = FIXED.match(ra), FIXED.match(rb)
                if fa and fb:
                    continue
                area = lambda r: (boxes[r][2] - boxes[r][0]) * (boxes[r][3] - boxes[r][1])
                mover, other = (b, a) if fa or (not fb and area(rb) <= area(ra)) else (a, b)
                M, O = boxes[mover.GetReference()], boxes[other.GetReference()]
                step = pcbnew.FromMM(0.05)
                if ox < oy:
                    d = ox + step if (M[0] + M[2]) >= (O[0] + O[2]) else -(ox + step)
                    mover.Move(pcbnew.VECTOR2I(int(d), 0))
                else:
                    d = oy + step if (M[1] + M[3]) >= (O[1] + O[3]) else -(oy + step)
                    mover.Move(pcbnew.VECTOR2I(0, int(d)))
                boxes[mover.GetReference()] = courtyard(mover)
                changed = True
        if not changed:
            break
    moved = {}
    for f in fps:
        d = f.GetPosition() - start[f.GetReference()]
        if d.x or d.y:
            moved[f.GetReference()] = (pcbnew.ToMM(d.x), -pcbnew.ToMM(d.y))
    return moved


def patch_project():
    """Net classes and JLCPCB-compatible minimums in powerpack.kicad_pro (KiCad wrote its defaults)."""
    import json
    pro = os.path.join(KICAD, "powerpack.kicad_pro")
    d = json.load(open(pro))
    ns = d["net_settings"]
    default = next(c for c in ns["classes"] if c["name"] == "Default")
    default.update(clearance=0.13, track_width=0.25, via_diameter=0.6, via_drill=0.3)
    power = dict(default, name="Power", clearance=0.3, track_width=1.5, via_diameter=0.8, via_drill=0.4,
                 priority=0)
    ns["classes"] = [default, power]
    ns["netclass_patterns"] = [{"netclass": "Power", "pattern": n} for n in POWER_NETS]
    r = d["board"]["design_settings"]["rules"]
    r.update(min_clearance=0.127, min_track_width=0.127, min_via_diameter=0.45, min_through_hole_diameter=0.3,
             min_copper_edge_clearance=0.3, min_hole_clearance=0.25, min_hole_to_hole=0.25)
    with open(pro, "w", newline="\n") as f:
        json.dump(d, f, indent=2)
        f.write("\n")


def main():
    if os.path.exists(PCB) and "--force" not in sys.argv:
        raise SystemExit(f"{PCB} exists; it belongs to the owner now. Use --force to overwrite.")
    net_file = os.path.join(KICAD, "out", "powerpack.net")
    tree = sexpr.parse(open(net_file, encoding="utf-8").read())

    board = pcbnew.NewBoard(PCB)
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()

    # nets
    pad_net = {}
    netinfo = {}
    for n in findall(find(tree, "nets"), "net"):
        name = find(n, "name")[1]
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
        for node in findall(n, "node"):
            pad_net[(find(node, "ref")[1], find(node, "pin")[1])] = ni

    pos = placement()
    pos.update(EXTRA)
    pos.update(HOLES)
    missing = []
    for comp in findall(find(tree, "components"), "comp"):
        ref = find(comp, "ref")[1]
        fpid = find(comp, "footprint")[1]
        value = find(comp, "value")[1]
        fields = {find(f, "name")[1]: (f[2] if len(f) > 2 else "") for f in findall(find(comp, "fields") or [], "field")}
        tstamp = find(comp, "tstamps")[1]
        fp = load_fp(fpid)
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetPath(pcbnew.KIID_PATH("/" + tstamp))
        for k in ("Description", "LCSC", "MPN", "Fit"):
            if fields.get(k):
                fp.SetField(k, fields[k])
                f = fp.GetField(k)
                if f:
                    f.SetVisible(False)
        if NOT_PLACED.match(ref):
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
        for pad in fp.Pads():
            ni = pad_net.get((ref, pad.GetNumber()))
            if ni:
                pad.SetNet(ni)
        board.Add(fp)
        fp.SetOrientationDegrees(ROT.get(ref, 0))
        if ref not in pos:
            missing.append(ref)
            xy = (110, 40)
        else:
            xy = pos[ref]
        target = kpos(*xy)
        fp.SetPosition(target)
        c = body_centre(fp)
        fp.Move(pcbnew.VECTOR2I(target.x - c.x, target.y - c.y))

    moved = nudge(board)

    # outline
    pts = [(0, 0), (BW, 0), (BW, BH), (0, BH)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(0.1))
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % 4]
        seg.SetStart(kpos(ax, ay))
        seg.SetEnd(kpos(bx, by))
        board.Add(seg)

    # title block
    tb = board.GetTitleBlock()
    tb.SetTitle("12 V vehicle UPS power board")
    tb.SetRevision(open(os.path.join(REPO, "VERSION.txt")).readline().strip())
    tb.SetComment(0, "Board 100 x 80 mm, 2 layers. Pre-placed from blocks/04-placement-gen.py")

    pcbnew.SaveBoard(PCB, board)
    patch_project()
    print(f"wrote {PCB}: {len(list(board.GetFootprints()))} footprints, {len(netinfo)} nets")
    if moved:
        print("small parts nudged off their neighbours (mm, board coordinates y up):")
        for ref, (dx, dy) in sorted(moved.items()):
            print(f"  {ref}: {dx:+.2f}, {dy:+.2f}")
    if missing:
        print("not in the placement plan (parked right of the board):", ", ".join(missing))


if __name__ == "__main__":
    main()
