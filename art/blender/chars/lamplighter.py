from kit import *
# Sawbones — ship's surgeon: white hair, brass spectacles, canvas apron over a brown waistcoat, lantern + bottle of grog.
ATTACKS["toast"] = dict(aR=[-15, -50, -100, -140, -160, -140, -70, -15], aL=[-25, -35, -50, -62, -70, -62, -40, -25],
                        torso=[0, -3, -6, -8, -8, -6, -3, 0], head=[0, -4, -8, -10, -10, -8, -4, 0], lL=[0] * 8, lR=[0] * 8,
                        k=dict(gR=[15, 50, 95, 130, 175, 140, 70, 15], gL=[25, 35, 50, 62, 70, 62, 40, 25],
                               lantern=[1, 1.1, 1.3, 1.7, 2.3, 1.8, 1.3, 1]))

def apron(rig, C):
    sc = rig["sc"]; tp = rig["torso"]; z = rig["hip_h"]; bw = rig["bw"]; th = rig["torso_h"]
    attach(box((0.06 * sc, bw * 0.66, th * 0.75 + z * 0.65), PAL["canvas"], (bw * 0.45, 0, z + th * 0.375 - z * 0.3), taper=(1, 0.8), name="apron"), tp)
    attach(box((0.03 * sc, 0.08 * sc, 0.1 * sc), (0.5, 0.1, 0.08), (bw * 0.49, -bw * 0.12, z - 0.05 * sc), name="stain", outline=0.0), tp)
    attach(box((0.03 * sc, 0.06 * sc, 0.06 * sc), (0.5, 0.1, 0.08), (bw * 0.49, bw * 0.1, z + 0.15 * sc), name="stain", outline=0.0), tp)

def sawbones(t):
    return dict(id="lamplighter", scale=1.0, bulk=0.95, head=1.0, helmet="whitehair", specs=True, nose_col=(0.86, 0.5, 0.42),
                weapon="bottle", offhand="lantern", extras=[apron],
                style=dict(die_g=0, attack="toast", aR0=-15, aL0=-25, stride=22,
                           anims=dict(idle=with_k(a_idle, gL=25), walk=with_k(a_walk, gL=25))),
                colors=crew_colors(body=(0.45, 0.3, 0.2), arms=(0.88, 0.84, 0.74), legs=(0.26, 0.22, 0.2)))
tiered(sawbones)
