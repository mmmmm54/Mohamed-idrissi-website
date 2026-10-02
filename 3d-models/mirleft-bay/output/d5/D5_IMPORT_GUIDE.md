# D5 import guide: Mirleft Bay

Blender stays the source of truth for geometry. D5 adds realistic vegetation, people, cars, atmosphere and fast rendering.

## Files
| File | Use |
|---|---|
| `Mirleft_Bay_D5.fbx` (16 MB) | **Import this into D5**: the complete scene (buildings, palms, pink trees, olives, cars, parking, water, terrain, 11 cameras) |
| `Mirleft_Bay_D5.blend` | The same scene, if you use D5's Blender sync plugin instead of FBX |

The file contains about 2.4 million triangles in 2939 objects. Everything is included, so in D5 you only fix small things. The one thing left out is the close-up grass tufts (4 million triangles): put D5 grass on the `T03_Lawn` faces where the camera is close. Leaf textures (palm fans, olive and pink blossom cards) are embedded. If a leaf shows as a square card in D5, turn on the material's **opacity / alpha** using the same texture.

## Steps
1. D5 ▸ **Import model** ▸ `Mirleft_Bay_D5.fbx`. Units: metres (scale 1). If the site arrives 100× too big or small, re-import with the unit set to metre.
2. The ocean plane is 80 km wide: give it a D5 **water** material (sea preset), or hide it and use D5's own ocean.
3. Re-assign materials with **D5_MATERIAL_MAPPING.md**. Names are kept (M01_Render_Sand, M04_Stone_Rubble…). The UVs are in metres, so set D5 texture size to the physical tile size.
4. People (and, if you like, swap some palms or cars for D5 library assets): **D5_ASSET_LIST.md**.
5. Light: **D5_LIGHTING_GUIDE.md** (golden hour, sun direction for the site).
6. Cameras: the 11 shots come in with the FBX (SH01…SH11); see **D5_CAMERA_GUIDE.md**. Set D5's output to **1080 × 1920 (9:16)**.

## What stays in Blender
Architecture, site levels, water features, cameras. Any geometry change is made in Blender with `blender/20_pipeline.py`, then re-exported with `blender/19_export_package.py`.
