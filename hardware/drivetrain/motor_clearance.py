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
    print(f"motor {S.MOTOR_W:.0f} x {S.MOTOR_H:.0f} x {S.MOTOR_L:.0f} mm; each support starts flush with its own plate's inboard face: strut A at |x| = {S.A_PLATE[0]:.2f} "
          f"({S.A_PLATE[0] - face:+.2f} mm from the body face), strut B at {S.B_PLATE[0]:.2f}")
    sa = S.strut(S.A_BOSS, S.A_PLATE, S.WHEEL_X[0], +1)
    sb = S.strut(S.B_BOSS, S.B_PLATE, S.WHEEL_X[0], +1)
    sup_a = S.motor(+1, S.A_PLATE[0]) + S.spindle(+1, S.A_PLATE[0]) + S.bearings(+1)      # A's whole wheel support, which strut A clamps
    sup_b = S.motor(+1, S.B_PLATE[0]) + S.spindle(+1, S.B_PLATE[0]) + S.bearings(+1)      # B's, drawn on a +y arm so it can be rotated like the strut
    bad_a = bad_b = 0
    for a in angles:
        for b in angles:
            h = sup_a.rotate(axis, a) & sb.rotate(axis, b)       # A's wheel support against strut B
            bad_a += bool(h and h.volume > 1e-3)
            h = sup_b.rotate(axis, b) & sa.rotate(axis, a)       # B's wheel support against strut A
            bad_b += bool(h and h.volume > 1e-3)
    print(f"A's wheel support hits strut B at {bad_a} of {len(angles)**2} angle pairs; B's wheel support hits strut A at {bad_b}")
    print("(A's tube lies in B's layer only from B's plate outward, B's starts flush with its own plate: only A's tube reaches into B's layer, and the wheels collide well before.)")


if __name__ == "__main__":
    main()
