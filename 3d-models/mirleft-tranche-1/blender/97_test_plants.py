"""Quick look at the plant library (21_plants): python 97_test_plants.py out_dir  (SAMPLES=n, SHOTS=a,b)"""
import importlib.util, math, os, sys
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("b05", os.path.join(HERE, "05_build_scene.py"))
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
L = B.L
bpy.ops.wm.read_factory_settings(use_empty=True)
for k in [k for k in os.listdir(os.path.join(os.path.dirname(HERE), "data", "textures")) if k.startswith("TEX_V2_")] if os.environ.get("RETEX") else []:
    os.remove(os.path.join(os.path.dirname(HERE), "data", "textures", k))
PL = B.load("21_plants.py")
M = {}
col = L.C.collection("SRC")
S = PL.build_sources(M, col)
show = L.C.collection("SHOW")
spots = {"date": (0, 0), "date_v1": (7, 0), "date_v2": (14, 0), "wash": (0, 10), "wash_v1": (7, 10), "wash_v2": (14, 10),
         "grass": (22, 0), "agave": (24, 0), "agave_b": (22, 2), "lavender": (24, 2), "jar": (22, 4), "amphora": (24, 4), "olive": (30, 0), "olive_v1": (35, 0)}
for k, (x, y) in spots.items():
    src = S[k[:-3] + "_v"][int(k[-1])] if k.endswith(("_v1", "_v2")) else S[k]
    ob = bpy.data.objects.new("SHOW_" + k, src.data)
    ob.location = (x, y, 0)
    show.objects.link(ob)
mg = bpy.data.materials.new("ground"); mg.use_nodes = True
mg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.32, 0.36, 0.18, 1)
bpy.ops.mesh.primitive_plane_add(size=200); bpy.context.object.data.materials.append(mg)
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.cycles.transparent_max_bounces = 64; sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "24")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.4
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
shots = {"palms_date": ((7, -16, 4.5), (7, 0, 4.2), 35), "palms_wash": ((7, -6, 6.0), (7, 10, 7.0), 30),
         "date_crown": ((2.5, -5.5, 6.8), (0, 0, 6.2), 40), "date_trunk": ((1.2, -2.6, 1.6), (0, 0, 1.4), 40),
         "wash_crown": ((2.5, 5.0, 10.5), (0, 10, 9.8), 40), "small": ((23, -3.2, 1.6), (23, 2.2, 0.3), 32),
         "date_top": ((0.3, -0.3, 16), (0, 0, 5), 30), "olive": ((32.5, -9, 2.2), (32.5, 0, 2.0), 35)}
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
for n, (e, t, lens) in shots.items():
    if os.environ.get("SHOTS") and n not in os.environ["SHOTS"].split(","):
        continue
    cam.location = Vector(e); cam.rotation_euler = (Vector(t) - Vector(e)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
    sc.render.filepath = os.path.join(out, n + ".jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
    print("SHOT", n, flush=True)
tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in col.objects}
print("TRIS", tris)
