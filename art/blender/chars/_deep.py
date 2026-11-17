from kit import *
# Shared colour set for the Deep (enemies face left: facing=-1). Wet green-grey/teal, shell, sickly green glow, ink.
def deep_colors(**over):
    C = dict(body=PAL["drown"], legs=(0.22, 0.33, 0.31), skin=(0.4, 0.55, 0.48), arms=(0.36, 0.5, 0.44), hands=(0.36, 0.5, 0.44),
             boots=(0.16, 0.22, 0.22), bone=PAL["shell"], eyes=PAL["sick"], blood=PAL["ink"], belt=(0.3, 0.26, 0.2),
             metal=(0.42, 0.44, 0.42), metal_dk=(0.2, 0.22, 0.22), trim=(0.45, 0.36, 0.2), wood=(0.35, 0.28, 0.2),
             rust=PAL["rust"], ember=PAL["sick"], kelp=PAL["kelp"], fin=PAL["teal"], rag=(0.47, 0.5, 0.45))
    C.update(over)
    return C

DEEP = dict(facing=-1, eye_style="slit", limb=0.65, taper=(1.3, 1.0))


def shoulder_barnacles(rig, C, s=1.0, n=4, side="R"):
    sc = rig["sc"]; z = rig["shoulder_z"]; bw = rig["bw"]
    y0 = -bw * 0.5 if side == "R" else bw * 0.5
    pts = [(-0.05 * sc + i * 0.07 * sc, y0 - 0.06 * sc, z + 0.06 * sc - (i % 2) * 0.08 * sc) for i in range(n)]
    barnacles(rig, C, rig["arm_" + side], pts, s)
