# PCBs

| Board                         | Folder             | Layers | Size           | Thickness | Copper                    | Solder mask | Parts on    |
| :---------------------------- | :----------------- | :----- | :------------- | :-------- | :------------------------ | :---------- | :---------- |
| Rotor / controller            | `controller/`      | 4      | 60 x 60 mm     | 1.6 mm    | 1 oz outer, 0.5 oz inner  | Purple      | top only    |
| Stator                        | `stator/`          | 2      | 44 x 44 mm     | 1.6 mm    | 1 oz                      | Black       | both sides  |
| Magnetic sensor (MA600A)      | `sensor/ma600a/`   | 2      | 22.3 x 20 mm   | 1.6 mm    | 1 oz                      | Yellow      | both sides  |

ENIG surface finish is recommended.
Minimum track width and clearance are 0.15 mm, minimum drill is 0.25 mm (controller) or 0.3 mm (stator, sensor).

Each board folder contains:

| Path                  | Content                                                                          |
| :-------------------- | :------------------------------------------------------------------------------- |
| `schematic.pdf`       | Schematic.                                                                       |
| `src/`                | KiCad project and STEP model of the assembled board.                             |
| `production/generic/` | Files for any manufacturer (see below).                                          |
| `production/jlcpcb/`  | Files ready to upload to JLCPCB for fabrication and assembly.                    |

The easiest way to get the files is the [latest release](https://github.com/sedlak477/owl-hardware/releases/latest): `owl-<version>-jlcpcb.zip` has the JLCPCB files and `owl-<version>-generic.zip` the generic files and schematics, each with one folder per board.

## Ordering from JLCPCB

> [!WARNING]
> **Check the rotation of every part in JLCPCB's placement preview before you order.**
> JLCPCB's part models don't always line up with the footprints, so some parts can show up rotated (often by 90° or 180°) or shifted.
> JLCPCB assembles the board as the preview shows it: a wrongly rotated IC, LED or connector is soldered on the wrong way round, and the board has to be reworked or thrown away.
> See step 5 below.

Order each board (`controller`, `stator`, `sensor-ma600a`) separately. Download and unzip `owl-<version>-jlcpcb.zip`, then for each board:

1. Go to [jlcpcb.com](https://jlcpcb.com), click *Order now*, and upload `<board>/<board>-gerbers.zip`. Don't unzip it, JLCPCB wants the zip.
2. Check that layers, size and thickness match the table above, and pick the solder mask color you like.
3. Enable *PCB Assembly*. The controller is assembled on the top side only; the stator and the sensor have parts on both sides, so select assembly on both sides for them.
4. Upload `<board>/<board>-bom.csv` as the BOM and `<board>/<board>-positions.csv` as the CPL (pick-and-place) file.
5. Check the part matching, then go through **every part** in the placement preview and check both its position and its rotation:
   - Position: its pins sit on their pads.
   - Rotation of ICs: the pin-1 marker on the part (dot, notch or bevel) sits at the pin-1 marker on the silkscreen.
   - Rotation of LEDs: the cathode sits at the cathode marker on the silkscreen.
   - Rotation of connectors: the part matches its silkscreen outline, with the opening on the correct side.

   Rotate or move any part that is off directly in the preview before ordering. Resistors and ceramic capacitors are not polarized, so for them a 180° rotation does not matter.

On the controller, the optional RM2 radio module (U6) and microSD socket (J8) are marked DNP and are not assembled, and neither are their support parts on the bottom side (C43, C44, R1, R2). Solder them by hand if you need them; their values and part numbers are in the schematic.

## Ordering elsewhere

`owl-<version>-generic.zip` (or `production/generic/` in each board folder) contains manufacturer-neutral files, plus each board's schematic:

| File                      | Content                                                                                       |
| :------------------------ | :-------------------------------------------------------------------------------------------- |
| `<board>-gerbers.zip`     | Gerber X2 layers, Excellon drill files (plated and non-plated separate), and a Gerber job file with the stackup. |
| `<board>-netlist.ipc`     | IPC-D-356 netlist for electrical testing.                                                     |
| `<board>-bom.csv`         | BOM with manufacturer and manufacturer part number (MPN), plus the LCSC number where available. |
| `<board>-positions.csv`   | Pick-and-place file as exported by KiCad (mm, rotation in KiCad convention, both sides).      |

The Gerbers work at any PCB manufacturer.
Assembly houses usually want the BOM and position files in their own format; the columns in the generic files map directly to theirs.
Rotation conventions differ between assembly houses, so **check the rotation of every polarized part in their placement preview**, the same way as for JLCPCB (step 5 above).
The JLCPCB position file is not generic: it contains JLCPCB-specific rotation and offset corrections.

## Regenerating the production files (only after changing the design)

Not needed for ordering boards: the production files in each release are ready to use.

Run `pcb/export-production.sh` (or `pcb/export-production.sh <board>` for one board: `controller`, `stator`, `sensor-ma600a`).
It needs `kicad-cli` (KiCad 10) and, for the JLCPCB files, the [Fabrication Toolkit](https://github.com/bennymeg/Fabrication-Toolkit) KiCad plugin.
Set `KICAD_PYTHON` to the Python interpreter KiCad uses if it is not the default `python3`, and `FABRICATION_TOOLKIT_DIR` if the plugin is not installed in `~/.local/share/kicad/10.0/3rdparty/plugins`.
