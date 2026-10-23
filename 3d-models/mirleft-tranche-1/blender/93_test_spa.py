"""Quick look at the SPA alone: python 93_test_spa.py out_dir  (VIEWS=a,b SAMPLES=n)"""
import importlib.util, os, sys
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib as L
spec = importlib.util.spec_from_file_location("spa", os.path.join(HERE, "15_spa.py"))
S = importlib.util.module_from_spec(spec); S.__dict__["L"] = L; spec.loader.exec_module(S)
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
col = L.C.collection("SPA")
W, Lg = 23.2, 50.9
obs, plants, lamps = S.build(M, col, W, Lg)
print("objects", len(obs), "plants", len(plants), "lamps", len(lamps), "faces", sum(len(o.data.polygons) for o in obs))
bpy.ops.mesh.primitive_plane_add(size=120, location=(W / 2, Lg / 2, -0.001))
bpy.context.object.data.materials.append(M["lawn"])
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "24")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
views = {"aerial": ((50, -25, 38), (W / 2, Lg / 2, 2), 26), "north": ((W / 2 + 12, Lg + 22, 2.0), (W / 2, Lg - 3, 4.0), 24),
         "court": ((W / 2 - 3.0, 39.6, 1.7), (W / 2, 12, 2.2), 20), "court2": ((W / 2 + 3.0, 11.0, 1.7), (W / 2 - 1, 38, 2.5), 22),
         "south": ((-14, -18, 3.0), (6, 6, 5.0), 24), "top": ((W / 2, Lg / 2, 80), (W / 2, Lg / 2 + 0.01, 0), 30),
         "east": ((W + 30, Lg / 2 - 8, 14), (W / 2, Lg / 2, 5.0), 28), "junction": ((W + 9, 4.0, 13.0), (W / 2, 10.0, 6.0), 26)}
for k, (p, t, lens) in views.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    cam.data.lens = lens
    cam.location = p
    d = Vector(t) - Vector(p)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"spa_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
