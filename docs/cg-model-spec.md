# The CG nanorover (1998 animation): measurements and model (2026-11-19)

Plan: `docs/cg-model-plan.md`. Model: `hardware/reference/cg_nanorover.py` (build123d; writes `hardware/reference/out/cg_nanorover.step`, 140 x 140 x 60 mm body, 65 mm wheels, for the sim). Frames (private): `jpl-nanorover-private/analysis/cg-frames/`. Times are in the 1998 video (`vid1016-91`). Tags: MEAS measured from frames, EST estimate, ASM assumed from our real rover.

## Method
1. Segment the blue top face (HSV) in four frames and fit its quadrilateral (4:36, 4:47, 4:48, 1:06).
2. The camera is unknown: solve the focal length from the orthogonality of the top face's two edge directions, per frame (principal point at the image centre). Results: 716, 549, 1190 and 717 px (a 30 to 60 degree field of view); a common f of 750 px (48 degrees) is consistent with three of four.
3. At f = 750 px the top face's edge ratio is **0.99, 1.01 and 1.08** in the frames 4:48, 4:36 and 4:47 (1:06 gives 0.75: its quad is clipped by wheels, discarded). **The top is square within about 10%.**
4. The pose from the top quad (solvePnP, square of 140 mm) predicts where the body's bottom edge falls for a given height; overlaying 40, 50 and 60 mm in three frames, **60 mm fits the dark body's bottom edge**, 40 and 50 are too shallow (overlay image kept in the scratchpad, not committed).
5. Scale: the CG has no scale. Wheels at 65 mm and the body at 140 x 140 x 60 are consistent with the proportions measured (wheel diameter about the body height and a little more because the wheels are nearer the camera in the side view 4:43). **So the CG rover's proportions match the real nanorover's (the papers' figures), and the model needs no rescale: body 140 x 140 x 60, wheels 65 mm.** (My first guess in the plan, a body of 1.7 : 1, was wrong: it came from judging a foreshortened face by eye.)

## Features (positions in fractions of the body, from the side view 4:43 and the top views)
| Feature | Value | Tag |
|---|---|---|
| Cells on top | 6 x 6 grid, dark gaps, a tan centre square about 0.21 of the width (30 mm) | MEAS (4:48, 2:31) |
| Round window | pale yellow, about 0.75 of the body height across (42 mm), centre 0.17 L from one end, at mid-height | MEAS (4:43) |
| Rectangular panel | purple, from 0.32 to 0.66 L along the same face, 0.25 to 0.80 of the height from the top | MEAS (4:43) |
| End faces | grey cylindrical nub on the hub axis, about 22 mm across, 14 mm long; the opposite end shows a tan rectangle (4:47) | EST |
| Struts | thin black bars, length 70 mm; pose at the 25 degree stance | ASM (frames agree within 15%: the strut-to-wheel distance reads about 0.6 L) |
| Wheels | 65 mm cylinders; width 28 mm (0.43 of the diameter) with a yellow, white, yellow banding (8, 12, 8 mm), grey end discs | EST (width and bands), 3:54 to 3:59 |

## Not done
- A rendered overlay of the finished model on the frames (plan step 5): the model is a faithful block-in, not yet verified by render overlay beyond the body.
- The rear-face electronics (2:44), the end-face tan rectangle's size, the nub's position, the strut cross-section and the banded wheel's true width are rough; each carries 15% or more.
- Fine texture and the terrain; colours are approximations of the video's.

## In the sim (2026-11-19)
`hardware/reference/export_cg_glb.py` writes `sim/public/rover_cg.glb` (62 kB) and `rover_cg.json`: rover frame X forward (the window face), Y left, Z up, ground at the wheels' lowest point, glTF axes as `sim/src/worldView.ts`. `WorldView` loads it in place of the placeholder box (the box stays if loading fails). Checked: `npm run check` passes, `vite build` copies the file, and a Cycles render of the GLB shows the model upright with the window forward. **Not checked in a browser** (no Playwright on this machine). The sim's photo camera sits 1 mm ahead of the window face, outside the model's 0.8 mm window and panel relief. The strut and wheel nodes are ready for posing and spinning, which `rover.ts` does not do yet.
