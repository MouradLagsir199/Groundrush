"""Terreinvoetafdrukken (2D) voor bank/dek, geknipt op de binnenrand van het betonvlak.

Schrijft park.json["terrain"]: {naam: {"poly": [[x,y]...], "kind": "bank"|"deck", params}}
Hoogtes rekent build.py uit (zelfde formules), zodat 2D en 3D gescheiden blijven.
"""
import json
import numpy as np
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union

park = json.load(open('data/park.json'))
inner = Polygon(park['slab']['inner']).buffer(0)
FN = park['folds_north']
lower = [tuple(p) for p in FN['lower']]
upper = [tuple(p) for p in FN['upper']]
F = FN
X0 = lower[0][0]

def line_y_poly(poly, x):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    return float(np.interp(x, xs, ys))
S = park['elements']['STAIRS']
wa, wb = np.array(S['west_line'][0]), np.array(S['west_line'][1])
# halfvlak west van de trap-westlijn
d = (wb - wa) / np.linalg.norm(wb - wa)
far = 40
west_of_stairs = Polygon([tuple(wa - d * far), tuple(wb + d * far), tuple(wb + d * far + np.array([-far, 0])), tuple(wa - d * far + np.array([-far, 0]))]).buffer(0)
bank = Polygon(lower + upper[::-1]).buffer(0).intersection(inner).intersection(west_of_stairs)

# zuidgrens van het dek
ang = np.radians(S['nosing_angle']); tn = np.array([np.cos(ang), np.sin(ang)])
top = max(S['nosings'], key=lambda q: q[2])
nose_pt = np.array(top[:2])
def nose_y(x): return nose_pt[1] + (x - nose_pt[0]) * tn[1] / tn[0]
ea, eb = np.array(S['east_line'][0]), np.array(S['east_line'][1])
def line_x_at_y(a, b, y): return a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
xw = line_x_at_y(wa, wb, nose_y(12.6)); xe = line_x_at_y(ea, eb, nose_y(15.6))
EB = park['elements'].get('EAST_BANK', {"lower_y": 9.30, "upper_y": 11.70, "x0": 15.95})
south = [p for p in upper if p[0] < xw] + [(xw, line_y_poly(upper, xw))]
south += [(xw, nose_y(xw)), (xe, nose_y(xe)), (EB['x0'], EB['upper_y']), (30.0, EB['upper_y'])]
deck = Polygon(south + [(30.0, 40.0), (X0, 40.0)]).buffer(0).intersection(inner).difference(bank)
east_bank = box(EB['x0'], EB['lower_y'], 30.0, EB['upper_y']).intersection(inner)

def dens(poly, ds=0.2):
    if poly.geom_type == 'MultiPolygon':
        poly = max(poly.geoms, key=lambda g: g.area)
    ring = LineString(list(poly.exterior.coords))
    n = max(4, int(ring.length / ds))
    pts = [ring.interpolate(i / n, normalized=True) for i in range(n)]
    # hoekpunten behouden
    corners = list(poly.exterior.coords)[:-1]
    allp = sorted([(ring.project(p.__class__(c) if False else type(pts[0])(c)), c) for c in corners] + [(ring.project(p), (p.x, p.y)) for p in pts])
    out = []
    for _, c in allp:
        if not out or np.hypot(c[0] - out[-1][0], c[1] - out[-1][1]) > 0.02:
            out.append((round(c[0], 3), round(c[1], 3)))
    return out

# noord-QP: regio's (helling west/midden/oost, blokplateau, achterplateau), gescheiden door de kreukellijnen
QN = park['QP_NORTH']
SEC = {sc['name']: sc for sc in QN['sections']}
def frame(sc):
    c0, c1 = np.array(sc['c0']), np.array(sc['c1'])
    L = np.linalg.norm(c1 - c0); dd = (c1 - c0) / L; nn = np.array([-dd[1], dd[0]])
    return c0, dd, nn, L
def band(sc, a0, a1, u0, u1):
    c0, dd, nn, L = frame(sc)
    return Polygon([tuple(c0 + dd * a0 + nn * u0), tuple(c0 + dd * a1 + nn * u0), tuple(c0 + dd * a1 + nn * u1), tuple(c0 + dd * a0 + nn * u1)])
def halfplane(name, right):
    (bx, by), (tx, ty) = QN['junctions'][name]
    B = np.array([bx, by]); T = np.array([tx, ty]); dj = (T - B) / np.linalg.norm(T - B); nj = np.array([dj[1], -dj[0]])  # rechts
    far = 60
    side = nj if right else -nj
    return Polygon([tuple(B - dj * far), tuple(B + dj * far), tuple(B + dj * far + side * far), tuple(B - dj * far + side * far)])
W, M, E = SEC['west'], SEC['midden'], SEC['oost']
_, _, _, Lm = frame(M)
w_ramp = band(W, -40, frame(W)[3] + 5, -W['depth'], 0).intersection(halfplane('west', False)).intersection(inner)
m_ramp = band(M, -5, Lm + 5, -M['depth'], 0).intersection(halfplane('west', True)).intersection(halfplane('oost', False)).intersection(inner)
e_ramp = band(E, -5, frame(E)[3] + 40, -E['depth'], 0).intersection(halfplane('oost', True)).intersection(inner)
m_plat = band(M, 0, Lm, 0, M['back']).intersection(inner)
behind = unary_union([band(W, -40, frame(W)[3] + 5, 0, 12).intersection(halfplane('west', False)),
                      band(M, -5, Lm + 5, 0, 12).intersection(halfplane('west', True)).intersection(halfplane('oost', False)),
                      band(E, -5, frame(E)[3] + 40, 0, 12).intersection(halfplane('oost', True))]).intersection(inner).difference(m_plat)
qp = unary_union([w_ramp, m_ramp, e_ramp, m_plat, behind]).buffer(0)
deck = deck.difference(qp.buffer(0.001)).buffer(0)
qp_regions = {"QP_HELLING_WEST": ("qp_ramp", "west", w_ramp), "QP_HELLING_MIDDEN": ("qp_ramp", "midden", m_ramp),
              "QP_HELLING_OOST": ("qp_ramp", "oost", e_ramp), "QP_BLOK": ("qp_flat", "midden", m_plat), "QP_PLATEAU": ("qp_behind", None, behind)}

park['terrain'] = {
    "NOORD_BANK": {"kind": "bank", "poly": dens(bank), "fit": F},
    "NOORD_DEK": {"kind": "deck", "poly": dens(deck)},
    "OOST_BANK": {"kind": "bank_y", "poly": dens(east_bank), "lower_y": EB['lower_y'], "upper_y": EB['upper_y']},
}
for nm, (kind, sec, geom) in qp_regions.items():
    if geom.is_empty:
        continue
    park['terrain'][nm] = {"kind": kind, "section": sec, "poly": dens(geom, 0.1)}
park['elements']['EAST_BANK'] = EB
json.dump(park, open('data/park.json', 'w'), indent=1)
for k, v in park['terrain'].items():
    print(k, "punten", len(v['poly']), "opp", round(Polygon(v['poly']).area, 2))
