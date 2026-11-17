from kit import *
# World B (Saltreach) hero: Tide-Captain with harpoon
SPEC = dict(id="b_captain", scale=1.1, bulk=1.1, helmet="tricorn", cape=True, weapon="harpoon",
  style=dict(attack="thrust"), cell=(384, 384),
  colors=dict(body=(0.1, 0.38, 0.42), legs=(0.85, 0.78, 0.6), boots=(0.25, 0.15, 0.1), skin=(0.78, 0.55, 0.42),
    metal=(0.7, 0.72, 0.7), trim=(0.85, 0.7, 0.3), cloth=(0.12, 0.14, 0.22), wood=(0.45, 0.3, 0.18), belt=(0.3, 0.18, 0.1)))
build_and_animate(SPEC)
