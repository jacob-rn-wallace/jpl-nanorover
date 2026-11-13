// The true world as a three.js scene: used for photographs (rendered from the rover's camera) and for the spectator view (key G).
// Coordinates: simulation (x, y, z up) maps to three.js (X = x, Y = z, Z = -y); a yaw of theta is a rotation of theta about Y.
import * as THREE from "three";
import { World } from "./world";
import { Rover } from "./rover";
import { ROVER, PHOTO } from "./constants";

export class WorldView {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(45, 1, 0.02, 20);
  private rover = new THREE.Group();
  private lamp: THREE.SpotLight;
  private ground: THREE.Mesh[] = [];
  constructor(private world: World) {
    const s = this.scene;
    s.background = new THREE.Color(0x05060a);
    s.add(new THREE.AmbientLight(0xffffff, 0.22));
    const hemi = new THREE.HemisphereLight(0x8899bb, 0x222222, 0.35); s.add(hemi);
    // the table top
    const tex = this.floorTexture();
    const top = new THREE.Mesh(new THREE.BoxGeometry(world.w, 0.05, world.d), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.9 }));
    top.position.y = -0.025; s.add(top);
    // the sunlit patch: a soft decal and a spot light from a window above
    const patch = new THREE.Mesh(new THREE.CircleGeometry(world.sun.r, 48), new THREE.MeshBasicMaterial({ color: 0xffe9a8, transparent: true, opacity: 0.25, depthWrite: false }));
    patch.rotation.x = -Math.PI / 2; patch.position.set(world.sun.x, 0.0015, -world.sun.y); s.add(patch);
    const sun = new THREE.SpotLight(0xfff0cc, 14, 5, Math.atan(world.sun.r / 1.4), 0.35, 1.0);
    sun.position.set(world.sun.x - 0.3, 1.4, -world.sun.y + 0.2); sun.target.position.set(world.sun.x, 0, -world.sun.y); s.add(sun, sun.target);
    // obstacles
    for (const b of world.boxes) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(b.x1 - b.x0, b.h, b.y1 - b.y0), new THREE.MeshStandardMaterial({ color: b.color, roughness: 0.95 }));
      m.position.set((b.x0 + b.x1) / 2, b.h / 2, -(b.y0 + b.y1) / 2); s.add(m);
    }
    for (const r of world.ramps) {                                         // wedges rising along x
      const L = r.x1 - r.x0, W = r.y1 - r.y0, shape = new THREE.Shape([new THREE.Vector2(0, 0), new THREE.Vector2(L, 0), new THREE.Vector2(L, r.hHigh)]);
      const g = new THREE.ExtrudeGeometry(shape, { depth: W, bevelEnabled: false });
      const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x9a8f7f, roughness: 0.9 }));
      m.position.set(r.x0, 0, -r.y1); s.add(m);
    }
    for (const p of world.pits) {                                           // the pit reads as a black hole
      const m = new THREE.Mesh(new THREE.PlaneGeometry(p.x1 - p.x0, p.y1 - p.y0), new THREE.MeshBasicMaterial({ color: 0x000000 }));
      m.rotation.x = -Math.PI / 2; m.position.set((p.x0 + p.x1) / 2, 0.002, -(p.y0 + p.y1) / 2); s.add(m);
    }
    for (const mk of world.markers) {
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.003, 0.003, 0.05, 8), new THREE.MeshStandardMaterial({ color: 0xcccccc }));
      const flag = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.025, 0.002), new THREE.MeshStandardMaterial({ color: mk.color, roughness: 0.6 }));
      const g = new THREE.Group(); pole.position.y = 0.025; flag.position.set(0.018, 0.04, 0); g.add(pole, flag);
      g.position.set(mk.x, world.heightAt(mk.x, mk.y), -mk.y); s.add(g);
    }
    // the rover
    const body = new THREE.Mesh(new THREE.BoxGeometry(ROVER.body.l, ROVER.body.h, ROVER.body.w), new THREE.MeshStandardMaterial({ color: 0x23272e, roughness: 0.5, metalness: 0.3 }));
    body.position.y = 0.0325 + 0.0; this.rover.add(body);
    const cells = new THREE.Mesh(new THREE.BoxGeometry(0.128, 0.002, 0.128), new THREE.MeshStandardMaterial({ color: 0x14224a, roughness: 0.3, metalness: 0.5 }));
    cells.position.y = 0.0325 + 0.031; this.rover.add(cells);
    const win = new THREE.Mesh(new THREE.CircleGeometry(0.013, 20), new THREE.MeshBasicMaterial({ color: 0x000000 }));
    win.rotation.y = Math.PI / 2; win.position.set(0.0705, 0.0325, 0); this.rover.add(win);
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
      const w = new THREE.Mesh(new THREE.CylinderGeometry(ROVER.wheelR, ROVER.wheelR, 0.02, 20), new THREE.MeshStandardMaterial({ color: 0x9aa3ad, roughness: 0.4, metalness: 0.8 }));
      w.rotation.x = Math.PI / 2; w.position.set(sx * 0.05, ROVER.wheelR, sz * 0.085); this.rover.add(w);
    }
    this.lamp = new THREE.SpotLight(0xffffff, 0, 1.6, 0.6, 0.5, 1.0);
    this.lamp.position.set(0.07, 0.04, 0); const tgt = new THREE.Object3D(); tgt.position.set(0.7, 0.0, 0); this.rover.add(this.lamp, tgt); this.lamp.target = tgt;
    s.add(this.rover);
    this.camera.position.set(0.0, 1.5, 1.35); this.camera.lookAt(0, 0, 0);
  }
  private floorTexture(): THREE.Texture {
    const c = document.createElement("canvas"); c.width = c.height = 512; const g = c.getContext("2d")!;
    g.fillStyle = "#5b4a3a"; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 6000; i++) { g.fillStyle = `rgba(${40 + Math.random() * 50},${30 + Math.random() * 40},${20 + Math.random() * 30},0.18)`; g.fillRect(Math.random() * 512, Math.random() * 512, 2 + Math.random() * 10, 1); }
    g.strokeStyle = "rgba(255,255,255,0.10)"; g.lineWidth = 1;                // a 10 cm grid so distances read in photographs
    for (let i = 0; i <= 512; i += 512 / 16) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 512); g.moveTo(0, i); g.lineTo(512, i); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(this.world.w / 1.6 * 1, this.world.d / 1.6 * 1);
    return t;
  }
  syncRover(r: Rover, lampOn: boolean): void {
    this.rover.position.set(r.x, r.z, -r.y);
    this.rover.rotation.set(0, 0, 0); this.rover.rotation.order = "YZX";
    this.rover.rotation.y = r.theta; this.rover.rotation.z = r.pitch; this.rover.rotation.x = -r.roll;
    this.lamp.intensity = lampOn ? 7 : 0;
  }
  /** the photograph: rendered from the rover's window with the lamp on, as RGBA pixels */
  capture(renderer: THREE.WebGLRenderer, r: Rover, w: number, h: number, lampOn: boolean): ImageData {
    this.syncRover(r, lampOn);
    const cam = new THREE.PerspectiveCamera((PHOTO.fovV * 180) / Math.PI, w / h, 0.02, 10);
    const f = ROVER.mountFwd + 0.001;
    cam.position.set(r.x + Math.cos(r.theta) * f, r.z + 0.055, -(r.y + Math.sin(r.theta) * f));
    cam.lookAt(cam.position.x + Math.cos(r.theta) * Math.cos(r.pitch), cam.position.y + Math.sin(r.pitch), cam.position.z - Math.sin(r.theta) * Math.cos(r.pitch));
    const rt = new THREE.WebGLRenderTarget(w, h, { colorSpace: THREE.SRGBColorSpace });
    const prev = renderer.getRenderTarget();
    renderer.setRenderTarget(rt); renderer.render(this.scene, cam);
    const buf = new Uint8Array(w * h * 4); renderer.readRenderTargetPixels(rt, 0, 0, w, h, buf);
    renderer.setRenderTarget(prev); rt.dispose();
    const img = new ImageData(w, h);
    for (let y = 0; y < h; y++) img.data.set(buf.subarray((h - 1 - y) * w * 4, (h - y) * w * 4), y * w * 4);   // flip vertically
    return img;
  }
}
