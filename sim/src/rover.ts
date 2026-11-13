// The true rover: pose, steps, slopes, a pit that traps, falling, tipping, righting, and the battery. No physics engine in the slice.
import { ROVER, POWER } from "./constants";
import { World } from "./world";
import { clamp } from "./util";

export interface Cmd { v: number; w: number; lamp: boolean; right: boolean; cameraOn: boolean; radioUtil: number }

export class Rover {
  x = 0; y = 0; theta = 0; z = 0; pitch = 0; roll = 0;
  vel = 0; omega = 0;
  tipped = false; fallen = false; stuck = false; blocked = false; dead = false; righting = 0;
  contactSide = 0;                       // -1 right, 0 centre, +1 left of the heading (which half of the footprint touched), like a pair of bump switches
  energyWh = POWER.batteryWh; loadW = 0; solarW = 0; travelled = 0;
  constructor(public world: World) { this.reset(); }

  reset(): void {
    const s = this.world.start;
    this.x = s.x; this.y = s.y; this.theta = s.theta; this.z = this.world.heightAt(s.x, s.y);
    this.vel = 0; this.omega = 0; this.tipped = false; this.fallen = false; this.stuck = false; this.blocked = false;
    this.dead = false; this.righting = 0; this.energyWh = POWER.batteryWh; this.travelled = 0;
    this.attitude();
  }

  /** truth pitch (nose up positive) and roll (left side up positive) from four contact heights */
  attitude(): void {
    const f = 0.06, c = Math.cos(this.theta), s = Math.sin(this.theta), w = this.world;
    const clampH = (v: number) => (v < -0.2 ? this.z : v);
    const hF = clampH(w.heightAt(this.x + f * c, this.y + f * s)), hB = clampH(w.heightAt(this.x - f * c, this.y - f * s));
    const hL = clampH(w.heightAt(this.x - f * s, this.y + f * c)), hR = clampH(w.heightAt(this.x + f * s, this.y - f * c));
    this.pitch = Math.atan2(hF - hB, 2 * f);
    this.roll = Math.atan2(hL - hR, 2 * f);
  }

  step(dt: number, cmd: Cmd): void {
    const wd = this.world;
    this.blocked = false; this.contactSide = 0;
    let v = 0, w = 0;
    if (!this.dead && !this.fallen) {
      if (this.righting > 0) {
        this.righting -= dt;
        if (this.righting <= 0) { this.righting = 0; this.tipped = false; }
      } else if (cmd.right && this.tipped) this.righting = ROVER.rightTime;
      else if (!this.tipped) { v = clamp(cmd.v, -ROVER.maxSpeed, ROVER.maxSpeed); w = clamp(cmd.w, -ROVER.maxTurn, ROVER.maxTurn); }
    }
    if (this.stuck && v !== 0) { v = 0; this.blocked = true; }          // a pit holds the rover until it is retrieved
    if (v !== 0 || w !== 0) {
      this.theta += w * dt;
      if (v !== 0) {
        const dir = v > 0 ? 1 : -1, base = this.theta + (dir > 0 ? 0 : Math.PI);
        let step = -Infinity, worstA = 0;                           // the tallest step across the leading half of the circular footprint
        for (let a = -3.5; a <= 3.5; a += 1) {
          const ang = base + a * (Math.PI / 8) * 1.0, ux = Math.cos(ang), uy = Math.sin(ang);
          const outer = wd.heightAt(this.x + ux * (ROVER.radius - 0.005), this.y + uy * (ROVER.radius - 0.005));
          const inner = wd.heightAt(this.x + ux * (ROVER.radius - 0.035), this.y + uy * (ROVER.radius - 0.035));
          if (outer - inner > step) { step = outer - inner; worstA = a; }
        }
        if (step > ROVER.climbMax) { v = 0; this.blocked = true; this.contactSide = Math.abs(worstA) < 1 ? 0 : (worstA > 0 ? 1 : -1) * (dir > 0 ? 1 : -1); }
        else if (step > ROVER.climbSlow) v *= 0.5;
        this.x += Math.cos(this.theta) * v * dt; this.y += Math.sin(this.theta) * v * dt;
        this.travelled += Math.abs(v) * dt;
        const hNew = wd.heightAt(this.x, this.y), drop = this.z - hNew;
        if (drop > ROVER.dropFall) this.fallen = true;
        else if (drop > ROVER.dropOk) { this.stuck = true; this.z = hNew; }
        else this.z = hNew;
        if (!this.fallen && wd.slopeAt(this.x, this.y) > ROVER.tipSlope) this.tipped = true;
      }
    }
    this.vel = v; this.omega = w;
    this.attitude();
    // battery: loads from hardware/body/power_budget.py; the cells work either way up, so a tipped rover still charges
    const frac = Math.min(1, Math.abs(v) / ROVER.maxSpeed + Math.abs(w) / ROVER.maxTurn);
    if (this.dead) this.loadW = 0;
    else this.loadW = POWER.idle + POWER.hold + POWER.wheels * frac + (cmd.lamp ? POWER.lamp : 0) + (cmd.cameraOn ? POWER.camera : 0)
      + POWER.radioTx * clamp(cmd.radioUtil, 0, 1) + (this.righting > 0 ? POWER.righting : 0);
    this.solarW = this.fallen ? 0 : POWER.sun * wd.inSun(this.x, this.y);
    this.energyWh = clamp(this.energyWh + ((this.solarW - this.loadW) * dt) / 3600, 0, POWER.batteryWh);
    if (!this.dead && this.energyWh <= 0) this.dead = true;
    else if (this.dead && this.energyWh >= POWER.wake * POWER.batteryWh) this.dead = false;
  }
  get batteryFrac(): number { return this.energyWh / POWER.batteryWh; }
}
