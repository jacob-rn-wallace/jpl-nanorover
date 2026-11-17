#!/usr/bin/env python3
"""The CURRENT design as one STEP assembly (2026-11-17): the carbon body's design block (cavities, wire channels, servo seats), the servo mounting plates, the hub (housings, shafts, bearings, gears, servos),
the four struts with their wire-cover skins, tip caps and M1.6 screws, the wheel drives (motors, spindle tubes, bearings) and the wheels, at the default 25 degree stance.

Run from the repository root, after hardware/body/block.py, hub.py, strut.py and wheel.py (the part STEP files must be current):
    .venv/bin/python hardware/assembly/rover_current.py
Writes hardware/assembly/out/rover_current.step (colour and label per group; millimetres, z up, the body spans x and y +-70, z 0 to 60).  It contains no Hammond geometry, so it is tracked.
Not in it: the lids' solar cells and cams (the block is the body middle and the lids as one solid), the battery, boards, camera and XBee (they are cavities in the block), the optimised structure.
Replaces rover.py (the old Hammond-box assembly) for inspection; rover.py is kept for its mass summary.
"""
from pathlib import Path

from build123d import Color, Compound, export_step, import_step

HERE = Path(__file__).resolve().parent
HW = HERE.parent
OUT = HERE / "out"

GROUPS = [  # (label, file, rgb)
    ("body block (design volume)", HW / "body/out/body_block.step", (0.20, 0.20, 0.22)),
    ("servo mounting plates", HW / "body/out/servo_mount_plates.step", (0.92, 0.93, 0.95)),
    ("hub housings", HW / "hub/out/hub_housing.step", (0.60, 0.62, 0.66)),
    ("hub shafts", HW / "hub/out/hub_shafts.step", (0.25, 0.25, 0.27)),
    ("hub bearings", HW / "hub/out/hub_bearings.step", (0.45, 0.47, 0.50)),
    ("hub gears", HW / "hub/out/hub_gears.step", (0.70, 0.72, 0.76)),
    ("strut servos (STS3215)", HW / "hub/out/strut_servos.step", (0.10, 0.10, 0.12)),
    ("struts (bases)", HW / "strut/out/struts.step", (0.82, 0.84, 0.88)),
    ("strut skins and tip caps", HW / "strut/out/strut_covers.step", (0.72, 0.78, 0.86)),
    ("strut cover screws (M1.6)", HW / "strut/out/strut_cover_screws.step", (0.25, 0.25, 0.27)),
    ("wheel drives (motor, coupler, shaft)", HW / "strut/out/wheel_motors.step", (0.15, 0.15, 0.17)),
    ("spindle tubes", HW / "strut/out/wheel_spindles.step", (0.88, 0.89, 0.91)),
    ("wheel bearings", HW / "strut/out/wheel_bearings.step", (0.45, 0.47, 0.50)),
    ("wheels", HW / "wheel/out/wheels.step", (0.88, 0.89, 0.91)),
]


def main():
    OUT.mkdir(exist_ok=True)
    kids = []
    for label, path, rgb in GROUPS:
        if not path.exists():
            print(f"skipped (missing): {label}: {path}")
            continue
        s = import_step(path)
        solids = s.solids()
        c = Compound(children=list(solids), label=label)
        c.color = Color(*rgb)
        kids.append(c)
        print(f"{label:<40} {len(solids):3d} solids, {s.volume / 1000:8.2f} cm3")
    asm = Compound(children=kids, label="jpl-nanorover (current design)")
    bb = asm.bounding_box()
    print(f"assembly: {bb.size.X:.1f} wide x {bb.size.Y:.1f} long x {bb.size.Z:.1f} high")
    export_step(asm, str(OUT / "rover_current.step"))
    chk = import_step(OUT / "rover_current.step")
    print(f"wrote {OUT / 'rover_current.step'}; re-imported: {len(chk.solids())} solids, volume {chk.volume / 1000:.2f} cm3")


if __name__ == "__main__":
    main()
