# Reference field

The reference field of a component contains its reference designator.
The following designators are recommended. Note the general big-endian
format: less specific letters (D for diode) come before more specific
(Z for zener).

| Designator | Component type |
| ---------- | -------------- |
| A     | Removable assemblies, daughterboards, modules, ... |
| AE    | Aerials, antennas |
| AT    | Attenuators |
| BT    | Batteries |
| C     | Capacitors |
| CN    | Capacitor networks or arrays |
| CV    | Capacitors, variable |
| D     | Diodes |
| DL    | Delay lines |
| DS    | Displays, display elements, LEDs, indicators, ... |
| DZ    | Diodes, Zener or avalanche |
| E     | Ferrite beads, other lossy RF filters |
| F     | Fuses, excluding PTC current limiting devices (see RT) |
| FAN   | Fans |
| FID   | Fiducials, assembly positioning marks |
| FL    | Filters, excluding attenuators (AT), including PCB elements |
| G     | Graphical elements with matching PCB items (logos, etc) |
| HY    | Circulators, directional couplers |
| J     | Jacks: least movable part of a connector pair. Can be used as a prefix (JU = IC socket). |
| JP    | Jumpers |
| K     | Relays, not including solid-state relays (see U, Q) |
| L     | Inductors, coils, tapped coils, ... |
| LCD   | LCDs |
| M     | Motors, excluding fans (see FAN) |
| MIC   | Microphones |
| MP    | Mechanical parts, screws, heatsinks, ... |
| P     | Plugs: most movable part of a connector pair |
| Q     | Transistors, thyristors, miscellaneous discrete semiconductors |
| R     | Resistors |
| RN    | Resistor networks or arrays |
| RT    | Resistors, thermal, including PTC current limiting devices |
| RV    | Resistors, variable |
| SP    | Speakers, buzzers, including externally and internally driven |
| SW    | Switches, including momentary, excluding switch ICs (see U) |
| SYM   | Graphical symbols with no PCB components |
| T     | Transformers |
| TC    | Thermocouples |
| TP    | Test points |
| TVS   | Transient voltage suppressors, even if also diodes or thyristors |
| U     | Integrated circuits, non-removable assemblies |
| V     | Vacuum tubes, valves |
| W     | Wires, cables, transmission lines, including PCB elements |
| X     | Crystals, resonators, excluding self-contained oscillators |

Note: if you need a designator for something not in this table, feel free to
choose one and submit a pull request on this document adding it. Remember that
we have no problem using multiple letters for these, there's no need to use opaque
single-letter designators that aren't already in widespread use.
