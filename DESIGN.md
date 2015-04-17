# Design Guidelines

## General

- Description should end in (FOOTPRINT)
- Seperate power units: orient vertically, pins at +/- 0.4in with 0.15in length
- Pin length, numbering, general naming:

    - ICs: at least 0.15in
    - Discretes: when omitting pin numbers is practical, keep short for maximum wiring flexibility
    - Omitting pin numbers is allowed on discrete devices, but consider leaving the numbers for devices with nonstandard pinouts
    - Name all pins. Hide names when the symbol graphic labels the pin instead (transistor BCE, etc)

- In manufacturer libraries, name parts according to manufacturer naming scheme.
- One part per footprint; specify footprint in Footprint field
- For parts with a large number of variants (e.g. fixed-voltage regulators), a placeholder in the name is acceptable: LM1117DT-v.v
- Prefer logical schematic to blank parts with names - e.g., use buffer symbol in buffers, not just pins named IN and OUT.
- Include [bomtool](https://github.com/cpavlina/bomtool) BOM lines whenever possible.

## Power supply naming

- Do not follow manufacturer naming
- For single rail parts, name main supply V+ (not VCC, VDD)
- For multi-rail parts, name main supply according to use when possible (VCORE, not V1.2)
- Ground is GND, not VSS

## Template parts

- Do not include description
- Do not include footprints

## Very large logic (FPGA, large MCU, etc)

- Use "bracketed" multi-part style

## Small logic (7400, etc)

- Use traditional (non-IEC) symbols for very simple like NAND
- Use IEC or IEC-like symbols for more complex like shift register
- Use separate power units
