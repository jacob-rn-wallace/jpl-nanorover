"""Compare drivetrain layouts: mass, motor count, shafts per hub, and whether the stance can change by rolling.  Pure Python.

    python3 hardware/drivetrain/layouts.py

Catalogue figures (maxon 2025/26, read 2026-11-11): EC-max 16 5 W 36 g, motor body 24 mm (the overall-length table minus the gearhead length);
GP 16 C 4-stage 370:1 33 g, 0.50 / 0.75 N.m, 65 %; GPX 16 C 3-stage 27 g, 0.47 / 0.58 N.m; ECX SPEED 10 M 12 g with GPX 10 4-stage 8.2 g (0.15 / 0.20 N.m).
EVERYTHING called ASSUMED is my estimate: pulley, belt, bearing and friction-disc masses, the friction coefficient, the 0.35 N.m friction torque.
"""
import math

G = 9.81
M, L, R = 1.0, 0.070, 0.0325                 # kg design mass, strut length, wheel radius
W = M * G
ALPHA = math.radians(25)                     # default stance (a choice)
MU = 0.6                                     # ASSUMED wheel-ground friction coefficient while scrubbing

STRUTS_G, WHEELS_G = 4 * 27, 4 * 45          # struts (estimate), thin-walled aluminium wheels (wheel_mass.py)
STRUT_MOTOR_G = 73                           # EC-max 16 5 W + GP 16 C 5-stage 1621:1
WHEEL_MOTOR_G = 20.2                         # ECX SPEED 10 M + GPX 10 4-stage
BIG_MOTOR_G = 36 + 33                        # EC-max 16 5 W + GP 16 C 4-stage 370:1 (69 g, 54.4 mm long, 0.50 / 0.75 N.m)
SIDE_DRIVE_G = 36 + 27                       # EC-max 16 5 W + GPX 16 C 3-stage (63 g, 0.47 N.m): one motor driving two wheels
BELT_SET_G = 11                              # ASSUMED per wheel: tip pulley, hub pulley, belt, small bearings
IDLER_SIDE_G = 24                            # ASSUMED per side: idler, two tip pulleys, two belts, bearings
FRICTION_SIDE_G = 30                         # ASSUMED per side for JPL's friction layout: idler, pulleys, belts, wafers and springs

W_PER_WHEEL = W / 4
H = L * math.sin(ALPHA) + R                  # hub height above the ground at the default stance
SCRUB = MU * W_PER_WHEEL * H                 # N.m about the hub if a wheel has to slide instead of roll
HOLD = 2 * W / 4 * L                         # strut torque with the arms horizontal, margin x2 (0.34 N.m)
PUSH = W / 2 * L                             # one-pair push, no margin (0.34 N.m)

LAYOUTS = [
    # name, motors, drivetrain grams, coaxial shafts per hub, independent wheel rolling?, strut pose held by
    ("C   wheel motors in the wheels, strut motors in the body", "4 + 4",
     STRUTS_G + WHEELS_G + 4 * STRUT_MOTOR_G + 4 * WHEEL_MOTOR_G, 2, "yes", "strut motors (0.03 W each)"),
    ("2a  all motors in the body, one belt per wheel", "4 + 4",
     STRUTS_G + WHEELS_G + 4 * STRUT_MOTOR_G + 4 * WHEEL_MOTOR_G + 4 * BELT_SET_G, 4, "yes", "strut motors (0.03 W each)"),
    ("2b  one drive motor per side, shared idler (JPL belts)", "4 + 2",
     STRUTS_G + WHEELS_G + 4 * STRUT_MOTOR_G + 2 * SIDE_DRIVE_G + 2 * IDLER_SIDE_G, 3, "NO", "strut motors (0.03 W each)"),
    ("3   JPL friction pivots, tip motors, shared idler", "4",
     STRUTS_G + WHEELS_G + 4 * BIG_MOTOR_G + 2 * FRICTION_SIDE_G, 3, "NO", "friction discs (free)"),
]

if __name__ == "__main__":
    print(f"hub height {H*1e3:.0f} mm; scrub torque if a wheel must slide: mu {MU} x {W_PER_WHEEL:.2f} N x {H*1e3:.0f} mm = {SCRUB:.3f} N.m per strut (ASSUMED mu)")
    print(f"load torques: hold, arms horizontal, margin x2 = {HOLD:.2f} N.m; one-pair push = {PUSH:.2f} N.m\n")
    print(f"{'layout':60s} {'motors':>6s} {'drivetrain':>10s} {'left of 1 kg':>12s} {'shafts':>6s} {'roll apart':>10s}")
    for name, n, g, sh, roll, held in LAYOUTS:
        print(f"{name:60s} {n:>6s} {g:8.0f} g {1000 - g:10.0f} g {sh:6d} {roll:>10s}   pose held by {held}")
    # Layout 3: pose change torque = friction T + lifting load (+ scrub because the wheels cannot roll)
    T = 0.35
    need = T + PUSH + SCRUB
    print(f"\nLayout 3: friction torque T = {T} N.m (holds {T/ (HOLD/2):.1f} x the worst static load).")
    print(f"  lifting with a scrubbing wheel needs T + push + scrub = {T} + {PUSH:.2f} + {SCRUB:.2f} = {need:.2f} N.m "
          f"against the gearhead's 0.75 N.m intermittent: {'OK' if need <= 0.75 else 'SHORT by %.0f %%' % (100 * (need / 0.75 - 1))}")
    print(f"  without the scrub (wheels free to roll): {T + PUSH:.2f} N.m: {'OK' if T + PUSH <= 0.75 else 'SHORT'}")
    drive = 0.138                      # wheel torque at the half-wheel-radius step (torque_budget.py, no margin)
    static = HOLD / 2                  # worst static load on a strut, arms horizontal, no margin
    print(f"  driving at the step load ({drive} N.m) reacts on the strut; it must not slip the pivot: needs {drive} < T - static load = {T - static:.2f}: "
          f"{'OK' if drive < T - static else 'NO'}")
