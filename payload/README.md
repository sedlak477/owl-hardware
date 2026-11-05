# Payloads

A payload is the device you rotate with the OWL, such as a development board or a set of motion-capture markers.
It sits on an adapter, which locks onto the connector base on top of the OWL.

> [!IMPORTANT]
> These adapters use version 2 of the payload connector: a base with three T-lugs and a spring detent. It is incompatible with version 1, which locks with pegs in slots.
> For an OWL with the version 1 connector, use the adapters from [release v1.2.2](https://github.com/sedlak477/owl-hardware/tree/v1.2.2/payload), or print the version 2 base and stand and swap them in (see steps 22 and 23 of the [assembly instructions](../docs/Assembly%20instructions.md)).

To attach an adapter, put it on the base with its double groove over the base's single groove, so the lugs drop into the adapter's pockets.
Then twist it clockwise (seen from above) by 45° until the detent clicks and the single grooves line up.
To take it off, twist it back counterclockwise. The detent needs a firm twist to release.

## Folder structure

| Path              | Content                                                                         |
| :---------------- | :------------------------------------------------------------------------------ |
| `generic/`        | The generic adapter: a blank adapter with a flat mount face, to extend for your own payload. |
| `adapters/<name>/` | Ready-made adapters, each with a STEP model, an image and a README.             |
| `mounts/<name>/`   | Mounts that provide a payload connector without an OWL.                         |
| `src/`             | The connector source (`payload_connector.py`), the build script and the holders it puts on the adapters. |

## Adapters

| Adapter                                                    | For                                                              |
| :--------------------------------------------------------- | :--------------------------------------------------------------- |
| [`nrf52840dk`](adapters/nrf52840dk/README.md)              | Nordic nRF52840 DK                                               |
| [`nrf54l15dk`](adapters/nrf54l15dk/README.md)              | Nordic nRF54L15 DK                                               |
| [`nrf7002dk`](adapters/nrf7002dk/README.md)                | Nordic nRF7002 DK                                                |
| [`dwm3001cdk`](adapters/dwm3001cdk/README.md)              | Qorvo DWM3001CDK                                                 |
| [`mocap`](adapters/mocap/README.md)                        | Five optical motion-capture markers                              |
| [`quarter-inch-thread`](adapters/quarter-inch-thread/README.md) | Anything with a camera tripod screw (female 1/4"-20 thread) |
| [`zip-tie-ring`](adapters/zip-tie-ring/README.md)          | Anything you can fix with zip ties or straps                     |

These adapters were made for our own experiments, and some of them are quick designs that could be done better.
If you improve one, please contribute it back (see [Contributing](#contributing)).

## Using adapters without an OWL

The [tripod mount](mounts/tripod/README.md) screws onto a camera tripod and has the same connector base as the OWL, so every adapter fits it.
Use it for devices that stay fixed in your setup, such as anchors or reference nodes: they sit on the same adapters and at the same geometry as the rotating ones, and you can move a device between an OWL and a fixed position without taking it off its adapter.

## Electrical interface

The controller PCB on the rotating part offers two connectors for the payload.

### USB-C passthrough

The main connection for a payload.
This port is a downstream port of the controller's USB 2.0 hub, so a payload plugged in there shows up on the host next to the OWL itself, over the same data cable through the slip ring.
It also powers the payload from the controller's 5V rail. With the controller's `VBUS` solder jumper open (as manufactured), that rail runs from the power supply, so the payload is only powered while the power supply is connected.

### Qwiic / STEMMA QT

A JST SH 4-pin connector with the Qwiic / STEMMA QT pinout:

| Pin | Signal | RP2354B |
| :-- | :----- | :------ |
| 1   | GND    |         |
| 2   | 3.3V   |         |
| 3   | SDA    | GPIO0   |
| 4   | SCL    | GPIO1   |

This port connects to the OWL's controller, not to the host, so using it requires changes to the [firmware](https://github.com/sedlak477/owl-firmware).
The controller has no pull-up resistors on SDA and SCL; most Qwiic / STEMMA QT modules have their own.
GPIO0 and GPIO1 can also be configured as UART0 TX and RX, so the port can be used as a UART port instead.

## Designing your own adapter

The connector is defined in [`src/payload_connector.py`](src/payload_connector.py) (CadQuery 2.4+). Build on top of it and leave its geometry unchanged.
Fuse your holder onto the mount face of the generic adapter, [`generic/payload-generic.step`](generic/payload-generic.step) in any CAD tool, or in CadQuery:

```python
adapter().union(holder.translate((0, 0, ADAPTER_T)))
```

- **Mount face:** the top face of the adapter, solid Ø39 at z = 4. The STEP is in print orientation, with the mating face on z = 0.
- **Keep-out:** nothing below z = 4 within 18 mm of the axis (lug pockets and detent groove). Don't cover the alignment grooves on the rim: the single groove at 240° and the double groove at about 195°.
- **Orientation:** the generic STEP is in the locked pose, in the OWL's frame: origin on the rotor axis, angles counterclockwise seen from above. A holder drawn on it sits the same way round on the OWL.
- **Printing:** the adapter prints mount face up without supports, so keep overhangs ≤ 45° and bridges ≤ 10 mm. The clearances are set for PLA on a Bambu X1C (0.4 mm nozzle, 0.2 mm layers). In PETG, add about 0.05 mm to the clearances and use 0.15 mm elephant-foot compensation.
- **Load:** the three lugs carry pull-off and moment loads; the detent only stops the adapter from turning. Keep the payload's centre of mass within about 30 mm of the axis. PLA creeps under heat and constant load, so use PETG for warm or outdoor use.

The adapters in `adapters/` and the tripod mount are built by [`src/build.py`](src/build.py), from the holders in `src/holders/` and its own code for the 1/4" thread adapter and the tripod mount. To rebuild all of them, run from the repository root:

```sh
uv run payload/src/build.py
```

## Contributing

New adapters and mounts are welcome, and so are improvements to the existing ones. Add a folder `adapters/<name>/` (or `mounts/<name>/`) with a short lowercase name without spaces, for example the board it holds, containing:

- `<name>.step`: the model
- `<name>.png`: an image of it
- `README.md`: what it holds and any extra hardware needed (screws, inserts, glue)
- optionally `<name>.3mf`, ready to slice

If you build it with `build.py`, also add the holder as `src/holders/<name>.step` (mount face at z = 0, locked pose) and its name to `HOLDERS`.

Then add it to the table above and open a pull request.
Contributions are licensed under the same [CERN-OHL-P-2.0](../LICENSE) as the rest of the OWL hardware.
