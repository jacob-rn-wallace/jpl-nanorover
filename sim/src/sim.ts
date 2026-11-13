// The whole loop without a screen: world, true rover, sensors, firmware, radio, the console's model, and the operator's commands (which also travel with a latency).
import { DT, LINK, PHOTO, TOF, ROVER, POWER, SLAM_QUALITY } from "./constants";
import { Rng } from "./util";
import { World } from "./world";
import { Rover } from "./rover";
import { Odometry, tofMeasure } from "./sensors";
import { Firmware, Mode } from "./firmware";
import { Link } from "./link";
import { ConsoleMap, PhotoPayload } from "./consoleMap";

export type CaptureHook = (size: string, w: number, h: number, lampOn: boolean) => ImageData | null;

export class Sim {
  world = new World(); rover: Rover; rng: Rng; odo: Odometry; fw = new Firmware(); link = new Link(); map = new ConsoleMap();
  t = 0; timeScale = 1;
  captureHook: CaptureHook | null = null;
  private cmds: { at: number; fn: () => void }[] = [];
  private tofTimer = 0;
  private job: { size: string; t0: number } | null = null;
  private lampJob = false; private cameraJob = false;
  private lampManual = false; private slamIdx = 1;
  stats = { photos: 0, startedAt: 0, finishedAt: -1 };

  constructor(seed = 1) {
    this.rng = new Rng(seed); this.rover = new Rover(this.world); this.odo = new Odometry(this.rng);
    this.reset();
  }
  reset(): void {
    this.rover.reset(); this.odo.quality = SLAM_QUALITY[this.slamIdx]; this.odo.reset(this.rover);
    this.fw = new Firmware(); this.link = new Link(); this.map = new ConsoleMap(); this.cmds = []; this.tofTimer = 0; this.job = null;
    this.lampJob = false; this.cameraJob = false; this.lampManual = false; this.t = 0; this.stats = { photos: 0, startedAt: 0, finishedAt: -1 };
    this.map.say(0, "rover started; photograph the three markers");
  }

  // ---- the operator's commands: they reach the firmware after the uplink latency ----
  private cmd(fn: () => void) { this.cmds.push({ at: this.t + this.link.latency, fn }); }
  setMode(m: Mode) { this.cmd(() => this.fw.setMode(m)); }
  setRisk(r: number) { this.cmd(() => this.fw.setRisk(r)); }
  setDrive(v: number, w: number) { this.cmd(() => this.fw.setDrive(v, w)); }
  setOverride(b: boolean) { this.cmd(() => { this.fw.override = b; }); }
  setSelfRecover(b: boolean) { this.cmd(() => this.fw.setSelfRecover(b)); }
  setGoals(g: { x: number; y: number }[]) { this.map.goals = g.map(p => ({ ...p })); this.cmd(() => this.fw.setGoals(g.map(p => ({ ...p })))); }
  toggleLamp() { this.lampManual = !this.lampManual; const v = this.lampManual; this.cmd(() => this.fw.setLamp(v)); }
  right() { this.cmd(() => this.fw.right()); }
  setLinkRate(i: number) { this.link.rate = LINK.rates[Math.max(0, Math.min(LINK.rates.length - 1, i))]; }
  cycleSlam() { this.slamIdx = (this.slamIdx + 1) % SLAM_QUALITY.length; this.odo.quality = SLAM_QUALITY[this.slamIdx]; this.odo.reset(this.rover); this.map.say(this.t, `dead-reckoning error x${SLAM_QUALITY[this.slamIdx]}`); }
  get slamQuality(): number { return SLAM_QUALITY[this.slamIdx]; }
  requestPhoto(size: string) {
    this.cmd(() => {
      if (this.job || this.link.photoBusy) { this.fw.say("photo refused: busy"); return; }
      if (this.rover.dead) return;
      this.job = { size, t0: this.t };
    });
  }
  get photoBusy(): boolean { return this.job !== null || this.link.photoBusy; }
  get lampIsOn(): boolean { return this.lampManual || this.lampJob; }
  get override(): boolean { return this.fw.override; }

  /** markers in the camera's view and lit, from the true state (the rover cannot tell; the photograph shows them) */
  detectMarkers(lampOn: boolean): { found: string[]; dists: Record<string, number> } {
    const r = this.rover, found: string[] = [], dists: Record<string, number> = {};
    const cx = r.x + Math.cos(r.theta) * ROVER.mountFwd, cy = r.y + Math.sin(r.theta) * ROVER.mountFwd, cz = r.z + 0.055;
    for (const m of this.world.markers) {
      const dx = m.x - cx, dy = m.y - cy, d = Math.hypot(dx, dy);
      if (d < 0.08 || d > PHOTO.range) continue;
      const az = Math.atan2(dy, dx) - r.theta, azw = Math.atan2(Math.sin(az), Math.cos(az));
      if (Math.abs(azw) > PHOTO.fovH / 2) continue;
      const el = Math.atan2(this.world.heightAt(m.x, m.y) + 0.03 - cz, d) - r.pitch;
      if (Math.abs(el) > PHOTO.fovV / 2) continue;
      const dir: [number, number, number] = [dx / d, dy / d, (this.world.heightAt(m.x, m.y) + 0.03 - cz) / d];
      const hit = this.world.rayHit([cx, cy, cz], dir, d - 0.02);
      if (hit !== null) continue;                                  // something in the way
      const lit = (lampOn && d < 0.8) || this.world.inSun(m.x, m.y) > 0.3;
      if (!lit) continue;
      found.push(m.id); dists[m.id] = d;
    }
    return { found, dists };
  }

  step(dt = DT): void {
    while (this.cmds.length && this.cmds[0].at <= this.t) this.cmds.shift()!.fn();
    const r = this.rover;
    this.tofTimer += dt;
    let tof: Float32Array | null = null;
    if (this.tofTimer >= 1 / TOF.hz) { this.tofTimer = 0; if (!r.dead) tof = tofMeasure(this.world, r, this.rng); }
    this.fw.photoBusy = this.photoBusy;
    let v = 0, w = 0, lamp = false, right = false;
    if (!r.dead) {
      const o = this.fw.tick({ t: this.t, dt, tof, pose: this.odo.est, imu: this.odo.imu, blocked: r.blocked, contactSide: r.contactSide, tipped: r.tipped, fallen: r.fallen, stuck: r.stuck, battery: r.batteryFrac });
      v = o.v; w = o.w; lamp = o.lamp; right = o.right;
      for (const p of o.packets) this.link.send(p);
    }
    // photograph: the lamp and the camera are on for a second, then the frame is captured and transferred
    this.lampJob = false; this.cameraJob = false;
    if (this.job && !r.dead) {
      const el = this.t - this.job.t0;
      if (el < PHOTO.captureTime) { this.lampJob = true; this.cameraJob = true; }
      else {
        const [pw, ph] = PHOTO.sizes[this.job.size], lampOn = true, det = this.detectMarkers(lampOn);
        const lit = this.world.inSun(r.x, r.y) > 0.3 || lampOn;
        const image = this.captureHook ? this.captureHook(this.job.size, pw, ph, lampOn) : null;
        const bytes = Math.round((pw * ph * (lit ? PHOTO.bppLit : PHOTO.bppDark)) / 8);
        const payload: PhotoPayload = { size: this.job.size, w: pw, h: ph, image, lit, t: this.t, found: det.found, dists: det.dists, pose: { ...this.odo.est }, bytes };
        this.link.startPhoto(bytes, ph, payload); this.job = null; this.stats.photos++;
      }
    } else if (this.job && r.dead) this.job = null;
    r.step(dt, { v, w, lamp: lamp || this.lampJob, right, cameraOn: this.cameraJob, radioUtil: this.link.utilization });
    this.odo.step(r, dt);
    this.link.update(dt, this.t);
    const got = this.link.poll(this.t);
    for (const p of got.packets) this.map.ingest(p);
    for (const ph of got.photos) {
      this.map.addPhoto(ph as PhotoPayload, this.t);
      if (this.map.markers.size >= this.world.markers.length && this.stats.finishedAt < 0) { this.stats.finishedAt = this.t; this.map.say(this.t, `ALL MARKERS PHOTOGRAPHED in ${this.t.toFixed(0)} s`); }
    }
    this.t += dt;
  }
  /** advance by real time dt, scaled by the time warp */
  advance(realDt: number): void {
    let n = Math.min(Math.round((realDt * this.timeScale) / DT), 800);
    while (n-- > 0) this.step(DT);
  }
}
export { POWER };
