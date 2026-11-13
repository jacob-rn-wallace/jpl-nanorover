# Absolute positioning and lower drift (research, 2026-11-13)

Question from handover section 15: can the rover anchor its pose (a landmark or beacon), or else get the drift down "as much as humanly possible"? Rules in force: parts selection follows the era spirit (no Linux board, PIC32 the single controller, serial radio), the rover stays a teleoperated rover with a camera, and the volume is a 140 x 140 x 60 mm carbon body whose lids and end faces are already allocated (cells, window, antenna).

**Status of the numbers:** the sim findings in section 1 were measured in this repo. Everything in sections 2 to 4 about real parts is **from memory and unchecked** (assumption until a datasheet is read); each is marked with what to check.

## 1. What actually dominates the sim's drift (measured)

Read `sim/src/sensors.ts` (`Odometry`) and ran `tests/map-check.ts` with the quality factor q set directly.

- **Heading is the only drift term that matters.** The gyro bias is drawn at sd 0.003 q rad/s (0.17 deg/s at q = 1, so about 10 deg per minute) plus a random walk. The distance noise is white per step (2% q) with no systematic scale or slip error, so it averages out. At 1 deg of heading error the position is 1.7 cm off per metre driven.
- **q = 1 is an uncalibrated cheap gyro.** A MEMS gyro zeroed at rest and then holding 0.01 to 0.05 deg/s (from memory; check the part) is q of about 0.06 to 0.3. The rover stops often, so a bias estimate at every standstill (zero-velocity update) is cheap and was not modelled.
- **The sim's map degradation is not only drift.** The q switch also turns on a white 0.5 deg noise on the tilt sensor (`imu`), applied per frame to the ToF projection (`consoleMap.ts` lines 42 and 85). At 1 m that is 9 mm of height error per sample against a 30 mm rock threshold. With 6 seeds on the short route, q = 0 gave precision 56%, and q = 0.03 (a bias of 0.006 deg/s, negligible) already gave 31%, with q = 0.1 to 1 all at 25 to 39%. So most of the loss from perfect to q = 0.03 is the tilt noise, not the pose. A real accelerometer plus gyro complementary filter gives about 0.1 deg (assumption), five times better than the sim. **Do not tune on this yet:** the map metric is noisy (recall 32 to 46% across all q, 6 seeds, one short route) and only separates q = 0 from the rest; a longer route and more seeds are needed before a conclusion about drift alone.
- **Not modelled, and the real rover would suffer from it:** skid-steer slip. Four wheels turning in place scrub badly, so yaw from wheel counts is poor (tens of percent, from memory) and the gyro must own heading. Also a posed strut that lifts a wheel breaks the count for that wheel; use the mean of the wheels in contact, or the flow sensor below.

## 2. Candidate sensors

| Option | Measures | Typical error (unchecked) | Era | Fits the body? | Verdict |
|---|---|---|---|---|---|
| Gyro, calibrated at every stop (ZUPT) | heading rate | 0.01 to 0.05 deg/s residual, so 1 to 3 deg per minute driving | MEMS from 1990s (ADXRS, 2000s) | any internal spot | **Do it first**; costs only firmware |
| Magnetometer | absolute heading | 2 to 5 deg outdoors; indoors steel, motors and magnets near the part make it unreliable | KMZ51 or Vector 2X compass modules, late 1990s | inside, away from the strut motors | Useful as a slow correction only; needs tilt compensation, and the rover flips |
| Sun compass from the face cells | heading outdoors | a few deg; needs sun azimuth from a clock and place | Sojourner-era idea (sun sensors) | **already there**: currents of the four cell faces | Cheap and thematic; outdoor only; upside-down ambiguity resolved by the tilt sensor |
| Downward optical flow (mouse sensor) | translation over the ground without wheel slip | 1 to 5% of distance, surface dependent; fails on glossy or featureless surfaces and on dust | ADNS-2610 class, 1999 on | needs a hole in a lid and a standoff of a few mm to a few cm that changes with the struts | Good tabletop odometry; the belly is a cell lid and the rover works upside down, so two sensors (one per lid) or none |
| Beacon ranging, ultrasonic (Cricket, Active Bat) | range to 2 or 3 posts | about 1 cm (published systems quoted a few cm; from memory) | MIT Cricket 2000, AT&T Active Bat 1999 | 40 kHz capsule 10 mm, beam narrow, so one per lid and end; radio packet gives the time sync, so no extra RF | **Best absolute fix**; operator places 3 posts; no drift at all; indoor or outdoor short range |
| Landmark in a still (coloured or fiducial marker) | bearing, rough range | at 160 x 120 and 60 deg, 0.4 deg per pixel; a 60 mm marker at 1 m is about 9 px, so range is poor (about 10%), bearing about 0.2 deg | the sim already has it | uses the existing camera; the window is fixed on one end, so the rover turns to look | Cheap fix every few seconds at the cost of link time (about 3 s for a 160 x 120 still at 9600 bit/s, assumed 3 KB); two markers triangulate |
| Known-arena map matching (table edge, walls as lines) | distance and angle to a straight edge | limited by the 8 x 8 ToF (3 mm + 1% of range) | Monte Carlo localisation, 1999 | no hardware | **Free for the tabletop sim**; resets lateral position and heading whenever an edge is seen; outdoors nothing |
| Overhead camera on the console side | the rover's position | very good | not era | none on the rover | Breaks the premise (the operator would see the rover); mention only |

## 3. Recommendation

1. **Calibrate the gyro at every standstill and fuse tilt properly** (firmware, no parts). Expect the sim's default to move from x1 to about x0.1 with no hardware change.
2. **One absolute fix: ultrasonic beacons** (3 posts, radio-synchronised), the Cricket pattern. It is the only option here that removes drift on both axes and heading (three ranges give a pose when two receivers are on the body) and it needs nothing but two capsules and a timer capture on the PIC32. Cost: the capsules need windows on faces already allocated, which is the real design question (section 4).
3. **Cheap second layer:** coloured markers by still (already in the sim) as a bearing fix, and a table-edge fix in the sim's console.
4. A downward flow sensor is optional; it fixes wheel slip, which is not what dominates (section 1).

## 4. Open questions for the owner

- Are beacon posts acceptable in the interpretation? They are placed by the operator, like a landmark, and give the rover no map. They also add a setup step (place, survey, or three known positions).
- Where do the 40 kHz capsules go (two needed for heading, one per lid because the rover works inverted)? The lids are full cell pockets and the end faces hold the window and antenna, so the likeliest answer is a small hole through the lid between cell edges, or the hub faces (which have no cells).
- Check, in this order: the Cricket and Active Bat papers for accuracy and range; a MEMS gyro datasheet for in-run bias stability; the ADNS-2610 or 3080 datasheet for height range and field.

## 5. Next steps

1. Sim: split the q switch into pose drift and tilt noise, add gyro calibration at stops, rerun `npm run map` over a longer route and more seeds.
2. Sim: add a beacon-fix option and a table-edge fix; measure the map again.
3. Read the sources in section 4 and replace the unchecked figures.
