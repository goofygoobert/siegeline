from kit import *
# Husk Warden (mini-boss, 1.5x) — husk in rusted armour scraps with a big cleaver.
def scraps(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]; bw = rig["bw"]; th = rig["torso_h"]; sz = rig["shoulder_z"]
    R = C["rust"]
    attach(box((0.1 * sc, bw * 0.6, th * 0.5), R, (bw * 0.42, -bw * 0.1, z + th * 0.55), rot=(math.radians(12), 0, math.radians(-5)), name="breast"), rig["torso"])
    attach(box((0.34 * sc, 0.32 * sc, 0.16 * sc), R, (0, -bw * 0.55, sz + 0.02 * sc), rot=(math.radians(-15), 0, 0), name="spaul"), rig["arm_R"])
    attach(spike((0, -bw * 0.62, sz + 0.08 * sc), (0.1, -0.5, 1), 0.28 * sc, 0.07 * sc, C["metal_dk"]), rig["arm_R"])
    # half helm, cracked open on the far side
    hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    attach(ball(r * 1.08, R, (hx - 0.02 * sc, -r * 0.15, hz + r * 0.25), scale=(1, 0.75, 0.75), name="halfhelm"), rig["head"])
    attach(box((0.05 * sc, 0.04 * sc, r * 0.9), C["metal_dk"], (hx + r * 0.95, -r * 0.35, hz - 0.02 * sc), name="nasal"), rig["head"])
    attach(box((bw * 0.9, bw * 0.8, 0.12 * sc), R, (0, 0, z + 0.06 * sc), name="rustbelt"), rig["torso"])
    for y in (-0.15, 0.12):
        attach(box((0.08 * sc, 0.22 * sc, z * 0.55), R, (bw * 0.42, y * sc, z * 0.75), rot=(0, math.radians(-6), 0), name="tasset"), rig["torso"])
    cracks(rig, rig["torso"], [(bw * 0.3, -bw * 0.38, z + th * 0.3, 25, 0.2)], C)

register(dict(HOLLOW, id="husk_warden", scale=1.5, bulk=0.95, head=0.88, torso=1.1, leg=1.0, arm=1.2, limb=0.75, head_fwd=0.12,
              weapon="cleaver", grip=30,
              extras=[scraps, lambda r, C: hollow_horns(r, C, 1.0, "R"), hollow_maw, lambda r, C: hollow_spikes(r, C, 3),
                      hollow_elbows],
              style=dict(attack="heavy", lean=18, headc=0.7, die="fwd", aR0=-15, aL0=5, heavy=1.3, stride=24),
              colors=hollow_colors(body=(0.3, 0.285, 0.285))))
