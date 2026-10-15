"""
09_export_d5 — D5 Render package of the 1er TRANCHE scene: FBX with its textures.

    python 09_export_d5.py

D5 reads a Principled BSDF with images plugged straight into it; the scene's node materials (procedural
tiles, stone, noise) would come in white. Every material is swapped as in 08_export_glb (tileable
colour image with the tint baked in and box-projected UVs at true size, or a plain colour), keeps its
name, and the textured ones get a normal map baked from their colour image. Writes d5/:
  Mirleft_Tranche_1_D5_FULL.fbx       everything (buildings, ground, pool court, furniture, plants, the
                                      13 cameras), textures embedded
  Mirleft_Tranche_1_D5_NO_TREES.fbx   the same without trees, palms, shrubs, agaves and grasses, to place
                                      D5 library plants; textures embedded
  textures/                           the same images, to reassign by hand if a material comes in white
  D5_IMPORT_GUIDE.md
and zips the folder to Mirleft_Tranche_1_D5.zip next to the .blend.
"""
import importlib.util
import os
import shutil
import zipfile

import bpy  # noqa: I001
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "d5")
TEX_OUT = os.path.join(OUT, "textures")
_spec = importlib.util.spec_from_file_location("t1_08", os.path.join(HERE, "08_export_glb.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)


def bake_normal(src, dst, strength=4.0):
    """Tangent-space (OpenGL) normal map from the colour image's luminance, seamless."""
    a = np.asarray(Image.open(src).convert("L").filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float32) / 255.0
    dx = (np.roll(a, -1, 1) - np.roll(a, 1, 1)) * strength
    dy = (np.roll(a, -1, 0) - np.roll(a, 1, 0)) * strength
    n = np.stack([-dx, dy, np.ones_like(a)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(dst, quality=90)


def d5_materials(vl):
    swapped, done = {}, set()
    for o in list(vl.objects):
        if o.type != "MESH":
            continue
        me = o.data
        if me.name in done:
            continue
        face_tiles = {}
        for i, old in enumerate(list(me.materials)):
            if old is None:
                continue
            if old.name not in swapped:
                swapped[old.name] = G.new_mat(old)
            newm, tile = swapped[old.name]
            me.materials[i] = newm
            if tile:
                face_tiles[i] = tile
        if face_tiles:
            G.box_uv(me, face_tiles)
        done.add(me.name)
    for name, (m, tile) in swapped.items():
        bpy.data.materials[name].name = name + "_blender"
        m.name = name
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        imgs = [n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image]
        if not imgs:
            continue
        t = imgs[0]
        src = bpy.path.abspath(t.image.filepath)
        ext = os.path.splitext(src)[1].lower()
        col = os.path.join(TEX_OUT, f"{name}_COL{ext}")
        shutil.copy(src, col)
        t.image.filepath = col
        t.image.reload()
        if tile and ext in (".jpg", ".jpeg"):               # tileable surfaces: add a normal map
            nrm = os.path.join(TEX_OUT, f"{name}_NRM.jpg")
            bake_normal(col, nrm)
            tn = nt.nodes.new("ShaderNodeTexImage")
            tn.image = bpy.data.images.load(nrm, check_existing=True)
            tn.image.colorspace_settings.name = "Non-Color"
            nm = nt.nodes.new("ShaderNodeNormalMap")
            nm.inputs["Strength"].default_value = 0.6
            nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return swapped


def export(path):
    bpy.ops.export_scene.fbx(filepath=path, use_selection=False, use_visible=True,
                             object_types={"MESH", "CAMERA", "EMPTY"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
                             mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="COPY",
                             embed_textures=True, bake_space_transform=False)
    print("FBX", os.path.basename(path), round(os.path.getsize(path) / 2 ** 20, 1), "MiB", flush=True)


GUIDE = """# D5 import guide: Mirleft 1er TRANCHE

| File | Contents | Use it when |
|---|---|---|
| `Mirleft_Tranche_1_D5_FULL.fbx` | Everything: duplexes, restaurant, commerces, pool court, ground, walls, stairs, furniture, trees, palms and plants, and the 13 cameras | You want everything placed already |
| `Mirleft_Tranche_1_D5_NO_TREES.fbx` | The same without trees, palms, shrubs, agaves and grasses | You place D5 library plants yourself |

Both FBX files carry their textures inside. The same images are in `textures/`: keep that folder next to the FBX.

## Import
1. D5 ▸ Import ▸ Model ▸ the FBX, unit **metres**.
2. Don't import the Blender files (`*.blend`) into D5: their node materials come in white.
3. If a material still shows white, set Base Color to `textures/<material>_COL.jpg` and Normal to `textures/<material>_NRM.jpg`.

## Recommended D5 material swaps
- `M10_Pool_Water` (pools, bassins, fountain) → D5 Water. The tiled floor and walls under it stay visible.
- `M06_Glass` → D5 Glass.
- `T03_Lawn` → D5 Grass (scatter) if you want real grass.

UVs are box-projected in metres divided by each texture's tile size, so the textures sit at true scale with D5 tiling = 1.
The material names are the Blender ones: `T13_Travertine_Planks` (pool deck), `M04_Stone_Rubble` (stone walls), `D05_Bejmat_Terre_De_Sienne`, and so on.
"""


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(TEX_OUT)
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "Mirleft_Tranche_1.blend"))
    vl = bpy.context.view_layer
    src = bpy.data.collections.get("SRC")
    if src is not None:                                       # sources of the shared meshes: not exported
        for o in list(src.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    vl.update()
    swapped = d5_materials(vl)
    print("D5_MATERIALS", len(swapped))
    export(os.path.join(OUT, "Mirleft_Tranche_1_D5_FULL.fbx"))
    for o in list(bpy.data.objects):
        if o.name.startswith("VEG_"):
            bpy.data.objects.remove(o, do_unlink=True)
    export(os.path.join(OUT, "Mirleft_Tranche_1_D5_NO_TREES.fbx"))
    open(os.path.join(OUT, "D5_IMPORT_GUIDE.md"), "w").write(GUIDE)
    z = os.path.join(ROOT, "Mirleft_Tranche_1_D5.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for r, _, fs in os.walk(OUT):
            for f in fs:
                p = os.path.join(r, f)
                zf.write(p, os.path.join("Mirleft_Tranche_1_D5", os.path.relpath(p, OUT)))
    print("D5_ZIP", round(os.path.getsize(z) / 2 ** 20, 1), "MiB")


if __name__ == "__main__":
    main()
