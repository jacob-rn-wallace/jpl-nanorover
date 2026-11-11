"""Clearance of the wheel motor (layout C) against the body and the other strut of the same hub, for several shaft pads.

    .venv/bin/python hardware/drivetrain/motor_clearance.py        (after hardware/body/body.py)

The motor, its size and its position come from hardware/strut/strut.py (S.motor, S.MOTOR_*): 10 mm x 44.9 mm (ECX SPEED 10 M + GPX 10 A 4-stage), output end as far
toward the cone apex as the cone's inner radius allows less MOTOR_PAD.  Reports where the tail ends and tests one strut's motor against the other strut of the same hub at every
pair of angles (30 degree steps; strut.py's own check at the default pad).  The flexprint cable (about 4 mm at the tail) is not modelled.
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
    for pad in (0.0, 3.0, 6.0):
        S.MOTOR_PAD = pad
        S.MOTOR_FRONT = S.WHEEL_X[1] - S.CONE_T - S.CONE_H * (S.MOTOR_D / 2) / S.CONE_R - pad
        S.MOTOR_TAIL = S.MOTOR_FRONT - S.MOTOR_L
        print(f"\nSHAFT_PAD {pad:.0f} mm: motor from |x| = {S.MOTOR_TAIL:.2f} (tail) to {S.MOTOR_FRONT:.2f}; tail is {S.MOTOR_TAIL - face:+.2f} mm from the body face, "
              f"{S.WHEEL_X[0] - S.MOTOR_TAIL:.2f} mm inboard of the wheel's inner face")
        sa = S.strut(S.A_BOSS, S.A_PLATE, S.WHEEL_X[0], +1)
        sb = S.strut(S.B_BOSS, S.B_PLATE, S.WHEEL_X[0], +1)
        m = S.motor(+1)
        bad_a = bad_b = 0
        for a in angles:
            for b in angles:
                h = m.rotate(axis, a) & sb.rotate(axis, b)       # A's motor against B's strut
                bad_a += bool(h and h.volume > 1e-3)
                h = m.rotate(axis, b) & sa.rotate(axis, a)       # B's motor against A's strut
                bad_b += bool(h and h.volume > 1e-3)
        print(f"   A's motor hits strut B at {bad_a} of {len(angles)**2} angle pairs; B's motor hits strut A at {bad_b}")


if __name__ == "__main__":
    main()
