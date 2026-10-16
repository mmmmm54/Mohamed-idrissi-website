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
- `M10_Pool_Water` (pools, bassins, fountain) → D5 Water. The blue tiled floor and walls under it show through.
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
