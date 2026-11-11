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

## Open decisions (owner)
1. **Woven laminate or forged carbon**, and the manufacturing route (a mould from a printed plug, CNC-cut plate bonded into a box, or a bought moulded part).
2. **Closed shell or open frame:** a sealed box is not required by the scope (no spaceflight), but dust and water tolerance would need deciding.
3. Antenna: a real patch behind a window, or a dummy.

## Next steps
1. Choose between woven and forged, and the route.
2. A parametric CAD shell (`hardware/body/`) at 140 x 140 x 60 mm with the hub bores, servo clearance from `hub.py`, a lid flange and a window, and a mass check against the budget above.
3. Place the electronics, cells and camera, and check the centre of mass.
