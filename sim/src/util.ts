// Small helpers: a seeded random generator (so runs and tests repeat), angles and 3-vectors.
export class Rng {
  private s: number;
  constructor(seed = 1) { this.s = seed >>> 0; }
  next(): number {                       // mulberry32
    this.s = (this.s + 0x6d2b79f5) >>> 0;
    let t = this.s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
  gauss(): number {                      // Box-Muller
    const u = Math.max(this.next(), 1e-12), v = this.next();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }
}
export const clamp = (x: number, a: number, b: number) => Math.min(b, Math.max(a, x));
export const wrap = (a: number) => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };
export const deg = (d: number) => (d * Math.PI) / 180;
export type V3 = [number, number, number];
// rotation: yaw about z, then pitch (nose up positive) about the body's y axis, then roll about x:  R = Rz(yaw) Ry(-pitch) Rx(roll)
export function rotate(v: V3, yaw: number, pitch: number, roll: number): V3 {
  let [x, y, z] = v;
  const cr = Math.cos(roll), sr = Math.sin(roll);
  [y, z] = [y * cr - z * sr, y * sr + z * cr];
  const b = -pitch, cb = Math.cos(b), sb = Math.sin(b);
  [x, z] = [x * cb + z * sb, -x * sb + z * cb];
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  [x, y] = [x * cy - y * sy, x * sy + y * cy];
  return [x, y, z];
}
// rotate about the y axis by +b (positive tilts the x axis down), used for the sensor's downward tilt
export function tiltDown(v: V3, b: number): V3 {
  const [x, y, z] = v, c = Math.cos(b), s = Math.sin(b);
  return [x * c + z * s, y, -x * s + z * c];
}
