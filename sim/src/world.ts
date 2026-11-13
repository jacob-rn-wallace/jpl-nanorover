// The arena: a height function with boxes, ramps, a pit, the table edge, a sunlit patch and three markers.
import { ARENA, VOID_Z } from "./constants";

export interface Box { x0: number; x1: number; y0: number; y1: number; h: number; color: number; name: string }
export interface Ramp { x0: number; x1: number; y0: number; y1: number; hLow: number; hHigh: number; along: "x" | "y"; name: string }
export interface Pit { x0: number; x1: number; y0: number; y1: number; depth: number }
export interface Marker { id: string; x: number; y: number; color: number; label: string }

export class World {
  w = ARENA.w; d = ARENA.d;
  start = { x: -0.70, y: -0.40, theta: 0 };
  sun = { x: 0.52, y: 0.30, r: 0.22 };                    // the window patch (charges the rover)
  boxes: Box[] = [
    { x0: -0.25, x1: -0.17, y0: -0.30, y1: -0.22, h: 0.020, color: 0x8a7f72, name: "rock A (2 cm)" },
    { x0: 0.05,  x1: 0.15,  y0: -0.05, y1: 0.07,  h: 0.050, color: 0x6e665c, name: "rock B (5 cm, blocks)" },
    { x0: 0.25,  x1: 0.33,  y0: -0.35, y1: -0.27, h: 0.035, color: 0x7b7266, name: "rock C (3.5 cm, blocks)" },
    { x0: -0.05, x1: 0.02,  y0: 0.25,  y1: 0.31,  h: 0.025, color: 0x8f8579, name: "rock D (2.5 cm)" },
    { x0: -0.55, x1: -0.47, y0: 0.30,  y1: 0.40,  h: 0.045, color: 0x726a60, name: "rock E (4.5 cm, blocks)" },
    { x0: -0.12, x1: -0.06, y0: -0.18, y1: -0.12, h: 0.015, color: 0x978d80, name: "pebble F (1.5 cm)" },
    { x0: 0.70,  x1: 0.80,  y0: -0.30, y1: -0.05, h: 0.100, color: 0x5d6f7a, name: "platform (10 cm)" },
  ];
  ramps: Ramp[] = [
    { x0: 0.20, x1: 0.50, y0: 0.10, y1: 0.36, hLow: 0, hHigh: 0.03, along: "x", name: "gentle ramp (6 degrees)" },
    { x0: 0.55, x1: 0.70, y0: -0.30, y1: -0.05, hLow: 0, hHigh: 0.10, along: "x", name: "steep ramp (34 degrees)" },
  ];
  pits: Pit[] = [{ x0: -0.40, x1: -0.30, y0: -0.10, y1: 0.00, depth: 0.05 }];
  markers: Marker[] = [
    { id: "red", x: -0.10, y: 0.42, color: 0xd9342b, label: "red" },
    { id: "green", x: 0.62, y: -0.20, color: 0x2fa84f, label: "green" },
    { id: "blue", x: -0.58, y: 0.12, color: 0x2f6fd9, label: "blue" },
  ];

  heightAt(x: number, y: number): number {
    if (x < -this.w / 2 || x > this.w / 2 || y < -this.d / 2 || y > this.d / 2) return VOID_Z;
    for (const p of this.pits) if (x >= p.x0 && x <= p.x1 && y >= p.y0 && y <= p.y1) return -p.depth;
    let h = 0;
    for (const r of this.ramps) if (x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1) {
      const t = r.along === "x" ? (x - r.x0) / (r.x1 - r.x0) : (y - r.y0) / (r.y1 - r.y0);
      h = Math.max(h, r.hLow + t * (r.hHigh - r.hLow));
    }
    for (const b of this.boxes) if (x >= b.x0 && x <= b.x1 && y >= b.y0 && y <= b.y1) h = Math.max(h, b.h);
    return h;
  }
  /** slope magnitude (rise over run) around a point, central differences over +-e; the void beyond the table edge is ignored */
  slopeAt(x: number, y: number, e = 0.05): number {
    const c = this.heightAt(x, y);
    const h = (px: number, py: number) => { const v = this.heightAt(px, py); return v < -0.2 ? c : v; };
    const gx = (h(x + e, y) - h(x - e, y)) / (2 * e);
    const gy = (h(x, y + e) - h(x, y - e)) / (2 * e);
    return Math.hypot(gx, gy);
  }
  inSun(x: number, y: number): number {                   // 0 to 1, soft edge
    const d = Math.hypot(x - this.sun.x, y - this.sun.y);
    return Math.min(1, Math.max(0, (this.sun.r - d) / 0.05));
  }
  /** distance along a ray to the first surface, or null beyond maxR (a fixed-step march with one refinement) */
  rayHit(o: [number, number, number], d: [number, number, number], maxR: number): number | null {
    const step = 0.004;
    let prev = 0;
    for (let t = step; t <= maxR; t += step) {
      const x = o[0] + d[0] * t, y = o[1] + d[1] * t, z = o[2] + d[2] * t;
      if (z <= this.heightAt(x, y)) {
        let lo = prev, hi = t;                              // refine
        for (let k = 0; k < 6; k++) {
          const m = (lo + hi) / 2;
          if (o[2] + d[2] * m <= this.heightAt(o[0] + d[0] * m, o[1] + d[1] * m)) hi = m; else lo = m;
        }
        return hi;
      }
      prev = t;
      if (d[2] >= 0 && z > 0.12) return null;               // rising above everything
    }
    return null;
  }
}
