"""Fit camera (positie, oriëntatie, brandpuntsafstand) + onbekende hoogtes aan paspunten.

GCP-bestand (JSON): {"photo": "...", "size": [w,h], "init": {"cam": [x,y,z], "look": [x,y,z], "f": px},
  "params": {"r": 0.15, ...}, "points": [[u, v, X, Y, "zexpr", "label"], ...]}
zexpr is een Python-expressie in de parameters (bijv. "0", "hL7", "3.5*r").
"""
import json, sys, math
import numpy as np
from scipy.optimize import least_squares
import cv2

LEAN = (0.07, 0.25)


def look_rvec(cam, look):
    cam, look = np.array(cam, float), np.array(look, float)
    fwd = look - cam; fwd /= np.linalg.norm(fwd)
    up = np.array([0, 0, 1.0])
    right = np.cross(fwd, up); right /= np.linalg.norm(right)
    down = np.cross(fwd, right)
    R = np.stack([right, down, fwd])  # wereld -> camera (x rechts, y omlaag, z vooruit)
    rvec, _ = cv2.Rodrigues(R)
    return rvec.ravel()


def project(params_cam, f, cx, cy, P, k1=0.0, k2=0.0):
    rvec, cam = params_cam[:3], params_cam[3:6]
    R, _ = cv2.Rodrigues(rvec)
    Pc = (R @ (P - cam).T).T
    x = Pc[:, 0] / Pc[:, 2]; y = Pc[:, 1] / Pc[:, 2]
    r2 = x * x + y * y
    d = 1 + k1 * r2 + k2 * r2 * r2
    u = f * x * d + cx
    v = f * y * d + cy
    return np.stack([u, v], 1), Pc[:, 2]


def solve(cfg, fixed=None, verbose=True, dist=False, pp=False):
    fixed = fixed or {}
    w, h = cfg["size"]; cx, cy = w / 2, h / 2
    pnames = [k for k in cfg["params"] if k not in fixed]
    if dist:
        pnames = pnames + ["_k1", "_k2"]
        cfg = dict(cfg); cfg["params"] = dict(cfg["params"], _k1=0.0, _k2=0.0)
    if pp:
        pnames = pnames + ["_cx", "_cy"]
        cfg = dict(cfg); cfg["params"] = dict(cfg["params"], _cx=0.0, _cy=0.0)
    x0 = list(look_rvec(cfg["init"]["cam"], cfg["init"]["look"])) + list(cfg["init"]["cam"]) + [cfg["init"]["f"]] + [cfg["params"][k] for k in pnames]
    pts = cfg["points"]
    UV = np.array([[p[0], p[1]] for p in pts], float)

    def unpack(x):
        env = dict(fixed); env.update({k: x[7 + i] for i, k in enumerate(pnames)}); env["math"] = math
        rows = []
        for p in pts:
            z = eval(p[4], {}, env)
            zd = eval(p[6], {}, env) if len(p) > 6 else 0.0   # hoogte van het kenmerk zoals de drone het ziet
            rows.append([p[2] - LEAN[0] * zd, p[3] - LEAN[1] * zd, z])
        P = np.array(rows, float)
        return x[:6], x[6], P, env

    def resid(x):
        cam, f, P, env = unpack(x)
        uv, z = project(cam, f, cx + env.get("_cx", 0.0), cy + env.get("_cy", 0.0), P, env.get("_k1", 0.0), env.get("_k2", 0.0))
        r = (uv - UV).ravel()
        r = np.where(np.isfinite(r), r, 1e4)
        return r

    sol = least_squares(resid, x0, loss="soft_l1", f_scale=3.0, max_nfev=20000)
    cam, f, P, env = unpack(sol.x)
    uv, z = project(cam, f, cx + env.get("_cx", 0.0), cy + env.get("_cy", 0.0), P, env.get("_k1", 0.0), env.get("_k2", 0.0))
    err = np.linalg.norm(uv - UV, axis=1)
    R, _ = cv2.Rodrigues(cam[:3])
    fwd = R[2]
    out = {"cam_pos": cam[3:6].tolist(), "rvec": cam[:3].tolist(), "f": float(f), "fov_h_deg": math.degrees(2 * math.atan(w / 2 / f)),
           "depression_deg": math.degrees(math.asin(-fwd[2])), "heading_deg": (math.degrees(math.atan2(fwd[0], fwd[1])) + 360) % 360,
           "params": {k: env[k] for k in cfg["params"] if not k.startswith("_")}, "rms_px": float(np.sqrt(np.mean(err ** 2))),
           "k1": float(env.get("_k1", 0.0)), "k2": float(env.get("_k2", 0.0)),
           "cx": float(cx + env.get("_cx", 0.0)), "cy": float(cy + env.get("_cy", 0.0))}
    if verbose:
        print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items() if k != "params"}, indent=0))
        print("hoogtes:", {k: round(v, 3) for k, v in out["params"].items()})
        for p, e, q in zip(pts, err, uv):
            print(f"  {p[5] if len(p) > 5 else '':28s} fout {e:6.1f}px  ({q[0]:.0f},{q[1]:.0f}) vs ({p[0]},{p[1]})")
    return out, sol


if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    out, _ = solve(cfg)
    if len(sys.argv) > 2:
        json.dump(out, open(sys.argv[2], "w"), indent=1)
