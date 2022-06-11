# ME 405 Pen Plotter

Ryan Ghosh and Ryan Flaherty (mecha18)

ME 405-03

![Pen Plotter](Images/plotter.jpg?raw=true)

## Introduction

For our ME 405 term project, we designed, built, and programmed a polar pen plotter.

(incomplete)

The following videos show the plotter in action:
- [Drawing a pentagon, hexagon, and line](https://photos.app.goo.gl/KpNNWDwEAwex2bkJ8)
- [Drawing a spiral](https://photos.app.goo.gl/GEohXohUGA1frtkg9)

## Python Code

[Documentation](https://rsghosh.github.io/ME_405_Plotter/)

[Source code](https://github.com/rsghosh/ME_405_Plotter/tree/master/Python_Code)

## CAD Files

SolidWorks files for the pen plotter can be found [here.](https://github.com/rsghosh/ME_405_Plotter/tree/master/CAD)

## STL and DXF Files

All custom parts for the plotter are either 3D-printed or laser-cut.

### 3D-Printed Files

All stl files can be found in the [STLs folder.](https://github.com/rsghosh/ME_405_Plotter/tree/master/STLs)

In each filename, `_x#` indicates the quantity required, and `_rev#` indicates the revision number.

### Laser-Cut Files

The base for the plotter should be laser-cut from 3mm or 0.125" thick material. The dxf file can be found in the [DXFs folder.](https://github.com/rsghosh/ME_405_Plotter/tree/master/DXFs)

## Bill of Materials

The following table contains all the parts you need for the pen plotter that are not either 3D-printed or laser-cut:

| Item #    | Description   | Quantity       | Source        |
| ---       | ---           | ---           | ---           |
| (incomplete)

## Wiring

### Stepper Driver Board #1
| Signal    | Nucleo Pin        | Color |
| ---       | ---               | ---   |
| EN1       | C2                | red   |
| EN2       | C3                | green |
| GND       | GND               | black |
| 3V3       | 3V3               | gray  |
| CLK       | PB6               | brown |
| CS1       | PB8               | yellow|
| CS2       | PB9               | orange|
| SCK       | PB13 (SPI2_SCLK)  | blue  |
| MOSI      | PB15 (SPI2_MOSI)  | white |
| MISO      | PB14 (SPI2_MISO)  | purple|

### Stepper Driver Board #2
| Signal    | Nucleo Pin        | Color |
| ---       | ---               | ---   |
| EN1       | C6                | blue  |
| GND       | GND               | green |
| 3V3       | 3V3               | yellow|
| CLK       | PB6               | brown |
| CS1       | C7                | orange|
| CS2       | 3V3               | white |
| SCK       | PB13 (SPI2_SCLK)  | blue  |
| MOSI      | PB15 (SPI2_MOSI)  | white |
| MISO      | PB14 (SPI2_MISO)  | purple|

### Limit Switch Wiring

The wires should be soldered to the outermost legs on the limit switches so that they are normally closed.

| Endstop       | Stepper Board #   | Pin   |
| ---           | ---               | ---   |
| theta         | 1                 | REFL1 |
| radius        | 1                 | REFL2 |
| pen up/down   | 2                 | REFL1 |

### Stepper Driver Board Jumpers

To set the TMC2208 drivers to use 8 microsteps, jumpers should be placed on the JP6 and JP7 headers to short MS1 and MS2 to GND.

### Setting VREF

To calculate the VREF values to set on the TMC2208 drivers, the desired RMS current should be multiplied by 1.41 ohm.

The following table shows the VREF values we used:

| Motor         | Target RMS Current (A)    | VREF (V)  |
| ---           | ---                       | ---       |
| theta         | 1.13                      | 1.59      |
| radius        | 1.13                      | 1.59      |
| pen up/down   | 0.35                      | 0.49      |

### Wiring Example

![Wiring Example](Images/wiring.jpg?raw=true)

## Task Diagram

(incomplete)

## Kinematics

(incomplete)
