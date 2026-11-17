from kit import *
# Gnawer — small fast four-legged crawler with a bone jaw.
register(dict(id="gnawer", facing=-1, builder=quad, scale=1.0,
              style=dict(anims=QUAD_ANIMS),
              colors=hollow_colors(body=(0.25, 0.24, 0.24), skin=(0.3, 0.28, 0.28), legs=(0.2, 0.19, 0.19))))
