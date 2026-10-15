"""
04_pool — the pool court of the 1er TRANCHE (block 'PISCINE' of the plan de masse 12-10).

Pool-local frame: origin at the centre of the basin (DWG 251999.57, 119407.49), axes turned by
-24.02 deg (u across the pool towards the gradins, v along it to the north-north-east), z = 0 at
the deck ('PLAGE PISCINE').

Read from the plan:
  CUVE            21.71 x 7.50 m basin, Roman steps (four arcs) in two opposite corners
  PISCINE ENFANT  9.6 x 3.8 m shallow pool at the south end
  TRANSATS        31 lounger drawings (one of them a pair) on the west and east decks
  GRADINS         three strips (0.7 m) between the deck and the upper level, flanked by the two
                  'ESCALIERS PISCINE' of ten steps (numbered 1-10, rising to the east)
  LES BACS A FLEURS  four 1.45 m planters with the four palms ('palmier')
  RAMPE           1.4 m ramp along the south side, walls on both sides
  JARDIN          planted bed along the north side; 'COUVERTURE PISCINE AMOVIBLE' (cover reel)
  colonnes de douche  two shower columns at the north-east corner, two by the local technique
Levels: the court is sunk so that the gradins (four risers of 0.425 m) and the stairs (ten of
0.17 m) climb 1.70 m to the upper level on the east; the deck is therefore 1.70 m below the
ground at the top of the gradins. The other sides are retaining walls with a 1.00 m guard.
"""
import math

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C

RISE = 1.70
COURT = unary_union([box(-12.40, -17.10, 8.70, 20.20), box(-12.60, -19.20, -7.00, -17.10)])
GRADINS_U = [9.10, 9.85, 10.60, 11.35, 11.85]           # step fronts (last = into the upper ground)
GRADINS_V = (-14.20, 14.80)
STAIRS = [box(8.70, 15.00, 11.60, 17.40), box(8.70, -17.00, 11.60, -14.30)]
BACS = [(7.60, 9.05, v - 0.725, v + 0.725) for v in (13.90, 5.60, -5.20, -13.10)]
RAMP = (-7.00, 11.90, -18.60, -17.25)                   # u0, u1 (upper end), v0, v1
BED_N = box(-12.30, 17.55, 4.30, 20.20)
REEL = (-6.50, 3.80, 18.10)
SHOWERS = [(5.70, 18.90), (7.10, 18.90), (-11.70, -9.40), (-11.70, -10.80)]
CUVE_CORNERS = [((-3.75, 10.85), (1, -1)), ((3.75, -10.85), (-1, 1))]


def upper_pad():
    """Strip behind the gradins, levelled at their top (deck + 1.70); the scene blends it into the slope."""
    return box(GRADINS_U[3], -19.50, 16.00, 21.00)


def footprint():
    """Area cut out of the generic ground (court, gradins, stairs, ramp)."""
    g = [COURT, box(GRADINS_U[0], GRADINS_V[0], GRADINS_U[-1], GRADINS_V[1])] + STAIRS + [box(RAMP[0], RAMP[2] - 0.25, RAMP[1], RAMP[3])]
    return unary_union(g).buffer(0.30, join_style=2)


def wall_strip(mb, mat, a, b, t, z0, ztop, side=1.0, seg=1.5):
    """Wall of thickness t on one side of the line a->b; bottom z0, top ztop(x, y) sampled every seg."""
    a, b = (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))
    Lg = math.dist(a, b)
    if Lg < 0.02:
        return
    ux, uy = (b[0] - a[0]) / Lg, (b[1] - a[1]) / Lg
    nx, ny = -uy * side, ux * side
    n = max(1, int(Lg / seg))
    for i in range(n):
        p = (a[0] + ux * Lg * i / n, a[1] + uy * Lg * i / n)
        q = (a[0] + ux * Lg * (i + 1) / n, a[1] + uy * Lg * (i + 1) / n)
        zt = ztop((p[0] + q[0]) / 2 + nx * t / 2, (p[1] + q[1]) / 2 + ny * t / 2)
        pg = Polygon([p, q, (q[0] + nx * t, q[1] + ny * t), (p[0] + nx * t, p[1] + ny * t)])
        L.prism(mb, mat, pg, z0, zt)
        L.prism(mb, "trim", pg.buffer(0.03, join_style=2), zt, zt + 0.05)


def build(M, col, ground, water_polys, name="POOL_COURT", north_top=None, north_gap=None):
    """ground(u, v): height of the natural (graded) ground above the deck at a pool-local point.
    water_polys: {'pool': Polygon, 'kids_pool': Polygon} in pool-local coordinates.
    north_top(u): top of the north wall above the deck, when the long north stair runs along it (the
    wall is then its 1 m guard over the court); north_gap (u0, u1): opening where that stair lands."""
    mb = C.MeshBuilder()
    pool = water_polys["pool"]
    kids = water_polys["kids_pool"]
    # ---- deck ----------------------------------------------------------------------------------
    deck = COURT.difference(pool.buffer(0.30, join_style=2)).difference(kids.buffer(0.30, join_style=2)).difference(BED_N)
    L.prism(mb, "deck_stone", deck, -0.60, 0.0)
    # ---- basins: tiled walls, coping, water -------------------------------------------------------
    for w, depth in ((pool, 1.40), (kids, 0.45)):
        L.prism(mb, "pool_tile", w, -depth - 0.05, -depth, sides=False)
        L.prism(mb, "pool_tile", w.buffer(0.01, join_style=2).difference(w.buffer(-0.01, join_style=2)), -depth, 0.0)
        L.prism(mb, "coping", w.buffer(0.30, join_style=2).difference(w), -0.30, 0.03)
        L.prism(mb, "pool_water", w.buffer(-0.01, join_style=2), -0.14, -0.12, sides=False)
    # Roman steps: quarter discs in two corners of the basin
    for (cx, cy), (su, sv) in CUVE_CORNERS:
        for r, z in ((1.75, -1.05), (1.30, -0.70), (0.85, -0.35)):
            q = Point(cx, cy).buffer(r, 32).intersection(box(min(cx, cx + su * 3), min(cy, cy + sv * 3), max(cx, cx + su * 3), max(cy, cy + sv * 3)))
            L.prism(mb, "pool_tile", q.intersection(pool), -1.40, z)
    # ---- gradins (four risers of 0.425) ----------------------------------------------------------
    v0, v1 = GRADINS_V
    for k in range(4):
        L.prism(mb, "terrace", box(GRADINS_U[k], v0, GRADINS_U[k + 1] + (0.0 if k < 3 else 0.40), v1), -0.30, RISE * (k + 1) / 4)
        mb.box("trim", GRADINS_U[k] - 0.03, GRADINS_U[k] + 0.06, v0, v1, RISE * (k + 1) / 4 - 0.06, RISE * (k + 1) / 4 + 0.01)
    # ---- 'ESCALIERS PISCINE': ten risers rising to the east, cheek walls -------------------------
    for s in STAIRS:
        x0, y0, x1, y1 = s.bounds
        for k in range(10):
            L.prism(mb, "terrace", box(x0 + (x1 - x0) * k / 10, y0, x1 + 0.40, y1), -0.30, 0.17 * (k + 1))
    # ---- planters with the palms ('les bacs à fleurs') -------------------------------------------
    for u0, u1, va, vb in BACS:
        bx = box(u0, va, u1, vb)
        L.prism(mb, "render", L.ring_poly(bx, 0.15), -0.10, 0.55)
        L.prism(mb, "trim", L.ring_poly(bx.buffer(0.03, join_style=2), 0.21), 0.55, 0.60)
        L.prism(mb, "soil", bx.buffer(-0.15, join_style=2), 0.0, 0.45, sides=False)
    # ---- planted bed along the north side ----------------------------------------------------------
    L.prism(mb, "render", L.ring_poly(BED_N, 0.15), -0.10, 0.45)
    L.prism(mb, "lawn", BED_N.buffer(-0.15, join_style=2), 0.0, 0.40, sides=False)
    # ---- ramp along the south side: from the upper level (east) down to the deck (west) ----------
    u0, u1, ra, rb = RAMP
    n = 24
    for i in range(n):
        ua, ub = u0 + (u1 - u0) * i / n, u0 + (u1 - u0) * (i + 1) / n
        za, zb = RISE * i / n, RISE * (i + 1) / n
        mb.poly("concrete", [(ua, ra, za), (ub, ra, zb), (ub, rb, zb), (ua, rb, za)], [(ua, ra), (ub, ra), (ub, rb), (ua, rb)])
        mb.poly("render", [(ua, ra, -0.40), (ub, ra, -0.40), (ub, ra, zb), (ua, ra, za)])
        mb.poly("render", [(ub, rb, -0.40), (ua, rb, -0.40), (ua, rb, za), (ub, rb, zb)])
    mb.poly("render", [(u1, ra, -0.40), (u1, rb, -0.40), (u1, rb, RISE), (u1, ra, RISE)])
    zr = lambda x, y: RISE * min(1.0, max(0.0, (x - u0) / (u1 - u0)))
    wall_strip(mb, "render", (u0, rb), (u1, rb), 0.20, -0.60, lambda x, y: max(zr(x, y), 0.0) + 1.00)          # ramp / deck
    wall_strip(mb, "render", (u1, ra), (u0 - 5.60, ra), 0.25, -0.60, lambda x, y: max(ground(x, y), zr(x, y)) + 1.00)
    # ---- retaining walls with a guard around the court (not on the gradins / stairs side) --------
    ring = list(COURT.exterior.coords)
    if not COURT.exterior.is_ccw:
        ring = ring[::-1]
    for a, b in zip(ring, ring[1:]):
        if abs(a[0] - 8.70) < 0.01 and abs(b[0] - 8.70) < 0.01:
            continue                                         # east: gradins and stairs
        if abs(a[1] - b[1]) < 0.01 and abs(a[1] + 17.10) < 0.01:
            continue                                         # south: ramp wall built above
        if abs(a[1] - b[1]) < 0.01 and abs(a[1] + 19.20) < 0.01:
            continue                                         # south-west: the local technique
        if abs(a[0] + 7.00) < 0.01 and abs(b[0] + 7.00) < 0.01:
            continue                                         # foot of the ramp
        if north_top is not None and abs(a[1] - 20.20) < 0.01 and abs(b[1] - 20.20) < 0.01:
            g0, g1 = north_gap if north_gap else (b[0], b[0])
            for p_, q_ in (((max(a[0], b[0]), 20.20), (g1, 20.20)), ((g0, 20.20), (min(a[0], b[0]), 20.20))):
                if p_[0] - q_[0] > 0.05:                     # north: guard of the stair, minus the opening
                    wall_strip(mb, "render", p_, q_, 0.25, -0.60, lambda x, y: north_top(x), side=-1.0)
            continue
        wall_strip(mb, "render", a, b, 0.25, -0.60, lambda x, y: max(ground(x, y), 0.0) + 1.00, side=-1.0)
    # north-east: short wall from the court corner to the stair, and the stair cheeks
    wall_strip(mb, "render", (8.70, 20.20), (8.70, 17.40), 0.25, -0.60, lambda x, y: max(ground(x, y), 0.0) + 1.00, side=1.0)
    wall_strip(mb, "render", (8.70, -17.10), (8.70, -17.00), 0.25, -0.60, lambda x, y: max(ground(x, y), 0.0) + 1.00, side=1.0)
    # ---- pool cover reel and shower columns ----------------------------------------------------------
    ua, ub, vr = REEL
    seg = 16
    for k in range(seg):
        a0, a1 = 2 * math.pi * k / seg, 2 * math.pi * (k + 1) / seg
        p0 = (vr + 0.24 * math.cos(a0), 0.45 + 0.24 * math.sin(a0))
        p1 = (vr + 0.24 * math.cos(a1), 0.45 + 0.24 * math.sin(a1))
        mb.poly("pool_cover", [(ua, p0[0], p0[1]), (ub, p0[0], p0[1]), (ub, p1[0], p1[1]), (ua, p1[0], p1[1])])
    for uu in (ua - 0.12, ub + 0.05):
        mb.box("metal_dark", uu, uu + 0.07, vr - 0.30, vr + 0.30, 0.0, 0.75)
    for su, sv in SHOWERS:
        L.prism(mb, "metal_dark", Point(su, sv).buffer(0.05, 12), 0.0, 2.25)
        mb.box("metal_dark", su - 0.03, su + 0.03, sv - 0.03, sv + 0.40, 2.18, 2.25)
        L.prism(mb, "metal_dark", Point(su, sv + 0.40).buffer(0.12, 16), 2.10, 2.16)
        L.prism(mb, "stone", Point(su, sv).buffer(0.45, 20), -0.05, 0.02)
    obs = mb.build("POOL", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    return ob


def lounger(M, col, name="SRC_LOUNGER"):
    """Sun lounger 1.95 x 0.75 m: timber frame on four legs, cushion, raised backrest (local +x = head)."""
    mb = C.MeshBuilder()
    mb.box("timber", -0.95, 0.95, -0.36, 0.36, 0.28, 0.33)
    for x in (-0.88, 0.80):
        for y in (-0.32, 0.26):
            mb.box("timber", x, x + 0.06, y, y + 0.06, 0.0, 0.28)
    mb.box("cushion", -0.92, 0.30, -0.34, 0.34, 0.33, 0.40)
    a = math.radians(35)
    x0, z0 = 0.30, 0.36
    pts = [(x0, -0.34, z0), (x0 + 0.62 * math.cos(a), -0.34, z0 + 0.62 * math.sin(a)),
           (x0 + 0.62 * math.cos(a), 0.34, z0 + 0.62 * math.sin(a)), (x0, 0.34, z0)]
    mb.poly("cushion", pts[::-1])
    mb.poly("cushion", [(p[0] + 0.05 * math.sin(a), p[1], p[2] - 0.05 * math.cos(a)) for p in pts])
    obs = mb.build(name, col, M)
    return L.join(obs, name)
