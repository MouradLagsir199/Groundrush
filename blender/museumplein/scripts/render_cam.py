"""Rendert museumplein.blend vanuit een teruggerekende fotocamera (refs/cam_<foto>.json).

Output: renders/check/cam_<foto>_<tag>.png (RGBA, zelfde resolutie als de foto).
Gebruik: Blender -b museumplein.blend -P scripts/render_cam.py -- <foto> <tag> [collectie-filter]
"""
import json
import os
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
photo, tag = argv[0], argv[1]
filt = argv[2] if len(argv) > 2 else ""
cam_json = json.load(open(os.path.join(C.REFS, f"cam_{photo}.json")))
W, H = 2000, 1334

# OpenCV-rotatie (wereld->camera) uit Rodrigues-vector
import math
rx, ry, rz = cam_json["rvec"]
theta = math.sqrt(rx * rx + ry * ry + rz * rz)
if theta < 1e-12:
    R = Matrix.Identity(3)
else:
    k = [rx / theta, ry / theta, rz / theta]
    K = Matrix(((0, -k[2], k[1]), (k[2], 0, -k[0]), (-k[1], k[0], 0)))
    R = Matrix.Identity(3) + math.sin(theta) * K + (1 - math.cos(theta)) * (K @ K)
flip = Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1)))
Rbl = R.transposed() @ flip  # camera->wereld voor Blender (kijkt langs -Z, Y omhoog)

scene = bpy.context.scene
cd = bpy.data.cameras.new("photo_cam")
cd.sensor_fit = "HORIZONTAL"
cd.sensor_width = 36.0
cd.lens = cam_json["f"] * 36.0 / W
cd.shift_x = (W / 2 - cam_json.get("cx", W / 2)) / W
cd.shift_y = (cam_json.get("cy", H / 2) - H / 2) / W
cd.clip_start = 0.1
cd.clip_end = 500
cam = bpy.data.objects.new("photo_cam", cd)
M = Rbl.to_4x4()
M.translation = cam_json["cam_pos"]
cam.matrix_world = M
scene.collection.objects.link(cam)
scene.camera = cam

for obj in scene.objects:
    if obj.type in ("MESH", "CURVE"):
        keep = (not filt) or any(filt in c.name for c in obj.users_collection) or obj.name.startswith(filt)
        obj.hide_render = not keep

C.setup_workbench(scene, W, H, color_type="OBJECT" if os.environ.get("OBJCOL") else "MATERIAL", outline=False)
if os.environ.get("OBJCOL"):
    import random
    rnd = random.Random(7)
    for obj in scene.objects:
        obj.color = (rnd.random(), rnd.random(), rnd.random(), 1.0)
scene.display.shading.light = "STUDIO" if os.environ.get("SHADED") else "FLAT"
if os.environ.get("SHADED"):
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.curvature_ridge_factor = 2.0
    scene.display.shading.curvature_valley_factor = 2.0
scene.display.render_aa = "OFF" if not os.environ.get("SHADED") else "8"
scene.display.shading.show_specular_highlight = False
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
os.makedirs(os.path.join(C.RENDERS, "check"), exist_ok=True)
C.render(scene, os.path.join(C.RENDERS, "check", f"cam_{photo}_{tag}.png"))
