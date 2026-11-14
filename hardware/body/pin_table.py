#!/usr/bin/env python3
"""PIC32MX250F128D (44-pin TQFP) pin allocation, solved against the datasheet tables.

Source: Microchip DS60001168K (private repo, datasheets/): Table 12 (44-pin TQFP pin names),
Table 11-1 (input pin select), Table 11-2 (output pin select), Table 1-1 (fixed functions).
Plain python3; no dependencies.  Run:  python3 hardware/body/pin_table.py

Findings it prints:
  * the package has 33 I/O pins (no RB6 on 44-pin parts), 31 after the ICSP pair;
  * which configurations (UART roles, I2C port, camera link, crystal or not) have a perfect
    assignment, and the one recommended.
Not checked here: 5 V tolerance (shading is not in the PDF text), pin electrical limits.
"""
import itertools

# ---- package (Table 12): pin number -> port name -------------------------------------------------
PIN = {1: "RB9", 2: "RC6", 3: "RC7", 4: "RC8", 5: "RC9", 8: "RB10", 9: "RB11", 11: "RB13", 12: "RA10",
       13: "RA7", 14: "RB14", 15: "RB15", 19: "RA0", 20: "RA1", 21: "RB0", 22: "RB1", 23: "RB2",
       24: "RB3", 25: "RC0", 26: "RC1", 27: "RC2", 30: "RA2", 31: "RA3", 32: "RA8", 33: "RB4",
       34: "RA4", 35: "RA9", 36: "RC3", 37: "RC4", 38: "RC5", 41: "RB5", 43: "RB7", 44: "RB8"}
NUM = {v: k for k, v in PIN.items()}
IO = set(PIN.values())  # 33 pins

# ---- peripheral pin select, outputs (Table 11-2): groups of pins sharing functions --------------
G1 = ["RA0", "RB3", "RB4", "RB15", "RB7", "RC7", "RC0", "RC5"]   # U1TX, U2RTS, SS1, OC1
G2 = ["RA1", "RB5", "RB1", "RB11", "RB8", "RA8", "RC8", "RA9"]   # SDO1, SDO2, OC2
G3 = ["RA3", "RB14", "RB0", "RB10", "RB9", "RC9", "RC2", "RC4"]  # U1RTS, U2TX, SS2, OC3
G4 = ["RA2", "RB6", "RA4", "RB13", "RB2", "RC6", "RC1", "RC3"]   # SDO1, SDO2, OC4, OC5
G = [[p for p in g if p in IO] for g in (G1, G2, G3, G4)]        # RB6 is not on the 44-pin package
# inputs (Table 11-1): the same four groups of pins; U1RX, SDI2 on G4's pins; U2RX, SDI1 on G2's.
# fixed functions (Table 12): SCK1 RB14, SCK2 RB15, SDA1 RB9, SCL1 RB8, SDA2 RB2, SCL2 RB3
ADC = {"RA0": 0, "RA1": 1, "RB0": 2, "RB1": 3, "RB2": 4, "RB3": 5, "RC0": 6, "RC1": 7, "RC2": 8,
       "RB15": 9, "RB14": 10, "RB13": 11, "RC3": 12}
ICSP = ["RA10", "RA7"]   # PGED4/PGEC4 (TMS/TCK): no other function on these two pins, so reserve them
OSC = ["RA2", "RA3"]     # lost if a crystal is used (the internal FRC frees them)

UART = {  # tx pins (output group), rx pins (input group)
    1: (G[0], G[3]),
    2: (G[2], G[1]),
}
SPI = {  # sck fixed, mosi (SDO), miso (SDI)
    1: (["RB14"], sorted(set(G[1]) | set(G[3])), G[1]),
    2: (["RB15"], sorted(set(G[1]) | set(G[3])), G[3]),
}
I2C = {1: ["RB8", "RB9"], 2: ["RB2", "RB3"]}


def match(sigs, blocked):
    """sigs: {name: candidate pins}. Bipartite matching; returns {name: pin} or None."""
    owner = {}

    def try_(s, seen):
        for p in sigs[s]:
            if p in blocked or p in seen:
                continue
            seen.add(p)
            if p not in owner or try_(owner[p], seen):
                owner[p] = s
                return True
        return False

    for s in sigs:
        if not try_(s, set()):
            return None
    return {s: p for p, s in owner.items()}


def build(xbee_uart, i2c_port, camera, crystal, with_reset, with_int):
    sigs, blocked = {}, set(ICSP) | (set(OSC) if crystal else set())
    sv_uart = 2 if xbee_uart == 1 else 1
    sigs["xbee_tx"], sigs["xbee_rx"] = UART[xbee_uart]
    sigs["servo_tx"], sigs["servo_rx"] = UART[sv_uart]
    for i, g in enumerate(G):                    # motor i on OC(i+1): both drive pins from its group
        sigs[f"motor{i+1}_in1"] = g
        sigs[f"motor{i+1}_in2"] = g
    for pin, name in zip(I2C[i2c_port], ("scl", "sda")):
        sigs[f"i2c_{name}"] = [pin]
    if camera in (1, 2):                          # SPI camera
        sck, mosi, miso = SPI[camera]
        sigs["cam_sck"], sigs["cam_mosi"], sigs["cam_miso"] = sck, mosi, miso
        sigs["cam_cs"] = sorted(IO)
    else:                                         # UART camera: needs a third UART, a bit-bang pair
        sigs["cam_tx"] = sorted(IO)
        sigs["cam_rx"] = sorted(IO)
    for n in ("bemf1", "bemf2", "bemf3", "bemf4", "vbat", "ibat"):
        sigs[n] = sorted(ADC)
    # the wheel drivers' nSLEEP is tied to the boost enable (they run from the 7.4 V rail it switches)
    gpio = ["xbee_sleep", "servo_dir", "led_en", "boost_en", "chg_status"]
    if with_reset:
        gpio.append("xbee_reset")
    gpio += {"both": ["rng_int", "imu_int"], "rng": ["rng_int"], "none": []}[with_int]
    for n in gpio:
        sigs[n] = sorted(IO)
    return sigs, blocked


def main():
    print(f"I/O pins on the 44-pin TQFP: {len(IO)} (RB6 is absent); ICSP pair reserved: {len(IO)-2} usable;"
          f" with a crystal: {len(IO)-4}\n")
    rows = []
    for xb, i2c, cam, xtal, rst, intr in itertools.product((1, 2), (1, 2), (1, 2, 0), (False, True),
                                                           (True, False), ("both", "rng", "none")):
        sigs, blocked = build(xb, i2c, cam, xtal, rst, intr)
        sol = match(sigs, blocked)
        rows.append((xb, i2c, cam, xtal, rst, intr, len(sigs), sol is not None))
    print("signals needed / feasible by option (camera 1,2 = SPI port, 0 = bit-banged UART):")
    for cam in (1, 2, 0):
        for xtal in (False, True):
            for rst, intr in ((True, "both"), (False, "both"), (False, "rng"), (True, "rng"), (False, "none")):
                ok = [r for r in rows if r[2] == cam and r[3] == xtal and r[4] == rst and r[5] == intr and r[7]]
                n = next(r[6] for r in rows if r[2] == cam and r[3] == xtal and r[4] == rst and r[5] == intr)
                print(f"  camera {cam}, {'crystal' if xtal else 'FRC    '}, xbee_reset={'y' if rst else 'n'},"
                      f" int lines={intr:4s}: {n} signals, feasible configs {len(ok)} of 8")
    # recommended: SPI camera, internal FRC, no XBee reset line, ranging interrupt only
    sol = None
    for rec in itertools.product((1, 2), (1, 2), (1, 2), (False,), (False,), ("rng",)):
        sigs, blocked = build(*rec)
        sol = match(sigs, blocked)
        if sol:
            break
    if not sol:
        print("\nno assignment for the recommended set")
        return
    print("\nOne full assignment (xbee on UART%d, I2C%d, SPI%d camera, FRC, no XBee reset, ranging INT only):" % rec[:3])
    for s_, p in sorted(sol.items(), key=lambda kv: NUM[kv[1]]):
        print(f"  pin {NUM[p]:2d} {p:5s} {s_}")
    free = sorted(IO - set(sol.values()) - set(ICSP), key=lambda p: NUM[p])
    print("  free:", ", ".join(f"{NUM[p]} {p}" for p in free) or "none")


if __name__ == "__main__":
    main()
