from kit import *
from scenery import *
# fx atlas sources: 384x384 cells at 96 px/u (packed to 72 ppu), side camera (no elevation), anchor = cell centre.
# frames: 1 arrow, 2 bolt, 3 spit, 4 fireball, 5 ember_stone, 6-11 fire_patch, 12-19 blast, 20-25 flare
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 32
CELL, PPU_R = 384, 96
S.render.resolution_x = S.render.resolution_y = CELL
sprite_lights()
GOLD = (1.0, 0.86, 0.5); YEL = (1.0, 0.9, 0.55); ORG = EMBER; RED = (0.85, 0.25, 0.08)
R90 = math.radians(90)


def halo(x, z, r, color, a=0.6, p=2.0):
    ellipse(x, z, r, r, 1.5, color, n=48, alpha=a, radial=p)   # behind the 3D shapes


def annulus(x, z, r0, r1, color, alpha, glow=1.0, n=64):
    bm = bmesh.new(); outer = []; inner = []
    for i in range(n):
        a = i / n * math.tau
        outer.append(bm.verts.new((x + math.cos(a) * r1, -1.5, z + math.sin(a) * r1)))
        inner.append(bm.verts.new((x + math.cos(a) * r0, -1.5, z + math.sin(a) * r0)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((outer[i], outer[j], inner[j], inner[i]))
    ob = _mesh_obj("ring", bm); ob.data.materials.append(fmat(color, alpha, glow))


def arrow(x):
    box((1.0, 0.05, 0.05), WOOD, (x - 0.05, 0, 0), bevel=0.01, name="shaft")
    cyl(0.07, 0.2, (0.7, 0.7, 0.74), (x + 0.52, 0, 0), rot=(0, R90, 0), r2=0.0, seg=8)
    for sz in (1, -1):
        box((0.22, 0.03, 0.08), CRIMSON, (x - 0.45, 0, sz * 0.05), rot=(0, math.radians(15 * sz), 0), bevel=0.0, name="fletch")


def bolt(x):
    halo(x + 0.35, 0, 0.75, ORG, a=0.55)
    box((1.5, 0.09, 0.09), WOOD_D, (x - 0.15, 0, 0), bevel=0.02, name="shaft")
    cyl(0.13, 0.36, IRON, (x + 0.78, 0, 0), rot=(0, R90, 0), r2=0.0, seg=8)
    box((0.1, 0.13, 0.13), BRASS, (x + 0.56, 0, 0), name="band")
    for sz in (1, -1):
        box((0.3, 0.04, 0.12), CRIMSON, (x - 0.78, 0, sz * 0.07), rot=(0, math.radians(15 * sz), 0), bevel=0.0, name="fletch")
    for k, (dz, l, s) in enumerate(((0.0, 0.95, 1.0), (0.09, 0.6, 0.7), (-0.08, 0.7, 0.75))):
        cyl(0.16 * s, l, ORG, (x + 0.5 - l / 2, -0.05 - k * 0.02, dz), rot=(0, -R90, 0), r2=0.0, seg=7, glow=1.3, name="fl")
    cyl(0.09, 0.5, YEL, (x + 0.38, -0.15, 0), rot=(0, -R90, 0), r2=0.0, seg=7, glow=1.6, name="fl_in")


def spit(x):   # enemy glob, travels LEFT (trail to the right)
    halo(x, 0, 0.55, ORG, a=0.45)
    ball(0.2, ORG, (x, 0, 0), scale=(1.15, 1, 0.95), glow=1.2)
    ball(0.11, YEL, (x - 0.04, -0.12, 0.03), glow=1.6)
    for k, (dx, dz, r) in enumerate(((0.32, 0.06, 0.09), (0.5, -0.04, 0.06), (0.64, 0.08, 0.04))):
        ball(r, ORG, (x + dx, 0, dz), glow=1.2)
    for (dx, dz) in ((0.1, 0.12), (-0.12, -0.08), (0.05, -0.15)):
        ball(0.04, (0.2, 0.08, 0.05), (x + dx, -0.17, dz))


def fireball(x):   # travels LEFT (flame tail to the right)
    halo(x, 0, 0.95, ORG, a=0.55)
    for k, (dz, l, s) in enumerate(((0.0, 1.0, 1.0), (0.17, 0.7, 0.7), (-0.16, 0.75, 0.7), (0.3, 0.45, 0.45), (-0.28, 0.5, 0.45))):
        cyl(0.28 * s, l, ORG if k % 2 == 0 else RED, (x + 0.15 + l / 2, 0.1, dz), rot=(0, R90, 0), r2=0.0, seg=8, glow=1.2, name="tail")
    ball(0.36, ORG, (x, 0, 0), glow=1.3)
    ball(0.24, YEL, (x - 0.06, -0.2, 0.02), glow=1.8)


def ember_stone(x):   # ember-rain rock, falls DOWN (flame trail up)
    halo(x, 0.1, 0.8, ORG, a=0.45)
    for k, (dx, l, s) in enumerate(((0.0, 0.9, 1.0), (0.13, 0.55, 0.65), (-0.13, 0.6, 0.65))):
        cyl(0.24 * s, l, ORG, (x + dx, 0.1, 0.15 + l / 2), r2=0.0, seg=7, glow=1.2, name="trail")
    ball(0.27, (0.28, 0.2, 0.18), (x, 0, 0), seg=7, scale=(1.1, 1, 0.95))
    for a in (0.3, 1.4, 2.4):
        box((0.04, 0.03, 0.3), YEL, (x + math.cos(a) * 0.08, -0.26, math.sin(a) * 0.08), rot=(0, a, 0), glow=1.6, name="crack")


def fire_patch(x, f):
    t = f / 6.0
    ball(0.85, (0.14, 0.11, 0.11), (x, 0, 0.0), scale=(1.0, 0.6, 0.12), seg=20, name="scorch")
    for i, (dx, base, ph) in enumerate(((-0.55, 0.55, 0.0), (-0.22, 0.85, 2.1), (0.12, 1.0, 4.0), (0.45, 0.7, 1.1), (0.72, 0.45, 3.2))):
        h = base * (0.78 + 0.22 * math.sin(math.tau * t + ph))
        lean = 0.12 * math.sin(math.tau * t + ph * 1.7)
        cyl(0.2, h, ORG if i % 2 else RED, (x + dx + lean * 0.5, 0.05 - i * 0.01, h / 2), r2=0.0, seg=7, glow=1.2, name="fp",
            rot=(0, lean, 0))
        cyl(0.11, h * 0.6, YEL, (x + dx + lean * 0.3, -0.12, h * 0.3), r2=0.0, seg=7, glow=1.6, name="fp_in", rot=(0, lean, 0))
    rr = random.Random(f)
    for k in range(3):
        ball(0.035, YEL, (x + rr.uniform(-0.7, 0.7), -0.2, 0.4 + ((k * 0.37 + t) % 1.0) * 1.0), glow=1.8, name="spark")


def blast(x, f):
    t = f / 7.0
    rr = random.Random(5)
    r = (0.45, 0.85, 1.1, 1.22, 1.25, 1.2, 1.05, 0.9)[f]
    fire = (1.0, 0.95, 0.75, 0.55, 0.3, 0.1, 0.0, 0.0)[f]
    smk = (0.0, 0.0, 0.15, 0.4, 0.7, 0.9, 0.8, 0.5)[f]
    if f < 5:
        halo(x, 0.0, r * 1.7, ORG if f else YEL, a=0.7 * (1 - f / 5))
    if f <= 1:
        annulus(x, 0, r * 1.15, r * 1.3, YEL, 0.8)
    for k in range(9):
        a = k / 9 * math.tau + 0.3; d = r * 0.45 * rr.uniform(0.6, 1.0); br = r * rr.uniform(0.38, 0.55)
        px, pz = x + math.cos(a) * d, math.sin(a) * d * 0.85 + r * 0.1 * t
        if smk > 0.05 and (k % 3 != 0 or smk > 0.5):
            ball(br * (0.6 + 0.6 * smk), SMOKE if k % 2 else SMOKE_L, (px, 0.25, pz + smk * 0.3), name="smk")
        if fire > 0.05:
            ball(br * fire, ORG if k % 2 else RED, (px, -0.05, pz), glow=1.3, name="fire")
    if fire > 0.3:
        ball(r * 0.45 * fire, YEL, (x, -0.4, 0), glow=1.8, name="core")
    if 1 <= f <= 5:
        for k in range(7):
            a = k / 7 * math.tau + 0.5; d = r * (0.9 + 0.5 * t)
            box((0.12, 0.1, 0.1), (0.2, 0.15, 0.14), (x + math.cos(a) * d, -0.3, math.sin(a) * d), rot=(a, a, 0), name="debris")
            if f <= 3:
                ball(0.05, YEL, (x + math.cos(a + 0.4) * d * 1.1, -0.3, math.sin(a + 0.4) * d * 1.1), glow=1.8, name="spark")


def flare(x, f):
    t = f / 5.0
    R = 0.35 + 1.45 * t; w = 0.28 * (1 - t) + 0.06; a = 1.0 - 0.75 * t
    annulus(x, 0, R - w, R, GOLD, a, glow=1.0)
    annulus(x, 0, max(R - w * 2.4, 0.01), R - w, (1.0, 0.7, 0.3), a * 0.35, glow=0.6)
    ellipse(x, 0, R * 1.05, R * 1.05, -1.0, GOLD, n=48, alpha=0.5 * (1 - t), radial=1.5)
    for k in range(8):
        ang = k / 8 * math.tau + 0.2
        seg(x + math.cos(ang) * R * 0.95, math.sin(ang) * R * 0.95, x + math.cos(ang) * (R + 0.35 * (1 - t) + 0.1),
            math.sin(ang) * (R + 0.35 * (1 - t) + 0.1), 0.09 * (1 - t) + 0.02, 0.0, -1.6, YEL, alpha=a, glow=1.0)


cam = ortho_cam()
items = [lambda x: arrow(x), lambda x: bolt(x), lambda x: spit(x), lambda x: fireball(x), lambda x: ember_stone(x)]
items += [(lambda f: (lambda x: fire_patch(x, f)))(f) for f in range(6)]
items += [(lambda f: (lambda x: blast(x, f)))(f) for f in range(8)]
items += [(lambda f: (lambda x: flare(x, f)))(f) for f in range(6)]
for i, fn in enumerate(items):
    x = i * 10.0
    fn(x)
    sprite_cam_key(cam, i + 1, x, 0.0, CELL / PPU_R, elev=0)
flush()
const_keys()
S.frame_start, S.frame_end = 1, len(items)
