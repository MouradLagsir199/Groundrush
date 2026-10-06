"""Robuust gladstrijken van een gesloten contour: periodieke spline met iteratieve uitschieter-weging."""
import numpy as np
from scipy.interpolate import splprep, splev


def robust_closed_spline(P, smooth_cm=1.5, thr_cm=5.0, iters=6, n_out=1600):
    P = np.asarray(P, float)
    keep = np.concatenate([[True], np.linalg.norm(np.diff(P, axis=0), axis=1) > 1e-3])
    P = P[keep]
    if np.linalg.norm(P[0] - P[-1]) < 1e-3:
        P = P[:-1]
    w = np.ones(len(P))
    for it in range(iters):
        sel = w > 0
        Q = P[sel]
        tck, u = splprep([Q[:, 0], Q[:, 1]], s=len(Q) * (smooth_cm / 100) ** 2, per=True, quiet=2)
        uu = np.linspace(0, 1, 6000, endpoint=False)
        S = np.stack(splev(uu, tck), 1)
        # residu van ALLE punten tot de spline
        from scipy.spatial import cKDTree
        d, _ = cKDTree(S).query(P)
        new_w = (d < thr_cm / 100).astype(float)
        # bescherm tegen te veel verwijderen
        if new_w.mean() < 0.7:
            break
        if np.array_equal(new_w, w):
            break
        w = new_w
    uu = np.linspace(0, 1, n_out, endpoint=False)
    S = np.stack(splev(uu, tck), 1)
    return S, w, d


def rdp_closed(P, eps):
    def rdp(pts):
        if len(pts) < 3:
            return pts
        a, b = pts[0], pts[-1]
        ab = b - a
        L = np.hypot(*ab)
        dd = np.abs(ab[0] * (pts[:, 1] - a[1]) - ab[1] * (pts[:, 0] - a[0])) / L if L > 0 else np.hypot(*(pts - a).T)
        i = int(np.argmax(dd))
        if dd[i] > eps:
            return np.vstack([rdp(pts[:i + 1])[:-1], rdp(pts[i:])])
        return np.vstack([a, b])
    k = len(P) // 2
    A = rdp(P[:k + 1])
    B = rdp(np.vstack([P[k:], P[:1]]))
    return np.vstack([A[:-1], B[:-1]])
