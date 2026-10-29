"""
01_parse_dwg — reads the client's DWG (converted to JSON with libredwg-web) and writes
data/facades.json: windows, coloured window surrounds, coloured blocks, railings and the door of
every drawn facade, in building-local metres.

Building frame: x = 0 at the left facade (FACADE GAUCHE), x = 9.00 at the right party wall;
y = 0 at the main facade (FACADE PRINCIPALE, entrance), y = 9.90 at the rear facade;
z = 0 at the street / garden level (the facades' ground line; RDC floor is +0.50).
Every value is read off the signed permit drawing (planche 1/1, 1/100, DWG in millimetres).
Colours: the DWG hatch's true colour; hatches with an index colour only are sampled from the PDF.

    python -I 01_parse_dwg.py <dwg.json> <signed.pdf> <out.json>
"""
import json
import sys

import numpy as np

SRC, PDF, OUT = sys.argv[1:4]
db = json.load(open(SRC))

# facade view frames on the sheet (DWG mm): origin x, ground y, direction of the local axis
FACADES = {
    #  name           view box (x0, y0, x1, y1)            u0 (DWG x at local 0)  sign  ground y   length
    "front": dict(box=(336500, -41000, 346500, -31800), u0=336990, sign=+1, ground=-40574, length=9.00),
    "left":  dict(box=(337000, -30000, 347500, -21000), u0=347294, sign=-1, ground=-29659, length=9.90),
    "rear":  dict(box=(350000, -54200, 359800, -45300), u0=359408, sign=-1, ground=-53863, length=9.00),
}
GLASS = (204, 210, 207)
FRAME = (216, 204, 181)
RAIL = (207, 207, 211)

# ---- PDF colour sampler (for index-colour hatches) -------------------------------------------
import pymupdf
from PIL import Image
pg = pymupdf.open(PDF)[0]
DPI = 300
pix = pg.get_pixmap(dpi=DPI)
IMG = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
# DWG -> PDF points (least squares on five labels, residual < 1.2 pt): see the session notes
CX = (2.83464561e-02, -7.49013629e-11, -8.41264251e+03)
CY = (2.43045320e-05, -2.83357078e-02, -5.48961668e+02)


def pdf_rgb(x, y):
    px = (CX[0] * x + CX[1] * y + CX[2]) * DPI / 72.0
    py = (CY[0] * x + CY[1] * y + CY[2]) * DPI / 72.0
    return IMG.getpixel((int(px), int(py)))


# ---- hatches ---------------------------------------------------------------------------------
rects = []
for i, e in enumerate(db["entities"]):
    if e["type"] != "HATCH":
        continue
    for bp in e.get("boundaryPaths", []):
        pts = [(v["x"], v["y"]) for v in bp.get("vertices", [])] or \
              [(ed["start"]["x"], ed["start"]["y"]) for ed in bp.get("edges", []) if "start" in ed]
        if len(pts) < 3:
            continue
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        is_rect = all(min(abs(p[0] - x0), abs(p[0] - x1)) < 2 and min(abs(p[1] - y0), abs(p[1] - y1)) < 2 for p in pts)
        if not is_rect:
            continue                                            # drawn shadows are slanted polygons
        c = e.get("color")
        rgb = ((c >> 16) & 255, (c >> 8) & 255, c & 255) if c is not None else None
        rects.append(dict(i=i, x0=x0, x1=x1, y0=y0, y1=y1, rgb=rgb))


def in_box(r, b):
    return r["x0"] >= b[0] and r["x1"] <= b[2] and r["y0"] >= b[1] and r["y1"] <= b[3]


def to_local(f, r):
    a = (r["x0"] - f["u0"]) * f["sign"] / 1000.0
    b = (r["x1"] - f["u0"]) * f["sign"] / 1000.0
    return [round(min(a, b), 3), round((r["y0"] - f["ground"]) / 1000.0, 3), round(max(a, b), 3), round((r["y1"] - f["ground"]) / 1000.0, 3)]


def colour(r):
    if r["rgb"] is not None:
        return list(r["rgb"])
    # sample inside, away from edges
    return list(pdf_rgb(r["x0"] + 0.3 * (r["x1"] - r["x0"]), r["y0"] + 0.3 * (r["y1"] - r["y0"])))


out = {}
for name, f in FACADES.items():
    R = [r for r in rects if in_box(r, f["box"])]
    w = lambda r: r["x1"] - r["x0"]
    h = lambda r: r["y1"] - r["y0"]
    # blocks: 0.50 x 0.50 squares (last drawn wins at a position)
    blocks = {}
    for r in sorted(R, key=lambda r: r["i"]):
        if 470 < w(r) < 530 and 470 < h(r) < 530 and r["rgb"] not in (GLASS, FRAME, RAIL):
            blocks[(round(r["x0"] / 50), round(r["y0"] / 50))] = r
    # window glass panes
    panes = [r for r in R if r["rgb"] == GLASS and w(r) > 80 and h(r) > 80]
    # cluster panes into windows (gap < 0.35 m)
    clusters = []
    for p in sorted(panes, key=lambda r: (r["y0"], r["x0"])):
        for cl in clusters:
            if any(p["x0"] < q["x1"] + 350 and q["x0"] < p["x1"] + 350 and p["y0"] < q["y1"] + 350 and q["y0"] < p["y1"] + 350 for q in cl):
                cl.append(p)
                break
        else:
            clusters.append([p])
    frames = [r for r in R if r["rgb"] == FRAME]
    windows = []
    for cl in clusters:
        bx = [min(q["x0"] for q in cl), min(q["y0"] for q in cl), max(q["x1"] for q in cl), max(q["y1"] for q in cl)]
        fr = [r for r in frames if r["x0"] > bx[0] - 260 and r["x1"] < bx[2] + 260 and r["y0"] > bx[1] - 260 and r["y1"] < bx[3] + 260]
        ob = [min([bx[0]] + [r["x0"] for r in fr]), min([bx[1]] + [r["y0"] for r in fr]),
              max([bx[2]] + [r["x1"] for r in fr]), max([bx[3]] + [r["y1"] for r in fr])]
        windows.append(dict(opening=to_local(f, dict(x0=ob[0], x1=ob[2], y0=ob[1], y1=ob[3])),
                            panes=[to_local(f, q) for q in sorted(cl, key=lambda q: q["x0"] * f["sign"])]))
    # coloured surrounds: an outer rect with an inner rect (the opening) 0.10-0.40 m inside it on every side
    surrounds = []
    sat = [r for r in R if r["rgb"] not in (GLASS, FRAME, RAIL) and w(r) > 900 and h(r) > 900]
    for r in sat:   # true colour, or sampled 80 mm inside the outer edge (on the ring, not the glass)
        r["c"] = tuple(r["rgb"]) if r["rgb"] is not None else tuple(pdf_rgb(r["x0"] + 80, (r["y0"] + r["y1"]) / 2))
    used = set()
    for o in sorted(sat, key=lambda r: -(w(r) * h(r))):
        if id(o) in used:
            continue
        for n in sorted(sat, key=lambda r: -(w(r) * h(r))):
            if n is o or id(n) in used:
                continue
            m = (n["x0"] - o["x0"], o["x1"] - n["x1"], n["y0"] - o["y0"], o["y1"] - n["y1"])
            if all(90 < v < 420 for v in m):
                surrounds.append(dict(outer=to_local(f, o), inner=to_local(f, n), rgb=list(o["c"])))
                used.add(id(n)); used.add(id(o))
                break
    rails = [to_local(f, r) for r in R if r["rgb"] == RAIL and w(r) > 200 and h(r) > 200]
    out[name] = dict(blocks=[dict(rect=to_local(f, r), rgb=colour(r)) for r in blocks.values()],
                     windows=windows, surrounds=surrounds, rails=rails)
    print(name, {k: len(v) for k, v in out[name].items()})
json.dump(out, open(OUT, "w"), indent=1)
