"""
payload_connector.py: payload connector, version 2 (T-lugs and spring detent), CadQuery 2.4+

  base()       grey part: T-lugs, opposed spring arms, 3 counterbored screw holes. Prints lugs up.
  adapter()    orange part: flat mount face on top, lug pockets + detent groove below. Prints mount face up.
  tripod()     stand option A: three tubes tied together by bridged beams. Prints tubes on the bed.
  standoff()   stand option B: one plain tube. Print 3 (plus spares), or use bought spacers Ø5 × H with bore ≥ 1.7.

Device frame (the frame used by Rotor.step), used by assembled() and for all angles below:
  origin on the rotor axis, z = 0 at the sensor PCB top, angles CCW seen from above.
  Screws: 3× M1.6 on R10.25 at 100 / 220 / 340°. Locked alignment groove at 240°.
  Lock = twist the adapter CLOCKWISE seen from above.

Stack (all from SCREW_L):  H = SCREW_L - (BASE_T - CB_DEPTH) - HOUSING_DEPTH - THREAD_ENG
  M1.6×20 → H = 11.3: base underside 11.3, base top 14.3, adapter top 18.3.
  Keep H ≥ TALL_CONN_TOP + CABLE_CLEAR (9.3) so the 6-pin connector's cable can exit upward.

Run `python payload_connector.py` to write STEP + STL for every part and print the stack report.
"""
import cadquery as cq
from math import cos, sin, tan, radians, pi, sqrt

# ---------------- stack / device interface ----------------
SCREW_L = 20.0           # M1.6 socket head length
THREAD_ENG = 2.25        # thread in housing; housing holes are only ~2.9 deep → aim 2.0–2.5
HOUSING_DEPTH = 5.12     # housing top below sensor PCB top (sensor PCB + spacer + controller PCB)
TALL_CONN_TOP = 5.32     # 6-pin controller connector top above sensor PCB top
CABLE_CLEAR = 4.0        # min space above it for the upward cable
SCREW_R = 10.25
SCREWS_DEV = (100.0, 220.0, 340.0)

# ---------------- base ----------------
DISC_R = 19.5
BASE_T = 3.0
HOLE_D = 2.2             # M1.6 clearance
CB_D, CB_DEPTH = 3.6, 1.7  # counterbore for Ø3.0 × 1.6 head (head sits 0.1 below face)

# ---------------- stand ----------------
TUBE_OD = 5.0
BEAM_W, BEAM_H = 2.4, 1.6

# ---------------- adapter ----------------
ADAPTER_T = 4.0

# ---------------- T-lugs / pockets (print-validated) ----------------
LUG_COUNT = 3
LUG_START, LUG_SPAN = 5.0, 40.0
LUG_R_IN, LUG_R_OUT = 13.5, 16.5
LUG_NECK_H, LUG_FLARE = 1.2, 0.9
SLOT_IN_R, SLOT_OUT_R = 13.3, 16.7
POCKET_IN, POCKET_OUT = 12.3, 17.7
LEDGE_H, ROOF_Z = 1.0, 2.2
PK_A0, PK_LOCK, PK_A1 = 4.0, 49.0, 91.0
LEAD_IN_DEG, LEAD_IN_MIN = 2.5, 0.4
UC_EMBED = 0.2

# ---------------- detent (arms between the screws) ----------------
LOCK_RAMP = 20.0         # deg, lock-in ramp
REL = 45.0               # deg, release flank (40 softer … 50 firmer)
ARMS = [(100.0, 1), (300.0, -1)]   # construction frame: (free-tip angle, direction toward root)
SPAN = 80.0              # deg, arm length (~1.0 % strain)
TOOTH_OFFSET = 8.0       # deg from tip
ARM_IN, ARM_OUT = 8.8, 10.4        # 1.6 wide = 4 lines @ 0.4
ARM_SLOT_IN, ARM_SLOT_OUT = 7.6, 11.0   # inner 1.2 = over-travel stop
TOOTH_FLAT = 2.5
TIP, TOOTH_BASE_R, TOOTH_H = 10.45, 9.6, 2.0
WALL, CREST, FLOOR, RELIEF = 9.85, 9.85, 10.53, 10.6
NOTCH_HALF, CREST_W, TRAVEL_END = 2.6, 0.8, 54.0
ISLAND_R = 6.6

# ---------------- grip + alignment ----------------
GRIP_N, GRIP_H = 12, 0.9
FLAG_HALF = 9.0
MARK, TWIST = 300.0, 45.0          # construction frame (→ 240° device)
GROOVE_HALF_DEG, GROOVE_DEPTH = 3.0, 1.0
RIM_STEP = 0.5
RIM_SEGS = 24

E = 0.01

# ---------------- derived ----------------
H = round(SCREW_L - (BASE_T - CB_DEPTH) - HOUSING_DEPTH - THREAD_ENG, 2)
SCREWS = [180.0 - a for a in SCREWS_DEV]   # construction frame (parts are mirrored at the end)


# ---------------- helpers ----------------
def mm(x, r=10.1):
    return x * 180 / (pi * r)


def P(r, a):
    return (r * cos(radians(a)), r * sin(radians(a)))


def V(r, a, z=0.0):
    x, y = P(r, a)
    return cq.Vector(x, y, z)


def path_wire(items):
    """('p', r, a) points and ('a', r, a0, a1) arcs, joined by lines, closed."""
    edges, cur, start = [], None, None

    def go(v):
        nonlocal cur, start
        if cur is None:
            start = v
        elif (v - cur).Length > 1e-6:
            edges.append(cq.Edge.makeLine(cur, v))
        cur = v

    for it in items:
        if it[0] == 'p':
            go(V(it[1], it[2]))
        else:
            _, r, a0, a1 = it
            go(V(r, a0))
            v1 = V(r, a1)
            edges.append(cq.Edge.makeThreePointArc(cur, V(r, (a0 + a1) / 2), v1))
            cur = v1
    if (start - cur).Length > 1e-6:
        edges.append(cq.Edge.makeLine(cur, start))
    return cq.Wire.assembleEdges(edges)


def poly_wire(pts):
    v = [cq.Vector(x, y, 0) for x, y in pts]
    return cq.Wire.makePolygon(v + [v[0]])


def circle_wire(r, cx=0.0, cy=0.0):
    return cq.Wire.makeCircle(r, cq.Vector(cx, cy, 0), cq.Vector(0, 0, 1))


def prism(wire, z0, z1):
    return (cq.Workplane("XY").add(wire.translate(cq.Vector(0, 0, z0)))
            .toPending().extrude(z1 - z0).val())


def cyl(r, cx, cy, z0, z1):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(cx, cy, z0), cq.Vector(0, 0, 1))


def sector(r0, r1, a0, a1):
    return path_wire([('a', r1, a0, a1), ('a', r0, a1, a0)])


def revolve(profile, a0, a1):
    span = a1 - a0
    s = cq.Workplane("XZ").polyline(profile).close().revolve(span, (0, 0, 0), (0, 1, 0)).val()
    c = s.Center()
    from math import atan2, degrees
    if degrees(atan2(c.y, c.x)) < 0:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), span)
    return s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), a0)


def loft_profiles(profile_at, a0, a1, step=0.5):
    n = max(2, int(round((a1 - a0) / step)))
    wires = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts = [V(r, a, z) for r, z in profile_at(a)]
        wires.append(cq.Wire.makePolygon(pts + [pts[0]]))
    return cq.Solid.makeLoft(wires, True)


def _rot(shape, a):
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), a)


def rim_r(a, marks):
    """Rim radius without the alignment grooves: grip lobes, flattened around each mark."""
    t = (a * GRIP_N / 360) % 1
    r = DISC_R + GRIP_H * 0.85 * sin(t * pi) ** 1.5
    for g in marks:
        ctr = (g[0] + g[-1]) / 2
        dc = abs(((a - ctr + 540) % 360) - 180)
        half = FLAG_HALF + (g[-1] - g[0]) / 2
        if dc >= half + 4:
            continue
        u = min(1, max(0, (half + 4 - dc) / 4))
        w = u * u * (3 - 2 * u)
        r = r * (1 - w) + (DISC_R + GRIP_H) * w
    return r


def rim_wire(marks):
    """Smooth rim as RIM_SEGS spline segments; a single periodic spline imports broken into Onshape."""
    n = int(round(360 / RIM_STEP))
    per = n // RIM_SEGS
    pt = lambda i: V(rim_r(i * RIM_STEP, marks), i * RIM_STEP)
    tan = lambda i: (pt(i + 1) - pt(i - 1)).normalized()
    edges = []
    for k in range(RIM_SEGS):
        idx = range(k * per, (k + 1) * per + 1)
        edges.append(cq.Edge.makeSpline([pt(i) for i in idx], tangents=[tan(idx[0]), tan(idx[-1])], scale=True))
    return cq.Wire.assembleEdges(edges)


def rim_disc(marks, t):
    """Disc with the grip rim, alignment grooves cut as elliptic cylinders (sharp edges stay exact)."""
    d = prism(rim_wire(marks), 0, t)
    r0 = DISC_R + GRIP_H
    groove = prism(cq.Wire.makeEllipse(r0 * sin(radians(GROOVE_HALF_DEG)), GROOVE_DEPTH, cq.Vector(0, 0, 0),
                                       cq.Vector(0, 0, 1), cq.Vector(0, 1, 0)), -1, t + 1).translate(cq.Vector(r0, 0, 0))
    for g in marks:
        for m in g:
            d = d.cut(_rot(groove, m))
    return d.clean()


BASE_MARKS = [[MARK]]
ADAPTER_MARKS = [[MARK], [MARK + TWIST - 2.6, MARK + TWIST + 2.6]]


# ---------------- construction-frame parts ----------------
def _base():
    b = rim_disc(BASE_MARKS, BASE_T)
    for f, s in ARMS:
        void = path_wire([('a', ARM_SLOT_OUT, f - 3 * s, f + s * SPAN), ('a', ARM_OUT, f + s * SPAN, f),
                          ('a', ARM_IN, f, f + s * SPAN), ('a', ARM_SLOT_IN, f + s * SPAN, f - 3 * s)])
        b = b.cut(prism(void, -E, BASE_T + E))
    for a in SCREWS:
        x, y = P(SCREW_R, a)
        b = b.cut(cyl(HOLE_D / 2, x, y, -E, BASE_T + E))
        b = b.cut(cyl(CB_D / 2, x, y, BASE_T - CB_DEPTH, BASE_T + E))
    tf = TOOTH_FLAT
    tw = tf + mm((TIP - TOOTH_BASE_R) / tan(radians(45)))
    for f, s in ARMS:
        c = f + TOOTH_OFFSET * s
        tooth = path_wire([('a', ARM_IN, c + tw, c - tw), ('p', TOOTH_BASE_R, c - tw),
                           ('a', TIP, c - tf, c + tf), ('p', TOOTH_BASE_R, c + tw)])
        b = b.fuse(prism(tooth, BASE_T - E, BASE_T + TOOTH_H))
    lug_h = LUG_NECK_H + LUG_FLARE
    z0 = BASE_T - E
    lug = revolve([(LUG_R_IN, z0), (LUG_R_OUT, z0), (LUG_R_OUT, BASE_T + LUG_NECK_H),
                   (LUG_R_OUT + LUG_FLARE, BASE_T + lug_h), (LUG_R_IN - LUG_FLARE, BASE_T + lug_h),
                   (LUG_R_IN, BASE_T + LUG_NECK_H)], LUG_START, LUG_START + LUG_SPAN)
    for k in range(LUG_COUNT):
        b = b.fuse(_rot(lug, k * 360 / LUG_COUNT))
    return b.clean()


def _groove_wire():
    nf = NOTCH_HALF
    fl = mm((FLOOR - CREST) / tan(radians(REL)))
    cw = mm(CREST_W)
    rp = mm((RELIEF - CREST) / tan(radians(LOCK_RAMP)))
    feats = []
    for f, s in ARMS:
        c = f + TOOTH_OFFSET * s
        a0, a1 = c - nf - fl, c + TRAVEL_END
        feats.append((a0, a1, [('p', WALL, a0), ('a', FLOOR, c - nf, c + nf), ('p', CREST, c + nf + fl),
                               ('a', CREST, c + nf + fl, c + nf + fl + cw),
                               ('a', RELIEF, c + nf + fl + cw + rp, a1), ('p', WALL, a1)]))
    feats.sort(key=lambda t: t[0])
    items = []
    for i, (a0, a1, it) in enumerate(feats):
        items += it
        nxt = feats[(i + 1) % len(feats)][0]
        if nxt <= a1:
            nxt += 360
        items.append(('a', WALL, a1, nxt))
    return path_wire(items)


def _adapter():
    a = rim_disc(ADAPTER_MARKS, ADAPTER_T)
    a = a.cut(prism(_groove_wire(), -E, ROOF_Z))
    a = a.fuse(prism(circle_wire(ISLAND_R), 0, ROOF_Z + E))
    for k in range(LUG_COUNT):
        o = k * 360 / LUG_COUNT
        key = path_wire([('a', SLOT_OUT_R, PK_A0 + o, PK_LOCK + o), ('a', POCKET_OUT, PK_LOCK + o, PK_A1 + o),
                         ('a', POCKET_IN, PK_A1 + o, PK_LOCK + o), ('a', SLOT_IN_R, PK_LOCK + o, PK_A0 + o)])
        a = a.cut(prism(key, -E, LEDGE_H))
        a = a.cut(prism(sector(POCKET_IN, POCKET_OUT, PK_A0 + o, PK_A1 + o), LEDGE_H - E, ROOF_Z))
    # undercut triangles, extended by UC_EMBED into the pocket wall so they don't share a face with it
    inner = lambda q: [(POCKET_IN - UC_EMBED, LEDGE_H), (POCKET_IN + q, LEDGE_H),
                       (POCKET_IN - UC_EMBED, LEDGE_H + q + UC_EMBED)]
    outer = lambda q: [(POCKET_OUT - q, LEDGE_H), (POCKET_OUT + UC_EMBED, LEDGE_H),
                       (POCKET_OUT + UC_EMBED, LEDGE_H + q + UC_EMBED)]
    lead = lambda ang: min(1, max(LEAD_IN_MIN, LEAD_IN_MIN + (1 - LEAD_IN_MIN) * (PK_LOCK - ang) / LEAD_IN_DEG))
    for prof in (inner, outer):
        uc = revolve(prof(1.0), PK_A0, PK_LOCK - LEAD_IN_DEG).fuse(
            loft_profiles(lambda ang: prof(lead(ang)), PK_LOCK - LEAD_IN_DEG, PK_LOCK))
        for k in range(LUG_COUNT):
            a = a.fuse(_rot(uc, k * 360 / LUG_COUNT))
    return a


def _tube(a):
    x, y = P(SCREW_R, a)
    return cyl(TUBE_OD / 2, x, y, 0, H).cut(cyl(HOLE_D / 2, x, y, -E, H + E))


def _tripod():
    t = None
    for a in SCREWS:
        t = _tube(a) if t is None else t.fuse(_tube(a))
    for i in range(3):
        p, q = cq.Vector(*P(SCREW_R, SCREWS[i]), 0), cq.Vector(*P(SCREW_R, SCREWS[(i + 1) % 3]), 0)
        u = (q - p).normalized()
        n = cq.Vector(-u.y, u.x, 0) * (BEAM_W / 2)
        a = p + u * (TUBE_OD / 2 - 0.4)
        b = q - u * (TUBE_OD / 2 - 0.4)
        beam = prism(poly_wire([(c.x, c.y) for c in (a + n, b + n, b - n, a - n)]), H - BEAM_H, H)
        t = t.fuse(beam)
    for a in SCREWS:                       # keep bores clear where beams meet tubes
        x, y = P(SCREW_R, a)
        t = t.cut(cyl(HOLE_D / 2, x, y, -E, H + E))
    return t.clean()


# ---------------- public API (device frame) ----------------
def _final(shape):
    return cq.Workplane("XY").add(shape.mirror("YZ"))


def base():
    """Base, print orientation: bottom on z=0, lugs up."""
    return _final(_base())


def adapter():
    """Adapter, print orientation: mating face z=0, mount face z=ADAPTER_T."""
    return _final(_adapter())


def tripod():
    """4a stand, print orientation: tubes on z=0, beams on top."""
    return _final(_tripod())


def standoff():
    """4b single tube at the origin (print 3)."""
    return cq.Workplane("XY").add(cyl(TUBE_OD / 2, 0, 0, 0, H).cut(cyl(HOLE_D / 2, 0, 0, -E, H + E)))


def assembled(locked=True, stand="tripod"):
    """Device frame: stand on the sensor PCB (z=0), base at z=H, adapter at z=H+BASE_T."""
    ad = adapter().translate((0, 0, H + BASE_T))
    if not locked:
        ad = ad.rotate((0, 0, 0), (0, 0, 1), TWIST)
    if stand == "tripod":
        st = tripod()
    else:
        st = None
        for a in SCREWS_DEV:
            s = standoff().translate((*P(SCREW_R, a), 0))
            st = s if st is None else st.union(s)
    return st, base().translate((0, 0, H)), ad


def report():
    seat = H + BASE_T - CB_DEPTH
    tip = seat - SCREW_L
    print(f"stack: H = {H:.2f}  base top {H + BASE_T:.2f}  adapter top {H + BASE_T + ADAPTER_T:.2f}")
    print(f"screw M1.6x{SCREW_L:g}: seat {seat:.2f}, tip {tip:.2f}, thread in housing {-HOUSING_DEPTH - tip:.2f} mm")
    print(f"clearance above 6-pin connector: {H - TALL_CONN_TOP:.2f} mm (need >= {CABLE_CLEAR})")
    if H - TALL_CONN_TOP < CABLE_CLEAR:
        print("  WARNING: base too low for the upward cable; use a longer screw")


if __name__ == "__main__":
    report()
    parts = {"connector_base": base(), "connector_adapter": adapter(),
             "connector_tripod": tripod(), "connector_standoff": standoff()}
    for name, p in parts.items():
        cq.exporters.export(p, f"{name}.step")
        cq.exporters.export(p, f"{name}.stl", tolerance=0.01, angularTolerance=0.1)
    print("wrote", ", ".join(parts))
elif "show_object" in globals():
    st, b, a = assembled()
    show_object(st, name="tripod", options={"color": "#8d9298"})
    show_object(b, name="base", options={"color": "#5a5e63"})
    show_object(a, name="adapter", options={"color": "#d9772f"})
