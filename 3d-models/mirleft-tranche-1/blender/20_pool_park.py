"""
20_pool_park — the last part of the site, west of Tranche 3 on the cliff over the Atlantic (client 26-10: "zid had
partie lakhriya w pscine dira f chi chkel machi nfs chi likayn f plan because this pscine is the important things
bghiaha dkun naaadya"). A DESIGN PROPOSAL, not the plan's: the plan draws three round basins with bridges and a
round kiosk; here the ground, graded on the plane at Tranche 3's level (client 26-10: not sunk), steps down to the
cliff in four terraces held by stone walls, the pools cascading down them towards the ocean:
  the arrival terrace by Tranche 3: the pool bar (a flat-roofed block in the residence's render, its cornice, a
    mashrabiya window, the counter opening onto the view) under a cedar pergola, loungers along the parapet;
  the main pool, the important one: a long sinuous infinity pool (lobes 6 to 10 m deep from its edge) whose water
    runs over the green zellige wall in one sheet into the lagoon 2.6 m below; a palm island in its widest lobe, a sun
    shelf (0.35 m deep) along its inner edge with loungers in the water, travertine decks, parasols, palms;
  the lagoon terrace: the lagoon at the foot of the waterfall, its decks, loungers and palms, lawn;
  the lower terrace: two round jacuzzis, a children's pool, three cabanas (daybeds under timber and canvas)
    facing the sunset, lawn and olive trees;
  the planted tip over the cliff, a path to the belvedere on it (a stone platform with its parapet, a timber
    pergola and benches).
Stairs alongside the walls join the terraces. Everything follows the ground of 05 (H); the site's empty land is
cut away in the zone (envelope()).
"""
import json
import math
import os
import random

import bpy
import numpy as np
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box
from shapely.ops import linemerge, substring, unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = json.load(open(os.path.join(ROOT, "data", "site.json")))
T2 = json.load(open(os.path.join(ROOT, "data", "t2_site.json")))
T3 = json.load(open(os.path.join(ROOT, "data", "t3_site.json")))
RNG = random.Random(20261026)

# the terraces: (lowest ground they take, their level); below the last one, the planted tip. Client 26-10 ("ard
# ... machi dji ghr9a, drja3 nfs mostawa dyal akhrin"): the zone is graded on the plane as Tranche 3 (05), so the
# terraces step down from Tranche 3's level, not from the natural slope under it
TERRACES = ((-4.3, -3.8), (-6.0, -6.0), (-7.3, -8.6), (-8.6, -9.0))
WALL, PARAPET = 0.40, 0.95          # retaining walls: thickness, parapet over the upper level
POOL_D, LAG_D = 1.40, 0.90          # depths of the main pool and of the lagoon


def _zone():
    site = Polygon(SITE["boundary"]).buffer(0)
    built = unary_union([Polygon(r["ext"]).buffer(0) for r in SITE["t1_region"]]
                        + [Polygon(T2["env"]["ext"]).buffer(0), Polygon(T3["env"]["ext"]).buffer(0)])
    rest = site.difference(built)
    return max(L.as_polys(rest), key=lambda g: g.area).buffer(0)


ZONE = _zone()


def envelope():
    """The pool park's ground: the site's empty land is cut away there (05 build_terrain)."""
    return ZONE


def _smooth(g, r=2.0):
    return g.buffer(r, join_style=1).buffer(-2 * r, join_style=1).buffer(r, join_style=1).simplify(0.2)


def build(M, B, srcv, H):
    """B: the 05_build_scene module, srcv: its plant sources, H: its terrain height function. Returns the T4
    cameras."""
    hz = lambda x, y: float(H(np.array([[x, y]]))[0])
    cols = {k: C.collection(k) for k in ("T4_01_GROUND", "T4_02_POOLS", "T4_03_LANDSCAPE", "T4_04_TREES_PALMS")}
    nveg = [0]

    def put(key, xy, z, s=1.0):
        if key == "shrub" and RNG.random() < 0.3:
            key = "shrub_pink"
        ob = bpy.data.objects.new(f"T4_VEG_{key.upper()}_{nveg[0]:03d}", srcv[key].data)
        ob.location = (float(xy[0]), float(xy[1]), z)
        ob.rotation_euler = (0, 0, RNG.uniform(0, 6.283))
        ob.scale = (s, s, s)
        (cols["T4_03_LANDSCAPE"] if key.startswith(("shrub", "agave", "grass")) else cols["T4_04_TREES_PALMS"]).objects.link(ob)
        nveg[0] += 1

    # ---- the terraces from the ground: {H >= t} smoothed, nested ------------------------------------------
    x0, y0, x1, y1 = ZONE.bounds
    st = 1.5
    xs, ys = np.arange(x0 - st, x1 + st, st), np.arange(y0 - st, y1 + st, st)
    XY = np.array([(x + st / 2, y + st / 2) for x in xs for y in ys])
    HZ = H(XY)
    cums, prev = [], Polygon()
    for t, _ in TERRACES:
        cells = [box(x, y, x + st, y + st) for (x, y), h in zip(XY - st / 2, HZ) if h >= t]
        g = _smooth(unary_union(cells), 3.0).simplify(0.6).union(prev).intersection(ZONE)
        cums.append(g)
        prev = g
    bands, prev = [], Polygon()
    for g, (t, lev) in zip(cums, TERRACES):
        b_ = unary_union([q for q in L.as_polys(g.difference(prev)) if q.area > 25.0])
        bands.append((b_, lev))
        prev = g
    slope = unary_union([q for q in L.as_polys(ZONE.difference(prev)) if q.area > 5.0])
    print("  T4: terraces", ", ".join(f"{lev:.1f}: {b_.area:.0f} m2" for b_, lev in bands), f"slope {slope.area:.0f} m2")
    (bA, zA), (bB, zB), (bC, zC), (bD, zD) = bands

    def shared(upper, lower):
        """the longest line between two terraces"""
        g = upper.boundary.intersection(lower.buffer(0.05))
        ls = [q for q in getattr(g, "geoms", [g]) if q.geom_type in ("LineString", "MultiLineString")]
        u = unary_union(ls) if ls else LineString()
        m = linemerge(u) if u.geom_type == "MultiLineString" else u
        return max(getattr(m, "geoms", [m]), key=lambda q: q.length) if not m.is_empty else LineString()

    mb = C.MeshBuilder()           # ground, decks, walls
    mp = C.MeshBuilder()           # pools and water
    hard = []

    # ---- the main pool on the second terrace: its infinity edge along the wall over the lagoon -------------
    Lb = shared(bB, bC)
    ring_BC = bB.intersection(bC.buffer(WALL, join_style=2))
    Linf = substring(Lb, 0.22 * Lb.length, 0.78 * Lb.length)
    lobes = unary_union([Point(Linf.interpolate(s)).buffer(6.5 + 6.0 * math.sin(math.pi * s / 21.0 + 0.6) ** 2, 24)
                         for s in np.arange(0.0, Linf.length + 0.01, 1.2)])
    pool = _smooth(lobes.intersection(bB).intersection(ZONE.buffer(-4.0)), 0.8).difference(ring_BC)
    pool = max(L.as_polys(pool), key=lambda q: q.area)
    # the palm island: in the widest lobe
    best, bd = None, 0.0
    sample = [Point(x, y) for x in np.arange(pool.bounds[0], pool.bounds[2], 0.8) for y in np.arange(pool.bounds[1], pool.bounds[3], 0.8)]
    for p in sample:
        if pool.contains(p):
            d = pool.exterior.distance(p)
            if d > bd:
                best, bd = p, d
    island = best.buffer(min(2.6, bd - 2.0), 24) if best is not None and bd > 4.2 else Polygon()
    water = pool.difference(island)
    inf_lip = ring_BC.intersection(pool.buffer(0.6, join_style=2))          # the stretch of wall the water runs over
    shelf = water.difference(water.buffer(-2.6, join_style=2)).difference(ring_BC.buffer(3.2, join_style=2)).difference(island.buffer(1.0))
    shelf = unary_union([q for q in L.as_polys(shelf) if q.area > 4.0])
    L.prism(mp, "pool_tile", water, zB - POOL_D - 0.05, zB - POOL_D, sides=False)
    L.prism(mp, "pool_tile", water.buffer(0.01, join_style=2).difference(water.buffer(-0.01, join_style=2)), zB - POOL_D, zB - 0.06)
    L.prism(mp, "pool_tile", shelf, zB - POOL_D, zB - 0.40)                  # the sun shelf
    L.prism(mp, "pool_water", water.buffer(-0.01, join_style=2), zB - 0.08, zB - 0.06, sides=False)
    L.prism(mp, "pool_water", inf_lip, zB - 0.09, zB - 0.07, sides=False)
    cop = pool.buffer(0.35, join_style=2).difference(pool).difference(ring_BC.buffer(0.02))
    L.prism(mb, "coping", cop, zB - 0.30, zB + 0.03)
    L.prism(mb, "coping", island.difference(island.buffer(-0.30)), zB - POOL_D, zB + 0.30)
    L.prism(mb, "lawn", island.buffer(-0.30), zB - POOL_D, zB + 0.25, sides=False)
    hard += [pool.buffer(0.35, join_style=2)]
    # the waterfall: one sheet down the wall's face into the lagoon
    face = ring_BC.boundary.intersection(bC.buffer(0.02)).intersection(inf_lip.buffer(0.05, join_style=2))
    sheets = [q for q in getattr(face, "geoms", [face]) if q.geom_type == "LineString" and q.length > 0.5]

    # ---- the lagoon at the foot of the wall --------------------------------------------------------------
    lob2 = unary_union([Point(Linf.interpolate(s)).buffer(4.5 + 3.5 * math.sin(math.pi * s / 15.0 + 0.3) ** 2, 24)
                        for s in np.arange(0.0, Linf.length + 0.01, 1.2)])
    lag = _smooth(lob2.intersection(bC).intersection(ZONE.buffer(-4.0)), 0.6)
    lag = max(L.as_polys(lag), key=lambda q: q.area) if not lag.is_empty else Polygon()
    L.prism(mp, "pool_tile", lag, zC - LAG_D - 0.05, zC - LAG_D, sides=False)
    L.prism(mp, "pool_tile", lag.buffer(0.01, join_style=2).difference(lag.buffer(-0.01, join_style=2)), zC - LAG_D, zC - 0.08)
    L.prism(mp, "pool_water", lag.buffer(-0.01, join_style=2), zC - 0.12, zC - 0.10, sides=False)
    L.prism(mb, "coping", lag.buffer(0.35, join_style=2).difference(lag).intersection(bC).difference(bB.buffer(0.02)), zC - 0.30, zC + 0.03)
    hard.append(lag.buffer(0.35, join_style=2))
    for ln in sheets:                                       # the sheet of water, a hand off the wall
        n = max(2, int(ln.length / 0.8))
        pts = [ln.interpolate(k / n, normalized=True) for k in range(n + 1)]
        for p, q in zip(pts, pts[1:]):
            m = Point((p.x + q.x) / 2, (p.y + q.y) / 2)
            d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
            nv = np.array([-d[1], d[0]])
            if bB.contains(Point(m.x + nv[0] * 0.3, m.y + nv[1] * 0.3)):
                nv = -nv
            a = (p.x + nv[0] * 0.04, p.y + nv[1] * 0.04)
            b = (q.x + nv[0] * 0.04, q.y + nv[1] * 0.04)
            for o_ in (0.0, 0.03):
                mp.poly("pool_water", [(a[0] + nv[0] * o_, a[1] + nv[1] * o_, zC - 0.11), (b[0] + nv[0] * o_, b[1] + nv[1] * o_, zC - 0.11),
                                       (b[0] + nv[0] * o_, b[1] + nv[1] * o_, zB - 0.08), (a[0] + nv[0] * o_, a[1] + nv[1] * o_, zB - 0.08)])

    # ---- the lower terrace: jacuzzis, the children's pool, the cabanas -------------------------------------
    Ld = shared(bC, bD)
    Le = shared(bD, slope) if not slope.is_empty else LineString()
    spa_pts = []
    if Ld.length > 20:
        for f in (0.42, 0.56):
            p = Ld.interpolate(f, normalized=True)
            q = Ld.interpolate(min(1.0, f + 0.02), normalized=True)
            d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
            nv = np.array([-d[1], d[0]])
            if not bD.contains(Point(p.x + nv[0] * 5.0, p.y + nv[1] * 5.0)):
                nv = -nv
            spa_pts.append(Point(p.x + nv[0] * 5.0, p.y + nv[1] * 5.0))
    jac = unary_union([c.buffer(1.7, 32) for c in spa_pts if bD.buffer(-2.2).contains(c)])
    for j in L.as_polys(jac):
        L.prism(mb, "coping", j.buffer(0.30).difference(j), zD - 0.30, zD + 0.45)
        L.prism(mp, "tile_jade", j, zD - 0.55, zD - 0.50, sides=False)
        L.prism(mp, "tile_jade", j.difference(j.buffer(-0.02)), zD - 0.50, zD + 0.30)
        L.prism(mp, "pool_water", j.buffer(-0.02), zD + 0.30, zD + 0.32, sides=False)
        hard.append(j.buffer(0.3))
    kid = Polygon()
    if Ld.length > 20:
        p = Ld.interpolate(0.78, normalized=True)
        q = Ld.interpolate(0.80, normalized=True)
        d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
        nv = np.array([-d[1], d[0]])
        if not bD.contains(Point(p.x + nv[0] * 6.0, p.y + nv[1] * 6.0)):
            nv = -nv
        c = np.array([p.x, p.y]) + nv * 6.5
        kid = unary_union([Point(*(c + d * k * 1.6 + nv * math.sin(k) * 0.9)).buffer(2.2 - 0.25 * abs(k), 20) for k in range(-3, 4)])
        kid = kid.intersection(bD.buffer(-2.5))
        if not kid.is_empty:
            kid = max(L.as_polys(kid), key=lambda g: g.area)
            L.prism(mp, "pool_tile", kid, zD - 0.55, zD - 0.50, sides=False)
            L.prism(mp, "pool_tile", kid.buffer(0.01).difference(kid.buffer(-0.01)), zD - 0.50, zD - 0.06)
            L.prism(mp, "pool_water", kid.buffer(-0.01), zD - 0.10, zD - 0.08, sides=False)
            L.prism(mb, "coping", kid.buffer(0.30).difference(kid), zD - 0.30, zD + 0.03)
            hard.append(kid.buffer(0.3))

    def lounger(x, y, ang, z):
        ca, sa = math.cos(ang), math.sin(ang)
        Q = lambda a, b: (x + a * ca - b * sa, y + a * sa + b * ca)
        g = Polygon([Q(-0.35, -0.95), Q(0.35, -0.95), Q(0.35, 0.95), Q(-0.35, 0.95)])
        L.prism(mb, "lounger_white", g, z + 0.06, z + 0.30)
        L.prism(mb, "sofa_cushion", g.buffer(-0.04), z + 0.30, z + 0.36)
        L.prism(mb, "sofa_cushion", Polygon([Q(-0.33, 0.55), Q(0.33, 0.55), Q(0.33, 0.93), Q(-0.33, 0.93)]), z + 0.36, z + 0.66)

    def parasol(x, y, z):
        L.prism(mb, "metal_dark", Point(x, y).buffer(0.035, 6), z, z + 2.55)
        rim = [(x + 1.35 * math.cos(2 * math.pi * k / 8), y + 1.35 * math.sin(2 * math.pi * k / 8), z + 2.30) for k in range(8)]
        for k in range(8):
            mb.poly("canvas", [rim[k], rim[(k + 1) % 8], (x, y, z + 2.80)])
            mb.poly("canvas", [rim[(k + 1) % 8], rim[k], (x, y, z + 2.78)])

    def along(line, step, off, band, avoid):
        """points every step along a line, off into band, clear of avoid; with the line's direction"""
        out = []
        if line.is_empty or line.length < step:
            return out
        for s in np.arange(step / 2, line.length, step):
            p, q = line.interpolate(s), line.interpolate(min(line.length, s + 0.5))
            d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
            nv = np.array([-d[1], d[0]])
            if not band.contains(Point(p.x + nv[0] * off, p.y + nv[1] * off)):
                nv = -nv
            c = Point(p.x + nv[0] * off, p.y + nv[1] * off)
            if band.buffer(-1.0).contains(c) and avoid.distance(c) > 1.2:
                out.append((c, d, nv))
        return out

    # cabanas along the lower edge, facing the sunset
    cabs = []
    for c, d, nv in along(Le if not Le.is_empty else Ld, 9.0, 3.2, bD, unary_union(hard))[:3]:
        a = math.atan2(d[1], d[0])
        g = Polygon([tuple(np.array([c.x, c.y]) + d * u + nv * v) for u, v in ((-1.5, -1.3), (1.5, -1.3), (1.5, 1.3), (-1.5, 1.3))])
        L.prism(mb, "lounger_white", g.buffer(-0.15), zD, zD + 0.40)
        L.prism(mb, "sofa_cushion", g.buffer(-0.25), zD + 0.40, zD + 0.55)
        for u, v in ((-1.5, -1.3), (1.5, -1.3), (1.5, 1.3), (-1.5, 1.3)):
            pc = np.array([c.x, c.y]) + d * u + nv * v
            mb.box("timber", pc[0] - 0.07, pc[0] + 0.07, pc[1] - 0.07, pc[1] + 0.07, zD, zD + 2.60)
        L.prism(mb, "canvas", g.buffer(0.15, join_style=2), zD + 2.60, zD + 2.66)
        L.prism(mb, "timber", g.buffer(0.20, join_style=2).difference(g.buffer(0.05, join_style=2)), zD + 2.55, zD + 2.70)
        cabs.append(g.buffer(0.3))
    hard += cabs

    # ---- the arrival terrace: the pool bar under its pergola -------------------------------------------------
    La = shared(bA, bB)
    bar = Polygon()
    if La.length > 15:
        p = La.interpolate(0.5, normalized=True)
        q = La.interpolate(0.52, normalized=True)
        d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
        nv = np.array([-d[1], d[0]])
        if not bA.contains(Point(p.x + nv[0] * 3.0, p.y + nv[1] * 3.0)):
            nv = -nv
        P = lambda u, v: tuple(np.array([p.x, p.y]) + d * u + nv * v)
        bar = Polygon([P(-4.5, 5.0), P(4.5, 5.0), P(4.5, 10.5), P(-4.5, 10.5)])
        if bA.buffer(-0.5).contains(bar):
            fb = bar.buffer(-0.25, join_style=2)
            open_ = Polygon([P(-3.2, 4.9), P(3.2, 4.9), P(3.2, 5.4), P(-3.2, 5.4)])
            ringb = bar.difference(fb)
            L.prism(mb, "villa", ringb.difference(open_), zA, zA + 3.70)
            L.prism(mb, "villa", ringb.intersection(open_), zA + 2.60, zA + 3.70)
            L.prism(mb, "villa", fb, zA + 3.50, zA + 3.70, bottom=True)
            L.prism(mb, "timber", Polygon([P(-3.1, 5.3), P(3.1, 5.3), P(3.1, 6.0), P(-3.1, 6.0)]), zA, zA + 1.10)
            for z0, z1, pd, mat in ((zA + 3.70, zA + 3.78, 0.10, "ledge"), (zA + 3.78, zA + 3.92, 0.06, "band"), (zA + 3.92, zA + 4.00, 0.14, "ledge")):
                L.prism(mb, mat, bar.buffer(pd, join_style=2).difference(bar), z0, z1, bottom=True)
            L.prism(mb, "villa", bar.difference(bar.buffer(-0.25, join_style=2)), zA + 3.70, zA + 4.40)
            L.prism(mb, "coping", bar.buffer(0.02, join_style=2).difference(bar.buffer(-0.27, join_style=2)), zA + 4.40, zA + 4.46)
            L.prism(mb, "mashrabiya", Polygon([P(-1.0, 10.52), P(1.0, 10.52), P(1.0, 10.56), P(-1.0, 10.56)]), zA + 1.0, zA + 2.8)
            for u in np.arange(-4.4, 4.41, 0.55):                          # the pergola over the bar's terrace
                a_, b_ = P(u, 1.2), P(u, 5.0)
                L.prism(mb, "timber", LineString([a_, b_]).buffer(0.05, cap_style=2), zA + 2.95, zA + 3.10)
            for u in (-4.4, 0.0, 4.4):
                c_ = P(u, 1.3)
                mb.box("timber", c_[0] - 0.09, c_[0] + 0.09, c_[1] - 0.09, c_[1] + 0.09, zA, zA + 2.95)
            L.prism(mb, "timber", LineString([P(-4.5, 1.3), P(4.5, 1.3)]).buffer(0.09, cap_style=2), zA + 2.80, zA + 2.95)
            hard.append(bar.buffer(1.0))
        else:
            bar = Polygon()

    # ---- decks, lawns, loungers, parasols, palms on the terraces --------------------------------------------
    for b_, lev, near in ((bA, zA, La), (bB, zB, Lb), (bC, zC, Lb), (bD, zD, Ld)):
        blocked = unary_union([pool, lag, jac, kid, bar, island])
        deck = b_.intersection(unary_union([near.buffer(5.0)] + [h.buffer(4.0, join_style=1) for h in hard])).difference(blocked)
        lawn = b_.difference(deck).difference(blocked)
        L.prism(mb, "deck_stone", deck, lev - 0.30, lev, sides=False)
        L.prism(mb, "lawn", lawn, lev - 0.30, lev + 0.04, sides=False)
        L.prism(mb, "deck_stone", b_.intersection(blocked).difference(unary_union([pool, lag, jac, kid])).difference(island).difference(bar), lev - 0.30, lev, sides=False)
        for c in [Point(x, y) for x in np.arange(x0, x1, 9.0) for y in np.arange(y0, y1, 9.0)]:
            if lawn.buffer(-2.5).contains(c) and RNG.random() < 0.7:
                put("olive" if RNG.random() < 0.6 else "date", (c.x + RNG.uniform(-2, 2), c.y + RNG.uniform(-2, 2)), lev, RNG.uniform(0.7, 0.9))
    # loungers and parasols along the main pool and the lagoon; palms on the decks and the island
    edge_in = pool.exterior.difference(ring_BC.buffer(0.6))
    for g in getattr(edge_in, "geoms", [edge_in]):
        if g.length < 4:
            continue
        for s in np.arange(2.5, g.length - 1.0, 4.0):
            p, q = g.interpolate(s), g.interpolate(min(g.length, s + 0.5))
            d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
            nv = np.array([-d[1], d[0]])
            if pool.contains(Point(p.x + nv[0] * 0.8, p.y + nv[1] * 0.8)):
                nv = -nv
            c = np.array([p.x, p.y]) + nv * 1.8
            if bB.buffer(-1.0).contains(Point(*c)) and not unary_union([bar, island]).buffer(1.0).contains(Point(*c)):
                k = int(s / 4.0) % 3
                if k == 2:
                    parasol(c[0], c[1], zB)
                else:
                    lounger(c[0], c[1], math.atan2(nv[1], nv[0]) - math.pi / 2, zB)
            if int(s / 4.0) % 4 == 1:
                cp = np.array([p.x, p.y]) + nv * 3.6
                if bB.buffer(-1.0).contains(Point(*cp)):
                    put("wash" if RNG.random() < 0.5 else "date", tuple(cp), zB, RNG.uniform(0.8, 0.95))
    for g in L.as_polys(shelf):                              # loungers in the water, on the sun shelf
        pts = [Point(x, y) for x in np.arange(g.bounds[0], g.bounds[2], 2.5) for y in np.arange(g.bounds[1], g.bounds[3], 2.5)]
        for p in [p for p in pts if g.buffer(-0.9).contains(p)][:4]:
            lounger(p.x, p.y, RNG.uniform(0, 3.14), zB - 0.42)
    if not island.is_empty:
        put("date", tuple(island.centroid.coords[0]), zB + 0.25, 0.9)
        cc = island.centroid
        put("wash", (cc.x + 0.9, cc.y + 0.6), zB + 0.25, 0.75)
    if not lag.is_empty:
        e2 = lag.exterior.difference(bB.buffer(0.5))
        for g in getattr(e2, "geoms", [e2]):
            if g.length < 4:
                continue
            for s in np.arange(2.0, g.length - 1.0, 4.5):
                p, q = g.interpolate(s), g.interpolate(min(g.length, s + 0.5))
                d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
                nv = np.array([-d[1], d[0]])
                if lag.contains(Point(p.x + nv[0] * 0.8, p.y + nv[1] * 0.8)):
                    nv = -nv
                c = np.array([p.x, p.y]) + nv * 1.7
                if bC.buffer(-1.0).contains(Point(*c)):
                    if int(s / 4.5) % 3 == 1:
                        put("date", tuple(np.array([p.x, p.y]) + nv * 3.2), zC, RNG.uniform(0.75, 0.9))
                    else:
                        lounger(c[0], c[1], math.atan2(nv[1], nv[0]) - math.pi / 2, zC)
    if not bar.is_empty:                                     # loungers along the arrival terrace's parapet
        for c, d, nv in along(La, 5.0, 1.6, bA.difference(bar.buffer(1.5)), Polygon()):
            if RNG.random() < 0.8:
                lounger(c.x, c.y, math.atan2(-nv[1], -nv[0]) - math.pi / 2, zA)

    # ---- the walls: between the terraces (stone, parapet over the upper one), round the edge ----------------
    stairs = []
    seq = [(bA, zA), (bB, zB), (bC, zC), (bD, zD)]
    for (bu, zu), (bl, zl_) in zip(seq, seq[1:]):
        ring = bu.intersection(bl.buffer(WALL, join_style=2))
        lip = inf_lip if bu is bB else Polygon()
        # the stair alongside the wall, at its northern end, on the lower terrace
        ln = shared(bu, bl)
        flight = Polygon()
        if ln.length > 14:
            ends = [ln.interpolate(3.0), ln.interpolate(ln.length - 3.0)]
            top = max(ends, key=lambda p: p.y)
            s0 = ln.project(top)
            sgn = -1 if s0 > ln.length / 2 else 1
            n_r = int(math.ceil((zu - zl_) / 0.16))
            run = n_r * 0.30
            for k in range(n_r):
                a_, b_ = s0 + sgn * k * 0.30, s0 + sgn * (k + 1) * 0.30
                seg = substring(ln, min(a_, b_), max(a_, b_))
                if seg.length < 0.05:
                    continue
                side = seg.buffer(2.4, single_sided=True)
                if not bl.buffer(0.5).contains(side.centroid):
                    side = seg.buffer(-2.4, single_sided=True)
                tread = side.difference(ring).intersection(bl.buffer(0.1))
                L.prism(mb, "deck_stone", tread, zl_ - 0.30, zu - k * (zu - zl_) / n_r)
                flight = flight.union(tread)
            stairs.append(flight)
            landing = top.buffer(1.4).intersection(ring)
        else:
            landing = Polygon()
        body = ring.difference(lip)
        L.prism(mb, "stone", body.difference(landing), zl_ - 0.60, zu + PARAPET)
        L.prism(mb, "coping", body.difference(landing).buffer(0.03, join_style=2).intersection(ring.buffer(0.03, join_style=2)), zu + PARAPET, zu + PARAPET + 0.06)
        L.prism(mb, "stone", landing, zl_ - 0.60, zu - 0.02)
        L.prism(mb, "deck_stone", landing, zu - 0.02, zu)
        if not lip.is_empty:                                 # the waterfall's wall in green zellige under the sheet
            L.prism(mb, "tile_jade", lip, zl_ - 0.60, zB - 0.12)
            L.prism(mb, "tile_jade", lip, zB - 0.12, zB - 0.10, sides=False)
        hard.append(ring)
    # between the lower terrace and the slope: its parapet, the wall down to the ground
    if not slope.is_empty:
        ring = bD.intersection(slope.buffer(WALL, join_style=2))
        lowz = min(hz(*p) for p in ring.exterior.coords) if not ring.is_empty else zD - 4
        L.prism(mb, "stone", ring, lowz - 1.0, zD + PARAPET)
        L.prism(mb, "coping", ring.buffer(0.03, join_style=2), zD + PARAPET, zD + PARAPET + 0.06)

    # round the zone's edge: each terrace held up or holding the ground outside, a parapet over it
    allb = unary_union([b_ for b_, _ in seq])
    for b_, lev in seq:
        e = b_.boundary.difference(unary_union([o.buffer(0.05) for o, _ in seq if o is not b_] + [slope.buffer(0.05)]))
        for g in getattr(e, "geoms", [e]):
            if g.geom_type != "LineString" or g.length < 0.3:
                continue
            n = max(1, int(math.ceil(g.length / 0.8)))
            pts = [g.interpolate(k / n, normalized=True) for k in range(n + 1)]
            for p, q in zip(pts, pts[1:]):
                d = np.array([q.x - p.x, q.y - p.y]); dl = np.linalg.norm(d)
                if dl < 1e-6:
                    continue
                d = d / dl
                nv = np.array([-d[1], d[0]])
                m = np.array([(p.x + q.x) / 2, (p.y + q.y) / 2])
                if not b_.contains(Point(*(m + nv * 0.2))):
                    nv = -nv
                out = m - nv * 0.8
                ho = hz(*out)
                top, bot = max(lev + PARAPET, ho + 0.15), min(lev, ho) - 1.0
                A, Bq = np.array([p.x, p.y]), np.array([q.x, q.y])
                Ai, Bi = A + nv * WALL, Bq + nv * WALL
                mb.poly("stone", [(A[0], A[1], bot), (Bq[0], Bq[1], bot), (Bq[0], Bq[1], top), (A[0], A[1], top)])
                mb.poly("stone", [(Bi[0], Bi[1], bot), (Ai[0], Ai[1], bot), (Ai[0], Ai[1], top), (Bi[0], Bi[1], top)])
                mb.poly("coping", [(A[0], A[1], top), (Bq[0], Bq[1], top), (Bi[0], Bi[1], top), (Ai[0], Ai[1], top)])

    # ---- the slope: planted, the stepped path to the belvedere on the tip ------------------------------------
    belv = Polygon()
    if not slope.is_empty:
        tip = min(ZONE.exterior.coords, key=lambda p: p[0])
        cz = np.array(ZONE.centroid.coords[0])
        tv = (np.array(tip) - cz) / np.linalg.norm(np.array(tip) - cz)
        bc = np.array(tip) - tv * 9.0
        belv = Point(*bc).buffer(4.5, 32).intersection(slope.buffer(-1.0))
        zb = hz(*bc) + 0.30
        if not belv.is_empty and belv.area > 20:
            path_from = Le.interpolate(0.5, normalized=True) if not Le.is_empty else Point(*cz)
            path = LineString([(path_from.x, path_from.y), tuple(bc)])
            n = int(path.length / 0.6)
            for k in range(n):
                seg = substring(path, k * 0.6, (k + 1) * 0.6)
                tr = seg.buffer(1.0, cap_style=2).intersection(slope).difference(belv)
                if tr.is_empty:
                    continue
                zt = hz(*seg.interpolate(0.5, normalized=True).coords[0])
                L.prism(mb, "deck_stone", tr, zt - 1.5, zt + 0.12)
            pathp = path.buffer(1.0, cap_style=2)
            L.prism(mb, "stone", belv, zb - 3.0, zb - 0.05)
            L.prism(mb, "deck_stone", belv, zb - 0.05, zb, sides=False)
            par = belv.difference(belv.buffer(-0.35)).difference(pathp)
            L.prism(mb, "stone", par, zb, zb + 0.90)
            L.prism(mb, "coping", par.buffer(0.03), zb + 0.90, zb + 0.96)
            sq = Point(*bc).buffer(2.2, cap_style=3)
            for x_, y_ in list(sq.exterior.coords)[:4]:
                mb.box("timber", x_ - 0.09, x_ + 0.09, y_ - 0.09, y_ + 0.09, zb, zb + 2.70)
            for k in range(8):
                a_, b_ = sq.bounds[1] + 0.2 + k * 0.55, 0
                mb.box("timber", sq.bounds[0] - 0.2, sq.bounds[2] + 0.2, a_ - 0.04, a_ + 0.04, zb + 2.70, zb + 2.84)
            for sg in (-1, 1):
                mb.box("timber", bc[0] - 1.5, bc[0] + 1.5, bc[1] + sg * 1.4 - 0.22, bc[1] + sg * 1.4 + 0.22, zb, zb + 0.45)
            hard += [belv, pathp]
        else:
            belv = Polygon()
        rest = slope.difference(belv).difference(path.buffer(1.0, cap_style=2) if not belv.is_empty else Polygon())
        L.prism(mb, "lawn", rest, -1.0, 0.05, zf=hz)
        for c in [Point(x, y) for x in np.arange(x0, x1, 4.5) for y in np.arange(y0, y1, 4.5)]:
            c2 = Point(c.x + RNG.uniform(-1.5, 1.5), c.y + RNG.uniform(-1.5, 1.5))
            if rest.buffer(-1.0).contains(c2):
                put("shrub" if RNG.random() < 0.8 else "agave", (c2.x, c2.y), hz(c2.x, c2.y), RNG.uniform(0.8, 1.1))

    mb.build("T4_GROUND", cols["T4_01_GROUND"], M)
    mp.build("T4_POOLS", cols["T4_02_POOLS"], M)
    print(f"  T4: pool park: main pool {pool.area:.0f} m2 ({Linf.length:.0f} m of infinity edge), island {island.area:.0f} m2, "
          f"lagoon {lag.area:.0f} m2, jacuzzis {len(L.as_polys(jac))}, cabanas {len(cabs)}, {len(stairs)} stairs, {nveg[0]} plants")
    return cameras(pool, Lb, zB, zC)


def cameras(pool, Lb, zB, zC):
    col = bpy.data.collections["07_CAMERAS"]
    from mathutils import Vector
    c = np.array(pool.centroid.coords[0])
    m = Lb.interpolate(0.5, normalized=True)
    n = np.array([m.x, m.y]) - c
    n = n / max(1e-9, np.linalg.norm(n))                       # from the pool towards the ocean
    t = np.array([-n[1], n[0]])
    mm = np.array([m.x, m.y])
    shots = {                                                  # eye, its height, target, its height, lens
        "T4_CAM_01_POOL_PARK_AERIAL": (c - n * 50 + t * 35, zB + 40.0, c + n * 12, zC, 24),
        "T4_CAM_02_INFINITY_POOL": (c - n * 9, zB + 1.7, c + n * 40, zB - 3.0, 20),
        "T4_CAM_03_CASCADE": (mm + n * 16 + t * 8, zC + 1.7, mm - t * 3, zC + 3.5, 20),
    }
    cams = {}
    for name, (e, eh, tg, th, lens) in shots.items():
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        col.objects.link(cam)
        E = Vector((float(e[0]), float(e[1]), eh))
        T = Vector((float(tg[0]), float(tg[1]), th))
        cam.location = E
        cam.rotation_euler = (T - E).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        cam.data.clip_end = 40000
        cams[name] = cam
    return cams
