from kit import *
# Hatchguard — burly deckhand: ship's hatch door as a shield, short cutlass, red polka-dot bandana, brown beard.
def hatchguard(t):
    return dict(id="ashguard", scale=1.0, bulk=1.32, leg=0.85, head=1.0, helmet="bandana", beard=(0.36, 0.22, 0.12),
                weapon="cutlass_s", grip=150, shield="hatch",
                style=dict(attack="thrust", aL0=-45, aR0=-60, heavy=1.25, swingL=False),
                colors=crew_colors(body=(0.86, 0.8, 0.66), arms=PAL["skin"], legs=PAL["navy"], hat=PAL["sea_red"]))
tiered(hatchguard)
