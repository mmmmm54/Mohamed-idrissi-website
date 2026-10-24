"""
02_duplex — the 'DUPLEX JUMELEE' of the 1er TRANCHE (12 pairs), exterior.

Rev 4 (remarks on the D5 model, slides 7, 9 and 10): rebuilt to the architect's VILLA N°09 drawing
(DUPLRX_N__09.dwg: plans RDC / 1er étage / terrasse, coupe A-A, façades principale, arrière and
droite) and to the two reference images sent with the remarks (front view, rear view). One design for
every pair; the drawing shows one villa, its neighbour is its mirror across the 'Axe limite villa'.

  RDC 84.32 m2: the front wing (bedroom), entrance door with its canopy next to the wing, kitchen
      window (allège 1.00), salon window on the side, 4-leaf sliding door onto the garden; a row of
      eight square niches across the rear at the terrace level.
  1er 54.36 m2: set back 1.36 m behind the wing (front terrace, solid parapet with three niches) and
      3.44 m behind the rear (rear terrace: masonry piers and wooden geometric railings, 'Cadre en
      bois'); one window over the wing, one in the side part, a 2-leaf sliding door onto the rear
      terrace; niches under the cornice.
  Roof +7.10, cornice = grey stone ledge / ochre stone band / grey stone ledge, acrotère to +8.30
      with a rounded coping; stair cage of the two villas over their stairs (+9.80) with the same
      cornice, its roof door on the side, a small window at the back (no horns, client 24-10); 'GT' ducts.
  Timber pergolas over both terraces ('Pergola en bois', plan TERRASSE 'V/Terrasse').
  Remark of slide 10: the two villas' terraces are separated by a wall on the joint (front terrace,
      rear terrace and roof terrace), as the drawing shows it on the joint.
  Window and door surrounds in taupe stone, beige aluminium frames (darker than the render, 20-10), studded timber entrance door: from the
      reference images. Low stone-clad front garden wall with its coping, gate pillars and gate
      (façade principale), paved rear terrace (plan RDC).

Local frame (metres): origin on the joint axis, x along the pair (joint at x = 0, side faces at
+-8.19), y towards the rear garden with the side-part front faces at y = -3.47 (same origin as the
previous model, so the plan de masse placements are unchanged): wing front -7.32, rear 5.55.
z = 0 at the house pad (+0.00 of the drawing), RDC floor +0.20, terraces +3.90, roof +7.10,
acrotère +8.30, stair cage +9.80. Interiors are not modelled (dark interior proxy behind the glass).
"""
import math

from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]          # lib module, injected by the scene script
C = L.C

HX, WX = 8.19, 3.50                          # half width of the pair, half width of the two wings
YW, YF, YR = -7.32, -3.47, 5.55              # RDC: wing front, side-part fronts, rear
YWE, YRE = -5.96, 2.11                       # 1er étage: wing front, rear
Z_FL, Z1, Z2 = 0.20, 3.90, 7.10              # RDC floor, terraces / 1er floor, roof
Z_PF, Z_PR, Z_CURB = 4.90, 4.70, 3.98        # front parapet, rear piers and side parapets, railing curb
Z_ACRO, Z_CW, Z_CTOP = 8.30, 9.03, 9.78      # acrotère, stair cage walls, stair cage top
CX, CY0 = 3.09, -1.82                        # stair cage: half width, front face (rear = YRE)
SEP = 0.17                                   # half thickness of the separation wall on the joint

RDC = unary_union([box(-HX, YF, HX, YR), box(-WX, YW, WX, YF)])
ET = unary_union([box(-HX, YF, HX, YRE), box(-WX, YWE, WX, YF)])
CAGE = box(-CX, CY0, CX, YRE)
REAR_TERRACE = box(-HX, YR, HX, 7.60)        # paved terrace behind the salons (plan RDC)
FOOT = unary_union([RDC, REAR_TERRACE])      # what the scene keeps clear of trees
PIERS = [(SEP, 0.40), (3.70, 4.50), (7.80, HX)]   # rear terrace edge, between them the railings
REV = 0.20                                   # reveal depth; frames sit 0.10 behind the face
COP = 0.04                                   # rounded coping on the parapets (height)


def mirror_x(ops):
    out = []
    for o in ops:
        out.append(o)
        m = dict(o)
        if o["axis"] == "y":
            m["u0"], m["u1"] = -o["u1"], -o["u0"]
        else:
            m["c"] = -o["c"]
        out.append(m)
    return out


def mirror(g):
    return unary_union([g, affinity.scale(g, xfact=-1.0, origin=(0, 0))])


def op(axis, c, u0, u1, z0, z1, kind, n=1):
    return {"axis": axis, "c": c, "u0": u0, "u1": u1, "z0": z0, "z1": z1, "kind": kind, "n": n}


def niche(axis, c, uc, z0, z1, w=0.20):
    return op(axis, c, uc - w / 2, uc + w / 2, z0, z1, "niche")


# openings of the east villa (x > 0), mirrored: axis 'y' = wall in the plane y = c (u = x),
# axis 'x' = wall in the plane x = c (u = y). Sizes from the façades, positions from the plans.
OPENINGS = mirror_x([
    op("y", YW, 1.03, 2.51, 1.20, 2.35, "window", 2),          # RDC wing front (Ch 1)
    op("y", YF, 3.65, 4.78, Z_FL, 2.55, "door"),               # entrance
    op("y", YF, 5.20, 6.70, 1.20, 2.40, "window", 2),          # kitchen, allège 1.00
    op("x", HX, 3.40, 4.90, 1.18, 2.38, "window", 2),          # salon, side
    {**op("y", YR, 2.12, 6.14, Z_FL, 2.64, "baie", 4), "rev": 0.36, "rev_mat": "surround"},   # salon onto the garden
    op("y", YWE, 1.07, 2.48, 4.92, 6.04, "window", 2),         # 1er, over the wing (Ch 3)
    op("y", YF, 5.69, 6.29, 4.92, 6.04, "sash"),               # 1er, side part (SDB)
    op("y", YRE, 5.09, 7.59, Z1 + 0.02, 5.74, "slider", 2),    # Ch 2 onto the rear terrace
    op("x", CX, -1.24, -0.54, Z2 + 0.02, 9.00, "roofdoor"),    # stair cage, roof door
    op("y", YRE, 1.76, 2.14, 8.30, 8.70, "window"),            # stair cage, small rear window
    # square niches (0.20 x 0.20, 0.10 deep)
    *[niche("y", YW, x, 4.30, 4.50) for x in (0.675, 1.675, 2.675)],                 # front parapet
    *[niche("y", YF, x, 6.71, 6.91) for x in (4.40, 5.16, 5.92, 6.68, 7.44)],         # under the cornice
    *[niche("y", YR, x, 3.10, 3.30) for x in (0.43, 1.43, 2.43, 3.43, 4.43, 5.55, 6.55, 7.55)],
    *[niche("x", HX, y, 6.23, 6.43) for y in (-2.27, -1.27, -0.26, 0.73, 1.74)],     # side, 1er
    *[niche("x", WX, y, 6.23, 6.43) for y in (-5.59, -4.59)],                         # wing side, 1er
    *[niche("x", CX, y, 8.80, 8.98) for y in (-0.10, 0.50, 1.10, 1.70)],              # stair cage
])

BREAK_X = sorted({s * v for v in (0.0, SEP, 0.40, 3.70, 4.50, 7.80, WX, HX, CX) for s in (1, -1)})
BREAK_Y = sorted({YW, YWE, YF, YRE, YR, CY0})


def rdc_top(x, y):
    """Top of the RDC wall face at (x, y): the parapets of the two terraces carry the façade up."""
    ax = abs(x)
    if ax < SEP - 1e-6 and (y < YWE or y > YRE):
        return Z1                                           # the separation wall takes over
    if y < YWE - 1e-6 and ax <= WX + 1e-6:
        return Z_PF - COP                                   # front terrace parapet
    if y > YRE + 1e-6:
        if abs(y - YR) < 1e-3:                              # rear edge: piers, railings between them
            return Z_PR - COP if any(a - 1e-6 <= ax <= b + 1e-6 for a, b in PIERS) else Z_CURB
        return Z_PR - COP                                   # side parapet of the rear terrace
    return Z1


def edges(poly):
    c = list(poly.exterior.coords)
    if not poly.exterior.is_ccw:
        c = c[::-1]
    return list(zip(c, c[1:]))


def wall(mb, p, q, z0, ztop, mat="villa"):
    """Outer wall face p->q (CCW outline, outward normal on the right) with its openings and niches.
    ztop: a height, or a function (x, y) -> height, constant between the BREAK_X / BREAK_Y lines."""
    (ax, ay), (bx, by) = p, q
    Lg = math.dist(p, q)
    ux, uy = (bx - ax) / Lg, (by - ay) / Lg
    nx, ny = uy, -ux                                  # outward normal
    axis = "y" if abs(uy) < 1e-6 else "x"
    cst = ay if axis == "y" else ax
    org, du = (ax, ux) if axis == "y" else (ay, uy)
    if callable(ztop):
        cuts = {0.0, Lg}
        for v in (BREAK_X if axis == "y" else BREAK_Y):
            s = (v - org) / du
            if 1e-6 < s < Lg - 1e-6:
                cuts.add(s)
        cuts = sorted(cuts)
        face = unary_union([box(a, z0, b, ztop(ax + ux * (a + b) / 2, ay + uy * (a + b) / 2))
                            for a, b in zip(cuts, cuts[1:])])
    else:
        face = box(0, z0, Lg, ztop)
    z1 = face.bounds[3]
    holes = []
    for o in OPENINGS:
        if o["axis"] != axis or abs(o["c"] - cst) > 0.03 or o["z1"] <= z0 or o["z0"] >= z1:
            continue
        s0, s1 = sorted(((o["u0"] - org) / du, (o["u1"] - org) / du))
        if s0 < -0.01 or s1 > Lg + 0.01:
            continue
        holes.append((s0, s1, o["z0"], o["z1"], o))
    for s0, s1, h0, h1, _ in holes:
        face = face.difference(box(s0, h0, s1, h1))
    P3 = lambda s, z, d=0.0: (ax + ux * s - nx * d, ay + uy * s - ny * d, z)
    for t in L.tri_poly(face):
        mb.poly(mat, [P3(s, z) for s, z in t], [(s, z) for s, z in t])
    for s0, s1, h0, h1, o in holes:
        dep = o.get("rev", 0.10 if o["kind"] == "niche" else REV)
        for (sa, za), (sb, zb) in [((s0, h1), (s0, h0)), ((s1, h0), (s1, h1)), ((s1, h1), (s0, h1)), ((s0, h0), (s1, h0))]:
            mb.poly(o.get("rev_mat", mat), [P3(sa, za), P3(sb, zb), P3(sb, zb, dep), P3(sa, za, dep)])
        insert(mb, P3, s0, s1, h0, h1, o, mat)
    return holes


def pbox(mb, P3, a0, a1, b0, b1, df, db, mat):
    """Box in wall coordinates between depths df (front, < db) and db; df < 0 stands proud."""
    f = lambda a, b: P3(a, b, df)
    w = lambda a, b: P3(a, b, db)
    mb.poly(mat, [f(a0, b0), f(a1, b0), f(a1, b1), f(a0, b1)], [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])
    mb.poly(mat, [w(a0, b1), f(a0, b1), f(a1, b1), w(a1, b1)])
    mb.poly(mat, [w(a1, b0), f(a1, b0), f(a0, b0), w(a0, b0)])
    mb.poly(mat, [w(a0, b0), f(a0, b0), f(a0, b1), w(a0, b1)])
    mb.poly(mat, [w(a1, b1), f(a1, b1), f(a1, b0), w(a1, b0)])


def insert(mb, P3, s0, s1, z0, z1, o, wall_mat):
    """What fills an opening: niche back, or frame + leaves + glass + curtains + stone surround,
    or the studded entrance door with its canopy, or the stair cage's roof door."""
    kind = o["kind"]
    d = 0.10                                          # frame plane
    fr = 0.06

    def rect(mat, a0, a1, b0, b1, dd):
        mb.poly(mat, [P3(a0, b0, dd), P3(a1, b0, dd), P3(a1, b1, dd), P3(a0, b1, dd)], [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])

    def frame(a0, a1, b0, b1, mat="frame"):
        pbox(mb, P3, a0, a1, b0, b1, d - 0.03, d + 0.03, mat)

    if kind == "niche":
        rect(wall_mat, s0, s1, z0, z1, 0.10)
        return
    if kind == "baie":
        baie(mb, P3, s0, s1, z0, z1, o["n"], rect)
        return
    rect("interior", s0 - 0.3, s1 + 0.3, z0 - 0.3, z1 + 0.3, 0.75)
    if kind == "door":
        rect("surround", s0, s1, z0, z1, d + 0.03)                         # stone behind the arched head
        fw, rise = 0.07, 0.16
        a0, a1, top = s0 + fw, s1 - fw, z1 - fw
        arc = [(a0 + (a1 - a0) * k / 12, top - rise + rise * math.sin(math.pi * k / 12)) for k in range(13)]
        leaf = Polygon([(a0, z0), (a1, z0)] + arc[::-1]).buffer(0)
        for t in L.tri_poly(leaf):
            mb.poly("door_wood", [P3(a, b, d) for a, b in t], [(a, b) for a, b in t])
        frame(s0, s0 + fw, z0, z1 - fw, "surround")
        frame(s1 - fw, s1, z0, z1 - fw, "surround")
        frame(s0, s1, z1 - fw, z1, "surround")
        nx_, nz_ = 6, 13                                                   # studs
        for i in range(nx_):
            for j in range(nz_):
                a = a0 + 0.10 + (a1 - a0 - 0.20) * i / (nx_ - 1)
                b = z0 + 0.15 + (top - rise - z0 - 0.25) * j / (nz_ - 1)
                pbox(mb, P3, a - 0.012, a + 0.012, b - 0.012, b + 0.012, d - 0.018, d, "metal_dark")
        hz_ = z0 + 1.05
        pbox(mb, P3, a1 - 0.16, a1 - 0.12, hz_ - 0.12, hz_ + 0.12, d - 0.05, d, "metal_dark")   # ring pull
        # canopy (façade principale +2.67 / +2.96, reference images): stone slab with a sloped top
        c0, c1 = s0 - 0.15, s1 + 0.17
        prof = Polygon([(-0.02, z1 + 0.10), (-0.02, z1 + 0.42), (0.20, z1 + 0.40), (0.44, z1 + 0.27), (0.44, z1 + 0.10)])
        ext(mb, "surround", prof, lambda a, b, w: P3(w, b, -a), c0, c1)
        return
    if kind == "roofdoor":
        rect("door_wood", s0, s1, z0, z1, d)
        frame(s0, s1, z1 - fr, z1)
        frame(s0, s0 + fr, z0, z1 - fr)
        frame(s1 - fr, s1, z0, z1 - fr)
        return
    rect("glass", s0, s1, z0, z1, d)
    frame(s0, s1, z0, z0 + fr)                        # frames butt-jointed: no overlapping faces
    frame(s0, s1, z1 - fr, z1)
    frame(s0, s0 + fr, z0 + fr, z1 - fr)
    frame(s1 - fr, s1, z0 + fr, z1 - fr)
    n = o["n"]
    for k in range(1, n):
        s = s0 + (s1 - s0) * k / n
        frame(s - fr / 2, s + fr / 2, z0 + fr, z1 - fr)
    if kind == "sash":
        zm = z0 + (z1 - z0) * 0.52
        frame(s0 + fr, s1 - fr, zm - fr / 2, zm + fr / 2)
        frame((s0 + s1) / 2 - 0.015, (s0 + s1) / 2 + 0.015, zm + fr / 2, z1 - fr)
    # curtains drawn to the sides (reference images)
    cw = (s1 - s0) * (0.17 if kind == "slider" else 0.26)
    rect("curtain", s0 + fr, s0 + fr + cw, z0 + 0.03, z1 - 0.03, 0.30)
    rect("curtain", s1 - fr - cw, s1 - fr, z0 + 0.03, z1 - 0.03, 0.30)
    # stone surround, 0.20 wide, standing 0.04 proud; windows also get the sill piece
    w_, top = (0.18, 0.20) if kind == "slider" else (0.20, 0.23)
    b0 = z0 if kind == "slider" else z0 - 0.20
    pbox(mb, P3, s0 - w_, s0, b0, z1 + top, -0.04, 0.02, "surround")
    pbox(mb, P3, s1, s1 + w_, b0, z1 + top, -0.04, 0.02, "surround")
    pbox(mb, P3, s0, s1, z1, z1 + top, -0.04, 0.02, "surround")
    if kind != "slider":
        pbox(mb, P3, s0, s1, z0 - 0.20, z0, -0.04, 0.02, "surround")


def baie(mb, P3, s0, s1, z0, z1, n, rect):
    """Salon sliding door onto the garden (client 19-10, reference photo): set back in a taupe stone
    reveal, a flat taupe band round it, slim beige aluminium frames on staggered leaves, sheer linen curtains
    hanging in folds (the third leaf left open) and the lit salon behind with its sofa."""
    W = s1 - s0
    fr, dg = 0.06, 0.30                               # frame width, glazing plane
    b = 0.26                                          # stone band, standing 0.03 proud
    pbox(mb, P3, s0 - b, s0, z0, z1 + b, -0.03, 0.02, "surround")
    pbox(mb, P3, s1, s1 + b, z0, z1 + b, -0.03, 0.02, "surround")
    pbox(mb, P3, s0, s1, z1, z1 + b, -0.03, 0.02, "surround")
    fb = lambda a0, a1, c0, c1, d0, d1: pbox(mb, P3, a0, a1, c0, c1, d0, d1, "frame_taupe")
    fb(s0, s1, z0, z0 + fr, dg - 0.05, dg + 0.05)    # outer frame, butt-jointed
    fb(s0, s1, z1 - fr, z1, dg - 0.05, dg + 0.05)
    fb(s0, s0 + fr, z0 + fr, z1 - fr, dg - 0.05, dg + 0.05)
    fb(s1 - fr, s1, z0 + fr, z1 - fr, dg - 0.05, dg + 0.05)
    lw = (W - 2 * fr) / n
    for k in range(n):                                # leaves on two tracks, overlapping 4 cm
        a0, a1 = s0 + fr + lw * k - (0.02 if k else 0.0), s0 + fr + lw * (k + 1) + (0.02 if k < n - 1 else 0.0)
        d = dg - 0.02 if k % 2 == 0 else dg + 0.02
        rect("glass", a0 + fr, a1 - fr, z0 + 2 * fr, z1 - 2 * fr, d)
        fb(a0, a0 + fr, z0 + fr, z1 - fr, d - 0.015, d + 0.015)
        fb(a1 - fr, a1, z0 + fr, z1 - fr, d - 0.015, d + 0.015)
        fb(a0 + fr, a1 - fr, z0 + fr, z0 + 2 * fr, d - 0.015, d + 0.015)
        fb(a0 + fr, a1 - fr, z1 - 2 * fr, z1 - fr, d - 0.015, d + 0.015)

    def curtain(a0, a1, d=0.46, pitch=0.11, amp=0.035):
        m = max(2, int((a1 - a0) / pitch))
        xs = [a0 + (a1 - a0) * j / m for j in range(m + 1)]
        for j in range(m):
            da, db = d + (amp if j % 2 else -amp), d + (-amp if j % 2 else amp)
            mb.poly("sheer", [P3(xs[j], z0 + 0.04, da), P3(xs[j + 1], z0 + 0.04, db),
                              P3(xs[j + 1], z1 + 0.02, db), P3(xs[j], z1 + 0.02, da)])
        pbox(mb, P3, a0 - 0.05, a1 + 0.05, z1 + 0.02, z1 + 0.05, d - 0.02, d + 0.02, "frame_taupe")   # rail
    curtain(s0 + fr, s0 + fr + 1.85 * lw)             # first leaf and most of the second
    curtain(s0 + fr + 2.95 * lw, s1 - fr)             # the fourth
    # the salon behind: warm walls, floor, ceiling, a linen sofa and a low table seen through the third leaf
    D = 3.40
    zc = z1 + 0.70
    rect("interior_warm", s0 - 0.40, s1 + 0.40, z0 - 0.01, zc, D)
    for a in (s0 - 0.40, s1 + 0.40):
        mb.poly("interior_warm", [P3(a, z0 - 0.01, 0.36), P3(a, z0 - 0.01, D), P3(a, zc, D), P3(a, zc, 0.36)])
    mb.poly("interior_floor", [P3(s0 - 0.40, z0 - 0.005, 0.36), P3(s1 + 0.40, z0 - 0.005, 0.36), P3(s1 + 0.40, z0 - 0.005, D), P3(s0 - 0.40, z0 - 0.005, D)])
    mb.poly("interior_warm", [P3(s0 - 0.40, zc, 0.36), P3(s0 - 0.40, zc, D), P3(s1 + 0.40, zc, D), P3(s1 + 0.40, zc, 0.36)])
    c = s0 + fr + 2.45 * lw                           # centre of the third leaf
    pbox(mb, P3, c - 1.20, c + 1.20, z0, z0 + 0.42, 2.20, 3.05, "sofa")          # seat
    pbox(mb, P3, c - 1.20, c + 1.20, z0 + 0.42, z0 + 0.82, 2.85, 3.10, "sofa")   # back
    for a in (c - 1.20, c + 1.00):                                                 # arms
        pbox(mb, P3, a, a + 0.20, z0 + 0.42, z0 + 0.62, 2.20, 3.05, "sofa")
    for k in range(3):                                                             # cushions
        a = c - 0.98 + 0.66 * k
        pbox(mb, P3, a, a + 0.62, z0 + 0.42, z0 + 0.56, 2.25, 2.85, "sofa_cushion")
    pbox(mb, P3, c - 0.55, c + 0.55, z0 + 0.30, z0 + 0.36, 1.25, 1.85, "door_wood")   # low table
    pbox(mb, P3, c - 0.45, c + 0.45, z0, z0 + 0.30, 1.35, 1.75, "door_wood")


def ext(mb, mat, poly, P, w0, w1):
    """Extrude a 2D (Multi)Polygon in (a, b) from w0 to w1; P(a, b, w) -> (x, y, z), any affine map."""
    o = P(0.0, 0.0, 0.0)
    A = [P(1.0, 0.0, 0.0)[i] - o[i] for i in range(3)]
    B = [P(0.0, 1.0, 0.0)[i] - o[i] for i in range(3)]
    W = [P(0.0, 0.0, 1.0)[i] - o[i] for i in range(3)]
    cr = (A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0])
    flip = (cr[0] * W[0] + cr[1] * W[1] + cr[2] * W[2]) * (w1 - w0) < 0
    fix = (lambda pts: pts[::-1]) if flip else (lambda pts: pts)
    for pg in L.as_polys(poly):
        for t in L.tri_poly(pg):
            mb.poly(mat, fix([P(a, b, w1) for a, b in t]), fix([(a, b) for a, b in t]))
            mb.poly(mat, fix([P(a, b, w0) for a, b in t[::-1]]), fix([(a, b) for a, b in t[::-1]]))
        for k, ring in enumerate([pg.exterior] + list(pg.interiors)):
            c = list(ring.coords)
            if ring.is_ccw == (k > 0):
                c = c[::-1]
            u = 0.0
            for (pa, pb), (qa, qb) in zip(c, c[1:]):
                lg = math.dist((pa, pb), (qa, qb))
                if lg < 1e-6:
                    continue
                mb.poly(mat, fix([P(pa, pb, w0), P(qa, qb, w0), P(qa, qb, w1), P(pa, pb, w1)]),
                        fix([(u, w0), (u + lg, w0), (u + lg, w1), (u, w1)]))
                u += lg


def prism_open(mb, mat, poly, z0, z1):
    """L.prism without the side faces that lie on the RDC outline (those come from wall())."""
    bound = RDC.exterior
    for pg in L.as_polys(poly):
        for t in L.tri_poly(pg):
            mb.poly(mat, [(x, y, z1) for x, y in t], [(x, y) for x, y in t])
        for k, ring in enumerate([pg.exterior] + list(pg.interiors)):
            c = list(ring.coords)
            if ring.is_ccw == (k > 0):
                c = c[::-1]
            for (ax_, ay_), (bx_, by_) in zip(c, c[1:]):
                lg = math.dist((ax_, ay_), (bx_, by_))
                if lg < 1e-6:
                    continue
                mid = ((ax_ + bx_) / 2, (ay_ + by_) / 2)
                if all(bound.distance(Point(pt)) < 1e-4 for pt in ((ax_, ay_), (bx_, by_), mid)):
                    continue
                mb.poly(mat, [(ax_, ay_, z0), (bx_, by_, z0), (bx_, by_, z1), (ax_, ay_, z1)], [(0, z0), (lg, z0), (lg, z1), (0, z1)])


def coping(mb, mat, poly, ztop, h=COP):
    """Rounded top: two thinner slices above the wall body (which stops at ztop - h)."""
    L.prism(mb, mat, poly.buffer(-0.022, join_style=1), ztop - h, ztop - h * 0.35)
    L.prism(mb, mat, poly.buffer(-0.065, join_style=1), ztop - h * 0.35, ztop)


def rafter(mb, s, x0, x1, ya, yb, z0, z1, mat="timber"):
    """Pergola rafter along y from ya (wall) to yb (free end, cut with a bevel underneath)."""
    sg = 1 if yb > ya else -1
    prof = Polygon([(ya, z0), (yb - sg * 0.16, z0), (yb, z1 - 0.06), (yb, z1), (ya, z1)])
    ext(mb, mat, prof, lambda a, b, w: (s * w, a, b), x0, x1)


def railing(mb, s, a, b, y0, y1, z0, z1, mat="timber"):
    """Wooden geometric railing ('Cadre en bois', façade arrière) between x = a and x = b."""
    t = 0.05
    X = lambda u: s * u
    n = max(1, round((b - a) / 1.10))
    wpan = (b - a) / n
    h = z1 - z0
    for i in range(n + 1):                                          # posts
        u = a + wpan * i
        mb.box(mat, X(max(a, u - t / 2)), X(min(b, u + t / 2)), y0, y1, z0, z1)
    for zz in (z0, z0 + h / 3 - t / 2, z0 + 2 * h / 3 - t / 2, z1 - t):   # rails
        mb.box(mat, X(a), X(b), y0, y1, zz, zz + t)
    for i in range(n):
        u0, u1 = a + wpan * i, a + wpan * (i + 1)
        for f in (0.30, 0.70):                                      # verticals of the top and bottom bands
            uc = u0 + (u1 - u0) * f
            mb.box(mat, X(uc - t / 2), X(uc + t / 2), y0, y1, z0, z0 + h / 3)
            mb.box(mat, X(uc - t / 2), X(uc + t / 2), y0, y1, z0 + 2 * h / 3, z1)
        ia, ib = u0 + 0.16, u1 - 0.16                               # nested rectangle in the middle band
        za, zb = z0 + h / 3 + 0.05, z0 + 2 * h / 3 - 0.08
        mb.box(mat, X(ia), X(ib), y0, y1, za, za + 0.035)
        mb.box(mat, X(ia), X(ib), y0, y1, zb - 0.035, zb)
        mb.box(mat, X(ia), X(ia + 0.035), y0, y1, za, zb)
        mb.box(mat, X(ib - 0.035), X(ib), y0, y1, za, zb)


def horn(mb, poly_uv, P):
    ext(mb, "villa", poly_uv, P, 0.0, 0.20)


def build(M, col, variant="A"):
    """One design for the whole tranche (the variant name is kept for the scene's placements)."""
    mb = C.MeshBuilder()
    M = dict(M)

    # ---- façades with their openings and niches -----------------------------------------------
    for p, q in edges(RDC):
        wall(mb, p, q, -1.00, rdc_top)                       # down to the foundation: the ground slopes
    for p, q in edges(ET):
        wall(mb, p, q, Z1, Z2)
    for p, q in edges(CAGE):
        wall(mb, p, q, Z2, Z_CW)

    # ---- terraces: floors, parapets, piers, separation walls on the joint -----------------------
    L.prism(mb, "terrace", RDC.difference(ET.buffer(-0.01, join_style=2)), Z1 - 0.01, Z1, sides=False)
    front = mirror(unary_union([box(SEP, YW, WX, YW + 0.20), box(WX - 0.20, YW, WX, YWE - 0.002)]))
    prism_open(mb, "villa", front, Z1, Z_PF - COP)
    coping(mb, "villa", front, Z_PF)
    high = [box(HX - 0.20, YRE + 0.002, HX, YR)] + [box(a, YR - 0.20, b, YR) for a, b in PIERS]
    high = mirror(unary_union(high))
    prism_open(mb, "villa", high, Z1, Z_PR - COP)
    coping(mb, "villa", high, Z_PR)
    spans = [(PIERS[i][1], PIERS[i + 1][0]) for i in range(len(PIERS) - 1)]
    curb = mirror(unary_union([box(a, YR - 0.20, b, YR) for a, b in spans]))
    prism_open(mb, "villa", curb, Z1, Z_CURB)
    for s in (1, -1):
        for a, b in spans:
            railing(mb, s, a, b, YR - 0.125, YR - 0.075, Z_CURB, Z_PR)
    sep_f = box(-SEP, YW, SEP, YWE - 0.002)                  # remark slide 10: up to the pergola
    L.prism(mb, "villa", sep_f, Z1, 7.20 - COP)
    coping(mb, "villa", sep_f, 7.20)
    sep_r = box(-SEP, YRE + 0.002, SEP, YR)
    L.prism(mb, "villa", sep_r, Z1, 6.90 - COP)
    coping(mb, "villa", sep_r, 6.90)

    # ---- cornice (grey ledge / ochre stone band / grey ledge), acrotère with rounded coping -----
    for z0, z1, pd, mat in [(7.22, 7.30, 0.13, "ledge"), (7.30, 7.46, 0.10, "band"), (7.46, 7.62, 0.16, "ledge")]:
        L.prism(mb, mat, ET.buffer(pd, join_style=2).difference(ET), z0, z1, bottom=True)
    ring = ET.difference(ET.buffer(-0.30, join_style=2)).difference(CAGE)
    L.prism(mb, "villa", ring, Z2, 7.62)
    soft = ET.buffer(-0.12, join_style=2).buffer(0.12, join_style=1)        # rounded outer corners
    ring_s = soft.difference(ET.buffer(-0.30, join_style=2)).difference(CAGE)
    L.prism(mb, "villa", ring_s, 7.62, Z_ACRO - 0.12)
    L.prism(mb, "villa", ring_s.buffer(-0.02, join_style=1), Z_ACRO - 0.12, Z_ACRO - 0.06)
    L.prism(mb, "villa", ring_s.buffer(-0.06, join_style=1), Z_ACRO - 0.06, Z_ACRO - 0.02)
    L.prism(mb, "villa", ring_s.buffer(-0.10, join_style=1), Z_ACRO - 0.02, Z_ACRO)
    L.prism(mb, "terrace", ET.buffer(-0.30, join_style=2).difference(CAGE), Z2 - 0.01, Z2, sides=False)
    # roof terraces of the two villas separated on the joint (plan TERRASSE), lower than the acrotère
    sep_t = box(-0.15, YWE + 0.10, 0.15, CY0 - 0.002)
    L.prism(mb, "villa", sep_t, Z2, 8.12 - COP)
    coping(mb, "villa", sep_t, 8.12)

    # ---- stair cage (+9.80): cornice, parapet (client 24-10: no horns on any house) -----------------
    for z0, z1, pd, mat in [(Z_CW, 9.10, 0.08, "ledge"), (9.10, 9.24, 0.07, "band"), (9.24, 9.40, 0.13, "ledge")]:
        L.prism(mb, mat, CAGE.buffer(pd, join_style=2).difference(CAGE), z0, z1, bottom=True)
    cring = CAGE.difference(CAGE.buffer(-0.20, join_style=2))
    L.prism(mb, "villa", cring, Z_CW, Z_CTOP - 0.08)
    coping(mb, "villa", cring, Z_CTOP, 0.08)
    L.prism(mb, "roof", CAGE.buffer(-0.20, join_style=2), 9.39, 9.40, sides=False)

    # ---- 'GT' ducts on the roof ------------------------------------------------------------------
    for s in (1, -1):
        mb.box("villa", s * 7.36, s * 7.89, -3.17, -2.97, Z2, 8.12)
        ext(mb, "villa", Polygon([(-3.17, 8.12)] + [(-3.07 - 0.10 * math.cos(math.pi * k / 8), 8.12 + 0.10 * math.sin(math.pi * k / 8)) for k in range(9)][1:] + [(-2.97, 8.12)]),
            lambda a, b, w, s=s: (s * w, a, b), 7.36, 7.89)
        mb.box("villa", s * 0.23, s * 0.92, -2.25, CY0 - 0.002, Z2, 7.80)
        mb.box("ledge", s * 0.20, s * 0.95, -2.28, CY0 - 0.002, 7.80, 7.86)

    # ---- pergolas (timber): rear terrace (15 rafters) and front terrace (7 rafters) ---------------
    T = "timber"
    for s in (1, -1):
        X = lambda u, s=s: s * u
        for xc in (0.30, 3.02, 5.21, 7.96):
            mb.box(T, X(xc - 0.065), X(xc + 0.065), 4.455, 4.585, Z1, 6.55)
        mb.box(T, X(SEP), X(HX + 0.10), 4.46, 4.58, 6.55, 6.75)
        mb.box(T, X(SEP), X(HX), YRE + 0.002, YRE + 0.08, 6.60, 6.75)
        for k in range(15):
            xc = 0.28 + 0.549 * k
            rafter(mb, s, xc - 0.03, xc + 0.03, YRE + 0.002, 4.98, 6.75, 6.90)
        for xc in (0.24, 3.24):
            mb.box(T, X(xc - 0.06), X(xc + 0.06), -6.82, -6.70, Z1, 6.85)
        mb.box(T, X(SEP), X(WX + 0.10), -6.82, -6.70, 6.85, 7.05)
        mb.box(T, X(SEP), X(WX), YWE - 0.08, YWE - 0.002, 6.90, 7.05)
        for k in range(7):
            xc = 0.30 + 0.515 * k
            rafter(mb, s, xc - 0.03, xc + 0.03, YWE - 0.002, -7.44, 7.05, 7.20)

    # ---- front garden wall (façade principale): stone cladding, coping, gate pillars, gate --------
    for s in (1, -1):
        X = lambda u, s=s: s * u
        for x0, x1, y0, y1 in [(5.35, 8.79, YW, YW + 0.25), (8.54, 8.79, YW + 0.25, -5.80)]:
            mb.box("cladding", X(x0), X(x1), y0, y1, -0.40, 0.70)
            mb.box("coping_beige", X(x0 - (0.03 if x0 > 5.4 else 0.0)), X(x1 + 0.03), y0 - 0.03, y1 + 0.03, 0.70, 0.78)
        for x0, x1 in ((WX + 0.002, 3.88), (4.97, 5.35)):
            mb.box("cladding", X(x0), X(x1), YW - 0.02, YW + 0.31, -0.40, 1.38)
            mb.box("coping_beige", X(x0 - 0.03 if x0 > 4 else x0), X(x1 + 0.03), YW - 0.05, YW + 0.34, 1.38, 1.46)
        for k in range(10):                                          # timber gate, vertical slats
            u = 3.92 + (4.93 - 3.92 - 0.07) * k / 9
            mb.box("door_wood", X(u), X(u + 0.07), YW + 0.10, YW + 0.14, 0.12, 1.30)
        for zz in (0.30, 1.10):
            mb.box("door_wood", X(3.90), X(4.95), YW + 0.14, YW + 0.18, zz, zz + 0.08)
        mb.box("coping_beige", X(WX + 0.002), X(4.95), -3.87, YF - 0.002, -0.30, 0.12)   # door step

    # the paved terrace behind the salons (REAR_TERRACE) is built by the scene on the graded ground

    obs = mb.build("DPX", col, M)
    ob = L.join(obs, f"SRC_DUPLEX_{variant}")
    L.weld(ob, 0.0003)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob
