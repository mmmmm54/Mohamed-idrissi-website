"""
01_extract_site — read the plan de masse "MASSE_12-10_MIRLEFT" (1er TRANCHE) and write data/site.json.

    python -I 01_extract_site.py <masse_12-10.pkl> <inserts.pkl> [check.png]

Inputs are made from the DWG with tools/: dwg2json.mjs (DWG -> JSON), flatten.py (primitives in
world coordinates, tagged with their block path), inserts.py (every block insert with its transform).
The plan is organised in named blocks (D5-D8 ... D19-D24, PISCINE, RESTAURANT MIRLEFT, COMMERCES
MIRLEFT, PARKING 2 + PETANQUE, TRACAGE VOIRIE, RVT 01 ...); the duplex pairs are two repeated blocks.

World frame of the model: metres, x east, y north (the plan's north arrow points up), origin =
DWG (252000, 119430), z = altitude - 50 m. The plan is the 2013 plan de masse turned by -33.002 deg:
its site boundary matches the 2013 one to 0.4 mm on 16 vertices, so the 2013 contours (55 / 60 m)
are brought over with that transform for the ground levels.

Surfaces: hatches of the plan (lawn, herringbone lanes, terraces, stabilisé, water ...) are used as
drawn (even-odd loops). The unhatched areas are the regions the plan's lines enclose (found on a
5 cm raster); roads are listed by seed points, the other unhatched regions are paving.

Road paint: the pedestrian crossings (blocks 'DFGW' / 'xwdfrg' and the stripes of 'TRACAGE VOIRIE').
Stairs: outline, axis and flights (the plan's riser lines) of 'ESC 16-17' and 'ESC V4'.
"""
import json
import math
import os
import pickle
import sys
from collections import Counter, defaultdict

import cv2
import numpy as np
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AB_SITE = os.path.join(os.path.dirname(ROOT), "mirleft-tranche-ab", "data", "site.json")

O = (252000.0, 119430.0)
XF13 = (-33.00208, (251974.6365, 119431.7749))      # 2013 local (DWG - (47900, 290320)) -> this plan
U_LIMIT = -89.7                                     # western limit of the 1er TRANCHE (yellow line)
ROW = -33.0                                         # direction of the duplex rows (deg)

P = pickle.load(open(sys.argv[1], "rb"))
INS = pickle.load(open(sys.argv[2], "rb"))
CHECK = sys.argv[3] if len(sys.argv) > 3 else None
site = {"origin_dwg": list(O), "xf_2013": {"theta_deg": XF13[0], "t": list(XF13[1])}}


def loc(p):
    return (p[0] - O[0], p[1] - O[1])


def uv(p):
    a = math.radians(ROW)
    dx, dy = p[0] - O[0], p[1] - O[1]
    return (dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a))


def gloc(g):
    return affinity.translate(g, -O[0], -O[1])


def as_polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]


def poly_out(g, nd=3):
    out = []
    for p in as_polys(g):
        if p.area < 1e-3:
            continue
        out.append({"ext": [[round(x, nd), round(y, nd)] for x, y in p.exterior.coords[:-1]],
                    "holes": [[[round(x, nd), round(y, nd)] for x, y in r.coords[:-1]] for r in p.interiors]})
    return out


def in_block(p, name):
    return bool(p["path"]) and p["path"][0] == name


def pts2(p):
    return [q[:2] for q in p["pts"]]


# ---- frame, boundary, tranche ------------------------------------------------------------------
BOUND = [(252103.3, 119361.36), (252004.17, 119375.24), (251941.3, 119394.16), (251926.22, 119402.11), (251900.85, 119403.49),
         (251865.67, 119400.11), (251814.99, 119417.98), (251767.37, 119476.91), (251750.32, 119503.11), (251690.82, 119540.83),
         (251643.61, 119565.21), (251629.44, 119578.68), (251599.52, 119630.63), (251540.37, 119726.96), (251593.99, 119752.12),
         (251604.38, 119766.99), (251636.51, 119739.81), (251727.95, 119669.97), (251857.98, 119592.85), (251980.12, 119514.85),
         (252120.64, 119454.08)]          # '02-menuiseries bois' red polyline = the site boundary (bornes B1..B13)
SITE_POLY = Polygon(BOUND)
a = math.radians(ROW)
far = 2000
half = Polygon([(O[0] + U_LIMIT * math.cos(a) - s * far * math.sin(a), O[1] + U_LIMIT * math.sin(a) + s * far * math.cos(a)) for s in (-1, 1)] +
               [(O[0] + (U_LIMIT + far) * math.cos(a) + s * far * math.sin(a), O[1] + (U_LIMIT + far) * math.sin(a) - s * far * math.cos(a)) for s in (-1, 1)])
T1 = SITE_POLY.intersection(half)
site["boundary"] = [list(map(lambda v: round(v, 3), loc(p))) for p in BOUND]
site["boundary_area_m2"] = round(SITE_POLY.area, 1)
site["t1_region"] = poly_out(gloc(T1))
print("site", round(SITE_POLY.area), "m2  tranche 1", round(T1.area), "m2")

# ---- contours of the 2013 plan, brought over --------------------------------------------------
ab = json.load(open(AB_SITE))
th = math.radians(XF13[0])


def from13(p):
    return (math.cos(th) * p[0] - math.sin(th) * p[1] + XF13[1][0] - O[0], math.sin(th) * p[0] + math.cos(th) * p[1] + XF13[1][1] - O[1])


site["contours"] = [{"z": c["z"], "pts": [[round(v, 3) for v in from13(p)] for p in c["pts"]]} for c in ab["contours"]]
# grading plane of the 2013 A+B area (same ground), expressed in this frame: z = a x + b y + c (z = alt - 50)
pa, pb, pc = 0.03653, 0.04115, 59.41131 - 50.0
ga = pa * math.cos(th) - pb * math.sin(th)         # gradient rotated by theta
gb = pa * math.sin(th) + pb * math.cos(th)
# value at the local origin: local (0,0) -> 2013 local
x13 = math.cos(-th) * (O[0] - XF13[1][0]) - math.sin(-th) * (O[1] - XF13[1][1])
y13 = math.sin(-th) * (O[0] - XF13[1][0]) + math.cos(-th) * (O[1] - XF13[1][1])
site["plane"] = [round(ga, 6), round(gb, 6), round(pa * x13 + pb * y13 + pc, 4)]
print("plane", site["plane"])

# ---- hatches (even-odd per HATCH entity) -------------------------------------------------------
groups = defaultdict(list)
for p in P:
    if p["k"] == "hatch" and len(p["pts"]) > 2:
        groups[p["hid"]].append(p)
HATCH = []
for hid, ps in groups.items():
    loops = []
    for p in ps:
        g = Polygon(pts2(p)).buffer(0)
        if not g.is_empty:
            loops.append(g)
    if not loops:
        continue
    p0 = ps[0]
    if p0["layer"] in ("PR", "bassin") and p0["rgb"] in ((0, 63, 255), (255, 255, 255)):
        g = unary_union(loops)             # pool / median bassins: overlapping outlines, filled as one
    else:
        g = loops[0]
        for l in loops[1:]:
            g = g.symmetric_difference(l)
    HATCH.append(dict(hid=hid, layer=p0["layer"], rgb=tuple(p0["rgb"]), pat=p0.get("pat"), path=p0["path"], geom=g.buffer(0)))

CLS = [
    ("lawn", lambda h: h["rgb"] in ((88, 186, 72), (0, 255, 0), (0, 153, 38), (0, 153, 76)) and h["layer"] not in ("Consol", "02-menuiseries bois")),
    ("lane", lambda h: h["layer"] in ("01-murs ext", "-id-revetement 1 hachure") and h["pat"] == "AR-HBONE"),
    ("terrace", lambda h: h["layer"] == "03-vue" and h["rgb"] == (214, 214, 214) and h["pat"] == "AR-HBONE"),
    ("terracotta", lambda h: h["layer"] == "03-vue" and h["rgb"] == (248, 153, 30)),
    ("stabilise", lambda h: h["layer"] == "-id-stabilisé"),
    ("concrete", lambda h: h["layer"] == "03-vue" and h["rgb"] == (255, 255, 255) and h["pat"] == "AR-CONC"),
    ("paving", lambda h: (h["pat"] in ("ANSI37", "AR-B816C", "AR-B816") and h["layer"] not in ("02-menuiseries bois", "RV"))
     or (h["layer"] == "01-murs ext" and h["rgb"] == (76, 0, 0))),
    ("water", lambda h: h["layer"] in ("PR", "VERDURE", "bassin") and h["pat"] in ("AR-SAND", "BRASS") and h["geom"].area > 1.0),
    ("ramp", lambda h: h["layer"] == "rampe"),
]
HCLS = defaultdict(list)
for h in HATCH:
    if h["path"] and h["path"][0] in ("topkjk",):
        continue
    if any(n in h["path"] for n in ("DFGW", "xwdfrg")):      # zebra crossings: removed (client, 13-10)
        continue
    if not T1.intersects(h["geom"]):
        continue
    for name, f in CLS:
        if f(h):
            HCLS[name].append(h)
            break
for k, v in HCLS.items():
    print(f"  hatch {k:11s} {len(v):3d}  {sum(h['geom'].area for h in v):8.1f} m2")

# ---- unhatched regions (raster of the plan's lines) --------------------------------------------
X0, Y0, X1, Y1 = 251885.0, 119355.0, 252130.0, 119530.0
RES = 20.0
W, H = int((X1 - X0) * RES), int((Y1 - Y0) * RES)
SEP = {"012", "01-murs ext", "Mur gard cour", "-id-structure jardin", "03-vue", "Mur de soutenement", "trottoire", "mur",
       "041_rue chemin chaussee", "-id-revetement 3", "terrasse", "TERRASSE +", "ENDUIT MUR", "mur extérieur", "01-Mur ext",
       "MENUISERIE", "A-WALL", "PR", "-id-espace vert", "-id-stabilisé", "VERDURE", "rampe", "02-menuiseries bois", "05-sols",
       "Equip_ Escaliers int", "0_No_stylo__27", "bassin", "jardin", "pergola", "A-concrete hatch_Stylo_No__4", "construction"}


def px(p):
    return (int(round((p[0] - X0) * RES)), int(round((Y1 - p[1]) * RES)))


img = np.zeros((H, W), np.uint8)
for p in P:
    if p["k"] not in ("line", "hatch") or p["layer"] not in SEP:
        continue
    if p["layer"] == "012" and len(p["pts"]) == 42 and p["closed"]:
        continue                                            # road-width circles
    q = [px(v) for v in p["pts"]]
    if p["k"] == "hatch" or p["closed"]:
        q = q + [q[0]]
    if len(q) > 1:
        cv2.polylines(img, [np.array(q, np.int32)], False, 255, 1)
img = cv2.dilate(img, np.ones((3, 3), np.uint8))
n, lab, stats, cent = cv2.connectedComponentsWithStats((img == 0).astype(np.uint8), connectivity=4)


def fill_mask(geoms, shape):
    m = np.zeros(shape, np.uint8)
    for g in geoms:
        for pg in as_polys(g):
            cv2.fillPoly(m, [np.array([px(v) for v in pg.exterior.coords], np.int32)], 1)
            for r in pg.interiors:
                cv2.fillPoly(m, [np.array([px(v) for v in r.coords], np.int32)], 0)
    return m


hm = fill_mask([h["geom"] for v in HCLS.values() for h in v], lab.shape)
area = np.bincount(lab.ravel(), minlength=n)
cov = np.bincount(lab.ravel(), weights=hm.ravel().astype(float), minlength=n) / np.maximum(area, 1)


def seed(x, y):
    return int(lab[int((Y1 - y) * RES), int((x - X0) * RES)])


SEEDS = {
    # roads: the network around the tranche (north, east and south roads, parking bays), the road
    # west of row A, the 8.5 m road between rows A and B (three lanes of its marking) and the bays
    # south-west of D-24
    "asphalt": [(251935.98, 119404.18), (251905.98, 119443.02), (251906.68, 119414.22), (251979.08, 119499.88),
                (251981.68, 119500.72), (251903.18, 119422.62)],
    "deck": [(251997.02, 119423.88), (251993.78, 119406.48), (251990.78, 119400.12)],   # plage piscine, lounger strip
    "lawn": [(252016.12, 119393.42)],                       # unhatched ground between the pool and the restaurant terrace (to confirm)
    "kids_pool": [(251994.82, 119395.48)],
}
ids = {k: {seed(*p) for p in v} for k, v in SEEDS.items()}
print("  seed regions", {k: sorted(v) for k, v in ids.items()})
special = set().union(*ids.values()) | {0}
# zebra crossings (blocks DFGW / xwdfrg) are removed (client, 13-10): their stripes stay road
zeb = defaultdict(list)
for p in P:
    for nm in ("DFGW", "xwdfrg"):
        if nm in p["path"]:
            zeb[(nm, p["iids"][p["path"].index(nm)])].extend(pts2(p))
zm = fill_mask([Polygon(np.array(v)).convex_hull.buffer(0.3) for v in zeb.values() if len(v) > 2], lab.shape)
zfrac = np.bincount(lab.ravel(), weights=zm.ravel().astype(float), minlength=n) / np.maximum(area, 1)
special |= {i for i in range(1, n) if zfrac[i] > 0.5}
default_paving = [i for i in range(1, n) if cov[i] < 0.4 and i not in special and area[i] >= RES * RES * 0.3]


def vec(id_list, dil=2):
    m = np.isin(lab, list(id_list)).astype(np.uint8)
    if dil:
        m = cv2.dilate(m, np.ones((2 * dil + 1, 2 * dil + 1), np.uint8))
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    if hier is None:
        return Polygon()
    hier = hier[0]
    for k, c in enumerate(cs):
        if hier[k][3] != -1 or len(c) < 3:
            continue
        ext = [(X0 + (x + 0.5) / RES, Y1 - (y + 0.5) / RES) for x, y in c[:, 0, :]]
        holes = []
        ch = hier[k][2]
        while ch != -1:
            if len(cs[ch]) >= 3:
                holes.append([(X0 + (x + 0.5) / RES, Y1 - (y + 0.5) / RES) for x, y in cs[ch][:, 0, :]])
            ch = hier[ch][0]
        pg = Polygon(ext, holes).buffer(0)
        out.append(pg)
    return unary_union(out).simplify(0.04)


REG = {"paving": vec(default_paving), "deck": vec(ids["deck"]), "lawn": vec(ids["lawn"]), "water": vec(ids["kids_pool"])}

# ---- precedence: later layers win -----------------------------------------------------------------
layers = [("paving", REG["paving"]), ("deck", REG["deck"]), ("lawn", REG["lawn"])]
for k in ("concrete", "paving", "terracotta", "terrace", "stabilise", "lane", "lawn", "ramp"):
    layers.append((k, unary_union([h["geom"] for h in HCLS.get(k, [])])))
water_h = [h for h in HCLS.get("water", [])]
layers.append(("water", unary_union([h["geom"] for h in water_h] + [REG["water"]])))
final = defaultdict(list)
acc = Polygon()
for k, g in reversed(layers):
    g = g.intersection(T1).difference(acc).buffer(0)
    acc = unary_union([acc, g])
    final[k].append(g)
surf = {}
for k, gl in final.items():
    g = unary_union(gl)
    g = unary_union([p for p in as_polys(g) if p.area > 0.05])
    surf[k] = poly_out(gloc(g))
    print(f"  surface {k:11s} {gloc(g).area:9.1f} m2  {len(surf[k])} polys")
surf["asphalt_base"] = poly_out(gloc(T1))
site["surfaces"] = surf

# water bodies, by kind
wb = []
for h in water_h:
    kind = {"PR": "pool", "VERDURE": "fountain", "bassin": "bassin"}[h["layer"]]
    if kind == "bassin" and h["path"] and h["path"][0] == "RVT 01":
        kind = "median"            # entrance median: no water (15-10 request), paved like the plan's hatch
    elif kind == "bassin" and h["path"] and h["path"][0] == "RESTAURANT MIRLEFT":
        kind = "resto_bassin"      # the restaurant is built from its own plan, bassins included
    for pg in as_polys(h["geom"]):
        wb.append({"kind": kind, "poly": poly_out(gloc(pg))[0]})
for pg in as_polys(REG["water"]):
    wb.append({"kind": "kids_pool", "poly": poly_out(gloc(pg))[0]})
site["water"] = wb
print("  water bodies", Counter(w["kind"] for w in wb))


# ---- duplex pairs: two repeated blocks ----------------------------------------------------------
# block-local point of the model origin (joint axis; side-part front face at y = -3.47 of the permit)
DPX_REF = {"ghghhg": ("A", 47906.70, 290197.535), "jjjsdrf1554": ("B", 48022.63, 290272.355)}
RDC = unary_union([box(-8.10, -3.47, 8.10, 5.35), box(-3.52, -7.27, 3.52, -3.47)])
labels = [(p["pts"][0][:2], str(p["text"])) for p in P if p["k"] == "text" and p["layer"] == "construction" and str(p["text"]).startswith("D-")]
dups, houses = [], []
for g in INS:
    if g["name"] not in DPX_REF:
        continue
    typ, bx, by = DPX_REF[g["name"]]
    A, t = g["A"], g["t"]
    c = (A[0][0] * bx + A[0][1] * by + t[0], A[1][0] * bx + A[1][1] * by + t[1])
    rot = g["rot"] + 90.0
    units = sorted([n for _, n in sorted(labels, key=lambda nt: math.dist(nt[0], c))[:2]], key=lambda s_: int(s_[2:]))
    dups.append({"type": typ, "units": units, "c": [round(v, 3) for v in loc(c)], "rot_deg": round(rot, 3)})
    houses.append(affinity.translate(affinity.rotate(RDC, rot, origin=(0, 0)), c[0], c[1]))
dups.sort(key=lambda d: int(d["units"][0][2:]))
site["duplexes"] = dups
print("duplexes", [(d["type"], "/".join(d["units"])) for d in dups])

# ---- gardens, planters and walls -----------------------------------------------------------------
DBLK = ("D1-D2", "D3-D4", "D5-D8", "D9-D12", "D13-D16+", "D17-D18", "D19-D24", "JARDINIERES D1-D4")
gardens, planters = [], []
house_u = unary_union(houses)
near_house = house_u.buffer(0.9, join_style=2)
for h in HCLS["lawn"]:
    blk = h["path"][0] if h["path"] else ""
    if blk not in DBLK:
        continue
    for pg in as_polys(h["geom"]):
        if pg.area >= 15 and pg.intersects(near_house):
            gardens.append(pg)                       # plot garden: walled
        elif pg.area < 40:
            planters.append(pg)                      # 'Jardin' beds on the pavements: raised planters
SOLID_WALLS = {("01-murs ext", (255, 0, 0), "SOLID"): ("garden", 1.80),             # rear wall of row B along the 8.5 m road
               ("08-hachures", (205, 105, 40), "SOLID"): ("garden", 1.80),          # walls of the small gardens south of D-3/4
               ("-id-structure jardin", (255, 255, 255), "ANSI37"): ("enclosure", 1.20),   # pétanque, east boundary
               ("08-hachures", (212, 186, 43), "SOLID"): ("pool", 1.10)}            # pool terrace enclosure (north / west)
solid = [(h, SOLID_WALLS[(h["layer"], h["rgb"], h["pat"])]) for h in HATCH
         if (h["layer"], h["rgb"], h["pat"]) in SOLID_WALLS and T1.intersects(h["geom"])]
solid_u = unary_union([h["geom"] for h, _ in solid])
# Walls run along the garden edges, except where the edge faces the house: the plan draws lawn up to the
# house, or (D-3/D-4) a 1 m paved band round it, and no wall there. An edge segment running along a house
# wholly within 2 m of it is that edge; one within 0.7 m of a wall the plan draws is that wall, not a second one.
cut = house_u.buffer(0.55, join_style=2)
near_h = house_u.buffer(2.0, join_style=2)
near_w = solid_u.buffer(0.7)
segs_w = []
for pg in gardens:
    edge = pg.exterior.difference(cut)
    for ln in getattr(edge, "geoms", [edge]):
        if ln.is_empty:
            continue
        c_ = list(ln.coords)
        for a_, b_ in zip(c_, c_[1:]):
            pts3 = [Point(a_), Point(b_), Point(((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2))]
            along = abs(house_u.distance(pts3[0]) - house_u.distance(pts3[1])) < 0.5 * math.dist(a_, b_)
            if (along and all(near_h.contains(q) for q in pts3)) or all(near_w.contains(q) for q in pts3):
                continue                     # (a short piece joining a wall to the house is kept)
            segs_w.append(LineString([a_, b_]))
garden_walls = unary_union([l.buffer(0.10, cap_style=2, join_style=2) for l in segs_w])
garden_walls = unary_union([p for p in as_polys(garden_walls.difference(house_u)) if p.area > 0.08])
walls = [{"kind": "garden", "h": 1.80, "poly": q} for q in poly_out(gloc(garden_walls))]
band = house_u.buffer(1.10, join_style=2)          # the 1 m band round D-3/D-4 stays clear of the plot walls
for h, (kind, hh) in solid:
    g = h["geom"].difference(band) if kind == "garden" else h["geom"]
    for q in poly_out(gloc(g)):
        walls.append({"kind": kind, "h": hh, "poly": q})
# the 'JARDIN' plots beside D-4 (PISCINE block) are drawn 0.6 m into the band: closed by a wall on the
# band edge, their lawn stops there and the band is paved
plots = unary_union([h["geom"] for h in HCLS["lawn"] if h["path"] and h["path"][0] == "PISCINE"])
over = band.intersection(plots.buffer(0.05))
if not over.is_empty:
    closing = band.buffer(0.20, join_style=2).difference(band).intersection(plots.buffer(0.05))
    for q in poly_out(gloc(closing)):
        walls.append({"kind": "garden", "h": 1.80, "poly": q})
    sl = unary_union([Polygon(p["ext"], p["holes"]).buffer(0) for p in site["surfaces"]["lawn"]])
    sp = unary_union([Polygon(p["ext"], p["holes"]).buffer(0) for p in site["surfaces"]["paving"]])
    ov = gloc(over)
    site["surfaces"]["lawn"] = poly_out(sl.difference(ov))
    site["surfaces"]["paving"] = poly_out(sp.union(ov.intersection(sl)))
    print("  band beside D-4: plot lawn trimmed", round(ov.intersection(sl).area, 1), "m2")
# '03-vue' grey solid: walls of the local technique block (building) and the retaining wall along the south road
LT_BOX = box(251970, 119383, 251990, 119412)
lt_walls = []
for h in HATCH:
    if (h["layer"], h["rgb"], h["pat"]) == ("03-vue", (99, 100, 102), "SOLID"):
        for pg in as_polys(h["geom"]):
            if LT_BOX.contains(pg.centroid) and pg.area < 8:
                lt_walls.append(pg)
            else:
                walls.append({"kind": "retaining", "h": 1.0, "poly": poly_out(gloc(pg))[0]})
site["walls"] = walls
site["planters"] = poly_out(gloc(unary_union(planters)))
site["local_technique_walls"] = poly_out(gloc(unary_union(lt_walls)))
print("walls", Counter(w["kind"] for w in walls), " planters", len(site["planters"]), " gardens", len(gardens))


# ---- per-instance symbols (trees, meters, bins) --------------------------------------------------
def instances(name):
    inst = defaultdict(list)
    for p in P:
        if name in p["path"]:
            inst[p["iids"][p["path"].index(name)]].extend(pts2(p))
    out = []
    for k in sorted(inst):
        a = np.array(inst[k])
        lo, hi = a.min(0), a.max(0)
        out.append(((lo + hi) / 2, float((hi - lo).max() / 2)))
    return out


trees = []
for name, kind in (("cay10", "palm"), ("Plant Pln 004.", "olive"), ("palmier", "washingtonia"), ("uyuryuy", "shade")):
    for c, r in instances(name):
        if T1.contains(Point(c)):
            trees.append({"kind": kind, "c": [round(v, 3) for v in loc(c)], "r": round(r, 2)})
pits = []
for p in P:
    if p["k"] == "line" and p["closed"] and len(p["pts"]) >= 30:
        a_ = np.array(pts2(p))
        cen = a_.mean(0)
        r = np.linalg.norm(a_ - cen, axis=1)
        if r.std() < 0.02 and abs(r.mean() - 0.6) < 0.03 and p["layer"] == "01-murs ext":
            pits.append(cen)
        if r.std() < 0.02 and abs(r.mean() - 0.5) < 0.03 and p["path"] and p["path"][0] == "PARKING 2 + PETANQUE":
            if all(math.dist(cen, (t_["c"][0] + O[0], t_["c"][1] + O[1])) > 0.3 for t_ in trees):
                trees.append({"kind": "shade", "c": [round(v, 3) for v in loc(cen)], "r": 0.5})
uniq = []
for c in pits:
    if all(math.dist(c, u) > 0.2 for u in uniq):
        uniq.append(c)
for c in uniq:
    trees.append({"kind": "pit", "c": [round(v, 3) for v in loc(c)], "r": 0.6})
site["trees"] = trees
print("trees", Counter(t["kind"] for t in trees))

ins_by = defaultdict(list)
for g in INS:
    ins_by[g["name"]].append(g)
small = []
for name, kind in (("EMPLACEMENT COMPTEUR", "meter"), ("POUBELLE", "bin")):
    for (c, r), g in zip(instances(name), ins_by[name]):
        small.append({"kind": kind, "c": [round(v, 3) for v in loc(c)], "rot_deg": round(g["rot"], 2)})
site["street_furniture"] = small
print("meters/bins", Counter(s_["kind"] for s_ in small))


# ---- public buildings ----------------------------------------------------------------------------
def block_point(name, bx, by):
    g = ins_by[name][0]
    A, t = g["A"], g["t"]
    return (A[0][0] * bx + A[0][1] * by + t[0], A[1][0] * bx + A[1][1] * by + t[1]), g["rot"]


c, r = block_point("dfhgfdjjj", 2327.925, 1443.41)      # restaurant: centre between the four towers
site["restaurant"] = {"c": [round(v, 3) for v in loc(c)], "rot_deg": round(r, 3)}
site["commerces"] = {"c": [round(v, 3) for v in loc((252049.5, 119448.0))], "rot_deg": -9.46}
toilet = Polygon([(252032.64, 119436.57), (252035.6, 119436.1), (252035.12, 119433.09), (252032.16, 119433.56)])
site["toilet_kiosk"] = {"c": [round(v, 3) for v in loc(toilet.centroid.coords[0])], "rot_deg": -9.0, "size": 3.0}
site["pool"] = {"c": [round(v, 3) for v in loc((251999.57, 119407.49))], "rot_deg": -24.02}
site["petanque"] = {"c": [round(v, 3) for v in loc((252088.0, 119445.0))], "rot_deg": -10.5}

# loungers (transats): clusters of the 'PERSONE' drawings around the pool
segs = [LineString(pts2(p)) for p in P if p["layer"] == "PERSONE" and len(p["pts"]) > 1]
lou = []
for g in as_polys(unary_union([s_.buffer(0.06) for s_ in segs])):
    rr = g.minimum_rotated_rectangle
    cc = list(rr.exterior.coords)
    e = sorted([(math.dist(cc[i], cc[i + 1]), math.degrees(math.atan2(cc[i + 1][1] - cc[i][1], cc[i + 1][0] - cc[i][0]))) for i in range(2)])
    n_ = 2 if e[0][0] > 1.2 else 1                 # one drawing of two side-by-side loungers
    lou.append({"c": [round(v, 3) for v in loc(g.centroid.coords[0])], "rot_deg": round(e[1][1], 2), "n": n_})
site["loungers"] = lou
print("loungers", len(lou), sum(l_["n"] for l_ in lou))

# stairs crossing the rows ('ESC 16-17' = escaliers existants between D-16 and D-17, 'ESC V4')
stairs = []
for name in ("ESC 16-17", "ESC V4"):
    ls = [LineString(pts2(p)) for p in P if p["path"] and p["path"][0] == name and p["k"] == "line" and len(p["pts"]) > 1]
    rr = unary_union(ls).minimum_rotated_rectangle
    cc = [np.array(q) for q in list(rr.exterior.coords)[:4]]
    if np.linalg.norm(cc[1] - cc[0]) >= np.linalg.norm(cc[2] - cc[1]):
        eA, eB, wd = (cc[3] + cc[0]) / 2, (cc[1] + cc[2]) / 2, np.linalg.norm(cc[2] - cc[1])
    else:
        eA, eB, wd = (cc[0] + cc[1]) / 2, (cc[2] + cc[3]) / 2, np.linalg.norm(cc[1] - cc[0])
    ax = (eB - eA) / np.linalg.norm(eB - eA)
    ts = []                                   # riser lines: across the stair (each half of it, split by the centre rail)
    for l_ in ls:
        q = np.array(l_.coords)
        for a_, b_ in zip(q, q[1:]):
            v_ = b_ - a_
            n_ = np.linalg.norm(v_)
            if n_ >= 0.3 * wd and abs(np.dot(v_ / n_, ax)) < 0.2:
                t_ = float(np.dot((a_ + b_) / 2 - eA, ax))
                if all(abs(t_ - u_) > 0.15 for u_ in ts):
                    ts.append(t_)
    ts.sort()
    flights, cur = [], [ts[0]]
    for t_ in ts[1:]:
        if t_ - cur[-1] > 1.2:
            flights.append(cur)
            cur = [t_]
        else:
            cur.append(t_)
    flights.append(cur)
    flights = [[round(f[0], 3), round(f[-1], 3), len(f)] for f in flights if len(f) >= 3]
    stairs.append({"name": name, "poly": poly_out(gloc(rr))[0], "n_lines": len(ls),
                   "axis": [list(np.round(loc(eA), 3)), list(np.round(loc(eB), 3))], "width": round(float(wd), 3),
                   "flights": flights})
    print("stair", name, "length", round(float(np.linalg.norm(eB - eA)), 2), "width", round(float(wd), 2), "flights", flights)
site["stairs"] = stairs

# road paint: the pedestrian crossings the plan draws, as flat paint (15-10 request). Entrance and median:
# blocks 'DFGW' / 'xwdfrg' (solid stripes); the 8.5 m road at the stair exits: 'TRACAGE VOIRIE' stripes
# drawn as open outlines. Direction arrows and parking marks stay out.
zeb = [h["geom"] for h in HATCH if any(n in h["path"] for n in ("DFGW", "xwdfrg")) and h["geom"].area < 2.0]
for p in P:
    if "TRACAGE VOIRIE" in p["path"] and p["layer"] == "-id-structure jardin" and p["k"] == "line" and 4 <= len(p["pts"]) <= 5:
        g = Polygon(pts2(p)).buffer(0)
        if g.is_empty:
            continue
        rr = g.minimum_rotated_rectangle
        cc = list(rr.exterior.coords)
        e = sorted(math.dist(cc[i], cc[i + 1]) for i in range(2))
        if 0.25 <= e[0] <= 0.7 and 2.0 <= e[1] <= 4.0 and g.area > 0.8 * e[0] * e[1]:
            zeb.append(g)
zeb = [g for g in as_polys(unary_union(zeb)) if T1.intersects(g)]
site["road_paint"] = [{"kind": "zebra", "poly": q} for g in zeb for q in poly_out(gloc(g))]
print("road paint: zebra stripes", len(site["road_paint"]))

json.dump(site, open(os.path.join(ROOT, "data", "site.json"), "w"))
print("wrote", os.path.join(ROOT, "data", "site.json"))
