"""Uitsnede van een foto met pixelgrid (OpenCV-versie, sneller dan Blender)."""
import os, sys
import cv2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def grid(photo, name, x0, y0, x1, y1, step=20, out_w=1400):
    img = cv2.imread(os.path.join(ROOT, "refs", photo))
    c = img[y0:y1, x0:x1].copy()
    s = out_w / (x1 - x0)
    c = cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    for gx in range((x0 // step + 1) * step, x1, step):
        u = int((gx - x0) * s); major = gx % (step * 5) == 0
        cv2.line(c, (u, 0), (u, c.shape[0]), (0, 0, 255) if major else (255, 220, 0), 1)
        if major: cv2.putText(c, str(gx), (u + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
    for gy in range((y0 // step + 1) * step, y1, step):
        v = int((gy - y0) * s); major = gy % (step * 5) == 0
        cv2.line(c, (0, v), (c.shape[1], v), (0, 0, 255) if major else (255, 220, 0), 1)
        if major: cv2.putText(c, str(gy), (2, v - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
    cv2.imwrite(os.path.join(ROOT, "renders", "measure", name + ".jpg"), c)
if __name__ == "__main__":
    a = sys.argv[1:]
    grid(a[0], a[1], *map(int, a[2:6]), step=int(a[6]) if len(a) > 6 else 20)
