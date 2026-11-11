"""Isogrid on the strut arm plates: mass saved, weakest cross-section, bending stiffness and thermal conduction.

    .venv/bin/python hardware/drivetrain/isogrid_study.py        (after hardware/body/body.py)

Builds strut A with ISOGRID off and on (hardware/strut/strut.py settings), compares volumes and the metal cross-section along the arm, then estimates what that does to
conduction to the hub, to the weak-axis bending stiffness, and to a simple stress check.  Everything about the loads and the convection is an assumption.
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

RHO = 2.70e-3   # g/mm3, 6061


def slab_areas(shape, xs, thick=1.0):
    """Cross-section area (mm2) of `shape` in slabs perpendicular to the arm (local x), centred at world y = x for an arm along +y at the hub."""
    out = []
    for x in xs:
        slab = Box(300, thick, 300, align=(Align.CENTER, Align.CENTER, Align.CENTER)).moved(Location((0, x, E.HUB_Z)))
        hit = shape & slab
        out.append((hit.volume / thick) if hit else 0.0)
    return out


def main():
    results = {}
    for flag in (False, True):
        S.ISOGRID = flag
        sa = S.strut(S.A_BOSS, S.A_PLATE, S.WHEEL_X[0], +1)
        sb = S.strut(S.B_BOSS, S.B_PLATE, S.WHEEL_X[0], +1)
        results[flag] = (sa, sb)
        print(f"ISOGRID {flag}: strut A {sa.volume * RHO:.1f} g (valid {sa.is_valid}, {len(sa.solids())} solid), strut B {sb.volume * RHO:.1f} g")
    a0, a1 = results[False][0], results[True][0]
    saved = (results[False][0].volume + results[False][1].volume - results[True][0].volume - results[True][1].volume) * RHO
    print(f"mass saved: {saved:.1f} g per hub pair, {2 * saved:.1f} g for four struts ({100 * saved / ((results[False][0].volume + results[False][1].volume) * RHO):.0f} % of strut mass)")
    n = isogrid_count()
    print(f"pockets per plate: {n}")
    xs = [18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58]
    s0, s1 = slab_areas(a0, xs), slab_areas(a1, xs)
    print("arm cross-section (mm2) by distance from the pivot:")
    for x, u, v in zip(xs, s0, s1):
        print(f"   x = {x:2d}: solid {u:5.1f}   isogrid {v:5.1f}   ({100 * v / u:3.0f} %)")
    frac_min = min(v / u for u, v in zip(s0, s1))
    frac_avg = sum(s1) / sum(s0)
    print(f"weakest section keeps {100 * frac_min:.0f} % of the metal, average {100 * frac_avg:.0f} %")

    # conduction along the arm (series of slabs: resistance ~ sum of dx / (k A))
    k = 167.0
    print(f"arm conduction resistance hub to tip over x = 18..58 mm: solid {sum(1e-3*4/(k*a*1e-6) for a in s0):.1f} K/W, isogrid {sum(1e-3*4/(k*a*1e-6) for a in s1):.1f} K/W")
    print("(the pivot through the 12 mm stud, about 8 K/W, is in series; see docs/drivetrain-spec.md)")

    # weak-axis bending: second moment of area about the arm's long axis across the thickness, plate 24 mm wide, 3 mm thick
    w, t, skin, rib_frac = 24.0, S.PLATE_T, S.PLATE_T - S.ISO_DEPTH, 1 - frac_avg
    I_solid = w * t**3 / 12
    # isogrid: skin full width + ribs (fraction of width) full depth; neutral axis shifts, estimate by composite section
    A_skin, A_rib = w * skin, w * rib_frac * S.ISO_DEPTH
    y_skin, y_rib = skin / 2, skin + S.ISO_DEPTH / 2
    yc = (A_skin * y_skin + A_rib * y_rib) / (A_skin + A_rib)
    I_iso = w * skin**3 / 12 + A_skin * (y_skin - yc)**2 + w * rib_frac * S.ISO_DEPTH**3 / 12 + A_rib * (y_rib - yc)**2
    print(f"weak-axis bending (out of the plate plane): I solid {I_solid:.1f} mm4, isogrid {I_iso:.1f} mm4 ({100 * I_iso / I_solid:.0f} %)")
    # stress: 5 N sideways at the tip (an assumed knock, twice the wheel's static load) on a 70 mm cantilever, aluminium yield 240 MPa
    F, M = 5.0, 5.0 * 70
    for name, I, c in (("solid", I_solid, t / 2), ("isogrid", I_iso, max(yc, t - yc))):
        print(f"   {name:8s} sideways 5 N at the tip: {M * c / I:5.1f} MPa (6061-T6 yield about 240 MPa, factor {240 / (M * c / I):4.0f})")
    print("in-plane load (wheel weight 2.45 N at the 70 mm lever): bending about the 24 mm width, about 0.6 MPa: negligible either way")


def isogrid_count():
    S.ISOGRID = True
    p = S.isogrid_pockets()
    return len(p.solids()) if p is not None else 0


if __name__ == "__main__":
    main()
