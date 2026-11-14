"""Section renders of the catch-and-cam lid joint (hardware/body/lid_cams.py), unlocked and locked side by side, from the CAD parts (so nothing here is a sketch: the parts are the solids that
lid_cams.py checks for interference).

Run: VIEW=axial ~/tools/blender-4.5.9-linux-x64/blender -b -P hardware/assembly/blender_cam_sections.py      (VIEW = axial or radial; SAMPLES, RES optional)
  axial : the joint cut along the cam's axis through the catch (the plane y = 40), seen from inside the body looking out: the hub face is on the right.
  radial: the joint cut across the cam through the catch (the plane x = 60), seen from the hub face looking in: shows the spiral groove and where the catch's head sits in it.
Writes docs/images/cam-joint-<view>.png. Orthographic camera.
"""
import math, os
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

VIEW = os.environ.get("VIEW", "axial")
SAMPLES = int(os.environ.get("SAMPLES", "64"))
RES = [int(v) for v in os.environ.get("RES", "1600x900").split("x")]
ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "hardware" / "body" / "out" / "cam_joint"
Y0, ZC, XC = 40.0, 38.5, 60.0
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name, base, metallic=0.0, rough=0.45, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1); b.inputs["Metallic"].default_value = metallic; b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = 2.0
    return m


M = dict(body=mat("body", (0.12, 0.12, 0.13)), lid=mat("lid", (0.12, 0.26, 0.55)), cam=mat("cam", (0.95, 0.45, 0.05), 0.3, 0.35), catch=mat("catch", (0.75, 0.76, 0.8), 1.0, 0.25),
         seam_gasket=mat("seam gasket", (0.8, 0.08, 0.05), 0, 0.7), cam_gasket=mat("cam gasket", (0.55, 0.05, 0.08), 0, 0.7), text=mat("text", (0.03, 0.03, 0.03), 0, 0.9),
         line=mat("line", (0.2, 0.2, 0.2), 0, 0.9), lidt=mat("lidt", (0.10, 0.25, 0.60), 0, 0.9), bodyt=mat("bodyt", (0.3, 0.3, 0.32), 0, 0.9), camt=mat("camt", (0.85, 0.40, 0.02), 0, 0.9), catcht=mat("catcht", (0.45, 0.47, 0.52), 0, 0.9), gaskett=mat("gaskett", (0.8, 0.08, 0.05), 0, 0.9), green=mat("green", (0.1, 0.8, 0.2), 0, 0.5, emit=(0.1, 0.8, 0.2)), red=mat("red", (0.95, 0.1, 0.1), 0, 0.5, emit=(0.95, 0.1, 0.1)))
# the second state sits beside the first: x +36 for the axial view, y +34 for the radial view
SHIFT = Vector((36, 0, 0)) if VIEW == "axial" else Vector((0, 34, 0))
FACE = Vector((0, -1, 0)) if VIEW == "axial" else Vector((1, 0, 0))            # the direction towards the camera
for state, shift in (("unlocked", Vector()), ("locked", SHIFT)):
    for f in sorted(STL.glob(f"{VIEW}_{state}_*.stl")):
        bpy.ops.wm.stl_import(filepath=str(f)); ob = bpy.context.selected_objects[0]
        name = f.stem.split("_", 2)[2]
        ob.data.materials.append(M[name]); ob.location = shift; ob.name = f"{state} {name}"
        bpy.context.view_layer.objects.active = ob; bpy.ops.object.shade_smooth(); ob.select_set(False)


def label(text, loc, size=1.9, material="text", rot=None):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = text; cu.size = size; cu.align_x = "CENTER"
    ob = bpy.data.objects.new("label", cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(M[material]); ob.location = loc
    ob.rotation_euler = rot or ((math.radians(90), 0, 0) if VIEW == "axial" else (math.radians(90), 0, math.radians(90)))
    ob.visible_shadow = False
    return ob


def line(p0, p1, r=0.08, material="line"):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    me = bpy.data.meshes.new("l"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("line", me); bpy.context.collection.objects.link(ob); ob.data.materials.append(M[material]); ob.location = p0
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def pt(h, z, shift=Vector(), depth=0.0):
    """A point in the view plane: h = x for the axial view, y for the radial view; in front of the cut by `depth`."""
    return (Vector((h, Y0 - 1 - depth, z)) if VIEW == "axial" else Vector((XC + 1 + depth, h, z))) + shift


if VIEW == "axial":
    for state, shift, hub in (("UNLOCKED", Vector(), 70.5), ("LOCKED", SHIFT, 70.0)):
        label(state, pt(57, 66.5, shift), 2.6)
        label("hub face", pt(hub - 2, 28.2, shift), 1.4)
    label("unlocked: the lid rides on the seam gasket, 0.4 mm proud;", pt(57, 26.4), 1.3); label("the cam stands 0.5 mm out of the hub face on its gasket", pt(57, 24.6), 1.3)
    label("locked: the cam is turned 180 degrees and threaded in flush;", pt(93, 26.4, Vector()), 1.3); label("the catch is drawn down 0.4 mm, both gaskets squeezed", pt(93, 24.6), 1.3)
    for i, (txt, m) in enumerate((("lid and its ear", "lidt"), ("body", "bodyt"), ("cam", "camt"), ("catch (steel)", "catcht"), ("seam gasket", "gaskett"), ("cam gasket", "gaskett"))):
        label(txt, pt(112, 62.0 - 3.2 * i), 1.7, m)
else:
    for state, shift in (("UNLOCKED", Vector()), ("LOCKED", SHIFT)):
        label(state, pt(Y0, 63.8, shift), 2.6)
    label("catch head at the groove's throat,", pt(Y0, 28.4), 1.4); label("3.4 mm from the cam's axis", pt(Y0, 26.6), 1.4)
    label("cam turned 180 degrees: the groove has drawn", pt(Y0 + 34, 28.4), 1.4); label("the head to 3.0 mm from the axis (the lid is down 0.4 mm)", pt(Y0 + 34, 26.6), 1.4)
    label('colours as in the axial view: lid blue, body grey, cam orange, catch steel', pt(Y0 + 17, 59.5 + 3.4), 1.2)

# ---- world, lights, camera ----
w = bpy.data.worlds.new("w"); scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.88, 0.89, 0.91, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.2
sd = bpy.data.lights.new("sun", "SUN"); sd.energy = 2.5; so = bpy.data.objects.new("sun", sd); bpy.context.collection.objects.link(so)
so.rotation_euler = (Vector(FACE) + Vector((0.3, 0.2, 0.7))).to_track_quat("Z", "Y").to_euler()
cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = 84 if VIEW == "axial" else 76
co = bpy.data.objects.new("cam", cam); bpy.context.collection.objects.link(co); scene.camera = co
if VIEW == "axial":
    ctr = Vector((75.0, Y0, 47.0)); co.location = ctr + Vector((0, -200, 0)); co.rotation_euler = (math.radians(90), 0, 0)
else:
    ctr = Vector((XC, Y0 + 17, 45.0)); co.location = ctr + Vector((200, 0, 0)); co.rotation_euler = (math.radians(90), 0, math.radians(90))
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = RES; scene.view_settings.view_transform = "Standard"
out = ROOT / "docs" / "images" / f"cam-joint-{VIEW}.png"
scene.render.filepath = str(out); bpy.ops.render.render(write_still=True); print("wrote", out)
