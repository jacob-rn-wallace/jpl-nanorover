# Blender render of the rover

A Cycles render of the interpreted nanorover (forged-carbon body, IXOLAR cells, windows, struts and wheels), made headless with Blender. The software renderer in `hardware/assembly/concept_render.py` (matplotlib, no ray tracing) is the quick preview; this is the presentation image.

## Setup (done on the owner's machine, 2026-11-13)

- Blender **4.5.9 LTS** from the portable Linux tarball, `~/tools/blender-4.5.9-linux-x64/` (downloaded from `download.blender.org/release/Blender4.5/`, SHA-256 `dcdc3eca6c9825bb35a8033b689c053f3cb5a9b0cd2a61b2eac2a49436b4ad3d`, matching the checksum Blender publishes). No root, nothing installed system-wide; delete the folder to remove it. The 4.5 LTS line was chosen so the script stays stable (5.3 was current).
- The machine: 4 CPU cores, 7 GB of memory, only Intel integrated graphics, so Cycles runs on the CPU. A 1600 x 1000 image at 64 samples took several minutes; 900 x 560 at 32 samples about a minute.

## Run

```
.venv/bin/python hardware/assembly/blender_export.py          # STL of the struts and wheels into hardware/assembly/out/blender/ (git-ignored)
VIEW=hero ~/tools/blender-4.5.9-linux-x64/blender -b -P hardware/assembly/blender_render.py
```

`VIEW` is `hero` (camera end, three-quarter), `rear` (comms end), `top` (orthographic), `detail` (close-up of the camera-end corner, with depth of field) or `cells` (close-up of the top-lid cells at a raking angle). `SAMPLES` (default 96) and `RES` (default `1600x1000`) are optional. Output: `docs/images/rover-<view>.png`. Run `strut.py` and `wheel.py` first so the STEP files exist.

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

The camera end now shows the design of `docs/hardware-spec.md` section 5: a 26 mm cover glass (dark, glossy), behind it a black lens hood and mask ring, the M12 lens front (a black disc with a dark-blue inner element), a smoked dead-front annulus over seven LEDs (the LEDs are barely lighter than the film, so they vanish when off) and, in the ring's top slot, the ranging sensor under infrared-passing ink (very dark, slightly red). These are drawn as thin discs in front of the dark pane, not as real transmission through glass: the look is right, the physics is not. New view: `VIEW=window` (a close-up of the window from +y). The lens shows a broad grey reflection of the softbox: a real lens would show smaller highlights.
