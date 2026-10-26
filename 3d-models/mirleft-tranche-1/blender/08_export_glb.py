"""
08_export_glb — light GLB of the 1er TRANCHE scene, with textures and colours (After Effects,
web viewers, D5...).   python 08_export_glb.py [--ae | --ae-safe]

glTF only carries image textures and plain colours, so every procedural material of the scene is
swapped for a Principled BSDF with
  * a tileable colour image (JPEG, 1024 px max, tint baked in) and box-projected UVs at true size, or
  * a plain colour (glass, aluminium, water, courts, foliage stems...).
Leaf cards, palm fans and the mashrabiya keep their PNG with alpha (alphaMode MASK). The plant library (21_plants,
client 26-10: the detailed palms, olive trees, grasses, agaves, lavender, the jars and the beds' gravel) keeps its
own images on its own UVs.
The 12 duplex pairs (two variants), the loungers and the trees share their meshes, so the file
stays small. No cameras or lights. Units metres, +Y up (glTF). Writes Mirleft_Tranche_1.glb next to
the .blend.
"""
import os
import sys
import tempfile

import bpy  # noqa: I001
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BAY = os.path.join(os.path.dirname(ROOT), "mirleft-bay")
D5 = os.path.join(BAY, "output", "d5", "textures")
TIL = os.path.join(BAY, "assets", "textures", "tileable")
TMP = tempfile.mkdtemp()
SIZE = 1024


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def tinted(src, name, tint_from=None, tint_to=None, size=SIZE):
    """Resized JPEG copy; optional colour shift tint_from -> tint_to (multiplied in linear light)."""
    im = Image.open(src).convert("RGB").resize((size, size), Image.LANCZOS)
    if tint_from:
        a = np.asarray(im).astype(np.float32) / 255.0
        a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
        f = np.array(lin(tint_to)) / np.maximum(np.array(lin(tint_from)), 1e-4)
        a = np.clip(a * f, 0, 1)
        a = np.where(a > 0.0031308, 1.055 * a ** (1 / 2.4) - 0.055, a * 12.92)
        im = Image.fromarray((a * 255).astype(np.uint8))
    p = os.path.join(TMP, name + ".jpg")
    im.save(p, quality=85)
    return p


def gen_tiles(name, cols, rows, c1, c2, mortar, period_px=512, stagger=True, diag=False, noise=10):
    """Small generated tile textures (bejmat, roof tiles, diagonal pavers, asphalt)."""
    rng = np.random.default_rng(len(name))
    N = period_px
    im = Image.new("RGB", (N, N), mortar)
    d = ImageDraw.Draw(im)
    if diag:                                   # diamonds (squares at 45 deg), two per tile each way
        h = N // 4
        for i in range(-1, 3):
            for j in range(-1, 3):
                for (cx, cy), col in (((i * 2 * h, j * 2 * h), c1), ((i * 2 * h + h, j * 2 * h + h), c2)):
                    d.polygon([(cx, cy - h + 3), (cx + h - 3, cy), (cx, cy + h - 3), (cx - h + 3, cy)], fill=col)
    elif cols == 0:
        a = rng.normal(0, noise, (N, N, 1)) + np.array(Image.new("RGB", (1, 1), c1)).reshape(1, 1, 3)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    else:
        w, h = N / cols, N / rows
        for j in range(rows):
            off = (w / 2 if (stagger and j % 2) else 0)
            for i in range(-1, cols + 1):
                x0 = i * w + off
                shade = rng.integers(-14, 14)
                base = c1 if rng.random() < 0.5 else c2
                col = tuple(int(np.clip(int(base[k:k + 2], 16) + shade, 0, 255)) for k in (1, 3, 5))
                d.rectangle([x0 + 2, j * h + 2, x0 + w - 2, (j + 1) * h - 2], fill=col)
    a = np.asarray(im).astype(np.int16) + rng.integers(-6, 6, (N, N, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    p = os.path.join(TMP, name + ".jpg")
    im.save(p, quality=88)
    return p


GEN = os.path.join(ROOT, "data", "textures")          # textures drawn by lib.py (rev 4)

# material -> (texture path, tile size in metres)
TEX = {
    "M01_Render_Sand": (tinted(os.path.join(D5, "M01_Render_Sand_COL.jpg"), "render_sand", "#D2B289", "#C8AA86"), 2.5),
    "M02_Render_Ochre": (tinted(os.path.join(D5, "M02_Render_Ochre_COL.jpg"), "render_ochre"), 2.5),
    "D04_Render_Trim": (tinted(os.path.join(D5, "M01_Render_Sand_COL.jpg"), "render_trim", "#D2B289", "#E6D3B2"), 2.5),
    "D10_Render_Terre_De_Sienne": (tinted(os.path.join(D5, "M01_Render_Sand_COL.jpg"), "render_sienna", "#D2B289", "#B9774C"), 2.5),
    "M03_Timber_Pergola": (tinted(os.path.join(D5, "M03_Timber_Pergola_COL.jpg"), "timber"), 1.2),
    "M07_Pavers_Beige": (tinted(os.path.join(D5, "M07_Pavers_Beige_COL.jpg"), "pavers"), 2.0),
    "M09_Terrace_Stone": (tinted(os.path.join(D5, "M09_Terrace_Stone_COL.jpg"), "terrace"), 2.4),
    "M10_Pool_Mosaic": (tinted(os.path.join(D5, "M10_Pool_Mosaic_COL.jpg"), "pool_mosaic", size=512), 0.5),
    "T01_Terrain_Soil_Sand_Rock": (tinted(os.path.join(D5, "T01_Terrain_Soil_Sand_Rock_COL.jpg"), "terrain"), 9.0),
    "T16_Site_Land_Soil": (tinted(os.path.join(D5, "T01_Terrain_Soil_Sand_Rock_COL.jpg"), "site_land", "#FFFFFF", "#CFB6A8"), 18.0),
    "T03_Lawn": (tinted(os.path.join(TIL, "TEX_LAWN_COL.jpg"), "lawn"), 2.0),
    "Kerb_Concrete": (tinted(os.path.join(TIL, "TEX_CONCRETE_COL.jpg"), "paving", size=512), 2.0),
    "T22_Trottoir_Kerb_Entrance": (tinted(os.path.join(TIL, "TEX_CONCRETE_COL.jpg"), "paving_ent", size=512), 2.0),
    "M12_Roof_Gravel": (tinted(os.path.join(TIL, "TEX_GRAVEL_COL.jpg"), "roof", size=512), 1.0),
    "M11_Asphalt": (gen_tiles("asphalt", 0, 0, "#5E5B57", None, (90, 88, 84), noise=14), 2.0),
    "M11_Asphalt_Entrance": (gen_tiles("asphalt_ent", 0, 0, "#5E5B57", None, (90, 88, 84), noise=14), 2.0),
    "D05_Bejmat_Terre_De_Sienne": (gen_tiles("bejmat", 10, 20, "#A0522D", "#8B4526", (110, 74, 54)), 1.0),
    "D11_Roof_Tiles_Terracotta": (gen_tiles("roof_tiles", 4, 6, "#A9573A", "#8E452D", (107, 59, 42)), 1.2),
    "D12_Island_Diagonal_Pavers": (gen_tiles("island", 2, 2, (220, 209, 189), (205, 191, 166), (156, 144, 128), diag=True), 1.414),
    "M04_Stone_Rubble": (tinted(os.path.join(D5, "M04_Stone_Rubble_COL.jpg"), "stone"), 2.0),
    "T01_Pavers_Herringbone_Charcoal": (gen_tiles("lane", 10, 20, "#5A5B5E", "#4B4C50", (56, 57, 59)), 2.0),
    "T01_Pavers_Herringbone_Beige": (tinted(os.path.join(GEN, "TEX_PAVERS_BEIGE_HERRINGBONE.jpg"), "lane"), 0.8),
    "T21_Trottoir_Herringbone_Entrance": (tinted(os.path.join(GEN, "TEX_PAVERS_BEIGE_HERRINGBONE.jpg"), "lane_ent"), 0.8),
    "T02_Pavers_Herringbone_Light": (gen_tiles("terrace_hb", 10, 20, "#D9D6CF", "#CBC7BE", (169, 164, 154)), 2.0),
    "T03_Terracotta_Herringbone": (gen_tiles("terracotta", 10, 20, "#C47A4F", "#B26A42", (138, 90, 64)), 2.0),
    "T04_Concrete_Slabs": (gen_tiles("concrete", 5, 5, "#C9C6BF", "#BDB9B1", (158, 154, 146), stagger=False), 2.0),
    "T05_Stabilise_Sand": (gen_tiles("stabilise", 0, 0, "#CDB894", None, (205, 184, 148), noise=12), 2.0),
    "T06_Travertine_Deck": (gen_tiles("travertine", 4, 6, "#E6DCC8", "#DCCFB7", (194, 180, 154)), 2.4),
    "D09_Sand": (gen_tiles("sand", 0, 0, "#D9C49A", None, (217, 196, 154), noise=10), 2.0),
    "T13_Travertine_Planks": (gen_tiles("planks", 2, 8, "#E5D8C0", "#D7C7AA", (185, 169, 142)), 1.8),
    "T12_Overflow_Grille_Black": (gen_tiles("grille", 16, 16, "#2A2A2C", "#1F1F21", (6, 6, 6), stagger=False), 0.56),
    # rev 4: villa N°09 finishes, beige pavers, beige and green tiles
    "D13_Render_Villa_Beige": (tinted(os.path.join(D5, "M01_Render_Sand_COL.jpg"), "render_villa", "#D2B289", "#C8AA86"), 2.5),
    "D14_Stone_Surround_Taupe": (gen_tiles("surround", 0, 0, "#B09A82", None, (176, 154, 130), noise=16), 1.0),
    "D15_Stone_Ledge_Grey": (gen_tiles("ledge", 0, 0, "#BAB4AB", None, (186, 180, 171), noise=10), 1.0),
    "D16_Stone_Band_Ochre": (tinted(os.path.join(GEN, "TEX_STONE_BAND_OCHRE.jpg"), "band"), 0.8),
    "D18_Stone_Cladding_Beige": (tinted(os.path.join(D5, "M04_Stone_Rubble_COL.jpg"), "cladding", "#BC9461", "#C3B39D"), 1.8),
    "D19_Coping_Beige_Stone": (gen_tiles("coping_beige", 0, 0, "#CDBBA6", None, (205, 187, 166), noise=10), 1.0),
    "T17_Pavers_Beige_Herringbone": (tinted(os.path.join(GEN, "TEX_PAVERS_BEIGE_HERRINGBONE.jpg"), "pave_beige"), 0.8),
    "T20_Pavers_Sidewalk_Beige": (tinted(os.path.join(GEN, "TEX_PAVERS_BEIGE_HERRINGBONE.jpg"), "pave_side"), 0.8),
    "T27_Trottoirs_Grey": (tinted(os.path.join(GEN, "TEX_PAVERS_SIDEWALK_GREY.jpg"), "trottoirs_grey"), 0.8),
    "T23_Lane_1_Herringbone": (tinted(os.path.join(GEN, "TEX_PAVERS_BEIGE_HERRINGBONE.jpg"), "lane_1"), 0.8),
    "T24_Lane_2_Herringbone": (tinted(os.path.join(GEN, "TEX_PAVERS_BEIGE_HERRINGBONE.jpg"), "lane_2"), 0.8),
    "T25_Commerce_Terrace_Squares": (gen_tiles("terrace_squares", 10, 20, "#5A5B5E", "#4B4C50", (56, 57, 59)), 2.0),
    "T26_Commerce_Strip_Beige": (tinted(os.path.join(GEN, "TEX_PAVERS_BEIGE_HERRINGBONE.jpg"), "strip_beige"), 0.8),
    "T18_Tile_Ardesia_Beige": (tinted(os.path.join(GEN, "TEX_TILE_ARDESIA_BEIGE.jpg"), "tile_ardesia"), 1.2),
    "T19_Tile_Jade_Green": (tinted(os.path.join(GEN, "TEX_TILE_JADE_GREEN.jpg"), "tile_jade"), 1.2),
}
FLAT = {   # plain colours (hex), roughness, metallic
    "A06_Interior_Proxy": ("#D2C2AA", 0.9, 0.0), "D02_Door_Wood_Dark": ("#5C3A22", 0.6, 0.0),
    "D03_Slate_Access": ("#4F5257", 0.7, 0.0), "D06_Synthetic_Turf": ("#3F7F3A", 0.9, 0.0),
    "D07_Tennis_Acrylic": ("#2F6E8F", 0.6, 0.0), "D08_Play_Rubber": ("#C9734A", 0.9, 0.0),
    "M05_Aluminium_Bronze": ("#433C37", 0.38, 0.8), "M06_Glass": ("#8FA2A8", 0.05, 0.0),
    "M10_Pool_Water": ("#4FA9CC", 0.05, 0.0), "Road_Paint_White": ("#EDEBE6", 0.6, 0.0),
    "T02_Terrain_Cut_Soil": ("#8C6E52", 0.95, 0.0), "V01_Palm_Leaf": ("#5E7536", 0.6, 0.0),
    "V01_Palm_Skirt": ("#9E8462", 0.9, 0.0), "V01_Palm_Trunk": ("#7D6650", 0.9, 0.0),
    "A01_Cushion_White": ("#EDE7DA", 0.8, 0.0), "A02_Metal_Dark": ("#2E2E30", 0.4, 0.7),
    "V05_Hedge": ("#4E6B34", 0.85, 0.0), "T07_Coping_White_Stone": ("#EEE8DC", 0.5, 0.0),
    "T08_Planter_Soil": ("#6B5240", 0.95, 0.0), "T09_Pool_Cover_Blue": ("#2C5E8C", 0.5, 0.0),
    "T10_Terrain_Cut_Soil": ("#8C6E52", 0.95, 0.0), "T11_Road_Paint_White": ("#E9E7E0", 0.6, 0.0),
    "T14_Lounger_White_Resin": ("#F1EFE9", 0.35, 0.0), "T15_Parasol_Canvas": ("#D9C8A9", 0.85, 0.0),
    "V09_Agave_Leaf": ("#7E9B8A", 0.6, 0.0), "V04_Ornamental_Grass": ("#B7A56E", 0.75, 0.0),
    "H04_Ocean_Atlantic": ("#1E5A6C", 0.08, 0.0),
    "D17_Frame_Aluminium_Quartz": ("#A99F8F", 0.45, 0.0), "A06_Curtain_Linen": ("#E9DFCF", 0.95, 0.0),
    "A07_Curtain_Sheer": ("#F2ECE1", 0.9, 0.0),
    "A08_Interior_Warm": ("#C9A47E", 0.9, 0.0), "A09_Interior_Floor": ("#C9B394", 0.6, 0.0),
    "A10_Sofa_Linen": ("#D8CBB4", 0.9, 0.0), "A11_Cushion_Grey": ("#8E857A", 0.9, 0.0),
    "Lamp_Warm": ("#FFC98F", 0.5, 0.0),                      # the SPA's lanterns (set emissive in D5)
}
ALPHA = {"D01_Mashrabiya_Wood": "#3B2414", "V01_Palm_Fan": None, "V03_Olive_Foliage": None,
         "V07_Pink_Blossom_Tree": None, "V08_Green_Shade_Tree": None}


def new_mat(old):
    name = old.name
    m = bpy.data.materials.new(name + "_GLB")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.85
    tile = None
    if name.startswith("T2_") and name not in TEX and name not in FLAT:   # Tranche 2's copies of Tranche 1's materials
        base = max((k for k in list(TEX) + list(FLAT) if name[3:].startswith(k)), key=len, default=None)
        if base:
            name = base
    if name in TEX:
        path, tile = TEX[name]
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(path, check_existing=True)
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    elif name.startswith("V2_"):                  # client 26-10: the plant library keeps its own image on its own UVs
        src = next((n.image for n in old.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
        if src is not None:
            alpha = src.filepath.lower().endswith(".png")
            im = Image.open(bpy.path.abspath(src.filepath)).convert("RGBA" if alpha else "RGB")
            im.thumbnail((SIZE, SIZE), Image.LANCZOS)
            p = os.path.join(TMP, name + (".png" if alpha else ".jpg"))
            im.save(p) if alpha else im.save(p, quality=88)
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(p, check_existing=True)
            nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
            if alpha:
                nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
                m.blend_method = "CLIP"
            ob_ = next((n for n in old.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            b.inputs["Roughness"].default_value = ob_.inputs["Roughness"].default_value if ob_ else 0.7
    elif name in ALPHA:
        src = next((n.image for n in old.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
        if src is not None:
            im = Image.open(bpy.path.abspath(src.filepath) if src.filepath else src.filepath_raw).convert("RGBA")
            if ALPHA[name]:                       # mashrabiya: white lattice -> dark timber
                r, g, bb = (int(ALPHA[name][k:k + 2], 16) for k in (1, 3, 5))
                a = np.asarray(im).copy()
                a[..., 0], a[..., 1], a[..., 2] = r, g, bb
                im = Image.fromarray(a)
            im = im.resize((min(im.width, 512), min(im.height, 512)), Image.LANCZOS)
            p = os.path.join(TMP, name + ".png")
            im.save(p)
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(p, check_existing=True)
            nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
            nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
            m.blend_method = "CLIP"
            b.inputs["Roughness"].default_value = 0.6
        if name == "D01_Mashrabiya_Wood":
            tile = 0.5
    else:
        hexcol, rough, metal = FLAT.get(name, ("#B0A090", 0.85, 0.0))
        b.inputs["Base Color"].default_value = (*lin(hexcol), 1.0)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        if name == "M06_Glass":                   # see-through, so the curtains and the salon show (19-10); a
            b.inputs["Alpha"].default_value = 0.35   # lighter glass on a lit room behind, never black (22-10)
            m.blend_method = "BLEND"
    return m, tile


def box_uv(me, face_tiles):
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


def main():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "Mirleft_Tranche_1.blend"))
    vl = bpy.context.view_layer
    swapped, done = {}, set()
    for o in list(vl.objects):
        if o.type != "MESH" or o.hide_render:
            continue
        me = o.data
        if me.name in done:
            continue
        face_tiles = {}
        for i, old in enumerate(list(me.materials)):
            if old is None:
                continue
            if old.name not in swapped:                 # satellite terrain: already an image material
                swapped[old.name] = (old, None) if old.name.startswith("GEO_") else new_mat(old)
            newm, tile = swapped[old.name]
            me.materials[i] = newm
            if tile:
                face_tiles[i] = tile
        if face_tiles:
            box_uv(me, face_tiles)
        done.add(me.name)
    out = os.path.join(ROOT, "Mirleft_Tranche_1.glb")
    if "--ae" in sys.argv:
        # After Effects: origin at the centre of the tranche, its ground at height 0
        cx, cy, cz = centre()
        for o in vl.objects:
            if o.parent is None:
                o.location.x -= cx
                o.location.y -= cy
                o.location.z -= cz
        out = os.path.join(ROOT, "Mirleft_Tranche_1_AE_centred.glb")
    if "--ae-safe" in sys.argv:
        out = ae_safe(vl)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_visible=True, export_cameras=False,
                              export_lights=False, export_apply=True, export_image_format="JPEG" if "--ae-safe" in sys.argv else "AUTO",
                              export_materials="EXPORT", export_yup=True, export_draco_mesh_compression_enable=False)
    print("GLB", round(os.path.getsize(out) / 2 ** 20, 1), "MiB", "materials", len(swapped), "meshes", len(done))
    if "--ae-safe" in sys.argv:
        export_obj(out)


def centre():
    import json
    site = json.load(open(os.path.join(ROOT, "data", "site.json")))
    a, b, c = site["plane"]
    cx, cy = 5.0, 5.0
    return cx, cy, a * cx + b * cy + c


def ae_safe(vl):
    """Most compatible variant (After Effects): the tranche only (no empty-land terrain), no
    alpha-card trees, every instance made real and joined into ONE mesh, centred on the tranche
    with its ground at height 0. Plain JPEG textures and colours."""
    src = bpy.data.collections.get("SRC")
    if src is not None:
        for o in list(src.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    for o in list(vl.objects):
        if o.type != "MESH" or o.name.startswith(("TERRAIN", "VEG_")) or o.hide_render:
            bpy.data.objects.remove(o, do_unlink=True)
    vl.update()
    for o in list(bpy.data.objects):
        if o.type in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(o, do_unlink=True)
    mats = [m for m in bpy.data.materials if m.name.endswith("_GLB") and m.node_tree and
            any(n.type == "TEX_IMAGE" and n.image and n.image.filepath.lower().endswith(".png") for n in m.node_tree.nodes)]
    for m in mats:                     # mashrabiya: opaque dark timber instead of the alpha lattice
        nt = m.node_tree
        for n in [n for n in nt.nodes if n.type == "TEX_IMAGE"]:
            nt.nodes.remove(n)
        m.blend_method = "OPAQUE"
        b = nt.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*lin("#3B2414"), 1.0)
        b.inputs["Alpha"].default_value = 1.0
    vl.update()
    obs = [o for o in vl.objects if o is not None and o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    vl.objects.active = obs[0]
    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    ob = vl.objects.active
    ob.name = ob.data.name = "MIRLEFT_TRANCHE_1"
    cx, cy, cz = centre()
    ob.data.transform(__import__("mathutils").Matrix.Translation((-cx, -cy, -cz)))
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("AE_SAFE one mesh", tris, "triangles", len(ob.data.materials), "materials")
    return os.path.join(ROOT, "Mirleft_Tranche_1_AE_SAFE.glb")


def export_obj(glb):
    """OBJ + MTL + JPEG textures of the same single mesh, zipped (After Effects also reads OBJ)."""
    import shutil
    import zipfile
    d = os.path.join(TMP, "Mirleft_Tranche_1_OBJ")
    os.makedirs(d, exist_ok=True)
    objp = os.path.join(d, "Mirleft_Tranche_1.obj")
    bpy.ops.wm.obj_export(filepath=objp, export_selected_objects=False, forward_axis="NEGATIVE_Z", up_axis="Y",
                          export_materials=True, path_mode="COPY", export_uv=True, export_normals=True)
    z = os.path.join(ROOT, "Mirleft_Tranche_1_OBJ.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(d):
            zf.write(os.path.join(d, f), f)
    print("OBJ_ZIP", round(os.path.getsize(z) / 2 ** 20, 1), "MiB", len(os.listdir(d)), "files")


if __name__ == "__main__":
    main()
