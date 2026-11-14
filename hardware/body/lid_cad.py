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
board = LY.comps["power + motor-driver board (upper lid module)"][1]        # x0, x1, y0, y1, z0, z1 of the upper board
MARGIN = 2.0                                                              # platform margin round the board
Z_FLOOR = board[4] - 2.0                                                  # platform floor 2 mm below the board's lower face

def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location(((x0 + x1) / 2, (y0 + y1) / 2, z0)))

def lid_spaces():
    """The top and bottom lid design spaces as build123d solids (the bottom is the top mirrored about z = 30)."""
    plate = box(-70, 70, -70, 70, 60 - D_RIM, 60)
    platform = box(board[0] - MARGIN, board[1] + MARGIN, board[2] - MARGIN, board[3] + MARGIN, Z_FLOOR, 60 - D_RIM)
    top = plate + platform
    return top, top.mirror(Plane.XY.offset(30))


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
