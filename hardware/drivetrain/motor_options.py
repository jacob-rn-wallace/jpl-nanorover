"""Motor options by cost: the maxon choice against hobby-grade parts, checked against the same loads.  Pure Python.

    python3 hardware/drivetrain/motor_options.py

Loads (1.0 kg, 70 mm struts, 65 mm wheels; torque_budget.py): strut hold 0.156 N.m at the 25 degree stance (0.17 arms horizontal), one-pair push 0.34 N.m,
both without margin; wheel 0.027 N.m for a 20 degree slope, 0.138 N.m for a half-radius step.  Design margin x2 on the struts.

Sources (read 2026-11-11):
  maxon          catalogue 2025/26 pages 279, 417, 199, 373; PRICE: owner, from maxon's website, "over $200 each" (not checked by me)
  Feetech ST3215 waveshare.com/st3215-servo.htm (12 V: 30 kg.cm locked rotor, 2.7 A, kt 11 kg.cm/A; 7.4 V: 19.5 kg.cm, 2.5 A, kt 7.8; 360 degrees, 12-bit magnetic
                 encoder, continuous mode, serial bus, price range $16.99 to $21.99 on that page); servodatabase.com (55 g, 45.2 x 24.7 x 35 mm, metal gears 345:1);
                 mass 69 g from a Waveshare listing in a search snippet.  Other sellers list $26 to $49.  The "rated" 10 kg.cm at 12 V is a retailer table, unchecked.
  Pololu #3068   pololu.com/product/3068/specs and /faqs: 10 x 12 x 25 mm (plus a 10 mm shaft), 9.5 g, 249:1, 130 rpm at 6 V, 0.15 A no load, stall 3.2 kg.cm and 1.5 A
                 (theoretical), best efficiency 0.66 kg.cm at 100 rpm (29 %), $26.45 each (1 unit); FAQ: keep continuous loads at about 25 % of stall or less
  Pololu #3046   pololu.com/product/3046/specs: 10 x 12 x 28.5 mm (page also says 29.5 mm plus a 10 mm shaft), 10.5 g, 986:1, 35 rpm at 12 V, stall 10 kg.cm
                 (theoretical), best efficiency 2.1 kg.cm at 27 rpm, 0.19 A (25 %), $37.95 each (1 unit)
ASSUMED: servo winding resistance from 12 V / 2.7 A; no controllers, drivers, bus adapters or wiring are priced.
"""
KGCM = 0.0980665            # N.m per kg.cm
HOLD, PUSH = 0.156, 0.343   # strut loads, N.m, no margin
SLOPE, STEP = 0.027, 0.138  # wheel loads, N.m, no margin


def servo_hold_loss(torque, kt_kgcm_per_A, stall_A, volts):
    """Copper loss while holding: I = T / kt, R = V / I_stall, P = I^2 R (W)."""
    i = torque / (kt_kgcm_per_A * KGCM)
    r = volts / stall_A
    return i, i * i * r


def main():
    print("== Struts ==")
    print(f"{'option':44s} {'mass':>5s} {'price each':>11s} {'peak':>7s} {'rated':>7s}  push margin  hold loss/strut")
    rows = [
        ("maxon EC-max 16 5 W + GP 16 C 1621:1", 73, "> $200 (owner)", 0.90, 0.60, 0.03),
        ("Feetech ST3215, 12 V", 69, "$17 to $28", 30 * KGCM, 10 * KGCM, None),
        ("Feetech ST3215, 7.4 V version", 69, "$17 to $28", 19.5 * KGCM, 6.5 * KGCM, None),
    ]
    for name, m, price, peak, rated, loss in rows:
        if loss is None:
            v, ist, kt = (12, 2.7, 11) if "12 V" in name else (7.4, 2.5, 7.8)
            i, loss = servo_hold_loss(HOLD, kt, ist, v)
        print(f"{name:44s} {m:4d}g {price:>11s} {peak:6.2f} {rated:7.2f}  {peak / PUSH:5.1f} x peak, {rated / PUSH:4.1f} x rated   {loss:5.2f} W at the 25 deg stance")
    print("(peak = intermittent / locked rotor; rated = continuous; margins are against the 0.34 N.m push with no design margin)\n")

    print("== Wheels (Pololu micro metal gearmotors; FAQ guideline: continuous load about 25 % of stall or less) ==")
    # (name, mass g, price, no-load rpm, stall kg.cm, V)
    wheel_motors = [("Pololu #3046 1000:1 HPCB 12 V", 10.5, 37.95, 35, 10.0, 12), ("Pololu #3068  250:1 HPCB  6 V", 9.5, 26.45, 130, 3.2, 6)]
    loads = ((SLOPE, "20 deg slope"), (2 * SLOPE, "slope, margin x2"), (0.1, "0.1 N.m design"), (STEP, "half-radius step"))
    for name, m, price, n0, st, v in wheel_motors:
        stall = st * KGCM
        print(f"{name}: {m} g, ${price}, stall {stall:.3f} N.m, 25 % guideline {0.25 * stall:.3f} N.m")
        for load, what in loads:
            frac = load / stall
            rpm_full = n0 * (1 - frac)
            duty = (12 / n0 + frac)           # fraction of full voltage that gives 12 rpm (about 40 mm/s) at this load
            print(f"   {what:18s} {load:5.3f} N.m = {100 * frac:3.0f} % of stall: {'ok ' if frac <= 0.25 else 'OVER'} "
                  f"{rpm_full:5.1f} rpm at full voltage; 12 rpm needs about {100 * duty:3.0f} % duty")
    print("  realistic continuous load on a table is far lower: rolling resistance about 0.03 to 0.05 x 2.45 N x 32.5 mm = 0.002 to 0.004 N.m\n")

    print("== Drivetrain mass and cost (struts 22 g x4, thin wheels 34 g x4) ==")
    for name, strut_g, wheel_g, cost in (
            ("maxon strut + maxon wheel motors (now)", 4 * 73, 4 * 20.2, ">= 8 x $200 = $1600+ (owner)"),
            ("Feetech ST3215 struts + Pololu #3046 wheels", 4 * 69, 4 * 10.5, "4 x $17-28 + 4 x $37.95 = $220 to $264"),
            ("Feetech ST3215 struts + Pololu #3068 wheels", 4 * 69, 4 * 9.5, "4 x $17-28 + 4 x $26.45 = $174 to $218")):
        total = 4 * 22 + 4 * 34 + strut_g + wheel_g
        print(f"{name:48s} {total:4.0f} g drivetrain, {1000 - total:4.0f} g left of 1 kg, {cost}")
    print("(controllers, drivers, a servo bus adapter and wiring are not priced)")


if __name__ == "__main__":
    main()
