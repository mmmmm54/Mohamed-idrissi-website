"""Explode a libredwg-web JSON DWG into flat primitives in model space (world coordinates).
Usage: python -I flatten.py in.json out.pkl
Primitive: dict(k=kind, layer, rgb, pts=[(x,y,z)...], closed, text, h, path, iids)  kinds: line, hatch, text, face
  path / iids: names and instance numbers of the blocks the primitive sits in (outermost first)
  hatch: one primitive per boundary loop; loops of the same HATCH share `hid` (even-odd fill)"""
import json, math, pickle, sys, colorsys

def aci_rgb(i):
    base = {1: (255, 0, 0), 2: (255, 255, 0), 3: (0, 255, 0), 4: (0, 255, 255), 5: (0, 0, 255), 6: (255, 0, 255), 7: (255, 255, 255),
            8: (128, 128, 128), 9: (192, 192, 192)}
    if i in base: return base[i]
    if 250 <= i <= 255:
        v = int(51 + (i - 250) * 40.8); return (v, v, v)
    if 10 <= i <= 249:
        h = ((i - 10) // 10) * 15 / 360.0
        sub = (i - 10) % 10
        v = [1.0, 1.0, 0.8, 0.8, 0.6, 0.6, 0.5, 0.5, 0.3, 0.3][sub]
        s = 1.0 if sub % 2 == 0 else 0.5
        r, g, b = colorsys.hsv_to_rgb(h, s, v); return (int(r * 255), int(g * 255), int(b * 255))
    return (200, 200, 200)

db = json.load(open(sys.argv[1]))
LAY = {l["name"]: l for l in db["tables"]["LAYER"]["entries"]}
BLK = {b["name"]: b for b in db["tables"]["BLOCK_RECORD"]["entries"]}
out = []
HID = [0]
PATH = []
IID = [0]

def ent_rgb(e, layer, parent_rgb):
    c = e.get("color")
    ci = e.get("colorIndex", 256)
    if c is not None and ci not in (0, 256):
        return ((c >> 16) & 255, (c >> 8) & 255, c & 255)
    if ci == 0:  # BYBLOCK
        return parent_rgb
    if ci == 256 or ci is None:
        L = LAY.get(layer, {})
        lc = L.get("color")
        if lc is not None and L.get("colorIndex", 7) not in (7,):
            return aci_rgb(L.get("colorIndex", 7))
        return aci_rgb(L.get("colorIndex", 7))
    return aci_rgb(ci)

def xf_make(ins, base):
    sx, sy, sz = ins.get("xScale", 1) or 1, ins.get("yScale", 1) or 1, ins.get("zScale", 1) or 1
    r = ins.get("rotation", 0) or 0
    ex = ins.get("extrusionDirection", {}).get("z", 1)
    p = ins["insertionPoint"]; bx, by, bz = base
    c, s = math.cos(r), math.sin(r)
    def f(x, y, z=0.0):
        x, y, z = (x - bx) * sx, (y - by) * sy, (z - bz) * sz
        if ex < 0: x = -x
        return (p["x"] + c * x - s * y, p["y"] + s * x + c * y, p.get("z", 0) + z)
    return f

def bulge_pts(v, closed):
    pts = []
    n = len(v)
    for i in range(n if closed else n - 1):
        a, b = v[i], v[(i + 1) % n]
        pts.append((a["x"], a["y"]))
        bu = a.get("bulge", 0) or 0
        if abs(bu) > 1e-6:
            th = 4 * math.atan(bu)
            dx, dy = b["x"] - a["x"], b["y"] - a["y"]; ch = math.hypot(dx, dy)
            if ch > 0:
                rad = ch / (2 * math.sin(th / 2))
                mx, my = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
                d = rad * math.cos(th / 2)
                nx, ny = -dy / ch, dx / ch
                cx, cy = mx + nx * d * (1 if bu > 0 else -1) * (1 if rad > 0 else -1), my + ny * d * (1 if bu > 0 else -1) * (1 if rad > 0 else -1)
                a0 = math.atan2(a["y"] - cy, a["x"] - cx); a1 = math.atan2(b["y"] - cy, b["x"] - cx)
                if bu > 0 and a1 < a0: a1 += 2 * math.pi
                if bu < 0 and a1 > a0: a1 -= 2 * math.pi
                R = math.hypot(a["x"] - cx, a["y"] - cy)
                k = max(2, int(abs(a1 - a0) / 0.2))
                for j in range(1, k):
                    t = a0 + (a1 - a0) * j / k
                    pts.append((cx + R * math.cos(t), cy + R * math.sin(t)))
    if not closed: pts.append((v[-1]["x"], v[-1]["y"]))
    return pts

def arc_pts(cx, cy, R, a0, a1):
    if a1 < a0: a1 += 2 * math.pi
    k = max(4, int((a1 - a0) / 0.15))
    return [(cx + R * math.cos(a0 + (a1 - a0) * j / k), cy + R * math.sin(a0 + (a1 - a0) * j / k)) for j in range(k + 1)]

def emit(kind, e, layer, rgb, pts, f, closed=False, **kw):
    P = [f(*p) if len(p) == 3 else f(p[0], p[1]) for p in pts]
    out.append(dict(k=kind, layer=layer, rgb=rgb, pts=P, closed=closed, path=tuple(n for n, _ in PATH), iids=tuple(i for _, i in PATH), **kw))

def walk(ents, f, depth, parent_layer, parent_rgb):
    if depth > 8: return
    for e in ents:
        t = e["type"]
        layer = e.get("layer", "0")
        if layer == "0" and parent_layer: layer = parent_layer
        L = LAY.get(layer, {})
        if L.get("off") or L.get("frozen"): continue
        rgb = ent_rgb(e, layer, parent_rgb)
        try:
            if t == "LINE":
                a, b = e["startPoint"], e["endPoint"]
                emit("line", e, layer, rgb, [(a["x"], a["y"], a.get("z", 0)), (b["x"], b["y"], b.get("z", 0))], f)
            elif t == "LWPOLYLINE":
                v = e["vertices"]
                if len(v) > 1:
                    cl = bool(e.get("flag", 0) & 1)
                    emit("line", e, layer, rgb, bulge_pts(v, cl), f, cl)
            elif t in ("POLYLINE2D", "POLYLINE3D"):
                v = [x for x in e["vertices"] if not (x.get("flag", 0) & 16)]
                if len(v) > 1: emit("line", e, layer, rgb, [(x["x"], x["y"], x.get("z", 0)) for x in v], f, bool(e.get("flag", 0) & 1))
            elif t == "CIRCLE":
                c = e["center"]; emit("line", e, layer, rgb, arc_pts(c["x"], c["y"], e["radius"], 0, 2 * math.pi), f, True)
            elif t == "ARC":
                c = e["center"]; emit("line", e, layer, rgb, arc_pts(c["x"], c["y"], e["radius"], e["startAngle"], e["endAngle"]), f)
            elif t == "ELLIPSE":
                c, m = e["center"], e["majorAxisEndPoint"]; R = math.hypot(m["x"], m["y"]); r = R * e["axisRatio"]; rot = math.atan2(m["y"], m["x"])
                a0, a1 = e["startAngle"], e["endAngle"]
                if a1 < a0: a1 += 2 * math.pi
                k = max(8, int((a1 - a0) / 0.15))
                pts = []
                for j in range(k + 1):
                    tt = a0 + (a1 - a0) * j / k; x, y = R * math.cos(tt), r * math.sin(tt)
                    pts.append((c["x"] + x * math.cos(rot) - y * math.sin(rot), c["y"] + x * math.sin(rot) + y * math.cos(rot)))
                emit("line", e, layer, rgb, pts, f)
            elif t == "SPLINE":
                cp = e.get("fitPoints") or e.get("controlPoints") or []
                if len(cp) > 1: emit("line", e, layer, rgb, [(p["x"], p["y"], p.get("z", 0)) for p in cp], f)
            elif t == "HATCH":
                HID[0] += 1
                for bp in e.get("boundaryPaths", []):
                    if bp.get("vertices"):
                        pts = bulge_pts(bp["vertices"], True)
                    else:
                        pts = []
                        for ed in bp.get("edges", []):
                            if ed.get("type") == 1 and "start" in ed: pts.append((ed["start"]["x"], ed["start"]["y"]))
                            elif ed.get("type") == 2 and "center" in ed:
                                c = ed["center"]; a0, a1 = ed.get("startAngle", 0), ed.get("endAngle", 0)
                                seg = arc_pts(c["x"], c["y"], ed["radius"], a0, a1) if ed.get("isCCW", 1) else list(reversed(arc_pts(c["x"], c["y"], ed["radius"], -a1, -a0)))
                                pts += seg
                            elif "controlPoints" in ed:
                                pts += [(p["x"], p["y"]) for p in ed["controlPoints"]]
                    if len(pts) > 2:
                        emit("hatch", e, layer, rgb, pts, f, True, solid=e.get("solidFill", 0), pat=e.get("patternName"), hid=HID[0])
            elif t in ("TEXT", "MTEXT"):
                p = e.get("insertionPoint") if t == "MTEXT" else e.get("startPoint")
                import re
                txt = re.sub(r"\\[A-Za-z][^;]*;", "", e.get("text", "")); txt = re.sub(r"[{}]", "", txt).replace("\\P", " ").strip()
                if p and txt: emit("text", e, layer, rgb, [(p["x"], p["y"], 0)], f, text=txt, h=e.get("textHeight", 0))
            elif t in ("SOLID", "3DFACE"):
                cs = [e[k] for k in ("corner1", "corner2", "corner3", "corner4") if k in e]
                pts = [(c["x"], c["y"], c.get("z", 0)) for c in cs]
                if t == "SOLID" and len(pts) == 4: pts = [pts[0], pts[1], pts[3], pts[2]]
                emit("face", e, layer, rgb, pts, f, True)
            elif t == "INSERT":
                b = BLK.get(e["name"])
                if not b or not b.get("entities"): continue
                bp = b.get("basePoint") or {"x": 0, "y": 0, "z": 0}
                inner = xf_make(e, (bp.get("x", 0), bp.get("y", 0), bp.get("z", 0)))
                g = (lambda inner: (lambda x, y, z=0.0: f(*inner(x, y, z))))(inner)
                IID[0] += 1
                PATH.append((e["name"], IID[0]))
                walk(b["entities"], g, depth + 1, layer if layer != "0" else parent_layer, rgb)
                PATH.pop()
                for a in e.get("attribs", []) or []:
                    if a.get("text"): emit("text", a, layer, rgb, [(a.get("startPoint", a.get("insertionPoint", {"x": 0, "y": 0}))["x"], a.get("startPoint", a.get("insertionPoint", {"x": 0, "y": 0}))["y"], 0)], f, text=a["text"], h=a.get("textHeight", 0))
        except Exception as ex:
            pass

ident = lambda x, y, z=0.0: (x, y, z)
ms = BLK.get("*Model_Space")
walk(ms["entities"] if ms else db["entities"], ident, 0, None, (255, 255, 255))
pickle.dump(out, open(sys.argv[2], "wb"))
import collections
print(len(out), collections.Counter(o["k"] for o in out))
