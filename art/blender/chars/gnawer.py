from kit import *
# Scuttler — dog-sized crab-thing: six legs, eye stalks, one big snapping claw (snaps shut on frame 4).
register(dict(id="gnawer", facing=-1, builder=crab, scale=1.2,
              style=dict(anims=CRAB_ANIMS),
              colors=deep_colors(body=(0.2, 0.4, 0.41), skin=(0.33, 0.5, 0.46), legs=(0.26, 0.42, 0.4))))
