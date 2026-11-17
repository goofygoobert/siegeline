from kit import *
# World C enemy: Brass Sentinel automaton — box head with one lens eye
def lens(rig, C):
    sc = rig["sc"]; hz = rig["head_z"]; r = rig["head_r"]
    attach(box((r * 2.0, r * 1.9, r * 1.8), C["metal"], (0, 0, hz), name="boxhead", bevel=0.05), rig["head"])
    attach(cyl(r * 0.45, 0.1 * sc, (0.1, 0.1, 0.1), (r * 1.02, 0, hz), rot=(0, math.radians(90), 0)), rig["head"])
    attach(ball(r * 0.3, C["eyes"], (r * 1.1, 0, hz), glow=2.0, name="lens"), rig["head"])
    attach(cyl(0.12 * sc, 0.3 * sc, C["trim"], (-0.3 * sc, 0, rig["shoulder_z"] - 0.1 * sc), rot=(0, math.radians(90), 0)), rig["torso"])
SPEC = dict(id="c_sentinel", facing=-1, scale=1.05, bulk=1.15, taper=(1.25, 1.1), weapon="axe", pauldrons=True, extra=lens,
  style=dict(attack="swing", heavy=1.2), cell=(384, 384),
  colors=dict(body=(0.72, 0.5, 0.2), legs=(0.4, 0.3, 0.2), skin=(0.6, 0.45, 0.2), eyes=(0.3, 0.9, 1.0),
    metal=(0.78, 0.58, 0.25), trim=(0.45, 0.32, 0.18), wood=(0.3, 0.25, 0.2), arms=(0.55, 0.4, 0.2), belt=(0.3, 0.2, 0.1)))
build_and_animate(SPEC)
