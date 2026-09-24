"""
Bakes the Cycles lighting (sun, sky, shadows, bounce light) into the textures of
Imara_Teal_R6.blend and exports Imara_Teal_R6_HQ.glb.

Why: a GLB carries no lights, so After Effects (or any viewer) re-lights it with its
own real-time lights and the result looks flat. Here every opaque surface gets a
texture = albedo x Cycles lighting, tone-mapped with the same AgX look as the
previews, on an unlit material (KHR_materials_unlit). It looks the same in every
viewer. Glass and glass railings stay as PBR materials so they keep reflecting.

Run with Blender's Python (bpy 4.2), after build_imara.py:
    python bake_hq.py <model_dir> [samples] [px_per_metre]
"""
import math
import os
import sys
import time

import bpy  # noqa: I001  (bpy must load before bmesh / mathutils)
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 64
DENSITY = float(sys.argv[3]) if len(sys.argv) > 3 else 72.0   # texels per metre
BAKE_DIR = os.path.join(OUT, "baked")
os.makedirs(BAKE_DIR, exist_ok=True)
KEEP_PBR = {"Imara_Window_Glass", "Imara_Balcony_Glass_Railing"}
EMISSIVE = {"Imara_Downlights"}

bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "Imara_Teal_R6.blend"))
sc = bpy.context.scene
vl = bpy.context.view_layer
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.render.bake.margin = 8
sc.render.bake.margin_type = "EXTEND"
root = bpy.data.objects["Imara_Teal_R6"]
targets = [o for o in root.children if o.type == "MESH"]


def log(*a):
    print("[bake %s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def hemisphere(n=24):
    """Fixed, evenly spread directions on the +Z hemisphere."""
    dirs, golden = [], math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 0.08 + 0.92 * (i + 0.5) / n
        r = math.sqrt(1 - z * z)
        dirs.append(Vector((math.cos(golden * i) * r, math.sin(golden * i) * r, z)))
    return dirs


def cull_hidden_faces(objs):
    """Delete faces that no ray from outside can reach (wall insides, faces pressed
    against other faces). Every other face keeps its geometry untouched."""
    verts, polys = [], []
    for o in objs:
        base = len(verts)
        verts.extend(o.matrix_world @ v.co for v in o.data.vertices)
        polys.extend([base + i for i in p.vertices] for p in o.data.polygons)
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    hemi = hemisphere()
    removed = 0
    for o in objs:
        if o.name in ("Imara_Balcony_Glass_Railing",):
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        dead = []
        for f in bm.faces:
            nrm = f.normal.normalized()
            t = nrm.orthogonal().normalized()
            b = nrm.cross(t)
            c = f.calc_center_median()
            pts = [c] + [c.lerp(v.co, 0.9) for v in f.verts]
            visible = False
            for pnt in pts:
                org = pnt + nrm * 0.002
                for d in hemi:
                    w = t * d.x + b * d.y + nrm * d.z
                    if tree.ray_cast(org, w, 500.0)[0] is None:
                        visible = True
                        break
                if visible:
                    break
            if not visible:
                dead.append(f)
        removed += len(dead)
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()
        log("cull", o.name, "removed", len(dead), "kept", len(o.data.polygons))
    return removed


def select_only(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    vl.objects.active = ob


def pin_texture_uvs(mat):
    """Tiled textures keep reading the world-scale 'UVMap' while baking to 'Bake'."""
    nt = mat.node_tree
    for n in list(nt.nodes):
        if n.type == "TEX_IMAGE" and not n.inputs["Vector"].is_linked:
            uvn = nt.nodes.new("ShaderNodeUVMap")
            uvn.uv_map = "UVMap"
            nt.links.new(uvn.outputs["UV"], n.inputs["Vector"])


def resolution(me):
    area = sum(p.area for p in me.polygons)
    need = math.sqrt(area / 0.55) * DENSITY
    for r in (512, 1024, 2048, 4096, 8192):
        if r >= need:
            return r
    return 8192


def bake(ob, mat, res, kind, passes=None, samples=1):
    img = bpy.data.images.new("tmp_%s_%s" % (ob.name, kind), res, res, float_buffer=True, alpha=False)
    nt = mat.node_tree
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = img
    nt.nodes.active = node
    sc.cycles.samples = samples
    if kind == "normal":
        bpy.ops.object.bake(type="NORMAL", normal_space="OBJECT", use_clear=True, margin=8)
    else:
        bpy.ops.object.bake(type="DIFFUSE", pass_filter=passes, use_clear=True, margin=8)
    nt.nodes.remove(node)
    px = np.empty(res * res * 4, np.float32)
    img.pixels.foreach_get(px)
    return img, px.reshape(res, res, 4)


def denoise(light_img, normal_img, res):
    """OIDN on the lighting-only bake (no texture detail to lose)."""
    dsc = bpy.data.scenes.get("Denoise") or bpy.data.scenes.new("Denoise")
    dsc.use_nodes = True
    nt = dsc.node_tree
    nt.nodes.clear()
    a = nt.nodes.new("CompositorNodeImage")
    a.image = light_img
    nn = nt.nodes.new("CompositorNodeImage")
    nn.image = normal_img
    dn = nt.nodes.new("CompositorNodeDenoise")
    dn.use_hdr = True
    dn.prefilter = "ACCURATE"
    out = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(a.outputs["Image"], dn.inputs["Image"])
    nt.links.new(nn.outputs["Image"], dn.inputs["Normal"])
    nt.links.new(dn.outputs["Image"], out.inputs["Image"])
    dsc.render.resolution_x = dsc.render.resolution_y = res
    dsc.render.resolution_percentage = 100
    dsc.render.image_settings.file_format = "OPEN_EXR"
    dsc.render.image_settings.color_depth = "32"
    path = os.path.join(BAKE_DIR, "_denoise.exr")
    dsc.render.filepath = path
    bpy.ops.render.render(scene=dsc.name, write_still=True)
    img = bpy.data.images.load(path, check_existing=False)
    px = np.empty(res * res * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    os.remove(path)
    return px.reshape(res, res, 4)


def unlit_material(name, image):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "Bake"
    bg = nt.nodes.new("ShaderNodeBackground")
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    m.use_backface_culling = False
    return m


def main():
    t0 = time.time()
    cull_hidden_faces(targets)
    for ob in targets:
        if ob.name in KEEP_PBR:
            continue
        me = ob.data
        mat = me.materials[0]
        if ob.name in EMISSIVE:
            white = bpy.data.images.new("Baked_Downlights", 4, 4)
            white.pixels.foreach_set(np.ones(64, np.float32))
            white.pack()
            me.materials[0] = unlit_material("HQ_Downlights", white)
            continue
        res = resolution(me)
        log(ob.name, "faces", len(me.polygons), "res", res)
        select_only(ob)
        uv = me.uv_layers.new(name="Bake")
        me.uv_layers.active = uv
        me.uv_layers["UVMap"].active_render = True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0015,
                                 area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        pin_texture_uvs(mat)

        i_col, col = bake(ob, mat, res, "color", {"COLOR"}, samples=4)
        i_nrm, _ = bake(ob, mat, res, "normal", samples=4)
        i_lit, _ = bake(ob, mat, res, "light", {"DIRECT", "INDIRECT"}, samples=SAMPLES)
        lit = denoise(i_lit, i_nrm, res)
        final = col.copy()
        final[..., :3] = col[..., :3] * np.clip(lit[..., :3], 0, None)
        final[..., 3] = 1.0

        out_img = bpy.data.images.new("lin_" + ob.name, res, res, float_buffer=True, alpha=False)
        out_img.pixels.foreach_set(final.ravel())
        png = os.path.join(BAKE_DIR, ob.name.replace("Imara_", "") + ".png")
        out_img.save_render(png, scene=sc)          # applies AgX, same look as the previews
        for im in (i_col, i_nrm, i_lit, out_img):
            bpy.data.images.remove(im)

        baked = bpy.data.images.load(png)
        baked.name = "Baked_" + ob.name.replace("Imara_", "")
        baked.pack()
        me.materials[0] = unlit_material("HQ_" + mat.name, baked)
        me.uv_layers.active = me.uv_layers["Bake"]
        me.uv_layers["Bake"].active_render = True
        me.uv_layers.remove(me.uv_layers["UVMap"])
        log("done", ob.name, "%.0fs total" % (time.time() - t0))

    select_only(root)
    for ob in targets:
        ob.select_set(True)
    glb = os.path.join(OUT, "Imara_Teal_R6_HQ.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True,
                              export_image_format="JPEG", export_jpeg_quality=92,
                              export_yup=True, export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Imara_Teal_R6_HQ.blend"), compress=True)
    if os.path.exists(os.path.join(OUT, "Imara_Teal_R6_HQ.blend1")):
        os.remove(os.path.join(OUT, "Imara_Teal_R6_HQ.blend1"))
    log("SAVED", glb, "%.0f min" % ((time.time() - t0) / 60))


main()
