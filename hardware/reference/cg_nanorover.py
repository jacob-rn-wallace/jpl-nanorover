#!/usr/bin/env python3
"""The nanorover as drawn in JPL's 1998 computer animation (the flight-concept rover), at the size of the real rover, for the operator-console sim.

Run from the repository root:   .venv/bin/python hardware/reference/cg_nanorover.py     writes hardware/reference/out/cg_nanorover.step (mm; z up; the body spans x and y +-70, z 0 to 60; wheels on the ground at z = -32.5 + ...).
Every number is read off frames of the 1998 video (docs/cg-model-spec.md has the frame, the method and the uncertainty); NONE is from a drawing.  Tags: MEAS = measured from frames, EST = estimate, ASM = assumed from the real rover.
Colours as in the animation: black body, blue cells with dark gaps, a tan centre square, a pale-yellow round window, a purple rectangular panel, grey hub nub, black struts, wheels grey with yellow-white-yellow bands.
"""
import math
from pathlib import Path

from build123d import (Align, Box, Color, Compound, Cylinder, Location, Pos, Rot, export_step, import_step)

L = W = 140.0          # MEAS: top face square within 15% (frames 4:36, 4:47, 4:48), taken as the real 140 x 140
H = 60.0               # MEAS: the overlay of a 140 x 140 top with a 60 mm drop fits the body bottom in three frames (40 and 50 are too shallow)
CELLS = 6              # MEAS: 6 x 6 grid on top (4:48, 2:31)
GAP = 1.2              # EST: dark gaps between cells
CENTRE = 30.0          # MEAS: tan centre square about 0.21 of the width
WIN_D, WIN_X, WIN_Z = 42.0, -70 + 0.17 * L, 0.53 * H      # MEAS 4:43: window 0.75 H across, centre 0.17 L from the left end, at 0.53 H from the top (here: from the bottom measured as 1 - that)
PAN = (-70 + 0.32 * L, -70 + 0.66 * L, 0.25 * H, 0.80 * H)     # MEAS 4:43: x0, x1, z0, z1 as fractions of L and H from the top
NUB_D, NUB_L, NUB_Z = 22.0, 14.0, 0.55 * H                  # EST: grey cylinder on the hub face
STRUT_L, STRUT_W, STRUT_T = 70.0, 8.0, 4.0                  # ASM from the real rover (70 mm); the frames agree within 15%
WHEEL_D, WHEEL_W = 65.0, 28.0                               # ASM 65 mm (papers); EST width, 0.43 of the diameter from 4:36
BANDS = (8.0, 12.0, 8.0)                                    # EST: yellow, white, yellow along the cylinder
STANCE = 25.0                                               # degrees below horizontal (ASM, the rover's default)

C_BLACK, C_BLUE, C_TAN = Color(0.05, 0.05, 0.07), Color(0.28, 0.28, 0.80), Color(0.45, 0.42, 0.18)
C_WIN, C_PAN, C_GREY = Color(0.85, 0.85, 0.55), Color(0.42, 0.40, 0.85), Color(0.72, 0.72, 0.75)
C_YEL, C_WHT = Color(0.65, 0.68, 0.05), Color(0.82, 0.82, 0.84)


def lab(s, name, col):
    s.label, s.color = name, col
    return s


def body():
    parts = [lab(Pos(0, 0, H / 2) * Box(L, W, H), "body", C_BLACK)]
    pitch = (L - 2 * 4.0) / CELLS
    cells = None
    for i in range(CELLS):
        for j in range(CELLS):
            if abs(-L / 2 + 4 + (i + .5) * pitch) < CENTRE / 2 and abs(-W / 2 + 4 + (j + .5) * pitch) < CENTRE / 2:
                continue
            c = Pos(-L / 2 + 4 + (i + .5) * pitch, -W / 2 + 4 + (j + .5) * pitch, H + 0.4) * Box(pitch - GAP, pitch - GAP, 0.8)
            cells = c if cells is None else cells + c
    parts.append(lab(cells, "cells", C_BLUE))
    parts.append(lab(Pos(0, 0, H + 0.4) * Box(CENTRE, CENTRE, 0.8), "centre square", C_TAN))
    wall = -W / 2                                                  # the window face is the -y face
    parts.append(lab(Pos(WIN_X, wall - 0.4, H - WIN_Z) * Rot(90, 0, 0) * Cylinder(WIN_D / 2, 0.8), "window", C_WIN))
    x0, x1, z0, z1 = PAN
    parts.append(lab(Pos((x0 + x1) / 2, wall - 0.4, H - (z0 + z1) / 2) * Box(x1 - x0, 0.8, z1 - z0), "panel", C_PAN))
    for s in (1, -1):
        parts.append(lab(Pos(s * (L / 2 + NUB_L / 2), 0, NUB_Z) * Rot(0, 90, 0) * Cylinder(NUB_D / 2, NUB_L), f"nub {'+' if s > 0 else '-'}x", C_GREY))
    return parts


def strut_and_wheel(sx, sy):
    """sx = +-1 (hub face), sy = +-1 (strut points to +y or -y); pivot at the hub face, axle at STRUT_L, STANCE degrees below horizontal."""
    a = math.radians(STANCE)
    piv = (sx * (L / 2 + NUB_L / 2), 0.0, NUB_Z)
    axle = (piv[0], sy * STRUT_L * math.cos(a), piv[2] - STRUT_L * math.sin(a))
    ang = math.degrees(math.atan2(axle[2] - piv[2], axle[1] - piv[1]))
    mid = tuple((p + q) / 2 for p, q in zip(piv, axle))
    s = Pos(*mid) * Rot(ang, 0, 0) * Box(STRUT_T, STRUT_L, STRUT_W)
    s = lab(s, f"strut {sx:+d}{sy:+d}", C_BLACK)
    out = [s]
    x_in = piv[0] + sx * (STRUT_T / 2 + 0.5)
    pos = 0.0                                                       # the wheel spans x_in .. x_in + sx * WHEEL_W, axle along x
    for w, col in zip(BANDS, (C_YEL, C_WHT, C_YEL)):
        out.append(lab(Pos(x_in + sx * (pos + w / 2), axle[1], axle[2]) * Rot(0, 90, 0) * Cylinder(WHEEL_D / 2, w), "band", col))
        pos += w
    out.append(lab(Pos(x_in + sx * (pos + 1.0), axle[1], axle[2]) * Rot(0, 90, 0) * Cylinder(WHEEL_D / 2 - 1.0, 2.0), "wheel end disc", C_GREY))
    return out


def main():
    kids = body()
    for sx in (1, -1):
        for sy in (1, -1):
            kids += strut_and_wheel(sx, sy)
    asm = Compound(children=kids, label="jpl-nanorover (CG, 1998 animation)")
    bb = asm.bounding_box()
    print(f"{len(kids)} solids; {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm; z from {bb.min.Z:.1f} to {bb.max.Z:.1f}")
    out = Path(__file__).resolve().parent / "out"; out.mkdir(exist_ok=True)
    export_step(asm, str(out / "cg_nanorover.step"))
    chk = import_step(out / "cg_nanorover.step")
    print(f"re-imported: {len(chk.solids())} solids, {chk.volume / 1000:.1f} cm3")


if __name__ == "__main__":
    main()
