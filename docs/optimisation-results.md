# First topology-optimisation results (2026-11-15, 3.8 mm grid)

pyMOTO 2.0.1 (MIT; installed with the owner's permission in `.venv-to`) was set up and run on the body middle. **This is a first pass: a layout of the load paths on a coarse grid, not a manufacturable design** (limits below). Reproduce: `python3 -m venv .venv-to && .venv-to/bin/pip install -r hardware/body/requirements-to.txt`; `.venv/bin/python hardware/body/to_inputs.py --grid 36`; `.venv-to/bin/python hardware/body/to_run.py --n 36 --mass 40`; `.venv-to/bin/python hardware/body/to_plot.py hardware/body/out/to_result_n36_m40.npz`. Setup, formulation and the fixed regions: `optimisation-setup.md`, `load-cases.md`, `servo-mounts.md`. Tags as elsewhere: SRC, ESTIMATE, ASM.

## What was run

- Grid 36 x 36 x 12 cells of 3.83 mm over the body middle (x, y +-69 mm, z 7 to 53 mm): 15,552 cells, 5,274 fixed void, 2,342 fixed solid, 7,936 design (3,968 unknowns in the upper half; the lower half is the mirror about z = 30, the fixed voids mirrored too).
- **Casting constraint along z** (two cores meeting at z = 30): a density filter (radius 1.5 cells), then Langelaar's overhang filter with the draw direction +z from the parting plane and a 0.5 degree overhang angle, then the fixed solids put back. A test on a 3D cantilever confirmed it: the largest density increase going up a column was 0.05 with it, against 0.48 with the default 45 degree angle.
- **Eleven load cases** (`to_run.py`; equilibrated, three isostatic supports at the hub rings take only the residual): the 0.3 m drop (100 g), a 310 N corner impact, the lid clamp (330 N per cam), the 2.9 N.m stall of each of the four servos, the battery, the camera end and the XBee each under 100 g, and 30 N handling. The objective is the mean of compliance divided by its value at the starting design (so every case counts equally); the constraint is the added mass, 20, 40 or 80 g (both halves, 1.55 g/cm3).
- Solver: CG with geometric multigrid, MMA; a solve of all the load cases takes about 1.3 s, a full 80-iteration run 8 to 12 minutes on this machine (4 cores).

## Results

| Added structure | Hub-ring displacement, drop (mm) | Hub-ring displacement, corner impact (mm) | Hub-ring displacement, servo stall (mm, largest of four) | Battery group, drop (mm) | Everything else, drop (mm) | Grey cells (0.2 < density < 0.8) |
|---|---|---|---|---|---|---|
| 20 g | 0.046 | 0.476 | 0.066 | **44.4** | 0.04 to 0.6 | 4% |
| **40 g** | 0.040 | 0.191 | 0.021 | **4.3** | 0.04 to 0.10 | 8% |
| **80 g** | 0.028 | 0.094 | 0.008 | **1.04** | 0.03 to 0.05 | 19% |

(Displacements are the largest nodal value over the group's nodes; E 35.5 GPa, all ESTIMATE-grade; `to_run.py` prints them per load case and per mass group.)

**Compared with having no added material** (the skin and fixed regions alone, evaluated at the same loads): the drop and corner cases are **about 1,250 and 140 times more compliant** (compliance 6.8 x 10^4 and 8.7 x 10^3 N.mm, against 54 and 63 with 40 g). The skin is not weak; the servo seats, the hub rings and the lid rims are separate islands, and what the optimiser adds is the load path between them. This reverses the earlier expectation (`body-redesign.md`) that the optimiser would "mostly return remove everything".

## Where the material goes (the 80 g result, `docs/images/to-n36_m80.png`)

- **A spine**, a thin web in the plane x = 0 running along y through the centre gap from the rear wall nearly to the camera end, **branching into a Y at the rear** (to the two rear corners) **and a T bar at the front** (under the battery bay).
- **Posts at the two hub faces**, between the hub rings, the four servo seats, the cam bosses and the lid rims (48% of the added mass sits at |x| > 45).
- **Diagonal bracing in the camera-end wall** and a thin beam along the rear wall (35% in the end walls, |y| > 45); the interior carries 17%.
- At 40 g the same pattern but thinner and the spine nearly absent; at 20 g only the side posts and the end walls (72% at the hub faces).

## What it says (findings, in order of importance)

1. **The battery has no load path in the design as it stands, and that is the largest single result.** In the first run (before the component load cases were added) the battery hung 35 mm off in the drop; with its own load case it still moves 44 mm at 20 g, 4.3 mm at 40 g and 1.04 mm at 80 g, the largest displacement at every mass. The front bay is far from the walls, so holding 30 g at 100 g costs structure. **It needs a defined mount** (a cradle fixed to a wall, or ribs under it); this is the open item "battery, camera, XBee and patch mounts" of `body-redesign.md`, now with a measurement behind it. The camera end and the XBee need little (0.03 to 0.1 mm from 40 g up).
2. **About 40 g of structure connects everything except the battery to within 0.1 mm in the drop, and 80 g brings the battery to about 1 mm.** The servo seats move 0.06 to 0.08 mm (40 g) and 0.03 to 0.05 mm (80 g) in the drop. The hub-bore target of `load-cases.md` (0.05 mm, operating loads) is met by the stall cases from 40 g (0.021 mm; 0.066 at 20 g) and by the drop at all three masses; the corner impact (an abuse case) is 0.19 and 0.094 mm at the ring.
3. **Mass outlook (ESTIMATE).** Body contents are 456 g; adding 40 to 80 g gives 496 to 536 g against the 386 g budget (110 to 150 g over), **a total of about 1.11 to 1.15 kg** (1.07 kg now). `chassis_sim.py` with those masses (`--body-mass 496` or `536`, `--body-y` 5.2 or 4.8): worst-case hold 0.179 to 0.186 N.m (0.166 originally), self-righting peak 0.143 to 0.150 N.m (0.118): still about 5 times inside the servo's rated 0.98 N.m. The mass is the owner's to decide; nothing here forces it down.
4. **The casting constraint costs little and the spine is a web, not a column.** A web in the plane x = 0 is formable with cores along z; the Y and T are the layout that connects the end walls to it.

## Limits (read these before using the picture)

- **Not crisp:** the largest density is 0.97 at 80 g and 0.54 at 20 g; at 80 g 19% of the cells are grey and only 296 of 3,968 exceed 0.5. The run is 80 iterations with no continuation (the penalty stays at 3), converged by MMA's own tolerance but not to a 0/1 design. The load paths are visible; the member sizes are not meaningful.
- **Coarse:** 3.83 mm cells cannot resolve the 1.5 mm forged minimum rib; the skin is represented by a stiffness weight, not geometry. Cell sizes of 2.9 mm (n = 48) and 2 mm (n = 72) need `to_inputs.py --grid 48` and a longer run (not yet done, see "Next").
- **Loads are first-pass:** inertial loads are spread over attachment regions I chose (the seat walls, the rims and cam bosses, the cells next to a component's void); the corner impact leaves a residual moment of about 12 kN.mm (40% of its own moment) carried by the supports; the self-weight of the optimised material and the 0.05 mm hub-bore target as a constraint are not in the optimisation (the displacement is reported after).
- **No stress constraint:** compliance only. `load-cases.md` found strength not to be the problem except at the lid catches (the seam gasket load), which are fixed regions here and untouched.
- **Fixed regions are my first cuts** (`to_inputs.py`), the plate seats and ring sizes ASM; the 11 wire channels are fixed voids, the servo modules' retention is not modelled, and the servo plates' own stiffness is not (the seat walls take the load directly).
- The z mirror and the casting filter were tested on a cantilever and in the full model; the convergence is MMA's, with no independent check against a finer grid yet.

## Next (none needs a decision from the owner)

1. Re-run at 2.9 mm (`--grid 48`) from the 3.8 mm result, with more iterations, to see whether the spine, the posts and the end-wall bracing hold their place and become crisper.
2. Penalty continuation (p from 3 to 4 or 5) and a projection to get a 0/1 design; then the hub-bore deflection as a constraint.
3. A stress check (a p-norm of the von Mises stress, or a post-run solve) against the 113.7 / 2 MPa allowable.
4. **Needs the owner:** a battery mount (a cradle fixed to a wall or an explicit rib set), and whether to accept the 1.11 to 1.15 kg outlook.

## Update: the same problem on a finer grid (2.9 mm, `--n 48`, started from the 3.8 mm 80 g result)

36,864 cells (2.875 mm), 9,813 unknowns in the upper half, 80 iterations in 34 minutes (about 25 s per iteration here against 8 s at 3.8 mm); `docs/images/to-n48_m80.png`. **The layout does not change with the grid**: the same spine with its Y and T, the same hub-face posts and end-wall bracing; the mass split is 53% at the hub faces, 33% in the end walls and 15% in the interior (48, 35 and 17% at 3.8 mm).

| 80 g | Hub ring, drop (mm) | Hub ring, corner (mm) | Servo seats, drop (mm) | Battery, drop (mm) | Grey cells | Cells above 0.8 |
|---|---|---|---|---|---|---|
| 3.8 mm | 0.028 | 0.094 | 0.033 to 0.047 | 1.04 | 19% | 1.2% |
| 2.9 mm | 0.027 | 0.099 | 0.037 to 0.063 | 1.20 | 15% | 2.1% |

So **the displacements agree to within about 15% across the two grids** (the largest difference is the battery, 1.04 against 1.20 mm), which is as much grid independence as this first pass can show. The result is slightly crisper (grey 15%, maximum density 1.00). Penalty continuation (p = 4, then 5) is running from this result; its pictures are `to-n48_m80_p4.png` and `to-n48_m80_p5.png` if it finished, and the numbers are in `to_result_n48_m80_p*.npz` (each result file holds the compliances, the ring and overall displacements and the density).

