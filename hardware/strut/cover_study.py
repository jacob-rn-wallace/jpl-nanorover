#!/usr/bin/env python3
"""Study of a covered wire channel in the strut arms (owner idea, 2026-11-17): a 2 mm base with the channel cut in it and a 1 mm skin on the INBOARD face, closing the tube end flush.
Plain python3 (no CAD).  Compares (a) the monolithic 3 mm plate now in strut.py, (b) base + skin held by screws and a groove gasket, (c) base + skin bonded (epoxy; only if never opened),
and sizes the rigid conductor rails for (c).  Tags: ASM = assumption, ESTIMATE = my arithmetic from a typical figure.   Prints the numbers docs/strut-cover.md quotes.
"""
import math

E = 69e3            # N/mm2, 6061-T6 (handbook)
YIELD = 276.0       # N/mm2, 6061-T6 (handbook)
L, R1, R2 = 70.0, 15.0, 12.0     # pivot to tip (strut.py), boss and tip radii
T_PLATE, T_BASE, T_SKIN = 3.0, 1.8, 1.2
CH_W, CH_D = 3.0, 1.0            # channel cut in the base from the inboard face (strut.py has 1.5 x 1.0 for two 0.6 mm wires; 3.0 gives a flat PCB rail room)
F_SIDE = 5.0                     # N sideways at the tip: the same assumed knock as strut-spec.md (isogrid study)


def width(x):
    return 2 * (R1 + (R2 - R1) * x / L)


def base_i(w):
    """Base section (width w, thickness T_BASE) less the channel at its inboard edge, about the base's own centre."""
    a = CH_W * CH_D
    d = T_BASE / 2 - CH_D / 2
    return w * T_BASE ** 3 / 12 - (CH_W * CH_D ** 3 / 12 + a * d * d)


def inertia(case, x):
    w = width(x)
    if case == "mono":
        return w * T_PLATE ** 3 / 12
    skin_i = w * T_SKIN ** 3 / 12
    if case == "slip":                                         # screws and gasket: the layers bend about their own centres
        return base_i(w) + skin_i
    a_b, a_s = w * T_BASE - CH_W * CH_D, w * T_SKIN            # bonded: one section about the common centroid (the channel's effect on the base centroid is ignored)
    y_b, y_s = T_BASE / 2, T_BASE + T_SKIN / 2
    yc = (a_b * y_b + a_s * y_s) / (a_b + a_s)
    return base_i(w) + a_b * (y_b - yc) ** 2 + skin_i + a_s * (y_s - yc) ** 2


def tip_deflection(case, n=700):
    """Cantilever from the pivot boss edge with a sideways tip load; curvature integrated with the tapering width."""
    dx = (L - R1) / n
    return sum(F_SIDE * (L - x) ** 2 / (E * inertia(case, x)) * dx for x in (R1 + (k + 0.5) * dx for k in range(n)))


print("== stiffness of the arm to a sideways knock (5 N at the tip, ASM) ==")
for case, far in (("mono", T_PLATE / 2), ("bonded", 1.7), ("slip", T_BASE / 2)):
    s = F_SIDE * (L - R1) * far / inertia(case, R1)
    print(f"  {case:7s} I(root) {inertia(case, R1):6.1f} mm4   tip deflection {tip_deflection(case):5.2f} mm   root stress {s:5.1f} MPa  (6061-T6 yield {YIELD:.0f}: factor {YIELD / s:4.0f})")
print(f"  slip is {inertia('slip', R1) / inertia('mono', R1) * 100:.0f}% and bonded {inertia('bonded', R1) / inertia('mono', R1) * 100:.0f}% of the monolithic plate's I at the root")

print("\n== gasket for the screwed skin: a cord in a groove with a metal-to-metal stop (the squeeze then does not depend on screw torque) ==")
CORD, SQUEEZE, G_W = 0.50, 0.20, 0.65
G_D = CORD * (1 - SQUEEZE)
fill = math.pi / 4 * CORD ** 2 / (G_W * G_D)
print(f"  0.50 mm silicone cord, groove {G_W} wide x {G_D:.2f} deep in the base, squeeze {SQUEEZE * 100:.0f}%, groove fill {fill * 100:.0f}% (keep under 90%)")
T_SCREW, K = 0.15, 0.2     # N.m for an M1.6 A2 screw (ESTIMATE, typical), torque coefficient
print(f"  M1.6 clamp force about {T_SCREW / (K * 1.6e-3):.0f} N per screw at {T_SCREW} N.m (ESTIMATE); thread engagement as modelled 1.4 mm = {1.4 / 1.6:.2f} d in the 1.8 mm base; stripping capacity about {0.5 * math.pi * 1.6 * 1.4 * 0.6 * 207:.0f} N (ESTIMATE: 6061-T6 shear 207 MPa), so tighten to 0.1 N.m, not {T_SCREW}")

print("\n== screw count (two rows beside the groove; pitch set by the 1 mm skin bending between screws, ASM) ==")
PITCH = 8.5
rows = 10                      # as modelled: five positions a side (strut.py SK_SCREW_X)
ring, pivot = 3, 0
per = rows + ring + pivot
print(f"  pitch {PITCH} mm: {rows} along the arm + {ring} round the tip cap + {pivot} at the pivot = about {per} per strut, {4 * per} for the rover, M1.6 x 4 about 0.12 g each = {4 * per * 0.12:.0f} g")

print("\n== rigid conductor rails (bonded option): a 0.8 mm FR-4 strip with two traces sits in the 3.0 x 1.0 mm channel ==")
RHO, I_STALL = 1.72e-8, 1.6
for oz, t_um in (("1 oz", 35), ("2 oz", 70)):
    w_mm = 1.0
    r_per_m = RHO / (w_mm * 1e-3 * t_um * 1e-6)
    r = r_per_m * (L + 10) * 1e-3 * 2
    a_mil2 = (w_mm / 0.0254) * (t_um / 25.4)
    amp = 0.048 * 10 ** 0.44 * a_mil2 ** 0.725         # IPC-2221, outer layer, 10 C rise
    print(f"  {oz} copper, {w_mm} mm trace: {r_per_m * 1e3:.0f} mohm/m; out and back over {L + 10:.0f} mm = {r * 1e3:.0f} mohm; at stall ({I_STALL} A, ESTIMATE) {r * I_STALL * 1e3:.0f} mV, {r * I_STALL ** 2 * 1e3:.0f} mW; ampacity {amp:.1f} A")
