"""Estimate of the lid spring contacts' voltage drop, heating and loss on the power paths, and the contact counts that follow.   (plain python3; an ESTIMATE, not a measurement)

Run: python3 hardware/body/contact_estimate.py
Method of 2026-11-14 (CLAUDE.md): no bench test, so bound it by arithmetic. Inputs (ASM unless SRC):
  contact resistance per spring contact incl. its pad: 10 to 40 mOhm new (a typical figure for gold-plated spring contacts, remembered, to confirm in the datasheet), times 2.5 when aged (wear, dust,
  oxide: the lids come off for service) -> 10 to 100 mOhm over the contact's life;
  pack side peak current 3.5 A at 3.0 V cell voltage (SRC: hardware-spec section 3: 7.4 V x 1.2 A with 85% efficiency); 7.4 V rail: 1.2 A design, 2.0 A worst (ASM, with the wheels in use);
  rating per contact: 2 A continuous (the ultra-low-profile Mill-Max 815/817 series, search listing; the 0.050 in series quotes 7 A at a 30 C rise: both to confirm).
Criteria I set: total path drop at most 3% of the node voltage, at most 1 A per contact, at most 50 mW per contact.
"""
R_LO, R_HI = 0.010, 0.100          # ohm per contact over life
CRIT_DROP, CRIT_I, CRIT_W = 0.03, 1.0, 0.050
paths = [
    # name, current A, node volts, (contacts forward, contacts return), current counts: contacts per side
    ("battery to power board (VBAT out and back)", 3.5, 3.0),
    ("7.4 V rail out of the power board", 2.0, 7.4),
    ("7.4 V rail into the wheel drivers (lower lid)", 2.0, 7.4),
    ("VBAT into the 3.3 V converter (lower lid)", 0.3, 3.0),
]
print(f"{'path':46s} {'I':>4s} {'n':>2s} | drop mV (new to aged, out+back) | % of node | A/contact | W/contact aged")
rec = {}
for name, i, v in paths:
    for n in (2, 3, 4, 6):
        lo = 2 * i * R_LO / n; hi = 2 * i * R_HI / n               # out and back, the same count both ways
        ic = i / n; w = ic ** 2 * R_HI
        ok = hi / v <= CRIT_DROP and ic <= CRIT_I and w <= CRIT_W
        print(f"{name:46s} {i:4.1f} {n:2d} | {lo * 1000:6.0f} to {hi * 1000:5.0f}               | {hi / v * 100:4.1f}%   | {ic:5.2f}     | {w * 1000:5.0f} {'  ok' if ok else ''}")
        if ok and name not in rec:
            rec[name] = n
    if name not in rec:
        rec[name] = 6
print("\ncontacts per net (smallest count that meets all three criteria at the aged resistance):")
for k, v in rec.items():
    print(f"  {k}: {v} (forward) and {v} (return)")
print("\nREADING: at 2 contacts the battery path would drop up to 0.35 V of a 3.0 V cell (12%) and each contact would carry 1.75 A and dissipate 0.3 W when aged: not acceptable. Use the counts above.")
print("A cheaper way to cut the problem: the battery's leads go to the power board through its own pocket only (as now); do NOT route the pack current through two pockets. To be measured: contact resistance new and after")
print("20 lid cycles (milliohm meter, four-wire), and the temperature rise at 2 A.")
