"""Plane-sweep stereo tussen foto 04 en foto 05 (zelfde moment, zelfde licht).

Per rastercel (x,y) en kandidaat-hoogte z: beide foto's samplen op (x,y,z), NCC over een venster.
Kostvolume wordt ruimtelijk gemiddeld (cost aggregation); argmax per cel.
Output: refs/height_pp.npz + renders/measure/height_pp.png
"""
import json, os, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heights import load_cam

RES = float(sys.argv[1]) if len(sys.argv) > 1 else 0.06
WIN = int(sys.argv[2]) if len(sys.argv) > 2 else 9
AGG = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
X0, X1, Y0, Y1 = [float(v) for v in (sys.argv[4:8] if len(sys.argv) > 7 else (-20, 23, -22, 25))]
ZS = np.arange(-0.3, 1.2, 0.01)
nx, ny = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
xs = X0 + (np.arange(nx) + 0.5) * RES
ys = Y1 - (np.arange(ny) + 0.5) * RES
GX, GY = np.meshgrid(xs, ys)

cams, imgs = [], []
for name in ["photo04", "photo05"]:
    cams.append(load_cam(os.path.join(REFS, f"cam_{name}.json")))
    g = cv2.cvtColor(cv2.imread(os.path.join(REFS, f"{name}.jpg")), cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = g - cv2.GaussianBlur(g, (0, 0), 6.0)
    imgs.append(g)


def proj(cam, z):
    P = np.stack([GX.ravel(), GY.ravel(), np.full(GX.size, z)], 1) - cam["C"]
    Pc = P @ cam["R"].T
    u = (cam["f"] * Pc[:, 0] / Pc[:, 2] + cam["cx"]).reshape(ny, nx).astype(np.float32)
    v = (cam["f"] * Pc[:, 1] / Pc[:, 2] + cam["cy"]).reshape(ny, nx).astype(np.float32)
    return u, v


def box(a, w):
    return cv2.boxFilter(a, -1, (w, w), normalize=True, borderType=cv2.BORDER_REFLECT)


vol = np.zeros((len(ZS), ny, nx), np.float32)
valid_all = np.zeros((ny, nx), bool)
for i, z in enumerate(ZS):
    W = []
    ok = np.ones((ny, nx), bool)
    for cam, g in zip(cams, imgs):
        u, v = proj(cam, z)
        ok &= (u > 3) & (u < g.shape[1] - 4) & (v > 3) & (v < g.shape[0] - 4)
        W.append(cv2.remap(g, u, v, cv2.INTER_LINEAR))
    a, b = W
    ma, mb = box(a, WIN), box(b, WIN)
    va = box(a * a, WIN) - ma * ma
    vb = box(b * b, WIN) - mb * mb
    s = (box(a * b, WIN) - ma * mb) / np.sqrt(np.maximum(va * vb, 1e-3))
    s[~ok] = -1
    if AGG > 0:
        s = cv2.GaussianBlur(s, (0, 0), AGG)
    vol[i] = s
    valid_all |= ok
iz = np.argmax(vol, axis=0)
best = np.take_along_axis(vol, iz[None], 0)[0]
# sub-sample verfijning (parabool)
izc = np.clip(iz, 1, len(ZS) - 2)
s0 = np.take_along_axis(vol, (izc - 1)[None], 0)[0]
s1 = np.take_along_axis(vol, izc[None], 0)[0]
s2 = np.take_along_axis(vol, (izc + 1)[None], 0)[0]
den = s0 - 2 * s1 + s2
off = np.where(np.abs(den) > 1e-6, 0.5 * (s0 - s2) / den, 0)
zbest = ZS[izc] + np.clip(off, -0.5, 0.5) * (ZS[1] - ZS[0])
# uniciteit: beste vs beste buiten ±0.15 m
mask = np.abs(ZS[:, None, None] - zbest[None]) > 0.15
second = np.max(np.where(mask, vol, -2), axis=0)
np.savez_compressed(os.path.join(REFS, "height_pp.npz"), z=zbest.astype(np.float32), score=best, second=second,
                    meta=np.array([X0, X1, Y0, Y1, RES]))
conf = (best > 0.5) & (best - second > 0.05)
vis = np.clip((zbest + 0.5) / 3.5, 0, 1)
col = cv2.applyColorMap((vis * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
col[~conf] = (col[~conf] * 0.25).astype(np.uint8)
col[~valid_all] = 0
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "height_pp.png"), cv2.resize(col, None, fx=max(1, int(0.06 / RES * 1.5)), fy=max(1, int(0.06 / RES * 1.5)), interpolation=cv2.INTER_NEAREST))
print("betrouwbaar:", round(conf.sum() / valid_all.sum() * 100, 1), "%")
