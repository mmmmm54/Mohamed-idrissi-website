"""
09_export_d5 — D5 Render package of the 1er TRANCHE scene: FBX with its textures.

    python 09_export_d5.py

D5 reads a Principled BSDF with images plugged straight into it; the scene's node materials (procedural
tiles, stone, noise) would come in white. Every material is swapped as in 08_export_glb (tileable
colour image with the tint baked in and box-projected UVs at true size, or a plain colour), keeps its
name, and the textured ones get a normal map baked from their colour image. Writes d5/:
  Mirleft_Tranche_1_D5_FULL.fbx       everything (buildings, ground, pool court, furniture, plants, the
                                      13 cameras), textures embedded
  Mirleft_Tranche_1_D5_NO_PALMS_TREES.fbx   the same without the palms and trees (shrubs, agaves and
                                      grasses kept), to place D5 library trees; textures embedded
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
            if old.name not in swapped:                 # satellite terrain: already an image material
                swapped[old.name] = (old, None) if old.name.startswith("GEO_") else G.new_mat(old)
            newm, tile = swapped[old.name]
            me.materials[i] = newm
            if tile:
                face_tiles[i] = tile
        if face_tiles:
            G.box_uv(me, face_tiles)
        done.add(me.name)
    for name, (m, tile) in swapped.items():
        if m.name != name or not name.startswith("GEO_"):
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
| `Mirleft_Tranche_1_D5_FULL.fbx` | Everything: duplexes, restaurant, commerces, pool court, ground, walls, stairs, furniture, trees, palms and plants, Tranche 2 (33 villas type B), and the 20 cameras | You want everything placed already |
| `Mirleft_Tranche_1_D5_NO_PALMS_TREES.fbx` | The same without the palms and trees; the shrubs, agaves and grasses stay | You place D5 library palms and trees yourself |

Both FBX files carry their textures inside. The same images are in `textures/`: keep that folder next to the FBX.

## Import
1. D5 ▸ Import ▸ Model ▸ the FBX, unit **metres**.
2. Don't import the Blender files (`*.blend`) into D5: their node materials come in white.
3. If a material still shows white, set Base Color to `textures/<material>_COL.jpg` and Normal to `textures/<material>_NRM.jpg`.

## Recommended D5 material swaps
- `M10_Pool_Water` (pools, bassins, fountain) → D5 Water. The tiled floor and walls under it show through: green
  `T19_Tile_Jade_Green` in the two pools, blue mosaic in the bassins and the fountain.
- `H04_Ocean_Atlantic` (the ocean, at sea level) → D5 Water (ocean preset).
- `T16_Site_Land_Soil` (the project's land inside its boundary) can take any D5 soil material; keep it darker than the satellite ground so the limits read.
- `M06_Glass` → D5 Glass.
  It comes in see-through (opacity 0.22) so the curtains and the salon behind the villas' sliding doors show;
  `A07_Curtain_Sheer` → D5 Fabric with some translucency for the sheer curtains.

## Terrain and ocean round the site
The real surroundings come in with the model (collection `00_SURROUNDINGS`): the terrain over ±3 km (20 m) and out to
±12 km (150 m), with a Sentinel-2 satellite image on it (`GEO_Satellite_Near`, `GEO_Satellite_Far`), and the ocean.
The heights are AWS Terrain Tiles (SRTM). Image: Contains modified Copernicus Sentinel data 2025.
The project's land (the site boundary minus the tranche) sits on it in its own brown soil, `T16_Site_Land_Soil`
(object `TERRAIN_SITE_EMPTY_LAND`, collection `01_TERRAIN`), the real ground 0.60 m lower along its limits, so
a short cut face (`T10_Terrain_Cut_Soil`) marks the boundary, with the boundary posts at its corners.
- `T03_Lawn` → D5 Grass (scatter) if you want real grass.

UVs are box-projected in metres divided by each texture's tile size, so the textures sit at true scale with D5 tiling = 1.
The material names are the Blender ones: `T13_Travertine_Planks` (pool deck), `M04_Stone_Rubble` (stone walls), `D05_Bejmat_Terre_De_Sienne`, and so on.

## Rev 4 finishes (remarks on the D5 model)
- The ground is split so each part can be finished on its own in D5 (separate objects and materials):
  - by the villas: roads `GROUND_ROADS_VILLAS` (`M11_Asphalt`), the lane by D-1 to D-4 `GROUND_LANE_1` (`T23_Lane_1_Herringbone`), the lane by D-13 to D-18 `GROUND_LANE_2` (`T24_Lane_2_Herringbone`), pavements `GROUND_PAVEMENTS_VILLAS` (`Kerb_Concrete`);
  - in the entrance zone: roads `GROUND_ROADS_ENTRANCE` (`M11_Asphalt_Entrance`), herringbone trottoirs `GROUND_TROTTOIRS_HERRINGBONE_ENTRANCE` (`T21_Trottoir_Herringbone_Entrance`), kerb trottoirs `GROUND_TROTTOIRS_KERB_ENTRANCE` (`T22_Trottoir_Kerb_Entrance`);
  - commerce terrace `GROUND_TERRACOTTA` (`T03_Terracotta_Herringbone`), the dark squares in that terrace `GROUND_COMMERCE_TERRACE_SQUARES` (`T25_Commerce_Terrace_Squares`), the strip between the commerces and D-1/D-2 `GROUND_COMMERCE_STRIP_BEIGE` (`T26_Commerce_Strip_Beige`), the trottoirs along the commerces and the restaurant plaza to the road `GROUND_TROTTOIRS_COMMERCES_RESTAURANT` (`T20_Pavers_Sidewalk_Grey`), restaurant terrace and plaza `GROUND_TERRACE` (`T02_Pavers_Herringbone_Light`), playground `GROUND_COURT_TILE` (`T18_Tile_Ardesia_Beige`), villa entrance paths `DUPLEX_ENTRANCE_PATHS` (`T17_Pavers_Beige_Herringbone`), rear terraces `DUPLEX_REAR_TERRACES` (`M09_Terrace_Stone`).
- Beige paver and grey trottoir textures are in `data/textures/` of the repository if you want them (`TEX_PAVERS_BEIGE_HERRINGBONE.jpg`, `TEX_PAVERS_SIDEWALK_GREY.jpg`).
- `T18_Tile_Ardesia_Beige`: the ground of the playground area by the pool (AZUVI Ardesia Nature type, 30 x 60).
  In D5 it can be swapped for the real product's texture if you have it.
- `T19_Tile_Jade_Green`: the two pools (La Platera Jade type, 30 x 60).
- Duplexes (villa N°09): `D13_Render_Villa_Beige` walls, `D14_Stone_Surround_Taupe` window and door surrounds,
  `D15_Stone_Ledge_Grey` and `D16_Stone_Band_Ochre` cornice, `D17_Frame_Aluminium_Beige` aluminium frames (windows, balcony and garden sliding doors), `D18_Stone_Cladding_Beige`
  front garden walls with `D19_Coping_Beige_Stone`, `M03_Timber_Pergola` pergolas and railings.

## Tranche 2: villas type B (21-10)
The type B blocks of the plan de masse 31-05-13 west of the tranche: 33 villas (the northern block 21, the southern
block 12), villa type B of `5-VILLA_TYPE_B.DWG` with its own pool, in the finishes of the duplexes above
(same render, surrounds, cornice, beige aluminium, pergolas, jade pool tiles). Everything of Tranche 2 is in its own
collections (`T2_01_GROUND`, `T2_02_VILLAS`, `T2_03_LANDSCAPE`, `T2_04_TREES_PALMS`) and objects, and its ground in
its own materials, so it can be finished apart from Tranche 1:
- villas `T2_VILLA_B01` to `T2_VILLA_B33` (one mesh shared, the mirrored ones another);
- streets `T2_GROUND_ROADS` (`T2_M11_Asphalt`), pavements `T2_GROUND_PAVEMENTS` (`T2_T17_Pavers_Beige_Herringbone_Pavements`),
  kerbs `T2_GROUND_KERBS` (`T2_Kerb_Concrete`), gardens `T2_GROUND_GARDENS_LAWN` (`T2_T03_Lawn_Gardens`), paths to the doors
  `T2_GROUND_ENTRANCE_PATHS` (`T2_T17_Pavers_Beige_Herringbone_Paths`),
  the parking bays `T2_GROUND_PARKING` (`T2_M11_Asphalt_Parking`) with their lines, the Centre d'entretien and the
  Office `T2_BUILDINGS_CENTRE_ENTRETIEN_OFFICE`;
- garden walls `T2_WALLS_GARDENS`, street front walls with gate pillars and gates `T2_WALLS_FRONT_GATES`, palm pits `T2_TREE_PITS`.
Cameras `T2_CAM_01` to `T2_CAM_07`.
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
    for cn in ("06_TREES_PALMS", "T2_04_TREES_PALMS"):
        trees = bpy.data.collections.get(cn)
        for o in list(trees.objects if trees else []):
            bpy.data.objects.remove(o, do_unlink=True)
    export(os.path.join(OUT, "Mirleft_Tranche_1_D5_NO_PALMS_TREES.fbx"))
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
