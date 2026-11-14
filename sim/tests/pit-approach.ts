// Does the rover stop in front of a 5 cm pit when it drives straight at it in mission mode? (the dynamics, not a single frame)
// For each seed: start 30 cm from the pit facing it, goal beyond it, risk 2 (normal); count the runs in which the rover's body ever goes into the pit.
import { Sim } from "../src/sim";
import { RISK } from "../src/constants";
function run(seed: number, drop: number, depth = 0.05) {
  RISK[1].drop = drop;
  const s = new Sim(seed); s.world.pits[0].depth = depth;
  s.rover.x = -0.05; s.rover.y = -0.05; s.rover.theta = Math.PI; s.rover.z = s.world.heightAt(s.rover.x, s.rover.y); s.rover.attitude(); s.odo.reset(s.rover);
  s.setRisk(1); s.setMode("mission"); s.setGoals([{ x: -0.7, y: -0.05 }]);
  let t = 0, entered = false, minDist = 1; const pit = s.world.pits[0];
  while (t < 240 && !s.rover.fallen && !s.rover.stuck && !s.rover.tipped) {
    s.step(); t += 0.02;
    const dx = Math.max(pit.x0 - s.rover.x, 0, s.rover.x - pit.x1), dy = Math.max(pit.y0 - s.rover.y, 0, s.rover.y - pit.y1);
    minDist = Math.min(minDist, Math.hypot(dx, dy)); if (dx === 0 && dy === 0) entered = true;     // the rover's centre over the pit: it went in
    if (s.fw.goals.length === 0 && t > 5) break;
  }
  return { entered, minDist, fallen: s.rover.fallen, t };
}
const N = 12;
for (const drop of [0.045, 0.035]) for (const depth of [0.05, 0.04]) {
  let ent = 0, md = 1, mn = 0;
  for (let seed = 1; seed <= N; seed++) { const r = run(seed, drop, depth); if (r.entered) ent++; md = Math.min(md, r.minDist); mn += r.minDist / N; }
  console.log(`drop threshold ${(drop * 100).toFixed(1)} cm, ${(depth * 100).toFixed(0)} cm pit: the rover went into the pit in ${ent} of ${N} runs; its centre came as close as ${(md * 100).toFixed(0)} cm (mean ${(mn * 100).toFixed(0)} cm) to the pit`);
}
