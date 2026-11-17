from kit import *
# Bloater — fat round body with glowing pyre cracks, slow. Die = bursts into ichor and embers.
def belly(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]; th = rig["torso_h"]
    c = Vector((0.06 * sc, 0, z + th * 0.42))
    R = 0.62 * sc
    attach(ball(R, C["body"], c, scale=(1.0, 0.95, 0.92), seg=20, name="gut"), rig["torso"])
    gp = glow_pivot(rig, "pyre", c, rig["torso"])
    rnd = [(10, -40, 0.32), (35, -10, 0.28), (-15, -60, 0.24), (50, -35, 0.2), (-30, -20, 0.3), (20, -70, 0.2), (65, -15, 0.16)]
    for el, az, L in rnd:   # cracks on the camera-facing surface of the gut
        e = math.radians(el); a = math.radians(az)
        n = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
        p = c + Vector((n.x * R, n.y * R * 0.95, n.z * R * 0.92))
        attach(box((0.05 * sc, 0.05 * sc, L * sc), C["eyes"], p, rot=(math.radians(az), math.radians(el + 40), 0), glow=1.8, name="pyre", outline=0.0), gp)
    for i in range(3):
        attach(spike(c + Vector((-R * 0.7, (i - 1) * 0.2 * sc, R * 0.5)), (-0.6, 0, 1), (0.22, 0.3, 0.18)[i] * sc, 0.06 * sc, C["bone"]), rig["torso"])
    # burst chunks (hidden until the die anim): parented to the holder, scale-keyed
    br = empty("burst", (c.x, 0, c.z))
    rig["free"].append(br)
    import random as _r
    rr = _r.Random(3)
    for i in range(14):
        a = i / 14 * math.tau; el = rr.uniform(-0.4, 0.9)
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el) * 0.4, math.sin(el)))
        col = (PAL["ember"], C["body"], PAL["blood"], C["bone"])[i % 4]
        attach(ball(rr.uniform(0.06, 0.13) * sc, col, (c.x + d.x * 0.5 * sc, d.y * 0.5 * sc, c.z + d.z * 0.5 * sc),
                    glow=1.6 if i % 4 == 0 else 0.0, name="chunk", seg=8), br)
    keyable(rig, "burst", br, "scale", default=0.001)

BURST = dict(rs=[1.05, 1.12, 1.2, 1.28, 0.001, 0.001, 0.001, 0.001], torso=[0, -4, -6, -8, 0, 0, 0, 0],
             aR=[-30, -50, -70, -80, 0, 0, 0, 0], aL=[-30, -50, -70, -80, 0, 0, 0, 0],
             k=dict(pyre=[1.1, 1.25, 1.4, 1.6, 1, 1, 1, 1], burst=[0.001, 0.001, 0.001, 0.001, 0.9, 1.5, 1.9, 2.1]))

register(dict(HOLLOW, id="bloater", scale=1.1, bulk=1.15, head=0.72, torso=1.0, leg=0.72, arm=0.85, limb=0.7, head_fwd=0.1,
              foot=1.2, extras=[belly, lambda r, C: hollow_horns(r, C, 0.7, "L"), lambda r, C: hollow_maw(r, C, 0.8)],
              style=dict(attack="belly", lean=10, headc=0.5, aR0=-25, aL0=-20, stride=18, heavy=1.3, bounce=0.03,
                         anims=dict(die=lambda t, st: _tab(BURST, t))),
              colors=hollow_colors(body=(0.27, 0.25, 0.25))))
