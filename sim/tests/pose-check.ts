// Pose error of the dead-reckoned estimate along the autopilot's route, with and without the ultrasonic beacon fix (npm run pose).
import { Sim } from "../src/sim";
const goals = [{ x: -0.2, y: -0.35 }, { x: 0.2, y: 0.0 }, { x: 0.6, y: 0.3 }];
function run(q: number, seed: number, beacons: boolean, calibrate: boolean, lh = false, detect = 1) {
  const s = new Sim(seed); while (s.slamQuality !== q) s.cycleSlam();
  s.odo.beacons = beacons; s.odo.calibrate = calibrate; s.odo.lighthouse = lh; s.odo.lhDetect = detect;
  s.setRisk(1); s.setMode("mission"); s.setGoals(goals);
  let t = 0, se = 0, n = 0, mx = 0;
  while (t < 600 && !s.rover.fallen && !s.rover.stuck && !s.rover.tipped) {
    s.step(); t += 0.02;
    const e = Math.hypot(s.odo.est.x - s.rover.x, s.odo.est.y - s.rover.y); se += e * e; n++; mx = Math.max(mx, e);
    if (s.fw.goals.length === 0 && t > 5) break;
  }
  return { rms: Math.sqrt(se / n), mx, t };
}
const N = 6;
for (const q of [1]) for (const [b, c, lh, det] of [[false, false, false, 1], [false, true, false, 1], [true, true, false, 1], [false, false, true, 1], [false, false, true, 0.5], [false, false, true, 0.2]] as const) {
  let r = 0, m = 0, tt = 0;
  for (let seed = 1; seed <= N; seed++) { const o = run(q, seed, b, c, lh, det); r += o.rms; m += o.mx; tt += o.t; }
  console.log(`x${q}  beacons ${b ? "on " : "off"} calibration ${c ? "on " : "off"} lighthouse ${lh ? "on, detect " + det : "off"}: mean RMS position error ${(r / N * 100).toFixed(1)} cm, mean worst ${(m / N * 100).toFixed(1)} cm (${N} seeds, mean ${(tt / N).toFixed(0)} s)`);
}
