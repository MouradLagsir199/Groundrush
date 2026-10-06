"""Rendert de luchtfoto met metergrid, als meetinstrument voor het natekenen.

Gebruik: Blender -b -P measure.py -- <naam> <cx> <cy> <breedte_m> <pixels>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
name = argv[0] if argv else "overview"
cx, cy, width, pixels = (float(argv[1]), float(argv[2]), float(argv[3]), int(argv[4])) if len(argv) >= 5 else (2.0, -1.0, 50.0, 2000)
step = float(argv[5]) if len(argv) >= 6 else 1.0

scene = C.reset_scene()
C.add_ortho_plane(z=-0.01)
C.add_grid(cx - width / 2, cy - width / 2, cx + width / 2, cy + width / 2, z=0.0, step=step, label_size=max(0.3, width / 40))
C.setup_workbench(scene, pixels, pixels, color_type="TEXTURE", outline=False)
scene.display.shading.light = "FLAT"
C.ortho_camera(scene, cx, cy, width)
os.makedirs(os.path.join(C.RENDERS, "measure"), exist_ok=True)
C.render(scene, os.path.join(C.RENDERS, "measure", f"{name}.png"))
