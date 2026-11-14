#!/usr/bin/env python3
"""Fit of the lid joint's spring contacts: Mill-Max series 854 horizontal SMT strips in the pocket.   (plain python3)

Run: python3 hardware/body/contact_fit.py
SRC = Mill-Max "Fine Pitch Right Angle & Horizontal SMT Spring-Loaded Connectors" (PR661, 2016) and its datasheet page 18.2 (private repo, datasheets/):
  854-22-0XX-40-001101 (horizontal SMT), 0XX = 02 to 20 positions, .050 in pitch, single row; the piston moves PARALLEL to the board surface; with mounting pegs: 854-22-0XX-40-601101.
  Strip length (N x .050 + .015) in; profile height .087 in (2.21 mm) above the board; piston centreline .0435 in (1.10 mm) above the board; piston .019 in (0.48 mm) diameter;
  side view: piston protrudes .075 in from the body at the initial height, body .172 in deep, tails .183 +- .010 in behind it (overall .430 in from piston tip to tail end);
  stroke .0275 in mid (0.70 mm), .055 in +- .005 max (1.40 mm); spring force 25 g at the initial height, 60 g at mid stroke; 2 A continuous, 3 A peak per contact; contact resistance 20 mOhm max;
  1,000,000 cycles; gold over nickel; footprint: pads .026 wide on .050 pitch, .106 long, tail pads .202 in from the mounting-hole row.
ASM = my assumption.  The force at the other end of the stroke is not given: it is taken as linear between the two datasheet points (ASM).
"""
IN = 25.4
PITCH = 1.27
PIST_FREE, BODY, TAIL = 0.075 * IN, 0.172 * IN, 0.183 * IN         # mm along the piston axis (x in the pocket)
MID, MAXS = 0.0275 * IN, 0.055 * IN
H_PROFILE, H_CENTRE = 0.087 * IN, 0.0435 * IN
F0, F_MID = 25.0, 60.0                                              # grams at the initial height and at mid stroke
G = 9.81e-3                                                         # N per gram

POCKET_Z = 3.2                                                      # mm, the pocket's height (harness.py, lid_cad.py)
BOARD_T = 0.8                                                       # mm, a 0.8 mm board under the strip (ASM; 1.0 mm would not fit)
PAD_PLANE = 37.0                                                    # |x| of the lid platform's side face, where the pads are

print("DEPTH along x from the pad plane (|x| = %.1f), at mid-stroke compression %.2f mm:" % (PAD_PLANE, MID))
prot = PIST_FREE - MID
front = PAD_PLANE + prot
rear = front + BODY
tail = rear + TAIL
print(f"  piston protrudes {prot:.2f} mm beyond the body; body front |x| = {front:.2f}, body rear {rear:.2f}, tail ends {tail:.2f}")
print(f"  overall piston tip to tail end {PIST_FREE + BODY + TAIL:.1f} mm (datasheet .430 in = 10.9 mm); the old pocket was 6 mm deep (|x| 37 to 43): too shallow")
POCKET_X1 = 49.0
print(f"  recommended pocket |x| {PAD_PLANE:.0f} to {POCKET_X1:.0f} = {POCKET_X1 - PAD_PLANE:.0f} mm deep: tail pads end at {tail:.1f}, {POCKET_X1 - tail:.1f} mm left for the wires' solder pads (ASM)")
print(f"  the board tab under the strip: |x| {front:.1f} to {POCKET_X1:.0f} ({POCKET_X1 - front:.1f} mm) carries the body and the tail pads")

print("\nHEIGHT in the pocket (z):")
stack = BOARD_T + H_PROFILE
print(f"  board {BOARD_T} + profile {H_PROFILE:.2f} = {stack:.2f} mm in a {POCKET_Z} mm pocket: slack {POCKET_Z - stack:.2f} mm" + ("" if stack < POCKET_Z else "  DOES NOT FIT"))
print(f"  piston centre {BOARD_T + H_CENTRE:.2f} mm above the pocket floor (pocket middle {POCKET_Z / 2:.2f}): the pads sit {BOARD_T + H_CENTRE - POCKET_Z / 2:+.2f} mm off the pocket's middle")
print(f"  with a 1.0 mm board: {1.0 + H_PROFILE:.2f} mm, over the pocket: the board must be 0.8 mm or thinner")

print("\nLENGTH along y (strip = N x 0.050 in + 0.015 in; harness.py: the largest contact count on any side is 18, so both pockets are 24.6 mm and ONE part, the 18-position strip, serves every pocket; unused positions are left unconnected):")
for n, pocket in ((18, 24.6),):
    ln = n * 0.050 * IN + 0.015 * IN
    print(f"  {n} positions: strip {ln:.1f} mm in a {pocket} mm pocket: slack {pocket - ln:.1f} mm; part 854-22-{n:03d}-40-601101 (with pegs)")

print("\nFORCES and STROKE:")
def force(compress):                                                # grams, linear between 25 g at 0 and 60 g at mid stroke (ASM), extended to max stroke
    return F0 + (F_MID - F0) * compress / MID
for c in (0.2, MID, 1.2):
    print(f"  compression {c:.2f} mm: {force(c):4.0f} g = {force(c) * G:.2f} N per contact")
print(f"  stroke window: 0 to {MAXS:.2f} mm available; nominal {MID:.2f} mm leaves +-0.5 mm for the pad plane and the strip's placement (lid face +-0.2, strip +-0.15, ASM) with margin to both ends")
for side, n in (("+", 18), ("-", 18)):
    print(f"  {side} side, {n} contacts at mid stroke: {n * force(MID) * G:.1f} N pushing the lid platform's side face outward")
net = 0.0
print(f"  the two sides push in opposite directions: net {net:.2f} N along x (the cam catches locate the lid); no vertical force, so the contacts add nothing to the gasket load")
MU = 0.3
print(f"  lifting the lid drags the pistons along the pads: friction at mu = {MU} (ASM): up to {MU * 36 * force(MID) * G:.1f} N in total for 36 contacts, about the weight of a 0.6 kg object: a light extra pull when the lid is lifted off by hand, and it acts only while the lid moves (the sideways forces cancel at rest)")

print("\nCURRENT (contact_estimate.py's worst per-contact figure is 0.58 A): rating 2 A continuous / 3 A peak -> margin x%.1f; contact resistance 20 mOhm max new (datasheet), 10 to 100 mOhm over life used in contact_estimate.py (ASM) stays valid." % (2.0 / 0.58))

print("\nPADS on the lid platform's side face (ASM; the datasheet gives only the contact): 0.9 mm wide on the 1.27 mm pitch (piston 0.48 mm: +-0.2 mm of alignment slack),")
print("  at least 3 mm tall and running up to a chamfered edge so the rounded piston tip rides on as the lid goes down; HARD gold, 30 microinch (0.76 micron) over 100 to 200 microinch nickel (a standard edge-finger finish, remembered, ESTIMATE):")
print("  the pistons slide along the pad on every lid removal, which wipes oxide off but wears soft ENIG gold (2 to 5 microinch) in tens of cycles; the contact itself is rated for a million.")
