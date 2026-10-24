"""
10_fetch_geo — the real surroundings of the 1er TRANCHE: ground heights and a satellite image round
the site, for the terrain and the ocean of the scene (05_build_scene builds them from data/geo/).

    python 10_fetch_geo.py          (outside Blender; needs network, numpy, Pillow, pyproj, rasterio)

Georeference: the plan's coordinates are local, so the centre of the tranche (centroid of its region)
is put at the point the client placed on the map, 29°32'54.74"N 10°03'10.50"W (Google Earth ground
60.88 m, as the model's levels), the plan's north arrow taken as true north, metres 1:1 (azimuthal
equidistant projection on that point).

Sources (free and open):
  heights   AWS Terrain Tiles ('terrarium', SRTM on land, ETOPO1 bathymetry at sea), metres above sea
  image     Sentinel-2 L2A true colour (TCI, 10 m), the least cloudy summer scene of tile 29RLN
            (AWS open data 'sentinel-cogs'). Attribution: Contains modified Copernicus Sentinel data.
Writes data/geo/: dem_near.npz (20 m grid, ±3 km), dem_far.npz (150 m grid, ±12 km), sat_near.jpg
(±3 km), sat_far.jpg (±12 km), geo.json (georeference, scene, extents).
"""
import io
import json
import math
import os
import ssl
import urllib.request

import numpy as np
from PIL import Image, ImageEnhance
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "geo")
SITE = json.load(open(os.path.join(ROOT, "data", "site.json")))
PIN = (29 + 32 / 60 + 54.74 / 3600, -(10 + 3 / 60 + 10.50 / 3600))
NEAR, NEAR_STEP = 3000.0, 20.0
FAR, FAR_STEP = 12000.0, 150.0
S2 = "https://sentinel-cogs.s3.us-west-2.amazonaws.com"
S2_TILE = "sentinel-s2-l2a-cogs/29/R/LN"
CA = "/root/.ccr/ca-bundle.crt"
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
if os.path.exists(CA):
    os.environ.setdefault("CURL_CA_BUNDLE", CA)
    os.environ.setdefault("GDAL_HTTP_CAINFO", CA)


def get(url):
    with urllib.request.urlopen(url, context=CTX, timeout=60) as r:
        return r.read()


def centre():
    t1 = unary_union([Polygon(p["ext"], p["holes"]).buffer(0) for p in SITE["t1_region"]])
    return t1.centroid.x, t1.centroid.y


CX, CY = centre()
AEQD = f"+proj=aeqd +lat_0={PIN[0]} +lon_0={PIN[1]} +x_0={CX} +y_0={CY} +datum=WGS84 +units=m +no_defs"
TO_LL = Transformer.from_crs(AEQD, "EPSG:4326", always_xy=True)
TO_UTM = Transformer.from_crs(AEQD, "EPSG:32629", always_xy=True)


def terrarium(xs, ys, z):
    """Heights (m above sea) on the local grid xs x ys from the terrarium tiles at zoom z (bilinear)."""
    X, Y = np.meshgrid(xs, ys)
    lon, lat = TO_LL.transform(X, Y)
    n = 2 ** z
    px = (lon + 180.0) / 360.0 * n * 256
    lr = np.radians(lat)
    py = (1 - np.log(np.tan(lr) + 1 / np.cos(lr)) / math.pi) / 2 * n * 256
    tx0, tx1 = int(px.min() // 256), int(px.max() // 256)
    ty0, ty1 = int(py.min() // 256), int(py.max() // 256)
    mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            im = np.asarray(Image.open(io.BytesIO(get(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{tx}/{ty}.png"))).convert("RGB"), np.float32)
            h = im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768
            mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = h
    u, v = px - tx0 * 256 - 0.5, py - ty0 * 256 - 0.5
    i0, j0 = np.clip(np.floor(v).astype(int), 0, mos.shape[0] - 2), np.clip(np.floor(u).astype(int), 0, mos.shape[1] - 2)
    fv, fu = np.clip(v - i0, 0, 1), np.clip(u - j0, 0, 1)
    return (mos[i0, j0] * (1 - fu) * (1 - fv) + mos[i0, j0 + 1] * fu * (1 - fv)
            + mos[i0 + 1, j0] * (1 - fu) * fv + mos[i0 + 1, j0 + 1] * fu * fv)


def cloud_score(pre, half=FAR):
    """Share of cloud (bright) and shadow (dark) pixels over the land of the far square, on an overview."""
    import rasterio
    from rasterio.windows import from_bounds
    E, N = TO_UTM.transform(*np.meshgrid(np.linspace(CX - half, CX + half, 5), np.linspace(CY - half, CY + half, 5)))
    with rasterio.open(f"/vsicurl/{S2}/{pre}TCI.tif") as src:
        win = from_bounds(E.min(), N.min(), E.max(), N.max(), src.transform)
        a = src.read([1, 2, 3], window=win, out_shape=(3, 160, 160), boundless=True, fill_value=0).astype(np.float32)
    if (a.sum(0) == 0).mean() > 0.02:
        return 1.0                                               # no data over part of the area
    land = a[0] > a[2] * 1.15                                    # ochre land; the sea is blue-grey
    if land.mean() < 0.2:
        return 1.0
    bright = (a.min(0) > 165) & land | (a.min(0) > 190)
    dark = (a.max(0) < 45) & land
    return float((bright | dark)[land | (a.min(0) > 190)].mean())


def best_scene():
    """The summer scene of tile 29RLN (2023-2025) with the least cloud and cloud shadow over Mirleft,
    measured on the image itself (the tile's cloud percentage misses small cumulus)."""
    import re
    best = None
    for y in (2025, 2024, 2023):
        for m in (5, 6, 7, 8, 9, 10, 4, 11):
            xml = get(f"{S2}/?list-type=2&prefix={S2_TILE}/{y}/{m}/&delimiter=/").decode()
            for pre in re.findall(r"<Prefix>([^<]*_L2A/)</Prefix>", xml):
                try:
                    sc = cloud_score(pre)
                except Exception:
                    continue
                if best is None or sc < best[0]:
                    best = (sc, pre)
                    print("  candidate", pre.split("/")[-2], round(sc, 4), flush=True)
            if best and best[0] < 0.002:
                return best
    return best


def satellite(pre, half, size, path, gain=0.66):
    """True-colour image of the local square ±half (size px), resampled through the UTM grid."""
    import rasterio
    from rasterio.windows import from_bounds
    xs = np.linspace(CX - half, CX + half, 9)
    E, N = TO_UTM.transform(*np.meshgrid(xs, np.linspace(CY - half, CY + half, 9)))
    with rasterio.open(f"/vsicurl/{S2}/{pre}TCI.tif") as src:
        pad = 100.0
        win = from_bounds(E.min() - pad, N.min() - pad, E.max() + pad, N.max() + pad, src.transform)
        dec = max(1, int(round(2 * half / size / 10.0)))           # read an overview when it is coarse
        h_, w_ = int(win.height / dec), int(win.width / dec)
        rgb = src.read([1, 2, 3], window=win, out_shape=(3, h_, w_), boundless=True, fill_value=0).astype(np.float32)
        wt = src.window_transform(win)
    # output pixel centres -> local -> UTM -> source pixel (bilinear)
    g = (np.arange(size) + 0.5) / size
    X, Y = np.meshgrid(CX - half + 2 * half * g, CY + half - 2 * half * g)
    E, N = TO_UTM.transform(X, Y)
    col = (E - wt.c) / (wt.a * win.width / w_)
    row = (N - wt.f) / (wt.e * win.height / h_)
    c0, r0 = np.clip(np.floor(col - 0.5).astype(int), 0, w_ - 2), np.clip(np.floor(row - 0.5).astype(int), 0, h_ - 2)
    fc, fr = np.clip(col - 0.5 - c0, 0, 1), np.clip(row - 0.5 - r0, 0, 1)
    out = np.zeros((size, size, 3), np.float32)
    for k in range(3):
        b = rgb[k]
        out[..., k] = (b[r0, c0] * (1 - fc) * (1 - fr) + b[r0, c0 + 1] * fc * (1 - fr)
                       + b[r0 + 1, c0] * (1 - fc) * fr + b[r0 + 1, c0 + 1] * fc * fr)
    im = Image.fromarray(np.clip(out * gain, 0, 255).astype(np.uint8))
    im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.12)).enhance(0.95)   # it renders as albedo under the sun
    im.save(path, quality=90)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    xs = np.arange(CX - NEAR, CX + NEAR + 1e-6, NEAR_STEP)
    ys = np.arange(CY - NEAR, CY + NEAR + 1e-6, NEAR_STEP)
    np.savez_compressed(os.path.join(OUT, "dem_near.npz"), xs=xs, ys=ys, h=terrarium(xs, ys, 13).astype(np.float32))
    xf = np.arange(CX - FAR, CX + FAR + 1e-6, FAR_STEP)
    yf = np.arange(CY - FAR, CY + FAR + 1e-6, FAR_STEP)
    np.savez_compressed(os.path.join(OUT, "dem_far.npz"), xs=xf, ys=yf, h=terrarium(xf, yf, 10).astype(np.float32))
    print("DEM near", len(xs), "x", len(ys), " far", len(xf), "x", len(yf), flush=True)
    gp = os.path.join(OUT, "geo.json")
    if os.path.exists(gp):                                         # keep the scene chosen before
        g = json.load(open(gp))
        cc, pre = g["cloud_pct"], f"{S2_TILE}/{g['scene'].split('_')[2][:4]}/{int(g['scene'].split('_')[2][4:6])}/{g['scene']}/"
    else:
        cc, pre = best_scene()
    print("SCENE", pre, "cloud", cc, flush=True)
    satellite(pre, NEAR, 2048, os.path.join(OUT, "sat_near.jpg"))
    satellite(pre, FAR, 2048, os.path.join(OUT, "sat_far.jpg"))
    lon, lat = TO_LL.transform(CX, CY)
    json.dump({"pin_lat_lon": PIN, "centre_local": [CX, CY], "centre_lat_lon": [lat, lon], "proj": AEQD,
               "near": [CX - NEAR, CY - NEAR, CX + NEAR, CY + NEAR], "far": [CX - FAR, CY - FAR, CX + FAR, CY + FAR],
               "scene": pre.rstrip("/").split("/")[-1], "cloud_pct": cc,
               "attribution": "Contains modified Copernicus Sentinel data (Sentinel-2 L2A, AWS open data). "
                              "Heights: AWS Terrain Tiles (SRTM, ETOPO1)."},
              open(os.path.join(OUT, "geo.json"), "w"), indent=1)
    print("GEO done", OUT)


if __name__ == "__main__":
    main()
