# Wheels

Spec and design record for `hardware/wheel/wheel.py` (run after `hardware/body/body.py` and `hardware/strut/strut.py`).

The sources give one wheel number: **65 mm diameter** (Wilcox & Jones, MUSES-CN; "about 6 cm" for the earlier prototypes, aluminium, with a motor
inside and helical cleats). Everything else comes from two JPL photographs of the prototype, kept in the private companion repository:
`NanoRover-hires.original.jpg` (a silver-bodied unit, three-quarter view) and `img840-340-hires.original.jpg` (a black-bodied unit beside a quarter).

## What the wheel is

A **hollow drum with diagonal saw-tooth grousers, closed at the outside by a real cone**, the collar sitting on the cone's apex.

- **The cone is a cone.** In the second photo two wheels are seen almost edge-on (the axle is 78 to 80 degrees from the viewing ray), so the disk reads as a
  thin triangle whose apex is the collar. Projecting a model back onto the photo, the cone rim is the same size as the drum's root, and the apex stands about 10 mm
  above the rim (the collar centre about 14 mm), for a rim 59.5 mm across before scaling. In the first photo the disk looks nearly flat and the same fit
  puts the collar centre only about 5 mm out, so the two photographed wheels are different versions; the second is the better guide to the MUSES-CN wheel.
  (The owner's reading of the second photo, which corrected my first model's flat lathe-finished disk.)
- **The drum is not a stack of saw blades.** Its cross-section is a ratchet (a long ramp and a short step, 16 of them) twisted along the drum, so the grousers run
  diagonally. Each crest also carries fine serrations. My first model, a smooth disk over eight stacked saw-tooth discs, mistook the stepped ridges for separate discs.
- **Direction:** the grousers lean 43.5 degrees from the axle and are right-handed (seen from outside they turn counterclockwise going outward). That comes from the
  slope of the dark step lines on the front of the drum (about 20 degrees on the image, which the camera model turns into 43.5 degrees from the axle).
  The ramp direction (which flank is the step) is not determined and is a choice.

## How it was measured

For the second photo the camera was solved from the vanishing points of about 440 line segments along the solar-cell edges (focal length about 1920 px for a 997 px
wide image). With a known camera, a circle on the wheel axis projects to a known ellipse, so the wheel was fitted by overlay and the model was then projected back onto the photo
and compared by eye (the red rim ellipse, the green cone profile and the crest lines line up with the cone, the collar and the dark step lines). The scale uses the
apparent cone-rim diameter (169 px) as 59.5 mm; that is a normalisation, not a measurement.

| Quantity | Value (photo units, then scaled) | Notes |
|---|---|---|
| Cone rim = ratchet root | radius 27.0 -> 29.75 mm | the same ratio to the tooth tips (0.915) in both photos |
| Tooth crests | radius 29.5 -> 32.5 mm | teeth stand about 2.75 mm proud of the cone rim |
| Cone apex above the rim | 9.2 -> 10.1 mm | collar centre about 14 mm; collar about 8 mm across and 8 mm long |
| Drum length | 31.3 -> 34.5 mm | the right-hand edge of the drum on the photo |
| Grousers | 16, 43.5 degrees from the axle, right-handed | spacing 19 to 25 degrees on the visible arc (14 to 19 by that count); the first photo gave 17 teeth at the rim |
| Serrations along each crest | about 3 mm pitch, 1.4 mm deep | read from the silhouette bumps |

The scale factor 65 / 59 is applied to every measured length so the tooth diameter is the published MUSES-CN 65 mm. The photographed wheels are about 59 mm across the teeth.

## What the CAD has

- Ratchet cross-section twisted by 58 degrees over the 34.5 mm drum (the twist follows from the 43.5 degree helix at the crest radius), hollowed to a 27.25 mm inner
  radius with a 2 mm inboard end plate, a 12 mm hub tube around the 6 mm axle, a 1.5 mm cone shell, an 8 x 8 mm collar, and about 190 small right-triangle notches for the serrations.
- Mass about 90 g per wheel as aluminium with no motor; 361 g for four. The hollow interior, wall thicknesses, hub tube and collar are estimates.
- The same wheel on both sides (a rotated copy, so the helix keeps its handedness).
- Checks: the wheels overlap nothing (casting, studs, struts, lid) and the exported STEP re-imports with the same volume. Default stance: overall 275.7 mm wide
  by 191.9 mm long, wheel bottoms 32.1 mm below the box floor. The width depends on the strut layout, which is a placeholder (see `strut-spec.md`).

## Caveats

- The scale is a normalisation. If the photographed rover is smaller or larger than the published sizes, every measurement scales with it.
- Wall thicknesses, the hollow interior, the hub tube, the ramp direction, the number of grousers (16, give or take two) and the serration shape are estimates.
- The two photos disagree on the cone depth, and the second photo's body is not 14 x 14 cm (its top face is about 1.11:1), so it is not the same unit as the first. The wheel here
  follows the second photo; revise `H_CONE` if a better source appears.
- Change the numbers in the parameter block at the top of `wheel.py`; the checks rerun.
