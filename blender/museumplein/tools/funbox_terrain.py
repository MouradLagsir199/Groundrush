"""Funbox-terrein: Laplace-hoogteveld met vaste dekken en z=0 aan de buitenrand (ware coördinaten)."""
import json
import cv2
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve
from shapely.geometry import Polygon, box
from shapely.affinity import translate

LEAN = np.array([0.07, 0.25])
park = json.load(open('data/park.json'))
seg = json.load(open('refs/funbox_seg.json'))
F = park.setdefault('FUNBOX', {})
DECK_W, DECK_E = F.get('deck_w', 0.34), F.get('deck_e', 0.57)
X_CLIP_W = F.get('x_clip_w', -4.75)
decks = sorted(seg['deck'], key=lambda d: np.mean([p[0] for p in d['pts']]))
west_app = Polygon(decks[0]['pts']).buffer(0)
east_app = Polygon(decks[1]['pts']).buffer(0)
west = translate(west_app, -LEAN[0] * DECK_W, -LEAN[1] * DECK_W).simplify(0.03)
east = translate(east_app, -LEAN[0] * DECK_E, -LEAN[1] * DECK_E).minimum_rotated_rectangle
# vlakke dektoppen volgens stereo (plateaus) samenvoegen met de donkere kleurvlakken
from shapely.geometry import MultiPoint
from shapely.ops import unary_union
_d = np.load('refs/height_pp.npz'); _z = _d['z']; _s = _d['score']; _sec = _d['second']; _sx0, _sx1, _sy0, _sy1, _R = _d['meta']
_conf = (_s > 0.4) & (_s - _sec > 0.03)
def plateau(lo, hi, xmin, xmax):
    m = (_conf & (_z > lo) & (_z < hi)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    polys = []
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] * _R * _R < 1.5: continue
        ys, xs = np.where(lab == i); X = _sx0 + xs * _R; Y = _sy1 - ys * _R
        if X.mean() < xmin or X.mean() > xmax: continue
        polys.append(MultiPoint(list(zip(X, Y))).convex_hull)
    return unary_union(polys)
if 'deck_offsets' in F:
    west = Polygon(F['deck_west']); east = Polygon(F['deck_east'])
elif F.get('use_stereo_plateau', True):
    west = unary_union([west, plateau(DECK_W - 0.035, DECK_W + 0.045, -3.5, 2.6)]).convex_hull
    east = unary_union([east, plateau(DECK_E - 0.05, DECK_E + 0.06, 3.2, 8.2)]).convex_hull
region_app = Polygon(seg['bank_plus_deck'][0]['pts']).buffer(0)
inner = Polygon(park['slab']['inner']).buffer(0)
clip = box(X_CLIP_W, -2.2, 10.5, F.get('y_clip_n', 7.6))
region = region_app.buffer(0.02).intersection(clip).intersection(inner)
west = west.intersection(clip)

RES = 0.05
x0, y0, x1, y1 = -7.0, -2.2, 10.5, 9.0
nx, ny = int((x1 - x0) / RES), int((y1 - y0) / RES)
def rasterize(poly):
    m = np.zeros((ny, nx), np.uint8)
    geoms = getattr(poly, 'geoms', [poly])
    for g in geoms:
        if g.is_empty or g.geom_type != 'Polygon': continue
        pts = np.array(g.exterior.coords)
        px = ((pts[:, 0] - x0) / RES).astype(np.int32); py = ((y1 - pts[:, 1]) / RES).astype(np.int32)
        cv2.fillPoly(m, [np.stack([px, py], 1)], 1)
    return m > 0
R = rasterize(region); W = rasterize(west); E = rasterize(east)
fixed = ~R | W | E
val = np.zeros((ny, nx)); val[W] = DECK_W; val[E] = DECK_E
idx = -np.ones((ny, nx), np.int64); free = ~fixed
idx[free] = np.arange(free.sum())
A = lil_matrix((free.sum(), free.sum())); b = np.zeros(free.sum())
ys, xs = np.where(free)
for k, (i, j) in enumerate(zip(ys, xs)):
    A[k, k] = 4
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ii, jj = i + di, j + dj
        if ii < 0 or jj < 0 or ii >= ny or jj >= nx:
            b[k] += 0; continue
        if free[ii, jj]: A[k, idx[ii, jj]] = -1
        else: b[k] += val[ii, jj]
z = val.copy(); z[free] = spsolve(csr_matrix(A), b)
z[~R] = 0.0
np.savez_compressed('data/funbox_z.npz', z=z.astype(np.float32), meta=np.array([x0, y1, RES]))
def coords(p):
    if p.geom_type == 'MultiPolygon': p = max(p.geoms, key=lambda g: g.area)
    return [[round(x, 3), round(y, 3)] for x, y in list(p.exterior.coords)[:-1]]
F.update({"deck_w": DECK_W, "deck_e": DECK_E, "x_clip_w": X_CLIP_W, "region": coords(region), "deck_west": coords(west.intersection(region)), "deck_east": coords(east.intersection(region)),
          "raster": "data/funbox_z.npz", "bron": "drone-kleursegmentatie (dek/bank/vloer), dekhoogtes stereo foto04+05 v4, Laplace voor banks"})
json.dump(park, open('data/park.json', 'w'), indent=1)
print("regio m2", round(region.area, 1), "dek W", round(west.area, 2), "dek O", round(east.area, 2))
vis = cv2.applyColorMap((np.clip(z / 0.8, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
vis[~R] = (vis[~R] * 0.3).astype(np.uint8)
cv2.imwrite('renders/measure/funbox_laplace.png', vis)
