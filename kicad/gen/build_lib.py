"""Build the project library kicad/lib/pwrpack.{pretty,kicad_sym,3dshapes}.

Run with the system python3 (it needs the pcbnew module from KiCad 10):
    python3 kicad/gen/build_lib.py

Sources:
- lib/lcsc.* : pulled with easyeda2kicad (C352820 Keystone 3557-2, C6264900 Wurth 61400416021,
  C1329351 SRP6540 body). Converted here to KiCad 10 format and renamed.
- The XIAO socket, AC10, SRP6540 and fuse-holder parts are drawn here from the datasheet
  dimensions cited next to each one.
"""
import os, shutil, uuid
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.normpath(os.path.join(HERE, "..", "lib"))
PRETTY = os.path.join(LIB, "pwrpack.pretty")
SHAPES = os.path.join(LIB, "pwrpack.3dshapes")
LCSC = os.path.join(LIB, "lcsc.pretty")
MODEL = "${KIPRJMOD}/lib/pwrpack.3dshapes/"
os.makedirs(PRETTY, exist_ok=True)
os.makedirs(SHAPES, exist_ok=True)


def uid(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "pwrpack-lib/" + tag))


def write_fp(name, body):
    with open(os.path.join(PRETTY, name + ".kicad_mod"), "w") as f:
        f.write(body)


def rect(layer, x1, y1, x2, y2, w, tag):
    return (f'\t(fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f})\n'
            f'\t\t(stroke (width {w}) (type solid)) (fill no) (layer "{layer}") (uuid "{uid(tag)}"))\n')


def text(kind, val, x, y, layer, tag, hide=False):
    h = " (hide yes)" if hide else ""
    return (f'\t(property "{kind}" "{val}" (at {x:.3f} {y:.3f} 0) (layer "{layer}"){h} (uuid "{uid(tag)}")\n'
            f'\t\t(effects (font (size 1 1) (thickness 0.15))))\n')


def header(name, descr, attr):
    return (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "pwrpack-build_lib")\n'
            f'\t(layer "F.Cu")\n\t(descr "{descr}")\n\t(attr {attr})\n')


def tht(num, x, y, size, drill, shape="circle", tag=""):
    return (f'\t(pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {size} {size}) (drill {drill})\n'
            f'\t\t(layers "*.Cu" "*.Mask") (uuid "{uid(tag or num + str(x) + str(y))}"))\n')


def model(fname):
    return (f'\t(model "{MODEL}{fname}"\n\t\t(offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n')


# --- XIAO ESP32-C6 on two 1x7 2.54 mm female headers --------------------------------------
# Seeed XIAO: 21 x 17.5 mm, two rows of 7 at 2.54 mm, rows 15.24 mm apart (checked against
# the Flux footprint: 1.1 mm holes, 15.24 mm rows). Pin 1 (D0) top left with the USB-C end
# at the top (y negative); left row 1-7 = D0-D6, right row bottom to top 8-14 = D7, D8, D9,
# D10, 3V3, GND, 5V.
def xiao():
    n = "XIAO_ESP32C6_Socketed_2x1x07_P2.54mm"
    s = header(n, "Seeed XIAO ESP32-C6 in two 1x7 2.54 mm female headers, rows 15.24 mm apart. "
               "USB-C end at the top; antenna end at the bottom", "through_hole")
    s += text("Reference", "REF**", 0, -12.5, "F.SilkS", n + "ref")
    s += text("Value", "XIAO_ESP32C6", 0, 12.5, "F.Fab", n + "val")
    for i in range(7):
        y = -7.62 + i * 2.54
        s += tht(str(i + 1), -7.62, y, 1.7, 1.0, "rect" if i == 0 else "circle")
        s += tht(str(14 - i), 7.62, y, 1.7, 1.0)
    s += rect("F.Fab", -8.75, -10.5, 8.75, 10.5, 0.1, n + "fab")
    s += rect("F.Fab", -4.5, -11.5, 4.5, -8.5, 0.1, n + "usb")  # USB-C plug
    s += rect("F.SilkS", -8.87, -10.62, 8.87, 10.62, 0.12, n + "silk")
    s += rect("F.CrtYd", -9.25, -12.0, 9.25, 11.0, 0.05, n + "crt")
    s += ('\t(fp_text user "USB" (at 0 -9.3 0) (layer "F.SilkS") (uuid "' + uid(n + "usbt") +
          '")\n\t\t(effects (font (size 0.8 0.8) (thickness 0.12))))\n')
    s += ('\t(fp_text user "ANT" (at 0 9.3 0) (layer "F.SilkS") (uuid "' + uid(n + "antt") +
          '")\n\t\t(effects (font (size 0.8 0.8) (thickness 0.12))))\n')
    s += model("XIAO_ESP32C6_Socketed.step")  # from build_models.py
    write_fp(n, s + ")\n")


# --- Vishay AC10, kinked "EK" leads, 52 mm pitch ------------------------------------------
# [DS Vishay AC] AC10: L max 44.0, D max 8.0, lead d 0.8 +/- 0.03, EK pitch 52 mm (code N).
def ac10():
    n = "R_Axial_Vishay_AC10_EK_L44.0mm_D8.0mm_P52.00mm"
    s = header(n, "Vishay AC10 cemented wirewound, single-kink EK leads, 52 mm pitch, body 44 x 8 mm. "
               "Mount raised 3-5 mm", "through_hole")
    s += text("Reference", "REF**", 26, -5.5, "F.SilkS", n + "ref")
    s += text("Value", "AC10", 26, 5.5, "F.Fab", n + "val")
    s += tht("1", 0, 0, 2.2, 1.2, "rect")
    s += tht("2", 52, 0, 2.2, 1.2)
    s += rect("F.Fab", 4, -4, 48, 4, 0.1, n + "fab")
    s += rect("F.SilkS", 3.88, -4.12, 48.12, 4.12, 0.12, n + "silk")
    s += rect("F.CrtYd", -1.35, -4.5, 53.35, 4.5, 0.05, n + "crt")
    s += model("R_Axial_Vishay_AC10.step")  # from build_models.py
    write_fp(n, s + ")\n")


# --- Bourns SRP6540 ----------------------------------------------------------------------
# [DS SRP6540] body 7.20 x 6.50 mm, 4.0 mm max height. Recommended layout read as: outer span
# 7.40, gap 3.40, pad height 3.70, so each pad 2.00 x 3.70 at x = +/-2.70.
def srp6540():
    n = "L_Bourns_SRP6540_7.2x6.5mm"
    s = header(n, "Bourns SRP6540 shielded power inductor, 7.2 x 6.5 x 4.0 mm, Bourns recommended layout",
               "smd")
    s += text("Reference", "REF**", 0, -4.6, "F.SilkS", n + "ref")
    s += text("Value", "SRP6540", 0, 4.6, "F.Fab", n + "val")
    for num, x in (("1", -2.7), ("2", 2.7)):
        s += (f'\t(pad "{num}" smd roundrect (at {x} 0) (size 2.0 3.7) (layers "F.Cu" "F.Mask" "F.Paste")\n'
              f'\t\t(roundrect_rratio 0.125) (uuid "{uid(n + num)}"))\n')
    s += rect("F.Fab", -3.6, -3.25, 3.6, 3.25, 0.1, n + "fab")
    s += ('\t(fp_line (start -3.72 -3.37) (end 3.72 -3.37) (stroke (width 0.12) (type solid)) '
          f'(layer "F.SilkS") (uuid "{uid(n + "s1")}"))\n')
    s += ('\t(fp_line (start -3.72 3.37) (end 3.72 3.37) (stroke (width 0.12) (type solid)) '
          f'(layer "F.SilkS") (uuid "{uid(n + "s2")}"))\n')
    s += rect("F.CrtYd", -4.0, -3.65, 4.0, 3.65, 0.05, n + "crt")
    s += model("IND-SMD_L7.2-W6.6-H3.0_GPSR07X0.step")
    write_fp(n, s + ")\n")


# --- Converted from easyeda2kicad --------------------------------------------------------
def convert(src, dst, model_file, rename_pads=None, descr=""):
    fp = pcbnew.FootprintLoad(LCSC, src)
    fp.SetFPID(pcbnew.LIB_ID("pwrpack", dst))
    if descr:
        fp.SetLibDescription(descr)
    for pad in fp.Pads():
        if rename_pads and pad.GetNumber() in rename_pads:
            pad.SetNumber(rename_pads[pad.GetNumber()])
    models = fp.Models()
    for i in range(len(models)):
        models[i].m_Filename = MODEL + model_file
    fp.SetValue(dst)
    pcbnew.FootprintSave(PRETTY, fp)
    os.replace(os.path.join(PRETTY, src + ".kicad_mod") if os.path.exists(os.path.join(PRETTY, src + ".kicad_mod"))
               else os.path.join(PRETTY, dst + ".kicad_mod"), os.path.join(PRETTY, dst + ".kicad_mod"))


def copy_models():
    for f in ("FUSE-TH_4P-L19.8-W6.7_3557-2.step", "USB-A-TH_61400416021.step",
              "IND-SMD_L7.2-W6.6-H3.0_GPSR07X0.step"):
        src = os.path.join(LIB, "lcsc.3dshapes", f)  # not in git; re-pull with easyeda2kicad if needed
        if os.path.exists(src):
            shutil.copy(src, os.path.join(SHAPES, f))


# --- Symbols -----------------------------------------------------------------------------
def pin(num, name, typ, x, y, ang, length=2.54, hide=False):
    h = " (hide yes)" if hide else ""
    return (f'\t\t\t(pin {typ} line (at {x} {y} {ang}) (length {length}){h}\n'
            f'\t\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27)))))\n')


def prop(k, v, x, y, hide=False, ang=0):
    h = " (hide yes)" if hide else ""
    return (f'\t\t(property "{k}" "{v}" (at {x} {y} {ang})\n'
            f'\t\t\t(effects (font (size 1.27 1.27)){h}))\n')


def sym(name, ref, value, fp, descr, body, pins, pin_names_offset=None, hide_pin_numbers=False):
    s = f'\t(symbol "{name}"\n'
    if pin_names_offset is not None:
        s += f'\t\t(pin_names (offset {pin_names_offset}))\n'
    if hide_pin_numbers:
        s += '\t\t(pin_numbers (hide yes))\n'
    s += '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
    s += prop("Reference", ref, 0, 6.35) + prop("Value", value, 0, -6.35)
    s += prop("Footprint", fp, 0, -8.89, True) + prop("Datasheet", "", 0, 0, True)
    s += prop("Description", descr, 0, 0, True)
    s += f'\t\t(symbol "{name}_0_1"\n{body}\t\t)\n'
    s += f'\t\t(symbol "{name}_1_1"\n{pins}\t\t)\n\t)\n'
    return s


def poly(pts, w=0.254, fill="none"):
    p = " ".join(f"(xy {x} {y})" for x, y in pts)
    return f'\t\t\t(polyline (pts {p}) (stroke (width {w}) (type default)) (fill (type {fill})))\n'


def rectg(x1, y1, x2, y2, fill="background"):
    return (f'\t\t\t(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default)) '
            f'(fill (type {fill})))\n')


def symbols():
    out = '(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "pwrpack-build_lib")\n'
    # Keystone 3557-2: pads 1+2 are one clip, 3+4 the other ([DS Keystone 3557]: 3.4 mm within
    # a pair, 13.5 mm between pairs; the footprint puts 1,2 at x=-6.74 and 3,4 at x=+6.74).
    body = rectg(-2.54, -1.016, 2.54, 1.016, "none") + poly([(-2.54, 0), (2.54, 0)])
    pins = (pin("1", "~", "passive", -5.08, 0, 0) + pin("2", "~", "passive", -5.08, 0, 0, hide=True) +
            pin("3", "~", "passive", 5.08, 0, 180) + pin("4", "~", "passive", 5.08, 0, 180, hide=True))
    out += sym("Fuseholder_3557-2", "F", "3557-2", "pwrpack:Fuseholder_Blade_ATO_Keystone_3557-2",
               "Keystone 3557-2 ATO/ATC blade fuse holder; pins 1+2 one clip, 3+4 the other", body, pins,
               pin_names_offset=0, hide_pin_numbers=True)
    # XIAO ESP32-C6, 14 pins
    left = [("1", "D0"), ("2", "D1"), ("3", "D2"), ("4", "D3"), ("5", "D4"), ("6", "D5"), ("7", "D6")]
    right = [("14", "5V", "power_in"), ("13", "GND", "power_in"), ("12", "3V3", "power_out"),
             ("11", "D10", "bidirectional"), ("10", "D9", "bidirectional"), ("9", "D8", "bidirectional"),
             ("8", "D7", "bidirectional")]
    body = rectg(-7.62, 10.16, 7.62, -10.16)
    pins = ""
    for i, (n, nm) in enumerate(left):
        pins += pin(n, nm, "bidirectional", -12.7, 7.62 - i * 2.54, 0, 5.08)
    for i, (n, nm, t) in enumerate(right):
        pins += pin(n, nm, t, 12.7, 7.62 - i * 2.54, 180, 5.08)
    s = sym("XIAO_ESP32C6", "J", "XIAO_ESP32C6", "pwrpack:XIAO_ESP32C6_Socketed_2x1x07_P2.54mm",
            "Seeed XIAO ESP32-C6, socketed. D0 GPIO0, D1 GPIO1, D2 GPIO2, D3 GPIO21, D4 GPIO22, "
            "D5 GPIO23, D6 GPIO16, D7 GPIO17, D8 GPIO19, D9 GPIO20, D10 GPIO18", body, pins)
    out += s.replace('(property "Reference" "J" (at 0 6.35 0)', '(property "Reference" "J" (at 0 11.43 0)') \
            .replace('(property "Value" "XIAO_ESP32C6" (at 0 -6.35 0)', '(property "Value" "XIAO_ESP32C6" (at 0 -11.43 0)')
    # DMP4015SK3 P-MOSFET, TO-252: G 1, D 2 (tab), S 3 [DS DMP4015SK3]
    body = (poly([(0.254, 1.905), (0.254, -1.905)]) + poly([(0.762, 2.286), (0.762, 1.27)]) +
            poly([(0.762, 0.508), (0.762, -0.508)]) + poly([(0.762, -1.27), (0.762, -2.286)]) +
            poly([(0.762, -1.778), (3.302, -1.778), (3.302, 1.778), (0.762, 1.778)]) +
            poly([(2.286, 1.778), (2.286, 2.54)]) + poly([(2.286, -1.778), (2.286, -2.54)]) +
            poly([(0.762, 0), (2.286, 0), (2.286, -1.778)]) +
            poly([(2.032, 0.381), (1.524, 0), (2.032, -0.381), (2.032, 0.381)], fill="outline"))
    pins = (pin("1", "G", "input", -5.08, 0, 0, 5.334) + pin("2", "D", "passive", 2.54, 5.08, 270) +
            pin("3", "S", "passive", 2.54, -5.08, 90))
    s = sym("DMP4015SK3", "Q", "DMP4015SK3", "Package_TO_SOT_SMD:TO-252-2",
            "Diodes DMP4015SK3 P-channel MOSFET, -40 V, 11 mOhm, TO-252 (tab = drain)", body, pins,
            pin_names_offset=0, hide_pin_numbers=True)
    out += s
    out += ")\n"
    with open(os.path.join(LIB, "pwrpack.kicad_sym"), "w") as f:
        f.write(out)


if __name__ == "__main__":
    xiao(); ac10(); srp6540()
    convert("FUSE-TH_4P-L19.8-W6.7_3557-2", "Fuseholder_Blade_ATO_Keystone_3557-2",
            "FUSE-TH_4P-L19.8-W6.7_3557-2.step",
            descr="Keystone 3557-2 ATO/ATC blade fuse holder, 30 A. Pads 1+2 one clip, 3+4 the other "
                  "(13.5 mm between pairs, 3.4 mm within a pair)")
    convert("USB-A-TH_61400416021", "USB_A_Wuerth_61400416021_Horizontal", "USB-A-TH_61400416021.step",
            rename_pads={"SH1": "SH", "SH2": "SH"},
            descr="Wurth 61400416021 USB-A receptacle, horizontal, THT. Opening at +Y")
    copy_models()
    symbols()
    print("built", sorted(os.listdir(PRETTY)))
