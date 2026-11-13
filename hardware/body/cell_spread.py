"""Spread the parts of an IXOLAR layout so they form a perfect rectangle with lines of the most uniform thickness.

Run: python3 hardware/body/cell_spread.py   (needs numpy and matplotlib; writes hardware/body/out/cell_spread_ixolar.png and .svg)

Owner's request (2026-11-12): for both layouts, space the cells out so that they form a perfect rectangle and the lines between them are as uniform as possible.

Method: the parts keep their datasheet sizes (rigid) and their neighbours from the packed layout. Unknowns are every part's position, the four margins and one common line
thickness g. Least squares pulls every gap between neighbouring parts, and each of the four margins (carbon border), towards g. Exact constraints make the outer edges flush:
all parts on the left (right, bottom, top) side of the block have the same edge coordinate, so the block is a perfect rectangle. What cannot be fixed is a part that is
shorter or narrower than its row or column by more than the gaps can absorb (89 against 90 mm, 44.5 x 3 against 52 + 40 + 40): that difference shows up as a thicker or
thinner line, and the script prints how much. The parts' own tolerance is +-0.3 mm per side (datasheets), so differences below about 0.5 mm are inside it.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cell_catalogue as C
import cell_diagram as D

FACE = C.FACE
EDGE_TOL = 2.5   # mm: a part whose outer edge is within this of the block's side counts as sitting on that side (it must end up flush)


def initial(counts):
    ar, tree, W, H = D.find(counts)
    items = []
    bw, bh = C.draw(tree, 0, 0, 0.0, items)
    return items, bw, bh


def solve(items, bw, bh, margin_weight=0.2):
    n = len(items)
    xs = [it[0] for it in items]; ys = [it[1] for it in items]
    ws = [it[2] for it in items]; hs = [it[3] for it in items]
    # sides
    L = [i for i in range(n) if xs[i] <= EDGE_TOL]
    R = [i for i in range(n) if bw - (xs[i] + ws[i]) <= EDGE_TOL]
    B = [i for i in range(n) if ys[i] <= EDGE_TOL]
    T = [i for i in range(n) if bh - (ys[i] + hs[i]) <= EDGE_TOL]
    # neighbours (a left of b with overlapping y; a below b with overlapping x)
    hadj, vadj = [], []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            oy = min(ys[i] + hs[i], ys[j] + hs[j]) - max(ys[i], ys[j])
            ox = min(xs[i] + ws[i], xs[j] + ws[j]) - max(xs[i], xs[j])
            if oy > 1.0 and 0 <= xs[j] - (xs[i] + ws[i]) < 3.0:
                hadj.append((i, j, oy))
            if ox > 1.0 and 0 <= ys[j] - (ys[i] + hs[i]) < 3.0:
                vadj.append((i, j, ox))
    # unknowns: x0..x(n-1), y0..y(n-1), xL, xR, yB, yT, g
    N = 2 * n + 5
    ix = lambda i: i
    iy = lambda i: n + i
    iL, iR, iB, iT, ig = 2 * n, 2 * n + 1, 2 * n + 2, 2 * n + 3, 2 * n + 4
    rows, rhs = [], []
    meanlen = np.mean([a[2] for a in hadj + vadj])
    for i, j, ov in hadj:                       # x_j - x_i - w_i - g = 0
        r = np.zeros(N); r[ix(j)] = 1; r[ix(i)] = -1; r[ig] = -1
        rows.append(r * np.sqrt(ov / meanlen)); rhs.append(ws[i] * np.sqrt(ov / meanlen))
    for i, j, ov in vadj:
        r = np.zeros(N); r[iy(j)] = 1; r[iy(i)] = -1; r[ig] = -1
        rows.append(r * np.sqrt(ov / meanlen)); rhs.append(hs[i] * np.sqrt(ov / meanlen))
    mw = np.sqrt(margin_weight)
    r = np.zeros(N); r[iL] = 1; r[ig] = -1; rows.append(r * mw); rhs.append(0)                     # left margin = g
    r = np.zeros(N); r[iR] = -1; r[ig] = -1; rows.append(r * mw); rhs.append(-FACE * mw)                 # FACE - xR = g
    r = np.zeros(N); r[iB] = 1; r[ig] = -1; rows.append(r * mw); rhs.append(0)
    r = np.zeros(N); r[iT] = -1; r[ig] = -1; rows.append(r * mw); rhs.append(-FACE * mw)
    A, b = np.array(rows), np.array(rhs)
    Ce, d = [], []
    for i in L:
        r = np.zeros(N); r[ix(i)] = 1; r[iL] = -1; Ce.append(r); d.append(0)
    for i in R:
        r = np.zeros(N); r[ix(i)] = 1; r[iR] = -1; Ce.append(r); d.append(-ws[i])
    for i in B:
        r = np.zeros(N); r[iy(i)] = 1; r[iB] = -1; Ce.append(r); d.append(0)
    for i in T:
        r = np.zeros(N); r[iy(i)] = 1; r[iT] = -1; Ce.append(r); d.append(-hs[i])
    # straight lines: neighbours of equal height in a row share their bottom edge, neighbours of equal width in a column share their left edge
    for i, j, _ in hadj:
        if abs(hs[i] - hs[j]) < 0.05:
            r = np.zeros(N); r[iy(i)] = 1; r[iy(j)] = -1; Ce.append(r); d.append(0)
    for i, j, _ in vadj:
        if abs(ws[i] - ws[j]) < 0.05:
            r = np.zeros(N); r[ix(i)] = 1; r[ix(j)] = -1; Ce.append(r); d.append(0)
    Ce, d = np.array(Ce), np.array(d)
    # equality-constrained least squares by nullspace elimination: u = u0 + Z v, with Ce u0 = d and Ce Z = 0 (robust to redundant constraints)
    u0 = np.linalg.lstsq(Ce, d, rcond=None)[0]
    U, sv, Vt = np.linalg.svd(Ce)
    rank = int((sv > 1e-9).sum())
    Z = Vt[rank:].T
    v = np.linalg.lstsq(A @ Z, b - A @ u0, rcond=None)[0]
    u = u0 + Z @ v
    assert np.allclose(Ce @ u, d, atol=1e-6), "flush constraints not met"
    pos = [(u[ix(i)], u[iy(i)], ws[i], hs[i], items[i][4]) for i in range(n)]
    gaps = [u[ix(j)] - u[ix(i)] - ws[i] for i, j, _ in hadj] + [u[iy(j)] - u[iy(i)] - hs[i] for i, j, _ in vadj]
    margins = (u[iL], FACE - u[iR], u[iB], FACE - u[iT])
    return pos, u[ig], gaps, margins


def draw(ax, pos, title, info):
    D.carbon(ax)
    for x, y, w, h, name in pos:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=D.COL[name], edgecolor="#6f86b8", lw=0.5, zorder=2))
        if name.startswith("SM531"):
            for i in range(1, 4):
                ax.plot([x + i * w / 4] * 2, [y, y + h], color="#6f86b8", lw=0.25, zorder=3)
                ax.plot([x, x + w], [y + i * h / 4] * 2, color="#6f86b8", lw=0.25, zorder=3)
        ax.text(x + w / 2, y + h / 2, f"{D.SHORT[name]}\n{w:g} x {h:g}", ha="center", va="center", fontsize=5.2, color="#e8eefc", zorder=4)
    ax.add_patch(Rectangle((0, 0), FACE, FACE, fill=False, edgecolor="#bbbbbb", lw=1.2, zorder=5))
    ax.set_title(title, fontsize=9, loc="left", pad=8)
    ax.text(0, -4, info, fontsize=6.3, va="top", color="#222")
    ax.set_xlim(-3, FACE + 3); ax.set_ylim(-22, FACE + 3); ax.set_aspect("equal"); ax.axis("off")


if __name__ == "__main__":
    layouts = (("Layout 1", {"SM401K08TF 90x40": 2, "SM531K08TFS 89x52": 1, "SM940K09L 44.5x21.5": 6}),
               ("Layout 2", {"SM531K08TFS 89x52": 1, "SM811K08TF 89x78": 1, "SM940K09L 44.5x21.5": 6}))
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.4), facecolor="white")
    for ax, (name, counts) in zip(axs, layouts):
        items, bw, bh = initial(counts)
        pos, g, gaps, margins = solve(items, bw, bh)
        xs = [p[0] for p in pos]; xe = [p[0] + p[2] for p in pos]; ys = [p[1] for p in pos]; ye = [p[1] + p[3] for p in pos]
        gmin, gmax = min(gaps), max(gaps)
        area = sum(p[2] * p[3] for p in pos) / 100
        print(f"{name}: block {max(xe) - min(xs):.2f} x {max(ye) - min(ys):.2f} mm, line target g = {g:.2f} mm")
        print(f"  gaps between parts: min {gmin:.2f}, max {gmax:.2f}, mean {np.mean(gaps):.2f}, spread {gmax - gmin:.2f} mm ({len(gaps)} neighbour pairs)")
        print(f"  margins (left, right, bottom, top): " + ", ".join(f"{m:.2f}" for m in margins) + " mm")
        print(f"  cells {area:.1f} cm2 = {area * 100 / FACE ** 2 * 100:.1f}% of the face (same parts, so same area as before)")
        for p in sorted(pos, key=lambda p: (-p[1], p[0])):
            print(f"    {p[4]:24s} at x {p[0]:6.2f}, y {p[1]:6.2f}, {p[2]:g} x {p[3]:g}")
        info = (f"line target {g:.2f} mm; gaps {gmin:.2f} to {gmax:.2f} mm (spread {gmax - gmin:.2f}); margins "
                + ", ".join(f"{m:.2f}" for m in margins) + f" mm\n{area:.1f} cm2 = {area * 100 / FACE ** 2 * 100:.1f}% of the face; block {max(xe) - min(xs):.1f} x {max(ye) - min(ys):.1f} mm (perfect rectangle)")
        draw(ax, pos, f"{name}: spread to a perfect rectangle", info)
    fig.suptitle("IXOLAR option spread out: 140 x 140 mm face seen from outside, parts at their datasheet sizes, lines as uniform as possible (mm)", fontsize=10, y=0.99)
    fig.text(0.5, 0.01, "Same parts and neighbours as before; line thickness and carbon border are pulled to one value, the outer outline is exactly rectangular. Part tolerance is +-0.3 mm per side. "
             "Only the SM531K08TFS shows its sub-cell grid. Carbon texture illustrative.", ha="center", fontsize=6.3, color="#444")
    out = HERE / "out"
    fig.savefig(out / "cell_spread_ixolar.png", dpi=160, bbox_inches="tight")
    fig.savefig(out / "cell_spread_ixolar.svg", bbox_inches="tight")
    print("wrote", out / "cell_spread_ixolar.png")


# ---------------------------------------------------------------------------------------------------------------------------
# Symmetric arrangement of Layout 1 (owner's sketch, 2026-11-12): the same nine parts, mirror symmetric left-right and top-bottom:
# a row of three SM940K09L on top, a row of three at the bottom, and between them SM401K08TF (standing), SM531K08TFS (standing), SM401K08TF.
# The packing search found the same area for this arrangement (same parts) but did not prefer it; symmetry was not in its objective.
# ---------------------------------------------------------------------------------------------------------------------------
def symmetric_items():
    s9, s5, s4 = "SM940K09L 44.5x21.5", "SM531K08TFS 89x52", "SM401K08TF 90x40"
    items = []
    for row_y in (0.0, 21.5 + 90.0):
        for k in range(3):
            items.append((44.5 * k, row_y, 44.5, 21.5, s9))
    items.append((0.0, 21.5, 40.0, 90.0, s4))
    items.append((40.0, 21.5, 52.0, 89.0, s5))
    items.append((92.0, 21.5, 40.0, 90.0, s4))
    return items, 133.5, 133.0


if __name__ == "__main__":
    items, bw, bh = symmetric_items()
    fig, ax = plt.subplots(1, 1, figsize=(7.2, 7.4), facecolor="white")
    pos, g, gaps, margins = solve(items, bw, bh, margin_weight=1.0)
    xs = [p[0] for p in pos]; xe = [p[0] + p[2] for p in pos]; ys = [p[1] for p in pos]; ye = [p[1] + p[3] for p in pos]
    area = sum(p[2] * p[3] for p in pos) / 100
    print("\nSYMMETRIC LAYOUT 1 (owner's sketch)")
    print(f"  block {max(xe) - min(xs):.2f} x {max(ye) - min(ys):.2f} mm, line target g = {g:.2f} mm")
    print(f"  gaps between parts: min {min(gaps):.2f}, max {max(gaps):.2f}, mean {np.mean(gaps):.2f}, spread {max(gaps) - min(gaps):.2f} mm ({len(gaps)} neighbour pairs)")
    print(f"  margins (left, right, bottom, top): " + ", ".join(f"{m:.2f}" for m in margins) + " mm")
    print(f"  cells {area:.1f} cm2 = {area * 100 / FACE ** 2 * 100:.1f}% of the face")
    cx = FACE / 2
    mism = max(abs((p[0] + p[2] / 2 - cx) + 0) for p in pos if False) if False else 0
    # symmetry check: reflect every part about the face centre lines and look for a partner of the same kind at the same place
    def has(x, y, w, h, name):
        return any(abs(q[0] - x) < 0.02 and abs(q[1] - y) < 0.02 and q[4] == name and abs(q[2] - w) < 1e-6 for q in pos)
    ok_lr = all(has(FACE - p[0] - p[2], p[1], p[2], p[3], p[4]) for p in pos)
    ok_tb = all(has(p[0], FACE - p[1] - p[3], p[2], p[3], p[4]) for p in pos)
    print(f"  mirror symmetric left-right: {ok_lr}; top-bottom: {ok_tb}")
    rows = sorted({round(p[1], 2) for p in pos})
    for p in sorted(pos, key=lambda p: (-p[1], p[0])):
        print(f"    {p[4]:24s} at x {p[0]:6.2f}, y {p[1]:6.2f}, {p[2]:g} x {p[3]:g}")
    info = (f"line target {g:.2f} mm; gaps {min(gaps):.2f} to {max(gaps):.2f} mm (spread {max(gaps) - min(gaps):.2f}); margins "
            + ", ".join(f"{m:.2f}" for m in margins) + f" mm\n{area:.1f} cm2 = {area * 100 / FACE ** 2 * 100:.1f}% of the face; block {max(xe) - min(xs):.1f} x {max(ye) - min(ys):.1f} mm; mirror symmetric: {ok_lr and ok_tb}")
    draw(ax, pos, "Layout 1, symmetric arrangement (owner's sketch)", info)
    out = HERE / "out"
    fig.savefig(out / "cell_spread_symmetric.png", dpi=160, bbox_inches="tight")
    fig.savefig(out / "cell_spread_symmetric.svg", bbox_inches="tight")
    print("wrote", out / "cell_spread_symmetric.png")
