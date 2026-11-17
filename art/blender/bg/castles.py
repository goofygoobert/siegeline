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
for k in range(3):
    keep(k * 20.0, k)
    maw(60.0 + k * 20.0, k)
ballista(120.0, 1.0)
cam = ortho_cam()
for k in range(3):
    sprite_cam_key(cam, 1 + k, k * 20.0 + 0.4, 4.0, CELL / PPU_R)
    sprite_cam_key(cam, 4 + k, 60.0 + k * 20.0, 4.0, CELL / PPU_R)
sprite_cam_key(cam, 7, 120.5, 1.0, CELL / PPU_R)
const_keys()
S.frame_start, S.frame_end = 1, 7
