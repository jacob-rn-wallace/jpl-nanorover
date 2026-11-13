// The operator's view: a 3D height map built from what has arrived over the radio, the rover as the rover believes it is, waypoints, the trail, markers.
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { ConsoleMap } from "./consoleMap";
import { HZ_DROP, HZ_ROCK, HZ_SLOPE } from "./firmware";
import { ROVER } from "./constants";
import { Rover } from "./rover";

const EXAG = 3;                               // heights are exaggerated three times on screen
export class ConsoleView {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(45, 1, 0.02, 20);
  controls: OrbitControls;
  private mesh: THREE.Mesh; private geom: THREE.PlaneGeometry;
  private glyph = new THREE.Group(); private ring: THREE.Mesh; private ghost: THREE.Mesh;
  private goals = new THREE.Group(); private markers = new THREE.Group(); private trail: THREE.Line;
  private seen = -1; private view: "top" | "oblique" = "oblique";
  readonly plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  private get map(): ConsoleMap { return this.getMap(); }
  constructor(private getMap: () => ConsoleMap, dom: HTMLElement) {
    const s = this.scene, map = getMap(); s.background = new THREE.Color(0x0b0f14);
    s.add(new THREE.AmbientLight(0xffffff, 0.75)); const d = new THREE.DirectionalLight(0xffffff, 0.8); d.position.set(0.5, 2, 1); s.add(d);
    this.geom = new THREE.PlaneGeometry(map.cols * map.res, map.rows * map.res, map.cols - 1, map.rows - 1);
    this.geom.rotateX(-Math.PI / 2);
    this.geom.setAttribute("color", new THREE.BufferAttribute(new Float32Array(this.geom.attributes.position.count * 3), 3));
    this.mesh = new THREE.Mesh(this.geom, new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true }));
    s.add(this.mesh);
    // the map's own frame (not the table: the operator does not know where the table ends)
    const gridMat = new THREE.LineBasicMaterial({ color: 0x1d2a38 });
    const grid = new THREE.GridHelper(1.8, 18, 0x2a3a4c, 0x182230); grid.position.set(0, -0.001, 0); s.add(grid); void gridMat;
    // the rover glyph (estimated pose), its pose uncertainty, and a ghost of the true pose for development (key G)
    const body = new THREE.Mesh(new THREE.BoxGeometry(ROVER.body.l, ROVER.body.h * EXAG * 0.5, ROVER.body.w), new THREE.MeshLambertMaterial({ color: 0xf2b134 }));
    const nose = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.08, 12), new THREE.MeshLambertMaterial({ color: 0xffe08a }));
    nose.rotation.z = -Math.PI / 2; nose.position.set(0.11, 0, 0); this.glyph.add(body, nose); s.add(this.glyph);
    this.ring = new THREE.Mesh(new THREE.RingGeometry(0.0, 0.01, 48), new THREE.MeshBasicMaterial({ color: 0xf2b134, transparent: true, opacity: 0.25, side: THREE.DoubleSide }));
    this.ring.rotation.x = -Math.PI / 2; s.add(this.ring);
    this.ghost = new THREE.Mesh(new THREE.BoxGeometry(ROVER.body.l, 0.02, ROVER.body.w), new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true })); this.ghost.visible = false; s.add(this.ghost);
    s.add(this.goals, this.markers);
    const tg = new THREE.BufferGeometry(); tg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(3000 * 3), 3)); tg.setDrawRange(0, 0);
    this.trail = new THREE.Line(tg, new THREE.LineBasicMaterial({ color: 0x66d9ff })); s.add(this.trail);
    this.controls = new OrbitControls(this.camera, dom); this.controls.enableDamping = true; this.controls.maxPolarAngle = Math.PI * 0.49;
    this.setView("oblique");
  }
  setView(v: "top" | "oblique"): void {
    this.view = v;
    if (v === "top") this.camera.position.set(0.0, 2.1, 0.001); else this.camera.position.set(0.0, 1.25, 1.45);
    this.controls.target.set(0, 0, 0); this.controls.update();
  }
  toggleView(): void { this.setView(this.view === "top" ? "oblique" : "top"); }
  showGhost(on: boolean) { this.ghost.visible = on; }
  private cellColor(c: number, out: number[]): void {
    if (!this.map.n[c]) { out.push(0.045, 0.055, 0.075); return; }
    const hz = this.map.haz[c];
    if (hz & HZ_DROP) { out.push(1.0, 0.45, 0.05); return; }
    if (hz & HZ_ROCK) { out.push(0.95, 0.15, 0.15); return; }
    if (hz & HZ_SLOPE) { out.push(0.85, 0.2, 0.8); return; }
    const h = Math.max(-0.06, Math.min(0.12, this.map.z[c])), t = (h + 0.06) / 0.18;
    out.push(0.18 + 0.35 * t, 0.42 + 0.35 * t, 0.30 + 0.2 * t);
  }
  /** rebuild the mesh when the map changed, then place the glyphs */
  update(truth: Rover | null, showGhost: boolean): void {
    const m = this.map;
    if (m.version !== this.seen) {
      this.seen = m.version;
      const pos = this.geom.attributes.position as THREE.BufferAttribute, col = this.geom.attributes.color as THREE.BufferAttribute;
      for (let j = 0; j < m.rows; j++) for (let i = 0; i < m.cols; i++) {
        const c = j * m.cols + i, v = j * m.cols + i;                       // vertex (i, j) of the plane (rows run along -Z after the rotation: row 0 is the far edge)
        const vi = (m.rows - 1 - j) * m.cols + i;
        pos.setXYZ(vi, m.x0 + (i + 0.5) * m.res, m.n[c] ? m.z[c] * EXAG : 0, -(m.y0 + (j + 0.5) * m.res));
        const rgb: number[] = []; this.cellColor(c, rgb); col.setXYZ(vi, rgb[0], rgb[1], rgb[2]); void v;
      }
      pos.needsUpdate = true; col.needsUpdate = true; this.geom.computeVertexNormals();
      const tp = this.trail.geometry.attributes.position as THREE.BufferAttribute, n = Math.min(m.trail.length, 3000);
      for (let k = 0; k < n; k++) { const p = m.trail[m.trail.length - n + k]; tp.setXYZ(k, p.x, 0.004, -p.y); }
      tp.needsUpdate = true; this.trail.geometry.setDrawRange(0, n);
      this.goals.clear(); for (const g of m.goals) { const c = new THREE.Mesh(new THREE.ConeGeometry(0.02, 0.07, 10), new THREE.MeshLambertMaterial({ color: 0x35e0ff })); c.position.set(g.x, 0.035, -g.y); this.goals.add(c); }
      this.markers.clear();
      const colors: Record<string, number> = { red: 0xd9342b, green: 0x2fa84f, blue: 0x2f6fd9 };
      for (const [id, p] of m.markers) { const s = new THREE.Mesh(new THREE.SphereGeometry(0.025, 14, 10), new THREE.MeshLambertMaterial({ color: colors[id] ?? 0xffffff })); s.position.set(p.x, 0.05, -p.y); this.markers.add(s); }
    }
    if (m.pose) {
      const e = m.pose;
      this.glyph.position.set(e.x, e.z * EXAG + 0.03, -e.y); this.glyph.rotation.y = e.theta;
      this.ring.position.set(e.x, 0.006, -e.y);
      const g = new THREE.RingGeometry(Math.max(0.0, e.sigma - 0.004), Math.max(e.sigma, 0.005), 48); this.ring.geometry.dispose(); this.ring.geometry = g;
    }
    this.ghost.visible = showGhost && !!truth;
    if (truth && this.ghost.visible) { this.ghost.position.set(truth.x, truth.z * EXAG + 0.03, -truth.y); this.ghost.rotation.y = truth.theta; }
    this.controls.update();
  }
  /** a click on the canvas as a point on the map (simulation x, y) */
  pick(ndcX: number, ndcY: number): { x: number; y: number } | null {
    const ray = new THREE.Raycaster(); ray.setFromCamera(new THREE.Vector2(ndcX, ndcY), this.camera);
    const p = new THREE.Vector3(); if (!ray.ray.intersectPlane(this.plane, p)) return null;
    return { x: p.x, y: -p.z };
  }
}
