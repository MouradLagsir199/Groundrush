"""Vrije perspectiefrender (studio-licht + cavity) voor visuele inspectie.
Gebruik: Blender -b museumplein.blend -P render_persp.py -- naam camx camy camz doelx doely doelz [lens] [wire]
"""
import os, sys
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
a = sys.argv[sys.argv.index("--") + 1:]
name = a[0]; loc = tuple(map(float, a[1:4])); tgt = tuple(map(float, a[4:7]))
lens = float(a[7]) if len(a) > 7 else 30
scene = bpy.context.scene
C.setup_workbench(scene, 1600, 1000, color_type="MATERIAL", outline=True, cavity=True)
scene.display.shading.light = "STUDIO"
if len(a) > 8 and a[8] == "wire":
    scene.display.shading.show_xray = False
    for o in scene.objects:
        if o.type == "MESH":
            m = o.modifiers.new("w", "WIREFRAME"); m.thickness = 0.004; m.use_replace = False
C.persp_camera(scene, loc, tgt, lens)
os.makedirs(os.path.join(C.RENDERS, "views"), exist_ok=True)
C.render(scene, os.path.join(C.RENDERS, "views", f"{name}.png"))
