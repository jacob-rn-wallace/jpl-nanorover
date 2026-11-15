# How heavy can the rover get? (2026-11-15)

Owner's direction (2026-11-15): **budget for more than 1.0 kg**; the project will not have the materials a space agency has, and aesthetics outrank saving mass in several places. This file says where the servos and wheel motors set the limit. Tags: SRC, ESTIMATE, ASM as elsewhere. Numbers from `hardware/drivetrain/chassis_sim.py` (`--body-mass`, `--body-y`; the drivetrain, servos, hub, struts, wheels and wheel supports are 614 g) and the datasheets in the private repo's `datasheets/`.

## A correction first: the servos' torque at 7.4 V

The servos run from the 7.4 V rail (`hardware-spec.md` section 3). **At 7.4 V the STS3215's rated torque is 5 kg.cm = 0.49 N.m at 650 mA, and its stall torque is 19.5 kg.cm = 1.91 N.m at 2.5 A, with Kt = 8 kg.cm/A (0.785 N.m/A)** (SRC Feetech specification A/0 2020-04-10, page 3, the document `hub.py` already cites). **The figures used elsewhere in the project, rated 0.98 N.m and peak 2.9 N.m, are the 12 V variant at 12 V** (the variant the parts list names). They overstated the margin by about 2 at this rail: the maximum hold (0.17 N.m) is **2.9 times** the rated torque, not 5.9, and the stall load on the servo mounts is 1.9 N.m, not 2.9 (`chassis-simulation.md`, `load-cases.md`, `servo-mounts.md` carry corrections). The case is glass-filled nylon (PA+GF) with metal (copper alloy) gears, ball bearings, two 3-pin 2.54 mm terminals, a 15 cm cable (same page 4).

## What limits the mass (the rover with a body of 686, 886 and 1,386 g)

| Total mass | Worst strut hold (N.m) | Margin on the servo's 0.49 N.m rated | Self-righting peak (N.m) | Margin on rated | Wheel torque, 20 degree slope (N.m) | Wheel torque, a half-wheel step (N.m) |
|---|---|---|---|---|---|---|
| 1.07 kg (now) | 0.172 | 2.8 | 0.136 | 3.6 | 0.029 | 0.148 |
| 1.15 kg (the optimiser's 80 g) | 0.186 | 2.6 | 0.150 | 3.3 | 0.031 | 0.159 |
| **1.30 kg** | **0.212** | **2.3** | 0.174 | 2.8 | 0.035 | 0.179 |
| **1.50 kg** | **0.245** | **2.0** | 0.210 | 2.3 | 0.041 | 0.207 |
| 2.00 kg | 0.333 | 1.5 | 0.293 | 1.7 | 0.054 | 0.276 |

- **Strut holds** scale with mass (0.162 N.m per kg at the worst pose). The project's rule is a margin of 2 on the hold: **the servos reach it at about 1.5 kg** (0.245 N.m against the 0.49 N.m rated). With a margin of 1.5 the limit is about 2.0 kg; at no margin, 3.0 kg.
- **Wheel motors (Pololu #3068, stall 0.314 N.m, FAQ guideline of about 25% of stall = 0.078 N.m continuous):** the 20 degree slope torque (0.027 N.m per wheel at 1.0 kg, SRC `drivetrain-spec.md`) reaches half the continuous guideline at about 1.4 kg, so a slope margin of 2 holds to about **1.4 kg**. The half-wheel step (0.138 N.m at 1.0 kg, front pair carrying everything) is above the continuous guideline already and is a brief stall-region load: it reaches **two-thirds of stall at 1.5 kg and 88% at 2.0 kg**. **The wheel motors, not the servos, are the tighter limit for climbing**, so a mass past about 1.5 kg should come with a better wheel gearmotor.
- **Running time falls with mass.** Holding a pose costs about I = T / Kt: 0.12 N.m (a typical stance hold) is 0.15 A per servo and the worst hold 0.24 A (the 0.16 to 0.32 A of `hardware-spec.md` section 3), so four servos holding use about 4 to 7 W at 7.4 V, **in proportion to the mass**: from 1.15 to 1.5 kg is 30% more hold power on a 3.7 Wh cell. Servo idle current (6 to 60 mA, sources differ) is still the first thing to measure.
- Not binding below 2 kg: the hub gears (tooth stress about 14.5 MPa at 0.33 N.m, `chassis-simulation.md`; at 0.49 N.m about 21 MPa, metal), the struts and the thin-walled wheels (static loads), the self-righting peak against the rated torque (3.3 times at 1.15 kg, 2.3 at 1.5 kg, only brief), the body's own stiffness (`optimisation-results.md`).
- **A lever if more is wanted:** the servo variant named in the parts list is the 12 V one (rated 0.98 N.m and stall 2.9 N.m at 12 V). Running it at a higher rail than 7.4 V (the boost converter could be set higher; the wheel drivers and LED ring would need checking) restores up to twice the torque and moves the servo limit to about 3 kg; the wheel motors would then limit.

## Decision (owner, 2026-11-15): a 1.5 kg budget and a 2.0 kg hard ceiling

The owner chose more generous numbers than the 1.3 and 1.5 kg I proposed. **What they mean (ESTIMATE, from the table above and `layout.py`):**

| | Total | Body contents allowed (total minus the 614 g drivetrain) | Servo hold margin | Wheel step, share of #3068 stall | Slope margin (continuous guideline) | Hold power on the 3.7 Wh cell, against 1.15 kg |
|---|---|---|---|---|---|---|
| now | 1.07 kg | 456 g | 2.8 | 47% | 2.7 | -7% |
| **budget** | **1.5 kg** | **886 g** (430 g of reserve over now, 350 to 390 g over the optimiser's 496 to 536 g) | **2.0** | 66% | 1.9 | +30% |
| **ceiling** | **2.0 kg** | **1,386 g** | **1.5** | **88%** | **1.4** | **+74%** |

- **At the 1.5 kg budget** everything keeps its margin of about 2 (the servos' hold, the wheel motors on a 20 degree slope), so the budget needs no hardware change. **At the 2.0 kg ceiling the margins are thin** (the strut hold at 1.5 times rated, a half-wheel step at 88% of the #3068's stall, the slope at 1.4 times the continuous guideline, and hold power up 74%), so **a rover that actually reaches 2 kg wants these changed first, in this order:** (1) **the wheel gearmotors**: the Pololu #3046 is a drop-in (same 10 x 12 mm profile and 3 mm shaft, a shorter body, `drivetrain-spec.md`) with about three times the torque headroom; it is a 12 V motor, so at the 7.4 V rail expect about 0.6 of its 0.98 N.m stall (ESTIMATE, scaling with voltage): a step at 2 kg would then be about 46% of its stall; (2) **the servo rail**: the parts list names the 12 V variant of the servo, so a separate higher rail for the servos (not the wheel drivers or the LED ring) would double their torque (rated 0.98, stall 2.9 N.m at 12 V) and take the servo limit to about 3 kg; (3) **the battery**: hold power is in proportion to mass, so a second cell or a larger one if the running time matters.
- **What the generous budget lets the body do** (nothing is decided): the topology optimisation can be run at more added structure (the sweep so far stopped at 80 g; 120 to 200 g would give crisper, stiffer and less skeletal members, and the forged skin's 1.5 mm is now a choice, not a necessity: 2 to 2.5 mm adds about 55 to 110 g, is more robust and easier to press and finish). The wall thickness and any bosses and fillets that make the body look right can be taken as drawn.
- **Still to do for the ceiling:** none of these hardware changes is made; the current parts list (Pololu #3068, the servo at 7.4 V) is good to about 1.5 kg.
