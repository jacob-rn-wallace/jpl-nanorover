#!/usr/bin/env python3
"""Pictures of a to_run.py result: .venv-to/bin/python hardware/body/to_plot.py out/to_result_n36_m40.npz [out.png]"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src = Path(sys.argv[1]); dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[2] / "docs" / "images" / f"to-{src.stem.replace('to_result_', '')}.png"
r = np.load(src)
rho, des, sol, voi, h = r["rho_h"], r["design_h"], r["solid_h"], r["void_h"], float(r["h"])
n, _, nzh = rho.shape
z0 = 30.0
mat = np.where(des, rho, 0.0)
print(f"result {src.name}: {r['mass_g']:.1f} g added; grey cells (0.2 < rho < 0.8): {100 * ((mat > 0.2) & (mat < 0.8)).sum() / max(des.sum(), 1):.0f}% of the design cells; solid (rho > 0.8): {100 * (mat > 0.8).sum() / max(des.sum(), 1):.0f}%")
ext = [-69, 69, -69, 69]
def layer(k):
    img = np.ones((n, n, 3))
    img[sol[:, :, k].T] = (0.55, 0.55, 0.6)
    img[voi[:, :, k].T] = (1, 1, 1)
    m = mat[:, :, k].T
    col = np.stack([1 - 0.85 * m, 1 - 0.55 * m, 1 - 0.25 * m], axis=2)
    mk = des[:, :, k].T
    img[mk] = col[mk]
    return img
fig, ax = plt.subplots(2, 3, figsize=(15, 10))
ks = [0, nzh // 3, 2 * nzh // 3, nzh - 1]
for a, k in zip(ax.flat[:4], ks):
    a.imshow(layer(k), origin="lower", extent=ext, interpolation="nearest")
    a.set_title(f"z = {z0 + (k + 0.5) * h:.0f} mm (upper half; the lower half is the mirror)", fontsize=9)
    a.set_xlabel("x (mm), +x right"); a.set_ylabel("y (mm), camera end at the top")
a = ax.flat[4]
th = (mat * h).sum(axis=2).T
im = a.imshow(th, origin="lower", extent=ext, cmap="viridis"); a.set_title("added material, thickness in the upper half (mm)", fontsize=9); plt.colorbar(im, ax=a, shrink=0.8)
a = ax.flat[5]; a.axis("off")
a.text(0, 1, f"{src.stem}\nadded structure {float(r['mass_g']):.1f} g (both halves)\ncell {h:.2f} mm\n\nlegend: blue = added material,\ndark grey = fixed solid (skin, rims, bosses, rings, seat walls),\nwhite = fixed void or empty.\n\ncompliance against the start:\n" + "\n".join(f"  {nm}: {c / c0:.2f}" for nm, c, c0 in zip(r["names"], r["c"], r["c0"])), va="top", fontsize=9, family="monospace")
fig.tight_layout(); fig.savefig(dst, dpi=110)
print("wrote", dst)
