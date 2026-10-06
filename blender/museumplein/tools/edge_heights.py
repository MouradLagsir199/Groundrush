"""Hoogteprofiel z(s) langs een plattegrond-polylijn via randen in de gekalibreerde foto's.

Voor elk punt van de polylijn (zoals gezien door de drone, dus met schuinstand) en elke kandidaat-z
wordt het wereldpunt geprojecteerd in foto 04/05; score = beeldgradiënt loodrecht op de
geprojecteerde lijn. Dynamisch programmeren geeft een glad profiel z(s).
"""
import json, os, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heights import load_cam

LEAN = np.array([0.07, 0.25])
PHOTOS = {}


def _load():
    if PHOTOS:
        return
    for name in ["photo04", "photo05"]:
        cam = load_cam(os.path.join(REFS, f"cam_{name}.json"))
        g = cv2.cvtColor(cv2.imread(os.path.join(REFS, f"{name}.jpg")), cv2.COLOR_BGR2GRAY).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 1.2)
        gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
        PHOTOS[name] = (cam, gx, gy, g.shape)


def dens(P, ds=0.05):
    P = np.asarray(P, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    ss = np.arange(0, cum[-1] + 1e-9, ds)
    return np.stack([np.interp(ss, cum, P[:, 0]), np.interp(ss, cum, P[:, 1])], 1), ss


def project(cam, X):
    Pc = (X - cam["C"]) @ cam["R"].T
    u = cam["f"] * Pc[:, 0] / Pc[:, 2] + cam["cx"]
    v = cam["f"] * Pc[:, 1] / Pc[:, 2] + cam["cy"]
    return u, v, Pc[:, 2]


def score_volume(Pd, zs, photos=("photo04", "photo05"), lean=True):
    _load()
    n, K = len(Pd), len(zs)
    S = np.zeros((n, K), np.float32)
    C = np.zeros((n, K), np.float32)
    t = np.gradient(Pd, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-12
    for name in photos:
        cam, gx, gy, (H, W) = PHOTOS[name]
        for k, z in enumerate(zs):
            off = LEAN * z if lean else np.zeros(2)
            X = np.c_[Pd - off, np.full(n, z)]
            u, v, d = project(cam, X)
            X2 = np.c_[Pd - off + t * 0.05, np.full(n, z)]
            u2, v2, _ = project(cam, X2)
            tu, tv = u2 - u, v2 - v
            tn = np.hypot(tu, tv) + 1e-9
            nu, nv = -tv / tn, tu / tn
            ok = (d > 0) & (u > 2) & (u < W - 3) & (v > 2) & (v < H - 3)
            gxs = cv2.remap(gx, u.astype(np.float32).reshape(1, -1), v.astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR).ravel()
            gys = cv2.remap(gy, u.astype(np.float32).reshape(1, -1), v.astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR).ravel()
            s = np.abs(gxs * nu + gys * nv)
            S[:, k] += np.where(ok, s, 0)
            C[:, k] += ok
    return np.where(C > 0, S / np.maximum(C, 1), 0)


def dp_profile(S, zs, lam=40.0, max_step=0.08):
    """Maximaliseer som(score) - lam*|dz|; dz per punt begrensd."""
    n, K = S.shape
    dz = np.abs(zs[:, None] - zs[None, :])
    trans = -lam * dz
    trans[dz > max_step] = -1e9
    acc = S[0].copy()
    back = np.zeros((n, K), np.int32)
    for i in range(1, n):
        cand = acc[None, :] + trans  # [k_new, k_old]
        back[i] = np.argmax(cand, axis=1)
        acc = cand[np.arange(K), back[i]] + S[i]
    k = int(np.argmax(acc))
    path = np.zeros(n, np.int32)
    for i in range(n - 1, -1, -1):
        path[i] = k
        k = back[i, k]
    return zs[path], S[np.arange(n), path]


def profile(P, zmin=-0.6, zmax=3.0, dzs=0.01, lam=40.0, max_step=0.06, photos=("photo04", "photo05"), lean=True, ds=0.05):
    Pd, ss = dens(P, ds)
    zs = np.arange(zmin, zmax + 1e-9, dzs)
    S = score_volume(Pd, zs, photos, lean)
    z, sc = dp_profile(S, zs, lam, max_step)
    return Pd, ss, z, sc, S, zs


if __name__ == "__main__":
    P = json.loads(sys.argv[1])
    Pd, ss, z, sc, S, zs = profile(P)
    for i in range(0, len(ss), max(1, len(ss) // 12)):
        print(f"s={ss[i]:.2f} xy=({Pd[i,0]:.2f},{Pd[i,1]:.2f}) z={z[i]:.2f} score={sc[i]:.1f}")
