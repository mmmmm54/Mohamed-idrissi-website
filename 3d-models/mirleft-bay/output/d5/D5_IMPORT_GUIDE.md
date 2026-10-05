# D5 import guide — Mirleft Bay

## Why surfaces came in WHITE (fixed 2026-10-05)
The Blender scene (`scenes/Mirleft_Bay_Scene*.blend`) builds its colours with node math (detail transfer,
box projection). D5 does not read those nodes, so every surface arrives white. **Do not import the
Blender scene into D5.** Use the files in this folder, where every material is a plain image material.

## Import
1. Keep `Mirleft_Bay_D5.fbx` and the `textures/` folder side by side (unzip the whole `d5` folder).
2. D5 ▸ Import ▸ Model ▸ `Mirleft_Bay_D5.fbx`, unit **metres**.
3. If a material still shows white: select it ▸ Base Color ▸ load the matching `textures/<material>_COL.jpg`
   (and `_NRM.jpg` in Normal). The material names are the same as the texture names.
4. Swap these for D5 library materials for the best result:
   - `M06_Glass` → D5 Glass
   - `M10_Pool_Water`, `M10_Lake_Water`, `H03_Ocean` → D5 Water
   - `T03_Lawn` → D5 Grass (scatter)
   - trees and cars → D5 library assets, if you want them more realistic

## What is in the FBX
Every building of the permit plan, the streets with their markings, the parking and cars, the garden walls, the trees, the water, and the 14 cameras.
UVs are box-projected in metres divided by the texture's tile size, so textures sit at true scale with D5 tiling = 1.
Only the 300k close-up grass tufts are left out: use D5 grass on the lawns instead.
