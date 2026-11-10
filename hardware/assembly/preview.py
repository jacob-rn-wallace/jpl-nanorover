#!/usr/bin/env python3
"""Rough software render of the rover model for docs/images/rover-preview.png.

Run from the repository root, after body.py, strut.py and wheel.py:
    .venv/bin/python hardware/assembly/preview.py

Needs numpy, matplotlib and trimesh as well as build123d (hardware/requirements.txt).  The renderer is a small
painter's-algorithm projector, so shading is approximate and nine tapered faces of Hammond's casting do not mesh and
show as small holes.  The STEP files are fine.
"""
import tempfile
from pathlib import Path

import matplotlib
import numpy as np
import trimesh
from build123d import export_stl, import_step

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

HW = Path(__file__).resolve().parents[1]
IMG = HW.parent / "docs" / "images" / "rover-preview.png"
# (file, colour, explode multiplier)
PARTS = [(HW / "body/out/body_hammond.step", "#8d97a3", 0), (HW / "body/out/oring.step", "#1a1a1a", 1),
         (HW / "body/out/lid_plate.step", "#b4bdc7", 2), (HW / "body/out/hub_studs.step", "#d6a84a", 0),
         (HW / "body/out/hub_orings_and_nuts.step", "#3a3a3a", 0), (HW / "body/out/window_pane.step", "#101820", 0), (HW / "strut/out/struts.step", "#c9a46a", 0),
         (HW / "wheel/out/wheels.step", "#cfd3d8", 0)]
BASE = {"body_hammond", "oring", "lid_plate", "hub_studs", "hub_orings_and_nuts", "window_pane"}


def mesh_of(path, tmp):
    stl = Path(tmp) / (path.stem + ".stl")
    export_stl(import_step(path), str(stl), tolerance=0.05, angular_tolerance=0.2)
    return trimesh.load(stl)


def view(el, az):
    el, az = np.radians(el), np.radians(az)
    d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    r = np.cross([0, 0, 1.0], d)
    r /= np.linalg.norm(r)
    return r, np.cross(d, r), d


def render(ax, meshes, el, az, names, explode=0, title=None):
    r, u, d = view(el, az)
    polys, cols, depth = [], [], []
    light = np.array([0.5, -0.4, 0.8])
    light /= np.linalg.norm(light)
    for (path, colour, k), m in zip(PARTS, meshes):
        if path.stem not in names:
            continue
        v = m.vertices.copy()
        v[:, 2] += explode * k
        base = np.array(matplotlib.colors.to_rgb(colour))
        for f, nrm in zip(m.faces, m.face_normals):
            if nrm @ d < -0.05:
                continue
            t = v[f]
            polys.append(np.c_[t @ r, t @ u])
            cols.append(tuple(np.clip(base * (0.45 + 0.55 * max(0, nrm @ light)), 0, 1)))
            depth.append((t @ d).mean())
    order = np.argsort(depth)
    ax.add_collection(PolyCollection([polys[i] for i in order], facecolors=[cols[i] for i in order],
                                     edgecolors=[cols[i] for i in order], linewidths=0.3))
    a = np.concatenate(polys)
    ax.set_xlim(a[:, 0].min() - 5, a[:, 0].max() + 5)
    ax.set_ylim(a[:, 1].min() - 5, a[:, 1].max() + 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        meshes = [mesh_of(p, tmp) for p, _, _ in PARTS]
    everything = {p.stem for p, _, _ in PARTS}
    fig, axs = plt.subplots(2, 2, figsize=(13, 10.5))
    render(axs[0, 0], meshes, 26, 125, BASE, title="box, lid plate, hub stud and the window face (+y): 140 x 140 x 60")
    render(axs[0, 1], meshes, 28, -55, BASE, explode=28, title="exploded: box, O-ring, lid plate (hubs stay on the box)")
    render(axs[1, 0], meshes, 24, -38, everything, title="struts and wheels, default stance (25 deg below horizontal)")
    render(axs[1, 1], meshes, 0, 0, everything, title="side view from +x: 65 mm wheels, 25 deg stance")
    plt.tight_layout()
    IMG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(IMG, dpi=80)
    print("wrote", IMG)


if __name__ == "__main__":
    main()
