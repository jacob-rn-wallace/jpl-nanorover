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

# ---- DATASHEET FIGURES (2026-11-14; replaces the listing figures above) -----------------------------------------------------------------------------------------
# SRC: Samsung LM281B+ Pro family data sheet Rev 0.8 (private repo, datasheets/): pages 3, 4, 5, 6, 23. SRC: onsemi BSS138/D Rev 3: page 2 and its RDS(on) curve.
# Part: SPMWH1228MD5WAR0VK = 2835 (2.8 x 3.5 x 0.7 mm), sorted at 65 mA, ANSI chromaticity, CRI >= 80, voltage rank WA (2.6 to 3.0 V at 65 mA), 5000 K whole bin, flux bin VK
#       (35.5 to 37.5 lm at 65 mA; +-5% flux and +-0.1 V measurement tolerance). Absolute maximum: 200 mA continuous, 300 mA pulsed (1/10 duty, 10 ms), Tj 115 C, Rth(j-solder) 15 C/W;
#       the note recommends at least 10 mA "to avoid uneven brightness". Rank WN (2.6 to 2.8 V) is the narrower voltage option, same code with WN in digits 13-14.
# The Vf-vs-current curve (page 23, read by eye, +-0.01 V): about 2.72 V at 65 mA and 2.63 V at 25 mA, so Vf(25 mA) = Vf(65 mA) - 0.09 V (a typical-bin curve; applied to every bin: ASM).
# BSS138: VGS(th) 0.8 / 1.3 / 1.5 V; RDS(on) 0.7 typ / 3.5 max at 10 V, 1.0 typ / 6.0 max at 4.5 V (ID 0.22 A); NOT TABULATED at 3.3 V. ESTIMATE from the normalised curve
#       (3.3 V is about 1.4 x the 4.5 V value): typ 1.4, max 8.4 ohm; x1.2 for the part's own heating (max 10 ohm). PD 0.36 W, 350 C/W on a minimum pad.
print("\nDATASHEET DRIVER CHECK: three strings share the MOSFET, so I = (Vrail - 2 Vf) / (R + 3 RDS(on))")
R_NOM, TOL = 75.0, 0.01
for rank, (v_lo, v_hi) in (("WA 2.6-3.0 V", (2.6, 3.0)), ("WN 2.6-2.8 V", (2.6, 2.8))):
    # Vf at 25 mA over the bin and the +-0.1 V measurement tolerance (extreme, ASM: both at once)
    vf_lo, vf_hi = v_lo - 0.09 - 0.1, v_hi - 0.09 + 0.1
    lo = (7.4 * 0.97 - 2 * vf_hi) / (R_NOM * (1 + TOL) + 3 * 10.0)       # high Vf, low rail, worst RDS(on)
    hi = (7.4 * 1.03 - 2 * vf_lo) / (R_NOM * (1 - TOL) + 3 * 1.0)         # low Vf, high rail, best RDS(on) (typ 1.4 x 0.7, ASM)
    print(f"  rank {rank}: Vf at 25 mA {vf_lo:.2f} to {vf_hi:.2f} V (with tolerance): {lo * 1000:4.1f} to {hi * 1000:4.1f} mA per LED "
          f"(datasheet minimum 10 mA, maximum 200 mA)")
i = 0.025
print(f"  at the typical 25 mA: Vf 2.63 V, MOSFET drop {3 * i * 1.4:4.2f} V typ and {3 * i * 10.0:4.2f} V at the worst RDS(on) (10 ohm); LED dissipation {2.63 * i * 1000:3.0f} mW, junction rise {2.63 * i * 15:3.1f} C over the solder point")
print("  MOSFET dissipation at 99 mA total and 10 ohm: %.0f mW against 360 mW (350 C/W: %.0f C over ambient)" % (0.099 ** 2 * 10 * 1000, 0.099 ** 2 * 10 * 350))
print("  conclusion: the earlier 0.15 to 0.25 V MOSFET drop was optimistic (0.75 V at 25 mA per LED and the worst RDS(on)), but the drop LOWERS the current, so every case stays between the 10 mA minimum and the 200 mA maximum; the lamp is dimmer at the low end, not unsafe.")
print("  luminous flux at 25 mA: flux scales about linearly with current (page 23), 25/65 x 36.5 lm = %.1f lm per LED (bin VK, +-5%%), %.0f lm for six before the film (the earlier 0.9 exponent gave 15.3 lm: the lux figures above are about 8%% high on the linear reading, ASM)." % (25 / 65 * 36.5, 6 * 25 / 65 * 36.5))
