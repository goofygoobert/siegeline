from kit import *
# Barnacle Troll (1.6x) — hulking sea troll crusted in barnacles and coral, tusks, kelp beard, driftwood club.
def crust(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]; bw = rig["bw"]; th = rig["torso_h"]; sz = rig["shoulder_z"]
    attach(ball(0.32 * sc, C["body"], (-bw * 0.15, -bw * 0.2, sz), scale=(1, 1, 0.8), name="hump"), rig["torso"])
    barnacles(rig, C, rig["torso"], [(-bw * 0.2 + i * 0.07 * sc, -bw * 0.45 - 0.02 * sc, sz - 0.05 * sc - (i % 3) * 0.12 * sc) for i in range(6)], 1.2)
    barnacles(rig, C, rig["torso"], [(bw * 0.38, -bw * 0.3 + i * 0.12 * sc, z + th * 0.3 + (i % 2) * 0.1 * sc) for i in range(4)], 1.0)
    for (a, L) in ((-0.3, 0.3), (0.2, 0.36), (0.7, 0.24)):    # coral branches on the shoulder hump
        b = Vector((-bw * 0.2, -bw * 0.25, sz + 0.12 * sc)); e = b + Vector((math.sin(a) * 0.4, -0.2, 1)).normalized() * L * sc
        attach(rod(b, e, 0.045 * sc, PAL["coral"], r2=0.02 * sc, seg=6), rig["torso"])
        attach(spike(tuple(e), (math.sin(a + 0.6), 0, 1), 0.12 * sc, 0.025 * sc, PAL["coral"]), rig["torso"])
        attach(ball(0.035 * sc, PAL["coral"], tuple(e), name="coralnub", outline=0.008), rig["torso"])

def troll_face(rig, C):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    for y in (-0.35, 0.35):
        attach(spike((hx + r * 0.85, y * r, hz - r * 0.5), (0.3, 0, 1), 0.16 * sc, 0.04 * sc, C["bone"]), hp)
    attach(ball(r * 0.3, C["skin"], (hx + r * 1.0, 0, hz - r * 0.05), scale=(1, 0.9, 0.8), name="nose"), hp)
    for i in range(5):    # kelp beard
        y = (-0.5 + i * 0.25) * r
        b = Vector((hx + r * 0.7, y, hz - r * 0.7)); e = b + Vector((-0.05, 0, -1)).normalized() * (0.25 + 0.08 * (i % 2)) * sc
        attach(rod(b, e, 0.04 * sc, C["kelp"], r2=0.01 * sc, seg=6), hp)
    barnacles(rig, C, hp, [(hx - r * 0.2, -r * 0.7, hz + r * 0.55), (hx + r * 0.1, -r * 0.6, hz + r * 0.7)], 0.9)

register(dict(DEEP, id="brute", scale=1.6, bulk=1.3, head=0.72, torso=1.05, leg=0.85, limb=1.0, arm=1.1, hand=1.7,
              arm_scale=dict(R=1.55, L=1.2), head_fwd=0.2, weapon="driftclub", grip=60,
              extras=[crust, troll_face, hollow_maw, lambda r, C: hollow_spikes(r, C, 4, 1.1), lambda r, C: hollow_cracks(r, C, 2),
                      lambda r, C: shoulder_barnacles(r, C, 1.0, 4), lambda r, C: shoulder_barnacles(r, C, 0.9, 3, "L")],
              style=dict(die_rz=0.62, attack="heavy", lean=24, headc=0.7, die="fwd", aR0=-10, aL0=5, heavy=1.4, stride=24),
              colors=deep_colors(body=(0.3, 0.42, 0.4), skin=(0.38, 0.5, 0.46), arms=(0.34, 0.47, 0.43), hands=(0.34, 0.47, 0.43),
                                 legs=(0.24, 0.34, 0.33))))
