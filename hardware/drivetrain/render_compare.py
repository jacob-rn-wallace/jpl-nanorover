#!/usr/bin/env python3
"""Render the rover as modelled before the motor work against option C (thin-walled aluminium wheels with the wheel motor inside).

    .venv/bin/python hardware/drivetrain/render_compare.py OUT.png

Run after strut.py (struts.step) with the .venv.  Needs numpy, matplotlib, trimesh.  The body is a plain 140 x 140 x 60 mm box (no Hammond geometry), so the picture contains only our own parts.  Cutaway column: the wheels are cut at axle height (mesh slice) and the upper half removed; the motors are shown whole.

Before : wheel preset "v1" (2.5 mm wall, 12 mm hub tube on a 6 mm axle, 78 g each) with the struts in TIP_MODE "axle".
C      : wheel preset "thin" (1.0 mm wall, 0.8 mm cone and blades, no hub tube, 34 g each) with the struts in TIP_MODE "motor": a 10 mm x 44.9 mm motor and gearhead
         (ECX SPEED 10 M + GPX 10 A 4-stage) carried by the strut tip, tail poking inboard (strut.py has its dimensions).
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

ALU, GEAR = "#cfd3d8", "#3f64b0"


def struts_posed():
    """All four struts at the default pose with the current S.TIP_MODE."""
    out = []
    for side in (1, -1):
        for (bossr, platr, d) in ((S.A_BOSS, S.A_PLATE, +1), (S.B_BOSS, S.B_PLATE, -1)):
            st = S.posed(S.strut(bossr, platr, S.WHEEL_X[0], d), d, S.POSE_DEG)
            out.append(st.mirror(Plane.YZ) if side < 0 else st)
    return Compound(out)


def motors_posed():
    out = []
    for side in (1, -1):
        for d in (+1, -1):
            m = S.posed(S.motor(d), d, S.POSE_DEG)
            out.append(m.mirror(Plane.YZ) if side < 0 else m)
    return out


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
    box = (Box(140, 140, 60, align=(Align.CENTER, Align.CENTER, Align.MIN)), "#8d97a3")   # featureless body, floor at z = 0
    # before: preset v1 wheel (hub tube on a 6 mm axle) and the 6 mm axle stub on the struts
    S.TIP_MODE = "axle"
    Wh.use_preset("v1")
    w_before = Wh.wheel_local()
    wb = Compound(placed(w_before))
    st_before = struts_posed()
    # C: preset thin wheel, the strut tips carry the wheel motors
    S.TIP_MODE = "motor"
    Wh.use_preset("thin")
    w_c = Wh.wheel_local()
    wc = Compound(placed(w_c))
    st_c = struts_posed()
    mot = motors_posed()
    print(f"wheel mass (aluminium): before {w_before.volume * 2.7e-3:.0f} g, C {w_c.volume * 2.7e-3:.0f} g; motor tail {S.MOTOR_TAIL:.1f} mm |x|")
    with tempfile.TemporaryDirectory() as tmp:
        M = lambda s_, n: mesh_of(s_, tmp, n)
        base_m = [(M(box[0], "box"), box[1])]
        zc = wb.bounding_box().center().Z               # axle height (all four wheels share it at this pose)
        wb_full, wc_full = M(wb, "wb"), M(wc, "wc")
        wb_cut, wc_cut = mesh_cut(wb_full, zc), mesh_cut(wc_full, zc)
        sb_m, sc_m = (M(st_before, "sb"), "#c9a46a"), (M(st_c, "sc"), "#c9a46a")
        # motors: body (dark) and gearhead (bright) as one piece here; cut nothing, shown whole
        mot_m = [(M(Compound(mot), "mot"), GEAR)]
        rows = [("Before (as modelled)", sb_m, [(wb_full, ALU)], [(wb_cut, ALU)]),
                ("Option C (thin wheel, motor inside)", sc_m, [(wc_full, ALU)], [(wc_cut, ALU)] + mot_m)]
        fig, axs = plt.subplots(2, 3, figsize=(16, 9.5))
        for i, (name, st, full, cut) in enumerate(rows):
            render(axs[i, 0], base_m + [st] + full, 24, -38, f"{name}: default stance")
            render(axs[i, 1], base_m + [st] + full, 0, 0, f"{name}: end view from +x")
            render(axs[i, 2], base_m + [st] + cut, 62, -90, f"{name}: cutaway, top half of each wheel removed")
        plt.tight_layout()
        plt.savefig(out_png, dpi=75)
    print("wrote", out_png)


if __name__ == "__main__":
    main(sys.argv[1])
