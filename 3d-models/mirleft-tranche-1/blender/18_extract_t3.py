"""
18_extract_t3 — Tranche 3 (the hotel and the villas type A) from the plan de masse of 31-05-13, written as
data/t3_site.json.

    python -I 18_extract_t3.py <plan_masse_31-05-13.pkl>

Client 23-10: "zid db had tranche kayn fiha hotel and villa type a" (the zone circled in blue on the plan,
west of the SPA and of the type C block). Read from the same flattened plan as 11_extract_t2, in the same
model frame (site.json "xf_2013"), and worked in the plan's own frame: e towards the plan's east, n towards
its north (the plan turned by -33.002 deg).

The plan's lines ('zoning' and '012', top level) are polygonised into cells, and the cells taken by where
they lie:
  - the four lots of the villas type A (25.5 x 34 m, west of street 7) and the passage between the second
    and the third (a footpath between two planted strips);
  - the hotel's plot between street 7 and the parking: its garden with the long pool and its arm, the
    two buildings' plots (north 15.5 x 47.7 m, south 14 x 57.7 m) and the crossing between them;
  - the two parking strips along the hotel's east side, their bays at 45 degrees as the plan's teeth draw
    them (2.5 m wide, one per tooth);
everything else of the tranche (between the lots' west line, Tranche 2 and the site's boundary) is street:
street 7 (6 m), the Voie Publique on the north and the south road along the boundary, each with the 0.40 m
of pavement along the fences as in Tranche 2.

The villas type A: the plan's drawing of the villa ('FGHF', four times, the same drawing moved along the
plan's north): the house round its patio, the pool, the terraces and the planters; written as each one's
origin (its outline's south-west corner) and the plan's turn, for 16_villa_a.
"""
import json
import math
import os
import pickle
import sys

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
site = json.load(open(os.path.join(ROOT, "data", "site.json")))
T2 = json.load(open(os.path.join(ROOT, "data", "t2_site.json")))
P = pickle.load(open(sys.argv[1], "rb"))
th = math.radians(site["xf_2013"]["theta_deg"])
T13, O = site["xf_2013"]["t"], site["origin_dwg"]
A_N = math.radians(90.0 + site["xf_2013"]["theta_deg"])          # the plan's north in the model frame
UN = np.array([math.cos(A_N), math.sin(A_N)])
UE = np.array([UN[1], -UN[0]])


def f13(p):
    x, y = p[0] - 47900.0, p[1] - 290320.0
    return (T13[0] + x * math.cos(th) - y * math.sin(th) - O[0], T13[1] + x * math.sin(th) + y * math.cos(th) - O[1])


def en(p):
    """model (x, y) -> plan frame (e, n)"""
    return (float(np.dot(p, UE)), float(np.dot(p, UN)))


def xy(p):
    """plan frame (e, n) -> model (x, y)"""
    return tuple(UE * p[0] + UN * p[1])


def to_en(g):
    return Polygon([en(p) for p in g.exterior.coords], [[en(p) for p in r.coords] for r in g.interiors]).buffer(0)


def to_xy(g):
    return unary_union([Polygon([xy(p) for p in q.exterior.coords], [[xy(p) for p in r.coords] for r in q.interiors])
                        for q in as_polys(g)]).buffer(0)


def as_polys(g):
    return [g] if g.geom_type == "Polygon" else [q for q in getattr(g, "geoms", []) if q.geom_type == "Polygon"]


def poly_out(g, nd=3):
    return [{"ext": [[round(x, nd), round(y, nd)] for x, y in q.exterior.coords[:-1]],
             "holes": [[[round(x, nd), round(y, nd)] for x, y in r.coords[:-1]] for r in q.interiors]}
            for q in as_polys(g) if q.area > 0.05]


P_ = lambda d: Polygon(d["ext"], d.get("holes", [])).buffer(0)

# ---- the plan's cells (its top-level 'zoning' and '012' lines), in the plan frame --------------------------
segs = []
for it in P:
    if it["layer"] not in ("zoning", "012") or it["k"] != "line" or len(it["pts"]) < 2:
        continue
    if it["path"] and it["path"][0] != "dfgedgr":
        continue
    q = [en(f13(p)) for p in it["pts"]]
    if not any(-430 < e < -310 and -95 < n < 65 for e, n in q):
        continue
    segs.append(LineString(q + ([q[0]] if it["closed"] else [])))
cells = [c for c in polygonize(unary_union(segs)) if c.area > 3.0]


def cell(e0, e1, n0, n1, amin, amax):
    """the cell whose representative point lies in the box, with its area in [amin, amax]"""
    got = [c for c in cells if e0 < c.representative_point().x < e1 and n0 < c.representative_point().y < n1 and amin < c.area < amax]
    assert len(got) == 1, (e0, e1, n0, n1, [round(c.area) for c in got])
    return got[0]


lots = [cell(-415, -379, n0, n1, 800, 950) for n0, n1 in ((22, 49), (-5, 23), (-45, -18), (-71, -44))]
passage = unary_union([c for c in cells if -415 < c.representative_point().x < -379 and -19.5 < c.representative_point().y < -4.0]).buffer(0)
garden = cell(-375, -342, -72, 45, 2000, 3000)
pool = cell(-368, -344, -39, 16, 400, 500)
bld_a = cell(-346, -330, -7, 42, 600, 700)
bld_b = cell(-345, -320, -72, -14, 800, 900)
cross = unary_union([cell(-345, -330, -13.5, -7.5, 60, 80), cell(-345, -330, -8.5, -6.0, 15, 25)])
park_n = cell(-346, -323, -14, 45, 300, 400)
park_s = cell(-345, -320, -72, -12, 280, 300)
plot = unary_union([garden, pool, bld_a, bld_b, cross]).buffer(0.01, join_style=2).buffer(-0.01, join_style=2)
# the rill: the narrow channel the garden's outline goes round (along street 7, with its inlet from it)
closed = plot.buffer(1.6, join_style=2).buffer(-1.6, join_style=2)
rill = unary_union([q for q in as_polys(closed.difference(plot)) if q.area > 10.0])
plot = unary_union([plot, rill])
print(f"lots {[round(l.area) for l in lots]} m2, passage {passage.area:.0f} m2, hotel plot {plot.area:.0f} m2 "
      f"(garden {garden.area:.0f}, pool {pool.area:.0f}, rill {rill.area:.0f}, buildings {bld_a.area:.0f} + {bld_b.area:.0f} m2)")

# ---- the tranche: the site west of Tranche 2, from the lots' west line --------------------------------------
site_en = to_en(Polygon(site["boundary"]))
t2_en = to_en(P_(T2["env"]))
t1_en = to_en(unary_union([P_(d) for d in site["t1_region"]]))
e_w = min(l.bounds[0] for l in lots)
env = site_en.intersection(box(e_w, -200, -200, 200)).difference(t2_en).difference(t1_en)
env = max(as_polys(env.buffer(0.05, join_style=2).buffer(-0.05, join_style=2)), key=lambda q: q.area)
env = env.intersection(box(e_w, -100, t2_en.bounds[0] + 40.0, 80))
parking = unary_union([park_n, park_s])

# the bays: one per tooth of the plan's zigzag (the bays' ends), their sides at the teeth's slant
bays = []
for band in (park_n, park_s):
    ring = [band.exterior.coords[0]]
    for p in band.exterior.coords[1:]:
        if math.dist(p, ring[-1]) > 0.05:
            ring.append(p)
    valleys = []
    for i in range(1, len(ring) - 1):
        a, b, c = np.array(ring[i - 1]), np.array(ring[i]), np.array(ring[i + 1])
        if np.linalg.norm(b - a) < 0.3 or np.linalg.norm(c - b) < 0.3:
            continue
        if b[0] < min(a[0], c[0]) - 0.8 and b[0] > band.bounds[0] + 2.0:      # a tooth's inner corner (west)
            valleys.append((b, c))
    for b, c in valleys:
        d = (b - c) / np.linalg.norm(b - c)                                  # along the tooth's long side, inwards
        bays.append(LineString([tuple(b + d * -0.2), tuple(b + d * 7.0)]).intersection(band))
bays = [g for g in bays if g.length > 1.5]
print(f"parking {parking.area:.0f} m2, {len(bays)} bay lines")

# ---- streets and pavements ---------------------------------------------------------------------------------
built = unary_union(lots + [passage, plot, parking])
roads = env.difference(built)
roads = unary_union([q for q in as_polys(roads.buffer(0)) if q.area > 2.0])
pave = unary_union([unary_union(lots).buffer(0.40, join_style=2), plot.buffer(0.40, join_style=2)]).intersection(roads)
roads = roads.difference(pave)
fill = env.difference(unary_union([built, roads, pave]))
roads = unary_union([roads] + [q for q in as_polys(fill) if q.area < 3.0])
path = unary_union([c for c in cells if c.within(passage.buffer(0.05)) and c.bounds[3] - c.bounds[1] > 1.95 and c.bounds[3] - c.bounds[1] < 4.2 and c.area < 120])
strips = passage.difference(path)
print(f"streets {roads.area:.0f} m2, pavements {pave.area:.0f} m2, passage path {path.area:.0f} m2 and planted strips {strips.area:.0f} m2")

# ---- the villas type A: the plan's drawing 'FGHF', four times ------------------------------------------------
blk = {}
for it in P:
    if it["path"] and it["path"][0] == "FGHF" and len(it["path"]) == 1 and it.get("iids") and it["k"] == "line" and len(it["pts"]) == 26:
        blk[it["iids"][0]] = np.array(it["pts"])[:, :2].min(0)
villas_a = []
for k, o in sorted(blk.items(), key=lambda kv: -kv[1][1]):
    org = f13(o)
    lot = min(lots, key=lambda l: l.distance(Point(en(org))))
    villas_a.append({"id": f"A-{len(villas_a) + 1:02d}", "origin": [round(org[0], 3), round(org[1], 3)],
                     "rot_deg": round(site["xf_2013"]["theta_deg"], 3), "garden": poly_out(to_xy(lot))[0]})
print("villas type A", len(villas_a), [v["origin"] for v in villas_a])

js = {"source": "plan de masse 31-05-13 (the hotel and the villas type A, west of the SPA), model frame of site.json",
      "frame": {"un": [round(float(UN[0]), 6), round(float(UN[1]), 6)], "ue": [round(float(UE[0]), 6), round(float(UE[1]), 6)]},
      "env": poly_out(to_xy(env))[0], "villas_a": villas_a,
      "roads": poly_out(to_xy(roads)), "pavements": poly_out(to_xy(pave)),
      "passage_path": poly_out(to_xy(path)), "passage_strips": poly_out(to_xy(strips)),
      "parking": poly_out(to_xy(parking)),
      "bays": [[[round(c, 3) for c in xy(p)] for p in g.coords] for g in bays if g.geom_type == "LineString"],
      "hotel": {"plot": poly_out(to_xy(plot))[0], "garden": poly_out(to_xy(garden))[0],
                "pool": poly_out(to_xy(pool))[0], "rill": poly_out(to_xy(rill)),
                "bld_a": poly_out(to_xy(bld_a))[0], "bld_b": poly_out(to_xy(bld_b))[0], "cross": poly_out(to_xy(cross))[0]}}
json.dump(js, open(os.path.join(ROOT, "data", "t3_site.json"), "w"))
print("written data/t3_site.json")
