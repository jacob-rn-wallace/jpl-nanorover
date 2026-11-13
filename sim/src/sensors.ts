// The rover's sensors as the firmware sees them: an 8 x 8 multizone time-of-flight sensor, wheel odometry, a gyro and a tilt sensor.
import { ROVER, TOF, SLAM_QUALITY, BEACON, LIGHTHOUSE as LH } from "./constants";
import { Rng, rotate, tiltDown, V3, wrap } from "./util";
import { World } from "./world";
import { Rover } from "./rover";

export const ZONES = TOF.n * TOF.n;
export const NO_TARGET = -1;     // nothing within range: a missing return
export const DROPOUT = -2;       // an unreliable zone (low confidence), ignored by the firmware

let dirsCache: Float32Array | null = null;
/** unit direction of every zone in the body frame (x forward, y left, z up); zone k = row j * 8 + column i, row 0 on top, column 0 on the left */
export function tofDirs(): Float32Array {
  if (dirsCache) return dirsCache;
  const out = new Float32Array(ZONES * 3);
  for (let j = 0; j < TOF.n; j++) for (let i = 0; i < TOF.n; i++) {
    const az = (0.5 - (i + 0.5) / TOF.n) * TOF.fov, el = (0.5 - (j + 0.5) / TOF.n) * TOF.fov;
    let d: V3 = [1, Math.tan(az), Math.tan(el)];
    const m = Math.hypot(...d); d = [d[0] / m, d[1] / m, d[2] / m];
    d = tiltDown(d, ROVER.tofPitch);
    out.set(d, (j * TOF.n + i) * 3);
  }
  return (dirsCache = out);
}

/** one sensor frame from the true state; ranges in metres, NO_TARGET or DROPOUT otherwise */
export function tofMeasure(world: World, r: Rover, rng: Rng): Float32Array {
  const dirs = tofDirs(), out = new Float32Array(ZONES);
  const m = rotate([ROVER.mountFwd, 0, ROVER.mountH], r.theta, r.pitch, r.roll);
  const o: V3 = [r.x + m[0], r.y + m[1], r.z + m[2]];
  for (let k = 0; k < ZONES; k++) {
    const d = rotate([dirs[3 * k], dirs[3 * k + 1], dirs[3 * k + 2]], r.theta, r.pitch, r.roll);
    const t = world.rayHit(o, d, TOF.maxR);
    if (t === null) out[k] = NO_TARGET;
    else if (rng.next() < TOF.dropout) out[k] = DROPOUT;
    else {
      const rr = t + rng.gauss() * (TOF.sigma0 + TOF.sigmaRel * t);
      out[k] = rr < TOF.minR ? DROPOUT : rr;
    }
  }
  return out;
}
/** a zone's point in the rover's body frame, origin at the ground under the rover's centre (so a flat floor has z = 0) */
export function bodyPoint(dirs: Float32Array, k: number, range: number): V3 {
  return [ROVER.mountFwd + dirs[3 * k] * range, dirs[3 * k + 1] * range, ROVER.mountH + dirs[3 * k + 2] * range];
}

export interface PoseEst { x: number; y: number; theta: number; z: number; sigma: number }
export interface Imu { pitch: number; roll: number }

/** dead reckoning from wheel odometry and a gyro; the quality setting scales the errors (0 gives the true pose) */
export class Odometry {
  est: PoseEst = { x: 0, y: 0, theta: 0, z: 0, sigma: 0 };
  imu: Imu = { pitch: 0, roll: 0 };
  private bias = 0;
  quality = SLAM_QUALITY[1];
  /** tilt sensor noise, rad (0.5 degrees raw), independent of the quality switch; 0 gives the true tilt */
  tiltSigma = 0.0087;
  /** gyro zero-rate calibration at stops: the firmware averages the gyro while the wheels are still and subtracts it (firmware only, no hardware) */
  calibrate = true;
  /** ultrasonic beacon fixes: off by default so the earlier measurements stay comparable */
  beacons = false;
  /** Lighthouse 1.0 fix from the up-lid cells; overrides nothing else, can run with the beacons off */
  lighthouse = false; lhDetect = LH.detect;
  private lhT = 0; lhFixes = 0; lhRejected = 0;
  private beaconT = 0; fixes = 0; rejected = 0;
  private still = 0; private accum = 0; private n = 0; private biasEst = 0;
  constructor(private rng: Rng) {}
  reset(r: Rover): void {
    this.est = { x: r.x, y: r.y, theta: r.theta, z: r.z, sigma: 0 };
    this.bias = this.rng.gauss() * 0.003 * this.quality;
    this.still = 0; this.accum = 0; this.n = 0; this.biasEst = 0; this.beaconT = 0; this.fixes = 0; this.rejected = 0; this.lhT = 0; this.lhFixes = 0; this.lhRejected = 0;
  }
  /** angles (azimuth about vertical, elevation) from a station to a point, as the sweeps would give them */
  private static lhAngles(st: { x: number; y: number; z: number }, p: V3): [number, number] {
    const dx = p[0] - st.x, dy = p[1] - st.y, dz = p[2] - st.z;
    return [Math.atan2(dy, dx), Math.atan2(dz, Math.hypot(dx, dy))];
  }
  private lhPoints(x: number, y: number, z: number, th: number, pitch: number, roll: number): V3[] {
    return LH.sensors.map(([sx, sy]) => { const m = rotate([sx, sy, 0], th, pitch, roll); return [x + m[0], y + m[1], z + LH.lidH + m[2]] as V3; });
  }
  /** Lighthouse 1.0: noisy sweep angles from the true pose, then a Gauss-Newton fit of (x, y, heading) to the estimate's height and tilt; gated and blended like the beacon fix */
  private lighthouseFix(r: Rover, dt: number): void {
    this.lhT += dt; if (this.lhT < LH.period) return; this.lhT = 0;
    const e = this.est, sig = 2 * Math.PI * LH.rate * LH.sigmaT;      // rad of angle per timing error
    const truth = this.lhPoints(r.x, r.y, r.z, r.theta, r.pitch, r.roll);
    const obs: { si: number; k: number; az: number; el: number }[] = [];
    LH.stations.forEach((st, si) => truth.forEach((p, k) => {
      const [az, el] = Odometry.lhAngles(st, p);
      if (this.rng.next() < this.lhDetect) obs.push({ si, k, az: az + this.rng.gauss() * sig, el: el + this.rng.gauss() * sig });   // each axis is its own sweep
    }));
    if (obs.length < 6) return;
    const pitch = this.imu.pitch, roll = this.imu.roll;
    const res = (q: number[]): number[] => {
      const pts = this.lhPoints(q[0], q[1], e.z, q[2], pitch, roll), out: number[] = [];
      for (const o of obs) { const [az, el] = Odometry.lhAngles(LH.stations[o.si], pts[o.k]); out.push(wrap(az - o.az), el - o.el); }
      return out;
    };
    let q = [e.x, e.y, e.theta];
    for (let it = 0; it < 6; it++) {
      const f0 = res(q), J: number[][] = [];
      for (let c = 0; c < 3; c++) { const h = c < 2 ? 1e-4 : 1e-3, qq = q.slice(); qq[c] += h; const f1 = res(qq); J.push(f1.map((v, i) => (v - f0[i]) / h)); }
      const A = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], b = [0, 0, 0];
      for (let i = 0; i < f0.length; i++) for (let a = 0; a < 3; a++) { b[a] -= J[a][i] * f0[i]; for (let c = 0; c < 3; c++) A[a][c] += J[a][i] * J[c][i]; }
      const d = Odometry.solve3(A, b); if (!d) return;
      q = [q[0] + d[0], q[1] + d[1], q[2] + d[2]];
    }
    if (Math.hypot(q[0] - e.x, q[1] - e.y) > LH.gate) { this.lhRejected++; return; }
    e.x += LH.gain * (q[0] - e.x); e.y += LH.gain * (q[1] - e.y); e.theta += LH.gain * wrap(q[2] - e.theta);
    e.sigma = Math.min(e.sigma, 0.01); this.lhFixes++;
  }
  private static solve3(A: number[][], b: number[]): number[] | null {
    const M = A.map((row, i) => [...row, b[i]]);
    for (let i = 0; i < 3; i++) {
      let p = i; for (let j = i + 1; j < 3; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      if (Math.abs(M[p][i]) < 1e-12) return null; [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < 3; j++) { const f = M[j][i] / M[i][i]; for (let c = i; c < 4; c++) M[j][c] -= f * M[i][c]; }
    }
    const x = [0, 0, 0]; for (let i = 2; i >= 0; i--) { x[i] = (M[i][3] - M[i].slice(i + 1, 3).reduce((s, v, k) => s + v * x[i + 1 + k], 0)) / M[i][i]; }
    return x;
  }
  /** ranges to the posts, then a few Gauss-Newton steps from the dead-reckoned position; a fix far from the estimate is taken for an echo and dropped */
  private beaconFix(r: Rover, dt: number): void {
    this.beaconT += dt; if (this.beaconT < BEACON.period) return; this.beaconT = 0;
    const e = this.est, rg: number[] = [], px: { x: number; y: number }[] = [];
    for (const p of BEACON.posts) {
      const d = Math.hypot(p.x - r.x, p.y - r.y);
      if (d > BEACON.maxRange) continue;
      rg.push(d + this.rng.gauss() * BEACON.sigma + (this.rng.next() < BEACON.echo ? BEACON.echoBias : 0)); px.push(p);
    }
    if (rg.length < 3) return;
    let x = e.x, y = e.y;
    for (let it = 0; it < 5; it++) {
      let a = 0, b = 0, c = 0, gx = 0, gy = 0;
      for (let i = 0; i < rg.length; i++) {
        const dx = x - px[i].x, dy = y - px[i].y, d = Math.max(Math.hypot(dx, dy), 1e-6), ux = dx / d, uy = dy / d, res = rg[i] - d;
        a += ux * ux; b += ux * uy; c += uy * uy; gx += ux * res; gy += uy * res;
      }
      const det = a * c - b * b; if (Math.abs(det) < 1e-9) return;
      x += (c * gx - b * gy) / det; y += (a * gy - b * gx) / det;
    }
    if (Math.hypot(x - e.x, y - e.y) > BEACON.gate) { this.rejected++; return; }
    e.x += BEACON.gain * (x - e.x); e.y += BEACON.gain * (y - e.y);
    // heading from two receivers on the body: a noisy direct measurement of theta, blended in on the shortest arc
    const meas = r.theta + this.rng.gauss() * BEACON.headingSigma;
    let dth = meas - e.theta; dth -= 2 * Math.PI * Math.round(dth / (2 * Math.PI));
    e.theta += BEACON.headingGain * dth;
    e.sigma = Math.min(e.sigma, 0.05); this.fixes++;
  }
  step(r: Rover, dt: number): void {
    const q = this.quality, e = this.est;
    if (q === 0) { e.x = r.x; e.y = r.y; e.theta = r.theta; e.z = r.z; e.sigma = 0; this.imu = { pitch: r.pitch, roll: r.roll }; return; }
    this.imu = { pitch: r.pitch + this.rng.gauss() * this.tiltSigma, roll: r.roll + this.rng.gauss() * this.tiltSigma };
    this.bias += this.rng.gauss() * 0.0008 * Math.sqrt(dt) * q;
    const v = r.vel * (1 + this.rng.gauss() * 0.02 * q), raw = r.omega + this.bias;
    if (this.calibrate) {                       // wheel counts say "stopped": average the raw gyro over the stop (after 0.5 s of settling)
      if (Math.abs(r.vel) < 1e-4 && Math.abs(r.omega) < 1e-4) {
        this.still += dt;
        if (this.still > 0.5) { this.accum += raw; this.n++; this.biasEst = this.accum / this.n; }
      } else { this.still = 0; this.accum = 0; this.n = 0; }
    }
    const w = raw - (this.calibrate ? this.biasEst : 0);
    e.theta += w * dt;
    e.x += v * Math.cos(e.theta) * dt; e.y += v * Math.sin(e.theta) * dt;
    e.z += v * dt * Math.sin(this.imu.pitch);
    e.sigma += Math.abs(r.vel) * dt * 0.04 * q + Math.abs(r.omega) * dt * 0.005 * q;     // a rough 1-sigma radius for the display
    if (this.beacons) this.beaconFix(r, dt);
    if (this.lighthouse) this.lighthouseFix(r, dt);
  }
}
