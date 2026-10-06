"""Randen preciseren langs normaalprofielen en robuust lijnen fitten."""
import json, os
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png")).astype(np.float32)
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]
B, G, R = rect[:, :, 0], rect[:, :, 1], rect[:, :, 2]
CH = {
    "red": cv2.GaussianBlur(R - (G + B) / 2, (0, 0), 1.5),     # baksteen hoog, beton laag
    "lum": cv2.GaussianBlur((R + G + B) / 3, (0, 0), 1.5),
}

def sample(ch, x, y):
    px = np.float32((np.asarray(x) - X0) / mpp).ravel(); py = np.float32((Y1 - np.asarray(y)) / mpp).ravel()
    n = len(px); w = 4096; pad = (-n) % w
    px = np.concatenate([px, np.zeros(pad, np.float32)]).reshape(-1, w)
    py = np.concatenate([py, np.zeros(pad, np.float32)]).reshape(-1, w)
    return cv2.remap(CH[ch], px, py, cv2.INTER_LINEAR).ravel()[:n]

def profile_edges(a, b, ch="red", sign=+1, search=1.0, step=0.25, ds=0.01):
    """Langs segment a->b; normaal = links van de richting. Zoek max gradiënt (sign) binnen ±search."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a; L = np.linalg.norm(d); t = d / L; n = np.array([-t[1], t[0]])
    out = []
    for s in np.arange(step, L - step + 1e-9, step):
        p = a + t * s
        offs = np.arange(-search, search + 1e-9, ds)
        xy = p[None, :] + offs[:, None] * n[None, :]
        val = sample(ch, xy[:, 0], xy[:, 1])
        g = np.gradient(val) * sign
        i = int(np.argmax(g))
        if g[i] > 2.0:
            out.append((p + offs[i] * n).tolist() + [float(g[i])])
    return np.array(out)

def fit_line(pts, thr=0.05, iters=2000, seed=0):
    rng = np.random.default_rng(seed)
    P = pts[:, :2]; best = None
    for _ in range(iters):
        i, j = rng.choice(len(P), 2, replace=False)
        d = P[j] - P[i]; n = np.array([-d[1], d[0]]); nn = np.linalg.norm(n)
        if nn < 1e-6: continue
        n /= nn; r = np.abs((P - P[i]) @ n)
        inl = r < thr
        if best is None or inl.sum() > best.sum(): best = inl
    Q = P[best]; c = Q.mean(0); u, s, vt = np.linalg.svd(Q - c)
    dirv = vt[0]; n = np.array([-dirv[1], dirv[0]])
    res = (Q - c) @ n
    return c, dirv, best, float(np.sqrt(np.mean(res ** 2)))

def intersect(c1, d1, c2, d2):
    A = np.array([d1, -d2]).T
    t = np.linalg.solve(A, c2 - c1)
    return c1 + t[0] * d1
