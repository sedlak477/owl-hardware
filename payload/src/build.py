# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["cadquery>=2.4"]
# ///
"""
build.py: payload adapters and tripod mount on the payload connector, CadQuery 2.4+

  generic/                 the blank adapter(), to build your own adapter on
  adapters/<name>/         adapter() with holders/<name>.step fused onto its mount face
  adapters/quarter-inch-thread/   adapter() with a boss for a 1/4"-20 heat insert
  mounts/tripod/           base() and a body with a 1/4"-20 heat insert, screwed together like on the OWL

Run `uv run payload/src/build.py` from the repository root. Every STEP is written in print orientation, on z = 0.
Holder STEPs are in the adapter's device frame (locked pose) with the mount face at z = 0.
"""
from math import radians, tan
from pathlib import Path

import cadquery as cq

import payload_connector as connector

SRC = Path(__file__).resolve().parent
PAYLOAD = SRC.parent

# ---------------- 1/4"-20 heat insert (same as the OWL's tripod adapter) ----------------
INSERT_D = 8.0
INSERT_DEPTH = 12.5
CHAMFER = 0.5

# ---------------- quarter-inch-thread boss ----------------
BOSS_D = 18.0
BOSS_H = 13.0
BOSS_FOOT_D, BOSS_FOOT_H = 24.0, 3.0   # 45° foot, stiffens the joint to the mount face

# ---------------- tripod mount body (cone as in the old mount, printed upside down) ----------------
BODY_H = 14.0
FOOT_R = 7.7                           # 3.7 mm wall around the insert
CONE_ANGLE = 30.0                      # from vertical; top radius ≈ 15.8, under most of the lugs
GRIP_R, GRIP_SPAN, GRIP_Z0, GRIP_Z1, GRIP_FILLET = 8.4, 60.0, 1.3, 8.6, 2.0   # flats between the screws
PILOT_D, PILOT_DEPTH = 1.3, 5.5        # M1.6×6 screws cut their own thread
RELIEF_DEPTH, RELIEF_MARGIN = 0.4, 0.3   # keeps the spring arms off the body
BASE_GAP = 45.0                        # base next to the body on the print bed

HOLDERS = ("nrf52840dk", "nrf54l15dk", "nrf7002dk", "dwm3001cdk", "mocap", "zip-tie-ring")


def single_solid(shape: cq.Shape, name: str) -> cq.Shape:
    solids = shape.Solids()
    if len(solids) != 1:
        raise ValueError(f"{name}: {len(solids)} solids, expected one")
    return solids[0]


def export(shapes: list[cq.Shape], path: Path) -> None:
    cq.exporters.export(cq.Workplane("XY").add(shapes), str(path))
    print("wrote", path.relative_to(PAYLOAD.parent))


def on_adapter(mount: cq.Shape) -> cq.Shape:
    return connector.adapter().val().fuse(mount.translate(cq.Vector(0, 0, connector.ADAPTER_T))).clean()


def holder_adapter(name: str) -> cq.Shape:
    mount = cq.importers.importStep(str(SRC / "holders" / f"{name}.step")).val()
    return single_solid(on_adapter(mount), name)


def quarter_inch_adapter() -> cq.Shape:
    boss = (cq.Workplane("XY")
            .circle(BOSS_FOOT_D / 2).workplane(offset=BOSS_FOOT_H).circle(BOSS_D / 2).loft()
            .union(cq.Workplane("XY").circle(BOSS_D / 2).extrude(BOSS_H))
            .faces(">Z").edges().chamfer(CHAMFER)
            .faces(">Z").workplane().hole(INSERT_D, INSERT_DEPTH)
            .faces(">Z").edges(cq.selectors.RadiusNthSelector(0)).chamfer(CHAMFER))
    return single_solid(on_adapter(boss.val()), "quarter-inch-thread")


def tripod_body() -> cq.Shape:
    """Upright, in payload_connector's construction frame and mirrored like its parts, so screws and arms line up."""
    top_r = FOOT_R + BODY_H * tan(radians(CONE_ANGLE))
    profile = [(0, 0), (FOOT_R, 0), (top_r, BODY_H), (0, BODY_H)]
    body = (cq.Workplane("XZ").polyline(profile).close().revolve(360, (0, 0, 0), (0, 1, 0))
            .faces("<Z").edges().chamfer(CHAMFER)
            .faces("<Z").workplane().hole(INSERT_D, INSERT_DEPTH)
            .faces("<Z").edges(cq.selectors.RadiusNthSelector(0)).chamfer(CHAMFER)
            .val())
    for a in connector.SCREWS:
        x, y = connector.P(connector.SCREW_R, a)
        body = body.cut(connector.cyl(PILOT_D / 2, x, y, BODY_H - PILOT_DEPTH, BODY_H + connector.E))
        grip = connector.sector(GRIP_R, connector.DISC_R + 5, a + 60 - GRIP_SPAN / 2, a + 60 + GRIP_SPAN / 2)
        grip = grip.offset2D(-GRIP_FILLET, "arc")[0].offset2D(GRIP_FILLET, "arc")[0]
        body = body.cut(connector.prism(grip, GRIP_Z0, GRIP_Z1))
    for tip, direction in connector.ARMS:
        relief = connector.sector(connector.ARM_SLOT_IN - RELIEF_MARGIN, connector.ARM_SLOT_OUT + RELIEF_MARGIN,
                           tip - 3 * direction, tip + direction * connector.SPAN)
        body = body.cut(connector.prism(relief, BODY_H - RELIEF_DEPTH, BODY_H + connector.E))
    return single_solid(body.mirror("YZ").clean(), "tripod body")


def main() -> None:
    export([connector.adapter().val()], PAYLOAD / "generic" / "payload-generic.step")
    for name in HOLDERS:
        export([holder_adapter(name)], PAYLOAD / "adapters" / name / f"{name}.step")
    export([quarter_inch_adapter()], PAYLOAD / "adapters" / "quarter-inch-thread" / "quarter-inch-thread.step")
    body = tripod_body().rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180).translate(cq.Vector(0, 0, BODY_H))
    base = connector.base().val().translate(cq.Vector(BASE_GAP, 0, 0))
    export([body, base], PAYLOAD / "mounts" / "tripod" / "tripod.step")


if __name__ == "__main__":
    main()
