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

Levels: the blocks are graded on the plane of Tranche 1 (the 2013 contours fit it within 1.5 m there);
away from them the streets follow the site's own ground (the terrain's height function H of 05, which
blends the plane into the natural ground over 25 m), so the south road goes down along the type C villas
as the contours do. Streets at H, pavements 0.15 m over it with a concrete kerb; each villa's pad at the
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
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
T2 = json.load(open(os.path.join(ROOT, "data", "t2_site.json")))
RNG = random.Random(20261021)
LAWN_DZ = 0.17           # lawn over the pad (the terraces at +0.195)
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
    """The two blocks of villas, graded on the plane: the empty land blends into them (05 build_terrain)."""
    return P(T2["blocks"])


def mats(M):
    """Tranche 2's ground materials: copies of Tranche 1's under their own names, to be finished apart in D5."""
    for k, src, suffix in (("t2_road", "asphalt", ""), ("t2_parking", "asphalt", "_Parking"), ("t2_pave", "pave_beige", "_Pavements"),
                           ("t2_path", "pave_beige", "_Paths"), ("t2_kerb", "kerb", ""), ("t2_lawn", "lawn", "_Gardens")):
        name = f"T2_{M[src].name}{suffix}"                    # T2_<Tranche 1's material>: 08 exports it with that one's texture
        M[k] = M[src].copy()
        M[k].name = name


class Villa:
    def __init__(self, v):
        self.id, self.v = v["id"], v
        self.o, self.rot, self.m, self.c = np.array(v["origin"]), v["rot_deg"], v["mirror"], v["compact"]
        a = math.radians(self.rot)
        self.ex, self.ey = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
        self.garden = P(v["garden"])
        self.gate = v["gate"]
        xs = [self.local(q) for q in self.garden.exterior.coords]
        self.gx0, self.gx1 = min(x for x, _ in xs), max(x for x, _ in xs)
        self.gy1 = max(y for _, y in xs)

    def mx(self, x):
        return 12.20 - x if self.m else x

    def w(self, x, y):
        """drawing local (before mirroring) -> world"""
        return tuple(self.o + self.ex * self.mx(x) + self.ey * y)

    def fw(self, x, y):
        """frame local (as placed, not mirrored) -> world"""
        return tuple(self.o + self.ex * x + self.ey * y)

    def g(self, geom):
        """a polygon in drawing coordinates -> world (mirrored with the villa)"""
        if self.m:
            geom = affinity.scale(geom, -1.0, 1.0, origin=(6.10, 0.0))
        return self.f(geom)

    def f(self, geom):
        """a polygon in frame coordinates -> world"""
        return affinity.translate(affinity.rotate(geom, self.rot, origin=(0, 0)), *self.o)

    def local(self, p):
        d = np.array(p) - self.o
        return float(np.dot(d, self.ex)), float(np.dot(d, self.ey))

    def side_kind(self):
        """for a side gate: is it on the side of the front terrace (drawing +x) or of the kitchen wing?"""
        right = self.gate == "right"
        return "terrace" if right != self.m else "kitchen"


def build(M, B, srcv, H):
    """B: the 05_build_scene module (collections, load), srcv: its plant sources, H: its terrain height
    function (xy array -> z). Returns the T2 cameras."""
    hz = lambda x, y: float(H(np.array([[x, y]]))[0])
    VB = B.load("12_villa_b.py")
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

    vs = [Villa(v) for v in T2["villas"]]
    gardens = unary_union([v.garden for v in vs])
    roads, pave, parking = PL(T2["roads"]), PL(T2["pavements"]), PL(T2["parking"])
    bays = [P(b) for b in T2["bays"]]
    buildings = [(b["name"], P(b["poly"])) for b in T2["buildings"]]
    public = unary_union([roads, pave, parking])

    # ---- villas --------------------------------------------------------------------------------
    for v in vs:
        v.pad = hz(*v.w(6.10, 12.0))
        v.zl = v.pad + LAWN_DZ
        ob = bpy.data.objects.new("T2_VILLA_" + v.id.replace("-", ""), src[(v.m, v.c)].data)
        ob.location = (*v.o, v.pad)
        ob.rotation_euler = (0, 0, math.radians(v.rot))
        cols["T2_02_VILLAS"].objects.link(ob)
    print(f"  T2: {len(vs)} villas type B ({sum(v.m for v in vs)} mirrored, {sum(v.c for v in vs)} compact); gates "
          f"{sum(v.gate == 'front' for v in vs)} on the front, {sum(v.gate != 'front' for v in vs)} on the side")

    def level(x, y, pad=0.6):
        """the highest garden level within pad of (x, y), or None"""
        p = Point(x, y)
        zs = [v.zl for v in vs if v.garden.distance(p) <= pad]
        return max(zs) if zs else None

    # ---- the gates: (villa, axis, c, a, b) in frame coordinates: a wall along x at y = c, or along y at x = c
    gates = []
    for v in vs:
        if v.gate == "front":
            a, b = sorted((v.mx(GATE[0]), v.mx(GATE[1])))
            gates.append((v, "y", v.gy1, a, b))
        else:
            y0, y1 = (17.30, 19.30) if v.side_kind() == "terrace" else (16.20, 17.80)
            gates.append((v, "x", v.gx1 if v.gate == "right" else v.gx0, y0, y1))

    def gate_box(axis, c, a, b, d=0.6):
        return box(a, c - d, b, c + d) if axis == "y" else box(c - d, a, c + d, b)

    # ---- walls: garden walls on the gardens' outlines, the low wall on each villa's street side -----
    ring = unary_union([v.garden.boundary.buffer(0.10, cap_style=2, join_style=2) for v in vs])
    houses = unary_union([v.g(VB.RDC.union(box(1.03, 18.11, 5.47, 20.11))) for v in vs])
    low_zone, openings = [], []
    for v, axis, c, a, b in gates:
        if axis == "y":
            low_zone.append(v.f(box(v.gx0 - 1.0, c - 0.60, v.gx1 + 1.0, c + 0.60)))
        else:
            low_zone.append(v.f(box(c - 0.60, 10.0, c + 0.60, v.gy1 + 1.0)))
        openings.append(v.f(gate_box(axis, c, a, b)))
    lz = unary_union(low_zone).intersection(public.buffer(0.4))
    low = ring.intersection(lz).difference(houses).difference(unary_union(openings))
    high = ring.difference(lz).difference(houses).difference(unary_union(openings))
    mb = C.MeshBuilder()
    zg = lambda x, y: max(hz(x, y), (level(x, y) or -1e9) - (W_GARDEN - 1.20))
    for g in L.as_polys(high):
        if g.area < 0.02:
            continue
        L.prism(mb, "render", g, -1.60, W_GARDEN, zf=zg)
        L.prism(mb, "trim", g.buffer(0.03, join_style=2).difference(houses), W_GARDEN, W_GARDEN + 0.05, zf=zg)
    mb.build("T2_WALLS_GARDENS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    zf_low = lambda x, y: max(hz(x, y) + PAVE_DZ, level(x, y, 0.4) or -1e9)
    for g in L.as_polys(low):
        if g.area < 0.02:
            continue
        L.prism(mb, "cladding", g, -1.20, W_FRONT, zf=zf_low)
        L.prism(mb, "coping_beige", g.buffer(0.04, join_style=2).intersection(low.buffer(0.04, join_style=2)), W_FRONT, W_FRONT + 0.08, zf=zf_low)
    # gate pillars and gates (as Tranche 1's villas): stone-clad pillars with their coping, timber slats
    for v, axis, c, a, b in gates:
        mid = v.fw(*(((a + b) / 2, c) if axis == "y" else (c, (a + b) / 2)))
        z = max(hz(*mid) + PAVE_DZ, v.zl)
        flat = lambda x, y, z=z: z
        for p0, p1 in ((a - 0.40, a), (b, b + 0.40)):
            g = v.f(gate_box(axis, c, p0, p1, 0.20))
            L.prism(mb, "cladding", g, -1.20, 1.38, zf=flat)
            L.prism(mb, "coping_beige", g.buffer(0.03, join_style=2), 1.38, 1.46, zf=flat)
        n = max(6, int((b - a) / 0.11))
        for k in range(n):
            t = a + 0.03 + (b - a - 0.13) * k / (n - 1)
            L.prism(mb, "door_wood", v.f(gate_box(axis, c, t, t + 0.07, 0.02)), 0.12, 1.30, zf=flat)
        for zz in (0.30, 1.10):
            L.prism(mb, "door_wood", v.f(gate_box(axis, c, a + 0.02, b - 0.02, 0.02)), zz, zz + 0.08, zf=flat)
    mb.build("T2_WALLS_FRONT_GATES", cols["T2_01_GROUND"], M)
    print(f"  T2: garden walls {high.area:.0f} m2 of plan, low street walls {low.area:.0f} m2, {len(gates)} gates")

    # ---- gardens: lawn, path from the gate to the door, slab under the house -----------------------
    walls = unary_union([high, low])
    mb_l, mb_p, mb_s = C.MeshBuilder(), C.MeshBuilder(), C.MeshBuilder()
    paths = []
    for (v, axis, c, a, b) in gates:
        hd = v.g(hard[v.c])
        if axis == "y":
            path = v.f(box(a, 18.05, b, c + 1.0))
        elif v.side_kind() == "terrace":                      # along the front to the front terrace
            x_h = 12.22 if not v.m else -0.02
            path = v.f(box(min(c, x_h) - 0.6, a, max(c, x_h) + 0.6, b))
        else:                                                 # to the kitchen's side door
            x_h = 1.03 if not v.m else 11.17
            path = v.f(box(min(c, x_h) - 0.6, a, max(c, x_h) + 0.6, b))
        path = path.intersection(v.garden).difference(hd)
        paths.append(path)
        low_z = min(hz(x, y) for x, y in v.garden.exterior.coords) - 0.65
        lawn = v.garden.difference(hd).difference(path).difference(walls)
        flat = lambda x, y, z=v.zl: z
        L.prism(mb_l, "t2_lawn", lawn, low_z - v.zl, 0.0, zf=flat)
        L.prism(mb_p, "t2_path", path.difference(walls), low_z - v.zl, Z_PATH, zf=flat)
        L.prism(mb_s, "interior_floor", v.g(VB.RDC.buffer(-0.05, join_style=2)), low_z - v.zl, 0.02, zf=flat)
    mb_l.build("T2_GROUND_GARDENS_LAWN", cols["T2_01_GROUND"], M)
    mb_p.build("T2_GROUND_ENTRANCE_PATHS", cols["T2_01_GROUND"], M)
    mb_s.build("T2_GROUND_HOUSE_SLABS", cols["T2_01_GROUND"], M)

    # ---- streets, pavements, kerbs, parking --------------------------------------------------------
    roads = roads.difference(gardens)
    pave = pave.difference(gardens)
    kerb = pave.intersection(roads.union(parking).buffer(0.16, join_style=2))
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
    L.prism(mb, "t2_parking", parking, -0.65, 0.0, zf=hz)
    mb.build("T2_GROUND_PARKING", cols["T2_01_GROUND"], M)
    # the bays as the plan draws them: 10 cm white lines on their two long sides
    mb = C.MeshBuilder()
    for b in bays:
        q = list(b.exterior.coords)[:4]
        e = sorted(((q[i], q[(i + 1) % 4]) for i in range(4)), key=lambda ab: -math.dist(*ab))[:2]
        for p0, p1 in e:
            g = LineString([p0, p1]).buffer(0.05, cap_style=2)
            L.prism(mb, "paint", g, 0.004, 0.006, zf=hz, sides=False)
    mb.build("T2_ROAD_PAINT_PARKING", cols["T2_01_GROUND"], M)
    print(f"  T2: streets {roads.area:.0f} m2, pavements {pave.area:.0f} m2, parking {parking.area:.0f} m2 ({len(bays)} bays)")

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
        foot = v.g(VB.FOOT.union(deck[v.c]))
        lawn = v.garden.difference(v.g(hard[v.c])).difference(walls).difference(path_all).buffer(-1.3)
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
    bed = bed.difference(path_all.buffer(0.3)).difference(unary_union([v.g(hard[v.c]) for v in vs]))
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
    gate_pts = [Point(v.fw(*(((a + b) / 2, c) if axis == "y" else (c, (a + b) / 2)))) for v, axis, c, a, b in gates]
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
    # two date palms at each building's door
    for name, g in buildings:
        e = g.buffer(1.6, join_style=2).exterior
        for k in (0.12, 0.62):
            p = e.interpolate(k, normalized=True)
            if pave.contains(p):
                put("date", (p.x, p.y), hz(p.x, p.y) + PAVE_DZ, RNG.uniform(0.6, 0.75))
    print(f"  T2: planting {nveg[0]} (street palms {len(pits)})")
    return cameras(vs, hz, buildings)


def cameras(vs, hz, buildings):
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
