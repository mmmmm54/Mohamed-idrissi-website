"""
20_pipeline — rebuilds the Mirleft Bay scene from scratch, deterministic by name.

    python 20_pipeline.py [--until graybox|landscape|lighting|cameras|final] [--validate] [--render]

Runs with Blender's Python module (bpy 4.2). Every stage saves a checkpoint .blend in
output/checkpoints/. Scripts are loaded by file name (they start with digits).
"""
import argparse
import importlib.util
import os
import sys
import time

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
STAGES = ["graybox", "landscape", "lighting", "cameras", "final"]


def load(fname, C=None):
    spec = importlib.util.spec_from_file_location("mb_" + fname[:2], os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    if C is not None:
        mod.__dict__["C"] = C
    spec.loader.exec_module(mod)
    return mod


def log(*a):
    print("[pipeline %s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def save(C, name):
    path = os.path.join(C.CHECKPOINTS, name)
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    if os.path.exists(path + "1"):
        os.remove(path + "1")
    log("checkpoint", name)


def setup_render(sc, preview=True):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 32 if preview else 256
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.transparent_max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920        # 9:16 (client)
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.film_transparent = False


def setup_haze(sc):
    """Aerial perspective: mist pass mixed with a warm haze colour in the compositor."""
    sc.view_layers[0].use_pass_mist = True
    sc.view_layers[0].use_pass_z = True
    w = sc.world
    w.mist_settings.start = 120.0
    w.mist_settings.depth = 6000.0
    w.mist_settings.falloff = "QUADRATIC"
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    mix = nt.nodes.new("CompositorNodeMixRGB")
    mix.blend_type = "MIX"
    mix.inputs[2].default_value = (0.93, 0.78, 0.62, 1.0)
    mul = nt.nodes.new("CompositorNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.55
    comp = nt.nodes.new("CompositorNodeComposite")
    geo = nt.nodes.new("CompositorNodeMath")          # 1 on geometry, 0 on the sky
    geo.operation = "LESS_THAN"
    geo.inputs[1].default_value = 1.0e6
    nt.links.new(rl.outputs["Depth"], geo.inputs[0])
    mm = nt.nodes.new("CompositorNodeMath")
    mm.operation = "MULTIPLY"
    nt.links.new(rl.outputs["Mist"], mm.inputs[0])
    nt.links.new(geo.outputs[0], mm.inputs[1])
    nt.links.new(mm.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], mix.inputs[0])
    nt.links.new(rl.outputs["Image"], mix.inputs[1])
    nt.links.new(mix.outputs[0], comp.inputs["Image"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--until", default="final", choices=STAGES)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--render", default="", help="comma list of camera names, or 'all'")
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--plan", default="")
    ap.add_argument("--pct", type=int, default=100)
    args = ap.parse_args(sys.argv[1:])
    until = STAGES.index(args.until)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    C = load("00_config.py")
    for name in C.COLLECTIONS:
        C.collection(name)
    sc = bpy.context.scene
    setup_render(sc)
    sc.render.resolution_percentage = args.pct
    sc.unit_settings.system = "METRIC"

    t0 = time.time()
    mats = load("07_build_materials.py", C).build()
    log("materials", len(mats))
    terr = load("03_build_terrain.py", C).build(mats)
    log("terrain done")
    site = load("02_build_site.py", C)
    C.DRAPED = site.draped
    log("site", site.build(mats))
    counts = load("04_build_architecture.py", C).build(mats)
    log("architecture", counts)
    light = load("14_build_lighting.py", C)
    log("lighting", light.build())
    save(C, "checkpoint_02_graybox.blend")
    if args.validate:
        plan = args.plan or os.path.join(C.ROOT, "..", "..", "..", "masse_rot.png")
        rep = load("18_validate_scene.py", C).build(counts, plan, "graybox")
        log("validation", rep)
    if until >= 1:
        log("landscape", load("09_build_landscape.py", C).build(mats))
        save(C, "checkpoint_07_landscape.blend")
    if until >= 2:
        pass
    if until >= 3:
        cams = load("15_build_cameras.py", C)
        log("cameras", cams.build())
        land = load("09_build_landscape.py", C)
        zones = []
        for nm, rad, dens in (("SH05_GARDEN_REVEAL", 14, 260), ("SH09_DETAIL_NICHES", 8, 260), ("SH10_SUNSET_LAKE", 30, 140),
                              ("SH08_POOL_PAVILLON", 22, 120), ("SH06_PERGOLA_TERRACE", 16, 120)):
            o = bpy.data.objects[nm]
            fwd = o.matrix_world.to_3x3() @ __import__("mathutils").Vector((0, 0, -1))
            c = (o.location.x + fwd.x * rad * 0.8, o.location.y + fwd.y * rad * 0.8)
            zones.append((c, rad, dens))
        log("hero grass tufts", land.build_grass(mats, zones))
        # keep a clear radius around ground-level cameras (no trunk / leaf card in the lens)
        removed = 0
        for o in list(C.collection("13_CAMERAS").objects):
            if o.location.z - C.TERRAIN_HEIGHT(__import__("numpy").array([[o.location.x, o.location.y]]))[0] > 12:
                continue
            for v in list(bpy.data.objects):
                if v.name.startswith("VEG_") and (v.location.xy - o.location.xy).length < 3.5:
                    bpy.data.objects.remove(v, do_unlink=True)
                    removed += 1
        log("vegetation cleared near cameras", removed)
        setup_haze(sc)
        save(C, "checkpoint_09_cameras.blend")
        if args.render:
            names = [c.name for c in C.collection("13_CAMERAS").objects] if args.render == "all" else args.render.split(",")
            if args.samples:
                sc.cycles.samples = args.samples
            for n in names:
                cams.render(n)
    if until >= 4:
        save(C, "checkpoint_10_final.blend")
    log("done in %.1f min" % ((time.time() - t0) / 60))


main()
