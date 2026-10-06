"""Segmenteert licht (banks/transitions/pads) vs donker (vloeren/decks) beton in de plattegrond."""
import json, os
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
mpp, X0, Y1 = meta["mpp"], meta["x0"], meta["y1"]
park = cv2.imread(os.path.join(ROOT, "renders", "measure", "park_mask.png"), 0) > 0
park = cv2.erode(park.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
lab = cv2.cvtColor(rect, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0]
# vlakke belichting corrigeren met grote mediaan van het park
Ls = cv2.GaussianBlur(L, (0, 0), 1.5)
dark = cv2.imread(os.path.join(ROOT, "renders", "measure", "dark_mask.png"), 0) > 0
Ls[dark] = np.median(Ls[park])
light = (Ls > np.percentile(Ls[park], 55)) & park
light = cv2.morphologyEx(light.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
light = cv2.morphologyEx(light, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "light_mask.png"), light * 255)
cnts, hier = cv2.findContours(light, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
out = []
vis = (rect * 0.5).astype(np.uint8)
for i, c in enumerate(cnts):
    a = cv2.contourArea(c) * mpp * mpp
    if a < 0.6: continue
    ap = cv2.approxPolyDP(c, 2.0, True).reshape(-1, 2)
    pts = [[round(X0 + x * mpp, 3), round(Y1 - y * mpp, 3)] for x, y in ap]
    hole = hier[0][i][3] >= 0
    out.append({"id": len(out), "area": round(a, 2), "hole": bool(hole), "pts": pts})
    col = (0, 255, 255) if not hole else (255, 0, 255)
    cv2.drawContours(vis, [c], -1, col, 2)
    M = cv2.moments(c)
    if M["m00"]:
        cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
        cv2.putText(vis, str(len(out) - 1), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 5)
        cv2.putText(vis, str(len(out) - 1), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
json.dump(out, open(os.path.join(REFS, "regions.json"), "w"))
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "regions.jpg"), cv2.resize(vis, None, fx=0.6, fy=0.6))
for r in out: print(r["id"], r["area"], "gat" if r["hole"] else "", len(r["pts"]))
