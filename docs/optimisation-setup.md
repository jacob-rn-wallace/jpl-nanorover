# Setting up the topology optimisation: draw direction, core plan, solver, inputs

Written 2026-11-15, after the load cases (`load-cases.md`) and the servo mounts (`servo-mounts.md`). The decisions are mine and are for the owner to confirm. Numbers: `hardware/body/draw_analysis.py` and `hardware/body/to_inputs.py` (both need the venv). Tags: SRC, ESTIMATE, ASM as elsewhere. **Update 2026-11-15 (later): the owner chose pyMOTO and gave permission; it is installed (`.venv-to`, `requirements-to.txt`), tested on a cantilever and run on the body: results in `optimisation-results.md`. The statements below about the solver's speed and fit were written before that and are kept as written; where they differ, the results file wins (a full solve of 11 load cases takes about 1.3 s at 3.8 mm; an 80-iteration run takes 8 to 12 minutes).**

## 1. Draw direction: along z, two cores meeting at z = 30

**The rule** (a press with two cores, one from each side along the draw axis, meeting inside the part at a parting plane; the outside machined afterwards, owner 2026-11-12): a core makes a void and must be pulled out along the axis, so everything between a void and the face its core comes from has to be void as well. Material cannot stand in the *shadow* of a fixed void on its core's side.

**Measured** (`draw_analysis.py`, 1 mm voxels; the body middle z 7 to 53 has 547 cm3 of design space before any constraint; the fixed voids are the servo pockets and hub parts, the placed components and plug zones, the 11 wire channels, the four plate seats and the contact pockets; the lid-mounted boards and the holes drilled from outside, the hub and cam bores and the windows, are not counted):

| Draw plan | Design space left | Lost to shadows |
|---|---|---|
| **two-sided along z, parting at z = 30** | **388 cm3 (71%)** | 159 cm3 |
| one-sided along z (core from +z / from -z) | 450 / 420 cm3 (82% / 77%) | 97 / 127 cm3 |
| two-sided along x, parting at x = 0 | 380 cm3 (69%) | 167 cm3 |
| one-sided along x (+x / -x) | 321 / 330 cm3 (59% / 60%) | 226 / 217 cm3 |
| two-sided along y, parting at y = 0 | 341 cm3 (62%) | 206 cm3 |
| one-sided along y (+y / -y) | 331 / 304 cm3 (61% / 56%) | 216 / 243 cm3 |

**Choice: two-sided along z with the parting plane at z = 30.** Why: (1) **the assembly is along z** (the servo modules are lowered in with the lids off; every pocket and the battery bay must open to a lid face anyway); (2) **the lids come off along z**, identical top and bottom; (3) **the owner's symmetry is about z = 30** (the body, the lids and the parts reused round it), which a two-sided plan with the parting at z = 30 keeps and a one-sided plan breaks (one side would have a floor and the other none); (4) the hub faces carry the hub bores, the struts and the cam bores, which a core drawn along x would run into. The volume figure does not decide it: x is nearly as good on volume and y is worse, but **volume is not scarce** (the structure the loads need is a small part of the 388 cm3; `load-cases.md` finding 1). The 31% lost to shadows is not a binding cost.

**What it means for the part.**
- **One piece, not two half-shells.** The press is one forging with two cores; its parting line lies on the outside and is machined away. (The earlier idea of two identical half-shells bonded at z = 30 would split the hub bores through their bearing seats; not needed.)
- **Every pocket opens to a lid face.** The servo pockets, the battery bay, the camera, XBee and patch bays: no floor below them and no roof above (the lids close them). The servo's shadow is the biggest cost: 133 of the 159 cm3.
- **Structure is vertical walls and ribs** (running z), joined where the cores meet at z = 30; no horizontal web may sit above or below a fixed void in its column. In practice: a perimeter frame with bulkheads and the seat walls, which is what a body with removable lids wants anyway.
- **Anything reachable only from outside is drilled or machined after pressing**: the hub bores and their rings' faces, the cam bores, the window, the antenna window, the wire holes through the hub walls (owner's route: machine the outside). These do not constrain the draw.
- **The 11 wire channels** (tunnels along x and y, with bends) cannot be cored by a z draw. Two ways out; the first is the one I recommend: (a) **do not cut them at all**: once the optimiser has removed the interior, the wires run through void; the channels are kept in the optimisation as fixed voids (so no material is put in the way), and clips or grooves for the wires come with the refinement (step 6); (b) soluble or fusible cores for any tunnel that must stay. Their shadow costs 12 cm3 of design space, which is conservative.
- **Draft:** at least 1 degree on every face parallel to z (`body-redesign.md`).
- **The plate seats** (`block.py`) are now plain recesses 3.1 mm deep with no head pockets: pockets along x would have been undercuts.

## 2. How the optimiser is posed

- **Design space and fixed regions:** `to_inputs.py` writes `out/to_inputs_r2.npz`: the body middle (z 6 to 54, x and y +-70) on a 2 mm grid (70 x 70 x 24 cells): **291 cm3 fixed void, 107 cm3 fixed solid** (outer skin 51, lid seat rims 33, cam bore bosses 17, hub bore rings 7, window ring 7, seat walls 6), **542 cm3 design space (67,785 cells; 33,536 unknowns once mirrored about z = 30)**. The fixed solids' sizes are first cuts (ASM, listed in the script); `--res 4` gives a 4 mm grid.
- **Symmetry:** design variables for the z >= 30 half, mirrored (owner's decision).
- **Draw (casting) constraint along z:** the shadow rule of section 1. In the upper half a cell must be void if any cell between it and the parting plane, in its column, is void (a fixed void or one the optimiser has made); the lower half is the mirror. Implemented as a smooth running-minimum filter along z from the plane outward (an explicit parametrisation in the style of Gersborg and Andreasen's casting constraint, remembered, not checked), applied to the density before the stiffness interpolation, with the fixed solids exempt.
- **Minimum member size:** a density filter of radius 3 mm (1.5 cells) gives about 3 mm members at the 2 mm grid; the forged minimum is 1.5 mm, which this grid cannot resolve, so **the first pass is a layout of load paths, not a manufacturable design**, and the 1.5 mm ribs are set in step 6 (the refinement).
- **Objective and constraints:** minimise the weighted compliance of LC1, LC2 and LC6 (the operating cases) for a sweep of added structure of 0, 10, 20, 40 and 80 g above the skin; strength, hub-bore deflection (0.05 mm), seat flatness and the cell faces' stiffness checked on each result (`load-cases.md`). Strength: the impact cases LC3 to LC5 as separate static solves, peak stress at most 113.7 / 2 MPa.
- **Material:** isotropic, E 35.5 GPa, density 1.55 g/cm3 (SRC `body-redesign.md`).

## 3. The solver

| Option | Licence | For | Against |
|---|---|---|---|
| **pyMOTO** (Python, modular, 3D examples) | MIT (SRC its documentation) | **the problem needs custom pieces** (the casting filter, the z mirror, several load cases with weights, fixed solid and void regions, a volume sweep, later a stress measure) and pyMOTO is built as modules you chain with automatic derivatives; scriptable from this repository | I could not install or run it (refused), so its speed and its handling of the fixed-region and multi-load setup are unverified; no built-in casting constraint found |
| PyTopo3D (Python, 3D SIMP, optimality criteria) | MIT (SRC its PyPI page) | takes an STL design domain and obstacles, exports STL: the quickest route to a first picture | a fixed compliance and volume formulation (optimality criteria): no obvious place for the casting filter or several weighted load cases; no draw constraint found |
| A commercial tool (Altair Inspire, Autodesk Fusion generative design) | commercial | a built-in die-casting or draw constraint, a GUI, STEP in and out (`out/body_block.step`, the lids' steps) | not scriptable from here; licence and what the owner has: not known |

**Recommendation: pyMOTO**, for the custom constraints and because a scripted pipeline can be rerun when the load cases or the draw plan change; PyTopo3D as a quick-look first if a picture is wanted sooner; a commercial tool if the owner already has one and prefers it (the `.step` files are the input). **Not verified:** that pyMOTO runs here and does this; the first job is a smoke test (a 3D cantilever), then a 4 mm run of the real set with LC1 only.

**Can this machine run it?** It has 4 cores, 7 GB and SciPy's SuperLU only (no CHOLMOD, no multigrid). ESTIMATE: at 4 mm (about 14,000 design cells, 50,000 degrees of freedom) a direct solve is seconds, so a 100-iteration run with six load cases is minutes to an hour; at 2 mm (about 67,000 cells, 210,000 degrees of freedom) a direct factorisation needs a few GB and minutes, so the same run is hours (several to tens). **Use 4 mm here to find the load paths, and the 2 mm run on the owner's MacBook Air (M2, 16 GB) or with a multigrid solver.** All of this is arithmetic from the sizes, not measured.

## 4. What is done and what is next

Done: the draw direction (this file), the non-design regions as one set (`to_inputs.py`, first cuts), the load cases and the servo mounts. **Next, in order:** (1) the solver: an owner decision (pyMOTO recommended) and permission to install it, then the smoke test; (2) turn the load cases into forces on the fixed-solid regions of `to_inputs_r*.npz` (the region names are in the `.json`); (3) the casting filter and the z mirror; (4) the first 4 mm run, the volume sweep, and a look at the load paths; (5) review with the owner before the 2 mm run and the refinement (step 6); the access check (step 4 of the owner's process) is still to do and can run alongside.
