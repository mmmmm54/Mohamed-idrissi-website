"""Quick look at the hotel alone: python 95_test_hotel.py out_dir  (VIEWS=a,b SAMPLES=n PLANTS=0)"""
import importlib.util, json, math, os, sys
import bpy
import numpy as np
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib as L
spec = importlib.util.spec_from_file_location("ho", os.path.join(HERE, "17_hotel.py"))
HO = importlib.util.module_from_spec(spec); HO.__dict__["L"] = L; spec.loader.exec_module(HO)
ROOT = os.path.dirname(HERE)
SITE = json.load(open(os.path.join(ROOT, "data", "site.json")))
T3 = json.load(open(os.path.join(ROOT, "data", "t3_site.json")))
PL = SITE["plane"]
hz = lambda x, y: PL[0] * x + PL[1] * y + PL[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
col = L.C.collection("HO")
obs, plants, (o, U, V) = HO.build(M, col, T3["hotel"], T3["frame"], hz)
print("objects", len(obs), "faces", sum(len(ob.data.polygons) for ob in obs), "plants", len(plants))
w = lambda u, v: tuple(o + U * u + V * v)
# the ground round it: a plane on hz
from shapely.geometry import Point, Polygon
c = np.array(w(-7, -8))
mbg = L.C.MeshBuilder()
L.prism(mbg, "pave_beige", Point(*c).buffer(130, 8).difference(Polygon(T3["hotel"]["plot"]["ext"])), -0.3, -0.05, zf=hz)
mbg.build("GROUND", col, M)
if os.environ.get("PLANTS", "1") == "1":
    LS = L.bay("09_build_landscape.py")
    src = {"date": LS.make_source("DATE_PALM", LS.date_palm(4, 5.0), M, col),
           "wash": LS.make_source("WASHINGTONIA", LS.washingtonia(1, 9.0), M, col)}
    for kind, u, v, z, s in plants:
        if kind in src:
            ob = bpy.data.objects.new("P", src[kind].data); col.objects.link(ob)
            xy = w(u, v); ob.location = (xy[0], xy[1], z); ob.scale = (s, s, s)
        else:
            xy = w(u, v)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.6 * s if kind == "olive" else 0.5 * s, location=(xy[0], xy[1], z + (2.4 if kind == "olive" else 0.4)))
            bpy.context.object.data.materials.append(M["olive_leaf"])
    for k in list(src):
        src[k].hide_render = True
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "16")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
z0 = hz(*w(0, 0))
# views in the hotel frame: (eye u, v, dz over ground), (target u, v, dz), lens
views = {"aerial": ((-75, -70, 55), (-5, -5, 0), 26), "north": ((-20, 85, 6), (5, 40, 7), 24),
         "gate": ((7.0, 62, 1.7), (7.05, 47, 6.0), 22), "garden": ((-27, 40, 2.0), (-10, 0, 3.0), 20),
         "pool": ((-18.5, 26, 1.7), (-18.5, -10, 1.2), 22), "arm": ((-20.5, -4.0, 1.7), (7, -4, 2.5), 22),
         "pavilion": ((40, -4, 3.0), (7, -4, 4.0), 24), "suites": ((-30, -75, 6), (5, -35, 3), 24),
         "street7": ((-38, -25, 1.7), (-28.7, -4, 2.5), 22), "top": ((-7, -8, 170), (-7, -7.99, 0), 30),
         "toparm": ((-9, -4, 45), (-9, -3.99, 0), 30), "west": ((-60, 10, 14), (0, 10, 4), 22), "east": ((40, 30, 10), (7, 10, 5), 22)}
for k, (e, t, lens) in views.items():
    if os.environ.get("VIEWS") and k not in os.environ["VIEWS"].split(","): continue
    pe, pt = w(e[0], e[1]), w(t[0], t[1])
    pe = Vector((pe[0], pe[1], hz(*pe) + e[2])); pt = Vector((pt[0], pt[1], hz(*pt) + t[2]))
    cam.data.lens = lens
    cam.location = pe
    cam.rotation_euler = (pt - pe).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"ho_{k}.jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
