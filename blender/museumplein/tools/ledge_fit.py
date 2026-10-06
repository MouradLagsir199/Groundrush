"""Meet de bovenkant van een ledge (lichte bovenvlak met donkere stalen rand) in de drone-plattegrond.

Neemt een georiënteerd venster rond (cx,cy,hoek,lengte); dwars- en langsprofielen van de helderheid
geven de randen van het lichte bovenvlak en van de donkere rand.
Gebruik: python ledge_fit.py cx cy hoek_graden lengte [breedte_venster]
"""
import json, os, sys
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]
L = cv2.GaussianBlur(cv2.cvtColor(rect, cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32), (0, 0), 1.0)


def window(cx, cy, ang, length, width, ds=0.01):
    a = np.radians(ang)
    t = np.array([np.cos(a), np.sin(a)]); n = np.array([-t[1], t[0]])
    ss = np.arange(-length / 2, length / 2 + 1e-9, ds)
    rr = np.arange(-width / 2, width / 2 + 1e-9, ds)
    S, Rr = np.meshgrid(ss, rr)  # rijen = dwars, kolommen = langs
    X = cx + S * t[0] + Rr * n[0]
    Y = cy + S * t[1] + Rr * n[1]
    px = ((X - X0) / mpp).astype(np.float32); py = ((Y1 - Y) / mpp).astype(np.float32)
    return cv2.remap(L, px, py, cv2.INTER_LINEAR), ss, rr, t, n


def edges_1d(prof, coords, thr_frac=0.5):
    """Plateau (licht bovenvlak): grootste aaneengesloten stuk boven drempel tussen min en max."""
    p = np.convolve(prof, np.ones(5) / 5, "same")
    lo, hi = np.percentile(p, 10), np.percentile(p, 95)
    thr = lo + thr_frac * (hi - lo)
    above = p > thr
    best, cur, start = (0, 0, 0), 0, 0
    for i, a in enumerate(above):
        if a:
            if cur == 0: start = i
            cur += 1
            if cur > best[0]: best = (cur, start, i)
        else:
            cur = 0
    _, i0, i1 = best
    # subpixel: interpoleer drempelovergang
    def cross(i, j):
        if p[j] == p[i]: return coords[i]
        f = (thr - p[i]) / (p[j] - p[i]); return coords[i] + f * (coords[j] - coords[i])
    e0 = cross(max(i0 - 1, 0), i0); e1 = cross(i1, min(i1 + 1, len(p) - 1))
    return e0, e1, thr


def fit(cx, cy, ang, length, width=1.2):
    W, ss, rr, t, n = window(cx, cy, ang, length + 0.8, width)
    # dwars: mediaan over het middelste 60% van de lengte
    mid = (np.abs(ss) < length * 0.3)
    cross_prof = np.median(W[:, mid], axis=1)
    r0, r1, thr = edges_1d(cross_prof, rr)
    rows = (rr > r0 + 0.04) & (rr < r1 - 0.04)
    long_prof = np.median(W[rows, :], axis=0)
    s0, s1, _ = edges_1d(long_prof, ss)
    c = np.array([cx, cy]) + t * (s0 + s1) / 2 + n * (r0 + r1) / 2
    return {"center": c.round(3).tolist(), "angle": ang, "top_len": round(s1 - s0, 3), "top_wid": round(r1 - r0, 3),
            "s": [round(s0, 3), round(s1, 3)], "r": [round(r0, 3), round(r1, 3)],
            "cross_profile": [[round(float(a), 2), round(float(b), 1)] for a, b in zip(rr[::4], cross_prof[::4])]}


if __name__ == "__main__":
    a = list(map(float, sys.argv[1:]))
    res = fit(*a)
    print(json.dumps({k: v for k, v in res.items() if k != "cross_profile"}))
    print("dwarsprofiel:", " ".join(f"{r:+.2f}:{v:.0f}" for r, v in res["cross_profile"]))
