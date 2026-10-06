"""Legt de randen van een camera-render over de originele foto.

Gebruik: python cam_overlay.py <foto> <tag> [x0 y0 x1 y1 uitsnede]
"""
import os, sys
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def label_edges(rgba):
    a = rgba[:, :, 3] > 127
    q = (rgba[:, :, :3].astype(np.int32) // 24)
    key = np.where(a, q[:, :, 0] * 4096 + q[:, :, 1] * 64 + q[:, :, 2] + 1, 0)
    e = np.zeros(a.shape, bool)
    e[:-1, :] |= key[:-1, :] != key[1:, :]
    e[:, :-1] |= key[:, :-1] != key[:, 1:]
    return e, a


def overlay(photo, tag, crop=None, out_w=1600):
    img = cv2.imread(os.path.join(ROOT, "refs", f"{photo}.jpg"))
    rgba = cv2.imread(os.path.join(ROOT, "renders", "check", f"cam_{photo}_{tag}.png"), cv2.IMREAD_UNCHANGED)
    e, a = label_edges(rgba)
    vis = img.copy()
    if os.environ.get("TINT"):
        tint = vis.copy()
        tint[a] = (0.65 * vis[a] + 0.35 * rgba[a][:, :3]).astype(np.uint8)
        vis = tint
    vis[e] = (0, 255, 255)
    if crop:
        x0, y0, x1, y1 = crop
        vis = vis[y0:y1, x0:x1]
        raw = img[y0:y1, x0:x1]
    else:
        raw = img
    if os.environ.get("SIDE"):
        vis = np.vstack([raw, vis])
    s = out_w / vis.shape[1]
    vis = cv2.resize(vis, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    cv2.imwrite(os.path.join(ROOT, "renders", "check", f"camov_{photo}_{tag}.jpg"), vis)


if __name__ == "__main__":
    photo, tag = sys.argv[1], sys.argv[2]
    crop = tuple(map(int, sys.argv[3:7])) if len(sys.argv) >= 7 else None
    overlay(photo, tag, crop)
