"""Rendert een uitsnede van een foto met pixelgrid (om pixelcoördinaten af te lezen).

Gebruik: Blender -b -P measure_photo.py -- <foto> <naam> <px_cx> <px_cy> <breedte_px> <render_px> [stap_px]
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
photo, name = a[0], a[1]
pcx, pcy, wpx, rpx = float(a[2]), float(a[3]), float(a[4]), int(a[5])
step = float(a[6]) if len(a) > 6 else 50.0

scene = C.reset_scene()
img = bpy.data.images.load(os.path.abspath(photo))
W, H = img.size
S = 0.01  # 1 pixel = 0.01 unit; pixel (px,py) -> (px*S, -py*S)
mesh = bpy.data.meshes.new("photo")
mesh.from_pydata([(0, 0, -0.01), (W * S, 0, -0.01), (W * S, -H * S, -0.01), (0, -H * S, -0.01)], [], [(0, 1, 2, 3)])
uv = mesh.uv_layers.new(name="UVMap")
for loop, co in zip(mesh.loops, [(0, 1), (1, 1), (1, 0), (0, 0)]):
    uv.data[loop.index].uv = co
obj = bpy.data.objects.new("photo", mesh)
scene.collection.objects.link(obj)
mat = bpy.data.materials.new("photo")
mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = img
emit = nt.nodes.new("ShaderNodeEmission")
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
nt.nodes.active = tex
mesh.materials.append(mat)

# grid in pixelruimte; labels tonen pixelcoördinaten
x0, x1 = pcx - wpx / 2, pcx + wpx / 2
y0, y1 = pcy - wpx / 2, pcy + wpx / 2
gmat = C.flat_material("g", (0.1, 0.9, 1.0))
lmat = C.flat_material("l", (1.0, 0.0, 1.0))
verts, faces = [], []
w = wpx * S / 900
gx = (int(x0 // step) + 1) * step
while gx < x1:
    i = len(verts)
    X = gx * S
    verts += [(X - w, -y0 * S, 0), (X + w, -y0 * S, 0), (X + w, -y1 * S, 0), (X - w, -y1 * S, 0)]
    faces.append((i, i + 1, i + 2, i + 3))
    gx += step
gy = (int(y0 // step) + 1) * step
while gy < y1:
    i = len(verts)
    Y = -gy * S
    verts += [(x0 * S, Y - w, 0), (x1 * S, Y - w, 0), (x1 * S, Y + w, 0), (x0 * S, Y + w, 0)]
    faces.append((i, i + 1, i + 2, i + 3))
    gy += step
gm = bpy.data.meshes.new("grid")
gm.from_pydata(verts, [], faces)
gm.materials.append(gmat)
go = bpy.data.objects.new("grid", gm)
scene.collection.objects.link(go)
lab_step = step * 2
gx = (int(x0 // lab_step) + 1) * lab_step
while gx < x1:
    gy = (int(y0 // lab_step) + 1) * lab_step
    while gy < y1:
        cu = bpy.data.curves.new("t", "FONT")
        cu.body = f"{int(gx)},{int(gy)}"
        cu.size = wpx * S / 45
        cu.materials.append(lmat)
        t = bpy.data.objects.new("t", cu)
        t.location = (gx * S + 0.02 * wpx * S / 10, -gy * S + 0.02 * wpx * S / 10, 0.01)
        scene.collection.objects.link(t)
        gy += lab_step
    gx += lab_step

C.setup_workbench(scene, rpx, rpx, color_type="TEXTURE", outline=False)
scene.display.shading.light = "FLAT"
C.ortho_camera(scene, pcx * S, -pcy * S, wpx * S)
os.makedirs(os.path.join(C.RENDERS, "measure"), exist_ok=True)
C.render(scene, os.path.join(C.RENDERS, "measure", f"{name}.png"))
