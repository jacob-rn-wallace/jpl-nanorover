"""The strut stop gap on a 5 degree grid (docs/mechanical-spec.md item 7; the follow-up to stop_gap_search.py, which used 15 degrees).

Run (needs the repository's .venv; about 10 minutes to build the graph, then a few minutes to search): .venv/bin/python hardware/strut/stop_gap_fine.py
Each strut's stop leaves a dead sector that the strut cannot enter or cross; on the 5 degree grid a sector 10 degrees wide removes 2 grid angles at most (9.5 degrees from a 1.5 mm
tab and a 1 mm pin on a 15 mm radius). For every placement of the sector for strut A and for strut B (72 x 72) it counts the inverted rest states, not themselves in a dead sector,
that can no longer reach an upright rest. It reports the design of 2026-11-14 (A's sector between absolute 15 and 30 degrees, B's between 345 and 360) and the set of placements that strand none.
"""
import sys, math, time
from collections import deque
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "drivetrain"))
import chassis_sim as C

STEP, N = 5, 72
def tkey(th): return int(round(math.degrees(th) / 2.0)) % 180

rest, starts = {}, []
t0 = time.time()
for iA in range(N):
    for iB in range(N):
        if not C.arc_ok(iA * STEP, iB * STEP): continue
        sh = C.Shape(iA * STEP, iB * STEP)
        seen = {}
        for t in range(0, 360, 20):
            th = C.settle(sh, math.radians(t)); seen[tkey(th)] = th
        for k, th in seen.items():
            rest[(iA, iB, k)] = th; starts.append((iA, iB, k))
print(f"{len(starts)} rest states found in {time.time() - t0:.0f} s", flush=True)
edges, queue, visited, goal = [], deque(starts), set(starts), set()
n = 0
while queue:
    s = queue.popleft(); iA, iB, k = s; th = rest[s]
    if math.degrees(th) < 8.0 or math.degrees(th) > 352.0: goal.add(s)
    for which in ("A", "B"):
        for d in (1, -1):
            ok, th2, pk, rolled = C.move(iA * STEP, iB * STEP, th, which, d * STEP, step=float(STEP))
            if not ok: continue
            nA, nB = ((iA + d) % N, iB) if which == "A" else (iA, (iB + d) % N)
            s2 = (nA, nB, tkey(th2)); edges.append((s, s2, which))
            if s2 not in visited:
                visited.add(s2); rest[s2] = th2; queue.append(s2)
    n += 1
    if n % 2000 == 0: print(f"  {n} states expanded, {len(queue)} queued, {time.time() - t0:.0f} s", flush=True)
print(f"graph: {len(visited)} states, {len(edges)} edges, {len(goal)} upright, {time.time() - t0:.0f} s", flush=True)

def stranded(remA, remB):
    """remA, remB: sets of removed grid indices (the dead sector). Returns (stranded, valid inverted starts)."""
    rev = {}
    for s, s2, which in edges:
        if (which == "A" and (s[0] in remA or s2[0] in remA)) or (which == "B" and (s[1] in remB or s2[1] in remB)): continue
        rev.setdefault(s2, []).append(s)
    ok = {g for g in goal if g[0] not in remA and g[1] not in remB}; q = deque(ok)
    while q:
        x = q.popleft()
        for p in rev.get(x, []):
            if p not in ok: ok.add(p); q.append(p)
    inv = [s for s in visited if s not in goal and s[0] not in remA and s[1] not in remB]
    return sum(1 for s in inv if s not in ok), len(inv)

def sector(centre_deg, k):
    """k removed grid angles centred on centre_deg (a half-step offset for even k)."""
    first = round(centre_deg / STEP - (k - 1) / 2.0)
    return {(first + j) % N for j in range(k)}

def row(gA):
    return gA, [stranded(sector(gA * STEP + STEP / 2, 2), sector(gB * STEP + STEP / 2, 2))[0] for gB in range(N)]

if __name__ == "__main__":
    for k in (1, 2):
        a, b = stranded(sector(22.5, k), sector(352.5, k))
        print(f"design of 2026-11-14 (A sector centred at 22.5, B at 352.5), {k} grid angle(s) removed each: {a} stranded of {b} inverted starts", flush=True)
    t1 = time.time()
    with Pool(4) as pool:
        rows = dict(pool.map(row, range(N)))
    print(f"search of 72 x 72 placements (2 grid angles removed each) in {time.time() - t1:.0f} s")
    good = [(gA, gB) for gA in range(N) for gB in range(N) if rows[gA][gB] == 0]
    print(f"{len(good)} of {N * N} placements strand none")
    by = {}
    for gA, gB in good: by.setdefault(gA, []).append(gB)
    print("A sector centred at (absolute degrees) -> B sector centres that work (absolute degrees):")
    for gA in sorted(by):
        print(f"  A {gA * STEP + STEP / 2:6.1f}: B " + " ".join(f"{gB * STEP + STEP / 2:.1f}" for gB in by[gA]))
