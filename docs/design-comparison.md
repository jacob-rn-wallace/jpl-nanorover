# Three designs, and what the CAD is

The project draws on three descriptions of "the JPL nanorover" that do not agree, and the CAD (`hardware/`) is a fourth, hybrid model. This page records them side by side so the choice
of what to replicate is made once, in one place. Status: **the reference unit is undecided** (owner, 2026-11-10). Until it is, the CAD keeps the papers' body and strut figures.

## The three designs

| | A. The published MUSES-CN design | B. The silver-bodied unit | C. The black-bodied unit |
|---|---|---|---|
| Where it comes from | Wilcox & Jones, Jones & Wilcox (1999 to 2000), four papers; one sentence repeated in all four: "Each strut is 7 cm long from the center of their pivot to the center of the wheel axis" | `NanoRover-hires.original.jpg` (JPL research page, "Prototype of the nanorover, only 20cm long"); **the same photograph is Figure 1 of Jones & Wilcox 2000**; shown with its body open and the optics in JPL's 1997 video | `img840-340-hires.original.jpg` (JPL gallery, "Nanorover (circa 1997)"); seen running in JPL's 1997 and 1998 videos, in a 1997 KTLA news segment (owner's statement; not viewed), and as an animation in the saved IROS'97 page |
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

- **The papers' own rover figure is the silver unit.** Figure 1 of Jones & Wilcox (2000) is the same photograph as `NanoRover-hires.original.jpg`: the silver body, round window, headlamp, antenna loop and the same rock. So the papers' text (14 x 14 x 6 cm, 6.5 cm wheels, 7 cm struts) is illustrated by unit B, and A and B are not independent sources. The strut figure is stated only in the four Jones/Wilcox papers (one author pair repeating one sentence); Tunstel (1999) and Weisbin (1998) do not give a strut length.
- **B and C share a drivetrain** (owner). A cross-check supports it: scaling each photo by its own wheels gives the same strut-to-wheel ratio to 3% (1.32 and 1.29) and the same wheel position outboard of the body to about 4 mm.
- **B's hub faces are the papers' 14 x 6 cm** (138 x 61 mm). Its length, about 154 mm, is not 14 cm. C is square, but about 155 mm square and about 45 mm tall: neither unit is 14 x 14 x 6.
- **The height fits the owner's account.** The instrument stack sets B's height; a mock-up without the optical bench would be thinner, as C is.
- **Which was built first, and which is closer to flight, cannot be told from what has been read.** The JPL captions give only "circa 1997" for C. The 1998 animation of the flight vehicle has a round window and a rectangular panel on one end face, which resembles B more than C, but it also has banded wheels that match neither.

## What the CAD is today

A hybrid: the **papers' body size** (140 x 140 x 60 mm, which B's hub faces match), the **papers' 70 mm struts**, the **units' cleated wheel** (the owner chose it over the papers' banded wheel),
**B's round window** (the headlamp is not modelled yet), and **C's-photo-derived solar cell sizes** (at the 140 mm scale; about 11% larger under the shared-drivetrain scale). It is good for fit checks and mechanics. It is not any one of A, B or C.

## Rule for settling values, and what it locks (proposed by the owner 2026-11-10, with two amendments)

**Rule.** A value is authoritative when at least two of the three designs (A the papers, B the silver unit, C the black unit) agree on it. Amendments: (1) votes must be independent: B and C share the same struts and wheels (owner), so for anything that is part of the drivetrain they count as **one** vote; (2) B's and C's absolute sizes were scaled from A's 65 mm wheel, so they cannot confirm A's absolute numbers, only scale-free ratios (for example B's hub face is 0.44 high to wide, against A's 0.43). Agreement must hold within the stated uncertainty. A tie stays open and is decided by the owner.

**Locked (all three agree):**
- Four wheels on four independently posable struts.
- The struts are on hubs at the centre of two opposite faces of the body.
- A flat rectangular box body.
- Solar cells on the top face.
- An imaging window on one end face.

**Locked (two independent votes):**
- Height about 60 mm: A 60 mm, B 61 mm (the ratio of height to width agrees independently of scale).
- Hub-axis width about 140 mm: A 140 mm, B 138 mm.
- A square footprint: A 14 x 14 cm and C square (scale-free). B's 1.11 : 1 is the outvoted exception.

So the rule gives a **140 x 140 x 60 mm body**, which is what the CAD already has.

**Open (no two independent votes agree):**
- Strut length: A 70 mm against B and C together about 86 mm (one vote each).
- Wheel construction: A banded cylinder against B and C together cleated. The owner chose the cleated wheel, a decision outside the rule.
- Window shape (round on B, square on C, not stated in A), its size, and whether there is a headlamp (B only).
- Body finish, solar cell layout and counts, the antenna, and the mass (only A gives one).
- Body length where it matters (B about 154 mm; A and C say square): decided by the square-footprint vote above, so 140 mm.

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
