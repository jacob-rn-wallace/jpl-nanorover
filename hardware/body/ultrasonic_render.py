#!/usr/bin/env python3
"""Render of the ultrasonic receiver sites on the carbon body block with the struts and wheels at the default stance,
plus a ray test of each site's 90 degree cone (assumed, 40 kHz capsules, 10 mm) against the struts, wheels and body.

Run from the repository root (venv; body_block.step from block.py, struts and wheels from strut.py and wheel.py):
    .venv/bin/python hardware/body/ultrasonic_render.py
Writes docs/images/ultrasonic-sites.png.  Sites are proposals (docs/positioning.md section 8), not placed parts.
The cone half-angle (45 deg) and the capsule size (10 mm) are from memory, not a datasheet.
"""
import importlib.util
import tempfile
from pathlib import Path

import matplotlib
import numpy as np
import trimesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HW = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preview", HW / "assembly" / "preview.py")
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

GAP = (140 - 26 - 87.2) / 3
HALF = np.radians(45)
# (name, position on the face (mm), outward normal); the body spans x, y in -70..70 and z in 0..60, hub axis at z = 30
SITES = [("hub +x, +y side", (70, 21.5, 30), (1, 0, 0)), ("hub +x, -y side", (70, -21.5, 30), (1, 0, 0)),
         ("hub -x, +y side", (-70, 21.5, 30), (-1, 0, 0)), ("hub -x, -y side", (-70, -21.5, 30), (-1, 0, 0)),
         ("end +y, gap by window", (70 - GAP - 26 - GAP / 2, 70, 30), (0, 1, 0)),
         ("end -y, gap by antenna", (-(70 - GAP - 26 - GAP / 2), -70, 30), (0, -1, 0))]


def cyl(pos, nrm, r=5.0, h=3.0, out=0.0):
    """a capsule face marker: a short cylinder on the face, axis along the outward normal"""
    m = trimesh.creation.cylinder(radius=r, height=h, sections=32)
    z = np.array([0, 0, 1.0]); n = np.array(nrm, float)
    T = trimesh.geometry.align_vectors(z, n)
    m.apply_transform(T)
    m.apply_translation(np.array(pos, float) + n * (h / 2 + out))
    return m


def rays_for(pos, nrm, elev_deg, n=37):
    """unit directions in the cone: azimuth -45..45 about the face normal in the horizontal plane, at one elevation"""
    nrm = np.array(nrm, float); side = np.cross([0, 0, 1.0], nrm)
    e = np.radians(elev_deg); out = []
    for a in np.linspace(-HALF, HALF, n):
        d = np.cos(e) * (np.cos(a) * nrm + np.sin(a) * side) + np.sin(e) * np.array([0, 0, 1.0])
        out.append(d)
    return np.array(out)


class Rays:
    """Moller-Trumbore, vectorised over the triangles (trimesh's own intersector needs rtree, which is not installed here)"""
    def __init__(self, mesh):
        t = mesh.triangles
        self.v0 = t[:, 0]; self.e1 = t[:, 1] - t[:, 0]; self.e2 = t[:, 2] - t[:, 0]

    def first_hit(self, org, d):
        """distance to the first hit along unit direction d from org, or inf"""
        h = np.cross(d, self.e2); a = (self.e1 * h).sum(1)
        ok = np.abs(a) > 1e-12
        f = np.where(ok, 1.0 / np.where(ok, a, 1), 0)
        s = org - self.v0; u = f * (s * h).sum(1)
        q = np.cross(s, self.e1); v = f * (q * d).sum(1)
        t = f * (self.e2 * q).sum(1)
        m = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
        return t[m].min() if m.any() else np.inf


def main():
    with tempfile.TemporaryDirectory() as tmp:
        body = pv.mesh_of(HW / "body/out/body_block.step", tmp)
        struts = pv.mesh_of(HW / "strut/out/struts.step", tmp)
        wheels = pv.mesh_of(HW / "wheel/out/wheels.step", tmp)
    occ = trimesh.util.concatenate([body, struts, wheels])
    inter = Rays(occ)
    # ---- ray test: fraction of each site's cone that is clear for 400 mm, at three elevations ----
    print("site                           elev -10   0   +10   (percent of the 90 degree cone clear to 400 mm)")
    clear0 = {}
    for name, pos, nrm in SITES:
        row = []
        for el in (-10, 0, 10):
            org = np.array(pos, float) + np.array(nrm) * 0.2
            ds = rays_for(pos, nrm, el)
            blocked = np.array([inter.first_hit(org, d) < 400 for d in ds])
            row.append(100 * (1 - blocked.mean()))
            if el == 0: clear0[name] = blocked
        print(f"{name:30s} {row[0]:6.0f} {row[1]:5.0f} {row[2]:6.0f}")
    # ---- render ----
    # capsules are flush in 10 mm holes: a black aperture inside a coloured ring (0.2 and 0.35 mm proud, only so the painter's renderer shows them)
    hub = [(p, n) for (nm, p, n) in SITES if nm.startswith("hub")]; end = [(p, n) for (nm, p, n) in SITES if nm.startswith("end")]
    ring_h = trimesh.util.concatenate([cyl(p, n, r=6.3, h=0.2) for p, n in hub])
    ring_e = trimesh.util.concatenate([cyl(p, n, r=6.3, h=0.2) for p, n in end])
    holes = trimesh.util.concatenate([cyl(p, n, r=5.0, h=0.2, out=0.15) for p, n in hub + end])
    parts = [(Path("body_block.step"), "#3a3f45", 0), (Path("struts.step"), "#c9a46a", 0), (Path("wheels.step"), "#cfd3d8", 0),
             (Path("ring_hub.step"), "#10c4d6", 0), (Path("ring_end.step"), "#f06a1d", 0), (Path("apertures.step"), "#020304", 0)]
    pv.PARTS = parts
    meshes = [body, struts, wheels, ring_h, ring_e, holes]
    names = {p.stem for p, _, _ in parts}
    fig, axs = plt.subplots(2, 2, figsize=(13, 10.5))
    pv.render(axs[0, 0], meshes, 22, 35, names, title="flush capsule holes: cyan ring hub face, orange ring end face (does not fit)")
    pv.render(axs[0, 1], meshes, 0, 0, names, title="from +x: the struts cover the hub-face sites")
    pv.render(axs[1, 0], meshes, 22, 215, names, title="opposite corner: -x hub face, -y comms end")
    ax = axs[1, 1]
    pv.render(ax, meshes, 89.9, -90, names, title="plan: 90 deg cones, green clear, red blocked within 400 mm")
    r, u, d = pv.view(89.9, -90)
    for name, pos, nrm in SITES:
        org = np.array(pos, float) + np.array(nrm) * 0.2
        ds = rays_for(pos, nrm, 0)
        hitd = {i: inter.first_hit(org, d) for i, d in enumerate(ds) if inter.first_hit(org, d) < 400}
        for i, dd in enumerate(ds):
            L = min(hitd.get(i, 400.0), 400.0)
            a, b = org, org + dd * L
            ax.plot([a @ r, b @ r], [a @ u, b @ u], color="#d33" if i in hitd and hitd[i] < 400 else "#2a2", lw=0.5, alpha=0.7)
    ax.relim(); ax.set_xlim(-300, 300); ax.set_ylim(-300, 300); ax.set_aspect("equal")
    plt.tight_layout()
    out = HW.parent / "docs" / "images" / "ultrasonic-sites.png"
    plt.savefig(out, dpi=80)
    print("wrote", out)


if __name__ == "__main__":
    main()
