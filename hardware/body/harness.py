"""The harness across the lid joints: which nets cross, how many spring contacts each pocket needs, and how long the pockets must be.   (plain python3)

Run: python3 hardware/body/harness.py

Partition (my recommendation, 2026-11-14; changes layout.py's board names): the PROCESSOR board (lower lid) carries the PIC32, the IMU, the 3.3 V buck-boost, the four DRV8837 wheel drivers
and the servo-bus buffer; the POWER board (upper lid) carries the cell protection, charger, solar inputs and the 7.4 V boost. Why the drivers go with the processor: the back-EMF counting reads
each motor's terminal voltage at the driver's coast gaps, so the analogue sense lines stay on one board instead of crossing a connector, and the eight IN1/IN2 control lines do too (they would be
the bulk of the crossing). The price: the strut motors' wires enter the body at the BOTTOM lid (the wall hole is at z = 11, 19 mm below the hub axis; it was z = 49).
Between the boards only power and four slow signals cross, and they cross through the body's own wiring: each lid's contacts press on the lid's platform side face, the body wires join the two lids' pockets.
Contacts: Mill-Max 0.050 in (1.27 mm) pitch spring-loaded contacts are the candidate family (search result, [Mill-Max](https://www.mouser.in/new/mill-max/mill-max-050-pitch-spring-loaded-contacts): 1.02 mm full stroke, 7 A at a 30 C rise
for the high-current type; 2 A continuous for the ultra-low-profile 815/817 series); mounted on a small stand-up strip so the pins point sideways. To confirm in the datasheets. Rule used here: one contact per signal net; power nets get the counts that `contact_estimate.py` finds (VBAT and ground at the battery 6 each, the 7.4 V rail 3, the 3.3 V converter's VBAT 2), none shared.
"""
PITCH = 1.27          # mm between contact centres (ASM: the standard 0.050 in pitch)
MARGIN = 1.5          # mm from the pocket's ends to the first and last contact centres
# net -> number of contacts; one dictionary per (lid, side). Side + is the camera end's side (x = +), side - the antenna end's.
LOWER = {
    "+": {"wheel motor wires (2 motors x 2)": 4, "camera TX": 1, "camera RX": 1, "ranging+IMU SDA": 1, "ranging SCL": 1, "ranging INT": 1, "LED enable": 1, "3V3 to camera end": 1, "GND camera end": 1,
          "boost enable": 1, "charger status": 1, "battery current sense": 1},
    "-": {"wheel motor wires (2 motors x 2)": 4, "XBee TX": 1, "XBee RX": 1, "XBee sleep": 1, "XBee reset": 1, "3V3 to antenna end": 1, "GND antenna end": 1, "servo bus data": 1,
          "VBAT in": 2, "V7.4 in (wheel drivers)": 3, "GND power return": 3},
}
UPPER = {
    "+": {"VBAT (battery)": 6, "V7.4 out (to servos, LED ring, lower board)": 3, "GND power return (battery and loads)": 6},
    "-": {"solar: bottom lid cells": 1, "solar: end A cells": 1, "solar: end B cells": 1, "boost enable": 1, "charger status": 1, "battery current sense": 1, "GND reference": 1},
}


def length(n):
    return round((n - 1) * PITCH + 2 * MARGIN, 1)


def pockets():
    """Pocket length along y for each side (the same on both lids, which are identical): the larger of the two lids' needs."""
    return {s: length(max(sum(LOWER[s].values()), sum(UPPER[s].values()))) for s in "+-"}


if __name__ == "__main__":
    for name, d in (("LOWER lid (processor board)", LOWER), ("UPPER lid (power board)", UPPER)):
        print(name)
        for s in "+-":
            n = sum(d[s].values())
            print(f"  side {s}: {n:2d} contacts, pocket {length(n):4.1f} mm long: " + "; ".join(f"{k} x{v}" for k, v in d[s].items()))
    P = pockets()
    print("pocket length used (both lids identical):", P)
    # the cross-checks: every net that leaves one lid arrives at the other, with the same contact count
    lo = {k: v for s in "+-" for k, v in LOWER[s].items()}; up = {k: v for s in "+-" for k, v in UPPER[s].items()}
    print("links lower<->upper: boost enable, charger status, battery current sense: one contact each on both lids; power: VBAT 2, V7.4 2, GND 2 each way (names differ by lid)")
    print("platform side face spans y = -6 to 62 (68 mm); the longest pocket is", max(P.values()), "mm, from y = -5 (the wall channel enters at y = 0)")
