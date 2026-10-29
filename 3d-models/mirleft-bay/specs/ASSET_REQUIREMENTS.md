# ASSET REQUIREMENTS — Mirleft Bay (proposed, nothing procured yet)

Priority: HERO (close-ups) · HIGH · MEDIUM · BACKGROUND. Source status: `TO SOURCE` (CC0 library once network access is open) · `PROCEDURAL` (built in Blender) · `BLOCKED` (network policy) · `USER` (needs a user reference).
Network status on 2026-10-01: Poly Haven and ambientCG return 403 from this environment → every external item is **BLOCKED** until access is opened (MISSING_INFORMATION I6).

## ARCHITECTURAL MATERIALS

| ID | Name | Physical material | Location | Priority | Close-up | PBR | Displ. | Texture scale | Colour (sRGB) | Roughness | Reflect. | Direction | Reference | Source plan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M01 | Sand lime render | Hand-trowelled lime/cement render | All villa and public façades | HERO | YES | YES | micro-normal only | grain 1–3 mm, trowel waves 0.3–1 m | #C9A77D | 0.85–0.95 | very low | none | F04, F07 | ambientCG *Plaster* (CC0) + colour tint · fallback PROCEDURAL |
| M02 | Ochre recessed render | Same render, darker | Kasbah recessed bays, window surrounds | HIGH | YES | YES | no | as M01 | #B39175 | 0.9 | very low | none | F04, F06 | Derived from M01 |
| M03 | Pergola timber | Sawn softwood / iroko, oiled, weathered | Pergolas, lattice guardrails | HERO | YES | YES | no | board 0.10–0.20 m wide | #BC9E7B | 0.6–0.75 | low | grain along beam | F06, F07 | Poly Haven *wood planks* (CC0) |
| M04 | Rubble stone wall | Local warm sandstone, dry-laid look | Garden walls, retaining walls, Pavillon terraces | HIGH | YES | YES | YES (hero) | stones 0.15–0.40 m | #BA6F4B | 0.8 | low | horizontal courses | F07, F02 p10 | Poly Haven *stone wall* (CC0) |
| M05 | Bronze aluminium | Powder-coated aluminium | Window/door frames | HIGH | YES | YES | no | — | #433C37 | 0.35–0.45 | metallic 0.8 | — | F07 | PROCEDURAL |
| M06 | Clear glazing | Double glazing | Windows, sliding doors | HIGH | YES | — | no | — | clear, slight green | 0.02 | IOR 1.52 | — | F07 | PROCEDURAL (+ interior proxy behind) |
| M07 | Beige concrete pavers | Interlocking concrete pavers | Roads, paths, terraces | HIGH | YES | YES | YES (hero) | paver 0.20 × 0.10 m | #C8AD94–#D6CABA | 0.8 | low | herringbone / running bond | F04, F07 | ambientCG *PavingStones* (CC0) |
| M08 | Red brick pavers | Clay pavers | Entrance plaza (if C5 = render) | MEDIUM | NO | YES | no | 0.20 × 0.10 m | #A05D48 | 0.75 | low | herringbone | F05 | ambientCG *PavingStones* |
| M09 | Terrace stone | Honed limestone slabs | Ground-floor terraces, pool decks | HIGH | YES | YES | no | slab 0.60 × 0.40 m | #D8CCB8 | 0.6 | low | aligned to façade | F06, F02 p10 | Poly Haven / ambientCG *Tiles* |
| M10 | Pool mosaic + water | Glass mosaic, water | Pools, lake | HIGH | YES | YES | water displacement | tile 25 mm | sand/turquoise | 0.1 | refraction | — | F02 p10 | PROCEDURAL water + CC0 tiles |
| M11 | Asphalt | Asphalt | Main roads | MEDIUM | NO | YES | no | aggregate 5–10 mm | #4A4744 | 0.9 | low | — | F01 | ambientCG *Asphalt* |
| M12 | Roof finish | Gravel / roof tiles | Roofs | BACKGROUND | NO | YES | no | — | #CDBFA9 | 0.9 | low | — | ASSUMED | PROCEDURAL |
| M13 | Kasbah crenellation render | M01 | Tower crowns, chevron reliefs | HERO | YES | YES | relief = real geometry | — | #C9A77D | 0.9 | low | — | F04 | Geometry + M01 |

## SURFACE / LANDSCAPE TEXTURES

| ID | Name | Use | Priority | Scale | Source plan |
|---|---|---|---|---|---|
| T01 | Ochre desert soil + scattered stones | Terrain outside the plot | HIGH (aerials) | 1–2 m tiles + macro variation | Poly Haven *aerial_rocks* / *coast_sand* (CC0) |
| T02 | Beach sand | Beach | HIGH | 1 m | Poly Haven *coast_sand* |
| T03 | Lawn | Gardens | HIGH | blades 5–8 cm | geometry/particles + ambientCG *Grass* |
| T04 | Gravel / mulch | Planting beds | MEDIUM | 1–3 cm | ambientCG *Gravel* |
| T05 | Coastal rock / cliff | Cliff edge, ravines | MEDIUM | 0.5–2 m | Poly Haven *rock* textures |

## VEGETATION (3D)

| ID | Type | Height | Location | Priority | Source plan |
|---|---|---|---|---|---|
| V01 | Washingtonia fan palm | 6–12 m | Roads, gardens (as built) | HERO | Poly Haven has few palms → may need a user-supplied / licensed model; fallback: PROCEDURAL palm |
| V02 | Date / Canary palm | 6–10 m | Pavillon, plaza | HIGH | as V01 |
| V03 | Olive tree | 3–5 m | Gardens, plaza | HIGH | Poly Haven / Blender asset library (CC0 if available) |
| V04 | Ornamental grass (Pennisetum) | 0.6–1 m | Beds along paths (F04) | HIGH | PROCEDURAL / CC0 |
| V05 | Hedge (Pittosporum) | 1–1.5 m | Villa garden edges | HIGH | PROCEDURAL boxes + leaf shader |
| V06 | Bougainvillea | 1–3 m | Walls | MEDIUM | CC0 or PROCEDURAL |
| V07 | Argan tree, euphorbia, scrub | 0.3–6 m | Native context | BACKGROUND | PROCEDURAL scatter |

## FURNITURE / PROPS / PEOPLE / VEHICLES

| ID | Item | Priority | Plan |
|---|---|---|---|
| A01 | Sun loungers (timber + white cushion) | HIGH | PROCEDURAL (simple, matches F06) |
| A02 | Round outdoor table + 4 chairs | HIGH | PROCEDURAL / CC0 |
| A03 | Stone fire pit + curved bench | MEDIUM | PROCEDURAL |
| A04 | Pool umbrellas, cabanas | MEDIUM | PROCEDURAL |
| A05 | Roof jacuzzi | MEDIUM | PROCEDURAL |
| A06 | Interior proxies (sofa, bed, curtains) behind glazing | MEDIUM | PROCEDURAL, CINEMATIC_APPROXIMATION |
| A07 | People | OPTIONAL | Higgsfield motion rather than 3D |
| A08 | Cars | OPTIONAL | CC0 if access opens, else none |

## HDRI / SKY

| ID | Item | Plan |
|---|---|---|
| H01 | Clear midday sky | Nishita sky (built in) or Poly Haven HDRI |
| H02 | Golden hour / sunset HDRI | Poly Haven (CC0), BLOCKED now → Nishita sky with low sun |
| H03 | Atlantic ocean surface | PROCEDURAL ocean modifier + shader |
