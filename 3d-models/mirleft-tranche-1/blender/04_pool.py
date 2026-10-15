"""
04_pool — the pool court of the 1er TRANCHE (block 'PISCINE' of the plan de masse 12-10).

Pool-local frame: origin at the centre of the basin (DWG 251999.57, 119407.49), axes turned by
-24.02 deg (u across the pool towards the gradins, v along it to the north-north-east), z = 0 at
the deck ('PLAGE PISCINE').

Read from the plan:
  CUVE            21.71 x 7.50 m basin, Roman steps (four arcs) in two opposite corners
  PISCINE ENFANT  9.6 x 3.8 m shallow pool at the south end, against the basin (built square to it)
  TRANSATS        31 lounger drawings (one of them a pair) on the west and east decks; the west row is
                  completed to eighteen, evenly spaced and square to the basin (15-10)
  PR              ten 0.45 m circles between the lounger pairs of the east deck: parasols (INFERRED)
  GRADINS         three planted strips (the plan hatches them 'JARDIN', 0.62 m) stepping up from the
                  deck to the upper level, flanked by the two 'ESCALIERS PISCINE' of ten steps
                  (numbered 1-10, rising to the east)
  LES BACS A FLEURS  four 1.45 m planters with the four palms ('palmier')
  RAMPE           1.4 m ramp along the south side, walls on both sides
  JARDIN          planted beds along the north side and in the north-east corner; 'COUVERTURE PISCINE
                  AMOVIBLE' (cover reel); 'colonnes de douche', two at the north-east, two by the
                  local technique
Levels: the court is sunk; the gradins (four risers of 0.425 m) and the stairs (ten of 0.17 m) climb
1.70 m to the upper walk on the east. The other sides are retaining walls.

Look and finishes from the reference images of 15-10 (to confirm): rubble stone walls with travertine
caps, travertine planks, a black overflow grille round the basins, three timber cabanas on the west
deck, planting (agaves, grasses, shrubs) in every bed, and
two tiers of planted stone terraces between the upper walk and the lawn by the restaurant terrace,
with a stair up to the lawn in line with each pool stair.
"""
import math
import random

from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C

RISE = 1.70
LAWN = 0.15                                             # top of the paving round the court above the graded ground (scene OFFS)
COURT = unary_union([box(-12.40, -17.10, 8.70, 20.20), box(-12.60, -19.20, -7.00, -17.10)])
DECK_E = box(8.70, -14.30, 9.10, 15.00)                 # deck strip in front of the gradins
GRAD_F = [9.10, 9.92, 10.72, 11.50]                     # fronts of the three gradins and of the upper walk
GRAD_V = (-14.30, 15.00)
GRAD_SOIL_V = (-13.93, 14.61)                           # the plan's 'JARDIN' strips
GRAD_WALL = 0.18
STAIRS = [box(8.70, 15.00, 11.50, 17.40), box(8.70, -17.00, 11.50, -14.30)]
BACS = [(7.60, 9.05, v - 0.725, v + 0.725) for v in (13.93, 5.33, -5.46, -13.39)]   # centred on the palms
BAC_SOIL = 0.48
RAMP = (-7.00, 11.50, -18.60, -17.25)                   # u0, u1 (upper end), v0, v1
BED_N = box(-12.40, 17.55, 4.30, 20.20)
BED_W = box(-12.40, -8.96, -11.60, 17.55)               # planting at the wall foot (reference images)
BED_SW = box(-12.40, -17.10, -11.85, -11.59)
BED_NE = box(8.70, 17.40, 11.50, 20.20)                 # the plan's 'JARDIN' in the north-east corner
BED_SOIL = 0.42
REEL = (-6.50, 3.80, 17.20)
SHOWERS = [(5.70, 18.90), (7.10, 18.90), (-11.70, -9.40), (-11.70, -10.80)]
CUVE_CORNERS = [((-3.75, 10.85), (1, -1)), ((3.75, -10.85), (-1, 1))]
KIDS_POOL = box(-6.05, -14.82, 3.55, -11.02)            # 9.60 x 3.80 m, square to the basin (the hatch is drawn askew)
WEST_LOUNGERS = [(-5.00, -9.91 + 1.235 * k) for k in range(18)]   # the plan's twelve plus six, in one even row
PARASOLS = [(8.70, v) for v in (-11.55, -9.68, -7.49, -3.29, -1.09, 1.10, 3.30, 7.50, 9.70, 11.90)]
CABANAS = [(-10.10, 10.00), (-10.10, 5.00), (-10.10, 0.00)]
# upper level, east of the gradins
WALK = (11.50, 13.90)
TIERS = ((13.90, 14.15, 15.10), (15.10, 15.35, 16.20))  # (wall u0, wall u1 = soil u0, soil u1)
ZONE_E = 16.20                                          # the lawn beyond (the restaurant terrace border is past 16.23)
ZONE_V = (-18.90, 20.45)
N_WALL = box(8.70, 20.20, ZONE_E, 20.50)
UP_V = [(15.00, 17.40), (-17.00, -14.30)]               # stairs up to the lawn, in line with the pool stairs
WALL_T = 0.30
LAY = {}


def solid(mb, mat, poly, z0, top, sides=True, top_mat=None):
    """Prism from a flat bottom z0 to a top that is a number or a function top(u, v) (exact if linear)."""
    f = top if callable(top) else (lambda x, y, c=top: c)
    for pg in L.as_polys(poly):
        if pg.area < 1e-4:
            continue
        for t in L.tri_poly(pg):
            mb.poly(top_mat or mat, [(x, y, f(x, y)) for x, y in t], [(x, y) for x, y in t])
        if not sides:
            continue
        for k, ring in enumerate([pg.exterior] + list(pg.interiors)):
            c = list(ring.coords)
            outer = k == 0
            for (ax, ay), (bx, by) in zip(c, c[1:]):
                p, q = ((ax, ay), (bx, by)) if ring.is_ccw == outer else ((bx, by), (ax, ay))
                Lg = math.dist(p, q)
                if Lg < 1e-5:
                    continue
                za, zb = f(*p), f(*q)
                mb.poly(mat, [(p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], zb), (p[0], p[1], za)],
                        [(0.0, z0), (Lg, z0), (Lg, zb), (0.0, za)])


def wall(mb, poly, top, z0=-0.60):
    """Rubble stone wall with a travertine cap; top: number or function top(u, v)."""
    f = top if callable(top) else (lambda x, y, c=top: c)
    if poly.is_empty:
        return
    solid(mb, "stone", poly, z0, f)
    L.prism(mb, "deck_stone", poly.buffer(0.02, join_style=2), 0.0, 0.04, zf=f)


def layout(ground, avoid=None):
    """Upper level: the walk at RISE behind the gradins, two tiers of planted stone terraces up to the
    lawn, a stair up to it in line with each pool stair (risers of at most 0.17 m, treads 0.30 m).
    ground(u, v): graded ground above the deck (a plane, so linear). avoid: pool-local area kept
    clear (the road's footway, which cuts the south-east corner)."""
    zone = box(GRAD_F[3], ZONE_V[0], ZONE_E, ZONE_V[1])
    if avoid is not None and not avoid.is_empty:
        zone = max(L.as_polys(zone.difference(avoid.buffer(0.02, join_style=2))), key=lambda p: p.area)
    ups = []
    for v0, v1 in UP_V:
        vm = 0.5 * (v0 + v1)
        n = 4
        for _ in range(5):
            n = max(2, int(math.ceil((ground(WALK[1] + 0.30 * (n - 1), vm) + LAWN - RISE) / 0.17 - 1e-6)))
        uT = WALK[1] + 0.30 * (n - 1)
        zT = ground(uT, vm) + LAWN
        uE = max(uT + 0.30, ZONE_E)
        ups.append({"v0": v0, "v1": v1, "n": n, "uT": uT, "zT": zT, "h": (zT - RISE) / n, "uE": uE})
    LAY.clear()
    LAY.update(zone=zone, ups=ups, ground=ground)
    return LAY


def s1(ground):
    return lambda u, v: 0.5 * ground(u, v) + 0.5 * RISE        # first tier: halfway up to the lawn


def s2(ground):
    return lambda u, v: ground(u, v) + LAWN                     # second tier: the lawn level


def level_at(u, v):
    """Finished level of the upper zone at (u, v) (the walk, tier walls and beds, the lawn beyond)."""
    g = LAY["ground"]
    if u < TIERS[0][0]:
        return RISE
    if u < TIERS[0][1]:
        return s1(g)(u, v) + 0.08
    if u < TIERS[1][0]:
        return s1(g)(u, v)
    if u < TIERS[1][1]:
        return s2(g)(u, v) + 0.08
    return s2(g)(u, v)


def up_boxes(st):
    v0, v1, uE = st["v0"], st["v1"], st["uE"]
    return box(WALK[1], v0 - 0.25, uE, v1 + 0.25)


def footprint():
    """Area cut out of the generic ground (court, walls, gradins, stairs, ramp, upper level)."""
    court = unary_union([COURT, DECK_E, box(GRAD_F[0], GRAD_V[0], GRAD_F[3], GRAD_V[1]), BED_NE] + STAIRS)
    g = [court.buffer(WALL_T, join_style=2), box(RAMP[0], RAMP[2] - WALL_T, RAMP[1], RAMP[3]), N_WALL, LAY["zone"]]
    g += [up_boxes(st) for st in LAY["ups"]]
    return unary_union(g)


def wall_strip(mb, a, b, t, z0, ztop, side=1.0, seg=1.5):
    """Stone wall of thickness t on one side of the line a->b; bottom z0, top ztop(x, y) sampled every seg."""
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
        wall(mb, Polygon([p, q, (q[0] + nx * t, q[1] + ny * t), (p[0] + nx * t, p[1] + ny * t)]), zt, z0)


def scatter(spots, rng, poly, z, step, mix, inset=0.12):
    """Plants on a jittered grid inside poly: (u, v, z, kind, scale); z number or function."""
    poly = poly.buffer(-inset, join_style=2)
    if poly.is_empty:
        return
    x0, y0, x1, y1 = poly.bounds
    kinds = [m[0] for m in mix]
    wts = [m[1] for m in mix]
    nu = max(1, int((x1 - x0) / step + 0.5))
    nv = max(1, int((y1 - y0) / step + 0.5))
    for i in range(nu):
        for j in range(nv):
            u = x0 + (x1 - x0) * (i + 0.5) / nu + rng.uniform(-0.25, 0.25) * step
            v = y0 + (y1 - y0) * (j + 0.5) / nv + rng.uniform(-0.30, 0.30) * step
            if not poly.contains(Point(u, v)):
                continue
            k = rng.choices(kinds, wts)[0]
            m = mix[kinds.index(k)]
            zz = z(u, v) if callable(z) else z
            spots.append((u, v, zz, k, rng.uniform(m[2], m[3])))


MIX_GRAD = [("grass", 0.45, 0.80, 1.15), ("agave", 0.35, 0.90, 1.25), ("shrub", 0.20, 0.65, 0.90)]
MIX_BED = [("shrub", 0.40, 0.85, 1.30), ("grass", 0.30, 0.90, 1.20), ("agave", 0.30, 1.00, 1.40)]


def build(M, col, ground, water_polys, name="POOL_COURT", north_steps=(), north_gap=(7.40, 8.70)):
    """ground(u, v): graded ground above the deck at a pool-local point (linear).
    water_polys: {'pool': Polygon, 'kids_pool': Polygon} in pool-local coordinates.
    north_steps: [(u0, u1, level)] of the long stair north of the court (its treads above the deck);
    the court's north wall is its 1 m guard, open over north_gap where the stair lands on the deck.
    layout() must have been called. Returns (object, plant spots [(u, v, z, kind, scale)])."""
    rng = random.Random(1510)
    spots = []
    mb = C.MeshBuilder()
    pool = water_polys["pool"]
    kids = KIDS_POOL
    G = ground
    top_out = lambda u, v: G(u, v) + 0.60                       # retaining walls: parapet over the ground
    # ---- basins: one outline (the two pools side by side), lip, overflow grille ------------------
    basin = unary_union([pool, kids]).buffer(0.08, join_style=2).buffer(-0.08, join_style=2)
    grille = basin.buffer(0.25, join_style=2).difference(basin)
    divider = basin.difference(pool).difference(kids)
    rim = basin.difference(basin.buffer(-0.05, join_style=2)).union(divider)
    L.prism(mb, "grille", grille, -0.30, -0.01)
    L.prism(mb, "pool_tile", divider, -1.45, -0.12)
    L.prism(mb, "coping", rim, -0.12, -0.015)
    for w, depth in ((pool, 1.40), (kids, 0.45)):
        L.prism(mb, "pool_tile", w, -depth - 0.05, -depth, sides=False)
        L.prism(mb, "pool_tile", w.buffer(0.01, join_style=2).difference(w.buffer(-0.01, join_style=2)), -depth, -0.03)
        L.prism(mb, "pool_water", w.buffer(-0.01, join_style=2), -0.05, -0.03, sides=False)
    for (cx, cy), (su, sv) in CUVE_CORNERS:                     # Roman steps: quarter discs
        for r, z in ((1.75, -1.05), (1.30, -0.70), (0.85, -0.35)):
            q = Point(cx, cy).buffer(r, 32).intersection(box(min(cx, cx + su * 3), min(cy, cy + sv * 3), max(cx, cx + su * 3), max(cy, cy + sv * 3)))
            L.prism(mb, "pool_tile", q.intersection(pool), -1.40, z)
    # ---- deck: travertine planks -----------------------------------------------------------------
    bacs = unary_union([box(u0, va, u1, vb) for u0, u1, va, vb in BACS])
    beds = unary_union([BED_N, BED_W, BED_SW])
    deck = unary_union([COURT, DECK_E]).difference(basin.buffer(0.25, join_style=2)).difference(beds).difference(bacs)
    solid(mb, "deck_stone", deck, -0.60, 0.0, top_mat="planks")
    # ---- planted beds of the court (stone kerbs) and the palm planters ---------------------------
    for bed in (unary_union([BED_N, BED_W]), BED_SW):
        wall(mb, L.ring_poly(bed, 0.20), BED_SOIL + 0.08, -0.30)
        L.prism(mb, "soil", bed.buffer(-0.20, join_style=2), -0.30, BED_SOIL, sides=False)
    scatter(spots, rng, BED_N.buffer(-0.20, join_style=2), BED_SOIL, 0.65, MIX_BED, inset=0.05)
    scatter(spots, rng, BED_W.buffer(-0.20, join_style=2).difference(BED_N), BED_SOIL, 0.55, MIX_BED, inset=0.0)
    scatter(spots, rng, BED_SW.buffer(-0.20, join_style=2), BED_SOIL, 0.55, MIX_BED, inset=0.0)
    for u0, u1, va, vb in BACS:
        bx = box(u0, va, u1, vb)
        wall(mb, L.ring_poly(bx, 0.18), BAC_SOIL + 0.07, -0.30)
        L.prism(mb, "soil", bx.buffer(-0.18, join_style=2), -0.30, BAC_SOIL, sides=False)
        cu, cv = 0.5 * (u0 + u1), 0.5 * (va + vb)
        for du, dv in ((-0.36, -0.36), (0.36, -0.30), (-0.30, 0.36), (0.34, 0.34)):
            spots.append((cu + du, cv + dv, BAC_SOIL, "agave", rng.uniform(0.70, 0.95)))
    # ---- gradins: three planted strips in stone, the upper walk behind -------------------------------
    v0, v1 = GRAD_V
    for k in range(3):
        lip = RISE * (k + 1) / 4
        blk = box(GRAD_F[k], v0, GRAD_F[k + 1], v1)
        soil = box(GRAD_F[k] + GRAD_WALL, GRAD_SOIL_V[0], GRAD_F[k + 1], GRAD_SOIL_V[1])
        wall(mb, blk.difference(soil), lip, -0.30)
        L.prism(mb, "soil", soil, -0.30, lip - 0.07, sides=False)
        scatter(spots, rng, soil, lip - 0.07, 0.48, MIX_GRAD, inset=0.08)
    # ---- 'ESCALIERS PISCINE': ten risers of 0.17 rising to the east, planks ---------------------------
    for s in STAIRS:
        x0, y0, x1, y1 = s.bounds
        for k in range(10):
            solid(mb, "planks", box(x0 + (x1 - x0) * k / 10, y0, x0 + (x1 - x0) * (k + 1) / 10, y1), -0.30, 0.17 * (k + 1))
    # ---- north-east 'JARDIN': raised planter beside the north pool stair ------------------------------
    ne_top = RISE + 0.40
    wall(mb, BED_NE.difference(box(8.95, 17.65, 11.25, 20.20)), ne_top + 0.08, -0.30)
    L.prism(mb, "soil", box(8.95, 17.65, 11.25, 20.20), -0.30, ne_top, sides=False)
    scatter(spots, rng, box(8.95, 17.65, 11.25, 20.20), ne_top, 0.60, MIX_BED)
    # ---- upper level: walk, tiers of planted terraces, stairs up to the lawn --------------------------
    zone = LAY["zone"]
    ups = LAY["ups"]
    f1, f2 = s1(G), s2(G)
    cut = unary_union([up_boxes(st) for st in ups])
    swall = zone.difference(affinity.translate(zone, 0.0, WALL_T))
    inner = zone.difference(N_WALL).difference(swall)
    wall(mb, N_WALL, top_out, -0.30)
    wall(mb, swall, top_out, -0.30)
    walk = inner.intersection(box(WALK[0], -99, WALK[1], 99))
    solid(mb, "stone", walk, -0.30, RISE, top_mat="planks")
    L.prism(mb, "deck_stone", box(WALK[0], v0, WALK[0] + 0.30, v1), RISE - 0.03, RISE + 0.002, sides=False)
    (a0, a1, a2), (b0, b1, b2) = TIERS
    wall(mb, inner.intersection(box(a0, -99, a1, 99)).difference(cut), lambda u, v: f1(u, v) + 0.08, 0.60)
    bed1 = inner.intersection(box(a1, -99, a2, 99)).difference(cut)
    solid(mb, "soil", bed1, 0.60, f1, sides=False)
    wall(mb, inner.intersection(box(b0, -99, b1, 99)).difference(cut), lambda u, v: f2(u, v) + 0.08, 0.60)
    bed2 = inner.intersection(box(b1, -99, b2, 99)).difference(cut)
    solid(mb, "soil", bed2, 0.60, f2)
    scatter(spots, rng, bed1, f1, 0.55, MIX_BED, inset=0.10)
    scatter(spots, rng, bed2, f2, 0.55, MIX_BED, inset=0.10)
    for st in ups:
        sv0, sv1, n, h, uT, zT, uE = st["v0"], st["v1"], st["n"], st["h"], st["uT"], st["zT"], st["uE"]
        edges = [WALK[1] + 0.30 * j for j in range(n)]          # risers
        treads = [(edges[j], edges[j + 1], RISE + h * (j + 1)) for j in range(n - 1)]
        for ta, tb, z in treads:
            solid(mb, "planks", box(ta, sv0, tb, sv1), 0.60, z)
        if uT + 0.30 <= ZONE_E + 1e-6:                           # path through the beds to the lawn
            solid(mb, "planks", box(uT, sv0, ZONE_E, sv1), 0.60, f2)
            tops = treads + [(uT, ZONE_E, None)]
        else:                                                     # landing at the lawn level
            solid(mb, "planks", box(uT, sv0, uT + 0.30, sv1), 0.60, zT)
            tops = treads + [(uT, uT + 0.30, zT)]
        for ta, tb, z in tops:                                    # stone cheeks, cut at the tier lines
            cuts = sorted({ta, tb} | {x for x in (a0, a1, b0, b1, ZONE_E) if ta < x < tb})
            for ca, cb in zip(cuts, cuts[1:]):
                um = 0.5 * (ca + cb)
                for va_, vb_ in ((sv0 - 0.25, sv0), (sv1, sv1 + 0.25)):
                    vo = va_ - 0.30 if va_ < sv0 else vb_ + 0.30
                    zl = level_at(um, vo) if um < ZONE_E else G(um, vo) + LAWN
                    zs = z if z is not None else f2(um, 0.5 * (sv0 + sv1))
                    wall(mb, box(ca, va_, cb, vb_), max(zl, zs) + 0.08, 0.60)
    # ---- ramp along the south side: from the deck (west) up to the walk (east) --------------------------
    u0, u1, ra, rb = RAMP
    zr = lambda x: RISE * min(1.0, max(0.0, (x - u0) / (u1 - u0)))
    n = 24
    for i in range(n):
        ua, ub = u0 + (u1 - u0) * i / n, u0 + (u1 - u0) * (i + 1) / n
        mb.poly("planks", [(ua, ra, zr(ua)), (ub, ra, zr(ub)), (ub, rb, zr(ub)), (ua, rb, zr(ua))], [(ua, ra), (ub, ra), (ub, rb), (ua, rb)])
    wall(mb, box(u0, rb, u1, rb + 0.25), lambda x, y: zr(x) + 0.90)                       # guard over the court / stair
    wall(mb, box(u0, ra - WALL_T, u1, ra), top_out)                                        # retaining the ground
    # ---- retaining walls round the court ---------------------------------------------------------------
    T = WALL_T
    for g_ in (box(-12.40 - T, -17.10, -12.40, 20.20 + T),                                # west
               box(-12.60 - T, -19.20 - T, -12.60, -17.10),                                 # local technique side
               box(-12.60 - T, -19.20 - T, -7.00 + T, -19.20),                              # south-west
               box(-7.00, -19.20 - T, -7.00 + T, ra - T)):                                  # under the ramp's foot
        wall(mb, g_, top_out)
    for ua, ub, z in north_steps:                                 # north: the stair's guard, open where it lands
        ua, ub = max(ua, -12.40 - T), min(ub, north_gap[0])
        if ub - ua > 0.02:
            wall(mb, box(ua, 20.20, ub, 20.20 + T), z + 1.00)
    # ---- pool cover reel and shower columns ---------------------------------------------------------------
    ua, ub, vr = REEL
    seg = 16
    for k in range(seg):
        a0_, a1_ = 2 * math.pi * k / seg, 2 * math.pi * (k + 1) / seg
        p0 = (vr + 0.24 * math.cos(a0_), 0.45 + 0.24 * math.sin(a0_))
        p1 = (vr + 0.24 * math.cos(a1_), 0.45 + 0.24 * math.sin(a1_))
        mb.poly("pool_cover", [(ua, p0[0], p0[1]), (ub, p0[0], p0[1]), (ub, p1[0], p1[1]), (ua, p1[0], p1[1])])
    for uu in (ua - 0.12, ub + 0.05):
        mb.box("metal_dark", uu, uu + 0.07, vr - 0.30, vr + 0.30, 0.0, 0.75)
    for su, sv in SHOWERS:
        L.prism(mb, "metal_dark", Point(su, sv).buffer(0.05, 12), 0.0, 2.25)
        mb.box("metal_dark", su - 0.03, su + 0.03, sv - 0.03, sv + 0.40, 2.18, 2.25)
        L.prism(mb, "metal_dark", Point(su, sv + 0.40).buffer(0.12, 16), 2.10, 2.16)
        L.prism(mb, "grille", Point(su, sv).buffer(0.45, 20), -0.05, 0.005, sides=False)
    obs = mb.build("POOL", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    return ob, spots


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


def parasol(M, col, name="SRC_PARASOL"):
    """Market parasol: weighted base, timber pole, eight-panel canvas canopy 2.70 m across."""
    mb = C.MeshBuilder()
    L.prism(mb, "metal_dark", Point(0, 0).buffer(0.22, 16), 0.0, 0.06)
    L.prism(mb, "timber", Point(0, 0).buffer(0.025, 8), 0.06, 2.62)
    n, R, zr, za = 8, 1.35, 2.22, 2.58
    rim = [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        (xa, ya), (xb, yb) = rim[k], rim[(k + 1) % n]
        mb.poly("canvas", [(xa, ya, zr), (xb, yb, zr), (0.0, 0.0, za)])
        mb.poly("canvas", [(xa, ya, zr), (xb, yb, zr), (xb, yb, zr - 0.14), (xa, ya, zr - 0.14)])
    L.prism(mb, "timber", Point(0, 0).buffer(0.04, 8), za, za + 0.10)
    obs = mb.build(name, col, M)
    return L.join(obs, name)


def cabana(M, col, name="SRC_CABANA"):
    """Timber cabana 2.60 x 2.40 x 2.50 m (local +x = open front): slatted roof, back and sides, daybed."""
    mb = C.MeshBuilder()
    X, Y, H = 1.30, 1.20, 2.50
    for x in (-X, X - 0.12):
        for y in (-Y, Y - 0.12):
            mb.box("timber", x, x + 0.12, y, y + 0.12, 0.0, H)
    for y in (-Y, Y - 0.12):
        mb.box("timber", -X, X, y, y + 0.12, H - 0.22, H)
    for x in (-X, X - 0.12):
        mb.box("timber", x, x + 0.12, -Y, Y, H - 0.22, H - 0.02)
    x = -X + 0.10
    while x < X - 0.10:                                      # roof slats
        mb.box("timber", x, x + 0.06, -Y, Y, H - 0.06, H - 0.01)
        x += 0.14
    y = -Y + 0.14
    while y < Y - 0.14:                                      # back slats
        mb.box("timber", -X + 0.02, -X + 0.08, y, y + 0.05, 0.10, H - 0.22)
        y += 0.11
    for ys in (-Y + 0.03, Y - 0.09):                         # side slats, back half
        x = -X + 0.14
        while x < -0.10:
            mb.box("timber", x, x + 0.05, ys, ys + 0.06, 0.10, H - 0.22)
            x += 0.11
    mb.box("timber", -1.10, 1.00, -1.00, 1.00, 0.0, 0.35)
    mb.box("cushion", -1.05, 0.95, -0.95, 0.95, 0.35, 0.50)
    for y in (-0.62, 0.0, 0.62):
        mb.box("canvas", -1.02, -0.80, y - 0.26, y + 0.26, 0.50, 0.85)
    obs = mb.build(name, col, M)
    return L.join(obs, name)


def agave(seed, n=17, length=0.55):
    """Agave rosette: tapered, keeled leaves, upright in the centre, spreading outside (about 0.9 m across)."""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    for i in range(n):
        a = i * 2.39996 + r.uniform(-0.12, 0.12)             # golden angle
        f = i / (n - 1)                                       # 0 = outer, 1 = inner
        tilt = math.radians(18 + 55 * f + r.uniform(-6, 6))
        Lf = length * (1.05 - 0.35 * f) * r.uniform(0.85, 1.1)
        w = 0.075 * r.uniform(0.9, 1.15)
        d = (math.cos(a), math.sin(a))
        s = (-math.sin(a), math.cos(a))
        prof = [(0.0, 0.55), (0.30, 1.0), (0.70, 0.62), (1.0, 0.0)]
        pts = []
        for t, hw in prof:
            tl = tilt - 0.30 * t * (1 - f)                     # outer leaves droop a little
            cx, cz = Lf * t * math.cos(tl), Lf * t * math.sin(tl) + 0.03
            c = (d[0] * cx, d[1] * cx, cz)
            e = w * hw
            k = e * 0.35                                       # keel: edges lower than the midrib
            pts.append(((c[0] - s[0] * e, c[1] - s[1] * e, c[2] - k), c, (c[0] + s[0] * e, c[1] + s[1] * e, c[2] - k)))
        for j in range(len(pts) - 1):
            (l0, m0, r0), (l1, m1, r1) = pts[j], pts[j + 1]
            mb.poly("agave", [l0, l1, m1, m0])
            mb.poly("agave", [m0, m1, r1, r0])
    return mb
