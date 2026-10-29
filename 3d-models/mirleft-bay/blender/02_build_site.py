"""
02_build_site — graded site surface, kerbed blocks, garden plots, sidewalks, pools, lake, entrance, streets.

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


def ent_poly(r):
    """Rectangle in the entrance frame (a0, a1, b0, b1 px) -> world polygon."""
    return Polygon(C.plan_to_world(D.ent_rect(r)))


def ent_band(a_c, half_px, side=0):
    """Band along the entrance street direction: |a - a_c| <= half_px (side=+1: a >= a_c - half_px)."""
    b0, b1 = -900, 700
    lo, hi = (a_c - half_px, a_c + half_px) if side == 0 else (a_c - 32, a_c + half_px)
    return Polygon(C.plan_to_world([D.ent(lo, b0), D.ent(hi, b0), D.ent(hi, b1), D.ent(lo, b1)]))


def ellipse_world(c, r, n=32):
    return Polygon(C.plan_to_world([(c[0] + r[0] * math.cos(t), c[1] + r[1] * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]))


def open_terrain_under(water, site):
    """The natural terrain runs under the site at grade and would hide the pool floors (1.4 m down):
    delete its faces under the water. The paving and decks (at grade + 2 cm and up) cover the rest
    of each hole, so only the basins show through."""
    import bmesh
    import bpy
    ob = bpy.data.objects.get("TERRAIN_NEAR")
    if ob is None:
        return 0
    zone = prep(water.buffer(4.0).intersection(site.buffer(-0.7)))
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    mw = ob.matrix_world
    dead = [f for f in bm.faces if zone.contains(Point((mw @ f.calc_center_median()).xy))]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(ob.data)
    bm.free()
    return len(dead)


def water_body(name, poly, col, mat_top, h_top, mat_side, h_bottom, step=2.0):
    """Water surface + tiled walls (as before) + a tiled FLOOR at the basin depth, so a transparent
    water material (Blender or D5) shows the blue pool floor instead of the paving below."""
    ob = draped(name, poly, col, mat_top, h_top, mat_side, h_bottom, step=step)
    draped(name.replace("_Water", "_Floor"), poly, col, mat_side, h_bottom, step=step)
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
    channel = ent_poly(D.ENT_CHANNEL)
    (ha, hb), r_loop, r_basin = D.ENT_HALFMOON
    half = Polygon([D.ent(ha + r_basin * math.cos(t), hb + r_basin * math.sin(t)) for t in np.linspace(math.pi / 2, 1.5 * math.pi, 24)])
    half = Polygon(C.plan_to_world(list(half.exterior.coords)))
    small = [ent_poly(r) for r in D.CLUB_BASINS_ENT]
    jac = ellipse_world(D.CLUB_JACUZZI[0], (D.CLUB_JACUZZI[1], D.CLUB_JACUZZI[1]))
    wet = unary_union([lake_poly.buffer(1.2)] + [p.buffer(4.0) for p in pools] + [ch.buffer(1.5)] + [c.buffer(1.5) for c in canals]
                      + [channel.buffer(1.2), half.buffer(1.0), jac.buffer(1.2)] + [q.buffer(1.0) for q in small])
    water_only = unary_union([lake_poly, ch, channel, half, jac] + pools + canals + small)
    C.WATER_ONLY = water_only
    open_terrain_under(water_only, site)
    draped("SITE_Paving", site.difference(water_only), col, M["pavers"], 0.02, step=3.0)
    draped("SITE_Paving_Edge", site.difference(site.buffer(-0.6)), col, M["pavers"], 0.02, M["stone"], -9.0, step=3.0)   # retaining wall at the edges
    # 2. kerbed blocks: sidewalk ring + lawn inset
    road_cuts = unary_union([plan_rect_world(b) for b in D.ROAD_CUTS])
    blocks = []
    for name, b in D.GREEN_BLOCKS:
        if b is None:      # T6 lake park: the plot west of the villa A strip, below the north ring road
            (nx0, ny0), (nx1, ny1) = D.T6_PARK_NORTH
            k = (ny1 - ny0) / (nx1 - nx0)
            cut = Polygon(C.plan_to_world([(1000, ny0 + (1000 - nx0) * k), (2100, ny1), (2100, 3400), (1000, 3400)]))
            poly = site.buffer(-2.5).intersection(cut)
        elif isinstance(b, list):
            poly = Polygon(C.plan_to_world(b)).intersection(site.buffer(-1.0))
        else:
            poly = plan_rect_world(b).intersection(site.buffer(-1.0))
        poly = poly.difference(road_cuts)                 # streets through the villa blocks
        if poly.is_empty:
            continue
        blocks.append((name, poly))
        draped(f"SITE_Block_{name}_Sidewalk", poly.difference(water_only), col, M["pavers"], KERB_H, M["kerb"], 0.0, step=3.0)
        inner = poly.buffer(-SIDEWALK, join_style=2).difference(wet)
        if not inner.is_empty:
            draped(f"SITE_Block_{name}_Lawn", inner, col, M["lawn"], KERB_H + 0.03, step=3.0)
    # T1 / T2 (F01 re-read 2026-10-05): garden plots lawn edge to edge, paved club + plaza zone,
    # rotated entrance blocks (sports, garden, lot borders, mall median, drop-off island)
    for i, b in enumerate(D.T1_PLOTS + D.T2_PLOTS):
        poly = plan_rect_world(b)
        nm = f"T1_PLOT_{i:02d}" if i < len(D.T1_PLOTS) else f"T2_PLOT_{i - len(D.T1_PLOTS):02d}"
        blocks.append((nm, poly))
        draped(f"SITE_{nm}", poly, col, M["lawn"], KERB_H + 0.03, M["kerb"], 0.0, step=2.5)
    street_w = ent_band(D.ENT_STREET_A, 32 + 1)                 # entrance street (8 m) kept clear
    loop = Point(C.plan_to_world([D.ent(ha, hb)])[0]).buffer(r_loop * D.M_PER_PX, 40)
    pub = Polygon(C.plan_to_world(D.T1_PUBLIC_ZONE)).intersection(site.buffer(-D.ROAD_PERIMETER_SIDEWALK))
    zone_full = pub
    pub = pub.difference(ent_poly((D.PLAZA_EDGE_A, 900, -900, 900))).difference(loop)      # straight edge along the street
    strip = ent_poly((D.PLAZA_STRIP_A[0], D.PLAZA_STRIP_A[1], -900, 900)).intersection(zone_full).difference(loop).difference(street_w)
    beds = strip.intersection(ent_poly((D.PLAZA_STRIP_A[0], D.PLAZA_STRIP_A[1], D.PLAZA_BEDS_B[0], D.PLAZA_BEDS_B[1])))
    walk = strip.difference(beds)
    blocks.append(("T1_PLAZA_BEDS", beds))
    blocks.append(("T1_PLAZA_WALK", walk))
    draped("SITE_T1_Plaza_Beds", beds, col, M["lawn"], KERB_H + 0.04, M["kerb"], 0.0, step=1.5)
    draped("SITE_T1_Plaza_Walk", walk, col, M["pavers"], KERB_H, M["kerb"], 0.0, step=2.0)
    C.PLAZA_BEDS, C.PLAZA_WALK = beds, walk
    blocks.append(("T1_PUBLIC_ZONE", pub))
    draped("SITE_T1_Club_Plaza", pub.difference(wet), col, M["terrace"], KERB_H, M["kerb"], 0.0, step=2.5)
    # garden beds of the club (F01: green beds round the lagoon and along the west edge of the zone)
    beds = unary_union([pools[0].buffer(10.0).difference(pools[0].buffer(5.5)),
                        plan_rect_world((5322, 5350, 2320, 2690))]).intersection(pub.buffer(-0.5)).difference(wet)
    beds = beds.difference(Polygon(C.plan_to_world([(5380, 2560), (5600, 2560), (5600, 2700), (5380, 2700)])))   # keep the south deck open
    if not beds.is_empty:
        draped("SITE_T1_Club_Garden_Beds", beds, col, M["lawn"], KERB_H + 0.04, M["kerb"], KERB_H, step=1.5)
    C.CLUB_BEDS = beds
    island = Polygon(C.plan_to_world([D.ent(ha + (r_basin + 12) * math.cos(t), hb + (r_basin + 12) * math.sin(t))
                                      for t in np.linspace(math.pi / 2, 1.5 * math.pi, 28)]))
    blocks.append(("ENT_DROPOFF_ISLAND", island))
    draped("SITE_Ent_DropOff_Island", island.difference(half), col, M["terrace"], KERB_H + 0.02, M["kerb"], 0.0, step=1.5)
    ent_blocks = {"ENT_SPORTS_BLOCK": (D.ENT_SPORTS_BLOCK, "lawn"), "ENT_GARDEN_BLOCK": (D.ENT_GARDEN_BLOCK, "lawn"),
                  "ENT_MALL_MEDIAN": (D.ENT_MALL, "lawn")}
    for nm, (r, kind) in ent_blocks.items():
        poly = ent_poly(r).intersection(site.buffer(-D.ROAD_PERIMETER_SIDEWALK))
        blocks.append((nm, poly))
        draped(f"SITE_{nm}", poly.difference(wet), col, M["lawn"], KERB_H + 0.03, M["kerb"], 0.0, step=2.0)
    for i, r in enumerate(D.ENT_COURTS):
        draped(f"SITE_Ent_Court_{i}", ent_poly(r), col, M["court"], KERB_H + 0.06, step=2.0)
    borders = []
    m = D.M_PER_PX
    for i, (a0, a1, b0, b1) in enumerate(D.ENT_LOTS):       # planted strips on the west and street sides of each lot
        w = D.ENT_LOT_BORDER / m
        for j, r in enumerate(((a0 - w, a0, b0 - w, b1), (a0 - w, a1, b0 - w, b0) if i == 0 else (a0 - w, a1, b1, b1 + w))):
            q = ent_poly(r).intersection(site.buffer(-D.ROAD_PERIMETER_SIDEWALK))
            if q.area > 2.0:
                borders.append(q)
                blocks.append((f"ENT_LOT{i}_BORDER{j}", q))
                draped(f"SITE_Ent_Lot{i}_Border{j}", q, col, M["lawn"], KERB_H + 0.03, M["kerb"], 0.0, step=1.5)
    C.ENT_BORDERS = borders
    C.PUBLIC_ZONE = pub
    # T6 / hotel / T4 (F01 re-read 2026-10-05)
    hz = plan_rect_world(D.HOTEL_ZONE).intersection(site.buffer(-1.0))
    blocks.append(("T6_HOTEL_ZONE", hz))
    draped("SITE_Hotel_Terrace", hz.difference(water_only), col, M["terrace"], KERB_H, M["kerb"], 0.0, step=2.5)
    hg = plan_rect_world(D.HOTEL_GARDEN).difference(wet)
    blocks.append(("T6_HOTEL_GARDEN", hg))
    draped("SITE_Hotel_Garden", hg, col, M["lawn"], KERB_H + 0.04, M["kerb"], KERB_H, step=2.0)
    for i, (c, r) in enumerate(D.HOTEL_BIG_TREES):
        draped(f"SITE_Hotel_TreeCircle_{i}", ellipse_world(c, (r, r)).intersection(hz), col, M["lawn"], KERB_H + 0.04, M["kerb"], KERB_H, step=1.0)
    lp = Polygon(C.plan_to_world(D.LAKE_PLAZA)).buffer(0).difference(lake_poly.buffer(1.2))
    (lcx, lcy), lr = D.LAKE_ROUND
    lp = lp.difference(Polygon(C.plan_to_world([(lcx + lr * math.cos(t), lcy + lr * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)])))
    blocks.append(("T6_LAKE_PLAZA", lp))
    draped("SITE_Lake_Plaza", lp, col, M["terrace"], KERB_H + 0.06, M["kerb"], KERB_H, step=1.5)
    for i, b in enumerate(D.LAKE_BRIDGES):
        draped(f"SITE_Lake_Bridge_{i}", plan_rect_world(b), col, M["timber"], KERB_H + 0.40, M["stone"], -0.4, step=1.5)
    (jx, jy), jr = D.T4_JARDIN_RING
    ring = ellipse_world((jx, jy), (jr, jr)).difference(ellipse_world((jx, jy), (jr - 12, jr - 12)))
    draped("SITE_T4_Jardin_Ring", ring, col, M["terrace"], KERB_H + 0.06, M["kerb"], KERB_H, step=1.0)
    C.HOTEL_ZONE = hz
    C.LAKE_PLAZA = lp
    C.SITE_BLOCKS = blocks

    # 3. lake (T6): three basins + round planted island
    C.LAKE_POLY = lake_poly
    draped("SITE_Lake_Coping", lake_poly.buffer(1.2).difference(lake_poly), col, M["terrace"], KERB_H + 0.08, M["stone"], 0.0, step=2.5)
    water_body("SITE_Lake_Water", lake_poly, col, M["lake_water"], KERB_H + 0.02, M["pool_tile"], -1.2, step=2.5)
    (cx, cy), r = D.LAKE_ROUND
    island = Polygon(C.plan_to_world([(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)]))
    draped("SITE_Lake_Island", island, col, M["lawn"], KERB_H + 0.35, M["stone"], 0.0, step=2.0)
    C.LAKE_ISLAND = island

    # 4. club pools (T1) with stone deck
    for i, pg in enumerate(pools):
        draped(f"SITE_ClubPool_{i}_Deck", pg.buffer(4.0).difference(pg).difference(jac.buffer(1.2)).difference(unary_union(small).buffer(1.0)), col, M["terrace"], KERB_H + 0.08, M["kerb"], 0.0, step=2.0)
        water_body(f"SITE_ClubPool_{i}_Water", pg, col, M["pool_water"], KERB_H + 0.02, M["pool_tile"], -1.4, step=1.5)
    C.CLUB_POOLS = pools

    # 5. hotel water channel + sports court
    draped("SITE_Hotel_Water_Deck", ch.buffer(1.5).difference(ch), col, M["terrace"], KERB_H + 0.08, M["kerb"], 0.0, step=2.0)
    water_body("SITE_Hotel_Water", ch, col, M["pool_water"], KERB_H + 0.02, M["pool_tile"], -1.2, step=2.0)
    for i, cpoly in enumerate(canals):
        draped(f"SITE_Canal_{i}_Coping", cpoly.buffer(1.5, join_style=2).difference(cpoly), col, M["terrace"], KERB_H + 0.10, M["stone"], 0.0, step=2.0)
        water_body(f"SITE_Canal_{i}_Water", cpoly, col, M["pool_water"], KERB_H + 0.04, M["pool_tile"], -0.6, step=2.0)
    draped("SITE_Ent_Channel_Coping", channel.buffer(1.2, join_style=2).difference(channel), col, M["terrace"], KERB_H + 0.10, M["kerb"], 0.0, step=2.0)
    water_body("SITE_Ent_Channel_Water", channel, col, M["pool_water"], KERB_H + 0.04, M["pool_tile"], -0.6, step=2.0)
    water_body("SITE_Ent_HalfMoon_Water", half, col, M["pool_water"], KERB_H + 0.06, M["pool_tile"], -0.6, step=1.5)
    for i, q in enumerate(small):
        water_body(f"SITE_Club_Basin_{i}_Water", q, col, M["pool_water"], KERB_H + 0.04, M["pool_tile"], -0.6, step=1.0)
    draped("SITE_Club_Jacuzzi_Coping", jac.buffer(1.2).difference(jac), col, M["terrace"], KERB_H + 0.12, M["kerb"], 0.0, step=1.0)
    water_body("SITE_Club_Jacuzzi_Water", jac, col, M["pool_water"], KERB_H + 0.06, M["pool_tile"], -0.8, step=1.0)
    C.WET = wet
    roads = build_roads(M, col, site, blocks, wet)
    return dict(blocks=len(blocks), road_m2=round(roads.area))


ASPHALT_H = 0.06            # carriageway sits 4 cm above the paver base (no z-fighting on slopes)
MARK_H = ASPHALT_H + 0.012


def _strip(mb, G, a_, b_, half_w, h=None):
    """Flat white paint strip from a_ to b_ (world xy), draped on the graded site."""
    t = (b_ - a_) / (np.linalg.norm(b_ - a_) + 1e-9)
    w = np.array([-t[1], t[0]]) * half_w
    za, zb = (float(v) + (MARK_H if h is None else h) for v in G(np.array([a_, b_])))
    mb.poly("paint_line", [(a_[0] - w[0], a_[1] - w[1], za), (b_[0] - w[0], b_[1] - w[1], zb),
                           (b_[0] + w[0], b_[1] + w[1], zb), (a_[0] + w[0], a_[1] + w[1], za)])


def build_roads(M, col, site, blocks, wet):
    """F01 street network: asphalt everywhere between the kerbed blocks except the pedestrian zones,
    beige paver sidewalk along the plot edge, white markings (dashed centre lines, edge lines,
    zebra crossings)."""
    G = C.SITE_GRADED
    west = plan_rect_world((D.ROAD_ASPHALT_X_MIN, 7000, 1000, 4000))
    keep_out = unary_union([pg.buffer(0.05) for _, pg in blocks]
                           + [plan_rect_world(b) for b in D.ROAD_PEDESTRIAN]
                           + [wet] + [plan_rect_world(b).buffer(3.0) for _, b, *_ in D.PUBLIC_BUILDINGS if b[0] < 5000])
    asphalt = site.buffer(-D.ROAD_PERIMETER_SIDEWALK).intersection(west).difference(keep_out)
    small_lots = unary_union([plan_rect_world(b) for b in D.T1_SMALL_LOTS])
    exits = unary_union([ent_poly((a0, 260, b0, b1)) for a0, a1, b0, b1 in D.ENT_CARRIAGEWAYS]).intersection(site)   # mall to R104
    asphalt = unary_union([asphalt, small_lots, exits.difference(keep_out)]).buffer(-0.2).buffer(0.2)
    if asphalt.geom_type == "MultiPolygon":
        asphalt = unary_union([g for g in asphalt.geoms if g.area > 25.0])
    draped("SITE_Road_Asphalt", asphalt, col, M["asphalt"], ASPHALT_H, step=3.0)
    C.ROADS = asphalt

    mb = C.MeshBuilder()
    no_mark = unary_union([ent_poly(l) for l in D.ENT_LOTS] + [small_lots.buffer(0.5)])
    # 1. dashed centre lines (3 m dash, 3 m gap, 12 cm wide)
    lines = [LineString(C.plan_to_world(pl)) for pl in D.ROAD_CENTRELINES]
    lines.append(site.buffer(-(D.ROAD_PERIMETER_SIDEWALK + 3.6)).exterior)     # ring road centre
    lines.append(LineString(C.plan_to_world([D.ent(D.ENT_STREET_A, D.ENT_STREET_B[0]), D.ent(D.ENT_STREET_A, D.ENT_STREET_B[1])])))
    inner = prep(asphalt.buffer(-1.2))
    nm_ = prep(no_mark)
    nd = 0
    for ln in lines:
        for d in np.arange(0.0, ln.length - 3.0, 6.0):
            a_, b_ = np.array(ln.interpolate(d).coords[0]), np.array(ln.interpolate(d + 3.0).coords[0])
            if inner.contains(Point(a_)) and inner.contains(Point(b_)) and not nm_.contains(Point((a_ + b_) / 2)):
                _strip(mb, G, a_, b_, 0.06)
                nd += 1
    # 2. solid edge lines 35 cm inside every carriageway edge (not inside the parking lots)
    edge = asphalt.buffer(-0.35)
    rings = []
    for g in ([edge] if edge.geom_type == "Polygon" else list(edge.geoms)):
        rings += [g.exterior] + list(g.interiors)
    ne = 0
    for rg in rings:
        if rg.length < 12.0:
            continue
        for d in np.arange(0.0, rg.length - 1.0, 2.0):
            a_, b_ = np.array(rg.interpolate(d).coords[0]), np.array(rg.interpolate(min(d + 2.0, rg.length)).coords[0])
            if not nm_.contains(Point((a_ + b_) / 2)):
                _strip(mb, G, a_, b_, 0.05)
                ne += 1
    # 3. zebra crossings: 0.5 m stripes every 1 m, 3 m deep, across the road
    o = C.plan_to_world([(0, 0)])[0]
    u = C.plan_to_world([(1, 0)])[0] - o
    v = C.plan_to_world([(0, 1)])[0] - o
    u, v = u / np.linalg.norm(u), v / np.linalg.norm(v)
    ea = C.plan_to_world([D.ent(1, 0)])[0] - C.plan_to_world([D.ent(0, 0)])[0]
    eb = C.plan_to_world([D.ent(0, 1)])[0] - C.plan_to_world([D.ent(0, 0)])[0]
    ea, eb = ea / np.linalg.norm(ea), eb / np.linalg.norm(eb)
    zebras = [(C.plan_to_world([c])[0], (v, u) if rd == "y" else (u, v), w) for c, rd, w in D.ZEBRAS]
    zebras += [(C.plan_to_world([D.ent(a_, b_)])[0], (ea, eb), 5.0) for a_, b_ in D.ENT_ZEBRAS]
    zebras += [(C.plan_to_world([D.ent(D.ENT_STREET_A, bb)])[0], (eb, ea), 8.0) for bb in (-70, 70)]
    for c, (along, across), width in zebras:
        for k in np.arange(-width / 2 + 0.5, width / 2 - 0.3, 1.0):
            p0 = c + across * k - along * 1.5
            _strip(mb, G, p0, p0 + along * 3.0, 0.25)
    mb.build("SITE_Road_Markings", col, M)
    C.ROAD_MARK_COUNTS = {"dashes": nd, "edge_pieces": ne}
    return asphalt
