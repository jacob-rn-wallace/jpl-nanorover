#!/usr/bin/env python3
"""Add labels to a structure render: .venv/bin/python hardware/assembly/annotate_structure.py docs/images/structure-n48_m120_p5-iso.png
The label anchors are pixel positions for the 1500 x 1000 iso view of blender_structure.py (read off the picture); they are for that view only."""
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

src = Path(sys.argv[1])
im = Image.open(src).convert("RGB")
d = ImageDraw.Draw(im)
try:
    font = ImageFont.load_default(size=26)
    small = ImageFont.load_default(size=22)
except TypeError:
    font = small = ImageFont.load_default()
# (text, anchor on the picture, text position, colour)
L = [("Optimised structure (orange):\nwebs and ribs the optimiser added", (940, 650), (1040, 790), (255, 140, 30)),
     ("Battery (blue) in its\nthree-walled cradle", (870, 495), (1010, 160), (110, 170, 255)),
     ("Servos (silver) on their\nmounting plates", (800, 420), (560, 120), (225, 228, 235)),
     ("Hub-bore ring and cam bosses\n(fixed, grey)", (520, 590), (40, 760), (225, 228, 235)),
     ("Camera window ring\n(fixed)", (770, 700), (560, 880), (225, 228, 235)),
     ("Lid-seat rim frame (fixed):\nthe lid sits on this", (1120, 440), (1090, 330), (225, 228, 235))]
for text, (ax, ay), (tx, ty), col in L:
    lines = text.split("\n")
    w = max(d.textlength(t, font=small) for t in lines)
    hgt = 28 * len(lines)
    # leader line from the nearest edge of the text block to the anchor
    sx = tx + w / 2; sy = ty + hgt / 2
    d.line([(sx, sy), (ax, ay)], fill=col, width=3)
    d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], outline=col, width=3)
    d.rectangle([tx - 8, ty - 6, tx + w + 8, ty + hgt + 2], fill=(20, 22, 28))
    for i, t in enumerate(lines):
        d.text((tx, ty + 28 * i), t, fill=col, font=small)
mm = re.search(r"n(\d+)_m(\d+)(?:_p(\d))?", src.stem)           # the title from the file name: grid, added mass, penalty
n_, m_, p_ = (mm.group(1), mm.group(2), mm.group(3) or "3") if mm else ("?", "?", "?")
d.text((40, 30), f"Body middle with the optimised structure ({m_} g added, {138 / int(n_):.1f} mm grid, penalty {p_})" if mm else "Body middle with the optimised structure", fill=(255, 255, 255), font=font)
d.text((40, 66), "The 140 x 140 x 60 mm envelope is the thin frame; the lids are not shown; walls and skin are a faint ghost", fill=(200, 205, 215), font=small)
out = src.with_name(src.stem + "-labelled.png")
im.save(out); print("wrote", out)
