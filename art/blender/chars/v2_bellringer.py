from kit import *
# Shantyman (v2) — big singer: wide belly, yellow sou'wester, grey beard, a wide squeezebox in both hands.
# Silhouette hook: the wide squeezebox. He stands turned toward the audience; on the hit frame he pulls the
# bellows wide and sings (mouth open, sound rings + a note).

SM_LEAN = -3
SM_W0 = 0.40          # built half-width of the bellows
SM_N = 7              # pleats
SM_YELLOW = (0.99, 0.80, 0.16)


def sm_arc(cx, cz, R, a0, a1, th=0.10, n=10):
    out = []; inn = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n); k = 1 - th * math.sin(math.pi * i / n)
        out.append((cx + R * math.cos(a), cz + R * math.sin(a))); inn.append((cx + R * k * math.cos(a), cz + R * k * math.sin(a)))
    return out + inn[::-1][1:-1]


def sm_box(d, w, sink=0.0):
    """Arms + squeezebox for a bellows half-width w (0.26 squeezed .. 0.80 pulled wide). sink pushes it into the belly."""
    k = (w - 0.40) / 0.40
    k = max(-0.4, min(1.0, k))
    yaw = lerp(4, 40, k); up = lerp(50, 62, k); bend = lerp(45, 20, k)
    d["uaL"] = (up, 0, yaw); d["uaR"] = (up, 0, -yaw); d["laL"] = bend; d["laR"] = bend
    off = dict(d.get("off", {}))
    kk = max(k, 0.0)
    off["sq"] = (lerp(0, -0.06, kk) - sink * 0.6, 0, lerp(0, 0.05, kk) - sink)
    off["sqL"] = (0, w - SM_W0, 0); off["sqR"] = (0, -(w - SM_W0), 0)
    for i in range(SM_N):
        f = (i + 0.5) * 2 / SM_N - 1
        off["sqp%d" % i] = (0, f * (w - SM_W0), 0)
    d["off"] = off
    return d


def shantyman_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("sm%d" % t, INK_CREW, h=2.0)
    trim = V2["gold"] if t >= 3 else (V2["iron"] if t == 2 else V2["brass"])
    grey = (0.78, 0.78, 0.76)
    C = dict(skin=(0.88, 0.62, 0.48), body=V2["navy"], sleeve=V2["navy"], arm=V2["navy"], legs=V2["navy_dk"], belt=V2["tar"],
             boots=V2["leather"], cuff=V2["leather"], nose=(0.86, 0.44, 0.38))
    if t >= 2:
        C.update(body=V2["leather"])
    P = dict(hip=0.66, chest_h=0.72, wy=0.45, wx=0.33, shoulder=0.52, head_r=0.31, belly=1.36, arm_r=0.135, upper_arm=0.33, lower_arm=0.31,
             leg_r=0.16, thigh=0.27, shin=0.25, hip_w=0.21, lean=SM_LEAN, neck_x=0.03, chest_x=0.04)
    body(fig, P, C); fists(fig, C, 0.15); boots(fig, C, length=0.38, h=0.21)
    head_crew(fig, C, beard=grey, nose=1.3, jaw=1.12, brow=(0.34, 0.34, 0.37))
    hc = fig.head_c; r = fig.head_r; hip = fig.hip
    # sou'wester: domed crown, brim short in front and long and low at the back
    hz = hc.z + r * 0.46
    fig.add(loft([(hz - 0.03, r * 1.07, r * 1.07), (hz + r * 0.34, r * 0.99, r * 1.01, -0.01), (hz + r * 0.60, r * 0.66, r * 0.70, -0.03)],
                 seg=14, at=(hc.x, 0, 0), round_=(False, True), name="crown"), "head", SM_YELLOW)
    brim = orb(r, (hc.x - r * 0.36, 0, hz), (1.72, 1.42, 0.15), seg=14, name="brim")
    fig.add(turn(brim, -17, "Y", (hc.x, 0, hz)), "head", SM_YELLOW)
    fig.add(loft([(hz + 0.0, r * 1.09, r * 1.09), (hz + r * 0.14, r * 1.07, r * 1.07)], seg=14, at=(hc.x, 0, 0), round_=(False, False), name="band"),
            "head", V2["gold"] if t >= 3 else (0.80, 0.60, 0.12), metal=t >= 3, line=0)
    if t >= 2:      # gull feather in the hat band
        chain(fig, "feather", "head", (hc.x - r * 0.3, -r * 1.0, hz + r * 0.1), [0.19, 0.16], 0.065, V2["white"] if t == 2 else V2["gold"],
              (-0.6, -0.15, 0.8), flat=0.4, taper=0.7, sway=0.5, phase=0.2)
    # red neckerchief tail, brass buckle
    nk = (fig.neck.x - 0.16, 0, fig.neck.z - 0.02)
    chain(fig, "ker", "chest", nk, [0.17, 0.15], 0.06, V2["red"], (-1, 0, -0.5), sway=0.8)
    fig.add(block((0.06, 0.16, 0.13), (P["wx"] + 0.03, 0, hip + 0.09), bevel=0.02, name="buckle"), "hips", trim, metal=True, line=0.012)
    # squeezebox: two wooden ends + pleats, every piece on its own pivot so the bellows can stretch
    Q = Vector((0.60, 0.0, hip + 0.50))
    fig.joint("sq", Q, "chest", 1)
    for s, y in (("L", 1), ("R", -1)):
        fig.joint("sq" + s, (Q.x, y * SM_W0, Q.z), "sq", 1)
        fig.add(block((0.42, 0.13, 0.46), (Q.x, y * (SM_W0 + 0.065), Q.z), bevel=0.03, name="end"), "sq" + s, V2["wood"])
        fig.add(block((0.46, 0.035, 0.50), (Q.x, y * (SM_W0 + 0.01), Q.z), bevel=0.012, name="frame"), "sq" + s, trim, metal=True, line=0.012)
        fig.add(block((0.10, 0.03, 0.34), (Q.x - 0.02, y * (SM_W0 + 0.145), Q.z), bevel=0.01, name="strap"), "sq" + s, V2["leather"], line=0.01)
        for (dx, dz) in ((0.12, 0.13), (0.12, 0.0), (0.12, -0.13)):
            fig.add(orb(0.03, (Q.x + dx, y * (SM_W0 + 0.135), Q.z + dz), seg=6, name="key"), "sq" + s, V2["white"], glow=0.5, line=0)
    T = 0.115
    for i in range(SM_N):
        y0 = ((i + 0.5) * 2 / SM_N - 1) * SM_W0
        fig.joint("sqp%d" % i, (Q.x, y0, Q.z), "sq", 1)
        if t >= 3:
            col = V2["cursed"] if i % 2 == 0 else (0.42, 0.62, 0.26)
        else:
            col = V2["red"] if i % 2 == 0 else (0.58, 0.15, 0.13)
        fig.add(loft([(-T, 0.135, 0.15), (0, 0.20, 0.22), (T, 0.135, 0.15)], seg=8, axis="y", at=(Q.x, y0, Q.z), sq=0.7, round_=(False, False),
                     name="pleat"), "sqp%d" % i, col, glow=0.35 if (t >= 3 and i % 2 == 0) else 0.0, flat=True, line=0.012)
    # the song: rings spreading from the mouth and a note (hit frame)
    mouth = Vector((0.42, -0.52, hc.z - 0.10))
    toggle(fig, "ring", "root", mouth, 0)
    for R_ in (0.74, 1.04, 1.34):
        fig.add(slab(sm_arc(mouth.x, mouth.z, R_, -34, 34, th=0.10), 0.02, at=(0, mouth.y, 0), name="ring"), "ring", (1.0, 0.92, 0.62), glow=1.0)
    nx = mouth.x + 0.80; nz = mouth.z + 0.78
    fig.add(orb(0.09, (nx, mouth.y, nz), (1.25, 0.4, 0.9), seg=8, name="note"), "ring", (1.0, 0.96, 0.80), glow=1.0)
    fig.add(block((0.035, 0.02, 0.30), (nx + 0.085, mouth.y, nz + 0.15), bevel=0, name="stem"), "ring", (1.0, 0.96, 0.80), glow=1.0)
    fig.add(slab([(0, 0), (0.15, -0.08), (0.15, -0.16), (0, -0.07)], 0.02, at=(nx + 0.085, mouth.y, nz + 0.30), name="flag"), "ring",
            (1.0, 0.96, 0.80), glow=1.0)
    return fig


def _sm_stand(w=0.44, twist=-26):
    d = dict(chest=(0, 0, twist), head=(-2, 0, -twist * 0.55), thL=9, snL=-12, thR=-8, snR=-10, brow=0, sq=0)
    return sm_box(d, w)


def sm_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    # the bellows breathe with him; he rocks on his heels
    d = _sm_stand(0.44 + 0.07 * s, -26 + 3 * c)
    d.update(chest=(1.5 * s, 0, -26 + 3 * c), head=(-2 - 2 * s, 0, 14 + 4 * c), squash=(1 - 0.008 * s, 1 + 0.014 * s), sq=(0, 5 * c, 0),
             tail=(4, t))
    return d


def sm_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _sm_stand(0.46 + 0.10 * math.sin(2 * p), -26)
    d.update(thL=23 * s, snL=-8 - 38 * max(0, c), thR=-23 * s, snR=-8 - 38 * max(0, -c), chest=(4 + 2 * math.cos(2 * p), 4 * s, -26 + 5 * s),
             head=(-4 - 2 * math.cos(2 * p), -3 * s, 14), sq=(0, 7 * s, 0), root=(0, 0.02 * math.cos(2 * p)), tail=(24, t * 2))
    return d


def sm_attack(t, i, n):
    G = dict(_sm_stand(), tail=(0, 0.0))
    inh = sm_box(dict(chest=(8, 0, -34), head=(6, 0, 18), thL=12, snL=-18, thR=-10, snR=-14, squash=(1.03, 0.97), brow=-8, sq=0,
                      root=(0.02, 0), tail=(10, 0.2)), 0.27)
    wind = sm_box(dict(chest=(-6, 0, -40), head=(-6, 0, 20), thL=10, snL=-14, thR=-12, snR=-10, squash=(1.02, 0.985), brow=-12, sq=(0, -8, 0),
                       root=(-0.03, 0), tail=(-14, 0.4)), 0.26)
    sing = sm_box(dict(chest=(-13, 0, -62), hips=-3, head=(-13, 0, 34), thL=16, snL=-10, thR=-16, snR=-6, squash=(0.97, 1.04), brow=10,
                       sq=(0, 10, 0), root=(0.03, 0), vis=dict(ring=1, m_open=1, m_shut=0), tail=(-30, 0.5)), 0.80)
    ring2 = dict(sing, vis=dict(ring=1.28, m_open=1, m_shut=0), chest=(-15, 0, -62), tail=(-20, 0.6))
    ease_ = sm_box(dict(chest=(-6, 0, -44), head=(-6, 0, 24), thL=12, snL=-12, thR=-10, snR=-8, brow=4, sq=(0, 4, 0),
                        vis=dict(ring=0, m_open=1, m_shut=0), tail=(-6, 0.8)), 0.62)
    return keys([(0.0, G), (0.16, inh), (0.30, wind), (0.44, wind), (0.56, sing), (0.66, ring2), (0.78, ease_), (1.0, dict(G, tail=(0, 1.0)))], t)


def sm_hit(t, i, n):
    G = _sm_stand()
    back = sm_box(dict(chest=(-17, 0, -14), head=(-15, 0, 6), hips=-4, root=(-0.10, 0), squash=(1.06, 0.93), thL=9, snL=-12, thR=-8, snR=-10,
                       brow=14, sq=(0, -14, 0), vis=dict(m_open=1, m_shut=0), tail=(-30, 0.2)), 0.30)
    mid = sm_box(dict(G, chest=(-6, 0, -20), root=(-0.05, 0)), 0.38)
    return keys([(0.0, back), (0.45, mid), (1.0, G)], t)


def sm_die(t, i, n):
    G = _sm_stand()
    reel = sm_box(dict(chest=(-20, 0, -14), head=(-18, 0, 6), hips=-7, root=(-0.10, 0), thL=6, snL=-10, thR=-10, snR=-8, brow=16,
                       sq=(0, -16, 0), vis=dict(m_open=1, m_shut=0), tail=(-30, 0.2)), 0.56)
    fall = sm_box(dict(reel, rootrot=-60, root=(-0.18, 0.12), free=1, chest=(-12, 0, -6), head=(-12, 0, 0), thL=28, snL=-48, thR=10, snR=-28,
                       sq=(0, 10, 0)), 0.40, sink=0.04)
    down = sm_box(dict(fall, rootrot=-90, root=(-0.24, 0.31), chest=(-SM_LEAN, 0, 0), head=(-6, 0, 0), thL=13, snL=-20, thR=2, snR=-6,
                       sq=(0, 0, 0), vis=dict(m_open=0, m_shut=1), brow=0, tail=(0, 0.5)), 0.28, sink=0.12)
    bounce = sm_box(dict(down, root=(-0.24, 0.37), rootrot=-86), 0.34, sink=0.10)
    return keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, down), (1.0, down)], t)


def _sm(t):
    register(dict(id="bellringer" + ("" if t == 1 else "_t%d" % t), tier=t, v2=shantyman_fig,
                  anims=dict(idle=sm_idle, walk=sm_walk, attack=sm_attack, hit=sm_hit, die=sm_die)))


for _t in (1, 2, 3):
    _sm(_t)
