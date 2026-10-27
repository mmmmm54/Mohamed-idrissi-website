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
import math
import os
import shutil
import zipfile

import bpy  # noqa: I001
import bmesh  # after bpy, which provides it
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


# client 22-10: Tranche 2's ground takes Tranche 1's own materials in D5, so a texture changed there changes
# both tranches together (their copies looked the same in Blender but were finished apart in D5)
T2_SAME = {"T2_T17_Pavers_Beige_Herringbone": "T17_Pavers_Beige_Herringbone",
           "T2_T17_Pavers_Beige_Herringbone_Parking": "T17_Pavers_Beige_Herringbone",
           "T2_T17_Pavers_Beige_Herringbone_Paths": "T17_Pavers_Beige_Herringbone",
           "T2_Kerb_Concrete": "Kerb_Concrete", "T2_T03_Lawn_Gardens": "T03_Lawn", "T2_T03_Lawn_Verges": "T03_Lawn"}


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
            if old.name in T2_SAME and bpy.data.materials.get(T2_SAME[old.name]):
                old = bpy.data.materials[T2_SAME[old.name]]
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
| `Mirleft_Tranche_1_D5_FULL.fbx` | Everything: duplexes, restaurant, commerces, pool court, ground, walls, stairs, furniture, trees, palms and plants, Tranche 2 (33 villas type B, 12 villas type C, the SPA), Tranche 3 (the hotel, 4 villas type A), and the cameras | You want everything placed already |
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
  - by the villas: roads `GROUND_ROADS_BEIGE_T1_T2` (with Tranche 2's streets and bays, in `T17_Pavers_Beige_Herringbone` since 22-10), the lane by D-1 to D-4 `GROUND_LANE_1` (`T23_Lane_1_Herringbone`), the lane by D-13 to D-18 `GROUND_LANE_2` (`T24_Lane_2_Herringbone`), the other lanes `GROUND_LANES_VILLAS` (`T01_Pavers_Herringbone_Beige`), all in the beige pavers since 22-10, pavements `GROUND_KERBS_T1_T2` (`Kerb_Concrete`, with Tranche 2's kerbs);
  - in the entrance zone: roads `GROUND_ROADS_BEIGE_ENTRANCE` (`T17_Pavers_Beige_Herringbone` since 22-10), herringbone trottoirs `GROUND_TROTTOIRS_HERRINGBONE_ENTRANCE` (`T21_Trottoir_Herringbone_Entrance`, beige since 22-10), kerb trottoirs `GROUND_TROTTOIRS_KERB_ENTRANCE` (`T22_Trottoir_Kerb_Entrance`);
  - commerce terrace `GROUND_TERRACOTTA` (`T03_Terracotta_Herringbone`), the dark squares in that terrace `GROUND_COMMERCE_TERRACE_SQUARES` (`T25_Commerce_Terrace_Squares`), the strip between the commerces and D-1/D-2 `GROUND_COMMERCE_STRIP_BEIGE` (`T26_Commerce_Strip_Beige`), the trottoirs along the commerces and the restaurant plaza to the road `GROUND_TROTTOIRS_COMMERCES_RESTAURANT` (`T20_Pavers_Sidewalk_Beige`, beige as the strip since 22-10), restaurant terrace and plaza `GROUND_TERRACE` (`T02_Pavers_Herringbone_Light`), playground `GROUND_COURT_TILE` (`T18_Tile_Ardesia_Beige`), villa entrance paths `GROUND_PAVERS_BEIGE_T1_T2` (`T17_Pavers_Beige_Herringbone`, with Tranche 2's paths), rear terraces `DUPLEX_REAR_TERRACES` (`M09_Terrace_Stone`).
- Beige paver and grey trottoir textures are in `data/textures/` of the repository if you want them (`TEX_PAVERS_BEIGE_HERRINGBONE.jpg`, and the grey `TEX_PAVERS_SIDEWALK_GREY.jpg` the trottoirs had before 22-10).
- `T18_Tile_Ardesia_Beige`: the ground of the playground area by the pool (AZUVI Ardesia Nature type, 30 x 60).
  In D5 it can be swapped for the real product's texture if you have it.
- `T19_Tile_Jade_Green`: the two pools (La Platera Jade type, 30 x 60).
- Duplexes (villa N°09): `D13_Render_Villa_Beige` walls, `D14_Stone_Surround_Taupe` window and door surrounds,
  `D15_Stone_Ledge_Grey` and `D16_Stone_Band_Ochre` cornice, `D17_Frame_Aluminium_Quartz` aluminium frames (quartz, a light sand grey, since 22-10) (windows, balcony and garden sliding doors), `D18_Stone_Cladding_Beige`
  front garden walls with `D19_Coping_Beige_Stone`, `M03_Timber_Pergola` pergolas and railings.

## Tranche 2: villas type B (21-10)
The type B blocks of the plan de masse 31-05-13 west of the tranche: 33 villas (the northern block 21, the southern
block 12), villa type B of `5-VILLA_TYPE_B.DWG` with its own pool, in the finishes of the duplexes above
(same render, surrounds, cornice, beige aluminium, pergolas, jade pool tiles). Everything of Tranche 2 is in its own
collections (`T2_01_GROUND`, `T2_02_VILLAS`, `T2_03_LANDSCAPE`, `T2_04_TREES_PALMS`) and objects, and its ground in
its own materials, so it can be finished apart from Tranche 1:
- villas `T2_VILLA_B01` to `T2_VILLA_B33` (one mesh shared, the mirrored ones another);
- the Centre d'entretien and the Office `T2_BUILDINGS_CENTRE_ENTRETIEN_OFFICE`, the bay lines `T2_ROAD_PAINT_PARKING`,
  the stair between the two blocks with its two square fountains `T2_STAIR_BETWEEN_BLOCKS` (22-10).
  Since 22-10 the two tranches' ground is one object per surface, with one material each, in this package:
  streets and bays `GROUND_ROADS_BEIGE_T1_T2` (the entrance zone keeps `GROUND_ROADS_BEIGE_ENTRANCE`),
  beige paths `GROUND_PAVERS_BEIGE_T1_T2` (`T17_Pavers_Beige_Herringbone`), kerbs and the villas'
  pavements `GROUND_KERBS_T1_T2` (`Kerb_Concrete`), gardens, verges and lawns `GROUND_LAWN_T1_T2` (`T03_Lawn`):
  change one in D5 and both tranches change. Since 23-10 Tranche 2's pavements (trottoirs) are apart from the
  roads: `GROUND_TROTTOIRS_T2` in their own material `T27_Trottoirs_Grey` (grey pavers), to finish on their own.
  Delete the old model in D5 before importing this one;
- garden walls `T2_WALLS_GARDENS`, street front walls with gate pillars and gates `T2_WALLS_FRONT_GATES`, palm pits `T2_TREE_PITS`,
  (the lawn by Tranche 1's limit and the verges are in `GROUND_LAWN_T1_T2`).
Cameras `T2_CAM_01` to `T2_CAM_07`.

## Roads in beige pavers (22-10)
Every road and the parking bays (both tranches, the entrance zone too) are in the plaza's beige herringbone pavers,
the very same material `T17_Pavers_Beige_Herringbone` (0.80 m tile): no asphalt is left. Change that one material in
D5 and the roads and paths change together (Tranche 2's pavements are `T27_Trottoirs_Grey` since 23-10).
Since 23-10 the road objects are `GROUND_ROADS_BEIGE_T1_T2` and `GROUND_ROADS_BEIGE_ENTRANCE`, cut on a 3 m grid
(they had faces of hundreds of m2, which D5 showed black from afar). **Delete the old model in D5 completely
before importing** (don't replace or update it): D5 would keep the old dark road material on the old objects.

## Villas type C and the SPA (22-10)
- The villas type C of the plan de masse (the block south-west of the southern block): `T2_VILLA_C01` to
  `T2_VILLA_C12` (the plan's 13th, in the corner on the south road, left out on 23-10: that corner is street), villa type C of `PLAN_VILLA_TYPE_C.dwg` (battered towers, the portal tower with its
  arch and studded door, the outside stair, its pool), in the same finishes as the other villas; their gardens,
  walls and gates are in the Tranche 2 objects above.
- The SPA (collection `T2_05_SPA`, objects `T2_SPA_<material>`), since 23-10 from its permit drawing
  `7-SPA-A0-1.pdf` (it replaces the design suggestion): single storey (floor +0.20, roof terrace +4.20, parapet
  +5.20), the main block 37.6 x 13.65 m with its two glazed walls on the pools (louvred transoms), the indoor pool
  behind the southern one, two pairs of tall windows at the back; the centre block standing proud to +7.20 with the
  villas' cornice, horns, six niches and the studded door in its taupe alfiz; the roof terrace with the domes of the
  two bassin halls, four cantilever parasols and loungers, reached by the outside stair past axis 8; the two outdoor
  pools along the front, `M10_Pool_Water`, travertine `T06_Travertine_Deck`.
- Cameras `T2_CAM_08_VILLA_C_FRONT`, `T2_CAM_09_TYPE_C_AERIAL`, `T2_CAM_10_SPA_ENTRANCE`, `T2_CAM_11_SPA_POOLS`.
- Since 24-10 the villas type C's outside stair is solid down to the ground, and the SPA's landing is closed
  against the main block's parapet. The SPA is 0.40 m lower, its paving level with the pavement on its entrance
  path, the lot's edge a stone plinth down to the street where it runs lower (no gap under the paving) and a low
  wall where the street runs higher. Since 24-10 too the garden walls along the stair between the blocks and
  along the lane parallel to it (between the two rows of villas type C and on between the villas type B) are
  clad in stone (`D18_Stone_Cladding_Beige`, in `T2_WALLS_GARDENS`), no other wall (since 26-10 the low walls on
  the streets by the gates are in render too), and the horns are gone from all the houses (Tranche 1's duplexes,
  villas B, C and A).
- In the corner road by C-10 to C-12, three islands of grey pavement `GROUND_TROTTOIRS_T2` as the plan's two in
  front of C-08 and C-09 (23-10), and the 0.40 m pavement along the fences of C-11 and C-12 (a gap before).
Delete the old model in D5 before importing this one.

## Tranche 3: the hotel and the villas type A (23-10)
West of the SPA and the type C block, from the plan de masse 31-05-13 (collections `T3_01_GROUND`, `T3_02_VILLAS`,
`T3_03_LANDSCAPE`, `T3_04_TREES_PALMS`, `T3_05_HOTEL`):
- villas type A `T3_VILLA_A01` to `T3_VILLA_A04` (one mesh shared), since 24-10 from `VILLA_TYPE_A.dwg`: four
  battered towers with their niches and cornice round the central band and its patio, the entrance block
  +6.20 with the studded portal `D02_Door_Wood_Dark` on the entrance terrace, the chimney, the outside stair to
  the roof terrace, the pool `T19_Tile_Jade_Green` under `M10_Pool_Water`; walls `T3_WALLS_GARDENS`,
  `T3_WALLS_FRONT_GATES` on street 7;
- the hotel, **a design proposal** (no plan received), objects `T3_HOTEL_<material>`. Since 24-10 (second review)
  both buildings share one design at two storeys and one height (roofs +7.80 over each half's floor): on the garden
  the SPA's louvred glazing on the stone terrace, mashrabiya screens `D01_Mashrabiya_Wood` and stone balconies
  upstairs, a centre block with the SPA's studded door; on the parking, the principal front, a pointed horseshoe
  window in each bay in a taupe alfiz `D14_Stone_Surround_Taupe` with green zellige `T19_Tile_Jade_Green`, a zellige
  frieze, cedar mashrabiya oriels and stone balconies, bronze lanterns on the pilasters, the grand entrance in each
  half (horseshoe arch in its zellige alfiz, studded doors `D02_Door_Wood_Dark`); domed towers, domes, parasols
  and pergolas on the roofs; the main building's gate block on the Voie Publique; the gate pavilion on the
  crossing is new, standing over both (monumental arches, corner turrets, drum and dome to about +14, fountain);
  the water garden: the long basin in three basins over two weirs and its arm, `T19_Tile_Jade_Green` under
  `M10_Pool_Water` (set it to D5 Water), travertine decks `T06_Travertine_Deck`, loungers, parasols, the palm
  promenade `T17_Pavers_Beige_Herringbone` from the garden gate on street 7; lawns `T03_Lawn` (as T2's);
- the ground joins the objects above: streets and parking `GROUND_ROADS_BEIGE_T1_T2`, pavements
  `GROUND_TROTTOIRS_T2` (with the hotel's trottoir along its parking front and round the gate block, since 24-10),
  kerbs `GROUND_KERBS_T1_T2`, paths `GROUND_PAVERS_BEIGE_T1_T2`, gardens `GROUND_LAWN_T1_T2`; the parking along the
  hotel is a paved forecourt (no bay lines since the trottoir), Tranche 2's kerbs and island left in that street
  are gone.
Cameras `T3_CAM_01_AERIAL` to `T3_CAM_07_VILLA_A_POOL`. Since 26-10 the hotel has no domes (they read as a
mosque): square roof lanterns with mashrabiya windows, flat towers, a lantern over the pavilion.

## The pool park on the cliff (26-10)
The last part of the site, west of Tranche 3 over the Atlantic, **a design proposal on the plan de masse's layout**
(the plan's drawing placed by its boundary marks), on **one level**: collections `T4_01_GROUND`, `T4_02_POOLS`,
`T4_03_LANDSCAPE`, `T4_04_TREES_PALMS`, objects `T4_GROUND_<material>` and `T4_POOLS_<material>`. The street along
the northern boundary `t2_road` / `t2_pave`, the sinuous lagoon pool with its palm island, timber bridge and sun
shelf (`M10_Pool_Water`, set it to D5 Water), a jacuzzi, the round kiosk (timber pergola and
stone bar) on its plaza, decks `T06_Travertine_Deck`, lawn `T03_Lawn`, stone parapet `M04_Stone_Rubble` on the
cliff. Since the second 26-10 review the passage between the villas type A goes on to the pool (its paving, flush:
the passage rises to the park's level, no steps), its southern side planted like its northern strip, the bridge
is level with the pool's deck, and the children's pool is gone. Cameras `T4_CAM_01_POOL_PARK_AERIAL`, `T4_CAM_02_POOL_TO_OCEAN`, `T4_CAM_03_KIOSK`. **Delete the old model in
D5 completely before importing.**

## The landscape (26-10)
New plant library (`21_plants.py`): detailed date palms, Washingtonias and olive trees (not in the NO_PALMS_TREES
file: place D5's own palms there, or use the FULL file / the GLB), fountain grass, agaves, lavender and terracotta
jars (in both files, `*_03_LANDSCAPE`). Gravel beds edged in stone along the villas' garden walls
(`GARDEN_BEDS_T1`, `T2_GARDEN_BEDS`, `T3_GARDEN_BEDS`, material `V2_Gravel_Mulch`), one smaller olive tree per
garden, raised stone planters on the big stair (`T2_STAIR_BETWEEN_BLOCKS`), beds and planters in the pool park.
**Delete the old model in D5 completely before importing.**

## The children's playground (27-10)
On the tiled court by the restaurant: object `KIDS_PARK_<material>` in `08_PLAYGROUND` (play structure, slides,
swings, roundabout, seesaw, sandpit, spring riders, benches, shade sails), on coloured rubber surfaces
(`P09`-`P12_EPDM_*`), its paints `P01`-`P08`. Tranche 1's palms that stood outside the villas' garden walls are
inside the gardens now. **Delete the old model in D5 completely before importing.**
"""


# client 22-10: the two tranches' streets (and pavements, kerbs, lawns) in one object each, with one material,
# so D5 can neither show them apart nor give them two material instances
JOIN = {"GROUND_ROADS_BEIGE_T1_T2": ("GROUND_ROADS_VILLAS_asphalt", "T2_GROUND_ROADS_t2_road", "T2_GROUND_PARKING_t2_parking",
                                     "T3_GROUND_ROADS_t2_road", "T3_GROUND_PARKING_t2_parking", "T4_GROUND_t2_road"),
        "GROUND_PAVERS_BEIGE_T1_T2": ("DUPLEX_ENTRANCE_PATHS_pave_beige", "T2_GROUND_ENTRANCE_PATHS_t2_path", "T3_GROUND_PATHS_t2_path",
                                      "T4_GROUND_t2_path"),
        "GROUND_KERBS_T1_T2": ("GROUND_PAVEMENTS_VILLAS_kerb_paving", "T2_GROUND_KERBS_t2_kerb", "T3_GROUND_KERBS_t2_kerb"),
        "GROUND_LAWN_T1_T2": ("GROUND_LAWN_lawn", "T2_GROUND_GARDENS_LAWN_t2_lawn", "T2_GROUND_VERGES_t2_verge",
                              "T2_GROUND_LAWN_BY_TRANCHE_1_t2_verge", "T3_GROUND_GARDENS_LAWN_t2_lawn", "T3_GROUND_VERGES_t2_verge"),
        "GROUND_TROTTOIRS_T2": ("T2_GROUND_PAVEMENTS_t2_pave", "T3_GROUND_PAVEMENTS_t2_pave", "T4_GROUND_t2_pave")}


def join_ground():
    for name, parts in JOIN.items():
        obs = [bpy.data.objects[p] for p in parts if bpy.data.objects.get(p)]
        if len(obs) < 2:
            continue
        for o in obs:
            if o.data.users > 1:
                o.data = o.data.copy()
        with bpy.context.temp_override(active_object=obs[0], selected_editable_objects=obs, selected_objects=obs):
            bpy.ops.object.join()
        obs[0].name = name
        obs[0].data.name = name
        print("JOINED", name, [m.name for m in obs[0].data.materials])
    for old, name in RENAME.items():
        o = bpy.data.objects.get(old)
        if o is not None:
            o.name = o.data.name = name


# client 23-10: the roads came out black in D5 from afar and grey close to, though in T17 like the pavements.
# Their meshes had triangles up to 1700 m2 (the plan's long straight kerbs): D5 lights such faces badly, and
# it kept the old asphalt look on the objects of the same name. New names, and the faces cut on a 3 m grid:
# the very same surface and material, in pieces of 3 m at most (the cuts split the faces where they lie,
# their UVs interpolated exactly)
RENAME = {"GROUND_ROADS_ENTRANCE_asphalt_ent": "GROUND_ROADS_BEIGE_ENTRANCE",
          "T2_GROUND_PAVEMENTS_t2_pave": "GROUND_TROTTOIRS_T2"}       # client 23-10: the pavements apart from the roads
FINE = ("GROUND_ROADS_BEIGE_T1_T2", "GROUND_ROADS_BEIGE_ENTRANCE", "GROUND_TROTTOIRS_T2",
        "T3_HOTEL_t2_lawn", "T3_HOTEL_pave_beige", "T3_HOTEL_deck_stone",     # the hotel's long lawns, promenade, decks
        "T4_GROUND_deck_stone", "T4_GROUND_lawn")                             # the pool park's decks and lawn


def grid_cut(names, cell=3.0):
    for name in names:
        o = bpy.data.objects.get(name)
        if o is None:
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        n0 = len(bm.faces)
        for axis in (0, 1):
            vals = [v.co[axis] for v in bm.verts]
            c = (math.floor(min(vals) / cell) + 1) * cell
            while c < max(vals):
                co, no = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
                co[axis], no[axis] = c, 1.0
                bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no)
                c += cell
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.to_mesh(o.data)
        o.data.update()
        print("FINE", name, n0, "->", len(bm.faces), "faces, largest", round(max(f.calc_area() for f in bm.faces), 2), "m2")
        bm.free()


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
    join_ground()
    grid_cut(FINE)
    export(os.path.join(OUT, "Mirleft_Tranche_1_D5_FULL.fbx"))
    for cn in ("06_TREES_PALMS", "T2_04_TREES_PALMS", "T3_04_TREES_PALMS", "T4_04_TREES_PALMS"):
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
