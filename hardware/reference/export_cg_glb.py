#!/usr/bin/env python3
"""Export the CG nanorover (cg_nanorover.py) as a glTF binary for the browser sim (sim/public/rover_cg.glb) and a JSON of its joints.

Run from the repository root:   .venv/bin/python hardware/reference/export_cg_glb.py
Frames: the CAD has the window on its -y face and the hub nubs on +-x; the sim wants the window face forward.  Rover frame (X forward, Y left, Z up, mm, ground at the wheels' lowest point) = (-y_cad, +x_cad, z_cad + lift);
glTF (x, y, z) = (X, Z, -Y) / 1000 (Y up, metres), as in the sim's worldView.ts.
Nodes (rigid bodies; every mesh is stored relative to its joint origin so a node's rotation is the joint rotation): chassis (at the origin), strut_<lateral side><fore/aft> (origin = the pivot, rotation about the lateral axis posing the strut),
wheel_<...> (origin = the axle, a child of its strut; spins about the lateral axis).
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cg_nanorover as C  # noqa: E402

OUT = HERE.parent.parent / "sim" / "public"


def mesh_of(shapes, to_local):
    """one trimesh per colour; shapes is a list of build123d solids (CAD frame); to_local maps CAD points to the node's frame (rows of an (n,3) array, mm) -> metres, glTF axes."""
    by = {}
    for s in shapes:
        col = s.color
        key = tuple(round(c, 3) for c in tuple(col)[:3])
        v, f = s.tessellate(0.05, 0.3)
        v = np.array([[p.X, p.Y, p.Z] for p in v]); f = np.array(f)
        by.setdefault(key, []).append((to_local(v), f))
    meshes = []
    for key, items in by.items():
        vs, fs, off = [], [], 0
        for v, f in items:
            vs.append(v); fs.append(f + off); off += len(v)
        m = trimesh.Trimesh(np.vstack(vs), np.vstack(fs), process=False)
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=[*key, 1.0], metallicFactor=0.3, roughnessFactor=0.5))
        meshes.append(m)
    return meshes


def rover_frame(v, lift):
    """CAD (x, y, z) mm -> rover frame (X fwd, Y left, Z up) mm."""
    return np.column_stack([-v[:, 1], v[:, 0], v[:, 2] + lift])


def to_gltf(r):
    """rover frame mm -> glTF metres."""
    return np.column_stack([r[:, 0], r[:, 2], -r[:, 1]]) * 1e-3


def main():
    bodies = C.body()
    sw = [(sx, sy, C.strut_and_wheel(sx, sy)) for sx in (1, -1) for sy in (1, -1)]
    lowest = min(-C.WHEEL_D / 2 + C.NUB_Z - C.STRUT_L * math.sin(math.radians(C.STANCE)), 0)
    lift = -lowest
    scene = trimesh.Scene()

    jdesc = {"units": "metres; glTF axes (Y up, +X forward, -Z is rover left)", "source": "hardware/reference/export_cg_glb.py from cg_nanorover.py (docs/cg-model-spec.md)", "bodies": {}}
    scene.graph.update(frame_to="chassis", frame_from="world", matrix=np.eye(4))
    for i, m in enumerate(mesh_of(bodies, lambda v: to_gltf(rover_frame(v, lift)))):
        scene.add_geometry(m, node_name=f"chassis_mesh{i}", geom_name=f"chassis_mesh{i}", parent_node_name="chassis")
    jdesc["bodies"]["chassis"] = {"parent": None, "origin_m": [0, 0, 0]}
    for sx, sy, parts in sw:
        side = "L" if sx > 0 else "R"; fa = "F" if sy < 0 else "A"        # +x_cad is rover left; -y_cad is forward
        sname, wname = f"strut_{side}{fa}", f"wheel_{side}{fa}"
        strut = [p for p in parts if p.label.startswith("strut")]; wheel = [p for p in parts if not p.label.startswith("strut")]
        piv = np.array([sx * (C.L / 2 + C.NUB_L / 2), 0.0, C.NUB_Z])
        a = math.radians(C.STANCE); axle = np.array([piv[0], sy * C.STRUT_L * math.cos(a), piv[2] - C.STRUT_L * math.sin(a)])
        pg = to_gltf(rover_frame(piv[None, :], lift))[0]; ag = to_gltf(rover_frame(axle[None, :], lift))[0]
        T = np.eye(4); T[:3, 3] = pg; scene.graph.update(frame_to=sname, frame_from="chassis", matrix=T)
        T = np.eye(4); T[:3, 3] = ag - pg; scene.graph.update(frame_to=wname, frame_from=sname, matrix=T)
        for i, m in enumerate(mesh_of(strut, lambda v, o=piv: to_gltf(rover_frame(v - o, 0.0)))):
            scene.add_geometry(m, node_name=f"{sname}_mesh{i}", geom_name=f"{sname}_mesh{i}", parent_node_name=sname)
        for i, m in enumerate(mesh_of(wheel, lambda v, o=axle: to_gltf(rover_frame(v - o, 0.0)))):
            scene.add_geometry(m, node_name=f"{wname}_mesh{i}", geom_name=f"{wname}_mesh{i}", parent_node_name=wname)
        jdesc["bodies"][sname] = {"parent": "chassis", "origin_m": pg.tolist(), "axis": [0, 0, 1], "pose_deg_stance": C.STANCE, "strut_length_m": C.STRUT_L * 1e-3}
        jdesc["bodies"][wname] = {"parent": sname, "origin_m": (ag - pg).tolist(), "axis": [0, 0, 1], "radius_m": C.WHEEL_D / 2e3, "width_m": C.WHEEL_W * 1e-3}
    OUT.mkdir(parents=True, exist_ok=True)
    scene.export(OUT / "rover_cg.glb")
    jdesc["window_m"] = to_gltf(rover_frame(np.array([[C.WIN_X, -C.W / 2, C.H - C.WIN_Z]]), lift))[0].tolist()
    (OUT / "rover_cg.json").write_text(json.dumps(jdesc, indent=1))
    b = scene.bounds
    print(f"wrote {OUT / 'rover_cg.glb'} ({(OUT / 'rover_cg.glb').stat().st_size / 1024:.0f} kB); bounds (m) {np.round(b[0], 4).tolist()} to {np.round(b[1], 4).tolist()}; lift {lift:.1f} mm")
    chk = trimesh.load(OUT / "rover_cg.glb"); print("reloaded nodes:", sorted(chk.graph.nodes_geometry)[:3], "... total", len(chk.graph.nodes_geometry))


if __name__ == "__main__":
    main()
