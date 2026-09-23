# Payloads

A payload is the device you rotate with the OWL, such as a development board or a set of motion-capture markers.
It sits on an adapter, which locks into the payload connector on top of the OWL (`Rotor - Payload Connector` in [`cad/`](../cad/README.md)).

To attach an adapter, put its pegs through the holes in the payload connector and twist it to lock it in place.
Twist it back to take it off.

> [!CAUTION]
> The pegs are fragile. Don't force the adapter when you twist it.

## Folder structure

| Path              | Content                                                                         |
| :---------------- | :------------------------------------------------------------------------------ |
| `generic/`        | The generic adapter: a blank plate with the pegs, to extend for your own payload. |
| `adapters/<name>/` | Ready-made adapters, each with a STEP model, an image and a README.             |
| `mounts/<name>/`   | Mounts that provide a payload connector without an OWL.                         |

## Adapters

| Adapter                                                    | For                                                              |
| :--------------------------------------------------------- | :--------------------------------------------------------------- |
| [`nrf52840dk`](adapters/nrf52840dk/README.md)              | Nordic nRF52840 DK                                               |
| [`nrf54l15dk`](adapters/nrf54l15dk/README.md)              | Nordic nRF54L15 DK                                               |
| [`dwm3001cdk`](adapters/dwm3001cdk/README.md)              | Qorvo DWM3001CDK                                                 |
| [`mocap`](adapters/mocap/README.md)                        | Five optical motion-capture markers                              |
| [`quarter-inch-thread`](adapters/quarter-inch-thread/README.md) | Anything with a camera tripod screw (female 1/4"-20 thread) |
| [`zip-tie-ring`](adapters/zip-tie-ring/README.md)          | Anything you can fix with zip ties or straps                     |

## Using adapters without an OWL

The [tripod mount](mounts/tripod/README.md) screws onto a camera tripod and has the same payload connector as the OWL, so every adapter fits it.
Use it for devices that stay fixed in your setup, such as anchors or reference nodes: they sit on the same adapters and at the same geometry as the rotating ones, and you can move a device between an OWL and a fixed position without taking it off its adapter.

## Electrical interface

The controller PCB on the rotating part offers two connectors for the payload.

### USB-C passthrough (J3)

The main connection for a payload.
J3 is a downstream port of the controller's USB 2.0 hub, so a payload plugged in there shows up on the host next to the OWL itself, over the same data cable through the slip ring.
It also powers the payload from the controller's 5V rail. With the controller's `VBUS` jumper JP1 open (as manufactured), that rail runs from the power supply, so the payload is only powered while the power supply is connected.

### Qwiic / STEMMA QT (J9)

A JST SH 4-pin connector with the Qwiic / STEMMA QT pinout:

| Pin | Signal | RP2354B |
| :-- | :----- | :------ |
| 1   | GND    |         |
| 2   | 3.3V   |         |
| 3   | SDA    | GPIO0   |
| 4   | SCL    | GPIO1   |

J9 connects to the OWL's controller, not to the host, so using it requires changes to the [firmware](https://github.com/sedlak477/owl-firmware).
The controller has no pull-up resistors on SDA and SCL; most Qwiic / STEMMA QT modules have their own.
GPIO0 and GPIO1 can also be configured as UART0 TX and RX, so J9 can be used as a UART port instead.

## Designing your own adapter

Start from the generic adapter and build your holder on top of the plate, leaving the pegs unchanged so it still locks into the payload connector.
It is in the [Onshape document](https://cad.onshape.com/documents/fccfa08dfedefe67cfdb683e/w/4726c041ddb97f340fe57a69/e/d62cb220f0c6f90c2b79ed01) with the rest of the OWL, where you can copy it, and in [`generic/payload-generic.step`](generic/payload-generic.step) for any other CAD tool.

## Contributing

New adapters and mounts are welcome. Add a folder `adapters/<name>/` (or `mounts/<name>/`) with a short lowercase name without spaces, for example the board it holds, containing:

- `<name>.step`: the model
- `<name>.png`: an image of it
- `README.md`: what it holds and any extra hardware needed (screws, inserts, glue)
- optionally `<name>.3mf`, ready to slice

Then add it to the table above and open a pull request.
Contributions are licensed under the same [CERN-OHL-P-2.0](../LICENSE) as the rest of the OWL hardware.
