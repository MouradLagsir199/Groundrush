"""Rechte muurdelen (west, oost) exact op de gefitte lijnen leggen; buitenrand parallel op mediaan bandbreedte."""
import json, sys
import numpy as np
sys.path.insert(0, 'tools')
from robust_outline import rdp_closed

park = json.load(open('data/park.json'))
R = json.load(open('refs/edge_inner_lines.json'))
area = lambda P: 0.5 * abs(np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]))


def dens(P, ds=0.05):
    seg = np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
    ss = np.arange(0, cum[-1], ds); P2 = np.vstack([P, P[:1]])
    return np.stack([np.interp(ss, cum, P2[:, 0]), np.interp(ss, cum, P2[:, 1])], 1)


I = dens(np.array(park['slab']['inner'])); O = dens(np.array(park['slab']['outer']))
for k, out_sign, s_range in [("west", -1, (-15.0, 13.4)), ("oost", +1, (-13.5, 19.5))]:
    c = np.array(R[k]['c']); d = np.array(R[k]['d']); n = np.array([-d[1], d[0]])
    if np.sign(n[0]) != out_sign: n = -n
    # binnen: punten binnen 0.30 m van de lijn en binnen bereik -> op de lijn
    s = (I - c) @ d; o = (I - c) @ n
    m = (np.abs(o) < 0.30) & (s > s_range[0]) & (s < s_range[1])
    I[m] = c + np.outer(s[m], d)
    # buiten: bandbreedte = mediaan van de offset van buitenpunten in dit bereik
    so = (O - c) @ d; oo = (O - c) @ n
    mo = (oo > 0.2) & (oo < 1.5) & (so > s_range[0] + 1) & (so < s_range[1] - 1)
    w = np.median(oo[mo])
    dev = np.abs(oo[mo] - w)
    mo2 = mo.copy(); mo2[mo] = dev < 0.25   # alleen de rechte, niet de uitsprongen (ledges/trappen)
    O[mo2] = c + np.outer(so[mo2], d) + w * n
    print(f"{k}: binnenpunten gelijnd {m.sum()}, bandbreedte {w:.2f} m, buitenpunten gelijnd {mo2.sum()} (uitsprongen behouden {(mo & ~mo2).sum()})")
park['slab']['inner'] = rdp_closed(I, 0.006).round(3).tolist()
park['slab']['outer'] = rdp_closed(O, 0.006).round(3).tolist()
print("binnen opp", round(area(np.array(park['slab']['inner'])), 1), " buiten opp", round(area(np.array(park['slab']['outer'])), 1))
json.dump(park, open('data/park.json', 'w'), indent=1)
