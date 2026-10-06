"""Bovenaanzicht-render van museumplein.blend in exact het raster van de drone-plattegrond.

Elevated geometrie wordt verschoven met de drone-schuinstand (LEAN), zodat de render
1-op-1 over refs/drone_rectified.png past. Output: renders/check/top_<tag>.png (RGBA).
Gebruik: Blender -b museumplein.blend -P scripts/render_top.py -- <tag> [collectie-filter]
"""
import json
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

LEAN = (0.07, 0.25)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
tag = argv[0] if argv else "all"
filt = argv[1] if len(argv) > 1 else ""

meta = json.load(open(os.path.join(C.REFS, "drone_rectified.json")))
x0, x1, y0, y1, mpp = meta["x0"], meta["x1"], meta["y0"], meta["y1"], meta["mpp"]
W, H = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp))
scene = bpy.context.scene

# lean via geometry nodes: positie += (LEAN.x*z, LEAN.y*z, 0)
ng = bpy.data.node_groups.new("lean", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
n_in = ng.nodes.new("NodeGroupInput")
n_out = ng.nodes.new("NodeGroupOutput")
pos = ng.nodes.new("GeometryNodeInputPosition")
sep = ng.nodes.new("ShaderNodeSeparateXYZ")
comb = ng.nodes.new("ShaderNodeCombineXYZ")
mx = ng.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY"; mx.inputs[1].default_value = LEAN[0]
my = ng.nodes.new("ShaderNodeMath"); my.operation = "MULTIPLY"; my.inputs[1].default_value = LEAN[1]
setp = ng.nodes.new("GeometryNodeSetPosition")
ng.links.new(pos.outputs[0], sep.inputs[0])
ng.links.new(sep.outputs[2], mx.inputs[0])
ng.links.new(sep.outputs[2], my.inputs[0])
ng.links.new(mx.outputs[0], comb.inputs[0])
ng.links.new(my.outputs[0], comb.inputs[1])
ng.links.new(n_in.outputs[0], setp.inputs["Geometry"])
ng.links.new(comb.outputs[0], setp.inputs["Offset"])
ng.links.new(setp.outputs[0], n_out.inputs[0])

for obj in scene.objects:
    if obj.type != "MESH":
        continue
    keep = (not filt) or any(filt in c.name for c in obj.users_collection) or obj.name.startswith(filt)
    obj.hide_render = not keep
    if keep:
        m = obj.modifiers.new("lean", "NODES")
        m.node_group = ng

C.setup_workbench(scene, W, H, color_type="OBJECT" if os.environ.get("OBJCOL") else "MATERIAL", outline=False)
if os.environ.get("OBJCOL"):
    import random
    rnd = random.Random(7)
    for obj in scene.objects:
        obj.color = (rnd.random(), rnd.random(), rnd.random(), 1.0)
scene.display.shading.light = "FLAT"
scene.display.render_aa = "OFF"
scene.display.shading.show_specular_highlight = False
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
cam = C.ortho_camera(scene, (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0), z=80.0)
cam.data.sensor_fit = "VERTICAL" if H > W else "HORIZONTAL"
cam.data.ortho_scale = max(x1 - x0, y1 - y0)
os.makedirs(os.path.join(C.RENDERS, "check"), exist_ok=True)
C.render(scene, os.path.join(C.RENDERS, "check", f"top_{tag}.png"))
