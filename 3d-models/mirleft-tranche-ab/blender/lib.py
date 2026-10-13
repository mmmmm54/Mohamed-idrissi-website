"""
lib — shared helpers for the Mirleft Tranche A+B scene.

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


def uv_tiles(m):
    """Drive the brick texture of a tiles() material with UV (metres) instead of Object coords,
    so vertical cladding reads as tiles on every face."""
    nt = m.node_tree
    br = [n for n in nt.nodes if n.type == "TEX_BRICK"][0]
    tc = [n for n in nt.nodes if n.type == "TEX_COORD"][0]
    nt.links.new(tc.outputs["UV"], br.inputs["Vector"])
    return m


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
            for ring in [pg.exterior] + list(pg.interiors):
                c = list(ring.coords)
                ccw = ring.is_ccw
                inner = ring is not pg.exterior
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
