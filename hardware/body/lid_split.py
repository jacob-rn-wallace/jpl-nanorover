"""A first cut of the lid shape by the owner's method (2026-11-14): split the design space along the surface equidistant from the lid components and the body components,
for the top and the bottom lid, mirror one onto the other and keep what both have in common.

Run: .venv/bin/python hardware/body/lid_split.py     (imports layout.py, so run it from the repository root; about a minute)
Lid components (per lid): the solar cells on the lid face and the board that rides on that lid. Body components: the servos and hub (layout.py's occupied volume with its clearance), the
battery, the camera, the LED ring, the ranging sensor, the comms patch and the end-face cells. A point belongs to the top lid if it is closer to the top lid components than to any body
component (a 3D Euclidean distance transform, 1 mm voxels); the split surface is where the two distances are equal. To make a lid that can be lifted straight off (no undercuts) only
the part of that region connected to the lid face down each (x, y) column is kept ("height field"). The bottom lid is the same mirrored about z = 30; the common shape is the intersection of
the top lid and the mirrored bottom lid. Then the OUTER RIM RULE (owner agreed 2026-11-14): within BAND mm of the four outer faces the parting line is a flat plane D_RIM mm below the lid face
(above the end-face cells' top edge at z = 52.3, with the 1 mm clearance), and the Voronoi surface applies inside. Prints the numbers (volume, depth, clearance, shell mass) and writes
docs/images/lid-split.png.
"""
import contextlib, io, sys
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt as edt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
with contextlib.redirect_stdout(io.StringIO()):
    import layout as LY

X, Y, Z, RES = LY.X, LY.Y, LY.Z, LY.RES
nx, ny, nz = X.shape
def slab(x0, x1, y0, y1, z0, z1): return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= z0) & (Z <= z1)

CELL_T = 1.8                                                             # SM940K09L thickness (the datasheet: 1.8 mm)
cells_top = slab(-67.2, 67.2, -66.95, 66.95, 60 - CELL_T, 60)           # the lid pocket, about 134.4 x 133.9 mm (cell_pocket.py)
cells_bot = slab(-67.2, 67.2, -66.95, 66.95, 0, CELL_T)
board_top = next(m for n, m in LY.placed.items() if n.startswith("power"))
board_bot = next(m for n, m in LY.placed.items() if n.startswith("processor"))
ex = LY.END_CELL_X
end_cells = slab(ex - 43.6, ex + 43.6, 68.2, 70, 7.7, 52.3) | slab(-ex - 43.6, -ex + 43.6, -70, -68.2, 7.7, 52.3)
body_comps = LY.occ | end_cells
for n, m in LY.placed.items():
    if not (n.startswith("power") or n.startswith("processor")):
        body_comps |= m
lid_top = cells_top | board_top
lid_bot = cells_bot | board_bot

def lid_region(lid_comps, from_top):
    dl = edt(~lid_comps, sampling=RES)
    db = edt(~body_comps, sampling=RES)
    region = dl < db                                                     # closer to the lid than to the body: the lid's side of the equidistant surface
    hf = np.zeros_like(region)                                           # keep the part connected to the lid face down each column (no undercut)
    order = range(nz - 1, -1, -1) if from_top else range(nz)
    alive = np.ones(region.shape[:2], bool)
    for k in order:
        alive &= region[:, :, k]
        hf[:, :, k] = alive
    return region, hf

reg_t, hf_t = lid_region(lid_top, True)
reg_b, hf_b = lid_region(lid_bot, False)
hf_b_m = hf_b[:, :, ::-1]                                                # the bottom lid mirrored about z = 30 (the grid is symmetric about 30)
common = hf_t & hf_b_m
vox = RES ** 3 / 1000.0
print(f"top lid, equidistant region        {reg_t.sum() * vox:7.0f} cm3; lifted straight off (height field): {hf_t.sum() * vox:7.0f} cm3 ({100 * (1 - hf_t.sum() / reg_t.sum()):.0f}% of the region is undercut)")
print(f"bottom lid, same, mirrored          {reg_b.sum() * vox:7.0f} cm3; height field {hf_b.sum() * vox:7.0f} cm3")
print(f"common shape (intersection)         {common.sum() * vox:7.0f} cm3; the two lids differ by {((hf_t ^ hf_b_m).sum()) * vox:.0f} cm3 ({100 * (hf_t ^ hf_b_m).sum() / (hf_t | hf_b_m).sum():.0f}% of their union)")
# underside height of the common lid (mm above the floor) per column: the lowest z of the lid
low = np.where(common.any(axis=2), np.argmax(common, axis=2) * RES, np.nan)
th = np.where(common.any(axis=2), 60 - low, np.nan)
print(f"lid depth (face down to the split surface), common shape: min {np.nanmin(th):.0f}, median {np.nanmedian(th):.0f}, max {np.nanmax(th):.0f} mm; columns with no lid: {int((~common.any(axis=2)).sum())} of {nx * ny}")
step = np.abs(np.diff(th, axis=0)); step2 = np.abs(np.diff(th, axis=1))
print(f"how rough the split surface is: the depth changes by more than 3 mm between neighbouring 1 mm columns in {100 * np.nanmean(np.r_[(step > 3).ravel(), (step2 > 3).ravel()]):.1f}% of places")
perim = th[0:3, :].tolist()
edge_depths = np.r_[th[0, :], th[-1, :], th[:, 0], th[:, -1]]
print(f"depth at the outer faces (the rim a gasket would sit on): min {np.nanmin(edge_depths):.0f}, median {np.nanmedian(edge_depths):.0f}, max {np.nanmax(edge_depths):.0f} mm")


# ---------------- the outer rim rule ----------------
D_RIM, BAND = 6.5, 8.0                                                   # mm: parting depth at the rim, and the width of the band where it applies
d_edge = 70.0 - np.maximum(np.abs(X[:, :, 0]), np.abs(Y[:, :, 0]))      # distance of each column from the nearest outer face
depth_final = np.where(d_edge <= BAND, D_RIM, np.nan_to_num(th, nan=D_RIM))
final = Z >= (60.0 - depth_final)[:, :, None]
clash = int((final & body_comps).sum())
gap = edt(~body_comps, sampling=RES)
print(f"\nWITH THE RIM RULE (parting plane {D_RIM} mm below the face within {BAND:.0f} mm of the outer faces, the Voronoi surface inside):")
print(f"  lid region {final.sum() * vox:.0f} cm3; overlap with body components {clash} voxels; nearest body component to the lid {gap[final].min():.1f} mm (the layout's own clearance is {LY.CLR:.0f} mm)")
dd = np.where(final.any(axis=2), 60 - np.argmax(final, axis=2) * RES, np.nan)
print(f"  lid depth: min {np.nanmin(dd):.1f}, median {np.nanmedian(dd):.1f}, max {np.nanmax(dd):.1f} mm; rim depth is {D_RIM} mm all round, so the cell pocket leaves {D_RIM - CELL_T:.1f} mm of lid under the cells there")
# a shell of the lid: its outer area (the lid face, the side bands) plus the underside (the split surface)
face_a = final[:, :, -1].sum() * RES ** 2                                # the lid face
under_a = (final & ~np.roll(final, 1, axis=2) & (Z > 0)).sum() * RES ** 2   # voxel faces looking down into non-lid (the underside): lowest lid voxel in each column and steps
side = ((final & ~np.roll(final, 1, axis=0)).sum() + (final & ~np.roll(final, -1, axis=0)).sum() + (final & ~np.roll(final, 1, axis=1)).sum() + (final & ~np.roll(final, -1, axis=1)).sum()) * RES ** 2
cup = face_a + side                                                      # an open cup: the face and all the side walls (including the steps inside)
for t in (1.0, 1.5):
    print(f"  shell mass at {t} mm forged carbon (1.55 g/cm3): open cup (face and walls, underside open) {cup * t * 1.55e-3:.0f} g; closed (plus an underside plate over the lid footprint) {(cup + under_a) * t * 1.55e-3:.0f} g  [face {face_a / 100:.0f} cm2, walls {side / 100:.0f} cm2, underside {under_a / 100:.0f} cm2]")
print("  (the cells, the board and the screws are not in these figures)")
common = final                                                           # the figure shows the final lid
th = depth_final

fig, ax = plt.subplots(2, 3, figsize=(15, 9))
im = ax[0, 0].imshow(th.T, origin="lower", extent=(-70, 70, -70, 70), cmap="viridis"); ax[0, 0].set_title("depth of the final lid (rim rule) below its face (mm)\n(x across, y along; +y camera end up)", fontsize=9); plt.colorbar(im, ax=ax[0, 0], fraction=0.046)
def section(a, axis, val, title):
    idx = int(round((val + 70) / RES - 0.5)) if axis in "xy" else None
    if axis == "y": img = np.zeros((nz, nx, 3)); sl = (slice(None), idx, slice(None)); coords = (-70, 70)
    else: img = np.zeros((nz, ny, 3)); sl = (idx, slice(None), slice(None)); coords = (-70, 70)
    c, b, t, bt = common[sl].T, body_comps[sl].T, lid_top[sl].T, lid_bot[sl].T
    hfm = hf_t[sl].T
    img[:] = (0.92, 0.92, 0.92)
    img[hfm & ~c] = (0.80, 0.86, 0.95)          # top lid only (not in the common shape)
    img[hf_b_m[sl].T[::-1] & ~c] = (0.80, 0.86, 0.95) if False else img[hf_b_m[sl].T[::-1] & ~c]
    img[c] = (0.45, 0.65, 0.9)                  # the common lid shape (top)
    cb = common[sl][:, ::-1].T[::-1] if False else None
    img[b] = (0.85, 0.45, 0.35)                 # body components
    img[t | bt] = (0.2, 0.55, 0.3)              # lid components (cells, boards)
    a.imshow(img, origin="lower", extent=(coords[0], coords[1], 0, 60), aspect="equal"); a.set_title(title, fontsize=9)
section(ax[0, 1], "y", 0.5, "section at y = 0 (looking along y): blue = common top lid, red = body components,\ngreen = lid components (cells, board)")
section(ax[0, 2], "y", 40.5, "section at y = 40")
section(ax[1, 0], "x", 0.5, "section at x = 0 (y across, z up)")
section(ax[1, 1], "x", 48.0, "section at x = 48 (the camera window)")
section(ax[1, 2], "x", 60.5, "section at x = 60 (the hub housing)")
plt.tight_layout(); plt.savefig(LY.HERE.parent.parent / "docs" / "images" / "lid-split.png", dpi=90)
print("wrote docs/images/lid-split.png")
