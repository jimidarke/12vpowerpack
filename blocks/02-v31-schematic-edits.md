# v3.1 schematic edits (2026-11-14)

Brings the Flux schematic from the verified v3 capture (80 parts) to `netlist.md` v3.1 (77 parts). Part A is hand work in the Flux editor (free). Part B is an optional agent message for the bulk property edits; it is **not sent**. Send it only when the owner says go, on the root thread, and log it in `flux-log.md`.

After both parts, ask for a "check": `get_components`, `get_nets` and `get_bom` compared pin by pin with `netlist.md`.

## A. Hand edits in the Flux editor (free)

Do them in this order, and read back after step 4 if in doubt.

1. **USB (module 4):** delete U_USB. Wire J_USBA D+ to J_USBA D− and name the net `USB_D`. The nets `USB_DP` and `USB_DM` should then be gone; delete them if they linger.
2. **LED (module 6):** delete D_STAT, D_LED, C_LED and R_LED. Delete the nets `LED_VDD` and `LED_DIN_R` if they linger. Rename `LED_DIN` (now only on J_XIAO D10) to `LED_G`.
3. **New LEDs (module 6):** place two Generic Resistors, R_LG and R_LR, at 1 kΩ, and two 0603 LEDs:
   - D_RED: KT-0603R, LCSC C2286, Flux part https://www.flux.ai/adrian95/kt-0603r~7c (check the anode and cathode pin names on the symbol).
   - D_GRN: KT-0603YG, yellow-green, 2.0–2.2 V, LCSC C2289 (search the Flux library for it, or use a generic 0603 LED and set the MPN). **Not** the KT-0603G (C12624), which is a 3.1 V emerald green and would barely light from 3.3 V through 1 kΩ.
   - Wire them: J_XIAO D10 `LED_G` → R_LG → `LED_G_A` → D_GRN anode, cathode `GND`. J_XIAO D9 `LED_R` → R_LR → `LED_R_A` → D_RED anode, cathode `GND`.
4. **Spares and empty nets:** delete R1 and C1, and the empty nets `Net 1`, `J_12V` and `C_SYSIN`.
5. **F_BAT:** set the current rating to 10 A (it is at the symbol's 5 A default).
6. **D_TVS:** replace the Liown part with https://www.flux.ai/lcsc/smcj18caq-13-f~qsgb and rewire pin 1 `VIN_CAR`, pin 2 `GND` (bidirectional, either way round).

7. **D_5V:** replace the B140B (SMB) with a B5819W SOD-123 library part (LCSC C64885, MDD) and rewire anode `5V`, cathode `XIAO_5V`. If no library part turns up, keep the symbol and change the footprint and MPN with the properties in part B.
8. **Test points (optional here):** TP1–TP8 on `VIN_CAR`, `SYS`, `LOAD`, `VBAT`, `5V`, `3V3`, `EN_5V`, `GND`. They can also be bare pads added at layout. If placed now, the part count is 85, not 77.

Expected after part A, without test points: 77 parts. `USB_D` holds 2 pins, `LED_G` 2, `LED_G_A` 2, `LED_R` 2, `LED_R_A` 2. `GND` gains D_GRN and D_RED and loses U_USB, D_STAT and C_LED.

## B. Agent message: set properties only (draft, not sent)

The agent only sets properties on parts that are already placed; there is no wiring. Expected cost is about 1 credit, judging by the place-only runs at 0.7–1.3. Doing it by hand is also fine; it is about 60 property edits.

Message:

> Set properties only. Do not place, move, wire, rewire or delete anything.
>
> For each designator in the attached table, set exactly the properties listed (Package, MPN, Manufacturer, LCSC part number, Value where given) in ONE edit. Set no other properties. No research, no review, no electrical check.
>
> If a property cannot be set on a part, skip that part and carry on; do not retry. If an edit fails, stop and report.
>
> Reply in three lines: parts updated, parts skipped (with the reason), nothing else.

Attachment: the "LCSC part table" from `netlist.md`, cut down to the columns designator, value, package, MPN, manufacturer and LCSC number. Leave out the hand-soldered through-hole rows, whose footprints are set at layout.

## C. Footprints still to settle before layout (not part of A or B)

- **F_IN, F_BAT, F_OUT:** the Keystone 3557-2 footprint (LCSC C352820). No Flux library part was found by web search; the EasyEDA/LCSC library has one. The dimensions are in `datasheets/keystone-3557.txt`: four Ø1.6 mm holes, 13.5 mm between the contact pairs along the fuse and 3.4 mm across each pair. Look for a library part, or make the footprint from the datasheet.
- **F_CHG:** the Schurter UMT 250 footprint, or the LCSC alternative in the part table.
- **J_TEMP:** replace the 1×3 jumper placeholder with the 3-way screw terminal from the part table (Phoenix MKDS 1,5/3, 1715035); pin 1 `GND`, pin 2 `TEMP_DQ`, pin 3 `3V3`.
- **J_CAR, J_SLA:** the placed XY301V-A-5.0-2P has the same 5.0 mm pitch as the Phoenix MKDS 1,5/2 (1715022) chosen in the part table; check the hole size and body outline against Phoenix's drawing, or swap to a Phoenix library part.
- **Q_HOLD (BSS84LT1G):** confirmed wrong on 2026-11-14. The real part is G 1, S 2, D 3 (onsemi datasheet, style 21). Swap its two wires: symbol pin 2 (named D) to `SYS`, symbol pin 3 (named S) to `EN_SRC`. Add a canvas note: "Q_HOLD symbol D/S names swapped; wired by pad number".
- **J_XIAO:** two 1×7 female headers on 2.54 mm pitch. Take the row spacing from Seeed's XIAO dimension drawing; the board is 21 × 17.8 mm.
- **R_CHG:** an axial footprint with 52 mm lead pitch (Vishay AC10, kinked "EK" leads, body 44 × 8 mm **[DS Vishay AC]**), raised off the board.
