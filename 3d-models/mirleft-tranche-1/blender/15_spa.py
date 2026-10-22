"""
15_spa — the SPA (client 22-10: "add spa, we don't have a plan, we want a suggestion on the same size as on the
plan"; reference photos: a riad spa round a courtyard pool, arcades of Moroccan arches, timber pergolas with
flowering climbers, a crenellated tower, terracotta hipped roofs, palms, olive trees, lanterns, loungers).

A DESIGN SUGGESTION, not a drawing: it fills the plan's SPA cell (the walls 0.40 m inside its kerb lines,
about 50.9 x 23.2 m) in the style of the villas (the sand render, taupe stone surrounds, the grey ledge /
ochre band cornice, the pointed horseshoe arch of the villa type C's portal).

Local frame: x 0-W across the cell, y 0-Lg along it, y = Lg at its north end on the Voie Publique (the
entrance); z = 0 at the pad, floors +0.20.
  north pavilion (reception, tea salon): the portal on the street, hipped terracotta roof on timber eaves,
    three arched doors onto the courtyard;
  the courtyard: a 20 x 4 m pool in turquoise mosaic with a white stone coping, travertine decks with white
    loungers, a timber pergola over the loungers at its south end under bougainvillea, a round fountain at
    its north end, date palms in square planters at its four corners, olive trees in terracotta jars;
  the two wings (treatment rooms) behind arcades of pointed horseshoe arches on square pillars, a hanging
    lantern in each bay; flat roofs behind a crenellated parapet;
  south pavilion (hammam), hipped roof, its arched door on the courtyard; the crenellated tower at its
    south-west corner (11 m, three floors of small arched windows).
"""
import importlib.util
import math
import os

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t3_vc_spa", os.path.join(HERE, "14_villa_c.py"))
VC = importlib.util.module_from_spec(_spec)
VC.__dict__["L"] = L
_spec.loader.exec_module(VC)
D = VC.D

Z_FL = 0.20
WING_D, ARC_D = 5.00, 2.40          # treatment rooms, arcade
PAV_D, APRON = 9.00, 1.50           # pavilions (depth), paved apron in front of the north one
Z_WING, Z_PAV, Z_TOWER = 4.20, 5.00, 10.60
TOWER = 6.00


def ext(mb, mat, poly, P, w0, w1):
    D.ext(mb, mat, poly, P, w0, w1)


def merlons(mb, mat, ring_line, z0, h=0.55, w=0.55, pitch=1.10, t=0.40, inward=None):
    """Square merlons along a polyline (the parapet's centre line), standing on z0."""
    L_ = ring_line.length
    n = max(1, int(L_ / pitch))
    for k in range(n):
        d = (k + 0.5) * L_ / n
        p = ring_line.interpolate(d)
        q = ring_line.interpolate(min(L_, d + 0.01))
        dx, dy = q.x - p.x, q.y - p.y
        nrm = math.hypot(dx, dy) or 1.0
        ux, uy = dx / nrm, dy / nrm
        g = Polygon([(p.x - ux * w / 2 - uy * t / 2, p.y - uy * w / 2 + ux * t / 2), (p.x + ux * w / 2 - uy * t / 2, p.y + uy * w / 2 + ux * t / 2),
                     (p.x + ux * w / 2 + uy * t / 2, p.y + uy * w / 2 - ux * t / 2), (p.x - ux * w / 2 + uy * t / 2, p.y - uy * w / 2 - ux * t / 2)])
        L.prism(mb, mat, g, z0, z0 + h)


def hipped(mb, rect, ze, pitch_deg=30.0, ov=0.55):
    """Hipped terracotta roof over rect, eaves ov out at height ze, timber fascia and corbels under it."""
    x0, y0, x1, y1 = rect.bounds
    x0, y0, x1, y1 = x0 - ov, y0 - ov, x1 + ov, y1 + ov
    w, l = x1 - x0, y1 - y0
    tp = math.tan(math.radians(pitch_deg))
    if w <= l:
        h = w / 2 * tp
        r0, r1 = (0.5 * (x0 + x1), y0 + w / 2, ze + h), (0.5 * (x0 + x1), y1 - w / 2, ze + h)
    else:
        h = l / 2 * tp
        r0, r1 = (x0 + l / 2, 0.5 * (y0 + y1), ze + h), (x1 - l / 2, 0.5 * (y0 + y1), ze + h)
    a, b, c, d = (x0, y0, ze), (x1, y0, ze), (x1, y1, ze), (x0, y1, ze)

    def face(pts, eave):
        (ex0, ey0, _), (ex1, ey1, _) = eave
        el = math.hypot(ex1 - ex0, ey1 - ey0)
        ux, uy = (ex1 - ex0) / el, (ey1 - ey0) / el
        nx, ny = -uy, ux
        uv = []
        for (px_, py_, pz) in pts:
            s = (px_ - ex0) * ux + (py_ - ey0) * uy
            dist = math.hypot((px_ - ex0) * nx + (py_ - ey0) * ny, pz - ze)
            uv.append((s, dist))
        mb.poly("roof_tiles", pts, uv)
    if w <= l:
        face([a, b, r0], (a, b))
        face([b, c, r1, r0], (b, c))
        face([c, d, r1], (c, d))
        face([d, a, r0, r1], (d, a))
    else:
        face([a, b, r1, r0], (a, b))
        face([b, c, r1], (b, c))
        face([c, d, r0, r1], (c, d))
        face([d, a, r0], (d, a))
    # underside (soffit) and fascia
    L.prism(mb, "timber", box(x0, y0, x1, y1).difference(rect), ze - 0.16, ze, bottom=True)
    for k in range(int((x1 - x0) / 0.9) + 1):           # corbels along the long sides
        xx = x0 + 0.45 + 0.9 * k
        if xx > x1 - 0.3:
            break
        for yy0, yy1 in ((y0 + 0.05, rect.bounds[1]), (rect.bounds[3], y1 - 0.05)):
            mb.box("timber", xx - 0.06, xx + 0.06, yy0, yy1, ze - 0.34, ze - 0.16)


def face_with_holes(mb, mat, p, q, z0, z1, holes, dep=0.30, back=None, reveals=True, deps=None):
    """A plumb wall face p->q with arched / square holes (s, z polygons), their reveals dep deep, and what
    stands in them: back(s0, s1, poly, P3) callback."""
    Lg, P3, axis, org, du, cst, U, N = VC.frame_of(p, q, False)
    face = box(0.0, z0, Lg, z1)
    for h in holes:
        face = face.difference(h)
    for g in L.as_polys(face):
        for t in L.tri_poly(g):
            mb.poly(mat, [P3(s, z) for s, z in t], [(s, z) for s, z in t])
    for i, h in enumerate(holes if reveals else []):
        ring = list(h.exterior.coords)
        if not h.exterior.is_ccw:
            ring = ring[::-1]
        dp = deps[i] if deps else dep
        for (sa, za), (sb, zb) in zip(ring, ring[1:]):
            if za <= z0 + 1e-6 and zb <= z0 + 1e-6:
                continue
            mb.poly("surround" if dp > 0.11 else mat, [P3(sb, zb), P3(sa, za), P3(sa, za, dp), P3(sb, zb, dp)])
        if dp <= 0.11:                                    # a niche: its back
            s0, z0_, s1, z1_ = h.bounds
            mb.poly(mat, [P3(s0, z0_, dp), P3(s1, z0_, dp), P3(s1, z1_, dp), P3(s0, z1_, dp)])
        elif back:
            back(h, P3)
    return Lg, P3


def jambs(h):
    zb = h.bounds[1] + 0.5
    xs = [x for x, z in h.exterior.coords if z < zb]
    return min(xs), max(xs)


def arch(cx, w, zs, z0=0.0):
    a = VC.arch_poly(cx, w, zs)
    return a.intersection(box(cx - w, z0, cx + w, 50.0))


def build(M, col, W, Lg, name="T2_SPA"):
    """Returns (objects, plants [(kind, x, y, z, scale)], lanterns [(x, y, z)]) in the local frame."""
    mb = C.MeshBuilder()
    plants, lamps = [], []
    yS, yN = PAV_D, Lg - APRON - PAV_D                    # the courtyard between the pavilions
    xW, xE = WING_D, W - WING_D                            # the wings' inner walls
    aW, aE = xW + ARC_D, xE - ARC_D                        # the arcades' fronts

    # ---- ground: the plot paved, the courtyard in travertine, the arcades in terracotta ------------------
    cx = W / 2
    pool = box(cx - 2.0, 0.5 * (yS + yN) - 10.0 + 1.6, cx + 2.0, 0.5 * (yS + yN) + 10.0 + 1.6)
    L.prism(mb, "deck_stone", box(aW, yS, aE, yN).difference(pool.buffer(0.35, join_style=2)), -0.40, Z_FL)
    L.prism(mb, "terracotta", box(xW, yS, aW, yN), -0.40, Z_FL)
    L.prism(mb, "terracotta", box(aE, yS, xE, yN), -0.40, Z_FL)
    L.prism(mb, "deck_stone", box(0.0, Lg - APRON, W, Lg), -0.40, 0.05)

    # ---- the wings: rooms, flat roof, crenellated parapet, high windows outside, doors in the arcade ---
    nb = max(6, round((yN - yS) / 3.2))
    bay = (yN - yS) / nb
    for side, (x0, x1) in (("W", (0.0, xW)), ("E", (xE, W))):
        g = box(x0, yS, x1, yN)
        out_x, in_x = (x0, x1) if side == "W" else (x1, x0)
        # outer face with high windows (taupe surrounds), the inner face with a door per bay
        hi = [box((k + 0.5) * bay - 0.35, 2.40, (k + 0.5) * bay + 0.35, 3.30) for k in range(nb)]
        p, q = ((out_x, yN), (out_x, yS)) if side == "W" else ((out_x, yS), (out_x, yN))

        def win_back(h, P3):
            s0, z0_, s1, z1_ = h.bounds
            D.pbox(mb, P3, s0, s1, z0_, z1_, 0.12, 0.14, "glass")
            D.pbox(mb, P3, s0 - 0.18, s0, z0_ - 0.18, z1_ + 0.20, -0.04, 0.02, "surround")
            D.pbox(mb, P3, s1, s1 + 0.18, z0_ - 0.18, z1_ + 0.20, -0.04, 0.02, "surround")
            D.pbox(mb, P3, s0, s1, z1_, z1_ + 0.20, -0.04, 0.02, "surround")
            D.pbox(mb, P3, s0, s1, z0_ - 0.18, z0_, -0.04, 0.02, "surround")
            for k in range(1, 4):
                s = s0 + (s1 - s0) * k / 4
                D.pbox(mb, P3, s - 0.012, s + 0.012, z0_, z1_, 0.08, 0.12, "metal_dark")
        face_with_holes(mb, "villa", p, q, -1.0, Z_WING, hi, 0.12, win_back)
        doors = [box((k + 0.5) * bay - 0.55, Z_FL, (k + 0.5) * bay + 0.55, 2.55) for k in range(nb)]
        p, q = ((in_x, yS), (in_x, yN)) if side == "W" else ((in_x, yN), (in_x, yS))

        def door_back(h, P3):
            s0, z0_, s1, z1_ = h.bounds
            D.pbox(mb, P3, s0, s1, z0_, z1_, 0.14, 0.20, "door_wood")
            D.pbox(mb, P3, s0 - 0.20, s0, z0_, z1_ + 0.20, -0.04, 0.02, "surround")
            D.pbox(mb, P3, s1, s1 + 0.20, z0_, z1_ + 0.20, -0.04, 0.02, "surround")
            D.pbox(mb, P3, s0, s1, z1_, z1_ + 0.20, -0.04, 0.02, "surround")
            for sg in (-1, 1):
                D.pbox(mb, P3, 0.5 * (s0 + s1) + sg * 0.12 - 0.015, 0.5 * (s0 + s1) + sg * 0.12 + 0.015, 0.95, 1.15, 0.10, 0.14, "metal_dark")
        face_with_holes(mb, "villa", p, q, -1.0, Z_WING, doors, 0.14, door_back)
        L.prism(mb, "terrace", g.buffer(-0.30, join_style=2), Z_WING - 0.30, Z_WING - 0.29, sides=False)
        ring = g.difference(g.buffer(-0.30, join_style=2))
        L.prism(mb, "villa", g.buffer(-0.01, join_style=2).difference(g.buffer(-0.30, join_style=2)), Z_WING - 0.30, Z_WING + 0.10)
        for z0, z1, pd, mat in ((Z_WING - 0.42, Z_WING - 0.34, 0.08, "ledge"), (Z_WING - 0.34, Z_WING - 0.20, 0.05, "band"), (Z_WING - 0.20, Z_WING - 0.12, 0.10, "ledge")):
            L.prism(mb, mat, g.buffer(pd, join_style=2).difference(g), z0, z1, bottom=True)
        xm = out_x + (0.15 if side == "W" else -0.15)            # merlons on the street side
        merlons(mb, "villa", LineString([(xm, yS + 0.3), (xm, yN - 0.3)]), Z_WING + 0.10)

    # ---- the arcades: pointed horseshoe arches on square pillars, timber ceiling, a lantern per bay ------
    for side, xf in (("W", aW), ("E", aE)):
        p, q = ((xf, yS), (xf, yN)) if side == "W" else ((xf, yN), (xf, yS))
        holes = [arch((k + 0.5) * bay, bay - 0.50, 2.35, Z_FL) for k in range(nb)]
        Lw, P3 = face_with_holes(mb, "villa", p, q, Z_FL, 3.90, holes, 0.45)
        # the wall's back face (plumb, 0.45 behind, the same arches), its top and cornice, the gallery's roof
        xb = xf - 0.45 if side == "W" else xf + 0.45
        pb, qb = ((xb, yN), (xb, yS)) if side == "W" else ((xb, yS), (xb, yN))
        face_with_holes(mb, "villa", pb, qb, Z_FL, 3.90, [affinity.scale(h, -1.0, 1.0, origin=(Lw / 2, 0.0)) for h in holes], 0.45, reveals=False)
        g_top = box(min(xf, xb), yS, max(xf, xb), yN)
        L.prism(mb, "villa", g_top, 3.90, 4.05)
        for z0, z1, pd, mat in ((3.90, 3.98, 0.08, "ledge"), (3.98, 4.05, 0.04, "band")):
            L.prism(mb, mat, g_top.buffer(pd, join_style=2).difference(g_top), z0, z1, bottom=True)
        x_in = xW if side == "W" else xE
        L.prism(mb, "terrace", box(min(x_in, xb), yS, max(x_in, xb), yN), 4.04, 4.05, sides=False)
        L.prism(mb, "timber", box(min(x_in, xb), yS, max(x_in, xb), yN), 3.55, 3.62, bottom=True)
        for k in range(nb + 1):
            yy = yS + bay * k
            mb.box("timber", min(x_in, xb), max(x_in, xb), yy - 0.08, yy + 0.08, 3.40, 3.55)
        for k in range(nb):
            yy = yS + (k + 0.5) * bay
            xc = 0.5 * (x_in + xb)
            lamps.append((xc, yy, 2.55))

    # ---- pavilions: walls to +5.00, the villas' cornice, hipped roofs; the north one's portal on the street
    def pavilion(y0, y1, portal_side):
        g = box(0.0, y0, W, y1)
        z_c = Z_PAV
        for z0, z1, pd, mat in ((z_c - 0.40, z_c - 0.32, 0.10, "ledge"), (z_c - 0.32, z_c - 0.16, 0.06, "band"), (z_c - 0.16, z_c, 0.14, "ledge")):
            L.prism(mb, mat, g.buffer(pd, join_style=2).difference(g), z0, z1, bottom=True)
        hipped(mb, g, z_c + 0.02)
        return g

    def big_arch_back(h, P3, door=True):
        if door:
            arch_surround(h, P3, 0.16)
        else:
            return
        s0, z0_, s1, z1_ = h.bounds
        cx = 0.5 * (s0 + s1)
        jw = jambs(h)
        D.pbox(mb, P3, jw[0], jw[1], Z_FL, 2.90, 0.30, 0.38, "door_wood")
        tymp = h.intersection(box(-1e3, 2.98, 1e3, 1e3))
        for g in L.as_polys(tymp):
            for t in L.tri_poly(g):
                mb.poly("mashrabiya", [P3(s, z, 0.32) for s, z in t], [(s, z) for s, z in t])
        D.pbox(mb, P3, jw[0], jw[1], 2.90, 2.98, 0.28, 0.38, "door_wood")
        for i in range(5):
            for j in range(10):
                a = jw[0] + 0.10 + (jw[1] - jw[0] - 0.20) * i / 4
                b = Z_FL + 0.20 + 2.40 * j / 9
                D.pbox(mb, P3, a - 0.012, a + 0.012, b - 0.012, b + 0.012, 0.285, 0.30, "metal_dark")
        D.pbox(mb, P3, cx - 0.012, cx + 0.012, Z_FL, 2.90, 0.27, 0.30, "metal_dark")

    def arch_surround(h, P3, wd=0.14):
        ring = h.buffer(wd, join_style=2).difference(h).intersection(box(-1e3, h.bounds[1] - wd, 1e3, 1e3))
        ext(mb, "surround", ring, lambda a, b, w: P3(a, b, w), -0.03, 0.01)

    def glazed_arch_back(h, P3):
        arch_surround(h, P3)
        jw = jambs(h)
        z0_, z1_ = h.bounds[1], h.bounds[3]
        for gg in L.as_polys(h):
            for t in L.tri_poly(gg):
                mb.poly("glass", [P3(s, z, 0.20) for s, z in t], [(s, z) for s, z in t])
        mb.poly("interior", [P3(jw[0] - 0.3, z0_ - 0.3, 0.9), P3(jw[1] + 0.3, z0_ - 0.3, 0.9), P3(jw[1] + 0.3, z1_ + 0.3, 0.9), P3(jw[0] - 0.3, z1_ + 0.3, 0.9)])
        D.pbox(mb, P3, jw[0], jw[1], z0_, z0_ + 0.06, 0.17, 0.23, "frame")
        cx = 0.5 * (jw[0] + jw[1])
        zt = z0_ + 0.70 * (z1_ - z0_)
        D.pbox(mb, P3, cx - 0.03, cx + 0.03, z0_ + 0.06, zt, 0.17, 0.23, "frame")
        D.pbox(mb, P3, jw[0], jw[1], zt - 0.06, zt, 0.17, 0.23, "frame")

    # north pavilion: y from yN to Lg - APRON
    yP0, yP1 = yN, Lg - APRON
    gN = pavilion(yP0, yP1, "N")
    cx = W / 2
    face_with_holes(mb, "villa", (W, yP1), (0.0, yP1), -1.0, Z_PAV - 0.40,
                    [arch(W - cx, 2.10, 2.70, Z_FL)] + [arch(W - x, 1.30, 2.10, Z_FL).intersection(box(-1e3, 1.0, 1e3, 1e3)) for x in (cx - 6.0, cx + 6.0)],
                    0.40, lambda h, P3: big_arch_back(h, P3) if h.bounds[1] < 0.5 else glazed_arch_back(h, P3))
    face_with_holes(mb, "villa", (0.0, yP0), (W, yP0), -1.0, Z_PAV - 0.40,
                    [arch(x, 1.60, 2.30, Z_FL) for x in (cx - 3.0, cx, cx + 3.0)], 0.40, glazed_arch_back)
    for p, q in (((0.0, yP1), (0.0, yP0)), ((W, yP0), (W, yP1))):
        face_with_holes(mb, "villa", p, q, -1.0, Z_PAV - 0.40, [arch(PAV_D / 2, 1.30, 2.10, 1.0)], 0.30, glazed_arch_back)
    # the portal on the street: a block 0.90 m proud of the pavilion, up to +6.67 with the villas' cornice and
    # horns (as the villa type C's portal tower), the arch through it in a taupe alfiz, niches over it
    PB = box(cx - 2.30, yP1 - 0.30, cx + 2.30, yP1 + 0.90)
    hp = arch(2.30, 2.10, 2.70, Z_FL)
    nich = [box(2.30 + k - 0.10, 5.30, 2.30 + k + 0.10, 5.50) for k in (-0.9, 0.0, 0.9)]
    Lp, P3p = face_with_holes(mb, "villa", (cx + 2.30, yP1 + 0.90), (cx - 2.30, yP1 + 0.90), -1.0, 6.01, [hp] + nich, 1.20,
                              lambda h, P3: big_arch_back(h, P3, False), deps=[1.20, 0.10, 0.10, 0.10])
    alf = box(2.30 - 1.55, Z_FL, 2.30 + 1.55, 4.25).difference(hp)
    ext(mb, "surround", alf, lambda a, b, w: P3p(a, b, w), -0.04, 0.0)
    for p_, q_ in (((cx - 2.30, yP1 + 0.90), (cx - 2.30, yP1)), ((cx + 2.30, yP1), (cx + 2.30, yP1 + 0.90))):
        face_with_holes(mb, "villa", p_, q_, -1.0, 6.01, [])
    face_with_holes(mb, "villa", (cx - 2.30, yP1 - 0.30), (cx + 2.30, yP1 - 0.30), Z_PAV - 0.40, 6.01, [])
    for z0, z1, pd, mat in [(6.01, 6.08, 0.09, "ledge"), (6.08, 6.17, 0.05, "band"), (6.17, 6.25, 0.10, "ledge"), (6.25, 6.40, 0.15, "ledge")]:
        L.prism(mb, mat, PB.buffer(pd, join_style=2).difference(PB), z0, z1, bottom=True)
    L.prism(mb, "villa", PB.buffer(-0.01, join_style=2), 6.01, 6.61)
    D.coping(mb, "villa", PB, 6.67, 0.06)
    VC.horns(mb, PB, 6.67)
    mb.box("coping_beige", cx - 1.40, cx + 1.40, yP1 + 0.90, yP1 + 1.40, -0.30, 0.10)
    for x in (cx - 2.4, cx + 2.4):
        lamps.append((x, yP1 + 0.25, 2.80))
        xp = x + (-1.8 if x < cx else 1.8)
        g = box(xp - 0.45, Lg - APRON + 0.15, xp + 0.45, Lg - APRON + 1.05)
        L.prism(mb, "coping", g.difference(g.buffer(-0.08, join_style=2)), 0.05, 0.45)
        L.prism(mb, "soil", g.buffer(-0.08, join_style=2), 0.05, 0.40, sides=False)
        plants.append(("date", xp, Lg - APRON + 0.6, 0.40, 0.70))

    # south pavilion: y 0 to yS, the tower at its south-west corner
    gS = pavilion(0.0, yS, "S")
    face_with_holes(mb, "villa", (W, yS), (0.0, yS), -1.0, Z_PAV - 0.40,
                    [arch(W - cx, 2.10, 2.70, Z_FL)] + [arch(W - x, 1.40, 2.20, Z_FL) for x in (cx - 3.2, cx + 3.2)], 0.40,
                    lambda h, P3: big_arch_back(h, P3) if abs(0.5 * (h.bounds[0] + h.bounds[2]) - (W - cx)) < 0.5 else glazed_arch_back(h, P3))
    face_with_holes(mb, "villa", (TOWER, 0.0), (W, 0.0), -1.0, Z_PAV - 0.40,
                    [arch(x - TOWER, 1.20, 2.20, 1.0) for x in (TOWER + 2.5, W / 2 + 1.0, W - 2.6)], 0.30, glazed_arch_back)
    for p, q in (((W, 0.0), (W, yS)),):
        face_with_holes(mb, "villa", p, q, -1.0, Z_PAV - 0.40, [arch(PAV_D / 2, 1.30, 2.10, 1.0)], 0.30, glazed_arch_back)
    face_with_holes(mb, "villa", (0.0, yS), (0.0, TOWER), -1.0, Z_PAV - 0.40, [arch((yS - TOWER) / 2, 1.0, 2.0, 1.2)], 0.30, glazed_arch_back)

    # the tower: plumb walls, small arched windows on three floors, the villas' cornice, merlons
    T = box(0.0, 0.0, TOWER, TOWER)
    for p, q in VC.edges(T):
        face_with_holes(mb, "villa", p, q, -1.0, Z_TOWER, [arch(TOWER / 2, 0.80, zz + 1.10, zz) for zz in (2.0, 5.6, 8.4)], 0.30, glazed_arch_back)
    for z0, z1, pd, mat in ((Z_TOWER, Z_TOWER + 0.08, 0.10, "ledge"), (Z_TOWER + 0.08, Z_TOWER + 0.24, 0.07, "band"), (Z_TOWER + 0.24, Z_TOWER + 0.40, 0.16, "ledge")):
        L.prism(mb, mat, T.buffer(pd, join_style=2).difference(T), z0, z1, bottom=True)
    L.prism(mb, "villa", T.buffer(-0.01, join_style=2).difference(T.buffer(-0.35, join_style=2)), Z_TOWER - 0.6, Z_TOWER + 1.00)
    L.prism(mb, "terrace", T.buffer(-0.35, join_style=2), Z_TOWER - 0.61, Z_TOWER - 0.60, sides=False)
    merlons(mb, "villa", T.buffer(-0.175, join_style=2).exterior, Z_TOWER + 1.00, h=0.65, w=0.60, pitch=1.15, t=0.35)

    # ---- the courtyard: pool, decks, pergola, fountain, planters, jars, loungers ---------------------------
    L.prism(mb, "coping", pool.buffer(0.35, join_style=2).difference(pool), Z_FL - 0.05, Z_FL + 0.06)
    L.prism(mb, "pool_tile", pool, -1.30, -1.25, sides=False)
    L.prism(mb, "pool_tile", pool.buffer(0.01, join_style=2).difference(pool.buffer(-0.01, join_style=2)), -1.25, Z_FL + 0.02)
    L.prism(mb, "pool_water", pool.buffer(-0.01, join_style=2), Z_FL - 0.10, Z_FL - 0.08, sides=False)
    for k in range(3):                                    # steps across its south end
        L.prism(mb, "pool_tile", box(cx - 2.0, pool.bounds[1], cx + 2.0, pool.bounds[1] + 0.40 * (3 - k)), -1.25, Z_FL - 0.25 - 0.35 * k)
    # pergola at the south end over the loungers, bougainvillea on it
    py0, py1 = yS + 0.6, pool.bounds[1] - 0.9
    px0, px1 = aW + 0.6, aE - 0.6
    for x in (px0, px1):
        for y in (py0, py1):
            mb.box("timber", x - 0.09, x + 0.09, y - 0.09, y + 0.09, Z_FL, 3.10)
    for y in (py0, py1):
        mb.box("timber", px0 - 0.3, px1 + 0.3, y - 0.08, y + 0.08, 3.10, 3.34)
    n_r = int((px1 - px0) / 0.45)
    for k in range(n_r + 1):
        x = px0 + (px1 - px0) * k / n_r
        mb.box("timber", x - 0.035, x + 0.035, py0 - 0.4, py1 + 0.4, 3.34, 3.46)
    for k in range(10):                                   # bougainvillea over it and at its posts
        x = px0 + 0.5 + (px1 - px0 - 1.0) * ((k * 0.618) % 1.0)
        y = py0 + 0.4 + (py1 - py0 - 0.8) * ((k * 0.382 + 0.2) % 1.0)
        plants.append(("shrub_pink", x, y, 3.42, 0.95 + 0.15 * (k % 3)))
    for x in (px0, px1):
        for y in (py0, py1):
            plants.append(("shrub_pink", x, y, Z_FL, 1.05))
    # loungers along the pool, under the pergola and on the decks
    def lounger(x, y, ang):
        ca, sa = math.cos(ang), math.sin(ang)
        R = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
        g = Polygon([R(-0.35, -0.95), R(0.35, -0.95), R(0.35, 0.95), R(-0.35, 0.95)])
        L.prism(mb, "lounger_white", g, Z_FL + 0.06, Z_FL + 0.30)
        L.prism(mb, "cushion", g.buffer(-0.04), Z_FL + 0.30, Z_FL + 0.36)
        back = Polygon([R(-0.33, 0.55), R(0.33, 0.55), R(0.33, 0.93), R(-0.33, 0.93)])
        L.prism(mb, "cushion", back, Z_FL + 0.36, Z_FL + 0.70)
        for u, v in ((-0.3, -0.85), (0.3, -0.85), (-0.3, 0.85), (0.3, 0.85)):
            L.prism(mb, "lounger_white", Point(*R(u, v)).buffer(0.03, 4), Z_FL, Z_FL + 0.06)
    for k in range(4):
        lounger(px0 + 0.9 + (px1 - px0 - 1.8) * k / 3, 0.5 * (py0 + py1), 0.0)
    for x in (cx - 2.0 - 1.35, cx + 2.0 + 1.35):
        for k in range(4):
            lounger(x, pool.bounds[1] + 3.0 + 4.4 * k, 0.0 if x < cx else math.pi)
    # parasols on the decks
    for x, y in ((cx - 3.6, pool.bounds[1] + 5.2), (cx + 3.6, pool.bounds[1] + 9.6)):
        L.prism(mb, "metal_dark", Point(x, y).buffer(0.03, 6), Z_FL, 2.55)
        top = (x, y, 2.75)
        rim = [(x + 1.3 * math.cos(2 * math.pi * k / 8), y + 1.3 * math.sin(2 * math.pi * k / 8), 2.30) for k in range(8)]
        for k in range(8):
            mb.poly("canvas", [rim[k], rim[(k + 1) % 8], top])
    # round fountain at the pool's north end
    fc = (cx, pool.bounds[3] + 2.6)
    f = Point(*fc).buffer(1.25, 24)
    L.prism(mb, "coping", f.difference(Point(*fc).buffer(1.00, 24)), Z_FL, Z_FL + 0.50)
    L.prism(mb, "pool_tile", Point(*fc).buffer(1.00, 24), Z_FL, Z_FL + 0.05, sides=False)
    L.prism(mb, "pool_water", Point(*fc).buffer(0.99, 24), Z_FL + 0.38, Z_FL + 0.40, sides=False)
    L.prism(mb, "coping", Point(*fc).buffer(0.22, 12), Z_FL, Z_FL + 0.85)
    L.prism(mb, "coping", Point(*fc).buffer(0.45, 16), Z_FL + 0.85, Z_FL + 0.93)
    L.prism(mb, "bronze", Point(*fc).buffer(0.05, 8), Z_FL + 0.93, Z_FL + 1.25)
    # date palms in square planters at the four corners of the courtyard's centre; olive trees in jars
    for x in (aW + 1.1, aE - 1.1):
        for y in (pool.bounds[1] + 1.2, pool.bounds[3] - 1.2):
            g = box(x - 0.6, y - 0.6, x + 0.6, y + 0.6)
            L.prism(mb, "coping", g.difference(g.buffer(-0.10, join_style=2)), Z_FL, Z_FL + 0.45)
            L.prism(mb, "soil", g.buffer(-0.10, join_style=2), Z_FL, Z_FL + 0.40, sides=False)
            plants.append(("date", x, y, Z_FL + 0.40, 0.85))
    for x in (aW + 0.9, aE - 0.9):
        for k in (1, 3):
            y = pool.bounds[1] + 3.0 + 4.4 * k + 2.2
            if y > pool.bounds[3] - 2.5:
                continue
            jar = Point(x, y)
            L.prism(mb, "terracotta", jar.buffer(0.32, 10), Z_FL, Z_FL + 0.15)
            L.prism(mb, "terracotta", jar.buffer(0.42, 10), Z_FL + 0.15, Z_FL + 0.55)
            L.prism(mb, "terracotta", jar.buffer(0.36, 10), Z_FL + 0.55, Z_FL + 0.70)
            L.prism(mb, "soil", jar.buffer(0.30, 10), Z_FL + 0.66, Z_FL + 0.68, sides=False)
            plants.append(("olive", x, y, Z_FL + 0.68, 0.45))
    # standing lanterns at the pool's corners
    for x in (cx - 2.6, cx + 2.6):
        for y in (pool.bounds[1] - 0.5, pool.bounds[3] + 0.5):
            L.prism(mb, "metal_dark", Point(x, y).buffer(0.10, 8), Z_FL, Z_FL + 0.15)
            L.prism(mb, "metal_dark", Point(x, y).buffer(0.03, 6), Z_FL + 0.15, Z_FL + 1.10)
            lamps.append((x, y, Z_FL + 1.30))
    # bougainvillea climbing the pavilions' courtyard walls, beside their doors
    for y in (yS + 0.45, yN - 0.45):
        for x in (cx - 1.65, cx + 1.65):
            plants.append(("shrub_pink", x, y, Z_FL, 1.15))

    # lanterns: a bronze cage with warm glass
    for x, y, z in lamps:
        L.prism(mb, "bronze", Point(x, y).buffer(0.17, 6), z - 0.05, z)
        L.prism(mb, "lamp", Point(x, y).buffer(0.13, 6), z, z + 0.38)
        L.prism(mb, "bronze", Point(x, y).buffer(0.17, 6), z + 0.38, z + 0.43)
        L.prism(mb, "bronze", Point(x, y).buffer(0.08, 6), z + 0.43, z + 0.55)
    obs = mb.build(name, col, M)
    return obs, plants, lamps
