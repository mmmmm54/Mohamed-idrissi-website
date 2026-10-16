"""
imara_interior: the inside of the Imara Teal R+6, built into build_imara's geometry.

  floors 1-6    the plan "PLAN 1er, 2eme, 3eme et 4eme ETAGES": three flats (106, 110 and 118 m2), the
                stair, the lift and the spiral stair on the landing, and the courtyard. Doors, floor
                finishes, kitchens, bathrooms and furniture are placed as drawn. Floors 5 and 6 repeat
                the plan: its note gives the same courtyard void up to the 6th floor.
  ground floor  the entrance lobby to the stair and lift, the ramp enclosure, the shops as an open shell
  basement      parking under the ground-floor footprint. The ramp starts at the garage bay on the main
                street (X 0.37-3.38). Columns stay on the plan's structural grid.

Coordinates as in build_imara: metres, X along the main street, Y back along the side street, Z up,
origin at the left party wall on the main street line. Rectangles here are (x0, y0, x1, y1).
"""
import math

from shapely.geometry import Point
from shapely.geometry import box as R
from shapely.ops import unary_union
from shapely.prepared import prep

B = None                                      # the build_imara module, set by attach()

# ---------------------------------------------------------------------------
# Plan constants (from the plan's dimension lines and red column dots)
# ---------------------------------------------------------------------------
COLUMNS = [(0.12, 22.42), (6.73, 22.42), (11.71, 22.42), (15.66, 22.42),
           (0.11, 16.23), (3.74, 16.23), (9.99, 16.23), (15.66, 16.23),
           (3.73, 12.87), (10.61, 12.88), (15.66, 12.88), (0.11, 11.42), (3.74, 11.42),
           (10.61, 6.73), (15.65, 6.73), (0.11, 6.20), (6.74, 6.20),
           (0.11, 0.12), (10.61, 0.12), (15.65, 0.12)]
VOID = unary_union([R(0.15, 15.87, 3.65, 22.30), R(3.65, 16.70, 5.62, 22.30)])   # courtyard, floors 2-6
STAIR_HOLE = R(3.85, 12.55, 6.70, 16.50)
LIFT_HOLE = R(3.80, 9.65, 5.30, 11.30)
SPIRAL_HOLE = R(3.75, 7.70, 5.40, 9.50)
SPIRAL_C, SPIRAL_R = (4.575, 8.60), 0.78
MAIN = R(0.0, 0.0, 15.75, 22.50)
COURTYARD_OPEN = True                         # False: roof slab over the courtyard, as in the first model

# basement
Z_SS = -2.50                                  # finished parking floor
Z_RDC_SOFFIT = -0.30                          # underside of the ground-floor slab: 2.20 m clear
RAMP_X = (0.30, 3.50)
RAMP_Y = (0.30, 16.90)
RAMP_T = 2.0                                  # transitions at each end
VENT = R(0.30, 21.60, 4.50, 22.20)           # ventilation shaft under the plan's "lanterneau d'aeration"
TREMIE = R(0.30, 0.30, 3.50, 15.75)           # opening of the ground-floor slab over the ramp
LV_SS = "Niveau_-1_Sous-sol"


def attach(module):
    global B
    B = module


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def rects(geom):
    """Axis-aligned boxes (x0, y0, x1, y1) covering a rectilinear shapely geometry."""
    out = []
    polys = [geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]
    for pg in polys:
        if pg.area < 1e-5:
            continue
        pp = prep(pg)
        coords = list(pg.exterior.coords) + [c for r in pg.interiors for c in r.coords]
        xs = sorted({round(c[0], 4) for c in coords})
        ys = sorted({round(c[1], 4) for c in coords})
        live = {}
        for j in range(len(ys) - 1):
            ym = 0.5 * (ys[j] + ys[j + 1])
            runs, i = [], 0
            while i < len(xs) - 1:
                if pp.contains(Point(0.5 * (xs[i] + xs[i + 1]), ym)):
                    k = i
                    while k < len(xs) - 1 and pp.contains(Point(0.5 * (xs[k] + xs[k + 1]), ym)):
                        k += 1
                    runs.append((xs[i], xs[k]))
                    i = k
                else:
                    i += 1
            nxt = {r: live.pop(r) if r in live else ys[j] for r in runs}
            out += [(a, y0, b, ys[j]) for (a, b), y0 in live.items()]
            live = nxt
        out += [(a, y0, b, ys[-1]) for (a, b), y0 in live.items()]
    return [r for r in out if r[2] - r[0] > 1e-3 and r[3] - r[1] > 1e-3]


def U(*rs):
    return unary_union([R(*r) for r in rs])


def slab(geom, z0, z1, mat="white", faces=None):
    for x0, y0, x1, y1 in rects(geom):
        B.box(mat, x0, x1, y0, y1, z0, z1, faces=faces)


def finish(geom, z, mat, th=0.02):
    slab(geom, z, z + th, mat)


def uvf(mat):
    d = B.MAT_DEF[mat]
    return d[2], d[3]


def prism(mat, pts, z0, z1, top=True, bottom=True):
    """Vertical prism on a convex xy polygon given counter-clockwise."""
    if B.CUT[0] is not None:
        if z0 >= B.CUT[0]:
            return
        z1 = min(z1, B.CUT[0])
    tu, tv = uvf(mat)
    n = len(pts)
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        L = math.dist(a, b)
        B.poly(mat, [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)],
               [(0, z0 / tv), (L / tu, z0 / tv), (L / tu, z1 / tv), (0, z1 / tv)])
    if top:
        B.poly(mat, [(p[0], p[1], z1) for p in pts], [(p[0] / tu, p[1] / tv) for p in pts])
    if bottom:
        B.poly(mat, [(p[0], p[1], z0) for p in pts[::-1]], [(p[0] / tu, p[1] / tv) for p in pts[::-1]])


def obox(mat, cx, cy, z0, z1, lx, ly, ang):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(cx + c * u - s * v, cy + s * u + c * v) for u, v in
           ((-lx / 2, -ly / 2), (lx / 2, -ly / 2), (lx / 2, ly / 2), (-lx / 2, ly / 2))]
    prism(mat, pts, z0, z1)


def cyl(mat, cx, cy, r, z0, z1, n=20):
    prism(mat, [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)], z0, z1)


ROT = {"S": 0, "E": 90, "N": 180, "W": 270}   # furniture against this wall, facing into the room


class Fr:
    """Local frame for furniture: u along the wall, v from the wall into the room, z from the floor."""

    def __init__(self, x, y, wall, z):
        self.x, self.y, self.r, self.z = x, y, ROT[wall], z

    def w(self, u, v):
        return {0: (self.x + u, self.y + v), 90: (self.x - v, self.y + u),
                180: (self.x - u, self.y - v), 270: (self.x + v, self.y - u)}[self.r]

    def box(self, mat, u0, u1, v0, v1, z0, z1):
        a, b = self.w(u0, v0), self.w(u1, v1)
        B.box(mat, min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1]), self.z + z0, self.z + z1)

    def cyl(self, mat, u, v, r, z0, z1, n=16):
        x, y = self.w(u, v)
        cyl(mat, x, y, r, self.z + z0, self.z + z1, n)


def iwall(x0, x1, y0, y1, z0, z1, gaps=(), mat="paint", faces=None, h=2.10):
    """Interior wall; gaps are (a, b[, height]) along its length, with a lintel above."""
    along_x = (x1 - x0) >= (y1 - y0)
    a0, a1 = (x0, x1) if along_x else (y0, y1)
    pieces, cur = [], a0
    for g in sorted(gaps):
        g0, g1, gh = g[0], g[1], (g[2] if len(g) > 2 else h)
        pieces += [(cur, g0, z0, z1), (g0, g1, z0 + gh, z1)]
        cur = g1
    pieces.append((cur, a1, z0, z1))
    for p0, p1, za, zb in pieces:
        if p1 - p0 < 1e-4 or zb - za < 1e-4:
            continue
        if along_x:
            B.box(mat, p0, p1, y0, y1, za, zb, faces=faces)
        else:
            B.box(mat, x0, x1, p0, p1, za, zb, faces=faces)


def door(axis, c, a, b, z0, hinge="a", side=1, kind="int", t=0.10, ang=80.0, h=2.10):
    """Frame and leaf (open `ang` degrees) in the opening a..b of a wall centred on c; axis 'x' = the wall
    runs along X at y=c, 'y' = along Y at x=c. Hinge at end a or b, leaf swinging to the +side/-side."""
    leaf = {"int": "idoor", "bath": "idoor", "entry": "edoor", "fire": "door"}[kind]
    fmat = "edoor" if kind == "entry" else ("inox" if kind == "fire" else "idoor")
    ft = t / 2 + 0.02
    if axis == "x":
        B.box(fmat, a - 0.05, a, c - ft, c + ft, z0, z0 + h + 0.05)
        B.box(fmat, b, b + 0.05, c - ft, c + ft, z0, z0 + h + 0.05)
        B.box(fmat, a, b, c - ft, c + ft, z0 + h, z0 + h + 0.05)
        hx, hy = (a, c) if hinge == "a" else (b, c)
        cl = (1.0, 0.0) if hinge == "a" else (-1.0, 0.0)
        pp = (0.0, float(side))
    else:
        B.box(fmat, c - ft, c + ft, a - 0.05, a, z0, z0 + h + 0.05)
        B.box(fmat, c - ft, c + ft, b, b + 0.05, z0, z0 + h + 0.05)
        B.box(fmat, c - ft, c + ft, a, b, z0 + h, z0 + h + 0.05)
        hx, hy = (c, a) if hinge == "a" else (c, b)
        cl = (0.0, 1.0) if hinge == "a" else (0.0, -1.0)
        pp = (float(side), 0.0)
    hx, hy = hx + pp[0] * (t / 2 + 0.02), hy + pp[1] * (t / 2 + 0.02)
    th = math.radians(ang)
    d = (cl[0] * math.cos(th) + pp[0] * math.sin(th), cl[1] * math.cos(th) + pp[1] * math.sin(th))
    w = (b - a) - 0.02
    obox(leaf, hx + d[0] * w / 2, hy + d[1] * w / 2, z0 + 0.01, z0 + h - 0.01, w, 0.04, math.atan2(d[1], d[0]))
    ex, ey = hx + d[0] * (w - 0.08), hy + d[1] * (w - 0.08)
    n = (-d[1], d[0])
    for sgn in (1, -1):                                       # handles on both faces
        obox("inox", ex + n[0] * sgn * 0.045, ey + n[1] * sgn * 0.045, z0 + 1.02, z0 + 1.05, 0.14, 0.03, math.atan2(d[1], d[0]))


# ---------------------------------------------------------------------------
# Furniture (local frame Fr: u along the wall, v into the room)
# ---------------------------------------------------------------------------
def bed(x, y, wall, z, w=1.6, l=2.0, single=False):
    f = Fr(x, y, wall, z)
    hw = w / 2
    f.box("walnut", -hw - 0.05, hw + 0.05, 0.0, 0.05, 0.0, 1.10)
    f.box("headb", -hw, hw, 0.05, 0.13, 0.32, 1.02)
    f.box("walnut", -hw, hw, 0.05, l, 0.08, 0.32)
    f.box("duvet", -hw + 0.02, hw - 0.02, 0.13, l - 0.02, 0.32, 0.55)
    f.box("duvet", -hw - 0.015, hw + 0.015, 0.72, l + 0.015, 0.36, 0.585)
    f.box("gold", -hw - 0.02, hw + 0.02, l - 0.55, l - 0.30, 0.37, 0.595)
    pw = (w - 0.20) / (1 if single else 2)
    for k in range(1 if single else 2):
        u0 = -hw + 0.10 + k * pw
        f.box("duvet", u0 + 0.03, u0 + pw - 0.03, 0.16, 0.56, 0.55, 0.68)


def nightstand(x, y, wall, z):
    f = Fr(x, y, wall, z)
    f.box("walnut", -0.23, 0.23, 0.0, 0.40, 0.0, 0.50)
    f.box("inox", -0.20, 0.20, 0.40, 0.405, 0.30, 0.32)
    f.cyl("inox", 0.0, 0.20, 0.06, 0.50, 0.54)
    f.cyl("inox", 0.0, 0.20, 0.012, 0.54, 0.66, 8)
    f.cyl("shade", 0.0, 0.20, 0.13, 0.66, 0.86)


def wardrobe(x, y, wall, z, w=1.8, d=0.60, h=2.30):
    f = Fr(x, y, wall, z)
    f.box("oakf", -w / 2, w / 2, 0.0, d, 0.0, h)
    n = max(2, round(w / 0.6))
    for k in range(1, n):
        u = -w / 2 + w * k / n
        f.box("black", u - 0.004, u + 0.004, d, d + 0.004, 0.05, h - 0.05)
    for k in range(n):
        u = -w / 2 + w * (k + 0.5) / n + (0.12 if k % 2 == 0 else -0.12)
        f.box("inox", u - 0.012, u + 0.012, d, d + 0.03, 0.95, 1.35)


def dresser(x, y, wall, z, w=1.2):
    f = Fr(x, y, wall, z)
    f.box("walnut", -w / 2, w / 2, 0.0, 0.45, 0.10, 0.80)
    f.box("black", -w / 2 + 0.03, w / 2 - 0.03, 0.02, 0.43, 0.0, 0.10)
    for zz in (0.33, 0.56):
        f.box("black", -w / 2 + 0.02, w / 2 - 0.02, 0.45, 0.452, zz - 0.004, zz + 0.004)
    f.box("mirror", -0.40, 0.40, 0.0, 0.02, 1.10, 1.90)


def armchair(x, y, wall, z):
    f = Fr(x, y, wall, z)
    f.box("headb", -0.40, 0.40, 0.05, 0.80, 0.10, 0.42)
    f.box("headb", -0.40, 0.40, 0.05, 0.22, 0.42, 0.85)
    for u in (-0.40, 0.28):
        f.box("headb", u, u + 0.12, 0.05, 0.80, 0.42, 0.62)
    f.box("gold", -0.22, 0.22, 0.22, 0.36, 0.42, 0.72)


def console(x, y, wall, z, w=1.0):
    f = Fr(x, y, wall, z)
    f.box("walnut", -w / 2, w / 2, 0.0, 0.35, 0.10, 0.85)
    f.box("mirror", -0.35, 0.35, 0.0, 0.02, 1.15, 1.95)


def banquette(x0, y0, x1, y1, wall, z):
    """Moroccan salon bench (sedari) on the rectangle, back cushions against `wall`."""
    B.box("walnut", x0 + 0.02, x1 - 0.02, y0 + 0.02, y1 - 0.02, z, z + 0.28)
    B.box("sedari", x0, x1, y0, y1, z + 0.28, z + 0.44)
    bt = 0.16
    if wall == "N":
        B.box("sedari", x0, x1, y1 - bt, y1, z + 0.44, z + 0.92)
        n = max(1, int((x1 - x0) / 0.75))
        for k in range(n):
            u = x0 + (x1 - x0) * (k + 0.5) / n
            B.box("gold", u - 0.20, u + 0.20, y1 - bt - 0.12, y1 - bt, z + 0.44, z + 0.80)
    elif wall == "S":
        B.box("sedari", x0, x1, y0, y0 + bt, z + 0.44, z + 0.92)
        n = max(1, int((x1 - x0) / 0.75))
        for k in range(n):
            u = x0 + (x1 - x0) * (k + 0.5) / n
            B.box("gold", u - 0.20, u + 0.20, y0 + bt, y0 + bt + 0.12, z + 0.44, z + 0.80)
    elif wall == "E":
        B.box("sedari", x1 - bt, x1, y0, y1, z + 0.44, z + 0.92)
        n = max(1, int((y1 - y0) / 0.75))
        for k in range(n):
            v = y0 + (y1 - y0) * (k + 0.5) / n
            B.box("gold", x1 - bt - 0.12, x1 - bt, v - 0.20, v + 0.20, z + 0.44, z + 0.80)
    else:
        B.box("sedari", x0, x0 + bt, y0, y1, z + 0.44, z + 0.92)
        n = max(1, int((y1 - y0) / 0.75))
        for k in range(n):
            v = y0 + (y1 - y0) * (k + 0.5) / n
            B.box("gold", x0 + bt, x0 + bt + 0.12, v - 0.20, v + 0.20, z + 0.44, z + 0.80)


def mida(x, y, z, r=0.55):
    """Low round table of the Moroccan salon, with a tea tray."""
    cyl("walnut", x, y, r * 0.55, z, z + 0.36, 16)
    cyl("walnut", x, y, r, z + 0.36, z + 0.41, 28)
    cyl("inox", x, y, 0.24, z + 0.41, z + 0.43, 20)
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.4
        cyl("gold", x + 0.13 * math.cos(a), y + 0.13 * math.sin(a), 0.03, z + 0.43, z + 0.52, 10)
    cyl("inox", x, y, 0.05, z + 0.43, z + 0.60, 12)


def dining(x, y, z, lx=1.40, ly=0.90, seats=6):
    """Table centred on (x, y), long side along X, chairs around."""
    B.box("walnut", x - lx / 2, x + lx / 2, y - ly / 2, y + ly / 2, z + 0.72, z + 0.76)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.box("walnut", x + sx * (lx / 2 - 0.08) - 0.03, x + sx * (lx / 2 - 0.08) + 0.03,
                  y + sy * (ly / 2 - 0.08) - 0.03, y + sy * (ly / 2 - 0.08) + 0.03, z, z + 0.72)
    per = 2 if seats <= 4 else 3
    for k in range(per if seats > 4 else 2):
        u = x - lx / 2 + lx * (k + 0.5) / (per if seats > 4 else 2)
        chair(u, y - ly / 2 - 0.05, "S", z, back_away=True)
        chair(u, y + ly / 2 + 0.05, "N", z, back_away=True)


def chair(x, y, side, z, back_away=True):
    """Dining chair at the table edge point (x, y); side = the table side it stands on."""
    ux, uy = {"S": (0, -1), "N": (0, 1), "E": (1, 0), "W": (-1, 0)}[side]
    cx, cy = x + ux * 0.22, y + uy * 0.22
    B.box("oakf", cx - 0.21, cx + 0.21, cy - 0.21, cy + 0.21, z + 0.42, z + 0.47)
    B.box("headb", cx - 0.19, cx + 0.19, cy - 0.19, cy + 0.19, z + 0.47, z + 0.50)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.box("oakf", cx + sx * 0.18 - 0.02, cx + sx * 0.18 + 0.02, cy + sy * 0.18 - 0.02, cy + sy * 0.18 + 0.02, z, z + 0.42)
    bx, by = cx + ux * 0.19, cy + uy * 0.19
    if ux == 0:
        B.box("oakf", bx - 0.20, bx + 0.20, by - 0.02, by + 0.02, z + 0.47, z + 0.92)
    else:
        B.box("oakf", bx - 0.02, bx + 0.02, by - 0.20, by + 0.20, z + 0.47, z + 0.92)


def kitchen_run(x, y, wall, z, w, sink=None, hob=None, fridge=None, uppers=True):
    """Base cabinets 0.60 deep along a wall, centred on (x, y); sink/hob/fridge at u offsets."""
    f = Fr(x, y, wall, z)
    hw = w / 2
    f.box("black", -hw + 0.02, hw - 0.02, 0.0, 0.54, 0.0, 0.10)
    f.box("cabinet", -hw, hw, 0.0, 0.58, 0.10, 0.86)
    f.box("counter", -hw, hw, 0.0, 0.62, 0.86, 0.90)
    n = max(1, round(w / 0.6))
    for k in range(1, n):
        u = -hw + w * k / n
        f.box("black", u - 0.003, u + 0.003, 0.58, 0.584, 0.12, 0.84)
    for k in range(n):
        u = -hw + w * (k + 0.5) / n
        f.box("inox", u - 0.12, u + 0.12, 0.58, 0.60, 0.78, 0.80)
    if sink is not None:
        f.box("inox", sink - 0.40, sink + 0.40, 0.08, 0.52, 0.90, 0.905)
        f.box("black", sink - 0.36, sink + 0.36, 0.12, 0.48, 0.905, 0.907)
        f.box("inox", sink - 0.02, sink + 0.02, 0.04, 0.08, 0.90, 1.18)
        f.box("inox", sink - 0.02, sink + 0.02, 0.04, 0.26, 1.15, 1.18)
    if hob is not None:
        f.box("blackglass", hob - 0.30, hob + 0.30, 0.06, 0.56, 0.90, 0.907)
        f.box("inox", hob - 0.45, hob + 0.45, 0.0, 0.50, 1.55, 1.60)
        f.box("inox", hob - 0.15, hob + 0.15, 0.0, 0.25, 1.60, 2.30)
    if uppers:
        f.box("cabinet", -hw, hw, 0.0, 0.35, 1.50, 2.20)
        for k in range(1, n):
            u = -hw + w * k / n
            f.box("black", u - 0.003, u + 0.003, 0.35, 0.354, 1.52, 2.18)
        f.box("led", -hw + 0.05, hw - 0.05, 0.25, 0.30, 1.485, 1.50)
    if fridge is not None:
        f.box("inox", fridge - 0.32, fridge + 0.32, 0.0, 0.66, 0.0, 1.86)
        f.box("black", fridge - 0.32, fridge + 0.32, 0.66, 0.664, 1.20, 1.205)
        f.box("black", fridge + 0.24, fridge + 0.26, 0.66, 0.70, 0.60, 1.10)


def shower(x0, y0, x1, y1, z, glass=("E",)):
    B.box("ceramic", x0, x1, y0, y1, z, z + 0.05)
    B.box("inox", x0 + 0.05, x0 + 0.12, y0 + 0.05, y0 + 0.12, z + 0.05, z + 0.055)
    for g in glass:
        if g == "E":
            B.box("rail", x1 - 0.015, x1, y0, y1, z + 0.05, z + 2.00)
        elif g == "W":
            B.box("rail", x0, x0 + 0.015, y0, y1, z + 0.05, z + 2.00)
        elif g == "N":
            B.box("rail", x0, x1, y1 - 0.015, y1, z + 0.05, z + 2.00)
        else:
            B.box("rail", x0, x1, y0, y0 + 0.015, z + 0.05, z + 2.00)


def wc(x, y, wall, z):
    f = Fr(x, y, wall, z)
    f.box("ceramic", -0.20, 0.20, 0.0, 0.17, 0.0, 0.82)
    f.box("inox", -0.06, 0.06, 0.17, 0.175, 0.70, 0.76)
    f.box("ceramic", -0.18, 0.18, 0.17, 0.68, 0.0, 0.40)
    f.box("ceramic", -0.19, 0.19, 0.17, 0.70, 0.40, 0.43)


def vanity(x, y, wall, z, w=0.80):
    f = Fr(x, y, wall, z)
    f.box("walnut", -w / 2, w / 2, 0.0, 0.47, 0.38, 0.84)
    f.box("ceramic", -w / 2 - 0.01, w / 2 + 0.01, 0.0, 0.50, 0.84, 0.88)
    f.box("ceramic", -0.22, 0.22, 0.10, 0.42, 0.88, 0.98)
    f.box("inox", -0.02, 0.02, 0.03, 0.06, 0.88, 1.10)
    f.box("inox", -0.02, 0.02, 0.03, 0.16, 1.08, 1.10)
    f.box("mirror", -w / 2, w / 2, 0.0, 0.015, 1.10, 1.95)
    f.box("led", -w / 2, w / 2, 0.015, 0.02, 1.95, 1.98)


def rug(x0, y0, x1, y1, z):
    B.box("rug", x0, x1, y0, y1, z, z + 0.008)


def ceiling_light(x, y, zc, r=0.20):
    cyl("inox", x, y, r + 0.02, zc - 0.035, zc, 24)
    cyl("light", x, y, r, zc - 0.04, zc - 0.035, 24)


def pendant(x, y, zc, zlow, r=0.35):
    cyl("inox", x, y, 0.006, zlow + 0.20, zc, 6)
    cyl("shade", x, y, r, zlow, zlow + 0.20, 28)
    cyl("light", x, y, r * 0.7, zlow - 0.005, zlow, 20)


# ---------------------------------------------------------------------------
# Stairs and lift
# ---------------------------------------------------------------------------
def stair_flights(zb, zt):
    """Dog-leg stair from the floor landing (south, Y 11.45-12.55) at zb to the next at zt."""
    h = zt - zb
    nf = 2 if h <= 3.4 else 4
    m = max(5, round(h / nf / 0.175))
    r = h / (nf * m)
    g = 0.28
    run = (m - 1) * g
    y_s, y_n = 12.55, 12.55 + run
    z = zb
    for k in range(nf):
        west = (k % 2 == 0)
        x0, x1 = (3.85, 5.25) if west else (5.35, 6.70)
        for i in range(1, m):
            ztop = z + i * r
            if west:
                ya, yb = y_s + (i - 1) * g, y_s + i * g
            else:
                ya, yb = y_n - i * g, y_n - (i - 1) * g
            B.box("granite", x0, x1, ya, yb, ztop - r, ztop)
            B.box("white", x0, x1, ya, yb, ztop - r - 0.16, ztop - r)
        zl = z + m * r                                       # landing at the end of the flight
        if west:
            B.box("white", 3.85, 6.70, y_n, 16.50, zl - 0.18, zl - 0.02)
            B.box("granite", 3.85, 6.70, y_n, 16.50, zl - 0.02, zl)
        elif k < nf - 1:
            B.box("white", 3.85, 6.70, 11.45, y_s, zl - 0.18, zl - 0.02)
            B.box("granite", 3.85, 6.70, 11.45, y_s, zl - 0.02, zl)
        # handrail on the inner edge, rising with the flight
        xr = 5.24 if west else 5.36
        ya, yb = (y_s, y_n) if west else (y_n, y_s)
        za, zbb = z + r + 0.90, z + (m - 1) * r + 0.90
        L = math.hypot(yb - ya, zbb - za)
        for j in range(int(L / 0.30) + 1):
            t = j / max(1, int(L / 0.30))
            yy = ya + (yb - ya) * t
            zz = za + (zbb - za) * t
            B.box("steel", xr - 0.01, xr + 0.01, yy - 0.01, yy + 0.01, zz - 0.88, zz)
        nseg = 8
        for j in range(nseg):
            t0, t1 = j / nseg, (j + 1) / nseg
            ym0, ym1 = ya + (yb - ya) * t0, ya + (yb - ya) * t1
            zm0, zm1 = za + (zbb - za) * t0, za + (zbb - za) * t1
            B.poly("steel", [(xr - 0.025, ym0, zm0), (xr - 0.025, ym1, zm1), (xr + 0.025, ym1, zm1), (xr + 0.025, ym0, zm0)],
                   [(0, 0), (1, 0), (1, 1), (0, 1)])
        z = zl


def lift_doors(z0):
    B.box("inox", 5.455, 5.50, 9.95, 10.85, z0, z0 + 2.20)              # landing frame
    B.box("inox", 5.36, 5.40, 10.00, 10.395, z0, z0 + 2.10)
    B.box("inox", 5.36, 5.40, 10.405, 10.80, z0, z0 + 2.10)
    B.box("black", 5.50, 5.51, 11.00, 11.12, z0 + 1.00, z0 + 1.25)
    B.box("light", 5.51, 5.512, 11.04, 11.08, z0 + 1.10, z0 + 1.14)


def core_walls(z0, zc, stair_door=True, sas=False):
    iwall(3.65, 3.85, 11.30, 14.35, z0, zc)
    iwall(3.65, 3.85, 14.35, 16.70, z0, zc, faces={"-X": "white"})
    iwall(6.70, 6.85, 11.45, 16.50, z0, zc, gaps=[(11.55, 12.45)] if stair_door else ())
    iwall(3.65, 6.85, 11.30, 11.45, z0, zc, gaps=[(5.60, 6.50)] if sas else ())
    iwall(5.30, 5.45, 9.50, 11.30, z0, zc, gaps=[(10.00, 10.80, 2.20)])
    iwall(3.65, 3.80, 9.50, 11.30, z0, zc)
    iwall(3.65, 5.45, 9.50, 9.65, z0, zc)
    lift_doors(z0)
    if stair_door:
        door("y", 6.775, 11.55, 12.45, z0, hinge="a", side=-1, kind="fire", t=0.15)
    if sas:
        door("x", 11.375, 5.60, 6.50, z0, hinge="b", side=-1, kind="fire", t=0.15)


def spiral_level(zb, zt):
    cx, cy = SPIRAL_C
    n = 18
    r = (zt - zb) / n
    a0 = math.radians(25)
    for i in range(n):
        a, b = a0 + math.radians(20 * i), a0 + math.radians(20 * i + 22)
        ztop = zb + (i + 1) * r
        pts = [(cx + 0.07 * math.cos(a), cy + 0.07 * math.sin(a))]
        for k in range(4):
            t = a + (b - a) * k / 3
            pts.append((cx + SPIRAL_R * math.cos(t), cy + SPIRAL_R * math.sin(t)))
        pts.append((cx + 0.07 * math.cos(b), cy + 0.07 * math.sin(b)))
        prism("granite", pts, ztop - 0.05, ztop)
        t = 0.5 * (a + b)
        obox("steel", cx + SPIRAL_R * math.cos(t), cy + SPIRAL_R * math.sin(t), ztop, ztop + 0.90, 0.02, 0.02, 0)
        obox("steel", cx + (SPIRAL_R - 0.01) * math.cos(t), cy + (SPIRAL_R - 0.01) * math.sin(t), ztop + 0.88, ztop + 0.92,
             0.05, SPIRAL_R * 0.36, t)
    cyl("steel", cx, cy, 0.06, zb, zt, 16)


# ---------------------------------------------------------------------------
# Typical floor (floors 1-6)
# ---------------------------------------------------------------------------
def envelope():
    full = R(0.05, -1.45, 17.20, 22.45)
    out = unary_union([R(-1, -2, 2.02, 0.0), R(6.33, -2, 10.51, 0.0), R(13.96, -2, 18, 0.0),
                       R(15.97, 6.85, 18, 9.63), R(15.75, 9.63, 18, 12.76), R(15.86, 16.26, 18, 22.30)])
    return full.difference(out)


def teal_foot():
    xo, yo = B.X_OUT + B.TEAL_PROJ, B.Y_OUT - B.TEAL_PROJ
    return unary_union([R(B.FRONT_TEAL_X0, yo, xo, 0.0), R(B.RDC_W, 0.0, xo, B.SIDE_TEAL_Y1)])


def floor_slab(f):
    L = B.FL[f - 1]
    env = envelope()
    if f == 1:                    # over the ground floor: the courtyard floor, the ground-floor ceiling
        slab(env.intersection(MAIN).difference(unary_union([STAIR_HOLE, LIFT_HOLE, VENT])), L - 0.20, L)
        slab(env.difference(MAIN), L - 0.40, L)
        return
    g = env.difference(unary_union([VOID, STAIR_HOLE, LIFT_HOLE, SPIRAL_HOLE]))
    if B.teal_at(L):
        g = g.difference(teal_foot())
    slab(g, L - 0.20, L)


ROOMS = {   # name: (finish, rectangles)
    "hall106": ("tile", [(6.85, 12.96, 11.62, 14.33), (10.10, 14.33, 11.62, 20.14)]),
    "kitchen106": ("tile", [(6.85, 14.45, 10.00, 18.88)]),
    "bed1_106": ("parquet", [(5.78, 19.02, 9.38, 22.30)]),
    "bath106": ("bath", [(9.49, 20.24, 11.62, 22.30)]),
    "bed2_106": ("parquet", [(11.73, 19.30, 15.72, 22.30)]),
    "bed3_106": ("parquet", [(11.73, 16.25, 15.72, 19.19)]),
    "salon106": ("tile", [(11.73, 12.96, 17.00, 16.15)]),
    "hall110": ("tile", [(9.03, 7.98, 11.75, 9.50), (10.65, 5.25, 11.75, 7.98), (11.75, 5.25, 13.37, 6.60),
                         (12.25, 2.43, 13.37, 5.25)]),
    "salon110": ("tile", [(9.03, 9.60, 15.08, 12.76)]),
    "kitchen110": ("tile", [(11.85, 6.70, 15.75, 9.47)]),
    "bath110a": ("bath", [(9.05, 5.15, 10.55, 7.88)]),
    "bath110b": ("bath", [(10.65, 2.43, 12.15, 5.15)]),
    "bedF110": ("parquet", [(10.76, -1.25, 13.71, 0.0), (10.65, 0.0, 13.82, 2.33)]),
    "bed362": ("parquet", [(13.45, 3.40, 17.00, 6.62)]),
    "bed322": ("parquet", [(13.92, 0.20, 17.00, 3.30)]),
    "hall118": ("tile", [(2.45, 6.30, 8.88, 8.10), (2.45, 5.67, 4.40, 6.30), (3.30, 3.05, 4.40, 5.67),
                         (7.90, 5.15, 8.88, 6.30)]),
    "lobby118": ("parquet", [(2.45, 8.20, 3.65, 10.27)]),
    "bed348": ("parquet", [(0.15, 10.27, 3.65, 14.16)]),
    "bath118a": ("bath", [(0.15, 7.88, 2.35, 10.17)]),
    "bath118b": ("bath", [(0.15, 5.67, 2.35, 7.78)]),
    "bed366": ("parquet", [(0.15, 2.02, 3.20, 5.57)]),
    "bedF118": ("parquet", [(2.27, -1.25, 6.08, 0.0), (2.22, 0.0, 6.15, 1.82), (3.30, 1.82, 4.40, 2.95)]),
    "salon118": ("tile", [(4.50, 2.02, 7.80, 6.20)]),
    "kitchen118": ("tile", [(7.90, 0.62, 10.50, 5.00)]),
    "landing": ("granite", [(5.45, 8.25, 8.88, 11.45), (6.85, 11.45, 8.88, 12.76), (3.85, 11.45, 6.70, 12.55)]),
    "loggia": ("terrace", [(0.90, 0.0, 2.02, 0.20), (0.15, 0.20, 2.02, 1.82)]),
    "recess": ("terrace", [(6.33, -1.50, 10.51, 0.48), (6.33, 0.48, 7.80, 1.85)]),
    "corner": ("terrace", [(13.96, -1.50, 17.25, 0.0)]),
    "balconyB": ("terrace", [(15.97, 6.85, 17.25, 9.63), (15.27, 9.63, 17.25, 12.76)]),
    "balconyD": ("terrace", [(15.86, 16.26, 17.25, 21.50), (15.86, 21.50, 17.00, 22.30)]),
    "court118": ("terrace", [(0.15, 14.35, 3.65, 15.87)]),
    "court106": ("terrace", [(5.62, 16.70, 6.70, 18.88)]),
}
LIGHTS = [(8.5, 13.6), (10.86, 17.2), (8.4, 15.6), (8.6, 17.8), (7.6, 20.6), (10.5, 21.2), (13.7, 20.8),
          (13.7, 17.7), (13.4, 14.55), (15.4, 14.55), (11.0, 11.1), (13.4, 11.1), (13.8, 8.1), (10.2, 8.7),
          (12.6, 5.8), (9.8, 6.5), (11.4, 3.8), (12.2, 0.6), (15.2, 5.0), (15.45, 1.75), (6.1, 4.1),
          (9.2, 2.8), (5.5, 7.0), (1.25, 9.0), (1.25, 6.7), (1.7, 3.8), (1.9, 12.2), (4.2, 0.3), (7.2, 10.0)]


def typical_walls(z0, zc):
    w = lambda x0, x1, y0, y1, gaps=(), **k: iwall(x0, x1, y0, y1, z0, zc, gaps, **k)
    # core: stair, lift, spiral box, landing
    core_walls(z0, zc)
    w(3.65, 3.75, 7.60, 9.50)
    w(3.65, 5.45, 7.60, 7.70)
    w(5.40, 5.50, 7.70, 9.50, [(8.85, 9.45)])
    w(5.50, 8.90, 8.10, 8.25, [(7.60, 8.50)])
    w(8.88, 9.03, 5.00, 12.76, [(8.30, 9.30)])
    w(6.85, 15.27, 12.76, 12.96, [(7.05, 8.05)])
    # flat 106 (back right)
    w(6.85, 10.10, 14.33, 14.45)
    w(10.00, 10.10, 14.45, 18.88, [(16.40, 17.68, 2.30)])
    w(6.85, 10.10, 18.88, 19.02)
    w(9.38, 9.49, 19.02, 22.30, [(19.05, 19.85)])
    w(9.49, 11.62, 20.14, 20.24, [(9.55, 10.30)])
    w(11.62, 11.73, 12.96, 22.30, [(14.55, 16.15, 2.30), (18.32, 19.12), (19.38, 20.10)])
    w(11.73, 15.72, 19.19, 19.30)
    w(11.73, 15.75, 16.15, 16.25)
    # flat 110 (front right)
    w(9.03, 9.90, 9.50, 9.60)
    w(11.75, 15.08, 9.47, 9.63)
    w(11.75, 11.85, 7.66, 9.47)
    w(9.03, 10.65, 7.88, 7.98)
    w(10.55, 10.65, 5.15, 7.88, [(7.00, 7.72)])
    w(7.80, 10.65, 5.00, 5.15, [(7.90, 8.70)])
    w(11.75, 15.75, 6.60, 6.70)
    w(10.65, 12.25, 5.15, 5.25)
    w(12.15, 12.25, 2.43, 5.15)
    w(13.37, 13.45, 2.43, 6.60, [(2.50, 3.25), (3.45, 4.20)])
    w(13.45, 17.00, 3.30, 3.40)
    w(10.65, 13.92, 2.33, 2.43, [(11.40, 12.10), (12.40, 13.25)])
    w(13.82, 13.92, 0.20, 2.33)
    w(10.50, 10.65, 0.0, 5.15)
    # flat 118 (left)
    w(0.15, 2.45, 10.17, 10.27)
    w(2.35, 2.45, 7.88, 10.17, [(9.25, 10.00)])
    w(0.15, 2.45, 7.78, 7.88)
    w(2.35, 2.45, 5.67, 7.78, [(6.77, 7.47)])
    w(2.45, 3.65, 8.10, 8.20, [(2.65, 3.40)])
    w(0.15, 3.30, 5.57, 5.67)
    w(3.20, 3.30, 1.82, 5.57, [(4.65, 5.45)])
    w(4.40, 4.50, 2.02, 6.30)
    w(3.30, 4.40, 2.95, 3.05, [(3.62, 4.40)])
    w(2.22, 3.30, 1.82, 1.95)
    w(4.40, 6.85, 6.20, 6.30)
    w(4.40, 6.15, 1.85, 2.02)
    w(7.80, 7.90, 2.02, 5.50)


def typical_doors(z0):
    def d(axis, c, a, b, **k):
        door(axis, c, a, b, z0, **k)
    d("x", 12.86, 7.05, 8.05, hinge="a", side=1, kind="entry", t=0.20)          # A: flat 106
    d("y", 8.955, 8.30, 9.30, hinge="a", side=1, kind="entry", t=0.15)          # B: flat 110
    d("x", 8.175, 7.60, 8.50, hinge="b", side=-1, kind="entry", t=0.15)         # C: flat 118
    d("y", 5.45, 8.85, 9.45, hinge="b", side=-1, t=0.10)                        # spiral stair
    d("y", 9.435, 19.05, 19.85, hinge="a", side=-1)
    d("x", 20.19, 9.55, 10.30, hinge="a", side=1, kind="bath")
    d("y", 11.675, 19.38, 20.10, hinge="b", side=1)
    d("y", 11.675, 18.32, 19.12, hinge="a", side=1)
    d("y", 10.60, 7.00, 7.72, hinge="b", side=-1, kind="bath")
    d("x", 2.38, 11.40, 12.10, hinge="b", side=1, kind="bath")
    d("x", 2.38, 12.40, 13.25, hinge="a", side=-1, ang=50)
    d("y", 13.41, 3.45, 4.20, hinge="b", side=1)
    d("y", 13.41, 2.50, 3.25, hinge="a", side=1)
    d("x", 8.15, 2.65, 3.40, hinge="a", side=1)
    d("y", 2.40, 9.25, 10.00, hinge="b", side=-1, kind="bath")
    d("y", 2.40, 6.77, 7.47, hinge="b", side=-1, kind="bath")
    d("y", 3.25, 4.65, 5.45, hinge="b", side=-1)
    d("x", 3.00, 3.62, 4.40, hinge="b", side=-1)
    d("x", 5.075, 7.90, 8.70, hinge="a", side=-1)


def typical_finishes(f, z0):
    for name, (mat, rs) in ROOMS.items():
        g = U(*rs)
        if name == "hall118":
            g = g.difference(R(3.65, 7.60, 5.50, 9.50))
        if name == "landing":
            g = g.difference(R(5.40, 7.60, 5.50, 9.50))
        if f == 1 and name in ("court118", "court106"):
            continue                                     # level with the courtyard floor
        finish(g, z0, mat)
    if f == 1:                                           # the courtyard on the ground-floor roof
        court = unary_union([VOID, R(0.15, 14.35, 3.65, 15.87), R(5.62, 16.70, 6.70, 18.88)]).difference(VENT)
        finish(court, z0, "terrace")
        lanterneau(z0)
        for x, y, s in ((1.0, 16.6, 1.3), (5.0, 17.6, 1.1), (2.6, 16.6, 1.0)):
            B.plant(x, y, z0 + 0.02, s)


def lanterneau(z0):
    """'Lanterneau d'aeration' of the plan: louvred lantern over the ventilation shaft."""
    x0, y0, x1, y1 = VENT.bounds
    B.box("white", x0 - 0.10, x1 + 0.10, y0 - 0.10, y0, z0, z0 + 0.30)
    B.box("white", x1, x1 + 0.10, y0, y1, z0, z0 + 0.30)
    for k in range(7):
        zz = z0 + 0.32 + k * 0.06
        B.box("frame", x0 - 0.08, x1 + 0.08, y0 - 0.08, y0 - 0.06, zz, zz + 0.035)
    B.box("frame", x0 - 0.10, x1 + 0.10, y0 - 0.10, y1, z0 + 0.74, z0 + 0.80)
    for x in (x0 - 0.10, x1 + 0.02):
        B.box("frame", x, x + 0.08, y0 - 0.10, y0 - 0.02, z0 + 0.30, z0 + 0.74)


def typical_furniture(z):
    # flat 106
    bed(7.70, 22.30, "N", z, 1.8)
    nightstand(6.50, 22.30, "N", z)
    nightstand(8.90, 22.30, "N", z)
    wardrobe(9.38, 21.00, "E", z, 1.6)
    dresser(7.60, 19.02, "S", z, 1.2)
    armchair(5.78, 20.30, "W", z)
    rug(6.40, 19.70, 9.00, 21.00, z)
    shower(9.55, 21.50, 10.45, 22.30, z, ("E", "S"))
    wc(11.62, 21.75, "E", z)
    vanity(11.62, 20.80, "E", z, 0.8)
    kitchen_run(8.40, 14.45, "S", z, 3.10, sink=0.55, fridge=1.20)
    kitchen_run(6.85, 15.75, "W", z, 1.40, hob=0.0)
    dining(8.60, 17.80, z, 1.40, 0.90, 6)
    banquette(11.73, 12.96, 17.00, 13.66, "S", z)
    banquette(16.30, 13.66, 17.00, 16.15, "E", z)
    banquette(12.43, 15.45, 16.30, 16.15, "N", z)
    banquette(11.73, 13.66, 12.43, 14.50, "W", z)
    rug(12.90, 13.95, 15.90, 15.20, z)
    mida(14.40, 14.57, z)
    bed(12.80, 22.30, "N", z, 0.9, single=True)
    bed(14.40, 22.30, "N", z, 0.9, single=True)
    nightstand(13.60, 22.30, "N", z)
    wardrobe(11.73, 21.25, "W", z, 1.6)
    bed(13.50, 16.25, "S", z, 1.8)
    nightstand(12.30, 16.25, "S", z)
    nightstand(14.70, 16.25, "S", z)
    wardrobe(11.73, 17.55, "W", z, 1.4)
    dresser(14.30, 19.19, "N", z, 1.2)
    console(9.70, 12.96, "S", z, 1.0)
    B.plant(6.30, 17.20, z, 0.9)
    # flat 110
    banquette(9.03, 9.60, 9.73, 12.06, "W", z)
    banquette(9.03, 12.06, 15.08, 12.76, "N", z)
    banquette(14.38, 9.60, 15.08, 12.06, "E", z)
    banquette(11.85, 9.60, 14.38, 10.30, "S", z)
    rug(10.20, 10.55, 13.90, 11.80, z)
    mida(11.30, 11.15, z)
    mida(13.10, 11.15, z, 0.45)
    kitchen_run(13.75, 9.47, "N", z, 3.80, sink=-0.60, fridge=-1.55)
    kitchen_run(11.85, 8.30, "W", z, 1.10, hob=0.0)
    dining(13.80, 7.70, z, 1.40, 0.85, 4)
    vanity(9.05, 7.25, "W", z, 0.7)
    wc(9.05, 6.35, "W", z)
    shower(9.65, 5.15, 10.55, 6.05, z, ("N",))
    shower(10.65, 4.25, 11.60, 5.15, z, ("E", "S"))
    wc(10.65, 3.70, "W", z)
    vanity(10.65, 2.95, "W", z, 0.7)
    bed(10.65, 1.30, "W", z, 0.9, single=True)
    bed(10.76, -0.55, "W", z, 0.9, single=True)
    nightstand(10.65, 0.38, "W", z)
    wardrobe(13.82, 1.25, "E", z, 1.6)
    bed(15.40, 3.40, "S", z, 1.8)
    nightstand(14.20, 3.40, "S", z)
    nightstand(16.60, 3.40, "S", z)
    dresser(15.45, 6.62, "N", z, 1.2)
    wardrobe(13.45, 5.50, "W", z, 1.4)
    bed(15.45, 3.30, "N", z, 1.8)
    nightstand(14.25, 3.30, "N", z)
    nightstand(16.65, 3.30, "N", z)
    dresser(14.70, 0.20, "S", z, 1.0)
    rug(14.30, 0.60, 16.60, 1.90, z)
    # flat 118
    bed(0.15, 12.35, "W", z, 1.8)
    nightstand(0.15, 11.15, "W", z)
    nightstand(0.15, 13.55, "W", z)
    dresser(3.65, 12.25, "E", z, 1.2)
    wardrobe(3.65, 9.25, "E", z, 1.6)
    rug(1.20, 11.10, 2.90, 13.60, z)
    vanity(0.15, 9.65, "W", z, 0.7)
    shower(0.15, 7.88, 1.05, 8.75, z, ("E", "N"))
    wc(1.75, 7.88, "S", z)
    vanity(0.15, 7.20, "W", z, 0.7)
    shower(0.15, 5.67, 1.05, 6.55, z, ("E", "N"))
    wc(1.75, 5.67, "S", z)
    bed(0.15, 4.50, "W", z, 0.9, single=True)
    bed(0.15, 2.90, "W", z, 0.9, single=True)
    nightstand(0.15, 3.70, "W", z)
    wardrobe(3.20, 3.10, "E", z, 1.6)
    bed(2.27, 0.35, "W", z, 1.8)
    nightstand(2.27, -0.85, "W", z)
    nightstand(2.27, 1.55, "W", z)
    wardrobe(6.08, -0.45, "E", z, 1.5)
    dresser(4.70, -1.25, "S", z, 1.0)
    banquette(4.50, 2.02, 5.20, 6.20, "W", z)
    banquette(5.20, 5.50, 6.80, 6.20, "N", z)
    banquette(5.20, 2.02, 6.30, 2.72, "S", z)
    banquette(7.10, 2.72, 7.80, 5.40, "E", z)
    rug(5.40, 3.00, 6.90, 5.30, z)
    mida(6.15, 4.10, z)
    kitchen_run(9.68, 5.00, "N", z, 1.64, hob=0.0)
    kitchen_run(10.50, 3.15, "E", z, 2.50, sink=-0.40, fridge=0.90)
    dining(8.85, 1.85, z, 1.20, 0.80, 4)
    console(6.20, 8.10, "N", z, 1.0)
    B.plant(1.60, 0.40, z, 1.0)
    B.plant(0.50, 15.40, z, 0.9)
    B.plant(7.40, 1.50, z, 0.8)


def typical_floor(f):
    z0 = B.FL[f - 1]
    zc = (B.ROOF - 0.40) if f == 6 else B.FL[f] - 0.20
    floor_slab(f)
    typical_walls(z0, zc)
    typical_doors(z0)
    typical_finishes(f, z0)
    typical_furniture(z0 + 0.02)
    for x, y in LIGHTS:
        ceiling_light(x, y, zc)
        B.lamp("POINT", (x, y, zc - 0.12), 45, 0.12)
    stair_flights(z0, B.FL[f] if f < 6 else B.ROOF)
    if f < 6:
        spiral_level(z0, B.FL[f])


# ---------------------------------------------------------------------------
# Roof slab
# ---------------------------------------------------------------------------
def roof_slab():
    roof = unary_union([R(2.02, -1.55, 17.30, 0.0), R(0.0, 0.0, 17.30, 21.50), R(0.0, 21.50, 17.0, 22.50)])
    holes = [STAIR_HOLE, LIFT_HOLE] + ([VOID] if COURTYARD_OPEN else [])
    g = roof.difference(unary_union(holes))
    slab(g, B.ROOF - 0.40, B.ROOF)
    inner = roof.buffer(-0.22, join_style=2).difference(unary_union(
        [R(3.50, 11.10, 6.90, 16.70), R(3.45, 9.30, 5.65, 11.40)] + ([VOID.buffer(0.22, join_style=2)] if COURTYARD_OPEN else [])))
    inner = inner.difference(unary_union([R(2.40, -1.20, 5.80, -0.50), R(10.80, -1.20, 13.60, -0.50)]))
    finish(inner, B.ROOF, "roof")
    if COURTYARD_OPEN:                                   # parapet round the courtyard light well
        top = B.ROOF + 0.90
        B.box("white", 3.65, 5.84, 16.48, 16.70, B.ROOF, top)
        B.box("white", 5.62, 5.84, 16.70, 22.30, B.ROOF, top)
        B.box("white", 3.65, 3.87, 15.65, 16.70, B.ROOF, top)
        B.box("white", 0.20, 3.87, 15.65, 15.87, B.ROOF, top)
        B.box("party", 0.0, 0.15, 15.87, 22.30, B.ROOF - 0.40, B.ROOF)      # party walls up to the parapet
        B.box("party", 0.0, 5.84, 22.30, 22.50, B.ROOF - 0.40, B.ROOF)
    # stair house: hollow, door on the east side at the landing; lift overrun
    zt = B.ROOF + 2.60
    iwall(3.60, 3.80, 11.20, 16.60, B.ROOF, zt, mat="white", faces={"+X": "paint"})
    iwall(6.60, 6.80, 11.20, 16.60, B.ROOF, zt, gaps=[(11.55, 12.45)], mat="white", faces={"-X": "paint"})
    iwall(3.80, 6.60, 11.20, 11.40, B.ROOF, zt, mat="white", faces={"+Y": "paint"})
    iwall(3.80, 6.60, 16.40, 16.60, B.ROOF, zt, mat="white", faces={"-Y": "paint"})
    B.box("white", 3.50, 6.90, 11.10, 16.70, zt, zt + 0.15)
    door("y", 6.70, 11.55, 12.45, B.ROOF, hinge="a", side=1, kind="fire", t=0.20)
    B.box("white", 3.45, 5.65, 9.30, 11.20, B.ROOF, B.ROOF + 1.70)
    B.box("white", 3.40, 5.70, 9.25, 11.25, B.ROOF + 1.70, B.ROOF + 1.82)


# ---------------------------------------------------------------------------
# Ground floor: lobby, ramp enclosure, shops
# ---------------------------------------------------------------------------
def rdc_interior():
    zc = B.H_RDC - 0.20
    g = MAIN.difference(unary_union([TREMIE, STAIR_HOLE, LIFT_HOLE, VENT]))
    slab(g, -0.30, 0.0)
    lobby = unary_union([R(3.65, 0.30, 7.00, 8.25), R(3.65, 8.10, 8.88, 12.76)]).difference(
        unary_union([R(3.65, 9.50, 5.45, 11.45), R(3.65, 11.30, 6.85, 16.70)]))
    finish(lobby, 0.0, "lobby")
    finish(R(3.85, 11.45, 6.70, 12.55), 0.0, "granite")
    shops = R(0.30, 0.30, 15.45, 22.20).difference(unary_union(
        [R(0.30, 0.30, 3.65, 15.90), R(3.50, 0.30, 7.15, 8.25), R(3.50, 8.10, 9.03, 12.96),
         R(3.65, 9.50, 5.45, 11.45), R(3.65, 11.30, 6.85, 16.70), VENT.buffer(0.15, join_style=2)]))
    finish(shops, 0.0, "polished")
    # ramp enclosure (the garage passage over the ramp)
    iwall(3.50, 3.65, 0.30, 15.90, 0.0, zc, mat="paint", faces={"-X": "white"})
    iwall(3.65, 6.85, 16.50, 16.70, 0.0, zc)                    # back wall of the stair
    iwall(0.30, 3.50, 15.75, 15.90, 0.0, zc, mat="white", faces={"+Y": "paint"})
    # lobby walls
    iwall(7.00, 7.15, 0.30, 8.10, 0.0, zc)
    iwall(7.00, 8.90, 8.10, 8.25, 0.0, zc)
    iwall(8.88, 9.03, 8.10, 12.76, 0.0, zc)
    iwall(6.85, 9.03, 12.76, 12.96, 0.0, zc)
    core_walls(0.0, zc)
    stair_flights(0.0, B.FL[0])
    # ventilation shaft through the ground floor
    iwall(0.30, 4.65, 21.45, 21.60, 0.0, zc, mat="paint")
    iwall(4.50, 4.65, 21.60, 22.20, 0.0, zc, mat="paint")
    # columns standing in the shop shell
    for x, y in COLUMNS:
        if 0.4 < x < 15.3 and 0.4 < y < 22.0 and not (3.5 < x < 7.0 and 9.3 < y < 16.8):
            B.box("white", x - 0.15, x + 0.15, y - 0.15, y + 0.15, 0.0, zc)
    # lobby design: wood slat wall with a mirror and bench, mailboxes, pendants, mat
    for k in range(34):
        y = 0.55 + k * 0.26
        B.box("wood", 3.65, 3.70, y, y + 0.16, 0.0, 3.40)
    B.box("led", 3.65, 3.68, 0.50, 9.30, 3.40, 3.43)
    B.box("mirror", 3.70, 3.72, 3.20, 5.60, 0.95, 2.45)
    B.box("walnut", 3.70, 4.15, 3.00, 5.80, 0.40, 0.46)
    B.box("black", 3.72, 4.10, 3.05, 5.75, 0.0, 0.40)
    for i in range(6):
        for j in range(3):
            y0, z0 = 2.40 + i * 0.42, 1.05 + j * 0.34
            B.box("inox", 6.96, 7.00, y0, y0 + 0.40, z0, z0 + 0.32)
            B.box("black", 6.955, 6.96, y0 + 0.08, y0 + 0.32, z0 + 0.22, z0 + 0.25)
    B.box("black", 4.20, 6.20, 0.45, 1.65, 0.0, 0.012)
    for y in (2.6, 5.4, 9.8):
        pendant(5.30, y, zc, 3.10, 0.40)
        B.lamp("POINT", (5.30, y, 3.0), 160, 0.15)
    B.lamp("AREA", (7.70, 10.6, zc - 0.05), 120, (1.5, 1.5))
    B.plant(6.60, 7.60, 0.0, 1.3)
    B.plant(6.60, 0.80, 0.0, 1.1)


# ---------------------------------------------------------------------------
# Basement parking, ramp and the street entrance
# ---------------------------------------------------------------------------
def ramp_z(y):
    """Ramp surface level along Y: 0 at the door, -2.50 at the foot, 2 m transitions at each end."""
    y0, y1 = RAMP_Y
    Lm = (y1 - y0) - 2 * RAMP_T
    s = -Z_SS / (Lm + RAMP_T)
    d = min(max(y - y0, 0.0), y1 - y0)
    if d <= RAMP_T:
        return -s * d * d / (2 * RAMP_T)
    if d <= RAMP_T + Lm:
        return -(s * RAMP_T / 2 + s * (d - RAMP_T))
    e = (y1 - y0) - d
    return Z_SS + s * e * e / (2 * RAMP_T)


def ramp_slope():
    y0, y1 = RAMP_Y
    return -Z_SS / ((y1 - y0) - RAMP_T)


def ramp():
    x0, x1 = RAMP_X
    y0, y1 = RAMP_Y
    n = int(round((y1 - y0) / 0.25))
    ys = [y0 + (y1 - y0) * k / n for k in range(n + 1)]
    tu, tv = uvf("ramp")
    acc = [0.0]
    for k in range(n):
        acc.append(acc[-1] + math.hypot(ys[k + 1] - ys[k], ramp_z(ys[k + 1]) - ramp_z(ys[k])))
    xa, xb = x0 + 0.22, x1 - 0.22
    for k in range(n):
        ya, yb = ys[k], ys[k + 1]
        za, zb = ramp_z(ya), ramp_z(yb)
        B.poly("ramp", [(xa, ya, za), (xb, ya, za), (xb, yb, zb), (xa, yb, zb)],
               [(xa / tu, acc[k] / tv), (xb / tu, acc[k] / tv), (xb / tu, acc[k + 1] / tv), (xa / tu, acc[k + 1] / tv)])
        B.poly("white", [(x0, yb, zb - 0.22), (x1, yb, zb - 0.22), (x1, ya, za - 0.22), (x0, ya, za - 0.22)],
               [(0, 0), (1, 0), (1, 1), (0, 1)])
        for c0, c1 in ((x0, xa), (xb, x1)):                 # wheel curbs, painted
            m = "yellow" if (k // 2) % 2 == 0 else "black"
            B.poly(m, [(c0, ya, za + 0.15), (c1, ya, za + 0.15), (c1, yb, zb + 0.15), (c0, yb, zb + 0.15)],
                   [(0, 0), (1, 0), (1, 1), (0, 1)])
            side = c1 if c0 == x0 else c0
            pts = [(side, ya, za), (side, yb, zb), (side, yb, zb + 0.15), (side, ya, za + 0.15)]
            B.poly(m, pts if c0 == x0 else pts[::-1], [(0, 0), (1, 0), (1, 1), (0, 1)])
        # teal band and LED line on both walls, 0.90-1.15 m above the ramp, following the slope
        for xw, sgn in ((x0 + 0.004, 1), (x1 - 0.004, -1)):
            for (h0, h1, m) in ((0.90, 1.15, "teal"), (1.15, 1.18, "led")):
                q = [(xw, ya, za + h0), (xw, yb, zb + h0), (xw, yb, zb + h1), (xw, ya, za + h1)]
                B.poly(m, q if sgn < 0 else q[::-1], [(0, 0), (1, 0), (1, 1), (0, 1)])
    for c0, c1 in ((x0, xa), (xb, x1)):
        B.poly("yellow", [(c0, y0, 0.0), (c1, y0, 0.0), (c1, y0, 0.15), (c0, y0, 0.15)], [(0, 0), (1, 0), (1, 1), (0, 1)])
    # trench drains at the top and the foot, and the sump grate
    B.box("black", x0, x1, 0.32, 0.50, ramp_z(0.4) - 0.01, ramp_z(0.4) + 0.004)
    B.box("black", x0, x1, 16.95, 17.15, Z_SS, Z_SS + 0.006)
    B.box("black", 0.55, 1.35, 17.30, 18.10, Z_SS, Z_SS + 0.006)


def digit(ch, x, y, z, hgt, mat, ax="Y", flip=False):
    """Painted 7-segment digit lying on the floor (z) or on a wall plane; x, y = lower-left corner."""
    segs = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
            "7": "abc", "8": "abcdefg", "9": "abcfgd", "-": "g"}[ch]
    w, t = hgt * 0.55, hgt * 0.12
    pos = {"a": (0, hgt - t, w, hgt), "g": (0, hgt / 2 - t / 2, w, hgt / 2 + t / 2), "d": (0, 0, w, t),
           "f": (0, hgt / 2, t, hgt), "b": (w - t, hgt / 2, w, hgt), "e": (0, 0, t, hgt / 2), "c": (w - t, 0, w, hgt / 2)}
    for s in segs:
        u0, v0, u1, v1 = pos[s]
        if ax == "floor":
            if flip:
                B.box(mat, x - u1, x - u0, y - v1, y - v0, z, z + 0.004)
            else:
                B.box(mat, x + u0, x + u1, y + v0, y + v1, z, z + 0.004)
        elif ax == "wallY":                                   # on a wall facing -Y at y, reading along +X
            B.box(mat, x + u0, x + u1, y - 0.006, y, z + v0, z + v1)
        else:                                                 # on a wall facing +X at x, reading along -Y... along +Y
            B.box(mat, x, x + 0.006, y + u0, y + u1, z + v0, z + v1)


BAYS = [  # (x0, y0, x1, y1, nose side) parking bays, 5.00 m (N1: compact 4.40 m)
    (7.00, 1.90, 9.70, 6.90, "S"), (10.80, 1.90, 13.12, 6.90, "S"), (13.12, 1.90, 15.45, 6.90, "S"),
    (7.20, 12.45, 9.70, 16.85, "N"),
]
PARALLEL = [(4.65, 20.00, 10.05, 22.20), (10.15, 20.00, 15.45, 22.20)]


def bay_lines(x0, y0, x1, y1, open_side, z):
    lw = 0.10
    if open_side in ("N", "S"):
        for x in (x0, x1 - lw):
            B.box("line", x, x + lw, y0, y1, z, z + 0.004)
        yb = y0 if open_side == "N" else y1 - lw
        B.box("line", x0, x1, yb, yb + lw, z, z + 0.004)
    else:
        for y in (y0, y1 - lw):
            B.box("line", x0, x1, y, y + lw, z, z + 0.004)


def basement():
    B.LEVEL[0] = LV_SS
    zf, zc = Z_SS, Z_RDC_SOFFIT
    B.box("concrete", 0.0, 15.75, 0.0, 22.50, zf - 0.30, zf - 0.02)
    floor = R(0.30, 0.30, 15.45, 22.20).difference(unary_union(
        [R(0.30, 0.30, 3.65, RAMP_Y[1]), R(3.65, 11.30, 6.85, 16.70), R(3.65, 9.50, 5.45, 11.45),
         VENT.buffer(0.15, join_style=2)]))
    finish(floor, zf - 0.02, "epoxy")
    finish(R(0.30, 0.30, 3.50, 2.00), zf - 0.02, "concrete")
    # retaining walls, columns, core
    B.box("concrete", 0.0, 0.30, 0.0, 22.50, zf - 0.30, zc)
    B.box("concrete", 15.45, 15.75, 0.0, 22.50, zf - 0.30, zc)
    B.box("concrete", 0.30, 15.45, 0.0, 0.30, zf - 0.30, zc)
    B.box("concrete", 0.30, 15.45, 22.20, 22.50, zf - 0.30, zc)
    for x, y in COLUMNS:
        if 0.4 < x < 15.3 and 0.4 < y < 22.0 and not (3.5 < x < 4.0):
            B.box("white", x - 0.15, x + 0.15, y - 0.15, y + 0.15, zf, zc)
            B.box("teal", x - 0.155, x + 0.155, y - 0.155, y + 0.155, zf + 1.00, zf + 1.30)
            for k in range(4):
                m = "yellow" if k % 2 == 0 else "black"
                B.box(m, x - 0.16, x + 0.16, y - 0.16, y + 0.16, zf + k * 0.08, zf + (k + 1) * 0.08)
    # wall design: teal band at 1.00-1.30 m and a grey dado below it on the parking walls
    for x0, x1, y0, y1 in ((0.30, 0.31, RAMP_Y[1], 22.20), (15.44, 15.45, 0.30, 22.20),
                           (7.00, 15.45, 0.30, 0.31), (4.65, 15.45, 22.19, 22.20)):
        B.box("teal", x0, x1, y0, y1, zf + 1.00, zf + 1.30)
        B.box("dado", x0, x1, y0, y1, zf, zf + 1.00)
    core_walls(zf, zc, stair_door=False, sas=True)
    iwall(3.65, 6.85, 16.50, 16.70, zf, zc)                     # back wall of the stair
    stair_flights(zf, 0.0)
    iwall(6.85, 7.00, 9.35, 11.45, zf, zc, gaps=[(9.80, 10.70)])
    iwall(5.45, 7.00, 9.35, 9.50, zf, zc)
    door("y", 6.925, 9.80, 10.70, zf, hinge="a", side=1, kind="fire", t=0.15)
    # under the ramp: pump room at the front, the water tank behind it
    iwall(3.50, 3.65, 0.30, RAMP_Y[1], zf, zc, gaps=[(0.60, 1.50, 2.00)], mat="concrete", faces={"-X": "white"})
    door("y", 3.575, 0.60, 1.50, zf, hinge="a", side=1, kind="fire", t=0.15)
    B.box("concrete", 0.30, 3.50, 2.00, 2.20, zf, ramp_z(2.2) - 0.22)
    B.box("concrete", 0.30, 3.50, 11.00, 11.20, zf, ramp_z(11.1) - 0.22)
    for k, (x, y) in enumerate(((0.80, 1.00), (1.60, 1.00), (2.40, 1.00))):
        cyl("teal" if k < 2 else "red", x, y, 0.22, zf, zf + 0.90, 16)
        cyl("inox", x, y, 0.05, zf + 0.90, zf + 1.30, 8)
    B.box("inox", 0.40, 3.40, 1.45, 1.55, zf + 1.30, zf + 1.40)
    B.box("black", 2.80, 3.40, 1.85, 1.99, zf + 0.20, zf + 0.80)
    # ventilation shaft (the lanterneau above) with its louvred grille
    iwall(0.30, 4.65, 21.45, 21.60, zf, zc, mat="concrete")
    iwall(4.50, 4.65, 21.60, 22.20, zf, zc, mat="concrete")
    for k in range(9):
        zz = zf + 1.40 + k * 0.08
        B.box("frame", 0.80, 4.20, 21.43, 21.45, zz, zz + 0.05)
    B.LEVEL[0] = "Niveau_0_RDC"                 # hung from the ground-floor slab: hidden with it in the plan views
    B.box("inox", 4.65, 13.0, 21.20, 21.80, zc - 0.40, zc - 0.05)          # extract duct
    for x in (6.5, 9.5, 12.5):
        B.box("frame", x, x + 0.50, 21.18, 21.20, zc - 0.35, zc - 0.10)
    B.LEVEL[0] = LV_SS
    # bays: lines, numbers, wheel stops
    zl = zf + 0.001
    for i, (x0, y0, x1, y1, nose) in enumerate(BAYS):
        bay_lines(x0, y0, x1, y1, "N" if nose == "S" else "S", zl)
        cx = 0.5 * (x0 + x1)
        if nose == "S":
            B.box("yellow", cx - 0.80, cx - 0.20, y0 + 0.75, y0 + 0.90, zf, zf + 0.10)
            B.box("yellow", cx + 0.20, cx + 0.80, y0 + 0.75, y0 + 0.90, zf, zf + 0.10)
            digit(str(i + 1), cx + 0.22, y1 - 0.60, zl, 0.80, "line", ax="floor", flip=True)
        else:
            B.box("yellow", cx - 0.80, cx - 0.20, y1 - 0.90, y1 - 0.75, zf, zf + 0.10)
            B.box("yellow", cx + 0.20, cx + 0.80, y1 - 0.90, y1 - 0.75, zf, zf + 0.10)
            digit(str(i + 1), cx - 0.22, y0 + 0.60, zl, 0.80, "line", ax="floor")
    for j, (x0, y0, x1, y1) in enumerate(PARALLEL):
        bay_lines(x0, y0, x1, y1, "E", zl)
        B.box("line", x0, x0 + 0.10, y0, y1, zl, zl + 0.004)
        B.box("line", x1 - 0.10, x1, y0, y1, zl, zl + 0.004)
        digit(str(len(BAYS) + j + 1), 0.5 * (x0 + x1) - 0.20, y0 + 0.50, zl, 0.80, "line", ax="floor")
    # aisle arrows and the keep-clear hatch in front of the lobby door
    for (x, y, ang) in ((2.0, 19.0, 0.0), (8.0, 18.4, -math.pi / 2), (12.8, 14.6, math.pi), (11.0, 9.6, math.pi / 2)):
        c, s = math.cos(ang), math.sin(ang)
        shaft = [(-0.10, -0.90), (0.10, -0.90), (0.10, 0.20), (-0.10, 0.20)]
        head = [(-0.35, 0.20), (0.35, 0.20), (0.0, 0.80)]
        for pts in (shaft, head):
            B.poly("line", [(x + c * v - s * u, y + s * v + c * u, zl + 0.003) for u, v in pts],
                   [(0, 0)] * len(pts))
    for k in range(7):
        y = 9.40 + k * 0.22
        B.poly("yellow", [(7.00, y, zl + 0.002), (8.40, y + 0.70, zl + 0.002), (8.40, y + 0.80, zl + 0.002), (7.00, y + 0.10, zl + 0.002)],
               [(0, 0)] * 4)
    # motorcycles and bicycles at the front left; storage lockers along the front wall
    for k in range(3):
        x = 3.85 + k * 0.95
        bay_lines(x, 0.40, x + 0.90, 2.60, "N", zl)
    for k in range(6):
        x = 3.95 + k * 0.42
        B.box("steel", x, x + 0.04, 3.40, 3.44, zf, zf + 0.75)
        B.box("steel", x, x + 0.04, 3.90, 3.94, zf, zf + 0.75)
        B.box("steel", x, x + 0.04, 3.40, 3.94, zf + 0.73, zf + 0.77)
    for k in range(6):
        xa = 7.00 + k * 1.40
        xb = xa + 1.40 if k < 5 else 15.45
        B.box("steel", xa, xa + 0.05, 0.30, 1.75, zf, zc - 0.05)
        B.box("mesh", xa + 0.05, xb - 0.05, 1.70, 1.73, zf + 0.05, zc - 0.10)
        B.box("steel", xa + 0.05, xb - 0.05, 1.69, 1.75, zc - 0.10, zc - 0.05)
        B.box("steel", xa + 0.05, xb - 0.05, 1.69, 1.75, zf, zf + 0.05)
        B.box("black", xb - 0.25, xb - 0.20, 1.73, 1.76, zf + 0.95, zf + 1.10)
    B.box("steel", 15.40, 15.45, 0.30, 1.75, zf, zc - 0.05)
    # lighting, signs, extinguishers
    for x0, x1, y in ((1.5, 3.0, 19.5), (5.0, 6.5, 18.6), (8.0, 9.5, 18.6), (11.0, 12.5, 18.6), (13.5, 15.0, 19.5),
                      (8.2, 9.7, 9.6), (11.2, 12.7, 9.6), (13.6, 15.1, 9.6), (11.5, 13.0, 14.6), (7.8, 9.3, 4.3),
                      (11.2, 12.7, 4.3), (13.6, 15.1, 4.3), (4.4, 5.9, 4.0), (8.0, 9.5, 14.6)):
        B.LEVEL[0] = "Niveau_0_RDC"
        B.box("frame", x0, x1, y - 0.06, y + 0.06, zc - 0.07, zc)
        B.box("led", x0 + 0.02, x1 - 0.02, y - 0.04, y + 0.04, zc - 0.075, zc - 0.07)
        B.lamp("AREA", (0.5 * (x0 + x1), y, zc - 0.08), 70, (x1 - x0, 0.10), B.COOL)
        B.LEVEL[0] = LV_SS
    B.box("exit", 7.00, 7.02, 10.00, 10.50, zf + 2.02, zf + 2.17)
    B.box("exit", 1.60, 2.20, 16.92, 16.94, zc - 0.25, zc - 0.10)
    digit("-", 7.006, 10.90, zf + 0.60, 0.70, "teal", ax="wallX")
    digit("1", 7.006, 11.35, zf + 0.60, 0.70, "teal", ax="wallX")
    for x, y in ((10.80, 6.95), (7.15, 12.30)):
        cyl("red", x, y, 0.08, zf + 0.20, zf + 0.75, 14)
        cyl("black", x, y, 0.03, zf + 0.75, zf + 0.85, 8)
    B.LEVEL[0] = LV_SS
    ramp()
    B.LEVEL[0] = None


def entrance_portal():
    """The garage bay on the main street (X 0.37-3.38): teal portal, wood-lined reveal, open roller door,
    height bar, traffic light, parking sign and a contrasting driveway band on the sidewalk."""
    x0, x1, zt = 0.37, 3.38, 3.90
    B.box("teal", 0.08, x0, -0.40, 0.0, 0.0, 4.60)
    B.box("teal", x1, 3.67, -0.40, 0.0, 0.0, 4.60)
    B.box("teal", 0.08, 3.67, -0.40, 0.0, zt, 4.60)
    B.box("led", x0 + 0.03, x1 - 0.03, -0.36, -0.30, zt - 0.012, zt)
    B.box("wood", x0, x0 + 0.04, 0.0, 0.30, 0.0, zt)
    B.box("wood", x1 - 0.04, x1, 0.0, 0.30, 0.0, zt)
    B.box("wood", x0, x1, 0.0, 0.30, zt - 0.04, zt)
    B.box("frame", x0, x0 + 0.06, 0.30, 0.42, 0.0, zt)
    B.box("frame", x1 - 0.06, x1, 0.30, 0.42, 0.0, zt)
    B.box("frame", x0 - 0.02, x1 + 0.02, 0.30, 0.80, zt, zt + 0.50)
    # parking sign on the portal head: blue square, white P
    sx, sz = 1.875, 4.25
    B.box("signblue", sx - 0.28, sx + 0.28, -0.43, -0.40, sz - 0.28, sz + 0.28)
    B.box("sign", sx - 0.14, sx - 0.06, -0.44, -0.43, sz - 0.20, sz + 0.20)
    B.box("sign", sx - 0.06, sx + 0.08, -0.44, -0.43, sz + 0.12, sz + 0.20)
    B.box("sign", sx - 0.06, sx + 0.08, -0.44, -0.43, sz - 0.02, sz + 0.06)
    B.box("sign", sx + 0.08, sx + 0.15, -0.44, -0.43, sz - 0.02, sz + 0.20)
    digit("-", 2.35, -0.43, sz - 0.18, 0.36, "sign", ax="wallY")
    digit("1", 2.62, -0.43, sz - 0.18, 0.36, "sign", ax="wallY")
    # height bar 2.10 m inside the door, hung from the ceiling
    for k in range(10):
        xa = 0.45 + k * 0.285
        B.box("yellow" if k % 2 == 0 else "black", xa, xa + 0.285, 0.95, 1.05, 2.10, 2.22)
    for x in (0.70, 3.05):
        B.box("inox", x - 0.01, x + 0.01, 0.99, 1.01, 2.22, B.H_RDC - 0.20)
    # traffic light on the right jamb
    B.box("black", 3.43, 3.61, -0.50, -0.40, 2.05, 2.55)
    B.box("red", 3.47, 3.57, -0.505, -0.50, 2.36, 2.46)
    B.box("exit", 3.47, 3.57, -0.505, -0.50, 2.14, 2.24)
    # sidewalk: driveway band and bollards
    B.SITE[0] = True
    B.box("granite", x0, x1, -4.0, -0.40, -0.15, 0.003)
    for x in (0.12, 3.62):
        cyl("inox", x, -3.70, 0.07, 0.0, 0.90, 14)
    B.SITE[0] = False
    # linear lights over the ramp
    for y in (2.5, 6.0, 9.5, 13.0):
        B.box("frame", 1.70, 2.10, y - 1.2, y + 1.2, B.H_RDC - 0.30, B.H_RDC - 0.20)
        B.box("led", 1.72, 2.08, y - 1.18, y + 1.18, B.H_RDC - 0.305, B.H_RDC - 0.30)
        B.lamp("AREA", (1.90, y, B.H_RDC - 0.31), 180, (0.36, 2.36), B.COOL)
    B.LEVEL[0] = LV_SS
    for y in (15.0, 16.5):                       # the foot of the ramp, under the ground-floor slab
        B.lamp("AREA", (1.90, y, Z_RDC_SOFFIT - 0.05), 60, (2.0, 0.2), B.COOL)
    B.LEVEL[0] = None


def build_all():
    rdc_interior()
    basement()
    entrance_portal()
