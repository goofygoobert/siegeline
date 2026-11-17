from kit import *
# Torchbow — hooded archer, bow, quiver of burning arrows. Attack = "shoot" (arrow leaves on frame 4).
def nocked_arrow(rig, C):
    sc = rig["sc"]; hand = rig["hand_R"]; p = hand.matrix_world.translation.copy()
    h = empty("arrow", (p.x, p.y - 0.05 * sc, p.z))
    attach(rod((p.x, p.y - 0.05 * sc, p.z - 0.1 * sc), (p.x, p.y - 0.05 * sc, p.z + 0.62 * sc), 0.018 * sc, C["wood"]), h)
    attach(ball(0.05 * sc, C["ember"], (p.x, p.y - 0.05 * sc, p.z + 0.64 * sc), scale=(1, 1, 1.5), glow=2.0, outline=0.0, name="tip"), h)
    h.rotation_euler = (0, math.radians(170), 0)
    bpy.context.view_layer.update()
    h.parent = hand; h.matrix_parent_inverse = hand.matrix_world.inverted()
    keyable(rig, "arrow", h, "scale", default=0.0)

def torchbow(t):
    return dict(id="torchbow", scale=0.95, bulk=0.95, head=1.0, tabard=True, helmet="hood", offhand="bow",
                extras=[quiver, nocked_arrow],
                style=dict(attack="shoot", aL0=-10, aR0=-15),
                colors=warden_colors(body=(0.42, 0.28, 0.18), arms=(0.42, 0.28, 0.18), legs=(0.26, 0.2, 0.17),
                                     metal=(0.42, 0.44, 0.48) if t < 2 else PAL["steel"]))
tiered(torchbow)
