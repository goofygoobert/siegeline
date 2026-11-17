from kit import *
# UI icons — small rendered objects in the cast's style, built around the origin (cell centre), facing the camera.
B = PAL["brass"]; E = PAL["ember"]; G = PAL["glow"]

def _star_pts(R=0.62, r=0.27, n=5):
    pts = []
    for i in range(n * 2):
        a = math.pi / 2 + i * math.pi / n
        rad = R if i % 2 == 0 else r
        pts.append((math.cos(a) * rad, math.sin(a) * rad - 0.04))
    return pts

def _flame_pts(s=1.0):
    return [(x * s, z * s) for x, z in ((0.0, 0.66), (0.14, 0.32), (0.3, 0.38), (0.36, 0.05), (0.3, -0.28), (0.12, -0.42),
                                        (-0.12, -0.42), (-0.3, -0.28), (-0.36, 0.0), (-0.28, 0.28), (-0.16, 0.16))]

def i_star(root, spec):
    attach(prism(_star_pts(), 0.18, B, glow=0.15), root)
    attach(prism(_star_pts(0.4, 0.18), 0.06, (1.0, 0.84, 0.45), loc=(0, -0.1, 0.0), glow=0.4, outline=0.0), root)

def i_star_empty(root, spec):
    attach(prism(_star_pts(), 0.18, (0.27, 0.25, 0.27)), root)
    attach(prism(_star_pts(0.4, 0.18), 0.06, (0.15, 0.14, 0.16), loc=(0, -0.1, 0.0), outline=0.0), root)

def i_energy(root, spec):
    attach(prism(_flame_pts(1.0), 0.16, E, glow=0.8), root)
    attach(prism(_flame_pts(0.55), 0.06, G, loc=(0, -0.1, -0.12), glow=1.2, outline=0.0), root)
    attach(prism(_flame_pts(0.25), 0.04, (1, 0.95, 0.75), loc=(0, -0.13, -0.24), glow=1.5, outline=0.0), root)

def i_mark(root, spec):
    rot = (math.radians(90), 0, 0)
    attach(cyl(0.6, 0.14, B, rot=rot, seg=28, bevel=0.03, name="coin"), root)
    attach(cyl(0.48, 0.05, (0.66, 0.45, 0.16), loc=(0, -0.08, 0), rot=rot, seg=28, name="inner", outline=0.0), root)
    # ember-lantern emblem
    attach(box((0.32, 0.06, 0.06), PAL["steel_dk"], (0, -0.12, 0.22), name="cap", outline=0.012), root)
    attach(box((0.3, 0.06, 0.06), PAL["steel_dk"], (0, -0.12, -0.2), name="base", outline=0.012), root)
    for x in (-0.13, 0.13):
        attach(box((0.05, 0.06, 0.38), PAL["steel_dk"], (x, -0.12, 0.01), name="bar", outline=0.012), root)
    attach(ball(0.1, E, (0, -0.12, 0.0), scale=(1, 0.5, 1.35), glow=1.8, outline=0.0), root)
    attach(spike((0, -0.12, 0.25), (0, 0, 1), 0.1, 0.06, PAL["steel_dk"], outline=0.012), root)

def i_rally(root, spec):
    attach(cyl(0.2, 0.62, B, (0, 0, 0.08), r2=0.1, seg=20, name="bell"), root)
    attach(cyl(0.32, 0.1, B, (0, 0, -0.24), seg=20, name="rim"), root)
    attach(ball(0.1, PAL["steel_dk"], (0, -0.05, -0.36), name="clapper"), root)
    attach(cyl(0.07, 0.12, PAL["wood"], (0, 0, 0.45), name="handle"), root)
    attach(ball(0.09, PAL["wood"], (0, 0, 0.55), name="knob"), root)
    for s in (-1, 1):   # ring arcs
        for i in range(3):
            a0 = math.radians(-35 + i * 25); a1 = math.radians(-35 + (i + 1) * 25)
            r = 0.58
            attach(rod((s * math.cos(a0) * r, -0.1, math.sin(a0) * r + 0.02), (s * math.cos(a1) * r, -0.1, math.sin(a1) * r + 0.02), 0.035, G, glow=1.2, outline=0.0), root)

def i_ember_rain(root, spec):
    for (x, z, s) in ((-0.28, 0.25, 1.0), (0.22, 0.38, 0.8), (0.12, -0.25, 1.15)):
        attach(ball(0.17 * s, (0.3, 0.2, 0.17), (x, -0.05, z), seg=10, name="stone"), root)
        attach(ball(0.1 * s, E, (x + 0.05 * s, -0.17 * s, z - 0.04 * s), glow=1.6, outline=0.0, name="hot"), root)
        attach(rod((x + 0.04, 0.0, z + 0.14 * s), (x + 0.3 * s, 0.0, z + 0.55 * s), 0.11 * s, E, r2=0.0, glow=1.0, outline=0.0), root)

def i_lock(root, spec):
    attach(box((0.7, 0.24, 0.56), PAL["steel"], (0, 0, -0.18), bevel=0.06, name="lockbody"), root)
    pts = []
    for i in range(9):
        a = math.pi * i / 8
        pts.append(Vector((math.cos(a) * 0.22, 0, 0.1 + math.sin(a) * 0.3)))
    for a, b in zip(pts, pts[1:]):
        attach(rod(a, b, 0.07, PAL["steel_dk"]), root)
    attach(rod((0.22, 0, 0.1), (0.22, 0, -0.02), 0.07, PAL["steel_dk"]), root)
    attach(rod((-0.22, 0, 0.1), (-0.22, 0, -0.02), 0.07, PAL["steel_dk"]), root)
    attach(box((0.74, 0.26, 0.08), B, (0, 0, 0.06), name="band"), root)
    attach(cyl(0.08, 0.1, PAL["dark"], (0, -0.12, -0.12), rot=(math.radians(90), 0, 0), name="keyhole", outline=0.0), root)
    attach(box((0.06, 0.1, 0.14), PAL["dark"], (0, -0.12, -0.24), name="keyslot", outline=0.0), root)

for fn, yaw in ((i_star, 0), (i_star_empty, 0), (i_energy, 0), (i_mark, 12), (i_rally, 15), (i_ember_rain, 0), (i_lock, 15)):
    register(dict(id=fn.__name__, icon=fn, yaw=yaw))
