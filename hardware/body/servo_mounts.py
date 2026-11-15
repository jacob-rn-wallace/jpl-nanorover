#!/usr/bin/env python3
"""Servo mounts: where the four servos are screwed, how the loads go, and whether the mounting plates fit.   (needs the venv: it imports layout.py and build123d)

Run: .venv/bin/python hardware/body/servo_mounts.py        (writes out/servo_mount_plates.step)

DECISION (2026-11-15, mine, OWNER to confirm; docs/servo-mounts.md): each servo is screwed to its OWN MOUNTING PLATE through the four small holes on its output face, and the plates are fastened to the
shell. A plate cannot be part of the forged shell: the screw heads are on the plate's outboard side (the servo's holes face outboard, toward the hub), and nothing outboard of the plate is reachable once the
body is closed; so the servo and its plate are one module, assembled on the bench and lowered in.
SRC: Feetech STS3215 specification A/0 (2020-04-10), page 6 drawing (private repo datasheets/): body 45.23 x 24.73 mm, output boss 9 mm across, 3.4 mm high (hub.py).  The four small holes are read by eye
from the output-face view: the drawing's callout "B-PA2.0 self-tapping screw" points at them (ASM that they are the mounting holes; the drawing does not say so).  The view is stretched about 18% along
the length relative to the width, so each axis is scaled from its own stated dimension (45.23 along, 24.73 across).
"""
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
with contextlib.redirect_stdout(io.StringIO()):
    import layout as LY

H = LY.H

# ---- 1. the hole pattern, measured in pixels of the 300 dpi crop of the output-face view ----
PX_LEN = (913 - 152) / 45.23                       # px per mm along the length (outline 152 to 913)
PX_WID = (540 - 187) / 24.73                       # px per mm across the width (outline 187 to 540)
SHAFT_PX, CENTRE_Z_PX = 745.0, 365.0               # output axis and the width centre line
HOLES_PX = [(258, 213), (258, 512), (603, 213), (603, 512)]
holes = sorted({(round((SHAFT_PX - x) / PX_LEN, 1), round(abs(CENTRE_Z_PX - y) / PX_WID, 1)) for x, y in HOLES_PX})
ALONG = sorted({h[0] for h in holes}); ACROSS = round(np.mean([h[1] for h in holes]), 1)
print(f"scales: {PX_LEN:.2f} px/mm along, {PX_WID:.2f} px/mm across (the drawing is stretched {PX_LEN / PX_WID:.2f}x)")
print(f"mounting holes (ASM: the four small output-face holes): {ALONG[0]} and {ALONG[1]} mm from the output axis toward the long end, {ACROSS} mm either side of the centre line;")
print(f"  pattern {ALONG[1] - ALONG[0]:.1f} x {2 * ACROSS:.1f} mm; reading error about +-0.3 mm along and +-0.5 across (by eye on a stretched image)")
assert (tuple(ALONG), ACROSS) == (tuple(LY.MOUNT_ALONG), LY.MOUNT_ACROSS), 'layout.py MOUNT_ALONG / MOUNT_ACROSS differ from the measured pattern'
R_FAR = float(np.hypot(ALONG[1], ACROSS)); R_NEAR = float(np.hypot(ALONG[0], ACROSS))

# ---- 2. positions in the body frame for the four servos ----
HZ = LY.HZ
rows = []
for (tag, side), s in LY.servos.items():
    ldir = +1 if tag == "B" else -1
    for a in ALONG:
        for dz in (+ACROSS, -ACROSS):
            rows.append((tag, side, side * s["xf"], s["y_shaft"] + ldir * a, HZ + dz))
print(f"\n{len(rows)} hole positions (|x| of the output face, y, z); e.g. B (+x): " + ", ".join(f"({r[3]:.1f}, {r[4]:.1f})" for r in rows if r[0] == 'B' and r[1] == 1))
print("                                          A (+x): " + ", ".join(f"({r[3]:.1f}, {r[4]:.1f})" for r in rows if r[0] == 'A' and r[1] == 1))

# ---- 3. loads on the screws (LC2 of docs/load-cases.md) ----
print("\nSCREW LOADS from the servo's torque about its output axis (a rigid plate: shear on a screw is proportional to its distance from the axis):")
S2 = 2 * (R_NEAR ** 2 + R_FAR ** 2)
print(f"  distances from the axis {R_NEAR:.1f} and {R_FAR:.1f} mm; shear per screw = T x r / sum(r^2) = T x {R_FAR / S2 * 1000:.1f} (far) and T x {R_NEAR / S2 * 1000:.1f} (near) per N.m, in N")
CAP_SHEAR, CAP_PULL = (100.0, 240.0), (100.0, 250.0)     # N, ESTIMATE: a 2.0 mm self-tapping screw in the servo's plastic housing, about 3.5 mm engaged (shear on the plastic's bearing; pull-out); the real figures are not given
for name, T in (("max hold 0.169", 0.169), ("design hold 0.34", 0.34), ("rated 0.98", 0.98), ("stall peak 2.9", 2.9)):
    f_far, f_near = T * R_FAR / S2 * 1000, T * R_NEAR / S2 * 1000
    print(f"  {name:18s}: {f_far:5.1f} N on the far screws, {f_near:5.1f} N on the near ones; margin against the {CAP_SHEAR[0]:.0f} to {CAP_SHEAR[1]:.0f} N (ESTIMATE) shear capacity: x{CAP_SHEAR[0] / f_far:.1f} to x{CAP_SHEAR[1] / f_far:.1f}")
print("  the screws also carry the servo's weight (55 g, 0.5 N) and the radial strut loads' share is taken by the hub housing, not by the servo (LC1)")

# ---- 4. the mounting plate ----
T_PLATE = 1.5                                     # mm, 6061 aluminium (ASM)
RHO_AL = 2.70
BORE_D = H.SV_BOSS_D + 2.0                         # clearance round the rotating output boss
plates, mass_each = [], None
area = H.SV_L * H.SV_W - np.pi / 4 * BORE_D ** 2 - 4 * np.pi / 4 * 2.2 ** 2
mass_each = area * T_PLATE * RHO_AL / 1000
print(f"\nPLATE: {H.SV_L:.2f} x {H.SV_W:.2f} x {T_PLATE} mm 6061 (the servo's footprint), a {BORE_D:.0f} mm bore round the output boss, four 2.2 mm clearance holes: {mass_each:.1f} g each, {4 * mass_each:.0f} g for four (not in layout.py's mass: the overage grows by this)")
print(f"  bearing at a screw hole at stall: {2.9 * R_FAR / S2 * 1000:.0f} N on {2.2 * T_PLATE:.1f} mm2 = {2.9 * R_FAR / S2 * 1000 / (2.2 * T_PLATE):.0f} MPa (6061 yields at about 275: ok)")

# clearance of the plate slab against the other parts (voxels at 1 mm)
blocked = np.zeros_like(LY.keep_in)
for n, m in LY.placed.items():
    if "plug zone" not in n:                          # the plug zones are on the servos' back faces
        blocked |= m
wr = HERE / "out" / "wire_routes.json"
if wr.exists():
    for _nm, r in json.loads(wr.read_text()).items():
        h = r["channel_side_mm"] / 2
        for a, b in zip(r["points"][:-1], r["points"][1:]):
            lo = [min(a[i], b[i]) - h for i in range(3)]; hi = [max(a[i], b[i]) + h for i in range(3)]
            blocked |= LY.box_mask(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
# hub parts (not the servos): housing tube, gear A, pinion A, hollow shaft, horn adapter on B (layout.py's masks, rebuilt without the servo bodies)
hub = np.zeros_like(LY.keep_in)
for side in (1, -1):
    hub |= LY.cylx_mask(0.0, HZ, H.HOUSE_OD / 2 + LY.CLR, side * H.X_HOUSE_IN - side * LY.CLR, side * 70.0)
    hub |= LY.cylx_mask(0.0, HZ, H.GEAR_OD / 2 + LY.CLR, side * H.X_GEAR[0] - side * LY.CLR, side * (H.X_GEAR[1] + LY.CLR))
    hub |= LY.cylx_mask(-H.CD, HZ, H.GEAR_OD / 2 + LY.CLR, side * H.X_GEAR[0] - side * LY.CLR, side * (H.X_GEAR[1] + LY.CLR))
    hub |= LY.cylx_mask(0.0, HZ, H.HOLLOW_OD / 2 + LY.CLR, side * H.X_HOLLOW[0] - side * LY.CLR, side * 70.0)
    hub |= LY.cylx_mask(0.0, HZ, 10.0 + LY.CLR, side * (H.B_ADAPTER[0] - LY.CLR), side * (H.B_ADAPTER[1] + LY.CLR))
print("\nPLATE AND SCREW-HEAD FIT (voxels of the plate's volume and the screw heads, outside the bore, that touch another part; 0 is clear):")
HEAD_D, HEAD_H = 3.8, 1.2                           # ASM: a pan head on a 2.0 mm self-tapping screw
for (tag, side), s in LY.servos.items():
    xa, xb = sorted((side * s["xf"], side * (s["xf"] + T_PLATE)))
    plate = LY.box_mask(xa, xb, s["y0"], s["y1"], HZ - H.SV_W / 2, HZ + H.SV_W / 2) & ~LY.cylx_mask(s["y_shaft"], HZ, BORE_D / 2, xa - 1, xb + 1)
    heads = np.zeros_like(plate)
    for r in rows:
        if r[0] == tag and r[1] == side:
            hx0, hx1 = sorted((side * (s["xf"] + T_PLATE), side * (s["xf"] + T_PLATE + HEAD_H)))
            heads |= LY.cylx_mask(r[3], r[4], HEAD_D / 2, hx0, hx1)
    c_plate = int((plate & (blocked | hub)).sum()); c_head = int((heads & (blocked | hub)).sum())
    print(f"  servo {tag} ({'+' if side > 0 else '-'}x): plate x {abs(xa):.1f} to {abs(xb):.1f}: {c_plate} voxels on other parts; screw heads to x {max(abs(hx0), abs(hx1)):.1f}: {c_head} voxels")

# ---- 5. CAD of the plates (reference solids, not cut from the block) ----
try:
    from build123d import Box, Cylinder, Location, export_step, import_step
    solids = None
    for (tag, side), s in LY.servos.items():
        ymid = (s["y0"] + s["y1"]) / 2
        p = Box(H.SV_L, T_PLATE, H.SV_W)                               # y long, x thin, z across
        p = p.rotate(__import__("build123d").Axis.Z, 90)               # long side along y
        p = p.moved(Location((side * (s["xf"] + T_PLATE / 2), ymid, HZ)))
        p = p - Cylinder(BORE_D / 2, 4.0).rotate(__import__("build123d").Axis.Y, 90).moved(Location((side * (s["xf"] + T_PLATE / 2), s["y_shaft"], HZ)))
        for r in rows:
            if r[0] == tag and r[1] == side:
                p = p - Cylinder(1.1, 4.0).rotate(__import__("build123d").Axis.Y, 90).moved(Location((side * (s["xf"] + T_PLATE / 2), r[3], r[4])))
        solids = p if solids is None else solids + p
    out = HERE / "out"; out.mkdir(exist_ok=True)
    export_step(solids, str(out / "servo_mount_plates.step"))
    re = import_step(str(out / "servo_mount_plates.step"))
    print(f"\nCAD: out/servo_mount_plates.step re-imports as {len(re.solids())} solid(s), volume {re.volume / 1000:.2f} cm3 (expected {4 * area * T_PLATE / 1000:.2f} cm3)")
except Exception as e:                                                # the CAD is a convenience; the numbers above stand on their own
    print("\n(CAD export skipped:", e, ")")
