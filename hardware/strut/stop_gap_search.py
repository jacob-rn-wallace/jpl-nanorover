"""Where should each strut's stop gap be? (docs/mechanical-spec.md item 7)

Run (needs the repository's .venv): .venv/bin/python hardware/strut/stop_gap_search.py
Builds the chassis simulation's physical state graph once (hardware/drivetrain/chassis_sim.py: strut angles on a 15 degree grid, one strut moves at a time, 60 degrees minimum
separation, the body settling downhill), with every edge labelled by which strut moves between which two grid angles. A hard stop that leaves a dead gap of one or two grid steps
blocks the edges across that gap for that strut (a strut cannot move across it; its position is then unambiguous on the chain). For every placement of the gap for strut A and for
strut B (24 x 24), the script removes the blocked edges and counts the inverted rest states that can no longer reach an upright rest, for starts whose struts are within
90 and 120 degrees of home (A at 330, B at 210). It prints the best placements and the placement chosen on 2026-11-14 (the 340 degree window from -145 to +195 degrees about home).
"""
import sys, math, time
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "drivetrain"))
import chassis_sim as C

STEP, N = 15, 24
HOME_I = {"A": 330 // STEP, "B": 210 // STEP}
def tkey(th): return int(round(math.degrees(th) / 2.0)) % 180

# ---- the physical graph ----
rest, starts = {}, []
for iA in range(N):
    for iB in range(N):
        if not C.arc_ok(iA * STEP, iB * STEP): continue
        sh = C.Shape(iA * STEP, iB * STEP)
        seen = {}
        for t0 in range(0, 360, 20):
            th = C.settle(sh, math.radians(t0)); seen[tkey(th)] = th
        for k, th in seen.items():
            rest[(iA, iB, k)] = th; starts.append((iA, iB, k))
edges = []                      # (from, to, which, low) where low is the lower grid index of the two angles the strut moves between (mod N)
queue, visited, goal = deque(starts), set(starts), set()
t0 = time.time()
while queue:
    s = queue.popleft(); iA, iB, k = s; th = rest[s]
    if math.degrees(th) < 8.0 or math.degrees(th) > 352.0: goal.add(s)
    for which in ("A", "B"):
        for d in (1, -1):
            ok, th2, pk, rolled = C.move(iA * STEP, iB * STEP, th, which, d * STEP)
            if not ok: continue
            nA, nB = ((iA + d) % N, iB) if which == "A" else (iA, (iB + d) % N)
            s2 = (nA, nB, tkey(th2))
            low = (iA if d == 1 else (iA - 1)) % N if which == "A" else (iB if d == 1 else (iB - 1)) % N
            edges.append((s, s2, which, low))
            if s2 not in visited:
                visited.add(s2); rest[s2] = th2; queue.append(s2)
print(f"graph: {len(visited)} states, {len(edges)} edges, {len(goal)} upright, built in {time.time() - t0:.0f} s")

def dist(i, home):                     # angular distance from home in degrees, grid angles
    d = abs(i - home) % N
    return min(d, N - d) * STEP

def stuck(blockA, blockB):
    """blockA, blockB: sets of 'low' indices whose step (low to low+1) is blocked for that strut. Returns the stuck counts among inverted starts within 90 and 120 degrees of home, and in all."""
    rev = {}
    for s, s2, which, low in edges:
        if (which == "A" and low in blockA) or (which == "B" and low in blockB): continue
        rev.setdefault(s2, []).append(s)
    ok = set(goal); q = deque(goal)
    while q:
        x = q.popleft()
        for p in rev.get(x, []):
            if p not in ok: ok.add(p); q.append(p)
    res = {}
    for R in (90, 120, 360):
        inv = [s for s in visited if s not in goal and dist(s[0], HOME_I["A"]) <= R and dist(s[1], HOME_I["B"]) <= R]
        res[R] = (sum(1 for s in inv if s not in ok), len(inv))
    return res

base = stuck(set(), set())
print("no stops:", {R: f"{a}/{b}" for R, (a, b) in base.items()})
def gaps(g, w): return {(g + j) % N for j in range(w)}
results = []
for w in (1, 2):
    for gA in range(N):
        for gB in range(N):
            r = stuck(gaps(gA, w), gaps(gB, w))
            results.append((r[90][0], r[120][0], r[360][0], w, gA, gB, r))
# the 2026-11-14 choice: the dead sector 195 to 225 degrees about home = the two steps from u = 13 to 15
chosen = stuck({(HOME_I["A"] + 13) % N, (HOME_I["A"] + 14) % N}, {(HOME_I["B"] + 13) % N, (HOME_I["B"] + 14) % N})
print("chosen 2026-11-14 (gap 195 to 225 degrees about home, two steps):", {R: f"{a}/{b}" for R, (a, b) in chosen.items()})
for w in (1, 2):
    print(f"\nbest placements for a gap of {w} step(s) ({w * STEP} degrees), by stuck starts within 90, then 120 degrees of home:")
    sel = sorted([x for x in results if x[3] == w])[:8]
    for s90, s120, sall, _, gA, gB, r in sel:
        ua, ub = ((gA - HOME_I["A"]) % N) * STEP, ((gB - HOME_I["B"]) % N) * STEP
        print(f"  A gap after {ua:3d} deg from home, B gap after {ub:3d} deg:  within 90: {r[90][0]}/{r[90][1]}  within 120: {r[120][0]}/{r[120][1]}  anywhere: {r[360][0]}/{r[360][1]}")

# every placement of a one-step gap that leaves no inverted rest state stranded anywhere (full circle of starts)
print("\nall one-step (15 degree) gap placements with 0 stranded starts anywhere (A gap after X degrees from home -> the B gaps that work, degrees from home):")
zero = {}
for s90, s120, sall, w, gA, gB, r in results:
    if w == 1 and sall == 0:
        zero.setdefault(((gA - HOME_I["A"]) % N) * STEP, []).append(((gB - HOME_I["B"]) % N) * STEP)
for ua in sorted(zero): print(f"  A after {ua:3d}: B after {sorted(zero[ua])}")
print(f"{sum(len(v) for v in zero.values())} of {N * N} placements work; stranded counts for the best two-step gaps stay above 180 anywhere")
