# Plan: a 3D model of the JPL computer-generated nanorover (2026-11-19)

Owner request: find clear frames of the CG nanorover in the JPL videos and plan a real 3D model of it. This is a reference model of the **animation's** rover (the 1998 video's flight concept), separate from our own interpretation in `hardware/`. Frames are NASA/JPL imagery of unchecked usage terms, so they are **not in this repository**; only timestamps are recorded here. Extracted at full size (640 x 480) in the session scratchpad; copied (owner, 2026-11-19) to `jpl-nanorover-private/analysis/cg-frames/` (private repo, 19 frames and a README).

## Which CG rover? There are two
| | Video | What it shows |
|---|---|---|
| **A, the 1998 flight concept** (the one to model) | 1998 video (`vid1016-91`) | Black box body; blue cell grid on top; round pale-yellow window and a purple/blue rectangular panel on one long face; a grey cylindrical nub on the hub face; thin V-shaped struts; wheels are grey cylinders with two yellow bands and a white band between (banded conductor wheel). Same rover from 4:35 to 5:17, 1:04 to 1:09, 2:30 to 2:49, 3:45 to 4:04 (the wheel unrolling). |
| B, the 1997 CG | 1997 video (`vid1016-90`) | Early rover in space with sawtooth (cleated) wheels, gold-foil body at 3:35 to 3:45; blue-celled body and cleated wheels at 4:49 to 4:52 and 0:53 to 1:03 of the 1998 video; wireframe at 4:00 to 4:48 (a dynamics model, no detail). Low resolution and small in frame. |

Not CG: 6:20 to 6:22 of the 1998 video (blue-backdrop frame with a key for scale, silver ridged cylindrical wheels) looks like a **photograph or composite of a physical model**; use it as a wheel and strut reference, not as a CG source.

## Best frames (video time m:ss; 1998 video unless stated)
| Use | Time | Why |
|---|---|---|
| Front three-quarter, window, vents, wheels, struts | 1:05 to 1:08 | static camera, rover fills frame; but softest (sharpness score 42) |
| Front three-quarter, low | 4:36 | window and nub, wheel bands |
| **Side elevation: window + panel + both struts** | **4:43 to 4:44** | nearly orthographic; best for proportions of body, window, panel, wheel width |
| Opposite end face | 4:46 to 4:47 | tan panel (vent or radiator?) on the end |
| **Top, cell grid** | **4:48** and **2:30 to 2:32** | 4 x 4 cell grid plus a central square (tan); 2:31 is a big close-up (sharpest, score 233) |
| Rear face (electronics) | 2:44 to 2:49 | a two-by-four cell group; a green board labelled "DC-1000" behind a translucent panel |
| Wheel construction | 3:54 to 3:59 | the band unrolls: a yellow band, a white band, a yellow band |
| Underside, hub | 4:54 | body from below with the hub nub |
| Rock climbing, strut motion | 2:35 to 2:42 (small), 3:45 to 3:48 | strut kinematics, not for dimensions |
| Cleated 1997 wheel, large | 4:50 to 4:51 of the **1997** video | sawtooth wheel on its strut |

## What the frames tell us (readable by eye, to be measured)
- Body: a long box, roughly 1.7 : 1 : 0.9 (length : width : height, ESTIMATE from 4:43), unlike our 140 x 140 x 60. The animation is a concept, not a unit.
- Wheels: cylinder diameter about 0.55 of the body length, width about a quarter of the diameter; three bands (yellow, white, yellow).
- Struts: thin and straight, attached low on the hub end; a cylindrical nub sits on the hub axis.
- Cells: 4 x 4 grid on top with a central square patch; a 2 x 4 group on the rear face.
- A round pale-yellow window and a rectangular panel on one long face.

## Plan
1. **Frame set (small).** Extract the table's frames at full size, plus 2 to 3 neighbours each, into `jpl-nanorover-private/analysis/cg-frames/`; a short `README` with timestamps. Done (private repo commit 879565f).
2. **Scale (owner, 2026-11-19: the model is for the sim, so it should be about the size of the actual rover).** Scale the CG so its wheels are the papers' 65 mm diameter, then report the body length that results; if that is far from 140 mm, keep the wheel at 65 mm (the sim's rover wheels) and say so. Record the scale factor and both lengths.
3. **Camera calibration per frame.** The side view (4:43) is close to orthographic; the others are perspective. Recover the camera with the same method as `analysis/photo-measure` (box corners as correspondences; the cell grid and window give vanishing points). Output: body L x W x H, wheel diameter and width, strut length and angle, window and panel positions and sizes, the cell grid pitch.
4. **Block-in.** build123d script `hardware/reference/cg_nanorover.py`: body box, cell tiles, window, panel, nub, struts, banded wheels. Dimensioned from step 3; every number tagged with its frame and uncertainty.
5. **Overlay check.** Render the model from each recovered camera (Blender, same pipeline as `blender_render.py`) and overlay on the frame; iterate until the silhouettes agree to a few pixels.
6. **Texture and finish.** Flat colours matched from the frames (black body, blue cells, yellow and white bands, pale-yellow window). Good enough to read as the animation.
7. **Deliverables.** STEP and a Blender turntable (not the frames); `docs/cg-model-spec.md` with the measured table; a statement in `design-comparison.md` that the CG rover is a third reference beside the silver and black units.

Effort: steps 1 to 2 are small; 3 is the real work (about a session); 4 to 6 about another. Risks: the CG is a 1990s low-poly concept with 640 x 480 compression, so dimensions will carry 5 to 10 percent uncertainty; hidden faces (the underside, the far end) must be inferred or marked as assumed.

## Recommendation
Model **rover A** (the 1998 flight concept): it is the clearest, appears from many angles, and is the rover JPL chose to show as the future vehicle. Use 4:43 (side), 4:48 and 2:31 (top), 4:47 (the end) and 1:05 (front three-quarter) as the calibration set.


## Update (2026-11-19, later)
Steps 2 to 4 done in a first pass: **the CG rover's proportions turned out to match the real nanorover (140 x 140 x 60 body, 65 mm wheels), so no rescale is needed**; the earlier "about 1.7 : 1" reading above was wrong (see `docs/cg-model-spec.md`). The model is `hardware/reference/cg_nanorover.py`. Step 5 (render overlay) remains.
