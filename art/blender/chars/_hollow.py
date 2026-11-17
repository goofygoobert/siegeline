from kit import *
# Shared Hollow Host colour set (enemies face left: facing=-1).
def hollow_colors(**over):
    C = dict(body=PAL["hskin"], legs=(0.19, 0.18, 0.18), skin=(0.26, 0.25, 0.25), arms=PAL["hlimb"], hands=PAL["hlimb"],
             boots=(0.15, 0.14, 0.14), bone=PAL["bone"], eyes=PAL["ember"], blood=PAL["blood"], belt=PAL["blood"],
             metal=(0.4, 0.38, 0.36), metal_dk=(0.2, 0.19, 0.19), trim=PAL["rust"], wood=(0.3, 0.22, 0.16),
             rust=PAL["rust"], ember=PAL["ember"])
    C.update(over)
    return C

HOLLOW = dict(facing=-1, eye_style="slit", limb=0.65, taper=(1.3, 1.0))
