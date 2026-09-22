# CAD

The mechanical parts of the OWL are designed in Onshape:

<https://cad.onshape.com/documents/fccfa08dfedefe67cfdb683e/w/4726c041ddb97f340fe57a69/e/d62cb220f0c6f90c2b79ed01?renderMode=0&uiState=6ab278394572ec6a44ada120>

The Onshape document is the source of truth. Anything in this folder is an export of it.

## Printing the parts

Download `owl-<version>-3d-print.zip` from the [latest release](https://github.com/sedlak477/owl-hardware/releases/latest) and print **`OWL.3mf`**.
It contains all parts for one OWL, already laid out on one plate with a brim, so you only have to open it in your slicer, pick your printer and filament, and print.
Use a heat-resistant filament like ABS or ASA: the motor gets warm, and the motor adapter and the parts around it must not soften.

Alternatively, the archive has one STEP file per part, for example to arrange the parts yourself or to print only the motor adapter in ABS and the rest in another material.

## Files

The same files are in [`3d-print/`](3d-print/):

| File                               | Content                                                             |
| :--------------------------------- | :------------------------------------------------------------------ |
| `OWL.3mf`                          | All parts for one OWL, laid out on a plate, ready to slice.          |
| `Stator - Motor Adapter.step`      | Motor adapter. Print in a heat-resistant filament (e.g. ABS).        |
| `Stator - Small Spacer.step`       | Small spacers between motor adapter and stator PCB.                 |
| `Stator - Big Spacer.step`         | Big spacers between stator PCB and tripod adapter.                  |
| `Stator - Tripod Adapter.step`     | Tripod adapter with the 1/4'' heat insert.                          |
| `Rotor - Board Spacers.step`       | Spacers between sensor PCB and controller PCB.                      |
| `Rotor - Payload Connector.step`   | Payload connector on top of the rotor.                              |

Each STEP file contains as many copies of the part as one OWL needs.

See the [assembly instructions](../docs/Assembly%20instructions.md) for how the parts go together.
