"""
03_build_terrain — natural terrain, graded site platform, beach and ocean.

Heights (sources, see PROJECT_BIBLE §07-08):
  * spot heights read off the plan F01                                  INFERRED +/- 2 m
  * shoreline z = 0.3 m from the client's Google Earth view             INFERRED +/- 5 m
  * seabed, southern cliff top, inland plateau and far hills            ASSUMED (context only)
Inside the plot the plan gives no levels, and its spot heights sit in the two ravines on either
side of the plot. The plot is a spur between those ravines. Its ground is graded to a smooth
profile along the site axis, calibrated to the client's Google Earth elevation stats over the
plot (min 18.72, median 51.28, max 64.99 m), then blended into the natural ground over 25 m.
                                                                  INFERRED (calibrated, +/- 2 m)
"""
import math

import numpy as np
from scipy.interpolate import RBFInterpolator
from shapely.geometry import LineString, Point, Polygon
from shapely.prepared import prep

C = globals()["C"]          # 00_config, injected by 20_pipeline
D = C.D

GRID = 5.0                                   # m, near field
X0, X1, Y0, Y1 = -1550.0, 1250.0, -720.0, 880.0
FAR = 30000.0                                 # m, far ring for the horizon
BLEND = 25.0                                 # m, graded site -> natural ground


def control_points():
    pts, z = [], []
    for x, y, h in D.SPOT_HEIGHTS:
        pts.append(C.plan_to_world([(x, y)])[0])
        z.append(h)
    shore = C.ge_to_world(D.GE_SHORELINE)
    line = LineString(shore)
    for d in np.linspace(0, line.length, 60):
        p = np.array(line.interpolate(d).coords[0])
        q = np.array(line.interpolate(min(d + 5, line.length)).coords[0]) - np.array(line.interpolate(max(d - 5, 0)).coords[0])
        t = q / (np.linalg.norm(q) + 1e-9)
        west = np.array([t[1], -t[0]])
        if west[0] > 0:
            west = -west
        pts += [p, p + west * 120, p + west * 350, p + west * 900]
        z += [0.3, -6.0, -15.0, -28.0]
        # land side: sandy beach to the north of the site, rocky cliff to the south (GE imagery)
        if p[1] > 150:
            pass
        else:
            pts.append(p - west * 45)
            z.append(16.0 if p[1] < -150 else 10.0)
    for p in C.ge_to_world(D.GE_BEACH_BACK):
        pts.append(p)
        z.append(5.0)
    road = C.ge_to_world(D.GE_ROAD_R104)
    rl = LineString(road)
    for d in np.linspace(0, rl.length, 12):
        p = np.array(rl.interpolate(d).coords[0])
        pts += [p + np.array([350.0, 0]), p + np.array([900.0, 0])]
        z += [70.0, 85.0]
    for p, h in [((3500, 2500), 230.0), ((4200, -800), 260.0), ((3000, -2600), 180.0), ((2600, 4200), 200.0),
                 ((1800, 1800), 120.0), ((1600, -1500), 110.0)]:
        pts.append(np.array(p, float))
        z.append(h)
    return np.array(pts), np.array(z)


GE_MIN, GE_MEDIAN, GE_MAX = 18.72, 51.28, 64.99      # CONFIRMED F08


def site_profile(site, ax):
    """Concave profile z(u) = zmin + (zmax - zmin) * (1 - (1 - t)^p), p solved so that the
    area-weighted median over the plot equals the Google Earth median."""
    xs, ys = np.meshgrid(np.arange(-330, 330, 3.0), np.arange(-260, 260, 3.0))
    flat = np.stack([xs.ravel(), ys.ravel()], 1)
    sp = prep(site)
    u = np.array([p @ ax for p in flat if sp.contains(Point(p))])
    u0, u1 = u.min(), u.max()
    zmin, zmax = GE_MIN + 0.5, GE_MAX - 1.0
    def zf(uu, p):
        t = np.clip((np.asarray(uu) - u0) / (u1 - u0), 0, 1)
        return zmin + (zmax - zmin) * (1 - (1 - t) ** p)
    lo, hi = 0.3, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if np.median(zf(u, mid)) < GE_MEDIAN:
            lo = mid
        else:
            hi = mid
    p = (lo + hi) / 2
    centres = np.linspace(u0 - 30, u1 + 30, 200)
    return centres, zf(centres, p), p


def build_terrain_function():
    site = Polygon(C.site_polygon_world())
    ang = C.yaw()
    ax = np.array([math.cos(ang), math.sin(ang)])
    perp = np.array([-ax[1], ax[0]])
    centres, prof, pexp = site_profile(site, ax)
    P, Z = control_points()
    # the spur: the graded profile along three lines inside the plot joins the natural terrain
    ridge, rz = [], []
    for off in (-25.0, 0.0, 25.0):
        for uu in np.linspace(centres[0] + 30, centres[-1] - 30, 40):
            q = ax * uu + perp * off + np.array(site.centroid.coords[0]) * 0
            if site.buffer(-5).contains(Point(q)):
                ridge.append(q)
                rz.append(np.interp(uu, centres, prof))
    P = np.vstack([P, np.array(ridge)])
    Z = np.concatenate([Z, np.array(rz)])
    rbf0 = RBFInterpolator(P, Z, kernel="thin_plate_spline", smoothing=8.0, degree=1)
    shore = C.ge_to_world(D.GE_SHORELINE)
    shore_line = LineString(shore)

    def land_side(pxy):
        """+1 east (land) of the shoreline polyline, -1 west (sea)."""
        out = np.empty(len(pxy))
        for i, p in enumerate(pxy):
            d = shore_line.project(Point(p))
            a = np.array(shore_line.interpolate(max(d - 3, 0)).coords[0])
            b = np.array(shore_line.interpolate(min(d + 3, shore_line.length)).coords[0])
            t = b - a
            out[i] = 1.0 if (t[0] * (p[1] - a[1]) - t[1] * (p[0] - a[0])) > 0 else -1.0
        return out

    def rbf(pxy):
        pxy = np.asarray(pxy, float).reshape(-1, 2)
        z = rbf0(pxy)
        land = land_side(pxy) > 0
        z[land] = np.maximum(z[land], 0.6 + 0.04 * np.array([shore_line.distance(Point(p)) for p in pxy[land]]).clip(0, 40))
        return z
    sprep = prep(site)
    boundary = site.exterior

    def graded(pxy):
        uu = np.asarray(pxy) @ ax
        return np.interp(uu, centres, prof)

    def height(pxy):
        pxy = np.asarray(pxy, float).reshape(-1, 2)
        zn_ = rbf(pxy)
        zg = graded(pxy)
        out = zn_.copy()
        for i, p in enumerate(pxy):
            pt = Point(p)
            if sprep.contains(pt):
                out[i] = zg[i]
            else:
                d = boundary.distance(pt)
                if d < BLEND:
                    t = d / BLEND
                    t = t * t * (3 - 2 * t)
                    out[i] = zg[i] * (1 - t) + zn_[i] * t
        return out

    height.profile_exponent = pexp
    height.rbf0 = rbf0
    return height, graded, rbf, (centres, prof)


def terrain_masks(pxy, z, rbf):
    """Per-vertex sand / rock / site weights (stored as a colour attribute)."""
    shore = LineString(C.ge_to_world(D.GE_SHORELINE))
    back = LineString(C.ge_to_world(D.GE_BEACH_BACK))
    site = prep(Polygon(C.site_polygon_world()).buffer(3.0))
    sand = np.zeros(len(pxy))
    rock = np.zeros(len(pxy))
    insite = np.zeros(len(pxy))
    gx = (rbf(pxy + [2.0, 0]) - rbf(pxy - [2.0, 0])) / 4.0
    gy = (rbf(pxy + [0, 2.0]) - rbf(pxy - [0, 2.0])) / 4.0
    slope = np.sqrt(gx * gx + gy * gy)
    for i, p in enumerate(pxy):
        pt = Point(p)
        ds = shore.distance(pt)
        if p[1] > 120:                        # sandy bay north of the site
            db = back.distance(pt)
            sand[i] = 1.0 if (z[i] < 6.5 and ds < 260) else max(0.0, 1 - db / 25.0) * (z[i] < 9)
        else:                                 # rocky coast south of the site
            sand[i] = max(0.0, 1 - ds / 18.0) * (z[i] < 3)
            rock[i] = max(0.0, 1 - ds / 70.0)
        rock[i] = max(rock[i], min(1.0, max(0.0, (slope[i] - 0.35) * 2.5)))
        insite[i] = 1.0 if site.contains(pt) else 0.0
    return sand, rock, insite


def build(materials):
    import bpy
    height, graded, rbf, prof = build_terrain_function()
    rbf0_far = height.rbf0
    C.TERRAIN_HEIGHT = height
    C.SITE_GRADED = graded
    col = C.collection("02_TERRAIN")

    nx = int((X1 - X0) / GRID) + 1
    ny = int((Y1 - Y0) / GRID) + 1
    xs = np.linspace(X0, X1, nx)
    ys = np.linspace(Y0, Y1, ny)
    gx, gy = np.meshgrid(xs, ys)
    pxy = np.stack([gx.ravel(), gy.ravel()], 1)
    z = height(pxy)
    verts = np.column_stack([pxy, z])
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))
    uvs = [(p[0] / 10.0, p[1] / 10.0) for p in pxy]
    ob = C.mesh_object("TERRAIN_NEAR", verts, faces, col, materials["terrain"], uvs, smooth=True)
    sand, rock, insite = terrain_masks(pxy, z, rbf)
    me = ob.data
    attr = me.color_attributes.new("mask", "FLOAT_COLOR", "POINT")
    cols = np.column_stack([sand, rock, insite, np.ones(len(sand))]).astype(np.float32)
    attr.data.foreach_set("color", cols.ravel())

    # far ring: grid lines include the near-field edges; faces inside the near field are removed
    def axis(lo, hi):
        left = lo - np.geomspace(GRID * 4, FAR, 22)[::-1]
        right = hi + np.geomspace(GRID * 4, FAR, 22)
        inner = np.linspace(lo, hi, 15)
        return np.concatenate([left, inner, right])
    rx, ry = axis(X0, X1), axis(Y0, Y1)
    fx, fy = np.meshgrid(rx, ry)
    fp = np.stack([fx.ravel(), fy.ravel()], 1)
    fz = np.clip(rbf0_far(fp), -40, 320)
    # sea side of the coast line (extended beyond the traced shoreline) stays under water
    sh = C.ge_to_world(D.GE_SHORELINE)
    a0, a1 = sh[0], sh[-1]
    t = (a1 - a0) / np.linalg.norm(a1 - a0)
    nrm = np.array([t[1], -t[0]])
    sd = (fp - a0) @ nrm                        # > 0 = west / sea side
    sea = sd > 60
    fz[sea] = np.minimum(fz[sea], -8.0 - 0.004 * sd[sea])
    edge = (np.isclose(fp[:, 0], X0) | np.isclose(fp[:, 0], X1) | np.isclose(fp[:, 1], Y0) | np.isclose(fp[:, 1], Y1)) & \
           (fp[:, 0] >= X0 - 1e-6) & (fp[:, 0] <= X1 + 1e-6) & (fp[:, 1] >= Y0 - 1e-6) & (fp[:, 1] <= Y1 + 1e-6)
    if edge.any():
        fz[edge] = height(fp[edge]) - 0.4
    fverts = np.column_stack([fp, fz])
    ffaces = []
    nx_, ny_ = len(rx), len(ry)
    for j in range(ny_ - 1):
        for i in range(nx_ - 1):
            cx_ = (rx[i] + rx[i + 1]) / 2
            cy_ = (ry[j] + ry[j + 1]) / 2
            if X0 < cx_ < X1 and Y0 < cy_ < Y1:
                continue                         # hole: the near terrain lives here
            a = j * nx_ + i
            ffaces.append((a, a + 1, a + nx_ + 1, a + nx_))
    fuv = [(p[0] / 10.0, p[1] / 10.0) for p in fp]
    fob = C.mesh_object("TERRAIN_FAR", fverts, ffaces, col, materials["terrain"], fuv, smooth=True)
    fattr = fob.data.color_attributes.new("mask", "FLOAT_COLOR", "POINT")
    fattr.data.foreach_set("color", np.column_stack([np.zeros(len(fp)), np.zeros(len(fp)), np.zeros(len(fp)), np.ones(len(fp))]).astype(np.float32).ravel())

    # ocean surface
    s = 40000.0
    C.mesh_object("OCEAN", [(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [(0, 1, 2, 3)], col,
                  materials["ocean"], [(-s / 20, -s / 20), (s / 20, -s / 20), (s / 20, s / 20), (-s / 20, s / 20)])
    return dict(profile=prof)
