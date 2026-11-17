from kit import *
from scenery import *
from r1_lib import *
# Title key art 1920x1080: Lantern Keep left, Wardens + Marshal in front, Hollows cresting the ash ridge right.
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 48
S.render.resolution_x, S.render.resolution_y = 1920, 1080
S.render.film_transparent = False
W = 1920 / 90.0                      # 21.33 u wide at 90 px/u
ELEV_T = 5.0
GROUND_ROW = 0.8                     # ground line at 80% of the height
CZ = 6.0 - GROUND_ROW * 12.0 + 6.0 - 6.0  # camera centre z: ground (z=0) sits 0.8 down the frame
CZ = 12.0 * (GROUND_ROW - 0.5)       # 3.6
sprite_lights()

# painted backdrop (shifted so the camera tilt doesn't lift distant layers)
before = set(bpy.data.objects)
rect(-1, CZ + 5.0, W + 1, CZ + 7.0, 81, DAY["sky"][-1][1])
build_sky(DAY, False, calm=(5.0, 14.0, 5.2), W=W + 1)
build_far(DAY, False, W=W + 1)
build_mid(DAY, False, W=W + 1)
flush()
t = math.tan(math.radians(ELEV_T))
for ob in set(bpy.data.objects) - before:
    if ob.type == "MESH":
        for v in ob.data.vertices:
            v.co.z -= (ob.location.y + v.co.y) * t

# ash ridge on the right that the Hollows pour over
Yr = 4.0
ridge_pts = profile(9.0, W + 1, lambda x: max(0.0, min(2.6, (x - 10.0) * 0.55)) + 0.15 * math.sin(x * 2.1), 0.2)
before = set(bpy.data.objects)
band([(x, z + 0.08) for x, z in ridge_pts], 0.2, Yr + 0.2, DAY["rim"])
band(ridge_pts, 0.2, Yr, (0.12, 0.1, 0.1), top=(0.2, 0.16, 0.15), noise=0.12)
for i in range(14):
    x = 10 + i * 0.85; tuft(x, max(0.0, min(2.6, (x - 10.0) * 0.55)) - 0.05, 0.3, Yr - 0.1, DAY["grass_d"], seed=i)
dead_tree(16.2, 2.4, 2.6, Yr + 0.3, DAY["sil"], seed=8, lean=0.25)
pike(13.0, 1.4, 1.6, Yr + 0.3, DAY["sil"], bone=DAY["lit"], lean=-0.2)
flush()
for ob in set(bpy.data.objects) - before:
    for v in ob.data.vertices:
        v.co.z -= (ob.location.y + v.co.y) * t

# near ground
before = set(bpy.data.objects)
w = wave(71, base=0.5)
top = profile(-1, W + 1, lambda x: 0.3 + 0.07 * w(x), 0.2)
band(top, -4, 10, DAY["ground"][0], top=DAY["ground"][1], noise=0.14, nscale=0.8)
lip = top + [(x, z - 0.12) for x, z in reversed(top)]
poly(lip, 9.8, DAY["lip"])
r = random.Random(3)
for i in range(60):
    x = r.uniform(0, W); z = r.uniform(-2.6, 0.1); s = r.uniform(0.05, 0.14)
    ellipse(x, z, s * 1.4, s, 9.7, DAY["pebble"], n=8, wob=0.3, seed=i)
for i in range(5):
    crack(r.uniform(1, W - 3), r.uniform(-2.2, -0.4), r.uniform(1.0, 2.0), 9.6, DAY["crackc"], seed=i, glow=0.6, w=0.04)
for i in range(30):
    x = r.uniform(0, W); tuft(x, 0.28, r.uniform(0.2, 0.35), 9.5, DAY["grass"] if i % 2 else DAY["grass_d"], seed=i)
flush()
for ob in set(bpy.data.objects) - before:
    for v in ob.data.vertices:
        v.co.z -= (ob.location.y + v.co.y) * t

# the keep
KX = 4.4
keep(KX, 0)
for ob in bpy.data.objects:
    pass


def figure(sid, x, y, z=0.0, anim="idle", t=0.0, yaw=25, size=1.0):
    """Build a registered cast member (art/blender/chars) holding one pose, placed like the sprite renders."""
    spec = REG[sid]; st = spec.get("style", {})
    rig = build_char(spec)
    facing = spec.get("facing", 1)
    holder = empty("H_" + sid, (x, y, z))
    holder.scale = (facing * size, size, size)
    holder.rotation_euler = (0, 0, math.radians(-yaw * facing))
    _parent_keep_local(rig["root"], holder)
    for ob in rig["free"]:
        _parent_keep_local(ob, holder)
    rig["hips_base"] = tuple(rig["hips"].location)
    fn = {"idle": a_idle, "walk": a_walk, "attack": a_attack}.get(anim) or st["anims"][anim]
    apply(rig, 1, fn(t, st), st)
    return rig


# Wardens around the keep's gate (real unit designs from art/blender/chars)
for sid, x, y, tt in (("torchbow", 2.9, -1.4, 0.1), ("ashguard", 6.9, -1.6, 0.0), ("maulwright_t2", 8.4, -1.2, 0.3),
                     ("ashguard_t2", 5.6, -2.4, 0.5), ("lamplighter", 9.5, -0.9, 0.2), ("bellringer", 4.3, -0.6, 0.6)):
    if sid in REG:
        figure(sid, x, y, t=tt)
# the Marshal in front, lantern raised
figure("marshal", 11.3, -3.2, anim="special", t=0.3, size=1.25)
# Hollows: a crowd on the ridge crest + a few close ones
r = random.Random(9)
crowd = ["husk", "husk", "gnawer", "husk", "spitter", "husk", "brute", "husk", "husk"]
for i, sid in enumerate(crowd):
    x = 12.8 + i * 0.95 + r.uniform(-0.2, 0.2)
    z = max(0.0, min(2.6, (x - 10.0) * 0.55)) + 0.05 - (Yr - 0.6) * t
    if sid in REG:
        figure(sid, x, Yr - 0.6, z, anim="walk", t=r.random(), size=0.85)
for sid, x, y, tt in (("husk", 16.0, -0.9, 0.3), ("husk_warden", 18.2, -2.0, 0.6)):
    if sid in REG:
        figure(sid, x, y, anim="walk", t=tt)
# floating embers in front
embers(0, W, -2.5, 9.0, -8, 40, (1.0, 0.62, 0.22), seed=33, size=0.05, alpha=0.9, glow=0.8)
flush()

cam = ortho_cam()
e = math.radians(ELEV_T)
cam.data.ortho_scale = W
cam.location = (W / 2, -60 * math.cos(e), CZ + 60 * math.sin(e))
cam.rotation_euler = (math.radians(90) - e, 0, 0)
S.frame_start = S.frame_end = 1
