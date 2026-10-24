"""
17_hotel — the hotel (client 23-10: "for hotel we dont have plan so i want you to be creative and give me
proposition ... perfect and the same style we have on our residence ... not the same design ... the perfect one").

A DESIGN PROPOSAL, not a drawing. It keeps the plan de masse's zoning of the hotel's plot (between street 7
and the parking, 31 x 117 m): the two buildings on their cells along the parking, the crossing between them,
the long basin with its arm on the crossing's axis, the promenade along the basin with its gate on street 7 on
the same axis, the garden. The residence's materials (the sand render, the taupe stone surrounds, the grey
ledge / ochre band cornice, the rounded coping, the horns, quartz aluminium, cedar, mashrabiya, green zellige)
in forms of its own, on a water garden.

Client 24-10: the SPA is right; the hotel's two buildings were permit drawings, ordinary: one height right and
left, two storeys, the SPA's style. Second review the same day: the suites the same as the main building, the
parking front is the principal one and wants real decoration, the pavilion changed for something better, the
trottoir again. So:
  the two buildings, one design, each in two halves of two storeys stepping with the ground (roofs +7.80 over
    each half's floor): the main building on the north cell (2 x 7 bays of 3.25 m), the suites on the south one
    (2 x 9 bays of 3.13 m), both 14.1 m deep on the parking line. On the garden the SPA's louvred glazing on the
    stone terrace with its balustrade and flights, french windows upstairs behind cedar mashrabiya screens or
    onto stone balconies, a centre block with the SPA's studded door; on the parking a pointed horseshoe window
    in each bay (glass, a mashrabiya in the arch, the taupe frame, the alfiz with zellige spandrels), a zellige
    frieze under a stone string course, mashrabiya oriels on corbels and stone balconies upstairs, bronze
    lanterns on the taupe pilasters, a carved band under the cornice, and a centre block with the grand entrance
    (the horseshoe arch in its zellige alfiz, studded doors under a mashrabiya tympanum, steps down to the
    trottoir); domed towers at the corners facing the pavilion; on the roofs a dome on its drum, parasols and
    loungers, a cedar pergola; the main building's gate block on the Voie Publique (+10.40, the horseshoe arch
    in its zellige alfiz, studded doors under a mashrabiya tympanum, steps down inside);
  the gate pavilion on the crossing, standing over both: walls to +9.00, monumental pointed horseshoe arches east
    (from the parking) and west (onto the arm's head) in taupe alfiz framed in zellige under a row of niches,
    blind zellige arches north and south, four corner turrets with small domes, the drum with its zellige band
    and arched lights, the dome to about +14 with its bronze finial, a fountain inside;
  the trottoir (TROT, trottoir()): along the parking front of both and round the gate block, built by
    19_tranche3 with Tranche 3's pavements;
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
FL_A = (0.20, 4.20)                      # floors over each half's reference ground (client 24-10: two storeys)
ZR_A, PAR, PW = 7.80, 0.80, 1.00         # roof terrace; parapets of the pavilion and of the two wings
NB_A, NB_B = 7, 9                        # bays per half: main building (3.25 m), suites (3.13 m)
POD = 3.0                                # the garden terrace along the garden fronts
B = (0.0, -64.8, 14.1, -8.4)             # the suites (client 24-10: the same as the main building)
B_N = (0.0, -36.6, 14.1, -8.4)           # their two halves
B_S = (0.0, -64.8, 14.1, -36.6)
TOWERS_B = ((0.0, -13.4, 5.0, -8.4), (9.1, -13.4, 14.1, -8.4))
TROT, TROT_DZ = 2.50, 0.15               # the trottoir along the parking front and on the Voie Publique (19_tranche3)
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


def trottoir():
    """The trottoir in the hotel's frame (client 24-10: "3awet tritoire"): along the parking front of both
    buildings, from the south road's pavement to the Voie Publique, and along the main building's north front
    round the gate block; built with Tranche 3's pavements (19_tranche3), TROT_DZ over the street."""
    band = unary_union([box(A_S[2], B[1] - 0.45, A_S[2] + TROT, A_N[3] + 4.10), box(A_N[0], A_N[3], A_S[2] + TROT, A_N[3] + 4.10)])
    return band.difference(unary_union([box(A_N[0], B[1], A_N[2], A_N[3]), box(*PORCH)]))


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

    def f_louv(P3, h, dep):
        """the SPA's glazing: glass doors to the transom, louvres over it, quartz aluminium mullions, sheers,
        the stone surround"""
        s0, z0, s1, z1 = h.bounds
        n, d, zt_ = max(2, int(round((s1 - s0) / 0.75))), 0.14, z0 + 2.30
        rect(P3, "interior", s0 - 0.3, s1 + 0.3, z0, z1 + 0.3, 1.10)
        rect(P3, "glass", s0, s1, z0, zt_, d)
        rect(P3, "glass", s0, s1, zt_, z1, d + 0.06)
        for k in range(n + 1):
            sk = s0 + (s1 - s0) * k / n
            D.pbox(mb, P3, max(s0, sk - 0.04), min(s1, sk + 0.04), z0, z1, d - 0.05, d + 0.04, "frame")
        for zz in (z0, zt_ - 0.04, z1 - 0.06):
            D.pbox(mb, P3, s0, s1, zz, zz + 0.06, d - 0.05, d + 0.04, "frame")
        zz = zt_ + 0.10
        while zz < z1 - 0.10:
            D.pbox(mb, P3, s0, s1, zz, zz + 0.035, d - 0.03, d + 0.03, "frame")
            zz += 0.135
        rect(P3, "curtain", s0 + 0.06, s0 + 0.06 + (s1 - s0) * 0.16, z0 + 0.05, zt_ - 0.05, 0.36)
        rect(P3, "curtain", s1 - 0.06 - (s1 - s0) * 0.16, s1 - 0.06, z0 + 0.05, zt_ - 0.05, 0.36)
        for a0, a1, b0, b1 in ((s0 - 0.20, s0, z0, z1 + 0.22), (s1, s1 + 0.20, z0, z1 + 0.22), (s0, s1, z1, z1 + 0.22)):
            D.pbox(mb, P3, a0, a1, b0, b1, -0.04, 0.02, "surround")

    def f_tall(P3, h, dep):
        """the SPA's tall window in its stone frame of two borders: glass, aluminium frame, curtains"""
        s0, z0, s1, z1 = h.bounds
        d = 0.12
        rect(P3, "interior", s0 - 0.3, s1 + 0.3, z0 - 0.3, z1 + 0.3, 0.80)
        rect(P3, "glass", s0 + 0.12, s1 - 0.12, z0 + 0.12, z1 - 0.12, d)
        for a0, a1, b0, b1 in ((s0 + 0.06, s1 - 0.06, z0 + 0.06, z0 + 0.12), (s0 + 0.06, s1 - 0.06, z1 - 0.12, z1 - 0.06),
                               (s0 + 0.06, s0 + 0.12, z0 + 0.12, z1 - 0.12), (s1 - 0.12, s1 - 0.06, z0 + 0.12, z1 - 0.12),
                               ((s0 + s1) / 2 - 0.03, (s0 + s1) / 2 + 0.03, z0 + 0.12, z1 - 0.12)):
            D.pbox(mb, P3, a0, a1, b0, b1, d - 0.03, d + 0.03, "frame")
        rect(P3, "curtain", s0 + 0.12, s0 + 0.30, z0 + 0.15, z1 - 0.15, 0.30)
        rect(P3, "curtain", s1 - 0.30, s1 - 0.12, z0 + 0.15, z1 - 0.15, 0.30)
        for w, df in ((0.16, -0.05), (0.06, -0.08)):
            for a0, a1, b0, b1 in ((s0 - w, s0, z0 - w, z1 + w), (s1, s1 + w, z0 - w, z1 + w), (s0, s1, z1, z1 + w), (s0, s1, z0 - w, z0)):
                D.pbox(mb, P3, a0, a1, b0, b1, df, 0.02, "surround")

    def f_msh(P3, h, dep):
        """a french window behind a cedar mashrabiya screen in its frame"""
        f_fr(P3, h, dep)
        s0, z0, s1, z1 = h.bounds
        rect(P3, "mashrabiya", s0 + 0.02, s1 - 0.02, z0 + 0.02, z1 - 0.02, 0.06)
        for a0, a1, b0, b1 in ((s0, s1, z0, z0 + 0.08), (s0, s1, z1 - 0.08, z1), (s0, s0 + 0.08, z0, z1), (s1 - 0.08, s1, z0, z1),
                               (s0, s1, z0 + 1.00, z0 + 1.06)):
            D.pbox(mb, P3, a0, a1, b0, b1, 0.03, 0.07, "timber")

    def f_sdoor(P3, h, dep):
        """the SPA's centre door: studded leaves to +3.00 and the studded transom, in the taupe alfiz"""
        s0, z0, s1, z1 = h.bounds
        d, zt_ = 0.28, z0 + 3.0
        for a0, a1, b0, b1 in ((s0, (s0 + s1) / 2 - 0.01, z0, zt_), ((s0 + s1) / 2 + 0.01, s1, z0, zt_), (s0, s1, zt_ + 0.10, z1)):
            rect(P3, "door_wood", a0, a1, b0, b1, d)
            nx, nz = max(2, int((a1 - a0) / 0.16)), max(2, int((b1 - b0) / 0.18))
            for i in range(nx):
                for j in range(nz):
                    a = a0 + 0.08 + (a1 - a0 - 0.16) * i / (nx - 1)
                    b = b0 + 0.08 + (b1 - b0 - 0.16) * j / (nz - 1)
                    D.pbox(mb, P3, a - 0.013, a + 0.013, b - 0.013, b + 0.013, d - 0.02, d, "metal_dark")
        D.pbox(mb, P3, s0, s1, zt_, zt_ + 0.10, d - 0.04, d, "door_wood")
        for k in (-1, 1):
            D.pbox(mb, P3, (s0 + s1) / 2 + k * 0.20 - 0.07, (s0 + s1) / 2 + k * 0.20 + 0.07, z0 + 1.05, z0 + 1.13, d - 0.06, d, "metal_dark")
        D.ext(mb, "surround", box(s0 - 0.52, z0, s1 + 0.52, z1 + 0.37).difference(box(s0, z0, s1, z1)), lambda a, b, w: P3(a, b, w), -0.06, 0.0)
        D.ext(mb, "surround", box(s0 - 0.30, z0, s1 + 0.30, z1 + 0.17).difference(box(s0 - 0.20, z0, s1 + 0.20, z1 + 0.07)),
              lambda a, b, w: P3(a, b, w), -0.10, -0.06)

    def f_awin(P3, h, dep):
        """the parking front's window: a pointed horseshoe arch, glass under the springing, a cedar mashrabiya in
        the arch, the taupe frame, the alfiz with green zellige in its spandrels, the stone sill"""
        s0, z0, s1, z1 = h.bounds
        w, sm = s1 - s0, (s0 + s1) / 2
        zs = z1 - math.sqrt((w / 2 + 0.25) ** 2 - 0.0625)          # the springing (14_villa_c.arch_poly)
        d = dep - 0.10
        rect(P3, "interior", s0 - 0.3, s1 + 0.3, z0, z1 + 0.3, dep + 0.9)
        for g, mat, dd in ((h.intersection(box(s0 - 1, z0 - 1, s1 + 1, zs)), "glass", d), (h.intersection(box(s0 - 1, zs, s1 + 1, z1 + 1)), "mashrabiya", d - 0.04)):
            for q in L.as_polys(g):
                for t in L.tri_poly(q):
                    mb.poly(mat, [P3(s, z, dd) for s, z in t], [(s, z) for s, z in t])
        for a0, a1, b0, b1 in ((sm - 0.03, sm + 0.03, z0, zs), (s0, s1, zs - 0.04, zs + 0.02), (s0, s1, z0, z0 + 0.06)):
            D.pbox(mb, P3, a0, a1, b0, b1, d - 0.07, d - 0.01, "frame")
        rect(P3, "curtain", s0 + 0.05, s0 + 0.30, z0 + 0.05, zs - 0.05, d + 0.20)
        rect(P3, "curtain", s1 - 0.30, s1 - 0.05, z0 + 0.05, zs - 0.05, d + 0.20)
        ring = h.buffer(0.14, join_style=2).difference(h).intersection(box(s0 - 1, z0, s1 + 1, z1 + 1))
        D.ext(mb, "surround", ring, lambda a, b, w_: P3(a, b, w_), -0.04, 0.01)
        spd = box(s0 - 0.20, zs, s1 + 0.20, z1 + 0.20).difference(h.buffer(0.14, join_style=2))
        D.ext(mb, "tile_jade", spd, lambda a, b, w_: P3(a, b, w_), -0.015, 0.0)
        alf = box(s0 - 0.32, z0, s1 + 0.32, z1 + 0.32).difference(box(s0 - 0.20, z0, s1 + 0.20, z1 + 0.20))
        D.ext(mb, "surround", alf, lambda a, b, w_: P3(a, b, w_), -0.05, 0.0)
        D.pbox(mb, P3, s0 - 0.32, s1 + 0.32, z0 - 0.14, z0, -0.10, 0.02, "surround")

    FILL = {"niche": f_niche, "blind": f_blind, "win": f_win, "fr": f_fr, "door": f_door, "arch": f_arch,
            "louv": f_louv, "tall": f_tall, "msh": f_msh, "sdoor": f_sdoor,
            "gate": lambda P3, h, dep: gate(P3, h, dep, 2.6, 3.8), "egate": lambda P3, h, dep: gate(P3, h, dep, 2.0, 2.9),
            "awin": f_awin,
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

    def dome(c, r, z0, h, n=40, nr=10, finial=True):
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
        if not finial:
            return
        L.prism(mb, "bronze", Point(*c).buffer(0.10, 10), zt - 0.05, zt + 0.15)
        L.prism(mb, "bronze", Point(*c).buffer(0.03, 6), zt, zt + 1.0)
        for r_, zz in ((0.17, 0.45), (0.12, 0.78)):
            L.prism(mb, "bronze", Point(*c).buffer(r_, 12), zt + zz - r_ * 0.8, zt + zz + r_ * 0.8)

    def qubba(c, r, z0, zd, h, finial=True):
        """a dome on its drum, the ledge round the drum's head"""
        L.prism(mb, "villa", Point(*c).buffer(r, 40), z0, zd)
        L.prism(mb, "ledge", Point(*c).buffer(r + 0.08, 40).difference(Point(*c).buffer(r - 0.2, 40)), zd - 0.10, zd, bottom=True)
        dome(c, r, zd, h, finial=finial)

    hard = []                                                 # everything that is not lawn

    # =========================================================================================================
    # the two buildings, one design (client 24-10, second review: the suites "ghsha dkun the same likayn f lisar",
    # the parking front is the principal one, "chi zwa9 wa3er"): each in two halves of two storeys stepping with
    # the ground, the roofs +7.80 over each half's floor. On the garden the SPA's louvred glazing on the stone
    # terrace, french windows upstairs behind cedar mashrabiya screens or onto stone balconies, a centre block with
    # the SPA's studded door. On the parking a pointed horseshoe window in each bay, its alfiz with green zellige
    # in the spandrels, a zellige frieze under a stone string course, cedar mashrabiya oriels on stone corbels and
    # stone balconies upstairs, bronze lanterns on the taupe pilasters, and a centre block with the grand entrance:
    # the horseshoe arch in its zellige alfiz, studded doors under a mashrabiya tympanum, steps down to the
    # trottoir. Domed towers at the corners facing the pavilion; domes, parasols and a cedar pergola on the roofs.
    def horns_at(g, zt, corners):
        """the curled horns at the chosen corners of a box: (0 | 1, 0 | 1) for its low or high u and v"""
        us = [0.80 - 0.62 * k / 12 for k in range(13)]
        prof = Polygon([(0.0, zt - 0.40), (0.80, zt - 0.40)] + [(u_, zt + 0.43 * ((0.80 - u_) / 0.62) ** 1.6) for u_ in us]
                       + [(0.07, zt + 0.41), (0.0, zt + 0.34)])
        prof_b = prof.intersection(box(0.20, -50.0, 2.0, 50.0))
        cx0, cy0, cx1, cy1 = g.buffer(0.012, join_style=2).bounds
        for i, j in corners:
            xc, sx = (cx0, 1) if i == 0 else (cx1, -1)
            yc, sy = (cy0, 1) if j == 0 else (cy1, -1)
            D.horn(mb, prof, lambda a, b, w, xc=xc, sx=sx, yc=yc, sy=sy: (xc + sx * a, yc + sy * w, b))
            D.horn(mb, prof_b, lambda a, b, w, xc=xc, sx=sx, yc=yc, sy=sy: (xc + sx * w, yc + sy * a, b))

    def pilasters(P3, ss, z0, z1, w=0.50, d=0.08):
        for s_ in ss:
            D.pbox(mb, P3, s_ - w / 2, s_ + w / 2, z0, z1, -d, 0.0, "surround")
            D.pbox(mb, P3, s_ - w / 2 - 0.04, s_ + w / 2 + 0.04, z1 - 0.16, z1, -d - 0.04, 0.0, "surround")
            D.pbox(mb, P3, s_ - w / 2 - 0.03, s_ + w / 2 + 0.03, z0, z0 + 0.40, -d - 0.03, 0.0, "surround")

    def balcony(P3, s_, zb, w=1.05):
        c0, c1 = s_ - w, s_ + w
        D.pbox(mb, P3, c0, c1, zb - 0.14, zb, -0.80, 0.0, "surround")
        for kk in range(3):
            sb = c0 + 0.25 + (c1 - c0 - 0.50) * kk / 2
            D.pbox(mb, P3, sb - 0.07, sb + 0.07, zb - 0.42, zb - 0.14, -0.60, 0.0, "surround")
        D.pbox(mb, P3, c0, c1, zb + 0.95, zb + 1.02, -0.80, -0.72, "timber")
        for kk in range(13):
            sb = c0 + 0.05 + (c1 - c0 - 0.10) * kk / 12
            D.pbox(mb, P3, sb - 0.02, sb + 0.02, zb, zb + 0.95, -0.78, -0.74, "timber")
        for sa in (c0, c1):
            D.pbox(mb, P3, sa - 0.03, sa + 0.03, zb, zb + 1.02, -0.80, 0.0, "timber")

    def oriel(P3, s_, zb, zt, w=1.80, d=0.70):
        """a cedar mashrabiya oriel on three stone corbels, under its cedar cap and zellige roll"""
        a, b = s_ - w / 2, s_ + w / 2
        D.pbox(mb, P3, a, b, zb - 0.14, zb, -d, 0.0, "surround")
        for kk in range(3):
            c = a + 0.30 + (w - 0.60) * kk / 2
            D.pbox(mb, P3, c - 0.08, c + 0.08, zb - 0.60, zb - 0.14, -d + 0.20, 0.0, "surround")
        rect(P3, "mashrabiya", a + 0.05, b - 0.05, zb, zt, -d + 0.03)
        for sa in (a + 0.03, b - 0.03):
            mb.poly("mashrabiya", [P3(sa, zb, -0.02), P3(sa, zb, -d + 0.05), P3(sa, zt, -d + 0.05), P3(sa, zt, -0.02)])
        for a0, a1, d0, d1 in ((a, a + 0.06, -d, -d + 0.06), (b - 0.06, b, -d, -d + 0.06), (a, a + 0.06, -0.06, 0.0), (b - 0.06, b, -0.06, 0.0)):
            D.pbox(mb, P3, a0, a1, zb, zt, d0, d1, "timber")
        for zz in (zb, zb + 1.00, zt - 0.08):
            D.pbox(mb, P3, a, b, zz, zz + 0.08, -d, -d + 0.06, "timber")
        D.pbox(mb, P3, a - 0.10, b + 0.10, zt, zt + 0.10, -d - 0.12, 0.0, "timber")
        D.pbox(mb, P3, a - 0.04, b + 0.04, zt + 0.10, zt + 0.22, -d - 0.06, 0.0, "tile_jade")

    def lantern(P3, s_, z):
        """a bronze wall lantern on its bracket"""
        D.pbox(mb, P3, s_ - 0.03, s_ + 0.03, z + 0.30, z + 0.36, -0.32, -0.08, "metal_dark")
        D.pbox(mb, P3, s_ - 0.11, s_ + 0.11, z, z + 0.04, -0.44, -0.20, "bronze")
        D.pbox(mb, P3, s_ - 0.11, s_ + 0.11, z + 0.26, z + 0.30, -0.44, -0.20, "bronze")
        D.pbox(mb, P3, s_ - 0.09, s_ + 0.09, z + 0.04, z + 0.26, -0.42, -0.22, "glass")

    def pergola(v0, v1, zr):
        for vv in np.arange(v0 + 0.2, v1 - 0.19, 0.60):
            mb.box("timber", 1.8, 12.3, vv - 0.05, vv + 0.05, zr + 2.70, zr + 2.86)
        for uu in (2.2, 11.9):
            mb.box("timber", uu - 0.10, uu + 0.10, v0, v1, zr + 2.50, zr + 2.70)
            for vv in (v0 + 0.2, v1 - 0.2):
                mb.box("timber", uu - 0.09, uu + 0.09, vv - 0.09, vv + 0.09, zr, zr + 2.50)

    porch = box(*PORCH)
    WINGS = (("main", (A_S, A_N), NB_A, TOWERS, 1), ("suites", (B_N, B_S), NB_B, TOWERS_B, -1))
    wings = {}
    for wname, cells, nb, tws, dirv in WINGS:
        towers = [box(*t) for t in tws]
        zbot = min(zl(x, y) for x in (-POD - 2.5, 14.1 + TROT) for c_ in cells for y in (c_[1], c_[3])) - 1.8
        halves = []
        for c_ in cells:
            z0 = zl(7.05, (c_[1] + c_[3]) / 2)
            halves.append((box(*c_), [z0 + f for f in FL_A], z0 + ZR_A))
        (g_in, fl_in, zr_in), (g_out, fl_out, zr_out) = halves
        v_in = g_in.bounds[1] if dirv > 0 else g_in.bounds[3]            # the end facing the pavilion
        v_b = g_in.bounds[3] if dirv > 0 else g_in.bounds[1]             # the step between the halves
        v_far = g_out.bounds[3] if dirv > 0 else g_out.bounds[1]         # the far end
        hi = 0 if zr_in > zr_out else 1                                  # the higher half
        up = 1 if halves[hi][0].centroid.y > v_b else -1                 # from the lower half towards the higher
        wings[wname] = (halves, zbot)
        cbs = []
        for k, (g, fl, zr) in enumerate(halves):
            x0, y0, x1, y1 = g.bounds
            zw = zr - 0.02
            bay = (y1 - y0) / nb
            cs = [y0 + (i + 0.5) * bay for i in range(nb)]
            mid = cs[nb // 2]
            side = [v for v in cs if abs(v - mid) > 0.1]
            bnd = [y0 + i * bay for i in range(nb + 1)]
            # the garden front
            wl = min(2.0, bay - 1.30)
            west = [((x0, v), wl, fl[0], fl[0] + 3.20, "louv", 0.30) for v in side]
            west += [((x0, v), 1.40, fl[1], fl[1] + 2.60, "msh" if i % 2 else "fr", 0.30) for i, v in enumerate(side)]
            P3w, sw = wall((x0, y1), (x0, y0), (-1, 0), zbot, zw, west)
            pilasters(P3w, [sw((x0, v)) for v in bnd if abs(v - mid) > 2.0], fl[0] - 0.20, zr)
            for i, v in enumerate(side):
                if i % 2 == 0:
                    balcony(P3w, sw((x0, v)), fl[1])
            # the parking front, the principal one
            east = [((x1, v), 1.50, fl[0] + 0.55, 0, "awin", 0.30, fl[0] + 2.30) for v in side]
            east += [((x1, v), 1.30, fl[1] + 0.05, fl[1] + 2.55, "fr", 0.30) for v in side]
            P3e, se = wall((x1, y0), (x1, y1), (1, 0), zbot, zw, east)
            pe = [se((x1, v)) for v in bnd if abs(v - mid) > 2.0]
            pilasters(P3e, pe, fl[0] - 0.20, zr)
            for s_ in pe:
                lantern(P3e, s_, fl[0] + 2.55)
            sa_, sb_ = sorted((se((x1, y0)), se((x1, y1))))
            D.pbox(mb, P3e, sa_, sb_, fl[1] - 0.45, fl[1] - 0.27, -0.02, 0.0, "tile_jade")
            D.pbox(mb, P3e, sa_, sb_, fl[1] - 0.27, fl[1] - 0.15, -0.07, 0.0, "surround")
            D.pbox(mb, P3e, sa_, sb_, zr - 0.50, zr - 0.38, -0.04, 0.0, "surround")
            for i, v in enumerate(side):
                if i % 2:
                    oriel(P3e, se((x1, v)), fl[1] + 0.05, fl[1] + 2.55)
                else:
                    balcony(P3e, se((x1, v)), fl[1] + 0.05, 0.95)
            # the ends: the one facing the pavilion, the step, the far end
            for ve in ((v_in,) if k == 0 else (v_far,)):
                out = (0, -1) if ve == y0 else (0, 1)
                if wname == "main" and ve == v_far:                     # either side of the gate block
                    for a_, b_, u in (((x1, ve), (PORCH[2], ve), 12.5), ((PORCH[0], ve), (x0, ve), 1.6)):
                        P3n, sn = wall(a_, b_, out, zbot, zw, [((u, ve), 1.30, fl[f] + 0.70, fl[f] + 3.00, "tall", 0.30) for f in (0, 1)])
                        pilasters(P3n, [sn((x0 if u < 7 else x1, ve))], fl[0] - 0.20, zr)
                else:
                    P3x, sx = wall((x0, ve), (x1, ve), out, zbot, zw,
                                   [((u, ve), 1.30, fl[f] + 0.70, fl[f] + 3.00, "tall", 0.30) for u in (2.5, 7.05, 11.6) for f in (0, 1)])
                    pilasters(P3x, [sx((u, ve)) for u in (x0, x1)], fl[0] - 0.20, zr)
            if k == hi:                                                    # the step, above the lower roof
                wall((x0, v_b), (x1, v_b), (0, -up), halves[1 - hi][2] - 0.02, zw)
            # the centre blocks: the garden's with the SPA's door, the parking's with the grand entrance
            for xf, sg in ((x0, -1), (x1, 1)):
                hw, zcb = (1.95, zr + 1.60) if sg < 0 else (2.10, zr + 2.20)
                xo = xf + sg * 0.90
                cb = box(min(xf, xo), mid - hw, max(xf, xo), mid + hw)
                if sg < 0:
                    ops = [((xo, mid), 1.85, fl[0], fl[0] + 4.00, "sdoor", 0.40)]
                    ops += [((xo, mid + dv), 0.75, fl[1] + 0.70, fl[1] + 2.90, "tall", 0.30) for dv in (-0.95, 0.95)]
                else:
                    ops = [((xo, mid), 2.60, fl[0], 0, "egate", 0.60, fl[0] + 2.90)]
                    ops += [((xo, mid), 1.30, fl[1] + 1.05, fl[1] + 2.95, "msh", 0.30)]
                ops += [((xo, mid + dv), 0.20, zcb - 0.95, zcb - 0.75, "niche", 0.10) for dv in np.linspace(-hw + 0.45, hw - 0.45, 5)]
                wall((xo, mid - hw), (xo, mid + hw), (sg, 0), zbot, zcb - 0.02, ops)
                wall((xo, mid - hw), (xf, mid - hw), (0, -1), zbot, zcb - 0.02)
                wall((xo, mid + hw), (xf, mid + hw), (0, 1), zbot, zcb - 0.02)
                wall((xf, mid - hw), (xf, mid + hw), (-sg, 0), zr - 0.02, zcb - 0.02)       # over the roof
                cornice(cb, zcb)
                roof(cb, zcb, zcb + PAR)
                hard.append(cb)
                cbs.append(box(min(xf - sg * 0.31, xo), mid - hw - 0.01, max(xf - sg * 0.31, xo), mid + hw + 0.01))
                if sg > 0:                                                 # down to the trottoir
                    steps((xo, mid - 1.6, mid + 1.6), 1, fl[0], zl(xo + 1.0, mid) + TROT_DZ)
            L.prism(mb, "interior_floor", g.buffer(-0.05, join_style=2), zbot + 0.4, fl[0])
            # the roof: a dome on its drum towards the step; parasols (by the towers) or the pergola (far end)
            s_st = 1 if v_b > mid else -1
            qubba((7.05, mid + s_st * 5.0), 1.85, zr - 0.02, zr + PW + 0.20, 1.70, finial=False)
            if k == 0:
                for uu, ul in ((4.0, 5.6), (10.1, 8.5)):
                    vp = mid - s_st * 3.5
                    parasol(uu, vp, zr)
                    lounger(ul, vp - 0.9, 0.0, zr)
                    lounger(ul, vp + 0.9, 0.0, zr)
            else:
                pa, pb = sorted((mid - s_st * 2.6, mid - s_st * 6.9))
                pergola(pa, pb, zr)
            # the garden terrace: its balustrade, flights down to the garden
            pod = box(x0 - POD, y0, x0, y1)
            L.prism(mb, "villa", pod, zbot + 0.4, fl[0] - 0.03)
            L.prism(mb, "deck_stone", pod, fl[0] - 0.03, fl[0])
            hard.append(pod)
            gaps = []
            for vf in (cs[1], cs[-2]):
                zg = zl(x0 - POD - 1.0, vf)
                if fl[0] - zg > 0.20:
                    hard.append(steps((x0 - POD, vf - 1.4, vf + 1.4), -1, fl[0], zg))
                    gaps.append(box(x0 - POD - 0.5, vf - 1.4, x0 - POD + 0.5, vf + 1.4))
            bal = box(x0 - POD, y0, x0 - POD + 0.22, y1)
            if k == 0:
                bal = bal.union(box(x0 - POD, v_in - (0 if dirv > 0 else 0.22), x0, v_in + (0.22 if dirv > 0 else 0)))
            bal = bal.difference(unary_union(gaps)) if gaps else bal
            L.prism(mb, "villa", bal, fl[0], fl[0] + 0.86)
            D.coping(mb, "villa", bal.buffer(0.03, join_style=2).intersection(pod.buffer(0.03, join_style=2)), fl[0] + 0.94, 0.08)
            hard.append(g)
        # between the two terraces: a flight on the lower one, rising to the step
        zlo, zhi = halves[1 - hi][1][0], halves[hi][1][0]
        nf = max(1, int(math.ceil((zhi - zlo) / 0.16)))
        for k in range(nf):
            a_, b_ = v_b - up * (nf - k) * 0.30, v_b - up * (nf - k - 1) * 0.30
            L.prism(mb, "deck_stone", box(-POD + 0.22, min(a_, b_), 0.0, max(a_, b_)), zbot + 0.4, zlo + (k + 1) * (zhi - zlo) / nf)
        # the roofs: no parapet against the step, the towers, the centre blocks or the gate block; the horns at
        # the free corners
        cbc = unary_union(cbs)
        tw = unary_union(towers)
        for k, (g, fl, zr) in enumerate(halves):
            x0, y0, x1, y1 = g.bounds
            cut_c, cut_r = cbc.buffer(0.01), cbc
            if k == 0:
                cut_c, cut_r = cut_c.union(tw.buffer(0.02)), cut_r.union(tw.buffer(0.01))
            if k != hi:
                cut_c = cut_c.union(box(-1.0, min(v_b, v_b + up), 15.1, max(v_b, v_b + up)))
                cut_r = cut_r.union(box(0.30, v_b - 0.31, x1 - 0.30, v_b + 0.01) if up > 0 else box(0.30, v_b - 0.01, x1 - 0.30, v_b + 0.31))
            if wname == "main" and k == 1:
                cut_c, cut_r = cut_c.union(porch.buffer(0.02)), cut_r.union(porch.buffer(0.01))
            cornice(g, zr, cut_c)
            roof(g, zr, zr + PW, cut_r, horns=False)
            corners = []
            for i in (0, 1):
                for j in (0, 1):
                    vc = y0 if j == 0 else y1
                    if k == 0 and abs(vc - v_in) < 1e-6:
                        continue                                           # the towers there
                    if k != hi and abs(vc - v_b) < 1e-6:
                        continue                                           # under the step
                    corners.append((i, j))
            horns_at(g, zr + PW, corners)
        zc = zr_in + 1.50
        for t in towers:
            box_walls(t, zr_in - 0.02, zc - 0.02)
            cornice(t, zc)
            roof(t, zc, zc + PAR)
            qubba(t.centroid.coords[0], 1.45, zc - 0.02, zc + PAR + 0.15, 1.45)

    # the gate block on the Voie Publique: proud of the main building's north front, rising to +10.40, the arch
    # in its alfiz, six niches over it, steps down inside to the trottoir
    halves_m, zbotA = wings["main"]
    fS, fN, zrN = halves_m[0][1], halves_m[1][1], halves_m[1][2]
    px0, py0, px1, py1 = PORCH
    zpk = zrN + 2.60
    pc = (px0 + px1) / 2
    ops = [((pc, py1), 3.60, fN[0], 0, "gate", 1.60, fN[0] + 3.40)]
    ops += [((u, py1), 0.22, zpk - 1.10, zpk - 0.88, "niche", 0.10) for u in np.linspace(px0 + 1.2, px1 - 1.2, 6)]
    wall((px1, py1), (px0, py1), (0, 1), zbotA, zpk - 0.02, ops)
    for xs, out in ((px0, (-1, 0)), (px1, (1, 0))):
        wall((xs, A_N[3]), (xs, py1), out, zbotA, zrN - 0.02)
        wall((xs, py0), (xs, py1), out, zrN - 0.02, zpk - 0.02)
    wall((px0, py0), (px1, py0), (0, -1), zrN - 0.02, zpk - 0.02)
    cornice(porch, zpk)
    roof(porch, zpk, zpk + PAR)
    L.prism(mb, "deck_stone", porch, zbotA + 0.4, fN[0])
    zst = zl(pc, py1) + TROT_DZ
    for k in range(max(0, int(round((zst + 0.02 - fN[0]) / 0.15)))):
        L.prism(mb, "deck_stone", box(pc - 2.2, py1 - 0.45 - 0.30 * k, pc + 2.2, py1 - (0.45 + 0.30 * (k - 1) if k else 0.0)),
                fN[0], zst + 0.02 - 0.15 * k)
    hard.append(porch)

    # =========================================================================================================
    # the gate pavilion on the crossing (client 24-10, second review: "bdel adiya bchi7aja li 7ssn"): a domed qubba
    # standing over both buildings, its monumental pointed horseshoe arches east (from the parking) and west (onto
    # the arm's head) in taupe alfiz framed in green zellige under a row of niches, blind zellige arches north and
    # south, four corner turrets with their small domes, the high drum with its zellige band and arched lights,
    # the dome with its bronze finial, the fountain inside
    zX = zl(7.05, -4.0) + 0.15
    pv = box(*PAV)
    qx0, qy0, qx1, qy1 = PAV
    qc = ((qx0 + qx1) / 2, (qy0 + qy1) / 2)
    zpw = zX + 9.00
    t_ = 0.60
    aw, azs = 4.00, zX + 4.20
    nz = zX + 7.75
    nis = np.linspace(-2.4, 2.4, 7)
    box_walls(pv, zX - 0.6, zpw - 0.02,
              {"W": [((qx0, qc[1]), aw, zX, 0, "open", t_, azs)] + [((qx0, qc[1] + d_), 0.22, nz, nz + 0.30, "niche", 0.10) for d_ in nis],
               "E": [((qx1, qc[1]), aw, zX, 0, "open", t_, azs)] + [((qx1, qc[1] + d_), 0.22, nz, nz + 0.30, "niche", 0.10) for d_ in nis],
               "N": [((qc[0], qy1), aw, zX, 0, "blind", 0.14, azs)] + [((qc[0] + d_, qy1), 0.22, nz, nz + 0.30, "niche", 0.10) for d_ in nis],
               "S": [((qc[0], qy0), aw, zX, 0, "blind", 0.14, azs)] + [((qc[0] + d_, qy0), 0.22, nz, nz + 0.30, "niche", 0.10) for d_ in nis]})
    for xs, sgn in ((qx0, 1), (qx1, -1)):                     # inside faces, the arches' soffits, alfiz and zellige
        wall((xs + sgn * t_, qy0 + t_), (xs + sgn * t_, qy1 - t_), (sgn, 0), zX - 0.6, zpw - 0.02,
             [((xs + sgn * t_, qc[1]), aw, zX, 0, "open", 0.0, azs)])
        h = arch(qc[1], aw, azs, zX)
        soffit(h, zX, lambda s, z, k, xs=xs, sgn=sgn: (xs + sgn * t_ * k, s, z))
        al = box(qc[1] - 2.70, zX, qc[1] + 2.70, azs + 2.75)
        D.ext(mb, "surround", al.difference(h), lambda a, b, w, xs=xs, sgn=sgn: (xs - sgn * w, a, b), 0.0, 0.05)
        D.ext(mb, "tile_jade", box(qc[1] - 3.00, zX, qc[1] + 3.00, azs + 3.05).difference(al),
              lambda a, b, w, xs=xs, sgn=sgn: (xs - sgn * w, a, b), 0.0, 0.07)
    for ys, sgn in ((qy0, 1), (qy1, -1)):
        wall((qx0 + t_, ys + sgn * t_), (qx1 - t_, ys + sgn * t_), (0, sgn), zX - 0.6, zpw - 0.02)
    L.prism(mb, "villa", pv.buffer(-0.01, join_style=2), zpw - 0.20, zpw - 0.02, bottom=True)
    turrets = [box(qx0, qy0, qx0 + 1.2, qy0 + 1.2), box(qx1 - 1.2, qy0, qx1, qy0 + 1.2),
               box(qx0, qy1 - 1.2, qx0 + 1.2, qy1), box(qx1 - 1.2, qy1 - 1.2, qx1, qy1)]
    tu = unary_union(turrets)
    cornice(pv, zpw, tu.buffer(0.02))
    roof(pv, zpw, zpw + PAR, tu.buffer(0.01), horns=False)
    zt_ = zpw + 1.90
    for t in turrets:                                          # the corner turrets and their small domes
        box_walls(t, zpw - 0.02, zt_ - 0.02)
        cornice(t, zt_)
        L.prism(mb, "terrace", t.buffer(-0.005, join_style=2), zt_ - 0.02, zt_, sides=False)
        c_ = t.centroid.coords[0]
        qubba(c_, 0.48, zt_ - 0.02, zt_ + 0.45, 0.62, finial=False)
        L.prism(mb, "bronze", Point(*c_).buffer(0.035, 6), zt_ + 1.02, zt_ + 1.40)
        L.prism(mb, "bronze", Point(*c_).buffer(0.08, 10), zt_ + 1.12, zt_ + 1.26)
    rd = 2.50
    zd = zpw + 1.90
    L.prism(mb, "villa", Point(*qc).buffer(rd, 48), zpw - 0.02, zd)
    L.prism(mb, "tile_jade", Point(*qc).buffer(rd + 0.03, 48).difference(Point(*qc).buffer(rd - 0.2, 48)), zd - 0.55, zd - 0.30)
    L.prism(mb, "ledge", Point(*qc).buffer(rd + 0.10, 48).difference(Point(*qc).buffer(rd - 0.2, 48)), zd - 0.10, zd, bottom=True)
    for k in range(8):                                         # the drum's arched lights
        a = 2 * math.pi * (k + 0.5) / 8
        for r_, hw_, z0_, z1_, mat in ((rd + 0.010, 0.34, zpw + 0.45, zpw + 1.30, "surround"), (rd + 0.018, 0.24, zpw + 0.55, zpw + 1.20, "glass")):
            da = hw_ / rd
            p0 = (qc[0] + r_ * math.cos(a - da), qc[1] + r_ * math.sin(a - da))
            p1 = (qc[0] + r_ * math.cos(a + da), qc[1] + r_ * math.sin(a + da))
            top = (qc[0] + r_ * math.cos(a), qc[1] + r_ * math.sin(a), z1_ + hw_ * 0.9)
            mb.poly(mat, [(p0[0], p0[1], z0_), (p1[0], p1[1], z0_), (p1[0], p1[1], z1_), top, (p0[0], p0[1], z1_)])
    dome(qc, rd, zd, rd * 1.25)
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
    hs = wings["suites"][0]
    print(f"  T3 hotel: main building floors {fS[0]:.2f} / {fN[0]:.2f}, suites {hs[0][1][0]:.2f} / {hs[1][1][0]:.2f}, pavilion {zX:.2f}, "
          f"basins {zN:.2f} / {zC:.2f} / {zS:.2f}, {len(plants)} plants")
    return obs, plants, (o, U, V)
