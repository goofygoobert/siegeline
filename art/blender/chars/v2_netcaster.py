from kit import *
# Netcaster (v2) — stocky fisherwoman: orange headscarf, faded blue shirt with rolled sleeves, green bib waders and
# wader boots, a brass hoop earring. She swings a weighted cast-net round over her head.
# Silhouette hook: the wide round net disc (cords + weight balls on the rim) spinning above her head.
# Attack: winds the net round faster and back (held), THROWS forward on frame 5 (the net leaves her hand), follow-through.

NC_LEAN = 3
NC_SCARF = (0.90, 0.50, 0.18)
NC_SCARF_DK = (0.72, 0.36, 0.12)
NC_SHIRT = (0.44, 0.58, 0.72)
NC_WADER = (0.24, 0.34, 0.27)
NC_WADER_DK = (0.16, 0.23, 0.19)
NC_CORD = (0.90, 0.82, 0.62)
NC_TWINE = (0.30, 0.22, 0.15)
NC_LEAD = (0.30, 0.31, 0.36)
NC_R = 0.74          # net radius
NC_SPOKES = 12


def nc_num(d, k):
    v = d.get(k, 0.0)
    return v if isinstance(v, (int, float)) else v[0]


def nc_hand(d, elev=0.0):
    """Keep the casting hand's frame level in the world (so the net disc keeps its designed tilt)."""
    d["handR"] = elev + d.get("rootrot", 0) + nc_num(d, "hips") + nc_num(d, "chest") + NC_LEAN - nc_num(d, "uaR") - nc_num(d, "laR")
    return d


def nc_torus(R, r, c, seg=28, rs=6, dz=0.0, name="ring"):
    """Horizontal ring (axis Z) of radius R, tube radius r, centre c, dropped by dz."""
    bm = bmesh.new(); rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg; ring = []
        for j in range(rs):
            b = 2 * math.pi * j / rs
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), c[2] - dz + r * math.sin(b))))
        rings.append(ring)
    for i in range(seg):
        for j in range(rs):
            a, b = rings[i], rings[(i + 1) % seg]
            bm.faces.new((a[j], b[j], b[(j + 1) % rs], a[(j + 1) % rs]))
    return _obj(name, bm)


def nc_net(fig, joint, c, R, t, sag=0.10, scale=1.0):
    """A weighted cast-net as a shallow dish in the joint's horizontal plane: dark mesh fill, light cords (spokes and
    rings), a heavier rim and weight balls (cork floats on t2, brass on t3, glowing cursed rim on t3)."""
    R = R * scale
    rimc = V2["cursed"] if t >= 3 else NC_CORD
    wc = V2["brass"] if t >= 3 else NC_LEAD

    def zat(k):          # dish: rim hangs lower than the hub
        return c[2] - sag * scale * k * k

    # diamond mesh: two sets of parallel cords at +-45 deg, clipped to the dish (reads as netting, not a wheel)
    step = R / 3.4
    for ang in (45, -45):
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        k = -3
        while k <= 3:
            o = k * step
            half = math.sqrt(max(R * R * 0.97 - o * o, 0.0))
            if half > 0.05:
                pts = []
                for u in (-half, half):
                    x = -sa * o + ca * u; y = ca * o + sa * u
                    rk = math.sqrt(x * x + y * y) / R
                    pts.append((c[0] + x, c[1] + y, zat(rk) + 0.01))
                mid = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2, zat(abs(o) / R) + 0.01)
                for p0, p1 in ((pts[0], mid), (mid, pts[1])):
                    fig.add(cone(p0, p1, 0.02 * scale, 0.02 * scale, seg=5, name="cord"), joint, NC_TWINE, line=0.0)
            k += 1
    fig.add(nc_torus(R * 0.5, 0.018 * scale, (c[0], c[1], zat(0.5) + 0.01), name="cord"), joint, NC_TWINE, line=0.0)
    fig.add(nc_torus(R, 0.036 * scale, (c[0], c[1], zat(1.0) + 0.01), name="rim"), joint, rimc, glow=0.35 if t >= 3 else 0.0,
            metal=t >= 3, line=0.01)
    # hub knot and the hand line
    fig.add(orb(0.06 * scale, (c[0], c[1], c[2] + 0.03), seg=8, name="hub"), joint, NC_CORD, line=0.01)
    # weights on the rim (t2 adds cork floats between them)
    for i in range(NC_SPOKES):
        a = 2 * math.pi * i / NC_SPOKES
        p = (c[0] + R * math.cos(a), c[1] + R * math.sin(a), zat(1.0) - 0.02)
        fig.add(orb(0.062 * scale, p, seg=8, name="weight"), joint, wc, metal=True, line=0.01)
        if t >= 2:
            a2 = a + math.pi / NC_SPOKES; k = 0.86
            q = (c[0] + R * k * math.cos(a2), c[1] + R * k * math.sin(a2), zat(k) + 0.03)
            fig.add(orb(0.055 * scale, q, (1.2, 1.2, 0.8), seg=8, name="cork"), joint, (0.80, 0.56, 0.30), line=0.008)
    if t >= 3:
        fig.add(nc_torus(R * 1.03, 0.05 * scale, (c[0], c[1], zat(1.0) + 0.01), seg=28, rs=5, name="rimglow"), joint, V2["cursed"], glow=1.0, line=0.0)


def netcaster_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("nc%d" % t, INK_CREW, h=1.8)
    C = dict(skin=(0.88, 0.62, 0.47), body=NC_SHIRT, sleeve=NC_SHIRT, arm=(0.88, 0.62, 0.47), legs=NC_WADER, belt=V2["leather"],
             boots=NC_WADER_DK, cuff=NC_WADER_DK, shin=NC_WADER, nose=(0.86, 0.52, 0.42))
    P = dict(hip=0.60, chest_h=0.60, wy=0.39, wx=0.29, shoulder=0.43, head_r=0.30, belly=1.12, arm_r=0.125, upper_arm=0.27,
             lower_arm=0.27, leg_r=0.15, thigh=0.25, shin=0.23, hip_w=0.18, lean=NC_LEAN, neck_x=0.03)
    body(fig, P, C); fists(fig, C, 0.135); boots(fig, C, length=0.36, h=0.22, cuff=True)
    head_crew(fig, C, nose=0.95, jaw=1.02, brow=(0.30, 0.17, 0.10))
    hc = fig.head_c; r = fig.head_r; hip = fig.hip; wx = P["wx"]; wy = P["wy"]; ch = P["chest_h"]
    ex = hc.x + r * 0.90
    # rosy cheeks, fringe of hair, hoop earring
    for y in (-1, 1):
        fig.add(orb(r * 0.16, (ex - r * 0.10, y * r * 0.58, hc.z - r * 0.22), (0.5, 1.0, 0.8), seg=8, name="cheek"), "head", (0.92, 0.50, 0.42), line=0)
    fig.add(orb(r * 0.5, (hc.x + r * 0.55, 0, hc.z + r * 0.52), (0.55, 1.6, 0.42), seg=10, name="fringe"), "head", V2["hair"], line=0.01)
    hoop = nc_torus(r * 0.16, 0.016, (0, 0, 0), seg=12, rs=5, name="hoop")
    hoop.data.transform(Matrix.Translation((hc.x - r * 0.02, -r * 1.02, hc.z - r * 0.40)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    fig.add(hoop, "head", V2["gold"] if t >= 3 else V2["brass"], metal=True, line=0)
    # headscarf: cap tied at the back with a knot and two tails
    fig.add(loft([(hc.z + r * 0.40, r * 1.06, r * 1.06, -0.01), (hc.z + r * 0.66, r * 1.0, r * 1.03, -0.03), (hc.z + r * 0.88, r * 0.70, r * 0.74, -0.05)],
                 seg=14, at=(hc.x, 0, 0), round_=(False, True), name="scarf"), "head", NC_SCARF)
    fig.add(loft([(hc.z + r * 0.34, r * 1.09, r * 1.09), (hc.z + r * 0.48, r * 1.09, r * 1.09)], seg=14, at=(hc.x, 0, 0), round_=(False, False),
                 name="scarfband"), "head", NC_SCARF_DK)
    for (dx, dy, dz) in ((0.45, -0.70, 0.70), (0.0, -0.84, 0.74), (-0.45, -0.70, 0.72), (0.15, -0.44, 0.98)):
        fig.add(orb(r * 0.08, (hc.x + r * dx, r * dy, hc.z + r * dz), seg=6, name="dot"), "head", V2["white"], glow=0.6, line=0)
    kn = (hc.x - r * 1.04, 0.0, hc.z + r * 0.40)
    fig.add(orb(r * 0.2, kn, name="knot", seg=8), "head", NC_SCARF, line=0.012)
    chain(fig, "tailA", "head", kn, [0.15, 0.13], 0.06, NC_SCARF, (-1, 0, -0.5), sway=1.0)
    chain(fig, "tailB", "head", kn, [0.12, 0.10], 0.05, NC_SCARF_DK, (-1, 0, -1.0), sway=0.8, phase=0.3)
    # rolled sleeves: a fat cuff roll above the elbow
    for s, y in (("L", 1), ("R", -1)):
        sy = y * P["shoulder"]; sz = fig.sh_z; ua = P["upper_arm"]
        fig.add(loft([(sz - ua * 0.95, 0.155, 0.155), (sz - ua * 0.70, 0.16, 0.16)], seg=10, at=(0, sy, 0), name="roll"), "ua" + s,
                (0.62, 0.74, 0.84), line=0.012)
    # wader bib on the chest with shoulder straps
    bib = loft([(hip + 0.08, wx * 1.00 * 1.12, wy * 1.0), (hip + ch * 0.55, wx * 1.06 * 1.12, wy * 0.98, 0.015)], name="bib", sq=0.35,
               round_=(False, False))
    fig.add(bib, "chest", NC_WADER)
    for y in (-0.18, 0.18):
        fig.add(block((0.05, 0.06, ch * 0.42), (wx * 1.12, y, hip + ch * 0.74), rot=(-8, "Y"), bevel=0.01, name="strap"), "chest", NC_WADER, line=0.01)
        fig.add(orb(0.035, (wx * 1.16 + 0.02, y, hip + ch * 0.55), seg=6, name="clip"), "chest", V2["gold"] if t >= 3 else V2["brass"], metal=True, line=0.006)
    if t >= 2:      # oilskin apron over the waders
        fig.add(loft([(hip + 0.14, wx * 1.10, wy * 1.06, 0.01), (hip - 0.10, wx * 1.24, wy * 1.10, 0.02), (hip - 0.30, wx * 1.30, wy * 1.08, 0.03)],
                     name="apron", sq=0.3, round_=(False, False)), "hips", (0.86, 0.64, 0.20))
        fig.add(loft([(hip + 0.13, wx * 1.12, wy * 1.08), (hip + 0.19, wx * 1.12, wy * 1.08)], name="apronband", sq=0.3, round_=(False, False)),
                "hips", V2["leather"], line=0)
    # the cast-net: held at the hub by the raised near hand, spinning on its own pivots
    h = fig.W["handR"]
    hub = Vector((h.x - 0.08, h.y + 0.38, h.z + 0.70))
    toggle(fig, "net", "handR", h, 1)
    fig.joint("ntilt", hub, "net", 1)
    fig.joint("nspin", hub, "ntilt", 1)
    fig.add(cone((h.x, h.y, h.z - 0.02), (hub.x, hub.y, hub.z + 0.02), 0.016, 0.014, seg=5, name="handline"), "net", NC_CORD, line=0.006)
    nc_net(fig, "nspin", hub, NC_R, t)
    # the thrown net: a wide fan opening out in front (shown on the throw frame only), on the root
    T = Vector((1.78, -0.10, 1.05))
    toggle(fig, "cast", "root", T, 0)
    fig.joint("ctilt", T, "cast", 1)
    nc_net(fig, "ctilt", T, NC_R, t, sag=0.04, scale=0.86)
    for i, (dz, ln) in enumerate(((0.12, 0.34), (-0.14, 0.30), (0.0, 0.44))):     # speed streaks behind the throw
        fig.add(slab([(0, -0.012), (ln, -0.004), (ln, 0.004), (0, 0.012)], 0.01, at=(T.x - 0.62 - ln, T.y - 0.25, T.z + dz), name="streak"),
                "cast", (1.0, 0.96, 0.84), glow=1.0)
    return fig


NC_TILT = 42         # net disc tipped toward the camera so it reads as a wide disc


def _nc_base():
    return dict(chest=2, head=(-3, 0, 0), uaR=(186, 0, 0), laR=4, uaL=(30, 0, 0), laL=60, thL=10, snL=-14, thR=-9, snR=-10,
                brow=-2, ntilt=(6, NC_TILT, 0))


def nc_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _nc_base()
    d.update(chest=2 + 1.6 * s, head=(-3 - 1.2 * s, 0, 5 * c), uaR=(186 + 3 * c, 3 * s, 0), laR=4 + 3 * s, laL=60 + 4 * c,
             squash=(1 - 0.008 * s, 1 + 0.014 * s), ntilt=(6 + 4 * s, NC_TILT + 4 * c, 0), nspin=(0, 0, 180 * t), tail=(6, t))
    return nc_hand(d)


def nc_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _nc_base()
    d.update(thL=24 * s, snL=-8 - 38 * max(0, c), thR=-24 * s, snR=-8 - 38 * max(0, -c), chest=7 + 2.5 * math.cos(2 * p),
             head=(-5 - 2 * math.cos(2 * p), 0, 0), uaR=(184 + 3 * c, 3 * s, 0), uaL=(30 - 22 * s, 0, 0), laL=55,
             root=(0, 0.022 * math.cos(2 * p)), ntilt=(8 + 3 * math.cos(2 * p), NC_TILT + 3 * s, 0), nspin=(0, 0, 180 * t), tail=(24, t * 2))
    return nc_hand(d)


def nc_attack(t, i, n):
    G = nc_hand(dict(_nc_base(), nspin=(0, 0, 0), tail=(0, 0.0)))
    # wind-up: lean back, net swung back over the shoulder and tipped hard, spinning fast (held)
    windp = dict(G, chest=(-10, 0, -18), hips=-3, head=(6, 0, 0), uaR=(196, 0, 0), laR=4, uaL=(60, 0, 0), laL=30, thL=22, snL=-26, thR=-18, snR=-10,
                 root=(-0.06, 0), squash=(1.03, 0.97), brow=-12, vis=dict(m_open=1, m_shut=0), tail=(-16, 0.2))
    wind = nc_hand(dict(windp, ntilt=(-14, NC_TILT + 8, 0), nspin=(0, 0, 70)), 0)
    wind2 = nc_hand(dict(windp, chest=(-13, 0, -24), root=(-0.08, 0), squash=(1.05, 0.95), ntilt=(-20, NC_TILT + 10, 0), nspin=(0, 0, 160)), 0)
    # throw: body uncoils forward, arm whips out level, the net leaves the hand and flies open in front
    throw = nc_hand(dict(G, chest=(24, 0, 20), hips=7, head=(-10, 0, 0), uaR=(98, 0, 0), laR=4, uaL=(-40, 0, 0), laL=20, thL=34, snL=-30,
                         thR=-30, snR=-4, root=(0.18, 0), squash=(0.97, 1.04), brow=-16,
                         vis=dict(m_open=1, m_shut=0, net=0, cast=1), ctilt=(-10, 70, 0), tail=(40, 0.5)), 0)
    follow = nc_hand(dict(throw, chest=(27, 0, 14), uaR=(84, 0, 0), laR=8, root=(0.20, 0), vis=dict(m_open=1, m_shut=0, net=0, cast=0),
                          tail=(10, 0.7)), 0)
    end = nc_hand(dict(G, uaR=(60, 0, 0), laR=30, vis=dict(net=0), tail=(0, 1.0)), 0)
    return keys([(0.0, G), (0.24, wind), (0.44, wind2), (0.56, throw), (0.72, follow), (1.0, end)], t)


def nc_hit(t, i, n):
    G = _nc_base()
    back = nc_hand(dict(G, chest=-18, head=(-15, 0, 0), hips=-5, root=(-0.10, 0), squash=(1.06, 0.93), uaR=(176, 0, 0), laR=24, brow=14,
                        ntilt=(-16, NC_TILT + 10, 0), vis=dict(m_open=1, m_shut=0, eyes_shut=1), tail=(-30, 0.2)))
    mid = nc_hand(dict(G, chest=-6, root=(-0.05, 0), ntilt=(-4, NC_TILT + 4, 0), nspin=(0, 0, 10)))
    return keys([(0.0, back), (0.45, mid), (1.0, nc_hand(dict(G, nspin=(0, 0, 18))))], t)


def nc_die(t, i, n):
    G = nc_hand(_nc_base())
    reel = nc_hand(dict(G, chest=-22, head=(-20, 0, 0), hips=-8, root=(-0.10, 0), uaR=(120, 0, 0), laR=40, uaL=(-40, 0, 0), laL=30, brow=16,
                        ntilt=(-30, NC_TILT + 20, 0), vis=dict(m_open=1, m_shut=0, eyes_shut=1), tail=(-30, 0.2)))
    fall = dict(reel, rootrot=-60, root=(-0.20, 0.10), free=1, thL=30, snL=-50, thR=10, snR=-30, uaR=(-30, 0, 0), laR=30, uaL=(-100, 0, 0),
                vis=dict(m_open=1, m_shut=0, eyes_shut=1, net=0))
    down = dict(fall, rootrot=-90, root=(-0.30, 0.26), chest=-3, head=(-4, 0, 0), thL=12, snL=-18, thR=2, snR=-6, uaR=(-150, 0, 0), laR=10,
                uaL=(-140, 0, 0), laL=10, vis=dict(m_open=0, m_shut=1, eyes_shut=1, net=0), brow=0, squash=(1.10, 0.86), tail=(0, 0.5))
    bounce = dict(down, root=(-0.30, 0.32), rootrot=-86, squash=(0.96, 1.05))
    rest = dict(down, squash=(1.0, 1.0))
    return keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, rest), (1.0, rest)], t)


def _nc(t):
    register(dict(id="netcaster" + ("" if t == 1 else "_t%d" % t), tier=t, v2=netcaster_fig,
                  anims=dict(idle=nc_idle, walk=nc_walk, attack=nc_attack, hit=nc_hit, die=nc_die)))


for _t in (1, 2, 3):
    _nc(_t)
