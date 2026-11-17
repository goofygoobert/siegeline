from kit import *
# Barnacle Troll (v2) — hulking sea troll, about 2.9 tall. A huge hump crusted in pale barnacles and coral rides
# higher than its small sunken head; one massive knuckle-dragging arm carries a driftwood club; short bowed legs.
# Silhouette hook: hump higher than the head + club. Light signature shape: the pale barnacle crust on the hump.

BT_SKIN = (0.36, 0.56, 0.53); BT_DARK = (0.17, 0.31, 0.35); BT_PALE = (0.60, 0.69, 0.58)
BT_CRUST = (0.66, 0.67, 0.58); BT_CORAL = (0.80, 0.47, 0.50); BT_WOOD = (0.68, 0.60, 0.47)
BT_FLASH = (1.0, 0.96, 0.84)


def bt_barn(fig, joint, pos, nrm, s, hole=True):
    p = Vector(pos); n = Vector(nrm).normalized()
    fig.add(cone(p - n * s * 0.45, p + n * s * 0.95, s, s * 0.55, seg=6, name="barn"), joint, V2["barn"], line=0.014)
    if hole:
        q = p + n * s * 0.95
        fig.add(orb(s * 0.50, q, (1, 1, 1), seg=6, name="hole"), joint, V2["glow"], glow=1.0)


def bt_fig(spec):
    fig = Fig("bt", INK_DEEP, h=2.9, line=0.03)
    C = dict(skin=BT_SKIN, body=BT_SKIN, sleeve=BT_SKIN, arm=(0.30, 0.49, 0.48), legs=(0.27, 0.45, 0.46), shin=(0.30, 0.49, 0.48),
             boots=BT_DARK, hand=(0.22, 0.38, 0.40), claw=V2["bone"])
    P = dict(hip=0.74, chest_h=1.30, wy=0.72, wx=0.56, shoulder=0.86, head_r=0.41, belly=1.2, arm_r=0.19, upper_arm=0.50, lower_arm=0.56,
             leg_r=0.23, thigh=0.32, shin=0.30, hip_w=0.40, lean=24, head_rest=-14, neck_x=0.42, arm_k=dict(R=1.3, L=0.82),
             sh_up=dict(L=-0.10, R=0.04), ankle=0.92, chest_x=0.08)
    body(fig, P, C); fists(fig, C, 0.26, claws=False)
    hip = fig.hip
    # feet: broad slabs with three bone claws
    for s in ("L", "R"):
        p = fig.W["ft" + s]
        fig.add(loft([(-0.17, 0.10, 0.17, 0.10), (0.10, 0.105, 0.22, 0.105), (0.42, 0.06, 0.26, 0.06)], seg=8, axis="x",
                     at=(p.x, p.y, 0), name="foot", sq=0.25), "ft" + s, BT_DARK)
        for i in (-1, 0, 1):
            fig.add(cone((p.x + 0.40, p.y + i * 0.15, 0.06), (p.x + 0.62, p.y + i * 0.19, 0.0), 0.065, 0.0, seg=5), "ft" + s, V2["bone"], line=0.014)
        k = fig.W["sn" + s]
        fig.add(orb(0.25, (k.x + 0.04, k.y, k.z), (1, 1, 0.9), seg=8, name="knee"), "sn" + s, C["legs"])
    # pale belly plate and glowing cracks across it
    fig.add(orb(0.52, (0.30, 0, hip + 0.44), (0.62, 1.12, 0.95), seg=12, name="belly"), "chest", BT_PALE)
    for (z, y, w, a) in ((hip + 0.62, -0.30, 0.30, 24), (hip + 0.40, -0.20, 0.22, -18), (hip + 0.27, -0.42, 0.16, 30)):
        fig.add(block((0.05, w, 0.05), (0.60, y, z), rot=(a, "X"), bevel=0.0, name="crack"), "chest", V2["glow"], glow=1.0)
    # the hump: a crusted mound on the back, higher than the head, with barnacles and coral
    hc = Vector((-0.24, 0.0, hip + 1.30 + 0.20)); R = 0.64; sc = (1.08, 1.22, 1.0)
    fig.add(orb(R, hc, sc, seg=14, name="hump"), "chest", BT_CRUST)
    fig.add(orb(0.40, (hc.x + 0.20, -0.62, hc.z - 0.34), (1.1, 1.0, 0.8), seg=10, name="crust2"), "chest", BT_CRUST)
    fig.add(orb(0.5, (hc.x - 0.30, 0, hc.z - 0.55), (1.0, 1.3, 1.1), seg=12, name="hump2"), "chest", BT_SKIN)

    def on_hump(a, b, k=1.0):
        a = math.radians(a); b = math.radians(b)
        n = Vector((math.cos(b) * math.cos(a), math.cos(b) * math.sin(a), math.sin(b)))
        return Vector((hc.x + n.x * R * sc[0] * k, hc.y + n.y * R * sc[1] * k, hc.z + n.z * R * sc[2] * k)), n

    for (a, b, s) in ((-90, 20, 0.17), (-60, 50, 0.14), (-125, 45, 0.16), (-30, 22, 0.12), (-155, 12, 0.13), (-90, 72, 0.13),
                      (0, 58, 0.13), (180, 52, 0.15), (-100, -12, 0.11), (172, 18, 0.12), (22, 30, 0.10), (-45, 82, 0.10),
                      (-140, -18, 0.10), (-62, 2, 0.09)):
        p, n = on_hump(a, b)
        bt_barn(fig, "chest", p, n, s)
    for i, (a, b, ln, fork) in enumerate(((-140, 74, 0.50, 1), (165, 62, 0.40, -1), (-15, 76, 0.36, 1), (95, 60, 0.42, -1), (-80, 86, 0.30, 1))):
        p, n = on_hump(a, b, 0.92)
        tip = p + n * ln + Vector((0, 0, ln * 0.35))
        fig.add(cone(p, tip, 0.085, 0.035, seg=6, name="coral"), "chest", BT_CORAL, glow=0.25, line=0.016)
        mid = p + (tip - p) * 0.5
        t2 = mid + Vector((fork * 0.20, 0.0, 0.22))
        fig.add(cone(mid, t2, 0.055, 0.025, seg=5, name="coral"), "chest", BT_CORAL, glow=0.25, line=0.014)
        for q in (tip, t2):
            fig.add(orb(0.05, q, seg=6, name="tip"), "chest", V2["glow"], glow=1.0)
    for i, (a, b, ln, ph) in enumerate(((178, 20, 0.34, 0.0), (-165, -5, 0.30, 0.3), (160, -8, 0.36, 0.6), (-178, -30, 0.28, 0.8))):
        p, n = on_hump(a, b)
        chain(fig, "bkelp%d" % i, "chest", p, [ln, ln * 0.85, ln * 0.7], 0.11, V2["kelp_lt"] if i % 2 else (0.36, 0.52, 0.30),
              (-0.5, 0, -1), flat=0.45, sway=0.8, phase=ph)
    # barnacles on the big shoulder and forearm
    sR = fig.W["uaR"]; eR = fig.W["laR"]
    for (dx, dy, dz, s) in ((0.0, -0.26, 0.16, 0.12), (-0.16, -0.20, 0.10, 0.10), (0.14, -0.18, 0.2, 0.09)):
        bt_barn(fig, "uaR", (sR.x + dx, sR.y + dy, sR.z + dz), (dx, dy * 2, 0.5), s)
    for (dx, dz, s) in ((-0.02, -0.30, 0.09), (0.08, -0.48, 0.08)):
        bt_barn(fig, "laR", (eR.x + dx, eR.y - 0.24, eR.z + dz), (dx, -1, 0.1), s)
    # head: small, wide, sunk into the front of the chest below the hump. Underbite with two tusks.
    n = fig.neck; r = fig.head_r; cx = n.x + 0.18; cz = n.z - 0.22
    fig.head_c = Vector((cx, 0, cz))
    HS = (0.46, 0.66, 0.60)
    fig.add(loft([(-r * 0.8, r * 0.86, r * 0.98), (0.0, r * 1.0, r * 1.08), (r * 0.70, r * 0.80, r * 0.92, -0.02), (r * 1.10, r * 0.50, r * 0.62, -0.05)],
                 seg=12, axis="x", at=(cx, 0, cz), name="skull", sq=0.25), "head", HS, glow=0.12)
    fig.joint("jaw", (cx + r * 0.05, 0, cz - r * 0.50), "head", -1)
    fig.add(loft([(0.0, r * 0.30, r * 0.86), (r * 0.80, r * 0.30, r * 0.84), (r * 1.38, r * 0.22, r * 0.62)], seg=10, axis="x",
                 at=(cx + r * 0.05, 0, cz - r * 0.78), name="jaw", sq=0.25), "jaw", (0.30, 0.48, 0.47))
    fig.add(orb(r * 0.55, (cx + r * 0.78, 0, cz - r * 0.56), (1.1, 1.1, 0.34), seg=10, name="maw"), "head", V2["glow"], glow=1.0)
    for y in (-1, 1):
        fig.add(cone((cx + r * 1.22, y * r * 0.52, cz - r * 0.80), (cx + r * 1.42, y * r * 0.66, cz + r * 0.12), r * 0.17, 0.0, seg=6, name="tusk"),
                "jaw", V2["bone"], glow=0.2, line=0.014)
        fig.add(orb(r * 0.36, (cx + r * 0.84, y * r * 0.50, cz + r * 0.14), (0.7, 0.9, 0.95), seg=8, name="eye"), "head", V2["glow"], glow=1.3)
        fig.add(block((r * 0.55, r * 0.46, r * 0.16), (cx + r * 0.78, y * r * 0.50, cz + r * 0.46), rot=(-20, "Y"), bevel=0.02, name="lid"),
                "head", BT_DARK, line=0.008)
    for i, (y, ph) in enumerate(((-0.5, 0.1), (0.4, 0.6))):
        chain(fig, "hkelp%d" % i, "head", (cx - r * 0.3, r * y, cz + r * 0.85), [0.2, 0.17], 0.07, V2["kelp_lt"], (-0.7, 0, -0.6), flat=0.45, sway=0.8, phase=ph)
    # rag loincloth
    for i, (x, y, ln) in enumerate(((0.44, -0.30, 0.34), (0.20, -0.62, 0.42), (-0.20, -0.58, 0.36), (0.46, 0.25, 0.36), (-0.4, 0.1, 0.40))):
        chain(fig, "rag%d" % i, "hips", (x, y, hip + 0.06), [ln * 0.55, ln * 0.45], 0.14, V2["rag"] if i % 2 else (0.52, 0.54, 0.46),
              (-0.15, 0, -1), flat=0.4, taper=0.6, sway=0.6, phase=i * 0.21)
    # driftwood club in the big near hand: built pointing forward with the arm hanging
    h = fig.W["handR"]; g = Vector((h.x + 0.02, h.y - 0.02, h.z - 0.19))
    fig.add(loft([(-0.34, 0.08, 0.08), (0.20, 0.10, 0.10), (0.78, 0.18, 0.20, 0.03), (1.15, 0.29, 0.30, -0.02), (1.40, 0.22, 0.24, 0.0)],
                 seg=8, axis="x", at=g, name="club", sq=0.2), "handR", BT_WOOD, glow=0.1)
    for (x, dz, dy, ln) in ((0.72, 0.17, -0.04, 0.24), (1.08, -0.26, 0.02, 0.24), (1.24, 0.25, -0.1, 0.20), (0.95, 0.24, 0.05, 0.16)):
        b = Vector((g.x + x, g.y + dy, g.z + dz * 0.6))
        fig.add(cone(b, b + Vector((0.08, dy, math.copysign(ln, dz))), 0.07, 0.03, seg=5, name="stub"), "handR", (0.56, 0.48, 0.38), line=0.014)
    for x in (0.34, 0.42):
        fig.add(loft([(x - 0.03, 0.125, 0.125), (x + 0.03, 0.13, 0.13)], seg=8, axis="x", at=g, round_=(False, False), name="rope"),
                "handR", V2["rag"], line=0.012)
    bt_barn(fig, "handR", (g.x + 1.08, g.y - 0.28, g.z + 0.02), (0, -1, 0.1), 0.09)
    bt_barn(fig, "handR", (g.x + 1.28, g.y - 0.16, g.z + 0.18), (0.2, -0.6, 1), 0.07)
    # ground impact for the slam
    toggle(fig, "impact", "root", (2.55, -0.88, 0.0), 0)
    ix, iy = 2.55, -0.88
    fig.add(orb(0.8, (ix, iy, 0.03), (1.25, 0.9, 0.05), seg=14, name="shock"), "impact", BT_FLASH, glow=1.0)
    for i, (a, ln) in enumerate(((165, 0.6), (140, 0.8), (62, 1.1), (40, 0.9), (18, 0.8))):
        a = math.radians(a)
        b = Vector((ix + 0.45 * math.cos(a), iy - 0.02 * i, 0.06 + 0.2 * math.sin(a)))
        t = Vector((ix + (0.45 + ln) * math.cos(a), iy - 0.02 * i, 0.06 + (0.3 + ln) * math.sin(a)))
        fig.add(cone(b, t, 0.10, 0.0, seg=5, name="ray"), "impact", BT_FLASH, glow=1.0)
    for (dx, dz, s) in ((-0.9, 0.7, 0.09), (0.75, 0.95, 0.08), (-0.35, 1.2, 0.07), (0.3, 1.35, 0.06), (1.05, 0.45, 0.07)):
        fig.add(block((s * 2, s * 2, s * 1.6), (ix + dx, iy, dz), rot=(30, "Y"), bevel=0.01, name="grit"), "impact", (0.80, 0.62, 0.44), glow=0.6, line=0.012)
    # death: ink pool and what is left on it (built stretched, because the body is squashed flat by then)
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(1.0, (0.25, 0, 0.012), (1.35, 0.8, 0.04), seg=16, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((0.9, -0.3, 0.10), (-0.6, -0.2, 0.08), (0.2, -0.55, 0.07), (1.2, -0.05, 0.06)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "puddle", V2["glow"], glow=1.0)
    toggle(fig, "remains", "root", (0, 0, 0.0), 0)
    un = Matrix.Diagonal((1 / BT_POOL[0], 1 / BT_POOL[0], 1 / BT_POOL[1], 1))
    rem = []
    for (x, y, s) in ((-0.30, -0.25, 0.17), (0.05, -0.05, 0.20), (-0.55, 0.0, 0.14), (0.30, -0.35, 0.12)):
        rem.append((cone((x, y, 0.02), (x, y, 0.02 + s * 1.3), s, s * 0.55, seg=6, name="rbarn"), V2["barn"], 0.0))
        rem.append((orb(s * 0.5, (x, y, 0.02 + s * 1.3), seg=6), V2["glow"], 1.0))
    rem.append((cone((-0.1, -0.2, 0.05), (0.15, -0.2, 0.5), 0.08, 0.03, seg=6, name="rcoral"), BT_CORAL, 0.25))
    rem.append((loft([(0.5, 0.09, 0.09, 0.12), (1.1, 0.17, 0.19, 0.19), (1.55, 0.24, 0.25, 0.24), (1.7, 0.19, 0.2, 0.2)], seg=8, axis="x",
                     at=(0, -0.5, 0), name="rclub", sq=0.2), BT_WOOD, 0.1))
    for ob, col, gl in rem:
        ob.data.transform(un)
        fig.add(ob, "remains", col, glow=gl, line=0.014)
    return fig


BT_POOL = (1.36, 0.13)      # final squash of the death (x/y, z)
BT_OFF = dict(snL=(0, 0.10, 0), ftL=(0, -0.10, 0), snR=(0, -0.10, 0), ftR=(0, 0.10, 0))    # bowed knees


def bt_base():
    return dict(chest=0, head=0, jaw=-10, uaR=30, laR=22, handR=-27, uaL=22, laL=34, thL=18, snL=-34, thR=6, snR=-22, off=BT_OFF)


def bt_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = bt_base()
    d.update(chest=(2.5 * s, 1.5 * c, 0), head=4 * c, jaw=-10 - 8 * max(0, s), uaR=30 + 3 * s, handR=-27 + 3 * c, uaL=22 - 5 * s, laL=34 + 6 * c,
             root=(0.015 * s, 0), squash=(1 + 0.012 * s, 1 - 0.016 * s), tail=(3, t))
    return d


def bt_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = bt_base()
    # a slow lumber: short steps, the whole trunk rolls over the planted foot, the club arm swings late and heavy
    d.update(thL=10 + 24 * s, snL=-30 - 34 * max(0, c), thR=8 - 24 * s, snR=-24 - 38 * max(0, -c),
             chest=(3 + 5 * math.sin(p - 0.5), 5 * s, 0), hips=(0, -3 * s, 0), head=3 - 6 * math.sin(p - 1.2), jaw=-12 - 8 * max(0, s),
             uaR=30 + 14 * math.sin(p - 1.0), laR=22 + 8 * math.sin(p - 1.6), handR=-27 + 7 * math.sin(p - 2.2),
             uaL=22 - 20 * math.sin(p - 0.8), laL=34, root=(0.04 * math.sin(p - 0.4), 0.035 * math.cos(2 * p)), tail=(18, t * 2))
    return d


def bt_attack(t, i, n):
    B = bt_base()
    # club hauled up overhead and held, then slammed into the ground in front
    wind = dict(B, chest=-30, hips=-5, head=-16, jaw=-26, uaR=186, laR=22, handR=-88, uaL=-30, laL=50, thL=22, snL=-32, thR=10, snR=-18,
                root=(-0.10, 0), squash=(0.96, 1.05), tail=(-22, 0.2))
    wind2 = dict(wind, chest=-34, uaR=192, laR=30, root=(-0.13, 0))
    slam = dict(B, chest=16, hips=5, head=-4, jaw=-46, uaR=70, laR=5, handR=-42, uaL=50, laL=20, thL=34, snL=-44, thR=-12, snR=-26,
                root=(0.10, 0), squash=(1.06, 0.94), vis=dict(impact=1), tail=(40, 0.5))
    hold = dict(slam, chest=19, handR=-36, squash=(1.03, 0.97), vis=dict(impact=0), tail=(8, 0.7))
    return keys([(0.0, B), (0.28, wind), (0.44, wind2), (0.56, slam), (0.74, hold), (1.0, B)], t)


def bt_hit(t, i, n):
    B = bt_base()
    back = dict(B, chest=-24, head=-24, jaw=-44, root=(-0.10, 0), uaR=6, laR=40, uaL=-36, squash=(1.05, 0.94), tail=(-30, 0.2))
    return keys([(0.0, back), (0.5, dict(B, chest=-8, root=(-0.05, 0))), (1.0, B)], t)


def bt_die(t, i, n):
    B = bt_base()
    jolt = dict(B, chest=-30, head=-28, jaw=-52, uaR=-10, laR=40, handR=-10, uaL=-60, root=(-0.08, 0), squash=(0.95, 1.07), tail=(-30, 0.2))
    sag = dict(B, chest=22, head=34, jaw=-30, uaR=44, laR=10, handR=-20, uaL=30, thL=48, snL=-96, thR=40, snR=-88, squash=(1.12, 0.72),
               vis=dict(puddle=0.5), tail=(10, 0.5))
    melt = dict(sag, chest=40, head=52, thL=62, snL=-118, thR=56, snR=-110, squash=(1.26, 0.36), vis=dict(puddle=0.85))
    pool = dict(melt, chest=52, head=60, squash=BT_POOL, vis=dict(puddle=1.0), free=1, root=(0, -0.02))
    rest = dict(pool, vis=dict(puddle=1.0, remains=1))
    return keys([(0.0, B), (0.16, jolt), (0.45, sag), (0.70, melt), (0.86, pool), (0.87, rest), (1.0, rest)], t)


register(dict(id="brute", facing=-1, v2=bt_fig, anims=dict(idle=bt_idle, walk=bt_walk, attack=bt_attack, hit=bt_hit, die=bt_die)))
