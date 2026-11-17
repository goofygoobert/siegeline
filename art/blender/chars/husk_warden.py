from kit import *
# The Kelpie (mini-boss, 1.5x) — ghastly water-horse rearing on its hind legs: long horse skull, kelp mane and tail,
# glowing eyes, hooves. Attack = rears and stamps both fore-hooves down (frame 4).
def horse_head(rig, C):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    sk = C["skin"]
    attach(rod((0, 0, rig["shoulder_z"] - 0.05 * sc), (hx + r * 0.1, 0, hz - r * 0.2), r * 0.6, sk, r2=r * 0.5, seg=12), hp)
    attach(box((r * 1.6, r * 1.3, r * 1.35), sk, (hx, 0, hz + r * 0.1), taper=(0.85, 0.9), name="skull"), hp)
    sn = box((r * 1.7, r * 0.85, r * 0.8), sk, (hx + r * 1.35, 0, hz - r * 0.3), taper=(0.8, 0.85), rot=(0, math.radians(18), 0), name="snout")
    attach(sn, hp)
    attach(box((r * 1.3, r * 0.6, r * 0.18), C["bone"], (hx + r * 1.3, 0, hz + r * 0.08), rot=(0, math.radians(18), 0), name="bonestrip"), hp)
    for y in (-0.22, 0.22):
        attach(ball(0.04 * sc, PAL["dark"], (hx + r * 2.1, y * r, hz - r * 0.45), name="nostril", outline=0.0), hp)
    for i in range(4):
        attach(spike((hx + r * (1.3 + i * 0.22), -r * 0.36, hz - r * 0.72 + i * 0.05 * sc), (0.1, 0, -1), 0.08 * sc, 0.025 * sc, C["bone"], outline=0.006), hp)
    for y in (-0.62, 0.62):
        attach(box((0.08 * sc, r * 0.32, r * 0.18), C["eyes"], (hx + r * 0.55, y * r, hz + r * 0.25), rot=(math.radians(25 if y > 0 else -25), 0, 0), glow=2.0, name="eye", outline=0.012), hp)
        attach(spike((hx - r * 0.3, y * r * 0.6, hz + r * 0.7), (-0.3, y * 0.3, 1), 0.24 * sc, 0.06 * sc, sk), hp)
    col = C["kelp"]
    for i in range(7):    # mane from the poll down the neck
        b = Vector((hx - r * 0.5 - i * 0.07 * sc, (-1) ** i * 0.05 * sc, hz + r * 0.6 - i * 0.11 * sc))
        e = b + Vector((-0.6, 0, -0.8)).normalized() * (0.38 + 0.1 * (i % 3)) * sc
        attach(rod(b, e, 0.06 * sc, col, r2=0.012 * sc, seg=6), hp)

def kelp_tail(rig, C):
    sc = rig["sc"]; z = rig["hip_h"]; bw = rig["bw"]
    for i, (a, L) in enumerate(((-20, 0.7), (-35, 0.6), (-8, 0.55))):
        b = Vector((-bw * 0.4, (i - 1) * 0.05 * sc, z + 0.05 * sc)); ra = math.radians(a)
        m = b + Vector((-0.5, 0, -0.2)).normalized() * L * 0.5 * sc; e = m + Vector((-0.3, 0, -1)).normalized() * L * 0.5 * sc
        attach(rod(b, m, 0.07 * sc, C["kelp"], r2=0.045 * sc, seg=6), rig["torso"]); attach(rod(m, e, 0.045 * sc, C["kelp"], r2=0.01 * sc, seg=6), rig["torso"])

register(dict(DEEP, id="husk_warden", scale=1.5, bulk=0.95, head=0.85, no_face=True, torso=1.15, leg=1.05, arm=1.15, limb=0.85, head_fwd=0.16,
              hand=1.5, foot=1.05,
              extras=[horse_head, kelp_tail, lambda r, C: hollow_ribs(r, C, 3, 0.8), lambda r, C: dorsal_fin(r, C, 0.7, 4),
                      lambda r, C: shoulder_barnacles(r, C, 1.0, 3), lambda r, C: hollow_cracks(r, C, 3)],
              style=dict(attack="heavy", lean=8, headc=0.5, die="fwd", aR0=-55, aL0=-40, heavy=1.3, stride=24),
              colors=deep_colors(body=(0.2, 0.36, 0.37), skin=(0.34, 0.47, 0.45), arms=(0.27, 0.42, 0.41), hands=(0.13, 0.15, 0.15),
                                 boots=(0.13, 0.15, 0.15), legs=(0.24, 0.38, 0.38))))
