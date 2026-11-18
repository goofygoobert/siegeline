from kit import *
# Bellback (v2) — a man-sized hermit crab living in a drowned, green-crusted bronze ship's bell. It carries the bell
# tipped forward in front of it like a ram and shield: crown and hanging loop to the front, the open mouth to the back
# where the crab sits. Glowing eyes on stalks peer over the rim, one big pale claw grips the bell's near flank, the
# other hooks over its top; six legs splay out behind. Silhouette hook: the big bell shape in front.
# Attack: rears the bell back, then rams it forward. Die: the bell tips over onto the sand and stays there; the crab
# slumps out of it and sinks into an ink puddle.

BB_C = Vector((0.30, 0, 0.82))      # bell axis centre
BB_TILT = -14                       # crown tipped up
BB_AZ = (-75, -112, -148, 75, 112, 148)
BB_PROF = [(-0.58, 0.66), (-0.52, 0.625), (-0.44, 0.53), (-0.32, 0.455), (-0.13, 0.41), (0.10, 0.39), (0.32, 0.385), (0.46, 0.36), (0.54, 0.30),
           (0.58, 0.20)]


def bb_r(u):
    for (u0, r0), (u1, r1) in zip(BB_PROF, BB_PROF[1:]):
        if u <= u1:
            return r0 + (r1 - r0) * (u - u0) / (u1 - u0)
    return BB_PROF[-1][1]


def bb_t(ob):
    return turn(ob, BB_TILT, "Y", BB_C)


def bb_surf(u, ang, k=1.0):
    """Point on the bell surface (rest, untilted): u along the axis, ang around it (0 = top, 90 = near side)."""
    r = bb_r(u) * k; a = math.radians(ang)
    return BB_C + Vector((u, -r * math.sin(a), r * math.cos(a)))


def bb_tilted(p):
    return BB_C + Matrix.Rotation(math.radians(BB_TILT), 3, "Y") @ (Vector(p) - BB_C)


def bb_star(n, r0, r1, cx, cz):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + 0.3; r = r0 if i % 2 == 0 else r1
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def bellback_fig(spec):
    fig = Fig("bb", INK_DEEP, h=1.5, line=0.024)
    fig.rim = 2.0
    BR = (0.66, 0.47, 0.24); BRD = (0.44, 0.30, 0.16); VG = (0.44, 0.72, 0.60); VGD = (0.28, 0.52, 0.46)
    CR = (0.32, 0.50, 0.52); CRD = (0.18, 0.32, 0.36); CLAW = V2["bone"]; CLAWD = (0.55, 0.50, 0.44); SOFT = (0.72, 0.64, 0.56)
    D = (0.05, 0.09, 0.10)
    fig.joint("body", (-0.10, 0, 0.60), "root", 1)
    fig.joint("bell", (-0.25, 0, 0.75), "body", 1)
    fig.head_c = Vector((-0.2, 0, 1.3))
    # ---- the bell: lofted body, flared lip, inner dark, crown boss and hanging loop, raised bands, verdigris crust
    fig.add(bb_t(loft([(u, r, r) for u, r in BB_PROF], seg=20, axis="x", at=tuple(BB_C), name="bell", round_=(False, True))), "bell", BR, metal=True)
    fig.add(bb_t(loft([(-0.63, 0.68, 0.68), (-0.53, 0.665, 0.665)], seg=20, axis="x", at=tuple(BB_C), name="lip", round_=(False, False))),
            "bell", BRD)
    fig.add(bb_t(orb(0.58, tuple(BB_C + Vector((-0.635, 0, 0))), (0.05, 1, 1), seg=16, name="inside")), "bell", D, glow=0.9, line=0)
    for u in (-0.20, -0.12, 0.30):
        fig.add(bb_t(loft([(u, bb_r(u) + 0.025, bb_r(u) + 0.025), (u + 0.045, bb_r(u + 0.045) + 0.025, bb_r(u + 0.045) + 0.025)], seg=20, axis="x",
                          at=tuple(BB_C), name="band", round_=(False, False))), "bell", BRD, line=0.010)
    crown = BB_C + Vector((0.62, 0, 0))
    fig.add(bb_t(cone(crown - Vector((0.04, 0, 0)), crown + Vector((0.16, 0, 0)), 0.17, 0.11, seg=10, name="boss")), "bell", BRD)
    lc = crown + Vector((0.27, 0, 0))
    for k in range(12):
        a = 2 * math.pi * k / 12
        fig.add(bb_t(orb(0.045, tuple(lc + Vector((0.10 * math.cos(a), 0, 0.10 * math.sin(a)))), seg=7, name="loop")), "bell", VGD, line=0.012)
    # verdigris crust: raised pale-green patches, mostly on the near side and top
    for (u, ang, s) in ((-0.40, 120, 0.11), (-0.28, 150, 0.10), (-0.05, 135, 0.09), (0.25, 150, 0.08), (0.42, 40, 0.07), (-0.36, 60, 0.08)):
        p = bb_surf(u, ang, 0.96)
        fig.add(bb_t(orb(s, tuple(p), (1.6, 1.0, 1.0), seg=10, name="verd")), "bell", VG if s > 0.085 else VGD, line=0.010)
    # barnacles near the lip and a glowing crack across the near flank
    for (u, ang, s) in ((-0.50, 70, 0.06), (-0.48, 110, 0.05), (-0.46, 20, 0.055), (-0.35, 135, 0.045)):
        b = bb_surf(u, ang, 1.0); o = bb_surf(u, ang, 1.0 + s * 2.2 / bb_r(u))
        fig.add(bb_t(cone(b, o, s, s * 0.55, seg=6, name="barn")), "bell", V2["barn"], line=0.010)
    pts = [bb_surf(0.05, 82, 1.01), bb_surf(0.16, 96, 1.01), bb_surf(0.22, 88, 1.01), bb_surf(0.34, 104, 1.01)]
    for a, b in zip(pts, pts[1:]):
        fig.add(bb_t(cone(a, b, 0.026, 0.02, seg=5, name="crack")), "bell", V2["glow"], glow=1.0)
    for k, (u, ang) in enumerate(((-0.45, 150), (0.05, 160))):
        st = bb_tilted(bb_surf(u, ang, 0.98))
        chain(fig, "kelp%d" % k, "bell", st, [0.14, 0.12], 0.05, V2["kelp_lt"] if k else V2["kelp"], (-0.3, -0.2, -1), flat=0.45, sway=0.8,
              phase=0.3 * k)
    # ram flash at the crown
    tip = bb_tilted(lc + Vector((0.10, 0, 0)))
    toggle(fig, "ram", "bell", tip, 0)
    fig.add(slab(bb_star(7, 0.46, 0.15, tip.x + 0.12, tip.z), 0.02, at=(0, -0.55, 0), name="flash"), "ram", (0.78, 1.0, 0.84), glow=1.0)
    fig.add(slab(bb_star(5, 0.22, 0.08, tip.x + 0.12, tip.z), 0.02, at=(0, -0.57, 0), name="flash2"), "ram", (1.0, 1.0, 0.92), glow=1.0)
    # ---- the crab (shrinks into the puddle when it dies)
    toggle(fig, "crabv", "body", (-0.50, 0, 0.0), 1)
    fig.joint("crab", (-0.40, 0, 0.66), "crabv", 1)
    fig.add(orb(0.31, (-0.46, 0, 0.72), (1.0, 1.08, 0.86), seg=14, name="carapace"), "crab", CR)
    for (x, y, z, s) in ((-0.55, -0.16, 0.88, 0.10), (-0.38, -0.26, 0.86, 0.09), (-0.62, 0.05, 0.92, 0.08)):
        fig.add(orb(s, (x, y, z), (1.2, 1.0, 0.5), seg=8, name="plate"), "crab", CRD, line=0.008)
    fig.add(orb(0.22, (-0.74, 0, 0.62), (1.1, 0.95, 0.9), seg=12, name="abdomen"), "crab", SOFT)
    fig.add(orb(0.13, (-0.86, 0, 0.52), (1.0, 0.9, 0.9), seg=10, name="curl"), "crab", SOFT, line=0.012)
    fig.add(block((0.10, 0.03, 0.03), (-0.72, -0.21, 0.66), rot=(20, "Y"), bevel=0.0, name="glowseam"), "crab", V2["glow"], glow=1.0)
    # eye stalks over the rim
    for k, y in enumerate((-0.15, 0.13)):
        b = Vector((-0.30, y, 0.92)); tp = Vector((-0.16, y * 1.35, 1.50))
        fig.joint("ey%d" % k, b, "crab", 1)
        fig.add(cone(b, tp, 0.055, 0.04, seg=7, name="stalk"), "ey%d" % k, CRD, line=0.014)
        fig.add(orb(0.13, tp + Vector((0.02, 0, 0.03)), seg=10, name="eye"), "ey%d" % k, V2["glow"], glow=1.3)
        fig.add(orb(0.05, tp + Vector((0.12, -0.03, 0.03)), (0.6, 1, 1.4), seg=6, name="pupil"), "ey%d" % k, (0.03, 0.10, 0.08), glow=1.0)
    # six legs splayed out behind and to the sides
    for i, az in enumerate(BB_AZ):
        a = math.radians(az); dx, dy = math.cos(a), math.sin(a)
        hip = Vector((-0.48 + 0.18 * dx, 0.28 * dy, 0.56)); knee = hip + Vector((dx * 0.34, dy * 0.34, 0.26))
        foot = Vector((knee.x + dx * 0.24, knee.y + dy * 0.24, 0.0))
        fig.joint("lh%d" % i, hip, "crab", 1); fig.joint("lk%d" % i, knee, "lh%d" % i, 1)
        fig.add(cone(hip, knee, 0.085, 0.065, seg=6, name="thigh"), "lh%d" % i, CR, line=0.016)
        fig.add(orb(0.075, knee, seg=8, name="knee"), "lk%d" % i, CRD, line=0.014)
        mid = knee.lerp(foot, 0.6)
        fig.add(cone(knee, mid, 0.065, 0.045, seg=6, name="shin"), "lk%d" % i, CR, line=0.016)
        fig.add(cone(mid - (foot - knee) * 0.04, foot, 0.046, 0.0, seg=6, name="toe"), "lk%d" % i, CLAWD, line=0.014)
    # big near claw: reaches round the rim and grips the bell's near flank
    S = Vector((-0.32, -0.34, 0.52)); E = Vector((0.0, -0.62, 0.36))
    fig.joint("cu", S, "crab", 1); fig.joint("cl", E, "cu", 1)
    fig.add(cone(S, E, 0.10, 0.085, seg=7, name="carm"), "cu", CR, line=0.016)
    fig.add(orb(0.10, E, seg=8, name="elbow"), "cl", CRD, line=0.014)
    fig.add(loft([(0.0, 0.11, 0.09), (0.16, 0.20, 0.13), (0.32, 0.18, 0.12)], seg=10, axis="x", at=tuple(E), name="palm", sq=0.2), "cl", CLAW)
    fig.add(cone(E + Vector((0.28, 0, -0.08)), E + Vector((0.64, 0, -0.02)), 0.09, 0.0, seg=6, name="finger"), "cl", CLAW, line=0.016)
    fig.add(cone(E + Vector((0.52, 0, -0.04)), E + Vector((0.64, 0, -0.02)), 0.04, 0.0, seg=6, name="fingertip"), "cl", CLAWD, line=0.012)
    Pj = E + Vector((0.30, 0, 0.09))
    fig.joint("cj", Pj, "cl", 1)
    fig.add(cone(Pj, Pj + Vector((0.32, 0, -0.03)), 0.085, 0.0, seg=6, name="thumb"), "cj", CLAW, line=0.016)
    # far claw hooks over the top of the bell
    S2 = Vector((-0.30, 0.30, 0.92)); E2 = Vector((-0.06, 0.36, 1.40))
    fig.joint("cf", S2, "crab", 1)
    fig.add(cone(S2, E2, 0.085, 0.07, seg=7, name="farm"), "cf", CR, line=0.016)
    fig.add(orb(0.085, E2, seg=8, name="felbow"), "cf", CRD, line=0.014)
    fig.add(loft([(0.0, 0.09, 0.08), (0.14, 0.15, 0.11), (0.26, 0.13, 0.10)], seg=10, axis="x", at=tuple(E2), name="fpalm", sq=0.2), "cf", CLAW)
    fig.add(cone(E2 + Vector((0.22, 0, 0.04)), E2 + Vector((0.50, 0, -0.04)), 0.07, 0.0, seg=6, name="ffinger"), "cf", CLAW, line=0.014)
    fig.add(cone(E2 + Vector((0.22, 0, -0.06)), E2 + Vector((0.46, 0, -0.14)), 0.065, 0.0, seg=6, name="fthumb"), "cf", CLAWD, line=0.014)
    # ink puddle for the death
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.72, (-0.55, 0, 0.012), (1.3, 0.85, 0.045), seg=14, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((-0.10, -0.35, 0.07), (-1.10, -0.15, 0.05), (-0.55, -0.52, 0.05)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "puddle", V2["glow"], glow=1.0)
    return fig


def bb_leg(d, i, lift=0.0, swing=0.0, curl=0.0):
    """lift: hip raises the leg, swing: forward (+) / back, curl: knee folds the shin inward (+)."""
    a = math.radians(BB_AZ[i]); c, s = math.cos(a), math.sin(a)
    side = -1 if s < 0 else 1
    d["lh%d" % i] = (-lift * c, lift * s, -swing * side)
    d["lk%d" % i] = (curl * c, -curl * s, 0.0)


def _bb_base(lift=0.0, curl=0.0):
    d = dict(body=0, bell=0, crab=0, ey0=0, ey1=0, cu=0, cl=0, cj=0, cf=0)
    for i in range(6):
        bb_leg(d, i, lift, 0.0, curl)
    return d


def bb_idle(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _bb_base()
    for k in range(6):
        bb_leg(d, k, 2 * s, 0, -2 * s)
    bb_leg(d, 5, 12 * max(0, math.sin(2 * p)), 6, 0)
    d.update(bell=2 * s, crab=1.5 * c, ey0=8 * s, ey1=-8 * c, cj=-14 * max(0, math.sin(2 * p + 1)), cf=4 * c,
             off=dict(body=(0, 0, 0.012 * s)), tail=(0, t))
    return d


def bb_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p)
    d = _bb_base()
    for k in range(6):
        ph = p + (0 if k in (0, 2, 4) else math.pi)
        bb_leg(d, k, 26 * max(0, math.cos(ph)), 20 * math.sin(ph), -8 * max(0, math.cos(ph)))
    d.update(body=(2 * math.sin(2 * p), 3 * s, 0), bell=3 * math.sin(2 * p - 0.8), crab=2 * math.sin(2 * p), ey0=-6 + 8 * math.sin(2 * p - 1.0),
             ey1=-6 + 8 * math.sin(2 * p - 1.6), cf=5 * s, off=dict(body=(0.02 * s, 0, 0.02 * abs(math.sin(p)))), tail=(-10, t * 2))
    return d


def bb_attack(t, i, n):
    B = _bb_base()
    rear = _bb_base()
    for k in (0, 3):
        bb_leg(rear, k, 18, -10, 0)
    for k in (2, 5):
        bb_leg(rear, k, -6, -12, 10)
    rear.update(body=-5, bell=-20, crab=-6, ey0=-24, ey1=-24, cj=-30, cf=-10, root=(-0.24, 0), tail=(10, 0.2))
    ram = _bb_base()
    for k in (0, 3):
        bb_leg(ram, k, -4, 22, 0)
    for k in (2, 5):
        bb_leg(ram, k, 12, -24, -12)
    ram.update(body=3, bell=10, crab=8, ey0=20, ey1=20, cj=4, cf=6, root=(0.52, 0), squash=(1.04, 0.96), vis=dict(ram=1), tail=(-30, 0.5))
    hold = dict(ram, root=(0.42, 0), bell=6, squash=(1, 1), vis=dict(ram=0), tail=(-10, 0.7))
    return keys([(0.0, B), (0.30, rear), (0.44, rear), (0.56, ram), (0.72, hold), (1.0, B)], t)


def bb_hit(t, i, n):
    B = _bb_base()
    back = _bb_base(lift=-10, curl=-8)
    back.update(body=-4, bell=-12, crab=-10, ey0=-40, ey1=-34, cj=-30, cf=-14, root=(-0.13, 0), squash=(1.05, 0.93), tail=(20, 0.2))
    mid = dict(B, bell=-4, root=(-0.06, 0), ey0=12, ey1=8)
    return keys([(0.0, back), (0.5, mid), (1.0, B)], t)


def bb_die(t, i, n):
    B = _bb_base()
    jolt = _bb_base(lift=14)
    jolt.update(bell=-14, crab=-10, ey0=-34, ey1=-30, cj=-40, root=(-0.06, 0), tail=(20, 0.2))
    tip = _bb_base(lift=-20, curl=20)
    tip.update(bell=(14, -20, 6), off=dict(bell=(0.04, 0, -0.10), crab=(-0.12, 0, -0.10)), crab=-20, ey0=40, ey1=50, cj=-50, cf=-40,
               root=(-0.04, 0), tail=(-20, 0.4))
    slump = _bb_base(lift=-40, curl=60)
    slump.update(bell=(15, -22, 6), off=dict(bell=(0.04, 0, -0.11), crab=(-0.28, 0, -0.30)), crab=-38, ey0=80, ey1=86, cj=-10, cf=-60, cu=20,
                 root=(-0.04, 0), tail=(-30, 0.6))
    pool = dict(slump, off=dict(bell=(0.04, 0, -0.11), crab=(-0.34, 0, -0.42)), crab=-44)
    d = keys([(0.0, B), (0.12, jolt), (0.40, tip), (0.66, slump), (0.90, pool), (1.0, pool)], t)
    d["vis"] = dict(puddle=min(1.0, max(0.0, (t - 0.35) / 0.45)), crabv=1.0 - 0.72 * min(1.0, max(0.0, (t - 0.45) / 0.47)))
    return d


register(dict(id="bellback", facing=-1, v2=bellback_fig, anims=dict(idle=bb_idle, walk=bb_walk, attack=bb_attack, hit=bb_hit, die=bb_die)))
