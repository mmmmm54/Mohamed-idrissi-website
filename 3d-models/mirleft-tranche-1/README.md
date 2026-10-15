# Mirleft: 1er TRANCHE (plan de masse 12-10), detailed; rest of the site as empty land

This is a Blender model of the 1er TRANCHE of the Mirleft project, built from the new plan de masse **MASSE_12-10_MIRLEFT**. It includes:
- 12 duplex pairs, D-1 to D-24, with their gardens, garden walls, front pavements and planters
- the restaurant, Commerce 1 (superette) and Commerce 2 (glacier), and the toilet block on the plaza
- the sunken pool court (pool, children's pool, stepped seating, stairs, ramp, technical block)
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
  - D-3/D-4 have the 1 m paved band drawn around the house. No garden wall runs on it: the gardens open onto the band.
- **Both duplex types**
  - The plan draws lawn up to the house, so the permit's ground-level rear pergola and rear terrace are not built.
  - The dimensions are the permit's. The plan's block is about 2 % larger, so each pair is aligned on its front façade line.
- **Gardens and walls**
  - The gardens are the plan's lawn hatches. Walls run along the garden edges, except the edges that face the house.
  - The 'JARDIN' plots beside D-4 are drawn 0.6 m into that house's band. Their wall stands on the band's edge instead.
  - The 'Jardin' beds on the pavements are raised planters.
  - The 57 circles of Ø 1.2 m ('1.2m') on the front courts are tree pits, with a kerb ring and soil.
  - There are 20 meter cabinets ('Emplacement compteur') and 7 bin enclosures, at the plan's positions.
- **Ground surfaces** (from the hatches)
  - The 6 m lanes, the commerce road and the parking aisles: charcoal herringbone pavers ('AR-HBONE').
  - The restaurant terrace and plaza: light herringbone.
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
  - The platform: front bassins with planters, the bridge, the cour anglaise, the rear terrace and its bassin, and the timber pergolas at the rear corners.
  - It stands on the axis of the 12-10 restaurant block, moved 1.30 m back so the whole platform fits the plan's TERRASSE RESTAURANT.
  - Six trees of the 12-10 layout fall in its bassins or pergolas or against its walls. They are left out.
- **Commerces**
  - The four towers ('départ tours') and the two bodies.
  - The north block of Commerce 2.
  - The light wells to the sous-sol ('vide d'aération sous sol').
  - The entrances on the east side (from the plan's arrows), and the two stair runs.
- **Pool court**
  - The basin is 21.71 × 7.50 m, with Roman steps in two corners. The children's pool is 9.6 × 3.8 m.
  - 32 loungers ('TRANSATS'), at the plan's positions.
  - Stepped seating ('GRADINS') flanked by two stairs of ten steps ('ESCALIERS PISCINE', numbered 1-10).
  - Four planters with palms ('LES BACS A FLEURS').
  - The ramp along the south ('RAMPE'), the planted bed along the north, the pool cover reel ('COUVERTURE PISCINE AMOVIBLE'), four shower columns.
  - The technical block (toilettes H / F, local technique, bâche à eau), from its drawn walls.
- **Pétanque**: two courts, the pergola, benches, the curved wall ('Mur') and the trees in the semicircle.
- **Entrance**: the median, the fountain (semicircle) and the ring road.
  - Median (revision 15-10): no water. The two beds the plan hatches are paved flush, in diagonal stripes of dark slate and light travertine like the hatch.
- **Pedestrian crossings** (revision 15-10): every crossing the plan draws, as flat white paint on the road.
  - Six at the entrance and median ('DFGW', 'xwdfrg').
  - Two on the 8.5 m road at the stair exits ('TRACAGE VOIRIE').
- **Trees**: at every tree symbol of the plan.
  - 98 small palms, 31 round-crowned trees on the plaza and terraces, and 4 palms in the pool planters.
  - 7 trees at the pétanque.
  - 57 trees in the Ø 1.2 m pits. The plan draws 31 of these pits against a façade, so those trees are clipped standards
    (a ball about 0.8 m wide on a 1.85 m stem) that stay clear of the wall. The other 26 are street trees.

## Levels
- **Ground**: the 1er TRANCHE is graded on one plane fitted to the contours, 5.5 % rising to the east.
- **Buildings**
  - Each duplex pair sits at the plane height of its centre.
  - The commerces sit at the level of their entrance side (east). The restaurant's platform deck is level with the highest ground at its edge. On the downhill side their plinths show.
- **Pool court**: sunk 1.70 m below the top of its gradins (four risers of 0.425 m, and the ten 0.17 m steps of the stairs).
  - The strip behind the gradins is levelled at that height and blends back into the slope over 10 m.
  - The other sides are retaining walls with a 1.00 m guard. The ramp climbs from the deck to the upper level.
- **Stairs** (revision 15-10): built stairs, filled wall to wall. Each step has a level tread, a vertical riser and a dark stone nosing. A handrail runs on the centre line over each flight.
  - The flights are where the plan draws them: 'ESC 16-17' and 'ESC V4' across the rows, and the long stair north of the pool.
  - The plan gives no levels. Each stair climbs the height the ground gives between its two ends, in risers of about 15 cm:

    | Stair | Height | Risers | Risers drawn |
    |---|---|---|---|
    | ESC 16-17 | 0.79 m | 5 × 0.158 m | 9 + 9 |
    | ESC V4 | 0.65 m | 4 × 0.163 m | 9 + 12 |
    | North of the pool | 0.58 m | 4 × 0.145 m | 10 + 11 |

  - The level walk between the flights takes the rest of the length.

## Removed (client, 13-10)
Direction arrows and cars. The zebra crossings were put back as paint (15-10).

## Not on the drawings (to confirm)
- **Heights not given**
  - Commerces: single storey to +4.40 with a crown to +5.20, towers to +8.10.
  - Toilet block: 3.20 m.
  - Technical block: 3.00 m.
- **Commerce stairs**: modelled going down to the sous-sol, which the light wells point to.
- **Walls**: garden walls 1.80 m; pétanque and boundary walls 1.20 m.
- **Ground between the pool and the restaurant terrace**: not hatched on the plan; modelled as lawn.
- **Stair heights**: the risers the plan draws (18 to 21 per stair) would need about 2.7 to 3.4 m of height. The contours show 0.6 to 0.8 m.
  - So the stairs follow the ground.
  - With the platform levels of the rows, the drawn risers can be built instead.
- **Median paving**: the material of the two beds is read from the plan's hatch.
- **Planting**
  - The plan gives tree positions, not species.
  - Small palms are modelled as date palms, the round symbols as olive-like trees, and the pool and pétanque trees as drawn.
  - The Ø 1.2 m circles are read as tree pits; the clipped standards against the façades are a choice.
  - The shrubs in the raised beds are added.
- **Colours**: the duplexes and building bodies use the sand render of the Mirleft Bay model. The towers' terre de sienne and bejmat come from the pavilion drawings.
- **Not modelled**: interiors, the sous-sols, the other tranches, and the RN road outside the boundary.

## Renders
| Camera | View |
|---|---|
| CAM_01_AERIAL_T1 | Aerial view of the tranche |
| CAM_02_AERIAL_FROM_WEST | The tranche from the west, with the empty land |
| CAM_03_POOL_COURT | The pool court from the top of the gradins |
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
