from kit import *
from scenery import *
from r1_lib import *
# Region r1 "Cinderfold Vale" parallax layers, day (frames 1-4) and night/boss r1n (frames 5-8).
# Every frame renders 3900x810 (66 px/u); tools/pack_scenery.py crops each to its contract width.
# frame: 1 sky, 2 far, 3 mid, 4 near, 5 sky(n), 6 far(n), 7 mid(n), 8 near(n)
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 32
cam = ortho_cam("bgcam")
cam.rotation_euler = (math.radians(90), 0, 0)
cam.data.ortho_scale = 3900 / BG_PX
S.render.resolution_x, S.render.resolution_y = 3900, 810
S.render.resolution_percentage = 100
frame = 1
for night, P in ((False, DAY), (True, NIGHT)):
    for name, fn in (("sky", build_sky), ("far", build_far), ("mid", build_mid), ("near", build_near)):
        oz = (frame - 1) * 20.0
        before = set(bpy.data.objects)
        fn(P, night); flush()
        for ob in set(bpy.data.objects) - before:
            ob.location.z += oz
        key_cam(cam, frame, (3900 / BG_PX / 2, -100, oz + (BG_BOT + BG_TOP) / 2))
        frame += 1
const_keys()
S.frame_start, S.frame_end = 1, 8
