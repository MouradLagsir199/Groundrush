"""Referentiemaskers uit de gerectificeerde drone-plattegrond: beton, baksteen."""
import json, os
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]
hsv = cv2.cvtColor(rect, cv2.COLOR_BGR2HSV)
h, s, v = [hsv[:, :, i].astype(int) for i in range(3)]
valid = rect.sum(2) > 0
conc = ((s < 45) & (v > 105)) | ((s < 30) & (v > 80))
conc = conc.astype(np.uint8)
conc = cv2.morphologyEx(conc, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(conc)
conc = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
conc = cv2.morphologyEx(conc, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
# gaten vullen
cnts, _ = cv2.findContours(conc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
conc_f = np.zeros_like(conc); cv2.drawContours(conc_f, [max(cnts, key=cv2.contourArea)], -1, 1, -1)
brick = (((h < 14) | (h > 170)) & (s > 70) & (v > 60) & valid).astype(np.uint8)
brick = cv2.morphologyEx(brick, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
# baksteenring = baksteen die aan beton grenst
ring = cv2.dilate(conc_f, np.ones((121, 121), np.uint8)) & brick & (1 - conc_f)
n, lab, st, _ = cv2.connectedComponentsWithStats(ring)
keep = np.zeros_like(ring)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] > 4000: keep[lab == i] = 1
outer = cv2.morphologyEx(conc_f | keep, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
cnts, _ = cv2.findContours(outer, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
outer_f = np.zeros_like(outer); cv2.drawContours(outer_f, [max(cnts, key=cv2.contourArea)], -1, 1, -1)
cv2.imwrite(os.path.join(REFS, "mask_concrete.png"), conc_f * 255)
cv2.imwrite(os.path.join(REFS, "mask_outer.png"), outer_f * 255)
vis = rect.copy()
for m, col in [(conc_f, (0, 255, 255)), (outer_f, (255, 0, 255))]:
    c, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(vis, c, -1, col, 3)
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "masks.jpg"), cv2.resize(vis, None, fx=0.4, fy=0.4))
print("beton m2", round(conc_f.sum() * mpp * mpp, 1), " buitenrand m2", round(outer_f.sum() * mpp * mpp, 1))
