"""
19_tranche3 — Tranche 3: the hotel and the villas type A, west of the SPA and of the type C block (client 23-10:
"zid db had tranche kayn fiha hotel and villa type a", the zone circled in blue on the plan de masse), built into
the scene by 05_build_scene after Tranche 2, in collections, objects and materials of its own (T3_...).

Data: data/t3_site.json (18_extract_t3): the four lots of the villas type A west of street 7 and the passage
between the second and the third, the hotel's plot between street 7 and the parking, the parking with its bays,
the streets (street 7, the Voie Publique, the south road) with their 0.40 m of pavement along the fences.
Models: 16_villa_a (from the plan de masse's drawing of the villa), 17_hotel (a design proposal).

Levels as Tranche 2: the tranche is graded on the plane of Tranche 1 (05 build_terrain blends the site's
empty land into it); streets on it, pavements 0.15 m over them with their kerb; each villa's garden flat at
its pad (the height of the house's centre, lawn +0.07), held by its walls: 1.80 m in the villas' render with
the trim, a low stone-clad wall with its beige coping on street 7, the gate pillars and timber gate of the
residence on the axis of the house's entrance court, a paved path to it.
"""
import json
import math
import os
import random

import bpy
import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
T3 = json.load(open(os.path.join(ROOT, "data", "t3_site.json")))
RNG = random.Random(20261023)
PAVE_DZ = 0.15           # pavements over the street
LAWN_A = 0.07            # lawn over the pad (the villa's terraces at +0.195)
W_GARDEN, W_FRONT = 1.80, 0.70
Z_PATH = 0.025


def P(p):
    return Polygon(p["ext"], p.get("holes", [])).buffer(0)


def PL(lst):
    return unary_union([P(p) for p in lst]) if lst else Polygon()


def envelope():
    """Tranche 3's ground: graded on the plane, the site's empty land cut away there (05 build_terrain)."""
    return P(T3["env"])


def build(M, B, srcv, H):
    """B: the 05_build_scene module (load), srcv: its plant sources, H: its terrain height function. Returns the
    T3 cameras."""
    hz = lambda x, y: float(H(np.array([[x, y]]))[0])
    VA = B.load("16_villa_a.py")
    HO = B.load("17_hotel.py")
    cols = {k: C.collection(k) for k in ("T3_01_GROUND", "T3_02_VILLAS", "T3_03_LANDSCAPE", "T3_04_TREES_PALMS", "T3_05_HOTEL")}
    src_a, plants_a = VA.build(M, C.collection("SRC"), "SRC_T3_VILLA_A")
    nveg = [0]

    def put(key, xy, z, s=1.0):
        if key == "shrub" and RNG.random() < 0.25:
            key = "shrub_pink"
        ob = bpy.data.objects.new(f"T3_VEG_{key.upper()}_{nveg[0]:03d}", srcv[key].data)
        ob.location = (float(xy[0]), float(xy[1]), z)
        ob.rotation_euler = (0, 0, RNG.uniform(0, 6.283))
        ob.scale = (s, s, s)
        (cols["T3_03_LANDSCAPE"] if key.startswith(("shrub", "agave", "grass")) else cols["T3_04_TREES_PALMS"]).objects.link(ob)
        nveg[0] += 1

    # ---- the villas type A on their lots ------------------------------------------------------------------
    vs = []
    for v in T3["villas_a"]:
        o, a = np.array(v["origin"]), math.radians(v["rot_deg"])
        ex, ey = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
        w = lambda x, y, o=o, ex=ex, ey=ey: tuple(o + ex * x + ey * y)
        loc = lambda p, o=o, ex=ex, ey=ey: (float(np.dot(np.array(p) - o, ex)), float(np.dot(np.array(p) - o, ey)))
        lot = Polygon(v["garden"]["ext"]).buffer(0)
        pad = hz(*w(*VA.HOUSE_C))
        ob = bpy.data.objects.new("T3_VILLA_" + v["id"].replace("-", ""), src_a.data)
        ob.location = (float(o[0]), float(o[1]), pad)
        ob.rotation_euler = (0, 0, a)
        cols["T3_02_VILLAS"].objects.link(ob)
        for kind, x, y, z, s in plants_a:
            put(kind, w(x, y), pad + z, s)
        lot_l = Polygon([loc(p) for p in lot.exterior.coords])
        gy = (VA.GATE_Y[0] + VA.GATE_Y[1]) / 2
        cut_ = lot_l.boundary.intersection(LineString([(-50, gy), (80, gy)]))
        xe = max(p.x for p in getattr(cut_, "geoms", [cut_]))     # the lot's edge on street 7, on the gate's axis
        f = lambda g, w=w: unary_union([Polygon([w(x, y) for x, y in q.exterior.coords], [[w(x, y) for x, y in r.coords] for r in q.interiors])
                                        for q in L.as_polys(g)])
        vs.append({"id": v["id"], "lot": lot, "pad": pad, "zl": pad + LAWN_A, "w": w, "f": f, "ex": ex,
                   "foot": f(VA.FOOT.buffer(0.02, join_style=2)), "gate": f(box(xe - 0.6, VA.GATE_Y[0], xe + 0.6, VA.GATE_Y[1])),
                   "gate_c": w(xe, gy), "path": f(box(VA.HOUSE.bounds[2] - 0.05, VA.GATE_Y[0], xe + 0.5, VA.GATE_Y[1])), "xe": xe, "gy": gy})
    print(f"  T3: {len(vs)} villas type A, pads", ", ".join(f"{v_['pad']:.2f}" for v_ in vs))

    def level(x, y, pad=0.6):
        p = Point(x, y)
        zs = [v["zl"] for v in vs if v["lot"].distance(p) <= pad]
        return max(zs) if zs else None

    roads, pave, parking = PL(T3["roads"]), PL(T3["pavements"]), PL(T3["parking"])
    ppath, strips = PL(T3["passage_path"]), PL(T3["passage_strips"])
    public = unary_union([roads, pave, parking])
    # walls: the lots' outlines, a low wall on street 7 (the lot's side facing the plan's east), the gates
    ring = unary_union([v["lot"].boundary.buffer(0.10, cap_style=2, join_style=2) for v in vs])
    low_zone, openings = [], []
    for v in vs:
        ring_ = orient(v["lot"], 1.0).exterior.coords
        for p0, p1 in zip(ring_[:-1], ring_[1:]):
            e = np.array(p1) - np.array(p0)
            if np.linalg.norm(e) > 0.05 and float(np.dot(np.array([e[1], -e[0]]) / np.linalg.norm(e), v["ex"])) > 0.82:
                low_zone.append(LineString([p0, p1]).buffer(0.60, cap_style=2, join_style=2))
        openings.append(v["gate"])
    lz = unary_union(low_zone).intersection(public.buffer(0.4))
    low = ring.intersection(lz).difference(unary_union(openings))
    high = ring.difference(lz).difference(unary_union(openings))
    mb = C.MeshBuilder()
    zg = lambda x, y: max(hz(x, y), (level(x, y) or -1e9) - (W_GARDEN - 1.20))
    for g in L.as_polys(high):
        if g.area > 0.02:
            L.prism(mb, "render", g, -1.60, W_GARDEN, zf=zg)
            L.prism(mb, "trim", g.buffer(0.03, join_style=2), W_GARDEN, W_GARDEN + 0.05, zf=zg)
    mb.build("T3_WALLS_GARDENS", cols["T3_01_GROUND"], M)
    mb = C.MeshBuilder()
    zf_low = lambda x, y: max(hz(x, y) + PAVE_DZ, level(x, y, 0.4) or -1e9)
    for g in L.as_polys(low):
        if g.area > 0.02:
            L.prism(mb, "cladding", g, -1.20, W_FRONT, zf=zf_low)
            L.prism(mb, "coping_beige", g.buffer(0.04, join_style=2).intersection(low.buffer(0.04, join_style=2)), W_FRONT, W_FRONT + 0.08, zf=zf_low)
    for v in vs:                                              # pillars and the timber gate, across the lot's edge
        z = max(hz(*v["gate_c"]) + PAVE_DZ, v["zl"])
        flat = lambda x, y, z=z: z
        a_, b_ = VA.GATE_Y
        for p0, p1 in ((a_ - 0.40, a_), (b_, b_ + 0.40)):
            g = v["f"](box(v["xe"] - 0.20, p0, v["xe"] + 0.20, p1))
            L.prism(mb, "cladding", g, -1.20, 1.38, zf=flat)
            L.prism(mb, "coping_beige", g.buffer(0.03, join_style=2), 1.38, 1.46, zf=flat)
        n = max(6, int((b_ - a_) / 0.11))
        for k in range(n):
            t = a_ + 0.03 + (b_ - a_ - 0.13) * k / (n - 1)
            L.prism(mb, "door_wood", v["f"](box(v["xe"] - 0.02, t, v["xe"] + 0.02, t + 0.07)), 0.12, 1.30, zf=flat)
        for zz in (0.30, 1.10):
            L.prism(mb, "door_wood", v["f"](box(v["xe"] - 0.02, a_ + 0.02, v["xe"] + 0.02, b_ - 0.02)), zz, zz + 0.08, zf=flat)
    mb.build("T3_WALLS_FRONT_GATES", cols["T3_01_GROUND"], M)
    walls = unary_union([high, low])
    # gardens: the lawn at the pad, the path from the gate to the court's arch; trees in the lawn
    mb_l, mb_p = C.MeshBuilder(), C.MeshBuilder()
    for v in vs:
        path = v["path"].intersection(v["lot"]).difference(v["foot"])
        low_z = min(hz(x, y) for x, y in v["lot"].exterior.coords) - 0.65
        flat = lambda x, y, z=v["zl"]: z
        lawn = v["lot"].difference(v["foot"]).difference(path).difference(walls)
        L.prism(mb_l, "t2_lawn", lawn, low_z - v["zl"], 0.0, zf=flat)
        L.prism(mb_p, "t2_path", path.difference(walls), low_z - v["zl"], Z_PATH, zf=flat)
        spots = []
        zone = lawn.buffer(-1.4)
        x0, y0, x1, y1 = zone.bounds if not zone.is_empty else (0, 0, 0, 0)
        for _ in range(300):
            if len(spots) >= 4 or zone.is_empty:
                break
            p = Point(RNG.uniform(x0, x1), RNG.uniform(y0, y1))
            if zone.contains(p) and v["foot"].distance(p) > 2.0 and all(p.distance(q) > 5.0 for q in spots):
                spots.append(p)
        for k, p in enumerate(spots):
            put("olive" if k % 2 == 0 else "date", (p.x, p.y), v["zl"], RNG.uniform(0.65, 0.85))
        for t in np.linspace(0.15, 0.85, 4):                  # shrubs behind the low wall
            q = Point(v["w"](v["xe"] - 1.0, -2.0 + 24.0 * t))
            if lawn.buffer(-0.4).contains(q) and q.distance(Point(v["gate_c"])) > 2.0:
                put("shrub", (q.x, q.y), v["zl"], RNG.uniform(0.8, 1.0))
    # the passage between the second and the third lot: a paved footpath between two planted strips
    L.prism(mb_p, "t2_path", ppath, -0.65, PAVE_DZ, zf=hz)
    mb_l.build("T3_GROUND_GARDENS_LAWN", cols["T3_01_GROUND"], M)
    mb_p.build("T3_GROUND_PATHS", cols["T3_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_verge", strips, -0.65, 0.12, zf=hz)
    mb.build("T3_GROUND_VERGES", cols["T3_01_GROUND"], M)
    for g in L.as_polys(strips):                             # shrubs along each strip's axis, every 3.5 m
        r = np.array(g.minimum_rotated_rectangle.exterior.coords[:4])
        i = int(np.argmax([np.linalg.norm(r[(k + 1) % 4] - r[k]) for k in range(4)]))
        m0, m1 = (r[i] + r[(i + 3) % 4]) / 2, (r[(i + 1) % 4] + r[(i + 2) % 4]) / 2
        n = max(1, int(np.linalg.norm(m1 - m0) / 3.5))
        for k in range(n):
            p = Point(*(m0 + (m1 - m0) * (k + 0.5) / n))
            if g.buffer(-0.3).contains(p):
                put("shrub", (p.x, p.y), hz(p.x, p.y) + 0.12, RNG.uniform(0.8, 1.0))

    # ---- streets, pavements, kerbs, parking --------------------------------------------------------------
    kerb = pave.intersection(roads.union(parking).buffer(0.16, join_style=2))
    mb = C.MeshBuilder()
    L.prism(mb, "t2_road", roads, -0.65, 0.0, zf=hz)
    mb.build("T3_GROUND_ROADS", cols["T3_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_pave", pave.difference(kerb), -0.65, PAVE_DZ, zf=hz)
    mb.build("T3_GROUND_PAVEMENTS", cols["T3_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_kerb", kerb, -0.65, PAVE_DZ + 0.005, zf=hz)
    mb.build("T3_GROUND_KERBS", cols["T3_01_GROUND"], M)
    mb = C.MeshBuilder()
    L.prism(mb, "t2_parking", parking, -0.65, 0.0, zf=hz)
    mb.build("T3_GROUND_PARKING", cols["T3_01_GROUND"], M)
    mb = C.MeshBuilder()
    for ln in T3["bays"]:
        L.prism(mb, "paint", LineString(ln).buffer(0.03, cap_style=2), 0.004, 0.006, zf=hz, sides=False)
    mb.build("T3_ROAD_PAINT_PARKING", cols["T3_01_GROUND"], M)
    print(f"  T3: streets {roads.area:.0f} m2, pavements {pave.area:.0f} m2, parking {parking.area:.0f} m2 ({len(T3['bays'])} bay lines), "
          f"garden walls {high.area:.0f} m2 of plan, low walls {low.area:.0f} m2")

    # ---- the hotel (17_hotel, a design proposal) ------------------------------------------------------------
    n0 = nveg[0]
    obs, plants, (ho, hu, hv) = HO.build(M, cols["T3_05_HOTEL"], T3["hotel"], T3["frame"], hz, name="T3_HOTEL", lawn="t2_lawn")
    for kind, x, y, z, s in plants:
        put(kind, tuple(ho + hu * x + hv * y), z, s)
    print(f"  T3: hotel {len(obs)} objects, {nveg[0] - n0} plants; {nveg[0]} plants in the tranche")
    return cameras(hz, vs, (ho, hu, hv))


def cameras(hz, vs, hf):
    """Tranche 3's cameras: aerial, the hotel's gate on the Voie Publique, its water garden, the arm and the gate
    pavilion, the suites, a villa type A from street 7 and from its pool."""
    col = bpy.data.collections["07_CAMERAS"]
    ho, hu, hv = hf
    hw = lambda u, v: tuple(ho + hu * u + hv * v)
    va = vs[1]["w"]
    shots = {
        "T3_CAM_01_AERIAL": (hw(-80.0, -75.0), 60.0, hw(-15.0, -5.0), 0.0, 26),
        "T3_CAM_02_HOTEL_GATE": (hw(7.0, 62.0), 1.7, hw(7.05, 47.0), 6.0, 22),
        "T3_CAM_03_HOTEL_WATER_GARDEN": (hw(-18.5, 26.0), 1.7, hw(-18.5, -10.0), 1.2, 22),
        "T3_CAM_04_HOTEL_PAVILION": (hw(-20.5, -4.0), 1.7, hw(7.0, -4.0), 2.5, 22),
        "T3_CAM_05_HOTEL_SUITES": (hw(-30.0, -75.0), 6.0, hw(5.0, -35.0), 3.0, 24),
        "T3_CAM_06_VILLA_A_STREET": (va(vs[1]["xe"] + 6.0, 1.0), 1.7, va(17.0, vs[1]["gy"]), 2.2, 22),
        "T3_CAM_07_VILLA_A_POOL": (va(-8.6, -2.2), 1.7, va(4.0, 14.0), 2.0, 20),
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
