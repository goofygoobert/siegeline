from kit import *
# World B enemy: Drowned Bosun — bloated, barnacled, eel-lamp eyes
def barnacles(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]
    for (x, y, dz) in ((0.2, -0.2, 0.3), (0.15, 0.1, 0.5), (-0.1, -0.25, 0.45), (0.22, -0.05, 0.15)):
        attach(cyl(0.07 * sc, 0.07 * sc, C["bone"], (x * sc, y * sc, z + dz * sc), r2=0.04 * sc, seg=7), rig["torso"])
SPEC = dict(id="b_drowned", facing=-1, scale=1.05, bulk=1.45, head=1.1, taper=(0.9, 0.9), weapon="hammer", extra=barnacles,
  style=dict(attack="swing", heavy=1.4, lean=6), cell=(384, 384),
  colors=dict(body=(0.32, 0.42, 0.36), legs=(0.2, 0.26, 0.24), skin=(0.45, 0.55, 0.5), bone=(0.75, 0.75, 0.68),
    eyes=(0.4, 1.0, 0.8), eye_glow=2.0, metal=(0.35, 0.4, 0.38), trim=(0.5, 0.45, 0.3), wood=(0.25, 0.2, 0.15), belt=(0.2, 0.15, 0.12)))
build_and_animate(SPEC)
