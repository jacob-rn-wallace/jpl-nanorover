#!/usr/bin/env python3
"""Planar quasi-static simulation of the four-strut chassis: stances, tipping margins, the torque each strut needs, and self-righting.

    .venv/bin/python hardware/drivetrain/chassis_sim.py [--figure PATH]

MODEL (everything here is an assumption or a simplification; see docs/chassis-simulation.md)
  * The two sides move together, so the rover is treated in the y-z plane (looking along the hub axis): a 140 x 60 mm body (y from -70 to 70, z from 0 to 60) with the hub
    at its centre (0, 30), and two struts A and B of 70 mm.  Angle phi is measured from +y, counter-clockwise in the y-z plane; the default stance is A at -25 degrees (down
    toward +y) and B at 205 degrees (down toward -y).  Wheels are circles of radius 32.5 mm at the strut tips.
  * The assembly of body, struts and wheels (struts locked) is one rigid shape.  It rests on the ground in the orientation that is a local minimum of its centre-of-mass height
    (the support is a body corner or a wheel, with the ground frictionless, so the forces are vertical).  After a strut moves the shape changes, and the assembly rolls
    downhill in centre-of-mass height from its old orientation to the nearest minimum (overdamped, no momentum).  A strut cannot pass the other strut: the wheels collide when the
    two struts are less than 60 degrees apart (strut.py found wheel contact up to about 55 degrees), so both arcs between them must stay at least 60 degrees.
  * Strut torque is what the servo must hold: the moment about the hub of the ground reaction on that strut's wheel plus the weight of the strut, wheel and wheel support,
    per strut (half the planar value, because two sides share the load).  Ground reactions for one or two support features follow from force and moment balance.
  * MASSES (1.0 kg, from the CAD and datasheets; the body lump is what is left of the 1 kg budget): body lump 386 g at the centre; servos 4 x 55 g at their positions in hub.py (servo B
    on the axis, long side toward +y; servo A offset 23 mm toward -y); hub parts 74 g near the hub; struts 94 g; wheels 133 g; wheel supports (motors, spindles, bearings) 93 g.
NOT covered: dynamics (momentum, impacts), friction, side-to-side tipping, steps and slopes (only a tip-over slope estimate), both struts moving at once.
"""
import argparse
import heapq
import math
import sys
from collections import deque

import numpy as np

G = 9.81
M_TOTAL = 1.0
STRUT_L, WHEEL_R = 0.070, 0.0325
HUB = np.array([0.0, 0.030])                # (y, z) in the body frame, m
BODY = [(-0.070, 0.0), (0.070, 0.0), (0.070, 0.060), (-0.070, 0.060)]
MIN_ARC = 60.0                              # degrees between the struts (wheels collide below this)

# mass lumps (kg), planar totals for both sides; the body lump is the part of the 1 kg budget left after everything else
M_SERVO, M_HUB, M_STRUT, M_WHEEL, M_SUPPORT = 4 * 0.055, 0.074, 0.094, 0.133, 0.093
M_BODY = M_TOTAL - (M_SERVO + M_HUB + M_STRUT + M_WHEEL + M_SUPPORT)
SERVO_B_Y, SERVO_A_Y = (-0.0107 + 0.03453) / 2.0, (-0.0575 - 0.0123) / 2.0   # body-frame y of the servo bodies' centres (hub.py)


def tip(phi_deg):
    p = math.radians(phi_deg)
    return HUB + STRUT_L * np.array([math.cos(p), math.sin(p)])


class Shape:
    """Rigid assembly for strut angles (phiA, phiB), degrees: features, masses, centre of mass in the body frame."""

    def __init__(self, phiA, phiB):
        self.phiA, self.phiB = phiA % 360.0, phiB % 360.0
        self.cA, self.cB = tip(phiA), tip(phiB)
        lumps = [(M_BODY, np.array([0.0, 0.030])), (M_HUB, np.array([-0.005, 0.030])),
                 (2 * 0.055, np.array([SERVO_B_Y, 0.030])), (2 * 0.055, np.array([SERVO_A_Y, 0.030]))]
        self.strut_m = {"A": M_STRUT / 2 + M_WHEEL / 2 + M_SUPPORT / 2, "B": M_STRUT / 2 + M_WHEEL / 2 + M_SUPPORT / 2}
        self.parts = {}
        for name, c in (("A", self.cA), ("B", self.cB)):
            mid = HUB + 0.5 * (c - HUB)
            parts = [(M_STRUT / 2, mid), (M_WHEEL / 2, c), (M_SUPPORT / 2, c)]
            self.parts[name] = parts
            lumps += parts
        self.M = sum(m for m, _ in lumps)
        self.com = sum(m * p for m, p in lumps) / self.M
        # feature positions relative to the COM: body corners (points) and wheels (circle centres)
        self.corners = np.array(BODY) - self.com
        self.centres = np.array([self.cA, self.cB]) - self.com
        self.hub = HUB - self.com


def rot(v, th):
    c, s = math.cos(th), math.sin(th)
    return np.array([v[..., 0] * c - v[..., 1] * s, v[..., 0] * s + v[..., 1] * c]).T if v.ndim > 1 else np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


THETAS = np.radians(np.arange(0.0, 360.0, 0.05))


def height_profile(sh):
    """h(theta): height of the COM above the ground when the shape, rotated counter-clockwise by theta about its COM, rests on its lowest feature."""
    s, c = np.sin(THETAS)[:, None], np.cos(THETAS)[:, None]
    zc = sh.corners[:, 0][None, :] * s + sh.corners[:, 1][None, :] * c                    # corner heights, (T, 4)
    zw = sh.centres[:, 0][None, :] * s + sh.centres[:, 1][None, :] * c - WHEEL_R             # wheel lowest points, (T, 2)
    low = np.minimum(zc.min(axis=1), zw.min(axis=1))
    return -low


def settle(sh, th0):
    """Roll downhill in COM height from orientation th0 (radians) to the nearest local minimum; returns the new theta (radians)."""
    h = height_profile(sh)
    n = len(h)
    k = int(round(math.degrees(th0) / 0.05)) % n
    # descend
    for _ in range(n):
        up, dn = h[(k + 1) % n], h[(k - 1) % n]
        if h[k] <= up + 1e-12 and h[k] <= dn + 1e-12:
            break
        k = (k + 1) % n if up < dn else (k - 1) % n
    return THETAS[k]


def support(sh, th, tol=1e-4):
    """Features touching the ground at orientation th: list of (kind, index, y position relative to the COM)."""
    s, c = math.sin(th), math.cos(th)
    feats = []
    for i, p in enumerate(sh.corners):
        feats.append(("corner", i, p[0] * c - p[1] * s, p[0] * s + p[1] * c))
    for i, p in enumerate(sh.centres):
        feats.append(("wheel", i, p[0] * c - p[1] * s, p[0] * s + p[1] * c - WHEEL_R))
    zmin = min(f[3] for f in feats)
    return [(k, i, y) for k, i, y, z in feats if z - zmin < tol], zmin


def strut_torques(sh, th):
    """Per-strut holding torque magnitude, N.m, at a rest orientation; also the support list.  Returns (tauA, tauB, supports, stable)."""
    sup, _ = support(sh, th)
    ys = sorted(sup, key=lambda f: f[2])
    W = sh.M * G
    reac = {}
    if len(ys) == 1:
        reac[ys[0][:2]] = W if abs(ys[0][2]) < 1e-3 else None
        stable = abs(ys[0][2]) < 1e-3
        if reac[ys[0][:2]] is None:
            reac[ys[0][:2]] = W
    else:
        yl, yr = ys[0], ys[-1]
        stable = yl[2] <= 1e-6 and yr[2] >= -1e-6
        d = yr[2] - yl[2]
        reac[yl[:2]] = W * yr[2] / d
        reac[yr[:2]] = W * (-yl[2]) / d
    # torque about the hub for each strut
    c, s = math.cos(th), math.sin(th)
    hub = np.array([sh.hub[0] * c - sh.hub[1] * s, sh.hub[0] * s + sh.hub[1] * c])
    out = []
    for name, wi in (("A", 0), ("B", 1)):
        tau = 0.0
        for m, p in sh.parts[name]:
            r = p - sh.com
            rp = np.array([r[0] * c - r[1] * s, r[0] * s + r[1] * c])
            tau += (rp[0] - hub[0]) * (-m * G)
        R = reac.get(("wheel", wi), 0.0)
        if R:
            contact_y = sh.centres[wi][0] * c - sh.centres[wi][1] * s
            tau += (contact_y - hub[0]) * R
        out.append(abs(tau) / 2.0)           # per strut: two sides share the planar load
    return out[0], out[1], ys, stable


def arc_ok(phiA, phiB):
    d = (phiA - phiB) % 360.0
    return d >= MIN_ARC and (360.0 - d) >= MIN_ARC


def stance_table():
    print("== Symmetric stances (A at -alpha, B at 180 + alpha), upright, resting on both wheels ==")
    print("alpha deg | body floor mm | COM height mm | hold torque per strut N.m | tip-over slope, forward / backward (deg)")
    for alpha in (0, 10, 25, 40, 55, 70, 85):
        sh = Shape(-alpha, 180 + alpha)
        th = settle(sh, 0.0)
        tA, tB, sup, stable = strut_torques(sh, th)
        # body floor height: lowest body corner above the ground
        s, c = math.sin(th), math.cos(th)
        zc = [p[0] * s + p[1] * c for p in sh.corners]
        zw = [p[0] * s + p[1] * c - WHEEL_R for p in sh.centres]
        zmin = min(zc + zw)
        floor = (min(zc) - zmin) * 1000
        h_com = -zmin * 1000
        ys = [f[2] for f in sup]
        yl, yr = min(ys), max(ys)
        fwd = math.degrees(math.atan2(yr, h_com / 1000)) if len(ys) > 1 else float("nan")
        bwd = math.degrees(math.atan2(-yl, h_com / 1000)) if len(ys) > 1 else float("nan")
        print(f"{alpha:8d}  | {floor:12.1f}  | {h_com:12.1f}  | {tA:.3f} (A), {tB:.3f} (B)         | {fwd:5.1f} / {bwd:5.1f}   theta {math.degrees(th):6.2f}")
    print("(analytic check at 25 degrees from torque_budget.py: W/4 x 70 cos25 = 0.155 N.m, plus the strut weights)\n")


def state_key(iA, iB, th):
    return (iA, iB, int(round(math.degrees(th) / 2.0)) % 180)


def move(phiA, phiB, th, which, delta, step=3.0):
    """Move strut `which` by delta degrees in `step` degree increments, settling each time.  Returns (ok, new_theta, peak torque, rolled)."""
    peak, rolled = 0.0, False
    a, b = phiA, phiB
    n = int(abs(delta) / step)
    sgn = 1 if delta > 0 else -1
    for _ in range(n):
        if which == "A":
            a += sgn * step
        else:
            b += sgn * step
        if not arc_ok(a, b):
            return False, th, peak, rolled
        sh = Shape(a, b)
        new = settle(sh, th)
        if abs(((new - th + math.pi) % (2 * math.pi)) - math.pi) > math.radians(2.0):
            rolled = True
        th = new
        tA, tB, sup, stable = strut_torques(sh, th)
        peak = max(peak, tA, tB)
    return True, th, peak, rolled


def righting(figure=None, objective="torque"):
    STEP = 15
    N = 360 // STEP
    start = (330.0, 210.0)                       # A at -30, B at 210: the stance 30 degrees below horizontal, relative to the body
    sh0 = Shape(*start)
    th0 = settle(sh0, math.pi)                   # body inverted
    print(f"== Self-righting from inverted, objective: {'lowest peak torque' if objective == 'torque' else 'fewest moves'} (struts {STEP} degrees per move, one strut at a time, quasi-static) ==")
    print(f"start: A {start[0]:.0f}, B {start[1]:.0f}; rests at theta {math.degrees(th0):.1f} degrees (180 = upside down)")
    # Dijkstra over (iA, iB, theta key) with cost (peak torque, moves): minimise the peak torque first, then the number of moves
    sA, sB = int(round(start[0] / STEP)) % N, int(round(start[1] / STEP)) % N
    k0 = state_key(sA, sB, th0)
    key = (lambda pk, mv: (pk, mv)) if objective == "torque" else (lambda pk, mv: (mv, pk))
    best = {k0: key(0.0, 0)}
    parent = {k0: None}
    store = {k0: (sA, sB, th0)}
    pq = [(*key(0.0, 0), k0)]
    goal = None
    while pq:
        c0, c1, k = heapq.heappop(pq)
        if best[k] < (c0, c1):
            continue
        peak, moves = (c0, c1) if objective == "torque" else (c1, c0)
        iA, iB, th = store[k]
        if (math.degrees(th) < 8.0 or math.degrees(th) > 352.0) and moves > 0:
            goal = k
            break
        for which in ("A", "B"):
            for d in (STEP, -STEP):
                phiA, phiB = iA * STEP, iB * STEP
                ok, th2, pk, rolled = move(phiA, phiB, th, which, d)
                if not ok:
                    continue
                niA, niB = (iA + (d // STEP if which == "A" else 0)) % N, (iB + (d // STEP if which == "B" else 0)) % N
                k2 = state_key(niA, niB, th2)
                c2 = key(max(peak, pk), moves + 1)
                if k2 not in best or c2 < best[k2]:
                    best[k2] = c2
                    parent[k2] = (k, which, d, pk, rolled)
                    store[k2] = (niA, niB, th2)
                    heapq.heappush(pq, (*c2, k2))
    if goal is None:
        print("no sequence found within the model's limits")
        return None
    path = []
    k = goal
    while parent[k] is not None:
        pk_, which, d, pk, rolled = parent[k]
        path.append((which, d, pk, rolled, store[k]))
        k = pk_
    path.reverse()
    peak_goal = max(p[2] for p in path)
    print(f"sequence: {len(path)} moves, peak strut torque {peak_goal:.3f} N.m (per strut, no margin)")
    for n, (which, d, pk, rolled, (iA, iB, th)) in enumerate(path, 1):
        print(f"  {n:2d}. strut {which} {d:+4d} deg -> A {iA * STEP:3d}, B {iB * STEP:3d}, theta {math.degrees(th):6.1f}, peak torque in the move {pk:.3f} N.m{'  (rolls)' if rolled else ''}")
    if figure:
        draw_sequence(start, th0, path, STEP, figure)
    return path, peak_goal


def draw_sequence(start, th0, path, STEP, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    frames = [(start[0], start[1], th0, "start")]
    a, b = start
    for which, d, pk, rolled, (iA, iB, th) in path:
        frames.append((iA * STEP, iB * STEP, th, f"strut {which} {d:+d}\n{pk:.2f} N.m"))
    n = len(frames)
    cols = min(6, n)
    rows = int(math.ceil(n / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(2.6 * cols, 2.3 * rows))
    axs = np.atleast_1d(axs).ravel()
    for ax, (pA, pB, th, lab) in zip(axs, frames):
        sh = Shape(pA, pB)
        c, s = math.cos(th), math.sin(th)
        def w(p):                                                       # body-frame point (relative to the COM) -> world
            q = np.array([p[0] * c - p[1] * s, p[0] * s + p[1] * c])
            return q
        corners = [w(p - sh.com) for p in np.array(BODY)]
        zmin = min(min(q[1] for q in corners), min(w(cc - sh.com)[1] - WHEEL_R for cc in (sh.cA, sh.cB)))
        off = np.array([0.0, -zmin])
        poly = np.array([q + off for q in corners])
        ax.fill(poly[:, 0] * 1000, poly[:, 1] * 1000, color="#8d97a3")
        hub = w(HUB - sh.com) + off
        for cc, col in ((sh.cA, "#c9a46a"), (sh.cB, "#a8783f")):
            wc = w(cc - sh.com) + off
            ax.plot([hub[0] * 1000, wc[0] * 1000], [hub[1] * 1000, wc[1] * 1000], color=col, lw=2.5)
            ax.add_patch(plt.Circle((wc[0] * 1000, wc[1] * 1000), WHEEL_R * 1000, fill=False, color=col, lw=1.5))
        com = w(np.zeros(2)) + off
        ax.plot(com[0] * 1000, com[1] * 1000, "r+", ms=7)
        ax.axhline(0, color="k", lw=1)
        ax.set_xlim(-150, 150); ax.set_ylim(-5, 210); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(lab, fontsize=7)
    for ax in axs[len(frames):]:
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(out, dpi=90)
    print("wrote", out)


def envelope():
    """Worst holding torque per strut over every stable rest state of every allowed strut-angle pair (5 degree grid): what a servo might have to hold."""
    print("== Holding torque envelope over all strut angles and all stable rest orientations (no margin) ==")
    worst, count = [], 0
    for a in range(0, 360, 5):
        for b in range(0, 360, 5):
            if not arc_ok(a, b):
                continue
            sh = Shape(a, b)
            h = height_profile(sh)
            n = len(h)
            idx = [k for k in range(n) if h[k] <= h[(k + 1) % n] and h[k] < h[(k - 1) % n]]
            for k in idx:
                tA, tB, sup, stable = strut_torques(sh, THETAS[k])
                if stable:
                    worst.append((max(tA, tB), a, b, math.degrees(THETAS[k])))
                    count += 1
    worst.sort(reverse=True)
    vals = np.array([w[0] for w in worst])
    print(f"{count} stable rest states: median {np.median(vals):.3f} N.m, 95th percentile {np.percentile(vals, 95):.3f}, 99th {np.percentile(vals, 99):.3f}, maximum {vals.max():.3f} N.m per strut")
    for w in worst[:3]:
        print(f"   worst: {w[0]:.3f} N.m at A {w[1]}, B {w[2]}, theta {w[3]:.1f}")
    return vals.max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figure")
    args = ap.parse_args()
    print(f"masses: body lump {M_BODY * 1000:.0f} g + servos {M_SERVO * 1000:.0f} + hub {M_HUB * 1000:.0f} + struts {M_STRUT * 1000:.0f} + wheels {M_WHEEL * 1000:.0f} + wheel supports {M_SUPPORT * 1000:.0f} = {M_TOTAL * 1000:.0f} g")
    sh = Shape(-25, 205)
    print(f"COM at the 25 degree stance (body frame, mm): y {sh.com[0] * 1000:.1f}, z {sh.com[1] * 1000:.1f} (hub at 0, 30); servo A and B on opposite sides of the hub axis shift it toward -y\n")
    stance_table()
    righting(args.figure, "torque")
    print()
    righting(None, "moves")
    print()
    envelope()


if __name__ == "__main__":
    main()
