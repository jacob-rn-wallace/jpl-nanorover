"""Analytic mass estimate for the wheel and what it would weigh if lightened.  Pure Python, no CAD.

    python3 hardware/drivetrain/wheel_mass.py

Geometry is the parameter block of hardware/wheel/wheel.py (R_ROOT 29.75, R_TIP 32.5, L_DRUM 34.5, H_CONE 10.1 mm).
The first row reproduces the CAD's ~78 g as a check on this estimate; the other rows are choices, not the original's.
Wall thicknesses and materials are ASSUMED.  Printed-plastic densities are typical for PA12 (MJF/SLS), not a measured part.
"""
import math

R_ROOT, R_TIP, L_DRUM, H_CONE = 29.75, 32.5, 34.5, 10.1   # mm, from wheel.py
N_TEETH, HELIX = 16, 43.5
SERR_KEEP = 0.78      # fraction of grouser volume left after the serrations (notch 1.4 mm deep on a 3.35 mm blade, half the length)


def wheel(wall, end_t, cone_t, grouser_t, hub_od, hub_len, rho, hub_rho=None, collar=True):
    """Grams. wall = cylinder wall thickness (mm), rho in g/cm3. Hub tube and collar use hub_rho if given (e.g. metal bushing)."""
    cyl = math.pi * (R_ROOT**2 - (R_ROOT - wall)**2) * (L_DRUM - end_t)
    plate = math.pi * R_ROOT**2 * end_t
    slant = math.hypot(R_ROOT, H_CONE)
    cone = math.pi * R_ROOT * slant * cone_t
    blade_len = L_DRUM / math.cos(math.radians(HELIX))
    groups = N_TEETH * grouser_t * (R_TIP - R_ROOT + 0.6) * blade_len * SERR_KEEP
    hub = math.pi * ((hub_od / 2)**2 - 3**2) * hub_len           # 6 mm bore for the axle
    col = math.pi * 4**2 * 8 if collar else 0
    body = cyl + plate + cone + groups
    return (body * rho + (hub + col) * (hub_rho or rho)) / 1000.0


ROWS = [
    # label, wall, end, cone, grouser, hub_od, hub_len, rho, hub_rho
    ("CAD as modelled (Al 6061: wall 2.5, plate 2, cone 1.5, blades 1.2)", 2.5, 2.0, 1.5, 1.2, 12, 40, 2.70, None),
    ("Al thin-walled (wall 1.0, plate 1.0, cone 0.8, blades 0.8)",         1.0, 1.0, 0.8, 0.8, 12, 40, 2.70, None),
    ("Al thinnest machinable (wall 0.8, plate 0.8, cone 0.6, blades 0.6)", 0.8, 0.8, 0.6, 0.6, 10, 30, 2.70, None),
    ("PA12 printed (wall 1.5, plate 1.5, cone 1.2, blades 1.0)",           1.5, 1.5, 1.2, 1.0, 12, 40, 1.01, None),
    ("PA12 printed, thin (wall 1.2, plate 1.2, cone 1.0, blades 0.8)",     1.2, 1.2, 1.0, 0.8, 12, 40, 1.01, None),
]

if __name__ == "__main__":
    print(f"{'wheel':72s} {'g each':>7s} {'g x4':>6s}")
    for lab, *a in ROWS:
        g = wheel(*a)
        print(f"{lab:72s} {g:7.1f} {4*g:6.0f}")
