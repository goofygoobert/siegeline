from kit import *
# Scuttler (v2) — dog-sized crab-thing. Flat wide barnacled shell on six two-segment legs, two glowing eye stalks,
# one big raised bone claw (near side) and one small. Silhouette hook: flat and wide with one raised claw.
# Dies by flipping onto its back, legs curling, sinking into an ink puddle.

SC_AZ = (-52, -98, -146, 52, 98, 146)      # leg directions (deg from +X); 0-2 near side, 3-5 far side
SC_CZ = 0.40


def sc_star(n, r0, r1, cx, cz):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + 0.3; r = r0 if i % 2 == 0 else r1
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def scuttler_fig(spec):
    fig = Fig("sc", INK_DEEP, h=0.95, line=0.020)
    SH = (0.36, 0.60, 0.56); SH2 = (0.22, 0.42, 0.45); LEG = (0.24, 0.44, 0.46); BEL = (0.66, 0.70, 0.58)
    BONE = V2["bone"]; D = (0.12, 0.25, 0.30)
    cz = SC_CZ
    fig.joint("base", (0, 0, cz), "root", 1)
    fig.joint("shell", (0, 0, cz), "base", 1)
    fig.head_c = Vector((0.3, 0, 0.55))
    # shell: flat wide dome over a pale belly plate
    fig.add(loft([(cz - 0.10, 0.36, 0.42), (cz - 0.03, 0.55, 0.63), (cz + 0.06, 0.53, 0.61), (cz + 0.13, 0.40, 0.46), (cz + 0.18, 0.18, 0.21),
                  (cz + 0.195, 0.03, 0.03)], seg=12, name="shell", round_=(False, False), sq=0.12), "shell", SH)
    fig.add(loft([(cz - 0.17, 0.10, 0.12), (cz - 0.15, 0.30, 0.34), (cz - 0.08, 0.42, 0.48)], seg=12, name="belly", round_=(False, False), sq=0.12),
            "shell", BEL)
    # carved plates on the back, darker rim scallops at the rear
    for (x, y, s) in ((0.10, -0.26, 0.15), (-0.16, -0.10, 0.17), (0.12, 0.14, 0.14), (-0.20, 0.26, 0.13)):
        fig.add(orb(s, (x, y, cz + 0.135), (1.2, 1.1, 0.34), seg=8, name="plate"), "shell", SH2, line=0.008)
    # barnacles (pale) clustered toward the back
    for (x, y, z, s) in ((-0.30, -0.22, cz + 0.12, 0.075), (-0.38, 0.00, cz + 0.10, 0.065), (-0.12, -0.36, cz + 0.10, 0.06), (-0.02, 0.10, cz + 0.17, 0.07),
                         (-0.26, 0.24, cz + 0.11, 0.06), (0.16, -0.40, cz + 0.08, 0.05)):
        fig.add(cone((x, y, z - s * 0.4), (x, y, z + s * 1.0), s, s * 0.55, seg=6, name="barn"), "shell", V2["barn"], line=0.012)
        fig.add(orb(s * 0.42, (x, y, z + s * 1.0), (1, 1, 0.5), seg=6), "shell", D, glow=0.8, line=0)
    # glowing cracks on the near flank, glowing mouth slit
    for (x, z, w, r) in ((0.02, cz + 0.02, 0.17, 30), (0.13, cz + 0.05, 0.11, -35), (-0.30, cz + 0.01, 0.13, -25)):
        fig.add(block((w, 0.03, 0.032), (x, -0.60 + abs(x) * 0.12, z), rot=(r, "Y"), bevel=0.0, name="crack"), "shell", V2["glow"], glow=1.0)
    fig.add(block((0.04, 0.26, 0.04), (0.535, 0, cz - 0.045), bevel=0.0, name="mouth"), "shell", V2["glow"], glow=1.0)
    # eye stalks
    for i, y in enumerate((-0.17, 0.17)):
        b = Vector((0.30, y, cz + 0.13)); tp = Vector((0.36, y * 1.25, 0.78))
        fig.joint("ey%d" % i, b, "shell", 1)
        fig.add(cone(b, tp, 0.045, 0.032, seg=6, name="stalk"), "ey%d" % i, SH2, line=0.014)
        fig.add(orb(0.105, tp + Vector((0.02, 0, 0.02)), (1, 1, 1), seg=10, name="eye"), "ey%d" % i, V2["glow"], glow=1.3)
        fig.add(orb(0.04, tp + Vector((0.09, -0.03, 0.02)), (0.6, 1, 1.5), seg=6, name="pupil"), "ey%d" % i, (0.03, 0.10, 0.08), glow=1.0)
    # six legs: hip on the shell edge, knee up and out, foot on the ground
    for i, az in enumerate(SC_AZ):
        a = math.radians(az); dx, dy = math.cos(a), math.sin(a)
        hip = Vector((0.46 * dx, 0.55 * dy, cz - 0.03)); knee = hip + Vector((dx * 0.30, dy * 0.30, 0.17))
        foot = Vector((knee.x + dx * 0.20, knee.y + dy * 0.20, 0.0))
        fig.joint("lh%d" % i, hip, "base", 1); fig.joint("lk%d" % i, knee, "lh%d" % i, 1)
        fig.add(cone(hip, knee, 0.085, 0.062, seg=6, name="thigh"), "lh%d" % i, LEG, line=0.016)
        fig.add(orb(0.075, knee, seg=8, name="knee"), "lk%d" % i, SH2, line=0.014)
        mid = knee.lerp(foot, 0.55)
        fig.add(cone(knee, mid, 0.062, 0.04, seg=6, name="shin"), "lk%d" % i, LEG, line=0.016)
        fig.add(cone(mid - (foot - knee) * 0.04, foot, 0.042, 0.0, seg=6, name="toe"), "lk%d" % i, BONE, line=0.014)
    # big claw, near side: upper arm, then palm + fixed finger, hinged top finger
    S = Vector((0.46, -0.34, cz + 0.02)); E = Vector((0.70, -0.42, 0.60)); ang = -48
    R = Matrix.Rotation(math.radians(ang), 3, "Y")
    fig.joint("cu", S, "shell", 1); fig.joint("cl", E, "cu", 1)
    fig.add(cone(S, E, 0.095, 0.075, seg=7, name="carm"), "cu", LEG, line=0.016)
    fig.add(orb(0.095, E, seg=8, name="elbow"), "cl", SH2, line=0.014)
    fig.add(turn(loft([(0.0, 0.09, 0.08), (0.13, 0.19, 0.13), (0.28, 0.165, 0.115)], seg=10, axis="x", at=tuple(E), name="palm", sq=0.2), ang, "Y", E),
            "cl", BONE)
    fig.add(turn(cone(E + Vector((0.22, 0, -0.085)), E + Vector((0.52, 0, 0.0)), 0.085, 0.0, seg=6, name="finger"), ang, "Y", E), "cl", BONE, line=0.016)
    Pj = E + Vector((0.24, 0, 0.085))
    fig.joint("cj", E + R @ (Pj - E), "cl", 1)
    fig.add(turn(cone(Pj - Vector((0.03, 0, 0)), Pj + Vector((0.17, 0, 0.045)), 0.09, 0.062, seg=6, name="thumb"), ang, "Y", E), "cj", BONE, line=0.016)
    fig.add(turn(cone(Pj + Vector((0.15, 0, 0.04)), E + Vector((0.53, 0, 0.03)), 0.064, 0.0, seg=6, name="thumbtip"), ang, "Y", E), "cj", BONE, line=0.016)
    tip = E + R @ Vector((0.50, 0, 0.0))
    toggle(fig, "snap", "cl", tip, 0)
    fig.add(slab(sc_star(6, 0.40, 0.13, tip.x + 0.04, tip.z), 0.02, at=(0, tip.y - 0.12, 0), name="flash"), "snap", (0.78, 1.0, 0.84), glow=1.0)
    fig.add(slab(sc_star(4, 0.20, 0.07, tip.x + 0.04, tip.z), 0.02, at=(0, tip.y - 0.14, 0), name="flash2"), "snap", (1.0, 1.0, 0.92), glow=1.0)
    # small claw, far side, held low
    S2 = Vector((0.42, 0.34, cz - 0.02)); E2 = Vector((0.66, 0.40, cz + 0.06))
    fig.joint("cs", S2, "shell", 1)
    fig.add(cone(S2, E2, 0.07, 0.055, seg=6, name="sarm"), "cs", LEG, line=0.014)
    fig.add(orb(0.085, E2 + Vector((0.05, 0, 0)), (1.3, 0.9, 1.0), seg=8, name="spalm"), "cs", BONE, line=0.014)
    fig.add(cone(E2 + Vector((0.08, 0, 0.04)), E2 + Vector((0.27, 0, 0.07)), 0.045, 0.0, seg=5), "cs", BONE, line=0.012)
    fig.add(cone(E2 + Vector((0.08, 0, -0.04)), E2 + Vector((0.26, 0, -0.05)), 0.04, 0.0, seg=5), "cs", BONE, line=0.012)
    # ink puddle for the death
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.80, (-0.1, 0, 0.012), (1.3, 0.85, 0.04), seg=14, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((0.62, -0.30, 0.07), (-0.85, -0.2, 0.05), (0.2, -0.56, 0.05), (-0.45, -0.52, 0.04)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "puddle", V2["glow"], glow=1.0)
    return fig


def sc_leg(d, i, lift=0.0, swing=0.0, curl=0.0):
    """lift: hip raises the leg, swing: forward (+) / back, curl: knee folds the shin inward (+)."""
    a = math.radians(SC_AZ[i]); c, s = math.cos(a), math.sin(a)
    side = -1 if s < 0 else 1
    d["lh%d" % i] = (-lift * c, lift * s, -swing * side)
    d["lk%d" % i] = (curl * c, -curl * s, 0.0)


def _sc_base(lift=0.0, curl=0.0):
    d = dict(cj=-24, cu=-10, cl=-6, shell=0, ey0=0, ey1=0, cs=0)
    for i in range(6):
        sc_leg(d, i, lift, 0.0, curl)
    return d


def sc_idle(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _sc_base()
    for k in range(6):
        sc_leg(d, k, 3 * s, 0, -3 * s)
    sc_leg(d, 0, 14 * max(0, math.sin(p * 2)), 6, 0)      # fidget: the near front leg taps
    d.update(shell=(2.5 * s, 2 * c, 0), cu=-10 + 4 * s, cl=-6 + 5 * c, cj=-24 - 16 * max(0, math.sin(p * 2 + 1)), ey0=8 * s, ey1=-8 * c, cs=6 * c,
             off=dict(base=(0, 0, 0.015 * s)))
    return d


def sc_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p)
    d = _sc_base()
    for k in range(6):
        ph = p + (0 if k in (0, 2, 4) else math.pi)
        sc_leg(d, k, 30 * max(0, math.cos(ph)), 24 * math.sin(ph), -10 * max(0, math.cos(ph)))
    d.update(shell=(3 + 2 * math.sin(2 * p), 6 * s, 5 * s), cu=-12 + 6 * math.sin(2 * p - 0.8), cl=-6 + 6 * math.sin(2 * p - 1.4), cj=-24 - 10 * max(0, s),
             ey0=-10 + 8 * math.sin(2 * p - 1.0), ey1=-10 + 8 * math.sin(2 * p - 1.6), cs=8 * s,
             off=dict(base=(0.02 * s, 0, 0.025 * abs(math.sin(p)))))
    return d


def sc_attack(t, i, n):
    B = _sc_base()
    rear = _sc_base()
    for k in (0, 3):
        sc_leg(rear, k, 22, -8, 0)
    for k in (2, 5):
        sc_leg(rear, k, -8, -10, 12)
    rear.update(shell=-16, cu=-46, cl=-26, cj=-58, ey0=-22, ey1=-22, cs=-20, root=(-0.10, 0))
    snap = _sc_base()
    for k in (0, 3):
        sc_leg(snap, k, -6, 20, 0)
    for k in (2, 5):
        sc_leg(snap, k, 14, -22, -14)
    snap.update(shell=10, cu=40, cl=14, cj=8, ey0=24, ey1=24, cs=25, root=(0.30, 0), squash=(1.05, 0.95), vis=dict(snap=1))
    hold = dict(snap, cu=34, cl=10, shell=7, vis=dict(snap=0), squash=(1, 1))
    return keys([(0.0, B), (0.28, rear), (0.42, rear), (0.56, snap), (0.72, hold), (1.0, B)], t)


def sc_hit(t, i, n):
    B = _sc_base()
    back = _sc_base(lift=-12, curl=-10)
    back.update(shell=(-22, 8, 0), cu=-30, cl=-20, cj=-50, ey0=-40, ey1=-34, root=(-0.12, 0), squash=(1.07, 0.9))
    mid = dict(B, shell=(-8, -5, 0), root=(-0.05, 0), ey0=14, ey1=10)
    return keys([(0.0, back), (0.5, mid), (1.0, B)], t)


def sc_die(t, i, n):
    B = _sc_base()
    jolt = _sc_base(lift=18)
    jolt.update(base=-70, cu=30, cj=-60, ey0=-30, ey1=-30, root=(-0.06, 0.34))
    onback = _sc_base(lift=-30, curl=15)
    onback.update(base=-180, cu=95, cl=-10, cj=-50, ey0=75, ey1=75, cs=40, root=(-0.10, -0.20))
    twitch = _sc_base(lift=-48, curl=55)
    twitch.update(base=-184, cu=80, cl=20, cj=-10, ey0=80, ey1=80, cs=50, root=(-0.10, -0.20))
    curl = _sc_base(lift=-40, curl=85)
    curl.update(base=-180, cu=112, cl=40, cj=0, ey0=84, ey1=84, cs=60, root=(-0.10, -0.20 * 0.62), squash=(1.08, 0.62))
    pool = dict(curl, root=(-0.10, -0.20 * 0.15), squash=(1.0, 0.15))
    d = keys([(0.0, B), (0.14, jolt), (0.34, onback), (0.48, twitch), (0.66, curl), (0.90, pool), (1.0, pool)], t)
    d["vis"] = dict(puddle=min(1.0, max(0.0, (t - 0.30) / 0.5)))
    return d


register(dict(id="gnawer", facing=-1, v2=scuttler_fig, anims=dict(idle=sc_idle, walk=sc_walk, attack=sc_attack, hit=sc_hit, die=sc_die)))
