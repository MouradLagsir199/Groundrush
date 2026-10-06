"""Python-kopie van de QP-hoogtefunctie uit build.py (voor analyse buiten Blender)."""
import json
import numpy as np

park = json.load(open('data/park.json'))
Q = park['QP_NORTH']
prof = np.array(Q['profile'])
dk = np.array(park['deck_z']['pts'])


def P(t):
    return np.interp(t, prof[:, 0], prof[:, 1])


def deck(x):
    return np.interp(x, dk[:, 0], dk[:, 1])


def sec_z(s, x, y, use_ext=True):
    c0 = np.array(s['c0']); c1 = np.array(s['c1']); L = np.linalg.norm(c1 - c0); d = (c1 - c0) / L; n = np.array([-d[1], d[0]])
    a = (x - c0[0]) * d[0] + (y - c0[1]) * d[1]
    u = (x - c0[0]) * n[0] + (y - c0[1]) * n[1]
    ext = s.get('ext', 0.0) if use_ext else 0.0
    zb = deck(x)
    if a < -ext or a > L + ext:
        return None
    outside = a < 0 or a > L
    if outside:
        if u >= 0 or u < -s['depth']:
            return None
        top = s['top'][0] if a < 0 else s['top'][1]
        dist = -a if a < 0 else a - L
        z = zb + (top - zb) * P(-u / s['depth'])
        z = min(z, s['cap']) - s.get('ext_slope', 0.0) * dist
        return z
    if u >= 0:
        if u > s.get('back', 99):
            return None
        return s['top'][0] + (s['top'][1] - s['top'][0]) * a / L
    if s.get('platform_only'):
        return None
    if u < -s['depth']:
        return None
    top = s['top'][0] + (s['top'][1] - s['top'][0]) * a / L
    return zb + (top - zb) * P(-u / s['depth'])


def qp_z(x, y):
    best = None
    for s in Q['sections']:
        z = sec_z(s, x, y)
        if z is not None:
            best = z if best is None else max(best, z)
    return best if best is not None else deck(x)
