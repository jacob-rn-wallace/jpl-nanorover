"""Mixed solar array: how much of a lit face should be amorphous silicon (a-Si) and how much monocrystalline silicon (mono-Si)?

Run: python3 hardware/body/cell_split.py   (no CAD needed). SRC = a cited source (docs/body-redesign.md), ASM = my assumption.

Owner's framing (2026-11-12): the rover has to work in dim or dark conditions (hence the headlamp), so the cells cannot be what powers it;
they charge the battery and lighten its load. The right measure is therefore ENERGY PER DAY into the battery, not power at one light level.

Because each cell type's output is proportional to its area, the energy of a mixed face is a straight line in the a-Si fraction f.
A straight line has its best value at an end (f = 0 or f = 1), never in between, unless a constraint cuts the line. So the script prints
(1) the line's two ends and a few steps along it, (2) the break-even: how much weight indoor energy would need against outdoor energy
for any a-Si to pay, and (3) what the answer does when each uncertain input is moved.
"""
LARGE = 39.6 * 23.5 / 100       # cm2 (SRC: photo measurement, as power_budget.py)
CENTRE = 19.6 * 44.0 / 100
FACE = 10 * LARGE + 4 * CENTRE  # one top or bottom face, 127.6 cm2
CELL = FACE / 14                # average cell, about 9.1 cm2: the split comes in steps of about 7% of a face
SUN = 100.0                     # mW/cm2 (1000 W/m2)

# ---- output density, mW per cm2 of cell, per light condition. Each set is (mono-Si, a-Si). ----
def outdoor(eta_mono=0.20, eta_asi=0.06, frac=1.0):
    """frac = fraction of full sun (1.0 sun, 0.1 thin overcast: ASM, linear in light; real cells lose a little efficiency at low light)."""
    return (SUN * frac * eta_mono, SUN * frac * eta_asi)

# eta_mono 0.20 (ASM, good monocrystalline; power_budget.py uses 15/20/24 %), eta_asi 0.06 (SRC: a vendor blog's 6 % a-Si against 20 % mono; marketing-level)
INDOOR_200 = (2.8e-3, 5.9e-3)   # 200 lux CFL: poly-Si 2.8, a-Si 5.9 uW/cm2 (SRC: Applied Energy study via search, poly-Si used for mono)
INDOOR_500 = (8e-3, 10e-3)      # 500 lux LED: poly-Si 8, a-Si 10 uW/cm2 (SRC: as power_budget.py)

def energy(f, dens_by_hours):
    """mWh per day on one face with a fraction f of its area a-Si. dens_by_hours = [((mono, asi) mW/cm2, hours), ...]."""
    return sum(FACE * ((1 - f) * m + f * a) * h for (m, a), h in dens_by_hours)

def report(name, profile, steps=(0, 1, 2, 4, 7, 14)):
    base = energy(0, profile)
    print(f"\n{name}")
    print(f"  {'a-Si cells of 14':>16s} {'a-Si share':>10s} {'sun+overcast':>13s} {'indoor':>11s} {'total':>11s} {'vs all mono':>12s}")
    sunpart = [((m, a), h) for (m, a), h in profile if m > 0.5]
    inpart = [((m, a), h) for (m, a), h in profile if m <= 0.5]
    for k in steps:
        f = k / 14
        eo, ei = energy(f, sunpart), energy(f, inpart)
        print(f"  {k:16d} {f * 100:9.0f}% {eo:11.1f} mWh {ei:9.3f} mWh {eo + ei:9.1f} mWh {(eo + ei) / base * 100:10.1f}%")

# a day for the rover: sun-equivalent hours outdoors (ASM: 2 h outdoors in full sun, 2 h in overcast), the rest indoors.
day_a = [(outdoor(), 2.0), (outdoor(frac=0.1), 2.0), (INDOOR_200, 20.0)]
day_b = [(outdoor(), 0.5), (outdoor(frac=0.1), 1.0), (INDOOR_200, 22.5)]     # mostly indoors
day_c = [(outdoor(), 0.0), (outdoor(frac=0.1), 0.0), (INDOOR_200, 24.0)]     # never outdoors
report("Day A: 2 h full sun, 2 h overcast, 20 h indoors at 200 lux (all ASM)", day_a)
report("Day B: 0.5 h full sun, 1 h overcast, 22.5 h indoors at 200 lux (all ASM)", day_b)
report("Day C: 24 h indoors at 200 lux, never outdoors", day_c, steps=(0, 7, 14))

# ---- the break-even: how many hours of indoor light per hour of full sun make a-Si pay ----
print("\nBreak-even (a-Si pays only if its indoor gain beats its outdoor loss):")
for name, ind in (("200 lux CFL", INDOOR_200), ("500 lux LED", INDOOR_500)):
    gain_per_h = ind[1] - ind[0]                      # mW/cm2 gained per indoor hour
    for eta_asi in (0.06, 0.08, 0.10):
        m, a = outdoor(eta_asi=eta_asi)
        loss_per_h = m - a                            # mW/cm2 lost per hour of full sun
        print(f"  {name}, a-Si {eta_asi * 100:.0f}% outdoors: {loss_per_h / gain_per_h:6.0f} indoor hours per hour of full sun, "
              f"i.e. a-Si pays only below {24 * gain_per_h / (loss_per_h + gain_per_h) * 3600:.0f} s of full sun in a 24 h day (none if it is longer)")

# ---- what indoor power is worth against the load (context: the indoor numbers are tiny either way) ----
IDLE_MW = 105.0     # mW, controller awake with radio idle (SRC dev-board measurement, power_budget.py)
BATT_MWH = 0.5 * 3.7 * 1000   # 500 mAh at 3.7 V (ASM, power_budget.py)
for name, ind in (("200 lux CFL", INDOOR_200), ("500 lux LED", INDOOR_500)):
    for lab, d in (("all mono", ind[0]), ("all a-Si", ind[1])):
        p = FACE * d
        print(f"  indoors {name}, one face {lab}: {p:.2f} mW = {p / IDLE_MW * 100:.2f}% of the idle load, {p * 24 / BATT_MWH * 100:.2f}% of the battery per day")
m, a = outdoor()
print(f"  full sun, one face all mono: {FACE * m / 1000:.2f} W; all a-Si: {FACE * a / 1000:.2f} W")
print(f"\nOne cell is about {CELL:.1f} cm2, so each a-Si cell swapped in takes {CELL * (m - a) / 1000:.2f} W from the full-sun output and adds "
      f"{CELL * (INDOOR_200[1] - INDOOR_200[0]) * 1000:.1f} to {CELL * (INDOOR_500[1] - INDOOR_500[0]) * 1000:.1f} uW indoors.")
