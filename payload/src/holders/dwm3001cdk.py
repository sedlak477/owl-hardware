# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["cadquery>=2.4"]
# ///
"""
dwm3001cdk.py: holder for the Qorvo DWM3001CDK, CadQuery 2.4+

Writes holders/dwm3001cdk.step (device frame, locked pose, mount face at z = 0) for build.py.
Run `uv run payload/src/holders/dwm3001cdk.py` from the repository root, then `uv run payload/src/build.py`.

The board snaps into six clips: two on the mount face under its lower edge and two on each side.
The clips and the board pose are the same as on the previous solid-plate holder, which puts the antenna on the
rotor axis: board upright, front face on y = 0.725, side edges on x = -17 and 26, lower edge on z = 1.75,
turned 10° about the axis.
Instead of the plate behind the board, the clips sit on an open frame: two side stiles, a bottom bar and an X brace
whose feet stand on the mount face. Every strut rises at 45° or steeper.
"""
from math import atan2, cos, degrees, hypot, radians, sin
from pathlib import Path

import cadquery as cq

YAW = 10.0                             # holder turned about the rotor axis, as before

# ---------------- board seat (from the previous holder, mm) ----------------
BOARD_X0, BOARD_X1 = -17.0, 26.0       # board side edges
WALL_L, WALL_R = -18.75, 27.75         # outer walls of the side clips
Y_ROOT = 12.975                        # clip roots: back of the free space behind the board

# clip cross-section in (u, d): u along y (toward the board's back is +u), d inward from the clip's outer wall.
# Board front face on u = 0.725, back face on u = 2.475, edge on d = 1.75, with Ø0.6 reliefs in the corners.
CLIP_W = 8.0
SIDE_CLIPS_L = (1.75, 37.5)            # z of the lower end of each left clip
SIDE_CLIPS_R = (11.0, 37.5)
BOTTOM_CLIPS = (-6.75, 15.75)          # x of the left end of each bottom clip

# ---------------- frame (behind the clip roots) ----------------
FRAME_T = 3.0                          # depth along y, from Y_ROOT back
LIP_D = 1.75                           # rim lip along the stiles, in front of Y_ROOT, as on the old plate
STILE_W = 4.5                          # covers the clip gussets (d = 4.26)
STILE_TOP = 45.5                       # top of the upper side clips
BAR_H = 4.5                            # bottom bar, covers the bottom clip gussets
STRUT_W = 4.0
FEET = (-9.0, 9.0)                     # x of the X-brace feet on the mount face
TOP_Z = 43.5                           # where the X brace meets the stiles
BUTTRESS_H, BUTTRESS_R = 8.0, 19.3     # 45° wedge behind the bottom bar, inside the mount face
MIN_SLOPE = 45.0
E = 0.01

OUT = Path(__file__).resolve().parent / "dwm3001cdk.step"


def clip_profile() -> cq.Workplane:
    """Closed clip cross-section in a workplane whose local x is u and local y is d."""
    return (cq.Workplane("XY")
            .moveTo(Y_ROOT + E, 0).lineTo(-0.739, 0)
            .threePointArc((-1.739, 1.0), (-1.239, 1.866))         # rounded hook tip
            .lineTo(0.725, 3.0)                                     # lead-in
            .lineTo(0.725, 2.05)                                    # catch on the board front
            .threePointArc((0.425, 1.75), (1.025, 1.75))            # corner relief
            .lineTo(2.175, 1.75)                                    # seat for the board edge
            .threePointArc((2.475, 1.45), (2.475, 2.05))            # corner relief
            .lineTo(2.475, 3.75)                                    # rest for the board back
            .lineTo(4.182, 2.043)
            .threePointArc((4.506, 1.826), (4.889, 1.75))
            .lineTo(9.966, 1.75)
            .lineTo(Y_ROOT + E, 4.257)                              # gusset to the root
            .close())


def clip(kind: str, at: float) -> cq.Shape:
    """kind 'L'/'R': side clip with its lower end at z = at; 'B': bottom clip with its left end at x = at."""
    prof = clip_profile().extrude(CLIP_W).val()             # u → x, d → y, width → z
    # map (u, d, w) to the holder frame
    if kind == "B":                                          # u → y, d → z, w → x
        m = cq.Matrix([[0, 0, 1, at], [1, 0, 0, 0], [0, 1, 0, 0]])
    elif kind == "L":                                        # u → y, d → +x from the left wall, w → z
        m = cq.Matrix([[0, 1, 0, WALL_L], [1, 0, 0, 0], [0, 0, 1, at]])
    else:                                                    # u → y, d → -x from the right wall, w → z
        m = cq.Matrix([[0, -1, 0, WALL_R], [1, 0, 0, 0], [0, 0, 1, at]])
    return prof.transformGeometry(m)


def box(x0, x1, y0, y1, z0, z1) -> cq.Shape:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def strut(p, q) -> cq.Shape:
    """Stadium bar from p to q in the frame plane (x, z), FRAME_T deep behind Y_ROOT."""
    (x0, z0), (x1, z1) = p, q
    length = hypot(x1 - x0, z1 - z0)
    s = cq.Workplane("XZ", origin=(0, Y_ROOT - E, 0)).slot2D(length + STRUT_W, STRUT_W, 0).extrude(-FRAME_T - E).val()
    return (s.rotate(cq.Vector(), cq.Vector(0, 1, 0), -degrees(atan2(z1 - z0, x1 - x0)))
            .translate(cq.Vector((x0 + x1) / 2, 0, (z0 + z1) / 2)))


def holder() -> cq.Shape:
    y1 = Y_ROOT + FRAME_T
    xl, xr = WALL_L + STILE_W / 2, WALL_R - STILE_W / 2      # stile centre lines
    braces = [((FEET[0], 0.0), (xr, TOP_Z)), ((FEET[1], 0.0), (xl, TOP_Z))]
    for p, q in braces:
        slope = degrees(atan2(abs(q[1] - p[1]), abs(q[0] - p[0])))
        if slope < MIN_SLOPE:
            raise ValueError(f"strut {p} → {q} rises at {slope:.1f}°, needs supports")

    parts = [
        box(WALL_L, WALL_L + STILE_W, Y_ROOT - E, y1, 0, STILE_TOP),          # left stile
        box(WALL_R - STILE_W, WALL_R, Y_ROOT - E, y1, 0, STILE_TOP),          # right stile
        box(WALL_L, WALL_L + LIP_D, Y_ROOT - 2.25, Y_ROOT, 0, STILE_TOP),     # rim lips, as on the old plate
        box(WALL_R - LIP_D, WALL_R, Y_ROOT - 2.25, Y_ROOT, 0, STILE_TOP),
        box(WALL_L, WALL_R, Y_ROOT - E, y1, 0, BAR_H),                        # bottom bar
    ]
    parts += [strut(p, q) for p, q in braces]
    # wedge behind the bottom bar, sloped at 45° and kept on the mount face
    wedge = (cq.Workplane("YZ", origin=(-30, 0, 0))
             .polyline([(y1 - E, 0), (y1 + BUTTRESS_H, 0), (y1 - E, BUTTRESS_H + E)]).close()
             .extrude(60).val())
    parts.append(wedge.intersect(cq.Solid.makeCylinder(BUTTRESS_R, BUTTRESS_H + 1)))
    parts += [clip("L", z) for z in SIDE_CLIPS_L] + [clip("R", z) for z in SIDE_CLIPS_R]
    parts += [clip("B", x) for x in BOTTOM_CLIPS]

    h = parts[0]
    for p in parts[1:]:
        h = h.fuse(p)
    h = h.cut(box(-100, 100, -100, 100, -20, 0)).clean()       # nothing below the mount face
    return h.rotate(cq.Vector(), cq.Vector(0, 0, 1), YAW)


if __name__ == "__main__":
    h = holder()
    bb = h.BoundingBox()
    print(f"solids {len(h.Solids())}, volume {h.Volume() / 1000:.1f} cm3, "
          f"x {bb.xmin:.1f}..{bb.xmax:.1f} y {bb.ymin:.1f}..{bb.ymax:.1f} z {bb.zmin:.1f}..{bb.zmax:.1f}")
    cq.exporters.export(cq.Workplane("XY").add(h), str(OUT))
    print("wrote", OUT)
