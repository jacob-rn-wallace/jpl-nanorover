"""Estimate of the lid cam's breakaway torque (the torque that turns a locked cam), against the 0.4 N.m target.   (plain python3; an ESTIMATE, not a measurement)

Run: python3 hardware/body/cam_estimate.py
Why an estimate: purchasing is deferred, so there is no bench test; the project's method (owner, 2026-11-14) is to estimate the value with a stated range, design to the whole range and tag it
as an estimate until a test replaces it. Every input below is ASM (my assumption, from handbook formulas and remembered typical figures) unless marked; the ranges are meant to bracket the truth.
What resists turning a locked cam (the spiral groove is self-locking: slope about 2 degrees against a friction angle of about 8.5, so the lid's gasket spring-back does not turn the cam):
  1. the thread under the cam gasket's squeeze (thread friction + the flange's friction on the gasket + the pitch term),
  2. the prevailing-torque patch on the thread (a nylon patch, the Minifix-type fix),
  3. the spiral groove's friction on the catch head (small: the head carries only the seam gasket's spring-back).
"""
import math

# geometry (SRC: lid_cams.py)
PITCH, R_THREAD = 1.0, 4.65            # M10 x 1.0: pitch; mean thread radius (pitch diameter about 9.35 mm)
A_WASHER = math.pi * (6.5 ** 2 - 5.1 ** 2)      # cam gasket washer's area, mm2: flange radius 6.5, bore 5.1
R_FLANGE_FRIC = 5.8                    # mean radius of the flange's friction on the gasket, mm
T_LOCKED, T_UNLOCKED = 0.8, 1.3        # gasket thickness locked and unlocked, mm (lid_cams.py: squeeze 0.5 mm)
STRAIN = 1 - T_LOCKED / T_UNLOCKED     # compression of the washer when locked: about 38%
# ranges (ASM)
STRESS = (0.5, 2.0)                    # MPa: 50 Shore A silicone at about 38% compression (typical handbook range)
MU_THREAD = (0.10, 0.30)               # thread friction, dry stainless or brass on an insert
MU_GASKET = (0.30, 0.80)               # silicone on a metal flange (rubber friction is high; a lubricated seal is at the low end)
PATCH = (0.30, 1.50)                   # N.m: prevailing torque of a nylon-patch M10 thread, remembered order of magnitude (ISO 2320 and DIN 267-28 give figures per size; to confirm), 0.30 for a small patch
REUSE = 0.6                            # fraction of the patch torque left after several removals (ASM: it wears; supplier data usually shows a drop of a third to a half)
SPIRAL_TORQUE = (0.005, 0.03)          # N.m: friction of the head in the groove under about 5 to 20 N of gasket spring-back at a 3 mm arm and mu 0.1 to 0.3
TARGET = 0.4                           # N.m (owner's snag-resistance target, handover section 20)
HEX_LIMIT = 3.0                        # N.m: what the 4 mm hex socket in stainless can be turned with (ASM, an M5 cap screw socket takes about 6)


def friction_torque(stress, mu_t, mu_g):
    F = stress * A_WASHER                                                  # axial force on the cam from the gasket squeeze, N
    t = F * (PITCH / (2 * math.pi) + mu_t * R_THREAD / math.cos(math.radians(30)) + mu_g * R_FLANGE_FRIC)   # N.mm
    return F, t / 1000.0


F_lo, t_lo = friction_torque(STRESS[0], MU_THREAD[0], MU_GASKET[0])
F_hi, t_hi = friction_torque(STRESS[1], MU_THREAD[1], MU_GASKET[1])
print(f"gasket washer area {A_WASHER:.0f} mm2, compressed {STRAIN * 100:.0f}% when locked")
print(f"axial force on the cam from the gasket: {F_lo:.0f} to {F_hi:.0f} N")
print(f"1. thread + gasket friction alone: {t_lo:.3f} to {t_hi:.3f} N.m  -> the low end is {'BELOW' if t_lo < TARGET else 'above'} the {TARGET} N.m target")
print(f"3. spiral friction: {SPIRAL_TORQUE[0]} to {SPIRAL_TORQUE[1]} N.m")
lo_new = t_lo + SPIRAL_TORQUE[0] + PATCH[0]; hi_new = t_hi + SPIRAL_TORQUE[1] + PATCH[1]
lo_old = t_lo + SPIRAL_TORQUE[0] + PATCH[0] * REUSE
print(f"with a patch ({PATCH[0]} to {PATCH[1]} N.m): breakaway {lo_new:.2f} to {hi_new:.2f} N.m when new; the lowest case after reuse ({REUSE:.0%} of the patch) is {lo_old:.2f} N.m")
print(f"ceiling: {hi_new:.2f} N.m against the hex socket's {HEX_LIMIT} N.m -> {'ok' if hi_new < HEX_LIMIT else 'TOO HIGH'}")
print()
for need in (TARGET,):
    p_min = need - t_lo - SPIRAL_TORQUE[0]
    print(f"to guarantee {need} N.m at the worst corner of the friction ranges, after reuse, the patch must give at least {p_min / REUSE:.2f} N.m when new")
    print(f"  (with the patch at {p_min / REUSE:.2f} to {(p_min / REUSE) + 1.2:.2f} N.m new the ceiling stays {t_hi + SPIRAL_TORQUE[1] + (p_min / REUSE) + 1.2:.2f} N.m or less)")
print("\nREADING: friction alone does not reach 0.4 N.m at its low corner; the patch must be specified at 0.6 N.m or more first-on prevailing torque (0.55 is the computed minimum) (a requirement on the supplier, not a hope), which keeps")
print("the used cam above 0.4 N.m and the new one under about 2.4 N.m. Nothing here is measured. To be measured later: breakaway torque with a torque screwdriver (10 cams, 20 cycles).")
