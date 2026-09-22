1. 3D-print all parts & cleanup from print (especially the payload connector mounting holes). The CAD files are in [`cad/`](../cad/README.md). Print the lower parts, especially the motor adapter and everything else touching the motor, in a heat-resistant filament like ABS; the motor gets warm. For the remaining parts the material does not matter.
2. Prepare materials
	1. 1x BLDC motor: SparkFun [ROB-20441](https://www.sparkfun.com/three-phase-brushless-gimbal-stabilizer-motor.html) (Mouser 474-ROB-20441)
	2. 1x slip ring, 6 wire, 2A: SparkFun [ROB-13064](https://www.sparkfun.com/slip-ring-6-wire-2a.html) (Mouser 474-ROB-13064)
	3. 1x stator PCB, 1x controller PCB, 1x sensor PCB
	4. 3x M5 nuts
	5. 3x M5 counter-sunk screws, 40mm long
	6. 3x M1.6x6 flat-head screws
	7. 3x M1.6x10 flat-head screws
	8. 1x 1/4'' heat insert, 8.7mm outer diameter, ~12.7mm long (a shorter one works too, it just must not be longer)
	9. 1x Molex Pico-EZmate cable assembly, 6 circuits, 50mm: [36920-0600](https://www.molex.com/en-us/products/part-detail/369200600) (Mouser 538-36920-0600)
	10. 2x JST PA 6-pin housing (PAP-06V-S) with 12x crimp contacts, for the slip ring
	11. 2x USB-C cables. Take care with cheap cables: many are charge-only and have no data lines.
	12. 1x USB-C power supply that can deliver the voltage the stator requests (see below)
3. Tools: soldering iron (for the heat insert), crimping tool for JST PA contacts, wire strippers, side cutters, 2mm allen key, multimeter
4. Prepare PCBs (Remove panels)
5. Press 1/4'' heat into stator
	1. Insert until 1mm still sticks out
	2. While still hot, turn around and press against flat surface (CAUTION: Don't press on the center with your finger or you could burn yourself on the heat insert)
	3. This ensures the insert is level with the bottom surface
6. Put the M5 bolts into the motor adapter
7. Mount the motor to the top of the motor adapter
	1. Pre-screw the M1.6x6 screws into the small holes; Leave 1/2mm sticking out of the top to make aligning the motor easier
	2. Ensure the M5 bolts are already insert into the big holes
	3. Align the motor (magnetic ring facing away) with the screws and tighten the screws
	4. Ensure the motor does not wiggle and it rotates freely. If it sounds like it is scraping, then the screws are going in too far and are damaging the motors internals!
8. Thread the cables of the slip ring through the motor and slide it onto the M5 screws. The thin side of the slip ring should disappear into the motor adapter and the flanch should sit flush against the motor adapter.
9. Add one small spacer to each M5 screw, then slide on the stator PCB with the connectors facing *away* from the assembly. Ensure you thread the slip ring cables through the large center hole of the stator PCB and the connectors are aligned with the symbols (the JST connector should be on the side where there's no symbol)
10. Cut the cables to size (leave some slack to allow for some mistakes when crimping), strip the ends, and crimp on the JST crimps.
11. Insert the crimps into the connector housing, remember the order (or better, take a picture). The order does not matter, but it just has to match the order on the other side. I recommend ordering them so the cables can lie pretty coming out of the connector. (Picture for color order)
12. Insert the connector
13. Slide two big spacers onto each M5 screw, carefully bend the cables to the side, and slide on the tripod adapter.
14. Screw the M5 nuts onto the ends of the M5 screws. Depending on 3D printing tolerences, an allen key should just fit beside the motor to turn the screw. After a few rotations, the nut will be held in place by the tripod adapter and you can tighten it all the way.
15. The stator assembly is now finished!
16. Thread the slip ring and motor cables though the center hole of the controller PCB and place it on top of the motor.
17. Again, cut the wires to length and crimp on the connector (same as steps 10 & 11). Ensure you insert the cables in the same order as on the other end.
18. Before plugging anything in, check the slip ring wiring with a multimeter. Unplug the housing on the stator side and measure continuity between the two housings: pin 1 must reach pin 1, pin 2 must reach pin 2, and so on. If the crimps went in mirrored, the order still "matches" but VM ends up on VBUS. Also check that no two neighbouring pins are shorted by a crimp.
19. Plug in the slip ring connector and the motor connector.
20. !!!!! Make sure the slip ring cables are bent to the side and lay flat against the PCB, so the sensor can later be mounted on top.
21. Plug the Pico-EZmate cable into the sensor PCB. Lay the sensor flat on the table align the connector from the top and just press down, the connector should click into place very easily.
22. Thread the M1.6x10 screws through the payload connector, slide on the sensor PCB (the sensor IC facing *away* from the payload connector), and slide on the board spacers. The fit on the spacers is tight, so I recommend screwing into them and letting 2mm stick out for alignment.
23. Align the controller PCB with the motor's mounting holes, add the payload connector + sensor assembly on top, and screw the three M1.6 screws down into the motor.
24. Plug the other end of the Pico-EZmate cable into the controller PCB.

## Power supply

The stator uses a CH224K USB PD trigger to ask the power supply for the motor voltage.
Which voltage it requests is set by the solder jumpers JP1 (CFG1), JP2 (CFG2) and JP3 (CFG3) on the stator PCB.
As manufactured, the stator requests 9V.
Any USB-C PD supply that offers 9V will do.

You can change the requested voltage with the jumpers.
If you do, also set `SUPPLY_VOLTAGE` in the firmware's [`src/main.cpp`](https://github.com/sedlak477/owl-firmware/blob/main/src/main.cpp) to the new voltage, otherwise SimpleFOC computes the wrong phase voltages.
The firmware limits the motor to 4V (`motor.voltage_limit`); keep it below the motor's 7.4V rating.

## Checks

You are now done with the mechanical assembly! A few checks before continuing:
- Make sure the top rotates freely
- Check the following LEDs
	- Power plugged in, data **unplugged**
		- `VM`: green
		- `5V`: green
		- `3.3V`: green
		- Rest off (`USB`, `USER`, `DRV FAULT`, `PG`)
	- Power **unplugged**, data plugged in
		- `5V`: green
		- `3.3V`: green
		- `USB`: yellow
		- Rest off (`VM`, `USER`, `DRV FAULT`, `PG`)
	- Both plugged in
		- `VM`: green
		- `5V`: green
		- `3.3V`: green
		- `USB`: yellow
		- Rest off  (`USER`, `DRV FAULT`, `PG`)

If those checks passed, you can continue on to flashing the firmware.

## Flashing the firmware

1. Download the latest `.uf2` image from the [owl-firmware releases](https://github.com/sedlak477/owl-firmware/releases) page.
2. Plug in **only** the data cable. On a new board the flash is blank, so the controller starts in BOOT mode by itself. To reflash a board that already has firmware, hold the BOOT button while plugging in the data cable.
3. The OWL will show up as a USB thumb drive.
4. Copy the firmware image to this drive.
5. The controller will flash the firmware and reset.
6. Done!

## What next

For a first controlled move, use [pyowl](https://github.com/sedlak477/pyowl), the Python library for the OWL.
To step through orientations and record measurements, use [owl-ranger](https://github.com/sedlak477/owl-ranger).