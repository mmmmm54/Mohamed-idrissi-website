"""
14_build_lighting — physically placed sun + Nishita sky, six presets.

Sun positions are computed for 29.553 N, 10.060 W (UTC+1) with the NOAA solar equations,
so the light direction is true to the site orientation (PROJECT_BIBLE §05, §32).
Master look = LIGHTING_03_GOLDEN_HOUR (client, 2026-10-01).
"""
import datetime as dt
import math

C = globals()["C"]

# (preset, date, local time, sun strength, sky strength, sky air/dust, interior lamps)
PRESETS = {
    "LIGHTING_01_DAYLIGHT":    ((2026, 10, 15), (13, 30), 4.0, 1.0, (1.0, 1.0), 0.0),
    "LIGHTING_02_MORNING":     ((2026, 10, 15), (9, 30), 3.2, 0.9, (1.0, 1.2), 0.0),
    "LIGHTING_03_GOLDEN_HOUR": ((2026, 10, 15), (18, 20), 4.6, 0.9, (1.4, 1.2), 0.8),
    "LIGHTING_04_SUNSET":      ((2026, 10, 15), (19, 2), 1.6, 0.35, (1.4, 4.0), 1.0),
    "LIGHTING_05_BLUE_HOUR":   ((2026, 10, 15), (19, 30), 0.0, 0.12, (1.0, 1.0), 1.4),
    "LIGHTING_06_NIGHT":       ((2026, 10, 15), (22, 30), 0.0, 0.01, (1.0, 1.0), 1.6),
}
MASTER = "LIGHTING_03_GOLDEN_HOUR"


def solar_position(date, hm, lat=None, lon=None, utc=None):
    """Return (azimuth deg from north, clockwise; elevation deg). NOAA algorithm."""
    lat = C.LATITUDE if lat is None else lat
    lon = C.LONGITUDE if lon is None else lon
    utc = C.UTC_OFFSET if utc is None else utc
    t = dt.datetime(*date, hm[0], hm[1])
    doy = t.timetuple().tm_yday
    hour = hm[0] + hm[1] / 60
    g = 2 * math.pi / 365 * (doy - 1 + (hour - 12) / 24)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g)
            - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    tst = hour * 60 + eqt + 4 * lon - 60 * utc
    ha = math.radians(tst / 4 - 180)
    la = math.radians(lat)
    cz = math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)
    zen = math.acos(max(-1, min(1, cz)))
    el = 90 - math.degrees(zen)
    az = math.degrees(math.atan2(math.sin(ha), math.cos(ha) * math.sin(la) - math.tan(decl) * math.cos(la))) + 180
    return az % 360, el


def apply(preset=MASTER):
    import bpy
    from mathutils import Vector
    date, hm, sun_s, sky_s, (air, dust), lamps = PRESETS[preset]
    az, el = solar_position(date, hm)
    sc = bpy.context.scene
    col = C.collection("12_LIGHTING")
    world = bpy.data.worlds.get("WORLD_SKY") or bpy.data.worlds.new("WORLD_SKY")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_disc = True
    sky.sun_size = math.radians(0.545)
    sky.sun_elevation = math.radians(max(el, -6))
    # Nishita: sun_rotation 0 = sun towards +X (east); counter-clockwise. Bearing az -> 90 - az.
    sky.sun_rotation = math.radians((90 - az) % 360)
    sky.altitude = 30.0
    sky.air_density = air
    sky.dust_density = dust
    sky.ozone_density = 1.0
    sky.sun_intensity = 1.0
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = sky_s * 0.35
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    # explicit sun lamp (sharper shadows, warm tint at low sun)
    C.remove_object("SUN")
    sun = bpy.data.lights.get("SUN") or bpy.data.lights.new("SUN", "SUN")
    warm = max(0.0, min(1.0, (15 - el) / 15))
    sun.color = (1.0, 0.90 - 0.24 * warm, 0.78 - 0.40 * warm)
    sun.energy = sun_s if el > -1 else 0.0
    sun.angle = math.radians(0.6)
    ob = bpy.data.objects.new("SUN", sun)
    col.objects.link(ob)
    d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)),
                math.cos(math.radians(az)) * math.cos(math.radians(el)),
                math.sin(math.radians(el))))
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    # interior lamps glow (golden hour / evening)
    lamp = bpy.data.materials.get("Lamp_Warm")
    if lamp:
        lamp.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 25.0 * max(lamps, 0.05)
    inter = bpy.data.materials.get("A06_Interior_Proxy")
    if inter:
        inter.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.6 * max(lamps, 0.15)
    sc["lighting_preset"] = preset
    sc["sun_azimuth_deg"] = round(az, 2)
    sc["sun_elevation_deg"] = round(el, 2)
    return az, el


def build(materials=None):
    import bpy
    report = {p: solar_position(v[0], v[1]) for p, v in PRESETS.items()}
    txt = bpy.data.texts.get("LIGHTING_PRESETS.txt") or bpy.data.texts.new("LIGHTING_PRESETS.txt")
    txt.clear()
    txt.write("Run in Blender's Python console:  exec(bpy.data.texts['LIGHTING_PRESETS.txt'].as_string())\n")
    txt.write("# preset: azimuth / elevation (deg), 29.553N 10.060W, 2026-10-15\n")
    for p, (az, el) in report.items():
        txt.write(f"# {p}: az {az:.1f}  el {el:.1f}\n")
    az, el = apply(MASTER)
    return {p: (round(a, 1), round(e, 1)) for p, (a, e) in report.items()}
