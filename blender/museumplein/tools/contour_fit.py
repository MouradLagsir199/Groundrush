"""Gesloten contour = rechte zijden + afrondingen; fit op beeldgradiënten (actieve contour)."""
import json, sys
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from edgefit import sample


def line_from(c, ang):
    return np.array(c, float), np.array([np.cos(ang), np.sin(ang)])


def build_outline(lines, radii, ds=0.05):
    """lines: lijst (punt, richting) in volgorde rond (tegen de klok in of met de klok mee).
    radii: afrondingsstraal per hoek i (tussen lijn i en lijn i+1). Geeft polyline (gesloten)."""
    n = len(lines)
    corners = []
    for i in range(n):
        (c1, d1), (c2, d2) = lines[i], lines[(i + 1) % n]
        A = np.array([d1, -d2]).T
        t = np.linalg.solve(A, c2 - c1)
        P = c1 + t[0] * d1
        r = radii[i]
        # hoek tussen richtingen
        cosang = np.clip(np.dot(-d1, d2), -1, 1)
        theta = np.arccos(cosang)  # binnenhoek
        tl = r / np.tan(theta / 2) if r > 0 else 0.0
        T1 = P - d1 * tl; T2 = P + d2 * tl
        # middelpunt
        bis = (-d1 + d2); bis /= np.linalg.norm(bis)
        cdist = r / np.sin(theta / 2) if r > 0 else 0.0
        M = P + bis * cdist
        corners.append((T1, T2, M, r, P))
    pts = []
    for i in range(n):
        T1, T2, M, r, P = corners[i]
        # boog van T1 naar T2 rond M
        if r > 1e-6:
            a1 = np.arctan2(*(T1 - M)[::-1]); a2 = np.arctan2(*(T2 - M)[::-1])
            da = (a2 - a1 + np.pi) % (2 * np.pi) - np.pi
            k = max(2, int(abs(da) * r / ds))
            for a in np.linspace(a1, a1 + da, k):
                pts.append(M + r * np.array([np.cos(a), np.sin(a)]))
        else:
            pts.append(P)
        # recht stuk naar volgende hoek
        T1n = corners[(i + 1) % n][0]
        L = np.linalg.norm(T1n - T2)
        k = max(2, int(L / ds))
        for s in np.linspace(0, 1, k)[1:-1]:
            pts.append(T2 + (T1n - T2) * s)
    return np.array(pts), corners


def normals(pts):
    t = np.roll(pts, -1, 0) - np.roll(pts, 1, 0)
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    return np.stack([-t[:, 1], t[:, 0]], 1)


def edge_offsets(pts, ch, sign, search=0.35, ds=0.01, outward=+1):
    nrm = normals(pts) * outward
    offs = np.arange(-search, search + 1e-9, ds)
    xy = pts[:, None, :] + offs[None, :, None] * nrm[:, None, :]
    val = sample(ch, xy[..., 0].ravel(), xy[..., 1].ravel()).reshape(len(pts), -1)
    g = np.gradient(val, axis=1) * sign
    i = np.argmax(g, axis=1)
    strength = g[np.arange(len(pts)), i]
    return offs[i], strength
