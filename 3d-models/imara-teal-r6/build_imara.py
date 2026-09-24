"""
Imara Teal R+6 — builds the corner apartment building in Blender and exports GLB.

Run with Blender's Python (bpy 4.2):
    python build_imara.py <output_dir> [--render]

Units are metres. Axes: X runs along the main street (FAÇADE PRINCIPALE),
Y runs back along the side street (FAÇADE LATÉRALE DROITE), Z is up.
Origin = left party-wall corner of the ground floor on the main street.

Measurements come from "PLAN 1er, 2eme, 3eme et 4eme ETAGES" and the two
elevations. Colours and finishes come from the two colour renders.
"""
import math
import os
import random
import sys

import bpy
import numpy as np
from PIL import Image

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "out")
RENDER = "--render" in sys.argv
TEX_DIR = os.path.join(OUT, "textures")
os.makedirs(TEX_DIR, exist_ok=True)
NAME = "Imara_Teal_R6"

# ---------------------------------------------------------------------------
# Dimensions (metres)
# ---------------------------------------------------------------------------
RDC_W, RDC_D = 15.75, 22.50          # ground-floor footprint
ENC = 1.50                           # encorbellement over both streets
TOT_W, TOT_D = RDC_W + ENC, RDC_D + ENC   # 17.25 x 24.00 upper-floor envelope
X_OUT = TOT_W                        # side-street outer face of upper floors
Y_OUT = -ENC                         # main-street outer face of upper floors
H_RDC = 5.50                         # ground floor + mezzanine
H_FL = 3.20                          # floor to floor, étages 1-6
FL = [H_RDC + H_FL * i for i in range(7)]   # 5.5 ... 24.7 (roof)
ROOF = FL[6]
PARAPET = 1.20
TEAL_TOP = ROOF + 1.50               # teal cap and back band
T = 0.25                             # wall thickness
SILL, HEAD = 0.90, 2.25              # windows: sill and head above floor
SLAB = 0.25                          # white balcony slab
TEAL_SLAB = 0.40                     # teal slab / frame board
TEAL_PROJ = 0.60                     # teal projection past the outer face
TEAL_LEVELS = [FL[1], FL[2], FL[4], FL[5]]   # F2, F3 floor edges + F5 frame
FRONT_TEAL_X0 = 5.93                 # teal bands on the main street start here
SIDE_TEAL_Y1 = 13.16                 # ...and end here on the side street

# ---------------------------------------------------------------------------
# Procedural, tileable textures
# ---------------------------------------------------------------------------
RNG = np.random.default_rng(7)
S = 1024


def _noise(cells, size=S):
    g = RNG.random((cells, cells)).astype(np.float32)
    big = Image.fromarray(np.tile(g, (3, 3)), mode="F").resize((size * 3, size * 3), Image.BICUBIC)
    return np.asarray(big)[size:2 * size, size:2 * size]


def fbm(base, octaves=5, size=S):
    acc, amp, tot = np.zeros((size, size), np.float32), 1.0, 0.0
    for o in range(octaves):
        c = base * 2 ** o
        if c > size // 2:
            break
        acc += amp * _noise(c, size)
        tot += amp
        amp *= 0.5
    return acc / tot


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def save(name, rgb):
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB")
    path = os.path.join(TEX_DIR, name + ".jpg")
    img.save(path, quality=90)
    return path


def grid_lines(n_u, n_v, width_px, size=S):
    """1 on joints, 0 elsewhere; n_u vertical joints and n_v horizontal joints per tile."""
    y, x = np.mgrid[0:size, 0:size]
    ju = (x % (size / n_u)) < width_px if n_u else np.zeros_like(x, bool)
    jv = (y % (size / n_v)) < width_px if n_v else np.zeros_like(y, bool)
    return ju | jv


def tex_beige():
    # large-format facade panels (1.50 x 1.60 m), light warm grey
    base = hexrgb("#C3BCB7")
    n = (fbm(8) - 0.5) * 0.05 + (fbm(64, 3) - 0.5) * 0.03
    img = base[None, None, :] + n[..., None]
    j = grid_lines(1, 1, 7)
    img[j] = hexrgb("#85807B")
    return save("beige_panels", img)


def tex_white():
    base = hexrgb("#F1F0EE")
    n = (fbm(16) - 0.5) * 0.03
    return save("white_render", base[None, None, :] + n[..., None])


def tex_teal():
    base = hexrgb("#3E7B8D")
    n = (fbm(12) - 0.5) * 0.035
    return save("teal_paint", base[None, None, :] + n[..., None])


def tex_stone():
    # dark brown-grey stone tiles 1.20 x 0.60 m, running bond, tile = 2.4 x 2.4 m
    y, x = np.mgrid[0:S, 0:S]
    row = (y // (S // 4)).astype(int)
    xs = (x + (row % 2) * (S // 4)) % S
    col = (xs // (S // 2)).astype(int)
    tone = RNG.normal(0, 0.035, (4, 2)).astype(np.float32)
    per_tile = tone[row, col]
    base = hexrgb("#6C635D")
    mott = (fbm(10) - 0.5) * 0.10 + (fbm(90, 3) - 0.5) * 0.08
    speck = (RNG.random((S, S)).astype(np.float32) - 0.5) * 0.05
    img = base[None, None, :] + (mott + speck + per_tile)[..., None]
    img[..., 2] -= 0.01
    joint = ((xs % (S // 2)) < 4) | ((y % (S // 4)) < 4)
    img[joint] = hexrgb("#3B3632")
    return save("stone_brown", img)


def tex_wood():
    # vertical planks 0.12 m, tile = 1.2 x 2.4 m
    y, x = np.mgrid[0:S, 0:S]
    plank = (x * 10 // S).astype(int)
    tone = RNG.normal(0, 0.05, 10).astype(np.float32)[plank]
    warp = fbm(4)
    grain = 0.5 + 0.5 * np.sin(2 * np.pi * (x / S * 90 + warp * 5))
    base = hexrgb("#A26A38")
    img = base[None, None, :] * (0.86 + 0.14 * grain[..., None]) + tone[..., None]
    img += ((fbm(32, 3) - 0.5) * 0.06)[..., None]
    img[(x * 10 % S) < 40] = hexrgb("#4A2E17")
    return save("wood_cladding", img)


def tex_marble():
    # black marble with white veins, 1.20 x 2.40 m slabs, tile = 2.4 x 2.4 m
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    t1 = 2 * np.pi * (2 * x + 1 * y) / S + 7.0 * fbm(3)
    t2 = 2 * np.pi * (1 * x - 3 * y) / S + 9.0 * fbm(5)
    v = np.exp(-np.abs(np.sin(t1)) * 34) * 0.55 + np.exp(-np.abs(np.sin(t2)) * 60) * 0.30
    v *= 0.55 + 0.45 * fbm(6)
    base = hexrgb("#161618")
    vein = hexrgb("#D9D6D0")
    img = base[None, None, :] * (1 - v[..., None]) + vein[None, None, :] * v[..., None]
    img += ((fbm(40, 3) - 0.5) * 0.04)[..., None]
    joint = ((x % (S / 2)) < 3) | (y < 3)
    img[joint] = hexrgb("#0A0A0B")
    return save("marble_black", img)


def tex_shutter():
    # rolling shutter, 10 slats per metre
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    p = (y % (S / 10)) / (S / 10)
    shade = 0.78 + 0.22 * np.sin(np.pi * p)
    base = hexrgb("#B4B6B9")
    img = base[None, None, :] * shade[..., None]
    img[p < 0.06] = hexrgb("#5E6063")
    return save("shutter_metal", img)


def tex_roof():
    base = hexrgb("#BDB7AE")
    n = (fbm(20) - 0.5) * 0.08 + (RNG.random((S, S)).astype(np.float32) - 0.5) * 0.05
    return save("roof_concrete", base[None, None, :] + n[..., None])


def tex_paver():
    base = hexrgb("#C3BFB8")
    img = base[None, None, :] + ((fbm(30) - 0.5) * 0.06)[..., None]
    img[grid_lines(5, 5, 4)] = hexrgb("#8A8680")
    return save("sidewalk_pavers", img)


def tex_asphalt():
    base = hexrgb("#3B3C3F")
    n = (fbm(40) - 0.5) * 0.06 + (RNG.random((S, S)).astype(np.float32) - 0.5) * 0.08
    return save("asphalt", base[None, None, :] + n[..., None])


def tex_party():
    base = hexrgb("#E2DED8")
    return save("party_wall", base[None, None, :] + ((fbm(10) - 0.5) * 0.05)[..., None])


# material key -> (label, texture fn or hex, tile_u, tile_v, off_u, off_v, roughness, metallic, extra)
MAT_DEF = {
    "beige":   ("Facade_Panels_Beige", tex_beige, 1.50, 1.60, 0.0, H_RDC, 0.55, 0.0, {}),
    "white":   ("Render_White", tex_white, 3.0, 3.0, 0, 0, 0.6, 0.0, {}),
    "teal":    ("Teal_Frames", tex_teal, 3.0, 3.0, 0, 0, 0.45, 0.0, {}),
    "stone":   ("Stone_Cladding_Brown", tex_stone, 2.4, 2.4, 0, H_RDC, 0.8, 0.0, {}),
    "wood":    ("Wood_Cladding", tex_wood, 1.2, 2.4, 0, 0, 0.6, 0.0, {}),
    "marble":  ("Marble_Black_RDC", tex_marble, 2.4, 2.4, 0, 0, 0.18, 0.0, {}),
    "shutter": ("Shutters_Metal", tex_shutter, 1.0, 1.0, 0, 0, 0.4, 0.6, {}),
    "roof":    ("Roof_Concrete", tex_roof, 4.0, 4.0, 0, 0, 0.9, 0.0, {}),
    "party":   ("Party_Walls", tex_party, 4.0, 4.0, 0, 0, 0.9, 0.0, {}),
    "paver":   ("Sidewalk", tex_paver, 2.0, 2.0, 0, 0, 0.85, 0.0, {}),
    "asphalt": ("Asphalt", tex_asphalt, 6.0, 6.0, 0, 0, 0.9, 0.0, {}),
    "glass":   ("Window_Glass", "#1D2A3A", 1, 1, 0, 0, 0.04, 0.35, {}),
    "frame":   ("Window_Frames_Black", "#1B1B1D", 1, 1, 0, 0, 0.35, 0.5, {}),
    "rail":    ("Balcony_Glass_Railing", "#8FB9C8", 1, 1, 0, 0, 0.05, 0.0, {"alpha": 0.22}),
    "steel":   ("Railing_Cap_Steel", "#C9CCCF", 1, 1, 0, 0, 0.25, 1.0, {}),
    "light":   ("Downlights", "#FFF4DD", 1, 1, 0, 0, 0.5, 0.0, {"emit": 3.0}),
    "pot":     ("Planters", "#3C3C3F", 1, 1, 0, 0, 0.6, 0.0, {}),
    "leaf":    ("Plants_Green", "#3F7A2E", 1, 1, 0, 0, 0.6, 0.0, {"double": True}),
    "leaf2":   ("Plants_Light", "#6A9B3C", 1, 1, 0, 0, 0.6, 0.0, {"double": True}),
    "door":    ("Doors_Dark", "#2B2622", 1, 1, 0, 0, 0.5, 0.2, {}),
}
SITE_MATS = {"paver", "asphalt"}

# ---------------------------------------------------------------------------
# Geometry accumulators: one mesh per material
# ---------------------------------------------------------------------------
G = {}


def _acc(key, site=False):
    k = (key, site)
    if k not in G:
        G[k] = ([], [], [])
    return G[k]


SITE = [False]


def poly(mat, pts, uvs):
    V, F, U = _acc(mat, SITE[0])
    i = len(V)
    V.extend(pts)
    F.append(tuple(range(i, i + len(pts))))
    U.extend(uvs)


def box(mat, x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
        return
    d = MAT_DEF[mat]
    tu, tv, ou, ov = d[2], d[3], d[4], d[5]

    def uv(u, v):
        return ((u - ou) / tu, (v - ov) / tv)

    poly(mat, [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
         [uv(x0, z0), uv(x1, z0), uv(x1, z1), uv(x0, z1)])
    poly(mat, [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
         [uv(-x1, z0), uv(-x0, z0), uv(-x0, z1), uv(-x1, z1)])
    poly(mat, [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
         [uv(-y1, z0), uv(-y0, z0), uv(-y0, z1), uv(-y1, z1)])
    poly(mat, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
         [uv(y0, z0), uv(y1, z0), uv(y1, z1), uv(y0, z1)])
    poly(mat, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
         [uv(x0, y0), uv(x1, y0), uv(x1, y1), uv(x0, y1)])
    poly(mat, [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
         [uv(x0, y1), uv(x1, y1), uv(x1, y0), uv(x0, y0)])


def pbox(mat, ax, plane, n, ua, ub, da, db, za, zb):
    """Box in facade coordinates: u along the facade, d = depth inward from the
    outer face (negative = in front of it). ax='Y': facade lies in plane Y=plane,
    u is X. ax='X': facade lies in plane X=plane, u is Y. n = outward normal sign."""
    c1, c2 = plane - n * da, plane - n * db
    if ax == "Y":
        box(mat, ua, ub, c1, c2, za, zb)
    else:
        box(mat, c1, c2, ua, ub, za, zb)


def O(u0, u1, z0, z1, kind):
    return dict(u0=u0, u1=u1, z0=z0, z1=z1, kind=kind)


def win(u0, u1, f):
    return O(u0, u1, FL[f - 1] + SILL, FL[f - 1] + HEAD, "win")


def door(u0, u1, f):
    return O(u0, u1, FL[f - 1], FL[f - 1] + HEAD, "door")


def glazing(ax, plane, n, o):
    u0, u1, z0, z1, kind = o["u0"], o["u1"], o["z0"], o["z1"], o["kind"]
    fw = 0.06
    if kind == "shutter":
        pbox("shutter", ax, plane, n, u0, u1, 0.10, 0.14, z0, z1 - 0.35)
        pbox("frame", ax, plane, n, u0, u1, 0.03, 0.14, z1 - 0.35, z1)
        pbox("frame", ax, plane, n, u0, u0 + 0.05, 0.03, 0.14, z0, z1)
        pbox("frame", ax, plane, n, u1 - 0.05, u1, 0.03, 0.14, z0, z1)
        return
    w = u1 - u0
    panes = {"win": max(2, round(w / 1.25)), "door": 2,
             "shop": max(2, round(w / 1.4)), "entrance": 2}[kind]
    # outer frame
    pbox("frame", ax, plane, n, u0, u1, 0.08, 0.16, z0, z0 + fw)
    pbox("frame", ax, plane, n, u0, u1, 0.08, 0.16, z1 - fw, z1)
    pbox("frame", ax, plane, n, u0, u0 + fw, 0.08, 0.16, z0, z1)
    pbox("frame", ax, plane, n, u1 - fw, u1, 0.08, 0.16, z0, z1)
    for i in range(1, panes):
        um = u0 + w * i / panes
        pbox("frame", ax, plane, n, um - fw / 2, um + fw / 2, 0.08, 0.16, z0, z1)
    if kind == "entrance":
        pbox("frame", ax, plane, n, u0, u1, 0.08, 0.16, z0 + 2.40, z0 + 2.40 + fw)
    pbox("glass", ax, plane, n, u0 + fw / 2, u1 - fw / 2, 0.11, 0.13, z0 + fw / 2, z1 - fw / 2)
    if kind == "win":   # projecting stone sill
        pbox("white", ax, plane, n, u0 - 0.05, u1 + 0.05, -0.05, 0.10, z0 - 0.05, z0)


def _subtract(a, b, cuts):
    out = [(a, b)]
    for c0, c1 in cuts:
        nxt = []
        for s0, s1 in out:
            if c1 <= s0 or c0 >= s1:
                nxt.append((s0, s1))
                continue
            if c0 > s0:
                nxt.append((s0, c0))
            if c1 < s1:
                nxt.append((c1, s1))
        out = nxt
    return [(s0, s1) for s0, s1 in out if s1 - s0 > 1e-4]


def wall(mat, ax, plane, n, u0, u1, z0, z1, openings=(), t=T):
    """Wall panel with rectangular openings; reveals come from the split pieces."""
    ops = [o for o in openings]
    cuts = sorted({u0, u1, *[min(max(o["u0"], u0), u1) for o in ops],
                   *[min(max(o["u1"], u0), u1) for o in ops]})
    for ua, ub in zip(cuts[:-1], cuts[1:]):
        cover = [(o["z0"], o["z1"]) for o in ops if o["u0"] <= ua + 1e-6 and o["u1"] >= ub - 1e-6]
        for za, zb in _subtract(z0, z1, cover):
            pbox(mat, ax, plane, n, ua, ub, 0, t, za, zb)
    for o in ops:
        glazing(ax, plane, n, o)


def railing(ax, plane, n, u0, u1, z):
    """Frameless glass balustrade, 1.05 m, with a slim steel cap."""
    pbox("rail", ax, plane, n, u0 + 0.02, u1 - 0.02, 0.06, 0.08, z, z + 1.02)
    pbox("steel", ax, plane, n, u0 + 0.02, u1 - 0.02, 0.05, 0.09, z + 1.02, z + 1.06)
    for u in (u0 + 0.03, u1 - 0.03):
        pbox("steel", ax, plane, n, u - 0.02, u + 0.02, 0.05, 0.09, z, z + 0.08)


def downlight(x, y, z):
    box("light", x - 0.06, x + 0.06, y - 0.06, y + 0.06, z - 0.012, z + 0.002)


PRNG = random.Random(11)


def plant(cx, cy, z, size=1.0, pot=True):
    if pot:
        box("pot", cx - 0.22, cx + 0.22, cy - 0.22, cy + 0.22, z, z + 0.45)
        base = z + 0.42
    else:
        base = z
    n = PRNG.randint(9, 13)
    for i in range(n):
        a = 2 * math.pi * i / n + PRNG.uniform(-0.25, 0.25)
        r = PRNG.uniform(0.35, 0.65) * size
        h = PRNG.uniform(0.55, 1.05) * size
        wd = PRNG.uniform(0.07, 0.11) * size
        ca, sa = math.cos(a), math.sin(a)
        wx, wy = -sa, ca
        b = (cx, cy, base)
        m = (cx + ca * r * 0.55, cy + sa * r * 0.55, base + h * 0.75)
        tip = (cx + ca * r, cy + sa * r, base + h * PRNG.uniform(0.7, 1.0))
        mat = "leaf" if i % 3 else "leaf2"
        poly(mat, [(b[0] - wx * wd * 0.3, b[1] - wy * wd * 0.3, b[2]),
                   (b[0] + wx * wd * 0.3, b[1] + wy * wd * 0.3, b[2]),
                   (m[0] + wx * wd, m[1] + wy * wd, m[2]),
                   (m[0] - wx * wd, m[1] - wy * wd, m[2])],
             [(0, 0), (1, 0), (1, 0.7), (0, 0.7)])
        poly(mat, [(m[0] - wx * wd, m[1] - wy * wd, m[2]),
                   (m[0] + wx * wd, m[1] + wy * wd, m[2]), tip],
             [(0, 0.7), (1, 0.7), (0.5, 1)])


# ---------------------------------------------------------------------------
# Facade finish per floor (from the renders)
# ---------------------------------------------------------------------------
def mat_c(f):   # left front room + zone C on the side street: stone F1-F3, panels F4-F6
    return "stone" if f <= 3 else "beige"


def mat_e(f):   # corner rooms: panels F1-F4, stone inside the teal frame F5, white F6
    return {5: "stone", 6: "white"}.get(f, "beige")


def mat_f(f):   # corner balcony back wall
    return "beige" if f <= 4 else "white"


def teal_at(level):
    return any(abs(level - L) < 1e-6 for L in TEAL_LEVELS)


def balcony_slab(x0, x1, y0, y1, f, teal_zone):
    L = FL[f - 1]
    if teal_zone and teal_at(L):
        return          # the teal band is the slab here
    th = 0.40 if f == 1 else SLAB
    box("white", x0, x1, y0, y1, L - th, L)


def soffit_z(f, teal_zone):
    if f == 6:
        return ROOF - 0.40
    L = FL[f]
    return L - (TEAL_SLAB if teal_zone and teal_at(L) else SLAB)


# ---------------------------------------------------------------------------
# Ground floor (RDC): black marble, shops with shutters + mezzanine glazing
# ---------------------------------------------------------------------------
def build_rdc():
    lo, g0, g1 = 2.90, 3.30, 5.00
    front = [O(0.37, 3.38, 0, 3.90, "shutter"),          # garage
             O(4.00, 6.20, 0, 5.00, "entrance"),         # building entrance
             O(7.25, 10.15, 0, lo, "shutter"), O(7.25, 10.15, g0, g1, "shop"),
             O(11.10, 15.10, 0, lo, "shutter"), O(11.10, 15.10, g0, g1, "shop")]
    wall("marble", "Y", 0.0, -1, 0.0, RDC_W, 0.0, H_RDC, front, t=0.30)
    side = []
    for a, b in [(0.66, 5.57), (6.29, 10.73), (13.60, 16.97), (17.80, 21.76)]:
        side += [O(a, b, 0, lo, "shutter"), O(a, b, g0, g1, "shop")]
    wall("marble", "X", RDC_W, +1, 0.0, RDC_D, 0.0, H_RDC, side, t=0.30)
    wall("party", "X", 0.0, -1, 0.0, RDC_D, 0.0, H_RDC)
    wall("party", "Y", RDC_D, +1, 0.0, RDC_W, 0.0, H_RDC)
    box("white", 0.0, RDC_W, 0.0, RDC_D, H_RDC - 0.20, H_RDC)       # RDC roof slab
    box("roof", 0.25, 5.58, 16.60, RDC_D - 0.25, H_RDC, H_RDC + 0.02)  # court floor (1er étage)
    # door leaf inside the entrance and floor mat of the lobby
    pbox("door", "Y", 0.0, -1, 4.55, 5.65, 0.12, 0.14, 0.0, 2.35)
    # downlights under the overhangs
    for x in np.arange(3.0, RDC_W + 0.5, 2.6):
        downlight(float(x), -0.75, H_RDC - 0.40)
    for y in np.arange(0.9, RDC_D - 1.0, 2.6):
        downlight(X_OUT - 0.75, float(y), H_RDC - 0.40)


# ---------------------------------------------------------------------------
# Typical floors 1-6
# ---------------------------------------------------------------------------
def build_floor(f):
    z0, z1 = FL[f - 1], FL[f]

    # --- MAIN STREET (outer face Y = -1.50, main line Y = 0) -----------------
    # a. pier by the left party wall + b. loggia (balcon 1.90)
    box(mat_c(f), 0.0, 0.90, 0.0, 1.60, z0, z1)
    wall("white", "Y", 1.60, -1, 0.90, 2.02, z0, z1, [door(1.05, 1.87, f)])
    wall("white", "X", 2.02, -1, 0.0, 1.60, z0, z1)
    balcony_slab(0.90, 2.02, -0.05, 1.60, f, False)
    railing("Y", 0.0, -1, 0.90, 2.02, z0)

    # c. bedroom in encorbellement, X 2.02-6.33 (window 2.50)
    wall(mat_c(f), "Y", Y_OUT, -1, 2.02, 6.33, z0, z1, [win(2.92, 5.42, f)])
    wall(mat_c(f), "X", 2.02, -1, Y_OUT + T, 0.0, z0, z1)
    wall(mat_c(f), "X", 6.33, +1, Y_OUT + T, 0.0, z0, z1)

    # d. balcony 4.18 (salon + SAM), wood-clad back wall with two sliding doors
    wall("wood", "Y", 0.0, -1, 6.33, 10.51, z0, z1, [door(6.60, 8.10, f), door(8.80, 10.30, f)])
    balcony_slab(6.33, 10.51, Y_OUT - 0.05, 0.0, f, True)
    railing("Y", Y_OUT, -1, 6.33, 10.51, z0)

    # e. bedroom in encorbellement, X 10.51-13.96 (window 2.50)
    wall(mat_e(f), "Y", Y_OUT, -1, 10.51, 13.96, z0, z1, [win(10.96, 13.46, f)])
    wall(mat_e(f), "X", 10.51, -1, Y_OUT + T, 0.0, z0, z1)
    wall(mat_e(f), "X", 13.96, +1, Y_OUT + T, 0.0, z0, z1)

    # f. corner balcony X 13.96-17.25
    wall(mat_f(f), "Y", 0.0, -1, 13.96, RDC_W, z0, z1, [door(14.20, 15.50, f)])
    wall(mat_e(f), "Y", 0.0, -1, RDC_W, X_OUT - T, z0, z1, [door(15.95, 16.85, f)])
    balcony_slab(13.96, X_OUT + 0.05, Y_OUT - 0.05, 0.0, f, True)
    railing("Y", Y_OUT, -1, 13.96, X_OUT, z0)
    railing("X", X_OUT, +1, Y_OUT, 0.0, z0)

    # --- SIDE STREET (outer face X = 17.25, main line X = 15.75) -------------
    # A. two bedrooms in encorbellement, Y 0-7.02
    wall(mat_e(f), "X", X_OUT, +1, 0.0, 7.02, z0, z1, [win(0.50, 3.00, f), win(3.84, 6.34, f)])
    wall(mat_e(f), "Y", 7.02, +1, RDC_W, X_OUT - T, z0, z1)
    # B. balcony 1.90 in front of kitchen / SAM, wood-clad, Y 7.02-12.76
    wall("wood", "X", RDC_W, +1, 7.02, 12.76, z0, z1, [door(7.50, 9.00, f), door(10.00, 12.30, f)])
    balcony_slab(RDC_W, X_OUT + 0.05, 7.02, 12.76, f, True)
    railing("X", X_OUT, +1, 7.02, 12.76, z0)
    # C. salon marocain in encorbellement, Y 12.76-16.26 (window 2.50)
    wall(mat_c(f), "X", X_OUT, +1, 12.76, 16.26, z0, z1, [win(13.26, 15.76, f)])
    wall(mat_c(f), "Y", 12.76, -1, RDC_W, X_OUT - T, z0, z1)
    wall(mat_c(f), "Y", 16.26, +1, RDC_W, X_OUT - T, z0, z1)
    # D. bedroom balconies (balcon 1.40), Y 16.26-21.50
    wall("white", "X", RDC_W, +1, 16.26, 21.50, z0, z1, [door(16.90, 18.90, f), door(19.50, 21.20, f)])
    balcony_slab(RDC_W, X_OUT + 0.05, 16.26, 21.50, f, False)
    railing("X", X_OUT, +1, 16.26, 21.50, z0)

    # --- COURTYARD (cour au 1er étage, vide sur cour 2-6) ---------------------
    wall("white", "X", 5.58, -1, 16.60, RDC_D - T, z0, z1, [win(17.30, 18.80, f), win(19.80, 21.30, f)])
    wall("white", "Y", 16.60, +1, T, 5.58 + T, z0, z1, [win(1.00, 2.60, f)])

    # --- plants and downlights on the balconies -----------------------------
    zt = soffit_z(f, True)
    zw = soffit_z(f, False)
    for x in (7.40, 9.45):
        downlight(x, -0.75, zt)
    for x in (14.90, 16.40):
        downlight(x, -0.75, zt)
    for y in (8.40, 11.30):
        downlight(16.50, y, zt)
    for y in (17.60, 20.20):
        downlight(16.50, y, zw)
    plant(6.75, -1.10, z0, 0.9)
    plant(16.85, -1.10, z0, 1.0)
    plant(16.85, 12.35, z0, 0.9)
    plant(16.85, 21.05, z0, 1.0)
    if f % 2:
        plant(16.85, 16.70, z0, 0.8)
        plant(10.05, -1.10, z0, 0.8)


# ---------------------------------------------------------------------------
# Teal bands, F5 frame, fins, back band, roof
# ---------------------------------------------------------------------------
def build_teal():
    xo, yo = X_OUT + TEAL_PROJ, Y_OUT - TEAL_PROJ
    for L in TEAL_LEVELS:
        box("teal", FRONT_TEAL_X0, xo, yo, 0.0, L - TEAL_SLAB, L)
        box("teal", RDC_W, xo, 0.0, SIDE_TEAL_Y1, L - TEAL_SLAB, L)
        # downlights on the projecting teal soffit
        for x in np.arange(6.8, X_OUT + 0.2, 2.6):
            downlight(float(x), Y_OUT - TEAL_PROJ / 2, L - TEAL_SLAB)
        for y in np.arange(0.8, SIDE_TEAL_Y1 - 0.3, 2.6):
            downlight(X_OUT + TEAL_PROJ / 2, float(y), L - TEAL_SLAB)
    # F5 frame end plates
    zb, zt = FL[4], FL[5] - TEAL_SLAB
    box("teal", FRONT_TEAL_X0, FRONT_TEAL_X0 + 0.40, yo, Y_OUT, zb, zt)
    box("teal", X_OUT, xo, SIDE_TEAL_Y1 - 0.40, SIDE_TEAL_Y1, zb, zt)
    # back band on the side street (party-wall end), full height up to the cap
    box("teal", RDC_W, X_OUT + 0.20, 21.50, RDC_D, H_RDC - 0.40, TEAL_TOP)
    # cap along the side-street roof edge
    box("teal", X_OUT - 0.40, X_OUT + 0.20, Y_OUT - 0.05, 21.50, ROOF, TEAL_TOP)


def fins(ax, plane, n, u0, count, z0, z1):
    """White vertical fins (brise-soleil) standing on the outer face line."""
    for i in range(count):
        u = u0 + i * 0.16
        pbox("white", ax, plane, n, u, u + 0.08, -0.05, 0.25, z0, z1)


def build_fins():
    zf0, zf1 = FL[2], FL[4] - TEAL_SLAB          # F3-F4 between the teal bands
    fins("Y", Y_OUT, -1, 9.95, 4, zf0, zf1)
    fins("X", X_OUT, +1, 7.10, 4, zf0, zf1)
    zg0, zg1 = FL[4], FL[5] - TEAL_SLAB          # inside the F5 frame
    fins("Y", Y_OUT, -1, 6.40, 4, zg0, zg1)
    fins("X", X_OUT, +1, 12.20, 4, zg0, zg1)


def build_roof():
    e = 0.05
    rects = [(2.02, X_OUT + e, Y_OUT - e, 0.0),
             (0.0, X_OUT + e, 0.0, 16.60),
             (5.58, X_OUT + e, 16.60, RDC_D)]
    for x0, x1, y0, y1 in rects:
        box("white", x0, x1, y0, y1, ROOF - 0.40, ROOF)
        box("roof", x0 + 0.1, x1 - 0.3, y0 + 0.1, y1 - 0.1, ROOF, ROOF + 0.02)
    top = ROOF + PARAPET
    box("white", 2.02, X_OUT - 0.40, Y_OUT - e, Y_OUT + 0.20, ROOF, top)
    box("white", 2.02, 2.22, Y_OUT, 0.0, ROOF, top)
    box("white", 0.0, 2.02, 0.0, 0.20, ROOF, top)
    box("white", 0.0, 0.20, 0.0, 16.60, ROOF, top)
    box("white", 0.0, 5.58, 16.60, 16.80, ROOF, top)
    box("white", 5.58, 5.78, 16.60, RDC_D, ROOF, top)
    box("white", 5.58, RDC_W, RDC_D - 0.20, RDC_D, ROOF, top)
    # stair house (cage d'escalier) — plan X 3.60-6.80, Y 11.20-16.60
    box("white", 3.60, 6.80, 11.20, 16.60, ROOF, ROOF + 2.60)
    box("white", 3.50, 6.90, 11.10, 16.70, ROOF + 2.60, ROOF + 2.75)
    box("door", 6.80, 6.84, 13.40, 14.40, ROOF + 0.02, ROOF + 2.20)
    # rooftop planters seen in the renders
    for x0, x1 in [(2.40, 5.80), (10.80, 13.60)]:
        box("white", x0, x1, Y_OUT + 0.30, Y_OUT + 1.00, ROOF, ROOF + 0.60)
        for x in np.arange(x0 + 0.45, x1 - 0.2, 0.75):
            plant(float(x), Y_OUT + 0.65, ROOF + 0.55, 1.5, pot=False)


def build_site():
    SITE[0] = True
    box("paver", -4.0, X_OUT + 4.5, -4.0, 0.0, -0.15, 0.0)
    box("paver", RDC_W, X_OUT + 4.5, 0.0, RDC_D + 4.0, -0.15, 0.0)
    box("asphalt", -30.0, 50.0, -16.0, -4.0, -0.30, -0.15)
    box("asphalt", X_OUT + 4.5, 32.0, -4.0, 45.0, -0.30, -0.15)
    box("asphalt", -150.0, 150.0, -150.0, 150.0, -0.40, -0.31)
    box("party", -14.0, 0.0, 0.0, RDC_D, 0.0, 19.5)          # neighbours (render context)
    box("party", -2.0, RDC_W, RDC_D, RDC_D + 12.0, 0.0, 23.0)
    SITE[0] = False


# ---------------------------------------------------------------------------
# Materials and Blender objects
# ---------------------------------------------------------------------------
def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def make_material(key):
    label, src, _, _, _, _, rough, metal, extra = MAT_DEF[key]
    m = bpy.data.materials.new(label)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if callable(src):
        path = src()
        img = bpy.data.images.load(path)
        img.pack()
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = img
        tn.location = (-400, 250)
        nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        rgb = [srgb_to_lin(float(v)) for v in hexrgb(src)]
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        m.diffuse_color = (*rgb, 1.0)
    if "alpha" in extra:
        bsdf.inputs["Alpha"].default_value = extra["alpha"]
        for attr, val in (("blend_method", "BLEND"), ("surface_render_method", "BLENDED")):
            try:
                setattr(m, attr, val)
            except (AttributeError, TypeError):
                pass
    if "emit" in extra:
        rgb = [srgb_to_lin(float(v)) for v in hexrgb(src)]
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Emission Strength"].default_value = extra["emit"]
    m.use_backface_culling = not (extra.get("double") or "alpha" in extra)
    return m


def build_objects():
    root = bpy.data.objects.new(NAME, None)
    bpy.context.scene.collection.objects.link(root)
    site_col = bpy.data.collections.new("Site_Context")
    bpy.context.scene.collection.children.link(site_col)
    mats = {}
    building = []
    for (key, site), (V, F, U) in sorted(G.items()):
        if key not in mats:
            mats[key] = make_material(key)
        label = MAT_DEF[key][0]
        me = bpy.data.meshes.new(("Site_" if site else "Imara_") + label)
        me.from_pydata(V, [], F)
        uvl = me.uv_layers.new(name="UVMap")
        for poly_ in me.polygons:
            for li in poly_.loop_indices:
                uvl.data[li].uv = U[me.loops[li].vertex_index]
        me.materials.append(mats[key])
        me.validate()
        me.update()
        ob = bpy.data.objects.new(me.name, me)
        if site:
            site_col.objects.link(ob)
        else:
            bpy.context.scene.collection.objects.link(ob)
            ob.parent = root
            building.append(ob)
    return root, building


# ---------------------------------------------------------------------------
# Preview renders (Cycles, CPU)
# ---------------------------------------------------------------------------
def look_at(ob, target):
    from mathutils import Vector
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("Sky")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(38)
    sky.sun_rotation = math.radians(200)
    sky.sun_intensity = 0.35
    nt.links.new(sky.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    nt.nodes["Background"].inputs["Strength"].default_value = 0.35
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 2.6
    sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (math.radians(50), 0, math.radians(35))
    sc.collection.objects.link(so)


def render_view(name, loc, target, lens=None, ortho=None, res=(1100, 1300)):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new("Cam_" + name)
    ob = bpy.data.objects.new("Cam_" + name, cam)
    sc.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    if ortho:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho
    else:
        cam.lens = lens
        cam.sensor_width = 36
    cam.clip_end = 500
    sc.camera = ob
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 90
    sc.render.filepath = os.path.join(OUT, "previews", name + ".jpg")
    bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_rdc()
    for f in range(1, 7):
        build_floor(f)
    build_teal()
    build_fins()
    build_roof()
    build_site()
    root, building = build_objects()

    blend_path = os.path.join(OUT, NAME + ".blend")
    glb_path = os.path.join(OUT, NAME + ".glb")

    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for ob in building:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format="GLB", use_selection=True,
                              export_image_format="JPEG", export_jpeg_quality=88,
                              export_yup=True, export_apply=True)

    if RENDER:
        os.makedirs(os.path.join(OUT, "previews"), exist_ok=True)
        setup_render()
        render_view("corner_view", (31.0, -22.0, 1.7), (11.0, 4.0, 14.0), lens=22)
        render_view("side_street_view", (40.0, -6.0, 1.7), (15.5, 10.5, 14.0), lens=22)
        render_view("elevation_principale", (8.625, -60.0, 13.1), (8.625, 0.0, 13.1),
                    ortho=30.0, res=(1000, 1100))
        render_view("elevation_laterale_droite", (70.0, 11.25, 13.1), (0.0, 11.25, 13.1),
                    ortho=30.0, res=(1100, 1100))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, compress=True)
    if os.path.exists(blend_path + "1"):
        os.remove(blend_path + "1")
    print("SAVED", glb_path, blend_path)


main()
