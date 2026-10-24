"""
13_tranche2 — Tranche 2: the villas type B of the plan de masse 31-05-13 (client 21-10: "zid ghir tranche
2", every type B villa of the blocks circled on the plan), built into the scene of Tranche 1 by
05_build_scene after Tranche 1's planting. Everything here lives in collections, objects and materials of
its own (T2_...); Tranche 1 is not touched.

Data: data/t2_site.json (11_extract_t2): 33 villas on their gardens as the plan draws them, the streets
and pavements read from the plan's lines (the Voie Publique, the street along Tranche 1 and the south road
the client marked in yellow, 21-10), the parking bays and the three buildings on the parking strip
('Centre d'entretien' twice and 'Office'). Model: 12_villa_b (villa type B with its pool; the compact one
where the plan's plot is short).

Levels: the blocks are graded on the plane of Tranche 1 (the 2013 contours fit it within 1.5 m there), the
type C block and its streets out to the boundary too (client 23-10); away from them the streets follow the
site's own ground (the terrain's height function H of 05, which blends the plane into the natural ground
over 25 m). Streets at H, pavements 0.15 m over it with a concrete kerb; each villa's pad at the
height of its centre, its garden flat at the pad (+0.17, lawn 3 cm under the terraces), held by its walls
where the ground falls away. Garden walls 1.80 m in the render of the villas with their trim (at least
1.20 m over the lawn); on the villa's street side a low stone-clad wall with its beige coping, the gate
pillars and timber gate of the villas of Tranche 1 and a paved path to the door. Planting: olive trees and
date palms in the gardens, shrubs behind the low walls, Washingtonia palms in pits along the streets.
"""
import json
import math
import os
import random

import bpy
import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
T2 = json.load(open(os.path.join(ROOT, "data", "t2_site.json")))
RNG = random.Random(20261021)
LAWN_DZ = 0.17           # lawn over the pad (the terraces at +0.195)
LAWN_C = 0.07            # type C: lawn over the natural ground level of its model (pool coping +0.10, terraces +0.195)
PAVE_DZ = 0.15           # pavements over the street
W_GARDEN, W_FRONT = 1.80, 0.70
GATE = (5.62, 7.70)      # pedestrian gate on the front, drawing x (the plan's 'Accès', between kitchen and stair)
Z_PATH = 0.025           # the path's top over the lawn (the terraces' level)
BLD_H = 3.40             # the parking strip's buildings: walls, and the pyramid roof the plan draws over them
ROOF_H = 1.90


def P(p):
    return Polygon(p["ext"], p["holes"]).buffer(0)


def PL(lst):
    return unary_union([P(p) for p in lst]) if lst else Polygon()


def envelope():
    """Tranche 2's ground: the site's empty land is cut away there (05 build_terrain)."""
    return P(T2["env"])


def blocks():
    """The blocks of villas, graded on the plane: the empty land blends into them (05 build_terrain). The
    SPA's cell beside the northern block too, and the type C block with its streets out to the boundary
    (client 23-10: on the natural ground its streets lay up to 9 m under the gardens and their gates)."""
    extra = ([P(T2["spa"]["cell"])] if "spa" in T2 else []) + ([P(T2["graded_c"])] if "graded_c" in T2 else [])
    return unary_union([P(T2["blocks"])] + extra).buffer(0)


def spa_frame():
    """The SPA's local frame (15_spa): origin, u (across), v (along, to the entrance on the Voie Publique), W, Lg."""
    sp = P(T2["spa"]["plot"])
    rr = list(sp.minimum_rotated_rectangle.exterior.coords)
    e1, e2 = np.array(rr[1]) - np.array(rr[0]), np.array(rr[2]) - np.array(rr[1])
    el, es = (e1, e2) if np.linalg.norm(e1) >= np.linalg.norm(e2) else (e2, e1)
    v = el / np.linalg.norm(el)
    v = v if v[1] > 0 else -v                                 # its north end, on the Voie Publique
    u = np.array([v[1], -v[0]])
    W, Lg = float(np.linalg.norm(es)), float(np.linalg.norm(el))
    c = np.array(sp.minimum_rotated_rectangle.centroid.coords[0])
    return c - u * W / 2 - v * Lg / 2, u, v, W, Lg


def t1_trim():
    """Tranche 1's ground under the street along it, south of where the street's east kerb leaves Tranche 1's
    limit (client 22-10): not built by 05, the street is built there by Tranche 2."""
    return PL(T2.get("t1_trim", []))


def mats(M):
    """Tranche 2's ground materials: copies of Tranche 1's under their own names, to be finished apart in D5."""
    for k, src, suffix in (("t2_road", "asphalt", ""), ("t2_parking", "asphalt", "_Parking"),
                           ("t2_path", "pave_beige", "_Paths"), ("t2_kerb", "kerb", ""), ("t2_lawn", "lawn", "_Gardens"),
                           ("t2_verge", "lawn", "_Verges")):
        name = f"T2_{M[src].name}{suffix}"                    # T2_<Tranche 1's material>: 08 exports it with that one's texture
        M[k] = M[src].copy()
        M[k].name = name
    # client 23-10: the pavements (trottoirs) apart from the roads, in their own material, grey pavers, to be
    # finished on their own in D5 ("fslom bach nt7akm fihum maykunuch dakhlin m3a road")
    M["t2_pave"] = L.img_mat("T27_Trottoirs_Grey", "sidewalk", 0.8, 0.35)


class Villa:
    def __init__(self, v, t="B", W=12.20):
        self.id, self.v, self.t, self.W = v["id"], v, t, W
        self.o, self.rot, self.m, self.c = np.array(v["origin"]), v["rot_deg"], v["mirror"], v.get("compact", False)
        a = math.radians(self.rot)
        self.ex, self.ey = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
        self.garden = P(v["garden"])
        self.gate = v["gate"]
        xs = [self.local(q) for q in self.garden.exterior.coords]
        self.gx0, self.gx1 = min(x for x, _ in xs), max(x for x, _ in xs)
        self.gy0, self.gy1 = min(y for _, y in xs), max(y for _, y in xs)

    def mx(self, x):
        return self.W - x if self.m else x

    def w(self, x, y):
        """drawing local (before mirroring) -> world"""
        return tuple(self.o + self.ex * self.mx(x) + self.ey * y)

    def fw(self, x, y):
        """frame local (as placed, not mirrored) -> world"""
        return tuple(self.o + self.ex * x + self.ey * y)

    def g(self, geom):
        """a polygon in drawing coordinates -> world (mirrored with the villa)"""
        if self.m:
            geom = affinity.scale(geom, -1.0, 1.0, origin=(self.W / 2.0, 0.0))
        return self.f(geom)

    def f(self, geom):
        """a polygon in frame coordinates -> world"""
        return affinity.translate(affinity.rotate(geom, self.rot, origin=(0, 0)), *self.o)

    def local(self, p):
        d = np.array(p) - self.o
        return float(np.dot(d, self.ex)), float(np.dot(d, self.ey))

    def edge(self, axis, out, t):
        """the garden's fence across frame x = t (axis 'y') or y = t (axis 'x'), on the side out (+1 or -1):
        where the gate goes, the fence being askew to the villa where the street is (client 22-10)"""
        if axis == "y":
            ln = LineString([self.fw(t, self.gy0 - 1.0), self.fw(t, self.gy1 + 1.0)])
        else:
            ln = LineString([self.fw(self.gx0 - 1.0, t), self.fw(self.gx1 + 1.0, t)])
        x = ln.intersection(self.garden)
        vals = [self.local(q)[1 if axis == "y" else 0] for g in getattr(x, "geoms", [x]) for q in getattr(g, "coords", [])]
        if not vals:
            return (self.gy1 if out > 0 else self.gy0) if axis == "y" else (self.gx1 if out > 0 else self.gx0)
        return max(vals) if out > 0 else min(vals)



def build(M, B, srcv, H):
    """B: the 05_build_scene module (collections, load), srcv: its plant sources, H: its terrain height
    function (xy array -> z). Returns the T2 cameras."""
    hz = lambda x, y: float(H(np.array([[x, y]]))[0])
    VB = B.load("12_villa_b.py")
    VC = B.load("14_villa_c.py")
    mats(M)
    cols = {k: C.collection(k) for k in ("T2_01_GROUND", "T2_02_VILLAS", "T2_03_LANDSCAPE", "T2_04_TREES_PALMS")}
    srcc = C.collection("SRC")
    src = {}
    for compact in (False, True):
        sfx = "_COMPACT" if compact else ""
        src[(False, compact)] = VB.build(M, srcc, "SRC_T2_VILLA_B" + sfx, compact=compact)
        src[(True, compact)] = VB.mirrored(src[(False, compact)], "SRC_T2_VILLA_B" + sfx + "_MIRRORED")
    hard = {c: VB.ground(c)[2] for c in (False, True)}
    deck = {c: VB.ground(c)[1] for c in (False, True)}
    src_c = {False: VC.build(M, srcc, "SRC_T2_VILLA_C")}
    src_c[True] = VC.mirrored(src_c[False], "SRC_T2_VILLA_C_MIRRORED")
    hard_of = lambda v: v.g(hard[v.c]) if v.t == "B" else v.g(VC.HARD)

    vs = [Villa(v) for v in T2["villas"]] + [Villa(v, "C", VC.PLOT_W) for v in T2.get("villas_c", [])]
    gardens = unary_union([v.garden for v in vs])
    roads, pave, parking = PL(T2["roads"]), PL(T2["pavements"]), PL(T2["parking"])
    greens = PL(T2.get("greens", []))
    verges = PL(T2.get("verges", []))
    fix = globals().get("STREET_FIX")                         # client 24-10: by the hotel, street (19_tranche3)
    if fix is not None:
        roads = roads.union(unary_union([pave, verges]).intersection(fix))
        pave, verges = pave.difference(fix), verges.difference(fix)
    st = T2.get("stair")
    stair = PL(st["poly"]) if st else Polygon()
    bays = [P(b) for b in T2["bays"]]
    buildings = [(b["name"], P(b["poly"])) for b in T2["buildings"]]
    public = unary_union([roads, pave, parking, verges, stair])

    # ---- villas --------------------------------------------------------------------------------
    for v in vs:
        v.pad = hz(*(v.w(6.10, 12.0) if v.t == "B" else v.w(*VC.HOUSE_C)))
        v.zl = v.pad + (LAWN_DZ if v.t == "B" else LAWN_C)
        ob = bpy.data.objects.new("T2_VILLA_" + v.id.replace("-", ""), (src[(v.m, v.c)] if v.t == "B" else src_c[v.m]).data)
        ob.location = (*v.o, v.pad)
        ob.rotation_euler = (0, 0, math.radians(v.rot))
        cols["T2_02_VILLAS"].objects.link(ob)
    print(f"  T2: {sum(v.t == 'B' for v in vs)} villas type B, {sum(v.t == 'C' for v in vs)} type C ({sum(v.m for v in vs)} mirrored, {sum(v.c for v in vs)} compact); gates "
          f"{sum(v.gate == 'front' for v in vs)} on the front, {sum(v.gate != 'front' for v in vs)} on the side")

    def level(x, y, pad=0.6):
        """the highest garden level within pad of (x, y), or None"""
        p = Point(x, y)
        zs = [v.zl for v in vs if v.garden.distance(p) <= pad]
        return max(zs) if zs else None

    # ---- the gates: (villa, axis, c, a, b, kind) in frame coordinates: a wall along x at y = c, or along y
    # at x = c. The side the extraction chose first; where the street is not right outside it (a building,
    # a neighbour's garden), the next of: the front (beside the front terrace too), the terrace side, the
    # kitchen side, and last the rear, by the pool (the villas the plan draws back to front with no street
    # in front, whose rear is on the street)
    blocked = unary_union([g for _, g in buildings] + [v.garden for v in vs])
    outside_ok = lambda p: public.contains(Point(p)) and not blocked.contains(Point(p))

    def gate_options(v):
        if v.t == "C":                                        # type C: on the front, on the portal's axis; or on
            for side in [v.gate] + [g for g in ("front", "right", "left") if g != v.gate]:   # a side, past the stair
                if side == "front":
                    a, b = sorted((v.mx(VC.PORTAL_X - 1.0), v.mx(VC.PORTAL_X + 1.0)))
                    c = v.edge("y", 1, (a + b) / 2)
                    yield (v, "y", c, a, b, "c_front"), v.fw((a + b) / 2, c + 1.2)
                else:
                    y1 = max(14.4, min(v.gy1 - 0.5, 18.4))
                    c = v.edge("x", 1 if side == "right" else -1, y1 - 1.0)
                    yield (v, "x", c, y1 - 2.0, y1, "c_side"), v.fw(c + (1.2 if side == "right" else -1.2), y1 - 1.0)
            return
        terr = "right" if not v.m else "left"
        kit = "left" if terr == "right" else "right"
        order = [v.gate] + [g for g in ("front", terr, kit, "rear") if g != v.gate]
        for side in order:
            if side == "front":
                for ga, gb in (GATE, (8.60, 10.60)):
                    a, b = sorted((v.mx(ga), v.mx(gb)))
                    c = v.edge("y", 1, (a + b) / 2)
                    yield (v, "y", c, a, b, "front" if ga == GATE[0] else "front_terrace"), v.fw((a + b) / 2, c + 1.2)
            elif side == "rear":
                a, b = sorted((v.mx(9.30), v.mx(11.30)))
                c = v.edge("y", -1, (a + b) / 2)
                yield (v, "y", c, a, b, "rear"), v.fw((a + b) / 2, c - 1.2)
            else:
                kind = "terrace" if side == terr else "kitchen"
                y0, y1 = (17.30, 19.30) if kind == "terrace" else (16.20, 17.80)
                c = v.edge("x", 1 if side == "right" else -1, (y0 + y1) / 2)
                yield (v, "x", c, y0, y1, kind), v.fw(c + (1.2 if side == "right" else -1.2), (y0 + y1) / 2)

    gates = []
    for v in vs:
        opts = list(gate_options(v))
        ok = [g for g, p in opts if outside_ok(p)]
        if not ok:
            print("  T2: WARNING no street outside any gate of", v.id)
        gates.append(ok[0] if ok else opts[0][0])
        if gates[-1][5] == "rear":
            print("  T2: rear gate (no street in front or beside):", v.id)
    kinds = [g[5] for g in gates]
    print("  T2: gates:", {k: kinds.count(k) for k in sorted(set(kinds))})

    def gate_box(axis, c, a, b, d=0.6):
        return box(a, c - d, b, c + d) if axis == "y" else box(c - d, a, c + d, b)

    # ---- walls: garden walls on the gardens' outlines, the low wall on each villa's street side -----
    ring = unary_union([v.garden.boundary.buffer(0.10, cap_style=2, join_style=2) for v in vs])
    houses = unary_union([v.g(VB.RDC.union(box(1.03, 18.11, 5.47, 20.11))) if v.t == "B" else v.g(VC.FOOT) for v in vs])
    low_zone, openings = [], []
    for v, axis, c, a, b, kind in gates:
        if kind != "rear":                                    # the rear stays a high wall round the pool
            # the low wall: the stretches of the fence on the gate's side, square to it or askew (up to 35
            # degrees) where the street runs askew to the villa, the house's front half only on a side gate
            mid_ = (v.gy0 + v.gy1) / 2 if axis == "y" else (v.gx0 + v.gx1) / 2
            dvec = (v.ey if axis == "y" else v.ex) * (1.0 if c >= mid_ else -1.0)
            ring_ = orient(v.garden, 1.0).exterior.coords
            for p0, p1 in zip(ring_[:-1], ring_[1:]):
                e = np.array(p1) - np.array(p0)
                if np.linalg.norm(e) < 0.05:
                    continue
                nrm = np.array([e[1], -e[0]]) / np.linalg.norm(e)
                if float(np.dot(nrm, dvec)) > 0.82 and (axis == "y" or v.local(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2))[1] > (10.0 if v.t == "B" else 12.0)):
                    low_zone.append(LineString([p0, p1]).buffer(0.60, cap_style=2, join_style=2))
        openings.append(v.f(gate_box(axis, c, a, b)))
    lz = unary_union(low_zone).intersection(public.buffer(0.4))
    low = ring.intersection(lz).difference(houses).difference(unary_union(openings))
    high = ring.difference(lz).difference(houses).difference(unary_union(openings))
    # client 24-10 ("la pierre ... le côté escalier"): the garden walls along the stair between the blocks and
    # along the street between the two rows of villas type C are clad in stone as the street walls, with the
    # same coping
    gc_ = [v.garden for v in vs if v.t == "C"]
    lanes = [stair]
    if gc_:
        cs_ = unary_union(gc_).convex_hull.difference(unary_union(gc_))
        lanes += [q for q in L.as_polys(cs_) if q.area > 50.0]
    stone_zone = unary_union(lanes).buffer(0.45, join_style=2)
    high_s = high.intersection(stone_zone)
    high_r = high.difference(high_s)
    mb = C.MeshBuilder()
    zg = lambda x, y: max(hz(x, y), (level(x, y) or -1e9) - (W_GARDEN - 1.20))
    for g in L.as_polys(high_r):
        if g.area < 0.02:
            continue
        L.prism(mb, "render", g, -1.60, W_GARDEN, zf=zg)
        L.prism(mb, "trim", g.buffer(0.03, join_style=2).difference(houses).difference(high_s), W_GARDEN, W_GARDEN + 0.05, zf=zg)
    for g in L.as_polys(high_s):
        if g.area < 0.02:
            continue
        L.prism(mb, "cladding", g, -1.60, W_GARDEN, zf=zg)
        L.prism(mb, "coping_beige", g.buffer(0.04, join_style=2).difference(houses), W_GARDEN, W_GARDEN + 0.08, zf=zg)
    mb.build("T2_WALLS_GARDENS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    zf_low = lambda x, y: max(hz(x, y) + PAVE_DZ, level(x, y, 0.4) or -1e9)
    for g in L.as_polys(low):
        if g.area < 0.02:
            continue
        L.prism(mb, "cladding", g, -1.20, W_FRONT, zf=zf_low)
        L.prism(mb, "coping_beige", g.buffer(0.04, join_style=2).intersection(low.buffer(0.04, join_style=2)), W_FRONT, W_FRONT + 0.08, zf=zf_low)
    # gate pillars and gates (as Tranche 1's villas): stone-clad pillars with their coping, timber slats
    for v, axis, c, a, b, kind in gates:
        mid = v.fw(*(((a + b) / 2, c) if axis == "y" else (c, (a + b) / 2)))
        z = max(hz(*mid) + PAVE_DZ, v.zl)
        flat = lambda x, y, z=z: z
        ph, gh = (1.38, 1.30) if kind != "rear" else (W_GARDEN + 0.15, W_GARDEN - 0.10)   # in a high wall: full height
        for p0, p1 in ((a - 0.40, a), (b, b + 0.40)):
            g = v.f(gate_box(axis, c, p0, p1, 0.20))
            L.prism(mb, "cladding", g, -1.20, ph, zf=flat)
            L.prism(mb, "coping_beige", g.buffer(0.03, join_style=2), ph, ph + 0.08, zf=flat)
        n = max(6, int((b - a) / 0.11))
        for k in range(n):
            t = a + 0.03 + (b - a - 0.13) * k / (n - 1)
            L.prism(mb, "door_wood", v.f(gate_box(axis, c, t, t + 0.07, 0.02)), 0.12, gh, zf=flat)
        for zz in (0.30, gh - 0.20):
            L.prism(mb, "door_wood", v.f(gate_box(axis, c, a + 0.02, b - 0.02, 0.02)), zz, zz + 0.08, zf=flat)
    mb.build("T2_WALLS_FRONT_GATES", cols["T2_01_GROUND"], M)
    print(f"  T2: garden walls {high.area:.0f} m2 of plan ({high_s.area:.0f} in stone by the stair and the type C street), "
          f"low street walls {low.area:.0f} m2, {len(gates)} gates")

    # ---- gardens: lawn, path from the gate to the door, slab under the house -----------------------
    walls = unary_union([high, low])
    mb_l, mb_p, mb_s = C.MeshBuilder(), C.MeshBuilder(), C.MeshBuilder()
    paths = []
    for (v, axis, c, a, b, kind) in gates:
        hd = hard_of(v)
        if kind == "c_front":                                 # type C: straight to the portal's step
            path = v.f(box(a, VC.PLOT_D - 0.40, b, c + 1.0))
        elif kind == "c_side":                                # along the front of the house to the portal
            px_ = v.mx(VC.PORTAL_X)
            path = v.f(box(min(c, px_) - 0.6, a, max(c, px_) + 0.6, b)).union(v.f(box(px_ - 0.87, 16.8, px_ + 0.87, max(b, VC.PLOT_D + 0.1))))
        elif kind == "front":
            path = v.f(box(a, 18.05, b, c + 1.0))
        elif kind == "front_terrace":                         # onto the front terrace
            path = v.f(box(a, 19.20, b, c + 1.0))
        elif kind == "rear":                                  # past the pool to the rear terrace
            path = v.f(box(a, c - 1.0, b, 6.00))
        elif kind == "terrace":                               # along the front to the front terrace
            x_h = 12.22 if not v.m else -0.02
            path = v.f(box(min(c, x_h) - 0.6, a, max(c, x_h) + 0.6, b))
        else:                                                 # to the kitchen's side door, and on along the house to the garden
            x_h = 1.03 if not v.m else 11.17
            path = v.f(box(min(c, x_h) - 0.6, a, max(c, x_h) + 0.6, b))
            xw0, xw1 = (x_h - 1.10, x_h) if not v.m else (x_h, x_h + 1.10)
            path = path.union(v.f(box(xw0, 7.40, xw1, b)))
        path = path.intersection(v.garden).difference(hd)
        paths.append(path)
        low_z = min(hz(x, y) for x, y in v.garden.exterior.coords) - 0.65
        lawn = v.garden.difference(hd).difference(path).difference(walls)
        flat = lambda x, y, z=v.zl: z
        L.prism(mb_l, "t2_lawn", lawn, low_z - v.zl, 0.0, zf=flat)
        L.prism(mb_p, "t2_path", path.difference(walls), low_z - v.zl, Z_PATH, zf=flat)
        slab = v.g(VB.RDC.buffer(-0.05, join_style=2)) if v.t == "B" else v.g(VC.HOUSE.buffer(-0.05, join_style=2))
        L.prism(mb_s, "interior_floor", slab, low_z - v.zl, 0.02 if v.t == "B" else VC.Z_FL - LAWN_C - 0.01, zf=flat)
    mb_l.build("T2_GROUND_GARDENS_LAWN", cols["T2_01_GROUND"], M)
    mb_p.build("T2_GROUND_ENTRANCE_PATHS", cols["T2_01_GROUND"], M)
    mb_s.build("T2_GROUND_HOUSE_SLABS", cols["T2_01_GROUND"], M)

    # ---- streets, pavements, kerbs, parking --------------------------------------------------------
    roads = roads.difference(gardens)
    # a paved crossing over the planted strip in front of each gate, as wide as the gate and its pillars
    n_cross = 0
    for v, axis, c, a, b, kind in gates:
        sgn = 1.0 if c == (v.gy1 if axis == "y" else v.gx1) else -1.0
        d0, d1 = sorted((c, c + sgn * 8.0))
        g = v.f(box(a - 0.40, d0, b + 0.40, d1) if axis == "y" else box(d0, a - 0.40, d1, b + 0.40))
        g = g.intersection(verges)
        if g.area > 0.2:
            pave, verges = pave.union(g), verges.difference(g)
            n_cross += 1
    pave = pave.difference(gardens)
    verges = verges.difference(gardens)
    kerb = pave.intersection(roads.union(parking).buffer(0.16, join_style=2))
    kerb = kerb.union(verges.intersection(roads.union(parking).buffer(0.16, join_style=2)))
    verges = verges.difference(kerb)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_road", roads, -0.65, 0.0, zf=hz)
    mb.build("T2_GROUND_ROADS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_pave", pave.difference(kerb), -0.65, PAVE_DZ, zf=hz)
    mb.build("T2_GROUND_PAVEMENTS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_kerb", kerb, -0.65, PAVE_DZ + 0.005, zf=hz)
    mb.build("T2_GROUND_KERBS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_verge", greens, -0.65, 0.12, zf=hz)
    mb.build("T2_GROUND_LAWN_BY_TRANCHE_1", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_verge", verges, -0.65, 0.12, zf=hz)
    mb.build("T2_GROUND_VERGES", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_parking", parking, -0.65, 0.0, zf=hz)
    mb.build("T2_GROUND_PARKING", cols["T2_01_GROUND"], M)
    # the bays: one thin white line (6 cm) between two bays and at the ends of the rows, none across their
    # mouths (client 22-10); where two bays share a side it is painted once
    mb = C.MeshBuilder()
    lines = []
    for b in bays:
        q = list(b.exterior.coords)[:4]
        for p0, p1 in sorted(((q[i], q[(i + 1) % 4]) for i in range(4)), key=lambda ab: -math.dist(*ab))[:2]:
            ln = LineString([p0, p1])
            if any(ln.centroid.distance(o) < 0.45 or o.centroid.distance(ln) < 0.45 for o in lines):
                continue                                      # a side shared with the next bay (staggered rows too)
            lines.append(ln)
    for ln in lines:
        L.prism(mb, "paint", ln.buffer(0.03, cap_style=2), 0.004, 0.006, zf=hz, sides=False)
    mb.build("T2_ROAD_PAINT_PARKING", cols["T2_01_GROUND"], M)
    print(f"  T2: streets {roads.area:.0f} m2, pavements {pave.area:.0f} m2, verges and planted strips {verges.area:.0f} m2 "
          f"({n_cross} crossings at the gates), parking {parking.area:.0f} m2 ({len(bays)} bays)")

    # ---- the stair between the two blocks (client 22-10): level treads in the beige pavers, fence to fence,
    # each riser (about 15 cm) with a stone nosing; two square fountains on treads of their own, a raised
    # stone rim, tiled basin and a bronze spout on a stone pedestal ----------------------------------------
    if st:
        A, Bv = np.array(st["axis"][0]), np.array(st["axis"][-1])
        Lst = float(np.linalg.norm(Bv - A))
        dv = (Bv - A) / Lst
        nv = np.array([-dv[1], dv[0]])
        zA, zB = hz(*A), hz(*Bv)
        n_r = max(1, int(round(abs(zA - zB) / 0.15)))
        rise = (zA - zB) / n_r
        Lt = Lst / (n_r + 1)
        slab = lambda t0, t1: Polygon([tuple(A + dv * t0 + nv * 30), tuple(A + dv * t1 + nv * 30),
                                       tuple(A + dv * t1 - nv * 30), tuple(A + dv * t0 - nv * 30)])
        mb = C.MeshBuilder()
        for k in range(n_r + 1):
            t0, t1 = (k * Lt if k else -10.0), ((k + 1) * Lt if k < n_r else Lst + 10.0)
            z = zA - k * rise
            g = stair.intersection(slab(t0, t1))
            if g.is_empty:
                continue
            L.prism(mb, "t2_path", g, -0.90, 0.0, zf=lambda x, y, z=z: z)        # the stair's treads stay beige
            if k < n_r:
                L.prism(mb, "coping_beige", stair.intersection(slab(t1 - 0.30, t1)), -0.05, 0.006, zf=lambda x, y, z=z: z, sides=False)
        for fx, fy in st["fountains"]:
            t = float(np.dot(np.array([fx, fy]) - A, dv))
            k = min(n_r, max(0, int(t // Lt)))
            c = A + dv * (k + 0.5) * Lt + nv * float(np.dot(np.array([fx, fy]) - A, nv))
            z = zA - k * rise
            flat = lambda x, y, z=z: z
            sq = affinity.translate(affinity.rotate(box(-1.2, -1.2, 1.2, 1.2), math.degrees(math.atan2(dv[1], dv[0])), origin=(0, 0)), *c)
            L.prism(mb, "coping", sq.buffer(0.30, join_style=2).difference(sq), -0.05, 0.45, zf=flat)
            L.prism(mb, "pool_tile", sq, 0.0, 0.03, zf=flat, sides=False)
            L.prism(mb, "pool_tile", sq.difference(sq.buffer(-0.02, join_style=2)), 0.0, 0.40, zf=flat)
            L.prism(mb, "pool_water", sq.buffer(-0.02, join_style=2), 0.30, 0.32, zf=flat, sides=False)
            ped = Point(*c).buffer(0.22, 4).envelope
            L.prism(mb, "coping", ped, 0.0, 0.70, zf=flat)
            L.prism(mb, "coping", ped.buffer(0.08, join_style=2), 0.70, 0.78, zf=flat)
            L.prism(mb, "bronze", Point(*c).buffer(0.05, 8), 0.78, 1.05, zf=flat)
        mb.build("T2_STAIR_BETWEEN_BLOCKS", cols["T2_01_GROUND"], M)
        print(f"  T2: stair between the blocks: {Lst:.0f} m, {n_r} risers of {rise:.3f} m on treads of {Lt:.2f} m, "
              f"{len(st['fountains'])} fountains")

    # ---- the parking strip's buildings: 'Centre d'entretien' (two) and 'Office', the squares with hipped
    # roofs of the plan: walls in the villas' render on a stone base, the cornice of the villas, a pyramid
    # roof in terracotta tiles, a timber door towards the parking and windows in taupe surrounds -------
    mb = C.MeshBuilder()
    near_road = unary_union([roads, parking])
    for name, g in buildings:
        z0 = min(hz(x, y) for x, y in g.exterior.coords) + PAVE_DZ
        flat = lambda x, y, z=z0: z
        L.prism(mb, "stone", g.buffer(0.05, join_style=2), -0.80, 0.40, zf=flat)
        L.prism(mb, "villa", g, 0.40, BLD_H, zf=flat)
        for zz0, zz1, pd, mat in ((BLD_H - 0.40, BLD_H - 0.32, 0.10, "ledge"), (BLD_H - 0.32, BLD_H - 0.16, 0.08, "band"),
                                  (BLD_H - 0.16, BLD_H, 0.16, "ledge")):
            L.prism(mb, mat, g.buffer(pd, join_style=2).difference(g), zz0, zz1, zf=flat, bottom=True)
        eave = g.buffer(0.45, join_style=2)
        L.prism(mb, "timber", eave.difference(g.buffer(0.16, join_style=2)), BLD_H, BLD_H + 0.12, zf=flat, bottom=True)
        cx, cy = g.centroid.coords[0]
        ring = list(eave.exterior.coords)[:-1]
        top = (cx, cy, z0 + BLD_H + 0.12 + ROOF_H)
        for p, q in zip(ring, ring[1:] + ring[:1]):
            mb.poly("roof_tiles", [(p[0], p[1], z0 + BLD_H + 0.12), (q[0], q[1], z0 + BLD_H + 0.12), top])
        # the door on the side facing the road and the parking, windows on the others
        pts = list(g.exterior.coords)[:4]
        sides = [(np.array(pts[i]), np.array(pts[(i + 1) % 4])) for i in range(4)]
        door = min(range(4), key=lambda i: near_road.distance(LineString([tuple(sides[i][0]), tuple(sides[i][1])])))
        for i, (pa, pb) in enumerate(sides):
            Ls = float(np.linalg.norm(pb - pa))
            t = (pb - pa) / Ls
            n = np.array([t[1], -t[0]])
            mid = (pa + pb) / 2
            if np.dot(mid - np.array([cx, cy]), n) < 0:
                n = -n                                        # outward
            items = [(0.0, 1.20, 0.0, 2.40, "door_wood")] if i == door else \
                [(u, 0.90, 1.10, 2.30, "glass") for u in ((-1.6, 1.6) if Ls > 6.0 else (0.0,))]
            for u, w_, zb, zt, mat in items:
                p0, p1 = mid + t * (u - w_ / 2), mid + t * (u + w_ / 2)
                pane = Polygon([tuple(p0), tuple(p1), tuple(p1 + n * 0.07), tuple(p0 + n * 0.07)])
                frame = Polygon([tuple(p0 - t * 0.12), tuple(p1 + t * 0.12), tuple(p1 + t * 0.12 + n * 0.05), tuple(p0 - t * 0.12 + n * 0.05)])
                L.prism(mb, "surround", frame, 0.40 + zb - (0.0 if i == door else 0.12), 0.40 + zt + 0.12, zf=flat)
                L.prism(mb, mat, pane, 0.40 + zb, 0.40 + zt, zf=flat)
    mb.build("T2_BUILDINGS_CENTRE_ENTRETIEN_OFFICE", cols["T2_01_GROUND"], M)
    print(f"  T2: buildings on the parking strip: {', '.join(n for n, _ in buildings)}")

    # ---- planting --------------------------------------------------------------------------------
    nveg = [0]

    def put(key, xy, z, s=1.0):
        if key == "shrub" and RNG.random() < 0.25:
            key = "shrub_pink"
        ob = bpy.data.objects.new(f"T2_VEG_{key.upper()}_{nveg[0]:03d}", srcv[key].data)
        ob.location = (xy[0], xy[1], z)
        ob.rotation_euler = (0, 0, RNG.uniform(0, 6.283))
        ob.scale = (s, s, s)
        (cols["T2_03_LANDSCAPE"] if key.startswith(("shrub", "agave", "grass")) else cols["T2_04_TREES_PALMS"]).objects.link(ob)
        nveg[0] += 1

    path_all = unary_union(paths)
    for v in vs:
        foot = v.g(VB.FOOT.union(deck[v.c])) if v.t == "B" else v.g(VC.FOOT.union(VC.HARD))
        lawn = v.garden.difference(hard_of(v)).difference(walls).difference(path_all).buffer(-1.3)
        if lawn.is_empty:
            continue
        n = min(4, 1 + int(lawn.area / 45.0))
        x0, y0, x1, y1 = lawn.bounds
        spots = []
        for _ in range(200):
            p = Point(RNG.uniform(x0, x1), RNG.uniform(y0, y1))
            if lawn.contains(p) and foot.distance(p) > 1.6 and all(p.distance(q) > 4.0 for q in spots):
                spots.append(p)
            if len(spots) >= n:
                break
        for k, p in enumerate(spots):
            if k % 2 == 0:
                put("olive", (p.x, p.y), v.zl, RNG.uniform(0.70, 0.95))
            else:
                put("date", (p.x, p.y), v.zl, RNG.uniform(0.55, 0.75))
    # shrubs behind the low walls, inside the gardens
    bed = low.buffer(0.75, join_style=2).intersection(gardens).difference(low.buffer(0.15)).difference(houses.buffer(0.3))
    bed = bed.difference(path_all.buffer(0.3)).difference(unary_union([hard_of(v) for v in vs]))
    for q in L.as_polys(bed):
        if q.area < 0.4:
            continue
        ln = q.minimum_rotated_rectangle
        e = max(zip(list(ln.exterior.coords)[:2], list(ln.exterior.coords)[1:3]), key=lambda ab: math.dist(*ab))
        Lq = math.dist(*e)
        for k in range(int(Lq / 0.75)):
            p = q.representative_point() if Lq < 1.0 else Point(np.array(e[0]) + (np.array(e[1]) - np.array(e[0])) * (k + 0.5) / int(Lq / 0.75))
            p = q.exterior.interpolate(q.exterior.project(p)) if not q.contains(p) else p
            put("shrub", (p.x, p.y), (level(p.x, p.y, 0.1) or hz(p.x, p.y)), RNG.uniform(0.70, 0.90))
    # street palms in pits along the kerb, every 11 m, clear of the gates
    gate_pts = [Point(v.fw(*(((a + b) / 2, c) if axis == "y" else (c, (a + b) / 2)))) for v, axis, c, a, b, _ in gates]
    line = roads.boundary.intersection(pave.buffer(0.02))
    pits = []
    for seg in getattr(line, "geoms", [line]):
        if seg.length < 8.0:
            continue
        for k in range(int(seg.length / 11.0) + 1):
            d = 5.5 + 11.0 * k
            if d > seg.length - 3.0:
                break
            p = seg.interpolate(d)
            q = seg.interpolate(min(seg.length, d + 0.5))
            t = np.array([q.x - p.x, q.y - p.y])
            if np.linalg.norm(t) < 1e-6:
                continue
            t = t / np.linalg.norm(t)
            for sgn in (1, -1):
                c = Point(p.x - sgn * t[1] * 0.80, p.y + sgn * t[0] * 0.80)
                if pave.buffer(-0.45).contains(c):
                    break
            else:
                continue
            if any(c.distance(g) < 3.0 for g in gate_pts) or any(c.distance(o) < 7.0 for o in pits):
                continue
            pits.append(c)
    mb = C.MeshBuilder()
    for c in pits:
        g = c.buffer(0.60, 6)
        L.prism(mb, "kerb", g.difference(g.buffer(-0.08, 6)), -0.20, PAVE_DZ + 0.02, zf=hz)
        L.prism(mb, "soil", g.buffer(-0.08, 6), -0.20, PAVE_DZ - 0.04, zf=hz, sides=False)
        put("wash", (c.x, c.y), hz(c.x, c.y) + PAVE_DZ - 0.04, RNG.uniform(0.85, 1.0))
    mb.build("T2_TREE_PITS", cols["T2_01_GROUND"], M)
    # the planted strips (along Tranche 1's street, behind the bays): date palms down the wide ones every
    # 10 m, agaves, grasses and shrubs between them
    n0 = nveg[0]
    for q in L.as_polys(verges):
        if q.area < 25.0:
            continue
        for cq in L.as_polys(q.buffer(-1.1)):
            if cq.area < 2.0:
                continue
            r = list(cq.minimum_rotated_rectangle.exterior.coords)
            e0, e1 = max(zip(r[:2], r[1:3]), key=lambda ab: math.dist(*ab))
            t = (np.array(e1) - np.array(e0)) / math.dist(e0, e1)
            c0 = np.array(cq.minimum_rotated_rectangle.centroid.coords[0])
            half = math.dist(e0, e1) / 2.0
            for k in range(int(half * 2.0 / 2.5) + 1):
                d = -half + 1.25 + 2.5 * k
                if d > half - 0.5:
                    break
                p = Point(*(c0 + t * d))
                if not cq.contains(p):
                    p = cq.exterior.interpolate(cq.exterior.project(p))
                z = hz(p.x, p.y) + 0.12
                if k % 4 == 1:
                    put("date", (p.x, p.y), z, RNG.uniform(0.55, 0.70))
                else:
                    put(RNG.choice(("agave", "grass", "shrub")), (p.x, p.y), z, RNG.uniform(0.7, 0.95))
    print(f"  T2: planted strips: {nveg[0] - n0} plants")
    # two date palms at each building's door
    for name, g in buildings:
        e = g.buffer(1.6, join_style=2).exterior
        for k in (0.12, 0.62):
            p = e.interpolate(k, normalized=True)
            if pave.contains(p):
                put("date", (p.x, p.y), hz(p.x, p.y) + PAVE_DZ, RNG.uniform(0.6, 0.75))
    print(f"  T2: planting {nveg[0]} (street palms {len(pits)})")

    # ---- the SPA (15_spa, from its permit drawing, on the plan's SPA cell): built in its frame -------------------
    spa = None
    if "spa" in T2:
        SPA = B.load("15_spa.py")
        o_, u_, v_, W_, Lg_ = spa_frame()
        # client 24-10, second review ("habt bach dji 3la ard"): the lot's paving level with the pavement in the
        # middle of its front, on the entrance path; its edge down to the ground, or holding the pavement up
        z_ = hz(*(o_ + v_ * Lg_ / 2)) + PAVE_DZ - SPA.Z_LOT
        col_s = C.collection("T2_05_SPA")
        obs, plants, lamps = SPA.build(M, col_s, W_, Lg_, zg=lambda x, y: hz(*(o_ + u_ * x + v_ * y)) - z_)
        for ob in obs:
            ob.location = (o_[0], o_[1], z_)
            ob.rotation_euler = (0, 0, math.atan2(u_[1], u_[0]))
        n0 = nveg[0]
        for kind, x, y, z, sc_ in plants:
            put(kind, tuple(o_ + u_ * x + v_ * y), z_ + z, sc_)
        spa = (o_, u_, v_, W_, Lg_, z_)
        print(f"  T2: SPA {W_:.1f} x {Lg_:.1f} m on its cell, {len(obs)} objects, {nveg[0] - n0} palms and olive trees, {len(lamps)} lanterns")
    return cameras(vs, hz, buildings, spa)


def cameras(vs, hz, buildings, spa=None):
    """Tranche 2's cameras: aerial of the two blocks, a villa's front and its garden with the pool, a street
    of the northern block, the southern block from above, a gate, the parking strip."""
    col = bpy.data.collections["07_CAMERAS"]
    c = np.array(blocks().centroid.coords[0])
    by = {v.id: v for v in vs}
    hero, s = by["B-14"], by["B-26"]                         # mid-block villas of the northern and southern blocks
    fr = lambda v, x, y: v.fw(x, y)
    b0 = np.array(buildings[1][1].centroid.coords[0]) if len(buildings) > 1 else c
    shots = {
        "T2_CAM_01_AERIAL": (tuple(c + np.array([95.0, -110.0])), 85.0, tuple(c), 0.0, 30),
        "T2_CAM_02_VILLA_B_FRONT": (fr(hero, 15.5, 23.8), 1.7, fr(hero, 5.0, 15.0), 3.5, 20),
        "T2_CAM_03_VILLA_B_GARDEN_POOL": (fr(hero, 11.3, 0.9), 1.6, fr(hero, 3.0, 12.0), 3.0, 18),
        "T2_CAM_04_NORTH_STREET": (fr(hero, -12.0, 24.0), 1.7, fr(hero, 45.0, 23.0), 3.0, 24),
        "T2_CAM_05_SOUTH_BLOCK": (fr(s, -30.0, 40.0), 34.0, fr(s, 10.0, 0.0), 0.0, 26),
        "T2_CAM_06_GATE": (fr(hero, 6.6, 23.0), 1.6, fr(hero, 6.6, 16.0), 1.6, 24),
        "T2_CAM_07_PARKING_CENTRE_ENTRETIEN": (tuple(b0 + np.array([10.0, -24.0])), 6.0, tuple(b0), 2.0, 24),
    }
    if "C-12" in by:                                          # type C: a villa's portal from street 6, the block
        vc, vm = by["C-12"], by["C-04"]
        shots["T2_CAM_08_VILLA_C_FRONT"] = (fr(vc, vc.mx(8.7) + 5.0, 25.0), 1.7, fr(vc, vc.mx(8.7), 14.0), 3.6, 22)
        shots["T2_CAM_09_TYPE_C_AERIAL"] = (fr(vm, -30.0, 70.0), 55.0, fr(vm, 8.0, -12.0), 0.0, 26)
    if spa:                                                   # the SPA (15_spa, its permit drawing): its front, its pools
        o_, u_, v_, W_, Lg_, z_ = spa
        sw = lambda x, y: tuple(o_ + u_ * x + v_ * y)
        shots["T2_CAM_10_SPA_ENTRANCE"] = (sw(-9.0, Lg_ / 2 + 5.0), 1.7, sw(6.2, Lg_ / 2 - 1.0), 3.0, 22)
        shots["T2_CAM_11_SPA_POOLS"] = (sw(1.2, 3.0), 1.7, sw(3.6, 30.0), 1.2, 20)
    cams = {}
    from mathutils import Vector
    for n, (e, eh, t, th, lens) in shots.items():
        cam = bpy.data.objects.new(n, bpy.data.cameras.new(n))
        col.objects.link(cam)
        E = Vector((e[0], e[1], hz(*e) + eh))
        T = Vector((t[0], t[1], hz(*t) + th))
        cam.location = E
        cam.rotation_euler = (T - E).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        cam.data.clip_end = 40000
        cams[n] = cam
    return cams
