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

# ---------------- PARAMETERS ----------------
STRUT_L = 70.0                 # pivot axis to wheel axle (Wilcox & Jones)
WHEEL_D = 65.0                 # Wilcox & Jones
WHEEL_W = 34.6                 # stack width from the photo (see wheel.py); the papers do not publish it
COLLAR_L = 11.0                # shaft collar on the outside of each wheel (wheel.py)
POSE_DEG = 25.0                # strut angle below horizontal for the default stance (a choice, not sourced)
BOSS_D, BOSS_T = 30.0, 7.0     # pivot boss
TIP_D = 18.0                   # wheel-axle boss
PLATE_T = 3.0                  # arm plate thickness
AXLE_D = 6.0                   # wheel axle stub
BORE_D = 12.1                  # pivot bore on the stud's 12 mm axle
GAP = 1.0                      # washer gap between layers
# --------------------------------------------

X0 = E.SPOT_OUT + E.HUB_FLANGE_T                # outer face of the stud flange, |x|
A_BOSS = (X0 + GAP, X0 + GAP + BOSS_T)          # inboard strut boss, |x| range
B_BOSS = (A_BOSS[1] + GAP, A_BOSS[1] + GAP + BOSS_T)
A_PLATE = (A_BOSS[1] - PLATE_T, A_BOSS[1])      # plate flush with the outer face of boss A
B_PLATE = (B_BOSS[0], B_BOSS[0] + PLATE_T)      # plate flush with the inner face of boss B
WHEEL_X = (B_PLATE[1] + 1.0, B_PLATE[1] + 1.0 + WHEEL_W)


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


def on_axle(shape, x0):
    """Local frame (x along the arm, y up, z along the axle) -> world: arm toward +y, axle along +x at |x| = x0."""
    return shape.moved(Plane.YZ.offset(x0).location)


def strut(boss_range, plate_range, wheel_inner, direction):
    """One strut at the pivot (y = 0, z = HUB_Z), arm along +y (direction = +1) or -y (-1), horizontal."""
    t_plate = plate_range[1] - plate_range[0]
    boss = Cylinder(BOSS_D / 2, boss_range[1] - boss_range[0], align=(Align.CENTER, Align.CENTER, Align.MIN))
    boss = on_axle(boss, boss_range[0])
    arm = extrude(plate_outline(BOSS_D / 2, TIP_D / 2, STRUT_L), amount=t_plate)
    arm = on_axle(arm, plate_range[0])
    tip_axle = Cylinder(AXLE_D / 2, WHEEL_X[1] + COLLAR_L - plate_range[1], align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
        Location((STRUT_L, 0, 0)))
    tip_axle = on_axle(tip_axle, plate_range[1])
    s = boss + arm + tip_axle
    s = s - on_axle(Cylinder(BORE_D / 2, 20, align=(Align.CENTER, Align.CENTER, Align.MIN)), boss_range[0] - 1)
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


def posed(shape, direction, deg):
    """Rotate about the hub axis so the arm points `deg` below horizontal."""
    return shape.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), -deg if direction > 0 else deg)


def main():
    OUT.mkdir(exist_ok=True)
    struts, wheels = [], []
    for side in (1, -1):
        for (bossr, platr, d) in ((A_BOSS, A_PLATE, +1), (B_BOSS, B_PLATE, -1)):
            s = posed(strut(bossr, platr, WHEEL_X[0], d), d, POSE_DEG)
            w = posed(wheel_envelope(d), d, POSE_DEG)
            if side < 0:
                s, w = s.mirror(Plane.YZ), w.mirror(Plane.YZ)
            struts.append(s)
            wheels.append(w)
    S, W = Compound(struts), Compound(wheels)

    # ---- checks ----
    s0 = strut(A_BOSS, A_PLATE, WHEEL_X[0], +1)
    print(f"strut pivot-to-axle   {STRUT_L:.2f} mm (by construction); boss {BOSS_D} x {BOSS_T}, plate {PLATE_T} mm, tip boss {TIP_D} mm")
    print(f"layers (|x|)          flange face {X0:.2f}; boss A {A_BOSS[0]:.2f}-{A_BOSS[1]:.2f}; boss B {B_BOSS[0]:.2f}-{B_BOSS[1]:.2f}; "
          f"plate A {A_PLATE[0]:.2f}-{A_PLATE[1]:.2f}; plate B {B_PLATE[0]:.2f}-{B_PLATE[1]:.2f}; wheels {WHEEL_X[0]:.2f}-{WHEEL_X[1]:.2f}")
    print(f"stud axle stub ends at |x| = {X0 + E.HUB_AXLE_L:.2f}; {X0 + E.HUB_AXLE_L - B_BOSS[1]:.2f} mm left for a retainer")
    one_mass = lambda s: s.volume * 2.70e-3
    print(f"strut mass            about {one_mass(s0):.0f} g each (6061 estimate), {sum(one_mass(x) for x in struts):.0f} g for four")

    # interference of every strut with the stud/axle, the body and each other, over relative angles
    stud_hubs = import_step(BODY_OUT / "hub_studs.step")
    body = import_step(BODY_OUT / "body_hammond.step")
    bad = {}
    sa0 = strut(A_BOSS, A_PLATE, WHEEL_X[0], +1)
    sb0 = strut(B_BOSS, B_PLATE, WHEEL_X[0], +1)
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
    print(f"strut A vs strut B    interference at {len(bad)} of {len(angles)**2} angle pairs ({STEP_DEG} degree steps); layers are {GAP:.1f} mm apart")
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

    export_step(S, str(OUT / "struts.step"))
    print("wrote", OUT / "struts.step")


if __name__ == "__main__":
    main()
