from kit import *
from scenery import *
from r1_lib import *
# Title key art 1920x1080 (Tales of the Brine): the Gullwake fort on the left with the crew and Captain Halloran,
# the Deep coming up the beach at right (Drowners, Scuttlers, a Barnacle Troll, tentacles rising from the sea),
# sunset over the sea with the green moon rising. Calm sky centre-left for the logo; outer 8% kept free.
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 48
S.render.resolution_x, S.render.resolution_y = 1920, 1080
S.render.film_transparent = False
W = 1920 / 90.0                      # 21.33 u wide at 90 px/u
ELEV_T = 5.0
GROUND_ROW = 0.83                    # ground line at 83% of the height
CZ = 12.0 * (GROUND_ROW - 0.5)       # camera centre z (3.6)
t = math.tan(math.radians(ELEV_T))
sprite_lights()


def unshear(before):
    """Cancel the camera tilt for flat painted layers (keeps their painted heights)."""
    for ob in set(bpy.data.objects) - before:
        if ob.type == "MESH":
            for v in ob.data.vertices:
                v.co.z -= (ob.location.y + v.co.y) * t


# painted backdrop
before = set(bpy.data.objects)
rect(-1, CZ + 5.0, W + 1, CZ + 7.0, 81, DAY["sky"][-1][1])
build_sky(DAY, False, calm=(3.0, 13.0, 4.6), W=W + 1)
# the green moon rising over the sunset (top right, inside the safe area)
mx, mz, mr = 16.4, 8.3, 1.15
ellipse(mx, mz, mr * 3.4, mr * 3.4, 77.5, (0.35, 0.95, 0.5), n=64, alpha=0.4, radial=2.2)
ellipse(mx, mz, mr, mr, 77.0, (0.78, 1.0, 0.7), n=64, glow=0.4)
for (dx, dz, rx, rz) in ((-0.35, 0.25, 0.38, 0.28), (0.3, -0.3, 0.42, 0.25), (0.42, 0.42, 0.18, 0.16), (-0.45, -0.45, 0.2, 0.15)):
    ellipse(mx + dx, mz + dz, rx, rz, 76.8, (0.6, 0.86, 0.55), n=16, wob=0.25, seed=int(dx * 10 + 50))
build_far(DAY, False, W=W + 1)
flush()
unshear(before)

# tentacles rising from the sea behind the beach (right)
def tentacle(x, y, h, curl, s=1.0, seed=0):
    r = random.Random(seed); pts = []
    for i in range(15):
        u = i / 14
        a = curl * u ** 1.6
        pts.append((x + math.sin(a) * h * 0.35 * u + 0.25 * math.sin(u * 5 + seed) * s, y, -0.6 + h * (u - 0.25 * u ** 3) * s))
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        rr = 0.42 * s * (1 - i / 15) + 0.04
        rod(p, q, rr, (0.33, 0.2, 0.42), r2=rr * 0.93, seg=10, name="tentacle")
        if i % 2 == 0 and i < 12:
            ball(rr * 0.42, (0.85, 0.72, 0.8), (p[0] - rr * 0.75, y - rr * 0.6, p[2]), scale=(0.6, 0.6, 1), seg=8, name="sucker", outline=0.012)
    ball(1.4 * s, (0.08, 0.16, 0.2), (x, y + 0.3, -0.5), scale=(1.4, 0.4, 0.25), seg=12, name="swirl", outline=0.0)


tentacle(14.2, 12.5, 3.6, -2.2, 0.85, seed=1)
tentacle(17.6, 14.0, 4.4, 2.6, 1.0, seed=2)
tentacle(19.2, 13.0, 2.6, -1.8, 0.7, seed=3)

# beach (sand) in front
before = set(bpy.data.objects)
w = wave(71, base=0.5)
top = profile(-1, W + 1, lambda x: 0.35 + 0.08 * w(x), 0.2)
s0, s1, s2, s3 = DAY["sand"]
band(top, -4, 10, s1, stops=[(0.0, s0), (0.35, s1), (0.75, s2), (1.0, s3)], noise=0.1, nscale=0.8)
lip = top + [(x, z - 0.12) for x, z in reversed(top)]
poly(lip, 9.8, DAY["lip"])
band([(x, 0.62 + 0.05 * math.sin(x * 1.3)) for x in [i * 0.25 - 1 for i in range(95)]], 0.3, 10.2, DAY["foam"], alpha=0.55)
r = random.Random(3)
for i in range(40):
    x = r.uniform(0, W); z = r.uniform(-2.6, 0.1); s = r.uniform(0.05, 0.14)
    ellipse(x, z, s * 1.4, s, 9.7, (0.3, 0.2, 0.18), n=8, wob=0.3, seed=i)
for i in range(30):
    x = r.uniform(0, W); z = r.uniform(-2.2, -0.2)
    ellipse(x, z, r.uniform(0.5, 1.5), r.uniform(0.04, 0.09), 9.6, DAY["wet"], n=14, wob=0.3, seed=i, alpha=0.4)
sea_ribs(10.4, 0.25, 0.75, 9.9, DAY["ribs"], lit=DAY["ribs_lit"], n=5, seed=3, skull=False)
flush()
unshear(before)

# the Gullwake (scaled to leave the logo area clear), Long Tom aimed up the beach
KX, FS = 3.3, 0.8
def fort():
    gullwake(KX, 0)
    PX = KX + 2.3
    group(lambda: long_tom(PX, 4.4), (PX, 0, 4.4), rot=(0, math.radians(-10), 0))
g = group(fort, (KX, 0, 0), rot=(0, 0, math.radians(-15)), move=(0, 1.4, 0))
g.scale = (FS, FS, FS)
ellipse(KX - 1.4 * FS, 0.9 + 5.2 * FS, 1.6, 1.6, 3.2, (1.0, 0.7, 0.35), n=48, alpha=0.4, radial=2.0)  # lantern glow
flush()


def figure(sid, x, y, z=0.0, anim="idle", tt=0.0, yaw=25, size=1.0):
    """Build a registered cast member (art/blender/chars) holding one pose, placed like the sprite renders."""
    spec = REG[sid]; st = spec.get("style", {})
    if "v2" in spec:        # carved figures (kit2)
        fig = spec["v2"](spec); facing = spec.get("facing", 1)
        holder = empty("H_" + sid, (x, y, z)); holder.scale = (facing * size, size, size)
        holder.rotation_euler = (0, 0, math.radians(-yaw * facing))
        _parent_keep_local(fig.root, holder)
        a = anim if anim in spec["anims"] else "idle"
        pose(fig, 1, spec["anims"][a](tt, int(tt * 10), 10))
        return fig
    rig = build_char(spec)
    facing = spec.get("facing", 1)
    holder = empty("H_" + sid, (x, y, z))
    holder.scale = (facing * size, size, size)
    holder.rotation_euler = (0, 0, math.radians(-yaw * facing))
    _parent_keep_local(rig["root"], holder)
    for ob in rig["free"]:
        _parent_keep_local(ob, holder)
    rig["hips_base"] = tuple(rig["hips"].location)
    fn = st.get("anims", {}).get(anim) or BASE_ANIMS[anim]
    d = fn(tt, st); d["_anim"] = anim; d["_i"] = 0; d["_n"] = 1
    apply(rig, 1, d, st)
    return rig


# the crew around the fort
for sid, x, y, anim, tt in (("bellringer", 2.3, 0.2, "idle", 0.3), ("torchbow", 5.4, -0.6, "attack", 0.45),
                            ("maulwright", 3.9, -1.6, "idle", 0.2), ("ashguard", 7.0, -1.2, "idle", 0.0),
                            ("lamplighter", 2.6, -2.4, "idle", 0.6), ("cinder_runner", 9.7, -1.0, "walk", 0.3)):
    if sid in REG:
        figure(sid, x, y, anim=anim, tt=tt, size=1.15)
# Captain Halloran in front, flare pistol raised
if "marshal" in REG:
    figure("marshal", 8.4, -2.9, anim="special", tt=0.4, size=1.4)
# the Deep coming up the beach
for sid, x, y, tt, sz in (("husk", 12.3, -1.2, 0.1, 1.0), ("gnawer", 13.3, -2.6, 0.5, 1.0), ("husk", 14.4, 0.0, 0.7, 0.95),
                          ("brute", 16.0, -1.4, 0.3, 1.0), ("gnawer", 17.3, -3.0, 0.2, 1.0), ("spitter", 17.9, -0.1, 0.6, 0.95),
                          ("husk", 18.8, -1.9, 0.4, 1.0), ("husk", 13.1, 2.4, 0.2, 0.8), ("husk_warden", 15.4, 2.8, 0.5, 0.85)):
    if sid in REG:
        figure(sid, x, y, anim="walk", tt=tt, size=sz * 1.15)
# dark foreground framing (bottom corners): rocks, a barrel, rope, kelp
before = set(bpy.data.objects)
FG = (0.1, 0.07, 0.08); FG_L = (0.22, 0.14, 0.13)
for (x, z, s, sd) in ((0.4, -2.2, 0.9, 1), (1.5, -2.25, 0.55, 2), (20.7, -2.1, 1.0, 3), (19.4, -2.25, 0.55, 4), (21.4, -1.3, 0.6, 5)):
    rock(x, z, s, -9, FG, seed=sd, lit=FG_L)
barrel(2.4, -2.3, 0.45, -8.9, FG, FG_L, (0.06, 0.04, 0.05))
rope_coil(18.2, -2.2, 0.5, -8.9, FG, FG_L)
for k in range(5):
    seg(20.0 + k * 0.25, -1.6, 19.8 + k * 0.3, -0.9 + 0.15 * (k % 2), 0.08, 0.02, -8.8, (0.13, 0.15, 0.09))
flush()
unshear(before)
# ghost lights drifting over the shallows
rr = random.Random(5)
for i in range(8):
    wisp(rr.uniform(11.5, 19.5), rr.uniform(1.2, 4.0), rr.uniform(0.12, 0.25), -6, (0.45, 1.0, 0.6), alpha=0.6)
flush()

cam = ortho_cam()
e = math.radians(ELEV_T)
cam.data.ortho_scale = W
cam.location = (W / 2, -60 * math.cos(e), CZ + 60 * math.sin(e))
cam.rotation_euler = (math.radians(90) - e, 0, 0)
S.frame_start = S.frame_end = 1
