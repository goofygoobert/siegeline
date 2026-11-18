from kit import *
# Harpooner (v2) — lean, tall old whaler: mustard oilskin coat, sou'wester with a long drooping back brim, grey beard,
# a long barbed harpoon gun braced on the shoulder and held level, a coil of line at the hip.
# Silhouette hook: the very long level harpoon gun shaft (longer than he is wide) with the barbed head out front.
# Attack: brace low and hold the aim, FIRE (flash, the harpoon leaves the gun, line pays out), hard recoil, settle.

HP_LEAN = 6
HP_OIL = (0.86, 0.64, 0.20)
HP_OIL_DK = (0.66, 0.46, 0.14)
HP_ROPE = (0.82, 0.71, 0.50)
HP_GREY = (0.74, 0.72, 0.68)


def hp_num(d, k):
    v = d.get(k, 0.0)
    return v if isinstance(v, (int, float)) else v[0]


def hp_gun(d, elev):
    """Set the wrist so the gun points at a world elevation (deg above +X), whatever the body is doing."""
    d["handR"] = elev + d.get("rootrot", 0) + hp_num(d, "hips") + hp_num(d, "chest") + HP_LEAN - hp_num(d, "uaR") - hp_num(d, "laR")
    return d


def hp_torus(R, r, c, axis="y", seg=20, rs=7, name="coil"):
    bm = bmesh.new(); rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg; ring = []
        for j in range(rs):
            b = 2 * math.pi * j / rs
            rr = R + r * math.cos(b); h = r * math.sin(b)
            if axis == "y":
                p = (c[0] + rr * math.cos(a), c[1] + h, c[2] + rr * math.sin(a))
            else:
                p = (c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), c[2] + h)
            ring.append(bm.verts.new(p))
        rings.append(ring)
    for i in range(seg):
        for j in range(rs):
            a, b = rings[i], rings[(i + 1) % seg]
            bm.faces.new((a[j], b[j], b[(j + 1) % rs], a[(j + 1) % rs]))
    return _obj(name, bm)


def hp_brim(r, c, base):
    """Sou'wester brim: short and slightly turned up at the front, long and drooping down the back of the neck."""
    bm = bmesh.new(); ot = []; ob = []; it = []; ib = []
    n = 18
    for i in range(n):
        a = 2 * math.pi * i / n; ca = math.cos(a); sa = math.sin(a)
        back = (1 - ca) / 2
        k = 1.30 + 0.42 * back + 0.08 * abs(sa)
        z = 0.08 * max(ca, 0) - 0.42 * back ** 1.5
        ot.append(bm.verts.new((c.x + ca * k * r, sa * k * r * 0.96, base + z * r)))
        ob.append(bm.verts.new((c.x + ca * k * r * 0.97, sa * k * r * 0.93, base + z * r - 0.05)))
        it.append(bm.verts.new((c.x + ca * 0.86 * r, sa * 0.86 * r, base + 0.02)))
        ib.append(bm.verts.new((c.x + ca * 0.86 * r, sa * 0.86 * r, base - 0.05)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((it[i], ot[i], ot[j], it[j]))
        bm.faces.new((ot[i], ob[i], ob[j], ot[j]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    bm.faces.new(it); bm.faces.new(ib[::-1])
    return _obj("brim", bm)


def harpooner_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("hp%d" % t, INK_CREW, h=1.95)
    trim = V2["gold"] if t >= 3 else V2["brass"]
    C = dict(skin=(0.82, 0.58, 0.44), body=HP_OIL, sleeve=HP_OIL, arm=HP_OIL, legs=V2["navy_dk"], belt=V2["tar"],
             boots=V2["tar"], cuff=V2["tar"], nose=(0.80, 0.46, 0.38), hand=(0.82, 0.58, 0.44))
    P = dict(hip=0.82, chest_h=0.64, wy=0.29, wx=0.21, shoulder=0.36, head_r=0.28, belly=0.88, arm_r=0.10, upper_arm=0.30,
             lower_arm=0.28, leg_r=0.11, thigh=0.35, shin=0.33, hip_w=0.14, lean=HP_LEAN, neck_x=0.04)
    body(fig, P, C); fists(fig, C, 0.12); boots(fig, C, length=0.34, h=0.18)
    head_crew(fig, C, beard=HP_GREY, nose=1.25, jaw=0.95, brow=(0.42, 0.40, 0.38))
    hc = fig.head_c; r = fig.head_r; hip = fig.hip; wx = P["wx"]; wy = P["wy"]; ch = P["chest_h"]
    # sou'wester: low dome crown + long back brim, a chin strap
    base = hc.z + r * 0.58
    fig.add(loft([(base - 0.04, r * 0.98, r * 0.98), (base + r * 0.30, r * 0.88, r * 0.90), (base + r * 0.56, r * 0.62, r * 0.64)],
                 seg=14, at=(hc.x - 0.01, 0, 0), round_=(False, True), name="crown"), "head", HP_OIL_DK)
    fig.add(hp_brim(r, hc, base), "head", HP_OIL, flat=True)
    fig.add(loft([(base - 0.02, r * 1.0, r * 1.0), (base + 0.05, r * 0.98, r * 0.98)], seg=14, at=(hc.x - 0.01, 0, 0),
                 round_=(False, False), name="hatband"), "head", V2["tar"] if t < 3 else V2["gold"], metal=t >= 3, line=0.01)
    # long oilskin coat: flared skirt to the knee, split tails, high collar, toggles
    fig.add(loft([(hip + 0.13, wx * 1.06, wy * 1.04), (hip - 0.10, wx * 1.24, wy * 1.12, -0.01), (hip - 0.30, wx * 1.40, wy * 1.18, -0.04)],
                 name="skirt", sq=0.3, round_=(False, False)), "hips", HP_OIL)
    for i, y in enumerate((-0.13, 0.13)):
        chain(fig, "coat%d" % i, "hips", (-wx * 1.22, y, hip - 0.24), [0.16, 0.12], 0.10, HP_OIL_DK, (-0.35, 0, -1), flat=0.8, taper=0.85,
              sway=0.5, phase=0.3 * i)
    fig.add(loft([(hip + ch * 0.86, wx * 0.92, wy * 0.84), (hip + ch * 1.02, wx * 0.78, wy * 0.70)], name="collar", round_=(False, False), sq=0.2),
            "chest", HP_OIL_DK, line=0.012)
    for k in (0.28, 0.50, 0.72):
        fig.add(block((0.04, 0.09, 0.03), (wx * 1.10 + 0.04, -0.03, hip + ch * k), bevel=0.01, name="toggle"), "chest",
                trim if t >= 3 else V2["wood_dk"], metal=t >= 3, line=0.008)
    # coiled line on the near hip
    cc = (-0.08, -wy - 0.09, hip - 0.02)
    for k, rr in ((1.0, 0.03), (0.78, 0.03), (0.56, 0.03), (0.34, 0.03)):
        fig.add(hp_torus(0.12 * k + 0.01, rr, (cc[0], cc[1] - 0.012 * k, cc[2]), axis="y", name="coil"), "hips", HP_ROPE, line=0.01)
    chain(fig, "lineend", "hips", (cc[0] + 0.06, cc[1], cc[2] - 0.12), [0.12, 0.10], 0.03, HP_ROPE, (0.2, 0, -1), sway=0.6, phase=0.4, line=0.008)
    if t >= 2:      # leather bracers, red scarf with a trailing end
        for s, y in (("L", 1), ("R", -1)):
            sy = y * P["shoulder"]; sz = fig.sh_z; ua = P["upper_arm"]; la = P["lower_arm"]
            fig.add(loft([(sz - ua - la * 0.88, 0.125, 0.125), (sz - ua - la * 0.45, 0.13, 0.13)], seg=9, at=(0, sy, 0), name="bracer", sq=0.3,
                         round_=(False, False)), "la" + s, V2["leather"], line=0.01)
            fig.add(loft([(sz - ua - la * 0.86, 0.13, 0.13), (sz - ua - la * 0.80, 0.13, 0.13)], seg=9, at=(0, sy, 0), name="bstrap",
                         round_=(False, False)), "la" + s, trim, metal=True, line=0)
        n = fig.neck
        fig.add(loft([(n.z - 0.06, 0.17, 0.18), (n.z + 0.06, 0.15, 0.16)], seg=10, at=(n.x, 0, 0), name="scarf"), "chest", V2["red"], line=0.012)
        chain(fig, "scarf", "chest", (n.x - 0.15, -0.06, n.z - 0.02), [0.15, 0.13], 0.06, V2["red"], (-1, -0.1, -0.5), sway=1.0, phase=0.1)
    # harpoon gun in the near hand, built pointing forward with the arm hanging; butt braces on the shoulder
    h = fig.W["handR"]; g = Vector((h.x + 0.02, h.y - 0.04, h.z - 0.10))
    stock = [(-0.56, -0.08), (-0.54, 0.08), (-0.20, 0.07), (0.16, 0.055), (0.16, -0.035), (-0.06, -0.05), (-0.14, -0.20), (-0.24, -0.20), (-0.24, -0.07)]
    fig.add(slab(stock, 0.09, at=g, bevel=0.012, name="stock"), "handR", V2["wood"], line=0.016)
    bz = g.z + 0.07
    fig.add(loft([(-0.10, 0.058, 0.058), (1.12, 0.050, 0.050)], seg=8, axis="x", at=(g.x, g.y, bz), name="barrel"), "handR", V2["iron"],
            metal=True, line=0.016)
    fig.add(loft([(1.06, 0.075, 0.075), (1.16, 0.08, 0.08)], seg=8, axis="x", at=(g.x, g.y, bz), round_=(False, False), name="muzzle"), "handR",
            trim if t >= 3 else V2["iron"], metal=True, line=0.012)
    fig.add(block((0.40, 0.08, 0.07), (g.x + 0.56, g.y, bz - 0.07), bevel=0.015, name="foregrip"), "handR", V2["wood_dk"], line=0.012)
    fig.add(block((0.12, 0.04, 0.08), (g.x + 0.04, g.y - 0.05, bz - 0.01), bevel=0.01, name="lock"), "handR", V2["steel"], metal=True, line=0.01)
    bands = (0.0, 0.34, 0.78, 1.02) if t >= 3 else (0.34, 0.78)
    for x in bands:
        fig.add(loft([(x - 0.025, 0.068, 0.068), (x + 0.025, 0.068, 0.068)], seg=8, axis="x", at=(g.x, g.y, bz), round_=(False, False),
                     name="band"), "handR", trim if t >= 3 else V2["steel"], metal=True, line=0.008)
    # the loaded harpoon: shaft out of the muzzle + big barbed head (hidden from the shot frame on)
    M = Vector((g.x + 1.16, g.y, bz))
    toggle(fig, "harp", "handR", M, 1)
    fig.add(loft([(-0.10, 0.03, 0.03), (0.24, 0.028, 0.028)], seg=7, axis="x", at=(M.x, M.y, M.z), name="shaft"), "harp", V2["wood_dk"], line=0.012)
    head = [(0.0, 0.05), (0.14, 0.05), (0.06, 0.20), (0.22, 0.20), (0.52, 0.0), (0.22, -0.20), (0.06, -0.20), (0.14, -0.05), (0.0, -0.05)]
    hcol = V2["cursed"] if t >= 3 else V2["steel"]
    fig.add(slab(head, 0.05, at=(M.x + 0.20, M.y, M.z), bevel=0.008, name="harphead"), "harp", hcol, metal=True,
            glow=0.35 if t >= 3 else 0.0, line=0.014)
    # muzzle flash (shot frame), line paying out + smoke (after)
    toggle(fig, "flash", "handR", M, 0)
    star = []
    for i in range(16):
        a = math.radians(i * 22.5); R = 0.34 if i % 2 == 0 else 0.12
        star.append((0.24 + R * 1.4 * math.cos(a), R * math.sin(a)))
    fig.add(slab(star, 0.02, at=M, name="flash"), "flash", (1.0, 0.80, 0.36), glow=1.0)
    fig.add(slab([(0.10 + (x - 0.26) * 0.5 + 0.13, z * 0.5) for x, z in star], 0.02, at=(M.x, M.y - 0.03, M.z), name="core"), "flash",
            (1.0, 0.97, 0.86), glow=1.0)
    for (x, z, s) in ((0.80, 0.10, 0.035), (0.90, -0.06, 0.03), (0.74, -0.16, 0.025)):
        fig.add(orb(s, (M.x + x, M.y, M.z + z), seg=5), "flash", (1.0, 0.72, 0.30), glow=1.0)
    toggle(fig, "payout", "handR", M, 0)
    fig.add(cone((M.x, M.y, M.z), (M.x + 0.95, M.y, M.z + 0.05), 0.016, 0.014, seg=5, name="payline"), "payout", HP_ROPE, line=0.006)
    toggle(fig, "smoke", "handR", M, 0)
    for (x, z, s) in ((0.10, 0.05, 0.11), (0.25, 0.14, 0.14), (0.40, 0.09, 0.10), (0.20, 0.28, 0.09)):
        fig.add(orb(s, (M.x + x, M.y, M.z + z), seg=8, name="smoke"), "smoke", (0.84, 0.80, 0.80), glow=0.5, line=0.01)
    return fig


def _hp_port(elev=1):
    return hp_gun(dict(chest=1, head=-2, uaR=30, laR=80, uaL=(52, 0, -36), laL=22, thL=9, snL=-14, thR=-8, snR=-9, brow=4), elev)


def hp_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _hp_port()
    d.update(chest=1 + 1.4 * s, head=(-2 - 1.0 * s, 0, 6 * c), uaR=30 + 2 * s, laR=80 + 2 * c,
             squash=(1 - 0.006 * s, 1 + 0.012 * s), tail=(4, t))
    return hp_gun(d, 1 + 2 * c)


def hp_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _hp_port()
    d.update(thL=25 * s, snL=-8 - 40 * max(0, c), thR=-25 * s, snR=-8 - 40 * max(0, -c), chest=5 + 2.0 * math.cos(2 * p),
             head=-3 - 2 * math.cos(2 * p), uaR=30 - 4 * s, laR=80 + 3 * c, uaL=(52 + 4 * s, 0, -36),
             root=(0, 0.02 * math.cos(2 * p)), tail=(24, t * 2))
    return hp_gun(d, 2 + 3 * math.cos(2 * p + 0.9))


def hp_attack(t, i, n):
    G = dict(_hp_port(), tail=(0, 0.0))
    bracep = dict(chest=11, hips=2, head=8, uaR=36, laR=82, uaL=(58, 0, -36), laL=22, thL=30, snL=-36, thR=-26, snR=-14, brow=-12,
                  root=(0.04, 0), tail=(10, 0.2))
    brace = hp_gun(dict(bracep, squash=(1.03, 0.97)), -2)
    hold = hp_gun(dict(bracep, chest=13, head=10, squash=(1.05, 0.95), root=(0.06, 0), brow=-16), -3)
    fire = hp_gun(dict(bracep, chest=4, head=4, root=(-0.02, 0), squash=(0.97, 1.04), brow=-16,
                       vis=dict(flash=1, harp=0, m_open=1, m_shut=0), tail=(-30, 0.4)), 4)
    recoil = hp_gun(dict(bracep, chest=-16, hips=-5, head=-10, uaR=26, laR=92, uaL=(46, 0, -36), laL=30, thL=34, snL=-16, thR=-30, snR=-16,
                         root=(-0.20, 0), squash=(1.04, 0.97), brow=8, vis=dict(smoke=1.0, payout=1, harp=0, m_open=1, m_shut=0), tail=(-44, 0.6)), 26)
    settle = hp_gun(dict(bracep, chest=-4, hips=-1, head=-3, uaR=30, laR=84, thL=18, snL=-20, thR=-14, snR=-10, root=(-0.10, 0), brow=2,
                         vis=dict(smoke=1.45, harp=0), tail=(-12, 0.8)), 12)
    end = dict(G, tail=(0, 1.0), vis=dict(harp=0))
    return keys([(0.0, G), (0.24, brace), (0.44, hold), (0.56, fire), (0.68, recoil), (0.82, settle), (1.0, end)], t)


def hp_hit(t, i, n):
    G = _hp_port()
    back = hp_gun(dict(G, chest=-18, head=-15, hips=-5, root=(-0.10, 0), squash=(1.06, 0.93), uaR=20, laR=90, brow=14,
                       vis=dict(m_open=1, m_shut=0, eyes_shut=1), tail=(-30, 0.2)), 22)
    mid = hp_gun(dict(G, chest=-6, root=(-0.05, 0)), 8)
    return keys([(0.0, back), (0.45, mid), (1.0, G)], t)


def hp_die(t, i, n):
    G = _hp_port()
    reel = hp_gun(dict(G, chest=-22, head=-20, hips=-8, root=(-0.10, 0), uaR=0, laR=60, uaL=(-30, 0, 0), laL=30, brow=16,
                       vis=dict(m_open=1, m_shut=0, eyes_shut=1), tail=(-30, 0.2)), 40)
    fall = hp_gun(dict(reel, rootrot=-60, root=(-0.22, 0.10), free=1, thL=30, snL=-50, thR=10, snR=-30, uaR=-20, laR=30, uaL=(-110, 0, 0)), 30)
    down = hp_gun(dict(fall, rootrot=-90, root=(-0.34, 0.24), chest=-3, head=-4, thL=12, snL=-18, thR=2, snR=-6, uaR=10, laR=6, uaL=(-150, 0, 0),
                       laL=10, vis=dict(m_open=0, m_shut=1, eyes_shut=1), brow=0, squash=(1.10, 0.86), tail=(0, 0.5)), 2)
    bounce = hp_gun(dict(down, root=(-0.34, 0.30), rootrot=-86, squash=(0.96, 1.05)), 7)
    rest = dict(down, squash=(1.0, 1.0))
    return keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, rest), (1.0, rest)], t)


def _hp(t):
    register(dict(id="harpooner" + ("" if t == 1 else "_t%d" % t), tier=t, v2=harpooner_fig,
                  anims=dict(idle=hp_idle, walk=hp_walk, attack=hp_attack, hit=hp_hit, die=hp_die)))


for _t in (1, 2, 3):
    _hp(_t)
