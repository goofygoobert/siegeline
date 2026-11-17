from kit import *
# Shared Gullwake Crew colour set (players, face right). Tier looks come from the kit (spec["tier"]):
# t2 leather jerkin, bracers, boot cuffs, sash tails, hat feather; t3 gold trim, doubloon necklace, cursed green-gold weapon.
def crew_colors(**over):
    C = dict(body=PAL["navy"], tabard=PAL["navy"], legs=(0.30, 0.27, 0.25), boots=PAL["tar"], skin=PAL["skin"],
             metal=(0.66, 0.68, 0.72), metal_dk=(0.32, 0.33, 0.36), trim=PAL["gold"], arms=PAL["navy"], hands=PAL["skin"],
             belt=PAL["sea_red"], sash=PAL["sea_red"], shield=PAL["wood"], flame=PAL["lamp"], wood=PAL["wood"], crest=PAL["sea_red"],
             leather=PAL["leather"], jerkin=(0.45, 0.29, 0.17), cloth=PAL["sea_red"], hood=PAL["sea_red"], ember=PAL["cursed"],
             feather=(0.95, 0.93, 0.87), hat=PAL["tar"], eyes=(0.06, 0.05, 0.05))
    C.update(over)
    return C


def tiered(make):
    for t in (1, 2, 3):
        s = make(t)
        s["tier"] = t
        s["id"] = s["id"] + ("" if t == 1 else "_t%d" % t)
        register(s)
