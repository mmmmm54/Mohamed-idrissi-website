"""Quick look at the public buildings: python 91_test_public.py out_dir"""
import importlib.util, math, os, sys
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import lib as L
spec = importlib.util.spec_from_file_location("pub", os.path.join(HERE, "03_public.py"))
P = importlib.util.module_from_spec(spec); P.__dict__["L"] = L; spec.loader.exec_module(P)
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
col = L.C.collection("PUBLIC")
which = os.environ.get("WHICH", "adm")
if which == "adm":
    ob = P.pavilion(M, col); tgt = Vector((0, -2, 5)); R = 34
else:
    ob = P.market(M, col); tgt = Vector((0, 0, 5)); R = 30
print("faces", len(ob.data.polygons))
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -0.31)); bpy.context.object.data.materials.append(M["lawn"])
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "32")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 30
for k, (az, el) in {"front": (-110, 12), "rear": (60, 14), "aerial": (-140, 40)}.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    a, e = math.radians(az), math.radians(el)
    cam.location = tgt + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * R
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"{which}_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
