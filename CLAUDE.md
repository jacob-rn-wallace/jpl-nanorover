# jpl-nanorover: replica of the JPL MUSES-CN nanorover

An open replica of the JPL nanorover, the small four-wheeled asteroid rover designed for the Japanese MUSES-C (Hayabusa) mission and cancelled
by NASA in November 2000. A hobby build in the spirit of the sibling project `maha-rover` (same layout, same licence model).

**Picking the project back up: read `docs/handover.md` first** (status as of 2026-11-11 evening: sections 11 to 13 are the newest; open decisions, next steps). The drivetrain is designed and modelled; **the body is being redesigned in carbon (`docs/body-redesign.md`, handover section 13), at the stage of placeholders and a solid-block-with-cavities model; the current assembly CAD still contains the old Hammond box.**

## Scope (owner's decisions)
- **Goal:** a replica that matches the original's appearance and dimensions and performs most, if not all, of its non-science functions: driving on
  four wheels, posing its four struts independently, self-righting, solar power, and the camera (the owner counts the camera as a function, not as science).
- **There is no final nanorover (owner, 2026-11-10):** the project was cancelled mid-development, so every description is a snapshot. Elements are tagged built (seen on hardware), planned (stated in the papers) or concept (an idea under development, such as the banded wheel with ground sensing and the dust wipers); the default target is the most recent built hardware, and planned or concept items are opt-in. See `docs/design-comparison.md`.
- **Rule for settling values (owner, 2026-11-10):** the papers are authoritative by default; a paper value is overridden only when the two built units independently agree on a different one. The two units share their struts and wheels, so on drivetrain values they count as one observation and cannot override. Their sizes are also scaled from the papers' 65 mm wheel. Result: the body stays 140 x 140 x 60 mm, the struts 70 mm, the wheels 65 mm; the cleated wheel is the owner's exception to the papers' banded wheel. The papers' own rover figure is the silver unit. See `docs/design-comparison.md`.
- **Reference unit: undecided (owner, 2026-11-10: "not really sure").** Two JPL units are photographed: the silver-bodied unit (`NanoRover-hires.original.jpg`) and the black-bodied unit
  (`img840-340-hires.original.jpg`). The owner's account: the struts and wheels are identical on both; the black unit is a running mock-up with no instruments, used for publicity (both videos, a 1997 KTLA
  news segment); the silver unit is the internal test unit that carries the optics and was used for demonstrations of the instruments and teleoperation. Earlier the owner leaned to the silver unit as the more
  complete. Until it is settled, do not change the body or strut dimensions: the CAD keeps the papers' figures (a 140 x 140 x 60 mm body, 70 mm struts, 65 mm wheels), which C's footprint (about 139 x 139 mm) and the silver unit's length (about 140 mm) match. Measured against the quarter in the black unit's photo, the black unit is about 139 x 139 x 40 mm with struts about 76 mm and wheels about 59 mm across, and the silver unit (scaled with the same wheels) about 125 x 140 x 55 mm with struts about 78 mm (see `docs/photo-measurements.md`; an earlier version of those numbers assumed 65 mm wheels and was wrong).
- **Directions (owner, 2026-11-10): left and right are the viewer's.** Looking at a face or part from outside, left is the viewer's left. Say so when a drawing or description could be read the other way.
- **Drivetrain requirement (owner, 2026-11-11): the replica must lift itself under Earth gravity.** The papers' 10 g motors cannot do this (`docs/drivetrain-spec.md`, `hardware/drivetrain/torque_budget.py`); bigger strut motors are a deliberate deviation. **Design mass for performance figures: 1.0 kg total (owner, 2026-11-11);** the body will be redesigned later (deferred), so the current CAD's 1.46 kg is not the target. **The chassis simulation (`docs/chassis-simulation.md`) puts the maximum strut hold at 0.166 N.m, half the earlier figure; where `drivetrain-spec.md` differs, the simulation wins.** **Drivetrain layout C chosen (owner, 2026-11-11):** metal (thin-walled aluminium) wheels with the wheel motor inside, strut motors in the body; see `docs/drivetrain-spec.md`.
- **Out of scope:** spaceflight readiness, the science instruments beyond what is needed to look right (IR spectrometer, alpha X-ray spectrometer).
- **Wheel (decided 2026-11-10: stay with the cleated wheel):** the CAD wheel copies the 1997-98 prototype's aluminium cleated wheel, which is what the photographs show. The MUSES-CN papers describe the flight wheels as an assembly of thin conductors and insulator that also senses ground contact, and JPL's 1998 video shows plain banded cylinders. See `docs/wheel-spec.md`, "Which wheel?".
- **Black unit's camera aperture:** a square window with a bonded (adhesive) border on one end face, on the opposite end from the silver unit's round window. Secondary reference.
- **Body redesign (owner, 2026-11-11): the body will be carbon fibre or forged carbon, 140 x 140 x 60 mm (the papers' figures, reference unit still undecided), replacing the Hammond box.** Which of the two, and the manufacturing route, are open; see `docs/body-redesign.md`.
- **Body layout decisions (owner, 2026-11-11), where the replica now deliberately diverges from the originals:** (1) the **top and bottom faces are identical removable lids carrying solar cells** (so the rover works upside down), plus cells on both end faces, none on the hub faces; (2) the body is kept **symmetric about the transverse (z = 30) plane** (centre of mass, and parts reused around the body); (3) the **camera window is centred on a 60 x 60 mm square at one end of an end face** (30 mm from the top, bottom and side edges: x = +40, z = 30 on the +y face); (4) **camera and lamp share one window through a beamsplitter**; (5) the **antenna is on the opposite end face at the diagonally opposite position (x = -40, z = 30 on the -y face), a whip standing up in the plane of the face from a gravity-oriented pivot with a counterweight**. Details, checks and problems found: `docs/body-redesign.md`.
- **Body design method (owner, 2026-11-11):** treat the body as a solid, uniform 140 x 140 x 60 mm block with the components, connections and views cut out of it (`hardware/body/block.py`); once all the components are specified and placed, derive from that one block both a chassis of carbon tubs bonded together and a forged-carbon unibody. The block is a design volume, not the part. Purchasing for the project is deferred indefinitely (owner), so no bench tests for now.
- **Still open:** scale (the CAD is 1:1), carbon layup versus forged carbon and how the body is made, how the struts are actuated, the end use.

## Repo layout
- `docs/`: `design-comparison.md` sets the published design and the two photographed units side by side (read it first when the question is what to replicate). `jpl-nanorover-literature.md` is the annotated bibliography and the table of sourced dimensions with a verification level for each. `body-spec.md`,
  `strut-spec.md`, `wheel-spec.md`, `drivetrain-spec.md` (torque and mass budget, motor choices, layout study, coaxial hub; scripts in `hardware/drivetrain/`), `chassis-simulation.md` (planar quasi-static simulation: stances, tipping, strut torque, self-righting) record the CAD design decisions and checks. `photo-measurements.md` records what was measured from the two JPL photographs.
- Body redesign scripts in `hardware/body/` (no Hammond geometry, tracked): `cf_budget.py`, `cf_compare.py`, `cf_cost.py`, `power_budget.py` (plain python3 numbers), `layout.py` (keep-in volume, placements, mass and balance; needs the venv), `block.py` (the solid block with cavities, exports `out/body_block.step`; imports `layout.py`). Run `layout.py` before `block.py`.
- `hardware/`: CAD, parametric (build123d, `hardware/requirements.txt`). Each part has a script and a `out/` folder of STEP files:
  `body/body.py` (Hammond 1590Z090 box cut down, lid plate with O-ring groove and rib, thread inserts, hub studs for the earlier stud hub), `hub/hub.py` (coaxial hub, servos, gears), `strut/strut.py`, `wheel/wheel.py`,
  and `assembly/rover.py` (full assembly and mass summary), `assembly/preview.py` (rough render to `docs/images/rover-preview.png`).
  Run from the repository root with `.venv/bin/python hardware/<part>/<script>.py`, in the order body, hub, strut, wheel, assembly.
- `../jpl-nanorover-private` (private repo `jacob-rn-wallace/jpl-nanorover-private`, cloned beside this one; needs credentials): the source papers,
  images with `images/sources.csv` (a catalog; run `python3 images/catalog_images.py --check` after adding any), the saved Brescia page, the JPL video,
  the project handover note, Hammond's STEP file (`cad/vendor/hammond-1590Z090/`, with `SOURCE.md`) and the working photo-measurement scripts. Its contents
  belong to their authors or publishers: **never copy files from it into this repo**; record only numerical facts and citations here.

## Rules
- **All CAD work goes in `hardware/`** in this repository, with a spec in `docs/`. Anything that contains Hammond's geometry (the cut box, every
  assembly) stays out of git (see `.gitignore`); the scripts and our own parts are tracked.
- **Sources and status.** Record every dimension with its source and say how well it is supported. Mark anything without a source as an assumption,
  and do not present an assumption as the original's. The papers give very few rover dimensions: the 14 x 14 x 6 cm body, 6.5 cm wheels, 7 cm struts,
  the mass, the hub positions, solar cells on four of six faces. Everything else in the CAD is a labelled choice.
- **Check the numbers you are told, and say how you got them.** The photo scale assumes a 140 mm top face; the quarter suggests the prototype body
  could be 130 to 140 mm. Conflicting figures are listed in the bibliography.
- NASA/JPL imagery: usage terms are unchecked. Do not publish an image or something derived from one without checking.

## CAD notes (things that have already cost time)
- **STEP export of anything built from offset curves** (the lid plate's rib and groove) silently drops faces: the file re-imports as loose shells with
  zero volume. `body.py` runs `nurbs()` on the plate before export. After exporting a new part, re-import it and check `volume` and `len(solids())`;
  a boolean against a zero-volume import gives a false "no interference".
- Hammond's casting has nine tapered faces that do not mesh to STL, so renders show small holes. The STEP is fine.
- The casting is drafted (about 1 degree): the outer face is 138.4 mm at z = 10 and 140.0 at the rim. Spot-faces handle this at the hubs.
- The corner features of the casting (cover-screw bores open into the cavity, and wall-mounting tubes open at the floor) decide where the O-ring can run;
  see `docs/body-spec.md`.
- `hardware/` scripts print their own checks (fits, overlaps, masses). Read them rather than assuming.

## Design status
- **Body (superseded for the redesign, see `docs/body-redesign.md`): the CAD still models the Hammond box below; the carbon body is not modelled yet except as the cavity block (`hardware/body/block.py`).** Body 140 x 140 x 60 mm; total modelled mass about 1.5 kg (1459 g) before motors and electronics (target 1.3 kg: the cast box is the heavy part).
- Struts: 70 mm pivot to axle, two per side on concentric shafts driven by Feetech STS3215 servos in the body (`hardware/hub/hub.py`; `HUB_MODE`), bored at the tip for the wheel support (layout C; `TIP_MODE`). Wheels: 65 mm over the teeth, thin-walled aluminium (preset `thin`, 33 g; `v1` is the first model), a conical outer disk on a smooth hollow cylinder with 16 helical grousers (thin radial blades with serrated edges), fitted to the second JPL photo (`docs/wheel-spec.md`).
- Wheel drive (layout C): a Pololu #3068 gearmotor (10 x 12 x 25 mm box) inside a 19 mm spindle tube clamped in a bore in each strut tip, starting flush with that strut's plate (the strut is its heat sink), the wheel on two 3 x 8 x 4 mm bearings on a 3 mm stub shaft driven through an assumed coupling (`docs/strut-spec.md`, "Wheel support"). Not modelled: retention of the wheel and tube; for the hub, gear teeth, servo mounting, seals and retention (`docs/drivetrain-spec.md`). Motor choice follows cost: maxon motors are over $200 each (owner).
- Not yet modelled: the headlamp (a sealed-beam light beside the window, tilted toward the window's field of view), antenna, wiring feedthroughs, the camera and optics behind the window (the 26 mm window itself is modelled), the strut and wheel motors, the lid screws and O-ring washers, finish.
