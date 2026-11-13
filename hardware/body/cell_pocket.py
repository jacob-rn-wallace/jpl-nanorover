"""One pocket for all the cells on a face: the symmetric Layout 1 with every part butted together and the middle part centred.

Run: python3 hardware/body/cell_pocket.py   (needs matplotlib; writes hardware/body/out/cell_pocket.png and .svg, our own drawing, safe to track)

Owner's request (2026-11-12): move all cells in so there is as little gap between them as possible, keeping the middle cell centred and the layout symmetric, so that only one
pocket has to be made for all the cells on a side.

Parts (nominal, from the datasheets and Digi-Key listings, see cell_catalogue.py): 6 x SM940K09L 44.5 x 21.5, 2 x SM401K08TF 90 x 40 (standing), 1 x SM531K08TFS 89 x 52 (standing).
Rows: three 44.5 mm parts across the top and the bottom (133.5 mm), and in the middle 40 | 52 | 40 mm (132 mm). The middle row is 1.5 mm narrower than the pocket, so the middle
part is centred with 0.75 mm of slack on each side; it is also 1 mm shorter than the 90 mm parts, so 0.5 mm above and below. Everything else touches.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cell_diagram as D

FACE = 140.0
S9, S5, S4 = "SM940K09L 44.5x21.5", "SM531K08TFS 89x52", "SM401K08TF 90x40"
PW, PH = 3 * 44.5, 21.5 + 90.0 + 21.5          # pocket, nominal: 133.5 x 133.0
TOL = 0.3                                       # mm per side (datasheets of the SM531K08TFS and SM940K09L: +-0.3; the SM401 was not read, assumed the same)


def layout():
    mx, my = (FACE - PW) / 2, (FACE - PH) / 2
    parts = []
    for y in (my, my + 21.5 + 90.0):
        for k in range(3):
            parts.append((mx + 44.5 * k, y, 44.5, 21.5, S9))
    parts.append((mx, my + 21.5, 40.0, 90.0, S4))
    parts.append((mx + PW - 40.0, my + 21.5, 40.0, 90.0, S4))
    parts.append((FACE / 2 - 26.0, my + 21.5 + 0.5, 52.0, 89.0, S5))
    return parts, mx, my


if __name__ == "__main__":
    parts, mx, my = layout()
    area = sum(p[2] * p[3] for p in parts) / 100
    pocket = PW * PH / 100
    print(f"pocket {PW:.1f} x {PH:.1f} mm = {pocket:.1f} cm2, carbon rim {mx:.2f} mm left and right, {my:.2f} mm top and bottom")
    print(f"cells {area:.1f} cm2 = {area * 100 / FACE ** 2 * 100:.1f}% of the face, {area / pocket * 100:.1f}% of the pocket; {3.42:.2f} W at standard conditions (sum of datasheet and listing ratings)")
    # symmetry check
    def has(x, y, w, name):
        return any(abs(q[0] - x) < 1e-6 and abs(q[1] - y) < 1e-6 and q[4] == name and abs(q[2] - w) < 1e-6 for q in parts)
    print("mirror symmetric left-right:", all(has(FACE - p[0] - p[2], p[1], p[2], p[4]) for p in parts),
          "; top-bottom:", all(has(p[0], FACE - p[1] - p[3], p[2], p[4]) for p in parts))
    print("slack inside the pocket: 0.75 mm each side of the SM531 (inside the middle row), 0.5 mm above and below it; every other joint is 0")
    # tolerance: parts are +-TOL per side, so a row or column of three parts can be 3 * TOL over nominal
    wc_w, wc_h = PW + 3 * TOL, PH + 3 * TOL
    print(f"worst case: three parts in a row or column can each be {TOL} mm over, so the pocket would need {wc_w:.1f} x {wc_h:.1f} mm to take any set of parts "
          f"(rim {(FACE - wc_w) / 2:.2f} and {(FACE - wc_h) / 2:.2f} mm); the nominal pocket leaves no clearance at all")
    fig, ax = plt.subplots(1, 1, figsize=(7.4, 7.6), facecolor="white")
    D.carbon(ax)
    ax.add_patch(Rectangle((mx, my), PW, PH, facecolor="#101214", edgecolor="#8a9bb5", lw=0.8, ls="--", zorder=1))   # the pocket floor, seen in the slack
    for x, y, w, h, name in parts:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=D.COL[name], edgecolor="#6f86b8", lw=0.5, zorder=2))
        if name.startswith("SM531"):
            for i in range(1, 4):
                ax.plot([x + i * w / 4] * 2, [y, y + h], color="#6f86b8", lw=0.25, zorder=3)
                ax.plot([x, x + w], [y + i * h / 4] * 2, color="#6f86b8", lw=0.25, zorder=3)
        ax.text(x + w / 2, y + h / 2, f"{D.SHORT[name]}\n{w:g} x {h:g}", ha="center", va="center", fontsize=5.2, color="#e8eefc", zorder=4)
    ax.add_patch(Rectangle((0, 0), FACE, FACE, fill=False, edgecolor="#bbbbbb", lw=1.2, zorder=5))
    ax.annotate("", xy=(0, FACE + 3), xytext=(mx, FACE + 3), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#444"))
    ax.text(mx / 2, FACE + 4.6, f"{mx:.2f}", ha="center", fontsize=6)
    ax.annotate("", xy=(-3, 0), xytext=(-3, my), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#444"))
    ax.text(-4.5, my / 2, f"{my:.2f}", ha="right", va="center", fontsize=6)
    ax.text(0, -4, f"One pocket {PW:.1f} x {PH:.1f} mm (nominal), carbon rim {mx:.2f} mm at the sides and {my:.2f} mm top and bottom. Cells {area:.1f} cm2 = {area * 100 / FACE ** 2 * 100:.1f}% of the face.\n"
            f"Every joint is butted; the middle part is centred with 0.75 mm of slack at each side and 0.5 mm above and below. Mirror symmetric both ways.\n"
            f"Worst-case tolerance (+-{TOL} mm per part, three in a row) needs a {wc_w:.1f} x {wc_h:.1f} mm pocket.", fontsize=6.2, va="top", color="#222")
    ax.set_title("Layout 1 in a single pocket: parts butted, middle part centred (140 x 140 mm face, seen from outside)", fontsize=8.5, loc="left", pad=14)
    ax.set_xlim(-10, FACE + 4); ax.set_ylim(-18, FACE + 8); ax.set_aspect("equal"); ax.axis("off")
    out = HERE / "out"
    fig.savefig(out / "cell_pocket.png", dpi=160, bbox_inches="tight")
    fig.savefig(out / "cell_pocket.svg", bbox_inches="tight")
    print("wrote", out / "cell_pocket.png")
