"""Ingezoomde overlay-uitsneden: render-randen (geel) over de drone-plattegrond, met metergrid."""
import json, os, sys
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
OUT = os.path.join(ROOT, "renders", "check")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]


def labels_of(rgba, min_frac=0.0005):
    a = rgba[:, :, 3] > 127
    q = (rgba[:, :, :3] // 24).reshape(-1, 3)
    cols, inv, cnt = np.unique(q[a.ravel()], axis=0, return_inverse=True, return_counts=True)
    pal = cols[cnt > min_frac * a.sum()].astype(np.float32)
    d = np.linalg.norm(q[:, None, :].astype(np.float32) - pal[None, :, :], axis=2)
    lab = np.argmin(d, axis=1).reshape(a.shape) + 1
    lab[~a] = 0
    return lab


def edges_of(rgba):
    lab = labels_of(rgba)
    lab = cv2.medianBlur(lab.astype(np.uint8), 3)
    e = np.zeros(lab.shape, bool)
    e[:-1, :] |= lab[:-1, :] != lab[1:, :]
    e[:, :-1] |= lab[:, :-1] != lab[:, 1:]
    return e


def crops(tag, centers, w=6.0, px=700, cols=4):
    rgba = cv2.imread(os.path.join(OUT, f"top_{tag}.png"), cv2.IMREAD_UNCHANGED)
    e = edges_of(rgba[:, :, [2, 1, 0, 3]])
    tiles = []
    for name, cx, cy in centers:
        x0p = int((cx - w / 2 - X0) / mpp); y0p = int((Y1 - (cy + w / 2)) / mpp); n = int(w / mpp)
        c = rect[y0p:y0p + n, x0p:x0p + n].copy()
        ec = e[y0p:y0p + n, x0p:x0p + n]
        c = cv2.resize(c, (px, px), interpolation=cv2.INTER_CUBIC)
        ec = cv2.resize(ec.astype(np.uint8), (px, px), interpolation=cv2.INTER_NEAREST) > 0
        c[ec] = (0, 255, 255)
        s = px / w
        for g in np.arange(np.ceil(cx - w / 2), cx + w / 2, 1.0):
            u = int((g - (cx - w / 2)) * s); cv2.line(c, (u, 0), (u, px), (255, 160, 0), 1)
        for g in np.arange(np.ceil(cy - w / 2), cy + w / 2, 1.0):
            v = int(((cy + w / 2) - g) * s); cv2.line(c, (0, v), (px, v), (255, 160, 0), 1)
        cv2.putText(c, f"{name} ({cx},{cy}) 1m-grid", (6, px - 8), 0, 0.55, (0, 0, 255), 2)
        tiles.append(c)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    sheet = np.vstack(rows)
    cv2.imwrite(os.path.join(OUT, f"crops_{tag}.jpg"), cv2.resize(sheet, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA))


if __name__ == "__main__":
    tag = sys.argv[1]
    centers = json.loads(sys.argv[2])
    w = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
    crops(tag, centers, w)
