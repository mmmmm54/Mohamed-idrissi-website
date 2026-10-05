"""
19_export_package — D5 Render package (MODE A on request of the client, 2026-10-02; materials
rebuilt for D5 on 2026-10-05 after the client saw white surfaces in D5).

    python 19_export_package.py [--light]

Opens output/checkpoints/checkpoint_09_cameras.blend and writes output/d5/:
  * Mirleft_Bay_D5.fbx        architecture + site + terrain + water + cameras, every building
                              instance made real, material names kept (see D5_MATERIAL_MAPPING.md)
  * Mirleft_Bay_D5.blend      the same scene, for D5's Blender sync plugin if you use it
Everything is kept (buildings, palms, pink trees, olives, scrub, cars, parking, water) so D5 only
needs small fixes. Only the 300k close-up grass tufts are left out (about 4 million triangles; use
D5 grass on the T03_Lawn faces). `--light` drops vegetation and cars for a lighter file. UVs are in metres (1 UV unit = 1 m;
terrain 1 unit = 10 m), so D5 materials tile at true scale.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CK = os.path.join(ROOT, "output", "checkpoints", "checkpoint_09_cameras.blend")
OUT = os.path.join(ROOT, "output", "d5")
os.makedirs(OUT, exist_ok=True)
LIGHT = "--light" in sys.argv          # optional: drop vegetation + cars (old behaviour)

bpy.ops.wm.open_mainfile(filepath=CK)
sc = bpy.context.scene
vl = bpy.context.view_layer

# 1. strip what D5 does better (and the heavy grass)
removed = 0
for o in list(bpy.data.objects):
    n = o.name
    if n.startswith("GRASS_ZONE") or n.startswith("SRC_") or n.startswith("CAM_VAL") \
            or (LIGHT and (n.startswith("VEG_") or n.startswith("VEH_"))):
        bpy.data.objects.remove(o, do_unlink=True)
        removed += 1

# 2. make building instances real (D5 imports plain meshes)
for lc in vl.layer_collection.children["03_ARCHITECTURE"].children:
    lc.exclude = False
bpy.ops.object.select_all(action="DESELECT")
inst = [o for o in bpy.data.objects if o.instance_type == "COLLECTION" and o.instance_collection]
for o in inst:
    o.select_set(True)
vl.objects.active = inst[0] if inst else None
if inst:
    bpy.ops.object.duplicates_make_real(use_base_parent=False, use_hierarchy=False)
for o in inst:
    if o.name in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)
# the source type collections stay hidden: exclude them again so they are not exported twice
for lc in vl.layer_collection.children["03_ARCHITECTURE"].children:
    if lc.name.startswith("TYPE_"):
        lc.exclude = True

# 3. D5-ready materials. D5 reads only a Principled BSDF with an image plugged straight into Base
#    Color (and a normal map / alpha); Blender's Mix / Math / Mapping nodes come in WHITE. So every
#    material is rebuilt as: baked colour image (UV) -> Base Color, baked normal map -> Normal,
#    plain roughness value; untextured ones get their colour as a plain value. Textured faces get
#    box-projected UVs in metres / tile size, the same projection the Blender renders use.
import importlib.util
import math

import numpy as np
from PIL import Image, ImageFilter

TEXDIR = os.path.join(ROOT, "assets", "textures", "tileable")
GENDIR = os.path.join(ROOT, "assets", "textures", "generated")
PH = os.path.join(ROOT, "assets", "textures", "polyhaven")
TEX_OUT = os.path.join(OUT, "textures")
os.makedirs(TEX_OUT, exist_ok=True)
_spec = importlib.util.spec_from_file_location("mb07", os.path.join(HERE, "07_build_materials.py"))
M07 = importlib.util.module_from_spec(_spec)
M07.__dict__["C"] = type("C", (), {"ROOT": ROOT, "TEX_DIR": GENDIR})
_spec.loader.exec_module(M07)
M07.PH_DIR = PH


def lin(hexcol):
    return np.array(M07.srgb(hexcol)[:3])


def to_srgb8(x):
    x = np.clip(x, 0, 1)
    return (np.where(x > 0.0031308, 1.055 * np.power(x, 1 / 2.4) - 0.055, x * 12.92) * 255 + 0.5).astype(np.uint8)


def load_lin(path, size=2048):
    im = np.asarray(Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS), dtype=np.float32) / 255.0
    return np.where(im > 0.04045, ((im + 0.055) / 1.055) ** 2.4, im / 12.92)


def bake_normal(height, strength, path):
    """Tangent-space (OpenGL) normal map from a height field, seamless (wrap-around gradients)."""
    h = np.asarray(Image.fromarray((np.clip(height, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255.0
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength
    n = np.stack([-dx, dy, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(path, quality=92)


def bake_detail(src, target, keep, contrast, name):
    """Same maths as 07 ph_surface: site colour x normalised texture detail (+ keep of its own colour)."""
    tex = load_lin(src)
    lum = tex @ np.array([0.2126, 0.7152, 0.0722])
    mu = max(float(lum.mean()), 1e-3)
    det = 1.0 + (lum / mu - 1.0) * contrast
    col = lin(target)[None, None, :] * det[..., None]
    if keep > 0:
        col = col * (1 - keep) + tex * (M07.lum_of(target) / mu) * keep
    cp = os.path.join(TEX_OUT, name + "_COL.jpg")
    Image.fromarray(to_srgb8(col)).save(cp, quality=92)
    npth = os.path.join(TEX_OUT, name + "_NRM.jpg")
    bake_normal(det / max(det.max(), 1e-3), 6.0, npth)
    return cp, npth


# material -> how to bake it: ("ph", slug, tile, target, keep, contrast) | ("gen", TEX_NAME, tile, tint) | colour hex
BAKE = {k: ("ph",) + tuple(v) + ((1.0,) if len(v) == 4 else ()) for k, v in M07.PH_MAP.items()}
BAKE.update({
    "T01_Terrain_Soil_Sand_Rock": ("ph", "aerial_ground_rock", 9.0, "#B08458", 0.0, 0.6),
    "M10_Pool_Mosaic": ("gen", "TEX_POOL_MOSAIC", 0.5),
    "M12_Roof_Gravel": ("gen", "TEX_GRAVEL", 1.0),
    "Kerb_Concrete": ("gen", "TEX_CONCRETE", 2.0),
    "T03_Lawn": ("gen", "TEX_LAWN", 2.0),
})
FLAT = {   # plain colours of the procedural materials (hex from 07_build_materials)
    "M11_Asphalt": "#5E5B57", "A09_Sports_Court_Clay": "#B4583A", "H03_Ocean": "#0B3A44", "M10_Lake_Water": "#A9D8D2",
    "M10_Pool_Water": "#D4F2F0", "T03_Grass_Blade": "#5F7A33", "V01_Palm_Leaf": "#5E7536", "V01_Palm_Skirt": "#9E8462",
    "V01_Palm_Trunk": "#7D6650", "V04_Ornamental_Grass": "#B7A56E", "A06_Interior_Proxy": "#A88060", "V06_Bougainvillea": "#A42F66",
    "M06_Glass": "#2B3438",   # dark tint: D5 does not take Blender transmission from FBX, so glass would read white
}
ROUGH = {"M06_Glass": 0.02, "M10_Pool_Water": 0.02, "M10_Lake_Water": 0.04, "H03_Ocean": 0.06, "A08_Car_Glass": 0.08,
         "M05_Aluminium_Bronze": 0.38, "A08_Car_Paint": 0.25, "M09_Terrace_Stone": 0.6}


def plain(old):
    """Read colour / metal / roughness / transmission / emission off the old Principled BSDF."""
    ob_ = old.node_tree.nodes.get("Principled BSDF") if old.node_tree else None
    if ob_ is None:
        ob_ = next((n for n in old.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if old.node_tree else None
    vals = {}
    if ob_:
        for k in ("Base Color", "Metallic", "Roughness", "IOR", "Transmission Weight", "Emission Color", "Emission Strength", "Alpha"):
            if k in ob_.inputs and not ob_.inputs[k].is_linked:
                vals[k] = tuple(ob_.inputs[k].default_value) if hasattr(ob_.inputs[k].default_value, "__len__") else ob_.inputs[k].default_value
    return vals


def d5_material(old):
    name = old.name
    m = bpy.data.materials.new(name + "_D5")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    vals = plain(old)
    for k, v in vals.items():
        if k != "Base Color" or name not in FLAT:
            bsdf.inputs[k].default_value = v
    tile = None
    leaf = [n for n in old.node_tree.nodes if n.type == "TEX_IMAGE"] if old.node_tree and name not in BAKE else []
    if name in BAKE:
        spec = BAKE[name]
        if spec[0] == "ph" and M07.ph_maps(spec[1]):
            col, nrm = bake_detail(M07.ph_maps(spec[1])["col"], spec[3], spec[4], spec[5], name)
            tile = spec[2]
        else:
            gen = spec[1] if spec[0] == "gen" else {"M01_Render_Sand": "TEX_RENDER_SAND", "M02_Render_Ochre": "TEX_RENDER_OCHRE",
                                                    "M03_Timber_Pergola": "TEX_TIMBER", "M04_Stone_Rubble": "TEX_STONE_RUBBLE",
                                                    "M07_Pavers_Beige": "TEX_PAVERS", "M09_Terrace_Stone": "TEX_TERRACE_TILES",
                                                    "T01_Terrain_Soil_Sand_Rock": "TEX_TERRAIN_SOIL"}[name]
            col, nrm = os.path.join(TEXDIR, gen + "_COL.jpg"), os.path.join(TEXDIR, gen + "_NRM.jpg")
            tile = spec[2]
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(col, check_existing=True)
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        if os.path.exists(nrm):
            tn = nt.nodes.new("ShaderNodeTexImage")
            tn.image = bpy.data.images.load(nrm, check_existing=True)
            tn.image.colorspace_settings.name = "Non-Color"
            nm = nt.nodes.new("ShaderNodeNormalMap")
            nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
        bsdf.inputs["Roughness"].default_value = ROUGH.get(name, 0.85)
    elif leaf:                                   # leaf cards / palm fans: image -> colour, alpha -> alpha
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = leaf[0].image
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        if old.blend_method in ("HASHED", "CLIP", "BLEND") or "Leaf" in name or "Fan" in name or "Foliage" in name or "Tree" in name:
            nt.links.new(t.outputs["Alpha"], bsdf.inputs["Alpha"])
            m.blend_method = "HASHED"
        bsdf.inputs["Roughness"].default_value = 0.6
    else:
        hexcol = FLAT.get(name)
        if hexcol:
            bsdf.inputs["Base Color"].default_value = (*lin(hexcol), 1.0)
        elif "Base Color" not in vals:
            dc = tuple(old.diffuse_color)
            bsdf.inputs["Base Color"].default_value = dc if dc[:3] != (0.8, 0.8, 0.8) else (0.6, 0.6, 0.6, 1.0)
        for key, r in ROUGH.items():
            if name.startswith(key):
                bsdf.inputs["Roughness"].default_value = r
    m["d5_source"] = name
    return m, tile


def box_uv(me, face_tiles):
    """Box-projected UVs (local metres / tile) on the faces whose material is textured."""
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    co = np.empty(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    for p in me.polygons:
        tile = face_tiles.get(p.material_index)
        if not tile:
            continue
        nx, ny, nz = (abs(c) for c in p.normal)
        ax = (0, 1) if nz >= nx and nz >= ny else ((1, 2) if nx >= ny else (0, 2))
        for li in p.loop_indices:
            v = co[me.loops[li].vertex_index]
            uv[li].uv = (v[ax[0]] / tile, v[ax[1]] / tile)


swapped, done_mesh = {}, set()
for o in list(vl.objects):
    if o.type != "MESH" or not o.data.materials:
        continue
    me = o.data
    face_tiles = {}
    for i, old in enumerate(list(me.materials)):
        if old is None:
            continue
        base = old.get("d5_source", old.name)
        if base not in swapped:
            swapped[base] = d5_material(bpy.data.materials[base]) if base in bpy.data.materials else (old, None)
        newm, tile = swapped[base]
        me.materials[i] = newm
        if tile:
            face_tiles[i] = tile
    if face_tiles and me.name not in done_mesh:
        box_uv(me, face_tiles)
        done_mesh.add(me.name)
white = [b for b, (mm, _) in swapped.items()
         if not mm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].is_linked
         and tuple(mm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value)[:3] in ((1.0, 1.0, 1.0), (0.8, 0.8, 0.8))]
print("D5_MATERIALS", len(swapped), "left white:", white)

# 4. far terrain ring is 60 km wide: keep it (horizon), it is light
mesh_count = sum(1 for o in vl.objects if o.type == "MESH")
tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for o in vl.objects:
    if o.type == "MESH":
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)

fbx = os.path.join(OUT, "Mirleft_Bay_D5.fbx")
bpy.ops.object.select_all(action="DESELECT")
import shutil
bpy.ops.outliner.orphans_purge(do_recursive=True)       # old procedural materials and their images
for img in bpy.data.images:
    src = bpy.path.abspath(img.filepath) if img.filepath else ""
    if src and os.path.exists(src) and os.path.dirname(os.path.abspath(src)) != os.path.abspath(TEX_OUT):
        shutil.copy(src, TEX_OUT)
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, use_visible=True,
                         object_types={"MESH", "CAMERA", "EMPTY"}, apply_unit_scale=True,
                         apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
                         mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="COPY",
                         embed_textures=True, bake_space_transform=False)
blend = os.path.join(OUT, "Mirleft_Bay_D5.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, copy=True)
if os.path.exists(blend + "1"):
    os.remove(blend + "1")
print("D5_EXPORT", {"swapped_materials": len(swapped), "removed": removed, "meshes": mesh_count, "triangles": tris,
                    "fbx_MB": round(os.path.getsize(fbx) / 1e6, 1), "blend_MB": round(os.path.getsize(blend) / 1e6, 1)})
