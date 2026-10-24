# Jnane Deroua, lot N°77: villa converted into a kindergarten (exterior)

Blender model of the signed permit drawing "AMENAGEMENT + MODIFICATION D'UNE VILLA EN MATERNELLE"
(planche 1/1, scale 1/100, lotissement Jnane Deroua lot N°77, Deroua). Exterior only, as the
plan shows it ("à modifier" version).

| File | Contents |
|---|---|
| `Jnane_Deroua_Lot77_Maternelle.blend` | The scene: building, coloured blocks, windows, balcony, pergola, plot walls, garden, 5 cameras |
| `renders/` | CAM_FRONT, CAM_FRONT_3Q, CAM_LEFT, CAM_REAR, CAM_AERIAL (1920 × 1080) |
| `blender/01_parse_dwg.py` | Reads the DWG (converted to JSON) and writes `data/facades.json`: windows, coloured window frames, blocks, railings |
| `blender/02_build_scene.py` | Builds the scene from that data and the plan dimensions, saves the .blend, renders |

## Taken from the drawing (DWG in millimetres)
- **Plot:** 13.00 × 18.50 m. Setbacks: 4.20 m front, 4.40 m rear, 4.00 m left. The right side is the party wall on the plot boundary.
- **RDC:** 9.00 × 9.90 m. The RDC floor is at +0.50 (3 steps of 16.7 cm at the entrance).
- **1st floor:** at +4.40. The front is recessed 0.80 m for x > 3.72 m, with a balcony from 3.72 to 6.30 m and its railing. At the rear right there is an open courtyard on the RDC roof (2.10 × 3.36 m).
- **Roof:** terrace at +7.49, acrotère up to +8.19 (the height of all three façades).
- **Façades:**
  - The window positions and sizes, and the glazing bars of every window.
  - The entrance door: 1.80 × 2.49 m, double leaf.
  - The coloured window frames (13) and the 0.50 m coloured blocks (99), using the exact colours from the DWG (sampled from the PDF where the DWG uses index colours).
- **Entrance:** a path through the front wall (1.62 m wide) with a wooden pergola. Beams at +2.51 and +2.89, from the left façade.
- **Plot walls:** 2.50 m high (2.40–2.52 on the façades).

## Not on the drawing (kept simple, to confirm)
- **Right side:** it's the party wall, and the neighbouring house is not modelled.
- **Gate:** none is drawn in the front-wall opening.
- **Materials:** white smooth render and beige aluminium frames, from the 2008 legend and the DWG colours. Grey waterproofing on the roof.
- **Context:** the street and sidewalk outside the plot are context only.
