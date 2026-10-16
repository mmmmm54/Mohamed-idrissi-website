"""
export_d5: D5 Render package of the Imara Teal R+6: the building with its inside, the basement
parking, the ramp and the street.

    python export_d5.py <folder holding Imara_Teal_R6.blend>

The materials are already Principled BSDF with their image on Base Color (UVs at true size), which is
what D5 reads. Writes d5/ next to the .blend:
  Imara_Teal_R6_D5.fbx    every level (objects named SS_, RDC_, N1_ ... N6_, TOIT_ + material), the
                          street and the cameras, textures embedded
  textures/               the same images, to reassign by hand if a material comes in white
  D5_IMPORT_GUIDE.md
and zips the folder to Imara_Teal_R6_D5.zip.
"""
import os
import shutil
import sys
import zipfile

import bpy

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = os.path.join(ROOT, "d5")
TEX = os.path.join(OUT, "textures")

GUIDE = """# D5 import guide: Imara Teal R+6

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
"""


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(TEX)
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "Imara_Teal_R6.blend"))
    plan3d = bpy.data.collections.get("Plan3D_Niveau_3")       # render-only copy, not for D5
    if plan3d is not None:
        for ob in list(plan3d.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
    for img in bpy.data.images:                                # write the packed images out
        if img.packed_file is None:
            continue
        name = os.path.basename(img.filepath) or (img.name + ".jpg")
        dst = os.path.join(TEX, name)
        with open(dst, "wb") as fh:
            fh.write(img.packed_file.data)
        img.unpack(method="REMOVE")
        img.filepath = dst
        img.reload()
    bpy.context.view_layer.update()
    path = os.path.join(OUT, "Imara_Teal_R6_D5.fbx")
    bpy.ops.export_scene.fbx(filepath=path, use_selection=False, object_types={"MESH", "CAMERA", "EMPTY"},
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             axis_forward="-Z", axis_up="Y", mesh_smooth_type="FACE", path_mode="COPY",
                             embed_textures=True, bake_space_transform=False)
    print("FBX", round(os.path.getsize(path) / 2 ** 20, 1), "MiB", flush=True)
    open(os.path.join(OUT, "D5_IMPORT_GUIDE.md"), "w").write(GUIDE)
    z = os.path.join(ROOT, "Imara_Teal_R6_D5.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for r, _, fs in os.walk(OUT):
            for f in fs:
                p = os.path.join(r, f)
                zf.write(p, os.path.join("Imara_Teal_R6_D5", os.path.relpath(p, OUT)))
    print("D5_ZIP", round(os.path.getsize(z) / 2 ** 20, 1), "MiB", flush=True)


main()
