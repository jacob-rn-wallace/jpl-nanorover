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
| Scale | the top face is taken as **140 mm** square (MUSES-CN, 14 x 14 x 6 cm). The quarter in the photo gives an absolute check, below: the top face comes out about 139 mm (136 to 143 mm), so the assumption holds. The photo's own caption says "approximately 10 cm on a side", which the square face and the quarter rule out |

## Solar cells on the top face (top view, millimetres; the quarter confirms the 140 mm scale of this photo to about 3%)

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
- **End face with the window.** Rectified face-on (plane normal along the body's long axis, using the same camera), the face is 1065 px wide and 470 px tall including a base band and a seam line near the top: 0.44 high to wide, against 6/14 = 0.43. The values below take the face width as 140 mm, so they are proportions of the face. At the quarter-based scale the silver unit's face is about 125 mm wide, and every length below is then about 0.89 of its value (the window about 23 mm across); the CAD uses them as proportions of its own 140 mm face:

| Feature | Value | Notes |
|---|---|---|
| Face | about 140 x 62 mm | a base band about 12.5 mm tall under a green seam line, then the main face |
| Round window | 26 mm across; axis 29.2 mm from the left edge, 36.8 mm above the base | centred in the main face; the window looks black and glassy |
| Sealed-beam light (headlamp) | in a rounded-rectangle bezel about 22.3 x 14.5 mm, centred 59.8 mm from the left edge at the window's height, so about 30 mm to the viewer's right of the window axis | mounted at an angle, aimed across toward the window's field of view; two small screws about 12.5 mm above and below its centre. The tilt angle cannot be measured at this resolution (the lamp is about 25 x 15 px in the photo) |
| Corner screws | four small ones about 2.6 mm from the face's side edges, at about 21.7 and 50.6 mm above the base | about 2 mm heads |

 The top face of this unit is then about 1.11 times as long as it is wide (the long axis being the one the end face's normal points along), not square: about 140 x 125 mm at the quarter-based scale.
- **Top face.** A raised block close to the centre (offset about 8 mm and 4 mm from the face centre), footprint about 50 x 45 mm, with a cyan sensor-like panel on one sloping side, and a loop antenna made of two wires rising from it
  with a white bone-shaped piece lying beside it. The block's height was not measured (roughly 15 to 20 mm by eye). These are not the MUSES-CN features in the papers (a square patch antenna on the top face).

## Absolute scale from the quarter, and the sizes of both units

The only object of known size in either photo is the US quarter (24.26 mm) in the first. Its face is a 136.4 px ellipse (133 to 140 px depending on where the rim is read), which puts it 693 mm from the camera and the ground plane 351 mm from the camera along the plane normal. The near wheel rests on the same ground, so the plane distance of the wheel's bottom, worked out at the 140 mm assumption, can be compared:

| | Value |
|---|---|
| Ground plane distance from the quarter | 351 mm (342 to 360) |
| Wheel-bottom plane distance at the 140 mm scale | 353 mm |
| Scale factor k | **0.996** (0.97 to 1.02) |

So the black photo's 140 mm assumption was right to about 3%. At that scale the **black unit (C)** is about **139 x 139 mm** on top (136 to 143), its end face about 36 to 44 mm tall down to the PCB-like base seam, its **wheels about 59 mm across the grousers** (57 to 60; the sources say "about 6 cm" for the prototype wheels) and its **struts about 76 mm** (74 to 78) from pivot to wheel centre.

**The silver unit (B)** has no ruler, so its scale comes from the wheels it shares with C (owner's statement): with the wheel 59 mm across the grousers, its cone rim is 54 mm and the near wheel's 169 px rim ellipse fixes the distances. The same steps (wheel centres, then the hub axis, then the top plane half a body height above the hub) give:

| Silver unit (wheels 59 mm) | Value | Papers (MUSES-CN) |
|---|---|---|
| Width between the hub faces | about 125 mm | 140 mm |
| Length (across the hub axis) | about 140 mm | 140 mm |
| Height | about 55 mm | 60 mm |
| Strut length, pivot to wheel centre | about 78 mm | 70 mm |

Checks: the two wheel centres lie in one plane perpendicular to the hub axis (1.6 mm apart); the strut length comes out the same for both wheels whichever hub-cap pixel is used (85.8 to 88.8 mm in the first, 65 mm, version, 78 mm in this one); the strut-to-wheel-diameter ratio is 1.29 for C and 1.32 for B, which is scale-free; and the wheel plane sits 47 to 49 mm outboard of B's body face (both at the same scale as the table) against about 43 mm for C.

**Correction.** An earlier version of this page took the wheels as the papers' 65 mm (the published MUSES-CN size) and so scaled both photos up (a factor of 1.11 for C, giving a 155 mm square body, and the sizes 138 x 154 x 61 mm for B). The quarter contradicts that: the photographed prototype wheels are about 59 mm across, 9% smaller than the papers' 6.5 cm, so the papers' wheel is presumably the flight design's.
The silver unit's hub-axis width is then 125 mm and its height 55 mm, 11% and 8% below the papers' 14 x 6 cm, while its length equals the papers' 14 cm; C's footprint equals the papers' 14 x 14 cm but it is thinner. The units' struts are about 9 to 11% longer than the papers' 7 cm.

The sizes still depend on the camera solution, on the near wheel standing on the surface the quarter lies on, on the quarter's rim being read correctly, and (for B) on its wheels being the same as C's.

## The black unit's camera aperture

In the first photo the black unit's end face has a rounded-square window, about 25 mm wide and 22 mm tall (clear), inside a lighter bonded border about 35 x 30 mm (an adhesive fillet), near one end of the face. This is the camera aperture on the end face opposite the silver unit's round window (owner's reading). At the 140 mm scale of that photo; rough, because the face is seen at a steep angle.

## The Space Place top decal (compared by eye, 2026-11-11)

NASA Space Place's toy nanorover (a 1998 JPL pattern PDF, see `jpl-nanorover-literature.md`, item 19) has a printed top decal of solar cells. Compared with the top faces in the two photographs:

| Feature | Decal | Black unit (`img840-340`) | Silver unit (`NanoRover-hires`) |
|---|---|---|---|
| Large cells along two opposite edges | 5 + 5, in two rows | 5 + 5, in two columns (measured above) | not matched: about 14 flat cells in a different arrangement, several tilted in pairs |
| Cells beside the centre | 4 small (two of each orientation) | 4 centre cells | not matched |
| Extra cells | 2 + 2 more on the other two edges (18 in all, flat) | none; 14 flat cells | 14 flat cells |
| Centre | a flat cross and the antenna ring | a raised block with sloped cell faces | a raised block with a cell on its face, plus the antenna loop |

Reading: the decal's 5 + 5 edge rows and 4 centre cells match the black unit's layout, but it adds 4 side cells and has no raised block, so it is a simplified drawing, not a plan of either unit. It does not change the cell sizes above. It weakly suggests that JPL's own outreach drawing in October 1998 was drawn from something like the black unit's cell layout, not the silver unit's; that is an inference from one cartoon and settles nothing about the reference unit. Its lens decal (a ring around a crosshair) is round, like the silver unit's window, not the black unit's square one.

Wheel treads on the toy: the four printed strips come as two with one slant and two with the opposite slant, so the toy's four wheels are in mirror-image pairs. The real wheels are in mirror-image pairs too: the owner read the photos as front and rear opposite on one side, with the other side mirroring it, and my own check agrees on the silver unit and on the black unit's left side (not on the black unit's front-right wheel, which I read the other way). The owner then confirmed the choice on the side-by-side render of the CAD against the silver unit's photo (`photo_compare.py`), so the question is closed. The CAD now alternates handedness to match (`wheel-spec.md`, "Handedness alternates").

## What this does not give

Absolute accuracy better than a few percent, any dimension of the two faces not visible, the hub details (only partly visible), or the finish.
For authoritative dimensions the sources remain the papers and the JPL Robotics group.
