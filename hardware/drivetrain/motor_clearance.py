"""Option C for the wheel motor: the motor and gearhead sit inside the wheel, fixed to the strut tip, with the tail poking inboard.

    .venv/bin/python hardware/drivetrain/motor_clearance.py        (after hardware/body/body.py and hardware/strut/strut.py)

Model: a 10 mm diameter cylinder, 45.0 mm long (ECX SPEED 10 M 25.1 mm + GPX 10 A 4-stage 19.8 mm; maxon catalogue 2025/26),
carried by the strut tip.  Its output (outboard) end is put as far toward the cone apex as the cone's inner radius allows (the cone narrows),
less an assumed SHAFT_PAD mm of shaft and hub, and the tail runs inboard from there.  The flexprint cable (about 4 mm at the tail) is not modelled.
Checks: (1) how far the tail reaches inboard and how much clearance is left to the body face; (2) the motor of one strut against the other
strut of the same hub at every pair of angles (30 degree steps), against the 'stub only' interference found by strut.py.
"""
import math
import sys
from pathlib import Path
from build123d import *

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "strut"))
import body as E  # noqa: E402
import strut as S  # noqa: E402

MOTOR_D, MOTOR_L = 10.0, 45.0
CONE_T, H_CONE, R_ROOT = 0.8, 10.1, 29.75          # thin-walled aluminium wheel (docs/drivetrain-spec.md)
X_APEX = S.WHEEL_X[1]
# cone inner radius = MOTOR_D/2 at this x (the front face cannot go further out than this)
X_FRONT_MAX = X_APEX - CONE_T - H_CONE * (MOTOR_D / 2) / R_ROOT


def motor(x_front, direction):
    m = Cylinder(MOTOR_D / 2, MOTOR_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((S.STRUT_L, 0, 0)))
    m = S.on_axle(m, x_front - MOTOR_L).moved(Location((0, 0, E.HUB_Z)))
    if direction < 0:
        m = m.rotate(Axis((0, 0, E.HUB_Z), (1, 0, 0)), 180)
    return m


def main():
    body = import_step(S.BODY_OUT / "body_hammond.step")
    bb = body.bounding_box()
    face = max(abs(bb.min.X), abs(bb.max.X))
    print(f"body half-width (casting rim) {face:.2f} mm; stud flange face {S.X0:.2f}; strut layers A {S.A_PLATE[0]:.2f}-{S.A_BOSS[1]:.2f}, B {S.B_BOSS[0]:.2f}-{S.B_BOSS[1]:.2f}")
    print(f"wheel {S.WHEEL_X[0]:.2f} to {S.WHEEL_X[1]:.2f} (apex); the cone is {MOTOR_D:.0f} mm wide inside at x = {X_FRONT_MAX:.2f}")
    axis = Axis((0, 0, E.HUB_Z), (1, 0, 0))
    angles = range(0, 360, 30)
    for pad in (0.0, 3.0, 6.0):
        x_front = X_FRONT_MAX - pad
        x_tail = x_front - MOTOR_L
        print(f"\nSHAFT_PAD {pad:.0f} mm: motor from |x| = {x_tail:.2f} (tail) to {x_front:.2f}; tail is {x_tail - face:+.2f} mm from the body face, "
              f"{S.WHEEL_X[0] - x_tail:.2f} mm inboard of the wheel's inner face")
        # strut A (inboard layer) carries a motor; strut B (outboard layer) carries a motor; each against the other's strut
        sa = S.strut(S.A_BOSS, S.A_PLATE, S.WHEEL_X[0], +1)
        sb = S.strut(S.B_BOSS, S.B_PLATE, S.WHEEL_X[0], +1)
        ma, mb = motor(x_front, +1), motor(x_front, +1)
        bad_a = bad_b = 0
        for a in angles:
            for b in angles:
                h = ma.rotate(axis, a) & sb.rotate(axis, b)       # A's motor against B's strut
                if h and h.volume > 1e-3:
                    bad_a += 1
                h = mb.rotate(axis, b) & sa.rotate(axis, a)       # B's motor against A's strut
                if h and h.volume > 1e-3:
                    bad_b += 1
        print(f"   A's motor hits strut B at {bad_a} of {len(angles)**2} angle pairs; B's motor hits strut A at {bad_b} (strut.py: stubs alone hit at 12)")


if __name__ == "__main__":
    main()
