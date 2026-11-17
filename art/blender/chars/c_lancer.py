from kit import *
# World C (Glasswind) hero: Sun-Lancer
SPEC = dict(id="c_lancer", scale=1.1, bulk=1.0, helmet="sunhat", weapon="spear", shield="round", cape=True,
  style=dict(attack="thrust"), cell=(384, 384),
  colors=dict(body=(0.92, 0.88, 0.78), legs=(0.75, 0.5, 0.25), boots=(0.4, 0.25, 0.15), skin=(0.62, 0.42, 0.3),
    metal=(0.9, 0.75, 0.35), trim=(0.85, 0.35, 0.15), cloth=(0.85, 0.35, 0.15), wood=(0.5, 0.35, 0.2),
    shield=(0.9, 0.7, 0.3), belt=(0.6, 0.25, 0.1)))
build_and_animate(SPEC)
