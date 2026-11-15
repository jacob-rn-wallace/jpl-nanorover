# Load cases and constraints for the body's topology optimisation

Written 2026-11-15, the first of the two gates before step 5 of the owner's body process (`docs/body-redesign.md`, "How ready is the body for topology optimisation?"). The numbers are computed by `hardware/body/load_cases.py` (plain python3) so they can be checked and changed. **Tags:** SRC = from a cited document in this repository; ESTIMATE = my arithmetic from stated inputs; ASM = my assumption; **OWNER** = a choice for the owner to make or confirm. Nothing here was measured (purchasing is deferred; method of 2026-11-14 in `CLAUDE.md`).

## What the optimiser is asked to do

**Objective (proposed).** Minimise a weighted sum of the compliances of the operating cases (LC1, LC2, LC6) **for a sweep of added structure** (0, 10, 20, 40 and 80 g above the 1.5 mm skin), and report mass against stiffness, strength factor and hub-bore deflection for each. This follows the owner's rule that mass is not a decision input until the optimisation has run: the sweep gives the curve and the owner picks the mass. **Strength constraint:** with the impact cases LC3 to LC5 as separate static solves, the peak stress at most the allowable divided by 2 (a safety factor of 2, ASM).

**Design space.** The solid block with the cavities cut out (`block.py`: the body middle 562.6 cm3 and the two lids 136.8 and 136.7 cm3, all single solids). **The 1.5 mm outer skin is a non-design region** (it is the 164 g of "shell" in the budget; the optimiser adds structure behind it). The two lids stay identical (owner, 2026-11-11, symmetry about z = 30); the interior is mirrored about z = 30.

**Material (SRC `body-redesign.md`).** Forged carbon, treated as isotropic: density 1.55 g/cm3 (the project's figure; sources give 1.5); **E = 35.5 GPa** (Easy Composites flexural modulus, the lower of the two sources); **allowable 113.7 MPa** (Rock West's tensile figure, the lower of the two; Easy Composites gives 192 MPa; both untested, Rock West's from models); Poisson's ratio 0.3 (ASM). The whole set of numbers is ESTIMATE-grade until a coupon is tested.

**Mass used for the loads:** 1.054 kg (the real contents, 439.7 g, plus the 614 g drivetrain), the conservative figure; the 1.0 kg design mass gives 5% less.

## The load cases

Weight at 1.054 kg is 10.3 N. Loads act on the non-design regions named in the third column (the hub bores, the servo mounts, the lid seat, the outer skin).

| Id | Case | Magnitude | Applied to | Source / status |
|---|---|---|---|---|
| **LC1** | **Static, any stance** (the rover at rest on one or two features; the worst case is the whole weight on one wheel, shared by the two sides) | 5.2 N on one wheel per side; the hub housing's two bearing pairs see **outer 10 N, inner 5 N (strut A) and outer 16 N, inner 11 N (strut B)**, the inner one opposite in sign (lever arms 1.9 and 3.1 times the load) | the hub bores (the housing flange and its bonded ring at |x| 60 to 72) | ESTIMATE from `chassis_sim.py` and the bearing positions in `hub.py` |
| **LC2** | **Servo torque on its mounts** | **0.17 N.m maximum hold** (0.34 with margin 2) up to the **2.9 N.m stall peak**, which caps what a strut impact can push into the mounts; as tangential reaction at the four screws: **7 to 11 N total at the hold, 14 to 23 N at the design hold, 116 to 193 N at stall (29 to 48 N per screw)** | the four servos' screw bosses (not yet defined: gate 2) | SRC Feetech (0.98 rated, 2.9 peak) and `chassis-simulation.md`; the screw pattern measured from the drawing 2026-11-15 (`servo-mounts.md`: 20.5 x 20.8 mm, 13.4 and 30.7 mm from the axis): **39.7 N on the far two screws and 17.3 N on the near two at stall**; that the four small output-face holes are the mounting holes is ASM |
| **LC3** | **Drop onto the wheels** | **OWNER to choose the height.** Proposed: **0.3 m (a table) with no yield, and 0.6 m with no fracture.** Energy method, stopping in 3 mm through the wheel, strut and bearings: about **100 g, 1.0 kN in all, 260 N per wheel, 800 N on strut B's outer bearing** (0.3 m); 200 g, 2.1 kN, 520 N per wheel, 1.6 kN (0.6 m). With a stop of 2 to 10 mm the 0.3 m case spans 1.6 kN to 0.3 kN | the hub bores, through the strut and bearing path (the radial component only; the tangential is capped by the servo stall: 41 N at the tip) | ESTIMATE; the stopping distance is the soft spot (a thin-walled aluminium wheel's crush is a guess) |
| **LC4** | **Righting roll** (the body falls on a corner when a strut move rolls it; the centre of mass drops up to 30 mm) | 0.31 J, stopped in 1 mm of corner: **310 N at a body corner** (155 to 620 N for 2 to 0.5 mm) | the outer skin at each of the eight corners, directed through the corner | ESTIMATE from `chassis_sim.py` |
| **LC5** | **Lid clamp** (per lid, four cams) | cam gasket washer 26 to 102 N axial per cam (SRC `cam_estimate.py`); **seam gasket reaction up to 530 to 2100 N per lid, 130 to 530 N through each catch** (a flat gasket, loop 528 mm x 2 mm, at 0.5 to 2.0 MPa: the upper bound, a 1 mm cord gives less); the spring contacts push 10.6 N on each side face, equal and opposite, plus 6.4 N of friction when a lid is lifted | the lid seat (rim plane, gasket groove) and the four cam bores in the hub faces (|x| 54 to 70), with the catch ears on the lid | the gasket stress range is the project's silicone handbook assumption (ESTIMATE); **the seam gasket was not estimated before and is about five times the washer's load**: see Findings |
| **LC6** | **Handling** | **30 N squeezed across the two hub faces**, or 30 N point loads on the end faces (the struts and wheels out of the load path) | the hub faces and the end skins | ASM, **OWNER to confirm** |

Combination (ASM): LC1 + LC2 at the design hold is the operating case; LC3, LC4, LC5 are checked alone and with LC1.

## Constraints

- **Mouldability (SRC `body-redesign.md`):** forged carbon pressed in a metal mould: minimum wall and rib 1.5 mm, draft at least 1 degree, fillets at least 1 mm (ASM for the last two); enclosed cavities cannot be cored out of a pressed part, so **a draw direction or a core plan is part of the optimisation** (gate 5d; the hub bores along x and the wire holes are undercuts).
- **Fixed (non-design) regions:** the outer envelope and skin; the cell faces and pockets (cell_pocket.py, cell_endface.py); the lid seat and gasket groove; the hub bores and their bonded rings; the window and its moulded boss ring with six inserts; the four servo pockets and plug zones; the battery, board and component cavities; the 11 wire channels and the contact pockets (all in `block.py`); the catch ears and cam bores.
- **Stiffness (ESTIMATE-grade targets, to be revisited):** (i) the hub bore's displacement under LC1 + LC2 at most **0.05 mm** (gear centre distances and bearing alignment; ASM, from the 0.1 mm backlash the hub design allows); (ii) the lid seat's flatness along the gasket under LC5 at most **0.1 mm** (so the gasket line keeps its squeeze: ASM); (iii) **the cell faces: out-of-plane deflection under LC6's 30 N at most 0.2 mm (ASM), the real limit being the cells' bend tolerance, which is not looked up** (the IXOLAR parts are brittle silicon bonded flush).
- **Symmetry:** mirror about z = 30 (owner), lids identical; no symmetry required about x or y.

## Findings

1. **Strength is not the problem; stiffness and the concentrated cases are.** The static bearing reaction (16 N on about 84 mm2 of flange) is 0.2 MPa, 600 times inside the 113.7 MPa allowable; even the 0.3 m drop's 800 N is 9.5 MPa, 12 times inside. So the optimiser will mostly return thin structure; the result will be set by the constraints above, as `body-redesign.md` predicted.
2. **The lid seam gasket is the largest load in the set and was never estimated.** `cam_estimate.py` took only each cam's own washer (51 mm2, 26 to 102 N). The seam gasket (a 2 mm wide flat gasket round a 528 mm loop, the upper bound) at the handbook range gives 530 to 2100 N per lid, 130 to 530 N through each catch: about five times more. **Through each catch (130 to 530 N) the head's contact on the cam's rails is small**: the 2.1 mm head overlaps the 1.5 mm slit's edges by 0.3 mm each side, so with an assumed 1.5 mm chord the bearing area is about 0.9 mm2 and the contact stress is about **150 to 590 MPa** (crude ESTIMATE; more than a thin aluminium rail takes at the top of the range, and a hardened steel cam would be needed). **Before the optimisation relies on LC5, the cam design should be checked against this** (a softer 30 to 40 Shore A gasket or a narrower bead cuts it. **The model assumes a flat gasket 2 mm wide (the groove's width): the upper bound; the design allows "a flat silicone gasket or a 1 mm cord" in the groove (`mechanical-spec.md`), and a round cord's contact is narrower, so its reaction is lower; the design's 0.4 mm squeeze is about 33% of a 1.2 mm gasket.** This is the one case where my arithmetic suggests a design change, not just an input.
3. **LC3's drop height is the biggest free choice** (an order of magnitude between 0.3 m on a 10 mm stop and 0.6 m on a 2 mm stop) and it is the owner's.
4. **Servo stall caps the strut impact path**: whatever the drop, the gear train gives way before the mounts see more than 2.9 N.m (116 to 193 N total at the screws). The radial component goes to the bearings, not the gears.

## Open choices for the owner

1. **LC3: the drop height** (proposed 0.3 m no yield, 0.6 m no fracture).
2. **LC6: the handling load** (proposed 30 N).
3. **The seam gasket**: hardness and bead size, which fix LC5 (finding 2).
4. Whether to design to the real 1.054 kg (proposed) or the 1.0 kg design mass.

## Not covered

Thermal loads (the cells and the sun; the lamp's few kelvin), fatigue (the lid's 20-cycle life and the righting rolls), a pressure difference across the sealed seam, vibration and launch loads (spaceflight is out of scope), and the real stiffness of the thin-walled wheels (LC3's stopping distance). The optimisation also needs the servo mounts defined (gate 2), the non-design regions assembled into one set, a draw direction and a solver; see `body-redesign.md`.
