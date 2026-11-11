#!/usr/bin/env python3
"""Coaxial strut hub: two Feetech STS3215 servos per side drive the two struts through concentric shafts.

Run after hardware/body/body.py (it needs body_hammond.step to check the interior):
    .venv/bin/python hardware/hub/hub.py        writes hardware/hub/out/*.step

Layout (hub axis along x, at |x| = SPOT_OUT = 69.25 on each side, z = HUB_Z; this is the +x side, the -x side is a mirror image):
  * Strut B (outermost) is on a 5 mm steel INNER SHAFT, driven directly by servo B, whose output is on the hub axis (a horn adapter joins them).
  * Strut A (inboard layer) is on a 15 / 11 mm aluminium HOLLOW SHAFT around the inner shaft, driven by servo A through a 1:1 spur pair (centre distance 22 mm):
    a pinion on servo A's output and a gear on the hollow shaft.
  * A stationary HOUSING (flange 28 mm on the wall's outer spot-face, tube 24 mm through an opened 24.2 mm wall hole) carries two 6702-size thin bearings
    (15 x 21 x 4 mm) for the hollow shaft; two 685-size bearings (5 x 11 x 5 mm) run between the inner shaft and the hollow shaft.
  * The struts' pivot bores become 15.05 mm (strut A, on the hollow shaft) and 5.05 mm (strut B, on the inner shaft): see strut.py, HUB_MODE "coaxial".

Where the numbers come from
  * STS3215: Feetech product specification, STS3215 A/0 2020-04-10 (core-electronics.com.au copy), page 6 drawing and page 4: body 45.23 x 24.73 mm, 55 +- 1 g,
    32 mm body height along the shaft (35 mm with the ears), a 25-tooth spline output with a 3.4 mm boss on the output face and a 4.1 mm boss on the back (the shaft
    comes out of both faces), shaft about 10.7 mm from one end of the long side (READ BY EYE from the drawing's scale, plus or minus 1 mm), page 7 horn 19.95 mm, 4 x M3.
  * Everything else is a design choice of mine: shaft and bearing sizes (typical catalogue sizes, mass and rating not looked up), gear size, positions.
NOT modelled: gear teeth (the gears are plain discs at the pitch diameter + 2 mm), the servo mounting, wire routing, the housing's retention and seals, the
shaft retainers and set screws, the servo's cable, the strut stops.  Printed or aluminium gears: see docs/drivetrain-spec.md for the tooth stress.
"""
import math
import sys
from pathlib import Path
from build123d import *

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "strut"))
import body as E  # noqa: E402
import strut as S  # noqa: E402

OUT = HERE / "out"
BODY_OUT = HERE.parent / "body" / "out"

# ---------------- PARAMETERS ----------------
HZ = E.HUB_Z
# servo STS3215
SV_L, SV_W, SV_H = 45.23, 24.73, 32.0        # long side (along y), width (along z), body height along the hub axis (x)
SV_SHAFT_END = 10.7                          # shaft to the near end of the long side (read from the drawing by eye)
SV_BOSS_D, SV_BOSS_H = 9.0, 3.4              # output boss on the front face
SV_G = 55.0
# shafts and bearings
INNER_D = 5.0                                # strut B shaft (steel)
HOLLOW_OD, HOLLOW_ID = 15.0, 11.0            # strut A shaft (6061)
BRG_IN = dict(id=5.0, od=11.0, w=5.0)        # 685 size, between the shafts
BRG_OUT = dict(id=15.0, od=21.0, w=4.0)      # 6702 size (thin series), in the housing
HOUSE_FLANGE_D, HOUSE_BORE, HOUSE_OD = 28.0, 21.0, 24.0
WALL_HOLE_D = 24.2                           # the wall hole opened for the housing tube (was a 12.6 mm double-D hole for the stud)
# gears
CD = 23.0                                    # centre distance, servo A shaft to the hub axis (1:1); leaves 1.6 mm between the two servo bodies
GEAR_OD, GEAR_W = CD, 6.0                    # plain discs at the pitch circle (module 1, 23 teeth); the teeth would add 2 mm of tip diameter and mesh across the contact
# x positions (|x|, mm) -- the struts' layers come from strut.py: A boss 73.25-80.25, B boss 81.25-88.25
X_WALL_OUT = E.SPOT_OUT                      # outer plane of the wall at the hub, 69.25
X_FLANGE = (X_WALL_OUT, S.X0)                # housing flange 69.25 to 72.25
X_HOUSE_IN = 60.25                           # inboard end of the housing tube
X_BRG_OUT = ((68.25, 72.25), (61.25, 65.25)) # the two housing bearings
X_GEAR = (53.0, 53.0 + GEAR_W)               # gear A and pinion A plane: 0.1 mm clear of servo A's 3.4 mm output boss (49.5 to 52.9)
X_HOLLOW = (X_GEAR[0], S.A_BOSS[1])          # hollow shaft: from the gear plane to the end of strut A's boss
X_BRG_IN = ((74.25, 79.25), (54.0, 59.0))    # inner bearings, between the shafts
SERVO_B_FACE = 45.0                          # output face of servo B (body behind it, x 13 to 45, boss to 48.4)
SERVO_A_FACE = 49.5                          # output face of servo A (body x 17.5 to 49.5, boss to 52.9)
B_ADAPTER = (48.5, 51.5)                     # flange on servo B's horn, 20 mm x 3 mm, then the shaft (0.1 mm clear of the boss)
INNER_X = (B_ADAPTER[1], S.B_BOSS[1] + 4.0)  # inner shaft: from the adapter to 4 mm beyond strut B's boss (retainer room)
# --------------------------------------------


def cylx(r_out, r_in, x0, x1, y=0.0, dz=0.0):
    """Tube or rod along the hub axis from |x| = x0 to x1, centred at world y, z = HZ + dz (one side, +x)."""
    c = Cylinder(r_out, x1 - x0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if r_in:
        c = c - Cylinder(r_in, x1 - x0 + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -1)))
    c = c.moved(Location((y, dz, 0)))
    return S.on_axle(c, x0).moved(Location((0, 0, HZ)))


def servo(y_shaft, long_dir, x_face):
    """STS3215 envelope: a box 45.23 x 24.73 x 32 mm with the shaft at y_shaft, the long side toward long_dir (+1 or -1), its output face at |x| = x_face,
    plus the 9 mm x 3.4 mm output boss and the 4 mm boss on the back."""
    y0 = y_shaft - SV_SHAFT_END if long_dir > 0 else y_shaft - (SV_L - SV_SHAFT_END)
    box = Box(SV_L, SV_W, SV_H, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((y0, 0, 0)))
    body = S.on_axle(box, x_face - SV_H).moved(Location((0, 0, HZ)))
    front = cylx(SV_BOSS_D / 2, 0, x_face, x_face + SV_BOSS_H, y=y_shaft)
    back = cylx(SV_BOSS_D / 2, 0, x_face - SV_H - 4.1, x_face - SV_H, y=y_shaft)
    return body + front + back


def build_side():
    """All hub parts for the +x side, as a dict of name -> shape."""
    parts = {}
    # housing: flange + tube, bored 21 mm for the two 6702 bearings
    flange = cylx(HOUSE_FLANGE_D / 2, HOUSE_BORE / 2, *X_FLANGE)
    tube = cylx(HOUSE_OD / 2, HOUSE_BORE / 2, X_HOUSE_IN, X_FLANGE[0])
    parts["housing"] = flange + tube
    # hollow shaft A and its gear
    parts["hollow"] = cylx(HOLLOW_OD / 2, HOLLOW_ID / 2, *X_HOLLOW)
    parts["gear_a"] = cylx(GEAR_OD / 2, HOLLOW_OD / 2, *X_GEAR)
    # inner shaft B with the horn adapter
    parts["inner"] = cylx(INNER_D / 2, 0, *INNER_X)
    parts["adapter"] = cylx(20.0 / 2, INNER_D / 2, *B_ADAPTER)
    # bearings (as rings): two outer, two inner
    parts["bearings_out"] = Compound([cylx(BRG_OUT["od"] / 2, BRG_OUT["id"] / 2, x0, x1) for x0, x1 in X_BRG_OUT])
    parts["bearings_in"] = Compound([cylx(BRG_IN["od"] / 2, BRG_IN["id"] / 2, x0, x1) for x0, x1 in X_BRG_IN])
    # servos: B on the axis (long side toward +y), A offset by CD toward -y with its long side toward -y; A's pinion on its output
    parts["servo_b"] = servo(0.0, +1, SERVO_B_FACE)
    parts["servo_a"] = servo(-CD, -1, SERVO_A_FACE)
    parts["pinion_a"] = cylx(GEAR_OD / 2, 3.0, *X_GEAR, y=-CD)
    return parts


def mirrored(shape):
    return shape.mirror(Plane.YZ)


def main():
    OUT.mkdir(exist_ok=True)
    side = build_side()
    groups = {"hub_housing": ["housing"], "hub_shafts": ["hollow", "inner", "adapter"], "hub_bearings": ["bearings_out", "bearings_in"],
              "hub_gears": ["gear_a", "pinion_a"], "strut_servos": ["servo_a", "servo_b"]}
    out_shapes = {}
    for g, names in groups.items():
        shapes = []
        for n in names:
            shp = side[n]
            solids = shp.solids() if hasattr(shp, "solids") else [shp]
            shapes += [s for s in solids]
            shapes += [mirrored(s) for s in solids]
        out_shapes[g] = Compound(shapes)

    # ---- checks ----
    print(f"hub axis |x| = {X_WALL_OUT} on both sides, z = {HZ}; the struts' layers: A boss {S.A_BOSS[0]:.2f}-{S.A_BOSS[1]:.2f}, B boss {S.B_BOSS[0]:.2f}-{S.B_BOSS[1]:.2f}")
    print(f"housing               flange {HOUSE_FLANGE_D:.0f} mm at |x| {X_FLANGE[0]:.2f}-{X_FLANGE[1]:.2f}, tube {HOUSE_OD:.0f} mm to {X_HOUSE_IN}, bore {HOUSE_BORE:.0f} mm; wall hole opened to {WALL_HOLE_D} mm")
    print(f"hollow shaft (A)      {HOLLOW_OD:.0f} / {HOLLOW_ID:.0f} mm, |x| {X_HOLLOW[0]:.2f} to {X_HOLLOW[1]:.2f}; inner shaft (B) {INNER_D:.0f} mm, |x| {INNER_X[0]:.2f} to {INNER_X[1]:.2f}")
    print(f"gears                 1:1, centre distance {CD:.0f} mm, plain discs {GEAR_OD:.0f} mm x {GEAR_W:.0f} mm at |x| {X_GEAR[0]:.0f}-{X_GEAR[1]:.0f} (teeth not modelled)")
    for nm, shp in side.items():
        rho = {"housing": 2.70, "hollow": 2.70, "gear_a": 2.70, "pinion_a": 2.70, "inner": 7.85, "adapter": 2.70}.get(nm)
        if rho:
            print(f"  {nm:<14} {shp.volume * rho * 1e-3:6.1f} g each")
    sb = side["servo_b"].bounding_box()
    sa = side["servo_a"].bounding_box()
    print(f"servo B (on axis)     y {sb.min.Y:6.1f} to {sb.max.Y:6.1f}, z {sb.min.Z:5.1f} to {sb.max.Z:5.1f}, |x| {sb.min.X:5.1f} to {sb.max.X:5.1f}")
    print(f"servo A (offset)      y {sa.min.Y:6.1f} to {sa.max.Y:6.1f}, z {sa.min.Z:5.1f} to {sa.max.Z:5.1f}, |x| {sa.min.X:5.1f} to {sa.max.X:5.1f}")

    allside = {k: v for k, v in side.items()}
    names = list(allside)
    bad = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = allside[names[i]], allside[names[j]]
            ba, bb = a.bounding_box(), b.bounding_box()
            if ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z:
                continue
            hit = a & b
            if hit and hit.volume > 0.01:
                bad += 1
                print(f"  OVERLAP {hit.volume:8.2f} mm3: {names[i]} x {names[j]}")
    print(f"hub parts against each other (one side): {bad} overlapping pairs of {len(names) * (len(names) - 1) // 2}")

    # against the struts (bores: 15.05 on the hollow shaft, 5.05 on the inner shaft) and the body with the wall hole opened to 24.2 mm
    S.HUB_MODE = "coaxial"
    sa_ = S.strut(S.A_BOSS, S.A_PLATE, S.WHEEL_X[0], +1)
    sb_ = S.strut(S.B_BOSS, S.B_PLATE, S.WHEEL_X[0], +1)
    for nm in ("hollow", "inner", "housing", "bearings_out", "bearings_in", "adapter"):
        for lab, st in (("strut A", sa_), ("strut B", sb_)):
            hit = side[nm] & st
            if hit and hit.volume > 0.01:
                print(f"  {nm} x {lab}: {hit.volume:.2f} mm3")
    body = import_step(BODY_OUT / "body_hammond.step")
    lid = import_step(BODY_OUT / "lid_plate.step")
    opening = cylx(WALL_HOLE_D / 2, 0, 60.0, 70.0)
    body_open = body - opening
    for nm, shp in side.items():
        for lab, bd in (("body (hub hole opened)", body_open), ("lid plate", lid)):
            hit = shp & bd
            if hit and hit.volume > 0.01:
                print(f"  {nm} x {lab}: {hit.volume:.2f} mm3")
    both_sides = Compound([Compound([side[n], mirrored(side[n])]) for n in ("servo_a", "servo_b")])
    hit = side["servo_b"] & mirrored(side["servo_a"])
    print("servo checks done against the box with the hub hole opened, and the lid plate; the lists above print only overlaps")

    for g, shp in out_shapes.items():
        export_step(shp, str(OUT / f"{g}.step"))
        chk = import_step(OUT / f"{g}.step")
        print(f"re-imported {g}.step: {len(chk.solids())} solids, volume {chk.volume / 1000:.2f} cm3 (live {shp.volume / 1000:.2f})")
    servos_mass = 4 * SV_G
    print(f"servos {servos_mass:.0f} g (4 x {SV_G:.0f}, datasheet); see docs/drivetrain-spec.md for the hub mass")


if __name__ == "__main__":
    main()
