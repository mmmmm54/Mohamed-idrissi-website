# Imara Teal R+6 — 3D model

Corner apartment building (ground floor + mezzanine, 6 floors), modelled in Blender 4.2
from the floor plan *PLAN 1er, 2eme, 3eme et 4eme ETAGES*, the two elevations
(*FAÇADE PRINCIPALE*, *FAÇADE LATERAL DROITE*) and the two colour renders.

| File | What it is |
|---|---|
| `Imara_Teal_R6.glb` | The model, textures embedded. Opens in any glTF viewer, Blender, SketchUp, Twinmotion, three.js. |
| `Imara_Teal_R6.blend` | Blender project: same model + street, sun, sky, 5 still cameras and an animated drone camera, set up for an After Effects render. |
| `build_imara.py` | Script that generates everything. Change a number, re-run, get a new model. |
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

## Render for After Effects

The `.blend` is already set up: Cycles, 1920 × 1080, 25 fps, frames 1–250 (10 s),
256 samples + denoise, output **PNG 16-bit RGBA sequence** to `render_AE/` next to the `.blend`.
The active camera is `Cam_Drone_Orbit`, a drone shot that circles the corner.

1. Open `Imara_Teal_R6.blend` in Blender 4.2+.
2. Edit ▸ Preferences ▸ System ▸ Cycles Render Devices: pick your GPU (CUDA / OptiX / HIP / Metal).
3. Render ▸ Render Animation (Ctrl F12). Frames land in `render_AE/imara_0001.png` …
4. After Effects: File ▸ Import ▸ File, select `imara_0001.png`, tick **PNG Sequence**, Import.
   Right-click the footage ▸ Interpret Footage ▸ Main ▸ Assume this frame rate: **25**.
5. New composition from the footage (1920 × 1080, 25 fps). Set the project to 16 bpc
   (click "8 bpc" at the bottom of the Project panel) so the 16-bit PNGs keep their detail.
6. Export with Composition ▸ Add to Adobe Media Encoder Queue: H.264 "Match Source – High bitrate"
   (or 20–40 Mbps, 2-pass) for social media, ProRes 422 HQ for a master.

For 4K set Output Properties ▸ Resolution to 3840 × 2160. To use a different move, select
another camera and press Ctrl 0 before rendering. For a white background you can mask in After Effects,
tick Render Properties ▸ Film ▸ Transparent (the PNGs keep the alpha channel).

The GLB can also go straight into After Effects 2024+ (File ▸ Import, then the Advanced 3D
renderer), but that is a real-time preview. The Cycles image sequence is what keeps
every detail: reflections, shadows, textures and the glass.
