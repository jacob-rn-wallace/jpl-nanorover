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
| Scale | the top face is taken as **140 mm** square (MUSES-CN, 14 x 14 x 6 cm). That is an assumption: the quarter alone allows roughly 130 to 140 mm, and the photo's own caption says "approximately 10 cm on a side", which the square face and the quarter rule out |

## Solar cells on the top face (top view, millimetres at the 140 mm scale)

| Cells | Count | Size | Notes |
|---|---|---|---|
| Large cells, left and right columns | 5 + 5 | about 39.6 x 23.5 | widths measured 39 to 40.7 depending on the cell; the middle cells of each column almost touch (about 1 mm showing) |
| End cells of those columns | | about 21 to 22 tall at the top end, 23.5 at the bottom end | the top end cell's height is the least certain |
| Centre cells (two above, two below the central block) | 4 | about 19.6 x 44 | the long side is partly hidden by the central block: plus or minus 2 mm |
| Central raised block | 1 | not measured | carries at least two more small cells on its sloped faces |

Gaps: about 7 mm between the first and second large cells of a column, about 5 mm between the fourth and fifth, and black strips 5 to 8 mm wide between columns.
Total on the flat top face: 14 cells (plus the cells on the central block). Uncertainty: about 1 mm from locating the face edges, and about 2% from cell to cell.

## Wheel (see `wheel-spec.md`)

First photo: projecting circles on the wheel axis onto the photo gives a smooth outer disk of radius 27 mm, saw-tooth tips at radius about 29.5 mm (about 59 mm across the
teeth), a collar centre 5 mm outboard of the disk, and a stack reaching about 33 to 36 mm inboard. The strut angles solve to about 7 and 9 degrees below horizontal and
the collar plane about 51 mm outboard of the body's side face. If the true body is smaller than 140 mm these lengths scale with it.

## Second photograph: `NanoRover-hires.original.jpg` (997 x 750 px)

A silver-bodied unit (bare aluminium, a round window and a connector on one end face, an antenna loop and a raised block on the top, cells in a different layout
from the first photo). Same method: about 440 line segments along the cell edges, vanishing points, focal length about 1920 px (a 29 degree field of view), the camera looking at the top face from about 38 degrees above it.

- **Top face:** rectified, it measures about 518 x 465 px, **1.11:1, not square**. This is a different unit from the first photo's square body, and not 14 x 14 cm.
- **Wheels:** two wheels are seen almost edge-on (the axle 78 to 80 degrees from the viewing ray), which shows the cone profile directly. The collar sits on a cone apex about 10 mm
  above the rim; the drum behind it has diagonal saw-tooth grousers, 16 of them, leaning about 43.5 degrees from the axle, right-handed. See `wheel-spec.md` for the table.
- **Not yet measured from this photo:** the body's height and length (the window face and the raised block on top are the first things worth measuring, for the camera window).

## What this does not give

Absolute accuracy better than a few percent, any dimension of the two faces not visible, the hub details (only partly visible), or the finish.
For authoritative dimensions the sources remain the papers and the JPL Robotics group.
