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

## Owner's layout decisions and power study (2026-11-11)

**Decisions (owner), recorded in `CLAUDE.md`:**
1. **Top and bottom faces are the lids**, identical, each carrying solar cells so the rover works as well upside down; cells also on the front and back (end) faces, as the papers planned (cells on four of six faces); none on the hub faces, where the struts are.
2. **The body is kept symmetric about the transverse (z = 30) plane**: for a centred centre of mass and so the same parts can be reused around the body.
3. **Camera window centred on a 60 x 60 mm square at one end of an end face**, i.e. 30 mm from the top, bottom and side edges: x = +40, z = 30 on the +y face. (The earlier window, copied from the silver unit, was at x = +40.8, z = 36.8.)
4. **One window shared by camera and lamp**, through a beamsplitter.
5. **Antenna on the opposite end face, at the diagonally opposite position** (x = -40, z = 30 on the -y face: a 180 degree turn about z carries the camera's square onto the antenna's), a whip standing vertically in the plane of the face, on a low-friction pivot with a counterweight so it points up whichever way up the rover is.

**These are deliberate departures from all three descriptions of the original** (papers, silver unit, black unit): none has cells on a bottom lid, a shared camera and lamp window, or a gravity-oriented antenna. The papers' own antenna is a patch on the top face.

### Solar cells: target layout and area
- **Top and bottom faces (each):** the black unit's measured top-face layout (`photo-measurements.md`): 10 large cells of about 39.6 x 23.5 mm in two columns of five, and 4 centre cells of about 19.6 x 44 mm (plus or minus 2 mm), with gaps of 5 to 8 mm: **127.6 cm2 per face (65% of the 196 cm2 face)**. The NASA Space Place toy decal has 5 + 5 edge rows, 4 centre cells and 2 + 2 more on the other edges, 18 flat cells; it is a simplified drawing, so I used the measured layout. The black unit's raised centre block is left out: the antenna no longer goes there.
- **End faces (each):** the 60 x 60 mm window or antenna square leaves an 80 x 60 mm area; **three cells of 23.5 x 39.6 mm standing side by side fit** (about 76.5 mm with 3 mm gaps), **27.9 cm2 each**. No source gives an end-face layout; this is my choice. The two end faces are 180 degrees symmetric.
- **Total 311 cm2** (top 127.6 + bottom 127.6 + two ends 55.8). Mass at an assumed 0.15 to 0.35 g/cm2 (no cell chosen) is **47 to 109 g**; the bottom face alone is 19 to 45 g.

### Power: what the cells can supply (`hardware/body/power_budget.py`)
Sourced: 1000 W/m2 AM1.5 full sun; measured output at 500 lux LED of about 8 uW/cm2 (polycrystalline silicon) and 10 uW/cm2 (amorphous silicon) (from a web-search summary of indoor-photovoltaic studies; **I did not open the paper that reports them, so the figures are unconfirmed**; related background: [MDPI, typical artificial light sources for indoor PV](https://www.mdpi.com/1996-1073/7/3/1500)); STS3215 about 180 mA moving at 12 V and a standby draw between 6 mA (datasheet) and 60 mA (some listings), sources disagree; a bare ESP32-S3 deep sleep of 7 to 8 uA ([Lucidar](https://lucidar.me/en/esp32/power-consumption-of-esp32-s3-devkitm-1/)) and about 31.7 mA connected on a dev board. Assumed (**ASM**): cell efficiency 15 / 20 / 24%, a 10% overcast, radio transmit 0.65 W, camera 0.3 W, lamp 0.2 W, wheel motors about 0.1 W each.

| One lit face supplies | Power |
|---|---|
| Full sun, square to it (20% cells) | **2.55 W** (1.9 to 3.1 W over the efficiency range) |
| Full sun, 45 degrees off | 1.8 W |
| Thin overcast (ASM) | 0.26 W |
| **Indoors, 500 lux LED** | **about 1 to 1.3 mW** |

| Scenario | Load |
|---|---|
| A keep-alive: MCU deep sleep, RTC, wake input | about 0.1 mW (ASM) |
| B controller awake, radio idle | 0.105 W |
| C camera, radio streaming and lamp | 1.26 W |
| D driving (wheels, controller, radio, camera; four servos holding at 30 mA each) | 2.9 W (servo hold alone is 1.4 W; 0.3 to 2.9 W over the standby range) |
| E posing one strut (one servo moving) | 4.5 W |

Surplus of one lit face (W): in full sun A +2.55, B +2.45, **C +1.30, D -0.34, E -1.94**; overcast A +0.26, B +0.15, C and beyond negative; **indoors only A is positive (+1 mW) and even B is short by 0.1 W**. A 500 mAh battery (1.85 Wh, about 12 g, ASM) runs scenario D for about 38 minutes, C for 88 minutes and B for 18 hours; indoors the panel adds 0.031 Wh a day, 1.7% of it.

**What this means for your two ideas:**
- **Panels charging the rover:** works **outdoors**: in sun an idle rover (B) nets +2.4 W and the battery refills in about 45 minutes; even thin overcast beats idle (+0.15 W). **Indoors it does not**: 1.3 mW is about 1% of idle-with-radio. So the panels are an outdoor charger and an indoor trickle at best.
- **A subsystem run directly from the panels, so battery loads can power down fully:** in sun the whole controller, radio, camera and lamp (C, 1.26 W) runs from one face with 1.3 W to spare, so that works outdoors. **Driving (D) and posing (E) exceed one face even in full sun**, so they need the battery (the cells extend its runtime). **Indoors the only thing the cells can run is a micro-power keep-alive** (scenario A, a timer or wake input, tens of microwatts), which is enough to let the battery loads hard-off with a load switch and be woken from outside.
- **Suggested architecture (mine, for your decision):** three tiers: a keep-alive controller on the cells with a small supercapacitor; the battery behind a load switch for everything else (hard off at idle); the cells topping up the battery outdoors. **Servo hold current is the biggest unknown and the biggest lever**: four servos holding is 0.3 to 2.9 W against the sources' 6 to 60 mA range, so test whether the STS3215 holds a pose unpowered (already in the handover's prototype tests); if it does, idle drops to the keep-alive.
- **The bottom cells** exist for inverted operation. Right way up they see almost no light (the floor is 32 mm below, in the rover's own shadow), so they cost 19 to 45 g for a use that is occasional. That is your choice; the numbers just show the price.
- Not decided: the cell type (a-Si does better indoors, crystalline outdoors; the indoor figures are roughly 8 to 10 uW/cm2 for either), the battery chemistry and voltage (the servos and wheel motors want 12 V and 6 V, so boost converters or a 2S pack, neither modelled), and the radio.

### Layout with these decisions (`hardware/body/layout.py`; first pass, placeholders)
- **Two identical lid modules:** a processor board (about 20 g) on the bottom lid and a power and motor-driver board (about 20 g) on the top lid, mirror images about z = 30; the **mass above z = 30 equals the mass below (52 g each, cells and boards)**. The camera, beamsplitter, lamp, battery and antenna pivot sit on the plane. **Centre of mass x = +0.3 mm, z = 30.0 mm** (servos and hub included). The lid modules need a board-to-board link between them when a lid is removed: not designed.
- **Camera and lamp:** window axis at x = +40, z = 30. The camera (25 x 24 x 9 mm) sits behind at y = 36.5 to 45.5, looking +y through a 28 x 24 x 1.5 mm glass **plate** beamsplitter at 45 degrees (bounding box 20 x 20 x 24 mm at y = 47 to 67), and the lamp is on the body-centre side of the plate (x = 14 to 28) shining +x so the plate reflects it out of the window. All inside the free front bay, clear of servo B by 1 mm. **A 25 mm cube beamsplitter would weigh about 39 g (my estimate) against about 3 g for a plate.**
- **Antenna pivot:** a bearing, rotary RF joint and a 40 mm swing disc carrying the counterweight, behind the -y wall at x = -40, z = 30, 8 mm deep (y = -67.5 to -59.5), 2 mm clear of servo A; the whip stands outside.
- **All placeholders clear** the keep-in volume, the servos and each other; they use 14% of the free volume (113 of 818 cm3). Volume is still not the constraint.
- **Mass** (shell, rings and screws 32 g, seal 15 g, electronics 100 g now including battery, beamsplitter, pivot and wiring, and cells):

| Shell | cells 0.15 g/cm2 (47 g) | 0.25 (78 g) | 0.35 (109 g) |
|---|---|---|---|
| woven plates 1.0 mm + keys (141 g) | 335 g (51 g under 386) | 366 g (20 under) | 397 g (11 over) |
| forged 1.5 mm (164 g) | 358 g (28 under) | 389 g (**3 over**) | 420 g (34 over) |

  The shell choice is worth 23 g and the cell choice 62 g. **Forged at 1.5 mm is over budget at the middle cell weight; plates are not.** This leans further toward plates, and a four-wall frame with two identical lids suits plates directly (four 140 x 60 wall plates and two 140 x 140 lid plates), where forged would need a deep through-frame mould.
- **Balance:** the whole-rover centre of mass is about **-1.7 mm in y** (the simulation had -2.9). It is less well centred than the first pass (-0.9) because the boards are now centred; shifting the boards about 10 mm toward +y would centre it. The antenna's mass (13 g at -y) is partly offset by the camera group (20 g at +y).

### Problems to resolve (found while placing these; none is a blocker)
**The gravity-oriented antenna (a pendulum):**
1. **The counterweight must over-balance, not balance.** A pivot balanced exactly stays wherever it is left. For the whip to hang up, the weight opposite the whip must have a larger moment than the whip: the net unbalance sets the restoring torque. Example (mine): 2 g net at 15 mm gives about 0.3 mN.m; pivot and rotary-joint friction of 0.05 to 0.3 mN.m (an assumed range) would leave a dead band of about 10 to 90 degrees. A net unbalance of 5 g at 15 mm (about 0.7 mN.m) is a better start, within the 10 g allowance for the whole pivot.
2. **It only corrects rotation about its own axis**, which is the y-axis (normal to the end face): the rover rolling side to side. If the body pitches about x (a slope, a stance, a self-righting roll), the axis tilts and the whip tilts with it by the same angle; standing on an end, it points sideways. Fine for the rest poses the rover normally takes, not for steep ones.
3. **The feed needs a rotary RF joint or a limited-turn cable.** Upright to inverted is 180 degrees of rotation, and several rolls in one direction would wind a plain coax pigtail. A sprung contact or capacitive joint works at low frequency but is lossy and noisy; a stop with a pigtail good for about plus or minus 200 degrees is simpler. The antenna may also be a dummy, as the signal is not part of the scope.
4. **Damping.** A low-friction pendulum rings when the rover accelerates or rolls; a little viscous damping (grease, an eddy-current magnet) keeps the whip from swinging.
5. **The whip and the ground.** It stands off the end face by the stub length; rolling end over end in a righting sequence puts the face on the ground, so the whip must be flexible or short.
6. **The wall.** A shaft hole through the -y wall needs a bonded bushing and a seal; a carbon wall also screens the antenna's feed point.

**The beamsplitter:**
1. **Light loss.** A 50/50 plate sends half the lamp light out and passes half the scene light to the camera: ambient light to the camera is one stop darker, and the lamp needs about twice the power for the same illumination on the scene.
2. **Glare.** The lamp light that reflects from the window pane (about 4% per glass surface, then half through the plate) goes straight back into the camera, coaxially, and can swamp the dim return from a diffuse object centimetres away. Remedies: crossed linear polarisers (lamp polarised, camera analyser at 90 degrees), anti-reflection coated glass, a black baffle between the plate and the window, and a wedged plate to avoid a double image. **This is the biggest optical risk and I have not tested it.** A bench test with a cheap plate beamsplitter and a phone camera would decide it before the design is committed.

**Two lids:**
- Each lid has cells outside and a board inside; **when a lid is removed its board comes with it**, so the link between the two boards (and the cells' wiring) needs a connector at the lid joint on a face both lids share.
- Both lids need their own gasket and fasteners, doubling the lid screws and inserts in the budget (not yet doubled).
- Bonded cells on a carbon lid need an insulating layer under them.

## Design method: a solid block with cavities (owner, 2026-11-11; `hardware/body/block.py`)

**Method (owner):** treat the body as a completely solid, uniform 140 x 140 x 60 mm block; cut the components and their required connections and views out of it; when every component is specified and placed, derive from that one block both (a) a chassis made of carbon tubs joined together (the block's faces, exterior and interior, become laminate) and (b) a forged-carbon unibody (the cavities become the cores of a mould). **Purchasing is deferred indefinitely (owner), so no bench tests for now.** Current inputs are the placeholders of `layout.py`.

**What `block.py` does:** cuts 33 cavities from a 140 x 140 x 60 mm block as real CAD: four servo pockets (envelope plus 1 mm, with the output and back bosses), the hub drive on both sides (housing tube through the hub wall, gear and pinion discs, hollow shaft, horn adapter), the two lid-borne boards, the battery, the camera, the beamsplitter plate's bounding box, the lamp and its beam to the plate, the 26 mm window through the +y wall, **the camera's view as a 60 degree cone from the lens to the window**, the antenna swing disc and its shaft hole through the -y wall. It exports `hardware/body/out/body_block.step` (our own geometry), re-imports it (one solid, 867.2 cm3, matching) and measures what the cavities leave.

### What the block says
- **Cavities remove 26% of the block**: 867 of 1,176 cm3 remain. As solid carbon that would be **about 1.34 kg**, so the block is a design volume, never the part: all of the remaining material between the surfaces has to be taken out.
- **Almost everything is far from the outside.** The servo pockets are 11 to 24.5 mm from the nearest outer face and the battery 18 mm; **only the hub tubes (through the hub walls), the window and its optics, and the antenna shaft touch or come within 2 mm of the exterior.** So the exterior skin and the cavities do not share material except at those penetrations: lining a cavity means a second, separate skin.
- **The cost of lining every surface, outside and in** (surface area times thickness; no skin shared with a neighbour):

| Lined surface | Area | 1.0 mm woven | 1.5 mm forged |
|---|---|---|---|
| Outside | 728 cm2 | 113 g | 158 g |
| 4 servo pockets | 331 cm2 | 51 g | 72 g |
| Hub drive, both sides | 154 cm2 | 24 g | 33 g |
| Boards (ride on the lids) | 232 cm2 | 36 g | 51 g |
| Camera, beamsplitter, lamp and window | 94 cm2 | 15 g | 20 g |
| Antenna pivot | 36 cm2 | 6 g | 8 g |
| Battery | 20 cm2 | 3 g | 4 g |
| **Everything** | **1,594 cm2** | **247 g** | **347 g** |

  A voxel check (1 mm, unions where surfaces share material) gives a 1 mm skin of 135 cm3, 210 g woven or 196 g forged, consistent with the area sum less overlaps. **The voxel step is too coarse for 1.5 mm** (it jumps from 141 to 263 cm3 between 1.5 and 2.0 mm, grid rounding); the area-based figures are the better ones.
- **Against the 386 g budget** (shell, rings and screws 32 g, seal 15 g, electronics 100 g, cells 47 to 109 g, all from `layout.py`):

| Treatment | Total at cells 47 / 78 / 109 g |
|---|---|
| Line every cavity (woven 1.0 mm): 247 g of shell | **441 / 472 / 503 g, over budget by 55 to 117 g** |
| Outside + servo pockets + camera group + antenna pivot lined (woven 1.0 mm): 184 g | 378 / 409 / 440 g (under by 8 g only with the lightest cells) |
| Outside only (woven 1.0 mm + 28 g of keys): 141 g | 335 / 366 / 397 g (under by 51, 20 g; over by 11 g with the heaviest cells) |

  **The same holds for a forged unibody.** Forged at 1.5 mm with every surface lined is about 347 g of shell, 530 g or more in total: well over budget.

### Reading
- **The method works as a design tool**: it keeps one master model, shows exactly what touches the outside and what does not, and lets both bodies be checked against the same cavities.
- **The rule for deriving the part is what decides the mass.** **Lining every cavity does not fit the budget at 1.0 mm woven, and certainly not at 1.5 mm forged.** What the block says is that the interior should be mostly one open volume, with a lining or a local feature only for what needs a located, stiff interface: the servo group, the camera and window group, and the antenna pivot. Boards and battery do not need their own tubs: they ride on the lids or on standoffs.
- **The hub drive group does not need a lining either**: the aluminium hub housing is itself the structure; the wall needs a bonded reinforcing ring where the housing tube passes through it.
- **A cheaper way to locate the servos than four tubs:** the four servos could sit between two or three bulkhead plates (so the cost is a plate, not a box around each servo); the block can be re-cut with the bulkheads as surfaces to test this.
- **For the tub chassis:** the four walls and two lids form one set; the servo group, the camera group and the antenna pivot become small tubs bonded into the frame. **For the forged unibody:** the cores are the interior void plus the pockets; the mould is a pair of cores in a cavity, with the same wall rule.

### Design process and material lean (owner, 2026-11-12)

**Process (owner), in order:** (1) component placement; (2) component attachment points; (3) inter-component cavities (wiring, optical paths and so on); (4) access points to the components (for example, removing the material between components and the lids); (5) **topology optimisation for loads, as the penultimate step**; (6) a final refinement so the design can be fabricated. `block.py` covers steps 1 and part of 3 so far (placeholders). Steps 2, 4, 5 and 6 are not started.

**Material lean (owner): forged carbon**, for an aesthetic reason: the random chopped-fibre surface texture resembles the Widmanstatten pattern of iron meteorites, a space connection. This is a lean, not the end of the decision: the woven-plates recommendation above (crisp edges, wall thickness) is still on the table, and the choice stays open until the interior has real parts.

**Precedents found (2026-11-12, web search, not verified in depth):** topology-optimisation tools start from a solid design space and subtract void and fixed (non-design) regions, with loads applied to the non-design regions (Altair Inspire, Hexagon); skeleton-model top-down CAD; CubeSat structures machined from billet, which the industry has partly moved away from (thin sheet-metal chassis, Pumpkin); the Mars Exploration Rover warm electronics box (carbon skins on aluminium honeycomb, electronics isolated on tubes); soluble and fusible cores for hollow composite parts. No source found that derives both a bonded-tub chassis and a forged unibody from one block.

**Notes (mine, not decisions):**
- Forged carbon is closer to isotropic than woven laminate, which suits the isotropic material model of standard density-based topology optimisation; the vendor strength figures are untested (see above).
- The loads are small (0.2 to 4 MPa at the hubs on a 1 mm wall), so the optimiser will mostly return "remove everything"; the result will be set by constraints (minimum wall of about 1.5 mm for forged, mass budget, hub stiffness, lid clamping, drop and righting-roll impacts), so the load cases and constraints need writing down first.
- **Mouldability belongs inside step 5, not only step 6:** enclosed cavities cannot be cored out of a pressed forged part without soluble or fusible cores, so a draw direction (and draft) constraint in the optimisation is the usual remedy. The z = 30 symmetry suggests two identical half-shells bonded at the midplane (one mould), which would split the hub bores; to be tested, not chosen.
- **Texture is visible only where cells are not:** the cells cover 311 cm2 of about 728 cm2 of outer face (about 43%), so the texture shows on the hub faces, the gaps and the edges. A clear coat and the chip size (finer or coarser flakes) decide how much it reads as Widmanstatten; its real pattern is families of straight bands at fixed angles, so the likeness is loose (a metallic, crystalline glint) rather than exact.

### Fabrication route: mould, then machine the outside only (owner, 2026-11-12)

**Owner's idea:** press the forged-carbon body in mould(s) as a near-net form, then **machine only the outside**, which has to reach a specific form and finish; **the inside stays as moulded, so long as everything fits.** The outside stays rectilinear (owner). The outer envelope, cell faces, lid seating faces, hub bores and window are fixed (non-design) surfaces for the optimisation; only the skin thickness and the structure behind them are free.

**Why it helps (mine; from general knowledge, not searched):** the cutter, not the press, makes the crisp outer edges and flat cell and lid faces (the crisp-edge objection to forged carbon shrinks, though the thin-wall problem remains); located features (hub bores, bearing seats, lid seats, window) are cut from the outside and can be finish-machined to position; machining stock is left only on the outside; and nothing inside needs tool access, so the cores only have to give a shape that fits. Forged carbon is sold as machinable stock (Rock West forged blocks, cited above).

**What it adds to the process (mine, to be worked out):**
- A **machining allowance** on the outside (a few tenths of a millimetre is my guess, unchecked), carried in the CAD as moulded-oversize versus final surfaces, marked face by face.
- **Wall thickness after machining** = moulded wall minus allowance, plus or minus the core's shift relative to the mould. The minimum wall of about 1.5 mm for forged carbon has to hold after both, so the practical minimum may be higher.
- A **datum for the first cut**: the outside must end up in the right place relative to the servo and hub positions, so a moulded-in datum or an accurately moulded interior or hub feature is needed, plus fixturing for a thin hollow part (it will chatter; a soluble or wax fill is one option).
- An **interior clearance rule**: generous margins around servos, boards and battery for core shift, shrink, warp and flash.
- **Interior surface**: as-moulded forged carbon can shed fibres or have resin-poor patches; conductive fibres near boards are a short-circuit risk, so the inside needs sealing or an insulating coat (with the insulation under cells and boards already noted).
- **Dust and tooling**: carbon dust is conductive and a health hazard (extraction, clean-down before electronics go in); carbon wears cutters fast (diamond-coated or PCD tools, an assumption); cut edges expose fibre ends and need sealing against moisture and against galvanic contact with the aluminium hub parts.
- **Texture:** a cut face shows a section through the chips and looks different from a moulded face (nearer to a cut and etched meteorite slice); how it looks is unknown until tried, and it needs a clear coat.
- Mouldability (draw direction, draft, core extraction) is a constraint in the optimisation step, with the machining allowance and datums in the final refinement step.

### Not done yet
- The wiring channels and connectors (not specified), the lid split and its joint, the keys, the screws and insert bosses, the cells' surface, and the lamp beam's exact path are not cut. The pockets are boxes and discs, not the real part shapes.
- Nothing is derived into a tub or unibody design yet; it waits until the components are specified.

### Decisions needed to continue (owner)
1. For the derived designs, **which cavities become structural linings** (tubs, or in the forged case moulded pockets) versus open interior or bulkheads: my suggestion above is the servo group, the camera group and the antenna pivot only.
2. Whether to **test servo mounting on bulkhead plates** instead of pockets (cheaper in mass, by the area figures above).

## Open decisions (owner)
1. **Woven laminate or forged carbon** (revised recommendation: woven plates bonded into a box, for the crisp edges), and the manufacturing route (a mould from a printed plug, CNC-cut plate bonded into a box, or a bought moulded part).
2. **Closed shell or open frame:** a sealed box is not required by the scope (no spaceflight), but dust and water tolerance would need deciding.
3. Antenna: a real patch behind a window, or a dummy.

## Next steps
1. Choose between woven and forged, and the route.
2. A parametric CAD shell (`hardware/body/`) at 140 x 140 x 60 mm with the hub bores, servo clearance from `hub.py`, a lid flange and a window, and a mass check against the budget above.
3. Place the electronics, cells and camera, and check the centre of mass.
