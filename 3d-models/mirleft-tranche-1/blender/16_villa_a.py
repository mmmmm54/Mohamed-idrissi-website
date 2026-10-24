"""
16_villa_a — villa type A, from VILLA_TYPE_A.dwg (client 24-10: "sla7 villa type a because machi hadchi likaynin
f plan and face principal": REZ DE CHAUSSEE, TERRASSE, PLAN MASSE, façades principale, arrière, gauche and droite,
coupes A-A and B-B). It replaces the model of 23-10 read from the plan de masse's drawing of the villa.

Local frame: the drawing's (x towards the plan's east, y towards its north, metres), origin at the south-west
corner of the house (the west faces of the towers at x 0, the south protrusion and the outside stair at y 0):
the REZ DE CHAUSSEE's origin is DWG (47625.405, 290040.742), the TERRASSE's 28.204 m east of it. z = 0 is the
natural ground (T.N), the floor +0.20 as the drawing's levels.

A single-storey kasbah house round a patio, in the style of the villa type C (the plans and façades):
  four battered towers at the corners (the salon and the kitchen on the north, Chambres I and III on the south):
    walls leaning in 0.254 m over their 4.06 m, grooves at 0.53 / 1.41 / 2.29 / 3.17, a row of square niches
    under the cornice (grey ledge / ochre band / grey ledges, 4.06 - 4.44), parapet +4.80 with the rounded coping
    (its horns gone since 24-10, as on all the houses), roofs +3.92, a door in each parapet onto the central roof terrace;
  the central band between them (coin cheminée north, the hall, Chambre II south), plumb walls, parapet +4.70
    (+4.55 on the north protrusion), its roof terrace reached by the outside stair along Chambre I (21 risers,
    solid, the local technique under it); round the patio (garden, glazed on its four sides) its walls rise to the
    parapet;
  over the hall the entrance block, +6.20: on the entrance terrace the studded portal (1.85 x 3.79)
    and its studded panel over it, the doors onto the roof terrace on its north and south faces;
  the chimney of the coin cheminée with its rounded top and oculus (DETAIL 2);
  on the pool side the salon's and Chambre I's 4-leaf glazing in their stepped stone surrounds, the west terrace
    between them before the patio's glazing; on the street side the entrance terrace between the towers with its
    benches, planters along the east fronts and either side of the entrance;
  the pool 5.00 x 16.47 m over its coping (water 4.00 x 15.47 m), the deck along the house.
The façade droite is drawn mirrored (its chimney and doors on the wrong side): the plans win, as for the villas
types C and the SPA.
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
ZB, TB = 4.06, 0.254                          # towers: top of the lean, inset at the top
Z_TR, Z_TT = 3.92, 4.80                       # roofs (towers and band), tower parapets (coping)
Z_BP, Z_BN = 4.70, 4.55                       # band parapet, its north protrusion
Z_EW, Z_ET = 5.94, 6.00                       # entrance block: walls, coping
ENTRY_R = 5.76                                # its roof (its parapet's faces over it)
COP = 0.06
VC.ZB, VC.TB = ZB, TB                         # the villa C's faces lean as these towers

TOWERS = {   # outline, the parapet's door onto the band's roof (side, from, to)
    "NW": (box(0.0, 11.417, 5.531, 17.568), "E", (14.426, 15.626)),      # salon
    "SW": (box(0.0, 1.088, 5.531, 7.127), "E", (3.508, 4.708)),          # Chambre I
    "NE": (box(12.25, 11.417, 17.349, 17.566), "W", (14.426, 15.626)),   # cuisine
    "SE": (box(12.25, 1.088, 17.349, 7.127), "W", (3.508, 4.708)),       # Chambre III
}
BAND = Polygon([(5.331, 1.088), (6.666, 1.088), (6.666, 0.0), (12.45, 0.0), (12.45, 18.634), (5.331, 18.634)])
PATIO = box(5.731, 7.127, 10.251, 11.417)               # inside its walls
ENTRY = box(10.251, 6.79, 12.45, 12.0)                  # the entrance block over the hall
TER_W = box(0.0, 7.127, 5.331, 11.417)                  # the west terrace (pool side)
TER_E = box(12.45, 7.127, 17.349, 11.417)               # the entrance terrace (street side)
STAIR = (0.199, 5.599, 6.666, 0.19, 1.088)              # foot, top of the flight, end of the landing; y in, y out
CHIMNEY = box(8.56, 17.44, 9.33, 18.04)
POOL = box(-7.0, 1.098, -2.0, 17.568)                   # over the coping
WATER = box(-6.5, 1.598, -2.5, 17.068)
DECK = box(-2.0, 1.098, 0.0, 17.568)
PLANTERS = [box(17.449, 1.088, 18.749, 7.027), box(17.449, 7.027, 18.749, 8.027),
            box(17.449, 10.517, 18.749, 11.517), box(17.449, 11.517, 18.749, 17.566)]
HOUSE = unary_union([t[0] for t in TOWERS.values()] + [BAND]).buffer(0)
FOOT = unary_union([HOUSE, POOL, DECK, TER_W, TER_E, box(STAIR[0], 0.0, STAIR[2], STAIR[4])] + PLANTERS)   # kept clear of trees
HARD = FOOT
HOUSE_C = (8.7, 9.3)
GATE_Y = (8.52, 10.02)                                  # the garden's gate, on the entrance terrace's axis
POOL_DEPTH = 1.40

op = VC.op


def niches(axis, c, u0, u1, z0, step=0.90, w=0.20):
    n = max(1, int((u1 - u0) / step))
    return [op(axis, c, u0 + (u1 - u0) * (k + 0.5) / n - w / 2, u0 + (u1 - u0) * (k + 0.5) / n + w / 2, z0, z0 + w, "niche") for k in range(n)]


SMALL = dict(sw=0.28, st=0.28, sb=0.28)                 # the wide stone frames of the small windows
STEP = dict(rev=0.30, rev_mat="surround")
OPENINGS = [
    # pool side: the salon's and Chambre I's glazing, 4 leaves, set back in stepped stone surrounds
    {**op("x", 0.0, 12.46, 16.46, Z_FL, 2.55, "baie", 4), **STEP},
    {**op("x", 0.0, 2.14, 6.50, Z_FL, 2.55, "baie", 4), **STEP},
    # the towers' windows (façades and RDC)
    op("y", 17.568, 1.46, 3.46, 1.00, 2.79, "window", 2),                  # salon, north
    op("y", 17.566, 13.90, 15.90, 1.00, 2.79, "window", 2),                # cuisine, north
    op("x", 17.349, 12.94, 13.63, 1.22, 2.71, "window", 1, **SMALL),       # cuisine's W.C., east
    op("x", 17.349, 5.23, 5.93, 1.22, 2.71, "window", 1, **SMALL),         # Chambre III's bathroom, east
    op("y", 1.088, 13.94, 15.84, 1.00, 2.79, "window", 2),                 # Chambre III, south
    op("y", 11.417, 2.15, 3.75, 1.00, 2.60, "window", 2),                  # salon onto the west terrace
    op("y", 7.127, 2.15, 3.75, 1.00, 2.60, "window", 2),                   # Chambre I onto the west terrace
    # the band: the coin cheminée's two doors to the north garden, Chambre II's door and window, the L.T.'s door
    op("y", 18.634, 5.87, 6.67, Z_FL, 2.30, "door"),
    op("y", 18.634, 10.77, 11.57, Z_FL, 2.30, "door"),
    op("y", 0.0, 8.96, 9.81, Z_FL, 2.51, "door"),
    op("y", 0.0, 10.52, 11.12, 1.03, 2.52, "window", 1, sw=0.22, st=0.30, sb=0.30),
    # the patio, glazed on its four sides (the west side through its 0.40 m wall from the west terrace)
    {**op("x", 5.331, 7.83, 11.08, Z_FL, 2.57, "glz", 2), "rev": 0.40, "rev_mat": "surround", "interior": False},
    {**op("x", 5.731, 7.83, 11.08, Z_FL, 2.57, "open"), "rev": 0.0},
    {**op("y", 11.417, 7.25, 9.94, Z_FL, 2.50, "glz", 3), "rev": 0.20},
    {**op("y", 7.127, 7.25, 9.94, Z_FL, 2.50, "glz", 3), "rev": 0.20},
    {**op("x", 10.251, 7.90, 10.65, Z_FL, 2.50, "glz", 2), "rev": 0.20},
    {**op("x", 12.45, 8.88, 10.12, 0.155, 3.0, "open"), "rev": 0.0},        # the portal's leaves (portal())
    # the entrance block: the doors onto the roof terrace
    op("y", 12.0, 10.86, 11.86, Z_TR + 0.03, 5.70, "door"),
    op("y", 6.79, 10.86, 11.86, Z_TR + 0.03, 5.70, "door"),
    # niches under the cornices (towers 3.68) and the band's parapets (3.62 / 3.68)
    *niches("y", 17.568, 0.35, 5.0, 3.68), *niches("x", 0.0, 11.75, 17.25, 3.68), *niches("y", 11.417, 0.35, 5.0, 3.68),
    *niches("y", 7.127, 0.35, 5.0, 3.68), *niches("x", 0.0, 1.40, 6.80, 3.68),
    *niches("y", 17.566, 12.6, 17.0, 3.68), *niches("x", 17.349, 11.75, 17.25, 3.68), *niches("y", 11.417, 12.6, 17.0, 3.68),
    *niches("y", 7.127, 12.6, 17.0, 3.68), *niches("x", 17.349, 1.40, 6.80, 3.68), *niches("y", 1.088, 12.6, 17.0, 3.68),
    *niches("y", 18.634, 5.6, 12.2, 3.62, 1.0), *niches("y", 0.0, 6.9, 12.2, 3.68, 0.80),
]
VC.OPENINGS = OPENINGS
GROOVES = (0.53, 1.41, 2.29, 3.17)
_insert = VC.insert


def insert(mb, P3, s0, s1, z0, z1, o, wall_mat):
    k = o["kind"]

    def rect(mat, a0, a1, b0, b1, dd):
        mb.poly(mat, [P3(a0, b0, dd), P3(a1, b0, dd), P3(a1, b1, dd), P3(a0, b1, dd)], [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])

    if k == "open":
        return
    if k == "door":                                        # a cedar door in its taupe frame, two panels, a handle
        d = 0.10
        rect("door_wood", s0, s1, z0, z1, d)
        for b0, b1 in ((z0 + 0.15, z0 + 0.95), (z0 + 1.10, z1 - 0.15)):
            D.pbox(mb, P3, s0 + 0.12, s1 - 0.12, b0, b1, d - 0.02, d, "door_wood")
        D.pbox(mb, P3, s1 - 0.14, s1 - 0.10, z0 + 0.98, z0 + 1.10, d - 0.06, d, "metal_dark")
        for a0, a1, b0, b1 in ((s0 - 0.15, s0, z0, z1 + 0.18), (s1, s1 + 0.15, z0, z1 + 0.18), (s0, s1, z1, z1 + 0.18)):
            D.pbox(mb, P3, a0, a1, b0, b1, -0.04, 0.02, "surround")
        return
    if k == "glz":                                         # glazed doors onto the patio: quartz aluminium, curtains
        d = o.get("rev", 0.20) / 2
        if o.get("interior", True):
            rect("interior", s0 - 0.3, s1 + 0.3, z0, z1 + 0.3, o.get("rev", 0.20) + 0.80)
        rect("glass", s0, s1, z0, z1, d)
        fr = 0.06
        for a0, a1, b0, b1 in ((s0, s1, z0, z0 + fr), (s0, s1, z1 - fr, z1), (s0, s0 + fr, z0, z1), (s1 - fr, s1, z0, z1),
                               (s0, s1, z0 + 2.05, z0 + 2.05 + fr)):
            D.pbox(mb, P3, a0, a1, b0, b1, d - 0.03, d + 0.03, "frame")
        for j in range(1, o["n"]):
            s = s0 + (s1 - s0) * j / o["n"]
            D.pbox(mb, P3, s - fr / 2, s + fr / 2, z0, z1, d - 0.03, d + 0.03, "frame")
        cw = (s1 - s0) * 0.16
        rect("curtain", s0 + fr, s0 + fr + cw, z0 + 0.03, z1 - 0.03, d + 0.20)
        rect("curtain", s1 - fr - cw, s1 - fr, z0 + 0.03, z1 - 0.03, d + 0.20)
        return
    _insert(mb, P3, s0, s1, z0, z1, o, wall_mat)
    if k == "baie":                                        # the stepped stone surround of the façade arrière
        for w, df in ((0.46, -0.03), (0.66, -0.05)):
            for a0, a1, b0, b1 in ((s0 - w, s0 - w + 0.20, z0, z1 + w), (s1 + w - 0.20, s1 + w, z0, z1 + w), (s0 - w, s1 + w, z1 + w - 0.20, z1 + w)):
                D.pbox(mb, P3, a0, a1, b0, b1, df, 0.02, "surround")


VC.insert = insert


def face(mb, p, q, z0, z1, bat=False, grooves=(), ext=0.0, mat="villa"):
    """A face p -> q (outward on its right) from z0 to z1; ext: run its ends into the towers' leaning faces."""
    shape = (lambda Lg: box(-ext, z0, Lg + ext, z1)) if not bat else \
        (lambda Lg: Polygon([(VC.tz(ZBOT), ZBOT), (Lg - VC.tz(ZBOT), ZBOT), (Lg - TB, ZB), (TB, ZB)]))
    return VC.cface(mb, p, q, shape, bat, grooves, (), mat)


def tower(mb, name):
    g, side, (d0, d1) = TOWERS[name]
    x0, y0, x1, y1 = g.bounds
    top = box(x0 + TB, y0 + TB, x1 - TB, y1 - TB)
    xd = x1 if side == "E" else x0
    for p, q in VC.edges(g):
        inner = abs(p[0] - q[0]) < 1e-6 and abs(p[0] - xd) < 1e-6        # the side against the band
        face(mb, p, q, ZBOT, ZB, True, () if inner else GROOVES)
    door = box(xd - 0.60, d0, xd + 0.60, d1)
    for z0, z1, pd, mat in ((4.06, 4.13, 0.12, "ledge"), (4.13, 4.22, 0.08, "band"), (4.22, 4.29, 0.12, "ledge"), (4.29, 4.44, 0.18, "ledge")):
        L.prism(mb, mat, top.buffer(pd, join_style=2).difference(top).difference(door), z0, z1, bottom=True)
    L.prism(mb, "villa", top.buffer(0.02, join_style=2).difference(top.buffer(-0.01, join_style=2)).difference(door), 4.44, 4.67)
    ring = top.buffer(-0.01, join_style=2).difference(top.buffer(-0.30, join_style=2)).difference(door)
    L.prism(mb, "villa", ring, Z_TR, Z_TT - COP)
    D.coping(mb, "villa", top.difference(top.buffer(-0.30, join_style=2)).difference(door), Z_TT, COP)
    L.prism(mb, "terrace", unary_union([top.buffer(-0.30, join_style=2), door.intersection(top)]), Z_TR - 0.01, Z_TR, sides=False)
    L.prism(mb, "villa", top.buffer(-0.01, join_style=2), Z_TR - 0.15, Z_TR - 0.02, bottom=True)


def band(mb):
    """The central band: its outer faces, the patio's, the parapets, the roof terrace."""
    zr = Z_TR - 0.02                                        # faces to the roof, the parapets' own faces over it
    face(mb, (12.45, 17.566), (12.45, 18.634), ZBOT, zr)                         # the north protrusion
    face(mb, (12.45, 18.634), (5.331, 18.634), ZBOT, zr)
    face(mb, (5.331, 18.634), (5.331, 17.568), ZBOT, zr)
    face(mb, (6.666, 1.088), (6.666, 0.0), ZBOT, zr)                             # the south protrusion
    face(mb, (6.666, 0.0), (12.45, 0.0), ZBOT, zr)
    face(mb, (12.45, 0.0), (12.45, 1.088), ZBOT, zr)
    face(mb, (5.331, 11.417), (5.331, 7.127), ZBOT, zr, ext=TB)                  # onto the west terrace, into the towers
    for p, q in (((5.731, 7.127), (5.731, 11.417)), ((5.731, 11.417), (10.251, 11.417)),
                 ((10.251, 11.417), (10.251, 7.127)), ((10.251, 7.127), (5.731, 7.127))):
        face(mb, p, q, -0.05, zr)                           # the patio, inside
    # the east face on the entrance terrace and the entrance block over it: one face to the block's roof
    zb = ENTRY_R
    face(mb, (12.45, 6.79), (12.45, 12.0), ZBOT, zb)
    face(mb, (12.45, 12.0), (10.251, 12.0), zr, zb)
    face(mb, (10.251, 12.0), (10.251, 6.79), zr, zb)
    face(mb, (10.251, 6.79), (12.45, 6.79), zr, zb)
    # roof terrace (run under the towers' leaning faces) and the parapets with their coping
    towers = unary_union([t[0] for t in TOWERS.values()])
    strips = [box(5.27, 1.088, 5.331, 7.127), box(5.27, 11.417, 5.331, 17.568), box(12.45, 1.088, 12.51, 7.127), box(12.45, 11.417, 12.51, 17.566)]
    roof = unary_union([BAND] + strips).difference(PATIO).difference(ENTRY)
    L.prism(mb, "terrace", roof, Z_TR - 0.02, Z_TR, sides=False)
    L.prism(mb, "villa", BAND.difference(PATIO).buffer(-0.01, join_style=2), Z_TR - 0.15, Z_TR - 0.02, bottom=True)
    ring = BAND.difference(PATIO).difference(BAND.difference(PATIO).buffer(-0.20, join_style=2))
    ring = ring.difference(towers.buffer(0.005)).difference(box(5.50, 0.85, 6.70, 1.40)).difference(ENTRY.buffer(0.005))
    caps = [box(5.331, 7.127 - TB, 5.531, 7.127), box(5.331, 11.417, 5.531, 11.417 + TB),        # up to the towers'
            box(5.331, 17.568 - TB, 5.531, 17.568), box(12.25, 17.566 - TB, 12.45, 17.566),      # leaning faces
            box(12.25, 1.088, 12.45, 1.088 + TB)]
    ring = unary_union([ring] + caps)
    north = box(0, 17.567, 20, 20)
    for g, zt_ in ((ring.difference(north), Z_BP), (ring.intersection(north), Z_BN)):
        L.prism(mb, "villa", g, Z_TR - 0.02, zt_ - COP, bottom=False)
        D.coping(mb, "villa", g, zt_, COP)
    # the entrance block: its roof, parapet with the coping (client 24-10: no horns on any house)
    L.prism(mb, "villa", ENTRY.buffer(-0.01, join_style=2), ENTRY_R - 0.15, ENTRY_R - 0.02, bottom=True)
    L.prism(mb, "terrace", ENTRY.buffer(-0.25, join_style=2), ENTRY_R - 0.01, ENTRY_R, sides=False)
    er = ENTRY.difference(ENTRY.buffer(-0.25, join_style=2))
    L.prism(mb, "villa", er, ENTRY_R - 0.01, Z_EW + 0.01, bottom=False)
    D.coping(mb, "villa", er, Z_ET, COP)
    L.prism(mb, "interior_floor", HOUSE.difference(PATIO).buffer(-0.02, join_style=2), ZBOT + 0.6, Z_FL - 0.01)


def portal(mb):
    """The studded portal on the entrance terrace (façade principale): the leaves (1.24 x 2.85) set back in a
    studded frame 1.85 x 3.79, a studded panel over it to +5.13; the threshold step."""
    x = 12.45
    P = lambda y, z, d=0.0: (x + 0.0 - d, y, z)           # d into the wall (westwards)
    rect = lambda mat, a0, a1, b0, b1, d: VC.tri_out(mb, mat, [P(a0, b0, d), P(a1, b0, d), P(a1, b1, d), P(a0, b1, d)], (1.0, 0.0, 0.0))
    y0, y1, zt = 8.88, 10.12, 3.0
    for (a0, a1, b0, b1) in ((y0, y1, zt, 3.79), (8.57, y0, 0.0, 3.79), (y1, 10.44, 0.0, 3.79)):        # the frame
        D.pbox(mb, P, a0, a1, b0, b1, -0.05, 0.0, "door_wood")
    for a0, a1 in ((y0, (y0 + y1) / 2 - 0.01), ((y0 + y1) / 2 + 0.01, y1)):
        D.pbox(mb, P, a0, a1, 0.155, zt, 0.16, 0.22, "door_wood")
        for i in range(4):
            for j in range(12):
                a = a0 + 0.08 + (a1 - a0 - 0.16) * i / 3
                b = 0.30 + (zt - 0.45) * j / 11
                D.pbox(mb, P, a - 0.013, a + 0.013, b - 0.013, b + 0.013, 0.145, 0.16, "metal_dark")
    for sx in (-1, 1):                                     # the reveals of the leaves' opening, ring pulls
        yy = y0 if sx < 0 else y1
        VC.tri_out(mb, "door_wood", [P(yy, 0.155, 0.0), P(yy, zt, 0.0), P(yy, zt, 0.16), P(yy, 0.155, 0.16)], (0.0, -sx, 0.0))
        D.pbox(mb, P, (y0 + y1) / 2 + sx * 0.14 - 0.02, (y0 + y1) / 2 + sx * 0.14 + 0.02, 1.05, 1.30, 0.10, 0.145, "metal_dark")
    VC.tri_out(mb, "door_wood", [P(y0, zt, 0.0), P(y1, zt, 0.0), P(y1, zt, 0.16), P(y0, zt, 0.16)], (0.0, 0.0, -1.0))
    a0, a1, b0, b1, n_i, n_j = 8.68, 10.32, 3.83, 5.13, 9, 6                # the studded panel over it
    D.pbox(mb, P, a0, a1, b0, b1, -0.05, 0.0, "door_wood")
    D.pbox(mb, P, a0 + 0.09, a1 - 0.09, b0 + 0.18, b1 - 0.18, -0.07, -0.05, "door_wood")
    for i in range(n_i):
        for j in range(n_j):
            a = a0 + 0.05 + (a1 - a0 - 0.10) * i / (n_i - 1)
            b = b0 + 0.05 + (b1 - b0 - 0.10) * j / (n_j - 1)
            if i in (0, n_i - 1) or j in (0, n_j - 1):
                D.pbox(mb, P, a - 0.014, a + 0.014, b - 0.014, b + 0.014, -0.075, -0.05, "metal_dark")
    for i in range(14):                                    # studs round the frame
        for a in (8.57 + 0.155, 10.44 - 0.155):
            b = 0.25 + 3.30 * i / 13
            D.pbox(mb, P, a - 0.014, a + 0.014, b - 0.014, b + 0.014, -0.075, -0.05, "metal_dark")
    mb.box("coping_beige", x, x + 0.40, 8.47, 10.54, Z_FL - 0.30, Z_FL + 0.155)       # the threshold step


def stair(mb):
    """The outside stair along Chambre I's south face: 21 risers up to the roof terrace, solid (the local
    technique under its landing, its door on the south), the outer wall as its parapet."""
    xa, xb, xe, yi, yo = STAIR
    n = 21
    r, go = Z_TR / n, (xb - xa) / (n - 1)
    for k in range(n):
        a, b = xa + k * go, (xa + (k + 1) * go if k < n - 1 else xe)
        z = r * (k + 1)
        L.prism(mb, "villa", box(a, yi, b, yo + TB), ZBOT, z - 0.03)
        L.prism(mb, "coping_beige", box(a - 0.02, yi, b, yo + VC.tz(z)), z - 0.03, z)
    # the outer wall (parapet): 0.90 over the nosings, level along the landing, the rounded coping
    prof = Polygon([(xa, ZBOT), (xe, ZBOT), (xe, Z_TR + 0.78), (xb, Z_TR + 0.78), (xa, 0.95)])
    face_pts = lambda a, b, w: (a, w, b)
    D.ext(mb, "villa", prof.difference(box(5.77, 0.05, 6.62, 2.51)), face_pts, 0.0, yi)
    cap = [(xa, 0.95), (xb, Z_TR + 0.78), (xe, Z_TR + 0.78)]
    for (a0, z0), (a1, z1) in zip(cap, cap[1:]):
        D.ext(mb, "coping_beige", Polygon([(a0, z0), (a1, z1), (a1, z1 + 0.05), (a0, z0 + 0.05)]), face_pts, -0.02, yi + 0.02)
    # the L.T.'s door in the outer wall under the landing (frame and leaf as the house's doors)
    Pd = lambda s, z, d=0.0: (s, 0.0 + d, z)
    insert(mb, Pd, 5.77, 6.62, 0.05, 2.51, {"kind": "door", "n": 1}, "villa")


def chimney(mb):
    """The coin cheminée's chimney (DETAIL 2): a shaft to +6.35, its rounded top to +6.73, the oculus."""
    x0, y0, x1, y1 = CHIMNEY.bounds
    L.prism(mb, "villa", CHIMNEY, Z_TR - 0.02, 6.35)
    r = (x1 - x0) / 2
    xc = (x0 + x1) / 2
    arc = Polygon([(x0, 6.35)] + [(xc - r * math.cos(math.pi * k / 16), 6.35 + r * math.sin(math.pi * k / 16)) for k in range(17)] + [(x1, 6.35)])
    D.ext(mb, "villa", arc, lambda a, b, w: (a, w, b), y0, y1)
    oc = Point(xc, 6.32).buffer(0.13, 16)
    for yy, sg in ((y0 - 0.005, -1), (y1 + 0.005, 1)):
        for t in L.tri_poly(oc):
            VC.tri_out(mb, "metal_dark", [(a, yy, b) for a, b in t], (0.0, sg, 0.0))
    L.prism(mb, "ledge", CHIMNEY.buffer(0.04, join_style=2), 6.30 - 0.6, 6.30 - 0.52, bottom=True)


def grounds(mb, plants):
    # the pool: coping, jade tiles, Roman steps at its south end; the deck along the house
    L.prism(mb, "coping", POOL.difference(WATER), -0.30, Z_FL - 0.04)
    L.prism(mb, "tile_jade", WATER, -POOL_DEPTH - 0.05, -POOL_DEPTH + 0.15, sides=False)
    L.prism(mb, "tile_jade", WATER.buffer(0.01, join_style=2).difference(WATER.buffer(-0.01, join_style=2)), -POOL_DEPTH + 0.15, Z_FL - 0.06)
    L.prism(mb, "pool_water", WATER.buffer(-0.01, join_style=2), Z_FL - 0.19, Z_FL - 0.17, sides=False)
    wx0, wy0, wx1, wy1 = WATER.bounds
    for k in range(3):
        L.prism(mb, "tile_jade", box(wx0, wy0, wx1, wy0 + 0.40 * (3 - k)), -POOL_DEPTH + 0.15, -0.20 - 0.35 * k)
    for g in (DECK, TER_W, TER_E):
        L.prism(mb, "terrace", g, -0.40, Z_FL - 0.005)
    # the patio's garden: a planted bed round its date palm, a paved border
    pin = PATIO.buffer(-0.01, join_style=2)
    bed = PATIO.buffer(-0.60, join_style=2)
    L.prism(mb, "deck_stone", pin.difference(bed), -0.40, Z_FL - 0.005)
    L.prism(mb, "coping_beige", bed.difference(bed.buffer(-0.10, join_style=2)), -0.40, Z_FL + 0.10)
    L.prism(mb, "soil", bed.buffer(-0.10, join_style=2), -0.40, Z_FL - 0.02, sides=False)
    pc = PATIO.centroid
    plants.append(("date", pc.x + 0.6, pc.y + 0.4, Z_FL - 0.02, 0.75))
    for dx, dy in ((-1.3, -1.0), (1.4, -1.1), (-1.4, 1.1), (1.2, 1.2), (0.0, -1.3)):
        plants.append(("shrub", pc.x + dx, pc.y + dy, Z_FL - 0.02, 0.80))
    # the entrance terrace's benches along the towers, the planters along the east fronts
    for g in (box(12.45, 7.127, 17.349, 7.80), box(12.45, 10.80, 17.349, 11.417)):
        L.prism(mb, "villa", g, Z_FL, Z_FL + 0.40)
        L.prism(mb, "coping_beige", g.buffer(0.02, join_style=2).intersection(TER_E.buffer(0.02)), Z_FL + 0.40, Z_FL + 0.46)
    for g in PLANTERS:
        L.prism(mb, "villa", g.difference(g.buffer(-0.10, join_style=2)), -0.30, 0.55)
        L.prism(mb, "coping_beige", g.difference(g.buffer(-0.12, join_style=2)), 0.55, 0.60)
        L.prism(mb, "soil", g.buffer(-0.10, join_style=2), -0.30, 0.48, sides=False)
        x0, y0, x1, y1 = g.buffer(-0.45, join_style=2).bounds
        n = max(1, int((y1 - y0) / 1.3))
        for k in range(n + 1):
            plants.append(("shrub", (x0 + x1) / 2, y0 + (y1 - y0) * k / max(1, n), 0.48, 0.85))
    # the west terrace's parasol and table, loungers by the pool, parasols at its corners
    L.prism(mb, "metal_dark", Point(2.8, 9.27).buffer(0.035, 6), Z_FL, Z_FL + 2.45)
    rim = [(2.8 + 1.6 * math.cos(2 * math.pi * k / 8), 9.27 + 1.6 * math.sin(2 * math.pi * k / 8), Z_FL + 2.25) for k in range(8)]
    for k in range(8):
        mb.poly("canvas", [rim[k], rim[(k + 1) % 8], (2.8, 9.27, Z_FL + 2.70)])
        mb.poly("canvas", [rim[(k + 1) % 8], rim[k], (2.8, 9.27, Z_FL + 2.68)])
    L.prism(mb, "timber", Point(2.8, 9.27).buffer(0.55, 16), Z_FL + 0.70, Z_FL + 0.75)
    L.prism(mb, "metal_dark", Point(2.8, 9.27).buffer(0.06, 6), Z_FL, Z_FL + 0.70)
    for a in range(4):
        cx, cy = 2.8 + 0.95 * math.cos(math.pi / 2 * a), 9.27 + 0.95 * math.sin(math.pi / 2 * a)
        L.prism(mb, "lounger_white", box(cx - 0.22, cy - 0.22, cx + 0.22, cy + 0.22), Z_FL + 0.40, Z_FL + 0.45)
        for dx, dy in ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)):
            L.prism(mb, "lounger_white", Point(cx + dx, cy + dy).buffer(0.02, 4), Z_FL, Z_FL + 0.40)
    for yc in (8.2, 10.4):
        g = box(-1.85, yc - 0.35, -0.15, yc + 0.35)
        L.prism(mb, "lounger_white", g, Z_FL + 0.06, Z_FL + 0.30)
        L.prism(mb, "cushion", g.buffer(-0.04), Z_FL + 0.30, Z_FL + 0.36)
        L.prism(mb, "cushion", box(-0.53, yc - 0.33, -0.17, yc + 0.33), Z_FL + 0.36, Z_FL + 0.66)


def build(M, col, name="SRC_T3_VILLA_A"):
    mb = C.MeshBuilder()
    plants = []
    for k in TOWERS:
        tower(mb, k)
    band(mb)
    portal(mb)
    stair(mb)
    chimney(mb)
    grounds(mb, plants)
    obs = mb.build("VILLA_A", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob, plants
