#!/usr/bin/env python3
"""Struts for the rover: four 7 cm arms (pivot axis to wheel axle) on the two hub studs.

Run after hardware/body/body.py:
    .venv/bin/python hardware/strut/strut.py        writes hardware/strut/out/struts.step

What is modelled
  * Per side two struts on the stud's axle stub, one inboard (A, toward +y) and one outboard (B, toward -y), each
    a pivot boss (30 mm x 7 mm) with a 3 mm tapered plate arm to a wheel-axle boss, 70.00 mm pivot to axle
    (Wilcox & Jones: "each strut is 7 cm long from the center of their pivot to the center of the wheel axis").
  * A placeholder wheel envelope: 65 mm diameter (Wilcox & Jones), width and tread are NOT published, so 22 mm
    and a plain cylinder stand in for them.  The wheels sit outboard of the struts.
Everything else (pivot motors, bearings, potentiometers, belts, the strut plate outline) is a placeholder: the
sources give the strut length and wheel diameter only.  Z is up, z = 0 at the outside of the box floor.
"""
import math
import sys
from pathlib import Path
from build123d import *

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "body"))
import body as E  # noqa: E402

OUT = HERE / "out"
BODY_OUT = HERE.parent / "body" / "out"
HW_HUB = HERE.parent / "hub" / "out"

# ---------------- PARAMETERS ----------------
STRUT_L = 70.0                 # pivot axis to wheel axle (Wilcox & Jones)
WHEEL_D = 65.0                 # Wilcox & Jones
WHEEL_W = 44.6                 # inner face to cone apex, from the photos (see wheel.py); the papers do not publish it
COLLAR_L = 8.0                 # collar standing on the cone apex (wheel.py)
POSE_DEG = 25.0                # strut angle below horizontal for the default stance (a choice, not sourced)
BOSS_D, BOSS_T = 30.0, 7.0     # pivot boss
TIP_D = 24.0                   # wheel-axle boss (was 18 mm; 24 mm leaves 2.4 mm of wall around the 19 mm spindle tube)
PLATE_T = 3.0                  # arm plate thickness
AXLE_D = 6.0                   # wheel axle stub
BORE_D = 12.1                  # pivot bore on the stud's 12 mm axle
GAP = 1.0                      # washer gap between layers
HUB_MODE = "coaxial"           # "coaxial": the two struts of a side turn on concentric shafts driven by servos in the body (hardware/hub/hub.py): strut A's bore is 15.05 mm
                               # (hollow shaft), strut B's 5.05 mm (inner shaft); "stud": the earlier stationary 12 mm stud with a 12.1 mm bore (body.py)
TIP_MODE = "motor"             # "motor": the wheel motor sits in the wheel, carried by the strut tip (layout C, docs/drivetrain-spec.md);
                               # "axle": the earlier 6 mm wheel-axle stub (no motor)
# Isogrid lightening (off by default): triangular pockets cut from the INBOARD face of each arm plate only, so the outward faces stay smooth.
# Cells of side ISO_CELL, ribs ISO_RIB wide, pockets ISO_DEPTH deep (the plate is PLATE_T = 3 mm, so the skin left is PLATE_T - ISO_DEPTH), kept ISO_BORDER away
# from the plate edge and from the pivot and tip bosses.  An experiment; see docs/strut-spec.md.
ISOGRID = False
ISO_CELL, ISO_RIB, ISO_DEPTH, ISO_BORDER = 8.0, 1.5, 1.8, 2.5
# Wheel motor: Pololu #3068, 250:1 micro metal gearmotor HPCB 6 V (pololu.com/product/3068/specs, read 2026-11-11): 10 x 12 x 25 mm, 9.5 g, 3 mm D-shaft 9 mm long.
# Modelled as a 10 x 12 x 25 mm box (12 mm along the arm) with the tail at the inboard face of strut A's plate, clamped in a slot in each strut tip.
MOTOR_W, MOTOR_H, MOTOR_L = 10.0, 12.0, 25.0   # across (vertical, local y), along the arm (local x), length along the axle
MOTOR_G = 9.5
SHAFT_D = 3.0
# Wheel support (2026-11-11).  The #3068's shaft is only 9 mm long and Pololu gives a practical radial limit of 0.25 to 0.5 kgf, against 0.25 kgf of static wheel load, so
# the motor does not carry the wheel.  A thin-walled aluminium SPINDLE TUBE is clamped in a round bore in each strut tip; the motor sits inside it (paste or adhesive in the
# gap, so the strut is its heat sink); the tube ends in a cap and a BARREL holding two small ball bearings on a 3 mm STUB SHAFT; the stub shaft runs to the wheel's apex
# boss, and a small COUPLING joins it to the motor shaft inside the tube.  Dimensions below are my design choices; the bearings are 693-size (3 x 8 x 4 mm), their mass
# and rating are typical values, not looked up.
SPINDLE_OD, SPINDLE_ID = 19.0, 16.2    # tube; the motor is 15.6 mm across its diagonal
CAP_T = 1.5                            # end wall of the tube
BARREL_OD, BRG_OD, BRG_ID, BRG_W = 11.0, 8.0, 3.0, 4.0
TUBE_END = 116.25                      # |x| of the outer face of the cap (the same for both struts)
BRG_X = (116.25, 120.25)               # |x| of the inboard face of each bearing: side by side, no spacer (centres 118.25 and 122.25)
BARREL_END = 124.5                     # |x| where the barrel ends (the wheel's apex boss starts at 125.05)
# Tip clamp (docs/mechanical-spec.md item 2, hand check hardware/strut/pivot_checks.py): the 3 mm plate alone is too short a clamp (a 0.1 mm slip fit tilts the tube 1.9 degrees),
# so the tip boss gets a COLLAR_IN mm collar on its inboard side (toward the body wall at |x| = 70), the tube starts as far inboard, a 0.6 mm slit runs from the bore through the
# tip's outer wall, and an M2 clamp screw crosses the slit (2.0 mm hole, 3.9 mm counterbore for the head on the +y side in the strut's local frame).
COLLAR_IN, SLIT_W = 4.0, 0.6
WIRE_W, WIRE_DEPTH = 1.5, 1.0               # the wire groove on strut B's plate and the notch through the collar (two 0.6 mm silicone wires side by side fit)
SCREW_X = TIP_D / 2 - 1.2                 # local x offset of the screw axis from the tip centre, in the 2.45 mm wall between the bore and the outer edge
# Wire cover (owner, 2026-11-17, docs/strut-cover.md): the inboard SKIN_T of each arm's 3 mm plate is a separate SKIN (the plate keeps its 3 mm and its faces; the base is 3 - SKIN_T thick),
# the wire channel is cut in the base's face under the skin, and a flat CAP on the tip collar closes the tube end flush with the collar's outline.  M1.6 screws and a cord gasket in a groove keep both
# serviceable.  The skin starts SKIN_R0 from the pivot (clear of the pivot boss) and ends at the tip collar; inside SKIN_R0 strut B's channel is open on its inboard face, under strut A's boss (1 mm gap).
# Not inside the 1.0 mm gap between A and B: an added skin there would hit strut A (found 2026-11-17).
COVER = True
SKIN_T, CAP_T2, SKIN_R0 = 1.2, 1.2, 15.5
CH_W, CH_D = 3.0, 1.0                      # wire channel in the plate's inboard face (3.0 wide leaves room for a flat PCB rail later; two 0.6 mm wires need 1.2)
CH_END = STRUT_L - TIP_D / 2 + 2.3         # the channel ends where the tube wall's slot begins, 0.15 mm short of the plate bore (x = 60.3)
SK_SCREW_X = (20.0, 28.5, 37.0, 45.5, 54.0)
SK_SCREW_EDGE = 2.6                        # screw axis this far inside the arm's edge
CAP_SCREW_R, CAP_SCREW_DEG = 10.8, (135.0, 225.0, 270.0)
SCREW_CB_D, SCREW_CB_H, SCREW_HOLE_D, TAP_D, TAP_DEPTH = 3.2, 0.9, 1.8, 1.35, 1.4
GROOVE_W, GROOVE_D, GROOVE_Y = 0.65, 0.40, 2.4   # cord groove beside the channel: its inner edge at GROOVE_Y from the centre line
COUPLER_D, COUPLER_L = 8.0, 7.5        # ASSUMED small flexible 3 mm coupling, 0.5 mm from the motor's front face and 0.5 mm short of the cap (tight: real couplings are usually longer)
# Each strut's support starts flush with the inboard face of ITS OWN plate (A: 77.25, B: 81.25), so nothing sticks out behind the plate.
# --------------------------------------------

X0 = E.SPOT_OUT + E.HUB_FLANGE_T                # outer face of the stud flange, |x|
A_BOSS = (X0 + GAP, X0 + GAP + BOSS_T)          # inboard strut boss, |x| range
B_BOSS = (A_BOSS[1] + GAP, A_BOSS[1] + GAP + BOSS_T)
A_PLATE = (A_BOSS[1] - PLATE_T, A_BOSS[1])      # plate flush with the outer face of boss A
B_PLATE = (B_BOSS[0], B_BOSS[0] + PLATE_T)      # plate flush with the inner face of boss B
WHEEL_X = (B_PLATE[1] + 1.0, B_PLATE[1] + 1.0 + WHEEL_W)
MOTOR_TAIL = A_PLATE[0]                          # |x| of the motor's tail: the inboard face of strut A's plate (both struts' motors share this x range)
MOTOR_FRONT = MOTOR_TAIL + MOTOR_L


def plate_outline(r1, r2, d):
    """Convex hull of a circle r1 at the origin and a circle r2 at (d, 0), as a sketch in the local XY plane."""
    phi = math.asin((r1 - r2) / d)
    pts = [(r1 * math.sin(phi), r1 * math.cos(phi)), (d + r2 * math.sin(phi), r2 * math.cos(phi)),
           (d + r2 * math.sin(phi), -r2 * math.cos(phi)), (r1 * math.sin(phi), -r1 * math.cos(phi))]
    with BuildSketch() as sk:
        Polygon(*pts, align=None)
        Circle(r1)
        with Locations((d, 0)):
            Circle(r2)
    return sk.sketch


def isogrid_pockets():
    """Triangular pockets in the local frame (x along the arm, y across, z from the plate's inboard face outward), or None if ISOGRID is off."""
    if not ISOGRID:
        return None
    a = ISO_CELL
    h = a * math.sqrt(3) / 2
    rho = a / (2 * math.sqrt(3))
    shrink = (rho - ISO_RIB / 2) / rho
    r1, r2 = BOSS_D / 2, TIP_D / 2
    tris = []
    for j in range(-4, 4):
        for i in range(-2, int(STRUT_L / a) + 3):
            x0 = i * a + j * a / 2
            y0 = j * h
            tris.append([(x0, y0), (x0 + a, y0), (x0 + a / 2, y0 + h)])               # up
            tris.append([(x0 + a, y0), (x0 + a / 2, y0 + h), (x0 + 3 * a / 2, y0 + h)])   # down
    keep = []
    for t in tris:
        cx = sum(p[0] for p in t) / 3
        cy = sum(p[1] for p in t) / 3
        pts = [(cx + (px - cx) * shrink, cy + (py - cy) * shrink) for px, py in t]
        ok = True
        for px, py in pts:
            hw = r1 + (r2 - r1) * px / STRUT_L - ISO_BORDER                      # half width of the plate at x (approximate taper), less the border
            if not (0 < px < STRUT_L) or abs(py) > hw:
                ok = False
            if math.hypot(px, py) < r1 + ISO_BORDER or math.hypot(px - STRUT_L, py) < r2 + ISO_BORDER:
                ok = False
        if ok:
            keep.append(pts)
    solids = [extrude(Face(Wire.make_polygon([Vector(x, y, 0) for x, y in pts], close=True)), amount=ISO_DEPTH) for pts in keep]
    return Compound(solids) if solids else None


def on_axle(shape, x0):
    """Local frame (x along the arm, y up, z along the axle) -> world: arm toward +y, axle along +x at |x| = x0."""
    return shape.moved(Plane.YZ.offset(x0).location)


def _half_width(x):
    """Half the arm's width at x along it (the hull's straight edge)."""
    return BOSS_D / 2 + (TIP_D / 2 - BOSS_D / 2) * x / STRUT_L


def _place(shape, plate_range, direction):
    """Local strut frame (x along the arm, z from the plate's inboard face outward) -> world, as strut() does at its end."""
    s = on_axle(shape, plate_range[0]).moved(Location((0, 0, E.HUB_Z)))
    if direction < 0:
        s = s.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), 180)
    return s


def _skin_shape():
    """The skin's volume in the local frame: the arm outline between SKIN_R0 and the tip collar, z from 0 (the plate's inboard face) to SKIN_T, with the screw holes and counterbores."""
    sk = extrude(plate_outline(BOSS_D / 2, TIP_D / 2, STRUT_L), amount=SKIN_T)
    sk = sk - Cylinder(SKIN_R0, 10, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    sk = sk - Cylinder(TIP_D / 2 + 0.2, 10, align=(Align.CENTER, Align.CENTER, Align.CENTER)).moved(Location((STRUT_L, 0, 0)))
    return sk


def skin(plate_range, direction):
    """The skin (the part): _skin_shape() with the screw clearance holes and counterbores (from the inboard face)."""
    sk = _skin_shape()
    for xs in SK_SCREW_X:
        for sy in (1, -1):
            ys = sy * (_half_width(xs) - SK_SCREW_EDGE)
            sk = sk - Cylinder(SCREW_HOLE_D / 2, SKIN_T + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((xs, ys, -0.01)))
            sk = sk - Cylinder(SCREW_CB_D / 2, SCREW_CB_H + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((xs, ys, -0.01)))
    return _place(sk, plate_range, direction)


def cap(plate_range, direction):
    """The cap: a 24 mm disc, CAP_T2 thick, on the tip collar's inboard end face (z from -COLLAR_IN - CAP_T2 to -COLLAR_IN), so the collar's outline carries on flush and the tube end is closed."""
    c = Cylinder(TIP_D / 2, CAP_T2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((STRUT_L, 0, -COLLAR_IN - CAP_T2)))
    for deg in CAP_SCREW_DEG:
        cx, cy = STRUT_L + CAP_SCREW_R * math.cos(math.radians(deg)), CAP_SCREW_R * math.sin(math.radians(deg))
        c = c - Cylinder(SCREW_HOLE_D / 2, CAP_T2 + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((cx, cy, -COLLAR_IN - CAP_T2 - 0.01)))
        c = c - Cylinder(SCREW_CB_D / 2, SCREW_CB_H + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((cx, cy, -COLLAR_IN - CAP_T2 - 0.01)))
    return _place(c, plate_range, direction)


def cover_screws(plate_range, direction):
    """M1.6 pan-head screws (head 3.0 x 0.8, shank 1.6 x 1.7), a Compound of separate solids: ten for the skin, three for the cap."""
    out = []
    def one(x, y, z_face, depth):                 # head under the face by 0.1, shank into the tapped hole
        h = Cylinder(1.5, 0.8, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((x, y, z_face + 0.1)))
        sh = Cylinder(0.8, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((x, y, z_face + 0.9)))
        return h + sh
    for xs in SK_SCREW_X:
        for sy in (1, -1):
            out.append(_place(one(xs, sy * (_half_width(xs) - SK_SCREW_EDGE), 0.0, 0), plate_range, direction))
    for deg in CAP_SCREW_DEG:
        cx, cy = STRUT_L + CAP_SCREW_R * math.cos(math.radians(deg)), CAP_SCREW_R * math.sin(math.radians(deg))
        out.append(_place(one(cx, cy, -COLLAR_IN - CAP_T2, 0), plate_range, direction))
    return Compound(out)


def strut(boss_range, plate_range, wheel_inner, direction):
    """One strut at the pivot (y = 0, z = HUB_Z), arm along +y (direction = +1) or -y (-1), horizontal."""
    t_plate = plate_range[1] - plate_range[0]
    boss = Cylinder(BOSS_D / 2, boss_range[1] - boss_range[0], align=(Align.CENTER, Align.CENTER, Align.MIN))
    boss = on_axle(boss, boss_range[0])
    arm = extrude(plate_outline(BOSS_D / 2, TIP_D / 2, STRUT_L), amount=t_plate)
    pockets = isogrid_pockets()
    if pockets is not None:
        arm = arm - pockets          # pockets start at z = 0 on the plate's inboard face (local frame, before on_axle)
    arm = on_axle(arm, plate_range[0])
    s = boss + arm
    if TIP_MODE != "axle":
        collar = Cylinder(TIP_D / 2, COLLAR_IN, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((STRUT_L, 0, 0)))
        s = s + on_axle(collar, plate_range[0] - COLLAR_IN)
    if TIP_MODE == "axle":
        tip_axle = Cylinder(AXLE_D / 2, WHEEL_X[1] + COLLAR_L - plate_range[1], align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((STRUT_L, 0, 0)))
        s = s + on_axle(tip_axle, plate_range[1])
    else:   # a round bore through the tip boss and plate for the spindle tube (0.05 mm radial clearance, filled with thermal paste or adhesive)
        bore = Cylinder((SPINDLE_OD + 0.1) / 2, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((STRUT_L, 0, 0)))
        s = s - on_axle(bore, plate_range[0] - 5)
    if TIP_MODE != "axle":   # the clamp slit (from the bore through the tip's outer wall along +x) and the M2 screw across it
        zlen = t_plate + COLLAR_IN + 2.0
        slit = Box(TIP_D / 2 + 1.0, SLIT_W, zlen, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((STRUT_L + 0.5, 0, 0)))
        s = s - on_axle(slit, plate_range[0] - COLLAR_IN - 1.0)
        zc = (t_plate - COLLAR_IN) / 2.0                                            # the middle of the plate plus collar, local z from -COLLAR_IN to t_plate
        hole = Cylinder(1.0, TIP_D, align=(Align.CENTER, Align.CENTER, Align.CENTER)).rotate(Axis.X, 90)
        cbore = Cylinder(1.95, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN)).rotate(Axis.X, -90).moved(Location((0, 2.7, 0)))
        s = s - on_axle((hole + cbore).moved(Location((STRUT_L + SCREW_X, 0, zc))), plate_range[0])
    if TIP_MODE != "axle":   # the motor's wires (docs/mechanical-spec.md item 6): a notch through the collar's pivot side lets them out of the tube's tail; strut B (the outer strut) also gets a groove
        # on its plate's inboard face, all the way across its boss to the bore, where the hub's hollow shaft takes the wires in through a cross hole (hub.py, X_WIRE_B); strut A's wires run free in the channel between its plate and the body wall
        if not COVER:
            notch = Box(3.8, WIRE_W, COLLAR_IN + 0.1, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((STRUT_L - TIP_D / 2 - 0.5, 0, 0)))
            s = s - on_axle(notch, plate_range[0] - COLLAR_IN - 0.1)
            if boss_range == B_BOSS:
                groove = Box(STRUT_L - TIP_D / 2 + 0.5, WIRE_W, WIRE_DEPTH, align=(Align.MIN, Align.CENTER, Align.MIN))
                s = s - on_axle(groove, plate_range[0] - 0.01)
        else:
            s = s - on_axle(_skin_shape(), plate_range[0])            # the skin's layer is removed from the base (the skin is a separate part)
            x_start = 0.0 if boss_range == B_BOSS else SKIN_R0       # B's channel crosses its boss to the hub bore (open on the inboard face there, under strut A's boss); A's starts at the skin
            ch = Box(CH_END - x_start, CH_W, CH_D + 0.01, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((x_start, 0, SKIN_T - 0.01)))
            s = s - on_axle(ch, plate_range[0])
            if boss_range == B_BOSS:
                s = s - on_axle(Box(SKIN_R0 + 0.1, CH_W, SKIN_T + 0.02, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((0, 0, -0.01))), plate_range[0])
            for sy in (1, -1):                                         # the cord groove: two arms beside the channel, ending at the collar and open at the pivot end (the wires go on to the hub there)
                g = Box(STRUT_L - TIP_D / 2 - 1.0 - SKIN_R0 - 1.0, GROOVE_W, GROOVE_D + 0.01, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(
                    Location((SKIN_R0 + 1.0, sy * (GROOVE_Y + GROOVE_W / 2), SKIN_T - 0.01)))
                s = s - on_axle(g, plate_range[0])
            for xs in SK_SCREW_X:                                      # tapped holes for the skin screws (blind, from the base's face)
                for sy in (1, -1):
                    ys = sy * (_half_width(xs) - SK_SCREW_EDGE)
                    s = s - on_axle(Cylinder(TAP_D / 2, TAP_DEPTH + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((xs, ys, SKIN_T - 0.01))), plate_range[0])
            for deg in CAP_SCREW_DEG:                                  # tapped holes in the collar's end face for the cap screws
                cx, cy = STRUT_L + CAP_SCREW_R * math.cos(math.radians(deg)), CAP_SCREW_R * math.sin(math.radians(deg))
                s = s - on_axle(Cylinder(TAP_D / 2, 2.2 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((cx, cy, -COLLAR_IN - 0.01))), plate_range[0])
    bore_d = BORE_D if HUB_MODE == "stud" else (15.05 if boss_range == A_BOSS else 5.05)
    s = s - on_axle(Cylinder(bore_d / 2, 20, align=(Align.CENTER, Align.CENTER, Align.MIN)), boss_range[0] - 1)
    s = s.moved(Location((0, 0, E.HUB_Z)))
    if direction < 0:
        s = s.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), 180)
    return s


def wheel_envelope(direction):
    w = Cylinder(WHEEL_D / 2, WHEEL_W, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((STRUT_L, 0, 0)))
    w = on_axle(w, WHEEL_X[0]).moved(Location((0, 0, E.HUB_Z)))
    if direction < 0:
        w = w.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), 180)
    return w


def _at_tip(shape_local_z, direction):
    """Place a part built along the wheel axis (local z = |x|) at the strut tip, arm along +y (direction +1) or -y (-1), horizontal."""
    m = shape_local_z.moved(Location((0, 0, E.HUB_Z)))
    if direction < 0:
        m = m.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), 180)
    return m


def _cyl(r_out, r_in, x0, x1):
    """Tube or rod along the wheel axis at the strut tip from |x| = x0 to x1 (local frame before on_axle)."""
    c = Cylinder(r_out, x1 - x0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if r_in:
        c = c - Cylinder(r_in, x1 - x0 + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -1)))
    return on_axle(c.moved(Location((STRUT_L, 0, 0))), x0)


def tail_for(direction):
    """|x| of the support's tail: the inboard face of the strut's own plate (the +y strut is A, the -y strut is B)."""
    return A_PLATE[0] if direction > 0 else B_PLATE[0]


def spindle(direction, tail=None):
    """Spindle tube, end cap and bearing barrel (one aluminium part): tube OD 19 / ID 16.2 from the strut plate's inboard face to the cap, then the 11 mm barrel with an 8 mm bearing bore."""
    tail = tail_for(direction) - COLLAR_IN if tail is None else tail
    tube = _cyl(SPINDLE_OD / 2, SPINDLE_ID / 2, tail, TUBE_END - CAP_T)
    endcap = _cyl(SPINDLE_OD / 2, 2.5, TUBE_END - CAP_T, TUBE_END)                 # end wall with a 5 mm hole for the shaft
    barrel = _cyl(BARREL_OD / 2, BRG_OD / 2, TUBE_END, BARREL_END)
    body = tube + endcap + barrel
    if COVER:       # a 1.5 mm slot through the tube wall on the pivot side at the channel's depth (SKIN_T to SKIN_T + CH_D from the plate's inboard face): the leads run forward along the motor's pivot-side flat and leave the tube here into the channel
        t0 = tail_for(direction)
        slot = Box(3.0, WIRE_W, CH_D, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((STRUT_L - SPINDLE_OD / 2 - 0.5, 0, 0)))
        body = body - on_axle(slot, t0 + SKIN_T)
    return _at_tip(body, direction)


def bearings(direction):
    """Two 3 x 8 x 4 mm ball bearings (as rings) in the barrel."""
    rings = [_cyl(BRG_OD / 2, BRG_ID / 2, x, x + BRG_W) for x in BRG_X]
    return _at_tip(Compound(rings), direction)          # a Compound, not a union: the two bearings touch and must stay separate parts


def motor(direction, tail=None):
    """Wheel drive at the strut tip: the 10 x 12 x 25 mm gearmotor box (tail flush with the strut plate's inboard face), the coupling, and the 3 mm stub shaft to the wheel's collar."""
    tail = tail_for(direction) if tail is None else tail
    front = tail + MOTOR_L
    box = Box(MOTOR_H, MOTOR_W, MOTOR_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((STRUT_L, 0, 0)))
    box = on_axle(box, tail)
    coupler = _cyl(COUPLER_D / 2, 0, front + 0.5, front + 0.5 + COUPLER_L)
    shaft = _cyl(SHAFT_D / 2, 0, front, WHEEL_X[1] + COLLAR_L - 1.0)
    return _at_tip(box + coupler + shaft, direction)


def posed(shape, direction, deg):
    """Rotate about the hub axis so the arm points `deg` below horizontal."""
    return shape.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), -deg if direction > 0 else deg)


def main():
    OUT.mkdir(exist_ok=True)
    struts, wheels, motors, spindles, brgs = [], [], [], [], []
    covers, screws = [], []
    for side in (1, -1):
        for (bossr, platr, d) in ((A_BOSS, A_PLATE, +1), (B_BOSS, B_PLATE, -1)):
            s = posed(strut(bossr, platr, WHEEL_X[0], d), d, POSE_DEG)
            w = posed(wheel_envelope(d), d, POSE_DEG)
            parts = [posed(f(d), d, POSE_DEG) for f in (motor, spindle, bearings)] if TIP_MODE == "motor" else None
            if side < 0:
                s, w = s.mirror(Plane.YZ), w.mirror(Plane.YZ)
                parts = [q.mirror(Plane.YZ) for q in parts] if parts else None
            if COVER and TIP_MODE == "motor":
                cv = [posed(skin(platr, d), d, POSE_DEG), posed(cap(platr, d), d, POSE_DEG)]
                sc = posed(cover_screws(platr, d), d, POSE_DEG)
                if side < 0:
                    cv, sc = [q.mirror(Plane.YZ) for q in cv], sc.mirror(Plane.YZ)
                covers.extend(cv)
                screws.append(sc)
            struts.append(s)
            wheels.append(w)
            if parts:
                motors.append(parts[0])
                spindles.append(parts[1])
                brgs.append(parts[2])
    S, W = Compound(struts), Compound(wheels)

    # ---- checks ----
    s0 = strut(A_BOSS, A_PLATE, WHEEL_X[0], +1)
    print(f"strut pivot-to-axle   {STRUT_L:.2f} mm (by construction); boss {BOSS_D} x {BOSS_T}, plate {PLATE_T} mm, tip boss {TIP_D} mm")
    print(f"layers (|x|)          flange face {X0:.2f}; boss A {A_BOSS[0]:.2f}-{A_BOSS[1]:.2f}; boss B {B_BOSS[0]:.2f}-{B_BOSS[1]:.2f}; "
          f"plate A {A_PLATE[0]:.2f}-{A_PLATE[1]:.2f}; plate B {B_PLATE[0]:.2f}-{B_PLATE[1]:.2f}; wheels {WHEEL_X[0]:.2f}-{WHEEL_X[1]:.2f}")
    if HUB_MODE == "stud":
        print(f"stud axle stub ends at |x| = {X0 + E.HUB_AXLE_L:.2f}; {X0 + E.HUB_AXLE_L - B_BOSS[1]:.2f} mm left for a retainer")
    else:
        print(f"hub mode coaxial: strut A on the 15 mm hollow shaft (bore 15.05), strut B on the 5 mm inner shaft (bore 5.05), see hardware/hub/hub.py")
    one_mass = lambda s: s.volume * 2.70e-3
    print(f"strut mass            about {one_mass(s0):.0f} g each (6061 estimate), {sum(one_mass(x) for x in struts):.0f} g for four")

    # interference of every strut with the stud/axle, the body and each other, over relative angles
    if HUB_MODE == "stud":
        stud_hubs = import_step(BODY_OUT / "hub_studs.step")
    else:      # the coaxial hub's parts that reach the struts (run hardware/hub/hub.py first)
        hub_parts = [import_step(HW_HUB / f"{n}.step") for n in ("hub_housing", "hub_shafts", "hub_bearings", "hub_gears") if (HW_HUB / f"{n}.step").exists()]
        stud_hubs = Compound(hub_parts) if hub_parts else import_step(BODY_OUT / "hub_studs.step")
    body = import_step(BODY_OUT / "body_hammond.step")
    bad = {}
    sa0 = strut(A_BOSS, A_PLATE, WHEEL_X[0], +1)
    sb0 = strut(B_BOSS, B_PLATE, WHEEL_X[0], +1)
    if TIP_MODE == "motor":      # the motor is carried by its own strut; the other strut must clear it too
        m0 = motor(+1)
        sa0, sb0 = sa0 + m0, sb0 + m0
        if COVER:      # the skins sit inside the plate's envelope; the caps stand 1.2 mm inboard of each tip collar
            sa0, sb0 = sa0 + skin(A_PLATE, +1) + cap(A_PLATE, +1), sb0 + skin(B_PLATE, +1) + cap(B_PLATE, +1)
    axis = Axis((0, 0, E.HUB_Z), (1, 0, 0))
    STEP_DEG = 30
    angles = range(0, 360, STEP_DEG)
    sa_rot = {a: sa0.rotate(axis, a) for a in angles}
    sb_rot = {b: sb0.rotate(axis, b) for b in angles}
    for a in angles:
        for b in angles:
            hit = sa_rot[a] & sb_rot[b]
            if hit and hit.volume > 1e-3:
                bad[(a, b)] = hit.volume
    print(f"strut A vs strut B    {'(with the wheel motors) ' if TIP_MODE == 'motor' else '(axle stubs) '}interference at {len(bad)} of {len(angles)**2} angle pairs ({STEP_DEG} degree steps); layers are {GAP:.1f} mm apart")
    for nm, shp in (("stud (incl. axle stub)", stud_hubs), ("body", body)):
        hit = Compound(struts) & shp
        print(f"struts vs {nm:<22} overlap {hit.volume if hit else 0.0:.2f} mm3 (default pose)")
    # wheels vs everything at the default pose
    for nm, shp in (("body", body), ("stud", stud_hubs), ("struts", S)):
        hit = W & shp
        print(f"wheel envelopes vs {nm:<7} overlap {hit.volume if hit else 0.0:.2f} mm3 (default pose)")
    wh = {}
    for i, w in enumerate(wheels):
        bb = w.bounding_box()
        wh[i] = (bb.min.Z, bb.max.Z, bb.min.Y, bb.max.Y, bb.min.X, bb.max.X)
    zmin = min(v[0] for v in wh.values())
    print(f"default stance ({POSE_DEG:.0f} deg below horizontal): wheel bottoms at z = {zmin:.1f}, so the body floor is {-zmin:.1f} mm above the ground; "
          f"axle spacing {2 * STRUT_L * math.cos(math.radians(POSE_DEG)):.1f} mm; overall length {max(v[3] for v in wh.values()) - min(v[2] for v in wh.values()):.1f} mm; "
          f"overall width {max(v[5] for v in wh.values()) - min(v[4] for v in wh.values()):.1f} mm")
    flat = 2 * (STRUT_L + WHEEL_D / 2)
    print(f"struts horizontal (0 deg): overall length {flat:.1f} mm  (JPL's caption: prototype 'only 20cm long')")
    if motors:
        M, SP = Compound(motors), Compound(spindles)
        BR = Compound([b for g in brgs for b in g.solids()])     # flattened: a compound of compounds reports zero volume
        for nm, shp in (("body", body), ("stud", stud_hubs), ("struts", S)):
            for lab, grp in (("motor drive", M), ("spindle", SP), ("bearings", BR)):
                hit = grp & shp
                v = hit.volume if hit else 0.0
                if v > 1e-3 or lab == "motor drive":
                    print(f"{lab:<12} vs {nm:<7} overlap {v:.2f} mm3 (default pose)")
        for lab, a_, b_ in (("motor drive vs spindle", M, SP), ("bearings vs spindle", BR, SP), ("bearings vs motor drive", BR, M)):
            hit = a_ & b_
            print(f"{lab:<24} overlap {hit.volume if hit else 0.0:.2f} mm3")
        print(f"wheel motor           {MOTOR_W:.0f} x {MOTOR_H:.0f} x {MOTOR_L:.0f} mm (Pololu #3068), {MOTOR_G} g each; |x| tail {A_PLATE[0]:.2f} (strut A) and {B_PLATE[0]:.2f} (strut B), "
              f"flush with each strut plate's inboard face; strut A's tail is {A_PLATE[0] - 69.94:+.2f} mm from the body face")
        print(f"spindle tube          OD {SPINDLE_OD} / ID {SPINDLE_ID} mm from the plate's inboard face to the cap at {TUBE_END}, barrel to {BARREL_END}; "
              f"bearings 3 x 8 x 4 at |x| {BRG_X[0]:.2f} and {BRG_X[1]:.2f}; stub shaft {SHAFT_D} mm to {WHEEL_X[1] + COLLAR_L - 1.0:.2f}; "
              f"spindle mass {spindles[0].volume * 2.70e-3:.1f} g (A) and {spindles[1].volume * 2.70e-3:.1f} g (B), 6061")
        for nm, grp in (("wheel_motors.step", M), ("wheel_spindles.step", SP), ("wheel_bearings.step", BR)):
            export_step(grp, str(OUT / nm))
            chk = import_step(OUT / nm)
            print(f"re-imported {nm}: {len(chk.solids())} solids, volume {chk.volume / 1000:.2f} cm3 (live {grp.volume / 1000:.2f})")

    if covers:
        C = Compound(covers)
        CS = Compound([x for g in screws for x in g.solids()])
        print(f"cover (skin {SKIN_T} mm and tip cap {CAP_T2} mm): {len(covers)} parts, {C.volume * 2.70e-3:.1f} g in 6061; {len(CS.solids())} M1.6 screws, about {len(CS.solids()) * 0.12:.0f} g")
        for lab, shp in (("struts", S), ("motor drive", Compound(motors)), ("spindles", Compound(spindles)),
                         ("bearings", Compound([b for g in brgs for b in g.solids()])), ("wheels", W), ("body", body), ("hub parts", stud_hubs)):
            for nm, grp in (("cover parts", C), ("cover screws", CS)):
                hit = grp & shp
                v = hit.volume if hit else 0.0
                print(f"{nm:<12} vs {lab:<11} overlap {v:.3f} mm3 (default pose)")
        for nm, grp in (("strut_covers.step", C), ("strut_cover_screws.step", CS)):
            export_step(grp, str(OUT / nm))
            chk = import_step(OUT / nm)
            print(f"re-imported {nm}: {len(chk.solids())} solids, volume {chk.volume / 1000:.3f} cm3 (live {grp.volume / 1000:.3f})")

    export_step(S, str(OUT / "struts.step"))
    print("wrote", OUT / "struts.step")


if __name__ == "__main__":
    main()
