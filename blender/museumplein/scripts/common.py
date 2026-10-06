"""Gedeelde helpers voor de Museumplein-blender-scripts.

Coördinaten: 1 Blender-unit = 1 meter. X = oost, Y = noord (RD-uitgelijnd).
Oorsprong = RD (120710, 485730), het midden van de luchtfoto.
"""
import math
import os

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
RENDERS = os.path.join(ROOT, "renders")

RD_ORIGIN = (120710.0, 485730.0)
ORTHO_FILE = os.path.join(REFS, "ortho_2026_orthoHR.jpg")
ORTHO_BBOX = (120675.0, 485695.0, 120745.0, 485765.0)  # minx, miny, maxx, maxy (RD)


def rd_to_local(x, y):
    return x - RD_ORIGIN[0], y - RD_ORIGIN[1]


def px_to_local(px, py, size=1400):
    """Pixel in de 1400x1400 luchtfoto -> lokale meters."""
    minx, miny, maxx, maxy = ORTHO_BBOX
    mpp = (maxx - minx) / size
    return rd_to_local(minx + px * mpp, maxy - py * mpp)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def get_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


def flat_material(name, rgb, alpha=1.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, alpha)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
    return mat


def add_ortho_plane(z=-0.01, collection=None):
    """Luchtfoto als vlak op exacte schaal."""
    minx, miny, maxx, maxy = ORTHO_BBOX
    x0, y0 = rd_to_local(minx, miny)
    x1, y1 = rd_to_local(maxx, maxy)
    mesh = bpy.data.meshes.new("ortho")
    mesh.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name="UVMap")
    for loop, co in zip(mesh.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[loop.index].uv = co
    obj = bpy.data.objects.new("REF_ortho_2026", mesh)
    (collection or bpy.context.scene.collection).objects.link(obj)

    mat = bpy.data.materials.new("REF_ortho")
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(ORTHO_FILE)
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    nt.nodes.active = tex
    mesh.materials.append(mat)
    return obj


def add_grid(x0, y0, x1, y1, z=0.0, step=1.0, major=5, collection=None, labels=True, label_size=0.45):
    """Metergrid als dunne strips + labels elke `major` meter."""
    col = collection or get_collection("REF_grid")
    minor_mat = flat_material("REF_grid_minor", (0.1, 0.9, 1.0))
    major_mat = flat_material("REF_grid_major", (1.0, 0.1, 0.1))
    verts, faces_minor, faces_major = [], [], []

    def strip(a, b, w, target):
        (ax, ay), (bx, by) = a, b
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln * w / 2, dx / ln * w / 2
        i = len(verts)
        verts.extend([(ax + nx, ay + ny, z), (bx + nx, by + ny, z), (bx - nx, by - ny, z), (ax - nx, ay - ny, z)])
        target.append((i, i + 1, i + 2, i + 3))

    gx = math.ceil(x0 / step) * step
    while gx <= x1 + 1e-6:
        is_major = abs(round(gx) % major) < 1e-6 and abs(gx - round(gx)) < 1e-6
        strip((gx, y0), (gx, y1), 0.03 if is_major else 0.012, faces_major if is_major else faces_minor)
        gx += step
    gy = math.ceil(y0 / step) * step
    while gy <= y1 + 1e-6:
        is_major = abs(round(gy) % major) < 1e-6 and abs(gy - round(gy)) < 1e-6
        strip((x0, gy), (x1, gy), 0.03 if is_major else 0.012, faces_major if is_major else faces_minor)
        gy += step

    mesh = bpy.data.meshes.new("grid")
    mesh.from_pydata(verts, [], faces_minor + faces_major)
    mesh.materials.append(minor_mat)
    mesh.materials.append(major_mat)
    for i, poly in enumerate(mesh.polygons):
        poly.material_index = 0 if i < len(faces_minor) else 1
    obj = bpy.data.objects.new("REF_grid", mesh)
    col.objects.link(obj)

    if labels:
        lab_mat = flat_material("REF_grid_label", (1.0, 0.0, 1.0))
        gx = math.ceil(x0 / major) * major
        while gx <= x1:
            gy = math.ceil(y0 / major) * major
            while gy <= y1:
                cu = bpy.data.curves.new(f"lab_{gx}_{gy}", "FONT")
                cu.body = f"{int(gx)},{int(gy)}"
                cu.size = label_size
                t = bpy.data.objects.new(f"REF_label_{gx}_{gy}", cu)
                t.location = (gx + 0.08, gy + 0.08, z + 0.01)
                cu.materials.append(lab_mat)
                col.objects.link(t)
                gy += major
            gx += major
    return obj


def setup_workbench(scene, res_x, res_y, color_type="MATERIAL", outline=True, cavity=False):
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = color_type
    sh.show_object_outline = outline
    sh.show_cavity = cavity
    if cavity:
        sh.cavity_type = "BOTH"
    scene.display.render_aa = "8"
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    scene.world = world


def ortho_camera(scene, cx, cy, width, height_m=None, z=50.0, name="CAM_top"):
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(width, height_m or width)
    cam_data.clip_end = 500
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = (cx, cy, z)
    cam.rotation_euler = (0, 0, 0)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def persp_camera(scene, loc, target, lens=24, name="CAM_persp"):
    from mathutils import Vector
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_end = 1000
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def render(scene, path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
