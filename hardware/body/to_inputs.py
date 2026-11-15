#!/usr/bin/env python3
"""The topology optimisation's input set: the design space, the fixed voids and the fixed (non-design) solids, voxelised.   (needs the venv: it imports layout.py)

Run: .venv/bin/python hardware/body/to_inputs.py [--res 2]        (writes out/to_inputs_r<res>.npz and out/to_inputs_r<res>.json)

Gate 3 of docs/optimisation-setup.md: "assemble the non-design regions into one set".  Domain: the body middle, x and y +-70 mm, z 6 to 54 mm (the lids are separate parts, `block.py`), on a grid of `res` mm (2 by
default: 70 x 70 x 24 cells; the optimiser can coarsen it).  Classes per cell (majority of its 1 mm voxels):
  void   a fixed void: servo pockets and hub parts, placed components and servo plug zones, the 11 wire channels, the four plate seats, the four contact pockets (not the lid-mounted boards)
  solid  a fixed solid that the optimiser must keep (loads act on it): the outer skin, the hub bore rings, the servo plate seats' walls, the cam bores' bosses, the window's boss ring, the lid seat rims
  design everything else inside the keep-in volume
Load-application regions are listed in the .json (names, voxel counts, the load cases that act on them); the forces themselves are in docs/load-cases.md and hardware/body/load_cases.py.
ASM: the fixed-solid regions' sizes are my first cuts (a ring 3 mm thick round each hub bore, 2 mm walls round each seat, 3 mm bosses round the cam bores, a 4 mm window ring, 2 x 8 mm rims at the lid joints);
the mould's draft and the real shell are not in it.
"""
import argparse
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

ap = argparse.ArgumentParser()
ap.add_argument("--res", type=int, default=2, help="cell size in mm (a divisor of 2: 2 or 4)")
ap.add_argument("--grid", type=int, default=0, help="n: also write the optimiser grid, n x n x n/3 cells over x, y +-69 mm and z 7 to 53 mm (n = 36 gives 3.83 mm cells, n = 48 gives 2.875 mm), as cell fractions per class and per loaded region, to out/to_grid_n<n>.npz")
args = ap.parse_args()
R = args.res
H = LY.H
HZ = LY.HZ
vox = LY.vox

# ---------------- 1 mm masks ----------------
void = LY.occ.copy()
for n, m in LY.placed.items():
    if not (n.startswith("processor") or n.startswith("power")):       # the boards ride on the lids
        void |= m
wr = HERE / "out" / "wire_routes.json"
if wr.exists():
    for _nm, r in json.loads(wr.read_text()).items():
        h = r["channel_side_mm"] / 2
        for a, b in zip(r["points"][:-1], r["points"][1:]):
            lo = [min(a[i], b[i]) - h for i in range(3)]; hi = [max(a[i], b[i]) + h for i in range(3)]
            void |= LY.box_mask(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
for (tag, side), s in LY.servos.items():
    sa, sb = sorted((side * s["xf"], side * (s["xf"] + 3.1)))
    void |= LY.box_mask(sa, sb, s["y0"] - 0.2, s["y1"] + 0.2, HZ - LY.SV_Z - 0.2, HZ + LY.SV_Z + 0.2)
P = HN.pockets()
for zc in (49.0, 11.0):
    for sx in (1, -1):
        L = P["+" if sx > 0 else "-"]
        void |= LY.box_mask(*sorted((sx * 37.0, sx * 49.0)), -5.0, -5.0 + L, zc - 1.6, zc + 1.6)

regions = {}                                                              # fixed solids, by name
skin = ~LY.keep_in
regions["outer skin (2.5 mm, loads LC4 and LC6 act here)"] = skin
ring = np.zeros_like(void)
for side in (1, -1):
    ring |= LY.cylx_mask(0.0, HZ, 17.0, *sorted((side * 60.0, side * 70.0))) & ~LY.cylx_mask(0.0, HZ, 14.0, *sorted((side * 59.0, side * 71.0)))
regions["hub bore rings (r 14 to 17, |x| 60 to 70; LC1, LC3)"] = ring
seatw = np.zeros_like(void)
for (tag, side), s in LY.servos.items():
    sa, sb = sorted((side * s["xf"], side * (s["xf"] + 3.1 + 2.0)))
    big = LY.box_mask(sa, sb, s["y0"] - 2.2, s["y1"] + 2.2, HZ - LY.SV_Z - 2.2, HZ + LY.SV_Z + 2.2)
    small = LY.box_mask(sa, sb, s["y0"] - 0.2, s["y1"] + 0.2, HZ - LY.SV_Z - 0.2, HZ + LY.SV_Z + 0.2)
    seatw |= big & ~small
regions["servo plate seat walls (2 mm; LC2)"] = seatw
cam = np.zeros_like(void)
for zc in (38.5, 21.5):
    for sx in (1, -1):
        for y0 in (40.0, -40.0):
            cam |= LY.cylx_mask(y0, zc, 8.0, *sorted((sx * 54.0, sx * 70.0))) & ~LY.cylx_mask(y0, zc, 5.1, *sorted((sx * 53.0, sx * 71.0)))
regions["cam bore bosses (r 5.1 to 8, |x| 54 to 70; LC5)"] = cam
win = LY.cylx_mask(0, 0, 0, 0, 0)  # placeholder shape; the window ring is along y, built below
win = ((LY.X - LY.WIN_X) ** 2 + (LY.Z - LY.WIN_Z) ** 2 <= 22.0 ** 2) & ((LY.X - LY.WIN_X) ** 2 + (LY.Z - LY.WIN_Z) ** 2 >= 14.0 ** 2) & (LY.Y >= 60.0)
regions["window boss ring (r 14 to 22, y 60 to 70)"] = win
rim = ((LY.Z >= 51.0) & (LY.Z <= 53.0)) | ((LY.Z >= 7.0) & (LY.Z <= 9.0))
rim = rim & ((np.abs(LY.X) >= 62.0) | (np.abs(LY.Y) >= 62.0))
regions["lid seat rims (8 mm wide, 2 mm tall at each joint; LC5)"] = rim

# ---------------- the domain and the cell classes ----------------
Z0, Z1 = 6.0, 54.0
domain = (LY.Z >= Z0) & (LY.Z <= Z1)
solid = np.zeros_like(void)
for m in regions.values():
    solid |= m
solid &= ~void
design = LY.keep_in & ~void & ~solid & domain
void &= domain; solid &= domain


def coarsen(m):
    nx, ny, nz = m.shape
    zi = (np.arange(nz) + 0.5 >= Z0) & (np.arange(nz) + 0.5 <= Z1)       # the domain's z cells
    mm = m[:, :, zi]
    nz2 = mm.shape[2]
    if R == 1:
        return mm
    c = mm[: nx // R * R, : ny // R * R, : nz2 // R * R].reshape(nx // R, R, ny // R, R, nz2 // R, R).mean(axis=(1, 3, 5))
    return c >= 0.5


V, S, D = coarsen(void), coarsen(solid), coarsen(design)
S &= ~V; D &= ~V & ~S
cell = (R ** 3) / 1000.0
print(f"grid {D.shape} at {R} mm over the body middle (z {Z0:g} to {Z1:g}); cell volume {cell * 1000:.0f} mm3")
print(f"  fixed void  {V.sum() * cell:7.0f} cm3")
print(f"  fixed solid {S.sum() * cell:7.0f} cm3 ({', '.join(f'{k.split(' (')[0]}: {(coarsen(v & ~void) & S).sum() * cell:.0f}' for k, v in regions.items())})")
print(f"  design      {D.sum() * cell:7.0f} cm3 ({D.sum()} cells; with the z = 30 mirror the unknowns are {D[:, :, D.shape[2] // 2:].sum()})")
out = HERE / "out"; out.mkdir(exist_ok=True)
np.savez_compressed(out / f"to_inputs_r{R}.npz", void=V, solid=S, design=D, res_mm=R, z0=Z0, z1=Z1)
meta = {"res_mm": R, "z_range_mm": [Z0, Z1], "origin_mm": [-70.0, -70.0, Z0], "shape": list(D.shape),
        "fixed_solid_regions": {k: int((coarsen(v & ~void) & S).sum()) for k, v in regions.items()},
        "load_cases": "docs/load-cases.md, hardware/body/load_cases.py (LC1 static on the hub bore rings, LC2 servo torque on the seat walls, LC3 drop on the hub bore rings, LC4 corner impact on the skin, LC5 lid clamp on the cam bosses and the lid rims, LC6 handling on the skin)",
        "material": {"E_GPa": 35.5, "nu": 0.3, "density_g_cm3": 1.55, "allowable_MPa": 113.7}}
(out / f"to_inputs_r{R}.json").write_text(json.dumps(meta, indent=1))
print("wrote", out / f"to_inputs_r{R}.npz", "and .json")

# ---------------- the optimiser grid (for hardware/body/to_run.py, which runs in .venv-to and cannot import layout.py) ----------------
if args.grid:
    n = args.grid; nz = n // 3; hh = 138.0 / n
    assert abs(nz * hh - 46.0) < 1e-6 and nz % 2 == 0, "n must make 46 mm an even number of cells (36, 48, 72 ...)"
    ix = np.floor((LY.X + 69.0) / hh).astype(int); iy = np.floor((LY.Y + 69.0) / hh).astype(int); iz = np.floor((LY.Z - 7.0) / hh).astype(int)
    ok = (ix >= 0) & (ix < n) & (iy >= 0) & (iy < n) & (iz >= 0) & (iz < nz)
    cid = np.where(ok, (ix * n + iy) * nz + iz, -1)
    count = np.bincount(cid[ok], minlength=n * n * nz).astype(float)

    def frac(mask):
        m = ok & mask
        return (np.bincount(cid[m], minlength=n * n * nz) / np.maximum(count, 1)).reshape(n, n, nz)

    out_g = {"n": n, "nz": nz, "h_mm": hh}
    out_g["void"] = frac(void)
    out_g["keep_in"] = frac(LY.keep_in)
    out_g["skin"] = frac(skin)
    nonskin = np.zeros_like(void)
    for k, v in regions.items():
        if not k.startswith("outer skin"):
            nonskin |= v
    out_g["solid_other"] = frac(nonskin & ~void)
    # loaded regions, separated
    out_g["ring_p"] = frac(ring & (LY.X > 0)); out_g["ring_n"] = frac(ring & (LY.X < 0))
    for (tag, side), sv in LY.servos.items():
        sa, sb = sorted((side * sv["xf"], side * (sv["xf"] + 3.1 + 2.0)))
        big = LY.box_mask(sa, sb, sv["y0"] - 2.2, sv["y1"] + 2.2, HZ - LY.SV_Z - 2.2, HZ + LY.SV_Z + 2.2)
        small = LY.box_mask(sa, sb, sv["y0"] - 0.2, sv["y1"] + 0.2, HZ - LY.SV_Z - 0.2, HZ + LY.SV_Z + 0.2)
        out_g[f"seat_{tag}{'p' if side > 0 else 'n'}"] = frac((big & ~small) & ~void)
        out_g[f"seatpos_{tag}{'p' if side > 0 else 'n'}"] = np.array([sv["y_shaft"], HZ])
    out_g["cam_top"] = frac(cam & (LY.Z > HZ)); out_g["cam_bot"] = frac(cam & (LY.Z < HZ))
    out_g["rim_top"] = frac(rim & (LY.Z > HZ)); out_g["rim_bot"] = frac(rim & (LY.Z < HZ))
    out_g["window"] = frac(win)
    for nm, key in (("battery", "battery"), ("camera", "camera"), ("comms patch", "antenna"), ("XBee", "xbee")):
        mm = np.zeros_like(void)
        for pn, pm in LY.placed.items():
            if pn.startswith(nm):
                mm |= pm
        out_g["void_" + key] = frac(mm)
    np.savez_compressed(out / f"to_grid_n{n}.npz", **out_g)
    print(f"optimiser grid {n} x {n} x {nz} (cell {hh:.3f} mm, {n * n * nz} cells) written to out/to_grid_n{n}.npz")
