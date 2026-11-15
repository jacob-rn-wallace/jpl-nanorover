#!/usr/bin/env python3
"""Which draw direction can the forged body be pressed in?   (needs the venv: it imports layout.py)

Run: .venv/bin/python hardware/body/draw_analysis.py

The rule (a press with two cores, one coming in from each side along the draw axis, meeting at a parting plane through the middle, the outside machined afterwards, owner 2026-11-12): a void in the
part is made by a core, and a core must be pulled out along the draw axis, so *everything between a void and the face its core comes from must also be void*. So material may not stand in the "shadow"
of a fixed void on the side toward its core's face.  For each candidate axis (and parting plane) this script measures how much of the design space is lost to such shadows, which is a measure of how
well the fixed voids fit that draw direction.
Inputs: the voids that cannot move (voxels at 1 mm): the servo pockets and hub parts (layout.py `occ`), every placed component and servo plug zone, the 11 wire channels (wire_routes.json), the servo plate
seats and the contact pockets (rebuilt here from block.py's numbers).  Holes that are machined from OUTSIDE after pressing (the hub bores, the cam bores, the windows) are not counted: the owner's route
machines the outside, so they do not constrain the draw.  The 2.5 mm skin and the lids' own volumes are outside the design space.  Approximate: boxes and cylinders as in block.py; no draft.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
with contextlib.redirect_stdout(io.StringIO()):
    import layout as LY
    import harness as HN

H = LY.H
HZ = LY.HZ
vox = LY.vox

# ---- fixed voids ----
void = LY.occ.copy()
for n, m in LY.placed.items():
    void |= m
wr = HERE / "out" / "wire_routes.json"
n_ch = 0
if wr.exists():
    for _nm, r in json.loads(wr.read_text()).items():
        h = r["channel_side_mm"] / 2
        n_ch += 1
        for a, b in zip(r["points"][:-1], r["points"][1:]):
            lo = [min(a[i], b[i]) - h for i in range(3)]; hi = [max(a[i], b[i]) + h for i in range(3)]
            void |= LY.box_mask(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
for (tag, side), s in LY.servos.items():                      # the servo plate seats (block.py): footprint + 0.2 mm, 3.1 mm deep
    sa, sb = sorted((side * s["xf"], side * (s["xf"] + 3.1)))
    void |= LY.box_mask(sa, sb, s["y0"] - 0.2, s["y1"] + 0.2, HZ - LY.SV_Z - 0.2, HZ + LY.SV_Z + 0.2)
P = HN.pockets()
for zc in (49.0, 11.0):                                       # the contact pockets (lid_cad.py), 12 mm deep from |x| = 37
    for sx in (1, -1):
        L = P["+" if sx > 0 else "-"]
        void |= LY.box_mask(*sorted((sx * 37.0, sx * 49.0)), -5.0, -5.0 + L, zc - 1.6, zc + 1.6)
design = LY.keep_in & ~void                                   # the solid left to design with (the skin is outside keep_in)
print(f"voids counted: {void.sum() * vox:.0f} cm3 of fixed void ({n_ch} wire channels, the servo and hub parts, {len(LY.placed)} placed boxes, 4 plate seats, 4 contact pockets); design space {design.sum() * vox:.0f} cm3 of the {LY.keep_in.sum() * vox:.0f} cm3 keep-in")

# the body middle is the region between the lid joints (z 7 to 53); the lids are separate parts and are not drawn in this press
BODY = (LY.Z >= 7.0) & (LY.Z <= 53.0)
# the housing tube's bore through each hub wall (|x| >= 59.5, radius 14.5 about the hub axis) and the hollow shaft's through it are drilled from outside after pressing, so they cast no shadow
MACHINED = LY.cylx_mask(0.0, HZ, 14.5, 59.5, 70.0) | LY.cylx_mask(0.0, HZ, 14.5, -70.0, -59.5)
design_b = design & BODY
void_b = (void & BODY & ~MACHINED) & ~(LY.placed[[n for n in LY.placed if n.startswith('processor')][0]] | LY.placed[[n for n in LY.placed if n.startswith('power')][0]])      # the two boards ride on the lids, not in the body
print(f"body middle (z 7 to 53): design space {design_b.sum() * vox:.0f} cm3 before any draw constraint\n")


def shadow_two_sided(axis, plane, vmask=None):
    """Material is lost in the shadow of a void on the core's side. axis 0,1,2 = x,y,z; plane = the parting coordinate.
    A core from the + face fills everything between that face and a void in the half above the plane: a voxel above the plane is lost if there is a void at a LOWER coordinate in the same column, still above the plane.
    Likewise below the plane, toward the - face: lost if there is a void at a HIGHER coordinate, still below the plane."""
    v = np.moveaxis(void_b if vmask is None else vmask, axis, 0)
    coords = (LY.xs, LY.ys, LY.zs)[axis]
    up = coords > plane
    lost = np.zeros_like(v)
    vp = v.copy(); vp[~up] = False
    lost |= np.maximum.accumulate(vp, axis=0) & up[:, None, None]                                    # a void between the plane and this voxel
    vm = v.copy(); vm[up] = False
    lost |= np.flip(np.maximum.accumulate(np.flip(vm, axis=0), axis=0), axis=0) & ~up[:, None, None]  # a void between this voxel and the plane
    return np.moveaxis(lost, 0, axis)


def shadow_one_sided(axis, sign):
    """A single core from the face on the `sign` side: a voxel is lost if a void lies between it and the opposite side (toward the core's face the core must pass it): lost if a void is at a lower coordinate for a + core."""
    v = np.moveaxis(void_b, axis, 0)
    if sign > 0:
        cum = np.maximum.accumulate(v, axis=0)
    else:
        cum = np.flip(np.maximum.accumulate(np.flip(v, axis=0), axis=0), axis=0)
    return np.moveaxis(cum, 0, axis)


print(f"{'draw plan':44s} {'design space left':>18s} {'lost to shadows':>16s}")
rows = []
names = "xyz"
for axis in (2, 0, 1):
    centre = (HZ if axis == 2 else 0.0)
    lost = shadow_two_sided(axis, centre) & design_b
    left = design_b & ~lost
    rows.append((f"two-sided along {names[axis]}, parting at {names[axis]} = {centre:g}", left.sum() * vox, lost.sum() * vox))
    for sign in (+1, -1):
        lost = shadow_one_sided(axis, sign) & design_b
        left = design_b & ~lost
        rows.append((f"one-sided along {names[axis]}, core from the {'+' if sign > 0 else '-'}{names[axis]} face", left.sum() * vox, lost.sum() * vox))
tot = design_b.sum() * vox
for n, left, lost in rows:
    print(f"{n:44s} {left:10.0f} cm3 {100 * left / tot:4.0f}% {lost:10.0f} cm3")
best = max(rows, key=lambda r: r[1])
print(f"\nbest: {best[0]} keeps {best[1]:.0f} of {tot:.0f} cm3 ({100 * best[1] / tot:.0f}%)")
print("reading: a plan that keeps most of the design space fits the fixed voids; the voids that cost the most are the ones whose columns reach the faces.")

# which voids cost the most under the best two-sided z plan: the lost volume by void group
lost_z = shadow_two_sided(2, HZ) & design_b
print("\nunder 'two-sided along z': the lost volume is the shadow of these fixed voids (cm3 of design space lost if only that group were present):")
groups = {"servo pockets and hub": LY.occ & BODY & ~MACHINED}
for n, m in LY.placed.items():
    if not (n.startswith('processor') or n.startswith('power')):
        groups[n[:42]] = m & BODY
chan = np.zeros_like(void)
if wr.exists():
    for _nm, r in json.loads(wr.read_text()).items():
        h = r["channel_side_mm"] / 2
        for a, b in zip(r["points"][:-1], r["points"][1:]):
            lo = [min(a[i], b[i]) - h for i in range(3)]; hi = [max(a[i], b[i]) + h for i in range(3)]
            chan |= LY.box_mask(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
groups["wire channels (11 bundles)"] = chan & BODY
res = []
for n, m in groups.items():
    lost = shadow_two_sided(2, HZ, m) & design_b & ~m
    res.append((lost.sum() * vox, n))
for v, n in sorted(res, reverse=True)[:8]:
    print(f"  {v:7.0f} cm3  {n}")
