# ME 405 Pen Plotter

Ryan Ghosh and Ryan Flaherty (mecha18)

ME 405-03

![Pen Plotter](Images/plotter.jpg?raw=true)

## Introduction

For our ME 405 term project, we designed, built, and programmed a polar pen plotter.
A Nucleo board on the plotter reads an hpgl file, converts the commands to motor positions, and controls the stepper drivers to make the plotter draw. Meanwhile, a PC receives the commands over UART to draw the same shapes on the screen in sync with the plotter.

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

| Item #    | Description                           | Quantity      | Source        |
| ---       | ---                                   | ---           | ---           |
| 1         | 1515 Extrusion (300mm long)           | 3             | [Amazon](https://www.amazon.com/MakerBeam-XL-Anodized-300x15x15mm-Pieces/dp/B06XJ5G5QY/ref=sr_1_1?crid=18H96ZH5ZU5WV&keywords=makerbeam+300x15x15&qid=1650891296&s=hi&sprefix=makerbeam+300x15x15%2Ctools%2C108)  |
| 2         | MGN12C Rail (240mm long)              | 1             | [RobotDigg](https://www.robotdigg.com/product/766/Quality-440C-SUS-MGN12-linear-rail-with-carriage)   |
| 3         | NEMA17 Stepper Motor                  | 2             | [Printed Solid](https://www.printedsolid.com/collections/motors/products/ldo-nema-17-motor-cooler-ldo-42sth40-1004asr)  |
| 4         | 2GT 20T Toothed Idler (for 9mm belt)  | 1             | [Printed Solid](https://www.printedsolid.com/products/gates-powergrip-2gt-toothed-idler-5mm-id?variant=21236971274325)    |
| 5         | 2GT 20T Pulley (for 9mm belt)         | 2             | [Printed Solid](https://www.printedsolid.com/products/gates-powergrip-2gt-pulley?variant=21236966948949)  |
| 7         | 6201 Bearing                          | 2             | [AliExpress](https://www.aliexpress.com/item/32861605867.html)    |
| 8         | 5x25mm Shaft                          | 1             | [AliExpress](https://www.aliexpress.com/item/2255800484105446.html?gatewayAdapt=4itemAdapt)   |
| 9         | 3x20mm Shaft                          | 3             | [Misumi](https://us.misumi-ec.com/vona2/detail/110300086920/?HissuCode=NSFR3-20)  |
| 10        | 5x7x0.5mm Shim                        | 2             | [AliExpress](http://s.click.aliexpress.com/e/_sq74Gk) |
| 11        | Omron D2F-L Microswitch               | 3             | [Digikey](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/D2F-01L/83264?utm_medium=email&utm_source=oce&utm_campaign=4251_OCE22RT&utm_content=productdetail_US&utm_cid=2812508&so=75510383&mkt_tok=MDI4LVNYSy01MDcAAAGD_5ZwgIAdCIycXtOcbrJFsV5eWFmw2RGe3gRugyXSglp_PmGVFmrT3uu_n9H0YlmRV73A4_wJrtDHxOa4Ql6qXYBUBAEZN5DInWU_B7jr) |
| 12        | M3 Square Nut (DIN 562)               | 36            | [McMaster-Carr](https://www.mcmaster.com/97259A101/)  |
| 13        | M3 x 8mm Socket Head Cap Screw        | 59            | [McMaster-Carr](https://www.mcmaster.com/91290a113)   |
| 14        | M3 x 10mm Socket Head Cap Screw       | 5             | [McMaster-Carr](https://www.mcmaster.com/91290A115/)  |
| 15        | M3 x 12mm Socket Head Cap Screw       | 12            | [McMaster-Carr](https://www.mcmaster.com/91290A117)   |
| 16        | M3 x 20mm Socket Head Cap Screw       | 2             | [McMaster-Carr](https://www.mcmaster.com/91290A123/)  |
| 17        | M3 Heat-Set Insert (M3 x D5.0 x L4.0) | 27            | [AliExpress](http://s.click.aliexpress.com/e/oMUr6YsC)    |
| 18        | M3 Washer (narrow)                    | 8             | [McMaster-Carr](https://www.mcmaster.com/91166A210/)  |
| 19        | M3 Washer (large)                     | 4             | [McMaster-Carr](https://www.mcmaster.com/91100A120/)  |
| 20        | 36mm Round NEMA14 Stepper             | 1             | [Printed Solid](https://www.printedsolid.com/products/ldo-nema14-36mm-round-pancake-motor-ldo-36sth17-1004ah)
| 21        | M5 x 45mm Socket Head Cap Screw       | 1             | [McMaster-Carr](https://www.mcmaster.com/91290A260/)  |
| 22        | M2 x 12mm Pan Head Self Tapping Screw | 6             | [AliExpress](http://s.click.aliexpress.com/e/ojcLGreY)    |
| 23        | M5 Locknut                            | 1             | [McMaster-Carr](https://www.mcmaster.com/90576A104/)  |
| 24        | Unthreaded Bumper                     | 4             | [McMaster-Carr](https://www.mcmaster.com/9540K921/)   |
| 25        | Nucleo-L476RG                         | 1             | [Digikey](https://www.digikey.com/en/products/detail/stmicroelectronics/NUCLEO-L476RG/5347711)    |
| 26        | TMC2208 Stepstick                     | 3             | [Amazon](https://www.amazon.com/Printer-TMC2208-Screwdriver-Controller-Ramps1-4/dp/B082LSQWZF)    |
| 27        | Stepper Driver Board                  | 2             |               |

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

Since our pen plotter uses one motor for controlling the angle of the arm and another to control the radius, we had to use inverse kinematics to determine the motor angles needed to get the pen to the target x and y coordinates. We used the Newtom-Raphson algorithm to find the required motor angles to reach the target position. The following images show the steps we took to find the matrices and equations we would use in the algorithm:

1. Simplified schematic of the robot with links and pivots
2. Forward kinematics: determine `x = f(theta)`, where theta is the motor angles and x is the pen position
3. Find the Jacobian matrix for the system
4. Differentiate `x = f(theta)` with respect to time to find velocity
5. Find g(theta), where `g(theta) = x - f(theta)` and x is a constant target position. Then differentiate g with respect to theta.

We then used these equations in the NewtonRaphson function in [tasks.py](https://github.com/rsghosh/ME_405_Plotter/blob/master/Python_Code/tasks.py) to convert pen positions read from the hpgl file into motor angles.

![Kinematics steps 1-2](Images/ME_405_HW2_hand_calcs_1.jpg?raw=true)

![Kinematics steps 3-5](Images/ME_405_HW2_hand_calcs_2.jpg?raw=true)