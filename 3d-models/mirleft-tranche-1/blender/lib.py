"""
lib — shared helpers for the Mirleft 1er TRANCHE scene (same base as the Tranche A+B model).

Reuses the Mirleft Bay project next door (../mirleft-bay) so both models look the same:
its config helpers (MeshBuilder, collections), its material library (Poly Haven maps where the
folders exist, procedural otherwise), its plant generators and its sun/sky presets.
"""
import importlib.util
import math
import os

import bpy  # noqa: I001  (bpy before bmesh)
import numpy as np
import shapely
from shapely.geometry import MultiPolygon, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BAY = os.path.join(os.path.dirname(ROOT), "mirleft-bay", "blender")
TEX = os.path.join(ROOT, "data", "textures")
os.makedirs(TEX, exist_ok=True)


def _load(path, name, C=None):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    if C is not None:
        mod.__dict__["C"] = C
    spec.loader.exec_module(mod)
    return mod


C = _load(os.path.join(BAY, "00_config.py"), "bay_config")


def bay(fname):
    return _load(os.path.join(BAY, fname), "bay_" + fname[:2], C)


# ---- materials -------------------------------------------------------------------------------
def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


def mashrabiya_png():
    """Diamond lattice with rings at the crossings, as drawn on the duplex facades (layer 'motif en bois')."""
    path = os.path.join(TEX, "TEX_MASHRABIYA_LATTICE.png")
    if os.path.exists(path):
        return path
    from PIL import Image, ImageDraw
    N = 512
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = 30
    col = (255, 255, 255, 255)
    for k in range(-2, 3):
        o = k * N
        d.line([(o, 0), (o + N, N)], fill=col, width=w)
        d.line([(o + N, 0), (o, N)], fill=col, width=w)
        d.line([(o + N // 2, 0), (o + N // 2 + N, N)], fill=col, width=w)
        d.line([(o + N // 2 + N, 0), (o + N // 2, N)], fill=col, width=w)
    for cx, cy in [(0, 0), (N, 0), (0, N), (N, N), (N // 2, N // 2), (N // 2, 0), (0, N // 2), (N, N // 2), (N // 2, N)]:
        r = 46
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=22)
    d.rectangle([0, 0, N - 1, N - 1], outline=col, width=10)
    im.save(path)
    return path


def lattice_mat(name, hexcol, png, scale):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(png, check_existing=True)
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 40.0
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.inputs[0].default_value = 0.08
    mx.inputs[6].default_value = srgb(hexcol)
    nt.links.new(nz.outputs["Color"], mx.inputs[7])
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], im.inputs["Vector"])
    nt.links.new(mx.outputs[2], bs.inputs["Base Color"])
    nt.links.new(im.outputs["Alpha"], bs.inputs["Alpha"])
    bs.inputs["Roughness"].default_value = 0.65
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    m.blend_method = "HASHED" if hasattr(m, "blend_method") else None
    return m


def uv_tiles(m, rot_deg=0.0):
    """Drive the brick texture of a tiles() material with UV (metres) instead of Object coords,
    so vertical cladding reads as tiles on every face. rot_deg turns the pattern (45 = diagonal)."""
    nt = m.node_tree
    br = [n for n in nt.nodes if n.type == "TEX_BRICK"][0]
    tc = [n for n in nt.nodes if n.type == "TEX_COORD"][0]
    if rot_deg:
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(rot_deg))
        nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], br.inputs["Vector"])
    else:
        nt.links.new(tc.outputs["UV"], br.inputs["Vector"])
    return m



# ---- generated textures (rev 4 remarks): beige herringbone pavers, slate-look porcelain tiles, ochre
# stone band. Drawn here, cached in data/textures/, used by the scene and by 08/09 for D5 and glTF.
def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def tnoise(n, beta, seed, aniso=1.0):
    """Tileable fractal noise in [0, 1]: white noise shaped by 1/f^beta in Fourier space.
    aniso > 1 stretches the features along x (streaks)."""
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(n, n))
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    f = np.sqrt((fx * aniso) ** 2 + (fy / aniso) ** 2)
    f[0, 0] = 1.0
    s = np.real(np.fft.ifft2(np.fft.fft2(w) / f ** beta))
    s -= s.min()
    return s / s.max()


def herringbone(path, n=1024, units=8, seed=3, pal=None, joint="#A39283"):
    """90-degree herringbone of 2:1 pavers, tileable; units = paver widths (0.10 m) per tile edge."""
    rng = np.random.default_rng(seed)
    px = n / units
    pal = [hexc(c) for c in (pal or ("#D9BEA3", "#CFB295", "#DCC5AB", "#C9AA8F", "#D3B59B", "#E0CBB2"))]
    joint = hexc(joint)
    img = np.zeros((n, n, 3), np.float32) + joint
    grain = tnoise(n, 1.1, seed + 1)[..., None]
    yy, xx = np.mgrid[0:n, 0:n]
    bricks = []
    for k in range(units):
        for j in range(units // 4):
            ox, oy = k + 4 * j, k
            bricks.append((ox, oy, ox + 2, oy + 1))          # horizontal
            bricks.append((ox, oy + 1, ox + 1, oy + 3))      # vertical
    e = 3.0
    for (x0, y0, x1, y1) in bricks:
        col = pal[rng.integers(len(pal))] * rng.uniform(0.95, 1.04)
        for dx in (-units, 0, units):
            for dy in (-units, 0, units):
                a0, a1 = (x0 + dx) * px + e, (x1 + dx) * px - e
                b0, b1 = (y0 + dy) * px + e, (y1 + dy) * px - e
                if a1 < 0 or b1 < 0 or a0 > n or b0 > n:
                    continue
                i0, i1 = max(int(np.ceil(a0)), 0), min(int(a1), n)
                j0, j1 = max(int(np.ceil(b0)), 0), min(int(b1), n)
                if i1 <= i0 or j1 <= j0:
                    continue
                sub = img[j0:j1, i0:i1]
                # soft chamfer: darker within 4 px of the edge
                xs = np.minimum(xx[j0:j1, i0:i1] - a0, a1 - xx[j0:j1, i0:i1])
                ys = np.minimum(yy[j0:j1, i0:i1] - b0, b1 - yy[j0:j1, i0:i1])
                d = np.clip(np.minimum(xs, ys) / 5.0, 0, 1)[..., None]
                sub[:] = col * (0.86 + 0.14 * d)
    img = img * (0.9 + 0.2 * grain)
    img += np.random.default_rng(seed + 2).normal(0, 3.0, img.shape)
    from PIL import Image
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(path, quality=90)



def slate_tiles(path, base, light, vein, grout, seed, n=1024, period=1.2, tw=0.60, th=0.30, aniso=3.0, contrast=1.0):
    """Stone-look porcelain (slate cleft): 0.30 x 0.60 tiles in half bond, tileable over `period` m."""
    rng = np.random.default_rng(seed)
    ppm = n / period
    base, light, vein, grout = hexc(base), hexc(light), hexc(vein), hexc(grout)
    big = tnoise(n, 1.7, seed, aniso)
    mid = tnoise(n, 1.15, seed + 1, aniso * 1.3)
    cleft = tnoise(n, 0.95, seed + 3, 1.3)
    fine = tnoise(n, 0.55, seed + 2)
    t = np.clip((big - 0.5) * 1.8 * contrast + 0.5, 0, 1)[..., None]
    img = base * (1 - t) + light * t
    v = np.clip((mid - 0.58) * 4.0, 0, 1)[..., None] * contrast
    img = img * (1 - 0.6 * v) + vein * 0.6 * v
    c = np.clip((cleft - 0.5) * 3.0, -1, 1)[..., None]
    img *= 1.0 + 0.10 * c * contrast                      # cleft relief: patchy light and shade
    sp = (rng.random((n, n)) < 0.004)[..., None]
    img = np.where(sp, img * 0.78 + vein * 0.22, img)
    img *= (0.90 + 0.20 * fine[..., None])
    # per tile brightness shift, grout lines
    rows = int(round(period / th))
    cols = int(round(period / tw))
    yy, xx = np.mgrid[0:n, 0:n]
    r = (yy / (th * ppm)).astype(int)
    off = np.where(r % 2 == 1, tw * ppm / 2, 0)
    c = (((xx + off) / (tw * ppm)).astype(int)) % cols
    shift = rng.uniform(0.93, 1.07, (rows + 1, cols + 1))
    img *= shift[r % rows, c][..., None]
    g = 2.0
    gx = np.mod(xx + off, tw * ppm)
    gy = np.mod(yy, th * ppm)
    mask = (np.minimum(gx, tw * ppm - gx) < g) | (np.minimum(gy, th * ppm - gy) < g)
    img[mask] = grout
    from PIL import Image
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(path, quality=90)


def marble_band(path, seed=11, n=1024):
    """Golden-ochre veined stone for the cornice band (as on the reference renders)."""
    base, light, dark = hexc("#C0904E"), hexc("#DDBF8A"), hexc("#7E5128")
    a = tnoise(n, 1.5, seed, 2.5)
    b = tnoise(n, 1.0, seed + 1, 4.0)
    t = np.clip((a - 0.45) * 2.0 + 0.5, 0, 1)[..., None]
    img = base * (1 - t) + light * t
    veins = np.abs(np.sin(b * 18.0 + a * 6.0))
    v = np.clip((0.18 - veins) / 0.18, 0, 1)[..., None]
    img = img * (1 - 0.7 * v) + dark * 0.7 * v
    img *= (0.94 + 0.12 * tnoise(n, 0.6, seed + 2)[..., None])
    from PIL import Image
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(path, quality=90)


TEXTURES = {
    "pavers": ("TEX_PAVERS_BEIGE_HERRINGBONE.jpg", 0.80),
    "sidewalk": ("TEX_PAVERS_SIDEWALK_GREY.jpg", 0.80),
    "ardesia": ("TEX_TILE_ARDESIA_BEIGE.jpg", 1.20),
    "jade": ("TEX_TILE_JADE_GREEN.jpg", 1.20),
    "band": ("TEX_STONE_BAND_OCHRE.jpg", 0.80),
}


def texture(key):
    """Path of a generated texture (drawn on first use) and its tile size in metres."""
    fname, tile = TEXTURES[key]
    path = os.path.join(TEX, fname)
    if not os.path.exists(path):
        if key == "pavers":
            herringbone(path)
        elif key == "sidewalk":                 # pavements (trottoirs): grey pavers (client, 19-10)
            herringbone(path, seed=5, pal=("#8E8C88", "#85837F", "#979590", "#7E7C78", "#8A8783", "#9C9994"), joint="#605E5B")
        elif key == "ardesia":                  # beige slate-look porcelain, 30 x 60 (AZUVI Ardesia Nature type)
            slate_tiles(path, "#C4B092", "#DDCFB6", "#B08A55", "#B9B0A4", 21, aniso=1.8)
        elif key == "jade":                     # green-grey stone-look pool tile, 30 x 60 (La Platera Jade type)
            slate_tiles(path, "#67716B", "#87918A", "#4A524D", "#525A55", 31, aniso=1.8, contrast=0.9)
        else:
            marble_band(path)
    return path, tile


def img_mat(name, key, rough=0.75, bump=0.2):
    """Image texture at true size on the UVs (metres), with a light bump from its luminance."""
    path, tile = texture(key)
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0 / tile, 1.0 / tile, 1.0)
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(path, check_existing=True)
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.004
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], im.inputs["Vector"])
    nt.links.new(im.outputs["Color"], bs.inputs["Base Color"])
    nt.links.new(im.outputs["Color"], bw.inputs["Color"])
    nt.links.new(bw.outputs["Val"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bs.inputs["Normal"])
    bs.inputs["Roughness"].default_value = rough
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    m["source"] = "generated in lib.py: " + os.path.basename(path) + ", tile %.2f m" % tile
    return m


SAND = "#C8AA86"            # building render (rev 4, client photos)


def materials():
    mod = bay("07_build_materials.py")
    M = mod.build()
    M["mashrabiya"] = lattice_mat("D01_Mashrabiya_Wood", "#3B2414", mashrabiya_png(), 1.0)
    M["door_wood"] = mod.simple("D02_Door_Wood_Dark", "#5C3A22", 0.55, 0.0, 6.0, 0.2, 0.1)
    M["slate"] = mod.simple("D03_Slate_Access", "#4F5257", 0.7, 0.0, 10.0, 0.25, 0.2)
    M["trim"] = mod.render_plaster("D04_Render_Trim", "#E2CBA6", "#D3B990")
    M["bejmat"] = uv_tiles(mod.tiles("D05_Bejmat_Terre_De_Sienne", "#A0522D", "#8B4526", 0.10, 0.05, "#6E4A36", 0.004, 0.7, 0.3, 0.5))
    M["turf"] = mod.simple("D06_Synthetic_Turf", "#3F7F3A", 0.85, 0.0, 60.0, 0.12, 0.1)
    M["tennis"] = mod.simple("D07_Tennis_Acrylic", "#2F6E8F", 0.6, 0.0, 30.0, 0.06, 0.05)
    M["play"] = mod.simple("D08_Play_Rubber", "#C9734A", 0.9, 0.0, 30.0, 0.15, 0.1)
    M["sand"] = mod.simple("D09_Sand", "#D9C49A", 0.95, 0.0, 40.0, 0.25, 0.3)
    M["deck"] = M["timber"]
    M["sienna"] = mod.render_plaster("D10_Render_Terre_De_Sienne", "#B9774C", "#A5633D")
    M["roof_tiles"] = uv_tiles(mod.tiles("D11_Roof_Tiles_Terracotta", "#A9573A", "#8E452D", 0.30, 0.20, "#6B3B2A", 0.006, 0.7, 0.4, 0.5))
    M["island"] = uv_tiles(mod.tiles("D12_Island_Diagonal_Pavers", "#DCD1BD", "#CDBFA6", 0.50, 0.50, "#9C9080", 0.006, 0.7, 0.25, 0.0), 45.0)
    # 1er TRANCHE: the plan's hatches (AR-HBONE herringbone, AR-CONC, stabilisé) and the pool court
    M["lane"] = uv_tiles(mod.tiles("T01_Pavers_Herringbone_Charcoal", "#5A5B5E", "#4B4C50", 0.20, 0.10, "#38393B", 0.005, 0.8, 0.35, 0.5), 45.0)
    M["terrace_hb"] = uv_tiles(mod.tiles("T02_Pavers_Herringbone_Light", "#D9D6CF", "#CBC7BE", 0.20, 0.10, "#A9A49A", 0.004, 0.75, 0.25, 0.5), 45.0)
    M["terracotta"] = uv_tiles(mod.tiles("T03_Terracotta_Herringbone", "#C47A4F", "#B26A42", 0.20, 0.10, "#8A5A40", 0.004, 0.7, 0.3, 0.5), 45.0)
    M["concrete"] = uv_tiles(mod.tiles("T04_Concrete_Slabs", "#C9C6BF", "#BDB9B1", 0.40, 0.40, "#9E9A92", 0.004, 0.8, 0.25, 0.0))
    M["stabilise"] = mod.simple("T05_Stabilise_Sand", "#CDB894", 0.95, 0.0, 30.0, 0.25, 0.25)
    M["deck_stone"] = uv_tiles(mod.tiles("T06_Travertine_Deck", "#E6DCC8", "#DCCFB7", 0.60, 0.40, "#C2B49A", 0.003, 0.6, 0.2, 0.5))
    M["coping"] = mod.simple("T07_Coping_White_Stone", "#EEE8DC", 0.45, 0.0, 12.0, 0.1, 0.1)
    M["soil"] = mod.simple("T08_Planter_Soil", "#6B5240", 0.95, 0.0, 25.0, 0.3, 0.4)
    M["pool_cover"] = mod.simple("T09_Pool_Cover_Blue", "#2C5E8C", 0.5, 0.0, 0.0, 0.0, 0.0)
    M["paint"] = mod.simple("T11_Road_Paint_White", "#E9E7E0", 0.6, 0.0, 40.0, 0.12, 0.1)
    # pool court in the style of the 15-10 reference images
    M["grille"] = uv_tiles(mod.tiles("T12_Overflow_Grille_Black", "#2A2A2C", "#1F1F21", 0.035, 0.035, "#060606", 0.006, 0.45, 0.4, 0.0))
    M["planks"] = uv_tiles(mod.tiles("T13_Travertine_Planks", "#E5D8C0", "#D7C7AA", 0.90, 0.22, "#B9A98E", 0.003, 0.6, 0.2, 0.37), 90.0)
    M["lounger_white"] = mod.simple("T14_Lounger_White_Resin", "#F1EFE9", 0.35, 0.0, 0.0, 0.0, 0.0)
    M["canvas"] = mod.simple("T15_Parasol_Canvas", "#D9C8A9", 0.85, 0.0, 30.0, 0.08, 0.05)
    M["agave"] = mod.simple("V09_Agave_Leaf", "#7E9B8A", 0.55, 0.0, 20.0, 0.12, 0.05)
    # rev 4 (remarks on the D5 model, villa N°09 drawings and reference images)
    # one sand render for every building of the tranche, matched to the client's photos (rev 4, 19-10):
    # the built kasbah tower and the villa renders
    M["villa"] = (mod.ph_surface("D13_Render_Villa_Beige", "white_plaster_rough_01", 2.5, SAND, 0.0, 0.45)
                  or mod.render_plaster("D13_Render_Villa_Beige", "#D2B492", "#BEA07C"))
    M["render"] = mod.ph_surface("M01_Render_Sand", "white_plaster_rough_01", 2.5, SAND, 0.0, 0.45) or M["render"]
    M["surround"] = mod.simple("D14_Stone_Surround_Taupe", "#B09A82", 0.85, 0.0, 45.0, 0.22, 0.35)
    M["ledge"] = mod.simple("D15_Stone_Ledge_Grey", "#BAB4AB", 0.7, 0.0, 25.0, 0.12, 0.1)
    M["band"] = img_mat("D16_Stone_Band_Ochre", "band", 0.55, 0.15)
    M["frame"] = mod.simple("D17_Frame_Cream", "#DDD6CB", 0.4, 0.2)
    M["cladding"] = (mod.ph_surface("D18_Stone_Cladding_Beige", "stacked_stone_wall", 1.8, "#C3B39D", 0.35, 1.0)
                     or mod.stone_wall("D18_Stone_Cladding_Beige"))
    M["coping_beige"] = mod.simple("D19_Coping_Beige_Stone", "#CDBBA6", 0.6, 0.0, 20.0, 0.12, 0.1)
    M["pave_beige"] = img_mat("T17_Pavers_Beige_Herringbone", "pavers", 0.8, 0.35)
    M["pave_side"] = img_mat("T20_Pavers_Sidewalk_Grey", "sidewalk", 0.8, 0.35)
    M["tile_ardesia"] = img_mat("T18_Tile_Ardesia_Beige", "ardesia", 0.55, 0.25)
    M["tile_jade"] = img_mat("T19_Tile_Jade_Green", "jade", 0.35, 0.2)
    M["mod"] = mod
    return M


# ---- geometry --------------------------------------------------------------------------------
def tri_poly(poly):
    """Constrained triangulation of a shapely Polygon (holes respected) -> list of 2D triangles."""
    out = []
    for t in shapely.constrained_delaunay_triangles(poly).geoms:
        c = t.exterior.coords[:3]
        a = (c[1][0] - c[0][0]) * (c[2][1] - c[0][1]) - (c[1][1] - c[0][1]) * (c[2][0] - c[0][0])
        out.append(c if a > 0 else c[::-1])
    return out


def as_polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]


def prism(mb, mat, poly, z0, z1, zf=None, sides=True, bottom=False):
    """Extrude a shapely (Multi)Polygon. zf(x, y) optional height field added to both caps."""
    zf = zf or (lambda x, y: 0.0)
    for pg in as_polys(poly):
        if pg.area < 1e-4:
            continue
        for t in tri_poly(pg):
            mb.poly(mat, [(x, y, z1 + zf(x, y)) for x, y in t], [(x, y) for x, y in t])
            if bottom:
                mb.poly(mat, [(x, y, z0 + zf(x, y)) for x, y in t[::-1]], [(x, y) for x, y in t[::-1]])
        if sides:
            for k, ring in enumerate([pg.exterior] + list(pg.interiors)):
                c = list(ring.coords)
                ccw = ring.is_ccw
                inner = k > 0                     # (pg.exterior is a new object on each access: no `is` test)
                for (ax, ay), (bx, by) in zip(c, c[1:]):
                    if (ccw and not inner) or (not ccw and inner):
                        p, q = (ax, ay), (bx, by)
                    else:
                        p, q = (bx, by), (ax, ay)
                    L = math.dist(p, q)
                    if L < 1e-5:
                        continue
                    za, zb = zf(*p), zf(*q)
                    u0 = 0.0
                    mb.poly(mat, [(p[0], p[1], z0 + za), (q[0], q[1], z0 + zb), (q[0], q[1], z1 + zb), (p[0], p[1], z1 + za)],
                            [(u0, z0), (u0 + L, z0), (u0 + L, z1), (u0, z1)])


def ring_poly(poly, t):
    return poly.difference(poly.buffer(-t, join_style=2))


def quad_x(mb, mat, x0, x1, y, z0, z1, flip=False):
    """Vertical quad in the XZ plane at y (normal -y unless flip)."""
    P = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    U = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    if flip:
        P, U = P[::-1], U[::-1]
    mb.poly(mat, P, U)


def quad_y(mb, mat, x, y0, y1, z0, z1, flip=False):
    P = [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)]
    U = [(y1, z0), (y0, z0), (y0, z1), (y1, z1)]
    if flip:
        P, U = P[::-1], U[::-1]
    mb.poly(mat, P, U)


def join(obs, name):
    obs = [o for o in obs if o is not None]
    if not obs:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    return ob


def boolean(target, cutter, op="DIFFERENCE", solver="EXACT"):
    md = target.modifiers.new("bool", "BOOLEAN")
    md.operation = op
    md.solver = solver
    md.object = cutter
    if solver == "EXACT":
        md.material_mode = "TRANSFER"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=md.name)


def mesh_from_mb(mb, name, col, M):
    obs = mb.build(name, col, M)
    return obs


def weld(ob, dist=0.0005):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
