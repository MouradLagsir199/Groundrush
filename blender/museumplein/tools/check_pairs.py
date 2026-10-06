"""Rand-metriek per kleurpaar in de render, met verwacht beeldkanaal en teken.

spec: lijst van (naam, kleurA(rgb 0-255 of None=transparant), kleurB, kanaal, teken)
teken +1: kanaalwaarde stijgt van A naar B.
"""
import json, os, sys
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "refs")
OUT = os.path.join(ROOT, "renders", "check")
rect = cv2.imread(os.path.join(REFS, "drone_rectified.png")).astype(np.float32)
mpp = json.load(open(os.path.join(REFS, "drone_rectified.json")))["mpp"]
CH = {
    "lum": cv2.GaussianBlur(rect.mean(2), (0, 0), 2.0),
    "red": cv2.GaussianBlur(rect[:, :, 2] - (rect[:, :, 0] + rect[:, :, 1]) / 2, (0, 0), 2.0),
    "sat": cv2.GaussianBlur(cv2.cvtColor(rect.astype(np.uint8), cv2.COLOR_BGR2HSV)[:, :, 1].astype(np.float32), (0, 0), 2.0),
}


def region(rgba, col):
    if col is None:
        return rgba[:, :, 3] < 128
    c = np.array(col)
    return (rgba[:, :, 3] >= 128) & (np.abs(rgba[:, :, :3].astype(int) - c).max(2) < 12)


def pair_metric(rgba, A, B, chan, sign, search=0.3):
    ra, rb = region(rgba, A), region(rgba, B)
    # randpixels van A die grenzen aan B
    rb_d = cv2.dilate(rb.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    edge = ra & rb_d
    ys, xs = np.where(edge)
    if len(xs) == 0:
        return None
    sel = np.arange(len(xs))[:: max(1, len(xs) // 4000)]
    ys, xs = ys[sel], xs[sel]
    ind = cv2.GaussianBlur(rb.astype(np.float32) - ra.astype(np.float32), (0, 0), 3.0)
    nx = cv2.Sobel(ind, cv2.CV_32F, 1, 0, ksize=3); ny = cv2.Sobel(ind, cv2.CV_32F, 0, 1, ksize=3)
    nn = np.hypot(nx[ys, xs], ny[ys, xs]) + 1e-9
    ux, uy = nx[ys, xs] / nn, ny[ys, xs] / nn  # wijst van A naar B
    steps = np.arange(-search, search + 1e-9, 0.01) / mpp
    px = (xs[:, None] + ux[:, None] * steps[None, :]).astype(np.float32)
    py = (ys[:, None] + uy[:, None] * steps[None, :]).astype(np.float32)
    v = cv2.remap(CH[chan], px, py, cv2.INTER_LINEAR)
    dv = np.gradient(v, axis=1) * sign
    i = np.argmax(dv, axis=1)
    ok = dv[np.arange(len(i)), i] > 0.6
    off = steps[i] * mpp
    return np.abs(off[ok]), off[ok], xs[ok], ys[ok]


if __name__ == "__main__":
    tag = sys.argv[1]
    spec = json.loads(sys.argv[2])
    rgba = cv2.imread(os.path.join(OUT, f"top_{tag}.png"), cv2.IMREAD_UNCHANGED)[:, :, [2, 1, 0, 3]]
    res = {}
    allv = []
    for name, A, B, chan, sign, *rest in spec:
        search = rest[0] if rest else 0.3
        r = pair_metric(rgba, A, B, chan, sign, search)
        if r is None:
            print(f"  {name}: geen randen"); continue
        d, off, xs, ys = r
        allv.append(d)
        res[name] = {"median_cm": float(np.median(d) * 100), "p80_cm": float(np.percentile(d, 80) * 100), "p95_cm": float(np.percentile(d, 95) * 100), "bias_cm": float(np.median(off) * 100), "n": int(len(d))}
        print(f"  {name:18s} n={len(d):5d}  mediaan {np.median(d)*100:5.1f} cm  p80 {np.percentile(d,80)*100:5.1f}  p95 {np.percentile(d,95)*100:5.1f}  bias {np.median(off)*100:+5.1f} cm")
    json.dump(res, open(os.path.join(OUT, f"pairs_{tag}.json"), "w"), indent=1)
