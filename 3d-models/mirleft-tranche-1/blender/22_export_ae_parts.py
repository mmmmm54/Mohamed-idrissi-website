"""
22_export_ae_parts — light GLBs for After Effects, one per part of the project (client 26-10: "bghina version
mafihach bzaf dyal detail, ghir ta9ssim: villa A, SPA ...": the full GLB freezes After Effects).

From Mirleft_Tranche_1.blend: no plants (simple palm and tree volumes in a file of their own instead), no
furniture, curtains or interiors; every instance made real and each part joined into ONE mesh, welded, its flat
faces merged and decimated where it stays heavy; plain colours (the mean colour of each texture), the satellite
image of the surroundings at 1024 px. Every file has the same origin (the centre of Tranche 1, its ground at 0),
metres, Y up, so the parts fall into place when they are layered in After Effects.
Writes Mirleft_AE_PARTS.zip: Mirleft_AE_<PART>.glb (0.3 to 4 MB each) and Mirleft_AE_ALL_LIGHT.glb (every part
in one file, 27 MB).
    python 22_export_ae_parts.py
--zoning (client 26-10: "file wa7ed fih residence kamla, ghir ta9ssim, b colors"): the whole residence in ONE file,
lighter still, each zone in one flat colour (villas duplex, restaurant and commerces, villas type B, type C, SPA,
services, villas type A, hotel), the ground in three (paving and walls, green, water), no surroundings, no plants;
writes Mirleft_AE_ZONING.glb and its legend Mirleft_AE_ZONING_LEGEND.png.
    python 22_export_ae_parts.py --zoning
"""
import importlib.util
import math
import os
import random
import sys
import zipfile

import bpy  # noqa: I001  (bpy before bmesh)
import bmesh
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("glb08", os.path.join(HERE, "08_export_glb.py"))
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
OUT = os.path.join(G.TMP, "Mirleft_AE_PARTS")         # the GLBs are only shipped in the zip

# part -> (collections, object-name prefix or None, triangle budget)
PARTS = {
    "T1_VILLAS_DUPLEX": (("03_DUPLEX",), None, 45000),
    "T1_RESTAURANT_COMMERCES": (("04_PUBLIC",), None, 20000),
    "T1_POOL_COURT": (("05_POOL",), None, 12000),
    "T1_GROUND": (("01_TERRAIN", "02_GROUND", "06_LANDSCAPE"), None, 40000),
    "T1_PLAYGROUND": (("08_PLAYGROUND",), None, 20000),
    "T2_VILLAS_B": (("T2_02_VILLAS",), "T2_VILLA_B", 60000),
    "T2_VILLAS_C": (("T2_02_VILLAS",), "T2_VILLA_C", 30000),
    "T2_SPA": (("T2_05_SPA",), None, 12000),
    "T2_SERVICES": (("T2_01_GROUND",), "T2_BUILDINGS_CENTRE", 6000),
    "T2_GROUND_STAIR": (("T2_01_GROUND", "T2_03_LANDSCAPE"), None, 50000),
    "T3_VILLAS_A": (("T3_02_VILLAS",), None, 20000),
    "T3_HOTEL": (("T3_05_HOTEL",), None, 45000),
    "T3_GROUND": (("T3_01_GROUND", "T3_03_LANDSCAPE"), None, 15000),
    "T4_POOL_PARK": (("T4_01_GROUND", "T4_02_POOLS", "T4_03_LANDSCAPE"), None, 25000),
    "SURROUNDINGS": (("00_SURROUNDINGS",), None, 40000),
}
ZONING = "--zoning" in sys.argv
ZONES = {   # the zoning file: part -> (flat colour, legend)
    "T1_VILLAS_DUPLEX": ("#E4602A", "Villas duplex (Tranche 1)"),
    "T1_RESTAURANT_COMMERCES": ("#D7263D", "Restaurant, commerces, petanque (Tranche 1)"),
    "T2_VILLAS_B": ("#F6D63C", "Villas type B"),
    "T2_VILLAS_C": ("#8E5CC9", "Villas type C"),
    "T2_SPA": ("#E85A9C", "SPA"),
    "T2_SERVICES": ("#7D7D7D", "Services (centre d'entretien, office)"),
    "T3_VILLAS_A": ("#2D7DD2", "Villas type A"),
    "T3_HOTEL": ("#1B998B", "Hotel"),
    "T1_PLAYGROUND": ("#12B5CB", "Aire de jeux"),
}
ZBUDGET = {"T1_VILLAS_DUPLEX": 32000, "T1_RESTAURANT_COMMERCES": 14000, "T1_POOL_COURT": 6000, "T1_GROUND": 16000,
           "T2_GROUND_STAIR": 22000, "T3_VILLAS_A": 15000, "T3_HOTEL": 32000, "T4_POOL_PARK": 12000}   # the zoning file
GROUND_ZONES = (("#9FCB7B", "Espaces verts", ("Lawn", "lawn", "Verge", "Turf", "Gravel", "Planter_Soil")),
                ("#6EC6F0", "Eau, piscines", ("Water", "Pool_Mosaic", "Pool_Tile", "Jade")),
                ("#E6E1D8", "Voiries, parvis, murs, jardins", ()))
DROP_MATS = ("Parasol_Canvas", "Lounger", "Cushion", "Sofa", "Curtain", "Interior", "Lamp_Warm", "Mashrabiya")
DROP_OBS = ("LOUNGER_", "CABANA_")
HEX = {   # plain colours of the procedural materials (the others: the mean colour of their texture, or 08's FLAT)
    "M01_Render_Sand": "#C8AA86", "D13_Render_Villa_Beige": "#C8AA86", "D04_Render_Trim": "#E2CBA6",
    "D18_Stone_Cladding_Beige": "#BBA88E", "M06_Glass": "#5E6F75", "T03_Lawn": "#6E8A3E", "M10_Pool_Water": "#4FA9CC",
    "H04_Ocean_Atlantic": "#1E5A6C", "T01_Terrain_Soil_Sand_Rock": "#C9A27E", "T16_Site_Land_Soil": "#C7AE98",
}


def mean_hex(path):
    a = np.asarray(Image.open(path).convert("RGB").resize((64, 64))).reshape(-1, 3).mean(0)
    return "#%02X%02X%02X" % tuple(int(v) for v in a)


def colour(m):
    """the plain colour (hex) standing for material m"""
    name = m.name
    if name.startswith("T2_") and name not in G.TEX and name not in G.FLAT:
        base = max((k for k in list(G.TEX) + list(G.FLAT) + list(HEX) if name[3:].startswith(k)), key=len, default=None)
        name = base or name
    if name in HEX:
        return HEX[name]
    if name in G.TEX:
        return mean_hex(G.TEX[name][0])
    if name in G.FLAT:
        return G.FLAT[name][0]
    img = next((n.image for n in (m.node_tree.nodes if m.node_tree else []) if n.type == "TEX_IMAGE" and n.image), None)
    if img is not None and img.filepath:
        try:
            return mean_hex(bpy.path.abspath(img.filepath))
        except Exception:
            pass
    c = m.diffuse_color
    to_s = lambda v: 1.055 * v ** (1 / 2.4) - 0.055 if v > 0.0031308 else v * 12.92
    return "#%02X%02X%02X" % tuple(int(255 * min(1.0, to_s(v))) for v in c[:3])


_MATS = {}


def plain(m):
    """one plain material per source material; the satellite terrain keeps its image at 1024 px"""
    if m.name in _MATS:
        return _MATS[m.name]
    if m.name.startswith("GEO_"):
        img = next((n.image for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
        if img is not None:
            nm = bpy.data.materials.new(m.name + "_AE")
            nm.use_nodes = True
            b = nm.node_tree.nodes["Principled BSDF"]
            im = Image.open(bpy.path.abspath(img.filepath)).convert("RGB")
            im.thumbnail((1024, 1024))
            p = os.path.join(G.TMP, m.name + "_1k.jpg")
            im.save(p, quality=85)
            t = nm.node_tree.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(p)
            nm.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
            b.inputs["Roughness"].default_value = 0.95
            _MATS[m.name] = nm
            return nm
    nm = bpy.data.materials.new(m.name + "_AE")
    nm.use_nodes = True
    b = nm.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*G.lin(colour(m)), 1.0)
    b.inputs["Roughness"].default_value = 0.15 if "Glass" in m.name or "Water" in m.name or "Ocean" in m.name else 0.85
    _MATS[m.name] = nm
    return nm


def part_of(o):
    c = o.users_collection[0].name if o.users_collection else ""
    for part, (cols, prefix, _) in PARTS.items():
        if c in cols and (prefix is None or o.name.startswith(prefix)):
            return part
    return None


def simplify(ob, budget):
    """weld, merge the flat faces, decimate down to the budget; flat shading"""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts, edges=bm.edges, delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    if n > budget:
        mod = ob.modifiers.new("dec", "DECIMATE")
        mod.ratio = budget / n
        mod.use_collapse_triangulate = True
        dg = bpy.context.evaluated_depsgraph_get()
        new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.remove(mod)
        old, ob.data = ob.data, new
        new.name = old.name
        bpy.data.meshes.remove(old)
    if ZONING:                                       # the flat faces share their vertices (a lighter file), sharp edges
        ob.data.shade_smooth()
        ob.data.set_sharp_from_angle(angle=math.radians(30.0))
    else:
        for p in ob.data.polygons:
            p.use_smooth = False
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def join(name, obs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = ob.data.name = name
    return ob


def proxy_mesh(kind):
    """simple volumes standing for the plants: kind 'date', 'wash' or 'tree' (local, foot at 0)"""
    V, F, Mi = [], [], []

    def add(pts, faces, mi):
        i = len(V)
        V.extend(pts)
        F.extend([tuple(i + k for k in f) for f in faces])
        Mi.extend([mi] * len(faces))

    def cyl(r0, r1, z0, z1, n=6, mi=0):
        pts = [(r0 * math.cos(2 * math.pi * k / n), r0 * math.sin(2 * math.pi * k / n), z0) for k in range(n)]
        pts += [(r1 * math.cos(2 * math.pi * k / n), r1 * math.sin(2 * math.pi * k / n), z1) for k in range(n)]
        add(pts, [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)], mi)

    def blob(c, r, sz, mi):
        t = (1 + 5 ** 0.5) / 2
        ico = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
        fs = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
              (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
        k = r / math.sqrt(1 + t * t)
        add([(c[0] + x * k, c[1] + y * k, c[2] + z * k * sz) for x, y, z in ico], fs, mi)
    if kind == "date":
        cyl(0.32, 0.26, 0.0, 5.0)
        for k in range(10):                                     # ten drooping fronds
            a = 2 * math.pi * k / 10
            d, s = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
            el = 0.6 if k % 2 else 0.15
            p0 = (0, 0, 5.2)
            p1 = (d[0] * 1.5, d[1] * 1.5, 5.2 + 1.2 * el + 0.3)
            p2 = (d[0] * 2.9, d[1] * 2.9, 5.2 + 0.6 * el - 0.9)
            w = 0.35
            add([p0, (p1[0] - s[0] * w, p1[1] - s[1] * w, p1[2]), (p1[0] + s[0] * w, p1[1] + s[1] * w, p1[2]), p2],
                [(0, 1, 2), (1, 3, 2)], 1)
    elif kind == "wash":
        cyl(0.40, 0.22, 0.0, 9.0)
        cyl(0.42, 0.30, 7.6, 9.0, 8, 0)                         # the skirt
        blob((0, 0, 9.5), 1.5, 0.75, 1)
    else:
        cyl(0.16, 0.12, 0.0, 1.6)
        blob((0, 0, 2.6), 1.8, 0.7, 2)
    return V, F, Mi


_ZM = {}


def zmat(hexcol, name):
    if name not in _ZM:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*G.lin(hexcol), 1.0)
        b.inputs["Roughness"].default_value = 0.8
        m.diffuse_color = (*G.lin(hexcol), 1.0)
        _ZM[name] = m
    return _ZM[name]


def zone_paint(me, part):
    """the zoning file's colours: a building zone in its one colour; the ground in green, water or paving"""
    if part in ZONES:
        hexcol, label = ZONES[part]
        me.materials.clear()
        me.materials.append(zmat(hexcol, "ZONE_" + part))
        me.polygons.foreach_set("material_index", [0] * len(me.polygons))
        return
    for i, m in enumerate(list(me.materials)):
        if m is None:
            continue
        hexcol, label, keys = next(z for z in GROUND_ZONES if not z[2] or any(k in m.name for k in z[2]))
        me.materials[i] = zmat(hexcol, "ZONE_" + label.split(",")[0].replace(" ", "_").upper())


def legend(path):
    from PIL import ImageDraw, ImageFont
    rows = [(h, t) for h, t in ZONES.values()] + [(h, t) for h, t, _ in GROUND_ZONES]
    W, H = 900, 70 + 58 * len(rows)
    im = Image.new("RGB", (W, H), (250, 248, 244))
    d = ImageDraw.Draw(im)
    try:
        f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
        f2 = ImageFont.truetype("DejaVuSans.ttf", 26)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((30, 18), "Mirleft - zoning", fill=(40, 40, 40), font=f1)
    for k, (h, t) in enumerate(rows):
        y = 70 + 58 * k
        c = tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        d.rectangle([30, y, 90, y + 40], fill=c, outline=(90, 90, 90))
        d.text((110, y + 5), t, fill=(40, 40, 40), font=f2)
    im.save(path)


def main():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "Mirleft_Tranche_1.blend"))
    vl = bpy.context.view_layer
    for o in list(bpy.data.objects):
        if o.type in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(o, do_unlink=True)
    # the plants: their places kept for the simple volumes, the instances removed
    vl.update()
    plants = []
    for o in [o for o in bpy.data.objects if o.name in vl.objects]:
        cn = o.users_collection[0].name if o.users_collection else ""
        if o.type != "MESH":
            continue
        if cn.endswith("TREES_PALMS"):
            dn = o.data.name.upper()
            kind = "date" if "DATE" in dn else ("wash" if "WASHINGTONIA" in dn else "tree")
            plants.append((kind, o.matrix_world.copy()))
            bpy.data.objects.remove(o, do_unlink=True)
        elif "VEG_" in o.name or o.name.startswith(DROP_OBS) or o.hide_render or cn == "SRC":
            bpy.data.objects.remove(o, do_unlink=True)
    src = bpy.data.collections.get("SRC")
    if src is not None:
        for o in list(src.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    vl.update()
    cx, cy, cz = G.centre()
    os.makedirs(OUT, exist_ok=True)
    built = {}
    for part, (_, _, budget) in PARTS.items():
        obs = [o for o in bpy.data.objects if o.name in vl.objects and o.type == "MESH" and part_of(o) == part]
        if not obs or (ZONING and part == "SURROUNDINGS"):
            continue
        if ZONING:
            budget = ZBUDGET.get(part, budget)
        ob = join("MIRLEFT_" + part, obs)
        me = ob.data
        # furniture and interiors out, plain colours in
        drop = {i for i, m in enumerate(me.materials) if m is not None and any(k in m.name for k in DROP_MATS)}
        if drop:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in drop], context="FACES")
            bm.to_mesh(me)
            bm.free()
        keep_uv = any(m is not None and m.name.startswith("GEO_") for m in me.materials) and not ZONING
        if not ZONING:
            for i, m in enumerate(list(me.materials)):
                if m is not None:
                    me.materials[i] = plain(m)
        if not keep_uv:
            while me.uv_layers:
                me.uv_layers.remove(me.uv_layers[0])
        for a in [a for a in me.attributes if a.name.startswith(("mask", "Col", "color")) and not a.is_internal]:
            try:
                me.attributes.remove(a)
            except Exception:
                pass
        me.transform(__import__("mathutils").Matrix.Translation((-cx, -cy, -cz)))
        n = simplify(ob, budget)
        if ZONING:                                  # coloured after the decimation, which keeps to the materials
            zone_paint(ob.data, part)
        built[part] = ob
        print(f"PART {part:26s} {len(obs):5d} objects -> {n:7d} triangles", flush=True)
    if ZONING:
        bpy.ops.object.select_all(action="DESELECT")
        for o in built.values():
            o.select_set(True)
        p = os.path.join(ROOT, "Mirleft_AE_ZONING.glb")
        bpy.ops.export_scene.gltf(filepath=p, export_format="GLB", use_selection=True, export_yup=True, export_apply=True,
                                  export_cameras=False, export_lights=False, export_materials="EXPORT", export_draco_mesh_compression_enable=False)
        print(f"GLB {os.path.basename(p)} {os.path.getsize(p) / 2 ** 20:.1f} MiB", flush=True)
        legend(os.path.join(ROOT, "Mirleft_AE_ZONING_LEGEND.png"))
        return
    # the plants as simple volumes, one mesh
    from mathutils import Matrix, Vector
    mats = [bpy.data.materials.new(n) for n in ("AE_Trunk", "AE_Palm_Leaves", "AE_Tree_Leaves")]
    for m, h in zip(mats, ("#6E5A44", "#5C7438", "#6F7E55")):
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*G.lin(h), 1.0)
        m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    V, F, Mi = [], [], []
    proto = {k: proxy_mesh(k) for k in ("date", "wash", "tree")}
    off = Matrix.Translation((-cx, -cy, -cz))
    for kind, mw in plants:
        pv, pf, pm = proto[kind]
        i = len(V)
        M_ = off @ mw
        V.extend([tuple(M_ @ Vector(p)) for p in pv])
        F.extend([tuple(i + k for k in f) for f in pf])
        Mi.extend(pm)
    me = bpy.data.meshes.new("MIRLEFT_PLANTS_SIMPLE")
    me.from_pydata(V, [], F)
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", Mi)
    me.update()
    ob = bpy.data.objects.new("MIRLEFT_PLANTS_SIMPLE", me)
    bpy.context.scene.collection.objects.link(ob)
    built["PLANTS_SIMPLE"] = ob
    print(f"PART PLANTS_SIMPLE {len(plants)} palms and trees -> {len(F)} faces", flush=True)
    # one file per part, and all of them in one light file
    files = []
    opts = dict(export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_cameras=False,
                export_lights=False, export_materials="EXPORT", export_image_format="JPEG", export_draco_mesh_compression_enable=False)
    for part, ob in list(built.items()) + [("ALL_LIGHT", None)]:
        bpy.ops.object.select_all(action="DESELECT")
        for o in (built.values() if ob is None else [ob]):
            o.select_set(True)
        p = os.path.join(OUT, f"Mirleft_AE_{part}.glb")
        bpy.ops.export_scene.gltf(filepath=p, **opts)
        files.append(p)
        print(f"GLB {os.path.basename(p):40s} {os.path.getsize(p) / 2 ** 20:6.1f} MiB", flush=True)
    z = os.path.join(ROOT, "Mirleft_AE_PARTS.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, "Mirleft_AE_PARTS/" + os.path.basename(p))
    print("AE_ZIP", round(os.path.getsize(z) / 2 ** 20, 1), "MiB", flush=True)


if __name__ == "__main__":
    main()
