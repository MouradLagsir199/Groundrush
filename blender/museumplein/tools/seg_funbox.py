"""Segmenteert de funbox in vloer / bank / dek (drone-plattegrond) en schrijft polygonen (schijnbare xy)."""
import cv2, numpy as np, json
r = cv2.imread('refs/drone_rectified.png'); meta = json.load(open('refs/drone_rectified.json'))
mpp, X0, Y1 = meta['mpp'], meta['x0'], meta['y1']
lab = cv2.cvtColor(cv2.GaussianBlur(r, (0, 0), 2.0), cv2.COLOR_BGR2LAB).astype(np.float32)
L, A, B = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]
x0, x1, y0, y1 = -7.0, 10.0, -2.2, 9.0
sl = (slice(int((Y1 - y1) / mpp), int((Y1 - y0) / mpp)), slice(int((x0 - X0) / mpp), int((x1 - X0) / mpp)))
Lc, Ac, Bc = L[sl], A[sl], B[sl]
bank = (Lc > 206).astype(np.uint8)
deck = ((Ac + Bc > 259.6) & (Lc > 186) & (Lc <= 210)).astype(np.uint8)
dark = cv2.imread('renders/measure/dark_mask.png', 0)[sl] > 0
deck[dark] = 0; bank[dark] = 0
k = lambda n: np.ones((n, n), np.uint8)
bank = cv2.morphologyEx(cv2.morphologyEx(bank, cv2.MORPH_CLOSE, k(9)), cv2.MORPH_OPEN, k(9))
deck = cv2.morphologyEx(cv2.morphologyEx(deck, cv2.MORPH_OPEN, k(7)), cv2.MORPH_CLOSE, k(15))
def polys(mask, min_area):
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cnts:
        a = cv2.contourArea(c) * mpp * mpp
        if a < min_area: continue
        ap = cv2.approxPolyDP(c, 3.0, True).reshape(-1, 2)
        out.append({"area": round(a, 2), "pts": [[round(x0 + px * mpp, 3), round(y1 - py * mpp, 3)] for px, py in ap]})
    return out
res = {"deck": polys(deck, 2.0), "bank_plus_deck": polys(((bank | deck) > 0).astype(np.uint8) * 1, 20.0)}
json.dump(res, open('refs/funbox_seg.json', 'w'), indent=1)
vis = r[sl].copy()
vis[bank > 0] = (0.5 * vis[bank > 0] + [0, 120, 0]).astype(np.uint8)
vis[deck > 0] = (0.5 * vis[deck > 0] + [0, 0, 120]).astype(np.uint8)
cv2.imwrite('renders/measure/funbox_seg.jpg', cv2.resize(vis, None, fx=0.6, fy=0.6))
for k_, v in res.items():
    for p in v: print(k_, p['area'], len(p['pts']))
