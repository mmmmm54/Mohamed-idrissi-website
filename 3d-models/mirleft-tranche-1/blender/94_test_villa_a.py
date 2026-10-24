"""Quick look at the villa type A alone: python 94_test_villa_a.py out_dir  (VIEWS=a,b SAMPLES=n)"""
import importlib.util, os, sys
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib as L
spec = importlib.util.spec_from_file_location("va", os.path.join(HERE, "16_villa_a.py"))
VA = importlib.util.module_from_spec(spec); VA.__dict__["L"] = L; spec.loader.exec_module(VA)
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
col = L.C.collection("VA")
ob, plants = VA.build(M, col)
print("faces", len(ob.data.polygons), "plants", len(plants))
bpy.ops.mesh.primitive_plane_add(size=120, location=(8, 9, 0.07))
bpy.context.object.data.materials.append(M["lawn"])
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "24")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
views = {"ne": ((34, 32, 15), (8, 9, 2), 24), "sw": ((-20, -14, 10), (7, 9, 2), 24), "east": ((31, 9.3, 1.7), (12, 9.3, 3.0), 22),
         "west": ((-17, 9.3, 2.5), (4, 9.3, 2.6), 22), "top": ((6, 9.3, 48), (6, 9.31, 0), 30), "south": ((8, -15, 2.2), (8, 5, 2.8), 22),
         "north": ((9, 36, 3.0), (9, 14, 3.0), 22), "roof": ((24, -10, 13), (8, 9, 3.5), 24), "blk": ((22, 4, 9), (11.3, 9.3, 5.0), 30)}
for k, (p, t, lens) in views.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    cam.data.lens = lens
    cam.location = p
    cam.rotation_euler = (Vector(t) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"va_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
