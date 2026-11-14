# Agent message templates (v3)

The owner draws the schematic by hand from `netlist.md`. Send an agent message only when the owner asks, one objective per message, on the root thread.

## Template 1 — place parts only (used three times on 2026-11-13; 0.7–1.3 credits per run)

Message:

Place parts only. No wiring. Add every part in the attached list in ONE schematic edit, unwired, in free space.

- Do not touch, move, rewire or delete anything already on the schematic.
- Use exactly the library part at each link or UID; resistors and capacitors are Generic Resistor / Generic Capacitor with only designator and value set.
- Set no other properties. No research, no review, no electrical check.
- If an edit fails, do not retry: stop and report.
- Reply in three lines: parts placed, parts skipped, nothing else.

Attachment: a table of designator, library link or UID, and value.

Watch the run with `wait_for_thread`; if it starts retrying a failed edit, send "Stop now" on the same thread.

## Template 2 — capture one module (not used so far)

Use only for a module the owner asks the agent to wire. The attachment is the "Nets" table, the module's rows of the "Flux library parts" table, and the module's own table and check line, copied from `netlist.md`.

## Message (replace N and the name)

Module N — NAME. Schematic capture only.

1. Place every part in the attached module table, with the designators and values as written. Use the library part listed for each designator; do not search for alternatives.
2. Wire every pin as in the table, using the net names as written. Nets that leave the module are labels only.
3. Set only value and MPN on each part: no Role Details, no design notes.

All values and pin numbers are verified; do not research or open datasheets. Match source, gate, drain, anode and cathode by pin name on the symbol. If a symbol's pin names do not fit the table, stop and ask.

Do not change any existing part or wire. No layout. Do not run or fix the electrical check. To save credits, work in this thread without delegating if you can, and reply in five lines or fewer: parts placed, nets created, any mismatch.

## Done when
The module's check line in `netlist.md` holds when read back with `get_components` and `get_nets`.
