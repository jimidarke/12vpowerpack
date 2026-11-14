"""Generate kicad/powerpack.kicad_sch from netlist.md.

    python3 kicad/gen/gen_sch.py            # writes the schematic and kicad/out/expected.json

netlist.md is the source. Every pin gets a short wire and a net label (no drawn wires between
parts), so the schematic is exactly the table. UUIDs are derived from the designators, so a
regenerated schematic keeps its link to the board.

Run kicad/gen/check_sch.py afterwards: it upgrades the file to the native KiCad 10 format,
runs ERC and compares KiCad's netlist with netlist.md pin by pin.
"""
import json, math, os, re, sys, uuid
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexpr
from sexpr import Q, find, findall

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(KICAD, ".."))
STOCK = "/usr/share/kicad/symbols"
PROJECT = "powerpack"
G = 1.27  # schematic grid


def uid(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "pwrpack-sch/" + tag))


ROOT_UUID = uid("root")

# ------------------------------------------------------------------------------------------
# Part choices: symbol and footprint per designator (first matching rule wins).
# value None means: derive from the netlist.md part text.
# ------------------------------------------------------------------------------------------
RULES = [
    (r"R_SNS_", "Device:R", "Resistor_SMD:R_2512_6332Metric", None),
    (r"R_CHG$", "Device:R", "pwrpack:R_Axial_Vishay_AC10_EK_L44.0mm_D8.0mm_P52.00mm", None),
    (r"R_", "Device:R", "Resistor_SMD:R_0603_1608Metric", None),
    (r"C_", "Device:C", "Capacitor_SMD:C_{pkg}_{metric}Metric", None),
    (r"L1$", "Device:L", "pwrpack:L_Bourns_SRP6540_7.2x6.5mm", None),
    (r"F_(IN|BAT|OUT)$", "pwrpack:Fuseholder_3557-2", "pwrpack:Fuseholder_Blade_ATO_Keystone_3557-2", None),
    (r"F_CHG$", "Device:Fuse", "Fuse:Fuse_Schurter_UMT250", None),
    (r"D_TVS$", "Device:D_TVS", "Diode_SMD:D_SMC", "SMCJ18CA"),
    (r"D_(5V|IGN|OEN)$", "Device:D_Schottky", "Diode_SMD:D_SOD-123", None),
    (r"D_Z", "Device:D_Zener", "Diode_SMD:D_SOD-123", "BZT52C12"),
    (r"D_GRN$", "Device:LED", "LED_SMD:LED_0603_1608Metric", "green"),
    (r"D_RED$", "Device:LED", "LED_SMD:LED_0603_1608Metric", "red"),
    (r"U_OR", "Power_Management:LM74700", "Package_TO_SOT_SMD:SOT-23-6", "LM74700QDBVRQ1"),
    (r"Q_OR", "Transistor_FET:CSD18543Q3A", "Package_SON:VSON-8_3.3x3.3mm_P0.65mm_NexFET", "CSD18543Q3A"),
    (r"U_MON", "Sensor_Energy:INA226", "Package_SO:TSSOP-10_3x3mm_P0.5mm", "INA226AIDGSR"),
    (r"U_5V$", "Regulator_Switching:LMR33630ADDA",
     "Package_SO:Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm_ThermalVias", "LMR33630ADDAR"),
    (r"Q_(HOLDDRV|OUTDRV)$", "Transistor_FET:2N7002", "Package_TO_SOT_SMD:SOT-23", "2N7002"),
    (r"Q_HOLD$", "Transistor_FET:BSS84", "Package_TO_SOT_SMD:SOT-23", "BSS84"),
    (r"Q_OUT$", "pwrpack:DMP4015SK3", "Package_TO_SOT_SMD:TO-252-2", "DMP4015SK3"),
    (r"J_(CAR|SLA)$", "Connector:Screw_Terminal_01x02",
     "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal", "MKDS 1,5/2"),
    (r"J_TEMP$", "Connector:Screw_Terminal_01x03",
     "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3_1x03_P5.00mm_Horizontal", "MKDS 1,5/3"),
    (r"J_USBA$", "Connector:USB_A", "pwrpack:USB_A_Wuerth_61400416021_Horizontal", "61400416021"),
    (r"J_12V$", "Connector:Barrel_Jack_MountingPin", "Connector_BarrelJack:BarrelJack_CUI_PJ-063AH_Horizontal",
     "PJ-063AH"),
    (r"J_XIAO$", "pwrpack:XIAO_ESP32C6", "pwrpack:XIAO_ESP32C6_Socketed_2x1x07_P2.54mm", "XIAO ESP32-C6"),
    (r"JP_", "Jumper:SolderJumper_2_Open", "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", None),
    (r"TP\d", "Connector:TestPoint", "TestPoint:TestPoint_Pad_D1.5mm", None),
]
PKG_METRIC = {"0402": "1005", "0603": "1608", "0805": "2012", "1206": "3216", "1210": "3225"}
NOT_IN_BOM = re.compile(r"^(TP\d+|JP_.*|H\d+)$")

# Mounting holes: not in netlist.md; positions come from blocks/04-placement-gen.py.
MOUNTING = ["H1", "H2", "H3", "H4"]
# Nets fed only by connectors, the inductor or a diode: ERC needs a PWR_FLAG to accept that
# their power-input pins are driven.
PWR_FLAGS = ["GND", "VIN_CAR", "VBAT", "LOAD", "5V", "XIAO_5V"]

# Words in the Connect column that name a pin by function.
ALIASES = {
    "source": ["S"], "gate": ["G"], "drain": ["D"], "tab": ["D"], "anode": ["A"], "cathode": ["K"],
    "shell": ["SH"], "center pin": ["1"], "terminal": ["2"], "both mount pins": ["MP"],
    "thermal pad": ["9"],
}


def norm(s):
    s = s.replace("−", "-").replace("~{", "").replace("}", "").replace("~", "").strip().lower()
    return s


# ------------------------------------------------------------------------------------------
# netlist.md parsing
# ------------------------------------------------------------------------------------------
DES = r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*"


def expand_refs(cell):
    cell = cell.strip()
    if not re.fullmatch(rf"{DES}(\s*[,–]\s*{DES})*", cell):
        return []
    out = []
    for part in re.split(r"\s*,\s*", cell):
        if "–" in part:
            a, b = [x.strip() for x in part.split("–")]
            pa = re.fullmatch(r"(.*?)(\d+)", a)
            pb = re.fullmatch(r"(.*?)(\d+)", b)
            for i in range(int(pa.group(2)), int(pb.group(2)) + 1):
                out.append(f"{pa.group(1)}{i}")
        else:
            out.append(part)
    return out


def table_rows(lines, start):
    """Rows of the markdown table starting at or after line index start."""
    i = start
    while i < len(lines) and not lines[i].startswith("|"):
        i += 1
    rows = []
    header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    i += 2
    while i < len(lines) and lines[i].startswith("|"):
        rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
        i += 1
    return header, rows


def parse_netlist_md(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    modules, info = [], {}
    for i, ln in enumerate(lines):
        m = re.match(r"## Module (\d+) — (.*)", ln)
        if m:
            _, rows = table_rows(lines, i + 1)
            modules.append((int(m.group(1)), m.group(2).strip(), rows))
        m = re.match(r"### (Fitted by JLCPCB|Hand-soldered, from LCSC|Hand-soldered, from DigiKey)", ln)
        if m:
            fit = {"Fitted by JLCPCB": "fab", "Hand-soldered, from LCSC": "hand",
                   "Hand-soldered, from DigiKey": "DK"}[m.group(1)]
            header, rows = table_rows(lines, i + 1)
            col = {h: k for k, h in enumerate(header)}
            for r in rows:
                for ref in expand_refs(r[col["Designators"]]):
                    part = r[col["Part"]]
                    info[ref] = {
                        "fit": fit,
                        "lcsc": r[col["LCSC"]].strip("* ") if "LCSC" in col else "",
                        "part": re.split(r", (?=\D)", part)[0],
                        "part_full": part,
                    }
    return modules, info


# ------------------------------------------------------------------------------------------
# Library symbols
# ------------------------------------------------------------------------------------------
_libcache = {}


def load_lib(lib):
    if lib not in _libcache:
        p = os.path.join(KICAD, "lib", lib + ".kicad_sym")
        if not os.path.exists(p):
            p = os.path.join(STOCK, lib + ".kicad_sym")
        _libcache[lib] = sexpr.parse(open(p, encoding="utf-8").read())
    return _libcache[lib]


def flat_symbol(lib_id):
    """The library symbol, with 'extends' resolved, named 'Lib:Name' as the schematic cache wants."""
    lib, name = lib_id.split(":")
    t = load_lib(lib)
    syms = {s[1]: s for s in findall(t, "symbol")}
    s = syms[name]
    ext = find(s, "extends")
    if ext:
        base = flat_symbol(f"{lib}:{ext[1]}")
        props = {p[1]: p for p in findall(s, "property")}
        out = [c for c in base if not (isinstance(c, list) and c[0] == "property")]
        bprops = [p for p in findall(base, "property")]
        merged = [props.pop(p[1], p) for p in bprops] + list(props.values())
        out = out[:2] + merged + out[2:]
        out[1] = Q(lib_id)
        # rename units
        bname = base[1].split(":")[1]
        for u in findall(out, "symbol"):
            u[1] = Q(u[1].replace(bname + "_", name + "_", 1))
        return out
    out = [c if not isinstance(c, list) else c for c in s]
    out = list(out)
    out[1] = Q(lib_id)
    return out


def sym_pins(sym):
    """[(number, name, x, y, angle, hidden)] in library coordinates (y up)."""
    pins = []
    for u in findall(sym, "symbol"):
        for p in findall(u, "pin"):
            at = find(p, "at")
            hidden = any((isinstance(c, list) and c[0] == "hide" and c[1] == "yes") or c == "hide" for c in p)
            pins.append((find(p, "number")[1], find(p, "name")[1], float(at[1]), float(at[2]), float(at[3]), hidden))
    return pins


def sym_bbox(sym):
    xs, ys = [], []
    for u in findall(sym, "symbol"):
        for g in u:
            if not isinstance(g, list):
                continue
            if g[0] == "rectangle":
                for k in ("start", "end"):
                    a = find(g, k); xs.append(float(a[1])); ys.append(float(a[2]))
            elif g[0] in ("polyline", "bezier"):
                for xy in findall(find(g, "pts"), "xy"):
                    xs.append(float(xy[1])); ys.append(float(xy[2]))
            elif g[0] == "circle":
                c = find(g, "center"); r = float(find(g, "radius")[1])
                xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
            elif g[0] == "pin":
                a = find(g, "at"); xs.append(float(a[1])); ys.append(float(a[2]))
    return min(xs), min(ys), max(xs), max(ys)


# ------------------------------------------------------------------------------------------
# Geometry: library (y up) -> schematic (y down), rotation in degrees counter-clockwise on screen
# ------------------------------------------------------------------------------------------
def xform(x, y, rot):
    y = -y
    r = math.radians(-rot)  # screen y is down: CCW on screen is negative in y-down maths
    c, s = round(math.cos(r)), round(math.sin(r))
    return x * c - y * s, x * s + y * c


def pin_dir(angle, rot):
    """Unit vector (screen) pointing outward from the pin end, away from the body."""
    a = math.radians(angle + 180)
    dx, dy = round(math.cos(a)), round(math.sin(a))
    return xform(dx, dy, rot)


# ------------------------------------------------------------------------------------------
# Connect column -> {pin number: net or None (no connect)}
# ------------------------------------------------------------------------------------------
class ConnectError(Exception):
    pass


def resolve_spec(ref, spec, pins):
    """Pin numbers for a pin spec such as '1 VCAP', 'pin 2', 'source', 'D0', 'physical drain (pad 3)'."""
    spec = spec.strip().replace("physical ", "")
    by_num = {p[0]: p for p in pins}
    m = re.search(r"\((?:pad|pin) (\w+)\)", spec)
    if m:
        num = m.group(1)
        name = spec[:m.start()].strip().strip("`")
        check_name(ref, num, name, by_num)
        return [num]
    m = re.fullmatch(r"pin (\w+)", spec)
    if m:
        return [m.group(1)]
    m = re.fullmatch(r"(\d+) (.+)", spec)
    if m:
        check_name(ref, m.group(1), m.group(2), by_num)
        return [m.group(1)]
    if " and " in spec:
        return [n for part in spec.split(" and ") for n in resolve_spec(ref, part, pins)]
    key = norm(spec.strip("`"))
    if key in ALIASES:
        names = ALIASES[key]
        nums = [p[0] for p in pins if p[0] in names] or [p[0] for p in pins if p[1] in names]
        if nums:
            return nums
    nums = [p[0] for p in pins if norm(p[1]) == key]
    if nums:
        return nums
    raise ConnectError(f"{ref}: cannot place pin spec {spec!r} on pins {[(p[0], p[1]) for p in pins]}")


def check_name(ref, num, name, by_num):
    if num not in by_num:
        raise ConnectError(f"{ref}: pin {num} not on symbol")
    if not name:
        return
    a, b = norm(name), norm(by_num[num][1])
    cands = {a, ALIASES.get(a, [a])[0].lower()}
    if not any(c == b or c in b or b in c for c in cands):
        raise ConnectError(f"{ref}: netlist.md calls pin {num} {name!r}, the KiCad symbol calls it {by_num[num][1]!r}")


def parse_connect(ref, text, pins):
    text = text.strip()
    nets = {}
    two = re.fullmatch(r"`([^`]+)` to `([^`]+)`", text)
    if two:
        a, b = two.groups()
        nums = sorted({p[0] for p in pins}, key=lambda n: (len(n), n))
        if nums == ["1", "2", "3", "4"]:  # fuse holder: 1+2 one clip, 3+4 the other
            return {"1": a, "2": a, "3": b, "4": b}
        if nums != ["1", "2"]:
            raise ConnectError(f"{ref}: 'A to B' on a symbol with pins {nums}")
        return {"1": a, "2": b}
    for item in re.split(r";\s*", text):
        item = item.strip()
        if not item:
            continue
        if item.endswith(" open"):
            spec = item[:-5]
            if spec.startswith("all "):
                continue
            for s in re.split(r",\s*", spec):
                for n in resolve_spec(ref, s, pins):
                    nets[n] = None
            continue
        ticks = list(re.finditer(r"`([^`]+)`", item))
        if not ticks:
            raise ConnectError(f"{ref}: no net in {item!r}")
        if len(ticks) >= 2 and item.startswith("`"):  # `5V` `XIAO_5V` / `3V3` (pin 12) `3V3`
            spec, net = item[:ticks[1].start()].strip(), ticks[1].group(1)
            spec = spec.replace("`", "")
        else:
            spec, net = item[:ticks[0].start()].strip(), ticks[0].group(1)
        for n in resolve_spec(ref, spec, pins):
            if n in nets and nets[n] != net:
                raise ConnectError(f"{ref}: pin {n} given two nets")
            nets[n] = net
    return nets


# ------------------------------------------------------------------------------------------
# Values
# ------------------------------------------------------------------------------------------
def derive_value(ref, part):
    p = part.replace("µ", "u")
    if ref.startswith(("R_", "C_", "L")):
        m = re.search(r"(\d+(?:\.\d+)?)\s*(m|k|M|u|n|p)?\s*(Ω|F|H)", p)
        if not m:
            return part
        num, mult, unit = m.group(1), m.group(2) or "", m.group(3)
        if unit == "Ω":  # 4.7 kΩ -> 4k7, 3.3 Ω -> 3R3, 100 kΩ -> 100k
            sep = mult or "R"
            v = num.replace(".", sep) if "." in num else num + sep
        else:
            v = num + mult + unit
        if ref.startswith("C_"):
            mv = re.search(r"(\d+)\s*V\b", p)
            if mv:
                v += " " + mv.group(1) + "V"
        if ref.startswith("R_"):
            mw = re.search(r"(\d+)\s*W\b", p)
            if mw:
                v += " " + mw.group(1) + "W"
        return v
    if ref.startswith("F_"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*A\b", p)
        return m.group(1) + "A" if m else part
    if ref.startswith("JP_"):
        return "NO"
    m = re.match(r"([A-Z0-9][A-Z0-9-]{3,})", part)
    return m.group(1) if m else part


# ------------------------------------------------------------------------------------------
# Build
# ------------------------------------------------------------------------------------------
def rule_for(ref):
    for pat, lib_id, fp, value in RULES:
        if re.match(pat, ref):
            return lib_id, fp, value
    raise SystemExit(f"no part rule for {ref}")


def text_w(s, size=1.27):
    return len(s) * size * 0.85 + 1.0


def build():
    modules, info = parse_netlist_md(os.path.join(REPO, "netlist.md"))
    parts = []  # dicts
    expected = {}
    errors = []
    for num, title, rows in modules:
        for r in rows:
            refs = expand_refs(r[0])
            if not refs:
                errors.append(f"module {num}: cannot read designators {r[0]!r}")
                continue
            for k, ref in enumerate(refs):
                lib_id, fp, value = rule_for(ref)
                sym = flat_symbol(lib_id)
                pins = sym_pins(sym)
                if ref.startswith("TP"):
                    tp_nets = re.findall(r"`([^`]+)`", r[2])
                    nets = {"1": tp_nets[k]}
                    value = tp_nets[k]
                else:
                    try:
                        nets = parse_connect(ref, r[2], pins)
                    except ConnectError as e:
                        errors.append(str(e))
                        continue
                missing = [p[0] for p in pins if p[0] not in nets]
                if missing:
                    errors.append(f"{ref}: pins {missing} not given a net or 'open' in netlist.md")
                inf = info.get(ref, {})
                if "{pkg}" in fp:
                    m = re.search(r"\b(0402|0603|0805|1206|1210)\b", inf.get("part_full", "")) or \
                        re.search(r"\b(0402|0603|0805|1206|1210)\b", r[1])
                    pkg = m.group(1) if m else "0603"
                    fp = fp.format(pkg=pkg, metric=PKG_METRIC[pkg])
                if value is None:
                    value = derive_value(ref, r[1])
                parts.append(dict(ref=ref, module=num, lib_id=lib_id, sym=sym, pins=pins, nets=nets,
                                  fp=fp, value=value, desc=r[1], lcsc=inf.get("lcsc", ""),
                                  mpn=inf.get("part", ""), fit=inf.get("fit", "")))
                expected[ref] = {n: v for n, v in nets.items()}
    refs = [p["ref"] for p in parts]
    dup = {r for r in refs if refs.count(r) > 1}
    if dup:
        errors.append(f"designators used twice: {sorted(dup)}")
    if errors:
        print("netlist.md could not be turned into a schematic:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    for h in MOUNTING:
        sym = flat_symbol("Mechanical:MountingHole")
        parts.append(dict(ref=h, module=0, lib_id="Mechanical:MountingHole", sym=sym, pins=[], nets={},
                          fp="MountingHole:MountingHole_3.2mm_M3", value="M3", desc="M3 mounting hole",
                          lcsc="", mpn="", fit=""))
    for k, net in enumerate(PWR_FLAGS):
        sym = flat_symbol("power:PWR_FLAG")
        parts.append(dict(ref=f"#FLG{k + 1:02d}", module=0, lib_id="power:PWR_FLAG", sym=sym,
                          pins=sym_pins(sym), nets={"1": net}, fp="", value="PWR_FLAG", desc="", lcsc="",
                          mpn="", fit=""))
    return modules, parts, expected


def layout(modules, parts):
    """Place each part in its module's box; boxes flow in columns across the sheet."""
    titles = {n: t for n, t, _ in modules}
    titles[0] = "Mounting holes and power flags"
    order = [n for n, _, _ in modules] + [0]
    col_w = 150.0
    boxes = {}
    for mnum in order:
        mparts = [p for p in parts if p["module"] == mnum]
        x, y, row_h = 0.0, 10.0, 0.0
        for p in mparts:
            pins = p["pins"]
            rot = 0
            if len(pins) == 2 and all(int(pp[4]) in (90, 270) for pp in pins):
                rot = 90  # two-pin symbols drawn vertically (R, C, L, fuse) lie horizontal
            p["rot"] = rot
            bx1, by1, bx2, by2 = sym_bbox(p["sym"])
            pts = [xform(bx1, by1, rot), xform(bx2, by2, rot), xform(bx1, by2, rot), xform(bx2, by1, rot)]
            minx, maxx = min(q[0] for q in pts), max(q[0] for q in pts)
            miny, maxy = min(q[1] for q in pts), max(q[1] for q in pts)
            # room for labels
            ext = {"l": 0.0, "r": 0.0, "u": 0.0, "d": 0.0}
            seen = set()
            for num, name, px, py, ang, hidden in pins:
                if hidden:
                    continue
                sx, sy = xform(px, py, rot)
                if (sx, sy) in seen:
                    continue
                seen.add((sx, sy))
                dx, dy = pin_dir(ang, rot)
                net = p["nets"].get(num)
                w = 2.54 + (text_w(net) if net else 1.0)
                if dx < 0:
                    ext["l"] = max(ext["l"], w - sx)
                elif dx > 0:
                    ext["r"] = max(ext["r"], sx + w)
                elif dy < 0:
                    ext["u"] = max(ext["u"], w - sy)
                else:
                    ext["d"] = max(ext["d"], sy + w)
            left = up_grid(max(-minx, ext["l"]) + 2.0)
            right = up_grid(max(maxx, ext["r"]) + 2.0)
            up = up_grid(max(-miny, ext["u"]) + 4.5)   # reference text above
            down = up_grid(max(maxy, ext["d"]) + 4.5)  # value text below
            w, h = left + right, up + down
            if x > 0 and x + w > col_w:
                x, y = 0.0, y + row_h
                row_h = 0.0
            p["local"] = (x + left, y + up)
            p["fields"] = (up, down)
            x += w
            row_h = max(row_h, h)
        boxes[mnum] = (col_w, up_grid(y + row_h + 4.0))
    # flow boxes into columns of a fixed height
    page_h_target = 360.0
    cols, cur, cur_h = [], [], 0.0
    for mnum in order:
        h = boxes[mnum][1]
        if cur and cur_h + h > page_h_target:
            cols.append(cur); cur, cur_h = [], 0.0
        cur.append(mnum); cur_h += h + 8.0
    cols.append(cur)
    origin = {}
    X0, Y0 = 15.24, 15.24
    for ci, col in enumerate(cols):
        y = Y0
        for mnum in col:
            origin[mnum] = (X0 + ci * (col_w + 10.16), y)
            y += boxes[mnum][1] + 7.62
    width = X0 * 2 + len(cols) * (col_w + 10.16)
    height = max(origin[m][1] + boxes[m][1] for m in order) + 30
    for p in parts:
        ox, oy = origin[p["module"]]
        lx, ly = p["local"]
        p["at"] = (snap(ox + lx), snap(oy + ly))
    frames = [(m, titles[m], origin[m], boxes[m]) for m in order]
    return frames, width, height


def up_grid(v, g=2.54):
    return math.ceil(v / g - 1e-9) * g


def snap(v, g=2.54):
    return round(v / g) * g


def paper_for(w, h):
    for name, pw, ph in (("A3", 420, 297), ("A2", 594, 420), ("A1", 841, 594), ("A0", 1189, 841)):
        if w <= pw and h <= ph:
            return name
    return "A0"


def r4(v):
    return float(round(v, 4))


def effects(size=1.27, justify=None, hide=False):
    e = ["effects", ["font", ["size", size, size]]]
    if justify:
        e.append(["justify"] + justify)
    if hide:
        e.append(["hide", "yes"])
    return e


def symbol_instance(p):
    X, Y = p["at"]
    rot = p["rot"]
    up, down = p["fields"]
    props = [
        ("Reference", p["ref"], (X, Y - up + 1.5), False),
        ("Value", p["value"], (X, Y + down - 1.5), False),
        ("Footprint", p["fp"], (X, Y), True),
        ("Datasheet", "", (X, Y), True),
        ("Description", p["desc"], (X, Y), True),
    ]
    if p["lcsc"]:
        props.append(("LCSC", p["lcsc"], (X, Y), True))
    if p["mpn"]:
        props.append(("MPN", p["mpn"], (X, Y), True))
    if p["fit"]:
        props.append(("Fit", p["fit"], (X, Y), True))
    in_bom = "no" if NOT_IN_BOM.match(p["ref"]) or p["ref"].startswith("#") else "yes"
    on_board = "no" if p["ref"].startswith("#") else "yes"
    node = ["symbol", ["lib_id", Q(p["lib_id"])], ["at", r4(X), r4(Y), rot], ["unit", 1],
            ["exclude_from_sim", "no"], ["in_bom", in_bom], ["on_board", on_board], ["dnp", "no"],
            ["uuid", Q(uid("sym/" + p["ref"]))]]
    hide_value = p["ref"].startswith("#")
    for k, v, (x, y), hide in props:
        hide = hide or (k in ("Value", "Reference") and hide_value)
        # field angles are stored before the symbol's rotation is applied: undo it so text reads level
        node.append(["property", Q(k), Q(v), ["at", r4(x), r4(y), p["rot"]], effects(hide=hide)])
    for num, *_ in p["pins"]:
        node.append(["pin", Q(num), ["uuid", Q(uid(f"pin/{p['ref']}/{num}"))]])
    node.append(["instances", ["project", Q(PROJECT), ["path", Q("/" + ROOT_UUID),
                                                     ["reference", Q(p["ref"])], ["unit", 1]]]])
    return node


def wiring(p):
    """Wire stub + label (or no-connect flag) on every pin."""
    X, Y = p["at"]
    out = []
    seen = set()
    for num, name, px, py, ang, hidden in p["pins"]:
        sx, sy = xform(px, py, p["rot"])
        ex, ey = X + sx, Y + sy
        key = (round(ex, 3), round(ey, 3))
        net = p["nets"].get(num)
        if key in seen:
            continue
        seen.add(key)
        tag = f"{p['ref']}/{num}"
        if net is None:
            out.append(["no_connect", ["at", r4(ex), r4(ey)], ["uuid", Q(uid("nc/" + tag))]])
            continue
        dx, dy = pin_dir(ang, p["rot"])
        lx, ly = ex + dx * 2.54, ey + dy * 2.54
        out.append(["wire", ["pts", ["xy", r4(ex), r4(ey)], ["xy", r4(lx), r4(ly)]],
                    ["stroke", ["width", 0], ["type", "default"]], ["uuid", Q(uid("w/" + tag))]])
        if dx > 0:
            ang_l, just = 0, ["left", "bottom"]
        elif dx < 0:
            ang_l, just = 180, ["right", "bottom"]
        elif dy < 0:
            ang_l, just = 90, ["left", "bottom"]
        else:
            ang_l, just = 270, ["right", "bottom"]
        out.append(["label", Q(net), ["at", r4(lx), r4(ly), ang_l], ["fields_autoplaced", "yes"],
                    effects(justify=just), ["uuid", Q(uid("l/" + tag))]])
    return out


def main():
    modules, parts, expected = build()
    frames, w, h = layout(modules, parts)
    paper = paper_for(w, h)
    version = open(os.path.join(REPO, "VERSION.txt")).readline().strip()
    lib_ids = sorted({p["lib_id"] for p in parts})
    sch = ["kicad_sch", ["version", 20250114], ["generator", Q("eeschema")], ["generator_version", Q("9.0")],
           ["uuid", Q(ROOT_UUID)], ["paper", Q(paper)],
           ["title_block", ["title", Q("12 V vehicle UPS power board")], ["date", Q(date.today().isoformat())],
            ["rev", Q(version)], ["comment", 1, Q("Generated from netlist.md by kicad/gen/gen_sch.py. "
                                                  "Edit netlist.md, not this sheet.")],
            ["comment", 2, Q("Every pin carries a net label; labels with the same name are connected.")]],
           ["lib_symbols"] + [flat_symbol(l) for l in lib_ids]]
    for mnum, title, (ox, oy), (bw, bh) in frames:
        sch.append(["rectangle", ["start", r4(ox - 2.54), r4(oy)], ["end", r4(ox + bw), r4(oy + bh)],
                    ["stroke", ["width", 0.3], ["type", "dash"]], ["fill", ["type", "none"]],
                    ["uuid", Q(uid(f"box/{mnum}"))]])
        label = f"Module {mnum} — {title}" if mnum else title
        sch.append(["text", Q(label), ["exclude_from_sim", "no"], ["at", r4(ox), r4(oy + 5.08), 0],
                    ["effects", ["font", ["size", 2.54, 2.54], ["thickness", 0.5], ["bold", "yes"]],
                     ["justify", "left", "bottom"]], ["uuid", Q(uid(f"title/{mnum}"))]])
    for p in parts:
        sch.extend(wiring(p))
    for p in parts:
        sch.append(symbol_instance(p))
    sch.append(["sheet_instances", ["path", Q("/"), ["page", Q("1")]]])
    sch.append(["embedded_fonts", "no"])
    out = os.path.join(KICAD, PROJECT + ".kicad_sch")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(sexpr.dump(sch) + "\n")
    os.makedirs(os.path.join(KICAD, "out"), exist_ok=True)
    with open(os.path.join(KICAD, "out", "expected.json"), "w") as f:
        json.dump(expected, f, indent=1, sort_keys=True)
    print(f"wrote {out}: {len(parts)} symbols, paper {paper} ({w:.0f} x {h:.0f} mm)")


if __name__ == "__main__":
    main()
