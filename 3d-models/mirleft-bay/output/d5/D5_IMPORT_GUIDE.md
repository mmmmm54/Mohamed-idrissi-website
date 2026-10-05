# D5 import guide — Mirleft Bay

## Two versions
| File | Contents | Use it when |
|---|---|---|
| `Mirleft_Bay_D5_FULL.fbx` | Everything: buildings, streets, parking, walls, water, trees, palms, scrub, cars, 14 cameras | You want everything placed already |
| `Mirleft_Bay_D5_NO_TREES_CARS.fbx` | Same, **without** trees, palms, scrub and cars. Parking bays, lines, streets and garden walls stay | You place D5 library trees, palms and cars yourself |

Both use the same `textures/` folder: keep it next to the FBX.

## Import
1. D5 ▸ Import ▸ Model ▸ the FBX, unit **metres**.
2. Do **not** import the Blender scene (`scenes/Mirleft_Bay_Scene*.blend`) into D5: its node materials come in white.
3. If a material still shows white: Base Color ▸ `textures/<material>_COL.jpg`, Normal ▸ `textures/<material>_NRM.jpg`.

## Water (pools, canals, lake, channel, jacuzzi)
Each basin has three parts: the water surface (`M10_Pool_Water`, `M10_Lake_Water`), tiled walls and a tiled
**floor** 0.6–1.4 m down (`M10_Pool_Mosaic`, blue). Put D5 Water on the water surface. You see the blue
floor through it.

## Recommended D5 material swaps
- `M06_Glass` → D5 Glass
- `M10_Pool_Water`, `M10_Lake_Water`, `H03_Ocean` → D5 Water
- `T03_Lawn` → D5 Grass (scatter)

UVs are box-projected in metres divided by the texture's tile size, so textures sit at true scale with D5 tiling = 1.
Only the 300k close-up grass tufts are left out: use D5 grass on the lawns.
