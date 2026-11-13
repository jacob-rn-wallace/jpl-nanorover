"""Power: what the cells can supply against what the rover uses, in sun, overcast and indoors.

Run: python3 hardware/body/power_budget.py   (no CAD needed). SRC = a cited source (docs/body-redesign.md), ASM = my assumption.
The answer to "can the panels charge the rover or run a subsystem" depends mostly on the light, so every combination is printed.
"""
# ---- cell area (cm2), from the layout target (docs/photo-measurements.md: black unit's top face) ----
LARGE = 39.6 * 23.5 / 100          # cm2, 10 of them per top or bottom face (5 + 5 columns, SRC: photo measurement)
CENTRE = 19.6 * 44.0 / 100         # cm2, 4 of them (SRC: photo measurement, plus or minus 2 mm)
FACE_TB = 10 * LARGE + 4 * CENTRE  # one top or bottom face
FACE_END = 3 * 23.5 * 39.6 / 100   # one end face: 3 cells standing in the 80 x 60 mm left beside the 60 x 60 mm window or antenna square (my layout)
CELLS_CM2 = {"top": FACE_TB, "bottom": FACE_TB, "front": FACE_END, "back": FACE_END}
print("cell area per face (cm2):", {k: round(v, 1) for k, v in CELLS_CM2.items()}, f"; total {sum(CELLS_CM2.values()):.0f} cm2")

# ---- what one lit face can deliver (W) ----
SUN = 0.100          # W/cm2, 1000 W/m2 AM1.5 (SRC: 100 klux = 1000 W/m2)
ETA = (0.15, 0.20, 0.24)   # ASM: cheap cells, good monocrystalline, high-efficiency; no cell chosen
print("\nupward face, power in watts (cell efficiency 15 / 20 / 24 %):")
rows = [("full sun, panel square to it", SUN, 1.0), ("full sun, sun 45 deg off the normal", SUN, 0.707),
        ("thin overcast (about 10% of sun, ASM)", 0.1 * SUN, 1.0)]
solar = {}
for n, i, c in rows:
    p = [FACE_TB * i * e * c for e in ETA]
    solar[n] = p[1]
    print(f"  {n:42s} " + "  ".join(f"{v:6.2f} W" for v in p))
# indoors: measured output densities at 500 lux LED (SRC: about 8 uW/cm2 polycrystalline Si, 10 uW/cm2 amorphous Si; this is OUTPUT, not irradiance)
for n, d in (("indoors, 500 lux LED, poly-Si (8 uW/cm2)", 8e-6), ("indoors, 500 lux LED, a-Si (10 uW/cm2)", 10e-6)):
    p = FACE_TB * d
    solar[n] = p
    print(f"  {n:42s} {p * 1000:6.2f} mW")

# ---- loads (W) ----
V_SERVO = 12.0
loads = {
    "keep-alive: MCU deep sleep + RTC + wake input (ASM 0.1 mW; the chip alone is 7-8 uA, SRC)": 0.0001,
    "controller awake + radio receiving (PIC32MX250F128B about 0.5 mA/MHz x 40 MHz = 20 mA, a family-datasheet summary scaled by me, ASM; XBee 3 802.15.4 receive 15 mA, Digi page; both at 3.3 V)": (0.020 + 0.015) * 3.3,
    "radio transmitting, ABOVE the receiving figure (XBee 3 802.15.4 non-PRO 40 mA at +8 dBm, a manual snippet via distributors, less the 15 mA already counted; at 3.3 V)": (0.040 - 0.015) * 3.3,
    "camera streaming (ASM 0.3 W)": 0.3,
    "lamp on, through the 50/50 beamsplitter (ASM 0.2 W)": 0.2,
    "one servo moving at no load (180 mA at 12 V, SRC)": 0.180 * V_SERVO,
    "one servo holding or standby (6 mA datasheet to 60 mA other listings, at 12 V, SRC; sources disagree)": 0.030 * V_SERVO,
    "four wheel motors driving flat at 40 mm/s (ASM: about 0.1 W each; no-load 0.15 A at 6 V, SRC)": 0.4,
    "ranging sensor VL53L5CX ranging continuously (SRC: DS13754 rev 2 table 13, 313 mW at 3.3 V; 11 mW at 8x8 1 Hz autonomous)": 0.313,
}
print("\nloads (W):")
for n, w in loads.items():
    print(f"  {w:7.4f}  {n}")
L = list(loads.values())
scen = {
    "A keep-alive (RTC, wake input)":                         L[0],
    "B controller + radio idle":                              L[1],
    "C camera + radio streaming + lamp + ranging":            L[1] + L[2] + L[3] + L[4] + L[8],
    "D driving: wheels + controller + radio + camera + ranging, servos holding": L[7] + L[1] + L[2] + L[3] + L[8] + 4 * L[6],
    "E posing one strut: 1 servo moving, 3 holding, + C":     L[5] + 3 * L[6] + L[1] + L[2] + L[3] + L[4] + L[8],
}
print("\nscenarios (W), the servos holding at 30 mA each (the 6 mA and 60 mA cases move D and E by -0.3 and +0.7 W):")
for n, w in scen.items():
    print(f"  {w:7.3f} W  {n}")

print("\nsurplus of one lit face over each scenario (W; negative = the panel cannot carry it):")
print(f"  {'':44s}" + "".join(f"{s[0]:>9s}" for s in scen))
for n, p in solar.items():
    print(f"  {n:44s}" + "".join(f"{p - w:9.3f}" for w in scen.values()))

# ---- battery ----
BATT_WH = 1.0 * 3.7           # a 1000 mAh single cell, 3.7 V (Overlander SKU 2809 class, docs/hardware-spec.md section 4)
print(f"\nbattery {BATT_WH:.2f} Wh (1000 mAh at 3.7 V; about 28.5 g): runtime on D {BATT_WH / scen['D driving: wheels + controller + radio + camera + ranging, servos holding'] * 60:.0f} min, on C {BATT_WH / scen['C camera + radio streaming + lamp + ranging'] * 60:.0f} min, "
      f"on B {BATT_WH / scen['B controller + radio idle']:.0f} h")
ind = solar["indoors, 500 lux LED, a-Si (10 uW/cm2)"]
print(f"indoors the lit face gives {ind * 1000:.2f} mW: that is {ind / scen['B controller + radio idle'] * 100:.1f}% of scenario B and {ind * 24:.3f} Wh a day ({ind * 24 / BATT_WH * 100:.1f}% of the battery).")
sun = solar["full sun, panel square to it"]
print(f"in full sun it gives {sun:.2f} W: scenario C runs from the panel ({sun - scen['C camera + radio streaming + lamp + ranging']:+.2f} W) and the battery charges at about {max(sun - scen['B controller + radio idle'], 0):.1f} W when idle, "
      f"so about {BATT_WH / max(sun - scen['B controller + radio idle'], 1e-9) * 60:.0f} min from empty.")
