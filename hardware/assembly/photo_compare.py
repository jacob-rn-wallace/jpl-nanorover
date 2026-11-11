#!/usr/bin/env python3
"""Render the CAD rover from the camera of NanoRover-hires.original.jpg (the silver unit) and lay it over the photo.

Run from the repository root, after body.py, hub.py, strut.py and wheel.py:
    .venv/bin/python hardware/assembly/photo_compare.py

Needs numpy, scipy, trimesh, pillow and build123d, and the private companion repository beside this one (the photo and the camera
saved by the photo-measurement scripts, `analysis/photo-measure/p2_cam.npz`).  The result contains the photo (NASA/JPL, usage terms
unchecked), so it is written into the private repository, never into this one.

Pose (what is fitted and what is not):
  * Camera: focal length 1923 px and the three body directions (hub axis, long axis, top-face normal) from the vanishing points of
    the cell edges (docs/photo-measurements.md).  The CAD axes map to them as x = -d2 (the visible side face is +x), y = -d1 (the
    window end is +y), z = -n (up).
  * Strut angles and position: from the 3D centres of the two wheel cone rims on the visible side (the photo scripts get them from the
    rim's apparent size, 169 px and 145 px, for a 59.5 mm rim, the CAD wheel's own) and the hub cap pixel, as in sil_scale.py.  The
    angles are the photo's; the position puts the CAD hub axis through the photo's hub axis and the CAD wheel plane at the photo's.
  * The two struts on the far side are given the angles of their partners on the near side (mirror symmetry).  They are hidden in
    the photo apart from one wheel, so this is a guess.
  * The CAD is a 140 x 140 x 60 mm body with 70 mm struts, the silver unit is about 125 x 140 x 55 mm with struts about 78 mm
    (docs/photo-measurements.md): do not expect the body to match, and the wheel centres cannot both match.
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from build123d import Axis, Compound, Location, Plane, Sphere, export_stl, import_step

HERE = Path(__file__).resolve().parent
HW = HERE.parent
for sub in ("body", "strut", "wheel"):
    sys.path.insert(0, str(HW / sub))
import body as E  # noqa: E402
import strut as S  # noqa: E402
import wheel as W  # noqa: E402

PRIV = HW.parent.parent / "jpl-nanorover-private"
PHOTO = PRIV / "images" / "NanoRover-hires.original.jpg"
CAM = PRIV / "analysis" / "photo-measure" / "p2_cam.npz"
OUT_DIR = PRIV / "analysis" / "photo-measure"

# photo measurements of the two wheel cone rims on the visible (left) side: pixel of the rim centre, apparent rim diameter in px
NEAR = ((312.5, 627.5), 169.0, (272.5, 636.0))     # front-left wheel (window end), the pixel the axle points toward on the outside
BACK = ((156.8, 433.7), 145.0, None)                # back-left wheel

z = np.load(CAM)
K, d1, d2, n = z["K"], z["d1"], z["d2"], z["n"]
Ki = np.linalg.inv(K)
f = K[0, 0]
R = np.column_stack([-d2, -d1, -n])               # CAD axes in the camera frame


def rim_centre_cam(center_px, base_len_px, D=2 * W.R_ROOT):
    r = Ki @ np.r_[center_px, 1.0]
    return r / r[2] * (f * D / base_len_px)


C_NEAR = rim_centre_cam(NEAR[0], NEAR[1])
C_BACK = rim_centre_cam(BACK[0], BACK[1])


def rim_point(d, deg, side=1):
    """CAD position of the centre of a wheel's cone rim for the strut pointing along d (+1: +y) at `deg` below horizontal."""
    m = Sphere(0.3).moved(Location((0, 0, W.L_DRUM)))
    return np.array(list(W.place(m, d, deg, side).center()))


HUB_PX = (288.0, 400.0)       # the hub cap on the visible side face (one of the pixels used in sil_scale.py)


def perp_to_hub_axis(v):
    return v - (v @ d2) * d2


def solve_pose():
    """Strut angles and position from the photo: the hub axis is the line from which both wheel centres are equally far (the photo's own
    strut length, about 86 mm at the CAD wheel's size, against the CAD's 70 mm), and the angle of each wheel centre below the body's
    mid-plane gives that strut's angle.  The CAD struts are shorter, so its wheels do not land on the photo's."""
    ray = Ki @ np.r_[HUB_PX, 1.0]
    ray /= np.linalg.norm(ray)
    ts = np.linspace(300, 1200, 9001)
    f1 = np.array([np.linalg.norm(perp_to_hub_axis(t * ray - C_NEAR)) for t in ts])
    f2 = np.array([np.linalg.norm(perp_to_hub_axis(t * ray - C_BACK)) for t in ts])
    i = np.where(np.sign((f1 - f2)[:-1]) != np.sign((f1 - f2)[1:]))[0][0]
    H = ts[i] * ray
    ang = {}
    for nm, C in (("near", C_NEAR), ("back", C_BACK)):
        v = perp_to_hub_axis(C - H)
        ang[nm] = float(np.degrees(np.arcsin((v @ n) / np.linalg.norm(v))))
        print(f"{nm} strut: length {np.linalg.norm(v):.1f} mm in the photo (CAD {S.STRUT_L:.0f}), {ang[nm]:.1f} deg below the body's mid-plane")
    # position: hub axis line at the photo's perpendicular position, wheel plane at the photo's distance along the hub axis
    x_wheel = rim_point(+1, 0.0)[0]
    along = d2 @ ((C_NEAR + C_BACK) / 2) + x_wheel                      # d2 . T
    T = perp_to_hub_axis(H - R @ np.array([0, 0, E.HUB_Z])) + along * d2
    for nm, C, d in (("near", C_NEAR, +1), ("back", C_BACK, -1)):
        c = R @ rim_point(d, ang[nm]) + T
        print(f"{nm} wheel rim centre: photo vs CAD differ by {np.linalg.norm(c - C):.1f} mm ({np.linalg.norm(proj(c) - proj(C)):.0f} px)")
    return T, ang["near"], ang["back"]


def proj(P):
    p = K @ P
    return p[:2] / p[2]


def build_parts(a_front, a_back):
    """(name, shape) in CAD coordinates with the struts and wheels posed individually."""
    angle = {+1: a_front, -1: a_back}
    parts = []
    for name, path in (("body", HW / "body/out/body_hammond.step"), ("lid", HW / "body/out/lid_plate.step"), ("window", HW / "body/out/window_pane.step"),
                       ("hub", HW / "hub/out/hub_housing.step"), ("hub", HW / "hub/out/hub_shafts.step"), ("hub", HW / "hub/out/hub_gears.step"),
                       ("servo", HW / "hub/out/strut_servos.step")):
        if path.exists():
            parts.append((name, import_step(path)))
    w0 = W.wheel_local()
    w0_left = w0.mirror(Plane.YZ)
    for side in (1, -1):
        for (bossr, platr, d) in ((S.A_BOSS, S.A_PLATE, +1), (S.B_BOSS, S.B_PLATE, -1)):
            a = angle[d]
            s = S.posed(S.strut(bossr, platr, S.WHEEL_X[0], d), d, a)
            extra = [S.posed(fn(d), d, a) for fn in (S.motor, S.spindle, S.bearings)]
            if side < 0:
                s = s.mirror(Plane.YZ)
                extra = [q.mirror(Plane.YZ) for q in extra]
            parts.append(("strut", s))
            parts += [("tip", q) for q in extra]
            arg = d if side > 0 else -d
            w = W.place(w0, arg, a, side)
            c = w.center()
            if c.X * c.Y < 0:
                w = W.place(w0_left, arg, a, side)
            parts.append(("wheel", w))
    return parts


COLOURS = {"body": (176, 181, 188), "lid": (150, 155, 160), "window": (20, 28, 36), "hub": (190, 150, 90), "servo": (60, 60, 60),
           "strut": (205, 195, 175), "tip": (150, 150, 150), "wheel": (215, 219, 224)}


def mesh_of(shape, tmp, k):
    p = Path(tmp) / f"m{k}.stl"
    export_stl(shape, str(p), tolerance=0.08, angular_tolerance=0.25)
    return trimesh.load(p)


def render(parts, T, width, height, ss=2):
    """Z-buffer render at ss times the photo size; returns RGB float image and a coverage mask, both at photo size."""
    Wd, Ht = width * ss, height * ss
    K2 = K.copy()
    K2[:2] *= ss
    zbuf = np.full((Ht, Wd), np.inf)
    img = np.zeros((Ht, Wd, 3))
    light = np.array([-0.45, -0.65, -0.6])      # direction toward the light in the camera frame: left, up, toward the camera
    light /= np.linalg.norm(light)
    with tempfile.TemporaryDirectory() as tmp:
        for k, (name, shape) in enumerate(parts):
            m = mesh_of(shape, tmp, k)
            V = m.vertices @ R.T + T                       # CAD -> camera
            F = m.faces
            tri = V[F]
            nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            ln = np.linalg.norm(nrm, axis=1)
            ok = ln > 1e-9
            nrm[ok] /= ln[ok, None]
            cen = tri.mean(1)
            front = (nrm * -cen).sum(1) > 0
            P = V @ K2.T
            P = P[:, :2] / P[:, 2:3]
            base = np.array(COLOURS[name], float)
            for i in np.nonzero(front & ok)[0]:
                a, b, c = F[i]
                pa, pb, pc = P[a], P[b], P[c]
                x0, x1 = int(max(0, np.floor(min(pa[0], pb[0], pc[0])))), int(min(Wd - 1, np.ceil(max(pa[0], pb[0], pc[0]))))
                y0, y1 = int(max(0, np.floor(min(pa[1], pb[1], pc[1])))), int(min(Ht - 1, np.ceil(max(pa[1], pb[1], pc[1]))))
                if x1 < x0 or y1 < y0:
                    continue
                den = (pb[1] - pc[1]) * (pa[0] - pc[0]) + (pc[0] - pb[0]) * (pa[1] - pc[1])
                if abs(den) < 1e-12:
                    continue
                gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                l1 = ((pb[1] - pc[1]) * (gx - pc[0]) + (pc[0] - pb[0]) * (gy - pc[1])) / den
                l2 = ((pc[1] - pa[1]) * (gx - pc[0]) + (pa[0] - pc[0]) * (gy - pc[1])) / den
                l3 = 1 - l1 - l2
                inside = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
                if not inside.any():
                    continue
                za, zb, zc = V[a, 2], V[b, 2], V[c, 2]
                zz = 1.0 / (l1 / za + l2 / zb + l3 / zc)            # perspective-correct depth
                sub = zbuf[y0:y1 + 1, x0:x1 + 1]
                upd = inside & (zz < sub)
                if upd.any():
                    sub[upd] = zz[upd]
                    shade = 0.28 + 0.72 * max(0.0, float(nrm[i] @ light))
                    img[y0:y1 + 1, x0:x1 + 1][upd] = base * shade
            print(f"  rendered {name:<6} {len(F):7d} triangles")
    mask = np.isfinite(zbuf)
    im = img.reshape(height, ss, width, ss, 3).mean((1, 3))
    cov = mask.reshape(height, ss, width, ss).mean((1, 3))
    return im, cov


def main():
    T, a_front, a_back = solve_pose()
    parts = build_parts(a_front, a_back)
    photo = np.asarray(Image.open(PHOTO).convert("RGB"), float)
    h, w = photo.shape[:2]
    im, cov = render(parts, T, w, h)
    from scipy.ndimage import binary_dilation, binary_erosion
    cov3 = cov[..., None]
    solid = np.where(cov3 > 0, im / np.maximum(cov3, 1e-6), 0)
    blend = photo * (1 - 0.55 * cov3) + solid * 0.55 * cov3
    m = cov > 0.5
    edge = binary_dilation(m) & ~binary_erosion(m)
    outline = photo.copy()
    outline[edge] = (255, 40, 200)                      # the CAD silhouette on the untouched photo
    flat = np.full_like(photo, 232)
    flat = flat * (1 - cov3) + solid * cov3             # the CAD on a plain background, same camera

    def save(arr, name):
        Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(OUT_DIR / name)
    save(blend, "silver_cad_overlay.png")
    save(outline, "silver_cad_outline.png")
    save(np.hstack([photo, flat]), "silver_cad_side_by_side.png")
    print("wrote silver_cad_overlay.png, silver_cad_outline.png and silver_cad_side_by_side.png in", OUT_DIR)


if __name__ == "__main__":
    main()
