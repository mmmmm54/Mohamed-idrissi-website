"""
24_export_ae_baked — the residence for After Effects with its light and shadows baked in (client 27-10: "give me
version with lighting and shadows ... the final rendered scene should be perfect, not basic 3D"; After Effects
renders a GLB with its own lights only, and the full GLB froze it).

From Mirleft_Tranche_1.blend (no terrain or ocean round the site): the parts of 22_export_ae_parts (each part one
mesh, decimated, no furniture or interiors), each unwrapped on a lightmap and baked in Cycles with the scene's sun
and sky: the diffuse light, direct and bounced, with the shadows of the buildings, walls and every palm and tree
(the detailed ones), times the materials' colours, tone-mapped as the renders, into one JPEG per part (2k or 4k)
on a plain material. Water and glass keep a plain colour. The plants are light low-poly versions of the library
(shared meshes, no alpha), so the file stays light for After Effects.
In After Effects: Advanced 3D renderer, ONE Environment light, white, intensity 100 %, no sun (the light is in the
textures already).   python 24_export_ae_baked.py [--test]   writes Mirleft_AE_BAKED.glb
"""
import importlib.util
import math
import os
import sys
import time

import bpy  # noqa: I001  (bpy before bmesh)
import bmesh
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("ae22", os.path.join(HERE, "22_export_ae_parts.py"))
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
G = A.G
TEST = "--test" in sys.argv
SIZE = {"T1_GROUND": 4096, "T2_GROUND_STAIR": 4096, "T4_POOL_PARK": 4096, "T1_VILLAS_DUPLEX": 4096, "T2_VILLAS_B": 4096,
        "T3_HOTEL": 4096, "T2_SERVICES": 1024}
CLEAR = ("Water", "Glass", "Pool_Mosaic", "Ocean")            # kept in a plain colour, not baked
EXPOSURE = -0.7                                               # as the renders (05: AgX, exposure -0.7)


def tone(a):
    """linear radiance -> display: the renders' exposure, a filmic curve (ACES fit), sRGB"""
    x = np.clip(a * 2.0 ** EXPOSURE, 0, None)
    y = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    y = np.clip(y, 0, 1)
    return np.where(y > 0.0031308, 1.055 * y ** (1 / 2.4) - 0.055, y * 12.92)


def split_clear(ob):
    """water and glass faces into an object of their own, in a plain colour"""
    me = ob.data
    idx = {i for i, m in enumerate(me.materials) if m is not None and any(k in m.name for k in CLEAR)}
    if not idx:
        return None
    w = ob.copy()
    w.data = me.copy()
    for c in ob.users_collection:
        c.objects.link(w)
    for o_, keep in ((ob, False), (w, True)):
        bm = bmesh.new()
        bm.from_mesh(o_.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if (f.material_index in idx) != keep], context="FACES")
        bm.to_mesh(o_.data)
        bm.free()
    w.name = w.data.name = ob.name + "_WATER_GLASS"
    for i, m in enumerate(list(w.data.materials)):
        if m is not None:
            w.data.materials[i] = A.plain(m)
    return w


def unwrap(ob):
    me = ob.data
    lm = me.uv_layers.new(name="LM")
    me.uv_layers.active = lm
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.002, area_weight=1.0)
    bpy.ops.object.mode_set(mode="OBJECT")
    if len(me.uv_layers) > 1:                                 # the materials' own UVs render, the lightmap is baked to
        me.uv_layers[0].active_render = True


def bake(ob, size):
    img = bpy.data.images.new(ob.name + "_LM", size, size, float_buffer=True)
    for m in ob.data.materials:
        if m is None or not m.use_nodes:
            continue
        nt = m.node_tree
        t = nt.nodes.get("BAKE_TARGET") or nt.nodes.new("ShaderNodeTexImage")
        t.name = "BAKE_TARGET"
        t.image = img
        uv = nt.nodes.get("BAKE_UV") or nt.nodes.new("ShaderNodeUVMap")
        uv.name = "BAKE_UV"
        uv.uv_map = "LM"
        if not t.inputs["Vector"].is_linked:
            nt.links.new(uv.outputs["UV"], t.inputs["Vector"])
        for n in nt.nodes:
            n.select = False
        t.select = True
        nt.nodes.active = t
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT", "COLOR"}, margin=6, use_clear=True)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4)[::-1, :, :3]
    im = Image.fromarray((tone(a) * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))
    p = os.path.join(G.TMP, ob.name + "_LM.jpg")
    im.save(p, quality=90)
    bpy.data.images.remove(img)
    return p


def baked_material(ob, path):
    m = bpy.data.materials.new(ob.name + "_BAKED")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.15
    me = ob.data
    me.materials.clear()
    me.materials.append(m)
    me.polygons.foreach_set("material_index", [0] * len(me.polygons))
    lm = me.uv_layers["LM"]
    lm.active_render = True
    for u in [u for u in me.uv_layers if u.name != "LM"]:
        me.uv_layers.remove(u)


# ---- the plants, light: low-poly, opaque, shared meshes ----------------------------------------------------------
def _col(name, hexcol, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*G.lin(hexcol), 1.0)
    b.inputs["Roughness"].default_value = rough
    return m


def lod_meshes():
    mats = {"trunk": _col("AE_LOD_Palm_Trunk", "#7A644C"), "frond": _col("AE_LOD_Date_Frond", "#66784A", 0.7),
            "fan": _col("AE_LOD_Fan", "#5C7C38", 0.7), "skirt": _col("AE_LOD_Skirt", "#8C7452"),
            "olive": _col("AE_LOD_Olive_Crown", "#77805C"), "bark": _col("AE_LOD_Olive_Bark", "#7F786A"),
            "grass": _col("AE_LOD_Grass", "#A49F68"), "agave": _col("AE_LOD_Agave", "#7E9A8E", 0.6),
            "lav": _col("AE_LOD_Lavender", "#7B8A6C"), "lavf": _col("AE_LOD_Lavender_Flower", "#7462A6"),
            "jar": _col("AE_LOD_Terracotta", "#A65A3A"), "shrub": _col("AE_LOD_Shrub", "#5E7040"),
            "pink": _col("AE_LOD_Bougainvillea", "#C4648A")}

    def mesh(name, parts):
        V, F, Mi, ml = [], [], [], []
        for mat, polys in parts.items():
            if mats[mat] not in ml:
                ml.append(mats[mat])
            k = ml.index(mats[mat])
            for poly in polys:
                i = len(V)
                V.extend(poly)
                F.append(tuple(range(i, i + len(poly))))
                Mi.append(k)
        me = bpy.data.meshes.new(name)
        me.from_pydata(V, [], F)
        for m in ml:
            me.materials.append(m)
        me.polygons.foreach_set("material_index", Mi)
        me.update()
        return me

    def tube(p0, p1, r0, r1, n=6):
        out = []
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            out.append([(p0[0] + r0 * math.cos(a0), p0[1] + r0 * math.sin(a0), p0[2]), (p0[0] + r0 * math.cos(a1), p0[1] + r0 * math.sin(a1), p0[2]),
                        (p1[0] + r1 * math.cos(a1), p1[1] + r1 * math.sin(a1), p1[2]), (p1[0] + r1 * math.cos(a0), p1[1] + r1 * math.sin(a0), p1[2])])
        return out

    def blob(c, r, sz=0.75, jit=0.12, seed=1):
        rng = np.random.default_rng(seed)
        t = (1 + 5 ** 0.5) / 2
        V = [np.array(v, float) / np.linalg.norm(v) for v in ((-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t),
                                                             (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1))]
        Fc = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
              (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
        J = [r * (1 + rng.uniform(-jit, jit)) for _ in V]
        P = [(c[0] + v[0] * j, c[1] + v[1] * j, c[2] + v[2] * j * sz) for v, j in zip(V, J)]
        return [[P[a], P[b], P[c_]] for a, b, c_ in Fc]

    out = {}
    # date palm: trunk, crown bulb, 18 feathered fronds folded in a V
    fr = []
    for i in range(18):
        age = i / 17
        az = i * 2.39996
        el = math.radians(75 - 100 * age ** 0.8)
        droop = math.radians(25 + 60 * age)
        hd = np.array([math.cos(az), math.sin(az), 0.0])
        sd = np.array([-math.sin(az), math.cos(az), 0.0])
        p = np.array([0, 0, 5.35]) + hd * 0.2
        pts = [p]
        for k in range(5):
            e = el - droop * ((k + 0.5) / 5) ** 1.2
            pts.append(pts[-1] + (hd * math.cos(e) + np.array([0, 0, math.sin(e)])) * 3.3 / 5)
        for k in range(5):
            w0, w1 = 0.55 * math.sin(math.pi * (0.15 + 0.85 * k / 5)), 0.55 * math.sin(math.pi * (0.15 + 0.85 * (k + 1) / 5))
            a, b = pts[k], pts[k + 1]
            up = np.array([0, 0, 0.22])
            for sg in (-1, 1):
                fr.append([tuple(a), tuple(b), tuple(b + sd * sg * w1 + up * w1), tuple(a + sd * sg * w0 + up * w0)])
    out["date"] = mesh("AE_LOD_DATE_PALM", {"trunk": tube((0, 0, 0), (0, 0, 5.0), 0.34, 0.27, 8) + tube((0, 0, 5.0), (0, 0, 5.7), 0.38, 0.05, 8),
                                            "frond": fr})
    # Washingtonia: slender trunk, skirt, 16 fans
    fans = []
    for i in range(16):
        az = i * 2.39996
        el = math.radians(55 - 70 * i / 15)
        hd = np.array([math.cos(az), math.sin(az), 0.0])
        sd = np.array([-math.sin(az), math.cos(az), 0.0])
        h = np.array([0, 0, 9.3]) + (hd * math.cos(el) + np.array([0, 0, math.sin(el)])) * 1.1
        n = np.cross(sd, hd * math.cos(el) + np.array([0, 0, math.sin(el)]))
        f_ = hd * math.cos(el) + np.array([0, 0, math.sin(el)])
        rim = [h + (f_ * math.cos(t) + sd * math.sin(t)) * 1.0 - np.array([0, 0, 0.35 * abs(math.cos(t)) + 0.15]) + n * 0.08 * (k % 2)
               for k, t in enumerate(np.linspace(-1.9, 1.9, 9))]
        for k in range(8):
            fans.append([tuple(h), tuple(rim[k]), tuple(rim[k + 1])])
        fans.append([tuple(np.array([0, 0, 9.2])), tuple(h + sd * 0.03), tuple(h - sd * 0.03)])
    out["wash"] = mesh("AE_LOD_WASHINGTONIA", {"trunk": tube((0, 0, 0), (0, 0, 9.3), 0.42, 0.24, 8), "skirt": tube((0, 0, 7.4), (0, 0, 9.3), 0.30, 0.55, 10),
                                               "fan": fans})
    # olive: trunk, three limbs, a crown of lumps
    limbs = tube((0, 0, 0), (0, 0, 1.2), 0.22, 0.17, 6)
    crown = []
    for k, (dx, dy, dz, r) in enumerate(((0, 0, 2.6, 1.3), (1.0, 0.4, 2.3, 1.0), (-0.9, 0.6, 2.4, 1.0), (0.2, -1.0, 2.2, 0.95), (0.1, 0.2, 3.2, 0.9))):
        limbs += tube((0, 0, 1.1), (dx * 0.7, dy * 0.7, dz - 0.4), 0.12, 0.07, 5)
        crown += blob((dx, dy, dz), r, 0.7, 0.15, k)
    out["olive"] = mesh("AE_LOD_OLIVE", {"bark": limbs, "olive": crown})
    out["grass"] = mesh("AE_LOD_GRASS", {"grass": [[(0.04 * math.cos(a + 1.5), 0.04 * math.sin(a + 1.5), 0), (0.04 * math.cos(a - 1.5), 0.04 * math.sin(a - 1.5), 0),
                                                     (0.45 * math.cos(a), 0.45 * math.sin(a), 0.75)] for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]})
    ag = []
    for i in range(14):
        a = i * 2.39996
        f = i / 13
        e = math.radians(15 + 60 * f)
        L_ = 0.7 * (1 - 0.4 * f)
        d = np.array([math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)])
        s = np.array([-math.sin(a), math.cos(a), 0.0]) * 0.08
        ag.append([(0, 0, 0.05), tuple(d * L_ * 0.35 + s + np.array([0, 0, 0.05])), tuple(d * L_ + np.array([0, 0, 0.05])), tuple(d * L_ * 0.35 - s + np.array([0, 0, 0.05]))])
    out["agave"] = mesh("AE_LOD_AGAVE", {"agave": ag})
    out["lav"] = mesh("AE_LOD_LAVENDER", {"lav": blob((0, 0, 0.18), 0.38, 0.6, 0.1, 3), "lavf": blob((0, 0, 0.42), 0.30, 0.25, 0.25, 4)})
    prof = [(0.0, 0.16), (0.2, 0.31), (0.45, 0.38), (0.7, 0.34), (0.88, 0.18), (1.0, 0.19)]
    jar = []
    for j in range(len(prof) - 1):
        (z0, r0), (z1, r1) = prof[j], prof[j + 1]
        jar += tube((0, 0, z0 * 0.85), (0, 0, z1 * 0.85), r0 * 0.85, r1 * 0.85, 10)
    out["jar"] = mesh("AE_LOD_JAR", {"jar": jar})
    out["shrub"] = mesh("AE_LOD_SHRUB", {"shrub": blob((0, 0, 0.35), 0.48, 0.7, 0.18, 5)})
    out["pink"] = mesh("AE_LOD_BOUGAINVILLEA", {"pink": blob((0, 0, 0.4), 0.5, 0.8, 0.2, 6)})
    return out


LOD_OF = (("DATE_PALM", "date"), ("WASHINGTONIA", "wash"), ("OLIVE_TREE", "olive"), ("GREEN_SHADE", "olive"), ("STREET_TREE", "olive"),
          ("CLIPPED_STANDARD", "olive"), ("FOUNTAIN_GRASS", "grass"), ("ORNAMENTAL_GRASS", "grass"), ("AGAVE", "agave"),
          ("LAVENDER", "lav"), ("JAR_", "jar"), ("SHRUB_FLOWERING", "pink"), ("SHRUB", "shrub"))


def main():
    t0 = time.time()
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "Mirleft_Tranche_1.blend"))
    vl = bpy.context.view_layer
    sur = bpy.data.collections.get("00_SURROUNDINGS")
    for o in list(sur.all_objects) if sur else []:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in list(bpy.data.objects):
        if o.type == "CAMERA" or (o.type == "MESH" and (o.name.startswith(A.DROP_OBS) or o.hide_render) and "VEG" not in o.name):
            bpy.data.objects.remove(o, do_unlink=True)
    vl.update()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 6 if TEST else 14
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 3
    sc.render.bake.margin = 6
    parts = {}
    for part, (_, _, budget) in A.PARTS.items():
        if part == "SURROUNDINGS":
            continue
        obs = [o for o in bpy.data.objects if o.name in vl.objects and o.type == "MESH" and A.part_of(o) == part
               and not o.data.name.startswith("SRC_")]                # the plants stay apart (shadows, then their light versions)
        if not obs:
            continue
        ob = A.join("MIRLEFT_" + part, obs)
        me = ob.data
        drop = {i for i, m in enumerate(me.materials) if m is not None and any(k in m.name for k in A.DROP_MATS)}
        if drop:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in drop], context="FACES")
            bm.to_mesh(me)
            bm.free()
        A.simplify(ob, budget)
        parts[part] = ob
        print(f"PART {part:26s} {len(ob.data.polygons):7d} faces", flush=True)
    clear = {}
    for part, ob in parts.items():
        w = split_clear(ob)
        if w is not None:
            clear[part] = w
        unwrap(ob)
    print(f"UNWRAPPED {time.time() - t0:.0f} s", flush=True)
    todo = list(parts.items())
    if TEST:
        todo = [(k, v) for k, v in todo if k in ("T2_SPA",)]
    for part, ob in todo:
        size = 512 if TEST else SIZE.get(part, 2048)
        t1 = time.time()
        p = bake(ob, size)
        baked_material(ob, p)
        print(f"BAKED {part:26s} {size} px  {time.time() - t1:.0f} s", flush=True)
    # the plants on their light versions
    lods = lod_meshes()
    n = 0
    for o in list(bpy.data.objects):
        if o.type != "MESH" or o.name.startswith("SRC_") or o.name not in vl.objects:
            continue
        dn = o.data.name.upper()
        if not dn.startswith("SRC_"):
            continue
        k = next((v for key, v in LOD_OF if key in dn), None)
        if k is not None:
            o.data = lods[k]
            n += 1
    print(f"PLANTS {n} on their light versions", flush=True)
    for o in list(bpy.data.objects):
        if o.type == "LIGHT":
            bpy.data.objects.remove(o, do_unlink=True)
    out = os.path.join(ROOT, "Mirleft_AE_BAKED_TEST.glb" if TEST else "Mirleft_AE_BAKED.glb")
    bpy.ops.object.select_all(action="DESELECT")
    keep = list(parts.values()) + list(clear.values()) + [o for o in vl.objects if o.type == "MESH" and o.data.name.startswith("AE_LOD_")]
    for o in keep:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
                              export_cameras=False, export_lights=False, export_materials="EXPORT", export_image_format="JPEG",
                              export_draco_mesh_compression_enable=False)
    print(f"GLB {os.path.basename(out)} {os.path.getsize(out) / 2 ** 20:.1f} MiB, {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
