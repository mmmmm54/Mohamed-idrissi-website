# D5 import guide: Mirleft 1er TRANCHE

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
- garden walls `T2_WALLS_GARDENS`, street front walls with gate pillars and gates `T2_WALLS_FRONT_GATES`, palm pits `T2_TREE_PITS`,
  the lawn left by Tranche 1's limit `T2_GROUND_LAWN_BY_TRANCHE_1` (`T2_T03_Lawn_Verges`).
Cameras `T2_CAM_01` to `T2_CAM_07`.
