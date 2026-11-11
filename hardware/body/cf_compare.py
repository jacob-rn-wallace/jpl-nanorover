"""Woven carbon laminate versus forged carbon for the 140 x 140 x 60 mm body: project-specific numbers.

Run: python3 hardware/body/cf_compare.py   (no CAD needed). Property sources are in docs/body-redesign.md; the woven values are generic
catalogue figures (flexural modulus 50 to 70 GPa for a balanced 0/90 or twill laminate), not a tested part. Forged values are Easy Composites'
untested comparative figures (E 35.5 GPa standard, 61.1 optimised; density 1.5 and 1.58).
"""
import math
AREA_CM2 = 728.0                                  # outer surface of the 140 x 140 x 60 box
MATS = {                                          # name: (flexural modulus GPa, density g/cm3)
    "woven (E 55, mid of 50-70)": (55.0, 1.55),
    "woven (E 70, high)":         (70.0, 1.55),
    "woven (E 50, low)":          (50.0, 1.55),
    "forged standard":            (35.5, 1.50),
    "forged optimised":           (61.1, 1.58),
}
REF = "woven (E 55, mid of 50-70)"; T_REF = 1.0   # reference: 1.0 mm woven wall
E0, R0 = MATS[REF]
print("1. Same panel bending stiffness (D ~ E t^3) as a 1.0 mm woven wall (E 55 GPa):")
print(f"{'material':30s} {'t mm':>6s} {'shell g':>8s} {'vs woven':>9s}")
for n, (E, r) in MATS.items():
    t = T_REF * (E0 / E) ** (1 / 3)
    m = AREA_CM2 * t / 10 * r
    print(f"{n:30s} {t:6.2f} {m:8.0f} {m / (AREA_CM2 * T_REF / 10 * R0) - 1:+9.0%}")
print("   Panel bending stiffness sets a thin shell's feel and the board/servo mounting, not strength. Forged standard needs about 17% more\n"
      "   wall for the same stiffness, which is about 12% more shell mass at the lower density; 'optimised' forged (continuous tow added) is about equal.\n")

# 2. Loads at the hub: how stressed is the wall? (planar, quasi-static, my arithmetic)
M_REV = 0.166                                     # N.m per strut hold (chassis-simulation.md)
MASS = 1.0; G = 9.81
for label, dyn in (("static", 1.0), ("drop, x5", 5.0), ("drop, x20", 20.0)):
    F = MASS * G / 2 * dyn                        # each side's hub carries half the weight, times a dynamic factor
    M = 2 * M_REV                                 # both struts on a side at their hold torque
    t = 1.0
    bore = 24.2; flange = 28.0
    A_bearing = bore * t                          # mm2, load through the hub bore wall
    sig_brg = F / A_bearing
    A_ring = math.pi / 4 * (flange ** 2 - bore ** 2)     # bonded flange ring, mm2
    r_m = (flange + bore) / 4                     # mean radius, mm
    tau_bond = M * 1000 / (r_m * A_ring)          # torque via shear over the ring (thin-ring estimate)
    print(f"2. hub load {label:9s}: F {F:5.1f} N -> bearing {sig_brg:5.2f} MPa on a 1 mm wall; torque {M:.2f} N.m -> bond shear {tau_bond:5.2f} MPa over {A_ring:.0f} mm2")
print("   Woven tensile strength is several hundred MPa, forged standard 190 MPa (untested), a structural adhesive about 20 MPa in shear:\n"
      "   the hub loads are one to two orders of magnitude below any of them. Strength does not decide it; impact, stiffness and ease of making do.\n")

# 3. Heat: servo hold losses (my estimate) against the box's convection
STALL_T, STALL_A, V = 2.9, 2.8, 12.0              # STS3215 12 V: about 30 kg.cm, about 2.8 A (spec sheet, rounded)
R = V / STALL_A
I = STALL_A * (M_REV / STALL_T)                   # current for the hold torque if torque ~ current
P = 4 * I * I * R + 4 * 0.1                       # four servos plus 0.1 W idle each (assumed)
H = 7.0                                           # W/m2K natural convection plus radiation, still air
print(f"3. heat: hold current {I:.2f} A per servo, {P:.1f} W for four; box area {AREA_CM2/1e4:.3f} m2 at h = {H} W/m2K -> about {P / (H * AREA_CM2 / 1e4):.1f} K rise if all of it leaves through the walls.")
print("   Through a 1 mm laminate wall of k about 0.5 W/mK (through thickness, typical, not checked) the wall adds only", f"{0.001/0.5*P/(AREA_CM2/1e4):.2f} K. Heat is not a differentiator.\n")

# 4. Ply count for the woven shell
for gsm in (200, 245):
    ply = gsm / 1.8 / 0.5 / 1000                  # mm, fibre 1.8 g/cm3 at 50% fibre volume
    print(f"4. {gsm} gsm twill at 50% fibre volume: {ply:.2f} mm per ply -> 1.0 mm is {1.0/ply:.1f} plies, 1.5 mm is {1.5/ply:.1f} plies")
