from kit import *
# Captain Rook Halloran (v2 hero) — long red coat with trailing tails, big black tricorn with brass trim and a white
# plume, black beard. Cutlass in the near hand, brass flare pistol in the far hand.
# Silhouette hook: coat tails + plume. Special: raises the flare pistol overhead and fires (burst on frames 5-7).

def mr_star(cx, cz, n, R, r, a0=0.0):
    pts = []
    for i in range(n * 2):
        a = a0 + math.pi * i / n; k = R if i % 2 == 0 else r
        pts.append((cx + k * math.cos(a), cz + k * math.sin(a)))
    return pts


MR_PLUME = ("plume0", "plume1", "plume2")


def captain_fig(spec):
    fig = Fig("mr", INK_CREW, h=2.4, line=0.024)
    coat = (0.74, 0.17, 0.14); coat_dk = (0.58, 0.13, 0.12); black = (0.13, 0.12, 0.14); beard = (0.11, 0.10, 0.11)
    C = dict(skin=V2["skin"], body=coat, sleeve=coat, arm=coat, legs=V2["navy_dk"], belt=V2["navy"], boots=V2["tar"], cuff=V2["leather"],
             nose=(0.86, 0.52, 0.42))
    P = dict(hip=0.80, chest_h=0.82, wy=0.40, wx=0.29, shoulder=0.50, head_r=0.32, belly=1.0, arm_r=0.125, upper_arm=0.34,
             lower_arm=0.32, leg_r=0.15, thigh=0.34, shin=0.32, hip_w=0.19, lean=0, neck_x=0.03, chest_x=0.06)
    body(fig, P, C); fists(fig, C, 0.155); boots(fig, C, length=0.42, h=0.22)
    head_crew(fig, C, beard=beard, nose=1.15, jaw=1.08, brow=beard)
    hc = fig.head_c; r = fig.head_r; hip = fig.hip; ch = P["chest_h"]; wx = P["wx"]; wy = P["wy"]
    ar = P["arm_r"]; ua = P["upper_arm"]; la = P["lower_arm"]; sz = fig.sh_z
    # ---- coat front: canvas shirt down the middle, brass lapel edges and buttons, epaulettes, turned cuffs
    fig.add(loft([(hip + 0.16, wx * 1.04, wy * 0.40, 0.04), (hip + ch * 0.42, wx * 1.10, wy * 0.42, 0.05), (hip + ch * 0.72, wx * 1.14, wy * 0.44, 0.08),
                  (hip + ch * 0.92, wx * 0.86, wy * 0.40, 0.06)], name="shirt", sq=0.3), "chest", V2["canvas"], line=0.010)
    for y in (-1, 1):
        fig.add(block((0.06, 0.07, ch * 0.66), (wx * 1.12 + 0.06, y * wy * 0.47, hip + ch * 0.53), bevel=0.02, name="lapel"), "chest", V2["brass"],
                metal=True, line=0.010)
        for k in range(3):
            fig.add(orb(0.038, (wx * 1.12 + 0.07, y * wy * 0.66, hip + ch * (0.30 + 0.2 * k)), seg=6, name="button"), "chest", V2["gold"], metal=True, line=0)
    for s, y in (("L", 1), ("R", -1)):
        sy = y * fig.sh_w
        fig.add(orb(0.19, (0.0, sy + y * 0.02, sz + 0.07), (1.15, 1.05, 0.55), seg=10, name="epaulette"), "ua" + s, V2["brass"], metal=True)
        for k in (-1, 0, 1):
            fig.add(cone((k * 0.11, sy + y * 0.15, sz + 0.04), (k * 0.13, sy + y * 0.19, sz - 0.10), 0.04, 0.02, seg=5, name="fringe"), "ua" + s, V2["gold"],
                    metal=True, line=0.008)
        fig.add(loft([(sz - ua - la * 0.62, ar * 1.38, ar * 1.38), (sz - ua - la * 0.96, ar * 1.12, ar * 1.12)], seg=9, at=(0, sy, 0),
                     round_=(False, False), name="cuff"), "la" + s, V2["canvas"])
        fig.add(loft([(sz - ua - la * 0.58, ar * 1.42, ar * 1.42), (sz - ua - la * 0.66, ar * 1.42, ar * 1.42)], seg=9, at=(0, sy, 0),
                     round_=(False, False), name="cufftrim"), "la" + s, V2["brass"], metal=True, line=0.008)
    fig.add(block((0.07, 0.17, 0.15), (wx + 0.03, 0, hip + 0.09), bevel=0.02, name="buckle"), "hips", V2["brass"], metal=True, line=0.012)
    # ---- coat skirt: a short flare under the belt, then the long tails (chains, so they trail)
    fig.add(loft([(hip + 0.14, wx * 1.06, wy * 1.06, -0.02), (hip - 0.10, wx * 1.22, wy * 1.14, -0.06)], name="skirt", sq=0.3, round_=(False, False)),
            "hips", coat)
    z0 = hip - 0.02
    chain(fig, "tailN", "hips", (-0.10, -wy * 1.02, z0), [0.26, 0.24, 0.22], 0.21, coat, (-0.16, -0.06, -1), taper=0.90, flat=0.36, sway=0.45, phase=0.10)
    chain(fig, "tailB", "hips", (-0.30, -0.14, z0), [0.27, 0.25, 0.23], 0.20, coat_dk, (-0.30, 0, -1), taper=0.90, flat=0.5, sway=0.55, phase=0.30)
    chain(fig, "tailC", "hips", (-0.30, 0.16, z0), [0.26, 0.24, 0.22], 0.19, coat, (-0.42, 0, -1), taper=0.90, flat=0.5, sway=0.6, phase=0.55)
    chain(fig, "tailF", "hips", (-0.08, wy * 1.02, z0), [0.26, 0.24, 0.20], 0.20, coat_dk, (-0.14, 0.06, -1), taper=0.90, flat=0.36, sway=0.45, phase=0.75)
    # ---- tricorn: upturned three-cornered brim (front point forward), brass edge, crown, cockade
    zb = hc.z + r * 0.50; zt = hc.z + r * 0.92; off = -r * 0.30
    fig.add(loft([(zb, r * 1.30, r * 1.22, off * 0.5), (zt, r * 2.25, r * 1.95, off)], seg=3, at=(hc.x, 0, 0), round_=(False, False), name="brim"), "head", black)
    fig.add(loft([(zt - 0.035, r * 2.30, r * 2.0, off), (zt + 0.035, r * 2.34, r * 2.03, off)], seg=3, at=(hc.x, 0, 0), round_=(False, False), name="brimtrim"),
            "head", V2["brass"], metal=True, line=0.014)
    fig.add(loft([(zt + 0.02, r * 2.08, r * 1.80, off), (zt + 0.06, r * 2.02, r * 1.74, off)], seg=3, at=(hc.x, 0, 0), round_=(False, False), name="brimtop"),
            "head", black, line=0)
    fig.add(loft([(zb + 0.02, r * 1.04, r * 1.04, -0.02), (hc.z + r * 1.20, r * 0.98, r * 0.98, -0.03), (hc.z + r * 1.42, r * 0.80, r * 0.82, -0.04)], seg=12,
                 at=(hc.x, 0, 0), round_=(False, True), name="crown", sq=0.2), "head", black)
    fig.add(orb(r * 0.20, (hc.x + r * 0.2, -r * 0.88, zt - 0.05), (1, 0.5, 1), seg=8, name="cockade"), "head", V2["gold"], metal=True, line=0.010)
    # white plume: rises from the near side of the hat and sweeps back. Posed by hand (see _mr_plume), not by the kit's tail lean.
    pb = (hc.x - r * 0.15, -r * 0.95, zt + 0.02)
    def feather(s0, s1, n=8):
        A = []; B = []
        for k in range(n + 1):
            u = s0 + (s1 - s0) * k / n
            x = -0.10 * u - 0.78 * u * u; z = 0.95 * u - 0.22 * u * u
            dx = -0.10 - 1.56 * u; dz = 0.95 - 0.44 * u; m = math.hypot(dx, dz)
            w = 0.07 + 0.17 * math.sin(math.pi * min(1.0, u * 1.05) ** 0.8)
            A.append((x - dz / m * w, z + dx / m * w)); B.append((x + dz / m * w * 0.8, z - dx / m * w * 0.8))
        return A + B[::-1]
    def fpt(u):
        return Vector((pb[0] - 0.10 * u - 0.78 * u * u, pb[1], pb[2] + 0.95 * u - 0.22 * u * u))
    fig.joint("plume0", pb, "head", -1); fig.joint("plume1", fpt(0.5), "plume0", -1); fig.joint("plume2", fpt(0.8), "plume1", -1)
    fig.add(slab(feather(0.0, 0.56), 0.08, at=pb, bevel=0.02, name="plumeA"), "plume0", V2["white"], line=0.016)
    fig.add(slab(feather(0.46, 0.86), 0.075, at=(pb[0], pb[1] - 0.01, pb[2]), bevel=0.02, name="plumeB"), "plume1", V2["white"], line=0.016)
    fig.add(slab(feather(0.76, 1.0, 5), 0.07, at=(pb[0], pb[1] - 0.02, pb[2]), bevel=0.02, name="plumeC"), "plume2", (0.90, 0.90, 0.92), line=0.016)
    fig.add(orb(0.10, (pb[0] + 0.02, pb[1], pb[2] + 0.02), (1.0, 0.5, 1.0), seg=8, name="plumebase"), "head", V2["white"], line=0.012)
    # ---- cutlass in the near hand (built pointing forward with the arm hanging)
    h = fig.W["handR"]; g = Vector((h.x + 0.02, h.y - 0.02, h.z - 0.10))
    blade = [(0.08, -0.05), (0.62, -0.10), (0.96, -0.02), (1.12, 0.21), (0.88, 0.12), (0.60, 0.075), (0.08, 0.06)]
    fig.add(slab(blade, 0.04, at=g, bevel=0.01, name="blade"), "handR", V2["steel"], metal=True, line=0.018)
    fig.add(loft([(-0.17, 0.04, 0.04), (0.06, 0.045, 0.045)], seg=7, axis="x", at=g, name="grip"), "handR", V2["leather"], line=0.012)
    fig.add(orb(0.11, (g.x + 0.08, g.y, g.z), (0.45, 1.0, 1.3), seg=8, name="guard"), "handR", V2["brass"], metal=True, line=0.012)
    fig.add(orb(0.05, (g.x - 0.19, g.y, g.z), seg=6, name="pommel"), "handR", V2["brass"], metal=True, line=0.010)
    # ---- flare pistol in the far hand: fat brass barrel with a flared muzzle
    hL = fig.W["handL"]; q = Vector((hL.x + 0.02, hL.y, hL.z - 0.10))
    fig.add(block((0.10, 0.08, 0.24), (q.x - 0.03, q.y, q.z - 0.02), rot=(14, "Y"), bevel=0.02, name="pgrip"), "handL", V2["wood"], line=0.012)
    fig.add(loft([(0.0, 0.058, 0.058), (0.36, 0.064, 0.064), (0.46, 0.10, 0.10)], seg=9, axis="x", at=(q.x, q.y, q.z + 0.07), round_=(True, False), name="barrel"),
            "handL", V2["brass"], metal=True, line=0.014)
    fig.add(orb(0.07, (q.x + 0.465, q.y, q.z + 0.07), (0.25, 1, 1), seg=8, name="bore"), "handL", V2["tar"], line=0)
    M = Vector((q.x + 0.50, q.y, q.z + 0.07))
    toggle(fig, "flare", "handL", M, 0)
    fig.add(slab(mr_star(M.x + 0.42, M.z, 8, 0.66, 0.27, 0.2), 0.02, at=(0, M.y, 0), name="burst"), "flare", (1.0, 0.40, 0.20), glow=1.0)
    fig.add(slab(mr_star(M.x + 0.42, M.z, 8, 0.42, 0.17, 0.59), 0.02, at=(0, M.y - 0.05, 0), name="burst2"), "flare", (1.0, 0.95, 0.70), glow=1.0)
    fig.add(slab([(M.x + 0.5, M.z - 0.09), (M.x + 1.75, M.z), (M.x + 0.5, M.z + 0.09)], 0.02, at=(0, M.y - 0.03, 0), name="streak"), "flare", (1.0, 0.72, 0.40), glow=1.0)
    fig.add(orb(0.13, (M.x + 1.75, M.y - 0.03, M.z), seg=8, name="star"), "flare", (1.0, 0.97, 0.85), glow=1.0)
    for (dx, dz, s) in ((0.95, 0.5, 0.05), (1.1, -0.45, 0.045), (0.2, 0.62, 0.04), (0.1, -0.6, 0.05), (1.35, 0.3, 0.04), (1.4, -0.25, 0.035)):
        fig.add(orb(s, (M.x + dx, M.y - 0.04, M.z + dz), seg=6, name="spark"), "flare", (1.0, 0.80, 0.45), glow=1.0)
    # ---- slash arc
    toggle(fig, "swipe", "root", (0.45, -0.5, 1.4), 0)
    arc = []; inn = []
    for i in range(12):
        a = math.radians(132 - i * 13); k = math.sin(math.pi * i / 11)
        arc.append((0.45 + 1.85 * math.cos(a), 1.40 + 1.85 * math.sin(a)))
        inn.append((0.45 + 1.85 * (1 - 0.24 * k) * math.cos(a), 1.40 + 1.85 * (1 - 0.24 * k) * math.sin(a)))
    fig.add(slab(arc + inn[::-1][1:-1], 0.02, at=(0, -0.62, 0), name="swipe"), "swipe", (1.0, 0.96, 0.84), glow=1.0)
    return fig


def _mr_plume(d, lean=0.0, t=0.0, amp=1.0):
    """Plume links (pitch, positive = laid back). Each link lags the one before."""
    for k, jn in enumerate(MR_PLUME):
        d[jn] = lean * (0.5 if k == 0 else 0.35) + amp * 7 * (1 + 0.5 * k) * math.sin(2 * math.pi * t - 0.9 * k)
    return d


def _mr_base():
    # chest out, cutlass low and forward, pistol at the far hip
    return dict(chest=-2, head=0, uaR=-18, laR=42, handR=-8, uaL=8, laL=28, handL=-18, thL=12, snL=-16, thR=-10, snR=-12, brow=0)


def mr_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _mr_base()
    # fidget: he rolls the cutlass wrist
    d.update(chest=-2 + 1.6 * s, head=-1.2 * s, uaR=-18 + 2 * s, laR=42 + 4 * c, handR=-8 + 9 * math.sin(2 * math.pi * t - 0.8),
             laL=28 + 3 * c, squash=(1 - 0.008 * s, 1 + 0.014 * s), tail=(-5, t))
    return _mr_plume(d, 4, t, 1.0)


def mr_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _mr_base()
    d.update(thL=27 * s, snL=-8 - 40 * max(0, c), thR=-27 * s, snR=-8 - 40 * max(0, -c), chest=5 + 2.5 * math.cos(2 * p),
             head=-4 - 2 * math.cos(2 * p), uaR=-14 - 16 * s, laR=40 + 6 * c, handR=-6 + 6 * math.cos(2 * p - 0.8), uaL=8 + 20 * s, laL=30,
             root=(0, 0.022 * math.cos(2 * p)), tail=(-34, t * 2))
    return _mr_plume(d, 22, t * 2, 1.2)


def mr_attack(t, i, n):
    G = _mr_base()
    wind = dict(G, chest=-15, hips=-4, head=6, uaR=165, laR=48, handR=-18, uaL=40, laL=40, thL=20, snL=-26, thR=-18, snR=-10, root=(-0.08, 0),
                squash=(1.03, 0.97), brow=-12, vis=dict(m_open=1, m_shut=0), tail=(22, 0.2))
    hit = dict(G, chest=22, hips=6, head=-12, uaR=80, laR=10, handR=-100, uaL=-40, laL=30, thL=36, snL=-32, thR=-30, snR=-4, root=(0.20, 0),
               squash=(0.97, 1.03), brow=-16, vis=dict(m_open=1, m_shut=0, swipe=1), tail=(-48, 0.5))
    hold = dict(hit, uaR=58, laR=8, handR=-112, chest=25, root=(0.22, 0), vis=dict(m_open=1, m_shut=0), tail=(-12, 0.7))
    d = keys([(0.0, G), (0.30, wind), (0.44, wind), (0.556, hit), (0.72, hold), (1.0, dict(G, tail=(0, 1.0)))], t)
    v = dict(d.get("vis", {})); v["swipe"] = 1 if i == 5 else 0; d["vis"] = v
    return _mr_plume(d, {3: -14, 4: -18, 5: 40, 6: 24, 7: 8}.get(i, 0), t, 0.5)


def mr_hit(t, i, n):
    G = _mr_base()
    back = dict(G, chest=-19, head=-16, hips=-5, root=(-0.10, 0), squash=(1.06, 0.93), uaR=-60, laR=60, uaL=-30, laL=50, brow=14,
                vis=dict(m_open=1, m_shut=0), tail=(34, 0.2))
    d = keys([(0.0, back), (0.45, dict(G, chest=-7, root=(-0.05, 0))), (1.0, G)], t)
    return _mr_plume(d, (-30, 16, -6, 0)[min(i, 3)], t, 0.3)


def mr_die(t, i, n):
    G = _mr_base()
    reel = dict(G, chest=-22, head=-20, hips=-8, root=(-0.10, 0), uaR=-100, laR=30, uaL=-40, laL=20, brow=16, vis=dict(m_open=1, m_shut=0), tail=(34, 0.2))
    fall = dict(reel, rootrot=-60, root=(0.35, 0.12), free=1, thL=30, snL=-50, thR=10, snR=-30, uaR=-40, laR=10, handR=-60, uaL=-110)
    down = dict(fall, rootrot=-90, root=(1.0, 0.26), chest=-4, head=-8, thL=14, snL=-20, thR=2, snR=-6, uaR=4, laR=2, handR=-90, uaL=-170, laL=6,
                handL=-80, vis=dict(m_open=0, m_shut=1), brow=0, tail=(0, 0.5))
    bounce = dict(down, root=(1.0, 0.33), rootrot=-86)
    d = keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, down), (1.0, down)], t)
    _mr_plume(d, -26, t, 0.4)
    if t > 0.3:
        k = ease(min(1.0, (t - 0.3) / 0.38)); d["plume0"] = lerp(d["plume0"], -62, k); d["plume1"] = lerp(d["plume1"], -16, k); d["plume2"] = lerp(d["plume2"], -10, k)
    return d


def mr_special(t, i, n):
    G = _mr_base()
    # plant the feet, sweep the pistol up overhead (held 2 frames), fire on frame 5 with a kick down through the arm
    up = dict(G, chest=-8, head=-10, uaL=150, laL=30, handL=-96, uaR=-30, laR=30, handR=-20, thL=16, snL=-20, thR=-14, snR=-10, root=(-0.03, 0),
              brow=-8, tail=(8, 0.2))
    aim = dict(up, chest=-11, head=-16, uaL=166, laL=8, handL=-90, squash=(0.98, 1.03), vis=dict(m_open=1, m_shut=0))
    fire = dict(aim, chest=-6, head=-12, uaL=160, laL=20, handL=-98, squash=(1.03, 0.96), root=(-0.05, 0), brow=-14,
                vis=dict(m_open=1, m_shut=0), tail=(-20, 0.5))
    hold = dict(aim, chest=-9, head=-18, vis=dict(m_open=1, m_shut=0), tail=(0, 0.7))
    d = keys([(0.0, G), (0.26, up), (0.36, aim), (0.46, aim), (0.556, fire), (0.68, hold), (0.80, hold), (1.0, dict(G, tail=(0, 1.0)))], t)
    v = dict(d.get("vis", {})); v["flare"] = {5: 1.0, 6: 1.25, 7: 0.8}.get(i, 0); d["vis"] = v
    return _mr_plume(d, {5: -20, 6: 12}.get(i, 4), t, 0.5)


register(dict(id="marshal", v2=captain_fig,
              anims=dict(idle=mr_idle, walk=mr_walk, attack=mr_attack, hit=mr_hit, die=mr_die, special=mr_special)))
