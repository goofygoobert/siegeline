from kit import *
from scenery import *
# Region r1 palettes + layer builders (shared by r1_bgs.py and title.py). Bundle with --lib.
WID = {"sky": 1755 / BG_PX, "far": 2077 / BG_PX, "mid": 2720 / BG_PX, "near": 3900 / BG_PX}

DAY = dict(
    sky=[(0.0, (0.98, 0.64, 0.32)), (0.14, (0.9, 0.44, 0.2)), (0.36, (0.56, 0.22, 0.15)), (0.66, (0.27, 0.11, 0.14)), (1.0, (0.12, 0.06, 0.11))],
    orb=(1.0, 0.84, 0.58), halo=(1.0, 0.62, 0.3), cloud=(0.27, 0.11, 0.13), cloud_lit=(0.88, 0.44, 0.2), spark=(1.0, 0.62, 0.22),
    far_back=((0.62, 0.32, 0.24), (0.45, 0.22, 0.2)), far_front=((0.42, 0.21, 0.19), (0.35, 0.17, 0.17)), fog=(0.9, 0.5, 0.28),
    far_win=(1.0, 0.66, 0.3), far_smoke=(0.32, 0.14, 0.14),
    hill=((0.12, 0.11, 0.1), (0.25, 0.23, 0.19)), rim=(0.62, 0.36, 0.2), scrub=(0.29, 0.3, 0.23), scrub_d=(0.19, 0.2, 0.17),
    sil=(0.13, 0.09, 0.1), lit=(0.34, 0.19, 0.16), win=(1.0, 0.58, 0.22), front=((0.1, 0.09, 0.09), (0.17, 0.15, 0.14)),
    ground=((0.12, 0.09, 0.09), (0.27, 0.22, 0.19)), lip=(0.41, 0.35, 0.31), pebble=(0.18, 0.14, 0.13), bone=(0.4, 0.36, 0.32),
    crackc=(0.82, 0.36, 0.12), grass=(0.33, 0.35, 0.27), grass_d=(0.23, 0.24, 0.2), nsil=(0.11, 0.08, 0.09),
    rock=(0.21, 0.17, 0.17), rock_lit=(0.31, 0.25, 0.23), ash=(0.36, 0.31, 0.29), mist=(0.8, 0.45, 0.28),
)
NIGHT = dict(
    sky=[(0.0, (0.32, 0.1, 0.09)), (0.12, (0.18, 0.06, 0.09)), (0.38, (0.08, 0.04, 0.1)), (1.0, (0.02, 0.02, 0.05))],
    orb=(0.84, 0.76, 0.68), halo=(0.95, 0.38, 0.16), cloud=(0.05, 0.04, 0.08), cloud_lit=(0.42, 0.13, 0.11), spark=(1.0, 0.5, 0.18),
    far_back=((0.17, 0.08, 0.11), (0.12, 0.06, 0.1)), far_front=((0.1, 0.06, 0.09), (0.08, 0.05, 0.08)), fog=(0.4, 0.13, 0.12),
    far_win=(1.0, 0.48, 0.18), far_smoke=(0.1, 0.05, 0.08),
    hill=((0.05, 0.05, 0.06), (0.11, 0.1, 0.11)), rim=(0.46, 0.17, 0.12), scrub=(0.13, 0.14, 0.13), scrub_d=(0.08, 0.09, 0.09),
    sil=(0.05, 0.04, 0.06), lit=(0.17, 0.08, 0.09), win=(1.0, 0.5, 0.18), front=((0.04, 0.04, 0.05), (0.08, 0.07, 0.08)),
    ground=((0.06, 0.05, 0.06), (0.18, 0.15, 0.16)), lip=(0.28, 0.24, 0.26), pebble=(0.09, 0.08, 0.09), bone=(0.27, 0.25, 0.24),
    crackc=(0.85, 0.33, 0.1), grass=(0.17, 0.19, 0.17), grass_d=(0.11, 0.12, 0.11), nsil=(0.05, 0.04, 0.05),
    rock=(0.11, 0.09, 0.1), rock_lit=(0.19, 0.15, 0.16), ash=(0.22, 0.19, 0.21), mist=(0.35, 0.12, 0.12),
)


def build_sky(P, night, calm=None, W=None):
    W = W or WID["sky"] + 0.5; Y = 80
    st = [(0.0, P["sky"][0][1])] + [(0.24 + 0.76 * p, c) for p, c in P["sky"]]
    rect(-0.3, BG_BOT - 0.2, W, BG_TOP + 0.2, Y, P["sky"][0][1], stops=st)
    if night:
        r = random.Random(4)
        for i in range(160):
            x, z = r.uniform(0, W), r.uniform(3.5, BG_TOP); s = r.uniform(0.012, 0.035) * (1 + (z - 3) / 9)
            poly([(x - s, z), (x, z + s * 1.5), (x + s, z), (x, z - s * 1.5)], Y - 1, (0.86, 0.82, 0.92), alpha=r.uniform(0.3, 0.9))
    ox, oz, rad = (17.6, 5.9, 1.2) if night else (18.4, 3.3, 1.35)
    ellipse(ox, oz, rad * 6.5, rad * 6.5, Y - 2, P["halo"], n=64, alpha=0.75 if not night else 0.6, radial=2.2)
    ellipse(ox, oz, rad * 2.4, rad * 2.4, Y - 2.2, P["orb"], n=64, alpha=0.5 if not night else 0.35, radial=2.0)
    ellipse(ox, oz, rad, rad, Y - 3, P["orb"], n=48)
    if night:
        # dim maria and a glowing crack running across the moon
        for (dx, dz, rx, rz) in ((-0.4, 0.3, 0.45, 0.35), (0.35, -0.35, 0.5, 0.3), (0.5, 0.45, 0.22, 0.2)):
            ellipse(ox + dx, oz + dz, rx, rz, Y - 3.5, (0.66, 0.58, 0.54), n=16, wob=0.2, seed=int(dx * 10))
        pts = [(-1.15, 0.35), (-0.6, 0.15), (-0.35, 0.45), (0.1, -0.05), (0.45, 0.1), (0.75, -0.4), (1.1, -0.55)]
        for (a, b) in zip(pts, pts[1:]):
            seg(ox + a[0], oz + a[1], ox + b[0], oz + b[1], 0.12, 0.1, Y - 3.8, (1.0, 0.42, 0.1), glow=1.5)
            seg(ox + a[0], oz + a[1], ox + b[0], oz + b[1], 0.05, 0.04, Y - 3.9, (1.0, 0.82, 0.45), glow=2.0)
        seg(ox + 0.1, oz - 0.05, ox - 0.25, oz - 0.75, 0.07, 0.03, Y - 3.8, (1.0, 0.42, 0.1), glow=1.5)
        seg(ox - 0.35, oz + 0.45, ox - 0.2, oz + 1.0, 0.07, 0.03, Y - 3.8, (1.0, 0.42, 0.1), glow=1.5)
    # cloud streaks with lit undersides
    r = random.Random(7 if night else 3)
    for i in range(9):
        cx, cz = r.uniform(-1, W + 1), r.uniform(3.9, 8.6); rx, rz = r.uniform(2.5, 6.0), r.uniform(0.18, 0.42)
        if calm and calm[0] < cx < calm[1] and cz > calm[2]:
            cz = calm[2] - 0.4 * (i % 3); rx *= 0.6
        puffs = []
        for k in range(r.randint(7, 12)):
            t = k / 8.0
            px = cx - rx + 2 * rx * r.uniform(0.05, 0.95); pr = rz * r.uniform(0.8, 1.8) * (1 - abs(px - cx) / (rx * 1.25))
            puffs.append((px, cz + pr * 0.35, max(pr, 0.12)))
        for (px, pz, pr) in puffs:
            ellipse(px + 0.05, pz - 0.1, pr * 1.9, pr, Y - 5 - i * 0.3, P["cloud_lit"], n=20, wob=0.1, seed=k)
        for (px, pz, pr) in puffs:
            ellipse(px - 0.05, pz - 0.02, pr * 1.9, pr, Y - 5.1 - i * 0.3, P["cloud"], n=20, wob=0.1, seed=k + 9)
    # distant smoke columns at the horizon
    smoke(4.0, 0.5, 7.5, Y - 9, P["far_smoke"], alpha=0.3, seed=2, r0=0.5, drift=3.0)
    smoke(24.0, 1.0, 5.0, Y - 9, P["far_smoke"], alpha=0.22, seed=5, r0=0.4, drift=2.0)
    embers(0, W, 1.5, BG_TOP, Y - 10, 45, P["spark"], seed=9, size=0.035, alpha=0.8, glow=0.5)


def build_far(P, night, W=None):
    W = W or WID["far"] + 0.5; Y = 60
    top = hill_line(-1, W + 1, 2.7, 1.5, seed=31, freq=0.32, jag=0.35, step=0.3)
    # sharpen a few peaks
    r = random.Random(5)
    top = [(x, z + (0.9 * max(0, math.sin(x * 0.55 + 1.3)) ** 6)) for x, z in top]
    band(top, BG_BOT - 0.2, Y, P["far_back"][0], top=P["far_back"][1])
    hz = lambda x: min(top, key=lambda p: abs(p[0] - x))[1]
    for tx, th in ((5.2, 1.5), (16.8, 1.9), (26.5, 1.2)):
        ruin_tower(tx, hz(tx) - 0.15, 0.55, th, Y - 1, P["far_back"][1], win=P["far_win"], seed=int(tx), broken=0.3)
    smoke(16.9, hz(16.8) + th, 4.0, Y - 1.5, P["far_smoke"], alpha=0.3, seed=8, r0=0.25, drift=1.2)
    rect(-1, BG_BOT - 0.3, W + 1, 3.0, Y - 2, P["fog"], alpha=0.55, a_top=0.0)
    top2 = hill_line(-1, W + 1, 1.25, 0.6, seed=37, freq=0.45, jag=0.15, step=0.25)
    band(top2, BG_BOT - 0.2, Y - 3, P["far_front"][0], top=P["far_front"][1])
    hz2 = lambda x: min(top2, key=lambda p: abs(p[0] - x))[1]
    for tx in (2.5, 9.0, 12.5, 21.0, 29.5):
        ruin_tower(tx, hz2(tx) - 0.1, 0.38, r.uniform(0.7, 1.1), Y - 3.5, P["far_front"][1], seed=int(tx * 3), crenel=True)
    for i in range(26):
        tx = r.uniform(0, W)
        dead_tree(tx, hz2(tx) - 0.05, r.uniform(0.5, 0.9), Y - 3.6, P["far_front"][1], seed=i, w=0.03)
    rect(-1, BG_BOT - 0.3, W + 1, 1.2, Y - 4, P["fog"], alpha=0.35, a_top=0.0)
    if night:
        embers(0, W, 0.5, 3.5, Y - 5, 14, P["far_win"], seed=3, size=0.03, glow=1.0)


def build_mid(P, night, W=None):
    W = W or WID["mid"] + 0.5; Y = 40
    top = hill_line(-1, W + 1, 1.7, 1.0, seed=51, freq=0.2, step=0.2)
    rimtop = [(x, z + 0.09) for x, z in top]
    band(rimtop, BG_BOT - 0.2, Y, P["rim"])
    band(top, BG_BOT - 0.2, Y - 0.5, P["hill"][0], top=P["hill"][1], noise=0.12, nscale=0.9)
    hz = lambda x: min(top, key=lambda p: abs(p[0] - x))[1]
    r = random.Random(12)
    # scrub patches (grey-green vale growth)
    for i in range(70):
        x = r.uniform(0, W); z = hz(x) - r.uniform(0.15, 1.6)
        ellipse(x, z, r.uniform(0.3, 0.8), r.uniform(0.1, 0.22), Y - 0.8, P["scrub_d"] if i % 3 else P["scrub"], n=12, wob=0.4, seed=i)
    for i in range(40):
        x = r.uniform(0, W); tuft(x, hz(x) - 0.03, r.uniform(0.18, 0.32), Y - 0.9, P["scrub"], seed=i)
    # landmarks (behind hill crest slightly so they stand on it)
    ruin_tower(6.5, hz(6.5) - 0.1, 1.4, 4.4, Y - 0.3, P["sil"], lit=P["lit"], win=P["win"], seed=4, broken=0.3)
    smoke(6.6, hz(6.5) + 4.0, 4.0, Y - 0.25, P["far_smoke"], alpha=0.35, seed=4, r0=0.35, drift=1.4)
    chapel(21.0, hz(21.0) - 0.1, 1.05, Y - 0.3, P["sil"], P["lit"], P["win"])
    ruin_tower(33.5, hz(33.5) - 0.1, 0.9, 2.6, Y - 0.3, P["sil"], lit=P["lit"], win=P["win"], seed=9, broken=0.5)
    for tx, th, s in ((2.5, 2.4, 1), (11.5, 3.0, 2), (14.8, 2.0, 3), (27.0, 2.7, 4), (29.6, 1.8, 5), (38.5, 2.6, 6)):
        dead_tree(tx, hz(tx) - 0.05, th, Y - 0.6, P["sil"], seed=s, lean=r.uniform(-0.2, 0.2))
    gibbet(25.0, hz(25.0) - 0.1, 2.4, Y - 0.6, P["sil"])
    for k in range(4):
        pike(17.0 + k * 0.45, hz(17.0 + k * 0.45) - 0.1, r.uniform(1.0, 1.5), Y - 0.6, P["sil"], bone=P["lit"], lean=r.uniform(-0.15, 0.15))
    palisade(35.5, 40.5, hz(38) - 0.1, 0.9, Y - 0.6, P["sil"], seed=3)
    banner_pole(9.2, hz(9.2) - 0.1, 2.2, Y - 0.6, P["sil"], P["lit"], seed=2)
    # lower, nearer swell
    top2 = hill_line(-1, W + 1, 0.55, 0.28, seed=57, freq=0.35, step=0.2)
    band([(x, z + 0.06) for x, z in top2], BG_BOT - 0.2, Y - 2, P["rim"], alpha=0.6)
    band(top2, BG_BOT - 0.2, Y - 2.2, P["front"][0], top=P["front"][1], noise=0.1, nscale=1.4)
    hz2 = lambda x: min(top2, key=lambda p: abs(p[0] - x))[1]
    for i in range(18):
        x = r.uniform(0, W); rock(x, hz2(x) - 0.1, r.uniform(0.15, 0.35), Y - 2.4, P["front"][1], seed=i)
    for i in range(30):
        x = r.uniform(0, W); tuft(x, hz2(x) - 0.05, r.uniform(0.15, 0.3), Y - 2.5, P["scrub_d"], seed=i + 100)
    embers(0, W, 1.0, 8.0, Y - 3, 22, P["spark"], seed=21, size=0.045, alpha=0.85, glow=0.8)


def build_near(P, night, W=None):
    W = W or WID["near"] + 0.5; Y = 20
    w = wave(71, base=0.5)
    top = profile(-1, W + 1, lambda x: 0.3 + 0.07 * w(x), 0.2)
    gz = lambda x: 0.3 + 0.07 * w(x)
    r = random.Random(77)
    # sparse dark landmarks behind the walking band (kept low-contrast)
    dead_tree(13.5, gz(13.5), 3.8, Y + 1, P["nsil"], seed=41, lean=0.12)
    dead_tree(45.0, gz(45.0), 4.3, Y + 1, P["nsil"], seed=43, lean=-0.1)
    for k, (dx, h, ln) in enumerate(((0, 1.9, -0.1), (0.4, 1.5, 0.12), (0.75, 2.1, 0.05))):
        pike(27.5 + dx, gz(27.5) + 0.1, h, Y + 1, P["nsil"], bone=P["rock_lit"], lean=ln)
    # broken low wall
    wx = 36.5
    poly([(wx, 0.1), (wx, 0.9), (wx + 0.3, 1.1), (wx + 0.6, 0.85), (wx + 0.9, 1.25), (wx + 1.3, 0.7), (wx + 1.8, 0.8), (wx + 2.2, 0.4), (wx + 2.4, 0.1)], Y + 1, P["nsil"])
    for i in range(5):
        rect(wx + 0.1 + i * 0.45, 0.35 + (i % 2) * 0.25, wx + 0.45 + i * 0.45, 0.42 + (i % 2) * 0.25, Y + 0.9, P["rock"])
    seg(21.0, gz(21) , 21.15, gz(21) + 1.4, 0.12, 0.09, Y + 1, P["nsil"])   # leaning post
    seg(21.15, gz(21) + 1.4, 21.7, gz(21) + 1.0, 0.07, 0.06, Y + 1, P["nsil"])
    # ground body
    g0, g1 = P["ground"]
    dk = tuple(c * 0.62 for c in g0); md = tuple((a + b) / 2 for a, b in zip(g0, g1))
    band(top, BG_BOT - 0.3, Y, g0, stops=[(0.0, dk), (0.55, g0), (0.82, md), (1.0, g1)], noise=0.1, nscale=0.8)
    # ash crust along the top + a soft lighter walking strip
    lip = top + [(x, z - 0.1 - 0.03 * math.sin(x * 3.1)) for x, z in reversed(top)]
    poly(lip, Y - 0.5, P["lip"])
    under = [(x, z - 0.1 - 0.03 * math.sin(x * 3.1)) for x, z in top] + [(x, z - 0.32) for x, z in reversed(top)]
    poly(under, Y - 0.4, P["ground"][1], own=True, alpha=1.0, top=P["ground"][1], noise=0.05)
    # ash drifts, pebbles, bones, ember cracks
    for i in range(60):
        x = r.uniform(0, W); z = r.uniform(-1.4, 0.0)
        ellipse(x, z, r.uniform(0.4, 1.4), r.uniform(0.05, 0.12), Y - 0.6, P["ash"], n=14, wob=0.3, seed=i, alpha=0.35)
    for i in range(130):
        x = r.uniform(0, W); z = r.uniform(-1.5, 0.12) if i % 4 else r.uniform(BG_BOT + 0.1, -1.5); s = r.uniform(0.04, 0.12)
        ellipse(x, z, s * 1.4, s, Y - 0.7, P["pebble"], n=8, wob=0.3, seed=i)
    for i in range(9):
        x = r.uniform(1, W - 1); z = r.uniform(-1.2, -0.15); a = r.uniform(-0.4, 0.4); l = r.uniform(0.25, 0.45)
        x1, z1 = x + math.cos(a) * l, z + math.sin(a) * l
        seg(x, z, x1, z1, 0.05, 0.05, Y - 0.8, P["bone"])
        for (ex, ez) in ((x, z), (x1, z1)):
            ellipse(ex, ez + 0.02, 0.045, 0.035, Y - 0.8, P["bone"], n=8); ellipse(ex, ez - 0.03, 0.045, 0.035, Y - 0.8, P["bone"], n=8)
    for i in range(3):
        x = r.uniform(3, W - 3); z = r.uniform(-1.1, -0.4)
        ellipse(x, z + 0.1, 0.14, 0.13, Y - 0.8, P["bone"], n=12)
        rect(x - 0.07, z - 0.03, x + 0.07, z + 0.03, Y - 0.8, P["bone"])
        ellipse(x + 0.05, z + 0.11, 0.035, 0.04, Y - 0.85, P["pebble"], n=8)
    for i in range(6):
        x = r.uniform(1, W - 4); z = r.uniform(-1.0, -0.25)
        crack(x, z, r.uniform(0.8, 1.8), Y - 0.9, P["crackc"], seed=i, glow=0.0 if not night else 0.3, w=0.03)
    # rocks and grass along the crust
    for i in range(16):
        x = r.uniform(0, W); rock(x, gz(x) - 0.12, r.uniform(0.12, 0.3), Y - 1, P["rock"], seed=i, lit=P["rock_lit"])
    for i in range(55):
        x = r.uniform(0, W); tuft(x, gz(x) - 0.06, r.uniform(0.15, 0.3), Y - 1.1, P["grass"] if i % 2 else P["grass_d"], seed=i)


