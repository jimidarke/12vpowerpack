"""Check kicad/powerpack.kicad_sch against netlist.md.

    python3 kicad/gen/check_sch.py [--no-upgrade]

1. Upgrades the schematic to the native KiCad 10 format (kicad-cli sch upgrade), unless
   --no-upgrade.
2. Runs ERC (report in kicad/out/erc.rpt).
3. Exports KiCad's netlist and compares every pin with kicad/out/expected.json, which
   gen_sch.py writes from netlist.md. Pins marked 'open' must be on no net (or a one-pin
   unconnected net).
Exit status 0 only when the netlist matches exactly.
"""
import json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexpr
from sexpr import find, findall

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD = os.path.normpath(os.path.join(HERE, ".."))
SCH = os.path.join(KICAD, "powerpack.kicad_sch")
OUT = os.path.join(KICAD, "out")


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode not in (0, 5):  # 5: ERC found violations (--exit-code-violations)
        print(r.stdout, r.stderr)
        raise SystemExit(f"failed: {' '.join(args)}")
    return r


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--no-upgrade" not in sys.argv:
        run("kicad-cli", "sch", "upgrade", "--force", SCH)
    erc = os.path.join(OUT, "erc.rpt")
    run("kicad-cli", "sch", "erc", "--severity-all", "-o", erc, SCH)
    net = os.path.join(OUT, "powerpack.net")
    run("kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, SCH)

    tree = sexpr.parse(open(net, encoding="utf-8").read())
    got = {}  # (ref, pin) -> net
    for n in findall(find(tree, "nets"), "net"):
        name = find(n, "name")[1].lstrip("/")
        nodes = findall(n, "node")
        for node in nodes:
            ref, pin = find(node, "ref")[1], find(node, "pin")[1]
            unconnected = name.startswith("unconnected-") or (len(nodes) == 1 and name.startswith("Net-"))
            got[(ref, pin)] = None if unconnected else name

    expected = json.load(open(os.path.join(OUT, "expected.json")))
    problems = []
    for ref, pins in sorted(expected.items()):
        for pin, net in sorted(pins.items()):
            g = got.get((ref, pin), None)
            if g != net:
                problems.append(f"{ref} pin {pin}: netlist.md {net or 'open'}, KiCad {g or 'open'}")
    for (ref, pin), g in sorted(got.items()):
        if ref not in expected and g:
            problems.append(f"{ref} pin {pin}: on {g} in KiCad but not in netlist.md")

    nets = {}
    for (ref, pin), g in got.items():
        if g:
            nets.setdefault(g, []).append(f"{ref}.{pin}")
    single = sorted(n for n, m in nets.items() if len(m) == 1)

    # ERC summary
    rpt = open(erc, encoding="utf-8").read()
    kinds = {}
    for m in re.finditer(r"^\[(\w+)\]: (.*)$", rpt, re.M):
        kinds.setdefault(m.group(1), [0, m.group(2)])[0] += 1
    print(f"KiCad netlist: {len(nets)} nets, {sum(len(v) for v in nets.values())} connected pins")
    if single:
        print("nets with a single pin:", ", ".join(single))
    print("ERC:", "clean" if not kinds else "")
    for k, (count, msg) in sorted(kinds.items()):
        print(f"  {count:3d} x {k}: {msg}")
    if problems:
        print(f"MISMATCH ({len(problems)}):")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("netlist matches netlist.md pin for pin")


if __name__ == "__main__":
    main()
