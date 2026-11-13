// Logic checks with no browser: sensor geometry, hazard detection, a mission run, the pilot safety stop, the link, the energy balance.
import { Sim } from "../src/sim";
import { tofMeasure, tofDirs, ZONES } from "../src/sensors";
import { analyze, confirmAhead, HZ_DROP, HZ_ROCK, HZ_SLOPE, LOOK_MISSION, LOOK_PILOT } from "../src/firmware";
import { ROVER, POWER, LINK, PHOTO } from "../src/constants";
import { Rng } from "../src/util";

let fails = 0;
function check(name: string, ok: boolean, detail = "") { console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? "   " + detail : ""}`); if (!ok) fails++; }
function place(s: Sim, x: number, y: number, theta: number) {
  s.rover.x = x; s.rover.y = y; s.rover.theta = theta; s.rover.z = s.world.heightAt(x, y); s.rover.attitude(); s.odo.reset(s.rover);
}
const frame = (s: Sim, rng: Rng) => tofMeasure(s.world, s.rover, rng);
function frames(s: Sim, n: number, risk: number, look: number, seed = 5) {
  // frames in which a hazard lies AHEAD (inside the lookahead and the corridor) and is confirmed in two consecutive frames, by kind
  const rng = new Rng(seed); const hits = { drop: 0, rock: 0, slope: 0, any: 0 };
  let prev = analyze(frame(s, rng), risk, look).ahead;
  for (let i = 0; i < n; i++) {
    const cur = analyze(frame(s, rng), risk, look).ahead, c = confirmAhead(cur, prev); prev = cur;
    if (c.any) hits.any++; if (c.kinds & HZ_DROP) hits.drop++; if (c.kinds & HZ_ROCK) hits.rock++; if (c.kinds & HZ_SLOPE) hits.slope++;
  }
  return hits;
}

// 1. sensor against the analytic range on a flat floor
{
  const s = new Sim(1); place(s, -0.6, -0.25, Math.PI / 2); const d = tofDirs(), mean = new Float64Array(ZONES), N = 300, rng = new Rng(3);
  for (let i = 0; i < N; i++) { const f = frame(s, rng); for (let k = 0; k < ZONES; k++) mean[k] += (f[k] > 0 ? f[k] : NaN) / N; }
  let worst = 0, valid = 0;
  for (let k = 0; k < ZONES; k++) { const dz = d[3 * k + 2]; if (dz >= 0) continue; const exp = ROVER.mountH / -dz; if (exp > 2) continue; valid++; if (Number.isFinite(mean[k])) worst = Math.max(worst, Math.abs(mean[k] - exp)); }
  check("sensor: mean range on a flat floor matches the geometry", worst < 0.004, `worst error ${(worst * 1000).toFixed(1)} mm over ${valid} zones`);
  const top = ROVER.mountH / -d[2];
  check("sensor: the top row reaches the floor within range", top < 2.0, `top-row range ${(top * 100).toFixed(0)} cm`);
}
// 2. no false hazards on a flat floor
for (let r = 0; r < 3; r++) {
  const s = new Sim(1); place(s, -0.6, -0.25, Math.PI / 2);
  const h = frames(s, 400, r, LOOK_MISSION);
  check(`no false hazards ahead on a flat floor, risk ${r + 1}`, h.any === 0, `${h.any} of 400 frames flagged`);
}
// 3. the table edge, a rock, a pit, the ramps
{
  const s = new Sim(1);
  place(s, -0.5, -0.35, -Math.PI / 2); let h = frames(s, 50, 1, LOOK_MISSION);
  check("drop-off: the table edge 25 cm ahead is flagged (mission lookahead)", h.drop >= 49, `${h.drop} of 50`);
  place(s, -0.6, -0.10, -Math.PI / 2); h = frames(s, 50, 1, LOOK_MISSION);
  check("drop-off: nothing ahead with the edge 50 cm away", h.any === 0, `${h.any} of 50`);
  place(s, -0.5, -0.45, -Math.PI / 2); h = frames(s, 50, 1, LOOK_PILOT);
  check("drop-off: the edge 15 cm ahead is flagged (pilot lookahead)", h.drop >= 49, `${h.drop} of 50`);
  place(s, -0.12, 0.01, 0); h = frames(s, 50, 1, LOOK_MISSION);
  check("rock: the 5 cm rock ahead is flagged at risk 2", h.rock >= 49, `${h.rock} of 50`);
  place(s, -0.12, 0.01, 0); h = frames(s, 50, 2, LOOK_MISSION);
  check("rock: the 5 cm rock ahead is flagged at risk 3 (bold, threshold 4 cm)", h.rock >= 45, `${h.rock} of 50`);
  place(s, -0.20, -0.05, Math.PI); h = frames(s, 50, 1, LOOK_MISSION);
  check("pit: the 5 cm pit ahead is flagged at risk 2", h.rock + h.drop >= 45, `${h.rock + h.drop} of 50 (confirmed over two frames; a hazard is found within a few frames)`);
  place(s, 0.45, -0.175, 0); h = frames(s, 50, 0, LOOK_MISSION);
  check("slope: the steep ramp ahead is flagged at risk 1", h.any >= 45, `${h.any} of 50 (slope ${h.slope}, rock ${h.rock})`);
  place(s, 0.15, 0.23, 0); h = frames(s, 100, 1, LOOK_MISSION);
  check("slope: the gentle ramp is not flagged at risk 2", h.any === 0, `${h.any} of 100`);
  place(s, -0.45, -0.26, 0); h = frames(s, 100, 1, LOOK_MISSION);
  check("rock: the 2 cm rock A is not a hazard at risk 2", h.any === 0, `${h.any} of 100`);
}
// 4. a mission run across the rocks, from several random seeds, at risk 2 (index 1)
{
  const times: number[] = [], dists: number[] = []; let ok = 0; const notes: string[] = [];
  for (const seed of [1, 2, 3, 4, 5, 6]) {
    const s = new Sim(seed); s.setRisk(1); s.setMode("mission"); s.setGoals([{ x: 0.52, y: 0.30 }]);
    let reached = false, t = 0;
    while (t < 1500 && !s.rover.fallen && !s.rover.tipped && !s.rover.stuck) {
      s.step(); t += 0.02;
      if (s.map.log.some(l => l.includes("GOAL REACHED"))) { reached = true; break; }
      if (s.map.log.some(l => l.includes("ABORT"))) { notes.push(`seed ${seed}: ${s.map.log.filter(l => /ABORT/.test(l)).join("")}`); break; }
    }
    if (reached) { ok++; times.push(t); dists.push(s.rover.travelled); }
  }
  const mean = (a: number[]) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN);
  check("mission: reaches the sun patch across the rocks from 6 of 6 seeds, risk 2", ok === 6, `${ok} of 6; mean ${mean(times).toFixed(0)} s, mean path ${mean(dists).toFixed(2)} m (straight line 1.4 m) ${notes.join("; ")}`);
}
// 5. the pilot safety stop at the table edge
{
  const a = new Sim(1); place(a, -0.2, -0.30, -Math.PI / 2); a.setDrive(1, 0);
  for (let i = 0; i < 6000 / 1; i++) a.step();
  check("pilot: the safety stop holds the rover before the table edge", !a.rover.fallen && a.map.log.some(l => l.includes("SAFETY STOP")), `y=${a.rover.y.toFixed(3)} (edge at -0.600)`);
  const b = new Sim(1); place(b, -0.2, -0.30, -Math.PI / 2); b.setOverride(true); b.setDrive(1, 0);
  for (let i = 0; i < 6000; i++) b.step();
  check("pilot: with the override the rover goes over the edge", b.rover.fallen, `fallen=${b.rover.fallen}`);
}
// 6. the link: photo transfer time and the telemetry slow-down
{
  const s = new Sim(1); place(s, -0.6, 0.0, 0); s.setLinkRate(1);
  for (let i = 0; i < 500; i++) s.step();                              // 10 s of telemetry alone
  const f0 = s.map.frames; for (let i = 0; i < 500; i++) s.step(); const rate0 = (s.map.frames - f0) / 10;
  s.requestPhoto("M"); const tReq = s.t; const f1 = s.map.frames; let arrived = -1, f2 = f1, tCap = 0;
  for (let i = 0; i < 6000 && arrived < 0; i++) { s.step(); if (s.link.photoBusy && tCap === 0) { tCap = s.t; f2 = s.map.frames; } if (s.map.photos.length) arrived = s.t - tReq; }
  const rateDuring = (s.map.frames - f2) / Math.max(1, arrived - (tCap - tReq));
  const expect = (PHOTO.sizes.M[0] * PHOTO.sizes.M[1] * PHOTO.bppLit) / 8;
  check("link: telemetry runs at about 5 Hz before the photo", rate0 > 3 && rate0 < 5.5, `${rate0.toFixed(1)} frames/s at 9600 bit/s (a 160-byte frame at 5 Hz is ${(800 / (9600 / 8 * 0.9) * 100).toFixed(0)}% of the link)`);
  check("link: a 640 x 480 photo (about 25 KB) arrives in 25 to 55 s at 9600 bit/s", arrived > 25 && arrived < 55, `${arrived.toFixed(1)} s for ${(expect / 1000).toFixed(0)} KB`);
  check("link: the map slows to about 1 Hz while the photo transfers", rateDuring < 1.6 && rateDuring > 0.5, `${rateDuring.toFixed(2)} frames/s`);
}
// 7. the energy balance
{
  const s = new Sim(1); place(s, -0.6, 0.0, 0); s.rover.energyWh = 1.0;
  for (let i = 0; i < 3000; i++) s.step();                              // 60 s idle in the dark
  const used = 1.0 - s.rover.energyWh;
  check("energy: idling in the dark costs about 2 W", used > 0.03 && used < 0.045, `${(used * 1000).toFixed(1)} mWh in 60 s = ${(used * 3600 / 60).toFixed(2)} W`);
  const u = new Sim(1); place(u, u.world.sun.x, u.world.sun.y, 0); u.rover.energyWh = 1.0;
  for (let i = 0; i < 3000; i++) u.step();
  check("energy: idling in the sunlit patch gains charge", u.rover.energyWh > 1.0, `${((u.rover.energyWh - 1.0) * 1000).toFixed(1)} mWh in 60 s`);
}
console.log(fails ? `\n${fails} check(s) FAILED` : "\nall checks passed");
process.exit(fails ? 1 : 0);
