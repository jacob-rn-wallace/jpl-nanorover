#!/usr/bin/env python3
"""Full rover assembly: box, lid plate, O-rings, inserts, hub studs and nuts, struts and wheels.

Run from the repository root, after body.py, strut.py and wheel.py:
    .venv/bin/python hardware/assembly/rover.py

Writes hardware/assembly/out/rover_full.step.  It contains Hammond's casting geometry (through the cut box), so it is
git-ignored, like body_hammond.step.  Prints the size and mass summary of the assembly at the default stance.
Millimetres, Z up, z = 0 at the outside of the box floor.
"""
import sys
from pathlib import Path
from build123d import Compound, export_step, import_step

HERE = Path(__file__).resolve().parent
HW = HERE.parent
OUT = HERE / "out"

PARTS = [  # (label, file, material density g/cm3 as used by the individual scripts)
    ("box (die-cast, cut)", HW / "body/out/body_hammond.step", 2.70),
    ("lid plate with rib", HW / "body/out/lid_plate.step", 2.70),
    ("lid O-ring", HW / "body/out/oring.step", 1.2),
    ("window pane", HW / "body/out/window_pane.step", 2.5),
    ("cover-screw inserts", HW / "body/out/inserts.step", 7.9),
    ("hub studs", HW / "body/out/hub_studs.step", 7.9),
    ("hub O-rings and nuts", HW / "body/out/hub_orings_and_nuts.step", 7.9),
    ("struts", HW / "strut/out/struts.step", 2.70),
    ("wheels", HW / "wheel/out/wheels.step", 2.70),
]


def main():
    OUT.mkdir(exist_ok=True)
    shapes, total = [], 0.0
    for label, path, rho in PARTS:
        if not path.exists():
            sys.exit(f"missing {path}: run hardware/body/body.py, hardware/strut/strut.py and hardware/wheel/wheel.py first")
        s = import_step(path)
        m = s.volume * rho * 1e-3
        total += m
        shapes.append(s)
        print(f"{label:<24} {m:7.0f} g")
    asm = Compound(shapes)
    bb = asm.bounding_box()
    print(f"{'total (no motors, wiring, electronics)':<24} {total:7.0f} g   [MUSES-CN rover: 1300 g]")
    print(f"default stance: {bb.size.X:.1f} wide x {bb.size.Y:.1f} long x {bb.size.Z:.1f} high; body floor {-bb.min.Z:.1f} mm above the wheel bottoms")
    export_step(asm, str(OUT / "rover_full.step"))
    print("wrote", OUT / "rover_full.step")


if __name__ == "__main__":
    main()
