"""
11_extract_t2 — Tranche 2 (villas type B) from the plan de masse of 31-05-13, written as data/t2_site.json.

    python -I 11_extract_t2.py <plan_masse_31-05-13.pkl>

Input: the 2013 plan flattened by tools/flatten.py (primitives with their block paths), in 2013 DWG
coordinates. It is brought into the model frame with the transform of site.json ("xf_2013": 2013 local
= DWG - (47900, 290320), turned by -33.002 deg onto the 12-10 plan), the one the contours already use.

Tranche 2 is every villa type B of the plan, the two blocks west of Tranche 1 the client circled (21-10:
"block by block, by villa type"): the northern block along the Voie Publique (21 lots, three rows of seven)
and the southern block (12 lots, one drawn empty on the 2013 plan; the client's plan shows a villa there,
so it gets one). A lot is a cell of the plan's lot lines ('zoning', on the centre lines of the lanes)
holding a type B drawing, or one of the lots the plan colours for that block; the fenced plot of each
villa is read from the plan's lines ('012' fences, house outlines 'cadastre', pools 'Nouveau calque 11')
as the part of the lot the lanes do not reach. The three small lots of the southern block along the
south road are a planted square, a lawn and the angled parking bays the plan draws there.

Villa placement: the plan's own type B drawing in each lot gives the side of the pool (rear) and the
house (front); the villa type B model (12_villa_b.py, local x 0-12.20 across, y 0.40-20.10 from the pool
to the street) is set in the plot with its street side on the plot's front edge, centred across. Where
the plan's plot is too short for it (see below) the villa is turned a quarter onto its street. Each
villa's garden is its plot with the model's plot box; the streets keep a 1.50 m pavement along the
garden walls, a 2 m walk along the square.
"""
import json
import math
import os
import pickle
import sys
from collections import Counter

import cv2
import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
site = json.load(open(os.path.join(ROOT, "data", "site.json")))
P = pickle.load(open(sys.argv[1], "rb"))
th = math.radians(site["xf_2013"]["theta_deg"])
T13, O = site["xf_2013"]["t"], site["origin_dwg"]


def f13(p):
    x, y = p[0] - 47900.0, p[1] - 290320.0
    return (T13[0] + x * math.cos(th) - y * math.sin(th) - O[0], T13[1] + x * math.sin(th) + y * math.cos(th) - O[1])


X0, Y0, X1, Y1, RES = -270.0, -60.0, -5.0, 200.0, 10.0
W, H = int((X1 - X0) * RES), int((Y1 - Y0) * RES)


def px(q):
    return (int(round((q[0] - X0) * RES)), int(round((Y1 - q[1]) * RES)))


def raster(test):
    img = np.zeros((H, W), np.uint8)
    for it in P:
        if it["k"] not in ("line", "hatch") or not test(it):
            continue
        q = [px(f13(v)) for v in it["pts"]]
        if it["k"] == "hatch" or it["closed"]:
            q = q + [q[0]]
        if len(q) > 1:
            cv2.polylines(img, [np.array(q, np.int32)], False, 255, 1)
    img = cv2.dilate(img, np.ones((3, 3), np.uint8))
    return cv2.connectedComponentsWithStats((img == 0).astype(np.uint8), connectivity=4)


def vec(mask):
    cs, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    if hier is None:
        return Polygon()
    for k, c in enumerate(cs):
        if hier[0][k][3] != -1 or len(c) < 3:
            continue
        out.append(Polygon([(X0 + (x + 0.5) / RES, Y1 - (y + 0.5) / RES) for x, y in c[:, 0, :]]).buffer(0))
    return unary_union(out)


def as_polys(g):
    return [g] if g.geom_type == "Polygon" else [q for q in getattr(g, "geoms", []) if q.geom_type == "Polygon"]


def poly_out(g, nd=3):
    return [{"ext": [[round(x, nd), round(y, nd)] for x, y in q.exterior.coords[:-1]],
             "holes": [[[round(x, nd), round(y, nd)] for x, y in r.coords[:-1]] for r in q.interiors]}
            for q in as_polys(g) if q.area > 0.05]


# ---- the plan's type B drawings: pool water ('09-Eau', rear), entrance skylight ('ArchiCAD' hatch, front)
# and stair ('Menuiserie Bois', front, on the model's +x side of the pool) in each lot -------------------
VB = ("tyiurtyir", "rèyr(è-", "hjutfy")
marks = {"pool": [], "sky": [], "stair": []}
for it in P:
    if not it["path"] or it["path"][0] not in VB:
        continue
    key = {("09-Eau", "hatch"): "pool", ("ArchiCAD", "hatch"): "sky", ("Menuiserie Bois", "line"): "stair"}.get((it["layer"], it["k"]))
    if key:
        marks[key] += [f13(p) for p in it["pts"]]
marks = {k: np.array(v) for k, v in marks.items()}


# ---- lots: cells of the plan's lot lines, green and cyan ------------------------------------------
GREEN, CYAN = (0, 255, 0), (0, 255, 255)
nz, labz, stz, _ = raster(lambda it: it["layer"] == "zoning")
ZL = [(tuple(it["rgb"]), LineString([f13(p) for p in it["pts"]] + ([f13(it["pts"][0])] if it["closed"] else [])))
      for it in P if it["layer"] == "zoning" and len(it["pts"]) > 1]
lots = []
for i in range(1, nz):
    if not 250 < stz[i, 4] / RES / RES < 800:
        continue
    g = vec(labz == i).buffer(0.15, join_style=2).simplify(0.1)
    votes = Counter(min(ZL, key=lambda c: c[1].distance(g.exterior.interpolate(k / 60, normalized=True)))[0] for k in range(60))
    col = votes.most_common(1)[0][0]
    inner = g.buffer(-0.5)
    drawn_b = any(inner.contains(Point(q)) for q in marks["pool"])
    if col in (GREEN, CYAN) or drawn_b:                       # client 21-10: every type B lot of the plan
        lots.append({"block": "south" if col == CYAN else "north", "lot": g})
print("lots", Counter(l["block"] for l in lots))

# ---- fenced plots: the regions of the plan's lines that lie inside one lot -------------------------
SKIPB = {"COUPE_SPORT_3_65_32", "fds", "hjftyuitr"}            # figures, furniture
LAY = {"012", "041_rue chemin chaussee", "cadastre", "Nouveau calque 11", "zoning"}
n, lab, st, _ = raster(lambda it: it["layer"] in LAY and not (it["path"] and it["path"][0] in SKIPB)
                       and not (it["layer"] == "012" and len(it["pts"]) == 42 and it["closed"]))
for l in lots:
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array([px(v) for v in l["lot"].buffer(0.3).exterior.coords], np.int32)], 1)
    inside = np.bincount(lab.ravel(), weights=m.ravel().astype(float), minlength=n)
    ids = [i for i in range(1, n) if inside[i] >= 0.98 * st[i, 4] and st[i, 4] >= RES * RES * 0.2]
    plot = vec(np.isin(lab, ids)).buffer(0.25, join_style=2).buffer(-0.25, join_style=2)
    plot = max(as_polys(plot), key=lambda q: q.area)
    l["plot"] = Polygon(plot.exterior).simplify(0.15)



def rect_axes(g):
    r = list(g.minimum_rotated_rectangle.exterior.coords)
    e = [(np.array(r[k + 1]) - np.array(r[k])) for k in range(2)]
    return [v / np.linalg.norm(v) for v in e]


villas, extra = [], []
for l in lots:
    plot, lot = l["plot"], l["lot"]
    if lot.area < 340 and l["block"] == "south":              # the three small lots on the south road
        extra.append(l)
        continue
    if plot.area < 280:                                       # fence lines not closed on the plan
        l["plot"] = plot = lot.buffer(-2.6, join_style=2)
    inner = lot.buffer(-0.5)
    m = {k: np.array([q for q in v if inner.contains(Point(q))]) for k, v in marks.items()}
    l["drawn"] = all(len(v) for v in m.values())
    if l["drawn"]:
        pool, sky, stair = (m[k].mean(0) for k in ("pool", "sky", "stair"))
        l["fwd"] = (sky - pool) / np.linalg.norm(sky - pool)
        l["side"] = stair - pool
    villas.append(l)
for l in villas:                                              # the empty lot takes its neighbour's layout
    if not l["drawn"]:
        nb = min((v for v in villas if v["drawn"] and v["block"] == l["block"]), key=lambda v: v["plot"].distance(l["plot"]))
        l["fwd"], l["side"] = nb["fwd"], nb["side"]

# ---- the envelope of Tranche 2 and its small lots ---------------------------------------------------
boundary = Polygon(site["boundary"]).buffer(0)
t1 = unary_union([Polygon(r["ext"], r.get("holes", [])) for r in (site["t1_region"] if isinstance(site["t1_region"], list) else [site["t1_region"]])]).buffer(0)
all_lots = unary_union([l["lot"] for l in lots])
env = all_lots.buffer(3.5, join_style=2).intersection(boundary).difference(t1)   # the lot lines run on the road centres
env = unary_union([env, t1]).buffer(2.0, join_style=2).buffer(-2.0, join_style=2).difference(t1).intersection(boundary)
env = max(as_polys(env), key=lambda q: q.area)
# the zoning cells end in thin spikes where their lines overrun: cut them off the envelope (pieces an
# opening of 4 m removes, away from Tranche 1)
spikes = [q for q in as_polys(env.difference(env.buffer(-4.0).buffer(4.0))) if q.area < 80 and q.distance(t1) > 0.5]
env = env.difference(unary_union(spikes)).buffer(-0.05, join_style=2).buffer(0.05, join_style=2)   # and the 0-width ones
env = Polygon(max(as_polys(env), key=lambda q: q.area).exterior)                                     # no holes
print("envelope spikes cut:", len(spikes))
extra.sort(key=lambda l: l["plot"].centroid.x)
small = {}
for l in extra:
    zig = l["plot"].area < 110                                # the angled bays (saw-tooth kerb on the plan)
    small.setdefault("parking" if zig else "green", []).append(l["lot"].intersection(env))
smalls = unary_union(sum(small.values(), []))

# ---- villas on their plots -------------------------------------------------------------------------
NEED = 19.75      # the model from its pool's coping (local y 0.65) to its street front (20.10), and 0.30 to the fence
out = []
for l in villas:
    plot = l["plot"]
    axes = rect_axes(plot)
    k = max(range(2), key=lambda j: abs(float(np.dot(axes[j], l["fwd"]))))
    v = axes[k] * np.sign(np.dot(axes[k], l["fwd"]))           # rear (pool) -> street, as the plan draws it
    u = np.array([v[1], -v[0]])                                # right of v
    out.append({"block": l["block"], "lot": l["lot"], "plot": plot, "v": v, "u": u, "drawn": l["drawn"],
                "mirror": bool(np.dot(u, l["side"]) < 0),      # the model's stair is on +x of its pool
                "c": np.array(plot.minimum_rotated_rectangle.centroid.coords[0])})
plots_all = unary_union([o["plot"] for o in out])


def extents(o, u, v):
    proj = [(float(np.dot(np.array(q) - o["c"], u)), float(np.dot(np.array(q) - o["c"], v))) for q in o["plot"].exterior.coords]
    return min(a for a, _ in proj), max(a for a, _ in proj), min(b for _, b in proj), max(b for _, b in proj)


# The plan's drawings put some villas back to front in a row, on plots too short for the model with its
# pool (the southern block: its two southern rows and the two small lots of its northern row). Those are
# turned a quarter (client 21-10: "be creative"), their street fronts on the plots' long sides: the
# northern row onto the street between it and the middle row, the middle row onto that street too, the
# southern row onto the square and the road along it, so the middle and southern rows' pools are back to
# back across their shared line. The house against one side of its plot, the side garden on the salon
# marocain's side, the mirrored model every other plot of a row
turned = [o for o in out if extents(o, o["u"], o["v"])[3] - extents(o, o["u"], o["v"])[2] < NEED]
for o in out:
    o["turned"] = o in turned
if turned:
    u0 = turned[0]["u"]
    turned.sort(key=lambda o: float(np.dot(o["c"], u0)))
    rows, r = [[turned[0]]], 0
    for o in turned[1:]:
        if float(np.dot(o["c"] - rows[-1][-1]["c"], u0)) > 10.0:
            rows.append([])
        rows[-1].append(o)
    for r, row in enumerate(rows):                            # u0 runs south-south-west: row 0 is the northern one
        f = u0 if r % 2 == 0 else -u0
        row.sort(key=lambda o: float(np.dot(o["c"], [f[1], -f[0]])))
        for i, o in enumerate(row):
            o["v"], o["u"], o["mirror"] = f, np.array([f[1], -f[0]]), i % 2 == 1
for o in out:
    u, v = o["u"], o["v"]
    umin, umax, vmin, vmax = extents(o, u, v)
    front = vmax - 0.30
    over = NEED - (vmax - vmin)
    if o["turned"] and over > 0:                              # small lots: over the pavements, the rear one first
        front += max(0.0, over - 1.5)
    if o["turned"]:
        x0 = umax - 12.20 if o["mirror"] else umin            # the house against one side
    else:
        x0 = 0.5 * (umin + umax) - 6.10                       # centred across the plot
    # model origin: local x along u, local y along v, y 20.10 on the street front (the mirrored model is
    # mirrored across its own plot box, so it is placed the same way)
    o["origin"] = o["c"] + u * x0 + v * (front - 20.10)
    o["rot"] = math.degrees(math.atan2(u[1], u[0]))
print("villas turned a quarter onto their street:", sum(o["turned"] for o in out))


def world_box(o, g):
    from shapely import affinity
    return affinity.translate(affinity.rotate(g, o["rot"], origin=(0, 0), use_radians=False), *o["origin"])


# ---- gardens: the plot and the model's own plot box (the box wins over the neighbours' plots) ---------
for o in out:
    o["box"] = world_box(o, box(0.0, 0.40, 12.20, 20.10))
boxes = [o["box"] for o in out]
for i, a in enumerate(boxes):
    for b in boxes[i + 1:]:
        if a.intersection(b).area > 0.05:
            print("  WARNING villa boxes overlap", round(a.intersection(b).area, 2))
taken = Polygon()
for o in out:                                                 # the plots' outlines squared (spikes of the hatches off)
    o["plot"] = Polygon(max(as_polys(o["plot"].buffer(-1.0, join_style=2).buffer(1.0, join_style=2)), key=lambda q: q.area).exterior)
for i, o in enumerate(out):
    g = unary_union([o["plot"], o["box"]]).buffer(2.5, join_style=2).buffer(-2.5, join_style=2)     # notches of the hatches filled
    g = g.difference(unary_union(boxes[:i] + boxes[i + 1:])).intersection(env).difference(taken)
    g = g.buffer(-0.3, join_style=2).buffer(0.3, join_style=2)
    o["garden"] = Polygon(max(as_polys(g), key=lambda q: q.area).exterior)
    taken = taken.union(o["garden"])

# numbering: the northern block then the southern one, rows from the north
out.sort(key=lambda o: (o["block"] != "north", -round(o["c"][1] / 12.0), o["c"][0]))
villas_js = []
for i, o in enumerate(out, 1):
    villas_js.append({"id": f"B-{i:02d}", "block": o["block"], "origin": [round(float(x), 3) for x in o["origin"]],
                      "rot_deg": round(o["rot"], 3), "mirror": bool(o["mirror"]), "turned": bool(o["turned"]),
                      "drawn_on_plan": o["drawn"], "plot": poly_out(o["plot"])[0], "garden": poly_out(o["garden"])[0],
                      "lot": poly_out(o["lot"])[0]})
print("villas", len(villas_js), "mirrored", sum(v["mirror"] for v in villas_js), "drawn", sum(v["drawn_on_plan"] for v in villas_js))

# ---- public realm: the streets with their pavements round the gardens, the small lots ----------------
gardens = unary_union([o["garden"] for o in out])
public = env.difference(gardens).difference(smalls)
pave = public.intersection(gardens.buffer(1.50, join_style=2))  # 1.50 m pavement along the garden walls
walk = smalls.difference(gardens).intersection(gardens.buffer(2.0, join_style=2))   # and a 2 m walk along the square
pave = unary_union([pave, walk])
smalls_left = {k: unary_union(v).difference(gardens).difference(walk) for k, v in small.items()}
roads = public.difference(pave)
islands = [q for q in as_polys(roads) if q.area < 60.0]          # bits of road shut in by the gardens: paved
pave, roads = unary_union([pave] + islands), roads.difference(unary_union(islands)) if islands else roads

js = {"source": "plan de masse 31-05-13 (villas type B west of Tranche 1), model frame of site.json",
      "env": poly_out(env)[0], "villas": villas_js,
      "roads": poly_out(roads), "pavements": poly_out(pave),
      "greens": poly_out(smalls_left.get("green", Polygon())),
      "parking": poly_out(smalls_left.get("parking", Polygon()))}
json.dump(js, open(os.path.join(ROOT, "data", "t2_site.json"), "w"))
for k in ("roads", "pavements", "greens", "parking"):
    print(f"  {k:10s} {sum(Polygon(p['ext'], p['holes']).area for p in js[k]):8.1f} m2")
print("env", round(env.area), "m2")
