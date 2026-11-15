#!/usr/bin/env python3
"""Body-side wire routes: from each lid pocket's wire pads to where the wires go, found by a shortest-path search through the design block's free volume.

Run: .venv/bin/python hardware/body/wire_routes.py        (needs the venv: it imports layout.py, which builds the servo and component masks; writes out/wire_routes.json)

Method (2026-11-14; ASM = my assumption):
  * free space = the keep-in volume (2.5 mm in from every outer face) minus the servos and hub (with 1 mm clearance, layout.py) minus every placed component box; a route must keep 2 mm clear of all of
    these (a 4 mm square channel along the path fits), on a 2 mm grid; straight runs are preferred (each bend costs two cells); the path is Manhattan, so each route is a list of axis-aligned
    segments that block.py can cut as channels.
  * the nets and their lids and sides come from harness.py; the pocket's wire pads are at its inner end (|x| = 50), at the pocket's middle in y (the real wires fan out along the pocket's 24.6 mm).
  * wire: 30 AWG silicone (0.6 mm over the insulation: the size cable_check.py uses for the strut wires) for signals; 28 AWG silicone (0.8 mm) where a net carries power.  Masses per metre: ASM from copper
    density and a 0.2 mm silicone wall.  Each wire gets 6 mm at each end for the pad tail and a 10% slack allowance.
  * ends that the layout does not place (the cells' wire exits, the servo plugs' depth) are my assumptions and are marked ASM in the table.
Not done: the wires' fan-out along the pocket, the bundle's twisting and the connector bodies; the real shell's draft and ribs (the block is a design volume, `block.py`).
"""
import contextlib
import heapq
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
with contextlib.redirect_stdout(io.StringIO()):
    import layout as LY
    import harness as HN

STEP = 2.0                                           # mm, grid cell
BEND = 2                                             # bend cost in cells

blocked_mm = ~LY.keep_in | LY.occ
for _m in LY.placed.values():
    blocked_mm = blocked_mm | _m
# 2 mm grid from the 1 mm voxels: a cell is blocked if any voxel in it is
nx, ny, nz = (np.array(blocked_mm.shape) // 2).tolist()
cells = blocked_mm[: nx * 2, : ny * 2, : nz * 2].reshape(nx, 2, ny, 2, nz, 2).any(axis=(1, 3, 5))
pad = np.pad(cells, 1, constant_values=True)
dil = np.zeros_like(cells)
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            dil |= pad[1 + dx: 1 + dx + nx, 1 + dy: 1 + dy + ny, 1 + dz: 1 + dz + nz]
FREE = ~dil                                          # cell centres at least 2 mm from anything


def to_cell(p):
    return (int((p[0] + 70) // STEP), int((p[1] + 70) // STEP), int(p[2] // STEP))


def to_mm(c):
    return (c[0] * STEP - 70 + STEP / 2, c[1] * STEP - 70 + STEP / 2, c[2] * STEP + STEP / 2)


def snap(p, tag):
    """Nearest free cell to a point (the anchors sit beside obstacles)."""
    c0 = to_cell(p)
    best = None
    for r in range(0, 4):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    c = (c0[0] + dx, c0[1] + dy, c0[2] + dz)
                    if 0 <= c[0] < nx and 0 <= c[1] < ny and 0 <= c[2] < nz and FREE[c]:
                        d = (dx * dx + dy * dy + dz * dz)
                        if best is None or d < best[0]:
                            best = (d, c)
        if best:
            return best[1]
    raise SystemExit(f"no free cell near {tag} {p}")


DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def route(a_mm, b_mm, tag):
    a, b = snap(a_mm, tag + " start"), snap(b_mm, tag + " end")
    pq = [(0, 0, a, -1)]
    best = {(a, -1): 0}
    prev = {}
    goal = None
    while pq:
        f, g, c, d = heapq.heappop(pq)
        if best.get((c, d), 1e9) < g:
            continue
        if c == b:
            goal = (c, d); break
        for k, (dx, dy, dz) in enumerate(DIRS):
            n = (c[0] + dx, c[1] + dy, c[2] + dz)
            if not (0 <= n[0] < nx and 0 <= n[1] < ny and 0 <= n[2] < nz) or not FREE[n]:
                continue
            ng = g + 1 + (BEND if (d != -1 and k != d) else 0)
            if ng < best.get((n, k), 1e9):
                best[(n, k)] = ng; prev[(n, k)] = (c, d)
                h = abs(n[0] - b[0]) + abs(n[1] - b[1]) + abs(n[2] - b[2])
                heapq.heappush(pq, (ng + h, ng, n, k))
    if goal is None:
        return None
    path = [goal[0]]
    cur = goal
    while cur in prev:
        cur = prev[cur]; path.append(cur[0])
    path = path[::-1]
    pts = [to_mm(path[0])]
    for i in range(1, len(path) - 1):                 # keep only the corners
        d1 = tuple(np.subtract(path[i], path[i - 1])); d2 = tuple(np.subtract(path[i + 1], path[i]))
        if d1 != d2:
            pts.append(to_mm(path[i]))
    pts.append(to_mm(path[-1]))
    pts = [tuple(float(v) for v in a_mm)] + pts + [tuple(float(v) for v in b_mm)]
    length = sum(abs(np.array(pts[i + 1]) - np.array(pts[i])).sum() for i in range(len(pts) - 1))
    return pts, float(length)


# ---- anchors ----
P = HN.pockets()
PX = 50.0
def pocket(lid, side):                                  # the wire-pad end of a lid's pocket: lid "lower" z = 11, "upper" z = 49; side +1 / -1
    L = P["+" if side > 0 else "-"]
    return (side * PX, -5.0 + L / 2, 11.0 if lid == "lower" else 49.0)

CAM_END = (48.0, 60.0, 12.0)            # under the camera board's lower edge (the board's box is y 57 to 66, z 13 to 47)
LED_END = (61.0, 66.7, 25.0)            # beside the LED ring board's outboard edge (the ring board is x 39.2 to 59.9, y 66 to 67.5)
ANT_END = (-12.0, -61.0, 30.0)          # behind the XBee carrier board's -x end (layout.py: x -11 to 11, y -67 to -64, z 22 to 38), in the rear bay's centre
BATT_END = (30.0, 44.0, 30.0)           # the protection board's +y face (layout.py: x 26.5 to 34.5, y 39 to 42, z 24 to 36), at the battery's +x end in the front bay
# Servo connectors (Feetech STS3215 specification, page 6; layout.py "plug zone"): two 3-pin terminals per servo on its back face, facing the centre gap; the wires leave the plugs' rear ends into the gap.
# Two nodes in the gap: B at the mouth of the gap between the two B servos' plug zones (y 11 to 18; reached from the +y side), A between the two A servos' (y -34 to -41; reached from the +y side, now that the battery is out of the gap).
# The two servos of a pair are joined by a short jumper across the gap at the node (about 8 mm each: in the lengths below as 2 x 8 mm).
SERVO = {"B": (0.0, 23.0, 30.0), "A": (0.0, -31.5, 30.0)}
SOLAR_BOTTOM = (-40.0, 4.0, 5.0)        # ASM: the bottom lid cells' wires leave the lid at its -x edge (just outside the board, x = -40) at y = 4 (the cells' tabs: layout of the cell pocket not done)
SOLAR_ENDS = ((-17.47, 66.0, 30.0), (17.47, -66.0, 30.0))   # the end-face cell pockets' centres (cell_endface.py), wires leave at the pocket's middle

# bundles: (name, from, to, nets: [(count, awg)], note)
S30, S28 = 30, 28
bundles = [
    ("camera end (lower + pocket to the camera board)", pocket("lower", +1), CAM_END, [(10, S30)], "SCK, MOSI, MISO, CS, SDA, SCL, INT, LED enable, 3V3, GND"),
    ("LED ring supply (upper + pocket to the ring board)", pocket("upper", +1), LED_END, [(2, S28)], "V7.4 and GND for the three LED pairs (0.6 W while on)"),
    ("link signals (lower + pocket to upper + pocket)", pocket("lower", +1), pocket("upper", +1), [(3, S30)], "boost enable, charger status, battery current sense (moved to the + side of the upper lid: they were on its - side, across the body)"),
    ("battery (protection board to upper + pocket)", BATT_END, pocket("upper", +1), [(12, S28)], "VBAT 6 and GND 6 (the battery path, 3.5 A peak)"),
    ("antenna end (lower - pocket to the XBee carrier board)", pocket("lower", -1), ANT_END, [(5, S30)], "XBee TX, RX, sleep, 3V3, GND (to the XBee carrier board beside the patch)"),
    ("power across (upper + pocket to lower - pocket)", pocket("upper", +1), pocket("lower", -1), [(8, S28)], "V7.4 in 3, GND return 3, VBAT in 2 (wheel drivers, 3.3 V converter)"),
    ("solar: end face at the camera end (to upper - pocket)", SOLAR_ENDS[0], pocket("upper", -1), [(2, S30)], "one cell string: + and -"),
    ("solar: end face at the antenna end (to upper - pocket)", SOLAR_ENDS[1], pocket("upper", -1), [(2, S30)], "one cell string: + and -"),
    ("solar: bottom lid cells (to upper - pocket)", SOLAR_BOTTOM, pocket("upper", -1), [(2, S30)], "one cell string: + and -"),
]
# the servo chain: power (V7.4, GND) and the bus's data wire visiting the four servos' connectors (each servo has two in parallel, so the chain passes through), fed from the upper + pocket (power);
# the data wire's feed from the lower - pocket is not routed separately (ASM: it joins the chain at the B node)
chain = [("servo chain: upper + pocket to the B servos' plugs", pocket("upper", +1), SERVO["B"]), ("servo chain: B servos to the A servos' plugs", SERVO["B"], SERVO["A"])]
for nm, a, b in chain:
    bundles.append((nm, a, b, [(3, S30)], "V7.4, GND, bus data; plus short jumpers across the gap at each node (2 x 8 mm per servo pair, ASM)"))

OD = {30: 0.6, 28: 0.8}                                   # mm over the insulation (ASM)
G_PER_M = {30: 0.75, 28: 1.1}                             # g per metre, copper plus a 0.2 mm silicone wall (ASM)
END_TAIL, SLACK = 6.0, 1.10

rows, out, total_len, total_mass = [], {}, 0.0, 0.0
for nm, a, b, nets, note in bundles:
    r = route(a, b, nm)
    if r is None:
        rows.append((nm, None)); continue
    pts, ln = r
    wires = sum(c for c, _ in nets)
    area = sum(c * np.pi / 4 * OD[g] ** 2 for c, g in nets)
    side = max(2.0, float(np.sqrt(area / 0.5)) + 0.4)                  # square channel side at 50% fill plus a clearance
    wlen = (ln * SLACK + 2 * END_TAIL) / 1000                          # m per wire
    mass = sum(c * wlen * G_PER_M[g] for c, g in nets)
    total_len += ln; total_mass += mass
    rows.append((nm, (ln, wires, side, wlen, mass, len(pts) - 1, note)))
    out[nm] = {"points": [list(p) for p in pts], "length_mm": ln, "wires": wires, "channel_side_mm": round(side, 1)}

print(f"free cells {FREE.sum()} of {FREE.size} on a {STEP:.0f} mm grid (2 mm clear of every obstacle)\n")
print(f"{'bundle':58s} {'route mm':>8s} {'wires':>5s} {'seg':>3s} {'channel':>7s} {'wire m':>6s} {'g':>5s}")
for nm, r in rows:
    if r is None:
        print(f"{nm:58s}   NO ROUTE"); continue
    ln, w, side, wl, m, seg, note = r
    print(f"{nm:58s} {ln:8.0f} {w:5d} {seg:3d} {side:5.1f} mm {wl:6.3f} {m:5.2f}")
# ---- independent check at 1 mm: sweep a square channel of the bundle's side (at least 3 mm: the smallest channel worth moulding, ASM) along each route and count the obstacle voxels it touches
MIN_CH = 3.0
print("\nchannel check at 1 mm (obstacle voxels inside the swept channel, not counting the 4 mm at each end where it meets a pocket or a board):")
union = np.zeros_like(blocked_mm)
for nm, r in rows:
    if r is None: continue
    side = max(MIN_CH, r[2]); out[nm]["channel_side_mm"] = round(side, 1)
    pts = np.array(out[nm]["points"]); bad = 0; m_all = np.zeros_like(blocked_mm)
    for i in range(len(pts) - 1):
        lo = np.minimum(pts[i], pts[i + 1]) - side / 2; hi = np.maximum(pts[i], pts[i + 1]) + side / 2
        m_all |= LY.box_mask(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
    ends = LY.box_mask(pts[0][0] - 4, pts[0][0] + 4, pts[0][1] - 4, pts[0][1] + 4, pts[0][2] - 4, pts[0][2] + 4) | LY.box_mask(pts[-1][0] - 4, pts[-1][0] + 4, pts[-1][1] - 4, pts[-1][1] + 4, pts[-1][2] - 4, pts[-1][2] + 4)
    bad = int((m_all & blocked_mm & ~ends).sum())
    union |= m_all
    print(f"  {nm:58s} channel {side:3.1f} mm: {bad} obstacle voxels" + ("" if bad == 0 else "   <-- CONFLICT"))
print(f"  all channels together (overlaps counted once): {union.sum() * LY.vox:.1f} cm3 of the block")
print(f"\ntotal route length {total_len:.0f} mm; wire mass {total_mass:.1f} g (layout.py allows 15 g for wiring, connectors and board links; the strut-motor wires and the camera-end boards' own wiring are not in this list)")
out_dir = HERE / "out"; out_dir.mkdir(exist_ok=True)
(out_dir / "wire_routes.json").write_text(json.dumps(out, indent=1))
print("wrote", out_dir / "wire_routes.json")
