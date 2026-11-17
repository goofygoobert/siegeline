from kit import *
# Maulwright — huge (1.4x) blackened plate, great hammer, two-handed slam.
def maul(t):
    return dict(portrait_noweapon=True, id="maulwright", scale=1.4, bulk=1.3, leg=0.9, helmet="great", no_face=True, pauldrons=True, head=0.85,
                tabard=True, weapon="greathammer",
                style=dict(attack="slam", aR0=-30, aL0=-30, heavy=1.4, swingL=False, swingR=False),
                colors=warden_colors(metal=(0.36, 0.37, 0.41), metal_dk=(0.22, 0.22, 0.26), arms=(0.36, 0.37, 0.41),
                                     legs=(0.26, 0.26, 0.3), body=(0.36, 0.37, 0.41), tabard=PAL["red"]))
tiered(maul)
