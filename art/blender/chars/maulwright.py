from kit import *
ATTACKS["anchor"] = dict(ATTACKS["slam"], k=dict(gR=[0, 10, 20, 20, 0, -8, -10, 0]))
# Anchorman — huge (1.4x) bald sailor in a tar-black vest, bare arms, black handlebar moustache, swings a ship's anchor.
def anchorman(t):
    return dict(portrait_noweapon=True, id="maulwright", scale=1.4, bulk=1.36, leg=0.9, head=0.85, helmet="bald",
                moustache=(0.1, 0.08, 0.07), weapon="anchor", grip=120,
                style=dict(attack="anchor", aR0=-30, aL0=-30, heavy=1.4, swingL=False, swingR=False),
                colors=crew_colors(body=(0.2, 0.18, 0.17), arms=PAL["skin"], legs=PAL["navy"], skin=(0.82, 0.6, 0.46)))
tiered(anchorman)
