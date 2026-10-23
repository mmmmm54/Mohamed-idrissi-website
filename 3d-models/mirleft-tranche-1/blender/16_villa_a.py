"""
16_villa_a — villa type A (client 23-10: "zid had tranche kayn fiha hotel and villa type a, ha huwa plan dyal
villa type A"), from the villa's drawing on the plan de masse of 31-05-13 (block 'FGHF', the same drawing four
times): the outline of the house with its parapet line, the patio, the pool, the terraces and the planters.
There is no permit drawing of the type A: the heights, the openings and the finishes are those of the villas
of the complex (the render, the taupe stone surrounds, the grey ledge / ochre band cornice, the rounded coping,
the horns, quartz aluminium), to confirm.

Local frame: the drawing's own (x towards the plan's east, y towards its north, metres), origin at the south-west
corner of the house's outline; z = 0 the garden's ground, the floor +0.20.

A single-storey courtyard house round a patio with its date palm (4.52 x 4.92 m):
  the north and south wings, each with a raised salon over the patio (+5.30, the drawing's bays on the north
    and south fronts), the outer rooms lower (+4.40);
  the entrance hall between the wings on the east (+4.90), its studded door on the entrance
    court; the court (4.94 x 4.62 m) closed on the street by a wall with its arched gate;
  on the west, onto the pool, the terrace along the house and its bay between the wings under a timber pergola,
    the patio opening onto it through a pointed horseshoe arch in its screen wall;
  the pool 5.00 x 15.87 m over its coping (water 4.00 x 14.87 m), the planters along the south front.
"""
import importlib.util
import math
import os

from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t3_vc_a", os.path.join(HERE, "14_villa_c.py"))
VC = importlib.util.module_from_spec(_spec)
VC.__dict__["L"] = L
_spec.loader.exec_module(VC)
D = VC.D

ZBOT, Z_FL = -1.00, 0.20
P_ = lambda pts: Polygon(pts)
# the volumes (no two overlap): polygon, roof level, parapet top, horns (none: they would stand against the salons)
VOL = {
    "NWW": (box(0.0, 11.45, 4.60, 16.97), 3.80, 4.40, False),
    "RB": (P_([(4.60, 11.45), (10.52, 11.45), (10.52, 18.04), (6.77, 18.04), (6.77, 16.97), (4.60, 16.97)]), 4.70, 5.30, False),
    "NE": (P_([(10.52, 11.45), (12.41, 11.45), (12.41, 11.18), (17.35, 11.18), (17.35, 16.97), (11.87, 16.97), (11.87, 15.91), (10.52, 15.91)]), 3.80, 4.40, False),
    "MID": (box(10.15, 6.53, 12.41, 11.45), 4.30, 4.90, False),
    "SB": (P_([(4.60, 1.10), (6.66, 1.10), (6.66, 0.0), (10.18, 0.0), (10.18, 6.53), (4.60, 6.53)]), 4.70, 5.30, False),
    "SW1": (box(1.65, 1.10, 4.60, 6.53), 3.80, 4.40, False),
    "SW2": (P_([(10.18, 2.12), (11.81, 2.12), (11.81, 1.06), (17.35, 1.06), (17.35, 6.53), (10.18, 6.53)]), 3.80, 4.40, False),
}
PATIO = box(5.63, 6.53, 10.15, 11.45)
SCREEN = box(5.33, 6.53, 5.63, 11.45)                      # the patio's screen wall onto the terrace bay
COURT = box(12.41, 6.53, 17.05, 11.18)
COURT_W = box(17.05, 6.53, 17.35, 11.18)                    # the entrance court's wall on the street
BAY = box(0.0, 6.53, 5.33, 11.45)                           # the terrace bay under the pergola
TERRACE = unary_union([box(-2.0, 1.10, 0.0, 16.97), BAY, box(0.0, 1.10, 1.65, 6.53)])
POOL = box(-7.0, 1.10, -2.0, 16.97)                         # over the coping
WATER = box(-6.5, 1.60, -2.5, 16.47)
PLANTERS = [box(1.65, 0.0, 6.66, 1.10), box(10.18, 0.0, 11.81, 2.12), box(11.81, 0.0, 17.35, 1.06)]
HOUSE = unary_union([v[0] for v in VOL.values()] + [SCREEN, PATIO, COURT, COURT_W])
FOOT = unary_union([HOUSE, POOL, TERRACE] + PLANTERS)       # kept clear of trees
HARD = FOOT
HOUSE_C = (8.7, 9.0)
GATE_Y = (8.12, 9.62)                                       # the court's gate, y; the garden's gate on its axis
POOL_DEPTH = 1.40

S_SMALL = dict(sw=0.30, st=0.30, sb=0.30)
op = VC.op
OPENINGS = [
    op("x", 0.0, 12.30, 15.90, Z_FL, 2.90, "slider", 3),                 # NWW onto the terrace (west)
    op("y", 11.45, 0.70, 3.90, Z_FL, 2.90, "slider", 3),                 # NWW onto the terrace bay
    op("y", 16.97, 1.40, 3.00, 1.00, 2.60, "window", 2),                 # NWW, north
    op("y", 18.04, 7.25, 10.05, 1.00, 2.90, "window", 3),                # the north salon's bay
    {**op("y", 11.45, 6.35, 9.45, Z_FL, 3.20, "baie", 4), "rev": 0.36, "rev_mat": "surround"},    # north salon onto the patio
    op("y", 16.97, 12.90, 14.30, 1.00, 2.60, "window", 2),               # NE, north
    op("y", 16.97, 15.30, 16.70, 1.00, 2.60, "window", 2),
    op("x", 17.35, 13.30, 14.90, 1.00, 2.60, "window", 2),               # NE, east
    op("y", 11.18, 13.90, 15.90, 1.00, 2.60, "window", 2),               # NE onto the court
    op("x", 12.41, 8.32, 9.42, Z_FL, 2.55, "door"),                      # the entrance door on the court
    op("x", 10.15, 8.40, 9.60, Z_FL, 2.60, "slider", 2),                 # the hall onto the patio
    op("y", 0.0, 7.00, 9.80, 1.00, 2.90, "window", 3),                   # the south salon's bay
    {**op("y", 6.53, 6.35, 9.45, Z_FL, 3.20, "baie", 4), "rev": 0.36, "rev_mat": "surround"},     # south salon onto the patio
    op("x", 1.65, 2.10, 5.30, Z_FL, 2.90, "slider", 3),                  # SW1 onto the terrace (west)
    op("y", 1.10, 2.40, 3.90, 1.00, 2.60, "window", 2),                  # SW1, south
    op("y", 6.53, 2.00, 4.20, Z_FL, 2.90, "slider", 2),                  # SW1 onto the terrace bay
    op("y", 1.06, 12.70, 14.10, 1.00, 2.60, "window", 2),                # SW2, south
    op("y", 1.06, 15.20, 16.60, 1.00, 2.60, "window", 2),
    op("y", 2.12, 10.60, 11.40, 1.25, 2.55, "window", **S_SMALL),
    op("x", 17.35, 3.00, 4.60, 1.00, 2.60, "window", 2),                 # SW2, east
    op("y", 6.53, 13.90, 15.90, 1.00, 2.60, "window", 2),                # SW2 onto the court
    *[op("y", 18.04, u - 0.10, u + 0.10, 4.05, 4.25, "niche") for u in (7.40, 8.05, 8.70, 9.35, 10.00)],
    *[op("y", 0.0, u - 0.10, u + 0.10, 4.05, 4.25, "niche") for u in (7.15, 7.80, 8.45, 9.10, 9.75)],
]
VC.OPENINGS = OPENINGS
_insert = VC.insert


def insert(mb, P3, s0, s1, z0, z1, o, wall_mat):
    if o["kind"] == "door":                                 # the studded entrance door of the duplexes
        D.insert(mb, P3, s0, s1, z0, z1, o, wall_mat)
    else:
        _insert(mb, P3, s0, s1, z0, z1, o, wall_mat)


VC.insert = insert


def massing(mb):
    """Each volume's faces: from the ground where nothing stands outside, from the neighbour's roof where a
    lower volume adjoins, none against a volume as high; parapets, coping, cornice and roof terraces."""
    names = list(VOL)
    for nm in names:
        g, zr, zt, horned = VOL[nm]
        others = [(VOL[o][0], VOL[o][1], VOL[o][2]) for o in names if o != nm] + [(SCREEN, 3.0, 3.40), (COURT_W, 2.2, 2.60)]
        for p, q in VC.edges(g):
            Lg = math.dist(p, q)
            ux, uy = (q[0] - p[0]) / Lg, (q[1] - p[1]) / Lg
            nx, ny = uy, -ux
            cuts = {0.0, Lg}
            for og, _, _ in others:
                for c in og.exterior.coords:
                    s = (c[0] - p[0]) * ux + (c[1] - p[1]) * uy
                    if 0.01 < s < Lg - 0.01 and abs((c[0] - p[0]) * nx + (c[1] - p[1]) * ny) < 0.02:
                        cuts.add(round(s, 4))
            cuts = sorted(cuts)
            for s0, s1 in zip(cuts, cuts[1:]):
                m = ((s0 + s1) / 2)
                pt = Point(p[0] + ux * m + nx * 0.05, p[1] + uy * m + ny * 0.05)
                nb = [(ozr, ozt) for og, ozr, ozt in others if og.contains(pt)]
                if nb and nb[0][1] >= zt:
                    continue
                z0 = nb[0][0] if nb else ZBOT
                a = (p[0] + ux * s0, p[1] + uy * s0)
                b = (p[0] + ux * s1, p[1] + uy * s1)
                VC.cface(mb, a, b, lambda Lw, z0=z0, zr=zr: box(0.0, z0, Lw, zr - 0.02), False)
        higher = unary_union([VOL[o][0] for o in names if o != nm and VOL[o][2] >= zt]) if any(VOL[o][2] >= zt for o in names if o != nm) else Polygon()
        allo = unary_union([VOL[o][0] for o in names if o != nm])
        ring = g.difference(g.buffer(-0.30, join_style=2)).difference(higher.buffer(0.01, join_style=2))
        L.prism(mb, "villa", ring, zr - 0.02, zt - 0.06, bottom=False)
        D.coping(mb, "villa", ring, zt, 0.06)
        L.prism(mb, "terrace", g.buffer(-0.30, join_style=2), zr - 0.02, zr, sides=False)
        for z0, z1, pd, mat in ((zr - 0.42, zr - 0.35, 0.08, "ledge"), (zr - 0.35, zr - 0.21, 0.05, "band"), (zr - 0.21, zr - 0.14, 0.10, "ledge")):
            L.prism(mb, mat, g.buffer(pd, join_style=2).difference(g).difference(allo.buffer(0.005, join_style=2)), z0, z1, bottom=True)
        if horned:
            VC.horns(mb, g.buffer(0.012, join_style=2), zt)


def screen_wall(mb, g, zt, arch_w, arch_s, yc, mat="villa", gate=False):
    """A wall slab g (along y, its ends against the wings) with a pointed horseshoe arch through it centred on
    y = yc, the rounded coping; gate: a studded timber gate in the arch."""
    x0, y0, x1, y1 = g.bounds
    hole = VC.arch_poly(yc, arch_w, arch_s).intersection(box(yc - arch_w, Z_FL - 0.20, yc + arch_w, 50.0))
    face = box(y0, ZBOT, y1, zt - 0.06).difference(hole)
    for xf, sgn in ((x0, -1.0), (x1, 1.0)):
        for q in L.as_polys(face):
            for t in L.tri_poly(q):
                VC.tri_out(mb, mat, [(xf, s_, z_) for s_, z_ in t], (sgn, 0.0, 0.0))
    hc = hole.centroid
    ring = list(hole.exterior.coords)
    for (sa, za), (sb, zb) in zip(ring, ring[1:]):
        if za <= Z_FL - 0.19 and zb <= Z_FL - 0.19:
            continue
        want = (0.0, hc.x - (sa + sb) / 2, hc.y - (za + zb) / 2)
        VC.tri_out(mb, "surround", [(x0, sa, za), (x1, sa, za), (x1, sb, zb), (x0, sb, zb)], want)
    D.coping(mb, mat, g, zt, 0.06)
    if gate:
        xs = (x0 + x1) / 2
        for q in L.as_polys(hole.intersection(box(yc - arch_w, Z_FL, yc + arch_w, 50.0))):
            for t in L.tri_poly(q):
                for sgn in (-1.0, 1.0):
                    VC.tri_out(mb, "door_wood", [(xs + sgn * 0.03, s_, z_) for s_, z_ in t], (sgn, 0.0, 0.0))
        hb = hole.bounds
        for i in range(5):
            for j in range(9):
                s_ = hb[0] + 0.25 + (hb[2] - hb[0] - 0.50) * i / 4
                z_ = Z_FL + 0.25 + (arch_s - Z_FL - 0.35) * j / 8
                mb.box("metal_dark", xs + 0.03, xs + 0.045, s_ - 0.012, s_ + 0.012, z_ - 0.012, z_ + 0.012)


def grounds(mb, plants):
    # the pool: coping, jade tiles, Roman steps at its south end
    L.prism(mb, "coping", POOL.difference(WATER), -0.30, Z_FL - 0.04)
    L.prism(mb, "tile_jade", WATER, -POOL_DEPTH - 0.05, -POOL_DEPTH + 0.15, sides=False)
    L.prism(mb, "tile_jade", WATER.buffer(0.01, join_style=2).difference(WATER.buffer(-0.01, join_style=2)), -POOL_DEPTH + 0.15, Z_FL - 0.06)
    L.prism(mb, "pool_water", WATER.buffer(-0.01, join_style=2), Z_FL - 0.19, Z_FL - 0.17, sides=False)
    wx0, wy0, wx1, wy1 = WATER.bounds
    for k in range(3):
        L.prism(mb, "tile_jade", box(wx0, wy0, wx1, wy0 + 0.40 * (3 - k)), -POOL_DEPTH + 0.15, -0.20 - 0.35 * k)
    # terraces, patio, court at the floor level
    L.prism(mb, "terrace", TERRACE, -0.40, Z_FL - 0.005)
    L.prism(mb, "deck_stone", PATIO, -0.40, Z_FL - 0.005)
    L.prism(mb, "deck_stone", COURT, -0.40, Z_FL - 0.005)
    L.prism(mb, "interior_floor", unary_union([v[0] for v in VOL.values()]).buffer(-0.02, join_style=2), -0.40, Z_FL - 0.01)
    # the patio's palm in its square planter with a stone rim
    pc = PATIO.centroid
    pl = box(pc.x - 0.70, pc.y - 0.70, pc.x + 0.70, pc.y + 0.70)
    L.prism(mb, "coping_beige", pl.difference(pl.buffer(-0.12, join_style=2)), Z_FL, Z_FL + 0.45)
    L.prism(mb, "soil", pl.buffer(-0.12, join_style=2), Z_FL, Z_FL + 0.40, sides=False)
    plants.append(("date", pc.x, pc.y, Z_FL + 0.40, 0.75))
    # the planters along the south front
    for g in PLANTERS:
        L.prism(mb, "coping_beige", g.difference(g.buffer(-0.12, join_style=2)), -0.30, 0.55)
        L.prism(mb, "soil", g.buffer(-0.12, join_style=2), -0.30, 0.48, sides=False)
        x0, y0, x1, y1 = g.buffer(-0.35, join_style=2).bounds
        n = max(1, int((max(x1 - x0, y1 - y0)) / 1.1))
        for k in range(n + 1):
            t = k / max(1, n)
            plants.append(("shrub", x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 0.48, 0.85))
    # the pergola over the terrace bay: rafters from wing to wing, an edge beam on the pool side
    bx0, by0, bx1, by1 = BAY.bounds
    k = 0
    x = bx0 + 0.15
    while x < bx1 - 0.10:
        mb.box("timber", x - 0.05, x + 0.05, by0, by1, 2.98, 3.16)
        x += 0.55
        k += 1
    mb.box("timber", bx0 + 0.02, bx0 + 0.20, by0, by1, 2.80, 2.98)
    for y in (by0 + 0.12, by1 - 0.12):
        mb.box("timber", bx0 + 0.04, bx0 + 0.18, y - 0.07, y + 0.07, Z_FL, 2.80)


def build(M, col, name="SRC_T3_VILLA_A"):
    mb = C.MeshBuilder()
    plants = []
    massing(mb)
    screen_wall(mb, SCREEN, 3.40, 2.40, 2.20, PATIO.centroid.y)
    screen_wall(mb, COURT_W, 2.60, 1.50, 1.80, (GATE_Y[0] + GATE_Y[1]) / 2, gate=True)
    grounds(mb, plants)
    obs = mb.build("VILLA_A", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob, plants
