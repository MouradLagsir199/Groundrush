"""Haalt donkere lijnen (coping, rails, ledge-randen) uit de gerectificeerde drone-plattegrond.

Output: refs/lines.json met polylijnen in lokale meters + renders/measure/lines_ids.jpg ter controle.
"""
import json, os
import cv2
import numpy as np
from skimage.morphology import skeletonize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]
hsv = cv2.cvtColor(rect, cv2.COLOR_BGR2HSV)
v = hsv[:, :, 2].astype(np.int16)
s = hsv[:, :, 1].astype(np.int16)
# beton is licht en grijs; lijnen zijn donker. Gebruik lokaal contrast t.o.v. vervaagde omgeving.
gray = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY).astype(np.float32)
bg = cv2.GaussianBlur(gray, (0, 0), 6)
dark = ((bg - gray) > 35) & (gray < 110) & (s < 90)
# parkmasker: concrete-achtig gebied (grijs, laag verzadigd) - grof
conc = ((s < 40) & (v > 120)).astype(np.uint8)
conc = cv2.morphologyEx(conc, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
conc = cv2.morphologyEx(conc, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(conc)
big = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
park = (lab == big).astype(np.uint8)
park = cv2.dilate(park, np.ones((15, 15), np.uint8))
dark &= park.astype(bool)
dark = cv2.morphologyEx(dark.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "dark_mask.png"), dark * 255)
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "park_mask.png"), park * 255)

sk = skeletonize(dark > 0).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(sk, connectivity=8)
lines = []
vis = (rect * 0.55).astype(np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] < 40:  # < 0.8 m skeletonlengte
        continue
    ys, xs = np.where(lab == i)
    pts = np.stack([xs, ys], 1)
    # ordenen via contour van het (dunne) component
    comp = (lab == i).astype(np.uint8)
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=len)
    ap = cv2.approxPolyDP(c, 2.5, False).reshape(-1, 2)  # 5 cm tolerantie
    loc = [[round(X0 + x * mpp, 3), round(Y1 - y * mpp, 3)] for x, y in ap]
    L = stats[i, cv2.CC_STAT_AREA] * mpp
    lines.append({"id": len(lines), "len_m": round(L, 2), "pts": loc,
                  "bbox": [round(X0 + xs.min() * mpp, 2), round(Y1 - ys.max() * mpp, 2), round(X0 + xs.max() * mpp, 2), round(Y1 - ys.min() * mpp, 2)]})
    col = tuple(int(c) for c in np.random.RandomState(i).randint(80, 255, 3))
    vis[lab == i] = col
    cv2.putText(vis, str(len(lines) - 1), (int(xs.mean()) + 4, int(ys.mean())), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4)
    cv2.putText(vis, str(len(lines) - 1), (int(xs.mean()) + 4, int(ys.mean())), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
json.dump(lines, open(os.path.join(REFS, "lines.json"), "w"), indent=0)
vis = cv2.dilate(vis, np.ones((2, 2), np.uint8))
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "lines_ids.jpg"), cv2.resize(vis, None, fx=0.6, fy=0.6))
print(len(lines), "lijnen")
for l in sorted(lines, key=lambda l: -l["len_m"])[:80]:
    print(l["id"], l["len_m"], l["bbox"])
