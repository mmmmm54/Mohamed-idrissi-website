"""07_save_packed_2k — light copy of the scene: every texture packed inside, scaled to 2K max
(about 14 MB, small enough to send).   python 07_save_packed_2k.py"""
import os
import tempfile
import bpy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "Mirleft_Tranche_AB.blend"))
tmp = tempfile.mkdtemp()
for im in bpy.data.images:
    if im.source != "FILE":
        continue
    im.reload()
    w, h = im.size
    if max(w, h) > 2048:
        im.scale(int(w * 2048 / max(w, h)), int(h * 2048 / max(w, h)))
    png = im.filepath.lower().endswith(".png")
    p = os.path.join(tmp, im.name.rsplit(".", 1)[0] + (".png" if png else ".jpg"))
    im.filepath_raw = p
    im.file_format = "PNG" if png else "JPEG"
    im.save()
    im.filepath = p
    im.reload()
bpy.ops.file.pack_all()
dst = os.path.join(ROOT, "Mirleft_Tranche_AB_PACKED_2K.blend")
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, copy=True)
print("PACKED_2K", round(os.path.getsize(dst) / 2 ** 20, 1), "MiB")
