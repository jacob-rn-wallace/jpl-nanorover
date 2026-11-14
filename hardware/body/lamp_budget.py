"""The LED ring's light on the subject: how bright is a still photograph? (docs/hardware-spec.md, section 5)

Run: python3 hardware/body/lamp_budget.py   (plain python). SRC = a cited source, ASM = my assumption.
Six mid-power white LEDs (Samsung LM281B+ Pro class: about 36 lm at 65 mA and 2.7 V, from a distributor listing and Samsung's product table), in three series pairs on the
7.4 V rail with a resistor each, behind a smoked dead-front film. The light is taken as Lambertian (on-axis intensity = flux / pi), a fair guess for a flat-lens LED
behind a film (ASM). Illuminance on a surface facing the rover at distance d: E = I / d^2.
"""
import math
V_RAIL, V_LED, N_PER_STRING, STRINGS = 7.4, 2.7, 2, 3     # V; V per LED at 65 mA (SRC listing, lower at lower current: ASM); LEDs per string; strings
LM_65, I_65 = 36.0, 0.065                                  # lm and A (SRC)
print("per LED drive | rail power | LED power | flux before film | out of film at 20% | intensity | lux at 0.3 m | 0.5 m | 1 m")
for i_ma in (10, 20, 25, 40, 65):
    i = i_ma / 1000
    flux_led = LM_65 * (i / I_65) ** 0.9                   # slight efficacy droop at high current is ignored; below 65 mA the flux falls a little slower than the current (ASM exponent)
    p_rail = V_RAIL * i * STRINGS
    p_led = V_LED * i * N_PER_STRING * STRINGS
    flux = flux_led * N_PER_STRING * STRINGS
    out = flux * 0.20
    inten = out / math.pi
    print(f"{i_ma:4d} mA       | {p_rail:6.2f} W   | {p_led:6.2f} W | {flux:6.0f} lm        | {out:6.1f} lm           | {inten:5.1f} cd | {inten / 0.09:6.0f}      | {inten / 0.25:4.0f}  | {inten / 1:4.1f}")
print("\ncontext (ASM, typical figures): a dim living room is 50 lux, a bright room 300 lux, a phone flash gives about 50 to 100 lux at 0.3 m.")
print("choice: 25 mA per LED (0.56 W from the 7.4 V rail for about 1 s a photograph): about 65 lux at 0.3 m, 23 at 0.5 m, 6 at 1 m. The lamp is a close-range fill, not a floodlight.")
print("resistor per pair at 25 mA: (7.4 - 2 x 2.7) / 0.025 = 80 ohm; the rail is regulated (TPS61288), so the current follows the LEDs' forward voltage: +-0.4 V on a pair (+-0.2 V each) over 80 ohm is +-5 mA, 20% of the current.")

# ---- the ring's driver (2026-11-14): three series pairs, one resistor each, all switched by one low-side logic-level N-MOSFET (BSS138 class) on a plain GPIO; gate pull-down 100 k ----
print("\nDRIVER: current per string over the spread (resistor 75 ohm 1%, MOSFET drop 0.15 to 0.25 V for the three strings' 75 mA, rail 7.4 V +-3%)")
R = 75.0
for vf_name, vf in (("low Vf 2.50 V (hot-and-bright end, ASM)", 2.50), ("typical 2.65 V (ASM: the listing's 2.7 V is at 65 mA, lower at 25 mA)", 2.65), ("high Vf 2.85 V (ASM)", 2.85)):
    lo = (7.4 * 0.97 - 0.25 - 2 * vf) / (R * 1.01); hi = (7.4 * 1.03 - 0.15 - 2 * vf) / (R * 0.99)
    print(f"  {vf_name}: {lo * 1000:5.1f} to {hi * 1000:5.1f} mA per LED; dissipation in the resistor up to {(hi ** 2 * R) * 1000:4.0f} mW (0603 is 100 mW)")
print("  worst case over all: see the lowest and highest figures above; the datasheet's absolute maximum was not readable (its tables are images in the copy I got), the listings say 200 to 300 mA, so 25 mA is far inside it.")
print("  total on time: the firmware limits one lamp-on to 3 s and 10 s between (thermal: 0.56 W for 3 s is 1.7 J into a 4 g board; ASM: a few kelvin).")
