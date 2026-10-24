"""
15_spa — the SPA, from its permit drawing 7-SPA-A0-1.pdf (client 23-10, "ha huwa plan dyal SPA"): REZ DE
CHAUSSEE (grid 1-9 / A-I), TERRASSE / MASSE, façades principale, arrière, latérales gauche and droite, coupes
A-A and B-B. It replaces the design suggestion of 22-10.

A single-storey building (R+0, floor +0.20, roof slab +4.20, parapet +5.20) on the plan's SPA lot, its front
on the two outdoor pools and the back on street 5:
  the main block, 37.6 x 13.65 m (axes 1-8 at 5.65 / 4.44 / 5.25 / 6.63 / 5.26 / 4.44 / 5.64 m, rows B-I);
    on the front a glazed wall each side of the centre (9 leaves, louvred transoms over glass doors to
    +2.04): the indoor pool (14.85 m) behind the southern one, the salle de coiffeur and the salle de sport
    behind the northern one; on the back two pairs of tall windows in framed stone surrounds;
  the centre block (accueil, fontaine, mur d'eau), 7.00 x 6.40 m, standing 1.29 m proud of the front (row A)
    and rising to +7.20: the villas' cornice, the curled horns at its corners, six square niches, the studded
    door with its studded transom in a taupe alfiz, a tall framed window each side;
  the roof terrace: parapet with the rounded coping and curled horns, the two domes of the bassin halls
    (rows F-G, axes 2-3 and 6-7) rising over the slab, four cantilever parasols with loungers, reached by the
    outside stair along the end wall past axis 8 (1.35 m, up to the terrace at +4.20, solid parapet);
  the lot paved round it, the two outdoor pools (16.6 x 3.35 m) along the front either side of the entrance
    path, loungers and parasols at the ends as the TERRASSE / MASSE draws them.
The façade principale is drawn as from the back (its stair on the wrong side): the plans win, as for the
villa type C.

Placement: the plan's frame (x along the axes 1 -> 9, y across A -> I, metres from axis 1 / row A) is turned
onto the cell: the front (pools) on the cell's west side, the back on street 5, axis 9 (the stair) north.
Local frame of build(): x 0-W across the cell (west -> east), y 0-Lg along it (south -> north).
"""
import importlib.util
import math
import os

from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t3_vc_spa", os.path.join(HERE, "14_villa_c.py"))
VC = importlib.util.module_from_spec(_spec)
VC.__dict__["L"] = L
_spec.loader.exec_module(VC)
D = VC.D

Z_FL, Z_SL, Z_PA = 0.20, 4.20, 5.20          # floor, roof slab (terrace), parapet top
Z_BK, Z_BC = 7.20, 6.20                      # centre block: parapet top, its cornice
LOT = (-7.10, -5.58, 45.60, 15.94)           # the lot of the TERRASSE / MASSE, plan frame
X_AX = (0.0, 5.65, 10.09, 15.34, 21.97, 27.23, 31.67, 37.31, 38.87)     # axes 1-9
Y_RW = (0.0, 1.25, 6.02, 7.46, 9.04, 10.52, 12.30, 13.51, 14.60)        # rows A-I
MAIN = (-0.15, 1.10, 37.46, 14.75)           # main block, outer faces
BLOCK = (15.155, -0.19, 22.155, 6.21)        # centre block, outer faces
GLZ = ((1.62, 13.85), (24.05, 36.25))        # the two glazed walls on the front
Z_LOT = 0.10                                 # the lot's paving
Z_TR = 2.04                                  # the glazing's transom (louvres above, glass doors below)
STAIR = (37.46, 38.81, 1.25, 7.40, 8.75)     # outside stair: x0 x1, foot, top of the flight, end of the landing
POOLS = ((-0.70, -3.97, 15.90, -0.62), (21.34, -3.97, 38.03, -0.62))
IPOOL = (0.30, 1.45, 14.90, 5.30)            # the indoor pool's water
EDGE = 0.30                                  # the lot's edge (with the ground round it)
DOMES = ((7.87, 11.41), (29.45, 11.41))      # the bassin halls' domes: base r 1.85 on the slab, top +5.30


def build(M, col, W, Lg, name="T2_SPA", zg=None):
    """Returns (objects, plants, lanterns) in the local frame (plants and lanterns: none on the drawing). zg(x, y):
    the ground round the lot over the SPA's base, for the lot's edge."""
    ox = (W - (LOT[3] - LOT[1])) / 2 - LOT[1]
    oy = (Lg - (LOT[2] - LOT[0])) / 2 - LOT[0]
    lc = lambda p: (p[1] + ox, p[0] + oy)                     # plan (x, y) -> local (x, y)
    R = lambda x0, y0, x1, y1: box(y0 + ox, x0 + oy, y1 + ox, x1 + oy)
    mb = C.MeshBuilder()
    main, block = R(*MAIN), R(*BLOCK)
    ground = unary_union([main, block])

    def wall(a, b, cen, z0, z1, ops=(), mat="villa", dep=0.30):
        """A plumb face between plan points a, b, outward away from cen; ops: (u0, u1, h0, h1, kind) with u
        the plan coordinate along it; kinds: 'glz' (glazed wall), 'door', 'win' (framed window), 'niche'."""
        pa, pb = lc(a), lc(b)
        c = lc(cen)
        ux, uy = pb[0] - pa[0], pb[1] - pa[1]
        if (uy * (c[0] - pa[0]) - ux * (c[1] - pa[1])) > 0:   # the right-hand normal must point away from cen
            pa, pb, a, b = pb, pa, b, a
        Lw, P3, *_ = VC.frame_of(pa, pb, False)
        along_x = abs(a[1] - b[1]) < 1e-6
        s_of = lambda u: math.dist(pa, lc((u, a[1]) if along_x else (a[0], u)))
        holes = []
        for u0, u1, h0, h1, kind in ops:
            s0, s1 = sorted((s_of(u0), s_of(u1)))
            holes.append((box(s0, h0, s1, h1), kind))
        face = box(0.0, z0, Lw, z1)
        for h, _ in holes:
            face = face.difference(h)
        for g in L.as_polys(face):
            for t in L.tri_poly(g):
                mb.poly(mat, [P3(s, z) for s, z in t], [(s, z) for s, z in t])
        for h, kind in holes:
            s0, h0, s1, h1 = h.bounds
            dp = 0.10 if kind == "niche" else dep
            for (sa, za), (sb, zb) in (((s0, h1), (s0, h0)), ((s1, h0), (s1, h1)), ((s1, h1), (s0, h1)), ((s0, h0), (s1, h0))):
                if za <= z0 + 1e-6 and zb <= z0 + 1e-6:
                    continue
                mb.poly(mat if kind == "niche" else "surround", [P3(sb, zb), P3(sa, za), P3(sa, za, dp), P3(sb, zb, dp)])
            FILL[kind](P3, s0, s1, h0, h1, dp)

    def rect(P3, mat, a0, a1, b0, b1, d):
        mb.poly(mat, [P3(a0, b0, d), P3(a1, b0, d), P3(a1, b1, d), P3(a0, b1, d)], [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])

    def niche(P3, s0, s1, h0, h1, dp):
        rect(P3, "villa", s0, s1, h0, h1, dp)

    def glazed(P3, s0, s1, h0, h1, dp):
        """9 leaves: glass doors to the transom, louvres over it, aluminium mullions; a stone surround."""
        n, d = 9, 0.14
        rect(P3, "glass", s0, s1, h0, Z_TR, d)
        rect(P3, "glass", s0, s1, Z_TR, h1, d + 0.06)
        for k in range(n + 1):
            s = s0 + (s1 - s0) * k / n
            D.pbox(mb, P3, max(s0, s - 0.04), min(s1, s + 0.04), h0, h1, d - 0.05, d + 0.04, "frame")
        for z in (h0, Z_TR - 0.04, h1 - 0.06):
            D.pbox(mb, P3, s0, s1, z, z + 0.06, d - 0.05, d + 0.04, "frame")
        z = Z_TR + 0.10
        while z < h1 - 0.10:
            D.pbox(mb, P3, s0, s1, z, z + 0.035, d - 0.03, d + 0.03, "frame")
            z += 0.135
        D.pbox(mb, P3, s0 - 0.20, s0, h0, h1 + 0.22, -0.04, 0.02, "surround")
        D.pbox(mb, P3, s1, s1 + 0.20, h0, h1 + 0.22, -0.04, 0.02, "surround")
        D.pbox(mb, P3, s0, s1, h1, h1 + 0.22, -0.04, 0.02, "surround")

    def window(P3, s0, s1, h0, h1, dp):
        """A tall window in a framed stone surround (two borders), glass, aluminium frame, curtains."""
        d = 0.12
        rect(P3, "interior", s0 - 0.3, s1 + 0.3, h0 - 0.3, h1 + 0.3, 0.80)
        rect(P3, "glass", s0 + 0.12, s1 - 0.12, h0 + 0.12, h1 - 0.12, d)
        D.pbox(mb, P3, s0 + 0.06, s1 - 0.06, h0 + 0.06, h0 + 0.12, d - 0.03, d + 0.03, "frame")
        D.pbox(mb, P3, s0 + 0.06, s1 - 0.06, h1 - 0.12, h1 - 0.06, d - 0.03, d + 0.03, "frame")
        D.pbox(mb, P3, s0 + 0.06, s0 + 0.12, h0 + 0.12, h1 - 0.12, d - 0.03, d + 0.03, "frame")
        D.pbox(mb, P3, s1 - 0.12, s1 - 0.06, h0 + 0.12, h1 - 0.12, d - 0.03, d + 0.03, "frame")
        rect(P3, "curtain", s0 + 0.12, s0 + 0.30, h0 + 0.15, h1 - 0.15, 0.30)
        rect(P3, "curtain", s1 - 0.30, s1 - 0.12, h0 + 0.15, h1 - 0.15, 0.30)
        for w, df in ((0.16, -0.05), (0.06, -0.08)):              # the two borders of the frame
            D.pbox(mb, P3, s0 - w, s0, h0 - w, h1 + w, df, 0.02, "surround")
            D.pbox(mb, P3, s1, s1 + w, h0 - w, h1 + w, df, 0.02, "surround")
            D.pbox(mb, P3, s0, s1, h1, h1 + w, df, 0.02, "surround")
            D.pbox(mb, P3, s0, s1, h0 - w, h0, df, 0.02, "surround")

    def door(P3, s0, s1, h0, h1, dp):
        """The studded double door to +2.90 and its studded transom, in the taupe alfiz."""
        d = 0.28
        zt = 2.90
        for a0, a1, b0, b1 in ((s0, (s0 + s1) / 2 - 0.01, h0, zt), ((s0 + s1) / 2 + 0.01, s1, h0, zt), (s0, s1, zt + 0.10, h1)):
            rect(P3, "door_wood", a0, a1, b0, b1, d)
            nx, nz = max(2, int((a1 - a0) / 0.16)), max(2, int((b1 - b0) / 0.18))
            for i in range(nx):
                for j in range(nz):
                    a = a0 + 0.08 + (a1 - a0 - 0.16) * i / (nx - 1)
                    b = b0 + 0.08 + (b1 - b0 - 0.16) * j / (nz - 1)
                    D.pbox(mb, P3, a - 0.013, a + 0.013, b - 0.013, b + 0.013, d - 0.02, d, "metal_dark")
        D.pbox(mb, P3, s0, s1, zt, zt + 0.10, d - 0.04, d, "door_wood")
        for k in (-1, 1):
            D.pbox(mb, P3, (s0 + s1) / 2 + k * 0.20 - 0.07, (s0 + s1) / 2 + k * 0.20 + 0.07, 1.05, 1.13, d - 0.06, d, "metal_dark")
        ring = box(s0 - 0.52, h0, s1 + 0.52, h1 + 0.37).difference(box(s0, h0, s1, h1))
        D.ext(mb, "surround", ring, lambda a, b, w: P3(a, b, w), -0.06, 0.0)
        inner = box(s0 - 0.30, h0, s1 + 0.30, h1 + 0.17).difference(box(s0 - 0.20, h0, s1 + 0.20, h1 + 0.07))
        D.ext(mb, "surround", inner, lambda a, b, w: P3(a, b, w), -0.10, -0.06)

    FILL = {"glz": glazed, "win": window, "door": door, "niche": niche}

    # ---- the main block ------------------------------------------------------------------------------------
    x0, y0, x1, y1 = MAIN
    cen = ((x0 + x1) / 2, (y0 + y1) / 2)
    bx0, by0, bx1, by1 = BLOCK
    zw = Z_SL - 0.02                                          # the walls' faces up to the roof, the parapet over them
    wall((x0, y0), (bx0, y0), cen, -1.0, zw, [(GLZ[0][0], GLZ[0][1], Z_FL, 3.50, "glz")])
    wall((bx1, y0), (x1, y0), cen, -1.0, zw, [(GLZ[1][0], GLZ[1][1], Z_FL, 3.50, "glz")])
    wall((x0, y1), (x1, y1), cen, -1.0, zw,
         [(12.69, 13.79, 0.96, 4.00, "win"), (13.90, 14.89, 0.96, 4.00, "win"),
          (22.72, 23.75, 0.96, 4.00, "win"), (23.86, 24.92, 0.96, 4.00, "win")])
    wall((x0, y0), (x0, y1), cen, -1.0, zw)
    wall((x1, y0), (x1, y1), cen, -1.0, zw)
    # the roof: slab, terrace, parapet with the rounded coping (the stair's opening at the north end), cornice
    roof = main.difference(block)
    L.prism(mb, "villa", roof.buffer(-0.01, join_style=2), Z_SL - 0.15, Z_SL - 0.02, bottom=True)
    L.prism(mb, "terrace", roof.buffer(-0.30, join_style=2), Z_SL - 0.02, Z_SL, sides=False)
    gap = R(STAIR[0] - 0.4, STAIR[3], STAIR[0] + 0.4, STAIR[4])
    par = main.difference(main.buffer(-0.30, join_style=2)).difference(block).difference(gap)
    L.prism(mb, "villa", par, Z_SL - 0.02, Z_PA - 0.06, bottom=False)
    D.coping(mb, "villa", par, Z_PA, 0.06)
    for z0, z1, pd, mat in ((Z_SL, Z_SL + 0.08, 0.10, "ledge"), (Z_SL + 0.08, Z_SL + 0.22, 0.06, "band"), (Z_SL + 0.22, Z_SL + 0.30, 0.12, "ledge")):
        L.prism(mb, mat, main.buffer(pd, join_style=2).difference(main).difference(block.buffer(0.02, join_style=2)), z0, z1, bottom=True)
    VC.horns(mb, main.buffer(0.012, join_style=2), Z_PA)          # 12 mm proud of the parapet's face

    # ---- the centre block: to +7.20, cornice, horns, niches, the door in its alfiz, the two windows -----------
    bcen = ((bx0 + bx1) / 2, (by0 + by1) / 2)
    ns = [16.0 + 5.3 * k / 5 for k in range(6)]
    zb = Z_BK - 0.82
    wall((bx0, by0), (bx1, by0), bcen, -1.0, zb,
         [(18.04, 19.89, Z_FL, 4.95, "door"), (16.09, 17.08, 0.98, 4.11, "win"), (20.87, 21.88, 0.98, 4.11, "win")]
         + [(u - 0.10, u + 0.10, 5.70, 5.90, "niche") for u in ns], dep=0.45)
    wall((bx0, by1), (bx1, by1), bcen, Z_SL, zb, [(u - 0.10, u + 0.10, 5.70, 5.90, "niche") for u in ns])
    for xs in (bx0, bx1):
        wall((xs, by0), (xs, y0), bcen, -1.0, zb)
        wall((xs, y0), (xs, by1), bcen, Z_SL, zb)
    L.prism(mb, "terrace", block.buffer(-0.30, join_style=2), zb, zb + 0.02, sides=False)
    bpar = block.difference(block.buffer(-0.30, join_style=2))
    L.prism(mb, "villa", bpar, zb, Z_BK - 0.06, bottom=False)
    D.coping(mb, "villa", bpar, Z_BK, 0.06)
    for z0, z1, pd, mat in ((Z_BC, Z_BC + 0.07, 0.10, "ledge"), (Z_BC + 0.07, Z_BC + 0.17, 0.06, "band"), (Z_BC + 0.17, Z_BC + 0.25, 0.14, "ledge")):
        L.prism(mb, mat, block.buffer(pd, join_style=2).difference(block), z0, z1, bottom=True)
    VC.horns(mb, block.buffer(0.012, join_style=2), Z_BK)

    # ---- the domes of the bassin halls ------------------------------------------------------------------------
    rb, top = 1.85, Z_PA + 0.10
    Rs = (rb * rb + (top - Z_SL) ** 2) / (2 * (top - Z_SL))
    zc = top - Rs
    a0 = math.asin(rb / Rs)
    for dx, dy in DOMES:
        cx, cy = lc((dx, dy))
        rings = [(Rs * math.sin(a0 * (1 - k / 8)), zc + Rs * math.cos(a0 * (1 - k / 8))) for k in range(9)]
        n = 32
        for k in range(8):
            (r0, z0), (r1, z1) = rings[k], rings[k + 1]
            for j in range(n):
                t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                q = [(cx + r0 * math.cos(t0), cy + r0 * math.sin(t0), z0), (cx + r0 * math.cos(t1), cy + r0 * math.sin(t1), z0),
                     (cx + r1 * math.cos(t1), cy + r1 * math.sin(t1), z1), (cx + r1 * math.cos(t0), cy + r1 * math.sin(t0), z1)]
                mb.poly("villa", q if r1 > 1e-6 else q[:3])
        L.prism(mb, "villa", Point(cx, cy).buffer(rb + 0.10, 32).difference(Point(cx, cy).buffer(rb - 0.05, 32)), Z_SL, Z_SL + 0.12)

    # ---- the outside stair to the terrace (22 risers), solid under its flight, solid parapet --------------------
    sx0, sx1, sy0, sy1, sy2 = STAIR
    n_r = 22
    rise, go = (Z_SL - 0.0) / n_r, (sy1 - sy0) / (n_r - 1)
    for k in range(n_r):
        ya, yb = sy0 + k * go, (sy0 + (k + 1) * go if k < n_r - 1 else sy2)
        zt = rise * (k + 1)
        L.prism(mb, "villa", R(sx0, ya, sx1 - 0.15, yb), -1.0, zt - 0.03)
        L.prism(mb, "deck_stone", R(sx0, ya, sx1 - 0.15, yb), zt - 0.03, zt)
    prof = Polygon([(sy0 - 0.05, -1.0), (sy2, -1.0), (sy2, Z_PA), (sy1, Z_PA), (sy0 - 0.05, 1.0)])
    D.ext(mb, "villa", prof, lambda a, b, w: (lc((w, a))[0], lc((w, a))[1], b), sx1 - 0.15, sx1)
    # the landing's end wall against the main block's parapet (client 24-10: "chud hadiya", the landing was open
    # there, a slot between the two parapets)
    L.prism(mb, "villa", R(sx0, sy2, sx1, sy2 + 0.15), Z_SL - 0.05, Z_PA - 0.06)
    D.coping(mb, "villa", R(sx0, sy2, sx1, sy2 + 0.15), Z_PA, 0.06)
    cop = [(sy0 - 0.05, 1.0), (sy1, Z_PA), (sy2, Z_PA)]
    for (ya, za), (yb, zb) in zip(cop, cop[1:]):
        prof_c = Polygon([(ya, za), (yb, zb), (yb, zb + 0.06), (ya, za + 0.06)])
        D.ext(mb, "coping_beige", prof_c, lambda a, b, w: (lc((w, a))[0], lc((w, a))[1], b), sx1 - 0.18, sx1 + 0.03)

    # ---- inside, seen through the glazing: the floor, the indoor pool, the beds, the back walls ---------------
    L.prism(mb, "deck_stone", ground.buffer(-0.01, join_style=2).difference(R(*IPOOL).buffer(0.30, join_style=2)), -0.40, Z_FL)
    ip = R(*IPOOL)
    L.prism(mb, "coping", ip.buffer(0.30, join_style=2).difference(ip), Z_FL - 0.05, Z_FL + 0.02)
    L.prism(mb, "pool_tile", ip, -1.30, -1.25, sides=False)
    L.prism(mb, "pool_tile", ip.buffer(0.01, join_style=2).difference(ip.buffer(-0.01, join_style=2)), -1.25, Z_FL)
    L.prism(mb, "pool_water", ip.buffer(-0.01, join_style=2), Z_FL - 0.12, Z_FL - 0.10, sides=False)
    for xa, xb in ((x0, bx0), (bx1, x1)):
        wall((xa, Y_RW[3]), (xb, Y_RW[3]), (cen[0], y1 + 5.0), Z_FL, Z_SL - 0.15)        # facing the front
    wall((bx0, y0), (bx0, Y_RW[3]), (bx0 + 5.0, cen[1]), Z_FL, Z_SL - 0.15)
    wall((bx1, y0), (bx1, Y_RW[3]), (bx1 - 5.0, cen[1]), Z_FL, Z_SL - 0.15)

    def lounger(x, y, ang, z=Z_FL):
        ca, sa = math.cos(ang), math.sin(ang)
        Q = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
        g = Polygon([Q(-0.35, -0.95), Q(0.35, -0.95), Q(0.35, 0.95), Q(-0.35, 0.95)])
        L.prism(mb, "lounger_white", g, z + 0.06, z + 0.30)
        L.prism(mb, "cushion", g.buffer(-0.04), z + 0.30, z + 0.36)
        L.prism(mb, "cushion", Polygon([Q(-0.33, 0.55), Q(0.33, 0.55), Q(0.33, 0.93), Q(-0.33, 0.93)]), z + 0.36, z + 0.70)
        for u, v in ((-0.3, -0.85), (0.3, -0.85), (-0.3, 0.85), (0.3, 0.85)):
            L.prism(mb, "lounger_white", Point(*Q(u, v)).buffer(0.03, 4), z, z + 0.06)

    def parasol(x, y, z, r=1.4, h=2.55, arm=None):
        """a parasol on a pole; arm: (dx, dy) to a cantilevered canopy"""
        L.prism(mb, "metal_dark", Point(x, y).buffer(0.25, 8), z, z + 0.08)
        L.prism(mb, "metal_dark", Point(x, y).buffer(0.04, 6), z, z + h + 0.25)
        cx, cy = (x + arm[0], y + arm[1]) if arm else (x, y)
        if arm:
            Lr = math.hypot(*arm)
            g = Polygon([(x, y), (cx, cy), (cx + 0.03 * arm[1] / Lr, cy - 0.03 * arm[0] / Lr), (x + 0.03 * arm[1] / Lr, y - 0.03 * arm[0] / Lr)])
            L.prism(mb, "metal_dark", g.buffer(0.02), z + h + 0.15, z + h + 0.22)
        apex = (cx, cy, z + h + 0.25)
        rim = [(cx + r * math.cos(2 * math.pi * k / 8), cy + r * math.sin(2 * math.pi * k / 8), z + h - 0.15) for k in range(8)]
        for k in range(8):
            mb.poly("canvas", [rim[k], rim[(k + 1) % 8], apex])

    for xb_ in (3.6, 7.7, 11.8):                              # the relaxation beds by the indoor pool (rows C-D)
        lounger(*lc((xb_, 6.75)), math.pi / 2)

    # ---- outside: the lot paved, the two pools, the entrance path, loungers and parasols at the ends -----------
    lot = box(0.0, 0.0, W, Lg)
    pools = [R(*p) for p in POOLS]
    path = R(POOLS[0][2], LOT[1], POOLS[1][0], BLOCK[1])
    band = lot.difference(lot.buffer(-EDGE, join_style=2)) if zg else Polygon()
    pave = lot.difference(ground).difference(unary_union([p.buffer(-0.01) for p in pools])).difference(path).difference(band)
    L.prism(mb, "deck_stone", pave, -0.40, Z_LOT)
    L.prism(mb, "planks", path.difference(ground).difference(band), -0.40, 0.12)
    if zg:
        # client 24-10, second review: the lot's edge down to the ground where the street runs lower (a stone
        # plinth, no gap under the paving), holding the pavement where it runs higher, rising as a low wall (up
        # to 0.80 m) where the paving lies more than 0.30 m under it
        rings = [[(0.0, 0.0), (W, 0.0), (W, Lg), (0.0, Lg)], [(EDGE, EDGE), (W - EDGE, EDGE), (W - EDGE, Lg - EDGE), (EDGE, Lg - EDGE)]]
        for i in range(4):
            (ax, ay), (bx, by) = rings[0][i], rings[0][(i + 1) % 4]
            (cx, cy), (dx, dy) = rings[1][i], rings[1][(i + 1) % 4]
            n = max(1, int(math.ceil(math.hypot(bx - ax, by - ay) / 0.8)))
            pts = []
            for j in range(n + 1):
                t = j / n
                po, pi = (ax + (bx - ax) * t, ay + (by - ay) * t), (cx + (dx - cx) * t, cy + (dy - cy) * t)
                g = zg(po[0] + (by - ay) / max(1e-9, math.hypot(bx - ax, by - ay)) * 0.30,
                       po[1] - (bx - ax) / max(1e-9, math.hypot(bx - ax, by - ay)) * 0.30)
                top = max(Z_LOT, g + 0.155) + min(0.80, max(0.0, (g + 0.155 - Z_LOT - 0.30) * 2.0))   # a low wall over a drop
                pts.append((po, pi, top, min(Z_LOT, g) - 0.30))
            for (po0, pi0, t0, b0), (po1, pi1, t1, b1) in zip(pts, pts[1:]):
                mb.poly("surround", [(*po0, b0), (*po1, b1), (*po1, t1), (*po0, t0)])
                mb.poly("surround", [(*pi1, b1), (*pi0, b0), (*pi0, t0), (*pi1, t1)])
                mb.poly("coping", [(*po0, t0), (*po1, t1), (*pi1, t1), (*pi0, t0)])
    for p in pools:
        w_ = p.buffer(-0.30, join_style=2)
        L.prism(mb, "coping", p.difference(w_), -0.10, 0.16)
        L.prism(mb, "pool_tile", w_, -1.40, -1.35, sides=False)
        L.prism(mb, "pool_tile", w_.buffer(0.01, join_style=2).difference(w_.buffer(-0.01, join_style=2)), -1.35, 0.10)
        L.prism(mb, "pool_water", w_.buffer(-0.01, join_style=2), -0.06, -0.04, sides=False)
    for (px, py, ang) in ((-3.9, -2.9, 0.5), (-2.9, -2.4, 0.5), (41.9, -2.9, -0.5), (42.9, -2.4, -0.5), (-3.6, 3.9, 0.0), (41.2, 3.9, 0.0)):
        lounger(*lc((px, py)), ang, 0.10)
    for (px, py) in ((-1.9, -1.2), (40.0, -1.2), (-3.9, 7.8), (-3.9, 11.3), (41.4, 7.4), (41.5, 11.4)):
        parasol(*lc((px, py)), 0.10)
    # on the roof: four cantilever parasols over pairs of loungers
    for px in (3.5, 11.9, 26.6, 35.3):
        pole = lc((px - 2.0 if px < 18 else px + 1.6, 3.0))
        cn = lc((px, 3.0))
        parasol(*pole, Z_SL, 1.6, 2.70, (cn[0] - pole[0], cn[1] - pole[1]))
        for dxl in (-0.6, 0.6):
            lounger(*lc((px + dxl, 3.6)), math.pi / 2, Z_SL)
    obs = mb.build(name, col, M)
    return obs, [], []
