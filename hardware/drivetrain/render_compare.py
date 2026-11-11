#!/usr/bin/env python3
"""Render the rover as modelled before the motor work against option C (thin-walled aluminium wheels with the wheel motor inside).

    .venv/bin/python hardware/drivetrain/render_compare.py OUT.png

Run after strut.py (struts.step) with the .venv.  Needs numpy, matplotlib, trimesh.  The body is a plain 140 x 140 x 60 mm box (no Hammond geometry), so the picture contains only our own parts.  Cutaway column: the wheels are cut at axle height (mesh slice) and the upper half removed; the motors are shown whole.

Before : wheel.py as it is (2.5 mm wall, 12 mm hub tube on a 6 mm axle, 83 g each).
C      : wall 1.0, end plate 1.0, cone 0.8, blades 0.8 mm (45 g); no hub tube; a 10 mm x 45 mm motor and gearhead (ECX SPEED 10 M 25.1 mm + GPX 10 A 4-stage
         19.8 mm) fixed to the strut tip, its front face as far toward the cone apex as the cone allows less a 3 mm pad, the tail poking inboard.
"""
import sys
import tempfile
from pathlib import Path

import matplotlib
import numpy as np
import trimesh
from build123d import *

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

HERE = Path(__file__).resolve().parent
HW = HERE.parent
sys.path.insert(0, str(HW / "body"))
sys.path.insert(0, str(HW / "strut"))
sys.path.insert(0, str(HW / "wheel"))
import body as E  # noqa: E402
import strut as S  # noqa: E402
import wheel as Wh  # noqa: E402

ALU, MOTOR, GEAR = "#cfd3d8", "#2b4c8c", "#b9a24a"
MOTOR_D, MOTOR_BODY_L, GEAR_L, PAD = 10.0, 25.1, 19.8, 3.0


def wheel_c():
    """Thin-walled wheel without hub tube: same outline, grousers and cone, thinner walls."""
    Wh.R_INNER, Wh.END_T, Wh.CONE_T, Wh.GROUSER_T = Wh.R_ROOT - 1.0, 1.0, 0.8, 0.8
    d = Wh.cylinder()
    with BuildSketch(Plane.XZ) as sk:
        Polygon((Wh.R_ROOT, Wh.L_DRUM), (Wh.R_ROOT, Wh.L_DRUM - Wh.CONE_T), (0, Wh.L_DRUM + Wh.H_CONE - Wh.CONE_T),
                (0, Wh.L_DRUM + Wh.H_CONE), align=None)
    cone = revolve(sk.sketch, Axis.Z)
    collar = Cylinder(Wh.COLLAR_D / 2, Wh.COLLAR_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, Wh.W)))
    return d + cone + collar


def motors_local():
    """Motor body and gearhead in the wheel's local frame (axis +z, inner face of the wheel at z = 0)."""
    z_front = (S.WHEEL_X[1] - Wh.CONE_T - Wh.H_CONE * (MOTOR_D / 2) / Wh.R_ROOT - PAD) - S.WHEEL_X[0]
    z_gear0 = z_front - GEAR_L
    z_tail = z_gear0 - MOTOR_BODY_L
    gear = Cylinder(MOTOR_D / 2, GEAR_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, z_gear0)))
    body = Cylinder(MOTOR_D / 2, MOTOR_BODY_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, z_tail)))
    return body, gear


def placed(shape_local):
    out = []
    for side in (1, -1):
        for d in (+1, -1):
            out.append(Wh.place(shape_local, d if side > 0 else -d, S.POSE_DEG, side))
    return out


def mesh_cut(m, z):
    """Remove everything above height z from a mesh (the CAD boolean fails on the thin-walled wheel). Open cut, no cap, so the inside shows."""
    return trimesh.intersections.slice_mesh_plane(m, plane_normal=[0, 0, -1], plane_origin=[0, 0, z], cap=False)


def mesh_of(shape, tmp, name):
    stl = Path(tmp) / f"{name}.stl"
    export_stl(shape, str(stl), tolerance=0.06, angular_tolerance=0.25)
    return trimesh.load(stl)


def view(el, az):
    el, az = np.radians(el), np.radians(az)
    d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    r = np.cross([0, 0, 1.0], d)
    r /= np.linalg.norm(r)
    return r, np.cross(d, r), d


def render(ax, items, el, az, title, xlim=None):
    r, u, d = view(el, az)
    polys, cols, depth = [], [], []
    light = np.array([0.5, -0.4, 0.8])
    light /= np.linalg.norm(light)
    for m, colour in items:
        base = np.array(matplotlib.colors.to_rgb(colour))
        for f, nrm in zip(m.faces, m.face_normals):
            if nrm @ d < -0.05:
                continue
            t = m.vertices[f]
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
    ax.set_title(title, fontsize=9)


def main(out_png):
    # featureless body: 140 x 140 x 60 mm, floor at z = 0 (as in body.py), no Hammond geometry
    base = [(Box(140, 140, 60, align=(Align.CENTER, Align.CENTER, Align.MIN)), "#8d97a3")]
    struts = (import_step(HW / "strut/out/struts.step"), "#c9a46a")
    w_before = Wh.wheel_local()
    wb = placed(w_before)
    w_c = wheel_c()
    wc = placed(w_c)
    m_body, m_gear = motors_local()
    mb, mg = placed(m_body), placed(m_gear)
    print(f"wheel mass: before {w_before.volume * 2.7e-3:.0f} g, C {w_c.volume * 2.7e-3:.0f} g (aluminium); "
          f"motor tail {m_body.bounding_box().min.Z:.1f} mm from the wheel's inner face")
    with tempfile.TemporaryDirectory() as tmp:
        M = lambda s, n: mesh_of(s, tmp, n)
        base_m = [(M(s, f"b{i}"), c) for i, (s, c) in enumerate(base)]
        strut_m = (M(struts[0], "struts"), struts[1])
        zc = wb[0].bounding_box().center().Z          # axle height (all four wheels share it at this pose)
        wb_full, wc_full = M(Compound(wb), "wb"), M(Compound(wc), "wc")
        wb_cut, wc_cut = mesh_cut(wb_full, zc), mesh_cut(wc_full, zc)
        mot_cut = [(M(Compound(mb), "mb"), MOTOR), (M(Compound(mg), "mg"), GEAR)]     # motors shown whole
        rows = [("Before (as modelled)", [(wb_full, ALU)], [(wb_cut, ALU)], []),
                ("Option C (thin wheel, motor inside)", [(wc_full, ALU)], [(wc_cut, ALU)] + mot_cut, [])]
        fig, axs = plt.subplots(2, 3, figsize=(16, 9.5))
        for i, (name, full, cut, extra) in enumerate(rows):
            render(axs[i, 0], base_m + [strut_m] + full, 24, -38, f"{name}: default stance")
            render(axs[i, 1], base_m + [strut_m] + full, 0, 0, f"{name}: end view from +x")
            render(axs[i, 2], base_m + [strut_m] + cut, 62, -90, f"{name}: cutaway, top half of each wheel removed")
        plt.tight_layout()
        plt.savefig(out_png, dpi=75)
    print("wrote", out_png)


if __name__ == "__main__":
    main(sys.argv[1])
