from kit import *
# World A (Ashen Marches) hero: the Lantern Marshal
SPEC = dict(id="a_marshal", scale=1.15, bulk=1.25, head=1.0, pauldrons=True, helmet="great", cape=True,
  weapon="sword", offhand="lantern", style=dict(attack="swing", heavy=1.2), cell=(384, 384),
  colors=dict(body=(0.55, 0.12, 0.1), legs=(0.18, 0.16, 0.17), boots=(0.12, 0.1, 0.1), skin=(0.85, 0.62, 0.5),
    metal=(0.62, 0.62, 0.66), trim=(0.85, 0.62, 0.22), cloth=(0.5, 0.08, 0.07), wood=(0.35, 0.22, 0.12),
    flame=(1.0, 0.62, 0.15), belt=(0.25, 0.15, 0.08), arms=(0.5, 0.5, 0.55)))
build_and_animate(SPEC)
