"""Rendert maskers van donkere objecten (ledges, staal) vanuit een fotocamera bij verschillende hoogteschalen s.
Gebruik: Blender -b museumplein.blend -P render_scale_masks.py -- <foto> s1 s2 ...
"""
import json, math, os, sys
import bpy
from mathutils import Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

a = sys.argv[sys.argv.index("--") + 1:]
photo = a[0]; scales = [float(v) for v in a[1:]]
cj = json.load(open(os.path.join(C.REFS, f"cam_{photo}.json")))
W, H = 2000, 1334
rx, ry, rz = cj["rvec"]; th = math.sqrt(rx * rx + ry * ry + rz * rz)
k = [rx / th, ry / th, rz / th]
K = Matrix(((0, -k[2], k[1]), (k[2], 0, -k[0]), (-k[1], k[0], 0)))
R = Matrix.Identity(3) + math.sin(th) * K + (1 - math.cos(th)) * (K @ K)
Rbl = R.transposed() @ Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1)))
scene = bpy.context.scene
cd = bpy.data.cameras.new("pc"); cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 36.0; cd.lens = cj["f"] * 36.0 / W
cd.shift_x = (W / 2 - cj.get("cx", W / 2)) / W; cd.shift_y = (cj.get("cy", H / 2) - H / 2) / W; cd.clip_end = 500
cam = bpy.data.objects.new("pc", cd); M = Rbl.to_4x4(); M.translation = cj["cam_pos"]; cam.matrix_world = M
scene.collection.objects.link(cam); scene.camera = cam
dark = {"ledge_zijkant", "staal_zwart", "staal_coping"}
white = bpy.data.materials.new("W"); white.diffuse_color = (1, 1, 1, 1)
black = bpy.data.materials.new("B"); black.diffuse_color = (0, 0, 0, 1)
root = bpy.data.objects.new("ROOT", None); scene.collection.objects.link(root)
for o in list(scene.objects):
    if o.type == "MESH":
        isdark = any(s.material and s.material.name in dark for s in o.material_slots)
        o.data.materials.clear(); o.data.materials.append(black if isdark else white)
        mw = o.matrix_world.copy(); o.parent = root; o.matrix_world = mw
C.setup_workbench(scene, W, H, color_type="MATERIAL", outline=False)
scene.display.shading.light = "FLAT"; scene.display.render_aa = "OFF"
scene.render.film_transparent = True; scene.render.image_settings.color_mode = "RGBA"
os.makedirs(os.path.join(C.RENDERS, "scale"), exist_ok=True)
for s in scales:
    root.scale = (1, 1, s)
    bpy.context.view_layer.update()
    C.render(scene, os.path.join(C.RENDERS, "scale", f"{photo}_s{s:.2f}.png"))
