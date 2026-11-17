from kit import *
from scenery import *
# Castles atlas sources. 864x864 cells at 96 px/u (packed down to 72 ppu), kit camera (ELEV 8).
# frames: 1-3 keep_0..2 (The Gullwake), 4-6 maw_0..2 (The Drowned Grotto), 7 ballista (Long Tom barrel).  Layout constants are mirrored in tools/pack_scenery.py.
reset()
S = bpy.context.scene


class _SceneFig:      # forts are painted with the figures' sunset lighting (kit2.paint) instead of the old toon bands
    def __init__(self):
        self.mats = {}; self.h = 9.0; self.ink = INK_CREW
        self.root = bpy.data.objects.new("scene_root", None); S.collection.objects.link(self.root)


_SF = _SceneFig()
# the Grotto is the darkest large shape on screen so monsters (mid-teal) stand clear of it (review 4)
GR = (0.17, 0.22, 0.25); GR_D = (0.10, 0.14, 0.17); GR_L = (0.26, 0.32, 0.33)


def toon(color, name=None, glow=0.0, rim=0.25):
    return paint(_SF, color, glow=min(glow, 2.0))


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
    turned(lambda: gullwake(k * 20.0, k), k * 20.0, -YAW)
    turned(lambda: grotto(60.0 + k * 20.0, k), 60.0 + k * 20.0, YAW)
long_tom(120.0, 1.0)
# preview frame 8: keep_0 with Long Tom mounted at the pivot (checks the pivot offset)
turned(lambda: gullwake(140.0, 0), 140.0, -YAW)
PX = 140.0 + 2.3 * math.cos(math.radians(YAW))
group(lambda: long_tom(PX, 4.4), (PX, 0, 4.4), move=(0, -2.3 * math.sin(math.radians(YAW)), 0))

cam = ortho_cam()
for k in range(3):
    sprite_cam_key(cam, 1 + k, k * 20.0 + 0.4, 4.0, CELL / PPU_R, elev=CAM_ELEV)
    sprite_cam_key(cam, 4 + k, 60.0 + k * 20.0, 4.0, CELL / PPU_R, elev=CAM_ELEV)
sprite_cam_key(cam, 7, 120.5, 1.0, CELL / PPU_R, elev=CAM_ELEV)
sprite_cam_key(cam, 8, 140.4, 4.0, CELL / PPU_R, elev=CAM_ELEV)
const_keys()
S.frame_start, S.frame_end = 1, 8
