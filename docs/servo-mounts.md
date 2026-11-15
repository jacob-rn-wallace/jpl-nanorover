# How the four servos are held (gate 2 of the topology optimisation)

Written 2026-11-15. The decision below is mine and is for the owner to confirm. Numbers come from `hardware/body/servo_mounts.py` (needs the venv; also writes `out/servo_mount_plates.step`); the seats are cut in `block.py`. Tags: SRC = from a cited document; ESTIMATE = my arithmetic; ASM = my assumption.

## Decision

**Each servo is screwed to its own mounting plate through the four small holes on its output face; the plate sits in a seat in the shell.** The servo and its plate are one module, assembled on the bench and lowered into the body with the lids off.

**Why not make the plate part of the forged shell** (my first idea, and the one the block's design space suggested): the servo's four screw holes face *outboard*, toward the hub, so the screw heads are on the plate's outboard side, and once the body is closed nothing outboard of the plate is reachable (the hub housing and the wall are there). A screw cannot be driven into the servo from behind a plate that is part of the shell. A separate plate, screwed on the bench, is the way round it. It also makes a servo replaceable by lifting a lid and one module, not by cutting anything.

**Alternatives considered.** (a) *Integral bulkhead* in the shell: the access problem above. (b) *Clamping the servo in its pocket* (straps or foam): nothing positive to hold the output axis to the hub housing, which the gear mesh needs. (c) **One stepped bracket per side that carries both servos and clamps the hub housing tube** (a hub module): the best engineering, because the gear centre distance (23 mm between servo A's pinion and the hollow shaft's gear) would then no longer pass through the shell's stiffness; it needs the hub redesigned (the housing tube and the two plates would have to be one assembly), so **I recommend the per-servo plate now and (c) as a later refinement if the optimiser's hub-bore stiffness target (0.05 mm, `load-cases.md`) is expensive to meet**.

## The mounting holes

**SRC Feetech STS3215 specification A/0 (2020-04-10), page 6** (private repo, `datasheets/`; the drawing is an image, read by eye; the output-face view is stretched about 18% along its length against its width, so each axis is scaled from its own stated dimension, 45.23 and 24.73 mm). **ASM, the main one: the four small holes on the output face (the drawing's callout "B-PA2.0 self-tapping screw" points at them) are the mounting holes; the drawing does not say so.** If they are not, the mount changes (the standard accessory brackets use side holes, which I did not find).

- Pattern: **8.4 and 28.9 mm from the output axis toward the long end, 10.4 mm either side of the centre line** (20.5 x 20.8 mm; reading error about +-0.3 along, +-0.5 across). Distances from the axis 13.4 and 30.7 mm.
- In the body frame (`servo_mounts.py` lists all 16): servo B (+x) at y = 8.4 and 28.9, z = 19.6 and 40.4, on its output face at |x| = 45; servo A (+x) at y = -31.4 and -51.9 (its shaft is at y = -23), |x| = 49.5; the -x side mirrors.
- Screw: 2.0 mm self-tapping into the servo's plastic housing (ASM: pan head 3.8 x 1.2 mm, length about 5 mm).

## Loads and margins

Torque about the output axis goes into the screws as shear, proportional to each screw's distance from the axis (a rigid plate): **39.7 N on the far two screws and 17.3 N on the near two at the 2.9 N.m stall peak** (4.7 and 2.0 N at the 0.34 N.m design hold; 2.3 and 1.0 N at the 0.169 N.m maximum hold). Against an assumed shear capacity of 100 to 240 N for a 2.0 mm self-tapping screw in the plastic (ESTIMATE, no figure given): **margin 2.5 to 6 at stall, 21 to 52 at the design hold.** The plate's bearing at a hole at stall is 12 MPa (6061 aluminium, about 275 MPa yield). The servo's own weight (0.5 N) and the strut's radial loads are not carried by the screws (the hub housing takes those, LC1).

## The plate and its seat

- **Plate:** 1.5 mm 6061 aluminium (ASM), the servo's footprint (45.23 x 24.73 mm), an 11 mm bore round the rotating output boss, four 2.2 mm clearance holes: **4.1 g each, 16 g for four** (counted in `layout.py`, so the body contents are now **456 g, 70 g over the 386 g budget**; the whole-rover centre of mass y moves from -0.13 to -0.30 mm).
- **Seat (cut in `block.py`, group "servo plate seats"):** the footprint plus 0.2 mm all round, 1.7 mm deep from the servo's output face, so the plate's edges bear on the seat walls (the torque reaction: over 100 mm of edge, a few MPa) and its outer face on the seat floor (a shoulder at |x| = face + 1.7: 46.7 for B, 51.2 for A); plus four 4.4 mm pockets 1.4 mm deep for the screw heads, which stand 1.2 mm outboard of the plate.
- **Fit:** the plate and screw heads touch nothing else (0 voxels against the components, the wire channels and the hub parts, all four servos); the pinion A plane is 0.8 mm beyond A's screw heads. The 16 pockets and four seats take 3 cm3 from the body middle (now 559.3 cm3, single solids, lids unchanged).

## What this gives the optimiser

Non-design (fixed) regions: the four seats (floor, walls, head pockets) and the 16 screw positions, plus the servo pockets already there. **The shell around each seat is the load path** for the stall couple (116 to 193 N total at the screws) and must stay bonded to the seat walls; the optimiser sees the plates as given.

## Still open

1. **Retention of the module in the body** (not modelled): the seat holds the plate against torque and the floor holds it against the servo's weight toward the hub, but nothing holds the module *in* (toward the body's centre). My recommendation: two M2 screws per module through ears on the plate's top and bottom edges into inserts in the seat walls (axes along z, reached with a lid off), or a spring finger on the lid. Either adds a boss to the fixed set.
2. **Whether the four small holes are the mounting holes** (the largest assumption): check against a real STS3215 or Feetech's mounting documentation before the plate is drawn for manufacture.
3. The screw capacity (ESTIMATE, a pull-out and shear test on the servo's plastic would replace it: item 12 of `to-be-measured.md`).
4. The plate material and thickness (1.5 mm aluminium is a guess; 1.0 mm would save 1.4 g each; forged carbon is possible but has more thickness to spare).
5. Whether to go to the per-side hub module (alternative (c)) for the gear-mesh tolerance.
