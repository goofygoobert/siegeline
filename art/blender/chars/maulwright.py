from kit import *
# Maulwright — huge (1.4x) blackened plate, great hammer, two-handed slam.
def maul(t):
    return dict(id="maulwright", scale=1.4, bulk=1.3, leg=0.9, head=1.0, helmet="great", no_face=True, pauldrons=True,
                tabard=True, weapon="greathammer", grip=150,
                style=dict(attack="slam", aR0=-30, aL0=-30, heavy=1.4, swingL=False, swingR=False),
                colors=warden_colors(metal=(0.27, 0.28, 0.31), metal_dk=(0.17, 0.17, 0.2), arms=(0.27, 0.28, 0.31),
                                     legs=(0.2, 0.2, 0.23), body=(0.27, 0.28, 0.31), tabard=PAL["red"]))
tiered(maul)
