#!/usr/bin/env python3
"""Load cases for the body's topology optimisation: the numbers behind docs/load-cases.md.   (plain python3; every figure is SRC, ESTIMATE or ASM, as marked)

Run: python3 hardware/body/load_cases.py
SRC = a figure from a cited document in this repository; ESTIMATE = my arithmetic from stated inputs; ASM = my assumption (the owner should confirm those marked OWNER).
"""
import math

G = 9.81
W_KG = 1.054                         # kg: the real body contents (439.7 g) with the 614 g of drivetrain (layout.py, chassis-simulation.md); the design mass is 1.0 kg
W = W_KG * G                         # N

print(f"weight at {W_KG:.3f} kg: {W:.1f} N (1.0 kg: {1.0 * G:.1f} N)\n")

# ---------------- LC1: static, any stance (hub bearing reactions) ----------------
# SRC: hub.py: the housing's two bearing pairs are centred at |x| = 70.25 (outer) and 63.25 (inner), the strut bosses at 73.25-80.25 (A) and 81.25-88.25 (B).
X_B_OUT, X_B_IN = 70.25, 63.25
X_LOAD = {"A": 76.75, "B": 84.75}    # mm, boss midpoints
print("LC1 STATIC (every stance and rest orientation, quasi-static; chassis_sim.py):")
F_STATIC = W / 2                     # worst case: one wheel carries the whole weight, shared by the two sides (the planar model: reactions on one or two features)
print(f"  worst single wheel per side: {F_STATIC:.2f} N (the whole weight over two sides, on one wheel)")
for tag, xl in X_LOAD.items():
    r_out = F_STATIC * (xl - X_B_IN) / (X_B_OUT - X_B_IN); r_in = -F_STATIC * (xl - X_B_OUT) / (X_B_OUT - X_B_IN)
    print(f"  strut {tag} (load at |x| {xl}): outer bearing {r_out:.1f} N, inner bearing {r_in:.1f} N (opposite sign), arm ratios {r_out / F_STATIC:.2f} and {r_in / F_STATIC:.2f}")
print("  servo holds (SRC chassis-simulation.md, 2026-11-14 update): 0.169 N.m maximum per strut at the real mass (0.160 at 1.0 kg); 0.34 N.m with the usual margin of 2")

# ---------------- LC2: servo torque reaction at the servo mounts ----------------
print("\nLC2 SERVO TORQUE ON THE MOUNTS (the servo's output torque is reacted by its mounting screws into the shell):")
# ASM: the screw pattern of the STS3215 read by eye from the Feetech drawing: four self-tapping screws at the corners of about 40 x 21 mm; their distances from the output axis range about 15 to 25 mm
for name, T in (("maximum static hold", 0.169), ("design hold, margin 2", 0.34), ("rated torque (SRC Feetech)", 0.98), ("peak (stall) torque (SRC Feetech)", 2.9)):
    lo, hi = T / 0.025, T / 0.015
    print(f"  {name:36s} {T:5.3f} N.m: total tangential reaction at the screws {lo:5.0f} to {hi:5.0f} N ({lo / 4:4.0f} to {hi / 4:4.0f} N per screw, ESTIMATE)")
print("  the stall torque caps what a strut impact can push through the gear train into the mounts (the gears or the servo fail first)")
print(f"  at the 0.07 m strut the stall torque corresponds to a tip force of {2.9 / 0.07:.0f} N tangential")

# ---------------- LC3: drop onto the wheels ----------------
print("\nLC3 DROP (OWNER to choose the height; ESTIMATE: energy method, F = m g (1 + h/d) over a stopping distance d through the wheels, struts and bearings):")
print(f"  {'h m':>5s} {'d mm':>5s} | {'peak g':>6s} {'total N':>8s} {'per wheel N':>12s} | strut B outer-bearing reaction N (x3.07)")
for h in (0.3, 0.6):
    for d in (2, 3, 5, 10):
        k = 1 + h * 1000 / d
        f = W * k
        print(f"  {h:5.1f} {d:5d} | {k:6.0f} {f:8.0f} {f / 4:12.0f} | {f / 4 * 3.07:6.0f}")
print("  recommended design case (mine): h = 0.3 m (a table), d = 3 mm: about 100 g, 1.1 kN in all, 270 N per wheel, no yield; and h = 0.6 m as a no-fracture check")

# ---------------- LC4: righting rolls ----------------
print("\nLC4 RIGHTING ROLL (the body falls over a corner when a strut move rolls it; chassis_sim.py: the centre of mass drops by up to about 30 mm):")
dh = 0.030
E = W_KG * G * dh
for d in (0.5, 1.0, 2.0):
    print(f"  energy {E:.2f} J stopped in {d:.1f} mm of crushed corner and shell: {E / (d / 1000):.0f} N at a body corner (ESTIMATE)")

# ---------------- LC5: the lid ----------------
print("\nLC5 LID CLAMP (per lid; the lid is pulled onto its seam gasket by four cams):")
print("  cam gasket washer (SRC cam_estimate.py): 26 to 102 N axial per cam on its thread in the body")
SIGMA = (0.5, 2.0)                    # MPa: silicone 50 Shore A at about 38% compression (the handbook range used in to-be-measured.md item 5; ESTIMATE)
LOOP, WID = 4 * 132.0, 2.0            # mm, the seam gasket's loop (2 mm groove, inner edge 65 mm from the axis; lid_cad.py) and its width
lo, hi = SIGMA[0] * LOOP * WID, SIGMA[1] * LOOP * WID
print(f"  seam gasket (a flat 2 mm wide gasket: the UPPER BOUND; a 1 mm round cord has a narrower contact): loop {LOOP:.0f} mm x {WID:.0f} mm wide at {SIGMA[0]} to {SIGMA[1]} MPa = {lo:.0f} to {hi:.0f} N per lid, so {lo / 4:.0f} to {hi / 4:.0f} N through each of the four catches")
_ov = (2.1 - 1.5) / 2; _area = 2 * _ov * 1.5
print(f"  NOT previously estimated: this is about 5 times the cam washer's 26 to 102 N; a softer gasket (30 to 40 Shore A) or a narrower bead would cut it. Flag for the cam design: through one catch the head bears on about {_area:.1f} mm2 of rail (0.3 mm overlap each side of the 1.5 mm slit over an assumed 1.5 mm chord), so {lo / 4 / _area:.0f} to {hi / 4 / _area:.0f} MPa (crude).")
print("  spring contacts (SRC contact_fit.py): 10.6 N on each side face at mid stroke, equal and opposite on a lid; 6.4 N of friction while a lid is lifted (ESTIMATE)")

# ---------------- LC6: handling ----------------
print("\nLC6 HANDLING (ASM): picked up in one hand, squeezed 30 N between the two hub faces (struts and wheels removed from the load path), or 30 N point loads on the end faces (OWNER to confirm).")

# ---------------- strength check at the hub bore ----------------
print("\nCHECK that the loads are modest for the material (SRC body-redesign.md: forged carbon E 35.5 GPa flexural and 192 MPa tensile yield (Easy Composites), >46.9 GPa and >113.7 MPa (Rock West, from models); use 35.5 GPa and 113.7 MPa):")
for label, f in (("LC1 worst bearing reaction (B strut)", F_STATIC * 3.07), ("LC3 recommended case", W * (1 + 300 / 3) / 4 * 3.07)):
    area = 28.0 * 3.0                # mm2: the housing flange (28 mm across, 3 mm) bearing on the wall's bore, ASM
    print(f"  {label:38s} {f:6.0f} N on about {area:.0f} mm2 of flange: {f / area:5.1f} MPa bearing (against 113.7 MPa: x{113.7 / (f / area):.0f})")
