"""
19_export_package — D5 Render package (MODE A on request of the client, 2026-10-02).

    python 19_export_package.py [--light]

Opens output/checkpoints/checkpoint_09_cameras.blend and writes output/d5/:
  * Mirleft_Bay_D5.fbx        architecture + site + terrain + water + cameras, every building
                              instance made real, material names kept (see D5_MATERIAL_MAPPING.md)
  * Mirleft_Bay_D5.blend      the same scene, for D5's Blender sync plugin if you use it
Everything is kept (buildings, palms, pink trees, olives, scrub, cars, parking, water) so D5 only
needs small fixes. Only the 300k close-up grass tufts are left out (about 4 million triangles; use
D5 grass on the T03_Lawn faces). `--light` drops vegetation and cars for a lighter file. UVs are in metres (1 UV unit = 1 m;
terrain 1 unit = 10 m), so D5 materials tile at true scale.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CK = os.path.join(ROOT, "output", "checkpoints", "checkpoint_09_cameras.blend")
OUT = os.path.join(ROOT, "output", "d5")
os.makedirs(OUT, exist_ok=True)
LIGHT = "--light" in sys.argv          # optional: drop vegetation + cars (old behaviour)

bpy.ops.wm.open_mainfile(filepath=CK)
sc = bpy.context.scene
vl = bpy.context.view_layer

# 1. strip what D5 does better (and the heavy grass)
removed = 0
for o in list(bpy.data.objects):
    n = o.name
    if n.startswith("GRASS_ZONE") or n.startswith("SRC_") or n.startswith("CAM_VAL") \
            or (LIGHT and (n.startswith("VEG_") or n.startswith("VEH_"))):
        bpy.data.objects.remove(o, do_unlink=True)
        removed += 1

# 2. make building instances real (D5 imports plain meshes)
for lc in vl.layer_collection.children["03_ARCHITECTURE"].children:
    lc.exclude = False
bpy.ops.object.select_all(action="DESELECT")
inst = [o for o in bpy.data.objects if o.instance_type == "COLLECTION" and o.instance_collection]
for o in inst:
    o.select_set(True)
vl.objects.active = inst[0] if inst else None
if inst:
    bpy.ops.object.duplicates_make_real(use_base_parent=False, use_hierarchy=False)
for o in inst:
    if o.name in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)
# the source type collections stay hidden: exclude them again so they are not exported twice
for lc in vl.layer_collection.children["03_ARCHITECTURE"].children:
    if lc.name.startswith("TYPE_"):
        lc.exclude = True

# 3. far terrain ring is 60 km wide: keep it (horizon), it is light
mesh_count = sum(1 for o in vl.objects if o.type == "MESH")
tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for o in vl.objects:
    if o.type == "MESH":
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)

fbx = os.path.join(OUT, "Mirleft_Bay_D5.fbx")
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, use_visible=True,
                         object_types={"MESH", "CAMERA", "EMPTY"}, apply_unit_scale=True,
                         apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
                         mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="COPY",
                         embed_textures=True, bake_space_transform=False)
blend = os.path.join(OUT, "Mirleft_Bay_D5.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, copy=True)
print("D5_EXPORT", {"removed": removed, "meshes": mesh_count, "triangles": tris,
                    "fbx_MB": round(os.path.getsize(fbx) / 1e6, 1), "blend_MB": round(os.path.getsize(blend) / 1e6, 1)})
