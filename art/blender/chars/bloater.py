from kit import *
# Pufferghast — swollen spiny puffer-fish on stubby legs, glowing green cracks, fish lips. Die = bursts (slime + spines).
def puffer(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]; th = rig["torso_h"]
    c = Vector((0.06 * sc, 0, z + th * 0.42)); R = 0.62 * sc
    attach(ball(R, C["body"], c, scale=(1.0, 0.95, 0.92), seg=20, name="gut"), rig["torso"])
    attach(ball(R * 0.75, C.get("belly", PAL["shell"]), c + Vector((R * 0.3, -R * 0.15, -R * 0.3)), scale=(0.9, 0.9, 0.8), seg=16, name="belly"), rig["torso"])
    for i in range(26):    # spines over the whole ball (golden-angle spiral)
        u = (i + 0.5) / 26; el = math.asin(1 - 2 * u) * 0.95; az = i * 2.39996
        n = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        if n.z < -0.75:
            continue
        p = c + Vector((n.x * R, n.y * R * 0.95, n.z * R * 0.92))
        attach(spike(tuple(p), tuple(n), (0.2 + 0.08 * (i % 3)) * sc, 0.045 * sc, C["bone"]), rig["torso"])
    gp = glow_pivot(rig, "pyre", c, rig["torso"])
    for el, az, L in [(10, -40, 0.32), (35, -10, 0.28), (-15, -60, 0.24), (50, -35, 0.2), (-30, -20, 0.3), (20, -70, 0.2)]:
        e = math.radians(el); a = math.radians(az)
        n = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
        p = c + Vector((n.x * R, n.y * R * 0.95, n.z * R * 0.92))
        attach(box((0.05 * sc, 0.05 * sc, L * sc), C["eyes"], p, rot=(math.radians(az), math.radians(el + 40), 0), glow=1.8, name="pyre", outline=0.0), gp)
    # fish face on the front of the ball
    f = c + Vector((R * 0.92, -R * 0.1, R * 0.15))
    attach(cyl(0.12 * sc, 0.1 * sc, (0.72, 0.5, 0.45), tuple(f + Vector((0.04 * sc, 0, -0.12 * sc))), rot=(0, math.radians(90), 0), seg=14, name="lips"), rig["torso"])
    attach(cyl(0.07 * sc, 0.11 * sc, PAL["dark"], tuple(f + Vector((0.06 * sc, 0, -0.12 * sc))), rot=(0, math.radians(90), 0), seg=12, name="mouth", outline=0.0), rig["torso"])
    for y in (-0.22, 0.22):
        attach(ball(0.1 * sc, C["eyes"], tuple(f + Vector((-0.04 * sc, y * sc, 0.14 * sc))), glow=2.0, name="eye", outline=0.014), rig["torso"])
    attach(prism([(0, 0), (-0.32 * sc, 0.22 * sc), (-0.26 * sc, -0.2 * sc)], 0.04 * sc, C["fin"], loc=(c.x - R * 0.95, 0, c.z)), rig["torso"])
    for y in (-1, 1):
        attach(prism([(0, 0), (-0.2 * sc, 0.12 * sc), (-0.16 * sc, -0.1 * sc)], 0.03 * sc, C["fin"], loc=(c.x + 0.1 * sc, y * R * 0.95, c.z - 0.05 * sc)), rig["torso"])
    br = empty("burst", (c.x, 0, c.z)); rig["free"].append(br)
    import random as _r
    rr = _r.Random(3)
    for i in range(14):
        a = i / 14 * math.tau; el = rr.uniform(-0.4, 0.9)
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el) * 0.4, math.sin(el)))
        col = (PAL["sick"], C["body"], PAL["ink"], C["bone"])[i % 4]
        attach(ball(rr.uniform(0.06, 0.13) * sc, col, (c.x + d.x * 0.5 * sc, d.y * 0.5 * sc, c.z + d.z * 0.5 * sc),
                    glow=1.6 if i % 4 == 0 else 0.0, name="chunk", seg=8), br)
    keyable(rig, "burst", br, "scale", default=0.001)

BURST = dict(rs=[1.05, 1.12, 1.2, 1.28, 0.001, 0.001, 0.001, 0.001], torso=[0, -4, -6, -8, 0, 0, 0, 0],
             aR=[-30, -50, -70, -80, 0, 0, 0, 0], aL=[-30, -50, -70, -80, 0, 0, 0, 0],
             k=dict(pyre=[1.1, 1.25, 1.4, 1.6, 1, 1, 1, 1], burst=[0.001, 0.001, 0.001, 0.001, 0.9, 1.5, 1.9, 2.1]))

register(dict(DEEP, id="bloater", scale=1.1, bulk=1.15, head=0.5, no_face=True, torso=1.0, leg=0.72, arm=0.7, limb=0.7, head_fwd=0.1,
              foot=1.2, extras=[puffer],
              style=dict(attack="belly", lean=10, headc=0.5, aR0=-25, aL0=-20, stride=18, heavy=1.3, bounce=0.03,
                         anims=dict(die=lambda t, st: _tab(BURST, t))),
              colors=deep_colors(body=(0.5, 0.56, 0.36), belly=(0.78, 0.76, 0.6), arms=PAL["teal"], hands=PAL["teal"])))
