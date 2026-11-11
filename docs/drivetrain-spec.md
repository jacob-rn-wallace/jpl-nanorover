# Drivetrain

**Decided (owner, 2026-11-11): layout C.** Thin-walled aluminium wheels with the wheel motor inside each wheel, clamped in a slot in the strut tip so the strut is its heat sink; strut motors in the body; 1.0 kg design mass; drive speed about 40 mm/s. **Motors, after the cost review: Pololu #3068 for the wheels (in the CAD) and Feetech ST3215 for the struts (not yet in the CAD); the maxon parts of the earlier sections are superseded on cost.** The belt layouts 2a, 2b and the friction-pivot layout 3 were studied and not taken (see "Layout comparison"). Datasheet checks, the shaft pad and the strut-tip mounting are still to do. **The motor choice is reopened on cost (owner, 2026-11-11): maxon's motors are over $200 each; see "Motor cost" below. Nothing is decided; the CAD still shows the maxon wheel motor.**

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

## Option C in the CAD (2026-11-11)

Layout C is modelled with the **Pololu #3068** wheel motor and a **wheel support**: `wheel.py` preset `thin` (33 g wheels, 20.5 mm end-plate hole), `strut.py` `TIP_MODE = "motor"` (23 g struts, 24 mm tip boss, a 19.1 mm bore) with the wheel drive (motor box, assumed coupling, 3 mm stub shaft), a 19 mm spindle tube with barrel (9.7 g each) and two 3 x 8 x 4 mm bearings per wheel, and `assembly/rover.py` counts them. The whole model is **1351 g** (954 g of it the Hammond box and lid plate, to be redesigned), with the wheel drive and supports and no strut motors, wiring or electronics.

**Mass with the support:** wheel drive 50 g (motors 9.5 g + coupling 1.0 g + stub shaft 1.9 g, four), spindles 39 g, bearings 5 g, wheels 133 g, struts 93 g: 320 g; with four Feetech ST3215 struts (276 g) the drivetrain is 596 g, **leaving about 404 g of the 1.0 kg** for the body, electronics, cells and camera (462 g before the support was designed). The spindle tubes are the largest addition; a 0.6 mm wall would save about 18 g.

The support design and its loads are in `strut-spec.md` ("Wheel support"). Not modelled: the strut motors (Feetech ST3215, 45.2 x 24.7 x 35 mm, in the body), the coaxial hub, how the wheel and tube are retained, and the real coupling.

## Option C clearance (CAD check, 2026-11-11, Pololu #3068 with its spindle)

`hardware/drivetrain/motor_clearance.py` (needs `.venv`, run after `body.py`): the motor (10 x 12 x 25 mm) has its tail at |x| = 77.25 (the inboard face of strut A's plate) and its front at 102.25, inside a 19 mm spindle tube that runs to |x| = 113.5 and a barrel to 124.8.

- **The struts and wheels clear the body.** The tail is **7.3 mm from the body face** (casting rim at 69.94 mm) and 8.0 mm inboard of the wheel's inner face; the wheels sit 15 mm outboard of the casting.
- **No strut collisions from the wheel support:** one strut's motor, tube and bearings against the other strut gives 0 of 144 angle pairs (30 degree steps). `strut.py` with both supports included finds the same 12 equal-angle pairs as before (two wheels in the same place, impossible anyway). The tube lies in the other strut's layer, so it would meet that strut when the two point within about 20 degrees of each other; the wheels collide first (within about 55 degrees).
- **Not covered:** a finer angle step, the retention of the tube and wheel, the coupling's real size, the cable.
- (The earlier maxon motor, 10 mm x 45 mm, is superseded.)

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

## Motor cost (2026-11-11, open)

The owner found the maxon motors to be **over $200 each** on maxon's website (not checked by me), so eight would be $1,600 or more. `hardware/drivetrain/motor_options.py` compares hobby-grade parts against the same loads. Sources and the assumed items are listed at its top.

| Role | Option | Mass | Price each | Capability against the 1.0 kg loads |
|---|---|---|---|---|
| Strut | maxon EC-max 16 5 W + GP 16 C 1621:1 (now) | 73 g | over $200 (owner) | 0.90 N.m intermittent, 0.60 continuous: 2.6 x the 0.34 N.m push |
| Strut | **Feetech ST3215, 12 V** (bus servo, 345:1 metal gears, 360 degree 12-bit magnetic encoder, continuous mode) | 55 to 69 g (sources differ) | about $17 to $28 (other sellers up to $49) | 30 kg.cm locked rotor = 2.9 N.m, 10 kg.cm rated (retailer): 8.6 x peak, 2.9 x rated |
| Strut | Feetech ST3215, 7.4 V version | same | same | 19.5 kg.cm = 1.9 N.m: 5.6 x peak, 1.9 x rated |
| Wheel | maxon ECX SPEED 10 M + GPX 10 A 256:1 (now) | 20.2 g | not looked up, expected high | 0.15 / 0.20 N.m |
| Wheel | **Pololu 1000:1 micro metal gearmotor HPCB 12 V (#3046)** | 10.5 g | $37.95 | stall 10 kg.cm; 2.1 kg.cm (0.21 N.m) at best efficiency, 25 %; at 0.138 N.m about 30 rpm (102 mm/s) at 12 V, so run it at about 35 % duty for the 40 mm/s design speed |

What it says:
- **The cheap set meets every load.** Four ST3215 and four Pololu motors cost about **$220 to $264** (4 x $17 to $28 plus 4 x $37.95) against $1,600 or more, and weigh less: drivetrain 542 g against 597 g, leaving 458 g of the 1.0 kg instead of 403 g. Controllers, drivers, a servo bus adapter and wiring are **not priced**.
- **Holding costs more than with the maxon gearing but stays small:** at the 25 degree stance a strut holds 0.156 N.m, which is about 0.09 W of copper loss per strut (12 V version, from the servo's stall current and kt; 0.12 W for the 7.4 V version) against 0.03 W for the 1621:1 maxon. Four struts are about 0.4 W, plus the servos' idle current (not found). That matters for the solar goal but is not prohibitive.
- **Fit changes (superseded by the wheel support design):** the Pololu motor is 10 x 12 mm and 25 to 28.5 mm long and fits inside the wheel with room to spare. The bore in the strut tip is now 19.1 mm round (for the spindle tube that carries the motor and the wheel bearings) in a 24 mm tip boss, not the 15.8 mm bore in a 22 mm boss considered here. The ST3215 is 45.2 x 24.7 x 35 mm with its shaft off-centre; two of them per hub in the body still need the coaxial shaft design.
- **Unchecked:** the servo's mass and its rated torque (sources differ), whether it backdrives when unpowered, the lifetime of an HPCB micro metal gearbox under a 0.1 N.m continuous load (Pololu gives no continuous rating), and what the maxon wheel motor costs.

### Pololu #3068 against #3046 for the wheels (owner's question, 2026-11-11)

Read from Pololu's spec and FAQ pages: **#3068, 250:1 HPCB 6 V: 10 x 12 x 25 mm (plus a 10 mm shaft), 9.5 g, 130 rpm at 6 V, 0.15 A no load, stall 3.2 kg.cm (0.314 N.m) at 1.5 A (theoretical), best efficiency 0.66 kg.cm at 100 rpm (29 %), $26.45 each** ($24.33 for 5, $22.39 for 25). The page gives no continuous torque limit; Pololu's FAQ says to keep continuous loads at about 25 % of stall or less, which is 0.078 N.m here (and 0.245 N.m for the #3046). Stalling can damage the gears or windings within seconds.

| Load (1.0 kg) | N.m | % of #3068 stall | % of #3046 stall |
|---|---|---|---|
| 20 degree slope | 0.027 | 9 % | 3 % |
| slope with margin x2 | 0.054 | 17 % | 6 % |
| 0.1 N.m (the earlier design load) | 0.100 | **32 %: over the 25 % guideline** | 10 % |
| half-radius step | 0.138 | **44 %: over** | 14 % |

- **The #3068 is lighter (9.5 g against 10.5 g) and cheaper ($26.45 against $37.95, saving $46 for four) and handles the realistic wheel loads:** flat driving needs only about 0.002 to 0.004 N.m (rolling resistance, my estimate), a 20 degree slope is 9 % of stall and a slope with margin 17 %. At 12 rpm (about 40 mm/s) it needs about 18 to 26 % duty on those loads.
- **It is marginal only for the loads I set as design margin:** 0.1 N.m (32 %) and the step (44 %), which are above the guideline for continuous use. Steps are meant to be taken by the struts lifting the front wheels, so the wheels should rarely see them, and a brief excursion is not the continuous rating. The #3046 has about 3 times the headroom (all four loads within 14 % of stall) for $11.50 more each, and it would last longer under repeated load.
- **Fit:** the same 10 x 12 mm profile, 3 mm shaft and a slightly shorter body (25 mm against 28.5 mm); the strut-tip slot is the same.
- **Totals with the Feetech ST3215 struts:** #3068 about **$174 to $218**, 538 g drivetrain, 462 g left of 1 kg; #3046 about $220 to $264, 542 g, 458 g left. Controllers, drivers and wiring are not priced.
- **Recommendation: the #3068, with the rule that the wheels never push the rover against a step or stall, and a limit in firmware on motor current (about 0.5 A at 6 V, which is about a third of stall).** If a first test shows the gearbox warm or noisy at the 0.1 N.m load, swap to the #3046; the two are drop-in for each other apart from supply voltage (6 V against 12 V).

### Heating, and the struts and wheels as heat sinks (owner's question, 2026-11-11)

**What "lasts longer" means.** Pololu does not say what its 25 % of stall guideline protects. Load wears three things at once: the **windings** (heating, set by the copper loss I^2 R), the **brushes** (wear grows with current), and the **gear teeth** (stress grows with torque, and nothing but a stronger gearbox helps). A heat sink only helps the first. The #3046 spreads the same load over a gearbox rated for about three times the torque, so it is better on all three; the #3068 is limited mainly by gear stress and heat together.

**Copper loss (my estimate from the Pololu no-load and stall figures, I = I0 + (load/stall)(I stall - I0), R = V / I stall):**

| Load | #3068 (6 V) | #3046 (12 V) |
|---|---|---|
| flat driving (0.003 N.m) | 0.11 W | 0.11 W |
| 20 degree slope (0.027) | 0.28 W | 0.16 W |
| slope with margin x2 (0.054) | 0.58 W | 0.22 W |
| 0.1 N.m | 1.35 W | 0.35 W |
| half-radius step (0.138) | 2.2 W | 0.49 W |

**Heat paths (all my rough estimates: natural convection h = 10 W/m2K, 6061 aluminium, stainless stud; no measurement).**
- The motor alone in still air inside the closed wheel: about 75 K/W from its can area. At 0.6 W that is about 48 K above ambient on the can, with the winding hotter, and at 1.35 W about 100 K. That is why the guideline exists.
- **The strut is a good heat sink.** The motor is clamped in a bore in the aluminium strut tip. From there the arm conducts about 7 K/W to the hub and loses heat by convection from both faces (about 30 K/W to air); the pivot (a 12 mm stainless stud) adds about 8 K/W to the body. Together about **10 K/W, roughly 7 times better**: 0.6 W gives about 6 K on the can, 1.35 W about 14 K. The winding runs hotter than the can by an amount I could not find (the motor's internal thermal resistance).
- **The wheel is not a usable sink.** The only solid path from the motor to the wheel is the 3 mm steel output shaft, about 34 K/W (the wheel and motor rotate relative to each other, so a large contact is not possible). The wheel's large outer surface would cool well, but the heat cannot get there.
- **Design consequences:** keep the strut tips aluminium (not plastic), fit the motor into the bore with thermal paste or adhesive (about 0.05 mm of clearance now), keep the arm plate wide near the tip, and note that the body is a poor extra sink if the redesigned body is plastic. In vacuum only conduction counts, which the strut still provides; this is a feature of putting the motor on the strut tip.
- **Struts' own servos:** holding at the stance costs about 0.09 W of copper loss per servo (earlier section) and a one-pair push about 0.44 W briefly, so heating is not the issue for them; stalling is (the servo has overload protection, not checked).

### Brushed 130-size hobby motors for the wheels (owner's question, 2026-11-11)

Data: only third-party listings were found, no Mabuchi datasheet. RF-130 (6 V): 8,100 rpm no load, 36 mA no load, 0.70 A stall, starting torque 42 g.cm (4.1 mN.m, my conversion), 18 g. The can is about 20 x 15 x 25 mm (**my recollection, not found**). The Tamiya FA-130 on Pololu's page is a different motor (3 V). No sourced 130-size gearbox was found.

Estimate (my arithmetic, for a gearbox I assume at 250:1 and 40 to 50 % efficient, or 500:1 at 30 %): a 0.1 N.m wheel load needs about 0.7 to 1.0 mN.m at the motor, which is a quarter of its stall torque, about 0.2 A and 0.2 to 0.3 W of copper loss; the wheel then turns 14 to 26 rpm (46 to 89 mm/s), so the 12 rpm design speed is reached at reduced voltage. A half-radius step (0.138 N.m) needs 0.9 to 1.4 mN.m and 0.3 to 0.6 W: briefly acceptable, above what a 130 motor is usually rated to run continuously (not checked).

| | RF-130 + 250:1 plastic or metal gearbox | Pololu #3046 (10.5 g gearmotor) |
|---|---|---|
| Cost | motor about $1 to $3 (not looked up), a gearbox $5 to $15 (not looked up): roughly $10 to $15 | $37.95 |
| Mass | 18 g + gearbox about 20 to 30 g = about 40 to 50 g | 10.5 g |
| Four wheels | about 160 to 200 g | 42 g |
| Size | about 20 x 15 mm, 25 mm plus the gearbox, so about 50 mm or more long | 10 x 12 x 28.5 mm |
| Risk | gearbox must be found or built; plastic gears at 250:1 are noisy, loose (backlash) and wear | gearbox included |

Conclusion: a 130 motor can drive the wheels, but only with a gearbox of about 250:1 that I could not source, and it **saves roughly $100 for all four wheels at the cost of about 120 to 160 g** of the 1.0 kg budget (leaving about 300 g instead of 458 g) and a bigger bore (about 21 mm across) in the strut tip. The Pololu gearmotor is smaller, lighter and complete. The 130 route is worth it only if the cost per wheel motor must be under about $15. A cheaper Pololu part in the same family (for example the 250:1 HPCB 6 V, #3068, 9.5 g, 130 rpm at 6 V, stall 3.2 kg.cm = 0.31 N.m) would also reach the 0.1 N.m load (a third of its stall torque); its price was not looked up.

### Custom PCB-stator motor (owner's idea, 2026-11-11)

Measured data found: one research motor (Carnegie Mellon and Microbot, arXiv 2509.23561): 19 mm outside diameter, 6 mm thick, a **48-layer** stator of stacked HDI boards **with a steel core**, reported at 30.7 mN.m at 2000 rpm (whether that is peak or continuous was not clear from the snippets). A hobby 4-layer board cannot reproduce that, and the paper itself says low copper fill (under 35 %) gives high resistance and poor continuous torque. No measured data for an ordinary 4-layer board was found.

**My own first-principles estimate (order of magnitude, plus or minus a factor of 3; every input assumed):** a double-rotor, coreless stator of 50 mm outside and 20 mm inside diameter in the wheel (it fits the 57 mm interior), 4 layers of 1 oz copper, 12 coils of 8 turns per layer, 0.15 mm traces, N52 magnets of about 3 mm with steel back plates (0.4 T in the gap), 10 A/mm2 continuous. Result: Kt about 43 mN.m/A, about 33 ohm, about 52 mA and **about 2.3 mN.m continuous** (0.09 W of copper loss), no-load speed about 2,700 rpm at 12 V. The wheel's 0.1 N.m load then needs a reduction of about 100:1 (0.14 N.m continuous at 60 % efficiency); the struts' 0.34 to 0.69 N.m would need about 300:1 and a bigger or thicker stator.

| | PCB motor + about 100:1 reduction (wheel) | Pololu #3046 |
|---|---|---|
| Mass | about 70 g (board 6 g, 24 magnets 15 g, two 1 mm steel back plates about 26 g, shaft and bearings 5 g, printed reduction about 18 g); about 40 g with no back iron but half the torque | 10.5 g |
| Cost | board, magnets, bearings about $10 to $20; plus a three-phase driver (about $10 to $20) and sensing | $37.95 complete |
| Effort | motor design, windings, magnet fixture, reduction gear, commutation firmware | none |

Conclusion: **it does not beat the bought gearmotor on mass, cost or effort**, because a PCB stator is a low-torque, high-speed motor and the missing torque has to come from a custom reduction gear, which is where the mass and work go. Its real advantages are integration (Hall sensors and the driver on the same board) and being a custom, open, printable part. It is a reasonable later R&D project for the wheels, not the way to build the first drivetrain; for the struts it is not realistic.

## Isogrid on the struts and other thermal levers (2026-11-11)

The owner asked whether isogrid pockets on the hidden faces of the struts could improve heat sinking and free mass. Result (`strut.py` `ISOGRID`, `isogrid_study.py`; details in `strut-spec.md`): **no, at this size.** The arm plate is 3 mm thick and about 24 mm wide, so pockets 1.8 mm deep remove only 2.2 g from the four struts (2 %), leave arm conduction unchanged (3.6 to 3.8 K/W) and add little convective area (the pockets face the body or the other strut, with almost no air flow), while the out-of-plane stiffness drops to 16 % and the safety factor for a 5 N sideways knock from 25 to 3 (my assumed load). Isogrid pays off on large thin panels, not on a 70 mm arm.

Better thermal levers (my estimates, same assumptions as the heating section: strut path about 0.099 W/K, 10 K/W):
- **Black anodising the struts:** bare aluminium has an emissivity of about 0.05 to 0.1, black anodising about 0.8, which adds about 5 W/m2K of radiation to the 10 W/m2K of convection, raising the arm's air path from 0.034 to 0.051 W/K and the total by about **17 %**.
- **The pivot is the weak link:** the 12 mm stainless stud is about 8 K/W against about 7 K/W for the arm itself. A path through aluminium instead (an aluminium hub, or a copper or aluminium braid or shim across the pivot) would cut it below 1 K/W and raise the total by up to about **60 %**, but the stud is stainless for the O-ring seal and corrosion, so this is a hub design question.
- **Mass:** better places to take it out are the pivot bosses (about 11 g of each strut's 23 g, 4 mm of each boss is a plain disc), the wheels (33 g each) and above all the body (954 g).

## Hub sizing

- **Shafts are not the constraint.** A 6 mm steel shaft at 0.69 N.m sees about 16 MPa of shear. The envelope of the motors is the constraint.
- **Layout implied (a proposal, not built):** the current stationary stud with an axle stub (`strut-spec.md`) cannot be driven. Replace it with two **coaxial rotating shafts**, an inner shaft for one strut and a hollow outer shaft for the other, each through a bearing in the wall, each with its own motor inside the body, parallel to the axis and offset along the long dimension (y) by about 20 to 25 mm, with a spur reduction to the shaft and a potentiometer on each shaft (the papers put potentiometers in the shoulder hub). Motors offset in z would not fit: the interior is only about 50 mm tall, so two 25 mm motors would touch.
- **Envelope check still to do:** two 16 mm motors (about 40 to 50 mm long each) per hub fit the 140 mm width and about 50 mm interior height; 25 mm motors fit in height only barely. This needs a CAD check against the casting's corner bosses once the body redesign settles.
- A worm stage on the strut shaft would give free holding, but the packaging needs its own study.

## Next

Set the drive speed (owner), resolve the wheel motor fit, update `wheel.py` (parameters for material, wall thicknesses, no hub tube) and the strut axle stub, check the GPX 16 C alternative for the struts, then model the coaxial hub in CAD around the 16 mm x 58 mm motor and gearhead. Wheel motors and the real kinematic simulation are separate steps.
