from kit import *
from scenery import *
# Region r1 "Saltwick Cove" palettes + layer builders (shared by r1_bgs.py and title.py). Bundle with --lib.
# Day = sunset over the sea; night (r1n) = the cove under the green moon. z=0 is the ground line (y=400 logical).
WID = {"sky": 1755 / BG_PX, "far": 2077 / BG_PX, "mid": 2720 / BG_PX, "near": 3900 / BG_PX}
HZ = 2.9            # sea horizon height (far layer)

DAY = dict(
    sky=[(0.0, (1.0, 0.8, 0.5)), (0.5, (1.0, 0.74, 0.44)), (0.58, (0.98, 0.56, 0.32)), (0.7, (0.82, 0.38, 0.38)),
         (0.84, (0.44, 0.24, 0.4)), (1.0, (0.16, 0.14, 0.3))],
    orb=(1.0, 0.93, 0.72), halo=(1.0, 0.68, 0.38), cloud=(0.5, 0.26, 0.38), cloud_lit=(1.0, 0.7, 0.44),
    gull=(0.24, 0.13, 0.2), moon=None,
    sea=[(0.0, (0.16, 0.16, 0.3)), (0.55, (0.3, 0.24, 0.4)), (0.85, (0.66, 0.4, 0.44)), (1.0, (0.98, 0.7, 0.5))],
    glint=(1.0, 0.86, 0.58), isle=((0.62, 0.38, 0.42), (0.47, 0.28, 0.38)), isle_lit=(0.85, 0.5, 0.42),
    ship=(0.34, 0.2, 0.3), ship_sail=(0.5, 0.3, 0.38), beam=(1.0, 0.85, 0.55), lamp=(1.0, 0.9, 0.62),
    fog=(1.0, 0.72, 0.5), fog_a=0.35,
    cliff=((0.18, 0.11, 0.16), (0.3, 0.17, 0.22)), cliff_lit=(0.78, 0.4, 0.3), strata=(0.24, 0.14, 0.19),
    shore=((0.2, 0.13, 0.17), (0.38, 0.24, 0.26)), foam=(1.0, 0.82, 0.62),
    wood=(0.16, 0.09, 0.12), wood_lit=(0.42, 0.22, 0.2), netc=(0.2, 0.12, 0.15),
    lantern=(1.0, 0.68, 0.32), lcore=(1.0, 0.9, 0.6), win=(1.0, 0.72, 0.38),
    nsil=(0.13, 0.08, 0.1), nsil_lit=(0.36, 0.2, 0.18), ribs=(0.5, 0.36, 0.33), ribs_lit=(0.78, 0.6, 0.48),
    sand=((0.07, 0.05, 0.06), (0.2, 0.14, 0.13), (0.43, 0.29, 0.24), (0.62, 0.44, 0.33)), lip=(0.82, 0.6, 0.43),
    wet=(0.33, 0.22, 0.21), pebble=(0.15, 0.1, 0.1), shell=(0.62, 0.48, 0.4), rock=(0.2, 0.14, 0.16), rock_lit=(0.46, 0.3, 0.27),
    weed=(0.2, 0.22, 0.14), bone=(0.84, 0.72, 0.58), bone_lit=(1.0, 0.86, 0.66), wisp=None,
    crate=(0.42, 0.26, 0.17), crate_lit=(0.6, 0.38, 0.24), crate_d=(0.24, 0.14, 0.1), rope=(0.55, 0.42, 0.28), rope_l=(0.7, 0.55, 0.36),
)
NIGHT = dict(
    sky=[(0.0, (0.1, 0.24, 0.2)), (0.5, (0.09, 0.22, 0.19)), (0.6, (0.06, 0.15, 0.15)), (0.78, (0.03, 0.08, 0.1)), (1.0, (0.01, 0.03, 0.05))],
    orb=(0.78, 1.0, 0.7), halo=(0.35, 0.95, 0.5), cloud=(0.03, 0.08, 0.08), cloud_lit=(0.32, 0.7, 0.42),
    gull=(0.02, 0.05, 0.05), moon=(0.6, 0.86, 0.55),
    sea=[(0.0, (0.01, 0.03, 0.05)), (0.55, (0.03, 0.08, 0.09)), (0.85, (0.06, 0.16, 0.15)), (1.0, (0.16, 0.36, 0.26))],
    glint=(0.6, 1.0, 0.65), isle=((0.06, 0.15, 0.14), (0.04, 0.1, 0.1)), isle_lit=(0.2, 0.42, 0.3),
    ship=(0.03, 0.08, 0.08), ship_sail=(0.08, 0.17, 0.14), beam=(0.55, 1.0, 0.6), lamp=(0.75, 1.0, 0.7),
    fog=(0.3, 0.8, 0.5), fog_a=0.3,
    cliff=((0.02, 0.05, 0.06), (0.05, 0.11, 0.11)), cliff_lit=(0.26, 0.6, 0.38), strata=(0.04, 0.08, 0.09),
    shore=((0.03, 0.06, 0.07), (0.08, 0.15, 0.14)), foam=(0.55, 0.95, 0.65),
    wood=(0.02, 0.04, 0.05), wood_lit=(0.1, 0.2, 0.17), netc=(0.04, 0.08, 0.08),
    lantern=(1.0, 0.62, 0.28), lcore=(1.0, 0.85, 0.55), win=(1.0, 0.66, 0.3),
    nsil=(0.02, 0.04, 0.05), nsil_lit=(0.12, 0.25, 0.2), ribs=(0.16, 0.24, 0.22), ribs_lit=(0.36, 0.52, 0.42),
    sand=((0.02, 0.03, 0.04), (0.06, 0.09, 0.1), (0.14, 0.2, 0.19), (0.24, 0.33, 0.29)), lip=(0.36, 0.52, 0.42),
    wet=(0.1, 0.17, 0.17), pebble=(0.04, 0.06, 0.07), shell=(0.3, 0.4, 0.36), rock=(0.05, 0.09, 0.1), rock_lit=(0.18, 0.34, 0.28),
    weed=(0.08, 0.15, 0.11), bone=(0.5, 0.6, 0.52), bone_lit=(0.7, 0.9, 0.7), wisp=(0.45, 1.0, 0.6),
    crate=(0.11, 0.13, 0.12), crate_lit=(0.2, 0.28, 0.24), crate_d=(0.05, 0.07, 0.07), rope=(0.2, 0.25, 0.21), rope_l=(0.3, 0.38, 0.3),
)


def _clouds(P, W, Y, seed, n, calm=None, zr=(4.4, 8.6)):
    r = random.Random(seed)
    for i in range(n):
        cx, cz = r.uniform(-1, W + 1), r.uniform(*zr); rx, rz = r.uniform(2.0, 5.5), r.uniform(0.16, 0.36)
        if calm and calm[0] < cx < calm[1] and cz > calm[2]:
            cz = calm[2] - 0.4 * (i % 3); rx *= 0.6
        puffs = []
        for k in range(r.randint(6, 11)):
            px = cx - rx + 2 * rx * r.uniform(0.05, 0.95); pr = rz * r.uniform(0.8, 1.8) * (1 - abs(px - cx) / (rx * 1.25))
            puffs.append((px, cz + pr * 0.35, max(pr, 0.12)))
        for k, (px, pz, pr) in enumerate(puffs):
            ellipse(px + 0.04, pz - 0.09, pr * 2.1, pr, Y - 5 - i * 0.3, P["cloud_lit"], n=20, wob=0.1, seed=k)
        for k, (px, pz, pr) in enumerate(puffs):
            ellipse(px - 0.04, pz - 0.0, pr * 2.1, pr, Y - 5.1 - i * 0.3, P["cloud"], n=20, wob=0.1, seed=k + 9)


def build_sky(P, night, calm=None, W=None):
    W = W or WID["sky"] + 0.5; Y = 80
    rect(-0.3, BG_BOT - 0.2, W, BG_TOP + 0.2, Y, P["sky"][0][1], stops=P["sky"])
    if night:
        r = random.Random(4)
        for i in range(170):
            x, z = r.uniform(0, W), r.uniform(4.0, BG_TOP); s = r.uniform(0.012, 0.035) * (1 + (z - 3) / 9)
            poly([(x - s, z), (x, z + s * 1.5), (x + s, z), (x, z - s * 1.5)], Y - 1, (0.8, 0.95, 0.86), alpha=r.uniform(0.3, 0.9))
        # the huge green moon
        ox, oz, rad = 8.2, 6.0, 2.3
        ellipse(ox, oz, rad * 3.6, rad * 3.6, Y - 2, P["halo"], n=72, alpha=0.55, radial=2.0)
        ellipse(ox, oz, rad * 1.6, rad * 1.6, Y - 2.2, P["orb"], n=72, alpha=0.45, radial=1.6)
        ellipse(ox, oz, rad, rad, Y - 3, P["orb"], n=72, glow=0.4)
        rr = random.Random(12)
        for (dx, dz, rx, rz) in ((-0.7, 0.5, 0.75, 0.55), (0.6, -0.6, 0.85, 0.5), (0.85, 0.8, 0.38, 0.32), (-0.9, -0.9, 0.4, 0.3),
                                 (0.1, 0.05, 0.3, 0.25), (-1.4, -0.1, 0.25, 0.4)):
            ellipse(ox + dx, oz + dz, rx, rz, Y - 3.5, P["moon"], n=18, wob=0.25, seed=int(dx * 10 + 50))
        for i in range(10):
            a = rr.uniform(0, math.tau); d = rr.uniform(0.2, 1.9)
            ellipse(ox + math.cos(a) * d, oz + math.sin(a) * d, 0.11, 0.1, Y - 3.6, P["moon"], n=10)
        _clouds(P, W, Y, 7, 7, calm, zr=(3.6, 8.4))
        # green fog low over the horizon
        rect(-0.3, BG_BOT, W, HZ + 2.2, Y - 8, P["fog"], alpha=0.35, a_top=0.0)
    else:
        ox, oz, rad = 17.4, 3.35, 1.2
        ellipse(ox, oz, rad * 7.5, rad * 7.5, Y - 2, P["halo"], n=72, alpha=0.7, radial=2.4)
        ellipse(ox, oz, rad * 2.6, rad * 2.6, Y - 2.2, P["orb"], n=64, alpha=0.55, radial=1.8)
        ellipse(ox, oz, rad, rad, Y - 3, P["orb"], n=64, glow=0.3)
        # thin cloud bars across the sun
        for (dz, l, th) in ((0.25, 3.2, 0.07), (-0.2, 2.4, 0.05), (0.75, 2.0, 0.04)):
            ellipse(ox + 0.3, oz + dz, l, th, Y - 3.2, P["cloud"], n=24, alpha=0.7)
        _clouds(P, W, Y, 3, 9, calm)
        r = random.Random(5)
        for i in range(9):
            gull(r.uniform(3, W - 3), r.uniform(4.5, 7.8), r.uniform(0.12, 0.22), Y - 9, P["gull"], flap=r.uniform(-0.2, 0.3))


def build_far(P, night, W=None):
    W = W or WID["far"] + 0.5; Y = 60
    # sea, horizon at HZ
    rect(-1, BG_BOT - 0.3, W + 1, HZ, Y, P["sea"][0][1], stops=P["sea"])
    sx = 8.8 if night else 18.0          # glitter path under the sun / moon
    r = random.Random(17)
    for i in range(70):
        t = r.random() ** 1.3; zz = HZ - 0.05 - t * 3.6
        spread = 0.5 + t * 2.6; xx = sx + r.gauss(0, spread * 0.6)
        ellipse(xx, zz, r.uniform(0.15, 0.6) * (0.4 + t), 0.025 + 0.02 * t, Y - 0.5, P["glint"], n=10, alpha=r.uniform(0.4, 0.9) * (1.0 - 0.5 * t), glow=0.5)
    wave_lines(-1, W + 1, BG_BOT, HZ - 0.15, Y - 0.4, 90, P["sea"][2][1], alpha=0.55, seed=3, lmin=0.4, lmax=1.6)
    # distant islands on the horizon (back row: haze)
    for (cx, w, h, seed) in ((3.0, 4.5, 0.9, 1), (24.5, 6.0, 1.3, 2), (30.0, 3.0, 0.6, 3)):
        prof = hill_line(cx - w / 2, cx + w / 2, 0, 1, seed=seed, freq=1.1, step=0.15)
        prof = [(x, HZ - 0.05 + max(0.0, h * max(0.0, math.sin(math.pi * (x - cx + w / 2) / w)) ** 0.7 * (0.8 + 0.25 * z))) for x, z in prof]
        band(prof, HZ - 0.12, Y - 1, P["isle"][0])
    # lighthouse island (front row)
    lx = 11.5
    prof = profile(lx - 2.6, lx + 3.2, lambda x: HZ - 0.08 + max(0.0, 1.05 - 0.35 * abs(x - lx) ** 1.25 + 0.08 * math.sin(x * 7)), 0.12)
    band(prof, HZ - 0.15, Y - 2, P["isle"][1])
    band([(x, z) for x, z in prof if x > lx + 0.2], HZ - 0.15, Y - 2.05, P["isle_lit"], alpha=0.35)
    lighthouse(lx, HZ + 0.9, 1.7, Y - 2.2, P["isle"][1], P["isle_lit"], P["lamp"], stripe=P["isle"][0] if not night else None,
               beam=P["beam"], beam_a=0.22 if not night else 0.3, beam_dir=1)
    rect(lx + 0.7, HZ + 0.72, lx + 1.2, HZ + 1.05, Y - 2.2, P["isle"][1])        # keeper's hut
    poly([(lx + 0.62, HZ + 1.05), (lx + 0.95, HZ + 1.3), (lx + 1.28, HZ + 1.05)], Y - 2.2, P["isle"][1])
    # ships
    ship_sil(6.5, HZ - 0.12, 0.42, Y - 2.5, P["ship"], sail=P["ship_sail"], seed=1, flag=P["ship"])
    ship_sil(20.5, HZ - 0.08, 0.28, Y - 1.5, P["isle"][0], seed=2, masts=2)
    ship_sil(27.0, HZ - 0.2, 0.55, Y - 2.6, P["ship"], sail=P["ship_sail"], seed=3, wreck=night)
    # haze band hugging the horizon
    rect(-1, HZ - 0.6, W + 1, HZ + 0.9, Y - 3, P["fog"], alpha=P["fog_a"] * 0.6, a_top=0.0)
    if night:
        r = random.Random(8)
        for i in range(9):
            wisp(r.uniform(1, W - 1), r.uniform(HZ - 2.6, HZ - 0.5), r.uniform(0.18, 0.35), Y - 3.5, P["wisp"], alpha=0.5)
        rect(-1, HZ - 1.6, W + 1, HZ + 0.4, Y - 4, P["fog"], alpha=0.18, a_top=0.0)


def build_mid(P, night, W=None):
    W = W or WID["mid"] + 0.5; Y = 40
    r = random.Random(12)
    # left headland cliff
    cl = [(-1, BG_BOT), (-1, 5.6), (0.6, 5.9), (1.4, 5.5), (2.3, 5.7), (3.1, 4.9), (3.6, 4.3), (4.4, 3.9), (4.9, 2.6),
          (5.6, 2.1), (6.4, 1.2), (7.2, 0.8), (7.6, BG_BOT)]
    poly(cl, Y, P["cliff"][0], own=True, top=P["cliff"][1], noise=0.15, nscale=1.4)
    poly([(2.3, 5.7), (3.1, 4.9), (3.6, 4.3), (4.4, 3.9), (4.9, 2.6), (5.6, 2.1), (6.4, 1.2), (6.2, 1.1), (5.3, 1.9), (4.6, 2.4),
          (4.1, 3.6), (3.3, 4.1), (2.8, 4.7)], Y - 0.1, P["cliff_lit"], alpha=0.75)
    for k in range(5):
        zz = 0.6 + k * 0.95; seg(-1, zz, 5.2 - k * 0.7, zz + 0.15, 0.06, 0.04, Y - 0.15, P["strata"])
    # right headland with a sea arch, and a sea stack
    hr = [(31.5, BG_BOT), (32.0, 1.0), (32.7, 2.4), (33.2, 3.9), (34.4, 4.6), (35.6, 4.4), (36.5, 5.2), (38.0, 5.0),
          (39.3, 5.6), (40.5, 5.3), (W + 1, 5.6), (W + 1, BG_BOT)]
    poly(hr, Y, P["cliff"][0], own=True, top=P["cliff"][1], noise=0.15, nscale=1.4)
    # the arch opening (sea shows through: drawn as far-sea colour)
    ap = [(34.2, 0.6)] + [(35.4 + 1.1 * math.cos(a), 0.6 + 2.0 * math.sin(a)) for a in [math.pi * (1 - i / 14) for i in range(15)]] + [(36.6, 0.6)]
    poly(ap, Y - 0.2, P["sea"][2][1], own=True, top=P["sea"][3][1])
    poly([(32.0, 1.0), (32.7, 2.4), (33.2, 3.9), (34.4, 4.6), (34.1, 4.3), (33.0, 3.6), (32.5, 2.2), (31.8, 1.0)], Y - 0.1, P["cliff_lit"], alpha=0.75)
    for k in range(4):
        zz = 1.2 + k * 1.0; seg(36.8, zz, W + 1, zz + 0.12, 0.06, 0.04, Y - 0.15, P["strata"])
    stack = [(27.6, BG_BOT), (27.8, 1.6), (28.1, 2.9), (28.6, 3.2), (29.0, 2.7), (29.3, 1.4), (29.6, BG_BOT)]
    poly(stack, Y - 0.3, P["cliff"][0], own=True, top=P["cliff"][1], noise=0.12)
    poly([(28.1, 2.9), (28.6, 3.2), (28.5, 2.9), (28.2, 2.6)], Y - 0.35, P["cliff_lit"], alpha=0.7)
    # low rocky shore running the whole width
    sh = hill_line(-1, W + 1, 0.75, 0.3, seed=51, freq=0.5, jag=0.12, step=0.2)
    band([(x, z + 0.07) for x, z in sh], BG_BOT - 0.2, Y - 1, P["foam"], alpha=0.5)
    band(sh, BG_BOT - 0.2, Y - 1.1, P["shore"][0], top=P["shore"][1], noise=0.12, nscale=1.1)
    hz = lambda x: min(sh, key=lambda p: abs(p[0] - x))[1]
    for i in range(22):
        x = r.uniform(0, W); rock(x, hz(x) - 0.08, r.uniform(0.2, 0.45), Y - 1.2, P["shore"][0], seed=i, lit=P["shore"][1])
    # wrecked hull on the shore
    hull_wreck(12.6, hz(12.6) - 0.15, 0.95, Y - 0.6, P["wood"], lit=P["wood_lit"], seed=4)
    # nets drying on poles
    for px in (7.9, 9.6, 11.0):
        seg(px, hz(px) - 0.2, px + r.uniform(-0.06, 0.06), hz(px) + 2.0, 0.1, 0.08, Y - 1.3, P["wood"])
    net(7.9, hz(7.9) + 1.95, 9.6, hz(9.6) + 1.9, 0.35, Y - 1.25, P["netc"], n=8, m=5, drop=0.85)
    net(9.6, hz(9.6) + 1.9, 11.0, hz(11.0) + 1.95, 0.25, Y - 1.25, P["netc"], n=6, m=4, drop=0.6)
    # rickety jetty out into the water, shack on stilts
    jz = 1.55
    jetty(17.4, 23.8, jz, Y - 1.4, P["wood"], plank=P["wood_lit"], seed=2)
    stilt_hut(24.6, jz + 0.1, 0.95, Y - 1.5, P["wood"], P["wood_lit"], P["win"], seed=3)
    lantern_post(17.6, hz(17.6), 2.0, Y - 1.6, P["wood"], P["lantern"], P["lcore"], r=0.7, alpha=0.5 if not night else 0.65)
    lantern_post(22.6, jz, 1.4, Y - 1.6, P["wood"], P["lantern"], P["lcore"], r=0.6, arm=-1, alpha=0.5 if not night else 0.65)
    lantern_post(30.6, hz(30.6), 1.7, Y - 1.6, P["wood"], P["lantern"], P["lcore"], r=0.6, alpha=0.5 if not night else 0.65)
    glowdot(25.0, jz + 0.65, 0.9, Y - 1.45, P["lantern"], alpha=0.35)
    # rowboat pulled up
    poly([(14.9, hz(15.5) + 0.05), (15.1, hz(15.5) + 0.45), (16.6, hz(15.5) + 0.5), (16.8, hz(15.5) + 0.05)], Y - 1.3, P["wood"])
    seg(15.0, hz(15.5) + 0.48, 16.7, hz(15.5) + 0.52, 0.06, 0.06, Y - 1.31, P["wood_lit"])
    # foam lines along the shore
    wave_lines(-1, W + 1, 0.15, 0.5, Y - 1.05, 35, P["foam"], alpha=0.35, seed=8, lmin=0.4, lmax=1.4, th=0.02)
    if night:
        rr = random.Random(30)
        for x in (5.0, 15.5, 21.0, 26.5, 32.5, 38.0):
            wisp(x + rr.uniform(-0.6, 0.6), rr.uniform(1.4, 2.6), rr.uniform(0.25, 0.4), Y - 2.0, P["wisp"], alpha=0.55)
        rect(-1, 0.3, W + 1, 3.2, Y - 2.5, P["fog"], alpha=0.24, a_top=0.0)
    else:
        rect(-1, BG_BOT - 0.3, W + 1, 2.2, Y - 2.5, P["fog"], alpha=0.12, a_top=0.0)
        for i in range(5):
            gull(r.uniform(2, W - 2), r.uniform(3.0, 6.0), r.uniform(0.18, 0.28), Y - 2.6, P["gull"], flap=r.uniform(-0.2, 0.3))


def build_near(P, night, W=None):
    W = W or WID["near"] + 0.5; Y = 20
    w = wave(71, base=0.5)
    gz = lambda x: 0.3 + 0.07 * w(x)
    top = profile(-1, W + 1, gz, 0.2)
    r = random.Random(77)
    # sparse landmarks behind the walking band (kept low-contrast)
    sea_ribs(8.5, gz(8.5) - 0.05, 0.95, Y + 1, P["ribs"], lit=P["ribs_lit"], n=6, seed=2)
    anchor_sil(25.0, gz(25.0) - 0.1, 0.95, Y + 1, P["nsil"], lean=0.35)
    seg(34.0, gz(34) - 0.1, 34.3, gz(34) + 2.6, 0.2, 0.14, Y + 1, P["nsil"])       # broken mast stuck in the sand
    seg(34.3, gz(34) + 2.2, 35.2, gz(34) + 2.35, 0.09, 0.07, Y + 1, P["nsil"])
    seg(34.25, gz(34) + 2.5, 36.4, gz(34) + 0.05, 0.035, 0.035, Y + 1, P["nsil"])
    lantern_post(34.3, gz(34) + 1.5, 0.6, Y + 0.9, P["nsil"], P["lantern"], P["lcore"], r=0.7, arm=-1, alpha=0.4 if not night else 0.55)
    for k, (dx, ln) in enumerate(((0, -0.08), (0.5, 0.1))):
        seg(45.5 + dx, gz(45.5) - 0.2, 45.5 + dx + ln, gz(45.5) + 1.3 - 0.3 * k, 0.12, 0.1, Y + 1, P["nsil"])   # mooring posts
    net(45.5, gz(45.5) + 1.25, 46.1, gz(45.5) + 1.0, 0.1, Y + 0.95, P["nsil"], n=3, m=3, drop=0.6)
    hull_wreck(53.5, gz(53.5) - 0.1, 0.6, Y + 1, P["nsil"], lit=P["nsil_lit"], seed=9, flip=True)
    # ground body: lit sand at the top, dark plain sand below the ground line
    s0, s1, s2, s3 = P["sand"]
    band(top, BG_BOT - 0.3, Y, s1, stops=[(0.0, s0), (0.45, s1), (0.72, s2), (1.0, s3)], noise=0.08, nscale=0.8)
    lip = top + [(x, z - 0.1 - 0.03 * math.sin(x * 3.1)) for x, z in reversed(top)]
    poly(lip, Y - 0.5, P["lip"])
    # wet-sand streaks, shingle, shells
    for i in range(45):
        x = r.uniform(0, W); z = r.uniform(-1.3, 0.05)
        ellipse(x, z, r.uniform(0.5, 1.6), r.uniform(0.04, 0.09), Y - 0.6, P["wet"], n=14, wob=0.3, seed=i, alpha=0.35)
    for i in range(110):
        x = r.uniform(0, W); z = r.uniform(-1.0, 0.15) if i % 5 else r.uniform(BG_BOT + 0.1, -1.0); s = r.uniform(0.04, 0.12)
        ellipse(x, z, s * 1.4, s, Y - 0.7, P["pebble"], n=8, wob=0.3, seed=i)
    for i in range(14):
        x = r.uniform(1, W - 1); z = r.uniform(-1.0, 0.0); s = r.uniform(0.07, 0.12)
        poly([(x, z)] + [(x + math.cos(a) * s * 1.3, z + math.sin(a) * s * 1.2) for a in [math.pi * (0.1 + 0.8 * k / 6) for k in range(7)]],
             Y - 0.75, P["shell"])
    # rocks with weed along the crest
    for i in range(14):
        x = r.uniform(0, W); s = r.uniform(0.14, 0.34)
        rock(x, gz(x) - 0.12, s, Y - 1, P["rock"], seed=i, lit=P["rock_lit"])
        for k in range(2):
            ellipse(x - s * 0.5 + k * s * 0.8, gz(x) - 0.12 + s * 0.5, s * 0.45, s * 0.14, Y - 1.05, P["weed"], n=10, wob=0.4, seed=i * 3 + k)
    # cargo washed ashore: crates, barrels, rope
    cx = 39.5
    crate(cx, gz(cx) - 0.12, 0.32, Y - 1.1, P["crate"], P["crate_lit"], P["crate_d"], rot=0.05)
    crate(cx + 0.75, gz(cx) - 0.12, 0.26, Y - 1.15, P["crate"], P["crate_lit"], P["crate_d"], rot=-0.12)
    barrel(cx - 0.9, gz(cx) - 0.12, 0.34, Y - 1.2, P["crate"], P["crate_lit"], P["crate_d"])
    barrel(16.0, gz(16) - 0.15, 0.3, Y - 1.1, P["crate"], P["crate_lit"], P["crate_d"], lying=True)
    crate(29.5, gz(29.5) - 0.15, 0.24, Y - 1.1, P["crate"], P["crate_lit"], P["crate_d"], rot=0.3)
    rope_coil(20.5, gz(20.5) - 0.14, 0.42, Y - 1.1, P["rope"], P["rope_l"])
    rope_coil(49.0, gz(49) - 0.14, 0.36, Y - 1.1, P["rope"], P["rope_l"])
    for i in range(7):
        x = r.uniform(1, W - 2); driftwood(x, gz(x) - 0.14, r.uniform(0.5, 1.1), Y - 1.08, P["crate_d"], seed=i)
    if night:
        rect(-1, -0.2, W + 1, 2.6, Y - 2, P["fog"], alpha=0.22, a_top=0.0)
