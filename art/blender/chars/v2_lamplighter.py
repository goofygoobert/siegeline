from kit import *
# Sawbones (v2) — the ship's surgeon and healer. Thin, a little stooped, wild white hair, round brass spectacles,
# stained canvas apron. A lantern on a tall pole in the far hand, a green bottle in the near hand.
# Silhouette hook: the lantern on a pole above his head. "Attack" = heal: he thrusts the lantern up and it flares.

def lb_ring(R, r, at, axis="y", seg=14, tseg=6, name="ring"):
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


LB_LEAN = 9


def sawbones_fig(spec):
    t = spec.get("tier", 1)
    fig = Fig("lb%d" % t, INK_CREW, h=1.85)
    white = (0.95, 0.94, 0.90); apron = V2["canvas"]
    C = dict(skin=(0.90, 0.70, 0.56), body=V2["navy"], sleeve=V2["canvas"], arm=(0.90, 0.70, 0.56), legs=V2["navy_dk"], boots=V2["tar"],
             cuff=V2["leather"], nose=(0.88, 0.52, 0.44))
    P = dict(hip=0.64, chest_h=0.67, wy=0.27, wx=0.21, shoulder=0.33, head_r=0.29, belly=0.92, arm_r=0.085, upper_arm=0.28,
             lower_arm=0.27, leg_r=0.10, thigh=0.26, shin=0.24, hip_w=0.13, lean=LB_LEAN, neck_x=0.05, head_rest=-3)
    body(fig, P, C); fists(fig, C, 0.11); boots(fig, C, length=0.32, h=0.18)
    head_crew(fig, C, nose=1.3, jaw=0.92, brow=(0.50, 0.48, 0.52))
    hc = fig.head_c; r = fig.head_r; hip = fig.hip; ch = P["chest_h"]; wx = P["wx"]; wy = P["wy"]
    ex = hc.x + r * 0.90
    # wild white hair: a cap set back off the forehead, tufts flying out behind and at the sides
    fig.add(loft([(hc.z + r * 0.30, r * 1.02, r * 1.07, -0.10), (hc.z + r * 0.66, r * 0.98, r * 1.03, -0.10), (hc.z + r * 0.98, r * 0.62, r * 0.72, -0.12)],
                 seg=12, at=(hc.x, 0, 0), round_=(False, True), name="hair"), "head", white)
    for (y, dz, ln, up) in ((-0.75, 0.55, 0.9, 0.55), (0.0, 0.75, 1.0, 0.75), (0.75, 0.5, 0.9, 0.5), (-0.5, 0.1, 0.85, 0.05), (0.5, 0.1, 0.8, 0.05),
                            (-0.2, 1.0, 0.7, 1.2), (0.3, 0.95, 0.6, 1.3)):
        b = Vector((hc.x - r * 0.62, r * y, hc.z + r * dz))
        fig.add(cone(b, b + Vector((-r * ln, r * y * 0.35, r * up * 0.6)), r * 0.30, 0.02, seg=6, name="tuft"), "head", white, line=0.014)
    for y in (-1, 1):   # side whiskers
        fig.add(cone((hc.x + r * 0.15, y * r * 0.95, hc.z - r * 0.05), (hc.x + r * 0.25, y * r * 1.02, hc.z - r * 0.75), r * 0.2, 0.02, seg=6, name="whisker"),
                "head", white, line=0.012)
    fig.add(orb(r * 0.17, (ex + r * 0.02, 0, hc.z - r * 0.38), (0.7, 1.7, 0.5), seg=8, name="tache"), "head", white, line=0.010)
    # round spectacles: rims only, so the eyes stay readable
    rim = V2["gold"] if t >= 3 else V2["brass"]
    for y in (-1, 1):
        fig.add(lb_ring(r * 0.30, r * 0.055, (ex + r * 0.03, y * r * 0.40, hc.z + r * 0.13), axis="x", seg=12, tseg=5, name="rim"), "head", rim,
                metal=True, line=0.008)
        fig.add(cone((ex - r * 0.05, y * r * 0.70, hc.z + r * 0.15), (hc.x - r * 0.05, y * r * 1.0, hc.z + r * 0.12), r * 0.035, r * 0.035, seg=5, name="arm"),
                "head", rim, metal=True, line=0)
    fig.add(block((r * 0.06, r * 0.26, r * 0.06), (ex + r * 0.05, 0, hc.z + r * 0.16), bevel=0.0, name="bridge"), "head", rim, metal=True, line=0)
    # apron: bib on the chest, wrap skirt to the knees, stains, ties at the back
    fig.add(loft([(hip + 0.12, wx * 1.10, wy * 0.80, 0.04), (hip + ch * 0.45, wx * 1.18, wy * 0.84, 0.045), (hip + ch * 0.78, wx * 1.12, wy * 0.74, 0.06)],
                 name="bib", sq=0.4, round_=(False, False)), "chest", apron, line=0.012)
    fig.add(loft([(hip + 0.16, wx * 1.12, wy * 1.04, 0.03), (hip - 0.12, wx * 1.24, wy * 1.08, 0.05), (hip - 0.40, wx * 1.34, wy * 1.06, 0.07)],
                 name="skirt", sq=0.3, round_=(False, False)), "hips", apron)
    fig.add(loft([(hip + 0.10, wx * 1.16, wy * 1.08, 0.03), (hip + 0.18, wx * 1.14, wy * 1.06, 0.03)], name="tieband", sq=0.3, round_=(False, False)),
            "hips", V2["leather"] if t >= 2 else (0.78, 0.72, 0.60), line=0.008)
    stain_r = (0.60, 0.22, 0.20); stain_g = (0.45, 0.52, 0.30)
    for (x, y, z, s, c, sc) in ((0.12, -wy * 1.07, hip - 0.16, 0.075, stain_r, (1.0, 0.25, 1.3)), (-0.02, -wy * 1.07, hip - 0.30, 0.05, stain_r, (1.2, 0.25, 0.9)),
                                (0.20, -wy * 0.80, hip - 0.05, 0.045, stain_g, (0.7, 0.6, 1.0)), (wx * 1.2 + 0.03, -0.05, hip + ch * 0.42, 0.06, stain_r, (0.3, 1.0, 1.2)),
                                (wx * 1.3 + 0.05, 0.08, hip - 0.22, 0.07, stain_g, (0.3, 1.1, 0.9))):
        fig.add(orb(s, (x, y, z), sc, seg=8, name="stain"), "chest" if z > hip + 0.2 else "hips", c, line=0)
    chain(fig, "tieA", "hips", (-wx * 1.1, -0.05, hip + 0.14), [0.15, 0.13], 0.045, apron, (-0.5, 0, -1), sway=0.8)
    chain(fig, "tieB", "hips", (-wx * 1.1, 0.05, hip + 0.14), [0.12, 0.10], 0.04, (0.78, 0.72, 0.60), (-0.9, 0, -0.8), sway=0.9, phase=0.3)
    if t >= 2:   # leather satchel on the near hip with a strap, a feather behind the ear
        fig.add(block((0.26, 0.10, 0.22), (-0.08, -wy * 1.1 - 0.06, hip + 0.02), bevel=0.03, name="satchel"), "hips", V2["leather"])
        fig.add(block((0.27, 0.11, 0.09), (-0.08, -wy * 1.1 - 0.065, hip + 0.10), bevel=0.02, name="flap"), "hips", (0.33, 0.21, 0.13), line=0.010)
        fig.add(orb(0.03, (-0.08, -wy * 1.1 - 0.13, hip + 0.06), seg=6), "hips", V2["gold"] if t >= 3 else V2["steel"], metal=True, line=0)
        strap = loft([(-0.035, wx * 1.36, wy * 1.22, 0.04), (0.035, wx * 1.36, wy * 1.22, 0.04)], seg=12, round_=(False, False), sq=0.35, name="strap")
        turn(strap, -32, "X", (0, 0, 0)); strap.data.transform(Matrix.Translation((0, 0, hip + ch * 0.50)))
        fig.add(strap, "chest", V2["leather"], line=0.010)
        fb = Vector((hc.x - r * 0.25, -r * 1.0, hc.z + r * 0.2))
        fig.add(slab([(0, 0), (-0.10, 0.20), (-0.20, 0.44), (-0.28, 0.40), (-0.22, 0.16), (-0.06, -0.02)], 0.03, at=fb, name="feather"), "head", V2["red"], line=0.012)
    # ---- lantern pole in the far hand: built pointing forward (+X) with the arm hanging
    hL = fig.W["handL"]; g = Vector((hL.x + 0.02, hL.y, hL.z - 0.07))
    fig.add(loft([(-0.85, 0.030, 0.030), (1.55, 0.026, 0.026)], seg=7, axis="x", at=g, name="pole"), "handL", V2["wood_dk"], line=0.016)
    band = V2["gold"] if t >= 3 else (V2["iron"] if t >= 2 else V2["brass"])
    for u in ((-0.83, 1.50) if t < 2 else (-0.83, -0.30, 0.60, 1.50)):
        fig.add(loft([(u - 0.03, 0.04, 0.04), (u + 0.03, 0.04, 0.04)], seg=7, axis="x", at=g, round_=(False, False), name="ferrule"), "handL", band, metal=True, line=0.010)
    T = Vector((g.x + 1.53, g.y, g.z - 0.22))        # hook tip: in use (pole upright) this is in front of the pole top
    fig.add(cone((g.x + 1.55, g.y, g.z + 0.01), (T.x + 0.03, T.y, T.z), 0.024, 0.02, seg=6, name="hook"), "handL", V2["iron"], metal=True, line=0.012)
    fig.joint("lant", T, "handL", -1)                 # the lantern hangs; poses keep it plumb (see _lb_fix)
    cage = V2["gold"] if t >= 3 else V2["brass"]
    fig.add(lb_ring(0.035, 0.012, (T.x, T.y, T.z - 0.03), axis="y", seg=8, tseg=4), "lant", cage, metal=True, line=0.008)
    fig.add(cone((T.x, T.y, T.z - 0.20), (T.x, T.y, T.z - 0.06), 0.16, 0.035, seg=8, name="cap"), "lant", cage, metal=True, line=0.016)
    for (dx, dy) in ((0.11, 0.11), (0.11, -0.11), (-0.11, 0.11), (-0.11, -0.11)):
        fig.add(block((0.028, 0.028, 0.26), (T.x + dx, T.y + dy, T.z - 0.32), bevel=0.0, name="post"), "lant", V2["tar"], line=0.008)
    fig.add(block((0.30, 0.30, 0.06), (T.x, T.y, T.z - 0.47), bevel=0.02, name="base"), "lant", cage, metal=True, line=0.014)
    F = Vector((T.x, T.y, T.z - 0.32))
    toggle(fig, "flame", "lant", F, 1)
    fig.add(orb(0.10, F, (1.0, 1.0, 1.25), seg=10, name="flame"), "flame", (1.0, 0.78, 0.36), glow=1.0)
    fig.add(orb(0.05, (F.x, F.y - 0.07, F.z - 0.01), (1.0, 1.0, 1.3), seg=8, name="core"), "flame", (1.0, 0.97, 0.80), glow=1.0)
    # heal flare: a ring of light and rays around the lantern
    toggle(fig, "flare", "lant", F, 0)
    fc = (0.62, 1.0, 0.55) if t >= 3 else (1.0, 0.90, 0.58)
    fig.add(lb_ring(0.50, 0.035, (F.x, F.y - 0.02, F.z), axis="y", seg=24, tseg=5, name="glowring"), "flare", fc, glow=1.0)
    fig.add(lb_ring(0.30, 0.02, (F.x, F.y - 0.02, F.z), axis="y", seg=18, tseg=4, name="glowring2"), "flare", (1.0, 0.97, 0.82), glow=1.0)
    for k in range(8):
        a = math.radians(22.5 + k * 45); ca = math.cos(a); sa = math.sin(a); r0 = 0.60; r1 = 0.86 if k % 2 == 0 else 0.76; w = 0.035
        pts = [(F.x + r0 * ca - w * sa, F.z + r0 * sa + w * ca), (F.x + r1 * ca, F.z + r1 * sa), (F.x + r0 * ca + w * sa, F.z + r0 * sa - w * ca)]
        fig.add(slab(pts, 0.02, at=(0, F.y - 0.02, 0), name="ray"), "flare", fc, glow=1.0)
    # ---- bottle in the near hand (neck forward with the arm hanging)
    hR = fig.W["handR"]; b = Vector((hR.x + 0.02, hR.y - 0.02, hR.z - 0.07))
    glass = V2["cursed"] if t >= 3 else (0.20, 0.46, 0.32)
    fig.add(loft([(-0.17, 0.095, 0.095), (0.13, 0.10, 0.10), (0.21, 0.045, 0.045), (0.36, 0.04, 0.04)], seg=8, axis="x", at=b, name="bottle"), "handR",
            glass, glow=0.35 if t >= 3 else 0.12, line=0.014)
    fig.add(loft([(-0.10, 0.104, 0.104), (0.05, 0.104, 0.104)], seg=8, axis="x", at=b, round_=(False, False), name="label"), "handR", V2["canvas"], line=0)
    fig.add(block((0.07, 0.065, 0.065), (b.x + 0.41, b.y, b.z), bevel=0.01, name="cork"), "handR", V2["wood"], line=0.010)
    return fig


def _lb_fix(d, swing=0.0):
    """Keep the lantern hanging plumb whatever the arm and body do (all pure pitch)."""
    def num(k):
        v = d.get(k, 0.0)
        return v if isinstance(v, (int, float)) else v[0]
    d["lant"] = d.get("rootrot", 0.0) + num("hips") + num("chest") + LB_LEAN - num("uaL") - num("laL") - num("handL") + swing
    return d


def _lb_base():
    # pole upright in the far hand (butt just off the sand), bottle held up in the near hand
    return dict(chest=0, head=0, uaL=35, laL=50, handL=5, uaR=14, laR=62, handR=10, thL=10, snL=-16, thR=-8, snR=-12, brow=0)


def lb_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _lb_base()
    # fidget: he peers at the bottle and gives it a little shake
    k = max(0.0, math.sin(2 * math.pi * t - 0.6))
    d.update(chest=1.5 * s, head=-1 * s + 5 * k, uaR=14 + 10 * k, laR=62 + 22 * k, handR=10 + 14 * math.sin(4 * math.pi * t) * k,
             handL=5 + 2.5 * c, squash=(1 - 0.008 * s, 1 + 0.014 * s), tail=(3, t))
    return _lb_fix(d, 5 * math.sin(2 * math.pi * t - 1.0))


def lb_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _lb_base()
    d.update(thL=22 * s, snL=-8 - 36 * max(0, c), thR=-22 * s, snR=-8 - 36 * max(0, -c), chest=5 + 2.5 * math.cos(2 * p),
             head=-3 - 2 * math.cos(2 * p), uaL=35 + 4 * s, handL=8 + 4 * math.cos(2 * p - 0.6), uaR=12 - 10 * s, laR=60 + 6 * c,
             root=(0, 0.016 * math.cos(2 * p)), tail=(-20, t * 2))
    return _lb_fix(d, -6 + 11 * math.cos(2 * p - 1.4))


def lb_attack(t, i, n):
    G = _lb_base()
    # gather: he hunches and draws the lantern down and in; heal: stretches tall and thrusts it overhead
    wind = dict(G, chest=13, hips=3, head=8, uaL=22, laL=78, handL=18, uaR=-40, laR=70, thL=22, snL=-34, thR=-4, snR=-30,
                root=(-0.03, 0), squash=(1.04, 0.95), brow=-8, tail=(8, 0.2))
    hit = dict(G, chest=-15, hips=-3, head=-14, uaL=166, laL=6, handL=-88, uaR=-52, laR=40, handR=40, thL=6, snL=-4, thR=-6, snR=-2,
               root=(0.03, 0), squash=(0.96, 1.06), brow=10, vis=dict(m_open=1, m_shut=0, flare=1, flame=1.5), tail=(-24, 0.5))
    hold = dict(hit, chest=-12, uaL=160, laL=10, handL=-84, squash=(0.99, 1.02), vis=dict(m_open=1, m_shut=0, flare=0, flame=1.2), tail=(-6, 0.7))
    d = keys([(0.0, G), (0.28, wind), (0.44, wind), (0.556, hit), (0.74, hold), (1.0, dict(G, tail=(0, 1.0)))], t)
    v = dict(d.get("vis", {})); v["flare"] = {5: 1.0, 6: 1.3}.get(i, 0); v["flame"] = {4: 1.2, 5: 1.7, 6: 1.5, 7: 1.2}.get(i, 1)
    d["vis"] = v
    sw = {4: -14, 5: 10, 6: -6, 7: 3}.get(i, 0)
    return _lb_fix(d, sw)


def lb_hit(t, i, n):
    G = _lb_base()
    back = dict(G, chest=-20, head=-16, hips=-5, root=(-0.09, 0), squash=(1.06, 0.93), uaL=20, laL=70, handL=-12, uaR=-60, laR=60, brow=14,
                vis=dict(m_open=1, m_shut=0), tail=(30, 0.2))
    d = keys([(0.0, back), (0.45, dict(G, chest=-7, root=(-0.04, 0))), (1.0, G)], t)
    return _lb_fix(d, (-22, 14, -6, 0)[min(i, 3)])


def lb_die(t, i, n):
    G = _lb_base()
    reel = dict(G, chest=-22, head=-20, hips=-8, root=(-0.08, 0), uaL=30, laL=40, handL=-30, uaR=-110, laR=30, brow=16,
                vis=dict(m_open=1, m_shut=0), tail=(30, 0.2))
    fall = dict(reel, rootrot=-60, root=(0.18, 0.10), free=1, thL=30, snL=-50, thR=10, snR=-30, uaL=10, laL=10, handL=-70, uaR=-150)
    down = dict(fall, rootrot=-90, root=(0.60, 0.19), chest=-13, head=-6, thL=14, snL=-20, thR=2, snR=-6, uaL=0, laL=0, handL=-84,
                uaR=-176, laR=6, handR=-60, vis=dict(m_open=0, m_shut=1, flame=0.6), brow=0, tail=(0, 0.5))
    bounce = dict(down, root=(0.60, 0.25), rootrot=-86)
    out = dict(down, vis=dict(m_open=0, m_shut=1, flame=0))
    d = keys([(0.0, G), (0.2, reel), (0.5, fall), (0.68, down), (0.78, bounce), (0.9, down), (1.0, out)], t)
    if t < 0.5:
        return _lb_fix(d, -18 * math.sin(t * 9))
    # on the sand the lantern tips over and lies beside the pole
    k = min(1.0, (t - 0.5) / 0.18)
    _lb_fix(d); d["lant"] = lerp(d["lant"], 78, ease(k))
    return d


def _lb(t):
    register(dict(id="lamplighter" + ("" if t == 1 else "_t%d" % t), tier=t, v2=sawbones_fig,
                  anims=dict(idle=lb_idle, walk=lb_walk, attack=lb_attack, hit=lb_hit, die=lb_die)))


for _t in (1, 2, 3):
    _lb(_t)
