"""
12_villa_b — villa type B of Tranche 2, from 5-VILLA_TYPE_B.DWG (permis de construire: RDC, ETAGE,
TERRASSE, the four façades, coupes A-A and B-B), dressed like the villas of Tranche 1 (client 21-10:
"nfs designs and style et les couleurs").

Local frame (metres): the plot of the drawing, x 0-12.20 across (kitchen wing on the left seen from the
garden), y from the pool end (0.40) to the street (20.10); z = 0 at the house pad, as in 02_duplex.

From the drawing:
  RDC +0.20: séjour + S.A.M. and salon marocain across the rear (4-leaf glazing and a French door onto
    the terrace and the pool), kitchen wing at the front with its terrace, the entrance between the
    kitchen and the stair; hall, L.T., stair.
  ETAGE +3.90: three bedrooms and two bathrooms, the 'Manzah' balcony at the rear, the front terrace
    over the kitchen's, the open terrace over the salon marocain, the void over the entrance hall.
  TERRASSE +7.10, acrotère +8.20 with mashrabiya panels, stair cage to +9.90 / +10.10, skylight over
    the entrance void. Piscine (6.40 x 4.25 m, N = -1.60) behind the house.
Openings: positions from the RDC / ETAGE plans (gaps in the wall lines), heights from the façades.

Tranche 1 style: the villas' sand render, taupe stone surrounds, beige aluminium frames, sheer curtains,
the salon glazing set back in a stone reveal with the lit salon behind, rows of square niches, the
cornice of the villas (grey ledge / ochre band / grey ledge) and the rounded acrotère coping, the horned
crown of the stair cage, timber pergolas over the étage terraces, jade-green pool tiles with a white coping.
The voile (shade sail) the drawing puts over the front terrace is a timber pergola over the étage's front
balcony here (client 22-10: none over the ground-floor terrace).
"""
import importlib.util
import math
import os

from shapely.affinity import translate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

L = globals()["L"]
C = L.C
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t2_dpx_b", os.path.join(HERE, "02_duplex.py"))
D = importlib.util.module_from_spec(_spec)
D.__dict__["L"] = L
_spec.loader.exec_module(D)                  # the villa machinery of Tranche 1 (walls, openings, details)

Z_FL, Z1, Z2 = 0.20, 3.90, 7.10
Z_ACRO, Z_CW, Z_CTOP = 8.20, 9.90, 10.10
COP = D.COP
PLOT = box(0.0, 0.40, 12.20, 20.10)
RDC = Polygon([(1.03, 7.68), (8.54, 7.68), (8.54, 8.38), (12.22, 8.38), (12.22, 16.09), (5.47, 16.09),
               (5.47, 18.11), (1.03, 18.11)])
ET = Polygon([(1.03, 7.68), (8.54, 7.68), (8.54, 10.89), (12.22, 10.89), (12.22, 16.09), (5.47, 16.09),
              (5.47, 18.11), (1.03, 18.11)])
CAGE = box(7.85, 13.59, 12.02, 15.89)
SKY = box(5.62, 13.79, 7.65, 15.69)          # skylight over the entrance void
TER_R = box(8.54, 8.38, 12.22, 10.89)         # étage terrace over the salon marocain
FRONT_T = box(1.03, 18.11, 5.47, 20.11)       # étage terrace over the kitchen terrace
MANZAH = box(1.33, 6.38, 5.47, 7.68)          # rear balcony
POOL = box(1.50, 0.95, 7.90, 5.20)
POOL_DEPTH = 1.60
FOOT = unary_union([RDC, FRONT_T, MANZAH])    # kept clear of trees
REAR = box(1.03, 5.90, 12.22, 7.68).union(box(8.54, 7.68, 12.22, 8.38))   # terrace behind the séjour
FRONT_PAVE = unary_union([box(1.28, 18.11, 5.22, 19.86), box(5.47, 16.09, 7.60, 18.11), box(7.38, 16.09, 12.22, 19.40)])
COMPACT_DY = 1.50        # the compact model: the pool 1.50 m nearer the house (1 m from it, as the plan de masse draws it)


def ground(compact=False):
    """The pool, the deck round it and the rear terrace, and all the model builds on the ground."""
    dy = COMPACT_DY if compact else 0.0
    pool = translate(POOL, 0.0, dy)
    deck = unary_union([REAR, pool.buffer(0.80, join_style=2).intersection(box(0.0, PLOT.bounds[1] + dy, 12.20, 20.10))])
    return pool, deck, unary_union([RDC, deck, FRONT_PAVE, box(1.03, 18.11, 5.47, 20.11)])


_, DECK, HARD = ground()
op, niche = D.op, D.niche


def _niches(axis, c, a, b, z0, z1, avoid=()):
    out, u = [], a
    while u <= b + 1e-6:
        if not any(p - 0.25 <= u <= q + 0.25 for p, q in avoid):
            out.append(niche(axis, c, u, z0, z1))
        u += 1.0
    return out


OPENINGS = [
    # RDC
    {**op("y", 7.68, 2.11, 7.43, Z_FL, 2.70, "baie", 4), "rev": 0.36, "rev_mat": "surround"},   # séjour onto the terrace
    op("y", 8.38, 9.09, 11.22, Z_FL, 2.70, "slider", 2),                    # salon marocain, French door
    op("y", 16.09, 5.94, 7.38, Z_FL, 2.75, "door"),                         # entrance
    op("y", 16.09, 10.45, 11.05, 1.40, 3.10, "window"),                     # stair
    op("y", 18.11, 2.00, 4.60, 1.00, 2.40, "window", 2),                    # kitchen onto its terrace
    *[op("x", 1.03, a, b, 1.10, 2.70, "window") for a, b in ((9.93, 10.38), (11.08, 11.53), (14.34, 14.79), (15.49, 15.94))],
    op("x", 1.03, 16.54, 17.43, Z_FL, 2.45, "door"),                        # kitchen side door
    op("x", 12.22, 10.05, 12.05, 0.95, 2.55, "window", 2),                  # salon marocain, side
    op("x", 12.22, 13.95, 15.55, 1.60, 3.30, "window", 3),                  # stair
    # ETAGE
    op("y", 7.68, 2.28, 4.78, Z1 + 0.02, 6.20, "slider", 2),                # bedroom onto the Manzah
    op("y", 7.68, 5.53, 7.53, 4.80, 6.20, "window", 2),                     # bedroom III
    op("x", 8.54, 9.00, 10.20, 4.80, 6.20, "window", 2),                    # bedroom III onto the terrace
    op("y", 10.89, 9.15, 10.05, Z1 + 0.02, 6.20, "slider", 1),              # onto the terrace
    op("y", 10.89, 10.65, 11.40, 4.80, 6.20, "window"),
    *[op("x", 1.03, a, b, 4.50, 6.40, "window") for a, b in ((9.93, 10.38), (11.08, 11.53), (14.34, 14.79), (15.49, 15.94))],
    op("y", 18.11, 2.14, 4.22, Z1 + 0.02, 6.10, "slider", 2),               # bedroom onto the front terrace
    op("y", 16.09, 9.35, 9.95, 4.30, 5.90, "window"),                       # stair
    op("x", 12.22, 13.95, 15.55, 4.85, 6.40, "window", 3),                  # stair
    op("x", CAGE.bounds[0], 14.20, 15.00, Z2 + 0.02, 9.00, "roofdoor"),     # stair cage, roof door
    # square niches under the cornice and on the stair cage
    *_niches("y", 7.68, 1.55, 8.05, 6.75, 6.95),
    *_niches("y", 18.11, 1.55, 5.05, 6.75, 6.95),
    *_niches("y", 16.09, 5.95, 11.85, 6.75, 6.95),
    *_niches("y", 10.89, 9.05, 11.85, 6.75, 6.95),
    *_niches("x", 1.03, 8.20, 17.60, 6.75, 6.95),
    *_niches("x", 12.22, 11.30, 15.80, 6.75, 6.95, avoid=((13.95, 15.55),)),
    *_niches("x", 8.54, 8.20, 10.40, 6.75, 6.95),
    *_niches("y", CAGE.bounds[3], 8.45, 11.45, 9.30, 9.48),
]
BREAK_X = sorted({1.03, 5.47, 8.54, 12.22, CAGE.bounds[0], CAGE.bounds[2]})
BREAK_Y = sorted({7.68, 8.38, 10.89, 16.09, 18.11, CAGE.bounds[1], CAGE.bounds[3]})
PANELS = {   # mashrabiya panels on the acrotère (façades): (axis, c, u0, u1)
    "acro": [("y", 18.11, 1.92, 4.52), ("y", 7.68, 1.90, 4.40), ("y", 7.68, 5.50, 8.00), ("y", 10.89, 9.00, 11.50),
             ("x", 1.03, 8.40, 10.90), ("x", 1.03, 11.70, 14.20), ("x", 1.03, 15.00, 17.60), ("x", 12.22, 11.60, 13.40)],
}


def rdc_top(x, y):
    """RDC faces stop at the étage floor, or carry on as the parapet of the open étage terrace."""
    if x > 8.54 + 1e-6 and y < 10.89 - 1e-6:
        return Z1 + 1.00 - COP
    return Z1


def panel(mb, axis, c, u0, u1, z0, z1, out_n):
    """Mashrabiya panel on a wall face: a taupe frame and the timber lattice, 3 cm proud."""
    for (a0, a1, b0, b1, mat, d) in ((u0 - 0.08, u1 + 0.08, z0 - 0.08, z1 + 0.08, "surround", 0.03), (u0, u1, z0, z1, "mashrabiya", 0.05)):
        if axis == "y":
            mb.box(mat, a0, a1, min(c, c + out_n * d), max(c, c + out_n * d), b0, b1)
        else:
            mb.box(mat, min(c, c + out_n * d), max(c, c + out_n * d), a0, a1, b0, b1)


def _out_normal(poly, axis, c, u):
    """+1 / -1: the side of the face (axis, c) on which the outside of poly lies, near u."""
    from shapely.geometry import Point
    p = Point(u, c + 0.05) if axis == "y" else Point(c + 0.05, u)
    return -1.0 if poly.buffer(0.001).contains(p) else 1.0


def build(M, col, name="SRC_VILLA_B", compact=False):
    mb = C.MeshBuilder()
    D.OPENINGS, D.BREAK_X, D.BREAK_Y, D.RDC = OPENINGS, BREAK_X, BREAK_Y, RDC
    for p, q in D.edges(RDC):
        D.wall(mb, p, q, -1.00, rdc_top)
    for p, q in D.edges(ET):
        D.wall(mb, p, q, Z1, Z2)
    for p, q in D.edges(CAGE):
        D.wall(mb, p, q, Z2, Z_CW)

    # ---- floors of the terraces at the étage, the balconies -----------------------------------
    L.prism(mb, "terrace", TER_R, Z1 - 0.01, Z1, sides=False)
    for g in (FRONT_T, MANZAH):
        L.prism(mb, "villa", g, Z1 - 0.30, Z1 - 0.01)
        L.prism(mb, "terrace", g.buffer(-0.20, join_style=2), Z1 - 0.01, Z1, sides=False)
    # Manzah: solid parapet with a rounded coping, a planter along its edge
    mz = MANZAH.difference(MANZAH.buffer(-0.20, join_style=2)).difference(box(0, 7.60, 13, 8))
    L.prism(mb, "villa", mz, Z1, Z1 + 1.00 - COP)
    D.coping(mb, "villa", mz, Z1 + 1.00)
    bed = box(1.53, 6.58, 5.27, 7.08)
    L.prism(mb, "villa", bed.difference(bed.buffer(-0.08)), Z1, Z1 + 0.55)
    L.prism(mb, "soil", bed.buffer(-0.08), Z1, Z1 + 0.48, sides=False)
    # front terrace: side walls from the ground (a loggia over the kitchen terrace), parapet with a panel
    for g in (box(1.03, 18.11, 1.28, 20.11), box(5.22, 18.11, 5.47, 20.11)):
        L.prism(mb, "villa", g, -1.00, Z1 + 1.00 - COP)
        D.coping(mb, "villa", g, Z1 + 1.00)
    fp = box(1.28, 19.86, 5.22, 20.11)
    L.prism(mb, "villa", fp, Z1 - 0.30, Z1 + 0.30)
    L.prism(mb, "villa", box(1.28, 19.86, 1.55, 20.11), Z1 + 0.30, Z1 + 1.00 - COP)
    L.prism(mb, "villa", box(4.95, 19.86, 5.22, 20.11), Z1 + 0.30, Z1 + 1.00 - COP)
    L.prism(mb, "villa", box(1.28, 19.86, 5.22, 20.11), Z1 + 0.90, Z1 + 1.00 - COP)
    D.coping(mb, "villa", fp, Z1 + 1.00)
    mb.box("mashrabiya", 1.55, 4.95, 19.95, 20.02, Z1 + 0.30, Z1 + 0.90)
    # parapet panels of the open terrace (rear and side faces carry on from the RDC walls)
    panel(mb, "y", 8.38, 9.00, 11.70, Z1 + 0.20, Z1 + 0.75, -1.0)
    panel(mb, "x", 12.22, 8.80, 10.50, Z1 + 0.20, Z1 + 0.75, 1.0)
    D.coping(mb, "villa", unary_union([box(8.54, 8.38, 12.22, 8.58), box(12.02, 8.38, 12.22, 10.89)]), Z1 + 1.00)

    # ---- cornice, acrotère with the rounded coping, mashrabiya panels, roof ------------------------
    for z0, z1, pd, mat in [(7.22, 7.30, 0.13, "ledge"), (7.30, 7.46, 0.10, "band"), (7.46, 7.62, 0.16, "ledge")]:
        L.prism(mb, mat, ET.buffer(pd, join_style=2).difference(ET), z0, z1, bottom=True)
    ring = ET.difference(ET.buffer(-0.30, join_style=2)).difference(CAGE)
    L.prism(mb, "villa", ring, Z2, 7.62)
    soft = ET.buffer(-0.12, join_style=2).buffer(0.12, join_style=1)
    ring_s = soft.difference(ET.buffer(-0.30, join_style=2)).difference(CAGE)
    L.prism(mb, "villa", ring_s, 7.62, Z_ACRO - 0.12)
    L.prism(mb, "villa", ring_s.buffer(-0.02, join_style=1), Z_ACRO - 0.12, Z_ACRO - 0.06)
    L.prism(mb, "villa", ring_s.buffer(-0.06, join_style=1), Z_ACRO - 0.06, Z_ACRO - 0.02)
    L.prism(mb, "villa", ring_s.buffer(-0.10, join_style=1), Z_ACRO - 0.02, Z_ACRO)
    for axis, c, u0, u1 in PANELS["acro"]:
        panel(mb, axis, c, u0, u1, 7.74, 8.02, _out_normal(ET, axis, c, 0.5 * (u0 + u1)))
    L.prism(mb, "terrace", ET.buffer(-0.30, join_style=2).difference(CAGE).difference(SKY), Z2 - 0.01, Z2, sides=False)
    # skylight over the entrance void: a stone curb and a glazed lantern
    L.prism(mb, "villa", SKY.buffer(0.15, join_style=2).difference(SKY), Z2, Z2 + 0.45)
    L.prism(mb, "ledge", SKY.buffer(0.19, join_style=2).difference(SKY), Z2 + 0.45, Z2 + 0.50)
    L.prism(mb, "glass", SKY, Z2 + 0.40, Z2 + 0.42, sides=False)
    for x in (SKY.bounds[0] + 0.5, 0.5 * (SKY.bounds[0] + SKY.bounds[2]), SKY.bounds[2] - 0.5):
        mb.box("bronze", x - 0.025, x + 0.025, SKY.bounds[1], SKY.bounds[3], Z2 + 0.42, Z2 + 0.46)

    # ---- stair cage: cornice, parapet, horned crown (as Tranche 1) ---------------------------------
    for z0, z1, pd, mat in [(Z_CW - 0.70, Z_CW - 0.62, 0.08, "ledge"), (Z_CW - 0.62, Z_CW - 0.48, 0.07, "band"),
                            (Z_CW - 0.48, Z_CW - 0.32, 0.13, "ledge")]:
        L.prism(mb, mat, CAGE.buffer(pd, join_style=2).difference(CAGE), z0, z1, bottom=True)
    cring = CAGE.difference(CAGE.buffer(-0.20, join_style=2))
    L.prism(mb, "villa", cring, Z_CW - 0.32, Z_CTOP - 0.08)
    D.coping(mb, "villa", cring, Z_CTOP, 0.08)
    L.prism(mb, "roof", CAGE.buffer(-0.20, join_style=2), Z_CW - 0.33, Z_CW - 0.32, sides=False)
    cx0, cy0, cx1, cy1 = CAGE.bounds
    us = [0.95 - 0.75 * k / 12 for k in range(13)]
    prof = Polygon([(0.0, Z_CTOP - 0.40), (0.95, Z_CTOP - 0.40)] + [(u, Z_CTOP + 0.36 * ((0.95 - u) / 0.75) ** 1.6) for u in us]
                   + [(0.07, Z_CTOP + 0.34), (0.0, Z_CTOP + 0.28)])
    prof_b = prof.intersection(box(0.20, 0.0, 1.0, 20.0))
    for xc, sx in ((cx0, 1), (cx1, -1)):
        for yc, sy in ((cy0, 1), (cy1, -1)):
            D.horn(mb, prof, lambda a, b, w, xc=xc, sx=sx, yc=yc, sy=sy: (xc + sx * a, yc + sy * w, b))
            D.horn(mb, prof_b, lambda a, b, w, xc=xc, sx=sx, yc=yc, sy=sy: (xc + sx * w, yc + sy * a, b))

    # ---- pergolas (timber): over the étage terrace and over the étage's front balcony ---------------
    T = "timber"
    x0, y0, x1, y1 = TER_R.bounds
    for x, y in ((x1 - 0.20, y0 + 0.25), (x1 - 0.20, y1 - 0.20)):
        mb.box(T, x - 0.07, x + 0.07, y - 0.07, y + 0.07, Z1, Z1 + 2.55)
    mb.box(T, x1 - 0.30, x1 - 0.10, y0 + 0.10, y1, Z1 + 2.55, Z1 + 2.75)
    mb.box(T, x0, x1 - 0.10, y0 + 0.15, y0 + 0.35, Z1 + 2.55, Z1 + 2.75)
    for k in range(int((y1 - y0 - 0.3) / 0.50) + 1):
        y = y0 + 0.35 + 0.50 * k
        mb.box(T, x0 + 0.02, x1 - 0.05, y - 0.03, y + 0.03, Z1 + 2.75, Z1 + 2.90)
    # client 22-10: no pergola over the front terrace on the ground; it goes over the étage's front balcony
    # (the terrace over the kitchen's, the bedroom's sliding door onto it), from the façade to its parapet
    px0, py0, px1, py1 = 1.28, 18.11, 5.22, 19.86
    for x in (px0 + 0.10, px1 - 0.10):
        mb.box(T, x - 0.07, x + 0.07, py1 - 0.17, py1 - 0.03, Z1 + 1.00, Z1 + 2.55)
    mb.box(T, px0, px1, py1 - 0.20, py1, Z1 + 2.55, Z1 + 2.75)
    mb.box(T, px0, px1, py0, py0 + 0.08, Z1 + 2.60, Z1 + 2.75)
    for k in range(int((px1 - px0) / 0.48) + 1):
        x = px0 + 0.14 + 0.48 * k
        if x < px1 - 0.05:
            mb.box(T, x - 0.03, x + 0.03, py0, py1 + 0.15, Z1 + 2.75, Z1 + 2.90)

    # ---- terraces, porch, pool -------------------------------------------------------------------
    POOL, DECK, _ = ground(compact)
    deck = DECK.difference(POOL.buffer(0.30, join_style=2))
    L.prism(mb, "terrace", deck, -0.40, Z_FL - 0.005)
    L.prism(mb, "coping", POOL.buffer(0.30, join_style=2).difference(POOL), -0.30, Z_FL)
    L.prism(mb, "tile_jade", POOL, -POOL_DEPTH - 0.05, -POOL_DEPTH + 0.15, sides=False)
    L.prism(mb, "tile_jade", POOL.buffer(0.01, join_style=2).difference(POOL.buffer(-0.01, join_style=2)), -POOL_DEPTH + 0.15, Z_FL - 0.02)
    L.prism(mb, "pool_water", POOL.buffer(-0.01, join_style=2), Z_FL - 0.17, Z_FL - 0.15, sides=False)
    for k in range(3):                                         # Roman steps in the corner by the house
        q = box(POOL.bounds[0], POOL.bounds[3] - 0.45 * (3 - k), POOL.bounds[0] + 1.6, POOL.bounds[3])
        L.prism(mb, "tile_jade", q, -POOL_DEPTH + 0.15, Z_FL - 0.20 - 0.40 * k, sides=True)
    L.prism(mb, "terrace", FRONT_PAVE, -0.40, Z_FL - 0.005)
    mb.box("coping_beige", 5.94, 7.38, 16.09, 16.45, -0.30, Z_FL + 0.01)    # door step

    obs = mb.build("VILLA_B", col, M)
    ob = L.join(obs, name)
    L.weld(ob, 0.0003)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


def mirrored(src, name):
    """The same villa mirrored across its plot (kitchen wing on the other side), faces turned back out."""
    import bmesh
    import bpy
    me = src.data.copy()
    me.name = name
    bm = bmesh.new()
    bm.from_mesh(me)
    for v in bm.verts:
        v.co.x = PLOT.bounds[2] - v.co.x
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    for c in src.users_collection:
        c.objects.link(ob)
    return ob
