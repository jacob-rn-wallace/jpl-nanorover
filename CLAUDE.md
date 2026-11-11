# jpl-nanorover: replica of the JPL MUSES-CN nanorover

An open replica of the JPL nanorover, the small four-wheeled asteroid rover designed for the Japanese MUSES-C (Hayabusa) mission and cancelled
by NASA in November 2000. A hobby build in the spirit of the sibling project `maha-rover` (same layout, same licence model).

## Scope (owner's decisions)
- **Goal:** a replica that matches the original's appearance and dimensions and performs most, if not all, of its non-science functions: driving on
  four wheels, posing its four struts independently, self-righting, solar power, and the camera (the owner counts the camera as a function, not as science).
- **Rule for settling values (owner, 2026-11-10; amended):** a value is authoritative when two independent designs agree (the papers, the silver unit, the black unit; the two units count as one vote on their shared struts and wheels, and their sizes cannot confirm the papers' absolute numbers because they are scaled from the papers' wheel). It locks a 140 x 140 x 60 mm body and leaves the strut length (70 mm in the papers, about 86 mm in the units) and the wheel type open. See `docs/design-comparison.md`.
- **Reference unit: undecided (owner, 2026-11-10: "not really sure").** Two JPL units are photographed: the silver-bodied unit (`NanoRover-hires.original.jpg`) and the black-bodied unit
  (`img840-340-hires.original.jpg`). The owner's account: the struts and wheels are identical on both; the black unit is a running mock-up with no instruments, used for publicity (both videos, a 1997 KTLA
  news segment); the silver unit is the internal test unit that carries the optics and was used for demonstrations of the instruments and teleoperation. Earlier the owner leaned to the silver unit as the more
  complete. Until it is settled, do not change the body or strut dimensions: the CAD keeps the papers' figures (a 140 x 140 x 60 mm body, 70 mm struts, 65 mm wheels), which the silver unit's hub faces
  (about 138 x 61 mm) match. Measured against the 65 mm wheels, the silver unit is about 138 x 154 x 61 mm with about 86 mm struts, and the black unit about 155 x 155 x 45 mm (see `docs/photo-measurements.md`).
- **Directions (owner, 2026-11-10): left and right are the viewer's.** Looking at a face or part from outside, left is the viewer's left. Say so when a drawing or description could be read the other way.
- **Out of scope:** spaceflight readiness, the science instruments beyond what is needed to look right (IR spectrometer, alpha X-ray spectrometer).
- **Wheel (decided 2026-11-10: stay with the cleated wheel):** the CAD wheel copies the 1997-98 prototype's aluminium cleated wheel, which is what the photographs show. The MUSES-CN papers describe the flight wheels as an assembly of thin conductors and insulator that also senses ground contact, and JPL's 1998 video shows plain banded cylinders. See `docs/wheel-spec.md`, "Which wheel?".
- **Black unit's camera aperture:** a square window with a bonded (adhesive) border on one end face, on the opposite end from the silver unit's round window. Secondary reference.
- **Still open:** scale (the CAD is 1:1), materials and manufacturing method, how the struts are actuated, the end use.

## Repo layout
- `docs/`: `design-comparison.md` sets the published design and the two photographed units side by side (read it first when the question is what to replicate). `jpl-nanorover-literature.md` is the annotated bibliography and the table of sourced dimensions with a verification level for each. `body-spec.md`,
  `strut-spec.md`, `wheel-spec.md` record the CAD design decisions and checks. `photo-measurements.md` records what was measured from the two JPL photographs.
- `hardware/`: CAD, parametric (build123d, `hardware/requirements.txt`). Each part has a script and a `out/` folder of STEP files:
  `body/body.py` (Hammond 1590Z090 box cut down, lid plate with O-ring groove and rib, thread inserts, hub studs), `strut/strut.py`, `wheel/wheel.py`,
  and `assembly/rover.py` (full assembly and mass summary), `assembly/preview.py` (rough render to `docs/images/rover-preview.png`).
  Run from the repository root with `.venv/bin/python hardware/<part>/<script>.py`, in the order body, strut, wheel, assembly.
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
- Body 140 x 140 x 60 mm; total modelled mass about 1.5 kg (1459 g) before motors and electronics (target 1.3 kg: the cast box is the heavy part).
- Struts: 70 mm pivot to axle, two per side on a stationary hub stud. Wheels: 65 mm over the teeth, a conical outer disk on a smooth hollow cylinder with 16 helical grousers (thin radial blades with serrated edges), fitted to the second JPL photo (`docs/wheel-spec.md`).
- Not yet modelled: the headlamp (a sealed-beam light beside the window, tilted toward the window's field of view), antenna, wiring feedthroughs, the camera and optics behind the window (the 26 mm window itself is modelled), the strut and wheel motors, the lid screws and O-ring washers, finish.
