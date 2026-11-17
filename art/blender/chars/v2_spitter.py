from kit import *
# Inkspitter (v2) — squid-headed creature. Thin hunched body, tall bulb mantle for a head, face tentacles, a pale
# glowing throat sac. Silhouette hook: tall bulb head. Attack: sac swells, head rears, whips forward and spits a glob.

def is_tab(K, t):
    """Piecewise-linear value from [(time, value)]."""
    if t <= K[0][0]:
        return K[0][1]
    for (t0, a), (t1, b) in zip(K, K[1:]):
        if t <= t1:
            return a + (b - a) * (t - t0) / max(t1 - t0, 1e-6)
    return K[-1][1]


def inkspitter_fig(spec):
    fig = Fig("is", INK_DEEP, h=2.05, line=0.024)
    T = (0.36, 0.56, 0.56); D = (0.15, 0.29, 0.35); PALE = (0.80, 0.84, 0.68); PUR = (0.46, 0.30, 0.58); TL = (0.46, 0.66, 0.60)
    C = dict(skin=T, body=(0.30, 0.48, 0.50), sleeve=(0.30, 0.48, 0.50), arm=T, legs=D, boots=D, hand=D, claw=V2["bone"], shin=T)
    P = dict(hip=0.62, chest_h=0.56, wy=0.21, wx=0.17, shoulder=0.26, head_r=0.30, belly=0.78, arm_r=0.062, upper_arm=0.36, lower_arm=0.40,
             leg_r=0.082, thigh=0.29, shin=0.29, hip_w=0.10, lean=22, head_rest=-36, neck_x=0.04, arm_k=dict(R=1.12, L=0.94),
             sh_up=dict(L=0.04), ankle=0.7, chest_x=0.04)
    body(fig, P, C); fists(fig, C, 0.105, claws=True); bare_feet(fig, C, length=0.30)
    n = fig.neck; nx = n.x; nz = n.z
    fig.head_c = Vector((nx, 0, nz + 0.40))
    # mantle: tall bulb, widest above the middle, leaning back toward the tip
    fig.add(loft([(nz - 0.12, 0.16, 0.16, 0.05), (nz + 0.05, 0.25, 0.23, 0.07), (nz + 0.24, 0.27, 0.25, 0.03), (nz + 0.44, 0.38, 0.34, -0.06),
                  (nz + 0.62, 0.45, 0.39, -0.12), (nz + 0.78, 0.36, 0.32, -0.16), (nz + 0.87, 0.18, 0.17, -0.18)], seg=12, at=(nx, 0, 0), name="mantle", sq=0.1), "head", T)
    # ink blotches on the near side and crown
    for (x, y, z, s) in ((-0.10, -0.37, nz + 0.62, 0.10), (0.12, -0.30, nz + 0.46, 0.07), (-0.28, -0.30, nz + 0.76, 0.06), (0.04, -0.27, nz + 0.82, 0.05)):
        fig.add(orb(s, (nx + x, y, z), (1.0, 0.45, 1.25), seg=8, name="blotch"), "head", PUR, line=0)
    # pale fins at the tip (bone-light shape on top of the bulb)
    for y in (-1, 1):
        fig.add(slab([(0.06, -0.12), (-0.44, -0.06), (-0.10, 0.20)], 0.035, at=(nx - 0.44, y * 0.20, nz + 0.72), yaw=y * -22, name="fin", bevel=0.01),
                "head", PALE, line=0.016)
    # eyes: big glow discs low on the mantle with a heavy dark lid
    for y in (-1, 1):
        fig.add(orb(0.125, (nx + 0.23, y * 0.185, nz + 0.16), (0.6, 0.8, 1.0), seg=10, name="eye"), "head", V2["glow"], glow=1.3)
        fig.add(orb(0.045, (nx + 0.30, y * 0.20, nz + 0.15), (0.5, 0.8, 1.5), seg=6, name="pupil"), "head", (0.03, 0.10, 0.08), glow=1.0)
        fig.add(block((0.16, 0.20, 0.06), (nx + 0.25, y * 0.185, nz + 0.275), rot=(-20, "Y"), bevel=0.02, name="lid"), "head", D, line=0.008)
    # siphon mouth
    fig.add(cone((nx + 0.20, 0, nz + 0.0), (nx + 0.42, 0, nz - 0.05), 0.095, 0.075, seg=8, name="siphon"), "head", D, line=0.014)
    fig.add(orb(0.06, (nx + 0.425, 0, nz - 0.05), (0.4, 1, 1), seg=8, name="siphon_in"), "head", (0.80, 0.45, 1.0), glow=1.0)
    # face tentacles hanging in front of the throat
    for i, (y, ln, ph) in enumerate(((-0.17, 0.52, 0.0), (-0.07, 0.62, 0.3), (0.04, 0.56, 0.55), (0.15, 0.48, 0.8))):
        chain(fig, "tent%d" % i, "head", (nx + 0.27, y, nz - 0.07), [ln * 0.40, ln * 0.34, ln * 0.26], 0.062, TL if i % 2 == 0 else PUR,
              (0.38, 0, -1), taper=0.72, flat=0.7, sway=0.8, phase=ph)
    # throat sac: pale glowing bulge between chin and chest (scaled by vis['sac'])
    sc = Vector((nx + 0.10, 0, nz - 0.20))
    toggle(fig, "sac", "head", sc, 1)
    fig.add(orb(0.205, sc, (1.0, 0.98, 1.05), seg=12, name="sac"), "sac", (0.80, 1.0, 0.74), glow=0.55, line=0.018)
    for (x, y, z, s) in ((0.10, -0.14, 0.02, 0.05), (0.02, -0.17, -0.09, 0.04), (0.15, -0.08, -0.08, 0.035)):
        fig.add(orb(s, sc + Vector((x, y, z)), (1, 0.5, 1.3), seg=6, name="vein"), "sac", (0.62, 0.34, 0.85), glow=1.0)
    # the spit: glowing ink glob leaving the mouth
    g = Vector((nx + 0.98, -0.02, nz + 0.08))
    toggle(fig, "glob", "head", g, 0)
    fig.add(orb(0.20, g, (1.25, 1, 1), seg=12, name="glob"), "glob", V2["glow"], glow=1.0)
    fig.add(orb(0.14, g + Vector((0.02, -0.14, 0)), (1.25, 0.5, 1), seg=10, name="globcore"), "glob", (0.60, 0.30, 0.90), glow=1.0)
    for (dx, dz, s) in ((-0.27, 0.03, 0.085), (-0.40, -0.01, 0.06), (0.22, 0.12, 0.05), (0.26, -0.10, 0.04)):
        fig.add(orb(s, g + Vector((dx, 0, dz)), seg=6, name="drop"), "glob", V2["glow"] if dx < 0 else (0.80, 0.50, 1.0), glow=1.0)
    # rags of skin at the waist, small back fin
    hip = fig.hip
    for i, (x, y, ln) in enumerate(((0.14, -0.15, 0.22), (-0.02, -0.21, 0.28), (-0.14, -0.10, 0.24), (0.10, 0.12, 0.22))):
        chain(fig, "rag%d" % i, "hips", (x, y, hip + 0.02), [ln * 0.55, ln * 0.45], 0.06, PUR if i % 2 else (0.26, 0.42, 0.46), (-0.2, 0, -1),
              flat=0.4, taper=0.6, sway=0.7, phase=i * 0.23)
    fig.add(slab([(0.0, 0.0), (-0.20, 0.10), (-0.14, 0.28), (0.02, 0.36)], 0.03, at=(-0.14, 0, hip + 0.16), name="backfin"), "chest", TL, line=0.014)
    # ink puddle for the death
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.62, (0.05, 0, 0.012), (1.25, 0.8, 0.045), seg=14, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((0.3, -0.2, 0.07), (-0.35, -0.1, 0.05), (0.1, -0.34, 0.04)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "puddle", (0.70, 0.42, 0.95) if x > 0.2 else V2["glow"], glow=1.0)
    return fig


def _is_base():
    return dict(chest=0, head=0, uaR=12, laR=22, handR=8, uaL=4, laL=30, thL=14, snL=-28, thR=4, snR=-18)


def is_idle(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _is_base()
    d.update(chest=2.5 * s, head=(4 * c, 0, 3 * s), uaR=12 + 4 * s, laR=22 + 5 * c, uaL=4 - 4 * s, root=(0.012 * s, 0), tail=(4, t),
             vis=dict(sac=1.0 + 0.12 * math.sin(p * 2)))
    return d


def is_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _is_base()
    d.update(thL=10 + 26 * s, snL=-28 - 34 * max(0, c), thR=8 - 26 * s, snR=-22 - 34 * max(0, -c), chest=5 + 4 * math.sin(2 * p - 0.5),
             head=-2 - 8 * math.sin(2 * p - 1.3), uaR=10 - 20 * math.sin(p - 0.3), laR=24 + 10 * math.sin(p - 1.0), uaL=4 + 18 * math.sin(p - 0.3), laL=30,
             root=(0.02 * math.sin(p - 0.4), 0), tail=(20, t * 2), vis=dict(sac=1.0 + 0.08 * math.sin(2 * p)))
    return d


def is_attack(t, i, n):
    B = _is_base()
    rear = dict(B, chest=-24, head=-20, hips=-6, uaR=-34, laR=50, uaL=-40, laL=50, thL=22, snL=-34, thR=6, snR=-16, root=(-0.07, 0),
                squash=(0.97, 1.04), tail=(-30, 0.2))
    whip = dict(B, chest=2, head=30, hips=3, uaR=64, laR=34, handR=-20, uaL=50, laL=40, thL=30, snL=-38, thR=-14, snR=-22, root=(0.18, 0),
                squash=(1.04, 0.96), tail=(52, 0.5))
    hold = dict(whip, chest=2, head=22, uaR=44, uaL=34, tail=(10, 0.7))
    d = keys([(0.0, B), (0.28, rear), (0.42, rear), (0.56, whip), (0.72, hold), (1.0, B)], t)
    sac = is_tab([(0.0, 1.0), (0.12, 1.2), (0.30, 1.55), (0.44, 1.62), (0.50, 1.2), (0.56, 0.62), (0.74, 0.7), (1.0, 1.0)], t)
    d["vis"] = dict(sac=sac, glob=1 if i == 5 else 0)
    return d


def is_hit(t, i, n):
    B = _is_base()
    back = dict(B, chest=-26, head=-34, root=(-0.10, 0), uaR=-30, laR=50, uaL=-40, squash=(1.06, 0.93), tail=(-36, 0.2))
    d = keys([(0.0, back), (0.5, dict(B, chest=-8, head=14, root=(-0.05, 0), tail=(20, 0.5))), (1.0, B)], t)
    d["vis"] = dict(sac=is_tab([(0.0, 0.7), (0.5, 1.15), (1.0, 1.0)], t))
    return d


def is_die(t, i, n):
    B = _is_base()
    jolt = dict(B, chest=-30, head=-36, uaR=-50, laR=40, uaL=-60, root=(-0.08, 0), squash=(0.95, 1.07), tail=(-30, 0.2))
    sag = dict(B, chest=28, head=50, uaR=40, laR=10, uaL=30, thL=50, snL=-100, thR=40, snR=-90, squash=(1.12, 0.72), tail=(14, 0.5))
    melt = dict(sag, chest=55, head=72, thL=70, snL=-130, thR=60, snR=-120, squash=(1.3, 0.34))
    pool = dict(melt, chest=72, head=84, squash=(1.42, 0.13), free=1, root=(0, -0.02))
    d = keys([(0.0, B), (0.16, jolt), (0.45, sag), (0.72, melt), (0.92, pool), (1.0, pool)], t)
    d["vis"] = dict(sac=is_tab([(0.0, 1.0), (0.16, 1.5), (0.40, 0.5), (1.0, 0.3)], t), puddle=is_tab([(0.25, 0.0), (0.45, 0.5), (0.92, 1.0)], t))
    return d


register(dict(id="spitter", facing=-1, v2=inkspitter_fig, anims=dict(idle=is_idle, walk=is_walk, attack=is_attack, hit=is_hit, die=is_die)))
