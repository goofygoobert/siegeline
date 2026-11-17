from kit import *
from scenery import *
# Castles atlas sources. 864x864 cells at 96 px/u (packed down to 72 ppu), kit camera (ELEV 8).
# frames: 1-3 keep_0..2, 4-6 maw_0..2, 7 ballista.  Layout constants are mirrored in tools/pack_scenery.py.
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 32
CELL, PPU_R = 864, 96
S.render.resolution_x = S.render.resolution_y = CELL
sprite_lights()
YAW = 15.0          # castles turn this much toward the camera (characters use 25)
CAM_ELEV = 10.0     # same elevation as the character kit


def turned(fn, ox, deg):
    before = set(bpy.data.objects)
    fn()
    holder = empty("turn", (ox, 0, 0)); bpy.context.view_layer.update()
    for ob in set(bpy.data.objects) - before:
        if ob.parent is None and ob is not holder:
            ob.parent = holder; ob.matrix_parent_inverse = holder.matrix_world.inverted()
    holder.rotation_euler = (0, 0, math.radians(deg))


for k in range(3):
    turned(lambda: keep(k * 20.0, k), k * 20.0, -YAW)
    turned(lambda: maw(60.0 + k * 20.0, k), 60.0 + k * 20.0, YAW)
ballista(120.0, 1.0)
cam = ortho_cam()
for k in range(3):
    sprite_cam_key(cam, 1 + k, k * 20.0 + 0.4, 4.0, CELL / PPU_R, elev=CAM_ELEV)
    sprite_cam_key(cam, 4 + k, 60.0 + k * 20.0, 4.0, CELL / PPU_R, elev=CAM_ELEV)
sprite_cam_key(cam, 7, 120.5, 1.0, CELL / PPU_R, elev=CAM_ELEV)
const_keys()
S.frame_start, S.frame_end = 1, 7
