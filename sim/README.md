# nanorover operator-console simulation (vertical slice)

A static web app (three.js, Vite, TypeScript), modelled on maha-rover's simulation. It is a **fun test of the operator console**: the rover sends only range frames and its own pose estimate, the console builds a low-fidelity 3D map from them, and photographs cost time, lamp power and radio bandwidth. Spec, decisions and findings: [`../docs/sim-spec.md`](../docs/sim-spec.md).

```
cd sim
npm install
npm run dev        # http://localhost:5173
npm run build      # static site in sim/dist (GitHub Pages: ../.github/workflows/pages.yml)
npm run check      # logic checks, no browser (sensors, hazards, a mission run, the link, the energy balance)
```

## The game
Drive the rover around an indoor tabletop arena (1.6 x 1.2 m) and **photograph the three coloured markers**. You never see the arena: only the map the rover builds from its 8 x 8 range sensor (hazards coloured: red rock or hole, orange drop-off, magenta steep slope), where it thinks it is, and the photographs you ask for. The markers show up only in photographs, and are placed on the map at the pose the rover believed it had. The table edge is a drop; a 5 cm pit traps the rover; the steep ramp is 34 degrees against a tip-over of 38.

## Controls
| | |
|---|---|
| 1 / 2 | pilot (live driving) / mission (click a waypoint) |
| W A S D, arrows | drive (pilot); Shift overrides the safety stop |
| click the map | waypoint (mission); Shift-click adds one; C clears |
| Q / E | lower / raise the risk level (cautious, normal, bold) |
| P (or the S, M, L buttons) | take a photograph (320 x 240, 640 x 480, 1024 x 768) |
| L | lamp; F right the rover after a tip; X self-recovery after a contact |
| V | map view (oblique, top); drag to orbit, wheel to zoom |
| G | spectator: the true world in a corner, and the true pose (for development) |
| [ ] | link rate 4.8, 9.6, 38.4, 100 kbit/s |
| T | time warp 1, 2, 4, 8 |
| N | dead-reckoning error 0 (perfect), 0.5, 1, 2 |
| Backspace | reset |

## URL options
`?seed=N` (random seed), `?demo=1&t=120` runs a scripted mission for that many seconds before the first frame, `&photo=1` then takes a photograph, `&spectator=1`, `&view=top`.

## Files
`src/constants.ts` every number with its source or "ASM" (assumption); `world.ts` the arena; `rover.ts` the true rover (steps, slopes, pit, falls, tipping, battery); `sensors.ts` the range sensor, odometry and gyro; `firmware.ts` the rover's cyclic executive (hazards, pilot, mission); `link.ts` the radio; `consoleMap.ts` the operator's model; `sim.ts` the whole loop without a screen; `worldView.ts`, `consoleView.ts`, `main.ts` the browser parts; `tests/sim-check.ts` the checks.

Code is Apache-2.0, as in maha-rover.
