"""
17_hotel — the hotel (client 23-10: "for hotel we dont have plan so i want you to be creative and give me
proposition ... perfect and the same style we have on our residence ... not the same design ... the perfect one").

A DESIGN PROPOSAL, not a drawing. It keeps the plan de masse's zoning of the hotel's plot (between street 7
and the parking, 31 x 117 m): the two buildings on their cells along the parking, the crossing between them,
the long basin with its arm on the crossing's axis, the promenade along the basin with its gate on street 7 on
the same axis, the garden. The residence's materials (the sand render, the taupe stone surrounds, the grey
ledge / ochre band cornice, the rounded coping, the horns, quartz aluminium, cedar, mashrabiya, green zellige)
in forms of its own, a kasbah of three storeys on a water garden:
  the main building (north cell, 14.1 x 45.5 m, three storeys, +12.00): on the Voie Publique its gate block
    standing 1.30 proud and rising to +14.20 with its horns, a giant pointed horseshoe arch in a taupe alfiz
    framed in green zellige, studded doors under a mashrabiya tympanum, two steps down inside; on the garden
    an arcade of pointed horseshoe arches (lobby, restaurant) on a stone terrace with its balustrade and its
    flights of steps, cedar mashrabiya oriels on the first floor, stone balconies with cedar railings on the
    second; windows in taupe surrounds on the parking side; towers at the southern corners rising a half
    storey with their horns; a cedar pergola on the roof terrace. It steps down 0.9 m at mid-length with the
    ground (4 % along the plot);
  the gate pavilion on the crossing: a domed qubba, pointed horseshoe arches east (from the parking) and west
    (onto the arm's head) in taupe alfiz framed in zellige, blind zellige arches north and south, a fountain
    inside, the horns at its corners, the dome on its drum with a bronze finial;
  the suites (south cell, 13.3 x 56.4 m, two storeys): fourteen, stepping down the slope in pairs of
    heights, each with its terrace on the garden behind low walls under a cedar pergola, a balcony upstairs;
  the water garden: the long basin (7.1 x 53.7 m) in three basins stepping down the slope (the water running
    over two weirs) and its arm (5.0 x 15 m), green zellige, travertine decks with loungers, parasols and date
    palms; the arm's head under the crossing: a zellige wall with three bronze spouts; a promenade of palms
    along the basin from the garden gate on street 7; olive trees in the lawns; walls on the streets.

Frame: the hotel's own (u across, towards the parking; v along, towards the Voie Publique), origin at the
south-west corner of the north building's cell (plan de masse), absolute heights. build() places its objects
(location, turn) and returns the plants in its frame with the frame itself.
"""
import importlib.util
import math
import os

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t3_vc_h", os.path.join(HERE, "14_villa_c.py"))
VC = importlib.util.module_from_spec(_spec)
VC.__dict__["L"] = L
_spec.loader.exec_module(VC)
D = VC.D

A_S = (0.0, 0.5, 14.1, 23.25)            # the main building's two halves (u0 v0 u1 v1)
A_N = (0.0, 23.25, 14.1, 46.0)
PORCH = (3.25, 42.0, 10.85, 47.3)        # the gate block, proud of the north front
TOWERS = ((0.0, 0.5, 5.0, 5.5), (9.1, 0.5, 14.1, 5.5))
FL_A = (0.20, 4.40, 7.80)                # floors over each half's reference ground (the lobby storey 4.20)
ZR_A, PAR = 11.20, 0.80                  # roof terrace, parapet
NB = 7                                   # bays per half (3.25 m)
POD = 3.0                                # the garden terrace along the arcade
B = (0.4, -64.8, 13.7, -8.4)             # the suites
N_SU, FLB = 14, 3.40
PAV = (3.6, -7.5, 10.6, -0.5)            # the gate pavilion on the crossing
DECK = 2.6                               # pool decks
W2 = 0.15                                # half the weirs' thickness


def frame(H, F):
    """(origin, u, v) of the hotel's frame in model coordinates: v along the north building's west side,
    northwards, origin at its southern end."""
    UN, UE = np.array(F["un"]), np.array(F["ue"])
    en = lambda p: np.array([np.dot(p, UE), np.dot(p, UN)])
    A = [en(p) for p in H["bld_a"]["ext"]]
    ed = [(A[i], A[(i + 1) % len(A)]) for i in range(len(A))]
    longs = sorted(ed, key=lambda e: -np.linalg.norm(e[1] - e[0]))[:2]
    p0, p1 = sorted(min(longs, key=lambda e: e[0][0] + e[1][0]), key=lambda p: p[1])
    v = (p1 - p0) / np.linalg.norm(p1 - p0)
    u = np.array([v[1], -v[0]])
    m = lambda q: q[0] * UE + q[1] * UN
    return m(p0), m(u), m(v)


def build(M, col, H, F, zf, name="T3_HOTEL", lawn="lawn"):
    """H: t3_site.json's 'hotel', F its 'frame'; zf(x, y): the ground (model coordinates).
    Returns (objects, plants [(kind, u, v, z, scale)], (origin, u, v))."""
    o, U, V = frame(H, F)
    to_l = lambda p: (float(np.dot(np.array(p) - o, U)), float(np.dot(np.array(p) - o, V)))
    PL = lambda d: Polygon([to_l(p) for p in d["ext"]]).buffer(0)
    zl = lambda u, v: float(zf(*(o + U * u + V * v)))
    plot, garden, pool = PL(H["plot"]), PL(H["garden"]), PL(H["pool"])
    rill = max([PL(r) for r in H["rill"]], key=lambda g: g.area)          # the promenade and its gate path
    cross = unary_union([PL(H["cross"])] + [PL(r) for r in H["rill"] if PL(r).bounds[0] > -1.0]).buffer(0)
    plants = []
    mb = C.MeshBuilder()

    # ---- helpers -------------------------------------------------------------------------------------------
    def rect(P3, mat, a0, a1, b0, b1, d):
        mb.poly(mat, [P3(a0, b0, d), P3(a1, b0, d), P3(a1, b1, d), P3(a0, b1, d)], [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])

    def arch(sc, w, zs, z0):
        """pointed horseshoe arch (the villas' profile) over jambs down to z0"""
        return Polygon([(x, z0 if abs(z + 0.5) < 1e-9 else z) for x, z in VC.arch_poly(sc, w, zs).exterior.coords[:-1]])

    def soffit(h, z0, P):
        """the reveal round an arch through a slab: P(s, z, k) with k 0 / 1 the slab's two faces"""
        ring = list(h.exterior.coords)
        cx, cz = h.centroid.x, h.centroid.y
        for (sa, za), (sb, zb) in zip(ring, ring[1:]):
            if za <= z0 + 1e-6 and zb <= z0 + 1e-6:
                continue
            pa0, pa1, pb0, pb1 = P(sa, za, 0), P(sa, za, 1), P(sb, zb, 0), P(sb, zb, 1)
            m0, m1 = P((sa + sb) / 2, (za + zb) / 2, 0), P(cx, cz, 0)
            VC.tri_out(mb, "surround", [pa0, pa1, pb1, pb0], tuple(m1[i] - m0[i] for i in range(3)))

    def wall(a, b, out, z0, z1, ops=(), mat="villa"):
        """A plumb face a -> b facing out; ops: (centre (u, v), width, z0, z1, kind, depth[, springing]) with
        rectangular holes, or arched ones when a springing is given."""
        if (b[1] - a[1]) * out[0] - (b[0] - a[0]) * out[1] < 0:
            a, b = b, a
        Lw, P3, *_ = VC.frame_of(a, b, False)
        ux, uy = (b[0] - a[0]) / Lw, (b[1] - a[1]) / Lw
        s_of = lambda p: (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
        holes = []
        for op in ops:
            (c, w, h0, h1, kind, dep), zs = op[:6], (op[6] if len(op) > 6 else None)
            s = s_of(c)
            holes.append((arch(s, w, zs, h0) if zs is not None else box(s - w / 2, h0, s + w / 2, h1), kind, dep))
        face = box(0.0, z0, Lw, z1)
        for h, _, _ in holes:
            face = face.difference(h)
        for g in L.as_polys(face):
            for t in L.tri_poly(g):
                mb.poly(mat, [P3(s, z) for s, z in t], [(s, z) for s, z in t])
        for h, kind, dep in holes:
            if kind == "open":
                continue
            ring = list(h.exterior.coords)
            if not h.exterior.is_ccw:
                ring = ring[::-1]
            rm = "villa" if kind == "niche" else "surround"
            for (sa, za), (sb, zb) in zip(ring, ring[1:]):
                if za <= z0 + 1e-6 and zb <= z0 + 1e-6:
                    continue
                mb.poly(rm, [P3(sa, za), P3(sb, zb), P3(sb, zb, dep), P3(sa, za, dep)])
            FILL[kind](P3, h, dep)
        return P3, s_of

    def f_niche(P3, h, dep):
        s0, z0, s1, z1 = h.bounds
        rect(P3, "villa", s0, s1, z0, z1, dep)

    def f_blind(P3, h, dep):
        """a blind arch: green zellige in it, the taupe frame round it"""
        for t in L.tri_poly(h):
            mb.poly("tile_jade", [P3(s, z, dep) for s, z in t], [(s, z) for s, z in t])
        s0, z0, s1, z1 = h.bounds
        D.ext(mb, "surround", h.buffer(0.16, join_style=2).difference(h).intersection(box(s0 - 1, z0, s1 + 1, z1 + 1)),
              lambda a, b, w: P3(a, b, w), -0.04, 0.01)

    def f_win(P3, h, dep):
        s0, z0, s1, z1 = h.bounds
        d = 0.12
        rect(P3, "interior", s0 - 0.3, s1 + 0.3, z0 - 0.3, z1 + 0.3, 0.80)
        rect(P3, "glass", s0, s1, z0, z1, d)
        for a0, a1, b0, b1 in ((s0, s1, z0, z0 + 0.06), (s0, s1, z1 - 0.06, z1), (s0, s0 + 0.06, z0, z1), (s1 - 0.06, s1, z0, z1),
                               ((s0 + s1) / 2 - 0.03, (s0 + s1) / 2 + 0.03, z0, z1)):
            D.pbox(mb, P3, a0, a1, b0, b1, d - 0.03, d + 0.03, "frame")
        rect(P3, "curtain", s0 + 0.06, s0 + 0.06 + (s1 - s0) * 0.22, z0 + 0.05, z1 - 0.05, 0.30)
        rect(P3, "curtain", s1 - 0.06 - (s1 - s0) * 0.22, s1 - 0.06, z0 + 0.05, z1 - 0.05, 0.30)
        for a0, a1, b0, b1 in ((s0 - 0.18, s0, z0 - 0.18, z1 + 0.20), (s1, s1 + 0.18, z0 - 0.18, z1 + 0.20),
                               (s0, s1, z1, z1 + 0.20), (s0, s1, z0 - 0.18, z0)):
            D.pbox(mb, P3, a0, a1, b0, b1, -0.04, 0.02, "surround")

    def f_fr(P3, h, dep):
        """a french window, two leaves and a transom, its surround without the sill"""
        s0, z0, s1, z1 = h.bounds
        d = 0.14
        rect(P3, "interior", s0 - 0.3, s1 + 0.3, z0, z1 + 0.3, 0.90)
        rect(P3, "glass", s0, s1, z0, z1, d)
        for a0, a1, b0, b1 in ((s0, s1, z0, z0 + 0.06), (s0, s1, z1 - 0.06, z1), (s0, s0 + 0.06, z0, z1), (s1 - 0.06, s1, z0, z1),
                               ((s0 + s1) / 2 - 0.03, (s0 + s1) / 2 + 0.03, z0, z1), (s0, s1, z0 + 2.05, z0 + 2.11)):
            D.pbox(mb, P3, a0, a1, b0, b1, d - 0.03, d + 0.03, "frame")
        rect(P3, "curtain", s0 + 0.06, s0 + 0.30, z0 + 0.05, z1 - 0.05, 0.32)
        rect(P3, "curtain", s1 - 0.30, s1 - 0.06, z0 + 0.05, z1 - 0.05, 0.32)
        for a0, a1, b0, b1 in ((s0 - 0.18, s0, z0, z1 + 0.20), (s1, s1 + 0.18, z0, z1 + 0.20), (s0, s1, z1, z1 + 0.20)):
            D.pbox(mb, P3, a0, a1, b0, b1, -0.04, 0.02, "surround")

    def f_door(P3, h, dep):
        """a suite's door: cedar, a few studs, the taupe surround"""
        s0, z0, s1, z1 = h.bounds
        d = 0.16
        rect(P3, "door_wood", s0, s1, z0, z1, d)
        for i in range(3):
            for j in range(6):
                a = s0 + 0.15 + (s1 - s0 - 0.30) * i / 2
                b = z0 + 0.25 + (z1 - z0 - 0.50) * j / 5
                D.pbox(mb, P3, a - 0.014, a + 0.014, b - 0.014, b + 0.014, d - 0.02, d, "metal_dark")
        for a0, a1, b0, b1 in ((s0 - 0.22, s0, z0, z1 + 0.25), (s1, s1 + 0.22, z0, z1 + 0.25), (s0, s1, z1, z1 + 0.25)):
            D.pbox(mb, P3, a0, a1, b0, b1, -0.05, 0.02, "surround")

    def f_arch(P3, h, dep):
        """an arch of the arcade: glazing set back in it, the lit room behind, the taupe frame round it"""
        s0, z0, s1, z1 = h.bounds
        for t in L.tri_poly(h):
            mb.poly("glass", [P3(s, z, dep - 0.10) for s, z in t], [(s, z) for s, z in t])
        rect(P3, "interior", s0 - 0.4, s1 + 0.4, z0, z1 + 0.3, dep + 1.20)
        sm = (s0 + s1) / 2
        D.pbox(mb, P3, sm - 0.03, sm + 0.03, z0, z1 - 0.10, dep - 0.13, dep - 0.07, "frame")
        D.pbox(mb, P3, s0, s1, z0 + 2.40, z0 + 2.46, dep - 0.13, dep - 0.07, "frame")
        D.pbox(mb, P3, s0, s1, z0, z0 + 0.06, dep - 0.13, dep - 0.07, "frame")
        D.ext(mb, "surround", h.buffer(0.15, join_style=2).difference(h).intersection(box(s0 - 1, z0, s1 + 1, z1 + 1)),
              lambda a, b, w: P3(a, b, w), -0.04, 0.01)

    def gate(P3, h, dep, dw, dh, alfiz=True):
        """studded doors under a mashrabiya tympanum, set back in the arch; the alfiz and its zellige frame"""
        s0, z0, s1, z1 = h.bounds
        sm = (s0 + s1) / 2
        d = dep - 0.10
        for a0, a1 in ((sm - dw / 2, sm - 0.01), (sm + 0.01, sm + dw / 2)):
            rect(P3, "door_wood", a0, a1, z0, z0 + dh, d)
            ni, nj = max(3, int((a1 - a0) / 0.24)), max(5, int(dh / 0.30))
            for i in range(ni):
                for j in range(nj):
                    a = a0 + 0.12 + (a1 - a0 - 0.24) * i / (ni - 1)
                    b = z0 + 0.15 + (dh - 0.30) * j / (nj - 1)
                    D.pbox(mb, P3, a - 0.016, a + 0.016, b - 0.016, b + 0.016, d - 0.025, d, "metal_dark")
        rest = h.difference(box(sm - dw / 2, z0 - 1, sm + dw / 2, z0 + dh))
        for g in L.as_polys(rest):
            mat = "mashrabiya" if g.bounds[1] >= z0 + dh - 0.01 else "villa"
            for t in L.tri_poly(g):
                mb.poly(mat, [P3(s, z, d) for s, z in t], [(s, z) for s, z in t])
        D.pbox(mb, P3, sm - dw / 2 - 0.12, sm + dw / 2 + 0.12, z0 + dh, z0 + dh + 0.14, d - 0.06, d, "door_wood")
        for k in (-1, 1):
            D.pbox(mb, P3, sm + k * 0.25 - 0.08, sm + k * 0.25 + 0.08, z0 + 1.15, z0 + 1.25, d - 0.08, d, "metal_dark")
        if alfiz:
            w = s1 - s0
            a_ = box(s0 - 0.18 * w, z0, s1 + 0.18 * w, z1 + 0.20 * w).difference(h)
            D.ext(mb, "surround", a_, lambda a, b, w_: P3(a, b, w_), -0.06, 0.0)
            z_ = box(s0 - 0.25 * w, z0, s1 + 0.25 * w, z1 + 0.27 * w).difference(box(s0 - 0.18 * w, z0, s1 + 0.18 * w, z1 + 0.20 * w))
            D.ext(mb, "tile_jade", z_, lambda a, b, w_: P3(a, b, w_), -0.08, 0.0)

    FILL = {"niche": f_niche, "blind": f_blind, "win": f_win, "fr": f_fr, "door": f_door, "arch": f_arch,
            "gate": lambda P3, h, dep: gate(P3, h, dep, 3.0, 4.6),
            "gdoor": lambda P3, h, dep: gate(P3, h, dep, 2.0, 2.10, alfiz=False)}

    def box_walls(g, z0, z1, ops={}, skip=()):
        """the four faces of a box, ops per side 'W' 'E' 'S' 'N'"""
        x0, y0, x1, y1 = g.bounds
        for k, (a, b, out) in {"S": ((x0, y0), (x1, y0), (0, -1)), "E": ((x1, y0), (x1, y1), (1, 0)),
                               "N": ((x1, y1), (x0, y1), (0, 1)), "W": ((x0, y1), (x0, y0), (-1, 0))}.items():
            if k not in skip:
                wall(a, b, out, z0, z1, ops.get(k, ()))

    def cornice(g, z, cut=Polygon()):
        for z0, z1, pd, mat in ((z, z + 0.08, 0.10, "ledge"), (z + 0.08, z + 0.22, 0.06, "band"), (z + 0.22, z + 0.30, 0.14, "ledge")):
            L.prism(mb, mat, g.buffer(pd, join_style=2).difference(g).difference(cut), z0, z1, bottom=True)

    def roof(g, zr, zt, cut=Polygon(), horns=True):
        """parapet with the rounded coping (none where cut), the terrace, the horns"""
        ring = g.difference(g.buffer(-0.30, join_style=2)).difference(cut)
        L.prism(mb, "villa", ring, zr - 0.02, zt - 0.06, bottom=False)
        D.coping(mb, "villa", ring, zt, 0.06)
        L.prism(mb, "terrace", g.buffer(-0.005, join_style=2).difference(ring), zr - 0.02, zr, sides=False)
        if horns:
            VC.horns(mb, g.buffer(0.012, join_style=2), zt)

    def steps(edge, sgn, z_top, z_low, mat="deck_stone", tread=0.30, rise=0.16):
        """a flight from z_top down to z_low, leaving the edge (u, v0, v1) towards sgn along u"""
        n = int(math.ceil((z_top - z_low) / rise - 0.05))
        u, v0, v1 = edge
        out = []
        for k in range(n - 1):
            a, b = u + sgn * k * tread, u + sgn * (k + 1) * tread
            q = box(min(a, b), v0, max(a, b), v1)
            L.prism(mb, mat, q, z_low - 0.6, z_top - (k + 1) * (z_top - z_low) / n)
            out.append(q)
        return unary_union(out) if out else Polygon()

    def lounger(x, y, ang, z):
        ca, sa = math.cos(ang), math.sin(ang)
        Q = lambda a, b: (x + a * ca - b * sa, y + a * sa + b * ca)
        g = Polygon([Q(-0.35, -0.95), Q(0.35, -0.95), Q(0.35, 0.95), Q(-0.35, 0.95)])
        L.prism(mb, "lounger_white", g, z + 0.06, z + 0.30)
        L.prism(mb, "cushion", g.buffer(-0.04), z + 0.30, z + 0.36)
        L.prism(mb, "cushion", Polygon([Q(-0.33, 0.55), Q(0.33, 0.55), Q(0.33, 0.93), Q(-0.33, 0.93)]), z + 0.36, z + 0.66)

    def parasol(x, y, z):
        L.prism(mb, "metal_dark", Point(x, y).buffer(0.035, 6), z, z + 2.55)
        rim = [(x + 1.35 * math.cos(2 * math.pi * k / 8), y + 1.35 * math.sin(2 * math.pi * k / 8), z + 2.30) for k in range(8)]
        for k in range(8):
            mb.poly("canvas", [rim[k], rim[(k + 1) % 8], (x, y, z + 2.80)])
            mb.poly("canvas", [rim[(k + 1) % 8], rim[k], (x, y, z + 2.78)])

    def dome(c, r, z0, h, n=40, nr=10):
        for k in range(nr):
            a0, a1 = (math.pi / 2) * k / nr, (math.pi / 2) * (k + 1) / nr
            r0, r1 = r * math.cos(a0), r * math.cos(a1)
            z0_, z1_ = z0 + h * math.sin(a0), z0 + h * math.sin(a1)
            for j in range(n):
                t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                q = [(c[0] + r0 * math.cos(t0), c[1] + r0 * math.sin(t0), z0_), (c[0] + r0 * math.cos(t1), c[1] + r0 * math.sin(t1), z0_),
                     (c[0] + r1 * math.cos(t1), c[1] + r1 * math.sin(t1), z1_), (c[0] + r1 * math.cos(t0), c[1] + r1 * math.sin(t0), z1_)]
                mb.poly("villa", q if k < nr - 1 else q[:3])
        zt = z0 + h
        L.prism(mb, "bronze", Point(*c).buffer(0.10, 10), zt - 0.05, zt + 0.15)
        L.prism(mb, "bronze", Point(*c).buffer(0.03, 6), zt, zt + 1.0)
        for r_, zz in ((0.17, 0.45), (0.12, 0.78)):
            L.prism(mb, "bronze", Point(*c).buffer(r_, 12), zt + zz - r_ * 0.8, zt + zz + r_ * 0.8)

    hard = []                                                 # everything that is not lawn

    # =========================================================================================================
    # the main building: two halves stepping with the ground
    halves = []
    for g_, vref in ((A_S, 11.9), (A_N, 34.6)):
        z0 = zl(7.05, vref)
        halves.append((box(*g_), [z0 + f for f in FL_A], z0 + ZR_A))
    (gS, fS, zrS), (gN, fN, zrN) = halves
    porch = box(*PORCH)
    towers = [box(*t) for t in TOWERS]
    zbotA = min(zl(x, y) for x in (-POD - 2.5, 14.1) for y in (0.5, 47.3)) - 1.8          # below the arm's deck and the crossing too
    bay = (A_N[3] - A_S[1]) / (2 * NB)
    for k, (g, fl, zr) in enumerate(halves):
        x0, y0, x1, y1 = g.bounds
        zw = zr - 0.02
        cs = [y0 + (i + 0.5) * bay for i in range(NB)]
        west = [((x0, v), 2.60, fl[0], 0, "arch", 0.45, fl[0] + 2.15) for v in cs]
        west += [((x0, v), 1.40, fl[f], fl[f] + 2.50, "fr", 0.30) for v in cs for f in (1, 2)]
        east = [((x1, v), 1.20, fl[f] + 0.90, fl[f] + 2.50, "win", 0.30) for v in cs for f in range(3)]
        east += [((x1, v), 0.20, zr - 0.75, zr - 0.55, "niche", 0.10) for v in cs]
        P3w, sw = wall((x0, y1), (x0, y0), (-1, 0), zbotA, zw, west)
        wall((x1, y0), (x1, y1), (1, 0), zbotA, zw, east)
        if k == 0:
            wall((x0, y0), (x1, y0), (0, -1), zbotA, zw,
                 [((u, y0), 1.20, fl[f] + 0.90, fl[f] + 2.50, "win", 0.30) for u in (2.5, 7.05, 11.6) for f in range(3)])
        else:
            wall((x0, y0), (x1, y0), (0, -1), zrS - 0.02, zrN - 0.02)             # the step, above the southern roof
            for a_, b_, u in (((x1, y1), (PORCH[2], y1), 12.5), ((PORCH[0], y1), (x0, y1), 1.6)):      # either side of the gate
                wall(a_, b_, (0, 1), zbotA, zw, [((u, y1), 1.10, fl[f] + 0.90, fl[f] + 2.50, "win", 0.30) for f in range(3)])
        # oriels (first floor) and balconies (second floor) along the garden front
        for v in cs:
            s = sw((x0, v))
            a0, a1, b0, b1 = s - 1.0, s + 1.0, fl[1] - 0.15, fl[1] + 2.75
            rect(P3w, "mashrabiya", a0, a1, b0 + 0.12, b1 - 0.12, -0.70)
            for sa in (a0, a1):
                q = [P3w(sa, b0 + 0.12, 0.0), P3w(sa, b0 + 0.12, -0.70), P3w(sa, b1 - 0.12, -0.70), P3w(sa, b1 - 0.12, 0.0)]
                mb.poly("mashrabiya", q)
                mb.poly("mashrabiya", q[::-1])
            D.pbox(mb, P3w, a0 - 0.06, a1 + 0.06, b0, b0 + 0.12, -0.78, 0.0, "timber")
            D.pbox(mb, P3w, a0 - 0.10, a1 + 0.10, b1 - 0.14, b1, -0.84, 0.0, "timber")
            for sa in (a0, a1):
                D.pbox(mb, P3w, sa - 0.04, sa + 0.04, b0, b1, -0.74, -0.66, "timber")
            for kk in range(4):
                sb = a0 + 0.15 + (a1 - a0 - 0.30) * kk / 3
                D.pbox(mb, P3w, sb - 0.05, sb + 0.05, b0 - 0.22, b0, -0.55, 0.0, "timber")
            c0, c1, zb = s - 1.05, s + 1.05, fl[2]
            D.pbox(mb, P3w, c0, c1, zb - 0.14, zb, -0.80, 0.0, "surround")
            for kk in range(3):
                sb = c0 + 0.25 + (c1 - c0 - 0.50) * kk / 2
                D.pbox(mb, P3w, sb - 0.07, sb + 0.07, zb - 0.42, zb - 0.14, -0.60, 0.0, "surround")
            D.pbox(mb, P3w, c0, c1, zb + 0.95, zb + 1.02, -0.80, -0.72, "timber")
            for kk in range(13):
                sb = c0 + 0.05 + (c1 - c0 - 0.10) * kk / 12
                D.pbox(mb, P3w, sb - 0.02, sb + 0.02, zb, zb + 0.95, -0.78, -0.74, "timber")
            for sa in (c0, c1):
                D.pbox(mb, P3w, sa - 0.03, sa + 0.03, zb, zb + 1.02, -0.80, 0.0, "timber")
        L.prism(mb, "interior_floor", g.buffer(-0.05, join_style=2), zbotA + 0.4, fl[0])
    # roofs: the southern one runs to the step; towers on the southern corners, the gate block on the north
    tw = unary_union(towers)
    cornice(gS, zrS, box(-1.0, A_S[3], 15.1, A_S[3] + 1.0).union(tw.buffer(0.02)))
    roof(gS, zrS, zrS + PAR, box(0.30, A_S[3] - 0.31, 14.1 - 0.30, A_S[3] + 0.01).union(tw.buffer(0.01)), horns=False)
    cornice(gN, zrN, porch.buffer(0.02))
    roof(gN, zrN, zrN + PAR, porch.buffer(0.01))
    zc = zrS + 1.30
    for t in towers:
        box_walls(t, zrS - 0.02, zc - 0.02)
        cornice(t, zc)
        roof(t, zc, zc + PAR)
    # the rooftop pergola on the northern half
    for vv in np.arange(26.5, 39.01, 0.60):
        mb.box("timber", 1.8, 12.3, vv - 0.05, vv + 0.05, zrN + 2.70, zrN + 2.86)
    for uu in (2.2, 11.9):
        mb.box("timber", uu - 0.10, uu + 0.10, 26.3, 39.2, zrN + 2.50, zrN + 2.70)
        for vv in (26.5, 30.7, 34.9, 39.0):
            mb.box("timber", uu - 0.09, uu + 0.09, vv - 0.09, vv + 0.09, zrN, zrN + 2.50)
    # the gate block: proud of the north front, rising to +14.20, the giant arch, six niches over it
    px0, py0, px1, py1 = PORCH
    zpk = fN[0] - FL_A[0] + 13.40
    pc = (px0 + px1) / 2
    ops = [((pc, py1), 4.40, fN[0], 0, "gate", 1.60, fN[0] + 5.20)]
    ops += [((u, py1), 0.22, zpk - 1.20, zpk - 0.98, "niche", 0.10) for u in np.linspace(px0 + 1.2, px1 - 1.2, 6)]
    wall((px1, py1), (px0, py1), (0, 1), zbotA, zpk - 0.02, ops)
    for xs, out in ((px0, (-1, 0)), (px1, (1, 0))):
        wall((xs, A_N[3]), (xs, py1), out, zbotA, zrN - 0.02)
        wall((xs, py0), (xs, py1), out, zrN - 0.02, zpk - 0.02)
    wall((px0, py0), (px1, py0), (0, -1), zrN - 0.02, zpk - 0.02)
    cornice(porch, zpk)
    roof(porch, zpk, zpk + PAR)
    L.prism(mb, "deck_stone", porch, zbotA + 0.4, fN[0])
    zst = zl(pc, py1)                                          # the street at the gate: steps down inside
    for k in range(max(0, int(round((zst + 0.02 - fN[0]) / 0.15)))):
        L.prism(mb, "deck_stone", box(pc - 2.2, py1 - 0.45 - 0.30 * k, pc + 2.2, py1 - (0.45 + 0.30 * (k - 1) if k else 0.0)),
                fN[0], zst + 0.02 - 0.15 * k)
    # the garden terrace along the arcade, its balustrade and flights of steps
    for k, (g, fl, zr) in enumerate(halves):
        x0, y0, x1, y1 = g.bounds
        pod = box(x0 - POD, y0, x0, y1)
        L.prism(mb, "villa", pod, zbotA + 0.4, fl[0] - 0.03)
        L.prism(mb, "deck_stone", pod, fl[0] - 0.03, fl[0])
        hard.append(pod)
        cs = [y0 + (i + 0.5) * bay for i in range(NB)]
        gaps = []
        for vf in (cs[1], cs[5]):
            zg = zl(x0 - POD - 1.0, vf)
            if fl[0] - zg > 0.20:
                hard.append(steps((x0 - POD, vf - 1.4, vf + 1.4), -1, fl[0], zg))
                gaps.append(box(x0 - POD - 0.5, vf - 1.4, x0 - POD + 0.5, vf + 1.4))
        bal = box(x0 - POD, y0, x0 - POD + 0.22, y1)
        if k == 0:
            bal = bal.union(box(x0 - POD, y0, x0, y0 + 0.22))
        bal = bal.difference(unary_union(gaps)) if gaps else bal
        L.prism(mb, "villa", bal, fl[0], fl[0] + 0.86)
        D.coping(mb, "villa", bal.buffer(0.03, join_style=2).intersection(pod.buffer(0.03, join_style=2)), fl[0] + 0.94, 0.08)
    dz = fN[0] - fS[0]                                         # between the two terraces: a flight on the southern one
    nf = max(1, int(math.ceil(dz / 0.16)))
    for k in range(nf):
        q = box(-POD + 0.22, A_S[3] - (nf - k) * 0.30, 0.0, A_S[3] - (nf - k - 1) * 0.30)
        L.prism(mb, "deck_stone", q, zbotA + 0.4, fS[0] + (k + 1) * dz / nf)
    hard += [gS, gN, porch]

    # =========================================================================================================
    # the gate pavilion on the crossing
    zX = zl(7.05, -4.0) + 0.15
    pv = box(*PAV)
    qx0, qy0, qx1, qy1 = PAV
    qc = ((qx0 + qx1) / 2, (qy0 + qy1) / 2)
    zpw = zX + 5.60
    t_ = 0.60
    aw, azs = 3.60, zX + 2.70
    box_walls(pv, zX - 0.6, zpw - 0.02,
              {"W": [((qx0, qc[1]), aw, zX, 0, "open", t_, azs)], "E": [((qx1, qc[1]), aw, zX, 0, "open", t_, azs)],
               "N": [((qc[0], qy1), aw, zX, 0, "blind", 0.14, azs)], "S": [((qc[0], qy0), aw, zX, 0, "blind", 0.14, azs)]})
    for xs, sgn in ((qx0, 1), (qx1, -1)):                     # inside faces, the arches' soffits, alfiz and zellige
        wall((xs + sgn * t_, qy0 + t_), (xs + sgn * t_, qy1 - t_), (sgn, 0), zX - 0.6, zpw - 0.02,
             [((xs + sgn * t_, qc[1]), aw, zX, 0, "open", 0.0, azs)])
        h = arch(qc[1], aw, azs, zX)
        soffit(h, zX, lambda s, z, k, xs=xs, sgn=sgn: (xs + sgn * t_ * k, s, z))
        al = box(qc[1] - 2.55, zX, qc[1] + 2.55, azs + 2.55)
        D.ext(mb, "surround", al.difference(h), lambda a, b, w, xs=xs, sgn=sgn: (xs - sgn * w, a, b), 0.0, 0.05)
        D.ext(mb, "tile_jade", box(qc[1] - 2.85, zX, qc[1] + 2.85, azs + 2.85).difference(al),
              lambda a, b, w, xs=xs, sgn=sgn: (xs - sgn * w, a, b), 0.0, 0.07)
    for ys, sgn in ((qy0, 1), (qy1, -1)):
        wall((qx0 + t_, ys + sgn * t_), (qx1 - t_, ys + sgn * t_), (0, sgn), zX - 0.6, zpw - 0.02)
    L.prism(mb, "villa", pv.buffer(-0.01, join_style=2), zpw - 0.20, zpw - 0.02, bottom=True)
    cornice(pv, zpw)
    roof(pv, zpw, zpw + PAR)
    rd = 2.30
    L.prism(mb, "villa", Point(*qc).buffer(rd, 48), zpw - 0.02, zpw + 1.50)
    L.prism(mb, "tile_jade", Point(*qc).buffer(rd + 0.03, 48).difference(Point(*qc).buffer(rd - 0.2, 48)), zpw + 1.05, zpw + 1.30)
    L.prism(mb, "ledge", Point(*qc).buffer(rd + 0.10, 48).difference(Point(*qc).buffer(rd - 0.2, 48)), zpw + 1.40, zpw + 1.50, bottom=True)
    dome(qc, rd, zpw + 1.50, rd * 1.10)
    L.prism(mb, "deck_stone", pv.buffer(-0.01, join_style=2), zX - 0.6, zX)
    fo = Point(*qc).buffer(1.05, 32)                           # the fountain
    L.prism(mb, "coping", fo.difference(fo.buffer(-0.18)), zX, zX + 0.45)
    L.prism(mb, "tile_jade", fo.buffer(-0.18), zX, zX + 0.05, sides=False)
    L.prism(mb, "pool_water", fo.buffer(-0.19), zX + 0.33, zX + 0.35, sides=False)
    L.prism(mb, "coping", Point(*qc).buffer(0.22, 16), zX, zX + 0.70)
    L.prism(mb, "bronze", Point(*qc).buffer(0.05, 8), zX + 0.70, zX + 0.95)
    L.prism(mb, "deck_stone", cross.difference(pv), zX - 2.2, zX)       # the crossing's terrace round it
    hard += [pv, cross]

    # =========================================================================================================
    # the suites: seven pairs stepping down the slope, higher and lower in turn
    b0u, b0v, b1u, b1v = B
    ws = (b1v - b0v) / N_SU
    zbotB = min(zl(x, y) for x in (b0u - 4.5, b1u) for y in (b0v, b1v)) - 0.6
    pairs = []
    for j in range(N_SU // 2):
        va, vb = b1v - (j + 1) * 2 * ws, b1v - j * 2 * ws
        f0 = round((zl(10.0, (va + vb) / 2) + 0.15) / 0.05) * 0.05
        pairs.append((va, vb, f0, f0 + 2 * FLB - 0.20 + (0.70 if j % 2 == 0 else 0.0)))
    for j, (va, vb, f0, zr) in enumerate(pairs):
        g = box(b0u, va, b1u, vb)
        f1 = f0 + FLB
        su = [va + ws / 2, va + 1.5 * ws]
        west = [((b0u, v), 2.40, f0, f0 + 2.60, "fr", 0.30) for v in su] + [((b0u, v), 1.60, f1, f1 + 2.50, "fr", 0.30) for v in su]
        east = [((b1u, v - 0.9), 1.00, f0, f0 + 2.30, "door", 0.30) for v in su] + [((b1u, v + 0.8), 0.80, f0 + 1.0, f0 + 2.2, "win", 0.30) for v in su]
        east += [((b1u, v), 0.90, f1 + 0.9, f1 + 2.3, "win", 0.30) for v in su]
        east += [((b1u, v + d_), 0.20, zr - 0.75, zr - 0.55, "niche", 0.10) for v in su for d_ in (-0.9, 0.0, 0.9)]
        wall((b0u, vb), (b0u, va), (-1, 0), zbotB, zr - 0.02, west)
        wall((b1u, va), (b1u, vb), (1, 0), zbotB, zr - 0.02, east)
        cut_r, cut_c = Polygon(), Polygon()
        for jn, side, sg in ((j - 1, vb, 1), (j + 1, va, -1)):     # the steps between pairs
            if 0 <= jn < len(pairs):
                cut_c = cut_c.union(box(b0u - 1, side, b1u + 1, side + sg))
                if pairs[jn][3] < zr:
                    wall((b0u, side), (b1u, side), (0, sg), pairs[jn][3] - 0.02, zr - 0.02)
                else:
                    cut_r = cut_r.union(box(b0u + 0.30, min(side, side - sg * 0.31), b1u - 0.30, max(side, side - sg * 0.31)))
            else:
                ends = [((u, side), 1.10, f + 1.0, f + 2.4, "win", 0.30) for u in (3.5, 10.0) for f in (f0, f1)]
                wall((b0u, side), (b1u, side), (0, sg), zbotB, zr - 0.02, ends)
        cornice(g, zr, cut_c)
        roof(g, zr, zr + PAR, cut_r, horns=(j % 2 == 0))
        L.prism(mb, "interior_floor", g.buffer(-0.05, join_style=2), zbotB + 0.4, f0)
        # each suite's terrace: walls between, a parapet with its opening and steps, the cedar pergola; balcony
        for i, v in enumerate(su):
            sa, sb_ = v - ws / 2, v + ws / 2
            ter = box(b0u - 3.4, sa, b0u, sb_)
            L.prism(mb, "villa", ter, zbotB + 0.4, f0 - 0.03)
            L.prism(mb, "terrace", ter, f0 - 0.03, f0)
            hard.append(ter)
            for sep in [box(b0u - 3.4, sa, b0u, sa + 0.20)] + ([box(b0u - 3.4, sb_ - 0.20, b0u, sb_)] if j == 0 and i == 1 else []):
                L.prism(mb, "villa", sep, f0, f0 + 1.20)
                D.coping(mb, "villa", sep.buffer(0.03, join_style=2), f0 + 1.28, 0.08)
            for g2 in (box(b0u - 3.4, sa + 0.2, b0u - 3.2, v - 0.8), box(b0u - 3.4, v + 0.8, b0u - 3.2, sb_ - (0.2 if j == 0 and i == 1 else 0.0))):
                L.prism(mb, "villa", g2, f0, f0 + 0.82)
                D.coping(mb, "villa", g2.buffer(0.03, join_style=2), f0 + 0.90, 0.08)
            zg = zl(b0u - 4.0, v)
            if f0 - zg > 0.20:
                hard.append(steps((b0u - 3.4, v - 0.8, v + 0.8), -1, f0, zg))
            for kk in range(6):
                vv = sa + 0.35 + (ws - 0.70) * kk / 5
                mb.box("timber", b0u - 3.45, b0u, vv - 0.04, vv + 0.04, f0 + 2.85, f0 + 3.05)
            mb.box("timber", b0u - 3.30, b0u - 3.12, sa + 0.25, sb_ - 0.25, f0 + 2.70, f0 + 2.85)
            for vv in (sa + 0.35, sb_ - 0.35):
                mb.box("timber", b0u - 3.29, b0u - 3.13, vv - 0.08, vv + 0.08, f0 + 0.82, f0 + 2.70)
            L.prism(mb, "surround", box(b0u - 1.0, v - 1.15, b0u, v + 1.15), f1 - 0.14, f1, bottom=True)
            L.prism(mb, "timber", box(b0u - 1.0, v - 1.15, b0u - 0.94, v + 1.15), f1 + 0.95, f1 + 1.02, bottom=True)
            for vv in (v - 1.15, v + 1.12):
                L.prism(mb, "timber", box(b0u - 1.0, vv, b0u, vv + 0.03), f1, f1 + 1.02)
            for kk in range(13):
                vv = v - 1.10 + 2.20 * kk / 12
                mb.box("timber", b0u - 0.99, b0u - 0.95, vv - 0.02, vv + 0.02, f1, f1 + 0.95)
            plants.append(("shrub", b0u - 2.9, sa + 0.6, f0, 0.85))
    hard.append(box(*B))

    # =========================================================================================================
    # the water garden: three basins stepping down, the arm, decks, kerbs
    pu0, pv0, _, pv1 = pool.bounds
    pu1 = pool.intersection(box(-1e3, pv0, 1e3, pv0 + 3.0)).bounds[2]
    _, av0, au1, av1 = pool.intersection(box(pu1 + 0.5, -1e3, 1e3, 1e3)).bounds
    uc, vac = (pu0 + pu1) / 2, (av0 + av1) / 2
    zN, zC, zS = (zl(uc, (av1 + pv1) / 2) + 0.15, zl(uc, vac) + 0.15, zl(uc, (pv0 + av0) / 2) + 0.15)
    LN = pool.intersection(box(-1e3, av1 + W2, 1e3, 1e3))
    LC = unary_union([pool.intersection(box(-1e3, av0 + W2, pu1, av1 - W2)), pool.intersection(box(pu1, -1e3, 1e3, 1e3))])
    LS = pool.intersection(box(-1e3, -1e3, 1e3, av0 - W2))
    WN = pool.intersection(box(-1e3, av1 - W2, pu1, av1 + W2))
    WS = pool.intersection(box(-1e3, av0 - W2, pu1, av0 + W2))
    for g, zb, cut, wat in ((LN, zN, WN, unary_union([LN, WN])), (LC, zC, unary_union([WN, WS]), unary_union([LC, WS])), (LS, zS, WS, LS)):
        L.prism(mb, "tile_jade", g, zb - 1.45, zb - 1.40, sides=False)
        L.prism(mb, "tile_jade", g.buffer(0.01, join_style=2).difference(g.buffer(-0.01, join_style=2)).difference(cut.buffer(0.02)), zb - 1.40, zb - 0.04)
        L.prism(mb, "pool_water", wat.buffer(-0.01, join_style=2), zb - 0.125, zb - 0.12, sides=False)
    for wg, zhi, zlo, vw in ((WN, zN, zC, av1 - W2), (WS, zC, zS, av0 - W2)):     # the weirs, the water over them
        L.prism(mb, "coping", wg, zlo - 1.45, zhi - 0.13)
        mb.poly("pool_water", [(pu1, vw - 0.012, zlo - 0.12), (pu0, vw - 0.012, zlo - 0.12), (pu0, vw - 0.012, zhi - 0.125), (pu1, vw - 0.012, zhi - 0.125)])
    for k in range(3):                                         # the arm's head: zellige, three bronze spouts
        vv = av0 + (av1 - av0) * (k + 1) / 4
        mb.box("bronze", au1 - 0.35, au1, vv - 0.06, vv + 0.06, zX - 0.42, zX - 0.30)
        q = [(au1 - 0.35, vv - 0.03, zC - 0.12), (au1 - 0.35, vv + 0.03, zC - 0.12), (au1 - 0.40, vv + 0.03, zX - 0.40), (au1 - 0.40, vv - 0.03, zX - 0.40)]
        mb.poly("pool_water", q)
        mb.poly("pool_water", q[::-1])
    mb.poly("tile_jade", [(au1 - 0.005, av1, zC - 0.12), (au1 - 0.005, av0, zC - 0.12), (au1 - 0.005, av0, zX - 0.05), (au1 - 0.005, av1, zX - 0.05)])
    hard.append(pool)
    # decks, coping and kerbs, each at its basin's level (the kerbs retain the lawn where it stands higher)
    RC = unary_union([box(-1e3, av0, 1e3, av1), box(pu1, av0 - DECK, 1e3, av1 + DECK)])
    RN = box(-1e3, av1, 1e3, 1e3).difference(RC)
    RS = box(-1e3, -1e3, 1e3, av0).difference(RC)
    blocked = unary_union(hard)
    near = pool.buffer(DECK, join_style=2).intersection(garden).difference(pool).difference(blocked)
    cop = pool.buffer(0.35, join_style=2).intersection(near)
    kerb_w = near.intersection(box(rill.bounds[2] - 0.01, -1e3, pu0 - 0.35, 1e3))
    dk = near.difference(kerb_w).difference(cop)
    hardk = unary_union([dk, cop])
    kerb = unary_union([hardk.buffer(0.30, join_style=2).intersection(garden).difference(hardk).difference(pool).difference(blocked), kerb_w])
    decks = []
    for R, zb in ((RN, zN), (RC, zC), (RS, zS)):
        L.prism(mb, "deck_stone", dk.intersection(R), zb - 2.2, zb)
        L.prism(mb, "coping", cop.intersection(R), zb - 2.2, zb + 0.04)
        L.prism(mb, "coping_beige", kerb.intersection(R), -2.2, 0.12, zf=lambda x, y, zb=zb: max(zl(x, y), zb))
        decks.append((dk.intersection(R), zb))
    hard += [dk, cop, kerb]

    # =========================================================================================================
    # the promenade and its gate on street 7, the walls on the streets, the lawns, what is left paved
    L.prism(mb, "pave_beige", rill, -2.2, 0.10, zf=zl)
    hard.append(rill)
    inlet = rill.intersection(box(-1e3, -1e3, rill.bounds[0] + 2.0, 1e3))
    gv0, gv1 = inlet.bounds[1], inlet.bounds[3]
    gu, gvc = plot.bounds[0], (inlet.bounds[1] + inlet.bounds[3]) / 2
    zg0 = zl(gu, gvc) + 0.10
    gblk = box(gu, gv0 - 1.2, gu + 0.60, gv1 + 1.2)
    gw, gzs = gv1 - gv0, zg0 + 1.90
    box_walls(gblk, zg0 - 0.8, zg0 + 3.98,
              {"W": [((gu, gvc), gw, zg0, 0, "gdoor", 0.30, gzs)], "E": [((gu + 0.6, gvc), gw, zg0, 0, "open", 0.0, gzs)]})
    h = arch(gvc, gw, gzs, zg0)
    soffit(h, zg0, lambda s, z, k: (gu + 0.30 + 0.30 * k, s, z))
    cornice(gblk, zg0 + 4.00)
    roof(gblk, zg0 + 4.00, zg0 + 4.80)
    D.ext(mb, "surround", box(gvc - 1.60, zg0, gvc + 1.60, zg0 + 3.75).difference(h), lambda a, b, w: (gu - w, a, b), 0.0, 0.05)
    L.prism(mb, "pave_beige", gblk.intersection(box(-1e3, gv0, 1e3, gv1)), -0.8, 0.10, zf=zl)
    hard.append(gblk)
    edge = plot.exterior.intersection(garden.boundary)
    wl = edge.buffer(0.25, cap_style=2, join_style=2).intersection(plot).difference(gblk.buffer(0.02))
    wl = unary_union([q for q in L.as_polys(wl) if q.area > 0.3])
    L.prism(mb, "villa", wl, -0.8, 1.94, zf=zl)
    L.prism(mb, "coping_beige", wl.buffer(0.03, join_style=2), 1.94, 2.02, zf=zl)
    hard.append(wl)
    lawn_g = garden.difference(unary_union(hard))
    lawn_g = unary_union([q for q in L.as_polys(lawn_g) if q.area > 0.05])
    L.prism(mb, lawn, lawn_g, -2.2, 0.07, zf=zl)
    rest = plot.difference(unary_union([garden] + hard))
    rest = unary_union([q for q in L.as_polys(rest) if q.area > 0.02])
    L.prism(mb, "deck_stone", rest, -1.0, 0.10, zf=zl)

    # =========================================================================================================
    # trees: palms along the promenade and the decks, olive trees in the lawns; loungers and parasols
    rx0 = rill.intersection(box(rill.bounds[0] + 2.5, -1e3, 1e3, 1e3)).bounds[0]
    strip = lawn_g.intersection(box(-1e3, -1e3, rx0, 1e3)).buffer(-0.6)
    for vv in np.arange(rill.bounds[1] + 1.5, rill.bounds[3], 5.5):
        if abs(vv - gvc) > 3.5:
            for x_, kind, s_ in (((gu + rx0) / 2 + 0.2, "wash", 0.85), ((gu + rx0) / 2 - 0.1, "shrub", 0.9)):
                p = Point(x_, vv if kind == "wash" else vv + 2.75)
                if strip.contains(p):
                    plants.append((kind, p.x, p.y, zl(p.x, p.y), s_))
    for d_, zb in decks:
        for vv in np.arange(pv0 + 2.0, pv1 + 2.0, 7.0):
            if d_.buffer(-0.3).contains(Point(pu1 + 2.15, vv)):
                plants.append(("date", pu1 + 2.15, vv, zb, 0.75))
            for dv in (2.3, 4.7):
                x, y = pu1 + 1.45, vv + dv
                if d_.buffer(-0.05).contains(box(x - 0.95, y - 0.4, x + 0.95, y + 0.4)):
                    lounger(x, y, -math.pi / 2, zb)
            if d_.buffer(-0.2).contains(Point(pu1 + 2.0, vv + 3.5)):
                parasol(pu1 + 2.0, vv + 3.5, zb)
    for a, b in ((qx1 + 1.6, qy0 + 0.9), (qx1 + 1.6, qy1 - 0.9)):
        plants.append(("date", a, b, zX, 0.8))
    hu = unary_union(hard)
    spots = [Point(x, y) for x in np.arange(-26.0, 0.0, 6.5) for y in np.arange(-63.0, 51.0, 7.5)]
    spots = [p for p in spots if lawn_g.buffer(-1.8).contains(p) and hu.distance(p) > 2.2]
    for k, p in enumerate(spots):
        plants.append(("olive" if k % 3 else "date", p.x, p.y, zl(p.x, p.y) + 0.07, 0.8 if k % 3 else 0.7))

    obs = mb.build(name, col, M, location=(float(o[0]), float(o[1]), 0.0), rotation_z=math.atan2(U[1], U[0]))
    print(f"  T3 hotel: north building floors {fS[0]:.2f} / {fN[0]:.2f}, pavilion {zX:.2f}, basins {zN:.2f} / {zC:.2f} / {zS:.2f}, "
          f"suites {pairs[0][2]:.2f} .. {pairs[-1][2]:.2f}, {len(plants)} plants")
    return obs, plants, (o, U, V)
