"""Solar cell layout as a monochrome Mondrian: rectangular cells separated by lines of one width, the same between cell and cell and between cell and face edge.

Run: python3 hardware/body/cell_layout.py   (no CAD needed; writes SVG previews to hardware/body/out/cell_layout_*.svg, our own drawings, safe to track)

Owner's brief (2026-11-12): the project is now an interpretation of the nanorover, not a replica, so the original's cell pattern no longer matters. Maximise the cell
area against the face area, with every gap (cell to cell, cell to face edge) the same, to get lines of equal thickness dividing an area like a monochrome Mondrian painting.

Method: a layout is a guillotine partition (every cut runs the full width or height of the rectangle it divides), the kind a Mondrian is made of. Cut positions are solved
so that every cell on a face has the SAME area. Why equal area: cells on one face are wired in series (one cell gives about 0.5 V), and a series string carries only the
current of its weakest cell, which scales with area, so unequal cells waste the bigger ones (ASM: 0.5 V per cell, area-proportional current, uniform light on a face).
The shapes still differ (different aspect ratios), which is what gives the Mondrian look. The gap g is the only free number; the minimum cell size and aspect limits are mine.

SRC = a cited source, ASM = my assumption (docs/body-redesign.md).
"""
import itertools
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
G = 2.0          # mm, the line width (ASM: the carbon rib between cell pockets; forged carbon's minimum wall is about 1.5 mm, owner's earlier figure from vendor pages)
MIN_DIM = 15.0   # mm, smallest cell dimension (ASM: narrower strips break and lose more to their edges)
MAX_ASPECT = 4.0 # longest side over shortest side of a cell (ASM)
SUN_MW_CM2 = 20.0  # mW per cm2 of mono-Si in full sun (ASM, 20% of 100 mW/cm2; as cell_split.py)
FACE = 140.0     # mm, the top and bottom faces are 140 x 140


# ---------------- guillotine trees ----------------
# a tree is None (a cell) or (direction, left, right): 'V' = vertical cut (left | right), 'H' = horizontal cut (bottom / top)
def trees(k):
    if k == 1:
        yield None
        return
    for k1 in range(1, k // 2 + 1):
        for d in "VH":
            for a in trees(k1):
                for b in trees(k - k1):
                    yield (d, a, b)


def leaves(t):
    return 1 if t is None else leaves(t[1]) + leaves(t[2])


def place(t, x, y, w, h, fr, ids, out, g):
    """Lay the tree out in the rectangle; fr[i] is the share of (dimension - g) that the first child gets at internal node i (preorder numbering)."""
    if t is None:
        out.append((x, y, w, h))
        return
    i = next(ids)
    d, a, b = t
    if d == "V":
        w1 = (w - g) * fr[i]
        place(a, x, y, w1, h, fr, ids, out, g)
        place(b, x + w1 + g, y, w - g - w1, h, fr, ids, out, g)
    else:
        h1 = (h - g) * fr[i]
        place(a, x, y, w, h1, fr, ids, out, g)
        place(b, x, y + h1 + g, w, h - g - h1, fr, ids, out, g)


def internal_count(t):
    return 0 if t is None else 1 + internal_count(t[1]) + internal_count(t[2])


def initial_fr(t):
    """Preorder list of the leaf-count share of each node's first child."""
    r = []
    def walk(u):
        if u is None:
            return
        r.append(leaves(u[1]) / leaves(u))
        walk(u[1]); walk(u[2])
    walk(t)
    return r


def solve_equal(t, w, h, g, sweeps=8):
    """Cut shares such that every cell has the same area (bisection on each node in turn)."""
    fr = initial_fr(t)
    n = len(fr)
    # leaf index ranges of each internal node's children, in preorder
    spans = []
    def walk(u, start):
        if u is None:
            return start + 1
        i = len(spans); spans.append(None)
        m = walk(u[1], start)
        e = walk(u[2], m)
        spans[i] = (start, m, e)
        return e
    walk(t, 0)

    def cells():
        out = []
        place(t, g, g, w - 2 * g, h - 2 * g, fr, iter(range(n)), out, g)
        return out

    for _ in range(sweeps):
        for i in range(n):
            s, m, e = spans[i]
            lo, hi = 0.02, 0.98
            for _ in range(26):
                mid = (lo + hi) / 2
                fr[i] = mid
                c = cells()
                left = sum(r[2] * r[3] for r in c[s:m]) / (m - s)
                right = sum(r[2] * r[3] for r in c[m:e]) / (e - m)
                if left < right:
                    lo = mid
                else:
                    hi = mid
            fr[i] = (lo + hi) / 2
    return fr, cells()


def describe(cells, w, h):
    areas = [r[2] * r[3] for r in cells]
    asp = [max(r[2], r[3]) / min(r[2], r[3]) for r in cells]
    return sum(areas) / (w * h), min(min(r[2], r[3]) for r in cells), max(asp), (max(areas) - min(areas)) / (sum(areas) / len(areas)), asp


def variety(asp):
    """Spread of the cells' shapes: standard deviation of log aspect ratio (0 = all alike)."""
    l = [math.log(a) for a in asp]
    m = sum(l) / len(l)
    return math.sqrt(sum((v - m) ** 2 for v in l) / len(l))


def canon(cells):
    """A key that is the same for mirror images (so duplicates can be dropped)."""
    def k(cs):
        return tuple(sorted((round(r[0]), round(r[1]), round(r[2]), round(r[3])) for r in cs))
    W = max(r[0] + r[2] for r in cells) + G
    Hh = max(r[1] + r[3] for r in cells) + G
    forms = [cells,
             [(W - r[0] - r[2], r[1], r[2], r[3]) for r in cells],
             [(r[0], Hh - r[1] - r[3], r[2], r[3]) for r in cells],
             [(W - r[0] - r[2], Hh - r[1] - r[3], r[2], r[3]) for r in cells]]
    return min(k(f) for f in forms)


def search(k, w, h, g, keep=60):
    """All guillotine partitions into k cells: rank by cell area first, with a first cheap estimate and then the exact equal-area solve."""
    est = []
    for t in trees(k):
        fr = initial_fr(t)
        n = len(fr)
        out = []
        place(t, g, g, w - 2 * g, h - 2 * g, fr, iter(range(n)), out, g)
        if min(min(r[2], r[3]) for r in out) < 0.7 * MIN_DIM or max(max(r[2], r[3]) / min(r[2], r[3]) for r in out) > 2.0 * MAX_ASPECT:
            continue                                   # cheap pre-filter on the first-guess layout
        est.append((sum(r[2] * r[3] for r in out), t))
    est.sort(key=lambda p: -p[0])
    res, seen = [], set()
    for _, t in est:
        fr, cs = solve_equal(t, w, h, g)
        frac, mind, maxa, spread, asp = describe(cs, w, h)
        if mind < MIN_DIM or maxa > MAX_ASPECT or spread > 0.02:
            continue
        key = canon(cs)
        if key in seen:
            continue
        seen.add(key)
        res.append((frac, variety(asp), t, cs, asp))
        if len(res) >= keep:
            break
    return res


# ---------------- drawings ----------------
def svg(path, w, h, cells, extra=None, scale=4.0):
    """Face in dark carbon grey, cells black-blue; extra = [(x, y, w, h, colour, label)] drawn as panels."""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * scale:.0f}" height="{h * scale:.0f}" viewBox="0 0 {w} {h}">',
             f'<rect width="{w}" height="{h}" fill="#3a3a3a"/>']
    for x, y, cw, ch in cells:
        parts.append(f'<rect x="{x:.2f}" y="{h - y - ch:.2f}" width="{cw:.2f}" height="{ch:.2f}" fill="#0f1b3a"/>')
        parts.append(f'<text x="{x + cw / 2:.1f}" y="{h - y - ch / 2:.1f}" font-size="4" fill="#8aa" text-anchor="middle" dominant-baseline="middle">{cw:.0f}x{ch:.0f}</text>')
    for x, y, cw, ch, col, lab in (extra or []):
        parts.append(f'<rect x="{x:.2f}" y="{h - y - ch:.2f}" width="{cw:.2f}" height="{ch:.2f}" fill="{col}"/>')
        parts.append(f'<text x="{x + cw / 2:.1f}" y="{h - y - ch / 2:.1f}" font-size="4" fill="#ddd" text-anchor="middle" dominant-baseline="middle">{lab}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts))


def mw_power(area_mm2):
    return area_mm2 / 100 * SUN_MW_CM2 / 1000   # W


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    face_area = FACE * FACE
    print(f"Top / bottom face {FACE:.0f} x {FACE:.0f} mm, line width g = {G} mm. Previous layout (black unit's photo): 127.6 cm2 = {127.6 * 100 / face_area * 100:.1f}% of the face, "
          f"{mw_power(127.6 * 100):.2f} W in full sun.")

    print("\n1. What each extra cut costs (the line is the only loss; the borders alone are 4 lines):")
    for g in (1.5, 2.0, 3.0, 4.0):
        one = (FACE - 2 * g) ** 2 / face_area * 100
        cut = g * (FACE - 2 * g) / face_area * 100
        print(f"   g = {g:.1f} mm: border only {one:.1f}% of the face; each full-length cut costs {cut:.2f} points; a 14-cell 5 x 3 grid-like layout would keep {(FACE - 6 * g) * (FACE - 4 * g) / face_area * 100:.1f}%")

    print("\n2. Equal-area cells by number of cells (best found, g = 2 mm, min side 15 mm, aspect <= 4):")
    best = {}
    for k in range(4, 11):
        r = search(k, FACE, FACE, G, keep=40)
        if not r:
            print(f"   {k:2d} cells: none met the limits")
            continue
        top = max(r, key=lambda p: p[0])
        v = max(r, key=lambda p: p[1] - 0.2 * (top[0] - p[0]) * 100)    # most varied, with a small penalty for losing area
        best[k] = (top, v, r)
        print(f"   {k:2d} cells: best area {top[0] * 100:5.1f}% ({top[0] * face_area / 100:5.1f} cm2, {mw_power(top[0] * face_area):.2f} W sun, string {k * 0.5:.1f} V; cell {top[3][0][2] * top[3][0][3] / 100:5.1f} cm2), "
              f"most varied {v[0] * 100:5.1f}% (shape spread {v[1]:.2f}, best {top[1]:.2f}); {len(r)} layouts kept")

    # candidates to look at: 8 cells (4 V string); save the top-area, the most varied, and a middle one
    k = 8
    top, v, r = best[k]
    mid = sorted(r, key=lambda p: -p[1])[len(r) // 3]
    for name, p in (("topArea", top), ("mostVaried", v), ("middle", mid)):
        svg(OUT / f"cell_layout_{k}_{name}.svg", FACE, FACE, p[3])
        print(f"   wrote cell_layout_{k}_{name}.svg: {p[0] * 100:.1f}%, shape spread {p[1]:.2f}, cells (mm): "
              + ", ".join(f"{c[2]:.0f}x{c[3]:.0f}" for c in sorted(p[3], key=lambda c: -c[2] * c[3])))

    print("\n3. End faces (140 x 60): the 60 x 60 mm window square (or antenna square) is a panel with the same lines around it, so it is (60 - 2g) square")
    for g in (1.5, 2.0, 3.0):
        pw = 60 - 2 * g
        rw, rh = 80 - g, 60 - 2 * g          # the cell zone beside it: from the face edge (g in) to the panel's gap
        for n in (1, 2, 3):
            ww = (rw - (n - 1) * g) / n
            area = n * ww * rh
            print(f"   g = {g:.1f} mm: panel {pw:.0f} x {pw:.0f} mm; {n} cell(s) of {ww:.1f} x {rh:.0f} mm = {area / 100:.1f} cm2 ({area / (140 * 60) * 100:.0f}% of the end face)")
    g = G
    ww = (80 - g - g) / 2
    # the face spans x = -70..70 in body coordinates; drawn from 0, the window square (centre x = +40) is at 80 + g .. 140 - g
    cells = [(g + i * (ww + g), g, ww, 60 - 2 * g) for i in range(2)]
    panel = [(80 + g, g, 60 - 2 * g, 60 - 2 * g, "#555", "window panel")]
    svg(OUT / "cell_layout_end_face.svg", 140, 60, cells, extra=panel)
    print("   wrote cell_layout_end_face.svg (two cells and the window panel, g = 2 mm)")
