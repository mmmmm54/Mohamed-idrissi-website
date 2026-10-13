"""
05_build_scene — Mirleft, Tranche A + B (detailed) on the full site boundary (empty land).

    python 05_build_scene.py [--render all|NAME,NAME] [--samples 96] [--pct 100] [--no-save]

World frame: metres, x east, y north (DWG axes, ocean to the west), origin = DWG (47900, 290320),
z = altitude - 50 m (NGM levels of the plan de masse contours).

Ground: Tranche A+B is graded on one plane fitted to the plan's contours inside the area (5.5 %
rising to the north-east, +60.9 at its centre); the rest of the site keeps the natural terrain of
the contours (5 m interval, labelled), blended over 25 m. Terrain stops at the site boundary
(82 139 m2, the title block's 8 ha 20 a 70 ca) with a cut edge and boundary markers at the bornes.
"""
import importlib.util
import json
import math
import os
import random
import sys

import bpy  # noqa: I001
import numpy as np
from mathutils import Vector
from shapely.geometry import LineString, MultiPoint, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import lib as L  # noqa: E402

C = L.C
SITE = json.load(open(os.path.join(ROOT, "data", "site.json")))
Z0 = 50.0
PLANE = (0.03653, 0.04115, 59.41131 - Z0)   # least-squares plane through the A+B contours
RNG = random.Random(20261013)


def load(fname):
    spec = importlib.util.spec_from_file_location("ab_" + fname[:2], os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    mod.__dict__["L"] = L
    spec.loader.exec_module(mod)
    return mod


def hg(x, y):
    return PLANE[0] * x + PLANE[1] * y + PLANE[2]


def polys(lst):
    out = []
    for p in lst:
        g = Polygon(p["ext"], p["holes"]).buffer(0)
        out += L.as_polys(g)
    return out


def P(lst):
    return unary_union(polys(lst)) if lst else Polygon()


# ---------------------------------------------------------------------------------------------
def natural_terrain():
    """Height field from the labelled contours (linear in the triangles, smoothed)."""
    from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator, RegularGridInterpolator
    from scipy.ndimage import gaussian_filter
    pts = []
    for c in SITE["contours"]:
        g = LineString(c["pts"])
        n = max(2, int(g.length / 2))
        for i in range(n + 1):
            p = g.interpolate(i / n, normalized=True)
            pts.append((p.x, p.y, c["z"] - Z0))
    A = np.array(pts)
    lin = LinearNDInterpolator(A[:, :2], A[:, 2])
    near = NearestNDInterpolator(A[:, :2], A[:, 2])
    xs = np.arange(-560, 190, 2.0)
    ys = np.arange(-130, 140, 2.0)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    Zl = lin(X, Y)
    Zn = near(X, Y)
    Z = np.where(np.isnan(Zl), Zn, Zl)
    Z = gaussian_filter(Z, 3.0)
    return RegularGridInterpolator((xs, ys), Z, bounds_error=False, fill_value=None)


def build_terrain(M, col, site, ab):
    import shapely
    Hn = natural_terrain()
    land = site.difference(ab)
    mb = C.MeshBuilder()
    step = 3.0
    x0, y0, x1, y1 = land.bounds

    def H(xy):
        xy = np.atleast_2d(xy)
        d = shapely.distance(shapely.points(xy), ab)
        w = np.clip(d / 25.0, 0, 1)
        w = w * w * (3 - 2 * w)
        return (1 - w) * hg(xy[:, 0], xy[:, 1]) + w * Hn(xy)

    from shapely.prepared import prep
    pl = prep(land)
    tris = []
    for i in range(int((x1 - x0) / step) + 1):
        for j in range(int((y1 - y0) / step) + 1):
            cell = box(x0 + i * step, y0 + j * step, x0 + (i + 1) * step, y0 + (j + 1) * step)
            if pl.contains(cell):
                a, b, c, d = cell.exterior.coords[:4]
                tris += [(a, b, c), (a, c, d)]
            elif pl.intersects(cell):
                for g in L.as_polys(land.intersection(cell)):
                    tris += [tuple(t) for t in L.tri_poly(g)]
    V = np.array([p for t in tris for p in t])
    Z = H(V)
    for k in range(len(tris)):
        pts = [(V[3 * k + m][0], V[3 * k + m][1], Z[3 * k + m]) for m in range(3)]
        mb.poly("terrain", pts, [(p[0], p[1]) for p in pts])
    # cut edge along the site boundary (site-model look) and boundary markers at the bornes
    ring = list(site.exterior.coords)
    if not site.exterior.is_ccw:
        ring = ring[::-1]
    for a, b in zip(ring, ring[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for k in range(n):
            p = np.array(a) + (np.array(b) - np.array(a)) * k / n
            q = np.array(a) + (np.array(b) - np.array(a)) * (k + 1) / n
            zp, zq = H(np.array([p, q]))
            if ab.buffer(0.5).contains(Point(*((p + q) / 2))):
                zp, zq = hg(*p) - 0.65, hg(*q) - 0.65
            mb.poly("terrain_cut", [(p[0], p[1], zp - 3.0), (q[0], q[1], zq - 3.0), (q[0], q[1], zq), (p[0], p[1], zp)])
    for (x, y) in ring[:-1]:
        z = float(H(np.array([[x, y]]))[0]) if not ab.buffer(0.5).contains(Point(x, y)) else hg(x, y)
        mb.box("kerb", x - 0.15, x + 0.15, y - 0.15, y + 0.15, z - 0.3, z + 0.45)
    obs = mb.build("TERRAIN", col, M)
    return L.join(obs, "TERRAIN_SITE_EMPTY_LAND"), H


# ---------------------------------------------------------------------------------------------
OFFS = {"asphalt": (0.00, "asphalt"), "plaza": (0.12, "pavers"), "lawn": (0.10, "lawn"), "deck": (0.15, "terrace"),
        "play": (0.10, "play"), "court": (0.05, None), "paving": (0.15, "kerb_paving")}


MIN_AREA = {"plaza": 3.0, "deck": 7.0, "lawn": 4.0, "play": 3.0, "paving": 1.0}


def build_ground(M, col, cut, ab, island_at=None):
    """A+B surfaces from the plan, extruded on the grading plane. One continuous asphalt base
    under everything (client, 13-10: no gaps at the tips of the parking teeth); the other
    surfaces sit 5-15 cm above it; leftover slivers under MIN_AREA are dropped (road)."""
    zf = lambda x, y: hg(x, y)
    out = []
    S = SITE["surfaces"]
    water = P(S.get("water", []))
    mb = C.MeshBuilder()
    L.prism(mb, "asphalt", ab.difference(water).difference(cut), -0.65, 0.0, zf=zf)
    out += mb.build("GROUND_ASPHALT_BASE", col, M)
    for key, (off, mat) in OFFS.items():
        if key in ("asphalt", "court"):
            continue
        keep = [g for g in polys(S.get(key, [])) if g.area >= MIN_AREA.get(key, 0)]
        g = unary_union(keep).difference(cut) if keep else Polygon()
        if g.is_empty:
            continue
        if key == "paving" and island_at is not None:
            isl = unary_union([q for q in L.as_polys(g) if q.buffer(0.5).contains(Point(island_at))])
            if not isl.is_empty:
                mbi = C.MeshBuilder()
                L.prism(mbi, "island", isl, -0.65, off, zf=zf)
                out += mbi.build("GROUND_ENTRANCE_ISLAND", col, M)
                g = g.difference(isl.buffer(0.01))
        mb = C.MeshBuilder()
        L.prism(mb, mat, g, -0.65, off, zf=zf)
        out += mb.build(f"GROUND_{key.upper()}", col, M)
    # courts: surfaces and painted lines
    for name, c in SITE["courts"].items():
        mb = C.MeshBuilder()
        g = Polygon(c["surface"]["ext"]).difference(cut)
        L.prism(mb, "tennis" if name == "tennis" else "turf", g, -0.65, 0.05, zf=zf)
        for a, b in c["lines"]:
            paint(mb, a, b, 0.06, 0.05 + 0.006)
        if name == "tennis":
            ln = max(c["lines"], key=lambda l: math.dist(*l))
        out += mb.build(f"COURT_{name.upper()}", col, M)
    # water: tiled basin, walls, water surface
    mb = C.MeshBuilder()
    for w in polys(SITE["surfaces"].get("water", [])):
        w = w.difference(cut)
        for g in L.as_polys(w):
            L.prism(mb, "pool_tile", g, -0.65, -0.60, zf=zf, sides=False)
            L.prism(mb, "pool_tile", g.buffer(-0.01).difference(g.buffer(-0.07)), -0.62, 0.02, zf=zf)
            L.prism(mb, "pool_water", g.buffer(-0.01), -0.14, -0.12, zf=zf, sides=False)
    out += mb.build("GROUND_WATER", col, M)
    return out


def paint(mb, a, b, w, dz):
    a, b = np.array(a), np.array(b)
    t = (b - a) / (np.linalg.norm(b - a) + 1e-9)
    n = np.array([-t[1], t[0]]) * w / 2
    q = [a - n, b - n, b + n, a + n]
    mb.poly("paint_line", [(p[0], p[1], hg(*p) + dz) for p in q])


# ---------------------------------------------------------------------------------------------
def place(src, name, xy, rot_deg, col, z=None):
    ob = bpy.data.objects.new(name, src.data)
    ob.location = (float(xy[0]), float(xy[1]), float(hg(*xy) if z is None else z))
    ob.rotation_euler = (0, 0, math.radians(rot_deg))
    col.objects.link(ob)
    bpy.context.view_layer.update()
    return ob


def snap_axis(long_deg, vec):
    """Return the angle (deg) of the rectangle axis (long or short, either sense) closest to vec."""
    a = math.atan2(vec[1], vec[0])
    best = None
    for k in range(4):
        ang = math.radians(long_deg + 90 * k)
        d = abs((a - ang + math.pi) % (2 * math.pi) - math.pi)
        if best is None or d < best[0]:
            best = (d, ang)
    return math.degrees(best[1])


def main():
    args = sys.argv[1:]
    render = args[args.index("--render") + 1] if "--render" in args else ""
    samples = int(args[args.index("--samples") + 1]) if "--samples" in args else 96
    pct = int(args[args.index("--pct") + 1]) if "--pct" in args else 100
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = L.materials()
    M["terrain_cut"] = M["mod"].simple("T02_Terrain_Cut_Soil", "#8C6E52", 0.95, 0.0, 6.0, 0.35, 0.3)
    M["kerb_paving"] = M["kerb"]
    site = Polygon(SITE["boundary"])
    ab = P(SITE["ab_region"])
    cols = {k: C.collection(k) for k in ("01_TERRAIN", "02_GROUND", "03_DUPLEX", "04_PUBLIC", "05_LANDSCAPE", "06_VEHICLES", "07_CAMERAS", "SRC")}
    cols["SRC"].hide_render = True

    terrain, H = build_terrain(M, cols["01_TERRAIN"], site, ab)

    # ---- buildings ------------------------------------------------------------------------------
    DPX = load("02_duplex.py")
    PUB = load("03_public.py")
    src_dpx = DPX.build(M, cols["SRC"])
    src_adm = PUB.pavilion(M, cols["SRC"], rear_bassin=False)
    src_mkt = PUB.market(M, cols["SRC"])
    pb = SITE["public"]
    for i, d in enumerate(SITE["duplexes"]):
        place(src_dpx, f"DUPLEX_{i + 1:02d}", d["c"], d["front_deg"] + 90, cols["03_DUPLEX"])
    # administration: front (portal, 'Accès' on the plan) towards the central plaza
    a = pb["administration"]
    acc = np.array([47960.5 - 47900, 290339.5 - 290320]) - np.array(a["c"])
    front = snap_axis(a["long_deg"], acc)
    adm = place(src_adm, "ADMINISTRATION", a["c"], front + 90, cols["04_PUBLIC"])
    cut = [Polygon([tuple(adm.matrix_world @ Vector((x, y, 0)))[:2] for x, y in PUB.PLATFORM_FULL.buffer(0.2, join_style=2).exterior.coords])]
    # boutique / restaurant at both clusters drawn on the plan de masse (same building type)
    for key in ("restaurant", "commerce"):
        r = pb[key]
        canal = np.array([86.0, 33.0]) - np.array(r["c"])          # plaza / canal axis
        tw = snap_axis(r["long_deg"], canal)                        # towers end towards the plaza
        rot = tw + 180                                              # local -x (towers) -> plaza
        ob = place(src_mkt, key.upper(), r["c"], rot, cols["04_PUBLIC"])
        cut.append(Polygon([tuple(ob.matrix_world @ Vector((x, y, 0)))[:2] for x, y in PUB.MK_ALL.buffer(1.3, join_style=2).exterior.coords]))
    st = Polygon(pb["station_epuration"]["outline"][0]["ext"])
    so = PUB.station(M, cols["04_PUBLIC"], "STATION_EPURATION", st)
    so.location.z = hg(*st.centroid.coords[0])
    # gatehouse on the entrance island (flat-roofed square on the plan), door towards the entrance (east)
    g = pb["gatehouse"]
    gh = PUB.kiosk(M, cols["04_PUBLIC"], "GATEHOUSE", min(g["size"]), h=3.20)
    gh.location = (g["c"][0], g["c"][1], hg(*g["c"]) + 0.15)
    gh.rotation_euler = (0, 0, math.radians(snap_axis(g["long_deg"], (1.0, 0.0)) + 90))
    # club des résidents and kiosks: hipped roofs drawn on the plan (slopes grouped per building)
    roofs = unary_union([Polygon(r["ext"]).buffer(0.25) for r in SITE["roofs"]])
    for k, rp in enumerate(sorted(L.as_polys(roofs), key=lambda p: -p.area)):
        rp = rp.buffer(-0.25)
        if rp.area < 6 or not ab.contains(rp.centroid):
            continue
        name = "CLUB_DES_RESIDENTS" if rp.area > 100 else ("CLUB_PAVILION" if rp.area > 25 else f"KIOSK_{k:02d}")
        ob = PUB.hipped(M, cols["04_PUBLIC"], name, rp.buffer(-0.40), wall_h=3.40)
        ob.location.z = hg(*rp.centroid.coords[0])
    cutp = unary_union(cut)

    # ---- ground ---------------------------------------------------------------------------------
    build_ground(M, cols["02_GROUND"], cutp, ab, island_at=tuple(pb["gatehouse"]["c"]))

    # ---- pergolas of the jardin aquatique / plaza (Menuiserie Bois slats on the plan) ---------
    adm_zone = cut[0].buffer(1.0)
    slats = [LineString(l) for l in SITE["pergola_lines"] if not adm_zone.intersects(LineString(l))]
    groups = L.as_polys(unary_union([s.buffer(0.35) for s in slats]))
    mb = C.MeshBuilder()
    for gp in groups:
        if gp.area < 6:
            continue
        r = gp.minimum_rotated_rectangle
        q = list(r.exterior.coords)[:4]
        z = hg(*r.centroid.coords[0]) + 0.12
        for x, y in q:
            cx, cy = r.centroid.x, r.centroid.y
            px, py = x + (cx - x) * 0.04, y + (cy - y) * 0.04
            mb.box("timber", px - 0.09, px + 0.09, py - 0.09, py + 0.09, z, z + 2.80)
        for (a, b) in [(q[0], q[1]), (q[2], q[3]), (q[1], q[2]), (q[3], q[0])]:
            beam(mb, a, b, z + 2.80, z + 3.05, 0.10)
        for s in slats:
            if gp.contains(s.centroid):
                (a, b) = list(s.coords)[:2]
                beam(mb, a, b, z + 3.05, z + 3.17, 0.04)
    mb.build("PERGOLAS_PUBLIC", cols["05_LANDSCAPE"], M)

    # ---- fountain on the entrance plaza (circle on the plan) -----------------------------------
    mb = C.MeshBuilder()
    fc = (67.5, 23.0)
    z = hg(*fc) + 0.12
    L.prism(mb, "trim", Point(fc).buffer(2.2, 48).difference(Point(fc).buffer(1.9, 48)), z - 0.2, z + 0.45)
    L.prism(mb, "pool_water", Point(fc).buffer(1.9, 48), z + 0.30, z + 0.32, sides=False)
    L.prism(mb, "trim", Point(fc).buffer(0.45, 24), z, z + 1.1)
    L.prism(mb, "trim", Point(fc).buffer(0.9, 32), z + 1.1, z + 1.25)
    mb.build("FOUNTAIN", cols["05_LANDSCAPE"], M)

    # ---- vegetation -----------------------------------------------------------------------------
    LS = L.bay("09_build_landscape.py")
    src = {
        "green": LS.make_source("GREEN_SHADE_TREE", tree(11, 5.0, 3.6, "green_leaf", 520), M, cols["SRC"]),
        "pink": LS.make_source("PINK_BLOSSOM_TREE", tree(9, 4.5, 3.2, "blossom", 480), M, cols["SRC"]),
        "olive": LS.make_source("OLIVE_TREE", tree(6, 4.0, 3.6, "olive_leaf", 300, card=0.9, gnarl=0.35), M, cols["SRC"]),
        "wash": LS.make_source("WASHINGTONIA", LS.washingtonia(1, 10.0), M, cols["SRC"]),
        "date": LS.make_source("DATE_PALM", LS.date_palm(4, 6.0), M, cols["SRC"]),
    }
    veg = cols["05_LANDSCAPE"]
    nveg = 0

    def plant(key, xy, s=1.0, lift=0.1):
        nonlocal nveg
        ob = bpy.data.objects.new(f"VEG_{key.upper()}_{nveg:03d}", src[key].data)
        ob.location = (xy[0], xy[1], hg(*xy) + lift)
        ob.rotation_euler = (0, 0, RNG.uniform(0, 6.283))
        ob.scale = (s, s, s)
        veg.objects.link(ob)
        nveg += 1

    for t in SITE["trees"]:                                   # street trees drawn on the plan
        plant("green" if RNG.random() < 0.6 else "pink", t["c"], RNG.uniform(0.9, 1.1), 0.15)
    walk = unary_union([P(SITE["surfaces"].get(k, [])) for k in ("paving", "lawn", "plaza", "deck")]).buffer(-0.6)
    for w in polys(SITE["surfaces"]["water"]):                # palms along the canal (INFERRED), never on the road
        if w.area < 200:
            continue
        ring = w.buffer(1.6, join_style=2).exterior
        for k in range(int(ring.length / 9)):
            p = ring.interpolate(k * 9.0)
            if walk.contains(p) and not cutp.buffer(1.0).contains(p):
                plant("wash", (p.x, p.y), RNG.uniform(0.85, 1.1), 0.15)
    # duplex gardens: two trees in each rear garden (INFERRED planting, not on the drawings)
    for i, d in enumerate(SITE["duplexes"]):
        th = math.radians(d["front_deg"] + 90)
        for lx, ly, k in [(-5.0, 9.6, "olive"), (5.2, 9.4, "pink" if i % 2 else "green")]:
            x = d["c"][0] + lx * math.cos(th) - ly * math.sin(th)
            y = d["c"][1] + lx * math.sin(th) + ly * math.cos(th)
            plant(k, (x, y), RNG.uniform(0.75, 0.95), 0.2)
    # club and public lawns: a few palms / olives (INFERRED)
    lawn = P(SITE["surfaces"]["lawn"]).difference(P(SITE["duplex_blocks"]).buffer(1.0))
    for g in L.as_polys(lawn):
        k = int(g.area / 120)
        x0, y0, x1, y1 = g.bounds
        tries = 0
        while k > 0 and tries < 200:
            tries += 1
            p = (RNG.uniform(x0, x1), RNG.uniform(y0, y1))
            if g.buffer(-2.0).contains(Point(p)):
                plant(RNG.choice(["date", "olive", "pink"]), p, RNG.uniform(0.8, 1.05), 0.15)
                k -= 1

    # ---- light, cameras, render settings --------------------------------------------------------
    lt = L.bay("14_build_lighting.py")
    lt.PRESETS["AB_MORNING"] = ((2026, 10, 15), (10, 15), 3.6, 0.95, (1.1, 0.6), 0.0)
    lt.apply("AB_MORNING")
    camera_sky()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = pct
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = -0.7
    cams = make_cameras(cols["07_CAMERAS"])
    d = SITE["duplexes"][2]                    # hero shot of one duplex, from its access side
    f = math.radians(d["front_deg"])
    cx, cy = d["c"]
    eye = (cx + math.cos(f) * 11.8 - math.sin(f) * 9.5, cy + math.sin(f) * 11.8 + math.cos(f) * 9.5)
    cams["CAM_11_DUPLEX_HERO"] = add_cam(cols["07_CAMERAS"], "CAM_11_DUPLEX_HERO", (eye[0], eye[1], 1.6), (cx + math.cos(f) * 3, cy + math.sin(f) * 3, 4.6), 24)
    bpy.context.view_layer.layer_collection.children["SRC"].exclude = True
    sc.camera = cams["CAM_01_AERIAL_AB"]
    if "--no-save" not in args:
        out = os.path.join(ROOT, "Mirleft_Tranche_AB.blend")
        bpy.ops.file.make_paths_relative() if bpy.data.filepath else None
        bpy.ops.wm.save_as_mainfile(filepath=out, compress=True, relative_remap=True)
        print("SAVED", out, round(os.path.getsize(out) / 1e6, 1), "MB")
    if render:
        os.makedirs(os.path.join(ROOT, "renders"), exist_ok=True)
        names = list(cams) if render == "all" else [n for n in cams if any(r in n for r in render.split(","))]
        for n in names:
            sc.camera = cams[n]
            sc.render.filepath = os.path.join(ROOT, "renders", n + ".jpg")
            sc.render.image_settings.file_format = "JPEG"
            sc.render.image_settings.quality = 92
            bpy.ops.render.render(write_still=True)
            print("RENDERED", n, flush=True)


def tree(seed, height, crown, leaf, cards, card=0.55, gnarl=0.18):
    """Round tapered trunk with three limbs and a crown of leaf cards (generated leaf textures of
    the Mirleft Bay project)."""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    seg = 8

    def limb(p0, p1, r0, r1):
        p0, p1 = np.array(p0, float), np.array(p1, float)
        d = p1 - p0
        d /= np.linalg.norm(d)
        a = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.99 else np.array([1.0, 0, 0])
        a /= np.linalg.norm(a)
        b = np.cross(d, a)
        ring = lambda c, rr: [c + (a * math.cos(2 * math.pi * k / seg) + b * math.sin(2 * math.pi * k / seg)) * rr for k in range(seg)]
        A, B = ring(p0, r0), ring(p1, r1)
        for k in range(seg):
            mb.poly("palm_trunk", [tuple(A[k]), tuple(A[(k + 1) % seg]), tuple(B[(k + 1) % seg]), tuple(B[k])])
        mb.poly("palm_trunk", [tuple(v) for v in B])

    th = height * 0.42
    lean = np.array([r.uniform(-1, 1), r.uniform(-1, 1), 0]) * gnarl
    top = np.array([0, 0, th]) + lean
    limb((0, 0, -0.2), top, 0.17, 0.12)
    centre = np.array([0, 0, th + crown * 0.42]) + lean
    for k in range(3):
        an = 2 * math.pi * k / 3 + r.uniform(-0.4, 0.4)
        tip = centre + np.array([math.cos(an), math.sin(an), 0]) * crown * 0.28 + np.array([0, 0, r.uniform(-0.2, 0.4)])
        limb(top, tip, 0.11, 0.05)
    for c in range(cards):
        u = np.array([r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1)])
        u /= np.linalg.norm(u) + 1e-9
        rad = crown * 0.5 * r.uniform(0.35, 1.0) ** 0.5
        p = centre + u * np.array([rad, rad, rad * 0.66])
        nrm = np.array([r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1) + 0.8])
        nrm /= np.linalg.norm(nrm)
        a1 = np.cross(nrm, [0, 0, 1.0]) if abs(nrm[2]) < 0.95 else np.array([1.0, 0, 0])
        a1 /= np.linalg.norm(a1)
        a2 = np.cross(nrm, a1)
        s_ = crown * r.uniform(0.15, 0.24) * card
        q = [p - a1 * s_ - a2 * s_, p + a1 * s_ - a2 * s_, p + a1 * s_ + a2 * s_, p - a1 * s_ + a2 * s_]
        mb.poly(leaf, [tuple(v) for v in q], [(0, 0), (1, 0), (1, 1), (0, 1)])
    return mb


def car_mesh(seed):
    """Saloon / SUV (4.5 x 1.8 m): body, sloped glasshouse, 8-sided wheels. Placeholder cars,
    as drawn on the plan (positions and headings)."""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    Lc, W = r.uniform(4.3, 4.7), r.uniform(1.76, 1.86)
    suv = r.random() < 0.35
    h0, h1, h2 = 0.32, (0.95 if suv else 0.82), (1.62 if suv else 1.42)
    hl, hw = Lc / 2, W / 2
    # lower body with slightly raked nose and tail
    prof = [(-hl, h0 + 0.05), (hl, h0 + 0.05), (hl, h1 - 0.12), (hl - 0.25, h1), (-hl + 0.2, h1), (-hl, h1 - 0.10)]
    for y, flip in ((-hw, False), (hw, True)):
        pts = [(x, y, z) for x, z in prof]
        mb.poly("car", pts[::-1] if flip else pts)
    for (x0, z0), (x1, z1) in zip(prof, prof[1:] + prof[:1]):
        mb.poly("car", [(x0, -hw, z0), (x1, -hw, z1), (x1, hw, z1), (x0, hw, z0)])
    # glasshouse
    f0, f1 = (hl - 1.25, hl - 1.95) if not suv else (hl - 1.0, hl - 1.45)
    b0, b1 = -hl + 0.55, -hl + (0.95 if not suv else 0.62)
    g = [(b0, h1), (f0, h1), (f1, h2), (b1, h2)]
    ins = 0.10
    for y, flip in ((-hw + ins, False), (hw - ins, True)):
        pts = [(x, y, z) for x, z in g]
        mb.poly("car_glass", pts[::-1] if flip else pts)
    for (x0, z0), (x1, z1) in zip(g, g[1:] + g[:1]):
        mat = "car" if abs(z0 - z1) < 1e-6 else "car_glass"
        mb.poly(mat, [(x0, -hw + ins, z0), (x1, -hw + ins, z1), (x1, hw - ins, z1), (x0, hw - ins, z0)])
    # wheels
    for xw in (-hl + 0.78, hl - 0.85):
        for y0, y1 in ((-hw - 0.01, -hw + 0.22), (hw - 0.22, hw + 0.01)):
            ring = [(xw + 0.34 * math.cos(2 * math.pi * k / 10), 0.34 + 0.34 * math.sin(2 * math.pi * k / 10)) for k in range(10)]
            mb.poly("tyre", [(x, y0, z) for x, z in ring])
            mb.poly("tyre", [(x, y1, z) for x, z in ring[::-1]])
            for (xa, za), (xb, zb) in zip(ring, ring[1:] + ring[:1]):
                mb.poly("tyre", [(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)])
    return mb


def camera_sky():
    """Camera rays see a soft coastal sky gradient; lighting still comes from the Nishita sky."""
    nt = bpy.context.scene.world.node_tree
    out = [n for n in nt.nodes if n.type == "OUTPUT_WORLD"][0]
    lit = out.inputs["Surface"].links[0].from_node
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.0, L.srgb("#EAD9C2")
    cr.elements[1].position, cr.elements[1].color = 0.35, L.srgb("#5E9AD3")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(lit.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2])
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


def beam(mb, a, b, z0, z1, w):
    a, b = np.array(a), np.array(b)
    t = (b - a) / (np.linalg.norm(b - a) + 1e-9)
    n = np.array([-t[1], t[0]]) * w / 2
    q = [a - n, b - n, b + n, a + n]
    for j in range(4):
        p0, p1 = q[j], q[(j + 1) % 4]
        mb.poly("timber", [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)])
    mb.poly("timber", [(p[0], p[1], z1) for p in q])
    mb.poly("timber", [(p[0], p[1], z0) for p in q[::-1]])


def make_cameras(col):
    shots = {
        # name: (eye xyz above the plane at eye, target xyz above plane at target, lens)
        "CAM_01_AERIAL_AB": ((-40, -150, 95), (40, 25, 0), 30),
        "CAM_02_AERIAL_SITE": ((-330, -260, 260), (-150, 30, 0), 28),
        "CAM_03_CANAL_PROMENADE": ((-63, 9.7, 2.4), (10, 8.6, 2.0), 24),
        "CAM_04_DUPLEX_FRONTS": ((30, -18, 6.0), (-8, -25, 3.0), 26),
        "CAM_05_ADMINISTRATION": ((80, 18, 2.0), (50, 16, 5.5), 22),
        "CAM_06_PLAZA_CANAL": ((105, 45, 6.0), (60, 25, 3.0), 24),
        "CAM_07_RESTAURANT": ((72, 40, 2.0), (95, 62, 6.0), 24),
        "CAM_08_CLUB_POOLS": ((35, -31, 7.0), (8, -4, 0.5), 24),
        "CAM_09_BIRDSEYE_DUPLEX": ((-60, 70, 45), (-20, 20, 0), 32),
        "CAM_10_TOP_PLAN": ((15, 10, 400), (15, 10.001, 0), 0),
        "CAM_12_ENTRANCE_ISLAND": ((126, 27, 6.5), (108.5, 40.1, 1.5), 26),
    }
    cams = {}
    for n, (e, t, lens) in shots.items():
        cam = add_cam(col, n, e, t, lens)
        cams[n] = cam
    return cams


def add_cam(col, n, e, t, lens):
    if True:
        cam = bpy.data.objects.new(n, bpy.data.cameras.new(n))
        col.objects.link(cam)
        E = Vector((e[0], e[1], hg(e[0], e[1]) + e[2]))
        T = Vector((t[0], t[1], hg(t[0], t[1]) + t[2]))
        cam.location = E
        cam.rotation_euler = (T - E).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens or 50
        if not lens:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = 215
            cam.rotation_euler = (0, 0, 0)
        cam.data.clip_end = 3000
    return cam


if __name__ == "__main__":
    main()
