"""Lokale rimpels in de binnenrand (bij ledges/borden) vervangen door een rechte brug tussen in- en uitgang van een kader."""
import json, sys
import numpy as np
sys.path.insert(0, 'tools')
from robust_outline import rdp_closed
park = json.load(open('data/park.json'))
def dens(P, ds=0.05):
    seg = np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
    ss = np.arange(0, cum[-1], ds); P2 = np.vstack([P, P[:1]])
    return np.stack([np.interp(ss, cum, P2[:, 0]), np.interp(ss, cum, P2[:, 1])], 1)
def bridge(P, box):
    x0, y0, x1, y1 = box
    m = (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > y0) & (P[:, 1] < y1)
    if not m.any(): return P, 0
    st = np.where(m & ~np.roll(m, 1))[0]
    if len(st) != 1: return P, -len(st)
    s = st[0]; P = np.roll(P, -s, 0); m = np.roll(m, -s)
    e = np.where(~m)[0][0]
    a, b = P[-1], P[e]
    k = e
    P[:e] = a + (b - a) * (np.arange(1, e + 1)[:, None] / (e + 1))
    return P, e
key = sys.argv[1]
boxes = json.loads(sys.argv[2])
P = dens(np.array(park['slab'][key]))
for bx in boxes:
    P, n = bridge(P, bx); print(key, bx, "punten vervangen:", n)
park['slab'][key] = rdp_closed(P, 0.006).round(3).tolist()
json.dump(park, open('data/park.json', 'w'), indent=1)
