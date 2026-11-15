#!/usr/bin/env python3
"""First-pass topology optimisation of the body middle with pyMOTO (docs/optimisation-setup.md, docs/load-cases.md).

Setup (once):  python3 -m venv .venv-to && .venv-to/bin/pip install -r hardware/body/requirements-to.txt
               .venv/bin/python hardware/body/to_inputs.py --grid 36        (writes out/to_grid_n36.npz; needs the CAD venv)
Run:           .venv-to/bin/python hardware/body/to_run.py --n 36 --mass 40 [--maxit 60] [--check]

WHAT IT SOLVES (first pass: a layout of load paths, NOT a manufacturable design; see "Limits" in docs/optimisation-setup.md)
  * Design variables: density of the UPPER half (z >= 30) of the body middle (x, y +-69 mm, z 7 to 53 mm); the lower half is its mirror (owner's symmetry about z = 30); the fixed voids are mirrored too.
  * Casting (draw) constraint along z: a density filter, then Langelaar's overhang filter with the draw direction +z from the parting plane and a ~0 degree overhang angle (a cell is supported only by the cell
    straight below it, so a void between a cell and the plane forces the cell void: the two-core shadow rule), then the fixed solids are put back (exempt).
  * Fixed: voids (servo pockets, components, plug zones, wire channels, plate seats, contact pockets), solids (the outer skin, hub bore rings, seat walls, cam bosses, window ring, lid seat rims).
  * Material: isotropic forged carbon, E 35.5 GPa, nu 0.3, SIMP p = 3; the skin cells carry a stiffness weight (skin thickness 1.5 mm over the cell size) instead of 1.
  * Load cases (N, mm; equilibrated: each applied force set has its reaction in the same set, so three isostatic supports at the hub rings take only the residual): the 0.3 m drop (100 g), a corner
    impact (310 N), the lid clamp (330 N per cam), the 2.9 N.m stall of each servo (its reaction couple on the hub ring), and handling (30 N). Inertial loads are placed on the masses' attachment regions.
  * Objective: the mean over the load cases of compliance / its value at the starting design. Constraint: added structure mass (upper-half design cells x 2 x 1.55 g/cm3) <= --mass grams.
  * Solver: CG with geometric multigrid (pyMOTO).  Optimiser: MMA.
Not included: the self-weight of the optimised material, stress constraints, the hub-bore deflection target, draft, the lids (separate parts).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pymoto as pym
from scipy import ndimage as ndi

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=36)
ap.add_argument("--mass", type=float, default=40.0, help="added structure, g (upper-half design cells x 2)")
ap.add_argument("--maxit", type=int, default=60)
ap.add_argument("--radius", type=float, default=1.5, help="density filter radius in cells")
ap.add_argument("--check", action="store_true", help="build, solve once at the starting design, report equilibrium and compliances, and stop")
ap.add_argument("--start", default=None, help="a result .npz from an earlier run to start from (resampled if its grid is coarser or finer)")
ap.add_argument("--p", type=float, default=3.0, help="SIMP penalty (3 first; 4 and 5 in continuation runs started from the previous result)")
args = ap.parse_args()

g = np.load(HERE / "out" / f"to_grid_n{args.n}.npz")
n, nz, h = int(g["n"]), int(g["nz"]), float(g["h_mm"])
nzh = nz // 2
E0, NU, EMIN, P_SIMP, RHO = 35500.0, 0.3, 1e-9, args.p, 1.55e-3      # MPa, -, -, -, g/mm3
print(f"grid {n} x {n} x {nz}, cell {h:.3f} mm, {n * n * nz} cells")


def flipz(a):
    return a[:, :, ::-1]


# ---------------- classes ----------------
void = (g["void"] >= 0.5); void |= flipz(void)
skin_f, other_f = g["skin"], g["solid_other"]
solid = ((skin_f >= 0.2) | (other_f >= 0.2)) & ~void; solid |= flipz(solid)
solid_w = np.clip(0.6 * skin_f + other_f, 0.0, 1.0); solid_w = np.maximum(solid_w, flipz(solid_w)); solid_w = np.where(solid, np.maximum(solid_w, 0.2), 0.0)
design = (g["keep_in"] >= 0.5) & ~void & ~solid
print(f"cells: void {void.sum()}, fixed solid {solid.sum()}, design {design.sum()} (upper half {design[:, :, nzh:].sum()}, the unknowns)")

domain = pym.VoxelDomain(n, n, nz, unitx=h, unity=h, unitz=h)
dom_h = pym.VoxelDomain(n, n, nzh, unitx=h, unity=h, unitz=h)
ndof = 3


def to_vec(dom, arr):
    v = np.empty(dom.nel, dtype=float); v[dom.elements.ravel()] = np.asarray(arr, dtype=float).ravel(); return v


# ---------------- loads ----------------
cell_vol = h ** 3
cx = (np.arange(n) + 0.5) * h - 69.0
cz = 7.0 + (np.arange(nz) + 0.5) * h
CX, CY, CZ = np.meshgrid(cx, cx, cz, indexing="ij")
F_cases, names = [], []


def attach(mask):
    m = mask & ~void
    assert m.any(), "empty attachment set"
    return m


def add_force(F, mask, vec):
    """vec (N) shared equally by the cells in `mask`, each cell's share split over its 8 nodes."""
    eidx = domain.elements[mask]
    share = np.asarray(vec, dtype=float) / len(eidx) / 8.0
    for c in range(3):
        np.add.at(F, ndof * domain.conn[eidx].ravel() + c, share[c])


def add_cell_forces(F, mask, forces):
    """forces: (ncells, 3) in the order of np.argwhere(mask)."""
    idx = np.argwhere(mask)
    for (i, j, k), f in zip(idx, forces):
        e = domain.elements[i, j, k]
        for c in range(3):
            np.add.at(F, ndof * domain.conn[e] + c, f[c] / 8.0)


solidish = solid | design
# mass items (g) and the cells they bear on
dil = lambda m: ndi.binary_dilation(m, iterations=1) & solidish
items = []
for tag in ("Bp", "Ap", "Bn", "An"):
    items.append((f"servo+plate {tag}", 59.1, attach(g[f"seat_{tag}"] >= 0.2)))
items.append(("hub parts", 74.0, attach((g["ring_p"] >= 0.2) | (g["ring_n"] >= 0.2))))
items.append(("lid top", 65.0, attach((g["rim_top"] >= 0.2) | (g["cam_top"] >= 0.2))))
items.append(("lid bottom", 65.0, attach((g["rim_bot"] >= 0.2) | (g["cam_bot"] >= 0.2))))
items.append(("battery + protection", 30.0, attach(dil(g["void_battery"] >= 0.5))))
items.append(("camera, ring, sensor", 18.0, attach((g["window"] >= 0.2) | dil(g["void_camera"] >= 0.5))))
items.append(("XBee + patch", 12.0, attach(dil(g["void_antenna"] >= 0.5) | dil(g["void_xbee"] >= 0.5))))
shell_g = 164.0 + 47.0 + 26.4 + 15.0                         # skin, rings/screws/seal, end-face cells, wiring: spread on all fixed solids
items.append(("shell and the rest", shell_g, attach(solid)))
M_G = sum(m for _, m, _ in items)
print(f"mass items: {M_G:.0f} g in {len(items)} groups")


def inertial(F, accel_ms2, direction):
    """Inertial forces on all items for an acceleration of the body (the load that the inertia exerts: -m a in `direction`... applied as -direction * m * a)."""
    tot = np.zeros(3)
    d = np.asarray(direction, dtype=float); d /= np.linalg.norm(d)
    for _, m, mask in items:
        f = -d * (m * 1e-3) * accel_ms2
        add_force(F, mask, f); tot += f
    return tot


ring_p, ring_n = attach(g["ring_p"] >= 0.2), attach(g["ring_n"] >= 0.2)
nf = domain.nnodes * ndof
# LC drop 0.3 m: the body decelerates at 100 g; the rings push up with the sum of the inertial forces
F = np.zeros(nf); tot = inertial(F, 100 * 9.81, (0, 0, -1))      # body accelerating up at 100 g: inertial load down (-z)... see sign below
# an upward acceleration a gives inertial forces -m a (downward); the rings carry +sum upward
add_force(F, ring_p, -tot / 2); add_force(F, ring_n, -tot / 2)
F_cases.append(F); names.append("drop 0.3 m, 100 g")
# LC corner impact 310 N at the bottom +x +y corner, toward the centre and up
corner = attach((CX > 69 - 2 * h) & (CY > 69 - 2 * h) & (CZ < 7 + 2 * h) & solidish)
d = np.array([-1.0, -1.0, 1.0]) / np.sqrt(3.0)
F = np.zeros(nf); add_force(F, corner, 310.0 * d)
for _, m, mask in items:
    add_force(F, mask, -310.0 * d * m / M_G)
F_cases.append(F); names.append("corner impact 310 N")
# LC lid clamp: +z on the top cam bosses (330 N each, 4), -z on the top rims; the bottom lid mirrored
F = np.zeros(nf)
add_force(F, attach(g["cam_top"] >= 0.2), (0, 0, 4 * 330.0)); add_force(F, attach(g["rim_top"] >= 0.2), (0, 0, -4 * 330.0))
add_force(F, attach(g["cam_bot"] >= 0.2), (0, 0, -4 * 330.0)); add_force(F, attach(g["rim_bot"] >= 0.2), (0, 0, 4 * 330.0))
F_cases.append(F); names.append("lid clamp 330 N per cam")
# LC servo stall: couple T about x on the servo's seat walls, the reaction couple on the hub ring of that side
T_STALL = 2900.0                                                    # N.mm


def couple(F, mask, y0, z0, T):
    """A pure couple T (N.mm) about the x axis through (y0, z0) on the cells in `mask`: tangential forces proportional to the distance from the axis, then the net force removed and the moment rescaled to T."""
    idx = np.argwhere(mask)
    ry = np.array([CY[i, j, k] - y0 for i, j, k in idx]); rz = np.array([CZ[i, j, k] - z0 for i, j, k in idx])
    r = np.hypot(ry, rz)
    fy, fz = -rz / r * r, ry / r * r                                 # tangential, proportional to r
    fy -= fy.mean(); fz -= fz.mean()                                 # no net force
    M = np.sum(ry * fz - rz * fy)
    sc = T / M
    add_cell_forces(F, mask, np.stack([np.zeros_like(r), sc * fy, sc * fz], axis=1))


for tag, ring in (("Bp", ring_p), ("Ap", ring_p), ("Bn", ring_n), ("An", ring_n)):
    ys, zs = float(g[f"seatpos_{tag}"][0]), float(g[f"seatpos_{tag}"][1])
    F = np.zeros(nf)
    couple(F, attach(g[f"seat_{tag}"] >= 0.2), ys, zs, T_STALL); couple(F, ring, 0.0, 30.0, -T_STALL)
    F_cases.append(F); names.append(f"servo {tag} stall 2.9 N.m")
# LC component retention under the 0.3 m drop (100 g): each light component on its own, so that a component hanging on no structure counts as much as a stiff servo seat (found 2026-11-15: without these
# the battery's 29 N carried no weight in the mean of the normalised compliances and the optimiser left it hanging, 35 mm in the drop)
for nm_i, m_i, mask_i in items:
    if nm_i.startswith(("battery", "camera", "XBee")):
        F = np.zeros(nf); f_i = np.array([0.0, 0.0, -(m_i * 1e-3) * 100 * 9.81])
        add_force(F, mask_i, f_i); add_force(F, ring_p, -f_i / 2); add_force(F, ring_n, -f_i / 2)
        F_cases.append(F); names.append(f"{nm_i.split(' ')[0].split(',')[0]} 100 g")
# LC handling: 30 N squeeze across the hub faces
F = np.zeros(nf)
pad_p = attach((CX > 69 - 1.5 * h) & (np.abs(CY) < 20) & (np.abs(CZ - 30) < 15) & solidish); pad_n = attach((CX < -69 + 1.5 * h) & (np.abs(CY) < 20) & (np.abs(CZ - 30) < 15) & solidish)
add_force(F, pad_p, (-30.0, 0, 0)); add_force(F, pad_n, (30.0, 0, 0))
F_cases.append(F); names.append("handling 30 N")
Fm = np.stack(F_cases, axis=1)
nLC = Fm.shape[1]
cc = domain.nodes
node_pos = np.zeros((domain.nnodes, 3))
nx_ = np.arange(n + 1) * h - 69.0; nz_ = 7.0 + np.arange(nz + 1) * h
for i in range(n + 1):
    for j in range(n + 1):
        for k in range(nz + 1):
            node_pos[cc[i, j, k]] = (nx_[i], nx_[j], nz_[k])
print("load-case resultants (N) and moments about the centre (N.mm):")
for k, nm in enumerate(names):
    f3 = Fm[:, k].reshape(-1, 3)
    R = f3.sum(axis=0); Mo = np.cross(node_pos - np.array([0, 0, 30.0]), f3).sum(axis=0)
    print(f"  {nm:28s} |F| {np.linalg.norm(R):7.2f} (applied total {np.abs(f3).sum():8.0f})   M {np.linalg.norm(Mo):9.0f}")

# ---------------- supports: three isostatic nodes on the hub rings ----------------
def ring_node(ring, ztop):
    i, j, k = [tuple(a) for a in np.argwhere(ring & (np.abs(CY) < h))][0 if ztop else -1]
    return domain.conn[domain.elements[i, j, k]][0]


n1, n2, n3 = ring_node(ring_p, True), ring_node(ring_n, True), ring_node(ring_p, False)
bc = np.array([3 * n1, 3 * n1 + 1, 3 * n1 + 2, 3 * n2 + 1, 3 * n2 + 2, 3 * n3 + 1])
free_lc = None

# ---------------- design variables and the network ----------------
V_T = args.mass / (RHO * 1000.0) * 1000.0                           # mm3 of added material: mass (g) / density (g/mm3)
design_h = design[:, :, nzh:]
Vd = 2 * design_h.sum() * cell_vol
volfrac = min(0.9, V_T / Vd)
print(f"added structure {args.mass:g} g = {V_T / 1000:.1f} cm3 of the {Vd / 1000:.0f} cm3 design space (volume fraction {volfrac:.3f})")
x0 = np.where(design_h, volfrac, 0.0)
if args.start:
    x0 = np.load(args.start)["rho_h"].astype(float)
    if x0.shape != design_h.shape:                                   # a result from another grid: resample (linear), keep inside the design cells
        x0 = ndi.zoom(x0, np.array(design_h.shape) / np.array(x0.shape), order=1)
    x0 = np.where(design_h, np.clip(x0, 0.0, 1.0), 0.0)
sx = pym.Signal("x", state=to_vec(dom_h, x0))
void_idx = dom_h.elements[void[:, :, nzh:]].ravel()
solid_idx = dom_h.elements[solid[:, :, nzh:]].ravel()


class StiffnessMap(pym.Module):
    """Mirror the upper-half density about z = 30 and map it to the element stiffness factors of the whole domain (SIMP for design cells, the skin and other fixed solids as set, Emin elsewhere)."""

    def __call__(self, rho_h):
        a = rho_h[dom_h.elements]
        full = np.empty((n, n, nz)); full[:, :, nzh:] = a; full[:, :, :nzh] = flipz(a)
        self.full = full
        E = np.where(design, EMIN + (1 - EMIN) * full ** P_SIMP, np.where(solid, solid_w + EMIN, EMIN))
        out = np.empty(domain.nel); out[domain.elements.ravel()] = E.ravel()
        return out

    def _sensitivity(self, dE):
        d = dE[domain.elements] * np.where(design, P_SIMP * (1 - EMIN) * self.full ** (P_SIMP - 1), 0.0)
        dh = d[:, :, nzh:] + flipz(d[:, :, :nzh])
        out = np.empty(dom_h.nel); out[dom_h.elements.ravel()] = dh.ravel()
        return out


mask_h = to_vec(dom_h, design_h)
with pym.Network() as fn:
    s0 = pym.SetValue(indices=void_idx, value=0.0)(sx)
    s1 = pym.SetValue(indices=solid_idx, value=1.0)(s0)
    sf = pym.FilterConv(dom_h, radius=args.radius)(s1)                       # mirror at all boundaries, including the parting plane
    so = pym.OverhangFilter(dom_h, direction="+z", overhang_angle=0.5)(sf)   # the casting (two-core) shadow rule
    sr = pym.SetValue(indices=solid_idx, value=1.0)(so)                       # the fixed solids are exempt from it
    sr.tag = "design density"
    sE = StiffnessMap()(sr)
    sK = pym.AssembleStiffness(domain, bc=bc, e_modulus=E0, poisson_ratio=NU)(sE)
    mg1 = pym.solvers.GeometricMultigrid(domain)
    mgs = [mg1]
    while True:
        if any(nn % 2 != 0 for nn in mgs[-1].sub_domain.size) or any(mgs[-1].sub_domain.size < 8):
            break
        mgs.append(pym.solvers.GeometricMultigrid(mgs[-1].sub_domain)); mgs[-2].inner_level = mgs[-1]
    print(f"multigrid: fine {n}x{n}x{nz}, {len(mgs)} level(s), coarsest {tuple(mgs[-1].sub_domain.size)}")
    solver = pym.solvers.CG(preconditioner=mg1, verbosity=0, tol=1e-6)
    su = pym.LinSolve(hermitian=True, solver=solver)(sK, Fm)
    sc = pym.EinSum("ik,ik->k")(su, Fm); sc.tag = "compliances"
    sw = pym.Signal("w", state=np.ones(nLC) / nLC)
    sobj = pym.EinSum("k,k->")(sc, sw); sobj.tag = "mean normalised compliance"
    s_obj = pym.Scaling(scaling=100.0)(sobj); s_obj.tag = "objective"
    svol = pym.EinSum("i,i->")(mask_h, sr)
    sg = pym.MathExpression(f"10*(inp0*{2 * cell_vol / V_T} - 1)")(svol); sg.tag = "mass constraint"

t0 = time.time()
fn.response()
c0 = np.array(sc.state)
print(f"first solve, all {nLC} load cases: {time.time() - t0:.1f} s")
sw.state = 1.0 / (nLC * c0)
for nm, c in zip(names, c0):
    print(f"  starting compliance {nm:28s} {c:12.4g} N.mm")
def group_displacements(label):
    U = np.asarray(su.state)[:, 0].reshape(-1, 3)                 # the drop case
    print(f"largest nodal displacement per mass group, {names[0]} ({label}):")
    for nm, m_, mask in items:
        nodes = np.unique(domain.conn[domain.elements[mask]].ravel())
        print(f"  {nm:24s} {m_:6.1f} g  {np.linalg.norm(U[nodes], axis=1).max():8.3f} mm")


if args.check:
    group_displacements("starting design")
    print("equilibrium: the resultants above are the supports' share (N); they should be small against the applied totals")
    sys.exit(0)

print(f"optimising: MMA, {args.maxit} iterations")
t0 = time.time()
pym.minimize_mma(sx, [s_obj, sg], function=fn, maxit=args.maxit, tolx=1e-3, tolf=1e-4)
dt = time.time() - t0
fn.response()
rho = np.asarray(sr.state)
rho_h = rho[dom_h.elements]
mass_added = 2 * (rho_h * design_h).sum() * cell_vol * RHO
print(f"done in {dt / 60:.1f} min; added structure {mass_added:.1f} g; compliances relative to the start: " + ", ".join(f"{nm}: {c / c0_:.2f}" for nm, c, c0_ in zip(names, sc.state, c0)))
# displacements (mm): the largest nodal displacement over the hub-ring nodes and over the whole model, per load case (the hub bore target of docs/load-cases.md is 0.05 mm under LC1 + LC2)
U = np.asarray(su.state)
ring_nodes = np.unique(domain.conn[domain.elements[ring_p | ring_n]].ravel())
u_ring = np.array([np.linalg.norm(U[:, k].reshape(-1, 3)[ring_nodes], axis=1).max() for k in range(nLC)])
u_all = np.array([np.linalg.norm(U[:, k].reshape(-1, 3), axis=1).max() for k in range(nLC)])
print("largest nodal displacement (mm): ring nodes / anywhere: " + "; ".join(f"{nm}: {a:.3f} / {b:.3f}" for nm, a, b in zip(names, u_ring, u_all)))
group_displacements("final design")
out = HERE / "out"
tag = f"n{n}_m{args.mass:g}" + ("" if args.p == 3.0 else f"_p{args.p:g}")
np.savez_compressed(out / f"to_result_{tag}.npz", rho_h=rho_h, design_h=design_h, solid_h=solid[:, :, nzh:], void_h=void[:, :, nzh:], h=h, mass_g=mass_added, names=np.array(names), c0=c0, c=np.array(sc.state), u_ring=u_ring, u_all=u_all)
print("wrote", out / f"to_result_{tag}.npz")
