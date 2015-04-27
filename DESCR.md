# Templates for part descriptions

## FPGA, CPLD, etc

`FPGA nLEs nIOs _RAM_ [footprint]`

`CPLD nLEs nIOs [footprint]`

- nLEs: Number of logic elements. `LEs:4608`
- nIOs: Number of IO pins. `IOs:142`
- RAM: Amount of RAM in metric kbits. `RAM:120kb`

These chips can differ significantly from each other, so just use common sense.

## A/D converters

`ADC.n nbit sps interface _inl_ _dnl_ _refppm_ [footprint]`

- sps: Samples per second. `50kSa/s` Alternatively: settling time. `15µs`
- interface: data interface (SPI, I2C, parallel, etc)
- inl: Integral nonlinearity, LSB. `INL:2`
- dnl: Differential nonlinearity, LSB. `DNL:3`
- refppm: PPM/K of integrated reference, if present. `Ref:2ppm/K`

## D/A converters

`DAC.n nbit sps interface _inl_ _dnl_ _refppm_ [footprint]`

- sps: Samples per second. `50kSa/s` Alternatively: settling time. `15µs`
- interface: data interface (SPI, I2C, parallel, etc)
- inl: Integral nonlinearity, LSB. `INL:2`
- dnl: Differential nonlinearity, LSB. `DNL:3`
- refppm: PPM/K of integrated reference, if present. `Ref:2ppm/K`

## Linear regulators, LDOs, DC-DC

`Reg Lin voltage current [footprint]`

`Reg LDO voltage current [footprint]`

`Reg Buck in:vin vout current freq [footprint]`

`Reg Boost in:vin vout current freq [footprint]`

- voltage: output voltage or AdjV
- current: maximum output current or AdjI

The cutoff for linear vs. LDO is suggested to be a typical dropout of 1.2V at full load.
This places the worst IC commonly considered "LDO" (LM1117) just inside the LDO category.

## Voltage references

`VRef Series/Shunt voltage tolerance ppm/K [footprint]`

## Logarithmic amplifiers, detectors

`LogAmp dynamic_range bandwidth [footprint]`

`LogDetect dynamic_range bandwidth [footprint]`

The distiction is that detectors typically have an integrated low-pass filter, so
high RF comes out as a DC power level.

## Comparators

`Comp.n _delay_ _irange_ _outtech_ _extras_ [footprint]`

- .n: number of units. omit if one.
- delay: propagation delay, ns.
- irange: RRI, SSI, OverTopI
- outtech: OpenDrain, OpenColl, TTL, CMOS, LVDS, etc.
- extras: ProgHysteresis, etc.

## Operational amplifiers, instrumentation amplifiers

`OpAmp.n _intype_ GBW _slewrate_ _iorange_ _tech_ _extras_ [footprint]`

`InAmp.n _intype_ GBW _slewrate_ _iorange_ _tech_ _extras_ [footprint]`

- .n: number of units. omit if one.
- intype:
  - VFB for voltage feedback, but omit for GBW < 75 MHz
  - CFA for current feedback
- slewrate:
  - Only specify if notable (suggested cutoff: 6V * GBW)
  - Always specified in V/µs
- iorange:
  - RRI, RRO, RRIO if rail-to-rail (go by manufacturer's claims)
  - SSI, SSO, SSIO if single-supply
  - OverTopI if over-the-top
  - OpenCollO, OpenDrnO if open-collector/open-drain
- tech: input circuit technology. CMOS, JFET, etc. Omit for BJT or if unspecified.
- extras:
  - LowVos: low V offset (suggested: < 1mV)
  - VLowVos: very low V offset (suggested: < 50µV)
  - LowIB: low input bias current (suggested: < 1µA)
  - VLowIB: very low input bias current (suggested: < 1 nA)
  - LowNoise: low noise (cutoff depends on applications!)
  - Chopper: chopper-stabilized

## Discrete transistors

`PMOS.n _semi_ -xV -xA _Rdson_ _Vgsth_ [footprint]`

`NMOS.n _semi_ xV xA _Rdson_ _Vgsth_ [footprint]`

`PNP.n _semi_ -xV -xA _Pd_ _ft_ [footprint]`

`NPN.n _semi_ xV xA _Pd_ _ft_ [footprint]`

- semi: specify semiconductor material for exotic devices
- Use negative voltage, current for P-type devices
- Rdson: on-resistance of MOSFET. `34mR`
- Vgsth: threshold of MOSFET. Typically at a low current like 250µA. Negative for P-type. `-3Vth`

## Discrete diodes

`DIODE xV xA [footprint]`

`SCHOTTKY xV xA [footprint]`

`ZENER xV xW Iz:xA [footprint]`

`TVS xV _pulse_ _Cj_ [footprint]`

- pulse: 8/20µs peak pulse

## Microcontrollers

`MCU nbit/arch ROM:nKB RAM:nKB _extras_ [footprint]`

- arch: for ARM, use such as ARM-M4
- extras: list features not including the usuals like SPI/I2C/UART.

## Passives

`IND nH nR _SRF:100MHz_ _(dimensions)_ _[footprint]_`

## Digital interface converters

`Interface FROM TO [footprint]`

## Digital attenuators

`Atten ndB nbit BW _tech_ [footprint]`

- tech: device/semiconductor technology, if appropriate

## Analog switch

`AnSwitch nPnT _tech_ _extras_ [footprint]`
