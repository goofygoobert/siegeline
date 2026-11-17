from kit import *
# Mother Fathom (v2, boss) — a towering sea hag, about 5.6 tall (three crew tall). Hunched crone in rotted
# sailcloth robes that reach the ground, fish-scale skin, a crown of coral and whale bone, a lantern-fish lure
# glowing on a stalk above her head, ONE long tentacle arm (near side) and a clawed arm (far side).
# Silhouette hook: lure light above a cloak triangle + tentacle. Light signature shapes: the lure and the pale robe.

MF_CLOTH = (0.62, 0.68, 0.60); MF_CLOTH_D = (0.42, 0.50, 0.47); MF_SHAWL = (0.37, 0.28, 0.46)
MF_SKIN = (0.40, 0.62, 0.56); MF_SKIN_D = (0.24, 0.42, 0.44); MF_SCALE = (0.62, 0.80, 0.68); MF_DARK = (0.12, 0.20, 0.27)
MF_CORAL = (0.84, 0.47, 0.52); MF_LURE = (0.88, 1.0, 0.62); MF_FLASH = (0.80, 1.0, 0.86); MF_INKGLOW = (0.66, 0.36, 0.92)
MF_POOL = (1.30, 0.06)       # final squash of the death (x/y, z)
MF_LEAN = 14                 # built-in hunch of the chest
MF_TL = [1.0, 0.95, 0.90, 0.80, 0.75, 0.70, 0.60, 0.50]                 # tentacle segment lengths
MF_TR = [0.44, 0.40, 0.35, 0.30, 0.25, 0.20, 0.155, 0.115, 0.06]         # radius at each joint
MF_ROBE = [(0.0, 2.25, 1.35, 0.0), (0.6, 2.0, 1.25, 0.0), (1.6, 1.45, 1.05, 0.05), (2.75, 1.0, 0.92, 0.15), (3.3, 1.0, 1.05, 0.25)]


def mf_robe_y(x, z, out=0.0):
    """y of the robe's near surface at (x, z)."""
    for (z0, a0, b0, d0), (z1, a1, b1, d1) in zip(MF_ROBE, MF_ROBE[1:]):
        if z <= z1:
            break
    k = min(max((z - z0) / (z1 - z0), 0.0), 1.0)
    a = lerp(a0, a1, k); b = lerp(b0, b1, k); d = lerp(d0, d1, k)
    u = min(abs(x - d) / a, 0.95)
    return -(b * math.sqrt(1 - u * u) + out)


def mf_crown_parts(c, r):
    """Crown of whale-bone ribs and coral, centred on c (band height). Returns [(object, colour, glow, line)]."""
    f = r / 0.5
    parts = [(loft([(c.z - 0.08 * f, r, r), (c.z + 0.10 * f, r * 1.06, r * 1.06)], seg=12, at=(c.x, c.y, 0), round_=(False, False), name="band"), (0.70, 0.66, 0.56), 0.0, None)]
    for k in range(8):
        a = math.radians(k * 45 + 12); ca, sa = math.cos(a), math.sin(a)
        b = Vector((c.x + r * ca, c.y + r * sa, c.z + 0.06 * f))
        if k % 2 == 0:      # whale-bone rib, curving back in at the top
            m = b + Vector((0.20 * ca, 0.20 * sa, 0.44)) * f; t = m + Vector((-0.12 * ca, -0.12 * sa, 0.40)) * f
            parts.append((cone(b, m, 0.115 * f, 0.085 * f, seg=6, name="rib"), V2["bone"], 0.25, 0.018))
            parts.append((cone(m, t, 0.085 * f, 0.0, seg=6, name="rib"), V2["bone"], 0.25, 0.018))
            parts.append((orb(0.088 * f, m, seg=6, name="ribj"), V2["bone"], 0.25, 0))
        else:               # coral branch with a fork and glowing tips
            t = b + Vector((0.16 * ca, 0.16 * sa, 0.50)) * f; m = b + (t - b) * 0.5
            t2 = m + Vector((0.22 * ca - 0.10 * sa, 0.22 * sa + 0.10 * ca, 0.20)) * f
            parts.append((cone(b, t, 0.09 * f, 0.04 * f, seg=6, name="coral"), MF_CORAL, 0.3, 0.016))
            parts.append((cone(m, t2, 0.06 * f, 0.03 * f, seg=5, name="coral"), MF_CORAL, 0.3, 0.014))
            parts.append((orb(0.06 * f, t, seg=6, name="tip"), V2["glow"], 1.0, 0))
            parts.append((orb(0.05 * f, t2, seg=6, name="tip"), V2["glow"], 1.0, 0))
    return parts


def mf_fig(spec):
    fig = Fig("mf", INK_DEEP, h=5.6, line=0.036)
    # ---- robe: skirt (hips), waist, hunched chest. A wide triangle that reaches the ground.
    fig.joint("hips", (0, 0, 0), "root", 1)
    fig.joint("waist", (0.05, 0, 1.40), "hips", 1)
    fig.joint("chest", (0.15, 0, 2.60), "waist", 1, rest=MF_LEAN)
    fig.add(loft([MF_ROBE[0], MF_ROBE[1], MF_ROBE[2]], seg=16, name="skirt", sq=0.2, round_=(False, True)), "hips", MF_CLOTH)
    fig.add(loft([(1.42, 1.55, 1.08, 0.05), (2.1, 1.22, 0.98, 0.10), (2.78, 1.0, 0.92, 0.15)], seg=16, name="waist", sq=0.2), "waist", MF_CLOTH)
    fig.add(loft([(2.52, 1.04, 0.94, 0.15), (3.3, 1.0, 1.05, 0.25), (3.95, 0.78, 0.98, 0.30), (4.3, 0.50, 0.62, 0.32)], seg=14, name="chest", sq=0.2), "chest", MF_CLOTH)
    # ragged hem: wedges that break the bottom edge, and a train that drags behind
    for (x, y, dx, dy, s) in ((2.05, -0.35, 0.62, -0.05, 0.20), (1.95, 0.3, 0.5, 0.1, 0.17), (1.6, -0.95, 0.5, -0.3, 0.17), (-2.0, 0.3, -0.5, 0.1, 0.18),
                              (0.6, -1.25, 0.3, -0.42, 0.17), (-0.5, -1.28, -0.25, -0.45, 0.18), (-1.5, -1.0, -0.45, -0.3, 0.16)):
        ob = cone((x, y, s * 1.6), (x + dx * 1.2, y + dy * 1.2, 0.06), s * 1.3, 0.02, seg=5, name="hem")
        ob.data.transform(Matrix.Diagonal((1, 1, 0.4, 1)))
        fig.add(ob, "hips", MF_CLOTH if abs(x) > 1.0 else MF_CLOTH_D)
    for i, (y, ln, ph) in enumerate(((-0.35, 0.50, 0.0), (0.25, 0.42, 0.4))):
        chain(fig, "train%d" % i, "hips", (-2.12, y, 0.18), [ln, ln * 0.8], 0.22, MF_CLOTH_D if i else MF_CLOTH, (-1, 0, -0.12), flat=0.5, sway=0.35, phase=ph)
    # patches, dark tears and glowing rents in the cloth (near side)
    for (x, z, s, col) in ((0.8, 1.0, 0.40, MF_CLOTH_D), (-0.9, 0.6, 0.36, (0.52, 0.56, 0.47)), (-0.45, 2.0, 0.30, MF_CLOTH_D), (0.75, 2.2, 0.24, (0.52, 0.56, 0.47))):
        fig.add(orb(s, (x, mf_robe_y(x, z, -0.02), z), (1.0, 0.16, 0.9), seg=8, name="patch"), "hips" if z < 1.4 else "waist", col, line=0.012)
    for (x, z, s) in ((-1.4, 0.45, 0.38), (0.2, 0.34, 0.34), (1.45, 0.42, 0.30), (-0.15, 1.3, 0.22)):
        fig.add(orb(s, (x, mf_robe_y(x, z, -0.03), z), (0.34, 0.14, 1.0), seg=8, name="tear"), "hips", MF_DARK, glow=0.6, line=0)
    for (x, z, s) in ((-0.70, 1.05, 0.28), (0.40, 1.7, 0.22), (1.3, 1.0, 0.2), (-1.1, 1.55, 0.16)):
        fig.add(orb(s, (x, mf_robe_y(x, z, -0.02), z), (0.26, 0.14, 1.0), seg=8, name="rent"), "hips" if z < 1.4 else "waist", V2["glow"], glow=1.0)
    # rope belt with bone charms
    fig.add(loft([(2.56, 1.09, 0.98, 0.15), (2.70, 1.06, 0.97, 0.16)], seg=14, name="belt", sq=0.2, round_=(False, False)), "waist", V2["leather"])
    for i, (x, ln) in enumerate(((0.65, 0.30), (0.2, 0.40), (-0.3, 0.28))):
        chain(fig, "charm%d" % i, "waist", (x, mf_robe_y(x, 2.56, 0.04), 2.56), [ln, ln * 0.8], 0.07, V2["bone"], (0, -0.1, -1), flat=0.6, taper=0.9, sway=0.5, phase=i * 0.3)
    # loose strips of sailcloth from the shoulders and waist
    for i, (x, ln, ph) in enumerate(((-0.75, 0.62, 0.0), (0.95, 0.5, 0.4), (-0.05, 0.45, 0.7))):
        chain(fig, "strip%d" % i, "waist", (x, mf_robe_y(x, 2.5, 0.05), 2.5), [ln, ln * 0.85, ln * 0.7], 0.17, MF_CLOTH_D if i % 2 else (0.54, 0.60, 0.52),
              (0.0, -0.12, -1), flat=0.4, taper=0.7, sway=0.5, phase=ph)
    # shawl over the hump of her back
    fig.add(orb(0.98, (-0.36, 0, 4.0), (1.0, 1.12, 0.86), seg=12, name="hump"), "chest", MF_SHAWL)
    fig.add(loft([(3.72, 0.98, 1.14, 0.22), (4.10, 0.80, 1.02, 0.24), (4.34, 0.50, 0.62, 0.30)], seg=14, name="shawl", sq=0.2, round_=(False, True)), "chest", MF_SHAWL)
    for i, (x, y) in enumerate(((0.62, -0.92), (0.2, -1.1), (-0.25, -1.12), (-0.7, -0.98))):
        fig.add(cone((x, y, 3.80), (x * 1.05, y * 1.04, 3.36 - 0.12 * (i % 2)), 0.22, 0.0, seg=5, name="fringe"), "chest", MF_SHAWL)
    # ---- head: low, pushed forward. Hooked nose, heavy angled brow, glowing eyes, underslung jaw with needle teeth
    r = 0.85; hx = 1.12; hz = 4.42
    fig.joint("head", (0.62, 0, 4.12), "chest", 1, rest=-6)
    fig.head_c = Vector((hx, 0, hz)); fig.head_r = r
    HS = (0.46, 0.68, 0.60)
    fig.add(loft([(3.9, 0.44, 0.46), (4.3, 0.46, 0.50)], seg=9, at=(0.72, 0, 0), name="neck", round_=(False, False)), "head", MF_SKIN_D, line=0)
    fig.add(loft([(-r * 0.9, r * 0.78, r * 0.86), (0.0, r * 0.90, r * 0.96), (r * 0.62, r * 0.68, r * 0.82, -0.07), (r * 1.08, r * 0.40, r * 0.54, -0.17)],
                 seg=12, axis="x", at=(hx, 0, hz), name="skull", sq=0.2), "head", HS, glow=0.12)
    nb = Vector((hx + r * 1.06, 0, hz - r * 0.06))
    fig.add(orb(r * 0.26, nb, (1.0, 0.8, 1.0), seg=8, name="nose"), "head", HS, glow=0.12, line=0.016)
    fig.add(cone(nb + Vector((0.06, 0, 0.02)), nb + Vector((r * 0.70, 0, -r * 0.62)), r * 0.24, r * 0.05, seg=6, name="hook"), "head", HS, glow=0.12, line=0.018)
    for y in (-1, 1):
        fig.add(orb(r * 0.40, (hx + r * 0.56, y * r * 0.62, hz + r * 0.06), (0.9, 0.7, 0.80), seg=8, name="socket"), "head", MF_DARK, line=0)
        fig.add(orb(r * 0.30, (hx + r * 0.62, y * r * 0.74, hz + r * 0.04), (0.9, 0.6, 0.70), seg=8, name="eye"), "head", V2["glow"], glow=1.5)
        fig.add(block((r * 0.95, r * 0.42, r * 0.22), (hx + r * 0.62, y * r * 0.70, hz + r * 0.36), rot=(-24, "Y"), bevel=0.03, name="brow"), "head", MF_SKIN_D, line=0.012)
        # cheek fins
        fig.add(slab([(0.0, 0.0), (-0.55, 0.42), (-0.36, 0.08), (-0.66, -0.06), (-0.30, -0.14), (-0.42, -0.42), (0.05, -0.2)], 0.05,
                     at=(hx - r * 0.62, y * r * 0.86, hz - r * 0.12), name="fin"), "head", MF_SCALE, glow=0.2, line=0.016)
    for (dx, dz, s) in ((0.10, -0.34, 0.10), (-0.12, -0.42, 0.09), (-0.3, -0.2, 0.09)):
        fig.add(orb(s, (hx + dx, -math.sqrt(max(0.05, (r * 0.95) ** 2 - dx * dx - dz * dz)), hz + dz), (1, 0.3, 0.8), seg=6, name="scale"), "head", MF_SCALE, glow=0.25, line=0)
    jp = Vector((hx + r * 0.10, 0, hz - r * 0.46))
    fig.joint("jaw", jp, "head", -1)
    fig.add(loft([(0.0, r * 0.30, r * 0.76), (r * 0.70, r * 0.28, r * 0.70), (r * 1.22, r * 0.20, r * 0.44, -0.02)], seg=10, axis="x",
                 at=(jp.x, 0, hz - r * 0.74), name="jaw", sq=0.2), "jaw", (0.32, 0.52, 0.50))
    fig.add(cone((jp.x + r * 0.9, 0, hz - r * 0.90), (jp.x + r * 1.30, 0, hz - r * 1.36), r * 0.2, 0.03, seg=6, name="chin"), "jaw", (0.32, 0.52, 0.50), line=0.018)
    fig.add(orb(r * 0.5, (hx + r * 0.74, 0, hz - r * 0.52), (1.2, 1.0, 0.36), seg=10, name="maw"), "head", V2["glow"], glow=1.0)
    for k in range(5):
        x = jp.x + r * (0.50 + 0.17 * k); yy = r * (0.50 - 0.07 * k)
        for y in (-1, 1):
            fig.add(cone((x, y * yy, hz - r * 0.60), (x + 0.02, y * yy, hz - r * (0.24 - 0.02 * (k % 2))), r * 0.055, 0.0, seg=4, name="tooth"), "jaw", V2["white"], glow=0.5, line=0.008)
            fig.add(cone((x + 0.05, y * yy * 0.95, hz - r * 0.36), (x + 0.05, y * yy * 0.95, hz - r * 0.64), r * 0.05, 0.0, seg=4, name="tooth"), "head", V2["white"], glow=0.5, line=0.008)
    # kelp hair from under the crown
    for i, (x, y, ln, ph) in enumerate(((-0.70, -0.60, 0.56, 0.0), (-0.86, -0.1, 0.62, 0.25), (-0.78, 0.5, 0.56, 0.5))):
        chain(fig, "hair%d" % i, "head", (hx + x, y, hz + r * 0.50), [ln, ln * 0.85, ln * 0.7], 0.13, V2["kelp_lt"] if i % 2 else (0.36, 0.56, 0.36),
              (-0.45, 0, -1), flat=0.45, sway=0.9, phase=ph)
    # crown of whale bone and coral
    cc = Vector((hx - 0.08, 0, hz + r * 0.62))
    for ob, col, gl, ln in mf_crown_parts(cc, r * 0.78):
        fig.add(ob, "head", col, glow=gl, line=ln)
    # ---- lantern-fish lure on a stalk that arcs up and forward over the head
    lp = Vector((hx - 0.10, 0, hz + r * 0.92)); par = "head"
    for i, (ln, rest_, r0, r1) in enumerate(((1.15, -10, 0.10, 0.08), (0.80, 44, 0.08, 0.06), (0.60, 50, 0.06, 0.045))):
        jn = "lure%d" % i
        fig.joint(jn, lp, par, 1, rest=rest_)
        q = lp + Vector((0, 0, ln))
        fig.add(cone(lp, q, r0, r1, seg=6, name="stalk"), jn, MF_SKIN_D, line=0.02)
        fig.add(orb(r0 * 1.15, lp, seg=6, name="stalkj"), jn, MF_SKIN_D, line=0.02)
        lp = q; par = jn
    fig.joint("bulb", lp, "lure2", 1)
    bc = lp + Vector((0.0, 0, 0.20))
    fig.add(orb(0.21, bc, (1, 1, 1.15), seg=10, name="bulb_off"), "bulb", (0.30, 0.42, 0.40))
    toggle(fig, "lure_on", "bulb", bc, 1)
    fig.add(orb(0.30, bc, (1, 1, 1.12), seg=12, name="bulb"), "lure_on", MF_LURE, glow=1.5)
    for k in range(8):
        a = math.radians(k * 45 + 20)
        d = Vector((math.cos(a), 0, math.sin(a)))
        fig.add(cone(bc + d * 0.36, bc + d * (0.56 if k % 2 else 0.70), 0.05, 0.0, seg=4, name="ray"), "lure_on", MF_LURE, glow=1.0)
    toggle(fig, "flare", "bulb", bc, 0)
    fig.add(orb(0.50, bc, seg=12, name="flare"), "flare", (0.96, 1.0, 0.80), glow=1.6)
    for k in range(12):
        a = math.radians(k * 30 + 8)
        d = Vector((math.cos(a), 0, math.sin(a)))
        fig.add(cone(bc + d * 0.50, bc + d * (1.05 if k % 2 else 1.5), 0.12, 0.0, seg=4, name="flray"), "flare", MF_LURE, glow=1.0)
    # ---- far arm: wide ragged sleeve, scaled forearm, long claws
    sh = Vector((0.25, 1.08, 3.98)); UA = 1.05; LA = 1.0
    fig.joint("uaL", sh, "chest", -1)
    fig.joint("laL", sh - Vector((0, 0, UA)), "uaL", -1)
    fig.joint("handL", sh - Vector((0, 0, UA + LA)), "laL", -1)
    fig.add(orb(0.40, sh, (1, 1, 0.95), seg=10, name="shoulderL"), "uaL", MF_SHAWL)
    fig.add(loft([(sh.z, 0.30, 0.30), (sh.z - UA * 0.6, 0.33, 0.32), (sh.z - UA - 0.10, 0.40, 0.38)], seg=10, at=(sh.x, sh.y, 0), name="sleeve", round_=(True, False)), "uaL", MF_CLOTH)
    for k in range(5):
        a = math.radians(k * 72 + 30)
        b = Vector((sh.x + 0.34 * math.cos(a), sh.y + 0.32 * math.sin(a), sh.z - UA - 0.06))
        fig.add(cone(b, b + Vector((0.06 * math.cos(a), 0.06 * math.sin(a), -0.30 - 0.08 * (k % 2))), 0.15, 0.0, seg=5, name="cuff"), "uaL", MF_CLOTH_D if k % 2 else MF_CLOTH)
    ez = sh.z - UA
    fig.add(orb(0.19, (sh.x, sh.y, ez), seg=8, name="elbow"), "laL", MF_SKIN)
    fig.add(loft([(ez, 0.17, 0.17), (ez - LA * 0.5, 0.165, 0.15), (ez - LA, 0.115, 0.11)], seg=9, at=(sh.x, sh.y, 0), name="forearm", sq=0.15), "laL", MF_SKIN)
    for k in range(3):
        fig.add(orb(0.075, (sh.x + 0.03, sh.y - 0.16, ez - 0.25 - k * 0.22), (1, 0.35, 0.8), seg=6, name="scale"), "laL", MF_SCALE, glow=0.25, line=0)
    hp = sh - Vector((0, 0, UA + LA))
    fig.add(orb(0.20, (hp.x, hp.y, hp.z - 0.12), (1.0, 0.8, 1.1), seg=9, name="palm"), "handL", MF_SKIN_D)
    for k, dx in enumerate((-1.0, -0.36, 0.36, 1.0)):
        b = Vector((hp.x + dx * 0.13, hp.y, hp.z - 0.24)); m = b + Vector((dx * 0.16, 0, -0.30)); t = m + Vector((dx * 0.02 + 0.10, 0, -0.42))
        fig.add(cone(b, m, 0.065, 0.045, seg=5, name="finger"), "handL", MF_SKIN_D, line=0.016)
        fig.add(cone(m, t, 0.05, 0.0, seg=5, name="claw"), "handL", V2["bone"], glow=0.25, line=0.016)
    # ---- near arm: one long tentacle of eight jointed segments, glow spots along the side, suckers along the top
    p = Vector((0.20, -1.16, 3.95)); par = "chest"
    fig.add(orb(0.54, p + Vector((0, 0.10, 0.04)), (1, 1, 0.95), seg=10, name="shoulderR"), "chest", MF_SHAWL)
    for i in range(8):
        jn = "tn%d" % i
        fig.joint(jn, p, par, -1)
        k = i / 7.0
        col = tuple(lerp(a, b, k) for a, b in zip(MF_SKIN, (0.56, 0.50, 0.70)))
        r0 = MF_TR[i]; r1 = MF_TR[i + 1]; z0 = p.z; z1 = z0 - MF_TL[i]
        fig.add(orb(r0 * 1.03, p, seg=8, name="tj"), jn, col)
        fig.add(loft([(z0, r0, r0), (z1, r1, r1)], seg=9, at=(p.x, p.y, 0), round_=(False, i == 7), name="tseg"), jn, col)
        for f in (0.28, 0.72):
            rr = lerp(r0, r1, f)
            fig.add(orb(rr * 0.36, (p.x + rr * 0.92, p.y, lerp(z0, z1, f)), (0.7, 1, 1), seg=6, name="sucker"), jn, (0.84, 0.86, 0.72), glow=0.3, line=0.01)
        rr = lerp(r0, r1, 0.5)
        fig.add(orb(max(rr * 0.34, 0.035), (p.x - rr * 0.1, p.y - rr * 0.92, lerp(z0, z1, 0.5)), (1, 0.45, 1.5), seg=6, name="spot"), jn, V2["glow"], glow=1.0)
        if i == 0:      # torn sleeve cap over the root of the tentacle
            fig.add(loft([(z0 + 0.14, 0.50, 0.50), (z0 - 0.42, 0.56, 0.55)], seg=10, at=(p.x, p.y, 0), round_=(True, False), name="cap"), jn, MF_CLOTH)
            for q in range(5):
                a = math.radians(q * 72 + 10)
                b = Vector((p.x + 0.48 * math.cos(a), p.y + 0.47 * math.sin(a), z0 - 0.38))
                fig.add(cone(b, b + Vector((0.05 * math.cos(a), 0.05 * math.sin(a), -0.34 - 0.1 * (q % 2))), 0.17, 0.0, seg=5, name="capcuff"), jn, MF_CLOTH_D if q % 2 else MF_CLOTH)
        p = Vector((p.x, p.y, z1)); par = jn
    # ---- effects
    # sweep: a wide crescent low over the ground in front, plus two falling streaks
    toggle(fig, "swipe", "root", (2.5, -1.0, 0.3), 0)
    pts = []; inner = []
    for i in range(13):
        b = math.radians(-28 + i * 9); k = math.sin(math.pi * i / 12)
        pts.append((5.6 * math.cos(b), 5.6 * math.sin(b)))
        inner.append((5.6 * (1 - 0.30 * k) * math.cos(b), 5.6 * (1 - 0.30 * k) * math.sin(b)))
    cres = slab(pts + inner[::-1][1:-1], 0.05, at=(0, 0, 0), name="crescent")
    cres.data.transform(Matrix.Translation((0.3, -0.6, 0.30)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    fig.add(cres, "swipe", MF_FLASH, glow=1.0)
    for k, R in enumerate((4.3, 4.7)):
        arc = []
        for i in range(9):
            a = math.radians(64 - i * 12); arc.append((1.1 + R * math.cos(a), 3.3 + R * math.sin(a)))
        for i in range(8, -1, -1):
            a = math.radians(64 - i * 12); w = 0.93 + 0.06 * abs(i - 4) / 4
            arc.append((1.1 + R * w * math.cos(a), 3.3 + R * w * math.sin(a)))
        fig.add(slab(arc, 0.02, at=(0, -1.3 - 0.05 * k, 0), name="streak"), "swipe", MF_FLASH, glow=1.0)
    # spit: a glowing ink bomb leaving the mouth
    gp = Vector((hx + r * 1.75, 0, hz - r * 0.62))
    toggle(fig, "glob", "head", gp, 0)
    fig.add(orb(0.44, gp + Vector((0.12, 0, 0)), (1.15, 1, 1), seg=12, name="glob"), "glob", MF_INKGLOW, glow=0.95, line=0.03)
    for (dx, dy, dz, s) in ((0.30, -0.36, 0.14, 0.12), (0.05, -0.40, -0.12, 0.10), (0.42, -0.3, -0.14, 0.08), (0.10, -0.32, 0.28, 0.07)):
        fig.add(orb(s, gp + Vector((dx, dy, dz)), seg=6, name="globspot"), "glob", V2["glow"], glow=1.0)
    for (dz, ln) in ((0.12, 0.5), (-0.02, 0.62), (-0.16, 0.44)):
        fig.add(cone(gp + Vector((-0.22, 0, dz)), gp + Vector((-0.22 - ln, 0, dz * 1.4)), 0.09, 0.0, seg=5, name="trail"), "glob", V2["glow"], glow=1.0)
    # death: wide ink pool, with the crown left on top (built stretched: the body is squashed flat by then)
    toggle(fig, "puddle", "root", (0, 0, 0.0), 0)
    fig.add(orb(2.2, (0.3, 0, 0.01), (1.15, 0.8, 0.02), seg=20, name="puddle"), "puddle", (0.10, 0.07, 0.15), glow=0.75, line=0.02)
    for (x, y, s) in ((1.9, -0.5, 0.16), (-1.3, -0.4, 0.13), (0.5, -1.0, 0.12), (2.5, 0.0, 0.10), (-2.0, -0.1, 0.09), (1.2, -1.2, 0.08)):
        fig.add(orb(s, (x, y, 0.03), (1, 1, 0.2), seg=6), "puddle", V2["glow"], glow=1.0)
    toggle(fig, "remains", "root", (0, 0, 0.0), 0)
    un = Matrix.Diagonal((1 / MF_POOL[0], 1 / MF_POOL[0], 1 / MF_POOL[1], 1))
    tilt = Matrix.Translation((0.7, -0.5, 0.30)) @ Matrix.Rotation(math.radians(-14), 4, "Y")
    rem = mf_crown_parts(Vector((0, 0, 0.0)), r * 0.78)
    rem.append((orb(0.2, (0, 0, -0.02), (2.2, 2.2, 0.6), seg=8, name="rmound"), MF_SHAWL, 0.0, 0.016))
    for ob, col, gl, ln in rem:
        ob.data.transform(un @ tilt)
        fig.add(ob, "remains", col, glow=gl, line=ln)
    return fig


# ---------------------------------------------------------------- poses
MF_T_REST = [0, 8, 18, 40, 70, 88, 95, 130]             # hangs, then lies forward along the ground, tip curled up
MF_T_UP = [150, 165, 180, 195, 215, 240, 265, 290]      # raised high overhead, curling back
MF_T_UP2 = [158, 172, 186, 200, 222, 250, 280, 312]
MF_T_SWEEP = [0, 4, 18, 52, 84, 90, 91, 93]             # flat and low across the ground in front
MF_T_AFTER = [-4, 4, 20, 54, 84, 92, 104, 128]
MF_T_CALL = [140, 120, 140, 180, 220, 250, 230, 200]    # raised in an S for the summon
MF_T_BACK = [-10, 0, 14, 40, 72, 88, 95, 120]


def mf_pose(hips=0.0, waist=0.0, chest=0.0, tent=MF_T_REST, claw=(30, 78), wave=None, **kw):
    """Pose from world-space arm directions. tent: world angle of each tentacle segment (0 = hanging, 90 = forward,
    180 = up). claw: world angles of the far arm's upper and lower part. wave: (amplitude, phase) ripple on the tentacle."""
    pit = lambda v: v[0] if isinstance(v, tuple) else v
    tot = MF_LEAN + pit(hips) + pit(waist) + pit(chest)
    ph = list(tent)
    if wave:
        ph = [a + wave[0] * (0.3 + i / 7.0) * math.sin(wave[1] - i * 0.75) for i, a in enumerate(ph)]
    d = dict(hips=hips, waist=waist, chest=chest, jaw=-14, lure0=0, lure1=0, lure2=0, handL=20)
    d["tn0"] = (ph[0] + tot, -8, 0)
    for i in range(1, 8):
        d["tn%d" % i] = ph[i] - ph[i - 1]
    d["uaL"] = claw[0] + tot; d["laL"] = claw[1] - claw[0]
    d.update(kw)
    return d


def mf_idle(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    return mf_pose(chest=1.5 * s, waist=(0.8 * c, 1.0 * s, 0), tent=MF_T_REST, wave=(7, p), claw=(30 + 3 * s, 78 + 6 * c), head=2.5 * c, jaw=-14 - 6 * max(0, s),
                   handL=20 + 10 * math.sin(p - 1.0), lure0=2 * s, lure1=4 * math.sin(p - 0.6), lure2=6 * math.sin(p - 1.2), bulb=8 * math.sin(p - 1.8),
                   squash=(1 - 0.006 * s, 1 + 0.010 * s), tail=(3, t))


def mf_walk(t, i, n):
    p = 2 * math.pi * t; s = math.sin(p); c = math.cos(p)
    # a slow glide: no steps, the robe sways under her and the tentacle drags
    return mf_pose(hips=(3.0 + 1.0 * s), waist=(2.5 * math.sin(p - 0.7), 2.2 * c, 0), chest=3 + 2.0 * math.sin(p - 1.4), tent=MF_T_BACK, wave=(9, p - 0.5),
                   claw=(34 + 5 * s, 82 + 8 * c), head=-4 + 3 * math.sin(p - 2.0), jaw=-14, handL=24 + 10 * c,
                   lure0=-3 + 3 * math.sin(p - 1.6), lure1=-4 + 5 * math.sin(p - 2.2), lure2=-4 + 8 * math.sin(p - 2.8), bulb=-10 + 10 * math.sin(p - 3.4),
                   root=(0.03 * s, 0.04 + 0.04 * math.sin(p - 0.6)), tail=(16, t))


def mf_sweep(t, i, n):
    B = mf_pose()
    up = mf_pose(hips=-3, chest=-16, tent=MF_T_UP, claw=(-20, 30), head=-10, jaw=-24, handL=40, lure0=-8, lure1=-8, lure2=-6,
                 root=(-0.20, 0), squash=(0.97, 1.04), tail=(-20, 0.2))
    up2 = mf_pose(hips=-4, chest=-20, tent=MF_T_UP2, claw=(-28, 24), head=-12, jaw=-30, handL=44, lure0=-10, lure1=-10, lure2=-8,
                  root=(-0.26, 0), squash=(0.96, 1.05), tail=(-24, 0.3))
    hit = mf_pose(hips=5, chest=22, tent=MF_T_SWEEP, claw=(70, 110), head=-22, jaw=-48, handL=10, lure0=12, lure1=14, lure2=12, bulb=20,
                  root=(0.34, 0), squash=(1.05, 0.95), vis=dict(swipe=1), tail=(40, 0.5))
    after = mf_pose(hips=5, chest=25, tent=MF_T_AFTER, claw=(64, 112), head=-20, jaw=-36, handL=10, lure0=6, lure1=8, lure2=8, bulb=-10,
                    root=(0.36, 0), squash=(1.03, 0.97), vis=dict(swipe=0), tail=(10, 0.7))
    return keys([(0.0, B), (0.27, up), (0.62, up2), (0.727, hit), (0.84, after), (1.0, B)], t)


def mf_summon(t, i, n):
    B = mf_pose()
    gather = mf_pose(hips=3, chest=14, tent=MF_T_BACK, claw=(30, 70), head=10, jaw=-4, handL=40, lure0=8, lure1=10, lure2=10,
                     root=(0.06, 0), squash=(1.04, 0.95), tail=(14, 0.2))
    call = mf_pose(hips=-3, chest=-20, tent=MF_T_CALL, claw=(165, 195), head=-22, jaw=-56, handL=-20, lure0=-6, lure1=-12, lure2=-14, bulb=-10,
                   root=(-0.10, 0), squash=(0.95, 1.07), vis=dict(flare=1, lure_on=1), tail=(-26, 0.5))
    call2 = mf_pose(hips=-3, chest=-22, tent=MF_T_CALL, wave=(10, 2.0), claw=(170, 188), head=-24, jaw=-50, handL=-10, lure0=-4, lure1=-10, lure2=-10, bulb=4,
                    root=(-0.12, 0), squash=(0.97, 1.04), vis=dict(flare=1, lure_on=1), tail=(-10, 0.7))
    return keys([(0.0, B), (0.30, gather), (0.50, gather), (0.667, call), (0.86, call2), (0.87, dict(call2, vis=dict(flare=0))), (1.0, B)], t)


def mf_spit(t, i, n):
    B = mf_pose()
    rear = mf_pose(hips=-4, chest=-22, tent=MF_T_BACK, claw=(10, 60), head=-24, jaw=4, handL=30, lure0=-10, lure1=-12, lure2=-10,
                   root=(-0.22, 0), squash=(0.96, 1.05), tail=(-24, 0.2))
    rear2 = dict(rear, chest=-26, head=-28, root=(-0.27, 0))
    lunge = mf_pose(hips=6, chest=12, tent=MF_T_REST, claw=(-10, 30), head=-2, jaw=-58, handL=10, lure0=14, lure1=16, lure2=14, bulb=24,
                    root=(0.40, 0), squash=(1.05, 0.95), vis=dict(glob=1), tail=(44, 0.5))
    hold = dict(lunge, chest=15, head=-4, jaw=-40, squash=(1.02, 0.98), vis=dict(glob=0), tail=(10, 0.7))
    return keys([(0.0, B), (0.30, rear), (0.52, rear2), (0.667, lunge), (0.82, hold), (1.0, B)], t)


def mf_hit(t, i, n):
    B = mf_pose()
    back = mf_pose(hips=-4, chest=-18, tent=MF_T_BACK, wave=(14, 1.0), claw=(-10, 80), head=-22, jaw=-44, handL=40, lure0=-14, lure1=-16, lure2=-16, bulb=-20,
                   root=(-0.18, 0), squash=(1.04, 0.95), tail=(-30, 0.2))
    return keys([(0.0, back), (0.5, mf_pose(chest=-6, root=(-0.08, 0))), (1.0, B)], t)


def mf_die(t, i, n):
    B = mf_pose()
    on = dict(lure_on=1); off = dict(lure_on=0)
    sway1 = mf_pose(hips=-5, chest=-20, tent=MF_T_BACK, wave=(14, 1.0), claw=(-20, 60), head=-24, jaw=-50, handL=40, lure0=-12, lure1=-14, lure2=-14,
                    root=(-0.20, 0), squash=(0.96, 1.05), vis=on, tail=(-30, 0.2))
    sway2 = mf_pose(hips=6, chest=16, tent=MF_T_REST, wave=(10, 3.0), claw=(60, 90), head=16, jaw=-30, handL=10, lure0=14, lure1=18, lure2=20, bulb=30,
                    root=(0.16, 0), squash=(1.02, 0.98), vis=off, tail=(30, 0.5))
    sway3 = mf_pose(hips=-3, chest=-6, tent=MF_T_REST, claw=(20, 50), head=20, jaw=-20, handL=10, lure0=20, lure1=30, lure2=34, bulb=40,
                    root=(-0.06, 0), squash=(1.04, 0.92), vis=off, tail=(-10, 0.7))
    sag = mf_pose(hips=2, chest=24, tent=MF_T_REST, claw=(30, 40), head=34, jaw=-24, handL=0, lure0=30, lure1=44, lure2=44, bulb=40,
                  squash=(1.12, 0.62), vis=dict(lure_on=0, puddle=0.45), tail=(10, 0.8))
    melt = dict(sag, chest=40, head=46, squash=(1.22, 0.26), vis=dict(lure_on=0, puddle=0.8))
    pool = dict(melt, chest=50, squash=MF_POOL, vis=dict(lure_on=0, puddle=1.0), root=(0, -0.02))
    rest = dict(pool, vis=dict(lure_on=0, puddle=1.0, remains=1))
    return keys([(0.0, B), (0.10, sway1), (0.26, sway2), (0.40, sway3), (0.58, sag), (0.76, melt), (0.90, pool), (0.91, rest), (1.0, rest)], t)


register(dict(id="cinder_matron", facing=-1, v2=mf_fig,
              anims=dict(idle=mf_idle, walk=mf_walk, sweep=mf_sweep, summon=mf_summon, spit=mf_spit, hit=mf_hit, die=mf_die)))
