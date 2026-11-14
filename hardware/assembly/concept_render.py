#!/usr/bin/env python3
"""Exterior concept render of the interpreted nanorover: carbon body, IXOLAR cells, windows, struts and wheels.

Run from the repository root (venv; strut.py and wheel.py first):
    .venv/bin/python hardware/assembly/concept_render.py
Writes docs/images/rover-concept.png.  This is NOT a CAD part: the body is a 140 x 140 x 60 mm block with 0.8 mm edges (the real part,
a forged-carbon shell, is not modelled; hardware/body/block.py is only the cavity volume) with the cells, windows and hub holes laid on its
faces as thin slabs from the same numbers as layout.py, cell_pocket.py and cell_endface.py.  Struts and wheels are the CAD parts at the 25 degree stance.
Not drawn: the lid screws and seals, the hub studs and rings, the lamp, the edge finish, any texture.  Same rough painter's renderer as preview.py.
"""
import importlib.util
import tempfile
from pathlib import Path

import matplotlib
import matplotlib.collections  # noqa: F401
import numpy as np
import trimesh
from build123d import Align, Box, export_stl

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HW = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preview", HW / "assembly" / "preview.py")
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

GAP = (140 - 26 - 87.2) / 3
T = 0.25                                     # slab thickness: cells and panes sit this far proud (flush in reality; the renderer needs a gap)


def fine(m, size=3.0):
    """split big triangles so the painter's depth sort works between the body and the thin overlays"""
    v, f = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=size)
    return trimesh.Trimesh(v, f)


def forged_texture(m, length=15.0, width=5.0, seed=11):
    """Forged-carbon look: random chopped chips, elongated (length x width) with random 3D orientation, a 3D Voronoi in each chip's own stretched metric,
    cut by the body's faces so the pattern runs round the edges.  Each chip has its own tone and a brightness ramp along its length (the sheen of a
    fibre bundle), and is a little darker at its boundary.  Returns one brightness gain per face."""
    from scipy.spatial import cKDTree
    rng = np.random.default_rng(seed)
    lo, hi = m.bounds[0] - length, m.bounds[1] + length
    n = int(np.prod(hi - lo) / (length * width * width) * 1.6)
    seeds = lo + rng.random((n, 3)) * (hi - lo)
    tone = np.clip(rng.normal(1.0, 0.24, n), 0.55, 1.55)
    ang = rng.random(n) * 2 * np.pi; phi = np.arccos(2 * rng.random(n) - 1)
    dirs = np.c_[np.sin(phi) * np.cos(ang), np.sin(phi) * np.sin(ang), np.cos(phi)]
    c = m.triangles_center
    _, cand = cKDTree(seeds).query(c, k=14)                               # nearest few by plain distance, then pick by the chips' own metric
    dv = c[:, None, :] - seeds[cand]
    along = (dv * dirs[cand]).sum(2)
    perp2 = (dv ** 2).sum(2) - along ** 2
    metric = np.sqrt((along / length) ** 2 + np.maximum(perp2, 0) / width ** 2)
    order = np.argsort(metric, axis=1)
    i0 = np.take_along_axis(cand, order[:, :1], 1)[:, 0]
    m0 = np.take_along_axis(metric, order[:, :1], 1)[:, 0]; m1 = np.take_along_axis(metric, order[:, 1:2], 1)[:, 0]
    ramp = np.take_along_axis(along, order[:, :1], 1)[:, 0] / length      # -0.5 .. 0.5 along the chip
    edge = np.clip((m1 - m0) / 0.12, 0, 1)                                # 0 on a boundary
    gain = tone[i0] * (1 + 0.5 * ramp) * (0.72 + 0.28 * edge) * (1 + 0.04 * rng.standard_normal(len(c)))
    return np.clip(gain, 0.35, 1.9)


def slab(face, a0, a1, b0, b1):
    """a thin rectangle on a face; face is '+z', '-z', '+y', '-y'; (a, b) are x and y on the lids, x and z on the end faces"""
    if face in ("+z", "-z"):
        z0 = 60.0 if face == "+z" else -T
        ext, pos = (a1 - a0, b1 - b0, T), ((a0 + a1) / 2, (b0 + b1) / 2, z0 + T / 2)
    else:
        y0 = 70.0 if face == "+y" else -70.0 - T
        ext, pos = (a1 - a0, T, b1 - b0), ((a0 + a1) / 2, y0 + T / 2, (b0 + b1) / 2)
    m = trimesh.creation.box(extents=ext); m.apply_translation(pos); return m


def disc(face, cx, cz, r):
    m = trimesh.creation.cylinder(radius=r, height=T, sections=48)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))   # axis along y
    m.apply_translation((cx, (70.0 + T / 2) if face == "+y" else (-70.0 - T / 2), cz)); return m


def lid_cells(face):
    out = []
    for k in range(3):
        x0 = -66.75 + 44.5 * k
        out += [slab(face, x0 + .15, x0 + 44.35, 45, 66.5), slab(face, x0 + .15, x0 + 44.35, -66.5, -45)]
    out += [slab(face, -66.75, -26.75, -45, 45), slab(face, 26.75, 66.75, -45, 45), slab(face, -26, 26, -44.5, 44.5)]
    return out


def end_cells(face):
    start = (70 - 2 * GAP - 26 - 87.2) if face == "+y" else (-70 + 2 * GAP + 26)
    return [slab(face, start + 21.8 * k, start + 21.8 * k + 21.5, 7.75, 52.25) for k in range(4)]


BIAS = {"cells": 1.5, "bezel": 1.8, "glass": 2.0, "plug": 1.5, "hood": 2.3, "lens": 2.4, "leds": 2.5, "tof": 2.6}     # mm toward the viewer: the thin overlays on the body faces must sort after the body


TEX = {}
UNIT = {"glass", "bezel", "hood", "lens", "leds", "tof"}      # overlays on the window: sorted as one unit each, so coplanar discs do not interleave


def render(ax, meshes, el, az, title, lims=None):
    r, u, d = pv.view(el, az)
    light = np.array([0.5, -0.4, 0.8]); light /= np.linalg.norm(light)
    polys, cols, depth = [], [], []
    for (path, colour, _k), m in zip(pv.PARTS, meshes):
        base = np.array(matplotlib.colors.to_rgb(colour)); bias = BIAS.get(path.stem, 0.0)
        gains = TEX.get(path.stem)
        for k, (f, nrm) in enumerate(zip(m.faces, m.face_normals)):
            if nrm @ d < -0.05:
                continue
            t = m.vertices[f]
            polys.append(np.c_[t @ r, t @ u]); depth.append(((t @ d).mean() if path.stem not in UNIT else (m.vertices @ d).mean()) + bias)
            cols.append(tuple(np.clip(base * (0.45 + 0.55 * max(0, nrm @ light)) * (1.0 if gains is None else gains[k]), 0, 1)))
    order = np.argsort(depth)
    ax.add_collection(matplotlib.collections.PolyCollection([polys[i] for i in order], facecolors=[cols[i] for i in order], edgecolors=[cols[i] for i in order], linewidths=0.3))
    a = np.concatenate(polys)
    ax.set_xlim(a[:, 0].min() - 5, a[:, 0].max() + 5); ax.set_ylim(a[:, 1].min() - 5, a[:, 1].max() + 5)
    if lims: ax.set_xlim(lims[0], lims[1]); ax.set_ylim(lims[2], lims[3])
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=10)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        b = Box(140, 140, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))
        b = b.fillet(0.8, b.edges())
        stl = Path(tmp) / "body.stl"; export_stl(b, str(stl), tolerance=0.05, angular_tolerance=0.2)
        body = trimesh.load(stl)
        body = fine(body, 1.6)
        struts = pv.mesh_of(HW / "strut/out/struts.step", tmp)
        wheels = pv.mesh_of(HW / "wheel/out/wheels.step", tmp)
    cells = fine(trimesh.util.concatenate(lid_cells("+z") + lid_cells("-z") + end_cells("+y") + end_cells("-y")))
    wx = 70 - (GAP + 13)
    glass = fine(disc("+y", wx, 30, 13.0))                                    # the cover glass: the original 26 mm circle again (LED ring instead of the beamsplitter)
    bezel = fine(disc("+y", wx, 30, 14.6)); bezel.apply_translation((0, -0.12, 0))
    hood = fine(disc("+y", wx, 30, 8.2))                                      # black mask ring and lens hood against the glass
    lens = fine(disc("+y", wx, 30, 6.3))                                      # the M12 lens front
    leds = fine(trimesh.util.concatenate([disc("+y", wx + 8.5 * np.cos(np.radians(90 + 45 * k)), 30 + 8.5 * np.sin(np.radians(90 + 45 * k)), 1.3) for k in range(1, 8)]))   # 7 white LEDs, top slot left free
    tof = fine(slab("+y", wx - 3.2, wx + 3.2, 40.5 - 1.5, 40.5 + 1.5))      # the ranging sensor (6.4 x 3.0 mm) in the ring's top slot
    plug = fine(slab("-y", -(70 - (GAP + 13)) - 13.5, -(70 - (GAP + 13)) + 13.5, 30 - 13.5, 30 + 13.5))
    parts = [(Path("body.step"), "#34383e", 0), (Path("struts.step"), "#b9b4aa", 0), (Path("wheels.step"), "#cdd1d6", 0),
             (Path("cells.step"), "#161a22", 0), (Path("bezel.step"), "#7a7f86", 0), (Path("glass.step"), "#0b0e13", 0), (Path("plug.step"), "#3f4a46", 0),
             (Path("hood.step"), "#0d0f13", 0), (Path("lens.step"), "#010203", 0), (Path("leds.step"), "#17150f", 0), (Path("tof.step"), "#4a5262", 0)]
    pv.PARTS = parts
    meshes = [body, struts, wheels, cells, bezel, glass, plug, hood, lens, leds, tof]
    TEX["body"] = forged_texture(body)
    fig, axs = plt.subplots(2, 2, figsize=(14, 10.5))
    render(axs[0, 0], meshes, 24, 38, title="camera end (+y), +x hub side, top lid")
    render(axs[0, 1], meshes, 24, 218, title="comms end (-y), -x hub side")
    render(axs[1, 0], meshes, 89.9, -90, title="top lid: IXOLAR cells in one pocket, camera end up")
    render(axs[1, 1], meshes, 0, 90, title="from +y: the 26 mm window (lens, LED ring, ranging sensor) and the end-face cells")
    for a in axs.flat: a.set_facecolor("#e9ecef")
    fig.patch.set_facecolor("#e9ecef")
    plt.tight_layout()
    f2, a2 = plt.subplots(figsize=(11, 7.2)); f2.patch.set_facecolor("#e9ecef"); a2.set_facecolor("#e9ecef")
    r, u, d = pv.view(24, 38)
    ctr = np.array([55.0, 70.0, 45.0])
    cx, cy = ctr @ r, ctr @ u
    render(a2, meshes, 24, 38, "close-up: forged-carbon body (chopped chips, about 15 x 5 mm), IXOLAR cells, 26 mm window (camera lens in the centre, a ring of LEDs round it, the ranging sensor in the top slot)", lims=(cx - 62, cx + 62, cy - 40, cy + 40))
    f2.savefig(HW.parent / "docs" / "images" / "rover-concept-detail.png", dpi=110, facecolor=f2.get_facecolor())
    f3, a3 = plt.subplots(figsize=(9, 7)); f3.patch.set_facecolor("#e9ecef"); a3.set_facecolor("#e9ecef")
    r3, u3, d3 = pv.view(0, 90)
    wp = np.array([wx, 70.0, 30.0]); cxx, cyy = wp @ r3, wp @ u3
    render(a3, meshes, 0, 90, "the 26 mm window from +y: lens, LED ring (off, behind a smoked dead-front), ranging sensor in the top slot", lims=(cxx - 36, cxx + 36, cyy - 26, cyy + 26))
    sp = np.array([wx, 70.0, 40.5]); a3.annotate("ranging sensor\n(VL53L5CX, 6.4 x 3 mm)", (sp @ r3, sp @ u3), (cxx - 30, cyy + 20), fontsize=9, arrowprops=dict(arrowstyle="->"), ha="center", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.5", alpha=0.92))
    cp = np.array([wx, 70.0, 30.0 - 4]); a3.annotate("camera lens (M12)\nand hood", (cp @ r3, cp @ u3), (cxx, cyy - 25), fontsize=9, arrowprops=dict(arrowstyle="->"), ha="center", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.5", alpha=0.92))
    gp = np.array([wx - 13.0 * 0.7, 70.0, 30.0 + 13.0 * 0.7]); a3.annotate("cover glass\n(26 mm)", (gp @ r3, gp @ u3), (cxx + 26, cyy + 20), fontsize=9, arrowprops=dict(arrowstyle="->"), ha="center", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.5", alpha=0.92))
    f3.savefig(HW.parent / "docs" / "images" / "rover-concept-window.png", dpi=110, facecolor=f3.get_facecolor())
    out = HW.parent / "docs" / "images" / "rover-concept.png"
    fig.savefig(out, dpi=80, facecolor=fig.get_facecolor())
    print("wrote", out)


if __name__ == "__main__":
    main()
