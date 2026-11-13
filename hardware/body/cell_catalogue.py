"""Fit a face from REAL cells: which combination of existing cells fills the 140 x 140 mm face the most, with equal lines between cells and little or no cutting.

Run: python3 hardware/body/cell_catalogue.py   (no CAD; writes SVGs to hardware/body/out/cell_catalogue_*.svg)

Owner's brief (2026-11-12, replacing the first approach in cell_layout.py, which solved for ideal rectangles): start from cells that exist, cut as little as possible and waste
as little of a complete cell as possible; the margin at the face edge may differ from the line between cells.

Two routes are compared:
  A. Whole, uncut parts of the catalogue below (fixed sizes, any number of each), laid out as a guillotine Mondrian with the same line g between parts. A part cannot be stretched,
     so a cut's two sides must have the same extent; a mismatch up to TOL is allowed and shows up as a slightly wider line (the shorter side's gap grows by that much).
     The slack between the parts' bounding box and the face is the edge margin (it may differ from g, but is kept within limits and nearly equal on all sides).
  B. Bare wafer cells, cut: how much silicon a face needs against what the wafer gives (utilisation), and the standard half and quarter cuts.

SRC = a cited source (third-party listings found by search, NOT manufacturer drawings, sizes are package outlines for the packaged parts); ASM = my assumption.
"""
import itertools
import math
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
FACE = 140.0
TOL = 0.5                   # mm, extents that differ by less than this are treated as matching (ASM: the listings give sizes to 0.5 to 1 mm)
M_MIN, M_MAX, M_DIFF = 1.5, 8.0, 1.0   # edge margin limits and the largest difference between the margins (ASM)

# name: (width, height) mm. Packaged parts include their own border and leads, so the visible silicon is smaller than the outline (not known).
CATALOGUE = {
    # Anysolar IXOLAR, monocrystalline, packaged (SRC: microchipusa and Digi-Key listings, third party; thickness 1.3 to 2 mm)
    "IXOLAR 90x79 (SLMD481H12)": (90.0, 79.0),
    "IXOLAR 89x78": (89.0, 78.0),
    "IXOLAR 89x67 (SLMD481H10)": (89.0, 67.0),
    "IXOLAR 89x52": (89.0, 52.0),
    "IXOLAR 58x58 (SLMD321H09L)": (58.0, 58.0),
    "IXOLAR 63x23": (63.0, 23.0),
    "IXOLAR 44.5x21.5 (SLMD960H09L)": (44.5, 21.5),
    "IXOLAR 35x42 (SLMD960H12)": (35.0, 42.0),
    "IXOLAR 35x22 (SLMD600H10)": (35.0, 22.0),
    "IXOLAR 32.5x33 (SLMD720H12L)": (32.5, 33.0),
    # others (SRC: Ward's Science listing; Shenzhen Sunfield listing)
    "Ward's mono 75x60": (75.0, 60.0),
    "Sunfield mono 52x29": (52.0, 29.0),
}


def pack(g, nmax=7, catalogue=CATALOGUE, limit=FACE - 2 * M_MIN):
    """All guillotine blocks of up to nmax whole parts with line g. Returns {size key: (area, n, tree)} keeping the best area per size."""
    q = lambda v: round(v * 2)                         # 0.5 mm buckets
    S = [dict() for _ in range(nmax + 1)]
    for name, (w, h) in catalogue.items():
        for (a, b) in ((w, h), (h, w)):
            if a <= limit and b <= limit:
                S[1][(q(a), q(b))] = (a * b, 1, ("P", name, a, b), a, b)
    allb = dict(S[1])
    for n in range(2, nmax + 1):
        for a in range(1, n // 2 + 1):
            b = n - a
            # index the second set by height and by width
            byh, byw = {}, {}
            for key, v in S[b].items():
                byh.setdefault(key[1], []).append(v)
                byw.setdefault(key[0], []).append(v)
            for v1 in S[a].values():
                _, _, _, w1, h1 = v1
                for dq in range(-(int(TOL * 2) + 1), int(TOL * 2) + 2):      # bucket neighbours out to the tolerance
                    for v2 in byh.get(q(h1) + dq, ()):            # side by side (cut is vertical): heights match
                        w2, h2 = v2[3], v2[4]
                        if abs(h1 - h2) > TOL:
                            continue
                        W, H = w1 + g + w2, max(h1, h2)
                        if W <= limit and H <= limit:
                            ar = v1[0] + v2[0]
                            if ar / (W * H) >= 0.78:
                                k = (q(W), q(H))
                                if k not in S[n] or S[n][k][0] < ar:
                                    S[n][k] = (ar, n, ("V", v1[2], v2[2], g), W, H)
                    for v2 in byw.get(q(w1) + dq, ()):            # stacked (cut is horizontal): widths match
                        w2, h2 = v2[3], v2[4]
                        if abs(w1 - w2) > TOL:
                            continue
                        W, H = max(w1, w2), h1 + g + h2
                        if W <= limit and H <= limit:
                            ar = v1[0] + v2[0]
                            if ar / (W * H) >= 0.78:
                                k = (q(W), q(H))
                                if k not in S[n] or S[n][k][0] < ar:
                                    S[n][k] = (ar, n, ("H", v1[2], v2[2], g), W, H)
        allb.update({k: v for k, v in S[n].items() if k not in allb or allb[k][0] < v[0]})
    return S


def parts_of(tree):
    if tree[0] == "P":
        return [tree[1]]
    return parts_of(tree[1]) + parts_of(tree[2])


def draw(tree, x, y, g, out):
    if tree[0] == "P":
        out.append((x, y, tree[2], tree[3], tree[1]))
        return tree[2], tree[3]
    d, a, b, _ = tree
    if d == "V":
        w1, h1 = draw(a, x, y, g, out)
        w2, h2 = draw(b, x + w1 + g, y, g, out)
        return w1 + g + w2, max(h1, h2)
    w1, h1 = draw(a, x, y, g, out)
    w2, h2 = draw(b, x, y + h1 + g, g, out)
    return max(w1, w2), h1 + g + h2


def svg(path, w, h, items, ox, oy, scale=4.0):
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * scale:.0f}" height="{h * scale:.0f}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#3a3a3a"/>']
    for x, y, cw, ch, name in items:
        p.append(f'<rect x="{ox + x:.2f}" y="{h - (oy + y) - ch:.2f}" width="{cw:.2f}" height="{ch:.2f}" fill="#0f1b3a"/>')
        p.append(f'<text x="{ox + x + cw / 2:.1f}" y="{h - (oy + y) - ch / 2:.1f}" font-size="3.2" fill="#8aa" text-anchor="middle" dominant-baseline="middle">{cw:.0f}x{ch:.0f}</text>')
    p.append("</svg>")
    path.write_text("\n".join(p))


def results(g, nmax=7, show=4):
    S = pack(g, nmax)
    cands = []
    for n in range(1, nmax + 1):
        for ar, nn, tree, W, H in S[n].values():
            mx, my = (FACE - W) / 2, (FACE - H) / 2
            if M_MIN <= mx <= M_MAX and M_MIN <= my <= M_MAX and abs(mx - my) <= M_DIFF:
                cands.append((ar / FACE ** 2, nn, W, H, mx, my, tree))
    cands.sort(key=lambda c: (-c[0], c[1]))
    return cands[:show], len(cands)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print("ROUTE A: whole, uncut catalogue parts on a 140 x 140 mm face (package outline taken as the cell; true silicon area is smaller)")
    print(" The sizes are fixed, so rows and columns rarely match; what is given up is the edge margin: the best layout for each limit on the margins (g = line between parts)")
    for g in (2.0, 3.0):
        S = pack(g, 8)
        allb = [(ar / FACE ** 2, nn, W, H, tree) for n in range(1, 9) for ar, nn, tree, W, H in S[n].values()]
        print(f"\n line g = {g:.1f} mm ({len(allb)} layouts found):")
        for mmax, diff in ((8, 1), (12, 1), (12, 3), (70, 70)):
            c = [b for b in allb if M_MIN <= (FACE - b[2]) / 2 <= mmax and M_MIN <= (FACE - b[3]) / 2 <= mmax and abs((FACE - b[2]) / 2 - (FACE - b[3]) / 2) <= diff]
            lab = f"margins {M_MIN} to {mmax} mm, within {diff} mm of each other" if mmax < 70 else "any margins from 1.5 mm (any difference)"
            if not c:
                print(f"  {lab}: none")
                continue
            f, n, W, H, t = max(c, key=lambda b: (b[0], -b[1]))
            pts = parts_of(t)
            print(f"  {lab}: {f * 100:4.1f}% ({f * FACE ** 2 / 100:5.1f} cm2), {n} parts, block {W:.1f} x {H:.1f}, margins {(FACE - W) / 2:.1f} and {(FACE - H) / 2:.1f} mm: "
                  + "; ".join(f"{pts.count(k)} x {k}" for k in sorted(set(pts))))
            items = []
            draw(t, 0, 0, g, items)
            svg(OUT / f"cell_catalogue_A_g{g:.0f}_m{mmax}.svg", FACE, FACE, items, (FACE - W) / 2, (FACE - H) / 2)

    print("\nROUTE B: bare wafer cells, cut. Silicon needed for the earlier 8-cell Mondrian: 174.9 cm2 per face (89.2%); the cut lines between pieces cost only a kerf, so the silicon that is lost")
    print(" is what lies outside the 136 x 136 mm region (the lines themselves can be left uncut by spacing the pieces on the carbon).")
    print("  wafer (SRC: standard formats; corners are truncated, so the real area is below side^2)")
    formats = (("125 pseudo-square (SunPower C60 size)", 125.0, 160.0), ("156.75 pseudo-square (M2)", 156.75, 210.0), ("166 pseudo-square (M6)", 166.0, 223.0))
    for name, a, diag in formats:
        # corner cut: the square of side a with corners trimmed to a circle of diameter diag; leg of the cut triangle
        half_diag = a * math.sqrt(2) / 2
        cut = max(half_diag - diag / 2, 0)
        leg = cut * math.sqrt(2)
        area = a * a - 2 * leg * leg
        corner_ok = math.hypot(68, 68) <= diag / 2
        print(f"  {name}: area {area / 100:6.1f} cm2 (corner legs {leg:4.1f} mm); a 136 x 136 mm region fits: {str(a >= 136 and corner_ok):5s}"
              + (f"; one wafer per face uses {136 * 136 / area * 100:4.1f}% of its silicon (the rest is the rim)" if a >= 136 and corner_ok else
                 f"; needs at least two wafers per face: {2 * area / 100:6.1f} cm2 of silicon for {174.9:5.1f} cm2 used = {174.9 * 100 / (2 * area) * 100:4.1f}% utilisation"))
    print("\n  Straight cuts of a 125 mm cell (the chamfered corners stay, so each piece keeps 0 to 2 notches of about 12 mm):")
    c60 = 125.0 ** 2 - 2 * 11.9 ** 2
    for label, pieces, w, h in (("2 halves, 62.5 x 125", 2, 62.5, 125.0), ("4 quarters, 62.5 x 62.5", 4, 62.5, 62.5), ("3 thirds, 41.7 x 125", 3, 41.7, 125.0)):
        if pieces == 4:
            W, H = 2 * w + 2.0, 2 * h + 2.0
        elif pieces == 2:
            W, H = 2 * w + 2.0, h
        else:
            W, H = 3 * w + 4.0, h
        print(f"   {label}: block {W:.1f} x {H:.1f} mm, margins {(FACE - W) / 2:.1f} and {(FACE - H) / 2:.1f} mm, silicon {c60 / 100:.1f} cm2 = {c60 / FACE ** 2 * 100:.1f}% of the face, zero waste (kerf only)")


# ---------------------------------------------------------------------------------------------------------------------------
# Rectangular cell field (owner, 2026-11-12): the block of cells need not be square; one pair of margins can equal the line g
# (cells run to the edge with the same thickness as the lines) and the other pair of margins can be wider.
# ---------------------------------------------------------------------------------------------------------------------------
C60_CM2 = 153.4          # silicon area of one 125 mm truncated-square cell (computed above)
C60_SLICES = {           # name: (w, h, fraction of one cell); straight cuts only, the truncated corners (about 12 mm) stay on some pieces
    "C60 whole 125x125": (125.0, 125.0, 1.0),
    "C60 half 62.5x125": (62.5, 125.0, 0.5),
    "C60 third 41.7x125": (41.667, 125.0, 1 / 3),
    "C60 quarter-strip 31.25x125": (31.25, 125.0, 0.25),
    "C60 quarter 62.5x62.5": (62.5, 62.5, 0.25),
    "C60 sixth 41.7x62.5": (41.667, 62.5, 1 / 6),
    "C60 eighth 31.25x62.5": (31.25, 62.5, 0.125),
}


def rect_field(allb, g, one_margin_equals_line=True):
    """Best fill for 1 type, 2 types, any number of types, where at least one pair of margins is within 0.5 mm of g."""
    out = {}
    for f, n, W, H, t in allb:
        mx, my = (FACE - W) / 2, (FACE - H) / 2
        if mx < M_MIN or my < M_MIN:
            continue
        if one_margin_equals_line and not (abs(mx - g) <= 0.6 or abs(my - g) <= 0.6):
            continue
        k = len(set(parts_of(t)))
        for lim in (1, 2, 99):
            if k <= lim and (lim not in out or (f, -n) > (out[lim][0], -out[lim][1])):
                out[lim] = (f, n, W, H, mx, my, t)
    return out


if __name__ == "__main__":
    print("\n\nRECTANGULAR FIELD: one pair of margins equal to the line g, the other pair free (cells run edge to edge in one direction)")
    for g in (2.0, 3.0):
        S = pack(g, 8)
        allb = [(ar / FACE ** 2, nn, W, H, tree) for n in range(1, 9) for ar, nn, tree, W, H in S[n].values()]
        res = rect_field(allb, g)
        print(f"\n IXOLAR and other whole parts, g = {g:.0f} mm:")
        for lim, lab in ((1, "one part type"), (2, "up to two types"), (99, "any types")):
            if lim not in res:
                print(f"  {lab}: none")
                continue
            f, n, W, H, mx, my, t = res[lim]
            pts = parts_of(t)
            print(f"  {lab}: {f * 100:4.1f}% ({f * FACE ** 2 / 100:5.1f} cm2), {n} parts, block {W:.1f} x {H:.1f}, margins {mx:.1f} and {my:.1f} mm: "
                  + "; ".join(f"{pts.count(k)} x {k}" for k in sorted(set(pts))))
    print("\n Slices of 125 mm cells (straight cuts); silicon = fraction of a cell x 153.4 cm2; waste = the unused part of the last cell")
    cat = {k: (w, h) for k, (w, h, _) in C60_SLICES.items()}
    frac = {k: fr for k, (_, _, fr) in C60_SLICES.items()}
    for g in (2.0, 3.0):
        S = pack(g, 8, catalogue=cat)
        best = {}
        for n in range(1, 9):
            for ar, nn, tree, W, H in S[n].values():
                pts = parts_of(tree)
                cells = sum(frac[p] for p in pts)
                used = math.ceil(cells - 1e-6)
                waste = (used - cells) / used
                mx, my = (FACE - W) / 2, (FACE - H) / 2
                if mx < M_MIN or my < M_MIN:
                    continue
                key = used
                si = cells * C60_CM2
                if key not in best or si > best[key][0]:
                    best[key] = (si, waste, nn, W, H, mx, my, pts)
        print(f"  g = {g:.0f} mm: best by silicon on the face, by number of cells bought")
        for used, (si, waste, nn, W, H, mx, my, pts) in sorted(best.items()):
            print(f"    {used} cell(s): {si:5.1f} cm2 = {si / (FACE ** 2 / 100) * 100:4.1f}% of the face, waste {waste * 100:3.0f}%, {nn} pieces, block {W:.1f} x {H:.1f}, margins {mx:.1f} and {my:.1f} mm: "
                  + "; ".join(f"{pts.count(k)} x {k}" for k in sorted(set(pts))))


# ---------------------------------------------------------------------------------------------------------------------------
# No gaps between cells (owner, 2026-11-12): cells butt together; only the margin at the face edge remains.
# g = 0 is the ideal; 0.3 mm stands for a practical joint (ASM: cells that touch can chip, and silicon and carbon expand differently).
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n\nNO GAPS BETWEEN CELLS (g = 0 and a practical 0.3 mm give the same answers)")
    for g in (0.0, 0.3):
        S = pack(g, 8)
        allb = [(ar / FACE ** 2, nn, W, H, tree) for n in range(1, 9) for ar, nn, tree, W, H in S[n].values()]
        print(f"\n whole parts, joint {g} mm:")
        for lim, lab in ((1, "one part type"), (2, "up to two types")):
            c = [b for b in allb if M_MIN <= (FACE - b[2]) / 2 and M_MIN <= (FACE - b[3]) / 2 and len(set(parts_of(b[4]))) <= lim]
            f, n, W, H, t = max(c, key=lambda b: (b[0], -b[1]))
            pts = parts_of(t)
            print(f"  {lab}: {f * 100:4.1f}% ({f * FACE ** 2 / 100:5.1f} cm2), {n} parts, block {W:.1f} x {H:.1f}, margins {(FACE - W) / 2:.1f} and {(FACE - H) / 2:.1f} mm: "
                  + "; ".join(f"{pts.count(k)} x {k}" for k in sorted(set(pts))))
    cat = {k: (w, h) for k, (w, h, _) in C60_SLICES.items()}
    frac = {k: fr for k, (_, _, fr) in C60_SLICES.items()}
    S = pack(0.0, 8, catalogue=cat)
    best = {}
    for n in range(1, 9):
        for ar, nn, tree, W, H in S[n].values():
            pts = parts_of(tree)
            cells = sum(frac[p] for p in pts)
            used = math.ceil(cells - 1e-6)
            if (FACE - W) / 2 < M_MIN or (FACE - H) / 2 < M_MIN:
                continue
            if used not in best or cells > best[used][0]:
                best[used] = (cells, (used - cells) / used, W, H, pts)
    print("\n slices of 125 mm cells:")
    for used, (cells, waste, W, H, pts) in sorted(best.items()):
        print(f"  {used} cell(s) bought: {cells * C60_CM2:5.1f} cm2 = {cells * C60_CM2 / (FACE ** 2 / 100) * 100:4.1f}% of the face, waste {waste * 100:3.0f}%, block {W:.1f} x {H:.1f}, margins {(FACE - W) / 2:.1f} and {(FACE - H) / 2:.1f} mm")
    print("\n wafer cut to a 137 x 137 mm field (margin 1.5 mm):")
    for name, a, diag in (("156.75 (M2)", 156.75, 210.0), ("166 (M6)", 166.0, 223.0)):
        leg = (a * math.sqrt(2) / 2 - diag / 2) * math.sqrt(2)
        area = a * a - 2 * leg * leg
        print(f"  {name}: fill {137 * 137 / FACE ** 2 * 100:.1f}%, {137 * 137 / area * 100:.1f}% of the wafer used, waste {100 - 137 * 137 / area * 100:.0f}%")


# ---------------------------------------------------------------------------------------------------------------------------
# Current, stocked IXOLAR SolarMD parts only (2026-11-12). The earlier 90% layout used SLMD481H10 and SLMD960H09L, which are OBSOLETE (Digi-Key listings).
# name: (w, h, Pmpp mW, Vmp V, mass g, where from). Datasheets read: SM531K08TFS (Rev. Jun 2026, preliminary) and SM940K09L (Rev. May 2025, preliminary):
# 89 x 52 x 1.2 +-0.3 mm, 9.4 g, 913 mW, 4.46 V, 25% typical, film-laminated (EVA and polymer), solder pads on the back, 0.2 mm gaps between its 16 sub-cells, no reflow, no IPA;
# 44.5 x 21.5 x 1.8 +-0.3 mm, 3.3 g, 183.7 mW, 5.02 V. SM811K08TF and SM401K08TF: Digi-Key listings only (mass scaled by area from the SM531).
# ---------------------------------------------------------------------------------------------------------------------------
CURRENT = {
    "SM940K09L 44.5x21.5": (44.5, 21.5, 183.7, 5.02, 3.3),
    "SM531K08TFS 89x52": (89.0, 52.0, 913.0, 4.46, 9.4),
    "SM811K08TF 89x78": (89.0, 78.0, 1405.0, 4.46, 9.4 * 78 / 52),
    "SM401K08TF 90x40": (90.0, 40.0, 702.0, 4.46, 9.4 * 40 / 52),
}

if __name__ == "__main__":
    print("\n\nCURRENT STOCKED PARTS ONLY, no joint; a larger step tolerance leaves a notch of up to that size in the edge line (the block is the parts' bounding box)")
    cat = {k: (v[0], v[1]) for k, v in CURRENT.items()}
    for tol in (0.5, 2.0):
        TOL = tol
        S = pack(0.0, 9, catalogue=cat)
        allb = [(ar / FACE ** 2, nn, W, H, tree, ar) for n in range(1, 10) for ar, nn, tree, W, H in S[n].values() if M_MIN <= (FACE - W) / 2 and M_MIN <= (FACE - H) / 2]
        allb.sort(key=lambda b: (-b[0], b[1]))
        print(f"\n step tolerance {tol} mm:")
        seen = set()
        for f, n, W, H, t, ar in allb:
            if (round(f, 3), n) in seen:
                continue
            seen.add((round(f, 3), n))
            pts = parts_of(t)
            print(f"  {f * 100:4.1f}% ({ar / 100:5.1f} cm2), {n} parts, block {W:.1f} x {H:.1f}, margins {(FACE - W) / 2:.1f} and {(FACE - H) / 2:.1f} mm; "
                  f"{sum(CURRENT[k][2] for k in pts) / 1000:.2f} W at standard conditions, {sum(CURRENT[k][4] for k in pts):.0f} g: " + "; ".join(f"{pts.count(k)} x {k}" for k in sorted(set(pts))))
            if len(seen) >= 3:
                break
