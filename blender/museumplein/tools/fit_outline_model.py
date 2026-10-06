"""Fit lijnen+bogen-model aan de gladde buitencontour."""
import json, sys
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contour_fit import build_outline

sm = np.load("refs/slab_outline_raw.npy")
# zijden met de klok mee: (naam, punt, hoek)
init = [
    ("W", (-6.0, 6.5), np.radians(50.7)),
    ("N", (14.0, 22.4), np.radians(-16.4)),
    ("E", (18.6, -2.9), np.radians(-100.0)),
    ("S", (-0.5, -19.75), np.radians(161.7)),
    ("Wb", (-19.6, -7.0), np.radians(75.0)),
]
r0 = [0.8, 1.0, 7.5, 6.0, 1.5]  # hoeken: W-N, N-E, E-S, S-Wb, Wb-W

def unpack(p):
    lines = []
    for i in range(5):
        cx, cy, a = p[3 * i: 3 * i + 3]
        lines.append((np.array([cx, cy]), np.array([np.cos(a), np.sin(a)])))
    radii = np.abs(p[15:20])
    return lines, radii

p0 = []
for _, c, a in init: p0 += [c[0], c[1], a]
p0 += r0
tree_pts = sm

def resid(p):
    lines, radii = unpack(p)
    try:
        poly, _ = build_outline(lines, radii, ds=0.05)
    except Exception:
        return np.full(len(sm), 10.0)
    t = cKDTree(poly)
    d, _ = t.query(sm)
    seg = np.linalg.norm(np.diff(np.vstack([poly, poly[:1]]), axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    ss = np.linspace(0, cum[-1], 600, endpoint=False)
    P2 = np.vstack([poly, poly[:1]])
    rs = np.stack([np.interp(ss, cum, P2[:, 0]), np.interp(ss, cum, P2[:, 1])], 1)
    d2, _ = cKDTree(sm).query(rs)
    return np.concatenate([d, d2])

# punt langs de lijn is vrij (degeneratie) -> vaste projectie: houd alleen loodrechte offset vrij door kleine regularisatie
sol = least_squares(resid, p0, loss="soft_l1", f_scale=0.05, max_nfev=4000)
lines, radii = unpack(sol.x)
poly, corners = build_outline(lines, radii, ds=0.02)
d, _ = cKDTree(poly).query(sm)
print("afstand contourpunten -> model: mediaan %.1f cm, p90 %.1f cm, max %.1f cm" % (np.median(d) * 100, np.percentile(d, 90) * 100, d.max() * 100))
names = ["W-N", "N-E", "E-S", "S-Wb", "Wb-W"]
for n, (T1, T2, M, r, P) in zip(names, corners):
    print(f"hoek {n:5s} straal {r:.2f} m  snijpunt {P.round(2)}")
for (nm, _, _), (c, dvec) in zip(init, lines):
    print(f"zijde {nm:2s} richting {np.degrees(np.arctan2(dvec[1], dvec[0])):.2f} gr")
area = 0.5 * abs(np.sum(poly[:, 0] * np.roll(poly[:, 1], -1) - np.roll(poly[:, 0], -1) * poly[:, 1]))
print("oppervlak model m2", round(area, 1))
json.dump({"lines": [[c.tolist(), dvec.tolist()] for c, dvec in lines], "radii": radii.tolist(), "names": [i[0] for i in init]},
          open("refs/outline_model.json", "w"), indent=1)
np.save("refs/outline_model_poly.npy", poly)
# afwijkingsprofiel per gebied
cen = sm.mean(0); ang = (np.degrees(np.arctan2(sm[:, 1] - cen[1], sm[:, 0] - cen[0])) + 360) % 360
for a0 in range(0, 360, 30):
    sel = (ang >= a0) & (ang < a0 + 30)
    print(f"  sector {a0:3d}: mediaan {np.median(d[sel])*100:.1f} cm  max {d[sel].max()*100:.1f} cm")
