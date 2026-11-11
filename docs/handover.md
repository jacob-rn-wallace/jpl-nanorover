# Handover: where the project stands (end of the first working session, 2026-11-10)

Written so a new session (or the owner, later) can pick the project up cold. It summarises, and points to, the other documents; where they disagree with this page, the more specific document wins. Read `CLAUDE.md` first for the working rules.

## 1. What the project is

An open replica of the JPL nanorover, the small four-wheeled asteroid rover built for the Japanese MUSES-C (Hayabusa) mission and cancelled by NASA in November 2000. The owner's scope: match the appearance and dimensions and perform most of the non-science functions (driving, independently posable struts, self-righting, solar power, the camera); not spaceflight, not the science instruments. All CAD is 1:1.
Open at the end of the session: which of three descriptions to copy, scale and materials, how the struts are actuated, and what the finished object is for (see sections 7 and 8). The owner decided to **defer the body and focus on the drivetrain**, which both built units share.

## 2. Repositories and how to run

- **`jpl-nanorover` (public, `jacob-rn-wallace/jpl-nanorover`).** `docs/` (specs, comparison, measurements, bibliography), `hardware/` (build123d CAD), `CLAUDE.md`, licences (Apache-2.0 code, CERN-OHL-S hardware, CC BY documentation; see `NOTICE.md`). Run from the repo root, in this order: `hardware/body/body.py`, `hardware/strut/strut.py`, `hardware/wheel/wheel.py`, `hardware/assembly/rover.py` (and `preview.py` for the picture). Each prints its own checks. `python3 -m venv .venv && .venv/bin/pip install -r hardware/requirements.txt`.
- **`jpl-nanorover-private` (private, cloned beside it).** The four Jones/Wilcox papers (`papers/`, with an INDEX), the two JPL photographs and a catalog (`images/sources.csv`, `python3 images/catalog_images.py --check` after adding any), the saved Brescia and IROS'97 pages, JPL's 1997 and 1998 videos, chat summaries (`previous-context/`), the old handover note, Hammond's STEP file (`cad/vendor/hammond-1590Z090/`, terms unchecked), and the photo-measurement scripts (`analysis/photo-measure/`, scratch quality, hard-coded paths, README explains the order).
- **Never copy files from the private repo into the public one**: record numbers and citations only. Anything containing Hammond's geometry stays out of git (`.gitignore`).
- **Videos (private repo, `video/`, with `SOURCES.md`):** the two JPL videos were re-encoded to .mp4 on 2026-11-10 to save space (49 + 58 MB down to 18 + 21 MB; SSIM 0.987 against the originals), and a 1997-era KTLA morning-news clip (5:25, 320 x 208) is committed too. Frames only were viewed, no audio heard: the black unit driven by a handheld remote on a studio floor, righting itself, with two guests on air. The old .mov files are still in the private repo's git history, so its size on GitHub (about 166 MB) shrinks only if that history is rewritten.
- Conventions: **left and right are the viewer's**; commits end with the attribution lines in the session's system reminder; decisions go in the docs with the date and "owner".

## 3. What the sources say

- **Papers (Jones & Wilcox, Wilcox & Jones, 1999 to 2000; four papers, one description).** 14 x 14 x 6 cm body, 1300 g; four 6.5 cm wheels on four 7 cm struts; struts in pairs on hubs at the centre of two opposite 14 x 6 cm faces; cells on four of six faces, patch antenna on top; each strut has two 10 g brushless motors (wheel, strut), 256:1 gearheads; potentiometers in the shoulder hub; contact sensor per wheel; optical bench of two aluminium-alloy panels; Synova R3000 processor, no battery, 2.3 W, 4800 bit/s; designed to 100 g, qualified for -180 to +110 C; rolling 1.5 mm/s, hops 10 cm/s; wheels "a complex assembly of thin conductors and insulator" that also sense the ground. **Written as a design in progress.** Strut length, body size and mass are stated in one sentence repeated in all four papers: one source.
- **Figure 1 of Jones & Wilcox (2000) is the silver unit's photograph.** The papers' text and unit B are not independent sources.
- **Weisbin (1998) / the JPL task page:** the task aims at 10 to 100 g rovers; first a few hundred grams, then "well under 100 g". The 1998 video narration (owner's transcription): "an even smaller Nanorover with a mass under 100 grams ... the key development is JPL's Widget Board". The 1.3 kg flight nanorover was a first step. `docs/smaller-than-nanorover.md` has the trail; the two JPL "Distributed motor controller" pages are a different (2006) project.
- **Videos (private repo).** 1997 (5:35) and 1998 (6:32) "Nanorover Technology Task". The black unit runs at 0:11 to 0:30 (1997) and 1:32 to 1:40 (1998); the silver unit is shown opened, with the optics, in 1997 (about 1:05 to 3:20); the 1998 video shows a banded-wheel lab prototype and animations of the flight vehicle.
- **Not obtained:** the full texts of Wilcox & Welch (1998, embedded control, an 80C51, several hundred grams), the i-SAIRAS '97 paper, the 1996 AIAA nanorover paper, the Wilcox oral history on ETHW (refused fetching).

## 4. The three designs, the status tags and the settling rule (`docs/design-comparison.md`)

- **A** the papers (the planned flight design); **B** the silver unit (carries the optics: round 26 mm window, tilted sealed-beam headlamp, antenna loop; owner: the internal test unit); **C** the black unit (square bonded camera window, thin box, PCB-like base; owner: a running publicity mock-up). **B and C have identical struts and wheels** (owner).
- **No final nanorover exists** (owner): elements are tagged **built** (seen), **planned** (papers) or **concept** (banded wheel with ground sensing, dust wipers, the sub-100 g rover). The default target is the most recent built hardware; planned and concept items are opt-in. The owner chose the built cleated wheel over the papers' planned banded wheel.
- **Settling rule (owner):** the papers win by default; a paper value is overridden only when B and C **independently** agree on a different one (on shared drivetrain parts they count as one observation). Result: body 140 x 140 x 60 mm, struts 70 mm, wheels 65 mm stand; the reference unit is **undecided** (owner: "not really sure").

## 5. Measurements from the photographs (`docs/photo-measurements.md`)

- Cameras solved from the vanishing points of the solar-cell edges (about 3900 px focal length for the black photo, about 1920 px for the silver).
- **Scale comes from the US quarter in the black photo:** k = 0.996 (0.97 to 1.02) on the 140 mm assumption. Black unit C: about 139 x 139 mm on top, 36 to 44 mm tall, struts about 76 mm, **wheels about 59 mm across the grousers**. Silver unit B (scaled with the wheel it shares with C): about 125 (hub axis) x 140 x 55 mm, struts about 78 mm. The papers' 6.5 cm wheels and 7 cm struts differ from the built hardware by 9 to 11%.
- **Wheel (`docs/wheel-spec.md`, fitted to the silver photo and checked by projecting the CAD back onto it):** a cone (apex about 10 mm above the rim) on a smooth hollow cylinder carrying 16 grousers in a helix: thin blades standing radially, serrated along their edges, 43.5 degrees from the axle, right-handed. Scaled to the papers' 65 mm over the grousers in the CAD (measured 59 mm).
- Window 26 mm, headlamp bezel about 22 x 14.5 mm, cell sizes (large cells about 40 x 23.5 mm on top), all as proportions of a face taken as 140 mm.

## 6. CAD status (`hardware/`, specs in `docs/*-spec.md`; the struts, wheels and hub below are superseded by section 11)

| Part | Modelled | Notes |
|---|---|---|
| Body | Hammond 1590Z090 box cut to 55 mm + 5 mm lid plate = 140 x 140 x 60 mm; 1.5 mm O-ring in a 2.0 x 1.1 mm groove on Hammond's own gasket path; 3 x 8 mm edge rib; M6 coil inserts; two stainless hub studs (double-D, face O-ring, jam nut); 26 mm window with a bonded pane | needs Hammond's STEP from the private repo |
| Struts | four, 70 mm, two layers per side on the stud's 12 mm axle | placeholder arm outline; struts cannot pass each other because each axle stub crosses the other's layer |
| Wheels | the cone and helical-grouser wheel, 65 mm, about 78 g | solid-ish, no motor |
| Assembly | whole model about 1455 g without motors or electronics (target 1300 g; the cast box is the heavy part) | overall at the default 25 degree stance: about 276 mm wide, 192 mm long |

Known problems: screw bosses are only 5 mm tall (inserts help); the O-ring groove has 0.55 mm of wall margin; the plate-bow estimate rests on an assumed 2 N/mm cord load and has no finite-element check; the real hub housing is larger than the 26 mm stud; the headlamp, the strut and wheel motors and wiring feedthroughs are not modelled; the Hammond terms of use are unchecked. **STEP export of anything built from offset curves silently drops faces** (the lid plate; `body.py` runs `nurbs()`); re-import every new part and check its volume.

## 7. Corrections made during the session (so they are not repeated)

Flat lathe-finished wheel disk -> a real cone. Stack of saw-blade discs, then a ratchet profile -> thin radial grousers in a helix. "Connector panel" -> a sealed-beam headlamp. "No black unit in the videos" (sampled too sparsely) -> it is in both. A scale factor of 1.11 from assuming the units' wheels were the papers' 65 mm -> the quarter gives 59 mm and k = 0.996. The first lid-plate STEP was broken (see above). The Distributed Motor Controller pages are not the Widget Board. The photo scales had assumed a 140 mm top face; the quarter now confirms it.

## 8. Open decisions (owner)

1. Which description to replicate (A, B or C), or a stated hybrid (what the CAD is today).
2. Wheel diameter (59 measured, 65 papers) and strut length (76 to 78 measured, 70 papers): both parameters; papers are the defaults under the rule.
3. Window shape, the headlamp, and whether to copy the black unit's look.
4. Purpose: a faithful display or working replica; a fun drivable rover (a camera-equipped toy-grade build: a Plantraco Desktop Rover plus camera cost about $180 in 2002; see the discussion of a possible pivot); or an open design others can build cheaply. A proposed two-stage path: a cheap working proof of concept first, the faithful build after.
5. The body is deferred; the drivetrain work of 2026-11-11 is in sections 11 and 12, and the body redesign is the next big job.

## 9. Next steps (drivetrain first; superseded by sections 11 and 12)

1. **Torque and speed budget** for lifting, self-righting and stepping with a body of 1.3 to 1.5 kg on 70 mm struts (a quick estimate: about 0.25 N.m per strut at worst, which is large for micro gearmotors); this decides the motors.
2. **Kinematic simulation** of the four-strut chassis with the body as a block of the right mass (poses, tipping, self-righting, step climbing). JPL itself ran a low-gravity dynamic simulation and planned KC-135 aircraft tests (the 1997 video, about 4:05 to 4:40 and 5:05); Tunstel (1999) evolved the self-righting sequences by genetic programming.
3. **Motor and hub design:** the strut-pivot motor at the hub, the wheel motor inside the drum, bearings, wire passage, the real hub size; then the wheel interior.
4. Make wheel diameter and strut length switchable parameters.
5. Later: the headlamp and window, the connector-free end face, wiring feedthroughs, the lid screws, the banded-wheel option.
- A side discussion on a toy-grade version and the possible pivot is in `docs/toy-version-notes.md`; a guide to what is in each video, with approximate timestamps, is in the private repo (`video/GUIDE.md`).
- **Research leads:** the Wilcox oral history; the full texts of the 1997 and 1998 papers (try `hdl.handle.net/2014/22984` and `/21976` from a browser, then put the PDFs in the private `papers/`); JPL Archives; the people named in the papers (Brian Wilcox, Ross Jones, Allen Sirota, Mike Johnson, Jack Morrison, Art Thompson; check whether any can be reached) with questions that survive foggy memory: which unit is which, do the units still exist, drawings or CAD, did the flight design keep the cleated wheel; measure the black unit's height and struts from the edge-on video frames (1997 video 0:23 to 0:29); transcribe the narrations.

## 10. Not verified

The owner's account of each unit's role (and the KTLA segment's unit) is taken on trust; the 1998 paper's contents come from search snippets; every size from the photographs is an estimate good to a few percent and depends on the quarter being read correctly and on the silver unit sharing the black unit's wheels; the cost and market comparisons for a toy version are rough and partly unverified.

## 11. The drivetrain session, 2026-11-11 (what was decided and built)

**Owner's decisions** (all recorded in `CLAUDE.md`): the replica must lift itself under Earth gravity; design mass 1.0 kg total, with the body to be redesigned later; metal wheels; layout C (thin-walled aluminium wheels with the wheel motor inside, strut servos in the body); motors chosen on cost (maxon motors are over $200 each, so Pololu and Feetech parts); a drive speed of about 40 mm/s, estimated from the videos (20 to 50 mm/s).

**What exists** (`docs/drivetrain-spec.md` is the long record; `docs/chassis-simulation.md` the simulation; `docs/strut-spec.md` and `docs/wheel-spec.md` the parts; scripts in `hardware/drivetrain/`):
- **Wheel:** `wheel.py` presets `thin` (default; 1.0 mm wall, 33 g) and `v1`. Maxon, Pololu #3046, Pololu #3068, 130-size and PCB-motor options were compared (`motor_options.py`); the **Pololu #3068** (9.5 g, $26.45) is in the CAD, clamped in the strut tip so the strut is its heat sink (about 7 times better than the motor alone, my estimate).
- **Wheel support** (`strut.py`, `TIP_MODE = "motor"`): the motor cannot carry the wheel (a 9 mm shaft, 0.25 to 0.5 kgf limit), so each wheel runs on two 3 x 8 x 4 mm bearings on a 3 mm stub shaft in a 19 mm aluminium spindle tube that the strut tip clamps, driven through an assumed coupling. Each strut's support starts flush with its own plate.
- **Coaxial hub** (`hardware/hub/hub.py`, `HUB_MODE = "coaxial"`): two Feetech STS3215 servos per side (55 g, datasheet), servo B on the axis driving a 5 mm inner shaft (outer strut B), servo A offset 23 mm driving a 15/11 mm hollow shaft (inner strut A) through a 1:1 gear pair, in a stationary housing with four small bearings.
- **Simulation:** the model shows the strut load is half what was designed for (maximum hold 0.166 N.m per strut), that the rover can right itself in about 3 s with 0.12 to 0.13 N.m, and that the working stance should stay at 25 to 40 degrees (tip-over 38 to 51 degrees).
- **Mass:** everything outside the old box is about 614 g, leaving **about 386 g of the 1.0 kg** for the body, electronics, solar cells and camera. The assembly model weighs 1574 g because it still contains the 961 g Hammond box and lid.
- **Checks:** 0 of 48 solids overlap at the default pose (struts, wheel support, wheels, hub, servos), and the servos fit inside the box with the wall's hub hole opened to 24.2 mm.
- **Studied and not taken:** belt layouts (2a, 2b), JPL's friction-pivot layout (3; now feasible, with 19 % margin), isogrid on the struts (2 g saved, stiffness 16 %), a custom PCB-stator motor, and 130-size motors.

**Run order:** body, hub, strut, wheel, assembly (`CLAUDE.md`); the first run needs `python3 -m venv .venv && .venv/bin/pip install -r hardware/requirements.txt`.

## 12. Open items and next steps after the drivetrain session

1. **The body redesign** (deferred by the owner; the next big job). Requirements it now has to meet: a mass of about 386 g with electronics and cells, the hub holes opened to 24.2 mm, room for four servos (45.2 x 24.7 x 32 mm, positions in `hub.py`) and the batteryless electronics, the centre of mass near the hub axis (the simulation's tip-over numbers assume it).
2. **Check the two unverified servo dimensions** against a real part or the full drawing: the shaft offset (about 10.7 mm from the end of the long side, read by eye) and the 32 mm body height.
3. **Smaller strut servos:** the load is low enough (0.17 N.m maximum hold) that a 3 to 5 kg.cm class servo could do; none was chosen. Dynamic loads are not simulated, so test before shrinking.
4. **Details not modelled:** gear teeth and backlash, how the pinion, the horn adapter, the wheel and the spindle tubes are fixed, a coupling of the right length (7.5 mm is tight), seals against dust on every shaft, strut stops, wiring, the shaft retainers, and the thermal paste or adhesive in the strut bores.
5. **Simulation extensions:** both struts moving together, momentum in the rolls, friction, steps and slopes (the handover asked for step climbing), the hop (JPL's 10 cm/s), and side-to-side tipping.
6. **Tests to do on a first print or prototype:** whether the STS3215 holds its position unpowered and how warm it runs at the hold torque; the #3068's temperature at the slope load; the wheel's stiffness at 0.8 mm walls; the gear mesh with printed against metal gears.
7. Older open items still stand: which unit to replicate, the banded-wheel option, the headlamp and window, the lid screws, and the research leads in section 9.
8. **Not verified:** the maxon price (owner's report), bearing masses and ratings (typical values), the servo's overload protection and torque limit register, prices and stock of every part, and every figure that comes from the planar simulation (see its limits).
