"""Can the rover right itself from every rest orientation if each strut is limited to a stop window? (docs/mechanical-spec.md item 7)

Run (needs the repository's .venv): .venv/bin/python hardware/strut/stop_window_check.py [WINDOW_DEG] [LOW_DEG] [skip_full]
Searches the chassis simulation's state graph (hardware/drivetrain/chassis_sim.py: strut angles on a 15 degree grid, one strut moves at a time, 60 degree minimum separation,
the body settles by rolling downhill in centre-of-mass height) from every rest state to an upright rest (theta within 8 degrees of 0), once with full-circle strut travel and once with each
strut limited to a window of WINDOW_DEG degrees starting LOW_DEG degrees from its home stance (home: A at 330, B at 210). The windows are linear: a strut cannot cross the dead sector.
"""
import sys, math, time
from collections import deque
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "drivetrain"))
import chassis_sim as C

STEP = 15
N = 360 // STEP
HOME = {"A": 330.0, "B": 210.0}
WINDOW = float(sys.argv[1]) if len(sys.argv) > 1 else 340.0
LOW = float(sys.argv[2]) if len(sys.argv) > 2 else -145.0      # degrees from home at the low stop; the high stop is LOW + WINDOW
U_LO, U_HI = math.ceil(LOW / STEP), math.floor((LOW + WINDOW) / STEP)    # allowed unwrapped grid index relative to home (15 degree units)

def tkey(th):
    return int(round(math.degrees(th) / 2.0)) % 180

def explore(windowed):
    """Return (states, edges, goal states). A state is (uA, uB, thkey); u is the unwrapped index from home in the windowed case, the index mod N otherwise."""
    def phi(which, u):
        return (HOME[which] + STEP * u) % 360.0
    def inside(u):
        return (U_LO <= u <= U_HI) if windowed else True
    lo_u, hi_u = (U_LO, U_HI) if windowed else (0, N - 1)
    rest = {}
    starts = []
    for uA in range(lo_u, hi_u + 1):
        for uB in range(lo_u, hi_u + 1):
            a, b = phi("A", uA), phi("B", uB)
            if not C.arc_ok(a, b):
                continue
            sh = C.Shape(a, b)
            seen = {}
            for t0 in range(0, 360, 20):
                th = C.settle(sh, math.radians(t0))
                seen[tkey(th)] = th
            for k, th in seen.items():
                starts.append((uA, uB, k)); rest[(uA, uB, k)] = th
    graph = {}
    goal = set()
    queue = deque(starts)
    visited = set(starts)
    t0 = time.time()
    while queue:
        s = queue.popleft()
        uA, uB, k = s
        th = rest[s]
        if math.degrees(th) < 8.0 or math.degrees(th) > 352.0:
            goal.add(s)
        graph[s] = []
        for which in ("A", "B"):
            for d in (1, -1):
                nA, nB = (uA + d, uB) if which == "A" else (uA, uB + d)
                if windowed and not (inside(nA) and inside(nB)):
                    continue
                if not windowed:
                    nA, nB = nA % N, nB % N
                ok, th2, pk, rolled = C.move(phi("A", uA), phi("B", uB), th, which, d * STEP)
                if not ok:
                    continue
                s2 = (nA, nB, tkey(th2))
                graph[s].append(s2)
                if s2 not in visited:
                    visited.add(s2); rest[s2] = th2; queue.append(s2)
        if len(graph) % 500 == 0:
            print(f"    {len(graph)} states expanded, {len(queue)} queued, {time.time() - t0:.0f} s", flush=True)
    return starts, graph, goal

def solve(windowed):
    starts, graph, goal = explore(windowed)
    rev = {}
    for s, outs in graph.items():
        for s2 in outs:
            rev.setdefault(s2, []).append(s)
    ok = set(goal); queue = deque(goal)
    while queue:
        s = queue.popleft()
        for p in rev.get(s, []):
            if p not in ok:
                ok.add(p); queue.append(p)
    inverted = [s for s in starts if s not in goal]
    bad = [s for s in inverted if s not in ok]
    return starts, goal, inverted, bad

print(f"strut grid {STEP} degrees; window {WINDOW:.0f} degrees from {LOW:+.0f} to {LOW + WINDOW:+.0f} degrees about home (grid indices {U_LO} to {U_HI})")
SKIP_FULL = len(sys.argv) > 3 and sys.argv[3] == "skip_full"
for windowed in ((True,) if SKIP_FULL else (False, True)):
    t = time.time()
    starts, goal, inverted, bad = solve(windowed)
    name = "windowed " if windowed else "full circle"
    print(f"{name}: {len(starts)} rest states, {len(goal)} already upright, {len(inverted)} not upright, {len(bad)} cannot reach upright ({100 * len(bad) / max(1, len(inverted)):.1f}%)  [{time.time() - t:.0f} s]")
    if windowed:
        # a rover flipped over with its struts held in a working pose starts with each strut near home, not at an arbitrary place in its window: score the starts by how far from home they are
        for R in (3, 6, 8, 12):
            near = [s for s in inverted if abs(s[0]) <= R and abs(s[1]) <= R]
            nb = [s for s in near if s in set(bad)]
            print(f"   starts within +-{R * STEP} degrees of home: {len(near)} not upright, {len(nb)} cannot reach upright ({100 * len(nb) / max(1, len(near)):.1f}%)")
    if bad:
        by = {}
        for uA, uB, k in bad:
            by.setdefault((uA, uB), 0); by[(uA, uB)] += 1
        print("   stuck strut-index pairs (a few):", list(by)[:12])
