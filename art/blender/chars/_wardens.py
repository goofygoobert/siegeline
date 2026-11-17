from kit import *
# Shared Lantern Warden colour set (players). Tier looks are handled by the kit (spec["tier"]).
def warden_colors(**over):
    C = dict(body=PAL["red"], tabard=PAL["red"], legs=PAL["steel_dk"], boots=(0.16, 0.12, 0.10), skin=PAL["skin"],
             metal=PAL["steel"], metal_dk=PAL["steel_dk"], trim=PAL["brass"], arms=PAL["steel"], hands=PAL["leather"],
             belt=PAL["leather"], shield=PAL["red"], flame=PAL["glow"], wood=PAL["wood"], crest=PAL["red"],
             leather=PAL["leather"], cloth=PAL["red"], hood=PAL["red_dk"], ember=PAL["ember"])
    C.update(over)
    return C


def tiered(make):
    for t in (1, 2, 3):
        s = make(t)
        s["tier"] = t
        s["id"] = s["id"] + ("" if t == 1 else "_t%d" % t)
        register(s)
