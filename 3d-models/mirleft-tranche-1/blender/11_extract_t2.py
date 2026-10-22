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
villa is the region of the plan's own lines (its top-level fences, kerbs and buildings) inside the lot.

Villa placement: the plan's own type B drawing in each lot gives the side of the pool (rear), of the house
(front) and of the stair (mirror); the villa type B model (12_villa_b.py, local x 0-12.20 across, y
0.40-20.10 from the pool to the front) is set with its house where the plan's house is and its front
0.18 m inside the plot's front fence; where the plot is shorter than the model with its pool, the compact
model (pool 1.50 m nearer the house, as the plan draws it). Each villa's garden is its plot.

The rest of the works (the blocks, and the streets round them the client marked in yellow, 21-10) is read
from the same lines, with the plan's widths (client 22-10): the zoning lines are the kerbs of the main
streets, so everything between them is carriageway (Voie Publique and south road 8 m inside a 1.6-2.9 m
verge, the street along Tranche 1 6.06 m, the streets between the blocks 5.1-6 m); the lanes inside the
blocks are the ground between facing gardens (5 m between kerbs 0.40 m off the fences); the plan's narrow
strips are pavements and its wide ones off the street planted strips. The street along Tranche 1 runs over
Tranche 1's west pavement south of where its east kerb leaves Tranche 1's limit: that pavement is cut away
under it (t1_trim, not built by 05). The bays along the south road are parking, and the three squares with
hipped roofs on the parking strip the 'Centre d'entretien' (twice) and the 'Office' of the plan's labels.
The pieces lying on the type C villas' lots are left out. T2_DEBUG=<png> writes the class map.
"""
import json
import math
import os
import pickle
import sys
from collections import Counter

import cv2
import numpy as np
from scipy import ndimage
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


def vec(mask, holes=False):
    cs, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    if hier is None:
        return Polygon()
    xy = lambda c: [(X0 + (x + 0.5) / RES, Y1 - (y + 0.5) / RES) for x, y in c[:, 0, :]]
    for k, c in enumerate(cs):
        if hier[0][k][3] != -1 or len(c) < 3:
            continue
        hs, ch = [], hier[0][k][2]
        while holes and ch != -1:
            if len(cs[ch]) >= 3:
                hs.append(xy(cs[ch]))
            ch = hier[0][ch][0]
        out.append(Polygon(xy(c), hs).buffer(0))
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
marks = {"pool": [], "sky": [], "stair": [], "house": []}
for it in P:
    if not it["path"] or it["path"][0] not in VB:
        continue
    key = {("09-Eau", "hatch"): "pool", ("ArchiCAD", "hatch"): "sky", ("Menuiserie Bois", "line"): "stair",
           ("cadastre", "line"): "house"}.get((it["layer"], it["k"]))
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


# ---- the works of Tranche 2: its two blocks, and the streets round them the client marked in yellow on the
# plan (21-10): the Voie Publique along the north boundary, the street between Tranche 2 and Tranche 1, the
# south road along the boundary from the west end of the type C villas, with its parking and buildings ---
boundary = Polygon(site["boundary"]).buffer(0)
t1 = unary_union([Polygon(r["ext"], r.get("holes", [])) for r in (site["t1_region"] if isinstance(site["t1_region"], list) else [site["t1_region"]])]).buffer(0)
all_lots = unary_union([l["lot"] for l in lots])
blocks = all_lots.buffer(3.5, join_style=2).intersection(boundary).difference(t1)   # the lot lines run on the road centres
blocks = unary_union([blocks, t1]).buffer(2.0, join_style=2).buffer(-2.0, join_style=2).difference(t1).intersection(boundary)
blocks = max(as_polys(blocks), key=lambda q: q.area)
spikes = [q for q in as_polys(blocks.difference(blocks.buffer(-4.0).buffer(4.0))) if q.area < 80 and q.distance(t1) > 0.5]
blocks = blocks.difference(unary_union(spikes)).buffer(-0.05, join_style=2).buffer(0.05, join_style=2)
blocks = Polygon(max(as_polys(blocks), key=lambda q: q.area).exterior)
B_NORTH = [(-272.1, 240.0), (-142.0, 162.8), (-19.9, 84.8)]           # site boundary, north
T1_WEST = [(-125.8, -29.1), (-42.5, 99.3)]                             # Tranche 1's west limit
B_SOUTH = [(-309.2, 110.8), (-249.7, 73.1), (-232.6, 46.9), (-185.0, -12.0), (-134.3, -29.9), (-125.8, -29.1)]
# the south road is 15 m wide inside the boundary along the type C villas (verge, kerb, 8 m carriageway,
# pavement, up to their fences) and 26 m along the southern block, where the parking strip lies beside it
corridors = unary_union([LineString(B_NORTH).buffer(22.0).intersection(box(-252.0, -100.0, 0.0, 300.0)),
                         LineString(T1_WEST).buffer(24.0), LineString(B_SOUTH[:4]).buffer(15.0, cap_style=2),
                         LineString([(-205.0, 12.0)] + B_SOUTH[3:]).buffer(26.0)])
works = unary_union([blocks, corridors]).intersection(boundary).difference(t1)
works = max(as_polys(works), key=lambda q: q.area)
# client 22-10: the street along Tranche 1 as the plan draws it, 6.06 m between its two zoning lines down to
# the south road. Its east kerb meets Tranche 1's limit 55 m up it; south of there it runs over Tranche 1's
# west pavement, which is cut away under it ("ida bghit dmsa7 trotoire dyal tranche 1 chi chwiya")
zstreet = unary_union([vec(labz == i, holes=True) for i in range(1, nz) if stz[i, 4] / RES / RES > 1500.0])
dT, oT = np.array([0.544, 0.839]), np.array(T1_WEST[0])     # along Tranche 1's limit, and across it into Tranche 1
nT = np.array([dT[1], -dT[0]])
band = Polygon([tuple(oT + dT * t + nT * s) for t, s in ((-15.0, -3.0), (60.0, -3.0), (60.0, 7.0), (16.0, 7.0), (16.0, 16.0), (-15.0, 16.0))])
t1_trim = zstreet.intersection(t1).intersection(band).buffer(-0.05, join_style=2).buffer(0.05, join_style=2)
t1_trim = unary_union([q for q in as_polys(t1_trim) if q.area > 2.0])
# what that leaves of the pavement between the street and Tranche 1's own road where it is under 1.5 m
# wide (and its tail at the south road) goes too: the two carriageways meet there, no sliver of kerb
t1pav = unary_union([Polygon(p["ext"], p.get("holes", [])).buffer(0) for p in site["surfaces"].get("paving", [])])
rem = t1pav.intersection(t1).intersection(band).difference(t1_trim)
thin = rem.difference(rem.buffer(-0.75, join_style=2).buffer(0.75, join_style=2))
thin = unary_union([q for q in as_polys(thin) if q.distance(t1_trim) < 0.05])
t1_trim = unary_union([t1_trim, thin]).buffer(0.10, join_style=2).buffer(-0.10, join_style=2).intersection(t1)
t1_trim = unary_union([q for q in as_polys(t1_trim.simplify(0.05)) if q.area > 2.0])
print(f"Tranche 1 ground under the street along it: {t1_trim.area:.0f} m2")
# the main streets round the blocks in full, to their far kerb and 1 m past it (client 22-10: the street "6"
# down the west side of the southern block, between it and the type C villas, is 6 m between its kerbs)
side = zstreet.intersection(blocks.buffer(9.0, join_style=2)).buffer(1.0, join_style=2).intersection(boundary).difference(t1)
works = max(as_polys(unary_union([works, side, t1_trim]).buffer(0.01, join_style=2).buffer(-0.01, join_style=2)), key=lambda q: q.area)

# ---- the plan's ground pieces: its top-level lines (fences, kerbs, buildings: '012', 'cadastre', the
# '041' chemin) and the site boundary drawn at 10 px/m; every region they enclose in the works is one piece
RG = 10.0
gx0, gy0, gx1, gy1 = (b + d for b, d in zip(works.bounds, (-2.0, -2.0, 2.0, 2.0)))
GW, GH = int((gx1 - gx0) * RG), int((gy1 - gy0) * RG)


def gpx(q):
    return (int(round((q[0] - gx0) * RG)), int(round((gy1 - q[1]) * RG)))


def gfill(g, val=1, img=None):
    img = np.zeros((GH, GW), np.uint8) if img is None else img
    for q in as_polys(g):
        cv2.fillPoly(img, [np.array([gpx(v) for v in q.exterior.coords], np.int32)], val)
        for r in q.interiors:
            cv2.fillPoly(img, [np.array([gpx(v) for v in r.coords], np.int32)], 0)
    return img


def gvec(mask, tol=0.08):
    cs, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    if hier is None:
        return Polygon()
    for k, c in enumerate(cs):
        if hier[0][k][3] != -1 or len(c) < 3:
            continue
        holes = []
        ch = hier[0][k][2]
        while ch != -1:
            if len(cs[ch]) >= 3:
                holes.append([(gx0 + (x + 0.5) / RG, gy1 - (y + 0.5) / RG) for x, y in cs[ch][:, 0, :]])
            ch = hier[0][ch][0]
        out.append(Polygon([(gx0 + (x + 0.5) / RG, gy1 - (y + 0.5) / RG) for x, y in c[:, 0, :]], holes).buffer(0))
    return unary_union(out).simplify(tol)


lines = np.zeros((GH, GW), np.uint8)
for it in P:
    if it["k"] != "line" or it["path"] or it["layer"] not in ("012", "cadastre", "041_rue chemin chaussee") or len(it["pts"]) < 2:
        continue
    q = [gpx(f13(v)) for v in it["pts"]] + ([gpx(f13(it["pts"][0]))] if it["closed"] else [])
    cv2.polylines(lines, [np.array(q, np.int32)], False, 255, 1)
bq = [gpx(v) for v in site["boundary"]]
cv2.polylines(lines, [np.array(bq + [bq[0]], np.int32)], False, 255, 1)
lines = cv2.dilate(lines, np.ones((3, 3), np.uint8))
mW = gfill(works)
ncomp, lab, stc, _ = cv2.connectedComponentsWithStats(((lines == 0) & (mW > 0)).astype(np.uint8), connectivity=4)
csize = stc[:, 4] / RG / RG


cwide = 2.0 * ndimage.maximum(cv2.distanceTransform((lab > 0).astype(np.uint8), cv2.DIST_L2, 5), lab, index=np.arange(ncomp)) / RG


def comps_in(g, frac):
    """the plan's regions inside g, but not its pavement strips (under 2.3 m across), which it cuts at the lots"""
    m = gfill(g)
    inside = np.bincount(lab.ravel(), weights=m.ravel().astype(float), minlength=ncomp)
    return [i for i in range(1, ncomp) if inside[i] >= frac * stc[i, 4] and csize[i] >= 1.0 and cwide[i] >= 2.3]


# ---- villas: the plot of each lot is the region (or regions) of the plan's lines inside it -----------
def rect_axes(g):
    r = list(g.minimum_rotated_rectangle.exterior.coords)
    e = [(np.array(r[k + 1]) - np.array(r[k])) for k in range(2)]
    return [v / np.linalg.norm(v) for v in e]


villas = []
for l in lots:
    lot = l["lot"]
    if lot.area < 340 and l["block"] == "south":              # the three small lots on the south road: parking
        continue
    ids = comps_in(lot.buffer(0.6), 0.7)
    plot = gvec(np.isin(lab, ids)).buffer(0.3, join_style=2).buffer(-0.3, join_style=2) if ids else Polygon()
    plot = Polygon(max(as_polys(plot), key=lambda q: q.area).exterior) if not plot.is_empty else Polygon()
    l["plot"] = plot
    inner = lot.buffer(-0.5)
    m = {k: np.array([q for q in v if inner.contains(Point(q))]) for k, v in marks.items()}
    l["drawn"] = all(len(m[k]) for k in ("pool", "sky", "stair"))
    if l["drawn"]:
        pool, sky, stair = (m[k].mean(0) for k in ("pool", "sky", "stair"))
        l["fwd"] = (sky - pool) / np.linalg.norm(sky - pool)
        l["side"] = stair - pool
        l["house"] = m["house"]
    villas.append(l)
from shapely import affinity
good = [v for v in villas if v["plot"].area >= 250]
for l in villas:                                              # fence lines not closed on the plan: the outline of the
    if l["plot"].area < 250:                                  # nearest plot of the block, moved onto this lot
        nb = min((v for v in good if v["block"] == l["block"]), key=lambda v: v["lot"].distance(l["lot"]))
        d = np.array(l["lot"].centroid.coords[0]) - np.array(nb["lot"].centroid.coords[0])
        l["plot"] = affinity.translate(nb["plot"], *d).intersection(l["lot"].buffer(0.5))
        print("  plot of the lot at", [round(float(x), 1) for x in l["lot"].centroid.coords[0]], "from its neighbour's")
for l in villas:                                              # the empty lot takes its neighbour's layout
    if not l["drawn"]:
        nb = min((v for v in villas if v["drawn"] and v["block"] == l["block"]), key=lambda v: v["plot"].distance(l["plot"]))
        l["fwd"], l["side"] = nb["fwd"], nb["side"]
print("villas", len(villas), "drawn", sum(l["drawn"] for l in villas))

# Placement as the plan draws each villa: pool at the rear, its house across where the plan's house is,
# its street front 0.25 m inside the plot's front fence (or, on the long plots at the ends of the rows, as
# far from the house as the plan draws it). Where the plot is shorter than the model with its pool
# (19.45 m from the pool's coping to the front), the compact model of 12_villa_b (the pool 1.50 m nearer
# the house, 1 m from it as the plan draws it) is used.
NEED, NEED_C = 19.45, 17.95
out = []
for l in villas:
    plot = l["plot"]
    axes = rect_axes(plot)
    k = max(range(2), key=lambda j: abs(float(np.dot(axes[j], l["fwd"]))))
    v = axes[k] * np.sign(np.dot(axes[k], l["fwd"]))           # rear (pool) -> front, as the plan draws it
    u = np.array([v[1], -v[0]])                                # right of v
    mirror = bool(np.dot(u, l["side"]) < 0)                    # the model's stair is on +x of its pool
    c = np.array(plot.minimum_rotated_rectangle.centroid.coords[0])
    pr = [(float(np.dot(np.array(q) - c, u)), float(np.dot(np.array(q) - c, v))) for q in plot.exterior.coords]
    umin, umax = min(a for a, _ in pr), max(a for a, _ in pr)
    vmin, vmax = min(b for _, b in pr), max(b for _, b in pr)
    front = vmax - 0.18
    if l["drawn"] and len(l["house"]):
        hu = (l["house"] - c) @ u
        hv = (l["house"] - c) @ v
        front = min(front, float(hv.max()) + 1.75)
        x0 = float(hu.min()) + (0.02 if mirror else -1.03)     # the model's house (x 1.03-12.22) on the plan's
    else:
        x0 = 0.5 * (umin + umax) - 6.10
    compact = front - vmin < NEED + 0.18
    if front - vmin < (NEED_C if compact else NEED) + 0.15:
        print("  WARNING villa longer than its plot by", round((NEED_C if compact else NEED) + 0.15 - (front - vmin), 2))
    origin = c + u * x0 + v * (front - 20.10)
    out.append({"block": l["block"], "lot": l["lot"], "plot": plot, "origin": origin, "u": u, "v": v,
                "rot": math.degrees(math.atan2(u[1], u[0])), "mirror": mirror, "compact": bool(compact),
                "drawn": l["drawn"], "c": c})
print("compact villas:", sum(o["compact"] for o in out))


def world_box(o, g):
    from shapely import affinity
    return affinity.translate(affinity.rotate(g, o["rot"], origin=(0, 0)), *o["origin"])


# gardens: the plot, and the model's own plot box where it reaches past it (the box wins over neighbours)
kerbs = zstreet.buffer(0.40, join_style=2)          # the main streets with the 0.40 m to the fences
for o in out:
    o["box"] = world_box(o, box(0.0, 1.90 if o["compact"] else 0.40, 12.20, 20.10))
for o in out:
    others = unary_union([q["box"] for q in out if q is not o])
    if o["box"].intersection(zstreet).area > 0.02:   # a villa over a street's kerb line: moved off it
        for d in np.arange(0.05, 1.55, 0.05):
            mv = [k for k in (o["u"], -o["u"], o["v"], -o["v"])
                  if affinity.translate(o["box"], *(k * d)).intersection(zstreet).area < 0.02
                  and affinity.translate(o["box"], *(k * d)).intersection(others).area < 0.05]
            if mv:
                o["origin"] = o["origin"] + mv[0] * d
                o["box"] = affinity.translate(o["box"], *(mv[0] * d))
                print(f"  villa at {[round(float(x), 1) for x in o['c']]} moved {d:.2f} m off the street's kerb line")
                break
boxes = [o["box"] for o in out]
for i, a in enumerate(boxes):
    for b in boxes[i + 1:]:
        if a.intersection(b).area > 0.05:
            print("  WARNING villa boxes overlap", round(a.intersection(b).area, 2))
taken = Polygon()
for i, o in enumerate(out):
    g = unary_union([o["plot"], o["box"]]).difference(unary_union(boxes[:i] + boxes[i + 1:])).intersection(works).difference(taken)
    g = g.buffer(-0.2, join_style=2).buffer(0.2, join_style=2)
    o["garden"] = Polygon(max(as_polys(g), key=lambda q: q.area).exterior)
    taken = taken.union(o["garden"])
# no garden over a street: the zoning lines are the kerbs of the main streets, the fences 0.40 m inside them
# (client 22-10, "7tarem distance dyal tri9"; the plots read at the west end of the southern block took in
# 2.2 m of its street, between the lane line and the kerb)
for o in out:
    over = o["garden"].intersection(kerbs).area
    if over > 0.5:
        print(f"  garden at {[round(float(x), 1) for x in o['c']]} cut back off the street: {over:.1f} m2"
              + (f" (its villa keeps {o['box'].intersection(kerbs).area:.1f} m2 of the 0.40 m)" if o["box"].intersection(kerbs).area > 0.2 else ""))
        o["garden"] = max(as_polys(o["garden"].difference(kerbs.difference(o["box"]))), key=lambda q: q.area)
# neighbouring gardens meet on one line: the plan's double fence line between them (with the drawing's
# tolerance up to 1.5 m between the regions read) goes to the gardens, no strip of ground left between walls
orig = [o["garden"] for o in out]
taken = Polygon()
for i, o in enumerate(out):
    gap = []
    for j, other in enumerate(orig):
        if j != i and o["garden"].distance(other) < 1.5:            # the gap between the two only (a closing)
            pair = unary_union([o["garden"], other])
            gap.append(pair.buffer(1.1, join_style=2).buffer(-1.1, join_style=2).difference(pair))
    others = unary_union(orig[:i] + orig[i + 1:])
    closed = o["garden"].buffer(0.9, join_style=2).buffer(-0.9, join_style=2)      # notches of the drawing filled
    g = unary_union([o["garden"], closed] + gap).difference(others).difference(taken).intersection(works).difference(kerbs.difference(o["box"]))
    g = g.buffer(0.05, join_style=2).buffer(-0.05, join_style=2)
    g = Polygon(max(as_polys(g.buffer(0)), key=lambda q: q.area).exterior).simplify(0.03).buffer(0)
    o["garden"] = max(as_polys(g), key=lambda q: q.area)
    taken = taken.union(o["garden"])
gardens = unary_union([o["garden"] for o in out])

# ---- the rest of the works: buildings, parking bays, streets and pavements, read from the plan's pieces
# 'Centre d'entretien' (two) and 'Office' on the parking strip: the plan's squares with hipped roofs
KIOSKS = [("CENTRE_ENTRETIEN_1", (-175.6, 14.1)), ("CENTRE_ENTRETIEN_2", (-155.7, 0.9)), ("OFFICE", (-119.9, -4.6))]
CL = np.zeros((GH, GW), np.uint8)                              # 1 garden 2 road 3 pavement 4 bay 5 building 9 not ours
gfill(gardens, 1, CL)
kiosks = []
for name, pt in KIOSKS:
    near = [i for i in range(1, ncomp) if csize[i] < 40 and Point(pt).distance(gvec(lab == i)) < 5.5] if True else []
    g = gvec(np.isin(lab, near)).buffer(0.2).convex_hull if near else Point(pt).buffer(4.0, 4)
    g = g.minimum_rotated_rectangle
    kiosks.append({"name": name, "poly": g})
    gfill(g, 5, CL)
bays = []
south_edge = LineString(B_SOUTH).buffer(45.0)
for i in range(1, ncomp):
    if not 8.0 <= csize[i] <= 17.0:
        continue
    g = gvec(lab == i)
    if g.is_empty or not south_edge.contains(g.centroid) or gardens.intersects(g.buffer(-0.2)):
        continue
    r = g.minimum_rotated_rectangle
    e = sorted(math.dist(*pp) for pp in zip(list(r.exterior.coords)[:2], list(r.exterior.coords)[1:3]))
    if 2.0 <= e[0] <= 3.3 and 4.2 <= e[1] <= 6.0 and g.area / r.area > 0.85:
        bays.append(r)
        CL[lab == i] = 4
pub = np.zeros((GH, GW), bool)
for i in range(1, ncomp):
    m = lab == i
    if not m.any() or (CL[m] > 0).mean() > 0.5:              # a garden, a bay or a building
        continue
    m &= CL == 0
    g_out = csize[i] > 100
    if g_out:
        g = gvec(m)
        r = g.minimum_rotated_rectangle
        e = sorted(math.dist(*pp) for pp in zip(list(r.exterior.coords)[:2], list(r.exterior.coords)[1:3]))
        if not blocks.buffer(1.0).contains(g.representative_point()) and g.area / r.area > 0.75 and e[0] > 6.0 and e[1] < 45.0:
            CL[m] = 9                                          # a lot of the type C villas: not ours
            continue
    pub |= m
# the streets as the plan draws them (client 22-10: "kima kayn f planning", "7tarem distance dyal tri9"). Its
# zoning lines run on the kerbs of the main streets: the Voie Publique and the south road, 8 m from the outer
# kerb (a 1.6 to 2.9 m verge inside the boundary) to the zoning line, the street along Tranche 1 6.06 m and
# the streets between the blocks 5.1 to 6 m between their two zoning lines. Inside the blocks the lanes are
# 5 m between kerbs drawn 0.40 m off the fences. Every piece of open ground in a zoning street cell is
# carriageway (its lanes, the gaps of the zebra crossings), but the verge along the boundary and the round
# islands; the lane-wide pieces joined to them outside the cells are the lanes and the parking aisles; the
# narrow ones (under 2.1 m across) the pavements, the wider ones off the street the planted strips (the 3.2
# to 5.1 m strip between the pavement and the fences along Tranche 1's street)
D = cv2.distanceTransform(pub.astype(np.uint8), cv2.DIST_L2, 5) / RG
npub, lpub = cv2.connectedComponents(pub.astype(np.uint8), connectivity=4)
pidx = np.arange(npub)
dmax = ndimage.maximum(D, lpub, index=pidx)
lane = dmax * 2.0 >= 2.1
lane[0] = False
zimg = np.zeros((GH, GW), np.uint8)
for it in P:
    if it["k"] == "line" and it["layer"] == "zoning" and len(it["pts"]) > 1:
        q = [gpx(f13(v)) for v in it["pts"]] + ([gpx(f13(it["pts"][0]))] if it["closed"] else [])
        cv2.polylines(zimg, [np.array(q, np.int32)], False, 255, 1)
zimg = cv2.dilate(zimg, np.ones((3, 3), np.uint8))
nzc, labzc = cv2.connectedComponents((zimg == 0).astype(np.uint8), connectivity=4)
zin = np.bincount(labzc[mW > 0], minlength=nzc) / RG / RG
main_ids = [i for i in range(1, nzc) if zin[i] > 1500.0]
print("zoning street cells in the works (m2):", [round(zin[i]) for i in main_ids])
MAIN = np.isin(labzc, main_ids)
inmain = ndimage.mean(MAIN, lpub, index=pidx)
bimg = np.zeros((GH, GW), np.uint8)
cv2.polylines(bimg, [np.array(bq + [bq[0]], np.int32)], False, 1, 1)
nearB = ndimage.mean(cv2.distanceTransform((bimg == 0).astype(np.uint8), cv2.DIST_L2, 5) / RG < 3.2, lpub, index=pidx)
psize = np.bincount(lpub.ravel(), minlength=npub) / RG / RG
verge_p = (inmain > 0.5) & (nearB > 0.8)
island = np.zeros(npub, bool)
for i in np.nonzero((psize < 60.0) & (inmain > 0.5) & lane)[0]:
    g = gvec(lpub == i, tol=0.02)
    island[i] = not g.is_empty and 4.0 * math.pi * g.area / g.length ** 2 > 0.75
carr = (inmain > 0.5) & ~verge_p & ~island
carr[0] = False
# the lanes inside the blocks: the ground between two gardens less than 7 m apart (whatever lines the plan
# draws in them, 5 m between the kerbs); then the lane-shaped pieces (2.1 to 7 m across) joined to the
# streets: the lane between the two parking squares. The squares round the kiosks stay paved
G = gfill(gardens)
corr = (cv2.morphologyEx(G, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71))) > 0) & (G == 0)
cm = corr & pub & ~MAIN                                          # joined over the lane lines drawn in them
cm = (cv2.morphologyEx(cm.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0) & corr & ~MAIN
nl, lbl, stl, _ = cv2.connectedComponentsWithStats(cm.astype(np.uint8), connectivity=8)
LANE = np.isin(lbl, [j for j in range(1, nl) if stl[j, 4] >= 40.0 * RG * RG]) & pub
k9 = np.ones((9, 9), np.uint8)
cand = lane & (dmax * 2.0 <= 7.0) & (psize >= 30.0) & (inmain <= 0.5) & ~island
behind = ndimage.sum(cv2.dilate((CL == 4).astype(np.uint8), k9) > 0, lpub, index=pidx) / RG / RG / 0.4 > 6.0
by_kiosk = ndimage.maximum(cv2.dilate((CL == 5).astype(np.uint8), k9) > 0, lpub, index=pidx) > 0
cand &= ~behind & ~by_kiosk                                    # the squares behind the bays, round the kiosks
for i in np.nonzero(by_kiosk & lane)[0]:                       # paved, but the long strips that end at one
    r = gvec(lpub == i).minimum_rotated_rectangle
    e = sorted(math.dist(*pp) for pp in zip(list(r.exterior.coords)[:2], list(r.exterior.coords)[1:3]))
    behind[i] |= e[1] < 4.0 * e[0]
while True:
    hit = ndimage.maximum(cv2.dilate((pub & (carr[lpub] | LANE)).astype(np.uint8), k9) > 0, lpub, index=pidx) > 0
    new = hit & cand & ~carr
    new[0] = False
    if not new.any():
        break
    carr |= new
strip = lane & ~carr & ~island & ~behind & (psize >= 40.0)
CL[pub & carr[lpub]] = 2
CL[pub & ~carr[lpub]] = 3
CL[pub & (verge_p | strip)[lpub]] = 6
CL[LANE] = 2
CL[pub & MAIN & ~(verge_p | island)[lpub]] = 2                # the zoning lines are the kerbs: what is between them
print(f"street pieces: {int(carr.sum())} carriageway, {int(verge_p.sum())} verge, {int(strip.sum())} planted strips, {int(island.sum())} islands; "
      f"lanes between the gardens {LANE.sum() / RG / RG:.0f} m2")
open_ = pub
# the lines themselves and the scraps: the class of the nearest piece
todo = (mW > 0) & (CL == 0)
_, ind = ndimage.distance_transform_edt(todo, return_indices=True)
CL = np.where(todo, CL[ind[0], ind[1]], CL)
CL[mW == 0] = 0
todo = (CL == 1) & (gfill(gardens) == 0)                     # the fence lines outside the gardens: the street's
CL[todo] = 0
_, ind = ndimage.distance_transform_edt((CL == 0) | (CL == 1), return_indices=True)
CL = np.where(todo, CL[ind[0], ind[1]], CL)
vi = cv2.dilate((pub & (verge_p | island)[lpub]).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
CL[(mW > 0) & MAIN & np.isin(CL, (0, 3, 6)) & ~vi & (gfill(gardens) == 0)] = 2   # and the lines and scraps between them
small = np.zeros_like(CL)
for k in (2, 3, 6):                                            # scraps under 3 m2 of one class inside another: absorbed
    n_, lb, st_, _ = cv2.connectedComponentsWithStats((CL == k).astype(np.uint8), connectivity=4)
    for j in range(1, n_):
        if st_[j, 4] < 3.0 * RG * RG:
            small[lb == j] = 1
todo = small > 0
CL[todo] = 0
_, ind = ndimage.distance_transform_edt(CL == 0, return_indices=True)
CL = np.where(todo, CL[ind[0], ind[1]], CL)
CL[mW == 0] = 0
if os.environ.get("T2_DEBUG"):                               # class map, for checking against the plan
    pal = np.array([[0, 0, 0], [120, 200, 120], [80, 80, 80], [210, 195, 165], [200, 110, 90], [40, 120, 230], [60, 150, 60]] + [[0, 0, 0]] * 2 + [[160, 40, 160]], np.uint8)
    dbg = pal[CL]
    dbg[lines > 0] = (255, 255, 255)
    cv2.imwrite(os.environ["T2_DEBUG"], cv2.resize(dbg[:, :, ::-1], (GW // 3, GH // 3), interpolation=cv2.INTER_AREA))
    np.savez_compressed(os.environ["T2_DEBUG"] + ".npz", CL=CL, lines=lines, open_=open_, MAIN=MAIN, zimg=zimg, bounds=np.array([gx0, gy0, gx1, gy1]))
# vector pieces that tile the works exactly: pavements and parking from the class map (grown 0.12 m over the
# drawing's tolerance), the streets everything else between them, the gardens and the buildings
parking = gvec(CL == 4)
foreign = gvec(CL == 9)
# what is left of Tranche 1's lots west of its limit line, between it and the street: lawn, level with
# Tranche 1's own (no strip of bare land between the two tranches)
greens = unary_union([q for q in as_polys(foreign) if q.distance(t1) < 0.6])
foreign = foreign.difference(greens.buffer(0.01))
env = works.difference(foreign.buffer(0.05)).buffer(0.0)
env = Polygon(max(as_polys(env), key=lambda q: q.area).exterior)
greens = greens.intersection(env)
solid = unary_union([gardens, greens] + [k["poly"] for k in kiosks])
# streets, verges and planted strips from the class map; pavements the rest of the ground. Scraps of street
# shut in between gardens (the drawing's double fences, notches of its outlines) go to the garden that
# borders them most; then along every fence on a street the plan's kerb 0.40 m off it
ground = env.difference(solid).difference(parking)
roads = gvec(CL == 2).intersection(ground)
verges = gvec(CL == 6).intersection(ground).difference(roads)
near = gardens.buffer(0.3, join_style=2)
n_abs = 0
for q in as_polys(roads):
    if q.area < 150.0 and q.exterior.intersection(near).length > 0.8 * q.exterior.length and q.intersection(kerbs).area < 0.5:
        o = max(out, key=lambda o: q.exterior.intersection(o["garden"].buffer(0.3, join_style=2)).length)
        o["garden"] = max(as_polys(unary_union([o["garden"], q.buffer(0.02)]).buffer(0)), key=lambda g: g.area)
        roads = roads.difference(q.buffer(0.02))
        n_abs += 1
        print("  street scrap", [round(c, 1) for c in q.centroid.coords[0]], f"{q.area:.0f} m2 to a garden")
# the lot the 2013 plan draws with another building (its villa from the client's plan): the dead-end lane off
# the street between its fences and the next lot's goes to the gardens, each up to its lot line (a paved
# forecourt is left at the street)
undrawn = unary_union([o["lot"] for o in out if not o["drawn"]])
for q in as_polys(roads.difference(kerbs)):
    mouths = q.boundary.intersection(kerbs.buffer(0.05)).buffer(0.2)
    if q.area > 2.0 and len(as_polys(mouths)) == 1 and q.intersection(undrawn).area > 0.4 * q.area:
        for o in out:
            part = q.intersection(o["lot"].buffer(0.05))
            if part.area > 1.0:
                o["garden"] = max(as_polys(unary_union([o["garden"], part.buffer(0.02)]).buffer(0)), key=lambda g: g.area)
        roads = roads.difference(q.buffer(0.02))
        print(f"  dead end by the lot drawn with another building: {q.area:.0f} m2 to the gardens")
gardens = unary_union([o["garden"] for o in out])
ground = ground.difference(gardens)
roads = roads.intersection(ground).difference(gardens.buffer(0.40, join_style=2))
roads = unary_union([q for q in as_polys(roads) if q.area > 0.5])
verges = verges.intersection(ground).difference(roads)
verges = unary_union([q for q in as_polys(verges) if q.area > 1.0])
# the street along Tranche 1, on Tranche 1's side north of where its east kerb leaves Tranche 1's limit:
# the plan's pavement (2.30 m from the zoning line to the back of its outer kerb), then a planted strip up
# to the limit, along the whole street (the stubs of the 2013 streets into the old lots, which Tranche 1's
# plan replaced, are not built)
seg = []
dR = (dT - 0.1393 * nT) / np.linalg.norm(dT - 0.1393 * nT)      # the street runs 8 degrees off Tranche 1's limit
for _, ln in ZL:
    c = np.array(ln.coords)
    for p0, p1 in zip(c[:-1], c[1:]):
        e = p1 - p0
        if np.linalg.norm(e) < 2.0 or abs(np.dot(e / np.linalg.norm(e), dR)) < 0.998:
            continue
        for p in (p0, p1):
            t_, s_ = float(np.dot(p - oT, dT)), float(np.dot(p - oT, nT))
            if 20.0 <= t_ <= 145.0 and abs(s_ - (4.18 - 0.1393 * (t_ - 25.0))) < 1.0:
                seg.append((t_, s_))
seg = np.array(seg)
kb, ka = np.polyfit(seg[:, 0], seg[:, 1], 1)
print(f"street along Tranche 1: east zoning line s = {ka:.2f} {kb:+.4f} t ({len(seg)} points, residual "
      f"{np.abs(seg[:, 1] - (ka + kb * seg[:, 0])).max():.2f} m)")
ts = np.arange(45.0, 151.0, 5.0)
xy = lambda t, s_: tuple(oT + dT * t + nT * s_)
zone = Polygon([xy(t, ka + kb * t) for t in ts] + [xy(t, 1.0) for t in ts[::-1]]).buffer(0)
zone = zone.difference(LineString(B_NORTH).buffer(12.4)).intersection(ground)
walk = Polygon([xy(t, ka + kb * t) for t in ts] + [xy(t, ka + kb * t + 2.30) for t in ts[::-1]]).buffer(0)
roads = roads.difference(zone)
verges = unary_union([verges.difference(zone), zone.difference(walk)])
verges = verges.difference(unary_union([k["poly"] for k in kiosks]).buffer(1.5, join_style=2))   # paved round the kiosks
verges = unary_union([q for q in as_polys(verges) if q.area > 1.0])
roads = unary_union([roads, t1_trim.intersection(ground)])        # Tranche 1's ground under the street: all carriageway
verges = verges.difference(t1_trim)
pave = ground.difference(roads).difference(verges)
pave = unary_union([q for q in as_polys(pave) if q.area > 0.3])
print("street scraps between gardens given to them:", n_abs)


# gates: on the front if the street is in front of the villa, else on the side the street runs along
def edge_open(o, side):
    from shapely import affinity
    loc = affinity.rotate(affinity.translate(o["garden"], -o["origin"][0], -o["origin"][1]), -o["rot"], origin=(0, 0))
    x0_, y0_, x1_, y1_ = loc.bounds
    strip = {"front": box(x0_ + 1.0, y1_ + 0.4, x1_ - 1.0, y1_ + 1.4), "right": box(x1_ + 0.4, 9.0, x1_ + 1.4, 19.0),
             "left": box(x0_ - 1.4, 9.0, x0_ - 0.4, 19.0)}[side]
    w = world_box(o, strip)
    return w.intersection(unary_union([roads, pave, parking, verges])).area / w.area


for o in out:
    sc = {s: edge_open(o, s) for s in ("front", "right", "left")}
    if os.environ.get("T2_DEBUG"):
        print("  DBG gate", [round(float(x)) for x in o["c"]], "m" if o["mirror"] else " ", {k: round(v_, 2) for k, v_ in sc.items()})
    terrace = "left" if o["mirror"] else "right"               # the side of the front terrace and the door
    if sc["front"] >= 0.6 or sc["front"] >= max(sc["right"], sc["left"]):
        o["gate"] = "front"
    elif sc[terrace] >= 0.6:
        o["gate"] = terrace
    else:
        o["gate"] = max(("right", "left"), key=lambda s: sc[s])

# numbering: the northern block then the southern one, rows from the north
out.sort(key=lambda o: (o["block"] != "north", -round(o["c"][1] / 12.0), o["c"][0]))
villas_js = []
for o in out:                                                 # valid outlines once rounded to the millimetre
    o["garden"] = max(as_polys(Polygon([(round(x, 3), round(y, 3)) for x, y in o["garden"].exterior.coords]).buffer(0)), key=lambda q: q.area)
for i, o in enumerate(out, 1):
    villas_js.append({"id": f"B-{i:02d}", "block": o["block"], "origin": [round(float(x), 3) for x in o["origin"]],
                      "rot_deg": round(o["rot"], 3), "mirror": bool(o["mirror"]), "compact": o["compact"], "gate": o["gate"],
                      "drawn_on_plan": o["drawn"], "plot": poly_out(o["plot"])[0], "garden": poly_out(o["garden"])[0],
                      "lot": poly_out(o["lot"])[0]})
print("villas", len(villas_js), "mirrored", sum(v["mirror"] for v in villas_js), "gates", Counter(v["gate"] for v in villas_js))
js = {"source": "plan de masse 31-05-13 (villas type B west of Tranche 1), model frame of site.json",
      "env": poly_out(env)[0], "blocks": poly_out(blocks)[0], "villas": villas_js,
      "roads": poly_out(roads), "pavements": poly_out(pave), "verges": poly_out(verges), "parking": poly_out(parking), "greens": poly_out(greens),
      "t1_trim": poly_out(t1_trim),
      "bays": [poly_out(b)[0] for b in bays], "buildings": [{"name": k["name"], "poly": poly_out(k["poly"])[0]} for k in kiosks]}
json.dump(js, open(os.path.join(ROOT, "data", "t2_site.json"), "w"))
print(f"  roads {roads.area:.0f} m2, pavements {pave.area:.0f} m2, verges and strips {verges.area:.0f} m2, lawn by Tranche 1 {greens.area:.0f} m2, parking bays {len(bays)} ({parking.area:.0f} m2), "
      f"buildings {len(kiosks)}, type C lots left out {foreign.area:.0f} m2, works {env.area:.0f} m2")
