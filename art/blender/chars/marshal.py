from kit import *
# Captain Rook Halloran (hero, 1.25x): long red coat, huge black tricorn with a white plume and gold trim, cutlass + flintlock.
# Extra anim: special = raises the flare pistol and fires a flare (flash on frame 4).
SPECIAL = dict(aL=[-28, -70, -130, -165, -172, -172, -120, -30], aR=[-15, -10, 0, 10, 10, 10, 0, -15],
               torso=[0, -3, -6, -8, -8, -6, -3, 0], head=[0, -5, -10, -12, -12, -10, -5, 0],
               lL=[0, 0, -5, -8, -8, -8, -4, 0], lR=[0, 0, 5, 8, 8, 8, 4, 0],
               k=dict(gL=[0, 20, 55, 75, 80, 80, 40, 0], flare=[0.001, 0.001, 0.001, 0.001, 2.2, 1.7, 1.0, 0.001]))
register(dict(id="marshal", scale=1.25, bulk=1.22, head=0.95, helmet="tricorn", plume=True, hat_trim=True, hat_big=1.22,
              moustache=(0.12, 0.09, 0.08), beard=(0.12, 0.09, 0.08), beard_size=0.7,
              weapon="cutlass", offhand="pistol", extras=[lambda r, C: coat(r, C, 1.05)],
              style=dict(die="fwd", attack="swing", heavy=1.2, aR0=-15, aL0=-28, anims=dict(special=lambda t, st: _tab(SPECIAL, t))),
              colors=crew_colors(body=PAL["canvas"], coat=(0.62, 0.14, 0.12), lapel=PAL["gold"], arms=(0.62, 0.14, 0.12),
                                 legs=PAL["tar"], boots=(0.12, 0.1, 0.09), hat=(0.1, 0.09, 0.09), sash=PAL["navy"], belt=PAL["navy"])))
