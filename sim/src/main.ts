// The browser app: the operator's console (3D map, photo panel, controls) on top of the simulation.
import * as THREE from "three";
import { Sim } from "./sim";
import { WorldView } from "./worldView";
import { ConsoleView } from "./consoleView";
import { RISK, LINK, PHOTO, SLAM_QUALITY, POWER } from "./constants";
import { PhotoPayload } from "./consoleMap";

const q = new URLSearchParams(location.search);
const canvas = document.getElementById("c") as HTMLCanvasElement;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const sim = new Sim(Number(q.get("seed") ?? 1));
const wv = new WorldView(sim.world);
sim.captureHook = (_size, w, h, lamp) => wv.capture(renderer, sim.rover, w, h, lamp);
const cv = new ConsoleView(() => sim.map, canvas);
(window as unknown as { __sim: Sim }).__sim = sim;
let spectator = q.get("spectator") === "1", specLarge = false, ghost = false, warpIdx = 0, photoSize = "M";
const WARPS = [1, 2, 4, 8];
if (q.get("view") === "top") cv.setView("top");

// ---- scripted start for screenshots and demos: ?demo=1&t=90 drives a mission, then ?photo=1 takes a photograph ----
if (q.get("demo")) {
  sim.setMode("mission"); sim.setGoals([{ x: 0.52, y: 0.30 }]);
  const steps = Math.round(Number(q.get("t") ?? 90) / 0.02); for (let i = 0; i < steps; i++) sim.step();
  if (q.get("photo")) { sim.requestPhoto(photoSize); for (let i = 0; i < Math.round(45 / 0.02); i++) sim.step(); }
}

// ---- keyboard ----
const keys = new Set<string>(); let lastV = 0, lastW = 0, lastShift = false;
function act(k: string): void {
  switch (k) {
    case "1": sim.setMode("pilot"); break;
    case "2": sim.setMode("mission"); break;
    case "q": sim.setRisk(sim.map.risk - 1); break;
    case "e": sim.setRisk(sim.map.risk + 1); break;
    case "c": sim.setGoals([]); break;
    case "x": sim.setSelfRecover(!(sim.fw.selfRecover)); break;
    case "f": sim.right(); break;
    case "p": sim.requestPhoto(photoSize); break;
    case "l": sim.toggleLamp(); break;
    case "v": cv.toggleView(); break;
    case "g": if (!spectator) { spectator = true; specLarge = false; } else if (!specLarge) specLarge = true; else { spectator = false; specLarge = false; } ghost = spectator; break;
    case "[": sim.setLinkRate(LINK.rates.indexOf(sim.link.rate) - 1); break;
    case "]": sim.setLinkRate(LINK.rates.indexOf(sim.link.rate) + 1); break;
    case "t": warpIdx = (warpIdx + 1) % WARPS.length; sim.timeScale = WARPS[warpIdx]; break;
    case "n": sim.cycleSlam(); break;
    case "backspace": sim.reset(); break;
  }
}
addEventListener("keydown", e => {
  const k = e.key.toLowerCase();
  if (["arrowup", "arrowdown", "arrowleft", "arrowright", "w", "a", "s", "d"].includes(k)) { keys.add(k); e.preventDefault(); return; }
  if (!e.repeat) act(k);
});
addEventListener("keyup", e => keys.delete(e.key.toLowerCase()));
const bind = (id: string, fn: () => void) => document.getElementById(id)!.addEventListener("click", () => { fn(); (document.activeElement as HTMLElement | null)?.blur(); });
bind("bPilot", () => act("1")); bind("bMission", () => act("2")); bind("bRiskDn", () => act("q")); bind("bRiskUp", () => act("e"));
bind("bClear", () => act("c")); bind("bRecover", () => act("x")); bind("bRight", () => act("f")); bind("bLamp", () => act("l"));
bind("bPhotoS", () => { photoSize = "S"; act("p"); }); bind("bPhotoM", () => { photoSize = "M"; act("p"); }); bind("bPhotoL", () => { photoSize = "L"; act("p"); });
bind("bView", () => act("v")); bind("bGhost", () => act("g")); bind("bLink", () => act("]")); bind("bWarp", () => act("t")); bind("bSlam", () => act("n")); bind("bReset", () => act("backspace"));
document.getElementById("bLink")!.addEventListener("contextmenu", e => { e.preventDefault(); act("["); });

// ---- clicking the map sends a waypoint (mission mode); a drag orbits ----
let down: { x: number; y: number } | null = null;
canvas.addEventListener("pointerdown", e => { down = { x: e.clientX, y: e.clientY }; });
canvas.addEventListener("pointerup", e => {
  if (!down) return; const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y); down = null;
  if (moved > 5 || sim.map.mode !== "mission") return;
  const r = canvas.getBoundingClientRect();
  const p = cv.pick(((e.clientX - r.left) / r.width) * 2 - 1, -(((e.clientY - r.top) / r.height) * 2 - 1)); if (!p) return;
  sim.setGoals(e.shiftKey ? [...sim.map.goals, p] : [p]);
});

// ---- the photo panel: the lines that have arrived, slow-scan style ----
const photoCanvas = document.getElementById("photo") as HTMLCanvasElement, pctx = photoCanvas.getContext("2d")!;
const offs = new WeakMap<PhotoPayload, HTMLCanvasElement>();
function bitmap(p: PhotoPayload): HTMLCanvasElement | null {
  if (!p.image) return null; let c = offs.get(p);
  if (!c) { c = document.createElement("canvas"); c.width = p.w; c.height = p.h; c.getContext("2d")!.putImageData(p.image, 0, 0); offs.set(p, c); }
  return c;
}
function drawPhoto(): void {
  const W = photoCanvas.width, H = photoCanvas.height, txt = document.getElementById("photoText")!;
  pctx.fillStyle = "#111"; pctx.fillRect(0, 0, W, H);
  const xfer = sim.link.photo, latest = sim.map.photos[0];
  if (xfer) {
    const p = xfer.payload as PhotoPayload, c = bitmap(p), rows = sim.link.photoRows;
    if (c && rows > 0) pctx.drawImage(c, 0, 0, p.w, rows, 0, 0, W, (rows / p.h) * H);
    const left = ((xfer.total - xfer.sent) / ((sim.link.rate / 8) * (1 - LINK.overhead))).toFixed(0);
    txt.textContent = `receiving ${p.size} ${p.w}x${p.h}: ${(sim.link.photoProgress * 100).toFixed(0)}%, about ${left} s left`;
  } else if (sim.photoBusy) txt.textContent = "taking a photograph (lamp and camera on)...";
  else if (latest) { const c = bitmap(latest); if (c) pctx.drawImage(c, 0, 0, latest.w, latest.h, 0, 0, W, H); txt.textContent = `photo ${sim.map.photos.length} of ${sim.stats.photos}: ${latest.size} ${latest.w}x${latest.h}, ${(latest.bytes / 1000).toFixed(0)} KB, ${latest.lit ? "lit" : "dark"}`; }
  else txt.textContent = "no photo yet";
}

// ---- the HUD ----
const hud = document.getElementById("hud")!, logEl = document.getElementById("log")!, warn = document.getElementById("warn")!;
function updateHud(): void {
  const m = sim.map, r = sim.rover, age = sim.t - m.lastFrameT, e = m.pose;
  const tilt = e ? Math.max(0, 0) : 0; void tilt;
  const found = m.markers.size, total = sim.world.markers.length;
  let s = `time ${sim.t.toFixed(0)} s   warp x${sim.timeScale}   seed ${q.get("seed") ?? 1}\n`;
  s += `mode ${m.mode.toUpperCase()}   risk ${RISK[m.risk]?.name}   nav ${m.nav}\n`;
  s += `battery ${(m.battery * 100).toFixed(0)}%   self-recover ${sim.fw.selfRecover ? "on" : "off"}   safety ${sim.override ? "OVERRIDDEN" : "on"}\n`;
  s += `link ${(sim.link.rate / 1000).toFixed(1)} kbit/s   used ${(sim.link.utilization * 100).toFixed(0)}%   last frame ${age < 0 ? "-" : age.toFixed(1)} s ago\n`;
  if (e) s += `est pose (${e.x.toFixed(2)}, ${e.y.toFixed(2)}) m  heading ${((e.theta * 180) / Math.PI).toFixed(0)} deg  +-${(e.sigma * 100).toFixed(0)} cm\n`;
  s += `dead-reckoning error x${sim.slamQuality}\n`;
  s += `hazard seen: ${m.hazardText()}\n`;
  s += `markers photographed: ${found} of ${total}${sim.stats.finishedAt >= 0 ? `   DONE in ${sim.stats.finishedAt.toFixed(0)} s` : ""}   photos taken ${sim.stats.photos}\n`;
  if (spectator) s += `\n[spectator] true pose (${r.x.toFixed(2)}, ${r.y.toFixed(2)}) battery ${(r.batteryFrac * 100).toFixed(0)}% load ${r.loadW.toFixed(2)} W sun ${r.solarW.toFixed(2)} W${r.tipped ? " TIPPED" : ""}${r.stuck ? " STUCK" : ""}${r.fallen ? " FALLEN" : ""}${r.dead ? " DEAD" : ""}`;
  hud.textContent = s;
  const silent = m.frames > 0 && age > 3;
  warn.style.display = silent || r.dead ? "block" : "none";
  warn.textContent = silent ? "NO TELEMETRY: the rover has stopped reporting (flat battery, a fall, or out of range)" : r.dead ? "rover is flat (spectator)" : "";
  logEl.textContent = m.log.slice(-10).join("\n");
  document.getElementById("bPhotoM")!.textContent = `P photo M 640x480`;
  void PHOTO; void POWER; void SLAM_QUALITY;
}

// ---- the loop ----
function resize(): void { renderer.setSize(innerWidth, innerHeight, false); }
addEventListener("resize", resize); resize();
let last = performance.now(), hudT = 0, first = true;
function frame(now: number): void {
  const dt = Math.min(0.1, (now - last) / 1000); last = now; hudT += dt;
  const up = keys.has("w") || keys.has("arrowup"), dn = keys.has("s") || keys.has("arrowdown"), lf = keys.has("a") || keys.has("arrowleft"), rt = keys.has("d") || keys.has("arrowright");
  const v = (up ? 1 : 0) - (dn ? 1 : 0), w = (lf ? 1 : 0) - (rt ? 1 : 0);
  if (v !== lastV || w !== lastW) { sim.setDrive(v, w); lastV = v; lastW = w; }
  const sh = false; void sh;
  sim.advance(dt);
  const W = innerWidth, H = innerHeight;
  cv.camera.aspect = W / H; cv.camera.updateProjectionMatrix();
  cv.update(sim.rover, ghost);
  renderer.setScissorTest(false); renderer.setViewport(0, 0, W, H); renderer.render(cv.scene, cv.camera);
  if (spectator) {
    const ph = specLarge ? Math.round(H * 0.5) : 225, pw = Math.round(ph * 4 / 3), x = W - pw - 12, y = 12;
    renderer.setScissorTest(true); renderer.setViewport(x, y, pw, ph); renderer.setScissor(x, y, pw, ph);
    wv.camera.aspect = pw / ph; wv.camera.updateProjectionMatrix(); wv.syncRover(sim.rover, sim.lampIsOn); renderer.render(wv.scene, wv.camera);
    renderer.setScissorTest(false);
  }
  if (hudT >= 0.1 || first) { hudT = 0; first = false; updateHud(); drawPhoto(); }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
// Shift overrides the safety stop in pilot mode
addEventListener("keydown", e => { if (e.key === "Shift" && !lastShift) { lastShift = true; sim.setOverride(true); } });
addEventListener("keyup", e => { if (e.key === "Shift" && lastShift) { lastShift = false; sim.setOverride(false); } });
