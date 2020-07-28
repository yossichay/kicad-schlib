# Library design manual - schematic

This manual is currently a work in progress.

- [0. Definitions](#0-definitions)
- [1. Component properties](#1-component-properties)
- [2. Fields](#2-fields)
- [3. Pins](#3-pins)

## 0. Definitions

**Block IC:** an integrated circuit symbol drawn as a simple block with named
pins inside. Typical examples are microcontrollers and FPGAs.

## 1. Component properties

**1.1. Component name** should be as close as reasonably possible to a full
part number. For generic parts, use short, simple names like `R` (resistor)
and `NMOS` (N-channel MOSFET).

**1.2. Description** should follow the format specified in [DESCR.md](DESCR.md).

**1.3. Keywords and Documentation File Name** are deprecated and must be
left blank.

**1.4. Aliases** are only for components with multiple similar variants, for
example fixed voltage regulators available in multiple voltages. The main
component should be a generic part covering the entire set, not just an
arbitrary member of the set.

**1.5. Footprint filter list** is only for parts with an unlimited number
of possible footprints, like generic connectors (WIP: the connector library
rewrite has not begun yet, and this is not yet fully standardized). Leave it
*blank* for single-footprint parts, with the single footprint in the Footprint
field.

## 2. Fields

**2.1. Text size** must be 50 mil.

**2.2. Visible fields** include *only* Reference and Value. All others must be
hidden.

**2.3. Hidden fields** must be arranged clearly; do not leave these in the pile
KiCad puts them in.

**2.4. Reference** designators should follow
[REFERENCE\_FIELD.md](REFERENCE_FIELD.md).

**2.5. Footprint** field should be set for all single-footprint parts. For parts
available in multiple footprints (e.g. integrated circuits made in DIP, SOIC,
and QFN), it is strongle encouraged to make multiple symbols, one per footprint,
with the footprint permanently assigned in this field.

**2.6. Datasheet** should contain a URL to a publicly accessible datasheet,
preferably in PDF format.

**2.7. BOM** contains a BOM line or BOM line template, per
[BOM\_FIELD.md](BOM_FIELD.md). For ICs, a quick summary is that this should
contain the contents of the Manuf and MPN fields separated by a space.

**2.8. Manuf** contains the manufacturer's name. This can be abbreviated.
Use the actual manufacturer; for example, Atmel was acquired by Microchip, so
Atmel parts get "Microchip" here.

**2.9. MPN** contains the manufacturer's part number. This should be as close
to an actual ordering code as possible, though omitting a packaging suffix
(reel/tray/etc) is acceptable. Placeholders for options should be formatted
as `{name}` where *name* is a short descriptor (vout for regulators, etc).

## 3. Pins

**3.1. Hidden Power Input pins**, except on actual power symbols, are strictly
forbidden and will be dealt with by tarring and feathering.

**3.2. Grid:** pins *must* be aligned to the 50 mil grid; pins on ICs *should*
be aligned to the 100 mil grid.

**3.3. Pin length:** IC pins must be at least 150 mil long, preferred
200mil. Pins on other components (discrete semiconductors, passives, etc) can
have any reasonable length; shorter is preferred.

**3.4. Pin text size:** Pins must have 50 mil text size, with the exception
that 0 mil size can be used to hide pin names when illustrating the pin function
graphically instead.

**3.5. Pin numbering:** Omit pin numbers for passives, discrete semiconductors,
etc., unless the part has more than three pins. Integrated circuits must always
have numbered pins.

**3.6. Pin naming:** All pins must be named, even when that name is hidden due
to graphical illustration of the pin function. Use the pin names used in
the part's datasheet, with the following exceptions:

*3.6.1. Power supply pins* for analog components supplied by only a single
rail and ground should be called `V+` and `GND`; for analog components supplied
by a single bipolar rail, use `V+` and `V-`.

*3.6.2. Active-low signals* should be indicated with an overbar (tilde `~`
prefix in KiCad) rather than any of the other conventions. In particular,
active-low signals *should be indicated*, period. Some datasheets do not
indicate logic polarity in the pin names.

*3.6.3. Anodes and cathodes* should be called `A` and `K`, respectively.

*3.6.4. Analog inputs and outputs* on simple amplifiers like opamps should
be called `IN` and `OUT`, with `+` and `-` suffixes for differential inputs
and outputs. For example, the three pins of an opamp are `IN+`, `IN-`, and
`OUT`.

**3.7. Pin types** should be assigned as follows:

| Pin type | Purpose |
| -------- | ------- |
| Input             | Must be driven by a signal |
| Output            | *Always* emits a signal |
| Bidirectional     | May operate as an input or an output; e.g. microcontroller and FPGA IOs |
| Tristate          | *Will* operate as both an input and an output; e.g. memory IC data pins, SPI slave outputs |
| Passive           | Pins on passive components and discrete semiconductors, or any other pin with a function not easily mapping to the input/output model |
| Open collector    | Open collector or open drain; can pull a signal in only one direction. NOT for collectors and drains of discrete semis. |
| Power input       | Must be supplied with power. Do NOT make these hidden, as hidden power input pins have side effects in KiCad. |
| Power output      | Can supply power to Power Input pins. NOT for "power sources" that cannot be used directly, like outputs of switching DC-DC converter ICs. |
| No connection     | Only for pins that *must not* be connected. For pins that are not connected internally but may be grounded, use Passive. For pins that are not connected internally but are strongly recommended to be grounded, use Power Input. |

The following pin types are not to be used: unspecified, open emitter.

**3.8. Pin style:** for all pins with visible names, the "line" pin style should
be used. When names are hidden, other pin styles may be used to illustrate pin
functions. **NEVER** use both "inverted" pin style and an overbar on an
active-low signal; this is double-inversion and leads to ambiguity.

**3.9. Pin orientation:** Avoid vertically oriented pins in *block ICs*.

**3.10. Pin arrangement** should be logical rather than phyical, in all cases.
These are schematic symbols, not footprints.
