# Mirleft: Tranche A + B (detailed), rest of the site as empty land

This is a Blender model of the south-east end of the Mirleft project, the area circled "A, B" on the plan de masse:
- the duplexes
- the administration
- the two boutique/restaurant buildings
- the club des résidents
- the courts, canal and pools
- the roads, parking and the entrance

The rest of the site is empty land, with the exact site boundary and the natural slope from the architect's contours. Everything is exterior only (no interiors).

| File | Contents |
|---|---|
| `Mirleft_Tranche_AB_PACKED.blend` | The same scene with every texture packed inside (71.7 MB): open it on any computer, no other folder needed. |
| `Mirleft_Tranche_AB_PACKED_2K.blend` | Same scene, textures packed at 2K (13.8 MiB): the light copy to send or open anywhere. |
| `Mirleft_Tranche_AB.blend` | The scene: terrain, ground surfaces, 17 duplexes, public buildings, trees and 12 cameras. Its textures are linked from `../mirleft-bay/assets/textures`, so keep the two folders side by side. |
| `renders/` | 12 views at 1920 × 1080 (see the list below). |
| `blender/01_extract_site.py` | Reads the plan de masse (DWG exploded to primitives by `tools/`) and writes `data/site.json`. |
| `blender/02_duplex.py` | The "duplex jumelée", from its permit drawings. |
| `blender/03_public.py` | The administration pavilion, the boutique/restaurant, and the hipped-roof club, kiosks and station. |
| `blender/05_build_scene.py` | Assembles everything and saves and renders the scene: `python 05_build_scene.py --render all`. |
| `blender/lib.py` | Shared helpers. It reuses the Mirleft Bay material library, plants and sun presets. |
| `tools/` | `dwg2json.mjs` (LibreDWG WASM reader) and `flatten.py` (explodes blocks to world coordinates). |

## Sources used
- **Plan de masse "pour la commission ad-hoc" (31-05-13)**
  - Used for: the layout, the site boundary and the contours. It is the plan the circled screenshot comes from.
  - Coordinates: in metres. The model origin is DWG (47900, 290320). z = altitude − 50 m.
  - Contents read from the plan:
    - the plots and the 17 duplex positions and orientations (access side to the east);
    - the pavements, plot gardens, parking bays and courts;
    - the canal, the bassins and the kids' pools;
    - the outlines of the public buildings;
    - the 12 street trees.
- **2-DUPLEX.DWG (permis de construire, duplex jumelée)**
  - Used for: the plans RDC / étage / terrasse, the three façades and the coupes A-A / B-B.
- **3-PLAN_RESTAURANT_PAVILLON.DWG**
  - Used for: the administration (accueil, bureaux, salle de réunion, cafeteria).
  - Includes: the plans, the four façades and the coupes A-A / B-B / C-C.
- **MARKET_ET_SPA.DWG (boutique, restaurant)**
  - Used for: the roof plan (six blocks), the façades and the coupes.
- **Not used for Tranche A + B:**
  - The villa A, B and C permits belong to other tranches.
  - The second plan de masse (12-10) draws a different arrangement of this end of the site.
  - The implantation survey is in another coordinate frame.

## Taken from the drawings
- **Site**
  - The boundary is the closed outline of the plan de masse, 82 139 m². That matches the title block's 8 ha 20 a 70 ca.
  - Bornes are marked at its vertices.
- **Ground of Tranche A + B**
  - It is graded on one plane fitted to the plan's contours (55 / 60 m) inside the area: 5.5 % rising to the north-east, +60.9 at the centre.
  - The empty land keeps the natural terrain of the contours (5 m interval, labelled) and blends into the platform over 25 m.
- **Duplex jumelée (17)**
  - **Footprint and levels**
    - The pair is 16.20 m long, with the joint de dilatation on the axis.
    - The RDC is 8.82 m deep, plus a 7.04 × 3.80 m wing on the access side.
    - Levels: RDC +0.20, étage +3.70, roof +7.50, acrotère +8.30, stair cages +9.80.
  - **Openings** (sizes and heights from the façades, end-wall positions from the RDC plan)
    - French windows in the wing.
    - An entrance door beside the wing; a glazed door (double on the left house, single on the right, as drawn).
    - Narrow windows on the étage.
    - A 6-leaf glazing to the rear garden.
  - **Mashrabiya panels** ('motif en bois'): in the acrotère, on the étage terraces, and as canopies over the side doors.
  - **Pergolas from the roof plan**
    - Rear: rafters every 0.47 m out to 2.45 m.
    - Front of the wing.
  - **Other details**
    - Terraces, access strips, the divider wall between the two gardens.
    - Rows of 0.20 m square ornaments, cornices.
    - The stair-cage crown with corner horns.
- **Administration**
  - **Towers:** four corner towers, 6.04 × 4.30 m, battered, up to +12.20.
    - Colour "couleur terre de sienne", with panels in "bejmat cuite".
    - Arched door and window with mashrabiya screens.
    - Parapet railings.
  - **Body:** to +9.20 (étage +4.40, roof +7.85). It has windows on the sides, the rear glazing and a skylight pyramid.
  - **Entrance:**
    - A portal to +7.70 (beam +6.50) with a horseshoe arch and a bejmat surround.
    - A passage (+5.60) with the "mur d'eau".
    - A bridge across the front bassin.
  - **Outside:** the rear terrace, the cour anglaise with its railing, timber pergolas at the rear corners, and planters in the front bassin.
  - **Rear bassin:** the permit draws one behind the rear terrace. It is paved over at the client's request, because the plan de masse already draws a bassin on that side.
- **Boutique / restaurant**
  - The roof plan has six square blocks in two rows. The two at one end are towers to +12.00; the others reach +8.70, and the links between them +6.20 (the niveaux on the façades).
  - It also has shopfront glazing, windows with surrounds and two pyramid skylights.
- **Plaza and public areas**
  - The canal, the fountain and the jardin aquatique with its pergola slats.
  - The tennis court and the two mini-foot pitches (lines from the plan), the espace enfant and the kids' pools.

## Ground: roads, pavements, gardens (client review, 13-10)
- **Roads and parking bays:** grey asphalt. The bays are the parallelograms between the sawtooth pavements and the road.
- **Pavements and plot paths:** light concrete paving (the plan's ANSI37 hatch). The herringbone patches are paved the same way.
- **Gardens:** the areas the plan's lines enclose inside each of the 17 plots, as lawn.
- **Asphalt base:** one continuous asphalt base runs under the whole area; the other surfaces sit 5–15 cm above it. Leftover slivers under 1–7 m² are left as road. This means there are no gaps at the tips of the parking teeth.
- **Entrance island:** the rounded 8 × 8 m island is paved with diagonal pavers (the plan's 45° crosshatch) and carries the gatehouse.
- **Removed, at the client's request:** zebra crossings, direction arrows and cars.

## Not on the drawings (to confirm)
- **Boutique / restaurant**
  - The plan de masse draws the same block cluster twice (RESTAURANT and EQUIPEMENT DE COMMERCE), larger than the permit drawing. The permit building is placed at true size on both spots, with its towers towards the plaza.
  - Its roof plan and façades do not line up one to one, so heights are assigned per block from the roof plan.
- **Club des résidents and kiosks**
  - Only their hipped roofs are on the plan de masse.
  - Modelled as single storeys: 3.40 m walls, 30° terracotta roofs.
- **Gatehouse**
  - The plan draws a 4.30 m square with a double outline and no hips, like the other flat-roofed blocks.
  - Modelled with a flat roof, 3.20 m walls and a crown, with its door facing the entrance road (height inferred).
- **Station d'épuration:** its outline is from the plan; the 3.00 m enclosure height is inferred.
- **Pergolas of the jardin aquatique:** the slats are from the plan; the posts and the 3.05 m height are inferred.
- **Colours**
  - The duplexes and the building bodies use the sand render of the Mirleft Bay model; the drawings give no colour for them.
  - The towers' terre de sienne and bejmat come from the drawing notes.
- **Planting**
  - Only the 12 street trees are on the plan.
  - Added for the renders: palms along the canal, two trees in each duplex rear garden, and a few trees on the club and public lawns.
- **Not modelled**
  - Interiors and the sous-sols.
  - The villas of the other tranches.
  - The RD road and the roundabout outside the boundary.
  - Plot walls, which are not drawn.

## Renders
| Camera | View |
|---|---|
| CAM_01_AERIAL_AB | Aerial view of Tranche A + B |
| CAM_02_AERIAL_SITE | The whole site with the empty land |
| CAM_03_CANAL_PROMENADE | Canal between the duplex blocks |
| CAM_04_DUPLEX_FRONTS | Duplex fronts from the club side |
| CAM_05_ADMINISTRATION | Administration portal and fountain |
| CAM_06_PLAZA_CANAL | Plaza, canal and parking |
| CAM_07_RESTAURANT | Boutique / restaurant and the tennis court |
| CAM_08_CLUB_POOLS | Club des résidents and the kids' pools |
| CAM_09_BIRDSEYE_DUPLEX | Bird's-eye view of the duplex blocks |
| CAM_10_TOP_PLAN | Orthographic top view, to compare with the plan de masse |
| CAM_11_DUPLEX_HERO | One duplex from its access side |
| CAM_12_ENTRANCE_ISLAND | Entrance island with the gatehouse |

Light: sun at 10:15 on 15 October, at the site's latitude and longitude, through a Nishita sky. The view transform is AgX Punchy.
