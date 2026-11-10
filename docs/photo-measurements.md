# Measurements taken from the JPL prototype photograph

Everything here comes from one picture: `img840-340-hires.original.jpg` (1650 x 1275 px), the JPL "Nanorover (circa 1997)" gallery image of the early
research prototype beside a US quarter. The photo itself is not in this repository (it is in the private companion repository, with its source in
`images/sources.csv`). These are photogrammetric estimates, not drawings: each value is labelled with how it was obtained and what it depends on.
The working scripts are in the private companion repository (`analysis/photo-measure/`); they have hard-coded paths and are not polished.

## Camera and scale

| | |
|---|---|
| Method | about 480 line segments along the solar-cell edges, split into the two in-plane directions of the top face; their vanishing points, with the image centre as the principal point, give the focal length |
| Focal length | about 3900 px on a 1650 px wide frame (about a 25 degree field of view: a long lens, little perspective) |
| Viewing angle | the camera looks at the top face from about 23 degrees above it. The quarter's ellipse independently gives about 22 degrees |
| Check that did not depend on the fit | the warped top face is **square to within 1%** (4432 x 4400 px) and the cells come out as clean right-angled rectangles |
| Scale | the top face is taken as **140 mm** square (MUSES-CN, 14 x 14 x 6 cm). That is an assumption, and the shared-drivetrain cross-check below says the true scale is about 1.11 times larger (about 155 mm): the quarter alone allows roughly 130 to 140 mm, and the photo's own caption says "approximately 10 cm on a side", which the square face and the quarter rule out |

## Solar cells on the top face (top view, millimetres at the 140 mm scale; multiply by about 1.11 under the shared-drivetrain scale below)

| Cells | Count | Size | Notes |
|---|---|---|---|
| Large cells, left and right columns | 5 + 5 | about 39.6 x 23.5 | widths measured 39 to 40.7 depending on the cell; the middle cells of each column almost touch (about 1 mm showing) |
| End cells of those columns | | about 21 to 22 tall at the top end, 23.5 at the bottom end | the top end cell's height is the least certain |
| Centre cells (two above, two below the central block) | 4 | about 19.6 x 44 | the long side is partly hidden by the central block: plus or minus 2 mm |
| Central raised block | 1 | not measured | carries at least two more small cells on its sloped faces |

Gaps: about 7 mm between the first and second large cells of a column, about 5 mm between the fourth and fifth, and black strips 5 to 8 mm wide between columns.
Total on the flat top face: 14 cells (plus the cells on the central block). Uncertainty: about 1 mm from locating the face edges, and about 2% from cell to cell.

## Wheel (see `wheel-spec.md`)

First photo: projecting circles on the wheel axis onto the photo gives a smooth outer disk of radius 27 mm, grouser tips at radius about 29.5 mm (about 59 mm across the
teeth), a collar centre 5 mm outboard of the disk, and a stack reaching about 33 to 36 mm inboard. The strut angles solve to about 7 and 9 degrees below horizontal and
the collar plane about 51 mm outboard of the body's side face. If the true body is smaller than 140 mm these lengths scale with it.

## Second photograph: `NanoRover-hires.original.jpg` (997 x 750 px)

A silver-bodied unit (bare aluminium, a round window and a small sealed-beam light on one end face, an antenna loop and a raised block on the top, cells in a different layout
from the first photo). Same method: about 440 line segments along the cell edges, vanishing points, focal length about 1920 px (a 29 degree field of view), the camera looking at the top face from about 38 degrees above it.

- **Top face:** rectified, it measures about 518 x 465 px, **1.11:1, not square**. This is a different unit from the first photo's square body, and not 14 x 14 cm.
- **Wheels:** two wheels are seen almost edge-on (the axle 78 to 80 degrees from the viewing ray), which shows the cone profile directly. The collar sits on a cone apex about 10 mm
  above the rim; the smooth cylinder behind it carries helical grousers (thin blades standing radially, serrated along their edges), 16 of them, leaning about 43.5 degrees from the axle, right-handed. See `wheel-spec.md` for the table.
- **End face with the window.** Rectified face-on (plane normal along the body's long axis, using the same camera), the face is 1065 px wide and 470 px tall including a base band and a seam line near the top: 0.44 high to wide, against 6/14 = 0.43. Taking the face width as 140 mm (3% uncertain, since a 60 mm body height would make it 136 mm) gives:

| Feature | Value | Notes |
|---|---|---|
| Face | about 140 x 62 mm | a base band about 12.5 mm tall under a green seam line, then the main face |
| Round window | 26 mm across; axis 29.2 mm from the left edge, 36.8 mm above the base | centred in the main face; the window looks black and glassy |
| Sealed-beam light (headlamp) | in a rounded-rectangle bezel about 22.3 x 14.5 mm, centred 59.8 mm from the left edge at the window's height, so about 30 mm to the viewer's right of the window axis | mounted at an angle, aimed across toward the window's field of view; two small screws about 12.5 mm above and below its centre. The tilt angle cannot be measured at this resolution (the lamp is about 25 x 15 px in the photo) |
| Corner screws | four small ones about 2.6 mm from the face's side edges, at about 21.7 and 50.6 mm above the base | about 2 mm heads |

 The top face of this unit is then about 156 x 140 mm (the long axis being the one the end face's normal points along), not square.
- **Top face.** A raised block close to the centre (offset about 8 mm and 4 mm from the face centre), footprint about 50 x 45 mm, with a cyan sensor-like panel on one sloping side, and a loop antenna made of two wires rising from it
  with a white bone-shaped piece lying beside it. The block's height was not measured (roughly 15 to 20 mm by eye). These are not the MUSES-CN features in the papers (a square patch antenna on the top face).

## The silver unit as the primary reference: size from its wheels

The silver unit is now the primary model (owner's decision), so its absolute size matters. Its top face is 518 x 465 px in the plan view (1.11:1) and its end face is 0.44 high to wide, but the photo has no ruler, so the scale comes from the wheels:
1. Each cone rim is fitted as an ellipse (apparent base diameter 169 px for the near wheel, 145 px for the left one) and taken as 59.5 mm across, the same normalisation as in `wheel-spec.md` (65 mm over the grousers). With the camera solved, that fixes both wheel centres in space.
2. The two wheel centres turn out to lie in the same plane perpendicular to the hub axis (1.6 mm apart along it), as two wheels on one hub should. That checks the camera and the scale together.
3. Putting the hub axis on the ray through the hub cap and asking for equal strut lengths to both wheels gives one answer, whichever point on the cap is used (hub pixel varied over four choices): **strut length about 86 mm** (85.8 to 88.8).
4. The hub is at mid-height, so the top plane is half a body height above it, which gives the plane's distance and the body size.

| Quantity (wheel tips = 65 mm) | Silver unit | Papers (MUSES-CN) |
|---|---|---|
| Width between the hub faces | about 138 mm | 140 mm |
| Height | about 61 mm | 60 mm |
| Length (across the hub axis) | about 154 mm | 140 mm |
| Strut length, pivot to wheel centre | about 86 mm | 70 mm |

The hub faces match the papers' 14 x 6 cm almost exactly, which supports the wheel scale. The length (154 mm) and the strut (86 mm) do not. The strut to wheel-diameter ratio, about 1.3, also appears in the first (black) photo, where the same fit gave 75.9 mm struts for 59 mm wheels. So the photographed prototypes have relatively longer struts than the published flight design. If instead the papers' 70 mm strut were true, the whole silver unit would be 0.81 times these sizes (113 x 125 x 50 mm, wheels 53 mm across). The uncertainty on these sizes is several percent: it rests on the wheel normalisation and on picking the hub axis point.

## The two units share a drivetrain (owner's statement): a cross-check of the scales

The owner states that the struts and wheels are identical on the black and silver units (the black unit being a running mock-up used for publicity, the silver unit the internal test unit that carries the optics). Taking that as a constraint gives an independent scale for the first (black) photo, which otherwise rests on assuming its top face is 140 mm:

| Quantity | Black photo at its 140 mm assumption | Silver photo (wheels = 65 mm across the grousers) | Scale factor that would make them equal |
|---|---|---|---|
| Wheel across the grousers | 59 mm | 65 mm | 1.10 |
| Strut length, pivot to wheel centre | 75.9 mm | about 86 mm | 1.13 |
| Strut length / wheel diameter | 1.29 | 1.32 | (3% apart) |
| Cone rim plane outboard of the body face | about 43 mm after correcting for the cone | 47 to 49 mm | within about 4 mm |

The two independent factors agree to 3%, so the black photo's true scale is about **1.11 times the 140 mm assumption**, with the same wheel and strut. That makes the black unit's top face about **155 mm square** (not 140), its end face about 40 to 49 mm tall to the PCB-like base seam (not 36 to 44), and every sized value taken from the first photo about 11% larger: the solar cells on the top face become about 44 x 26 mm (large) and 22 x 49 mm (centre), the square camera window about 28 x 24 mm, and the wheel is the same wheel as the silver unit's.
The silver unit's own sizes stand, since they were scaled from its wheels: hub faces about 138 x 61 mm, length about 154 mm. So both units have a body dimension of about 154 mm; the black one is a thin square box (about 155 x 155 x 45 mm), the silver one a thicker box (138 x 154 x 61 mm). That fits the owner's account: a mock-up without the optical bench would be thinner, and the instrument stack sets the silver unit's height.

The scale rests on the wheel normalisation (65 mm across the grousers, the published MUSES-CN size; the prototypes are described as "about 6 cm", which would shrink everything by about 9%) and on how well the hub and wheel points were placed (a few percent).

## The black unit's camera aperture

In the first photo the black unit's end face has a rounded-square window, about 25 mm wide and 22 mm tall (clear), inside a lighter bonded border about 35 x 30 mm (an adhesive fillet), near one end of the face. This is the camera aperture on the end face opposite the silver unit's round window (owner's reading). At the 140 mm scale of that photo; rough, because the face is seen at a steep angle.

## What this does not give

Absolute accuracy better than a few percent, any dimension of the two faces not visible, the hub details (only partly visible), or the finish.
For authoritative dimensions the sources remain the papers and the JPL Robotics group.
