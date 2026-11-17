from kit import *
from scenery import *
# fx atlas sources (Tales of the Brine): 384x384 cells at 96 px/u (packed to 72 ppu), side camera (no elevation), anchor = cell centre.
# frames: 1 arrow (musket ball), 2 bolt (flaming cannonball), 3 spit (ink glob), 4 fireball (ink bomb),
#         5 ember_stone (falling cannonball), 6-11 fire_patch (burning tar), 12-19 blast (explosion + splinters), 20-25 flare
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


INKC = (0.24, 0.12, 0.32); INK_L = (0.45, 0.24, 0.55); GRN = (0.49, 1.0, 0.6); GRN_D = (0.2, 0.62, 0.38)
LEAD = (0.3, 0.3, 0.34); TARC = (0.1, 0.08, 0.08)


def streak(x0, x1, z, w, color, alpha, y=0.5, glow=1.0):
    """Tapered flat streak from x0 (width w) to x1 (point)."""
    poly([(x0, z + w / 2), (x1, z), (x0, z - w / 2)], y, color, alpha=alpha, glow=glow)


def arrow(x):   # musket ball with a spark trail, travels RIGHT
    halo(x + 0.35, 0, 0.32, ORG, a=0.5)
    streak(x + 0.3, x - 0.85, 0.0, 0.12, ORG, 0.7)
    streak(x + 0.3, x - 0.5, 0.0, 0.06, YEL, 0.9, y=0.45, glow=1.6)
    ball(0.1, LEAD, (x + 0.35, 0, 0), seg=12)
    ball(0.035, (0.8, 0.8, 0.85), (x + 0.38, -0.08, 0.04), seg=6, outline=0.0)
    rr = random.Random(2)
    for k in range(6):
        sx = x + 0.1 - k * 0.17 + rr.uniform(-0.05, 0.05); sz = rr.uniform(-0.12, 0.12)
        ball(0.03 - k * 0.003, YEL, (sx, -0.2, sz), glow=1.8, seg=6, outline=0.0, name="spark")


def bolt(x):    # flaming cannonball, travels RIGHT (fire trails left)
    halo(x + 0.3, 0, 0.8, ORG, a=0.55)
    for k, (dz, l, s) in enumerate(((0.0, 1.15, 1.0), (0.12, 0.75, 0.7), (-0.12, 0.85, 0.72), (0.2, 0.45, 0.45), (-0.2, 0.5, 0.45))):
        cyl(0.26 * s, l, ORG if k % 2 == 0 else RED, (x + 0.3 - l / 2, 0.1 + k * 0.01, dz), rot=(0, -R90, 0), r2=0.0, seg=8, glow=1.2, name="tail")
    cyl(0.14, 0.7, YEL, (x + 0.05, -0.1, 0), rot=(0, -R90, 0), r2=0.0, seg=8, glow=1.7, name="tail_in")
    ball(0.27, (0.17, 0.15, 0.15), (x + 0.32, 0, 0), seg=16)
    ball(0.2, ORG, (x + 0.24, -0.08, 0.0), scale=(0.7, 0.5, 1.0), glow=1.4, seg=12, outline=0.0, name="hot")
    ball(0.06, (0.55, 0.5, 0.5), (x + 0.4, -0.24, 0.1), seg=8, outline=0.0)
    rr = random.Random(4)
    for k in range(5):
        ball(0.04, YEL, (x - 0.5 - k * 0.15, -0.2, rr.uniform(-0.25, 0.25)), glow=1.8, seg=6, outline=0.0, name="spark")


def spit(x):    # glob of glowing ink, travels LEFT (drips trail right)
    halo(x, 0, 0.5, GRN, a=0.4)
    ball(0.21, INKC, (x, 0, 0), scale=(1.2, 1, 0.92), seg=14)
    ball(0.13, GRN, (x - 0.06, -0.12, 0.04), scale=(1.2, 0.5, 0.85), glow=1.5, seg=10, outline=0.0)
    for k, (dx, dz, r) in enumerate(((0.3, 0.05, 0.1), (0.48, -0.03, 0.07), (0.62, 0.06, 0.05), (0.74, -0.02, 0.03))):
        ball(r, INKC if k % 2 else INK_L, (x + dx, 0, dz), seg=10)
    streak(x + 0.1, x + 0.75, 0.0, 0.16, GRN_D, 0.5)


def fireball(x):   # big ink bomb (boss), travels LEFT (ink trail right)
    halo(x, 0, 1.0, GRN, a=0.45)
    rr = random.Random(7)
    for k, (dz, l, s) in enumerate(((0.0, 1.1, 1.0), (0.2, 0.8, 0.6), (-0.2, 0.85, 0.62), (0.34, 0.5, 0.4), (-0.32, 0.55, 0.4))):
        cyl(0.3 * s, l, INKC if k % 2 == 0 else INK_L, (x + 0.15 + l / 2, 0.12, dz), rot=(0, R90, 0), r2=0.0, seg=10, name="tail")
    ball(0.42, INKC, (x, 0, 0), seg=18)
    for k, (dx, dz, s) in enumerate(((0.15, 0.2, 0.06), (0.22, -0.12, 0.05), (-0.05, -0.25, 0.045), (0.05, 0.05, 0.035))):   # glowing spots
        ball(s, GRN, (x + dx, -0.4, dz), scale=(1, 0.4, 1), glow=1.6, seg=8, outline=0.0, name="spot")
    ball(0.15, GRN, (x - 0.1, -0.33, 0.08), scale=(1, 0.4, 1), glow=1.8, seg=10, outline=0.0)
    for k in range(6):
        ball(rr.uniform(0.04, 0.08), INK_L, (x + 0.6 + k * 0.18, -0.1, rr.uniform(-0.4, 0.4)), seg=8, name="drop")


def ember_stone(x):   # Broadside: cannonball falling DOWN (fire/smoke trail up)
    halo(x, 0.15, 0.75, ORG, a=0.45)
    for k, (dx, l, s) in enumerate(((0.0, 1.0, 1.0), (0.12, 0.6, 0.65), (-0.12, 0.65, 0.65))):
        cyl(0.24 * s, l, ORG if k == 0 else RED, (x + dx, 0.1, 0.15 + l / 2), r2=0.0, seg=8, glow=1.2, name="trail")
    ball(0.2, SMOKE_L, (x + 0.05, 0.3, 1.05), seg=10, name="puff"); ball(0.15, SMOKE, (x - 0.08, 0.3, 1.3), seg=10, name="puff")
    ball(0.26, (0.17, 0.15, 0.15), (x, 0, 0), seg=16)
    ball(0.07, (0.5, 0.48, 0.5), (x - 0.1, -0.22, 0.1), seg=8, outline=0.0)


def fire_patch(x, f):   # burning tar splash (loop)
    t = f / 6.0
    ball(0.9, TARC, (x, 0, 0.0), scale=(1.0, 0.6, 0.1), seg=20, name="tar")
    for (dx, s) in ((-0.95, 0.16), (0.98, 0.12), (-0.6, 0.1), (0.7, 0.14)):
        ball(s, TARC, (x + dx, -0.1, 0.02), scale=(1.3, 0.8, 0.5), seg=10, name="splat")
    for i in range(3):     # bubbling tar blisters
        ph = (t + i / 3) % 1.0
        ball(0.09 * math.sin(math.pi * ph) + 0.01, (0.22, 0.18, 0.16), (x - 0.4 + i * 0.4, -0.3, 0.05), scale=(1, 0.8, 0.8), seg=10, name="blister")
    for i, (dx, base, ph) in enumerate(((-0.55, 0.5, 0.0), (-0.22, 0.8, 2.1), (0.12, 0.95, 4.0), (0.45, 0.65, 1.1), (0.72, 0.4, 3.2))):
        h = base * (0.78 + 0.22 * math.sin(math.tau * t + ph))
        lean = 0.12 * math.sin(math.tau * t + ph * 1.7)
        cyl(0.2, h, ORG if i % 2 else RED, (x + dx + lean * 0.5, 0.05 - i * 0.01, h / 2), r2=0.0, seg=7, glow=1.2, name="fp",
            rot=(0, lean, 0))
        cyl(0.11, h * 0.6, YEL, (x + dx + lean * 0.3, -0.12, h * 0.3), r2=0.0, seg=7, glow=1.6, name="fp_in", rot=(0, lean, 0))
    for k in range(2):     # greasy black smoke wisps
        ph = (t + k * 0.5) % 1.0
        ball(0.12 + 0.12 * ph, SMOKE, (x - 0.2 + k * 0.45 + 0.2 * ph, 0.2, 0.9 + ph * 0.9), seg=10, name="smk")
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
            box((0.34, 0.07, 0.07), HULL_L if k % 2 else HULL, (x + math.cos(a) * d, -0.3, math.sin(a) * d), rot=(0, -a + 0.6 * f, 0), name="splinter")
            if f <= 3:
                ball(0.05, YEL, (x + math.cos(a + 0.4) * d * 1.1, -0.3, math.sin(a + 0.4) * d * 1.1), glow=1.8, name="spark")


def flare(x, f):   # flare-pistol burst: hot white core, red-orange ring with a gold rim, star sparks
    t = f / 5.0
    R = 0.35 + 1.45 * t; w = 0.3 * (1 - t) + 0.07; a = 1.0 - 0.55 * t
    annulus(x, 0, R - w * 0.35, R, (1.0, 0.86, 0.45), a, glow=1.0)
    annulus(x, 0, R - w, R - w * 0.35, (1.0, 0.36, 0.16), a * 0.9, glow=1.0)
    ellipse(x, 0, R * 1.1, R * 1.1, -1.0, (1.0, 0.5, 0.2), n=48, alpha=0.35 * (1 - t), radial=3.0)
    if f < 3:
        ellipse(x, 0, 0.4 * (1 - t) + 0.05, 0.4 * (1 - t) + 0.05, -1.7, (1.0, 0.97, 0.9), n=24, glow=1.5)
    for k in range(8):
        ang = k / 8 * math.tau + 0.2; l = (0.45 if k % 2 else 0.3) * (1 - t) + 0.12
        seg(x + math.cos(ang) * R * 0.95, math.sin(ang) * R * 0.95, x + math.cos(ang) * (R + l),
            math.sin(ang) * (R + l), 0.1 * (1 - t) + 0.03, 0.0, -1.6, (1.0, 0.9, 0.55), alpha=a, glow=1.0)


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
