# PROJECT BIBLE — Mirleft Bay (Playa Village Mirleft)

Status tags: **[CONFIRMED]** stated in a source · **[INFERRED]** derived from sources with reasoning · **[ASSUMED]** my default, no source · **[MISSING]** not available · **[CONFLICTING]** sources disagree.
Source IDs (F01…F07) refer to `PROJECT_INVENTORY.md`. Version 0.3 (2026-10-01): blocking answers received, model built (see PRODUCTION_STATUS).

CLIENT STATEMENT (2026-10-01): "this is what I have on informations": no dimensioned plans, elevations, sections or DWG exist beyond F01–F08. Villa geometry is therefore **INFERRED** (catalogue plans + photos + permit areas), never presented as surveyed.
INTERIOR_DOCUMENTATION: **PARTIAL** (catalogue room layouts and areas for one villa type, no dimensions)
INTERIOR_ACCURACY: **APPROXIMATED** (cinematic approximation only, unless dimensioned plans arrive)

## 01_PROJECT_OVERVIEW
Tourist residential resort (RIPT) with a 3-star hotel, on an 8.2 ha coastal plot above a beach near Mirleft, Province of Sidi Ifni, Morocco [CONFIRMED F01]. Marketed as "Mirleft Bay" [CONFIRMED F02]. Partly built: at least one villa and one kasbah building exist on site [CONFIRMED F04, F07].

## 02_PROJECT_TYPE
Gated resort: duplex houses, detached villas (types A/B/C), hotel, club house / restaurant, supérette, administration, pools, artificial lake, shared landscape [CONFIRMED F01]. Marketing adds spa, beach club, market, conference room, sports ground, chiringuito, slow working [CONFIRMED F02] → see §43 C1.

## 03_SITE
Lieu-dit Atblkoukte, Commune rurale de Mirleft. TF 11512/31 [CONFIRMED F01]. Location ≈ **29.553° N, 10.060° W**, west of road R104, south-east of Playa de Tamajarusch / Tamahroucht beach, near Kasbah Tabelkoukt [CONFIRMED F08 Google Earth; centroid ± 100 m INFERRED from the screenshot]. Elongated plot from the beach (west) to the provincial road (east), between two ravines [CONFIRMED F01]. Bare ochre semi-desert, low scrub, Atlantic cliffs and beach [CONFIRMED F03].

## 04_SITE_BOUNDARY
Plot polygon drawn on F01, contenance 82 070 m² [CONFIRMED]. Digitised extent ≈ 650 × 100–220 m [INFERRED, scale verified to −2 %]. Client's Google Earth hand trace: 78 412 m², perimeter 1 435 m, length ≈ 695 m [CONFIRMED F08, hand trace, −4.5 % vs title]. The **plan raster stays the geometry source**; Google Earth gives the orientation and the terrain context. Exact boundary coordinates (survey points B1–B16 are visible) [MISSING as numbers → digitise from the raster, ± 0.3 m].

## 05_ORIENTATION
No north arrow on F01, but the client's Google Earth trace (F08) fixes it: the long axis runs at a bearing of **122.5°** (beach end WNW at 302.5°, road end ESE at 122.5°) [CONFIRMED F08: plan boundary fitted to the client polygon at fixed 1/500 scale, IoU 0.82, ± 1°]. On the plan, the ocean is on the left → **plan +X (towards the road) = bearing 122.5°, plan up = N32.5°E** [INFERRED from F08 ± 1°]. The beach end gets the sunset light: the golden-hour sun sets at about 250–295° depending on the season.

## 06_COORDINATE_SYSTEM
Blender: metres, Z up, **+Y = true north**, +X = east. The plan raster is placed rotated so that its long axis lies at bearing 122.5°. Origin = site centroid (matches the Google Earth polygon centroid) [INFERRED]. Geographic anchor 29.553° N, 10.060° W (for the sun position) [INFERRED F08]. No Lambert Maroc coordinates on the plan [MISSING, not needed for visualisation].

## 07_TERRAIN
Slopes down from ≈ 62 m (road) to ≈ 8–18 m (beach edge) over ≈ 650 m, i.e. about 6–8 % average, with ravines north and south [CONFIRMED spot heights F01]. Google Earth elevations over the traced polygon: min 18.72 m, median 51.28 m, max 64.99 m [CONFIRMED F08], consistent with F01. Inside the plot the levels are hidden under the colour tint [MISSING] → interpolate from the boundary spot heights and contours [INFERRED]. Platforms / terracing per villa [MISSING].

## 08_TOPOGRAPHY
Contours every ≈ 5 m with spot heights (e.g. 60.97, 61.70, 57.45, 59.39, 45.21, 40.00, 33.15, 28.92, 18.46, 15.00, 12.93) [CONFIRMED F01]. A DWG/topographic survey would replace digitising [MISSING].

## 09_BUILDING_MASSING
**Scope (client, 2026-10-01): the whole site at massing level + one detailed hero villa (Tranche 1 duplex).**
Footprints readable on F01 for every building at 1/500 (≈ 0.13 m/px) [CONFIRMED]. Heights: RDC = 1 storey, RDC+1 = 2 storeys [CONFIRMED]. Storey heights, parapets, roof terraces [MISSING]. Kasbah towers taller than the main body [CONFIRMED F04].

## 10_FLOOR_LEVELS
Not given anywhere [MISSING]. Default if not supplied [ASSUMED]: floor-to-floor 3.10 m, ground slab +0.30 m above the platform, parapet 1.10 m, rooftop stair house +2.60 m.

## 11_DIMENSIONS
Plot and road widths [CONFIRMED F01]: main public road 12 m; internal roads 14, 10, 8, 7, 6.2, 6, 5 m; roundabout ≈ 50 m (at the east entrance, outside the plot). Unit gross areas [CONFIRMED F01]: duplex 124 m², villa B 164 m², villa C 145 m², villa A 220 m². Villa dimensions (wall to wall) [MISSING]: catalogue plans are unscaled. Room areas [CONFIRMED F02 p8].

## 12_ROOM_LAYOUT
Catalogue villa (type uncertain, §43 C2) [CONFIRMED F02 p8]: RDC living/dining 31 m², kitchen 8.5 m², bedroom 1 with bathroom 18 m², guest WC 4 m², private garden (L-shaped, up to 100 m²). First floor: bedrooms 2 and 3 (14 m² each), bathroom 6 m², terrace 24 m² under a pergola. Roof terrace 47 m² with jacuzzi. Other types [MISSING].

## 13_WALLS
Thick rendered masonry, sand-coloured [CONFIRMED F04, F07]. Thickness [MISSING]; ASSUMED 0.30 m exterior. Decorative square wall niches ≈ 0.15–0.20 m in a row at mid-height [CONFIRMED F07]. Kasbah: tapered towers, stepped crenellations, chevron relief motifs [CONFIRMED F04].

## 14_SLABS
Flat roofs with parapets and roof terraces [CONFIRMED F02, F07]. Thicknesses [MISSING]; ASSUMED 0.25 m.

## 15_WINDOWS
Large sliding glass doors with deep projecting frame surrounds (≈ 0.15 m darker render or stone band) [CONFIRMED F06, F07]. Narrow vertical windows in recessed bays on the kasbah [CONFIRMED F04]. Dark bronze / brown aluminium frames [CONFIRMED F07]. Exact sizes [MISSING].

## 16_DOORS
Entrances [MISSING] (not visible in any source). Arch portal (horseshoe/Moorish arch) on the entrance plaza building [CONFIRMED F05].

## 17_STAIRS
Interior stair visible in the catalogue plans [CONFIRMED F02]. Exterior stairs between landscape levels shown in the Pavillon render [CONFIRMED F02 p10, render only].

## 18_ROOF
Flat roofs, rooftop terraces with pergola, jacuzzi on the roof terrace [CONFIRMED F02]. Kasbah crenellations [CONFIRMED F04]. Waterproofing finish [MISSING]; ASSUMED light gravel / tiles.

## 19_BALCONIES
First-floor terrace with a timber lattice guardrail (geometric Moroccan pattern) [CONFIRMED F06]; the built villa uses a solid rendered parapet instead [CONFIRMED F07] → [CONFLICTING] render vs as-built, minor.

## 20_TERRACES
Ground-floor stone terrace off the living room, 1st-floor terrace 24 m² with pergola, roof terrace 47 m² [CONFIRMED F02].

## 21_POOLS
Private pool per villa B (rectangles on the plan) [CONFIRMED F01]. Villa A long pools [CONFIRMED F01]. Club house pools: two free-form + kids' pool in Tranche 1 [CONFIRMED F01]. Pavillon pool facing the ocean [CONFIRMED F02]. Artificial lake: three free-form basins + circular feature, Tranche 6 [CONFIRMED F01]. Depths and finishes [MISSING]; ASSUMED light sand mosaic.

## 22_DRIVEWAYS
Internal asphalt road network with the stated widths, parking bays along the roads [CONFIRMED F01]. Paving material: grey-beige concrete pavers on the built road [CONFIRMED F04]; red brick pavers in the render [CONFIRMED F05] → [CONFLICTING], see C5.

## 23_PATHS
Pedestrian paths between villas, sea-front promenade (corniche) at the beach end [CONFIRMED F01]. Materials [INFERRED from F04/F07]: beige concrete pavers.

## 24_LANDSCAPE
Shared green spaces, garden per villa, lawn + hedges [CONFIRMED F06/F07, plan]. Planted "borne paysagère" along the beach edge [CONFIRMED F01]. Native terrain around the plot: bare ochre soil with scrub [CONFIRMED F03].

## 25_VEGETATION
Washingtonia fan palms (as-built, F04/F07) [CONFIRMED]. Date / Canary palms, olive trees, ornamental grasses (Pennisetum-type), lawn, hedges (Pittosporum-type), bougainvillea [CONFIRMED in photos F04 / renders]. Argan and euphorbia for the native context [INFERRED: Souss-Massa coast]. Final species list [MISSING / INFERRED].

## 26_MATERIALS
See `ASSET_REQUIREMENTS.md`. Core palette [CONFIRMED F04/F07]: sand-ochre lime render, darker ochre recessed panels, timber pergolas, warm rubble stone walls, bronze aluminium, clear glass, beige concrete pavers, asphalt, lawn, ochre soil.

## 27_TEXTURES
External PBR libraries (Poly Haven, ambientCG) are **blocked by this environment's network policy** (HTTP 403 on CONNECT, re-tested 2026-10-01 after the client sent the Poly Haven API docs) [CONFIRMED]. The client wants Poly Haven used (API docs supplied) → the environment's network settings must allow `api.polyhaven.com`, `dl.polyhaven.org`, `cdn.polyhaven.com`. Until access is opened: procedural / generated textures, labelled APPROXIMATED (in use, see assets/TEXTURE_MANIFEST.csv).

## 28_FURNITURE
Exterior: loungers, round dining table + chairs, stone fire pit, outdoor sofas on the roof [CONFIRMED F06, F02 p8]. Interior: warm wood, bouclé sofas, linen [CONFIRMED F02 p8–9].

## 29_PROPS
Umbrellas, pool loungers, pergola cabanas at the Pavillon [CONFIRMED F02 p10]. Lanterns, planters [INFERRED].

## 30_PEOPLE
Lifestyle people in the catalogue (couples, surfers, diners) [CONFIRMED F02]. In Blender renders: few or none [ASSUMED]. People motion is better done in Higgsfield (§40).

## 31_VEHICLES
Parked cars in F05 and the plan [CONFIRMED]. Optional, low priority [ASSUMED].

## 32_LIGHTING
Brand mood = golden hour / warm sunset [CONFIRMED F02 p1, p7, p10, p13]. The as-built photos are midday, clear blue sky [CONFIRMED F04/F07]. **Master look = golden hour** [CONFIRMED by the client 2026-10-01]. Sun from the WNW–W over the ocean, low (3–12° elevation), warm haze; computed for 29.553° N, 10.060° W. The other five presets (daylight, morning, sunset, blue hour, night) stay secondary.

## 33_COLOR_PALETTE
Render sand #C9A77D (albedo, INFERRED from sunlit #D1B18B / shade #99824F), recessed ochre #B39175, timber #BC9E7B, stone #BA6F4B, bronze #433C37, pavers #C8AD94–#D6CABA, brick pavers #A05D48 (render only), ocean teal, sky blue.

## 34_ARCHITECTURAL_STYLE
Contemporary southern-Moroccan / kasbah-inspired: simple cubic volumes, thick rendered walls, small square niches, tapered pylons, crenellations, horseshoe arches on public buildings, timber pergolas [CONFIRMED F02, F04–F07]. "Volumes simples, matières naturelles, lumière constante" [CONFIRMED F02 p7].

## 35_PHOTOGRAPHIC_STYLE
Warm, soft, slightly hazy golden-hour photography; natural contrast; editorial luxury real estate [CONFIRMED F02].

## 36_CINEMATIC_STYLE
Slow, calm, contemplative ("Un moment de vie. Rien d'autre.") [CONFIRMED F02 p1]. Slow drone drifts, gentle push-ins, ocean as the constant backdrop [INFERRED].

## 37_CAMERA_LANGUAGE
**Delivery format: vertical 9:16** [CONFIRMED by the client 2026-10-01], e.g. 1080 × 1920 (hero frames 2160 × 3840). Vertical framing favours tall subjects (palms, kasbah towers, pergola + sky), top-down drone reveals and slow vertical crane moves.

Proposed (to be validated after scope): 24–35 mm aerials and establishing shots, 35–50 mm human-scale villa and pool shots, 50–75 mm details (niches, pergola shadows, stone). Vertical lines kept straight on architecture shots. Shot list in the discovery report; written to `output/higgsfield/02_SHOT_LIST.md` after scope is fixed.

## 38_RENDERING
Machine available here: 4 CPU cores, no GPU, 15 GB RAM [CONFIRMED]. Cycles stills are feasible (≈ 1–5 min per 1080p frame at moderate samples). Long Cycles animations are not realistic here → video motion via Higgsfield, or rendering on the user's own PC [INFERRED].

## 39_D5_STRATEGY
D5 Render runs on Windows with a GPU, so it cannot run in this cloud session [CONFIRMED tool limits]. If MODE A: deliver a clean FBX/GLB + D5 guides, the user renders in D5. **Not used: MODE B selected by the client (2026-10-01).** D5 guides are not produced.

## 40_HIGGSFIELD_STRATEGY
The Higgsfield connector is available in this session (image-to-video generation, credits apply) [CONFIRMED]. Use it only on Blender hero frames, for motion: palms, water, people, light. Exact-architecture shots stay as Blender stills or camera moves [INFERRED].

## 41_ASSUMPTIONS
A1 storey height 3.10 m · A2 exterior walls 0.30 m · A3 slab 0.25 m · A4 parapet 1.10 m · A5 plan up = north · A6 the catalogue villa = Tranche 1 duplex (124 m² covered, 150 m² including terraces?) · A7 terrain interpolated from the boundary spot heights · A8 pool finish light sand mosaic · A9 F04 kasbah = administration / reception near the entrance. Each one waits for confirmation.

## 42_MISSING_INFORMATION
See `MISSING_INFORMATION.md`.

## 43_CONFLICTS
- **C1** Program: **RESOLVED 2026-10-01**: the catalogue 2026 is the truth for the programme and names; geometry and positions come from the scaled permit plan. Was: the permit (2013, approved 2016) lists club house, supérette, administration, hotel 3★, lake. The catalogue (2026) shows Restaurant Pavillon, market, two spas, beach club, conference room, sports ground, chiringuito, "La Plage" boutique hotel ~30 suites, 4 cliff villas. 
- **C2** Unit type and area: the catalogue's "24 villas, 150 m² habitable, R+1 + rooftop" matches the permit's 24 duplex (RDC+1) of 124 m² covered each? Or villa type B (164 m²)? **RESOLVED 2026-10-01: Tranche 1 Duplex** (paired R+1 houses with rooftop, 124 m² covered each; the catalogue's 150 m² is read as habitable area including terraces [INFERRED]).
- **C3** The F04 kasbah building and the F05 portal building are not identified on the plan.
- **C4** The Pavillon render (p10) shows a mountain backdrop and terraced stone retaining walls (AI-style render) that the plan does not confirm.
- **C5** Paving: beige concrete pavers (as-built F04) vs red brick pavers (render F05).
- **C6** First-floor guardrail: timber lattice (render F06) vs solid parapet (as-built F07).

## 44_VALIDATION_RULES
V1 footprints within ±0.3 m of the plan raster (1/500 scan) · V2 unit gross areas within ±3 % of the permit table · V3 storey count per building = table · V4 road widths = circled values · V5 terrain matches spot heights within ±0.5 m at the sampled points · V6 materials at real-world texel scale (paver ≈ 0.20 m, render grain mm-scale) · V7 no camera inside geometry, verticals kept straight · V8 top/front/side/perspective validation renders compared with F01, F06, F07.
