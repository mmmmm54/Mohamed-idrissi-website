"""
20_pool_park — the last part of the site, west of Tranche 3 on the cliff over the Atlantic (client 26-10: "zid had
partie lakhriya w pscine dira f chi chkel machi nfs chi likayn f plan because this pscine is the important things
bghiaha dkun naaadya"; then "look at the planning ... 3awjtiha bzzaf ... ghsha dkun mostawa wa7ed ... machi
tab9at": laid out as the plan de masse lays it out, on one level; then "just fix this little thing": Tranche 3's
passage between the villas type A carried on to the pool, the children's pool removed).

A DESIGN PROPOSAL on the plan de masse's layout: the plan's drawing of the zone (the pool area between the
round kiosk and the villas type A, the street along the boundary, the rows of palms) is placed on the site
by its boundary marks B6, B7 and B8 (PLAN, plan pixels -> model, residues under 0.2 m). The whole zone is one
level (LEVEL, between the villas type A's pads; 05 grades the ground there flat so its surroundings meet it):
  the street along the northern boundary as the plan draws it (the Voie Publique on to the cliff), its paved
    edge and the pedestrian crossing, rising at its eastern end to meet Tranche 3's street;
  the pool, the important thing, in the plan's pool area but not in its shape: one sinuous lagoon pool along
    the plan's axis (lobes 9 to 14 m from its spine), a palm island in its widest lobe, a timber bridge over its
    waist, a sun shelf with loungers in the water along its eastern edge, travertine decks, loungers and
    parasols; a jacuzzi by its southern end;
  the passage between the villas type A (Tranche 3) carried on to the pool: its middle paving, as wide, across
    the lawn to the pool's deck, steps up from the passage (lower than the level) between low stone walls;
  the round kiosk where the plan draws it: a round timber pergola (16 m across) on its posts, its radial
    beams as the plan's drawing, the round stone bar in its middle, on the plaza the plan hatches;
  the rows of palms, the big trees and the lawn as the plan places them; a stone parapet along the cliff and
    the southern boundary.
"""
import json
import math
import os
import random

import bpy
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = json.load(open(os.path.join(ROOT, "data", "site.json")))
T2 = json.load(open(os.path.join(ROOT, "data", "t2_site.json")))
T3 = json.load(open(os.path.join(ROOT, "data", "t3_site.json")))
RNG = random.Random(20261026)

LEVEL = -4.0                    # the zone's one level (the villas type A's pads -2.3 to -6.1)
PARAPET = 0.95
POOL_D = 1.40

# the plan de masse's drawing of the zone (its pixels, y down) -> model: by the boundary marks B8, B7, B6
_P = np.array([(282.0, -46.7), (280.0, -133.3), (128.7, -380.0)])
_Q = np.array([(-395.62, 336.99), (-406.01, 322.12), (-459.63, 296.96)])
_A = np.vstack([_P[:, 0] + 1j * _P[:, 1], np.ones(3)]).T
(_Z, _T), *_ = np.linalg.lstsq(_A, _Q[:, 0] + 1j * _Q[:, 1], rcond=None)


def PLAN(x, y):
    w = _Z * (x - 1j * y) + _T
    return (float(w.real), float(w.imag))


def _zone():
    site = Polygon(SITE["boundary"]).buffer(0)
    built = unary_union([Polygon(r["ext"]).buffer(0) for r in SITE["t1_region"]]
                        + [Polygon(T2["env"]["ext"]).buffer(0), Polygon(T3["env"]["ext"]).buffer(0)])
    return max(L.as_polys(site.difference(built)), key=lambda g: g.area).buffer(0)


ZONE = _zone()
T3ENV = Polygon(T3["env"]["ext"]).buffer(0)
NORTH = LineString([(-395.62, 336.99), (-363.49, 309.81), (-316.37, 273.82)])     # the boundary along the street


def envelope():
    """The pool park's ground: the site's empty land is cut away there (05 build_terrain)."""
    return ZONE


def flat_area():
    """Where 05's ground is the one level LEVEL: the zone and its boundary, not Tranche 3."""
    return ZONE.buffer(0.3, join_style=2).difference(T3ENV)


def _passage():
    """Tranche 3's passage between the villas type A, its middle paving: its end on the zone, its direction into the
    zone, its width"""
    r = np.array(Polygon(T3["passage_path"][0]["ext"]).buffer(0).minimum_rotated_rectangle.exterior.coords[:4])
    i = int(np.argmax([np.linalg.norm(r[(k + 1) % 4] - r[k]) for k in range(4)]))
    a, b = sorted([(r[i] + r[(i + 3) % 4]) / 2, (r[(i + 1) % 4] + r[(i + 2) % 4]) / 2], key=lambda p: ZONE.distance(Point(*p)))
    return a, (a - b) / np.linalg.norm(a - b), float(np.linalg.norm(r[(i + 2) % 4] - r[(i + 1) % 4]))


def _ppoly(pts):
    return Polygon([PLAN(*p) for p in pts]).buffer(0)


def _strip_wall(mb, line, z_top, z_bot, side_poly, mat="stone", t=0.35):
    """a wall along a line, t thick on the side away from side_poly, its top z_top(x, y), with its coping"""
    n = max(1, int(math.ceil(line.length / 0.8)))
    pts = [line.interpolate(k / n, normalized=True) for k in range(n + 1)]
    for p, q in zip(pts, pts[1:]):
        d = np.array([q.x - p.x, q.y - p.y]); dl = np.linalg.norm(d)
        if dl < 1e-6:
            continue
        d = d / dl
        nv = np.array([-d[1], d[0]])
        mid = np.array([(p.x + q.x) / 2, (p.y + q.y) / 2])
        if not side_poly.contains(Point(*(mid + nv * 0.2))):
            nv = -nv
        ta, tb = z_top(p.x, p.y), z_top(q.x, q.y)
        if ta is None or tb is None:
            continue
        A, Bq = np.array([p.x, p.y]), np.array([q.x, q.y])
        Ai, Bi = A + nv * t, Bq + nv * t
        mb.poly(mat, [(A[0], A[1], z_bot), (Bq[0], Bq[1], z_bot), (Bq[0], Bq[1], tb), (A[0], A[1], ta)])
        mb.poly(mat, [(Bi[0], Bi[1], z_bot), (Ai[0], Ai[1], z_bot), (Ai[0], Ai[1], ta), (Bi[0], Bi[1], tb)])
        mb.poly("coping", [(A[0], A[1], ta), (Bq[0], Bq[1], tb), (Bi[0], Bi[1], tb), (Ai[0], Ai[1], ta)])


def build(M, B, srcv, H):
    """B: the 05_build_scene module, srcv: its plant sources, H: its terrain height function. Returns the T4
    cameras."""
    cols = {k: C.collection(k) for k in ("T4_01_GROUND", "T4_02_POOLS", "T4_03_LANDSCAPE", "T4_04_TREES_PALMS")}
    nveg = [0]
    z0 = LEVEL

    def put(key, xy, z, s=1.0):
        if key == "shrub" and RNG.random() < 0.3:
            key = "shrub_pink"
        ob = bpy.data.objects.new(f"T4_VEG_{key.upper()}_{nveg[0]:03d}", srcv[key].data)
        ob.location = (float(xy[0]), float(xy[1]), z)
        ob.rotation_euler = (0, 0, RNG.uniform(0, 6.283))
        ob.scale = (s, s, s)
        (cols["T4_03_LANDSCAPE"] if key.startswith(("shrub", "agave", "grass")) else cols["T4_04_TREES_PALMS"]).objects.link(ob)
        nveg[0] += 1

    mb = C.MeshBuilder()           # ground, walls, furniture
    mp = C.MeshBuilder()           # pools and water

    # ---- the street along the northern boundary, as the plan draws it -------------------------------------
    south = Polygon([PLAN(-600, 120), PLAN(1600, 120), PLAN(1600, -800), PLAN(-600, -800)])
    road_all = ZONE.intersection(south)
    edge = road_all.intersection(NORTH.buffer(1.2, cap_style=2))
    road = road_all.difference(edge)
    hplane = B.hz

    def zroad(x, y):
        w = max(0.0, 1.0 - Point(x, y).distance(T3ENV) / 18.0)
        return z0 * (1 - w) + hplane(x, y) * w

    L.prism(mb, "t2_road", road, -1.0, 0.0, zf=zroad)
    L.prism(mb, "t2_pave", edge, -1.0, 0.15, zf=zroad)
    for k in range(7):                                         # the pedestrian crossing (the plan's hatching)
        xk = 506 + k * 4.2
        st_ = _ppoly([(xk, 80), (xk + 2.1, 80), (xk + 2.1, 120), (xk, 120)]).intersection(road)
        L.prism(mb, "paint", st_, 0.004, 0.006, zf=zroad, sides=False)
    # its southern side where it rises over the level at its eastern end: a stone wall with its parapet
    rs = road_all.boundary.intersection(ZONE.buffer(-0.05)).difference(NORTH.buffer(0.3))
    for g in getattr(rs, "geoms", [rs]):
        if g.geom_type == "LineString":
            _strip_wall(mb, g, lambda x, y: (zroad(x, y) + PARAPET) if zroad(x, y) > z0 + 0.25 else None, z0 - 0.3,
                        ZONE.difference(road_all))

    # ---- the pool: one sinuous lagoon along the plan's pool area ----------------------------------------------
    spine = LineString([PLAN(*p) for p in ((598, 196), (640, 255), (652, 322), (628, 395), (612, 455), (630, 520))])
    lobes = unary_union([Point(spine.interpolate(s)).buffer(9.0 + 5.0 * math.sin(math.pi * s / 26.0 + 0.4) ** 2, 32)
                         for s in np.arange(0.0, spine.length + 0.01, 1.0)])
    area = _ppoly([(512, 175), (735, 175), (735, 545), (512, 545)])
    pool = lobes.intersection(area).intersection(ZONE.buffer(-5.0)).difference(road_all.buffer(4.0))
    pool = pool.buffer(1.5, join_style=1).buffer(-1.5, join_style=1)
    pool = max(L.as_polys(pool), key=lambda g: g.area)
    best, bd = None, 0.0
    for x in np.arange(pool.bounds[0], pool.bounds[2], 0.8):
        for y in np.arange(pool.bounds[1], pool.bounds[3], 0.8):
            p = Point(x, y)
            if pool.contains(p) and pool.exterior.distance(p) > bd:
                best, bd = p, pool.exterior.distance(p)
    island = best.buffer(min(4.0, bd - 3.0), 32) if best is not None and bd > 6.0 else Polygon()
    # the bridge across the narrowest waist away from the island
    waist, wbest = None, 1e9
    for s in np.arange(0.25 * spine.length, 0.75 * spine.length, 1.0):
        p = spine.interpolate(s)
        if island.buffer(6.0).contains(p):
            continue
        q = spine.interpolate(min(spine.length, s + 0.5))
        d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
        nv = np.array([-d[1], d[0]])
        cut = LineString([(p.x - nv[0] * 30, p.y - nv[1] * 30), (p.x + nv[0] * 30, p.y + nv[1] * 30)]).intersection(pool)
        if cut.geom_type == "LineString" and 0 < cut.length < wbest:
            waist, wbest = (p, d, nv), cut.length
    bridge = Polygon()
    if waist is not None:
        p, d, nv = waist
        c = np.array([p.x, p.y])
        bridge = Polygon([tuple(c + nv * u + d * v) for u, v in ((-wbest / 2 - 2.0, -1.5), (wbest / 2 + 2.0, -1.5),
                                                                  (wbest / 2 + 2.0, 1.5), (-wbest / 2 - 2.0, 1.5))])
    water = pool.difference(island)
    shelf_side = _ppoly([(640, 150), (900, 150), (900, 600), (640, 600)])
    shelf = water.difference(water.buffer(-2.8, join_style=2)).intersection(shelf_side).difference(bridge.buffer(1.0)).difference(island.buffer(1.5))
    shelf = unary_union([q for q in L.as_polys(shelf) if q.area > 4.0])
    L.prism(mp, "pool_tile", water, z0 - POOL_D - 0.05, z0 - POOL_D, sides=False)
    L.prism(mp, "pool_tile", water.buffer(0.01, join_style=2).difference(water.buffer(-0.01, join_style=2)), z0 - POOL_D, z0 - 0.06)
    L.prism(mp, "pool_tile", shelf, z0 - POOL_D, z0 - 0.40)                  # the sun shelf
    L.prism(mp, "pool_water", water.buffer(-0.01, join_style=2), z0 - 0.08, z0 - 0.06, sides=False)
    L.prism(mb, "coping", pool.buffer(0.40, join_style=1).difference(pool), z0 - 0.30, z0 + 0.03)
    if not island.is_empty:
        L.prism(mb, "coping", island.difference(island.buffer(-0.35)), z0 - POOL_D, z0 + 0.30)
        L.prism(mb, "lawn", island.buffer(-0.35), z0 - POOL_D, z0 + 0.25, sides=False)
    if not bridge.is_empty:                                     # the timber bridge, its railings and piers
        p, d, nv = waist
        L.prism(mb, "planks", bridge, z0 + 0.25, z0 + 0.40)
        for sg in (-1, 1):
            rail = LineString([tuple(np.array([p.x, p.y]) + nv * u + d * sg * 1.40) for u in (-wbest / 2 - 1.8, wbest / 2 + 1.8)])
            L.prism(mb, "timber", rail.buffer(0.04, cap_style=2), z0 + 1.30, z0 + 1.38)
            for t in np.linspace(0, 1, int(rail.length / 1.2) + 1):
                q = rail.interpolate(t, normalized=True)
                L.prism(mb, "timber", Point(q.x, q.y).buffer(0.05, 4), z0 + 0.40, z0 + 1.30)
        span = LineString([tuple(np.array([p.x, p.y]) + nv * u) for u in (-wbest / 2, wbest / 2)])
        for t in np.linspace(0.3, 0.7, 3):
            q = span.interpolate(t, normalized=True)
            for sg in (-1, 1):
                L.prism(mb, "stone", Point(q.x + d[0] * sg * 1.2, q.y + d[1] * sg * 1.2).buffer(0.25, 8), z0 - POOL_D, z0 + 0.25)

    # the jacuzzi by the southern end (client 26-10: the children's pool, cut by the boundary, removed)
    jac = Point(*PLAN(560, 498)).buffer(1.8, 32)
    if not (ZONE.buffer(-3).contains(jac) and not jac.intersects(pool.buffer(2.0))):
        jac = Polygon()
    if not jac.is_empty:
        L.prism(mb, "coping", jac.buffer(0.30).difference(jac), z0 - 0.30, z0 + 0.45)
        L.prism(mp, "tile_jade", jac, z0 - 0.55, z0 - 0.50, sides=False)
        L.prism(mp, "tile_jade", jac.difference(jac.buffer(-0.02)), z0 - 0.50, z0 + 0.30)
        L.prism(mp, "pool_water", jac.buffer(-0.02), z0 + 0.30, z0 + 0.32, sides=False)

    # ---- the round kiosk where the plan draws it, on the plaza it hatches -------------------------------------
    kc = np.array(PLAN(530, 380))
    R = 8.0
    plaza = unary_union([_ppoly([(474, 252), (512, 238), (548, 262), (566, 318), (596, 396), (594, 442), (562, 470),
                                 (520, 452), (488, 410), (472, 330)]), Point(*kc).buffer(R + 2.0, 48)])
    for k in range(16):                                         # its posts on the ring
        a = 2 * math.pi * k / 16
        pc = kc + R * np.array([math.cos(a), math.sin(a)])
        L.prism(mb, "timber", Point(*pc).buffer(0.12, 8), z0, z0 + 3.05)
    L.prism(mb, "timber", Point(*kc).buffer(R + 0.15, 64).difference(Point(*kc).buffer(R - 0.15, 64)), z0 + 3.05, z0 + 3.30)
    for k in range(32):                                         # the radial beams of the plan's drawing
        a = 2 * math.pi * (k + 0.5) / 32
        ln = LineString([tuple(kc + 0.6 * np.array([math.cos(a), math.sin(a)])), tuple(kc + (R + 0.6) * np.array([math.cos(a), math.sin(a)]))])
        L.prism(mb, "timber", ln.buffer(0.05, cap_style=2), z0 + 3.30, z0 + 3.48)
    L.prism(mb, "stone", Point(*kc).buffer(2.6, 48).difference(Point(*kc).buffer(1.9, 48)), z0, z0 + 1.05)   # the round bar
    L.prism(mb, "timber", Point(*kc).buffer(2.85, 48).difference(Point(*kc).buffer(1.8, 48)), z0 + 1.05, z0 + 1.12)
    L.prism(mb, "stone", Point(*kc).buffer(0.35, 16), z0, z0 + 3.48)
    for k in range(12):                                         # stools round the bar
        a = 2 * math.pi * k / 12
        pc = kc + 3.4 * np.array([math.cos(a), math.sin(a)])
        L.prism(mb, "metal_dark", Point(*pc).buffer(0.04, 6), z0, z0 + 0.72)
        L.prism(mb, "planks", Point(*pc).buffer(0.20, 12), z0 + 0.72, z0 + 0.78)

    # ---- the ground: decks round the pools and on the plaza, the path from the crossing, lawn ------------------
    blocked = unary_union([pool, jac, island])
    path = LineString([PLAN(520, 118), PLAN(518, 248)]).buffer(1.3, cap_style=2)
    core = pool.buffer(4.0, join_style=1)
    deck = unary_union([core, jac.buffer(2.0) if not jac.is_empty else Polygon(), plaza, path])
    deck = deck.intersection(ZONE).difference(road_all).difference(blocked)

    # Tranche 3's passage carried on to the pool (client 26-10, the red lines): its middle paving as wide, from the
    # boundary to the deck, the steps up from the passage at its start between low stone walls
    pa, pd, pw = _passage()
    pn = np.array([-pd[1], pd[0]])
    band = lambda s0, s1, h=pw / 2: Polygon([tuple(pa + pd * s0 - pn * h), tuple(pa + pd * s1 - pn * h),
                                             tuple(pa + pd * s1 + pn * h), tuple(pa + pd * s0 + pn * h)])
    cross = lambda s: LineString([tuple(pa + pd * s - pn * pw / 2), tuple(pa + pd * s + pn * pw / 2)])
    s_end = next((s for s in np.arange(0.0, 80.0, 0.25) if core.contains(cross(s))), 80.0)
    alley = band(-0.05, s_end).difference(core).intersection(ZONE.buffer(0.3)).difference(blocked)
    zb = float(B.hz(*pa)) + 0.15                                # the passage's paving at its end (Tranche 3)
    nst = max(0, int(round((z0 - zb) / 0.16)))
    s_st = 0.40 * max(0, nst - 1)                               # treads 0.40, the last riser up to the level
    if nst:
        for k in range(nst - 1):
            L.prism(mb, "t2_path", band(0.40 * k - 0.05 * (k == 0), 0.40 * (k + 1)), zb - 0.60, zb + (k + 1) * (z0 - zb) / nst)
        for sg in (-1, 1):                                      # the low walls along the steps
            ln = LineString([tuple(pa + pn * sg * pw / 2 - pd * 0.05), tuple(pa + pn * sg * pw / 2 + pd * (s_st + 0.35))])
            _strip_wall(mb, ln, lambda x, y: z0 + 0.45, zb - 0.60, ZONE.buffer(1.0).difference(band(-1.0, s_end)))
    L.prism(mb, "t2_path", alley.difference(band(-1.0, s_st)), z0 - 0.40, z0 + 0.02, sides=False)
    deck = deck.difference(alley)
    lawn = ZONE.difference(road_all).difference(deck).difference(blocked).difference(alley).difference(band(-1.0, s_st + 0.35, pw / 2 + 0.35))
    lawn = unary_union([q for q in L.as_polys(lawn) if q.area > 0.5])
    L.prism(mb, "deck_stone", deck, z0 - 0.40, z0, sides=False)
    L.prism(mb, "lawn", lawn, z0 - 0.40, z0 + 0.04, sides=False)

    # ---- the parapet along the cliff and the southern boundary; the step against Tranche 3 --------------------
    inner = ZONE.difference(road_all)
    e = ZONE.boundary.difference(NORTH.buffer(0.4)).difference(road_all.buffer(0.2)).difference(band(-1.0, 1.0) if nst else Polygon())
    for g in getattr(e, "geoms", [e]):
        if g.geom_type != "LineString" or g.length < 0.3:
            continue
        c_ = g.interpolate(0.5, normalized=True)
        if T3ENV.buffer(0.5).contains(c_):                     # meeting Tranche 3's ground: close the step only
            _strip_wall(mb, g, lambda x, y: max(z0, hplane(x, y)) + 0.05, min(z0, -9.0) - 1.0, inner)
        else:
            _strip_wall(mb, g, lambda x, y: z0 + PARAPET, z0 - 1.2, inner)

    # ---- loungers and parasols round the pool, in the water on the shelf ----------------------------------------
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

    free = deck.buffer(-0.9)
    nogo = unary_union([plaza.buffer(0.5), bridge.buffer(1.5), path.buffer(0.5), alley.buffer(0.8)])
    ring = pool.exterior
    for k, s in enumerate(np.arange(1.5, ring.length, 3.4)):
        p, q = ring.interpolate(s), ring.interpolate(min(ring.length, s + 0.5))
        d = np.array([q.x - p.x, q.y - p.y]); d = d / max(1e-9, np.linalg.norm(d))
        nv = np.array([-d[1], d[0]])
        if pool.contains(Point(p.x + nv[0] * 0.8, p.y + nv[1] * 0.8)):
            nv = -nv
        c = np.array([p.x, p.y]) + nv * 1.9
        if not free.contains(Point(*c)) or nogo.contains(Point(*c)):
            continue
        if k % 3 == 2:
            parasol(c[0], c[1], z0)
        else:
            lounger(c[0], c[1], math.atan2(nv[1], nv[0]) - math.pi / 2, z0)
    for g in L.as_polys(shelf):
        pts = [Point(x, y) for x in np.arange(g.bounds[0], g.bounds[2], 2.6) for y in np.arange(g.bounds[1], g.bounds[3], 2.6)]
        for p in [p for p in pts if g.buffer(-0.9).contains(p)][:5]:
            lounger(p.x, p.y, RNG.uniform(0, 3.14), z0 - 0.42)

    # ---- palms in the plan's rows, its big trees, shrubs ------------------------------------------------------
    rows = [(x, y) for x in (712.0, 742.0) for y in np.arange(185, 600, 24)]
    rows += [(x, y) for x in np.arange(392, 462, 23) for y in np.arange(318, 500, 24)]
    rows += [(x, y) for x in np.arange(630, 728, 24) for y in np.arange(538, 610, 24)]
    keep_off = unary_union([pool.buffer(2.5), road_all.buffer(2.0), Point(*kc).buffer(R + 1.0), jac.buffer(2.0),
                            bridge.buffer(2.0), path, alley.buffer(1.2), band(-1.0, s_st + 1.0, pw / 2 + 1.2)])
    for x, y in rows:
        p = Point(*PLAN(x, y))
        if ZONE.buffer(-1.5).contains(p) and not keep_off.contains(p):
            put("date" if RNG.random() < 0.6 else "wash", (p.x, p.y), z0, RNG.uniform(0.8, 0.95))
    for x, y in ((513, 167), (481, 240), (757, 219), (753, 443), (753, 577)):
        p = Point(*PLAN(x, y))
        if ZONE.buffer(-2.0).contains(p) and not keep_off.contains(p):
            put("olive", (p.x, p.y), z0, 1.0)
    if not island.is_empty:
        cc = island.centroid
        put("date", (cc.x, cc.y), z0 + 0.25, 0.95)
        put("wash", (cc.x + 1.2, cc.y + 0.8), z0 + 0.25, 0.8)
        put("date", (cc.x - 1.0, cc.y - 1.1), z0 + 0.25, 0.75)
    for x, y in ((540, 222), (585, 213), (620, 205), (640, 640), (500, 520)):
        p = Point(*PLAN(x, y))
        if lawn.buffer(-1.0).contains(p):
            put("shrub", (p.x, p.y), z0, 1.0)

    mb.build("T4_GROUND", cols["T4_01_GROUND"], M)
    mp.build("T4_POOLS", cols["T4_02_POOLS"], M)
    print(f"  T4: pool park at {z0:.1f}: pool {pool.area:.0f} m2, island {island.area:.0f} m2, bridge {bridge.area:.0f} m2, "
          f"street {road_all.area:.0f} m2, passage {alley.area:.0f} m2 with {max(0, nst - 1)} steps up {z0 - zb:.2f} m, {nveg[0]} plants")
    return cameras(pool, kc, z0)


def cameras(pool, kc, z0):
    col = bpy.data.collections["07_CAMERAS"]
    from mathutils import Vector
    c = np.array(pool.centroid.coords[0])
    ocean = np.array(PLAN(150, 380)) - c
    ocean = ocean / np.linalg.norm(ocean)
    side = np.array([-ocean[1], ocean[0]])
    east = np.array(PLAN(700, 380))
    shots = {                                                  # eye, its height, target, its height, lens
        "T4_CAM_01_POOL_PARK_AERIAL": (c - ocean * 75 + side * 25, z0 + 48.0, c + ocean * 8, z0, 24),
        "T4_CAM_02_POOL_TO_OCEAN": (east, z0 + 1.7, east + ocean * 60, z0 - 1.0, 20),
        "T4_CAM_03_KIOSK": (kc + ocean * 18 + side * 10, z0 + 2.0, kc - ocean * 4, z0 + 2.0, 22),
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
