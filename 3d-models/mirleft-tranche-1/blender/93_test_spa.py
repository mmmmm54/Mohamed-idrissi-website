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
views = {"aerial": ((W + 28, -18, 30), (W / 2, Lg / 2, 2), 26), "front": ((-14, 18.0, 2.0), (8.0, 25.0, 3.0), 22),
         "court": ((5.0, 3.0, 1.7), (5.0, 30, 1.5), 20), "rear": ((W + 16, 10.0, 2.5), (W - 2.0, 25.0, 3.0), 22),
         "roof": ((-6, 2.0, 14.0), (14.0, 24.0, 4.5), 22), "north": ((8, Lg + 10, 3.0), (14, Lg - 10, 3.0), 24),
         "top": ((W / 2, Lg / 2, 80), (W / 2, Lg / 2 + 0.01, 0), 30)}
for k, (p, t, lens) in views.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    cam.data.lens = lens
    cam.location = p
    d = Vector(t) - Vector(p)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"spa_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
