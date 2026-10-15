"""
03_public — public buildings of the 1er TRANCHE (plan de masse 12-10), exterior only.

RESTAURANT   the pavilion of 3-PLAN_RESTAURANT_PAVILLON.DWG (15-10 request), as modelled for Tranche
             A+B: plans RDC / ETAGE / TERRASSE-MASSE, four facades, coupes A-A, B-B, C-C. Four
             tapered corner towers to +12.20 (terre de sienne, bejmat panels), body to +9.20 (etage
             +4.40, roof +7.85), portal with a horseshoe arch to +7.70, passage with water walls
             (+5.60), skylight, front and rear bassins, bridge, planters, cour anglaise, timber
             pergolas at the rear corners. Placed on the axis of the 12-10 block 'dfhgfdjjj', its
             platform inside the plan's TERRASSE RESTAURANT (scene script).
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
    if kind == "poly":                 # outline read from the elevations (s, z)
        return Polygon(h["pts"])
    if kind == "horseshoe":            # circle wider than the jambs, centre at the springing
        R = w / 2 * 1.16
        zc = z1 - R
        return unary_union([box(s0, z0, s1, zc), Point(sc, zc).buffer(R, 40).intersection(box(sc - R, zc - R * 0.55, sc + R, z1))])
    raise ValueError(kind)


def stepped(half):
    """Closed outline from its right half [(s, z) bottom to top], mirrored about s = 0."""
    return list(half) + [(-x, z) for x, z in reversed(half)]


# FACADE PRINCIPALE (3-PLAN_RESTAURANT_PAVILLON), read off the drawing in metres (z = level, +0.20 deck)
# tower windows: two leaves under a stepped head (three steps each side), in a plain surround
WIN_LOW = stepped([(0.648, 1.426), (0.648, 1.684), (0.582, 1.789), (0.582, 2.002), (0.497, 2.120), (0.497, 2.396),
                   (0.418, 2.530), (0.418, 2.688)])
WIN_UP = stepped([(0.431, 6.096), (0.431, 6.533), (0.387, 6.603), (0.387, 6.745), (0.331, 6.824), (0.331, 7.008),
                  (0.278, 7.097), (0.278, 7.202)])
SURR_LOW = box(-0.748, 1.426, 0.748, 3.026)
SURR_UP = box(-0.498, 6.096, 0.498, 7.427)
# portal arch (front and sides alike): pointed horseshoe, jambs 2.40 m apart with a notch at the
# springing, 2.48 m at its widest, apex at +4.79; half-widths every 0.10 m
ARCH_HALF = [(0.20, 1.200), (1.80, 1.200), (1.90, 1.187), (2.00, 1.126), (2.10, 1.098), (2.20, 1.080), (2.30, 1.084),
             (2.40, 1.111), (2.50, 1.163), (2.60, 1.193), (2.70, 1.211), (2.80, 1.226), (2.90, 1.237), (3.00, 1.242),
             (3.10, 1.240), (3.20, 1.234), (3.30, 1.220), (3.40, 1.202), (3.50, 1.179), (3.60, 1.154), (3.70, 1.116),
             (3.80, 1.071), (3.90, 1.024), (4.00, 0.968), (4.10, 0.900), (4.20, 0.831), (4.30, 0.740), (4.40, 0.641),
             (4.50, 0.523), (4.60, 0.389), (4.70, 0.219), (4.79, 0.0)]
ARCH_PTS = [(w, z) for z, w in ARCH_HALF[:-1]] + [(0.0, 4.79)] + [(-w, z) for z, w in reversed(ARCH_HALF[:-1])]
# its frame: two mouldings and a bejmat field, three nested rectangles from the deck
ARCH_FRAMES = [box(-1.807, 0.20, 1.807, 5.825), box(-1.636, 0.20, 1.636, 5.634), box(-1.464, 0.20, 1.464, 5.410)]


def relief(mb, mat, X, poly, d):
    """Flat relief on a face (X from face()): poly in (s, z) standing d proud, with its edges."""
    for pg in L.as_polys(poly):
        for t in L.tri_poly(pg):
            mb.poly(mat, [X(s, z, -d) for s, z in t])
        for ring in [pg.exterior] + list(pg.interiors):
            c = list(ring.coords)
            for (sa, za), (sb, zb) in zip(c, c[1:]):
                mb.poly(mat, [X(sa, za, 0.0), X(sb, zb, 0.0), X(sb, zb, -d), X(sa, za, -d)])


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
            if rev > 0:                                   # reveal (rev = 0: the inner face of a wall)
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
        if k in outer and panels:                  # windows of FACADE PRINCIPALE, both levels
            holes = [{"s0": -0.648, "s1": 0.648, "z0": 1.426, "z1": 2.688, "shape": "poly", "pts": WIN_LOW, "kind": "glass", "n": 2},
                     {"s0": -0.431, "s1": 0.431, "z0": 6.096, "z1": 7.202, "shape": "poly", "pts": WIN_UP, "kind": "glass", "n": 2}]
        X = face(mb, wall_mat, p, q, 0.0, z_wall, holes, taper=taper)
        if k in outer and panels:
            # bejmat panel (trapezoid 2.79 -> 2.11 m, +0.43 to +8.21) with the plain window surrounds
            panel(mb, "bejmat", X, 1.395, 1.056, 0.426, 8.21, [{"s0": -0.748, "s1": 0.748, "z0": 1.426, "z1": 3.026},
                                                             {"s0": -0.498, "s1": 0.498, "z0": 6.096, "z1": 7.427}])
            for sr, w in ((SURR_LOW, WIN_LOW), (SURR_UP, WIN_UP)):
                relief(mb, "trim", X, sr.difference(Polygon(w)), 0.03)
            screen(mb, X, -1.30, 1.30, 0.426, 1.426, 0.40)        # mashrabiya planter under the low window
            screen(mb, X, -0.70, 0.70, 5.426, 6.096, 0.35)        # mashrabiya balcony under the high one
            relief(mb, "trim", X, box(-0.72, 5.226, 0.72, 5.426), 0.40)
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
# RESTAURANT: the pavilion of 3-PLAN_RESTAURANT_PAVILLON.DWG (plans RDC / ETAGE / TERRASSE, facades,
# coupes), as built for Tranche A+B; placed on the axis of the 12-10 block 'dfhgfdjjj' (scene script)
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


def pavilion(M, col, rear_bassin=False, name="SRC_RESTAURANT", plinth=-1.80, cour=False):
    """The pavilion with its platform: front bassins and planters, bridge, cour anglaise, rear terrace,
    timber pergolas at the rear corners. rear_bassin: the plan's water behind it (the strip along the
    rear and the two by the pergolas), left out at the client's request (15-10): the deck covers it.
    cour: the plan's cour anglaise (sunken court with a railing on the left side), left out at the
    client's request (15-10): the deck covers it.
    plinth: depth of the platform's base below the pad, down to the lowest ground under its edge."""
    mb = C.MeshBuilder()
    plat = PLATFORM if rear_bassin else PLATFORM_FULL
    towers = [(-TX1, FT[0], -TX0, FT[1], ("front", "left")), (TX0, FT[0], TX1, FT[1], ("front", "right")),
              (-TX1, RT[0], -TX0, RT[1], ("rear", "left")), (TX0, RT[0], TX1, RT[1], ("rear", "right"))]
    # ---- ground: platform, bassins, bridge, cour anglaise --------------------------------------
    water = unary_union([box(-14.775, -12.18, 14.775, -3.18)]
                        + ([box(-14.775, 7.82, -13.815, 11.32), box(13.815, 7.82, 14.775, 11.32)] if rear_bassin else []))
    solids = unary_union([box(t[0], t[1], t[2], t[3]) for t in towers] + [PORTAL, PASSAGE, BODY])
    bridge = box(-1.10, -12.18, 1.10, -3.18)
    planters = [box(-8.90, -8.58, -5.40, -7.48), box(5.40, -8.58, 8.90, -7.48)]
    water = water.difference(solids.buffer(0.0)).difference(bridge).difference(unary_union(planters))
    # the deck runs 2 cm under the walls and planters; kept 5 mm off the water so that its edge never lies
    # in the plane of a wall face (coplanar faces render as a black band)
    deck = plat.difference(water.buffer(0.005, join_style=2)).difference(COUR if cour else Polygon()).difference(solids.buffer(-0.02))
    deck = deck.difference(unary_union(planters).buffer(-0.02, join_style=2))
    L.prism(mb, "terrace", deck, plinth, 0.20)
    L.prism(mb, "slate", bridge, 0.20, 0.22, sides=False)
    # inside the portal: the bridge runs through, 'Bassin' each side of it (RDC plan), under the arches
    inner = PORTAL.buffer(-0.40, join_style=2)
    L.prism(mb, "terrace", bridge.intersection(PORTAL.buffer(-0.02, join_style=2)), plinth, 0.20)
    L.prism(mb, "pool_tile", inner.difference(bridge), -0.60, -0.55, sides=False)
    L.prism(mb, "pool_water", inner.difference(bridge), -0.12, -0.10, sides=False)
    L.prism(mb, "render", PORTAL.difference(inner), -0.60, 0.0)
    L.prism(mb, "terrace", box(-2.20, -6.90, 2.20, -3.20), plinth, 0.20)      # floor of the passage
    for w in L.as_polys(water):
        L.prism(mb, "pool_tile", w, -0.60, -0.55, sides=False)
        L.prism(mb, "pool_water", w, -0.12, -0.10, sides=False)
    if rear_bassin:
        rim = box(-14.775, 11.32, 14.775, 13.62).difference(box(-14.575, 11.32, 14.575, 13.42))
        L.prism(mb, "stone", rim, plinth, 0.25)                    # its outer face is the platform's base
        L.prism(mb, "deck_stone", rim.buffer(0.02, join_style=2), 0.25, 0.28)
        L.prism(mb, "pool_tile", box(-14.565, 11.33, 14.565, 13.41).difference(box(-14.555, 11.34, 14.555, 13.40)), -0.55, -0.10)
        L.prism(mb, "pool_tile", box(-14.575, 11.32, 14.575, 13.42), -0.60, -0.55, sides=False)
        L.prism(mb, "pool_water", box(-14.575, 11.32, 14.575, 13.42), -0.12, -0.10, sides=False)
    edge = plat.buffer(0.15, join_style=2).difference(plat.buffer(-0.15, join_style=2))
    L.prism(mb, "stone", edge, plinth, 0.25)                         # base of the platform: rubble stone
    L.prism(mb, "deck_stone", edge.buffer(0.02, join_style=2), 0.25, 0.28)
    for p in planters:
        L.prism(mb, "render_dark", p, -0.60, 0.65)
        L.prism(mb, "lawn", p.buffer(-0.12, join_style=2), 0.60, 0.62, sides=False)
    # cour anglaise: walls down to the sous-sol and a bronze railing
    if cour:
        L.prism(mb, "render", L.ring_poly(COUR, 0.01), -3.20, 0.20)
        L.prism(mb, "terrace", COUR, -3.21, -3.20, sides=False)
    for (a, b) in ([] if not cour else [((-12.70, -3.10), (-8.62, -3.10)), ((-12.70, 3.20), (-8.62, 3.20)), ((-12.70, -3.10), (-12.70, 3.20))]):
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
    front = edge_index(body, (-8.60, -3.18), (8.60, -3.18))
    for k, X in enumerate(Xs):
        if k == front:                      # FACADE PRINCIPALE: twelve 0.25 m squares at +8.03, and the
            squares(mb, X, [-3.575 + 0.65 * j for j in range(12)], 8.155, size=0.25)   # bands either side of the portal
            relief(mb, "trim", X, unary_union([box(sg * a0, z - 0.04, sg * a1, z + 0.04) for z in (1.087, 1.797, 3.126, 4.455, 5.836)
                                               for sg, a0, a1 in ((1, 2.50, 3.76), (-1, 3.76, 2.50))]), 0.03)
        else:
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
    # portal (FACADE PRINCIPALE, DROITE, GAUCHE): the same pointed horseshoe arch on its front and both
    # sides, each in a rectangular frame (two mouldings, bejmat field), a frieze of eight 0.25 m squares at
    # +6.37, cornice at +7.04, parapet to +7.62 with horns
    arch = {"s0": -1.242, "s1": 1.242, "z0": 0.20, "z1": 4.79, "shape": "poly", "pts": ARCH_PTS, "kind": "open"}
    sh = hole_shape(arch)
    Xf = face(mb, "render", (-2.875, -12.18), (2.875, -12.18), 0.0, 7.19, [arch], rev=0.40)
    face(mb, "render", (2.875, -6.88), (-2.875, -6.88), 0.0, 7.19, [dict(arch)], rev=0.40)
    Xs = [Xf]
    for x0 in (-2.875, 2.475):
        xo, xi = (x0, x0 + 0.40) if x0 < 0 else (x0 + 0.40, x0)
        Xs.append(face(mb, "render", (xo, -6.88) if x0 < 0 else (xo, -12.18), (xo, -12.18) if x0 < 0 else (xo, -6.88), 0.0, 7.19,
                       [dict(arch)], rev=0.40))
        face(mb, "render", (xi, -12.18) if x0 < 0 else (xi, -6.88), (xi, -6.88) if x0 < 0 else (xi, -12.18), 0.0, 6.50,
             [dict(arch)], rev=0.0)
    for X in Xs:
        fa, fb, fc = ARCH_FRAMES
        relief(mb, "trim", X, fa.difference(fb), 0.07)
        relief(mb, "render", X, fb.difference(fc), 0.05)
        relief(mb, "bejmat", X, fc.difference(sh), 0.03)
        squares(mb, X, [-2.275 + 0.65 * k for k in range(8)], 6.495, size=0.25)
    for P0, P1 in (((2.475, -11.78), (-2.475, -11.78)), ((-2.475, -7.28), (2.475, -7.28))):
        face(mb, "render", P0, P1, 0.0, 6.50, [dict(arch)], rev=0.0)     # inner faces, front and back
    mb.box("render", -2.865, 2.865, -12.17, -6.89, 6.50, 7.19)
    cornice(mb, PORTAL, 6.68, 6.75, 0.04)
    cornice(mb, PORTAL, 6.89, 7.19, 0.10)
    crown(mb, PORTAL.buffer(-0.001, join_style=2), 7.19, 7.56, t=0.25)

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

    obs = mb.build("PAV", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    return ob


PAV_TOWERS = [box(-TX1, FT[0], -TX0, FT[1]), box(TX0, FT[0], TX1, FT[1]), box(-TX1, RT[0], -TX0, RT[1]), box(TX0, RT[0], TX1, RT[1])]
PAV_SOLIDS = unary_union(PAV_TOWERS + [BODY, REAR, PORTAL, PASSAGE])
PAV_WATER = box(-14.775, -12.18, 14.775, -3.18).difference(PAV_SOLIDS)      # front bassins (the rear water is left out)
PAV_PERGOLAS = [box(-14.40, 7.85, -TX1, 11.25), box(TX1, 7.85, 14.40, 11.25)]


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
