"""
08_export_glb — light GLB of the Tranche A+B scene, with textures and colours (After Effects,
web viewers, D5...).   python 08_export_glb.py

glTF only carries image textures and plain colours, so every procedural material of the scene is
swapped for a Principled BSDF with
  * a tileable colour image (JPEG, 1024 px max, tint baked in) and box-projected UVs at true size, or
  * a plain colour (glass, aluminium, water, courts, foliage stems...).
Leaf cards, palm fans and the mashrabiya keep their PNG with alpha (alphaMode MASK).
The 17 duplexes, the trees and the two boutique/restaurant buildings share their meshes, so the
file stays small. No cameras or lights. Units metres, +Y up (glTF). Writes
Mirleft_Tranche_AB.glb next to the .blend.
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


# material -> (texture path, tile size in metres)
TEX = {
    "M01_Render_Sand": (tinted(os.path.join(D5, "M01_Render_Sand_COL.jpg"), "render_sand"), 2.5),
    "M02_Render_Ochre": (tinted(os.path.join(D5, "M02_Render_Ochre_COL.jpg"), "render_ochre"), 2.5),
    "D04_Render_Trim": (tinted(os.path.join(D5, "M01_Render_Sand_COL.jpg"), "render_trim", "#D2B289", "#E6D3B2"), 2.5),
    "D10_Render_Terre_De_Sienne": (tinted(os.path.join(D5, "M01_Render_Sand_COL.jpg"), "render_sienna", "#D2B289", "#B9774C"), 2.5),
    "M03_Timber_Pergola": (tinted(os.path.join(D5, "M03_Timber_Pergola_COL.jpg"), "timber"), 1.2),
    "M07_Pavers_Beige": (tinted(os.path.join(D5, "M07_Pavers_Beige_COL.jpg"), "pavers"), 2.0),
    "M09_Terrace_Stone": (tinted(os.path.join(D5, "M09_Terrace_Stone_COL.jpg"), "terrace"), 2.4),
    "M10_Pool_Mosaic": (tinted(os.path.join(D5, "M10_Pool_Mosaic_COL.jpg"), "pool_mosaic", size=512), 0.5),
    "T01_Terrain_Soil_Sand_Rock": (tinted(os.path.join(D5, "T01_Terrain_Soil_Sand_Rock_COL.jpg"), "terrain"), 9.0),
    "T03_Lawn": (tinted(os.path.join(TIL, "TEX_LAWN_COL.jpg"), "lawn"), 2.0),
    "Kerb_Concrete": (tinted(os.path.join(TIL, "TEX_CONCRETE_COL.jpg"), "paving", size=512), 2.0),
    "M12_Roof_Gravel": (tinted(os.path.join(TIL, "TEX_GRAVEL_COL.jpg"), "roof", size=512), 1.0),
    "M11_Asphalt": (gen_tiles("asphalt", 0, 0, "#5E5B57", None, (90, 88, 84), noise=14), 2.0),
    "D05_Bejmat_Terre_De_Sienne": (gen_tiles("bejmat", 10, 20, "#A0522D", "#8B4526", (110, 74, 54)), 1.0),
    "D11_Roof_Tiles_Terracotta": (gen_tiles("roof_tiles", 4, 6, "#A9573A", "#8E452D", (107, 59, 42)), 1.2),
    "D12_Island_Diagonal_Pavers": (gen_tiles("island", 2, 2, (220, 209, 189), (205, 191, 166), (156, 144, 128), diag=True), 1.414),
}
FLAT = {   # plain colours (hex), roughness, metallic
    "A06_Interior_Proxy": ("#4A3A2E", 0.9, 0.0), "D02_Door_Wood_Dark": ("#5C3A22", 0.6, 0.0),
    "D03_Slate_Access": ("#4F5257", 0.7, 0.0), "D06_Synthetic_Turf": ("#3F7F3A", 0.9, 0.0),
    "D07_Tennis_Acrylic": ("#2F6E8F", 0.6, 0.0), "D08_Play_Rubber": ("#C9734A", 0.9, 0.0),
    "M05_Aluminium_Bronze": ("#433C37", 0.38, 0.8), "M06_Glass": ("#2B3438", 0.05, 0.0),
    "M10_Pool_Water": ("#4FA9CC", 0.05, 0.0), "Road_Paint_White": ("#EDEBE6", 0.6, 0.0),
    "T02_Terrain_Cut_Soil": ("#8C6E52", 0.95, 0.0), "V01_Palm_Leaf": ("#5E7536", 0.6, 0.0),
    "V01_Palm_Skirt": ("#9E8462", 0.9, 0.0), "V01_Palm_Trunk": ("#7D6650", 0.9, 0.0),
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
    if name in TEX:
        path, tile = TEX[name]
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(path, check_existing=True)
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
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
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "Mirleft_Tranche_AB.blend"))
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
            if old.name not in swapped:
                swapped[old.name] = new_mat(old)
            newm, tile = swapped[old.name]
            me.materials[i] = newm
            if tile:
                face_tiles[i] = tile
        if face_tiles:
            box_uv(me, face_tiles)
        done.add(me.name)
    out = os.path.join(ROOT, "Mirleft_Tranche_AB.glb")
    if "--ae" in sys.argv:
        # After Effects: origin at the centre of Tranche A+B, its ground at height 0
        cx, cy = 17.3, 19.6
        cz = 0.03653 * cx + 0.04115 * cy + 59.41131 - 50.0
        for o in vl.objects:
            if o.parent is None:
                o.location.x -= cx
                o.location.y -= cy
                o.location.z -= cz
        out = os.path.join(ROOT, "Mirleft_Tranche_AB_AE_centred.glb")
    if "--ae-safe" in sys.argv:
        out = ae_safe(vl)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_visible=True, export_cameras=False,
                              export_lights=False, export_apply=True, export_image_format="JPEG" if "--ae-safe" in sys.argv else "AUTO",
                              export_materials="EXPORT", export_yup=True, export_draco_mesh_compression_enable=False)
    print("GLB", round(os.path.getsize(out) / 2 ** 20, 1), "MiB", "materials", len(swapped), "meshes", len(done))
    if "--ae-safe" in sys.argv:
        export_obj(out)


def ae_safe(vl):
    """Most compatible variant (After Effects): Tranche A+B only (no empty-land terrain, the
    satellite photo is the ground), no alpha-card trees, every instance made real and joined
    into ONE mesh, centred on A+B with its ground at height 0. Plain JPEG textures and colours."""
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
    ob.name = ob.data.name = "MIRLEFT_TRANCHE_AB"
    cx, cy = 17.3, 19.6
    cz = 0.03653 * cx + 0.04115 * cy + 59.41131 - 50.0
    ob.data.transform(__import__("mathutils").Matrix.Translation((-cx, -cy, -cz)))
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("AE_SAFE one mesh", tris, "triangles", len(ob.data.materials), "materials")
    return os.path.join(ROOT, "Mirleft_Tranche_AB_AE_SAFE.glb")


def export_obj(glb):
    """OBJ + MTL + JPEG textures of the same single mesh, zipped (After Effects also reads OBJ)."""
    import shutil
    import zipfile
    d = os.path.join(TMP, "Mirleft_Tranche_AB_OBJ")
    os.makedirs(d, exist_ok=True)
    objp = os.path.join(d, "Mirleft_Tranche_AB.obj")
    bpy.ops.wm.obj_export(filepath=objp, export_selected_objects=False, forward_axis="NEGATIVE_Z", up_axis="Y",
                          export_materials=True, path_mode="COPY", export_uv=True, export_normals=True)
    z = os.path.join(ROOT, "Mirleft_Tranche_AB_OBJ.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(d):
            zf.write(os.path.join(d, f), f)
    print("OBJ_ZIP", round(os.path.getsize(z) / 2 ** 20, 1), "MiB", len(os.listdir(d)), "files")


if __name__ == "__main__":
    main()
