"""
02_build_site — graded site surface, kerbed blocks, sidewalks, pools, lake, sports court.

Base surface: beige concrete pavers (as-built photo F04). Streets: grey asphalt with white
markings on top, following the catalogue masterplan (client request 2026-10-02).
Block layout, pools and lake: INFERRED from the plan raster (+/- 1.3 m).
"""
import math

import numpy as np
from scipy.spatial import Delaunay
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely.prepared import prep

C = globals()["C"]
D = C.D

KERB_H = 0.15
SIDEWALK = 1.8


def densify(coords, step):
    out = []
    pts = list(coords)
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = np.array(a), np.array(b)
        n = max(1, int(np.linalg.norm(b - a) / step))
        for k in range(n):
            out.append(a + (b - a) * k / n)
    return out


def tri_fill(poly, step):
    """Delaunay triangulation of a (possibly concave / holed) polygon."""
    pts = densify(poly.exterior.coords, step)
    for ring in poly.interiors:
        pts += densify(ring.coords, step)
    minx, miny, maxx, maxy = poly.bounds
    inner = prep(poly.buffer(-step * 0.35))
    for x in np.arange(minx, maxx, step):
        for y in np.arange(miny, maxy, step):
            if inner.contains(Point(x, y)):
                pts.append(np.array([x, y]))
    pts = np.array(pts)
    tri = Delaunay(pts)
    pp = prep(poly)
    faces = [t for t in tri.simplices if pp.contains(Point(pts[t].mean(0)))]
    return pts, faces


def draped(name, poly, col, mat_top, h_top, mat_side=None, h_bottom=None, step=3.0, uv_scale=1.0):
    """Polygon draped on the graded site: top at graded+h_top, optional skirt down to h_bottom."""
    import bpy
    G = C.SITE_GRADED
    if poly.is_empty or poly.area < 0.5:
        return None
    polys = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    V, F, U = [], [], []
    for pg in polys:
        pts, faces = tri_fill(pg, step)
        z = G(pts) + h_top
        base = len(V)
        V += [(p[0], p[1], zz) for p, zz in zip(pts, z)]
        U += [(p[0] * uv_scale, p[1] * uv_scale) for p in pts]
        F += [tuple(int(i) + base for i in (t[0], t[1], t[2])) for t in faces]
    ob = C.mesh_object(name, V, F, col, mat_top, U)
    for poly_ in ob.data.polygons:                    # make every top face point up
        if poly_.normal.z < 0:
            poly_.flip()
    if mat_side is not None and h_bottom is not None:
        SV, SF, SU = [], [], []
        for pg in polys:
            for ring in [pg.exterior] + list(pg.interiors):
                ring_pts = densify(ring.coords, step) + [np.array(ring.coords[0])]
                zt = G(np.array(ring_pts)) + h_top
                zb = G(np.array(ring_pts)) + h_bottom
                s = 0.0
                for k in range(len(ring_pts) - 1):
                    a, b = ring_pts[k], ring_pts[k + 1]
                    i = len(SV)
                    SV += [(a[0], a[1], zb[k]), (b[0], b[1], zb[k + 1]), (b[0], b[1], zt[k + 1]), (a[0], a[1], zt[k])]
                    L = np.linalg.norm(b - a)
                    SU += [(s, zb[k]), (s + L, zb[k + 1]), (s + L, zt[k + 1]), (s, zt[k])]
                    s += L
                    SF.append((i, i + 1, i + 2, i + 3))
        C.mesh_object(name + "_side", SV, SF, col, mat_side, SU)
    return ob


def plan_rect_world(b):
    x0, x1, y0, y1 = b
    return Polygon(C.plan_to_world([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))


def build(materials):
    M = materials
    col = C.collection("01_SITE")
    site = Polygon(C.site_polygon_world())
    C.SITE_POLY = site

    # 1. whole-site paving (roads, parking, plazas)
    draped("SITE_Paving", site, col, M["pavers"], 0.02, M["stone"], -9.0, step=3.0)    # retaining wall at the edges

    # water areas (lake, club pools, hotel channel) are cut out of the lawns
    lake = []
    for x0, x1, y0, y1 in D.LAKE_BASINS:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
        ring = [(cx + rx * math.cos(t) * (1 + 0.06 * math.sin(3 * t + cx)), cy + ry * math.sin(t) * (1 + 0.05 * math.cos(2 * t)))
                for t in np.linspace(0, 2 * math.pi, 64, endpoint=False)]
        lake.append(Polygon(C.plan_to_world(ring)))
    lake_poly = unary_union(lake)
    pools = [Polygon(C.plan_to_world(p)).buffer(0) for p in D.T1_POOLS]
    ch = unary_union([plan_rect_world(b) for b in D.HOTEL_WATER])
    canals = [plan_rect_world(b) for b in D.CANALS]
    plaza = plan_rect_world(D.PLAZA_POOL)
    (hx, hy), hr = D.PLAZA_HALFMOON
    half = Polygon(C.plan_to_world([(hx + hr * math.cos(t), hy + hr * math.sin(t)) for t in np.linspace(-math.pi / 2, math.pi / 2, 24)]))
    wet = unary_union([lake_poly.buffer(1.2)] + [p.buffer(4.0) for p in pools] + [ch.buffer(1.5)] + [c.buffer(1.5) for c in canals] + [plaza.buffer(1.5), half.buffer(1.0)])
    # 2. kerbed blocks: sidewalk ring + lawn inset
    road_cuts = unary_union([plan_rect_world(b) for b in D.ROAD_CUTS])
    blocks = []
    for name, b in D.GREEN_BLOCKS:
        if b is None:      # T6 lake park: the plot west of the villa A strip
            cut = plan_rect_world((1000, 2100, 1500, 3400))
            poly = site.intersection(cut).buffer(-2.5)
        else:
            poly = plan_rect_world(b).intersection(site.buffer(-1.0))
        poly = poly.difference(road_cuts)                 # streets through the villa blocks
        if poly.is_empty:
            continue
        blocks.append((name, poly))
        draped(f"SITE_Block_{name}_Sidewalk", poly, col, M["pavers"], KERB_H, M["kerb"], 0.0, step=3.0)
        inner = poly.buffer(-SIDEWALK, join_style=2).difference(wet)
        if not inner.is_empty:
            draped(f"SITE_Block_{name}_Lawn", inner, col, M["lawn"], KERB_H + 0.03, step=3.0)
    C.SITE_BLOCKS = blocks

    # 3. lake (T6): three basins + round planted island
    C.LAKE_POLY = lake_poly
    draped("SITE_Lake_Coping", lake_poly.buffer(1.2).difference(lake_poly), col, M["terrace"], KERB_H + 0.08, M["stone"], 0.0, step=2.5)
    draped("SITE_Lake_Water", lake_poly, col, M["lake_water"], KERB_H + 0.02, M["pool_tile"], -1.2, step=2.5)
    (cx, cy), r = D.LAKE_ROUND
    island = Polygon(C.plan_to_world([(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)]))
    draped("SITE_Lake_Island", island, col, M["lawn"], KERB_H + 0.35, M["stone"], 0.0, step=2.0)
    C.LAKE_ISLAND = island

    # 4. club pools (T1) with stone deck
    for i, pg in enumerate(pools):
        draped(f"SITE_ClubPool_{i}_Deck", pg.buffer(4.0).difference(pg), col, M["terrace"], KERB_H + 0.08, M["kerb"], 0.0, step=2.0)
        draped(f"SITE_ClubPool_{i}_Water", pg, col, M["pool_water"], KERB_H + 0.02, M["pool_tile"], -1.4, step=1.5)
    C.CLUB_POOLS = pools

    # 5. hotel water channel + sports court
    draped("SITE_Hotel_Water_Deck", ch.buffer(1.5).difference(ch), col, M["terrace"], KERB_H + 0.08, M["kerb"], 0.0, step=2.0)
    draped("SITE_Hotel_Water", ch, col, M["pool_water"], KERB_H + 0.02, M["pool_tile"], -1.2, step=2.0)
    for i, cpoly in enumerate(canals):
        draped(f"SITE_Canal_{i}_Coping", cpoly.buffer(1.5, join_style=2).difference(cpoly), col, M["terrace"], KERB_H + 0.10, M["stone"], 0.0, step=2.0)
        draped(f"SITE_Canal_{i}_Water", cpoly, col, M["pool_water"], KERB_H + 0.04, M["pool_tile"], -0.6, step=2.0)
    draped("SITE_Plaza_Pool_Coping", plaza.buffer(1.2, join_style=2).difference(plaza), col, M["terrace"], KERB_H + 0.10, M["kerb"], 0.0, step=2.0)
    draped("SITE_Plaza_Pool_Water", plaza, col, M["pool_water"], KERB_H + 0.04, M["pool_tile"], -0.6, step=2.0)
    draped("SITE_Plaza_HalfMoon_Water", half, col, M["pool_water"], KERB_H + 0.04, M["pool_tile"], -0.6, step=1.5)
    C.WET = wet
    court = plan_rect_world(D.SPORTS_COURT)
    draped("SITE_Sports_Court", court.buffer(-1.0), col, M["court"], KERB_H, M["kerb"], 0.0, step=3.0)   # orange clay (catalogue)
    roads = build_roads(M, col, site, blocks, wet, court)
    return dict(blocks=len(blocks), road_m2=round(roads.area))


ASPHALT_H = 0.06            # carriageway sits 4 cm above the paver base (no z-fighting on slopes)
MARK_H = ASPHALT_H + 0.012


def build_roads(M, col, site, blocks, wet, court):
    """Masterplan street network: asphalt carriageways between the kerbed blocks, beige paver
    sidewalk along the plot edge, pedestrian promenades kept in pavers, roundabout + access at
    the entrance, white dashed centre lines."""
    import bpy
    G = C.SITE_GRADED
    west = plan_rect_world((D.ROAD_ASPHALT_X_MIN, 7000, 1000, 4000))
    keep_out = unary_union([pg.buffer(0.05) for _, pg in blocks]
                           + [plan_rect_world(b) for b in D.ROAD_PEDESTRIAN]
                           + [wet, court.buffer(1.0)]
                           + [plan_rect_world(b).buffer(3.0) for _, b, _, _ in D.PUBLIC_BUILDINGS])
    (rx, ry), r_out, r_isl = D.ROUNDABOUT
    rc = C.plan_to_world([(rx, ry)])[0]
    m = D.M_PER_PX
    ring_out = Point(rc).buffer(r_out * m, 48)
    island = Point(rc).buffer(r_isl * m, 32)
    (ax0, ay0), (ax1, ay1), aw = D.ENTRANCE_ACCESS
    access = LineString(C.plan_to_world([(ax0, ay0), (ax1, ay1)])).buffer(aw * m / 2, cap_style=2)
    asphalt = site.buffer(-D.ROAD_PERIMETER_SIDEWALK).intersection(west).difference(keep_out)
    asphalt = unary_union([asphalt, ring_out.difference(keep_out), access.intersection(site)]).difference(island)
    asphalt = asphalt.buffer(-0.2).buffer(0.2)                     # drop slivers
    if asphalt.geom_type == "MultiPolygon":
        asphalt = unary_union([g for g in asphalt.geoms if g.area > 25.0])
    draped("SITE_Road_Asphalt", asphalt, col, M["asphalt"], ASPHALT_H, step=3.0)
    draped("SITE_Roundabout_Island", island, col, M["lawn"], KERB_H + 0.05, M["kerb"], 0.0, step=1.5)
    C.ROADS = asphalt
    C.ROUNDABOUT_ISLAND = island

    # markings: dashed centre lines (3 m dash, 3 m gap, 12 cm wide)
    mb = C.MeshBuilder()
    lines = [LineString(C.plan_to_world(pl)) for pl in D.ROAD_CENTRELINES]
    lines.append(site.buffer(-(D.ROAD_PERIMETER_SIDEWALK + 3.6)).exterior)     # ring road centre
    lines.append(Point(rc).buffer((r_out + r_isl) * m / 2, 48).exterior)       # roundabout lane
    inner = prep(asphalt.buffer(-1.2))
    nd = 0
    for ln in lines:
        for d in np.arange(0.0, ln.length - 3.0, 6.0):
            a_, b_ = np.array(ln.interpolate(d).coords[0]), np.array(ln.interpolate(d + 3.0).coords[0])
            if not (inner.contains(Point(a_)) and inner.contains(Point(b_))):
                continue
            t = (b_ - a_) / (np.linalg.norm(b_ - a_) + 1e-9)
            w = np.array([-t[1], t[0]]) * 0.06
            za, zb = (float(v) + MARK_H for v in G(np.array([a_, b_])))
            mb.poly("paint_line", [(a_[0] - w[0], a_[1] - w[1], za), (b_[0] - w[0], b_[1] - w[1], zb),
                                   (b_[0] + w[0], b_[1] + w[1], zb), (a_[0] + w[0], a_[1] + w[1], za)])
            nd += 1
    if nd:
        mb.build("SITE_Road_Markings", col, M)
    return asphalt
