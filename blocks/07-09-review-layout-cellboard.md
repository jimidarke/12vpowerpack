# Blocks 7–9 — review, layout, cell board (outlines; detailed when reached)

## Block 7 — whole-schematic check and price checkpoint
Message: run the electrical/connectivity check on the full schematic and fix concrete faults only; then report the BOM with unit prices at quantity 12 and flag any part that is out of stock or not available for fab assembly. No new features, no layout.

Then, here: read `get_bom`, total it for each build variant, compare with the $75–110 target, and apply the cut list in this order if needed: USB-C output port → 5 V INA226 → USB-C PD input (barrel-jack laptop brick instead) → hand-assemble the easy parts.

## Block 8 — layout (three separate messages)
1. Board outline, stackup (4-layer, 2 oz outer if priced sensibly), connector placement on the edges, block placement following power flow. Review with `get_layout` / `get_layout_image`.
2. Route power stages first (charger and 12 V converter loops per their datasheet layout sections), then the rest.
3. Design-rule check, then manufacturing files and a fab-assembly BOM/placement file.

## Block 9 — cell board (new, small Flux project)
Four PCB-mount 18650 holders in series, 10 A pack fuse, tap protection, 103AT NTC, XT30 + JST-XH-5 + JST-XH-2 matching the main board pinout exactly. Settle before sending: holder part and its current rating; button-top vs flat-top cells; tap series element value against the 33 Ω balance filter.
