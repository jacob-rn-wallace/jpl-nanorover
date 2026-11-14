"""The lid's catch-and-cam fastening (the owner's idea, 2026-11-14): catches on the lid, cams in the body, a Minifix-style joint turned from the hub face.

Run: .venv/bin/python hardware/body/lid_cams.py     (needs the .venv; writes hardware/body/out/cam_joint/*.step, *.stl and prints the interference checks)
One joint, at the top lid's hub face x = +70, y = +40 (two per hub face per lid, eight in all; the bottom lid's are the mirror images about z = 30). It is drawn in two states:
  UNLOCKED: the lid sits on the seam gasket, which is 0.4 mm proud of its groove, and the cam stands 0.5 mm proud of the hub face on its own gasket; the catch's head is at the throat of the
            cam's spiral groove, 3.5 mm from the cam axis.
  LOCKED:   the cam has been turned 180 degrees and has threaded 0.5 mm in (an M8 x 1.0 thread, 0.5 mm of advance per half turn), flush with the face, squeezing its own gasket; the spiral groove
            has drawn the catch's head to 3.1 mm from the axis, pulling the lid down 0.4 mm onto the seam gasket (hard stop at the rim plane).
The groove is a spiral: its centre radius falls from 3.5 mm at the throat to 3.0 mm after 180 degrees (3.1 mm is reached after 144 degrees; the last 36 degrees are a dwell for tolerances), a slope of
about 2 degrees on the groove's mean arc of 11 mm, far under the 8.5 degrees at which a wedge of friction 0.15 stops being self-locking. Thread not modelled (plain cylinders).
Coordinates are the rover's: the hub face is the plane x = 70, y along the body, z up from the floor; the seam plane is z = 53.
"""
import math
from pathlib import Path
from build123d import *

OUT = Path(__file__).resolve().parent / "out" / "cam_joint"
X_FACE, Y0, ZC, SEAM = 70.0, 40.0, 38.5, 53.0
R_CAM, R_BORE, R_FLANGE, R_CBORE = 4.0, 4.1, 5.5, 5.7
X_CATCH = 60.0                                   # the catch's axis (the lid ear is at x 58 to 62)
GROOVE_W, GROOVE_R, HEAD_R, PIN_R = 3.8, 1.5, 1.35, 0.9
R_THROAT, R_END, R_LOCK = 3.5, 3.0, 3.1          # groove centre radius at the throat, at 180 degrees, and where the head sits when locked
STATES = {"unlocked": dict(adv=0.5, alpha=0.0, lid_dz=0.4), "locked": dict(adv=0.0, alpha=180.0, lid_dz=0.0)}


def cylx(r, x0, x1, y=Y0, z=ZC):
    return Cylinder(r, x1 - x0).rotate(Axis.Y, 90).moved(Location(((x0 + x1) / 2, y, z)))


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location(((x0 + x1) / 2, (y0 + y1) / 2, z0)))


def groove():
    """The cam's spiral groove at its own axis (alpha = 0): discs along the spiral from the throat (straight up) through 180 degrees, plus a straight throat out to the cam's surface."""
    g = None
    for i in range(0, 37):
        psi = math.radians(5 * i)
        r = R_THROAT - (R_THROAT - R_END) * psi / math.pi
        d = cylx(GROOVE_R, X_CATCH - GROOVE_W / 2, X_CATCH + GROOVE_W / 2, y=Y0 + r * math.sin(psi), z=ZC + r * math.cos(psi))
        g = d if g is None else g + d
    throat = box(X_CATCH - GROOVE_W / 2, X_CATCH + GROOVE_W / 2, Y0 - GROOVE_R, Y0 + GROOVE_R, ZC + R_THROAT, ZC + 6.0)
    return g + throat


def cam(adv, alpha):
    body = cylx(R_CAM, X_FACE - 15.5, X_FACE - 1.2)
    flange = cylx(R_FLANGE, X_FACE - 1.2, X_FACE)
    c = body + flange
    c = c - groove()
    c = c - box(X_FACE - 1.2, X_FACE + 0.1, Y0 - 0.8, Y0 + 0.8, ZC - 5.0, ZC + 5.0)             # the screwdriver slot across the flange (vertical at alpha = 0)
    c = c - Sphere(0.6).moved(Location((X_FACE, Y0, ZC + 4.7)))                                     # a dimple on the flange at the throat side: shows which way the throat points
    c = c.rotate(Axis((0, Y0, ZC), (1, 0, 0)), -alpha)
    return c.moved(Location((adv, 0, 0)))


def build(state):
    p = STATES[state]; adv, alpha, dz = p["adv"], p["alpha"], p["lid_dz"]
    parts = {}
    # body chunk: the wall region round the joint, with the bore, the counterbore, the catch hole, the ear pocket and the gasket groove
    body = box(44, 70, Y0 - 14, Y0 + 14, 30, SEAM)
    body = body - cylx(R_BORE, 54.0, 70.1) - cylx(R_CBORE, 68.0, 70.1) - Cylinder(2.1, SEAM - ZC).moved(Location((X_CATCH, Y0, ZC + (SEAM - ZC) / 2)))
    body = body - box(57.5, 62.5, Y0 - 3.6, Y0 + 3.6, 44.4, SEAM + 0.1) - box(65.0, 67.0, Y0 - 14.1, Y0 + 14.1, 52.2, SEAM + 0.1)
    parts["body"] = body
    lid = box(44, 70, Y0 - 14, Y0 + 14, SEAM + dz, 60 + dz)
    ear = box(58.0, 62.0, Y0 - 3.0, Y0 + 3.0, 45.0 + dz, SEAM + dz)
    ear = ear - Cylinder(PIN_R, 3.0).moved(Location((X_CATCH, Y0, 45.0 + dz + 1.5)))                # the blind hole for the catch's pin
    parts["lid"] = lid + ear
    r_head = R_THROAT if state == "unlocked" else R_LOCK
    zh = ZC + r_head
    pin = Cylinder(PIN_R, (45.0 + dz + 3.0) - zh).moved(Location((X_CATCH, Y0, (zh + 45.0 + dz + 3.0) / 2)))
    parts["catch"] = pin + Sphere(HEAD_R).moved(Location((X_CATCH, Y0, zh)))
    parts["cam"] = cam(adv, alpha)
    h = 1.2 if state == "unlocked" else 0.8
    parts["seam gasket"] = box(65.0, 67.0, Y0 - 14, Y0 + 14, 52.2, 52.2 + h)
    t = (X_FACE + adv - 1.2) - 68.0                                                                # the washer fills the space from the counterbore's shoulder to the flange
    parts["cam gasket"] = cylx(R_FLANGE, 68.0, 68.0 + t) - cylx(R_BORE, 67.9, 68.1 + t)
    return parts


def overlap(a, b):
    return (a & b).volume


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        parts = build(state)
        print(f"\n{state.upper()}")
        for n, s in parts.items():
            print(f"  {n:12s} {s.volume:9.1f} mm3, solids {len(s.solids())}")
        names = list(parts)
        bad = [(a, b, overlap(parts[a], parts[b])) for i, a in enumerate(names) for b in names[i + 1:] if overlap(parts[a], parts[b]) > 0.5]
        print("  interference between parts (mm3 over 0.5):", bad if bad else "none")
        # the head against the groove wall: the clearance in the locked state (a head grown by 0.1 mm should touch the cam if the clearance is under 0.1 mm)
        grown = Sphere(HEAD_R + 0.20).moved(Location((X_CATCH, Y0, ZC + (R_THROAT if state == 'unlocked' else R_LOCK))))
        print(f"  head grown by 0.2 mm overlaps the cam by {overlap(grown, parts['cam']):.2f} mm3 (0 means at least 0.2 mm of clearance round the head in this state)")
        sections = {"axial": box(40, 75, Y0, Y0 + 20, 25, 65), "radial": box(40, X_CATCH, Y0 - 20, Y0 + 20, 25, 65)}   # axial: the half with y >= 40 (cut through the cam's axis); radial: the half inboard of x = 60 (cut across the cam through the catch)
        for n, s in parts.items():
            export_step(s, str(OUT / f"{state}_{n.replace(' ', '_')}.step"))
            for sec, half in sections.items():
                try:
                    cut = s & half
                    if cut is None or cut.volume < 0.01: continue
                    export_stl(cut, str(OUT / f"{sec}_{state}_{n.replace(' ', '_')}.stl"), tolerance=0.02, angular_tolerance=0.1)
                except Exception:
                    continue                                                  # the part lies wholly outside this half
    print("\nwrote", OUT)
