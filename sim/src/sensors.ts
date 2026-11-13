// The rover's sensors as the firmware sees them: an 8 x 8 multizone time-of-flight sensor, wheel odometry, a gyro and a tilt sensor.
import { ROVER, TOF, SLAM_QUALITY } from "./constants";
import { Rng, rotate, tiltDown, V3 } from "./util";
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
  constructor(private rng: Rng) {}
  reset(r: Rover): void {
    this.est = { x: r.x, y: r.y, theta: r.theta, z: r.z, sigma: 0 };
    this.bias = this.rng.gauss() * 0.003 * this.quality;
  }
  step(r: Rover, dt: number): void {
    const q = this.quality, e = this.est;
    if (q === 0) { e.x = r.x; e.y = r.y; e.theta = r.theta; e.z = r.z; e.sigma = 0; this.imu = { pitch: r.pitch, roll: r.roll }; return; }
    this.imu = { pitch: r.pitch + this.rng.gauss() * 0.0087, roll: r.roll + this.rng.gauss() * 0.0087 };   // 0.5 degrees
    this.bias += this.rng.gauss() * 0.0008 * Math.sqrt(dt) * q;
    const v = r.vel * (1 + this.rng.gauss() * 0.02 * q), w = r.omega + this.bias;
    e.theta += w * dt;
    e.x += v * Math.cos(e.theta) * dt; e.y += v * Math.sin(e.theta) * dt;
    e.z += v * dt * Math.sin(this.imu.pitch);
    e.sigma += Math.abs(r.vel) * dt * 0.04 * q + Math.abs(r.omega) * dt * 0.005 * q;     // a rough 1-sigma radius for the display
  }
}
