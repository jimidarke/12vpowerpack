# Power board — requirements (v3)

Replaces v2 (two-chemistry power manager with charger IC, USB-C PD input, regulated 12 V and display). v3 is a vehicle-only unit and keeps only what the in-car use needs.

## Product
A small in-vehicle UPS: a 12 V sealed AGM battery floated on the car's own charging voltage, a pass-through 12 V output, a 5 V USB-A output, and a socketed ESP32 that times the shutdown and reports status. First use is the carNet in-car UPS (trunk, under an interior flap).

One build. No lithium variant, no charger IC, no USB-C PD input, no 12 V converter, no display.

## Input
- **Car feed only:** ignition-switched 12 V socket or fuse tap, 11–14.8 V, automotive transients, reverse polarity possible.
- The board never feeds the battery back into the car.
- Not for mains adapters: there is no charge regulation, so the input must be a vehicle charging system (about 13.5–14.8 V when running).

## Battery and charging
- 12 V sealed AGM, 2–12 Ah, on a fused connector.
- Charged from the car feed through a current-limiting resistor; charge voltage is whatever the alternator supplies.
- Accepted limits of this method: the battery is undercharged in deep cold (no temperature-compensated voltage), and recharge is slow (about 1 A at most, tapering). It is sized for the carNet duty of about 2.5 Wh per stop, not for heavy battery-only use.

## Outputs
- **12 V unregulated**, straight from the car feed or the battery: about 10.9–14.8 V. 3 A continuous, 5 A peak for several seconds, barrel jack (5.5 mm). Loads must tolerate that range.
- **5 V regulated**, 2 A minimum on USB-A with charging-port signature. Also powers the ESP32.

## Power control
- Ignition on: both outputs on.
- Ignition off: outputs stay on from the battery for a hold-up time, then everything switches off, including the ESP32, until the ignition returns. The hold-up time is a firmware setting, adjustable from Home Assistant without reflashing and kept across power cycles (default 30 min). The shortest time is 1 min. A setting of 0 means no timeout: the outputs stay on until the hardware low-voltage cutoff.
- **Low-voltage cutoff in hardware:** both outputs switch off when the battery falls to about 11.0 V and stay off until the ignition returns.
- With no ESP32 fitted, a jumper selects the behaviour: outputs on only with the ignition (default), or on until the low-voltage cutoff.
- Standby drain with everything off must be small against the battery's self-discharge.

## Monitoring
- Socketed Seeed XIAO ESP32-C6 running ESPHome; Wi-Fi/MQTT to Home Assistant as carNet does, or BLE.
- Reads car-feed voltage (ignition), battery voltage and battery temperature (probe on the battery). Can switch the 12 V output off.
- Two current monitors (INA226, no more): power in from the car feed, and power out to the loads (12 V output plus the 5 V rail). Battery current is the difference.
- No display.

## Safety
- **Safety never depends on the ESP32.** Fuses, the charge limit, reverse-polarity and backfeed blocking, and the low-voltage cutoff are all hardware. An ESP32 that is missing, crashed or mid-update can at worst leave the outputs on until the hardware cutoff, or off.

## Environment
- −40 °C winters (cold-soaked start, warms slowly while driving), trunk summer heat. Parts rated −40 to 85 °C or better.

## Build
- Batch of ~12. Fab assembly where it is economical; hot-air rework at home is acceptable.
- Target ≤ C$110 per board excluding battery and enclosure. Price checkpoint after schematic capture.

## Sizing figures
- 12 V output: 3 A continuous, 5 A peak.
- 5 V rail: 2 A × 5 V = 10 W out; at 90 % efficiency about 1.0 A from an 11 V supply.
- Car feed, ignition on: up to 3 A + 1 A + 1 A charging ≈ 5 A continuous, about 7 A at the output peak.
- Battery, ignition off: up to 4 A continuous, 6 A peak.
- carNet load ≈ 5 W for 30 min ≈ 2.5 Wh ≈ 0.2 Ah per stop.
