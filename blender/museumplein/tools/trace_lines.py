"""Geordende polylijnen (langste pad door skelet) per lijn-ID + omtrek van het betonvlak."""
import json, os
import cv2
import numpy as np
from skimage.morphology import skeletonize
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]
dark = cv2.imread(os.path.join(ROOT, "renders", "measure", "dark_mask.png"), 0) > 0
sk = skeletonize(dark).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(sk, connectivity=8)
nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def longest_path(pix):
    S = set(map(tuple, pix))
    def bfs(start):
        dist = {start: 0}; prev = {start: None}; q = deque([start]); last = start
        while q:
            p = q.popleft(); last = p
            for dy, dx in nb:
                nq = (p[0] + dy, p[1] + dx)
                if nq in S and nq not in dist:
                    dist[nq] = dist[p] + 1; prev[nq] = p; q.append(nq)
        far = max(dist, key=dist.get)
        return far, prev
    a, _ = bfs(tuple(pix[0]))
    b, prev = bfs(a)
    path = []; p = b
    while p is not None:
        path.append(p); p = prev[p]
    return path

def rdp(pts, eps):
    pts = np.asarray(pts, float)
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]
    ab = b - a; L = np.hypot(*ab)
    d = np.abs(np.cross(ab, pts - a)) / L if L > 0 else np.hypot(*(pts - a).T)
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([rdp(pts[:i + 1], eps)[:-1], rdp(pts[i:], eps)])
    return np.vstack([a, b])

out = {}
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] < 40: continue
    ys, xs = np.where(lab == i)
    path = longest_path(np.stack([ys, xs], 1))
    loc = np.array([[X0 + x * mpp, Y1 - y * mpp] for y, x in path])
    simp = rdp(loc, 0.03)
    out[str(len(out))] = {"len_m": round(float(np.sum(np.hypot(*np.diff(loc, axis=0).T))), 2),
                          "pts": [[round(float(x), 3), round(float(y), 3)] for x, y in simp]}

# omtrek betonvlak
park = cv2.imread(os.path.join(ROOT, "renders", "measure", "park_mask.png"), 0)
park = cv2.erode(park, np.ones((15, 15), np.uint8))  # dilatie uit extract_lines ongedaan maken
cnts, _ = cv2.findContours((park > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cnts, key=cv2.contourArea).reshape(-1, 2)
loc = np.array([[X0 + x * mpp, Y1 - y * mpp] for x, y in c])
simp = rdp(np.vstack([loc, loc[:1]]), 0.04)
area = 0.5 * abs(np.dot(loc[:, 0], np.roll(loc[:, 1], 1)) - np.dot(loc[:, 1], np.roll(loc[:, 0], 1)))
out["slab"] = {"area_m2": round(float(area), 1), "pts": [[round(float(x), 3), round(float(y), 3)] for x, y in simp]}
json.dump(out, open(os.path.join(REFS, "polylines.json"), "w"), indent=0)
print("betonvlak m2:", round(float(area), 1), "punten:", len(simp))
for k, v in out.items():
    if k == "slab": continue
    p = v["pts"]
    print(k, v["len_m"], "m", len(p), "pt", p[0], "->", p[-1])
