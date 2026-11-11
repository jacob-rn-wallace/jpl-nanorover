# Wheels

Spec and design record for `hardware/wheel/wheel.py` (run after `hardware/body/body.py` and `hardware/strut/strut.py`).

The sources give one wheel number: **65 mm diameter** (Wilcox & Jones, MUSES-CN; "about 6 cm" for the earlier prototypes, aluminium, with a motor
inside and helical cleats). Everything else comes from two JPL photographs of the prototype, kept in the private companion repository:
`NanoRover-hires.original.jpg` (a silver-bodied unit, three-quarter view) and `img840-340-hires.original.jpg` (a black-bodied unit beside a quarter).

## Which wheel? (decided: the cleated wheel)

The model below copies the **aluminium cleated wheel of the 1997-98 prototypes** as photographed. It is not the wheel the MUSES-CN papers describe. Jones & Wilcox write that the flight wheels
"are a complex assembly of thin conductors and insulator designed to function both as a mechanical wheel and as a proximity sensor to the asteroid surface" (the sentence is split across columns in the
PDF text; it follows the strut-motor description in section 4.3), and that each strut/wheel assembly includes a contact sensor. JPL's 1998 "Nanorover Technology Task" video
(`vid1016-91-video2.mp4` in the private companion repository, about 3:25 to 3:35 and the computer-generated sequences) shows what that looks like: **plain cylindrical wheels with flat ends and
bands of gold-orange and silver around them**, on a lab prototype and on the animated flight vehicle, and nothing like the saw-tooth wheel. So for a replica of the MUSES-CN flight design the wheel
would be a banded cylinder; the cleated wheel is the earlier prototype's. The wheel width in the video is roughly half to 0.6 of the diameter by eye (not measured). The owner decided (2026-11-10) to stay with the cleated wheel, so it is the model; swapping it later is a change to `hardware/wheel/wheel.py` only.

## What the wheel is

A **smooth hollow cylinder carrying grousers in a helix, closed at the outside by a real cone**, the collar sitting on the cone's apex.

- **The cone is a cone.** In the second photo two wheels are seen almost edge-on (the axle is 78 to 80 degrees from the viewing ray), so the disk reads as a
  thin triangle whose apex is the collar. Projecting a model back onto the photo, the cone rim is the same size as the cylinder, and the apex stands about 10 mm
  above the rim (the collar centre about 14 mm), for a rim 59.5 mm across before scaling. In the first photo the disk looks nearly flat and the same fit
  puts the collar centre only about 5 mm out, so the two photographed wheels are different versions; the second is the better guide to the MUSES-CN wheel.
  (The owner's reading of the second photo, which corrected my first model's flat disk.)
- **The grousers are thin blades that stand straight up from the cylinder, radially, and run along a helix.** They are not a ratchet profile and not separate saw-blade discs:
  the wide bright bands between the dark lines on the photo are the smooth cylinder, and the dark lines are the grousers and their shadows. Each blade has fine
  saw-tooth serrations along its outer edge. (The owner's description. My first model stacked eight saw-tooth discs, and my second twisted a ratchet profile; both read the pattern wrongly.)
- **Handedness alternates (owner, 2026-11-11, from the photos).** Front and rear wheels on one side have opposite handedness, and the other side is the mirror image of the first, so the wheels are bilaterally symmetric (the body is too, apart from the camera and headlamp cutouts). On the silver unit (`NanoRover-hires`) the wheels read, in my own check by eye: front-left right-handed, back-left left-handed, front-right left-handed (back-right hidden), which fits; the black unit's back-left and front-left also fit, but I read its front-right as right-handed, which does not (taken as a misread; low-resolution crops). "Front" is the end with the round window (the CAD's +y face) and "left" is the viewer's, facing that end. In the CAD that is: right-handed at (+x, +y) and (-x, -y), left-handed at (+x, -y) and (-x, +y) (`ALTERNATE_HANDS` in `wheel.py`; the left-handed wheel is a mirror of the right-handed one, not a rotated copy). The Space Place toy's tread strips (two of each slant) point the same way. Earlier versions of this spec and the CAD had all four right-handed.
- **Helix:** the grousers lean 43.5 degrees from the axle at their crests and are right-handed for the wheel as modelled (seen from outside they turn counterclockwise going outward; two of the four are mirrored, see above). That comes from
  the slope of the dark lines on the front of the cylinder (about 20 degrees on the image, which the camera model turns into 43.5 degrees from the axle).

## How it was measured

For the second photo the camera was solved from the vanishing points of about 440 line segments along the solar-cell edges (focal length about 1920 px for a 997 px
wide image). With a known camera, a circle on the wheel axis projects to a known ellipse, so the wheel was fitted by overlay and the model was then projected back onto the photo
and compared by eye (the red rim ellipse, the green cone profile and the crest lines line up with the cone, the collar and the dark step lines). The scale uses the
apparent cone-rim diameter (169 px) as 59.5 mm; that is a normalisation, not a measurement.

| Quantity | Value (photo units, then scaled) | Notes |
|---|---|---|
| Cylinder = cone rim | radius 27.0 -> 29.75 mm | the same ratio to the grouser tips (0.915) in both photos |
| Grouser crests | radius 29.5 -> 32.5 mm | the blades stand about 2.75 mm proud of the cylinder |
| Cone apex above the rim | 9.2 -> 10.1 mm | collar centre about 14 mm; collar about 8 mm across and 8 mm long |
| Cylinder length | 31.3 -> 34.5 mm | the right-hand edge of the cylinder on the photo |
| Grousers | 16, helical, 43.5 degrees from the axle at the crests, right-handed | spacing of the dark lines 19 to 25 degrees on the visible arc (14 to 19 by that count); the first photo gave 17 at the rim |
| Serrations along each crest | about 3 mm pitch, 1.4 mm deep | read from the silhouette bumps |

The scale factor 65 / 59 is applied to every measured length so the diameter over the grousers is the published MUSES-CN 65 mm (the papers' value stands under the settling rule). The photographed wheels are about 59 mm across the grousers, which the quarter in the first photo confirms (57 to 60 mm).

## What the CAD has

- A smooth cylinder of 29.75 mm radius, 34.5 mm long, hollow (27.25 mm inner radius, a 2 mm inboard end plate), with 16 blades each 1.2 mm thick standing radially 2.75 mm proud of it.
  Each blade is extruded with a twist of 58 degrees along the cylinder (the twist follows from the 43.5 degree helix at the crest radius), so it follows a helix and stays radial.
  About 190 small right-triangle notches cut the serrations along the crests (3 mm pitch, 1.4 mm deep).
- A 1.5 mm conical shell closing the outer end (apex 10.1 mm above the rim), a 12 mm hub tube around the 6 mm axle, and an 8 x 8 mm collar on the apex.
- Mass about 78 g per wheel as aluminium with no motor, 313 g for four (preset `v1`; see "Presets"). The hollow interior, wall thicknesses, hub tube, blade thickness and collar are estimates.
- Two right-handed and two left-handed wheels (see "Handedness alternates"); the left-handed ones are mirror copies.
- Checks: the wheels overlap nothing (casting, studs, struts, lid) and the exported STEP re-imports with the same volume. Default stance: overall 275.7 mm wide
  by 191.9 mm long, wheel bottoms 32.1 mm below the box floor. The width depends on the strut layout, which is a placeholder (see `strut-spec.md`).
- Projecting the CAD wheel back onto the second photo, the cone profile, the collar, the end of the cylinder and the grouser lines line up with the dark lines on the photo.

## Presets (2026-11-11, layout C)

`wheel.py` has two presets, switched with `use_preset(name)` (`PRESET` at the top selects the default): **`thin`** (default) and **`v1`**.

| | `v1` (as first modelled) | `thin` (layout C, owner chose metal wheels) |
|---|---|---|
| Cylinder wall | 2.5 mm | 1.0 mm |
| End plate / cone shell / blades | 2.0 / 1.5 / 1.2 mm | 1.0 / 0.8 / 0.8 mm |
| Hub | 12 mm tube on a 6 mm axle | none: a 20.5 mm hole in the end plate around the 19 mm spindle tube; an 8 mm boss under the cone apex and the collar, bored 3.1 mm for the 3 mm stub shaft; the wheel runs on two bearings on the spindle (see `strut-spec.md`, "Wheel support") |
| Mass (aluminium) | 78 g | 33 g |

The outline, grousers, serrations and cone are identical, so the wheel looks the same from outside. In `thin` the wheel motor sits inside a spindle tube fixed to the strut tip, and the wheel is carried on two small bearings on that spindle and driven by a stub shaft at the cone apex (`strut/out/wheel_motors.step`, `wheel_spindles.step`, `wheel_bearings.step`; see `strut-spec.md`). The checks show no overlap between the wheels and the body, studs, struts, lid plate, motors, spindles or bearings, and the STEP re-imports with the same volume. **Not decided:** how a 0.8 mm-walled aluminium wheel with helical serrated grousers is made (CNC, multi-part, metal printing), how the wheel is fixed to the stub shaft, and the stiffness of the thin shell (no analysis).

## Caveats

- The scale is a normalisation. If the photographed rover is smaller or larger than the published sizes, every measurement scales with it.
- Wall thicknesses, the hollow interior, the hub tube, the blade thickness, the number of grousers (16, give or take two) and the serration shape are estimates.
- The two photos disagree on the cone depth, and the second photo's body is not square (its top face is about 1.11:1), so it is not the same unit as the first. The wheel here
  follows the second photo; revise `H_CONE` if a better source appears.
- Change the numbers in the parameter block at the top of `wheel.py`; the checks rerun.
