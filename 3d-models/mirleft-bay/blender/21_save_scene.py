"""
21_save_scene — Blender-only delivery (client, 2026-10-02: "only in Blender, no D5").

    python 21_save_scene.py

Opens output/checkpoints/checkpoint_09_cameras.blend and writes scenes/:
  * Mirleft_Bay_Scene.blend          full scene (buildings, trees, cars, water, cameras, golden-hour
                                     light, haze compositor). Textures linked by RELATIVE path to
                                     ../assets/textures/, so keep the mirleft-bay folder together.
  * Mirleft_Bay_Scene_PACKED.blend   same file with every texture packed inside (open it anywhere),
                                     written only if it stays under 95 MB (GitHub limit 100 MB).
Only the 300k close-up grass tufts are left out (they make the file 240 MB); 20_pipeline.py
rebuilds them.
"""
import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CK = os.path.join(ROOT, "output", "checkpoints", "checkpoint_09_cameras.blend")
OUT = os.path.join(ROOT, "scenes")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=CK)
for o in list(bpy.data.objects):
    if o.name.startswith("GRASS_ZONE") or o.name.startswith("CAM_VAL"):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.outliner.orphans_purge(do_recursive=True)
sc = bpy.context.scene
sc.camera = bpy.data.objects["SH05_GARDEN_REVEAL"]
sc.cycles.samples = 256

linked = os.path.join(OUT, "Mirleft_Bay_Scene.blend")
bpy.ops.wm.save_as_mainfile(filepath=linked, compress=True, relative_remap=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile(filepath=linked, compress=True)

packed = os.path.join(OUT, "Mirleft_Bay_Scene_PACKED.blend")
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=packed, compress=True, copy=True)
mb = os.path.getsize(packed) / 1e6
if mb > 95:
    os.remove(packed)
for f in (linked, linked + "1", packed + "1"):
    if f.endswith("1") and os.path.exists(f):
        os.remove(f)
print("SCENE", {"linked_MB": round(os.path.getsize(linked) / 1e6, 1), "packed_MB": round(mb, 1),
                "packed_kept": mb <= 95, "images": len(bpy.data.images)})
