"""Registreert de drone-foto op de PDOK-luchtfoto (SIFT + RANSAC-homografie).

Output: refs/drone_rectified.png in het lokale meterstelsel (zie scripts/common.py),
plus refs/H_drone.json met de homografie lokale-meters -> drone-pixels.
"""
import json
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
ORTHO = os.path.join(REFS, "ortho_2026_orthoHR.jpg")
DRONE = os.path.join(REFS, "drone_top.jpg")
MPP_O = 70.0 / 1400  # 0.05 m per pixel
O_MINX, O_MAXY = 120675.0 - 120710.0, 485765.0 - 485730.0  # lokale coördinaten linksboven: (-35, 35)

o = cv2.imread(ORTHO)
d = cv2.imread(DRONE)
og = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY)
dg = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
og = clahe.apply(og)
dg_small = cv2.resize(dg, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
dg_small = clahe.apply(dg_small)

sift = cv2.SIFT_create(nfeatures=20000)
ko, do_ = sift.detectAndCompute(og, None)
kd, dd = sift.detectAndCompute(dg_small, None)
print("keypoints", len(ko), len(kd))
bf = cv2.BFMatcher(cv2.NORM_L2)
matches = bf.knnMatch(dd, do_, k=2)
good = [m for m, n in matches if m.distance < 0.8 * n.distance]
print("good matches", len(good))
src = np.float32([kd[m.queryIdx].pt for m in good]) / 0.6  # drone-pixels (volle resolutie)
dst = np.float32([ko[m.trainIdx].pt for m in good])        # ortho-pixels
H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 6.0, maxIters=20000, confidence=0.999)
inl = int(mask.sum()) if mask is not None else 0
print("inliers", inl)
if H is None or inl < 12:
    sys.exit("registratie mislukt")

# residu in meters
p = cv2.perspectiveTransform(src[mask.ravel() == 1].reshape(-1, 1, 2), H).reshape(-1, 2)
res = np.linalg.norm(p - dst[mask.ravel() == 1], axis=1) * MPP_O
print("residu (m): mediaan %.3f, p90 %.3f, max %.3f" % (np.median(res), np.percentile(res, 90), res.max()))

# ortho-pixel -> lokaal: x = O_MINX + px*mpp ; y = O_MAXY - py*mpp
A = np.array([[MPP_O, 0, O_MINX], [0, -MPP_O, O_MAXY], [0, 0, 1]])  # ortho px -> lokaal
H_d2l = A @ H                                   # drone px -> lokaal
H_l2d = np.linalg.inv(H_d2l)
json.dump({"H_local_to_drone": H_l2d.tolist(), "H_drone_to_local": H_d2l.tolist(),
           "inliers": inl, "median_residual_m": float(np.median(res))},
          open(os.path.join(REFS, "H_drone.json"), "w"), indent=1)

# rectificeren naar lokaal raster: x -20..25, y -27..25 op 0.02 m/px
MPP_R = 0.02
X0, X1, Y0, Y1 = -20.0, 25.0, -27.0, 25.0
W, Hh = int((X1 - X0) / MPP_R), int((Y1 - Y0) / MPP_R)
B = np.array([[MPP_R, 0, X0], [0, -MPP_R, Y1], [0, 0, 1]])  # rect px -> lokaal
M = H_l2d @ B                                              # rect px -> drone px
rect = cv2.warpPerspective(d, M, (W, Hh), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
cv2.imwrite(os.path.join(REFS, "drone_rectified.png"), rect)
json.dump({"x0": X0, "x1": X1, "y0": Y0, "y1": Y1, "mpp": MPP_R}, open(os.path.join(REFS, "drone_rectified.json"), "w"))

# controle-overlay op ortho-raster
o_l = cv2.warpPerspective(o, np.linalg.inv(A) @ B, (W, Hh), flags=cv2.INTER_LINEAR)
blend = cv2.addWeighted(rect, 0.5, o_l, 0.5, 0)
cv2.imwrite(os.path.join(ROOT, "renders", "measure", "registration_blend.jpg"), cv2.resize(blend, None, fx=0.5, fy=0.5))
print("klaar", W, Hh)
