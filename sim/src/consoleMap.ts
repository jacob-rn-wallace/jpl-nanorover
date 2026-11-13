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
  version = 0;
  pose: PoseEst | null = null; battery = 1; mode = "pilot"; risk = 1; nav = "idle"; frames = 0; lastFrameT = -1;
  trail: { x: number; y: number }[] = [];
  markers = new Map<string, { x: number; y: number }>();
  goals: { x: number; y: number }[] = [];
  photos: PhotoPayload[] = [];
  log: string[] = [];
  latestHazard = 0;

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
    const dirs = tofDirs(), e = p.pose, n = TOF.n;
    this.pose = e; this.battery = p.battery; this.mode = p.mode; this.risk = p.risk; this.nav = p.nav; this.frames++; this.lastFrameT = p.t;
    const last = this.trail[this.trail.length - 1];
    if (!last || Math.hypot(last.x - e.x, last.y - e.y) > 0.01) this.trail.push({ x: e.x, y: e.y });
    const world = (b: V3): V3 => { const w = rotate(b, e.theta, p.imu.pitch, p.imu.roll); return [e.x + w[0], e.y + w[1], e.z + w[2]]; };
    let kinds = 0;
    for (let k = 0; k < ZONES; k++) {
      const r = p.ranges[k];
      if (r > 0) {
        const w = world(bodyPoint(dirs, k, r)), c = this.idx(w[0], w[1]);
        if (c >= 0 && w[2] < -0.12) { this.haz[c] = HZ_DROP; this.z[c] = -0.04; this.n[c] = Math.max(this.n[c], 1); }       // the void beyond an edge: an edge marker, not a deep cell
        else if (c >= 0) {
          this.n[c] = Math.min(this.n[c] + 1, 60000);
          this.z[c] += (Math.max(-0.12, Math.min(0.2, w[2])) - this.z[c]) / Math.min(this.n[c], 6);       // far-below points (beyond an edge) are drawn at a limited depth
          this.haz[c] = p.haz[k];
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
            if (c >= 0) { this.haz[c] = HZ_DROP; this.z[c] = w[2] - 0.04; this.n[c] = Math.max(this.n[c], 1); }
          }
          kinds |= HZ_DROP;
          break;
        }
      }
    }
    this.latestHazard = kinds;
    this.version++;
  }
  addPhoto(ph: PhotoPayload, t: number): void {
    this.photos.unshift(ph);
    this.say(t, `photo received (${ph.size}, ${(ph.bytes / 1000).toFixed(0)} KB)` + (ph.found.length ? `: ${ph.found.join(", ")} marker` : ": no marker seen"));
    for (const id of ph.found) {                              // reported at the pose the rover believed it had, so drift shows
      const d = ph.dists[id] ?? 0.3, e = ph.pose;
      this.markers.set(id, { x: e.x + Math.cos(e.theta) * (ROVER.mountFwd + d), y: e.y + Math.sin(e.theta) * (ROVER.mountFwd + d) });
    }
  }
  hazardText(): string { return kindsText(this.latestHazard); }
}
