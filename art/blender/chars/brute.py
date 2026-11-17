from kit import *
# Bonecage Brute (1.6x) — exposed ribcage with an ember heart, huge uneven arms, bone club.
def ribcage(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]; bw = rig["bw"]; th = rig["torso_h"]
    x = bw * 0.42
    attach(box((0.06 * sc, bw * 0.5, th * 0.55), PAL["blood"], (x, 0, z + th * 0.55), name="cavity", outline=0.0), rig["torso"])
    gp = glow_pivot(rig, "heart", (x - 0.02 * sc, -0.02 * sc, z + th * 0.55), rig["torso"])
    attach(ball(0.12 * sc, PAL["ember"], (x - 0.0 * sc, -0.02 * sc, z + th * 0.55), glow=1.8, name="heart", outline=0.0), gp)
    for i in range(4):
        attach(box((0.06 * sc, bw * 0.62, 0.055 * sc), C["bone"], (x + 0.04 * sc, 0, z + th * (0.33 + i * 0.15)),
                   rot=(0, math.radians(-8), 0), name="rib"), rig["torso"])
    attach(box((0.07 * sc, 0.07 * sc, th * 0.65), C["bone"], (x + 0.05 * sc, 0, z + th * 0.55), name="sternum"), rig["torso"])
    # hump + spikes on the bigger shoulder
    attach(ball(0.3 * sc, C["body"], (-bw * 0.15, -bw * 0.3, rig["shoulder_z"]), scale=(1, 1, 0.8), name="hump"), rig["torso"])

register(dict(HOLLOW, id="brute", scale=1.6, bulk=1.3, head=0.72, torso=1.05, leg=0.85, limb=1.0, arm=1.3, hand=1.7,
              arm_scale=dict(R=1.55, L=1.2), head_fwd=0.2, weapon="boneclub", grip=25,
              extras=[ribcage, lambda r, C: hollow_horns(r, C, 1.2, "R"), hollow_maw, lambda r, C: hollow_spikes(r, C, 4, 1.1),
                      lambda r, C: hollow_cracks(r, C, 3)],
              style=dict(attack="heavy", lean=24, headc=0.7, die="fwd", aR0=-10, aL0=5, heavy=1.4, stride=24),
              colors=hollow_colors()))
