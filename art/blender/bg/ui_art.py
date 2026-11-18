from kit import *
from scenery import *
# Interface art rendered with the figures' cel paint: frame 1 doubloon, 2 Long Tom (cannon button), 3 powder keg.
# Bundle with --lib art/blender/scenery.py --lib art/blender/kit2.py.  Output: 384x384 PNG per frame, transparent.
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 32
S.render.resolution_x = S.render.resolution_y = 384
fig = Fig("ui", INK_CREW, h=2.0, line=0.05)
GOLD = (1.0, 0.76, 0.26); GOLD_D = (0.86, 0.56, 0.16); IRON = (0.26, 0.28, 0.33); WOOD = (0.56, 0.36, 0.2); WOOD_D = (0.38, 0.23, 0.13)


def held(name, x):
    """A pivot at x that the object's parts hang from, so the whole object can be turned toward the camera."""
    return fig.joint(name, (x, 0, 0), "root", 1)


# ---- 1: doubloon, face toward the camera, turned a little so its thickness shows
held("coin", 0.0)
fig.add(loft([(-0.11, 1.0, 1.0), (0.11, 1.0, 1.0)], seg=48, axis="y", round_=(False, False), name="coin"), "coin", GOLD, metal=True)
for i in range(30):            # beaded rim
    a = 2 * math.pi * i / 30
    fig.add(orb(0.055, (0.86 * math.cos(a), -0.12, 0.86 * math.sin(a)), seg=6), "coin", GOLD, metal=True, line=0.0)
# anchor emblem, raised
fig.add(block((0.13, 0.08, 0.95), (0, -0.14, -0.02), bevel=0.03, name="shank"), "coin", GOLD_D, metal=True, line=0.02)
fig.add(block((0.58, 0.08, 0.11), (0, -0.14, 0.33), bevel=0.03, name="stock"), "coin", GOLD_D, metal=True, line=0.02)
fig.add(orb(0.11, (0, -0.14, 0.52), (1, 0.6, 1), seg=10, name="ring"), "coin", GOLD_D, metal=True, line=0.02)
for sgn in (-1, 1):
    for k in range(5):        # curved arm as a chain of beads
        a = math.radians(-90 + sgn * (18 + k * 16))
        fig.add(orb(0.085, (0.42 * math.cos(a), -0.14, -0.06 + 0.42 * math.sin(a)), (1, 0.6, 1), seg=8), "coin", GOLD_D, metal=True, line=0.015)
    fig.add(cone((sgn * 0.38, -0.14, -0.22), (sgn * 0.5, -0.14, -0.02), 0.11, 0.0, seg=6, name="fluke"), "coin", GOLD_D, metal=True, line=0.015)

# ---- 2: Long Tom on its carriage, aimed up and right
held("gun", 0.0)
BX, BZ, AIM = 0.0, 0.25, 22
barrel = loft([(-1.05, 0.30, 0.30), (-0.85, 0.36, 0.36), (-0.55, 0.34, 0.34), (0.55, 0.26, 0.26), (0.95, 0.24, 0.24), (1.05, 0.29, 0.29)],
              seg=24, axis="x", round_=(True, False), name="barrel")
fig.add(turn(barrel, -AIM, "Y", (0, 0, 0)), "gun", IRON, metal=True)
for (u, r) in ((-0.72, 0.39), (-0.3, 0.36), (0.62, 0.29), (1.0, 0.31)):
    band = loft([(u - 0.05, r, r), (u + 0.05, r, r)], seg=24, axis="x", round_=(False, False), name="band")
    fig.add(turn(band, -AIM, "Y", (0, 0, 0)), "gun", GOLD, metal=True, line=0.02)
fig.add(turn(orb(0.16, (-1.22, 0, 0), seg=12, name="knob"), -AIM, "Y", (0, 0, 0)), "gun", IRON, metal=True)
fig.add(turn(orb(0.2, (1.08, 0, 0), (0.3, 1, 1), seg=16, name="mouth"), -AIM, "Y", (0, 0, 0)), "gun", (0.06, 0.05, 0.06), glow=0.9, line=0)
for ob in list(bpy.data.objects):
    if ob.parent == fig.J["gun"]:
        ob.location.z += BZ
fig.add(slab([(-0.95, -0.55), (0.75, -0.55), (0.55, 0.05), (-0.75, 0.25)], 0.5, at=(0, 0, 0), bevel=0.04, name="carriage"), "gun", WOOD)
for x in (-0.6, 0.45):
    fig.add(loft([(-0.36, 0.33, 0.33), (-0.24, 0.33, 0.33)], seg=24, axis="y", round_=(False, False), at=(x, 0, -0.55), name="wheel"), "gun", WOOD_D)
    fig.add(loft([(-0.38, 0.35, 0.35), (-0.34, 0.35, 0.35)], seg=24, axis="y", round_=(False, False), at=(x, 0, -0.55), name="tyre"), "gun", IRON, metal=True, line=0.015)
    fig.add(orb(0.08, (x, -0.4, -0.55), seg=8, name="hub"), "gun", GOLD, metal=True, line=0.012)

# ---- 3: powder keg
held("keg", 0.0)
fig.add(loft([(-0.85, 0.52, 0.52), (-0.4, 0.66, 0.66), (0.0, 0.70, 0.70), (0.4, 0.66, 0.66), (0.85, 0.52, 0.52)], seg=28, round_=(False, False), name="keg"), "keg", WOOD)
for z in (-0.62, -0.42, 0.42, 0.62):
    r = 0.54 + 0.13 * (1 - abs(z) / 0.85)
    fig.add(loft([(z - 0.05, r + 0.02, r + 0.02), (z + 0.05, r + 0.02, r + 0.02)], seg=28, round_=(False, False), name="hoop"), "keg", IRON, metal=True, line=0.015)
for i in range(7):            # stave lines on the near side
    a = math.radians(-150 + i * 20)
    fig.add(block((0.02, 0.02, 1.22), (0.665 * math.cos(a), 0.665 * math.sin(a) - 0.02, 0), bevel=0.0, name="stave"), "keg", WOOD_D, line=0.0)
fig.add(loft([(0.85, 0.5, 0.5), (0.9, 0.5, 0.5)], seg=28, round_=(False, False), name="lid"), "keg", WOOD_D)
fig.add(orb(0.1, (0.0, -0.7, 0.15), (1, 0.4, 1), seg=10, name="bung"), "keg", WOOD_D, line=0.015)
fig.add(cone((0.0, -0.74, 0.15), (0.12, -0.9, 0.42), 0.025, 0.02, seg=5, name="fuse"), "keg", (0.85, 0.8, 0.6), line=0.01)
fig.add(orb(0.07, (0.12, -0.9, 0.44), seg=8, name="spark"), "keg", (1.0, 0.8, 0.3), glow=1.4)

fig.J["gun"].location.x = 10.0; fig.J["keg"].location.x = 20.0     # spread the three objects apart (built at the origin)
# turn each object so it reads as a little 3D thing, not a flat disc
fig.J["coin"].rotation_euler = (math.radians(8), 0, math.radians(-22))
fig.J["gun"].rotation_euler = (0, 0, math.radians(-14))
fig.J["keg"].rotation_euler = (math.radians(14), math.radians(-10), math.radians(-18))

cam = ortho_cam()
for fr, (x, z, o) in enumerate(((0.0, 0.0, 2.35), (10.0, 0.1, 2.75), (20.0, 0.0, 2.15)), start=1):
    key_cam(cam, fr, (x, -40, z), (math.radians(90), 0, 0), o)
const_keys()
S.frame_start, S.frame_end = 1, 3
