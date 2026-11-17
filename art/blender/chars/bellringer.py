from kit import *
# Shantyman — big singer: yellow sou'wester, grey beard, navy jumper, red squeezebox. His shanty slows the Deep.
ATTACKS["squeeze"] = dict(aR=[-55, -48, -42, -40, -68, -66, -60, -55], aL=[-58, -64, -70, -72, -50, -52, -56, -58],
                          torso=[0, -3, -6, -7, 6, 5, 2, 0], head=[0, -6, -12, -15, 6, 4, 2, 0], lL=[0] * 8, lR=[0] * 8,
                          k=dict(squeeze=[1.0, 1.15, 1.3, 1.36, 0.68, 0.74, 0.88, 1.0], notes=[0.001, 0.001, 0.5, 0.8, 1.3, 1.1, 0.7, 0.001]))
_sq = lambda t: 1.0 + 0.14 * math.sin(t * math.tau)

def shantyman(t):
    return dict(id="bellringer", scale=1.0, bulk=1.25, head=1.02, helmet="souwester", beard=(0.78, 0.77, 0.74), beard_size=1.15,
                extras=[accordion],
                style=dict(attack="squeeze", aR0=-55, aL0=-58, stride=22, swingL=False, swingR=False, die_g=0,
                           anims=dict(idle=with_k(a_idle, squeeze=_sq, notes=lambda t: 0.001),
                                      walk=with_k(a_walk, squeeze=_sq))),
                colors=crew_colors(body=PAL["navy"], arms=PAL["navy"], legs=(0.32, 0.27, 0.22), hat=(0.96, 0.76, 0.16),
                                   box=PAL["sea_red"]))
tiered(shantyman)
