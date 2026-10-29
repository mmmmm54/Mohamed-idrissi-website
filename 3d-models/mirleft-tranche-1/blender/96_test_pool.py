"""Quick look at the pool park alone: python 96_test_pool.py out_dir  (CAMS=a,b SAMPLES=n)"""
import importlib.util, os, sys
import bpy
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("b05", os.path.join(HERE, "05_build_scene.py"))
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
L = B.L
bpy.ops.wm.read_factory_settings(use_empty=True)
M = L.materials()
site, t1 = Polygon(B.SITE["boundary"]), B.P(B.SITE["t1_region"])
T2M, T3M, PP = B.load("13_tranche2.py"), B.load("19_tranche3.py"), B.load("20_pool_park.py")
graded = unary_union([t1, T2M.blocks(), T3M.envelope(), PP.envelope()])
Hn = B.natural_terrain(site.bounds)
def H(xy):
    xy = np.atleast_2d(xy)
    d = shapely.distance(shapely.points(xy), graded)
    w = np.clip(d / 25.0, 0, 1); w = w * w * (3 - 2 * w)
    out = (1 - w) * np.array([B.hz(x, y) for x, y in xy]) + w * Hn(xy)
    out[shapely.contains_xy(PP.flat_area(), xy[:, 0], xy[:, 1])] = PP.LEVEL
    return out
cols = {k: L.C.collection(k) for k in ("07_CAMERAS", "SRC", "GROUND_AROUND")}
src = {}
for k in ("olive", "date", "wash", "shrub", "shrub_pink", "agave"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.8 if k == "olive" else (0.6 if k.startswith(("shrub", "agave")) else 1.2))
    ob = bpy.context.object; ob.name = "SRC_" + k
    ob.data.materials.append(M["olive_leaf"] if "olive_leaf" in M else M["lawn"])
    src[k] = ob; ob.hide_render = True
cams = PP.build(M, B, src, H)
# the ground round the zone (natural), coarse
mb = L.C.MeshBuilder()
L.prism(mb, "terrain" if "terrain" in M else "sand", PP.ZONE.buffer(60).difference(PP.ZONE), -1.0, -0.15, zf=lambda x, y: float(H(np.array([[x, y]]))[0]))
mb.build("AROUND", cols["GROUND_AROUND"], M)
lt = L.bay("14_build_lighting.py"); lt.apply("LIGHTING_01_DAYLIGHT")
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(os.environ.get("SAMPLES", "12")); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.6
out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
for n, cam in cams.items():
    if os.environ.get("CAMS") and n not in os.environ["CAMS"].split(","):
        continue
    sc.camera = cam
    sc.render.filepath = os.path.join(out, n + ".jpg"); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
    print("CAM", n, flush=True)
