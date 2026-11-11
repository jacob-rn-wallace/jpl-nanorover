"""Interior layout of the body, independent of the shell material (woven plates, layup or forged carbon).

Run: .venv/bin/python hardware/body/layout.py    (needs the venv for numpy, matplotlib and hub.py's build123d import; no CAD is exported)

What it does
  1. Defines the KEEP-IN volume: the 140 x 140 x 60 mm envelope pulled in 2.5 mm from every outer face (a 1.5 mm forged wall plus 1 mm of draft and
     tolerance; a 1.0 mm plate wall fits inside it with room to spare), minus a 6 mm strip along every edge (room for the plate box's bonded keys).
  2. Marks what the hub already occupies (the four STS3215 servos and the hub parts of hub.py, with 1 mm clearance) and reports the free bays.
  3. Places the remaining components as boxes (PLACEHOLDER sizes and masses, marked ASM: no parts are chosen) and checks that each lies in the
     keep-in volume, clear of the servos and hub, and clear of the others.
  4. Computes the centre of mass of the body contents and what it does to the chassis simulation's whole-rover centre of mass
     (docs/chassis-simulation.md: 2.9 mm toward -y of the hub axis at the 25 degree stance, with the body lump 386 g at the centre).

Coordinates (mm): x across between the two hub faces (+-70), y along the body (the end with the round window is +y), z up from the floor (0 to 60);
the hub axis is along x at y = 0, z = 30. Seen from outside, standing at +y and looking at the end face, +x is on the LEFT (viewer's left).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "hub"))
sys.path.insert(0, str(HERE.parent / "drivetrain"))
import hub as H  # noqa: E402

L = 140.0
HZ = 30.0
OFF = 2.5                 # keep-in inset from every outer face
STRIP = 6.0               # edge strip kept clear for bonded keys
CLR = 1.0                 # clearance round servos and hub parts
RES = 1.0                 # voxel size, mm

# ---------------- voxel grid over the envelope ----------------
xs = np.arange(-70 + RES / 2, 70, RES)
ys = np.arange(-70 + RES / 2, 70, RES)
zs = np.arange(0 + RES / 2, 60, RES)
X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")


def box_mask(x0, x1, y0, y1, z0, z1):
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= z0) & (Z <= z1)


def cylx_mask(y, z, r, xa, xb):
    """Cylinder along x from xa to xb (signed) centred at (y, z)."""
    lo, hi = min(xa, xb), max(xa, xb)
    return (X >= lo) & (X <= hi) & ((Y - y) ** 2 + (Z - z) ** 2 <= r * r)


# keep-in: inside the inset box, not within STRIP of two or more outer faces
d_faces = np.stack([70 - np.abs(X), 70 - np.abs(Y), np.minimum(Z, 60 - Z)])
near = (d_faces < STRIP).sum(axis=0)
inset = (np.abs(X) <= 70 - OFF) & (np.abs(Y) <= 70 - OFF) & (Z >= OFF) & (Z <= 60 - OFF)
keep_in = inset & (near < 2)

# ---------------- what the hub occupies (both sides) ----------------
SV_Z = H.SV_W / 2         # servo half-height about the hub axis is SV_W/2 in z (the width of the servo is along z)
servos = {}
for side in (+1, -1):
    for tag, y_shaft, long_dir, xf in (("B", 0.0, +1, H.SERVO_B_FACE), ("A", -H.CD, -1, H.SERVO_A_FACE)):
        y0 = y_shaft - H.SV_SHAFT_END if long_dir > 0 else y_shaft - (H.SV_L - H.SV_SHAFT_END)
        servos[(tag, side)] = dict(y0=y0, y1=y0 + H.SV_L, y_shaft=y_shaft, xf=xf, side=side)

occ = np.zeros_like(keep_in)
for (tag, side), s in servos.items():
    xa, xb = sorted((side * (s["xf"] - H.SV_H), side * s["xf"]))
    occ |= box_mask(xa - CLR, xb + CLR, s["y0"] - CLR, s["y1"] + CLR, HZ - SV_Z - CLR, HZ + SV_Z + CLR)
    occ |= cylx_mask(s["y_shaft"], HZ, H.SV_BOSS_D / 2 + CLR, side * s["xf"], side * (s["xf"] + H.SV_BOSS_H) + side * CLR)
    occ |= cylx_mask(s["y_shaft"], HZ, H.SV_BOSS_D / 2 + CLR, side * (s["xf"] - H.SV_H - 4.1) - side * CLR, side * (s["xf"] - H.SV_H))
for side in (+1, -1):
    occ |= cylx_mask(0.0, HZ, H.HOUSE_OD / 2 + CLR, side * H.X_HOUSE_IN - side * CLR, side * 70.0)          # housing tube
    occ |= cylx_mask(0.0, HZ, H.GEAR_OD / 2 + CLR, side * H.X_GEAR[0] - side * CLR, side * (H.X_GEAR[1] + CLR))   # gear A
    occ |= cylx_mask(-H.CD, HZ, H.GEAR_OD / 2 + CLR, side * H.X_GEAR[0] - side * CLR, side * (H.X_GEAR[1] + CLR))  # pinion A
    occ |= cylx_mask(0.0, HZ, H.HOLLOW_OD / 2 + CLR, side * H.X_HOLLOW[0] - side * CLR, side * 70.0)        # hollow shaft
    occ |= cylx_mask(0.0, HZ, 10.0 + CLR, side * (H.B_ADAPTER[0] - CLR), side * (H.B_ADAPTER[1] + CLR))      # horn adapter on servo B
free = keep_in & ~occ

vox = RES ** 3 / 1000.0   # cm3 per voxel
print(f"envelope {L:.0f} x {L:.0f} x 60 mm; keep-in (inset {OFF} mm, {STRIP:.0f} mm edge strips clear) {keep_in.sum() * vox:.0f} cm3; "
      f"servos and hub with {CLR:.0f} mm clearance take {(keep_in & occ).sum() * vox:.0f} cm3; free {free.sum() * vox:.0f} cm3")

# ---------------- the bays ----------------
yB = max(s["y1"] for (t, _), s in servos.items() if t == "B")      # front end of servo B
yA = min(s["y0"] for (t, _), s in servos.items() if t == "A")      # rear end of servo A
zlo = HZ - SV_Z - CLR
zhi = HZ + SV_Z + CLR
bays = {
    "front (y > servo B)":   (-70, 70, yB + CLR, 70, 0, 60),
    "rear (y < servo A)":    (-70, 70, -70, yA - CLR, 0, 60),
    "lower (z < servos)":    (-70, 70, -70, 70, 0, zlo),
    "upper (z > servos)":    (-70, 70, -70, 70, zhi, 60),
    "centre gap between the servo pairs": (-(H.SERVO_B_FACE - H.SV_H - 4.1 - CLR), H.SERVO_B_FACE - H.SV_H - 4.1 - CLR, -70, 70, 0, 60),
}
print("\nfree bays (keep-in minus servos and hub; bays overlap each other):")
for n, (x0, x1, y0, y1, z0, z1) in bays.items():
    m = free & box_mask(x0, x1, y0, y1, z0, z1)
    pts = np.argwhere(m)
    if len(pts):
        ext = [(xs[pts[:, 0]].min(), xs[pts[:, 0]].max()), (ys[pts[:, 1]].min(), ys[pts[:, 1]].max()), (zs[pts[:, 2]].min(), zs[pts[:, 2]].max())]
        e = " x ".join(f"{b - a + RES:.0f}" for a, b in ext)
    else:
        e = "none"
    print(f"  {n:38s} {m.sum() * vox:6.0f} cm3   extent {e} mm")

# ---------------- components (PLACEHOLDERS: sizes and masses are assumptions, no parts chosen) ----------------
WIN_X, WIN_Z = 40.8, 36.8       # body.py: window axis on the +y face
LAMP_X = WIN_X - 30.6           # headlamp about 30.6 mm toward -x from the window axis (body-spec.md), same height
comps = {  # name: (mass g, (x0, x1, y0, y1, z0, z1), note)
    "main board (processor, 4 motor drivers, servo bus)": (35.0, (-35, 35, -6, 62, 4, 11.6),   "70 x 68 x 7.6 mm placeholder, low in the lower bay"),
    "power board (solar conditioning, no battery)":       (12.0, (-22, 22, -12, 18, 44, 50),    "44 x 30 x 6 mm placeholder, upper bay"),
    "camera module behind the window":                    (12.0, (WIN_X - 12.5, WIN_X + 12.5, 57, 66, WIN_Z - 12, WIN_Z + 12), "25 x 24 x 9 mm module plus lens, lens 1 mm behind the pane"),
    "headlamp (sealed beam) and driver":                  (5.0,  (LAMP_X - 11, LAMP_X + 11, 51, 66, WIN_Z - 7.25, WIN_Z + 7.25), "22 x 14.5 bezel, 15 mm deep"),
    "patch antenna, top":                                 (6.0,  (-17.5, 17.5, -17.5, 17.5, 53, 57), "35 x 35 x 4 mm; needs a non-conductive window in a carbon top"),
}
extra_mass = {  # no position in the box needed: on or near the centre
    "wiring, connectors, servo cables": (15.0, (0.0, 0.0, HZ)),
    "solar cells (four faces, about 60% coverage)": (None, (0.0, 0.0, HZ)),
}
CELL_AREA_CM2 = (2 * 140 * 140 + 2 * 140 * 60) / 100.0 * 0.6      # ASM: two 140 x 140 faces and two 140 x 60 faces, 60% covered
CELL_G_PER_CM2 = (0.15, 0.25, 0.35)                              # ASM: thin to thick bonded cells with cover and wiring; no cell chosen

print("\nplacement checks (box inside the keep-in volume, clear of servos and hub, clear of each other):")
ok_all = True
placed = {}
for n, (m, (x0, x1, y0, y1, z0, z1), note) in comps.items():
    bm = box_mask(x0, x1, y0, y1, z0, z1)
    n_vox = bm.sum()
    bad_keep = (bm & ~keep_in).sum()
    bad_occ = (bm & occ).sum()
    placed[n] = bm
    ok = bad_keep == 0 and bad_occ == 0
    ok_all &= ok
    print(f"  {'OK ' if ok else 'BAD'} {n:52s} {m:5.1f} g  {(x1 - x0):4.0f} x {(y1 - y0):3.0f} x {(z1 - z0):3.0f}   outside keep-in {bad_keep * vox:.1f} cm3, on servos/hub {bad_occ * vox:.1f} cm3")
names = list(placed)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        o = (placed[names[i]] & placed[names[j]]).sum()
        if o:
            ok_all = False
            print(f"  BAD overlap {names[i]} / {names[j]}: {o * vox:.1f} cm3")
print("  all placements clear" if ok_all else "  PROBLEMS above")
used = sum(m.sum() for m in placed.values()) * vox
print(f"  placed components take {used:.0f} cm3 of the {free.sum() * vox:.0f} cm3 free ({used / (free.sum() * vox):.0%})")

# ---------------- mass and centre of mass ----------------
print("\nmass of the body contents (grams) against the 386 g left of 1.0 kg:")
SHELL = {"woven plates, 1.0 mm": 113.0 + 28.0, "forged tub, 1.5 mm": 164.0}   # budget table in docs/body-redesign.md (plates plus about 28 g of keys and adhesive)
ALLOW = 4 * 6.0 + 4 * 2.0 + 15.0 - 15.0                                       # bore rings, screws and inserts (the 15 g seal is counted below)
SEAL = 15.0
for shell_name, shell_g in SHELL.items():
    for cg in CELL_G_PER_CM2:
        cells = CELL_AREA_CM2 * cg
        parts = sum(m for m, _, _ in comps.values()) + extra_mass["wiring, connectors, servo cables"][0]
        total = shell_g + ALLOW + SEAL + parts + cells
        print(f"  {shell_name:22s} cells {cg:.2f} g/cm2 ({cells:3.0f} g): shell {shell_g:3.0f} + rings/screws {ALLOW:2.0f} + seal {SEAL:.0f} + electronics etc {parts:3.0f} + cells {cells:3.0f} = {total:4.0f} g  ({'over by' if total > 386 else 'under by'} {abs(total - 386):.0f} g)")

# centre of mass (y, z) of the body contents with plates and mid cells; x is symmetric apart from the camera and headlamp
shell_g = SHELL["woven plates, 1.0 mm"]
cells_g = CELL_AREA_CM2 * CELL_G_PER_CM2[1]
lumps = [(shell_g + ALLOW + SEAL, 0.0, HZ), (cells_g, 0.0, HZ), (extra_mass["wiring, connectors, servo cables"][0], 0.0, HZ)]
for n, (m, (x0, x1, y0, y1, z0, z1), _) in comps.items():
    lumps.append((m, (y0 + y1) / 2, (z0 + z1) / 2))
M = sum(m for m, _, _ in lumps)
cy = sum(m * y for m, y, _ in lumps) / M
cz = sum(m * z for m, _, z in lumps) / M
print(f"\nbody contents (plates, mid cells): {M:.0f} g, centre of mass y = {cy:+.1f} mm, z = {cz:.1f} mm (hub axis at y = 0, z = 30)")
# chassis_sim.py: the whole-rover centre of mass at a symmetric stance is (body lump * 0 + hub + servos) / total, because the struts, wheels and
# supports are roughly symmetric about y = 0; that gave -2.9 mm with the 386 g body lump at y = 0. Replace the lump by this layout's contents.
import chassis_sim as C  # noqa: E402
g = 1000.0
hub_servo_moment = g * (C.M_HUB * (-5.0) + 2 * 0.055 * C.SERVO_B_Y * 1000 + 2 * 0.055 * C.SERVO_A_Y * 1000)    # g.mm of hub parts and servos about y = 0
other = g * (C.M_HUB + C.M_SERVO + C.M_STRUT + C.M_WHEEL + C.M_SUPPORT)                                          # g, everything but the body
sim_y = hub_servo_moment / (C.M_BODY * g + other)
new_y = (M * cy + hub_servo_moment) / (M + other)
need = -hub_servo_moment / (C.M_BODY * g)
print(f"simulation (body lump {C.M_BODY * g:.0f} g at y = 0): whole-rover centre of mass y = {sim_y:+.1f} mm; this layout ({M:.0f} g at y = {cy:+.1f}, total {M + other:.0f} g): y = {new_y:+.1f} mm")
print(f"a {C.M_BODY * g:.0f} g body would put the whole rover on the hub axis at a centroid of y = {need:+.1f} mm; the z shift of the whole centre of mass is "
      f"{M * (cz - HZ) / (M + other):+.2f} mm (negligible)")

# ---------------- picture ----------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    fig, ax = plt.subplots(1, 2, figsize=(12, 5.6))
    cols = {"main": "#4c78a8", "power": "#f58518", "camera": "#54a24b", "headlamp": "#e45756", "patch": "#b279a2"}
    pal = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#b279a2"]

    def draw(a, ia, ib, xl, yl, title):
        a.add_patch(Rectangle((-70, 0) if ib == 2 else (-70, -70), 140, 60 if ib == 2 else 140, fill=False, lw=1.5, ec="k"))
        a.add_patch(Rectangle((-70 + OFF, OFF if ib == 2 else -70 + OFF), 140 - 2 * OFF, (60 - 2 * OFF) if ib == 2 else 140 - 2 * OFF, fill=False, lw=0.8, ls="--", ec="gray"))
        for (tag, side), s in servos.items():
            ext = {0: (side * (s["xf"] - H.SV_H), side * s["xf"]), 1: (s["y0"], s["y1"]), 2: (HZ - SV_Z, HZ + SV_Z)}
            (a0, a1), (b0, b1) = ext[ia], ext[ib]
            a.add_patch(Rectangle((min(a0, a1), min(b0, b1)), abs(a1 - a0), abs(b1 - b0), fc="#cccccc", ec="#666666", lw=0.8))
        for k, (n, (m, (x0, x1, y0, y1, z0, z1), _)) in enumerate(comps.items()):
            e = {0: (x0, x1), 1: (y0, y1), 2: (z0, z1)}
            (a0, a1), (b0, b1) = e[ia], e[ib]
            a.add_patch(Rectangle((a0, b0), a1 - a0, b1 - b0, fc=pal[k], alpha=0.75, ec="k", lw=0.6, label=n.split(" (")[0]))
        a.plot([0], [0 if ib == 1 else HZ], "r+", ms=10)
        a.set_xlim(-76, 76); a.set_ylim((-4, 64) if ib == 2 else (-76, 76)); a.set_aspect("equal")
        a.set_xlabel(xl); a.set_ylabel(yl); a.set_title(title, fontsize=10)
    draw(ax[0], 0, 1, "x (mm); +x is the page's right", "y (mm); the window end is +y, at the top", "Top view (looking down): servos grey, components coloured; dashed = keep-in inset")
    draw(ax[1], 1, 2, "y (mm)", "z (mm)", "Side view from +x, +y to the right: hub axis (red +) at y = 0, z = 30")
    ax[1].set_xlim(-76, 76)
    # the window on the front face, in the side view
    ax[1].add_patch(Rectangle((66.5, WIN_Z - 13), 3.5, 26, fc="none", ec="k", lw=1.2, ls=":"))
    ax[0].legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    out = HERE.parent.parent / "docs" / "images" / "body-layout.png"
    out.parent.mkdir(exist_ok=True)
    fig.tight_layout(); fig.savefig(out, dpi=130); print("\nwrote", out)
except Exception as e:  # the picture is optional
    print("picture skipped:", e)
