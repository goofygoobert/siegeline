from kit import *
# Blackpowder (v2) — lean musketeer: navy coat, black tricorn with three clear points, long flintlock held diagonally.
# Silhouette hook: the long diagonal musket and the tricorn points. Attack: shoulder, aim, FIRE (flash + recoil), lower.

TB_LEAN = 3


def tb_num(d, k):
    v = d.get(k, 0.0)
    return v if isinstance(v, (int, float)) else v[0]


def tb_gun(d, elev):
    """Set the wrist so the musket points at a world elevation (deg above +X), whatever the body is doing."""
    d["handR"] = elev + d.get("rootrot", 0) + tb_num(d, "hips") + tb_num(d, "chest") + TB_LEAN - tb_num(d, "uaR") - tb_num(d, "laR")
    return d


def tb_tricorn(r, c, base):
    pts = [(0, 2.15, 0.16), (32, 1.20, 0.44), (65, 1.02, 0.64), (98, 1.16, 0.44), (130, 1.95, 0.20), (155, 1.14, 0.44),
           (180, 0.98, 0.60), (205, 1.14, 0.44), (230, 1.95, 0.20), (262, 1.16, 0.44), (295, 1.02, 0.64), (328, 1.20, 0.44)]
    bm = bmesh.new(); ot = []; ob = []; it = []; ib = []
    for a, k, z in pts:
        ca = math.cos(math.radians(a)); sa = math.sin(math.radians(a))
        ot.append(bm.verts.new((c.x + ca * k * r, sa * k * r, base + z * r)))
        ob.append(bm.verts.new((c.x + ca * k * r * 0.93, sa * k * r * 0.93, base + z * r - 0.075)))
        it.append(bm.verts.new((c.x + ca * 0.84 * r, sa * 0.84 * r, base + 0.02)))
        ib.append(bm.verts.new((c.x + ca * 0.84 * r, sa * 0.84 * r, base - 0.06)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((it[i], ot[i], ot[j], it[j]))
        bm.faces.new((ot[i], ob[i], ob[j], ot[j]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    bm.faces.new(it); bm.faces.new(ib[::-1])
    return _obj("tricorn", bm)


def blackpowder_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("tb%d" % t, INK_CREW, h=1.95)
    trim = V2["gold"] if t >= 3 else V2["brass"]
    C = dict(skin=(0.84, 0.60, 0.46), body=V2["navy"], sleeve=V2["navy"], arm=V2["navy"], legs=V2["canvas"], belt=V2["red"],
             boots=V2["tar"], cuff=V2["tar"], nose=(0.80, 0.50, 0.40))
    P = dict(hip=0.70, chest_h=0.66, wy=0.32, wx=0.22, shoulder=0.39, head_r=0.28, belly=0.92, arm_r=0.10, upper_arm=0.30,
             lower_arm=0.28, leg_r=0.12, thigh=0.29, shin=0.27, hip_w=0.15, lean=TB_LEAN, neck_x=0.03)
    body(fig, P, C); fists(fig, C, 0.125); boots(fig, C, length=0.34, h=0.19)
    head_crew(fig, C, nose=1.1, jaw=0.98, brow=(0.13, 0.10, 0.09))
    hc = fig.head_c; r = fig.head_r; hip = fig.hip; wx = P["wx"]; wy = P["wy"]; ch = P["chest_h"]
    ex = hc.x + r * 0.90
    fig.add(orb(r * 0.2, (ex + r * 0.02, 0, hc.z - r * 0.36), (0.7, 1.7, 0.5), seg=8, name="tache"), "head", (0.13, 0.10, 0.09), line=0.01)
    # tricorn: crown + three-pointed upturned brim
    base = hc.z + r * 0.62
    fig.add(loft([(base - 0.04, r * 0.96, r * 0.96), (base + r * 0.35, r * 0.82, r * 0.84), (base + r * 0.66, r * 0.60, r * 0.62)],
                 seg=12, at=(hc.x, 0, 0), round_=(False, True), name="crown"), "head", V2["tar"])
    fig.add(tb_tricorn(r, hc, base), "head", (0.20, 0.17, 0.16), flat=True)
    if t >= 3:      # gold edging: beads on the three points
        for a, k, z in ((0, 2.08, 0.17), (130, 1.90, 0.21), (230, 1.90, 0.21)):
            fig.add(orb(r * 0.13, (hc.x + math.cos(math.radians(a)) * k * r, math.sin(math.radians(a)) * k * r, base + z * r), seg=6),
                    "head", V2["gold"], metal=True, line=0.01)
    if t >= 2:      # feather in the hat
        chain(fig, "feather", "head", (hc.x - r * 0.2, -r * 0.80, base + r * 0.5), [0.20, 0.17], 0.07, V2["red"] if t == 2 else V2["gold"],
              (-0.75, -0.1, 0.65), flat=0.4, taper=0.7, sway=0.5, phase=0.2)
    # hair queue with a ribbon
    q = (hc.x - r * 0.98, 0, hc.z - r * 0.05)
    fig.add(orb(r * 0.17, q, seg=8, name="ribbon"), "head", V2["red"], line=0.012)
    chain(fig, "queue", "head", q, [0.15, 0.13], 0.06, (0.22, 0.15, 0.10), (-0.7, 0, -1), sway=0.9)
    # coat: flared skirt, two tails, brass buttons, red collar, powder horn
    fig.add(loft([(hip + 0.13, wx * 1.04, wy * 1.02), (hip - 0.08, wx * 1.18, wy * 1.08, -0.01), (hip - 0.27, wx * 1.34, wy * 1.14, -0.04)],
                 name="skirt", sq=0.3, round_=(False, False)), "hips", V2["navy"])
    for i, y in enumerate((-0.14, 0.14)):
        chain(fig, "coat%d" % i, "hips", (-wx * 1.15, y, hip - 0.18), [0.20, 0.18], 0.11, V2["navy_dk"], (-0.3, 0, -1), flat=0.8, taper=0.85,
              sway=0.6, phase=0.3 * i)
    for k in (0.30, 0.50, 0.70):
        fig.add(orb(0.035, (wx * 1.10 + 0.03, -0.06, hip + ch * k), seg=6, name="button"), "chest", trim, metal=True, line=0.008)
    fig.add(loft([(hip + ch * 0.90, wx * 0.80, wy * 0.74), (hip + ch * 1.0, wx * 0.66, wy * 0.56)], name="collar", round_=(False, False), sq=0.2),
            "chest", V2["red"], line=0.012)
    fig.add(cone((0.10, -wy - 0.10, hip + 0.12), (-0.16, -wy - 0.11, hip - 0.10), 0.07, 0.018, seg=7, name="horn"), "hips", V2["bone"], line=0.014)
    fig.add(orb(0.05, (0.11, -wy - 0.10, hip + 0.13), seg=6), "hips", trim, metal=True, line=0.008)
    if t >= 2:      # leather bandolier + shoulder piece
        fig.add(orb(0.15, (0.0, -P["shoulder"] - 0.02, fig.sh_z + 0.03), (1.1, 1.0, 0.75), seg=10, name="epaulette"), "uaR",
                V2["gold"] if t >= 3 else V2["leather"], metal=t >= 3)
        fig.add(loft([(hip + 0.16, wx * 1.0, wy * 1.0), (hip + 0.24, wx * 1.07, wy * 1.02, 0.008)], name="jerkin", sq=0.35, round_=(False, False)),
                "chest", V2["leather"], line=0)
    # musket in the near hand, built pointing forward with the arm hanging
    h = fig.W["handR"]; g = Vector((h.x + 0.02, h.y - 0.03, h.z - 0.10))
    stock = [(-0.46, -0.20), (-0.44, 0.04), (-0.14, 0.055), (0.86, 0.035), (0.86, -0.045), (0.10, -0.065), (-0.10, -0.08), (-0.30, -0.24)]
    fig.add(slab(stock, 0.085, at=g, bevel=0.012, name="stock"), "handR", V2["wood"], line=0.016)
    bc = V2["cursed"] if t >= 3 else V2["iron"]
    fig.add(loft([(-0.12, 0.046, 0.046), (1.36, 0.038, 0.038)], seg=7, axis="x", at=(g.x, g.y, g.z + 0.075), name="barrel"), "handR", bc,
            metal=True, glow=0.35 if t >= 3 else 0.0, line=0.016)
    fig.add(orb(0.056, (g.x + 1.37, g.y, g.z + 0.075), (0.7, 1, 1), seg=7, name="muzzle"), "handR", bc, metal=True, glow=0.35 if t >= 3 else 0.0, line=0.012)
    for x in (0.36, 0.80):
        fig.add(orb(0.065, (g.x + x, g.y, g.z + 0.035), (0.45, 1.0, 1.3), seg=7, name="band"), "handR", trim, metal=True, line=0.01)
    fig.add(block((0.12, 0.035, 0.07), (g.x + 0.0, g.y - 0.045, g.z + 0.05), bevel=0.01, name="lock"), "handR", trim, metal=True, line=0.01)
    fig.add(cone((g.x - 0.06, g.y - 0.045, g.z + 0.07), (g.x - 0.02, g.y - 0.045, g.z + 0.17), 0.025, 0.012, seg=5, name="hammer"), "handR",
            V2["steel"], metal=True, line=0.01)
    # muzzle flash + sparks (hit frame) and smoke (after)
    M = Vector((g.x + 1.40, g.y, g.z + 0.075))
    toggle(fig, "flash", "handR", M, 0)
    star = []
    for i in range(16):
        a = math.radians(i * 22.5); R = 0.33 if i % 2 == 0 else 0.12
        star.append((0.24 + R * 1.4 * math.cos(a), R * math.sin(a)))
    fig.add(slab(star, 0.02, at=M, name="flash"), "flash", (1.0, 0.80, 0.36), glow=1.0)
    fig.add(slab([(0.10 + (x - 0.26) * 0.5 + 0.13, z * 0.5) for x, z in star], 0.02, at=(M.x, M.y - 0.03, M.z), name="core"), "flash",
            (1.0, 0.97, 0.86), glow=1.0)
    for (x, z, s) in ((0.78, 0.10, 0.035), (0.88, -0.06, 0.03), (0.74, -0.16, 0.025), (0.96, 0.03, 0.022)):
        fig.add(orb(s, (M.x + x, M.y, M.z + z), seg=5), "flash", (1.0, 0.72, 0.30), glow=1.0)
    toggle(fig, "smoke", "handR", M, 0)
    for (x, z, s) in ((0.10, 0.05, 0.11), (0.25, 0.14, 0.14), (0.40, 0.09, 0.10), (0.20, 0.28, 0.09)):
        fig.add(orb(s, (M.x + x, M.y, M.z + z), seg=8, name="smoke"), "smoke", (0.84, 0.80, 0.80), glow=0.5, line=0.01)
    return fig


def _tb_port(elev=40):
    return tb_gun(dict(chest=2, head=-1, uaR=4, laR=62, uaL=(74, 0, -38), laL=14, thL=10, snL=-16, thR=-9, snR=-10, brow=0), elev)


def tb_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _tb_port()
    d.update(chest=2 + 1.5 * s, head=(-1 - 1.0 * s, 0, 9 * c), uaR=4 + 2 * s, laR=62 + 3 * c,
             squash=(1 - 0.006 * s, 1 + 0.012 * s), tail=(4, t))
    return tb_gun(d, 40 + 3 * c)


def tb_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _tb_port()
    d.update(thL=27 * s, snL=-8 - 42 * max(0, c), thR=-27 * s, snR=-8 - 42 * max(0, -c), chest=7 + 2.5 * math.cos(2 * p),
             head=-4 - 2 * math.cos(2 * p), uaR=6 - 6 * s, laR=60 + 5 * c, uaL=(72 + 4 * s, 0, -38),
             root=(0, 0.02 * math.cos(2 * p)), tail=(26, t * 2))
    return tb_gun(d, 41 + 4 * math.cos(2 * p + 0.9))


def tb_attack(t, i, n):
    G = dict(_tb_port(), tail=(0, 0.0))
    aimp = dict(chest=7, hips=1, head=5, uaR=72, laR=100, uaL=(100, 0, -34), laL=5, thL=22, snL=-22, thR=-20, snR=-6, brow=-10,
                root=(0.03, 0), tail=(8, 0.2))
    aim = tb_gun(dict(aimp), 7)
    aim2 = tb_gun(dict(aimp, chest=9, head=9, squash=(1.02, 0.98), root=(0.05, 0), brow=-14), 6)
    fire = tb_gun(dict(aimp, chest=1, head=2, uaR=68, laR=102, root=(-0.03, 0), squash=(0.98, 1.03), brow=-16,
                       vis=dict(flash=1, m_open=1, m_shut=0), tail=(-30, 0.4)), 10)
    recoil = tb_gun(dict(aimp, chest=-9, hips=-3, head=-6, uaR=70, laR=104, uaL=(92, 0, -34), laL=14, thL=26, snL=-14, thR=-24, snR=-12,
                         root=(-0.12, 0), brow=6, vis=dict(smoke=1.0, m_open=1, m_shut=0), tail=(-40, 0.6)), 30)
    settle = tb_gun(dict(aimp, chest=-3, hips=-1, head=-2, uaR=40, laR=90, uaL=(82, 0, -36), laL=12, root=(-0.08, 0), brow=0,
                         vis=dict(smoke=1.45), tail=(-10, 0.8)), 36)
    return keys([(0.0, G), (0.26, aim), (0.44, aim2), (0.56, fire), (0.68, recoil), (0.80, settle), (1.0, dict(G, tail=(0, 1.0)))], t)


def tb_hit(t, i, n):
    G = _tb_port()
    back = tb_gun(dict(G, chest=-18, head=-15, hips=-5, root=(-0.10, 0), squash=(1.06, 0.93), uaR=-30, laR=74, uaL=(40, 0, -30), brow=14,
                       vis=dict(m_open=1, m_shut=0), tail=(-30, 0.2)), 62)
    mid = tb_gun(dict(G, chest=-6, root=(-0.05, 0)), 48)
    return keys([(0.0, back), (0.45, mid), (1.0, G)], t)


def tb_die(t, i, n):
    G = _tb_port()
    reel = tb_gun(dict(G, chest=-22, head=-20, hips=-8, root=(-0.10, 0), uaR=-60, laR=50, uaL=(-30, 0, 0), laL=30, brow=16,
                       vis=dict(m_open=1, m_shut=0), tail=(-30, 0.2)), 75)
    fall = tb_gun(dict(reel, rootrot=-60, root=(-0.20, 0.10), free=1, thL=30, snL=-50, thR=10, snR=-30, uaR=-30, laR=30, uaL=(-110, 0, 0)), 40)
    down = tb_gun(dict(fall, rootrot=-90, root=(-0.30, 0.24), chest=-3, head=-4, thL=12, snL=-18, thR=2, snR=-6, uaR=6, laR=8, uaL=(-150, 0, 0),
                       laL=10, vis=dict(m_open=0, m_shut=1), brow=0, tail=(0, 0.5)), 2)
    bounce = tb_gun(dict(down, root=(-0.30, 0.30), rootrot=-86), 8)
    return keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, down), (1.0, down)], t)


def _tb(t):
    register(dict(id="torchbow" + ("" if t == 1 else "_t%d" % t), tier=t, v2=blackpowder_fig,
                  anims=dict(idle=tb_idle, walk=tb_walk, attack=tb_attack, hit=tb_hit, die=tb_die)))


for _t in (1, 2, 3):
    _tb(_t)
