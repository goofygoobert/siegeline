from kit import *
# Cinder Runner — lean, unarmoured, red scarf, twin knives, fast forward-leaning run.
def runner(t):
    return dict(id="cinder_runner", scale=0.95, bulk=0.82, limb=0.9, leg=1.08, head=0.95, helmet="hair",
                weapon="knife", offhand="knife", grip_L=95, extras=[scarf],
                style=dict(attack="slash", aR0=-30, aL0=-20, stride=46, walk_lean=20, bounce=0.08, lean=4),
                colors=warden_colors(body=PAL["red_dk"], arms=PAL["skin"], hands=PAL["leather"], legs=(0.22, 0.18, 0.17),
                                     hair=(0.13, 0.1, 0.09), scarf=(0.86, 0.3, 0.12),
                                     metal=(0.36, 0.25, 0.17) if t == 2 else PAL["steel"]))
tiered(runner)
