"""End-face cell options: the 140 x 60 mm end face with the window (or antenna) panel as a 60 x 60 mm square right up to the edge, and one pocket of cells in the remaining 80 x 60 mm.

Run: python3 hardware/body/cell_endface.py   (needs matplotlib; writes hardware/body/out/cell_endface.png and .svg, our own drawing, safe to track)

Owner's request (2026-11-12): start with the end faces; treat the window or antenna panel as a 60 x 60 mm square up to the edge; the body is treated as a single solid at this stage.
Orientation: seen from outside the +y face (the viewer's view, as in docs/body-redesign.md) the window at x = +40 is on the viewer's LEFT; a 180 degree turn about z puts the antenna
square on the -y face on the viewer's left too, so the two end faces look the same from outside: panel on the left, cells on the right.

Parts (current, active Anysolar IXOLAR parts; sizes from Digi-Key listings, the SM940K09L also from its datasheet; the +-0.3 mm tolerance is assumed for the SM351K09L):
  E1: one SM351K09L 57 x 64 mm turned to 64 x 57 (695 mW, 5.02 V, 375 in stock); E2: three SM940K09L 44.5 x 21.5 mm standing, side by side (the part used on the top face).
"""
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

W, H = 140.0, 60.0
TOL = 0.3


def carbon_rect(ax, seed=5):
    import math
    rnd = random.Random(seed)
    bg = Rectangle((0, 0), W, H, color="#2b2b2e", zorder=0)
    ax.add_patch(bg)
    for _ in range(420):
        cx, cy = rnd.uniform(0, W), rnd.uniform(0, H)
        a, b = rnd.uniform(1.5, 7), rnd.uniform(0.8, 3.2)
        th = rnd.uniform(0, 3.1416)
        pts = [(cx + dx * math.cos(th) - dy * math.sin(th), cy + dx * math.sin(th) + dy * math.cos(th)) for dx, dy in ((-a, -b), (a, -b), (a, b), (-a, b))]
        g = rnd.randint(30, 66)
        fl = Polygon(pts, closed=True, color=f"#{g:02x}{g:02x}{g + 3:02x}", lw=0, zorder=0.5)
        ax.add_patch(fl)
        fl.set_clip_path(bg)


def face(ax, title, parts, pocket_w, pocket_h, info, pw=60.0):
    carbon_rect(ax)
    # window / antenna panel: a 60 x 60 mm square at the viewer's left, to the edge
    ax.add_patch(Rectangle((0, 0), pw, 60, facecolor="#141416", edgecolor="#7d8798", lw=0.8, zorder=1))
    ax.add_patch(Circle((pw / 2, 30), 13, facecolor="#050506", edgecolor="#7d8798", lw=0.6, zorder=2))
    ax.text(pw / 2, 8, f"window (26 mm) or antenna pivot\n{pw:g} x 60 mm panel, to the edge", ha="center", va="center", fontsize=5.2, color="#c8cfdb", zorder=3)
    # pocket centred in the 80 x 60 zone to the right of the panel
    px = pw + ((W - pw) - pocket_w) / 2
    py = (60 - pocket_h) / 2
    ax.add_patch(Rectangle((px, py), pocket_w, pocket_h, facecolor="#101214", edgecolor="#8a9bb5", lw=0.7, ls="--", zorder=1))
    for (dx, dy, w, h, label, col) in parts:
        ax.add_patch(Rectangle((px + dx, py + dy), w, h, facecolor=col, edgecolor="#6f86b8", lw=0.5, zorder=2))
        ax.text(px + dx + w / 2, py + dy + h / 2, label, ha="center", va="center", fontsize=5.2, color="#e8eefc", zorder=4)
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, edgecolor="#bbbbbb", lw=1.2, zorder=5))
    # rims
    ax.annotate("", xy=(pw, 62.5), xytext=(px, 62.5), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#444"))
    ax.text((pw + px) / 2, 64, f"{px - pw:.2f}", ha="center", fontsize=5.5)
    ax.annotate("", xy=(px + pocket_w, 62.5), xytext=(W, 62.5), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#444"))
    ax.text((px + pocket_w + W) / 2, 64, f"{W - px - pocket_w:.2f}", ha="center", fontsize=5.5)
    ax.annotate("", xy=(W + 2.5, 0), xytext=(W + 2.5, py), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#444"))
    ax.text(W + 4, py / 2, f"{py:.2f}", ha="left", va="center", fontsize=5.5)
    ax.set_title(title, fontsize=8, loc="left", pad=12)
    ax.text(0, -3, info, fontsize=6, va="top", color="#222")
    ax.set_xlim(-2, W + 12); ax.set_ylim(-17, H + 8); ax.set_aspect("equal"); ax.axis("off")


if __name__ == "__main__":
    fig, axs = plt.subplots(3, 1, figsize=(8.4, 12.0), facecolor="white")
    # E1: one SM351K09L 57 x 64 turned to 64 x 57; pocket for the worst case (+0.3 mm per side, assumed)
    pw1, ph1 = 64 + TOL, 57 + TOL
    area1 = 64 * 57 / 100
    face(axs[0], "Option E1: one SM351K09L (57 x 64 mm, turned)",
         [((pw1 - 64) / 2, (ph1 - 57) / 2, 64.0, 57.0, "SM351K09L\n64 x 57", "#1f3f80")], pw1, ph1,
         f"{area1:.1f} cm2 = {area1 * 100 / (W * H) * 100:.0f}% of the end face; 0.695 W at standard conditions; 5.02 V; about 13 g (mass scaled, not read); pocket {pw1:.1f} x {ph1:.1f} mm (worst case). "
         f"Rim {(H - ph1) / 2:.2f} mm top and bottom\nis thin (the vendor guidance for forged carbon is about 1.5 mm); the cells are a single part, so no joints or slack. 375 in stock on Digi-Key listings.")
    # E2: three SM940K09L standing side by side
    pw2, ph2 = 3 * 21.5 + 3 * TOL, 44.5 + TOL
    area2 = 3 * 44.5 * 21.5 / 100
    face(axs[1], "Option E2: three SM940K09L (44.5 x 21.5 mm, standing), the part used on the top face",
         [(((pw2 - 64.5) / 2) + 21.5 * k, (ph2 - 44.5) / 2, 21.5, 44.5, "SM940K09L\n21.5 x 44.5", "#1c3a73") for k in range(3)], pw2, ph2,
         f"{area2:.1f} cm2 = {area2 * 100 / (W * H) * 100:.0f}% of the end face; 0.55 W at standard conditions; 5.02 V; 9.9 g (datasheet); pocket {pw2:.1f} x {ph2:.1f} mm (worst case). "
         f"Rim {(H - ph2) / 2:.2f} mm top and bottom,\nabout equal to the side rims; more carbon showing, less cell area. Same part as six on each of the top and bottom faces.")
    # E3: the panel relaxed from a 60 mm square to a rectangle (width pw3, full height) with the hole still centred; four SM940K09L standing
    pw3 = 46.5
    pw3p, ph3 = 4 * 21.5 + 4 * TOL, 44.5 + TOL
    area3 = 4 * 44.5 * 21.5 / 100
    face(axs[2], f"Option E3: panel relaxed to a {pw3:g} x 60 mm rectangle (hole centred, so the window moves to x = +{70 - pw3 / 2:.2f}), four SM940K09L standing",
         [(((pw3p - 86.0) / 2) + 21.5 * k, (ph3 - 44.5) / 2, 21.5, 44.5, "SM940K09L\n21.5 x 44.5", "#1c3a73") for k in range(4)], pw3p, ph3,
         f"{area3:.1f} cm2 = {area3 * 100 / (W * H) * 100:.0f}% of the end face ({area3 / (3 * 44.5 * 21.5 / 100) * 100 - 100:+.0f}% on E2); 0.73 W at standard conditions; 5.02 V; 13.2 g (datasheet); pocket {pw3p:.1f} x {ph3:.1f} mm (worst case).\n"
         f"Window and antenna pivot move from x = +-40 to +-{70 - pw3 / 2:.2f}; the antenna swing disc (40 mm) then reaches the hub wall (0.6 cm3 outside the keep-in volume at 47.5, no contact with servos).", pw=pw3)
    fig.suptitle("End faces, seen from outside (the same on the +y and -y faces): 140 x 60 mm, panel at the viewer's left, one pocket of cells at the right (mm)", fontsize=9, y=0.995)
    out = HERE / "out"
    fig.savefig(out / "cell_endface.png", dpi=160, bbox_inches="tight")
    fig.savefig(out / "cell_endface.svg", bbox_inches="tight")
    print("wrote", out / "cell_endface.png")
    print(f"E1: {area1:.1f} cm2, pocket {pw1:.1f} x {ph1:.1f}, rims {(80 - pw1) / 2:.2f} (sides, to the panel and to the edge), {(H - ph1) / 2:.2f} (top, bottom)")
    print(f"E2: {area2:.1f} cm2, pocket {pw2:.1f} x {ph2:.1f}, rims {(80 - pw2) / 2:.2f} (sides), {(H - ph2) / 2:.2f} (top, bottom)")


# ---------------------------------------------------------------------------------------------------------------------------
# Option E3 as adopted (owner, 2026-11-12): the panel is dropped and the horizontal space is divided evenly into three gaps:
# face edge to hole, hole to cell pocket, pocket to face edge. Hole 26 mm (the window; the antenna face gets the same circle, see docs), pocket 87.2 mm (worst case, four SM940K09L).
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    HOLE = 26.0
    PW4, PH4 = 4 * 21.5 + 4 * TOL, 44.5 + TOL
    gap = (W - HOLE - PW4) / 3
    cx = gap + HOLE / 2
    px = 2 * gap + HOLE
    fig, ax = plt.subplots(1, 1, figsize=(9.4, 4.9), facecolor="white")
    carbon_rect(ax)
    ax.add_patch(Circle((cx, 30), HOLE / 2, facecolor="#050506", edgecolor="#7d8798", lw=0.8, zorder=2))
    ax.add_patch(Rectangle((px, (H - PH4) / 2), PW4, PH4, facecolor="#101214", edgecolor="#8a9bb5", lw=0.7, ls="--", zorder=1))
    for k in range(4):
        x0 = px + (PW4 - 86.0) / 2 + 21.5 * k
        ax.add_patch(Rectangle((x0, (H - 44.5) / 2), 21.5, 44.5, facecolor="#1c3a73", edgecolor="#6f86b8", lw=0.5, zorder=2))
        ax.text(x0 + 10.75, 30, "SM940K09L\n21.5 x 44.5", ha="center", va="center", fontsize=5.4, color="#e8eefc", zorder=4)
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, edgecolor="#bbbbbb", lw=1.2, zorder=5))
    for x0, x1 in ((0, gap), (gap + HOLE, px), (px + PW4, W)):
        ax.annotate("", xy=(x0, 63), xytext=(x1, 63), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#333"))
        ax.text((x0 + x1) / 2, 65, f"{x1 - x0:.2f}", ha="center", fontsize=7, color="#111")
    ax.annotate("", xy=(gap, -3.5), xytext=(gap + HOLE, -3.5), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#555"))
    ax.text(cx, -6.5, "hole 26 (window or antenna)", ha="center", fontsize=6, color="#333")
    ax.annotate("", xy=(px, -3.5), xytext=(px + PW4, -3.5), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#555"))
    ax.text(px + PW4 / 2, -6.5, f"pocket {PW4:.1f} x {PH4:.1f} (worst case)", ha="center", fontsize=6, color="#333")
    ax.annotate("", xy=(W + 2.5, 0), xytext=(W + 2.5, (H - PH4) / 2), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#555"))
    ax.text(W + 4, (H - PH4) / 4, f"{(H - PH4) / 2:.2f}", ha="left", va="center", fontsize=6)
    ax.text(0, -11, f"Seen from outside, 140 x 60 mm. The three horizontal gaps are equal: ({W:g} - {HOLE:g} - {PW4:.1f}) / 3 = {gap:.3f} mm each. Hole centre {cx:.2f} mm from the viewer's left edge,\n"
            f"i.e. x = {70 - cx:+.2f} mm on the +y face (window) and x = {-70 + cx:+.2f} mm on the -y face (antenna); z = 30. Four SM940K09L: 38.3 cm2 = 46% of the end face, 0.73 W at standard conditions, 5.02 V.\n"
            f"Vertical rims: {(H - PH4) / 2:.2f} mm above and below the pocket, {(H - HOLE) / 2:.1f} mm above and below the hole.", fontsize=6.2, va="top", color="#222")
    ax.set_title("End face, option E3 adopted: panel dropped, horizontal space divided evenly into three gaps", fontsize=9, loc="left", pad=16)
    ax.set_xlim(-2, W + 12); ax.set_ylim(-24, H + 9); ax.set_aspect("equal"); ax.axis("off")
    out = HERE / "out"
    fig.savefig(out / "cell_endface_final.png", dpi=160, bbox_inches="tight")
    fig.savefig(out / "cell_endface_final.svg", bbox_inches="tight")
    print(f"\nE3 adopted: gaps {gap:.3f} mm each, hole centre {cx:.2f} mm from the viewer's left edge (x = {70 - cx:+.2f} / {-70 + cx:+.2f}), pocket {px:.2f} to {px + PW4:.2f}; wrote cell_endface_final.png")
