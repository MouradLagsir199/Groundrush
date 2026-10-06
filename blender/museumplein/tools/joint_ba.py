"""Gezamenlijke bundelvereffening van camera 04 en 05 met GCP's (bekende xyz) en verbindingspunten
(drone-schijnbare xy + beide foto's, xyz onbekend). Schrijft refs/cam_photo04.json / cam_photo05.json (v4)."""
import json, math, sys
import numpy as np
import cv2
from scipy.optimize import least_squares
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from camsolve import LEAN

DRONE_SIGMA = 0.04  # m per "pixel-equivalent"


def load_gcp(ph):
    cfg = json.load(open(f"refs/gcp_{ph}.json"))
    env = dict(cfg["params"]); env["math"] = math
    try:
        env.update(json.load(open(f"refs/cam_{ph}.json"))["params"])
    except Exception:
        pass
    obs = []
    for p in cfg["points"]:
        z = eval(p[4], {}, env)
        zd = eval(p[6], {}, env) if len(p) > 6 else 0.0
        obs.append((p[0], p[1], p[2] - LEAN[0] * zd, p[3] - LEAN[1] * zd, z, p[5]))
    return obs


def proj(par, X):
    rvec, C, f, cx, cy = par[:3], par[3:6], par[6], par[7], par[8]
    R, _ = cv2.Rodrigues(rvec)
    Pc = (X - C) @ R.T
    return np.stack([f * Pc[:, 0] / Pc[:, 2] + cx, f * Pc[:, 1] / Pc[:, 2] + cy], 1)


def cam_par(ph):
    c = json.load(open(f"refs/cam_{ph}.json"))
    return np.array(list(c["rvec"]) + list(c["cam_pos"]) + [c["f"], c.get("cx", 1000), c.get("cy", 667)], float)


def main():
    ties = json.load(open("refs/ties.json"))
    g4, g5 = load_gcp("photo04"), load_gcp("photo05")
    p4, p5 = cam_par("photo04"), cam_par("photo05")
    X0 = []
    for t in ties:
        z0 = t.get("z0", 0.5)
        X0 += [t["drone"][0] - LEAN[0] * z0, t["drone"][1] - LEAN[1] * z0, z0]
    x0 = np.concatenate([p4, p5, np.array(X0)])

    def res(x):
        a, b = x[:9], x[9:18]
        T = x[18:].reshape(-1, 3)
        r = []
        for par, g in ((a, g4), (b, g5)):
            G = np.array([[o[2], o[3], o[4]] for o in g]); UV = np.array([[o[0], o[1]] for o in g])
            r.append((proj(par, G) - UV).ravel())
        for i, t in enumerate(ties):
            Xt = T[i]
            app = Xt[:2] + np.array(LEAN) * Xt[2]
            r.append((app - np.array(t["drone"])) / DRONE_SIGMA)
            if "p04" in t:
                r.append((proj(a, Xt[None]) - np.array(t["p04"])).ravel())
            if "p05" in t:
                r.append((proj(b, Xt[None]) - np.array(t["p05"])).ravel())
        return np.concatenate(r)

    sol = least_squares(res, x0, loss="soft_l1", f_scale=3.0, max_nfev=50000)
    a, b = sol.x[:9], sol.x[9:18]; T = sol.x[18:].reshape(-1, 3)
    for nm, par, g in (("photo04", a, g4), ("photo05", b, g5)):
        G = np.array([[o[2], o[3], o[4]] for o in g]); UV = np.array([[o[0], o[1]] for o in g])
        e = np.linalg.norm(proj(par, G) - UV, axis=1)
        print(f"{nm}: GCP rms {np.sqrt(np.mean(e**2)):.2f} px, max {e.max():.1f} ({g[int(np.argmax(e))][5]})")
    for t, Xt in zip(ties, T):
        msg = f"  {t['name']:22s} xyz=({Xt[0]:.3f},{Xt[1]:.3f},{Xt[2]:.3f})"
        app = Xt[:2] + np.array(LEAN) * Xt[2]
        msg += f" drone-res {np.linalg.norm(app-np.array(t['drone']))*100:.1f} cm"
        if "p04" in t: msg += f" p04-res {np.linalg.norm(proj(a, Xt[None])[0]-np.array(t['p04'])):.1f}px"
        if "p05" in t: msg += f" p05-res {np.linalg.norm(proj(b, Xt[None])[0]-np.array(t['p05'])):.1f}px"
        print(msg)
    if "--write" in sys.argv:
        for nm, par in (("photo04", a), ("photo05", b)):
            c = json.load(open(f"refs/cam_{nm}.json"))
            json.dump(c, open(f"refs/cam_{nm}_v3b.json", "w"), indent=1)
            c.update({"rvec": par[:3].tolist(), "cam_pos": par[3:6].tolist(), "f": float(par[6]), "cx": float(par[7]), "cy": float(par[8]), "version": "v4-joint"})
            json.dump(c, open(f"refs/cam_{nm}.json", "w"), indent=1)
        json.dump([{"name": t["name"], "xyz": Xt.tolist()} for t, Xt in zip(ties, T)], open("refs/ties_solved.json", "w"), indent=1)
        print("camera's geschreven (v4)")


if __name__ == "__main__":
    main()
