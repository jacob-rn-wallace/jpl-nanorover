// How reliably is a pit found, as a function of its depth, the distance to it and the drop threshold? (the rule that decides is `analyze` in firmware.ts)
// For each drop threshold at risk 2 (normal): the fraction of 50 frames, confirmed over two frames, in which a hazard lies ahead (rock or drop kind), for a pit of each depth, the rover facing it from several distances.
// Also the false-alarm rate on a flat floor with that threshold (400 frames). Usage: npm run pit
import { Sim } from "../src/sim";
import { tofMeasure } from "../src/sensors";
import { analyze, confirmAhead, HZ_DROP, HZ_ROCK, LOOK_MISSION } from "../src/firmware";
import { RISK } from "../src/constants";
import { Rng } from "../src/util";

function place(s: Sim, x: number, y: number, theta: number) { s.rover.x = x; s.rover.y = y; s.rover.theta = theta; s.rover.z = s.world.heightAt(x, y); s.rover.attitude(); s.odo.reset(s.rover); }
function rate(s: Sim, n: number, risk: number, seed = 5, kinds = HZ_DROP | HZ_ROCK) {
  const rng = new Rng(seed); let hits = 0, prev = analyze(tofMeasure(s.world, s.rover, rng), risk, LOOK_MISSION).ahead;
  for (let i = 0; i < n; i++) { const cur = analyze(tofMeasure(s.world, s.rover, rng), risk, LOOK_MISSION).ahead, c = confirmAhead(cur, prev); prev = cur; if (c.kinds & kinds) hits++; }
  return hits / n;
}
const depths = [0.03, 0.04, 0.05, 0.07], dists = [0.08, 0.12, 0.16, 0.20, 0.25, 0.30];
const orig = RISK[1].drop;
for (const th of [0.045, 0.040, 0.035, 0.030]) {
  RISK[1].drop = th;
  console.log(`\nrisk 2, drop threshold ${(th * 100).toFixed(1)} cm   (rows: pit depth; columns: rover centre ${dists.map(d => (d * 100).toFixed(0)).join(", ")} cm from the pit's edge; % of frames flagged)`);
  for (const dp of depths) {
    const row = dists.map(d => {
      let sum = 0; const seeds = [5, 6, 7];
      for (const sd of seeds) { const s = new Sim(1); s.world.pits[0].depth = dp; place(s, -0.30 + d, -0.05, Math.PI); sum += rate(s, 50, 1, sd); }
      return (sum / seeds.length * 100).toFixed(0).padStart(3);
    });
    console.log(`  ${(dp * 100).toFixed(0)} cm pit:  ${row.join("  ")}`);
  }
  const s = new Sim(1); place(s, -0.6, -0.25, Math.PI / 2);
  console.log(`  false alarms on a flat floor: ${(rate(s, 400, 1) * 100).toFixed(1)}% of frames`);
}
RISK[1].drop = orig;
