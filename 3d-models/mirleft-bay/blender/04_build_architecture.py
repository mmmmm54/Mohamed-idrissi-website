"""
04_build_architecture — building kit (walls, openings, details) and every building type.

Geometry status (PROJECT_BIBLE §09-19):
  * Duplex pair (hero, Tranche 1/2): INFERRED from catalogue p7-p8 (room areas, render),
    site photo F07 and the permit area (124 m2 covered per unit). Footprint 15.4 x 10.4 m
    matches the pair outline on the plan (15.4 x 13.3 m incl. front terraces).
  * Villa B / C / A: INFERRED from the permit areas (164 / 145 / 220 m2) and lot sizes, same
    architectural language as the built villa.
  * Public buildings: kasbah language from photo F04 / render F05, footprints from the plan.
Heights: storey 3.10 m + slabs, parapet 1.10 m (ASSUMED A1-A4).

Local frame of every type: x = depth (garden facade at the low-x side faces the ocean, WNW),
y = width, z up, origin at the footprint centre on the finished ground floor.
"""
import math

import numpy as np

C = globals()["C"]
D = C.D

GF_H = 3.35            # ground floor incl. slab (finished floor to terrace floor)
UF_H = 3.10            # upper floor
PAR = 1.10
T = 0.30
CORNICE = 0.10


# ---------------------------------------------------------------------------
# Kit
# ---------------------------------------------------------------------------
class Kit(C.MeshBuilder):
    """Facade helpers on top of MeshBuilder. 'side' = which face of an axis-aligned volume."""

    def wall_x(self, mat, x_face, inward, y0, y1, z0, z1, openings=(), t=T):
        """Wall in the plane x = x_face, thickness t towards 'inward' (+1 / -1), with openings
        given as (y0, y1, z0, z1, kind)."""
        xa, xb = sorted((x_face, x_face + inward * t))
        self._wall(mat, "x", xa, xb, y0, y1, z0, z1, openings)
        for o in openings:
            self.opening("x", x_face, inward, o)

    def wall_y(self, mat, y_face, inward, x0, x1, z0, z1, openings=(), t=T):
        ya, yb = sorted((y_face, y_face + inward * t))
        self._wall(mat, "y", ya, yb, x0, x1, z0, z1, openings)
        for o in openings:
            self.opening("y", y_face, inward, o)

    def _wall(self, mat, ax, a0, a1, u0, u1, z0, z1, openings):
        cuts = sorted({u0, u1, *[min(max(o[0], u0), u1) for o in openings], *[min(max(o[1], u0), u1) for o in openings]})
        for ua, ub in zip(cuts[:-1], cuts[1:]):
            cover = sorted((o[2], o[3]) for o in openings if o[0] <= ua + 1e-6 and o[1] >= ub - 1e-6)
            segs = [(z0, z1)]
            for c0, c1 in cover:
                nxt = []
                for s0, s1 in segs:
                    if c1 <= s0 or c0 >= s1:
                        nxt.append((s0, s1))
                        continue
                    if c0 > s0:
                        nxt.append((s0, c0))
                    if c1 < s1:
                        nxt.append((c1, s1))
                segs = nxt
            for s0, s1 in segs:
                if s1 - s0 > 1e-4:
                    if ax == "x":
                        self.box(mat, a0, a1, ua, ub, s0, s1)
                    else:
                        self.box(mat, ua, ub, a0, a1, s0, s1)

    def fbox(self, mat, ax, face, inward, u0, u1, d0, d1, z0, z1):
        """Box in facade coordinates: d measured inward from the face (negative = proud)."""
        a, b = face + inward * d0, face + inward * d1
        if ax == "x":
            self.box(mat, a, b, u0, u1, z0, z1)
        else:
            self.box(mat, u0, u1, a, b, z0, z1)

    def opening(self, ax, face, inward, o):
        u0, u1, z0, z1, kind = o
        F = lambda *a: self.fbox(*a)
        # projecting surround (darker render band), as on the built villa
        band, proud = 0.22, 0.06
        F("render_dark", ax, face, inward, u0 - band, u0, -proud, 0.02, z0 - (band if kind == "win" else 0), z1 + band)
        F("render_dark", ax, face, inward, u1, u1 + band, -proud, 0.02, z0 - (band if kind == "win" else 0), z1 + band)
        F("render_dark", ax, face, inward, u0 - band, u1 + band, -proud, 0.02, z1, z1 + band)
        if kind == "win":
            F("render_dark", ax, face, inward, u0 - band, u1 + band, -proud - 0.03, 0.02, z0 - band, z0)
        # frame + glass (sliding: mullions every ~1.2 m)
        fw = 0.06
        F("bronze", ax, face, inward, u0, u1, 0.10, 0.17, z0, z0 + fw)
        F("bronze", ax, face, inward, u0, u1, 0.10, 0.17, z1 - fw, z1)
        F("bronze", ax, face, inward, u0, u0 + fw, 0.10, 0.17, z0, z1)
        F("bronze", ax, face, inward, u1 - fw, u1, 0.10, 0.17, z0, z1)
        n = max(1, round((u1 - u0) / 1.2))
        for i in range(1, n):
            um = u0 + (u1 - u0) * i / n
            F("bronze", ax, face, inward, um - 0.035, um + 0.035, 0.10, 0.17, z0, z1)
        F("glass", ax, face, inward, u0 + fw, u1 - fw, 0.13, 0.14, z0 + fw, z1 - fw)
        # interior proxy (CINEMATIC_APPROXIMATION): room box behind the glazing + linen curtains
        depth = 2.8
        F("interior", ax, face, inward, u0 - 0.6, u1 + 0.6, depth, depth + 0.05, z0 - 0.05, z1 + 0.35)
        F("interior", ax, face, inward, u0 - 0.6, u1 + 0.6, T, depth, z0 - 0.06, z0 - 0.01)
        F("interior", ax, face, inward, u0 - 0.6, u1 + 0.6, T, depth, z1 + 0.30, z1 + 0.35)
        F("interior", ax, face, inward, u0 - 0.65, u0 - 0.6, T, depth, z0 - 0.05, z1 + 0.35)
        F("interior", ax, face, inward, u1 + 0.6, u1 + 0.65, T, depth, z0 - 0.05, z1 + 0.35)
        cw = min(0.55, (u1 - u0) * 0.18)
        F("curtain", ax, face, inward, u0 + 0.05, u0 + 0.05 + cw, 0.32, 0.40, z0 + 0.02, z1 - 0.05)
        F("curtain", ax, face, inward, u1 - 0.05 - cw, u1 - 0.05, 0.32, 0.40, z0 + 0.02, z1 - 0.05)
        if kind == "door":
            F("lamp", ax, face, inward, (u0 + u1) / 2 - 0.12, (u0 + u1) / 2 + 0.12, 1.2, 1.45, z1 + 0.18, z1 + 0.22)

    def niches(self, ax, face, inward, u0, u1, z, step=0.95, size=0.16, depth=0.10):
        """Row of small square wall niches (built villa F07). Built as dark recess boxes slightly
        proud of a cut, approximated by a thin shadow box set into the wall face."""
        n = int((u1 - u0) / step)
        off = (u1 - u0 - (n - 1) * step) / 2
        for i in range(n):
            u = u0 + off + i * step
            self.fbox("render_dark", ax, face, inward, u - size / 2, u + size / 2, -0.004, depth, z, z + size)

    def parapet_ring(self, mat, x0, x1, y0, y1, z0, h=PAR, t=0.25, skip=()):
        sides = {"x0": (x0, x0 + t, y0, y1), "x1": (x1 - t, x1, y0, y1),
                 "y0": (x0, x1, y0, y0 + t), "y1": (x0, x1, y1 - t, y1)}
        for k, (a, b, c, d) in sides.items():
            if k in skip:
                continue
            self.box(mat, a, b, c, d, z0, z0 + h)
            # slim cornice cap
            self.box("render", a - (CORNICE if k == "x0" else 0), b + (CORNICE if k == "x1" else 0),
                     c - (CORNICE if k == "y0" else 0), d + (CORNICE if k == "y1" else 0), z0 + h, z0 + h + 0.06)

    def pergola(self, x0, x1, y0, y1, z0, top, spacing=0.42, along="x"):
        """Timber pergola (F06/F07): 2 posts at the free edge, a header beam, rafters running
        perpendicular to the facade with a 0.35 m overhang."""
        post = 0.15
        for y in (y0 + 0.1, y1 - 0.1 - post):
            self.box("timber", x0 + 0.15, x0 + 0.15 + post, y, y + post, z0, top - 0.22)
        self.box("timber", x0 + 0.1, x0 + 0.32, y0, y1, top - 0.36, top - 0.14)            # header
        self.box("timber", x1 - 0.22, x1, y0, y1, top - 0.36, top - 0.14)                   # wall plate
        n = int((y1 - y0) / spacing)
        for i in range(n + 1):
            y = y0 + i * (y1 - y0 - 0.06) / n
            self.box("timber", x0 - 0.35, x1, y, y + 0.06, top - 0.14, top + 0.06)

    def lattice(self, x0, x1, y0, y1, z0, z1, along="y"):
        """Moroccan geometric timber screen (render F06): frame + nested rectangles."""
        t = 0.04
        if along == "y":
            self.box("timber", x0, x1, y0, y1, z0, z0 + t)
            self.box("timber", x0, x1, y0, y1, z1 - t, z1)
            n = max(2, int((y1 - y0) / 0.9))
            for i in range(n + 1):
                y = y0 + i * (y1 - y0 - t) / n
                self.box("timber", x0, x1, y, y + t, z0, z1)
            for i in range(n):
                ya = y0 + i * (y1 - y0 - t) / n + 0.16
                yb = y0 + (i + 1) * (y1 - y0 - t) / n - 0.12
                zm = (z0 + z1) / 2
                self.box("timber", x0, x1, ya, yb, zm - 0.12, zm - 0.12 + t)
                self.box("timber", x0, x1, ya, yb, zm + 0.10, zm + 0.10 + t)
                self.box("timber", x0, x1, ya, ya + t, zm - 0.12, zm + 0.14)
        else:
            self.box("timber", x0, x1, y0, y1, z0, z0 + t)
            self.box("timber", x0, x1, y0, y1, z1 - t, z1)
            n = max(2, int((x1 - x0) / 0.9))
            for i in range(n + 1):
                x = x0 + i * (x1 - x0 - t) / n
                self.box("timber", x, x + t, y0, y1, z0, z1)

    def jacuzzi(self, cx, cy, z):
        r, seg = 0.95, 24
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            pts_o = [(cx + (r + 0.18) * math.cos(a), cy + (r + 0.18) * math.sin(a)) for a in (a0, a1)]
            pts_i = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in (a0, a1)]
            (ox0, oy0), (ox1, oy1) = pts_o
            (ix0, iy0), (ix1, iy1) = pts_i
            self.poly("terrace", [(ix0, iy0, z + 0.55), (ox0, oy0, z + 0.55), (ox1, oy1, z + 0.55), (ix1, iy1, z + 0.55)])
            self.poly("render", [(ox0, oy0, z), (ox1, oy1, z), (ox1, oy1, z + 0.55), (ox0, oy0, z + 0.55)])
            self.poly("pool_tile", [(ix1, iy1, z - 0.2), (ix0, iy0, z - 0.2), (ix0, iy0, z + 0.55), (ix1, iy1, z + 0.55)])
            self.poly("pool_water", [(cx, cy, z + 0.45), (ix0, iy0, z + 0.45), (ix1, iy1, z + 0.45)])


# ---------------------------------------------------------------------------
# Hero: duplex pair (two mirrored units, party wall at y = 0)
# ---------------------------------------------------------------------------
DUP_W, DUP_D, DUP_SET = 15.4, 10.4, 3.6


def duplex_unit(k, s):
    """One unit; s = -1 for the unit on the -y side, +1 for the mirrored one."""
    W, Dp, SB = DUP_W / 2, DUP_D, DUP_SET
    x0, x1 = -Dp / 2, Dp / 2
    yo = s * W                               # outer side wall
    ylo, yhi = sorted((0.0, yo))
    Y = lambda a, b: tuple(sorted((s * a, s * b)))       # unit-local |y| -> signed range
    z1 = GF_H
    z2 = GF_H + UF_H
    # ground floor slab and plinth
    k.box("render_dark", x0 - 0.05, x1 + 0.05, ylo, yhi, -1.6, 0.02)
    # --- ground floor walls
    y_s, y_b = Y(1.4, 5.0), Y(5.7, 6.9)
    k.wall_x("render", x0, +1, ylo, yhi, 0.02, z1,
             [(y_s[0], y_s[1], 0.02, 2.62, "door"), (y_b[0], y_b[1], 0.95, 2.45, "win")])
    k.niches("x", x0, +1, ylo + 0.4, yhi - 0.4, 2.98)
    ye, yk, yw = Y(1.0, 2.1), Y(3.2, 4.2), Y(5.6, 6.4)
    k.wall_x("render", x1, -1, ylo, yhi, 0.02, z1,
             [(ye[0], ye[1], 0.02, 2.35, "door"), (yk[0], yk[1], 1.2, 2.35, "win"), (yw[0], yw[1], 1.6, 2.35, "win")])
    k.niches("x", x1, -1, ylo + 0.4, yhi - 0.4, 2.98)
    xa, xb = -1.6, 3.4
    k.wall_y("render", yo, -s, x0 + T, x1 - T, 0.02, z1,
             [(xa, xa + 0.9, 0.02, 2.45, "door"), (xb - 0.6, xb + 0.6, 1.1, 2.35, "win")])
    # party wall (shared, full height), built by the -y unit only
    if s < 0:
        k.box("render", x0, x0 + SB, -0.12, 0.12, 0.02, z1 + 1.9)          # GF + terrace privacy wall
        k.box("render", x0 + SB, x1, -0.12, 0.12, 0.02, z2 + PAR)
    # --- terrace over the ground floor (x0 .. x0 + SB)
    k.box("render", x0, x1, ylo, yhi, z1 - 0.30, z1)                     # slab
    k.box("terrace", x0 + 0.25, x0 + SB, ylo + (0.12 if s > 0 else 0), yhi - (0.12 if s < 0 else 0), z1, z1 + 0.03)
    # terrace parapet: solid low wall + timber lattice on the outer part, solid near the party wall
    k.box("render", x0, x0 + 0.25, ylo, yhi, z1, z1 + 0.50)
    ylt = Y(2.6, W - 0.3)
    k.lattice(x0 + 0.06, x0 + 0.19, ylt[0], ylt[1], z1 + 0.50, z1 + 1.05)
    ysol = Y(0.12, 2.6)
    k.box("render", x0, x0 + 0.25, ysol[0], ysol[1], z1 + 0.50, z1 + 1.15)
    k.box("render", x0, x0 + SB, yo - s * 0.25 if s > 0 else yo, yo if s > 0 else yo + 0.25, z1, z1 + 1.05)
    # --- upper floor (set back)
    ux0 = x0 + SB
    y_t, y_w2 = Y(1.2, 3.6), Y(4.6, 6.4)
    k.wall_x("render", ux0, +1, ylo, yhi, z1, z2, [(y_t[0], y_t[1], z1 + 0.03, z1 + 2.55, "door"), (y_w2[0], y_w2[1], z1 + 0.9, z1 + 2.3, "win")])
    k.niches("x", ux0, +1, ylo + 0.4, yhi - 0.4, z1 + 2.72)
    yb2 = Y(4.4, 5.6)
    k.wall_x("render", x1, -1, ylo, yhi, z1, z2, [(yb2[0], yb2[1], z1 + 0.9, z1 + 2.3, "win")])
    k.wall_y("render", yo, -s, ux0 + T, x1 - T, z1, z2, [(2.0, 3.2, z1 + 0.9, z1 + 2.3, "win")])
    k.box("render", ux0, x1, ylo, yhi, z2 - 0.30, z2)                    # roof slab
    # pergola over the outer part of the terrace (render F06 / photo F07)
    yp = Y(2.4, W - 0.05)
    k.pergola(x0 - 0.05, ux0, yp[0], yp[1], z1, z1 + 2.75)
    # --- roof terrace
    k.parapet_ring("render", ux0, x1, ylo, yhi, z2, PAR, 0.25, skip=("y1" if s < 0 else "y0",))
    k.box("terrace", ux0 + 0.25, x1 - 0.25, ylo + 0.12, yhi - 0.12, z2, z2 + 0.04)
    # stair house at the street corner + its door
    sx0, sx1 = x1 - 3.0, x1
    sy = Y(W - 2.6, W)
    k.box("render", sx0, sx1, sy[0], sy[1], z2, z2 + 2.55)
    k.box("render", sx0 - CORNICE, sx1 + CORNICE, sy[0] - CORNICE, sy[1] + CORNICE, z2 + 2.55, z2 + 2.65)
    k.fbox("bronze", "x", sx0, +1, sy[0] + 0.7, sy[1] - 0.8, -0.02, 0.05, z2 + 0.05, z2 + 2.2)
    k.jacuzzi(ux0 + 1.6, s * (W - 1.6), z2 + 0.04)


def build_duplex_pair(k):
    duplex_unit(k, -1)
    duplex_unit(k, +1)


# ---------------------------------------------------------------------------
# Villas (same language)
# ---------------------------------------------------------------------------
def villa_r1(k, Wd=11.0, Dp=8.6, SB=3.4):
    """Villa type B: detached R+1, ~164 m2 covered (permit)."""
    x0, x1, y0, y1 = -Dp / 2, Dp / 2, -Wd / 2, Wd / 2
    z1, z2 = GF_H, GF_H + UF_H
    k.box("render_dark", x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, -1.6, 0.02)
    k.wall_x("render", x0, +1, y0, y1, 0.02, z1, [(-4.4, -0.6, 0.02, 2.62, "door"), (1.2, 3.6, 0.95, 2.45, "win")])
    k.niches("x", x0, +1, y0 + 0.4, y1 - 0.4, 2.98)
    k.wall_x("render", x1, -1, y0, y1, 0.02, z1, [(-0.6, 0.6, 0.02, 2.35, "door"), (2.2, 3.2, 1.2, 2.35, "win")])
    k.wall_y("render", y0, +1, x0 + T, x1 - T, 0.02, z1, [(-0.45, 0.45, 0.02, 2.45, "win")])
    k.wall_y("render", y1, -1, x0 + T, x1 - T, 0.02, z1, [(0.8, 2.0, 1.1, 2.35, "win")])
    k.box("render", x0, x1, y0, y1, z1 - 0.3, z1)
    k.box("terrace", x0 + 0.25, x0 + SB, y0 + 0.25, y1 - 0.25, z1, z1 + 0.03)
    k.box("render", x0, x0 + 0.25, y0, y1, z1, z1 + 0.5)
    k.lattice(x0 + 0.06, x0 + 0.19, y0 + 0.3, y1 - 0.3, z1 + 0.5, z1 + 1.05)
    for yy in (y0, y1 - 0.25):
        k.box("render", x0, x0 + SB, yy, yy + 0.25, z1, z1 + 1.05)
    ux0 = x0 + SB
    k.wall_x("render", ux0, +1, y0, y1, z1, z2, [(-3.6, -1.2, z1 + 0.03, z1 + 2.55, "door"), (1.0, 3.0, z1 + 0.9, z1 + 2.3, "win")])
    k.niches("x", ux0, +1, y0 + 0.4, y1 - 0.4, z1 + 2.72)
    k.wall_x("render", x1, -1, y0, y1, z1, z2, [(-2.5, -1.3, z1 + 0.9, z1 + 2.3, "win")])
    k.wall_y("render", y0, +1, ux0 + T, x1 - T, z1, z2, [])
    k.wall_y("render", y1, -1, ux0 + T, x1 - T, z1, z2, [(0.4, 1.4, z1 + 0.9, z1 + 2.3, "win")])
    k.box("render", ux0, x1, y0, y1, z2 - 0.3, z2)
    k.pergola(x0 - 0.05, ux0, y0 + 0.2, 1.2, z1, z1 + 2.75)
    k.parapet_ring("render", ux0, x1, y0, y1, z2)
    k.box("roof", ux0 + 0.25, x1 - 0.25, y0 + 0.25, y1 - 0.25, z2, z2 + 0.04)
    k.box("render", x1 - 3.0, x1, y1 - 2.6, y1, z2, z2 + 2.55)
    k.box("render", x1 - 3.0 - CORNICE, x1 + CORNICE, y1 - 2.6 - CORNICE, y1 + CORNICE, z2 + 2.55, z2 + 2.65)
    k.jacuzzi(ux0 + 1.5, y0 + 1.5, z2 + 0.04)


def villa_rdc(k, Wd, Dp, pergola_w):
    """Villa type C (~145 m2) / A (~220 m2): single storey with a roof terrace."""
    x0, x1, y0, y1 = -Dp / 2, Dp / 2, -Wd / 2, Wd / 2
    z1 = GF_H
    k.box("render_dark", x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, -1.6, 0.02)
    ops = []
    n = 2 if Wd < 14 else 3
    seg = Wd / n
    for i in range(n):
        yc = y0 + seg * (i + 0.5)
        ops.append((yc - min(1.8, seg * 0.35), yc + min(1.8, seg * 0.35), 0.02, 2.62, "door" if i == 0 else "win"))
    k.wall_x("render", x0, +1, y0, y1, 0.02, z1, ops)
    k.niches("x", x0, +1, y0 + 0.4, y1 - 0.4, 2.98)
    k.wall_x("render", x1, -1, y0, y1, 0.02, z1, [(-0.6, 0.6, 0.02, 2.35, "door"), (y1 - 3.0, y1 - 1.8, 1.2, 2.35, "win")])
    k.niches("x", x1, -1, y0 + 0.4, y1 - 0.4, 2.98)
    k.wall_y("render", y0, +1, x0 + T, x1 - T, 0.02, z1, [(-0.6, 0.6, 1.1, 2.35, "win")])
    k.wall_y("render", y1, -1, x0 + T, x1 - T, 0.02, z1, [(-1.5, -0.6, 0.02, 2.45, "win")])
    k.box("render", x0, x1, y0, y1, z1 - 0.3, z1)
    k.parapet_ring("render", x0, x1, y0, y1, z1)
    k.box("roof", x0 + 0.25, x1 - 0.25, y0 + 0.25, y1 - 0.25, z1, z1 + 0.04)
    k.pergola(x0 + 0.3, x0 + 4.0, y0 + 0.3, y0 + 0.3 + pergola_w, z1 + 0.04, z1 + 2.7)
    k.box("render", x1 - 2.8, x1, y1 - 2.6, y1, z1, z1 + 2.55)
    k.box("render", x1 - 2.8 - CORNICE, x1 + CORNICE, y1 - 2.6 - CORNICE, y1 + CORNICE, z1 + 2.55, z1 + 2.65)


# ---------------------------------------------------------------------------
# Public buildings: kasbah language (photo F04)
# ---------------------------------------------------------------------------
def crenellation(k, x0, x1, y0, y1, z, merlon=0.55, gap=0.55, h=0.6, t=0.35):
    for (a0, a1, b0, b1, along) in ((x0, x1, y0, y0 + t, "x"), (x0, x1, y1 - t, y1, "x"),
                                     (x0, x0 + t, y0, y1, "y"), (x1 - t, x1, y0, y1, "y")):
        L = (a1 - a0) if along == "x" else (b1 - b0)
        n = max(1, int(L / (merlon + gap)))
        step = L / n
        k.box("render", a0, a1, b0, b1, z, z + 0.25)
        for i in range(n):
            if along == "x":
                c = a0 + step * (i + 0.5)
                k.box("render", c - merlon / 2, c + merlon / 2, b0, b1, z + 0.25, z + 0.25 + h)
                k.box("render", c - merlon / 4, c + merlon / 4, b0, b1, z + 0.25 + h, z + 0.4 + h)
            else:
                c = b0 + step * (i + 0.5)
                k.box("render", a0, a1, c - merlon / 2, c + merlon / 2, z + 0.25, z + 0.25 + h)
                k.box("render", a0, a1, c - merlon / 4, c + merlon / 4, z + 0.25 + h, z + 0.4 + h)


def kasbah(k, Wd, Dp, levels, towers=True, portal=False):
    x0, x1, y0, y1 = -Dp / 2, Dp / 2, -Wd / 2, Wd / 2
    H = levels * 3.6
    k.box("render_dark", x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, -1.6, 0.02)
    # main body with recessed vertical window bays on the long faces
    for face, inward in ((x0, +1), (x1, -1)):
        bays = max(2, int(Wd / 4.2))
        ops = []
        for i in range(bays):
            yc = y0 + Wd * (i + 0.5) / bays
            ops.append((yc - 0.55, yc + 0.55, 0.9, H - 1.2, "win"))
        if portal and face == x0:
            ops[len(ops) // 2] = (-1.6, 1.6, 0.02, 3.4, "door")
        k.wall_x("render", face, inward, y0, y1, 0.02, H, ops, t=0.45)
    for face, inward in ((y0, +1), (y1, -1)):
        k.wall_y("render", face, inward, x0 + 0.45, x1 - 0.45, 0.02, H,
                 [(-0.5, 0.5, 0.9, H - 1.2, "win")], t=0.45)
    k.box("render", x0, x1, y0, y1, H - 0.3, H)
    crenellation(k, x0, x1, y0, y1, H)
    # chevron relief band under the parapet
    for face, inward in ((x0, +1), (x1, -1)):
        n = int(Wd / 0.6)
        for i in range(n):
            yc = y0 + 0.3 + i * 0.6
            k.fbox("render_dark", "x", face, inward, yc - 0.12, yc + 0.12, -0.05, 0.0, H - 0.9 + (i % 2) * 0.12, H - 0.7 + (i % 2) * 0.12)
    if towers:
        th = H + 2.6
        for cx, cy in ((x0, y0), (x0, y1), (x1, y0), (x1, y1)):
            a = 1.6
            k.box("render", cx - a, cx + a, cy - a, cy + a, 0.02, th)
            k.box("render", cx - a - 0.12, cx + a + 0.12, cy - a - 0.12, cy + a + 0.12, th - 0.9, th - 0.75)
            crenellation(k, cx - a, cx + a, cy - a, cy + a, th, 0.45, 0.4, 0.55, 0.3)
            k.fbox("render_dark", "x", cx - a if cx < 0 else cx + a, +1 if cx < 0 else -1, cy - 0.25, cy + 0.25, -0.01, 0.12, th - 2.4, th - 1.4)


# ---------------------------------------------------------------------------
# Lot dressing (built per lot, draped on the graded ground)
# ---------------------------------------------------------------------------
def lot_dressing(kd, lot_poly_local, house_local, pool_local, mats_used):
    """Hedges on the lot edges, stone wall on the street edge, terrace paving and the pool.
    All coordinates in plan-local metres (u, v); kd collects world-space boxes later."""
    pass


def type_collection(name):
    import bpy
    col = C.child_collection("03_ARCHITECTURE", name)
    return col


def build_type(name, fn, materials):
    k = Kit()
    fn(k)
    col = type_collection(name)
    k.build(name, col, materials)
    return col


def place(col_src, name, world_xy, z, rot, target):
    import bpy
    C.remove_object(name)
    inst = bpy.data.objects.new(name, None)
    inst.instance_type = "COLLECTION"
    inst.instance_collection = col_src
    inst.location = (float(world_xy[0]), float(world_xy[1]), float(z))
    inst.rotation_euler = (0, 0, rot)
    target.objects.link(inst)
    return inst


def build(materials):
    import bpy
    M = materials
    G = C.SITE_GRADED
    yaw = C.yaw()
    lift = 0.18 + 0.30                          # lawn top + plinth to finished floor

    types = {
        "TYPE_DUPLEX_PAIR": build_type("TYPE_DUPLEX_PAIR", build_duplex_pair, M),
        "TYPE_VILLA_B": build_type("TYPE_VILLA_B", villa_r1, M),
        "TYPE_VILLA_C": build_type("TYPE_VILLA_C", lambda k: villa_rdc(k, 12.4, 11.6, 4.2), M),
        "TYPE_VILLA_A": build_type("TYPE_VILLA_A", lambda k: villa_rdc(k, 16.4, 13.4, 5.0), M),
    }
    placed = C.child_collection("03_ARCHITECTURE", "PLACED_BUILDINGS")
    count = {}
    records = []

    def put(tname, cx_px, cy_px, idx, extra_rot=0.0):
        w = C.plan_to_world([(cx_px, cy_px)])[0]
        z = float(G(np.array([w]))[0]) + lift
        nm = f"{tname[5:]}_{idx:03d}"
        place(types[tname], nm, w, z, yaw + extra_rot, placed)
        count[tname] = count.get(tname, 0) + 1
        records.append((nm, tname, w, z))

    i = 0
    for tr, pairs in D.DUPLEX_PAIRS.items():
        for b in pairs:
            i += 1
            put("TYPE_DUPLEX_PAIR", (b[0] + b[1]) / 2, (b[2] + b[3]) / 2, i)
    lots = []
    for tr, ty, cols, rows in D.LOT_GRIDS:
        for (x0, x1) in cols:
            for (y0, y1) in rows:
                lots.append((tr, ty, x0, x1, y0, y1))
    for j, (tr, ty, x0, x1, y0, y1) in enumerate(lots):
        m = 1.0 / D.M_PER_PX
        if ty == "B":
            cx = x1 - (1.6 + 8.6 / 2) * m
        else:
            cx = x1 - (1.6 + 11.6 / 2) * m
        put("TYPE_VILLA_" + ty, cx, (y0 + y1) / 2, j + 1)
    for j, ((x0, x1), (y0, y1)) in enumerate(D.VILLA_A_LOTS):
        put("TYPE_VILLA_A", x1 - (2.0 + 13.4 / 2) / D.M_PER_PX, (y0 + y1) / 2, j + 1)

    # public buildings (unique, built in place)
    for name, b, lv, style in D.PUBLIC_BUILDINGS:
        (cx, cy), (su, sv) = C.plan_box_world(b)
        k = Kit()
        if style == "light":
            k.box("render_dark", -su / 2, su / 2, -sv / 2, sv / 2, -1.0, 0.02)
            k.box("terrace", -su / 2, su / 2, -sv / 2, sv / 2, 0.02, 0.15)
            k.pergola(-su / 2, su / 2, -sv / 2, sv / 2, 0.15, 3.0)
        else:
            kasbah(k, sv, su, lv, towers=(style == "kasbah_towers" or "HOTEL" in name or "PAVILLON" in name),
                   portal=("RECEPTION" in name or "PAVILLON" in name))
        col = C.child_collection("03_ARCHITECTURE", "PUBLIC_" + name)
        z = float(G(np.array([[cx, cy]]))[0]) + lift
        obs = k.build("PUB_" + name, col, M)
        for ob in obs:
            ob.location = (cx, cy, z)
            ob.rotation_euler = (0, 0, yaw)
        records.append(("PUB_" + name, style, (cx, cy), z))
    C.BUILDING_RECORDS = records
    C.TYPES = types
    # hide the source type collections from the view layer (instances still render)
    for tname, colx in types.items():
        lc = bpy.context.view_layer.layer_collection.children["03_ARCHITECTURE"].children[tname]
        lc.exclude = True
    return count
