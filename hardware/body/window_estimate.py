"""Estimate of what a 0.5 mm sapphire window does to the VL53L5CX's crosstalk and signal, against 0.5 mm glass.   (plain python3; an ESTIMATE, not a measurement)

Run: python3 hardware/body/window_estimate.py
Method of 2026-11-14 (CLAUDE.md): no bench test is possible, so bound the effect by arithmetic. Three effects, each with a range (inputs are ASM unless marked):
  A. how much more light the window reflects (Fresnel, an incoherent slab: R_total = 2R / (1 + R));
  B. whether a DIRECT specular reflection from either surface can land on the receiver (geometry: the reflected ray is displaced sideways by 2 (g tan(a) + t tan(a'))), which is what
     ST's gap rule (0.5 to 0.7 mm, SRC: the cover-glass note, third-party mirror) is about: it lets us back out the emitter-to-receiver separation D;
  C. how much of the target's return the window loses (two passes).
Not estimable here: the scattered (diffuse) crosstalk and the sensor's absolute crosstalk limit (not found); that part stays a bench test, and the decision rule below says what to do without it.
"""
import math

N_GLASS, N_SAPPH = 1.52, 1.77            # refractive index near 940 nm (glass: a typical value ASM; sapphire: Edmund Optics listing, SRC)
T = 0.5                                  # window thickness, mm
HALF_FOV = math.radians(32.5)            # half the diagonal field of view of the 8x8 zones, about 65 degrees (ASM from the sensor's listing, to confirm)


def fresnel(n):
    r = ((n - 1) / (n + 1)) ** 2
    return r, 2 * r / (1 + r)             # one surface, the slab's total reflectance (incoherent)


def displacement(g, n, a=HALF_FOV, t=T):
    """Sideways displacement of a ray reflected from the window's outer surface, at the field's edge (g = gap sensor-to-window)."""
    ar = math.asin(math.sin(a) / n)
    return 2 * (g * math.tan(a) + t * math.tan(ar))


def inner(g, a=HALF_FOV):
    return 2 * g * math.tan(a)


print("A. reflection")
for name, n in (("glass", N_GLASS), ("sapphire", N_SAPPH)):
    r, tot = fresnel(n)
    print(f"  {name:9s} n {n}: {r * 100:4.1f}% a surface, {tot * 100:4.1f}% total reflected, {(1 - tot) * 100:4.1f}% transmitted, round-trip signal {(1 - tot) ** 2 * 100:4.1f}%")
rg, tg = fresnel(N_GLASS); rs, ts = fresnel(N_SAPPH)
print(f"  reflected light, sapphire / glass: {ts / tg:.2f}x; round-trip signal, sapphire / glass: {((1 - ts) / (1 - tg)) ** 2:.2f} (the ranging range falls by the square root of that, about {(1 - math.sqrt(((1 - ts) / (1 - tg)) ** 2)) * 100:.0f}%)")
print(f"  with a VIS-NIR AR coating (0.5% a surface, ASM): reflected {2 * 0.005 / 1.005 * 100:.1f}% total, which is {2 * 0.005 / 1.005 / ts * 100:.0f}% of the uncoated sapphire's (ST says: no coating over the apertures, so this is the fallback only)")

print("\nB. direct specular paths: the emitter-to-receiver separation D that a direct reflection would need to reach")
print("  ST's rule: a 0.5 mm glass window works with a gap up to 0.5 to 0.7 mm; taking that as the gap at which a direct path just reaches the receiver gives D (outer surface):")
Ds = [displacement(g, N_GLASS) for g in (0.5, 0.7)]
print(f"  D = {Ds[0]:.2f} to {Ds[1]:.2f} mm  (so I use D = 1.0 to 1.5 mm for the sensor; its real value is not in the sources I read)")
for D in (1.0, 1.5):
    print(f"  D = {D} mm: sapphire gap limit for a direct path to MISS the receiver: ", end="")
    gs = [g / 100 for g in range(1, 300) if displacement(g / 100, N_SAPPH) < D]
    gi = [g / 100 for g in range(1, 300) if inner(g / 100) < D]
    print(f"outer surface g < {max(gs) if gs else 0:.2f} mm, inner (sensor-side) surface g < {max(gi) if gi else 0:.2f} mm; glass: outer g < {max([g / 100 for g in range(1, 300) if displacement(g / 100, N_GLASS) < D] or [0]):.2f} mm")
print("  our gap is 0.5 mm (sapphire seated at y = 68.0): at D = 1.0 mm the outer-surface direct path is "
      f"{displacement(0.5, N_SAPPH):.2f} mm away, i.e. a MARGINAL miss; at 0.3 mm it is {displacement(0.3, N_SAPPH):.2f} mm (clear) and the inner surface {inner(0.3):.2f} mm.")

print("\nREADING (an estimate; the diffuse part and ST's absolute limit are not estimable here):")
print("  1. sapphire reflects about 1.8x the light of glass and costs about 14% of the round-trip signal (7% of the range); at the 12 to 16 cm that matters, the signal is plentiful, so the loss is harmless.")
print("  2. the direct-path geometry is marginal at a 0.5 mm gap and clear at 0.3 mm: DESIGN CHANGE: seat the sensor so the gap is 0.3 mm (or less, spacer-defined), with the black foam ring pressed against the glass round the sensor.")
print("  3. decision rule: build with uncoated sapphire at the 0.3 mm gap; if the bench test (when possible) shows crosstalk over the limit, use the AR-coated sapphire, then 0.5 mm glass. TO BE MEASURED: the sensor's reported")
print("     crosstalk histogram at 1 to 3 cm behind the real window, glass against sapphire.")
