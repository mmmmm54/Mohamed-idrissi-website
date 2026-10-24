"""
02_duplex — "DUPLEX JUMELEE" (permis de construire, 2-DUPLEX.DWG), exterior only.

Local frame (metres): origin = centre of the two stair cages on the roof plan, x along the pair
(-8.10 .. +8.10, joint de dilatation at x = 0), y towards the rear garden, front (access side) = -y.
z = 0 terrain naturel (T.N), RDC floor +0.20, etage floor +3.70, roof +7.50, acrotère +8.30,
stair cages +9.80 (niveaux on the facades and coupes A-A / B-B).

Read from the drawing:
  plans RDC / ETAGE / TERRASSE   outer walls ('mur extérieur'), parapets ('Mur gard cour'),
                                 pergola rafters and beams ('pergola'), terraces, access strips
  FACADE PRINCIPALE / ARRIERE    window and door sizes and heights (glazing sashes), mashrabiya
                                 panels ('motif en bois'), cornices, rows of square ornaments
  FACADE GAUCHE/DROIT            end-wall windows (sizes; positions from the RDC plan)
Interiors are not modelled (dark interior proxy behind the glass).
"""
import math

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

L = globals()["L"]          # lib module, injected by the scene script
C = L.C

Z_FL, Z1, Z2, Z_ACRO, Z_CAGE = 0.20, 3.70, 7.50, 8.30, 9.14
RDC = unary_union([box(-8.10, -3.47, 8.10, 5.35), box(-3.52, -7.27, 3.52, -3.47)])
ET = unary_union([box(-8.10, -3.47, 8.10, 2.05), box(-3.52, -5.87, 3.52, -3.47)])
CAGE = box(-3.37, -1.91, 3.37, 2.04)
REV = 0.20                  # reveal depth (outer leaf); frames sit 0.10 behind the face


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


def op(axis, c, u0, u1, z0, z1, kind, n=1):
    return {"axis": axis, "c": c, "u0": u0, "u1": u1, "z0": z0, "z1": z1, "kind": kind, "n": n}


# openings: axis 'y' = wall in the plane y = c (u = x); axis 'x' = wall in the plane x = c (u = y)
OPENINGS = mirror_x([
    # RDC front of the wing (FACADE PRINCIPALE): two french windows
    op("y", -7.27, -2.65, -0.90, Z_FL, 2.70, "french", 2),
    # RDC front of the side parts: entrance door next to the wing + glazed door
    op("y", -3.47, -4.55, -3.70, Z_FL, 2.75, "door"),
    # etage front of the side parts: two narrow windows each
    op("y", -3.47, -6.78, -6.23, 4.10, 6.05, "window", 1),
    op("y", -3.47, -5.43, -4.88, 4.10, 6.05, "window", 1),
    # etage front of the wing: double windows behind the wing terrace
    op("y", -5.87, -2.60, -0.85, 4.63, 6.00, "window", 2),
    # RDC rear (FACADE ARRIERE): 6-leaf glazing per house onto the garden terrace
    op("y", 5.35, -6.98, -0.65, Z_FL, 2.70, "slider", 6),
    # etage rear: double window, glazed door to the terrace, narrow window
    op("y", 2.05, -7.45, -5.20, 4.73, 6.12, "window", 2),
    op("y", 2.05, -4.95, -4.00, 3.75, 6.20, "french", 1),
    op("y", 2.05, -1.32, -0.87, 4.73, 6.00, "window", 1),
    # end walls (FACADE GAUCHE / DROIT sizes, positions from the RDC plan)
    op("x", -8.10, -2.27, -0.48, 0.96, 2.66, "window", 2),
    op("x", -8.10, 1.03, 1.62, 0.82, 2.66, "window", 1),
    op("x", -8.10, 3.46, 4.05, 0.82, 2.66, "window", 1),
]) + [
    # asymmetric on the drawing: left house double glazed door, right house single
    op("y", -3.47, -6.87, -5.12, Z_FL, 2.70, "french", 2),
    op("y", -3.47, 5.12, 6.02, Z_FL, 2.70, "french", 1),
]

# mashrabiya gaps in parapets: (axis, c, u0, u1)
GAP_RDC = [("y", 5.35, a, b) for a, b in [(-7.20, -4.60), (-3.53, -0.93), (0.93, 3.53), (4.60, 7.20)]] + \
          [("y", -7.27, a, b) for a, b in [(-3.00, -0.52), (0.52, 3.00)]]
GAP_ACRO = [("y", -3.47, a, b) for a, b in [(-6.76, -4.31), (4.31, 6.76)]] + \
           [("y", -5.87, a, b) for a, b in [(-3.00, -0.55), (0.55, 3.00)]] + \
           [("y", 2.05, a, b) for a, b in [(-6.95, -4.50), (4.50, 6.95)]] + \
           [("x", -8.10, -1.91, 0.49), ("x", 8.10, -1.91, 0.49)]


def edges(poly):
    c = list(poly.exterior.coords)
    if not poly.exterior.is_ccw:
        c = c[::-1]
    return list(zip(c, c[1:]))


def wall(mb, p, q, z0, z1, mat="render"):
    """Outer wall face p->q (CCW outline, outward normal on the right) with its openings."""
    (ax, ay), (bx, by) = p, q
    Lg = math.dist(p, q)
    ux, uy = (bx - ax) / Lg, (by - ay) / Lg
    nx, ny = uy, -ux                                  # outward normal
    axis = "y" if abs(uy) < 1e-6 else "x"
    cst = ay if axis == "y" else ax
    holes = []
    for o in OPENINGS:
        if o["axis"] != axis or abs(o["c"] - cst) > 0.03 or o["z1"] <= z0 or o["z0"] >= z1:
            continue
        # u along the face from p
        a = (o["u0"] - (ax if axis == "y" else ay)) / (ux if axis == "y" else uy)
        b = (o["u1"] - (ax if axis == "y" else ay)) / (ux if axis == "y" else uy)
        s0, s1 = sorted((a, b))
        if s0 < -0.01 or s1 > Lg + 0.01:
            continue
        holes.append((s0, s1, max(o["z0"], z0), min(o["z1"], z1), o))
    face = box(0, z0, Lg, z1)
    for s0, s1, h0, h1, _ in holes:
        face = face.difference(box(s0, h0, s1, h1))
    P3 = lambda s, z, d=0.0: (ax + ux * s - nx * d, ay + uy * s - ny * d, z)
    for t in L.tri_poly(face):
        mb.poly(mat, [P3(s, z) for s, z in t], [(s, z) for s, z in t])
    for s0, s1, h0, h1, o in holes:
        # reveals (jambs, head, sill) facing into the opening
        for (sa, za), (sb, zb) in [((s0, h1), (s0, h0)), ((s1, h0), (s1, h1)), ((s1, h1), (s0, h1)), ((s0, h0), (s1, h0))]:
            mb.poly(mat, [P3(sa, za), P3(sb, zb), P3(sb, zb, REV), P3(sa, za, REV)])
        insert(mb, P3, s0, s1, h0, h1, o)
    return holes


def insert(mb, P3, s0, s1, z0, z1, o):
    """Frame, mullions, glass, interior proxy, sill; or a timber door."""
    d = 0.10
    fr = 0.06

    def rect(mat, a0, a1, b0, b1, dd, flip=False):
        pts = [P3(a0, b0, dd), P3(a1, b0, dd), P3(a1, b1, dd), P3(a0, b1, dd)]
        mb.poly(mat, pts[::-1] if flip else pts, [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])

    def frame_box(a0, a1, b0, b1, mat="bronze"):
        for dd in (d - 0.03, d + 0.03):
            rect(mat, a0, a1, b0, b1, dd, flip=dd > d)
        mb.poly(mat, [P3(a0, b1, d - 0.03), P3(a1, b1, d - 0.03), P3(a1, b1, d + 0.03), P3(a0, b1, d + 0.03)])
        mb.poly(mat, [P3(a1, b0, d - 0.03), P3(a0, b0, d - 0.03), P3(a0, b0, d + 0.03), P3(a1, b0, d + 0.03)])
        mb.poly(mat, [P3(a0, b0, d - 0.03), P3(a0, b1, d - 0.03), P3(a0, b1, d + 0.03), P3(a0, b0, d + 0.03)])
        mb.poly(mat, [P3(a1, b1, d - 0.03), P3(a1, b0, d - 0.03), P3(a1, b0, d + 0.03), P3(a1, b1, d + 0.03)])

    rect("interior", s0 - 0.3, s1 + 0.3, z0 - 0.3, z1 + 0.3, 0.75)
    if o["kind"] == "door":
        rect("door_wood", s0, s1, z0, z1, d)
        w = s1 - s0
        rect("glass", s0 + w * 0.62, s0 + w * 0.80, z0 + 0.25, z1 - 0.25, d - 0.01)
        frame_box(s0, s1, z1 - fr, z1)
        frame_box(s0, s0 + fr, z0, z1)
        frame_box(s1 - fr, s1, z0, z1)
        return
    rect("glass", s0, s1, z0, z1, d)
    frame_box(s0, s1, z0, z0 + fr)
    frame_box(s0, s1, z1 - fr, z1)
    frame_box(s0, s0 + fr, z0, z1)
    frame_box(s1 - fr, s1, z0, z1)
    n = o["n"]
    for k in range(1, n):
        s = s0 + (s1 - s0) * k / n
        frame_box(s - fr / 2, s + fr / 2, z0, z1)
    if o["kind"] == "window":
        # stone sill + moulded surround (trim), proud of the face
        for (a0, a1, b0, b1, pd) in [(s0 - 0.12, s1 + 0.12, z0 - 0.08, z0, 0.06),
                                     (s0 - 0.12, s0, z0, z1 + 0.12, 0.035), (s1, s1 + 0.12, z0, z1 + 0.12, 0.035),
                                     (s0, s1, z1, z1 + 0.12, 0.035)]:
            proud_box(mb, P3, a0, a1, b0, b1, pd, "trim")
    else:
        for (a0, a1, b0, b1) in [(s0 - 0.10, s0, z0, z1 + 0.10), (s1, s1 + 0.10, z0, z1 + 0.10), (s0, s1, z1, z1 + 0.10)]:
            proud_box(mb, P3, a0, a1, b0, b1, 0.03, "trim")


def proud_box(mb, P3, a0, a1, b0, b1, pd, mat):
    """Box standing proud of the wall face by pd (face plane d = 0)."""
    f = lambda a, b: P3(a, b, -pd)
    w = lambda a, b: P3(a, b, 0.02)
    mb.poly(mat, [f(a0, b0), f(a1, b0), f(a1, b1), f(a0, b1)], [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])
    mb.poly(mat, [w(a0, b1), f(a0, b1), f(a1, b1), w(a1, b1)])
    mb.poly(mat, [w(a1, b0), f(a1, b0), f(a0, b0), w(a0, b0)])
    mb.poly(mat, [w(a0, b0), f(a0, b0), f(a0, b1), w(a0, b1)])
    mb.poly(mat, [w(a1, b1), f(a1, b1), f(a1, b0), w(a1, b0)])


def face_box(mb, axis, c, out_sign, u0, u1, z0, z1, pd, mat):
    """Proud box on a wall plane: axis 'y' -> plane y=c, outward = out_sign * y."""
    if axis == "y":
        y0, y1 = sorted((c - out_sign * 0.02, c + out_sign * pd))
        mb.box(mat, u0, u1, y0, y1, z0, z1)
    else:
        x0, x1 = sorted((c - out_sign * 0.02, c + out_sign * pd))
        mb.box(mat, x0, x1, u0, u1, z0, z1)


def gap_rects(gaps, t_in, t_out=0.3):
    out = []
    for axis, c, a, b in gaps:
        if axis == "y":
            out.append(box(a, c - t_in - t_out if c > 0 else c - t_out, b, c + t_out if c > 0 else c + t_in + t_out))
        else:
            out.append(box(c - t_in - t_out if c > 0 else c - t_out, a, c + t_out if c > 0 else c + t_in + t_out, b))
    return unary_union(out)


def mashrabiya(mb, axis, c, u0, u1, z0, z1, inset):
    """Lattice panel (alpha-cut texture) as two faces 3 cm apart, inset from the face."""
    sgn = 1 if c > 0 else -1
    for k, off in enumerate((inset, inset + 0.03)):
        cc = c - sgn * off
        uv = [(u0 / 0.5, z0 / 0.5), (u1 / 0.5, z0 / 0.5), (u1 / 0.5, z1 / 0.5), (u0 / 0.5, z1 / 0.5)]
        if axis == "y":
            pts = [(u0, cc, z0), (u1, cc, z0), (u1, cc, z1), (u0, cc, z1)]
        else:
            pts = [(cc, u0, z0), (cc, u1, z0), (cc, u1, z1), (cc, u0, z1)]
        if (sgn < 0) == (k == 0) if axis == "y" else (sgn > 0) == (k == 0):
            mb.poly("mashrabiya", pts, uv)
        else:
            mb.poly("mashrabiya", pts[::-1], uv[::-1])
    # thin timber frame around the panel
    for (a0, a1, b0, b1) in [(u0, u1, z0 - 0.04, z0), (u0, u1, z1, z1 + 0.04), (u0 - 0.04, u0, z0 - 0.04, z1 + 0.04), (u1, u1 + 0.04, z0 - 0.04, z1 + 0.04)]:
        if axis == "y":
            mb.box("mashrabiya_frame", a0, a1, c - sgn * (inset + 0.05), c - sgn * (inset - 0.02), b0, b1)
        else:
            mb.box("mashrabiya_frame", c - sgn * (inset + 0.05), c - sgn * (inset - 0.02), a0, a1, b0, b1)


def build(M, col):
    import bpy
    mb = C.MeshBuilder()
    M = dict(M)
    M["mashrabiya_frame"] = M["timber"]
    # ---- walls with openings ------------------------------------------------------------------
    for p, q in edges(RDC):
        wall(mb, p, q, 0.0, Z1)
    for p, q in edges(ET):
        wall(mb, p, q, Z1, Z2)
    # plinth (proud 4 cm) and roof caps
    L.prism(mb, "render_dark", RDC.buffer(0.04, join_style=2).difference(RDC.buffer(-0.05, join_style=2)), -1.00, Z_FL)
    L.prism(mb, "terrace", RDC.difference(ET.buffer(-0.01, join_style=2)), Z1 - 0.01, Z1, sides=False)
    L.prism(mb, "roof", ET.buffer(-0.19, join_style=2).difference(CAGE), Z2 - 0.01, Z2, sides=False)

    # ---- RDC-roof terrace parapets (rear terrace, wing terrace) -------------------------------
    t = 0.20
    rdc_par = unary_union([box(-8.10, 5.35 - t, 8.10, 5.35), box(-8.10, 2.05, -8.10 + t, 5.35), box(8.10 - t, 2.05, 8.10, 5.35),
                           box(-3.52, -7.27, 3.52, -7.27 + t), box(-3.52, -7.27, -3.52 + t, -5.87), box(3.52 - t, -7.27, 3.52, -5.87)])
    rdc_par = rdc_par.difference(gap_rects(GAP_RDC, t))
    L.prism(mb, "render", rdc_par, Z1, 4.90)
    L.prism(mb, "trim", rdc_par.buffer(0.03, join_style=2), 4.90, 4.97)
    for axis, c, a, b in GAP_RDC:
        mashrabiya(mb, axis, c, a, b, 3.85, 4.72, 0.06)
    # divider between the two houses on the RDC roof and in the rear garden
    mb.box("render", -0.22, 0.22, 2.05, 5.35, Z1, 5.50)
    mb.box("render", -0.22, 0.22, 5.35, 7.79, -0.80, 2.20)
    mb.box("trim", -0.25, 0.25, 5.35, 7.82, 2.20, 2.27)
    mb.box("trim", -0.25, 0.25, 2.05, 5.38, 5.50, 5.57)

    # ---- acrotère with mashrabiya, cornices ---------------------------------------------------
    acro = L.ring_poly(ET, 0.20).difference(gap_rects(GAP_ACRO, 0.20))
    L.prism(mb, "render", acro, Z2, 8.19)
    L.prism(mb, "trim", acro.buffer(0.04, join_style=2).intersection(ET.buffer(0.04, join_style=2)).difference(ET.buffer(-0.24, join_style=2)), 8.19, Z_ACRO)
    for axis, c, a, b in GAP_ACRO:
        mashrabiya(mb, axis, c, a, b, 7.52, 7.97, 0.06)
        g = gap_rects([(axis, c, a, b)], 0.2, 0.0)
        L.prism(mb, "trim", g.buffer(0.0), 7.97, 8.05)
    for z0, z1, pd in [(7.05, 7.20, 0.06), (7.20, 7.40, 0.14)]:
        L.prism(mb, "trim", ET.buffer(pd, join_style=2).difference(ET.buffer(-0.05, join_style=2)), z0, z1)
    L.prism(mb, "trim", RDC.buffer(0.05, join_style=2).difference(RDC.buffer(-0.05, join_style=2)).difference(ET.buffer(0.2, join_style=2)), 3.52, 3.70)

    # ---- stair cages (+9.80): walls, two-step cornice, crown with corner horns ----------------
    L.prism(mb, "render", CAGE, Z2, Z_CAGE)
    for z0, z1, pd in [(9.14, 9.28, 0.15), (9.28, 9.54, 0.40)]:
        L.prism(mb, "trim", CAGE.buffer(pd, join_style=2), z0, z1, bottom=True)
    crown = L.ring_poly(CAGE.buffer(0.10, join_style=2), 0.20)
    L.prism(mb, "render", crown, 9.54, 9.90)
    L.prism(mb, "trim", crown.buffer(0.03, join_style=2).difference(CAGE.buffer(-0.13, join_style=2)), 9.90, 9.96)
    for sx in (-1, 1):
        for sy, yc in ((-1, -1.91), (1, 2.04)):
            x0 = sx * 3.49 - (0.49 if sx > 0 else 0)
            y0 = yc + sy * 0.12 - (0.49 if sy > 0 else 0)
            mb.box("render", x0, x0 + 0.49, y0, y0 + 0.49, 9.545, 10.12)
            mb.box("trim", x0 - 0.03, x0 + 0.52, y0 - 0.03, y0 + 0.52, 10.12, 10.20)
    mb.box("render", -0.20, 0.20, -1.91, 2.04, 9.54, 9.90)       # joint between the two cages

    # ---- square ornaments (0.20 x 0.20) -------------------------------------------------------
    for x in (-7.43, -6.43, -5.42, -4.43):
        for s in (1, -1):
            face_box(mb, "y", -3.47, -1, s * x - 0.10, s * x + 0.10, 6.75, 6.95, 0.03, "trim")
    for k in range(7):
        for s in (1, -1):
            xr = s * (0.41 + k)
            face_box(mb, "y", 5.35, 1, xr - 0.10, xr + 0.10, 3.18, 3.38, 0.03, "trim")
            xe = s * (0.85 + k)
            face_box(mb, "y", 2.05, 1, xe - 0.10, xe + 0.10, 6.54, 6.74, 0.03, "trim")
    for k in range(-2, 3):
        y = -0.71 + k
        for sx in (-8.10, 8.10):
            face_box(mb, "x", sx, 1 if sx > 0 else -1, y - 0.10, y + 0.10, 6.45, 6.65, 0.03, "trim")
    for x in (-3, -2, -1, 1, 2, 3):
        face_box(mb, "y", -1.91, -1, x - 0.10, x + 0.10, 8.60, 8.80, 0.03, "trim")
        face_box(mb, "y", 2.04, 1, x - 0.10, x + 0.10, 8.60, 8.80, 0.03, "trim")
    face_box(mb, "y", 5.35, 1, -0.20, 0.20, 0.0, 7.40, 0.05, "render")          # axis pilaster, rear

    # ---- pergolas (plan TERRASSE, layer 'pergola') -------------------------------------------
    T = "timber"
    # rear: wall plate y 5.34-5.49, beam y 7.15-7.30, rafters 0.15 every 0.47 m out to y 7.79
    mb.box(T, -8.10, 8.10, 5.35, 5.49, 4.45, 4.70)
    mb.box(T, -8.10, 8.10, 7.15, 7.30, 4.45, 4.70)
    xs = [-8.10 + 0.4686 * i for i in range(35)]
    for x in xs:
        mb.box(T, x, x + 0.15, 5.35, 7.79, 4.70, 4.86)
    for x in (-8.02, 7.87):
        mb.box(T, x, x + 0.15, 7.15, 7.30, 0.20, 4.45)
    # front of the wing (etage terrace): wall plate y -6.02/-5.88, beam y -7.18/-7.03, rafters to y -7.46
    mb.box(T, -3.53, 3.47, -6.02, -5.87, 6.45, 6.70)
    mb.box(T, -3.53, 3.47, -7.18, -7.03, 6.33, 6.70)
    for i in range(16):
        x = -3.53 + 0.4686 * i
        mb.box(T, x, x + 0.15, -7.46, -5.87, 6.70, 6.88)
    for x in (-3.52, 3.32):
        mb.box("render", x, x + 0.20, -7.25, -7.05, 4.90, 6.33)
    # canopies over the side doors (hatched band on FACADE PRINCIPALE, z 2.85-3.65)
    for s in (-1, 1):
        a, b = sorted((s * 4.69, s * 7.29))
        for x in (a, b - 0.10):
            mb.box(T, x, x + 0.10, -4.47, -3.47, 3.30, 3.62)
        for i in range(11):
            x = a + (b - a - 0.06) * i / 10
            mb.box(T, x, x + 0.06, -4.47, -3.47, 3.62, 3.68)
        mashrabiya(mb, "y", -4.47, a + 0.10, b - 0.10, 2.92, 3.55, 0.0)

    # ---- garden-level terraces and access strips (plan RDC) ----------------------------------
    mb.box("terrace", -8.10, 8.10, 5.35, 7.79, -0.80, Z_FL)
    for s in (-1, 1):
        a, b = sorted((s * 8.10, s * 5.40))
        mb.box("terrace", a, b, -5.00, -3.47, -0.80, Z_FL)
        a, b = sorted((s * 5.40, s * 3.80))
        mb.box("slate", a, b, -9.50, -3.47, -0.80, 0.16)

    obs = mb.build("DPX", col, M)
    ob = L.join(obs, "SRC_DUPLEX")
    L.weld(ob, 0.0003)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob
