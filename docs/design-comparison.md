# Three designs, and what the CAD is

The project draws on three descriptions of "the JPL nanorover" that do not agree, and the CAD (`hardware/`) is a fourth, hybrid model. This page records them side by side so the choice
of what to replicate is made once, in one place. Status: **the reference unit is undecided** (owner, 2026-11-10). Until it is, the CAD keeps the papers' body and strut figures.

## The three designs

| | A. The published MUSES-CN design | B. The silver-bodied unit | C. The black-bodied unit |
|---|---|---|---|
| Where it comes from | Wilcox & Jones, Jones & Wilcox (1999 to 2000), four papers | `NanoRover-hires.original.jpg` (JPL research page, "Prototype of the nanorover, only 20cm long"); shown with its body open and the optics in JPL's 1997 video | `img840-340-hires.original.jpg` (JPL gallery, "Nanorover (circa 1997)"); seen running in JPL's 1997 and 1998 videos, in a 1997 KTLA news segment (owner's statement; not viewed), and as an animation in the saved IROS'97 page |
| Role (owner's account) | the intended flight vehicle | internal test unit that carried the science optics; used to demonstrate the optical train and teleoperation | running mock-up with no instruments, used for publicity |
| Body | 14 x 14 x 6 cm, mass 1300 g | about 138 x 154 x 61 mm (scaled from its wheels) | about 155 x 155 x 45 mm (scaled from its wheels, with the shared drivetrain; 140 x 140 if its top face is taken as the papers' size) |
| Struts | 7 cm, pivot to wheel axis | about 86 mm | same as B (shared drivetrain; 75.9 mm on the 140 mm scale) |
| Wheels | 6.5 cm; "a complex assembly of thin conductors and insulator" that also senses ground contact; banded cylinders in JPL's 1998 video | cone on a smooth cylinder with 16 helical serrated grousers, about 65 mm across them (normalised to the papers' size) | same as B (owner: identical struts and wheels) |
| Camera window | one on the front face, for the camera and IR spectrometer | round window, 26 mm, plus a tilted sealed-beam headlamp, on one end face | square window, about 28 x 24 mm, fixed over the opening with adhesive, on the opposite end face from B's (owner's reading) |
| Solar cells | four of six faces; the antenna on the top face | top face: 14 flat cells plus cells on a raised block; an antenna loop and a bone-shaped piece on top | top face: about 14 flat cells plus cells on a raised block |
| Finish | not stated | bare aluminium | black enclosure with a green PCB-like base seam |

Sizes in B and C are photogrammetric estimates (see `photo-measurements.md`): they depend on taking the wheels as 65 mm across the grousers and on how the camera was solved, and are uncertain by several percent.
The papers' wheel is a different design from B and C's, and the papers' strut/wheel ratio (1.08) differs from the units' (about 1.3).

## What the evidence says

- **B and C share a drivetrain** (owner). A cross-check supports it: scaling each photo by its own wheels gives the same strut-to-wheel ratio to 3% (1.32 and 1.29) and the same wheel position outboard of the body to about 4 mm.
- **B's hub faces are the papers' 14 x 6 cm** (138 x 61 mm). Its length, about 154 mm, is not 14 cm. C is square, but about 155 mm square and about 45 mm tall: neither unit is 14 x 14 x 6.
- **The height fits the owner's account.** The instrument stack sets B's height; a mock-up without the optical bench would be thinner, as C is.
- **Which was built first, and which is closer to flight, cannot be told from what has been read.** The JPL captions give only "circa 1997" for C. The 1998 animation of the flight vehicle has a round window and a rectangular panel on one end face, which resembles B more than C, but it also has banded wheels that match neither.

## What the CAD is today

A hybrid: the **papers' body size** (140 x 140 x 60 mm, which B's hub faces match), the **papers' 70 mm struts**, the **units' cleated wheel** (the owner chose it over the papers' banded wheel),
**B's round window** (the headlamp is not modelled yet), and **C's-photo-derived solar cell sizes** (at the 140 mm scale; about 11% larger under the shared-drivetrain scale). It is good for fit checks and mechanics. It is not any one of A, B or C.

## What choosing would change

| If the replica follows | Body | Struts | Wheel | End face |
|---|---|---|---|---|
| A, the published design | 140 x 140 x 60 | 70 mm | banded cylinder | one window |
| B, the silver unit | about 138 x 154 x 61 (a 154 mm box, not the Hammond 140 mm one) | about 86 mm | cleated (as now) | round window plus headlamp |
| C, the black unit | about 155 x 155 x 45 | about 86 mm | cleated (as now) | square bonded window, black finish |
| A hybrid (today) | 140 x 140 x 60 | 70 mm | cleated | round window |

Choices that do not depend on the unit: four wheels on two hubs with independently posable struts, a flat sealed box, cells on top, the hub studs and the O-ring lid.

## Open questions

1. Which unit, or which design, is the replica of? (owner: not sure)
2. If B or C: strut length 86 mm instead of 70 mm, and a body 154 or 155 mm long instead of 140 mm (the Hammond 1590Z090 box is 140 x 140).
3. If A: the wheel would change from the cleated wheel to the banded cylinder.
4. What a "looks-like replica" should copy from C (the black finish, the square window) if the dimensions follow B.
