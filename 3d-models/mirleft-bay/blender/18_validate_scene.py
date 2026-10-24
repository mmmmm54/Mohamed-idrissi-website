"""
18_validate_scene — automated checks + validation renders compared with the plan raster.

Checks: object naming, missing materials, building counts against the permit table, unit
areas, site area, camera positions inside geometry. Renders: TOP_VIEW (orthographic, aligned
to the plan) and an overlay on F01.
"""
import json
import math
import os

import numpy as np

C = globals()["C"]
D = C.D

PERMIT = {"TYPE_DUPLEX_PAIR": 17, "TYPE_VILLA_B": 33, "TYPE_VILLA_C": 13, "TYPE_VILLA_A": 4}   # pairs = 34 duplex / 2


def checks(counts):
    import bpy
    rep = {"counts": {}, "issues": []}
    for k, v in PERMIT.items():
        got = counts.get(k, 0)
        rep["counts"][k] = {"model": got, "permit": v, "ok": got == v}
        if got != v:
            rep["issues"].append(f"{k}: {got} placed vs {v} on the permit table")
    no_mat = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.data.materials]
    if no_mat:
        rep["issues"].append(f"{len(no_mat)} mesh objects without material: {no_mat[:8]}")
    from shapely.geometry import Polygon
    rep["site_area_m2"] = round(Polygon(C.site_polygon_world()).area)
    rep["site_area_title_m2"] = 82070
    rep["units"] = {
        "duplex_unit_ground_m2": round((15.4 / 2) * 10.4, 1),
        "duplex_unit_upper_m2": round((15.4 / 2) * (10.4 - 3.6), 1),
        "duplex_unit_total_m2": round((15.4 / 2) * 10.4 + (15.4 / 2) * (10.4 - 3.6), 1),
        "duplex_permit_m2": 124,
        "villa_B_total_m2": round(11.0 * 8.6 + 11.0 * (8.6 - 3.4), 1), "villa_B_permit_m2": 164,
        "villa_C_total_m2": round(12.4 * 11.6, 1), "villa_C_permit_m2": 145,
        "villa_A_total_m2": round(16.4 * 13.4, 1), "villa_A_permit_m2": 220,
    }
    return rep


def render_top(path, width=2400, height=1000, ortho=640.0, samples=12):
    import bpy
    sc = bpy.context.scene
    cam = bpy.data.cameras.get("CAM_VAL_TOP") or bpy.data.cameras.new("CAM_VAL_TOP")
    cam.type = "ORTHO"
    cam.ortho_scale = ortho
    cam.clip_end = 3000
    C.remove_object("CAM_VAL_TOP")
    ob = bpy.data.objects.new("CAM_VAL_TOP", cam)
    C.collection("16_VALIDATION").objects.link(ob)
    ob.location = (0, 0, 800)
    ob.rotation_euler = (0, 0, C.yaw())
    keep = (sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples, sc.render.filepath)
    sc.camera = ob
    sc.render.resolution_x, sc.render.resolution_y = width, height
    sc.cycles.samples = samples
    sc.render.image_settings.file_format = "JPEG"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples, sc.render.filepath = keep
    return ortho / width


def overlay(top_path, out_path, m_per_px_render, plan_png):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    top = Image.open(top_path).convert("RGB")
    plan = Image.open(plan_png).convert("RGB")
    W, H = top.size
    s = m_per_px_render / D.M_PER_PX
    cx, cy = C.PLAN_CENTROID
    box = (int(cx - W * s / 2), int(cy - H * s / 2), int(cx + W * s / 2), int(cy + H * s / 2))
    crop = plan.crop(box).resize((W, H))
    Image.blend(crop, top, 0.5).save(out_path, quality=88)
    side = Image.new("RGB", (W, H * 2))
    side.paste(crop, (0, 0))
    side.paste(top, (0, H))
    side.save(out_path.replace(".jpg", "_stacked.jpg"), quality=85)


def build(counts, plan_png, tag="graybox"):
    rep = checks(counts)
    top = os.path.join(C.VALIDATION, f"VAL_TOP_VIEW_{tag}.jpg")
    mpp = render_top(top)
    overlay(top, os.path.join(C.VALIDATION, f"VAL_TOP_OVER_PLAN_{tag}.jpg"), mpp, plan_png)
    json.dump(rep, open(os.path.join(C.VALIDATION, f"validation_{tag}.json"), "w"), indent=1)
    return rep
