from kit import *
# UI icons (Tales of the Brine) — small rendered objects in the cast's style, built around the origin (cell centre), facing the camera.
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
    """Powder keg: bulging wooden barrel, iron hoops, lit fuse with a spark."""
    W = PAL["wood"]; Wd = (0.33, 0.22, 0.13); I = PAL["iron"]
    attach(cyl(0.36, 0.42, W, (0, 0, 0.18), r2=0.3, seg=20, name="kegtop"), root)
    attach(cyl(0.3, 0.42, W, (0, 0, -0.24), r2=0.36, seg=20, name="kegbot"), root)
    for z, r in ((0.36, 0.33), (-0.03, 0.375), (-0.42, 0.33)):
        attach(cyl(r + 0.015, 0.07, I, (0, 0, z), seg=20, name="hoop"), root)
    for x in (-0.18, 0.0, 0.18):   # stave lines
        attach(box((0.02, 0.02, 0.62), Wd, (x, -0.36 + abs(x) * 0.35, -0.03), name="stave", outline=0.0), root)
    attach(box((0.34, 0.03, 0.16), PAL["canvas"], (0, -0.385, -0.03), name="label", outline=0.008), root)
    for x in (-0.07, 0.07):   # "XX" on the label
        for a in (40, -40):
            attach(box((0.03, 0.02, 0.15), PAL["tar"], (x, -0.405, -0.03), rot=(0, math.radians(a), 0), name="x", outline=0.0), root)
    attach(rod((0.05, -0.05, 0.38), (0.16, -0.05, 0.58), 0.025, PAL["tar"]), root)
    attach(ball(0.13, PAL["lamp"], (0.18, -0.12, 0.62), glow=1.8, outline=0.0, name="spark"), root)
    attach(ball(0.06, (1, 0.97, 0.8), (0.18, -0.2, 0.62), glow=2.0, outline=0.0, name="sparkcore"), root)
    for a in (0, 60, 120, 180, 240, 300):
        ra = math.radians(a)
        attach(spike((0.18, -0.12, 0.62), (math.cos(ra), 0, math.sin(ra)), 0.2, 0.03, PAL["lamp"], glow=1.6, outline=0.0), root)

def i_mark(root, spec):
    """Doubloon: thick gold coin with a raised rim and an anchor stamped in the middle."""
    rot = (math.radians(90), 0, 0); G = PAL["gold"]; Gd = (0.6, 0.42, 0.12)
    attach(cyl(0.6, 0.14, G, rot=rot, seg=28, bevel=0.03, name="coin", glow=0.1), root)
    attach(cyl(0.49, 0.05, Gd, loc=(0, -0.07, 0), rot=rot, seg=28, name="inner", outline=0.0), root)
    for i in range(16):   # milled dots round the rim
        a = i * math.tau / 16
        attach(ball(0.025, (1.0, 0.85, 0.45), (math.cos(a) * 0.545, -0.08, math.sin(a) * 0.545), name="dot", outline=0.0), root)
    A = (1.0, 0.82, 0.38); y = -0.11
    attach(box((0.07, 0.05, 0.56), A, (0, y, -0.02), name="shank", outline=0.01), root)
    attach(box((0.3, 0.05, 0.06), A, (0, y, 0.17), name="stock", outline=0.01), root)
    attach(cyl(0.07, 0.05, A, (0, y, 0.3), rot=rot, seg=14, name="ring", outline=0.01), root)
    for s in (-1, 1):
        attach(rod((0, y, -0.3), (s * 0.2, y, -0.18), 0.035, A, outline=0.01), root)
        attach(spike((s * 0.2, y, -0.18), (s * 0.3, 0, 1), 0.12, 0.05, A, outline=0.01), root)

def i_rally(root, spec):
    """Sea Shanty: red squeezebox with canvas bellows, a brass ship's bell and two glowing notes."""
    R = PAL["sea_red"]
    attach(box((0.16, 0.36, 0.5), R, (-0.3, 0, -0.12), name="endL"), root)
    attach(box((0.16, 0.36, 0.5), R, (0.3, 0, -0.12), name="endR"), root)
    for i in range(5):
        x = -0.2 + i * 0.1
        attach(box((0.085, 0.32, 0.44 - abs(i - 2) * 0.03), PAL["canvas"] if i % 2 == 0 else (0.3, 0.24, 0.2), (x, 0, -0.12), rot=(0, 0, 0), name="pleat", bevel=0.01), root)
    for z in (0.0, -0.12, -0.24):
        attach(ball(0.035, PAL["canvas"], (0.3, -0.19, z), name="key", outline=0.0), root)
    attach(box((0.7, 0.38, 0.05), PAL["gold"], (0, 0, 0.14), name="topbar"), root)
    # bell hanging top-left
    attach(cyl(0.11, 0.24, PAL["gold"], (-0.36, 0, 0.42), r2=0.05, seg=16, name="bell"), root)
    attach(cyl(0.15, 0.05, PAL["gold"], (-0.36, 0, 0.3), seg=16, name="bellrim"), root)
    attach(ball(0.05, PAL["iron"], (-0.36, -0.03, 0.25), name="clapper"), root)
    for (x, z, s) in ((0.12, 0.46, 1.0), (0.42, 0.36, 0.85)):
        attach(ball(0.09 * s, PAL["lamp"], (x, -0.12, z), scale=(1.3, 0.6, 1), glow=1.5, name="notehead", outline=0.012), root)
        attach(box((0.035, 0.04, 0.3 * s), PAL["lamp"], (x + 0.09 * s, -0.12, z + 0.15 * s), glow=1.5, name="stem", outline=0.012), root)
        attach(box((0.14 * s, 0.04, 0.05), PAL["lamp"], (x + 0.15 * s, -0.12, z + 0.28 * s), rot=(0, 0.5, 0), glow=1.5, name="flag", outline=0.012), root)

def i_ember_rain(root, spec):
    """Broadside: black iron cannon on a wooden carriage, firing, with cannonballs flying out."""
    I = (0.36, 0.37, 0.41)
    attach(box((0.62, 0.3, 0.16), PAL["wood"], (-0.12, 0, -0.38), name="carriage"), root)
    for x in (-0.34, 0.1):
        attach(cyl(0.14, 0.08, (0.36, 0.25, 0.15), (x, -0.17, -0.44), rot=(math.radians(90), 0, 0), seg=14, name="wheel"), root)
        attach(ball(0.04, PAL["iron"], (x, -0.22, -0.44), name="hub", outline=0.0), root)
    attach(rod((-0.42, -0.02, -0.28), (0.24, -0.02, 0.08), 0.15, I, r2=0.1, seg=16), root)
    attach(ball(0.15, I, (-0.44, -0.02, -0.29), name="cascabel"), root)
    for f in (0.15, 0.6):
        attach(cyl(0.16 - f * 0.06, 0.05, PAL["gold"], (-0.42 + 0.66 * f, -0.02, -0.28 + 0.36 * f), rot=(0, math.radians(61), 0), seg=16, name="ring"), root)
    attach(cyl(0.12, 0.06, I, (0.25, -0.02, 0.09), rot=(0, math.radians(61), 0), seg=16, name="muzzle"), root)
    attach(ball(0.17, PAL["lamp"], (0.36, -0.05, 0.17), scale=(1.2, 0.6, 1), glow=1.8, outline=0.0, name="flash"), root)
    attach(ball(0.08, (1, 0.97, 0.8), (0.36, -0.12, 0.17), glow=2.0, outline=0.0, name="flashcore"), root)
    for (x, z, s) in ((0.5, 0.45, 0.9), (0.15, 0.55, 0.7)):
        attach(ball(0.12 * s, (0.3, 0.3, 0.33), (x, -0.06, z), seg=12, name="ball"), root)
        attach(rod((x - 0.1 * s, 0.0, z - 0.06 * s), (x - 0.38 * s, 0.0, z - 0.22 * s), 0.08 * s, PAL["lamp"], r2=0.0, glow=1.0, outline=0.0), root)

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
