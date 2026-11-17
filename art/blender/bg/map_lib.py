# World map data — PURE PYTHON (no bpy). Bundled into worldmap.py (--lib) and imported by tools/pack_scenery.py.
# Tales of the Brine: an old sea chart (parchment border, painted sea, raised islands) of the six regions.
import math

MAP_W, MAP_H = 2048, 1024
ORTHO = 40.0                 # world units across the image width
TILT = 35.0                  # degrees away from straight-down
CAM_T = (20.0, 11.5, 0.0)    # point at the image centre

# id, name, marker position (x, y), land colour (sRGB)
REGIONS = [
    ("r1", "Saltwick Cove", (7.0, 7.5), (0.55, 0.58, 0.4)),
    ("r2", "The Fogbanks", (12.5, 15.5), (0.58, 0.6, 0.56)),
    ("r3", "The Cutthroat Isles", (18.5, 8.0), (0.5, 0.45, 0.4)),
    ("r4", "Sunken Bell Reef", (24.5, 15.5), (0.9, 0.72, 0.62)),
    ("r5", "Leviathan's Reach", (29.5, 8.0), (0.62, 0.58, 0.42)),
    ("r6", "The Maelstrom", (34.0, 15.0), (0.4, 0.4, 0.42)),
]
# dotted sailing route (Catmull-Rom through these)
ROAD = [(7.0, 7.5), (9.0, 11.0), (12.5, 15.5), (15.0, 13.5), (16.5, 10.0), (18.5, 8.0), (20.8, 10.5), (22.5, 14.0),
        (24.5, 15.5), (26.8, 13.5), (28.0, 10.0), (29.5, 8.0), (31.5, 9.8), (33.0, 12.5), (34.0, 15.0)]
# islands: (cx, cy, rx, ry, height, kind)   kind = region id used for the land colour; "ring" = atoll
ISLANDS = [
    (5.0, 6.2, 3.3, 2.7, 1.1, "r1"), (2.6, 9.4, 1.1, 0.9, 0.6, "r1"),
    (11.2, 17.4, 1.2, 0.95, 0.55, "r2"), (13.9, 17.2, 0.9, 0.75, 0.45, "r2"), (10.4, 14.4, 0.8, 0.7, 0.4, "r2"),
    (12.6, 15.85, 0.7, 0.55, 0.3, "r2"),
    (18.4, 6.7, 1.5, 1.25, 0.9, "r3"), (20.7, 6.4, 1.1, 0.9, 0.8, "r3"), (16.6, 4.9, 0.8, 0.7, 0.7, "r3"), (19.7, 4.3, 0.9, 0.7, 0.7, "r3"),
    (30.2, 6.4, 2.5, 1.15, 0.6, "r5"), (33.4, 5.4, 0.8, 0.6, 0.45, "r5"),
    (36.9, 12.8, 0.7, 0.55, 0.6, "r6"), (36.6, 17.6, 0.8, 0.6, 0.6, "r6"), (31.6, 17.3, 0.6, 0.5, 0.5, "r6"),
]
ATOLL = (24.5, 16.3, 1.9, 0.45, 0.3)     # cx, cy, ring radius, half width, height (r4)
WHIRL = (34.0, 15.0, 2.7)                # r6 whirlpool centre + radius
COMPASS = (3.6, 19.4, 1.7)


def _n(x, y, s):
    return (math.sin(x * 0.9 + s) * math.cos(y * 1.1 - s * 0.7) + 0.5 * math.sin(x * 2.3 + y * 1.7 + s * 2.1)
            + 0.25 * math.sin(x * 4.7 - y * 3.9 + s)) / 1.75


def land(x, y):
    """(height, kind). Height < 0 is sea depth."""
    best, kind = -0.9, None
    for cx, cy, rx, ry, H, k in ISLANDS:
        d = math.hypot((x - cx) / rx, (y - cy) / ry) * (1 + 0.16 * _n(x * 1.4, y * 1.4, cx))
        v = H * (1 - d * d) if d < 1 else -0.9 + 0.9 * math.exp(-(d - 1) * 2.4)
        if v > best:
            best, kind = v, k
    cx, cy, R, w, H = ATOLL
    d = abs(math.hypot(x - cx, (y - cy) * 1.1) - R) / w * (1 + 0.25 * _n(x * 3, y * 3, 2.0))
    v = H * (1 - d * d) if d < 1 else -0.9 + 0.9 * math.exp(-(d - 1) * 1.2)
    if v > best:
        best, kind = v, "r4"
    return best, kind


def height(x, y):
    return land(x, y)[0]


def project(x, y, z):
    t = math.radians(TILT)
    sy = (y - CAM_T[1]) * math.cos(t) + (z - CAM_T[2]) * math.sin(t)
    u = 0.5 + (x - CAM_T[0]) / ORTHO
    v = 0.5 - sy / (ORTHO * MAP_H / MAP_W)
    return u, v


def unproject_y(v, z=0.0):
    """World y on the plane z for image row v (0 top .. 1 bottom)."""
    t = math.radians(TILT)
    sy = (0.5 - v) * ORTHO * MAP_H / MAP_W
    return CAM_T[1] + (sy - (z - CAM_T[2]) * math.sin(t)) / math.cos(t)


def marker_z(x, y):
    return max(height(x, y), 0.0) + 0.3


def markers():
    out = []
    for rid, name, (x, y), _ in REGIONS:
        u, v = project(x, y, marker_z(x, y))
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


if __name__ == "__main__":
    for m in markers():
        print(m)
