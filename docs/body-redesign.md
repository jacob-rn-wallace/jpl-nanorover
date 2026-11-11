# Body redesign: carbon fibre or forged carbon (started 2026-11-11)

**Owner's decision (2026-11-11):** the body is carbon fibre or forged carbon, 140 x 140 x 60 mm (the papers' figures; the reference unit is still undecided, so no change to size), replacing the 961 g Hammond box (`body-spec.md`, which stays as the record of the earlier body). Not yet chosen: layup versus forged carbon, and how it is made.

## Requirements it must meet (from `handover.md`, section 12)
- About **386 g** for body, electronics, solar cells and camera (1.0 kg design mass less about 614 g of servos, hub, struts, wheels and wheel drive).
- Hub holes opened to **24.2 mm**, on the middle of two opposite 140 x 60 faces, hub axis at 30 mm height.
- Room for four STS3215 servos, 45.23 x 24.73 x 32 mm (positions in `hardware/hub/hub.py`; shaft offset 10.2 mm, measured on Feetech's drawing, see `drivetrain-spec.md`), and the batteryless electronics.
- Centre of mass near the hub axis (the simulation's tip-over numbers assume it).
- **Edges (owner, 2026-11-11): crisp enough to look completely rectilinear, not sharp enough to injure; consumer-product crispness, which I take as an edge radius of about 0.5 to 1 mm.** A single layup over a plug is expected to leave about 1.5 to 3 mm at the corners (general practice, not sourced), so it is borderline at best.
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

~~**Recommendation: woven twill laminate, 4 to 5 plies (about 1.0 mm), made over a printed plug as a tub with a separate lid, with bonded printed or machined hub rings and bosses.** I would revisit forged carbon only for the lid or the bosses, if a mould becomes available. This follows from the 55 mm draw and the one-off nature of the build, not from strength.~~ **Superseded by the edge requirement:** **Revised recommendation (after the edge requirement above): woven carbon as six CNC-cut flat plates of about 1.0 mm, bonded into a box, with every outside edge broken to a 0.5 to 1 mm radius by hand and the cut edges sealed with epoxy; the lid is one plate that stays removable.** Flat plates give true flat faces meeting at a crisp edge with no tooling, and a flat face is the best surface for the solar cells. The cost is that the box is no longer seamless: each edge needs an inside key (a printed or carbon angle) to carry load and seal the joint, which I estimate at about 25 to 30 g with adhesive (my rough figure, not designed), and the cut fibre ends need sealing. A layup over a plug stays the fallback if you accept 1.5 to 3 mm corners; forged carbon is only worth it if a proper mould is available. Both choices follow from the edge and the build, not from strength. The inputs are mine or vendor-supplied and untested; a printed-plug test tub and a drop test would settle it.

## Cost: bonded woven plates versus forged carbon in 3D-printed moulds (2026-11-11)

Model: `hardware/body/cf_cost.py`; every input there is tagged **SRC** (a vendor page) or **ASM** (my assumption). Results in US dollars, low / mid / high; **shipping, import duty, dangerous-goods surcharges on resin, tax and your time are not included**, and the exchange rates (1 GBP = 1.30 USD, 1 ZAR = 0.055 USD) are assumptions. Treat the totals as order-of-magnitude.

### Sourced inputs
- **Woven sheet (Easy Composites, [1 mm high-strength twill sheet](https://www.easycomposites.co.uk/high-strength-carbon-fibre-sheet)):** GBP 257.78 per m2 ex VAT (so about GBP 61 for a 500 x 470 mm sheet; **the GBP 14.50 headline price is the smallest, 250 x 230 mm, sheet**, a correction to a first reading), sheets 250 x 230 to 2000 x 980 mm, 1, 2, 3 and 4 mm only (no 1.5 mm). Easy Composites **does not cut** sheet: it says to use a waterjet or CNC machinist. Rock West lists a 600 x 600 x 1 mm twill plate at USD 188.99 (a search snippet; the page I fetched showed no price, only options, so unconfirmed). Rock West also offers a custom-cut plate with a "forged/marbled" pattern option, on request for a quote; I did not get a price or confirm it is true chopped carbon.
- **Cutting:** Flying Robot ([CNC carbon cutting](https://flyingrobot.co/products/cnc-carbon-cutting-per-sq-cm), South Africa): ZAR 1.72 per cm2 for 1 mm, minimum 100 cm2, quote from a DXF. The only per-area price I found; other services quote per job. FMS Carbon says tolerance is about +-0.1 to 0.2 mm on thickness.
- **Forged materials (Easy Composites, [forged carbon kit](https://www.easycomposites.co.uk/forged-carbon-fibre-kit) and [compression moulding guide](https://www.easycomposites.co.uk/learning/compression-moulding-forged-carbon-fibre)):** kit GBP 66.63 ex VAT (750 g CT-12 chopped tow, 50 g long tow, 1 kg IN2 epoxy with fast hardener, release wax, gloves, pots; classed as dangerous goods for shipping); chopped tow GBP 8.65 per 150 g, IN2 fast GBP 22 per kg, release wax GBP 13.90, TC80 tool-cast epoxy GBP 67.50 for 5.3 kg. Recipe: fibre is 60% of the finished part mass, mix about 25% more resin than fibre weight, excess squeezed out. Rock West ([forged starter kit](https://sfccdev.rockwestcomposites.com/chopped-kit.html), a snippet from what looks like a staging site): USD 269.99 for 1.5 lb of 12 mm chopped carbon and West System slow epoxy.
- **Printed moulds (same guide, and [Dynamism](https://www.dynamism.com/learn/automotive/how-to-3d-print-carbon-fiber-molds.html)):** PETG at 75% infill or more and 0.15 mm layers or finer; FDM layer lines transfer to the part, so a good surface needs the mould sealed and coated; cure is at ambient temperature (a heated cure warps PETG moulds); **a printed mould suits "short runs and one-off prototypes", no count given**; cast epoxy tools are good for "tens if not hundreds" of parts. The mould needs "compression space" (a telescoping section at least 25% of the part depth) and 2 to 3 degrees of draft on the telescoping section. **No clamping force is given**; small moulds go in a vice or G-clamps, larger ones in a press. **Wall thickness: 1.5 mm is "very much towards the lower limit"** that can realistically be moulded.

### Result (mine; `cf_cost.py`)
| Bodies built | Bonded woven plates (low / mid / high) | Forged, printed moulds (low / mid / high) |
|---|---|---|
| 1 | $173 / $299 / $531 | $137 / $523 / $1,173 |
| 2 | $254 / $428 / $743 | $156 / $603 / $1,396 |
| 5 | $656 / $1,036 / $1,757 | $212 / $945 / $1,748 |
| 20 | $2,427 / $3,744 / $6,260 | $631 / $2,455 / $3,984 |

- **For one body the two overlap**, so cost does not decide it. At the mid assumptions woven is cheaper for 1 to 2 bodies, the two cross at about 4 or 5, and forged is cheaper beyond that, because the printed mould is paid for once and the plates' cutting cost recurs.
- **What drives each result:** for plates, the cutting price (the one sourced figure, South African, is the low case; mid and high are my guesses) and the sheet price. For forged, **how many parts a printed mould lasts (assumed 10 / 5 / 2), how many parts are lost learning a 55 mm deep 1.5 mm tub (1 / 3 / 5), and the press (a vice you own, or a shop press at about $250)**. None of these is sourced.
- **Material for the forged part is cheap:** about $18 to $46 per part at the listed prices. The cost is the tooling and the learning.
- **Printing:** the cavity block and plug are about 2 kg of PETG and, by my estimate, about 140 hours of printing on a hobby FDM machine. If you do not own a printer with a bed of at least about 170 mm, that is a cost not in the table.

### What the cost model does not capture (the real differences)
1. **Mass.** At 1.5 mm, the thinnest the source calls realistic, a forged shell is about **164 g** (at 2.0 mm about 218 g). The woven plate box is 113 g of plate plus about 25 to 30 g of keys and adhesive, about 140 g. With about 47 g of other allowances and 386 g to spend, forged leaves about 175 g for electronics, cells and camera, against about 200 g for plates. Not decisive, but it narrows the budget.
2. **Edges and draft.** A moulded forged tub can take its crisp edge from the printed mould's corner (about 0.5 to 1 mm is printable; the chopped material should flow into it, **my judgement, not sourced**), with no edge joint. But a pulled tub 55 mm deep needs draft: at 1 degree the sides lean about 1 mm each over the depth, at 2 degrees about 1.9 mm, which works against "completely rectilinear". The 2 to 3 degrees in the guide is for the telescoping section, not necessarily the outer faces, so the outer-face draft is unresolved. Plates have none.
3. **Surface.** FDM layer lines transfer to the part, so a consumer-grade finish needs a coated, sanded mould (in the cost) and probably clearcoat on the part.
4. **Risk and time.** A 55 mm deep 1.5 mm tub is at the edge of what the guide calls realistic; plates are a well-trodden route. By my estimate plates take about 8 hours of work against about 140 hours of printing plus finishing and trial pressings for forged, with an uncertain cure time (not stated by the source).
5. **Integral features.** A forged tub can mould in the bosses, hub rings and the lid lip, which the plate box buys as separate bonded parts.

### Reading
- **Forged with printed moulds is not meaningfully cheaper for one body.** Its low case is cheaper and its mid and high cases are well above plates; only a run of about five or more bodies shows a clear advantage.
- **What forged buys is integration** (no edge joints or keys, moulded bosses) **at the price of risk, time, a heavier shell and an unresolved draft problem.** What plates buy is a predictable, tooling-free route, flat faces for the cells, and no draft.
- **Revised recommendation stands (bonded woven plates)** for a first body. **A middle path worth testing cheaply:** print a small test mould for the lid or a corner and press one forged part, to see what edge radius, surface and thickness the process really gives before committing to the deep tub.
- **Uncertainty:** the table's gap between low and high is a factor of 3 to 8; the sourced prices pin only the materials. Get two quotes (a cutting service for the six plates, and a print or press) before treating any figure as a budget.

## Decision deferred; interior layout first (owner, 2026-11-11)

**The woven-versus-forged choice is deferred** until the interior is laid out, so the comparison can use real part placement instead of allowances. The layout is material-independent by design:
- **Keep-in volume:** the 140 x 140 x 60 mm envelope pulled in **2.5 mm** from every outer face (a 1.5 mm forged wall plus 1 mm of draft and tolerance; a 1.0 mm plate wall fits inside with room to spare), minus a **6 mm strip along every edge** (room for the plate box's bonded keys). If forged wins the keys disappear and the interior only gains room; designing for forged and then switching to plates would be the risky direction.
- **Fixed regardless:** the 24.2 mm hub bores, the servo and hub positions from `hub.py`, the window (26 mm, on the +y face at x = +40.8, z = 36.8), the headlamp about 30.6 mm toward -x of it.
- **What the layout feeds back to the comparison:** the real wall-thickness need (local thickening at the servos, board mounts, camera), the number and place of mounting bosses (many favour forged, which can mould them in; few favour bonded standoffs), whether the interior tolerates draft, the lid face and size, a measured mass, and a better cost model.
- **In parallel, if wanted:** a small printed test mould for a lid or corner (about $100) to see the real edge radius and surface forged gives.

## Interior layout, first pass (`hardware/body/layout.py`, 2026-11-11)

![body layout](images/body-layout.png)

Top view looking down with +y (the window end) at the top and **+x on the page's right, so the window at x = +40.8 appears on the right here; standing at +y facing the end face (the viewer's view) it is on the left.** The side view looks from +x with +y to the right. Servos grey, components coloured, the dashed line is the keep-in inset; overlaps between a component and a servo in one view are projection (they differ in the other axis).

**All component sizes and masses are placeholders (ASM): no electronics, camera, headlamp, antenna or cells have been chosen.** The servos and hub are the real modelled geometry from `hub.py`, with 1 mm clearance.

### What the numbers say
| | Result |
|---|---|
| Keep-in volume | 1,016 cm3 (of 1,176 cm3 envelope) after the 2.5 mm inset and 6 mm edge strips |
| Taken by servos and hub (1 mm clearance) | 198 cm3; **818 cm3 free** |
| Free bays | front (behind the window, y beyond servo B): 136 x 32 x 56 mm, 236 cm3; lower (under the servos): 136 x 136 x 15 mm, 268 cm3; upper (above them): 136 x 136 x 15 mm, 268 cm3; rear: 136 x 9 x 56 mm, only 62 cm3; centre gap between the two servo pairs: 16 mm wide x 136 x 56 mm, 121 cm3 |
| Placed placeholders | main board 70 x 68 x 7.6 mm (lower bay), power board 44 x 30 x 6 mm and a 35 x 35 x 4 mm patch antenna (upper bay), a 25 x 24 x 9 mm camera behind the window, a 22 x 14.5 x 15 mm headlamp: all clear of the keep-in limits, the servos and each other; **they use 7% of the free volume** |

- **Volume is not the constraint; mass is.** With over 800 cm3 free and the placeholders using 61 cm3, the box has far more room than it needs. The 386 g budget is the tight resource.
- **Solar cells are the biggest unknown in the mass budget.** Cells on four faces at 60% coverage are about 560 cm2 x 0.6; at an assumed 0.15 to 0.35 g/cm2 (**no cell chosen**) that is 50 to 118 g. Total body contents (shell, rings and screws 32 g, seal 15 g, electronics and wiring 85 g, cells):

| Shell | cells 0.15 g/cm2 | 0.25 | 0.35 |
|---|---|---|---|
| woven plates 1.0 mm + keys (141 g) | 323 g (63 g under 386) | 357 g (29 g under) | 391 g (5 g over) |
| forged tub 1.5 mm (164 g) | 346 g (40 g under) | 380 g (6 g under) | 414 g (28 g over) |

  So **the shell choice is worth about 23 g, the cell choice 68 g.** Forged at 1.5 mm is only workable with light cells, and plates with all but the heaviest. Light cells matter more than the shell material.
- **Balance.** The simulation put the whole rover's centre of mass 2.9 mm toward -y of the hub axis because the two servos on a side sit at different y (servo B +12.4, servo A -35.4 mm). With the camera, headlamp and main board toward the +y end, the body contents' centre of mass is at **y = +5.7 mm** (z = 29.1 mm against the hub at 30), which moves the whole rover's to **y = -0.9 mm** (z shift 0.3 mm). A 386 g body would need +7.5 mm to centre it exactly. This is a good side effect of putting the camera at the window end; the sim's tip-over numbers improve slightly (not re-run).

### Cautions
- The 1 mm voxel grid and 1 mm clearance make the checks good to about 1 mm. The servo connector side, cable bends, the hub housing's retention and the strut stops are not modelled.
- The antenna in the top face needs a non-conductive window; with a carbon body it cannot sit behind a bare top.
- The camera and headlamp positions put their mass at the front, which also moves the centre of mass; changing them changes the balance.
- Nothing has been placed for the lid screws, board standoffs, camera mounts, sealing or the wiring paths.

### Next
1. Choose cells (the 68 g spread), and a board/camera/lamp, so the placeholders become parts.
2. Decide the lid face, which fixes the joints and the seal for either shell material.
3. Re-run the comparison (`cf_cost.py`, `cf_compare.py`) with the real wall thickness, mount count and mass.

## Open decisions (owner)
1. **Woven laminate or forged carbon** (revised recommendation: woven plates bonded into a box, for the crisp edges), and the manufacturing route (a mould from a printed plug, CNC-cut plate bonded into a box, or a bought moulded part).
2. **Closed shell or open frame:** a sealed box is not required by the scope (no spaceflight), but dust and water tolerance would need deciding.
3. Antenna: a real patch behind a window, or a dummy.

## Next steps
1. Choose between woven and forged, and the route.
2. A parametric CAD shell (`hardware/body/`) at 140 x 140 x 60 mm with the hub bores, servo clearance from `hub.py`, a lid flange and a window, and a mass check against the budget above.
3. Place the electronics, cells and camera, and check the centre of mass.
