"""Torque and speed budget for the four-strut drivetrain (first pass, quasi-static).

Pure Python, no CAD needed:  python3 hardware/drivetrain/torque_budget.py

Sourced inputs (papers, see docs/jpl-nanorover-literature.md): strut 70 mm, wheel 65 mm, rolling speed 1.5 mm/s,
256:1 gearheads, two ~10 g brushless motors per strut (one for the strut, one for the wheel).
Design mass: 1.0 kg total (owner decision). The current CAD is heavier (see MASS below).
EVERYTHING ELSE below is an assumption, labelled ASSUMED, and is not the original's.
"""
import math

G_EARTH = 9.81
G_ASTEROID = 1e-4 * G_EARTH      # ASSUMED order of magnitude for a km-scale asteroid (Itokawa surface ~ 1e-5 to 1e-4 g)

MASS = 1.0             # kg, DESIGN MASS (owner, 2026-11-11): total rover incl. motors and electronics, to simplify the budget.
                       # The papers say 1.3 kg; the current CAD (cast box) is ~1.46 kg before motors; the body will be redesigned.
L = 0.070              # m, pivot to axle (papers)
R = 0.0325             # m, wheel radius (papers: 65 mm)
STANCE = math.radians(25)   # arm below horizontal, CAD default (a choice)
V_ROLL = 1.5e-3        # m/s (papers)

# ASSUMED drive hardware: a 10 g brushless micro motor, 0.6 mN.m continuous, 256:1 gearhead at 60 % efficiency
MOTOR_TORQUE = 0.6e-3  # N.m continuous
GEAR, EFF = 256, 0.6
MOTOR_RPM_MAX = 10000  # ASSUMED


def budget(m, g, label):
    W = m * g
    print(f"\n=== {label}: m = {m:.2f} kg, g = {g:.3g} m/s^2, weight = {W:.4g} N ===")
    # 1. Hold the body up at the default stance, weight shared by four wheels.
    #    Wheel contact is directly below the axle; the pivot is L*cos(stance) horizontally from it.
    t_hold = W / 4 * L * math.cos(STANCE)
    # 2. Worst case: arms horizontal.
    t_hold_max = W / 4 * L
    # 3. Standing up / self-righting push: the body's weight on one strut pair, arms horizontal (upper bound).
    t_push = W / 2 * L
    # 4. Wheel torque to climb a 20 degree slope (all four wheels share) and to rise over a step of R/2 (front pair carries all).
    t_slope = W * math.sin(math.radians(20)) * R / 4
    h = R / 2
    t_step = (W / 2) * math.sqrt(R**2 - (R - h)**2)
    # 5. Rolling at 1.5 mm/s.
    w_wheel = V_ROLL / R
    rpm_wheel = w_wheel * 60 / (2 * math.pi)
    print(f"strut, hold at {math.degrees(STANCE):.0f} deg stance : {t_hold*1e3:8.2f} mN.m")
    print(f"strut, hold arms horizontal   : {t_hold_max*1e3:8.2f} mN.m")
    print(f"strut, push on one pair       : {t_push*1e3:8.2f} mN.m   (upper bound for righting/standing)")
    print(f"wheel, 20 deg slope           : {t_slope*1e3:8.2f} mN.m")
    print(f"wheel, R/2 step (front pair)  : {t_step*1e3:8.2f} mN.m")
    print(f"wheel speed at {V_ROLL*1e3:.1f} mm/s      : {rpm_wheel:8.3f} rpm  -> motor {rpm_wheel*GEAR:6.0f} rpm through {GEAR}:1")
    avail = MOTOR_TORQUE * GEAR * EFF
    print(f"ASSUMED motor+gearhead output : {avail*1e3:8.1f} mN.m  (0.6 mN.m x {GEAR} x {EFF})")
    for name, t in [("strut hold", t_hold), ("strut push", t_push), ("wheel slope", t_slope), ("wheel step", t_step)]:
        print(f"  {name:12s} needs {t/avail:5.2f} x the motor  {'OK' if t <= avail else 'SHORT'}")


def sizing(margin=2.0):
    """REQUIREMENT (owner, 2026-11-11): the replica must lift itself under Earth gravity.
    Strut output torque needed (hold / one-pair push) vs total mass, with a design margin."""
    print(f"\n=== Required strut output torque, Earth, margin x{margin:g} (N.m) ===")
    print("mass kg | hold (stance) | push (one pair) | motor torque needed at 256:1, 60 % (mN.m)")
    for m in (0.6, 0.8, 1.0, 1.3, 1.66):
        W = m * G_EARTH
        hold = margin * W / 4 * L * math.cos(STANCE)
        push = margin * W / 2 * L
        print(f"{m:7.2f} | {hold:13.3f} | {push:15.3f} | {push/(GEAR*EFF)*1e3:8.2f}")
    print("(hold/push at the 70 mm strut length from the papers)")


def mass_budget(strut_motor_g, wheel_motor_g=20, wheel_g=78, strut_g=27):
    """Does the 1.0 kg design mass close? wheel_g and strut_g are the CAD/estimate figures (docs/strut-spec.md,
    wheel-spec.md); wheel_motor_g is a catalogue figure (ECX SPEED 10 M 12 g + GPX 10 4-stage 8.2 g); strut_motor_g is a candidate's catalogue mass."""
    drive = 4 * (strut_motor_g + wheel_motor_g + wheel_g + strut_g)
    left = MASS * 1000 - drive
    print(f"strut motor {strut_motor_g:3.0f} g -> drivetrain {drive:4.0f} g, left for body, electronics, cells, camera: {left:4.0f} g")


# maxon catalogue 2025/26, pages 279 (EC-max 16 5 W, 6 V: 283826), 281 (8 W), 417 (GP 16 C), 381 (GPX 16 C), read 2026-11-11.
EC5 = dict(name="EC-max 16 5 W (283826, 6 V)", mass=36, nominal_mNm=3.2, stall_mNm=5.79, kt_mNm_A=3.9, R_ohm=4.04, nom_rpm=5690, length=39.6)
EC8 = dict(name="EC-max 16 8 W (283833, 12 V)", mass=52, nominal_mNm=8.02, stall_mNm=21.1, kt_mNm_A=9.32, R_ohm=5.3, nom_rpm=7300, length=None)
GEARS = [  # name, ratio, efficiency, continuous N.m, intermittent N.m, mass g, gearhead length mm
    ("GP 16 C 3-stage 84:1", 84, .73, 0.40, 0.60, 29, 26.8),
    ("GP 16 C 4-stage 370:1", 370, .65, 0.50, 0.75, 33, 30.4),
    ("GP 16 C 5-stage 1621:1", 1621, .59, 0.60, 0.90, 37, 33.9),
]


def candidates(hold=0.311, push=0.687, motor=EC5):
    """Check each GP 16 C ratio on the motor: gearhead limits, motor torque at the peak, speed, holding loss."""
    print(f"\n=== {motor['name']}, {motor['mass']} g, with a maxon GP 16 C (hold {hold} N.m, push {push} N.m, margin x2 included) ===")
    for name, i, eta, cont, inter, gm, gl in GEARS:
        t_motor_push = push / (i * eta) * 1e3          # mN.m at the motor for the peak push
        t_motor_hold = hold / (i * eta) * 1e3
        amps = t_motor_hold / motor["kt_mNm_A"]
        p_hold = amps**2 * motor["R_ohm"]               # W, copper loss only, per strut
        ok_gear = cont >= hold and inter >= push
        ok_motor = t_motor_push <= motor["stall_mNm"] and t_motor_hold <= motor["nominal_mNm"]
        rpm = motor["nom_rpm"] / i
        print(f"{name:24s} {motor['mass']+gm:3d} g  gearhead {'ok ' if ok_gear else 'NO '}"
              f"(cont {cont}, int {inter})  motor at push {t_motor_push:5.2f} mN.m {'ok ' if ok_motor else 'NO '}"
              f" out {rpm:5.1f} rpm  hold {p_hold:4.2f} W/strut ({4*p_hold:4.2f} W for four)")


def shaft_stress(torque=0.69, d=6e-3):
    """Shear stress in a solid steel shaft: tau = 16 T / (pi d^3), MPa."""
    return 16 * torque / (math.pi * d**3) / 1e6


if __name__ == "__main__":
    sizing()
    print()
    for g in (96, 60, 40, 25):
        mass_budget(g)
    candidates()
    print("\nMass with the chosen candidate (73 g, EC-max 16 5 W + GP 16 C 5-stage 1621:1):")
    for wg in (78, 45, 23):
        mass_budget(73, wheel_g=wg)
    print("(wheel_g 78 = CAD as modelled, 45 = thin-walled aluminium, 23 = printed PA12; see wheel_mass.py)")
    print(f"\n6 mm shaft at 0.69 N.m: {shaft_stress():.1f} MPa shear (steel yields ~ 300 MPa+): the shafts are not the constraint")
    budget(MASS, G_EARTH, "Earth (the replica on a table)")
    budget(1.3, G_ASTEROID, "Asteroid (the original's job)")
