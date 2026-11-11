# Body redesign: carbon fibre or forged carbon (started 2026-11-11)

**Owner's decision (2026-11-11):** the body is carbon fibre or forged carbon, 140 x 140 x 60 mm (the papers' figures; the reference unit is still undecided, so no change to size), replacing the 961 g Hammond box (`body-spec.md`, which stays as the record of the earlier body). Not yet chosen: layup versus forged carbon, and how it is made.

## Requirements it must meet (from `handover.md`, section 12)
- About **386 g** for body, electronics, solar cells and camera (1.0 kg design mass less about 614 g of servos, hub, struts, wheels and wheel drive).
- Hub holes opened to **24.2 mm**, on the middle of two opposite 140 x 60 faces, hub axis at 30 mm height.
- Room for four STS3215 servos, 45.23 x 24.73 x 32 mm (positions in `hardware/hub/hub.py`; shaft offset 10.2 mm, measured on Feetech's drawing, see `drivetrain-spec.md`), and the batteryless electronics.
- Centre of mass near the hub axis (the simulation's tip-over numbers assume it).
- A sealed or at least dust-tight box, a window (26 mm, silver unit) and room for the headlamp and antenna.

## Mass budget (`hardware/body/cf_budget.py`; typical densities, not measured parts)
The outer surface is 728 cm2. A hollow shell with a lid, in grams:

| Wall | 0.8 mm | 1.0 | 1.2 | 1.5 | 2.0 |
|---|---|---|---|---|---|
| Woven CFRP laminate (1.55 g/cm3) | 90 | 113 | 135 | 169 | 226 |
| Forged carbon (1.45 g/cm3) | 84 | 106 | 127 | 158 | 211 |
| Sandwich, 0.3 mm skins on 0.06 g/cm3 foam | 69 | 69 | 70 | 72 | 74 |

With about 47 g for inserts, hub-bore rings and gasket (my allowance: 4 x 2 g screws and inserts, 4 x 6 g bore rings, 15 g seal), a 1.0 mm woven shell leaves about 226 g for electronics, cells, camera and wiring; 1.5 mm leaves about 170 g; 2.0 mm about 113 g. **So the mass target closes, with a wall of about 1 to 1.5 mm; the Hammond box could not (961 g).** Not yet known: how much the electronics, cells and camera weigh (no parts chosen), and whether 1 mm is stiff enough at the hub holes.

## Things carbon changes (to design for, none yet modelled)
1. **Radio.** Carbon is conductive and blocks RF: the patch antenna on top (papers) needs a non-conductive window or panel, and the headlamp and camera windows need their own cutouts.
2. **Insulating the cells and electronics.** The laminate conducts: solar cells, wiring and the board need an insulating layer or standoffs. Cells bonded to bare carbon would short.
3. **Galvanic corrosion.** Carbon against aluminium in a damp joint corrodes the aluminium; use insulating washers, coatings or stainless/titanium hardware at the hub rings and inserts.
4. **Hub loads.** The strut hub loads go into a thin shell (hold torque up to 0.166 N.m per strut plus wheel loads in a drop): the hub bores need a bonded reinforcing ring or local thickening; the hub housing's flange (28 mm, `hub.py`) spreads the load.
5. **Corners and joints.** A box of continuous fibre needs a mould or plug; flat plate bonded into a box is simpler but its corner joints decide stiffness and sealing. Forged carbon (chopped prepreg, compression-moulded) can form bosses, ribs and a lid lip in one piece, but needs a metal mould (cost), and its strength is lower and less predictable than woven laminate.
6. **Sealing.** The earlier O-ring in a groove in a lid plate (`body-spec.md`) does not carry over; a moulded lip, a gasket on a flat flange, or a bonded joint needs choosing.
7. **Thermal.** The cast box was the servos' and electronics' heat path; carbon (laminate) conducts poorly through the thickness. The servo hold test (`handover.md`, section 12, item 6) matters more.

## Woven laminate versus forged carbon (deeper comparison, 2026-11-11)

Numbers by `hardware/body/cf_compare.py`. **Sourced** = from a cited page; **mine** = my arithmetic; **unverified** = a typical value I did not find a source for.

### What the sources say
- **Forged carbon (Easy Composites, [mechanical properties of forged carbon fibre](https://www.easycomposites.eu/learning/mechanical-properties-of-forged-carbon-fibre); sourced, but the page says "no formal ISO or ASTM standards were applied", gives no specimen size, no scatter and no fibre fraction, and calls the results comparative):** density 1.5 g/cm3; tensile yield 192 MPa and flexural modulus 35.5 GPa for standard forged carbon; an "optimised" version with continuous tow added reaches 875 MPa and 61.1 GPa at 1.58 g/cm3 (continuous tow should not exceed about 50% of the carbon weight, or voids are likely). Recommended wall 1 to 10 mm, features under about 0.5 mm avoided, resin Tg about 92 C for the IN2 system or over 160 C for EL160, "small to medium" parts (about 500 x 500 mm at most).
- **Woven or 0/90 laminate ([DragonPlate FAQ](https://dragonplate.com/just-how-strong-is-carbon-fiber); sourced, generic):** about 600 MPa tensile strength and about 70 GPa tensile modulus for a balanced 0/90 laminate. The script uses a flexural modulus of 50 to 70 GPa (mid 55); that range is a typical figure, **unverified** for any particular layup.
- **A Warsaw University of Technology conference abstract ([PDF](https://read.meil.pw.edu.pl/wp-content/uploads/Program/2026/Abstracts/ID40.pdf); sourced, truncated):** forged carbon is highly isotropic in-plane, with lower absolute tensile strength than unidirectional laminates; fibre length (6 versus 15 mm) matters.
- **Rock West Composites' forged blocks ([datasheet](https://www.rockwestcomposites.com/downloads/RWC_forgedblocks_tds.pdf); sourced):** tensile strength over 113.7 MPa and modulus over 46.88 GPa, but the datasheet says these come from mathematical models and need testing.
- **Tooling and process ([HPA, compression moulding and forged carbon](https://www.hpacademy.com/courses/motorsport-composite-fundamentals/construction-techniques-compression-moulding-and-forged-carbon/); a summary page):** forged carbon is a high-volume process with a costly compression mould (an illustrative $25,000 mould and $100 part in one source, not a quote). Cheaper routes mentioned: hand-placed chopped fibre in a mould, chopped prepreg sheet, and dry chopped tow with liquid epoxy in an FDM-printed compression mould (no costs given). A practitioner forum post says chopped moulding compound suits cosmetic parts and that for a highly loaded structural piece they want a fabric or unidirectional layup.
- **RF ([Mobility Engineering Tech, composite enclosures](https://www.mobilityengineeringtech.com/component/content/article/40988-sae-ma-00113) and others; sourced, general):** carbon-fibre enclosures give modest shielding (about 20 to 40 dB), and a shielded box's leakage is dominated by its apertures and joints, not its walls. That applies to both materials equally: neither lets an antenna radiate from inside.
- **Not found:** through-thickness thermal conductivity of either material, galvanic corrosion data for carbon on aluminium, and a minimum wall for compression-moulded forged carbon beyond Easy Composites' "at least 1 mm". The corrosion and thermal points here are from general knowledge, **unverified**.

### What the project's own numbers say (mine)
| Question | Result |
|---|---|
| Wall for the same panel stiffness as 1.0 mm woven (E 55 GPa) | forged standard 1.16 mm (+12% shell mass); forged optimised 0.97 mm (-2%); woven E 70 gives 0.92 mm |
| Are the hub loads a strength problem? | No. 1.0 kg, half on each hub: 0.2 MPa bearing on a 1 mm wall (4 MPa for a 20 g impact), bond shear 0.16 MPa from 0.33 N.m. About 50 times below even the standard forged figure |
| Is heat a problem? | No. About 0.8 W for four servos holding, about 1.6 K rise over a 0.073 m2 box in still air (servo current assumed proportional to torque; idle 0.1 W each assumed) |
| Plies for a 1.0 mm woven wall | 4 to 5 plies of 200 gsm twill, or 4 of 245 gsm (at 50% fibre volume) |

The hub-load result covers only the hub. **A drop on a corner or edge, and a wheel strike, are not analysed**, and that is where the materials differ most: woven fabric is stiffer and stronger per mass, while forged is isotropic and damage-tolerant in all directions (a vendor claim, [Nitpro](https://www.nitprocomposites.com/blog/carbon-fiber-reinforced-polymer-vs-forged-carbon-whats-the-difference); unverified).

### How each is made at this size (a 140 x 140 x 55 mm tub, about 1 mm wall)
| | Woven laminate | Forged carbon |
|---|---|---|
| Hobby route | Wet layup or vacuum bag over a male plug (printed or machined), or CNC-cut flat plate bonded into a box with corner fillets | Dry chopped tow plus liquid epoxy pressed in a printed two-part mould, or chopped prepreg in a metal mould and heated press |
| Tooling | One plug (printed or foam); no press | A two-part matched mould that withstands pressing; a metal one is the costly case. Needs draft (about 3 degrees assumed) |
| A 55 mm deep tub with 1 mm walls | Easy: plies drape over the plug; corners need small radii | The hard case: chopped material must flow 55 mm up thin walls, so voids, thin spots and resin-rich corners are likely (**my judgement, not sourced**) |
| Bosses, ribs, lid lip | Bonded on (printed or machined inserts) or built up | Can be moulded in one piece: the real advantage |
| Holes (hub bore 24.2 mm, window) | Drilled or routed after cure, with backing against delamination; the dust is conductive and an irritant | Same; no ply delamination in an isotropic part |
| Finish | The weave shows through a clear coat (or it is painted) | Marbled; fine detail is softened, per Easy Composites |
| Repeatability | Good with a controlled layup | Depends on how evenly the chips are placed |

### Reading
- **Neither is chosen by strength or heat.** Both are far over the loads that were computed.
- **Woven laminate** suits a thin, deep, 1 mm tub better: equal or lighter at equal stiffness, a cheap one-off route (one plug), and predictable. It cannot form bosses, so bosses are bonded on.
- **Forged carbon** earns its place only if the body needs integral bosses, ribs and a lid lip in one piece **and** a proper mould is affordable. Its cheap hobby route is weakest at exactly the 55 mm-deep thin-walled shape the tub needs. The marbled look is its main non-structural draw, and a painted or wrapped body, as the black and silver units are, cancels that.
- **A hybrid** is possible: a woven tub with moulded forged or printed bosses and hub rings bonded in. It adds a joint but puts each material where it is good.
- **Appearance against the originals:** the black unit's body is black and the silver unit's silver (`design-comparison.md`); a bare carbon body matches neither, whichever type. If looking like the originals matters, either type needs finishing, and then the look argument for forged disappears.

**Recommendation: woven twill laminate, 4 to 5 plies (about 1.0 mm), made over a printed plug as a tub with a separate lid, with bonded printed or machined hub rings and bosses.** I would revisit forged carbon only for the lid or the bosses, if a mould becomes available. This follows from the 55 mm draw and the one-off nature of the build, not from strength. The inputs are mine or vendor-supplied and untested; a printed-plug test tub and a drop test would settle it.

## Open decisions (owner)
1. **Woven laminate or forged carbon** (recommendation above: woven twill over a printed plug), and the manufacturing route (a mould from a printed plug, CNC-cut plate bonded into a box, or a bought moulded part).
2. **Closed shell or open frame:** a sealed box is not required by the scope (no spaceflight), but dust and water tolerance would need deciding.
3. Antenna: a real patch behind a window, or a dummy.

## Next steps
1. Choose between woven and forged, and the route.
2. A parametric CAD shell (`hardware/body/`) at 140 x 140 x 60 mm with the hub bores, servo clearance from `hub.py`, a lid flange and a window, and a mass check against the budget above.
3. Place the electronics, cells and camera, and check the centre of mass.
