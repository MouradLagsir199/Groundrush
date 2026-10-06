"""Registratie drone -> lokaal via handmatige paspunten, optioneel verfijnd met ECC op randen.

Gebruik: python register_manual.py [--ecc]
Paspunten staan in refs/gcp_drone.json: [[drone_px, drone_py, local_x, local_y], ...]
"""
import json
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
OUT = os.path.join(ROOT, "renders", "measure")
o = cv2.imread(os.path.join(REFS, "ortho_2026_orthoHR.jpg"))
d = cv2.imread(os.path.join(REFS, "drone_top.jpg"))
MPP_O = 0.05
A = np.array([[MPP_O, 0, -35.0], [0, -MPP_O, 35.0], [0, 0, 1]])  # ortho px -> lokaal

gcp = np.array(json.load(open(os.path.join(REFS, "gcp_drone.json"))), dtype=np.float64)
H_d2l, _ = cv2.findHomography(gcp[:, :2], gcp[:, 2:], 0)
pred = cv2.perspectiveTransform(gcp[:, :2].reshape(-1, 1, 2), H_d2l).reshape(-1, 2)
print("GCP-residu (m):", np.round(np.linalg.norm(pred - gcp[:, 2:], axis=1), 3))

MPP_R = 0.02
X0, X1, Y0, Y1 = -20.0, 25.0, -27.0, 25.0
W, Hh = int((X1 - X0) / MPP_R), int((Y1 - Y0) / MPP_R)
B = np.array([[MPP_R, 0, X0], [0, -MPP_R, Y1], [0, 0, 1]])


def warp(H_d2l):
    M = np.linalg.inv(H_d2l) @ B
    return cv2.warpPerspective(d, M, (W, Hh), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)


o_l = cv2.warpPerspective(o, np.linalg.inv(A) @ B, (W, Hh), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
# let op: WARP_INVERSE_MAP verwacht dst->src; hier is (inv(A) @ B) rect px -> ortho px

if "--ecc" in sys.argv:
    # ECC op gradiëntbeelden, lagere resolutie, alleen binnen het park
    s = 0.25
    def grad(img):
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 2.0)
        gx = cv2.Sobel(g, cv2.CV_32F, 1, 0); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
        m = cv2.magnitude(gx, gy)
        return cv2.normalize(m, None, 0, 1, cv2.NORM_MINMAX)
    rect = warp(H_d2l)
    a = cv2.resize(grad(o_l), None, fx=s, fy=s)
    b = cv2.resize(grad(rect), None, fx=s, fy=s)
    warpM = np.eye(3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 500, 1e-6)
    cc, warpM = cv2.findTransformECC(a, b, warpM, cv2.MOTION_HOMOGRAPHY, crit, None, 5)
    print("ECC correlatie", round(cc, 4))
    # warpM: a-px -> b-px (beide op schaal s van het rect-raster). Omzetten naar lokaal.
    Sm = np.diag([s, s, 1.0])
    Mrect = np.linalg.inv(Sm) @ warpM @ Sm           # rect px (ortho-gerelateerd) -> rect px (drone-warp)
    # lokaal(true) -> rect px -> (Mrect) -> rect px drone -> lokaal(drone-schatting) -> drone px
    H_l2d = np.linalg.inv(H_d2l) @ B @ Mrect @ np.linalg.inv(B)
    H_d2l = np.linalg.inv(H_l2d)
    pred = cv2.perspectiveTransform(gcp[:, :2].reshape(-1, 1, 2), H_d2l).reshape(-1, 2)
    print("GCP-verschuiving na ECC (m):", np.round(np.linalg.norm(pred - gcp[:, 2:], axis=1), 3))

rect = warp(H_d2l)
cv2.imwrite(os.path.join(REFS, "drone_rectified.png"), rect)
json.dump({"H_drone_to_local": H_d2l.tolist(), "H_local_to_drone": np.linalg.inv(H_d2l).tolist()},
          open(os.path.join(REFS, "H_drone.json"), "w"), indent=1)
json.dump({"x0": X0, "x1": X1, "y0": Y0, "y1": Y1, "mpp": MPP_R}, open(os.path.join(REFS, "drone_rectified.json"), "w"))
# controlebeeld: drone in rood/groen-kanalen tegen ortho
g1 = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY)
g2 = cv2.cvtColor(o_l, cv2.COLOR_BGR2GRAY)
check = cv2.merge([g2, g1, g2])  # magenta = ortho, groen = drone
cv2.imwrite(os.path.join(OUT, "registration_check.jpg"), cv2.resize(check, None, fx=0.6, fy=0.6))
blend = cv2.addWeighted(rect, 0.5, o_l, 0.5, 0)
cv2.imwrite(os.path.join(OUT, "registration_blend.jpg"), cv2.resize(blend, None, fx=0.6, fy=0.6))
print("klaar")
