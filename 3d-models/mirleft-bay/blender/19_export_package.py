"""
19_export_package — D5 Render package (MODE A on request of the client, 2026-10-02).

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

# 3. image-texture materials for D5: FBX cannot carry Blender's procedural node trees, so every
#    procedural material is swapped for a seamless image material and the UVs (in metres) are
#    scaled by 1 / tile size, so D5 shows the texture at true scale with repeat = 1.
TEXDIR = os.path.join(ROOT, "assets", "textures", "tileable")
PH = os.path.join(ROOT, "assets", "textures", "polyhaven")      # client's Poly Haven maps, if present
#   FBX material   ->  (generated texture, tile m, Poly Haven folder or None)
TEXMAP = {
    "M01_Render_Sand": ("TEX_RENDER_SAND", 2.0, "white_plaster_rough_01"),
    "M02_Render_Ochre": ("TEX_RENDER_OCHRE", 2.0, "white_plaster_rough_01"),
    "M03_Timber_Pergola": ("TEX_TIMBER", 1.0, "wood_planks"),
    "M04_Stone_Rubble": ("TEX_STONE_RUBBLE", 1.5, "stacked_stone_wall"),
    "M07_Pavers_Beige": ("TEX_PAVERS", 1.0, "patterned_paving"),
    "M09_Terrace_Stone": ("TEX_TERRACE_TILES", 1.2, "marble_tiles"),
    "M10_Pool_Mosaic": ("TEX_POOL_MOSAIC", 0.5, None),
    "M12_Roof_Gravel": ("TEX_GRAVEL", 1.0, None),
    "Kerb_Concrete": ("TEX_CONCRETE", 2.0, None),
    "T03_Lawn": ("TEX_LAWN", 2.0, None),
    "T01_Terrain_Soil_Sand_Rock": ("TEX_TERRAIN_SOIL", 2.0, "aerial_ground_rock"),   # terrain UV unit = 10 m
}
TINT = {"M01_Render_Sand": (0.82, 0.70, 0.54), "M02_Render_Ochre": (0.72, 0.58, 0.45)}


def ph_maps(folder):
    """Find colour / normal / roughness maps in a Poly Haven download folder (any resolution)."""
    d = os.path.join(PH, folder) if folder else None
    if not d or not os.path.isdir(d):
        return None
    files = []
    for root_, _, fs in os.walk(d):
        files += [os.path.join(root_, f) for f in fs if f.lower().endswith((".jpg", ".png", ".exr"))]
    pick = lambda *keys: next((f for f in files if any(k in os.path.basename(f).lower() for k in keys)), None)
    col = pick("diff", "col", "albedo")
    return {"col": col, "nrm": pick("nor_gl", "normal_gl", "nor"), "rough": pick("rough", "arm")} if col else None


def image_material(old, spec):
    gen, tile, phf = spec
    maps = ph_maps(phf) or {"col": os.path.join(TEXDIR, gen + "_COL.jpg"), "nrm": os.path.join(TEXDIR, gen + "_NRM.jpg"), "rough": None}
    m = bpy.data.materials.new(old.name + "_D5")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(maps["col"], check_existing=True)
    col = tex.outputs["Color"]
    if old.name in TINT and phf and ph_maps(phf):
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        nt.links.new(col, mul.inputs[6])
        mul.inputs[7].default_value = (*TINT[old.name], 1.0)
        col = mul.outputs[2]
    nt.links.new(col, bsdf.inputs["Base Color"])
    if maps.get("nrm") and os.path.exists(maps["nrm"]):
        nimg = nt.nodes.new("ShaderNodeTexImage")
        nimg.image = bpy.data.images.load(maps["nrm"], check_existing=True)
        nimg.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(nimg.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    if maps.get("rough"):
        r = nt.nodes.new("ShaderNodeTexImage")
        r.image = bpy.data.images.load(maps["rough"], check_existing=True)
        r.image.colorspace_settings.name = "Non-Color"
        nt.links.new(r.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = 0.85
    return m, tile


def flat_material(old):
    """Keep simple PBR values (colour / metal / glass / water / emission) from the procedural material."""
    m = bpy.data.materials.new(old.name + "_D5")
    m.use_nodes = True
    nb = m.node_tree.nodes["Principled BSDF"]
    ob_ = old.node_tree.nodes.get("Principled BSDF") if old.node_tree else None
    if ob_:
        for k in ("Base Color", "Metallic", "Roughness", "IOR", "Transmission Weight", "Alpha", "Emission Color", "Emission Strength"):
            if k in ob_.inputs and k in nb.inputs and not ob_.inputs[k].is_linked:
                nb.inputs[k].default_value = ob_.inputs[k].default_value
            elif k in ob_.inputs and ob_.inputs[k].is_linked and k == "Base Color":
                nb.inputs[k].default_value = old.diffuse_color
        # image-based (leaf cards): keep the original material untouched
    return m


swapped, scaled = {}, set()
for o in list(vl.objects):
    if o.type != "MESH" or not o.data.materials:
        continue
    me = o.data
    for i, old in enumerate(list(me.materials)):
        if old is None or old.name.endswith("_D5"):
            continue
        base = old.name
        if base not in TEXMAP and any(n.type == "TEX_IMAGE" for n in old.node_tree.nodes):
            continue                                  # leaf cards: already image based
        if base not in swapped:
            swapped[base] = image_material(old, TEXMAP[base]) if base in TEXMAP else (flat_material(old), None)
        newm, tile = swapped[base]
        me.materials[i] = newm
        if tile and len(me.materials) == 1 and me.name not in scaled and me.uv_layers:
            for d in me.uv_layers.active.data:
                d.uv = (d.uv[0] / tile, d.uv[1] / tile)
            scaled.add(me.name)

# 4. far terrain ring is 60 km wide: keep it (horizon), it is light
mesh_count = sum(1 for o in vl.objects if o.type == "MESH")
tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for o in vl.objects:
    if o.type == "MESH":
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)

fbx = os.path.join(OUT, "Mirleft_Bay_D5.fbx")
bpy.ops.object.select_all(action="DESELECT")
tex_out = os.path.join(OUT, "textures")
os.makedirs(tex_out, exist_ok=True)
for img in bpy.data.images:
    if img.filepath and os.path.exists(bpy.path.abspath(img.filepath)):
        import shutil
        shutil.copy(bpy.path.abspath(img.filepath), tex_out)
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, use_visible=True,
                         object_types={"MESH", "CAMERA", "EMPTY"}, apply_unit_scale=True,
                         apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
                         mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="COPY",
                         embed_textures=True, bake_space_transform=False)
blend = os.path.join(OUT, "Mirleft_Bay_D5.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, copy=True)
print("D5_EXPORT", {"swapped_materials": len(swapped), "removed": removed, "meshes": mesh_count, "triangles": tris,
                    "fbx_MB": round(os.path.getsize(fbx) / 1e6, 1), "blend_MB": round(os.path.getsize(blend) / 1e6, 1)})
