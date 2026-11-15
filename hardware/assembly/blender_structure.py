"""Blender (Cycles) renders of an optimised body structure (hardware/body/to_geometry.py writes the meshes).

Run from the repository root:
    STEM=n48_m120_p5 VIEW=iso ~/tools/blender-4.5.9-linux-x64/blender -b -P hardware/assembly/blender_structure.py
STEM names the result (hardware/body/out/geom/<STEM>_{structure,fixed,skin,context}.obj); VIEW is iso (camera end toward the viewer), isorear, top, end (looking at the camera end), side (from +x);
WHEELS=on adds the struts and wheels (hardware/assembly/out/blender/*.stl, as blender_render.py); SKIN=on (default) shows the outer skin as a faint ghost shell; SAMPLES and RES as there.
Output: docs/images/structure-<STEM>-<VIEW>.png.  1 Blender unit = 1 mm; z up; the camera end is +y.
Colours: the optimised structure amber (smoothed from the optimiser's 2.9 mm cells: the surface is a visualisation, not a manufacturable shape), the other fixed solids grey (the lid rims, hub rings,
cam bosses, window ring, servo seat walls and the battery cradle), the servos silver, their mounting plates aluminium, the battery blue, the protection board and XBee green, the camera and patch dark.
"""
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "hardware" / "body" / "out" / "geom"
STEM = os.environ.get("STEM", "n48_m120_p5")
VIEW = os.environ.get("VIEW", "iso")
SAMPLES = int(os.environ.get("SAMPLES", "48"))
RES = [int(v) for v in os.environ.get("RES", "1500x1000").split("x")]
WHEELS = os.environ.get("WHEELS", "off").lower() == "on"
SKIN = os.environ.get("SKIN", "on").lower() == "on"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name, base, metallic=0.0, rough=0.5, alpha=1.0, emission=None, **extra):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1.0); b.inputs["Metallic"].default_value = metallic; b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    for k, v in extra.items():
        b.inputs[k.replace("_", " ")].default_value = v
    return m


M = {
    "structure": mat("structure", (1.0, 0.36, 0.02), 0.0, 0.30, Coat_Weight=0.3, Coat_Roughness=0.1),
    "fixed": mat("fixed", (0.55, 0.57, 0.63), 0.0, 0.5),
    "skin": mat("skin", (0.55, 0.62, 0.72), 0.0, 0.2, alpha=0.05),
    "servo": mat("servo", (0.70, 0.72, 0.76), 0.55, 0.35),
    "plate": mat("plate", (0.92, 0.93, 0.95), 1.0, 0.25),
    "battery": mat("battery", (0.04, 0.12, 0.55), 0.0, 0.3),
    "protection": mat("protection", (0.03, 0.40, 0.12), 0.0, 0.4),
    "xbee": mat("xbee", (0.05, 0.38, 0.14), 0.0, 0.4),
    "camera": mat("camera", (0.03, 0.03, 0.035), 0.0, 0.4),
    "patch": mat("patch", (0.10, 0.18, 0.12), 0.0, 0.45),
    "strut": mat("strut", (0.88, 0.89, 0.91), 1.0, 0.34),
    "wheel": mat("wheel", (0.88, 0.89, 0.91), 1.0, 0.30),
}
M["skin"].blend_method = "BLEND" if hasattr(M["skin"], "blend_method") else None


def load(path, names_to_mat, smooth=False, bevel=0.0):
    before = set(bpy.data.objects.keys())
    bpy.ops.wm.obj_import(filepath=str(path), forward_axis="Y", up_axis="Z")
    obs = [bpy.data.objects[k] for k in bpy.data.objects.keys() if k not in before]
    for ob in obs:
        key = next((v for k, v in names_to_mat.items() if ob.name.startswith(k)), None) or "fixed"
        ob.data.materials.clear(); ob.data.materials.append(M[key])
        bpy.context.view_layer.objects.active = ob
        if smooth:
            sub = ob.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
            sm = ob.modifiers.new("smooth", "SMOOTH"); sm.factor = 0.7; sm.iterations = 12
            for m in list(ob.modifiers):
                bpy.ops.object.modifier_apply(modifier=m.name)
            sm2 = ob.modifiers.new("smooth2", "SMOOTH"); sm2.factor = 0.5; sm2.iterations = 6
            bpy.ops.object.modifier_apply(modifier=sm2.name)
            bpy.ops.object.shade_smooth()
        elif bevel:
            bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = bevel; bv.segments = 2
            bpy.ops.object.modifier_apply(modifier=bv.name)
    return obs


load(GEOM / f"{STEM}_structure.obj", {"structure": "structure"}, smooth=True)
load(GEOM / f"{STEM}_fixed.obj", {"fixed": "fixed"})          # no bevel: the voxel surface is non-manifold where cells touch along an edge, and the bevel modifier turns that into large artefacts
if SKIN:
    load(GEOM / f"{STEM}_skin.obj", {"skin": "skin"})
load(GEOM / f"{STEM}_context.obj", {"servo": "servo", "plate": "plate", "battery": "battery", "protection": "protection", "camera": "camera", "xbee": "xbee", "patch": "patch"}, bevel=0.2)
if WHEELS:
    for nm, mk in (("struts", "strut"), ("wheels", "wheel")):
        p = ROOT / "hardware" / "assembly" / "out" / "blender" / f"{nm}.stl"
        if p.exists():
            bpy.ops.wm.stl_import(filepath=str(p)); ob = bpy.context.selected_objects[0]
            ob.data.materials.clear(); ob.data.materials.append(M[mk]); bpy.ops.object.shade_smooth()

# the body envelope as a thin frame, and a floor for shadows
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 30)); env = bpy.context.object; env.scale = (140, 140, 60); env.name = "envelope"
bpy.ops.object.transform_apply(scale=True)          # the wireframe modifier works in the object's own units: apply the scale first, or 0.5 means 70 mm
wf = env.modifiers.new("wire", "WIREFRAME"); wf.thickness = 0.4; wf.use_replace = True
env.data.materials.append(mat("envelope", (0.85, 0.87, 0.92), 0.0, 0.5))
fl = bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -34 if WHEELS else 3)); fl = bpy.context.object
fl.data.materials.append(mat("floor", (0.20, 0.21, 0.24), 0.0, 0.8))

# light and world
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.16, 0.18, 0.22, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
scene.world = w
for nm, loc, e in (("key", (400, 300, 700), 3.2), ("fill", (-500, -200, 300), 1.4)):
    ld = bpy.data.lights.new(nm, "SUN"); ld.energy = e; ld.angle = math.radians(8)
    lo = bpy.data.objects.new(nm, ld); scene.collection.objects.link(lo)
    lo.rotation_euler = (Vector((0, 0, 30)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=50, ortho=None):
    cam = bpy.data.cameras.new("cam"); cam.lens = lens; cam.sensor_width = 36; cam.clip_start = 1; cam.clip_end = 20000
    if ortho:
        cam.type = "ORTHO"; cam.ortho_scale = ortho
    ob = bpy.data.objects.new("cam", cam); scene.collection.objects.link(ob); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); scene.camera = ob


def orbit(az, el, dist, target=(0, 0, 30)):
    a, e = math.radians(az), math.radians(el)
    return Vector(target) + dist * Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))


if VIEW == "iso": camera(orbit(52, 32, 520), (0, 0, 28), 50)
elif VIEW == "isorear": camera(orbit(232, 32, 520), (0, 0, 28), 50)
elif VIEW == "top": camera((0, 0, 900), (0, 0, 30), 50, ortho=225); scene.camera.rotation_euler = (0, 0, 0)
elif VIEW == "end": camera(orbit(90, 12, 560), (0, 0, 28), 50)
elif VIEW == "side": camera(orbit(0, 12, 560), (0, 0, 28), 50)
else: raise SystemExit(f"unknown VIEW {VIEW}")

scene.render.engine = "CYCLES"; scene.cycles.samples = SAMPLES; scene.cycles.device = "CPU"
scene.cycles.use_denoising = True; scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.max_bounces = 8; scene.cycles.transparent_max_bounces = 16
scene.render.resolution_x, scene.render.resolution_y = RES; scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
out = ROOT / "docs" / "images" / f"structure-{STEM}-{VIEW}{os.environ.get('SUFFIX', '')}.png"
scene.render.filepath = str(out); scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"
bpy.ops.render.render(write_still=True)
print("wrote", out)
if os.environ.get("EXPORT", "off").lower() == "on":                      # the smoothed geometry as a glTF binary, viewable in any 3D viewer (the floor, the frame and the lights are left out)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name not in ("envelope",) and not ob.name.startswith("Plane"):
            ob.select_set(True)
    glb = GEOM / f"structure-{STEM}.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True)
    print("exported", glb)
