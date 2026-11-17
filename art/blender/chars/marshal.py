from kit import *
# Lantern Marshal (hero, 1.25x): crested great helm (no face inside), cape, sword + lantern. Extra anim: special.
SPECIAL = dict(aL=[10, -60, -130, -165, -172, -172, -120, -30], aR=[-15, -10, 0, 10, 10, 10, 0, -15],
               torso=[0, -3, -6, -8, -8, -6, -3, 0], head=[0, -5, -10, -12, -12, -10, -5, 0],
               lL=[0, 0, -5, -8, -8, -8, -4, 0], lR=[0, 0, 5, 8, 8, 8, 4, 0],
               k=dict(lantern=[1, 1, 1.2, 1.6, 3.4, 2.6, 1.6, 1]))
register(dict(id="marshal", scale=1.25, bulk=1.25, head=1.0, helmet="great", no_face=True, crest=True, gilded_helm=True,
              brass_pauldrons=True, pauldrons=True, cape=True, cape_len=1.05, tabard=True, weapon="sword", offhand="lantern",
              style=dict(attack="swing", heavy=1.2, aR0=-15, aL0=10, anims=dict(special=lambda t, st: _tab(SPECIAL, t))),
              colors=warden_colors(cloth=PAL["red"], metal=(0.42, 0.43, 0.48))))
