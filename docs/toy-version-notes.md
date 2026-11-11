# Notes on a toy-grade or hobby version

A side discussion (2026-11-10): strip the nanorover to its camera, drop flight qualification, and what is left is a compact, light, cheap all-terrain remote-control robot. Could that have been sold as a toy around 2000, and should the project pivot to such a version?
Nothing here is decided. It is recorded because it bears on the project's purpose (`handover.md`, open decisions).

## Could it have been a product around 2000? (an assessment, not research)

**Yes as a premium hobby gadget, not as a mass-market toy.**
- **Enablers.** CMOS image sensors were commercial: Eric Fossum's JPL active-pixel sensor was licensed to Photobit in 1995 (acquired by Micron in 2001). Wireless 2.4 GHz cameras were on sale by 2000 (X10's XCam2; a related X10 kit cost $199.99 in December 1999). NASA-licensed rover toys sold: Mattel's 1997 Hot Wheels Sojourner, made under a JPL licence (no radio control; no sales figures found).
- **Obstacles.** Eight actuators (four wheel motors and four strut motors) with gearboxes and position sensing, against the two motors of an ordinary radio-controlled toy; the camera and video link as the largest cost; short battery life; four independently posed struts are hard for a child to drive without preset behaviours; a toy bill of materials of roughly $15 to $25.
- **Rough cost sketch (my estimate).** With a camera: bill of materials $70 to $135, retail $200 to $400. Without it: $40 to $75, retail $100 to $200.
- **Real comparison.** Plantraco's Desktop Rover (a 4-inch two-motor tracked radio-controlled vehicle "inspired by NASA Planetary Exploration Missions") sold for $60 in 2002, and its PTV16C wireless video camera kit for $120: about $180 together. Camera rovers became mass-market later (WowWee Rovio and Spykee, around 2008). So a nanorover-class toy with a camera in 2000 would have been early but not impossible.

## Sources

- Matt Neuburg, "Desktop Rover Scores a Hit", TidBITS, 3 June 2002: https://tidbits.com/2002/06/03/desktop-rover-scores-a-hit/ (the $60 rover; its camera sends UHF channel 16 or 19 to any TV).
- Plantraco Desktop Rover page, archived 2 April 2002: https://web.archive.org/web/20020402182146/http://www.plantraco.com/product_dtr.html (infrared laser tag, the Telecommander PC interface, the optional PTV16C camera).
- Plantraco PTV16 wireless video camera page, archived 2 June 2002: https://web.archive.org/web/20020602040149/http://www.plantraco.com/product_ptv16.html ($120; 9 V battery; UHF channel 16; 150 ft range; FCC part 15; the page labels a "CMOS camera lens" but its text says "CCD"). The Wayback pages open in a browser; the author's fetch tool could not read them, so they were downloaded directly.
- JPL, "Mattel release toy of Sojourner rover": https://www.jpl.nasa.gov/news/mattel-release-toy-of-sojourner-rover/ (the licensing route).
- Photobit and the JPL sensor: https://en.wikipedia.org/wiki/Eric_Fossum; https://spectrum.ieee.org/tech-history/silicon-revolution/chip-hall-of-fame-photobit-pb100
- Not confirmed: prices of Sony's AIBO, Lego Mindstorms (1998) and Furby; the XCam2's launch price.

## The question of a pivot

The owner's observation: whatever is built will never fly, and the nanorover was never finished, so any replica interprets a design that never materialised. The assessment: the flight design never existed, but the two prototypes were real hardware that ran, and a replica of those is a replica of real objects; flight was out of scope from the start.
Options discussed: keep a faithful replica; build a functional toy-grade rover first (printed or laser-cut body at the same envelope, off-the-shelf motors and a camera module, no sealing; a modern build might cost on the order of $60 to $100, not priced) and the faithful version after; or an open design others can build cheaply. A middle path: a cheap working proof of concept to test the four-strut mobility, then the faithful build.
The owner's decision: defer the body and work on the drivetrain, which both units share and which is the same in all three paths.
