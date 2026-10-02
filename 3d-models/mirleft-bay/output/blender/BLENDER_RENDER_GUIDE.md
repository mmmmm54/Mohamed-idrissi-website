# Blender render guide — Mirleft Bay (Blender only)

## Open the final scene (no D5 needed)
1. On github.com/mmmmm54/3D-MODELS: **Code ▸ Download ZIP**, then unzip. Keep the `mirleft-bay` folder whole: the scene finds its textures in `mirleft-bay/assets/textures/`.
2. Open `mirleft-bay/scenes/Mirleft_Bay_Scene.blend` in Blender 4.2 or newer.
3. If a surface shows pink (missing texture): **File ▸ External Data ▸ Find Missing Files** and pick the `mirleft-bay/assets/textures` folder.
4. Choose a camera in the `13_CAMERAS` collection (select it, then Ctrl+Numpad 0), then press **F12**. The 11 shots are set up already: 9:16, golden hour, haze, depth of field on ground-level shots, plus bloom, warm/cool grade and vignette in the compositor.
5. Final quality: Render Properties ▸ Device = GPU (Preferences ▸ System ▸ CUDA/OptiX), samples 256 (already set).

What is in the scene:
- **Every building:** 17 duplex pairs, 33 villa B, 13 villa C, 4 villa A, the kasbah reception, the club and the Pavillon.
- **Roads and parking:** roads, parking with cars, canals, hotel T-water, pools and the lake.
- **Planting:** Washingtonia and date palms, olives, pink flowering trees mixed with green shade trees, stone garden walls.
- **Textures:** the client's Poly Haven CC0 4K maps (plaster, stone, wood, pavers, tiles, ground, beach), keeping the colours of the site photos.
- **Left out:** only the 300k close-up grass tufts (the file would be 240 MB). `20_pipeline.py` adds them back.

---

# Rebuild from scripts (MODE B: Blender → Higgsfield)

## Rebuild the scene
```
cd blender
python 20_pipeline.py --until final --validate --render all --samples 128
```
Python with the `bpy` 4.2 module, or `blender -b -P 20_pipeline.py -- --until final ...`.
Everything is rebuilt from the scripts, with deterministic names and seeds. Checkpoints are written to `output/checkpoints/`.

| Stage | Script(s) | Checkpoint |
|---|---|---|
| Materials | 07_build_materials.py | — |
| Terrain + ocean | 03_build_terrain.py | — |
| Site (paving, blocks, pools, lake) | 02_build_site.py | — |
| Architecture (kit + all types + placement) | 04_build_architecture.py | checkpoint_02_graybox.blend |
| Landscape | 09_build_landscape.py | checkpoint_07_landscape.blend |
| Lighting presets | 14_build_lighting.py | (in every checkpoint) |
| Cameras + hero-zone grass + haze | 15_build_cameras.py, 20_pipeline.py | checkpoint_09_cameras.blend |
| Final | — | checkpoint_10_final.blend |
| Validation | 18_validate_scene.py | output/validation/ |

The brief's other script slots are covered here: openings and details live in the architecture kit (`Kit.opening`, `niches`, `pergola`, `lattice`). Furniture and props are kept to the jacuzzis, because the architecture is the hero. People and vehicles are left to the Higgsfield shots.

## Render settings (BLENDER_RENDER_SETTINGS)
| Setting | Preview | Final |
|---|---|---|
| Engine | Cycles CPU | Cycles (GPU on your PC: Preferences ▸ System ▸ CUDA/OptiX) |
| Resolution | 1080 × 1920 (9:16), 50 % for checks | 1080 × 1920, or 2160 × 3840 for 4K |
| Samples | 16-48 + OpenImageDenoise | 128-256 + denoise |
| Colour | AgX, Medium High Contrast | same |
| Haze | Mist pass × 0.55, masked off the sky (compositor) | same |

## Lighting presets (BLENDER_LIGHTING_GUIDE)
Sun positions are computed for 29.553 N, 10.060 W on 2026-10-15 (`14_build_lighting.py`):

| Preset | Local time | Sun az / el |
|---|---|---|
| LIGHTING_01_DAYLIGHT | 13:30 | 182° / 52° |
| LIGHTING_02_MORNING | 09:30 | 114° / 22° |
| **LIGHTING_03_GOLDEN_HOUR (master)** | 18:20 | 257° / 10° |
| LIGHTING_04_SUNSET | 19:02 | 260° / 1° |
| LIGHTING_05_BLUE_HOUR | 19:30 | 263° / −5° |
| LIGHTING_06_NIGHT | 22:30 | moon-less, interior lamps only |

To switch preset in Blender's Python console: `exec(bpy.data.texts['LIGHTING_PRESETS.txt'].as_string())`, then load the module and call `apply("LIGHTING_04_SUNSET")`. The easier route is to change `MASTER` in `14_build_lighting.py` and re-run the pipeline.

## Cameras (BLENDER_CAMERA_GUIDE)
11 cameras in collection `13_CAMERAS`, all 9:16 with vertical sensor fit. Each one carries custom properties `purpose` and `higgsfield`. See `output/higgsfield/02_SHOT_LIST.md`.
