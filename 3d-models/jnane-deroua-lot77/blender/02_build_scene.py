"""
02_build_scene — Jnane Deroua lot N°77: villa converted into a kindergarten (exterior only).

    python 02_build_scene.py [--render all|front,left,rear,aerial] [--samples 64] [--pct 100]

Source: the signed permit drawing (planche 1/1, 1/100, "AMENAGEMENT + MODIFICATION D'UNE VILLA EN
MATERNELLE", architect J. Yassir), read from the client's DWG in millimetres. The modified (à
modifier) plans and the three drawn facades are used; data/facades.json comes from 01_parse_dwg.py.

Building frame (metres): x = 0 left facade .. 9.00 right party wall; y = 0 main facade (entrance)
.. 9.90 rear facade; z = 0 street / garden level, RDC floor +0.50, first floor +4.40,
roof slab +7.49, acrotère +8.19 (all read off the facades and the coupe A-A).

Status of what is not on the drawing: right side = party wall on the plot boundary (the
neighbouring house is not modelled); no gate is drawn in the front wall opening; street and
sidewalk outside the plot are context only.
"""
import json
import math
import os
import sys

import bpy  # noqa: I001  (bpy must be imported before bmesh)
import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = json.load(open(os.path.join(HERE, "data", "facades.json")))

# ---- dimensions read off the plans (m) --------------------------------------------------------
W, D = 9.00, 9.90                    # RDC footprint (plan RDC à modifier: 9.00 x 9.90)
PARTY = 0.20                         # right party wall on the plot boundary
Z_RDC = 0.50                         # RDC floor (3 steps x 16.7 cm on the main facade)
Z_ET = 4.40                          # first floor / RDC roof (balcony band top on the main facade)
Z_ROOF = 7.49                        # roof slab top (acrotère 0.70 below the top line)
Z_TOP = 8.19                         # top of acrotère (all three facades)
ET_FRONT_X = 3.72                    # first floor: front wall at y = 0 for x < 3.72 ...
ET_RECESS = 0.80                     # ... and recessed 0.80 m for x > 3.72
BALC_X1 = 6.30                       # balcony (V/TERRASSE) x 3.72 .. 6.30, y 0 .. 0.80
NOTCH_X0, NOTCH_Y0 = 6.85, 6.54      # open courtyard on the RDC roof, rear right (1.90+0.20 x 3.36)
PLOT_X0, PLOT_X1 = -4.00, 9.00       # plot 13.00 x 18.50: setback 4.00 on the left
PLOT_Y0, PLOT_Y1 = -4.20, 14.30      # front setback 4.20, rear 4.40
GATE_X0, GATE_X1 = 4.40, 6.02        # entrance path / opening in the front wall
DOOR_U0, DOOR_U1, DOOR_Z1 = 4.328, 6.128, 2.99
WALL_H = 2.50                        # plot walls (2.40-2.52 on the facades)


def srgb(c):
    c = [v / 255.0 for v in c[:3]]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


# ---- materials -------------------------------------------------------------------------------
MATS = {}


def mat(name, rgb, rough=0.6, metal=0.0, bump=0.0, emit=None):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = srgb(rgb) if max(rgb) > 1.0 else tuple(rgb) + (1.0,)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord")                 # object coordinates = metres (thin faces stay clean)
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = 40.0
        n.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump * 0.35
        bp.inputs["Distance"].default_value = 0.002
        nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = b.inputs["Base Color"].default_value
    MATS[name] = m
    return m


def colour_mat(rgb, kind):
    return mat(f"{kind}_{rgb[0]:03d}_{rgb[1]:03d}_{rgb[2]:03d}", rgb, rough=0.35 if kind == "Block" else 0.45)


M_RENDER = lambda: mat("Render_White_Smooth", (238, 236, 230), 0.85, bump=0.15)   # "enduit lisse blanc" (2008 legend)
M_FRAME = lambda: mat("Frame_Aluminium_Beige", (216, 204, 181), 0.35, 0.3)         # menuiserie, colour from the DWG
M_GLASS = lambda: mat("Glass_Exterior", (0.04, 0.055, 0.065), 0.04)
M_DARK = lambda: mat("Interior_Dark", (0.03, 0.028, 0.025), 0.9)
M_ROOF = lambda: mat("Roof_Waterproofing_Grey", (150, 148, 142), 0.9)
M_COPING = lambda: mat("Coping_White", (246, 245, 240), 0.6)
M_RAIL = lambda: mat("Railing_Metal", (139, 139, 146), 0.35, 0.8)
M_RAILP = lambda: mat("Railing_Panel", (207, 207, 211), 0.4, 0.2)
M_LAWN = lambda: mat("Garden_Lawn", (92, 128, 60), 0.9, bump=0.4)
M_PAVE = lambda: mat("Path_Pavers", (196, 182, 160), 0.85, bump=0.3)
M_WOOD = lambda: mat("Pergola_Wood", (172, 132, 92), 0.7)
M_STREET = lambda: mat("Street_Asphalt", (70, 70, 72), 0.9, bump=0.2)
M_SIDEWALK = lambda: mat("Sidewalk_Concrete", (190, 186, 178), 0.85, bump=0.2)
M_SOIL = lambda: mat("Ground_Soil", (168, 150, 120), 0.95, bump=0.3)


# ---- mesh helpers ----------------------------------------------------------------------------
COL = {}


def collection(name):
    if name not in COL:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COL[name] = c
    return COL[name]


def obj_from_bm(name, bm, m, col):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    me.materials.append(m)
    collection(col).objects.link(ob)
    return ob


def box_bm(bm, x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    v = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f])


def box(name, x0, x1, y0, y1, z0, z1, m, col="BUILDING"):
    bm = bmesh.new()
    box_bm(bm, x0, x1, y0, y1, z0, z1)
    return obj_from_bm(name, bm, m, col)


def prism(name, pts, z0, z1, m, col="BUILDING"):
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in pts]
    top = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, m, col)


def boolean(target, cutter, op="DIFFERENCE"):
    md = target.modifiers.new("cut", "BOOLEAN")
    md.operation = op
    md.solver = "EXACT"
    md.object = cutter
    try:
        md.material_mode = "TRANSFER"
    except AttributeError:
        pass
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


# ---- facade placement ------------------------------------------------------------------------
def plane_of(face, u0, z0):
    """Wall plane a facade element sits on (the elevation flattens the first-floor recesses)."""
    if face == "front":
        return ET_RECESS if (z0 >= Z_ET - 0.05 and u0 >= ET_FRONT_X - 0.02) else 0.0
    if face == "rear":
        return NOTCH_Y0 if (z0 >= Z_ET - 0.05 and u0 >= NOTCH_X0) else D
    return 0.0


def fbox(bm, face, u0, u1, z0, z1, d0, d1, plane=None):
    """Box on a facade: u along the facade, z up, d outward from the wall face (negative = into the wall)."""
    p = plane_of(face, u0, z0) if plane is None else plane
    if face == "front":
        box_bm(bm, u0, u1, p - d1, p - d0, z0, z1)
    elif face == "rear":
        box_bm(bm, u0, u1, p + d0, p + d1, z0, z1)
    else:                                            # left facade, plane x = 0, outward -x
        box_bm(bm, -d1, -d0, u0, u1, z0, z1)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"

    # 1. massing --------------------------------------------------------------------------------
    rdc = box("RDC_Volume", 0.0, W - PARTY, 0.0, D, 0.0, Z_ET, M_RENDER())
    et_pts = [(0, 0), (ET_FRONT_X, 0), (ET_FRONT_X, ET_RECESS), (W - PARTY, ET_RECESS), (W - PARTY, NOTCH_Y0),
              (NOTCH_X0, NOTCH_Y0), (NOTCH_X0, D), (0, D)]
    et = prism("Etage_Volume", et_pts, Z_ET, Z_ROOF, M_RENDER())
    box("Party_Wall_Right", W - PARTY, W, 0.0, D, 0.0, Z_TOP, M_RENDER())
    # acrotère round the first floor: one ring, 0.20 thick (overlapping boxes render black in Cycles)
    from shapely.geometry import Polygon as _P
    ring = _P(et_pts).difference(_P(et_pts).buffer(-0.20, join_style=2))
    bm = bmesh.new()
    outer = list(ring.exterior.coords)[:-1]
    inner = list(ring.interiors[0].coords)[:-1]
    for loop in (outer, inner):                                  # vertical faces of both loops
        bv = [bm.verts.new((x, y, Z_ROOF)) for x, y in loop]
        tv = [bm.verts.new((x, y, Z_TOP)) for x, y in loop]
        for i in range(len(loop)):
            j = (i + 1) % len(loop)
            bm.faces.new([bv[i], bv[j], tv[j], tv[i]])
    # top and bottom caps: triangulate the ring polygon
    from shapely.ops import triangulate as _tri
    for t in _tri(ring):
        if not ring.contains(t.representative_point()):
            continue
        pts = list(t.exterior.coords)[:-1]
        for z in (Z_ROOF, Z_TOP):
            bm.faces.new([bm.verts.new((x, y, z)) for x, y in pts])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj_from_bm("Acrotere", bm, M_RENDER(), "BUILDING")
    prism("Roof_Finish", [(0.2, 0.2), (ET_FRONT_X - 0.2, 0.2), (ET_FRONT_X - 0.2, ET_RECESS + 0.2), (W - PARTY, ET_RECESS + 0.2),
                          (W - PARTY, NOTCH_Y0 - 0.2), (NOTCH_X0 - 0.2, NOTCH_Y0 - 0.2), (NOTCH_X0 - 0.2, D - 0.2), (0.2, D - 0.2)],
          Z_ROOF, Z_ROOF + 0.01, M_ROOF())
    # RDC roof terraces (front ledge and rear courtyard)
    box("RDC_Roof_Front", ET_FRONT_X, W - PARTY, 0.0, ET_RECESS, Z_ET, Z_ET + 0.01, M_ROOF())
    box("RDC_Roof_Courtyard", NOTCH_X0, W - PARTY, NOTCH_Y0, D - 0.20, Z_ET, Z_ET + 0.01, M_ROOF())
    box("Courtyard_Edge_Coping", NOTCH_X0, W - PARTY, D - 0.20, D, Z_ET + 0.01, Z_ET + 0.12, M_COPING())

    # 2. openings: windows + door ---------------------------------------------------------------
    cut_rdc, cut_et = bmesh.new(), bmesh.new()
    frames, glass, interior = bmesh.new(), bmesh.new(), bmesh.new()
    windows = []
    for face, fd in DATA.items():
        for w in fd["windows"]:
            windows.append((face, w["opening"], w["panes"]))
    # door of the main facade: two glazed leaves (DWG door frame lines)
    windows.append(("front", [DOOR_U0, Z_RDC, DOOR_U1, DOOR_Z1],
                    [[DOOR_U0 + 0.10, Z_RDC + 0.12, (DOOR_U0 + DOOR_U1) / 2 - 0.04, DOOR_Z1 - 0.10],
                     [(DOOR_U0 + DOOR_U1) / 2 + 0.04, Z_RDC + 0.12, DOOR_U1 - 0.10, DOOR_Z1 - 0.10]]))
    frame_objs = []
    for k, (face, (u0, z0, u1, z1), panes) in enumerate(windows):
        p = plane_of(face, u0, z0)
        target = cut_rdc if z1 <= Z_ET + 0.01 else cut_et
        fbox(target, face, u0, u1, z0, z1, -0.40, 0.10, p)
        fbox(interior, face, u0, u1, z0, z1, -0.36, -0.34, p)
        # frame: opening slab minus the panes
        fbm = bmesh.new()
        fbox(fbm, face, u0, u1, z0, z1, -0.16, -0.10, p)
        fo = obj_from_bm(f"Frame_{face}_{k:02d}", fbm, M_FRAME(), "WINDOWS")
        cbm = bmesh.new()
        for (a0, b0, a1, b1) in panes:
            fbox(cbm, face, a0, a1, b0, b1, -0.20, -0.06, p)
            fbox(glass, face, a0, a1, b0, b1, -0.135, -0.125, p)
        co = obj_from_bm("tmp_cut", cbm, M_FRAME(), "WINDOWS")
        boolean(fo, co)
        frame_objs.append(fo)
    cr = obj_from_bm("cut_rdc", cut_rdc, M_RENDER(), "BUILDING")
    ce = obj_from_bm("cut_et", cut_et, M_RENDER(), "BUILDING")
    boolean(rdc, cr)
    boolean(et, ce)
    obj_from_bm("Window_Glass", glass, M_GLASS(), "WINDOWS")
    obj_from_bm("Window_Interior_Backdrop", interior, M_DARK(), "WINDOWS")

    # 3. facade colour: window surrounds and blocks ----------------------------------------------
    for face, fd in DATA.items():
        for s in fd["surrounds"]:
            (a0, b0, a1, b1), (i0, j0, i1, j1) = s["outer"], s["inner"]
            bm = bmesh.new()
            p = plane_of(face, a0, b0 + 0.3)
            for (u0, z0, u1, z1) in ((a0, b0, a1, j0), (a0, j1, a1, b1), (a0, j0, i0, j1), (i1, j0, a1, j1)):
                fbox(bm, face, u0, u1, z0, z1, 0.0, 0.025, p)
            obj_from_bm(f"Surround_{face}_{a0:.2f}_{b0:.2f}", bm, colour_mat(s["rgb"], "Surround"), "FACADE_COLOUR")
        groups = {}
        for b in fd["blocks"]:
            groups.setdefault(tuple(b["rgb"]), []).append(b["rect"])
        for rgb, rects in groups.items():
            bm = bmesh.new()
            for (u0, z0, u1, z1) in rects:
                if face == "left" and (u1 > D + 0.01 or u0 < -0.01):
                    continue
                fbox(bm, face, u0, u1, z0, z1, 0.0, 0.035)
            obj_from_bm(f"Blocks_{face}_{rgb[0]:03d}_{rgb[1]:03d}_{rgb[2]:03d}", bm, colour_mat(list(rgb), "Block"), "FACADE_COLOUR")

    # 4. balcony (V/TERRASSE) with its railing panels, door canopy and steps ----------------------
    box("Balcony_Parapet", ET_FRONT_X, BALC_X1, 0.0, 0.15, Z_ET + 0.01, Z_ET + 0.60, M_RENDER())
    box("Balcony_Parapet_Side", BALC_X1 - 0.15, BALC_X1, 0.15, ET_RECESS, Z_ET + 0.01, Z_ET + 0.60, M_RENDER())
    rail = bmesh.new(); panel = bmesh.new()
    for (u0, z0, u1, z1) in DATA["front"]["rails"]:
        fbox(panel, "front", u0 + 0.02, u1 - 0.02, z0, z1 - 0.03, 0.04, 0.06, 0.0)
        fbox(rail, "front", u0, u1, z1 - 0.04, z1, 0.02, 0.08, 0.0)
        fbox(rail, "front", u0, u0 + 0.04, z0, z1, 0.02, 0.08, 0.0)
    fbox(rail, "front", BALC_X1 - 0.12, BALC_X1 - 0.08, Z_ET + 0.6, Z_ET + 1.03, -0.75, 0.0, 0.0)
    obj_from_bm("Balcony_Railing", rail, M_RAIL(), "BUILDING")
    obj_from_bm("Balcony_Railing_Panels", panel, M_RAILP(), "BUILDING")
    box("Door_Canopy", DOOR_U0 - 0.20, DOOR_U1 + 0.20, -0.55, 0.0, DOOR_Z1 + 0.02, DOOR_Z1 + 0.10, M_FRAME())
    for i in range(3):                                          # 3 steps x 16.7 cm, 30 cm going
        box(f"Entrance_Step_{i + 1}", DOOR_U0 - 0.10, DOOR_U1 + 0.10, -0.30 * (3 - i), -0.30 * (2 - i), 0.02, Z_RDC * (i + 1) / 3, M_PAVE(), "SITE")

    # 5. plot: lawn, walls, path, pergola ----------------------------------------------------------
    box("Garden_Lawn", PLOT_X0, PLOT_X1, PLOT_Y0, PLOT_Y1, -0.05, 0.0, M_LAWN(), "SITE")
    box("Entrance_Path", GATE_X0, GATE_X1, PLOT_Y0 + 0.2, -0.9, 0.0, 0.02, M_PAVE(), "SITE")
    segs = [(PLOT_X0, PLOT_X0 + 0.2, PLOT_Y0, PLOT_Y1),             # left (full length)
            (PLOT_X0 + 0.2, GATE_X0, PLOT_Y0, PLOT_Y0 + 0.2),           # front, left of the opening
            (GATE_X1, PLOT_X1, PLOT_Y0, PLOT_Y0 + 0.2),                 # front, right of the opening
            (W - PARTY, W, PLOT_Y0 + 0.2, 0.0),                         # right boundary, front yard
            (PLOT_X0 + 0.2, PLOT_X1, PLOT_Y1 - 0.2, PLOT_Y1),           # rear
            (W - PARTY, W, D, PLOT_Y1 - 0.2)]                           # right boundary, rear yard
    walls, cop = bmesh.new(), bmesh.new()
    for (x0, x1, y0, y1) in segs:
        box_bm(walls, x0, x1, y0, y1, 0.0, WALL_H)
        box_bm(cop, x0, x1, y0, y1, WALL_H, WALL_H + 0.05)
    obj_from_bm("Plot_Walls", walls, M_RENDER(), "SITE")
    obj_from_bm("Plot_Wall_Copings", cop, M_COPING(), "SITE")
    box("Entrance_Path_Gate", GATE_X0, GATE_X1, PLOT_Y0, PLOT_Y0 + 0.2, 0.0, 0.02, M_PAVE(), "SITE")
    # pergola over the entrance path (plan: posts both sides of the path; facade gauche: beams +2.51 / +2.89)
    perg = bmesh.new()
    for x in (GATE_X0 - 0.10, GATE_X1 + 0.10):
        for y in (-0.37, -3.67):
            box_bm(perg, x - 0.06, x + 0.06, y - 0.06, y + 0.06, 0.0, 2.75)
        box_bm(perg, x - 0.04, x + 0.04, -4.20, -0.25, 2.55, 2.75)
    y = -0.40
    while y > -4.15:
        box_bm(perg, GATE_X0 - 0.30, GATE_X1 + 0.30, y - 0.03, y + 0.03, 2.75, 2.89)
        y -= 0.35
    obj_from_bm("Entrance_Pergola", perg, M_WOOD(), "SITE")

    # 6. context: sidewalk, street, ground beyond the plot ---------------------------------------
    box("Sidewalk", PLOT_X0 - 20, PLOT_X1 + 20, PLOT_Y0 - 2.0, PLOT_Y0, 0.0, 0.12, M_SIDEWALK(), "CONTEXT")
    box("Street", PLOT_X0 - 20, PLOT_X1 + 20, PLOT_Y0 - 9.0, PLOT_Y0 - 2.0, -0.05, 0.0, M_STREET(), "CONTEXT")
    gnd = box("Ground_Beyond", -60, 70, -60, 80, -0.10, -0.06, M_SOIL(), "CONTEXT")

    # 7. light + cameras ----------------------------------------------------------------------------
    world = bpy.data.worlds.new("Sky")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(38)
    sky.sun_rotation = math.radians(215)
    sky.altitude = 100
    nt.links.new(sky.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    nt.nodes["Background"].inputs["Strength"].default_value = 0.22
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 3.2
    sun.angle = math.radians(0.6)
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (math.radians(90 - 38), 0, math.radians(215) + math.pi / 2)   # same direction as the sky sun (front-left)
    collection("LIGHT").objects.link(so)
    from mathutils import Vector
    cams = {
        "CAM_FRONT_3Q": ((-9.5, -15.5, 1.7), (4.5, 3.0, 4.0), 24),
        "CAM_FRONT": ((4.5, -16.0, 1.6), (4.5, 2.0, 3.9), 28),
        "CAM_LEFT": ((-15.0, 3.0, 5.2), (2.0, 4.6, 3.9), 26),
        "CAM_REAR": ((-7.0, 25.0, 7.5), (4.0, 7.5, 4.2), 26),
        "CAM_AERIAL": ((-18.0, -20.0, 20.0), (3.5, 5.0, 2.5), 28),
    }
    for nm, (pos, tgt, lens) in cams.items():
        c = bpy.data.cameras.new(nm)
        c.lens = lens
        c.clip_end = 1000
        o = bpy.data.objects.new(nm, c)
        o.location = pos
        o.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        collection("CAMERAS").objects.link(o)
    sc.camera = bpy.data.objects["CAM_FRONT_3Q"]
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = -1.0                             # keeps the drawing's saturated block colours
    return frame_objs


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    render = args[args.index("--render") + 1] if "--render" in args else ""
    samples = int(args[args.index("--samples") + 1]) if "--samples" in args else 64
    pct = int(args[args.index("--pct") + 1]) if "--pct" in args else 100
    build()
    sc = bpy.context.scene
    out = os.path.join(ROOT, "Jnane_Deroua_Lot77_Maternelle.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print("SAVED", out)
    if render:
        names = [o.name for o in bpy.data.collections["CAMERAS"].objects] if render == "all" else render.split(",")
        os.makedirs(os.path.join(ROOT, "renders"), exist_ok=True)
        sc.cycles.samples = samples
        sc.render.resolution_percentage = pct
        sc.render.image_settings.file_format = "JPEG"
        sc.render.image_settings.quality = 92
        for n in names:
            sc.camera = bpy.data.objects[n]
            sc.render.filepath = os.path.join(ROOT, "renders", n + ".jpg")
            bpy.ops.render.render(write_still=True)
            print("RENDERED", n)


main()
