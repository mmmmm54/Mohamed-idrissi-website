"""Quick look at the villa type C alone: python 92_test_villa_c.py out_dir  (VIEWS=a,b SAMPLES=n MIRROR=1)"""
import importlib.util, os, sys
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib as L
spec = importlib.util.spec_from_file_location("vc", os.path.join(HERE, "14_villa_c.py"))
V = importlib.util.module_from_spec(spec); V.__dict__["L"] = L; spec.loader.exec_module(V)
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
col = L.C.collection("VILLA_C")
ob = V.build(M, col)
if os.environ.get("MIRROR"):
    m = V.mirrored(ob, "VILLA_C_M"); bpy.data.objects.remove(ob); ob = m
print("faces", len(ob.data.polygons), [m.name for m in ob.data.materials])
bpy.ops.mesh.primitive_plane_add(size=80, location=(8, 9, -0.001))
bpy.context.object.data.materials.append(M["lawn"])
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "24")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
# local frame: x 0-16.5 (stair on x 0-1.14), y 0 pool back .. 17.65 porch front
views = {"front": ((14, 34, 1.7), (8.7, 14, 3.4), 24), "front_l": ((-6, 30, 2.0), (6, 13, 3.2), 24),
         "rear": ((3, -14, 1.8), (8.7, 7, 2.8), 22), "west": ((-16, 4, 2.2), (1, 9, 3.0), 24),
         "east": ((32, 12, 2.0), (16, 10, 3.0), 24), "aerial": ((30, -14, 22), (8.5, 9, 3.0), 28),
         "aerial2": ((-12, 34, 20), (8.5, 9, 3.5), 28), "portal": ((8.7, 25, 1.7), (8.7, 17.6, 3.6), 30),
         "corner": ((-4, 22, 1.7), (2.5, 15, 3.8), 30), "stairtop": ((-5, 6, 6.5), (1.0, 11.5, 4.2), 30), "stairw": ((-12, 1, 7), (1.5, 8, 1.2), 28),
         "sdbe": ((24, 9.5, 6.5), (16.3, 9.5, 4.3), 28), "roof": ((8.5, -4, 14), (8.5, 10, 4.2), 30)}
for k, (p, t, lens) in views.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    cam.data.lens = lens
    cam.location = p
    d = Vector(t) - Vector(p)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"vc_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
