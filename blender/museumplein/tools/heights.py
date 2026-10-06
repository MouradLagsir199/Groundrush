"""Hoogte meten met een gekalibreerde camera: voor elke pixel de hoogte h waarbij de kijkstraal
boven de plattegrond-polylijn ligt."""
import json, math, sys
import numpy as np
import cv2

def load_cam(path, size=(2000, 1334)):
    c = json.load(open(path))
    R, _ = cv2.Rodrigues(np.array(c["rvec"]))
    return {"R": R, "C": np.array(c["cam_pos"]), "f": c["f"], "cx": c.get("cx", size[0] / 2), "cy": c.get("cy", size[1] / 2)}

def ray(cam, u, v):
    d_cam = np.array([(u - cam["cx"]) / cam["f"], (v - cam["cy"]) / cam["f"], 1.0])
    d = cam["R"].T @ d_cam
    return cam["C"], d / np.linalg.norm(d)

def dist_to_poly(p, poly):
    best = 1e9
    for a, b in zip(poly[:-1], poly[1:]):
        a, b = np.asarray(a), np.asarray(b); ab = b - a
        t = np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-12), 0, 1)
        best = min(best, np.linalg.norm(p - (a + t * ab)))
    return best

def height_on_poly(cam, u, v, poly, hmin=-1.5, hmax=4.0):
    C, d = ray(cam, u, v)
    hs = np.linspace(hmin, hmax, 1101)
    best = (1e9, None, None)
    for h in hs:
        t = (h - C[2]) / d[2]
        p = C[:2] + t * d[:2]
        e = dist_to_poly(p, poly)
        if e < best[0]: best = (e, h, p)
    return best  # (afstand m, hoogte, xy)

def height_at_xy(cam, u, v, xy):
    """Hoogte op verticale lijn door xy die het dichtst bij de kijkstraal komt."""
    C, d = ray(cam, u, v)
    # minimaliseer horizontale afstand: t zodat C+t d boven xy
    dh = d[:2]; t = np.dot(np.asarray(xy) - C[:2], dh) / np.dot(dh, dh)
    p = C + t * d
    return p[2], float(np.linalg.norm(p[:2] - np.asarray(xy)))


LEAN = (0.07, 0.25)  # schuinstand drone-plattegrond: top van object op hoogte h staat s*h verschoven


def height_on_poly_lean(cam, u, v, poly, hmin=-1.0, hmax=4.0, lean=LEAN):
    """Als height_on_poly, maar de plattegrond-polylijn (uit de drone) schuift mee met s*h."""
    C, d = ray(cam, u, v)
    best = (1e9, None, None)
    P = np.asarray(poly, float)
    for h in np.linspace(hmin, hmax, 1001):
        t = (h - C[2]) / d[2]
        p = C[:2] + t * d[:2]
        e = dist_to_poly(p + np.array(lean) * h, P)
        if e < best[0]:
            best = (e, h, p)
    return best
