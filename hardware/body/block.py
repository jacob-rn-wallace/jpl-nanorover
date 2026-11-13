"""The body as a solid, uniform 140 x 140 x 60 mm block with the components, connections and views cut out of it (owner's design method, 2026-11-11).

Run: .venv/bin/python hardware/body/block.py      (after layout.py's inputs exist; writes hardware/body/out/body_block.step, our own geometry, safe to track)

The block is a design volume, not the part: solid carbon would weigh about 1.8 kg. Both bodies under consideration are derived from it later:
  * a chassis of carbon tubs bonded together (the faces of the block, exterior and interior, become laminate), or
  * a forged-carbon unibody (the cavities become the cores of a mould).
This script cuts the cavities, checks the export, and measures what the cavities leave: how much solid there is, how much of it is within a skin thickness
of a surface, and the surface area of each cavity group (the mass of lining it with a skin).

It reuses layout.py's component list, servo positions and hub constants (its prints are suppressed). Placeholders stay placeholders: no part is chosen.
"""
import contextlib
import io
import math
import sys
from pathlib import Path

import numpy as np
from build123d import Align, Axis, Box, Cone, Cylinder, Location, Plane, Compound, import_step, export_step

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
with contextlib.redirect_stdout(io.StringIO()):          # layout.py prints its own report; only its definitions are wanted here
    import layout as LY
H = LY.H
OUT = HERE / "out"
HZ = LY.HZ
CLR = LY.CLR


def bx(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


def cyl(axis, c1, c2, r, a, b):
    """Cylinder of radius r along x, y or z from a to b, with its centre line through the other two coordinates (c1, c2)."""
    c = Cylinder(r, b - a, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if axis == "x":
        return c.rotate(Axis.Y, 90).moved(Location((a, c1, c2)))        # z -> +x
    if axis == "y":
        return c.rotate(Axis.X, -90).moved(Location((c1, a, c2)))       # z -> +y
    return c.moved(Location((c1, c2, a)))


# ---------------- cavity groups: name -> list of (solid, surface area mm2) ----------------
def area_box(x0, x1, y0, y1, z0, z1):
    a, b, c = x1 - x0, y1 - y0, z1 - z0
    return 2 * (a * b + b * c + c * a)


def area_cyl(r, h):
    return 2 * math.pi * r * h + 2 * math.pi * r * r


groups = {}


def add(group, solid, area):
    groups.setdefault(group, []).append((solid, area))


# servos (with 1 mm clearance) and their bosses
for (tag, side), s in LY.servos.items():
    xa, xb = sorted((side * (s["xf"] - H.SV_H), side * s["xf"]))
    b = (xa - CLR, xb + CLR, s["y0"] - CLR, s["y1"] + CLR, HZ - LY.SV_Z - CLR, HZ + LY.SV_Z + CLR)
    add("4 servo pockets", bx(*b), area_box(*b))
    r = H.SV_BOSS_D / 2 + CLR
    bo0, bo1 = sorted((side * s["xf"], side * (s["xf"] + H.SV_BOSS_H + CLR)))
    add("4 servo pockets", cyl("x", s["y_shaft"], HZ, r, bo0, bo1), area_cyl(r, H.SV_BOSS_H + CLR))
    xb0 = side * (s["xf"] - H.SV_H - 4.1) - side * CLR
    xb1 = side * (s["xf"] - H.SV_H)
    add("4 servo pockets", cyl("x", s["y_shaft"], HZ, r, min(xb0, xb1), max(xb0, xb1)), area_cyl(r, 4.1 + CLR))

# hub: housing tube through each hub wall, gears, hollow shaft, horn adapter (1 mm clearance)
for side in (+1, -1):
    def span(a, b):
        return (min(side * a, side * b), max(side * a, side * b))
    for nm, y, r, a, b in (("housing tube and wall hole", 0.0, H.HOUSE_OD / 2 + CLR, H.X_HOUSE_IN - CLR, 70.0),
                           ("gear A", 0.0, H.GEAR_OD / 2 + CLR, H.X_GEAR[0] - CLR, H.X_GEAR[1] + CLR),
                           ("pinion A", -H.CD, H.GEAR_OD / 2 + CLR, H.X_GEAR[0] - CLR, H.X_GEAR[1] + CLR),
                           ("hollow shaft", 0.0, H.HOLLOW_OD / 2 + CLR, H.X_HOLLOW[0] - CLR, 70.0),
                           ("horn adapter", 0.0, 10.0 + CLR, H.B_ADAPTER[0] - CLR, H.B_ADAPTER[1] + CLR)):
        lo, hi = span(a, b)
        add("hub drive (both sides)", cyl("x", y, HZ, r, lo, hi), area_cyl(r, hi - lo))

# placeholders from layout.py
for n, (m, bb, note, _c) in LY.comps.items():
    x0, x1, y0, y1, z0, z1 = bb
    if n.startswith("processor") or n.startswith("power"):
        add("boards (ride on the lids)", bx(*bb), area_box(*bb))
    elif n.startswith("battery"):
        add("battery", bx(*bb), area_box(*bb))
    elif n.startswith("comms patch"):
        add("comms antenna", bx(*bb), area_box(*bb))
    else:
        add("camera, beamsplitter and lamp", bx(*bb), area_box(*bb))

# connections and views
r_win = 13.0                                                              # 26 mm window aperture, through the +y wall
add("camera, beamsplitter and lamp", cyl("y", LY.WIN_X, LY.WIN_Z, r_win, 60.0, 70.0), area_cyl(r_win, 10.0))
frustum_len = 69.0 - 46.5                                                 # lens front to the window plane
cone = Cone(0.5, r_win, frustum_len, align=(Align.CENTER, Align.CENTER, Align.MIN)).rotate(Axis.X, -90).moved(Location((LY.WIN_X, 46.5, LY.WIN_Z)))
add("camera, beamsplitter and lamp", cone, math.pi * (0.5 + r_win) * math.hypot(r_win - 0.5, frustum_len))     # the view: 60 degree full angle at 26 mm
add("camera, beamsplitter and lamp", cyl("x", 57.0, LY.WIN_Z, 6.0, 28.0, LY.WIN_X), area_cyl(6.0, LY.WIN_X - 28.0))   # lamp beam to the plate
w = (LY.ANT_X - LY.ANT_WIN_HALF, LY.ANT_X + LY.ANT_WIN_HALF, -70.0, -67.5, LY.ANT_Z - LY.ANT_WIN_HALF, LY.ANT_Z + LY.ANT_WIN_HALF)
add("comms antenna", bx(*w), area_box(*w))   # 27 mm square RF-transparent window through the -y wall, flush with the face

# the through-wall opening for the shared cover glass is a circle of radius WIN_R_GLASS on the same centre (the ranging sensor sits in its ring)
add("ranging sensor", cyl("y", LY.WIN_X, LY.WIN_Z, LY.WIN_R_GLASS, 60.0, 70.0), area_cyl(LY.WIN_R_GLASS, 10.0))

block = Box(140, 140, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))
volume_block = block.volume
cut = block
all_cavities = [s for g in groups.values() for s, _ in g]
for s in all_cavities:
    cut = cut - s
OUT.mkdir(exist_ok=True)
step_path = OUT / "body_block.step"
export_step(cut, str(step_path))
chk = import_step(str(step_path))
print(f"block {volume_block / 1000:.0f} cm3; {len(all_cavities)} cavities cut; remaining {cut.volume / 1000:.0f} cm3 ({cut.volume / volume_block:.0%} of the block)")
print(f"re-imported {step_path.name}: {len(chk.solids())} solid(s), volume {chk.volume / 1000:.1f} cm3 (live {cut.volume / 1000:.1f}) -> {'OK' if abs(chk.volume - cut.volume) < 1.0 else 'MISMATCH'}")
print(f"if it were solid carbon at 1.55 g/cm3 the block with cavities weighs {cut.volume / 1000 * 1.55:.0f} g (a design volume, not the part)")

# ---------------- what the cavities leave: skin and core, by distance transform on a voxel copy ----------------
from scipy.ndimage import distance_transform_edt  # noqa: E402

solid = ~LY.occ & np.ones_like(LY.occ)
for n, bm in LY.placed.items():
    solid &= ~bm
# add the window, frustum, lamp beam and antenna window holes to the voxel copy
X, Y, Z = LY.X, LY.Y, LY.Z
solid &= ~((Y >= 60) & ((X - LY.WIN_X) ** 2 + (Z - LY.WIN_Z) ** 2 <= r_win ** 2))
tt = np.clip((Y - 46.5) / frustum_len, 0, 1)
solid &= ~((Y >= 46.5) & (Y <= 69) & ((X - LY.WIN_X) ** 2 + (Z - LY.WIN_Z) ** 2 <= (0.5 + tt * (r_win - 0.5)) ** 2))
solid &= ~((X >= 28) & (X <= LY.WIN_X) & ((Y - 57.0) ** 2 + (Z - LY.WIN_Z) ** 2 <= 36.0))
solid &= ~((Y >= 60) & ((X - LY.WIN_X) ** 2 + (Z - LY.WIN_Z) ** 2 <= LY.WIN_R_GLASS ** 2))
solid &= ~((Y <= -67.5) & (np.abs(X - LY.ANT_X) <= LY.ANT_WIN_HALF) & (np.abs(Z - LY.ANT_Z) <= LY.ANT_WIN_HALF))
pad = np.pad(solid, 1, constant_values=False)
d = distance_transform_edt(pad)[1:-1, 1:-1, 1:-1] * LY.RES
vox = LY.vox
print(f"\nvoxel copy (1 mm): solid {solid.sum() * vox:.0f} cm3 (the CAD says {cut.volume / 1000:.0f}; the difference is voxel rounding and cylinder facets)")
print("lining every surface, outside and in, with a skin of thickness t keeps only the material within t of a surface:")
for t in (1.0, 1.5, 2.0):
    skin = (solid & (d <= t)).sum() * vox
    print(f"  t = {t:.1f} mm: skin {skin:5.0f} cm3 -> {skin * 1.55:4.0f} g woven, {skin * 1.45:4.0f} g forged; the rest ({solid.sum() * vox - skin:.0f} cm3) is core to leave hollow")

# exterior alone, for comparison, and the cost of each cavity group's own lining
print("\nthe outside alone, 728 cm2: 1.0 mm skin = 113 g woven; 1.5 mm = 169 g.")
print("\nlining each cavity group (its surface area x t, no sharing with neighbours or the outside):")
print(f"  {'group':34s} {'area cm2':>9s} {'1.0 mm woven g':>15s} {'1.5 mm forged g':>16s}")
tot_a = 0.0
for g, items in groups.items():
    a = sum(x for _, x in items) / 100.0
    tot_a += a
    print(f"  {g:34s} {a:9.0f} {a * 0.1 * 1.55:15.0f} {a * 0.15 * 1.45:16.0f}")
print(f"  {'all groups':34s} {tot_a:9.0f} {tot_a * 0.1 * 1.55:15.0f} {tot_a * 0.15 * 1.45:16.0f}")
print(f"\nbudget for the whole body contents is 386 g; the forged shell is 164 g (1.5 mm), the electronics etc {LY.elec:.0f} g and the cells {LY.CELL_MASS_G:.0f} g (IXOLAR parts, layout.py).")

# which cavities come within a skin of the outside (share the outside's skin) and which are far from it
print("\ngap from each cavity group's bounding box to the nearest outer face (mm; a gap under 2 mm means it shares the outer skin or breaches it):")
for g, items in groups.items():
    gaps = []
    for s_, _ in items:
        bb = s_.bounding_box()
        gaps.append(min(70 - bb.max.X, bb.min.X + 70, 70 - bb.max.Y, bb.min.Y + 70, bb.min.Z, 60 - bb.max.Z))
    print(f"  {g:34s} nearest {min(gaps):5.1f} mm, farthest {max(gaps):5.1f} mm ({sum(1 for x in gaps if x < 2.0)} of {len(gaps)} within 2 mm or through the wall)")
