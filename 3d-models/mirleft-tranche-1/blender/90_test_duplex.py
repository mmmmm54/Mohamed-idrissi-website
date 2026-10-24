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
print("faces", len(ob.data.polygons), [m.name for m in ob.data.materials])
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.001))
bpy.context.object.data.materials.append(M["lawn"])
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "32")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
# the two reference views of the remarks (front from the left corner, rear of the pair), and two more
views = {"front": ((-17, -17, 1.7), (-3.5, -4.0, 4.2), 22), "rear": ((-13, 21, 1.7), (-1.5, 3.0, 3.8), 22),
         "aerial": ((20, -24, 21), (0, 0, 4.0), 30), "roof": ((-6, 12, 14), (0, -1, 7.5), 26),
         "cornice": ((-11.5, -9.5, 5.2), (-7.0, -3.6, 6.6), 30), "door": ((-6.5, -9.0, 1.7), (-4.3, -3.5, 1.9), 30)}
for k, (p, t, lens) in views.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    cam.data.lens = lens
    cam.location = p
    d = Vector(t) - Vector(p)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"dpx{var}_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
