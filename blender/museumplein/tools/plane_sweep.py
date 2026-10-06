"""Hoogtekaart via plane-sweep stereo: drone-plattegrond (met schuinstand) + gekalibreerde foto's.

Voor elke kandidaat-hoogte z wordt elke foto naar het plattegrondraster geprojecteerd alsof het
oppervlak op hoogte z ligt; de z met de hoogste lokale NCC (op high-pass beelden) wint.
Output: refs/height_sweep.npz (z, score, raster-meta) + renders/measure/height_sweep.png
"""
import json, math, os, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heights import load_cam

LEAN = np.array([0.07, 0.25])
RES = 0.05
X0, X1, Y0, Y1 = -20.0, 23.0, -22.0, 25.0
WIN = int(sys.argv[1]) if len(sys.argv) > 1 else 11
ZS = np.arange(-0.8, 3.21, 0.02)

meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
nx, ny = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
xs = X0 + (np.arange(nx) + 0.5) * RES
ys = Y1 - (np.arange(ny) + 0.5) * RES
GX, GY = np.meshgrid(xs, ys)


def hp(gray, sigma=4.0):
    g = gray.astype(np.float32)
    return g - cv2.GaussianBlur(g, (0, 0), sigma)


# drone-plattegrond op het sweep-raster (pixel = positie in de plattegrond)
mpx = (GX - meta["x0"]) / meta["mpp"]
mpy = (meta["y1"] - GY) / meta["mpp"]
plan = cv2.remap(cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY).astype(np.float32), mpx.astype(np.float32), mpy.astype(np.float32), cv2.INTER_AREA)
plan_hp = hp(plan, 3.0)


def box(a):
    return cv2.boxFilter(a, -1, (WIN, WIN), normalize=True, borderType=cv2.BORDER_REFLECT)


def ncc(a, b, valid):
    ma, mb = box(a), box(b)
    va = box(a * a) - ma * ma
    vb = box(b * b) - mb * mb
    cab = box(a * b) - ma * mb
    s = cab / np.sqrt(np.maximum(va * vb, 1e-6))
    s[~valid] = -1
    return s, va


photos = []
for name in ["photo04", "photo05"]:
    cam = load_cam(os.path.join(REFS, f"cam_{name}.json"))
    img = cv2.imread(os.path.join(REFS, f"{name}.jpg"))
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    photos.append((name, cam, g))

best_z = np.zeros((ny, nx), np.float32)
best_s = np.full((ny, nx), -2.0, np.float32)
second = np.full((ny, nx), -2.0, np.float32)
per_photo = {n: (np.zeros((ny, nx), np.float32), np.full((ny, nx), -2.0, np.float32)) for n, _, _ in photos}
plan_tex = None
for zi, z in enumerate(ZS):
    total = np.zeros((ny, nx), np.float32); cnt = np.zeros((ny, nx), np.float32)
    # wereldpunt dat in de plattegrond op (GX,GY) verschijnt als het op hoogte z ligt
    WX = GX - LEAN[0] * z
    WY = GY - LEAN[1] * z
    for name, cam, g in photos:
        P = np.stack([WX.ravel(), WY.ravel(), np.full(WX.size, z)], 1) - cam["C"]
        Pc = P @ cam["R"].T
        u = (cam["f"] * Pc[:, 0] / Pc[:, 2] + cam["cx"]).reshape(ny, nx).astype(np.float32)
        v = (cam["f"] * Pc[:, 1] / Pc[:, 2] + cam["cy"]).reshape(ny, nx).astype(np.float32)
        valid = (Pc[:, 2].reshape(ny, nx) > 0) & (u > 2) & (u < g.shape[1] - 3) & (v > 2) & (v < g.shape[0] - 3)
        warped = cv2.remap(g, u, v, cv2.INTER_LINEAR)
        s, va = ncc(plan_hp, hp(warped, 3.0), valid)
        bz, bs = per_photo[name]
        m = s > bs
        bz[m] = z; bs[m] = s[m]
        total += np.where(valid, s, 0); cnt += valid
    score = np.where(cnt > 0, total / np.maximum(cnt, 1), -1)
    m = score > best_s
    second = np.where(m, best_s, np.maximum(second, score))
    best_z[m] = z; best_s[m] = score[m]
    if zi % 40 == 0:
        print(f"z={z:.2f} klaar", flush=True)

_, vplan = ncc(plan_hp, plan_hp, np.ones_like(plan_hp, bool))
np.savez_compressed(os.path.join(REFS, "height_sweep.npz"), z=best_z, score=best_s, second=second, tex=vplan,
                    z04=per_photo["photo04"][0], s04=per_photo["photo04"][1], z05=per_photo["photo05"][0], s05=per_photo["photo05"][1],
                    meta=np.array([X0, X1, Y0, Y1, RES]))
vis = np.clip((best_z + 0.5) / 3.5, 0, 1)
col = cv2.applyColorMap((vis * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
col[best_s < 0.35] = (col[best_s < 0.35] * 0.3).astype(np.uint8)
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "height_sweep.png"), col)
print("klaar; mediaan score", float(np.median(best_s)))
