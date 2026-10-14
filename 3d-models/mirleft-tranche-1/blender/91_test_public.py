"""Quick look at the public buildings alone: python 91_test_public.py out_dir"""
import importlib.util, os, sys
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib as L
spec = importlib.util.spec_from_file_location("pub", os.path.join(HERE, "03_public.py"))
PB = importlib.util.module_from_spec(spec); PB.__dict__["L"] = L; spec.loader.exec_module(PB)
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
col = L.C.collection("PUB")
r = PB.restaurant(M, col)
c = PB.commerces(M, col); c.location = (40, 0, 0)
p = PB.petanque(M, col); p.location = (75, 0, 0)
k = PB.kiosk(M, col, "TOILETTE", 3.0); k.location = (60, -20, 0)
bpy.ops.mesh.primitive_plane_add(size=200, location=(30, 0, -0.001))
bpy.context.object.data.materials.append(M["lawn"])
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "32")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 30
views = {"resto_front": ((6, -34, 9), (0, -3, 5)), "resto_rear": ((-14, 34, 14), (0, 3, 5)), "comm": ((62, -30, 16), (40, -2, 3)), "pet": ((90, -22, 14), (73, 2, 1))}
for k_, (p_, t_) in views.items():
    if os.environ.get("VIEWS") and k_ not in os.environ["VIEWS"].split(","): continue
    cam.location = p_
    cam.rotation_euler = (Vector(t_) - Vector(p_)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"pub_{k_}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
