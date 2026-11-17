from kit import *
# Lamplighter — healer with a long lamp-pole, ash-white robe with red trim. Attack = "cast" (lamp flares).
def lamp(t):
    return dict(portrait_noweapon=True, id="lamplighter", scale=1.0, bulk=0.95, head=1.0, robe=True, helmet="hood", weapon="lamppole",
                style=dict(die_g=94, attack="cast", aR0=-15, aL0=8, stride=22),
                colors=warden_colors(robe=PAL["ash"], robe_trim=PAL["red"], body=PAL["ash"], arms=PAL["ash"], hood=PAL["ash"],
                                     hands=PAL["skin"], belt=PAL["red"]))
tiered(lamp)
