#!/usr/bin/env python3
"""Export the CAD parts the Blender render needs as STL (millimetres) into hardware/assembly/out/blender/.

Run from the repository root with the venv, after strut.py and wheel.py:
    .venv/bin/python hardware/assembly/blender_export.py
Then render with Blender (installed in ~/tools, see docs/blender-render.md):
    ~/tools/blender-4.5.9-linux-x64/blender -b -P hardware/assembly/blender_render.py
"""
from pathlib import Path

from build123d import export_stl, import_step

HW = Path(__file__).resolve().parents[1]
OUT = HW / "assembly" / "out" / "blender"
OUT.mkdir(parents=True, exist_ok=True)
PARTS = {"struts": HW / "strut/out/struts.step", "wheels": HW / "wheel/out/wheels.step"}
for name, path in PARTS.items():
    export_stl(import_step(path), str(OUT / f"{name}.stl"), tolerance=0.03, angular_tolerance=0.15)
    print("wrote", OUT / f"{name}.stl")
