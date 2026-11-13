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

## 6. Decisions of 2026-11-13 (owner) and what they change

**Decided (owner):** (1) outdoor use is a goal; (2) a modern GNSS module is acceptable under the era rule (the spirit governs parts selection only, and this is a judgement call: a multi-band RTK receiver is not a small simple part with a lineage to the era, so the era rule is bent here on purpose); (3) the radio moves from 900 MHz to a 2.4 GHz serial module (802.15.4 class, not Wi-Fi), and the end-face antenna becomes a patch, so the gravity-oriented whip and its counterweight are dropped.

**Direction finding on the rover was looked at and not adopted** (arithmetic, mine, unchecked): a two-element phase baseline gives about 5 deg at 900 MHz (100 mm, 0.3 wavelength) and about 3 deg at 2.4 GHz (60 mm, just under half a wavelength, no ambiguity) for a clean 10 deg of phase error; 3 deg at 2 m is about 11 cm laterally and indoor multipath is worse, so it does not beat beacons (about 1 cm) or RTK (1 to 2 cm), and two antennas on a line leave a front/back ambiguity. A second GNSS antenna for heading (about 100 mm of baseline, a few mm of relative error) gives roughly 2 to 5 deg, no better than the gyro; heading from motion with RTK is free (a few degrees after about 30 cm of travel, about 8 s at 40 mm/s), so heading is gyro, fused with course over ground. If radio direction finding is ever wanted, the array belongs at the console (BLE 5.1 AoA pattern), not on the rover.

**Antenna architecture now in `hardware/body/layout.py` and `block.py` (placeholders, all sizes and masses assumptions):**
- **Comms:** a 2.4 GHz ceramic patch (15 x 15 x 4 mm on a 30 x 30 mm ground board, 4 g) behind an RF-transparent 26 mm window in the -y wall at x = -48.07, z = 30, polarised along z. Upright and inverted are a 180 degree turn about y, which keeps the polarisation vertical, so nothing has to orient itself: the pendulum, its 8 mm disc, the rotary RF joint, the shaft hole and the outside whip (10 g + 3 g) are gone. The 26 mm circle also gives the -y face the same look as the camera face (the earlier "dummy circle" question is answered).
- **GNSS:** one patch per lid (25 x 25 x 5 mm with its ground board, 9 g each; the sky side is a 25 mm cell-free window through the lid), because the rover works inverted and a GNSS patch needs the sky; one RTK receiver module standing in the centre gap on the plane z = 30 (22 x 17 x 3 mm, 3 g; ZED-F9P class, from memory). The tilt sensor selects the antenna facing up; RTK reconverges after a flip (a few seconds to tens of seconds, assumption).
- **Checks:** all ten placements are clear of the keep-in volume, the servos and the hub; `block.py` cuts 38 cavities (was 33), 859 cm3 left, STEP re-imports as one solid. **Mass: the body contents are now 437 g against 386 g (over by 51 g, was 39 g): the two 25 mm GNSS patches (at an assumed 3.5 g/cm3 ceramic) outweigh the pendulum.** The mass budget is still deferred.

**New open items:**
1. **Cell layout:** each lid needs a 25 mm cell-free window and the symmetric IXOLAR arrangement has none. The cheapest cut is to drop one SM940K09L (44.5 x 21.5 mm, 9.6 cm2, 3.3 g) per lid, but a 25 mm patch does not fit its 21.5 mm width; an 18 mm L1-only patch would, at the price of the L2 band. Not decided; the cell areas and masses in `layout.py` are unchanged.
2. **A second comms patch.** A patch on one end face covers the -y hemisphere, with weaker sidelobes toward +/-x (the wheels and struts are there) and +y. The +y face has no room (window plus four cells). Options: swap one cell for a window on +y (the pocket is then redone), or accept one end. Indoors the margin is huge (about 90 dB at 2 to 5 m by free-space arithmetic); outdoors it matters.
3. **RF behaviour is unsimulated:** the carbon lid as a lossy ground plane for the GNSS patch, the aluminium wheels and struts around the comms patch, desensing of the GNSS receiver by the radio less than 10 cm away (a 2.4 GHz transmitter is easier to filter than 900 MHz, not tested). Needs an EM simulation or a bench test.
4. **RTK corrections** run from a base receiver at the console over the same radio, roughly 500 to 1000 bytes per second (from memory), so the link rate matters: the 9600 bit/s the sim assumes would be mostly used up. A 250 kbit/s 802.15.4 module (about 100 kbit/s real) solves it and also cuts a still from about 28 s to a few seconds; the sim's link model needs the new rate. A base needs a sky view and a surveyed antenna, an operator setup step like the beacons.
5. **Indoors RTK gives nothing**, so the beacons (section 3) stay as the indoor fix; outdoors GNSS replaces them.
6. Part numbers, current draw and the module's lifecycle for the 2.4 GHz serial radio and the GNSS receiver have not been looked up.
