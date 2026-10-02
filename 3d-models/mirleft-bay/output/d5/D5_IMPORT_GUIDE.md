# D5 import guide: Mirleft Bay

Blender stays the source of truth for geometry. D5 adds realistic vegetation, people, cars, atmosphere and fast rendering.

## Files
| File | Use |
|---|---|
| `Mirleft_Bay_D5.fbx` (13 MB) | **Import this into D5**: architecture, site, water, terrain, 11 cameras |
| `Mirleft_Bay_D5.blend` | The same scene, if you use D5's Blender sync plugin instead of FBX |

The file contains about 834k triangles in 1235 objects. All 88 buildings are real geometry, and the procedural palms, cars and grass have been removed (D5's library replaces them).

## Steps
1. D5 ▸ **Import model** ▸ `Mirleft_Bay_D5.fbx`. Units: metres (scale 1). If the site arrives 100× too big or small, re-import with the unit set to metre.
2. The ocean plane is 80 km wide: give it a D5 **water** material (sea preset), or hide it and use D5's own ocean.
3. Re-assign materials with **D5_MATERIAL_MAPPING.md**. Names are kept (M01_Render_Sand, M04_Stone_Rubble…). The UVs are in metres, so set D5 texture size to the physical tile size.
4. Vegetation, people and cars: follow **D5_ASSET_LIST.md**.
5. Light: **D5_LIGHTING_GUIDE.md** (golden hour, sun direction for the site).
6. Cameras: the 11 shots come in with the FBX (SH01…SH11); see **D5_CAMERA_GUIDE.md**. Set D5's output to **1080 × 1920 (9:16)**.

## What stays in Blender
Architecture, site levels, water features, cameras. Any geometry change is made in Blender with `blender/20_pipeline.py`, then re-exported with `blender/19_export_package.py`.
