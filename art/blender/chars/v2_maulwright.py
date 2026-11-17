from kit import *
# Anchorman (v2) — huge bald sailor with a handlebar moustache, black vest over a bare chest, red sash,
# canvas trousers. He carries a ship's anchor on a short chain.
# Silhouette hook: the anchor held overhead/behind the bald head. Attack: slow overhead smash into the sand.

def mw_ring(R, r, at, axis="y", seg=14, tseg=6, name="ring"):
    """Torus. axis = the ring's normal."""
    bm = bmesh.new(); rows = []
    for i in range(seg):
        a = 2 * math.pi * i / seg; row = []
        for j in range(tseg):
            b = 2 * math.pi * j / tseg
            u = (R + r * math.cos(b)) * math.cos(a); v = (R + r * math.cos(b)) * math.sin(a); w = r * math.sin(b)
            p = (u, w, v) if axis == "y" else ((w, u, v) if axis == "x" else (u, v, w))
            row.append(bm.verts.new((p[0] + at[0], p[1] + at[1], p[2] + at[2])))
        rows.append(row)
    for i in range(seg):
        for j in range(tseg):
            bm.faces.new((rows[i][j], rows[(i + 1) % seg][j], rows[(i + 1) % seg][(j + 1) % tseg], rows[i][(j + 1) % tseg]))
    return _obj(name, bm)


def mw_star(cx, cz, n, R, r, a0=0.0):
    pts = []
    for i in range(n * 2):
        a = a0 + math.pi * i / n; k = R if i % 2 == 0 else r
        pts.append((cx + k * math.cos(a), cz + k * math.sin(a)))
    return pts


def anchorman_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("mw%d" % t, INK_CREW, h=2.35, line=0.024)
    vest = (0.20, 0.18, 0.21); tache = (0.16, 0.12, 0.11)
    C = dict(skin=V2["skin"], body=vest, sleeve=V2["skin"], arm=V2["skin"], legs=V2["canvas"], belt=V2["red"],
             boots=V2["tar"], cuff=V2["leather"], nose=(0.86, 0.50, 0.40))
    P = dict(hip=0.80, chest_h=0.92, wy=0.50, wx=0.36, shoulder=0.62, head_r=0.34, belly=1.10, arm_r=0.17, upper_arm=0.38,
             lower_arm=0.38, leg_r=0.18, thigh=0.34, shin=0.32, hip_w=0.23, lean=3, neck_x=0.04, chest_x=0.05)
    body(fig, P, C); fists(fig, C, 0.19); boots(fig, C, length=0.44, h=0.23)
    head_crew(fig, C, nose=1.25, jaw=1.15, brow=tache)
    hc = fig.head_c; r = fig.head_r; hip = fig.hip; ch = P["chest_h"]; wx = P["wx"]; wy = P["wy"]
    ex = hc.x + r * 0.90
    # handlebar moustache: thick bar under the nose, two drooping horns
    fig.add(orb(r * 0.26, (ex + r * 0.04, 0, hc.z - r * 0.38), (0.75, 2.0, 0.62), seg=10, name="tache"), "head", tache, line=0.012)
    for y in (-1, 1):
        fig.add(cone((ex + r * 0.02, y * r * 0.42, hc.z - r * 0.40), (ex - r * 0.10, y * r * 0.86, hc.z - r * 0.92), r * 0.17, 0.02, seg=6, name="horn"),
                "head", tache, line=0.012)
    # earring on the near ear
    fig.add(mw_ring(r * 0.14, r * 0.04, (hc.x - r * 0.05, -r * 1.04, hc.z - r * 0.36), axis="y", seg=10, tseg=5), "head",
            V2["gold"] if t >= 3 else V2["brass"], metal=True, line=0.008)
    # open vest: bare chest and belly show down the front
    fig.add(loft([(hip + 0.16, wx * 1.10, wy * 0.46, 0.05), (hip + ch * 0.40, wx * 1.20, wy * 0.50, 0.05), (hip + ch * 0.70, wx * 1.16, wy * 0.52, 0.07),
                  (hip + ch * 0.90, wx * 0.86, wy * 0.46, 0.06)], name="barechest", sq=0.3), "chest", V2["skin"], line=0.010)
    # vest collar edges (trim): brass at tier 3
    trim = V2["brass"] if t >= 3 else (0.30, 0.27, 0.31)
    for y in (-1, 1):
        fig.add(block((0.07, 0.07, ch * 0.62), (wx * 1.12 + 0.05, y * wy * 0.55, hip + ch * 0.52), bevel=0.02, name="vestedge"), "chest", trim,
                metal=t >= 3, line=0.010)
    # sash: knot and tails on the near hip, brass buckle
    fig.add(orb(0.11, (0.02, -wy - 0.03, hip + 0.09), seg=8, name="knot"), "hips", V2["red"], line=0.014)
    chain(fig, "sashA", "hips", (0.0, -wy - 0.04, hip + 0.06), [0.24, 0.22], 0.09, V2["red"], (-0.2, -0.1, -1), sway=0.6, phase=0.5)
    chain(fig, "sashB", "hips", (-0.06, -wy - 0.02, hip + 0.06), [0.20, 0.17], 0.075, (0.62, 0.17, 0.14), (-0.5, -0.1, -1), sway=0.7, phase=0.2)
    fig.add(block((0.07, 0.19, 0.16), (wx + 0.02, 0, hip + 0.09), bevel=0.02, name="buckle"), "hips", V2["brass"], metal=True, line=0.012)
    # trouser patch (the one worn detail)
    fig.add(block((0.12, 0.03, 0.12), (0.03, -fig.hip_w - 0.19, hip - 0.24), bevel=0.01, name="patch"), "thR", V2["navy"], line=0.008)
    if t >= 2:   # leather bracers with iron studs, a strap across the chest, an iron shoulder guard
        ar = P["arm_r"]; ua = P["upper_arm"]; la = P["lower_arm"]
        for s, y in (("L", 1), ("R", -1)):
            sy = y * fig.sh_w
            fig.add(loft([(fig.sh_z - ua - la * 0.30, ar * 1.22, ar * 1.22), (fig.sh_z - ua - la * 0.88, ar * 1.0, ar * 1.0)], seg=9, at=(0, sy, 0),
                         round_=(False, False), name="bracer"), "la" + s, V2["leather"])
            for z in (0.42, 0.74):
                fig.add(orb(0.035, (ar * 1.1, sy - 0.02 * y, fig.sh_z - ua - la * z), seg=6), "la" + s, V2["gold"] if t >= 3 else V2["steel"], metal=True, line=0)
        fig.add(orb(0.25, (0.0, -fig.sh_w - 0.02, fig.sh_z + 0.05), (1.1, 1.0, 0.8), seg=10, name="pauldron"), "uaR",
                V2["brass"] if t >= 3 else V2["iron"], metal=True)
        strap = loft([(-0.045, wx * 1.34, wy * 1.26, 0.04), (0.045, wx * 1.34, wy * 1.26, 0.04)], seg=12, round_=(False, False), sq=0.35, name="strap")
        turn(strap, 30, "X", (0, 0, 0)); strap.data.transform(Matrix.Translation((0, 0, hip + ch * 0.52)))
        fig.add(strap, "chest", V2["leather"], line=0.010)
    if t >= 3:   # coin belt
        for i in range(5):
            a = math.radians(25 + i * 30)
            fig.add(orb(0.05, (wx * 1.04 * math.cos(a), -wy * 1.04 * math.sin(a), hip - 0.02), seg=6, name="coin"), "hips", V2["gold"], metal=True, line=0.008)
    # ---- the anchor: fist -> 3 chain links (joint chn) -> anchor (joint anc). Built hanging from the near hand.
    H = fig.W["handR"]; x0 = H.x + 0.01; y0 = H.y
    iron = V2["iron"]; anc_c = V2["cursed"] if t >= 3 else (0.40, 0.41, 0.47); ag = 0.35 if t >= 3 else 0.0
    fig.joint("chn", (x0, y0, H.z - 0.22), "handR", -1)
    for i in range(3):
        sc = (1.0, 0.45, 1.25) if i % 2 == 0 else (0.45, 1.0, 1.25)
        fig.add(orb(0.065, (x0, y0, H.z - 0.27 - i * 0.105), sc, seg=8, name="link"), "chn", V2["brass"] if t >= 3 else iron, metal=True, line=0.012)
    A = Vector((x0, y0, H.z - 0.54))
    fig.joint("anc", A, "chn", -1)
    fig.add(mw_ring(0.10, 0.032, (x0, y0, A.z - 0.07), axis="y"), "anc", V2["brass"] if t >= 3 else iron, metal=True, line=0.012)
    sh_top = A.z - 0.15; sh_len = 1.04; zb = sh_top - sh_len - 0.04; R = 0.55; zc = zb + R
    fig.add(block((0.14, 0.11, sh_len), (x0, y0, sh_top - sh_len / 2), bevel=0.025, name="shank"), "anc", anc_c, metal=True, glow=ag)
    fig.add(block((0.70, 0.12, 0.12), (x0, y0, sh_top - 0.12), bevel=0.03, name="stock"), "anc", V2["brass"] if t >= 3 else V2["wood_dk"], metal=t >= 3)
    outer = []; inner = []; n = 12
    for i in range(n + 1):
        a = math.radians(186 + i * (168.0 / n)); k = math.sin(math.pi * i / n)
        outer.append((x0 + R * math.cos(a), zc + R * math.sin(a)))
        ri = R - 0.06 - 0.18 * k
        inner.append((x0 + ri * math.cos(a), zc + ri * math.sin(a)))
    fig.add(slab(outer + inner[::-1], 0.10, at=(0, y0, 0), bevel=0.015, name="arms"), "anc", anc_c, metal=True, glow=ag, line=0.02)
    for sg in (-1, 1):
        px = x0 + sg * (R - 0.03); pz = zc - 0.05
        fig.add(slab([(px - sg * 0.21, pz - 0.08), (px + sg * 0.15, pz - 0.06), (px + sg * 0.01, pz + 0.37)], 0.09, at=(0, y0, 0), bevel=0.01, name="fluke"),
                "anc", anc_c, metal=True, glow=ag, line=0.02)
    fig.add(orb(0.105, (x0, y0, zb + 0.06), (1.2, 0.8, 0.8), seg=8, name="crown"), "anc", anc_c, metal=True, glow=ag, line=0.012)
    # ---- strike: overhead arc + sand burst where the anchor lands
    toggle(fig, "swipe", "root", (0.4, -0.5, 1.5), 0)
    arc = []; inn = []
    for i in range(13):
        a = math.radians(125 - i * 14.2); k = math.sin(math.pi * i / 12)
        arc.append((0.35 + 2.05 * math.cos(a), 1.45 + 2.05 * math.sin(a)))
        inn.append((0.35 + 2.05 * (1 - 0.17 * k) * math.cos(a), 1.45 + 2.05 * (1 - 0.17 * k) * math.sin(a)))
    fig.add(slab(arc + inn[::-1][1:-1], 0.02, at=(0, -0.72, 0), name="swipe"), "swipe", (1.0, 0.96, 0.84), glow=1.0)
    toggle(fig, "dust", "root", (2.0, -0.5, 0.0), 0)
    sand = (0.86, 0.72, 0.52)
    for (dx, dy, dz, s) in ((-0.42, -0.1, 0.16, 0.20), (0.0, 0.25, 0.26, 0.24), (0.36, -0.1, 0.15, 0.19), (-0.18, -0.2, 0.40, 0.15), (0.22, 0.1, 0.44, 0.13),
                            (-0.62, 0.1, 0.07, 0.10), (0.60, 0.1, 0.07, 0.10)):
        fig.add(orb(s, (2.0 + dx, -0.5 + dy, dz), (1.15, 1.0, 0.85), seg=8, name="puff"), "dust", sand, glow=0.55, line=0.016)
    fig.add(slab(mw_star(2.0, 0.20, 7, 0.78, 0.26, 0.22), 0.02, at=(0, -0.75, 0), name="impact"), "dust", (1.0, 0.95, 0.80), glow=1.0)
    for (dx, dz, s) in ((-0.75, 0.62, 0.05), (0.72, 0.70, 0.045), (-0.3, 0.95, 0.04), (0.35, 1.0, 0.05), (0.95, 0.35, 0.04)):
        fig.add(orb(s, (2.0 + dx, -0.6, dz), seg=6, name="grit"), "dust", sand, glow=0.55, line=0.01)
    return fig


def _mw_base():
    # anchor carried over the near shoulder: arm up and back, the anchor standing behind and above the head
    return dict(chest=1, head=-2, uaR=198, laR=42, handR=0, chn=-14, anc=-12, uaL=16, laL=56, thL=13, snL=-18, thR=-11, snR=-13, brow=0)


def mw_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _mw_base()
    # fidget: he hefts the anchor, which rocks late on its chain
    d.update(chest=1 + 1.8 * s, head=-2 - 1.2 * s, uaR=198 + 3 * s, laR=42 + 4 * c, chn=-14 + 7 * math.sin(2 * math.pi * t - 0.9),
             anc=-12 + 6 * math.sin(2 * math.pi * t - 1.6), laL=56 + 4 * c, squash=(1 - 0.008 * s, 1 + 0.014 * s), tail=(-3, t))
    return d


def mw_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _mw_base()
    d.update(thL=24 * s, snL=-8 - 38 * max(0, c), thR=-24 * s, snR=-8 - 38 * max(0, -c), chest=7 + 2.5 * math.cos(2 * p),
             head=-5 - 2 * math.cos(2 * p), uaR=196 + 4 * math.cos(2 * p), laR=40 + 5 * math.cos(2 * p - 0.5),
             chn=-12 + 10 * math.cos(2 * p - 1.2), anc=-10 + 9 * math.cos(2 * p - 2.0), uaL=14 - 22 * s, laL=50,
             root=(0, 0.022 * math.cos(2 * p)), tail=(-22, t * 2))
    return d


def mw_attack(t, i, n):
    G = _mw_base()
    # long wind-up: he leans back and lets the anchor drop behind him on its chain
    w1 = dict(G, chest=-10, hips=-3, head=4, uaR=212, laR=52, chn=14, anc=22, uaL=40, laL=40, thL=18, snL=-22, thR=-16, snR=-10,
              root=(-0.06, 0), brow=-10, vis=dict(m_open=0, m_shut=1), tail=(10, 0.1))
    w2 = dict(w1, chest=-19, hips=-6, head=8, uaR=222, laR=64, chn=30, anc=38, uaL=70, laL=30, root=(-0.12, 0), squash=(1.03, 0.97),
              brow=-14, vis=dict(m_open=1, m_shut=0), tail=(16, 0.2))
    hit = dict(G, chest=19, hips=5, head=-12, uaR=80, laR=10, handR=0, chn=0, anc=0, uaL=30, laL=30, thL=36, snL=-34, thR=-28, snR=-6,
               root=(0.08, 0), squash=(0.97, 1.03), brow=-16, vis=dict(m_open=1, m_shut=0, swipe=1, dust=1), tail=(-40, 0.5))
    hold = dict(hit, chest=22, uaR=76, laR=16, chn=-6, anc=4, vis=dict(m_open=1, m_shut=0, dust=0.8), root=(0.09, 0), squash=(1.0, 1.0), tail=(-10, 0.7))
    lift = dict(G, chest=8, uaR=120, laR=40, chn=-30, anc=-30, root=(0.03, 0), tail=(0, 0.9))
    d = keys([(0.0, G), (0.20, w1), (0.34, w2), (0.45, w2), (0.556, hit), (0.70, hold), (0.86, lift), (1.0, dict(G, tail=(0, 1.0)))], t)
    v = dict(d.get("vis", {})); v["swipe"] = 1 if i == 5 else 0; v["dust"] = {5: 1.0, 6: 1.15, 7: 0.7}.get(i, 0)
    d["vis"] = v
    return d


def mw_hit(t, i, n):
    G = _mw_base()
    back = dict(G, chest=-17, head=-15, hips=-5, root=(-0.10, 0), squash=(1.06, 0.93), uaR=206, laR=30, chn=10, anc=20, uaL=-30, laL=40,
                brow=14, vis=dict(m_open=1, m_shut=0), tail=(30, 0.2))
    return keys([(0.0, back), (0.45, dict(G, chest=-6, root=(-0.05, 0))), (1.0, G)], t)


def mw_die(t, i, n):
    G = _mw_base()
    reel = dict(G, chest=-20, head=-18, hips=-7, root=(-0.08, 0), uaR=150, laR=30, chn=40, anc=40, uaL=-40, laL=20, brow=16,
                vis=dict(m_open=1, m_shut=0), tail=(30, 0.2))
    fall = dict(reel, rootrot=-58, root=(0.25, 0.16), free=1, thL=30, snL=-50, thR=10, snR=-30, uaR=60, laR=10, chn=10, anc=10, uaL=-100)
    down = dict(fall, rootrot=-90, root=(0.80, 0.31), chest=-4, head=-8, thL=14, snL=-20, thR=2, snR=-6, uaR=4, laR=4, handR=0, chn=4, anc=4,
                uaL=-150, laL=10, vis=dict(m_open=0, m_shut=1), brow=0, tail=(0, 0.5))
    bounce = dict(down, root=(0.80, 0.38), rootrot=-86)
    return keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, down), (1.0, down)], t)


def _mw(t):
    register(dict(id="maulwright" + ("" if t == 1 else "_t%d" % t), tier=t, v2=anchorman_fig,
                  anims=dict(idle=mw_idle, walk=mw_walk, attack=mw_attack, hit=mw_hit, die=mw_die)))


for _t in (1, 2, 3):
    _mw(_t)
