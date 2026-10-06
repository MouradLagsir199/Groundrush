"""Uitsneden (lokale meters) uit het gerectificeerde drone-beeld, optioneel geblend met ortho en met metergrid."""
import json, os, sys
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png"))
meta = json.load(open(os.path.join(REFS, "drone_rectified.json")))
o = cv2.imread(os.path.join(REFS, "ortho_2026_orthoHR.jpg"))
mpp = meta["mpp"]; X0, Y1 = meta["x0"], meta["y1"]
A = np.array([[0.05, 0, -35.0], [0, -0.05, 35.0], [0, 0, 1]])
B = np.array([[mpp, 0, X0], [0, -mpp, Y1], [0, 0, 1]])
o_l = cv2.warpPerspective(o, np.linalg.inv(A) @ B, (rect.shape[1], rect.shape[0]), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)

def crop(name, cx, cy, w, mode="blend", step=1.0, out_px=1400):
    img = {"blend": cv2.addWeighted(rect, 0.5, o_l, 0.5, 0), "drone": rect, "ortho": o_l}[mode].copy()
    px0 = int((cx - w / 2 - X0) / mpp); py0 = int((Y1 - (cy + w / 2)) / mpp)
    n = int(w / mpp)
    c = img[max(py0, 0):py0 + n, max(px0, 0):px0 + n]
    c = cv2.resize(c, (out_px, out_px), interpolation=cv2.INTER_CUBIC)
    s = out_px / w
    x = np.ceil((cx - w / 2) / step) * step
    while x <= cx + w / 2:
        u = int((x - (cx - w / 2)) * s)
        major = abs(x - round(x)) < 1e-6 and int(round(x)) % 5 == 0
        cv2.line(c, (u, 0), (u, out_px), (0, 0, 255) if major else (255, 200, 0), 2 if major else 1)
        x += step
    y = np.ceil((cy - w / 2) / step) * step
    while y <= cy + w / 2:
        v = int(((cy + w / 2) - y) * s)
        major = abs(y - round(y)) < 1e-6 and int(round(y)) % 5 == 0
        cv2.line(c, (0, v), (out_px, v), (0, 0, 255) if major else (255, 200, 0), 2 if major else 1)
        y += step
    lx = np.ceil((cx - w / 2)); 
    while lx <= cx + w / 2:
        ly = np.ceil(cy - w / 2)
        while ly <= cy + w / 2:
            if (int(lx) % 2 == 0) and (int(ly) % 2 == 0):
                u = int((lx - (cx - w / 2)) * s) + 3; v = int(((cy + w / 2) - ly) * s) - 4
                cv2.putText(c, f"{int(lx)},{int(ly)}", (u, v), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
                cv2.putText(c, f"{int(lx)},{int(ly)}", (u, v), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            ly += 1
        lx += 1
    os.makedirs(os.path.join(ROOT, "renders", "measure"), exist_ok=True)
    cv2.imwrite(os.path.join(ROOT, "renders", "measure", name + ".jpg"), c)

if __name__ == "__main__":
    a = sys.argv[1:]
    crop(a[0], float(a[1]), float(a[2]), float(a[3]), a[4] if len(a) > 4 else "blend", float(a[5]) if len(a) > 5 else 1.0)
