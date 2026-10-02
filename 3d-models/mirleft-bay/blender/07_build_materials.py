"""
07_build_materials — project material library (procedural PBR).

Status: every material here is APPROXIMATED (procedural) because the CC0 libraries
(Poly Haven / ambientCG) are blocked by this environment's network policy. Colours come from
the client's site photos (PROJECT_BIBLE §33). Physical scale: Object coordinates in metres.
IDs match specs/ASSET_REQUIREMENTS.md (M01...).

Poly Haven layer (client download, CC0): if a folder assets/textures/polyhaven/<slug>/ exists,
the matching material is rebuilt from those image maps (colour, roughness, height) with box
projection in Object space at true size (PH_MAP below). Missing folders keep the procedural
material, so the scene always builds.
"""
import os

C = globals()["C"]


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


class NB:
    """Tiny node-tree builder."""

    def __init__(self, mat):
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.x = 0
        self.out = self.n("ShaderNodeOutputMaterial")
        self.bsdf = self.n("ShaderNodeBsdfPrincipled")
        self.l(self.bsdf, "BSDF", self.out, "Surface")
        tc = self.n("ShaderNodeTexCoord")
        self.obj = tc.outputs["Object"]
        self.uv = tc.outputs["UV"]

    def n(self, kind, **props):
        node = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(node, k, v)
        node.location = (self.x, 0)
        self.x -= 220
        return node

    def l(self, a, ao, b, bi):
        a_out = a.outputs[ao] if isinstance(a, object) and hasattr(a, "outputs") else a
        self.nt.links.new(a_out if not isinstance(ao, int) else a.outputs[ao], b.inputs[bi])

    def link(self, sock, node, inp):
        self.nt.links.new(sock, node.inputs[inp])

    def noise(self, scale, detail=6, rough=0.55, vec=None, dim="3D"):
        t = self.n("ShaderNodeTexNoise", noise_dimensions=dim)
        t.inputs["Scale"].default_value = scale
        t.inputs["Detail"].default_value = detail
        t.inputs["Roughness"].default_value = rough
        self.link(vec if vec is not None else self.obj, t, "Vector")
        return t

    def ramp(self, sock, stops):
        r = self.n("ShaderNodeValToRGB")
        cr = r.color_ramp
        cr.elements[0].position, cr.elements[0].color = stops[0][0], stops[0][1]
        cr.elements[1].position, cr.elements[1].color = stops[-1][0], stops[-1][1]
        for pos, col in stops[1:-1]:
            e = cr.elements.new(pos)
            e.color = col
        self.link(sock, r, "Fac")
        return r

    def bump(self, height_sock, strength=0.3, distance=0.02, normal=None):
        b = self.n("ShaderNodeBump")
        b.inputs["Strength"].default_value = strength
        b.inputs["Distance"].default_value = distance
        self.link(height_sock, b, "Height")
        if normal is not None:
            self.link(normal, b, "Normal")
        self.link(b.outputs["Normal"], self.bsdf, "Normal")
        return b

    def mix(self, fac, a, b, blend="MIX"):
        m = self.n("ShaderNodeMix", data_type="RGBA", blend_type=blend)
        if isinstance(fac, float):
            m.inputs[0].default_value = fac
        else:
            self.link(fac, m, 0)
        for idx, v in ((6, a), (7, b)):
            if isinstance(v, tuple):
                m.inputs[idx].default_value = v
            else:
                self.nt.links.new(v, m.inputs[idx])
        return m

    def set(self, **kw):
        names = {"base": "Base Color", "rough": "Roughness", "metal": "Metallic", "ior": "IOR",
                 "trans": "Transmission Weight", "alpha": "Alpha", "emit": "Emission Color",
                 "emit_s": "Emission Strength", "coat": "Coat Weight", "spec": "Specular IOR Level",
                 "sss": "Subsurface Weight"}
        for k, v in kw.items():
            sock = self.bsdf.inputs[names[k]]
            if hasattr(v, "is_output"):
                self.nt.links.new(v, sock)
            else:
                sock.default_value = v


def new_mat(name):
    import bpy
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, NB(m)


def render_plaster(name, light, dark, grain=1.0):
    """M01/M02 hand-trowelled lime render: large mottling + trowel waves + mm grain."""
    m, b = new_mat(name)
    big = b.noise(0.35, 4, 0.5)
    mid = b.noise(2.2, 8, 0.6)
    col = b.ramp(big.outputs["Fac"], [(0.3, srgb(dark)), (0.7, srgb(light))])
    spots = b.ramp(mid.outputs["Fac"], [(0.35, (0.82, 0.82, 0.82, 1)), (0.65, (1, 1, 1, 1))])
    base = b.mix(1.0, col.outputs["Color"], spots.outputs["Color"], "MULTIPLY")
    b.set(base=base.outputs[2], rough=0.92, spec=0.35)
    fine = b.noise(140.0 * grain, 3, 0.7)
    trowel = b.noise(1.6, 3, 0.4)
    h = b.mix(0.35, fine.outputs["Fac"], trowel.outputs["Fac"], "ADD")
    b.bump(h.outputs[2], 0.18, 0.004)
    return m


def timber(name, col_light, col_dark):
    """M03 oiled weathered softwood, grain along local X."""
    import bpy
    m, b = new_mat(name)
    mp = b.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 14.0, 14.0)           # grain streaks along local X
    b.link(b.obj, mp, "Vector")
    gr = b.noise(3.0, 10, 0.62, vec=mp.outputs["Vector"])
    col = b.ramp(gr.outputs["Fac"], [(0.35, srgb(col_dark)), (0.65, srgb(col_light))])
    fib = b.noise(90.0, 3, 0.5, vec=mp.outputs["Vector"])
    base = b.mix(0.15, col.outputs["Color"], fib.outputs["Color"], "OVERLAY")
    b.set(base=col.outputs["Color"], rough=0.62)
    b.bump(fib.outputs["Fac"], 0.08, 0.002)
    return m


def stone_wall(name):
    """M04 warm local rubble stone, stones 0.15-0.40 m, recessed joints."""
    m, b = new_mat(name)
    vo = b.n("ShaderNodeTexVoronoi", feature="F1")
    vo.inputs["Scale"].default_value = 5.0
    vo.inputs["Randomness"].default_value = 0.75
    mp = b.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, 2.6)              # flat coursed stones
    b.link(b.obj, mp, "Vector")
    b.link(mp.outputs["Vector"], vo, "Vector")
    edge = b.n("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE")
    edge.inputs["Scale"].default_value = 5.0
    edge.inputs["Randomness"].default_value = 0.75
    b.link(mp.outputs["Vector"], edge, "Vector")
    cell = b.ramp(vo.outputs["Color"], [(0.0, srgb("#9A7046")), (0.5, srgb("#BC9461")), (1.0, srgb("#D2B07C"))])
    joint = b.ramp(edge.outputs["Distance"], [(0.02, (0, 0, 0, 1)), (0.07, (1, 1, 1, 1))])
    grit = b.noise(25.0, 6, 0.65)
    c1 = b.mix(0.25, cell.outputs["Color"], grit.outputs["Color"], "OVERLAY")
    base = b.mix(joint.outputs["Color"], srgb("#7A6550"), c1.outputs[2])
    b.set(base=base.outputs[2], rough=0.85)
    h = b.mix(0.3, joint.outputs["Color"], grit.outputs["Color"], "ADD")
    b.bump(h.outputs[2], 0.6, 0.03)
    return m


def tiles(name, light, dark, size_x, size_y, mortar_col, mortar=0.004, rough=0.75, bump=0.25, offset=0.5):
    """Paving / stone slabs with the Brick texture at true size (metres)."""
    m, b = new_mat(name)
    br = b.n("ShaderNodeTexBrick")
    br.offset = offset
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = size_x
    br.inputs["Row Height"].default_value = size_y
    br.inputs["Mortar Size"].default_value = mortar
    br.inputs["Mortar Smooth"].default_value = 0.3
    br.inputs["Color1"].default_value = srgb(light)
    br.inputs["Color2"].default_value = srgb(dark)
    br.inputs["Mortar"].default_value = srgb(mortar_col)
    br.inputs["Bias"].default_value = 0.0
    b.link(b.obj, br, "Vector")
    n = b.noise(18.0, 6, 0.6)
    base = b.mix(0.18, br.outputs["Color"], n.outputs["Color"], "OVERLAY")
    b.set(base=base.outputs[2], rough=rough)
    h = b.mix(0.25, br.outputs["Fac"], n.outputs["Fac"], "ADD")
    b.bump(h.outputs[2], bump, 0.01)
    return m


def simple(name, hexcol, rough=0.5, metal=0.0, noise_scale=0.0, noise_amt=0.0, bump=0.0):
    m, b = new_mat(name)
    if noise_scale:
        n = b.noise(noise_scale, 6, 0.6)
        base = b.mix(noise_amt, srgb(hexcol), n.outputs["Color"], "OVERLAY")
        b.set(base=base.outputs[2])
        if bump:
            b.bump(n.outputs["Fac"], bump, 0.01)
    else:
        b.set(base=srgb(hexcol))
    b.set(rough=rough, metal=metal)
    m.diffuse_color = srgb(hexcol)
    return m


def glass(name):
    m, b = new_mat(name)
    b.set(base=srgb("#E8F0EE"), rough=0.02, ior=1.52, trans=1.0)
    return m


def water(name, tint, rough=0.03, wave_scale=0.6, wave_strength=0.25):
    m, b = new_mat(name)
    b.set(base=srgb(tint), rough=rough, ior=1.333, trans=1.0)
    n = b.noise(wave_scale, 4, 0.5)
    b.bump(n.outputs["Fac"], wave_strength, 0.05)
    return m


def ocean(name):
    m, b = new_mat(name)
    b.set(base=srgb("#0B3A44"), rough=0.06, spec=0.6)
    big = b.noise(0.012, 3, 0.5)
    small = b.noise(0.35, 6, 0.6)
    h = b.mix(0.35, big.outputs["Fac"], small.outputs["Fac"], "ADD")
    b.bump(h.outputs[2], 0.35, 0.5)
    return m


def terrain(name):
    """Ochre desert soil / beach sand / coastal rock, mixed by the 'mask' colour attribute."""
    m, b = new_mat(name)
    attr = b.n("ShaderNodeAttribute", attribute_name="mask")
    sep = b.n("ShaderNodeSeparateColor")
    b.link(attr.outputs["Color"], sep, "Color")
    macro = b.noise(0.012, 5, 0.6)
    soil = b.ramp(macro.outputs["Fac"], [(0.3, srgb("#9A6B45")), (0.5, srgb("#BC8F63")), (0.7, srgb("#A97A50")), (0.85, srgb("#8A6446"))])
    pebble = b.n("ShaderNodeTexVoronoi", feature="F1")
    pebble.inputs["Scale"].default_value = 9.0
    b.link(b.obj, pebble, "Vector")
    peb = b.ramp(pebble.outputs["Distance"], [(0.05, srgb("#6E5240")), (0.12, (1, 1, 1, 1))])
    soil2 = b.mix(1.0, soil.outputs["Color"], peb.outputs["Color"], "MULTIPLY")
    scrub = b.noise(0.6, 4, 0.7)
    scr = b.ramp(scrub.outputs["Fac"], [(0.56, (1, 1, 1, 1)), (0.66, srgb("#7E6A4A"))])
    soil3 = b.mix(1.0, soil2.outputs[2], scr.outputs["Color"], "MULTIPLY")
    sandn = b.noise(0.05, 4, 0.5)
    sand = b.ramp(sandn.outputs["Fac"], [(0.3, srgb("#D7BE96")), (0.7, srgb("#E6D1AC"))])
    rockn = b.noise(0.4, 8, 0.7)
    rock = b.ramp(rockn.outputs["Fac"], [(0.3, srgb("#4F3B2E")), (0.7, srgb("#8A6A50"))])
    c1 = b.mix(sep.outputs["Green"], soil3.outputs[2], rock.outputs["Color"])
    c2 = b.mix(sep.outputs["Red"], c1.outputs[2], sand.outputs["Color"])
    b.set(base=c2.outputs[2], rough=0.95, spec=0.3)
    fine = b.noise(6.0, 8, 0.7)
    h = b.mix(sep.outputs["Green"], fine.outputs["Fac"], rockn.outputs["Fac"])
    b.bump(h.outputs[2], 0.5, 0.15)
    return m


def lawn(name):
    m, b = new_mat(name)
    n1 = b.noise(0.8, 5, 0.6)
    n2 = b.noise(40.0, 4, 0.7)
    col = b.ramp(n1.outputs["Fac"], [(0.3, srgb("#4A5E2A")), (0.7, srgb("#76874A"))])
    base = b.mix(0.3, col.outputs["Color"], n2.outputs["Color"], "OVERLAY")
    b.set(base=base.outputs[2], rough=0.85, sss=0.05)
    b.bump(n2.outputs["Fac"], 0.5, 0.01)
    return m


def foliage(name, dark, light, scale=6.0):
    m, b = new_mat(name)
    vo = b.n("ShaderNodeTexVoronoi", feature="F1")
    vo.inputs["Scale"].default_value = scale
    b.link(b.obj, vo, "Vector")
    col = b.ramp(vo.outputs["Distance"], [(0.1, srgb(light)), (0.6, srgb(dark))])
    b.set(base=col.outputs["Color"], rough=0.7, sss=0.08)
    b.bump(vo.outputs["Distance"], 0.8, 0.05)
    return m


def image_mat(name, fname, alpha=False, box_scale=None, rough=0.7, sss=0.0, tint=None):
    """Material from a generated texture in assets/textures/generated (status GENERATED)."""
    import bpy, os
    m, b = new_mat(name)
    path = os.path.join(C.TEX_DIR, fname)
    img = bpy.data.images.load(path, check_existing=True)
    tex = b.n("ShaderNodeTexImage")
    tex.image = img
    if box_scale:
        tex.projection = "BOX"
        tex.projection_blend = 0.25
        mp = b.n("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (box_scale, box_scale, box_scale)
        b.link(b.obj, mp, "Vector")
        b.link(mp.outputs["Vector"], tex, "Vector")
    col = tex.outputs["Color"]
    if tint:
        mx = b.mix(1.0, col, srgb(tint), "SCREEN")
        mx.inputs[0].default_value = 0.35
        col = mx.outputs[2]
    b.set(base=col, rough=rough, sss=sss)
    if alpha:
        b.set(alpha=tex.outputs["Alpha"])
        try:
            m.blend_method = "HASHED"
        except Exception:
            pass
    bw = b.n("ShaderNodeRGBToBW")
    b.link(tex.outputs["Color"], bw, "Color")
    b.bump(bw.outputs["Val"], 0.35, 0.01)
    return m


def emissive(name, hexcol, strength):
    m, b = new_mat(name)
    b.set(base=srgb(hexcol), emit=srgb(hexcol), emit_s=strength, rough=0.5)
    return m


def interior(name):
    """Interior proxy behind glazing: warm plaster lit by lamps (CINEMATIC_APPROXIMATION)."""
    m, b = new_mat(name)
    n = b.noise(0.8, 3, 0.5)
    col = b.ramp(n.outputs["Fac"], [(0.3, srgb("#8C6A4E")), (0.7, srgb("#C49A72"))])
    b.set(base=col.outputs["Color"], rough=0.8, emit=srgb("#FFB878"), emit_s=0.6)
    return m


PH_DIR = None
#   material                      Poly Haven slug          tile m  colour multiplier (keeps the site-photo hue)
# Each texture gives its DETAIL (grain, joints, cracks); the colour stays the one measured on the
# site photos. keep = how much of the texture's own colour is kept (0 = pure site colour).
PH_MAP = {
    # contrast = strength of the texture detail (1 = as photographed)
    #                              slug                     tile m  site colour  keep  contrast
    "M01_Render_Sand":            ("white_plaster_rough_01", 2.5, "#D2B289", 0.0, 0.45),
    "M02_Render_Ochre":           ("white_plaster_rough_01", 2.5, "#B79473", 0.0, 0.45),
    "M03_Timber_Pergola":         ("wood_planks",            1.2, "#C7A47E", 0.55, 1.0),
    "M04_Stone_Rubble":           ("stacked_stone_wall",     2.5, "#BC9461", 0.35, 1.0),
    "M07_Pavers_Beige":           ("patterned_paving",       2.0, "#CDBDA6", 0.0, 0.8),
    "M09_Terrace_Stone":          ("marble_tiles",           2.4, "#DCD0BC", 0.0, 0.12),
}
PH_TERRAIN = {"soil": ("aerial_ground_rock", 9.0), "sand": ("aerial_beach_01", 10.0)}   # tile sizes INFERRED


def ph_maps(slug):
    """Colour / roughness / height maps in a Poly Haven folder (any resolution, any nesting).
    A *.blend.zip download unzipped keeps its maps in textures/; those are found too."""
    import os
    d = os.path.join(PH_DIR, slug)
    if not os.path.isdir(d):
        return None
    files = []
    for r, _, fs in os.walk(d):
        files += [os.path.join(r, f) for f in sorted(fs) if f.lower().endswith((".jpg", ".jpeg", ".png", ".exr", ".tif", ".tiff"))]
    def pick(*keys):
        for k in keys:
            for f in files:                      # match the map suffix only: the slug itself may
                if k in os.path.basename(f).lower().replace(slug, ""):   # contain "rough" etc.
                    return f
        return None
    col = pick("_diff", "diffuse", "_col", "albedo", "basecolor")
    if not col:
        return None
    return {"col": col, "rough": pick("_rough"), "arm": pick("_arm"), "disp": pick("_disp", "height"),
            "nrm": pick("nor_gl", "normal_gl")}


def ph_tex(b, path, vec, data=False):
    import bpy
    t = b.n("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path, check_existing=True)
    if data:
        t.image.colorspace_settings.name = "Non-Color"
    t.projection = "BOX"
    t.projection_blend = 0.2
    b.link(vec, t, "Vector")
    return t


def ph_vector(b, tile):
    mp = b.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0 / tile,) * 3
    b.link(b.obj, mp, "Vector")
    return mp.outputs["Vector"]


def mean_lum(path):
    """Mean linear luminance of a texture (to normalise its detail around 1.0)."""
    try:
        from PIL import Image
        import numpy as np
        im = np.asarray(Image.open(path).convert("RGB").resize((64, 64)), dtype=float) / 255.0
        lin = np.where(im > 0.04045, ((im + 0.055) / 1.055) ** 2.4, im / 12.92)
        return float((lin @ [0.2126, 0.7152, 0.0722]).mean())
    except Exception:
        return 0.2


def lum_of(hexcol):
    c = srgb(hexcol)
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ph_surface(name, slug, tile, target, keep, contrast=1.0):
    """Rebuild one material from Poly Haven maps. Returns the material or None if not downloaded."""
    maps = ph_maps(slug)
    if not maps:
        return None
    m, b = new_mat(name)
    vec = ph_vector(b, tile)
    tex = ph_tex(b, maps["col"], vec).outputs["Color"]
    mu = mean_lum(maps["col"])
    bw = b.n("ShaderNodeRGBToBW")
    b.link(tex, bw, "Color")
    norm = b.n("ShaderNodeMath", operation="MULTIPLY")             # texture detail around 1.0
    b.link(bw.outputs["Val"], norm, 0)
    norm.inputs[1].default_value = 1.0 / max(mu, 1e-3)
    if contrast != 1.0:                                            # 1 + (detail - 1) * contrast
        con = b.n("ShaderNodeMath", operation="MULTIPLY_ADD")
        b.link(norm.outputs[0], con, 0)
        con.inputs[1].default_value = contrast
        con.inputs[2].default_value = 1.0 - contrast
        norm = con
    detail = b.n("ShaderNodeVectorMath", operation="SCALE")        # site colour x detail
    detail.inputs[0].default_value = srgb(target)[:3]
    b.link(norm.outputs[0], detail, "Scale")
    col = detail.outputs["Vector"]
    if keep > 0:
        own = b.n("ShaderNodeVectorMath", operation="SCALE")       # texture colour, brightness matched
        b.link(tex, own, 0)
        own.inputs["Scale"].default_value = lum_of(target) / max(mu, 1e-3)
        col = b.mix(keep, col, own.outputs["Vector"]).outputs[2]
    b.set(base=col, spec=0.4)
    if maps["rough"]:
        b.set(rough=ph_tex(b, maps["rough"], vec, True).outputs["Color"])
    elif maps["arm"]:
        sep = b.n("ShaderNodeSeparateColor")
        b.link(ph_tex(b, maps["arm"], vec, True).outputs["Color"], sep, "Color")
        b.set(rough=sep.outputs["Green"])
    else:
        rr = b.ramp(bw.outputs["Val"], [(0.0, (0.95, 0.95, 0.95, 1)), (1.0, (0.7, 0.7, 0.7, 1))])
        b.set(rough=rr.outputs["Color"])
    h = ph_tex(b, maps["disp"], vec, True).outputs["Color"] if maps["disp"] else norm.outputs[0]   # same softened detail
    b.bump(h, 0.45, 0.015 * tile * (1.0 if maps["disp"] else mu))   # detail is normalised by 1/mu
    m["source"] = "POLY HAVEN CC0: " + slug + " (" + os.path.basename(maps["col"]) + "), tile %.1f m" % tile
    return m


def ph_detail(b, path, tile, contrast, rot=0.0):
    """Texture detail normalised around 1.0 (colour comes from elsewhere)."""
    mp = b.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0 / tile,) * 3
    mp.inputs["Rotation"].default_value = (0.0, 0.0, rot)
    b.link(b.obj, mp, "Vector")
    bw = b.n("ShaderNodeRGBToBW")
    b.link(ph_tex(b, path, mp.outputs["Vector"]).outputs["Color"], bw, "Color")
    con = b.n("ShaderNodeMath", operation="MULTIPLY_ADD")
    b.link(bw.outputs["Val"], con, 0)
    con.inputs[1].default_value = contrast / max(mean_lum(path), 1e-3)
    con.inputs[2].default_value = 1.0 - contrast
    return con.outputs[0]


def ph_terrain(name):
    """Terrain: the site's ochre soil / beach sand / rock palette (as before), with the detail of the
    client's Poly Haven aerial maps at two scales (9 m and 47 m, rotated) so tiles do not repeat
    from the air. None if aerial_ground_rock is missing."""
    soil_maps = ph_maps(PH_TERRAIN["soil"][0])
    if not soil_maps:
        return None
    sand_maps = ph_maps(PH_TERRAIN["sand"][0])
    m, b = new_mat(name)
    attr = b.n("ShaderNodeAttribute", attribute_name="mask")
    sep = b.n("ShaderNodeSeparateColor")
    b.link(attr.outputs["Color"], sep, "Color")
    macro = b.noise(0.012, 5, 0.6)
    soil = b.ramp(macro.outputs["Fac"], [(0.3, srgb("#9A6B45")), (0.5, srgb("#BC8F63")), (0.7, srgb("#A97A50")), (0.85, srgb("#8A6446"))])
    scrub = b.noise(0.6, 4, 0.7)
    scr = b.ramp(scrub.outputs["Fac"], [(0.56, (1, 1, 1, 1)), (0.66, srgb("#7E6A4A"))])
    soil2 = b.mix(1.0, soil.outputs["Color"], scr.outputs["Color"], "MULTIPLY")
    d1 = ph_detail(b, soil_maps["col"], PH_TERRAIN["soil"][1], 0.6)
    d2 = ph_detail(b, soil_maps["col"], PH_TERRAIN["soil"][1] * 5.3, 0.45, 0.7)
    dd = b.n("ShaderNodeMath", operation="MULTIPLY")
    b.link(d1, dd, 0)
    b.link(d2, dd, 1)
    soil3 = b.n("ShaderNodeVectorMath", operation="SCALE")
    b.link(soil2.outputs[2], soil3, 0)
    b.link(dd.outputs[0], soil3, "Scale")
    sandn = b.noise(0.05, 4, 0.5)
    sand = b.ramp(sandn.outputs["Fac"], [(0.3, srgb("#D7BE96")), (0.7, srgb("#E6D1AC"))]).outputs["Color"]
    if sand_maps:
        sd = b.n("ShaderNodeVectorMath", operation="SCALE")
        b.link(sand, sd, 0)
        b.link(ph_detail(b, sand_maps["col"], PH_TERRAIN["sand"][1], 0.6), sd, "Scale")
        sand = sd.outputs["Vector"]
    rockn = b.noise(0.4, 8, 0.7)
    rock = b.ramp(rockn.outputs["Fac"], [(0.3, srgb("#4F3B2E")), (0.7, srgb("#8A6A50"))])
    c1 = b.mix(sep.outputs["Green"], soil3.outputs["Vector"], rock.outputs["Color"])
    c2 = b.mix(sep.outputs["Red"], c1.outputs[2], sand)
    b.set(base=c2.outputs[2], rough=0.95, spec=0.3)
    h = b.mix(sep.outputs["Green"], d1, rockn.outputs["Fac"])
    b.bump(h.outputs[2], 0.35, 0.15)
    m["source"] = "POLY HAVEN CC0 detail: " + ", ".join(s for s, _ in PH_TERRAIN.values() if ph_maps(s))
    return m


def build():
    global PH_DIR
    import os
    PH_DIR = os.path.join(C.ROOT, "assets", "textures", "polyhaven")
    mats = {
        "render": render_plaster("M01_Render_Sand", "#D2B289", "#BE9C72"),
        "render_dark": render_plaster("M02_Render_Ochre", "#B79473", "#A3805F"),
        "timber": timber("M03_Timber_Pergola", "#C7A47E", "#A98560"),
        "stone": stone_wall("M04_Stone_Rubble"),
        "bronze": simple("M05_Aluminium_Bronze", "#433C37", 0.38, 0.8),
        "glass": glass("M06_Glass"),
        "pavers": tiles("M07_Pavers_Beige", "#D3C4AE", "#C2A98F", 0.20, 0.10, "#9C8E7E", 0.003),
        "brick": tiles("M08_Pavers_Brick", "#A9634B", "#8F4F3B", 0.20, 0.10, "#6B5446", 0.003),
        "terrace": tiles("M09_Terrace_Stone", "#DCD0BC", "#CFC1AA", 0.60, 0.40, "#A99B88", 0.003, 0.6, 0.15, 0.0),
        "pool_tile": tiles("M10_Pool_Mosaic", "#BFE3E0", "#A6D6D4", 0.025, 0.025, "#E8F2F0", 0.002, 0.2, 0.1, 0.0),
        "pool_water": water("M10_Pool_Water", "#D4F2F0", 0.02, 1.4, 0.12),
        "lake_water": water("M10_Lake_Water", "#A9D8D2", 0.04, 0.5, 0.2),
        "asphalt": simple("M11_Asphalt", "#4A4744", 0.9, 0.0, 30.0, 0.35, 0.3),
        "roof": simple("M12_Roof_Gravel", "#CDBFA9", 0.95, 0.0, 20.0, 0.4, 0.4),
        "kerb": simple("Kerb_Concrete", "#CFC6B8", 0.8, 0.0, 8.0, 0.2, 0.1),
        "terrain": terrain("T01_Terrain_Soil_Sand_Rock"),
        "ocean": ocean("H03_Ocean"),
        "lawn": lawn("T03_Lawn"),
        "hedge": image_mat("V05_Hedge", "TEX_HEDGE_LEAVES_GEN_1K.jpg", box_scale=2.0, rough=0.75, sss=0.05, tint="#9FC070"),
        "grass_blade": simple("T03_Grass_Blade", "#5F7A33", 0.7, 0.0, 2.0, 0.35),
        "olive_leaf": image_mat("V03_Olive_Foliage", "TEX_OLIVE_LEAFCARD_GEN_1K.png", alpha=True, rough=0.6, sss=0.1),
        "blossom": image_mat("V07_Pink_Blossom_Tree", "TEX_PINK_BLOSSOM_LEAFCARD_GEN_1K.png", alpha=True, rough=0.6, sss=0.12),
        "green_leaf": image_mat("V08_Green_Shade_Tree", "TEX_GREEN_SHADE_LEAFCARD_GEN_1K.png", alpha=True, rough=0.6, sss=0.12),
        "paint_line": simple("Road_Paint_White", "#EDEBE6", 0.6),
        "car_glass": simple("A08_Car_Glass", "#151a1f", 0.08, 0.3),
        "tyre": simple("A08_Tyre", "#1A1A1A", 0.85),
        "palm_fan": image_mat("V01_Palm_Fan", "TEX_WASHINGTONIA_FAN_GEN_1K.png", alpha=True, rough=0.55, sss=0.12),
        "palm_leaf": simple("V01_Palm_Leaf", "#5E7536", 0.55, 0.0, 3.0, 0.25),
        "palm_trunk": simple("V01_Palm_Trunk", "#7D6650", 0.9, 0.0, 12.0, 0.5, 0.6),
        "palm_skirt": simple("V01_Palm_Skirt", "#9E8462", 0.9, 0.0, 8.0, 0.4, 0.4),
        "grass_orn": simple("V04_Ornamental_Grass", "#B7A56E", 0.7, 0.0, 6.0, 0.3),
        "bougainvillea": foliage("V06_Bougainvillea", "#7A1F4E", "#C23A7A", 18.0),
        "cushion": simple("A01_Cushion_White", "#ECE6DA", 0.9),
        "metal_dark": simple("A02_Metal_Dark", "#2E2B29", 0.45, 0.7),
        "interior": interior("A06_Interior_Proxy"),
        "lamp": emissive("Lamp_Warm", "#FFC98F", 25.0),
        "curtain": simple("A06_Curtain_Linen", "#E9DFCF", 0.95),
        "car": simple("A08_Car_Paint", "#D8D6D0", 0.25, 0.6),
    }
    for m in mats.values():
        m["status"] = "APPROXIMATED (procedural; CC0 textures blocked by network policy)"
    used = []
    for key, m in mats.items():
        if m.name in PH_MAP and ph_surface(m.name, *PH_MAP[m.name]):
            m["status"] = "SOURCED"
            used.append(m.name)
    if ph_terrain("T01_Terrain_Soil_Sand_Rock"):
        mats["terrain"]["status"] = "SOURCED"
        used.append("T01_Terrain_Soil_Sand_Rock")
    print("[materials] Poly Haven maps used for:", used or "none (procedural only)", flush=True)
    return mats
