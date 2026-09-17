# OWL Hardware

Hardware design files for the OWL measurement tool.

<p align="center">
  <img src="docs/Full%20exploded%203D%20render.png" alt="Exploded 3D render" width="75%">
</p>

The OWL is a rotating platform driven by a BLDC motor under field-oriented control.
Power and USB data are passed from the stationary base to the rotating part through a slip ring,
so devices mounted on top can be rotated continuously while staying connected to a host.

## Architecture

![Hardware architecture](docs/OWL%20HW%20arch.drawio.png)

- **Stator PCB**: Sits in the stationary base. Provides the USB-C power input with a USB PD trigger (CH224K) and the USB data port to the host.
- **Rotor PCB** (controller): Rotates with the platform. Contains the RP2354B controller, the DRV8311 BLDC driver, 5 V and 3.3 V regulators, a USB hub with a passthrough port, an RM2 radio module, and an I²C/UART port.
- **Magnetic sensor PCB**: Measures the rotor angle for motor control using an MA600A magnetic angle sensor.

## Repository structure

| Path             | Content                                         |
| :--------------- | :---------------------------------------------- |
| `pcb/controller` | KiCad project for the rotor/controller PCB.     |
| `pcb/stator`     | KiCad project for the stator PCB.               |
| `pcb/sensor`     | KiCad projects for the magnetic sensor PCBs.    |
| `docs`           | Renders, architecture diagram, and logo.        |

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

MIT, see [LICENSE](LICENSE).
