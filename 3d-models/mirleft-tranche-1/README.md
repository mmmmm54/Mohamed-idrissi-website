# Mirleft: 1er TRANCHE (plan de masse 12-10), detailed; rest of the site as empty land

This is a Blender model of the 1er TRANCHE of the Mirleft project, built from the new plan de masse **MASSE_12-10_MIRLEFT**. It includes:
- 12 duplex pairs, D-1 to D-24, all built to the villa N°09 drawing (rev 4), with their gardens, garden walls, front pavements and planters
- the restaurant, Commerce 1 (superette) and Commerce 2 (glacier), and the toilet block on the plaza
- the sunken pool court (pool and children's pool, planted gradins, stairs, ramp, upper walk and planted stone terraces, technical block)
- the pétanque courts and their pergola
- the lanes, the roads and parking in beige herringbone pavers (rev 4), the pedestrian crossings, the entrance with its paved median and the fountain
- **Tranche 2 (21-10)**: the 33 villas type B of the plan de masse 31-05-13 west of the tranche, with their pools, gardens, walls and gates, the streets round them, the parking and the Centre d'entretien (see **Tranche 2** below)
- **Tranche 3 (23-10)**: the hotel (a design proposal, no plan; since 24-10 two storeys, one height, in the SPA's style) and the 4 villas type A of the plan de masse 31-05-13, west of the SPA and of the type C block, with their streets and parking (see **Tranche 3** below)

The rest of the site is empty land: the exact site boundary and the natural slope from the contours. Everything is exterior only (no interiors).

Round the site, the real surroundings: the terrain out to 12 km with a satellite image on it, and the Atlantic at sea level (see **Surroundings** below).

| File | Contents |
|---|---|
| `Mirleft_Tranche_1_PACKED_2K.blend` | The scene with every texture packed inside at 2K (25 MB): the light copy to send or open anywhere. |
| `Mirleft_Tranche_1_PACKED.blend` | The same scene with full-size textures packed inside (68 MB). |
| `Mirleft_Tranche_1.blend` | The scene with textures linked from `../mirleft-bay/assets/textures` and `data/textures` (11 MB): keep the folders side by side. |
| `Mirleft_Tranche_1.glb` | GLB with JPEG textures and colours (44 MB with the surroundings; shared meshes; no cameras or lights). Metres, Y up. `blender/08_export_glb.py` |
| `Mirleft_Tranche_1_AE_SAFE.glb` | The most compatible version for After Effects (95 MB, with Tranche 2): the two tranches only, one mesh, centred with its ground at 0, JPEG only, no alpha, no trees. `08_export_glb.py --ae-safe` |
| `Mirleft_Tranche_1_OBJ.zip` | The same single mesh as OBJ + MTL + JPEG textures (31 MB), written by the same command. |
| `d5/` | D5 Render package: `Mirleft_Tranche_1_D5_FULL.fbx` (everything, the 20 cameras, textures embedded), `Mirleft_Tranche_1_D5_NO_PALMS_TREES.fbx` (without the palms and trees, the agaves, grasses and shrubs kept, to place D5's own), `textures/` and `D5_IMPORT_GUIDE.md`. `blender/09_export_d5.py` |
| `renders/` | 20 views at 1920 × 1080 (see the list below). |
| `Mirleft_Tranche_1_views.jpg` | The 13 views of Tranche 1 on one sheet. |
| `blender/01_extract_site.py` | Reads the plan (DWG made into primitives by `tools/`) and writes `data/site.json`. |
| `blender/01b_parking_lines.py` | Adds the parking bays' separator lines of the plan to `data/site.json` (run after 01). |
| `blender/02_duplex.py` | The duplex pair: villa N°09 and its mirror (rev 4). |
| `blender/03_public.py` | Restaurant, commerces, toilet block, technical block, pétanque. |
| `blender/04_pool.py` | The pool court. |
| `blender/05_build_scene.py` | Builds, saves and renders the scene: `python 05_build_scene.py --render all`. |
| `blender/lib.py` | Shared helpers; reuses the Mirleft Bay materials, plants and sun; draws the rev 4 textures into `data/textures/` (pavers, tiles, stone band). |
| `blender/11_extract_t2.py` | Tranche 2: reads the plan de masse 31-05-13 and writes `data/t2_site.json` (lots, villa placements, gardens, streets). |
| `blender/12_villa_b.py` | The villa type B of `5-VILLA_TYPE_B.DWG`, in the finishes of the duplexes, with its pool. |
| `blender/13_tranche2.py` | Builds Tranche 2 into the scene (called by `05_build_scene.py`), in its own collections, objects and materials. |
| `blender/14_villa_c.py`, `15_spa.py` | The villa type C of `PLAN_VILLA_TYPE_C.dwg`; the SPA of `7-SPA-A0-1.pdf`. |
| `blender/16_villa_a.py`, `17_hotel.py` | The villa type A of `VILLA_TYPE_A.dwg`; the hotel (a design proposal). |
| `blender/18_extract_t3.py`, `19_tranche3.py` | Tranche 3: reads the plan de masse 31-05-13 into `data/t3_site.json`; builds it into the scene (called by `05_build_scene.py`). |
| `blender/10_fetch_geo.py` | Downloads the heights and the satellite image round the site into `data/geo/` (run once, outside Blender; needs pyproj and rasterio). |
| `tools/` | `dwg2json.mjs` (DWG reader), `flatten.py` (primitives with their block path), `inserts.py` (block placements). |

## Sources used
- **MASSE_12-10_MIRLEFT.dwg**: the layout of the 1er TRANCHE.
  - The plan is organised in named blocks: D1-D2 … D19-D24, PISCINE, RESTAURANT MIRLEFT, COMMERCES MIRLEFT, PARKING 1 / 2 + PETANQUE, TERRASSE RESTO, RVT 01 (surfaces), TRACAGE VOIRIE, RAMPE 1 / 2.
  - Every duplex position and rotation is read from the plan's two duplex blocks; they vary from -32.99° to -33.62° and 56.8° as drawn.
  - The tranche's west limit is the line drawn west of row A.
  - The model origin is DWG (252000, 119430). North is up, from the plan's north arrow.
- **DUPLRX_N__09.dwg** (villa N°09, rev 4): the duplex now. Plans RDC / 1er étage / terrasse, coupe A-A, façades principale, arrière and droite. It replaces **2-DUPLEX.DWG** (permis de construire), which the earlier rounds used.
- **Remarks on the D5 model (rev 4, 10 slides)** with their reference images: the front and rear renders of the villa, the paver photo, and the two tile references. The images are used for the look only (colours, surrounds, door, railings, planting). Nothing else is taken from them.
- **3-PLAN_RESTAURANT_PAVILLON.DWG**: the restaurant, built from this plan (revision 15-10).
  - The 12-10 plan draws a more compact version of the pavilion. Only its position and axis are taken from 12-10.
- **Reference images (15-10)**: two renders of a pool court, used only for the look of the pool court (finishes, planting, furniture). Nothing is taken from them for the layout, which stays the plan's.
- **Plan de masse 2013**: the ground levels, and the layout of Tranche 2 (its type B blocks, 21-10).
- **5-VILLA_TYPE_B.DWG** (21-10): the villa type B of Tranche 2.
  - The 12-10 plan is the 2013 plan turned by -33.002°. The two site boundaries match to 0.4 mm on 16 vertices.
  - With that transform, the 2013 contours (55 / 60 m) are brought over.

## Taken from the drawings
- **Duplexes, D-1 to D-24** (rev 4): all twelve pairs are villa N°09 and its mirror across the 'Axe limite villa'. The plan's two blocks keep their positions; the pairs are aligned on their front façade line as before.
  - **RDC** (84.32 m²): wing to the front (bedroom), entrance door beside it with its canopy, kitchen window (allège 1.00), salon window on the side, 4-leaf sliding door onto the garden. Eight square niches across the rear at +3.10.
  - **1er étage** (54.36 m²): set back 1.36 m behind the wing (front terrace) and 3.44 m behind the rear (rear terrace). One window over the wing, one in the side part, a 2-leaf sliding door onto the rear terrace, niches under the cornice and on the side.
  - **Levels**: RDC +0.20, terraces +3.90, roof +7.10, acrotère +8.30, stair cage +9.80. Front terrace parapet +4.90 with three niches; rear terrace side parapets and piers +4.70.
  - **Cornice** (façades and reference images): grey stone ledge, ochre stone band, grey stone ledge (+7.22 to +7.62), then the acrotère with a rounded coping. The stair cage has the same cornice.
  - **Stair cage** of the two villas over their stairs (plan TERRASSE), with its roof door on the side, a small window at the back, niches and horned corners. 'GT' ducts on the roof.
  - **Rear terrace**: masonry piers with wooden geometric railings between them ('Cadre en bois').
  - **Pergolas**: timber ('Pergola en bois', 'V/Terrasse'). Over the rear terrace, 15 rafters on a beam and four posts; over the front terrace, 7 rafters.
  - **Separation between the two villas' terraces** (remark, slide 10): a wall on the joint across the front terrace and the rear terrace, up to the pergolas, as the drawing shows it on the joint, and a lower one across the roof terraces.
  - **Finishes** (reference images): beige render, taupe stone surrounds round the windows and doors, beige aluminium frames a shade darker than the render (client 20-10; they came out black), studded dark timber entrance door with a stone canopy, curtains behind the glass.
  - **Front garden**: low stone-clad wall with a beige coping, gate pillars and a timber gate in front of the entrance path (façade principale), and a planted strip behind it.
  - **Rear**: the paved terrace behind the salons (plan RDC, 2.05 m deep). It follows the graded ground (never above the salons' floor) and the lawn is cut round it (19-10).
- **Client corrections (19-10)**: the 43 tree pits ('1.2m' circles) in front of the villas are removed with their trees (14 kept elsewhere); the garden walls, cut to the permit house, now run to the wider villa N°09 façades (gaps up to 1.2 m closed); the raised 'Jardin' beds take the lawn strip the plan left round them.
- **Villa entrances (19-10)**: every gate is reachable as on the villa N°09 drawing. Where the plan puts lawn or a garden wall between the gate and the lane (D-1 to D-4 and some others, 23 places), the garden wall is opened in front of the gate and a beige-paved path runs from the lane through the gate to the door. At D-1 to D-4 the tall walls in front of the houses, which the plan does not draw, are now the low stone wall of the villa drawing.
- **Client corrections (19-10, last round)**
  - The salon's sliding door onto the garden follows the client's reference photo: four leaves on two tracks with slim beige aluminium frames, set back in a taupe stone reveal with a flat taupe band round it, sheer linen curtains in folds (the third leaf left open) and the lit salon behind with a sofa and a low table.
  - The restaurant has the same portal block (pointed horseshoe arches on three sides, frames, frieze, parapet) behind its rear entrance too, on the rear terrace between the pergolas.
  - The long stair north of the pool court has nothing to do with the pool, which has its own stairs: people from the restaurant side take it to the north. From the ground at its east end it goes down west to the row C lane (1.06 m, seven risers in the plan's two flights), with no handrails. The court's north wall and the upper walk's north wall stand unbroken between it and the pool, and a 1 m parapet runs where the ground beside it is higher.
  - The villas' rear terrace is level with the salons' floor (+0.20), flush with the sliding door's sill, and the gardens round the villas (behind the side-part fronts, 26 lawn pieces) are levelled with it: the lawn lies flat 3 cm under the terrace instead of following the slope. The garden walls keep at least 1.20 m over a raised lawn.
  - The north stair's travertine planks carry on east past its top, over the pavement and the playground tiles that were there, to the trottoir along the restaurant terrace (26.7 m²).
  - No holes in the finished ground: the small holes and slivers the plan leaves in its hatches (and pieces too small to keep), where the road base showed through, are filled with the surface that borders them most (312 pieces, each under 2.5 m², never where a tree pit is).
  - Parking bays: the 34 separator lines the plan draws are painted as 10 cm white lines (`ROAD_PAINT_PARKING`), read from the DWG by `blender/01b_parking_lines.py`: PARKING 1 (12) and PARKING 2 (10), the angled bays by D-17/D-18 (5) and D-19/D-24 (4), and the bays along the kerb north of the commerces (3).
- **Gardens and walls**
  - The gardens are the plan's lawn hatches. Walls run along the garden edges, except the edges that face the house.
  - The 'JARDIN' plots beside D-4 are drawn 0.6 m into that house's band. Their wall stands on the band's edge instead.
  - Those plots are planted beds in 0.60 m rubble-stone planters, like the pool block's other beds.
  - The 'Jardin' beds on the pavements are raised planters.
  - The 57 circles of Ø 1.2 m ('1.2m') on the front courts are tree pits, with a kerb ring and soil.
  - There are 20 meter cabinets ('Emplacement compteur') and 7 bin enclosures, at the plan's positions.
- **Ground surfaces** (from the hatches; rev 4 finishes from the remarks)
  - Roads (asphalt), the herringbone lanes and trottoirs, the pavements, the commerce terrace (terracotta) and the restaurant terrace (light herringbone) are as first built: the client finishes them by hand in D5 (19-10). The commerce terrace keeps its terracotta, the strip between the commerces and D-1/D-2 is beige, and the trottoirs along the commerces and the restaurant plaza down to the road are their own object (client, 19-10), in the same beige pavers since 22-10 (they were grey). The two lanes between the villa rows, the dark squares in the commerce terrace, the beige strip and the villa entrance paths are each their own object with their own material too, so one texture never changes another (client, 19-10). Each part is its own object with its own material, and the entrance zone (fountain, median, parking) is kept apart from the villas: see `d5/D5_IMPORT_GUIDE.md`. The beige paver and grey trottoir textures stay in `data/textures/`.
  - The area the plan draws as lawn between the pool court, the restaurant and the road (the playground): beige slate-look tiles, 30 × 60 ('carrelage beige', AZUVI Ardesia Nature type, slide 5).
  - Pétanque: stabilisé.
  - The parking surrounds: concrete slabs.
  - Lawns and the fountain.
  - The unhatched areas are read from the plan's lines: the roads (asphalt) and the pavements and paths (paving).
- **Restaurant**: the pavilion of 3-PLAN_RESTAURANT_PAVILLON.DWG.
  - Sources: the RDC, ETAGE and TERRASSE plans, the four façades and the coupes A-A, B-B, C-C.
  - Four tapered corner towers to +12.20. Rev 4 (slide 1): in the building's colour, walls and panels, no more terre de sienne or bejmat on them.
  - The body to +9.20 (étage at +4.40, roof at +7.85) with the skylight over the hall.
  - The portal with its horseshoe arch to +7.70, and the passage with the 'murs d'eau' at +5.60.
  - The portal's side walls (revision 15-10, second round) are open, as FACADE DROITE and FACADE GAUCHE draw them. Inside, the bridge runs through with the 'Bassin' on each side of it (RDC plan).
  - Door and windows as FACADE PRINCIPALE draws them (revision 15-10, third round), read off the drawing in metres:
    - **Portal arch** (front and both sides alike): a pointed horseshoe arch, 2.40 m between the jambs with a notch at the springing, 2.48 m at its widest, apex at +4.79.
    - It sits in a rectangular frame of two mouldings and a bejmat field (3.61 × 5.63 m overall).
    - Above: a frieze of eight 0.25 m squares at +6.37, a cornice at +6.89 to +7.19, and the parapet to +7.62 with horns.
    - **Tower windows**: two leaves under a stepped head (three steps each side), in a plain surround, on a panel 2.79 → 2.11 m wide from +0.43 to +8.21 (bejmat until rev 4, now in the building's colour).
    - Lower window 1.30 m wide, from +1.43 to +2.69, on a mashrabiya planter (+0.43 to +1.43).
    - Upper window 0.86 m wide, from +6.10 to +7.20, on a mashrabiya balcony (+5.23 to +6.10).
    - **Body**: twelve 0.25 m squares at +8.03 on the front, and the five bands on the wall either side of the portal.
  - **Rear entrance** (rev 4, slide 4): the main façade's door between the rear towers: the same pointed horseshoe arch in the same frame (two mouldings and a bejmat field), glazed. The etage window above it is raised clear of the frame and the mashrabiya screen under it is gone.
  - The platform: front bassins with planters, the bridge, the rear terrace and the timber pergolas at the rear corners.
  - The plan's cour anglaise (the sunken court with a railing on the left side) is left out at the client's request (15-10). The deck covers it.
  - The water the plan draws behind the pavilion (the strip along the rear and the two by the pergolas) is left out at the client's request (15-10). The deck covers it.
  - The base of the platform, which shows above the paving on the pool side, is in rubble stone like the pool court's walls.
  - It stands on the axis of the 12-10 restaurant block, moved 1.30 m back.
  - Round it, the 12-10 plan de masse (client, 15-10, last round). There is no raised platform and no long front bassin.
    - The plan's two bassins with their planters are at the front corners, beside the portal.
    - Its two pergolas stand on a rear terrace behind the rear towers.
    - The TERRASSE RESTAURANT paving runs all round. The floor (+0.20) is at the highest ground; the stone base shows downhill.
  - Six trees of the 12-10 layout fall in its bassins or pergolas or against its walls. They are left out.
- **Commerces**
  - The four towers ('départ tours') and the two bodies.
  - The north block of Commerce 2.
  - The light wells to the sous-sol ('vide d'aération sous sol').
  - The entrances on the east side (from the plan's arrows), and the stair run on the north side. The south stair down to the sous-sol is left out (client, 15-10).
  - Rev 4 (slide 1): the restaurant's height. Bodies to +7.85 with the crown to +9.20, towers to +12.20, an upper row of windows like the pavilion's etage, the towers in the building's colour.
- **Pool court**
  - The basin is 21.71 × 7.50 m, with Roman steps in two corners.
  - Rev 4 (slide 6): both pools tiled in green stone-look porcelain, 30 × 60 ('carrelage vert', La Platera Jade type).
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
  - Each duplex pair sits at the plane height of its centre (villa +0.00 = the pad).
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
- **Stairs** (revision 15-10): built stairs, filled wall to wall. Each step has a level tread, a vertical riser and a dark stone nosing. No handrail on the centre line (client 20-10: removed).
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

## Surroundings (16-10)
- **Georeference**: the plan's coordinates are local. The centre of the tranche is put at the point the client placed on the map: 29°32'54.74"N 10°03'10.50"W (Google Earth ground 60.88 m, as the model's levels).
  - The plan's north arrow is taken as true north, at 1:1 scale.
  - The site outline then lies on the graded patch beside the north–south road, and the coast is about 1 km west, as on the map.
- **Terrain**: AWS Terrain Tiles (SRTM on land, ETOPO1 under the sea).
  - ±3 km at 20 m, and a ring out to ±12 km at 150 m.
  - Outside the site, the survey heights are moved to meet the site's own heights (contours) at the boundary. They agree to 1.4 m on average; the correction fades out over 300 m.
- **The project's land (16-10)**: inside the site boundary, the land keeps the site's own heights, in its own brown soil (`T16_Site_Land_Soil`, object `TERRAIN_SITE_EMPTY_LAND`), so the parcel reads within its limits on the satellite ground.
  - The real ground drops 0.60 m along the boundary, fading out over 15 m, so a short cut face (`T10_Terrain_Cut_Soil`) marks the limits. The boundary posts stand at its corners.
  - This step and the soil colour are for presentation. They are not on the plan.
- **Image**: Sentinel-2 L2A true colour, 10 m, from 14 July 2025. It is the least cloudy summer scene, picked by measuring cloud over Mirleft.
  - Contains modified Copernicus Sentinel data 2025.
- **Ocean**: a surface at sea level (altitude 0, z = −50) wherever the survey ground is under 1.5 m, so it meets the real shoreline. The seabed is set under it.
- `data/geo/` keeps the downloaded data, so the scene builds offline. `python 10_fetch_geo.py` refreshes it.
- To confirm: the exact position and orientation of the site on the map. A survey point on site would fix them.

## Rev 4: remarks on the D5 model (17-10)
| Slide | Remark | Done |
|---|---|---|
| 1 | Entrance roads in pavers; commerces at the restaurant's height; towers the colour of the building | Roads left for the client to pave in D5 (19-10); commerces to +7.85 / +9.20, towers to +12.20; all towers (commerces and restaurant) in the building's render |
| 2 | Surround of the commerces and the restaurant in beige pavers | Left for the client to finish in D5, each as its own object (19-10) |
| 3, 8 | Lanes next to the duplexes in beige pavers | Left for the client to pave in D5 (19-10) |
| 4 | Restaurant rear: the same entrance door as the main façade | Pointed horseshoe arch in its frame, glazed, between the rear towers |
| 5 | Ground by the playground in beige tiles (AZUVI Ardesia Nature) | Beige slate-look tiles 30 × 60 on that whole paved area |
| 6 | Pools in green tiles (La Platera Jade) | Both pools, floor, walls, steps and divider |
| 7, 9 | Duplex front and rear exactly as the reference images and the drawing | Duplexes rebuilt to villa N°09 (see **Duplexes**) |
| 10 | Roads between the rows in beige pavers; separation between the two terraces of each villa | Roads left for D5; walls on the joint across the front, rear and roof terraces |

## Tranche 2: villas type B (21-10)
Client 21-10: "zid ghir tranche 2", then "block by block, by villa type": every villa type B of the plan de masse
31-05-13 (`plan_masse_terrasse_31-05-13.dwg`, the plan the client circled), in the same file as Tranche 1, which is
left as it was. Sources: the plan de masse for the lots, plots, streets and the plan's own type B drawings (pool,
skylight and stair give each villa's orientation); `5-VILLA_TYPE_B.DWG` for the villa (RDC, étage, terrasse, the
four façades, coupes A-A and B-B).
- **Blocks**: the northern block along the Voie Publique, 21 villas (B-01 to B-21, three rows of seven); the southern
  block, 12 villas (B-22 to B-33). One southern lot is drawn empty on the 2013 plan; it gets a villa like its neighbours.
- **Villa type B** (`12_villa_b.py`): the drawing's plans and levels (RDC +0.20, étage +3.90, roof +7.10, acrotère
  +8.20, stair cage +9.90 / +10.10, pool 6.40 × 4.25 m, N = -1.60), dressed like the duplexes: the sand render,
  taupe surrounds, beige aluminium, sheer curtains and the lit salon behind the recessed glazing, the rows of square
  niches, the grey / ochre / grey cornice and rounded acrotère, the horned crown of the stair cage, mashrabiya panels
  in the acrotère and parapets, timber pergolas over the étage terrace and the front terrace (the drawing's voile),
  the 'Manzah' balcony with its planter, a skylight lantern over the entrance void, jade pool tiles, a white coping
  and Roman steps.
- **Placement (rev 21-10, "look at the architect plan")**: every villa as the plan de masse draws it, pool at the
  rear and house where the plan's house is, on the plot the plan's fences enclose. The southern block is the plan's
  grid of 3 rows of 4 plots, the villas back to front along each row as drawn, entered from the street along the
  side of their plot. Its plots are 18 to 19 m long, shorter than the villa drawing with its pool (19.45 m), so
  those 9 villas use the **compact** model: the pool 1.50 m nearer the house (1 m from it), as the plan de masse
  itself draws it (to confirm).
- **Gardens and walls**: each garden flat at its villa's pad (lawn 3 cm under the terraces), held by its walls where
  the ground falls away; garden walls 1.80 m in the render with its trim (at least 1.20 m over the lawn); on the
  villa's street side (the front, or the side for the southern block) a low stone-clad wall with its beige
  coping, the gate pillars and timber gate of the duplexes, and a paved path to the door (or, from the
  kitchen side, to the kitchen door and on along the house to the garden). Neighbouring gardens share one
  wall. The plan draws two villas of the northern block (B-02, B-08) back to front with no street in front
  or beside them: their gate is in the rear wall, on the street, beside the pool (to confirm).
- **Streets (rev 22-10, "kima kayn f planning", with the plan's widths)**: the plan's zoning lines are the kerbs
  of its main streets, so the carriageway is everything between them: the Voie Publique and the south road
  8 m inside a 1.6 to 2.9 m planted verge along the boundary, then a 2 m pavement; the street between Tranche 2
  and Tranche 1 6.06 m between its two zoning lines, with its pavement on both sides (2.1 and 2.3 m), the
  plan's 3.2 to 5.1 m planted strip between the pavement and the fences on the Tranche 2 side and a planted
  strip up to Tranche 1's limit on the other; the streets between the blocks and down the west side of the
  southern block 5.1 to 6 m. The lanes inside the blocks are 5 m between kerbs drawn 0.40 m off the fences
  (no pavement, as the plan). Paved crossings over the planted strips at the gates; date palms, agaves and
  grasses on the wide strips, Washingtonia palms in pits every 11 m on the pavements.
- **Tranche 1's west pavement (22-10)**: south of where the street's east kerb leaves Tranche 1's limit (55 m up
  from the south road) the street runs over Tranche 1's west pavement, as the plan draws it: that pavement is
  cut away under it (and where less than 1.5 m of it would be left), the street is built there by Tranche 2
  (`t1_trim` in `data/t2_site.json`). The rest of Tranche 1 is untouched.
- **Client remarks (22-10, second round)**: the second 'Centre d'entretien', drawn askew, is squared on the
  block like the other two, with lawn round it and a 1.50 m paved apron as the first; the bays open straight
  onto the street (no kerb across their mouths) with one 6 cm line between two bays; the villa on the lot
  the plan draws with another building (B-24) takes its whole lot, as wide as the next villa, up to the west
  street with the rounded kerb of the corner; what was left of Tranche 1's west pavement between the two
  carriageways at the south road is gone; the small islands of pavement at the lane mouths are street.
- **Client remarks (22-10, third round)**: the gates of the villas whose front fence runs askew along the
  street (B-18, B-20, B-21 on the street along Tranche 1) stand in the fence itself, the low stone wall
  along the whole askew front (a high wall stood behind the gate); the lanes run into the streets their full
  width, without the pavement returns into their mouths; the first row of bays backs onto its planted strip
  as the second does, with one line between two bays in the staggered row too.
- **Client remarks (22-10, fourth round)**:
  - the street between the northern block and the southern one (178 m, from the street along Tranche 1
    down to the west end of the block) is a stair, fence to fence (6.80 m): level treads of 3.87 m in the
    beige pavers, 45 risers of 15 cm with a stone nosing, two square fountains (2.40 m basin, stone rim,
    bronze spout on a stone pedestal) at a third and two thirds of it. The streets that came into it end at it;
  - villa type B: no pergola over the ground-floor front terrace; the pergola is over the étage's front
    balcony (the bedroom's sliding door opens onto it);
  - the aluminium of the frames in the 'quartz' colour (light sand grey, `D17_Frame_Aluminium_Quartz`), not
    brown; in the D5 package the glass is lighter and the rooms behind it a lit warm plaster, so the
    windows never read black.
- **All beige (22-10)**: the two herringbone lanes between the villa rows (`GROUND_LANE_1`, `GROUND_LANE_2`) and the
  entrance's herringbone trottoirs are in the same beige pavers as the pavements (they were charcoal, the same
  pattern darker); the commerce terrace keeps its dark squares.
- **D5 (22-10)**: in the D5 package the two tranches' ground is one object per surface with one material:
  streets and bays `GROUND_ROADS_T1_T2`, beige pavements and paths `GROUND_PAVERS_BEIGE_T1_T2`
  (`T17_Pavers_Beige_Herringbone`), kerbs `GROUND_KERBS_T1_T2` (`Kerb_Concrete`), lawns `GROUND_LAWN_T1_T2`
  (`T03_Lawn`), so a texture changed in D5 changes both tranches together. The entrance zone's roads stay their
  own object (`GROUND_ROADS_ENTRANCE`). The Blender scene keeps them apart.
- **Roads in beige pavers (22-10, later)**: "hadi ka7la mabghinahach, dir hadi texture bdabt bdabt": every road
  and the parking bays, both tranches and the entrance zone, are in the beige herringbone pavers of the plaza,
  the very same material `T17_Pavers_Beige_Herringbone` (0.80 m tile). No asphalt is left.
- **Exports (23-10)**: the scene, `Mirleft_Tranche_1_PACKED_2K.blend` and the D5 package (`d5/`, both FBX) were
  rebuilt with the villas type C, the SPA, the roads in beige pavers and the fixes of 23-10; the GLB, OBJ and
  renders are from 21-10.
- **Parking strip (rev 21-10)**: the 26 bays the plan draws along the south road, painted, and its three buildings:
  'Centre d'entretien' twice and 'Office', the squares with hipped roofs of the plan, in the villas' render
  with their cornice, a terracotta pyramid roof, a timber door to the parking and windows in taupe surrounds
  (heights 3.40 m + 1.90 m roof, to confirm).
- **By Tranche 1**: what is left of Tranche 1's lots west of its limit line, between it and the street, is lawn.
- **Levels**: the blocks graded on the plane of Tranche 1 (the 2013 contours fit it within 1.5 m there), each
  villa at the height of its centre; the streets follow the site's ground beyond them (blended over 25 m), so
  the south road goes down along the type C villas as the contours do; the empty land stops at the streets.
- **To confirm**: the compact pool of the southern block; the rear gates of B-02 and B-08; the buildings' heights; the planting.

## Villas type C and the SPA (22-10)
Client 22-10: "dzid villa type c nfs style dima, dont do mistakes, and add spa: we don't have a plan but we want
a suggestion on the same size as on the plan" (with reference photos of a riad spa).
- **Villa type C** (`14_villa_c.py`, from `PLAN_VILLA_TYPE_C.dwg`: rez-de-chaussée, terrasse, the four façades,
  coupes A-A and B-B): a single-storey kasbah house, 15.38 x 12.15 m. Four battered towers (the rooms of the two
  wings: Chambre III and the salon marocain, Chambres I and II), their walls leaning in 0.255 m over 4.31 m as the
  façades draw them, the villas' cornice (grey ledge / ochre band / grey ledge), a crown, parapet +4.80 with horns,
  roofs at +3.70 with a door in each parapet onto the terrace over the bathroom between them; the bathrooms lower
  (plain walls, parapet +4.60); the centre (kitchen, hall, W.C., salon) to +5.50 with the rounded coping, roof
  +4.50, four steps up to it from the bathroom terraces; the portal tower +6.70 with horns over the entrance hall:
  a taupe alfiz round a pointed horseshoe arch, the studded door and its transom, a mashrabiya tympanum. Rows of
  square niches, the horizontal grooves every metre of the façades, taupe surrounds (the wide panels of the
  small windows as drawn), quartz aluminium, curtains, the salon's 4-leaf glazing set back with the lit salon
  behind; the outside stair up to the west terrace (18 treads of 0.27 m and a landing, solid parapet); the pool
  7.50 x 4.00 m over its coping (basin 4.50 x 3.00 m, -1.40, Roman steps; spa basin 1.70 x 3.00 m).
- **Choices where the drawing's views differ** (to confirm): the salon marocain's tower is the whole room as the
  plans draw it (the façade gauche draws it 1.6 m shorter); the portal's arch is 1.40 m as the façade draws it
  (the plan's opening is 1.14 m); the façade principale is drawn mirrored (its stair on the wrong side): the plans
  win; the window of the salon marocain over the stair is set high (sill +2.05) to clear the treads.
- **Placement**: the 13 type C villas of the plan de masse 31-05-13 (the block south-west of the southern block:
  two rows of six, C-01 to C-12, and C-13 turned in the corner on the south road), each where the plan draws it:
  the plan's house outline is the drawing's house to the centimetre (15.38 x 12.15 m), so each villa sits on it,
  its front (portal) on the side of the plan's two terraces, its pool behind, its stair on the side of the plan's
  stair mark (all 13 the mirrored model). Plots and gardens from the plan's lines as for type B (not the parking
  strip in front of the south row's fences). Gates: on the front for the villas whose front is on a street
  (C-06, C-12, C-13), else on the side, past the stair, on the street between the two rows; the path runs along
  the front of the house to the portal. Each villa at the height of its centre, its lawn flat (+0.07, the pool
  coping +0.10, the terraces +0.20), held by its walls.
- **Levels (client 23-10, "tala3 l ard chwiya", "wssal l ard lhad mostawa bach dji m3a bab")**: the type C block
  and its streets out to the boundary are graded on Tranche 1's plane like the other blocks. On the natural
  ground the land falls about 10 m from the street between the two rows to the south road: the streets lay
  up to 9 m under the gardens and their gates, C-13 stood on a high platform with a void beside it. Now the
  streets come level with the gates (the plane falls about 4 % across the block) and the real terrain round
  the site is moved to meet the boundary there.
- **SPA** (`15_spa.py`), since 23-10 from its permit drawing `7-SPA-A0-1.pdf` (client: "ha huwa plan dyal SPA";
  rez-de-chaussée with its grid 1-9 / A-I, terrasse / masse, the four façades, coupes A-A and B-B). It replaces
  the design suggestion of 22-10 (the riad with its courtyard, closed as a pool hall on 23-10, its tower removed).
  A single storey (floor +0.20, roof terrace +4.20, parapet +5.20) on the plan's SPA lot, the pools on the
  cell's west side, the back on street 5: the main block 37.6 x 13.65 m (axes 1-8), on its front a glazed wall
  each side of the centre (9 leaves, louvred transoms over glass doors to +2.04) with the indoor pool (14.85 m)
  behind the southern one, on its back two pairs of tall windows in framed stone surrounds; the centre block
  (accueil, fontaine) 7.00 x 6.40 m, 1.29 m proud of the front, rising to +7.20 with the villas' cornice, the
  horns, six square niches, the studded door and transom in a taupe alfiz, a tall framed window each side; the
  roof terrace with the parapet, rounded coping and horns, the two domes of the bassin halls, four cantilever
  parasols with loungers, the outside stair past axis 8 (1.35 m wide, solid parapet); the lot paved round it, the
  two outdoor pools (16.6 x 3.35 m) along the front either side of the entrance path, loungers and parasols at
  their ends as the masse draws them. The façade principale is drawn as from the back (its stair on the wrong
  side): the plans win, as for the villa type C.
- **Fixes (client 23-10, "remove this / fix this")**: the island with its turning circle that the old plan drew in
  the street east of the SPA is gone (street), the SPA's cell keeps only its 0.40 m of pavement round its walls;
  the small notch in C-12's front fence (and C-05's) is filled, so no piece of high wall stands in the low front
  wall; where a lane opens onto a street's pavement (B-03/B-06, B-09/B-11, B-11/B-15, B-15/B-18, C-01/C-07) the
  pavement stops square on the lines of the gardens' side fences, with no wedge into the lane and no slanted end.
  Nothing else in the layout changed (the gates, gardens, stair, bays and kiosks are as on 22-10).
- **Roads in D5 (client 23-10, "3lach ka7la wakha fiha texture")**: the roads showed black in D5 from afar and
  grey close to, though they carry the same `T17_Pavers_Beige_Herringbone` as the pavements. Their meshes had
  triangles of up to 1,700 m2, and D5 kept the old asphalt look on the objects of the same name. In the D5
  package they are now `GROUND_ROADS_BEIGE_T1_T2` and `GROUND_ROADS_BEIGE_ENTRANCE`, cut on a 3 m grid (same
  surface, same material, same UVs). Delete the old model in D5 completely before importing.
- **The corner on the south road (client 23-10, "remove this and redo it with the road")**: the plan's 13th type C
  villa (C-13, turned in the corner on the south road) and the planted V beside it are left out; that corner,
  between the fences of C-10 to C-12 and the south road, is street (about 1,200 m2), with the 0.40 m of pavement
  along the fences as on the other streets. C-11's and C-12's fences there are brought back 0.6 to 0.9 m onto
  the line of the row's other fences, so the wall along the road runs straight. 12 type C villas remain.
- **Pavements apart from the roads (client 23-10, "fslom bach nt7akm fihum")**: Tranche 2's pavements (trottoirs,
  the strips along the fences, the islands of the south road, round the kiosks) are in their own material
  `T27_Trottoirs_Grey` (the grey pavers) and their own D5 object `GROUND_TROTTOIRS_T2`, no longer the roads' T17;
  the stair between the blocks stays beige.
- **Islands in the corner road (client 23-10, "zid 7ta hadi f7al hakda trotoire")**: the two islands of grey
  pavement the plan draws in the south road in front of C-08 and C-09 go on in front of C-10, C-11 and C-12 (the
  same island, 16.6 x 1.95 m, moved along the row by the villas' step, about 3 m off the fences). Along C-11's
  and C-12's fences the 0.40 m of pavement is now there (a strip of about 18 m2 was left neither street nor
  pavement when their fences were straightened).

- **Stairs closed (client 24-10, "chud hadiya 7ta hadi")**: the villas type C's outside stair is solid down to the
  ground (the void under its flight showed as a dark slot along the house); the SPA's landing has its end wall
  against the main block's parapet (it was open there, a slot between the two parapets).

## Tranche 3: the hotel and the villas type A (23-10)
Client 23-10: "zid db had tranche kayn fiha hotel and villa type a ... for hotel we dont have plan so i want you
to be creative and give me proposition ... the same style we have on our residence ... not the same design ...
the perfect one". The zone circled in blue on the plan de masse 31-05-13, west of the SPA and of the type C block.
- **Data** (`18_extract_t3.py` -> `data/t3_site.json`): the plan's 'zoning' and '012' lines polygonised in the
  plan's own frame: the four lots of the villas type A west of street 7 (826 to 887 m2) and the passage between
  the second and the third (a footpath between two planted strips); the hotel's plot between street 7 and the
  parking (4,939 m2: the two buildings' cells, the crossing between them, the long basin with its arm, the strip
  along the basin with its inlet from street 7, the garden); the parking along the hotel's east side, one bay per
  tooth of the plan's zigzag; the rest of the tranche is street (street 7, the Voie Publique, the south road) with
  the 0.40 m of pavement along the fences (grey, `T27_Trottoirs_Grey`, as Tranche 2's). Graded on Tranche 1's
  plane like Tranche 2 (the plane falls about 4 % along the hotel).
- **Villa type A** (`16_villa_a.py`), since 24-10 from its permit drawing `VILLA_TYPE_A.dwg` (client: "sla7 villa
  type a because machi hadchi likaynin f plan and face principal"; REZ DE CHAUSSEE, TERRASSE, PLAN MASSE, the four
  façades, coupes A-A and B-B). It replaces the model of 23-10 read from the plan de masse's drawing. A
  single-storey kasbah house round a patio, in the style of the villa type C:
  - four battered towers at the corners (salon and kitchen on the north, Chambres I and III on the south), walls
    leaning in 0.254 m over 4.06 m, grooves at 0.53 / 1.41 / 2.29 / 3.17, square niches under the cornice (grey
    ledge / ochre band / grey ledges, 4.06 to 4.44), parapet +4.80 with the rounded coping and the horns (+5.22),
    roofs +3.92 with a door in each parapet onto the central roof terrace;
  - the central band (coin cheminée to the north, the hall, Chambre II to the south) with plumb walls and its
    parapet +4.70 (+4.55 on the north protrusion), its roof terrace reached by the outside stair along Chambre I
    (21 risers, solid, the local technique under its landing with its door on the south); the patio in its middle,
    a garden glazed on its four sides;
  - over the hall the entrance block to +6.20 with its horns: on the entrance terrace (street side) the studded
    portal 1.85 x 3.79 with its studded panel over it, the doors onto the roof terrace on its north and south
    faces; the chimney of the coin cheminée with its rounded top and oculus (DETAIL 2);
  - on the pool side the salon's and Chambre I's 4-leaf glazing in their stepped stone surrounds, the west terrace
    between them with its parasol and table before the patio's glazing; on the street side the entrance terrace
    between the two towers with its benches, the planters along the east fronts and either side of the entrance;
    the pool 5.00 x 16.47 m over its coping (water 4.00 x 15.47 m), the deck along the house.
  The façade droite is drawn mirrored: the plans win. Each villa where the plan de masse draws it, its garden flat
  at the house's height, its walls as Tranche 2's (1.80 m, a low stone-clad wall on street 7 with the gate pillars
  and timber gate on the entrance terrace's axis, a paved path between the planters to it).
- **The hotel** (`17_hotel.py`) — **a design proposal, there is no plan**. It keeps the plan's zoning of the plot
  and builds, in the residence's materials but in forms of its own, two buildings and a domed pavilion on a water
  garden. **Client 24-10**: the SPA is right; the hotel's buildings looked like permit drawings, ordinary, front
  and back; one height right and left, two storeys (or close), the SPA's style and spirit, keep the middle of the
  old design, no new architects. So the gate pavilion on the crossing (the middle) is kept exactly as it was, and
  both buildings are redone at two storeys and one height (floor +0.20, first floor +4.20, roof +7.80, parapet
  +8.80 over each block's floor; the blocks step with the 4 % ground), with the SPA's elements: taupe stone
  pilasters, the louvred glazing, the tall windows in their double stone frames, the studded door and transom in
  its taupe alfiz, mashrabiya, domes:
  - the main building (north cell, 14.1 x 45.5 m, stepping down 0.9 m at mid-length with the ground): on the Voie
    Publique its gate block 1.30 m proud, rising to +10.40 with its horns, the pointed horseshoe arch (3.60 m) in a
    taupe alfiz framed in green zellige, studded doors under a mashrabiya tympanum, steps down inside; in each half
    a centre block 0.90 m proud on the garden and on the parking, rising to +9.40, with the SPA's studded door,
    tall windows and a row of niches; taupe pilasters between the bays; on the garden the SPA's louvred glazing
    (lobby, restaurant) on the stone terrace with its balustrade and flights of steps, upstairs french windows in
    turn behind cedar mashrabiya screens and onto stone balconies with cedar railings; on the parking and at the
    ends the SPA's tall windows; domed towers at the southern corners; on the roof terraces a dome on its drum,
    parasols and loungers, the cedar pergola;
  - the gate pavilion on the crossing between the two buildings: a domed qubba (7 x 7 m, dome to about +10.5 with
    a bronze finial), pointed horseshoe arches east (from the parking) and west (onto the arm) in taupe alfiz
    framed in zellige, blind zellige arches north and south, a fountain inside;
  - the suites (south cell, 13.3 x 56.4 m, two storeys, as high as the main building): fourteen in four level
    blocks (4, 3, 3, 4) stepping with the ground, taupe pilasters between the suites, the SPA's louvred glazing
    onto each terrace on the garden behind low walls under a cedar pergola, a french window onto a stone balcony
    upstairs, the door and tall windows on the parking side; two domed towers at the corners facing the pavilion,
    a dome on its drum on each other block;
  - the water garden: the long basin (7.1 x 53.7 m) in three basins stepping 0.59 m down the slope, the water
    running over two weirs, and its arm (5.0 x 15 m) on the crossing's axis, whose head under the pavilion is a
    zellige wall with three bronze spouts; green zellige, travertine decks with loungers, parasols and date palms,
    stone kerbs where the lawn stands higher or lower; the strip along the basin is a promenade in beige pavers
    under Washingtonia palms from the garden gate on street 7 (a block with its arch, studded doors, cornice and
    horns) on the arm's axis; olive trees and date palms in the lawns; walls (2.00 m) on the streets.
  Collections `T3_01_GROUND`, `T3_02_VILLAS`, `T3_03_LANDSCAPE`, `T3_04_TREES_PALMS`, `T3_05_HOTEL`
  (`19_tranche3.py`); the ground joins Tranche 1 and 2's objects in the D5 package.

## Removed (client, 13-10)
Direction arrows and cars. The zebra crossings were put back as paint (15-10).

## Not on the drawings (to confirm)
- **Heights not given**
  - Commerces: set to the restaurant's heights at the client's request (rev 4); their own drawings give none.
  - Toilet block: 3.20 m.
  - Technical block: 3.00 m.
- **Commerce stairs**: modelled going down to the sous-sol, which the light wells point to.
- **Walls**: garden walls 1.80 m; pétanque and boundary walls 1.20 m.
- **Ground between the pool and the restaurant terrace**: lawn on the plan, paved at the client's request (15-10), in beige tiles since rev 4. The upper walk and the planted stone terraces lie between it and the gradins.
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
- **Colours** (rev 4, 19-10): one sand render (#C8AA86) for every building, duplexes, restaurant, commerces and all towers, matched to the client's photos (the built kasbah tower and the villa renders). The bejmat stays only in the portal frames.
- **Villa N°09, choices where the drawing's views differ** (rev 4, to confirm):
  - The side-part first floor has one window (façade principale and reference image); the plan draws two small bathroom windows.
  - The stair cage is the size of the plans and section (3.09 m per villa, 3.93 m deep); the façades draw it larger.
  - The salon side window is placed from the plan (0.65 m from where the side façade draws it).
  - The wing's acrotère is at +8.30 as the façades and section draw it; the side façade also carries a '+07.90' label there.
  - The rear terrace piers follow the plans (0.80 m wide in the middle); the rear façade draws narrow posts.
  - The pergola heights follow the façades (+6.90 rear, +7.20 front); the section draws them a little lower.
  - The terrace separation walls go up to the pergolas as the drawing draws the joint; their height is to confirm.
  - The front garden wall runs from the gate to 0.60 m past the house and turns back 1.5 m; the lot widths are not on the drawing.
- **Tile and paver textures** (rev 4): drawn to look like the references (`data/textures/`), not the manufacturers' own images. In D5 the real product textures can replace them (`T18_Tile_Ardesia_Beige`, `T19_Tile_Jade_Green`, `T17_Pavers_Beige_Herringbone`).
- **Villa type A**: the patio's glazing on its north, south and east sides and the windows of the salon and Chambre I onto the west terrace are read from the RDC plan (no façade shows them).
- **Hotel**: a design proposal (no plan): everything about it is to confirm. Since 24-10 "le milieu" is read as the domed gate pavilion on the crossing (kept); if the client meant another part of the old design, it can be swapped.
- **Not modelled**: interiors, the sous-sols, the other tranches (beyond Tranches 2 and 3), and the RN road outside the boundary.

## Renders
| Camera | View |
|---|---|
| CAM_01_AERIAL_T1 | Aerial view of the tranche |
| CAM_02_AERIAL_FROM_WEST | The tranche from the west, with the empty land |
| CAM_03_POOL_COURT | The pool court from its south-west corner, towards the gradins, the terraces and the restaurant |
| CAM_04_RESTAURANT | The restaurant pavilion, portal and fountain |
| CAM_05_COMMERCES_PLAZA | Commerces and their terrace, from above the plaza |
| CAM_06_LANE_ROWS | Along a beige-paved lane between the duplex rows |
| CAM_07_DUPLEX_A_HERO | A D-5…D-24 pair from its lane (D-17 / D-18) |
| CAM_08_DUPLEX_B_D1_D2 | D-1 / D-2 from their access side |
| CAM_09_PETANQUE | Pétanque courts and pergola |
| CAM_10_ENTRANCE_FOUNTAIN | Entrance from the ring road: paved median, crossings, fountain, restaurant and commerces |
| CAM_11_GARDENS_BIRDSEYE | Bird's-eye view of the gardens and roofs |
| CAM_12_TOP_PLAN | Orthographic top view, to compare with the plan de masse |
| CAM_13_STAIR_ESC_V4 | The stair 'ESC V4' across row C, looking down it from the upper lane |
| T2_CAM_01_AERIAL | Tranche 2: aerial view of its two blocks of villas type B |
| T2_CAM_02_VILLA_B_FRONT | A villa type B from its street (B-14) |
| T2_CAM_03_VILLA_B_GARDEN_POOL | Its garden and pool |
| T2_CAM_04_NORTH_STREET | A street of the northern block |
| T2_CAM_05_SOUTH_BLOCK | The southern block from above |
| T2_CAM_06_GATE | The front wall, gate and path of a villa |
| T2_CAM_07_PARKING_CENTRE_ENTRETIEN | The parking strip, its bays and the Centre d'entretien |
| T2_CAM_08_VILLA_C_FRONT | A villa type C from its street (C-12) |
| T2_CAM_09_TYPE_C_AERIAL | The type C block from above |
| T2_CAM_10_SPA_ENTRANCE | The SPA's front, its centre block and pools |
| T2_CAM_11_SPA_POOLS | Along the SPA's outdoor pools |
| T3_CAM_01_AERIAL | Tranche 3: the hotel and the villas type A from above |
| T3_CAM_02_HOTEL_GATE | The hotel's gate on the Voie Publique |
| T3_CAM_03_HOTEL_WATER_GARDEN | Along the long basin, the decks and the palm promenade |
| T3_CAM_04_HOTEL_PAVILION | Down the arm to the gate pavilion between the two buildings |
| T3_CAM_05_HOTEL_SUITES | The suites and their terraces on the garden |
| T3_CAM_06_VILLA_A_STREET | A villa type A from street 7 (A-02) |
| T3_CAM_07_VILLA_A_POOL | Its pool and terrace |

**Lighting**: the sun at 10:15 on 15 October, at the site's latitude and longitude, through a Nishita sky. The view transform is AgX Punchy.
