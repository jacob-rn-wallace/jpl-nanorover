"""Hand checks for the strut tip clamp, the strut cable and the strut stops (docs/mechanical-spec.md items 2, 6 and 7).

Run: python3 hardware/strut/pivot_checks.py   (plain python, no CAD). Figures are from strut.py and hub.py (SRC = this repository's CAD constants) and from
the loads in docs/strut-spec.md; every material figure is an ASSUMPTION (ASM) unless marked.
"""
import math

# ---- 1. tip clamp: the 19 mm spindle tube in the 3 mm plate (strut.py: TIP_D 24, SPINDLE_OD 19.0, PLATE_T 3.0) ----
TIP_D, TUBE_OD, TUBE_ID, PLATE_T = 24.0, 19.0, 16.2, 3.0          # SRC strut.py
BORE = 19.1                                                          # SRC (bore on the 19 mm tube: 0.1 mm slip fit)
wall = (TIP_D - BORE) / 2
print(f"tip wall round the bore: {wall:.2f} mm; clamp length = plate thickness {PLATE_T} mm")
# loads on the wheel support (docs/strut-spec.md: 9 N bearing load static, 53 N in a 6x bump; the bearing pair's centre is about 40 mm outboard of the plate's inboard face, from strut.py)
LEVER = 118.25 - 77.25                                               # mm, bearing-pair centre (|x| 118.25) to strut A's plate inboard face (77.25), SRC strut.py
for name, f in (("static (9 N)", 9.0), ("6x bump (53 N)", 53.0)):
    m = f * LEVER / 1000                                             # N.m at the clamp
    couple = m / (PLATE_T / 1000)                                    # N: the two edge forces of the bore that resist the moment
    area = BORE * 1.0                                                # mm2 ASM: an edge contact strip of 1 mm along the tube on each edge of the bore
    print(f"  {name:16s} moment {m:.2f} N.m, bore edge force {couple:.0f} N, edge pressure {couple / area:.0f} MPa (6061-T6 yield about 275, ASM)")
I = math.pi / 64 * (TUBE_OD ** 4 - TUBE_ID ** 4)
print(f"  tube bending at the clamp (6x bump): {53.0 * LEVER * (TUBE_OD / 2) / I:.1f} MPa; tube I = {I:.0f} mm4 (wall {(TUBE_OD - TUBE_ID) / 2:.1f} mm)")
# motor reaction torque the clamp friction must hold: the #3068's stall torque 0.31 N.m (Pololu: 3.2 kg.cm at 6 V, 1.5 A), a worst case
T = 0.314
for mu in (0.2, 0.5):
    p = T / (mu * 2 * math.pi * (BORE / 2000) ** 2 * (PLATE_T / 1000))
    print(f"  stall reaction {T} N.m with mu = {mu}: bore pressure needed {p / 1e6:.2f} MPa, hoop stress in the tip wall {p * (BORE / 2) / wall / 1e6:.1f} MPa")
print("  -> strength is not the problem. The 3 mm clamp length is: a tilt of the tube of clearance / 3 mm (0.1 mm slip fit: 1.9 degrees if unclamped).")
print("     Fix: a tight fit plus retaining compound, and the M2 clamp screw needs an ear at the slit (a 2.45 mm wall cannot carry a screw head and thread).")

# ---- 2. cable round the hub boss: length to wrap and unwrap (strut.py: BOSS_D 30) ----
BOSS_R = 15.0 + 1.0 + 0.5                                            # boss radius plus a 1 mm clearance and half a cable
print("\ncable wrap round the 30 mm boss (radius to the cable centre %.1f mm):" % BOSS_R)
for travel in (340, 360, 540, 720):
    print(f"  {travel:4d} degrees of strut travel: {BOSS_R * math.radians(travel):6.0f} mm of cable to wrap or unwrap")
print(f"  free run along the arm from boss edge to the tip: {70 - 15:.0f} mm; the cable is looser than that only if it lies on the arm's face (a groove in the inboard face)")
print("  wire bend radius: 30 AWG silicone wire, 0.6 mm; a minimum bend of 5 times the diameter (ASM) is 3 mm, so a 16 mm radius is no problem")
print("  axial room on the boss: 7 mm (BOSS_T), so five turns of a 1.3 mm pair fit side by side; the 1 mm gap to the neighbour strut limits a pair to one layer")

# ---- 3. strut stops ----
print("\nstops: the chassis simulation (hardware/drivetrain/chassis_sim.py) uses each strut's angle over the FULL circle (a 5 degree grid from 0 to 360) with the two struts at least 60 degrees apart")
print("  my earlier claim that its poses stay within a half turn was not supported: it was wrong. The self-righting search (run below) moves strut A by up to 195 and B by 180 degrees")
print("  from the start stance in one sequence. See docs/mechanical-spec.md items 6 and 7.")
try:
    import contextlib, io, sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "drivetrain"))
    import chassis_sim as C                                   # needs numpy and matplotlib (the repository's .venv)
    for obj in ("torque", "moves"):
        with contextlib.redirect_stdout(io.StringIO()):
            r = C.righting(objective=obj)
        path, peak = r
        cum, lo, hi = {"A": 0, "B": 0}, {"A": 0, "B": 0}, {"A": 0, "B": 0}
        for which, d, pk, rolled, st in path:
            cum[which] += d; lo[which] = min(lo[which], cum[which]); hi[which] = max(hi[which], cum[which])
        print(f"  righting, objective {obj}: {len(path)} moves, peak {peak:.3f} N.m; excursion from the start stance: strut A {lo['A']:+d} to {hi['A']:+d}, strut B {lo['B']:+d} to {hi['B']:+d} degrees")
except Exception as e:      # plain python3 without the venv: skip
    print("  (righting search skipped:", type(e).__name__, ")")
