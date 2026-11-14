# Block 0 — reset the project to v3

**Goal:** clear the cancelled lithium work and give the project one short, current specification. No capture in this message.

**Status:** sent on the root thread 2026-11-13 and verified (0 components, 0 nets, spec replaced, three old documents bannered); 0.9 credits. The message as sent also asked the agent to work without delegating and to reply in three lines.

## Message
1. Delete all 31 placed components (all are in Functional Group `Li Protector`). The lithium build is cancelled.
2. Replace the content of document `power-board-requirements-v2` with the attached specification, unchanged, and title it "Power board specification v3".
3. Put this one line at the top of `power-board-architecture`, `bms-capture-handoff` and `block-1-capture-status`, and change nothing else in them: "SUPERSEDED by Power board specification v3. Do not use."
4. Do not place parts, do not research, do not draft. If something in the specification conflicts, list it and stop.

Reply with the component count, the net count and the document list.

## Done when
0 components, 0 nets; the specification document holds the attached text; the three old documents carry the banner.

## Attachment — Power board specification v3

### Product
A small in-vehicle UPS on one PCB. One build only. A 12 V sealed AGM battery is floated on the car's charging voltage through a charge resistor. Outputs: 12 V unregulated pass-through and 5 V USB-A. A socketed Seeed XIAO ESP32-C6 times the shutdown and reports status.

Cancelled and not to be reintroduced: lithium cells and protector, charger IC, USB-C PD input, 12 V converter, display.

### Electrical summary
- Input: ignition-switched car feed, 11–14.8 V. 10 A fuse, SMCJ18CA clamp, LM74700-Q1 ideal diode (reverse polarity, no backfeed to the car).
- Battery: 12 V AGM on a 10 A fuse. Charge path `SYS` → 1.6 A time-lag fuse → 3.3 Ω 10 W → `VBAT`. Discharge path through a second LM74700-Q1 ideal diode, `VBAT` → `SYS`.
- 12 V output: `LOAD` through a P-channel FET and a 7.5 A fuse to a barrel jack. 3 A continuous, 5 A peak. Unregulated, about 10.9–14.8 V.
- 5 V: LMR33630ADDA, 400 kHz, 2 A USB-A through a TPS2514A.
- Low-voltage cutoff: the LMR33630 EN divider (887 kΩ / 102 kΩ) switches the 5 V rail off below 10.97 V and on above 11.94 V. The LMR33630 PG pin drives the 12 V output FET, so both outputs share the cutoff.
- Hold-up: `EN_SRC` is fed from the car feed through a diode, or from `SYS` through a BSS84 that the XIAO turns on with `HOLD`. When the XIAO releases `HOLD` after ignition-off, the whole board switches off until the car feed returns.
- Monitoring: two INA226 (0x40 on the car input shunt, 0x41 on the load shunt), battery and car voltage dividers to XIAO ADC pins, DS18B20 probe, one SK6812 status LED.

### Rules
- Safety never depends on the XIAO. Fuses, charge limit, ideal diodes and the low-voltage cutoff are hardware.
- All parts are rated −40 to 85 °C or better, except the barrel jack (accepted).
- One ground net, `GND`.

### Capture rules for the agent
- Each capture message attaches a parts table and a pin-to-net table. Those tables are authoritative: use the designators, values and net names exactly as written.
- Every value and pin number in the tables is already verified against the datasheets. Do not research and do not open datasheets. If a pin name in a library symbol does not match the table, stop and ask.
- One block per message. Schematic capture only: no layout, no documents, no part substitutions.
- To save credits: use the library part given for each designator without searching for alternatives; set only the value, MPN and the block's Functional Group on each part (no Role Details or design notes); do not run or fix the electrical check unless asked; work in this thread without delegating if you can.
- Keep replies short: counts, and any pin-name mismatch. The owner verifies the netlist separately.
