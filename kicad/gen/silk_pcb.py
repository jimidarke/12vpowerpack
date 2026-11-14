"""Silkscreen pass: smaller reference labels, plus functional labels for build, test and use.

    python kicad/gen/silk_pcb.py [--dry-run]      (KiCad's Python; close the board in KiCad first)

Touches only F.Silkscreen text. Tracks, zones, pads and footprint positions are not changed.

1. Every visible reference label becomes REF_H mm high (was 1.0), in place. That is below JLCPCB's
   stated minimum of 1.0 mm; the functional labels stay at 1.0 mm or more.
2. The labels in MOVE_REF go to a new spot (they sat where a polarity mark has to go).
3. The labels in LABELS are added as board text in a group named GROUP. Running again removes
   that group first, so the script can be re-run after editing the table.

Coordinates are mm from the bottom-left board corner, y up (as in place_pcb.py). Each label is
put at the free spot nearest its wanted position: clear of pads, courtyards, silkscreen lines,
other text and the board edge. The script fails without writing if a label has no free spot
within its search radius.
"""
import math, os, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.normpath(os.path.join(HERE, "..", "powerpack.kicad_pcb"))
BW, BH, X0, Y0 = 100.0, 70.0, 50.0, 50.0
MM, NM = pcbnew.ToMM, pcbnew.FromMM
GROUP = "silk_labels"
REF_H, REF_T = 0.8, 0.15     # reference labels: height, line width. Below JLCPCB's stated 1.0 mm minimum height
                             # (capabilities page, read 2026-11-14), the owner's choice to make room; they may print soft.
MIN_H = 1.0                  # functional labels: never below JLCPCB's minimum
CLEAR = 0.15                 # label to anything else
EDGE = 0.4                   # label to board edge

MOVE_REF = {"F_IN": (4.3, 58.35), "F_BAT": (71.4, 58.35), "D_TVS": (32.5, 59.1)}

# (text, x, y, height, options). Options: rot=90, glyph=0.7 (a lone + or -: ink is that fraction of the height), r=search radius (default 2.5), lockx=True
# (search up and down only), inside="REF" (may sit inside that part's outline), thick=line width.
LABELS = [
    # car input: J_CAR pin 2 (left) is GND, pin 1 (right) is +
    ("-", 11.0, 58.35, 1.5, dict(lockx=True, r=0.6, thick=0.25, glyph=0.7)),
    ("CAR", 13.5, 58.35, 1.0, dict(r=0.6)),
    ("+", 16.0, 58.35, 1.5, dict(lockx=True, r=0.6, thick=0.25, glyph=0.7)),
    ("10A", 7.8, 58.35, 1.0, dict(r=1.0)),
    # battery: J_SLA pin 2 (left) is GND, pin 1 (right) is +
    ("-", 81.6, 58.35, 1.5, dict(lockx=True, r=0.6, thick=0.25, glyph=0.7)),
    ("BATT", 84.5, 58.35, 1.0, dict(r=0.6)),
    ("+", 87.4, 58.35, 1.5, dict(lockx=True, r=0.6, thick=0.25, glyph=0.7)),
    ("10A", 75.4, 58.35, 1.0, dict(r=1.0)),
    ("12V AGM ONLY >", 71.0, 66.5, 1.0, {}),
    # temperature probe: J_TEMP pin 3, 2, 1 from the left
    ("3V3", 45.0, 58.5, 1.0, dict(lockx=True, r=0.8)),
    ("DQ", 50.0, 58.5, 1.0, dict(lockx=True, r=0.8)),
    ("GND", 55.0, 58.5, 1.0, dict(lockx=True, r=0.8)),
    ("< DS18B20 PROBE", 64.8, 68.5, 1.0, {}),
    # outputs
    ("12V OUT", 86.0, 8.0, 1.2, {}),
    ("3A  5A PEAK", 86.0, 6.1, 1.0, {}),
    ("CENTRE +", 86.0, 4.3, 1.0, {}),
    ("7.5A", 87.85, 15.0, 1.0, dict(rot=90)),
    ("USB 5V OUT", 14.5, 8.6, 1.0, {}),
    ("1.6A T", 87.5, 45.7, 1.0, {}),
    # board identity and notes
    ("12V VEHICLE UPS", 14.5, 5.3, 1.0, dict(r=1.0)),
    ("REV 0.8", 14.5, 3.4, 1.0, dict(r=1.0)),
    ("XIAO ESP32-C6", 13.5, 30.0, 1.0, dict(inside="J_XIAO")),
    ("HOT!", 89.6, 28.0, 1.0, dict(rot=90, thick=0.2)),
    ("JP_HOLD: CLOSE IF NO XIAO", 70.0, 42.2, 1.0, dict(r=4.0)),
    # test point nets (netlist.md, module 8): placed beside each pad
    ("VIN_CAR", 28.4, 68.45, 1.0, dict(r=1.0)),
    ("SYS", "TP2", None, 1.0, dict(r=4.5)),
    ("LOAD", "TP3", None, 1.0, dict(r=4.5)),
    ("VBAT", "TP4", None, 1.0, dict(r=4.5)),
    ("5V", "TP5", None, 1.0, dict(r=4.5)),
    ("3V3", 25.0, 14.8, 1.0, dict(r=1.0)),
    ("EN_5V", "TP7", None, 1.0, dict(r=4.5)),
    ("GND", "TP8", None, 1.0, dict(r=4.5)),
]


def box(b, shrink=0.0):
    """KiCad BOX2I -> (x0, y0, x1, y1) in mm, board coordinates, y up."""
    return (MM(b.GetLeft()) - X0 + shrink, Y0 + BH - MM(b.GetBottom()) + shrink,
            MM(b.GetRight()) - X0 - shrink, Y0 + BH - MM(b.GetTop()) - shrink)


def tbox(t):
    """Ink box of a text item: KiCad's box carries about a quarter of the height as padding."""
    return box(t.GetBoundingBox(), 0.25 * MM(t.GetTextHeight()))


def ink(t, o):
    """tbox, or for a single + or - a square of o["glyph"] x height: those glyphs are much smaller than their box."""
    if "glyph" not in o:
        return tbox(t)
    c, d = t.GetPosition(), o["glyph"] * MM(t.GetTextHeight()) / 2
    x, y = MM(c.x) - X0, Y0 + BH - MM(c.y)
    return (x - d, y - d, x + d, y + d)


def hit(a, b, m=0.0):
    return a[0] - m < b[2] and b[0] - m < a[2] and a[1] - m < b[3] and b[1] - m < a[3]


def pos(x, y):
    return pcbnew.VECTOR2I(NM(X0 + x), NM(Y0 + BH - y))


def style(t, h, thick):
    t.SetTextSize(pcbnew.VECTOR2I(NM(h), NM(h)))
    t.SetTextThickness(NM(thick))


def main():
    dry = "--dry-run" in sys.argv
    lock = os.path.join(os.path.dirname(PCB), "~" + os.path.basename(PCB) + ".lck")
    if os.path.exists(lock):
        raise SystemExit("KiCad has the board open (lock file). Save and close it first.")
    board = pcbnew.LoadBoard(PCB)

    old = [d for d in board.GetDrawings() if d.GetParentGroup() and d.GetParentGroup().GetName() == GROUP]
    for g in [g for g in board.Groups() if g.GetName() == GROUP]:
        g.RemoveAll()
        board.Remove(g)
    for d in old:
        board.Remove(d)

    # 1, 2: reference labels
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for ref, f in fps.items():
        r = f.Reference()
        if r.IsVisible() and r.GetLayer() == pcbnew.F_SilkS:
            style(r, REF_H, REF_T)
            if ref in MOVE_REF:
                r.SetPosition(pos(*MOVE_REF[ref]))

    # obstacles: (owner, kind, box)
    obs = []
    for ref, f in fps.items():
        f.BuildCourtyardCaches()
        c = f.GetCourtyard(pcbnew.F_CrtYd)
        if c.OutlineCount():
            obs.append((ref, "courtyard", box(c.BBox())))
        for p in f.Pads():
            obs.append((ref, "pad", box(p.GetBoundingBox())))
        if f.Reference().IsVisible():
            obs.append((ref, "label", tbox(f.Reference())))
        for g in f.GraphicalItems():
            if g.GetLayer() != pcbnew.F_SilkS:
                continue
            if g.GetClass() == "PCB_TEXT":
                obs.append((ref, "text", tbox(g)))
            elif g.GetShape() == pcbnew.SHAPE_T_RECT:   # outline only, the inside is free
                x0, y0, x1, y1 = box(g.GetBoundingBox())
                w = MM(g.GetWidth())
                for e in ((x0, y0, x1, y0 + w), (x0, y1 - w, x1, y1), (x0, y0, x0 + w, y1), (x1 - w, y0, x1, y1)):
                    obs.append((ref, "outline", e))
            else:
                obs.append((ref, "silk", box(g.GetBoundingBox())))

    grp = pcbnew.PCB_GROUP(board)
    grp.SetName(GROUP)
    board.Add(grp)
    failed, report = [], []
    for text, x, y, h, o in LABELS:
        if h < MIN_H:
            raise SystemExit(f"{text!r}: height {h} is below {MIN_H} mm")
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetLayer(pcbnew.F_SilkS)
        style(t, h, o.get("thick", 0.15))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        if o.get("rot"):
            t.SetTextAngleDegrees(o["rot"])
        if isinstance(x, str):   # beside a part: start from its centre
            c = fps[x].GetPosition()
            x, y = MM(c.x) - X0, Y0 + BH - MM(c.y)
        skip = o.get("inside")
        r = o.get("r", 2.5)
        steps = int(r / 0.25)
        cands = sorted(((dx * 0.25, dy * 0.25) for dx in range(-steps, steps + 1) for dy in range(-steps, steps + 1)
                        if not (o.get("lockx") and dx)), key=lambda d: (math.hypot(d[0], 1.6 * d[1])))
        for dx, dy in cands:
            if math.hypot(dx, dy) > r:
                continue
            t.SetPosition(pos(x + dx, y + dy))
            b = ink(t, o)
            if b[0] < EDGE or b[1] < EDGE or b[2] > BW - EDGE or b[3] > BH - EDGE:
                continue
            if any(hit(b, ob, CLEAR) for owner, kind, ob in obs
                   if not (owner == skip and kind in ("courtyard", "outline"))):
                continue
            obs.append((text, "label", b))
            board.Add(t)
            grp.AddItem(t)
            report.append(f"  {text:26s} ({x + dx:5.2f}, {y + dy:5.2f})  moved {math.hypot(dx, dy):.2f}")
            break
        else:
            t.SetPosition(pos(x, y))
            b = ink(t, o)
            why = sorted({f"{owner} {kind}" for owner, kind, ob in obs if hit(b, ob, CLEAR)})
            failed.append(f"  {text!r} at ({x}, {y}): no free spot within {r} mm; in the way: {', '.join(why) or 'board edge'}")
    print("\n".join(report))
    if failed:
        print("FAILED:\n" + "\n".join(failed))
        raise SystemExit(1)
    if dry:
        print("dry run: nothing written")
        return
    pcbnew.SaveBoard(PCB, board, True)
    print(f"wrote {PCB}: {len(LABELS)} labels, reference labels {REF_H} mm")


if __name__ == "__main__":
    main()
