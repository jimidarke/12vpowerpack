"""Print the pins (number, name, type) of KiCad library symbols: libpins.py LIB:SYM ..."""
import sys, os
from kiutils.symbol import SymbolLib
STOCK = "/usr/share/kicad/symbols"
HERE = os.path.dirname(os.path.abspath(__file__))
def libpath(lib):
    p = os.path.join(HERE, "..", "lib", lib + ".kicad_sym")
    return p if os.path.exists(p) else os.path.join(STOCK, lib + ".kicad_sym")
def find(lib, name):
    sl = SymbolLib.from_file(libpath(lib))
    syms = {s.entryName: s for s in sl.symbols}
    s = syms[name]
    fp = [p.value for p in s.properties if p.key == "Footprint"]
    while s.extends:
        s = syms[s.extends]
    return s, fp
for arg in sys.argv[1:]:
    lib, name = arg.split(":")
    s, fp = find(lib, name)
    pins = [(p.number, p.name, p.electricalType) for u in s.units for p in u.pins]
    print(f"{arg}  fp={fp}  " + "  ".join(f"{n}:{nm}" for n, nm, t in sorted(pins, key=lambda x: (len(x[0]), x[0]))))
