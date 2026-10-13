"""
03_public — public buildings of Tranche A+B, exterior only.

ADMINISTRATION  "3-PLAN_RESTAURANT_PAVILLON.DWG" (accueil, bureaux, salle de réunion, cafeteria,
                maquette de site). Plans RDC / ETAGE / TERRASSE-MASSE, four facades, coupes A-A,
                B-B, C-C. Four tapered corner towers to +12.20 (couleur terre de sienne, panels in
                bejmat cuite), body to +9.20 (etage +4.40, roof +7.85), entrance portal with a
                horseshoe arch to +7.70 (beam +6.50), passage with water walls (+5.60), bassins
                front and rear, cour anglaise, timber pergolas.
BOUTIQUE / RESTAURANT  "MARKET_ET_SPA.DWG" (Boutique, Restaurant, stock, cuisine, sous-sol).
                Roof plan: six square blocks in two rows; the two at one end are towers to +12.00,
                the other four rise to +8.70, the links between them to +6.20 (niveaux on the
                facades), two pyramid skylights.
CLUB, KIOSKS    hipped roofs drawn on the plan de masse (ANSI33 hatches); single storey
                (height not on the drawings: 3.40 m walls, roof pitch 30 degrees, INFERRED).
STATION         outline from the plan de masse, 3.00 m enclosure (INFERRED height).

Local frames: metres, origin at the building centre, front (access) towards -y, z = 0 at T.N.
"""
import math

from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C


# ---------------------------------------------------------------------------------------------
# generic face with holes (handles tapered faces by bilinear mapping)
# ---------------------------------------------------------------------------------------------
def hole_shape(h):
    s0, s1, z0, z1 = h["s0"], h["s1"], h["z0"], h["z1"]
    w = s1 - s0
    sc = (s0 + s1) / 2
    kind = h.get("shape", "rect")
    if kind == "rect":
        return box(s0, z0, s1, z1)
    if kind == "arch":                 # round-headed: arch springs at z1 - w/2
        zs = z1 - w / 2
        return unary_union([box(s0, z0, s1, zs), Point(sc, zs).buffer(w / 2, 24).intersection(box(s0, zs, s1, z1))])
    if kind == "horseshoe":            # circle wider than the jambs, centre at the springing
        R = w / 2 * 1.16
        zc = z1 - R
        return unary_union([box(s0, z0, s1, zc), Point(sc, zc).buffer(R, 40).intersection(box(sc - R, zc - R * 0.55, sc + R, z1))])
    raise ValueError(kind)


def face(mb, mat, P0, P1, z0, z1, holes=(), taper=0.0, rev=0.25, centre=None):
    """Wall face over the bottom edge P0->P1 (outward normal on the right). Top edge pulled
    inward by `taper` (and shortened 2*taper) for battered kasbah walls. Holes in (s, z), s in
    metres from the face centre."""
    (ax, ay), (bx, by) = P0, P1
    Lb = math.dist(P0, P1)
    ux, uy = (bx - ax) / Lb, (by - ay) / Lb
    nx, ny = uy, -ux
    H = z1 - z0

    def X(s, z, d=0.0):
        t = (z - z0) / H
        k = taper * t
        sl = s * (Lb - 2 * k) / Lb
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        return (cx + ux * sl - nx * (k + d), cy + uy * sl - ny * (k + d), z)

    poly = box(-Lb / 2, z0, Lb / 2, z1)
    shapes = []
    for h in holes:
        sh = hole_shape(h)
        shapes.append((sh, h))
        poly = poly.difference(sh)
    for t in L.tri_poly(poly):
        mb.poly(mat, [X(s, z) for s, z in t], [(s, z) for s, z in t])
    for sh, h in shapes:
        ring = list(sh.exterior.coords)
        if not sh.exterior.is_ccw:
            ring = ring[::-1]
        for (sa, za), (sb, zb) in zip(ring, ring[1:]):
            mb.poly(mat, [X(sb, zb), X(sa, za), X(sa, za, rev), X(sb, zb, rev)])
        kind = h.get("kind", "window")
        inner = sh.buffer(-0.06, join_style=2)
        if kind == "open":
            continue
        for t in L.tri_poly(sh):
            mb.poly("interior", [X(s, z, rev + 0.6) for s, z in t])
        if kind == "door":
            for t in L.tri_poly(sh):
                mb.poly("door_wood", [X(s, z, 0.12) for s, z in t])
            continue
        for t in L.tri_poly(inner):
            mb.poly("glass", [X(s, z, 0.12) for s, z in t])
        fr = sh.difference(inner)
        for t in L.tri_poly(fr):
            mb.poly("bronze", [X(s, z, 0.10) for s, z in t])
        n = h.get("n", 1)
        if n > 1:
            for k in range(1, n):
                s = h["s0"] + (h["s1"] - h["s0"]) * k / n
                m = box(s - 0.03, h["z0"], s + 0.03, h["z1"]).intersection(sh)
                for t in L.tri_poly(m):
                    mb.poly("bronze", [X(a, b, 0.11) for a, b in t])
        if h.get("surround"):
            sr = sh.buffer(h["surround"], join_style=2).difference(sh).intersection(box(-Lb / 2, z0 + 0.01, Lb / 2, z1))
            for t in L.tri_poly(sr):
                mb.poly(h.get("surround_mat", "trim"), [X(s, z, -0.04) for s, z in t])
    return X


def panel(mb, mat, X, s_half_bottom, s_half_top, z0, z1, holes=(), proud=0.04):
    """Trapezoid cladding panel on a face (X from face()), with holes cut out."""
    p = Polygon([(-s_half_bottom, z0), (s_half_bottom, z0), (s_half_top, z1), (-s_half_top, z1)])
    for h in holes:
        p = p.difference(hole_shape(h).buffer(0.0))
    for t in L.tri_poly(p):
        mb.poly(mat, [X(s, z, -proud) for s, z in t], [(s, z) for s, z in t])


def screen(mb, X, s0, s1, z0, z1, out):
    """Mashrabiya screen standing `out` m in front of the face, with a timber frame."""
    pts = [X(s0, z0, -out), X(s1, z0, -out), X(s1, z1, -out), X(s0, z1, -out)]
    mb.poly("mashrabiya", pts, [(s0 / 0.5, z0 / 0.5), (s1 / 0.5, z0 / 0.5), (s1 / 0.5, z1 / 0.5), (s0 / 0.5, z1 / 0.5)])
    pts2 = [X(s0, z0, -out + 0.03), X(s1, z0, -out + 0.03), X(s1, z1, -out + 0.03), X(s0, z1, -out + 0.03)]
    mb.poly("mashrabiya", pts2[::-1], [(s0 / 0.5, z0 / 0.5), (s1 / 0.5, z0 / 0.5), (s1 / 0.5, z1 / 0.5), (s0 / 0.5, z1 / 0.5)][::-1])
    for (a0, a1, b0, b1) in [(s0 - 0.05, s1 + 0.05, z1, z1 + 0.06), (s0 - 0.05, s0, z0, z1), (s1, s1 + 0.05, z0, z1)]:
        q = [X(a0, b0, -out - 0.02), X(a1, b0, -out - 0.02), X(a1, b1, -out - 0.02), X(a0, b1, -out - 0.02)]
        mb.poly("timber", q)
        mb.poly("timber", [X(a0, b1, -out - 0.02), X(a1, b1, -out - 0.02), X(a1, b1, 0.0), X(a0, b1, 0.0)])


def squares(mb, X, s_list, z, size=0.20, proud=0.03, mat="trim"):
    for s in s_list:
        a0, a1, b0, b1 = s - size / 2, s + size / 2, z - size / 2, z + size / 2
        mb.poly(mat, [X(a0, b0, -proud), X(a1, b0, -proud), X(a1, b1, -proud), X(a0, b1, -proud)])
        for (p, q) in [((a0, b1), (a1, b1)), ((a1, b0), (a0, b0)), ((a0, b0), (a0, b1)), ((a1, b1), (a1, b0))]:
            mb.poly(mat, [X(*p, -proud), X(*q, -proud), X(*q, 0.01), X(*p, 0.01)])


def rect_edges(x0, y0, x1, y1):
    """CCW bottom edges of a rectangle: front(-y), right(+x), rear(+y), left(-x)."""
    return {"front": ((x0, y0), (x1, y0)), "right": ((x1, y0), (x1, y1)), "rear": ((x1, y1), (x0, y1)), "left": ((x0, y1), (x0, y0))}


def crown(mb, poly, z0, z1, t=0.25, horns=True, mat="render", horn=0.42):
    """Parapet ring with coping and 'horn' blocks at the corners (Souss kasbah crown)."""
    ring = L.ring_poly(poly, t)
    L.prism(mb, mat, ring, z0, z1)
    L.prism(mb, "trim", ring.buffer(0.03, join_style=2).intersection(poly.buffer(0.03, join_style=2)).difference(poly.buffer(-t - 0.03, join_style=2)), z1, z1 + 0.06)
    if horns:
        for x, y in list(poly.exterior.coords)[:-1]:
            hb = box(x - horn / 2, y - horn / 2, x + horn / 2, y + horn / 2).intersection(poly.buffer(0.02, join_style=2))
            if hb.area > 0.01:
                L.prism(mb, mat, hb, z1 + 0.06, z1 + 0.42)
                L.prism(mb, "trim", hb.buffer(0.03, join_style=2), z1 + 0.42, z1 + 0.48)


def cornice(mb, poly, z0, z1, pd):
    L.prism(mb, "trim", poly.buffer(pd, join_style=2).difference(poly.buffer(-0.05, join_style=2)), z0, z1, bottom=True)


def tower(mb, x0, y0, x1, y1, z_wall, z_top, outer, taper=0.40, panels=True, wall_mat="sienna"):
    """Kasbah tower: battered walls, cornice, parapet with a railing, bejmat panels with an arched
    door and an arched window (mashrabiya screens) on the `outer` faces."""
    E = rect_edges(x0, y0, x1, y1)
    for k, (p, q) in E.items():
        holes = []
        if k in outer and panels:
            holes = [{"s0": -0.70, "s1": 0.70, "z0": 0.20, "z1": 2.60, "shape": "arch", "kind": "glass", "n": 2},
                     {"s0": -0.60, "s1": 0.60, "z0": 4.90, "z1": 7.00, "shape": "arch", "kind": "glass", "n": 2}]
        X = face(mb, wall_mat, p, q, 0.0, z_wall, holes, taper=taper)
        if k in outer and panels:
            panel(mb, "bejmat", X, 1.40, 1.10, 0.20, 8.00, holes)
            screen(mb, X, -1.30, 1.30, 0.20, 1.05, 0.40)
            screen(mb, X, -0.70, 0.70, 4.90, 5.80, 0.35)
            Lb = math.dist(p, q)
            squares(mb, X, [s for s in (-1.8, -0.9, 0.0, 0.9, 1.8) if abs(s) < Lb / 2 - 0.6], z_wall - 1.2)
    top = box(x0 + taper, y0 + taper, x1 - taper, y1 - taper)
    L.prism(mb, "roof", top, z_wall - 0.01, z_wall, sides=False)
    cornice(mb, top, z_wall, z_wall + 0.15, 0.18)
    cornice(mb, top, z_wall + 0.15, z_wall + 0.35, 0.36)
    par = top.buffer(0.10, join_style=2)
    ring = L.ring_poly(par, 0.22)
    # railing in the middle of each parapet face (balustrade on the facades)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    gaps = unary_union([box(cx - 1.0, y0 - 1, cx + 1.0, y1 + 1), box(x0 - 1, cy - 1.0, x1 + 1, cy + 1.0)])
    solid = ring.difference(gaps)
    L.prism(mb, wall_mat, solid, z_wall + 0.35, z_top)
    L.prism(mb, "trim", solid.buffer(0.03, join_style=2).intersection(par.buffer(0.03, join_style=2)), z_top, z_top + 0.06)
    rail = ring.intersection(gaps)
    L.prism(mb, wall_mat, rail, z_wall + 0.35, z_wall + 0.55)
    for g in L.as_polys(rail):
        bx0, by0, bx1, by1 = g.bounds
        along_x = (bx1 - bx0) > (by1 - by0)
        n = int(((bx1 - bx0) if along_x else (by1 - by0)) / 0.12)
        for i in range(n + 1):
            if along_x:
                x = bx0 + (bx1 - bx0) * i / n
                mb.box("bronze", x - 0.015, x + 0.015, (by0 + by1) / 2 - 0.015, (by0 + by1) / 2 + 0.015, z_wall + 0.55, z_top - 0.15)
            else:
                y = by0 + (by1 - by0) * i / n
                mb.box("bronze", (bx0 + bx1) / 2 - 0.015, (bx0 + bx1) / 2 + 0.015, y - 0.015, y + 0.015, z_wall + 0.55, z_top - 0.15)
        L.prism(mb, "bronze", g.buffer(-0.07, join_style=2), z_top - 0.15, z_top - 0.10)


def body_walls(mb, poly, z0, z1, holes_by_edge=None, mat="render"):
    """Straight walls over every CCW edge of `poly`; holes_by_edge maps edge index -> holes."""
    c = list(poly.exterior.coords)
    if not poly.exterior.is_ccw:
        c = c[::-1]
    out = []
    for i, (p, q) in enumerate(zip(c, c[1:])):
        out.append(face(mb, mat, p, q, z0, z1, (holes_by_edge or {}).get(i, ())))
    return out


def edge_index(poly, p, q):
    c = list(poly.exterior.coords)
    if not poly.exterior.is_ccw:
        c = c[::-1]
    for i, (a, b) in enumerate(zip(c, c[1:])):
        if math.dist(a, p) < 0.05 and math.dist(b, q) < 0.05:
            return i
    raise KeyError((p, q))


# ---------------------------------------------------------------------------------------------
# ADMINISTRATION (pavilion)
# ---------------------------------------------------------------------------------------------
TX0, TX1 = 3.755, 9.785
FT = (-7.38, -3.13)          # front towers y
RT = (3.03, 7.37)            # rear towers y
BODY = box(-8.60, -3.18, 8.60, 3.22)
REAR = box(-4.20, 3.22, 4.20, 6.22)
PLATFORM = box(-14.775, -12.18, 14.775, 11.32)
PLATFORM_FULL = box(-14.775, -12.18, 14.775, 13.62)   # platform + the rear bassin strip
PORTAL = box(-2.875, -12.18, 2.875, -6.88)
PASSAGE = box(-2.50, -7.18, 2.50, -3.18)
COUR = box(-12.70, -3.10, -8.62, 3.20)


def pavilion(M, col, rear_bassin=True):
    """rear_bassin=False (client, 13-10): the plan de masse already draws a bassin on that side,
    so the strip behind the rear terrace is paved instead of a second bassin."""
    mb = C.MeshBuilder()
    plat = PLATFORM if rear_bassin else PLATFORM_FULL
    towers = [(-TX1, FT[0], -TX0, FT[1], ("front", "left")), (TX0, FT[0], TX1, FT[1], ("front", "right")),
              (-TX1, RT[0], -TX0, RT[1], ("rear", "left")), (TX0, RT[0], TX1, RT[1], ("rear", "right"))]
    # ---- ground: platform, bassins, bridge, cour anglaise --------------------------------------
    water = unary_union([box(-14.775, -12.18, 14.775, -3.18), box(-14.775, 7.82, -13.815, 11.32), box(13.815, 7.82, 14.775, 11.32)])
    solids = unary_union([box(t[0], t[1], t[2], t[3]) for t in towers] + [PORTAL, PASSAGE, BODY])
    bridge = box(-1.10, -12.18, 1.10, -3.18)
    planters = [box(-8.90, -8.58, -5.40, -7.48), box(5.40, -8.58, 8.90, -7.48)]
    water = water.difference(solids.buffer(0.0)).difference(bridge).difference(unary_union(planters))
    deck = plat.difference(water).difference(COUR).difference(solids.buffer(-0.02))
    L.prism(mb, "terrace", deck, -1.80, 0.20)
    L.prism(mb, "slate", bridge.difference(PORTAL.buffer(-0.40)), 0.20, 0.22, sides=False)
    for w in L.as_polys(water):
        L.prism(mb, "pool_tile", w, -0.60, -0.55, sides=False)
        L.prism(mb, "pool_water", w, -0.12, -0.10, sides=False)
    if rear_bassin:
        L.prism(mb, "pool_tile", box(-14.775, 11.32, 14.775, 13.62).difference(box(-14.575, 11.32, 14.575, 13.42)), -1.80, 0.25)
        L.prism(mb, "pool_tile", box(-14.575, 11.32, 14.575, 13.42), -0.60, -0.55, sides=False)
        L.prism(mb, "pool_water", box(-14.575, 11.32, 14.575, 13.42), -0.12, -0.10, sides=False)
    L.prism(mb, "terrace", plat.buffer(0.15, join_style=2).difference(plat.buffer(-0.15, join_style=2)), -1.80, 0.25)
    for p in planters:
        L.prism(mb, "render_dark", p, -0.60, 0.65)
        L.prism(mb, "lawn", p.buffer(-0.12, join_style=2), 0.60, 0.62, sides=False)
    # cour anglaise: walls down to the sous-sol and a bronze railing
    L.prism(mb, "render", L.ring_poly(COUR, 0.01), -3.20, 0.20)
    L.prism(mb, "terrace", COUR, -3.21, -3.20, sides=False)
    for (a, b) in [((-12.70, -3.10), (-8.62, -3.10)), ((-12.70, 3.20), (-8.62, 3.20)), ((-12.70, -3.10), (-12.70, 3.20))]:
        n = int(math.dist(a, b) / 0.15)
        for i in range(n + 1):
            x = a[0] + (b[0] - a[0]) * i / n
            y = a[1] + (b[1] - a[1]) * i / n
            mb.box("bronze", x - 0.015, x + 0.015, y - 0.015, y + 0.015, 0.20, 1.20)
        mb.box("bronze", min(a[0], b[0]) - 0.03, max(a[0], b[0]) + 0.03, min(a[1], b[1]) - 0.03, max(a[1], b[1]) + 0.03, 1.20, 1.25)

    # ---- body: RDC +0.20..+4.40, etage to +7.85, parapet to +9.20 ----------------------------
    body = unary_union([BODY, REAR])
    holes = {}
    for side, x in (("right", 8.60), ("left", -8.60)):
        p, q = ((8.60, -3.18), (8.60, 3.22)) if side == "right" else ((-8.60, 3.22), (-8.60, -3.18))
        holes[edge_index(body, p, q)] = [
            {"s0": -1.90, "s1": -0.70, "z0": 0.90, "z1": 2.70, "n": 2, "surround": 0.12},
            {"s0": 0.40, "s1": 0.95, "z0": 0.90, "z1": 2.70, "surround": 0.12},
            {"s0": 1.40, "s1": 1.95, "z0": 0.90, "z1": 2.70, "surround": 0.12},
            {"s0": -1.90, "s1": -0.70, "z0": 5.20, "z1": 6.95, "n": 2, "surround": 0.12},
            {"s0": 0.40, "s1": 0.95, "z0": 5.20, "z1": 6.95, "surround": 0.12},
            {"s0": 1.40, "s1": 1.95, "z0": 5.20, "z1": 6.95, "surround": 0.12}]
    holes[edge_index(body, (4.20, 6.22), (-4.20, 6.22))] = [
        {"s0": -2.80, "s1": 2.80, "z0": 0.20, "z1": 3.80, "n": 4},
        {"s0": -2.65, "s1": 2.65, "z0": 5.20, "z1": 7.10, "n": 4}]
    Xs = body_walls(mb, body, 0.0, 7.85, holes)
    rear_X = Xs[edge_index(body, (4.20, 6.22), (-4.20, 6.22))]
    screen(mb, rear_X, -2.65, 2.65, 4.55, 5.20, 0.30)
    for X in Xs:
        squares(mb, X, [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0], 8.45)
    L.prism(mb, "roof", body.buffer(-0.24, join_style=2), 7.84, 7.85, sides=False)
    cornice(mb, body, 7.75, 7.90, 0.10)
    crown(mb, body, 7.85, 9.20, t=0.25)
    # skylight pyramid over the hall (TERRASSE plan, x 47673.7-47677.1)
    sk = box(-1.70, -1.60, 1.70, 1.70)
    L.prism(mb, "trim", L.ring_poly(sk.buffer(0.15, join_style=2), 0.15), 7.85, 8.15)
    cx, cy = 0.0, 0.05
    pts = [(-1.70, -1.60), (1.70, -1.60), (1.70, 1.70), (-1.70, 1.70)]
    for (a, b) in zip(pts, pts[1:] + pts[:1]):
        mb.poly("glass", [(a[0], a[1], 8.15), (b[0], b[1], 8.15), (cx, cy, 9.05)])
        mb.box("bronze", min(a[0], b[0]) - 0.03, max(a[0], b[0]) + 0.03, min(a[1], b[1]) - 0.03, max(a[1], b[1]) + 0.03, 8.12, 8.18)

    # ---- passage (+5.60) and portal (+7.70, beam +6.50, horseshoe arch) ----------------------
    for x0 in (-2.50, 2.20):
        mb.box("render", x0, x0 + 0.30, -6.87, -3.19, 0.0, 5.30)
    mb.box("render", -2.50, 2.50, -6.87, -3.19, 5.30, 5.60)
    mb.box("trim", -2.58, 2.58, -6.87, -3.20, 5.60, 5.68)
    for x0 in (-2.20, 1.90):        # 'mur d'eau' water walls inside the passage
        mb.box("pool_tile", x0, x0 + 0.30, -6.60, -3.60, 0.20, 2.40)
    arch = {"s0": -1.45, "s1": 1.45, "z0": 0.20, "z1": 5.20, "shape": "horseshoe", "kind": "open"}
    Xf = face(mb, "render", (-2.875, -12.18), (2.875, -12.18), 0.0, 7.70, [arch], rev=0.40)
    Xb = face(mb, "render", (2.875, -6.88), (-2.875, -6.88), 0.0, 7.70, [dict(arch)], rev=0.40)
    for X in (Xf, Xb):
        sh = hole_shape(arch)
        fr = sh.buffer(0.38).difference(sh).intersection(box(-3, 0.21, 3, 8))
        for t in L.tri_poly(fr):
            mb.poly("bejmat", [X(s, z, -0.05) for s, z in t])
        squares(mb, X, [-2.0, -1.33, -0.67, 0.0, 0.67, 1.33, 2.0], 6.95)
        for s in (-2.45, 2.25):       # stacked blocks on the pilasters
            for k in range(7):
                z = 0.6 + k * 0.78
                mb.poly("trim", [X(s, z, -0.06), X(s + 0.2, z, -0.06), X(s + 0.2, z + 0.5, -0.06), X(s, z + 0.5, -0.06)])
    for x0 in (-2.875, 2.475):
        face(mb, "render", (x0, -6.88) if x0 < 0 else (x0 + 0.40, -12.18), (x0, -12.18) if x0 < 0 else (x0 + 0.40, -6.88), 0.0, 7.70)
        mb.box("render", x0 + 0.01, x0 + 0.39, -11.78, -7.28, 0.0, 6.50)
    mb.box("render", -2.865, 2.865, -12.17, -6.89, 6.50, 7.69)
    crown(mb, PORTAL.buffer(-0.001, join_style=2), 7.69, 8.10, t=0.25)
    cornice(mb, PORTAL, 7.45, 7.60, 0.10)

    # ---- towers ---------------------------------------------------------------------------------
    for x0, y0, x1, y1, outer in towers:
        tower(mb, x0, y0, x1, y1, 10.90, 12.20, outer)

    # ---- pergolas en bois at the rear corners ---------------------------------------------------
    for s in (-1, 1):
        a, b = sorted((s * 14.40, s * TX1))
        mb.box("timber", a, b, 7.85, 8.05, 4.30, 4.55)
        mb.box("timber", a, b, 11.05, 11.25, 4.30, 4.55)
        n = int((b - a) / 0.30)
        for i in range(n + 1):
            x = a + (b - a - 0.08) * i / n
            mb.box("timber", x, x + 0.08, 7.85, 11.25, 4.55, 4.65)
        px = s * 14.25
        for y in (7.95, 11.15):
            mb.box("timber", px - 0.08, px + 0.08, y - 0.08, y + 0.08, 0.20, 4.30)

    obs = mb.build("ADM", col, M)
    ob = L.join(obs, "SRC_ADMINISTRATION")
    L.weld(ob, 0.0003)
    return ob


# ---------------------------------------------------------------------------------------------
# BOUTIQUE / RESTAURANT (market)
# ---------------------------------------------------------------------------------------------
MK_TOWERS = [(-11.2, 1.05, -6.2, 6.15, ("rear", "left")), (-11.2, -6.15, -6.2, -1.05, ("front", "left"))]
MK_BLOCKS = [(-2.6, 0.95, 2.4, 6.15), (-2.6, -6.15, 2.4, -0.95), (6.0, 0.95, 11.2, 6.15), (6.0, -6.15, 11.2, -0.95)]
MK_ALL = box(-11.2, -6.15, 11.2, 6.15)
MK_SKY = [box(-6.0, 0.95, -2.7, 4.35), box(2.7, 0.95, 5.8, 4.35)]


def market(M, col, name="SRC_MARKET"):
    mb = C.MeshBuilder()
    L.prism(mb, "terrace", MK_ALL.buffer(1.2, join_style=2), -1.20, 0.20)
    # links at +6.20: the whole footprint except blocks and towers
    blocks = [box(*b) for b in MK_BLOCKS]
    towers = [box(*t[:4]) for t in MK_TOWERS]
    link = MK_ALL.difference(unary_union(blocks + towers).buffer(-0.01, join_style=2))
    link_out = MK_ALL.difference(unary_union(blocks + towers))
    # shopfronts on the long faces of the links (+6.20 bodies: large glazing on the facades)
    for p in L.as_polys(link_out):
        c = list(p.exterior.coords)
        if not p.exterior.is_ccw:
            c = c[::-1]
        for a, b in zip(c, c[1:]):
            on_out = (abs(a[1] - b[1]) < 1e-6 and abs(abs(a[1]) - 6.15) < 0.12) or (abs(a[0] - b[0]) < 1e-6 and abs(abs(a[0]) - 11.2) < 0.01)
            if not on_out:
                continue
            Lg = math.dist(a, b)
            hs = [{"s0": -Lg / 2 + 0.45, "s1": Lg / 2 - 0.45, "z0": 0.20, "z1": 3.20, "n": 3, "surround": 0.15}] if Lg > 2.0 else []
            X = face(mb, "render", a, b, 0.0, 6.20, hs)
            squares(mb, X, [s for s in (-1.4, -0.7, 0.0, 0.7, 1.4) if abs(s) < Lg / 2 - 0.3], 4.6)
    L.prism(mb, "roof", link.buffer(-0.2, join_style=2), 6.19, 6.20, sides=False)
    for b in blocks:
        x0, y0, x1, y1 = b.bounds
        E = rect_edges(x0, y0, x1, y1)
        for k, (p, q) in E.items():
            on_out = (k == "front" and y0 < -6.1) or (k == "rear" and y1 > 6.1) or (k == "right" and x1 > 11.1)
            hs = []
            if on_out:
                hs = [{"s0": -1.55, "s1": -0.85, "z0": 0.80, "z1": 3.00, "surround": 0.12},
                      {"s0": -0.35, "s1": 0.35, "z0": 0.80, "z1": 3.00, "surround": 0.12},
                      {"s0": 0.85, "s1": 1.55, "z0": 0.80, "z1": 3.00, "surround": 0.12}]
            X = face(mb, "render", p, q, 0.0 if on_out else 6.20, 8.16, hs)
            if on_out:
                squares(mb, X, [-1.6, -0.8, 0.0, 0.8, 1.6], 4.55)
        L.prism(mb, "roof", b.buffer(-0.25, join_style=2), 8.15, 8.16, sides=False)
        cornice(mb, b, 7.55, 7.75, 0.12)
        cornice(mb, b, 3.70, 3.85, 0.08)
        crown(mb, b, 8.16, 8.70, t=0.25)
    for p in L.as_polys(link_out):
        L.prism(mb, "trim", L.ring_poly(p.buffer(0.04, join_style=2), 0.30).difference(unary_union(blocks + towers)), 6.20, 6.28)
    for t in MK_TOWERS:
        tower(mb, t[0], t[1], t[2], t[3], 10.70, 12.00, t[4])
    for s in MK_SKY:
        x0, y0, x1, y1 = s.bounds
        L.prism(mb, "trim", L.ring_poly(s, 0.15), 6.20, 6.50)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        pts = [(x0 + 0.15, y0 + 0.15), (x1 - 0.15, y0 + 0.15), (x1 - 0.15, y1 - 0.15), (x0 + 0.15, y1 - 0.15)]
        for (a, b) in zip(pts, pts[1:] + pts[:1]):
            mb.poly("glass", [(a[0], a[1], 6.50), (b[0], b[1], 6.50), (cx, cy, 7.40)])
    obs = mb.build("MKT", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    return ob


# ---------------------------------------------------------------------------------------------
# hipped-roof buildings (club, kiosks) and the station, from plan-de-masse outlines
# ---------------------------------------------------------------------------------------------
def hipped(M, col, name, poly, wall_h=3.40, pitch=30.0, wall_mat="render"):
    """Single-storey building on the minimum rectangle of `poly` (local coords already), hipped
    terracotta roof with 0.40 m eaves."""
    mb = C.MeshBuilder()
    r = poly.minimum_rotated_rectangle
    q = list(r.exterior.coords)[:4]
    e1 = (q[1][0] - q[0][0], q[1][1] - q[0][1])
    ang = math.atan2(e1[1], e1[0])
    cx, cy = r.centroid.x, r.centroid.y
    loc = affinity.rotate(affinity.translate(r, -cx, -cy), -ang, origin=(0, 0), use_radians=True)
    x0, y0, x1, y1 = loc.bounds
    hs = []
    E = rect_edges(x0, y0, x1, y1)
    for k, (p, qq) in E.items():
        Lg = math.dist(p, qq)
        n = max(1, int(Lg / 3.2))
        holes = [{"s0": -Lg / 2 + (i + 0.5) * Lg / n - 0.6, "s1": -Lg / 2 + (i + 0.5) * Lg / n + 0.6, "z0": 0.9 if k != "front" or i else 0.2,
                  "z1": 2.6, "n": 2, "surround": 0.10} for i in range(n)]
        face(mb, wall_mat, p, qq, 0.0, wall_h, holes)
    L.prism(mb, "terrace", loc.buffer(1.0, join_style=2), -1.0, 0.15)
    ex = 0.40
    X0, Y0, X1, Y1 = x0 - ex, y0 - ex, x1 + ex, y1 + ex
    W, D = X1 - X0, Y1 - Y0
    h = min(W, D) / 2 * math.tan(math.radians(pitch))
    zr = wall_h
    if W >= D:
        r0, r1 = (X0 + D / 2, (Y0 + Y1) / 2), (X1 - D / 2, (Y0 + Y1) / 2)
    else:
        r0, r1 = ((X0 + X1) / 2, Y0 + W / 2), ((X0 + X1) / 2, Y1 - W / 2)
    A, B, Cc, Dd = (X0, Y0, zr), (X1, Y0, zr), (X1, Y1, zr), (X0, Y1, zr)
    R0, R1 = (r0[0], r0[1], zr + h), (r1[0], r1[1], zr + h)
    if W >= D:
        faces = [[A, B, R1, R0], [Cc, Dd, R0, R1], [Dd, A, R0], [B, Cc, R1]]
    else:
        faces = [[B, Cc, R1, R0], [Dd, A, R0, R1], [A, B, R0], [Cc, Dd, R1]]
    for f in faces:
        mb.poly("roof_tiles", f, [(p[0] + p[1], p[2] * 1.5) for p in f])
    mb.poly("trim", [A, Dd, Cc, B])
    L.prism(mb, "trim", loc.buffer(ex, join_style=2).difference(loc.buffer(-0.05, join_style=2)), zr - 0.18, zr)
    obs = mb.build(name, col, M)
    ob = L.join(obs, name)
    ob.location = (cx, cy, 0.0)
    ob.rotation_euler = (0, 0, ang)
    return ob


def kiosk(M, col, name, size, h=3.20):
    """Flat-roofed square kiosk (gatehouse): the plan draws a plain square with a double outline,
    like the other flat-roofed blocks, no hips. Door on local -y, windows on the other faces,
    cornice, crown with corner horns. Height INFERRED (3.20 m)."""
    mb = C.MeshBuilder()
    a = size / 2
    E = rect_edges(-a, -a, a, a)
    for k, (p, q) in E.items():
        if k == "front":
            hs = [{"s0": -0.50, "s1": 0.50, "z0": 0.15, "z1": 2.30, "kind": "door", "surround": 0.12}]
        else:
            hs = [{"s0": -0.45, "s1": 0.45, "z0": 1.05, "z1": 2.30, "surround": 0.12}]
        X = face(mb, "render", p, q, 0.0, h, hs)
        squares(mb, X, [-1.2, -0.6, 0.0, 0.6, 1.2], h - 0.55)
    sq = box(-a, -a, a, a)
    L.prism(mb, "roof", sq.buffer(-0.2, join_style=2), h - 0.01, h, sides=False)
    cornice(mb, sq, h - 0.30, h - 0.15, 0.08)
    crown(mb, sq, h, h + 0.45, t=0.20)
    obs = mb.build(name, col, M)
    return L.join(obs, name)


def station(M, col, name, poly, h=3.00):
    mb = C.MeshBuilder()
    poly = poly.buffer(0)
    L.prism(mb, "render_dark", L.ring_poly(poly, 0.25), -1.0, h)
    L.prism(mb, "trim", L.ring_poly(poly.buffer(0.03, join_style=2), 0.31), h, h + 0.06)
    L.prism(mb, "terrace", poly.buffer(-0.25), 0.0, 0.10, sides=False)
    obs = mb.build(name, col, M)
    return L.join(obs, name)
