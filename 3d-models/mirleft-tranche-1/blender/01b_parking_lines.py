"""
01b_parking_lines — the parking bays' separator lines of the plan de masse 12-10, added to data/site.json.

    python -I 01b_parking_lines.py <masse_12-10.pkl>

Input: the flattened DWG of 01_extract_site (tools/flatten.py). In the blocks 'PARKING 1 MIRLEFT' and
'PARKING 2 + PETANQUE' the bays are drawn as single 5 m lines ('-id-structure jardin') on the road, one
every 2.46 m. A line is a bay separator when it is 4.9-5.1 m long, lies on the road (not on the
pavements, lawns or kerbs round it) and has a parallel neighbour at a bay's width. Written as
site["parking_lines"]: [[x0, y0], [x1, y1]] in the model frame, painted by the scene (client 19-10).
"""
import json
import math
import os
import pickle
import sys

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_JSON = os.path.join(os.path.dirname(HERE), "data", "site.json")
O = (252000.0, 119430.0)
BLOCKS = ("PARKING 1 MIRLEFT", "PARKING 2 + PETANQUE")

P = pickle.load(open(sys.argv[1], "rb"))
site = json.load(open(SITE_JSON))
paved = unary_union([Polygon(p["ext"], p["holes"]).buffer(0) for k in ("lawn", "concrete", "paving", "stabilise")
                     for p in site["surfaces"].get(k, [])]).buffer(-0.05)

cand = []
for p in P:
    if not (p["path"] and p["path"][0] in BLOCKS and p["k"] == "line" and p["layer"] == "-id-structure jardin" and len(p["pts"]) == 2):
        continue
    a, b = [(q[0] - O[0], q[1] - O[1]) for q in p["pts"]]
    ls = LineString([a, b])
    if not 4.9 <= ls.length <= 5.1 or ls.intersection(paved).length > 0.1:
        continue
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    if all(math.dist(m, c[2]) > 0.10 for c in cand):          # the plan draws some twice
        cand.append((a, b, m))


def unit(a, b):
    L = math.dist(a, b)
    return ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


lines = []
for a, b, m in cand:
    u = unit(a, b)
    for a2, b2, m2 in cand:
        if m2 is m:
            continue
        u2 = unit(a2, b2)
        if abs(u[0] * u2[1] - u[1] * u2[0]) > 0.02:             # not parallel
            continue
        d = (m2[0] - m[0], m2[1] - m[1])
        along, across = d[0] * u[0] + d[1] * u[1], abs(d[0] * u[1] - d[1] * u[0])
        if abs(along) < 0.6 and 2.2 < across < 2.8:              # a bay's width away
            lines.append([[round(v, 3) for v in a], [round(v, 3) for v in b]])
            break
site["parking_lines"] = lines
json.dump(site, open(SITE_JSON, "w"))
print("parking bay lines:", len(lines))
