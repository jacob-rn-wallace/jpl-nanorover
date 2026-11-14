"""Rough 3D cutaway renders of the three ways to turn a horizontal screw's pull into a downward force on the lid (docs/mechanical-spec.md item 8).

Run: CONCEPT=A ~/tools/blender-4.5.9-linux-x64/blender -b -P hardware/assembly/blender_joint_concepts.py     (CONCEPT = A, B or C; SAMPLES, RES optional)
Each image shows one hub-face corner of the lid joint as a 14 mm thick slice, twice: loose (left, the lid resting on the uncompressed gasket) and tight (right, the screw or cam turned and the
gasket squeezed). Gap and gasket heights are exaggerated about three times so that they can be seen. u is the distance inward from the hub face (the x = 70 plane); z is height; the slice is 14 mm thick in y.
A: a wedge key (a separate tapered part, orange) that the screw pulls outward between a lid ear's foot and a ledge in the body.   B: a cam bolt (a bolt in the lid ear, a cam turned from the hub face).
C: a bell crank (an L-shaped lever, orange) that the screw pulls, whose other arm pushes down on a lug of the lid ear.   Colours: body dark grey, lid blue-grey, gasket red, screw steel, moving part orange.
This is an explanatory sketch, not a CAD design: sizes follow the layout (ears at u 8 to 12, the rim plane 7 mm below the lid face) but the details are illustrative.
"""
import math, os
from pathlib import Path
import bpy, bmesh
from mathutils import Matrix, Vector

CONCEPT = os.environ.get("CONCEPT", "A").upper()
SAMPLES = int(os.environ.get("SAMPLES", "48"))
RES = [int(v) for v in os.environ.get("RES", "1600x900").split("x")]
ROOT = Path(__file__).resolve().parents[2]
TH = 14.0                                  # slice thickness (y)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name, base, metallic=0.0, rough=0.5, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1); b.inputs["Metallic"].default_value = metallic; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = 1.5
    return m


M = dict(body=mat("body", (0.07, 0.07, 0.08), 0.0, 0.5), lid=mat("lid", (0.10, 0.20, 0.42), 0.0, 0.4), gasket=mat("gasket", (0.75, 0.08, 0.05), 0.0, 0.7),
         steel=mat("steel", (0.7, 0.71, 0.74), 1.0, 0.3), move=mat("moving part", (0.95, 0.45, 0.05), 0.2, 0.4), arrow_h=mat("pull", (0.1, 0.8, 0.2), 0, 0.4, emit=(0.1, 0.8, 0.2)),
         arrow_v=mat("force", (0.95, 0.1, 0.1), 0, 0.4, emit=(0.95, 0.1, 0.1)), text=mat("text", (0.02, 0.02, 0.02), 0, 0.9), lidt=mat("lidt", (0.10, 0.25, 0.60), 0, 0.9), bodyt=mat("bodyt", (0.25, 0.25, 0.27), 0, 0.9), gaskett=mat("gaskett", (0.80, 0.08, 0.05), 0, 0.9), movet=mat("movet", (0.85, 0.40, 0.02), 0, 0.9), steelt=mat("steelt", (0.4, 0.42, 0.46), 0, 0.9), cut=mat("cut face", (0.9, 0.9, 0.9), 0, 0.8))
OBJS = []


def mesh_obj(name, bm, material):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); ob.data.materials.append(M[material]); OBJS.append(ob)
    for p in me.polygons: p.use_smooth = False
    return ob


def prism(name, pts_uz, material, xoff, dz=0.0, du=0.0, y0=0.0, y1=TH):
    """A polygon in the (u, z) plane (u inward from the hub face) extruded along y."""
    bm = bmesh.new()
    vs0 = [bm.verts.new((xoff - (u + du), y0, z + dz)) for u, z in pts_uz]
    vs1 = [bm.verts.new((xoff - (u + du), y1, z + dz)) for u, z in pts_uz]
    n = len(pts_uz)
    bm.faces.new(vs0); bm.faces.new(vs1[::-1])
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, material)


def box(name, u0, u1, z0, z1, material, xoff, **kw):
    return prism(name, [(u0, z0), (u1, z0), (u1, z1), (u0, z1)], material, xoff, **kw)


def W(u, z, xoff, y=0.0):
    """World position of a point u mm inward from the hub face (the slice's x = xoff plane), at height z and depth y."""
    return Vector((xoff - u, y, z))


def cyl(name, p0, p1, r, material, n=40):
    """A cylinder from world point p0 to p1."""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    ob = mesh_obj(name, bm, material); ob.location = p0; ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def arrow(name, start, end, material, r=0.7):
    s, e = Vector(start), Vector(end); d = e - s; L = d.length
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=r, radius2=r, depth=L - 3 * r)
    for v in bm.verts: v.co.z += (L - 3 * r) / 2
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=2 * r, radius2=0, depth=3 * r, matrix=Matrix.Translation((0, 0, L - 1.5 * r)))
    ob = mesh_obj(name, bm, material); ob.location = s
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


AZ, EL = math.radians(14), math.radians(16)


def label(text, loc, size=3.0, material="text"):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = text; cu.size = size; cu.align_x = "CENTER"
    ob = bpy.data.objects.new("label", cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(M[material]); ob.location = loc
    ob.rotation_euler = (math.radians(90) - EL, 0, AZ); OBJS.append(ob)
    return ob


def gasket(xoff, loose):
    top = 52.2 + (2.2 if loose else 0.8)                  # exaggerated: 1.4 mm proud when loose, squeezed to 0.8 mm
    box("gasket", 3.0, 5.0, 52.2, top, "gasket", xoff)


def common(xoff, loose, z_floor):
    dz = 2.0 if loose else 0.0                             # the lid rests on the uncompressed gasket when loose (about 3 times the real gap)
    box("lid plate", 0.0, 28.0, 53.0, 60.0, "lid", xoff, dz=dz)
    gasket(xoff, loose)
    return dz


def build(xoff, loose):
    dz = common(xoff, loose, 36)
    if CONCEPT == "A":
        # body: wall, ledge, floor, backing; lid ear with a foot; the wedge key between the foot and the ledge; the screw
        box("wall", 0, 8, 36, 53, "body", xoff); box("ledge", 8, 17, 47, 49.5, "body", xoff); box("floor", 8, 28, 36, 41, "body", xoff); box("backing", 22, 28, 36, 53, "body", xoff)
        box("lid ear stem", 17.5, 21.5, 41.5, 53, "lid", xoff, dz=dz)
        k = math.tan(math.radians(15))
        prism("lid ear foot", [(9, 41.5), (17.5, 41.5), (17.5, 44.4 - 8.5 * k), (9, 44.4)], "lid", xoff, dz=dz)
        shift = 6.0 if loose else 0.0                      # the key sits further inboard when loose, and is pulled outward by the screw
        prism("wedge key", [(9, 47), (17, 47), (17, 44.4 - 8 * k), (9, 44.4)], "move", xoff, du=shift, dz=0.0)
        cyl("screw shank", W(-0.2, 45.7, xoff), W(15.0, 45.7, xoff), 1.0, "steel"); cyl("screw head", W(-1.6, 45.7, xoff), W(-0.2, 45.7, xoff), 1.9, "steel")
        if not loose:
            arrow("pull", W(7, 45.7, xoff, -3), W(1.0, 45.7, xoff, -3), "arrow_h", 0.5)
            arrow("clamp", W(24, 59.0, xoff, -3), W(24, 53.6, xoff, -3), "arrow_v", 0.6)
    elif CONCEPT == "B":
        box("lower body", 0, 28, 30, 34, "body", xoff); box("upper skin", 0, 2, 46, 53, "body", xoff); box("upper body", 8, 28, 46, 53, "body", xoff); box("backing", 10, 28, 34, 46, "body", xoff)
        box("lid ear", 2.0, 8.0, 46.0, 53.0, "lid", xoff, dz=dz)
        cyl("cam bolt shaft", W(5.0, 40.0 + dz, xoff), W(5.0, 47.0 + dz, xoff), 1.0, "steel")
        cyl("cam bolt head", W(5.0, 38.6 + dz, xoff), W(5.0, 40.0 + dz, xoff), 2.4, "steel")
        cyl("cam", W(0.0, 40.0, xoff), W(6.0, 40.0, xoff), 6.0, "move", n=48)
        ang = math.radians(0 if loose else 90)                # the screwdriver slot on the face: horizontal when loose, vertical when tight
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts: v.co = (v.co.x * 1.0, v.co.y * 10.0, v.co.z * 1.6)
        sl = mesh_obj("cam slot", bm, "body"); sl.location = W(-0.1, 40.0, xoff); sl.rotation_euler = (ang, 0, 0)
        if not loose:
            arrow("clamp", W(15, 59.0, xoff, -3), W(15, 53.6, xoff, -3), "arrow_v", 0.6)
        arrow("turn", W(-3, 48.5, xoff), W(-3, 46.5, xoff), "arrow_h", 0.5) if False else None
    else:
        box("wall", 0, 7, 36, 53, "body", xoff); box("floor", 7, 28, 36, 41, "body", xoff); box("backing", 22, 28, 36, 53, "body", xoff)
        box("lid ear stem", 15.0, 19.0, 43.0, 53.0, "lid", xoff, dz=dz); box("lid ear lug", 11.5, 15.0, 45.0, 47.0, "lid", xoff, dz=dz)
        cyl("pivot pin", W(9.5, 47.0, xoff, -1.2), W(9.5, 47.0, xoff, 3), 1.0, "steel")
        lever = prism("bell crank", [(8, 40.5), (11, 40.5), (11, 46.2), (15.8, 46.2), (15.8, 49.0), (8, 49.0)], "move", xoff)
        piv = W(9.5, 47.0, xoff, 0)                                           # turn about the pivot: put the object's origin there
        lever.data.transform(Matrix.Translation(-piv)); lever.location = piv
        lever.rotation_euler = (0, math.radians(-10 if loose else 0), 0)
        cyl("screw shank", W(-0.2, 42.5, xoff), W(11.0, 42.5, xoff), 1.0, "steel"); cyl("screw head", W(-1.6, 42.5, xoff), W(-0.2, 42.5, xoff), 1.9, "steel")
        if not loose:
            arrow("pull", W(7, 42.5, xoff, -3), W(1.0, 42.5, xoff, -3), "arrow_h", 0.5)
            arrow("clamp", W(24, 59.0, xoff, -3), W(24, 53.6, xoff, -3), "arrow_v", 0.6)
    return dz


TITLES = {"A": "A. Wedge key", "B": "B. Cam bolt", "C": "C. Bell crank"}
CAPTIONS = {"A": ("loose: the key is pulled back,\nthe lid rests on the thick gasket", "tight: the screw pulls the key outward,\nits taper pushes the ear's foot down, the gasket is squeezed"),
            "B": ("loose: the cam's slot is horizontal,\nthe lid rests on the thick gasket", "tight: the cam is turned 90 degrees from the hub face,\nit pulls the bolt down, the gasket is squeezed"),
            "C": ("loose: the lever is tipped up,\nthe lid rests on the thick gasket", "tight: the screw pulls the lever's lower arm out,\nits upper arm pushes the ear's lug down")}
build(-62.0, True); build(8.0, False)
label(TITLES[CONCEPT] + "  (gap and gasket exaggerated about 3 times)", (-27.0, -4.0, 71.0), 3.6)
label(CAPTIONS[CONCEPT][0], (-62.0 - 14.0, -4.0, 23.0), 2.4); label(CAPTIONS[CONCEPT][1], (8.0 - 14.0, -4.0, 23.0), 2.4)
label("hub face", (-62.0 + 4.0, -4.0, 27.5), 2.0); label("hub face", (8.0 + 4.0, -4.0, 27.5), 2.0)
for i, (txt, mt) in enumerate((("blue: lid and its ear", "lidt"), ("dark grey: body", "bodyt"), ("red: gasket", "gaskett"), ("orange: the moving part", "movet"), ("steel: screw, pin or bolt", "steelt"), ("green arrow: the screw's pull", "text"), ("red arrow: the lid pulled down", "text"))):
    label(txt, (36.0, -4.0, 68.0 - 4.2 * i), 2.1, mt)

# ---- world, light, camera ----
w = bpy.data.worlds.new("w"); scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.86, 0.87, 0.89, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
for name, loc, e in (("key", (-60, -90, 140), 4000), ("fill", (60, -60, 40), 1500)):
    ld = bpy.data.lights.new(name, "AREA"); ld.energy = e; ld.size = 80
    lo = bpy.data.objects.new(name, ld); bpy.context.collection.objects.link(lo); lo.location = loc
    lo.rotation_euler = (Vector(loc).to_track_quat("-Z", "Y")).to_euler()
cam = bpy.data.cameras.new("cam"); cam.lens = 60
co = bpy.data.objects.new("cam", cam); bpy.context.collection.objects.link(co); scene.camera = co
tgt = Vector((-24.0, 4.0, 45.0)); az, el, dist = AZ, EL, 320
co.location = tgt + dist * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
co.rotation_euler = (tgt - co.location).to_track_quat("-Z", "Y").to_euler()
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = RES; scene.view_settings.view_transform = "Standard"
out = ROOT / "docs" / "images" / f"lid-joint-{CONCEPT}-{ {'A': 'wedge-key', 'B': 'cam-bolt', 'C': 'bell-crank'}[CONCEPT] }.png"
scene.render.filepath = str(out); bpy.ops.render.render(write_still=True); print("wrote", out)
