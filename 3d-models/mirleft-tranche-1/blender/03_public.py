"""
03_public — public buildings of the 1er TRANCHE (plan de masse 12-10), exterior only.

RESTAURANT   block 'dfhgfdjjj' in 'RESTAURANT MIRLEFT': the restaurant pavilion of
             3-PLAN_RESTAURANT_PAVILLON.DWG redrawn more compact on the 12-10 plan. Footprint read
             from the block: four battered corner towers (5.56 x 3.9 m), central body with the roof
             terrace at +8.10 ('TERRASSE'), passage and portal at +5.70, rear block, two timber
             pergolas at the rear corners; the two front bassins with planters come from the plan
             hatches (scene script). Tower height (+12.20), crowns, arches, bejmat panels and
             mashrabiya screens from the pavilion permit; the rear block height (+5.70) is INFERRED.
COMMERCES    'COMMERCES MIRLEFT': Commerce 1 (superette) and Commerce 2 (glacier), towers ('départ
             tours'), bodies, light wells to the sous-sol ('vide d'aération sous sol'), the stair down
             on the south and the external stair of Commerce 2. Heights are not on the drawings:
             single storey to +4.40 with a crown to +5.20, towers to +8.10 (INFERRED, the pavilion's
             proportions).
TOILETTE     the 3 x 3 m block on the plaza: flat-roofed kiosk, 3.20 m (INFERRED height).
LOCAL TECHNIQUE  walls of the pool block (toilettes, local technique, bâche à eau), 3.00 m (INFERRED).
PETANQUE     timber pergola (posts, beams, slats as drawn), court edgings, benches.

Local frames: metres, origin at the building centre, front (access) towards -y, z = 0 at the pad.
"""
import math

from shapely.geometry import LineString, Point, Polygon, box
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




# ---------------------------------------------------------------------------------------------
# generic flat-roofed kasbah block: walls with openings chosen per face, cornice, crown
# ---------------------------------------------------------------------------------------------
def ccw_edges(poly):
    c = list(poly.exterior.coords)
    if not poly.exterior.is_ccw:
        c = c[::-1]
    return list(zip(c, c[1:]))


def block(mb, poly, h, rule, crown_h=0.80, mat="render", horns=True, squares_z=None):
    """rule(p, q, nx, ny, length) -> holes for that face (s from the face centre)."""
    for p, q in ccw_edges(poly):
        Lg = math.dist(p, q)
        if Lg < 0.05:
            continue
        ux, uy = (q[0] - p[0]) / Lg, (q[1] - p[1]) / Lg
        X = face(mb, mat, p, q, 0.0, h, rule(p, q, uy, -ux, Lg) if Lg > 1.0 else ())
        if squares_z and Lg > 2.4:
            n = int((Lg - 1.0) / 0.8)
            squares(mb, X, [(-(n - 1) / 2 + k) * 0.8 for k in range(n)], squares_z)
    L.prism(mb, "roof", poly.buffer(-0.20, join_style=2), h - 0.01, h, sides=False)
    cornice(mb, poly, h - 0.30, h - 0.15, 0.08)
    if crown_h:
        crown(mb, poly, h, h + crown_h, t=0.25, horns=horns)


def windows(Lg, z0, z1, w=0.70, gap=1.60, n_max=6, surround=0.12):
    n = max(1, min(n_max, int((Lg - 0.8) / gap)))
    if Lg < 1.6:
        return []
    return [{"s0": (-(n - 1) / 2 + k) * gap - w / 2, "s1": (-(n - 1) / 2 + k) * gap + w / 2, "z0": z0, "z1": z1, "surround": surround}
            for k in range(n)]


# ---------------------------------------------------------------------------------------------
# RESTAURANT (12-10 block 'dfhgfdjjj'; local x = X - 2327.925, y = Y - 1443.41, front = bassins = -y)
# ---------------------------------------------------------------------------------------------
R_TOWERS = [(-8.315, -6.06, -2.755, -2.12, ("front", "left")), (2.765, -6.06, 8.315, -2.12, ("front", "right")),
            (-8.315, 2.12, -2.755, 5.97, ("rear", "left")), (2.765, 2.12, 8.315, 5.97, ("rear", "right"))]
R_BODY = unary_union([box(-7.395, -2.12, 7.395, 2.12), box(-2.755, -2.12, 2.765, 5.05)])
R_PASSAGE = box(-2.755, -5.21, 2.765, -2.12)
R_PORTAL = box(-2.20, -10.01, 2.20, -5.21)
R_REAR = box(-2.725, 5.05, 2.775, 10.89)
R_PERGOLAS = [(-8.525, 6.49, -3.325, 10.79), (3.475, 6.49, 8.675, 10.79)]
R_FOOT = unary_union([box(*t[:4]).buffer(0.25, join_style=2) for t in R_TOWERS] + [R_BODY, R_PASSAGE, R_PORTAL, R_REAR])


def restaurant(M, col, name="SRC_RESTAURANT"):
    mb = C.MeshBuilder()
    L.prism(mb, "terrace", R_FOOT.buffer(0.30, join_style=2), -1.20, 0.20)
    # ---- body: RDC + etage, roof terrace +8.10 ('TERRASSE'), crown to +9.20 ----------------------
    def body_rule(p, q, nx, ny, Lg):
        if abs(nx) > 0.9 and Lg > 3.0:                      # side faces between front and rear towers
            return windows(Lg, 0.90, 2.70, w=0.60, gap=1.30, n_max=2) + windows(Lg, 5.20, 6.95, w=0.60, gap=1.30, n_max=2)
        if ny < -0.9:                                       # entrance at the back of the passage
            return [{"s0": -1.40, "s1": 1.40, "z0": 0.20, "z1": 3.60, "n": 4}]
        return []
    block(mb, R_BODY, 8.10, body_rule, crown_h=1.10, squares_z=8.55)
    # ---- passage (+5.70) with the 'murs d'eau' -----------------------------------------------------
    x0, y0, x1, y1 = R_PASSAGE.bounds
    mb.box("render", x0, x1, y0, y1, 5.30, 5.70)
    mb.box("trim", x0 - 0.06, x1 + 0.06, y0 - 0.06, y1, 5.70, 5.78)
    for xa in (x0 + 0.02, x1 - 0.32):
        mb.box("pool_tile", xa, xa + 0.30, y0 + 0.25, y1 - 0.30, 0.20, 2.40)
    # ---- portal (+5.70): horseshoe arch front and back, bejmat surround ---------------------------
    x0, y0, x1, y1 = R_PORTAL.bounds
    arch = {"s0": -1.25, "s1": 1.25, "z0": 0.20, "z1": 4.35, "shape": "horseshoe", "kind": "open"}
    Xf = face(mb, "render", (x0, y0), (x1, y0), 0.0, 5.70, [arch], rev=0.40)
    Xb = face(mb, "render", (x1, y1), (x0, y1), 0.0, 5.70, [dict(arch)], rev=0.40)
    for X in (Xf, Xb):
        sh = hole_shape(arch)
        fr = sh.buffer(0.34).difference(sh).intersection(box(-3, 0.21, 3, 6))
        for t in L.tri_poly(fr):
            mb.poly("bejmat", [X(s, z, -0.05) for s, z in t])
        squares(mb, X, [-1.6, -0.8, 0.0, 0.8, 1.6], 5.05)
    for xa in (x0, x1 - 0.40):
        face(mb, "render", (xa, y1) if xa < 0 else (xa + 0.40, y0), (xa, y0) if xa < 0 else (xa + 0.40, y1), 0.0, 5.70)
        mb.box("render", xa + 0.01, xa + 0.39, y0 + 0.40, y1 - 0.40, 0.0, 5.20)
    mb.box("render", x0 + 0.01, x1 - 0.01, y0 + 0.01, y1 - 0.01, 5.20, 5.69)
    crown(mb, R_PORTAL.buffer(-0.001, join_style=2), 5.69, 6.10, t=0.25)
    cornice(mb, R_PORTAL, 5.45, 5.60, 0.10)
    # ---- rear block (+5.70, INFERRED height): rear glazing, side windows -------------------------
    def rear_rule(p, q, nx, ny, Lg):
        if ny > 0.9:
            return [{"s0": -1.80, "s1": 1.80, "z0": 0.20, "z1": 3.40, "n": 4}]
        if abs(nx) > 0.9:
            return windows(Lg, 0.90, 2.90, w=0.70, gap=1.70, n_max=3)
        return []
    block(mb, R_REAR, 5.70, rear_rule, crown_h=0.55, squares_z=5.10)
    # ---- towers (+12.20) ----------------------------------------------------------------------------
    for x0, y0, x1, y1, outer in R_TOWERS:
        tower(mb, x0 - 0.25, y0 - 0.25, x1 + 0.25, y1 + 0.25, 10.90, 12.20, outer, taper=0.45)
    # ---- timber pergolas at the rear corners (slats every 0.55 m as drawn) -----------------------
    for x0, y0, x1, y1 in R_PERGOLAS:
        for y in (y0 + 0.10, y1 - 0.40):
            mb.box("timber", x0, x1, y - 0.10, y + 0.10, 4.30, 4.55)
        n = int((x1 - x0) / 0.55)
        for i in range(n + 1):
            x = x0 + (x1 - x0 - 0.08) * i / n
            mb.box("timber", x, x + 0.08, y0, y1, 4.55, 4.65)
        for px in (x0 + 0.15, x1 - 0.15):
            for py in (y0 + 0.10, y1 - 0.40):
                mb.box("timber", px - 0.08, px + 0.08, py - 0.08, py + 0.08, -1.50, 4.30)
    obs = mb.build("RST", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    return ob


# ---------------------------------------------------------------------------------------------
# COMMERCES (frame: centre DWG (252049.5, 119448), rotated -9.46 deg; x east, y north;
# entrances on the east side, from the plan's arrows)
# ---------------------------------------------------------------------------------------------
C_TOWERS = [(-5.40, 4.90, -2.00, 10.05, ("left", "rear")), (2.60, 4.80, 6.00, 9.95, ("right", "rear")),
            (-5.60, -13.15, -2.20, -7.65, ("left", "front")), (2.40, -13.10, 5.85, -7.55, ("right", "front"))]
C_NORTH = box(-1.15, 10.05, 1.75, 14.55)
C2_BODY = unary_union([box(-4.15, 0.80, 5.70, 10.05), box(-4.40, -3.75, 5.70, 0.80), box(4.55, 1.20, 6.10, 4.00)])
C1_BODY = box(-4.10, -11.85, 4.30, -3.75)
C_WELLS = [box(-6.00, -7.10, -4.10, -3.75), box(4.30, -7.10, 6.30, -3.75)]
C_STAIRS = [("south", box(-1.75, -13.85, 2.05, -12.30)), ("north", box(-5.05, 10.05, -2.10, 14.60))]
C_FOOT = unary_union([box(*t[:4]) for t in C_TOWERS] + [C_NORTH, C2_BODY, C1_BODY])


def commerces(M, col, name="SRC_COMMERCES"):
    mb = C.MeshBuilder()
    towers = unary_union([box(*t[:4]) for t in C_TOWERS])
    L.prism(mb, "terrace", C_FOOT.buffer(0.15, join_style=2).difference(unary_union(C_WELLS)), -1.20, 0.20)

    def rule(p, q, nx, ny, Lg):
        if nx > 0.9 and Lg > 3.0:                    # east: shopfront with the entrance (glacier)
            return [{"s0": -min(2.2, Lg / 2 - 0.5), "s1": min(2.2, Lg / 2 - 0.5), "z0": 0.20, "z1": 3.20, "n": 4, "surround": 0.15}]
        if Lg > 2.0:
            return windows(Lg, 1.00, 2.90, w=0.80, gap=1.80, n_max=4)
        return []
    for body in (C2_BODY.difference(towers), C1_BODY.difference(towers), C_NORTH):
        for pg in L.as_polys(body):
            block(mb, pg, 4.40, rule, crown_h=0.80, squares_z=3.90)
    for x0, y0, x1, y1, outer in C_TOWERS:
        tower(mb, x0 - 0.20, y0 - 0.20, x1 + 0.20, y1 + 0.20, 7.20, 8.10, outer, taper=0.35)
    # light wells to the sous-sol: walls down, floor, bronze railing
    for w in C_WELLS:
        L.prism(mb, "render", L.ring_poly(w, 0.01), -3.20, 0.20)
        L.prism(mb, "terrace", w, -3.21, -3.20, sides=False)
        railing(mb, w, 0.20, 1.20)
    # stairs down to the sous-sol (interpreted from the plan's stair runs): treads in a pit with a
    # guard wall (1.00 m) around it
    for kind, s in C_STAIRS:
        x0, y0, x1, y1 = s.bounds
        if kind == "south":                          # straight run, 9 risers, top at the east end
            pit = s
            for i in range(9):
                L.prism(mb, "terrace", box(x1 - (x1 - x0) * (i + 1) / 9, y0, x1 - (x1 - x0) * i / 9, y1), -3.0, -0.17 * (i + 1))
        else:                                        # L-shaped run: 6 risers west, landing, 8 risers south
            xm, ym = x0 + 0.90, 13.00
            pit = unary_union([box(x0, y0, xm, y1), box(x0, 13.65, x1, y1)])
            for i in range(6):
                L.prism(mb, "terrace", box(x1 - (x1 - xm) * (i + 1) / 6, 13.65, x1 - (x1 - xm) * i / 6, y1), -3.0, -0.17 * (i + 1))
            L.prism(mb, "terrace", box(x0, ym, xm, y1), -3.0, -0.17 * 7)
            for j in range(8):
                L.prism(mb, "terrace", box(x0, ym - (ym - y0) * (j + 1) / 8, xm, ym - (ym - y0) * j / 8), -3.0, -0.17 * (8 + j))
        L.prism(mb, "render", pit.buffer(0.15, join_style=2).difference(pit).difference(C_FOOT), -3.0, 1.00)
        L.prism(mb, "trim", pit.buffer(0.18, join_style=2).difference(pit.buffer(-0.03, join_style=2)).difference(C_FOOT), 1.00, 1.06)
    obs = mb.build("COM", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    return ob


def railing(mb, poly, z0, z1, step=0.13):
    ring = list(poly.exterior.coords)
    for a, b in zip(ring, ring[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for i in range(n + 1):
            x = a[0] + (b[0] - a[0]) * i / n
            y = a[1] + (b[1] - a[1]) * i / n
            mb.box("bronze", x - 0.015, x + 0.015, y - 0.015, y + 0.015, z0, z1)
        mb.box("bronze", min(a[0], b[0]) - 0.03, max(a[0], b[0]) + 0.03, min(a[1], b[1]) - 0.03, max(a[1], b[1]) + 0.03, z1, z1 + 0.05)


# ---------------------------------------------------------------------------------------------
# LOCAL TECHNIQUE of the pool (walls from the plan, local = world coords minus the pad origin)
# ---------------------------------------------------------------------------------------------
def local_technique(M, col, walls, h=3.00, name="LOCAL_TECHNIQUE_PISCINE"):
    mb = C.MeshBuilder()
    w = unary_union(walls).buffer(0.0)
    L.prism(mb, "render", w, -0.30, h)
    hull = w.convex_hull
    L.prism(mb, "roof", hull, h - 0.15, h)
    cornice(mb, hull, h - 0.35, h - 0.20, 0.06)
    crown(mb, hull.simplify(0.05), h, h + 0.45, t=0.20)
    obs = mb.build(name, col, M)
    return L.join(obs, name)


# ---------------------------------------------------------------------------------------------
# PETANQUE (frame: centre DWG (252088, 119445), rotated -10.5 deg)
# ---------------------------------------------------------------------------------------------
P_COURTS = [box(-8.40, -8.90, -5.40, 0.95), box(-4.00, -8.90, -1.00, 0.95)]
P_PERGOLA = (-9.60, 10.20, -1.60, 14.20)
P_BENCHES = [box(-0.30, 6.80, 0.40, 7.80), box(-0.30, 2.80, 0.40, 3.60), box(-0.30, -1.40, 0.40, -0.60)]


def petanque(M, col, zf=None, name="PETANQUE"):
    """zf(x, y): height of the graded ground above the object's origin (local coords)."""
    zf = zf or (lambda x, y: 0.0)
    mb = C.MeshBuilder()
    for c in P_COURTS:
        L.prism(mb, "sand", c.buffer(-0.08, join_style=2), 0.02, 0.09, zf=zf, sides=False)
        L.prism(mb, "timber", L.ring_poly(c, 0.08), -0.10, 0.20, zf=zf)
    x0, y0, x1, y1 = P_PERGOLA
    zp = zf((x0 + x1) / 2, (y0 + y1) / 2)
    for px in (-9.50, -5.60, -1.70):
        for py in (10.35, 14.05):
            mb.box("timber", px - 0.08, px + 0.08, py - 0.08, py + 0.08, zf(px, py) - 0.60, zp + 2.80)
    for py in (10.35, 12.25, 14.05):
        mb.box("timber", x0, x1, py - 0.08, py + 0.08, zp + 2.80, zp + 3.05)
    n = int((x1 - x0) / 0.40)
    for i in range(n + 1):
        x = x0 + (x1 - x0 - 0.05) * i / n
        mb.box("timber", x, x + 0.05, y0, y1, zp + 3.05, zp + 3.15)
    for b in P_BENCHES:
        L.prism(mb, "stone", b, -0.30, 0.45, zf=zf)
    obs = mb.build(name, col, M)
    return L.join(obs, name)
