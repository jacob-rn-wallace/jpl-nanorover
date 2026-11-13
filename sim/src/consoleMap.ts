// The operator's model of the world: built only from what has arrived over the radio (range frames, the rover's own pose estimate, photographs).
import { TOF, ROVER } from "./constants";
import { rotate, V3 } from "./util";
import { Packet, TofPacket, HZ_DROP, kindsText } from "./firmware";
import { tofDirs, bodyPoint, PoseEst, ZONES } from "./sensors";

export interface PhotoPayload {
  size: string; w: number; h: number; image: ImageData | null; lit: boolean; t: number;
  found: string[]; dists: Record<string, number>; pose: PoseEst; bytes: number;
}
export class ConsoleMap {
  res = 0.02; x0 = -0.9; y0 = -0.7; cols = 90; rows = 70;
  z = new Float32Array(90 * 70); n = new Uint16Array(90 * 70); haz = new Uint8Array(90 * 70);
  hs = new Float32Array(90 * 70); hk = new Uint8Array(90 * 70);       // evidence score and kind bits per cell; haz is what is shown (score >= 1, gaps filled)
  version = 0;
  pose: PoseEst | null = null; battery = 1; mode = "pilot"; risk = 1; nav = "idle"; frames = 0; lastFrameT = -1;
  trail: { x: number; y: number }[] = [];
  markers = new Map<string, { x: number; y: number }>();
  goals: { x: number; y: number }[] = [];
  photos: PhotoPayload[] = [];
  log: string[] = [];
  latestHazard = 0;
  corr = { dx: 0, dy: 0, dth: 0 };              // the console's correction to the rover's dead-reckoned pose, from matching frames against the map
  matchInfo = { used: 0, gain: 0 };

  idx(x: number, y: number): number {
    const ix = Math.floor((x - this.x0) / this.res), iy = Math.floor((y - this.y0) / this.res);
    return ix < 0 || iy < 0 || ix >= this.cols || iy >= this.rows ? -1 : iy * this.cols + ix;
  }
  say(t: number, text: string) { this.log.push(`${t.toFixed(0).padStart(4)} s  ${text}`); if (this.log.length > 60) this.log.shift(); }

  ingest(p: Packet): void {
    if (p.kind === "event") { this.say(p.t, p.text); return; }
    this.addFrame(p);
  }
  private addFrame(p: TofPacket): void {
    const dirs = tofDirs(), n = TOF.n;
    const e = this.align(p, dirs);
    this.pose = e; this.battery = p.battery; this.mode = p.mode; this.risk = p.risk; this.nav = p.nav; this.frames++; this.lastFrameT = p.t;
    const last = this.trail[this.trail.length - 1];
    if (!last || Math.hypot(last.x - e.x, last.y - e.y) > 0.01) this.trail.push({ x: e.x, y: e.y });
    const world = (b: V3): V3 => { const w = rotate(b, e.theta, p.imu.pitch, p.imu.roll); return [e.x + w[0], e.y + w[1], e.z + w[2]]; };
    let kinds = 0;
    for (let k = 0; k < ZONES; k++) {
      const r = p.ranges[k];
      if (r > 0) {
        const w = world(bodyPoint(dirs, k, r)), c = this.idx(w[0], w[1]);
        if (c >= 0 && w[2] < -0.12) { this.mark(c, HZ_DROP); this.z[c] = -0.04; this.n[c] = Math.max(this.n[c], 1); }       // the void beyond an edge: an edge marker, not a deep cell
        else if (c >= 0) {
          this.n[c] = Math.min(this.n[c] + 1, 60000);
          this.z[c] += (Math.max(-0.12, Math.min(0.2, w[2])) - this.z[c]) / Math.min(this.n[c], 6);       // far-below points (beyond an edge) are drawn at a limited depth
          if (p.haz[k]) this.mark(c, p.haz[k]);
          else if (Math.abs(w[2]) < 0.015) this.hs[c] = Math.max(0, this.hs[c] - 0.34);     // clear floor seen again: forget slowly
        }
        kinds |= p.haz[k];
      }
    }
    for (let i = 0; i < n; i++) {                              // missing returns: the edge is where the floor would have been in the lowest row that lost it
      for (let j = n - 1; j >= 0; j--) {
        const k = j * n + i;
        if (p.ranges[k] === -1) {
          const dz = dirs[3 * k + 2];
          if (dz < -1e-3) {
            const rf = ROVER.mountH / -dz;
            const w = world([ROVER.mountFwd + dirs[3 * k] * rf, dirs[3 * k + 1] * rf, 0]), c = this.idx(w[0], w[1]);
            if (c >= 0) { this.mark(c, HZ_DROP); this.z[c] = w[2] - 0.04; this.n[c] = Math.max(this.n[c], 1); }
          }
          kinds |= HZ_DROP;
          break;
        }
      }
    }
    this.latestHazard = kinds;
    this.shape();
    this.version++;
  }
  /** scan matching: nudge the correction so this frame's heights agree with what the map already holds (needs relief to lock onto: flat floor does not constrain it) */
  private align(p: TofPacket, dirs: Float32Array | number[]): PoseEst {
    const o = p.pose, q = this.corr, K = ZONES;
    const pts: { b: V3; z: number }[] = [];
    for (let k = 0; k < K; k++) if (p.ranges[k] > 0 && !p.haz[k]) pts.push({ b: bodyPoint(dirs as Float32Array, k, p.ranges[k]), z: 0 });
    const cost = (dx: number, dy: number, dth: number) => {
      let s = 0, m = 0;
      for (const t of pts) {
        const w = rotate(t.b, o.theta + q.dth + dth, p.imu.pitch, p.imu.roll);
        const x = o.x + q.dx + dx + w[0], y = o.y + q.dy + dy + w[1], c = this.idx(x, y);
        if (c < 0 || this.n[c] < 3 || this.hs[c] >= 1) continue;
        s += Math.min(0.03, Math.abs(this.z[c] - (o.z + w[2]))); m++;
      }
      return m < 10 ? null : s / m + 0.0004 * (Math.abs(dx) + Math.abs(dy)) + 0.002 * Math.abs(dth);
    };
    const base = cost(0, 0, 0);
    if (base !== null && base > 0.004) {
      let best = base, bx = 0, by = 0, bt = 0;
      for (let dx = -0.04; dx <= 0.041; dx += 0.01) for (let dy = -0.04; dy <= 0.041; dy += 0.01) for (let dt = -0.06; dt <= 0.061; dt += 0.03) {
        const c = cost(dx, dy, dt); if (c !== null && c < best - 1e-6) { best = c; bx = dx; by = dy; bt = dt; }
      }
      if (best < base * 0.8) { q.dx += 0.5 * bx; q.dy += 0.5 * by; q.dth += 0.5 * bt; this.matchInfo = { used: pts.length, gain: base - best }; }
    }
    return { ...o, x: o.x + q.dx, y: o.y + q.dy, theta: o.theta + q.dth };
  }
  private mark(c: number, kind: number): void { this.hs[c] = Math.min(3, this.hs[c] + 1); this.hk[c] |= kind; }
  /** shown hazards: cells with enough evidence, plus cells enclosed by them (an 8x8 frame samples a rock every 4 cm, the grid is 2 cm) */
  private shape(): void {
    const C = this.cols, R = this.rows, h = this.haz;
    for (let c = 0; c < C * R; c++) { h[c] = this.hs[c] >= 2 ? this.hk[c] : 0; if (this.hs[c] < 0.01) this.hk[c] = 0; }
    const base = h.slice();
    for (let j = 1; j < R - 1; j++) for (let i = 1; i < C - 1; i++) {
      const c = j * C + i; if (base[c]) continue;
      let cnt = 0, kind = 0;
      for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) { const b = base[c + dj * C + di]; if (b) { cnt++; kind |= b; } }
      const opp = (base[c - 1] && base[c + 1]) || (base[c - C] && base[c + C]) || (base[c - C - 1] && base[c + C + 1]) || (base[c - C + 1] && base[c + C - 1]);
      if (cnt >= 3 || opp) { h[c] = kind; if (!this.n[c]) this.n[c] = 1; }
    }
  }
  addPhoto(ph: PhotoPayload, t: number): void {
    this.photos.unshift(ph);
    this.say(t, `photo received (${ph.size}, ${(ph.bytes / 1000).toFixed(0)} KB)` + (ph.found.length ? `: ${ph.found.join(", ")} marker` : ": no marker seen"));
    for (const id of ph.found) {                              // reported at the pose the rover believed it had, so drift shows
      const d = ph.dists[id] ?? 0.3, e = { ...ph.pose, x: ph.pose.x + this.corr.dx, y: ph.pose.y + this.corr.dy, theta: ph.pose.theta + this.corr.dth };
      this.markers.set(id, { x: e.x + Math.cos(e.theta) * (ROVER.mountFwd + d), y: e.y + Math.sin(e.theta) * (ROVER.mountFwd + d) });
    }
  }
  hazardText(): string { return kindsText(this.latestHazard); }
}
