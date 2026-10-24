"""
14_villa_c — villa type C, from PLAN_VILLA_TYPE_C.dwg (permis: REZ DE CHAUSSEE, TERRASSE, façades principale,
arrière, gauche and droite, coupes A-A and B-B), dressed like the villas of Tranche 1 and the villa type B
(client 22-10: "nfs style dima").

Plan frame of the drawing: x' = DWG x - 47600, y' = DWG y - 290000 (metres); the model is built there and
shifted by (-19.156, -38.035) at the end, so its local frame runs x 0-16.53 across (the outer face of the
outside stair at x 0) and y 0 at the back of the pool deck to 18.0 in front of the porch. z = 0 is the
natural ground (T.N), the floor is +0.20 as the drawing's levels.

A single-storey kasbah house (from the plans and façades):
  four battered towers, the rooms of the two wings (Chambre III and the salon marocain on the west,
    Chambres I and II on the east): walls leaning in 0.255 m over their 4.31 m (the façades' slanted
    edges), the villas' cornice (grey ledge / ochre band / grey ledge), a crown, parapet +4.80 with horns;
    roofs at +3.70, with a door in each parapet onto the terrace over the bathroom between the two;
  the bathrooms between the towers, lower: plain walls, roof terrace +3.70 (parapet +4.60 on the east,
    the outside stair arrives over it on the west);
  the centre (kitchen, entrance hall, W.C., salon / S.A.M.): plain walls to +5.50 with the rounded coping,
    roof +4.50, four steps up to it from each bathroom terrace;
  the portal tower over the entrance hall, +6.70 with horns, roof +5.70: a taupe alfiz round a pointed
    horseshoe arch, the studded wooden door and its transom, a mashrabiya tympanum.
Rows of square niches under the cornices and parapets, horizontal grooves every metre (z 0.56 - 3.56, and
4.51 / 5.06 on the centre), taupe stone surrounds (the wide panels of the small windows as drawn), quartz
aluminium, curtains, the salon's 4-leaf glazing set back with the lit salon behind. The outside stair up to
the west terrace (18 treads of 0.27 m and a landing, solid parapet). Pool 7.50 x 4.00 m over its coping: the
main basin 4.50 x 3.00 (-1.40) with Roman steps by the house and the 1.70 x 3.00 spa basin beside it.
"""
import importlib.util
import math
import os

from shapely.affinity import translate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t3_dpx_c", os.path.join(HERE, "02_duplex.py"))
D = importlib.util.module_from_spec(_spec)
D.__dict__["L"] = L
_spec.loader.exec_module(D)                  # the villa machinery of Tranche 1 (openings, baie, coping, horns)

XO, YO = 19.156, 38.035                      # plan frame -> local frame
ZBOT, Z_FL = -1.00, 0.20
ZB, TB = 4.31, 0.255                         # battered walls: top of the lean, inset at the top
Z_TR, Z_TT, Z_SP = 3.70, 4.80, 4.60          # wing roofs, tower parapets, east bathroom parapet
Z_CR, Z_CT = 4.50, 5.50                      # centre roof, centre parapet
Z_PR, Z_PW, Z_PT = 5.70, 6.01, 6.67          # portal roof, top of its walls, top of its parapet
REV, COP = D.REV, 0.06


def tz(z):
    return TB * z / ZB


# ---- volumes (plan frame) --------------------------------------------------------------------------------
TOWERS = {   # base rectangle, the side of the bathroom terrace (door in the parapet) and the door's x
    "TW1": (box(20.30, 49.75, 24.768, 53.173), "S", (22.00, 23.00)),     # Chambre III
    "TW2": (box(20.30, 43.535, 25.003, 48.45), "N", (22.00, 23.00)),     # salon marocain
    "TE1": (box(30.878, 48.15, 35.684, 52.105), "S", (32.50, 33.50)),    # Chambre I
    "TE2": (box(30.631, 43.535, 35.684, 46.80), "N", (32.50, 33.50)),    # Chambre II
}
SDB_W = (20.30, 48.45, 24.768, 49.75)
SDB_E = (30.878, 46.80, 35.684, 48.15)
# the centre, run into the towers to the top of their lean (their battered faces close on it)
CENX = Polygon([(24.748, 44.923), (30.886, 44.923), (30.886, 46.80), (31.133, 46.80), (31.133, 54.14),
                (24.513, 54.14), (24.513, 48.45), (24.748, 48.45)])
PT = box(26.275, 49.62, 29.463, 55.688)
OUTLINE = Polygon([(20.30, 43.535), (25.003, 43.535), (25.003, 44.923), (30.631, 44.923), (30.631, 43.535),
                   (35.684, 43.535), (35.684, 52.105), (31.133, 52.105), (31.133, 54.14), (29.463, 54.14),
                   (29.463, 55.688), (26.275, 55.688), (26.275, 54.14), (24.513, 54.14), (24.513, 53.173),
                   (20.30, 53.173)])
STEPS_W = (48.50, 49.70)                     # the four steps from the bathroom terraces up to the centre roof
STEPS_E = (46.82, 48.12)
STAIR = (19.156, 20.30, 43.61, 48.47, 49.92)  # outside stair: x0 x1, foot, top of the flight, end of the landing
POOL = box(24.123, 38.535, 31.624, 42.535)   # over the coping
BASIN = box(24.623, 39.035, 29.124, 42.035)
SPA = box(29.424, 39.035, 31.124, 42.035)
POOL_DEPTH, SPA_DEPTH = 1.40, 0.80
TER_REAR = box(25.003, 43.535, 30.631, 44.923)
TER_NW = box(20.30, 53.173, 24.513, 54.14)
TER_NE = box(31.133, 52.105, 35.684, 54.14)
PATH_W = box(19.156, 38.035, 20.30, 43.61)   # the paved strip along the west side to the stair
PLOT_W, PLOT_D = 35.684 - XO, 56.05 - YO     # local plot box 16.53 x 18.02 (the drawing's lot, porch step)


def loc(g):
    return translate(g, -XO, -YO)


FOOT = loc(unary_union([OUTLINE, box(STAIR[0], STAIR[2], STAIR[1], STAIR[4])]))   # kept clear of trees
HARD = loc(unary_union([OUTLINE, POOL, TER_REAR, TER_NW, TER_NE, PATH_W, box(24.122, 38.035, 31.624, 38.535),
                        box(STAIR[0], STAIR[2], STAIR[1], STAIR[4]), box(27.00, 55.688, 28.74, 56.05)]))
HOUSE = loc(OUTLINE)
HOUSE_C = HOUSE.centroid.coords[0]
PORTAL_X = 0.5 * (PT.bounds[0] + PT.bounds[2]) - XO   # the portal's axis, local x
PORCH = loc(box(27.00, 55.688, 28.74, 56.05))


def op(axis, c, u0, u1, z0, z1, kind, n=1, **kw):
    d = D.op(axis, c, u0, u1, z0, z1, kind, n)
    d.update(kw)
    return d


def niches(axis, c, us, z0, w=0.20):
    return [op(axis, c, u - w / 2, u + w / 2, z0, z0 + w, "niche") for u in us]


S_SMALL = dict(sw=0.30, st=0.30, sb=0.30)    # the wide stone panels of the small windows
OPENINGS = [
    # towers: windows (positions from the RDC plan, heights from the façades)
    op("y", 53.173, 21.452, 23.853, 1.00, 2.79, "window", 2),                 # Chambre III
    op("y", 52.105, 31.930, 34.392, 1.00, 2.79, "window", 2),                 # Chambre I
    op("x", 35.684, 49.218, 51.018, 0.85, 2.60, "window", 2, sw=0.25, st=0.24),   # Chambre I, east
    op("x", 35.684, 44.335, 46.135, 0.85, 2.60, "window", 2, sw=0.25, st=0.24),   # Chambre II, east
    op("y", 43.535, 21.152, 24.153, Z_FL, 2.97, "slider", 2),                # salon marocain onto the garden
    op("y", 43.535, 31.630, 34.692, Z_FL, 2.97, "slider", 2),                # Chambre II onto the garden
    op("x", 20.30, 45.586, 46.420, 2.05, 2.75, "window"),                    # salon marocain, over the stair
    # bathrooms, kitchen, W.C.
    op("x", 20.30, 48.864, 49.365, 1.25, 2.75, "window", **S_SMALL),
    op("x", 35.684, 47.225, 47.725, 1.25, 2.75, "window", **S_SMALL),
    op("y", 54.14, 25.212, 25.808, 1.03, 2.52, "window", **S_SMALL),
    op("y", 54.14, 29.939, 30.535, 1.03, 2.52, "window", **S_SMALL),
    # salon onto the terrace and the pool: 4 leaves set back in a stone reveal, the lit salon behind
    {**op("y", 44.923, 25.421, 30.224, Z_FL, 3.41, "baie", 4), "rev": 0.36, "rev_mat": "surround"},
    # niches: towers under the cornice (z 3.70), centre under its coping (north / south 4.78, sides 4.98),
    # portal tower 5.68
    *niches("y", 53.173, (21.02, 21.64, 22.26, 22.88, 23.50, 24.12), 3.70),
    *niches("y", 52.105, (31.75, 32.37, 32.99, 33.61, 34.23, 34.85), 3.70),
    *niches("x", 20.30, (50.60, 51.50, 52.40), 3.70),
    *niches("x", 20.30, (44.08, 44.98, 45.88), 3.70),
    *niches("x", 35.684, (43.99, 44.89, 45.79), 3.70),
    *niches("x", 35.684, (49.12, 50.32, 51.22), 3.70),
    *niches("y", 44.923, (25.835, 26.735, 27.635, 28.535, 29.435, 30.335), 4.78),
    *niches("y", 54.14, (24.85, 25.43, 26.01, 29.72, 30.30, 30.88), 4.78),
    *niches("x", 24.513, (50.87, 51.77, 53.57), 4.98),
    *niches("x", 24.748, (45.47, 46.37, 47.27), 4.98),
    *niches("x", 31.133, (49.25, 50.49, 52.29, 53.19), 4.98),
    *niches("x", 30.886, (45.26, 46.62), 4.98),
    *niches("y", 55.688, (26.97, 27.87, 28.77), 5.68),
    *niches("y", 49.62, (26.97, 27.87, 28.77), 5.68),
    *niches("x", 26.275, (50.49, 51.39, 52.29, 53.19, 54.09, 54.99), 5.68),
    *niches("x", 29.463, (50.49, 51.39, 52.29, 53.19, 54.09, 54.99), 5.68),
]
GROOVES = (0.56, 1.56, 2.56, 3.56)
GROOVES_C = GROOVES + (4.51, 5.06)


# ---- faces ----------------------------------------------------------------------------------------------
def frame_of(p, q, bat):
    """Wall face p->q (CCW outline: outward normal on the right). P3(s, z, d, zm): s along, d into the wall
    from the face; a battered face leans in by tz(z). Frames and glass (d >= 0.05) stand plumb, at the lean
    of the opening's mid-height zm, the stone round them follows the wall."""
    (ax, ay), (bx, by) = p, q
    Lg = math.dist(p, q)
    ux, uy = (bx - ax) / Lg, (by - ay) / Lg
    nx, ny = uy, -ux
    lean = tz if bat else (lambda z: 0.0)

    def P3(s, z, d=0.0, zm=None):
        off = d + (lean(zm) if (zm is not None and d >= 0.05) else lean(z))
        return (ax + ux * s - nx * off, ay + uy * s - ny * off, z)
    axis = "y" if abs(uy) < 1e-6 else "x"
    org, du, cst = (ax, ux, ay) if axis == "y" else (ay, uy, ax)
    return Lg, P3, axis, org, du, cst, (ux, uy), (nx, ny)


def openings_on(axis, org, du, cst, Lg, z0, z1):
    out = []
    for o in OPENINGS:
        if o["axis"] != axis or abs(o["c"] - cst) > 0.03 or o["z1"] <= z0 or o["z0"] >= z1:
            continue
        s0, s1 = sorted(((o["u0"] - org) / du, (o["u1"] - org) / du))
        if s0 < -0.3 or s1 > Lg + 0.3:
            continue
        out.append((s0, s1, o["z0"], o["z1"], o))
    return out


def surround_box(s0, s1, h0, h1, o):
    k = o["kind"]
    if k == "niche":
        return box(s0, h0, s1, h1)
    if k == "baie":
        return box(s0 - 0.27, h0, s1 + 0.27, h1 + 0.27)
    if k == "slider":
        return box(s0 - o.get("sw", 0.18), h0, s1 + o.get("sw", 0.18), h1 + o.get("st", 0.20))
    if k == "portal":
        return box(s0, h0, s1, h1)
    return box(s0 - o.get("sw", 0.20), h0 - o.get("sb", 0.20), s1 + o.get("sw", 0.20), h1 + o.get("st", 0.23))


def cface(mb, p, q, shape, bat, grooves=(), cut=(), mat="villa"):
    """A wall face: shape(Lg) -> its outline in (s, z); its openings (OPENINGS on its plane), grooves (5 cm
    bands standing 15 mm proud), cut: (s0, z0, s1, z1) boxes taken out (doors in the parapets, notches)."""
    Lg, P3, axis, org, du, cst, U, N = frame_of(p, q, bat)
    face = shape(Lg)
    for c in cut:
        face = face.difference(box(*c))
    z0, z1 = face.bounds[1], face.bounds[3]
    holes = [h for h in openings_on(axis, org, du, cst, Lg, z0, z1) if face.buffer(1e-6).contains(box(h[0], h[2], h[1], h[3]))]
    for s0, s1, h0, h1, o in holes:
        face = face.difference(box(s0, h0, s1, h1))
    for t in L.tri_poly(face) if face.geom_type == "Polygon" else [t for g in face.geoms for t in L.tri_poly(g)]:
        mb.poly(mat, [P3(s, z) for s, z in t], [(s, z) for s, z in t])
    for s0, s1, h0, h1, o in holes:
        zm = 0.5 * (h0 + h1)
        Po = lambda s, z, d=0.0, zm=zm: P3(s, z, d, zm)
        dep = o.get("rev", 0.10 if o["kind"] == "niche" else REV)
        for (sa, za), (sb, zb) in [((s0, h1), (s0, h0)), ((s1, h0), (s1, h1)), ((s1, h1), (s0, h1)), ((s0, h0), (s1, h0))]:
            mb.poly(o.get("rev_mat", mat), [Po(sa, za), Po(sb, zb), Po(sb, zb, dep), Po(sa, za, dep)])
        insert(mb, Po, s0, s1, h0, h1, o, mat)
    if grooves:
        keep = face.buffer(0)
        for s0, s1, h0, h1, o in holes:
            keep = keep.difference(surround_box(s0, s1, h0, h1, o).buffer(0.02, join_style=2))
        bands = unary_union([box(-1.0, g, Lg + 1.0, g + 0.05) for g in grooves]).intersection(keep)
        D.ext(mb, mat, bands, lambda a, b, w: P3(a, b, w), -0.015, 0.0)
    return Lg, P3, U, N


def insert(mb, P3, s0, s1, z0, z1, o, wall_mat):
    """What fills an opening (02_duplex's, with the drawing's surround widths): niche back, the salon's baie,
    or frame + leaves + glass + curtains + interior + taupe stone surround."""
    kind = o["kind"]

    def rect(mat, a0, a1, b0, b1, dd):
        mb.poly(mat, [P3(a0, b0, dd), P3(a1, b0, dd), P3(a1, b1, dd), P3(a0, b1, dd)], [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])

    if kind == "niche":
        rect(wall_mat, s0, s1, z0, z1, 0.10)
        return
    if kind == "baie":
        D.baie(mb, P3, s0, s1, z0, z1, o["n"], rect)
        return
    d, fr = 0.10, 0.06
    frame = lambda a0, a1, b0, b1: D.pbox(mb, P3, a0, a1, b0, b1, d - 0.03, d + 0.03, "frame")
    rect("interior", s0 - 0.3, s1 + 0.3, z0 - 0.3, z1 + 0.3, 0.75)
    rect("glass", s0, s1, z0, z1, d)
    frame(s0, s1, z0, z0 + fr)
    frame(s0, s1, z1 - fr, z1)
    frame(s0, s0 + fr, z0 + fr, z1 - fr)
    frame(s1 - fr, s1, z0 + fr, z1 - fr)
    for k in range(1, o["n"]):
        s = s0 + (s1 - s0) * k / o["n"]
        frame(s - fr / 2, s + fr / 2, z0 + fr, z1 - fr)
    cw = (s1 - s0) * (0.17 if kind == "slider" else 0.26)
    rect("curtain", s0 + fr, s0 + fr + cw, z0 + 0.03, z1 - 0.03, 0.30)
    rect("curtain", s1 - fr - cw, s1 - fr, z0 + 0.03, z1 - 0.03, 0.30)
    if kind == "slider":
        w_, top, sb = o.get("sw", 0.18), o.get("st", 0.20), 0.0
    else:
        w_, top, sb = o.get("sw", 0.20), o.get("st", 0.23), o.get("sb", 0.20)
    D.pbox(mb, P3, s0 - w_, s0, z0 - sb, z1 + top, -0.04, 0.02, "surround")
    D.pbox(mb, P3, s1, s1 + w_, z0 - sb, z1 + top, -0.04, 0.02, "surround")
    D.pbox(mb, P3, s0, s1, z1, z1 + top, -0.04, 0.02, "surround")
    if sb > 0:
        D.pbox(mb, P3, s0, s1, z0 - sb, z0, -0.04, 0.02, "surround")


def edges(poly):
    c = list(poly.exterior.coords)
    if not poly.exterior.is_ccw:
        c = c[::-1]
    return list(zip(c, c[1:]))


def tri_out(mb, mat, pts, want):
    """A planar polygon turned so its normal points along want."""
    a, b, c = pts[0], pts[1], pts[2]
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    if n[0] * want[0] + n[1] * want[1] + n[2] * want[2] < 0:
        pts = pts[::-1]
    mb.poly(mat, pts)


# ---- the pieces -----------------------------------------------------------------------------------------
def tower(mb, name):
    g, side, (gx0, gx1) = TOWERS[name]
    x0, y0, x1, y1 = g.bounds
    top = box(x0 + TB, y0 + TB, x1 - TB, y1 - TB)
    gy = y0 if side == "S" else y1                       # the parapet's door onto the bathroom terrace
    for p, q in edges(g):
        shape = lambda Lg: Polygon([(tz(ZBOT), ZBOT), (Lg - tz(ZBOT), ZBOT), (Lg - TB, ZB), (TB, ZB)])
        cut = []
        if abs(p[1] - q[1]) < 1e-6 and abs(p[1] - gy) < 1e-6:
            s0, s1 = sorted(((gx0 - p[0]) / (q[0] - p[0]) * math.dist(p, q), (gx1 - p[0]) / (q[0] - p[0]) * math.dist(p, q)))
            cut = [(s0, Z_TR, s1, ZB + 1.0)]
        cface(mb, p, q, shape, True, GROOVES, cut)
    door = box(gx0, gy - 0.6, gx1, gy + 0.6)
    # cornice (grey ledge / ochre band / grey ledge), crown, parapet with the rounded coping, horns
    for z0, z1, pd, mat in [(4.31, 4.38, 0.075, "ledge"), (4.38, 4.47, 0.02, "band"), (4.47, 4.54, 0.075, "ledge")]:
        L.prism(mb, mat, top.buffer(pd, join_style=2).difference(top).difference(door), z0, z1, bottom=True)
    L.prism(mb, "villa", top.buffer(0.13, join_style=2).difference(top.buffer(-0.01, join_style=2)).difference(door), 4.54, 4.67, bottom=True)
    L.prism(mb, "villa", top.buffer(0.10, join_style=2).difference(top.buffer(-0.01, join_style=2)).difference(door), 4.67, 4.71)
    ring_in = top.buffer(-0.01, join_style=2).difference(top.buffer(-0.30, join_style=2)).difference(door)
    L.prism(mb, "villa", ring_in, Z_TR, Z_TT - COP)
    D.coping(mb, "villa", top.difference(top.buffer(-0.30, join_style=2)).difference(door), Z_TT, COP)
    L.prism(mb, "terrace", unary_union([top.buffer(-0.30, join_style=2), door.intersection(top)]), Z_TR - 0.01, Z_TR, sides=False)
    horns(mb, top, Z_TT, skip_side="E" if name.startswith("TW") else "W")


def horns(mb, top, ztop, skip_side=None):
    """Horned corners (as Tranche 1's stair cages): a horn along each side at every corner."""
    us = [0.80 - 0.62 * k / 12 for k in range(13)]
    prof = Polygon([(0.0, ztop - 0.40), (0.80, ztop - 0.40)] + [(u, ztop + 0.43 * ((0.80 - u) / 0.62) ** 1.6) for u in us]
                   + [(0.07, ztop + 0.41), (0.0, ztop + 0.34)])
    prof_b = prof.intersection(box(0.20, -50.0, 2.0, 50.0))
    cx0, cy0, cx1, cy1 = top.bounds
    for xc, sx in ((cx0, 1), (cx1, -1)):
        for yc, sy in ((cy0, 1), (cy1, -1)):
            D.horn(mb, prof, lambda a, b, w, xc=xc, sx=sx, yc=yc, sy=sy: (xc + sx * a, yc + sy * w, b))
            side = "W" if sx == 1 else "E"
            if side != skip_side:
                D.horn(mb, prof_b, lambda a, b, w, xc=xc, sx=sx, yc=yc, sy=sy: (xc + sx * w, yc + sy * a, b))


def sdb_face(mb, p, q, ztop):
    """The bathroom's outer wall between two towers: plumb, its ends running out to the towers' leaning faces,
    closed against them."""
    def shape(Lg):
        za = min(ztop, ZB)
        pts = [(tz(ZBOT) * -1.0, ZBOT), (Lg + tz(ZBOT), ZBOT), (Lg + tz(za), za)]
        if ztop > ZB:
            pts += [(Lg + TB, ztop)]
        pts += [(-TB if ztop > ZB else -tz(za), ztop)]
        if ztop > ZB:
            pts += [(-TB, ZB)]
        return Polygon(pts)
    Lg, P3, U, N = cface(mb, p, q, shape, False, GROOVES)
    za = min(ztop, ZB)
    for s_sign, s_base, want in ((-1.0, 0.0, (-U[0], -U[1], 0.0)), (1.0, Lg, (U[0], U[1], 0.0))):
        s_top = s_base + s_sign * tz(za)
        tri_out(mb, "villa", [P3(s_base, 0.0), P3(s_top, za), P3(s_top, za, tz(za))], want)
        if ztop > ZB:
            s_t = s_base + s_sign * TB
            tri_out(mb, "villa", [P3(s_t, ZB), P3(s_t, ztop), P3(s_t, ztop, TB), P3(s_t, ZB, TB)], want)


def centre(mb):
    nw = (24.513, STEPS_W[0], 24.513, STEPS_W[1])
    ne = (31.133, STEPS_E[0], 31.133, STEPS_E[1])
    for p, q in edges(CENX):
        Lg = math.dist(p, q)
        cut = []
        for (cx, ya, _, yb) in (nw, ne):
            if abs(p[0] - q[0]) < 1e-6 and abs(p[0] - cx) < 1e-6:
                s0, s1 = sorted(((ya - p[1]) / (q[1] - p[1]) * Lg, (yb - p[1]) / (q[1] - p[1]) * Lg))
                cut.append((s0, Z_CR, s1, Z_CT + 1.0))
        cface(mb, p, q, lambda Lg: box(0.0, ZBOT, Lg, Z_CT - 0.14), False, GROOVES_C, cut)
    notch = unary_union([box(24.513 - 0.05, STEPS_W[0], 24.513 + 0.35, STEPS_W[1]), box(31.133 - 0.35, STEPS_E[0], 31.133 + 0.05, STEPS_E[1])])
    ring = CENX.difference(CENX.buffer(-0.30, join_style=2))
    L.prism(mb, "villa", CENX.buffer(-0.01, join_style=2).difference(CENX.buffer(-0.30, join_style=2)).difference(PT).difference(notch), Z_CR, Z_CT - 0.14)
    D.coping(mb, "villa", ring.difference(PT).difference(notch), Z_CT, 0.14)
    L.prism(mb, "terrace", unary_union([CENX.buffer(-0.30, join_style=2), notch.intersection(ring)]).difference(PT), Z_CR - 0.01, Z_CR, sides=False)
    # four steps (three treads and the wall's top) up from each bathroom terrace
    for k in range(3):
        mb.box("terrace", 24.513 - 0.27 * (3 - k), 24.513, STEPS_W[0], STEPS_W[1], Z_TR - 0.01, Z_TR + 0.20 * (k + 1))
        mb.box("terrace", 31.133, 31.133 + 0.27 * (3 - k), STEPS_E[0], STEPS_E[1], Z_TR - 0.01, Z_TR + 0.20 * (k + 1))


def bathrooms(mb):
    x0, y0, x1, y1 = SDB_W
    sdb_face(mb, (x0, y1), (x0, y0), Z_TR)                          # west: the stair lands over it
    L.prism(mb, "terrace", box(x0, y0 - tz(Z_TR), 24.513, y1 + tz(Z_TR)), Z_TR - 0.01, Z_TR, sides=False)
    x0, y0, x1, y1 = SDB_E
    sdb_face(mb, (x1, y0), (x1, y1), Z_SP - 0.12)
    xi = x1 - 0.26
    tri_out(mb, "villa", [(xi, y0 - TB, Z_TR), (xi, y1 + TB, Z_TR), (xi, y1 + TB, Z_SP - 0.12), (xi, y0 - TB, Z_SP - 0.12)], (-1.0, 0.0, 0.0))
    D.coping(mb, "villa", box(xi, y0 - TB, x1, y1 + TB), Z_SP, 0.12)
    L.prism(mb, "terrace", box(31.133, y0 - tz(Z_TR), xi, y1 + tz(Z_TR)), Z_TR - 0.01, Z_TR, sides=False)


def portal(mb):
    """The portal tower: plumb walls to +6.01, cornice, crown, parapet +6.67 with horns; on its front the
    alfiz round the pointed horseshoe arch, the studded door and transom, the mashrabiya tympanum."""
    cx = 0.5 * (PT.bounds[0] + PT.bounds[2])
    for p, q in edges(PT):
        if abs(p[1] - q[1]) < 1e-6 and abs(p[1] - PT.bounds[3]) < 1e-6:
            front(mb, p, q, cx)
        else:
            cface(mb, p, q, lambda Lg: box(0.0, ZBOT, Lg, Z_PW), False)
    for z0, z1, pd, mat in [(6.01, 6.08, 0.09, "ledge"), (6.08, 6.17, 0.05, "band"), (6.17, 6.25, 0.10, "ledge"), (6.25, 6.40, 0.15, "ledge")]:
        L.prism(mb, mat, PT.buffer(pd, join_style=2).difference(PT), z0, z1, bottom=True)
    L.prism(mb, "villa", PT.buffer(-0.01, join_style=2).difference(PT.buffer(-0.30, join_style=2)), Z_PR, Z_PT - COP)
    D.coping(mb, "villa", PT.difference(PT.buffer(-0.30, join_style=2)), Z_PT, COP)
    L.prism(mb, "terrace", PT.buffer(-0.30, join_style=2), Z_PR - 0.01, Z_PR, sides=False)
    hatch = box(28.70, 51.92, 29.10, 52.72)                       # roof hatch (plan TERRASSE)
    L.prism(mb, "villa", hatch.buffer(0.10, join_style=2).difference(hatch), Z_PR, Z_PR + 0.30)
    L.prism(mb, "metal_dark", hatch.buffer(0.12, join_style=2), Z_PR + 0.30, Z_PR + 0.34, bottom=True)
    horns(mb, PT, Z_PT)


def arch_poly(cx, w, zs, k=0.25, n=14):
    """Pointed horseshoe arch over jambs w wide: two arcs centred k inside the far jamb, turning in 15 deg
    under their springing."""
    R = w / 2 + k
    a1 = math.degrees(math.acos(k / R))
    left = [(cx + k - R * math.cos(math.radians(a)), zs + R * math.sin(math.radians(a))) for a in [-15.0 + (15.0 + a1) * i / n for i in range(n + 1)]]
    right = [(2 * cx - x, z) for x, z in left[::-1]]
    jw = cx - left[0][0]
    return Polygon([(cx - jw, -0.5)] + left + right[1:] + [(cx + jw, -0.5)])


def front(mb, p, q, cx):
    Lg, P3, axis, org, du, cst, U, N = frame_of(p, q, False)
    sc = (cx - org) / du                                   # tower centre in s
    alf = box(sc - 1.095, -0.5, sc + 1.095, 5.55)          # alfiz (façade principale: 2.19 x 5.55)
    arch = arch_poly(sc, 1.40, 4.35)
    face = box(0.0, ZBOT, Lg, Z_PW)
    holes = openings_on(axis, org, du, cst, Lg, ZBOT, Z_PW)
    for s0, s1, h0, h1, o in holes:
        face = face.difference(box(s0, h0, s1, h1))
    face = face.difference(alf.intersection(box(-1, 0.0, Lg + 1, 6)))
    for t in L.tri_poly(face):
        mb.poly("villa", [P3(s, z) for s, z in t], [(s, z) for s, z in t])
    for s0, s1, h0, h1, o in holes:
        zm = 0.5 * (h0 + h1)
        Po = lambda s, z, d=0.0, zm=zm: P3(s, z, d, zm)
        for (sa, za), (sb, zb) in [((s0, h1), (s0, h0)), ((s1, h0), (s1, h1)), ((s1, h1), (s0, h1)), ((s0, h0), (s1, h0))]:
            mb.poly("villa", [Po(sa, za), Po(sb, zb), Po(sb, zb, 0.10), Po(sa, za, 0.10)])
        insert(mb, Po, s0, s1, h0, h1, o, "villa")
    # alfiz: 6 cm deep, taupe stone, the arch cut through it 0.40 m deep
    a0, a1 = sc - 1.095, sc + 1.095
    for (sa, za), (sb, zb) in [((a0, 5.55), (a0, 0.0)), ((a1, 0.0), (a1, 5.55)), ((a1, 5.55), (a0, 5.55))]:
        mb.poly("surround", [P3(sa, za), P3(sb, zb), P3(sb, zb, 0.06), P3(sa, za, 0.06)])
    panel = box(a0, 0.0, a1, 5.55).difference(arch)
    for g in L.as_polys(panel):
        for t in L.tri_poly(g):
            mb.poly("surround", [P3(s, z, 0.06) for s, z in t], [(s, z) for s, z in t])
    ring = list(arch.exterior.coords)
    for (sa, za), (sb, zb) in zip(ring, ring[1:]):
        if za < 0.0 and zb < 0.0:
            continue
        za, zb = max(za, 0.0), max(zb, 0.0)
        mb.poly("surround", [P3(sb, zb, 0.06), P3(sa, za, 0.06), P3(sa, za, 0.40), P3(sb, zb, 0.40)])
    # behind the arch: the studded door (to 3.30), its transom (3.39 - 4.10), the mashrabiya tympanum
    a_in = arch.intersection(box(-1, 0.0, Lg + 1, 10))
    j0, j1 = min(x for x, z in a_in.exterior.coords if z < 1.0), max(x for x, z in a_in.exterior.coords if z < 1.0)
    D.pbox(mb, P3, j0, j1, 0.0, 3.30, 0.40, 0.48, "door_wood")
    D.pbox(mb, P3, j0, j1, 3.30, 3.39, 0.38, 0.48, "door_wood")
    D.pbox(mb, P3, j0, j1, 3.39, 4.10, 0.40, 0.48, "door_wood")
    D.pbox(mb, P3, j0, j1, 4.10, 4.17, 0.38, 0.48, "door_wood")
    tymp = a_in.intersection(box(-1, 4.17, Lg + 1, 10))
    for g in L.as_polys(tymp):
        for t in L.tri_poly(g):
            mb.poly("mashrabiya", [P3(s, z, 0.42) for s, z in t], [(s, z) for s, z in t])
    D.pbox(mb, P3, sc - 0.012, sc + 0.012, 0.0, 3.30, 0.37, 0.40, "metal_dark")       # the leaves' meeting
    for i in range(7):                                                             # studs
        for j in range(16):
            a = j0 + 0.10 + (j1 - j0 - 0.20) * i / 6
            b = 0.20 + 2.95 * j / 15
            D.pbox(mb, P3, a - 0.013, a + 0.013, b - 0.013, b + 0.013, 0.385, 0.40, "metal_dark")
        for j in range(4):
            a = j0 + 0.10 + (j1 - j0 - 0.20) * i / 6
            b = 3.50 + 0.48 * j / 3
            D.pbox(mb, P3, a - 0.013, a + 0.013, b - 0.013, b + 0.013, 0.385, 0.40, "metal_dark")
    for sg in (-1, 1):                                                             # ring pulls
        D.pbox(mb, P3, sc + sg * 0.16 - 0.02, sc + sg * 0.16 + 0.02, 1.08, 1.32, 0.35, 0.40, "metal_dark")
    mb.box("coping_beige", *sorted((P3(sc - 0.87, 0.0)[0], P3(sc + 0.87, 0.0)[0])),
           PT.bounds[3], PT.bounds[3] + 0.36, -0.30, 0.10)            # door step


def stair(mb):
    """Outside stair up the west side: 18 treads of 0.27 m, 19 risers to the landing at +3.70 over the west
    bathroom; solid down to the ground (client 24-10: the void under the flight showed as a dark slot along the
    house), a solid parapet on its outer side."""
    x0, x1, ya, yb, ye = STAIR
    ye = 49.75 + TB                                       # the landing and its end wall run into the tower's face
    n = 19
    r = Z_TR / n
    prof = [(ya, ZBOT)]
    for k in range(n - 1):
        prof += [(ya + 0.27 * k, r * (k + 1)), (ya + 0.27 * (k + 1), r * (k + 1))]
    prof += [(yb, Z_TR), (ye, Z_TR), (ye, ZBOT)]
    body = Polygon(prof).buffer(0)
    D.ext(mb, "villa", body, lambda a, b, w: (w, a, b), x1 + TB, x0 + 0.15)
    for k in range(n - 1):
        mb.box("coping_beige", x0 + 0.15, x1 + 0.02, ya + 0.27 * k - 0.02, ya + 0.27 * (k + 1), r * (k + 1), r * (k + 1) + 0.03)
    mb.box("coping_beige", x0 + 0.15, x1 + TB, yb - 0.02, ye - 0.15, Z_TR, Z_TR + 0.03)
    par = Polygon([(ya, ZBOT), (ye, ZBOT), (ye, Z_TR + 1.00), (yb, Z_TR + 1.00), (ya, r + 1.00)])
    D.ext(mb, "villa", par, lambda a, b, w: (w, a, b), x0, x0 + 0.15)
    mb.box("villa", x0 + 0.15, x1 + TB, ye - 0.15, ye, Z_TR, Z_TR + 1.00)             # the landing's end
    # rounded coping on the parapet: a narrower slice on its top
    top = Polygon([(ya, r + 1.00), (yb, Z_TR + 1.00), (ye, Z_TR + 1.00), (ye, Z_TR + 1.04), (yb, Z_TR + 1.04), (ya, r + 1.04)])
    D.ext(mb, "villa", top, lambda a, b, w: (w, a, b), x0 + 0.025, x0 + 0.125)
    mb.box("villa", x0 + 0.125, x1 + TB, ye - 0.125, ye - 0.025, Z_TR + 1.00, Z_TR + 1.04)


def pool_and_ground(mb):
    L.prism(mb, "coping", POOL.difference(BASIN).difference(SPA), -0.30, 0.10)
    for b_, dep in ((BASIN, POOL_DEPTH), (SPA, SPA_DEPTH)):
        L.prism(mb, "tile_jade", b_, -dep - 0.05, -dep + 0.15, sides=False)
        L.prism(mb, "tile_jade", b_.buffer(0.01, join_style=2).difference(b_.buffer(-0.01, join_style=2)), -dep + 0.15, 0.08)
        L.prism(mb, "pool_water", b_.buffer(-0.01, join_style=2), -0.07, -0.05, sides=False)
    bx0, by0, bx1, by1 = BASIN.bounds
    for k in range(3):                                     # Roman steps in the corner by the house (coupe A-A)
        q = box(bx0, by1 - 0.40 * (3 - k), bx0 + 1.60, by1)
        L.prism(mb, "tile_jade", q, -POOL_DEPTH + 0.15, -0.30 - 0.35 * k, sides=True)
    sx0, sy0, sx1, sy1 = SPA.bounds                        # the spa basin's bench round three sides
    L.prism(mb, "tile_jade", box(sx0, sy0, sx1, sy1).difference(box(sx0, sy0 + 0.40, sx1 - 0.40, sy1 - 0.40)), -SPA_DEPTH + 0.15, -0.45)
    L.prism(mb, "terrace", box(24.122, 38.035, 31.624, 38.535), -0.30, 0.10)
    for g in (TER_REAR, TER_NW.union(box(20.30, 53.12, 24.513, 53.173)), TER_NE.union(box(31.133, 52.05, 35.684, 52.105)), PATH_W):
        L.prism(mb, "terrace", g, -0.40, Z_FL - 0.005 if g is not PATH_W else 0.09)
    for pl in (box(20.30, 53.173, 20.72, 54.14), box(35.26, 52.105, 35.684, 54.14)):        # the terraces' planters
        L.prism(mb, "villa", pl.difference(pl.buffer(-0.08, join_style=2)), Z_FL, Z_FL + 0.55)
        L.prism(mb, "soil", pl.buffer(-0.08, join_style=2), Z_FL, Z_FL + 0.48, sides=False)


def build(M, col, name="SRC_VILLA_C"):
    import bpy
    from mathutils import Matrix
    mb = C.MeshBuilder()
    for k in TOWERS:
        tower(mb, k)
    bathrooms(mb)
    centre(mb)
    portal(mb)
    stair(mb)
    pool_and_ground(mb)
    obs = mb.build("VILLA_C", col, M)
    ob = L.join(obs, name)
    ob.data.transform(Matrix.Translation((-XO, -YO, 0.0)))
    L.weld(ob, 0.0003)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


def mirrored(src, name):
    """The villa mirrored across its plot (its stair on the other side), faces turned back out."""
    import bmesh
    import bpy
    me = src.data.copy()
    me.name = name
    bm = bmesh.new()
    bm.from_mesh(me)
    for v in bm.verts:
        v.co.x = PLOT_W - v.co.x
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    for c in src.users_collection:
        c.objects.link(ob)
    return ob
