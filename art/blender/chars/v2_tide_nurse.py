from kit import *
# Tide Nurse (v2) — a pale glowing jellyfish bell drifting at waist height. Scalloped dome with green glowing canals and
# four glowing crescents (the core seen through the bell), a bright green core hanging under the rim, two small glowing
# eyes at the front, long pale ribbon tendrils and two frilled oral arms. Light-coloured so it reads in the dark Grotto.
# Silhouette hook: the dome bell and the hanging ribbons. Attack: contracts, then a heal pulse (the core flares).
# Die: deflates and sinks to a flat glowing smear on the sand.

TN_Z = 1.10
TN_PROF = [(0.86, 0.50), (0.92, 0.545), (1.05, 0.525), (1.22, 0.445), (1.36, 0.30), (1.44, 0.12)]


def tn_r(z):
    for (z0, r0), (z1, r1) in zip(TN_PROF, TN_PROF[1:]):
        if z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return TN_PROF[-1][1]


def tn_star(n, r0, r1, cx, cz):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + 0.2; r = r0 if i % 2 == 0 else r1
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def tide_nurse_fig(spec):
    fig = Fig("tn", INK_DEEP, h=1.5, line=0.020)
    fig.rim = 1.6
    PALE = (0.86, 0.88, 0.94); PALE2 = (0.72, 0.78, 0.90); FRILL = (0.92, 0.80, 0.90); RIB = (0.80, 0.92, 0.86); GL = (0.55, 1.0, 0.72)
    fig.joint("bell", (0, 0, TN_Z), "root", 1)
    fig.head_c = Vector((0.2, 0, 1.15))
    # dome and its paler underside
    fig.add(loft([(z, r, r) for z, r in TN_PROF], seg=20, name="dome", round_=(False, True)), "bell", PALE, glow=0.30)
    fig.add(orb(0.47, (0, 0, 0.87), (1, 1, 0.22), seg=16, name="under"), "bell", PALE2, glow=0.45, line=0)
    # scalloped rim
    for k in range(14):
        a = 2 * math.pi * k / 14
        fig.add(orb(0.075, (0.53 * math.cos(a), 0.53 * math.sin(a), 0.865), (1, 1, 0.75), seg=8, name="scallop"), "bell", FRILL, glow=0.35, line=0.010)
    # glowing radial canals running down the dome
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8; ca, sa = math.cos(a), math.sin(a)
        pts = [Vector(((tn_r(z) + 0.008) * ca, (tn_r(z) + 0.008) * sa, z)) for z in (1.43, 1.36, 1.26, 1.14, 1.0, 0.90)]
        for p, q in zip(pts, pts[1:]):
            fig.add(cone(p, q, 0.018, 0.018, seg=5, name="canal"), "bell", GL, glow=0.9, line=0)
    # the core seen through the bell: four glowing crescents round the crown, and a bright knot on top
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4; ca, sa = math.cos(a), math.sin(a)
        r = tn_r(1.29)
        fig.add(orb(0.11, (r * ca * 0.97, r * sa * 0.97, 1.29), (1.0, 1.0, 0.65), seg=10, name="crescent"), "bell", V2["glow"], glow=1.1)
    fig.add(orb(0.09, (0, 0, 1.44), (1, 1, 0.7), seg=10, name="crownglow"), "bell", V2["glow"], glow=1.1)
    # eyes at the front of the dome
    for y in (-1, 1):
        a = math.radians(y * 17); r = tn_r(1.00)
        p = Vector((r * math.cos(a), r * math.sin(a), 1.00))
        fig.add(orb(0.075, tuple(p), (0.6, 1, 1.1), seg=10, name="eye"), "bell", V2["glow"], glow=1.3)
        fig.add(orb(0.032, tuple(p + Vector((0.04, -0.01, 0))), (0.6, 1, 1.3), seg=6, name="pupil"), "bell", (0.03, 0.10, 0.08), glow=1.0)
    # the core hanging under the bell
    fig.add(orb(0.19, (0.02, 0, 0.76), (1, 1, 0.9), seg=12, name="core"), "bell", V2["glow"], glow=1.2)
    fig.add(orb(0.11, (0.02, 0, 0.80), seg=10, name="corehi"), "bell", (0.88, 1.0, 0.90), glow=1.2)
    # core charging (wind-up) and flaring (heal pulse)
    toggle(fig, "charge", "bell", (0.02, 0, 0.76), 0)
    fig.add(orb(0.28, (0.02, 0, 0.76), seg=12, name="charge"), "charge", (0.70, 1.0, 0.80), glow=1.2)
    toggle(fig, "flare", "bell", (0.02, 0, 0.80), 0)
    fig.add(orb(0.36, (0.02, 0, 0.70), seg=14, name="flare"), "flare", (0.80, 1.0, 0.86), glow=1.4)
    fig.add(slab(tn_star(8, 0.70, 0.26, 0.02, 0.76), 0.02, at=(0, 0.62, 0), name="burst"), "flare", (0.62, 1.0, 0.74), glow=1.0)
    fig.add(slab(tn_star(6, 0.46, 0.15, 0.10, 0.70), 0.02, at=(0, -0.66, 0), name="burst2"), "flare", (1.0, 1.0, 0.92), glow=1.0)
    # ribbon tendrils from under the rim, trailing back as it drifts
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.2; ca, sa = math.cos(a), math.sin(a)
        st = (0.42 * ca, 0.42 * sa, 0.85)
        col = (PALE, FRILL, RIB)[k % 3]
        chain(fig, "rib%d" % k, "bell", st, [0.22, 0.20, 0.18, 0.12], 0.055, col, (-0.12 + 0.10 * ca, 0.10 * sa, -1), taper=0.90, flat=0.25,
              sway=0.40, phase=k * 0.13, line=0)
    # two frilled oral arms from the centre, glowing faintly
    for k, y in enumerate((-0.09, 0.09)):
        chain(fig, "arm%d" % k, "bell", (0.06, y, 0.70), [0.17, 0.16, 0.14, 0.10], 0.10, RIB, (-0.06, 0, -1), taper=0.82, flat=0.30, sway=0.35,
              phase=0.4 + 0.3 * k, line=0.012)
    # what is left: a flat glowing smear
    toggle(fig, "smear", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.60, (0.0, 0, 0.015), (1.35, 0.85, 0.05), seg=16, name="smear"), "smear", (0.40, 0.62, 0.56), glow=0.8, line=0.02)
    fig.add(orb(0.34, (0.05, -0.05, 0.03), (1.4, 0.8, 0.06), seg=14, name="smearglow"), "smear", V2["glow"], glow=1.0, line=0)
    for (x, y, s) in ((0.55, -0.30, 0.07), (-0.60, -0.15, 0.06), (0.10, -0.48, 0.05), (-0.25, 0.30, 0.05)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "smear", (0.85, 1.0, 0.90), glow=1.0)
    return fig


def tn_pulse(d, sx, sz, lift=0.0, x=0.0):
    """Squash/stretch the whole jelly about its own centre (root squash scales from the ground, so lift it back)."""
    d["squash"] = (sx, sz)
    d["root"] = (x, TN_Z * (1 - sz) + lift)
    return d


def tn_idle(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = dict(bell=3 * c, tail=(-3 + 3 * s, t))
    return tn_pulse(d, 1 - 0.045 * s, 1 + 0.06 * s, 0.04 * math.sin(p - 1.2))


def tn_walk(t, i, n):
    # drifting pulse: each squeeze pushes it forward and up a little, ribbons stream behind
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = dict(bell=10 + 3 * c, tail=(-14 + 6 * s, t))
    return tn_pulse(d, 1 - 0.07 * s, 1 + 0.10 * s, 0.05 * math.sin(p - 1.0), 0.03 * math.sin(p - 0.6))


def tn_attack(t, i, n):
    B = tn_pulse(dict(bell=3, tail=(0, 0.0)), 1, 1)
    tight = tn_pulse(dict(bell=-6, tail=(8, 0.25)), 1.10, 0.84, 0.06, -0.06)
    flare = tn_pulse(dict(bell=4, tail=(-10, 0.5)), 0.94, 1.14, 0.02, 0.04)
    relax = tn_pulse(dict(bell=2, tail=(-6, 0.7)), 1.02, 0.98, 0.0, 0.02)
    d = keys([(0.0, B), (0.30, tight), (0.44, tight), (0.56, flare), (0.74, relax), (1.0, B)], t)
    d["vis"] = dict(charge=(0, 0, 0.5, 0.85, 1.0, 0, 0, 0, 0, 0)[min(i, 9)], flare=(0, 0, 0, 0, 0, 1.0, 0.75, 0.45, 0, 0)[min(i, 9)])
    return d


def tn_hit(t, i, n):
    B = tn_pulse(dict(bell=3, tail=(0, 0.0)), 1, 1)
    back = tn_pulse(dict(bell=-16, tail=(14, 0.2)), 1.10, 0.88, 0.0, -0.13)
    mid = tn_pulse(dict(bell=-6, tail=(10, 0.5)), 0.97, 1.04, 0.0, -0.05)
    return keys([(0.0, back), (0.5, mid), (1.0, B)], t)


def tn_die(t, i, n):
    B = tn_pulse(dict(bell=3, tail=(0, 0.0)), 1, 1)
    jolt = tn_pulse(dict(bell=-12, tail=(24, 0.2)), 0.90, 1.10, 0.0, -0.06)
    sag = dict(bell=6, tail=(-10, 0.4), squash=(1.16, 0.58), root=(-0.04, 0.12))
    sink = dict(bell=4, tail=(-20, 0.6), squash=(1.32, 0.24), root=(-0.04, 0.0))
    flat = dict(bell=0, tail=(-24, 0.7), squash=(1.42, 0.08), root=(-0.04, 0.0))
    d = keys([(0.0, B), (0.14, jolt), (0.42, sag), (0.70, sink), (0.90, flat), (1.0, flat)], t)
    d["vis"] = dict(smear=min(1.0, max(0.0, (t - 0.45) / 0.4)))
    return d


register(dict(id="tide_nurse", facing=-1, v2=tide_nurse_fig, anims=dict(idle=tn_idle, walk=tn_walk, attack=tn_attack, hit=tn_hit, die=tn_die)))
