"""
00_config — shared constants, coordinate transforms and Blender helpers for Mirleft Bay.

World frame: metres, Z up, +Y = true north, +X = east, origin = site centroid.
Every other script imports this module through 20_pipeline.py (``C`` in their namespace).
"""
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER_DIR = os.path.join(ROOT, "blender")
DATA_DIR = os.path.join(BLENDER_DIR, "data")
OUT_DIR = os.path.join(ROOT, "output")
CHECKPOINTS = os.path.join(OUT_DIR, "checkpoints")
VALIDATION = os.path.join(OUT_DIR, "validation")
PREVIEWS = os.path.join(OUT_DIR, "previews")
TEX_DIR = os.path.join(ROOT, "assets", "textures", "generated")
for _d in (CHECKPOINTS, VALIDATION, PREVIEWS, TEX_DIR):
    os.makedirs(_d, exist_ok=True)

sys.path.insert(0, DATA_DIR)
import digitized_site as D  # noqa: E402

# Site location (CONFIRMED from the client's Google Earth view, centroid INFERRED +/- 100 m)
LATITUDE = 29.553
LONGITUDE = -10.060
UTC_OFFSET = 1          # Morocco, UTC+1

_REG = json.load(open(os.path.join(DATA_DIR, "registration.json")))
_BND = json.load(open(os.path.join(DATA_DIR, "site_boundary_px.json")))
BEARING = _REG["bearing_deg"]
PLAN_CENTROID = np.array(_REG["plan_centroid_px"])
_ang = math.radians(90.0 - BEARING)                 # rotation from plan-local to world
_C, _S = math.cos(_ang), math.sin(_ang)

# Building heights (ASSUMED A1-A4 in the Project Bible unless noted)
FLOOR_H = 3.10          # floor to floor
GROUND_LIFT = 0.30      # finished floor above the platform
PARAPET_H = 1.10
SLAB_T = 0.25
WALL_T = 0.30


def plan_to_local(px):
    """Plan raster px -> metres in plan orientation (u = towards the road, v = plan up)."""
    p = np.asarray(px, float).reshape(-1, 2)
    u = (p[:, 0] - PLAN_CENTROID[0]) * D.M_PER_PX
    v = -(p[:, 1] - PLAN_CENTROID[1]) * D.M_PER_PX
    return np.stack([u, v], 1)


def local_to_world(uv):
    uv = np.asarray(uv, float).reshape(-1, 2)
    return np.stack([uv[:, 0] * _C - uv[:, 1] * _S + _REG["tx"],
                     uv[:, 0] * _S + uv[:, 1] * _C + _REG["ty"]], 1)


def plan_to_world(px):
    return local_to_world(plan_to_local(px))


def ge_to_world(px):
    p = np.asarray(px, float).reshape(-1, 2)
    return np.stack([(p[:, 0] - D.GE_SITE_CENTROID_PX[0]) * D.GE_M_PER_PX,
                     -(p[:, 1] - D.GE_SITE_CENTROID_PX[1]) * D.GE_M_PER_PX], 1)


def yaw():
    """Rotation (radians, about Z) that turns plan-local axes into world axes."""
    return _ang


def site_polygon_world():
    return plan_to_world(_BND["polygon_px"])


def plan_box_world(box):
    """(x0, x1, y0, y1) in plan px -> centre (world xy), size (along u, along v) in m."""
    x0, x1, y0, y1 = box
    c = plan_to_world([((x0 + x1) / 2, (y0 + y1) / 2)])[0]
    return c, (abs(x1 - x0) * D.M_PER_PX, abs(y1 - y0) * D.M_PER_PX)


# ---------------------------------------------------------------------------
# Blender helpers (imported lazily so the data side can run without bpy)
# ---------------------------------------------------------------------------
COLLECTIONS = ["00_REFERENCE", "01_SITE", "02_TERRAIN", "03_ARCHITECTURE", "04_OPENINGS",
               "05_DETAILS", "06_MATERIALS", "07_LANDSCAPE", "08_FURNITURE", "09_PROPS",
               "10_PEOPLE", "11_VEHICLES", "12_LIGHTING", "13_CAMERAS", "14_RENDER",
               "15_HIGGSFIELD", "16_VALIDATION"]


def collection(name):
    import bpy
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def child_collection(parent, name):
    import bpy
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        collection(parent).children.link(col)
    return col


def remove_object(name):
    import bpy
    ob = bpy.data.objects.get(name)
    if ob is not None:
        me = ob.data if ob.type == "MESH" else None
        bpy.data.objects.remove(ob, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)


def mesh_object(name, verts, faces, col, mat=None, uvs=None, smooth=False):
    """Create (or replace, deterministic by name) a mesh object."""
    import bpy
    remove_object(name)
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, v)) for v in verts], [], [tuple(f) for f in faces])
    if uvs is not None:
        layer = me.uv_layers.new(name="UVMap")
        for p in me.polygons:
            for li in p.loop_indices:
                layer.data[li].uv = uvs[me.loops[li].vertex_index]
    if mat is not None:
        me.materials.append(mat)
    me.validate()
    me.update()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    (col if not isinstance(col, str) else collection(col)).objects.link(ob)
    return ob


class MeshBuilder:
    """Accumulates boxes / polygons per material, then builds one object per material."""

    def __init__(self):
        self.parts = {}

    def _p(self, mat):
        return self.parts.setdefault(mat, ([], [], []))

    def poly(self, mat, pts, uvs=None):
        V, F, U = self._p(mat)
        i = len(V)
        V.extend(pts)
        F.append(tuple(range(i, i + len(pts))))
        U.extend(uvs if uvs is not None else [(p[0], p[2] if abs(p[2]) > 0 else p[1]) for p in pts])

    def box(self, mat, x0, x1, y0, y1, z0, z1):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        z0, z1 = sorted((z0, z1))
        if min(x1 - x0, y1 - y0, z1 - z0) < 1e-4:
            return
        P = self.poly
        P(mat, [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], [(x0, z0), (x1, z0), (x1, z1), (x0, z1)])
        P(mat, [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], [(-x1, z0), (-x0, z0), (-x0, z1), (-x1, z1)])
        P(mat, [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], [(-y1, z0), (-y0, z0), (-y0, z1), (-y1, z1)])
        P(mat, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], [(y0, z0), (y1, z0), (y1, z1), (y0, z1)])
        P(mat, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        P(mat, [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], [(x0, y1), (x1, y1), (x1, y0), (x0, y0)])

    def build(self, prefix, col, materials, location=(0, 0, 0), rotation_z=0.0, parent=None):
        obs = []
        for mat, (V, F, U) in sorted(self.parts.items()):
            ob = mesh_object(f"{prefix}_{mat}", V, F, col, materials.get(mat), U)
            ob.location = location
            ob.rotation_euler = (0, 0, rotation_z)
            if parent is not None:
                ob.parent = parent
                ob.location = (0, 0, 0)
                ob.rotation_euler = (0, 0, 0)
            obs.append(ob)
        return obs
