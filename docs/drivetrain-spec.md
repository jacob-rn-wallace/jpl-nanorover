# Drivetrain

**Decided (owner, 2026-11-11): layout C.** Thin-walled aluminium wheels with the wheel motor (maxon ECX SPEED 10 M with a GPX 10 A 4-stage 256:1 gearhead) inside each wheel, fixed to the strut tip with its tail poking inboard; strut motors (EC-max 16 5 W with GP 16 C 1621:1) in the body, 1.0 kg design mass, drive speed about 40 mm/s. The belt layouts 2a, 2b and the friction-pivot layout 3 were studied and not taken (see "Layout comparison"). Datasheet checks, the shaft pad and the strut-tip mounting are still to do.

Record for `hardware/drivetrain/torque_budget.py` (plain Python, no CAD). Started 2026-11-11, following handover section 9, step 1.

## Requirement (owner, 2026-11-11)

**The replica must be able to lift itself under Earth gravity.** This is a functional requirement, not a replica of the original's asteroid job. It makes the strut motors the main drivetrain design problem.

**Design mass (owner, 2026-11-11): 1.0 kg exactly, total, including motors and electronics**, to simplify the performance figures. The papers say 1.3 kg and the current CAD is about 1.46 kg before motors; the owner intends to redesign the body later (deferred), which is what makes 1.0 kg reachable. Until then 1.0 kg is a target, not a modelled mass.

What it implies (from `torque_budget.py`, margin x2, 70 mm struts): at 1.0 kg a strut needs about 0.31 N.m to hold the body and about 0.69 N.m for a one-pair push, which is about 4.5 mN.m at the motor through a 256:1 gearhead at 60 %. That is roughly seven times the assumed 0.6 mN.m of a 10 g motor, so the papers' motors do not meet the requirement and the strut motors will be bigger than the hub as modelled. Mass matters linearly: each 100 g removed saves about 0.07 N.m on the push (with the margin).

Levers, to be decided: larger or higher-ratio strut motors (and a bigger hub); a non-backdriving stage (worm or lead screw) so holding is free; mass cut (the cast Hammond box is the heavy part); a dynamic flip for righting instead of a quasi-static push. Any change to the hub or strut motors breaks the "papers' 10 g motors" match, so record it as a deliberate deviation.

## Torque and speed budget (first pass, quasi-static)

Sourced inputs: 70 mm struts, 65 mm wheels, 1.5 mm/s rolling, 256:1 gearheads, two ~10 g brushless motors per strut (papers; one source, see the bibliography). Mass is the 1.0 kg design mass. The 25 degree stance is a choice. **The motor torque (0.6 mN.m continuous at the motor, 60 % gearhead efficiency) is an assumption, not a datasheet or paper value.**

| Load (Earth, 1.0 kg, no margin) | Needed at the output | vs. assumed 92 mN.m |
|---|---|---|
| Strut, hold body at 25 degree stance | 156 mN.m | 1.7 x |
| Strut, arms horizontal | 172 mN.m | 1.9 x |
| Strut, whole weight on one pair (righting upper bound) | 343 mN.m | 3.7 x |
| Wheel, 20 degree slope | 27 mN.m | 0.3 x |
| Wheel, step of R/2 (front pair carries all) | 138 mN.m | 1.5 x |
| Wheel speed at 1.5 mm/s | 0.44 rpm (113 rpm at the motor) | easy |

## What it says

- **On an asteroid the loads are negligible** (about 1e-4 g, assumed): the original's motors were sized by speed, friction and the gearhead, not by lifting. The replica on Earth is a different problem, about 10^4 times heavier, so the Earth numbers are the ones that matter for a build.
- **Wheels are fine; struts are not.** With 10 g motors the wheel drive works on slopes, but holding the body up on the struts needs about 1.7 times the assumed output, and a one-pair push for self-righting about 3.7 times (before margin). The handover estimated about 0.25 N.m per strut at 1.3 to 1.5 kg.
- **Options to close the gap** (none chosen): larger strut motors (which may not fit a 26 mm hub as modelled); a lower stance geometry or a worm/non-backdriving stage so holding costs no power; lighter body (the cast box is the heavy part); or accept low-gravity-style operation, with the body lifted only slowly and righting done as a dynamic flip (as the 1997 video suggests) instead of a push.
- Hopping at 10 cm/s (papers) is a separate, energy-storage question and is not covered here.

## Not done

Dynamic and kinematic simulation, motor selection from real datasheets, the hub and bearing design, strut stops, and a worm-gear option. Next in the handover list: step 2, the kinematic simulation.

## Strut motor candidates (maxon catalogue 2025/26, read 2026-11-11)

Need (1.0 kg, margin x2): 0.31 N.m continuous to hold, 0.69 N.m peak for a one-pair push. Figures are from maxon catalogue pages 279 and 281 (EC-max 16), 416 and 417 (GP 16 A, GP 16 C) and 381 (GPX 16), read from the PDFs on 2026-11-11. Prices, stock and the exact motor and gearhead pairing are **not checked**.

**Chosen for now: maxon EC-max 16, 5 W, 6 V (283826) with a GP 16 C, 5-stage, 1621:1.**
- Motor: 16 mm, 36 g, about 24 mm long (the catalogue's 39.6 mm is motor plus a 1-stage GP 16 A; the overall-length tables give 24.0 mm for the motor), 3.2 mN.m nominal, 5.79 mN.m stall, 3.9 mN.m/A, 4.04 ohm phase to phase, Hall sensors.
- Gearhead (ceramic): 0.6 N.m continuous, 0.9 N.m intermittent, 59 % efficient, 37 g, 33.9 mm, backlash about 3 degrees, ball bearing output. Together 73 g and 57.9 mm overall (catalogue length table).
- At the 0.69 N.m peak the motor sees only 0.72 mN.m, so the motor is oversized for torque; the gearhead is the limit. Output speed at nominal about 3.5 rpm, so a 90 degree strut move takes about 4 s.
- **Holding costs almost nothing at this ratio:** a planetary at 59 to 73 % efficiency is backdrivable, so the motor must hold the body, but copper loss falls with the square of the ratio: 0.03 W per strut at 1621:1 (0.11 W for four), against 0.44 W per strut (1.8 W for four) at 370:1, which is most of the papers' 2.3 W. So the high ratio also removes the need for a worm stage or brake, at the price of speed.

| Combination (EC-max 16 5 W) | Mass | Gearhead limits (cont / int) | Motor torque at push | Output speed | Hold loss, four struts |
|---|---|---|---|---|---|
| GP 16 C 84:1 (3-stage) | 65 g | 0.40 / 0.60: fails the push | 11.2 mN.m: exceeds stall | 68 rpm | 27 W |
| GP 16 C 370:1 (4-stage) | 69 g | 0.50 / 0.75: ok | 2.9 mN.m: ok | 15 rpm | 1.8 W |
| **GP 16 C 1621:1 (5-stage)** | **73 g** | **0.60 / 0.90: ok** | **0.72 mN.m** | **3.5 rpm** | **0.11 W** |

Other findings: GP 16 A tops out at 0.30 N.m continuous and 0.45 intermittent, below the push (rejected). The GPX 16 C (page 381) reaches 0.60 continuous / 0.75 intermittent in 4 stages at 31 g (ratios 243 to 1526) and is a lighter alternative to check. The 8 W EC-max 16 (283833) is 52 g, heavier and not needed. The Pololu 25D worm and spur gearmotors from the first pass are rejected: too heavy and too large.

## Wheel (decided to do first, 2026-11-11)

**Owner decision (2026-11-11): metal wheels.** The owner expects to find the weight savings in the redesigned body instead. So the working wheel is thin-walled aluminium, 45 g each (wall 1.0, plate 1.0, cone 0.8, blades 0.8 mm), or 33 g if the thinnest machinable walls prove workable. The printed PA12 option below is not taken. With 45 g wheels the drivetrain is 660 g, leaving 340 g for the body and everything else (see the mass budget). How a 1 mm-walled aluminium wheel with helical serrated grousers is made (CNC, multi-part, or metal printing) is open.

**Mass.** `hardware/drivetrain/wheel_mass.py` estimates the wheel from the parameter block of `wheel.py` (it reproduces the CAD's 78 g to within 5 %: 83 g). Wall thicknesses and materials are assumptions; the PA12 density is a typical value, not a measured part.

| Wheel | Each | Four |
|---|---|---|
| CAD as modelled (Al, wall 2.5, cone 1.5) | 83 g | 332 g |
| Al, thin (wall 1.0, plate 1.0, cone 0.8, blades 0.8) | 45 g | 180 g |
| Al, thinnest machinable (0.8 / 0.8 / 0.6 / 0.6) | 33 g | 130 g |
| **PA12 printed (wall 1.5, plate 1.5, cone 1.2, blades 1.0)** | **23 g** | **91 g** |
| PA12 printed, thin (1.2 / 1.2 / 1.0 / 0.8) | 19 g | 77 g |

The same outline in printed plastic is about a quarter of the CAD wheel. Printed PA12 is the proposal: the look (cone, helical serrated grousers) is unchanged, it is printable as one part, and it is not the original's aluminium (a deliberate deviation; the papers' wheel is a conductor/insulator assembly anyway). A 1 mm-walled aluminium wheel is possible but needs a multi-part or metal-printed build.

**Wheel motor: maxon ECX SPEED 10 M (9 V, 12 g) with a GPX 10 A 4-stage gearhead, 256:1** (maxon catalogue pages 199 and 373, read 2026-11-11; price and stock unchecked).
- Motor: 10 mm, 25.1 mm long, 1.83 mN.m nominal, 15.6 mN.m stall, 1.42 mN.m/A, 0.82 ohm, Hall sensors, 12 g. Gearhead: 0.15 N.m continuous, 0.20 intermittent, 65 % efficient, 8.2 g, 19.8 mm, backlash 2.2 degrees, ball-bearing output. Together **20.2 g and about 45 mm.**
- Torque (1.0 kg, no margin): 27 mN.m for a 20 degree slope and 138 mN.m for a step of half the wheel radius with the front pair carrying the weight. The gearhead covers both (0.15 continuous, 0.20 intermittent); the step is within 1.45 x of the intermittent limit, so **steps should be taken by lifting the front wheels with the struts, as the original does**, with the wheels doing slopes and flat driving. At the 0.1 N.m design load the motor sees 0.6 mN.m, a third of its nominal.
- Speed: the gearhead takes at most 12 000 rpm in, so 47 rpm out (about 160 mm/s) at the top. The papers' 1.5 mm/s needs 0.44 rpm at the wheel, which is 110 rpm at the motor: too slow for a hall-sensor brushless motor to run smoothly. **No drive speed has been set by the owner. The videos show about 20 to 50 mm/s** (see "Speed seen in the videos"), which is 6 to 15 rpm at the wheel and 1500 to 3900 rpm at the motor: workable.
- **Fit: the motor and gearhead are about 45 mm long, against a wheel interior of about 44.6 mm** (inner face to the cone apex, less the end plate and the apex collar). It does not fit as drawn. Options: the 3-stage 64:1 (16.6 mm, 41.7 mm total, 0.10 N.m continuous, 0.15 intermittent; fine for slopes, needs very slow motor speeds); let the gearhead end project into the strut axle stub; or widen the wheel by a few millimetres (the 34.5 mm cylinder length is a measurement, so I would not).
- The 6 mm axle and the 12 mm hub tube in `wheel.py` go away: the motor body is fixed to the strut and the wheel is attached to its output shaft. That is a change to `wheel.py` and to the strut's axle stub, **not made yet**.

## Mass budget (does 1.0 kg close?)

`torque_budget.py` adds up the drivetrain: 4 struts at 27 g (estimate), 4 strut motors at 73 g (EC-max 16 5 W with GP 16 C 1621:1), 4 wheel motors at 20 g (ECX SPEED 10 M with GPX 10), and the wheel.

| Wheel | Drivetrain | Left for body, electronics, cells, camera |
|---|---|---|
| CAD, 78 g | 792 g | 208 g |
| Al thin-walled, 45 g | 660 g | 340 g |
| **PA12 printed, 23 g** | **572 g** | **428 g** |

With the printed wheel the drivetrain is 572 g and 428 g remain. Whether that is enough depends on the redesigned body (a plastic or printed shell, a PCB base as in the black unit, small solar cells), which is not designed. For scale, the papers' 1.3 kg included a 140 x 140 x 60 mm body and 10 g motors.

## Speed seen in the videos (estimate, 2026-11-11)

Method: frames of the black unit (private repo, `video/`) were extracted at 2 per second with a pixel grid, and its position was read by eye against a fixed or slowly panning background. The scale is the rover's own size: the body about 139 mm long (the settled figure), which agrees with the wheels (about 55 to 60 mm across the grousers). Positions were read to a few pixels from contact sheets, not tracked by software. No frames are kept in this repository.

| Clip | What was measured | Speed |
|---|---|---|
| 1998 video, 1:32 to 1:40, black unit on sand, seen end-on | the body moves about 62 px/s (480 px-wide tiles) relative to the rock behind it, steadily over about 6 s; body 175 px = 139 mm, so 0.79 mm/px | **about 50 mm/s** |
| 1997 video, about 0:21 to 0:24, approach to a rock, side view | the near wheel's left edge moves 40 px per 0.5 s before it touches the rock, then 8 to 27 px per 0.5 s while climbing; wheel about 125 px = 59 mm | **about 38 mm/s approaching, about 23 mm/s averaged through the contact** |
| KTLA studio clip, about 1:35 to 1:45, wide shot | the rover moved less than 5 px of 25 px (body 139 mm) in 10 s | **under about 14 mm/s**, mostly standing still: an upper bound only |

**Result: the rover is driven at roughly 20 to 50 mm/s (2 to 5 cm/s) in the videos**, about 15 to 30 times the papers' 1.5 mm/s rolling speed. A hand-held remote drove it in the studio, and the papers' figure is a flight design value for a rover on an asteroid. At 65 mm wheels, 40 mm/s is 0.2 rev/s, or about 12 rpm at the wheel.

Caveats: the uncertainty is about plus or minus 40 %. The background rock in the 1998 clip is farther from the camera than the rover, and the camera pans, so the relative motion overstates the speed somewhat. I assume the videos run in real time and are not sped up or edited. The speeds are the demonstration speeds of a lab unit, not a specification.

**Effect on the drivetrain:** the wheel motor choice (256:1) suits this: 12 rpm at the wheel is about 3000 rpm at the motor, comfortably inside the GPX 10's 12 000 rpm input limit and smooth for a hall-sensor motor. Wheel power at 0.1 N.m and 1.2 rad/s is about 0.12 W. So the earlier assumed 5 to 20 mm/s is replaced by **a design drive speed of 40 mm/s, with a cruise range of 20 to 50 mm/s taken from the videos**, until the owner sets another.

## Option C clearance (CAD check, 2026-11-11)

`hardware/drivetrain/motor_clearance.py` (needs `.venv`, run after `body.py` and `strut.py`) puts the 10 mm x 45 mm wheel motor and gearhead in each wheel, carried by the strut tip, with the output end as far toward the cone apex as the cone's inner radius allows (|x| = 127.35 mm) less a shaft-and-hub pad, and the tail running inboard.

| Shaft pad | Tail at |x| | Tail to body face (casting rim at 69.94 mm) | Tail inboard of the wheel's inner face |
|---|---|---|---|
| 0 mm | 82.35 | 12.4 mm | 2.9 mm |
| 3 mm | 79.35 | 9.4 mm | 5.9 mm |
| 6 mm | 76.35 | 6.4 mm | 8.9 mm |

- **The struts and wheels still clear the body.** The tail stays at least 6 mm from the body face even with a 6 mm pad. The wheels and struts hang outside the body faces and never meet the body (the wheel is 15 mm outboard of the casting); only the stud flange and nuts are near the hub.
- **No new strut collisions.** One strut's motor hits the other strut of the same hub at the same 12 of 144 angle pairs (30 degree steps) as the 6 mm axle stubs do (equal angles; the struts cannot swap places, as before).
- **Not covered:** the motor's flexprint cable at the tail (about 4 mm), a finer angle step than 30 degrees, the strut's real tip mounting (a 10 mm bore in the 18 mm tip boss leaves 4 mm of wall), and the thin-wall wheel's end plate. The motor is a plain cylinder.

## Idea: motors in the body, belts to the wheels (NPO-20057)

The Tech Brief (Wilcox and Nasif, NASA Tech Briefs NPO-20057, 1998; the page text and its figure, which is in the private repo) already uses belts, but **with the motors at the wheels**: "each wheel and its gearmotor are mounted at the free end of a strut", both gearmotors of one side drive a **single idler pulley on the pivot axis** through belts, and the struts pivot on spring-loaded friction wafers that hold a pose by static friction (torque T). The pose is changed by powering one strut's own motor to a torque of T; a gearmotor "acts as a brake when not energized". So the pulley is JPL's, but the motor location in the idea is new.

Findings so far (analysis, not CAD):
- **The belt length stays constant** if the drive pulley is on the pivot axis: the pivot-to-axle distance is a fixed 70 mm at any strut angle. A pulley anywhere else would change length with the angle.
- **Gains:** the wheel interior is free (the 45 mm motor fit problem goes away and the wheel can be a plain light shell); motors can be larger and cheaper; a belt reduction (for example 3:1) can replace gearhead stages; the strut tip is lighter.
- **Costs:** every driven wheel needs its own drive shaft on the pivot axis, so a hub carries two strut shafts plus two drive shafts, four coaxial shafts, unless the wheels of one side share one idler as JPL did (then one drive motor per side and the two wheels of a side always turn together: skid steering). Belts and pulleys add mass and bearing load, need tension, and run in dust. The mass is not saved: the motors still weigh the same, only in the body.
- **Possible bigger win, not analysed:** JPL's friction-pivot posing means holding is free and needs no separate strut motors, but the motor that turns a strut must then deliver the full friction torque T, which for the 1 kg rover is 0.3 to 0.7 N.m. That is strut-motor size, not wheel-motor size, so it would trade 8 small motors for 4 big ones plus friction discs.

## Layout comparison (2026-11-11; `hardware/drivetrain/layouts.py`, analysis only, no CAD)

**Owner's concern (correct):** changing the stance moves the two wheels of a side toward or away from each other, so they must roll in opposite directions. With a shared idler and open belts of equal pulleys the belt kinematics give each wheel's absolute rotation equal to the idler's, so the two wheels of a side can only turn together. A stance change then has to **scrub** the wheels across the ground. JPL's design lives with that in microgravity; on Earth it is a real load: with an assumed friction coefficient of 0.6, a wheel sliding under 2.45 N at a hub height of 62 mm costs about **0.09 N.m per strut** (the hold load is 0.34 N.m with margin).

| Layout | Motors (strut + wheel) | Drivetrain | Left of 1 kg | Coaxial shafts per hub | Wheels can roll apart |
|---|---|---|---|---|---|
| C: wheel motors in the wheels, strut motors in the body (now) | 4 + 4 | 661 g | 339 g | 2 | yes |
| 2a: all motors in the body, one belt per wheel | 4 + 4 | 705 g | 295 g | 4 | yes |
| 2b: one drive motor per side, shared idler | 4 + 2 | 754 g | 246 g | 3 | **no** |
| 3: JPL friction pivots, big motors at the strut tips, shared idler | 4 | 624 g | 376 g | 3 | **no** |

The belt, pulley, bearing and friction-disc masses are my assumptions (11 g per wheel set; 24 g per side for a shared idler; 30 g per side for the friction layout). Motor masses are catalogue figures.

- **2a** gives up 44 g to belts and gains a free wheel interior (no 45 mm motor fit, no tip motor mount) and the freedom to use any motor in the body. It is the only belt layout that keeps independent wheel rolling. Cost: four coaxial shafts per hub (two strut, two drive).
- **2b** is JPL's belt layout with body motors. It is the heaviest and loses independent rolling, so a stance change scrubs. **Not recommended.** A differential in the idler would restore counter-rolling at more mass and complexity (not analysed).
- **3** is the lightest and holds pose for free, but: (a) it works only with the motor **at the strut tip**, because the strut must be turned by the reaction torque of its own motor; a body motor with a belt along the strut gives no moment about the pivot; (b) the motor must deliver the friction torque, so each tip motor is a 16 mm class unit (EC-max 16 5 W with GP 16 C 4-stage 370:1, 69 g, 54.4 mm overall, 0.50 N.m continuous, 0.75 intermittent), which fits inside the wheel only just: with its front at the cone's 8 mm inner radius (|x| = 126.3) the tail reaches |x| = 71.9, **2.0 mm from the body face**; (c) with the wheels forced to scrub, lifting needs friction torque T (0.35 N.m, 2.0 x the worst static load) + the one-pair push (0.34) + scrub (0.09) = **0.78 N.m against the gearhead's 0.75 N.m intermittent: 5 % short**. A 5-stage gearhead (0.90 N.m) would pass but drives the wheels at only 3.5 rpm (11 mm/s), against about 40 mm/s seen in the videos. Without the scrub (wheels free to roll) it would pass with 0.69 N.m. Driving at the step load (0.138 N.m) does not slip the pivot (0.138 < 0.18).

**Assessment.** Layout 3 saves 37 g over C but is marginal on Earth and needs the 2 mm fit; layout 2b is dominated; layout 2a costs 44 g over C and buys a free wheel interior. **C remains the simplest layout that meets the requirement, 2a is the alternative if the wheel interior is wanted, and 3 is a lighter option only for a rover that can scrub (low gravity or low friction).** The choice does not change the strut motors' sizing in C and 2a.

## Hub sizing

- **Shafts are not the constraint.** A 6 mm steel shaft at 0.69 N.m sees about 16 MPa of shear. The envelope of the motors is the constraint.
- **Layout implied (a proposal, not built):** the current stationary stud with an axle stub (`strut-spec.md`) cannot be driven. Replace it with two **coaxial rotating shafts**, an inner shaft for one strut and a hollow outer shaft for the other, each through a bearing in the wall, each with its own motor inside the body, parallel to the axis and offset along the long dimension (y) by about 20 to 25 mm, with a spur reduction to the shaft and a potentiometer on each shaft (the papers put potentiometers in the shoulder hub). Motors offset in z would not fit: the interior is only about 50 mm tall, so two 25 mm motors would touch.
- **Envelope check still to do:** two 16 mm motors (about 40 to 50 mm long each) per hub fit the 140 mm width and about 50 mm interior height; 25 mm motors fit in height only barely. This needs a CAD check against the casting's corner bosses once the body redesign settles.
- A worm stage on the strut shaft would give free holding, but the packaging needs its own study.

## Next

Set the drive speed (owner), resolve the wheel motor fit, update `wheel.py` (parameters for material, wall thicknesses, no hub tube) and the strut axle stub, check the GPX 16 C alternative for the struts, then model the coaxial hub in CAD around the 16 mm x 58 mm motor and gearhead. Wheel motors and the real kinematic simulation are separate steps.
