"""
21_plants — the detailed plant library and garden objects (client 26-10: "pour nkhal mabghitch had model dyal nkhal
because is soo sample and not realistic ... create something perfect with details"; the client's notes on the
aménagement paysager: the jars, the plants and everything of the gardens, the planting along the walls and the big
stairs as the pool reference).

Every plant is real geometry (no alpha cards but the grass plumes), so it reads the same in Cycles, D5 and a GLB
viewer, and every material is one image texture (generated here, data/textures/TEX_V2_*) on a Principled BSDF:
  date_palm      Phoenix dactylifera: a trunk of diamond leaf bases (relief and texture on the same lattice), the
                 crown bulb, 36 to 44 arching pinnate fronds of folded leaflets set in two planes (the palm's V),
                 spines on the petioles, yellowing old fronds and a few hanging dead ones, date bunches;
  washingtonia   Washingtonia robusta: a slender ringed trunk flaring at its foot, the criss-cross leaf bases under
                 the crown, about 28 costapalmate fans of pleated segments drooping at their split tips on spiny
                 petioles, two spear leaves, a skirt of dead fronds (skirt=True) or a trimmed head;
  grass          fountain grass: arching blades and feathery plumes;
  agave          Agave americana: thick keeled leaves with their terminal spines, blue grey;
  lavender       a lavender mound: grey needles and purple flower spikes;
  jar            the terracotta jars (khabia, amphora), turned;
Placement is done by the tranches' scripts (05, 13, 19, 20) with the keys of 05's srcv.
"""
import math
import os
import random

import bpy
import numpy as np

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEX = os.path.join(ROOT, "data", "textures")
GOLD = math.pi * (3.0 - math.sqrt(5.0))


# ---- textures (numpy, PIL) ---------------------------------------------------------------------------------
def _hex(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def _noise(shape, scale, rng, octaves=4):
    """smooth value noise, tileable, values about 0..1"""
    from PIL import Image
    h, w = shape
    out = np.zeros(shape)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        sy, sx = max(2, int(h / scale * 2 ** o)), max(2, int(w / scale * 2 ** o))
        g = rng.random((sy, sx))
        g = np.concatenate([g, g[:1]], 0)
        g = np.concatenate([g, g[:, :1]], 1)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w + w // sx, h + h // sy), Image.BICUBIC)
        out += amp * np.asarray(im)[:h, :w] / 255.0
        tot += amp
        amp *= 0.5
    return out / tot


def _save(name, a):
    from PIL import Image
    os.makedirs(TEX, exist_ok=True)
    p = os.path.join(TEX, name)
    if a.shape[-1] == 4:
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA").save(p)
    else:
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").save(p, quality=92)
    return p


def tex_leaflet(name, base, mid, tip, seed, dry_tip=0.0, rib="#C8C59A", w=96, h=768):
    """a leaf strip: u across (midrib at 0.5), v from base to tip; fine parallel veins, a lighter midrib"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    rng = np.random.default_rng(seed)
    v = np.linspace(0, 1, h)[:, None]
    u = np.linspace(0, 1, w)[None, :]
    c0, c1, c2 = _hex(base), _hex(mid), _hex(tip)
    col = np.where(v[..., None] < 0.5, c0 + (c1 - c0) * (v[..., None] / 0.5), c1 + (c2 - c1) * ((v[..., None] - 0.5) / 0.5))
    col = np.broadcast_to(col, (h, w, 3)).copy()
    veins = np.sin(u * math.pi * 14) ** 8                       # parallel veins along the leaf
    streak = _noise((h, w), 120, rng, 3)
    col *= (0.93 + 0.05 * veins[..., None] + 0.10 * (streak[..., None] - 0.5))
    ribm = np.exp(-((u - 0.5) / 0.035) ** 2)[..., None]
    col = col * (1 - 0.55 * ribm) + _hex(rib) * 0.55 * ribm
    edge = np.clip(1 - np.minimum(u, 1 - u) / 0.08, 0, 1)[..., None]
    col *= (1 - 0.12 * edge)
    if dry_tip:
        d = np.clip((v - (1 - dry_tip)) / dry_tip, 0, 1)[..., None] ** 1.5
        col = col * (1 - d) + _hex("#8C7650") * d
    spots = (_noise((h, w), 18, rng, 2) > 0.78)[..., None]
    col = col * (1 - 0.06 * spots)
    return _save(name, np.broadcast_to(col, (h, w, 3)))


def tex_date_trunk(name="TEX_V2_DATE_TRUNK.jpg", seed=3, n=512):
    """one period of the trunk's lattice (u = n_boot * angle / 2pi, v = z / pz): the diamond leaf bases with their
    cut tops, the dark fibre between them"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    rng = np.random.default_rng(seed)
    u = (np.arange(n) + 0.5)[None, :] / n
    v = (np.arange(n) + 0.5)[:, None] / n
    v = 1 - v                                                    # image rows top down, v up
    fa, fb = np.mod(u + v, 1.0), np.mod(u - v, 1.0)
    t = (fa - fb + 1) / 2                                        # bottom -> top of the diamond
    hh = fa + fb - 1                                             # across
    edge = np.minimum.reduce([fa, 1 - fa, fb, 1 - fb])
    fib = _noise((n, n), 40, rng, 4)
    fib2 = np.asarray(__import__("PIL.Image", fromlist=["Image"]).fromarray((rng.random((n, n // 16)) * 255).astype(np.uint8))
                      .resize((n, n), 2)) / 255.0               # vertical fibres
    boot = _hex("#7A634A") * (0.85 + 0.25 * fib[..., None]) * (0.9 + 0.15 * fib2[..., None])
    cut = _hex("#A88E6C") * (0.9 + 0.2 * fib[..., None])
    groove = _hex("#3A2B20") * (0.8 + 0.4 * fib2[..., None])
    a = boot.copy()
    top = np.clip((t - 0.70) / 0.12, 0, 1)[..., None] * (np.abs(hh) < 0.55)[..., None]
    a = a * (1 - top) + cut * top
    g = np.clip(1 - edge / 0.07, 0, 1)[..., None]
    a = a * (1 - g) + groove * g
    a *= (0.75 + 0.25 * np.clip(t, 0, 1)[..., None])            # each base darker at its foot, under the next one
    return _save(name, a)


def tex_wash_trunk(name="TEX_V2_WASH_TRUNK.jpg", seed=5, n=512):
    """the Washingtonia's grey brown trunk: fine horizontal ring scars, vertical cracks (u = 3 * angle / 2pi,
    v = z / 1 m)"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    rng = np.random.default_rng(seed)
    v = np.arange(n)[:, None] / n
    rings = np.zeros((n, 1))
    z = 0.0
    while z < 1.0:
        k = int(z * n)
        rings[k:k + 3] += rng.uniform(0.5, 1.0)
        z += rng.uniform(0.025, 0.05)
    cr = _noise((n, n), 30, rng, 4)
    vert = np.asarray(__import__("PIL.Image", fromlist=["Image"]).fromarray((rng.random((n // 32, n)) * 255).astype(np.uint8))
                      .resize((n, n), 2)) / 255.0
    base = _hex("#6E6152") * (0.85 + 0.25 * cr[..., None])
    a = base * (1 - 0.35 * np.clip(rings, 0, 1)[..., None]) * (0.88 + 0.18 * vert[..., None])
    a = a * (1 - 0.25 * (cr[..., None] > 0.72))
    return _save(name, np.broadcast_to(a, (n, n, 3)))


def tex_boots_red(name="TEX_V2_WASH_BOOTS.jpg"):
    """the criss-cross leaf bases under the Washingtonia's crown: the date trunk's lattice in red brown"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    from PIL import Image
    a = np.asarray(Image.open(tex_date_trunk())).astype(float)
    a = a * np.array([1.12, 0.86, 0.72])
    return _save(name, a)


def tex_flat(name, hexcol, seed, amt=0.12, n=128, stretch=1):
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    rng = np.random.default_rng(seed)
    nz = _noise((n * stretch, n), 20, rng, 3)
    a = _hex(hexcol) * (1 - amt / 2 + amt * nz[..., None])
    return _save(name, a)


def tex_terracotta(name="TEX_V2_TERRACOTTA.jpg", seed=9, n=512):
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    rng = np.random.default_rng(seed)
    big = _noise((n, n), 160, rng, 3)
    fine = _noise((n, n), 8, rng, 2)
    a = _hex("#9C5234") * (0.82 + 0.3 * big[..., None]) * (0.94 + 0.1 * fine[..., None])
    salt = np.clip((big - 0.62) / 0.2, 0, 1)[..., None] * 0.35      # whitish bloom of the fired clay
    a = a * (1 - salt) + _hex("#D8C3A6") * salt
    rings = (np.sin(np.arange(n)[:, None] / n * math.pi * 2 * 40) > 0.96)[..., None]   # the wheel's lines
    a *= (1 - 0.05 * rings)
    return _save(name, a)


def tex_gravel(name="TEX_V2_GRAVEL_MULCH.jpg", seed=11, n=512):
    """the beds' mulch: beige gravel, 1 m tile"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    from PIL import Image, ImageDraw, ImageFilter
    rng = np.random.default_rng(seed)
    im = Image.new("RGB", (n, n), (150, 132, 108))
    d = ImageDraw.Draw(im)
    for _ in range(5200):
        x, y = rng.uniform(0, n, 2)
        r = rng.uniform(2.0, 6.5)
        c = _hex(["#D8C7A8", "#C9B492", "#BBA27E", "#E3D6BE", "#A89274"][rng.integers(5)]) * rng.uniform(0.9, 1.08)
        for dx in (-n, 0, n):
            for dy in (-n, 0, n):
                d.ellipse([x + dx - r, y + dy - r * 0.8, x + dx + r, y + dy + r * 0.8], fill=tuple(int(v) for v in np.clip(c, 0, 255)))
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    return _save(name, np.asarray(im).astype(float))


def tex_plume(name="TEX_V2_GRASS_PLUME.png", seed=13, w=128, h=512):
    """a fountain grass plume with its alpha: a soft foxtail of bristles"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    from PIL import Image, ImageDraw, ImageFilter
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(900):
        t = rng.uniform(0.0, 1.0)
        y = h * (0.04 + 0.92 * t)
        half = w * 0.42 * math.sin(math.pi * (0.15 + 0.85 * (1 - t))) ** 0.8
        x0 = w / 2 + rng.normal(0, 2)
        x1 = x0 + rng.uniform(-1, 1) * half
        y1 = y - rng.uniform(4, 22)
        c = _hex(["#E8D9BC", "#D9C29A", "#C9A98A", "#F0E6D2"][rng.integers(4)])
        d.line([(x0, y), (x1, y1)], fill=(int(c[0]), int(c[1]), int(c[2]), 230), width=1)
    d.line([(w / 2, h * 0.02), (w / 2, h)], fill=(160, 140, 100, 255), width=2)
    im = im.filter(ImageFilter.GaussianBlur(0.4))
    p = os.path.join(TEX, name)
    im.save(p)
    return p


# ---- materials ------------------------------------------------------------------------------------------------
def _img_mat(name, path, rough=0.6, trans=0.0, alpha=False, bump=0.0, sheen=0.0):
    """image -> Principled BSDF (base colour, alpha); leaves let some light through (Translucent mix, Cycles only:
    the GLB export keeps the Principled)"""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path, check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if alpha:
        nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
        m.blend_method = "HASHED" if hasattr(m, "blend_method") else m.blend_method
    if bump:
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        bp.inputs["Distance"].default_value = 0.01
        nt.links.new(t.outputs["Color"], bw.inputs["Color"])
        nt.links.new(bw.outputs["Val"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if sheen and "Sheen Weight" in b.inputs:
        b.inputs["Sheen Weight"].default_value = sheen
    if trans:
        tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
        hsv = nt.nodes.new("ShaderNodeHueSaturation")
        hsv.inputs["Value"].default_value = 1.25
        hsv.inputs["Saturation"].default_value = 1.15
        nt.links.new(t.outputs["Color"], hsv.inputs["Color"])
        nt.links.new(hsv.outputs["Color"], tr.inputs["Color"])
        mix = nt.nodes.new("ShaderNodeMixShader")
        mix.inputs["Fac"].default_value = trans
        nt.links.new(b.outputs["BSDF"], mix.inputs[1])
        nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
        if alpha:
            tp = nt.nodes.new("ShaderNodeBsdfTransparent")
            mx2 = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(t.outputs["Alpha"], mx2.inputs["Fac"])
            nt.links.new(tp.outputs["BSDF"], mx2.inputs[1])
            nt.links.new(mix.outputs["Shader"], mx2.inputs[2])
            nt.links.new(mx2.outputs["Shader"], out.inputs["Surface"])
        else:
            nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    else:
        nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    m["v2_image"] = os.path.basename(path)
    return m


def materials(M):
    """adds the plant library's materials to the scene's material dict M (keys v2_...)"""
    M["v2_date_leaf"] = _img_mat("V2_Date_Palm_Leaflet", tex_leaflet("TEX_V2_DATE_LEAFLET.jpg", "#6F7748", "#566A42", "#4C603D", 21, 0.03, "#8E9466"), 0.55, 0.30)
    M["v2_date_old"] = _img_mat("V2_Date_Palm_Leaflet_Old", tex_leaflet("TEX_V2_DATE_LEAFLET_OLD.jpg", "#8F8650", "#7E7C4A", "#7A6B42", 22, 0.12, "#A69E70"), 0.6, 0.25)
    M["v2_dead"] = _img_mat("V2_Palm_Dead_Frond", tex_leaflet("TEX_V2_PALM_DEAD.jpg", "#8C7452", "#7E6849", "#6B573D", 23, 0.0, "#A08A66"), 0.85, 0.05)
    M["v2_fan"] = _img_mat("V2_Washingtonia_Fan", tex_leaflet("TEX_V2_FAN_SEGMENT.jpg", "#62803A", "#557434", "#506C35", 24, 0.06, "#93A266"), 0.5, 0.30)
    M["v2_fan_old"] = _img_mat("V2_Washingtonia_Fan_Old", tex_leaflet("TEX_V2_FAN_SEGMENT_OLD.jpg", "#9C9A55", "#8E8E4E", "#8A7A47", 25, 0.15, "#C6C08A"), 0.6, 0.25)
    M["v2_rachis"] = _img_mat("V2_Palm_Rachis", tex_flat("TEX_V2_RACHIS.jpg", "#7F7C4C", 26, 0.16, 64, 4), 0.55)
    M["v2_petiole"] = _img_mat("V2_Washingtonia_Petiole", tex_flat("TEX_V2_PETIOLE.jpg", "#7A6A48", 33, 0.18, 64, 4), 0.6)
    M["v2_date_trunk"] = _img_mat("V2_Date_Palm_Trunk", tex_date_trunk(), 0.9, bump=0.4)
    M["v2_wash_trunk"] = _img_mat("V2_Washingtonia_Trunk", tex_wash_trunk(), 0.85, bump=0.3)
    M["v2_wash_boots"] = _img_mat("V2_Washingtonia_Boots", tex_boots_red(), 0.9, bump=0.4)
    M["v2_dates"] = _img_mat("V2_Dates_Fruit", tex_flat("TEX_V2_DATES.jpg", "#B7712C", 27, 0.3), 0.45)
    M["v2_grass"] = _img_mat("V2_Grass_Blade", tex_leaflet("TEX_V2_GRASS_BLADE.jpg", "#6E7C44", "#8A9258", "#AFA372", 28, 0.25, "#A3A57A", 32, 512), 0.6, 0.30)
    M["v2_plume"] = _img_mat("V2_Grass_Plume", tex_plume(), 0.8, 0.35, alpha=True)
    M["v2_agave"] = _img_mat("V2_Agave_Leaf", tex_leaflet("TEX_V2_AGAVE_LEAF.jpg", "#7F978A", "#6B867C", "#5F7A72", 29, 0.02, "#93A89B"), 0.45, 0.10)
    M["v2_spine"] = _img_mat("V2_Agave_Spine", tex_flat("TEX_V2_SPINE.jpg", "#4A3424", 30, 0.2), 0.5)
    M["v2_lav_leaf"] = _img_mat("V2_Lavender_Leaf", tex_flat("TEX_V2_LAVENDER_LEAF.jpg", "#6F7C62", 31, 0.2), 0.7, 0.2)
    M["v2_lav_flower"] = _img_mat("V2_Lavender_Flower", tex_flat("TEX_V2_LAVENDER_FLOWER.jpg", "#6A5698", 32, 0.3), 0.75, 0.2)
    M["v2_olive_leaves"] = _img_mat("V2_Olive_Leaves", tex_olive_leaves(), 0.6, 0.25, alpha=True)
    M["v2_olive_bark"] = _img_mat("V2_Olive_Bark", tex_olive_bark(), 0.95, bump=0.6)
    M["v2_terracotta"] = _img_mat("V2_Terracotta_Jar", tex_terracotta(), 0.8, bump=0.15)
    M["v2_gravel"] = _img_mat("V2_Gravel_Mulch", tex_gravel(), 0.95, bump=0.5)
    # client 28-10: the orange trees and the flower tufts of his D5 garden
    M["v2_citrus_leaves"] = _img_mat("V2_Citrus_Leaves", tex_citrus_leaves(), 0.45, 0.25, alpha=True)
    M["v2_orange"] = _img_mat("V2_Orange_Fruit", tex_flat("TEX_V2_ORANGE.jpg", "#E98A1E", 34, 0.15), 0.4)
    M["v2_flower_leaf"] = _img_mat("V2_Flower_Leaf", tex_flat("TEX_V2_FLOWER_LEAF.jpg", "#4E6A34", 35, 0.2), 0.7, 0.2)
    M["v2_flower_orange"] = _img_mat("V2_Flower_Orange", tex_flat("TEX_V2_FLOWER_ORANGE.jpg", "#EE8A2C", 36, 0.25), 0.7, 0.2)
    M["v2_flower_white"] = _img_mat("V2_Flower_White", tex_flat("TEX_V2_FLOWER_WHITE.jpg", "#F2ECCB", 38, 0.15), 0.7, 0.2)
    return M


# ---- geometry helpers ------------------------------------------------------------------------------------------
Z = np.array([0.0, 0.0, 1.0])


def _n(v):
    return v / (np.linalg.norm(v) + 1e-12)


def _frame(d):
    d = _n(d)
    s = np.cross(Z, d)
    s = _n(s) if np.linalg.norm(s) > 1e-6 else np.array([1.0, 0, 0])
    return d, s, np.cross(d, s)


def _rot(v, axis, ang):
    axis = _n(axis)
    return v * math.cos(ang) + np.cross(axis, v) * math.sin(ang) + axis * np.dot(axis, v) * (1 - math.cos(ang))


def _P(v):
    return (float(v[0]), float(v[1]), float(v[2]))


def _grid(mb, mat, rows, uvs=None, close=False):
    """quads between consecutive rows of points (rows: list of lists, same length); uvs the same shape"""
    for j in range(len(rows) - 1):
        a, b = rows[j], rows[j + 1]
        n = len(a) if close else len(a) - 1
        for i in range(n):
            i2 = (i + 1) % len(a)
            q = [a[i], a[i2], b[i2], b[i]]
            if uvs is not None:
                ua, ub = uvs[j], uvs[j + 1]
                mb.poly(mat, [_P(p) for p in q], [ua[i], ua[i2] if i2 else (ua[-1][0] + (ua[1][0] - ua[0][0]), ua[0][1]),
                                                   ub[i2] if i2 else (ub[-1][0] + (ub[1][0] - ub[0][0]), ub[0][1]), ub[i]])
            else:
                mb.poly(mat, [_P(p) for p in q])


def _tube(mb, mat, pts, radii, seg=6, v_scale=1.0):
    """a tapered tube along a polyline"""
    rows, uvs = [], []
    acc = 0.0
    for k, (p, r) in enumerate(zip(pts, radii)):
        d = pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]
        d, s, u = _frame(d)
        if k:
            acc += np.linalg.norm(pts[k] - pts[k - 1])
        rows.append([p + (s * math.cos(2 * math.pi * i / seg) + u * math.sin(2 * math.pi * i / seg)) * r for i in range(seg)])
        uvs.append([(i / seg, acc * v_scale) for i in range(seg)])
    _grid(mb, mat, rows, uvs, close=True)


def _leaf(mb, mat, base, d, up, length, width, fold=0.35, droop=0.12, prof=(0.45, 1.0, 0.75), curl=0.0):
    """one leaflet: a folded strip from base along d (unit), its face towards up; widths at 0, 0.35, 0.7, a point
    at the tip; it bends down (droop) and sideways (curl)"""
    d = _n(d)
    w_ax = _n(np.cross(up, d))
    nrm = np.cross(d, w_ax)
    st = (0.0, 0.35, 0.7, 1.0)
    rows = []
    for s, wf in zip(st, prof + (0.0,)):
        c = base + d * length * s - Z * droop * length * s * s + w_ax * curl * length * s * s
        hw = width * wf / 2
        rows.append((c - w_ax * hw + nrm * fold * hw, c - nrm * fold * hw * 0.3, c + w_ax * hw + nrm * fold * hw))
    for j in range(3):
        (l0, m0, r0), (l1, m1, r1) = rows[j], rows[j + 1]
        v0, v1 = st[j], st[j + 1]
        if j < 2:
            mb.poly(mat, [_P(l0), _P(m0), _P(m1), _P(l1)], [(0, v0), (0.5, v0), (0.5, v1), (0, v1)])
            mb.poly(mat, [_P(m0), _P(r0), _P(r1), _P(m1)], [(0.5, v0), (1, v0), (1, v1), (0.5, v1)])
        else:
            mb.poly(mat, [_P(l0), _P(m0), _P(m1)], [(0, v0), (0.5, v0), (0.5, v1)])
            mb.poly(mat, [_P(m0), _P(r0), _P(m1)], [(0.5, v0), (1, v0), (0.5, v1)])


def _leaf_lo(mb, mat, base, d, up, length, width, fold=0.35, droop=0.12):
    """the light leaflet (lo=True): two triangles folded along the midrib, widest at 40 %"""
    d = _n(d)
    w_ax = _n(np.cross(up, d))
    nrm = np.cross(d, w_ax)
    mid = base + d * length * 0.4 - Z * droop * length * 0.16
    tip = base + d * length - Z * droop * length
    hw = width / 2
    lft, rgt = mid - w_ax * hw + nrm * fold * hw, mid + w_ax * hw + nrm * fold * hw
    mb.poly(mat, [_P(base), _P(lft), _P(tip)], [(0.5, 0.0), (0.0, 0.4), (0.5, 1.0)])
    mb.poly(mat, [_P(base), _P(tip), _P(rgt)], [(0.5, 0.0), (0.5, 1.0), (1.0, 0.4)])


def finish(ob, angle=55.0):
    """weld the builder's loose faces, smooth shading with sharp edges over angle"""
    import bmesh
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    try:
        me.set_sharp_from_angle(angle=math.radians(angle))
    except AttributeError:
        pass
    me.update()
    return ob


def source(name, mb, M, col):
    """build the mesh builder into one object SRC_<name> (hidden source for the instances)"""
    obs = mb.build("SRC_" + name, col, M)
    if len(obs) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for o in obs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active if len(obs) > 1 else obs[0]
    ob.name = ob.data.name = "SRC_" + name
    return finish(ob)


# ---- date palm ------------------------------------------------------------------------------------------------
def _trunk_lattice(mb, mat, centre, radius, z0, z1, n_boot, pz, amp, seg_per=6, rings_per=7, tex_v0=0.0):
    """a trunk between z0 and z1 whose surface is a lattice of n_boot diamond leaf bases around, pz high: each base
    rises outwards to its cut top and drops under the next (relief on the texture's lattice)"""
    nseg = n_boot * seg_per
    nr = max(2, int((z1 - z0) / pz * rings_per))
    rows, uvs = [], []
    for j in range(nr + 1):
        z = z0 + (z1 - z0) * j / nr
        c = centre(z)
        r0 = radius(z)
        row, uv = [], []
        for i in range(nseg):
            th = 2 * math.pi * i / nseg
            u = n_boot * th / (2 * math.pi)
            v = (z - z0) / pz + tex_v0
            fa, fb = (u + v) % 1.0, (u - v) % 1.0
            t = (fa - fb + 1) / 2
            hh = fa + fb - 1
            edge = min(fa, 1 - fa, fb, 1 - fb)
            ca, cb = math.floor(u + v), math.floor(u - v)
            cell = ((ca * 73856093) ^ (cb * 19349663)) % 1000 / 1000.0          # each base its own size
            bump = (t ** 1.6) * max(0.0, 1 - hh * hh) * min(1.0, edge / 0.08)
            r = r0 * (1 + amp * bump * (0.65 + 0.7 * cell) + 0.012 * math.sin(7 * th + 3 * z) * math.sin(5 * z))
            row.append(c + np.array([math.cos(th), math.sin(th), 0.0]) * r)
            uv.append((u, v))
        rows.append(row)
        uvs.append(uv)
    _grid(mb, mat, rows, uvs, close=True)


def _pinnate_frond(mb, r, base, az, el, droop, length, age, mats, nleaf=62, spread=1.0, lo=False):
    """a date palm frond: rachis from base (azimuth az, elevation el, bending down by droop), spines on its petiole,
    leaflets in two planes along it (lo: a lighter rachis, no spines, wider two-triangle leaflets)"""
    leaf_mat, rachis_mat = mats
    hd = np.array([math.cos(az), math.sin(az), 0.0])
    twist = r.uniform(-0.15, 0.15)
    ns = 14
    pts, dirs = [base], []
    for k in range(ns):
        t = (k + 0.5) / ns
        e = el - droop * t ** 1.25
        d = hd * math.cos(e) + Z * math.sin(e)
        d = _rot(d, Z, twist * t)
        dirs.append(d)
        pts.append(pts[-1] + d * length / ns)
    pts = np.array(pts)
    radii = [0.036 * (1 - 0.9 * (k / ns)) ** 1.2 + 0.004 for k in range(ns + 1)]
    if lo:
        _tube(mb, rachis_mat, list(pts[::2]), radii[::2], seg=3, v_scale=0.5)
    else:
        _tube(mb, rachis_mat, list(pts), radii, seg=4, v_scale=0.5)

    def at(t):
        f = t * ns
        k = min(ns - 1, int(f))
        return pts[k] + (pts[k + 1] - pts[k]) * (f - k), dirs[k]
    # spines on the petiole
    for k in range(0 if lo else 9):
        t = 0.04 + 0.14 * k / 9
        p, d = at(t)
        d, s, u = _frame(d)
        for sg in (-1, 1):
            tip = p + s * sg * r.uniform(0.07, 0.13) + d * 0.06 + u * 0.03
            w = s * sg * 0.0 + d * 0.006
            mb.poly(rachis_mat, [_P(p - w), _P(p + w), _P(tip)], [(0, 0), (1, 0), (0.5, 1)])
    # leaflets: from 18 % of the rachis to its tip, longest at about 45 %, in groups of two or three
    tt, t = [], 0.18
    while t < 0.985:
        tt.append(t)
        t += (0.80 / nleaf) * (0.6 if (len(tt) % 3) else 1.8)
    for idx, t in enumerate(tt):
        p, d = at(t)
        d, s, u = _frame(d)
        prof = math.sin(math.pi * min(1.0, (t - 0.12) / 0.92)) ** 0.65
        ll = length * (0.11 + 0.05 * spread) * (0.25 + 0.75 * prof) * r.uniform(0.88, 1.08)
        fwd = math.radians(48 - 26 * t + r.uniform(-6, 6))     # leaflets point towards the tip
        for sg in (-1, 1):
            plane = (idx + (sg > 0)) % 3                        # three planes: the palm's V and its fuzz
            elev = math.radians((52, 22, 4)[plane] * spread + r.uniform(-8, 8) - 18 * age)
            ld = d * math.cos(fwd) + s * sg * math.sin(fwd)
            ld = _n(ld * math.cos(elev) + u * math.sin(elev))
            b = p + s * sg * 0.02
            if lo:
                _leaf_lo(mb, leaf_mat, b, ld, u + Z * 0.3, ll, ll * r.uniform(0.13, 0.16), fold=0.6, droop=0.12 + 0.25 * age)
                continue
            _leaf(mb, leaf_mat, b, ld, u + Z * 0.3, ll, ll * r.uniform(0.060, 0.075), fold=0.6, droop=0.12 + 0.25 * age,
                  curl=r.uniform(-0.05, 0.05))


def date_palm(seed, height, n_fronds=48, dates=True, M=None, lo=False, cards=False):
    """Phoenix dactylifera, trunk `height` m to the crown (local coords, foot at the origin); lo: the light version
    (build_lod)"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    lean = np.array([r.uniform(-1, 1), r.uniform(-1, 1), 0.0])
    lean = _n(lean) * r.uniform(0.02, 0.07)
    bow = r.uniform(-0.04, 0.04)

    def centre(z):
        t = z / height
        return lean * z + np.array([bow, -bow, 0]) * math.sin(math.pi * t) * height * 0.3 + Z * z

    def radius(z):
        t = z / height
        flare = 0.30 * math.exp(-z / 0.35)                      # the root plate
        return 0.27 * (1.0 - 0.10 * t) + flare + 0.05 * max(0.0, (t - 0.9) / 0.1) ** 2
    if lo:
        _trunk_lattice(mb, "v2_date_trunk", centre, radius, 0.0, height, n_boot=10, pz=0.15, amp=0.0, seg_per=1, rings_per=0.5)
    else:
        _trunk_lattice(mb, "v2_date_trunk", centre, radius, 0.0, height, n_boot=10, pz=0.15, amp=0.11)
    top = centre(height)
    # the crown bulb: rings of leaf bases closing over the top
    rows, uvs = [], []
    nj, na = (4, 10) if lo else (7, 28)
    for j in range(nj):
        t = j / (nj - 1)
        rr = (0.33 + 0.12 * math.sin(math.pi * t * 0.9)) * (1 - t ** 3)
        zz = height + 0.75 * t
        rows.append([top + np.array([math.cos(a) * rr, math.sin(a) * rr, zz - height]) for a in np.linspace(0, 2 * math.pi, na, endpoint=False)])
        uvs.append([(9 * k / na, 6 + t * 4) for k in range(na)])
    _grid(mb, "v2_date_trunk", rows, uvs, close=True)
    # fronds: golden angle, young ones upright in the centre, old ones low and drooping
    for i in range(n_fronds):
        age = i / (n_fronds - 1)
        az = i * GOLD + r.uniform(-0.12, 0.12)
        el = math.radians(80 - 100 * age ** 0.8 + r.uniform(-7, 7))
        droop = math.radians(22 + 75 * math.sin(math.pi * min(1.0, 0.15 + age * 0.85)) ** 0.7 * (0.6 + 0.4 * age) + r.uniform(-8, 8))
        Lf = (2.4 + 1.6 * math.sin(math.pi * min(1.0, 0.25 + age))) * r.uniform(0.9, 1.06)
        rb = 0.18 + 0.12 * age
        base = top + np.array([math.cos(az) * rb, math.sin(az) * rb, 0.72 - 0.75 * age])
        mats = ("v2_date_old" if age > 0.86 and r.random() < 0.6 else "v2_date_leaf", "v2_rachis")
        if cards:
            _frond_card(mb, r, base, az, el, droop, Lf, age, "v2_date_card_old" if mats[0] == "v2_date_old" else "v2_date_card",
                        spread=1.0 if age > 0.08 else 0.45)
            continue
        _pinnate_frond(mb, r, base, az, el, droop, Lf, age, mats, nleaf=22 if lo else 82, spread=1.0 if age > 0.08 else 0.45, lo=lo)
    for k in range(r.randint(2, 3)):                            # dead fronds hanging under the crown
        az = r.uniform(0, 2 * math.pi)
        base = top + np.array([math.cos(az) * 0.3, math.sin(az) * 0.3, 0.05])
        if cards:
            _frond_card(mb, r, base, az, math.radians(-62), math.radians(25), r.uniform(2.6, 3.2), 1.0, "v2_dead_card", spread=0.5)
            continue
        _pinnate_frond(mb, r, base, az, math.radians(-62), math.radians(25), r.uniform(2.6, 3.2), 1.0, ("v2_dead", "v2_dead"),
                       nleaf=10 if lo else 40, spread=0.5, lo=lo)
    if dates and not lo:                                                   # date bunches under the crown, orange
        for k in range(r.randint(3, 5)):
            az = r.uniform(0, 2 * math.pi)
            p0 = top + np.array([math.cos(az) * 0.35, math.sin(az) * 0.35, 0.25])
            d = np.array([math.cos(az) * 0.6, math.sin(az) * 0.6, -0.8])
            p1 = p0 + d * 0.9
            _tube(mb, "v2_rachis", [p0, p0 + d * 0.45, p1], [0.025, 0.02, 0.015], seg=5)
            for s_ in range(70):
                q = p1 + np.array([r.gauss(0, 0.14), r.gauss(0, 0.14), -abs(r.gauss(0, 0.25))])
                _tube(mb, "v2_rachis", [p1, q], [0.004, 0.004], seg=3)
                rr = 0.018
                ring = [q + np.array([math.cos(a) * rr, math.sin(a) * rr, 0]) for a in np.linspace(0, 2 * math.pi, 5, endpoint=False)]
                lo, hi = q - Z * 0.032, q + Z * 0.012
                for a in range(5):
                    mb.poly("v2_dates", [_P(lo), _P(ring[(a + 1) % 5]), _P(ring[a])], [(0, 0), (1, 0.5), (0, 0.5)])
                    mb.poly("v2_dates", [_P(ring[a]), _P(ring[(a + 1) % 5]), _P(hi)], [(0, 0.5), (1, 0.5), (0.5, 1)])
    return mb


# ---- Washingtonia robusta -------------------------------------------------------------------------------------
def _fan(mb, r, hast, f, R, mat, nseg=48, open_deg=115, droop=1.0, fold=0.35, dead=False, lo=False):
    """a costapalmate fan at the hastula hast, facing along f (unit): pleated segments, joined to 55 % of the radius,
    free beyond and drooping to their tips"""
    f, s, n = _frame(f)
    if dead:
        n = -n
    st = (0.03, 0.55, 0.8, 1.0) if lo else (0.03, 0.18, 0.36, 0.55, 0.70, 0.85, 1.0)
    dphi = math.radians(2 * open_deg) / nseg
    for k in range(nseg):
        phi_c = -math.radians(open_deg) + dphi * (k + 0.5)
        tipr = r.uniform(0.92, 1.08)
        sd = r.uniform(0.7, 1.3) * droop
        rows, uvs = [], []
        for rho in st:
            free = max(0.0, (rho - 0.55) / 0.45)
            wf = 1.0 if rho <= 0.55 else (1 - free) ** 0.8
            rr = R * rho * (tipr if rho > 0.55 else 1.0)
            row = []
            for j, side in enumerate((-0.5, 0.0, 0.5)):
                phi = phi_c + side * dphi * wf
                rd = f * math.cos(phi) + s * math.sin(phi)
                p = hast + rd * rr + n * (fold * R * abs(math.sin(phi)) * rho * 0.6)
                p = p - Z * (R * 0.22 * rho * rho + R * 0.75 * sd * free * free * (0.6 + 0.4 * abs(math.sin(phi))))
                if j == 1:                                     # the pleat's ridge
                    p = p + n * 0.035 * R * min(1.0, rho * 2.2) * (1 - 0.6 * free)
                row.append(p)
            rows.append(row)
            uvs.append([(0.0, rho), (0.5, rho), (1.0, rho)])
        for j in range(len(st) - 1):
            a, b = rows[j], rows[j + 1]
            ua, ub = uvs[j], uvs[j + 1]
            for i in range(2):
                mb.poly(mat, [_P(a[i]), _P(a[i + 1]), _P(b[i + 1]), _P(b[i])], [ua[i], ua[i + 1], ub[i + 1], ub[i]])


def washingtonia(seed, height, skirt=True, n_fronds=28, lo=False, cards=False):
    """Washingtonia robusta, trunk `height` m to the crown (local coords, foot at the origin); lo: the light version
    (build_lod)"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    lean = _n(np.array([r.uniform(-1, 1), r.uniform(-1, 1), 0.0])) * r.uniform(0.01, 0.04)
    bow = r.uniform(-0.05, 0.05)

    def centre(z):
        t = z / height
        return lean * z + np.array([bow, bow * 0.5, 0]) * math.sin(math.pi * t) * height * 0.15 + Z * z

    def radius(z):
        return 0.20 + 0.03 * (1 - z / height) + 0.26 * math.exp(-z / 0.55)
    zb = height - 1.4                                           # the criss-cross leaf bases under the crown
    nseg, nr = (8, max(2, int(zb / 1.2))) if lo else (18, int(zb / 0.25))
    rows, uvs = [], []
    for j in range(nr + 1):
        z = zb * j / nr
        c, rr = centre(z), radius(z)
        rows.append([c + np.array([math.cos(a) * rr, math.sin(a) * rr, 0]) for a in np.linspace(0, 2 * math.pi, nseg, endpoint=False)])
        uvs.append([(3 * k / nseg, z) for k in range(nseg)])
    _grid(mb, "v2_wash_trunk", rows, uvs, close=True)
    _trunk_lattice(mb, "v2_wash_boots", centre, lambda z: radius(z) * (1 + 0.15 * (z - zb) / 1.4), zb, height, n_boot=8, pz=0.16,
                   amp=0.0 if lo else 0.22, seg_per=1 if lo else 6, rings_per=0.5 if lo else 7)
    top = centre(height)
    rows, uvs = [], []
    nj, na = (3, 10) if lo else (5, 24)
    for j in range(nj):
        t = j / (nj - 1)
        rr = (radius(height) * 1.15 + 0.06 * math.sin(math.pi * t)) * (1 - t ** 3)
        rows.append([top + np.array([math.cos(a) * rr, math.sin(a) * rr, 0.55 * t]) for a in np.linspace(0, 2 * math.pi, na, endpoint=False)])
        uvs.append([(8 * k / na, 9 + t * 3) for k in range(na)])
    _grid(mb, "v2_wash_boots", rows, uvs, close=True)
    for i in range(n_fronds):
        age = i / (n_fronds - 1)
        az = i * GOLD + r.uniform(-0.1, 0.1)
        el = math.radians(62 - 80 * age ** 0.9 + r.uniform(-6, 6))
        hd = np.array([math.cos(az), math.sin(az), 0.0])
        base = top + hd * (0.12 + 0.08 * age) + Z * (0.5 - 0.45 * age)
        Lp = r.uniform(1.0, 1.35) * (0.8 + 0.3 * (1 - abs(age - 0.4)))
        pd = hd * math.cos(el) + Z * math.sin(el)
        pts = [base]
        for k in range(6):
            e = el - math.radians(10) * (k / 5)
            pts.append(pts[-1] + (hd * math.cos(e) + Z * math.sin(e)) * Lp / 6)
        pr = [0.035, 0.032, 0.028, 0.025, 0.022, 0.02, 0.02]
        _tube(mb, "v2_petiole", pts[::3] if lo else pts, pr[::3] if lo else pr, seg=3 if lo else 4, v_scale=0.5)
        for k in range(1, 1 if lo else 6):                      # the petiole's teeth
            p = pts[k]
            d, s, u = _frame(pts[k] - pts[k - 1])
            for sg in (-1, 1):
                mb.poly("v2_petiole", [_P(p + s * sg * 0.02 - d * 0.01), _P(p + s * sg * 0.02 + d * 0.01), _P(p + s * sg * 0.05 + d * 0.03)],
                        [(0, 0), (1, 0), (0.5, 1)])
        fdir = _n(pts[-1] - pts[-2]) + Z * 0.25
        mat = "v2_fan_old" if age > 0.85 and r.random() < 0.6 else "v2_fan"
        if cards:
            _fan_card(mb, r, pts[-1], fdir, r.uniform(0.85, 1.05), mat.replace("fan", "fan_card"), droop=0.6 + 0.6 * age)
            continue
        _fan(mb, r, pts[-1], fdir, r.uniform(0.85, 1.05), mat, nseg=15 if lo else 46, droop=0.6 + 0.6 * age, lo=lo)
    for k in range(2):                                          # the spear leaves, still folded
        p0 = top + Z * 0.5
        d = _n(Z + np.array([r.uniform(-0.2, 0.2), r.uniform(-0.2, 0.2), 0]))
        _tube(mb, "v2_fan", [p0, p0 + d * 0.8, p0 + d * 1.5], [0.05, 0.035, 0.005], seg=3 if lo else 6)
    if skirt:                                                   # the skirt of dead fronds hanging against the trunk
        for layer in range(2 if lo else 3):
            nn = (8 if lo else 16) + 3 * layer
            for i in range(nn):
                az = 2 * math.pi * (i + 0.5 * layer) / nn + r.uniform(-0.1, 0.1)
                hd = np.array([math.cos(az), math.sin(az), 0.0])
                z0 = height - 0.1 - 0.45 * layer
                base = centre(z0) + hd * (radius(z0) + 0.05)
                tip = base + hd * 0.25 - Z * 0.55
                _tube(mb, "v2_dead", [base, tip], [0.025, 0.02], seg=3)
                fd = _n(hd * 0.25 - Z)
                if cards:
                    _fan_card(mb, r, tip, fd, r.uniform(0.75, 0.95), "v2_dead_fan_card", open_deg=40, droop=0.15, fold=0.15,
                              dead=True, ncol=2)
                    continue
                _fan(mb, r, tip, fd, r.uniform(0.75, 0.95), "v2_dead", nseg=3 if lo else 22, open_deg=40, droop=0.15, fold=0.15,
                     dead=True, lo=lo)
    return mb


# ---- small plants ----------------------------------------------------------------------------------------------
def grass(seed, h=0.75, n=230, plumes=24, lo=False):
    """fountain grass: arching blades out of a tight base, feathery plumes over them (lo: wider blades on four rows,
    two cards a plume)"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    for i in range(n):
        az = r.uniform(0, 2 * math.pi)
        hd = np.array([math.cos(az), math.sin(az), 0.0])
        b = hd * r.uniform(0, 0.07)
        hh = h * r.uniform(0.55, 1.0)
        out = r.uniform(0.15, 0.75)
        w = r.uniform(0.008, 0.013) * (2.5 if lo else 1.0)
        s = np.cross(Z, hd)
        rows, uvs = [], []
        nk = 4 if lo else 7
        for k in range(nk):
            t = k / (nk - 1)
            p = b + Z * hh * math.sin(t * math.pi * 0.62) / math.sin(math.pi * 0.62) + hd * out * hh * t ** 1.6
            p = p - Z * out * hh * 0.5 * max(0, t - 0.6) ** 2
            ww = w * (1 - t) ** 0.7 + 0.0005
            rows.append([p - s * ww, p + s * ww])
            uvs.append([(0, t), (1, t)])
        _grid(mb, "v2_grass", rows, uvs)
    for i in range(plumes):
        az = r.uniform(0, 2 * math.pi)
        hd = np.array([math.cos(az), math.sin(az), 0.0])
        hh = h * r.uniform(1.05, 1.35)
        out = r.uniform(0.1, 0.4)
        p0 = hd * r.uniform(0, 0.05)
        p1 = p0 + Z * hh * 0.7 + hd * out * hh * 0.3
        p2 = p0 + Z * hh + hd * out * hh * 0.75
        _tube(mb, "v2_grass", [p0, p2] if lo else [p0, p1, p2], [0.003, 0.002] if lo else [0.003, 0.0025, 0.002], seg=3)
        d = _n(p2 - p1)
        pl = 0.20 * r.uniform(0.8, 1.2)
        nc = 2 if lo else 3
        for k in range(nc):                                    # crossed cards with the plume's texture
            a = math.pi * k / nc + az
            sv = np.array([math.cos(a), math.sin(a), 0.0])
            sv = _n(sv - d * np.dot(sv, d)) * 0.035
            q0, q1 = p2 - d * 0.02, p2 + d * pl
            mb.poly("v2_plume", [_P(q0 - sv), _P(q0 + sv), _P(q1 + sv), _P(q1 - sv)], [(0, 0), (1, 0), (1, 1), (0, 1)])
    return mb


def agave(seed, n=30, length=0.75, lo=False):
    """Agave americana: thick keeled leaves, channelled on top, with their dark terminal spines (lo: four rows a leaf,
    wider, no spines)"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    for i in range(n):
        f = i / (n - 1)                                         # 0 = outer, 1 = inner
        az = i * GOLD + r.uniform(-0.1, 0.1)
        hd = np.array([math.cos(az), math.sin(az), 0.0])
        s = np.cross(Z, hd)
        tilt = math.radians(14 + 66 * f ** 0.8 + r.uniform(-5, 5))
        Lf = length * (1.0 - 0.45 * f) * r.uniform(0.85, 1.1)
        w = 0.10 * (1 - 0.3 * f) * r.uniform(0.9, 1.1) * (1.25 if lo else 1.0)
        th = w * 0.6
        prof = [(0.0, 0.75), (0.3, 0.95), (0.7, 0.55), (1.0, 0.0)] if lo else [(0.0, 0.75), (0.15, 1.0), (0.45, 0.85), (0.75, 0.5), (0.93, 0.15), (1.0, 0.0)]
        rows, uvs = [], []
        for t, hw in prof:
            e = tilt - math.radians(30) * t * t * (1 - f)        # the outer leaves arch over
            c = hd * Lf * t * math.cos(e) + Z * (0.04 + Lf * t * math.sin(e))
            up = _n(-hd * math.sin(e) + Z * math.cos(e))
            ew, et = w * hw, th * hw
            rows.append([c - s * ew + up * et * 0.25, c - up * et * 0.15, c + s * ew + up * et * 0.25,   # top, channelled
                         c - up * et])                                                             # keel below
            uvs.append([(0, t), (0.5, t), (1, t), (0.5, t)])
        _grid(mb, "v2_agave", rows, uvs, close=True)
        if lo:
            continue
        tip_c = hd * Lf * math.cos(tilt - math.radians(30) * (1 - f)) + Z * (0.04 + Lf * math.sin(tilt - math.radians(30) * (1 - f)))
        d = _n(tip_c - rows[-2][1])
        _tube(mb, "v2_spine", [tip_c - d * 0.01, tip_c + d * 0.035], [0.006, 0.0005], seg=4)
    return mb


def lavender(seed, r0=0.38, h=0.36, needles=520, spikes=80, lo=False):
    """a lavender mound: grey needle leaves, purple spikes on long stems (lo: wider two-triangle needles)"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    for i in range(needles):
        u = np.array([r.gauss(0, 1), r.gauss(0, 1), abs(r.gauss(0, 1)) + 0.2])
        u = _n(u)
        k = r.uniform(0.35, 1.0) ** 0.5
        p = np.array([u[0] * r0 * k, u[1] * r0 * k, u[2] * h * k])
        d = _n(np.array([u[0], u[1], u[2] + 0.8]) + np.array([r.gauss(0, 0.3), r.gauss(0, 0.3), 0]))
        if lo:
            _leaf_lo(mb, "v2_lav_leaf", p - d * 0.06, d, _n(np.cross(d, np.cross(Z, d)) + 1e-3), 0.15, 0.04, fold=0.2, droop=0.0)
        else:
            _leaf(mb, "v2_lav_leaf", p - d * 0.05, d, _n(np.cross(d, np.cross(Z, d)) + 1e-3), 0.11, 0.014, fold=0.2, droop=0.0)
    for i in range(spikes):
        az = r.uniform(0, 2 * math.pi)
        rr = r0 * r.uniform(0, 0.8)
        hd = np.array([math.cos(az), math.sin(az), 0.0])
        p0 = hd * rr * 0.5 + Z * h * 0.4
        p1 = hd * (rr * 0.8 + 0.05) + Z * (h + r.uniform(0.15, 0.28))
        _tube(mb, "v2_lav_leaf", [p0, p1], [0.002, 0.0015], seg=3)
        d = _n(p1 - p0)
        q1 = p1 + d * r.uniform(0.06, 0.09)
        _tube(mb, "v2_lav_flower", [p1, p1 + d * 0.03, q1], [0.009, 0.011, 0.002], seg=3 if lo else 5)
    return mb


def jar(seed, kind="khabia", height=0.9, lo=False):
    """a turned terracotta jar: kind 'khabia' (round belly) or 'amphora' (tall, narrow foot)"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    if kind == "amphora":
        prof = [(0.0, 0.09), (0.04, 0.11), (0.25, 0.22), (0.50, 0.29), (0.70, 0.27), (0.85, 0.17), (0.90, 0.12),
                (0.95, 0.12), (0.97, 0.15), (1.0, 0.15), (1.0, 0.12), (0.93, 0.10)]
    else:
        prof = [(0.0, 0.16), (0.03, 0.19), (0.18, 0.31), (0.42, 0.38), (0.65, 0.35), (0.82, 0.24), (0.90, 0.17),
                (0.94, 0.17), (0.97, 0.20), (1.0, 0.20), (1.0, 0.17), (0.94, 0.15)]
    seg = 12 if lo else 28
    rows, uvs = [], []
    for k, (t, rad) in enumerate(prof):
        rr = rad * height * r.uniform(0.98, 1.02)
        rows.append([np.array([math.cos(a) * rr, math.sin(a) * rr, t * height]) for a in np.linspace(0, 2 * math.pi, seg, endpoint=False)])
        uvs.append([(2 * i / seg, t * 1.5) for i in range(seg)])
    _grid(mb, "v2_terracotta", rows, uvs, close=True)
    rows0 = rows[0]
    for i in range(seg):                                        # the foot
        mb.poly("v2_terracotta", [_P(rows0[(i + 1) % seg]), _P(rows0[i]), (0.0, 0.0, 0.0)], [(0, 0), (1, 0), (0.5, 0.5)])
    return mb


def tex_olive_leaves(name="TEX_V2_OLIVE_LEAVES.png", seed=17, n=512):
    """a spray of olive leaves on its twig, with alpha: narrow lanceolate leaves, dark grey green above, silver
    below"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    from PIL import Image, ImageDraw, ImageFilter
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    twigs = [((n * 0.5, n * 0.98), (n * 0.5 + rng.normal(0, 30), n * 0.05))]
    for _ in range(3):
        y0 = rng.uniform(0.3, 0.8) * n
        twigs.append(((n * 0.5, y0), (n * 0.5 + rng.choice([-1, 1]) * rng.uniform(120, 220), y0 - rng.uniform(80, 200))))
    for (x0, y0), (x1, y1) in twigs:
        d.line([(x0, y0), (x1, y1)], fill=(96, 84, 66, 255), width=4)
        L_ = math.hypot(x1 - x0, y1 - y0)
        k = 0
        while k * 14 < L_:
            t = k * 14 / L_
            px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            ang = math.atan2(y1 - y0, x1 - x0)
            for sg in (-1, 1):
                a = ang + sg * rng.uniform(0.5, 0.9)
                ll, ww = rng.uniform(46, 70) * (1 - 0.3 * t), rng.uniform(7, 10)
                tip = (px + math.cos(a) * ll, py + math.sin(a) * ll)
                nx, ny = -math.sin(a) * ww / 2, math.cos(a) * ww / 2
                mx, my = px + math.cos(a) * ll * 0.45, py + math.sin(a) * ll * 0.45
                silver = rng.random() < 0.35
                c = _hex("#A3A88E" if silver else ["#4F5A3A", "#59643F", "#475236"][rng.integers(3)]) * rng.uniform(0.9, 1.1)
                d.polygon([(px, py), (mx + nx, my + ny), tip, (mx - nx, my - ny)], fill=(int(c[0]), int(c[1]), int(c[2]), 255))
            k += 1
    im = im.filter(ImageFilter.GaussianBlur(0.5))
    im.save(p)
    return p


def tex_olive_bark(name="TEX_V2_OLIVE_BARK.jpg", seed=19, n=512):
    """the olive's grey bark: deep twisted fissures, lichen grey and brown"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n] / n
    warp = _noise((n, n), 90, rng, 3)
    fiss = np.abs(np.sin((x * 9 + warp * 2.2 + y * 0.8) * math.pi))      # fissures, twisted
    fiss = np.clip((fiss - 0.15) / 0.5, 0, 1)
    tone = _noise((n, n), 60, rng, 4)
    a = _hex("#8A8478") * (0.8 + 0.35 * tone[..., None])
    a = a * (0.45 + 0.55 * fiss[..., None])
    lich = np.clip((_noise((n, n), 25, rng, 3) - 0.62) / 0.15, 0, 1)[..., None] * 0.4
    a = a * (1 - lich) + _hex("#B8B7A6") * lich
    return _save(name, a)


def olive(seed, height=4.0, spread=4.2, lo=False):
    """an old olive tree: a short gnarled trunk splitting in three twisted leaders, branches and twigs spreading into
    a broad irregular dome, sprays of leaves at their ends (alpha cards with the leaf texture)"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    tips = []
    crown_c = Z * height * 0.62

    def branch(pts0, rad0, d, length, depth):
        pts, radii = [pts0], [rad0]
        n = (3 if depth < 2 else 2) if lo else (6 if depth < 2 else 4)
        for k in range(n):
            out = _n(np.array([pts[-1][0], pts[-1][1], 0.0]) + 1e-3)
            d = _n(d + np.array([r.gauss(0, 0.22), r.gauss(0, 0.22), r.gauss(0.0, 0.1)]) + out * 0.10)
            if pts[-1][2] > height * 0.85:
                d = _n(d - Z * 0.4)
            pts.append(pts[-1] + d * length / n)
            radii.append(rad0 * (1 - 0.6 * (k + 1) / n))
        _tube(mb, "v2_olive_bark", pts, radii, seg=((4, 3, 3, 3) if lo else (8, 6, 5, 4))[min(depth, 3)], v_scale=1.0)
        if depth >= 3:
            tips.extend([pts[-1], pts[-2]])
            return
        nb = r.randint(2, 3)
        for k in range(nb):
            i = r.randint(n // 2, n)
            dd = _n(d + np.array([r.gauss(0, 0.7), r.gauss(0, 0.7), r.uniform(-0.1, 0.5)]))
            branch(pts[i], radii[i] * 0.8, dd, length * r.uniform(0.55, 0.72), depth + 1)
        if depth >= 2:
            tips.append(pts[-1])
    th = height * 0.28
    pts = [np.zeros(3) - Z * 0.15]
    for k in range(4):                                           # the gnarled trunk, twisting
        pts.append(pts[-1] + np.array([r.gauss(0, 0.06), r.gauss(0, 0.06), th / 4]))
    _tube(mb, "v2_olive_bark", pts, [0.30, 0.24, 0.21, 0.20, 0.19], seg=6 if lo else 10)
    for k in range(3):                                           # its burls
        p = pts[1 + k] + _n(np.array([r.gauss(0, 1), r.gauss(0, 1), 0])) * 0.16
        _tube(mb, "v2_olive_bark", [p - Z * 0.12, p, p + Z * 0.14], [0.05, 0.10, 0.04], seg=4 if lo else 6)
    n_lead = 3
    for k in range(n_lead):
        a = 2 * math.pi * k / n_lead + r.uniform(-0.3, 0.3)
        hd = np.array([math.cos(a), math.sin(a), 0.0])
        branch(pts[-1] + hd * 0.08, 0.14, _n(hd * 0.75 + Z), height * 0.42, 0)
    for p in tips:                                               # leaf sprays, turned out of the crown
        for k in range(4 if lo else 7):
            c = p + np.array([r.gauss(0, 0.22), r.gauss(0, 0.22), r.gauss(0.05, 0.15)])
            out = _n(c - crown_c)
            nrm = _n(out * 0.6 + np.array([r.gauss(0, 0.6), r.gauss(0, 0.6), r.gauss(0.3, 0.5)]))
            a1 = _n(np.cross(nrm, Z) + 1e-3)
            a2 = np.cross(nrm, a1)
            s_ = r.uniform(0.24, 0.36) * (1.3 if lo else 1.0)
            q = [c - a1 * s_ - a2 * s_, c + a1 * s_ - a2 * s_, c + a1 * s_ + a2 * s_, c - a1 * s_ + a2 * s_]
            mb.poly("v2_olive_leaves", [_P(v) for v in q], [(0, 0), (1, 0), (1, 1), (0, 1)])
    return mb




# ---- the gardens as the client's D5 duplex (28-10): orange trees, tufts of flowers ---------------------------------
def tex_citrus_leaves(name="TEX_V2_CITRUS_LEAVES.png", seed=37, n=512):
    """a spray of citrus leaves on its twig, with alpha: broad glossy oval leaves, deep green, a lighter midrib"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    from PIL import Image, ImageDraw, ImageFilter
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    twigs = [((n * 0.5, n * 0.98), (n * 0.5 + rng.normal(0, 30), n * 0.06))]
    for _ in range(3):
        y0 = rng.uniform(0.3, 0.8) * n
        twigs.append(((n * 0.5, y0), (n * 0.5 + rng.choice([-1, 1]) * rng.uniform(110, 200), y0 - rng.uniform(70, 180))))
    for (x0, y0), (x1, y1) in twigs:
        d.line([(x0, y0), (x1, y1)], fill=(88, 80, 58, 255), width=4)
        L_ = math.hypot(x1 - x0, y1 - y0)
        k = 0
        while k * 24 < L_:
            t = k * 24 / L_
            px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            ang = math.atan2(y1 - y0, x1 - x0)
            for sg in (-1, 1):
                a = ang + sg * rng.uniform(0.6, 1.0)
                ll, ww = rng.uniform(44, 62) * (1 - 0.25 * t), rng.uniform(18, 25)
                pts = []
                for j in range(13):                             # an oval leaf
                    u = j / 12
                    w_ = math.sin(math.pi * u) ** 0.8 * ww / 2
                    pts.append((u, w_))
                c = _hex(["#2E5A22", "#376628", "#3F702D", "#2A5220"][rng.integers(4)]) * rng.uniform(0.9, 1.1)
                outline = [(px + math.cos(a) * ll * u - math.sin(a) * w_, py + math.sin(a) * ll * u + math.cos(a) * w_) for u, w_ in pts] + \
                          [(px + math.cos(a) * ll * u + math.sin(a) * w_, py + math.sin(a) * ll * u - math.cos(a) * w_) for u, w_ in pts[::-1]]
                d.polygon(outline, fill=(int(c[0]), int(c[1]), int(c[2]), 255))
                d.line([(px, py), (px + math.cos(a) * ll * 0.9, py + math.sin(a) * ll * 0.9)], fill=(int(c[0] * 1.35), int(c[1] * 1.3), int(c[2] * 1.2), 255), width=1)
            k += 1
    im = im.filter(ImageFilter.GaussianBlur(0.5))
    im.save(p)
    return p


def _ball(mb, mat, c, rad, lo=False):
    """a small round fruit or flower head (UV sphere, a few faces)"""
    nl, nv = (2, 4) if lo else (3, 6)
    rows = []
    for j in range(1, nl + 1):
        ph = math.pi * j / (nl + 1)
        rows.append([c + np.array([math.cos(2 * math.pi * i / nv) * math.sin(ph), math.sin(2 * math.pi * i / nv) * math.sin(ph), math.cos(ph)]) * rad
                     for i in range(nv)])
    _grid(mb, mat, rows, [[(i / nv, j / nl) for i in range(nv)] for j in range(nl)], close=True)
    top, bot = c + Z * rad, c - Z * rad
    for i in range(nv):
        i2 = (i + 1) % nv
        mb.poly(mat, [_P(top), _P(rows[0][i]), _P(rows[0][i2])], [(0.5, 1), (0, 0.8), (1, 0.8)])
        mb.poly(mat, [_P(bot), _P(rows[-1][i2]), _P(rows[-1][i])], [(0.5, 0), (1, 0.2), (0, 0.2)])


def citrus(seed, height=2.6, spread=2.3, lo=False):
    """an orange tree as in the client's D5 garden: a short trunk, three or four limbs, a dense rounded crown of leaf
    sprays (alpha cards), oranges on its outside"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    ht = height * 0.30
    top = np.array([r.gauss(0, 0.04), r.gauss(0, 0.04), ht])
    _tube(mb, "v2_olive_bark", [-Z * 0.1, top * 0.5 + np.array([r.gauss(0, 0.03), r.gauss(0, 0.03), 0]), top], [0.09, 0.075, 0.065],
          seg=5 if lo else 7)
    cc = Z * (ht + (height - ht) * 0.52)
    R, Rz = spread / 2, (height - ht) / 2
    for k in range(3 if lo else 4):                              # limbs into the crown
        a = 2 * math.pi * k / (3 if lo else 4) + r.uniform(-0.3, 0.3)
        tip = cc + np.array([math.cos(a) * R * 0.55, math.sin(a) * R * 0.55, r.uniform(-0.1, 0.3) * Rz])
        mid = (top + tip) / 2 + np.array([r.gauss(0, 0.06), r.gauss(0, 0.06), 0.05])
        _tube(mb, "v2_olive_bark", [top, mid, tip], [0.05, 0.035, 0.02], seg=4 if lo else 5)
    n_cards = 70 if lo else 150
    for i in range(n_cards):                                     # leaf sprays on a rounded shell, turned outwards
        zz = 1 - 2 * (i + 0.5) / n_cards
        rad = math.sqrt(max(0.0, 1 - zz * zz))
        th = i * GOLD
        dv = np.array([math.cos(th) * rad, math.sin(th) * rad, zz])
        c = cc + dv * np.array([R, R, Rz]) * r.uniform(0.62, 1.0)
        nrm = _n(dv + np.array([r.gauss(0, 0.4), r.gauss(0, 0.4), r.gauss(0.2, 0.4)]))
        a1 = _n(np.cross(nrm, Z) + 1e-3)
        a2 = np.cross(nrm, a1)
        s_ = r.uniform(0.28, 0.38) * (1.35 if lo else 1.0)
        q = [c - a1 * s_ - a2 * s_, c + a1 * s_ - a2 * s_, c + a1 * s_ + a2 * s_, c - a1 * s_ + a2 * s_]
        mb.poly("v2_citrus_leaves", [_P(v) for v in q], [(0, 0), (1, 0), (1, 1), (0, 1)])
    for i in range(14 if lo else 34):                            # the oranges, on the outside of the crown
        zz = r.uniform(-0.45, 0.75)
        th = r.uniform(0, 2 * math.pi)
        rad = math.sqrt(1 - zz * zz)
        dv = np.array([math.cos(th) * rad, math.sin(th) * rad, zz])
        _ball(mb, "v2_orange", cc + dv * np.array([R, R, Rz]) * r.uniform(0.95, 1.04), 0.045, lo)
    return mb


def flowers(seed, mat="v2_flower_orange", r0=0.30, h=0.30, leaves=160, heads=40, lo=False):
    """a tuft of flowering perennials as in the client's D5 garden (orange lantana, white daisies): a low mound of
    small leaves, flower heads dotted over it"""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    for i in range(leaves):
        u = _n(np.array([r.gauss(0, 1), r.gauss(0, 1), abs(r.gauss(0, 1)) + 0.25]))
        k = r.uniform(0.3, 1.0) ** 0.5
        p = np.array([u[0] * r0 * k, u[1] * r0 * k, u[2] * h * k])
        d = _n(np.array([u[0], u[1], u[2] + 0.6]) + np.array([r.gauss(0, 0.3), r.gauss(0, 0.3), 0]))
        up = _n(np.cross(d, np.cross(Z, d)) + 1e-3)
        if lo:
            _leaf_lo(mb, "v2_flower_leaf", p - d * 0.04, d, up, 0.11, 0.05, fold=0.2, droop=0.05)
        else:
            _leaf(mb, "v2_flower_leaf", p - d * 0.03, d, up, 0.08, 0.035, fold=0.25, droop=0.05)
    for i in range(heads):
        u = _n(np.array([r.gauss(0, 1), r.gauss(0, 1), abs(r.gauss(0, 0.6)) + 0.5]))
        k = r.uniform(0.75, 1.0)
        c = np.array([u[0] * r0 * k, u[1] * r0 * k, u[2] * h * k + 0.03])
        _ball(mb, mat, c, r.uniform(0.028, 0.04), lo)
    return mb

# ---- the light palms' cards (build_lod, the After Effects GLB: a frond or a fan is one card painted with its own
# leaflets, a few triangles instead of a few thousand) --------------------------------------------------------------
def _strip_colours(path, us=(0.5,), n=24):
    """the colours of a leaf strip texture as the 3D leaves show it (Blender reads the image bottom up): for each u
    in us, n colours from v = 0 (base) to v = 1 (tip), a narrow band averaged"""
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    h, w = a.shape[:2]
    out = []
    for u in us:
        x0, x1 = int(max(0, (u - 0.08) * w)), int(min(w, (u + 0.08) * w)) + 1
        col = a[:, x0:x1].mean(axis=1)
        out.append([tuple(col[int(round((1 - k / (n - 1)) * (h - 1)))]) for k in range(n)])
    return out


def _shade(c, f):
    return tuple(int(max(0, min(255, v * f))) for v in c) + (255,)


def tex_frond_card(name, leaf, seed, dead=False, H=1024):
    """a date palm frond lying flat (the rachis up the middle, base at the bottom), its leaflets either side painted
    with the leaflet texture `leaf` and spaced, angled and sized as _pinnate_frond's; alpha"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    from PIL import Image, ImageDraw
    r = random.Random(seed)
    cols = _strip_colours(leaf, us=(0.3,))[0]                  # beside the lighter midrib
    W = H // 4                                                # power of two; x squeezed by W / (2 CARD_HW H)
    bg = tuple(int(np.mean([c[k] for c in cols])) for k in range(3))
    im = Image.new("RGBA", (W, H), bg + (0,))
    d = ImageDraw.Draw(im)

    def X(x, y):
        return (W / 2 + x / CARD_HW * W / 2, H * (1 - y))
    tt, t = [], 0.18
    nleaf = 40 if dead else 82
    while t < 0.985:
        tt.append(t)
        t += (0.80 / nleaf) * (0.6 if (len(tt) % 3) else 1.8)
    for idx, t in enumerate(tt):
        prof = math.sin(math.pi * min(1.0, (t - 0.12) / 0.92)) ** 0.65
        for sg in (-1, 1):
            plane = (idx + (sg > 0)) % 3
            elev = math.radians((52, 22, 4)[plane] + r.uniform(-8, 8))
            ll = (0.11 + 0.05 * (0.5 if dead else 1.0)) * (0.25 + 0.75 * prof) * r.uniform(0.88, 1.08)
            ll *= abs(math.cos(elev - CARD_RISE))                    # seen in the card's plane
            fwd = math.radians(48 - 26 * t + r.uniform(-6, 6))
            dx, dy = sg * math.sin(fwd), math.cos(fwd)
            nx, ny = -dy, dx
            w = ll * r.uniform(0.060, 0.075)
            f = r.uniform(0.93, 1.07)
            bx, by = sg * 0.004, t
            steps = 6
            for k in range(steps):
                s0, s1 = k / steps, (k + 1) / steps
                ws = [w / 2 * (0.45 + 0.55 * min(1.0, s / 0.35) if s < 0.35 else 1.0 - 0.25 * (s - 0.35) / 0.35 if s < 0.7
                               else 0.75 * (1 - s) / 0.3) for s in (s0, s1)]
                c0 = (bx + dx * ll * s0, by + dy * ll * s0)
                c1 = (bx + dx * ll * s1, by + dy * ll * s1)
                poly = [X(c0[0] - nx * ws[0], c0[1] - ny * ws[0]), X(c0[0] + nx * ws[0], c0[1] + ny * ws[0]),
                        X(c1[0] + nx * ws[1], c1[1] + ny * ws[1]), X(c1[0] - nx * ws[1], c1[1] - ny * ws[1])]
                d.polygon(poly, fill=_shade(cols[min(len(cols) - 1, int((s0 + s1) / 2 * len(cols)))], f))
    rach = _hex("#7F7C4C")
    for k in range(24):
        t0, t1 = k / 24, (k + 1) / 24
        hw0, hw1 = (0.010 * (1 - 0.85 * t0) + 0.0015), (0.010 * (1 - 0.85 * t1) + 0.0015)
        d.polygon([X(-hw0, t0), X(hw0, t0), X(hw1, t1), X(-hw1, t1)], fill=_shade(tuple(rach), 1.0))
    im.save(p, optimize=True)
    return p


def tex_fan_card(name, seg, seed, H=512, W=512):
    """a Washingtonia fan seen from the front (the hastula low in the middle, the fan opening 115 degrees either side
    of up), its pleated segments painted with the segment texture `seg`, joined to 55 % and split beyond, as _fan's;
    alpha"""
    p = os.path.join(TEX, name)
    if os.path.exists(p):
        return p
    from PIL import Image, ImageDraw
    r = random.Random(seed)
    L, Mi, R_ = _strip_colours(seg, us=(0.22, 0.5, 0.78), n=16)
    bg = tuple(int(np.mean([c[k] for c in Mi])) for k in range(3))
    im = Image.new("RGBA", (W, H), bg + (0,))
    d = ImageDraw.Draw(im)

    def X(phi, rho):
        x, y = math.sin(phi) * rho, math.cos(phi) * rho
        return ((x + 1) / 2 * W, (1 - (y + FAN_Y0) / (1 + FAN_Y0)) * H)
    nseg, open_deg = 46, 115
    dphi = math.radians(2 * open_deg) / nseg
    st = (0.03, 0.18, 0.36, 0.55, 0.70, 0.85, 1.0)
    for k in range(nseg):
        phi_c = -math.radians(open_deg) + dphi * (k + 0.5)
        tipr = r.uniform(0.92, 1.0)
        f = r.uniform(0.94, 1.06)
        for j in range(len(st) - 1):
            row = []
            for rho in (st[j], st[j + 1]):
                free = max(0.0, (rho - 0.55) / 0.45)
                wf = 1.0 if rho <= 0.55 else (1 - free) ** 0.8
                rr = rho * (tipr if rho > 0.55 else 1.0)
                row.append([X(phi_c + side * dphi * wf, rr) for side in (-0.5, 0.0, 0.5)])
            ci = min(15, int((st[j] + st[j + 1]) / 2 * 16))
            d.polygon([row[0][0], row[0][1], row[1][1], row[1][0]], fill=_shade(L[ci], f))
            d.polygon([row[0][1], row[0][2], row[1][2], row[1][1]], fill=_shade(R_[ci], f))
    im.save(p, optimize=True)
    return p


CARD_HW = 0.14                 # a frond card's half width, in frond lengths
CARD_RISE = math.radians(25)   # its halves rise from the rachis (the palm's V)
FAN_Y0 = 0.43                  # a fan card's texture reaches 0.43 R below the hastula (115 degrees each side)


def card_materials(M):
    """the cards' materials (alpha), with the leaflet textures they are painted from"""
    M["v2_date_card"] = _img_mat("V2_Date_Frond_Card", tex_frond_card("TEX_V2_DATE_FROND_CARD.png", os.path.join(TEX, "TEX_V2_DATE_LEAFLET.jpg"), 41), 0.55, 0.30, alpha=True)
    M["v2_date_card_old"] = _img_mat("V2_Date_Frond_Card_Old", tex_frond_card("TEX_V2_DATE_FROND_CARD_OLD.png", os.path.join(TEX, "TEX_V2_DATE_LEAFLET_OLD.jpg"), 42), 0.6, 0.25, alpha=True)
    M["v2_dead_card"] = _img_mat("V2_Palm_Dead_Frond_Card", tex_frond_card("TEX_V2_DEAD_FROND_CARD.png", os.path.join(TEX, "TEX_V2_PALM_DEAD.jpg"), 43, dead=True), 0.85, 0.05, alpha=True)
    M["v2_fan_card"] = _img_mat("V2_Washingtonia_Fan_Card", tex_fan_card("TEX_V2_FAN_CARD.png", os.path.join(TEX, "TEX_V2_FAN_SEGMENT.jpg"), 44), 0.5, 0.30, alpha=True)
    M["v2_fan_card_old"] = _img_mat("V2_Washingtonia_Fan_Card_Old", tex_fan_card("TEX_V2_FAN_CARD_OLD.png", os.path.join(TEX, "TEX_V2_FAN_SEGMENT_OLD.jpg"), 45), 0.6, 0.25, alpha=True)
    M["v2_dead_fan_card"] = _img_mat("V2_Palm_Dead_Fan_Card", tex_fan_card("TEX_V2_DEAD_FAN_CARD.png", os.path.join(TEX, "TEX_V2_PALM_DEAD.jpg"), 46), 0.85, 0.05, alpha=True)
    return M


def _frond_card(mb, r, base, az, el, droop, length, age, mat, spread=1.0, ns=6):
    """a date palm frond as two cards (the light palms): the rachis curving as _pinnate_frond's, a card either side
    rising CARD_RISE (less with age), its leaflets drooping at the edge, painted by tex_frond_card"""
    hd = np.array([math.cos(az), math.sin(az), 0.0])
    twist = r.uniform(-0.15, 0.15)
    pts, dirs = [base], []
    for k in range(ns):
        t = (k + 0.5) / ns
        e = el - droop * t ** 1.25
        d = _rot(hd * math.cos(e) + Z * math.sin(e), Z, twist * t)
        dirs.append(d)
        pts.append(pts[-1] + d * length / ns)
    hw = CARD_HW * length * (0.11 + 0.05 * spread) / 0.16
    rise = CARD_RISE - math.radians(18) * age
    dro = (0.12 + 0.25 * age) * 0.5
    rows = []
    for k in range(ns + 1):
        d, s, u = _frame(dirs[min(k, ns - 1)])
        p = pts[k]
        rows.append([p + (-s * math.cos(rise) + u * math.sin(rise)) * hw - Z * dro * hw, p,
                     p + (s * math.cos(rise) + u * math.sin(rise)) * hw - Z * dro * hw])
    uvs = [[(0.0, k / ns), (0.5, k / ns), (1.0, k / ns)] for k in range(ns + 1)]
    _grid(mb, mat, rows, uvs)


def _fan_card(mb, r, hast, f, R, mat, open_deg=115, droop=1.0, fold=0.35, dead=False, ncol=6):
    """a Washingtonia fan as one card (the light palms): cupped and drooping at its split tips as _fan's, painted by
    tex_fan_card"""
    f, s, n = _frame(f)
    if dead:
        n = -n
    sd = r.uniform(0.7, 1.3) * droop
    rows, uvs = [], []
    for rho in (0.03, 0.55, 0.8, 1.0):
        free = max(0.0, (rho - 0.55) / 0.45)
        row, uv = [], []
        for i in range(ncol + 1):
            phi = math.radians(-open_deg + 2 * open_deg * i / ncol)
            rd = f * math.cos(phi) + s * math.sin(phi)
            q = hast + rd * R * rho + n * (fold * R * abs(math.sin(phi)) * rho * 0.6)
            row.append(q - Z * (R * 0.22 * rho * rho + R * 0.75 * sd * free * free * (0.6 + 0.4 * abs(math.sin(phi)))))
            uv.append(((math.sin(phi) * rho + 1) / 2, (math.cos(phi) * rho + FAN_Y0) / (1 + FAN_Y0)))
        rows.append(row)
        uvs.append(uv)
    _grid(mb, mat, rows, uvs)


# ---- beds and planters (the client's notes: the planting along the walls and the stairs, the jars) -----------------
MIX = (("grass", 0.30), ("lavender", 0.36), ("agave_b", 0.20), ("agave", 0.14))
SCALE = {"grass": (0.8, 1.1), "lavender": (0.85, 1.15), "agave": (0.6, 0.85), "agave_b": (0.8, 1.05),
         "jar": (0.85, 1.05), "amphora": (0.8, 1.0), "olive": (0.45, 0.55)}


def clean(g, r=0.15, min_area=1.0):
    """a bed's polygon(s) without its slivers"""
    from shapely.ops import unary_union
    g = g.buffer(-r, join_style=2).buffer(r, join_style=2)
    return unary_union([q for q in L.as_polys(g) if q.area >= min_area])


def bed_surface(mb, q, z, edge=True):
    """a bed: beige gravel mulch 3 cm over z, a slim stone edging 8 cm high round it"""
    flat = lambda x, y: z
    if edge:
        ring = q.difference(q.buffer(-0.07, join_style=2))
        L.prism(mb, "coping_beige", ring, -0.25, 0.08, zf=flat)
        q = q.buffer(-0.07, join_style=2)
    L.prism(mb, "v2_gravel", q, -0.25, 0.03, zf=flat)


def bed_plants(q, z, put, rng, mix=MIX, jar_every=7.0, density=1.0, spacing=0.62, avoid=None):
    """drifts of grasses, lavender and agaves in a bed (the species set in 2.2 m patches, so they read as drifts),
    a terracotta jar about every jar_every metres; put(key, xy, z, scale). Returns the number of plants."""
    from shapely.geometry import Point
    inner = q.buffer(-0.28, join_style=2)
    if inner.is_empty:
        return 0
    x0, y0, x1, y1 = inner.bounds
    n = int(q.area / 0.48 * density)
    pts, jars = [], []
    for _ in range(n * 12):
        if len(pts) >= n:
            break
        p = Point(rng.uniform(x0, x1), rng.uniform(y0, y1))
        if inner.contains(p) and all(p.distance(o) > spacing for o in pts) and (avoid is None or not avoid.contains(p)):
            pts.append(p)
    keys, w = zip(*mix)
    for p in pts:
        if jar_every and all(p.distance(j) > jar_every for j in jars) and rng.random() < 0.35:
            k = "jar" if rng.random() < 0.6 else "amphora"
            jars.append(p)
        else:
            cell = (int(math.floor(p.x / 2.2)) * 92821 + int(math.floor(p.y / 2.2)) * 68917) % 1000 / 1000.0
            acc, k = 0.0, keys[-1]
            for kk, ww in zip(keys, w):
                acc += ww
                if cell < acc:
                    k = kk
                    break
        put(k, (p.x, p.y), z + (0.03 if k not in ("jar", "amphora") else 0.0), rng.uniform(*SCALE[k]))
    return len(pts)


def planter_box(mb, q, z, h=0.45, wall="cladding"):
    """a raised planter as the pool reference: stone faces, a beige coping, the soil 5 cm under it; returns the
    soil's level"""
    flat = lambda x, y: z
    ring = q.difference(q.buffer(-0.14, join_style=2))
    L.prism(mb, wall, ring, -0.20, h, zf=flat)
    L.prism(mb, "coping_beige", q.difference(q.buffer(-0.17, join_style=2)), h, h + 0.05, zf=flat)
    L.prism(mb, "soil", q.buffer(-0.14, join_style=2), -0.20, h - 0.05, zf=flat, sides=False)
    return z + h - 0.05


def garden_trees(mb, region, beds, foot, z, put, rng, taken, olive=True):
    """client 27-10 ("add palms and trees, something cool, on the duplex and villas, this looks empty"): a garden's
    trees as a composition: a grove of three date palms of three heights in its far corner (a gravel island and
    agaves under them where it stands in the lawn), a pair of Washingtonias along its longest bed, one olive tree in
    the open lawn, flowering shrubs against the walls. region: where trees may stand (lawn and beds, clear of the
    house, terraces and pool), beds: the beds along the walls, foot: the house, z: the lawn's level, taken: Points
    already planted (extended). Returns the number of trees."""
    from shapely.geometry import LineString, Point
    n0 = len(taken)
    if region.is_empty:
        return 0
    free = lambda p, d=2.2: region.buffer(-0.7).contains(p) and all(p.distance(q) > d for q in taken)
    # the grove in the far corner, near the walls
    inner = region.buffer(-1.4)
    x0, y0, x1, y1 = region.bounds
    best = None
    for _ in range(260):
        p = Point(rng.uniform(x0, x1), rng.uniform(y0, y1))
        if inner.contains(p) and region.boundary.distance(p) < 3.2 and all(p.distance(q) > 3.0 for q in taken):
            sc_ = foot.distance(p) if not foot.is_empty else 5.0
            if best is None or sc_ > best[0]:
                best = (sc_, p)
    if best is not None:
        c = best[1]
        a0 = rng.uniform(0, 2 * math.pi)
        in_lawn = beds.is_empty or not beds.buffer(0.2).contains(c)
        if in_lawn:
            isl = c.buffer(2.3, 24).intersection(region.buffer(-0.3))
            if beds is not None and not beds.is_empty:
                isl = isl.difference(beds)
            if not isl.is_empty and isl.area > 3.0:
                bed_surface(mb, isl, z)
        for (dx, dy), s_ in (((0.0, 0.0), 0.85), ((1.35, 0.45), 0.70), ((0.40, 1.35), 0.58)):
            p = Point(c.x + dx * math.cos(a0) - dy * math.sin(a0), c.y + dx * math.sin(a0) + dy * math.cos(a0))
            if region.buffer(-0.5).contains(p):
                put("date", (p.x, p.y), z + 0.03, s_ * rng.uniform(0.95, 1.05))
                taken.append(p)
        for k in range(5):                                        # agaves and grasses under the grove
            r_, t_ = rng.uniform(1.3, 2.0), a0 + 2 * math.pi * k / 5 + 0.3
            p = Point(c.x + 0.6 * math.cos(a0) + r_ * math.cos(t_), c.y + 0.6 * math.sin(a0) + r_ * math.sin(t_))
            if region.buffer(-0.4).contains(p):
                put("agave_b" if k % 2 else "grass", (p.x, p.y), z + 0.03, rng.uniform(0.85, 1.05))
    # a pair of Washingtonias along the longest bed
    if beds is not None and not beds.is_empty:
        g = max(L.as_polys(beds), key=lambda q: q.area)
        r = list(g.minimum_rotated_rectangle.exterior.coords)[:4]
        e = max(((r[k], r[(k + 1) % 4]) for k in range(4)), key=lambda ab: math.dist(*ab))
        ln = LineString(e)
        if ln.length > 7.0:
            for t in (0.25, 0.75):
                p = ln.interpolate(t, normalized=True)
                p = g.exterior.interpolate(g.exterior.project(p)) if not g.contains(p) else p
                q = Point(*(np.array(p.coords[0]) + (np.array(g.centroid.coords[0]) - np.array(p.coords[0])) * 0.3))
                if free(q, 2.6) or (g.contains(q) and all(q.distance(o) > 2.6 for o in taken)):
                    put("wash", (q.x, q.y), z + 0.03, rng.uniform(0.62, 0.72))
                    taken.append(q)
            for t in (0.08, 0.5, 0.92):                            # flowering shrubs against the wall
                p = ln.interpolate(t, normalized=True)
                if g.buffer(0.1).contains(p) and all(p.distance(o) > 1.2 for o in taken):
                    put("shrub_pink", (p.x, p.y), z + 0.03, rng.uniform(0.9, 1.15))
    # one olive tree in the open lawn
    if olive:
        best = None
        for _ in range(200):
            p = Point(rng.uniform(x0, x1), rng.uniform(y0, y1))
            if inner.contains(p) and (beds is None or beds.is_empty or not beds.buffer(0.8).contains(p)):
                d = min([p.distance(q) for q in taken] + [6.0]) + 0.3 * min(foot.distance(p) if not foot.is_empty else 4.0, 4.5)
                if best is None or d > best[0]:
                    best = (d, p)
        if best is not None and best[0] > 2.4:
            put("olive", (best[1].x, best[1].y), z, rng.uniform(0.6, 0.72))
            taken.append(best[1])
    return len(taken) - n0


def garden_photo(region, foot, z, put, rng, taken=None):
    """client 28-10 (the D5 duplex he sent: "dir chjar w rbi3 like li f tswira ... f duplex kamlin villas, ykunu nitum"):
    a garden planted as that picture, and neat: a date palm in each of its two far corners, one big olive tree in the
    open lawn, an orange tree along the side, smaller olive trees spaced out, low shrubs at the palms' feet, tufts of
    orange, white and purple flowers dotted on the lawn along its edges. No gravel beds. region: the lawn clear of the
    house, terraces, paths and walls; foot: the house(s); z: the lawn's level. Returns the number of plants."""
    from shapely.geometry import Point
    from shapely.prepared import prep
    placed = [] if taken is None else taken
    if region.is_empty or region.area < 14.0:
        return 0
    inner = region.buffer(-1.0)
    if inner.is_empty:
        return 0
    house = min(L.as_polys(foot), key=lambda q: q.distance(region)) if not foot.is_empty else region.centroid
    hc = np.array(house.centroid.coords[0])
    bnd = region.boundary
    pin = prep(inner)
    x0, y0, x1, y1 = inner.bounds
    cand = [Point(x, y) for x in np.arange(x0, x1 + 0.01, 0.5) for y in np.arange(y0, y1 + 0.01, 0.5)]
    cand = [p for p in cand if pin.contains(p)]
    if not cand:
        return 0
    edge = {id(p): bnd.distance(p) for p in cand}
    dist = lambda p: min([p.distance(q) for q in placed] + [99.0])
    n = 0

    def unit(p):
        v = np.array(p.coords[0]) - hc
        return v / (np.linalg.norm(v) + 1e-9)
    # a date palm in the far corner, a second one in another corner
    corner = [p for p in cand if edge[id(p)] < 1.7] or cand
    p1 = max(corner, key=lambda p: house.distance(p))
    palms = [p1]
    c2 = [p for p in corner if p.distance(p1) > 6.0 and float(np.dot(unit(p), unit(p1))) < 0.3]
    if c2:
        palms.append(max(c2, key=lambda p: house.distance(p) + 0.5 * min(p.distance(p1), 12.0)))
    for p in palms:
        put("date", (p.x, p.y), z + 0.03, rng.uniform(0.72, 0.86))
        placed.append(p)
        n += 1
    # one big olive tree in the most open spot of the lawn
    open_ = [p for p in cand if dist(p) > 3.5 and edge[id(p)] > 1.6]
    if open_:
        p = max(open_, key=lambda p: min(edge[id(p)], house.distance(p)) + 0.15 * min(dist(p), 8.0))
        put("olive", (p.x, p.y), z, rng.uniform(0.72, 0.8))
        placed.append(p)
        n += 1
    # orange trees, then smaller olive trees, each as far as it can be from what is planted
    plan = ["citrus"] * (1 if region.area < 130 else 2) + ["olive"] * int(np.clip(region.area / 55.0, 1, 3))
    for key in plan:
        free = [p for p in cand if edge[id(p)] > 1.2]
        if not free:
            break
        p = max(free, key=dist)
        if dist(p) < 2.8:
            break
        put(key, (p.x, p.y), z, rng.uniform(0.95, 1.1) if key == "citrus" else rng.uniform(0.48, 0.58))
        placed.append(p)
        n += 1
    # low shrubs at the palms' feet
    rin = prep(region.buffer(-0.3))
    for p in palms:
        for k in range(2):
            a = rng.uniform(0, 2 * math.pi)
            q = Point(p.x + math.cos(a) * rng.uniform(0.9, 1.3), p.y + math.sin(a) * rng.uniform(0.9, 1.3))
            if rin.contains(q):
                put("shrub", (q.x, q.y), z + 0.02, rng.uniform(0.75, 0.95))
                n += 1
    # tufts of flowers on the lawn along its edges, spaced out
    kinds = ("flower_orange", "flower_orange", "flower_white", "lavender")
    j = 0
    for ring in L.as_polys(region.buffer(-0.75)):
        ln = ring.exterior
        for t in np.arange(rng.uniform(0.5, 1.5), ln.length, 3.0):
            q = ln.interpolate(t)
            if min([q.distance(o) for o in placed] + [9.0]) < 1.1:
                continue
            put(kinds[j % len(kinds)], (q.x, q.y), z + 0.02, rng.uniform(0.85, 1.15))
            j += 1
            n += 1
    return n


def build_sources(M, col):
    """the library's sources, keyed as 05's srcv: (key -> object); variants listed under key + '_v'"""
    materials(M)
    S = {}
    S["date"] = source("DATE_PALM_V2_A", date_palm(4, 5.0), M, col)
    S["date_v"] = [S["date"], source("DATE_PALM_V2_B", date_palm(7, 5.6, n_fronds=42), M, col),
                   source("DATE_PALM_V2_C", date_palm(12, 4.6, n_fronds=38, dates=False), M, col)]
    S["wash"] = source("WASHINGTONIA_V2_A", washingtonia(1, 9.0, skirt=True), M, col)
    S["wash_v"] = [S["wash"], source("WASHINGTONIA_V2_B", washingtonia(3, 9.6, skirt=False), M, col),
                   source("WASHINGTONIA_V2_C", washingtonia(8, 8.4, skirt=True), M, col)]
    S["olive"] = source("OLIVE_TREE_V2_A", olive(6), M, col)
    S["olive_v"] = [S["olive"], source("OLIVE_TREE_V2_B", olive(9, 3.8, 3.4), M, col)]
    S["grass"] = source("FOUNTAIN_GRASS_V2", grass(5), M, col)
    S["agave"] = source("AGAVE_V2", agave(3), M, col)
    S["agave_b"] = source("AGAVE_V2_SMALL", agave(8, n=24, length=0.5), M, col)
    S["lavender"] = source("LAVENDER_V2", lavender(6), M, col)
    S["jar"] = source("JAR_KHABIA_V2", jar(2, "khabia", 0.85), M, col)
    S["amphora"] = source("JAR_AMPHORA_V2", jar(4, "amphora", 1.05), M, col)
    S["citrus"] = source("CITRUS_V2", citrus(15), M, col)              # client 28-10: his D5 garden
    S["citrus_v"] = [S["citrus"], source("CITRUS_V2_B", citrus(23, 2.3, 2.0), M, col)]
    S["flower_orange"] = source("FLOWERS_ORANGE_V2", flowers(5, "v2_flower_orange"), M, col)
    S["flower_white"] = source("FLOWERS_WHITE_V2", flowers(9, "v2_flower_white"), M, col)
    for o in list(S.values()):
        for ob in (o if isinstance(o, list) else [o]):
            ob.hide_render = True
            ob.hide_viewport = True
    return S


LOD = {"DATE_PALM_V2_A": lambda: date_palm(4, 5.0, lo=True, cards=True),
       "DATE_PALM_V2_B": lambda: date_palm(7, 5.6, n_fronds=42, lo=True, cards=True),
       "DATE_PALM_V2_C": lambda: date_palm(12, 4.6, n_fronds=38, dates=False, lo=True, cards=True),
       "WASHINGTONIA_V2_A": lambda: washingtonia(1, 9.0, skirt=True, lo=True, cards=True),
       "WASHINGTONIA_V2_B": lambda: washingtonia(3, 9.6, skirt=False, lo=True, cards=True),
       "WASHINGTONIA_V2_C": lambda: washingtonia(8, 8.4, skirt=True, lo=True, cards=True),
       "OLIVE_TREE_V2_A": lambda: olive(6, lo=True), "OLIVE_TREE_V2_B": lambda: olive(9, 3.8, 3.4, lo=True),
       "FOUNTAIN_GRASS_V2": lambda: grass(5, n=30, plumes=6, lo=True), "AGAVE_V2": lambda: agave(3, n=10, lo=True),
       "AGAVE_V2_SMALL": lambda: agave(8, n=8, length=0.5, lo=True), "LAVENDER_V2": lambda: lavender(6, needles=34, spikes=12, lo=True),
       "JAR_KHABIA_V2": lambda: jar(2, "khabia", 0.85, lo=True), "JAR_AMPHORA_V2": lambda: jar(4, "amphora", 1.05, lo=True),
       "CITRUS_V2": lambda: citrus(15, lo=True), "CITRUS_V2_B": lambda: citrus(23, 2.3, 2.0, lo=True),
       "FLOWERS_ORANGE_V2": lambda: flowers(5, "v2_flower_orange", leaves=40, heads=18, lo=True),
       "FLOWERS_WHITE_V2": lambda: flowers(9, "v2_flower_white", leaves=40, heads=18, lo=True)}


def build_lod(M, col):
    """the light versions of the sources (the light GLB for After Effects, client 27-10): the same plants with the same
    materials and textures, about 25 times fewer triangles (the palms' fronds and fans as cards painted with their
    own leaflets, card_materials); {source mesh name: light object}. A variant named instead of built shares that
    light version"""
    materials(M)
    card_materials(M)
    S = {}
    for k, make in LOD.items():
        if callable(make):
            S["SRC_" + k] = ob = source(k + "_LOD", make(), M, col)
            ob.hide_render = ob.hide_viewport = True
    for k, make in LOD.items():
        if not callable(make):
            S["SRC_" + k] = S["SRC_" + make]
    return S


def vary(S, seed=26):
    """every instance of the date palm and the Washingtonia on one of their variants (deterministic)"""
    rng = random.Random(seed)
    n = 0
    for key in ("date", "wash", "olive", "citrus"):
        base = S[key].data
        vs = [o.data for o in S[key + "_v"]]
        for ob in bpy.data.objects:
            if ob.type == "MESH" and ob.data == base and not ob.name.startswith("SRC_"):
                ob.data = vs[rng.randrange(len(vs))]
                n += 1
    return n
