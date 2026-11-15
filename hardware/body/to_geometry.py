#!/usr/bin/env python3
"""Turn a to_run.py result into geometry for viewing: OBJ surface meshes of the optimised structure, the other fixed solids, the skin, and the main components.   (needs the CAD venv: it imports layout.py)

Run: .venv/bin/python hardware/body/to_geometry.py hardware/body/out/to_result_n48_m120_p5.npz [threshold 0.5]
Writes hardware/body/out/geom/<result>_{structure,fixed,skin,context}.obj (mm; x across, y along (the camera end is +y), z up; the body middle only, z 7 to 53).  They are BLOCKY voxel surfaces (the
optimiser's cells); hardware/assembly/blender_structure.py smooths the structure and renders it.  The structure is the cells with density above the threshold in both halves (the lower half is the mirror).
"""
import contextlib
import io
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
with contextlib.redirect_stdout(io.StringIO()):
    import layout as LY

src = Path(sys.argv[1])
thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
r = np.load(src)
rho_h, des_h = r["rho_h"], r["design_h"]
h = float(r["h"]); n = rho_h.shape[0]; nzh = rho_h.shape[2]; nz = 2 * nzh
g = np.load(HERE / "out" / f"to_grid_n{n}.npz")
ORIGIN = np.array([-69.0, -69.0, 7.0])


def full(a_h):
    out = np.zeros((n, n, nz), dtype=a_h.dtype); out[:, :, nzh:] = a_h; out[:, :, :nzh] = a_h[:, :, ::-1]; return out


void = g["void"] >= 0.5; void |= void[:, :, ::-1]
other = (g["solid_other"] >= 0.2) & ~void; other |= other[:, :, ::-1]
skin = (g["skin"] >= 0.2) & ~void & ~other; skin |= skin[:, :, ::-1]
struct = full((rho_h > thr) & des_h)
print(f"{src.name}: structure cells {struct.sum()} (threshold {thr}), other fixed solids {other.sum()}, skin {skin.sum()}")


def surface(mask):
    """Exposed faces of a boolean voxel grid as quads (corner index triplets), outward normals."""
    pad = np.pad(mask, 1)
    quads = []
    for axis in range(3):
        for sgn in (1, -1):
            nb = np.roll(pad, -sgn, axis=axis)[1:-1, 1:-1, 1:-1]
            ex = mask & ~nb
            idx = np.argwhere(ex)
            if not len(idx):
                continue
            a1, a2 = (axis + 1) % 3, (axis + 2) % 3
            base = idx.copy()
            if sgn > 0:
                base[:, axis] += 1
            c = []
            for d1, d2 in ((0, 0), (1, 0), (1, 1), (0, 1)):
                p = base.copy(); p[:, a1] += d1; p[:, a2] += d2; c.append(p)
            q = np.stack(c, axis=1)                                   # (m, 4, 3), counter-clockwise seen from +a (axis, a1, a2 are a right-handed set)
            if sgn < 0:
                q = q[:, ::-1]
            quads.append(q)
    if not quads:
        return np.zeros((0, 3)), np.zeros((0, 4), dtype=int)
    q = np.concatenate(quads)
    flat = q.reshape(-1, 3)
    uniq, inv = np.unique(flat, axis=0, return_inverse=True)
    return uniq * h + ORIGIN, inv.reshape(-1, 4)


def write_obj(path, objects):
    """objects: list of (name, vertices (m,3), faces (k,4) 0-based)."""
    with open(path, "w") as f:
        off = 1
        for name, v, fa in objects:
            f.write(f"o {name}\n")
            for p in v:
                f.write(f"v {p[0]:.3f} {p[1]:.3f} {p[2]:.3f}\n")
            for q in fa:
                f.write("f " + " ".join(str(int(i) + off) for i in q) + "\n")
            off += len(v)


def box(x0, x1, y0, y1, z0, z1):
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], dtype=float)
    f = np.array([[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]])
    return v, f


out = HERE / "out" / "geom"; out.mkdir(exist_ok=True)
stem = src.stem.replace("to_result_", "")
for name, m in (("structure", struct), ("fixed", other), ("skin", skin)):
    v, f = surface(m)
    write_obj(out / f"{stem}_{name}.obj", [(name, v, f)])
    print(f"  {name}: {len(v)} vertices, {len(f)} faces")

# context: the servos, their mounting plates, the battery and its protection board, the camera module, the XBee carrier and the patch
H = LY.H; HZ = LY.HZ
ctx = []
for (tag, side), s in LY.servos.items():
    xa, xb = sorted((side * (s["xf"] - H.SV_H), side * s["xf"]))
    ctx.append((f"servo_{tag}{'p' if side > 0 else 'n'}", *box(xa, xb, s["y0"], s["y1"], HZ - H.SV_W / 2, HZ + H.SV_W / 2)))
    pa, pb = sorted((side * s["xf"], side * (s["xf"] + 1.5)))
    ctx.append((f"plate_{tag}{'p' if side > 0 else 'n'}", *box(pa, pb, s["y0"], s["y1"], HZ - H.SV_W / 2, HZ + H.SV_W / 2)))
for nm, (m, bb, note, _c) in LY.comps.items():
    if nm.startswith("battery"):
        ctx.append(("battery", *box(*bb)))
    elif nm.startswith("cell protection"):
        ctx.append(("protection", *box(*bb)))
    elif nm.startswith("camera module"):
        ctx.append(("camera", *box(*bb)))
    elif nm.startswith("XBee"):
        ctx.append(("xbee", *box(*bb)))
    elif nm.startswith("comms patch"):
        ctx.append(("patch", *box(*bb)))
write_obj(out / f"{stem}_context.obj", ctx)
print(f"  context: {len(ctx)} boxes")
print("wrote", out)
