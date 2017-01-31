# Library design manual - schematic

This manual is currently a work in progress.

## Fields

All fields should have a text size of 50 mil. Note that this is different
from the KiCad default. The following fields must be present:

<dl>
<dt>Reference</dt>
<dd>This contains the reference designator for the part. The following
    designators are recommended. Note the general big-endian format: less
    specific letters (D for diode) come before more specific (Z for zener).
    <table>
    <tr><th>Designator</th>	<th>Component type</th></tr>
    <tr><td>A</td>			<td>Assembly, daughterboard, module, ...</td></tr>
    <tr><td>AE</td>         <td>Aerial, antenna</td></tr>
    <tr><td>AT</td>         <td>Attenuator</td></tr>
    <tr><td>BT</td>         <td>Battery</td></tr>
    <tr><td>C</td>          <td>Capacitor</td></tr>
    <tr><td>CN</td>         <td>Capacitor network or array</td></tr>
    <tr><td>CV</td>         <td>Capacitor, variable</td></tr>
    <tr><td>D</td>          <td>Diode, or diode array, bridge rectifier, ...</td></tr>
    <tr><td>DL</td>         <td>Delay line</td></tr>
    <tr><td>DS</td>         <td>Display, display element, LED, indicator</td></tr>
    <tr><td>DZ</td>         <td>Diode, Zener or avalanche</td></tr>
    <tr><td>E</td>          <td>Ferrite bead, other lossy RF filter</td></tr>
    <tr><td>F</td>          <td>Fuse, excluding PTC current limiting devices (see RT)</td></tr>
    <tr><td>FAN</td>        <td>Fan</td></tr>
    <tr><td>FID</td>        <td>Fiducial, assembly positioning mark</td></tr>
    <tr><td>FL</td>         <td>Filter, excluding attenuators (AT)</td></tr>
    <tr><td>G</td>          <td>Graphical elements with matching PCB items</td></tr>
    <tr><td>HY</td>         <td>Circulator, directional coupler</td></tr>
    <tr><td>J</td>          <td>Jack: least movable part of a connector pair.
                                Can be used as a prefix (JU = IC socket).</td></tr>
    <tr><td>JP</td>         <td>Jumper</td></tr>
    <tr><td>K</td>          <td>Relay, not including solid-state relays (see U, Q)</td></tr>
    <tr><td>L</td>          <td>Inductor, coil, tapped coil</td></tr>
    <tr><td>LCD</td>        <td>LCD</td></tr>
    <tr><td>M</td>          <td>Motor, not fan (see FAN)</td></tr>
    <tr><td>MIC</td>        <td>Microphone</td></tr>
    <tr><td>MP</td>         <td>Mechanical parts, screws, heatsinks...</td></tr>
    <tr><td>P</td>          <td>Plug: most movable part of a connector pair</td></tr>
    <tr><td>Q</td>          <td>Transistor, thyristor, miscellaneous discrete semiconductors</td></tr>
    <tr><td>R</td>          <td>Resistor</td></tr>
    <tr><td>RN</td>         <td>Resistor network</td></tr>
    <tr><td>RT</td>         <td>Resistor, thermal, including PTC current limiting devices</td></td>
    <tr><td>RV</td>         <td>Resistor, variable</td></tr>
    <tr><td>SP</td>         <td>Speaker, buzzer</td></tr>
    <tr><td>SW</td>         <td>Switch, including momentary, excluding switch ICs (see U)</td></tr>
    <tr><td>SYM</td>        <td>Graphical symbols with no PCB component</td></tr>
    <tr><td>T</td>          <td>Transformer</td></tr>
    <tr><td>TC</td>         <td>Thermocouple</td></tr>
    <tr><td>TP</td>         <td>Test point</td></tr>
    <tr><td>TVS</td>        <td>Transient voltage suppressor, even if also a diode or thyristor</td></tr>
    <tr><td>U</td>          <td>Integrated circuit</td></tr>
    <tr><td>V</td>          <td>Vacuum tube, valve</td></tr>
    <tr><td>VAR</td>        <td>Varistor, MOV</td></tr>
    <tr><td>W</td>          <td>Wire, cable, transmission line, including PCB elements</td></tr>
    <tr><td>X</td>          <td>Crystal, resonator, not excluding self-contained oscillators</td></tr>
    </table>

    Note: if you need a designator for something not in this table, feel free to
    choose one and submit a pull request on this document adding it. Remember that
    we have no problem using multiple letters for these, there's no need to use opaque
    single-letter designators that aren't already in widespread use.</dd>

</dl>
