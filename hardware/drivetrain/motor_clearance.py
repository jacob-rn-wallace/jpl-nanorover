"""Clearance of the wheel drive (layout C: Pololu #3068, spindle tube, bearings, stub shaft) against the body and the other strut of the same hub.

    .venv/bin/python hardware/drivetrain/motor_clearance.py        (after hardware/body/body.py)

The motor, its size and its position come from hardware/strut/strut.py (S.motor, S.MOTOR_*): a 10 x 12 x 25 mm box with its tail at |x| = S.MOTOR_TAIL (the inboard
face of strut A's plate) and a placeholder 3 mm output rod to the wheel collar.  Reports how far the tail is from the body face and tests one strut's motor against the
other strut of the same hub at every pair of angles (30 degree steps).
"""
import sys
from pathlib import Path
from build123d import *

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "strut"))
import body as E  # noqa: E402
import strut as S  # noqa: E402


def main():
    body = import_step(S.BODY_OUT / "body_hammond.step")
    bb = body.bounding_box()
    face = max(abs(bb.min.X), abs(bb.max.X))
    axis = Axis((0, 0, E.HUB_Z), (1, 0, 0))
    angles = range(0, 360, 30)
    print(f"body half-width (casting rim) {face:.2f} mm; wheel {S.WHEEL_X[0]:.2f} to {S.WHEEL_X[1]:.2f}")
    print(f"motor {S.MOTOR_W:.0f} x {S.MOTOR_H:.0f} x {S.MOTOR_L:.0f} mm from |x| = {S.MOTOR_TAIL:.2f} to {S.MOTOR_FRONT:.2f}; tail is {S.MOTOR_TAIL - face:+.2f} mm from the body face, "
          f"{S.WHEEL_X[0] - S.MOTOR_TAIL:.2f} mm inboard of the wheel's inner face")
    sa = S.strut(S.A_BOSS, S.A_PLATE, S.WHEEL_X[0], +1)
    sb = S.strut(S.B_BOSS, S.B_PLATE, S.WHEEL_X[0], +1)
    m = S.motor(+1) + S.spindle(+1) + S.bearings(+1)      # the whole wheel support, which the strut clamps
    bad_a = bad_b = 0
    for a in angles:
        for b in angles:
            h = m.rotate(axis, a) & sb.rotate(axis, b)       # A's motor against B's strut
            bad_a += bool(h and h.volume > 1e-3)
            h = m.rotate(axis, b) & sa.rotate(axis, a)       # B's motor against A's strut
            bad_b += bool(h and h.volume > 1e-3)
    print(f"A's wheel support hits strut B at {bad_a} of {len(angles)**2} angle pairs; B's wheel support hits strut A at {bad_b}")
    print("(B's spindle tube lies in strut A's layer, so it meets strut A when the two point within about 20 degrees of each other; the wheels collide well before that.)")


if __name__ == "__main__":
    main()
