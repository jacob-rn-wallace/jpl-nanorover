"""Mass budget for a carbon-fibre (or forged-carbon) body, 140 x 140 x 60 mm, hollow shell with a lid.

Run: python3 hardware/body/cf_budget.py   (no CAD needed). Densities are typical catalogue values, not measured parts.
"""
L = W = 140.0; H = 60.0
TARGET_G = 386.0                      # CLAUDE.md / handover section 12: what is left of 1.0 kg for body, electronics, cells, camera
area_cm2 = (2 * L * W + 4 * L * H) / 100.0     # outer surface, six faces
print(f"outer surface {area_cm2:.0f} cm2")
print(f"{'material':28s} {'rho':>5s}", *[f"{t:>6.1f}mm" for t in (0.8, 1.0, 1.2, 1.5, 2.0, 2.5)])
for name, rho in (("woven CFRP laminate", 1.55), ("forged carbon (chopped)", 1.45)):
    if rho:
        print(f"{name:28s} {rho:5.2f}", *[f"{area_cm2 * t / 10 * rho:7.0f}" for t in (0.8, 1.0, 1.2, 1.5, 2.0, 2.5)])
# sandwich: two 0.3 mm skins + core of thickness t-0.6 at 0.06 g/cm3 (rigid foam); skins 1.55 g/cm3
print(f"{'CF sandwich (0.3 skins, foam)':28s} {'':5s}", *[f"{area_cm2 * (2 * 0.03 * 1.55 + max(t - 0.6, 0) / 10 * 0.06):7.0f}" for t in (0.8, 1.0, 1.2, 1.5, 2.0, 2.5)])
print()
print("For comparison the Hammond box + lid plate is 961 g; the 'everything else' (servos, hub, struts, wheels, drive) is about 614 g.")
for t in (1.0, 1.5, 2.0):
    shell = area_cm2 * t / 10 * 1.55
    # inserts/bosses/seal/fasteners allowance: lid screws, inserts, hub-bore reinforcement rings, O-ring/gasket
    extras = 4 * 2.0 + 4 * 6.0 + 15.0
    left = TARGET_G - shell - extras
    print(f"woven {t:.1f} mm: shell {shell:5.0f} g + inserts/rings/gasket ~{extras:.0f} g -> {left:5.0f} g left for electronics, cells, camera, wiring")
