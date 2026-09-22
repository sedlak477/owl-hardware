# OWL Hardware

Hardware design files for the OWL measurement tool.

<p align="center">
  <img src="docs/Full%20exploded%203D%20render.png" alt="Exploded 3D render" width="75%">
</p>

The OWL is a rotating platform driven by a BLDC motor under field-oriented control.
Power and USB data are passed from the stationary base to the rotating part through a slip ring,
so devices mounted on top can be rotated continuously while staying connected to a host.

## Building an OWL

1. Download the files from the [latest release](https://github.com/sedlak477/owl-hardware/releases/latest):
   - `owl-<version>-jlcpcb.zip`: everything needed to order the three assembled PCBs from JLCPCB
   - `owl-<version>-3d-print.zip`: the 3D-printed parts
   - `owl-<version>-generic.zip`: manufacturer-neutral PCB files and schematics, if you order elsewhere
2. Order the PCBs, see [pcb/README.md](pcb/README.md).
3. Print the parts, see [cad/README.md](cad/README.md).
4. Assemble the OWL and flash the firmware, see the [assembly instructions](docs/Assembly%20instructions.md).

## Architecture

![Hardware architecture](docs/OWL%20HW%20arch.drawio.png)

- **Stator PCB**: Sits in the stationary base. Provides the USB-C power input with a USB PD trigger (CH224K) and the USB data port to the host.
- **Rotor PCB** (controller): Rotates with the platform. Contains the RP2354B controller, the DRV8311 BLDC driver, 5 V and 3.3 V regulators, a USB hub with a passthrough port, and an I²C/UART port.
- **Magnetic sensor PCB**: Measures the rotor angle for motor control using a magnetic angle sensor.

## Repository structure

| Path             | Content                                         |
| :--------------- | :---------------------------------------------- |
| `pcb/controller` | KiCad project for the rotor/controller PCB.     |
| `pcb/stator`     | KiCad project for the stator PCB.               |
| `pcb/sensor`     | KiCad projects for the magnetic sensor PCBs.    |
| `cad`            | Link to the Onshape document and 3D-print files.|
| `docs`           | Assembly instructions, renders, and diagrams.   |

Each PCB folder contains a `schematic.pdf`, the KiCad project in `src`, and production files in `production` (generic, and ready to upload to JLCPCB). See [pcb/README.md](pcb/README.md) for the stackups and how to order the boards.

## Editing the design

Requirements:

- [KiCad](https://www.kicad.org/) 10 or newer
- [Git LFS](https://git-lfs.com/) for STEP models, PDFs, images, and fabrication archives

```sh
git lfs install
git clone git@github.com:sedlak477/owl-hardware.git
```

After changing a board, regenerate its production files with `pcb/export-production.sh` (see [pcb/README.md](pcb/README.md#regenerating-the-production-files)).
Pushing a tag starting with `v` (e.g. `v1.1.0`) creates a release with the packaged production and 3D-print files.

## Related resources

[owl-firmware](https://github.com/sedlak477/owl-firmware): The firmware for the OWL platform.  
[owl-ranger](https://github.com/sedlak477/owl-ranger): A script for stepping through some orientations and recording measurements.  
[pyowl](https://github.com/sedlak477/pyowl): A python library for interacting with the OWL.  
[Dataset](https://doi.org/10.3217/kh254-z8374): Orientation-diverse BLE Channel Sounding and UWB ranging measurements recorded with the OWL.

## License

Copyright 2026 Michael Sedlak.

This hardware is licensed under the CERN Open Hardware Licence Version 2 - Permissive (CERN-OHL-P-2.0), see [LICENSE](LICENSE).
It is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE.
