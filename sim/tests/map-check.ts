// How good is the operator's map? Run the autopilot along a route, then compare the console's map with the true world.
//   recall:    of the truly hazardous cells (rock >= 3 cm, pit, steep ramp, platform, beyond the table edge) within 30 cm of the path, how many does the map show as hazardous
//   precision: of the cells the map shows as hazardous, how many are truly hazardous
//   coverage:  of all cells within 25 cm of the path, how many has the map seen at all
//   height error: RMS of (map height - true height) over seen cells inside the table
import { Sim } from "../src/sim";

function run(quality: number, seed: number, goals: { x: number; y: number }[]) {
  const s = new Sim(seed);
  while (s.slamQuality !== quality) s.cycleSlam();
  s.setRisk(1); s.setMode("mission"); s.setGoals(goals);
  const path: { x: number; y: number }[] = []; let t = 0, k = 0;
  while (t < 900 && !s.rover.fallen && !s.rover.stuck && !s.rover.tipped) {
    s.step(); t += 0.02; if (++k % 25 === 0) path.push({ x: s.rover.x, y: s.rover.y });
    if (s.fw.goals.length === 0 && t > 5) break;
  }
  // let the last frames arrive
  for (let i = 0; i < 100; i++) s.step();
  const m = s.map, w = s.world;
  const near = (x: number, y: number, d: number) => path.some(p => Math.hypot(p.x - x, p.y - y) < d);
  let fpNear = 0, fpFar = 0, fpDrop = 0, fpRock = 0, fpSlope = 0, tp = 0, fp = 0, fn = 0, seen = 0, cover = 0, total = 0, se = 0, ne = 0;
  for (let j = 0; j < m.rows; j++) for (let i = 0; i < m.cols; i++) {
    const x = m.x0 + (i + 0.5) * m.res, y = m.y0 + (j + 0.5) * m.res, c = j * m.cols + i;
    const inside = Math.abs(x) <= w.w / 2 && Math.abs(y) <= w.d / 2;
    const h = w.heightAt(x, y);
    const truthHaz = !inside ? near(x, y, 0.3) : Math.abs(h) >= 0.03 || w.slopeAt(x, y, 0.03) > 0.45;
    const mapSeen = m.n[c] > 0;
    const mapHaz = mapSeen && (m.haz[c] !== 0 || Math.abs(m.z[c]) >= 0.03);
    if (near(x, y, 0.25)) { total++; if (mapSeen) cover++; }
    if (mapSeen && inside) { seen++; se += (m.z[c] - h) ** 2; ne++; }
    if (mapHaz && near(x, y, 0.3)) { if (truthHaz) tp++; else {
        fp++;
        let nearTruth = false;
        for (let dj = -3; dj <= 3 && !nearTruth; dj++) for (let di = -3; di <= 3; di++) { const xx = x + di * m.res, yy = y + dj * m.res; if (Math.abs(xx) <= w.w / 2 && Math.abs(yy) <= w.d / 2 && (Math.abs(w.heightAt(xx, yy)) >= 0.03 || w.slopeAt(xx, yy, 0.03) > 0.45)) { nearTruth = true; break; } }
        if (nearTruth) fpNear++; else fpFar++;
        if (!nearTruth) { if (m.haz[c] & 1) fpDrop++; if (m.haz[c] & 2) fpRock++; if (m.haz[c] & 4) fpSlope++; }
      } }
    if (truthHaz && near(x, y, 0.3) && inside && !mapHaz) fn++;
  }
  const recall = tp / Math.max(1, tp + fn), precision = tp / Math.max(1, tp + fp);
  return { fpNear, fpFar, fpDrop, fpRock, fpSlope, t, ok: s.fw.goals.length === 0, recall, precision, coverage: cover / Math.max(1, total), rms: Math.sqrt(se / Math.max(1, ne)), cells: seen };
}
const route = [{ x: 0.52, y: 0.30 }];
for (const q of [0, 0.5, 1]) {
  const r: ReturnType<typeof run>[] = [1, 2, 3].map(seed => run(q, seed, route));
  const avg = (f: (x: ReturnType<typeof run>) => number) => r.reduce((a, b) => a + f(b), 0) / r.length;
  console.log(`   false alarms: ${avg(x=>x.fpNear).toFixed(0)} within 6 cm of a real hazard (smear), ${avg(x=>x.fpFar).toFixed(0)} elsewhere (phantom: drop ${avg(x=>x.fpDrop).toFixed(0)}, rock ${avg(x=>x.fpRock).toFixed(0)}, slope ${avg(x=>x.fpSlope).toFixed(0)})`);
  console.log(`dead-reckoning x${q}: goals reached ${r.filter(x => x.ok).length}/3, recall ${(avg(x => x.recall) * 100).toFixed(0)}%, precision ${(avg(x => x.precision) * 100).toFixed(0)}%, coverage ${(avg(x => x.coverage) * 100).toFixed(0)}%, height error ${(avg(x => x.rms) * 100).toFixed(1)} cm RMS`);
}
