# Blender render guide — Mirleft Bay (MODE B: Blender → Higgsfield)

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
