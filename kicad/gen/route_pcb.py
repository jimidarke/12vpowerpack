"""First routing pass for kicad/powerpack.kicad_pcb: power pours by script, the rest by Freerouting.

    <KiCad python> kicad/gen/route_pcb.py zones   # add the copper zones and the antenna keep-out, fill, save
    <KiCad python> kicad/gen/route_pcb.py dsn     # export kicad/out/route/powerpack.dsn for Freerouting
    java -jar freerouting-1.9.0.jar -de powerpack.dsn -do powerpack.ses -mp 40 -inc Skip -da -dct 0   (in kicad/out/route)
    <KiCad python> kicad/gen/route_pcb.py ses     # import the routed session, refill the zones, save

The high-current path is copper zones on the top layer (ZONES below, mm from the board's bottom-left
corner, y up), each at least as wide as blocks/03-layout-brief.md asks where the parts allow it.
The bottom layer is a GND zone. Freerouting connects everything the zones do not reach.

"zones" refuses to run on a board that already has zones or tracks. Close the board in KiCad first.
"""
import json, os, shutil, sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_pcb import BW, BH, PCB, KICAD, kpos

NM = pcbnew.FromMM
ROUTE = os.path.join(KICAD, "out", "route")

# net: (layer, priority, [(x, y), ...])
ZONES = {
    "GND": ("B", 0, [(0.5, 0.5), (BW - 0.5, 0.5), (BW - 0.5, BH - 0.5), (0.5, BH - 0.5)]),
    # car input: J_CAR pin 1 -> F_IN left clip
    "J_CAR_P": ("F", 1, [(3.5, 50.4), (7.2, 50.4), (7.2, 58.0), (18.6, 58.0), (18.6, 67.6), (13.4, 67.6),
                         (13.4, 62.4), (3.5, 62.4)]),
    # F_IN right clip -> Q_OR1 source, D_TVS, C_VIN, TP1
    "VIN_CAR": ("F", 1, [(23.4, 50.6), (27.0, 50.6), (27.0, 57.4), (29.5, 57.4), (29.5, 67.2), (21.5, 67.2),
                         (21.5, 57.4), (17.3, 57.4), (17.3, 50.6), (22.1, 50.6), (22.1, 48.6), (23.4, 48.6),
                         (23.4, 50.6)]),
    # Q_OR1 drain -> R_SNS_IN, C_SYSIN
    "SYS_IN": ("F", 1, [(27.4, 52.9), (32.0, 52.9), (32.0, 49.9), (33.4, 49.9), (33.4, 52.9), (36.3, 52.9),
                        (36.3, 56.2), (27.4, 56.2)]),
    # R_SNS_IN -> C_SYS1/2 -> over the top to Q_OR2 drain; down to R_SNS_OUT; across to F_CHG
    "SYS": ("F", 1, [(40.8, 52.6), (44.8, 52.6), (44.8, 51.2), (46.4, 51.2), (46.4, 57.0), (49.6, 57.0),
                     (49.6, 43.2), (53.9, 43.2), (53.9, 43.6), (75.9, 43.6), (75.9, 49.3), (73.7, 49.3),
                     (73.7, 47.6), (61.4, 47.6), (61.4, 48.9), (59.9, 48.9), (59.9, 47.6), (53.9, 47.6), (53.9, 57.0), (56.5, 57.0), (56.5, 53.0), (60.2, 53.0),
                     (60.2, 61.5), (40.8, 61.5)]),
    # R_SNS_OUT -> Q_OUT source; down the left of the buck input capacitors to U_5V VIN
    "LOAD": ("F", 1, [(40.3, 24.4), (49.7, 24.4), (49.7, 27.0), (41.9, 27.0), (41.9, 31.0), (75.0, 31.0),
                      (75.0, 38.3), (73.7, 38.3), (73.7, 36.4), (69.4, 36.4), (69.4, 38.2), (68.1, 38.2),
                      (68.1, 36.4), (63.3, 36.4), (63.3, 38.2), (62.1, 38.2), (62.1, 36.4), (54.0, 36.4), (54.0, 38.9), (50.1, 38.9), (50.1, 35.0), (40.3, 35.0)]),
    # battery: Q_OR2 source and F_BAT left clip; over the top of F_BAT and down the right edge to R_CHG pad 2
    "VBAT": ("F", 1, [(59.8, 50.0), (72.8, 50.0), (72.8, 57.3), (91.0, 57.3), (91.0, 7.7), (98.0, 7.7),
                      (98.0, 59.4), (60.5, 59.4), (60.5, 52.8), (59.8, 52.8)]),
    # J_SLA pin 1 -> F_BAT right clip, on the bottom because the VBAT pour crosses above it on top
    "J_SLA_P": ("B", 1, [(83.0, 50.4), (88.7, 50.4), (88.7, 66.6), (83.0, 66.6)]),
    # Q_OUT drain tab -> F_OUT top clip
    "12V_SW": ("F", 1, [(71.4, 23.5), (86.6, 23.5), (86.6, 30.3), (71.4, 30.3)]),
    # F_OUT bottom clip -> J_12V, C_12V
    "12V_OUT": ("F", 1, [(69.8, 11.8), (86.6, 11.8), (86.6, 16.4), (74.3, 16.4), (74.3, 14.7), (71.9, 14.7),
                         (71.9, 18.2), (70.6, 18.2), (70.6, 14.7), (69.8, 14.7)]),
    # L1 output -> C_O1..4 -> J_USBA pin 1
    "5V": ("F", 1, [(25.4, 7.8), (27.5, 7.8), (27.5, 10.3), (69.2, 10.3), (69.2, 28.5), (65.5, 28.5),
                    (65.5, 14.6), (51.3, 14.6), (51.3, 18.2), (50.1, 18.2), (50.1, 14.6), (46.8, 14.6),
                    (46.8, 18.2), (45.6, 18.2), (45.6, 14.6), (25.4, 14.6)]),
    # switch node: U_5V SW pin -> C_BOOT -> L1
    "SW_5V": ("F", 1, [(53.3, 27.45), (60.2, 27.45), (60.2, 24.6), (62.4, 24.6), (62.4, 29.6), (53.3, 29.6)]),
}
ANTENNA = [(0.0, 21.0), (4.8, 21.0), (4.8, 39.0), (0.0, 39.0)]  # no copper under the XIAO antenna, both layers

# Top-layer areas the autorouter may not put tracks or vias in: the necks of the power pours, so that
# signal tracks cross them on the bottom layer instead of cutting them. None contains a pad of another net.
# They exist only in the copy exported to Freerouting, not in the board.
KEEP = [
    (3.6, 58.1, 18.5, 62.3), (3.6, 50.5, 7.1, 58.1),            # J_CAR_P
    (17.4, 50.7, 25.9, 57.3),                                   # VIN_CAR
    (27.5, 53.0, 36.2, 56.1), (32.1, 50.0, 33.3, 53.0),         # SYS_IN
    (41.0, 57.1, 60.1, 61.4), (49.7, 44.8, 53.0, 57.0), (54.0, 43.7, 73.6, 47.5),  # SYS
    (40.9, 52.7, 46.3, 57.1), (44.9, 51.3, 46.3, 52.7),
    (54.1, 31.1, 72.9, 36.3), (40.4, 31.1, 50.0, 34.9), (40.4, 27.1, 41.8, 31.1),  # LOAD
    (61.5, 57.4, 98.0, 59.3), (91.1, 7.8, 98.0, 57.4), (61.6, 50.1, 72.7, 57.4),  # VBAT
    (71.5, 23.6, 86.5, 30.2),                                   # 12V_SW
    (69.9, 11.9, 86.5, 14.6), (74.4, 14.6, 86.5, 16.3),         # 12V_OUT
    (33.0, 10.4, 69.1, 14.5), (65.6, 14.5, 69.1, 28.4),         # 5V
    (50.2, 14.5, 51.2, 18.1), (45.7, 14.5, 46.7, 18.1),
    (53.4, 27.5, 60.1, 29.5),                                   # SW_5V
    # corridors of the hand-placed tracks in MANUAL
    (27.7, 47.7, 28.3, 50.3), (23.5, 47.8, 26.1, 48.3),         # under U_OR1; U_OR1 pin 3 to C_OR1
    (59.2, 48.3, 59.8, 50.7),                                   # under U_OR2
    (43.0, 48.2, 44.6, 52.0), (34.8, 51.2, 43.4, 52.7),         # U_MON_IN sense lines
    (63.9, 38.6, 78.0, 39.6),                                   # G_OUT above the gate parts
]

# Connections placed by hand because the autorouter would cut a pour to make them (their nets are in the
# "Skip" class, or the autorouter leaves them). (net, layer, width, points); a via joins the layers where
# a top and a bottom run of the same net meet at a point listed in VIAS.
MANUAL = [
    # CHG_F: R_CHG pad 1 to F_CHG pad 2, about 1.2 A. On top it would cut the VBAT pour.
    ("CHG_F", "B", 1.0, [(95.0, 61.0), (91.0, 57.0), (91.0, 51.0), (87.2, 47.2), (85.4, 47.2)]),
    ("CHG_F", "B", 1.0, [(85.4, 46.6), (85.4, 47.8)]),
    ("CHG_F", "F", 0.8, [(85.4, 46.6), (83.6, 46.6)]),
    ("CHG_F", "F", 0.8, [(85.4, 47.8), (83.6, 47.8)]),
    # Q_OR2 gate to U_OR2 pin 5: on top it would cut Q_OR2's source pins off the VBAT pour.
    ("OR2_GATE", "F", 0.25, [(60.95, 55.45), (61.95, 55.45)]),
    ("OR2_GATE", "B", 0.25, [(61.95, 55.45), (61.95, 49.5)]),
    ("OR2_GATE", "F", 0.25, [(61.95, 49.5), (60.65, 49.5)]),
    # The two VBAT pins of U_OR2 and the two VIN_CAR pins of U_OR1, joined under the package.
    ("VBAT", "F", 0.25, [(58.35, 48.55), (59.5, 48.55), (59.5, 50.45), (60.65, 50.45)]),
    ("VIN_CAR", "F", 0.25, [(26.85, 48.05), (28.0, 48.05), (28.0, 49.95), (29.15, 49.95)]),
    # U_OR1 pin 3 to the VIN_CAR pour at C_OR1; U_OR1 pin 4 to the SYS_IN pour at C_SYSIN.
    ("VIN_CAR", "F", 0.25, [(26.85, 48.05), (23.3, 48.05), (22.75, 48.7)]),
    ("SYS_IN", "F", 0.25, [(29.15, 48.05), (31.5, 48.05), (32.75, 49.3), (32.75, 50.3)]),
    # Kelvin sense lines of U_MON_IN: pin 10 to the SYS_IN pad of R_SNS_IN, pins 8/9 to SYS at C_SYS2.
    ("SYS_IN", "F", 0.2, [(42.15, 49.0), (43.4, 49.0), (43.4, 51.6), (36.4, 51.6), (35.8, 52.2), (35.8, 53.0)]),
    ("SYS", "F", 0.2, [(42.15, 48.5), (44.2, 48.5), (44.2, 51.0), (45.3, 51.8)]),
    # G_OUT across the top of the gate parts: R_OG1, C_OG, D_ZO.
    ("G_OUT", "F", 0.25, [(64.3, 37.5), (64.3, 39.1), (77.65, 39.1), (77.65, 37.5)]),
    ("G_OUT", "F", 0.25, [(70.25, 37.5), (70.25, 39.1)]),
]
VIAS = [("CHG_F", 85.4, 46.6, 0.8, 0.4), ("CHG_F", 85.4, 47.8, 0.8, 0.4),
        ("OR2_GATE", 61.95, 55.45, 0.6, 0.3), ("OR2_GATE", 61.95, 49.5, 0.6, 0.3)]

# Net classes for the autorouter only (the project's own classes are for hand routing and are not changed).
# The zones carry the current; tracks on power nets only pick up small pads, so they must fit between IC pins.
ROUTE_CLASSES = {
    "Default": dict(track_width=0.2, clearance=0.15, via_diameter=0.6, via_drill=0.3),
    "Power": dict(track_width=0.25, clearance=0.2, via_diameter=0.8, via_drill=0.4),
    "Mid": dict(track_width=0.6, clearance=0.2, via_diameter=0.8, via_drill=0.4),
    "Skip": dict(track_width=1.0, clearance=0.2, via_diameter=0.8, via_drill=0.4),  # run Freerouting with -inc Skip
}
MID_NETS = ["5V", "XIAO_5V", "SW_5V"]
SKIP_NETS = ["CHG_F", "OR2_GATE"]


def outline(zone, pts):
    o = zone.Outline()
    o.NewOutline()
    for x, y in pts:
        p = kpos(x, y)
        o.Append(p.x, p.y)


def fill(board):
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def guard():
    lock = os.path.join(KICAD, "~" + os.path.basename(PCB) + ".lck")
    if os.path.exists(lock):
        raise SystemExit("KiCad has the board open (lock file). Save and close it first.")


def zones():
    guard()
    board = pcbnew.LoadBoard(PCB)
    if board.GetAreaCount() or len(board.GetTracks()):
        raise SystemExit("The board already has zones or tracks; this step is for an unrouted board.")
    for key, (layer, prio, pts) in ZONES.items():
        net = key.split("#")[0]
        code = board.GetNetcodeFromNetname("/" + net)
        if code <= 0:
            raise SystemExit(f"no net /{net} on the board")
        z = pcbnew.ZONE(board)
        z.SetLayer(pcbnew.F_Cu if layer == "F" else pcbnew.B_Cu)
        z.SetNetCode(code)
        z.SetZoneName(key)
        z.SetAssignedPriority(prio)
        z.SetLocalClearance(NM(0.3))
        z.SetMinThickness(NM(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)  # solid on SMD pads, spokes on through-hole
        z.SetThermalReliefGap(NM(0.4))
        z.SetThermalReliefSpokeWidth(NM(1.0))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        outline(z, pts)
        board.Add(z)
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    k.SetZoneName("XIAO antenna keep-out")
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.B_Cu)
    k.SetLayerSet(ls)
    k.SetDoNotAllowTracks(True)
    k.SetDoNotAllowVias(True)
    k.SetDoNotAllowZoneFills(True)
    k.SetDoNotAllowPads(False)
    k.SetDoNotAllowFootprints(False)
    outline(k, ANTENNA)
    board.Add(k)
    fill(board)
    pcbnew.SaveBoard(PCB, board, True)
    print(f"added {len(ZONES)} zones and the antenna keep-out; filled; wrote {PCB}")


def dsn():
    """Copy the project to kicad/out/route with autorouter net classes and export the Specctra DSN."""
    os.makedirs(ROUTE, exist_ok=True)
    for ext in (".kicad_pcb", ".kicad_pro"):
        shutil.copy(PCB[:-len(".kicad_pcb")] + ext, os.path.join(ROUTE, "powerpack" + ext))
    pro = os.path.join(ROUTE, "powerpack.kicad_pro")
    d = json.load(open(pro))
    ns = d["net_settings"]
    base = next(c for c in ns["classes"] if c["name"] == "Default")
    ns["classes"] = [dict(base, name=n, **v) for n, v in ROUTE_CLASSES.items()]
    ns["netclass_patterns"] = [p for p in ns["netclass_patterns"] if p["netclass"] == "Power"] + \
                              [{"netclass": "Mid", "pattern": "/" + n} for n in MID_NETS] + \
                              [{"netclass": "Skip", "pattern": "/" + n} for n in SKIP_NETS]
    json.dump(d, open(pro, "w", newline="\n"), indent=2)
    board = pcbnew.LoadBoard(os.path.join(ROUTE, "powerpack.kicad_pcb"))
    for x0, y0, x1, y1 in KEEP:
        k = pcbnew.ZONE(board)
        k.SetIsRuleArea(True)
        k.SetLayer(pcbnew.F_Cu)
        k.SetDoNotAllowTracks(True)
        k.SetDoNotAllowVias(True)
        k.SetDoNotAllowZoneFills(False)
        k.SetDoNotAllowPads(False)
        k.SetDoNotAllowFootprints(False)
        outline(k, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        board.Add(k)
    out = os.path.join(ROUTE, "powerpack.dsn")
    if not pcbnew.ExportSpecctraDSN(board, out):
        raise SystemExit("DSN export failed")
    print("wrote", out)


def ses():
    guard()
    board = pcbnew.LoadBoard(PCB)
    src = os.path.join(ROUTE, "powerpack.ses")
    if not pcbnew.ImportSpecctraSES(board, src):
        raise SystemExit("SES import failed")
    for net, layer, width, pts in MANUAL:
        for p, q in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(kpos(*p))
            t.SetEnd(kpos(*q))
            t.SetWidth(NM(width))
            t.SetLayer(pcbnew.F_Cu if layer == "F" else pcbnew.B_Cu)
            t.SetNetCode(board.GetNetcodeFromNetname("/" + net))
            board.Add(t)
    for net, x, y, dia, drill in VIAS:
        v = pcbnew.PCB_VIA(board)
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetPosition(kpos(x, y))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetWidth(pcbnew.F_Cu, NM(dia))
        v.SetDrill(NM(drill))
        v.SetNetCode(board.GetNetcodeFromNetname("/" + net))
        board.Add(v)
    fill(board)
    pcbnew.SaveBoard(PCB, board, True)
    tr = board.GetTracks()
    print(f"imported {sum(1 for t in tr if t.GetClass() == 'PCB_TRACK')} track segments and "
          f"{sum(1 for t in tr if t.GetClass() == 'PCB_VIA')} vias; refilled; wrote {PCB}")


if __name__ == "__main__":
    {"zones": zones, "dsn": dsn, "ses": ses}[sys.argv[1] if len(sys.argv) > 1 else ""]()
