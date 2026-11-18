from kit import *
# Gallows Gull (v2) — a skeletal sea-bird that flies. Bare bone skull with a long hooked beak and glowing eye sockets,
# exposed ribs, wide ragged wings (torn feather plates on bone struts), a frayed noose of kelp knotted round its neck
# and dangling below. Built in the air (body around z = 1.12, nothing on the ground); the game lifts it higher.
# Silhouette hook: the wide ragged wings and the dangling noose. Attack: rises, then dives and pecks.
# Die: drops onto the sand, crumples into bones and kelp, ink puddle.

GG_Z = 1.12


def gg_star(n, r0, r1, cx, cz):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + 0.25; r = r0 if i % 2 == 0 else r1
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def gg_plate(pts, side, at, depth=0.035, name="wing"):
    """Flat plate lying in the XY plane from outline points (x, out); out runs away from the body on `side` (-1 near, +1 far)."""
    ob = slab([(x, -side * o) for x, o in pts], depth, name=name)
    turn(ob, 90, "X", (0, 0, 0))
    ob.data.transform(Matrix.Translation(Vector(at)))
    return ob


def gallows_gull_fig(spec):
    fig = Fig("gg", INK_DEEP, h=1.4, line=0.022)
    fig.rim = 2.2
    BONE = V2["bone"]; BONE2 = (0.70, 0.66, 0.57)
    F = (0.50, 0.58, 0.58); F2 = (0.33, 0.42, 0.45); TORSO = (0.22, 0.32, 0.36)
    K = (0.56, 0.68, 0.30); K2 = (0.34, 0.48, 0.24)
    Z = GG_Z
    fig.joint("fly", (0, 0, 0), "root", 1)
    fig.joint("body", (0, 0, Z), "fly", 1)
    fig.joint("head", (0.32, 0, Z + 0.14), "body", 1)
    fig.joint("jaw", (0.52, 0, Z + 0.20), "head", 1)
    fig.joint("fan", (-0.26, 0, Z + 0.02), "body", 1)
    fig.joint("legs", (-0.04, 0, Z - 0.10), "body", -1)
    fig.head_c = Vector((0.46, 0, Z + 0.24))
    # torso: dark feathered keel with bare ribs and a bone breastbone
    fig.add(loft([(-0.30, 0.11, 0.11), (-0.10, 0.165, 0.15), (0.10, 0.165, 0.14), (0.24, 0.11, 0.10)], seg=12, axis="x", at=(0, 0, Z),
                 name="torso", sq=0.1), "body", TORSO)
    for x in (-0.14, -0.04, 0.06, 0.15):
        pts = []
        for a in (15, 60, 105, 150, 175):
            r = 0.185 - abs(x) * 0.12
            pts.append(Vector((x - 0.03 * math.sin(math.radians(a)), -r * math.sin(math.radians(a)), Z + r * math.cos(math.radians(a)))))
        for a, b in zip(pts, pts[1:]):
            fig.add(cone(a, b, 0.024, 0.02, seg=5, name="rib"), "body", BONE, line=0.010)
    fig.add(slab([(-0.14, -0.10), (0.20, -0.08), (0.10, -0.24), (-0.06, -0.21)], 0.05, at=(0, 0, Z), name="keel"), "body", BONE2, line=0.012)
    fig.add(cone((-0.30, 0, Z + 0.10), (0.22, 0, Z + 0.12), 0.03, 0.03, seg=6, name="spine"), "body", BONE, line=0.010)
    # neck vertebrae
    for k in range(4):
        u = k / 3.0
        fig.add(orb(0.05, (0.20 + 0.16 * u, 0, Z + 0.06 + 0.15 * u), seg=8, name="vert"), "head", BONE, line=0.010)
    # skull: long bone skull, dark sockets with glowing eyes, heavy brow, hooked beak
    fig.add(orb(0.13, (0.45, 0, Z + 0.25), (1.3, 0.82, 0.92), seg=12, name="skull"), "head", BONE)
    for y in (-1, 1):
        fig.add(orb(0.065, (0.48, y * 0.08, Z + 0.27), (1.0, 0.7, 1.0), seg=8, name="socket"), "head", (0.05, 0.09, 0.10), glow=0.9, line=0)
        fig.add(orb(0.05, (0.49, y * 0.095, Z + 0.27), (0.8, 0.6, 0.9), seg=8, name="eye"), "head", V2["glow"], glow=1.4)
        fig.add(block((0.13, 0.05, 0.035), (0.48, y * 0.09, Z + 0.33), rot=(-18, "Y"), bevel=0.01, name="brow"), "head", F2, line=0.008)
    fig.add(cone((0.53, 0, Z + 0.25), (0.86, 0, Z + 0.17), 0.065, 0.02, seg=8, name="beak"), "head", BONE)
    fig.add(cone((0.83, 0, Z + 0.19), (0.89, 0, Z + 0.10), 0.032, 0.0, seg=6, name="hook"), "head", BONE2, line=0.012)
    fig.add(cone((0.52, 0, Z + 0.20), (0.80, 0, Z + 0.155), 0.045, 0.012, seg=7, name="lowbeak"), "jaw", BONE2)
    # ragged crest of torn feathers on the back of the skull
    for (dx, dz, ln) in ((-0.30, 0.10, 0.20), (-0.36, 0.0, 0.18), (-0.25, 0.18, 0.15)):
        fig.add(cone((0.40, 0, Z + 0.30), (0.40 + dx * 0.7, 0, Z + 0.30 + dz + 0.05), 0.04, 0.0, seg=5, name="crest"), "head", F2, line=0.012)
    # noose: a loop of kelp rope round the neck, a knot, and a long frayed tail hanging below
    nc = Vector((0.27, 0, Z + 0.11)); u1 = Vector((0, 1, 0)); u2 = Vector((-0.66, 0, 0.75))
    for k in range(12):
        a = 2 * math.pi * k / 12
        fig.add(orb(0.052, nc + (u1 * math.cos(a) + u2 * math.sin(a)) * 0.10, seg=7, name="loop"), "body", K, line=0.012)
    knot = Vector((0.30, 0, Z + 0.02))
    fig.add(orb(0.07, knot, (1, 1, 1.2), seg=8, name="knot"), "body", K)
    rope = chain(fig, "noose", "body", knot, [0.18, 0.17, 0.16, 0.14], 0.065, K, (-0.30, 0, -1), taper=0.88, flat=0.7, sway=0.9, phase=0.0, line=0.016)
    end = knot + Vector((-0.30, 0, -1)).normalized() * 0.65
    lc = end + Vector((0.0, 0, -0.07))
    for k in range(9):      # the open hangman's loop at the end of the rope
        a = 2 * math.pi * k / 9
        fig.add(orb(0.038, lc + Vector((0.075 * math.cos(a), 0, 0.075 * math.sin(a))), seg=6, name="eyeloop"), rope[-1], K, line=0.010)
    end = lc + Vector((0, 0, -0.07))
    for k, (dx, ph, c) in enumerate(((-0.6, 0.2, K2), (0.1, 0.4, K), (0.6, 0.6, K2))):
        chain(fig, "fray%d" % k, rope[-1], end, [0.12, 0.10], 0.04, c, (dx, 0, -1), taper=0.7, flat=0.6, sway=1.2, phase=ph, line=0.012)
    chain(fig, "kflag", rope[1], knot + Vector((-0.30, 0, -1)).normalized() * 0.22, [0.12, 0.09], 0.04, K2, (-1, 0, -0.5), taper=0.6, flat=0.5,
          sway=1.0, phase=0.3, line=0.012)
    # tail: a ragged vertical fan
    fig.add(slab([(-0.26, 0.06), (-0.60, 0.16), (-0.54, 0.07), (-0.68, 0.03), (-0.56, -0.02), (-0.64, -0.10), (-0.50, -0.07), (-0.26, -0.05)],
                  0.10, at=(0, 0, Z), name="tailfan"), "fan", F2)
    # legs: bone shanks tucked back, talons
    for y in (-0.07, 0.07):
        a = Vector((-0.02, y, Z - 0.10)); b = Vector((-0.18, y, Z - 0.28)); c = Vector((-0.34, y, Z - 0.34))
        fig.add(cone(a, b, 0.035, 0.025, seg=6, name="thigh"), "legs", BONE2, line=0.012)
        fig.add(cone(b, c, 0.025, 0.02, seg=6, name="shank"), "legs", BONE, line=0.012)
        for dz in (-0.05, 0.0, 0.05):
            fig.add(cone(c, c + Vector((-0.10, 0, dz - 0.04)), 0.018, 0.0, seg=5, name="talon"), "legs", BONE2, line=0.010)
    # wings: torn feather plates on bone struts, inner part on the shoulder, outer part on the wrist
    inner = [(0.12, 0.0), (0.18, 0.25), (0.16, 0.5), (-0.39, 0.5), (-0.546, 0.42), (-0.364, 0.36), (-0.546, 0.26), (-0.338, 0.18), (-0.442, 0.08), (-0.234, 0.0)]
    outer = [(0.16, 0.48), (0.11, 0.7), (0.01, 0.9), (-0.182, 1.07), (-0.312, 0.98), (-0.247, 0.92), (-0.494, 0.86), (-0.351, 0.78), (-0.572, 0.7), (-0.39, 0.63), (-0.546, 0.55), (-0.39, 0.48)]
    for s, side in (("R", -1), ("L", 1)):
        W = Vector((0.06, side * 0.12, Z + 0.08))

        def P(x, o):
            return W + Vector((x, side * o, 0))
        fig.joint("wg" + s, W, "body", 1)
        fig.joint("wt" + s, P(0.15, 0.49), "wg" + s, 1)
        fig.add(gg_plate(inner, side, W, name="wingin"), "wg" + s, F)
        fig.add(gg_plate(outer, side, W, name="wingout"), "wt" + s, F2)
        fig.add(cone(P(0.0, 0.0), P(0.17, 0.25), 0.04, 0.032, seg=6, name="humerus"), "wg" + s, BONE, line=0.012)
        fig.add(cone(P(0.17, 0.25), P(0.15, 0.50), 0.032, 0.028, seg=6, name="ulna"), "wg" + s, BONE, line=0.012)
        fig.add(cone(P(0.10, 0.12), P(-0.30, 0.30), 0.016, 0.006, seg=5, name="quill"), "wg" + s, BONE2, line=0.008)
        fig.add(orb(0.035, P(0.15, 0.49), seg=6, name="wrist"), "wt" + s, BONE, line=0.010)
        for a, b in (((0.15, 0.49), (0.10, 0.71)), ((0.10, 0.71), (0.0, 0.91)), ((0.0, 0.91), (-0.13, 1.05))):
            fig.add(cone(P(*a), P(*b), 0.026, 0.018, seg=5, name="digit"), "wt" + s, BONE, line=0.010)
        for b in ((-0.34, 0.85), (-0.38, 0.66)):
            fig.add(cone(P(0.14, 0.50), P(*b), 0.018, 0.005, seg=5, name="finger"), "wt" + s, BONE2, line=0.008)
    # peck flash at the beak tip
    toggle(fig, "peck", "head", (0.92, 0, Z + 0.14), 0)
    fig.add(slab(gg_star(6, 0.36, 0.12, 0.96, Z + 0.12), 0.02, at=(0, -0.30, 0), name="flash"), "peck", (0.78, 1.0, 0.84), glow=1.0)
    fig.add(slab(gg_star(4, 0.18, 0.06, 0.96, Z + 0.12), 0.02, at=(0, -0.32, 0), name="flash2"), "peck", (1.0, 1.0, 0.92), glow=1.0)
    # what is left on the sand: ink puddle, loose bones, kelp clumps
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.70, (0.05, 0, 0.012), (1.3, 0.8, 0.045), seg=14, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((0.45, -0.25, 0.06), (-0.55, -0.15, 0.05), (0.05, -0.42, 0.045)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "puddle", V2["glow"], glow=1.0)
    toggle(fig, "bones", "root", (0, 0, 0.0), 0)
    for (x, y, a, ln) in ((0.55, -0.30, 20, 0.30), (-0.62, -0.32, 160, 0.26), (-0.10, -0.48, -60, 0.22), (0.30, 0.10, 200, 0.24)):
        dx = math.cos(math.radians(a)); dy = math.sin(math.radians(a))
        p = Vector((x, y, 0.05)); q = p + Vector((dx * ln, dy * ln * 0.5, 0.0))
        fig.add(cone(p, q, 0.03, 0.025, seg=5, name="bone"), "bones", BONE, line=0.012)
        fig.add(orb(0.04, q, seg=6), "bones", BONE, line=0.010)
    for (x, y, s) in ((-0.30, -0.36, 0.13), (0.70, -0.10, 0.10), (-0.80, 0.05, 0.11)):
        fig.add(orb(s, (x, y, 0.04), (1.5, 0.8, 0.30), seg=8, name="kclump"), "bones", K, line=0.012)
    return fig


def gg_wings(d, up, bend, sweep=0.0):
    """up: shoulder raise (deg), bend: wrist raise (deg), sweep: wings swept back (deg)."""
    d["wgR"] = (0, -up, -sweep); d["wgL"] = (0, up, sweep)
    d["wtR"] = (0, -bend, 0); d["wtL"] = (0, bend, 0)
    return d


def _gg_base():
    return gg_wings(dict(body=4, head=0, jaw=0, fan=0, legs=-18), 20, 0, 40)


def gg_idle(t, i, n):
    # a hover: slow deep flaps, the body rides up on each downstroke
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _gg_base()
    gg_wings(d, 22 + 58 * s, 30 * math.sin(p - 1.3), 46 - 14 * s)
    d.update(body=4 + 3 * c, head=-5 * c, jaw=8 * max(0, math.sin(2 * p)), fan=8 * c, legs=-16 + 6 * s, root=(0.0, -0.07 * s), tail=(-22, t))
    return d


def gg_walk(t, i, n):
    # flapping flight: bigger, faster strokes, body pitched into the flight, noose trailing back
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _gg_base()
    gg_wings(d, 24 + 62 * s, 36 * math.sin(p - 1.1), 50 - 16 * s)
    d.update(body=10 + 3 * c, head=-8 + 4 * c, jaw=0, fan=-6 + 8 * c, legs=-26, root=(0.03 * c, -0.09 * s), tail=(-30, t))
    return d


def gg_attack(t, i, n):
    B = gg_idle(0.0, 0, 8)
    rise = gg_wings(dict(body=-24, head=-22, jaw=10, fan=20, legs=30, root=(-0.18, 0.28), tail=(-6, 0.2)), 78, -24, 30)
    hold = gg_wings(dict(rise, body=-28, head=-18, jaw=34, root=(-0.20, 0.32), tail=(-4, 0.3)), 84, -30, 26)
    dive = gg_wings(dict(body=28, head=22, jaw=0, fan=-20, legs=-40, root=(0.58, -0.40), tail=(-70, 0.5), vis=dict(peck=1)), 50, 40, 70)
    after = gg_wings(dict(body=14, head=8, jaw=10, fan=-8, legs=-20, root=(0.40, -0.24), tail=(-40, 0.7)), -30, -10, 46)
    return keys([(0.0, B), (0.28, rise), (0.44, hold), (0.56, dive), (0.74, after), (1.0, B)], t)


def gg_hit(t, i, n):
    B = gg_idle(0.0, 0, 8)
    back = gg_wings(dict(body=-26, head=-30, jaw=30, fan=24, legs=20, root=(-0.16, 0.08), tail=(30, 0.2)), 72, -34, 20)
    mid = gg_wings(dict(body=-8, head=-10, jaw=10, fan=8, legs=-10, root=(-0.07, 0.03), tail=(8, 0.5)), 40, -6, 36)
    return keys([(0.0, back), (0.5, mid), (1.0, B)], t)


def gg_die(t, i, n):
    B = gg_idle(0.0, 0, 8)
    jolt = gg_wings(dict(body=-30, head=-40, jaw=36, fan=26, legs=30, root=(-0.10, 0.10), tail=(20, 0.2)), 82, -34, 24)
    fall = gg_wings(dict(body=(34, 14, 0), head=30, jaw=20, fan=-20, legs=40, root=(-0.12, 0), off=dict(fly=(0, 0, -0.55)), tail=(-60, 0.4)),
                    66, 50, 50)
    land = gg_wings(dict(body=(10, 12, 0), head=26, jaw=24, fan=-10, legs=70, root=(-0.10, 0), off=dict(fly=(0, 0, -1.02)), tail=(-84, 0.5)),
                    -4, -14, 30)
    crumple = dict(land, squash=(1.14, 0.50), head=34, legs=90)
    flat = dict(crumple, squash=(1.24, 0.26))
    d = keys([(0.0, B), (0.12, jolt), (0.34, fall), (0.54, land), (0.78, crumple), (0.94, flat), (1.0, flat)], t)
    d["vis"] = dict(puddle=min(1.0, max(0.0, (t - 0.45) / 0.45)), bones=min(1.0, max(0.0, (t - 0.55) / 0.3)))
    return d


register(dict(id="gallows_gull", facing=-1, v2=gallows_gull_fig, anims=dict(idle=gg_idle, walk=gg_walk, attack=gg_attack, hit=gg_hit, die=gg_die)))
