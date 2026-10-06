"""Optimaliseert de dekranden (zij-offsets van twee rechthoeken) tegen stereohoogtes met Laplace-banks."""
import json, itertools
import cv2
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import splu
from shapely.geometry import Polygon, Point, box
from shapely.affinity import translate

LEAN = np.array([0.07, 0.25])
park = json.load(open('data/park.json')); seg = json.load(open('refs/funbox_seg.json'))
F = park['FUNBOX']; DW, DE = F['deck_w'], F['deck_e']
decks = sorted(seg['deck'], key=lambda d: np.mean([p[0] for p in d['pts']]))
wpoly = translate(Polygon(decks[0]['pts']).buffer(0), -LEAN[0] * DW, -LEAN[1] * DW).intersection(box(-3.6, -5, 10, 10))
epoly = translate(Polygon(decks[1]['pts']).buffer(0), -LEAN[0] * DE, -LEAN[1] * DE)
def rect_params(p):
    r = np.array(p.minimum_rotated_rectangle.exterior.coords)[:4]
    c = r.mean(0); e1 = r[1] - r[0]; e2 = r[2] - r[1]
    if np.linalg.norm(e1) < np.linalg.norm(e2): e1, e2 = e2, e1
    u = e1 / np.linalg.norm(e1); v = np.array([-u[1], u[0]])
    return c, u, v, np.linalg.norm(e1) / 2, np.linalg.norm(e2) / 2
RW, RE = rect_params(wpoly), rect_params(epoly)
def rect(params, off):  # off = (+u, -u, +v, -v) uitbreidingen
    c, u, v, a, b = params
    a1, a0, b1, b0 = a + off[0], a + off[1], b + off[2], b + off[3]
    pts = [c + u * a1 + v * b1, c - u * a0 + v * b1, c - u * a0 - v * b0, c + u * a1 - v * b0]
    return Polygon(pts)
region = Polygon(F['region']).buffer(0)
RES = 0.1
x0, y0, x1, y1 = -7.0, -2.2, 10.5, 9.0
nx, ny = int((x1 - x0) / RES), int((y1 - y0) / RES)
XX, YY = np.meshgrid(x0 + (np.arange(nx) + 0.5) * RES, y1 - (np.arange(ny) + 0.5) * RES)
def raster(poly):
    m = np.zeros((ny, nx), np.uint8)
    for g in getattr(poly, 'geoms', [poly]):
        if g.is_empty: continue
        pts = np.array(g.exterior.coords)
        cv2.fillPoly(m, [np.stack([((pts[:, 0] - x0) / RES), ((y1 - pts[:, 1]) / RES)], 1).astype(np.int32)], 1)
    return m > 0
REG = raster(region)
d = np.load('refs/height_pp.npz'); zs = d['z']; s = d['score']; sec = d['second']; sx0, sx1, sy0, sy1, R = d['meta']
conf = (s > 0.45) & (s - sec > 0.04)
excl = Polygon([(1.3, 1.8), (3.4, 1.8), (3.4, 4.5), (1.3, 4.5)])
def near_line(p, a, b, w):
    a = np.array(a); b = np.array(b); p = np.array(p); t = np.clip(np.dot(p - a, b - a) / np.dot(b - a, b - a), 0, 1); return np.linalg.norm(a + t * (b - a) - p) < w
lines = [((5.26, 1.66), (7.22, 5.82)), ((-4.76, 2.2), (-1.94, 5.64)), ((-0.48, 3.3), (0.1, 4.62))]
obs = []
for x in np.arange(-5, 10, 0.2):
    for y in np.arange(-2, 8.5, 0.2):
        if not region.contains(Point(x, y)) or excl.contains(Point(x, y)) or any(near_line((x, y), a, b, 0.45) for a, b in lines): continue
        ix = int((x - sx0) / R); iy = int((sy1 - y) / R)
        zz = zs[iy - 1:iy + 2, ix - 1:ix + 2]; cc = conf[iy - 1:iy + 2, ix - 1:ix + 2]
        if cc.sum() < 6: continue
        obs.append((int((y1 - y) / RES), int((x - x0) / RES), float(np.median(zz[cc]))))
obs = np.array(obs)
def solve(wd, ed):
    W = raster(wd); E = raster(ed)
    fixed = ~REG | W | E
    val = np.zeros((ny, nx)); val[W] = DW; val[E] = DE
    free = ~fixed; idx = -np.ones((ny, nx), np.int64); idx[free] = np.arange(free.sum())
    n = free.sum(); A = lil_matrix((n, n)); b = np.zeros(n)
    ys, xs = np.where(free)
    for k, (i, j) in enumerate(zip(ys, xs)):
        A[k, k] = 4
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ii, jj = i + di, j + dj
            if ii < 0 or jj < 0 or ii >= ny or jj >= nx: continue
            if free[ii, jj]: A[k, idx[ii, jj]] = -1
            else: b[k] += val[ii, jj]
    z = val.copy(); z[free] = splu(csr_matrix(A).tocsc()).solve(b); z[~REG] = 0
    return z
def cost(z):
    e = z[obs[:, 0].astype(int), obs[:, 1].astype(int)] - obs[:, 2]
    return float(np.mean(np.minimum(np.abs(e), 0.2)))  # robuust
offW = [0.0, 0.0, 0.0, 0.0]; offE = [0.0, 0.0, 0.0, 0.0]
best = cost(solve(rect(RW, offW), rect(RE, offE))); print("start", round(best, 4))
steps = [0.3, 0.15, 0.08]
for st in steps:
    improved = True
    while improved:
        improved = False
        for which in ("W", "E"):
            for k in range(4):
                for dv in (st, -st):
                    oW, oE = list(offW), list(offE)
                    (oW if which == "W" else oE)[k] += dv
                    c = cost(solve(rect(RW, oW), rect(RE, oE)))
                    if c < best - 1e-4:
                        best, offW, offE, improved = c, oW, oE, True
                        print(f"  stap {st}: {which}{k} {dv:+.2f} -> {best:.4f}  offW {np.round(offW,2)} offE {np.round(offE,2)}")
wd, ed = rect(RW, offW), rect(RE, offE)
z = solve(wd, ed); e = z[obs[:, 0].astype(int), obs[:, 1].astype(int)] - obs[:, 2]
print("eind: mediaan |fout| %.3f  p80 %.3f  bias %.3f" % (np.median(np.abs(e)), np.percentile(np.abs(e), 80), np.median(e)))
F['deck_west'] = [[round(x, 3), round(y, 3)] for x, y in list(wd.exterior.coords)[:-1]]
F['deck_east'] = [[round(x, 3), round(y, 3)] for x, y in list(ed.exterior.coords)[:-1]]
F['deck_offsets'] = {"W": offW, "E": offE}
json.dump(park, open('data/park.json', 'w'), indent=1)
