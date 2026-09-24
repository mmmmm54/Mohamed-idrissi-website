# Imara Teal R+6 — 3D model

Corner apartment building (ground floor + mezzanine, 6 floors), modelled in Blender 4.2
from the floor plan *PLAN 1er, 2eme, 3eme et 4eme ETAGES*, the two elevations
(*FAÇADE PRINCIPALE*, *FAÇADE LATERAL DROITE*) and the two colour renders.

| File | What it is |
|---|---|
| `Imara_Teal_R6_HQ.glb` | **For After Effects**: lighting and shadows baked into the textures, looks like the previews in any viewer. |
| `Imara_Teal_R6.glb` | Plain PBR model with tiled textures, for engines with their own lighting (Twinmotion, Lumion, Unreal, Blender). |
| `Imara_Teal_R6.blend` | Blender project: model + street, sun, sky and the preview cameras. |
| `build_imara.py` | Script that generates the model. Change a number, re-run, get a new model. |
| `bake_hq.py` | Bakes the lighting into textures and exports `Imara_Teal_R6_HQ.glb`. |
| `textures/` | The procedural textures (panels, stone, wood, black marble, shutters…). |
| `previews/` | Renders, plus drawing vs model comparisons. |

Rebuild: `python build_imara.py . --render` with the `bpy` 4.2 module (drop `--render` to skip the previews).

## Measurements (metres)

Taken from the plan's dimension lines; heights scaled from the elevations.

| | |
|---|---|
| Upper floors envelope | **17.25 × 24.00** |
| Ground floor footprint | **15.75 × 22.50** |
| Encorbellement (both streets) | **1.50** |
| Ground floor + mezzanine | 5.50 |
| Floor to floor, floors 1–6 | 3.20 |
| Roof slab | +24.70 |
| White parapet / teal cap | +25.90 / +26.20 |
| Stair house (X 3.60–6.80, Y 11.20–16.60) | +27.45 |
| Windows (bedrooms, salon) | 2.50 wide, sill 0.90, head 2.25 |
| Balcony glass railing | 1.05 high |

Main street bays, left to right: 2.02 (loggia) · 4.31 (bedroom, projecting) · 4.18 (balcony) ·
3.45 (bedroom, projecting) · 3.29 (corner balcony) = 17.25.

Side street bays, front to back: 1.50 (overhang) · 7.02 (two bedrooms) · 5.74 (balcony 1.90) ·
3.50 (salon marocain) · 5.24 (bedroom balconies) · 1.00 (teal band) = 24.00.

Axes in Blender: X along the main street, Y back along the side street, Z up. Origin is the ground-floor
corner at the left party wall. The GLB is Y-up as glTF requires.

## Finishes (from the renders)

- Teal petrol frames: floor edges at floors 2 and 3, the frame around floor 5, the back band and the roof cap on the side street
- Light grey-beige facade panels with joints
- Dark brown stone cladding (left column and salon column floors 1–3, inside the teal frame on floor 5)
- Wood cladding on the recessed balconies
- White render, slab edges and vertical fins
- Frameless glass balconies with a steel top rail, black aluminium windows
- Black marble ground floor with white veins, metal roller shutters, mezzanine glazing
- Plants on balconies and roof planters, downlights under the soffits

## Assumptions

- Where the black-and-white elevations and the colour renders disagree, the renders win on colour
  (pink → beige panels, grey → teal, stone → brown stone). The stone column is straight as in the renders,
  not tapered as in the elevation.
- The white slats drawn on floor 6 are not in the renders, so they are left out.
- The courtyard on the plan is filled in: the back and the left side are full-height blind walls
  and the roof is one flat slab with the stair house, as on the site photos.
- Floor heights (5.50 / 3.20) are scaled off the elevations, not written on the plan. If the permit
  drawings give exact levels, change `H_RDC` and `H_FL` at the top of `build_imara.py` and re-run.

## After Effects: use `Imara_Teal_R6_HQ.glb`

`Imara_Teal_R6_HQ.glb` is the version made for After Effects and other real-time viewers.
The Cycles lighting (sun, sky, soft shadows, bounce light, downlights) is **baked into the
textures** and the materials are unlit (`KHR_materials_unlit`), so the building looks the same
as the previews whatever lights the viewer has. Glass and glass railings stay as real
reflective / transparent materials. Hidden faces (wall insides) are removed.
`previews/hq_glb_*.jpg` show the GLB in a plain viewer with no lights of its own.

1. File ▸ Import ▸ File ▸ `Imara_Teal_R6_HQ.glb`, drag it into a composition.
2. Composition Settings ▸ 3D Renderer ▸ **Advanced 3D**.
3. Lights: an **Environment** light only (Layer ▸ New ▸ Light ▸ Environment). It lights the glass.
   No directional or spot light with shadows: the shadows are already in the textures.
4. Preview at Full resolution with Draft 3D off; render with Quality **Best**.

The sun direction is fixed by the bake. For a different time of day or new materials,
change `setup_scene()` / `MAT_DEF` in `build_imara.py`, re-run it, then run
`python bake_hq.py . 48 72` (samples, texels per metre; about 80 min on 4 CPU cores).
It also writes the 16-bit baked textures to `baked/` and `Imara_Teal_R6_HQ.blend`,
which are too big for git and are ignored.

`Imara_Teal_R6.glb` is the plain PBR version (tiled textures, no baked light) for
engines that do their own lighting (Twinmotion, Lumion, Unreal, Blender).
