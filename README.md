# OWL Hardware

Hardware design files for the OWL measurement tool.

<p align="center">
  <img src="docs/Full%20exploded%203D%20render.png" alt="Exploded 3D render" width="75%">
</p>

The OWL is a rotating platform driven by a BLDC motor under field-oriented control.
Power and USB data are passed from the stationary base to the rotating part through a slip ring,
so devices mounted on top can be rotated continuously while staying connected to a host.

## Assembly

Step-by-step build instructions, from 3D-printed parts to the first power-up checks and flashing the firmware, are in [docs/Assembly instructions.md](docs/Assembly%20instructions.md).

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

Each PCB folder contains the KiCad project, a STEP model, a schematic PDF (where exported), and a `production` folder with Gerbers, BOM, and placement files for JLCPCB.

## Usage

Requirements:

- [KiCad](https://www.kicad.org/) 10 or newer
- [Git LFS](https://git-lfs.com/) for STEP models, PDFs, images, and fabrication archives

```sh
git lfs install
git clone git@github.com:sedlak477/owl-hardware.git
```

Fabrication outputs are generated with the [Fabrication Toolkit](https://github.com/bennymeg/Fabrication-Toolkit) KiCad plugin.

## Related resources

[owl-firmware](https://github.com/sedlak477/owl-firmware): The firmware for the OWL platform.  
[owl-ranger](https://github.com/sedlak477/owl-ranger): A script for stepping through some orientations and recording measurements.  
[pyowl](https://github.com/sedlak477/pyowl): A python library for interacting with the OWL.  
[Dataset](https://doi.org/10.3217/kh254-z8374): Orientation-diverse BLE Channel Sounding and UWB ranging measurements recorded with the OWL.

## License

Copyright 2026 Michael Sedlak.

This hardware is licensed under the CERN Open Hardware Licence Version 2 - Permissive (CERN-OHL-P-2.0), see [LICENSE](LICENSE).
It is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE.
