"""Interior layout of the body. The body is FORGED carbon (owner, 2026-11-12: assumed from now on, no longer a competition with woven plates or layup).

Run: .venv/bin/python hardware/body/layout.py    (needs the venv for numpy, matplotlib and hub.py's build123d import; no CAD is exported)

What it does
  1. Defines the KEEP-IN volume: the 140 x 140 x 60 mm envelope pulled in 2.5 mm from every outer face (a 1.5 mm forged wall plus 1 mm of draft and
     tolerance). No edge strips: a forged body has no bonded keys at its edges (the plates route needed a 6 mm strip for them).
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
STRIP = 0.0               # edge strip kept clear: none for a forged body (the 6 mm strip was room for the bonded keys of the plates route)
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
print(f"envelope {L:.0f} x {L:.0f} x 60 mm; keep-in (inset {OFF} mm, no edge strips: forged) {keep_in.sum() * vox:.0f} cm3; "
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
# Owner's decisions (2026-11-11): top and bottom faces are identical lids carrying cells; the body is kept symmetric about the transverse (z = 30) plane;
# one window for the camera, its LED ring and the ranging sensor (the beamsplitter was dropped on 2026-11-14); the comms antenna on the opposite end face at the diagonally opposite position (a 180 degree turn about z carries
# the camera's position onto the antenna's).
# Antenna (owner, 2026-11-13, supersedes the gravity-oriented whip with a counterweight): the radio is 2.4 GHz. The comms antenna is a 2.4 GHz ceramic patch polarised along z behind an
# RF-transparent 26 mm window in the -y wall (the identical-look circle); upright and inverted are a 180 degree turn about y, which keeps the polarisation vertical, so nothing has to
# orient itself. GNSS was dropped by the owner the same day (absolute positioning is left to the Lighthouse idea, docs/positioning.md section 12), so the lids carry cells only.
# Sizes and masses are assumptions; see docs/positioning.md.
# End faces (owner, 2026-11-12, hardware/body/cell_endface.py; supersedes the 60 x 60 mm square at x = +-40): no panel; along the 140 mm of the end face the hole (window, 26 mm),
# the cell pocket (four SM940K09L standing, worst case 87.2 mm) and the face edges are separated by three EQUAL gaps, (140 - 26 - 87.2) / 3 = 8.933 mm.
# Seen from outside the +y face the hole is on the viewer's left (+x), so the window is at x = 70 - (gap + 13) = +48.07, the antenna at x = -48.07 on the -y face, z = 30.
END_HOLE_D = 26.0
END_POCKET_W = 4 * 21.5 + 4 * 0.3
END_GAP = (140.0 - END_HOLE_D - END_POCKET_W) / 3
WIN_X, WIN_Z = 70.0 - (END_GAP + END_HOLE_D / 2), 30.0
ANT_X, ANT_Z = -WIN_X, 30.0
ANT_WIN_HALF = 13.5     # the -y end face's RF-transparent window is a 27 mm SQUARE (owner, 2026-11-13), flush with the face, so the 25 x 25 mm patch sees its whole area
# LED ring instead of the beamsplitter (owner idea, 2026-11-14): the camera and its lamp no longer share the window through a 45 degree plate. The camera moves forward until its lens is 1.5 mm
# behind the cover glass (hood and black mask ring against the glass), and a ring of six mid-power white LEDs on a thin board sits round the lens behind the same glass: the 26 mm window is back to the
# original size (WIN_R_GLASS = 13), one circle on the same centre. Ranging sensor (VL53L5CX, docs/hardware-spec.md section 5): in the ring's inboard slot (10.5 mm toward the body's centre line from the camera axis), on the camera's horizontal axis (z = 30: 62.1 mm above the ground at the 25 degree stance, the same either way up), turned 90 degrees so its long axis (6.4 mm) is vertical and its 3.0 mm width is horizontal (edge 12.0 mm from the camera axis, 0.6 mm inside the circle at the sensor's corner), looking +y, tilted down 22 degrees as in the sim by a small wedge (not modelled).
WIN_R_GLASS = 13.0
RNG_X, RNG_Z = WIN_X - 10.5, WIN_Z       # the ring's INBOARD slot, on the camera's horizontal axis (owner 2026-11-14: the top and bottom slots break the symmetry about z = 30, since upside down the sensor would be 72.6 mm above the ground instead of 51.6; at z = 30 it is 62.1 mm either way; the sensor is turned 90 degrees, long axis vertical; docs/hardware-spec.md section 5)
END_CELL_X = 70.0 - (2 * END_GAP + END_HOLE_D + END_POCKET_W / 2)   # body x of the end pocket's centre on the +y face (-17.47); on the -y face it is +17.47
comps = {  # name: (mass g, (x0, x1, y0, y1, z0, z1), note, optional (x, y, z) of the centre of mass if not the box centre)
    "processor + motor-driver board (lower lid module)":   (20.0, (-35, 35, -6, 62, 4, 11.6),      "70 x 68 x 7.6 mm placeholder, rides on the bottom lid", None),
    "power board (upper lid module)": (20.0, (-35, 35, -6, 62, 48.4, 56.0), "mirror of the lower board about z = 30, rides on the top lid", None),
    "cell protection board (BQ29700 + FET pair)": (1.5, (26.5, 34.5, 39.0, 42.0, 24.0, 36.0), "8 x 3 x 12 mm placeholder (x, y, z) at the battery's +x end, beside the cell's tab end (moved with the battery, 2026-11-14): the protection IC and its two FETs (28 mOhm total or less), so the under-voltage trip sees the cell and not the cell less the lid contacts' drop (contact_estimate.py)", None),
    "battery (1S 1000 mAh, 25C class)":     (28.5, (-25.5, 25.5, 38.0, 48.0, 14.5, 45.5), "MOVED 2026-11-14 from the centre gap to the front bay, lying across x (51 mm), 10 mm thick in y, 31 mm tall, between the lid boards: the eight servo connectors face the centre gap and their plugs and wires need all of it (servo_connectors in this file, wire_routes.py). Overlander SKU 2809 class pouch, about 50 x 31 x 9 mm and 28 to 28.5 g (retailer listings differ); no protection circuit assumed (it goes on the power board); docs/hardware-spec.md section 4", None),
    "camera module":                        (12.0, (WIN_X - 12.0, WIN_X + 12.0, 57.0, 66.0, WIN_Z - 17, WIN_Z + 17), "SPI camera with frame buffer (Arducam Mini class, 34 x 24 mm board turned long side vertical, owner 2026-11-14; depth 9 mm is an ESTIMATE, to check against the module): 24 x 34 x 9 mm; its lens front is 1 mm ahead of the box (y = 67), 1.5 mm behind the cover glass's inner face, looking +y (no beamsplitter: owner idea 2026-11-14)", None),
    "LED ring (6 mid-power white LEDs on a ring board)": (4.0,  (WIN_X - 8.9, WIN_X + 11.8, 66.0, 67.5, WIN_Z - 11.4, WIN_Z + 11.4), "six 2835-class white LEDs (3.5 x 2.8 mm; Samsung LM281B+ Pro class) round the lens at about 10 mm radius, at 0, 45, 135, 180, 225 and 315 degrees (the top slot is the ranging sensor's, the bottom is left empty), in three series pairs on the 7.4 V rail, behind the same cover glass and its smoked film; a black mask and a lens hood keep their light out of the lens; the box stands for the ring zone; docs/hardware-spec.md section 5, hardware/body/lamp_budget.py", None),
    "ranging sensor (VL53L5CX) on its board":    (2.0,  (RNG_X - 1.5, RNG_X + 1.5, 66.2, 67.7, RNG_Z - 3.2, RNG_Z + 3.2), "6.4 x 3.0 x 1.5 mm sensor, long axis vertical, on a small board in the inboard (x - 10.5) slot of the LED ring, behind the shared cover glass, looking +y", None),
    "comms patch (2.4 GHz) on its ground board": (9.0, (ANT_X - 12.5, ANT_X + 12.5, -67.5, -62.0, ANT_Z - 12.5, ANT_Z + 12.5), "Taoglas WPC.25A.07.0150C: 25 x 25 x 5.5 mm incl. its own ground board, directly behind the flush 27 mm square window plug in the -y wall (mass ASM, not in the datasheet)", None),
    "XBee 3 Micro (XB3-24AUM-J) on its carrier board": (3.0, (-11.0, 11.0, -67.0, -64.0, ANT_Z - 8, ANT_Z + 8), "module 13.5 x 19.3 x 2.2 mm (0.533 x 0.76 x 0.087 in, Digi XBee 3 family datasheet) on a 22 x 16 x 0.8 mm carrier board with the five wire pads and 3.3 V decoupling, long side along x, U.FL jack on the patch (-x) side, in the rear bay at the centre (x -11 to 11: behind the gap between the servo pairs, so the servos' connectors at their rear faces keep their access, which a place beside the patch did not), centred on x = 0 and z = 30, 24.6 mm from the patch; stays in the body (an RF cable must not cross the lid joint); the patch's standard 150 mm lead is too long here: order a custom 40 to 60 mm lead (Taoglas offers custom lengths); mass ASM, 1.5 g module and 1.5 g board", None),
}
# Servo connector plug zones (2026-11-14; Feetech STS3215 specification A/0 2020-04-10, page 6 drawing, private repo datasheets/): each servo has TWO 3-pin 2.54 mm terminals ("5264 / 2.54 3P", S V G, wired in
# parallel for daisy-chaining) on its BACK face (the face opposite the output shaft, toward the body's centre plane), side by side across the servo's width, 11.4 to 17.5 mm from the shaft axis toward the long end,
# +-9.9 mm either side of the width centre line (read from the drawing; the drawing's two views differ in scale along the width, so +-8 to 10).  The connector shroud stands about 3 mm proud of the back face (side view);
# how far the mated plug and its wires stand out is NOT given: ESTIMATE 10 mm (range 6 to 12 mm: a 3-circuit Molex KK 254 housing is 8.1 x 5 mm in plan, height not found; the plug also covers the shroud).
PLUG_D = 10.0
for (tag, side), sv in servos.items():
    back = side * (sv["xf"] - H.SV_H)
    xa, xb = sorted((back - side * PLUG_D, back - side * (CLR + 0.5)))      # from just outside the servo's 1 mm clearance shell inward (0.5 mm voxel margin); the depth is counted from the back face
    ya, yb = sorted((sv["y_shaft"] + (+1 if tag == "B" else -1) * 11.0, sv["y_shaft"] + (+1 if tag == "B" else -1) * 18.0))
    comps[f"servo {tag} ({'+' if side > 0 else '-'}x) connector plug zone"] = (0.0, (xa, xb, ya, yb, HZ - 10.5, HZ + 10.5), f"keep-out for the two 3-pin plugs on the servo's back face and their wires: {PLUG_D:.0f} mm deep (ESTIMATE, range 6 to 12), y {ya:.0f} to {yb:.0f}, z 19.5 to 40.5; the plugs open toward the body's centre plane", None)

OUT_COMPS = {}  # outside the envelope, counted for mass and balance only (the whip is gone: the antennas are inside the body behind RF windows)
# Servo mounting plates (2026-11-15, hardware/body/servo_mounts.py, docs/servo-mounts.md): each servo is screwed to its own 1.5 mm 6061 plate (45.23 x 24.73 mm, an 11 mm bore, four 2.2 mm holes: 4.1 g) on its output face;
# counted here for mass and balance only (the plate sits against the servo's face, inside the 1 mm clearance shell, so it is not a separate placed box)
PLATE_G = 4.1
MOUNT_ALONG, MOUNT_ACROSS = (8.4, 28.9), 10.4        # mm: the servo's four mounting holes from the output axis toward the long end, and either side of the centre line (read from the Feetech drawing by servo_mounts.py; ASM that they are the mounting holes)
MOUNT_HEAD_D, MOUNT_HEAD_H = 3.8, 1.2                # mm: the pan heads of the 2.0 mm self-tapping screws (ASM)
for (tag, side), sv in servos.items():
    OUT_COMPS[f"servo mounting plate {tag} ({'+' if side > 0 else '-'}x)"] = (PLATE_G, (side * (sv["xf"] + 0.75), (sv["y0"] + sv["y1"]) / 2, HZ))
extra_mass = {"wiring, connectors, board-to-board links": (15.0, (0.0, 0.0, HZ))}
# cells (owner, 2026-11-12): Anysolar IXOLAR SolarMD parts; top and bottom faces identical (6 x SM940K09L 44.5 x 21.5, 2 x SM401K08TF 90 x 40, 1 x SM531K08TFS 89 x 52 in one pocket),
# both end faces 4 x SM940K09L standing; none on the hub faces (the struts are there). Masses: SM940K09L 3.3 g and SM531K08TFS 9.4 g from their datasheets (Rev. 2025/2026,
# preliminary), SM401K08TF scaled by area from the SM531 (not read). See docs/body-redesign.md and cell_pocket.py, cell_endface.py.
SM940_G, SM531_G, SM401_G = 3.3, 9.4, 9.4 * 40 / 52
FACE_TB = (6 * 44.5 * 21.5 + 89 * 52 + 2 * 90 * 40) / 100          # cm2: 175.7
FACE_END = 4 * 44.5 * 21.5 / 100                                    # cm2: 38.3
CELL_MASS_TB = 6 * SM940_G + SM531_G + 2 * SM401_G                  # g per top or bottom face
CELL_MASS_END = 4 * SM940_G                                         # g per end face
CELL_AREA_CM2 = 2 * FACE_TB + 2 * FACE_END
CELL_MASS_G = 2 * CELL_MASS_TB + 2 * CELL_MASS_END
CELL_G_PER_CM2 = (CELL_MASS_G / CELL_AREA_CM2,)                     # one effective value now that parts are chosen (about 0.26 g/cm2)

print("\nplacement checks (box inside the keep-in volume, clear of servos and hub, clear of each other):")
ok_all = True
placed = {}
for n, (m, (x0, x1, y0, y1, z0, z1), note, _c) in comps.items():
    bm = box_mask(x0, x1, y0, y1, z0, z1)
    bad_keep = (bm & ~keep_in).sum()
    bad_occ = (bm & occ).sum()
    placed[n] = bm
    ok = bad_keep == 0 and bad_occ == 0
    ok_all &= ok
    print(f"  {'OK ' if ok else 'BAD'} {n:60s} {m:5.1f} g  {(x1 - x0):4.0f} x {(y1 - y0):3.0f} x {(z1 - z0):3.0f}   outside keep-in {bad_keep * vox:.1f} cm3, on servos/hub {bad_occ * vox:.1f} cm3")
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
print(f"  cells: top and bottom {FACE_TB:.1f} cm2 each ({CELL_MASS_TB:.1f} g), end faces {FACE_END:.1f} cm2 each ({CELL_MASS_END:.1f} g), total {CELL_AREA_CM2:.0f} cm2, {CELL_MASS_G:.0f} g")
print(f"  window at x = {WIN_X:+.2f}, antenna at x = {ANT_X:+.2f} (end gaps {END_GAP:.3f} mm), RF-window square {2 * ANT_WIN_HALF:.0f} mm")

# ---------------- mass and centre of mass ----------------
# Mass budget (owner, 2026-11-15): 1.5 kg total budget, 2.0 kg hard ceiling (docs/mass-headroom.md); the drivetrain (servos, hub, struts, wheels, wheel supports) is 614 g, so the body contents may be
# 886 g (budget) or 1386 g (ceiling). The old budget was 1.0 kg, which left 386 g.
DRIVETRAIN_G = 614.0
BUDGET_G, CEILING_G = 1500.0 - DRIVETRAIN_G, 2000.0 - DRIVETRAIN_G
print(f"\nmass of the body contents (grams) against the {BUDGET_G:.0f} g left of the 1.5 kg budget ({CEILING_G:.0f} g at the 2.0 kg ceiling; it was 386 g left of 1.0 kg):")
SHELL = {"forged, 1.5 mm": 164.0}                                              # forged shell, budget table in docs/body-redesign.md (the plates option, 141 g with keys, is dropped)
ALLOW = 4 * 6.0 + 4 * 2.0                                                      # bore rings, screws and inserts
SEAL = 15.0
elec = sum(m for m, _, _, _ in comps.values()) + sum(m for m, _ in OUT_COMPS.values()) + extra_mass["wiring, connectors, board-to-board links"][0]
for shell_name, shell_g in SHELL.items():
    for cg in CELL_G_PER_CM2:
        cells = CELL_AREA_CM2 * cg
        total = shell_g + ALLOW + SEAL + elec + cells
        print(f"  {shell_name:22s} cells {cg:.2f} g/cm2 ({cells:3.0f} g): shell {shell_g:3.0f} + rings/screws {ALLOW:2.0f} + seal {SEAL:.0f} + electronics etc {elec:3.0f} + cells {cells:3.0f} = {total:4.0f} g  ({'over' if total > BUDGET_G else 'under'} the budget by {abs(total - BUDGET_G):.0f} g; {CEILING_G - total:.0f} g below the ceiling; against the old 386 g: {total - 386:+.0f} g)")

lumps = []   # (mass, x, y, z)
shell_g = SHELL["forged, 1.5 mm"]
cells_g = CELL_MASS_G
# cells: top and bottom equal and opposite in z; the end pockets sit on the side away from the window or antenna (centres at x = -17.47 on +y and +17.47 on -y)
lumps += [(CELL_MASS_TB, 0.0, 0.0, 60.0), (CELL_MASS_TB, 0.0, 0.0, 0.0),
          (CELL_MASS_END, END_CELL_X, 70.0, HZ), (CELL_MASS_END, -END_CELL_X, -70.0, HZ)]
lumps += [(shell_g + ALLOW + SEAL, 0.0, 0.0, HZ), (extra_mass["wiring, connectors, board-to-board links"][0], 0.0, 0.0, HZ)]
for n, (m, (x0, x1, y0, y1, z0, z1), _, c) in comps.items():
    lumps.append((m, *(c if c else ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))))
for n, (m, (x, y, z)) in OUT_COMPS.items():
    lumps.append((m, x, y, z))
# servos and hub parts (the body's frame, both sides), grams from hub.py: servo 55 g each; hub parts 74 g total at the hub axis
for (tag, side), s_ in servos.items():
    lumps.append((55.0, side * (s_["xf"] - H.SV_H / 2), (s_["y0"] + s_["y1"]) / 2, HZ))
lumps.append((74.0, 0.0, -5.0, HZ))
M = sum(l[0] for l in lumps)
cx, cy, cz = (sum(l[0] * l[k] for l in lumps) / M for k in (1, 2, 3))
print(f"\nbody contents + servos + hub (forged shell, IXOLAR cells): {M:.0f} g, centre of mass x = {cx:+.1f}, y = {cy:+.1f}, z = {cz:.1f} mm (hub axis at x = 0, y = 0, z = 30)")
top = sum(l[0] for l in lumps if l[3] > HZ + 0.01); bot = sum(l[0] for l in lumps if l[3] < HZ - 0.01)
print(f"mass above z = 30: {top:.0f} g, below: {bot:.0f} g (a transverse-plane-symmetric body has these equal; the camera, comms patch and battery sit on the plane)")
# struts, wheels and supports: add their roughly symmetric lumps (320 g) to get the whole-rover y
import chassis_sim as C  # noqa: E402
struts = C.M_STRUT + C.M_WHEEL + C.M_SUPPORT
whole_y = (M * cy) / (M + 1000 * struts)
sim_y = 1000 * (C.M_HUB * -0.005 + 2 * 0.055 * C.SERVO_B_Y + 2 * 0.055 * C.SERVO_A_Y) / 1.0
print(f"whole-rover centre of mass y (struts, wheels and supports taken symmetric about y = 0): {whole_y:+.2f} mm; the chassis simulation had {sim_y:+.1f} mm with the body lump at the centre")

# ---------------- picture ----------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 6))
    pal = ["#4c78a8", "#f58518", "#e9c46a", "#54a24b", "#2a9d8f", "#e45756", "#b279a2", "#9d755d", "#bab0ac", "#76b7b2", "#ff9da6"]

    def draw(a, ia, ib, xl, yl, title):
        a.add_patch(Rectangle((-70, 0) if ib == 2 else (-70, -70), 140, 60 if ib == 2 else 140, fill=False, lw=1.5, ec="k"))
        a.add_patch(Rectangle((-70 + OFF, OFF if ib == 2 else -70 + OFF), 140 - 2 * OFF, (60 - 2 * OFF) if ib == 2 else 140 - 2 * OFF, fill=False, lw=0.8, ls="--", ec="gray"))
        for (tag, side), s_ in servos.items():
            ext = {0: (side * (s_["xf"] - H.SV_H), side * s_["xf"]), 1: (s_["y0"], s_["y1"]), 2: (HZ - SV_Z, HZ + SV_Z)}
            (a0, a1), (b0, b1) = ext[ia], ext[ib]
            a.add_patch(Rectangle((min(a0, a1), min(b0, b1)), abs(a1 - a0), abs(b1 - b0), fc="#cccccc", ec="#666666", lw=0.8))
        for k, (n, (m, (x0, x1, y0, y1, z0, z1), _, _c)) in enumerate(comps.items()):
            e = {0: (x0, x1), 1: (y0, y1), 2: (z0, z1)}
            (a0, a1), (b0, b1) = e[ia], e[ib]
            a.add_patch(Rectangle((a0, b0), a1 - a0, b1 - b0, fc=pal[k % len(pal)], alpha=0.75, ec="k", lw=0.6, label=n.split(" (")[0].split(",")[0]))
        a.plot([0], [0 if ib == 1 else HZ], "r+", ms=10)
        a.set_xlim(-76, 76); a.set_ylim((-4, 64) if ib == 2 else (-84, 88)); a.set_aspect("equal")
        a.set_xlabel(xl); a.set_ylabel(yl); a.set_title(title, fontsize=9.5)
    draw(ax[0], 0, 1, "x (mm); +x is the page's right", "y (mm); the camera window is at +y (top), the comms patch at -y", "Top view: servos grey, components coloured; dashed = keep-in inset")
    ax[0].plot([WIN_X], [70], "ks", ms=7, mfc="none"); ax[0].annotate(f"camera window\n(x={WIN_X:+.1f})", (WIN_X, 70), (WIN_X - 4, 77), fontsize=7, ha="center")
    ax[0].plot([ANT_X], [-70], "k^", ms=7, mfc="none"); ax[0].annotate(f"comms patch window\n(x={ANT_X:+.1f})", (ANT_X, -70), (ANT_X + 5, -79), fontsize=7, ha="center")
    ax[0].legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    draw(ax[1], 1, 2, "y (mm); +y (camera end) to the right", "z (mm)", "Side view from +x: hub axis (red +) at y = 0, z = 30; boards mirror about z = 30")
    ax[1].set_xlim(-82, 76)
    ax[1].add_patch(Rectangle((66.5, WIN_Z - 13), 3.5, 26, fc="none", ec="k", lw=1.2, ls=":"))
    out = HERE.parent.parent / "docs" / "images" / "body-layout.png"
    out.parent.mkdir(exist_ok=True)
    fig.tight_layout(); fig.savefig(out, dpi=130); print("\nwrote", out)
except Exception as e:  # the picture is optional
    print("picture skipped:", e)
