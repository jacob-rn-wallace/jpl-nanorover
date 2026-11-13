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
| Beacon ranging, ultrasonic (Cricket, Active Bat) | range to 2 or 3 posts | **plan on 3 to 5 cm, not 1 cm** (see section 7: Active Bat about 3 cm with a ceiling grid; Marvelmind claims 2 cm but an independent lab test measured 4.7 to 10 cm RMS) | MIT Cricket 2000, AT&T Active Bat 1999 | 40 kHz capsule 10 mm, beam narrow, so one per lid and end; radio packet gives the time sync, so no extra RF | **Best absolute fix**; operator places 3 posts; no drift at all; indoor or outdoor short range |
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

> **Superseded in part by section 12 (same day): GNSS was dropped.** The GNSS patches, receiver and lid window described below, and the open items about them, no longer apply; the 2.4 GHz comms patch and the radio decision stand.

**Decided (owner):** (1) outdoor use is a goal; (2) a modern GNSS module is acceptable under the era rule (the spirit governs parts selection only, and this is a judgement call: a multi-band RTK receiver is not a small simple part with a lineage to the era, so the era rule is bent here on purpose); (3) the radio moves from 900 MHz to a 2.4 GHz serial module (802.15.4 class, not Wi-Fi), and the end-face antenna becomes a patch, so the gravity-oriented whip and its counterweight are dropped.

**Direction finding on the rover was looked at and not adopted** (arithmetic, mine, unchecked): a two-element phase baseline gives about 5 deg at 900 MHz (100 mm, 0.3 wavelength) and about 3 deg at 2.4 GHz (60 mm, just under half a wavelength, no ambiguity) for a clean 10 deg of phase error; 3 deg at 2 m is about 11 cm laterally and indoor multipath is worse, so it does not clearly beat beacons (3 to 5 cm, section 7) or RTK (1 to 2 cm, from memory), and two antennas on a line leave a front/back ambiguity. A second GNSS antenna for heading (about 100 mm of baseline, a few mm of relative error) gives roughly 2 to 5 deg, no better than the gyro; heading from motion with RTK is free (a few degrees after about 30 cm of travel, about 8 s at 40 mm/s), so heading is gyro, fused with course over ground. If radio direction finding is ever wanted, the array belongs at the console (BLE 5.1 AoA pattern), not on the rover.

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

## 7. Precedents for beacon positioning, checked 2026-11-13 (web search; what was and was not confirmed)

**Correction first:** the earlier "about 1 cm" for ultrasonic beacons (sections 2 and 3) was from memory and too optimistic. Confirmed figures: Active Bat about 3 cm "throughout our 10000 square foot building" (Cambridge page), and Marvelmind states 1 to 3% of distance absolute and plus or minus 2 cm differential, but a 2026 independent lab test (AGV and robot arm) measured 101 to 104 mm RMS on raw ultrasonic data and 47 to 49 mm after fusing an IMU, and a forum user reports echo problems. **Plan on 3 to 5 cm after fusion**, and the two-receiver heading estimate (about 0.3 deg from a 0.5 mm path difference over 100 mm) stays an unchecked arithmetic claim: echoes and the speed of sound are common to both receivers, which helps, but no source here confirms it.

| System | What was confirmed | What was not |
|---|---|---|
| **Eurobot (2.1 x 3 m table), Pierlot and Van Droogenbroeck, Liege, 2009** | Three infrared beacons per robot on supports around the field (one mid small edge, two at opposite corners); the robot carries a rotating-turret IR receiver (TSOP7000, stepper, PIC in assembly, no OS, 8 x 8 x 8 cm, 100 mA, 10 Hz); angle precision about 0.1 deg (the authors say the accuracy was not measured directly; the triangulation position error on the field is about 1 cm and implies about 0.1 deg); no synchronisation between beacons and robot; triangulation also gives heading; the authors say lasers are restricted by the rules | The start year (1998 was from memory) and how many teams use beacons |
| **Active Bat (Cambridge, Ward, Jones and Hopper, IEEE Personal Communications, Oct. 1997)** | Ultrasonic time of flight to ceiling receivers; about 3 cm | The "95% of readings" qualifier (not found); it tracked people and objects, not robots |
| **Cricket Compass (MIT, Priyantha et al., MobiCom 2001; Wang, MEng thesis 2004)** | One RF receiver and several passive ultrasonic receivers on a board; orientation from the differences in reported distances; 3-DOF orientation from an array | The accuracy in degrees, the number of receivers and the spacing (the thesis PDF was not readable here; I said about 3 deg from memory, unconfirmed) |
| **Marvelmind** | 915 or 868 MHz radio plus ultrasonic ranging, stationary beacons, mobile beacon with optional IMU; figures above | Real-world accuracy beyond the one 2026 study |
| *Borenstein, Everett and Feng, "Where Am I?" (1996)* | The report exists and covers positioning methods including active beacons | That it covers Kleeman or Figueroa (not found; those two names were from memory and are unconfirmed) |
| Underwater long-baseline acoustics, iRobot NorthStar, Mars Exploration Rover sun-finding | Not searched | Everything; from memory |

**What the Eurobot design teaches (mine):** (1) it is the closest precedent in scale and setup (a table, three operator-placed posts, a PIC, no synchronisation); (2) it measures angles, not ranges, and gets heading for free, but its receiver is a motor-driven turret of 8 x 8 x 8 cm, which is a large share of a 140 x 140 x 60 mm body and moves a part (the era would accept it, the sealed body less so); (3) its field is open (the beacons see the receiver along a line of sight above the robot, in a volume the rules reserve), where the nanorover's receivers would sit on the lids close to the ground, so line of sight to low posts and echo from the table are the real risks; (4) an angle-based IR system and a range-based ultrasonic one are alternatives, and neither has been bench-tested here. Both need beacon posts the operator places.

Sources: [Pierlot and Van Droogenbroeck 2009 (PDF)](https://orbi.uliege.be/bitstream/2268/30550/1/Pierlot2009ASimple.pdf); [Cambridge Active Bat page](https://www.cl.cam.ac.uk/research/dtg/attarchive/bat/); [Wang 2004 thesis record](https://dspace.mit.edu/handle/1721.1/16689); [Marvelmind accuracy discussion (Pololu forum)](https://forum.pololu.com/t/precise-2cm-indoor-navigation-system-for-robots/8392); [Borenstein, Everett and Feng, "Where Am I?"](https://users.exa.unicen.edu.ar/catedras/irobotic/papers/pos96rep.pdf); the 2026 Marvelmind study ([citedrive record](https://www.citedrive.com/en/discovery/performance-evaluation-and-error-mitigation-of-ultrasonic-indoor-positioning-an-esp32-based-imu-eskf-architecture/)) was seen only as a search summary, not read.

## 8. Decision (owner, 2026-11-13): ultrasonic beacons

The owner chose **ultrasonic ranging (Cricket pattern)** over the IR angle system (Eurobot pattern). Reasons (mine, from the comparison in conversation): the receivers are a few cm3 against about 500 cm3 for a turret, nothing moves, the radio packet gives the time sync, and four 10 mm holes fit a sealed, invertible body where a turret window does not. IR's better accuracy (about 1 cm, tabletop) does not outweigh that. Not compared in the sim: only the ultrasonic fix was built.

**On the body (corrected the same day, see below):** 40 kHz capsules on the vertical faces, plus a timer capture and an amplifier on the PIC32. The first version of this paragraph put two per lid behind holes; that does not work (a lid capsule faces the sky, the posts sit near the horizon). **Off the body:** three operator-placed posts, each an emitter, a radio and a battery.

**In the sim** (`sim/src/sensors.ts`, `BEACON` in `constants.ts`; off by default, `odo.beacons`): a range to each post every 0.5 s with 4 cm noise and a 5% echo rate (+15 cm), a Gauss-Newton position from the dead-reckoned start, gating of fixes more than 25 cm off, a gain of 0.3, and a noisy heading (3 deg) blended at 0.1. All figures except the 3 to 5 cm are assumptions. `npm run pose` prints the pose error with and without it.

**Site check on the CAD** (`hardware/body/ultrasonic_render.py`, picture `docs/images/ultrasonic-sites.png`; the 90 degree cone and the 10 mm capsule are from memory, not a datasheet): a fixed capsule hears only its cone, so coverage needs at least one per vertical face (four), and two per face for a heading baseline. Rays cast from each proposed site against the carbon block, struts and wheels at the default 25 degree stance: **the hub-face sites (y = +-21.5 mm, z = 30 mm, beside the hub hole) are blocked, 0 to 16% of the cone clear to 400 mm at elevations of -10, 0 and +10 degrees, because the strut V covers the face**; the end-face sites are 100% clear but there is no room, the gaps between window, cells and edge being 8.9 mm against a 10 mm capsule. Struts at other poses were not tried. Untested ideas: a smaller capsule or re-divided gaps on the end faces; a capsule row in the 7.75 mm strips above and below the end cells (too small for 10 mm); the lid edges.

**Still open:** where capsules go at all (the end faces need a capsule smaller than 8.9 mm or a different split; the hub faces are covered by the struts); echoes off the table are not modelled; post placement and set-up by the operator.

## 9. Candidate: Valve Lighthouse base stations, received by the solar cells (indoor only; owner, 2026-11-13)

**Assumptions given by the owner:** stock Valve base stations, indoor use only (outdoors was to be covered by GNSS, since dropped, section 12), the rover only receives. **Idea:** the IXOLAR cells already on the lids and end faces act as the photodiodes, so no windows or holes are needed.

**What was checked (web search, standard mode; sources at the end) and what was not**
- Lighthouse 1.0 (V1): each station has two 60 rev/s drums, one sweep each, plus an IR LED flash for sync; the flash is a plain pulse of 62.5 us (announces azimuth sweep), 72.9 us (elevation) or 104.0 us (skip); a sweep takes 8.3 ms for 180 degrees; at most two stations, synced by cable or by line of sight (the figures are from a paper linked by Bitcraze; one other paper says the drums turn at 120 Hz, not resolved). A V1 signal is therefore plain optical pulses with no carrier.
- Lighthouse 2.0 (V2, the stations Valve sells now): the signal is modulated and carries an LFSR-coded data stream. One early Hackaday log reports a 1.8 MHz base-station frequency (a single, unresolved source). Bitcraze have written firmware that decodes it. **Not checked:** the V2 modulation details from a primary source.
- IXOLAR SM940K09L: monocrystalline silicon, sensitive from 300 to 1100 nm for the product family (a SolarMD document reposted by a distributor). Listings disagree on its electrical figures (DigiKey: 184 mW, 6.22 V open circuit, 39 mA short circuit; datasheets.com: 1.25 W, 246 mA, 9 cells in series). **No spectral curve or capacitance for the part was found.** A series string of about nine cells has far less capacitance than one big junction (my inference from the nine-in-series figure; the 0.1 to 1 uF guess I gave earlier was for a single junction and is probably too high).

**Arithmetic (mine, unchecked against hardware)**
- A laser line sweeping at 60 rev/s moves at 377 m/s per metre of range. A 21.5 mm cell is crossed in about 57 us at 1 m and 28 us at 2 m; a 44.5 mm cell in 118 us and 59 us. The sync flashes are 62.5 to 104 us, so a sweep pulse across a cell can be as wide as a sync pulse; the firmware tells them apart by when they arrive in the frame (the flash comes first), not by width.
- One microsecond of timing is 0.38 mrad (0.022 degrees), which is 0.75 mm sideways at 2 m. An edge jitter of a few microseconds is a few millimetres.
- A transimpedance amplifier that holds the cell near zero volts (10 kOhm feedback, 10 nF cell, a 10 MHz op-amp) gives a bandwidth of about 100 kHz, a rise time of a few microseconds. A cell loaded by an ordinary resistor would smear the pulses.

**What stock stations imply**
1. **V1 stations suit the cells; V2 stations probably do not.** V1 is plain pulses a transimpedance stage can follow. V2 needs a front end that follows a carrier of about 1 MHz, which a large-area cell with its capacitance is a poor fit for; the Triad receiver chips used for V2 are made for small photodiodes. V1 stations are no longer sold new (used market only, my understanding), so the owner's choice of stations decides the receiver.
2. **Cells as separate receivers.** Each lid holds nine separate cells (six SM940K09L, two SM401K08TF, one SM531K08TFS), spread over 133 mm, so heading and, with enough sensors, a pose from a single station may be solvable (not worked out here). That needs each cell wired out separately through its own tap, which also has to leave the charging path alone.
3. **Capture channels.** Sensors on one lid are hit within about 130 us of each other (100 mm at 754 m/s), so they need simultaneous capture. The PIC32MX has five input captures; an analog switch picking the lid that faces up (the tilt sensor knows) would let five cells on the up-lid use them. My design idea, not worked out.
4. **Unknowns that decide it:** the cells' response at the stations' wavelength (I believe 850 nm for V1; not checked), the transmission of the lid's top layer in the IR, the light at the cell at 2 m (unchecked), and the cell's capacitance and shunt noise.
5. Indoors, the stations are overhead and the lid cells face them; the end-face cells see them at a steep angle (about 60 degrees off axis for a base 2 m high and 1 m away), where a flat cell's response falls. Struts and wheels cannot shadow the lid cells (no part rises above z = 45 mm, the lid is at 60 mm).
6. The Valve stations track a roughly 5 m volume (from memory); a tabletop sits well inside it.

Sources: [Bitcraze, Lighthouse system overview](https://bitcraze.io/documentation/repository/crazyflie-firmware/master/functional-areas/lighthouse/system_overview); [Lighthouse positioning dataset, accuracy and precision (arXiv 2104.11523)](https://arxiv.org/pdf/2104.11523); [Bitcraze, Advanced Lighthouse usage, 2021](https://www.bitcraze.io/about/events/documents/bam2021/Advanced_Lighthouse_Usage_bam2021.pdf); [Bitcraze, lighthouse v2 deck prototype, 2025](https://www.bitcraze.io/2025/03/working-on-lighthouse-v2-deck-new-prototype/); [Bespeland, Lighthouse 2.0 tracker research](https://bespeland.github.io/portfolio/p3-LH2-Tracker); [Hackaday log on the TS4231](https://scriptagc.wasmer.app/https_hackaday_io/project/153224/logs); [DigiKey, SM940K09L](https://www.digikey.sg/en/products/detail/anysolar-ltd/SM940K09L/9990450); [datasheets.com, SM940K09L](https://www.datasheets.com/anytek-technology/sm940k09l).

## 10. Lighthouse 1.0 and the cells, against the BPW34 (owner, 2026-11-13: focus on 1.0 stations; the BPW34 was the receiving photodiode)

**BPW34, from the Vishay datasheet (Rev. 2.1, document 81521, read in full):** a silicon PIN photodiode, radiant sensitive area 7.5 mm2, spectral range 430 to 1100 nm with the peak at 900 nm, half-sensitivity angle +-65 degrees, short-circuit current 47 uA at 1 mW/cm2 and 950 nm (70 uA at 1 klx), capacitance 70 pF at 0 V and 25 pF at 3 V, rise and fall times 100 ns (10 V, 1 kOhm load, 820 nm), noise equivalent power 4 x 10^-14 W/sqrt(Hz). The 47 uA over 75 uW of light on its area gives a responsivity of 0.63 A/W (my division).

**The cell, as far as it could be pinned down.** The datasheet for the SM940K09L itself was not found: the two Anysolar PDFs retrieved were for other parts (SM641K10TF and KXOB201K04TF; the family is laminated in EVA and a polymer film, monocrystalline, 300 to 1100 nm, 25 % efficient). The SM940K09L figures are from the DigiKey listing (39 mA short-circuit current, 6.22 V open circuit) and a second listing that says nine cells in series. These agree: at about 40 mA/cm2 for a 25 % cell (my typical figure), 39 mA means about 1 cm2 per cell, and nine of them is 9 to 10 cm2, which matches the 44.5 x 21.5 mm outline. So **each sub-cell is about 100 mm2, about 13 times the BPW34's area**, and a string of nine sits in each part.

**How the cells compare with the BPW34 (arithmetic mine, not measured)**

| | BPW34 | SM940K09L (inferred) |
|---|---|---|
| Light-collecting area | 7.5 mm2 | about 100 mm2 per sub-cell, nine in series |
| Responsivity near 900 to 950 nm | 0.63 A/W | similar order, not found for the part; the laminate's loss is unknown |
| Capacitance | 70 pF at 0 V | unknown; scaled by area from the BPW34 gives about 1 nF per sub-cell, so 0.1 nF for the string (more if a cell junction is higher-capacitance than a PIN diode: up to about 1 nF) |
| Edge speed | 100 ns | set by the amplifier: a transimpedance stage (10 kOhm, 10 MHz op-amp) gives a bandwidth of 0.4 to 1.3 MHz and a rise time of 0.3 to 0.9 us |
| Acceptance angle | +-65 degrees | a flat cell follows the cosine law, roughly +-60 degrees, much the same |

**What follows**
1. **Speed is not the obstacle.** A Lighthouse 1.0 pulse is tens of microseconds wide (sync 62.5 to 104 us; a sweep across a cell 28 to 118 us). A 1 us rise time is a hundred times slower than the BPW34's and still far faster than the pulse. Edge-time walk with amplitude, a microsecond or so, is about 0.75 mm sideways per microsecond at 2 m (section 9).
2. **Signal is comparable, not obviously worse.** A sub-cell collects 13 times the light of a BPW34 when lit uniformly, but a sweeping laser line lights only a strip of it at a time (the beam's thickness at the cell is not known), so the amplitude lands within a factor of a few of the BPW34's. That depends on the light the stations put on a cell at 2 m, which was not found.
3. **The real risk is the series string.** The nine sub-cells are in series, so the string's short-circuit current is limited by its darkest sub-cell. If the sub-cells lie side by side along the sweep direction, a thin line lights one of nine at a time and the current pulse is mostly lost. A horizontal sweep and a vertical sweep cross the part along different axes, so one of them hits the long axis whatever the orientation, unless the nine cells are laid out in two dimensions. **This needs the package drawing for the SM940K09L (cell layout), which was not found.** A possible readout that avoids it: sense the string's open-circuit voltage (a lit sub-cell adds about 0.5 to 0.6 V while dark ones add little) with a high-impedance AC-coupled comparator. My idea, not tested; its edge speed (the cell's photocurrent charging its own capacitance) is also unchecked.
4. **The lamination should not block the IR.** EVA and polymer film are transparent in the near infrared (my knowledge, not from the datasheet), and the family is rated to 1100 nm, so the cells should see 850 to 950 nm.
5. **Wavelength:** I believe the Lighthouse 1.0 stations use about 850 nm (not checked), inside both parts' range.

Sources: [Vishay BPW34 datasheet](https://www.vishay.com/docs/81521/bpw34.pdf); [DigiKey, SM940K09L](https://www.digikey.sg/en/products/detail/anysolar-ltd/SM940K09L/9990450); [datasheets.com, SM940K09L](https://www.datasheets.com/anytek-technology/sm940k09l); Anysolar SolarMD datasheets for SM641K10TF and KXOB201K04TF (family wording only).

### 10b. The SM940K09L datasheet, found (Anysolar, "Preliminary", Rev. May 2025; read as text and as page images)

- **Part:** 44.5 x 21.5 x 1.8 mm, 3.3 g; Voc 6.22 V, Isc 39.0 mA, Vmpp 5.02 V, Impp 36.6 mA, 183.7 mW at 1 sun (AM1.5); efficiency 25 %; laminated in EVA and polymer film.
- **Cell count:** not stated. The per-cell curves run to about 0.69 V per cell, and 6.22 / 0.69 gives **nine cells in series**; the per-cell short-circuit density is about 41 mA/cm2, so 39 mA is about 0.95 cm2 per cell, nine of them filling the outline. This confirms the inference in section 10.
- **Layout: not shown.** The front view is one uniform blue block (44.5 x 21.5 outline, 20.0 mm active height, no cell boundaries drawn); the back shows two contact pads. **Whether the nine cells are strips across the long axis or along it is still unknown.** (Unresolved; Anysolar's email, techdevelop@anysolar.biz, is the listed contact.)
- **Spectral response (external quantum efficiency curve, page 2):** about 95 to 99 % from 400 to 1000 nm, falling through 1050 nm to near zero at 1200 nm. **At 850 and 940 nm that is about 98 %**, which gives a responsivity (my arithmetic, EQE x wavelength / 1240) of about 0.67 A/W at 850 nm and 0.74 A/W at 940 nm, against the BPW34's 0.63 A/W at 950 nm. It is the cell's figure; the loss in the EVA and film is not stated.
- **Capacitance: not given.** Voc against irradiance is logarithmic: about 0.48 V per cell at the lowest irradiance plotted, 0.69 V at 1000 W/m2.

**Correction to section 10 point 3.** The open-circuit-voltage readout I suggested is probably too slow: a forward-biased junction has a large diffusion capacitance (my estimate, not measured), so a lit cell charging to about 0.5 V from tens of microamperes would take milliseconds, not microseconds. Drop it. With a transimpedance amplifier (the string shorted) a thin sweep that lights few of the nine cells is not lost completely: the current has to pass through the dark cells, limited by their shunt resistance and a reverse voltage the lit cell can supply (a fraction of 0.5 V, shared among eight cells). The datasheet gives no shunt resistance, so the attenuation is unknown. If the cells are strips across the long axis, a sweep line parallel to the strips lights one at a time and loses most of its signal, while a perpendicular one lights all nine and loses little; one of the two orthogonal sweeps is always the bad case unless the layout is two-dimensional (my reasoning). The sim parameter `LIGHTHOUSE.detect` stands in for that loss.

### 10c. Lighthouse 1.0 in the sim (`sim/src/sensors.ts`, `LIGHTHOUSE` in `constants.ts`; `odo.lighthouse`, off by default; `npm run pose`)

Two stations at diagonal table corners, 1.6 m up, a fix every 33 ms (assumed); five lid cells (four near the corners, one at the centre) as sensors; noisy azimuth and elevation per sensor (3 us timing error, 0.065 degrees), a Gauss-Newton fit of position and heading to the estimate's height and the tilt sensor's pitch and roll, gated at 15 cm and blended at 0.25 per fix. Six seeds, the same route, drift setting x1:

| Run | Mean RMS position error | Mean worst |
|---|---|---|
| no fix, no gyro calibration | 28.2 cm | 52.1 cm |
| gyro calibration only | 0.5 cm | 0.9 cm |
| calibration and ultrasonic beacons | 2.8 cm | 8.4 cm |
| **Lighthouse, no calibration, every sweep detected** | **0.1 cm** | 0.2 cm |
| Lighthouse, half the sweeps detected | 0.1 cm | 0.2 cm |
| Lighthouse, one sweep in five detected | 4.1 cm | 10.4 cm |

**Reading it:** the Lighthouse fix pins the pose to about a millimetre, better than the beacons' 3 cm and than calibration alone, and it keeps working when half the sweeps are lost (the series-string loss of section 10b). At one in five detected there are too few angles per fix (the fit needs six) and the error is back up to 4 cm. **Limits of the comparison:** the sim has only gyro-bias drift (section 1), so calibration alone already does well; line-of-sight shadowing by the table's rocks, the rover's own wheels at the lid edges, and reflections are not modelled; the 3 us timing error, five sensors, 30 Hz fix rate and the station positions are assumptions; the sensor angles are computed from the true pose with no calibration error in the stations' positions, which a real set-up would have (Lighthouse base stations are normally calibrated by the host software against the sensor geometry).

## 11. Sun tracking against GNSS, outdoors (question from the owner, 2026-11-13; web search for the figures cited, the rest is my reasoning)

**What a sun sensor can give.** The cells already on the faces are cosine-law sensors: the photocurrent of a face follows the cosine of the angle between its normal and the sun. The lids give the vertical component of the sun vector, the end faces give the component along the body's y axis, and there are no cells on the hub faces, so the x component comes only from the unit length of the vector (a sign ambiguity: the sun is ahead of or behind the cross axis). With the time (a clock), an approximate location, and the tilt from the inertial sensor, the sun's world azimuth is known, so the measured body-frame direction yields **heading, and nothing else**. A sun fix cannot give position at this accuracy: a position line from the sun's elevation needs sextant-class angles (one arc-minute is one nautical mile), orders of magnitude beyond cells.

**What was found:** sun-based heading is proven on rovers (Furgale, Enright and Barfoot's rover study used a sun sensor, an inclinometer and a clock and called both of their techniques accurate); a camera-only sun sensor reached heading within 2.4 degrees in a Caltech thesis; a commercial CMOS celestial heading sensor claims 0.1 degrees (a vendor claim, not an independent test); simple photodiode designs are coarser, and photodiode readings drift with temperature in one satellite study. **No head-to-head comparison with GNSS heading on a small outdoor robot was found.**

**Comparison (mine, unchecked)**

| | GNSS (RTK, section 6) | Sun from the cells |
|---|---|---|
| Position | 1 to 2 cm (from memory, section 6) | none |
| Heading | from motion, a few degrees after about 30 cm of travel (section 6); none at rest | a few degrees, my guess for cosine cells, calibrated; works at rest |
| Needs | sky view, a base for RTK | a visible sun, a clock, a rough location, a calibration of the cells |
| Fails when | under canopy or beside buildings (multipath) | overcast, near sunrise or sunset (tilt error grows), with the sun near the zenith (azimuth poorly defined), and wherever struts or wheels shade a cell |

A heading error of 3 degrees over 10 m of travel is about 0.5 m of sideways dead-reckoning drift (10 m x tan 3 degrees); at 40 mm/s that is 250 s. So the sun alone, with odometry, is a coarse, drifting navigation aid (about 5 % of distance), where GNSS is centimetres absolute. **Verdict:** feasible and nearly free as a heading aid (the cells exist; it needs a current measurement per face, a clock, a rough location, and a calibration), useful when the rover is stationary or when GNSS motion-heading is slow; not a replacement for GNSS. The diffuse sky light on a cloudy day biases the cells toward the zenith and it fails under overcast, which is when the cells also barely charge the battery (section 6 of body-redesign: 0.26 W in thin overcast). Not built in the sim.

Sources: [Heading Estimation via Sun Sensing for Autonomous Navigation (Caltech thesis)](https://thesis.caltech.edu/10338/); [Sun Sensor Navigation for Planetary Rovers: Theory and Field Testing](https://www.bohrium.com/paper-details/sun-sensor-navigation-for-planetary-rovers-theory-and-field-testing/811648944273620992-2511); [Stelion Heading (vendor)](https://www.unmannedsystemstechnology.com/company/stelion-systems/stelion-heading/).


## 12. Decision (owner, 2026-11-13): GNSS dropped; absolute positioning is an optional extra

**Decided:** because the Lighthouse idea (section 9 to 10c) needs nothing from the design, absolute positioning is set aside for the foreseeable future. If the Lighthouse fix works with the existing cells, it is a free auxiliary system, like GNSS was meant to be; if it does not, the rover works without it (dead reckoning with gyro calibration at stops and tilt fusion, section 1 and the sim). **GNSS is removed** (both lid patches, the receiver, the 25 mm cell-free lid windows, the RTK link requirement); **the 2.4 GHz comms patch and the radio stay.** Outdoors the rover therefore has no absolute fix; section 11 (sun heading) is a possible later aid, not planned.

**Done in the repository:** `hardware/body/layout.py` and `block.py` no longer have the GNSS placements, windows or cut; `layout.py` and `block.py` were rerun: 7 placements clear, **33 cavities** (the count before GNSS), 871 cm3 remaining, the STEP re-imports as one solid. The cell layout was never changed for GNSS (the symmetric IXOLAR arrangement stayed in `cell_pocket.py`; a window was only proposed), so nothing to revert there. **Mass: the body contents are now 416 g against the 386 g budget (over by 30 g), down from 437 g (over by 51 g)**, after taking out the two patches and the receiver (assumed 9 + 9 + 3 g). The body centre of mass is x +0.9, y -1.5, z 30.0 mm.

**What no longer applies:** section 6's GNSS items, the cell-layout window problem, the RTK corrections and the faster-link argument (the 2.4 GHz module stays for its own reasons: the still and the cyclic loop), the GNSS-desense question. Sections 6 and 11 are kept as the record.
