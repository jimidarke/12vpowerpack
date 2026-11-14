#!/usr/bin/env python3
"""Generate the v3.1 placement plan: a to-scale SVG and a coordinate table (Markdown).

Coordinates are part centres in mm from the board's bottom-left corner, y up.
Sizes are approximate footprint extents (w along x, h along y) for drawing only.
"""
import sys, html

OUT_SVG, OUT_MD = sys.argv[1], sys.argv[2]
BW, BH = 100.0, 80.0

MODS = {
    1: ("Car input", "#e05252"),
    2: ("Battery & charge", "#e8913a"),
    3: ("Current monitors", "#9b59b6"),
    4: ("USB-A", "#1abc9c"),
    5: ("5 V buck", "#3a7bd5"),
    6: ("Controller, sensors, LEDs", "#2e9e4f"),
    7: ("12 V output switch", "#8d6e63"),
    8: ("Enable & hold", "#7f8c8d"),
}

# (designator, cx, cy, w, h, module, orientation note)
P = [
    # module 1: car input (top-left, flows right)
    ("J_CAR", 15, 76, 10.2, 8, 1, "screw entries face top edge; pin 1 (+) on the right"),
    ("F_IN", 18, 66, 19.8, 6.8, 1, "3557-2 lying along x; fuse inserts from above"),
    ("D_TVS", 32, 66.5, 6.6, 9.3, 1, "SMC turned 90 deg (pads along y), either way round"),
    ("C_VIN", 32, 60.5, 1.6, 0.8, 1, "below D_TVS"),
    ("D_IGN", 34, 58, 2.7, 1.6, 8, "anode left (VIN_CAR)"),
    ("Q_OR1", 39, 66.5, 3.3, 3.3, 1, "source pins toward D_TVS, drain toward R_SNS_IN"),
    ("U_OR1", 39, 61.5, 3, 3, 1, "next to Q_OR1 gate"),
    ("C_OR1", 42.5, 61.5, 1.6, 0.8, 1, "at U_OR1 VCAP"),
    ("C_SYSIN", 42.35, 66.5, 0.8, 1.6, 1, "turned 90 deg in the gap between Q_OR1 and R_SNS_IN"),
    # module 3: monitors
    ("R_SNS_IN", 47.5, 66.5, 6.3, 3.2, 3, "2512 along x; Kelvin taps to U_MON_IN"),
    ("U_MON_IN", 47.5, 61.5, 4.9, 3, 3, ""),
    ("C_MON1", 51.5, 61.5, 1.6, 0.8, 3, ""),
    ("R_SNS_OUT", 55, 54, 3.2, 6.3, 3, "2512 along y: SYS at top, LOAD at bottom"),
    ("U_MON_OUT", 60.5, 54, 3, 4.9, 3, ""),
    ("C_MON2", 60.5, 50.5, 1.6, 0.8, 3, ""),
    # module 2: battery and charge (top-right)
    ("C_SYS1", 55, 66.5, 3.2, 1.6, 2, "SYS hub"),
    ("C_SYS2", 55, 63.5, 3.2, 1.6, 2, "SYS hub"),
    ("Q_OR2", 61, 66.5, 3.3, 3.3, 2, "source pins toward F_BAT (VBAT), drain toward SYS hub"),
    ("U_OR2", 61, 61.5, 3, 3, 2, ""),
    ("C_OR2", 64.5, 61.5, 1.6, 0.8, 2, "at U_OR2 VCAP"),
    ("F_BAT", 80.2, 66, 19.8, 6.8, 2, "3557-2 lying along x"),
    ("J_SLA", 84, 76, 10.2, 8, 2, "screw entries face top edge"),
    ("F_CHG", 78, 57.5, 10.1, 3, 2, "UMT 250 along x: SYS left, CHG_F right"),
    ("R_CHG", 95, 36, 8, 56, 2, "AC10 along y, raised 3-5 mm; CHG_F pad top (y 62), VBAT pad bottom (y 10)"),
    # module 6: controller (left)
    ("J_TEMP", 52, 76, 15.2, 8, 6, "screw entries face top edge; pin 1 GND on the left"),
    ("J_XIAO", 14, 40, 21, 17.8, 6, "socket; ANTENNA END AT LEFT EDGE, USB-C facing right"),
    ("C_X3", 28, 34, 1.6, 0.8, 6, ""),
    ("D_5V", 28, 31, 2.7, 1.6, 6, "anode right (5V), cathode left (XIAO_5V)"),
    ("C_X5", 28, 28.5, 2.0, 1.25, 6, ""),
    ("R_SDA", 28, 44, 1.6, 0.8, 6, ""),
    ("R_SCL", 28, 42.5, 1.6, 0.8, 6, ""),
    ("R_DQ", 28, 41, 1.6, 0.8, 6, ""),
    ("R_VC1", 22, 56, 1.6, 0.8, 6, ""),
    ("R_VC2", 22, 54.5, 1.6, 0.8, 6, ""),
    ("C_VC", 22, 53, 1.6, 0.8, 6, ""),
    ("R_VB1", 30, 56, 1.6, 0.8, 6, ""),
    ("R_VB2", 30, 54.5, 1.6, 0.8, 6, ""),
    ("C_VB", 30, 53, 1.6, 0.8, 6, ""),
    ("D_GRN", 5, 22, 1.6, 0.8, 6, "at left edge for a light pipe"),
    ("R_LG", 12, 22, 1.6, 0.8, 6, ""),
    ("D_RED", 5, 18, 1.6, 0.8, 6, "at left edge for a light pipe"),
    ("R_LR", 12, 18, 1.6, 0.8, 6, ""),
    # module 8: enable and hold (between XIAO and buck)
    ("JP_HOLD", 32, 50, 2.0, 1.2, 8, ""),
    ("Q_HOLD", 36, 50, 2.9, 2.4, 8, "wired by pad number (see netlist)"),
    ("R_HG1", 40, 52, 1.6, 0.8, 8, ""),
    ("D_ZH", 40, 50, 2.7, 1.6, 8, "cathode toward SYS side"),
    ("R_HG2", 40, 48, 1.6, 0.8, 8, ""),
    ("Q_HOLDDRV", 36, 46, 2.9, 2.4, 8, ""),
    ("R_HOLD", 32, 46, 1.6, 0.8, 8, ""),
    ("R_EN1", 40, 43, 1.6, 0.8, 8, ""),
    ("R_EN2", 40, 41.5, 1.6, 0.8, 8, ""),
    ("C_EN", 40, 40, 1.6, 0.8, 8, "close to U_5V EN"),
    # module 5: buck (bottom-centre)
    ("U_5V", 47, 33, 5, 6.2, 5, "pin 1 top-left; thermal pad via array to GND"),
    ("C_IN5", 47, 39, 3.2, 1.6, 5, "right at VIN/PGND"),
    ("C_HF5", 51, 39, 2.0, 1.25, 5, "right at VIN/PGND"),
    ("C_VCC", 42.5, 31, 1.6, 0.8, 5, ""),
    ("C_BOOT", 51.5, 35, 1.6, 0.8, 5, ""),
    ("R_FBT", 52, 31, 1.6, 0.8, 5, "keep FB trace away from L1/SW"),
    ("R_FBB", 52, 29.5, 1.6, 0.8, 5, ""),
    ("L1", 47, 24, 7.2, 6.6, 5, "SW node short to U_5V"),
    ("C_O1", 54, 27, 3.2, 1.6, 5, ""),
    ("C_O2", 54, 24, 3.2, 1.6, 5, ""),
    ("C_O3", 54, 21, 3.2, 1.6, 5, ""),
    ("C_O4", 54, 18, 3.2, 1.6, 5, ""),
    # module 4: USB (bottom edge)
    ("J_USBA", 38, 7, 13.1, 14, 4, "opening at bottom edge"),
    ("C_USB", 47, 12, 1.6, 0.8, 4, ""),
    # module 7: 12 V output (bottom-right)
    ("Q_OUT", 72, 40, 6.6, 10, 7, "TO-252, drain tab toward bottom (F_OUT)"),
    ("R_OG1", 64, 44.5, 1.6, 0.8, 7, ""),
    ("C_OG", 64, 42.5, 1.6, 0.8, 7, ""),
    ("D_ZO", 64, 40.5, 2.7, 1.6, 7, "cathode toward LOAD"),
    ("R_OG2", 64, 38, 1.6, 0.8, 7, ""),
    ("Q_OUTDRV", 64, 35, 2.9, 2.4, 7, ""),
    ("R_PG", 60, 35, 1.6, 0.8, 7, ""),
    ("D_OEN", 60, 32.5, 2.7, 1.6, 7, "anode OUT_EN, cathode toward XIAO"),
    ("F_OUT", 82, 22, 6.8, 19.8, 7, "3557-2 along y: 12V_SW top, 12V_OUT bottom"),
    ("J_12V", 68, 7.5, 9, 14.5, 7, "barrel opening at bottom edge"),
    ("C_12V", 76, 10, 1.6, 0.8, 7, ""),
]

LBL = {
    "C_VIN": "l", "Q_OR1": "in", "U_OR1": "in", "C_OR1": "b", "C_SYSIN": "b", "U_MON_IN": "in",
    "C_SYS1": "in", "C_SYS2": "in", "Q_OR2": "in", "U_OR2": "in", "R_SNS_OUT": "in", "U_MON_OUT": "r",
    "JP_HOLD": "l", "Q_HOLD": "in", "Q_HOLDDRV": "b", "R_HOLD": "l", "C_IN5": "in", "C_VCC": "l",
    "C_BOOT": "b", "C_O1": "in", "C_O2": "in", "C_O3": "in", "C_O4": "in",
    "R_OG1": "l", "C_OG": "l", "D_ZO": "l", "R_OG2": "l", "Q_OUTDRV": "b", "R_PG": "l", "D_OEN": "l",
    "D_GRN": "t", "R_LG": "t", "D_RED": "t", "R_LR": "t", "R_SNS_IN": "in",
}

HOLES = [(4, 4), (96, 4), (4, 76), (96, 76)]
NETS = [  # hub labels drawn on the board
    ("VIN_CAR", 30, 70.5), ("SYS hub", 57.5, 59.5), ("VBAT", 70, 70.5),
    ("LOAD", 55, 48.5), ("5V", 50, 15.5), ("EN_SRC", 36, 54.5),
]

# --- overlap check (rectangles) ---
def rect(p):
    _, cx, cy, w, h = p[:5]
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
bad = []
for i in range(len(P)):
    a = rect(P[i])
    if a[0] < 0 or a[1] < 0 or a[2] > BW or a[3] > BH:
        bad.append(("off-board", P[i][0]))
    for hx, hy in HOLES:
        if a[0] - 3.25 < hx < a[2] + 3.25 and a[1] - 3.25 < hy < a[3] + 3.25:
            bad.append(("hole", P[i][0]))
    for j in range(i + 1, len(P)):
        b = rect(P[j])
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            bad.append(("overlap", P[i][0], P[j][0]))
print("checks:", bad if bad else "no overlaps, all parts on board, holes clear")

# --- SVG ---
S = 10.0           # px per mm
M = 60             # margin px
MT = 95            # top margin px
LEG = 300          # legend width px
W = int(BW * S + 2 * M + LEG)
H = int(BH * S + MT + M + 40)
def X(x): return M + x * S
def Y(y): return MT + (BH - y) * S

o = []
o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
o.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
o.append(f'<text x="{M}" y="30" font-size="18" font-weight="bold" fill="#222">12 V power pack v3.1 - placement plan (top view, to scale, 100 x 80 mm)</text>')
o.append(f'<text x="{M}" y="52" font-size="12" fill="#555">Coordinates in mm from the bottom-left corner. Grid 10 mm. Sizes approximate. All SMT parts on top.</text>')
# board
o.append(f'<rect x="{X(0)}" y="{Y(BH)}" width="{BW*S}" height="{BH*S}" rx="{1*S}" fill="#f4f8f1" stroke="#2c3e50" stroke-width="2"/>')
for g in range(10, 100, 10):
    o.append(f'<line x1="{X(g)}" y1="{Y(0)}" x2="{X(g)}" y2="{Y(BH)}" stroke="#dde5d8" stroke-width="1"/>')
    o.append(f'<text x="{X(g)}" y="{Y(0)+14}" font-size="10" fill="#888" text-anchor="middle">{g}</text>')
for g in range(10, 80, 10):
    o.append(f'<line x1="{X(0)}" y1="{Y(g)}" x2="{X(BW)}" y2="{Y(g)}" stroke="#dde5d8" stroke-width="1"/>')
    o.append(f'<text x="{X(0)-6}" y="{Y(g)+3}" font-size="10" fill="#888" text-anchor="end">{g}</text>')
o.append(f'<text x="{X(0)-6}" y="{Y(0)+3}" font-size="10" fill="#888" text-anchor="end">0</text>')
# edge labels
o.append(f'<text x="{X(50)}" y="{Y(BH)-8}" font-size="12" fill="#c0392b" text-anchor="middle" font-weight="bold">TOP EDGE: wiring in (car, probe, battery)</text>')
o.append(f'<text x="{X(50)}" y="{Y(0)+30}" font-size="12" fill="#c0392b" text-anchor="middle" font-weight="bold">BOTTOM EDGE: outputs (USB-A, 12 V barrel)</text>')
o.append(f'<text x="{X(0)-38}" y="{Y(40)}" font-size="11" fill="#2e9e4f" text-anchor="middle" transform="rotate(-90 {X(0)-38} {Y(40)})" font-weight="bold">LEFT EDGE: XIAO antenna, LEDs</text>')
# antenna keep-out
o.append(f'<rect x="{X(0)}" y="{Y(49.5)}" width="{6*S}" height="{19*S}" fill="url(#hatch)" stroke="#2e9e4f" stroke-dasharray="4 3"/>')
o.insert(1, '<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#2e9e4f" stroke-width="1.5" opacity="0.5"/></pattern></defs>')
o.append(f'<text x="{X(0.5)}" y="{Y(29.3)}" font-size="9" fill="#2e9e4f">no copper under</text>')
o.append(f'<text x="{X(0.5)}" y="{Y(27.8)}" font-size="9" fill="#2e9e4f">antenna (both layers)</text>')
# R_CHG hot zone
o.append(f'<rect x="{X(89.5)}" y="{Y(65)}" width="{11*S-4}" height="{58*S}" fill="#fdebd0" opacity="0.6" stroke="#e8913a" stroke-dasharray="6 3"/>')
# holes
for hx, hy in HOLES:
    o.append(f'<circle cx="{X(hx)}" cy="{Y(hy)}" r="{3.25*S}" fill="none" stroke="#999" stroke-dasharray="3 3"/>')
    o.append(f'<circle cx="{X(hx)}" cy="{Y(hy)}" r="{1.6*S}" fill="#fff" stroke="#333" stroke-width="1.5"/>')
    o.append(f'<text x="{X(hx)}" y="{Y(hy)+3}" font-size="7" fill="#333" text-anchor="middle">M3</text>')
# nets
for name, nx, ny in NETS:
    o.append(f'<text x="{X(nx)}" y="{Y(ny)}" font-size="10" fill="#444" font-style="italic" text-anchor="middle">{html.escape(name)}</text>')
# parts
for d, cx, cy, w, h, m, note in P:
    col = MODS[m][1]
    x0, y0 = X(cx - w / 2), Y(cy + h / 2)
    o.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" fill="{col}" fill-opacity="0.22" stroke="{col}" stroke-width="1.5" rx="2"/>')
    side = LBL.get(d, 'in' if (w * S >= 40 and h * S >= 14) else 'r')
    if side == 'in':
        fs = 12 if (w * S >= 60 and h * S >= 24) else 8
        rot = h > w * 1.6
        tx, ty = X(cx), Y(cy) + fs * 0.35
        tr = f' transform="rotate(-90 {tx:.1f} {Y(cy):.1f})"' if rot else ''
        o.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{fs}" font-weight="bold" fill="#111" text-anchor="middle"{tr}>{d}</text>')
    else:
        fs = 9
        if side == 'r':   tx, ty, an = X(cx + w/2) + 3, Y(cy) + 3, 'start'
        elif side == 'l': tx, ty, an = X(cx - w/2) - 3, Y(cy) + 3, 'end'
        elif side == 't': tx, ty, an = X(cx), Y(cy + h/2) - 3, 'middle'
        else:             tx, ty, an = X(cx), Y(cy - h/2) + 10, 'middle'
        o.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{fs}" fill="#111" text-anchor="{an}">{d}</text>')
# special callouts
o.append(f'<text x="{X(14)}" y="{Y(40)+18}" font-size="10" fill="#1d6b35" text-anchor="middle">&#8592; antenna   USB-C &#8594;</text>')
o.append(f'<text x="{X(95)}" y="{Y(18)}" font-size="9" fill="#a35a10" text-anchor="middle" transform="rotate(-90 {X(95)} {Y(18)})">HOT: raised, vented</text>')
o.append(f'<text x="{X(68)}" y="{Y(1.2)}" font-size="9" fill="#333" text-anchor="middle">plug &#8595;</text>')
o.append(f'<text x="{X(38)}" y="{Y(1.2)}" font-size="9" fill="#333" text-anchor="middle">plug &#8595;</text>')
# legend
lx = M + BW * S + 40
o.append(f'<text x="{lx}" y="{MT}" font-size="13" font-weight="bold" fill="#222">Modules (netlist.md)</text>')
for i, (m, (name, col)) in enumerate(MODS.items()):
    yy = MT + 24 + i * 24
    o.append(f'<rect x="{lx}" y="{yy-11}" width="16" height="14" fill="{col}" fill-opacity="0.3" stroke="{col}"/>')
    o.append(f'<text x="{lx+24}" y="{yy}" font-size="12" fill="#222">{m}. {html.escape(name)}</text>')
notes = [
    "Power path (wide pours, >= 4.5 mm):",
    " J_CAR > F_IN > Q_OR1 > R_SNS_IN > SYS",
    " J_SLA > F_BAT > Q_OR2 > SYS",
    " SYS > R_SNS_OUT > LOAD > Q_OUT >",
    "   F_OUT > J_12V",
    "Bottom layer: solid GND pour.",
    "Check after placing:",
    " - 3557-2 pads 1+3 on the same clip",
    " - R_CHG pads 52 mm apart",
    " - no copper under XIAO antenna",
    " - USB-A / barrel flush with edge",
]
for i, t in enumerate(notes):
    o.append(f'<text x="{lx}" y="{MT + 250 + i*18}" font-size="11" fill="#333">{html.escape(t)}</text>')
o.append('</svg>')
open(OUT_SVG, "w").write("\n".join(o))

# --- Markdown table ---
lines = ["| Module | Designator | X (mm) | Y (mm) | Orientation / note |", "|---|---|---:|---:|---|"]
for d, cx, cy, w, h, m, note in sorted(P, key=lambda p: (p[5], p[0])):
    lines.append(f"| {m}. {MODS[m][0]} | {d} | {cx:g} | {cy:g} | {note} |")
open(OUT_MD, "w").write("\n".join(lines) + "\n")
print("parts:", len(P))
