# Mirleft: 1er TRANCHE (plan de masse 12-10), detailed; rest of the site as empty land

This is a Blender model of the 1er TRANCHE of the Mirleft project, built from the new plan de masse **MASSE_12-10_MIRLEFT**. It includes:
- 12 duplex pairs, D-1 to D-24, with their gardens, garden walls, front pavements and planters
- the restaurant, Commerce 1 (superette) and Commerce 2 (glacier), and the toilet block on the plaza
- the sunken pool court (pool and children's pool, planted gradins, stairs, ramp, upper walk and planted stone terraces, technical block)
- the pétanque courts and their pergola
- the herringbone lanes, the roads and parking, the pedestrian crossings, the entrance with its paved median and the fountain

The rest of the site is empty land: the exact site boundary and the natural slope from the contours. Everything is exterior only (no interiors).

| File | Contents |
|---|---|
| `Mirleft_Tranche_1_PACKED_2K.blend` | The scene with every texture packed inside at 2K (14 MB): the light copy to send or open anywhere. |
| `Mirleft_Tranche_1_PACKED.blend` | The same scene with full-size textures packed inside (66 MB). |
| `Mirleft_Tranche_1.blend` | The scene with textures linked from `../mirleft-bay/assets/textures` (4 MB): keep the two folders side by side. |
| `Mirleft_Tranche_1.glb` | Light GLB with JPEG textures and colours (14 MB; shared meshes; no cameras or lights). Metres, Y up. `blender/08_export_glb.py` |
| `Mirleft_Tranche_1_AE_SAFE.glb` | The most compatible version for After Effects (16 MB): the tranche only, one mesh of 187k triangles, centred with its ground at 0, JPEG only, no alpha, no trees. `08_export_glb.py --ae-safe` |
| `Mirleft_Tranche_1_OBJ.zip` | The same single mesh as OBJ + MTL + JPEG textures (6 MB), written by the same command. |
| `d5/` | D5 Render package: `Mirleft_Tranche_1_D5_FULL.fbx` (everything, the 13 cameras, textures embedded), `Mirleft_Tranche_1_D5_NO_PALMS_TREES.fbx` (without the palms and trees, the agaves, grasses and shrubs kept, to place D5's own), `textures/` and `D5_IMPORT_GUIDE.md`. `blender/09_export_d5.py` |
| `renders/` | 13 views at 1920 × 1080 (see the list below). |
| `Mirleft_Tranche_1_views.jpg` | The 13 views on one sheet. |
| `blender/01_extract_site.py` | Reads the plan (DWG made into primitives by `tools/`) and writes `data/site.json`. |
| `blender/02_duplex.py` | The duplex pair, in the two variants the plan draws. |
| `blender/03_public.py` | Restaurant, commerces, toilet block, technical block, pétanque. |
| `blender/04_pool.py` | The pool court. |
| `blender/05_build_scene.py` | Builds, saves and renders the scene: `python 05_build_scene.py --render all`. |
| `blender/lib.py` | Shared helpers; reuses the Mirleft Bay materials, plants and sun. |
| `tools/` | `dwg2json.mjs` (DWG reader), `flatten.py` (primitives with their block path), `inserts.py` (block placements). |

## Sources used
- **MASSE_12-10_MIRLEFT.dwg**: the layout of the 1er TRANCHE.
  - The plan is organised in named blocks: D1-D2 … D19-D24, PISCINE, RESTAURANT MIRLEFT, COMMERCES MIRLEFT, PARKING 1 / 2 + PETANQUE, TERRASSE RESTO, RVT 01 (surfaces), TRACAGE VOIRIE, RAMPE 1 / 2.
  - Every duplex position and rotation is read from the plan's two duplex blocks; they vary from -32.99° to -33.62° and 56.8° as drawn.
  - The tranche's west limit is the line drawn west of row A.
  - The model origin is DWG (252000, 119430). North is up, from the plan's north arrow.
- **2-DUPLEX.DWG** (permis de construire): the duplex envelope, levels, openings, mashrabiya and ornaments.
- **3-PLAN_RESTAURANT_PAVILLON.DWG**: the restaurant, built from this plan (revision 15-10).
  - The 12-10 plan draws a more compact version of the pavilion. Only its position and axis are taken from 12-10.
- **Reference images (15-10)**: two renders of a pool court, used only for the look of the pool court (finishes, planting, furniture). Nothing is taken from them for the layout, which stays the plan's.
- **Plan de masse 2013**: used only for the ground levels.
  - The 12-10 plan is the 2013 plan turned by -33.002°. The two site boundaries match to 0.4 mm on 16 vertices.
  - With that transform, the 2013 contours (55 / 60 m) are brought over.

## Taken from the drawings
- **Duplexes, D-5 to D-24** (ten pairs, the plan's block 'ghghhg')
  - The permit duplex, without the stair cages on the roof.
  - Each house has a spiral stair (Ø 1.65 m) on its upper terrace next to the joint, going up to the roof.
  - A timber pergola covers the whole upper terrace: slats every 0.395 m, beam on the rear parapet line, posts as drawn.
  - The technical shafts ('GT') sit at the front corners of the roof.
- **Duplexes, D-1 to D-4** (two pairs, block 'jjjsdrf1554', parallel to the north boundary)
  - The permit duplex with its stair cages ('Toiture-cage d'escalier') and the pergola over the wing terrace.
  - The same pergola over the upper terrace as D-5 to D-24.
  - D-3/D-4 have the 1 m paved band drawn around the house. No garden wall runs along it: the gardens open onto the band.
  - The D-4 rear garden (revision 15-10, second round) is walled on the lane side and along the 'JARDIN' plots, and a wall crosses the band at the joint of the two houses to close it.
- **Both duplex types**
  - The plan draws lawn up to the house, so the permit's ground-level rear pergola and rear terrace are not built.
  - The dimensions are the permit's. The plan's block is about 2 % larger, so each pair is aligned on its front façade line.
- **Gardens and walls**
  - The gardens are the plan's lawn hatches. Walls run along the garden edges, except the edges that face the house.
  - The 'JARDIN' plots beside D-4 are drawn 0.6 m into that house's band. Their wall stands on the band's edge instead.
  - Those plots are planted beds in 0.60 m rubble-stone planters, like the pool block's other beds.
  - The 'Jardin' beds on the pavements are raised planters.
  - The 57 circles of Ø 1.2 m ('1.2m') on the front courts are tree pits, with a kerb ring and soil.
  - There are 20 meter cabinets ('Emplacement compteur') and 7 bin enclosures, at the plan's positions.
- **Ground surfaces** (from the hatches)
  - The 6 m lanes, the commerce road and the parking aisles: charcoal herringbone pavers ('AR-HBONE').
  - The restaurant terrace and plaza: light herringbone.
  - The lawn the plan draws between the pool court, the restaurant and the road is paved the same way (15-10).
  - The commerce terrace: terracotta herringbone with its charcoal squares.
  - Pétanque: stabilisé.
  - The parking surrounds: concrete slabs.
  - Lawns and the fountain.
  - The unhatched areas are read from the plan's lines: the roads (asphalt) and the pavements and paths (paving).
- **Restaurant**: the pavilion of 3-PLAN_RESTAURANT_PAVILLON.DWG.
  - Sources: the RDC, ETAGE and TERRASSE plans, the four façades and the coupes A-A, B-B, C-C.
  - Four tapered corner towers to +12.20, in terre de sienne with bejmat panels.
  - The body to +9.20 (étage at +4.40, roof at +7.85) with the skylight over the hall.
  - The portal with its horseshoe arch to +7.70, and the passage with the 'murs d'eau' at +5.60.
  - The portal's side walls (revision 15-10, second round) are open, as FACADE DROITE and FACADE GAUCHE draw them. Inside, the bridge runs through with the 'Bassin' on each side of it (RDC plan).
  - Door and windows as FACADE PRINCIPALE draws them (revision 15-10, third round), read off the drawing in metres:
    - **Portal arch** (front and both sides alike): a pointed horseshoe arch, 2.40 m between the jambs with a notch at the springing, 2.48 m at its widest, apex at +4.79.
    - It sits in a rectangular frame of two mouldings and a bejmat field (3.61 × 5.63 m overall).
    - Above: a frieze of eight 0.25 m squares at +6.37, a cornice at +6.89 to +7.19, and the parapet to +7.62 with horns.
    - **Tower windows**: two leaves under a stepped head (three steps each side), in a plain surround, on a bejmat panel 2.79 → 2.11 m wide from +0.43 to +8.21.
    - Lower window 1.30 m wide, from +1.43 to +2.69, on a mashrabiya planter (+0.43 to +1.43).
    - Upper window 0.86 m wide, from +6.10 to +7.20, on a mashrabiya balcony (+5.23 to +6.10).
    - **Body**: twelve 0.25 m squares at +8.03 on the front, and the five bands on the wall either side of the portal.
  - The platform: front bassins with planters, the bridge, the rear terrace and the timber pergolas at the rear corners.
  - The plan's cour anglaise (the sunken court with a railing on the left side) is left out at the client's request (15-10). The deck covers it.
  - The water the plan draws behind the pavilion (the strip along the rear and the two by the pergolas) is left out at the client's request (15-10). The deck covers it.
  - The base of the platform, which shows above the paving on the pool side, is in rubble stone like the pool court's walls.
  - It stands on the axis of the 12-10 restaurant block, moved 1.30 m back so the whole platform fits the plan's TERRASSE RESTAURANT.
  - Six trees of the 12-10 layout fall in its bassins or pergolas or against its walls. They are left out.
- **Commerces**
  - The four towers ('départ tours') and the two bodies.
  - The north block of Commerce 2.
  - The light wells to the sous-sol ('vide d'aération sous sol').
  - The entrances on the east side (from the plan's arrows), and the two stair runs.
- **Pool court**
  - The basin is 21.71 × 7.50 m, with Roman steps in two corners.
  - The children's pool is 9.6 × 3.8 m, against the basin. The plan's hatch is drawn askew; it is built square to the basin (15-10).
  - Loungers ('TRANSATS'): the east deck's as drawn. The west row (12 drawn) is completed to 18, evenly spaced and square to the basin (15-10). All face the pool, backrest on the far side.
  - The gradins: the plan hatches them 'JARDIN'. They are three planted strips of 0.62 m in rubble-stone steps of 0.425 m, flanked by the two stairs of ten steps ('ESCALIERS PISCINE', numbered 1-10).
  - Four planters with palms ('LES BACS A FLEURS').
  - The ramp along the south ('RAMPE'), the planted beds along the north and in the north-east corner ('JARDIN'), the pool cover reel ('COUVERTURE PISCINE AMOVIBLE'), four shower columns.
  - Ten parasols, at the ten Ø 0.45 m circles drawn between the lounger pairs of the east deck (layer 'PR').
  - The technical block (toilettes H / F, local technique, bâche à eau), from its drawn walls.
- **Pool court: look from the reference images** (revision 15-10, second round)
  - Rubble-stone walls with travertine caps.
  - A travertine plank deck, walk, stairs and ramp.
  - A black overflow grille round the basins, a white lip and the strip between the two pools.
  - Three timber cabanas on the west deck, and a planted bed at the foot of the west wall.
  - Agaves, ornamental grasses and Mediterranean shrubs in every bed, gradin and terrace.
- **Pétanque**: two courts, the pergola, benches, the curved wall ('Mur') and the trees in the semicircle.
- **Entrance**: the median, the fountain (semicircle) and the ring road. The fountain's basin is cut into the ground, so its blue tiled floor shows under the water.
  - Median (revision 15-10): no water. The two beds the plan hatches are paved flush, in diagonal stripes of dark slate and light travertine like the hatch.
- **Pedestrian crossings** (revision 15-10): every crossing the plan draws, as flat white paint on the road.
  - Six at the entrance and median ('DFGW', 'xwdfrg').
  - Two on the 8.5 m road at the stair exits ('TRACAGE VOIRIE').
- **Trees**: at every tree symbol of the plan. In the .blend they are in their own collection, `06_TREES_PALMS`; the shrubs, agaves and grasses are in `06_LANDSCAPE`.
  - 98 small palms, 31 round-crowned trees on the plaza and terraces, and 4 palms in the pool planters.
  - 7 trees at the pétanque.
  - 57 trees in the Ø 1.2 m pits. The plan draws 31 of these pits against a façade, so those trees are clipped standards
    (a ball about 0.8 m wide on a 1.85 m stem) that stay clear of the wall. The other 26 are street trees.

## Levels
- **Ground**: the 1er TRANCHE is graded on one plane fitted to the contours, 5.5 % rising to the east.
- **Buildings**
  - Each duplex pair sits at the plane height of its centre.
  - The commerces sit at the level of their entrance side (east). On the downhill side their plinth shows.
  - The restaurant's platform deck is level with the highest ground at its edge. Its plinth goes down to the lower ground on the pool side.
- **Pool court**: 1.70 m from the deck to the top of its gradins (four risers of 0.425 m, and the ten 0.17 m steps of the stairs).
  - Revision 15-10: the whole pool area is 1.00 m lower. The deck is 2.70 m below the graded ground at the top of the gradins.
  - Behind the gradins, an upper walk 2.40 m wide at the gradins' top level (deck + 1.70 m) runs the length of the court. The ramp climbs from the deck to it.
  - Second round of 15-10: no more graded slope behind the walk. Two tiers of planted terraces in stone take it up to the paving by the restaurant terrace (0.7 to 2.0 m higher, rising to the north).
    - The first tier is halfway up and the second at the paving level.
  - A stair in line with each pool stair climbs from the walk to the paving, in risers of at most 0.17 m on 0.30 m treads:

    | Stair | Height | Risers |
    |---|---|---|
    | North (in line with the north pool stair) | 1.96 m | 12 × 0.163 m |
    | South (in line with the south pool stair) | 0.76 m | 5 × 0.151 m |

  - The other sides are retaining walls in stone, with a parapet about 0.45 m above the paving or lawn outside.
  - The ramp has a 0.90 m guard over the court.
  - The north wall is the 1 m guard of the long stair beside it. It steps down with the stair and opens where the stair lands on the deck.
- **Stairs** (revision 15-10): built stairs, filled wall to wall. Each step has a level tread, a vertical riser and a dark stone nosing. A handrail runs on the centre line over each flight.
  - The flights are where the plan draws them: 'ESC 16-17' and 'ESC V4' across the rows, and the long stair north of the pool.
  - The plan gives no levels. Each stair climbs the height the ground gives between its two ends, in risers of about 15 cm:

    | Stair | Height | Risers | Risers drawn |
    |---|---|---|---|
    | ESC 16-17 | 0.79 m | 5 × 0.158 m | 9 + 9 |
    | ESC V4 | 0.65 m | 4 × 0.163 m | 9 + 12 |
    | North of the pool | 2.47 m down | 16 × 0.154 m | 10 + 11 |

  - The level walk between the flights takes the rest of the length.
  - The long stair north of the pool goes down from the row C lane into the pool court (revision 15-10). It lands on the deck at the court's north-east corner, by the showers.
    - Retaining walls hold the higher ground on its north side and at its end.

## Removed (client, 13-10)
Direction arrows and cars. The zebra crossings were put back as paint (15-10).

## Not on the drawings (to confirm)
- **Heights not given**
  - Commerces: single storey to +4.40 with a crown to +5.20, towers to +8.10.
  - Toilet block: 3.20 m.
  - Technical block: 3.00 m.
- **Commerce stairs**: modelled going down to the sous-sol, which the light wells point to.
- **Walls**: garden walls 1.80 m; pétanque and boundary walls 1.20 m.
- **Ground between the pool and the restaurant terrace**: lawn on the plan, paved in light herringbone at the client's request (15-10). The upper walk and the planted stone terraces lie between it and the gradins.
- **Stair heights**: the plan gives no levels.
  - 'ESC 16-17' and 'ESC V4' follow the ground (0.65 to 0.79 m). Their drawn risers (18 and 21) would need about 2.7 to 3.4 m.
  - The extra 1.00 m for the pool area is a choice. With it, the stair north of the pool goes down 2.47 m in 16 risers. Its 21 drawn risers would need about 3.3 m.
  - With the platform levels, the drawn risers can be built instead.
- **Median paving**: the material of the two beds is read from the plan's hatch.
- **Pool court**
  - The finishes, the cabanas, the bed at the foot of the west wall and the planting come from the reference images, not from the plan.
  - The 'PR' circles are read as parasols.
  - The layout of the terraces and of the two stairs up to the paving is a proposal.
  - The parapet heights (about 0.45 m over the ground outside, 0.90 m on the ramp, 1 m on the stair) are to confirm.
- **Planting**
  - The plan gives tree positions, not species.
  - Small palms are modelled as date palms, the round symbols as olive-like trees, and the pool and pétanque trees as drawn.
  - The Ø 1.2 m circles are read as tree pits; the clipped standards against the façades are a choice.
  - The shrubs in the raised beds and all the pool court planting are added (agaves, grasses, rosemary-like and flowering shrubs).
- **Colours**: the duplexes and building bodies use the sand render of the Mirleft Bay model. The towers' terre de sienne and bejmat come from the pavilion drawings.
- **Not modelled**: interiors, the sous-sols, the other tranches, and the RN road outside the boundary.

## Renders
| Camera | View |
|---|---|
| CAM_01_AERIAL_T1 | Aerial view of the tranche |
| CAM_02_AERIAL_FROM_WEST | The tranche from the west, with the empty land |
| CAM_03_POOL_COURT | The pool court from its south-west corner, towards the gradins, the terraces and the restaurant |
| CAM_04_RESTAURANT | The restaurant pavilion, portal and fountain |
| CAM_05_COMMERCES_PLAZA | Commerces and their terrace, from above the plaza |
| CAM_06_LANE_ROWS | Along a herringbone lane between the duplex rows |
| CAM_07_DUPLEX_A_HERO | A D-5…D-24 pair from its lane (D-17 / D-18) |
| CAM_08_DUPLEX_B_D1_D2 | D-1 / D-2 from their access side |
| CAM_09_PETANQUE | Pétanque courts and pergola |
| CAM_10_ENTRANCE_FOUNTAIN | Entrance from the ring road: paved median, crossings, fountain, restaurant and commerces |
| CAM_11_GARDENS_BIRDSEYE | Bird's-eye view of the gardens and roofs |
| CAM_12_TOP_PLAN | Orthographic top view, to compare with the plan de masse |
| CAM_13_STAIR_ESC_V4 | The stair 'ESC V4' across row C, looking down it from the upper lane |

**Lighting**: the sun at 10:15 on 15 October, at the site's latitude and longitude, through a Nishita sky. The view transform is AgX Punchy.
