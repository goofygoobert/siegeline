from kit import *
# Rope Rat (v2) — wiry cabin hand: bare feet, striped shirt, ginger shock of hair, a knife in each hand.
# Silhouette hook: the low forward lean and the two knives. Scampering walk; attack = two quick slashes.

RR_LEAN = 20
RR_GINGER = (0.90, 0.43, 0.12)


def rr_num(d, k):
    v = d.get(k, 0.0)
    return v if isinstance(v, (int, float)) else v[0]


def rr_aim(d, R=None, L=None):
    """Set the wrists so each knife points at a world elevation (deg above +X)."""
    for s, e in (("R", R), ("L", L)):
        if e is not None:
            d["hand" + s] = e + d.get("rootrot", 0) + rr_num(d, "hips") + rr_num(d, "chest") + RR_LEAN - rr_num(d, "ua" + s) - rr_num(d, "la" + s)
    return d


def rr_band(fig, k0, k1, color):
    """A thin painted stripe round the chest between two heights (fractions of chest height)."""
    P = fig.P; hip = fig.hip; ch = P["chest_h"]; wx = P["wx"]; wy = P["wy"]; b = P.get("belly", 1.0); cx = P.get("chest_x", 0.03)
    R = [(hip + 0.10, wx * 0.92 * b, wy * 0.92, 0.0), (hip + ch * 0.38, wx * 1.05 * b, wy * 1.02, cx * 0.5),
         (hip + ch * 0.70, wx * 1.12, wy * 1.18, cx), (hip + ch * 0.93, wx * 0.86, wy * 1.10, cx * 0.6)]

    def at(z):
        for a, c in zip(R, R[1:]):
            if z <= c[0]:
                f = (z - a[0]) / (c[0] - a[0])
                return (z, lerp(a[1], c[1], f) * 1.04 + 0.004, lerp(a[2], c[2], f) * 1.04 + 0.004, lerp(a[3], c[3], f))
        return (z, R[-1][1] * 1.04, R[-1][2] * 1.04, R[-1][3])
    fig.add(loft([at(hip + ch * k0), at(hip + ch * k1)], name="stripe", sq=0.35, round_=(False, False)), "chest", color, line=0)


def rr_arc(cx, cz, R, a0, a1, th=0.26, n=10):
    out = []; inn = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n); k = 1 - th * math.sin(math.pi * i / n)
        out.append((cx + R * math.cos(a), cz + R * math.sin(a))); inn.append((cx + R * k * math.cos(a), cz + R * k * math.sin(a)))
    return out + inn[::-1][1:-1]


def roperat_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("rr%d" % t, INK_CREW, h=1.6, line=0.020)
    skin = (0.90, 0.68, 0.52)
    C = dict(skin=skin, body=V2["canvas"], sleeve=V2["canvas"], arm=skin, legs=V2["navy"], shin=skin, belt=V2["red"], claw=skin,
             nose=(0.88, 0.56, 0.44))
    if t >= 2:
        C.update(legs=V2["leather"])
    P = dict(hip=0.54, chest_h=0.52, wy=0.27, wx=0.20, shoulder=0.32, head_r=0.25, belly=0.9, arm_r=0.085, upper_arm=0.26, lower_arm=0.25,
             leg_r=0.10, thigh=0.23, shin=0.22, hip_w=0.13, lean=RR_LEAN, neck_x=0.03, ankle=0.72)
    body(fig, P, C); fists(fig, C, 0.115); bare_feet(fig, C, length=0.30)
    head_crew(fig, C, nose=0.9, jaw=0.94, brow=(0.50, 0.22, 0.08))
    hc = fig.head_c; r = fig.head_r; hip = fig.hip
    # striped shirt: thin navy bands on chest and sleeves
    for k0, k1 in ((0.30, 0.365), (0.43, 0.50), (0.57, 0.64), (0.73, 0.80), (0.855, 0.915)):
        rr_band(fig, k0, k1, V2["navy"])
    ar = P["arm_r"]
    for s, y in (("L", 1), ("R", -1)):
        for z in (0.10, 0.20):
            fig.add(loft([(fig.sh_z - z, ar * 1.17, ar * 1.17), (fig.sh_z - z - 0.045, ar * 1.14, ar * 1.14)], seg=9, at=(0, y * P["shoulder"], 0),
                         name="sstripe", round_=(False, False)), "ua" + s, V2["navy"], line=0)
    # ginger hair: cap + a shock of spikes swept back
    fig.add(loft([(hc.z + r * 0.44, r * 1.07, r * 1.07), (hc.z + r * 0.72, r * 1.02, r * 1.04, -0.01), (hc.z + r * 0.94, r * 0.72, r * 0.76, -0.03)],
                 seg=12, at=(hc.x, 0, 0), round_=(False, True), name="hair"), "head", RR_GINGER)
    for (dx, dy, dz, lx, lz, s) in ((0.55, 0.0, 0.92, 0.30, 0.42, 0.11), (0.10, -0.45, 1.05, -0.10, 0.50, 0.12), (0.10, 0.45, 1.05, -0.10, 0.50, 0.12),
                                    (-0.40, 0.0, 1.05, -0.40, 0.48, 0.13), (-0.80, -0.30, 0.80, -0.62, 0.22, 0.12), (-0.80, 0.30, 0.80, -0.62, 0.22, 0.12),
                                    (-0.95, 0.0, 0.45, -0.60, -0.05, 0.12)):
        b = Vector((hc.x + r * dx, r * dy, hc.z + r * dz))
        fig.add(cone(b - Vector((lx, 0, lz)) * r * 0.3, b + Vector((lx * r, dy * r * 0.3, lz * r)), s, 0.0, seg=6, name="spike"), "head", RR_GINGER,
                line=0.014)
    # neckerchief and sash tails
    nk = (fig.neck.x - 0.10, 0, fig.neck.z + 0.01)
    fig.add(orb(0.07, nk, seg=7, name="knot"), "chest", V2["red"], line=0.012)
    chain(fig, "ker", "chest", nk, [0.15, 0.13], 0.055, V2["red"], (-1, 0, -0.3), sway=1.0)
    chain(fig, "sash", "hips", (-0.05, -0.27, hip + 0.06), [0.15, 0.13], 0.06, V2["red"], (-0.4, -0.1, -1), sway=0.7, phase=0.4)
    if t >= 2:      # leather bracers + a bandolier strap of rope
        for s, y in (("L", 1), ("R", -1)):
            z = fig.sh_z - P["upper_arm"]
            fig.add(loft([(z - 0.06, ar * 1.22, ar * 1.22), (z - 0.19, ar * 1.12, ar * 1.12)], seg=9, at=(0, y * P["shoulder"], 0), name="bracer",
                         round_=(False, False)), "la" + s, V2["gold"] if t >= 3 else V2["leather"], metal=t >= 3, line=0.012)
    if t >= 3:      # gold earring and buckle
        fig.add(orb(0.05, (hc.x - r * 0.05, -r * 1.05, hc.z - r * 0.28), seg=6, name="earring"), "head", V2["gold"], metal=True, line=0.008)
        fig.add(block((0.05, 0.11, 0.10), (0.215, 0, hip + 0.09), bevel=0.015, name="buckle"), "hips", V2["gold"], metal=True, line=0.01)
    # a knife in each hand, built pointing forward with the arm hanging
    blade = [(0.05, -0.042), (0.37, -0.06), (0.58, 0.018), (0.37, 0.056), (0.05, 0.046)]
    bc = V2["cursed"] if t >= 3 else V2["steel"]
    for s, y in (("L", 1), ("R", -1)):
        h = fig.W["hand" + s]; g = Vector((h.x + 0.02, h.y + y * 0.01, h.z - 0.075))
        fig.add(slab(blade, 0.035, at=g, bevel=0.008, name="blade"), "hand" + s, bc, metal=True, glow=0.35 if t >= 3 else 0.0, line=0.015)
        fig.add(loft([(-0.11, 0.03, 0.03), (0.05, 0.034, 0.034)], seg=6, axis="x", at=g, name="grip"), "hand" + s, V2["leather"], line=0.01)
        fig.add(orb(0.055, (g.x + 0.055, g.y, g.z), (0.45, 1.0, 1.3), seg=7, name="guard"), "hand" + s, V2["gold"] if t >= 3 else V2["brass"],
                metal=True, line=0.01)
    # swipe arcs: first (far hand) and second (near hand, the hit)
    toggle(fig, "swipeA", "root", (0.2, 0.25, 0.9), 0)
    fig.add(slab(rr_arc(0.22, 0.86, 0.80, 118, -12, th=0.20), 0.02, at=(0, 0.25, 0), name="swipeA"), "swipeA", (1.0, 0.93, 0.74), glow=1.0)
    toggle(fig, "swipe", "root", (0.4, -0.3, 0.9), 0)
    fig.add(slab(rr_arc(0.42, 0.84, 0.92, 124, -28, th=0.26), 0.02, at=(0, -0.34, 0), name="swipe"), "swipe", (1.0, 0.96, 0.84), glow=1.0)
    return fig


def _rr_ready():
    return rr_aim(dict(chest=10, head=-3, uaR=44, laR=40, uaL=-58, laL=24, thL=32, snL=-50, thR=-16, snR=-30, brow=-4), R=22, L=204)


def rr_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t); s2 = math.sin(4 * math.pi * t)
    d = _rr_ready()
    # restless: bounces on his toes, near knife weaves
    d.update(chest=10 + 3 * s, head=(-3 - 2 * s, 0, 8 * c), uaR=44 + 6 * s2, laR=40 + 8 * c, uaL=-58 - 5 * s, thL=32 + 4 * s2, snL=-50 - 8 * s2,
             thR=-16 - 3 * s2, snR=-30 - 6 * s2, squash=(1 - 0.012 * s2, 1 + 0.02 * s2), tail=(8, t))
    return rr_aim(d, R=22 + 14 * s, L=204 - 8 * c)


def rr_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _rr_ready()
    d.update(thL=48 * s, snL=-16 - 62 * max(0, c), thR=-48 * s, snR=-16 - 62 * max(0, -c), chest=14 + 4 * math.cos(2 * p), hips=4,
             head=-6 - 3 * math.cos(2 * p), uaR=-52 * s + 6, laR=66 + 10 * c, uaL=52 * s + 6, laL=66 - 10 * c,
             root=(0.03 * math.cos(2 * p), 0.045 * abs(c)), tail=(42, t * 2))
    return rr_aim(d, R=20 - 30 * s, L=200 + 30 * s)


def rr_attack(t, i, n):
    G = dict(_rr_ready(), tail=(0, 0.0))
    windA = rr_aim(dict(G, chest=-6, head=4, uaL=188, laL=-22, uaR=20, laR=50, root=(-0.04, 0), brow=-10, tail=(-14, 0.1)), R=30, L=128)
    slashA = rr_aim(dict(G, chest=14, hips=3, head=-6, uaL=66, laL=8, uaR=-44, laR=64, thL=36, snL=-40, thR=-22, snR=-18, root=(0.10, 0), brow=-12,
                         vis=dict(swipeA=1, m_open=1, m_shut=0), tail=(30, 0.3)), R=60, L=-24)
    windB = rr_aim(dict(G, chest=-10, hips=-3, head=6, uaR=202, laR=-26, uaL=24, laL=44, thL=26, snL=-50, thR=-10, snR=-34, root=(0.05, 0),
                        squash=(1.04, 0.96), brow=-14, vis=dict(m_open=0, m_shut=1), tail=(-20, 0.4)), R=132, L=6)
    hitB = rr_aim(dict(G, chest=26, hips=7, head=-16, uaR=74, laR=10, uaL=-56, laL=30, thL=42, snL=-34, thR=-38, snR=-4, root=(0.30, 0),
                       squash=(0.96, 1.04), brow=-16, vis=dict(swipe=1, m_open=1, m_shut=0), tail=(46, 0.5)), R=-26, L=-50)
    hold = rr_aim(dict(hitB, uaR=52, laR=8, chest=29, root=(0.32, 0), vis=dict(swipe=0, m_open=1, m_shut=0), tail=(10, 0.7)), R=-48, L=-40)
    return keys([(0.0, G), (0.11, windA), (0.22, slashA), (0.33, windB), (0.44, windB), (0.56, hitB), (0.72, hold), (1.0, dict(G, tail=(0, 1.0)))], t)


def rr_hit(t, i, n):
    G = _rr_ready()
    back = rr_aim(dict(G, chest=-34, head=-18, hips=-6, root=(-0.10, 0), squash=(1.07, 0.92), uaR=-60, laR=60, uaL=-80, laL=40, brow=14,
                       vis=dict(m_open=1, m_shut=0), tail=(-34, 0.2)), R=80, L=60)
    mid = rr_aim(dict(G, chest=-12, root=(-0.05, 0)), R=55, L=190)
    return keys([(0.0, back), (0.45, mid), (1.0, G)], t)


def rr_die(t, i, n):
    G = _rr_ready()
    reel = rr_aim(dict(G, chest=-40, head=-20, hips=-8, root=(-0.10, 0), uaR=-110, laR=40, uaL=-60, laL=30, thL=10, snL=-20, thR=-10, snR=-10,
                       brow=16, vis=dict(m_open=1, m_shut=0), tail=(-30, 0.2)), R=100, L=70)
    fall = rr_aim(dict(reel, rootrot=-60, root=(-0.20, 0.08), free=1, chest=-30, thL=34, snL=-56, thR=12, snR=-30, uaR=-140, uaL=-90), R=150, L=120)
    down = rr_aim(dict(fall, rootrot=-90, root=(-0.30, 0.19), chest=-RR_LEAN, head=10, thL=16, snL=-24, thR=2, snR=-6, uaR=-158, laR=8, uaL=-24,
                       laL=14, vis=dict(m_open=0, m_shut=1), brow=0, tail=(0, 0.5)), R=176, L=4)
    bounce = rr_aim(dict(down, root=(-0.30, 0.25), rootrot=-85), R=170, L=10)
    return keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, down), (1.0, down)], t)


def _rr(t):
    register(dict(id="cinder_runner" + ("" if t == 1 else "_t%d" % t), tier=t, v2=roperat_fig,
                  anims=dict(idle=rr_idle, walk=rr_walk, attack=rr_attack, hit=rr_hit, die=rr_die)))


for _t in (1, 2, 3):
    _rr(_t)
