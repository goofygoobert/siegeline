from kit import *
# Pufferghast (v2) — swollen spiny puffer-fish monster on two stubby legs. Round body covered in bone spikes, pale belly,
# small angry glowing eyes, wide toothy mouth, glowing green cracks, tiny fins. Silhouette hook: spiky ball.
# Attack: swells, then head-butts. Die: swells to bursting, then only scraps and a puddle remain.

PG_R = 0.60
PG_CZ = 0.92


def pg_tab(K, t):
    """Piecewise-linear value from [(time, value)]."""
    if t <= K[0][0]:
        return K[0][1]
    for (t0, a), (t1, b) in zip(K, K[1:]):
        if t <= t1:
            return a + (b - a) * (t - t0) / max(t1 - t0, 1e-6)
    return K[-1][1]


def pg_dir(az, el):
    a = math.radians(az); e = math.radians(el)
    return Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))


def pg_surf(az, el, k=1.0):
    d = pg_dir(az, el)
    return Vector((d.x * PG_R * k, d.y * PG_R * 0.96 * k, PG_CZ + d.z * PG_R * 0.97 * k))


def pg_crack(fig, joint, pts, r=0.030):
    for a, b in zip(pts, pts[1:]):
        fig.add(cone(pg_surf(a[0], a[1], 1.012), pg_surf(b[0], b[1], 1.012), r, r * 0.7, seg=5, name="crack"), joint, V2["glow"], glow=1.0)


def pg_star(n, r0, r1, cx, cz):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + 0.2; r = r0 if i % 2 == 0 else r1
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def pufferghast_fig(spec):
    fig = Fig("pg", INK_DEEP, h=1.7, line=0.024)
    BODY = (0.36, 0.60, 0.55); BACK = (0.24, 0.44, 0.46); D = (0.15, 0.30, 0.34); PALE = (0.80, 0.82, 0.66); FIN = (0.52, 0.74, 0.62)
    BONE = V2["bone"]; R = PG_R; cz = PG_CZ
    fig.joint("torso", (0, 0, 0.42), "root", 1)
    toggle(fig, "puff", "torso", (0, 0, 0.50), 1)
    toggle(fig, "legs", "root", (0, 0, 0), 1)
    fig.head_c = Vector((0.2, 0, cz + 0.1))
    # body: round ball, darker saddle on the back, pale belly pushing out low at the front
    fig.add(orb(R, (0, 0, cz), (1.0, 0.96, 0.97), seg=16, name="ball"), "puff", BODY)
    fig.add(orb(R * 0.80, (-0.17, 0, cz + 0.15), (1.0, 0.96, 0.95), seg=12, name="saddle"), "puff", BACK, line=0)
    fig.add(orb(R * 0.90, (0.09, 0, cz - 0.11), (1.0, 0.95, 0.95), seg=14, name="belly"), "puff", PALE, line=0)
    # bone spikes over the whole ball except the face and the underside
    N = 54; ga = math.pi * (3 - math.sqrt(5))
    for k in range(N):
        z = 1 - 2 * (k + 0.5) / N; rr = math.sqrt(1 - z * z); a = ga * k
        u = Vector((rr * math.cos(a), rr * math.sin(a), z))
        if u.z < -0.62:
            continue
        if u.x > 0.50 and abs(u.y) < 0.62 and -0.60 < u.z < 0.50:
            continue
        ln = 0.26 + 0.07 * math.sin(k * 2.3)
        b = Vector((u.x * R * 0.93, u.y * R * 0.90, cz + u.z * R * 0.92)); tp = Vector((u.x * R * (1 + ln / R), u.y * R * (1 + ln / R), cz + u.z * R * (1 + ln / R)))
        fig.add(cone(b, tp, 0.078, 0.0, seg=6, name="spike"), "puff", BONE, line=0.016)
    # face: small angry glowing eyes under slanted lids, wide mouth with teeth
    for y in (-1, 1):
        e = pg_surf(y * 27, 15, 0.99)
        fig.add(orb(0.125, e, (0.6, 1.0, 0.95), seg=10, name="eye"), "puff", V2["glow"], glow=1.3)
        fig.add(orb(0.036, e + Vector((0.055, y * 0.02, -0.01)), (0.5, 1, 1.3), seg=6, name="pupil"), "puff", (0.03, 0.10, 0.08), glow=1.0)
        fig.add(turn(block((0.16, 0.30, 0.07), tuple(e + Vector((0.04, 0, 0.125))), rot=(y * 26, "X"), bevel=0.02, name="lid"), y * 27, "Z", tuple(e)),
                "puff", D, line=0.010)
    m = pg_surf(0, -20, 0.93)
    fig.add(orb(0.28, m, (0.50, 1.40, 0.40), seg=12, name="mouth"), "puff", (0.09, 0.05, 0.11), glow=0.92, line=0.014)
    fig.add(orb(0.13, m + Vector((0.07, 0, -0.01)), (0.5, 1.9, 0.42), seg=8, name="throat"), "puff", V2["glow"], glow=1.0)
    for i, y in enumerate((-0.29, -0.17, -0.055, 0.055, 0.17, 0.29)):
        xo = 0.105 - abs(y) * 0.20
        fig.add(cone(m + Vector((xo, y, 0.105 - abs(y) * 0.09)), m + Vector((xo + 0.03, y, 0.0)), 0.040, 0.0, seg=5, name="tooth"), "puff", BONE, line=0.010)
    for i, y in enumerate((-0.23, -0.11, 0.0, 0.11, 0.23)):
        xo = 0.10 - abs(y) * 0.20
        fig.add(cone(m + Vector((xo, y, -0.105 + abs(y) * 0.09)), m + Vector((xo + 0.03, y, -0.02)), 0.036, 0.0, seg=5, name="tooth"), "puff", BONE, line=0.010)
    # glowing cracks, mostly on the near side
    pg_crack(fig, "puff", [(-42, 40), (-58, 26), (-50, 10), (-68, -4), (-60, -20), (-74, -34)])
    pg_crack(fig, "puff", [(-58, 26), (-78, 30), (-92, 20)], 0.024)
    pg_crack(fig, "puff", [(-68, -4), (-88, -8), (-98, -22)], 0.024)
    pg_crack(fig, "puff", [(-128, 34), (-118, 16), (-134, 2), (-124, -16)])
    pg_crack(fig, "puff", [(-15, 64), (-50, 58), (-42, 40)], 0.024)
    # extra cracks that open when it is about to burst (vis['hot'])
    toggle(fig, "hot", "puff", (0, 0, cz), 0)
    pg_crack(fig, "hot", [(-30, 30), (-36, 8), (-28, -8)], 0.04)
    pg_crack(fig, "hot", [(-92, 20), (-104, 44), (-96, 62)], 0.04)
    pg_crack(fig, "hot", [(-98, -22), (-112, -6), (-134, 2)], 0.04)
    pg_crack(fig, "hot", [(-74, -34), (-96, -44), (-120, -36)], 0.04)
    pg_crack(fig, "hot", [(-50, 10), (-36, 8)], 0.04)
    # tiny fins: one on the near flank, one far, a tail fin
    for s, y in (("R", -1), ("L", 1)):
        fp = Vector((-0.10, y * R * 0.97, cz - 0.02))
        fig.joint("fin" + s, fp, "puff", 1)
        fig.add(slab([(0.08, -0.04), (-0.20, -0.20), (-0.40, 0.16), (-0.04, 0.10)], 0.035, at=(fp.x, fp.y + y * 0.02, fp.z), yaw=y * -18, name="fin", bevel=0.01),
                "fin" + s, FIN, line=0.016)
    tp = Vector((-R * 0.95, 0, cz + 0.02))
    fig.joint("tailfin", tp, "puff", 1)
    fig.add(slab([(0.06, 0.06), (-0.30, 0.25), (-0.20, 0.0), (-0.30, -0.23), (0.06, -0.06)], 0.035, at=tuple(tp), name="tail", bevel=0.01), "tailfin", FIN,
            line=0.016)
    # stubby legs with clawed webbed feet
    for s, y in (("L", 1), ("R", -1)):
        hy = y * 0.25
        fig.joint("leg" + s, (0, hy, 0.44), "legs", -1)
        fig.joint("ft" + s, (0.0, hy, 0.07), "leg" + s, -1)
        fig.add(loft([(0.50, 0.15, 0.15), (0.26, 0.135, 0.135), (0.08, 0.10, 0.10)], seg=9, at=(0, hy, 0), name="leg", sq=0.2), "leg" + s, D)
    bare_feet(fig, dict(skin=BACK, claw=BONE), length=0.36)
    # head-butt flash
    toggle(fig, "butt", "root", (R + 0.60, -0.45, cz - 0.25), 0)
    fig.add(slab(pg_star(7, 0.50, 0.17, R + 0.60, cz - 0.25), 0.02, at=(0, -0.55, 0), name="flash"), "butt", (0.78, 1.0, 0.84), glow=1.0)
    fig.add(slab(pg_star(5, 0.25, 0.09, R + 0.60, cz - 0.25), 0.02, at=(0, -0.58, 0), name="flash2"), "butt", (1.0, 1.0, 0.92), glow=1.0)
    # what is left after the burst: puddle, bone spikes, skin scraps, one foot
    toggle(fig, "scraps", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.72, (0.0, 0, 0.012), (1.35, 0.85, 0.045), seg=14, name="puddle"), "scraps", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((0.45, -0.25, 0.08), (-0.55, -0.12, 0.06), (0.1, -0.44, 0.05), (-0.2, -0.38, 0.04), (0.75, -0.05, 0.045)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "scraps", V2["glow"], glow=1.0)
    for (x, y, a, ln) in ((0.30, -0.30, 20, 0.30), (-0.42, -0.34, 160, 0.26), (-0.05, -0.50, -70, 0.24), (0.62, -0.20, -15, 0.22), (-0.70, -0.05, 200, 0.24)):
        dx = math.cos(math.radians(a)); dy = math.sin(math.radians(a))
        fig.add(cone((x, y, 0.07), (x + dx * ln, y + dy * ln * 0.5, 0.05 + 0.08 * (ln > 0.25)), 0.07, 0.0, seg=6, name="scrapspike"), "scraps", BONE, line=0.016)
    for (x, y, s, col) in ((0.08, -0.16, 0.20, BODY), (-0.30, -0.10, 0.16, BACK), (0.36, 0.05, 0.15, PALE)):
        fig.add(orb(s, (x, y, 0.06), (1.3, 0.9, 0.36), seg=8, name="scrap"), "scraps", col, line=0.016)
    return fig


def _pg_base():
    return dict(torso=0, legL=0, legR=0, ftL=0, ftR=0, finL=0, finR=0, tailfin=0)


def pg_idle(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _pg_base()
    d.update(torso=(2 * s, 2.5 * c, 0), finR=(0, 0, 22 * math.sin(2 * p)), finL=(0, 0, -22 * math.sin(2 * p)), tailfin=(0, 0, 16 * s),
             off=dict(torso=(0, 0, 0.012 * s)), vis=dict(puff=1.0 + 0.035 * s))
    return d


def pg_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _pg_base()
    # slow heavy waddle: the ball rolls from side to side over each planted foot
    d.update(torso=(5 + 3 * math.cos(2 * p), 11 * s, 7 * s), legL=24 * s, legR=-24 * s, ftL=-24 * s + 14 * max(0, c), ftR=24 * s + 14 * max(0, -c),
             finR=(0, 0, 26 * math.sin(2 * p - 0.6)), finL=(0, 0, -26 * math.sin(2 * p - 0.6)), tailfin=(0, 0, 22 * math.sin(p - 0.8)),
             off=dict(torso=(0.03 * math.sin(p - 0.5), 0, 0.035 * abs(s) - 0.01), legL=(0, 0, 0.075 * max(0, c)), legR=(0, 0, 0.075 * max(0, -c))),
             vis=dict(puff=1.0 + 0.03 * math.cos(2 * p)))
    return d


def pg_attack(t, i, n):
    B = _pg_base()
    swell = dict(B, torso=-17, legL=14, legR=-10, ftL=-14, ftR=10, finR=(0, 0, -30), finL=(0, 0, 30), tailfin=(-25, 0, 0), root=(-0.12, 0),
                 off=dict(torso=(0, 0, 0.03)))
    butt = dict(B, torso=34, legL=30, legR=-30, ftL=-30, ftR=30, finR=(0, 0, 16), finL=(0, 0, -16), tailfin=(30, 0, 0), root=(0.38, 0),
                off=dict(torso=(0.06, 0, -0.02)), vis=dict(butt=1))
    hold = dict(butt, torso=26, vis=dict(butt=0))
    d = keys([(0.0, B), (0.28, swell), (0.42, swell), (0.56, butt), (0.72, hold), (1.0, B)], t)
    v = dict(d.get("vis") or {})
    v["puff"] = pg_tab([(0.0, 1.0), (0.14, 1.12), (0.30, 1.26), (0.44, 1.30), (0.56, 1.16), (0.74, 1.05), (1.0, 1.0)], t)
    d["vis"] = v
    return d


def pg_hit(t, i, n):
    B = _pg_base()
    wob = (13, -10, 6, 0)[min(i, 3)]
    d = dict(B, torso=(pg_tab([(0.0, -18), (0.5, -8), (1.0, 0)], t), wob, 0), root=(pg_tab([(0.0, -0.12), (1.0, 0)], t), 0),
             finR=(0, 0, -34 + 34 * t), finL=(0, 0, 34 - 34 * t), tailfin=(0, 0, wob * 2),
             off=dict(torso=(0, 0, pg_tab([(0.0, -0.05), (1.0, 0)], t))),
             vis=dict(puff=(0.86, 0.92, 0.97, 1.0)[min(i, 3)]))
    return d


def pg_die(t, i, n):
    B = _pg_base()
    k = min(i, 4)
    shake = (0, 7, -8, 9, -6)[k]
    if i <= 4:      # swells to bursting; the game adds the explosion on top of the next frames
        return dict(B, torso=(-4 * k, shake, 0), legL=-6 * k, legR=5 * k, ftL=6 * k, ftR=-5 * k, finR=(0, 0, -12 * k), finL=(0, 0, 12 * k),
                    off=dict(torso=(0, 0, 0.02 * k)), vis=dict(puff=(1.0, 1.14, 1.28, 1.42, 1.55)[k], hot=1 if i >= 2 else 0))
    g = pg_tab([(5, 0.55), (6, 0.82), (7, 0.95), (8, 1.0)], i)
    return dict(B, vis=dict(puff=0, legs=0, scraps=g))


register(dict(id="bloater", facing=-1, v2=pufferghast_fig, anims=dict(idle=pg_idle, walk=pg_walk, attack=pg_attack, hit=pg_hit, die=pg_die)))
