"""Build the 3D models that neither KiCad nor the vendors supply: kicad/lib/pwrpack.3dshapes/*.step

    python kicad/gen/build_models.py        (any Python with CadQuery: pip install cadquery)

These are envelope models drawn from datasheet dimensions, for the 3D view and for fitting the
case. They are not vendor models; check heights against the parts in hand.

Model axes are KiCad's: x as in the footprint, y opposite to the footprint's y, z up from the board.

- XIAO_ESP32C6_Socketed.step   Seeed XIAO ESP32-C6 (21 x 17.8 mm board) on two 1x7 female headers
                               8.5 mm tall (HCTL PM254-1-07-Z-8.5), with its own pin headers.
                               Shield can, USB-C and antenna sizes are approximate.
- R_Axial_Vishay_AC10.step     Vishay AC10: body 44 x 8 mm, 0.8 mm leads [DS Vishay AC], straight
                               leads bent down to the 52 mm pitch, body held 4 mm off the board.
- Fuse_Schurter_UMT250.step    Schurter UMT 250: 10.1 x 3 x 3 mm, 1.6 mm end caps [DS Schurter UMT 250].
"""
import os
import cadquery as cq

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib", "pwrpack.3dshapes"))
BLACK, PCB, METAL, TIN = cq.Color(0.12, 0.12, 0.12), cq.Color(0.08, 0.1, 0.12), cq.Color(0.75, 0.75, 0.78), cq.Color(0.85, 0.85, 0.85)
GREEN, WHITE, GOLD = cq.Color(0.25, 0.45, 0.3), cq.Color(0.92, 0.92, 0.88), cq.Color(0.85, 0.7, 0.3)


def box(sx, sy, sz, x=0.0, y=0.0, z0=0.0):
    """Box of size sx, sy, sz centred on x, y with its base at z0."""
    return cq.Workplane("XY").box(sx, sy, sz).translate((x, y, z0 + sz / 2))


def save(assy, name):
    path = os.path.join(OUT, name)
    assy.save(path)
    print("wrote", path)


def xiao():
    SOCKET_H, HEADER_H, T = 8.5, 2.5, 1.0     # female header, the module's pin header plastic, module board
    a = cq.Assembly(name="XIAO_ESP32C6_Socketed")
    for sx in (-7.62, 7.62):
        a.add(box(2.54, 17.78, SOCKET_H, x=sx), color=BLACK)
        a.add(box(2.54, 17.78, HEADER_H, x=sx, z0=SOCKET_H), color=BLACK)
        for i in range(7):                       # solder tails above the module board
            a.add(box(0.64, 0.64, 1.2, x=sx, y=-7.62 + i * 2.54, z0=SOCKET_H + HEADER_H + T), color=GOLD)
    z = SOCKET_H + HEADER_H
    a.add(box(17.8, 21.0, T, z0=z), color=PCB)
    top = z + T
    a.add(box(8.94, 7.35, 3.26, y=10.5 + 1.4 - 7.35 / 2, z0=top).edges("|Y").fillet(1.2), color=METAL)   # USB-C, 1.4 mm overhang
    a.add(box(11.0, 9.0, 2.2, y=-1.0, z0=top), color=METAL)                # shield can (approximate)
    a.add(box(5.0, 1.6, 1.0, y=-9.3, z0=top), color=WHITE)                 # ceramic antenna (approximate)
    save(a, "XIAO_ESP32C6_Socketed.step")


def ac10():
    L, D, d, PITCH, LIFT = 44.0, 8.0, 0.8, 52.0, 4.0
    zc = LIFT + D / 2
    a = cq.Assembly(name="R_Axial_Vishay_AC10")
    body = cq.Workplane("YZ").circle(D / 2).extrude(L).translate(((PITCH - L) / 2, 0, zc))
    a.add(body, color=GREEN)
    for x0, x1 in ((0.0, (PITCH - L) / 2), (PITCH, (PITCH + L) / 2)):
        a.add(cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0).translate((x0, 0, zc)), color=TIN)   # along the axis
        a.add(cq.Workplane("XY").circle(d / 2).extrude(zc + 3.0).translate((x0, 0, -3.0)), color=TIN)  # down through the board
        a.add(cq.Workplane("XY").sphere(d / 2).translate((x0, 0, zc)), color=TIN)                      # the bend
    save(a, "R_Axial_Vishay_AC10.step")


def umt250():
    L, W, H, CAP = 10.1, 3.0, 3.0, 1.6
    a = cq.Assembly(name="Fuse_Schurter_UMT250")
    a.add(box(L - 2 * CAP, W - 0.2, H - 0.2, z0=0.1), color=WHITE)
    for s in (-1, 1):
        a.add(box(CAP, W, H, x=s * (L - CAP) / 2), color=METAL)
    save(a, "Fuse_Schurter_UMT250.step")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    xiao()
    ac10()
    umt250()
