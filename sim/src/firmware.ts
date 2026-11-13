// The rover's firmware, as a cyclic executive: one fixed-rate loop dispatching periodic tasks (scan, hazard check, navigation, telemetry),
// in the manner of Sojourner's (docs/electronics-concept.md). The hazards are Sojourner's: missing data (a drop-off), a height jump between
// adjacent zones (a rock or a hole), a large height spread (a steep slope); while moving, tilt, stall and a flat battery. Thresholds are a table keyed to a risk level.
import { ROVER, TOF, RISK, LINK } from "./constants";
import { clamp, wrap } from "./util";
import { ZONES, NO_TARGET, tofDirs, bodyPoint, PoseEst, Imu } from "./sensors";

export type Mode = "pilot" | "mission";
export const HZ_DROP = 1, HZ_ROCK = 2, HZ_SLOPE = 4;

export interface TofPacket { kind: "tof"; t: number; ranges: Float32Array; haz: Uint8Array; pose: PoseEst; imu: Imu; battery: number; mode: Mode; risk: number; nav: string; bytes: number }
export interface EventPacket { kind: "event"; t: number; text: string; bytes: number }
export type Packet = TofPacket | EventPacket;

export interface Hazard {
  flags: Uint8Array;                        // per zone: HZ_DROP | HZ_ROCK | HZ_SLOPE
  ahead: { left: boolean; center: boolean; right: boolean; any: boolean; kinds: number; nl: number; nc: number; nr: number };   // nl, nc, nr: flagged zones ahead on each side
  minFwd: number;                           // distance to the nearest hazard in the corridor (Infinity if none)
}
export const LOOK_PILOT = 0.17, LOOK_MISSION = 0.32;     // m from the body centre: how far ahead a hazard counts

/** Least-squares plane z = a x + b y + c through the ground under the nose (the three nearest rows), starting from the flat nominal floor and dropping outliers in three passes
 *  (tolerances 4.5, 2 and 1 cm), so a rock, a hole or a ramp is not fitted as ground. A tilt beyond 0.30 (17 degrees) cannot be the body's own: then null (use the body plane). */
function groundPlane(valid: Uint8Array, xf: Float32Array, yl: Float32Array, zb: Float32Array): [number, number, number] | null {
  const n = TOF.n;
  const pool: number[] = [];
  for (let j = n - 3; j < n; j++) for (let i = 0; i < n; i++) if (valid[j * n + i]) pool.push(j * n + i);
  let plane: [number, number, number] = [0, 0, 0];
  for (const tol of [0.045, 0.02, 0.01]) {
    const idx = pool.filter(k => Math.abs(zb[k] - (plane[0] * xf[k] + plane[1] * yl[k] + plane[2])) < tol);
    if (idx.length < 10) return null;
    let sxx = 0, sxy = 0, sx = 0, syy = 0, sy = 0, sxz = 0, syz = 0, sz = 0;
    const sn = idx.length;
    for (const k of idx) { const x = xf[k], y = yl[k], z = zb[k]; sxx += x * x; sxy += x * y; sx += x; syy += y * y; sy += y; sxz += x * z; syz += y * z; sz += z; }
    const det = sxx * (syy * sn - sy * sy) - sxy * (sxy * sn - sy * sx) + sx * (sxy * sy - syy * sx);
    if (Math.abs(det) < 1e-12) return null;
    plane = [
      (sxz * (syy * sn - sy * sy) - sxy * (syz * sn - sy * sz) + sx * (syz * sy - syy * sz)) / det,
      (sxx * (syz * sn - sy * sz) - sxz * (sxy * sn - sy * sx) + sx * (sxy * sz - syz * sx)) / det,
      (sxx * (syy * sz - syz * sy) - sxy * (sxy * sz - syz * sx) + sxz * (sxy * sy - syy * sx)) / det,
    ];
    if (Math.abs(plane[0]) > 0.30 || Math.abs(plane[1]) > 0.30) return null;
  }
  return plane;
}

/** Sojourner's three proximity conditions on an 8 x 8 range frame, with the thresholds of a risk level (0 to 2). Heights are measured from the ground plane
 *  under the rover's nose, so a rover that is tilted by a step does not see the flat floor ahead as a wall. */
export function analyze(ranges: Float32Array, risk: number, look: number): Hazard {
  const th = RISK[risk], dirs = tofDirs(), n = TOF.n;
  const valid = new Uint8Array(ZONES), xf = new Float32Array(ZONES), yl = new Float32Array(ZONES), zb = new Float32Array(ZONES);
  for (let k = 0; k < ZONES; k++) if (ranges[k] > 0) { const p = bodyPoint(dirs, k, ranges[k]); valid[k] = 1; xf[k] = p[0]; yl[k] = p[1]; zb[k] = p[2]; }
  const pl = groundPlane(valid, xf, yl, zb);
  if (pl) for (let k = 0; k < ZONES; k++) if (valid[k]) zb[k] -= pl[0] * xf[k] + pl[1] * yl[k] + pl[2];
  const near = new Uint8Array(ZONES);                           // heights are judged only within 0.5 m (beyond that the plane's error grows and the rover decides nothing)
  for (let k = 0; k < ZONES; k++) near[k] = valid[k] && xf[k] <= 0.5 ? 1 : 0;
  const flags = new Uint8Array(ZONES);
  for (let k = 0; k < ZONES; k++) if (ranges[k] === NO_TARGET || (near[k] && zb[k] < -th.drop) || (valid[k] && !near[k] && zb[k] < -0.3)) flags[k] |= HZ_DROP;   // missing data or far below: a drop-off
  for (let k = 0; k < ZONES; k++) if (near[k] && zb[k] > th.rock) flags[k] |= HZ_ROCK;      // a surface above the ground by more than the risk level allows: a rock, seen as a wall
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const k = j * n + i;
    if (!near[k]) continue;
    for (const k2 of [i + 1 < n ? k + 1 : -1, j + 1 < n ? k + n : -1]) {
      if (k2 >= 0 && near[k2] && Math.abs(zb[k] - zb[k2]) > th.rock) { flags[k] |= HZ_ROCK; flags[k2] |= HZ_ROCK; }          // adjacent zones differ in height: a rock or a hole
    }
  }
  let lo = Infinity, hi = -Infinity;
  for (let k = 0; k < ZONES; k++) if (near[k]) { lo = Math.min(lo, zb[k]); hi = Math.max(hi, zb[k]); }
  if (hi - lo > th.slope) for (let k = 0; k < ZONES; k++) if (near[k] && Math.abs(zb[k]) > th.slope / 2) flags[k] |= HZ_SLOPE;   // a steep slope
  const ahead = { left: false, center: false, right: false, any: false, kinds: 0, nl: 0, nc: 0, nr: 0 };
  let minFwd = Infinity;
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const k = j * n + i;
    if (!flags[k]) continue;
    let fx = xf[k], fy = yl[k];
    if (!valid[k] || (flags[k] & HZ_DROP)) {                    // a missing return, or a surface far below, is located where the floor would have been (a flat floor under the sensor)
      const dz = dirs[3 * k + 2];
      if (dz >= -1e-3) continue;
      const rf = ROVER.mountH / -dz; fx = ROVER.mountFwd + dirs[3 * k] * rf; fy = dirs[3 * k + 1] * rf;
    }
    if (fx < look && Math.abs(fy) < 0.12) {                     // inside the corridor the rover (radius 9 cm) will sweep
      ahead.any = true; ahead.kinds |= flags[k]; minFwd = Math.min(minFwd, fx);
      if (i < 3) { ahead.left = true; ahead.nl++; } else if (i < 5) { ahead.center = true; ahead.nc++; } else { ahead.right = true; ahead.nr++; }
    }
  }
  return { flags, ahead, minFwd };
}

/** a hazard counts only if it is seen in two consecutive frames (noise rarely repeats): the sides are ANDed, the kinds are those both frames saw */
export function confirmAhead(a: Hazard["ahead"], b: Hazard["ahead"]): Hazard["ahead"] {
  const left = a.left && b.left, center = a.center && b.center, right = a.right && b.right;
  return { left, center, right, any: left || center || right, kinds: a.kinds & b.kinds, nl: Math.min(a.nl, b.nl), nc: Math.min(a.nc, b.nc), nr: Math.min(a.nr, b.nr) };
}

export interface FwIn {
  t: number; dt: number; tof: Float32Array | null; pose: PoseEst; imu: Imu;
  blocked: boolean; contactSide: number; tipped: boolean; fallen: boolean; stuck: boolean; battery: number;
}
export interface FwOut { v: number; w: number; lamp: boolean; right: boolean; packets: Packet[] }

const SEG = 0.06, SCAN_TIME = 0.6, TURN_RATE = 0.5, TURN_TIME = 0.5, GOAL_TOL = 0.05;
export function kindsText(k: number): string {
  const a: string[] = []; if (k & HZ_DROP) a.push("drop-off"); if (k & HZ_ROCK) a.push("rock or hole"); if (k & HZ_SLOPE) a.push("steep slope");
  return a.join(", ") || "none";
}

export class Firmware {
  mode: Mode = "pilot"; risk = 1; override = false; photoBusy = false;
  selfRecover = true;                       // the operator's permission to back up, turn and try again after a contact (Sojourner had this option)
  goals: { x: number; y: number }[] = [];
  nav: "idle" | "scan" | "drive" | "turn" | "align" | "backup" = "idle";
  private drive = { v: 0, w: 0 }; private lampCmd = false; private rightCmd = false;
  private frame: { t: number; ranges: Float32Array; hazard: Hazard } | null = null;
  private prevAhead: Hazard["ahead"] | null = null; private conf: Hazard["ahead"] | null = null;      // conf: the hazards confirmed over two frames
  private stateT = 0; private scanStart = 0; private turnDir = 0; private turnAccum = 0; private exitSegs = 0; private straight = false; private margin = false;
  private recoveries = 0; private recoverT = 0; private recoverDir = 1;
  private telTimer = 0; private stallT = 0; private safetyOn = false; private events: string[] = [];
  private t = 0;

  setDrive(v: number, w: number) { this.drive = { v: clamp(v, -1, 1), w: clamp(w, -1, 1) }; }
  setMode(m: Mode) { if (m !== this.mode) { this.mode = m; this.nav = "idle"; this.stateT = 0; this.turnDir = 0; this.exitSegs = 0; this.say(`mode ${m}`); } }
  setRisk(r: number) { this.risk = clamp(Math.round(r), 0, RISK.length - 1); this.say(`risk level ${RISK[this.risk].name}`); }
  setGoals(g: { x: number; y: number }[]) { this.goals = g; if (!g.length) this.nav = "idle"; }
  setLamp(on: boolean) { this.lampCmd = on; }
  setSelfRecover(b: boolean) { this.selfRecover = b; this.say(`self-recovery ${b ? "permitted" : "not permitted"}`); }
  right() { this.rightCmd = true; }
  say(text: string) { this.events.push(text); }
  abort(reason: string) { this.goals = []; this.nav = "idle"; this.turnDir = 0; this.exitSegs = 0; this.margin = false; this.say(`ABORT: ${reason}`); }

  tick(inp: FwIn): FwOut {
    this.t = inp.t;
    const out: FwOut = { v: 0, w: 0, lamp: this.lampCmd, right: false, packets: [] };
    if (inp.tof) {
      const look = this.mode === "pilot" ? LOOK_PILOT : LOOK_MISSION;
      this.frame = { t: inp.t, ranges: inp.tof, hazard: analyze(inp.tof, this.risk, look) };
      this.conf = this.prevAhead ? confirmAhead(this.frame.hazard.ahead, this.prevAhead) : { ...this.frame.hazard.ahead, left: false, center: false, right: false, any: false, kinds: 0 };
      this.prevAhead = this.frame.hazard.ahead;
    }
    if (this.rightCmd) { out.right = true; this.rightCmd = false; }
    const th = RISK[this.risk];
    const tilt = Math.max(Math.abs(inp.imu.pitch), Math.abs(inp.imu.roll));
    this.stallT = inp.blocked ? this.stallT + inp.dt : 0;
    if (inp.fallen || inp.tipped || inp.stuck) { if (this.nav !== "idle" || this.goals.length) this.abort(inp.fallen ? "fallen" : inp.stuck ? "stuck in a hole" : "tipped over"); }
    else if (this.mode === "pilot") this.pilot(out, tilt > th.tilt);
    else this.mission(out, inp, tilt > th.tilt);
    // telemetry task: the newest range frame at the telemetry rate (slower while a photograph is transferring)
    this.telTimer += inp.dt;
    const hz = this.photoBusy ? LINK.hzPhoto : LINK.hzNormal;
    if (this.frame && this.telTimer >= 1 / hz) {
      this.telTimer = 0;
      out.packets.push({ kind: "tof", t: inp.t, ranges: this.frame.ranges, haz: this.frame.hazard.flags, pose: { ...inp.pose }, imu: { ...inp.imu },
        battery: inp.battery, mode: this.mode, risk: this.risk, nav: this.nav, bytes: LINK.tofBytes + LINK.poseBytes });
    }
    for (const e of this.events) out.packets.push({ kind: "event", t: inp.t, text: e, bytes: 8 + e.length });
    this.events = [];
    return out;
  }

  private pilot(out: FwOut, tiltBad: boolean) {
    let v = this.drive.v * ROVER.maxSpeed; const w = this.drive.w * ROVER.maxTurn;
    const hz = this.conf;
    const stop = !this.override && v > 0 && ((hz && hz.center) || tiltBad);
    if (stop) { if (!this.safetyOn) { this.safetyOn = true; this.say(`SAFETY STOP: ${hz && hz.center ? kindsText(hz.kinds) : "tilt"}`); } v = 0; }
    else this.safetyOn = false;
    out.v = v; out.w = w;
  }

  private mission(out: FwOut, inp: FwIn, tiltBad: boolean) {
    if (!this.goals.length) { this.nav = "idle"; return; }
    if (tiltBad) { this.abort(`tilt ${(Math.max(Math.abs(inp.imu.pitch), Math.abs(inp.imu.roll)) * 57.3).toFixed(0)} degrees beyond the limit`); return; }
    this.recoverT += inp.dt; if (this.recoverT > 40) this.recoveries = 0;
    if (this.stallT > 0.3 && this.nav !== "backup") {
      if (this.selfRecover && this.recoveries < 4) {                // back up, then turn away from the side that touched, and carry on
        this.recoveries++; this.recoverT = 0; this.stallT = 0;
        this.recoverDir = inp.contactSide !== 0 ? -inp.contactSide : (this.recoveries % 2 ? 1 : -1);
        this.nav = "backup"; this.stateT = 0; this.say("CONTACT: backing up");
      } else { this.abort("contact or stall"); return; }
    }
    if (inp.battery < 0.08) { this.abort("low battery"); return; }
    const g = this.goals[0], e = inp.pose;
    const dx = g.x - e.x, dy = g.y - e.y, dist = Math.hypot(dx, dy), err = wrap(Math.atan2(dy, dx) - e.theta);
    if (dist < GOAL_TOL) { this.goals.shift(); this.say("GOAL REACHED"); this.nav = "scan"; this.stateT = 0; this.scanStart = this.t; this.turnDir = 0; return; }
    if (this.nav === "idle") { this.nav = "scan"; this.stateT = 0; this.scanStart = this.t; }
    this.stateT += inp.dt;
    if (this.nav === "scan") {                                   // stopped: wait for a frame measured at rest, then look for hazards
      if (this.stateT >= SCAN_TIME && this.frame && this.frame.t > this.scanStart + 0.1) {
        const h = { ahead: this.conf ?? this.frame.hazard.ahead };
        if (h.ahead.any) {
          if (this.turnDir === 0) this.turnDir = h.ahead.nl > h.ahead.nr ? -1 : h.ahead.nr > h.ahead.nl ? 1 : err >= 0 ? 1 : -1;     // away from the side with more hazard, else toward the goal
          this.nav = "turn"; this.stateT = 0;
        } else {
          if (this.turnDir !== 0 && !this.margin) { this.margin = true; this.nav = "turn"; this.stateT = 0; return; }              // one more half turn for clearance
          if (this.turnDir !== 0) { this.turnDir = 0; this.margin = false; this.exitSegs = 3; this.turnAccum = 0; }
          this.straight = this.exitSegs > 0; if (this.exitSegs > 0) this.exitSegs--;
          if (!this.straight && Math.abs(err) > 0.30) { this.nav = "align"; this.stateT = 0; }                                      // face the goal first, then drive straight
          else { this.nav = "drive"; this.stateT = 0; }
        }
      }
    } else if (this.nav === "turn") {                            // turn in place away from the hazard, then scan again
      out.w = this.turnDir * TURN_RATE; this.turnAccum += TURN_RATE * inp.dt;
      if (this.stateT >= (this.margin ? TURN_TIME / 2 : TURN_TIME)) { this.nav = "scan"; this.stateT = 0; this.scanStart = this.t; }
      if (this.turnAccum > 6.3) this.abort("boxed in");
    } else if (this.nav === "backup") {
      out.v = -ROVER.maxSpeed;
      if (this.stateT >= 1.5) { this.turnDir = this.recoverDir; this.turnAccum = 0; this.margin = false; this.nav = "turn"; this.stateT = 0; }
    } else if (this.nav === "align") {                           // turn in place toward the goal
      out.w = clamp(2 * err, -TURN_RATE, TURN_RATE);
      if (Math.abs(err) < 0.12 || this.stateT > 6) { this.nav = "scan"; this.stateT = 0; this.scanStart = this.t; }
    } else if (this.nav === "drive") {                           // a short straight segment toward the goal (arcs would swing the body into a rock's corner)
      out.v = ROVER.maxSpeed; out.w = 0;
      if (this.stateT >= SEG / ROVER.maxSpeed) { this.nav = "scan"; this.stateT = 0; this.scanStart = this.t; }
    }
  }
}
