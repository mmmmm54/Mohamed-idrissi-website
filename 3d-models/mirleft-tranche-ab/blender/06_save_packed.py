"""06_save_packed — copy of the scene with every texture packed inside (opens anywhere), kept only
if it stays under 95 MB (GitHub limit 100 MB).   python 06_save_packed.py"""
import os
import bpy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "Mirleft_Tranche_AB.blend")
dst = os.path.join(ROOT, "Mirleft_Tranche_AB_PACKED.blend")
bpy.ops.wm.open_mainfile(filepath=src)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, copy=True)
mb = os.path.getsize(dst) / 1e6
if mb > 95:
    os.remove(dst)
print("PACKED", round(mb, 1), "MB", "kept" if mb <= 95 else "removed (over 95 MB)")
