"""
05_build_scene — Mirleft, 1er TRANCHE (plan de masse 12-10), detailed, on the full site boundary.

    python 05_build_scene.py [--render all|NAME,NAME] [--samples 96] [--pct 100] [--no-save]

World frame: metres, x east, y north (the plan's north arrow), origin = DWG (252000, 119430),
z = altitude - 50 m. The 1er TRANCHE is graded on the plane fitted to the plan's contours (the 2013
contours brought over, 5.5 % rising to the east); duplex pads, the restaurant and the commerces sit
at the plane height of their centre; the pool deck is 2.70 m below the graded ground at the top of
its gradins, which climb 1.70 m to an upper walk; planted stone terraces take that walk up to the
lawn by the restaurant terrace (04_pool). The rest of the site keeps the natural terrain of the
contours, blended over 25 m.

Revision 15-10: the restaurant is the pavilion of its own plan (3-PLAN_RESTAURANT_PAVILLON) on the
12-10 axis; the stairs are built (level treads, risers of about 15 cm for the height the ground
gives, flights where the plan draws them); the entrance median is paved, not water; the pedestrian
crossings are painted on the road; no garden wall along the paved band round D-3/D-4. The pool area
is 1.00 m lower; the long stair north of it goes down from the row C lane to its deck.
Second round of 15-10: the pool court in the style of the reference images (stone, planks, planting,
parasols, cabanas); the restaurant portal open on its sides as its facades draw it; the D-4 rear
garden walled, the 'JARDIN' plots beside it in 0.60 m stone planters.
Third round of 15-10: the restaurant's windows, portal arch and frames as FACADE PRINCIPALE draws
them; no water behind the restaurant; the lawn between the pool, the restaurant and the road paved;
the children's pool square to the basin, the in-pool loungers moved to the west deck's row.
Rev 4 (remarks on the D5 model): the duplexes rebuilt to the VILLA N°09 drawing and its reference
images (02_duplex), one design for the twelve pairs; every road and lane of the tranche in beige
herringbone pavers ('pavé beige'), as the commerces' and the restaurant's surrounds; the paved area
between the pool, the restaurant and the road (the playground) in beige slate-look tiles ('carrelage
beige', AZUVI Ardesia Nature type); the pools tiled in green ('carrelage vert', La Platera Jade
type); the commerces at the restaurant's height, all towers in the buildings' colour, the restaurant's
rear entrance as its main door (03_public).
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
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import lib as L  # noqa: E402

C = L.C
SITE = json.load(open(os.path.join(ROOT, "data", "site.json")))
Z0 = 50.0
PLANE = SITE["plane"]
RNG = random.Random(20261014)


def pave_restaurant_lawn():
    """15-10 (third round): the lawn between the pool court, the restaurant and the road is paved.
    Rev 4 (slide 5): that ground, where the playground is, in beige tiles ('court_tile')."""
    r = Point(SITE["restaurant"]["c"])
    keep, move = [], []
    for p in SITE["surfaces"]["lawn"]:
        g = Polygon(p["ext"], p["holes"]).buffer(0)
        (move if g.area > 800 and g.distance(r) < 40 else keep).append(p)
    SITE["surfaces"]["lawn"] = keep
    SITE["surfaces"].setdefault("court_tile", []).extend(move)
    return sum(Polygon(p["ext"], p["holes"]).buffer(0).area for p in move)


def drop_road_strip():
    """15-10: the paved strip the plan draws across the ring road between the fountain and the median
    (from one zebra crossing to the other) is left out at the client's request: road there."""
    zone = box(60.5, -30.0, 66.5, -12.0)
    keep = [p for p in SITE["surfaces"]["paving"] if not zone.contains(Polygon(p["ext"], p["holes"]).buffer(0))]
    n = len(SITE["surfaces"]["paving"]) - len(keep)
    SITE["surfaces"]["paving"] = keep
    return n


def load(fname):
    spec = importlib.util.spec_from_file_location("t1_" + fname[:2], os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    mod.__dict__["L"] = L
    spec.loader.exec_module(mod)
    return mod


def hg(x, y):
    return PLANE[0] * x + PLANE[1] * y + PLANE[2]


def hz(x, y):
    """Graded ground of the tranche: the fitted plane (the pool court builds its own levels)."""
    return hg(x, y)


def polys(lst):
    out = []
    for p in lst:
        g = Polygon(p["ext"], p["holes"]).buffer(0)
        out += L.as_polys(g)
    return out


def P(lst):
    return unary_union(polys(lst)) if lst else Polygon()


def frame(c, rot_deg):
    """local (x, y) -> world (x, y) for an object at c turned by rot_deg."""
    a = math.radians(rot_deg)
    ca, sa = math.cos(a), math.sin(a)
    return lambda x, y: (c[0] + ca * x - sa * y, c[1] + sa * x + ca * y)


def to_world(g, c, rot_deg):
    return affinity.translate(affinity.rotate(g, rot_deg, origin=(0, 0)), c[0], c[1])


def to_local(g, c, rot_deg):
    return affinity.rotate(affinity.translate(g, -c[0], -c[1]), -rot_deg, origin=(0, 0))


# ---------------------------------------------------------------------------------------------
def natural_terrain(bounds):
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
    x0, y0, x1, y1 = bounds
    xs = np.arange(x0 - 20, x1 + 20, 2.0)
    ys = np.arange(y0 - 20, y1 + 20, 2.0)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    Zl = lin(X, Y)
    Zn = near(X, Y)
    Z = np.where(np.isnan(Zl), Zn, Zl)
    Z = gaussian_filter(Z, 3.0)
    return RegularGridInterpolator((xs, ys), Z, bounds_error=False, fill_value=None)


def build_terrain(M, col, site, t1, geo=False):
    """The site's empty land (natural terrain of the contours, blended into the graded tranche over 25 m),
    the cut faces at its edge and the boundary posts; returns H. With geo the real terrain round the site
    (build_surroundings) meets it EDGE lower at the boundary, so the land of the project stands out on
    it with its own soil and a short cut face along its limits."""
    import shapely
    Hn = natural_terrain(site.bounds)
    land = site.difference(t1)
    mb = C.MeshBuilder()
    step = 3.0
    x0, y0, x1, y1 = land.bounds

    def H(xy):
        xy = np.atleast_2d(xy)
        d = shapely.distance(shapely.points(xy), t1)
        w = np.clip(d / 25.0, 0, 1)
        w = w * w * (3 - 2 * w)
        return (1 - w) * np.array([hz(x, y) for x, y in xy]) + w * Hn(xy)

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
        mb.poly("site_land" if geo else "terrain", pts, [(p[0], p[1]) for p in pts])
    ring = list(site.exterior.coords)
    if not site.exterior.is_ccw:
        ring = ring[::-1]
    for a, b in zip(ring, ring[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for k in range(n):
            p = np.array(a) + (np.array(b) - np.array(a)) * k / n
            q = np.array(a) + (np.array(b) - np.array(a)) * (k + 1) / n
            zp, zq = H(np.array([p, q]))
            if t1.buffer(0.5).contains(Point(*((p + q) / 2))):
                zp, zq = hz(*p) - 0.65, hz(*q) - 0.65
            dz = 1.5 if geo else 3.0
            mb.poly("terrain_cut", [(p[0], p[1], zp - dz), (q[0], q[1], zq - dz), (q[0], q[1], zq), (p[0], p[1], zp)])
    for (x, y) in ring[:-1]:
        z = float(H(np.array([[x, y]]))[0]) if not t1.buffer(0.5).contains(Point(x, y)) else hz(x, y)
        mb.box("kerb", x - 0.15, x + 0.15, y - 0.15, y + 0.15, z - 0.3, z + 0.45)
    obs = mb.build("TERRAIN", col, M)
    L.join(obs, "TERRAIN_SITE_EMPTY_LAND")
    return H


GEO = os.path.join(ROOT, "data", "geo")
EDGE, EDGE_FADE = 0.60, 15.0          # the real ground under the site's edge, and over how far it fades out


def geo_material(name, img):
    """Principled BSDF with the satellite image on Base Color (UV), the way D5 and glTF read it."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(GEO, img), check_existing=True)
    t.extension = "EXTEND"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    return m


SOIL = os.path.join(os.path.dirname(ROOT), "mirleft-bay", "output", "d5", "textures", "T01_Terrain_Soil_Sand_Rock_COL.jpg")
SITE_LAND_TINT = (0.624, 0.468, 0.392)   # the soil image darkened to a deeper brown (linear), to stand out on the satellite ground


def site_land_material():
    """The project's land: the soil image (18 m tile, mesh UVs in metres) in a deeper brown than the
    satellite ground round it, so the parcel reads within its limits; D5 gets the same tinted image."""
    m = bpy.data.materials.new("T16_Site_Land_Soil")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    uv = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / 18.0, 1 / 18.0, 1.0)
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(SOIL, check_existing=True)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    mix.inputs["B"].default_value = (*SITE_LAND_TINT, 1.0)
    nt.links.new(uv.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
    nt.links.new(t.outputs["Color"], mix.inputs["A"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Specular IOR Level"].default_value = 0.25
    return m


def build_surroundings(M, col, site, t1, Hsite):
    """The real surroundings from data/geo (10_fetch_geo.py): terrain on the AWS Terrain Tiles heights
    with the Sentinel-2 image on it, ±3 km at 20 m and a far ring to ±12 km at 150 m, and the ocean at
    sea level (altitude 0 = z -50). The site is left open: its own land (build_terrain) fills it. Round
    it the survey heights are moved to meet the site's heights at the boundary, the correction fading
    out over 300 m, and the ground drops EDGE under the site's edge (fading out over EDGE_FADE), so the
    project's land reads on the real ground with a short cut face along its limits."""
    import shapely
    from scipy.interpolate import RegularGridInterpolator
    from scipy.spatial import cKDTree
    G = json.load(open(os.path.join(GEO, "geo.json")))
    dn, df = np.load(os.path.join(GEO, "dem_near.npz")), np.load(os.path.join(GEO, "dem_far.npz"))
    In = RegularGridInterpolator((dn["ys"], dn["xs"]), dn["h"], bounds_error=False, fill_value=None)
    If = RegularGridInterpolator((df["ys"], df["xs"]), df["h"], bounds_error=False, fill_value=None)
    hole = unary_union([site, t1])
    ring = site.exterior
    bp = np.array([ring.interpolate(d).coords[0][:2] for d in np.arange(0, ring.length, 5.0)])
    dB = Hsite(bp) - (In(bp[:, ::-1]) - Z0)
    tree_ = cKDTree(bp)
    print(f"  surroundings: survey vs site heights at the boundary {dB.mean():+.2f} m (min {dB.min():+.2f}, max {dB.max():+.2f})")

    # ocean at sea level: wherever a grid cell has a corner under 1.5 m (the terrain dips under the water
    # there), at 20 m near the site and 150 m beyond; past the far grid, west of its end rows' coast
    def land(xs, ys, h, thr=1.5):
        cells = []
        ok = (h[:-1, :-1] >= thr) & (h[:-1, 1:] >= thr) & (h[1:, :-1] >= thr) & (h[1:, 1:] >= thr)
        for j in range(ok.shape[0]):
            k = 0
            while k < ok.shape[1]:
                if ok[j, k]:
                    k0 = k
                    while k < ok.shape[1] and ok[j, k]:
                        k += 1
                    cells.append(box(xs[k0], ys[j], xs[k], ys[j + 1]))
                else:
                    k += 1
        return unary_union(cells)
    nsq = box(*G["near"])
    xs, ys, h = df["xs"], df["ys"], df["h"]
    ground = unary_union([land(dn["xs"], dn["ys"], dn["h"]), land(xs, ys, h).difference(nsq)])
    def coast_x(j):
        k = 0
        while k < len(xs) - 3 and not (h[j, k] > 2.5 and h[j, k + 1] > 2.5 and h[j, k + 2] > 2.5):
            k += 1
        return xs[k] + 300.0
    E = 40000.0
    sea = box(-E, ys[0], xs[-1], ys[-1]).difference(ground)
    sea = unary_union([sea, box(-E, -E, coast_x(0), ys[0]), box(-E, ys[-1], coast_x(len(ys) - 1), E)])
    sea = unary_union([Polygon(pg.exterior) for pg in L.as_polys(sea)] )   # specks of 'land' out at sea go under
    land_ = box(-E, -E, E, E).difference(sea)
    from shapely.prepared import prep as _prep
    psea = _prep(sea.buffer(-5.0))

    def H(xy, far=False):
        xy = np.atleast_2d(xy)
        h = (If if far else In)(xy[:, ::-1])
        h = h - 7.0 * np.clip((1.5 - h) / 1.5, 0, 1) - Z0          # the survey's sea at 0 m: seabed under the water
        sea_v = shapely.contains_xy(sea.buffer(-5.0), xy[:, 0], xy[:, 1])
        h[sea_v] = np.minimum(h[sea_v], -Z0 - 7.0)
        dist, idx = tree_.query(xy)
        w = np.clip(1 - dist / 300.0, 0, 1)
        h = h + dB[idx] * w * w * (3 - 2 * w)
        if not far:
            nb = dist < EDGE_FADE + 5.0
            if nb.any():
                db = shapely.distance(shapely.points(xy[nb]), hole.boundary)
                on = db < 0.05                                     # on the boundary: the site's height
                hb = h[nb]
                f = np.clip(db / EDGE_FADE, 0, 1)
                hb = hb - EDGE * (1 - f * f * (3 - 2 * f))
                if on.any():
                    hb[on] = Hsite(xy[nb][on]) - EDGE
                h[nb] = hb
        return h

    from shapely.prepared import prep
    pt1 = prep(hole)
    out = []
    for key, d, far, img in (("NEAR", dn, False, "sat_near.jpg"), ("FAR", df, True, "sat_far.jpg")):
        xs, ys = d["xs"], d["ys"]
        X0, X1, Y0, Y1 = xs[0], xs[-1], ys[0], ys[-1]
        nx0, ny0, nx1, ny1 = G["near"]
        M["geo_" + key] = geo_material(f"GEO_Satellite_{key.title()}", img)
        mat = "geo_" + key
        tris = []
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                cx0, cx1, cy0, cy1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
                if far and cx0 >= nx0 - 1e-3 and cx1 <= nx1 + 1e-3 and cy0 >= ny0 - 1e-3 and cy1 <= ny1 + 1e-3:
                    continue                                       # inside the near square
                cell = box(cx0, cy0, cx1, cy1)
                if not far and pt1.intersects(cell):
                    if pt1.contains(cell):
                        continue
                    for g in L.as_polys(cell.difference(hole)):
                        tris += [tuple(t) for t in L.tri_poly(g)]
                else:
                    a, b, c, e = (cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)
                    tris += [(a, b, c), (a, c, e)]
        V = np.array([p for t in tris for p in t])
        Z = H(V, far)
        mb = C.MeshBuilder()
        uv = lambda x, y: ((x - X0) / (X1 - X0), (y - Y0) / (Y1 - Y0))
        for k in range(len(tris)):
            pts = [(V[3 * k + m][0], V[3 * k + m][1], Z[3 * k + m]) for m in range(3)]
            mb.poly(mat, pts, [uv(p[0], p[1]) for p in pts])
        edge = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1), (X0, Y0)]          # skirt round the square
        step = xs[1] - xs[0]
        for a, b in zip(edge, edge[1:]):
            n = max(1, int(round(math.dist(a, b) / step)))
            P_ = [np.array(a) + (np.array(b) - np.array(a)) * k / n for k in range(n + 1)]
            zz = H(np.array(P_), far)
            for k in range(n):
                p, q = P_[k], P_[k + 1]
                lo = -Z0 - 60.0 if far else min(zz[k], zz[k + 1]) - 6.0
                mb.poly(mat, [(p[0], p[1], lo), (q[0], q[1], lo), (q[0], q[1], zz[k + 1]), (p[0], p[1], zz[k])],
                        [uv(*p), uv(*q), uv(*q), uv(*p)])
        obs = mb.build("TERRAIN_SURROUND_" + key, col, M)
        ob = L.join(obs, "TERRAIN_SURROUND_" + key)
        L.weld(ob, 0.001)
        out.append(ob)
        print(f"  surroundings {key}: {len(tris)} triangles")
    mb = C.MeshBuilder()
    M["ocean_t1"] = M["mod"].simple("H04_Ocean_Atlantic", "#1E5A6C", 0.10, 0.0, 0.04, 0.20, 0.25)
    for pg in L.as_polys(sea):
        if pg.area > 50:
            L.prism(mb, "ocean_t1", pg, -Z0 - 0.02, -Z0, sides=False)
    ob = L.join(mb.build("OCEAN", col, M), "OCEAN_ATLANTIC")
    out.append(ob)
    coast = [(coast_x(j) - 300.0, 0) for j in range(len(ys))]
    print(f"  ocean at sea level, coast {np.mean([c[0] for c in coast]):.0f} m west of the centre on average")
    return out


# ---------------------------------------------------------------------------------------------
# ground of the tranche: one base (the roads), the plan's surfaces 2-15 cm above it. Rev 4: roads, lanes
# and the surrounds of the commerces and the restaurant in beige herringbone pavers, the playground
# ground in beige tiles
OFFS = [("lane", 0.02, "pave_beige"), ("ramp", 0.03, "concrete"), ("stabilise", 0.08, "stabilise"), ("concrete", 0.12, "concrete"),
        ("paving", 0.15, "kerb_paving"), ("terrace", 0.15, "pave_beige"), ("terracotta", 0.15, "pave_beige"),
        ("court_tile", 0.15, "tile_ardesia"), ("lawn", 0.12, "lawn")]
MIN_AREA = {"paving": 0.6, "lawn": 0.5}


def build_ground(M, col, t1, cut):
    zf = hz
    S = SITE["surfaces"]
    out = []
    mb = C.MeshBuilder()
    # 19-10: the roads next to the villas in beige pavers like the lanes (slide 3: 'toutes les voies de
    # circulation attenantes au duplex'); the entrance, the ring road, the median roads and the parking
    # in grey road pavers so they read as roads
    near = unary_union([to_world(DPX_FOOT, d["c"], d["rot_deg"]) for d in SITE["duplexes"]]).buffer(26.0)
    base = t1.difference(cut)
    L.prism(mb, "pave_beige", base.intersection(near), -0.65, 0.0, zf=zf)
    L.prism(mb, "pave_road", base.difference(near), -0.65, 0.0, zf=zf)
    out += mb.build("GROUND_ROADS_PAVERS", col, M)
    for key, off, mat in OFFS:
        keep = [g for g in polys(S.get(key, [])) if g.area >= MIN_AREA.get(key, 0.05)]
        g = unary_union(keep).difference(cut) if keep else Polygon()
        if g.is_empty:
            continue
        mb = C.MeshBuilder()
        L.prism(mb, mat, g, -0.65, off, zf=zf)
        out += mb.build(f"GROUND_{key.upper()}", col, M)
    return out


def build_water(M, col, cut):
    """Bassins (restaurant, entrance median) and the fountain: raised stone rim, tiled basin."""
    mb = C.MeshBuilder()
    fountain = [Polygon(w["poly"]["ext"], w["poly"]["holes"]) for w in SITE["water"] if w["kind"] == "fountain"]
    for w in SITE["water"]:
        if w["kind"] != "bassin":
            continue
        g = Polygon(w["poly"]["ext"], w["poly"]["holes"]).buffer(0)
        z = hz(*g.centroid.coords[0])
        L.prism(mb, "coping", g.buffer(0.25, join_style=2).difference(g), z - 0.30, z + 0.35)
        L.prism(mb, "pool_tile", g, z - 0.45, z - 0.40, sides=False)
        L.prism(mb, "pool_tile", g.buffer(0.01, join_style=2).difference(g.buffer(-0.01, join_style=2)), z - 0.40, z + 0.30)
        L.prism(mb, "pool_water", g.buffer(-0.01, join_style=2), z + 0.18, z + 0.20, sides=False)
        for r in g.interiors:                                       # planters inside the bassin
            pl = Polygon(r)
            L.prism(mb, "coping", L.ring_poly(pl, 0.12), z - 0.40, z + 0.45)
            L.prism(mb, "lawn", pl.buffer(-0.12, join_style=2), z - 0.40, z + 0.40, sides=False)
    if fountain:
        f = unary_union([g.buffer(0.10) for g in fountain])
        hull = f.convex_hull
        z = hz(*hull.centroid.coords[0])
        L.prism(mb, "coping", hull.buffer(0.35).difference(hull), z - 0.30, z + 0.55)
        L.prism(mb, "coping", hull.difference(f), z - 0.30, z + 0.42)
        for g in fountain:
            L.prism(mb, "pool_tile", g, z - 0.10, z - 0.05, sides=False)
            L.prism(mb, "pool_water", g.buffer(-0.02), z + 0.30, z + 0.32, sides=False)
            c = g.representative_point()
            L.prism(mb, "bronze", c.buffer(0.04, 8), z + 0.30, z + 0.55)
    return mb.build("GROUND_BASSINS_FOUNTAIN", col, M)


def build_median(M, col):
    """Entrance median: no water (15-10 request). The two beds the plan hatches are paved flush with the
    median's border, in diagonal stripes of dark slate and light travertine like the hatch."""
    mb = C.MeshBuilder()
    for w in SITE["water"]:
        if w["kind"] != "median":
            continue
        g = Polygon(w["poly"]["ext"], w["poly"]["holes"]).buffer(0)
        rr = list(g.minimum_rotated_rectangle.exterior.coords)
        e = max(((rr[i], rr[i + 1]) for i in range(2)), key=lambda ab: math.dist(*ab))
        ang = math.degrees(math.atan2(e[1][1] - e[0][1], e[1][0] - e[0][0])) + 45.0
        c = g.centroid
        gl = affinity.rotate(g, -ang, origin=c)
        x0, y0, x1, y1 = gl.bounds
        k, y = 0, y0
        while y < y1:
            strip = affinity.rotate(gl.intersection(box(x0 - 1, y, x1 + 1, y + 0.25)), ang, origin=c)
            for q in L.as_polys(strip):
                L.prism(mb, "slate" if k % 2 == 0 else "deck_stone", q, -0.65, 0.15, zf=hz)
            k, y = k + 1, y + 0.25
    return mb.build("GROUND_MEDIAN_PAVING", col, M)


def build_road_paint(M, col):
    """Pedestrian crossings from the plan (15-10 request): white paint on the road, no thickness."""
    mb = C.MeshBuilder()
    for r in SITE.get("road_paint", []):
        g = Polygon(r["poly"]["ext"], r["poly"]["holes"]).buffer(0)
        cx, cy = g.centroid.coords[0]
        off = ground_top(cx, cy) - hz(cx, cy) + 0.006
        L.prism(mb, "paint", g, off - 0.002, off, zf=hz, sides=False)
    return mb.build("ROAD_PAINT_CROSSINGS", col, M)


def build_walls(M, col, DPX, openings=Polygon()):
    mb = C.MeshBuilder()
    zf = hz
    houses = unary_union([to_world(DPX.RDC, d["c"], d["rot_deg"]) for d in SITE["duplexes"]])
    garden = unary_union([Polygon(w["poly"]["ext"], w["poly"]["holes"]).buffer(0) for w in SITE["walls"] if w["kind"] == "garden"])
    # rev 4 (19-10): the garden walls were cut to the permit house; close the gaps the wider villa N°09
    # leaves (up to 1.2 m) so every wall meets its façade, and fill the small steps between wall pieces
    r = 0.60
    shut = unary_union([garden, houses]).buffer(r, join_style=2).buffer(-r, join_style=2).difference(garden).difference(houses)
    patches = [q for q in L.as_polys(shut) if q.area < 0.8 and q.distance(garden) < 1e-3]
    garden = unary_union([garden] + patches).difference(houses).difference(openings)   # opened at the gates
    print(f"  garden wall gaps closed: {len(patches)}")
    # 19-10: D-1 to D-4 open onto their lane at the front (plan 12-10: no wall drawn there); the tall
    # garden walls in front of the houses become the villa drawing's low stone wall with its coping
    fronts = unary_union([to_world(box(-14.0, -14.0, 14.0, -7.40), d["c"], d["rot_deg"]) for d in SITE["duplexes"] if d["type"] == "B"])
    low = garden.intersection(fronts)
    garden = garden.difference(fronts)
    for g in L.as_polys(low):
        if g.area < 0.02:
            continue
        L.prism(mb, "cladding", g, -0.40, 0.70, zf=zf)
        L.prism(mb, "coping_beige", g.buffer(0.04, join_style=2).intersection(low.buffer(0.04, join_style=2)), 0.70, 0.78, zf=zf)
    for g in L.as_polys(garden):
        L.prism(mb, "render", g, -0.40, 1.80, zf=zf)
        L.prism(mb, "trim", g.buffer(0.03, join_style=2).difference(houses), 1.80, 1.85, zf=zf)
    for w in SITE["walls"]:
        if w["kind"] in ("pool", "retaining", "garden"):
            continue                                                # pool court walls: built with the court
        g = Polygon(w["poly"]["ext"], w["poly"]["holes"]).buffer(0)
        mat, cap = ("stone", "deck_stone") if w["kind"] == "planter" else ("render", "trim")
        L.prism(mb, mat, g, -0.40, w["h"], zf=zf)
        L.prism(mb, cap, g.buffer(0.03, join_style=2), w["h"], w["h"] + 0.05, zf=zf)
    lawn = P(SITE["surfaces"]["lawn"])
    for p in polys(SITE["planters"]):                              # 'Jardin' beds: raised planters
        if p.area < 0.6:
            continue
        # rev 4 (19-10): the bed takes the lawn strip the plan leaves round it (no grass outside its wall)
        p = unary_union([p, lawn.intersection(p.buffer(0.20, join_style=2))]).buffer(0.02, join_style=2).buffer(-0.02, join_style=2)
        p = max(L.as_polys(p), key=lambda q: q.area)
        L.prism(mb, "render", L.ring_poly(p, 0.12), -0.30, 0.45, zf=zf)
        L.prism(mb, "trim", L.ring_poly(p.buffer(0.02, join_style=2), 0.16), 0.45, 0.50, zf=zf)
        L.prism(mb, "lawn", p.buffer(-0.12, join_style=2), -0.30, 0.38, zf=zf, sides=False)
    return mb.build("WALLS_PLANTERS", col, M)


_TOPS = {}


def ground_top(x, y):
    """Height of the finished ground at (x, y): the graded plane plus the offset of the surface there."""
    if not _TOPS:
        from shapely.prepared import prep
        for key, off, _ in OFFS:
            g = P(SITE["surfaces"].get(key, []))
            _TOPS[key] = (prep(g), off)
    p = Point(x, y)
    for key, (g, off) in _TOPS.items():
        if g.contains(p):
            return hz(x, y) + off
    return hz(x, y)


RISER = 0.15
POOL_DROP = 1.00       # the pool court lowered 1.00 m more (15-10 request), its gradins top with it
DPX_FOOT = None
PAV_DY = 1.30          # restaurant pavilion: its centre on the 12-10 axis, 1.30 m behind the block's centre


def stair_plan(eA, eB, flights, zB=None):
    """Levels of a built stair from end A to end B: the ground there (or zB, a fixed level at B).
    Flights where the plan draws them, each with its share of the risers; their number comes from
    the height to climb (risers of about RISER m), the walk between the flights is level."""
    eA, eB = np.array(eA, float), np.array(eB, float)
    Lt = float(np.linalg.norm(eB - eA))
    ax = (eB - eA) / Lt
    zA = ground_top(*(eA - ax * 0.4))
    zB = ground_top(*(eB + ax * 0.4)) if zB is None else zB
    dz = zB - zA
    n_tot = max(len(flights), int(round(abs(dz) / RISER)))
    drawn = sum(f[2] for f in flights)
    ns = [max(1, int(round(n_tot * f[2] / drawn))) for f in flights]
    ns[-1] = max(1, n_tot - sum(ns[:-1]))
    risers = []
    for (t0, t1, _), n in zip(flights, ns):
        risers += [0.5 * (t0 + t1)] if n == 1 else [t0 + (t1 - t0) * j / (n - 1) for j in range(n)]
    return {"eA": eA, "ax": ax, "nr": np.array([-ax[1], ax[0]]), "Lt": Lt, "zA": zA, "zB": zB, "dz": dz,
            "h": dz / sum(ns), "risers": sorted(risers), "flights": flights, "n": sum(ns)}


def stair_level(sp, t):
    """Tread level of the stair at distance t from end A."""
    return sp["zA"] + sp["h"] * sum(1 for r in sp["risers"] if r <= t)


POOL_STAIR_MATS = {"tread": "planks", "nose": "coping", "cheek": "stone", "cap": "deck_stone"}


def solid_stair(mb, sp, width, pad=0.15, cheeks=(), mats=None):
    """The stair of stair_plan(), wall to wall: level treads, vertical risers, a dark stone nosing at
    each step, a slim handrail on the centre line over each flight (the plan's centre line).
    cheeks: sides (+1 left of A->B, -1 right) that get a retaining wall where the ground beside the
    stair is higher than its treads; an end wall closes B the same way. mats: tread / nose / cheek / cap
    materials (default light pavers, dark stone nosings, render cheeks)."""
    mats = mats or {"tread": "terrace", "nose": "slate", "cheek": "render", "cap": "trim"}
    eA, ax, nr, Lt, zA, zB, h = sp["eA"], sp["ax"], sp["nr"], sp["Lt"], sp["zA"], sp["zB"], sp["h"]
    flights, risers = sp["flights"], sp["risers"]
    ns = [sum(1 for r in risers if f[0] - 1e-6 <= r <= f[1] + 1e-6) for f in flights]
    W = lambda t, s: tuple(eA + ax * t + nr * s)
    quad = lambda t0, t1, s0, s1: Polygon([W(t0, s0), W(t1, s0), W(t1, s1), W(t0, s1)])
    zb = min(zA, zB) - 0.60
    edges = [0.0] + risers + [Lt]
    for k in range(len(edges) - 1):
        z = zA + h * k
        L.prism(mb, mats["tread"], quad(edges[k], edges[k + 1], -width / 2 - pad, width / 2 + pad), zb, z)
    for k, t in enumerate(risers):                        # dark stone nosing band at each step edge
        z = zA + h * (k + 1) if h > 0 else zA + h * k
        t0, t1 = (t, t + 0.30) if h > 0 else (t - 0.30, t)
        L.prism(mb, mats["nose"], quad(t0, t1, -width / 2, width / 2), z - 0.02, z + 0.005, sides=False)
        L.prism(mb, mats["nose"], quad(t - 0.004, t + 0.004, -width / 2, width / 2), z - abs(h), z)
    for (t0, t1, _), n in zip(flights, ns):              # centre handrail over the flight
        a, b = max(0.0, t0 - 0.40), min(Lt, t1 + 0.40)
        za = zA + h * sum(1 for r in risers if r < a)
        zb_ = zA + h * sum(1 for r in risers if r < b)
        m = max(2, int((b - a) / 1.4) + 1)
        for j in range(m):                                # posts from the tread up to the sloping rail
            t = a + (b - a) * j / (m - 1)
            zt = zA + h * sum(1 for r in risers if r <= t)
            zr = za + (zb_ - za) * (t - a) / (b - a) + 0.90
            p = W(t, 0.0)
            L.prism(mb, "bronze", Point(p).buffer(0.025, 6), zt, zr)
        pa, pb = np.array(W(a, 0.0)), np.array(W(b, 0.0))
        seg = 12
        for j in range(seg):
            u0, u1 = j / seg, (j + 1) / seg
            q0, q1 = pa + (pb - pa) * u0, pa + (pb - pa) * u1
            z0_, z1_ = za + (zb_ - za) * u0 + 0.90, za + (zb_ - za) * u1 + 0.90
            mb.poly("bronze", [(q0[0] - nr[0] * 0.025, q0[1] - nr[1] * 0.025, z0_), (q1[0] - nr[0] * 0.025, q1[1] - nr[1] * 0.025, z1_),
                               (q1[0] + nr[0] * 0.025, q1[1] + nr[1] * 0.025, z1_), (q0[0] + nr[0] * 0.025, q0[1] + nr[1] * 0.025, z0_)])
    e_ = width / 2 + pad
    for side in cheeks:                                   # retaining cheeks where the ground is higher
        for k in range(len(edges) - 1):
            t0, t1 = edges[k], edges[k + 1]
            m = max(1, int((t1 - t0) / 1.5 + 0.999))
            for j in range(m):
                a_, b_ = t0 + (t1 - t0) * j / m, t0 + (t1 - t0) * (j + 1) / m
                g = ground_top(*W(0.5 * (a_ + b_), side * (e_ + 0.45)))
                z = zA + h * k
                if g > z + 0.05:
                    s0, s1 = sorted((side * e_, side * (e_ + 0.20)))
                    L.prism(mb, mats["cheek"], quad(a_, b_, s0, s1), zb, g + 0.05)
                    L.prism(mb, mats["cap"], quad(a_, b_, s0, s1).buffer(0.03, join_style=2), g + 0.05, g + 0.10)
    if cheeks:
        g = ground_top(*(eA + ax * (Lt + 0.45)))
        if g > zB + 0.05:
            L.prism(mb, mats["cheek"], quad(Lt, Lt + 0.20, -e_ - 0.20, e_ + 0.20), zb, g + 0.05)
            L.prism(mb, mats["cap"], quad(Lt, Lt + 0.20, -e_ - 0.20, e_ + 0.20).buffer(0.03, join_style=2), g + 0.05, g + 0.10)
    return quad(0.0, Lt, -width / 2 - pad, width / 2 + pad)


# ---------------------------------------------------------------------------------------------
def place(src, name, xy, rot_deg, col, z=None):
    ob = bpy.data.objects.new(name, src.data)
    ob.location = (float(xy[0]), float(xy[1]), float(hz(*xy) if z is None else z))
    ob.rotation_euler = (0, 0, math.radians(rot_deg))
    col.objects.link(ob)
    return ob


def main():
    args = sys.argv[1:]
    render = args[args.index("--render") + 1] if "--render" in args else ""
    samples = int(args[args.index("--samples") + 1]) if "--samples" in args else 96
    pct = int(args[args.index("--pct") + 1]) if "--pct" in args else 100
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print(f"  lawn by the restaurant paved: {pave_restaurant_lawn():.0f} m2")
    print(f"  paved strip across the ring road removed: {drop_road_strip()}")
    M = L.materials()
    M["terrain_cut"] = M["mod"].simple("T10_Terrain_Cut_Soil", "#8C6E52", 0.95, 0.0, 6.0, 0.35, 0.3)
    M["kerb_paving"] = M["kerb"]
    M["site_land"] = site_land_material()
    site = Polygon(SITE["boundary"])
    t1 = P(SITE["t1_region"])
    cols = {k: C.collection(k) for k in ("00_SURROUNDINGS", "01_TERRAIN", "02_GROUND", "03_DUPLEX", "04_PUBLIC", "05_POOL", "06_LANDSCAPE", "06_TREES_PALMS", "07_CAMERAS", "SRC")}
    cols["SRC"].hide_render = True

    POOL = load("04_pool.py")
    pc = SITE["pool"]
    fw = frame(pc["c"], pc["rot_deg"])
    z_deck = hg(*fw(POOL.GRAD_F[3], 0.0)) - POOL.RISE - POOL_DROP
    geo = os.path.exists(os.path.join(GEO, "geo.json"))
    Hsite = build_terrain(M, cols["01_TERRAIN"], site, t1, geo=geo)
    if geo:                                   # the real terrain and the ocean round the site (10_fetch_geo)
        build_surroundings(M, cols["00_SURROUNDINGS"], site, t1, Hsite)

    # ---- duplexes ------------------------------------------------------------------------------
    DPX = load("02_duplex.py")
    PUB = load("03_public.py")
    global DPX_FOOT
    DPX_FOOT = DPX.FOOT
    dpx = DPX.build(M, cols["SRC"], "N09")                 # one design (villa N°09) for both blocks
    src = {"A": dpx, "B": dpx}
    for d in SITE["duplexes"]:
        name = "DUPLEX_" + "_".join(u.replace("-", "") for u in d["units"])
        place(src[d["type"]], name, d["c"], d["rot_deg"], cols["03_DUPLEX"])

    # ---- public buildings -----------------------------------------------------------------------
    cut = []
    r = SITE["restaurant"]
    # restaurant = the pavilion of its own plan (15-10 request), on the axis of the 12-10 block, moved
    # 1.30 m back; round it the 12-10 plan de masse (last round of 15-10): no platform, the plan's two
    # bassins at its front corners, its two pergolas behind the rear towers on a rear terrace, the
    # TERRASSE RESTAURANT paving all round. Floor (+0.20) at the highest ground under it, stone base downhill
    fr_ = frame(r["c"], r["rot_deg"])
    pav_c = fr_(0.0, PAV_DY)
    bassins = [to_local(Polygon(w["poly"]["ext"], w["poly"]["holes"]).buffer(0), pav_c, r["rot_deg"])
               for w in SITE["water"] if w["kind"] == "resto_bassin"]
    rfoot = unary_union([PUB.PAV_SOLIDS, PUB.REAR_TERRACE] + [Polygon(b.exterior).buffer(0.25, join_style=2) for b in bassins])
    fl = to_world(rfoot, pav_c, r["rot_deg"])
    z_pav = max(hz(x, y) for x, y in fl.exterior.coords[:-1]) - 0.20
    z_low = min(hz(*fl.exterior.interpolate(d).coords[0][:2]) for d in np.linspace(0, fl.exterior.length, 120))
    plinth = min(-1.00, z_low - z_pav - 0.30)          # its base below the lowest ground round it
    place(PUB.pavilion(M, cols["SRC"], plinth=plinth, site_bassins=bassins), "RESTAURANT", pav_c, r["rot_deg"], cols["04_PUBLIC"], z=z_pav)
    print(f"  restaurant: floor {z_pav + 0.20 + Z0:.2f} m, base {plinth:.2f} m below it")
    cut.append(to_world(unary_union([PUB.PAV_SOLIDS.buffer(-0.01, join_style=2), PUB.REAR_TERRACE]
                                    + [Polygon(b.exterior).buffer(0.25, join_style=2) for b in bassins]), pav_c, r["rot_deg"]))
    # pads of the commerces: the entrance side at the ground level (the slope rises to the east)
    c = SITE["commerces"]
    place(PUB.commerces(M, cols["SRC"]), "COMMERCES_1_2", c["c"], c["rot_deg"], cols["04_PUBLIC"], z=hz(*frame(c["c"], c["rot_deg"])(6.0, -4.0)))
    cut.append(to_world(PUB.C_FOOT.buffer(0.15, join_style=2), c["c"], c["rot_deg"]))
    for kind, s in PUB.C_STAIRS:
        cut.append(to_world(s.buffer(0.15, join_style=2), c["c"], c["rot_deg"]))
    for w in PUB.C_WELLS:
        cut.append(to_world(w, c["c"], c["rot_deg"]))
    k = SITE["toilet_kiosk"]
    kio = PUB.kiosk(M, cols["04_PUBLIC"], "TOILETTE_PLAZA", k["size"], h=3.20)
    kio.location = (k["c"][0], k["c"][1], hz(*k["c"]) + 0.15)
    kio.rotation_euler = (0, 0, math.radians(k["rot_deg"] + 180))
    pt = SITE["petanque"]
    fpt = frame(pt["c"], pt["rot_deg"])
    pet = PUB.petanque(M, cols["04_PUBLIC"], zf=lambda x, y: hz(*fpt(x, y)) - hz(*pt["c"]))
    pet.location = (pt["c"][0], pt["c"][1], hz(*pt["c"]) + 0.08)
    pet.rotation_euler = (0, 0, math.radians(pt["rot_deg"]))

    # ---- pool court -------------------------------------------------------------------------------
    ground = lambda u, v: hz(*fw(u, v)) - z_deck
    wp = {}
    for kind in ("pool", "kids_pool"):
        g = unary_union([Polygon(w["poly"]["ext"], w["poly"]["holes"]) for w in SITE["water"] if w["kind"] == kind])
        wp[kind] = to_local(g, pc["c"], pc["rot_deg"])
    # the upper level east of the gradins keeps clear of the road's footway, which cuts its south-east corner
    win = box(12.50, -25.0, 20.0, -10.0)
    foot = [to_local(g, pc["c"], pc["rot_deg"]) for g in polys(SITE["surfaces"]["paving"])]
    POOL.layout(ground, unary_union([g for g in foot if g.intersects(win)]))
    # the long stair north of the court ('ESCALIERS' 1-10 and 11-21): from the row C lane down into the
    # sunken court, landing on the deck at its north-east corner through an opening in the north wall;
    # that wall is its 1 m guard over the court
    sp_n = stair_plan(fw(-12.40, 22.175), fw(8.70, 22.175), [(0.0, 5.50, 10), (14.30, 19.80, 11)], zB=z_deck)
    ed = [0.0] + sp_n["risers"] + [sp_n["Lt"]]
    north_steps = [(-12.40 + ed[k], -12.40 + ed[k + 1], sp_n["zA"] + sp_n["h"] * k - z_deck) for k in range(len(ed) - 1)]
    pool_ob, spots = POOL.build(M, cols["SRC"], ground, wp, north_steps=north_steps, north_gap=(7.40, 8.70))
    place(pool_ob, "POOL_COURT", pc["c"], pc["rot_deg"], cols["05_POOL"], z=z_deck)
    pool_ob.users_collection[0].objects.unlink(pool_ob)
    pfoot = to_world(POOL.footprint(), pc["c"], pc["rot_deg"])
    cut.append(pfoot)
    for st in POOL.LAY["ups"]:
        print(f"  pool upper stair v {st['v0']:.2f}-{st['v1']:.2f}: rise {st['zT'] - POOL.RISE:.2f} m, {st['n']} risers of {st['h']:.3f} m")
    ltw = polys(SITE["local_technique_walls"])
    lt = PUB.local_technique(M, cols["05_POOL"], ltw)
    lt.location.z = z_deck
    src_lounger = POOL.lounger(M, cols["SRC"])
    loungers = [l for l in SITE["loungers"] if to_local(Point(l["c"]), pc["c"], pc["rot_deg"]).x > 0]   # east deck, as drawn
    loungers += [{"c": fw(u, v), "rot_deg": pc["rot_deg"], "n": 1} for u, v in POOL.WEST_LOUNGERS]   # west: one even row
    for i, l in enumerate(loungers):
        a = math.radians(l["rot_deg"])
        # backrest away from the pool, so that they face it (15-10)
        cx, cy = l["c"]
        to_pool = np.array(pc["c"]) - np.array([cx, cy])
        if np.dot(to_pool, [math.cos(a), math.sin(a)]) > 0:
            a += math.pi
        offs = [0.0] if l["n"] == 1 else [-0.42, 0.42]
        for j, o in enumerate(offs):
            x, y = cx - math.sin(a) * o, cy + math.cos(a) * o
            ob = bpy.data.objects.new(f"LOUNGER_{i:02d}_{j}", src_lounger.data)
            ob.location = (x, y, z_deck)
            ob.rotation_euler = (0, 0, a)
            cols["05_POOL"].objects.link(ob)
    src_par = POOL.parasol(M, cols["SRC"])                      # the plan's 'PR' circles of the east deck
    for i, (u, v) in enumerate(POOL.PARASOLS):
        ob = bpy.data.objects.new(f"PARASOL_{i:02d}", src_par.data)
        ob.location = (*fw(u, v), z_deck)
        ob.rotation_euler = (0, 0, math.radians(pc["rot_deg"] + 22.5 * (i % 2)))
        cols["05_POOL"].objects.link(ob)
    src_cab = POOL.cabana(M, cols["SRC"])                       # reference images: cabanas on the west deck
    for i, (u, v) in enumerate(POOL.CABANAS):
        ob = bpy.data.objects.new(f"CABANA_{i:02d}", src_cab.data)
        ob.location = (*fw(u, v), z_deck)
        ob.rotation_euler = (0, 0, math.radians(pc["rot_deg"]))
        cols["05_POOL"].objects.link(ob)
    fountain = [Polygon(w["poly"]["ext"], w["poly"]["holes"]) for w in SITE["water"] if w["kind"] == "fountain"]
    if fountain:                          # its basin is cut from the ground: the blue floor shows under the water
        cut.append(unary_union([g.buffer(0.10) for g in fountain]).convex_hull.buffer(0.35))
    # rev 4 (19-10): the tree pits in front of the villas are removed, with their trees
    dpx_zone = unary_union([to_world(DPX.FOOT, d["c"], d["rot_deg"]) for d in SITE["duplexes"]]).buffer(5.0)
    gone = {i for i, t in enumerate(SITE["trees"]) if t["kind"] == "pit" and dpx_zone.contains(Point(t["c"]))}
    pits = [Point(t["c"]).buffer(0.60, 6) for i, t in enumerate(SITE["trees"]) if t["kind"] == "pit" and i not in gone]
    print(f"  tree pits removed by the villas: {len(gone)}, kept: {len(pits)}")
    cut.extend(pits)
    # the villas' rear terraces (plan RDC): on the graded ground, the lawn cut round them
    terraces = [(to_world(DPX.REAR_TERRACE, d["c"], d["rot_deg"]), hz(*d["c"])) for d in SITE["duplexes"]]
    cut.extend(g for g, _ in terraces)
    # entrance of each villa (villa N°09, façade principale): from the lane through the gate to the door.
    # Where the plan puts lawn or a garden wall in the way (19-10: the gate opened onto a wall), the wall
    # is opened in front of the gate and a paved path runs through to the lane
    lawn_all = P(SITE["surfaces"]["lawn"])
    walls_g = unary_union([Polygon(w["poly"]["ext"], w["poly"]["holes"]).buffer(0) for w in SITE["walls"] if w["kind"] == "garden"])
    ENTRY_CUT, entries = [], []
    for d in SITE["duplexes"]:
        for sx in (1, -1):
            a0, a1 = sorted((sx * 3.88, sx * 4.97))
            b0, b1 = sorted((sx * 3.50, sx * 4.97))
            out_ = to_world(box(a0, -11.0, a1, -7.32), d["c"], d["rot_deg"])
            ins_ = to_world(box(b0, -7.07, b1, -3.47), d["c"], d["rot_deg"])
            ENTRY_CUT.append(to_world(box(a0, -11.0, a1, -7.40), d["c"], d["rot_deg"]))
            g = unary_union([out_.intersection(unary_union([lawn_all, walls_g])), ins_.intersection(lawn_all)])
            g = unary_union([q for q in L.as_polys(g) if q.area > 0.05])
            if not g.is_empty:
                entries.append(g)
    cut.extend(entries)
    print(f"  villa entrance paths through lawn or walls: {len(entries)}")
    # stairs: across the rows ('ESC 16-17', 'ESC V4', flights read from the plan) and the long stair
    # north of the pool court ('ESCALIERS' 1-10 and 11-21, landing between)
    stair_specs = [(s["name"], stair_plan(s["axis"][0], s["axis"][1], s["flights"]), s["width"], (), None) for s in SITE["stairs"]]
    stair_specs.append(("ESCALIERS NORD PISCINE", sp_n, 3.45, (1,), POOL_STAIR_MATS))
    mb_st = C.MeshBuilder()
    for name, sp, w_, cheeks, mats in stair_specs:
        cut.append(solid_stair(mb_st, sp, w_, cheeks=cheeks, mats=mats))
        print(f"  stair {name}: rise {sp['dz']:+.2f} m, {sp['n']} risers of {abs(sp['h']):.3f} m")
    mb_st.build("STAIRS", cols["02_GROUND"], M)
    cutp = unary_union(cut)

    # ---- ground, water, walls, road paint ---------------------------------------------------------
    build_ground(M, cols["02_GROUND"], t1, cutp)
    build_water(M, cols["02_GROUND"], cutp)
    build_median(M, cols["02_GROUND"])
    build_walls(M, cols["02_GROUND"], DPX, unary_union(ENTRY_CUT))
    mb = C.MeshBuilder()
    for g, zpad in terraces:                   # follows the slope, never above the salons' floor (+0.20)
        L.prism(mb, "terrace", g, -0.65, 0.0, zf=lambda x, y, zpad=zpad: min(hz(x, y) + 0.16, zpad + 0.17))
    for g in entries:
        L.prism(mb, "pave_beige", g, -0.65, 0.15, zf=hz)
    mb.build("DUPLEX_REAR_TERRACES_ENTRANCES", cols["02_GROUND"], M)
    build_road_paint(M, cols["02_GROUND"])

    # ---- street furniture: meter cabinets ('Emplacement compteur') and bin enclosures ------------
    mb = C.MeshBuilder()
    for f in SITE["street_furniture"]:
        w, d, h = (0.90, 0.35, 1.40) if f["kind"] == "meter" else (0.80, 0.60, 1.10)
        g = to_world(box(-w / 2, -d / 2, w / 2, d / 2), f["c"], f["rot_deg"])
        L.prism(mb, "render", g, -0.20, h, zf=lambda x, y: hz(x, y) + 0.15)
        L.prism(mb, "trim", g.buffer(0.03, join_style=2), h, h + 0.05, zf=lambda x, y: hz(x, y) + 0.15)
    mb.build("STREET_FURNITURE", cols["06_LANDSCAPE"], M)

    # ---- tree pits: the plan's Ø 1.2 m circles ('1.2m'), a kerb ring around soil -----------------
    mb = C.MeshBuilder()
    for g in pits:
        L.prism(mb, "kerb", g.difference(g.buffer(-0.08, 6)), -0.20, 0.17, zf=hz)
        L.prism(mb, "soil", g.buffer(-0.08, 6), -0.20, 0.09, zf=hz, sides=False)
    mb.build("TREE_PITS", cols["02_GROUND"], M)

    # ---- vegetation --------------------------------------------------------------------------------
    LS = L.bay("09_build_landscape.py")
    srcv = {
        "green": LS.make_source("GREEN_SHADE_TREE", tree(11, 5.0, 3.6, "green_leaf", 520), M, cols["SRC"]),
        "olive": LS.make_source("OLIVE_TREE", tree(6, 4.0, 3.6, "olive_leaf", 300, card=0.9, gnarl=0.35), M, cols["SRC"]),
        "pit": LS.make_source("STREET_TREE", tree(17, 4.2, 2.8, "green_leaf", 360), M, cols["SRC"]),
        # clipped crown on a 1.85 m stem, no lean; planted at half width: a 0.17 m stem, a crown
        # about 0.8 m wide and 1 m tall, within 0.59 m of the stem
        "standard": LS.make_source("CLIPPED_STANDARD_TREE", tree(23, 4.4, 1.60, "green_leaf", 220, card=0.70, gnarl=0.0), M, cols["SRC"]),
        "wash": LS.make_source("WASHINGTONIA", LS.washingtonia(1, 9.0), M, cols["SRC"]),
        "date": LS.make_source("DATE_PALM", LS.date_palm(4, 5.0), M, cols["SRC"]),
        "shrub": LS.make_source("SHRUB_MOUND", bush(31, "olive_leaf"), M, cols["SRC"]),
        "shrub_pink": LS.make_source("SHRUB_FLOWERING", bush(47, "blossom", cards=90), M, cols["SRC"]),
        "agave": LS.make_source("AGAVE", POOL.agave(3), M, cols["SRC"]),
        "agave_b": LS.make_source("AGAVE_SMALL", POOL.agave(8, n=14, length=0.45), M, cols["SRC"]),
        "grass": LS.make_source("ORNAMENTAL_GRASS", LS.grass_clump(5), M, cols["SRC"]),
    }
    veg = cols["06_LANDSCAPE"]
    nveg = [0]

    def plant(key, xy, s=1.0, z=None, sz=None):
        if key == "shrub" and RNG.random() < 0.25:
            key = "shrub_pink"                                   # a flowering one now and then
        ob = bpy.data.objects.new(f"VEG_{key.upper()}_{nveg[0]:03d}", srcv[key].data)
        ob.location = (xy[0], xy[1], (hz(*xy) + 0.12) if z is None else z)
        ob.rotation_euler = (0, 0, RNG.uniform(0, 6.283))
        ob.scale = (s, s, s if sz is None else sz)
        (veg if key.startswith(("shrub", "agave", "grass")) else cols["06_TREES_PALMS"]).objects.link(ob)
        nveg[0] += 1

    court = to_world(POOL.COURT, pc["c"], pc["rot_deg"])
    bld = unary_union([to_world(DPX.FOOT, d["c"], d["rot_deg"]) for d in SITE["duplexes"]])   # villa N°09 + rear terrace
    n_skip = 0
    for i_t, t in enumerate(SITE["trees"]):
        if i_t in gone:
            continue
        xy = t["c"]
        q = to_local(Point(xy), pav_c, r["rot_deg"])            # trees of the 12-10 layout on the pavilion:
        if (rfoot.buffer(0.6).contains(q) or PUB.PAV_SOLIDS.distance(q) < (1.8 if t["kind"] == "palm" else 2.6)
                or any(pg.buffer(0.6).contains(q) for pg in PUB.PERGOLAS_1210)):
            n_skip += 1                                          # in its bassins, pergolas or against its walls
            continue
        z = z_deck + POOL.BAC_SOIL if court.buffer(0.5).contains(Point(xy)) else None
        if t["kind"] == "palm":                                 # symbol 0.23-0.68 m radius on the plan: young palms
            plant("date", xy, 0.38 + 0.45 * min(t["r"], 0.7), z)
        elif t["kind"] == "olive":
            plant("olive", xy, 0.45 + 0.55 * min(t["r"], 0.85), z)
        elif t["kind"] == "washingtonia":
            plant("wash", xy, RNG.uniform(0.9, 1.05), z)
        elif t["kind"] == "shade":
            plant("green", xy, RNG.uniform(0.85, 1.0), z)
        elif bld.distance(Point(xy)) < 1.5:                    # pits drawn against a façade
            plant("standard", xy, min(0.5, 0.5 * (bld.distance(Point(xy)) - 0.02) / 0.59), hz(*xy) + 0.09, sz=1.0)
        else:
            plant("pit", xy, RNG.uniform(0.85, 1.0), hz(*xy) + 0.09)
    print("  trees of the 12-10 layout left out on the pavilion:", n_skip)
    # rev 4: a low planted strip behind each villa's stone front wall (front reference image)
    for d in SITE["duplexes"]:
        fd = frame(d["c"], d["rot_deg"])
        for s in (1, -1):
            for x in np.arange(5.75, 8.50, 0.70):
                plant("shrub", fd(s * x, -6.80), RNG.uniform(0.75, 0.95))
    for u, v, z, kind, s in spots:                                   # pool court beds (reference images)
        plant(RNG.choice(("agave", "agave_b")) if kind == "agave" else kind, fw(u, v), s, z_deck + z)
    print("  pool court plants:", len(spots))
    # the plan's 'JARDIN' beds of the pool block outside the court: the west strip at the lawn level,
    # the beds north of the long stair inside their 0.60 m stone planter walls (soil at 0.50)
    pwalls = unary_union([Polygon(w["poly"]["ext"], w["poly"]["holes"]).buffer(0) for w in SITE["walls"] if w["kind"] == "planter"])
    mb = C.MeshBuilder()
    n_out = 0
    for p in polys(SITE["pool_beds"]):
        for q in L.as_polys(p.difference(pfoot.buffer(0.05))):
            if q.area < 1.0:
                continue
            raised = q.distance(pwalls) < 0.30 if not pwalls.is_empty else False
            if raised:
                q = q.difference(pwalls)
                L.prism(mb, "soil", q, -0.30, 0.50, zf=hz, sides=False)
            x0, y0, x1, y1 = q.bounds
            for _ in range(int(q.area / 0.9)):
                pt = Point(RNG.uniform(x0, x1), RNG.uniform(y0, y1))
                if not q.buffer(-0.25).contains(pt):
                    continue
                k = RNG.choices(("shrub", "grass", "agave", "agave_b"), (0.40, 0.30, 0.15, 0.15))[0]
                zt = hz(pt.x, pt.y) + 0.50 if raised else ground_top(pt.x, pt.y)
                plant(k, (pt.x, pt.y), RNG.uniform(0.8, 1.2), zt)
                n_out += 1
    mb.build("POOL_BLOCK_JARDIN_SOIL", cols["02_GROUND"], M)
    print("  plants in the pool block's other beds:", n_out)
    for p in polys(SITE["planters"]):                                # shrubs in the raised beds (INFERRED planting)
        if p.area < 1.5:
            continue
        r_ = p.minimum_rotated_rectangle
        n = max(1, int(p.area / 2.5))
        x0, y0, x1, y1 = p.bounds
        tries = 0
        while n > 0 and tries < 60:
            tries += 1
            q = Point(RNG.uniform(x0, x1), RNG.uniform(y0, y1))
            if p.buffer(-0.35).contains(q):
                plant("shrub", (q.x, q.y), RNG.uniform(0.8, 1.2), hz(q.x, q.y) + 0.38)
                n -= 1

    # ---- light, cameras, render settings --------------------------------------------------------
    lt_ = L.bay("14_build_lighting.py")
    lt_.PRESETS["T1_MORNING"] = ((2026, 10, 15), (10, 15), 3.6, 0.95, (1.1, 0.6), 0.0)
    lt_.apply("T1_MORNING")
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
    cams = make_cameras(cols["07_CAMERAS"], z_deck)
    bpy.context.view_layer.layer_collection.children["SRC"].exclude = True
    sc.camera = cams["CAM_01_AERIAL_T1"]
    if "--no-save" not in args:
        out = os.path.join(ROOT, "Mirleft_Tranche_1.blend")
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
    """Round tapered trunk with three limbs and a crown of leaf cards (leaf textures of the
    Mirleft Bay project)."""
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


def bush(seed, leaf, cards=120, r=0.46, h=0.62):
    """Mediterranean shrub (rosemary / lavender / bougainvillea habit), about 0.9 m across and 0.6 m
    high: a mound of leaf cards (leaf textures of the Mirleft Bay project). INFERRED planting."""
    rr = random.Random(seed)
    mb = C.MeshBuilder()
    for _ in range(cards):
        u = np.array([rr.gauss(0, 1), rr.gauss(0, 1), abs(rr.gauss(0, 1))])
        u /= np.linalg.norm(u) + 1e-9
        k = rr.uniform(0.45, 1.0) ** 0.5
        p = np.array([u[0] * r * k, u[1] * r * k, 0.05 + u[2] * h * k])
        nrm = np.array([rr.gauss(0, 1), rr.gauss(0, 1), rr.gauss(0, 1) + 0.9])
        nrm /= np.linalg.norm(nrm)
        a1 = np.cross(nrm, [0, 0, 1.0]) if abs(nrm[2]) < 0.95 else np.array([1.0, 0, 0])
        a1 /= np.linalg.norm(a1)
        a2 = np.cross(nrm, a1)
        s_ = r * rr.uniform(0.22, 0.34)
        q = [p - a1 * s_ - a2 * s_, p + a1 * s_ - a2 * s_, p + a1 * s_ + a2 * s_, p - a1 * s_ + a2 * s_]
        mb.poly(leaf, [tuple(v) for v in q], [(0, 0), (1, 0), (1, 1), (0, 1)])
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


def make_cameras(col, z_deck):
    d = {"/".join(x["units"]): x for x in SITE["duplexes"]}
    pc = SITE["pool"]
    fw = frame(pc["c"], pc["rot_deg"])
    r = SITE["restaurant"]
    fr = frame(r["c"], r["rot_deg"])
    cm = SITE["commerces"]
    fc = frame(cm["c"], cm["rot_deg"])
    pt = SITE["petanque"]
    fp = frame(pt["c"], pt["rot_deg"])
    dA = d["D-17/D-18"]
    fa = frame(dA["c"], dA["rot_deg"])
    dB = d["D-1/D-2"]
    fb = frame(dB["c"], dB["rot_deg"])
    shots = {
        # name: (eye xy, eye height above the plane, target xy, target height, lens)
        "CAM_01_AERIAL_T1": ((115, -118), 82, (2, 8), 0, 30),
        "CAM_02_AERIAL_FROM_WEST": ((-175, -30), 95, (5, 10), 0, 30),
        "CAM_03_POOL_COURT": (fw(-11.6, -15.6), 4.2, fw(9.0, 5.0), 1.0, 20),
        "CAM_04_RESTAURANT": (fr(4.0, -32.0), 1.8, fr(0.0, 0.0), 6.0, 24),
        "CAM_05_COMMERCES_PLAZA": (fc(20.0, -24.0), 11.0, fc(0.0, -1.0), 2.0, 24),
        "CAM_06_LANE_ROWS": (fa(-24.0, -11.2), 1.7, fa(30.0, -11.2), 3.0, 24),
        "CAM_07_DUPLEX_A_HERO": (fa(6.5, -11.0), 1.7, fa(0.0, -1.0), 4.6, 18),
        "CAM_08_DUPLEX_B_D1_D2": (fb(4.2, -12.0), 2.2, fb(0.0, -1.0), 5.0, 18),
        "CAM_09_PETANQUE": (fp(8.0, -24.0), 3.0, fp(-3.0, 4.0), 1.0, 24),
        "CAM_10_ENTRANCE_FOUNTAIN": ((99.0, -19.0), 2.0, (58.0, -20.0), 3.0, 22),
        "CAM_11_GARDENS_BIRDSEYE": ((-115.0, 20.0), 45, (-40.0, 20.0), 0, 32),
        "CAM_12_TOP_PLAN": ((5.0, 5.0), 400, (5.0, 5.001), 0, 0),
        "CAM_13_STAIR_ESC_V4": ((-6.5, 3.0), 1.75, (-20.0, 14.0), 0.6, 24),
    }
    cams = {}
    for n, (e, eh, t, th, lens) in shots.items():
        cam = bpy.data.objects.new(n, bpy.data.cameras.new(n))
        col.objects.link(cam)
        ez = (z_deck if n == "CAM_03_POOL_COURT" else hz(*e)) + eh
        tz = (z_deck if n == "CAM_03_POOL_COURT" else hz(*t)) + th
        E = Vector((e[0], e[1], ez))
        T = Vector((t[0], t[1], tz))
        cam.location = E
        cam.rotation_euler = (T - E).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens or 50
        if not lens:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = 240
            cam.rotation_euler = (0, 0, 0)
        cam.data.clip_end = 40000
        cams[n] = cam
    return cams


if __name__ == "__main__":
    main()
