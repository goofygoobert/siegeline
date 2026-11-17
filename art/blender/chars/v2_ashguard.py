from kit import *
# Hatchguard (v2) — burly deckhand behind a ship's hatch door, short cutlass, red bandana, big brown beard.
# Silhouette hook: the door-sized square shield in front, bandana tails behind.

def hatchguard_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("hg%d" % t, INK_CREW, h=1.95)
    C = dict(skin=V2["skin"], body=V2["canvas"], sleeve=V2["canvas"], arm=V2["skin"], legs=V2["navy"], belt=V2["red"],
             boots=V2["tar"], cuff=V2["leather"], nose=(0.86, 0.52, 0.42))
    if t >= 2:
        C.update(body=V2["leather"], sleeve=V2["canvas"])
    P = dict(hip=0.66, chest_h=0.72, wy=0.40, wx=0.30, shoulder=0.47, head_r=0.31, belly=1.10, arm_r=0.135, upper_arm=0.30,
             lower_arm=0.30, leg_r=0.155, thigh=0.27, shin=0.25, hip_w=0.19, lean=5, neck_x=0.04)
    body(fig, P, C); fists(fig, C, 0.15); boots(fig, C); head_crew(fig, C, beard=V2["hair"], nose=1.2, jaw=1.12, brow=(0.26, 0.15, 0.09))
    hc = fig.head_c; r = fig.head_r; hip = fig.hip
    # bandana: cap, knot, two tails that trail
    fig.add(loft([(hc.z + r * 0.46, r * 1.05, r * 1.05, 0.0), (hc.z + r * 0.66, r * 1.0, r * 1.02, -0.01), (hc.z + r * 0.86, r * 0.68, r * 0.72, -0.03)],
                 seg=14, at=(hc.x, 0, 0), round_=(False, True), name="bandana"), "head", V2["red"])
    fig.add(loft([(hc.z + r * 0.40, r * 1.08, r * 1.08), (hc.z + r * 0.54, r * 1.08, r * 1.08)], seg=14, at=(hc.x, 0, 0), round_=(False, False),
                 name="band"), "head", (0.62, 0.17, 0.14))
    for (dx, dy, dz) in ((0.5, -0.66, 0.72), (0.05, -0.80, 0.78), (-0.45, -0.66, 0.74), (0.2, -0.42, 0.98), (-0.2, -0.3, 1.0)):
        fig.add(orb(r * 0.085, (hc.x + r * dx, r * dy, hc.z + r * dz), seg=6, name="dot"), "head", V2["white"], glow=0.6, line=0)
    kn = (hc.x - r * 1.03, 0.0, hc.z + r * 0.46)
    fig.add(orb(r * 0.2, kn, name="knot", seg=8), "head", V2["red"], line=0.014)
    chain(fig, "tailA", "head", kn, [0.17, 0.15], 0.065, V2["red"], (-1, 0, -0.45), sway=1.0)
    chain(fig, "tailB", "head", kn, [0.14, 0.12], 0.055, (0.62, 0.17, 0.14), (-1, 0, -0.95), sway=0.8, phase=0.3)
    # sash tails on the near hip, brass buckle
    chain(fig, "sash", "hips", (-0.06, -0.37, hip + 0.06), [0.17, 0.15], 0.07, V2["red"], (-0.25, -0.1, -1), sway=0.6, phase=0.5)
    fig.add(block((0.06, 0.15, 0.13), (0.31, 0, hip + 0.09), bevel=0.02, name="buckle"), "hips", V2["brass"], metal=True, line=0.012)
    if t >= 2:   # iron shoulder guard on the near shoulder
        fig.add(orb(0.19, (0.0, -0.48, fig.sh_z + 0.03), (1.1, 1.0, 0.8), seg=10, name="pauldron"), "uaR", V2["brass"] if t >= 3 else V2["iron"], metal=True)
    # hatch door shield, carried in front of the body on its own pivot
    S = Vector((0.52, -0.02, 0.86))
    fig.joint("shield", S, "chest", 1)
    woods = (V2["wood"], V2["wood_dk"], (0.47, 0.32, 0.19), V2["wood"])
    for i, w in enumerate(woods):
        y = (i - 1.5) * 0.185
        hgt = 0.94 - (0.05 if i in (0, 3) else 0.0)
        ob = block((0.075, 0.178, hgt), (S.x, S.y + y, S.z), bevel=0.02, name="plank")
        fig.add(turn(ob, -24, "Z", S), "shield", w)
    band = V2["brass"] if t >= 3 else V2["iron"]
    for z in (-0.29, 0.29):
        fig.add(turn(block((0.03, 0.76, 0.10), (S.x + 0.045, S.y, S.z + z), bevel=0.01, name="strap"), -24, "Z", S), "shield", band, metal=True, line=0.012)
        for y in (-0.3, -0.1, 0.1, 0.3):
            fig.add(turn(orb(0.028, (S.x + 0.07, S.y + y, S.z + z), seg=6, name="rivet"), -24, "Z", S), "shield", V2["steel"], metal=True, line=0)
    fig.add(turn(orb(0.09, (S.x + 0.06, S.y, S.z), (0.5, 1, 1), seg=10, name="boss"), -24, "Z", S), "shield", band, metal=True, line=0.012)
    if t >= 2:
        for z in (-0.47, 0.47):
            fig.add(turn(block((0.04, 0.78, 0.05), (S.x + 0.03, S.y, S.z + z), bevel=0.01, name="rim"), -24, "Z", S), "shield", band, metal=True, line=0.01)
    # short cutlass in the near hand: built pointing forward with the arm hanging
    h = fig.W["handR"]; g = Vector((h.x + 0.02, h.y - 0.02, h.z - 0.09))
    blade = [(0.07, -0.04), (0.46, -0.075), (0.70, -0.01), (0.80, 0.15), (0.64, 0.09), (0.44, 0.055), (0.07, 0.05)]
    bc = V2["cursed"] if t >= 3 else V2["steel"]
    fig.add(slab(blade, 0.035, at=g, bevel=0.01, name="blade"), "handR", bc, metal=True, glow=0.35 if t >= 3 else 0.0, line=0.016)
    fig.add(loft([(-0.14, 0.035, 0.035), (0.05, 0.04, 0.04)], seg=7, axis="x", at=g, name="grip"), "handR", V2["leather"], line=0.012)
    fig.add(orb(0.085, (g.x + 0.07, g.y, g.z), (0.45, 1.0, 1.25), seg=8, name="guard"), "handR", V2["brass"], metal=True, line=0.012)
    # swipe arc shown on the strike frames
    toggle(fig, "swipe", "root", (0.2, -0.3, 1.0), 0)
    arc = []; inner = []
    for i in range(11):
        a = math.radians(128 - i * 13); k = math.sin(math.pi * i / 10)
        arc.append((0.22 + 1.02 * math.cos(a), 1.12 + 1.02 * math.sin(a)))
        inner.append((0.22 + 1.02 * (1 - 0.24 * k) * math.cos(a), 1.12 + 1.02 * (1 - 0.24 * k) * math.sin(a)))
    fig.add(slab(arc + inner[::-1][1:-1], 0.02, at=(0, -0.42, 0), name="swipe"), "swipe", (1.0, 0.96, 0.84), glow=1.0)
    return fig


def _hg_guard(k=0.0):
    return dict(chest=3, head=-2, uaR=-38, laR=96, handR=4, uaL=42, laL=52, thL=13, snL=-20, thR=-11, snR=-14, brow=0, shield=0)


def hg_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _hg_guard()
    d.update(chest=3 + 1.6 * s, head=-2 - 1.2 * s, laR=96 + 5 * c, uaR=-38 + 2 * s, squash=(1 - 0.008 * s, 1 + 0.014 * s),
             shield=1.5 * c, tail=(4, t))
    return d


def hg_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _hg_guard()
    d.update(thL=26 * s, snL=-8 - 40 * max(0, c), thR=-26 * s, snR=-8 - 40 * max(0, -c), chest=9 + 2.5 * math.cos(2 * p),
             head=-6 - 2 * math.cos(2 * p), uaR=-34 - 9 * s, laR=92 + 6 * c, uaL=44 + 4 * s, shield=-3 + 3 * math.cos(2 * p),
             off=dict(shield=(0, 0, 0.02 * math.cos(2 * p + 0.8))), root=(0, 0.018 * math.cos(2 * p)), tail=(26, t * 2))
    return d


def hg_attack(t, i, n):
    G = _hg_guard()
    wind = dict(G, chest=-13, hips=-4, head=6, uaR=205, laR=-28, handR=-34, shield=-6, off=dict(shield=(-0.06, 0, 0.03)),
                thL=20, snL=-26, thR=-18, snR=-10, root=(-0.07, 0), squash=(1.03, 0.97), brow=-12, vis=dict(m_open=1, m_shut=0), tail=(-18, 0.2))
    hit = dict(G, chest=24, hips=7, head=-12, uaR=78, laR=14, handR=-112, shield=-22, off=dict(shield=(-0.10, 0, -0.10)),
               thL=34, snL=-30, thR=-30, snR=-4, root=(0.20, 0), squash=(0.97, 1.03), brow=-16,
               vis=dict(m_open=1, m_shut=0, swipe=1), tail=(40, 0.5))
    hold = dict(hit, uaR=58, laR=10, handR=-124, chest=27, vis=dict(m_open=1, m_shut=0, swipe=0), root=(0.22, 0), tail=(10, 0.7))
    return keys([(0.0, G), (0.30, wind), (0.42, wind), (0.56, hit), (0.72, hold), (1.0, dict(G, tail=(0, 1.0)))], t)


def hg_hit(t, i, n):
    G = _hg_guard()
    back = dict(G, chest=-19, head=-16, hips=-5, root=(-0.10, 0), squash=(1.06, 0.93), uaR=-70, laR=70, shield=9, brow=14,
                vis=dict(m_open=1, m_shut=0), tail=(-30, 0.2))
    return keys([(0.0, back), (0.45, dict(G, chest=-6, root=(-0.05, 0))), (1.0, G)], t)


def hg_die(t, i, n):
    G = _hg_guard()
    reel = dict(G, chest=-22, head=-20, hips=-8, root=(-0.10, 0), uaR=-120, laR=30, uaL=-40, laL=20, brow=16, vis=dict(m_open=1, m_shut=0),
                shield=10, tail=(-30, 0.2))
    fall = dict(reel, rootrot=-62, root=(-0.22, 0.10), free=1, thL=30, snL=-50, thR=10, snR=-30, uaR=-150, uaL=-100, shield=24, off=dict(shield=(-0.1, 0, 0.0)))
    down = dict(fall, rootrot=-90, root=(-0.34, 0.24), chest=-4, head=-8, thL=14, snL=-20, thR=2, snR=-6, uaR=-165, laR=10, uaL=-140, laL=10,
                shield=30, off=dict(shield=(-0.16, 0, -0.05)), vis=dict(m_open=0, m_shut=1), brow=0, tail=(0, 0.5))
    bounce = dict(down, root=(-0.34, 0.30), rootrot=-86)
    return keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, down), (1.0, down)], t)


def _hg(t):
    register(dict(id="ashguard" + ("" if t == 1 else "_t%d" % t), tier=t, v2=hatchguard_fig,
                  anims=dict(idle=hg_idle, walk=hg_walk, attack=hg_attack, hit=hg_hit, die=hg_die)))


for _t in (1, 2, 3):
    _hg(_t)
