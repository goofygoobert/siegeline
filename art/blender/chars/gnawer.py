from kit import *
# Gnawer — small fast four-legged crawler with a bone jaw.
register(dict(id="gnawer", facing=-1, builder=quad, scale=1.15,
              style=dict(anims=QUAD_ANIMS),
              colors=hollow_colors(body=(0.32, 0.30, 0.30), skin=(0.38, 0.36, 0.36), legs=(0.28, 0.26, 0.26))))
