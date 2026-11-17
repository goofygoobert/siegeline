from kit import *
# Spitter — bloated glowing throat sac, lobs ember spit (lean back, lurch forward: spit leaves on frame 4).
def sac(rig, C):
    sc = rig["sc"]; z = rig["shoulder_z"]; bw = rig["bw"]
    c = (bw * 0.38, -0.02 * sc, z - 0.02 * sc)
    gp = glow_pivot(rig, "sac", c, rig["torso"])
    attach(ball(0.24 * sc, C["eyes"], c, scale=(1, 1.05, 0.95), glow=1.0, name="sac"), gp)
    attach(ball(0.12 * sc, (1.0, 0.85, 0.45), (c[0] + 0.1 * sc, c[1] - 0.12 * sc, c[2] + 0.05 * sc), glow=2.0, name="saccore", outline=0.0), gp)
    for a in (-40, 10, 50):
        attach(box((0.03 * sc, 0.03 * sc, 0.26 * sc), (0.3, 0.1, 0.06), (c[0] + 0.18 * sc, c[1] - 0.1 * sc, c[2]), rot=(math.radians(a), 0, 0), name="vein", outline=0.0), gp)
    attach(box((0.03 * sc, 0.06 * sc, 0.14 * sc), PAL["ember"], (c[0] + 0.22 * sc, -0.05 * sc, c[2] - 0.3 * sc), glow=1.5, name="drool", outline=0.0), rig["torso"])

register(dict(HOLLOW, id="spitter", scale=1.0, bulk=0.88, head=0.85, torso=1.05, leg=1.0, arm=1.1, limb=0.6, head_fwd=0.1,
              extras=[sac, lambda r, C: hollow_horns(r, C, 0.8, "R"), hollow_maw, lambda r, C: hollow_spikes(r, C, 2),
                      lambda r, C: hollow_cracks(r, C, 2)],
              style=dict(attack="spit", lean=18, headc=0.75, die="fwd", aR0=0, aL0=8, stride=24),
              colors=hollow_colors(body=(0.31, 0.29, 0.29))))
