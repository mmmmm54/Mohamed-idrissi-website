"""
01_extract_site — Tranche A+B site data from the architect's plan de masse (DWG, 31-05-13).

    python -I 01_extract_site.py <plan_masse.pkl> [check.png]

The .pkl is the DWG exploded by tools/flatten.py (world metres, blocks resolved).
Writes ../data/site.json in local metres: origin O = (47900, 290320) of the DWG, x east, y north.

What is read, and from which layer:
  boundary      'niveau cote' red closed polyline (82 139 m2 = contenance 8 ha 20 a 70 ca)
  contours      'niveau cote' orange polylines, height from the nearest "xx.00" label
  paving        '012' ANSI37 hatches (pavements, plot paths, parking edges), AR-HBONE hatches
  roofs         '012' ANSI33 hatches (hipped roofs: club, kiosks)
  water         '041_rue chemin chaussee' hatches (canal, pools, jardin aquatique, bassins)
  duplexes      'Nouveau calque 11': 2 NET squares (stair cages), 2 ANSI31 access strips and
                2 ANSI37 rear terraces per duplex -> centre, front direction
  public bldgs  'cadastre' red/cyan outlines + 'ARWALL' (administration)
  cars          '010_personnage' line clusters -> oriented rectangles
  trees         'cadastre' green closed circles
  pergolas      'Menuiserie Bois' slats outside the duplex blocks
"""
import json
import math
import os
import pickle
import sys

import numpy as np
from shapely.geometry import LineString, MultiPoint, Point, Polygon, box
from shapely.ops import polygonize, unary_union

O = np.array([47900.0, 290320.0])
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "site.json")

P = pickle.load(open(sys.argv[1], "rb"))
AB_BOX = box(47805, 290225, 48075, 290430)
# west edge of Tranche A+B: just west of the N-S road that bounds the duplex blocks (the red circle)
CUT = [(47814.5, 290400.0), (47825.0, 290232.0)]


def xy(o):
    return [(p[0], p[1]) for p in o["pts"]]


def loc(pts):
    return [[round(x - O[0], 3), round(y - O[1], 3)] for x, y in pts]


def poly_loc(g):
    g = g.buffer(0)
    out = []
    for pg in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        if pg.is_empty or pg.area < 0.05:
            continue
        out.append({"ext": loc(pg.exterior.coords[:-1]), "holes": [loc(h.coords[:-1]) for h in pg.interiors]})
    return out


def inside(o, g=AB_BOX):
    return all(g.contains(Point(p)) for p in xy(o))


def cen(o):
    return np.array(xy(o)).mean(0)


site = {}

# ---- boundary + Tranche A+B region ---------------------------------------------------------
bd = [o for o in P if o["layer"] == "niveau cote" and o["rgb"] == (255, 0, 0) and o["k"] == "line" and len(o["pts"]) == 22][0]
SITE = Polygon(xy(bd)[:-1])
(ax, ay), (bx, by) = CUT
far = 2000
dx, dy = bx - ax, by - ay
n = math.hypot(dx, dy)
ux, uy = dx / n, dy / n
east = Polygon([(ax - ux * far, ay - uy * far), (bx + ux * far, by + uy * far),
                (bx + ux * far - uy * far, by + uy * far + ux * far), (ax - ux * far - uy * far, ay - uy * far + ux * far)])
AB = SITE.intersection(east)
site["boundary"] = loc(SITE.exterior.coords[:-1])
site["boundary_area_m2"] = round(SITE.area, 1)
site["ab_region"] = poly_loc(AB)

# ---- contours --------------------------------------------------------------------------------
C = [o for o in P if o["layer"] == "niveau cote" and o["rgb"] == (255, 191, 0) and o["k"] == "line" and len(o["pts"]) > 1]
G = [LineString(xy(o)) for o in C]
labels = [(Point(o["pts"][0][:2]), float(str(o["text"]).strip())) for o in P
          if o["k"] == "text" and o["layer"] == "niveau cote" and str(o["text"]).strip().endswith(".00")]
z = [None] * len(G)
for pt, v in labels:
    d = [g.distance(pt) for g in G]
    i = int(np.argmin(d))
    if d[i] < 6 and z[i] is None:
        z[i] = v
near = SITE.buffer(120)
site["contours"] = [{"z": z[i], "pts": loc(G[i].simplify(0.3).coords)} for i in range(len(G))
                    if z[i] is not None and G[i].intersects(near)]

# ---- paving / roofs / water ------------------------------------------------------------------
pav, hb, roofs, water, sand = [], [], [], [], []
for o in P:
    if o["k"] != "hatch" or len(o["pts"]) < 3 or not inside(o):
        continue
    g = Polygon(xy(o)).buffer(0)
    if not AB.buffer(1).intersects(g):
        continue
    if o["layer"] == "012":
        pat = o.get("pat")
        if pat == "ANSI37":
            pav.append(g)
        elif pat == "AR-HBONE":
            hb.append(g)
        elif pat == "ANSI33":
            roofs.append(g)
        elif pat == "AR-SAND":
            sand.append(g)
    elif o["layer"] == "041_rue chemin chaussee" or (o["layer"] == "cadastre" and o["rgb"] == (0, 255, 255)):
        water.append(g)
pav_u = unary_union(pav).intersection(AB)
site["paving"] = poly_loc(pav_u)
site["paving_hbone"] = poly_loc(unary_union(hb).intersection(AB))
site["roofs"] = [poly_loc(g)[0] for g in roofs]
site["water"] = poly_loc(unary_union(water).intersection(AB))
site["sand"] = poly_loc(unary_union(sand).intersection(AB)) if sand else []

# ---- duplex blocks (zoning plots) ------------------------------------------------------------
Z = [LineString(xy(o) + ([xy(o)[0]] if o["closed"] else [])) for o in P
     if o["layer"] == "zoning" and o["k"] == "line" and len(o["pts"]) > 1]
Z = [g for g in Z if g.intersects(AB_BOX)]
faces = list(polygonize(unary_union(Z)))
equip = max(faces, key=lambda f: f.area if f.centroid.x > 47915 else 0)
plots = [f for f in faces if 47825 < f.centroid.x < 47930 and f.area > 1 and not equip.buffer(-1).intersects(f)]
blocks = unary_union([p.buffer(0.6, join_style=2) for p in plots]).buffer(-0.6, join_style=2)
blocks = unary_union([Polygon(g.exterior) for g in (blocks.geoms if blocks.geom_type == "MultiPolygon" else [blocks]) if g.area > 800])
site["duplex_blocks"] = poly_loc(blocks.intersection(AB))
site["equipment_zone"] = poly_loc(equip)

# ---- duplex placements -----------------------------------------------------------------------
N = [o for o in P if o["layer"] == "Nouveau calque 11" and inside(o)]
nets = [cen(o) for o in N if o["k"] == "hatch" and o.get("pat") == "NET"]
acc = [cen(o) for o in N if o["k"] == "hatch" and o.get("pat") == "ANSI31"]
ter = [cen(o) for o in N if o["k"] == "hatch" and o.get("pat") == "ANSI37" and o["rgb"][0] == 173]
used, dup = set(), []
for i, a in enumerate(nets):
    if i in used:
        continue
    j = min((j for j in range(len(nets)) if j != i and j not in used), key=lambda j: np.linalg.norm(nets[j] - a))
    used |= {i, j}
    c = (a + nets[j]) / 2
    fa = np.mean([p for p in acc if np.linalg.norm(p - c) < 12], 0)
    ft = np.mean([p for p in ter if np.linalg.norm(p - c) < 12], 0)
    f = fa - ft
    front = math.atan2(f[1], f[0])            # direction the main facade (access side) faces
    dup.append({"c": [round(c[0] - O[0], 3), round(c[1] - O[1], 3)], "front_deg": round(math.degrees(front), 3)})
dup.sort(key=lambda d: (-round(d["c"][1] / 25), d["c"][0]))
site["duplexes"] = dup

# ---- public buildings (outlines on the masse plan) ------------------------------------------
def cluster_outline(layer_rgbs, region):
    L = [LineString(xy(o)) for o in P if (o["layer"], o["rgb"]) in layer_rgbs and o["k"] == "line"
         and len(o["pts"]) > 1 and region.contains(Point(cen(o)))]
    return unary_union([g.buffer(0.15) for g in L])

REST = Polygon([(47975, 290405), (47998, 290410), (48010, 290362), (47985, 290352)])
COMM = Polygon([(47995, 290358), (48012, 290362), (48030, 290318), (48010, 290308)])
ADMIN = Polygon([(47926, 290346), (47952, 290356), (47966, 290322), (47938, 290312)])
STAT = Polygon([(47950, 290402), (47975, 290406), (47977, 290388), (47952, 290380)])
GATE = Polygon([(48001.5, 290356.5), (48011, 290356.5), (48011, 290366.5), (48001.5, 290366.5)])
pb = {}
for name, reg, lay in [("restaurant", REST, {("cadastre", (255, 0, 0))}),
                       ("commerce", COMM, {("cadastre", (255, 0, 0))}),
                       ("administration", ADMIN, {("ARWALL", (255, 0, 0)), ("cadastre", (0, 255, 255))}),
                       ("station_epuration", STAT, {("cadastre", (255, 0, 0))}),
                       ("gatehouse", GATE, {("cadastre", (255, 0, 0))})]:
    g = cluster_outline(lay, reg)
    r = g.minimum_rotated_rectangle
    q = np.array(r.exterior.coords)[:4]
    e1, e2 = q[1] - q[0], q[2] - q[1]
    ang = math.degrees(math.atan2(e1[1], e1[0])) if np.linalg.norm(e1) >= np.linalg.norm(e2) else math.degrees(math.atan2(e2[1], e2[0]))
    pb[name] = {"outline": poly_loc(g.buffer(0.3).buffer(-0.3)), "rect": loc(q),
                "c": [round(r.centroid.x - O[0], 3), round(r.centroid.y - O[1], 3)],
                "long_deg": round(ang, 3), "size": sorted([round(float(np.linalg.norm(e1)), 2), round(float(np.linalg.norm(e2)), 2)])}
site["public"] = pb

# ---- cars --------------------------------------------------------------------------------------
from scipy.cluster.hierarchy import fcluster, linkage
CAR_LINK = float(os.environ.get("CAR_LINK", "0.5"))
segs = [o for o in P if o["layer"] == "010_personnage" and o["k"] == "line" and inside(o, AB.buffer(2))]
mids = np.array([cen(o) for o in segs])
cars = []
if len(mids):
    lab = fcluster(linkage(mids, "single"), CAR_LINK, "distance")
    for k in set(lab):
        pts = [p for o, l in zip(segs, lab) if l == k for p in xy(o)]
        if len(pts) < 20:
            continue
        r = MultiPoint(pts).minimum_rotated_rectangle
        q = np.array(r.exterior.coords)[:4]
        e1, e2 = q[1] - q[0], q[2] - q[1]
        L1, L2 = np.linalg.norm(e1), np.linalg.norm(e2)
        Lmax, Lmin = max(L1, L2), min(L1, L2)
        if not (3.2 < Lmax < 5.6 and 1.4 < Lmin < 2.4):
            continue
        e = e1 if L1 >= L2 else e2
        cars.append({"c": [round(r.centroid.x - O[0], 2), round(r.centroid.y - O[1], 2)],
                     "deg": round(math.degrees(math.atan2(e[1], e[0])), 1), "len": round(Lmax, 2), "wid": round(Lmin, 2)})
site["cars"] = cars

# ---- trees ------------------------------------------------------------------------------------
trees = []
for o in P:
    if o["layer"] == "cadastre" and o["rgb"] == (0, 255, 0) and o["k"] == "line" and o["closed"] and inside(o, AB):
        q = np.array(xy(o))
        d = (q.max(0) - q.min(0)).max()
        if 0.8 < d < 3.5:
            c = q.mean(0)
            if all(np.hypot(*(c - O - np.array(t["c"]))) > 0.8 for t in trees):
                trees.append({"c": [round(c[0] - O[0], 2), round(c[1] - O[1], 2)], "d": round(float(d), 2)})
site["trees"] = trees

# ---- pergola slats (public areas only) --------------------------------------------------------
sl = []
for o in P:
    if o["layer"] == "Menuiserie Bois" and o["k"] == "line" and inside(o, AB) and not blocks.buffer(1).contains(Point(cen(o))):
        q = xy(o)
        if len(q) == 2 and math.dist(q[0], q[1]) > 0.4:
            sl.append(loc(q))
site["pergola_lines"] = sl

# ---- courts, zebra crossings --------------------------------------------------------------------
def segs_in(region, layer="012"):
    out = []
    for o in P:
        if o["layer"] == layer and o["k"] == "line" and all(region.contains(Point(p)) for p in xy(o)):
            q = xy(o)
            out += [(a, b) for a, b in zip(q, q[1:]) if math.dist(a, b) > 0.05]
    return out

courts = {}
for name, reg in [("tennis", Polygon([(47958, 290393), (47980, 290402), (47998, 290364), (47974, 290355)])),
                  ("minifoot", Polygon([(47980, 290340), (48008, 290348), (48012, 290305), (47985, 290298)]))]:
    sg = segs_in(reg)
    longest = max(math.dist(a, b) for a, b in sg)
    if name == "tennis":
        encl = MultiPoint([p for a, b in sg if math.dist(a, b) > 15 for p in (a, b)]).minimum_rotated_rectangle
    else:   # the two pitches (18.5 m lines) + 1 m run-off; the enclosure line also takes in parking bays
        encl = MultiPoint([p for a, b in sg if 18.0 < math.dist(a, b) < 19.0 for p in (a, b)]).minimum_rotated_rectangle.buffer(0.3, join_style=2)
    courts[name] = {"surface": poly_loc(encl)[0], "lines": [loc([a, b]) for a, b in sg if math.dist(a, b) > 0.5 and math.dist(a, b) < longest - 1.0
                                                         and encl.buffer(0.05).contains(LineString([a, b]))]}
site["courts"] = courts

two = [(a, b) for a, b in segs_in(AB) if 2.2 < math.dist(a, b) < 4.6]
zebra = []
arr = np.array([[a[0], a[1], b[0], b[1]] for a, b in two])
mid = (arr[:, :2] + arr[:, 2:]) / 2
for i, (a, b) in enumerate(two):
    u = np.array(b) - np.array(a)
    L = np.linalg.norm(u)
    u /= L
    nrm = np.array([-u[1], u[0]])
    dm = mid - mid[i]
    along = np.abs(dm @ u)
    perp = dm @ nrm
    for j in np.where((along < 0.3) & (perp > 0.3) & (perp < 0.65))[0]:
        a2, b2 = two[j]
        u2 = (np.array(b2) - np.array(a2)) / math.dist(a2, b2)
        if abs(abs(u @ u2) - 1) < 0.002 and abs(math.dist(a2, b2) - L) < 0.15:
            zebra.append(loc([tuple(mid[i] - u * L / 2), tuple(mid[i] + u * L / 2),
                              tuple(mid[i] + u * L / 2 + nrm * perp[j]), tuple(mid[i] - u * L / 2 + nrm * perp[j])]))
site["zebra"] = zebra

# ---- ground surfaces (disjoint, by precedence) --------------------------------------------------
F = [LineString(xy(o) + ([xy(o)[0]] if o["closed"] else [])) for o in P
     if o["layer"] in ("012", "041_rue chemin chaussee", "zoning", "cadastre", "ARWALL") and o["k"] == "line" and len(o["pts"]) > 1]
F = [g for g in F if g.intersects(AB_BOX) and g.length > 0.3]
faces2 = [f for f in polygonize(unary_union(F)) if f.area > 1.0]


def L_as_polys(g):
    return [g] if g.geom_type == "Polygon" else [q for q in getattr(g, "geoms", []) if q.geom_type == "Polygon"]


def face_at(x, y):
    c = [f for f in faces2 if f.contains(Point(x, y))]
    return min(c, key=lambda f: f.area)

pick = {"asphalt": [(47968, 290350)], "lawn": [(47905, 290320), (47990, 290378), (47895.5, 290373.6), (47899.8, 290347.0)],
        "deck": [(47905, 290328), (47915, 290300)], "play": [(47935, 290375)]}
picked = {k: unary_union([face_at(*p) for p in v]) for k, v in pick.items()}
water_u = unary_union(water).intersection(AB)
hb_u = unary_union(hb).intersection(AB)
court_u = unary_union([Polygon([(x + O[0], y + O[1]) for x, y in c["surface"]["ext"]]).buffer(0) for c in courts.values()])
# plot gardens = the areas the plan encloses with paving inside the duplex blocks (the parking
# bays along the streets are inside the zoning blocks too, but they are not enclosed: asphalt)
gardens = []
bl = blocks.buffer(1.0)
for pt in [(47912, 290380), (47922, 290356)]:          # the two plots inside the equipment zoning
    gardens += [f.difference(pav_u) for f in faces2 if f.contains(Point(pt))]
for f in faces2:
    if f.area > 40 and bl.contains(f.representative_point()) and f.intersection(pav_u).area < 0.5 * f.area:
        gardens.append(f.difference(pav_u))
gardens = unary_union(gardens + [picked["lawn"]])
# the road face of the equipment zone: direction arrows were drawn as closed triangles, fill them
asph = unary_union([Polygon(g.exterior, [h for h in g.interiors if Polygon(h).area > 40]) for g in L_as_polys(picked["asphalt"])])
# canal median at the entrance (client, 13-10): raised paved strip 6.8 m wide around the east canal,
# from the roundabout crossing to the gatehouse island (plan: lines 1.4 m outside each canal edge)
_ca, _cc = math.radians(22.41), (47986.1, 290350.9)
_U, _N = (math.cos(_ca), math.sin(_ca)), (-math.sin(_ca), math.cos(_ca))
_uv = lambda u, v: (_cc[0] + _U[0] * u + _N[0] * v, _cc[1] + _U[1] * u + _N[1] * v)
island = unary_union([q for q in L_as_polys(pav_u) if q.buffer(0.5).contains(Point(48008.5, 290360.1))])
median = Polygon([_uv(-15.2, -3.4), _uv(20.6, -3.4), _uv(20.6, 3.4), _uv(-15.2, 3.4)]).difference(island.buffer(0.02))
order = [("water", water_u), ("median", median), ("paving", unary_union([pav_u, hb_u])), ("court", court_u), ("play", picked["play"]),
         ("deck", picked["deck"]), ("lawn", gardens),
         ("asphalt", unary_union([asph, AB.difference(equip)])),
         ("plaza", equip.intersection(unary_union([Polygon([(x + O[0], y + O[1]) for x, y in pb[k]["outline"][0]["ext"]]).buffer(2.0)
                                                    for k in ("restaurant", "commerce")]
                                       + [Polygon(g.exterior) for g in L_as_polys(unary_union([picked["deck"], picked["lawn"]]))] + [court_u.buffer(3.0, join_style=2)])))]
# whatever is left in the equipment zone (parking bays between the sawtooth pavements) is road
taken = Polygon()
surf = {}
for k, g in order:
    g = g.intersection(AB).difference(taken).buffer(0)
    surf[k] = poly_loc(g)
    taken = unary_union([taken, g])
rest = AB.difference(taken).buffer(-0.05).buffer(0.05)
surf["asphalt"] += poly_loc(rest)
site["surfaces"] = surf

# ---- level marks ------------------------------------------------------------------------------
site["origin_dwg"] = O.tolist()
json.dump(site, open(OUT, "w"), separators=(",", ":"))
print("site.json", {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in site.items()})

# ---- check image ------------------------------------------------------------------------------
if len(sys.argv) > 2:
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = -100, -95, 175, 110
    s = 8
    W, H = int((x1 - x0) * s), int((y1 - y0) * s)
    im = Image.new("RGB", (W, H), (245, 245, 240))
    d = ImageDraw.Draw(im)
    T = lambda p: ((p[0] - x0) * s, H - (p[1] - y0) * s)

    def fill(polys, col, out=None):
        for pg in polys:
            d.polygon([T(p) for p in pg["ext"]], fill=col, outline=out)
            for h in pg["holes"]:
                d.polygon([T(p) for p in h], fill=(245, 245, 240))
    SC = {"asphalt": (70, 70, 75), "plaza": (225, 215, 195), "lawn": (120, 170, 90), "deck": (170, 120, 80),
          "play": (230, 200, 120), "court": (60, 130, 90), "hbone": (190, 140, 90), "paving": (200, 195, 180), "water": (60, 140, 220)}
    for k, col in SC.items():
        fill(site["surfaces"].get(k, []), col, (40, 40, 40) if k == "paving" else None)
    fill(site["roofs"], (180, 70, 50))
    for c in site["courts"].values():
        for l in c["lines"]:
            d.line([T(p) for p in l], fill=(255, 255, 255), width=1)
    for z in site["zebra"]:
        d.polygon([T(p) for p in z], fill=(255, 255, 255))
    for k, v in site["public"].items():
        fill(v["outline"], (230, 120, 30))
    d.line([T(p) for p in site["boundary"] + site["boundary"][:1]], fill=(255, 0, 0), width=3)
    for c in site["contours"]:
        d.line([T(p) for p in c["pts"]], fill=(230, 180, 0), width=1)
    for dp in site["duplexes"]:
        cx, cy = dp["c"]
        a = math.radians(dp["front_deg"])
        d.line([T((cx, cy)), T((cx + 8 * math.cos(a), cy + 8 * math.sin(a)))], fill=(255, 0, 255), width=3)
    for c in site["cars"]:
        a = math.radians(c["deg"])
        ux, uy = math.cos(a) * c["len"] / 2, math.sin(a) * c["len"] / 2
        vx, vy = -math.sin(a) * c["wid"] / 2, math.cos(a) * c["wid"] / 2
        cx, cy = c["c"]
        d.polygon([T((cx + ux + vx, cy + uy + vy)), T((cx - ux + vx, cy - uy + vy)), T((cx - ux - vx, cy - uy - vy)), T((cx + ux - vx, cy + uy - vy))], fill=(240, 240, 0))
    for t in site["trees"]:
        cx, cy = T(t["c"])
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(20, 120, 20))
    for l in site["pergola_lines"]:
        d.line([T(p) for p in l], fill=(120, 60, 20), width=1)
    im.save(sys.argv[2])
