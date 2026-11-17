from kit import *
# World A enemy: Hollow husk — gaunt, ash-grey, ember eyes, bone claws
def ribs(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]
    for i in range(3):
        attach(box((0.06 * sc, 0.4 * sc, 0.035 * sc), C["bone"], (0.17 * sc, 0, z + 0.28 * sc + i * 0.11 * sc), name="rib"), rig["torso"])
    attach(box((0.08 * sc, 0.1 * sc, 0.14 * sc), (0.35, 0.02, 0.03), (0.2 * sc, -0.1 * sc, z + 0.15 * sc), name="wound"), rig["torso"])
SPEC = dict(id="a_hollow", facing=-1, scale=1.0, bulk=0.8, head=0.9, torso=1.1, leg=1.1, taper=(1.3, 1.0),
  weapon="claws", offhand="claws", helmet="horns", extra=ribs, style=dict(attack="swing", lean=14),
  colors=dict(body=(0.24, 0.23, 0.25), legs=(0.18, 0.17, 0.19), skin=(0.3, 0.29, 0.31), bone=(0.82, 0.78, 0.66),
    eyes=(1.0, 0.45, 0.08), eye_glow=2.0, metal=(0.4, 0.4, 0.4), trim=(0.4, 0.3, 0.2), wood=(0.3, 0.2, 0.1), belt=(0.15, 0.12, 0.12)))
build_and_animate(SPEC)
