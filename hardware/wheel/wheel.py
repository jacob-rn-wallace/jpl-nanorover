#!/usr/bin/env python3
"""Wheels for the rover: a conical outer disk on a smooth hollow cylinder with helical, serrated grousers standing radially.

Run after hardware/body/body.py and hardware/strut/strut.py:
    .venv/bin/python hardware/wheel/wheel.py        writes hardware/wheel/out/wheels.step

Where the numbers come from (docs/wheel-spec.md has the full record)
  * NanoRover-hires.original.jpg (JPL, a silver-bodied prototype photographed from a three-quarter view).  The camera was solved from the
    vanishing points of the solar-cell edges (focal length about 1920 px).  Two wheels there are seen almost edge-on (the wheel axis is 78 to 80
    degrees from the viewing ray), so the cone profile reads directly off the image:
      - the outer disk is a real **cone**: the collar sits on the apex (about 10 mm proud of the rim, the collar centre about 14 mm) for a rim of 59.5 mm across;
      - behind it is a smooth cylinder whose radius equals the cone's rim, carrying **grousers in a helix**: thin blades that stand straight up, radially, from
        the cylinder surface, with fine saw-tooth serrations along their outer edges.  The helix leans 43.5 degrees from the axle at the crests,
        right-handed, and there are about 16 grousers (the dark step lines are spaced 19 to 25 degrees on the visible arc);
      - the cylinder is about 34 mm long and the grousers stand about 2.75 mm proud of it.
  * img840-340-hires.original.jpg (the earlier prototype) gives the same cone rim to tooth-tip ratio (27.0 / 29.5 = 0.915) and about 17 teeth;
    its disk looks nearly flat, so that wheel differs from the one in the second photo.  The second photo is the better guide to the MUSES-CN wheel.
  * Both photographed wheels are about 59 mm across the teeth (the sources say "about 6 cm" for the prototype); the MUSES-CN papers give
    65 mm.  All measured proportions are scaled by 65 / 59 so the tooth diameter is the published 65 mm (K_SCALE).
  * Wall thicknesses, the hollow interior, the hub tube, the collar size, the grouser thickness and the serration shape are estimates, not measurements.
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
R_TIP = 29.5 * K_SCALE            # grouser crests = 32.5 mm
R_ROOT = 27.0 * K_SCALE           # smooth cylinder = rim of the cone = 29.75 mm
N_TEETH = 16                      # grousers around the cylinder
HELIX_DEG = 43.5                  # helix angle of the grousers from the axle at the crests, right-handed (seen from outside it turns counterclockwise going outward)
L_DRUM = 31.3 * K_SCALE           # cylinder length (about 34.5 mm after scaling)
H_CONE = 9.2 * K_SCALE            # cone apex above the rim (about 10 mm): the collar centre is about 14 mm above the rim, the collar being 8 mm long
# Wall thicknesses are estimates.  "thin" is layout C (docs/drivetrain-spec.md): thin-walled aluminium, the wheel motor sits inside on the strut tip
# and drives the wheel through its output shaft at the cone apex, so there is no hub tube.  "v1" is the wheel as first modelled (with a hub tube on a 6 mm axle).
PRESETS = {
    "v1":   dict(WALL=2.5, END_T=2.0, CONE_T=1.5, GROUSER_T=1.2, HUB_TUBE=True),
    "thin": dict(WALL=1.0, END_T=1.0, CONE_T=0.8, GROUSER_T=0.8, HUB_TUBE=False),
}
PRESET = "thin"
HUB_D = 12.0                      # hub tube around the axle (v1 only)
HOLE_D = 12.0                     # hole in the inboard end plate for the wheel motor, 10 mm (thin only; 1 mm clearance all round)
SHAFT_BORE = S.SHAFT_D + 0.1      # bore in the apex boss and collar for the motor's output shaft (diameter assumed in strut.py)
BOSS_IN = 4.0                     # boss under the cone apex that the output shaft drives (thin only)
SERR_PITCH = 3.0                  # axial pitch of the serrations along each crest
SERR_DEPTH = 1.4
SERR_WIDTH = 2.4                  # tangential width of each notch
AXLE_D = S.AXLE_D
COLLAR_D = 8.0                    # collar on the cone apex (about 8 mm across and 8 mm long in the second photo)
COLLAR_L = S.COLLAR_L
# --------------------------------------------------------------------

def use_preset(name):
    """Switch the wall thicknesses and the hub style: sets the module-level parameters the builders read."""
    g = globals()
    g["PRESET"] = name
    g.update(PRESETS[name])
    g["R_INNER"] = R_ROOT - PRESETS[name]["WALL"]


use_preset(PRESET)

TWIST = math.degrees(L_DRUM * math.tan(math.radians(HELIX_DEG)) / R_TIP)   # azimuth turned over the cylinder length, from the helix angle at the crests
W = L_DRUM + H_CONE                                                      # inner face to the cone apex


def cylinder():
    """Smooth hollow cylinder with N helical grousers: radial blades that follow a helix along the cylinder, serrated along their crests."""
    shell = Cylinder(R_ROOT, L_DRUM, align=(Align.CENTER, Align.CENTER, Align.MIN)) - \
        Cylinder(R_INNER, L_DRUM - END_T, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, END_T)))
    # one grouser: a radial rectangle (set 0.6 mm into the cylinder wall), twisted about the axle as it is extruded
    r0 = R_ROOT - 0.6
    blade = Face(Wire.make_polygon([Vector(r0, -GROUSER_T / 2, 0), Vector(R_TIP, -GROUSER_T / 2, 0),
                                    Vector(R_TIP, GROUSER_T / 2, 0), Vector(r0, GROUSER_T / 2, 0)], close=True))
    one = Solid.extrude_linear_with_rotation(blade, Vector(0, 0, 0), Vector(0, 0, L_DRUM), TWIST)
    fins = [one.rotate(Axis.Z, 360.0 * j / N_TEETH) for j in range(N_TEETH)]
    # serrations: right-triangle notches in each crest every SERR_PITCH, following the helix
    prof = Wire.make_polygon([Vector(R_TIP + 0.6, 0, 0), Vector(R_TIP + 0.6, 0, SERR_PITCH),
                              Vector(R_TIP - SERR_DEPTH, 0, 0)], close=True)
    tmpl = Solid.extrude(Face(prof), Vector(0, SERR_WIDTH / 2, 0)) + Solid.extrude(Face(prof), Vector(0, -SERR_WIDTH / 2, 0))
    cutters = []
    n_st = int((L_DRUM - SERR_PITCH) // SERR_PITCH)
    for k in range(n_st):
        z = 1.2 + SERR_PITCH * k
        for j in range(N_TEETH):
            ang = 360.0 * j / N_TEETH + TWIST * z / L_DRUM
            cutters.append(tmpl.moved(Location((0, 0, z))).rotate(Axis.Z, ang))
    solid = shell + Compound(fins)
    solid = solid - Compound(cutters)
    return solid


def wheel_local():
    """Wheel with its axis along +z: inner face at z = 0, cone rim at z = L_DRUM, cone apex at z = W, collar beyond."""
    d = cylinder()
    # cone shell, revolved: outer line from the rim (R_ROOT, L_DRUM) up to the apex, thickness CONE_T measured normal-ish (kept vertical here)
    with BuildSketch(Plane.XZ) as sk:
        Polygon((R_ROOT, L_DRUM), (R_ROOT, L_DRUM - CONE_T), (0, L_DRUM + H_CONE - CONE_T), (0, L_DRUM + H_CONE), align=None)
    cone = revolve(sk.sketch, Axis.Z)
    collar = Cylinder(COLLAR_D / 2, COLLAR_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, W)))
    if HUB_TUBE:
        hub = Cylinder(HUB_D / 2, W, align=(Align.CENTER, Align.CENTER, Align.MIN))
        solid = d + cone + hub + collar
        return solid - Cylinder(AXLE_D / 2, W + COLLAR_L + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -1)))
    boss = Cylinder(COLLAR_D / 2, BOSS_IN + CONE_T, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, W - BOSS_IN - CONE_T)))
    solid = d + cone + boss + collar
    solid = solid - Cylinder(HOLE_D / 2, END_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -1)))
    z0 = W - BOSS_IN - CONE_T - 1
    solid = solid - Cylinder(SHAFT_BORE / 2, W + COLLAR_L + 2 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, z0)))
    return solid


def place(w, direction, deg, side):
    """Wheel at the strut tip for the strut pointing along +y (direction +1) or -y (-1), posed `deg` below horizontal."""
    w = w.moved(Location((S.STRUT_L, 0, 0)))
    w = S.on_axle(w, S.WHEEL_X[0]).moved(Location((0, 0, E.HUB_Z)))
    if direction < 0:
        w = w.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), 180)
    w = S.posed(w, direction, deg)
    if side < 0:
        w = w.rotate(Axis.Z, 180)         # the same wheel on the other side (a rotated copy, not a mirror), so the helix keeps its handedness
    return w


def main():
    OUT.mkdir(exist_ok=True)
    w0 = wheel_local()
    bb = w0.bounding_box()
    print(f"wheel               grouser tips {2 * R_TIP:.1f} mm across, cylinder and cone rim {2 * R_ROOT:.1f} mm, cylinder {L_DRUM:.1f} mm long, cone apex {H_CONE:.1f} mm above the rim, "
          f"{W:.1f} mm inner face to apex plus a {COLLAR_L:.0f} mm collar (bounding box {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f})")
    print(f"                    {N_TEETH} helical grousers ({360 / N_TEETH:.1f} degrees apart), blades {GROUSER_T} mm thick standing {R_TIP - R_ROOT:.2f} mm proud, "
          f"{HELIX_DEG} degrees from the axle at the crests, right-handed: {TWIST:.0f} degrees of turn over the cylinder; serrations {SERR_PITCH} mm pitch, {SERR_DEPTH} mm deep")
    print(f"                    valid {w0.is_valid}, solids {len(w0.solids())}, mass about {w0.volume * 2.70e-3:.0f} g each in aluminium (hollow drum, no motor; preset '{PRESET}'); photo scale {K_SCALE:.3f}")
    wheels = []
    for side in (1, -1):
        for d in (+1, -1):
            wheels.append(place(w0, d if side > 0 else -d, S.POSE_DEG, side))
    WH = Compound(wheels)

    # ---- checks against the other parts at the default pose ----
    parts = {"body": import_step(BODY_OUT / "body_hammond.step"), "hub studs": import_step(BODY_OUT / "hub_studs.step"),
             "struts": import_step(STRUT_OUT / "struts.step"), "lid plate": import_step(BODY_OUT / "lid_plate.step")}
    if (STRUT_OUT / "wheel_motors.step").exists() and not HUB_TUBE:
        parts["motors"] = import_step(STRUT_OUT / "wheel_motors.step")
    for nm, shp in parts.items():
        assert shp.volume > 0, f"{nm} imported with zero volume; re-run its script"
        hit = WH & shp
        print(f"wheels vs {nm:<10} overlap {hit.volume if hit else 0.0:.2f} mm3")
    for i, w in enumerate(wheels):
        b = w.bounding_box()
        print(f"  wheel {i}: x {b.min.X:7.1f} .. {b.max.X:7.1f}   y {b.min.Y:7.1f} .. {b.max.Y:7.1f}   z {b.min.Z:6.1f} .. {b.max.Z:6.1f}")
    bball = WH.bounding_box()
    print(f"overall (default pose) {bball.size.X:.1f} wide x {bball.size.Y:.1f} long; wheel bottoms at z = {bball.min.Z:.1f}")
    export_step(WH, str(OUT / "wheels.step"))
    chk = import_step(OUT / "wheels.step")
    print(f"re-imported wheels.step: {len(chk.solids())} solids, volume {chk.volume / 1000:.1f} cm3 (live {WH.volume / 1000:.1f})")
    print("wrote", OUT / "wheels.step")


if __name__ == "__main__":
    main()
