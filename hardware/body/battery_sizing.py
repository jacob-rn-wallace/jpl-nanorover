"""Battery sizing: what the rover draws at the worst moments, and which pack and rails follow.

Run: python3 hardware/body/battery_sizing.py   (plain python, no CAD). SRC = a cited figure, ASM = my assumption.
Replaces the placeholder's worry ("9 A at the battery"): that was the servo's locked-rotor current, not what the loads need.
"""
# ---- strut servo (Feetech STS3215, 12 V variant): SRC listings, docs/hardware-spec.md ----
V_RATED, I_STALL, T_STALL = 12.0, 2.7, 30 * 0.0980665      # V, A, N.m (30 kg.cm locked rotor)
R = V_RATED / I_STALL                                        # ohm, winding plus drive (ASM: stall current = V/R)
KT = T_STALL / I_STALL                                       # N.m per A at the output (ASM: linear, gearbox losses included)
print(f"servo: R = {R:.2f} ohm, output torque constant {KT:.2f} N.m/A; hold or push current = torque / {KT:.2f}")

# ---- strut loads, 1.0 kg Earth design mass, no margin (docs/drivetrain-spec.md, chassis simulation) ----
HOLD, PUSH = 0.172, 0.343        # N.m per strut: arms horizontal; whole weight on one pair (per strut of that pair)
W_MOVE = 10 * 2 * 3.14159 / 60   # rad/s while a strut moves under load (ASM: 10 rpm)

def servo_w(torque, omega, idle_a, v_supply):
    """Battery-side watts for one servo: winding loss + mechanical output + idle (ASM: idle current scales with the supply voltage)."""
    i = torque / KT
    return i * i * R + torque * omega + idle_a * v_supply

# ---- everything else (docs/body-redesign.md, power_budget.py): W ----
CTRL_RX, RADIO_TX_EXTRA = 0.1155, 0.0825
CAMERA, LAMP, WHEELS = 0.3, 0.2, 0.4       # ASM

def total(case, margin, idle_a, v_servo):
    base = CTRL_RX + RADIO_TX_EXTRA
    if case == "hold (driving)":      return base + CAMERA + WHEELS + 4 * servo_w(HOLD * margin, 0, idle_a, v_servo)
    if case == "pose one strut":      return base + CAMERA + servo_w(HOLD * margin, W_MOVE, idle_a, v_servo) + 3 * servo_w(HOLD * margin, 0, idle_a, v_servo)
    if case == "self-right (push)":   return base + 2 * servo_w(PUSH * margin, W_MOVE, idle_a, v_servo) + 2 * servo_w(HOLD * margin, 0, idle_a, v_servo)
    raise ValueError(case)

CASES = ["hold (driving)", "pose one strut", "self-right (push)"]
print("\nbattery-side load in watts, before converter loss (servos at 12 V, idle 6 / 30 / 60 mA):")
print(f"{'':20s}" + "".join(f"{f'x{m} idle {int(ia*1000)}mA':>18s}" for m in (1, 2) for ia in (0.006, 0.030, 0.060)))
for c in CASES:
    print(f"{c:20s}" + "".join(f"{total(c, m, ia, 12.0):18.2f}" for m in (1, 2) for ia in (0.006, 0.030, 0.060)))

# ---- options: pack, servo supply, charger ----
EFF = 0.85            # ASM: boost or buck converter efficiency
OPTS = [  # name, pack volts nominal / minimum, servo supply volts, mAh
    ("1S 500 mAh, servos on 12 V boost", 3.7, 3.0, 12.0, 500),
    ("1S 1000 mAh, servos on 12 V boost", 3.7, 3.0, 12.0, 1000),
    ("1S 1000 mAh, servos on 7.4 V boost", 3.7, 3.0, 7.4, 1000),
    ("2S 500 mAh, servos straight off the pack", 7.4, 6.0, 7.4, 500),
]
print("\npack options, worst realistic case (self-right at x2 margin, idle 30 mA), then driving hold at x1:")
print(f"{'option':44s}{'Wh':>6s}{'peak W':>8s}{'peak A':>8s}{'C-rate':>8s}{'hold W':>8s}{'hours':>7s}")
for name, vn, vmin, vs, mah in OPTS:
    wh = vn * mah / 1000
    conv = EFF if vs != vn else 0.95        # 2S straight to servos: only the other rails convert (ASM 0.95 overall)
    peak_w = total("self-right (push)", 2, 0.030, vs) / conv
    peak_a = peak_w / vmin
    hold_w = total("hold (driving)", 1, 0.030, vs) / conv
    print(f"{name:44s}{wh:6.2f}{peak_w:8.1f}{peak_a:8.2f}{peak_a / (mah / 1000):8.1f}{hold_w:8.2f}{wh / hold_w:7.2f}")

# ---- what fits in the battery bay (layout.py: x +-2.5 y +-15 z 18..42 as a placeholder; the gap between the servo pairs is wider) ----
ED = 400.0  # Wh/L, ASM: small Li-ion or LiPo pouch cells, volumetric, with their own wrap and tabs (memory, unchecked)
for label, dx in (("placeholder box 5 x 30 x 24 mm", 5.0), ("full 16 mm gap, 16 x 30 x 24 mm", 16.0)):
    v = dx * 30 * 24 / 1000
    print(f"bay {label}: {v:.1f} cm3 -> about {ED * v / 1000:.2f} Wh ({ED * v / 1000 / 3.7 * 1000:.0f} mAh at 3.7 V)")
