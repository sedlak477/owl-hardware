# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["cadquery>=2.4"]
# ///
"""
nrf7002dk.py: holder for the Nordic nRF7002 DK (PCA10143), CadQuery 2.4+

Writes holders/nrf7002dk.step (device frame, locked pose, mount face at z = 0) for build.py.
Run `uv run payload/src/holders/nrf7002dk.py` from the repository root, then `uv run payload/src/build.py`.

The DK stands upright with its antenna end up and the PCB mid-plane through the rotor axis, placed so that the
centre of mass of board and holder is on the axis. It sits on four M2.5 bosses on an open truss instead of a solid plate.
Every strut rises at 45° or steeper, so the adapter prints mount face up without supports.
Board coordinates are from Nordic's PCA10143 v0.7.2 production files (origin at the lower-left corner, top side).
"""
from math import atan2, degrees, hypot
from pathlib import Path

import cadquery as cq

# ---------------- board (PCA10143 v0.7.2, mm) ----------------
PCB_T = 1.6
BOARD_L = 136.525                      # along x; the antenna end (x = 136.5) points up
HOLES = [(13.97, 7.62), (15.24, 55.88), (66.04, 12.70), (66.04, 40.64)]   # Ø3.2 non-plated holes used
AXIS = (135.00, 31.42)                 # board point over the rotor axis: puts the centre of mass of a 35 g DK
                                       # (assumed uniform) and the solid holder on the axis.
                                       # (135.00, 5.85) puts the nRF7002's chip antenna A1 on the axis instead.
BOARD_Z0 = 24.0                        # board's lower edge above the mount face: room for the micro-USB plug (J2)

# ---------------- holder ----------------
STANDOFF = 3.0                         # board back to plate; the bottom side only has passives
PLATE_T = 4.0
STRUT_W = 5.0
BOSS_D = 7.5
HOLE_D = 3.2                           # M2.5 clearance, as on the other DK adapters
NUT_AF, NUT_DEPTH = 5.3, 2.0           # pocket for an M2.5 hex nut (5.0 AF) in the back of each boss
FEET = [(-10.0, 2.5), (10.0, 2.5)]     # strut nodes on the mount face, kept inside the rim
RIB_T, RIB_DEPTH, RIB_H = 3.0, 6.0, 30.0       # fin behind each foot strut, along it
GUSSET_DEPTH, GUSSET_H = 6.0, 14.0             # fin in front of each foot strut, below the board
MIN_SLOPE = 45.0
FACE_R = 18.5                          # foot stays inside this radius, clear of the rim grooves
E = 0.01

OUT = Path(__file__).resolve().parent / "nrf7002dk.step"


def holder_xz(p):
    """Board (x, y) → holder plane (x across seen from the front, z up)."""
    bx, by = p
    return (-(by - AXIS[1]), BOARD_Z0 + bx)


def struts():
    fl, fr = FEET
    h1, h2, h3, h4 = (holder_xz(h) for h in HOLES)
    return [(fl, fr), (fr, h1), (fl, h2), (h1, h3), (h2, h4), (h2, h3), (h1, h4)]


def bar(p, q):
    """Stadium bar from p to q in the sketch frame (x, z_holder, thickness)."""
    (x0, z0), (x1, z1) = p, q
    length = hypot(x1 - x0, z1 - z0)
    s = cq.Workplane("XY").slot2D(length + STRUT_W, STRUT_W, 0).extrude(PLATE_T).val()
    return (s.rotate(cq.Vector(), cq.Vector(0, 0, 1), degrees(atan2(z1 - z0, x1 - x0)))
            .translate(cq.Vector((x0 + x1) / 2, (z0 + z1) / 2, 0)))


def teardrop(r, x, z, y0, length, up=False):
    """Round bar along +y from y0 with a 45° point below (or above, for holes), so it prints without supports."""
    k = 1 if up else -1
    c = 2 ** 0.5
    wp = cq.Workplane("XZ", origin=(0, y0, 0))       # local (x, y) = global (x, z), normal -y
    disc = wp.center(x, z).circle(r).extrude(-length)
    tip = (cq.Workplane("XZ", origin=(0, y0, 0))
           .polyline([(x - r / c, z + k * r / c), (x, z + k * r * c), (x + r / c, z + k * r / c)]).close()
           .extrude(-length))
    return disc.union(tip).val()


def fin(foot, top, y0, depth, h):
    """Triangular fin on the strut foot → top: base on the mount face reaching `depth` along y from the
    plate face y0, edge along the strut's centre line up to height h, RIB_T thick."""
    (fx, fz), (tx, tz) = foot, top
    k = (tx - fx) / (tz - fz)                       # dx/dz along the strut
    zb = -RIB_T                                     # start below the mount face, cut off later, so the
    xb, xh = fx + k * (zb - fz), fx + k * (h - fz)  # tilted fin sits on the face over its full width
    n = cq.Vector(tz - fz, 0, -(tx - fx)).normalized()
    db = depth * (h - zb) / h                       # same hypotenuse as a fin based at z = 0
    pts = [cq.Vector(xb, y0, zb), cq.Vector(xb, y0 + db, zb), cq.Vector(xh, y0, h)]
    face = cq.Face.makeFromWires(cq.Wire.makePolygon(pts + [pts[0]]))
    return cq.Solid.extrudeLinear(face.translate(n * (-RIB_T / 2)), n * RIB_T)


def holder() -> cq.Shape:
    for p, q in struts()[1:]:
        slope = degrees(atan2(abs(q[1] - p[1]), abs(q[0] - p[0])))
        if slope < MIN_SLOPE - 0.5:
            raise ValueError(f"strut {p} → {q} rises at {slope:.1f}°, needs supports")
    holes = [holder_xz(h) for h in HOLES]

    # truss, drawn in the sketch frame and turned upright: sketch (x, y, z) → holder (x, z, y)
    t = None
    for p, q in struts():
        t = bar(p, q) if t is None else t.fuse(bar(p, q))
    t = t.cut(cq.Solid.makeBox(400, 50, 50, cq.Vector(-200, -50, -10)))   # nothing below the mount face
    t = t.rotate(cq.Vector(), cq.Vector(1, 0, 0), 90).mirror("XZ")

    y_board = PCB_T / 2                 # board back face; the PCB mid-plane is on the axis
    y_plate = y_board + STANDOFF
    t = t.translate(cq.Vector(0, y_plate, 0))

    h1, h2 = holder_xz(HOLES[0]), holder_xz(HOLES[1])
    for foot, top in ((FEET[0], h2), (FEET[1], h1)):          # the two struts that carry the board
        t = t.fuse(fin(foot, top, y_plate + PLATE_T - E, RIB_DEPTH, RIB_H))
        t = t.fuse(fin(foot, top, y_plate + E, -GUSSET_DEPTH, GUSSET_H))
    t = t.cut(cq.Solid.makeBox(400, 400, 10, cq.Vector(-200, -200, -10)))   # fins end on the mount face

    for x, z in holes:
        boss = teardrop(BOSS_D / 2, x, z, y_board, STANDOFF + PLATE_T)          # standoff and boss in one
        # the standoff sticks out of the plate's front: slope its underside at 45° back to the plate, so its
        # first layer starts on the plate instead of hanging out STANDOFF mm
        z_tip = z - BOSS_D / 2 * 2 ** 0.5
        ramp = (cq.Solid.makeBox(50, 50, 50, cq.Vector(-25, -50, -50))
                .rotate(cq.Vector(), cq.Vector(1, 0, 0), -45).translate(cq.Vector(x, y_plate, z_tip)))
        t = t.fuse(boss.cut(ramp))
        t = t.cut(teardrop(HOLE_D / 2, x, z, y_board - 1, STANDOFF + PLATE_T + 2, up=True))
        nut = (cq.Workplane("XZ", origin=(x, y_plate + PLATE_T + E, z))
               .transformed(rotate=(0, 0, 90))             # a corner on top: no flat overhang
               .polygon(6, NUT_AF / 0.8660254).extrude(NUT_DEPTH + E).val())
        t = t.cut(nut)
    t = t.clean()
    outside = cq.Solid.makeBox(100, 100, 1, cq.Vector(-50, -50, 0)).cut(cq.Solid.makeCylinder(FACE_R, 1))
    if t.intersect(outside).Volume() > 1e-3:
        raise ValueError(f"holder leaves the mount face (r > {FACE_R}) at its foot")
    return t


if __name__ == "__main__":
    h = holder()
    bb = h.BoundingBox()
    print(f"solids {len(h.Solids())}, volume {h.Volume() / 1000:.1f} cm3, "
          f"x {bb.xmin:.1f}..{bb.xmax:.1f} y {bb.ymin:.1f}..{bb.ymax:.1f} z {bb.zmin:.1f}..{bb.zmax:.1f}")
    cq.exporters.export(cq.Workplane("XY").add(h), str(OUT))
    print("wrote", OUT)
