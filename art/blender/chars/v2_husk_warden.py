from kit import *
# The Kelpie (v2, mini-boss) — a ghastly water-horse rearing on its hind legs, about 3.2 tall. Long skull-like
# head on a long curved neck, kelp mane and tail, glowing eyes, fore-hooves held up, dripping.
# Silhouette hook: the rearing horse neck and head. Light signature shape: the bone-white horse skull.

KP_BODY = (0.42, 0.60, 0.59); KP_LOW = (0.25, 0.42, 0.46); KP_DARK = (0.14, 0.26, 0.31); KP_BELLY = (0.58, 0.70, 0.62)
KP_SKULL = (0.90, 0.87, 0.76); KP_FLASH = (0.80, 1.0, 0.86)
KP_POOL = (1.34, 0.12)      # final squash of the death (x/y, z)


def kp_drip(fig, joint, p, ln=0.14, r=0.035):
    p = Vector(p)
    fig.add(cone(p, p - Vector((0, 0, ln)), r * 0.5, r, seg=5, name="drip"), joint, V2["glow"], glow=1.0)
    fig.add(orb(r * 1.25, p - Vector((0, 0, ln)), seg=6, name="drop"), joint, V2["glow"], glow=1.0)


def kp_fig(spec):
    fig = Fig("kp", INK_DEEP, h=3.2, line=0.028)
    TH = 0.46; SN = 0.48; FT = 0.38
    fig.P = dict(thigh=TH, shin=SN)            # pose() uses these to keep the lower hoof on the ground
    hz = FT + SN + TH
    fig.joint("hips", (0, 0, hz), "root", 1)
    fig.joint("chest", (0.0, 0, hz + 0.10), "hips", 1, rest=32)
    # haunches and the barrel of the body (ribs showing on the near flank)
    fig.add(loft([(hz - 0.36, 0.34, 0.36, -0.04), (hz - 0.02, 0.50, 0.46, -0.06), (hz + 0.34, 0.44, 0.42)], seg=12, name="haunch", sq=0.2), "hips", KP_BODY)
    fig.add(loft([(hz + 0.08, 0.42, 0.40), (hz + 0.46, 0.47, 0.43, 0.04), (hz + 0.80, 0.49, 0.45, 0.08), (hz + 1.04, 0.34, 0.36, 0.06)],
                 seg=12, name="barrel", sq=0.25), "chest", KP_BODY)
    fig.add(orb(0.40, (0.30, 0, hz + 0.64), (0.6, 0.95, 1.4), seg=10, name="belly"), "chest", KP_BELLY)
    for i in range(4):
        z = hz + 0.26 + i * 0.165
        fig.add(block((0.52, 0.05, 0.07), (0.06, -0.425 - 0.012 * (1.5 - abs(i - 1.5)), z), rot=(-22, "Y"), bevel=0.02, name="rib"), "chest", V2["bone"], line=0.012)
        if i < 3:
            fig.add(block((0.34, 0.03, 0.035), (0.06, -0.43, z + 0.09), rot=(-22, "Y"), bevel=0.0, name="ribglow"), "chest", V2["glow"], glow=1.0)
    for (x, z) in ((0.42, hz + 0.50), (0.50, hz + 0.86), (0.34, hz + 0.22)):
        kp_drip(fig, "chest", (x, -0.18, z), 0.16)
    # hind legs: thigh, gaskin, then cannon + hoof as the 'foot' (stays upright)
    for s, y in (("L", 1), ("R", -1)):
        hy = y * 0.27
        fig.joint("th" + s, (0, hy, hz), "hips", -1)
        fig.joint("sn" + s, (0, hy, hz - TH), "th" + s, -1)
        fig.joint("ft" + s, (0, hy, FT), "sn" + s, -1)
        fig.add(loft([(hz + 0.06, 0.29, 0.22), (hz - TH * 0.5, 0.24, 0.19, 0.03), (hz - TH, 0.15, 0.14)], seg=9, at=(0, hy, 0), name="thigh", sq=0.2), "th" + s, KP_BODY)
        fig.add(loft([(hz - TH, 0.16, 0.14), (hz - TH - SN * 0.4, 0.14, 0.12, -0.02), (FT, 0.095, 0.09)], seg=9, at=(0, hy, 0), name="gaskin", sq=0.2), "sn" + s, KP_LOW)
        fig.add(orb(0.12, (0, hy, FT), seg=8, name="hock"), "ft" + s, KP_LOW)
        fig.add(loft([(FT, 0.085, 0.08), (0.16, 0.075, 0.075)], seg=8, at=(0, hy, 0), name="cannon", round_=(False, False)), "ft" + s, KP_LOW)
        fig.add(loft([(0.20, 0.10, 0.10, 0.01), (0.0, 0.155, 0.15, 0.04)], seg=9, at=(0, hy, 0), name="hoof", round_=(False, False)), "ft" + s, KP_DARK)
        for k, (dx, ln) in enumerate(((-0.07, 0.18), (-0.04, 0.14))):
            fig.add(cone((dx, hy + (k - 0.5) * 0.08, 0.26), (dx - 0.12, hy + (k - 0.5) * 0.12, 0.26 - ln), 0.05, 0.0, seg=5, name="feather"), "ft" + s, V2["kelp_lt"], line=0.012)
    # fore-legs, held up in front of the chest
    for s, y in (("L", 1), ("R", -1)):
        sy = y * 0.30; sz = hz + 0.82; UA = 0.50; LA = 0.50
        fig.joint("ua" + s, (0.30, sy, sz), "chest", -1)
        fig.joint("la" + s, (0.30, sy, sz - UA), "ua" + s, -1)
        fig.joint("hand" + s, (0.30, sy, sz - UA - LA), "la" + s, -1)
        fig.add(orb(0.20, (0.30, sy, sz), (1, 0.9, 1.1), seg=9, name="shoulder"), "ua" + s, KP_BODY)
        fig.add(loft([(sz, 0.17, 0.15), (sz - UA, 0.11, 0.105)], seg=9, at=(0.30, sy, 0), name="forearm", sq=0.2), "ua" + s, KP_BODY)
        fig.add(orb(0.115, (0.30, sy, sz - UA), seg=8, name="knee"), "la" + s, KP_LOW)
        fig.add(loft([(sz - UA, 0.10, 0.095), (sz - UA - LA, 0.075, 0.075)], seg=8, at=(0.30, sy, 0), name="fcannon"), "la" + s, KP_LOW)
        hb = sz - UA - LA
        fig.add(loft([(hb + 0.04, 0.10, 0.10), (hb - 0.20, 0.16, 0.155, 0.03)], seg=9, at=(0.30, sy, 0), name="fhoof", round_=(True, False)), "hand" + s, KP_DARK)
        fig.add(loft([(hb - 0.20, 0.165, 0.16, 0.03), (hb - 0.225, 0.15, 0.145, 0.03)], seg=9, at=(0.30, sy, 0), name="shoe", round_=(False, False)),
                "hand" + s, V2["bone"], glow=0.3, line=0.01)
        fig.add(cone((0.22, sy, hb + 0.04), (0.08, sy, hb - 0.14), 0.05, 0.0, seg=5, name="feather"), "hand" + s, V2["kelp_lt"], line=0.012)
        kp_drip(fig, "hand" + s, (0.34, sy - 0.05, hb - 0.22), 0.13)
    # neck in two parts, curving forward
    nb = Vector((0.10, 0, hz + 0.90)); N1 = 0.66; N2 = 0.56
    fig.joint("neck", nb, "chest", 1, rest=-34)
    fig.add(loft([(nb.z - 0.14, 0.31, 0.28), (nb.z + N1 * 0.5, 0.27, 0.21), (nb.z + N1, 0.21, 0.17)], seg=10, at=(nb.x, 0, 0), name="neck1", sq=0.15), "neck", KP_BODY)
    fig.joint("neck2", (nb.x, 0, nb.z + N1), "neck", 1, rest=30)
    fig.add(loft([(nb.z + N1 - 0.06, 0.21, 0.17), (nb.z + N1 + N2 * 0.5, 0.19, 0.155), (nb.z + N1 + N2, 0.18, 0.15)], seg=10, at=(nb.x, 0, 0), name="neck2", sq=0.15),
            "neck2", KP_BODY)
    pz = nb.z + N1 + N2; px = nb.x
    fig.joint("head", (px, 0, pz), "neck2", 1, rest=8)
    fig.head_c = Vector((px + 0.3, 0, pz))
    # skull: long, bone-white, pointing forward from the poll
    fig.add(loft([(-0.10, 0.20, 0.19), (0.16, 0.235, 0.19, 0.0), (0.46, 0.155, 0.135, -0.03), (0.74, 0.125, 0.115, -0.06), (0.86, 0.105, 0.10, -0.07)],
                 seg=10, axis="x", at=(px, 0, pz), name="skull", sq=0.2), "head", KP_SKULL, glow=0.3)
    fig.joint("jaw", (px + 0.10, 0, pz - 0.14), "head", -1)
    fig.add(loft([(0.0, 0.10, 0.15), (0.30, 0.06, 0.105), (0.66, 0.045, 0.085)], seg=8, axis="x", at=(px + 0.10, 0, pz - 0.20), name="jaw", sq=0.2),
            "jaw", (0.74, 0.71, 0.60), glow=0.2)
    fig.add(orb(0.19, (px + 0.56, 0, pz - 0.155), (1.5, 0.5, 0.26), seg=8, name="maw"), "head", V2["glow"], glow=1.0)
    for k in range(4):
        x = px + 0.42 + k * 0.10
        for y in (-1, 1):
            fig.add(cone((x, y * 0.085, pz - 0.12), (x, y * 0.085, pz - 0.20), 0.03, 0.0, seg=4, name="tooth"), "head", V2["white"], glow=0.5, line=0)
    for y in (-1, 1):
        fig.add(orb(0.125, (px + 0.20, y * 0.135, pz + 0.045), (1.0, 0.6, 0.95), seg=8, name="socket"), "head", KP_DARK, line=0)
        fig.add(orb(0.10, (px + 0.215, y * 0.165, pz + 0.045), (1.0, 0.7, 1.0), seg=8, name="eye"), "head", V2["glow"], glow=1.4)
        fig.add(orb(0.035, (px + 0.80, y * 0.085, pz - 0.035), (1.2, 0.8, 0.8), seg=6, name="nostril"), "head", V2["glow"], glow=1.0)
        fig.add(cone((px - 0.02, y * 0.13, pz + 0.12), (px - 0.16, y * 0.19, pz + 0.42), 0.075, 0.0, seg=5, name="ear"), "head", KP_LOW, line=0.016)
    kp_drip(fig, "jaw", (px + 0.62, 0.0, pz - 0.25), 0.16)
    kp_drip(fig, "jaw", (px + 0.36, -0.05, pz - 0.27), 0.11, 0.028)
    # kelp mane down the back of the neck, forelock, tail
    ML = (0.38, 0.62, 0.42)
    mane = (("neck", nb.z + 0.10, 0.34, 0.0), ("neck", nb.z + 0.40, 0.36, 0.2), ("neck2", nb.z + N1 + 0.08, 0.36, 0.4), ("neck2", nb.z + N1 + 0.30, 0.32, 0.6),
            ("head", pz + 0.10, 0.28, 0.8), ("neck", nb.z + 0.24, 0.34, 0.1), ("neck2", nb.z + N1 + 0.20, 0.34, 0.5))
    for i, (par, z, ln, ph) in enumerate(mane):
        bx = px - (0.26 if par == "neck" else 0.18 if par == "neck2" else 0.12)
        chain(fig, "mane%d" % i, par, (bx, -0.10 if i % 2 else 0.0, z), [ln * 1.15, ln, ln * 0.8], 0.16, ML if i % 2 else V2["kelp_lt"],
              (-0.5, 0, -1), taper=0.7, flat=0.35, sway=1.0, phase=ph)
    chain(fig, "lock", "head", (px + 0.14, -0.10, pz + 0.19), [0.2, 0.17], 0.06, ML, (0.5, -0.1, -1), flat=0.45, sway=0.8, phase=0.3)
    for i, (dy, ln, ph, col) in enumerate(((-0.08, 0.40, 0.1, V2["kelp_lt"]), (0.08, 0.34, 0.5, ML), (0.0, 0.46, 0.8, V2["kelp"]))):
        chain(fig, "ktail%d" % i, "hips", (-0.44, dy, hz + 0.10 - i * 0.03), [ln, ln * 0.9, ln * 0.8, ln * 0.65], 0.12, col, (-0.55, 0, -1), flat=0.4,
              sway=0.9, phase=ph)
    # hoof strike: two falling streaks and a splash where they land
    toggle(fig, "swipe", "root", (1.0, -0.3, 1.5), 0)
    for k, (y, R) in enumerate(((-0.34, 1.50), (-0.30, 1.68))):
        arc = []
        for i in range(8):
            a = math.radians(78 - i * 17); arc.append((0.62 + R * math.cos(a), 1.85 + R * math.sin(a)))
        for i in range(7, -1, -1):
            a = math.radians(78 - i * 17); w = 0.93 + 0.06 * abs(i - 3.5) / 3.5
            arc.append((0.62 + R * w * math.cos(a), 1.85 + R * w * math.sin(a)))
        fig.add(slab(arc, 0.02, at=(0, y, 0), name="streak"), "swipe", KP_FLASH, glow=1.0)
    fig.add(orb(0.55, (2.0, -0.3, 0.03), (1.3, 0.9, 0.06), seg=12, name="splash"), "swipe", KP_FLASH, glow=1.0)
    for (a, ln) in ((150, 0.5), (115, 0.7), (80, 0.6), (45, 0.7), (20, 0.5)):
        a = math.radians(a)
        fig.add(cone((2.0 + 0.3 * math.cos(a), -0.3, 0.05), (2.0 + (0.3 + ln) * math.cos(a), -0.3, 0.05 + ln * math.sin(a)), 0.07, 0.0, seg=5, name="spray"),
                "swipe", KP_FLASH, glow=1.0)
    # death: ink pool, with the skull and some kelp left on it (built stretched: the body is squashed flat by then)
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.95, (0.35, 0, 0.012), (1.35, 0.8, 0.04), seg=16, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((1.0, -0.3, 0.09), (-0.4, -0.2, 0.07), (0.3, -0.5, 0.06), (1.3, 0.0, 0.05)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "puddle", V2["glow"], glow=1.0)
    toggle(fig, "remains", "root", (0, 0, 0.0), 0)
    un = Matrix.Diagonal((1 / KP_POOL[0], 1 / KP_POOL[0], 1 / KP_POOL[1], 1))
    rem = [(loft([(-0.10, 0.19, 0.19, 0.19), (0.16, 0.22, 0.19, 0.22), (0.46, 0.15, 0.135, 0.16), (0.80, 0.11, 0.10, 0.12)], seg=10, axis="x",
                 at=(0.25, -0.25, 0.0), rot=None, name="rskull", sq=0.2), KP_SKULL, 0.3, 0.016),
           (orb(0.11, (0.46, -0.42, 0.25), (1.0, 0.5, 0.95), seg=8, name="rsocket"), KP_DARK, 0.9, 0)]
    for (x0, x1, y) in ((-0.5, 0.2, -0.35), (-0.3, -0.9, -0.1), (0.9, 1.5, -0.3)):
        rem.append((cone((x0, y, 0.05), (x1, y - 0.1, 0.03), 0.09, 0.03, seg=6, name="rkelp"), ML, 0.0, 0.014))
    for ob, col, gl, ln in rem:
        ob.data.transform(un)
        fig.add(ob, "remains", col, glow=gl, line=ln)
    return fig


def kp_base():
    return dict(hips=0, chest=0, neck=0, neck2=0, head=0, jaw=-6, uaL=118, laL=-88, handL=18, uaR=100, laR=-72, handR=10,
                thL=44, snL=-80, thR=34, snR=-62)


def kp_idle(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = kp_base()
    # breathing, the neck sways and the head tosses once; the raised hooves paw the air
    toss = max(0.0, math.sin(p - 0.6)) ** 3
    d.update(chest=2.5 * s, neck=3 * c - 6 * toss, neck2=3 * s - 8 * toss, head=-4 * c - 14 * toss, jaw=-6 - 10 * toss,
             uaL=118 + 6 * math.sin(p - 0.8), laL=-88 - 14 * math.sin(p - 1.4), uaR=100 + 6 * math.sin(p + 2.2), laR=-72 - 14 * math.sin(p + 1.6),
             root=(0.012 * s, 0), squash=(1 - 0.008 * s, 1 + 0.012 * s), tail=(4, t))
    return d


def kp_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = kp_base()
    # upright prancing stalk: high-kneed hind steps, the body bobs twice a cycle, fore-hooves paddle alternately
    d.update(thL=40 + 26 * s, snL=-70 - 46 * max(0, c), thR=40 - 26 * s, snR=-70 - 46 * max(0, -c),
             hips=3 * math.cos(2 * p), chest=-2 + 4 * math.cos(2 * p - 0.6), neck=4 * math.sin(2 * p - 1.0), neck2=5 * math.sin(2 * p - 1.6),
             head=-6 * math.sin(2 * p - 2.2), jaw=-8 - 6 * max(0, s),
             uaL=112 + 16 * math.sin(p + 0.5), laL=-84 - 26 * max(0, math.sin(p - 0.4)), uaR=104 - 16 * math.sin(p + 0.5), laR=-76 - 26 * max(0, -math.sin(p - 0.4)),
             root=(0.03 * math.sin(p - 0.4), 0.05 * math.cos(2 * p)), tail=(24, t * 2))
    return d


def kp_attack(t, i, n):
    B = kp_base()
    # rears higher and holds, then drops both fore-hooves on the target
    rear = dict(B, hips=-6, chest=-24, neck=-8, neck2=-10, head=-18, jaw=-30, uaL=134, laL=-104, handL=30, uaR=114, laR=-84, handR=24,
                thL=24, snL=-42, thR=16, snR=-30, root=(-0.12, 0), squash=(0.96, 1.05), tail=(-26, 0.2))
    rear2 = dict(rear, chest=-28, uaL=142, laL=-112, uaR=122, laR=-92, root=(-0.15, 0))
    strike = dict(B, hips=0, chest=6, neck=18, neck2=14, head=-6, jaw=-40, uaL=90, laL=-6, handL=-14, uaR=100, laR=-12, handR=-18,
                  thL=54, snL=-96, thR=40, snR=-78, root=(0.22, 0), squash=(1.05, 0.95), vis=dict(swipe=1), tail=(44, 0.5))
    hold = dict(strike, chest=9, uaL=84, uaR=92, head=-4, squash=(1.02, 0.98), vis=dict(swipe=0), tail=(8, 0.7))
    return keys([(0.0, B), (0.28, rear), (0.44, rear2), (0.56, strike), (0.74, hold), (1.0, B)], t)


def kp_hit(t, i, n):
    B = kp_base()
    back = dict(B, chest=-22, neck=-16, neck2=-18, head=-26, jaw=-40, root=(-0.10, 0), uaL=150, uaR=136, squash=(1.05, 0.94), tail=(-34, 0.2))
    return keys([(0.0, back), (0.5, dict(B, chest=-8, root=(-0.05, 0))), (1.0, B)], t)


def kp_die(t, i, n):
    B = kp_base()
    jolt = dict(B, chest=-28, neck=-20, neck2=-22, head=-30, jaw=-50, uaL=170, uaR=156, root=(-0.10, 0), squash=(0.95, 1.07), tail=(-30, 0.2))
    sag = dict(B, chest=26, neck=24, neck2=30, head=30, jaw=-30, uaL=70, laL=-20, uaR=60, laR=-10, thL=66, snL=-120, thR=58, snR=-108,
               squash=(1.12, 0.70), vis=dict(puddle=0.5), tail=(10, 0.5))
    melt = dict(sag, chest=40, neck=34, neck2=40, head=40, thL=76, snL=-136, thR=70, snR=-128, squash=(1.26, 0.34), vis=dict(puddle=0.85))
    pool = dict(melt, chest=50, squash=KP_POOL, vis=dict(puddle=1.0), free=1, root=(0, -0.02))
    rest = dict(pool, vis=dict(puddle=1.0, remains=1))
    return keys([(0.0, B), (0.16, jolt), (0.45, sag), (0.70, melt), (0.86, pool), (0.87, rest), (1.0, rest)], t)


register(dict(id="husk_warden", facing=-1, v2=kp_fig, anims=dict(idle=kp_idle, walk=kp_walk, attack=kp_attack, hit=kp_hit, die=kp_die)))
