# Render jobs (the hand-off between the modelling session and the render session)

**How this works.** Two kinds of Claude Code session share this repository. The **modelling session** (the desktop, an HP EliteDesk with no GPU) changes the CAD and the render scripts, commits and pushes. The **render session** (the owner's MacBook Air, M2, 16 GB) pulls, renders the jobs that are `pending` below, checks the images, marks the jobs `done`, commits and pushes. The render session does not change the models, the scripts or the docs other than this file and the images. If something looks wrong in a render, it records that in the job's row and leaves the fix to the modelling session.

## For the render session: what to do

1. `git pull`. Read this file and `docs/blender-render.md` ("Setup on an Apple Silicon Mac", not yet tried: if a step there fails, note it under "Notes from the render session" below).
2. Make sure Blender 4.5.9 and the two meshes (`hardware/assembly/out/blender/struts.stl`, `wheels.stl`; git-ignored) are in place.
3. Render the pending jobs: `hardware/assembly/render_all.sh` (every job) or `hardware/assembly/render_all.sh R6 R7` (just those). It prints the device and the time of each job.
4. **Look at each image** before committing it (open the PNG): check that nothing is missing, black, blown out or in the wrong place; compare with the "expected" column.
5. In the table, set `Status` to `done YYYY-MM-DD` and put the render time in the `Notes` column; if an image is wrong, leave the job `pending` and say what is wrong.
6. `git add docs/images docs/render-jobs.md && git commit && git push` (the commit message names the jobs, for example "Renders R1 to R7 on the M2 (Metal)").

## For the modelling session: what to do

When a change to the CAD, the layout, the materials or the camera alters what a render shows, set the affected jobs to `pending` (with the reason in `Why`) and add a job here and in `hardware/assembly/render_all.sh` if a new view is needed. Commit and push, then tell the owner the render session has work.

## Jobs

| Id | Image (`docs/images/`) | Settings | Expected | Why (last change) | Status | Notes |
|---|---|---|---|---|---|---|
| R1 | `rover-hero.png` | `VIEW=hero`, 1600x1000, 96 samples | camera end three-quarter view: carbon body, near-black cells, aluminium struts and wheels, the 26 mm window with the lens visible | window redesigned 2026-11-14 (LED ring, lens, sensor; no beamsplitter); LEDs no longer drawn when off | pending | |
| R2 | `rover-rear.png` | `VIEW=rear`, 1600x1000, 96 | the comms end: the square RF window plug | unchanged since 2026-11-13; re-render only to refresh | pending (low priority) | |
| R3 | `rover-top.png` | `VIEW=top`, 1600x1000, 96 | top lid cells, camera end up | unchanged since 2026-11-13 | pending (low priority) | |
| R4 | `rover-detail.png` | `VIEW=detail`, 1500x940, 96 | the camera-end corner: the window with lens, hood, dead-front ring (no visible LED outlines now), sensor patch above the lens, four end-face cells | LED outlines removed (they showed as raised discs) | pending | |
| R5 | `rover-cells.png` | `VIEW=cells`, 1500x940, 96 | raking close-up of the top-lid cells | unchanged since 2026-11-13 | pending (low priority) | |
| R6 | `rover-window.png` | `VIEW=window`, 1500x940, 96 | straight-on close-up: glass, hood, lens, a smooth dark ring with no LED outlines, the small dark sensor patch at the top | LED outlines removed | done 2026-11-14 (desktop, CPU, as a test of `render_all.sh`; the Mac may redo it) | EliteDesk CPU: 457 s. A baseline for the Mac's time. The image shows no LED outlines. |
| R7 | `rover-window-lit.png` | `VIEW=window LED=on SUFFIX=-lit`, 1500x940, 96 | the same view with the seven white LEDs lit (the lamp on during a photograph) | new variant, 2026-11-14 | pending | |

## Notes from the render session

(empty: add dated lines here, for example the install steps that needed changing, the device the script reported, the time per job)
