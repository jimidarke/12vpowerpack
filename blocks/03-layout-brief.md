# Layout brief (v3.1, draft 2026-11-14)

The brief for board creation and placement in Flux. Send nothing from here until the v3.1 schematic edits (`blocks/02-v31-schematic-edits.md`) are in and checked, and the footprints in its part C are settled.

Order of work. Each step is its own agent message, or hand work, and is verified with the free reads before the next:
1. Board outline, stackup and mounting holes: owner, by hand (free).
2. Placement: agent message 1 below, or by hand. Verify with `get_layout` and the layout image.
3. Routing: a separate message, written after placement is accepted.
4. DRC, then the manufacturing export (Gerbers, BOM with LCSC numbers, CPL for JLCPCB): a separate message.

## Board

- Outline at most 100 × 100 mm, the cheapest JLCPCB price tier. Rectangular, with 1 mm corner radius.
- 2 layers, 1.6 mm FR-4, 1 oz copper, lead-free HASL. All SMT on the top side (economic PCBA is single-sided).
- 4 × M3 mounting holes (3.2 mm) about 4 mm in from each corner, with a 6.5 mm copper keep-out, for bosses in the 3D-printed case.
- Bottom layer: a solid `GND` pour, broken only where unavoidable.

### Copper for the power path **[calc]**

IPC-2221 external-layer formula, I = 0.048 · ΔT^0.44 · A^0.725 (A in mil²), at 1 oz (1.378 mil thick):

| Current | Rise 10 °C | Rise 20 °C |
|---|---|---|
| 7 A (car-feed peak) | 4.4 mm | 2.9 mm |
| 5 A | 2.8 mm | 1.8 mm |
| 2 A (charge path, allowing for F_CHG's slow blow) | 0.8 mm | 0.5 mm |

So 1 oz copper is enough if the power nets are pours or traces of at least 4.5 mm. 2 oz copper is not needed. Where a power net changes layer, use at least 8 vias of 0.3 mm drill. The `GND` return carries the same current as the feed, so it needs the same width.

Power nets, highest current first: `J_CAR_P`, `VIN_CAR`, `SYS_IN`, `SYS`, `LOAD`, `12V_SW`, `12V_OUT`, `VBAT`, `J_SLA_P`, `GND`. `CHG_F` carries about 1.2 A normally and up to about 3 A in a battery fault, until F_CHG blows.

## Placement zones

The power flows one way across the board: car in → input ideal diode → input shunt → `SYS` → output shunt → `LOAD` → loads. The battery corner sits beside `SYS`.

```
 ┌────────────────────────── board edge A (wiring: car, battery, probe) ─────────────────────┐
 │ J_CAR  F_IN   D_TVS U_OR1/Q_OR1 → R_SNS_IN → SYS ← U_OR2/Q_OR2   F_BAT  J_SLA   J_TEMP      │
 │                     C_VIN C_OR1   U_MON_IN    C_SYS1/2 C_OR2  F_CHG                         │
 │                                  R_SNS_OUT / U_MON_OUT                                      │
 │  module 8 (enable, hold)          LOAD                           R_CHG (raised, along edge) │
 │  module 6 (XIAO + sense)    U_5V buck (tight loop)   Q_OUT + module 7                       │
 │  XIAO antenna → off edge            L1, C_O1–4        F_OUT                                 │
 └──────────── board edge B (user-facing outputs: J_12V, J_USBA, LEDs) ───────────────────────┘
```

This is a sketch of neighbours, not a drawing to scale. The rules behind it:

- **Connectors:** the screw terminals J_CAR, J_SLA and J_TEMP on one edge, with their wire entries facing out. J_12V and J_USBA on the opposite edge (or the same edge, if the case wants one cable side). The LEDs D_GRN and D_RED near an edge, under a light pipe or hole.
- **Fuses:** F_IN next to J_CAR, F_BAT next to J_SLA, F_OUT next to J_12V. All three are Keystone 3557-2 holders (19.8 × 6.8 mm, 7.4 mm tall), reachable through a lid opening. F_CHG between `SYS` and R_CHG.
- **R_CHG:** Vishay AC10, body 44 × 8 mm, lead pitch 52 mm **[DS Vishay AC]**. Raised 3–5 mm off the board along an edge. Keep at least 10 mm from J_XIAO, the INA226s, the ceramic capacitor banks and the plastic case wall; it can run at 3.5–4.6 W normally and more in a battery fault. Vent the case over it.
- **Ideal diodes:** U_OR1 next to Q_OR1 and U_OR2 next to Q_OR2, with VCAP caps (C_OR1, C_OR2) at the VCAP pins and short gate traces. Give each CSD18543Q3A's drain tab a copper pour (0.3–0.4 W each **[calc]**).
- **Shunts:** each INA226 within about 10 mm of its shunt. Take IN+/IN− as a pair from the inner edges of the shunt pads (Kelvin), away from the power copper. C_MON1/C_MON2 at VS.
- **5 V buck (U_5V):** C_IN5 and C_HF5 right at VIN and PGND; a small `SW_5V` node; L1 next to SW; C_O1–C_O4 at L1's output; R_FBT/R_FBB at FB, with the `FB_5V` trace kept away from `SW_5V` and L1. Thermal pad to the `GND` pour with a via array.
- **Q_OUT (TO-252):** drain tab pour on `12V_SW`; the gate network (R_OG1, C_OG, D_ZO, R_OG2, Q_OUTDRV) next to it.
- **J_XIAO:** the socket at a board edge, with the ESP32-C6's ceramic antenna end at or over the edge and no copper (any layer) under the antenna. The XIAO's USB-C stays reachable, or the module comes out of its socket to flash; after the first flash, ESPHome updates are over the air.
- **Sense dividers** (R_VC1/R_VC2/C_VC, R_VB1/R_VB2/C_VB), the pull-ups and module 8 near J_XIAO, away from `SW_5V`.
- **Test points** TP1–TP8 (`VIN_CAR`, `SYS`, `LOAD`, `VBAT`, `5V`, `3V3`, `EN_5V`, `GND`) where a probe reaches them with the board in the case base. They are not yet in the schematic; add them in the v3.1 edits or as bare pads at layout.

## Agent message 1: placement only (draft, not sent)

> Placement only. Do not route, add copper pours, change the outline, or edit the schematic.
>
> Place every component inside the existing board outline, following the attached placement brief: the zones, the edges for the connectors, the keep-outs (mounting holes and the XIAO antenna) and the neighbour rules. All SMT parts go on the top layer.
>
> No research, no review, no DRC fixing. If a part cannot be placed, leave it off the board and list it.
>
> Reply in three lines: parts placed, parts not placed (with the reason), anything in the brief you could not follow.

Attachment: this file's "Board" and "Placement zones" sections.

Verify with `get_layout` (every part inside the outline, connectors on their edges, the XIAO at the edge, R_CHG along an edge) and the layout image, then refine by hand.
