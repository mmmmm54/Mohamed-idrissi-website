"""
13_tranche2 — Tranche 2: the villas type B of the plan de masse 31-05-13 (client 21-10: "zid ghir tranche
2", the type B blocks circled on the plan), built into the scene of Tranche 1 by 05_build_scene after
Tranche 1's planting. Everything here lives in collections, objects and materials of its own (T2_...);
Tranche 1 is not touched.

Data: data/t2_site.json (11_extract_t2): 33 villas on their gardens, the streets, pavements, the planted
square and the parking of the southern block. Model: 12_villa_b (villa type B, its pool in the garden).

Levels: the ground of Tranche 2 is graded on the plane of Tranche 1 (the 2013 contours fit it within
1.5 m there): streets at the plane, pavements 0.15 m over it with a concrete kerb; each villa's pad at the
plane height of its centre, its garden flat at the pad (+0.17, lawn 3 cm under the terraces), held by its
walls where the plane falls away. Garden walls 1.80 m in the render of the villas with their trim (at
least 1.20 m over the lawn), a low stone-clad wall with its beige coping on the street front, with the
gate pillars and timber gate of the villas of Tranche 1, a paved path to the door; where a turned villa
has its side garden on the street, a car gate and a paved drive. Planting: olive trees and date palms
in the gardens, shrubs behind the front walls, Washingtonia palms in pits along the streets, olive trees
on the square.
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
GATE = (5.62, 7.70)      # pedestrian gate, local x on the front (the plan's 'Accès', between kitchen and stair)
CAR_W = 3.20             # car gate of a side garden on the street
Z_PATH = 0.025           # the path's top over the lawn (the terraces' level)


def P(p):
    return Polygon(p["ext"], p["holes"]).buffer(0)


def PL(lst):
    return unary_union([P(p) for p in lst]) if lst else Polygon()


def envelope():
    """Tranche 2's ground: the terrain of the site is cut away there (05 build_terrain)."""
    return P(T2["env"])


def mats(M):
    """Tranche 2's ground materials: copies of Tranche 1's under their own names, to be finished apart in D5."""
    for k, src, suffix in (("t2_road", "asphalt", ""), ("t2_parking", "asphalt", "_Parking"), ("t2_pave", "pave_beige", "_Pavements"),
                           ("t2_path", "pave_beige", "_Paths"), ("t2_kerb", "kerb", ""), ("t2_lawn", "lawn", "_Gardens"),
                           ("t2_square", "lawn", "_Square")):
        name = f"T2_{M[src].name}{suffix}"                    # T2_<Tranche 1's material>: 08 exports it with that one's texture
        M[k] = M[src].copy()
        M[k].name = name


class Villa:
    def __init__(self, v):
        self.id, self.v = v["id"], v
        self.o, self.rot, self.m = np.array(v["origin"]), v["rot_deg"], v["mirror"]
        a = math.radians(self.rot)
        self.ex, self.ey = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
        self.garden = P(v["garden"])

    def mx(self, x):
        return 12.20 - x if self.m else x

    def w(self, x, y):
        """model local (as drawn, before mirroring) -> world"""
        return tuple(self.o + self.ex * self.mx(x) + self.ey * y)

    def g(self, geom):
        """a local polygon of the drawing -> world (mirrored with the villa)"""
        if self.m:
            geom = affinity.scale(geom, -1.0, 1.0, origin=(6.10, 0.0))
        return affinity.translate(affinity.rotate(geom, self.rot, origin=(0, 0)), *self.o)

    def local(self, p):
        d = np.array(p) - self.o
        return float(np.dot(d, self.ex)), float(np.dot(d, self.ey))


def build(M, B, srcv):
    """B: the 05_build_scene module (hz, collections), srcv: its plant sources. Returns the T2 cameras."""
    hz = B.hz
    VB = B.load("12_villa_b.py")
    mats(M)
    cols = {k: C.collection(k) for k in ("T2_01_GROUND", "T2_02_VILLAS", "T2_03_LANDSCAPE", "T2_04_TREES_PALMS")}
    src = {False: VB.build(M, B.C.collection("SRC"), "SRC_T2_VILLA_B")}
    src[True] = VB.mirrored(src[False], "SRC_T2_VILLA_B_MIRRORED")

    vs = [Villa(v) for v in T2["villas"]]
    env = envelope()
    gardens = unary_union([v.garden for v in vs])
    roads, pave = PL(T2["roads"]), PL(T2["pavements"])
    square, parking = PL(T2["greens"]), PL(T2["parking"])

    # ---- villas --------------------------------------------------------------------------------
    for v in vs:
        v.pad = hz(*v.w(6.10, 12.0))
        v.zl = v.pad + LAWN_DZ
        ob = bpy.data.objects.new("T2_VILLA_" + v.id.replace("-", ""), src[v.m].data)
        ob.location = (*v.o, v.pad)
        ob.rotation_euler = (0, 0, math.radians(v.rot))
        cols["T2_02_VILLAS"].objects.link(ob)
    print(f"  T2: {len(vs)} villas type B ({sum(v.m for v in vs)} mirrored, {sum(v.v.get('turned', False) for v in vs)} turned onto their street)")

    def level(x, y, pad=0.6):
        """the highest garden level within pad of (x, y), or None"""
        p = Point(x, y)
        zs = [v.zl for v in vs if v.garden.distance(p) <= pad]
        return max(zs) if zs else None

    # ---- walls: garden walls on the gardens' outlines, the low front wall on the street ------------
    ring = unary_union([v.garden.boundary.buffer(0.10, cap_style=2, join_style=2) for v in vs])
    houses = unary_union([v.g(VB.RDC.union(box(1.03, 18.11, 5.47, 20.11))) for v in vs])
    front_zone, front_open, gates, drives = [], [], [], []
    for v in vs:
        xs = [v.local(q)[0] for q in v.garden.exterior.coords]
        gx0, gx1 = min(xs), max(xs)                          # the garden across, in the villa's frame
        front_zone.append(v.g(box(-40.0, 19.90, 52.0, 21.0)))
        a, b = GATE
        front_open.append(v.g(box(a, 19.50, b, 21.5)))
        gates.append((v, a, b))
        # a side garden on the street (turned villas, 3.6 m or more beside the house on the salon side)
        side = (gx1 - 12.20) if not v.m else (0.0 - gx0)
        if side >= CAR_W + 0.60:
            c0 = 12.50                                          # drawing frame: past the salon marocain's side
            front_open.append(v.g(box(c0, 19.50, c0 + CAR_W, 21.5)))
            drives.append((v, c0, c0 + CAR_W))
    fz = unary_union(front_zone)
    low = ring.intersection(fz).difference(houses).difference(unary_union(front_open))
    high = ring.difference(fz).difference(houses)
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
    for v, a, b in gates + drives:
        cut = LineString([v.w(0.5 * (a + b), 15.0), v.w(0.5 * (a + b), 24.0)]).intersection(v.garden)
        y0 = max(v.local(q)[1] for q in (cut.coords if cut.geom_type == "LineString" else [v.w(0, 20.1)]))
        z = max(hz(*v.w(0.5 * (a + b), y0)) + PAVE_DZ, v.zl)
        for xa, xb in ((a - 0.40, a), (b, b + 0.40)):
            g = v.g(box(xa, y0 - 0.20, xb, y0 + 0.20))
            L.prism(mb, "cladding", g, -1.20, 1.38, zf=lambda x, y, z=z: z)
            L.prism(mb, "coping_beige", g.buffer(0.03, join_style=2), 1.38, 1.46, zf=lambda x, y, z=z: z)
        n = max(6, int((b - a) / 0.11))
        for k in range(n):
            u = a + 0.03 + (b - a - 0.13) * k / (n - 1)
            L.prism(mb, "door_wood", v.g(box(u, y0 - 0.02, u + 0.07, y0 + 0.02)), 0.12, 1.30, zf=lambda x, y, z=z: z)
        for zz in (0.30, 1.10):
            L.prism(mb, "door_wood", v.g(box(a + 0.02, y0 + 0.02, b - 0.02, y0 + 0.06)), zz, zz + 0.08, zf=lambda x, y, z=z: z)
    mb.build("T2_WALLS_FRONT_GATES", cols["T2_01_GROUND"], M)
    print(f"  T2: garden walls {high.area:.0f} m2 of plan, front walls {low.area:.0f} m2, {len(gates)} gates, {len(drives)} car gates")

    # ---- gardens: lawn, path to the door, drive, slab under the house ------------------------------
    walls = unary_union([high, low])
    mb_l, mb_p, mb_s = C.MeshBuilder(), C.MeshBuilder(), C.MeshBuilder()
    paths = []
    for v in vs:
        hard = v.g(VB.HARD)
        a, b = GATE
        path = v.g(box(a, 18.05, b, 21.5)).intersection(v.garden)
        for dv, c0, c1 in drives:
            if dv is v:
                path = path.union(v.g(box(c0, 13.0, c1, 21.5)).intersection(v.garden))
        path = path.difference(hard)
        paths.append(path)
        low_z = min(hz(x, y) for x, y in v.garden.exterior.coords) - 0.65
        lawn = v.garden.difference(hard).difference(path).difference(walls)
        flat = lambda x, y, z=v.zl: z
        L.prism(mb_l, "t2_lawn", lawn, low_z - v.zl, 0.0, zf=flat)
        L.prism(mb_p, "t2_path", path.difference(walls), low_z - v.zl, Z_PATH, zf=flat)
        L.prism(mb_s, "interior_floor", v.g(VB.RDC.buffer(-0.05, join_style=2)), low_z - v.zl, 0.02, zf=flat)
    mb_l.build("T2_GROUND_GARDENS_LAWN", cols["T2_01_GROUND"], M)
    mb_p.build("T2_GROUND_ENTRANCE_PATHS", cols["T2_01_GROUND"], M)
    mb_s.build("T2_GROUND_HOUSE_SLABS", cols["T2_01_GROUND"], M)

    # ---- streets, pavements, kerbs, square, parking ----------------------------------------------
    kerb = pave.intersection(roads.buffer(0.16, join_style=2)).difference(gardens)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_road", roads, -0.65, 0.0, zf=hz)
    mb.build("T2_GROUND_ROADS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_pave", pave.difference(kerb).difference(gardens), -0.65, PAVE_DZ, zf=hz)
    mb.build("T2_GROUND_PAVEMENTS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_kerb", kerb, -0.65, PAVE_DZ + 0.005, zf=hz)
    mb.build("T2_GROUND_KERBS", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_square", square, -0.65, 0.12, zf=hz)
    mb.build("T2_GROUND_SQUARE_LAWN", cols["T2_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_parking", parking, -0.65, 0.0, zf=hz)
    mb.build("T2_GROUND_PARKING", cols["T2_01_GROUND"], M)
    # the parking's bays: 10 cm white lines across its long side every 2.50 m, 5.00 m deep, from the kerb
    mb = C.MeshBuilder()
    n_bay = 0
    for q in L.as_polys(parking):
        rr = list(q.minimum_rotated_rectangle.exterior.coords)
        e = max(((rr[i], rr[i + 1]) for i in range(2)), key=lambda ab: math.dist(*ab))
        along = (np.array(e[1]) - np.array(e[0])) / math.dist(*e)
        nrm = np.array([-along[1], along[0]])
        c = np.array(q.centroid.coords[0])
        side = 1.0 if np.dot(np.array(e[0]) - c, nrm) > 0 else -1.0       # the edge the long side lies on
        Lq = math.dist(*e)
        for k in range(1, int(Lq / 2.5)):
            p0 = np.array(e[0]) + along * 2.5 * k
            ln = LineString([tuple(p0), tuple(p0 - nrm * side * 5.0)]).intersection(q.buffer(-0.3))
            if ln.length > 3.0:
                g = ln.buffer(0.05, cap_style=2)
                L.prism(mb, "paint", g, 0.004, 0.006, zf=hz, sides=False)
                n_bay += 1
    mb.build("T2_ROAD_PAINT_PARKING", cols["T2_01_GROUND"], M)
    print(f"  T2: streets {roads.area:.0f} m2, pavements {pave.area:.0f} m2, square {square.area:.0f} m2, parking {parking.area:.0f} m2 ({n_bay} bay lines)")

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

    foot = unary_union([v.g(VB.FOOT.union(VB.DECK)) for v in vs])
    path_all = unary_union(paths)
    for v in vs:
        lawn = v.garden.difference(v.g(VB.HARD)).difference(walls).buffer(-1.3)
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
        # shrubs behind the low front wall, both sides of the gate (as Tranche 1's villas)
        for x in list(np.arange(0.9, GATE[0] - 0.5, 0.75)) + list(np.arange(GATE[1] + 0.6, 12.0, 0.75)):
            p = v.w(x, 19.35)
            if v.garden.contains(Point(p)) and not v.g(VB.HARD).buffer(0.2).contains(Point(p)) and not path_all.contains(Point(p)):
                put("shrub", p, v.zl, RNG.uniform(0.70, 0.90))
    # street palms in pits along the kerb, every 11 m, clear of the gates and corners
    gate_pts = [Point(v.w(0.5 * (a + b), 20.3)) for v, a, b in gates + drives]
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
    # the square: olive trees on a loose grid, shrub clumps
    n_sq = 0
    for q in L.as_polys(square.buffer(-1.5)):
        x0, y0, x1, y1 = q.bounds
        for x in np.arange(x0 + 2.0, x1, 6.5):
            for y in np.arange(y0 + 2.0, y1, 6.5):
                p = Point(x + RNG.uniform(-1.2, 1.2), y + RNG.uniform(-1.2, 1.2))
                if q.contains(p):
                    put("olive", (p.x, p.y), hz(p.x, p.y) + 0.12, RNG.uniform(0.8, 1.0))
                    for _ in range(2):
                        put("shrub", (p.x + RNG.uniform(-1.5, 1.5), p.y + RNG.uniform(-1.5, 1.5)), hz(p.x, p.y) + 0.12, RNG.uniform(0.8, 1.1))
                    n_sq += 1
    print(f"  T2: planting {nveg[0]} (street palms {len(pits)}, square olives {n_sq})")
    return cameras(vs, hz)



def cameras(vs, hz):
    """Tranche 2's cameras: aerial of the two blocks, a street of the northern block, a villa's front
    and its garden with the pool, a street of the northern block, the southern block from above, a gate."""
    col = bpy.data.collections["07_CAMERAS"]
    env = envelope()
    c = np.array(env.centroid.coords[0])
    by = {v.id: v for v in vs}
    hero, s = by["B-14"], by["B-26"]                         # mid-block villas of the northern and southern blocks
    fr = lambda v, x, y: tuple(v.o + v.ex * x + v.ey * y)    # the villa's frame (not mirrored)
    shots = {
        "T2_CAM_01_AERIAL": (tuple(c + np.array([95.0, -110.0])), 85.0, tuple(c), 0.0, 30),
        "T2_CAM_02_VILLA_B_FRONT": (fr(hero, 15.5, 23.8), 1.7, fr(hero, 5.0, 15.0), 3.5, 20),
        "T2_CAM_03_VILLA_B_GARDEN_POOL": (fr(hero, 11.3, 0.9), 1.6, fr(hero, 3.0, 12.0), 3.0, 18),
        "T2_CAM_04_NORTH_STREET": (fr(hero, -12.0, 24.0), 1.7, fr(hero, 45.0, 23.0), 3.0, 24),
        "T2_CAM_05_SOUTH_BLOCK": (fr(s, -25.0, 48.0), 32.0, fr(s, 8.0, 6.0), 0.0, 26),
        "T2_CAM_06_GATE": (fr(hero, 6.6, 23.0), 1.6, fr(hero, 6.6, 16.0), 1.6, 24),
    }
    cams = {}
    for n, (e, eh, t, th, lens) in shots.items():
        cam = bpy.data.objects.new(n, bpy.data.cameras.new(n))
        col.objects.link(cam)
        E = np.array([e[0], e[1], hz(*e) + eh])
        T = np.array([t[0], t[1], hz(*t) + th])
        from mathutils import Vector
        cam.location = Vector(E)
        cam.rotation_euler = (Vector(T) - Vector(E)).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        cam.data.clip_end = 40000
        cams[n] = cam
    return cams
