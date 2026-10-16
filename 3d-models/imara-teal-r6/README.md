# Imara Teal R+6 — 3D model

Corner apartment building in Berkane (basement parking, ground floor + mezzanine, 6 floors), modelled in
Blender 4.2 from the floor plan *PLAN 1er, 2eme, 3eme et 4eme ETAGES*, the two elevations
(*FAÇADE PRINCIPALE*, *FAÇADE LATERAL DROITE*), the two colour renders and the site photo.
The model now has its inside: the plan of every floor (1 to 6), the ground-floor entrance lobby, and a
basement parking with its ramp from the garage bay on the main street (17-10).

| File | What it is |
|---|---|
| `Imara_Teal_R6.blend` | Blender project: the building inside and out, street, sun, sky, room lights, the preview cameras. One collection per level. |
| `Imara_Teal_R6.glb` | Plain PBR model with tiled textures, every level (Twinmotion, Lumion, Unreal, Blender). |
| `d5/` | **D5 Render** package: `Imara_Teal_R6_D5.fbx` (textures embedded), `textures/`, `D5_IMPORT_GUIDE.md`. |
| `Imara_Teal_R6_HQ.glb` | For After Effects, lighting baked into the textures. **Still the exterior-only version of 24-09**: run `bake_hq.py` again to refresh it. |
| `build_imara.py` | Builds the envelope and the scene. Change a number, re-run, get a new model. |
| `imara_interior.py` | The inside: floor plans 1-6, lobby, basement parking, ramp, street entrance. |
| `export_d5.py` | Writes the `d5/` package from the .blend. |
| `bake_hq.py` | Bakes the lighting into textures and exports `Imara_Teal_R6_HQ.glb`. |
| `textures/` | The procedural textures (panels, stone, wood, marble, floor tiles, parquet, ramp concrete…). |
| `previews/` | Renders, plus drawing vs model comparisons. |

Rebuild: `python build_imara.py . --render` with the `bpy` 4.2 module (drop `--render` to skip the previews;
`--only plan_etage_type,parking_allee` renders just those), then `python export_d5.py .` for D5.

## Levels and 3D plans

Every level is its own collection: `Niveau_-1_Sous-sol`, `Niveau_0_RDC`, `Niveau_1` … `Niveau_6`, `Toiture`
(and `Site_Context` for the street). To see a floor as a 3D plan, hide the collections above it. The
ceiling lights of a floor belong to the level above, so they go away with it.
`Plan3D_Niveau_3` is the 3rd floor cut at 1.40 m, the way 3D floor plans are drawn. It is excluded from the
view layer: tick it on, and hide `Niveau_3` and the levels above, to get `previews/plan_etage_type.jpg`
and `axo_etage_type.jpg`.

## The floors (1 to 6, from the plan)

Three flats per floor round the stair, the lift and the landing (floors 5 and 6 repeat the plan; its
courtyard note covers them):

| Flat | Where | Rooms |
|---|---|---|
| 106 m² (door A) | back, side street | hall, kitchen with dining room on the courtyard balcony, salon marocain (side street window), 3 bedrooms (two on the bedroom balcony, one on the courtyard), bathroom |
| 110 m² (door B) | front, side street | hall, salon marocain on the 1.90 balcony, kitchen + dining room on the 1.30 balcony, 3 bedrooms (front bedroom with its own bathroom and door to the corner balcony), 2 bathrooms |
| 118 m² (door C) | left, main street | hall, salon marocain and kitchen + dining room on the main-street balcony, 4 bedrooms (suite with bathroom on the courtyard, front bedroom, twin bedroom on the loggia), 2 bathrooms |

- Walls, doors (with their swing) and sliding doors as drawn. Columns on the plan's red grid.
- **Finishes:** porcelain 60 × 60 in the halls, salons and kitchens; oak parquet in the bedrooms; tiles in the bathrooms; outdoor tiles on the balconies and the courtyard; granite on the stair and the landing.
- **Furniture:** set out as the plan shows it: beds, salon marocain benches with the mida, dining tables, kitchens (worktop, sink, hob, hood, fridge), showers, WC, vanities, wardrobes.
- **Stair:** dog-leg, 18 risers of 17.8 cm per floor (treads 28 cm), granite with a steel handrail. The ground floor (5.50 m) takes 32 risers in 4 flights, and the basement 14.
- **Lift:** shaft 1.50 × 1.65 m inside (the one marked on the plan), stainless doors on every level, overrun on the roof.
- **Courtyard:** on floor 1 it is a terrace over the ground floor, with the plan's *lanterneau d'aération* on it. From floor 2 up it is a light well, open to the sky, with a parapet round it on the roof.

## Basement parking (sous-sol, design)

Under the ground-floor footprint (15.75 × 22.50), floor at **-2.50**, flat slab over it with **2.20 m clear**.
The ramp starts at the garage bay the site photo shows on the main street (X 0.37-3.38).

- **Ramp:** 3.20 m wide along the left party wall, 16.6 m long, **17.1 %** with 2 m transitions at each end, so cars don't scrape. Chevron-grooved concrete, yellow/black wheel curbs, a teal band and an LED line on both walls following the slope, drains at the top and the foot.
- **Places:** 6 cars.
  - 3 bays 5.00 m deep: 2.70, 2.32 and 2.33 m wide.
  - 1 compact bay 2.50 × 4.40.
  - 2 parallel bays 5.30–5.40 × 2.20 along the back wall.
  - Plus 3 motorcycle bays, a 6-bike rack and 6 storage lockers along the front wall.
- **Circulation:** the ramp lands in a 5.3 m aisle along the back wall. A 4.7 m passage along the side street leads to the 5.5 m main aisle.
- **Structure:** the bays sit between the plan's columns, which come down unchanged.
- **Capacity limit:** with the stair-and-lift core in the middle and a 15.75 m wide plot, there is no more room. A car lift instead of the ramp would free about 4 more places.
- **Stair and lift:** both come down to the basement, through a fire lobby (SAS) with fire doors. The keep-clear hatch in front of the SAS stays free.
- **Services under the ramp:** a pump room (booster) and the water tank, about 30 m³ usable.
- **Ventilation:** air comes in through the ramp and goes out through the shaft under the *lanterneau d'aération*, with an extract duct.
- **Finishes and safety:** grey epoxy floor, white columns with a teal band and yellow/black guards, a grey dado and teal band on the walls. LED battens, exit signs, extinguishers, painted bay numbers and arrows.

## Parking entrance (design)

The garage bay of the main street becomes the parking entrance:
- a teal portal, the colour of the building's frames, projecting 0.40 m, with an LED line in its soffit;
- a wood-lined reveal and a roller door (shown open);
- a lit blue **P -1** sign on the portal head, a red/green traffic light, and a 2.10 m height bar inside;
- a darker driveway band across the sidewalk with two steel bollards, and linear lights over the ramp.

The entrance lobby beside it has a white marble floor, a wood-slat wall with a mirror and bench, the
mailboxes, pendants over the double-height space, and the lift and stair doors.

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
- The back and the left side are full-height blind walls. Since 17-10 the plan's courtyard is open: a terrace on
  floor 1 and a light well above, which the rooms on it need. `COURTYARD_OPEN = False` in `imara_interior.py`
  puts the roof slab back over it.
- Envelope adjusted to the plan where the inside needs it (17-10). From the street the facade materials,
  teal bands and fins are unchanged.
  - The loggia's stone pier is a 0.20 m front pier.
  - The main-street balcony is recessed to the dining room and the salon, wood-clad.
  - The corner balcony has one sliding door.
  - The side-street balcony steps to 1.30 m (kitchen) and 1.90 m (salon).
  - The bedroom balcony runs to the back wall, behind a thinner teal band.
  - Window glass is transparent.
- Floor heights (5.50 / 3.20) are scaled off the elevations, not written on the plan. If the permit
  drawings give exact levels, change `H_RDC` and `H_FL` at the top of `build_imara.py` and re-run.

## To confirm (17-10)

- **Spiral stair** on the landing: modelled as drawn on floors 1 to 6, without knowing where it leads.
- **Floors 5 and 6:** same plan as 1 to 4.
- **Basement:** depth (-2.50) and clear height (2.20 m). The 17.1 % ramp and the water tank are design choices, to check with the structural and plumbing engineers.
- **Ground-floor shops:** left as one open shell, since their layout isn't drawn. No mezzanine is modelled.
- **Lift:** shaft size to confirm with the lift supplier.
- **Furniture and finishes:** indicative.

## D5 Render

Use `d5/Imara_Teal_R6_D5.fbx` (see `d5/D5_IMPORT_GUIDE.md`):
- Objects are named by level (`SS_`, `RDC_`, `N1_` … `TOIT_`), so each floor can be hidden in D5.
- Swap the glass to D5 Glass and the LED materials to emissive.

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
