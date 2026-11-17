# World map data — PURE PYTHON (no bpy). Bundled into worldmap.py (--lib) and imported by tools/pack_scenery.py.
import math

MAP_W, MAP_H = 2048, 1024
ORTHO = 40.0                 # world units across the image width
TILT = 35.0                  # degrees away from straight-down
CAM_T = (20.0, 11.5, 0.0)    # point at the image centre

# id, name, centre (x, y), base colour (sRGB)
REGIONS = [
    ("r1", "Cinderfold Vale", (6.5, 7.0), (0.42, 0.46, 0.36)),
    ("r2", "The Bell Marshes", (12.0, 16.5), (0.3, 0.38, 0.33)),
    ("r3", "Gilded Causeway", (19.0, 7.5), (0.66, 0.56, 0.34)),
    ("r4", "Hollowdeep Mines", (25.5, 17.5), (0.36, 0.34, 0.37)),
    ("r5", "The Ember Wastes", (31.0, 7.5), (0.52, 0.25, 0.15)),
    ("r6", "The Cinder Maw", (36.0, 15.5), (0.16, 0.13, 0.13)),
]
ROAD = [(3.5, 5.0), (6.5, 7.0), (8.5, 11.5), (12.0, 16.5), (15.0, 13.0), (17.0, 9.0), (19.0, 7.5), (21.5, 10.5),
        (23.5, 15.0), (25.5, 17.5), (28.0, 14.0), (29.5, 9.5), (31.0, 7.5), (33.5, 10.0), (35.0, 13.0), (36.0, 15.5)]


def _n(x, y, s):
    return (math.sin(x * 0.9 + s) * math.cos(y * 1.1 - s * 0.7) + 0.5 * math.sin(x * 2.3 + y * 1.7 + s * 2.1)
            + 0.25 * math.sin(x * 4.7 - y * 3.9 + s)) / 1.75


def height(x, y):
    # island mask
    dx = (x - 20.0) / 20.5; dy = (y - 12.0) / 11.0
    m = 1.0 - (abs(dx) ** 3 + abs(dy) ** 3) ** (1 / 3)
    h = -0.6 + 3.0 * m + 0.25 * _n(x, y, 1.0)
    h = min(h, 0.35 + 0.12 * _n(x, y, 2.0)) if h > 0.35 else h
    # mountains (r4) and ridges
    d4 = math.hypot(x - 25.5, (y - 18.5) * 1.3)
    h += max(0.0, 1 - d4 / 6.0) ** 1.5 * (2.6 + 1.2 * _n(x * 1.6, y * 1.6, 3.0))
    # marsh dips (r2)
    d2 = math.hypot(x - 11.5, y - 16.0)
    if d2 < 5.0:
        h -= (1 - d2 / 5.0) * 0.45 * (0.6 + 0.4 * _n(x * 2.5, y * 2.5, 5.0))
    # the Maw crater (r6)
    d6 = math.hypot(x - 36.0, (y - 15.5) * 1.1)
    if d6 < 5.0:
        h = max(h, 0.6 * min(1.0, (5.0 - d6) / 1.0))
    h += 1.6 * math.exp(-((d6 - 3.0) ** 2) / 1.2) - (0.45 if d6 < 2.4 else 0.0) * (1 - d6 / 2.4)
    # ember waste mesas (r5)
    d5 = math.hypot(x - 31.0, y - 6.5)
    if d5 < 5.0:
        h += 0.35 * max(0.0, _n(x * 1.2, y * 1.2, 7.0)) * (1 - d5 / 5.0)
    return h


def project(x, y, z):
    t = math.radians(TILT)
    sy = (y - CAM_T[1]) * math.cos(t) + (z - CAM_T[2]) * math.sin(t)
    u = 0.5 + (x - CAM_T[0]) / ORTHO
    v = 0.5 - sy / (ORTHO * MAP_H / MAP_W)
    return u, v


def markers():
    out = []
    for rid, name, (x, y), _ in REGIONS:
        u, v = project(x, y, max(height(x, y), 0.05) + 0.3)
        out.append({"id": rid, "x": round(u, 4), "y": round(v, 4)})
    return out


def road_curve(n=24):
    """Catmull-Rom through ROAD; returns dense (x, y) list."""
    P = [ROAD[0]] + ROAD + [ROAD[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(ROAD[-1])
    return out
