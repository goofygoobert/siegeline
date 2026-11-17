from kit import *
# Ashguard — stocky shield wall: tower shield, short sword, kettle helm.
def ashguard(t):
    return dict(id="ashguard", scale=1.0, bulk=1.32, leg=0.85, head=1.0, tabard=True, helmet="kettle",
                weapon="shortsword", grip=150, shield=True,
                style=dict(attack="thrust", aL0=-45, aR0=-60, heavy=1.25, swingL=False),
                colors=warden_colors())
tiered(ashguard)
