"""The lid DESIGN SPACE as a real CAD split of the block (the maximum space the lid may occupy, not a final lid form: topology optimisation, fasteners and the real walls come later): a stepped, flat-faced simplification of the equidistant-surface region of lid_split.py (owner's method, rim rule agreed 2026-11-14).

Run: .venv/bin/python hardware/body/lid_cad.py     (needs the .venv; imports layout.py; writes hardware/body/out/lid.step and body_mid.step)
Top lid: a plate from the lid face down to the rim plane (D_RIM below the face, over the whole 140 x 140 footprint) plus a raised platform under the board (the board's own footprint plus
a margin), to a floor 2 mm below the board's lower face. The bottom lid is the same mirrored about z = 30 (the two are identical, as lid_split.py found). The body between them is the block
(block.py's design volume, here a plain 140 x 140 x 60 box) minus both lids: the cavities of block.py are cut from it as before. Checks: no component overlaps a lid, and the clearances.
"""
import contextlib, io, sys
from pathlib import Path
import numpy as np
from build123d import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
with contextlib.redirect_stdout(io.StringIO()):
    import layout as LY

D_RIM = 7.0                       # lid depth at the rim (lid_split.py's 6.5 mm rule rounds to 7.0 on the 1 mm grid); the end-face cells stop at z = 52.3, so 53 leaves 0.7 mm
board = LY.comps["power board (upper lid module)"][1]        # x0, x1, y0, y1, z0, z1 of the upper board
MARGIN = 2.0                                                              # platform margin round the board
CAM_Z = 38.5                                                              # the cams' axis height on the top lid (the catch's head sits 3.1 to 3.5 mm above it)
EAR_Z0, EAR_Y = 60 - D_RIM - 8.0, (40.0, -40.0)                          # lid ears for the side-entry screws: 8 mm deep below the rim plane, two per hub face at y = +-40 (inboard of the gasket groove)
Z_FLOOR = board[4] - 2.0                                                  # platform floor 2 mm below the board's lower face

def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location(((x0 + x1) / 2, (y0 + y1) / 2, z0)))

def lid_spaces():
    """The top and bottom lid design spaces as build123d solids (the bottom is the top mirrored about z = 30)."""
    plate = box(-70, 70, -70, 70, 60 - D_RIM, 60)
    platform = box(board[0] - MARGIN, board[1] + MARGIN, board[2] - MARGIN, board[3] + MARGIN, Z_FLOOR, 60 - D_RIM)
    ears = [box(sx * 58.0 if sx > 0 else -62.0, sx * 62.0 if sx > 0 else -58.0, y0 - 3.0, y0 + 3.0, EAR_Z0, 60 - D_RIM) for sx in (1, -1) for y0 in EAR_Y]
    top = plate + platform
    for e in ears:
        top = top + e
    return top, top.mirror(Plane.XY.offset(30))


import sys as _s; _s.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent)); import harness as _h; PL = _h.pockets()


def joint_features():
    """The fastening details that the lids' design spaces need (stand-in design, docs/mechanical-spec.md item 8): returns (screw_holes, grooves) as lists of solids for both lids.
    Cam bores (replacing the side-entry screws of the first version, 2026-11-14): along x from each hub face (|x| = 70) inward, with a counterbore for the cam's flange and gasket and a vertical hole for the lid ear's catch (hardware/body/lid_cams.py); four per lid, two per hub face at y = +-40.
    Grooves: a gasket groove 2 mm wide and 0.8 mm deep in the body's rim face, a rectangular loop 3 to 5 mm in from the outer faces, one at each lid joint."""
    holes = []
    for zc, zear in ((CAM_Z, EAR_Z0), (60 - CAM_Z, 60 - EAR_Z0)):                 # the top lid's cams and the bottom lid's (mirror images about z = 30)
        for sx in (1, -1):
            for y0 in EAR_Y:
                bore = Cylinder(5.1, 16.1).rotate(Axis.Y, 90).moved(Location((sx * 62.05, y0, zc)))                       # the cam's bore, x 54 to 70.1
                cbore = Cylinder(6.7, 2.1).rotate(Axis.Y, 90).moved(Location((sx * 69.05, y0, zc)))                        # the counterbore for the cam's flange and its gasket, x 68 to 70.1
                hole = Cylinder(1.7, abs(zear - zc)).moved(Location((sx * 60.0, y0, (zear + zc) / 2)))                      # the catch's hole up to the ear pocket
                holes += [bore, cbore, hole]
    # strut motor wiring inside the body (docs/mechanical-spec.md item 6): from the wall hole's inner end (|x| = 60, y = 0; z = 11 on the lower lid, where the wheel drivers are) a 3.2 mm square channel runs inboard to a connector pocket against the
    # lid platform's side face (|x| = 37), where four spring contacts press horizontally on four pads on that face; the lid lifts straight off and the contacts part. The bottom lid's mirror.
    for zc in (49.0, 60 - 49.0):
        for sx in (1, -1):
            holes.append(Box(18.5, 3.2, 3.2).moved(Location((sx * (43.0 + 18.5 / 2), 0, zc))))                              # the channel, |x| 43 to 61.5 (it overlaps the wall hole's inner end at 60 and now the pocket's last 6 mm, |x| 43 to 49)
            L = PL["+" if sx > 0 else "-"]; holes.append(Box(12.0, L, 3.2).moved(Location((sx * (37.0 + 6.0), -5.0 + L / 2, zc))))        # the connector pocket for the side's spring contacts (harness.py), |x| 37 to 49 (12 mm: Mill-Max 854 horizontal strip, contact_fit.py; it was 6 mm), y from -5 along the platform's face
    grooves = []
    for z0 in (60 - D_RIM - 0.8, D_RIM):
        grooves.append(box(-67, 67, -67, 67, z0, z0 + 0.8) - box(-65, 65, -65, 65, z0 - 0.1, z0 + 0.9))
    return holes, grooves


def main():
    lid_top, lid_bot = lid_spaces()
    full = box(-70, 70, -70, 70, 0, 60)
    body_mid = full - lid_top - lid_bot
    for nm, sh in (("lid", lid_top), ("body_mid", body_mid)):
        print(f"{nm:9s} volume {sh.volume / 1000:6.1f} cm3, solids: {len(sh.solids())}")
    out = Path(__file__).resolve().parent / "out"; out.mkdir(exist_ok=True)
    export_step(lid_top, str(out / "lid.step")); export_step(body_mid, str(out / "body_mid.step"))
    re = import_step(str(out / "lid.step")); print(f"lid.step re-imports as {len(re.solids())} solid, volume {re.volume / 1000:.1f} cm3")
    # component overlap and clearance with the placed components (voxel masks from layout.py)
    X, Y, Z = LY.X, LY.Y, LY.Z
    lid_mask = ((Z >= 60 - D_RIM) | ((np.abs(X - (board[0] + board[1]) / 2) <= (board[1] - board[0]) / 2 + MARGIN) & (Y >= board[2] - MARGIN) & (Y <= board[3] + MARGIN) & (Z >= Z_FLOOR)))
    for sx in (1, -1):
        for y0 in EAR_Y:
            lid_mask = lid_mask | ((np.abs(X - sx * 60.0) <= 2.0) & (np.abs(Y - y0) <= 3.0) & (Z >= EAR_Z0))      # the lid ears (x 58 to 62, y +-3, down to 8 mm below the rim plane)
    lid_mask_bot = lid_mask[:, :, ::-1]
    body_comps = LY.occ.copy()
    for n, m in LY.placed.items():
        if not (n.startswith("power") or n.startswith("processor")):
            body_comps |= m
    ex = LY.END_CELL_X
    body_comps |= (((X >= ex - 43.6) & (X <= ex + 43.6) & (Y >= 68.2) & (Z >= 7.7) & (Z <= 52.3)) | ((X >= -ex - 43.6) & (X <= -ex + 43.6) & (Y <= -68.2) & (Z >= 7.7) & (Z <= 52.3)))
    from scipy.ndimage import distance_transform_edt as edt
    gap = edt(~body_comps, sampling=LY.RES)
    for nm, m in (("top lid", lid_mask), ("bottom lid", lid_mask_bot)):
        print(f"{nm}: overlap with body components {int((m & body_comps).sum())} voxels; nearest body component {gap[m].min():.1f} mm")


if __name__ == "__main__":
    main()
