from kit import *
# Drowner — a drowned sailor come back: grey-green, kelp hair, barnacles, rotted shirt rags, glowing eyes, claw hands.
register(dict(DEEP, id="husk", scale=1.0, bulk=0.8, head=0.9, torso=1.1, leg=1.05, arm=1.25, head_fwd=0.12,
              arm_scale=dict(R=1.15), weapon="claws", offhand="claws",
              extras=[kelp_hair, hollow_maw, gills, rags, lambda r, C: hollow_cracks(r, C, 2), hollow_elbows,
                      lambda r, C: shoulder_barnacles(r, C, 1.0, 4)],
              style=dict(attack="claw", lean=20, headc=0.7, die="fwd", aR0=-10, aL0=5, stride=26),
              colors=deep_colors(body=(0.42, 0.47, 0.46))))
