"""Vergelijkt een bovenaanzicht-render met de drone-plattegrond.

- overlay: renders/check/overlay_<tag>.jpg (render-randen in kleur over de foto)
- metriek: voor elke randpixel van de render (per materiaalkleur-regio) de afstand tot de
  sterkste beeldrand langs de normaal (±search). Rapporteert mediaan/p80/p95 in cm.
Gebruik: python check_top.py <tag> [search_m] [kanaal: lum|red|grad]
"""
import json
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
OUT = os.path.join(ROOT, "renders", "check")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp = meta["mpp"]


def boundaries(rgba):
    """Randpixels tussen verschillende render-kleuren (incl. transparant)."""
    a = rgba[:, :, 3] > 127
    key = (rgba[:, :, 0].astype(np.int32) // 8) * 1024 + (rgba[:, :, 1].astype(np.int32) // 8) * 32 + rgba[:, :, 2] // 8
    key = np.where(a, key + 1, 0)
    edge = np.zeros(a.shape, bool)
    edge[:-1, :] |= key[:-1, :] != key[1:, :]
    edge[:, :-1] |= key[:, :-1] != key[:, 1:]
    return edge, key


def edge_metric(rgba, search=0.25, chan="grad"):
    edge, key = boundaries(rgba)
    g = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    if chan == "red":
        f = rect.astype(np.float32)
        g = cv2.GaussianBlur(f[:, :, 2] - (f[:, :, 0] + f[:, :, 1]) / 2, (0, 0), 1.2)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.hypot(gx, gy)
    # normaal van de render-rand uit de gladgestreken render-sleutel
    kf = cv2.GaussianBlur((key > 0).astype(np.float32) + (key % 997).astype(np.float32) / 997.0, (0, 0), 2.0)
    nx = cv2.Sobel(kf, cv2.CV_32F, 1, 0, ksize=3)
    ny = cv2.Sobel(kf, cv2.CV_32F, 0, 1, ksize=3)
    ys, xs = np.where(edge)
    sel = np.arange(len(xs))[:: max(1, len(xs) // 6000)]
    ys, xs = ys[sel], xs[sel]
    nn = np.hypot(nx[ys, xs], ny[ys, xs]) + 1e-9
    ux, uy = nx[ys, xs] / nn, ny[ys, xs] / nn
    steps = np.arange(-search, search + 1e-9, mpp / 2) / mpp
    px = xs[:, None] + ux[:, None] * steps[None, :]
    py = ys[:, None] + uy[:, None] * steps[None, :]
    vals = cv2.remap(mag, px.astype(np.float32), py.astype(np.float32), cv2.INTER_LINEAR)
    i = np.argmax(vals, axis=1)
    off = steps[i] * mpp
    strong = vals[np.arange(len(i)), i] > np.percentile(mag, 75)
    return np.abs(off[strong]), xs[strong], ys[strong], off[strong]


def overlay(rgba, tag, scale=0.5):
    edge, _ = boundaries(rgba)
    vis = rect.copy()
    fill = rgba[:, :, 3] > 127
    tint = vis.copy()
    tint[fill] = (0.6 * vis[fill] + 0.4 * rgba[fill][:, [2, 1, 0]]).astype(np.uint8)
    vis = tint
    e = cv2.dilate(edge.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    vis[e] = (0, 255, 255)
    cv2.imwrite(os.path.join(OUT, f"overlay_{tag}.jpg"), cv2.resize(vis, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA))
    return vis


if __name__ == "__main__":
    tag = sys.argv[1]
    search = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    chan = sys.argv[3] if len(sys.argv) > 3 else "grad"
    rgba = cv2.imread(os.path.join(OUT, f"top_{tag}.png"), cv2.IMREAD_UNCHANGED)
    rgba = rgba[:, :, [2, 1, 0, 3]]
    if rgba.shape[:2] != rect.shape[:2]:
        rgba = cv2.resize(rgba, (rect.shape[1], rect.shape[0]), interpolation=cv2.INTER_NEAREST)
    d, xs, ys, off = edge_metric(rgba, search, chan)
    overlay(rgba, tag)
    print(f"[{tag}] randpunten {len(d)}  afwijking: mediaan {np.median(d)*100:.1f} cm | p80 {np.percentile(d,80)*100:.1f} cm | p95 {np.percentile(d,95)*100:.1f} cm")
    json.dump({"median_cm": float(np.median(d) * 100), "p80_cm": float(np.percentile(d, 80) * 100), "p95_cm": float(np.percentile(d, 95) * 100), "n": int(len(d))},
              open(os.path.join(OUT, f"metric_{tag}.json"), "w"))
