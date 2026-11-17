from kit import *
# Rope Rat — wiry cabin hand: bare feet, red-striped canvas shirt, spiky ginger hair, a knife in each hand, leaning run.
def roperat(t):
    return dict(id="cinder_runner", scale=0.95, bulk=0.82, limb=0.9, leg=1.08, head=0.95, helmet="hair",
                weapon="knife", offhand="knife", grip_L=95, extras=[stripes, scarf],
                style=dict(attack="slash", aR0=-30, aL0=-20, stride=46, walk_lean=20, bounce=0.08, lean=4),
                colors=crew_colors(body=PAL["canvas"], stripe=PAL["sea_red"], arms=PAL["skin"], legs=(0.48, 0.38, 0.27),
                                   boots=PAL["skin"], hair=(0.88, 0.42, 0.12), scarf=PAL["navy"]))
tiered(roperat)
