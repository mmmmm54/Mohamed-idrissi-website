"""
09_build_landscape — vegetation (procedural, APPROXIMATED), private gardens, pools, hedges.

Species follow the site photos (F04, F07: Washingtonia fan palms, lawn, hedges, ornamental
grass) and the renders (date palms, olives). Native context outside the plot: sparse argan /
euphorbia scrub (INFERRED: Souss-Massa coast). No CC0 vegetation could be downloaded (network
policy), so every plant is a procedural mesh with controlled variation. Seeds are fixed, so
the layout is the same on every rebuild.
"""
import math
import random

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep

C = globals()["C"]
D = C.D
RNG = random.Random(20261001)
SRC = {}


# ---------------------------------------------------------------------------
# Plant generators (local coords, base at origin)
# ---------------------------------------------------------------------------
def washingtonia(seed, height):
    r = random.Random(seed)
    mb = C.MeshBuilder()
    segs, rings = 10, 16
    bend = r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25)
    pts = []
    for j in range(rings + 1):
        t = j / rings
        z = t * height
        cx, cy = bend[0] * math.sin(t * math.pi * 0.8) * height * 0.12, bend[1] * math.sin(t * math.pi * 0.8) * height * 0.12
        rad = 0.42 - 0.17 * t + (0.08 if j == 0 else 0)
        pts.append([(cx + rad * math.cos(2 * math.pi * i / segs), cy + rad * math.sin(2 * math.pi * i / segs), z) for i in range(segs)])
    for j in range(rings):
        for i in range(segs):
            a, b = pts[j][i], pts[j][(i + 1) % segs]
            c, d = pts[j + 1][(i + 1) % segs], pts[j + 1][i]
            mb.poly("palm_trunk", [a, b, c, d], [(i / segs, a[2] / 2), ((i + 1) / segs, b[2] / 2), ((i + 1) / segs, c[2] / 2), (i / segs, d[2] / 2)])
    top = np.array([sum(p[0] for p in pts[-1]) / segs, sum(p[1] for p in pts[-1]) / segs, height])
    # short petticoat of dead fronds
    for i in range(14):
        a = 2 * math.pi * i / 14 + r.uniform(-0.1, 0.1)
        ca, sa = math.cos(a), math.sin(a)
        p0 = top + np.array([ca * 0.25, sa * 0.25, -0.2])
        p1 = top + np.array([ca * 0.55, sa * 0.55, -1.3 - r.uniform(0, 0.5)])
        w = np.array([-sa, ca, 0]) * 0.28
        mb.poly("palm_skirt", [tuple(p0 - w), tuple(p0 + w), tuple(p1 + w * 1.3), tuple(p1 - w * 1.3)])
    # crown of fan leaves: pleated half-disc meshes carrying the generated fan texture
    nleaf = r.randint(20, 26)
    for i in range(nleaf):
        az = 2 * math.pi * i / nleaf + r.uniform(-0.15, 0.15)
        el = math.radians(r.uniform(-30, 60))
        d = np.array([math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)])
        side = np.array([-math.sin(az), math.cos(az), 0.0])
        up = np.cross(side, d)
        L = r.uniform(1.0, 1.6)
        tip = top + d * L
        mb.poly("palm_trunk", [tuple(top - side * 0.035), tuple(top + side * 0.035), tuple(tip + side * 0.03), tuple(tip - side * 0.03)])
        R = r.uniform(1.0, 1.35)
        NA, radii = 24, (0.03, 0.3, 0.55, 0.8, 1.0)
        grid = []
        for ia in range(NA + 1):
            phi = math.pi * ia / NA
            row = []
            for t in radii:
                pl = (0.04 if ia % 2 else -0.04) * min(1.0, t * 2)
                v = tip + R * t * (d * math.sin(phi) - side * math.cos(phi)) + up * pl
                v = v - np.array([0, 0, 0.5 * R * t ** 2 * (0.5 + 0.7 * abs(math.cos(phi)))])
                rho = t * 0.48 * 1024
                uv = (0.5 - math.cos(phi) * rho / 1024, (20 + math.sin(phi) * rho) / 552)
                row.append((tuple(v), uv))
            grid.append(row)
        for ia in range(NA):
            for ir in range(len(radii) - 1):
                q = [grid[ia][ir], grid[ia + 1][ir], grid[ia + 1][ir + 1], grid[ia][ir + 1]]
                mb.poly("palm_fan", [p for p, _ in q], [u for _, u in q])
    return mb


def date_palm(seed, height):
    r = random.Random(seed)
    mb = C.MeshBuilder()
    segs, rings = 10, 12
    pts = []
    for j in range(rings + 1):
        t = j / rings
        rad = 0.38 - 0.06 * t
        z = t * height
        pts.append([(rad * math.cos(2 * math.pi * i / segs), rad * math.sin(2 * math.pi * i / segs), z) for i in range(segs)])
    for j in range(rings):
        for i in range(segs):
            mb.poly("palm_trunk", [pts[j][i], pts[j][(i + 1) % segs], pts[j + 1][(i + 1) % segs], pts[j + 1][i]])
    top = np.array([0, 0, height])
    nf = r.randint(22, 30)
    for i in range(nf):
        az = 2 * math.pi * i / nf + r.uniform(-0.12, 0.12)
        el = math.radians(r.uniform(-20, 60))
        L = r.uniform(2.6, 3.6)
        hdir = np.array([math.cos(az), math.sin(az), 0.0])
        side = np.array([-math.sin(az), math.cos(az), 0.0])
        def rach(t):
            return top + hdir * (L * t * math.cos(el)) + np.array([0, 0, L * t * math.sin(el) - 1.3 * (t ** 2) * L * 0.45])
        steps = 18
        for s in range(steps):
            t0, t1 = s / steps, (s + 1) / steps
            a, b = rach(t0), rach(t1)
            mb.poly("palm_trunk", [tuple(a - side * 0.025), tuple(a + side * 0.025), tuple(b + side * 0.025), tuple(b - side * 0.025)])
            if s > 2:
                ll = 0.55 * (1 - t0 * 0.6)
                fwd = (b - a) / (np.linalg.norm(b - a) + 1e-9)
                for sg in (-1, 1):
                    q = a + side * sg * ll + fwd * 0.25 + np.array([0, 0, -0.08])
                    mb.poly("palm_leaf", [tuple(a), tuple(a + fwd * 0.05), tuple(q + fwd * 0.03), tuple(q)])
    return mb


def blob_tree(seed, height, crown, mat, trunk_mat="palm_trunk", lobes=5, cards=170, card_scale=1.0):
    """Olive / argan: forked trunk + crown of leaf-cluster cards (generated olive texture)."""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    th = height * 0.45
    for k in range(3):
        a = 2 * math.pi * k / 3 + r.uniform(-0.3, 0.3)
        lean = np.array([math.cos(a), math.sin(a), 0]) * crown * 0.18
        for s in range(5):
            t0, t1 = s / 5, (s + 1) / 5
            p0 = lean * t0 ** 1.5 + np.array([0, 0, t0 * (th + 0.4)])
            p1 = lean * t1 ** 1.5 + np.array([0, 0, t1 * (th + 0.4)])
            w = 0.11 * (1 - 0.5 * t0)
            mb.box(trunk_mat, min(p0[0], p1[0]) - w, max(p0[0], p1[0]) + w, min(p0[1], p1[1]) - w, max(p0[1], p1[1]) + w, p0[2], p1[2])
    centre = np.array([0, 0, th + crown * 0.42])
    for c in range(cards):
        u = np.array([r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1)])
        u /= np.linalg.norm(u) + 1e-9
        rad = crown * 0.5 * r.uniform(0.45, 1.0) ** 0.5
        p = centre + u * np.array([rad, rad, rad * 0.62])
        nrm = np.array([r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1) + 0.8])
        nrm /= np.linalg.norm(nrm)
        a1 = np.cross(nrm, [0, 0, 1.0]) if abs(nrm[2]) < 0.95 else np.array([1.0, 0, 0])
        a1 /= np.linalg.norm(a1)
        a2 = np.cross(nrm, a1)
        s_ = crown * r.uniform(0.17, 0.26) * card_scale
        q = [p - a1 * s_ - a2 * s_, p + a1 * s_ - a2 * s_, p + a1 * s_ + a2 * s_, p - a1 * s_ + a2 * s_]
        mb.poly(mat, [tuple(v) for v in q], [(0, 0), (1, 0), (1, 1), (0, 1)])
    return mb
    # icosphere
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    Fc = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
          (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    V = [np.array(v) / np.linalg.norm(v) for v in V]
    # one subdivision
    cache = {}
    F2 = []
    def mid(i, j):
        key = tuple(sorted((i, j)))
        if key not in cache:
            m = (V[i] + V[j]) / 2
            V.append(m / np.linalg.norm(m))
            cache[key] = len(V) - 1
        return cache[key]
    for a, b, c in Fc:
        ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
        F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
    for l in range(0):
        cx = r.uniform(-crown * 0.35, crown * 0.35)
        cy = r.uniform(-crown * 0.35, crown * 0.35)
        cz = th + crown * 0.4 + r.uniform(-0.2, 0.5) * crown * 0.4
        rr = crown * r.uniform(0.35, 0.55)
        jit = [rr * (1 + r.uniform(-0.18, 0.18)) for _ in V]
        P = [(cx + v[0] * j, cy + v[1] * j, cz + v[2] * j * 0.75) for v, j in zip(V, jit)]
        for f in F2:
            mb.poly(mat, [P[f[0]], P[f[1]], P[f[2]]])
    return mb


def grass_clump(seed):
    r = random.Random(seed)
    mb = C.MeshBuilder()
    for i in range(26):
        a = r.uniform(0, 2 * math.pi)
        lean = r.uniform(0.15, 0.5)
        h = r.uniform(0.55, 0.95)
        d = np.array([math.cos(a), math.sin(a), 0])
        s = np.array([-math.sin(a), math.cos(a), 0]) * 0.012
        b = d * 0.05
        t = d * lean * h + np.array([0, 0, h])
        mb.poly("grass_orn", [tuple(b - s), tuple(b + s), tuple(t)])
    return mb


def make_source(name, mb, materials, src_col):
    obs = mb.build("SRC_" + name, src_col, materials)
    import bpy
    if len(obs) == 1:
        return obs[0]
    # join parts into one object so instances stay single objects
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "SRC_" + name
    return ob


def instance(src, name, xy, z, rot, scale, col):
    import bpy
    C.remove_object(name)
    ob = bpy.data.objects.new(name, src.data)
    ob.location = (float(xy[0]), float(xy[1]), float(z))
    ob.rotation_euler = (0, 0, rot)
    ob.scale = (scale, scale, scale)
    col.objects.link(ob)
    return ob


# ---------------------------------------------------------------------------
def lot_list():
    lots = []
    for tr, ty, cols, rows in D.LOT_GRIDS:
        for (x0, x1) in cols:
            for (y0, y1) in rows:
                lots.append((ty, x0, x1, y0, y1))
    for (x0, x1), (y0, y1) in D.VILLA_A_LOTS:
        lots.append(("A", x0, x1, y0, y1))
    return lots


def build(materials):
    import bpy
    M = materials
    G = C.SITE_GRADED
    draped = C.DRAPED
    yaw = C.yaw()
    col = C.collection("07_LANDSCAPE")
    src_col = C.child_collection("07_LANDSCAPE", "SRC_VEGETATION")
    src = {
        "wash_a": make_source("WASHINGTONIA_A", washingtonia(1, 10.0), M, src_col),
        "wash_b": make_source("WASHINGTONIA_B", washingtonia(2, 12.5), M, src_col),
        "wash_c": make_source("WASHINGTONIA_C", washingtonia(3, 8.0), M, src_col),
        "date_a": make_source("DATE_PALM_A", date_palm(4, 5.5), M, src_col),
        "date_b": make_source("DATE_PALM_B", date_palm(5, 7.0), M, src_col),
        "olive": make_source("OLIVE_A", blob_tree(6, 4.2, 3.6, "olive_leaf"), M, src_col),
        "argan": make_source("ARGAN_SCRUB_A", blob_tree(7, 2.4, 3.2, "olive_leaf", cards=60), M, src_col),
        "grass": make_source("GRASS_PENNISETUM_A", grass_clump(8), M, src_col),
        "pink": make_source("PINK_BLOSSOM_TREE_A", blob_tree(9, 4.4, 3.0, "blossom", cards=380, card_scale=0.55), M, src_col),
        "pink_s": make_source("PINK_BLOSSOM_TREE_B", blob_tree(10, 3.2, 2.3, "blossom", cards=260, card_scale=0.55), M, src_col),
        # green shade trees (client 2026-10-02: not every flowering tree pink, some green)
        "green": make_source("GREEN_SHADE_TREE_A", blob_tree(11, 4.8, 3.4, "green_leaf", cards=400, card_scale=0.55), M, src_col),
        "green_s": make_source("GREEN_SHADE_TREE_B", blob_tree(12, 3.4, 2.5, "green_leaf", cards=280, card_scale=0.55), M, src_col),
    }
    for ob in src.values():
        ob.hide_render = True
        ob.hide_viewport = True
    global SRC
    SRC = src                                    # reused by build_parking (island and mall trees)
    trees = C.child_collection("07_LANDSCAPE", "TREES")
    gardens = C.child_collection("07_LANDSCAPE", "GARDENS")
    n = {"palms": 0, "olives": 0, "scrub": 0, "grass": 0, "hedge_m": 0.0, "pools": 0}
    occupied = []

    def plant(key, xy, scale=1.0, base_lift=0.18, rot=None):
        z = float(G(np.array([xy]))[0]) + base_lift
        nm = f"VEG_{key.upper()}_{len(occupied):04d}"
        instance(src[key], nm, xy, z, RNG.uniform(0, 2 * math.pi) if rot is None else rot, scale, trees)
        occupied.append(xy)

    hedge = C.MeshBuilder()
    C.GRASS_BLOCKERS = [C.LAKE_POLY.buffer(1.5)] + [p.buffer(4.2) for p in C.CLUB_POOLS]

    def prism(mat, a, b, half_w, z0, zt):
        dvec = (b - a) / (np.linalg.norm(b - a) + 1e-9)
        nvec = np.array([-dvec[1], dvec[0]]) * half_w
        quad = [a - nvec, b - nvec, b + nvec, a + nvec]
        for j in range(4):
            q0, q1 = quad[j], quad[(j + 1) % 4]
            hedge.poly(mat, [(q0[0], q0[1], z0), (q1[0], q1[1], z0), (q1[0], q1[1], zt), (q0[0], q0[1], zt)])
        hedge.poly(mat, [(q[0], q[1], zt) for q in quad])

    def hedge_line(p0, p1, h=1.15, t=0.35):
        """Garden boundary: coursed rubble-stone wall with square stone piers and a render cap
        (as-built site photo of the villas, 2026-10-01). Name kept for continuity."""
        p0, p1 = np.array(p0), np.array(p1)
        L = np.linalg.norm(p1 - p0)
        if L < 0.5:
            return
        dvec = (p1 - p0) / L
        k = max(1, int(L / 3.0))
        for i in range(k):
            a = p0 + dvec * L * i / k
            b = p0 + dvec * L * (i + 1) / k
            z0 = float(G(np.array([(a + b) / 2]))[0]) + 0.10
            prism("stone", a, b, t / 2, z0 - 0.4, z0 + h)
            prism("render", a, b, t / 2 + 0.03, z0 + h, z0 + h + 0.06)
        npier = max(1, int(L / 4.0))
        for i in range(npier + 1):
            c = p0 + dvec * L * i / npier
            z0 = float(G(np.array([c]))[0]) + 0.10
            prism("stone", c - dvec * 0.24, c + dvec * 0.24, 0.24, z0 - 0.4, z0 + h + 0.25)
            prism("render", c - dvec * 0.28, c + dvec * 0.28, 0.28, z0 + h + 0.25, z0 + h + 0.33)
        n["hedge_m"] += L

    # villa lots: hedges, pool + coping, terrace, palms
    m = D.M_PER_PX
    for idx, (ty, x0, x1, y0, y1) in enumerate(lot_list()):
        corners = C.plan_to_world([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        inset = 0.4 / m
        c2 = C.plan_to_world([(x0 + inset, y0 + inset), (x1 - inset, y0 + inset), (x1 - inset, y1 - inset), (x0 + inset, y1 - inset)])
        for a, b in ((0, 1), (2, 3), (3, 0)):
            hedge_line(c2[a], c2[b])
        # street (east) side: gap for the gate in the middle
        mid1 = c2[1] + (c2[2] - c2[1]) * 0.42
        mid2 = c2[1] + (c2[2] - c2[1]) * 0.58
        hedge_line(c2[1], mid1)
        hedge_line(mid2, c2[2])
        pw, pl = {"B": (4.0, 9.0), "C": (3.6, 7.0), "A": (3.4, 15.0)}[ty]
        px0 = x0 + 1.4 / m
        cy = (y0 + y1) / 2
        pool = Polygon(C.plan_to_world([(px0, cy - pl / 2 / m), (px0 + pw / m, cy - pl / 2 / m),
                                        (px0 + pw / m, cy + pl / 2 / m), (px0, cy + pl / 2 / m)]))
        draped(f"LOT_{idx:03d}_PoolDeck", pool.buffer(1.0, join_style=2).difference(pool), gardens, M["terrace"], 0.24, M["kerb"], 0.17, step=1.5)
        C.GRASS_BLOCKERS.append(pool.buffer(1.1, join_style=2))
        draped(f"LOT_{idx:03d}_PoolWater", pool, gardens, M["pool_water"], 0.21, M["pool_tile"], -1.3, step=1.5)
        n["pools"] += 1
        house_d = {"B": 8.6, "C": 11.6, "A": 13.4}[ty]
        house_w = {"B": 11.0, "C": 12.4, "A": 16.4}[ty]
        hx1 = x1 - 1.6 / m - house_d / m
        terr = Polygon(C.plan_to_world([(hx1 - 3.0 / m, cy - house_w / 2 / m), (hx1, cy - house_w / 2 / m),
                                        (hx1, cy + house_w / 2 / m), (hx1 - 3.0 / m, cy + house_w / 2 / m)]))
        C.GRASS_BLOCKERS.append(terr.buffer(0.1))
        hb = Polygon(C.plan_to_world([(hx1, cy - house_w / 2 / m), (x1 - 1.6 / m, cy - house_w / 2 / m), (x1 - 1.6 / m, cy + house_w / 2 / m), (hx1, cy + house_w / 2 / m)]))
        C.GRASS_BLOCKERS.append(hb.buffer(0.2))
        draped(f"LOT_{idx:03d}_Terrace", terr, gardens, M["terrace"], 0.22, M["kerb"], 0.17, step=1.5)
        # palms at two lot corners (garden side), grasses along the pool
        for (u, v, key) in ((x0 + 1.2 / m, y0 + 1.3 / m, "wash_a"), (x0 + 1.2 / m, y1 - 1.3 / m, "wash_c")):
            if RNG.random() < 0.8:
                plant(RNG.choice(["wash_a", "wash_b", "wash_c"]), C.plan_to_world([(u, v)])[0], RNG.uniform(0.85, 1.15))
        for t in np.linspace(0.15, 0.85, 4):
            u = px0 + pw / m + 0.9 / m
            v = cy - pl / 2 / m + t * pl / m
            plant("grass", C.plan_to_world([(u, v)])[0], RNG.uniform(0.8, 1.2))
            n["grass"] += 1

    # duplex gardens (F01): every pair sits in its own plot; stone garden wall on the plot perimeter,
    # a wall between the two units on the building's centre line, terrace at the garden facade,
    # trees scattered in the garden (dark green dots on F01)
    from shapely.geometry import box as _box
    plots = [Polygon(C.plan_to_world([(b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3])])) for b in D.T1_PLOTS + D.T2_PLOTS]
    plot_px = D.T1_PLOTS + D.T2_PLOTS
    for (px0, px1, py0, py1), pg in zip(plot_px, plots):
        q = list(pg.exterior.coords)[:4]
        for k_ in range(4):
            hedge_line(np.array(q[k_]), np.array(q[(k_ + 1) % 4]))
    used = set()
    for tr, pairs in D.DUPLEX_PAIRS.items():
        for (x0, x1, y0, y1) in pairs:
            cxp, cyp = (x0 + x1) / 2, (y0 + y1) / 2
            j = next((i for i, b in enumerate(plot_px) if b[0] <= cxp <= b[1] and b[2] <= cyp <= b[3]), None)
            gx1 = cxp - 5.2 / m                 # garden facade
            foot = Polygon(C.plan_to_world([(gx1, cyp - 7.8 / m), (cxp + 5.3 / m, cyp - 7.8 / m), (cxp + 5.3 / m, cyp + 7.8 / m), (gx1, cyp + 7.8 / m)]))
            C.GRASS_BLOCKERS.append(foot)
            if j is not None:
                used.add(j)
                b = plot_px[j]
                hedge_line(np.array(C.plan_to_world([(b[0], cyp)])[0]), np.array(C.plan_to_world([(gx1, cyp)])[0]))
                hedge_line(np.array(C.plan_to_world([(cxp + 5.3 / m, cyp)])[0]), np.array(C.plan_to_world([(b[1], cyp)])[0]))
            for ya, yb in ((cyp - 7.7 / m, cyp), (cyp, cyp + 7.7 / m)):
                terr = Polygon(C.plan_to_world([(gx1 - 3.0 / m, ya + 0.3 / m), (gx1, ya + 0.3 / m), (gx1, yb - 0.3 / m), (gx1 - 3.0 / m, yb - 0.3 / m)]))
                C.GRASS_BLOCKERS.append(terr.buffer(0.1))
                draped(f"DUP_{tr}_{x0}_{ya:.0f}_Terrace", terr, gardens, M["terrace"], 0.22, M["kerb"], 0.17, step=1.5)
            # trees in this plot (both units), clear of the house, terraces and walls
            if j is not None:
                b = plot_px[j]
                free = plots[j].buffer(-1.6).difference(foot.buffer(1.8)).difference(Polygon(C.plan_to_world(
                    [(gx1 - 3.6 / m, cyp - 8.0 / m), (gx1, cyp - 8.0 / m), (gx1, cyp + 8.0 / m), (gx1 - 3.6 / m, cyp + 8.0 / m)])))
                fp = prep(free)
                minx, miny, maxx, maxy = free.bounds
                placed_t, tries = [], 0
                while len(placed_t) < 6 and tries < 200:
                    tries += 1
                    pt = np.array([RNG.uniform(minx, maxx), RNG.uniform(miny, maxy)])
                    if fp.contains(Point(pt)) and all(np.hypot(*(pt - q_)) > 4.0 for q_ in placed_t):
                        placed_t.append(pt)
                        k = RNG.random()
                        plant("wash_a" if k < 0.25 else "olive" if k < 0.5 else "green_s" if k < 0.85 else "pink_s", pt,
                              RNG.uniform(0.7, 1.0) if k >= 0.25 else RNG.uniform(0.8, 1.05))
                        n["olives"] += 1
    # plots without a house (F01 "jardin"): trees only
    for j, pg in enumerate(plots):
        if j in used:
            continue
        minx, miny, maxx, maxy = pg.buffer(-1.5).bounds
        for _ in range(5):
            plant(RNG.choice(["olive", "green_s", "pink_s"]), np.array([RNG.uniform(minx, maxx), RNG.uniform(miny, maxy)]), RNG.uniform(0.75, 1.0))

    # hotel lodge garden: big trees in the round beds, palms on the terrace, date palms round the basin
    for (c, r) in D.HOTEL_BIG_TREES:
        plant(RNG.choice(["olive", "green"]), C.plan_to_world([c])[0], RNG.uniform(1.15, 1.35), 0.2)
    hz = C.HOTEL_ZONE
    avoid_h = unary_union([C.WET.buffer(1.0)] + [Polygon(C.plan_to_world([(b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3])])).buffer(3.0)
                                                 for nm_, b, *_ in D.PUBLIC_BUILDINGS if nm_.startswith("HOTEL")])
    hp = prep(hz.buffer(-2.0).difference(avoid_h))
    minx, miny, maxx, maxy = hz.bounds
    for xx in np.arange(minx + 3, maxx, 8.0):
        for yy in np.arange(miny + 3, maxy, 8.0):
            pt = np.array([xx + RNG.uniform(-2, 2), yy + RNG.uniform(-2, 2)])
            if hp.contains(Point(pt)) and RNG.random() < 0.5:
                plant(RNG.choice(["date_a", "date_b", "wash_c", "green_s"]), pt, RNG.uniform(0.8, 1.05), 0.17)
                n["palms"] += 1
    # lake plaza: planters on a grid (the dots on F01)
    lpp = prep(C.LAKE_PLAZA.buffer(-1.5))
    minx, miny, maxx, maxy = C.LAKE_PLAZA.bounds
    for xx in np.arange(minx + 2, maxx, 5.5):
        for yy in np.arange(miny + 2, maxy, 5.5):
            pt = np.array([xx, yy])
            if lpp.contains(Point(pt)):
                plant(RNG.choice(["green_s", "olive", "pink_s"]), pt, RNG.uniform(0.6, 0.8), 0.25)
    # T4 jardin: trees round the round path
    (jx, jy), jr = D.T4_JARDIN_RING
    for k_ in range(8):
        a_ = 2 * math.pi * k_ / 8
        plant(RNG.choice(["olive", "green_s", "pink_s"]), C.plan_to_world([(jx + (jr + 10) * math.cos(a_), jy + (jr + 10) * math.sin(a_))])[0], RNG.uniform(0.75, 0.95))

    # tree-lined footpaths between the T1 columns
    for (lx0, lx1, ly0, ly1) in D.T1_LANES:
        if lx1 - lx0 < 30:
            continue
        for yy in np.arange(ly0 + 20, ly1 - 10, 62):
            plant(RNG.choice(["wash_b", "wash_c"]), C.plan_to_world([((lx0 + lx1) / 2, yy)])[0], RNG.uniform(0.85, 1.05), 0.05)

    # club + plaza (F01: palms scattered on the paving, garden beds), market forecourt trees
    pub = C.PUBLIC_ZONE
    avoid = unary_union([C.WET.buffer(1.5)] + [Polygon(C.plan_to_world([(b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3])])).buffer(5.0)
                                               for _, b, *_ in D.PUBLIC_BUILDINGS if b[0] > 5300])
    zone = prep(pub.buffer(-2.0).difference(avoid))
    minx, miny, maxx, maxy = pub.bounds
    for xx in np.arange(minx + 3, maxx, 9.0):
        for yy in np.arange(miny + 3, maxy, 9.0):
            pt = np.array([xx + RNG.uniform(-2.5, 2.5), yy + RNG.uniform(-2.5, 2.5)])
            if zone.contains(Point(pt)) and RNG.random() < 0.55:
                plant(RNG.choice(["date_a", "date_b", "wash_c", "green_s"]), pt, RNG.uniform(0.8, 1.1), 0.17)
                n["palms"] += 1
    # entrance: garden block (trees), sports block edges, lot borders
    for nm_, pg in C.SITE_BLOCKS:
        if nm_ == "ENT_GARDEN_BLOCK":
            gp = prep(pg.buffer(-2.0))
            gx0_, gy0_, gx1_, gy1_ = pg.bounds
            for _ in range(60):
                pt = np.array([RNG.uniform(gx0_, gx1_), RNG.uniform(gy0_, gy1_)])
                if gp.contains(Point(pt)):
                    plant(RNG.choice(["olive", "green", "pink", "wash_b"]), pt, RNG.uniform(0.8, 1.1), 0.2)
        if nm_.startswith("ENT_LOT") or nm_ == "ENT_SPORTS_BLOCK":
            ring_ = pg.buffer(-0.9).exterior if pg.area > 4 else None
            if ring_ is None:
                continue
            step_ = 7.0 if nm_.startswith("ENT_LOT") else 11.0
            for d in np.arange(2.0, ring_.length, step_):
                pt = np.array(ring_.interpolate(d).coords[0])
                if nm_ == "ENT_SPORTS_BLOCK" and pg.buffer(-3.0).contains(Point(pt)):
                    continue
                plant(RNG.choice(["green_s", "olive", "date_a"]), pt, RNG.uniform(0.75, 0.95), 0.2)

    # street palms along the outer ring road and the central east-west avenue
    site = C.SITE_POLY
    ring = site.buffer(-2.4).exterior                 # in the perimeter sidewalk, clear of the ring road
    for d in np.arange(0, ring.length, 13.0):
        p = np.array(ring.interpolate(d).coords[0])
        if site.buffer(-1.5).contains(Point(p)) and all(np.hypot(*(p - q)) > 5 for q in occupied[-40:]):
            plant(RNG.choice(["wash_a", "wash_b", "wash_b"]), p, RNG.uniform(0.95, 1.2), 0.17)
            n["palms"] += 1
    avenue = LineString(C.plan_to_world([(2900, 2420), (4560, 2440)]))
    for d in np.arange(4, avenue.length, 11.0):
        for off in (-4.2, 4.2):
            p = np.array(avenue.interpolate(d).coords[0]) + np.array([-math.sin(yaw), math.cos(yaw)]) * off
            plant("date_a" if RNG.random() < 0.5 else "date_b", p, RNG.uniform(0.9, 1.1), 0.17)
            n["palms"] += 1
            if int(d / 11.0) % 2 == 0:          # flowering / shade trees between the date palms: 1 pink in 3
                p2 = np.array(avenue.interpolate(d + 5.5).coords[0]) + np.array([-math.sin(yaw), math.cos(yaw)]) * off
                key = "pink" if int(d / 22.0) % 3 == 0 else "green"
                plant(key, p2, RNG.uniform(0.85, 1.05), 0.17)
                n[key] = n.get(key, 0) + 1

    # lake park: date palm clusters, olives, grasses (avoid water); island Washingtonia
    park = [b for nm, b in C.SITE_BLOCKS if nm == "T6_LAKE_PARK"]
    if park:
        park = park[0].buffer(-2.0)
        water = C.LAKE_POLY.buffer(2.5)
        pp, wp = prep(park), prep(water)
        minx, miny, maxx, maxy = park.bounds
        tries = 0
        placed = 0
        while placed < 90 and tries < 4000:
            tries += 1
            p = np.array([RNG.uniform(minx, maxx), RNG.uniform(miny, maxy)])
            pt = Point(p)
            if pp.contains(pt) and not wp.contains(pt) and all(np.hypot(*(p - q)) > 4.5 for q in occupied[-200:]):
                k = RNG.random()
                key = "date_a" if k < 0.25 else "date_b" if k < 0.42 else "olive" if k < 0.56 else "green" if k < 0.68 else "pink" if k < 0.76 else "grass"
                plant(key, p, RNG.uniform(0.8, 1.2) if key != "olive" else RNG.uniform(0.7, 1.0))
                placed += 1
        isl = C.LAKE_ISLAND
        c = np.array(isl.centroid.coords[0])
        for k in range(5):
            a = 2 * math.pi * k / 5
            plant("wash_b", c + np.array([math.cos(a), math.sin(a)]) * 3.5, RNG.uniform(1.0, 1.25), 0.5)
        n["palms"] += 5

    # club pools: date palms around
    for pg in C.CLUB_POOLS:
        ringp = pg.buffer(5.0).exterior
        for d in np.arange(0, ringp.length, 9.0):
            plant(RNG.choice(["date_a", "date_b", "date_a", "green_s", "pink_s"]), np.array(ringp.interpolate(d).coords[0]), RNG.uniform(0.9, 1.15))
            n["palms"] += 1

    # native scrub around the plot (aerial context), sparser with distance
    site_buf = prep(site.buffer(4))
    minx, miny, maxx, maxy = site.buffer(420).bounds
    k = 0
    for _ in range(9000):
        p = np.array([RNG.uniform(minx, maxx), RNG.uniform(miny, maxy)])
        pt = Point(p)
        dist = site.distance(pt)
        if site_buf.contains(pt) or RNG.random() > math.exp(-dist / 160.0) * 0.6:
            continue
        z = float(C.TERRAIN_HEIGHT(np.array([p]))[0])
        if z < 3.0:
            continue
        nm = f"VEG_SCRUB_{k:04d}"
        instance(src["argan" if RNG.random() < 0.7 else "grass"], nm, p, z - 0.05, RNG.uniform(0, 6.28), RNG.uniform(0.5, 1.3), trees)
        k += 1
    n["scrub"] = k
    hedge.build("GARDEN_WALLS", gardens, M)
    return n


# ---------------------------------------------------------------------------
# Hero-zone lawn: real grass tufts only where cameras are close (performance)
# ---------------------------------------------------------------------------
HERO_GRASS_ZONES = []        # filled by build_grass(): (world xy, radius)


def tuft(seed):
    r = random.Random(seed)
    mb = C.MeshBuilder()
    for i in range(14):
        a = r.uniform(0, 2 * math.pi)
        h = r.uniform(0.07, 0.14)
        lean = r.uniform(0.02, 0.06)
        b = np.array([math.cos(a) * 0.03, math.sin(a) * 0.03, 0])
        s = np.array([-math.sin(a), math.cos(a), 0]) * 0.004
        t = b + np.array([math.cos(a) * lean, math.sin(a) * lean, h])
        mb.poly("grass_blade", [tuple(b - s), tuple(b + s), tuple(t)])
    return mb


def build_grass(materials, zones):
    """Scatter tufts on lawns inside each (world xy, radius) zone; skips water, terraces, houses."""
    import bpy
    from shapely.ops import unary_union
    G = C.SITE_GRADED
    src_col = C.child_collection("07_LANDSCAPE", "SRC_VEGETATION")
    srcs = [make_source(f"GRASS_TUFT_{i}", tuft(100 + i), materials, src_col) for i in range(3)]
    for s in srcs:
        s.hide_render = True
        s.hide_viewport = True
    lawns = unary_union([b.buffer(-1.9) for _, b in C.SITE_BLOCKS])
    blockers = unary_union(C.GRASS_BLOCKERS)
    lp, bp = prep(lawns), prep(blockers)
    col = C.child_collection("07_LANDSCAPE", "GRASS_TUFTS")
    # one particle-like mesh per zone: duplicate tuft geometry (merged) keeps object count low
    r = random.Random(99)
    total = 0
    for zi, (c, rad, density) in enumerate(zones):
        V, F = [], []
        src_me = [s.data for s in srcs]
        n = int(math.pi * rad * rad * density)
        for _ in range(n):
            a = r.uniform(0, 2 * math.pi)
            d = rad * math.sqrt(r.random())
            p = np.array([c[0] + math.cos(a) * d, c[1] + math.sin(a) * d])
            pt = Point(p)
            if not lp.contains(pt) or bp.contains(pt):
                continue
            z = float(G(np.array([p]))[0]) + 0.18
            me = src_me[r.randrange(3)]
            rot = r.uniform(0, 2 * math.pi)
            sc = r.uniform(0.8, 1.3)
            cr, sr = math.cos(rot), math.sin(rot)
            base = len(V)
            for v in me.vertices:
                x, y, zz = v.co
                V.append((p[0] + (x * cr - y * sr) * sc, p[1] + (x * sr + y * cr) * sc, z + zz * sc))
            for poly in me.polygons:
                F.append(tuple(base + i for i in poly.vertices))
            total += 1
        if V:
            C.mesh_object(f"GRASS_ZONE_{zi}", V, F, col, materials["grass_blade"])
    return total



# ---------------------------------------------------------------------------
# Parking: bay markings + parked cars (added 2026-10-02 after client review)
# ---------------------------------------------------------------------------
def car_mesh(seed):
    """Simple saloon / SUV massing (4.6 x 1.85 m); D5 users replace them with library cars."""
    r = random.Random(seed)
    mb = C.MeshBuilder()
    L, W = r.uniform(4.4, 4.9), r.uniform(1.8, 1.9)
    suv = r.random() < 0.35
    h1 = 0.75 if not suv else 0.95
    mb.box("car", -L / 2, L / 2, -W / 2, W / 2, 0.32, h1)
    mb.box("car", -L / 2 + 0.25, L / 2 - 0.15, -W / 2 + 0.05, W / 2 - 0.05, h1, h1 + 0.12)
    cl0, cl1 = (-L / 2 + 0.9, L / 2 - 1.3) if not suv else (-L / 2 + 0.5, L / 2 - 1.0)
    mb.box("car_glass", cl0, cl1, -W / 2 + 0.12, W / 2 - 0.12, h1 + 0.12, h1 + (0.55 if not suv else 0.75))
    mb.box("car", cl0 + 0.1, cl1 - 0.1, -W / 2 + 0.16, W / 2 - 0.16, h1 + (0.55 if not suv else 0.75), h1 + (0.6 if not suv else 0.8))
    for x in (-L / 2 + 0.8, L / 2 - 0.8):
        for y in (-W / 2 + 0.05, W / 2 - 0.27):
            mb.box("tyre", x - 0.33, x + 0.33, y, y + 0.22, 0.0, 0.66)
    return mb


def build_parking(materials):
    import bpy
    G = C.SITE_GRADED
    M = materials
    col = C.child_collection("11_VEHICLES", "PARKING")
    src_col = C.child_collection("11_VEHICLES", "SRC_CARS")
    paints = ["#E9E8E4", "#B9BDC1", "#1D1F22", "#5B1E22", "#2E3B4E", "#CFC4AE"]
    srcs = []
    for i, hexcol in enumerate(paints):
        mat = M["car"].copy()
        mat.name = f"A08_Car_Paint_{i}"
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = C_srgb(hexcol)
        mats = dict(M)
        mats["car"] = mat
        s = make_source(f"CAR_{i}", car_mesh(200 + i), mats, src_col)
        s.hide_render = True
        s.hide_viewport = True
        srcs.append(s)
    from shapely.geometry import Polygon as _Poly, Point as _Pt, LineString as _LS, box as _box
    from shapely.ops import unary_union as _union
    from shapely.prepared import prep as _prep
    lines = C.MeshBuilder()
    r = random.Random(77)
    st = {"bays": 0, "cars": 0, "moving": 0, "island_trees": 0}
    asph = _prep(C.ROADS.buffer(0.05))
    def _ent(r):
        return _Poly(C.plan_to_world(D.ent_rect(r)))
    street_c = D.ENT_STREET_A
    streets = _union([_ent((street_c - 33, street_c + 33, -900, 700))] + [_ent(r) for r in D.ENT_CARRIAGEWAYS])
    taken = []

    def paint(a_, b_):
        a_, b_ = np.asarray(a_), np.asarray(b_)
        t = (b_ - a_) / (np.linalg.norm(b_ - a_) + 1e-9)
        w = np.array([-t[1], t[0]]) * 0.06
        za, zb_ = (float(h) + 0.075 for h in G(np.array([a_, b_])))       # on the asphalt (+0.06)
        lines.poly("paint_line", [(a_[0] - w[0], a_[1] - w[1], za), (b_[0] - w[0], b_[1] - w[1], zb_),
                                  (b_[0] + w[0], b_[1] + w[1], zb_), (a_[0] + w[0], a_[1] + w[1], za)])

    def stall_row(a, b, n, ang_deg, L, fill, clip=None):
        """Bays along the kerb line a->b (world), opening towards n (unit). 45 deg = angled."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        Lr = np.linalg.norm(b - a)
        t = (b - a) / Lr
        th = math.radians(ang_deg)
        sax = n * math.sin(th) + t * math.cos(th)            # bay axis
        sp = 2.5 / math.sin(th)                              # spacing along the kerb
        k, made = 0.0, 0
        while k + sp + L * math.cos(th) <= Lr:
            p = a + t * k
            q = _Poly([p, p + t * sp, p + t * sp + sax * L, p + sax * L])
            k += sp
            if not asph.contains(q) or q.intersects(streets) or (clip is not None and not clip.contains(q)):
                continue
            if any(q.buffer(-0.15).intersects(o) for o in taken[-60:]):
                continue
            taken.append(q)
            paint(p, p + sax * L)
            paint(p + t * sp, p + t * sp + sax * L)
            st["bays"] += 1
            made += 1
            if r.random() < fill:
                c = p + t * sp / 2 + sax * L / 2
                zc = float(G(np.array([c]))[0]) + 0.06
                ang = math.atan2(sax[1], sax[0]) + (math.pi if r.random() < 0.15 else 0)
                instance(r.choice(srcs), f"VEH_CAR_{st['cars']:03d}", c, zc, ang, 1.0, col)
                st["cars"] += 1
        return made

    # 1. kerb rows along the streets (side with asphalt wins; 45 deg as on the masterplan)
    for row in D.PARKING_ROWS:
        p0, p1, depth, side = row[:4]
        ang = row[4] if len(row) > 4 else 90
        a, b = C.plan_to_world([p0])[0], C.plan_to_world([p1])[0]
        t = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-t[1], t[0]])
        best = None
        for sgn in (side, -side):
            # try both directions of travel too, so 45 deg bays can face either way
            for aa, bb in ((a, b), (b, a)):
                tt = (bb - aa) / np.linalg.norm(bb - aa)
                nn = nrm * sgn
                cnt = sum(asph.contains(_Pt(aa + tt * d + nn * 2.5)) and not streets.contains(_Pt(aa + tt * d + nn * 2.5))
                          for d in np.linspace(2, np.linalg.norm(bb - aa) - 2, 8))
                if best is None or cnt > best[0]:
                    best = (cnt, aa, bb, nn)
        stall_row(best[1], best[2], best[3], ang, depth, 0.72)

    # 2. entrance lots (F01, rotated with the entrance street): double-loaded aisles along the mall
    #    direction, 90 deg bays; small "parking" lots south of T1 columns A and B; plaza bays
    def lot_rows(a0, a1, b0, b1, frame):
        """Rows inside a lot rectangle given in a local frame (function (a, b) -> plan px)."""
        depth, aisle = 5.0 / D.M_PER_PX, 6.0 / D.M_PER_PX
        if b1 - b0 < 2 * depth + aisle:                       # shallow lot: one row facing the aisle
            pa, pb = np.array(C.plan_to_world([frame(a0, b0)])[0]), np.array(C.plan_to_world([frame(a1, b0)])[0])
            nn = np.array(C.plan_to_world([frame(a0, b0 + 1)])[0]) - pa
            stall_row(pa, pb, nn / np.linalg.norm(nn), 90, 5.0, 0.7)
            return
        bb = b0
        while bb + 2 * depth + aisle <= b1 + 1:
            for kb, nb in ((bb, +1), (bb + 2 * depth + aisle, -1)):
                pa, pb = np.array(C.plan_to_world([frame(a0, kb)])[0]), np.array(C.plan_to_world([frame(a1, kb)])[0])
                nn = np.array(C.plan_to_world([frame(a0, kb + 1)])[0]) - pa
                stall_row(pa, pb, nn / np.linalg.norm(nn) * nb, 90, 5.0, 0.7)
            bb += 2 * depth + aisle
    for (a0, a1, b0, b1) in D.ENT_LOTS:
        lot_rows(a0 + 2, a1, b0 + 2, b1, D.ent)
    for (x0, x1, y0, y1) in D.T1_SMALL_LOTS:
        lot_rows(x0 + 2, x1 - 2, y0 + 2, y1, lambda a_, b_: (a_, b_))
    (q0, q1) = D.PLAZA_ROW
    a, b = C.plan_to_world([q0])[0], C.plan_to_world([q1])[0]
    t = (b - a) / np.linalg.norm(b - a)
    nrm = np.array([-t[1], t[0]])
    if not asph.contains(_Pt((a + b) / 2 + nrm * 2.5)):
        nrm = -nrm
    stall_row(a, b, nrm, 90, 5.0, 0.7)

    # 3. entrance mall: tree rows on both verges of the channel
    mall = [pg for nm_, pg in C.SITE_BLOCKS if nm_ == "ENT_MALL_MEDIAN"][0]
    xs, ys = mall.exterior.coords.xy
    pts = np.array(list(zip(xs, ys))[:4])
    e = sorted([(pts[i], pts[(i + 1) % 4]) for i in range(4)], key=lambda ab: -np.linalg.norm(ab[1] - ab[0]))
    cen = np.array(mall.centroid.coords[0])
    for a, b in e[:2]:
        n = (a + b) / 2 - cen
        n /= np.linalg.norm(n)
        L = np.linalg.norm(b - a)
        t = (b - a) / L
        for dd in np.arange(3.0, L - 2.0, 7.0):
            c = a + t * dd - n * 1.1
            z = float(G(np.array([c]))[0]) + 0.2
            instance(SRC["date_a" if int(dd / 7) % 2 else "green_s"], f"VEG_MALL_{st['island_trees']:03d}", c, z, r.uniform(0, 6.28), 0.8, col)
            st["island_trees"] += 1

    # 4. a few cars driving (right-hand traffic, 1.8 m right of the centre line)
    from shapely.geometry import LineString as _L
    drive = [_L(C.plan_to_world(pl)) for pl in D.ROAD_CENTRELINES]
    drive.append(C.SITE_POLY.buffer(-(D.ROAD_PERIMETER_SIDEWALK + 3.6)).exterior)
    inner = _prep(C.ROADS.buffer(-1.0))
    for ln in drive:
        for d in np.arange(r.uniform(10, 40), ln.length - 5, r.uniform(55, 90)):
            p, q = np.array(ln.interpolate(d).coords[0]), np.array(ln.interpolate(d + 1.0).coords[0])
            t = (q - p) / (np.linalg.norm(q - p) + 1e-9)
            dirn = 1 if r.random() < 0.5 else -1
            c = p + np.array([t[1], -t[0]]) * 1.8 * dirn
            if not inner.contains(_Pt(c)) or any(o.distance(_Pt(c)) < 4.0 for o in taken[-200:]):
                continue
            taken.append(_Pt(c).buffer(2.5))
            zc = float(G(np.array([c]))[0]) + 0.06
            instance(r.choice(srcs), f"VEH_DRIVE_{st['moving']:03d}", c, zc, math.atan2(t[1], t[0]) + (0 if dirn > 0 else math.pi), 1.0, col)
            st["moving"] += 1
    lines.build("PARKING_LINES", col, M)
    return st


def C_srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)
