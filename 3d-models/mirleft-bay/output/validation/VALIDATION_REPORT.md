# VALIDATION REPORT — Mirleft Bay

Run: 2026-10-01, `20_pipeline.py --validate` (automated) plus visual review of every preview render.
Status per row: **PASS** · **PASS (INFERRED)** = consistent with the sources but not surveyed · **OPEN** = known limitation.

## Automated checks (`validation_graybox.json`)

| Check | Model | Source | Result |
|---|---|---|---|
| Plot area | 82 350 m² | 82 070 m² (title block F01) | PASS (+0.3 %) |
| Plan scale 1/500 | 0.12697 m/px | sheet 1866 mm / 7348 px | PASS |
| Orientation | axis bearing 122.5° | client Google Earth polygon, IoU 0.82 | PASS (± 1°) |
| Duplex (T1 + T2) | 17 pairs = 34 units | 24 + 10 = 34 (permit) | PASS |
| Villa type B | 33 | 21 + 6 + 6 = 33 | PASS |
| Villa type C | 13 | 7 + 6 = 13 | PASS |
| Villa type A | 4 | 4 | PASS |
| Duplex unit area | 132.4 m² gross incl. walls | 124 m² covered | PASS (INFERRED, +6.8 %) |
| Villa B area | 151.8 m² | 164 m² | PASS (INFERRED, −7.4 %) |
| Villa C area | 143.8 m² | 145 m² | PASS |
| Villa A area | 219.8 m² | 220 m² | PASS |
| Terrain inside the plot | min 19.3 / median 51.3 / max 64.0 m | Google Earth 18.72 / 51.28 / 64.99 m | PASS (calibrated) |
| Objects without a material | 0 | — | PASS |
| Ground-level cameras clear of vegetation | 3.5 m radius cleared | — | PASS |

## Visual checks

| View | File | Compared with | Result |
|---|---|---|---|
| TOP_VIEW | `VAL_TOP_VIEW_graybox.jpg` | Plan F01 | PASS: blocks, lots, roads, lake and club pools sit on the drawn positions (`VAL_TOP_OVER_PLAN_graybox_stacked.jpg`) |
| Digitising overlay | `VAL_00_digitised_on_plan.jpg` | Plan F01 | PASS: 46 villa lots, 17 duplex pairs, public buildings, spot heights |
| Registration | `VAL_00_registration_google_earth.jpg` | Client's Google Earth trace | PASS |
| Hero duplex | `previews/SH05`, `SH06`, `SH07`, `SH09` | Catalogue p7, site photo F07 | PASS (INFERRED): set-back upper floor, pergolas, timber lattice, row of square niches, dark window surrounds, roof terrace with jacuzzi |
| Kasbah buildings | `previews/SH04`, `SH08` | Site photo F04 | PASS (INFERRED): crenellations, corner towers, recessed vertical bays. Simpler than the built one (no chevron friezes on the towers). |
| Golden-hour light | all previews | Catalogue mood p1, p7, p10 | PASS: sun from WSW 257°, elevation 10°, computed for the site |

## Known limitations (OPEN)

1. **No dimensioned drawings exist** (client, 2026-10-01). Every building is INFERRED from the permit areas, catalogue plans and photos (± 0.3 m on openings, ± 1.3 m on placement).
2. **Textures are procedural or generated** (APPROXIMATED). Poly Haven and ambientCG are blocked by this environment's network policy (HTTP 403), so no CC0 scans could be downloaded. See `assets/ASSET_MANIFEST.csv`.
3. **Terrain outside the plot**: from the plan spot heights + Google Earth coastline; the inland hills are ASSUMED. It reads smoother and sandier than the real rocky plateau.
4. **Hedges** are textured boxes: fine from 10 m and beyond, flat in close-ups.
5. **Tranche 2 duplex positions** are hidden under the red phase tint on the plan; they are spaced evenly (5 pairs).
6. **Hotel and spa** are kasbah massing at plan footprint; the catalogue does not show them.
7. **Interiors** are CINEMATIC_APPROXIMATION boxes behind the glazing (warm lit plaster + linen curtains), never presented as designed interiors.
