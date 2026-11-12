# Handover: where the project stands (sections 1 to 10: end of the first session, 2026-11-10; sections 11 to 13: 2026-11-11)

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
- **Wheel (`docs/wheel-spec.md`, fitted to the silver photo and checked by projecting the CAD back onto it):** a cone (apex about 10 mm above the rim) on a smooth hollow cylinder carrying 16 grousers in a helix: thin blades standing radially, serrated along their edges, 43.5 degrees from the axle, handedness alternating (front and rear opposite on a side, the other side mirrored; owner, from the photos and confirmed on the side-by-side render). Scaled to the papers' 65 mm over the grousers in the CAD (measured 59 mm).
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
5. The drivetrain work of 2026-11-11 is in sections 11 and 12; **the body redesign is under way in section 13** (carbon; layout and cavity model done, parts and derivation not).

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

1. **The body redesign** (started late on 2026-11-11: see section 13). Requirements it now has to meet: a mass of about 386 g with electronics and cells, the hub holes opened to 24.2 mm, room for four servos (45.2 x 24.7 x 32 mm, positions in `hub.py`) and the batteryless electronics, the centre of mass near the hub axis (the simulation's tip-over numbers assume it).
2. **Servo dimensions (checked 2026-11-11):** measured on the Feetech page 6 drawing, the shaft is 10.2 mm from the end of the long side (was 10.7 by eye; `hub.py` updated) and the 32 mm body height is a printed dimension. Still from a drawing, not a part.
3. **Smaller strut servos:** the load is low enough (0.17 N.m maximum hold) that a 3 to 5 kg.cm class servo could do; none was chosen. Dynamic loads are not simulated, so test before shrinking.
4. **Details not modelled:** gear teeth and backlash, how the pinion, the horn adapter, the wheel and the spindle tubes are fixed, a coupling of the right length (7.5 mm is tight), seals against dust on every shaft, strut stops, wiring, the shaft retainers, and the thermal paste or adhesive in the strut bores.
5. **Simulation extensions:** both struts moving together, momentum in the rolls, friction, steps and slopes (the handover asked for step climbing), the hop (JPL's 10 cm/s), and side-to-side tipping.
6. **Tests to do on a first print or prototype:** whether the STS3215 holds its position unpowered and how warm it runs at the hold torque; the #3068's temperature at the slope load; the wheel's stiffness at 0.8 mm walls; the gear mesh with printed against metal gears.
7. Older open items still stand: which unit to replicate, the banded-wheel option, the headlamp and window, the lid screws, and the research leads in section 9.
8. **Not verified:** the maxon price (owner's report), bearing masses and ratings (typical values), the servo's overload protection and torque limit register, prices and stock of every part, and every figure that comes from the planar simulation (see its limits).

## 13. The body redesign session, 2026-11-11 evening (what was decided, built and found)

**Where to start:** read `docs/body-redesign.md` (the long record, with sources and caveats), then run `hardware/body/layout.py` and `hardware/body/block.py` (venv; `layout.py` first). The old Hammond-box body (`hardware/body/body.py`, `docs/body-spec.md`) is untouched and still what `hardware/assembly/rover.py` builds.

**Small closed items from the same session**
- **Wheel handedness (owner, from the photos, confirmed on the side-by-side `photo_compare.py` render):** front and rear wheels on a side are opposite, the other side mirrored (`wheel-spec.md`; the CAD does this). My own read of the black unit's front-right wheel disagreed; treated as a misread, not resolved by the silver-photo render.
- **STS3215 dimensions:** the shaft is **10.2 mm** from the chamfered end of the long side (measured in pixels on Feetech's page 6 drawing against the 45.23 mm label, checked against the 12.5 mm label; the earlier by-eye 10.7 was 0.5 mm off); the 32 mm body height is a printed dimension. `hub.py` uses 10.2. The drawing is stretched about 1.18 times along the long side, so only that axis was used. Still a drawing, not a part.

**Owner's decisions (all in `CLAUDE.md`)**
1. **Body material: carbon fibre or forged carbon, 140 x 140 x 60 mm** (papers' size; reference unit still undecided). **The woven-versus-forged choice is deferred** until the interior has real parts in it.
2. **Edges: consumer-product crispness**, about 0.5 to 1 mm radius, "completely rectilinear".
3. **Top and bottom faces are identical removable lids carrying solar cells** (upside-down operation); cells also on both end faces; none on the hub faces. **The body is symmetric about the transverse (z = 30) plane.**
4. **Camera window** centred on a 60 x 60 mm square at one end of an end face (x = +40, z = 30 on the +y face); **camera and lamp share one window through a beamsplitter**; **antenna on the opposite end face at the diagonally opposite position (x = -40, z = 30 on the -y face)**, a whip standing up in the plane of the face from a **gravity-oriented pivot with a counterweight**. These depart on purpose from all three descriptions of the original.
5. **Design method: the body as a solid block with cavities cut out** (`block.py`); both a bonded-tub chassis and a forged unibody are to be derived from it once the components are specified.
6. **Purchasing is deferred indefinitely**, so no bench tests.

**What was found (sources, assumptions and caveats are in `body-redesign.md`)**
- **Woven versus forged (sourced from vendor pages, untested data):** strength and heat do not decide it: the hub loads on a 1 mm wall are 0.2 to 4 MPa against about 190 MPa for even standard forged carbon, and servo heat is about a 1.6 K rise. Standard forged needs about 16% more wall for the same panel stiffness. Easy Composites calls 1.5 mm "very much towards the lower limit" for forged. A deep 1 mm tub is the hard case for forged; layup over a plug leaves 1.5 to 3 mm corners, which fails the crisp-edge requirement.
- **Recommendation so far (mine, not the owner's decision): six woven 1.0 mm plates bonded into a box** (four walls plus two identical lids), edges hand-broken to 0.5 to 1 mm, cut edges sealed, bonded keys at the edges (about 28 g with adhesive, estimated). Forged is worth revisiting only for integral bosses or the lid, if a proper mould becomes available. **Cost (printed-mould forged against plates):** for one body the ranges overlap ($173 to $531 plates, $137 to $1,173 forged); forged wins only from about 4 to 5 bodies; the assumptions that drive it (mould life, scrap, press, cutting price) are mine.
- **Power** (`power_budget.py`): one lit face gives about **2.5 W in full sun, 0.26 W in thin overcast, about 1 to 1.3 mW indoors** (the indoor figures come from a search summary and are unconfirmed). The controller with its radio idle uses 0.105 W, camera plus radio plus lamp 1.26 W, driving 2.9 W, posing a strut 4.5 W. So the cells charge or run the camera and radio outdoors only; indoors they can run just a micro-power keep-alive. Suggested architecture (mine): a keep-alive controller on the cells, the battery behind a load switch, cells topping up outdoors. **Servo hold current (6 to 60 mA each by source) is the biggest unknown and lever**; whether the STS3215 holds a pose unpowered is still untested.
- **Layout** (`layout.py`, placeholders): keep-in volume = the envelope pulled in 2.5 mm, minus 6 mm edge strips; 818 cm3 free around the servos and hub, **placeholders use 14%: volume is not the constraint, mass is.** The 386 g budget: shell 141 g (plates) or 164 g (forged 1.5 mm) + rings and screws 32 + seal 15 + electronics 100 (boards, battery, camera, beamsplitter plate, lamp, antenna pivot, wiring) + cells 47 to 109 g (**no cell chosen; this is the biggest unknown**). Plates fit unless cells are heavy; **forged at 1.5 mm is 3 g over at middle cell weight.** Centre of mass: x +0.3, z 30.0 mm; whole-rover y about -1.7 mm (the simulation had -2.9; shifting the boards about 10 mm toward +y would centre it). **The chassis simulation has not been re-run with these changes.**
- **Cells:** top and bottom use the black unit's measured layout (10 large 39.6 x 23.5 mm, 4 centre 19.6 x 44 mm: 127.6 cm2 per face); each end face fits three cells standing in the 80 x 60 mm beside the window or antenna (27.9 cm2, my choice); 311 cm2 in all.
- **Block** (`block.py`): 33 cavities cut as CAD; 867 cm3 remains (about 1.34 kg if solid). Almost everything is 11 to 24 mm from the outside, so a lined cavity needs its own skin. **Lining every cavity does not fit the budget** (441 to 503 g total at 1.0 mm woven; forged 1.5 mm is worse); lining only the outside plus the servo group, camera group and antenna pivot gives 378 to 440 g. The rule for deriving the part decides the mass.

**Problems found, none a blocker (details in `body-redesign.md`)**
- *Antenna pendulum:* the counterweight must over-balance the whip (a balanced pivot stays where left); it only corrects roll about its own axis (the y-axis), not body pitch; it needs a rotary RF joint or a limited-turn cable, some damping, and the whip must survive the end-over-end righting rolls. The antenna may be a dummy.
- *Beamsplitter:* a 50/50 plate costs about one stop of ambient light and about double the lamp power, and **lamp light reflecting off the window pane goes straight back into the camera** (the biggest optical risk, untested): crossed polarisers, anti-reflection glass, a baffle and a wedged plate are the remedies. A plate is about 3 g; a 25 mm cube about 39 g (my estimate).
- *Two lids:* a removed lid takes its board with it, so a board-to-board link and connector at a shared lid joint are needed; lid screws and gaskets double; cells on carbon need an insulating layer.
- *Carbon in general:* it blocks RF and conducts (antenna window, insulation under cells and boards), and touching aluminium it corrodes the aluminium (insulating washers at the hub rings).

**Open decisions (owner)**
1. Woven plates or forged (deferred on purpose); layup tub ruled out by the crisp-edge requirement unless corners of 1.5 to 3 mm are accepted.
2. **Which cavities become structural linings or tubs** (mine: only the servo group, the camera and window group and the antenna pivot) and **whether to test servo mounting on two or three bulkhead plates** instead of pockets.
3. The cells (type, mass per cm2, indoor or outdoor use), the battery and voltage, the boards, the camera, the lamp and the radio: all placeholders now.
4. The lid joint (which faces are shared, the connector), the antenna (real or a dummy), and the old items still open (reference unit, banded wheel, purpose).

**Next steps (in order)**
1. Choose or specify the placeholder components (cells first, since they swing the mass by 62 g); replace the placeholders in `layout.py`.
2. Re-cut `block.py` with the specified parts, the wiring channels, the lid joint and the bulkhead variant; derive the tub chassis (walls, lids, small tubs) and the forged unibody (cores and mould) from it; re-run the cost and mass comparisons (`cf_cost.py`, `cf_compare.py`, `layout.py`) with real wall thickness, mount count and mass.
3. Re-run the chassis simulation (`hardware/drivetrain/chassis_sim.py`) with the new mass distribution (it assumes a 386 g lump at the centre).
4. Prototype tests, when purchasing resumes: servo hold unpowered, servo and wheel-motor temperatures, the beamsplitter glare, one pressed forged corner or lid.

**Not verified:** every price, density and efficiency from a vendor or search page (listed in `body-redesign.md`); the forged-carbon strength figures (a vendor's untested comparison); the indoor cell output figures; the radio, camera and lamp power; all component sizes and masses in `layout.py`; the 1 mm voxel analyses (coarse); and the cost model, which is dominated by assumptions.

**Working conventions this session:** left and right are the viewer's (the top-view picture in `body-redesign.md` says which way it is drawn); commits end with the attribution lines; push only when the owner asks; nothing from the private repo is copied here.
