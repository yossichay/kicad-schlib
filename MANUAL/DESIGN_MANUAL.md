# Library design manual - schematic

This manual is currently a work in progress.

## Fields

All fields should have a text size of 50 mil. Note that this is different
from the KiCad default. The following fields must be present:

**Reference.** See [REFERENCE\_FIELD.md](REFERENCE_FIELD.md).

**Value.** The value field contains the name of the component itself (as KiCad
requires).  For specific parts, this should be as close as reasonably possible
to a full part number. Lowercase letters can be used as placeholders when one
symbol represents multiple similar part numbers. For generic parts, use short,
simple names like `R` (resistor), `NMOS` (N-channel MOSFET), etc.

**Footprint.** KiCad allows a default footprint to be specified in the
footprint field, rather than requiring the user to select one later. *Do this*
for any parts where it is sensible. For parts available in multiple footprints
(integrated circuits made in DIP, SOIC, and QFN, etc), it is strongly
encouraged to make multiple symbols, one per footprint, with the footprint
permanently assigned in this field.

**Datasheet.** For specific parts, the datasheet field should contain a URL to
a publicly accessible datasheet, preferably in PDF format.

**BOM.** See [BOM\_FIELD.md](BOM_FIELD.md). For ICs, a quick summary is that
this should contain the manufacturer and the part number separated by a
space.

**Manuf.** Manufacturer's name. This can be abbreviated. Use the actual
manufacturer - for example, Atmel was acquired by Microchip, so Atmel parts get
"Microchip" here.

**MPN.** Manufacturer's part number. This should be as close to an actual
ordering code as possible, though omitting a packaging suffix (reel/tray/etc)
is acceptable. Placeholders for options should be formatted as `{name}` where
*name* is a short descriptor (vout for regulators, etc).
