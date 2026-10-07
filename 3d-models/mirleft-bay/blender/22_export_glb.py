"""
22_export_glb — GLB versions of the Mirleft Bay scene (client request 2026-10-07).

    python 22_export_glb.py

Reads the D5 package .blend files written by 19_export_package.py (plain image materials, which
glTF reads directly: colour image, normal map, roughness, alpha on the leaf cards) and writes
output/glb/:
  * Mirleft_Bay_FULL.glb             everything (buildings, streets, parking, water, trees, cars, cameras)
  * Mirleft_Bay_NO_TREES_CARS.glb    same without trees, palms, scrub and cars
Textures are embedded (JPEG; PNG for the leaf cards with alpha). Units metres, +Y up (glTF).
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "output", "d5")
OUT = os.path.join(ROOT, "output", "glb")
os.makedirs(OUT, exist_ok=True)
DRACO = "--draco" in sys.argv

for name in ("FULL", "NO_TREES_CARS"):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(SRC, f"Mirleft_Bay_D5_{name}.blend"))
    for img in bpy.data.images:                      # find the textures next to the D5 package
        if img.filepath and not os.path.exists(bpy.path.abspath(img.filepath)):
            cand = os.path.join(SRC, "textures", os.path.basename(img.filepath))
            if os.path.exists(cand):
                img.filepath = cand
    path = os.path.join(OUT, f"Mirleft_Bay_{name}{'_draco' if DRACO else ''}.glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_visible=True, export_cameras=True,
                              export_lights=False, export_apply=True, export_image_format="AUTO",
                              export_yup=True, export_draco_mesh_compression_enable=DRACO,
                              export_draco_mesh_compression_level=6)
    print("GLB", name, round(os.path.getsize(path) / 1e6, 1), "MB")
