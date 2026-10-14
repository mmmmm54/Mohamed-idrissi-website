"""Quick look at the duplex variants alone: python 90_test_duplex.py out_dir  (VARIANT=A|B)"""
import importlib.util, os, sys
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib as L
spec = importlib.util.spec_from_file_location("dpx", os.path.join(HERE, "02_duplex.py"))
D = importlib.util.module_from_spec(spec); D.__dict__["L"] = L; spec.loader.exec_module(D)
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
col = L.C.collection("DUPLEX")
var = os.environ.get("VARIANT", "A")
ob = D.build(M, col, var)
print("faces", len(ob.data.polygons))
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.001))
bpy.context.object.data.materials.append(M["lawn"])
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "32")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 32
views = {"front": ((6, -26, 6), (0, -1, 4.5)), "rear": ((-8, 26, 9), (0, 2, 5.5)), "aerial": ((18, 22, 20), (0, 2, 5.0)), "stair": ((-5, 9, 10.5), (-1, 3, 5.5))}
for k, (p, t) in views.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    cam.location = p
    d = Vector(t) - Vector(p)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"dpx{var}_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
