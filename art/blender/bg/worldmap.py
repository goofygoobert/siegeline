from kit import *
from scenery import *
from map_lib import *
# World map 2048x1024: painted toy diorama of the six regions joined by one road (data in map_lib.py).
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 48
S.render.resolution_x, S.render.resolution_y = MAP_W, MAP_H
S.render.film_transparent = False
sprite_lights()
for L_ in bpy.data.lights:
    L_.use_shadow = False      # no stair-step shadow banding on the faceted terrain
rnd = random.Random(4)


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def ground_color(x, y, h):
    ws = []; c = [0, 0, 0]; tot = 0
    for rid, _, (cx, cy), col in REGIONS:
        w = math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * 4.2 ** 2)); tot += w
        for i in range(3):
            c[i] += col[i] * w
    c = tuple(v / tot for v in c)
    k = 1 + 0.09 * math.sin(x * 3.1 + y * 2.3) * math.cos(y * 1.7 - x * 0.6)
    c = tuple(min(1, v * k) for v in c)
    if h < 0.1:
        c = mix(c, (0.38, 0.35, 0.31), min(1, (0.1 - h) / 0.1))
    if h > 0.9:
        c = mix(c, (0.44, 0.42, 0.44), min(1, (h - 0.9) / 0.8))
    if h > 2.6:
        c = mix(c, (0.72, 0.7, 0.68), min(1, (h - 2.6) / 0.5))
    d6 = math.hypot(x - 36.0, (y - 15.5) * 1.1)
    if d6 < 4.0:
        c = mix(c, (0.1, 0.08, 0.08), max(0, 1 - d6 / 4.0) ** 0.6)
    return c


def terrain():
    nx, ny = 210, 140
    x0, x1, y0, y1 = -2.0, 42.0, -4.0, 27.0
    verts = []; cols = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx; y = y0 + (y1 - y0) * j / ny; h = height(x, y)
            verts.append((x, y, h)); cols.append(ground_color(x, y, h))
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)]
    me = bpy.data.meshes.new("terrain"); me.from_pydata(verts, [], faces); me.update()
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
    for k, c in enumerate(cols):
        ca.data[k].color = (*lin(c), 1)
    ob = bpy.data.objects.new("terrain", me); S.collection.objects.link(ob)
    m = bpy.data.materials.new("terrain"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); dif = N.new("ShaderNodeBsdfDiffuse"); s2r = N.new("ShaderNodeShaderToRGB")
    bw = N.new("ShaderNodeRGBToBW"); ramp = N.new("ShaderNodeValToRGB"); cr = ramp.color_ramp; cr.interpolation = "EASE"
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.36, 0.32, 0.42, 1)
    cr.elements[1].position = 0.6; cr.elements[1].color = (1.08, 1.0, 0.92, 1)
    at = N.new("ShaderNodeVertexColor"); at.layer_name = "Col"
    mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1
    em = N.new("ShaderNodeEmission")
    L.new(dif.outputs[0], s2r.inputs[0]); L.new(s2r.outputs[0], bw.inputs[0]); L.new(bw.outputs[0], ramp.inputs[0])
    L.new(ramp.outputs[0], mul.inputs[6]); L.new(at.outputs[0], mul.inputs[7]); L.new(mul.outputs[2], em.inputs[0])
    L.new(em.outputs[0], out.inputs[0])
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = False
    return ob


def ground_z(x, y):
    return max(height(x, y), 0.02)


def tree(x, y, col, s=1.0):
    z = ground_z(x, y)
    cyl(0.06 * s, 0.3 * s, (0.25, 0.17, 0.12), (x, y, z + 0.15 * s), seg=6, outline=0.015)
    cyl(0.3 * s, 0.75 * s, col, (x, y, z + 0.6 * s), r2=0.0, seg=7, outline=0.015)


def dead(x, y, s=1.0):
    z = ground_z(x, y)
    cyl(0.04 * s, 0.6 * s, (0.15, 0.12, 0.12), (x, y, z + 0.3 * s), r2=0.015, seg=5, outline=0.012)
    cyl(0.025 * s, 0.3 * s, (0.15, 0.12, 0.12), (x + 0.08 * s, y, z + 0.45 * s), rot=(0, 0.8, 0), r2=0.01, seg=5, outline=0.012)


# terrain + ash sea
terrain()
sea = box((80, 60, 0.2), (0.15, 0.14, 0.17), (20, 11, -0.1), bevel=0.0, outline=0.0, name="sea")
# sea glints / ash floes
for i in range(80):
    x, y = rnd.uniform(-2, 42), rnd.uniform(-4, 27)
    if height(x, y) < -0.25:
        box((rnd.uniform(0.3, 0.9), 0.06, 0.02), (0.24, 0.22, 0.25), (x, y, 0.01), bevel=0.0, outline=0.0, name="floe")

# road: dark edge + dusty top
pts = road_curve()
for w, dz, col in ((0.34, 0.07, (0.2, 0.16, 0.14)), (0.2, 0.1, (0.66, 0.58, 0.46))):
    bm = bmesh.new(); prev = None
    for k, (x, y) in enumerate(pts):
        a = pts[min(k + 1, len(pts) - 1)]; b = pts[max(k - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]; l = math.hypot(dx, dy) or 1
        nx_, ny_ = -dy / l * w / 2, dx / l * w / 2
        z = ground_z(x, y) + dz
        v1 = bm.verts.new((x + nx_, y + ny_, z)); v2 = bm.verts.new((x - nx_, y - ny_, z))
        if prev:
            bm.faces.new((prev[0], prev[1], v2, v1))
        prev = (v1, v2)
    ob = _mesh_obj("road", bm); ob.data.materials.append(fmat(col))

# marsh pools (r2)
for i in range(40):
    x, y = rnd.uniform(8.0, 15.5), rnd.uniform(13.0, 20.5)
    if height(x, y) < 0.2:
        ob = cyl(rnd.uniform(0.3, 0.8), 0.04, (0.24, 0.32, 0.33), (x, y, max(height(x, y), 0) + 0.06), seg=12, outline=0.0, name="pool")
        ob.scale = (rnd.uniform(1.0, 1.8), rnd.uniform(0.6, 1.0), 1); ob.rotation_euler = (0, 0, rnd.uniform(0, 3))

# marker plinths (r6's marker is the glowing pool itself)
for rid, _, (x, y), _ in REGIONS[:-1]:
    z = ground_z(x, y)
    cyl(0.55, 0.16, (0.62, 0.58, 0.52), (x, y, z + 0.08), seg=20, outline=0.02, name="plinth")
    cyl(0.42, 0.04, (0.86, 0.64, 0.26), (x, y, z + 0.18), seg=20, outline=0.0, name="plinthring")


def near_road(x, y, d=0.8):
    return any(math.hypot(x - px, y - py) < d for px, py in pts[::3])


# r1 Cinderfold Vale: grey-green copses, the Lantern Keep
for i in range(90):
    x, y = rnd.uniform(1.5, 11.0), rnd.uniform(2.0, 11.5)
    if height(x, y) > 0.08 and not near_road(x, y):
        tree(x, y, (0.26, 0.32, 0.25) if i % 3 else (0.33, 0.38, 0.3), rnd.uniform(0.7, 1.1))
kx, ky = 3.6, 4.6; kz = ground_z(kx, ky)
box((0.9, 0.8, 1.2), STONE, (kx, ky, kz + 0.6), outline=0.02, name="mkeep")
cyl(0.32, 1.5, STONE_D, (kx - 0.55, ky + 0.2, kz + 0.75), seg=12, outline=0.02)
cyl(0.4, 0.5, SLATE, (kx - 0.55, ky + 0.2, kz + 1.75), r2=0.0, seg=12, outline=0.02)
box((0.32, 0.32, 0.36), GLOW, (kx, ky, kz + 1.4), glow=2.0, outline=0.02, name="mlantern")
cyl(0.26, 0.2, BRASS, (kx, ky, kz + 1.7), r2=0.04, seg=4, rot=(0, 0, 0.785), outline=0.02)
# r2 Bell Marshes: reeds, drowned trees, the bell tower
for i in range(70):
    x, y = rnd.uniform(7.5, 16.5), rnd.uniform(12.5, 21.5)
    h = height(x, y)
    if h > 0.02 and not near_road(x, y):
        if i % 3 == 0:
            tree(x, y, (0.2, 0.28, 0.25), rnd.uniform(0.6, 0.9))
        else:
            for k in range(3):
                cyl(0.025, 0.35, (0.42, 0.44, 0.3), (x + k * 0.07, y, max(h, 0) + 0.17), r2=0.0, seg=4, outline=0.0)
    elif h < 0.0 and i % 2:
        dead(x, y, rnd.uniform(0.7, 1.0))
bx, by = 13.8, 18.6; bz = ground_z(bx, by)
box((0.6, 0.6, 2.2), (0.48, 0.44, 0.4), (bx, by, bz + 1.1), outline=0.02, name="belltower")
cyl(0.55, 0.6, SLATE, (bx, by, bz + 2.5), r2=0.0, seg=4, rot=(0, 0, 0.785), outline=0.02)
ball(0.2, BRASS, (bx, by - 0.32, bz + 1.85), scale=(1, 1, 1.1), outline=0.02, name="bell")
# r3 Gilded Causeway: golden obelisks and an arch along the road
for k, (x, y) in enumerate(pts):
    if 16.2 < x < 22.0 and k % 9 == 0:
        for side in (-1, 1):
            cyl(0.12, 0.9, (0.86, 0.7, 0.34), (x, y + side * 0.45, ground_z(x, y) + 0.45), r2=0.04, seg=4, outline=0.02, name="obelisk")
ax_, ay_ = 19.0, 6.4; az = ground_z(ax_, ay_)
for side in (-0.55, 0.55):
    box((0.25, 0.25, 1.2), (0.82, 0.68, 0.36), (ax_ + side, ay_, az + 0.6), outline=0.02)
box((1.4, 0.3, 0.25), (0.9, 0.74, 0.38), (ax_, ay_, az + 1.3), outline=0.02)
for i in range(30):
    x, y = rnd.uniform(14.5, 23.5), rnd.uniform(3.0, 11.5)
    if height(x, y) > 0.1 and not near_road(x, y):
        box((0.2, 0.2, rnd.uniform(0.15, 0.4)), (0.7, 0.6, 0.42), (x, y, ground_z(x, y) + 0.1), rot=(0, 0, rnd.uniform(0, 3)), outline=0.015, name="ruinstone")
# r4 Hollowdeep Mines: shaft entrances with timber frames, spoil heaps, a headframe
for (x, y) in ((23.6, 15.6), (27.4, 16.2), (25.2, 14.9)):
    z = ground_z(x, y)
    box((0.55, 0.3, 0.5), (0.04, 0.03, 0.03), (x, y - 0.1, z + 0.25), outline=0.0, name="shaft")
    for sx in (-0.32, 0.32):
        box((0.08, 0.08, 0.6), WOOD, (x + sx, y - 0.2, z + 0.3), outline=0.015)
    box((0.75, 0.1, 0.08), WOOD, (x, y - 0.2, z + 0.62), outline=0.015)
    ball(0.35, (0.3, 0.27, 0.27), (x + 0.6, y - 0.4, z), scale=(1.2, 1, 0.5), outline=0.015)
hx_, hy_ = 22.8, 17.0; hz_ = ground_z(hx_, hy_)
for sx in (-0.25, 0.25):
    box((0.07, 0.07, 1.4), WOOD_D, (hx_ + sx, hy_, hz_ + 0.7), rot=(0, sx * 0.4, 0), outline=0.015)
cyl(0.18, 0.06, IRON, (hx_, hy_ - 0.05, hz_ + 1.35), rot=(math.radians(90), 0, 0), seg=10, outline=0.015)
box((0.06, 0.06, 0.06), GLOW, (24.2, 15.3, ground_z(24.2, 15.3) + 0.3), glow=2, outline=0.0)
# Hollowdeep peaks
for i in range(14):
    x, y = rnd.uniform(21.5, 30.0), rnd.uniform(17.0, 22.5)
    if near_road(x, y, 1.2) or height(x, y) < 0.5:
        continue
    hgt = rnd.uniform(1.2, 2.4); r_ = rnd.uniform(0.6, 1.1); z = ground_z(x, y)
    cyl(r_, hgt, (0.4, 0.38, 0.41), (x, y, z + hgt / 2 - 0.2), r2=0.05, seg=6, rot=(0, 0, rnd.uniform(0, 1)), outline=0.02, name="peak")
    cyl(r_ * 0.38, hgt * 0.36, (0.74, 0.72, 0.7), (x, y, z + hgt - 0.2 - hgt * 0.18 + 0.02), r2=0.04, seg=6, outline=0.0, name="ashcap")
# r5 Ember Wastes: glowing fissures, mesas, smoking vents
for i in range(22):
    x, y = rnd.uniform(27.0, 34.5), rnd.uniform(3.0, 11.0)
    if height(x, y) > 0.1 and not near_road(x, y, 0.5):
        z = ground_z(x, y)
        a = rnd.uniform(0, 3.14)
        box((rnd.uniform(0.6, 1.4), 0.07, 0.04), EMBER, (x, y, z + 0.02), rot=(0, 0, a), glow=1.5, outline=0.0, bevel=0.0, name="fissure")
for (x, y) in ((29.0, 5.5), (32.8, 9.6), (30.2, 10.2)):
    smoke_column(x, y, ground_z(x, y) + 0.2, 4, 0.5, seed=int(x), drift=0.15)
for i in range(25):
    x, y = rnd.uniform(26.5, 34.5), rnd.uniform(2.5, 11.5)
    if height(x, y) > 0.1 and not near_road(x, y):
        dead(x, y, rnd.uniform(0.6, 0.9))
# r6 the Cinder Maw: glowing crater pool, Maw gate on the rim, smoke
mz = ground_z(36.0, 15.5)
cyl(2.3, 0.08, (0.85, 0.28, 0.06), (36.0, 15.5, 0.25), seg=32, glow=0.4, outline=0.0, name="lava")
cyl(1.5, 0.1, (1.0, 0.5, 0.12), (36.0, 15.5, 0.29), seg=32, glow=0.6, outline=0.0, name="lavamid")
cyl(0.7, 0.12, (1.0, 0.8, 0.4), (36.0, 15.5, 0.33), seg=24, glow=0.8, outline=0.0, name="lavacore")
for i in range(16):
    a = rnd.uniform(0, math.tau); d = rnd.uniform(3.2, 4.4)
    x, y = 36.0 + math.cos(a) * d, 15.5 + math.sin(a) * d / 1.1
    cyl(rnd.uniform(0.12, 0.25), rnd.uniform(0.5, 1.1), (0.16, 0.13, 0.14), (x, y, ground_z(x, y) + 0.3), r2=0.0, seg=5, outline=0.015, name="crag")
for i in range(10):
    a = i / 10 * math.tau
    box((0.5, 0.06, 0.03), (0.15, 0.08, 0.06), (36.0 + math.cos(a) * 1.6, 15.5 + math.sin(a) * 1.5, 0.31), rot=(0, 0, a + 1.2), outline=0.0, bevel=0.0)
gx, gy = 33.6, 13.6; gz = ground_z(gx, gy)
for sx in (-0.4, 0.4):
    box((0.35, 0.35, 1.1), ASH, (gx + sx, gy, gz + 0.55), taper=(0.75, 0.75), outline=0.02)
box((0.9, 0.2, 0.18), BONE, (gx, gy - 0.1, gz + 0.85), outline=0.02)
for fx in (-0.2, 0.0, 0.2):
    cyl(0.06, 0.3, BONE, (fx + gx, gy - 0.15, gz + 0.62), r2=0.0, rot=(math.pi, 0, 0), seg=6, outline=0.015)
box((0.45, 0.06, 0.55), EMBER, (gx, gy - 0.05, gz + 0.35), glow=1.5, outline=0.0)
smoke_column(36.4, 16.0, 1.0, 6, 0.9, seed=3, drift=0.3)
pl = bpy.data.lights.new("maw", "POINT"); pl.energy = 900; pl.color = lin((1.0, 0.45, 0.15)); pl.shadow_soft_size = 2
po = bpy.data.objects.new("maw", pl); S.collection.objects.link(po); po.location = (36.0, 15.5, 1.5)

# camera
t = math.radians(TILT)
cd = bpy.data.cameras.new("mapcam"); cd.type = "ORTHO"; cd.ortho_scale = ORTHO; cd.clip_end = 300
cam = bpy.data.objects.new("mapcam", cd); S.collection.objects.link(cam); S.camera = cam
cam.rotation_euler = (t, 0, 0)
cam.location = (CAM_T[0], CAM_T[1] - 60 * math.sin(t), CAM_T[2] + 60 * math.cos(t))
w = S.world.node_tree.nodes.get("Background"); w.inputs[0].default_value = (*lin((0.12, 0.1, 0.12)), 1)
S.frame_start = S.frame_end = 1
