"""Bouwt het Museumplein-skatepark in Blender uit data/park.json.

Gebruik: Blender -b --factory-startup -P scripts/build.py -- [stukken...]
Zonder argumenten worden alle stukken gebouwd. Resultaat: museumplein.blend
1 Blender-unit = 1 meter. z=0 = straatvloer.
"""
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

ROOT = C.ROOT
DATA = json.load(open(os.path.join(ROOT, "data", "park.json")))
OUT_BLEND = os.path.join(ROOT, "museumplein.blend")

MAT = {}


def mat(name, rgb, rough=0.85, metal=0.0):
    if name not in MAT:
        m = C.flat_material(name, rgb)
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        MAT[name] = m
    return MAT[name]


def new_obj(name, bm, collection, material=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    obj = bpy.data.objects.new(name, me)
    collection.objects.link(obj)
    if material:
        me.materials.append(material)
    return obj


def polygon_prism(points, z_top, z_bot):
    """Gesloten polygoon (xy) -> prisma van z_bot tot z_top, bovenvlak getrianguleerd."""
    bm = bmesh.new()
    top = [bm.verts.new((x, y, z_top)) for x, y in points]
    bot = [bm.verts.new((x, y, z_bot)) for x, y in points]
    n = len(points)
    ftop = bm.faces.new(top)
    fbot = bm.faces.new(list(reversed(bot)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.triangulate(bm, faces=[ftop, fbot], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def ring_prism(outer, inner, z_top, z_bot):
    """Ring tussen twee gesloten polygonen (buiten, binnen), als massief prisma."""
    bm = bmesh.new()

    def loop(points, z):
        vs = [bm.verts.new((x, y, z)) for x, y in points]
        es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
        return vs, es

    ot, oe = loop(outer, z_top)
    it, ie = loop(inner, z_top)
    res = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=oe + ie)
    top_faces = res["geom"]
    # alleen driehoeken tussen de lussen houden (triangle_fill vult ook het gat)
    inner_poly = [Vector((x, y)) for x, y in inner]

    def inside(pt, poly):
        c = False
        j = len(poly) - 1
        for i in range(len(poly)):
            if ((poly[i].y > pt.y) != (poly[j].y > pt.y)) and (pt.x < (poly[j].x - poly[i].x) * (pt.y - poly[i].y) / (poly[j].y - poly[i].y + 1e-12) + poly[i].x):
                c = not c
            j = i
        return c

    kill = [f for f in top_faces if isinstance(f, bmesh.types.BMFace) and inside(f.calc_center_median().to_2d(), inner_poly)]
    bmesh.ops.delete(bm, geom=kill, context="FACES_ONLY")
    faces = [f for f in bm.faces]
    ext = bmesh.ops.extrude_face_region(bm, geom=faces)
    verts = [v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z_bot - z_top), verts=verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


LEAN = (0.07, 0.25)


def deleaned(xy, z):
    """Drone-plattegrondpositie van een punt op hoogte z -> echte xy."""
    return (xy[0] - LEAN[0] * z, xy[1] - LEAN[1] * z)


def box_mesh(center, angle_deg, length, width, z0, z1, round_ends=0.0, segs=8):
    """Georiënteerde balk; optioneel halfronde koppen (round_ends = straal)."""
    a = math.radians(angle_deg)
    t = Vector((math.cos(a), math.sin(a)))
    n = Vector((-t.y, t.x))
    c = Vector(center)
    pts = []
    if round_ends > 0:
        r = round_ends
        half = length / 2 - r
        for k in range(segs + 1):
            ang = -math.pi / 2 + math.pi * k / segs
            pts.append(c + t * (half + r * math.cos(ang)) + n * (r * math.sin(ang) * (width / 2) / r))
        for k in range(segs + 1):
            ang = math.pi / 2 + math.pi * k / segs
            pts.append(c + t * (-half + r * math.cos(ang)) + n * (r * math.sin(ang) * (width / 2) / r))
    else:
        for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            pts.append(c + t * (sx * length / 2) + n * (sy * width / 2))
    return polygon_prism([(p.x, p.y) for p in pts], z1, z0)


def tube_mesh(points, radius, segs=10):
    """Buis langs een 3D-polylijn (lijst van (x,y,z))."""
    bm = bmesh.new()
    P = [Vector(p) for p in points]
    rings = []
    for i, p in enumerate(P):
        if i == 0:
            d = (P[1] - P[0]).normalized()
        elif i == len(P) - 1:
            d = (P[-1] - P[-2]).normalized()
        else:
            d = ((P[i + 1] - P[i]).normalized() + (P[i] - P[i - 1]).normalized()).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        u = d.cross(up).normalized()
        w = d.cross(u).normalized()
        rings.append([bm.verts.new(p + radius * (math.cos(2 * math.pi * k / segs) * u + math.sin(2 * math.pi * k / segs) * w)) for k in range(segs)])
    for r0, r1 in zip(rings[:-1], rings[1:]):
        for k in range(segs):
            bm.faces.new((r0[k], r0[(k + 1) % segs], r1[(k + 1) % segs], r1[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def join_bms(bms):
    out = bmesh.new()
    for b in bms:
        me = bpy.data.meshes.new("tmp")
        b.to_mesh(me)
        b.free()
        out.from_mesh(me)
        bpy.data.meshes.remove(me)
    return out


def build_ledge(col, name, spec):
    """Ledge: betonnen kern met lichte bovenkant, donkere zijkanten, stalen hoekprofielen langs de bovenranden."""
    c = spec["center"]; ang = spec["angle"]; L = spec["length"]; W = spec["width"]; h = spec["height"]
    z0 = spec.get("z0", 0.0)
    steel = spec.get("steel", 0.03)
    rnd = spec.get("round_ends", 0.0)
    body = new_obj(name + "_kern", box_mesh(c, ang, L, W, z0, z0 + h - 0.005, rnd), col, mat("ledge_zijkant", (0.08, 0.08, 0.085), 0.6))
    top = new_obj(name + "_top", box_mesh(c, ang, L - 2 * steel, W - 2 * steel, z0 + h - 0.006, z0 + h, max(0.0, rnd - steel)), col,
                  mat("ledge_top", (0.70, 0.70, 0.68), 0.7))
    rim = new_obj(name + "_staal", box_mesh(c, ang, L, W, z0 + h - 0.005, z0 + h - 0.001, rnd), col, mat("staal_zwart", (0.03, 0.03, 0.03), 0.35, 0.8))
    objs = [body, top, rim]
    for o in objs:
        o["element"] = name
    return objs


def _interp(pts, s):
    """Lineaire interpolatie in [(s, z), ...]."""
    pts = sorted(pts)
    if s <= pts[0][0]:
        return pts[0][1]
    for (s0, z0), (s1, z1) in zip(pts[:-1], pts[1:]):
        if s <= s1:
            return z0 + (z1 - z0) * (s - s0) / max(1e-9, s1 - s0)
    return pts[-1][1]


def build_hoop_rail(col, name, spec):
    """Rail met hoepels.

    spec: p0, p1 (xy, langs de stang), bar: [(s, z_hart), ...] absolute hoogte van het stanghart,
    floor: [(s, z), ...] vloerhoogte onder de rail, posts: [s...], hoops: [[s_links, s_rechts], ...].
    Oud formaat (bar_z/hoops als middens + hoop_r) wordt ook ondersteund.
    """
    p0 = Vector((*spec["p0"], 0)); p1 = Vector((*spec["p1"], 0))
    t = (p1 - p0)
    L = t.length
    t.normalize()
    rb = spec.get("bar_r", 0.025); rh = spec.get("hoop_r_tube", 0.02)
    floor_pts = spec.get("floor", [(0.0, 0.0), (L, 0.0)])
    if "bar" in spec:
        bar_pts = spec["bar"]
    else:
        bz = spec["bar_z"]
        bar_pts = [(0.0, _interp(floor_pts, 0.0) + bz), (L, _interp(floor_pts, L) + bz)]
    hoops = spec.get("hoops", [])
    if hoops and not isinstance(hoops[0], (list, tuple)):
        r = spec.get("hoop_r", 0.22)
        hoops = [[c - r, c + r] for c in hoops]
    F = lambda s: _interp(floor_pts, s)
    Bz = lambda s: _interp(bar_pts, s)
    posts = spec.get("posts", [0.0, L])
    s_a, s_b = min(posts), max(posts)
    parts = [tube_mesh([p0 + t * s_a + Vector((0, 0, Bz(s_a))), p0 + t * s_b + Vector((0, 0, Bz(s_b)))], rb, 12)]
    for s in posts:
        p = p0 + t * s
        parts.append(tube_mesh([p + Vector((0, 0, F(s))), p + Vector((0, 0, Bz(s)))], rb, 12))
    for sl, sr in hoops:
        sc = (sl + sr) / 2
        r = (sr - sl) / 2
        zl, zr = F(sl), F(sr)
        apex = Bz(sc) - rb - rh
        pts = []
        for k in range(21):
            a = math.pi * k / 20
            ss = sc - r * math.cos(a)
            base = zl + (zr - zl) * (1 - math.cos(a)) / 2
            pts.append(p0 + t * ss + Vector((0, 0, base + (apex - (zl + zr) / 2) * math.sin(a))))
        parts.append(tube_mesh(pts, rh, 10))
    obj = new_obj(name, join_bms(parts), col, mat("staal_zwart", (0.03, 0.03, 0.03), 0.35, 0.8), smooth=True)
    obj["element"] = name
    return [obj]


# ---------------------------------------------------------------- stukken

def build_slab(col):
    """Stuk 1: plattegrond — betonvlak (straatvloer) en bakstenen muurkop-rand."""
    s = DATA["slab"]
    floor = new_obj("P1_beton_vloer", polygon_prism(s["inner"], 0.0, -0.30), col, mat("beton", (0.62, 0.62, 0.60)))
    rim = new_obj("P1_muurkop_rand", ring_prism(s["outer"], s["inner"], 0.0, -0.30), col, mat("baksteen_rollaag", (0.45, 0.26, 0.20)))
    for o in (floor, rim):
        o["stuk"] = "P1 plattegrond"
    return [floor, rim]


def build_east(col):
    """Stuk 2: oostzijde — ledge L7 en hoepelrail R7."""
    E = DATA["elements"]
    objs = []
    objs += build_ledge(col, "L7_ledge_oost", E["L7"])
    objs += build_hoop_rail(col, "R7_hoepelrail_oost", E["R7"])
    return objs


def _line_side(p, a, b):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def stairs_z(x, y, S=None):
    """Hoogte op de trap (traptreden); None buiten de trap."""
    S = S or DATA["elements"]["STAIRS"]
    ang = math.radians(S["nosing_angle"])
    t = (math.cos(ang), math.sin(ang))
    n = (-t[1], t[0])  # wijst ongeveer naar het noorden
    z = 0.0
    for nx, ny, nz in S["nosings"]:
        if (x - nx) * n[0] + (y - ny) * n[1] >= 0:  # noordelijk van deze neus -> minstens deze hoogte
            z = max(z, nz)
    return z


def build_stairs(col, name, S):
    ang = math.radians(S["nosing_angle"])
    t = Vector((math.cos(ang), math.sin(ang)))
    n = Vector((-t.y, t.x))
    wa, wb = Vector(S["west_line"][0]), Vector(S["west_line"][1])
    ea, eb = Vector(S["east_line"][0]), Vector(S["east_line"][1])

    def isect(p, d, a, b):
        e = b - a
        den = d.x * e.y - d.y * e.x
        u = ((a.x - p.x) * e.y - (a.y - p.y) * e.x) / den
        return p + d * u

    objs = []
    noses = sorted(S["nosings"], key=lambda q: -q[2])
    back = Vector((15.0, S["back_y"]))
    for k, (nx, ny, nz) in enumerate(noses):
        p = Vector((nx, ny))
        q = back if k == 0 else Vector((noses[k - 1][0], noses[k - 1][1]))
        # tree van deze neus tot de vorige (hogere) neus; trede k is een blok van z=0 tot nz
        w0, e0 = isect(p, t, wa, wb), isect(p, t, ea, eb)
        w1, e1 = isect(q, t, wa, wb), isect(q, t, ea, eb)
        poly = [(w0.x, w0.y), (e0.x, e0.y), (e1.x, e1.y), (w1.x, w1.y)]
        blk = new_obj(f"{name}_trede{k}", polygon_prism(poly, nz - 0.012, -0.05), col, mat("beton", (0.62, 0.62, 0.60)))
        nose = new_obj(f"{name}_neus{k}", polygon_prism([(w0.x, w0.y), (e0.x, e0.y), (e0.x + n.x * 0.04, e0.y + n.y * 0.04), (w0.x + n.x * 0.04, w0.y + n.y * 0.04)], nz, nz - 0.012), col,
                       mat("staal_zwart", (0.03, 0.03, 0.03), 0.35, 0.8))
        riser = new_obj(f"{name}_stootbord{k}", polygon_prism([(w0.x - n.x * 0.006, w0.y - n.y * 0.006), (e0.x - n.x * 0.006, e0.y - n.y * 0.006), (e0.x, e0.y), (w0.x, w0.y)], nz, nz - 0.12), col,
                        mat("staal_zwart", (0.03, 0.03, 0.03), 0.35, 0.8))
        objs += [blk, nose, riser]
    for o in objs:
        o["element"] = name
    return objs


def build_sloped_ledge(col, name, spec):
    """Ledge met schuine bovenkant (hubba): p0->p1, top-hoogtes [z0, z1], basis op z=0 (overlapt trap/bank)."""
    p0, p1 = Vector(spec["p0"]), Vector(spec["p1"])
    t = (p1 - p0).normalized(); n = Vector((-t.y, t.x))
    W = spec["width"]; r = spec.get("round_ends", 0.0); z0, z1 = spec["top"]
    L = (p1 - p0).length
    outline = []
    segs = 8
    for k in range(segs + 1):
        a = -math.pi / 2 + math.pi * k / segs
        outline.append((L - r + r * math.cos(a), (W / 2) * math.sin(a)))
    for k in range(segs + 1):
        a = math.pi / 2 + math.pi * k / segs
        outline.append((r + r * math.cos(a), (W / 2) * math.sin(a)))
    bm = bmesh.new()
    top, bot = [], []
    for s_, w_ in outline:
        p = p0 + t * s_ + n * w_
        zt = z0 + (z1 - z0) * s_ / L
        top.append(bm.verts.new((p.x, p.y, zt)))
        bot.append(bm.verts.new((p.x, p.y, -0.05)))
    m = len(outline)
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    body = new_obj(name, bm, col, mat("ledge_zijkant", (0.08, 0.08, 0.085), 0.6))
    # licht bovenvlak (iets ingesprongen)
    bm2 = bmesh.new()
    vs = []
    for s_, w_ in outline:
        sc = 0.03 / max(W / 2, 1e-6)
        p = p0 + t * (r + (s_ - r) * (1 - 0.03 / max(L / 2, 1e-6))) + n * (w_ * (1 - sc))
        zt = z0 + (z1 - z0) * s_ / L + 0.002
        vs.append(bm2.verts.new((p.x, p.y, zt)))
    bm2.faces.new(vs)
    top_o = new_obj(name + "_top", bm2, col, mat("ledge_top", (0.70, 0.70, 0.68), 0.7))
    for o in (body, top_o):
        o["element"] = name
    return [body, top_o]


def build_north_stairs(col):
    """Stuk 3a: trap (4 stootborden), hoepelrail R3 en hubba-ledge naast de trap."""
    E = DATA["elements"]
    objs = build_stairs(col, "TRAP", E["STAIRS"])
    objs += build_sloped_ledge(col, "HUBBA_trap", E["HUBBA_TRAP"])
    r3 = dict(E["R3"])
    if r3.get("zijplaat"):
        # schuine zwarte zijplaat onder de rail (bovenrand = vloerlijn van de hoepels)
        p0, p1 = Vector(r3["p0"]), Vector(r3["p1"])
        t = (p1 - p0).normalized(); n = Vector((-t.y, t.x))
        fl = sorted(r3["floor"])
        bm = bmesh.new()
        top = [bm.verts.new((*(p0 + t * s_ - n * 0.04), z)) for s_, z in fl]
        topb = [bm.verts.new((*(p0 + t * s_ + n * 0.04), z)) for s_, z in fl]
        bot = [bm.verts.new((*(p0 + t * s_ - n * 0.04), -0.02)) for s_, z in fl]
        botb = [bm.verts.new((*(p0 + t * s_ + n * 0.04), -0.02)) for s_, z in fl]
        for i in range(len(fl) - 1):
            bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
            bm.faces.new((botb[i + 1], botb[i], topb[i], topb[i + 1]))
            bm.faces.new((top[i], top[i + 1], topb[i + 1], topb[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        objs.append(new_obj("TRAP_zijplaat", bm, col, mat("staal_zwart", (0.03, 0.03, 0.03), 0.35, 0.8)))
    if r3.get("floor_from") == "STAIRS":
        p0, p1 = Vector(r3["p0"]), Vector(r3["p1"])
        L = (p1 - p0).length
        pts = []
        for i in range(0, 101):
            s_ = L * i / 100 * 1.05 - 0.05
            q = p0 + (p1 - p0).normalized() * s_
            pts.append((s_, stairs_z(q.x, q.y)))
        r3["floor"] = pts
    objs += build_hoop_rail(col, "R3_hoepelrail_trap", r3)
    return objs


def deck_z(x):
    return _interp(DATA["deck_z"]["pts"], x)


def _junction_side(name, x, y):
    """>0 = oostelijk (rechts) van de kreukellijn (lijn van voet naar top, verlengd)."""
    (bx, by), (tx, ty) = DATA["QP_NORTH"]["junctions"][name]
    return (tx - bx) * (y - by) - (ty - by) * (x - bx) < 0


def _junction_dist(name, x, y):
    (bx, by), (tx, ty) = DATA["QP_NORTH"]["junctions"][name]
    L = math.hypot(tx - bx, ty - by)
    return abs((tx - bx) * (y - by) - (ty - by) * (x - bx)) / L


def _mid_ramp(x, y):
    """Middenhelling onbegrensd lateraal doorgetrokken (voor de overgang naar de zijsecties)."""
    for sec in DATA["QP_NORTH"]["sections"]:
        if sec["name"] != "midden":
            continue
        c0x, c0y = sec["c0"]; c1x, c1y = sec["c1"]
        L = math.hypot(c1x - c0x, c1y - c0y)
        dx, dy = (c1x - c0x) / L, (c1y - c0y) / L
        u = (x - c0x) * (-dy) + (y - c0y) * dx
        if u >= 0 or u < -sec["depth"]:
            return None
        zb = deck_z(x)
        return zb + (sec["top"][0] - zb) * _interp(DATA["QP_NORTH"]["profile"], -u / sec["depth"])
    return None


def qp_z(x, y):
    z = _qp_z_raw(x, y)
    W = DATA["QP_NORTH"].get("blend", 0.0)
    if W > 0:
        for jn in DATA["QP_NORTH"]["junctions"]:
            d = _junction_dist(jn, x, y)
            if d < W:
                zm = _mid_ramp(x, y)
                if zm is not None and zm < z:
                    t = d / W
                    t = t * t * (3 - 2 * t)
                    z = zm + (z - zm) * t
    return z


def _qp_z_raw(x, y):
    Q = DATA["QP_NORTH"]
    best = None
    for sec in Q["sections"]:
        if "side" in sec:
            right = _junction_side(sec["side"][0], x, y)
            if (sec["side"][1] == "right") != right:
                continue
        c0x, c0y = sec["c0"]; c1x, c1y = sec["c1"]
        L = math.hypot(c1x - c0x, c1y - c0y)
        dx, dy = (c1x - c0x) / L, (c1y - c0y) / L
        nx, ny = -dy, dx
        a = (x - c0x) * dx + (y - c0y) * dy
        ext = sec.get("ext", 0.0)
        outside = a < -0.001 or a > L + 0.001
        if a < -0.001 - ext or a > L + 0.001 + ext:
            continue
        u = (x - c0x) * nx + (y - c0y) * ny
        if "between" in sec and u < 0:
            if not (_junction_side(sec["between"][0], x, y) and not _junction_side(sec["between"][1], x, y)):
                continue
        if outside:
            # verlengde helling naast een verhoogde sectie, afgetopt op de hoogte van de buursectie
            if u >= 0 or u < -sec["depth"]:
                continue
            zb = deck_z(x)
            top = sec["top"][0] if a < 0 else sec["top"][1]
            z = min(zb + (top - zb) * _interp(Q["profile"], -u / sec["depth"]), sec["cap"])
            best = z if best is None else max(best, z)
            continue
        zb = deck_z(x)
        top = sec["top"][0] + (sec["top"][1] - sec["top"][0]) * a / L
        h = top - zb
        if u >= 0:
            if u > sec.get("back", 99.0):
                continue
            z = top
        elif sec.get("platform_only"):
            continue
        elif u >= -sec["depth"]:
            z = zb + h * _interp(Q["profile"], -u / sec["depth"])
        else:
            continue
        best = z if best is None else max(best, z)
    return best if best is not None else deck_z(x)


def terrain_z_simple(T, x, y):
    return terrain_z(None, x, y, T)


def terrain_z(name, x, y, T=None):
    T = T or DATA["terrain"][name]
    if T["kind"] == "qp":
        return qp_z(x, y)
    if T["kind"] == "deck":
        return deck_z(x)
    if T["kind"] == "bank_y":
        f = (y - T["lower_y"]) / (T["upper_y"] - T["lower_y"])
        return deck_z(x) * min(1.0, max(0.0, f))
    FN = DATA["folds_north"]
    d1 = _side_dist(FN["lower"], x, y)    # positief = noordelijk (bergop) van de onderste vouw
    d2 = -_side_dist(FN["upper"], x, y)   # positief = zuidelijk van de bovenste vouw
    if d1 <= 0:
        return 0.0
    if d2 <= 0:
        return deck_z(x)
    return deck_z(x) * d1 / (d1 + d2)


def _side_dist(poly, x, y):
    """Afstand tot een polylijn (west->oost), positief links (noord) ervan."""
    best = None
    for (ax, ay), (bx, by) in zip(poly[:-1], poly[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
        px, py = ax + t * dx, ay + t * dy
        d = math.hypot(x - px, y - py)
        if best is None or d < best[0]:
            side = dx * (y - ay) - dy * (x - ax)
            best = (d, 1.0 if side >= 0 else -1.0)
    return best[0] * best[1]


def build_qp_heightfield(col, name):
    """Hoogteveld via constrained Delaunay (type 1 = driehoeken binnen de rand).

    Beperkingslijnen: copings, blok-eindvlakken (dubbel, 1 cm uit elkaar = verticale wand),
    blok-achterrand en de kreukellijnen (dubbel). Rijen evenwijdig aan de copings volgen het profiel;
    een grof grid vult alleen de vlakke delen.
    """
    from mathutils.geometry import delaunay_2d_cdt
    T = DATA["terrain"][name]
    poly = [Vector(p) for p in T["poly"]]
    # CCW
    area = sum(poly[i].x * poly[(i + 1) % len(poly)].y - poly[(i + 1) % len(poly)].x * poly[i].y for i in range(len(poly)))
    if area < 0:
        poly.reverse()

    def inside(p):
        c = False
        j = len(poly) - 1
        for i in range(len(poly)):
            if ((poly[i].y > p.y) != (poly[j].y > p.y)) and (p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y + 1e-12) + poly[i].x):
                c = not c
            j = i
        return c

    pts = [p.copy() for p in poly]
    face = list(range(len(poly)))
    edges = []
    cons = []  # (a, b) segmenten van beperkingslijnen, voor afstandstest

    def add_line(a, b, step=0.05):
        a, b = Vector(a), Vector(b)
        n = max(1, int((b - a).length / step))
        prev = None
        for i in range(n + 1):
            p = a + (b - a) * (i / n)
            if inside(p):
                pts.append(p)
                idx = len(pts) - 1
                if prev is not None:
                    edges.append((prev, idx))
                prev = idx
            else:
                prev = None
        cons.append((a, b))

    def near_cons(p, tol):
        for a, b in cons:
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
            if (a + ab * t - p).length < tol:
                return True
        return False

    Q = DATA["QP_NORTH"]
    secs = [s_ for s_ in Q["sections"] if not s_.get("platform_only")]
    frames = []
    for sec in secs:
        c0, c1 = Vector(sec["c0"]), Vector(sec["c1"])
        d = (c1 - c0).normalized(); nrm = Vector((-d.y, d.x)); L = (c1 - c0).length
        frames.append((sec, c0, d, nrm, L))
        ext = sec.get("ext", 0.0)
        for u in (0.0, 0.02):
            add_line(c0 + d * (-ext) + nrm * u, c0 + d * (L + ext) + nrm * u)
        if "back" in sec:
            for a in (-0.006, 0.006, L - 0.006, L + 0.006):
                add_line(c0 + d * a + nrm * 0.02, c0 + d * a + nrm * (sec["back"] + 0.4))
            for u in (sec["back"] - 0.006, sec["back"] + 0.006):
                add_line(c0 + nrm * u, c0 + d * L + nrm * u)
    for jn, ((bx, by), (tx, ty)) in Q["junctions"].items():
        B, Tp = Vector((bx, by)), Vector((tx, ty))
        dj = (Tp - B).normalized(); nj = Vector((-dj.y, dj.x))
        for off in (-0.012, 0.012):
            add_line(B - dj * 0.6 + nj * off, Tp + dj * 0.15 + nj * off, 0.04)
    rows = sorted(set([r[0] for r in Q["profile"]] + [i / 24 for i in range(25)] + [0.01, 0.02, 0.03, 0.05, 0.07, 0.09]))
    for sec, c0, d, nrm, L in frames:
        ext = sec.get("ext", 0.0)
        for f in rows:
            if f <= 0.0:
                continue
            u = -f * sec["depth"]
            k = max(2, int((L + 2 * ext) / 0.08))
            for i in range(k + 1):
                p = c0 + d * (-ext + (L + 2 * ext) * i / k) + nrm * u
                if inside(p) and not near_cons(p, 0.02):
                    pts.append(p)

    def in_ramp(p):
        for sec, c0, d, nrm, L in frames:
            ext = sec.get("ext", 0.0)
            a = (p - c0).dot(d); u = (p - c0).dot(nrm)
            if -ext - 0.1 <= a <= L + ext + 0.1 and -sec["depth"] - 0.1 <= u <= 0.1:
                return True
        return False

    xs = [p.x for p in poly]; ys = [p.y for p in poly]
    gx = min(xs) + 0.125
    while gx < max(xs):
        gy = min(ys) + 0.125
        while gy < max(ys):
            p = Vector((gx, gy))
            if inside(p) and not in_ramp(p) and not near_cons(p, 0.05):
                pts.append(p)
            gy += 0.25
        gx += 0.25
    out = delaunay_2d_cdt(pts, edges, [face], 1, 1e-5)
    verts2, faces = out[0], out[2]
    bm = bmesh.new()
    vs = [bm.verts.new((v.x, v.y, qp_z(v.x, v.y))) for v in verts2]
    for f in faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = new_obj(f"TER_{name}", bm, col, mat("beton_glad", (0.66, 0.66, 0.64)))
    obj["element"] = name
    obj["ground"] = True
    return obj


def _in_poly(p, poly):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        if ((poly[i][1] > p[1]) != (poly[j][1] > p[1])) and (p[0] < (poly[j][0] - poly[i][0]) * (p[1] - poly[i][1]) / (poly[j][1] - poly[i][1] + 1e-12) + poly[i][0]):
            c = not c
        j = i
    return c


def build_north_qp_copings(col):
    Q = DATA["QP_NORTH"]
    inner = DATA["slab"]["inner"]
    objs = []
    for sec in Q["sections"]:
        if sec.get("platform_only"):
            continue
        c0, c1 = Vector(sec["c0"]), Vector(sec["c1"])
        d = (c1 - c0).normalized(); nrm = Vector((-d.y, d.x))
        r = 0.03
        L = (c1 - c0).length
        ss = [L * i / 400 for i in range(401)]
        ins = [s_ for s_ in ss if _in_poly(c0 + d * s_ - nrm * 0.05, inner)]
        if not ins:
            continue
        c0, c1 = c0 + d * (min(ins) + 0.03), c0 + d * (max(ins) - 0.03)
        a = c0 - nrm * r; b = c1 - nrm * r
        objs.append(new_obj(f"COPING_{sec['name']}", tube_mesh([(a.x, a.y, sec["top"][0] - r), (b.x, b.y, sec["top"][1] - r)], r, 12), col,
                            mat("staal_coping", (0.25, 0.25, 0.26), 0.3, 0.9), smooth=True))
    return objs


def build_north_qp(col):
    """Stuk 4: noord-quarterpipe (drie secties + platform) en copingbuizen."""
    objs = [build_qp_heightfield(col, "NOORD_QP")]
    Q = DATA["QP_NORTH"]
    for sec in Q["sections"]:
        c0, c1 = Vector(sec["c0"]), Vector(sec["c1"])
        d = (c1 - c0).normalized(); nrm = Vector((-d.y, d.x))
        r = 0.03
        a = c0 - nrm * r; b = c1 - nrm * r
        objs.append(new_obj(f"COPING_{sec['name']}", tube_mesh([(a.x, a.y, sec["top"][0] - r), (b.x, b.y, sec["top"][1] - r)], r, 12), col,
                            mat("staal_coping", (0.25, 0.25, 0.26), 0.3, 0.9), smooth=True))
    return objs


def _sec(name):
    for sc in DATA["QP_NORTH"]["sections"]:
        if sc["name"] == name:
            return sc


def _frame(sc):
    c0 = Vector(sc["c0"]); c1 = Vector(sc["c1"])
    L = (c1 - c0).length; d = (c1 - c0) / L; n = Vector((-d.y, d.x))
    return c0, d, n, L


def region_z(T, x, y):
    kind = T["kind"]
    if kind == "qp_flat":
        return _sec(T["section"])["top"][0]
    if kind == "qp_behind":
        if not _junction_side("west", x, y):
            sc = _sec("west")
        elif _junction_side("oost", x, y):
            sc = _sec("oost")
        else:
            return _sec("achter")["top"][0] if _sec("achter") else 1.355
        c0, d, n, L = _frame(sc)
        a = (Vector((x, y)) - c0).dot(d)
        return sc["top"][0] + (sc["top"][1] - sc["top"][0]) * max(0.0, min(1.0, a / L))
    if kind == "qp_ramp":
        sc = _sec(T["section"])
        c0, d, n, L = _frame(sc)
        p = Vector((x, y))
        a = (p - c0).dot(d); u = (p - c0).dot(n)
        zb = deck_z(x)
        top = sc["top"][0] + (sc["top"][1] - sc["top"][0]) * max(0.0, min(1.0, a / L))
        f = max(0.0, min(1.0, -u / sc["depth"]))
        z = zb + (top - zb) * _interp(DATA["QP_NORTH"]["profile"], f)
        if T["section"] == "midden" and (a < 0 or a > L):
            z = min(z, sc.get("side_cap", 1.36))
        return z
    return terrain_z_simple(T, x, y)


def build_region(col, name, ramp_rows=True, skirt_to=0.0):
    """Algemene terreinregio: CDT binnen de polygoon + rijen (helling) of grid, hoogte uit region_z, randen verticaal."""
    from mathutils.geometry import delaunay_2d_cdt
    T = DATA["terrain"][name]
    poly = [Vector(p) for p in T["poly"]]
    ar = sum(poly[i].x * poly[(i + 1) % len(poly)].y - poly[(i + 1) % len(poly)].x * poly[i].y for i in range(len(poly)))
    if ar < 0:
        poly.reverse()

    def inside(p, margin=0.01):
        c = False
        j = len(poly) - 1
        for i in range(len(poly)):
            if ((poly[i].y > p.y) != (poly[j].y > p.y)) and (p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y + 1e-12) + poly[i].x):
                c = not c
            j = i
        if not c:
            return False
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
            if (a + ab * t - p).length < margin:
                return False
        return True

    pts = [p.copy() for p in poly]
    if T["kind"] == "qp_ramp":
        sc = _sec(T["section"])
        c0, d, n, L = _frame(sc)
        rows = sorted(set([r[0] for r in DATA["QP_NORTH"]["profile"]] + [i / 24 for i in range(25)] + [0.01, 0.02, 0.03, 0.05, 0.07, 0.09]))
        for f in rows:
            u = -f * sc["depth"]
            for i in range(-400, 800):
                p = c0 + d * (i * 0.08) + n * u
                if inside(p, 0.02):
                    pts.append(p)
    else:
        xs = [p.x for p in poly]; ys = [p.y for p in poly]
        gx = min(xs) + 0.1
        while gx < max(xs):
            gy = min(ys) + 0.1
            while gy < max(ys):
                p = Vector((gx, gy))
                if inside(p, 0.05):
                    pts.append(p)
                gy += 0.2
            gx += 0.2
    out = delaunay_2d_cdt(pts, [], [list(range(len(poly)))], 1, 1e-6)
    verts2, faces = out[0], out[2]
    bm = bmesh.new()
    vs = [bm.verts.new((v.x, v.y, region_z(T, v.x, v.y))) for v in verts2]
    for f in faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    # verticale randen (skirt) langs de polygoonrand
    idx = {}
    for i, v in enumerate(verts2):
        idx[(round(v.x, 5), round(v.y, 5))] = i
    ring = []
    for p in poly:
        k = (round(p.x, 5), round(p.y, 5))
        if k in idx:
            ring.append(vs[idx[k]])
    low = [bm.verts.new((v.co.x, v.co.y, skirt_to)) for v in ring]
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        if ring[i] is ring[j]:
            continue
        try:
            bm.faces.new((ring[i], low[i], low[j], ring[j]))
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = new_obj(f"TER_{name}", bm, col, mat("beton_glad", (0.66, 0.66, 0.64)))
    obj["element"] = name
    obj["ground"] = True
    return obj


def build_terrain_piece(col, name):
    """Bovenvlak (getrianguleerd) + verticale zijkanten tot z=0, z per hoekpunt uit de terreinformule."""
    T = DATA["terrain"][name]
    pts = T["poly"]
    bm = bmesh.new()
    top = [bm.verts.new((x, y, terrain_z(name, x, y))) for x, y in pts]
    face = bm.faces.new(top)
    bmesh.ops.triangulate(bm, faces=[face], quad_method="BEAUTY", ngon_method="BEAUTY")
    # zijkanten waar het bovenvlak boven de vloer ligt
    n = len(top)
    bot = [bm.verts.new((v.co.x, v.co.y, -0.02)) for v in top]
    for i in range(n):
        j = (i + 1) % n
        if top[i].co.z > 0.005 or top[j].co.z > 0.005:
            bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = new_obj(f"TER_{name}", bm, col, mat("beton_glad" if T["kind"] != "deck" else "beton", (0.66, 0.66, 0.64) if T["kind"] != "deck" else (0.62, 0.62, 0.60)))
    obj["element"] = name
    return obj


_BVH = {}


def ground_z(x, y, start=5.0):
    """Hoogste grond onder (x,y): raycast tegen alle objecten met custom prop 'ground'."""
    from mathutils.bvhtree import BVHTree
    if "tree" not in _BVH:
        verts, polys = [], []
        dg = bpy.context.evaluated_depsgraph_get()
        for o in bpy.data.objects:
            if o.type == "MESH" and o.get("ground"):
                me = o.evaluated_get(dg).to_mesh()
                off = len(verts)
                verts += [o.matrix_world @ v.co for v in me.vertices]
                polys += [[off + i for i in p.vertices] for p in me.polygons]
                o.evaluated_get(dg).to_mesh_clear()
        _BVH["tree"] = BVHTree.FromPolygons(verts, polys)
    hit = _BVH["tree"].ray_cast(Vector((x, y, start)), Vector((0, 0, -1)))
    return hit[0].z if hit[0] is not None else 0.0


def build_bank_ledge(col, name, spec):
    """Ledge die de grond volgt: bovenkant = grond + h langs de as (p0 -> p1), breedte W."""
    _BVH.clear()
    p0, p1 = Vector(spec["p0"]), Vector(spec["p1"])
    t = (p1 - p0); L = t.length; t.normalize(); n = Vector((-t.y, t.x))
    W = spec["width"]; h = spec.get("h"); steel = spec.get("steel", 0.03)
    k = max(2, int(L / 0.1))
    ss = [L * i / k for i in range(k + 1)]
    tops = []
    for s_ in ss:
        c = p0 + t * s_
        if "top_pts" in spec:
            tops.append(_interp(spec["top_pts"], s_))
        elif "top" in spec:
            tops.append(spec["top"][0] + (spec["top"][1] - spec["top"][0]) * s_ / L)
        else:
            g = max(ground_z(c.x + n.x * W / 2, c.y + n.y * W / 2), ground_z(c.x - n.x * W / 2, c.y - n.y * W / 2))
            tops.append(g + h)

    def strip(w, z_off, zb):
        bm = bmesh.new()
        L_, R_, LB, RB = [], [], [], []
        for s_, zt in zip(ss, tops):
            c = p0 + t * s_
            L_.append(bm.verts.new((*(c + n * w / 2), zt + z_off)))
            R_.append(bm.verts.new((*(c - n * w / 2), zt + z_off)))
            LB.append(bm.verts.new((*(c + n * w / 2), zb)))
            RB.append(bm.verts.new((*(c - n * w / 2), zb)))
        for i in range(k):
            bm.faces.new((L_[i], R_[i], R_[i + 1], L_[i + 1]))
            bm.faces.new((LB[i + 1], RB[i + 1], RB[i], LB[i]))
            bm.faces.new((L_[i + 1], LB[i + 1], LB[i], L_[i]))
            bm.faces.new((R_[i], RB[i], RB[i + 1], R_[i + 1]))
        bm.faces.new((L_[0], LB[0], RB[0], R_[0]))
        bm.faces.new((R_[-1], RB[-1], LB[-1], L_[-1]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm

    body = new_obj(name + "_kern", strip(W, -0.005, -0.05), col, mat("ledge_zijkant", (0.08, 0.08, 0.085), 0.6))
    top = new_obj(name + "_top", strip(W - 2 * steel, 0.0, None or 0.0) if False else strip(W - 2 * steel, 0.0, 0.0), col, mat("ledge_top", (0.70, 0.70, 0.68), 0.7))
    # top-strip: alleen het bovenvlak is zichtbaar; zijkanten zitten in de kern
    for o in (body, top):
        o["element"] = name
    return [body, top]


def build_north_bank(col):
    """Stuk 3b: noordbank + noorddek + oostbank, hoepelrails id6/id7, bank-ledges L3 en L4."""
    objs = [build_terrain_piece(col, k) for k in ("NOORD_BANK", "NOORD_DEK", "OOST_BANK")]
    for k in ("QP_HELLING_WEST", "QP_HELLING_MIDDEN", "QP_HELLING_OOST", "QP_BLOK", "QP_PLATEAU"):
        if k in DATA["terrain"]:
            objs.append(build_region(col, k))
    for o in objs:
        o["ground"] = True
    for o in bpy.data.objects:
        if o.name.startswith(("P1_beton_vloer", "TRAP_trede")):
            o["ground"] = True
    _BVH.clear()
    E = DATA["elements"]
    for key, nm in (("R6", "R6_hoepelrail_bank_west"), ("R5", "R5_hoepelrail_bank_oost")):
        spec = dict(E[key])
        p0, p1 = Vector(spec["p0"]), Vector(spec["p1"])
        L = (p1 - p0).length; tt = (p1 - p0).normalized()
        spec["floor"] = [(s_, ground_z(*(p0 + tt * s_))) for s_ in [L * i / 60 - 0.1 for i in range(64)]]
        objs += build_hoop_rail(col, nm, spec)
    objs += build_bank_ledge(col, "L3_bankledge", E["L3"])
    objs += build_bank_ledge(col, "L4_bankledge_oost", E["L4"])
    return objs


def build_funbox(col):
    """Stuk 5 (deel 1): funbox-terrein (Laplace-raster, dekken 0,34 / 0,57) + hubba-box."""
    import numpy as np
    from mathutils.geometry import delaunay_2d_cdt
    Fb = DATA["FUNBOX"]
    R = np.load(os.path.join(ROOT, Fb["raster"])); Z = R["z"]; x0, y1, res = [float(v) for v in R["meta"]]

    def zr(x, y):
        fx = (x - x0) / res - 0.5; fy = (y1 - y) / res - 0.5
        i, j = int(math.floor(fy)), int(math.floor(fx)); ty, tx = fy - i, fx - j
        i = max(0, min(Z.shape[0] - 2, i)); j = max(0, min(Z.shape[1] - 2, j))
        return float((Z[i, j] * (1 - tx) + Z[i, j + 1] * tx) * (1 - ty) + (Z[i + 1, j] * (1 - tx) + Z[i + 1, j + 1] * tx) * ty)

    poly = [Vector(p) for p in Fb["region"]]
    pts = [p.copy() for p in poly]
    edges = []
    for key in ("deck_west", "deck_east"):
        dp = [Vector(p) for p in Fb[key]]
        base = len(pts); pts += dp
        edges += [(base + i, base + (i + 1) % len(dp)) for i in range(len(dp))]
    xs = [p.x for p in poly]; ys = [p.y for p in poly]
    gx = min(xs)
    while gx < max(xs):
        gy = min(ys)
        while gy < max(ys):
            pts.append(Vector((gx, gy))); gy += 0.2
        gx += 0.2
    out = delaunay_2d_cdt(pts, edges, [list(range(len(poly)))], 1, 1e-5)
    bm = bmesh.new()
    vs = [bm.verts.new((v.x, v.y, zr(v.x, v.y))) for v in out[0]]
    for f in out[2]:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ter = new_obj("TER_FUNBOX", bm, col, mat("beton_glad", (0.66, 0.66, 0.64)))
    ter["ground"] = True
    objs = [ter]
    hb = DATA["elements"].get("HUBBA_BOX")
    if hb:
        objs += build_ledge(col, "HUBBA_BOX_funbox", hb)
    return objs


PIECES = {
    "P1": ("P1_plattegrond", build_slab),
    "P2": ("P2_oost_L7_R7", build_east),
    "P3a": ("P3a_trap_R3_hubba", build_north_stairs),
    "P3b": ("P3b_noordbank", build_north_bank),
    "P4": ("P4_noord_qp", lambda col: build_north_qp_copings(col)),
    "P5": ("P5_funbox", build_funbox),
}


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    wanted = argv or list(PIECES)
    C.reset_scene()
    root = C.get_collection("Museumplein_skatepark")
    for key in wanted:
        cname, fn = PIECES[key]
        col = C.get_collection(cname, root)
        objs = fn(col)
        print(f"[build] {key}: {len(objs)} objecten")
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    print("[build] opgeslagen:", OUT_BLEND)


if __name__ == "__main__":
    main()
