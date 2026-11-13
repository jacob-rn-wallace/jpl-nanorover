# Mechanical details: retention, couplings, seals, cables, stops, lids

Started 2026-11-13, as part of the push to specify the rover's own hardware (`docs/hardware-spec.md`). These are the items that `strut-spec.md`, `drivetrain-spec.md` and `body-redesign.md` list as "not modelled". Every choice here is **mine (recommended, owner has delegated this kind of call), from general engineering practice, not from a source**, and none is checked in CAD yet; sizes marked ASM are assumptions. Where the owner had already decided something, it is quoted.

## 1. Wheel to stub shaft

**Choice:** a D-flat on the 3 mm stub shaft and one M2 x 3 cup-point set screw through the wheel's apex collar onto the flat. The existing collar (`strut-spec.md`, apex boss and collar at |x| = 136.85) gets a tapped M2 radial hole. **Why:** a flat plus a set screw is the standard way to fix a hub to a 3 mm shaft; the wheel torque (at most 0.14 N.m at the wheel for the step case, `drivetrain-spec.md`) is well within what one M2 set screw on a flat holds (ASM, no figure checked). **Add:** a drop of thread-locker; the screw is the wheel's only axial retention, so the wheel also needs the bearing pair's inner faces to bear on a step (the existing 4 mm bearing span already does). **Change if:** the wheel is ever removed often (then a second screw, 90 degrees apart, on a second flat).

## 2. Spindle tube in the strut-tip bore

**Choice:** the 19 mm tube is a slip fit in the 19.1 mm bore, held by a **split clamp**: a slit through the tip's bore wall and one M2 screw across it, plus retaining compound in the bore as a backup. The tube's 1.5 mm outboard cap is its axial stop in one direction, the clamp holds the other. **Why:** `strut-spec.md` already calls for a clamp; a slit-and-screw clamp is the simplest, and the strut is also the motor's heat path, so a tight clamp helps. **Risk:** the clamp loads a thin aluminium tip (a 0.5 to 1 mm wall near the slit, ASM); check in CAD that the tip does not crack at the screw.

## 3. Motor-to-stub coupling

**Choice:** a single aluminium sleeve, 3 mm bore each end, 7.5 mm long (the length the CAD has room for, `drivetrain-spec.md` calls it tight), with one M2 set screw per end, the motor side onto the Pololu's D-flat and the stub side onto a flat. **Why:** it needs no part bought beyond a rod of aluminium, and the load is small. **Fallback if the screws do not fit in 7.5 mm:** bond the sleeve to the stub with retaining compound and use one set screw on the motor side only. **Note:** the Pololu #3068's output is a 3 mm D-shaft (`hardware-spec.md`, section 6), so the motor side is a standard D-flat.

## 4. Dust and seals

**Choice: shielded ball bearings (the "ZZ" type) and a labyrinth step, no rubber seals.** The wheel's collar overlaps the tube's cap by about 1 mm with a 0.2 mm gap (ASM), and the same at the hub housing. **Why:** a rubber lip seal adds friction that the 0.15 N.m wheel budget and the 0.17 N.m strut hold do not want, and the use case is an indoor tabletop (`docs/sim-spec.md`) where dust is not a function requirement. **Not covered:** fine dust that works through a labyrinth over hours; if the rover ever runs on regolith-like material, revisit with lip seals and a stronger servo.

## 5. Hub: adapters and pinions fixed to the servo horns

**Choice:** each horn adapter and pinion is a flanged part **bolted to the servo's supplied metal horn through the horn's own screw holes** (M2, ASM: the horn's pattern and thread are not confirmed), with the horn on the servo's 25-tooth output spline and its centre screw. **Why:** it uses the servo's own spline, so no shaft is broached and the servo output keeps its own backlash rating. **To do:** read the real horn dimensions from the Feetech drawing before the adapter diameters are fixed (the 20 mm horn adapter and the 28 mm housing flange in `hub.py` are placeholders); gear teeth at the 1:1 pair are still plain discs at the pitch circle.

## 6. Wire passage across the strut pivots

Each strut carries one wheel motor, so **two wires per strut, eight across the four pivots**, and the inner strut shaft (5 mm steel) is solid, so a wire cannot run through it.
**Choice:** a **limited-rotation strut with a service loop**: travel stopped at about plus or minus 170 degrees (ASM), and a flat or silicone-insulated two-conductor cable looped once around the strut's hub boss, entering the body through a slot in the hub-face wall with a printed or moulded strain-relief and a dab of sealant. **Why:** slip rings at 19 mm are bulky and the wire count is only 8; the strut does not need continuous rotation (`chassis-simulation.md` poses are within a half turn). **Check in CAD:** the loop's clearance to the wheel and the hub housing (`hardware/hub/hub.py`), and wire fatigue at 170 degrees (ASM: silicone-insulated multistrand is fine for the cycle count of a hobby rover).

## 7. Strut stops

**Choice:** firmware soft limits first (the STS3215 has angle-limit registers, from my memory of the protocol, to confirm in the manual), **plus a hard stop**: a pin in the hub housing and a matching tab on each strut hub, placed so that it stops the strut at the end of its travel before the cable loop is pulled taut. **Why:** the servo electronics are not a safety device, and a rover that flips itself over can command any angle; a hard stop protects the cable and the gear train. **Order of work:** the stop angles follow from the cable and the stances in `chassis-simulation.md` (the self-righting sweep).

## 8. The lids and their screws: a finding, and the recommendation

**Finding:** each lid is almost all cell. The cell pocket is about 134.4 x 133.9 mm in a 140 x 140 mm face (`body-redesign.md`), leaving a **rim of only 2.8 mm (sides) and 3.05 mm (top and bottom)**. An M2 pan head is about 3.8 mm across (ASM), so screws **cannot go through the lid face**, and the rim cannot carry a gasket and a screw boss as well.
**Owner's standing decision (2026-11-12, `body-redesign.md`):** for now the lids are not separate components in the design process; the body is one block of forged carbon, and the lid joint, lid screws and board-to-board link wait until the body is more concrete.
**Recommendation (mine) when the lids come back:** retain each lid by **side-entry screws**: M2 screws going in horizontally through the body wall's outer rim into threaded inserts in the lid's edge, on the two faces that have room (the hub faces have the hub hardware in the middle but free corners; the end faces have the window and the cell pocket, so the hub faces are the better choice), eight per lid or so (ASM, to match the gasket path of about 520 mm); **seal with a flat die-cut silicone gasket, 0.5 mm (ASM), on a flange inside the rim**, dust-tight rather than watertight, to match the tabletop use case. **Alternative:** a bonded lid (not removable), which loses the cell-replacement plan the owner asked for (`body-redesign.md`, item 3 of the cell decisions). I do not recommend it.
**Also needed for the removable lid:** a board-to-board connector at the joint (`body-redesign.md`, "Two lids"), and the cells' wiring through it.

## 9. Still open

- Real horn and housing dimensions (item 5), spindle-tube clamp stress (item 2), the cable and stop geometry (items 6 and 7): all need the CAD in `hardware/hub/` and `hardware/strut/`.
- The lid joint (item 8) waits for the owner's go-ahead on separating the lids.
- Camera and ranging-sensor windows and mounts, and the lamp (`docs/hardware-spec.md`, section 7).
