# Blender render of the rover

A Cycles render of the interpreted nanorover (forged-carbon body, IXOLAR cells, windows, struts and wheels), made headless with Blender. The software renderer in `hardware/assembly/concept_render.py` (matplotlib, no ray tracing) is the quick preview; this is the presentation image.

## Setup (done on the owner's machine, 2026-11-13)

- Blender **4.5.9 LTS** from the portable Linux tarball, `~/tools/blender-4.5.9-linux-x64/` (downloaded from `download.blender.org/release/Blender4.5/`, SHA-256 `dcdc3eca6c9825bb35a8033b689c053f3cb5a9b0cd2a61b2eac2a49436b4ad3d`, matching the checksum Blender publishes). No root, nothing installed system-wide; delete the folder to remove it. The 4.5 LTS line was chosen so the script stays stable (5.3 was current).
- The machine: 4 CPU cores, 7 GB of memory, only Intel integrated graphics, so Cycles runs on the CPU. A 1600 x 1000 image at 64 samples took several minutes; 900 x 560 at 32 samples about a minute.

## Setup on an Apple Silicon Mac (added 2026-11-14, not yet tried)

The owner's MacBook Air (M2, 16 GB) should render several times faster than the EliteDesk (my estimate from benchmark rankings, not measured: about 3 times on the CPU, and a further 2 to 3 times with the Metal GPU, so the views here should take well under two minutes each; the Air is fanless and may throttle on long runs).

1. Blender **4.5.9 LTS** for macOS Apple Silicon, installed as **`~/tools/Blender-4.5.9.app`** (the Mac's system Blender in `/Applications` is 4.1.1, too old: the cell material needs the thin-film input added in 4.2, and `render_pending.py` refuses any Blender older than 4.2 and prints which one it uses): `https://download.blender.org/release/Blender4.5/blender-4.5.9-macos-arm64.dmg`. Its SHA-256 in Blender's published checksum file (`blender-4.5.9.sha256`, read 2026-11-14) is `e3a3d7aac381fb4e4d05197f99cd8899484d7e8bc4497c134066e6733f372238`; check the download with `shasum -a 256`. Drag Blender into Applications; the binary for headless use is `/Applications/Blender.app/Contents/MacOS/Blender`.
2. The two meshes the render needs, `hardware/assembly/out/blender/struts.stl` and `wheels.stl`, are git-ignored. Either copy them from the desktop machine, or regenerate them with the CAD chain (`pip install -r hardware/requirements.txt` in a venv, then `hardware/body/body.py`, `hub/hub.py`, `strut/strut.py`, `wheel/wheel.py`, `assembly/blender_export.py`; body.py needs Hammond's STEP from the private repository).
3. To render every pending job in `docs/render-jobs.md`, mark it done, commit and push in one go, run `python3 hardware/assembly/render_pending.py` (see `docs/render-jobs.md`). To render one view by hand, run with the GPU: `DEVICE=gpu VIEW=hero /Applications/Blender.app/Contents/MacOS/Blender -b -P hardware/assembly/blender_render.py`. The script prints `render device: METAL [...]` when it finds the GPU and says so if it falls back to the CPU. Images will differ from the Linux ones only in noise.

## Run

```
.venv/bin/python hardware/assembly/blender_export.py          # STL of the struts and wheels into hardware/assembly/out/blender/ (git-ignored)
VIEW=hero ~/tools/blender-4.5.9-linux-x64/blender -b -P hardware/assembly/blender_render.py
```

`VIEW` is `hero` (camera end, three-quarter), `rear` (comms end), `top` (orthographic), `detail` (close-up of the camera-end corner, with depth of field) or `cells` (close-up of the top-lid cells at a raking angle). `DEVICE` is `cpu` (default) or `gpu` (Metal on a Mac; see the Mac setup above). `SAMPLES` (default 96) and `RES` (default `1600x1000`) are optional. Output: `docs/images/rover-<view>.png`. Run `strut.py` and `wheel.py` first so the STEP files exist.

## What is modelled, and what is not

- **Real:** the struts and wheels (the CAD STEP parts at the 25 degree stance). The cell, window and RF-plug positions and sizes come from the same numbers as `layout.py`, `cell_pocket.py` and `cell_endface.py`: nine IXOLAR cells per lid, four standing on each end face, the 26 mm round camera window with its bezel, the 27 mm square RF window on the -y face.
- **A stand-in:** the body is a 140 x 140 x 60 mm block with 0.8 mm bevelled edges, not the forged-carbon shell (`block.py` is only the cavity volume). The cells and panes stand 0.2 mm proud of it (flush in the design). 
- **Struts and wheels are bare machined aluminium** (6061, `docs/strut-spec.md`; owner, 2026-11-13): metallic, slightly anisotropic, no colour. An earlier version gave the struts a bronze colour that had no basis in the design.
- **Not modelled:** lid screws and seals, the hub studs and rings, the lamp, the beamsplitter and lens, the inside.
- **The forged carbon is procedural:** chips of random orientation lying flat in each face (a stretched 2D Voronoi per layer, five layers picked by a coarse Voronoi), each with its own tone and its own anisotropic-highlight direction, fine fibre streaks along the chip, a darker chip boundary, and a clear coat that does not follow the chip relief. The chip size (about 9 mm, stretched about 4:1) is a choice, not a measurement of any real part.
- **Lighting:** four soft boxes (invisible to the camera, visible in the reflections) and a grey world, over a plain ground plane at the wheel-bottom height.

## The solar cells (revised 2026-11-13 after finding product photographs)

**First pass was wrong.** It drew dark-blue cells with a pale grey film margin, from the datasheet drawing (a blue rectangle) and the Anysolar sentence "a homogeneous dark blue or dark grey". Product photographs of the same parts show otherwise.

**Reference photographs (looked at, not stored in the repository; they belong to their publishers):**
- the **SM940K09L** itself (DigiKey's product photo, 200 x 200 px): a matte, dark charcoal grey front with no gridlines, no seams and no pale border, about 1.8 mm thick with crisp square edges; the back is a black board with white silkscreen ("IXYS SM940K09L R3.0", + and - marks) and two square gold-coloured pads at opposite ends;
- the **KXOB25-14X1F** and **KXOB22-12X1F** SolarBITs (distributor photographs, 1024 x 684 and 640 x 640 px): a flat black front, again with no visible grid; a black back board with gold pads at both ends and gold silkscreen; on the side a thin light-grey layer (the silicon edge) under the black layers; one photo shows a small silver strip at one end of the front (not understood: a contact, or the cell edge).
Both photographs are small and lit by studio lights, so their colour is only roughly what the part looks like in a different light.

**What the render does now**
- **Front:** near-black charcoal with a satin finish (base colour about 0.02 linear, roughness 0.32, a light satin film over it with a very slight waviness) and only a faint cool sheen toward grazing angles. It is deliberately not blue: the real parts look black. The anti-reflection thin-film layer in the material is kept but its tint is muted.
- **Margin:** black, the same as the cell (the photos show no pale border); the datasheet's margins of 0.75 mm top and bottom and about 0.11 and 0.21 mm at the ends are kept as a slightly rougher black frame, which shows only as a faint line.
- **No gridlines, busbars or cell seams** are drawn, which matches the photographs; the nine-cell layout inside each part is still not visible anywhere (`docs/positioning.md` section 10b).
- **Not modelled:** the back (gold pads and silkscreen; the cells sit in the lids and the back is never seen), the silver strip of the KXOB25 photo, the layer line on the side edge, and the SM401K08TF and SM531K08TFS (no photographs were looked at; they get the same material and a 0.75 mm margin, an assumption).
- **To improve it further:** a larger, sharper photograph of a part in raking light would show the true gloss and any texture.

## Update 2026-11-14: the camera window with the LED ring and the ranging sensor

The camera end now shows the design of `docs/hardware-spec.md` section 5: a 26 mm cover glass (dark, glossy), behind it a black lens hood and mask ring, the M12 lens front (a black disc with a dark-blue inner element), a smoked dead-front annulus over six LEDs (not drawn at all when off; `LED=on` draws them lit) and, in the ring's inboard slot on the camera axis (long axis vertical; it was the top slot, then the bottom slot, until 2026-11-14 when the owner asked for symmetry about z = 30; the LEDs are at 45, 90, 135, 225, 270 and 315 degrees), the ranging sensor behind clear glass (a near-black package). Updated again on 2026-11-14: six mid-power LEDs at 10 mm radius (0, 45, 135, 180, 225, 315 degrees). These are drawn as thin discs in front of the dark pane, not as real transmission through glass: the look is right, the physics is not. New view: `VIEW=window` (a close-up of the window from +y). The lens shows a broad grey reflection of the softbox: a real lens would show smaller highlights.

## Update 2026-11-14: a Rubik's cube for scale

The two main shots (R1 `rover-hero.png`, R2 `rover-rear.png`) carry a **Rubik's cube** (57 mm on a side, the standard 3 x 3 x 3) on the ground at the right of the rover (owner's idea, 2026-11-14). It is nearly the height of the 60 mm body, saturated and multicoloured against a grey floor and a dark rover, and everyone knows its size; the lineage (a 1980s object, like the era the electronics follow) is a small bonus.

**The model is the CC BY 4.0 "Rubik's Cube" by BeyondDigital** (Sketchfab; 11,642 faces, one mesh, three baked textures), in `hardware/assembly/assets/rubiks-cube/` with `ATTRIBUTION.md` (textures reduced to 2048 x 2048; the original zip is in the private repository, `models/`). The script imports the glTF, scales it to 57 mm by its bounding box (the page gives no size), turns it `QYAW` degrees and sets it on the ground at `QX`, `QY`. Credit is also in the README, since the hero image shows it.

**Tried first and dropped:** (1) **a US quarter** (the JPL photographs use one, `docs/photo-measurements.md`): at the render's size it read only as "a coin", even with a hand-built bust, legends, a darker frosted field and more relief; (2) **a cube built in the script** (27 rounded cubies and 54 stickers): the owner found it looked wrong (the faces looked recessed). A golf ball and a AA cell were the other candidates; a banana or soda can would dwarf the 140 mm body.

Settings: `FIDUCIAL=cube` (default `off`, so the technical views are unchanged), `QX`, `QY` (the hero uses -5, 170 and the rear shot 5, -170, the 180 degree mirror), `QYAW` (default 28). `FIDUCIAL=quarter` (`QX`, `QY`, `QAZ`, `QLEAN`) is kept as an option. Checked on the desktop at 1000x625 and 32 samples (both views: 57.0 mm high, fully in frame, clear of the wheels); the full renders are queued as pending for the Mac.

## Update 2026-11-15: the GitHub social preview (R13)

`VIEW=social` makes `docs/images/rover-social.png`: 1280 x 640 (GitHub's recommended 2:1 size; its minimum is 640 x 320 and the file must be under 1 MB), the rover at the left with its camera end toward the viewer and the Rubik's cube at the right, on the plain grey ground, with margins all round so that a crop does not cut either. Camera: azimuth 36, elevation 17, 780 mm from a target at (20, 40, 4) (`AZ`, `EL`, `DIST`, `TX`, `TY` tune it), 55 mm lens; the cube at (-5, 170). For this view only, the PNG is written without an alpha channel and with the strongest compression (589 KB; with alpha it was 905 KB). Two framings were tried at 960 x 480 and this one chosen (the other had the rover larger but the cube nearer the edge). **To use it: Settings > General > Social preview > Edit > Upload an image** (GitHub has no API for this, so it is by hand; the image does not update by itself when the repository does). The cube's credit is in `hardware/assembly/assets/rubiks-cube/ATTRIBUTION.md` and the README.

