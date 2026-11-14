// Numbers with their provenance. SRC = a document in this repository (named), ASM = my assumption, untested against a real rover.
import { deg } from "./util";

export const DT = 0.02;                       // s: firmware and physics step, 50 Hz, a cyclic executive as Sojourner's (docs/electronics-concept.md)

export const ARENA = { w: 1.6, d: 1.2 };      // m, an indoor tabletop (ASM, docs/sim-spec.md)
export const VOID_Z = -0.75;                  // m, the floor below the table

export const ROVER = {
  body: { w: 0.14, l: 0.14, h: 0.06 },        // SRC CLAUDE.md (papers' figures)
  wheelR: 0.0325,                             // SRC 65 mm wheels
  radius: 0.09,                               // m, footprint circle (half the diagonal is 0.099) ASM
  climbMax: 0.032,                            // m, a step taller than this stops the rover (just under a wheel radius) ASM
  climbSlow: 0.015,                           // m, a step this tall halves the speed ASM
  maxSpeed: 0.04,                             // m/s SRC docs/drivetrain-spec.md (about 40 mm/s from the videos)
  maxTurn: 0.6,                               // rad/s ASM
  tipSlope: Math.tan(deg(38)),                // SRC docs/chassis-simulation.md: tip-over 38 to 51 degrees
  dropOk: 0.035,                              // m, a drop up to this is driven off ASM
  dropFall: 0.10,                             // m, a drop beyond this is a fall that ends the run ASM
  rightTime: 3.0,                             // s SRC docs/chassis-simulation.md (righting in about 3 s)
  mountFwd: 0.07, mountH: 0.052,              // m, the ranging sensor high on the front face (a rock taller than the sensor cannot be measured, only seen as a wall) ASM
  tofPitch: deg(22),                          // sensor tilted down ASM (a flat floor then fills every row, the top row at about 1.3 m)
};

export const TOF = {                          // VL53L5CX class (ST datasheet via docs/electronics-concept.md): 8 x 8 zones, 45 x 45 degrees, 60 Hz
  n: 8, fov: deg(45), hz: 10, minR: 0.02, maxR: 2.0,   // range limit cut to the table (the part reaches 4 m)
  sigma0: 0.003, sigmaRel: 0.01, dropout: 0.01,        // ASM
};

export const POWER = {                        // W, from hardware/body/power_budget.py (SRC) unless marked ASM
  batteryWh: 3.70,                            // 1000 mAh at 3.7 V (docs/hardware-spec.md section 4)
  idle: 0.1155,                               // PIC32 awake (20 mA ASM) + XBee 3 receiving (15 mA SRC Digi) at 3.3 V; was 0.105 from an ESP32-class dev board (docs/electronics-concept.md)
  hold: 1.44,                                 // four servos holding at 30 mA and 12 V SRC (sources disagree 6 to 60 mA)
  wheels: 0.4,                                // four wheel motors at full drive ASM
  lamp: 0.1,                                  // the LED ring round the camera lens, ASM (0.2 before the beamsplitter was dropped)
  camera: 0.3,                                // while capturing ASM
  radioTx: 0.0825,                            // W above the receiving figure at full link utilisation: XBee 3 802.15.4 non-PRO 40 mA at +8 dBm less 15 mA, at 3.3 V (manual snippet via distributors); was 0.65 ASM
  righting: 2.0,                              // servos moving ASM
  sun: 2.5,                                   // one lit face in full sun SRC power_budget.py (2.55 W)
  wake: 0.05,                                 // fraction of the battery at which a flat rover restarts
};

export const LINK = {
  rates: [4800, 9600, 38400, 100000, 250000],        // bit/s (4800 was the original's planned radio, SRC docs/design-comparison.md)
  overhead: 0.10,                             // framing ASM
  latency: 0.05,                              // s ASM
  tofBytes: 140,                              // 4 header + 64 x 2 B ranges + status ASM
  poseBytes: 20,
  hzNormal: 5, hzPhoto: 1,                    // telemetry rate, and while a photo is transferring ASM
};
export const PHOTO = {
  sizes: { S: [320, 240], M: [640, 480], L: [1024, 768] } as Record<string, [number, number]>,
  bppLit: 0.65, bppDark: 0.15,                // JPEG bits per pixel, lit scene and dark scene ASM (docs/electronics-concept.md)
  fovV: deg(41.5), fovH: deg(54),             // M12 3.6 mm lens on a 1/4 inch sensor SRC (optics ray trace)
  captureTime: 1.0,                           // s the lamp and camera are on ASM
  range: 0.9,                                 // m, a marker closer than this can be read ASM
};

// risk level 1 (cautious) to 3 (bold): thresholds are ASM, the structure (a table keyed to a risk level) is Sojourner's (docs/electronics-concept.md)
export const RISK = [
  { name: "1 cautious", rock: 0.020, slope: 0.060, tilt: deg(15), drop: 0.030 },     // refuses anything near the wheels' limit
  { name: "2 normal",   rock: 0.030, slope: 0.100, tilt: deg(25), drop: 0.045 },     // matches what the wheels can climb (climbMax 3.2 cm)
  { name: "3 bold",     rock: 0.040, slope: 0.160, tilt: deg(33), drop: 0.060 },     // overshoots: it will try rocks the wheels cannot climb
];
export const SLAM_QUALITY = [0, 0.5, 1, 2];   // 0 perfect; 1 a typical dead-reckoning drift ASM

/** ultrasonic beacon fix (Cricket pattern; owner decision 2026-11-13). The radio packet gives the time sync, so each post's range is a time of flight.
 *  Figures: sigma 4 cm is the middle of the 3 to 5 cm plan (docs/positioning.md section 7); the rest are ASM. */
export const BEACON = {
  posts: [{ x: -0.85, y: 0.65 }, { x: 0.85, y: 0.65 }, { x: 0.0, y: -0.65 }],   // m, three posts just off the table edge ASM
  period: 0.5,                 // s between fixes ASM
  sigma: 0.04,                 // m, range noise
  echo: 0.05, echoBias: 0.15,  // probability a range is an echo, and how much longer it reads ASM
  maxRange: 2.5,               // m, a 40 kHz capsule's usable range ASM
  gate: 0.25,                  // m, a fix further than this from the dead-reckoned position is rejected as an echo
  gain: 0.3,                   // fraction of the innovation applied per fix ASM
  headingSigma: 0.05,          // rad (about 3 degrees), deliberately worse than the unchecked 0.3 degrees from two receivers
  headingGain: 0.1,
};

/** Lighthouse 1.0 base stations received by solar cells on the up-facing lid (owner decision 2026-11-13; docs/positioning.md sections 9 and 10).
 *  Two stations sweep a laser plane at 60 rev/s; a sensor timing a sweep against the sync flash gets one angle. Everything below is ASM unless marked. */
export const LIGHTHOUSE = {
  stations: [{ x: -1.0, y: 0.8, z: 1.6 }, { x: 1.0, y: -0.8, z: 1.6 }],   // m, diagonal corners of the table, 1.6 m up ASM
  rate: 60,                    // rev/s SRC (Vishay-independent: Bitcraze system overview and the paper it links, docs/positioning.md section 9)
  period: 1 / 30,              // s between pose fixes: four sweeps (two stations, two axes) fit about two frames ASM
  sigmaT: 3e-6,                // s, timing error of a threshold crossing, from a ~1 us rise time and amplitude walk ASM (section 10)
  lidH: 0.092,                 // m, the lid's height above the ground: 32 mm body floor above the wheel bottoms + 60 mm SRC (CAD, assembly)
  sensors: [[-0.0445, 0.056], [0.0445, 0.056], [-0.0445, -0.056], [0.0445, -0.056], [0, 0]],   // m, five cell centres on the lid, one capture channel each ASM
  detect: 1,                   // probability a sweep pulse is detected per sensor: 1 = the cells work like BPW34s; section 10 says a series string may lose a sweep (layout unknown)
  gate: 0.15, gain: 0.25,      // m, innovation gate; fraction applied per fix ASM
};
