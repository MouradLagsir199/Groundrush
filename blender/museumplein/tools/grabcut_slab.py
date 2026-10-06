"""Betonvlak-contour via GrabCut, daarna glad (spline) en vereenvoudigd."""
import json, os, sys
import cv2
import numpy as np
from scipy.interpolate import splprep, splev
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contour_fit import edge_offsets
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]
m0 = cv2.imread(os.path.join(REFS, "mask_concrete.png"), 0) > 0
s = 0.5
small = cv2.resize(rect, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
m0s = cv2.resize(m0.astype(np.uint8), (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
gc = np.full(m0s.shape, cv2.GC_BGD, np.uint8)
gc[cv2.dilate(m0s, np.ones((41, 41), np.uint8)) > 0] = cv2.GC_PR_BGD
gc[m0s > 0] = cv2.GC_PR_FGD
gc[cv2.erode(m0s, np.ones((41, 41), np.uint8)) > 0] = cv2.GC_FGD
bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
cv2.grabCut(small, gc, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
fg = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)
fg = cv2.resize(fg, (rect.shape[1], rect.shape[0]), interpolation=cv2.INTER_LINEAR)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
fg = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cnts, key=cv2.contourArea).reshape(-1, 2).astype(float)
loc = np.stack([X0 + c[:, 0] * mpp, Y1 - c[:, 1] * mpp], 1)
# gladstrijken met periodieke spline
step = 5
tck, u = splprep([loc[::step, 0], loc[::step, 1]], s=len(loc[::step]) * 0.0008, per=True)
uu = np.linspace(0, 1, 2400, endpoint=False)
sx, sy = splev(uu, tck)
sm = np.stack([sx, sy], 1)
# oriëntatie: met de klok mee (buiten = links)
area = 0.5 * np.sum(sm[:, 0] * np.roll(sm[:, 1], -1) - np.roll(sm[:, 0], -1) * sm[:, 1])
if area > 0: sm = sm[::-1]
off, stg = edge_offsets(sm, "lum", -1, search=0.25, outward=+1)
print("oppervlak m2", round(abs(area), 1))
print("randafwijking t.o.v. sterkste lum-rand: mediaan %.1f cm, p80 %.1f cm" % (np.median(np.abs(off)) * 100, np.percentile(np.abs(off), 80) * 100))
np.save(os.path.join(REFS, "slab_outline_raw.npy"), sm)
cv2.imwrite(os.path.join(REFS, "mask_slab_grabcut.png"), fg * 255)
vis = rect.copy()
pts = np.stack([(sm[:, 0] - X0) / mpp, (Y1 - sm[:, 1]) / mpp], 1).astype(np.int32)
cv2.polylines(vis, [pts.reshape(-1, 1, 2)], True, (0, 255, 255), 2)
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "slab_grabcut.jpg"), cv2.resize(vis, None, fx=0.45, fy=0.45))
