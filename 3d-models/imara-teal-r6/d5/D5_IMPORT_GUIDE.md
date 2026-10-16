# D5 import guide: Imara Teal R+6

`Imara_Teal_R6_D5.fbx`: the whole building, inside and out, with the basement parking, the ramp and the
street. Textures are embedded; the same images are in `textures/` (keep the folder next to the FBX).

## Import
1. D5 > Import > Model > `Imara_Teal_R6_D5.fbx`, unit **metres**.
2. Objects are named by level, then material: `SS_` basement, `RDC_` ground floor, `N1_` to `N6_` floors,
   `TOIT_` roof, `Site_` street. To show one floor as a 3D plan, hide the objects of the levels above it.
3. If a material comes in white, set Base Color to `textures/<image>.jpg`.

## Material swaps in D5
- `Window_Glass`, `Balcony_Glass_Railing` -> D5 Glass. `Locker_Mesh` -> D5 metal mesh (or glass, 50 %).
- `LED_Light`, `Downlights`, `Exit_Sign_Green`, `Sign_White_Lit`, `Lamp_Shade` -> emissive (D5 Emissive),
  LEDs at 20-40.
- `Parking_Epoxy_Floor` -> raise reflections a little for a polished epoxy look.
- `Plants_Green` / `Plants_Light` -> replace with D5 plants if you like.

The Blender lamps (room lights, parking battens, ramp lights) do not travel through FBX: in D5 add
lights on the emissive fittings, or use the emissive materials above.
