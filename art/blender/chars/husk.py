from kit import *
# Husk — basic hunched Hollow: thin jagged limbs, bone claws, broken horn, ember eyes and cracks.
register(dict(HOLLOW, id="husk", scale=1.0, bulk=0.8, head=0.9, torso=1.1, leg=1.05, arm=1.25, head_fwd=0.12,
              weapon="claws", offhand="claws",
              extras=[lambda r, C: hollow_horns(r, C, 1.0, "L"), hollow_maw, hollow_ribs, hollow_cracks, hollow_elbows,
                      lambda r, C: hollow_spikes(r, C, 3)],
              style=dict(attack="claw", lean=20, headc=0.7, die="fwd", aR0=-10, aL0=5, stride=26),
              colors=hollow_colors()))
