from kit import *
# Inkspitter — squid-headed: tall mantle with fins, face tentacles, bulging ink sac in the throat (lobs ink on frame 4).
def mantle_head(rig, C):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    b = Vector((hx - r * 0.1, 0, hz + r * 0.3)); e = b + Vector((-0.42, 0, 0.62)) * sc
    attach(rod(b, e, r * 0.95, C["skin"], r2=r * 0.15, seg=14), hp)
    attach(ball(r * 1.05, C["skin"], tuple(b + (e - b) * 0.3), scale=(1, 0.95, 1.15), name="bulge"), hp)
    for i in range(3):   # spots
        attach(ball(0.04 * sc, C["eyes"], tuple(b + (e - b) * (0.3 + i * 0.2) + Vector((0, -r * (0.75 - i * 0.18), 0))), glow=1.5, name="spot", outline=0.0), hp)
    for y in (-1, 1):
        attach(prism([(0, 0), (-0.22 * sc, 0.06 * sc), (-0.05 * sc, 0.26 * sc)], 0.03 * sc, C["fin"],
                     loc=(e.x + 0.08 * sc, y * 0.08 * sc, e.z - 0.2 * sc), rot=(y * 0.5, 0, 0)), hp)

def ink_sac(rig, C):
    sc = rig["sc"]; z = rig["shoulder_z"]; bw = rig["bw"]
    c = (bw * 0.38, -0.02 * sc, z - 0.04 * sc)
    gp = glow_pivot(rig, "sac", c, rig["torso"])
    attach(ball(0.25 * sc, PAL["ink"], c, scale=(1, 1.05, 0.95), glow=0.3, name="sac"), gp)
    attach(ball(0.12 * sc, PAL["sick"], (c[0] + 0.12 * sc, c[1] - 0.12 * sc, c[2] + 0.03 * sc), glow=2.0, name="saccore", outline=0.0), gp)
    for a in (-40, 10, 50):
        attach(box((0.03 * sc, 0.03 * sc, 0.26 * sc), PAL["sick"], (c[0] + 0.18 * sc, c[1] - 0.1 * sc, c[2]), rot=(math.radians(a), 0, 0), glow=1.2, name="vein", outline=0.0), gp)
    attach(box((0.03 * sc, 0.06 * sc, 0.14 * sc), PAL["ink"], (c[0] + 0.22 * sc, -0.05 * sc, c[2] - 0.3 * sc), name="drool", outline=0.0), rig["torso"])

register(dict(DEEP, id="spitter", scale=1.0, bulk=0.88, head=0.85, torso=1.05, leg=1.0, arm=1.1, limb=0.6, head_fwd=0.1,
              extras=[ink_sac, mantle_head, face_tentacles, rags, lambda r, C: dorsal_fin(r, C, 0.8, 3),
                      lambda r, C: hollow_cracks(r, C, 2)],
              style=dict(attack="spit", lean=18, headc=0.75, die="fwd", aR0=0, aL0=8, stride=24),
              colors=deep_colors(body=PAL["teal"], skin=(0.55, 0.42, 0.55), arms=(0.5, 0.4, 0.5), hands=(0.5, 0.4, 0.5),
                                 rag=(0.38, 0.4, 0.38))))
