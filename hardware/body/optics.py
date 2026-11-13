"""Optical stack behind the 26 mm window: camera, 45 degree beamsplitter plate and lamp sharing one window (owner's decision, 2026-11-11), first-pass geometry and light budget.

RESULT in one line: the plate's depth along the axis (17.7 mm for a 25 mm plate at 45 degrees) keeps the camera pupil about 19 mm from the window, and the 26 mm window then passes only about
84% of the Pi Camera Module 3's field (35 x 57 degrees of 41 x 66); the full field needs a window of about 31 mm. See the output below.

Run: python3 hardware/body/optics.py   (needs numpy; matplotlib for the picture; writes hardware/body/out/optics_top_view.png and .svg, our own drawing)

SRC = from a cited source (docs/body-redesign.md), ASM = my assumption. Nothing here is a measurement of a real part.

Geometry (top view, x across, y toward the window, z up; u = x - WIN_X is the lateral coordinate from the window axis, which is z = 30 high):
  * the camera looks along +y from an entrance pupil of radius A_PUPIL at y_p (ASM: 3 mm behind the lens front);
  * the plate stands at 45 degrees with its centre on the axis at y_c = y_p + K (its normal is (-1, +1)/sqrt 2, so a lamp on the -x side shining +x is folded onto +y);
  * the lamp sits where the camera pupil is mirrored in the plate (coaxial), i.e. a distance K from the plate centre on the -x side, so the lamp lights the same cone the camera sees;
  * the window is a 26 mm circle at y_W (the pane is 2 mm, recessed in the 2.5 mm wall).
Rays are traced from the pupil over the whole field of view (corners and edge points, and the pupil's rim): a ray is lost if it misses the plate's clear aperture (square, side PLATE_CA)
or the window circle. Reported: the share lost, and the range of angle of incidence on the plate (the polarising plate's rating is 45 +- 15 degrees, Edmund Optics, SRC).
"""
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WIN_D = 26.0
Y_W = 68.5                    # mid-plane of the pane in the wall (wall y = 67.5 to 70; pane 2 mm, recessed 0.5 mm: ASM)
PLATE_CA = 21.0               # clear aperture of the 25 mm square plate (Edmund Optics broadband polarizing plate, 21 x 21 mm clear, 0.7 mm thick, SRC)
PUPIL_BEHIND = 3.0            # entrance pupil behind the lens front surface (ASM)
LED_HALF = 2.0                # half the lamp's width, a bare 3535 LED package with its holder (ASM)
K_MIN = 8                     # the lamp, a distance K from the plate centre, has to stand outside the camera's view cone: K (1 - tan(half-angle)) >= pupil radius + LED_HALF + 1 mm (about 7.5 mm for the standard lens)

CAMERAS = {  # name: (horizontal FOV deg, vertical FOV deg, entrance pupil radius mm, module W x H x thick mm); Raspberry Pi docs/retailers (SRC); pupil = focal length / (2 f-number) (ASM from SRC lens data)
    "Pi Camera Module 3 standard (66 x 41, f 4.74, F1.8)": (66.0, 41.0, 4.74 / 1.8 / 2, (25, 24, 11.5)),
    "Pi Camera Module 3 wide (102 x 67, f 2.75, F2.2)": (102.0, 67.0, 2.75 / 2.2 / 2, (25, 24, 12.4)),
}


def trace(h_half, v_half, a_pupil, y_p, k, plate_ca=PLATE_CA, n=9, win_d=WIN_D):
    """h_half is the field half-angle in the plate's tilt plane (x), v_half perpendicular to it (z). Returns (share lost at the plate, share lost at the window, min AOI, max AOI)."""
    y_c = y_p + k
    lost_p = lost_w = tot = 0
    aoi = []
    th = np.tan(np.radians(np.linspace(-h_half, h_half, n)))
    tv = np.tan(np.radians(np.linspace(-v_half, v_half, n)))
    pu = [(0.0, 0.0)] + [(a_pupil * math.cos(t), a_pupil * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
    for ax in th:
        for az in tv:
            d = np.array([ax, 1.0, az]); d /= np.linalg.norm(d)
            for px, pz in pu:
                tot += 1
                p0 = np.array([px, y_p, pz])
                # plate plane: y - y_c - x = 0
                t = (y_c - p0[1] + p0[0]) / (d[1] - d[0])
                q = p0 + t * d
                s = q[0] * math.sqrt(2)
                aoi.append(math.degrees(math.acos(abs(-d[0] + d[1]) / math.sqrt(2))))
                if abs(s) > plate_ca / 2 or abs(q[2]) > plate_ca / 2:
                    lost_p += 1
                    continue
                tw = (Y_W - p0[1]) / d[1]
                w = p0 + tw * d
                if math.hypot(w[0], w[2]) > win_d / 2:
                    lost_w += 1
    return lost_p / tot, lost_w / tot, min(aoi), max(aoi)


if __name__ == "__main__":
    name = "Pi Camera Module 3 standard (66 x 41, f 4.74, F1.8)"
    hf, vf, ap, (mw, mh, mt) = CAMERAS[name]
    tt, tv = math.tan(math.radians(min(hf, vf) / 2)), math.tan(math.radians(max(hf, vf) / 2))     # tilt plane holds the SHORT axis (sensor turned so its long side is vertical)
    WALL = 67.5          # inner face of the wall (wall y = 67.5 to 70)
    PLATE_L = 25.0       # side of the commercial plate (clear aperture 21 mm)
    half = PLATE_L / (2 * math.sqrt(2))   # half the plate's extent along y (and x) at 45 degrees: 8.84 mm

    def geom(K, plate_l=PLATE_L):
        """Plate centre so that its far end is 0.5 mm clear of the wall; pupil K behind the plate centre."""
        y_c = WALL - 0.5 - plate_l / (2 * math.sqrt(2)) - 0.35
        return y_c - K, y_c

    def maxfov(K, win_d=WIN_D, plate_ca=PLATE_CA, plate_l=PLATE_L):
        y_p, _ = geom(K, plate_l)
        lo, hi = 0.2, 1.0
        for _ in range(14):
            mid = (lo + hi) / 2
            h, v = math.degrees(math.atan(mid * tt)), math.degrees(math.atan(mid * tv))
            lp, lw, a0, a1 = trace(h, v, ap, y_p, K, plate_ca=plate_ca, win_d=win_d)
            if lp + lw <= 0:
                lo = mid
            else:
                hi = mid
        h, v = math.degrees(math.atan(lo * tt)), math.degrees(math.atan(lo * tv))
        lp, lw, a0, a1 = trace(h, v, ap, y_p, K, plate_ca=plate_ca, win_d=win_d)
        return lo, 2 * h, 2 * v, a0, a1

    print("1. Fit: a 25 mm plate at 45 degrees is 17.7 mm deep along the axis, so with its far end clear of the wall (67.5) the pupil is K + 8.8 + 0.85 mm behind the wall's inner face.")
    print("   Largest field (the Pi camera's 16:9 shape, sensor turned so the long side is vertical) that passes the plate (21 mm clear aperture) and a 26 mm window; the lamp needs K >= 8 mm:")
    for K in (8, 9, 10):
        y_p, y_c = geom(K)
        f, H, V, a0, a1 = maxfov(K)
        print(f"   K = {K}: pupil {Y_W - y_p:.1f} mm from the window plane, lens front at y = {y_p + PUPIL_BEHIND:.1f}: field {H:.0f} x {V:.0f} deg = {f * 100:.0f}% of the lens's {min(hf, vf):.0f} x {max(hf, vf):.0f}; plate AOI {a0:.0f} to {a1:.0f} deg (rated 30 to 60)")
    print("   For comparison: the full field with the pupil at most 15 mm from the window (no plate in the way) would pass, but then the plate's far end would be inside the wall.")

    print("\n2. Window diameter that passes the lens's full field (66 x 41) with the 25 mm plate (K = 8):")
    y_p, y_c = geom(8)
    for wd in range(26, 46):
        lp, lw, a0, a1 = trace(min(hf, vf) / 2, max(hf, vf) / 2, ap, y_p, 8, win_d=float(wd))
        if lp + lw <= 0:
            print(f"   {wd} mm (the plate itself clips {lp * 100:.0f}%); plate AOI {a0:.0f} to {a1:.0f} deg"); break
    else:
        print("   none up to 45 mm")

    print("\n3. Smaller custom plate (2 mm border), 26 mm window, full field: the clear aperture then clips the field or the pupil sits too far; smallest side that passes for K = 8:")
    ok = None
    for L in range(10, 26):
        yp2, yc2 = geom(8, L)
        lp, lw, a0, a1 = trace(min(hf, vf) / 2, max(hf, vf) / 2, ap, yp2, 8, plate_ca=L - 2.0)
        if lp + lw <= 0:
            ok = L; break
    print("   " + (f"side {ok} mm" if ok else "none up to 25 mm: the window, not the plate, clips the field once the pupil is more than about 15 mm away"))

    print("\n4. Light budget (unpolarised lamp and scene; a: 50/50 plate as placed so far, b: 50/50 plate with crossed polarisers, c: polarising plate or cube).")
    pane = 1 - (1 - 0.04) ** 2
    print("   Fractions of the lamp's light that leave the window, of the scene's ambient light that reaches the camera, and of the lamp light reflected by the pane that reaches the camera (4% per surface, ASM):")
    for lab, lamp, amb, glare in (("a  50/50 plate", 0.5, 0.5, pane * 0.5 * 0.5),
                                  ("b  50/50 plate + lamp polariser + crossed analyser at the camera", 0.25, 0.25, 0.0),
                                  ("c  polarising beamsplitter (S reflected, P passed), no extra polarisers", 0.5, 0.5, 0.0)):
        print(f"   {lab:70s} lamp out {lamp * 100:3.0f}%, ambient to camera {amb * 100:3.0f}%, window glare to camera {glare * 100:4.2f}% of the lamp light (before extinction ratio)")
    print("   c: the S light the pane reflects goes back to the plate as S and is sent toward the lamp, not the camera (extinction 1000:1 to 3000:1 for the Edmund wire-grid cube, SRC); diffuse scenes are depolarised, glossy ones are not.")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        K = 8
        y_p, y_c = geom(K)
        f, H, V, a0, a1 = maxfov(K)
        fig, ax = plt.subplots(1, 1, figsize=(8.2, 7.6), facecolor="white")
        ax.add_patch(Rectangle((-34, 67.5), 68, 2.5, fc="#2b2b2e", ec="#888"))
        ax.add_patch(Rectangle((-13, 67.5), 26, 2.5, fc="white", ec="#888", hatch="///"))
        ax.add_patch(Rectangle((-13, 67.7), 26, 2.0, fc="#9fd3ff", ec="#2a6fb0", alpha=0.85))
        ax.text(0, 71.0, "window 26 mm (wall 2.5 mm, pane 2 mm)", ha="center", fontsize=7)
        c = PLATE_L / (2 * math.sqrt(2))
        ax.plot([-c, c], [y_c - c, y_c + c], color="#c0392b", lw=3)
        ax.text(c + 1.5, y_c + 3.5, "polarising plate 25 x 25 x 0.7\nat 45 deg (21 mm clear)", fontsize=7, color="#c0392b")
        lens_front = y_p + PUPIL_BEHIND
        ax.add_patch(Rectangle((-mw / 2, lens_front - mt), mw, mt - 5.5, fc="#2c7a4b", ec="k", alpha=0.9))
        ax.add_patch(Rectangle((-6, lens_front - 5.5), 12, 5.5, fc="#444", ec="k"))
        ax.text(0, lens_front - mt / 2 - 2, f"camera module {mw} x {mh} x {mt}\n(sensor turned: long side vertical)", ha="center", fontsize=7, color="white")
        h = math.radians(H / 2)
        for sgn in (-1, 1):
            ax.plot([0, sgn * (Y_W - y_p) * math.tan(h)], [y_p, Y_W], color="#e67e22", lw=1.0)
        ax.plot([0], [y_p], "ko", ms=3)
        ax.text(1.5, y_p - 1.2, "pupil", fontsize=6)
        lx = -K
        ax.add_patch(Rectangle((lx - 2.5, y_c - 2), 5, 4, fc="#f1c40f", ec="k"))
        ax.annotate("", xy=(-c * 0.4, y_c), xytext=(lx + 2.5, y_c), arrowprops=dict(arrowstyle="->", color="#f39c12", lw=1.5))
        ax.text(lx - 2, y_c + 4, f"lamp (bare LED) {K} mm from the plate centre,\nat the pupil's mirror image (coaxial)", ha="center", fontsize=7)
        ax.annotate("", xy=(31, y_p), xytext=(31, Y_W), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text(32, (y_p + Y_W) / 2, f"{Y_W - y_p:.1f} mm\npupil to window", fontsize=7, va="center")
        ax.set_xlim(-34, 42); ax.set_ylim(y_p - 17, 74); ax.set_aspect("equal")
        ax.set_xlabel("lateral u from the window axis (mm); the -x side (body centre) on the left"); ax.set_ylabel("y (mm); window wall at the top")
        ax.set_title(f"Optical stack, top view: usable field {H:.0f} x {V:.0f} deg of the lens's {min(hf, vf):.0f} x {max(hf, vf):.0f} (orange: field in the tilt plane)", fontsize=8.5)
        fig.tight_layout()
        fig.savefig(HERE / "out" / "optics_top_view.png", dpi=150)
        fig.savefig(HERE / "out" / "optics_top_view.svg")
        print("\nwrote", HERE / "out" / "optics_top_view.png")
    except Exception as e:
        print("picture skipped:", e)


# ---------------------------------------------------------------------------------------------------------------------------
# Analog route (owner, 2026-11-12): a composite-video board camera with an M12 lens and an analog video transmitter. Sensor 1/3 inch (4.8 x 3.6 mm, 4:3: the standard
# optical-format figure, ASM for these cameras), lens F2.0 (ASM). The plate and window geometry are those of section 1 (25 mm plate, K = 8, 26 mm window).
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    WALL_ = 67.5
    y_c_ = WALL_ - 0.5 - 25.0 / (2 * math.sqrt(2)) - 0.35
    y_p_ = y_c_ - 8
    print("\n5. Analog board camera (1/3 inch, 4.8 x 3.6 mm) with an M12 lens, same geometry (pupil %.1f mm from the window):" % (Y_W - y_p_))
    for f in (2.1, 3.6, 4.0, 6.0, 8.0):
        Hh = 2 * math.degrees(math.atan(4.8 / 2 / f)); Vv = 2 * math.degrees(math.atan(3.6 / 2 / f))
        lp, lw, a0, a1 = trace(Vv / 2, Hh / 2, f / 4, y_p_, 8)
        print(f"   f = {f:3.1f} mm: field {Hh:5.1f} x {Vv:5.1f} deg; lost: plate {lp * 100:3.0f}%, window {lw * 100:3.0f}%; plate AOI {a0:.0f} to {a1:.0f} deg")
    print("   A 6 mm lens (43.6 x 33.4 degrees) passes with no loss; 4 mm loses about 10%; the 2.1 to 2.3 mm lenses of FPV cameras (145 to 165 degrees) are far too wide.")
