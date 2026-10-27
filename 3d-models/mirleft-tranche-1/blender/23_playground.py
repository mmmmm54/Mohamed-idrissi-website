"""
23_playground — the children's playground on the tiled court between the pool court, the restaurant and the road
(client 27-10: "we want to add a park for kids like this or even something different, should be with colours";
the plan draws that ground as the playground, rev 4 paved it in beige tiles, 05 pave_restaurant_lawn).

A DESIGN PROPOSAL, colourful, on coloured rubber (EPDM) safety surfaces poured on the tiles, laid out in the court's
own frame (its long side along the road):
  the main play structure: two towers with their pyramid roofs (decks at 1.20 and 1.60 m), a rope bridge between
    them, a wavy open slide, a spiral tube slide, a climbing net, a climbing wall with its holds, a ladder and a
    fireman's pole;
  a swing frame with a nest swing and two flat seats; a roundabout; a seesaw;
  the toddlers' corner: a sandpit in its timber edge, three spring riders;
  benches and bins round it, three shade sails over the seats, olive trees at the corners (no fence along the
  road, 27-10).
Built by 05 after Tranche 1's planting (collection 08_PLAYGROUND); camera CAM_14_KIDS_PARK.
"""
import json
import math
import os

import bpy
import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLM = None                      # the plant library module (21_plants, set by 05): its tube helpers
COURT_DZ = 0.15                 # the court's tiles over the ground (05: court_tile)
EPDM = 0.03                     # the rubber over the tiles

COLOURS = {   # material key -> (name, colour, roughness)
    "kp_red": ("P01_Play_Red", "#D62C2C", 0.45), "kp_blue": ("P02_Play_Blue", "#1F64C8", 0.45),
    "kp_yellow": ("P03_Play_Yellow", "#F6C319", 0.45), "kp_green": ("P04_Play_Green", "#38A84A", 0.45),
    "kp_orange": ("P05_Play_Orange", "#F27F1B", 0.45), "kp_purple": ("P06_Play_Purple", "#7E4DB8", 0.45),
    "kp_steel": ("P07_Play_Steel_Blue_Grey", "#3C4A5C", 0.35), "kp_rope": ("P08_Play_Rope", "#C9B48A", 0.85),
    "kp_epdm_blue": ("P09_EPDM_Blue", "#3E86C9", 0.95), "kp_epdm_green": ("P10_EPDM_Green", "#6CB548", 0.95),
    "kp_epdm_terra": ("P11_EPDM_Terracotta", "#C8643C", 0.95), "kp_epdm_yellow": ("P12_EPDM_Yellow", "#E9C23A", 0.95),
    "kp_sail_orange": ("P13_Shade_Sail_Orange", "#F08A24", 0.8), "kp_sail_white": ("P14_Shade_Sail_White", "#F1EEE6", 0.8),
    "kp_sail_blue": ("P15_Shade_Sail_Blue", "#2A8FD0", 0.8), "kp_fence": ("P16_Fence_Green", "#2F7D46", 0.5),
}


def materials(M):
    mod = M["mod"]
    for k, (name, hexcol, rough) in COLOURS.items():
        if k not in M:
            M[k] = mod.simple(name, hexcol, rough, 0.0)
    return M


def court():
    """the tiled court (05 pave_restaurant_lawn moved the plan's lawn there)"""
    S = json.load(open(os.path.join(ROOT, "data", "site.json")))
    r = Point(S["restaurant"]["c"])
    gs = [Polygon(p["ext"], p["holes"]).buffer(0) for p in S["surfaces"]["lawn"]]
    return max((g for g in gs if g.area > 800 and g.distance(r) < 40), key=lambda g: g.area)


# the court's frame: its long side along the road
U = np.array([70.0, -9.6]); U /= np.linalg.norm(U)
V = np.array([-U[1], U[0]])
O = np.array([29.9, -36.4])


def W(u, v):
    return O + U * u + V * v


class F:
    """an item's frame: centre (u, v) in the court's frame, turned by yaw, standing on zb"""

    def __init__(self, mb, u, v, yaw, zb):
        self.mb, self.u, self.v, self.ca, self.sa, self.zb = mb, u, v, math.cos(yaw), math.sin(yaw), zb

    def P(self, a, b, z):
        u, v = self.u + a * self.ca - b * self.sa, self.v + a * self.sa + b * self.ca
        x, y = W(u, v)
        return np.array([x, y, self.zb + z])

    def poly(self, mat, pts):
        self.mb.poly(mat, [tuple(map(float, self.P(*p))) for p in pts])

    def box(self, mat, a0, a1, b0, b1, z0, z1):
        c = [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]
        for k in range(4):
            (pa, pb), (qa, qb) = c[k], c[(k + 1) % 4]
            self.poly(mat, [(pa, pb, z0), (qa, qb, z0), (qa, qb, z1), (pa, pb, z1)])
        self.poly(mat, [(a, b, z1) for a, b in c])
        self.poly(mat, [(a, b, z0) for a, b in c[::-1]])

    def tube(self, mat, pts, r, seg=8, cap=False):
        P = [self.P(*p) for p in pts]
        rr = r if isinstance(r, (list, tuple)) else [r] * len(P)
        PLM._tube(self.mb, mat, P, rr, seg=seg)
        if cap:
            d = P[-1] - P[-2]
            d, s, w = PLM._frame(d)
            ring = [P[-1] + (s * math.cos(2 * math.pi * k / seg) + w * math.sin(2 * math.pi * k / seg)) * rr[-1] for k in range(seg)]
            self.mb.poly(mat, [tuple(map(float, q)) for q in ring])

    def post(self, mat, a, b, z0, z1, r=0.05, seg=8):
        self.tube(mat, [(a, b, z0), (a, b, z1)], r, seg, cap=True)

    def sphere(self, mat, a, b, z, rx, ry=None, rz=None, nu=10, nv=6):
        ry, rz = ry or rx, rz or rx
        rows = []
        for j in range(nv + 1):
            ph = math.pi * j / nv - math.pi / 2
            rows.append([(a + rx * math.cos(ph) * math.cos(2 * math.pi * i / nu), b + ry * math.cos(ph) * math.sin(2 * math.pi * i / nu),
                          z + rz * math.sin(ph)) for i in range(nu)])
        for j in range(nv):
            for i in range(nu):
                i2 = (i + 1) % nu
                self.poly(mat, [rows[j][i], rows[j][i2], rows[j + 1][i2], rows[j + 1][i]])


# ---- the equipment -----------------------------------------------------------------------------------------------
def tower(f, deck, size, roof_mat, panel_mat, open_sides=("+a",)):
    h = size / 2
    for a in (-h, h):
        for b in (-h, h):
            f.box("kp_blue", a - 0.05, a + 0.05, b - 0.05, b + 0.05, 0.0, deck + 1.40)
    f.box("timber", -h, h, -h, h, deck - 0.06, deck)
    for side, (a0, a1, b0, b1) in {"+a": (h - 0.03, h, -h, h), "-a": (-h, -h + 0.03, -h, h),
                                   "+b": (-h, h, h - 0.03, h), "-b": (-h, h, -h, -h + 0.03)}.items():
        if side in open_sides:
            continue
        f.box(panel_mat, a0, a1, b0, b1, deck + 0.10, deck + 0.85)
        f.box("kp_yellow" if panel_mat != "kp_yellow" else "kp_red", a0 - 0.01, a1 + 0.01, b0 - 0.01, b1 + 0.01, deck + 0.85, deck + 0.92)
    z = deck + 1.40                                                  # the pyramid roof
    o = h + 0.18
    c = [(-o, -o), (o, -o), (o, o), (-o, o)]
    for k in range(4):
        f.poly(roof_mat, [(*c[k], z), (*c[(k + 1) % 4], z), (0.0, 0.0, z + 1.0)])
        f.poly(roof_mat, [(*c[(k + 1) % 4], z - 0.02), (*c[k], z - 0.02), (0.0, 0.0, z + 0.98)])
    f.sphere("kp_yellow", 0.0, 0.0, z + 1.05, 0.08)


def bridge(f, length, z0, z1, width=0.9):
    n = int(length / 0.22)
    for k in range(n):
        t0, t1 = k / n, (k + 0.8) / n
        a0, a1 = -length / 2 + length * t0, -length / 2 + length * t1
        zz = z0 + (z1 - z0) * (t0 + t1) / 2 - 0.12 * math.sin(math.pi * (t0 + t1) / 2)
        f.box("timber", a0, a1, -width / 2, width / 2, zz - 0.04, zz)
    for b in (-width / 2, width / 2):
        for hgt in (0.45, 0.85):
            f.tube("kp_rope", [(-length / 2 + length * t, b, z0 + (z1 - z0) * t - 0.12 * math.sin(math.pi * t) + hgt)
                               for t in np.linspace(0, 1, 9)], 0.018, 5)
        for t in np.linspace(0.1, 0.9, 7):
            zz = z0 + (z1 - z0) * t - 0.12 * math.sin(math.pi * t)
            f.tube("kp_rope", [(-length / 2 + length * t, b, zz), (-length / 2 + length * t, b, zz + 0.85)], 0.012, 4)


def wavy_slide(f, length, h, mat="kp_yellow", width=0.55):
    rows = []
    n = 20
    for k in range(n + 1):
        t = k / n
        z = h * (1 - t) ** 1.15 + 0.10 * math.sin(3 * math.pi * t) * 4 * t * (1 - t) + 0.25 * (t > 0.92)
        a = length * t
        w = width / 2
        rows.append([(a, -w - 0.04, z + 0.28), (a, -w, z + 0.02), (a, -w * 0.4, z - 0.04), (a, w * 0.4, z - 0.04), (a, w, z + 0.02), (a, w + 0.04, z + 0.28)])
    for j in range(n):
        for i in range(5):
            f.poly(mat, [rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]])
            f.poly(mat, [rows[j + 1][i], rows[j + 1][i + 1], rows[j][i + 1], rows[j][i]])
    f.box("kp_blue", length * 0.55 - 0.05, length * 0.55 + 0.05, -0.05, 0.05, 0.0, h * 0.42)
    f.box("kp_blue", length - 0.15, length - 0.05, -0.05, 0.05, 0.0, 0.25)


def spiral_slide(f, h, r=1.05, turns=0.95, mat="kp_orange", width=0.55):
    """an open spiral slide round its blue post: its U channel turning down from the deck, a run-out at its foot"""
    path = []
    n = 30
    for k in range(n + 1):
        t = k / n
        a = 2 * math.pi * turns * t
        path.append((r * math.cos(a), r * math.sin(a), h - (h - 0.40) * t ** 0.9))
    a_end = 2 * math.pi * turns
    tdir = np.array([-math.sin(a_end), math.cos(a_end)])
    for k in (1, 2):
        e = np.array(path[n][:2]) + tdir * 0.45 * k
        path.append((e[0], e[1], 0.40 - 0.08 * k))
    rows = []
    for k, (a, b, z) in enumerate(path):
        p0, p1 = np.array(path[max(k - 1, 0)][:2]), np.array(path[min(k + 1, len(path) - 1)][:2])
        d = (p1 - p0) / max(1e-9, np.linalg.norm(p1 - p0))
        s = np.array([-d[1], d[0]])
        w = width / 2
        prof = [(-w - 0.04, 0.28), (-w, 0.02), (-w * 0.4, -0.04), (w * 0.4, -0.04), (w, 0.02), (w + 0.04, 0.28)]
        rows.append([(a + s[0] * o, b + s[1] * o, z + dz) for o, dz in prof])
    for j in range(len(rows) - 1):
        for i in range(5):
            f.poly(mat, [rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]])
            f.poly(mat, [rows[j + 1][i], rows[j + 1][i + 1], rows[j][i + 1], rows[j][i]])
    f.post("kp_blue", 0.0, 0.0, 0.0, h + 0.4, 0.09)
    for k in range(0, n, 6):                                    # its brackets to the post
        a, b, z = path[k]
        f.tube("kp_steel", [(0.0, 0.0, z - 0.05), (a * 0.75, b * 0.75, z - 0.05)], 0.025, 5)


def net(f, w, h, depth):
    for k in range(8):
        b = -w / 2 + w * k / 7
        f.tube("kp_rope", [(0.0, b, h), (depth, b, 0.05)], 0.016, 4)
    for k in range(1, 7):
        t = k / 7
        f.tube("kp_rope", [(depth * t, -w / 2, h * (1 - t)), (depth * t, w / 2, h * (1 - t))], 0.016, 4)
    f.post("kp_steel", depth, -w / 2, 0.0, 0.25, 0.04)
    f.post("kp_steel", depth, w / 2, 0.0, 0.25, 0.04)


def climbing_wall(f, w, h, tilt=0.35, mat="kp_purple"):
    f.poly(mat, [(0, -w / 2, 0), (0, w / 2, 0), (-tilt, w / 2, h), (-tilt, -w / 2, h)])
    f.poly(mat, [(0, w / 2, 0), (0, -w / 2, 0), (-tilt, -w / 2, h), (-tilt, w / 2, h)])
    cols = ("kp_yellow", "kp_red", "kp_green", "kp_orange", "kp_blue")
    k = 0
    for i in range(4):
        for j in range(3):
            t = (i + 0.5 + 0.3 * (j % 2)) / 4.3
            b = -w / 2 + w * (j + 0.5) / 3 + 0.08 * ((i + j) % 2)
            f.sphere(cols[k % 5], -tilt * t + 0.04, b, h * t, 0.06, 0.06, 0.05, 6, 4)
            k += 1


def swings(f, length=5.6, h=2.45):
    for a in (-length / 2, length / 2):
        for b in (-0.85, 0.85):
            f.tube("kp_steel", [(a, b, 0.0), (a, 0.0, h)], 0.045, 8)
    f.tube("kp_steel", [(-length / 2 - 0.1, 0.0, h), (length / 2 + 0.1, 0.0, h)], 0.06, 10)
    # a nest swing in the middle, a flat seat each side
    for a, kind in ((-1.75, "seat"), (0.25, "nest"), (1.95, "seat")):
        if kind == "nest":
            for b in (-0.35, 0.35):
                for da in (-0.35, 0.35):
                    f.tube("kp_rope", [(a + da * 0.4, b * 0.4, h), (a + da, b, 0.55)], 0.012, 4)
            ring = [(a + 0.5 * math.cos(2 * math.pi * k / 16), 0.5 * math.sin(2 * math.pi * k / 16), 0.55) for k in range(17)]
            f.tube("kp_orange", ring, 0.05, 8)
            f.poly("kp_rope", [p for p in ring[:-1]])
            f.poly("kp_rope", [p for p in ring[:-1][::-1]])
        else:
            for b in (-0.22, 0.22):
                f.tube("kp_steel", [(a, b, h), (a, b, 0.48)], 0.008, 4)
            f.box("kp_red" if a < 0 else "kp_blue", a - 0.10, a + 0.10, -0.24, 0.24, 0.44, 0.48)


def spring_rider(f, mat, head_mat):
    f.box("kp_steel", -0.25, 0.25, -0.18, 0.18, 0.0, 0.03)
    coil = [(0.09 * math.cos(2 * math.pi * k / 10), 0.09 * math.sin(2 * math.pi * k / 10), 0.03 + 0.32 * k / 60) for k in range(61)]
    f.tube("kp_steel", coil, 0.012, 4)
    f.sphere(mat, 0.0, 0.0, 0.52, 0.32, 0.14, 0.17)
    f.sphere(head_mat, 0.30, 0.0, 0.72, 0.13, 0.11, 0.13)
    f.tube("kp_yellow", [(0.18, -0.16, 0.80), (0.18, 0.16, 0.80)], 0.018, 5)
    f.tube("kp_yellow", [(0.18, 0.0, 0.62), (0.18, 0.0, 0.80)], 0.016, 5)


def seesaw(f, length=3.2):
    f.box("kp_blue", -0.2, 0.2, -0.25, 0.25, 0.0, 0.45)
    t = math.radians(8)
    a = length / 2
    f.poly("kp_red", [(-a, -0.14, 0.45 - a * t), (a, -0.14, 0.45 + a * t), (a, 0.14, 0.45 + a * t), (-a, 0.14, 0.45 - a * t)])
    f.poly("kp_red", [(-a, 0.14, 0.40 - a * t), (a, 0.14, 0.40 + a * t), (a, -0.14, 0.40 + a * t), (-a, -0.14, 0.40 - a * t)])
    for s in (-1, 1):
        x = s * (a - 0.45)
        z = 0.45 + x * t
        f.tube("kp_yellow", [(x, -0.15, z), (x, -0.15, z + 0.35), (x, 0.15, z + 0.35), (x, 0.15, z)], 0.018, 5)
        f.box("kp_green", s * (a - 0.25) - 0.15, s * (a - 0.25) + 0.15, -0.15, 0.15, 0.45 + s * (a - 0.25) * t, 0.50 + s * (a - 0.25) * t)


def roundabout(f, r=1.0):
    f.post("kp_steel", 0.0, 0.0, 0.0, 0.32, 0.12)
    n = 12
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        mat = "kp_red" if k % 2 else "kp_yellow"
        f.poly(mat, [(0.0, 0.0, 0.32), (r * math.cos(a0), r * math.sin(a0), 0.32), (r * math.cos(a1), r * math.sin(a1), 0.32)])
        f.poly("kp_steel", [(r * math.cos(a0), r * math.sin(a0), 0.24), (r * math.cos(a1), r * math.sin(a1), 0.24),
                            (r * math.cos(a1), r * math.sin(a1), 0.32), (r * math.cos(a0), r * math.sin(a0), 0.32)])
    for k in range(4):
        a = math.pi * k / 2 + math.pi / 4
        f.tube("kp_blue", [(0.15 * math.cos(a), 0.15 * math.sin(a), 0.32), (0.75 * math.cos(a), 0.75 * math.sin(a), 0.85),
                           (0.82 * math.cos(a), 0.82 * math.sin(a), 0.32)], 0.025, 6)


def sandpit(f, w, d):
    g = box(-w / 2, -d / 2, w / 2, d / 2).buffer(0.4, join_style=1)
    ring = g.difference(g.buffer(-0.12))
    ex = list(g.exterior.coords)
    for k in range(len(ex) - 1):
        (pa, pb), (qa, qb) = ex[k], ex[k + 1]
        f.poly("timber", [(pa, pb, 0.0), (qa, qb, 0.0), (qa, qb, 0.30), (pa, pb, 0.30)])
    inner = list(g.buffer(-0.12).exterior.coords)
    for k in range(len(inner) - 1):
        (pa, pb), (qa, qb) = inner[k + 1], inner[k]
        f.poly("timber", [(pa, pb, 0.0), (qa, qb, 0.0), (qa, qb, 0.30), (pa, pb, 0.30)])
    for t in L.tri_poly(ring):
        f.poly("timber", [(a, b, 0.30) for a, b in t])
    for t in L.tri_poly(g.buffer(-0.12)):
        f.poly("sand", [(a, b, 0.18) for a, b in t])


def bench(f, length=1.8):
    for a in (-length / 2 + 0.15, length / 2 - 0.15):
        f.box("kp_steel", a - 0.03, a + 0.03, -0.22, 0.22, 0.0, 0.42)
        f.box("kp_steel", a - 0.03, a + 0.03, 0.17, 0.22, 0.42, 0.85)
    for k in range(4):
        f.box("timber", -length / 2, length / 2, -0.22 + 0.11 * k, -0.22 + 0.11 * k + 0.09, 0.42, 0.46)
    for k in range(3):
        f.box("timber", -length / 2, length / 2, 0.20, 0.23, 0.52 + 0.11 * k, 0.61 + 0.11 * k)


def bin_(f):
    f.tube("kp_fence", [(0, 0, 0.0), (0, 0, 0.85)], 0.22, 12, cap=True)


def sail(mb, f, corners, mat):
    """a shade sail between three posts (corners: (a, b, z) on f), its edges curving in"""
    P = [np.array(c, float) for c in corners]
    for p in P:
        f.post("kp_steel", p[0], p[1], 0.0, p[2] + 0.1, 0.06)
    cen = sum(P) / 3 - np.array([0, 0, 0.25])
    n = 6
    for k in range(3):
        A, Bq = P[k], P[(k + 1) % 3]
        pts = []
        for i in range(n + 1):
            t = i / n
            q = A + (Bq - A) * t
            q = q + (cen - q) * 0.18 * math.sin(math.pi * t)          # the edge curving in
            pts.append(q)
        for i in range(n):
            f.poly(mat, [tuple(pts[i]), tuple(pts[i + 1]), tuple(cen)])
            f.poly(mat, [tuple(cen), tuple(pts[i + 1]), tuple(pts[i])])


# ---- the playground ------------------------------------------------------------------------------------------------
def build(M, col, srcv, hz, plant):
    """M: materials, col: its collection, srcv: 05's plant sources, hz: the ground, plant(key, xy, s, z)"""
    materials(M)
    cz = lambda u, v: float(hz(*W(u, v))) + COURT_DZ
    mb = C.MeshBuilder()
    # the coloured rubber: the structure's island, the swings', the toddlers' corner, the paths of colour between
    pw = lambda pts: Polygon([tuple(W(u, v)) for u, v in pts])
    zones = {
        "kp_epdm_blue": pw([(-1.5 + 8.0 * math.cos(a), -1.5 + 5.2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]),
        "kp_epdm_green": pw([(16.8 + 4.6 * math.cos(a), -2.0 + 3.6 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]),
        "kp_epdm_terra": pw([(-9.4 + 3.6 * math.cos(a), -4.5 + 4.2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]),
    }
    zones["kp_epdm_yellow"] = unary_union([Point(*W(9.2, -6.8)).buffer(2.0, 32), pw([(5.5, -4.6), (12.5, -2.6), (12.5, -1.4), (5.5, -3.4)])])
    flat = lambda x, y: float(hz(x, y)) + COURT_DZ
    done = Polygon()
    for k, g in zones.items():
        g = g.difference(done)
        L.prism(mb, k, g, -0.02, EPDM, zf=flat)
        done = done.union(g)
    for c_, r_, k in (((-4.0, 2.0), 1.1, "kp_epdm_green"), ((3.0, -5.0), 0.9, "kp_epdm_terra"), ((19.0, 0.4), 0.8, "kp_epdm_blue"),
                      ((-8.2, -7.0), 0.7, "kp_epdm_yellow"), ((0.5, 2.6), 0.6, "kp_epdm_yellow")):   # spots of colour
        L.prism(mb, k, Point(*W(*c_)).buffer(r_, 24), EPDM, EPDM + 0.004, zf=flat, sides=False)
    zr = lambda u, v: cz(u, v) + EPDM
    # the main play structure
    t1, t2 = F(mb, -4.0, -1.0, 0.0, zr(-4.0, -1.0)), F(mb, 1.6, -1.0, 0.0, zr(1.6, -1.0))
    tower(t1, 1.20, 1.6, "kp_red", "kp_yellow", open_sides=("+a", "-b"))
    tower(t2, 1.60, 1.7, "kp_blue", "kp_green", open_sides=("-a", "+b", "-b"))
    bridge(F(mb, -1.2, -1.0, 0.0, zr(-1.2, -1.0)), 4.0, 1.20 + zr(-4.0, -1.0) - zr(-1.2, -1.0), 1.60 + zr(1.6, -1.0) - zr(-1.2, -1.0))
    wavy_slide(F(mb, -4.0, -1.8, -math.pi / 2, zr(-4.0, -1.8)), 3.6, 1.20)
    spiral_slide(F(mb, 1.6, -3.3, 0.0, zr(1.6, -3.3)), 1.60 + 0.05)
    net(F(mb, 2.45, -0.2, 0.0, zr(2.45, -0.2)), 1.5, 1.60, 1.9)
    climbing_wall(F(mb, -4.85, -1.0, math.pi, zr(-4.85, -1.0)), 1.4, 1.20)
    lad = F(mb, -4.0, -0.15, math.pi / 2, zr(-4.0, -0.15))
    for b in (-0.25, 0.25):
        lad.box("kp_blue", 0.0, 0.05, b - 0.025, b + 0.025, 0.0, 1.30)
    for k in range(5):
        lad.box("kp_yellow", 0.0, 0.05, -0.25, 0.25, 0.25 * (k + 1) - 0.02, 0.25 * (k + 1) + 0.02)
    F(mb, 2.7, -1.0, 0.0, zr(2.7, -1.0)).tube("kp_steel", [(0.0, 0.0, 0.0), (0.0, 0.0, 3.0), (-0.3, 0.0, 3.1)], 0.035, 6)  # fireman's pole
    # swings, roundabout, seesaw
    swings(F(mb, 16.8, -2.0, 0.0, zr(16.8, -2.0)))
    roundabout(F(mb, 9.2, -6.8, 0.0, zr(9.2, -6.8)))
    seesaw(F(mb, 9.5, 1.6, 0.0, zr(9.5, 1.6)))
    L.prism(mb, "kp_epdm_terra", Point(*W(9.5, 1.6)).buffer(0.01).union(pw([(7.4, 0.9), (11.6, 0.9), (11.6, 2.3), (7.4, 2.3)])), EPDM, EPDM + 0.004, zf=flat, sides=False)
    # the toddlers' corner: the sandpit, three spring riders
    sandpit(F(mb, -9.6, -2.6, 0.0, zr(-9.6, -2.6)), 2.4, 1.6)
    for (u, v), m, hm, yaw in (((-11.0, -6.6), "kp_orange", "kp_yellow", 0.4), ((-9.3, -7.4), "kp_green", "kp_red", -0.3),
                               ((-7.7, -6.3), "kp_purple", "kp_yellow", 0.9)):
        spring_rider(F(mb, u, v, yaw, zr(u, v)), m, hm)
    # benches facing the play, bins, shade sails over the seats
    for (u, v), yaw in (((-6.0, 4.6), math.pi), ((-2.0, 4.6), math.pi), ((5.0, 4.6), math.pi), ((13.5, 4.8), math.pi),
                        ((20.5, 4.8), math.pi), ((23.4, -1.5), math.pi / 2), ((-13.2, -2.0), -math.pi / 2)):
        bench(F(mb, u, v, yaw, cz(u, v)))
    for u, v in ((-4.0, 4.9), (17.0, 5.0), (-13.4, -5.5)):
        bin_(F(mb, u, v, 0.0, cz(u, v)))
    for corners, mat in (([(-7.5, 3.4, 3.0), (-0.5, 3.6, 3.4), (-4.0, 6.0, 2.8)], "kp_sail_orange"),
                         ([(11.0, 3.4, 3.2), (22.0, 3.6, 3.0), (16.5, 6.4, 3.5)], "kp_sail_white"),
                         ([(-13.0, -0.4, 3.0), (-6.8, -8.9, 2.9), (-12.6, -8.6, 3.4)], "kp_sail_blue")):
        f0 = F(mb, 0.0, 0.0, 0.0, cz(*corners[0][:2]))
        sail(mb, f0, corners, mat)
    # (client 27-10: no fence along the road, nor its planting: "remove those")
    mb.build("KIDS_PARK", col, M)
    for u, v in ((-12.5, 3.5), (25.0, 4.0), (25.0, -9.0), (-12.0, -10.0), (6.0, 5.5)):   # olive trees at the corners
        plant("olive", tuple(W(u, v)), 0.65, cz(u, v))
    return cameras(cz)


def cameras(cz):
    from mathutils import Vector
    colc = bpy.data.collections["07_CAMERAS"]
    shots = {"CAM_14_KIDS_PARK": ((10.0, -24.0), 10.0, (3.0, -1.0), 0.5, 26),
             "CAM_15_KIDS_PARK_AERIAL": ((-20.0, -30.0), 26.0, (4.0, -1.0), 0.0, 24)}
    out = {}
    for n, ((eu, ev), eh, (tu, tv), th, lens) in shots.items():
        cam = bpy.data.objects.new(n, bpy.data.cameras.new(n))
        colc.objects.link(cam)
        e, t = W(eu, ev), W(tu, tv)
        E, T = Vector((e[0], e[1], cz(eu, ev) + eh)), Vector((t[0], t[1], cz(tu, tv) + th))
        cam.location = E
        cam.rotation_euler = (T - E).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        cam.data.clip_end = 40000
        out[n] = cam
    return out
