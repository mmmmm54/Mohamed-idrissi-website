"""
15_build_cameras — 9:16 architectural shot list (client: vertical delivery, golden hour).

Shots are defined either in plan px (site-scale shots) or in the hero duplex's local frame
(x = depth, garden facade at x = -5.2 facing WNW; y = width, unit A on -y; z from the
finished ground floor). Lens choices follow the camera language in PROJECT_BIBLE §37.
"""
import math
import os

import numpy as np

C = globals()["C"]
D = C.D

HERO = "DUPLEX_PAIR_009"          # Tranche 1, column C, next to the club pools

# name: (frame, position, target, lens_mm, higgsfield, purpose)
SHOTS = {
    "SH01_ESTABLISHING_AERIAL": ("world", (520, -260, 150), (-170, 90, 15), 28, "NO", "Backlit establishing: the spur from the road side, resort, beach and Atlantic horizon"),
    "SH02_AERIAL_TOPDOWN":      ("top", (3780, 2400, 820), None, 50, "NO", "Masterplan read top-down, axis vertical in the 9:16 frame"),
    "SH03_APPROACH_AVENUE":     ("plan", (4470, 2456, 1.7), (3000, 2445, 3.5), 35, "YES", "Date-palm avenue towards the ocean and the low sun"),
    "SH04_ENTRANCE_KASBAH":     ("plan", (5395, 2150, 1.4), (5545, 2105, 7.5), 20, "YES", "Reception towers, low angle, warm side light"),
    "SH05_GARDEN_REVEAL":       ("hero", (-11.0, -5.6, 1.6), (-5.0, -1.6, 3.3), 22, "YES", "Duplex garden facade, pergola, terrace, lawn"),
    "SH06_PERGOLA_TERRACE":     ("hero", (-2.2, -2.4, 4.95), (-30.0, -9.0, 3.2), 22, "YES", "Under the pergola looking out to the sunset"),
    "SH07_ROOFTOP_JACUZZI":     ("hero", (4.2, -3.2, 8.1), (-40.0, -14.0, 1.0), 20, "YES", "Roof terrace, jacuzzi, horizon"),
    "SH08_POOL_PAVILLON":       ("plan", (5400, 2610, 1.5), (5690, 2350, 4.0), 24, "YES", "Club pool with the Pavillon behind"),
    "SH09_DETAIL_NICHES":       ("hero", (-9.6, -4.3, 2.75), (-5.2, -4.1, 3.0), 50, "NO", "Wall niches, render grain, pergola shadow"),
    "SH10_SUNSET_LAKE":         ("plan", (2080, 2470, 1.6), (1250, 2330, 3.0), 30, "YES", "Lake park looking west, palms against the sun"),
    "SH11_FINAL_WIDE":          ("world", (-700, 520, 240), (0, -10, 30), 32, "NO", "Pull-back over the ocean, the resort on its spur"),
    "SH12_RESIDENCE_STREETS":   ("plan", (3600, 2950, 70), (3700, 2500, 0), 24, "NO", "Low aerial over road 7 and the boulevard between the villas"),
    "SH13_ENTRANCE_PARKING":    ("plan", (6250, 2700, 95), (5950, 2250, 0), 24, "NO", "Entrance: roundabout, parking fields, kasbah reception"),
}

# artistic depth of field on the ground-level shots: f-stop, focus on the shot's target point
DOF = {"SH03_APPROACH_AVENUE": 8.0, "SH04_ENTRANCE_KASBAH": 8.0, "SH05_GARDEN_REVEAL": 5.6,
       "SH06_PERGOLA_TERRACE": 4.0, "SH07_ROOFTOP_JACUZZI": 8.0, "SH08_POOL_PAVILLON": 5.6,
       "SH09_DETAIL_NICHES": 2.8, "SH10_SUNSET_LAKE": 5.6}


def hero_frame():
    import bpy
    ob = bpy.data.objects[HERO]
    return np.array(ob.location), ob.rotation_euler.z


def coast_point(y, offshore):
    """Point 'offshore' metres west of the traced shoreline at world latitude y."""
    from shapely.geometry import LineString
    sh = C.ge_to_world(D.GE_SHORELINE)
    i = int(np.argmin(np.abs(sh[:, 1] - y)))
    return np.array([sh[i, 0] - offshore, y])


def resolve(frame, p):
    if frame == "coast":                     # (offshore m, world y, height above sea)
        xy = coast_point(p[1], p[0] * -1) if p[0] < 0 else coast_point(p[1], 0) + [p[0], 0]
        return np.array([xy[0], xy[1], p[2]])
    if frame == "world":
        return np.array(p, float)
    if frame in ("plan", "top"):
        w = C.plan_to_world([p[:2]])[0]
        g = float(C.TERRAIN_HEIGHT(np.array([w]))[0])
        return np.array([w[0], w[1], g + p[2]])
    loc, rz = hero_frame()
    c, s = math.cos(rz), math.sin(rz)
    return np.array([loc[0] + p[0] * c - p[1] * s, loc[1] + p[0] * s + p[1] * c, loc[2] + p[2]])


def build():
    import bpy
    from mathutils import Vector
    col = C.collection("13_CAMERAS")
    out = {}
    for name, (frame, pos, tgt, lens, hf, purpose) in SHOTS.items():
        cam = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
        cam.lens = lens
        cam.sensor_fit = "VERTICAL"
        cam.sensor_height = 36.0
        cam.clip_start = 0.05
        cam.clip_end = 150000          # horizon from 200 m is ~50 km away
        C.remove_object(name)
        ob = bpy.data.objects.new(name, cam)
        col.objects.link(ob)
        P = resolve(frame, pos)
        ob.location = Vector(P)
        if frame == "top":
            ob.rotation_euler = (0, 0, C.yaw() - math.pi / 2 + math.pi)
        else:
            T = resolve("world" if frame == "coast" else frame, tgt)
            d = Vector(T) - Vector(P)
            ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
            if name in DOF:
                cam.dof.use_dof = True
                cam.dof.aperture_fstop = DOF[name]
                cam.dof.focus_distance = d.length
        ob["purpose"] = purpose
        ob["higgsfield"] = hf
        ground = float(C.TERRAIN_HEIGHT(np.array([P[:2]]))[0])
        out[name] = {"pos": [round(v, 1) for v in P], "lens": lens, "above_ground_m": round(P[2] - ground, 1)}
    bpy.context.scene.camera = bpy.data.objects["SH05_GARDEN_REVEAL"]
    return out


def render(name, folder=None, samples=None):
    import bpy
    sc = bpy.context.scene
    sc.camera = bpy.data.objects[name]
    if samples:
        sc.cycles.samples = samples
    folder = folder or C.PREVIEWS
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92
    sc.render.filepath = os.path.join(folder, name + ".jpg")
    bpy.ops.render.render(write_still=True)
    print("[render] saved", sc.render.filepath, flush=True)
