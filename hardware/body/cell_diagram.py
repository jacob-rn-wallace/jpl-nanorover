"""Diagram of the IXOLAR cell option: the two best 88 to 90% layouts of current, stocked Anysolar SolarMD parts on a 140 x 140 mm top or bottom face.

Run: python3 hardware/body/cell_diagram.py   (needs matplotlib; writes hardware/body/out/cell_diagram_ixolar.png and .svg, our own drawing, safe to track)

The positions come from cell_catalogue.py (the packing search), so the sizes are the ones that were counted. The face is seen from outside; the lids are identical and the orientation is arbitrary.
Only the SM531K08TFS shows its internal cell grid (4 x 4 from its datasheet drawing); the others are drawn plain because their drawings were not read. The carbon texture is only a hint of forged carbon.
"""
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cell_catalogue as C

FACE = C.FACE
C.TOL = 2.0
CAT = {k: (v[0], v[1]) for k, v in C.CURRENT.items()}
COL = {"SM940K09L 44.5x21.5": "#1c3a73", "SM531K08TFS 89x52": "#173060", "SM811K08TF 89x78": "#1f3f80", "SM401K08TF 90x40": "#122a58"}
SHORT = {"SM940K09L 44.5x21.5": "SM940K09L", "SM531K08TFS 89x52": "SM531K08TFS", "SM811K08TF 89x78": "SM811K08TF", "SM401K08TF 90x40": "SM401K08TF"}


def find(counts):
    """Best layout (largest area) of exactly these part counts, from the packing search."""
    S = C.pack(0.0, 9, catalogue=CAT)
    best = None
    for n in range(1, 10):
        for ar, nn, tree, W, H in S[n].values():
            pts = C.parts_of(tree)
            if {k: pts.count(k) for k in set(pts)} == counts and (FACE - W) / 2 >= C.M_MIN and (FACE - H) / 2 >= C.M_MIN:
                if best is None or ar > best[0]:
                    best = (ar, tree, W, H)
    return best


def carbon(ax, seed=3):
    """A hint of forged carbon: many small dark flakes of slightly different grey."""
    rnd = random.Random(seed)
    bg = Rectangle((0, 0), FACE, FACE, color="#2b2b2e", zorder=0)
    ax.add_patch(bg)
    for _ in range(900):
        cx, cy = rnd.uniform(0, FACE), rnd.uniform(0, FACE)
        a, b = rnd.uniform(1.5, 7), rnd.uniform(0.8, 3.2)
        th = rnd.uniform(0, 3.1416)
        import math
        pts = [(cx + dx * math.cos(th) - dy * math.sin(th), cy + dx * math.sin(th) + dy * math.cos(th)) for dx, dy in ((-a, -b), (a, -b), (a, b), (-a, b))]
        g = rnd.randint(30, 66)
        fl = Polygon(pts, closed=True, color=f"#{g:02x}{g:02x}{g + 3:02x}", lw=0, zorder=0.5)
        ax.add_patch(fl)
        fl.set_clip_path(bg)                                   # keep the flakes inside the face


def panel(ax, title, counts):
    ar, tree, W, H = find(counts)
    items = []
    bw, bh = C.draw(tree, 0, 0, 0.0, items)
    mx, my = (FACE - bw) / 2, (FACE - bh) / 2
    carbon(ax)
    for x, y, w, h, name in items:
        ax.add_patch(Rectangle((mx + x, my + y), w, h, facecolor=COL[name], edgecolor="#6f86b8", lw=0.6, zorder=2))
        if name.startswith("SM531"):                       # 4 x 4 sub-cells with 0.2 mm gaps (datasheet drawing, long side horizontal)
            lw, lh = (w, h) if w > h else (h, w)
            for i in range(1, 4):
                if w > h:
                    ax.plot([mx + x + i * w / 4] * 2, [my + y, my + y + h], color="#6f86b8", lw=0.25, zorder=3)
                    ax.plot([mx + x, mx + x + w], [my + y + i * h / 4] * 2, color="#6f86b8", lw=0.25, zorder=3)
                else:
                    ax.plot([mx + x + i * w / 4] * 2, [my + y, my + y + h], color="#6f86b8", lw=0.25, zorder=3)
                    ax.plot([mx + x, mx + x + w], [my + y + i * h / 4] * 2, color="#6f86b8", lw=0.25, zorder=3)
        ax.text(mx + x + w / 2, my + y + h / 2, f"{SHORT[name]}\n{w:g} x {h:g}", ha="center", va="center", fontsize=5.2, color="#e8eefc", zorder=4)
    ax.add_patch(Rectangle((0, 0), FACE, FACE, fill=False, edgecolor="#bbbbbb", lw=1.2, zorder=5))
    # margins and block size
    ax.annotate("", xy=(0, FACE + 3.5), xytext=(mx, FACE + 3.5), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#444"))
    ax.text(mx / 2, FACE + 5.2, f"{mx:.1f}", ha="center", fontsize=6, color="#222")
    ax.annotate("", xy=(FACE - mx, FACE + 3.5), xytext=(FACE, FACE + 3.5), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#444"))
    ax.text(FACE - mx / 2, FACE + 5.2, f"{mx:.1f}", ha="center", fontsize=6, color="#222")
    ax.annotate("", xy=(-3.5, 0), xytext=(-3.5, my), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#444"))
    ax.text(-5, my / 2, f"{my:.1f}", ha="right", va="center", fontsize=6, color="#222")
    ax.annotate("", xy=(-3.5, FACE - my), xytext=(-3.5, FACE), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#444"))
    ax.text(-5, FACE - my / 2, f"{my:.1f}", ha="right", va="center", fontsize=6, color="#222")
    pts = C.parts_of(tree)
    pw = sum(C.CURRENT[k][2] for k in pts) / 1000
    ms = sum(C.CURRENT[k][4] for k in pts)
    area = sum(C.CURRENT[k][0] * C.CURRENT[k][1] for k in pts) / 100
    ax.set_title(title, fontsize=9, loc="left", pad=16)
    ax.text(0, -9, f"{len(pts)} parts: " + ", ".join(f"{pts.count(k)} x {SHORT[k]}" for k in sorted(set(pts), key=lambda k: -C.CURRENT[k][0] * C.CURRENT[k][1])) +
            f"\n{area:.1f} cm2 = {area * 100 / FACE ** 2 * 100:.1f}% of the face; {pw:.2f} W at standard conditions (1 sun, 25 C); about {ms:.0f} g; block {bw:.1f} x {bh:.1f} mm",
            fontsize=6.3, va="top", color="#222")
    ax.set_xlim(-12, FACE + 6)
    ax.set_ylim(-24, FACE + 9)
    ax.set_aspect("equal")
    ax.axis("off")


if __name__ == "__main__":
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.6), facecolor="white")
    panel(axs[0], "Layout 1: 89.6% of the face", {"SM401K08TF 90x40": 2, "SM531K08TFS 89x52": 1, "SM940K09L 44.5x21.5": 6})
    panel(axs[1], "Layout 2: 88.3% of the face", {"SM531K08TFS 89x52": 1, "SM811K08TF 89x78": 1, "SM940K09L 44.5x21.5": 6})
    fig.suptitle("IXOLAR option: top or bottom face, 140 x 140 mm, seen from outside, parts butted together (dimensions in mm)", fontsize=10, y=0.985)
    fig.text(0.5, 0.012, "Parts with unequal sides leave a small notch (up to 2 mm) in the carbon edge line. Margins are the carbon border. Only the SM531K08TFS shows its 4 x 4 sub-cell grid (its datasheet drawing); "
             "package outlines, not measured parts. Carbon texture is illustrative.", ha="center", fontsize=6.3, color="#444")
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "cell_diagram_ixolar.png", dpi=160, bbox_inches="tight")
    fig.savefig(out / "cell_diagram_ixolar.svg", bbox_inches="tight")
    print("wrote", out / "cell_diagram_ixolar.png", "and .svg")
