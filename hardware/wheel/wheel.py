#!/usr/bin/env python3
"""Wheels for the rover: a flat outer disk over a stack of eight saw-tooth discs, on a hub core.

Run after hardware/body/body.py and hardware/strut/strut.py:
    .venv/bin/python hardware/wheel/wheel.py        writes hardware/wheel/out/wheels.step

Where the numbers come from (img840-340-hires.original.jpg, the early JPL prototype photographed beside a quarter)
  * The camera was solved from the vanishing points of the solar-cell edges (focal length about 3900 px) and the
    top face was taken as 140 mm square.  Projecting a circle on the wheel axis onto the photo fits the smooth
    outer disk at a radius of 27 mm, the saw-tooth rims at about 29.5 mm (the teeth stand about 2.5 mm proud of
    the disk), a collar centre 5 mm outboard of the disk, and a stack that reaches about 33 to 36 mm inboard of the
    disk.  The same fit puts the saw-tooth discs at 17 teeth (about 21 degrees apart at the disk rim) and eight
    stacked rims along each ridge.
  * The photographed wheel is about 59 mm across the teeth (the sources say "about 6 cm" for the prototype);
    the MUSES-CN papers give 65 mm.  All measured proportions are scaled by 65 / 59 so the tooth diameter is the
    published 65 mm.  K_SCALE is that factor.
  * Disk thickness, tooth shape, disc spacing, the hub core, the collar and the twist per disc are estimates read
    off the photos, not measurements.
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
STRUT_OUT = HERE.parent / "strut" / "out"

# ---------------- PARAMETERS (photo values x K_SCALE) ----------------
K_SCALE = 65.0 / 59.0
R_TIP = 29.5 * K_SCALE          # tooth tips = 32.5 mm
R_DISK = 27.0 * K_SCALE         # smooth outer disk
TOOTH_DEPTH = 2.5 * K_SCALE
N_TEETH = 17
N_DISCS = 8
DISC_T = 0.9 * K_SCALE
DISC_PITCH = 3.9 * K_SCALE      # axial pitch of the saw-tooth discs
FIRST_DISC = 3.2 * K_SCALE      # inboard distance from the outer face of the smooth disk to the first saw-tooth disc
TWIST_PER_DISC = 8.0            # degrees per disc going inboard, counterclockwise seen from outside (about 63 degrees over the stack)
R_CORE = 11.0                   # hub core under the discs (the wheel holds a gearmotor)
DISK_T = 1.0 * K_SCALE
AXLE_D = S.AXLE_D
COLLAR_D = 11.0 * K_SCALE * 0.95
COLLAR_L = S.COLLAR_L
# --------------------------------------------------------------------

W = FIRST_DISC + DISC_PITCH * (N_DISCS - 1) + DISC_T         # width from the outer face of the smooth disk to the inner face of the last disc
SAWTOOTH = None


def sawtooth_disc():
    pts = []
    for i in range(N_TEETH):
        a = 2 * math.pi * i / N_TEETH
        for r in (R_TIP - TOOTH_DEPTH, R_TIP):
            pts.append((r * math.cos(a), r * math.sin(a)))
    with BuildSketch() as sk:
        Polygon(*pts, align=None)
    return sk.sketch


def wheel_local():
    """Wheel with its axis along +z: inner face at z = 0, outer face of the smooth disk at z = W, collar beyond."""
    core = Cylinder(R_CORE, W, align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid = core
    face = sawtooth_disc()
    for i in range(N_DISCS):
        d = FIRST_DISC + DISC_PITCH * i                      # inboard distance of this disc's outer face
        z0 = W - d - DISC_T
        disc = extrude(face, amount=DISC_T).moved(Location((0, 0, z0)))
        disc = disc.rotate(Axis.Z, TWIST_PER_DISC * i)
        solid = solid + disc
    solid = solid + Cylinder(R_DISK, DISK_T, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, W - DISK_T)))
    solid = solid + Cylinder(COLLAR_D / 2, COLLAR_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, W)))
    solid = solid - Cylinder(AXLE_D / 2, W + COLLAR_L + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -1)))
    return solid


def place(w, direction, deg, side):
    """Wheel at the strut tip for the strut pointing along +y (direction +1) or -y (-1), posed `deg` below horizontal."""
    w = w.moved(Location((S.STRUT_L, 0, 0)))
    w = S.on_axle(w, S.WHEEL_X[0]).moved(Location((0, 0, E.HUB_Z)))
    if direction < 0:
        w = w.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), 180)
    w = S.posed(w, direction, deg)
    if side < 0:
        w = w.rotate(Axis.Z, 180)         # same wheel on the other side (a rotated copy, not a mirror), so the helix keeps its handedness
    return w


def main():
    OUT.mkdir(exist_ok=True)
    w0 = wheel_local()
    bb = w0.bounding_box()
    print(f"wheel               tooth diameter {2 * R_TIP:.1f} mm, smooth disk {2 * R_DISK:.1f} mm, width {W:.1f} mm to the disk face plus a {COLLAR_L:.0f} mm collar "
          f"(bounding box {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f})")
    print(f"                    {N_DISCS} saw-tooth discs of {N_TEETH} teeth, {DISC_T:.2f} mm thick on a {DISC_PITCH:.2f} mm pitch, "
          f"each turned {TWIST_PER_DISC:.0f} degrees from the last ({TWIST_PER_DISC * (N_DISCS - 1):.0f} degrees over the stack; a tooth is {360 / N_TEETH:.1f} degrees)")
    print(f"                    mass about {w0.volume * 2.70e-3:.0f} g each in aluminium, solid core, no motor; scale from the photo {K_SCALE:.3f}")
    wheels = []
    for side in (1, -1):
        for d in (+1, -1):
            wheels.append(place(w0, d if side > 0 else -d, S.POSE_DEG, side))
    WH = Compound(wheels)

    # ---- checks against the other parts at the default pose ----
    parts = {"body": import_step(BODY_OUT / "body_hammond.step"), "hub studs": import_step(BODY_OUT / "hub_studs.step"),
             "struts": import_step(STRUT_OUT / "struts.step"), "lid plate": import_step(BODY_OUT / "lid_plate.step")}
    for nm, shp in parts.items():
        hit = WH & shp
        print(f"wheels vs {nm:<10} overlap {hit.volume if hit else 0.0:.2f} mm3")
    for i, w in enumerate(wheels):
        b = w.bounding_box()
        print(f"  wheel {i}: x {b.min.X:7.1f} .. {b.max.X:7.1f}   y {b.min.Y:7.1f} .. {b.max.Y:7.1f}   z {b.min.Z:6.1f} .. {b.max.Z:6.1f}")
    bball = WH.bounding_box()
    print(f"overall (default pose) {bball.size.X:.1f} wide x {bball.size.Y:.1f} long; wheel bottoms at z = {bball.min.Z:.1f}")
    export_step(WH, str(OUT / "wheels.step"))
    print("wrote", OUT / "wheels.step")

if __name__ == "__main__":
    main()
