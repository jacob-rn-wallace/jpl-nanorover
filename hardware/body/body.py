#!/usr/bin/env python3
"""Rover body: Hammond 1590Z090 die-cast box, rim skimmed, with a flat O-ring lid plate.

Run from the repository root:  .venv/bin/python hardware/body/body.py
Needs build123d.  Reads Hammond's STEP and writes STEP files to hardware/body/out/.

Hammond's CAD file is third-party and is NOT in this repository (its terms of use have not been read).  The script
looks for it in the private companion repository, `../jpl-nanorover-private/cad/vendor/hammond-1590Z090/1590Z090.stp`,
or at the path in the environment variable HAMMOND_1590Z090_STP.  Output that contains Hammond's geometry
(`body_hammond.step`) is git-ignored; the parts that are ours (lid plate, O-rings, inserts, hub studs, nuts) are tracked.

Target: the MUSES-CN body, 140 x 140 x 60 mm.  The 1590Z090 is 140 x 140 x 90 (box 62 to the
tongue tip, 60 to the shoulder, plus a 30 mm deep cast lid), so the cast lid is discarded, the box
rim is cut down, and a flat plate of PLATE_T mm replaces the lid.  All dimensions in mm.
Z is up, z = 0 at the outside of the floor.

Seal layout (from the STEP): at each corner the rim has an M6 cover-screw bore (open at its bottom to
the cavity) and a separate 11.5 mm wall-mounting tube that runs through the floor, only 2.7 mm from the
cavity wall.  Hammond's own gasket runs in that 2.7 mm wall, between the cavity and the tubes
(SEAL_PATH = "original"), which leaves the tubes and screws outside the seal.  That fits only a small
cord (1.5 mm).  The alternative, SEAL_PATH = "outer", uses a standard 1.78 mm cord near the outer face
but encloses the tubes, which are open at the bottom, so they would have to be plugged.

Strut hubs: Jones & Wilcox say each strut carries its own two motors (wheel and strut) and that the "shoulder
hub" holds the position potentiometers, and the photos show wires leaving the centre of the hub.  So the hub is
modelled as a stationary hollow pivot stud on each 140 x 60 face (x = +-70, y = 0, z = 30) that the struts rotate
on, with no rotating shaft through the wall: the seals are static (a face O-ring under the stud flange) and the
wires go through the stud bore and are potted.  A double-D shank keeps the stud from turning.

Cover-screw threads: each boss is only 5 mm tall (z 50 to the rim at 55) and its bore is open at the bottom
into the cavity.  A 1D (6 mm) M6 x 1.0 helical insert is fitted flush with the top (recessed 0.4 mm); it
stands 1.4 mm out of the bottom of the boss.  The bore is modelled at the tapped major diameter (7.2 mm).

Lid plate stiffening: the four cover screws are 120 mm apart, so a plain 5 mm plate bows between them and
loosens the cord.  A rib loop on the plate underside, just inside the cavity wall, turns each plate edge into
a T-beam (RIB_T x RIB_H).

Everything below the 'PARAMETERS' block is derived or checked, not chosen.
"""
import math
import os
from pathlib import Path
from build123d import *
from build123d.topology import Shape
from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STEP_IN = Path(os.environ.get("HAMMOND_1590Z090_STP",
                              ROOT.parent / "jpl-nanorover-private" / "cad" / "vendor" / "hammond-1590Z090" / "1590Z090.stp"))
OUT = HERE / "out"

# ---------------- PARAMETERS ----------------
TARGET_H = 60.0      # overall height wanted (MUSES-CN body)
PLATE_T = 5.0        # lid plate thickness
SEAL_PATH = "original"   # "original": Hammond's own gasket path, hugging the cavity wall (tubes and screws outside)
                         # "outer": near the outer face, enclosing the corner tubes and screw bores
if SEAL_PATH == "original":
    OR_CS, GROOVE_D, GROOVE_W = 1.5, 1.1, 2.0      # fits the 2.7 mm wall between the cavity and the corner tubes
    GROOVE_OFF = 1.55                              # groove centreline, offset from the cavity edge into the wall
else:
    OR_CS, GROOVE_D, GROOVE_W = 1.78, 1.35, 2.4    # standard 1.78 mm cord
    GROOVE_OFF = 2.125                             # groove centreline, inward from the outer face of the rim
SCREW_XY = 60.0      # cover screws at (+-60, +-60) (Hammond drawing)
CLEAR_D = 6.6        # M6 clearance
CSK_D = 12.4         # M6 countersink diameter (ISO 10642 flat head, 90 deg)
RHO_AL = 2.70e-3     # g/mm3, for 6061 and as an estimate for the ADC12 casting
RIB_T = 3.0          # edge rib thickness
RIB_H = 8.0          # edge rib height below the plate underside (set 0 for a plain plate)
RIB_CLEAR = 1.0      # clearance between the rib and the cavity wall
INSERT = True        # thread-repair (helical coil) insert in each cover-screw boss
INS_OD = 7.2         # tapped major diameter after the STI tap (drill 6.2 mm, M6 x 1.0 insert tap)
INS_ID = 6.0         # screw major diameter
INS_L = 6.0          # 1D insert, 6 mm
INS_RECESS = 0.4     # installed this far below the rim face
HUBS = True          # strut pivot hubs on the two x faces (stationary hollow stud with a face O-ring)
HUB_Z = 30.0         # hub axis height: centre of the 60 mm face
SPOT_OUT = 69.25     # outer spot-face plane |x| (the wall's outer face leans about 1 degree: 69.5 at z = 30)
SPOT_IN = 65.20      # inner spot-face plane |x| for the nut seat (inner face is 64.9 at z = 30, leaning too)
SPOT_OUT_D = 30.0    # outer spot-face diameter
SPOT_IN_D = 26.0     # inner spot-face diameter
HUB_FLANGE_D, HUB_FLANGE_T = 26.0, 3.0
HUB_SHANK_D, HUB_SHANK_AF = 12.0, 10.5   # M12 x 1.0 shank with two flats (anti-rotation)
HUB_HOLE_D, HUB_HOLE_AF = 12.6, 10.8     # matching double-D hole in the wall
HUB_BORE = 8.0       # wire bore through the stud (potted)
HUB_AXLE_L = 20.0    # axle stub outside the flange (placeholder for the strut bearings)
HUB_OR_ID, HUB_OR_CS = 16.0, 1.5         # face O-ring 16 x 1.5
HUB_GROOVE_W, HUB_GROOVE_D = 2.0, 1.1
NUT_AF, NUT_H = 19.0, 6.0                # M12 thin jam nut (check the standard for your nut)
# --------------------------------------------

RIM_R = 10.0         # outer corner radius of the casting (measured from the STEP)
Z_CUT = TARGET_H - PLATE_T   # rim height after skimming


def nurbs(shape):
    """Convert every curve and surface to NURBS.  The rib and groove are built from offset curves, which the STEP
    writer drops; without this the exported lid plate re-imports as loose shells with no volume."""
    return Shape.cast(BRepBuilderAPI_NurbsConvert(shape.wrapped, True).Shape())


def load_box():
    if not STEP_IN.exists():
        raise SystemExit(f"Hammond 1590Z090 STEP not found at {STEP_IN}\nClone jpl-nanorover-private beside this repo, or set HAMMOND_1590Z090_STP.")
    s = import_step(STEP_IN)
    box = s.solids()[0]                    # solids: box, lid, gasket, 4 screws; STEP is Y-up
    return box.rotate(Axis.X, 90)          # now Z-up, floor at z = 0 (feet below), tongue at the top


def main():
    OUT.mkdir(exist_ok=True)
    box = load_box()
    # 1. Body: mill off the 1 mm feet and cut the rim (removes the tongue, shoulder and 5 mm of wall)
    keep = Box(400, 400, Z_CUT).moved(Location((0, 0, Z_CUT / 2)))
    body = box & keep
    body_uncut = body

    # 2. Groove path
    rim = body.intersect(Plane.XY.offset(Z_CUT - 0.05)).faces()[0]
    inner_wires = list(rim.inner_wires())
    cavity = max(inner_wires, key=lambda w: w.length)
    cavity0 = cavity.moved(Location((0, 0, -(Z_CUT - 0.05))))   # same outline at z = 0 for building the groove
    outer = rim.outer_wire().bounding_box().size.X     # ~139.9 at the rim (drafted walls)

    def grown(amount):
        """Groove outline `amount` mm from the reference edge (positive = further into the wall)."""
        if SEAL_PATH == "original":
            w = cavity0.offset_2d(amount, kind=Kind.ARC)         # cavity edge pushed out into the wall
            return w[0] if isinstance(w, (list, tuple)) else w
        side = outer - 2 * amount                                 # outer face pulled inward
        return Wire(RectangleRounded(side, side, RIM_R - amount).edges())

    centre = grown(GROOVE_OFF)
    groove_face = Face(grown(GROOVE_OFF + GROOVE_W / 2)) - Face(grown(GROOVE_OFF - GROOVE_W / 2))
    if SEAL_PATH == "outer":
        groove_face = Face(grown(GROOVE_OFF - GROOVE_W / 2)) - Face(grown(GROOVE_OFF + GROOVE_W / 2))
    groove_len = centre.length

    # 2b. Cover-screw bores opened up to the tapped major diameter for the inserts
    corners = [(sx * SCREW_XY, sy * SCREW_XY) for sx in (-1, 1) for sy in (-1, 1)]
    insert_parts = []
    if INSERT:
        for (cx, cy) in corners:
            body = body - Cylinder(INS_OD / 2, 12).moved(Location((cx, cy, Z_CUT - 4)))
            z_top = Z_CUT - INS_RECESS
            tube = Cylinder(INS_OD / 2, INS_L) - Cylinder(INS_ID / 2, INS_L + 1)
            insert_parts.append(tube.moved(Location((cx, cy, z_top - INS_L / 2))))

    # 2c. Hub holes: spot-faces and a double-D hole through each x wall
    def at_hub(shape, side):
        """Shape built about the hub axis (local +Z points out of the body, local z = 0 at the outer spot-face)."""
        rot = (0, 90, 0) if side > 0 else (0, -90, 0)
        return shape.moved(Location((side * SPOT_OUT, 0, HUB_Z), rot))

    def double_d(d, af):
        return Circle(d / 2) & Rectangle(d + 2, af)

    hub_parts, hub_orings, hub_nuts = [], [], []
    if HUBS:
        wall = SPOT_OUT - SPOT_IN
        # stud (local frame: z = 0 at the outer spot-face, +z outward)
        flange = Cylinder(HUB_FLANGE_D / 2, HUB_FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        r_mid = (HUB_OR_ID + HUB_OR_CS) / 2
        groove = Cylinder(r_mid + HUB_GROOVE_W / 2, HUB_GROOVE_D, align=(Align.CENTER, Align.CENTER, Align.MIN)) - \
            Cylinder(r_mid - HUB_GROOVE_W / 2, HUB_GROOVE_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
        flange = flange - groove
        axle = Cylinder(HUB_SHANK_D / 2, HUB_AXLE_L, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, HUB_FLANGE_T)))
        shank_len = wall + NUT_H + 2.0
        shank = extrude(double_d(HUB_SHANK_D, HUB_SHANK_AF), shank_len).moved(Location((0, 0, -shank_len)))
        stud = flange + axle + shank
        stud = stud - Cylinder(HUB_BORE / 2, shank_len + HUB_FLANGE_T + HUB_AXLE_L + 2,
                               align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -shank_len - 1)))
        oring_h = Torus(r_mid, HUB_OR_CS / 2).moved(Location((0, 0, HUB_GROOVE_D - HUB_OR_CS / 2)))
        nut = extrude(RegularPolygon(NUT_AF / math.cos(math.radians(30)) / 2, 6), NUT_H).moved(Location((0, 0, -wall - NUT_H)))
        nut = nut - Cylinder(HUB_SHANK_D / 2, NUT_H + 2).moved(Location((0, 0, -wall - NUT_H / 2)))
        for side in (1, -1):
            out_cut = Cylinder(SPOT_OUT_D / 2, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
            in_cut = Cylinder(SPOT_IN_D / 2, 10, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, -wall)))
            hole = extrude(double_d(HUB_HOLE_D, HUB_HOLE_AF), wall + 2).moved(Location((0, 0, -wall - 1)))
            body = body - at_hub(out_cut, side) - at_hub(in_cut, side) - at_hub(hole, side)
            hub_parts.append(at_hub(stud, side))
            hub_orings.append(at_hub(oring_h, side))
            hub_nuts.append(at_hub(nut, side))

    # 3. Lid plate: 140 x 140, R10 corners (matches the box at the rim), groove on its underside
    plate = extrude(RectangleRounded(140, 140, 10), PLATE_T).moved(Location((0, 0, Z_CUT)))
    groove = extrude(groove_face, GROOVE_D).moved(Location((0, 0, Z_CUT)))
    plate = plate - groove
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = (sx * SCREW_XY, sy * SCREW_XY)
            hole = Cylinder(CLEAR_D / 2, PLATE_T + 1).moved(Location((p[0], p[1], Z_CUT + PLATE_T / 2)))
            csk = Cone(bottom_radius=CLEAR_D / 2, top_radius=CSK_D / 2, height=(CSK_D - CLEAR_D) / 2,
                       align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
                Location((p[0], p[1], Z_CUT + PLATE_T - (CSK_D - CLEAR_D) / 2)))
            plate = plate - hole - csk

    # 3b. Edge rib: a loop on the plate underside following the cavity outline, RIB_CLEAR inside the wall
    rib = None
    if RIB_H > 0:
        def inset(d):
            w = cavity0.offset_2d(-d, kind=Kind.ARC)
            return w[0] if isinstance(w, (list, tuple)) else w
        rib_face = Face(inset(RIB_CLEAR)) - Face(inset(RIB_CLEAR + RIB_T))
        rib = extrude(rib_face, RIB_H).moved(Location((0, 0, Z_CUT - RIB_H)))
        plate = plate + rib

    # 4. O-ring (cord swept along the groove centreline)
    path = centre.moved(Location((0, 0, Z_CUT + GROOVE_D - OR_CS / 2)))   # seated against the groove floor
    prof = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    oring = sweep(prof * Circle(OR_CS / 2), path=path)

    # ---------------- checks ----------------
    bb = (body + plate).bounding_box()
    print(f"overall size        {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f}   (target 140 x 140 x {TARGET_H})")
    print(f"body                {body.volume/1000:.1f} cm3  ~{body.volume*RHO_AL:.0f} g (die-cast Al, estimated density)")
    print(f"lid plate           {plate.volume/1000:.1f} cm3  ~{plate.volume*RHO_AL:.0f} g (6061)")
    floor_top = 4.0
    print(f"cavity depth        {Z_CUT - floor_top:.0f} mm (floor ~4 mm)  rim wall ~4.5 mm")
    print(f"screw bosses        {Z_CUT - 50:.0f} mm tall (50 to {Z_CUT:.0f}); threaded engagement in the casting {(Z_CUT-50)/6:.2f} d as a plain M6 tap")
    print(f"groove              {GROOVE_W} wide x {GROOVE_D} deep, centreline length {groove_len:.0f} mm")
    print(f"O-ring              {OR_CS} cord, centreline length {groove_len:.0f} mm; squeeze {(OR_CS-GROOVE_D)/OR_CS*100:.0f}%")
    def pts_of(w, n=1500):
        return [w.position_at(i / n) for i in range(n)]

    def gap(wa, wb):
        pb = pts_of(wb)
        return min(math.hypot(p.X - q.X, p.Y - q.Y) for p in pts_of(wa, 600) for q in pb)

    e1, e2 = grown(GROOVE_OFF - GROOVE_W / 2), grown(GROOVE_OFF + GROOVE_W / 2)
    voids = {"cavity": [cavity], "tubes / bores": [w for w in inner_wires if w is not cavity]}
    for name, ws in voids.items():
        d = min(gap(e, w) for e in (e1, e2) for w in ws)
        print(f"groove edge to nearest {name}: {d:.2f} mm")
    print(f"groove edge to outer face: {min(gap(e, rim.outer_wire()) for e in (e1, e2)):.2f} mm")
    hit = groove_face.moved(Location((0, 0, Z_CUT - 0.05))) & rim
    covered = sum(f.area for f in hit.faces()) if hit else 0.0
    print(f"groove area {groove_face.area:.0f} mm2, on solid rim {covered:.0f} mm2 ({covered/groove_face.area*100:.1f}%)")
    ov = oring & body
    print(f"O-ring protrudes below the plate face by {OR_CS - GROOVE_D:.2f} mm; overlap with the rim (uncompressed model) {ov.volume if ov else 0.0:.0f} mm3")

    if rib is not None:
        hit = rib & body
        print(f"rib                 {RIB_T} x {RIB_H} mm, {inset(RIB_CLEAR + RIB_T / 2).length:.0f} mm long, {rib.volume/1000:.1f} cm3 ~{rib.volume*RHO_AL:.0f} g; interference with the box {hit.volume if hit else 0.0:.2f} mm3, closest approach {rib.distance_to(body):.2f} mm")
        # edge strip as a simply supported T-beam between the corner screws (hand estimate, not FEA)
        E, L, b, W_LOAD = 69000.0, 120.0, 20.0, 2.0     # MPa, mm, effective flange width, assumed cord load N/mm
        def I_T(h):
            A1, y1, A2, y2 = b * PLATE_T, PLATE_T / 2, RIB_T * h, PLATE_T + h / 2
            yc = (A1 * y1 + A2 * y2) / (A1 + A2)
            return b * PLATE_T**3 / 12 + A1 * (yc - y1)**2 + RIB_T * h**3 / 12 + A2 * (y2 - yc)**2
        d = lambda I: 5 * W_LOAD * L**4 / (384 * E * I)
        print(f"edge bow estimate   plain plate {d(I_T(0)):.2f} mm -> with rib {d(I_T(RIB_H)):.2f} mm "
              f"(I {I_T(0):.0f} -> {I_T(RIB_H):.0f} mm4; assumes {W_LOAD} N/mm cord load, {b:.0f} mm flange, simply supported over {L:.0f} mm)")

    if INSERT:
        def dist_pt(w, cx, cy, n=1200):
            return min(math.hypot(w.position_at(i / n).X - cx, w.position_at(i / n).Y - cy) for i in range(n))
        walls = []
        for (cx, cy) in corners:
            others = [w for w in [rim.outer_wire()] + inner_wires
                      if not (w.length < 25 and abs(w.bounding_box().center().X - cx) < 0.6 and abs(w.bounding_box().center().Y - cy) < 0.6)]
            walls.append(min(dist_pt(w, cx, cy) for w in others) - INS_OD / 2)
        ov = sum((Compound(insert_parts) & body).volume for _ in [0]) if (Compound(insert_parts) & body) else 0.0
        print(f"inserts             4 x M6x1.0 1D (6 mm), drill 6.2, tapped major {INS_OD}; wall left around each tapped hole {min(walls):.2f} mm; "
              f"insert/body overlap {ov:.2f} mm3")
        out_below = (Z_CUT - INS_RECESS - INS_L)
        print(f"                    insert spans z {out_below:.1f} to {Z_CUT - INS_RECESS:.1f}; boss bottom z 50, so {50 - out_below:.1f} mm stands out into the cavity")
        L_screw = 12.0
        thread_in = L_screw - PLATE_T - INS_RECESS
        print(f"                    M6x{L_screw:.0f} flat-head screw: {thread_in:.1f} mm in the insert (insert is {INS_L:.0f} mm), tip at z {60 - L_screw:.1f}")
        # hand estimate of thread strip-out in the casting: tau * pi * D * Le * 0.55, tau = 170 MPa assumed for the die-cast alloy
        tau, Le = 170.0, Z_CUT - 50.0
        plain = tau * math.pi * 5.0 * Le * 0.55 / 1000
        coil = tau * math.pi * INS_OD * Le * 0.55 / 1000
        print(f"                    strip-out estimate in the casting over {Le:.0f} mm: tapped M6 {plain:.1f} kN -> insert {coil:.1f} kN "
              f"(assumes tau {tau:.0f} MPa, 0.55 thread factor; M6 preload at 2 N.m is about {2/(0.2*0.006)/1000:.1f} kN)")

    if HUBS:
        studs, rings, nuts = Compound(hub_parts), Compound(hub_orings), Compound(hub_nuts)
        i_stud = studs & body
        i_nut = nuts & body
        i_or = rings & body
        wall_h = SPOT_OUT - SPOT_IN
        print(f"hubs                2 x stud on x = +-{SPOT_OUT} (spot-face dia {SPOT_OUT_D}), axis z = {HUB_Z}; wall left at the hub {wall_h:.2f} mm "
              f"(thinnest {SPOT_OUT - 65.21 - 0.0:.2f} mm over the spot-face, where the inner face leans out)")
        print(f"                    stud/body overlap {i_stud.volume if i_stud else 0.0:.2f} mm3, nut/body overlap {i_nut.volume if i_nut else 0.0:.2f} mm3 "
              f"(both should be 0); O-ring squeeze overlap {i_or.volume if i_or else 0.0:.0f} mm3")
        print(f"                    face O-ring {HUB_OR_ID:.0f} x {HUB_OR_CS} in a {HUB_GROOVE_W} x {HUB_GROOVE_D} groove in the flange, squeeze {(HUB_OR_CS - HUB_GROOVE_D) / HUB_OR_CS * 100:.0f}%")
        bore_a = math.pi * (HUB_BORE / 2) ** 2
        wire_a = 28 * math.pi * (0.62 / 2) ** 2     # 28 conductors of AWG30, about 0.62 mm over the insulation
        print(f"                    wire bore {HUB_BORE} mm = {bore_a:.0f} mm2; 28 x AWG30 conductors take about {wire_a:.0f} mm2 ({wire_a / bore_a * 100:.0f}% fill) before potting")
        print(f"                    stud mass {sum(p.volume for p in hub_parts) * 7.9e-3 / 2:.0f} g each (stainless), nut {nuts.volume * 7.9e-3 / 2:.0f} g each")
        print(f"                    nut across corners {NUT_AF / math.cos(math.radians(30)):.1f} mm in a {SPOT_IN_D} mm inner spot-face")

    export_step(body, str(OUT / "body_hammond.step"))   # contains Hammond geometry: git-ignored
    plate = nurbs(plate)
    export_step(plate, str(OUT / "lid_plate.step"))
    export_step(oring, str(OUT / "oring.step"))
    if INSERT:
        export_step(Compound(insert_parts), str(OUT / "inserts.step"))
    if HUBS:
        export_step(Compound(hub_parts), str(OUT / "hub_studs.step"))
        export_step(Compound(hub_orings + hub_nuts), str(OUT / "hub_orings_and_nuts.step"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
