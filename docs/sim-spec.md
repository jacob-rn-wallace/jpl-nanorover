# Operator-console simulation (vertical slice)

Status as of 2026-11-12. Specification and record for `sim/` (a browser app), modelled on the sibling project maha-rover's simulation (three.js, Vite, TypeScript, GitHub Pages; there with Rapier physics and a CAD-exported model).

## Why (owner, 2026-11-12)
The rover's operator view is a low-fidelity 3D map built from sensor data, with photographs on request at slow-scan speed (`docs/electronics-concept.md`). Nothing can be bought or tested physically (purchasing is deferred), and **the open question is whether driving through that view is fun** (Sojourner's constraints, a light-time delay and no repairs, do not apply here, so the scheme is a game). **The simulation exists to answer that question, so the first goal is a fun test of the operator console, built as a vertical slice**: a complete but crude loop (world, rover, sensors, firmware, radio link, console) rather than a high-fidelity part. Environment (owner's choice, mine to pick): Earth, indoors or outdoors, whichever best tests the question; chosen: **an indoor tabletop arena** (below).

## Decisions
| Item | Choice | Source |
|---|---|---|
| Stack | three.js, Vite, TypeScript, static site; GitHub Pages via `.github/workflows/pages.yml` | as maha-rover (assistant's choice) |
| Physics | none in the slice: a kinematic rover on a height function with rules for steps, holes, slopes and falls (Rapier comes in a later phase, as in maha-rover) | assistant, to reach the fun test quickly |
| Licence | code Apache-2.0 | as maha-rover (owner: "yes, let's do that") |
| Rover model | a box with four wheels (14 x 14 x 6 cm, 6.5 cm wheels); no CAD export yet | `CLAUDE.md` |
| Time | real time by default (the design speed is 40 mm/s), time warp 2, 4, 8 | `docs/drivetrain-spec.md` |

## The arena (my choice, a test of the question)
An indoor tabletop, 1.6 x 1.2 m, lit dimly, with **one sunlit patch** (a window patch: the rover charges there) and nothing else bright, so the stakes in the real rover (battery, solar, the lamp, tipping, edges) are all in play and an outdoor field adds nothing the question needs. The table edge is a drop-off. Obstacles: rocks of 2 to 5 cm (the 6.5 cm wheel climbs about 3.2 cm), a pit 5 cm deep (a trap), a gentle ramp and a steep ramp (34 degrees against a tip-over of 38 degrees from `docs/chassis-simulation.md`), a raised platform. **Objective: photograph three coloured markers**, which the range sensor cannot see: the operator must find them through photographs that cost time, lamp power and radio bandwidth. The markers are reported on the map at the pose the rover believed it had, so dead-reckoning drift shows.

## What the slice simulates
- **Rover truth** (`rover.ts`): pose, steps and slopes, a pit that traps, falling, tipping (the cells work either way up: top and bottom lids are identical), self-righting in 3 s (`docs/chassis-simulation.md`), the battery (500 mAh, 1.85 Wh, ASM), loads from `hardware/body/power_budget.py` (PIC32 and XBee receiving 0.1155 W, four servos holding 1.44 W, wheels 0.4 W, lamp 0.2 W, camera 0.3 W, radio transmit 0.0825 W above receiving at full utilisation; revised 2026-11-13 from an ESP32-class 0.105 W and 0.65 W, see `docs/electronics-concept.md`) and solar charging in the patch (2.5 W, one lit face).
- **Sensors** (`sensors.ts`): an 8 x 8 multizone time-of-flight sensor (VL53L5CX class: 45 x 45 degree field, 63 degrees diagonal; tilted 22 degrees down; range 2 m for the table; noise 3 mm plus 1% of range, ASM), wheel odometry with slip noise and a gyro with bias drift (the "SLAM quality" setting scales them; 0 is perfect), and an inertial tilt sensor. Heights are dead-reckoned from the tilt, not read from the truth.
- **Firmware** (`firmware.ts`): a cyclic executive at 50 Hz (as Sojourner's) with periodic tasks: scan, hazard check, navigation, telemetry. **Hazards are Sojourner's** (`docs/electronics-concept.md`): missing or far-below data (a drop-off), a height jump between adjacent zones above a risk-level threshold (a rock or a hole), and a height spread above a larger threshold (a steep slope); and, while moving, tilt beyond a risk-level limit, stall (contact) and a flat battery. The thresholds (risk 1 to 3) are ASM. Modes: **pilot** (live driving through the model; a safety stop that the operator can override) and **mission** (Sojourner-style: click a waypoint; the rover drives in short segments, stops to scan, turns in place away from hazards, and arcs back to the goal).
- **Link** (`link.ts`): a serial radio of 4.8, 9.6, 38.4, 100 or 250 kbit/s (the XBee 3's air rate). Telemetry (a 140-byte range frame and a pose, 5 Hz, newest frame wins) competes with a photograph (6 KB at 320 x 240, 25 KB at 640 x 480, 64 KB at 1024 x 768, about 0.65 bit per pixel, ASM): **while a photo is transferring, the map updates slow to 1 Hz**. The photo arrives line by line, slow-scan style.
- **Console** (`console.ts`, `main.ts`): the operator's only view: a 3D height map built from the received frames and the estimated pose (hazards coloured), the rover glyph with its pose uncertainty, waypoints, battery and link readouts, a photo panel, and a spectator view of the true world (key G, hidden by default, for development).

## Controls
1 pilot, 2 mission; W A S D drive (pilot); Shift overrides the safety stop; click the map to set a waypoint (mission), Shift-click adds one, C clears; Q and E lower and raise the risk level; P takes a photo (the size buttons choose it); L lamp; F right the rover; V changes the map view; G spectator; [ and ] change the link rate; T time warp; N SLAM quality; Backspace resets.

## Checks (`npm run check`, `sim/tests/sim-check.ts`, no browser)
The sensor against known distances; no false hazards on a flat floor over many noisy frames; a drop-off, a rock and a steep slope each detected; a mission run across the rocks that reaches its goal without falling; the pilot safety stop at the table edge (and the fall without it); telemetry utilisation and photo transfer times against the link rate; the energy balance in and out of the patch.

## Status and findings (2026-11-12)
**Built and checked:** `sim/` runs (`npm run dev`), builds (`npm run build`), and its 21 logic checks pass (`npm run check`). Rendered and inspected in headless Chrome: the map, hazard colours, trail, rover glyph, photo panel (progressive, slow-scan), HUD, log and the spectator view all work. **No person has played it yet; whether it is fun is still unanswered**, and this is the next step.

**Mission autopilot (six random seeds, risk 2, across the rocks):** reaches the sun patch from 6 of 6, in a mean of about 150 s, over about 2.5 m for a 1.4 m straight line.

**Findings from building it that bear on the real rover (mine; the sim's numbers are ASM):**
1. **A low-mounted ranging sensor cannot measure a rock taller than itself.** At 4 cm and tilted steeply, a 5 cm rock was only seen as a smooth ramp of heights and never flagged. **Mount it high on the front face (5.2 cm in the sim; the body is 6 cm), tilted about 22 degrees down** so the top row still reaches the floor; the hazard test must also use the absolute height above the ground, not only the jump between neighbouring zones. This is a layout item for the body (the sensor needs its own window on an end face).
2. **Judge heights against the ground plane under the nose, not the body.** A rover straddling a 3 cm step is nose-down by 12 degrees and sees the flat floor ahead as a wall; a plane fitted to the nearest three rows, with outliers rejected, fixed it. A tilt beyond 17 degrees is not accepted as the body's own (so a steep ramp is not fitted as ground).
3. **A missing return must be located where the floor would have been**, not at the farthest valid return, or one dropout makes a far edge look close; zones that see the void below an edge (valid but very far below) likewise.
4. **Require a hazard in two consecutive frames:** noise alone flagged about 1 frame in 400 on a flat floor at the cautious level.
5. **The forward-looking sensor is blind to its flanks.** After turning to face a goal the rover cut a rock's corner and touched it; Sojourner's answer was contact sensing and an operator-permitted "back up, turn, try again", which the sim has (X toggles it). Straight segments (turn in place, then drive) replaced arcs, which swing the body into corners.
6. **The risk levels got a meaning:** cautious rejects anything near the wheels' limit (2 cm), normal matches what the wheels can climb (3 cm against a 3.2 cm climb limit), bold overshoots (4 cm) and will try rocks the wheels cannot climb.
7. **A photo blinds the map:** at 9.6 kbit/s a 640 x 480 photograph (about 25 KB) takes 28 s and the map drops to one frame a second while it transfers; telemetry alone uses 74% of a 9.6 kbit/s link.
8. **The energy balance:** idling costs about 1.6 W (the servos holding alone are 1.44 W), so the 1.85 Wh battery lasts about 70 minutes and the sunlit patch gives a net 0.9 W (these were 2 W, 55 minutes and 0.5 W before the radio figures were revised); the stakes are real, and the servos' hold current (6 to 60 mA by source) is the largest unknown.

## First play-test and the map problem (2026-11-12, evening)
**Owner's verdict after playing:** "it works pretty well for being a first pass"; **the map was the weak point**: the owner had to rely on the spectator view, "which kinda defeats the purpose". A screenshot (seed 1, drift off, after about 570 s) shows why: a crumpled grey-green floor in which no rock is recognisable, tall orange walls of drop-off spikes around the whole table edge (the x3 height exaggeration), a trail tangled over the whole map, and a spectator thumbnail too small to compare against. **The default dead-reckoning drift is too harsh as well**: with it on, the rover's estimated position is on a different part of the map within minutes, so the owner turned it off to get a map at all.

**Measured (`npm run map`, `tests/map-check.ts`; 3 seeds, a mission to the sun patch; the console's map compared with the true world within 30 cm of the path; run as a measure, not yet a pass/fail check):**

| odometry drift | before: recall / precision | after: recall / precision |
|---|---|---|
| none (x0) | 49% / 72% | 61% / 64% |
| x0.5 | 19% / 38% | 27% / 55% |
| x1 (the default) | 32% / 23% | 47% / 22% |

Recall is the share of truly hazardous cells that the map shows as hazardous; precision is the share of shown hazards that are real. **Findings:** (1) drift is not the main cause: even with a perfect pose the old map showed under half of the real hazards; (2) the cause was how the map was built: each sample overwrote the cell's hazard flag, so a flat-looking sample cleared a rock, and an 8 x 8 frame samples a rock every 4 cm on a 2 cm grid, so rocks were scattered dots; (3) with a perfect pose about half of the false alarms are smear next to real hazards and about half are phantoms far from anything (mostly drop-offs and rocks), which are sensor-analysis false alarms (suspect: the missing-return rule); (4) at full drift the phantoms multiply (433 cells on average), because the same obstacle lands in different places on different passes and the map keeps both.

**Changed in `consoleMap.ts` (uncommitted until this note; now committed):** hazards persist with an evidence score (two hits to show, clear floor lowers it slowly), gaps between hazard samples are filled, and a scan-matching pose correction (`align`) was added. **The scan matching made no clear difference** (the arena is mostly flat floor, which does not constrain a match), so it is not a fix. **Changed in `consoleView.ts` and `main.ts` (rendered but not yet looked at by anyone; the Chrome extension was not connected, so no screenshot was taken):** height exaggeration 3 to 1.5; the floor drawn smoothed (3 x 3 mean) and pale; drop-offs flat orange marks, not walls; rocks red plateaus; a sensor field-of-view cone ahead of the rover; the trail fades with age; G cycles the spectator view off, small, large (half the window height).

**Next (in order):** the owner tests the redraw; the default drift gets much gentler; find where the phantom drop-offs come from; make the pose correction use the rover's own motion. **The owner's larger aim for the next session: the hardware.** See handover section 15.

## Not done (later phases)
Rapier physics and the CAD-exported model (struts that pose and push, wheels with motors), the real strut and wheel torques, the cell model by face, a loop-closure or scan-matching map correction, outdoor terrain, an asteroid-gravity mode, firmware shared with the PIC32 as portable C compiled to WebAssembly. **Everything numeric marked ASM is mine and untested against a real rover.**

## Honest limits
The slice cannot tell whether the physical rover would be fun, only whether this loop is: the speed, the noise, the photo cost and the thresholds are guesses, and a person who knows the arena (a small tabletop) plays differently from a stranger. It is a way to test the idea cheaply, not a prediction.
