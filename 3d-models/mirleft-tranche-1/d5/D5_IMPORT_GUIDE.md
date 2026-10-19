# D5 import guide: Mirleft 1er TRANCHE

| File | Contents | Use it when |
|---|---|---|
| `Mirleft_Tranche_1_D5_FULL.fbx` | Everything: duplexes, restaurant, commerces, pool court, ground, walls, stairs, furniture, trees, palms and plants, and the 13 cameras | You want everything placed already |
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
  - by the villas: roads `GROUND_ROADS_VILLAS` (`M11_Asphalt`), lanes `GROUND_LANES_VILLAS` (`T01_Pavers_Herringbone_Charcoal`), pavements `GROUND_PAVEMENTS_VILLAS` (`Kerb_Concrete`);
  - in the entrance zone: roads `GROUND_ROADS_ENTRANCE` (`M11_Asphalt_Entrance`), herringbone trottoirs `GROUND_TROTTOIRS_HERRINGBONE_ENTRANCE` (`T21_Trottoir_Herringbone_Entrance`), kerb trottoirs `GROUND_TROTTOIRS_KERB_ENTRANCE` (`T22_Trottoir_Kerb_Entrance`);
  - round the commerces `GROUND_COMMERCES_SURROUND` (`T02_Pavers_Herringbone_Light`, as the plaza), the strip between the commerces and D-1/D-2 `GROUND_COMMERCE_STRIP_BEIGE` (`T17_Pavers_Beige_Herringbone`), restaurant terrace and plaza `GROUND_TERRACE` (`T02_Pavers_Herringbone_Light`), playground `GROUND_COURT_TILE` (`T18_Tile_Ardesia_Beige`), villa entrance paths and rear terraces `DUPLEX_REAR_TERRACES_ENTRANCES`.
- Beige paver and grey trottoir textures are in `data/textures/` of the repository if you want them (`TEX_PAVERS_BEIGE_HERRINGBONE.jpg`, `TEX_PAVERS_SIDEWALK_GREY.jpg`).
- `T18_Tile_Ardesia_Beige`: the ground of the playground area by the pool (AZUVI Ardesia Nature type, 30 x 60).
  In D5 it can be swapped for the real product's texture if you have it.
- `T19_Tile_Jade_Green`: the two pools (La Platera Jade type, 30 x 60).
- Duplexes (villa N°09): `D13_Render_Villa_Beige` walls, `D14_Stone_Surround_Taupe` window and door surrounds,
  `D15_Stone_Ledge_Grey` and `D16_Stone_Band_Ochre` cornice, `D17_Frame_Cream` frames, `D18_Stone_Cladding_Beige`
  front garden walls with `D19_Coping_Beige_Stone`, `M03_Timber_Pergola` pergolas and railings.
