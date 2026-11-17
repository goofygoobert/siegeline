from kit import *
# Bellringer — robed support carrying a big hand-bell on a pole.
def bellringer(t):
    return dict(portrait_noweapon=True, id="bellringer", scale=1.0, bulk=1.0, head=1.0, robe=True, helmet="coif", weapon="bellpole",
                style=dict(die_g=94, attack="ring", aR0=-15, aL0=-25, stride=22),
                colors=warden_colors(robe=(0.33, 0.30, 0.31), robe_trim=PAL["red"], body=PAL["red"], arms=(0.33, 0.30, 0.31),
                                     hands=PAL["skin"], hood=PAL["red_dk"]))
tiered(bellringer)
