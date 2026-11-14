"""Blender (Cycles) render of the interpreted nanorover: forged-carbon body, IXOLAR cells, windows, struts and wheels at the 25 degree stance.

Run from the repository root, after hardware/assembly/blender_export.py:
    VIEW=hero ~/tools/blender-4.5.9-linux-x64/blender -b -P hardware/assembly/blender_render.py
VIEW is one of hero, rear, top, detail, cells, window (default hero); SAMPLES (default 96), RES (default 1600x1000) and DEVICE (cpu, the default, or gpu: Metal on a Mac) LED (off, the default, or on) and SUFFIX (a name suffix for the output, for example -lit) are optional.  Output: docs/images/rover-<view>.png.
1 Blender unit = 1 mm.  The body is a 140 x 140 x 60 mm block with 0.8 mm edges, NOT the real shell (hardware/body/block.py is only the cavity volume);
the cells, panes and windows are laid on its faces from the same numbers as layout.py, cell_pocket.py and cell_endface.py.  Not modelled: lid screws and
seals, hub studs and rings, the lamp, the beamsplitter, anything inside.  The forged-carbon pattern is procedural (chips of random orientation, each with
its own anisotropic highlight direction); its chip size is a choice, not a measurement.
"""
import math
import os
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Vector

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "hardware" / "assembly" / "out" / "blender"
GAP = (140 - 26 - 87.2) / 3
T = 0.2                                  # cells and panes stand this far proud of the carbon (flush in the design)
VIEW = os.environ.get("VIEW", "hero")
SAMPLES = int(os.environ.get("SAMPLES", "96"))
RES = [int(v) for v in os.environ.get("RES", "1600x1000").split("x")]
GROUND_Z = -32.1                         # wheel bottoms at the 25 degree stance

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ---------------------------------------------------------------- materials
def principled(name, base, metallic=0.0, rough=0.5, **extra):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    for k, v in extra.items():
        b.inputs[k.replace("_", " ")].default_value = v
    return m


def forged_carbon(chip=9.0, layers=5, seed=3):
    """chips of random orientation: each layer is a 3D Voronoi stretched along its own random axis; a coarse Voronoi picks which layer shows where.
    Each chip gets a random tone and a random anisotropic-highlight rotation, and is darker at its boundary; a clear coat sits on top."""
    rnd = random.Random(seed)
    m = bpy.data.materials.new("forged carbon"); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    bsdf = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    sel = N.new("ShaderNodeTexVoronoi"); sel.voronoi_dimensions = "2D"; sel.inputs["Scale"].default_value = 1.0 / (chip * 2.0)
    L.new(tc.outputs["UV"], sel.inputs["Vector"])
    selv = N.new("ShaderNodeSeparateColor"); L.new(sel.outputs["Color"], selv.inputs["Color"])
    sums = {}
    for i in range(layers):
        mp = N.new("ShaderNodeMapping")
        mp.inputs["Rotation"].default_value = (0, 0, rnd.uniform(0, 3.1416))
        mp.inputs["Scale"].default_value = (1.0 / (chip * 3.0), 1.0 / (chip * 0.7), 1.0)     # about 4:1, long along the layer's own x, flat in the face
        L.new(tc.outputs["UV"], mp.inputs["Vector"])
        v1 = N.new("ShaderNodeTexVoronoi"); v1.voronoi_dimensions = "2D"; v1.inputs["Scale"].default_value = 1.0; L.new(mp.outputs["Vector"], v1.inputs["Vector"])
        v2 = N.new("ShaderNodeTexVoronoi"); v2.voronoi_dimensions = "2D"; v2.feature = "DISTANCE_TO_EDGE"; v2.inputs["Scale"].default_value = 1.0; L.new(mp.outputs["Vector"], v2.inputs["Vector"])
        cs = N.new("ShaderNodeSeparateColor"); L.new(v1.outputs["Color"], cs.inputs["Color"])
        mp2 = N.new("ShaderNodeMapping"); mp2.inputs["Rotation"].default_value = mp.inputs["Rotation"].default_value
        mp2.inputs["Scale"].default_value = (1.0 / (chip * 2.5), 1.0 / 0.45, 1.0); L.new(tc.outputs["UV"], mp2.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "2D"; nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 2.0; L.new(mp2.outputs["Vector"], nz.inputs["Vector"])
        # mask: this layer shows where the selector's random value falls in its slice
        lo = N.new("ShaderNodeMath"); lo.operation = "GREATER_THAN"; lo.inputs[1].default_value = i / layers; L.new(selv.outputs["Red"], lo.inputs[0])
        hi = N.new("ShaderNodeMath"); hi.operation = "LESS_THAN"; hi.inputs[1].default_value = (i + 1) / layers + (1e-3 if i == layers - 1 else 0); L.new(selv.outputs["Red"], hi.inputs[0])
        mask = N.new("ShaderNodeMath"); mask.operation = "MULTIPLY"; L.new(lo.outputs[0], mask.inputs[0]); L.new(hi.outputs[0], mask.inputs[1])
        for src, kind in ((cs.outputs["Red"], "tone"), (v2.outputs["Distance"], "edge"), (nz.outputs["Fac"], "streak")):
            w = N.new("ShaderNodeMath"); w.operation = "MULTIPLY"; L.new(src, w.inputs[0]); L.new(mask.outputs[0], w.inputs[1])
            if kind not in sums: sums[kind] = w.outputs[0]
            else:
                a_ = N.new("ShaderNodeMath"); a_.operation = "ADD"; L.new(sums[kind], a_.inputs[0]); L.new(w.outputs[0], a_.inputs[1]); sums[kind] = a_.outputs[0]
    tone_sum, edge_sum, streak_sum = sums["tone"], sums["edge"], sums["streak"]
    ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (0.006, 0.006, 0.007, 1); ramp.color_ramp.elements[1].color = (0.15, 0.155, 0.17, 1)
    L.new(tone_sum, ramp.inputs["Fac"])
    edge = N.new("ShaderNodeMapRange"); edge.inputs["From Min"].default_value = 0.0; edge.inputs["From Max"].default_value = 0.10; edge.inputs["To Min"].default_value = 0.25; edge.inputs["To Max"].default_value = 1.0
    edge.clamp = True; L.new(edge_sum, edge.inputs["Value"])
    dark = N.new("ShaderNodeMix"); dark.data_type = "RGBA"; dark.blend_type = "MULTIPLY"; dark.inputs["Factor"].default_value = 1.0
    L.new(ramp.outputs["Color"], dark.inputs["A"]); L.new(edge.outputs["Result"], dark.inputs["B"]) if False else None
    edge_rgb = N.new("ShaderNodeCombineColor"); [L.new(edge.outputs["Result"], edge_rgb.inputs[k]) for k in ("Red", "Green", "Blue")]
    L.new(edge_rgb.outputs["Color"], dark.inputs["B"])
    sk = N.new("ShaderNodeMapRange"); sk.inputs["From Min"].default_value = 0.3; sk.inputs["From Max"].default_value = 0.7; sk.inputs["To Min"].default_value = 0.55; sk.inputs["To Max"].default_value = 1.25; sk.clamp = True
    L.new(streak_sum, sk.inputs["Value"])
    sk_rgb = N.new("ShaderNodeCombineColor"); [L.new(sk.outputs["Result"], sk_rgb.inputs[k]) for k in ("Red", "Green", "Blue")]
    streaked = N.new("ShaderNodeMix"); streaked.data_type = "RGBA"; streaked.blend_type = "MULTIPLY"; streaked.inputs["Factor"].default_value = 1.0
    L.new(dark.outputs["Result"], streaked.inputs["A"]); L.new(sk_rgb.outputs["Color"], streaked.inputs["B"])
    L.new(streaked.outputs["Result"], bsdf.inputs["Base Color"])
    tan = N.new("ShaderNodeTangent"); tan.direction_type = "RADIAL"; tan.axis = "Z"
    L.new(tan.outputs["Tangent"], bsdf.inputs["Tangent"])
    L.new(tone_sum, bsdf.inputs["Anisotropic Rotation"])
    bsdf.inputs["Anisotropic"].default_value = 0.9
    bsdf.inputs["Roughness"].default_value = 0.30
    bsdf.inputs["Metallic"].default_value = 0.55
    bsdf.inputs["Coat Weight"].default_value = 0.6
    bsdf.inputs["Coat Roughness"].default_value = 0.03        # the coat keeps the geometric normal, so the chip bump shows only in the layer beneath
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.06; bump.inputs["Distance"].default_value = 0.2
    L.new(edge.outputs["Result"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def solar_cell():
    """Monocrystalline silicon under a clear polymer film: a near-black cell whose colour comes from its anti-reflection coating (a thin film, modelled with
    Blender's thin-film layer: silicon nitride, about 75 nm, index 2.0, which reflects blue and purple at different angles), under a glossy laminate with a
    slight waviness.  No front gridlines or busbars: the contacts of these parts are both on the back (SM940K09L datasheet, page 3), which suggests back-contact cells."""
    m = bpy.data.materials.new("IXOLAR cell"); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.020, 0.021, 0.026, 1)                 # product photos of the SM940K09L and KXOB parts: near-black, matte, no blue cast
    b.inputs["Metallic"].default_value = 0.0; b.inputs["Roughness"].default_value = 0.32
    b.inputs["Specular IOR Level"].default_value = 0.5
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35            # facing ratio: the coating's colour moves from blue to violet toward grazing angles
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.50, 0.40, 0.85, 1); cr.color_ramp.elements[1].color = (0.80, 0.85, 1.0, 1)      # a faint cool sheen toward grazing angles only
    L.new(lw.outputs["Facing"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Specular Tint"])
    b.inputs["Thin Film Thickness"].default_value = 78.0; b.inputs["Thin Film IOR"].default_value = 2.0
    b.inputs["Coat Weight"].default_value = 0.30; b.inputs["Coat Roughness"].default_value = 0.22; b.inputs["Coat IOR"].default_value = 1.58      # a satin film (the SM940K09L front looks matte in its photo; index assumed)
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / 60.0, 1 / 60.0, 1 / 60.0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "3D"; nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 1.0; L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.5
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Coat Normal"])         # the film is slightly wavy; the cell beneath is flat
    return m


MAT = {
    "carbon": forged_carbon(),
    "cell": solar_cell(),
    "film": principled("laminate margin", (0.009, 0.010, 0.013), metallic=0.0, rough=0.42),     # photos show no pale border: the part is black edge to edge
    "glass": principled("camera pane", (0.0, 0.0, 0.0), metallic=0.0, rough=0.04, Coat_Weight=0.5, Coat_Roughness=0.02),
    "bezel": principled("bezel", (0.18, 0.18, 0.2), metallic=1.0, rough=0.28),
    "hood": principled("lens hood and mask ring", (0.004, 0.004, 0.005), metallic=0.0, rough=0.55),
    "lens": principled("M12 lens front", (0.0, 0.0, 0.0), metallic=0.0, rough=0.10, Coat_Weight=0.25, Coat_Roughness=0.12),
    "iris": principled("lens inner element", (0.004, 0.006, 0.022), metallic=0.0, rough=0.12, Coat_Weight=0.3, Coat_Roughness=0.08),
    "film": principled("laminate margin", (0.009, 0.010, 0.013), metallic=0.0, rough=0.42),
    "smoked": principled("smoked dead-front film", (0.010, 0.0095, 0.008), metallic=0.0, rough=0.12, Coat_Weight=0.4, Coat_Roughness=0.05),
    "led": principled("LED lit through the film", (1.0, 0.86, 0.62), metallic=0.0, rough=0.3, Emission_Color=(1.0, 0.86, 0.62, 1.0), Emission_Strength=6.0),
    "irink": principled("ranging sensor package behind clear glass", (0.012, 0.012, 0.015), metallic=0.0, rough=0.35),
    "plug": principled("RF window plug", (0.025, 0.032, 0.03), metallic=0.0, rough=0.45),
    "strut": principled("strut", (0.88, 0.89, 0.91), metallic=1.0, rough=0.34, Anisotropic=0.5),    # bare machined 6061 (docs/strut-spec.md)
    "wheel": principled("wheel", (0.88, 0.89, 0.91), metallic=1.0, rough=0.30, Anisotropic=0.6),
    "ground": principled("ground", (0.62, 0.63, 0.65), metallic=0.0, rough=0.55),
}


# ---------------------------------------------------------------- geometry
def make(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob); me.materials.append(MAT[mat]); return ob


def add_box(bm, x0, x1, y0, y1, z0, z1):
    r = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=r["verts"], vec=(x1 - x0, y1 - y0, z1 - z0))
    bmesh.ops.translate(bm, verts=r["verts"], vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def laminate(bms, face, a0, a1, b0, b1, m):
    """one laminated part on a face: the film outline (a0..a1 by b0..b1) and the cell inset by m = (left, right, bottom, top) on top of it.
    The lids use (x, y); the end faces use (x, z), with the part standing on the +y or -y face."""
    film, act = bms
    l, r, bt, tp = m
    if face in ("+z", "-z"):
        z0 = 60.0 if face == "+z" else -T
        add_box(film, a0, a1, b0, b1, z0, z0 + T); add_box(act, a0 + l, a1 - r, b0 + bt, b1 - tp, z0, z0 + T + 0.05)
    else:
        y0 = 70.0 if face == "+y" else -70.0 - T
        add_box(film, a0, a1, y0, y0 + T, b0, b1); add_box(act, a0 + l, a1 - r, y0, y0 + T + 0.05 if face == "+y" else y0 + T, b0 + bt, b1 - tp)


def cells():
    """Margins (film around the cell): the SM940K09L drawing gives 0.75 mm top and bottom and about 0.11 and 0.21 mm at the ends (page 3);
    the SM401K08TF and SM531K08TFS drawings were not found, so they get the same 0.75 mm all round (assumption)."""
    film, act = bmesh.new(), bmesh.new(); e = 0.1                 # each part inset by 0.1 mm per side: the seams show the carbon
    s940 = (0.11, 0.21, 0.75, 0.75); big = (0.75, 0.75, 0.75, 0.75)
    for face, z0 in (("+z", 60.0), ("-z", -T)):
        for k in range(3):
            x0 = -66.75 + 44.5 * k
            laminate((film, act), face, x0 + e, x0 + 44.5 - e, 45 + e, 66.5 - e, s940); laminate((film, act), face, x0 + e, x0 + 44.5 - e, -66.5 + e, -45 - e, s940)
        laminate((film, act), face, -66.75 + e, -26.75 - e, -45, 45, big); laminate((film, act), face, 26.75 + e, 66.75 - e, -45, 45, big); laminate((film, act), face, -26 + e, 26 - e, -44.5, 44.5, big)
    for face, start in (("+y", 70 - 2 * GAP - 26 - 87.2), ("-y", -70 + 2 * GAP + 26)):
        for k in range(4):
            x0 = start + 21.8 * k
            laminate((film, act), face, x0, x0 + 21.5, 7.75, 52.25, (0.75, 0.75, 0.11, 0.21))      # standing: the 44.5 mm side is vertical, so the end margins are top and bottom
    make("cell films", film, "film")
    return make("cells", act, "cell")


def cylinder_y(name, cx, cz, r, y0, y1, mat, verts=96):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=r, depth=abs(y1 - y0))
    for v in bm.verts:
        v.co = (v.co.x, v.co.z, -v.co.y)       # cone axis z -> y
    bmesh.ops.translate(bm, verts=bm.verts, vec=(cx, (y0 + y1) / 2, cz))
    return make(name, bm, mat)


def body():
    bm = bmesh.new(); add_box(bm, -70, 70, -70, 70, 0, 60)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:                                   # planar per face, in millimetres: chips lie in the surface plane
        n = f.normal; ax = max(range(3), key=lambda i: abs(n[i])); a, b = [i for i in range(3) if i != ax]
        off = 200.0 * (2 * (n[ax] > 0) + ax)             # a different patch of the pattern on each face
        for lp in f.loops: lp[uv].uv = (lp.vert.co[a] + off, lp.vert.co[b] + off)
    ob = make("body", bm, "carbon")
    bev = ob.modifiers.new("bevel", "BEVEL"); bev.width = 0.8; bev.segments = 4; bev.limit_method = "ANGLE"
    return ob


def smooth(ob, angle=30):
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle)); ob.select_set(False)


def import_stl(name, mat):
    bpy.ops.wm.stl_import(filepath=str(STL / f"{name}.stl"))
    ob = bpy.context.selected_objects[0]; ob.name = name; ob.data.materials.append(MAT[mat]); ob.select_set(False); smooth(ob, 35); return ob


smooth(body(), 30)
cells()
wx = 70 - (GAP + 13)
cylinder_y("bezel", wx, 30, 14.6, 70.0, 70.0 + T, "bezel")
cylinder_y("pane", wx, 30, 13.0, 70.0, 70.0 + T + 0.25, "glass")
# behind the cover glass (drawn just in front of the pane, which is dark glass): the smoked dead-front annulus over the LED ring, 7 LEDs (off), the lens hood, the lens, the ranging sensor's IR ink
y0 = 70.0 + T + 0.25
cylinder_y("film ring", wx, 30, 11.8, y0, y0 + 0.08, "smoked")
# LED=off (default): the LEDs do not appear at all, as behind a real dead-front film; LED=on draws them lit (warm white, emissive) for a photograph-with-lamp view
if os.environ.get("LED", "off").lower() == "on":
    for deg in (0, 45, 135, 180, 225, 315):        # six LEDs at 10 mm radius; the top slot is the ranging sensor's, the bottom is empty
        ang = math.radians(deg)
        cylinder_y(f"led{deg}", wx + 10.0 * math.cos(ang), 30 + 10.0 * math.sin(ang), 1.5, y0 + 0.08, y0 + 0.14, "led", verts=24)
cylinder_y("hood", wx, 30, 8.2, y0 + 0.08, y0 + 0.2, "hood")
cylinder_y("lens", wx, 30, 6.3, y0 + 0.2, y0 + 0.3, "lens")
cylinder_y("lens inner", wx, 30, 3.4, y0 + 0.3, y0 + 0.4, "iris")
bm = bmesh.new(); add_box(bm, wx - 3.2, wx + 3.2, y0 + 0.08, y0 + 0.2, 40.5 - 1.5, 40.5 + 1.5); make("ranging sensor", bm, "irink")
bm = bmesh.new(); add_box(bm, -wx - 13.5, -wx + 13.5, -70 - T, -70, 16.5, 43.5); make("RF plug", bm, "plug")
import_stl("struts", "strut"); import_stl("wheels", "wheel")
bm = bmesh.new(); add_box(bm, -3000, 3000, -3000, 3000, GROUND_Z - 1, GROUND_Z); make("ground", bm, "ground")

# ---------------------------------------------------------------- lights: soft boxes (visible only in reflections) and a world fill
def softbox(name, loc, size, strength, target=(0, 0, 12)):
    bm = bmesh.new(); add_box(bm, -size[0] / 2, size[0] / 2, -size[1] / 2, size[1] / 2, 0, 1)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength; em.inputs["Color"].default_value = (1, 0.98, 0.95, 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0]); me.materials.append(m)
    ob.location = loc
    d = Vector(target) - Vector(loc); ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    ob.visible_camera = False; return ob


softbox("key", (-380, 520, 520), (420, 300), 6.0)
softbox("strip", (620, -150, 260), (110, 520), 7.0)
softbox("top", (260, -240, 900), (400, 300), 2.2)
softbox("rim", (0, -700, 300), (500, 180), 4.0)
w = bpy.data.worlds.new("world"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.16, 0.17, 0.19, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
scene.world = w

# ---------------------------------------------------------------- camera
def camera(loc, target, lens=55, dof=None, ortho=None):
    cam = bpy.data.cameras.new("cam"); cam.lens = lens; cam.sensor_width = 36; cam.clip_start = 1; cam.clip_end = 20000
    if ortho: cam.type = "ORTHO"; cam.ortho_scale = ortho
    if dof: cam.dof.use_dof = True; cam.dof.focus_distance = dof; cam.dof.aperture_fstop = 6.3
    ob = bpy.data.objects.new("cam", cam); scene.collection.objects.link(ob); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); scene.camera = ob


def orbit(az, el, dist, target=(0, 0, 12)):
    a, e = math.radians(az), math.radians(el)
    return Vector(target) + dist * Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))


if VIEW == "hero": camera(orbit(38, 20, 640), (0, 0, 8), 55)
elif VIEW == "rear": camera(orbit(218, 20, 640), (0, 0, 8), 55)
elif VIEW == "top": camera((0, 0, 1400), (0, 0, 0), 55, ortho=330); scene.camera.rotation_euler = (0, 0, 0)         # image up = +y, the camera end
elif VIEW == "detail":
    tgt = (45, 70, 38); loc = orbit(32, 18, 230, tgt); camera(loc, tgt, 85, dof=(loc - Vector(tgt)).length)
elif VIEW == "window":
    tgt = (wx, 70, 33); loc = orbit(90, 10, 150, tgt); camera(loc, tgt, 100, dof=(loc - Vector(tgt)).length)
elif VIEW == "cells":
    tgt = (20, 30, 60); loc = orbit(24, 24, 190, tgt); camera(loc, tgt, 100, dof=(loc - Vector(tgt)).length)
else: raise SystemExit(f"unknown VIEW {VIEW}")

# ---------------------------------------------------------------- render
scene.render.engine = "CYCLES"; scene.cycles.samples = SAMPLES
# DEVICE=cpu (default) or DEVICE=gpu: gpu uses Metal on an Apple Silicon Mac (CUDA, OptiX or HIP elsewhere), falling back to the CPU if no GPU is found
scene.cycles.device = "CPU"
if os.environ.get("DEVICE", "cpu").lower() == "gpu":
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("METAL", "OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
            prefs.refresh_devices() if hasattr(prefs, "refresh_devices") else prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == kind]
        except Exception:
            continue
        if gpus:
            for d in prefs.devices:
                d.use = d.type in (kind, "CPU") if kind == "METAL" else d.type == kind     # on Apple Silicon the CPU cores help the GPU a little
            scene.cycles.device = "GPU"; print("render device:", kind, [d.name for d in gpus]); break
    else:
        print("no GPU device found; rendering on the CPU")
scene.cycles.use_denoising = True; scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.glossy_bounces = 4; scene.cycles.max_bounces = 6; scene.cycles.diffuse_bounces = 2; scene.cycles.transmission_bounces = 2
scene.render.resolution_x, scene.render.resolution_y = RES; scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
out = ROOT / "docs" / "images" / f"rover-{VIEW}{os.environ.get('SUFFIX', '')}.png"     # SUFFIX (for example -lit) keeps variants of a view apart
scene.render.filepath = str(out); scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("wrote", out)
