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
