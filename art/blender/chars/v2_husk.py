from kit import *
# Drowner (v2) — a drowned sailor come back. Hunched, head ahead of the feet, one long claw arm, kelp hair,
# hanging jaw, barnacled hump. Silhouette hook: hanging claws and kelp. Dies by slumping into an ink puddle.

def drowner_fig(spec):
    fig = Fig("dr", INK_DEEP, h=1.7, line=0.024)
    fig.rim = 2.4          # the sunset behind it draws a hot edge down its back (art direction: monsters are rim-lit)
    T = (0.27, 0.50, 0.49); D = (0.12, 0.25, 0.30)
    C = dict(skin=T, body=(0.50, 0.54, 0.47), sleeve=(0.50, 0.54, 0.47), arm=T, legs=D, boots=D, hand=(0.13, 0.27, 0.30), claw=V2["bone"], shin=T)
    P = dict(hip=0.56, chest_h=0.64, wy=0.29, wx=0.25, shoulder=0.35, head_r=0.34, belly=0.82, arm_r=0.085, upper_arm=0.33, lower_arm=0.37,
             leg_r=0.105, thigh=0.26, shin=0.26, hip_w=0.14, lean=10, head_rest=-16, neck_x=0.07, arm_k=dict(R=1.14, L=0.95),
             sh_up=dict(L=0.06), ankle=0.7, chest_x=0.05)
    body(fig, P, C); fists(fig, C, 0.135, claws=True); bare_feet(fig, C)
    n = fig.neck; r = fig.head_r; cz = n.z + r * 0.55; cx = n.x + 0.10
    fig.head_c = Vector((cx, 0, cz))
    # skull: long, low, pushed forward; no neck
    fig.add(loft([(-r * 0.9, r * 0.80, r * 0.82, 0.02), (0.0, r * 0.98, r * 0.92), (r * 0.75, r * 0.80, r * 0.78, 0.03), (r * 1.25, r * 0.50, r * 0.56, -0.02)],
                 seg=12, axis="x", at=(cx, 0, cz), name="skull", sq=0.2), "head", (0.62, 0.74, 0.66))
    # hanging jaw with teeth
    fig.joint("jaw", (cx + r * 0.1, 0, cz - r * 0.55), "head", -1)
    fig.add(loft([(r * 0.0, r * 0.26, r * 0.62), (r * 0.7, r * 0.24, r * 0.56), (r * 1.2, r * 0.16, r * 0.40)], seg=10, axis="x",
                 at=(cx + r * 0.1, 0, cz - r * 0.78), name="jaw", sq=0.2), "jaw", (0.14, 0.29, 0.31))
    fig.add(orb(r * 0.5, (cx + r * 0.7, 0, cz - r * 0.60), (1.1, 0.9, 0.36), seg=10, name="maw"), "head", V2["glow"], glow=1.0)
    for i, y in enumerate((-0.42, -0.14, 0.14, 0.42)):
        fig.add(cone((cx + r * (0.95 + 0.1 * (i % 2)), r * y, cz - r * 0.62), (cx + r * 1.0, r * y, cz - r * 0.26), r * 0.10, 0.0, seg=5), "jaw", V2["bone"], line=0.01)
        fig.add(cone((cx + r * (1.02 - 0.1 * (i % 2)), r * y * 0.9, cz - r * 0.40), (cx + r * 1.05, r * y * 0.9, cz - r * 0.72), r * 0.09, 0.0, seg=5), "head", V2["bone"], line=0.01)
    for y in (-1, 1):
        fig.add(orb(r * 0.40, (cx + r * 0.80, y * r * 0.50, cz + r * 0.12), (0.7, 0.9, 1.0), seg=8, name="eye"), "head", V2["glow"], glow=1.3)
        fig.add(block((r * 0.5, r * 0.36, r * 0.1), (cx + r * 0.76, y * r * 0.50, cz + r * 0.54), rot=(-24, "Y"), bevel=0.02, name="lid"), "head", D, line=0.008)
    # kelp hair: long strands down the back, one over the face
    for i, (y, ln, ph) in enumerate(((-0.6, 0.30, 0.0), (0.0, 0.36, 0.25), (0.6, 0.28, 0.5), (-0.3, 0.24, 0.7))):
        chain(fig, "kelp%d" % i, "head", (cx - r * (0.5 + 0.12 * i), r * y, cz + r * 0.55), [ln * 0.8, ln * 0.7, ln * 0.55], 0.075,
              V2["kelp"] if i % 2 else V2["kelp_lt"], (-0.45, 0, -1), flat=0.45, sway=1.0, phase=ph)
    chain(fig, "kelpf", "head", (cx + r * 0.5, -r * 0.75, cz + r * 0.6), [0.16, 0.14], 0.05, V2["kelp"], (0.35, -0.1, -1), flat=0.45, sway=0.8, phase=0.4)
    # barnacled hump on the high shoulder, rags at the waist and elbow, glowing cracks in the chest
    sz = fig.sh_z
    fig.add(orb(0.24, (-0.12, 0.12, sz + 0.02), (1.1, 1.1, 0.8), seg=10, name="hump"), "chest", (0.15, 0.30, 0.32))
    for (x, y, z, s) in ((-0.16, -0.02, sz + 0.18, 0.075), (-0.02, 0.10, sz + 0.21, 0.06), (-0.26, 0.12, sz + 0.13, 0.065), (-0.10, -0.14, sz + 0.12, 0.05)):
        fig.add(cone((x, y, z - s * 0.5), (x, y, z + s * 0.9), s, s * 0.55, seg=6, name="barn"), "chest", V2["barn"], line=0.012)
        fig.add(orb(s * 0.45, (x, y, z + s * 0.9), (1, 1, 0.5), seg=6), "chest", D, glow=0.8, line=0)
    hip = fig.hip
    for i, (x, y, ln) in enumerate(((0.20, -0.20, 0.22), (0.05, -0.29, 0.30), (-0.14, -0.24, 0.24), (0.22, 0.10, 0.26), (-0.2, 0.05, 0.3))):
        chain(fig, "rag%d" % i, "hips", (x, y, hip + 0.02), [ln * 0.55, ln * 0.45], 0.075, V2["rag"] if i % 2 else (0.34, 0.37, 0.35),
              (-0.2, 0, -1), flat=0.4, taper=0.6, sway=0.7, phase=i * 0.21)
    for (z, w) in ((hip + 0.34, 0.16), (hip + 0.44, 0.12)):
        fig.add(block((0.03, w, 0.035), (0.262, -0.05, z), rot=(18, "X"), bevel=0.0, name="crack"), "chest", V2["glow"], glow=1.0)
    # ink puddle for the death, claw streaks for the strike
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(0.62, (0.05, 0, 0.012), (1.25, 0.8, 0.045), seg=14, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((0.3, -0.2, 0.07), (-0.35, -0.1, 0.05), (0.1, -0.34, 0.04)):
        fig.add(orb(s, (x, y, 0.04), (1, 1, 0.3), seg=6), "puddle", V2["glow"], glow=1.0)
    toggle(fig, "swipe", "root", (0.3, -0.3, 0.9), 0)
    for k in range(3):
        arc = []
        R = 0.95 + k * 0.11
        for i in range(7):
            a = math.radians(95 - i * 17); arc.append((0.25 + R * math.cos(a), 0.85 + R * math.sin(a)))
        for i in range(6, -1, -1):
            a = math.radians(95 - i * 17); w = 0.90 + 0.09 * abs(i - 3) / 3
            arc.append((0.25 + R * w * math.cos(a), 0.85 + R * w * math.sin(a)))
        fig.add(slab(arc, 0.02, at=(0, -0.36, 0), name="streak"), "swipe", (0.75, 1.0, 0.82), glow=1.0)
    return fig


def _dr_base():
    return dict(chest=0, head=0, jaw=-34, uaR=14, laR=16, handR=10, uaL=4, laL=30, thL=16, snL=-30, thR=4, snR=-20)


def dr_idle(t, i, n):
    s = math.sin(2 * math.pi * t); c = math.cos(2 * math.pi * t)
    d = _dr_base()
    d.update(chest=2.5 * s, head=3 * c, jaw=-14 - 6 * max(0, s), uaR=14 + 5 * s, laR=16 + 6 * c, uaL=4 - 4 * s, root=(0.012 * s, 0),
             squash=(1 + 0.012 * s, 1 - 0.016 * s), tail=(3, t))
    return d


def dr_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    d = _dr_base()
    # a shamble: the near leg reaches, the far leg drags; the long arm swings late
    d.update(thL=12 + 22 * s, snL=-30 - 30 * max(0, c), thR=6 - 26 * s, snR=-22 - 40 * max(0, -c), chest=4 + 5 * math.sin(p - 0.6),
             head=4 - 7 * math.sin(p - 1.2), jaw=-16 - 8 * max(0, s), uaR=12 + 22 * math.sin(p - 1.0), laR=18 + 12 * math.sin(p - 1.6),
             uaL=4 - 16 * math.sin(p - 0.8), laL=30, root=(0.03 * math.sin(p - 0.4), 0), tail=(22, t * 2))
    return d


def dr_attack(t, i, n):
    B = _dr_base()
    rear = dict(B, chest=-30, head=-20, hips=-6, jaw=-52, uaR=178, laR=24, handR=-20, uaL=150, laL=30, thL=20, snL=-30, thR=8, snR=-18,
                root=(-0.08, 0), squash=(0.96, 1.05), tail=(-24, 0.2))
    slam = dict(B, chest=10, head=0, hips=4, jaw=-40, uaR=62, laR=18, handR=-30, uaL=48, laL=22, thL=32, snL=-40, thR=-14, snR=-24,
                root=(0.22, 0), squash=(1.05, 0.95), vis=dict(swipe=1), tail=(44, 0.5))
    hold = dict(slam, uaR=40, uaL=30, chest=15, vis=dict(swipe=0), tail=(8, 0.7))
    return keys([(0.0, B), (0.30, rear), (0.42, rear), (0.56, slam), (0.72, hold), (1.0, B)], t)


def dr_hit(t, i, n):
    B = _dr_base()
    back = dict(B, chest=-30, head=-28, jaw=-50, root=(-0.10, 0), uaR=-30, laR=50, uaL=-40, squash=(1.06, 0.93), tail=(-34, 0.2))
    return keys([(0.0, back), (0.5, dict(B, chest=-10, root=(-0.05, 0))), (1.0, B)], t)


def dr_die(t, i, n):
    B = _dr_base()
    jolt = dict(B, chest=-34, head=-30, jaw=-58, uaR=-50, laR=40, uaL=-60, root=(-0.08, 0), squash=(0.94, 1.08), tail=(-30, 0.2))
    sag = dict(B, chest=30, head=40, jaw=-30, uaR=40, laR=10, uaL=30, thL=50, snL=-100, thR=40, snR=-90, squash=(1.12, 0.72),
               vis=dict(puddle=0.5), tail=(10, 0.5))
    melt = dict(sag, chest=58, head=60, thL=70, snL=-130, thR=60, snR=-120, squash=(1.3, 0.34), vis=dict(puddle=0.85))
    pool = dict(melt, chest=75, head=70, squash=(1.42, 0.13), vis=dict(puddle=1.0), free=1, root=(0, -0.02))
    return keys([(0.0, B), (0.16, jolt), (0.45, sag), (0.72, melt), (0.92, pool), (1.0, pool)], t)


register(dict(id="husk", facing=-1, v2=drowner_fig, anims=dict(idle=dr_idle, walk=dr_walk, attack=dr_attack, hit=dr_hit, die=dr_die)))
