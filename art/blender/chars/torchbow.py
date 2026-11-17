from kit import *
# Blackpowder — musketeer: long flintlock, black tricorn, navy coat, powder horn. Shot leaves on frame 4 (muzzle flash).
ATTACKS["musket"] = dict(aR=[-50, -75, -88, -88, -86, -82, -70, -55], aL=[-40, -62, -75, -75, -72, -70, -58, -42],
                         torso=[0, -2, -4, -4, -9, -6, -2, 0], head=[0, 4, 8, 8, 2, 4, 2, 0],
                         rx=[0, 0, 0, 0, -0.07, -0.05, -0.02, 0], lL=[-8] * 8, lR=[10] * 8,
                         k=dict(gR=[0, 60, 96, 96, 92, 88, 50, 10], flash=[0.001, 0.001, 0.001, 0.001, 1.2, 0.7, 0.001, 0.001]))

def blackpowder(t):
    return dict(portrait_noweapon=True, id="torchbow", scale=0.95, bulk=0.98, head=1.0, helmet="tricorn", moustache=(0.12, 0.1, 0.09),
                weapon="musket", extras=[powder_horn, lambda r, C: coat(r, C, 0.75)],
                style=dict(attack="musket", aR0=-50, aL0=-40, swingR=False),
                colors=crew_colors(body=PAL["navy"], coat=PAL["navy"], lapel=PAL["sea_red"], arms=PAL["navy"],
                                   legs=(0.8, 0.74, 0.6), hat=PAL["tar"]))
tiered(blackpowder)
