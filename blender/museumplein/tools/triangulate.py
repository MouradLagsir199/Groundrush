"""Stereo-triangulatie van één punt uit foto 04 en foto 05 (midpoint-methode)."""
import sys, json
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from heights import load_cam, ray

C4 = load_cam("refs/cam_photo04.json"); C5 = load_cam("refs/cam_photo05.json")


def tri(uv4, uv5):
    a, da = ray(C4, *uv4); b, db = ray(C5, *uv5)
    w = a - b
    A = np.array([[da @ da, -da @ db], [da @ db, -db @ db]])
    rhs = np.array([-(w @ da), -(w @ db)])
    s, t = np.linalg.solve(A, rhs)
    p, q = a + s * da, b + t * db
    return (p + q) / 2, float(np.linalg.norm(p - q))


if __name__ == "__main__":
    pairs = json.loads(sys.argv[1])
    for nm, uv4, uv5 in pairs:
        X, gap = tri(uv4, uv5)
        print(f"{nm:28s} xyz=({X[0]:.3f}, {X[1]:.3f}, {X[2]:.3f})  straalafstand {gap*100:.1f} cm")
