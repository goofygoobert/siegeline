from kit import *
from scenery import *
from map_lib import *
# World map 2048x1024 (Tales of the Brine): an old sea chart as a toy diorama. Parchment border with a neatline,
# painted sea with depth bands and rhumb lines, raised islands, a dotted sailing route (data in map_lib.py).
reset()
S = bpy.context.scene
S.eevee.taa_render_samples = 48
S.render.resolution_x, S.render.resolution_y = MAP_W, MAP_H
S.render.film_transparent = False
sprite_lights()
for L_ in bpy.data.lights:
    L_.use_shadow = False      # no stair-step shadow banding on the faceted terrain
rnd = random.Random(4)
PARCH = (0.88, 0.8, 0.62); PARCH_D = (0.74, 0.62, 0.44); INKC = (0.2, 0.15, 0.13); ROUTE = (0.69, 0.19, 0.16)
SHALLOW = (0.74, 0.84, 0.72); MIDSEA = (0.58, 0.73, 0.68); DEEP = (0.46, 0.62, 0.62)
SAND_ = (0.88, 0.78, 0.56)
BORDER_U, BORDER_V = 0.022, 0.04


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def inside(x, y):
    u, v = project(x, y, 0.0)
    return BORDER_U < u < 1 - BORDER_U and BORDER_V < v < 1 - BORDER_V


def ground_color(x, y, h, kind):
    if not inside(x, y):
        k = 1 + 0.06 * _n(x * 2.0, y * 2.0, 9.0)
        return tuple(min(1, c * k) for c in PARCH)
    if h < 0:
        if h > -0.22:
            c = SHALLOW
        elif h > -0.55:
            c = MIDSEA
        else:
            c = DEEP
        wx, wy, wr = WHIRL
        dw = math.hypot(x - wx, y - wy)
        if dw < wr:
            c = mix(c, (0.16, 0.26, 0.34), (1 - dw / wr) ** 1.2)
        k = 1 + 0.05 * _n(x * 1.7, y * 1.7, 4.0)
        return tuple(min(1, v * k) for v in c)
    base = dict((rid, col) for rid, _, _, col in REGIONS).get(kind, (0.55, 0.55, 0.4))
    if h < 0.1:
        c = mix(SAND_ if kind != "r4" else (0.95, 0.78, 0.7), base, h / 0.1)
    else:
        c = base
        if h > 0.6:
            c = mix(c, (0.52, 0.48, 0.46), min(1, (h - 0.6) / 0.4))
    k = 1 + 0.08 * math.sin(x * 3.1 + y * 2.3) * math.cos(y * 1.7 - x * 0.6)
    return tuple(min(1, v * k) for v in c)


def terrain():
    nx, ny = 330, 230
    x0, x1, y0, y1 = -2.0, 42.0, -4.0, 27.0
    verts = []; cols = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx; y = y0 + (y1 - y0) * j / ny; h, kind = land(x, y)
            z = h if (h > 0 and inside(x, y)) else 0.0
            verts.append((x, y, z)); cols.append(ground_color(x, y, h, kind))
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
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.5, 0.45, 0.5, 1)
    cr.elements[1].position = 0.6; cr.elements[1].color = (1.05, 1.0, 0.94, 1)
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


def flatbox(x0, y0, x1, y1, z, color, alpha=1.0, glow=0.0):
    """Flat painted quad lying on the chart (unlit)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x0, y0, z)), bm.verts.new((x1, y0, z)), bm.verts.new((x1, y1, z)), bm.verts.new((x0, y1, z))]
    bm.faces.new(vs); ob = _mesh_obj("flat", bm); ob.data.materials.append(fmat(color, alpha, glow)); return ob


def flatpoly(pts, z, color, alpha=1.0, glow=0.0):
    bm = bmesh.new(); vs = [bm.verts.new((x, y, z)) for x, y in pts]
    bm.faces.new(vs); ob = _mesh_obj("flatp", bm); ob.data.materials.append(fmat(color, alpha, glow)); return ob


def line(p, q, w, z, color, alpha=1.0):
    dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy) or 1; nx_, ny_ = -dy / l * w / 2, dx / l * w / 2
    return flatpoly([(p[0] + nx_, p[1] + ny_), (q[0] + nx_, q[1] + ny_), (q[0] - nx_, q[1] - ny_), (p[0] - nx_, p[1] - ny_)], z, color, alpha)


def gz(x, y):
    return max(height(x, y), 0.0)


terrain()

# neatline (chart border): ink lines with alternating latitude ticks
xb0, xb1 = CAM_T[0] - ORTHO * (0.5 - BORDER_U), CAM_T[0] + ORTHO * (0.5 - BORDER_U)
yb0, yb1 = unproject_y(1 - BORDER_V), unproject_y(BORDER_V)
for (p, q) in (((xb0, yb0), (xb1, yb0)), ((xb0, yb1), (xb1, yb1)), ((xb0, yb0), (xb0, yb1)), ((xb1, yb0), (xb1, yb1))):
    line(p, q, 0.07, 0.03, INKC)
n = 28
for i in range(n):
    if i % 2 == 0:
        xa = xb0 + (xb1 - xb0) * i / n; xc = xb0 + (xb1 - xb0) * (i + 1) / n
        line((xa, yb0 - 0.12), (xc, yb0 - 0.12), 0.18, 0.03, INKC)
        line((xa, yb1 + 0.16), (xc, yb1 + 0.16), 0.22, 0.03, INKC)
m = 10
for i in range(m):
    if i % 2 == 0:
        ya = yb0 + (yb1 - yb0) * i / m; yc = yb0 + (yb1 - yb0) * (i + 1) / m
        line((xb0 - 0.12, ya), (xb0 - 0.12, yc), 0.18, 0.03, INKC)
        line((xb1 + 0.12, ya), (xb1 + 0.12, yc), 0.18, 0.03, INKC)

# compass rose + rhumb lines across the sea
cx, cy, cr_ = COMPASS
for k in range(16):
    a = k / 16 * math.tau
    end = (cx + math.cos(a) * 60, cy + math.sin(a) * 60)
    line((cx, cy), end, 0.035, 0.012, INKC, alpha=0.22)
for k in range(16):
    a = k / 16 * math.tau; big = k % 2 == 0; L = cr_ * (1.0 if k % 4 == 0 else 0.7 if big else 0.45)
    wdt = cr_ * (0.16 if big else 0.1)
    tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
    l_ = (cx + math.cos(a + math.pi / 2) * wdt, cy + math.sin(a + math.pi / 2) * wdt)
    r_ = (cx + math.cos(a - math.pi / 2) * wdt, cy + math.sin(a - math.pi / 2) * wdt)
    zz = 0.06 if k % 4 == 0 else 0.05 if big else 0.04
    flatpoly([(cx, cy), l_, tip], zz, NAVY if k % 4 == 0 else ROUTE if big else INKC)
    flatpoly([(cx, cy), tip, r_], zz, (0.95, 0.9, 0.78) if k % 4 == 0 else PARCH_D)
cyl(cr_ * 0.18, 0.06, BRASS, (cx, cy, 0.08), seg=20, outline=0.015, name="compasshub")
for k in range(48):
    a0 = k / 48 * math.tau; a1 = (k + 1) / 48 * math.tau
    line((cx + math.cos(a0) * cr_ * 0.82, cy + math.sin(a0) * cr_ * 0.82), (cx + math.cos(a1) * cr_ * 0.82, cy + math.sin(a1) * cr_ * 0.82),
         0.05, 0.035, INKC)
# north mark: a small fleur-like arrowhead
flatpoly([(cx - 0.18, cy + cr_ + 0.05), (cx, cy + cr_ + 0.5), (cx + 0.18, cy + cr_ + 0.05)], 0.06, ROUTE)

# sea glints / little wave marks
for i in range(120):
    x, y = rnd.uniform(0, 40), rnd.uniform(0.5, 23)
    if height(x, y) < -0.5 and inside(x, y) and math.hypot(x - WHIRL[0], y - WHIRL[1]) > WHIRL[2] and math.hypot(x - cx, y - cy) > cr_ * 1.2:
        for k in range(2):
            line((x + k * 0.22, y), (x + 0.12 + k * 0.22, y + 0.05), 0.04, 0.02, (0.92, 0.95, 0.88), alpha=0.6)
            line((x + 0.12 + k * 0.22, y + 0.05), (x + 0.22 + k * 0.22, y), 0.04, 0.02, (0.92, 0.95, 0.88), alpha=0.6)

# dotted sailing route
pts = road_curve(40)
acc = 0.0; dash = True
for a, b in zip(pts, pts[1:]):
    l = math.hypot(b[0] - a[0], b[1] - a[1]); acc += l
    if acc > (0.28 if dash else 0.2):
        acc = 0.0; dash = not dash
    if dash:
        za = max(gz(*a), gz(*b)) + 0.05
        line(a, b, 0.14, za, ROUTE)

# marker plinths: brass-rimmed parchment medallions
for rid, _, (x, y), _ in REGIONS:
    z = marker_z(x, y) - 0.3
    cyl(0.55, 0.16, PARCH_D, (x, y, z + 0.08), seg=24, outline=0.02, name="plinth")
    cyl(0.44, 0.04, BRASS, (x, y, z + 0.18), seg=24, outline=0.0, name="plinthring")


def tree(x, y, s=1.0, col=(0.3, 0.4, 0.28)):
    z = gz(x, y)
    cyl(0.05 * s, 0.25 * s, (0.3, 0.2, 0.14), (x, y, z + 0.12 * s), seg=6, outline=0.012)
    cyl(0.26 * s, 0.65 * s, col, (x, y, z + 0.5 * s), r2=0.0, seg=7, outline=0.012)


def tiny_ship(x, y, s=1.0, sail=CANVAS, wreck=False, ang=0.0):
    def build():
        box((1.1 * s, 0.38 * s, 0.26 * s), HULL, (x, y, 0.13 * s), taper=(1.15, 1.1), outline=0.014, name="mhull")
        box((0.32 * s, 0.4 * s, 0.22 * s), HULL_D, (x - 0.4 * s, y, 0.36 * s), outline=0.014)
        for k, dx in enumerate((-0.18, 0.2)):
            if wreck and k == 1:
                cyl(0.03 * s, 0.4 * s, HULL_D, (x + dx * s + 0.1 * s, y, 0.35 * s), rot=(0, 0.7, 0), seg=5, outline=0.01)
                continue
            cyl(0.03 * s, 0.95 * s, HULL_D, (x + dx * s, y, 0.7 * s), seg=5, outline=0.01)
            box((0.06 * s, 0.5 * s, 0.38 * s), sail, (x + dx * s, y, 0.78 * s), outline=0.012)
    group(build, (x, y, 0), rot=(0, 0, ang))


# r1 Saltwick Cove: lighthouse, the Gullwake on the rocks, harbour cottages, rugged trees
lx, ly = 3.4, 4.5
cyl(0.24, 1.6, (0.92, 0.88, 0.8), (lx, ly, gz(lx, ly) + 0.8), r2=0.17, seg=12, outline=0.015, name="lighthouse")
for k in range(3):
    cyl(0.235 - k * 0.022, 0.18, SEARED, (lx, ly, gz(lx, ly) + 0.35 + k * 0.45), seg=12, outline=0.0)
cyl(0.16, 0.22, (1.0, 0.85, 0.5), (lx, ly, gz(lx, ly) + 1.7), seg=10, glow=1.5, outline=0.012)
cyl(0.2, 0.2, INKC, (lx, ly, gz(lx, ly) + 1.9), r2=0.0, seg=10, outline=0.012)
tiny_ship(7.6, 6.3, 1.1, ang=0.4)
for (hx, hy) in ((5.6, 6.9), (6.1, 7.6), (5.0, 7.5)):
    hz = gz(hx, hy)
    box((0.45, 0.35, 0.3), (0.86, 0.8, 0.68), (hx, hy, hz + 0.15), outline=0.014)
    cyl(0.36, 0.25, SEARED, (hx, hy, hz + 0.42), r2=0.0, seg=4, rot=(0, 0, 0.785), outline=0.014)
for i in range(30):
    x, y = rnd.uniform(2.0, 8.0), rnd.uniform(3.6, 9.5)
    if height(x, y) > 0.25 and math.hypot(x - lx, y - ly) > 0.6 and math.hypot(x - 5.6, y - 7.3) > 1.0:
        tree(x, y, rnd.uniform(0.6, 0.9))
# r2 The Fogbanks: fog puffs and will-o'-wisps over low isles
for i in range(16):
    x, y = rnd.uniform(9.5, 15.0), rnd.uniform(13.6, 18.6)
    if math.hypot(x - 12.5, y - 15.5) < 1.4:
        continue
    ob = ball(rnd.uniform(0.3, 0.55), (0.93, 0.95, 0.92), (x, y, gz(x, y) + rnd.uniform(0.2, 0.5)), scale=(1.4, 1.1, 0.55), seg=12, outline=0.0, name="fog")
    ob.data.materials[0] = fmat((0.94, 0.96, 0.93), 0.42)
for i in range(9):
    x, y = rnd.uniform(9.8, 14.8), rnd.uniform(13.8, 18.3)
    ball(0.07, (0.5, 1.0, 0.62), (x, y, gz(x, y) + rnd.uniform(0.5, 0.9)), glow=2.0, seg=8, outline=0.0, name="wisp")
for i in range(12):
    x, y = rnd.uniform(9.5, 14.8), rnd.uniform(13.8, 18.3)
    if height(x, y) > 0.1:
        tree(x, y, rnd.uniform(0.45, 0.65), col=(0.36, 0.42, 0.38))
# r3 The Cutthroat Isles: jagged crags, wrecks of the Drowned Fleet, a black flag
for i in range(16):
    x, y = rnd.uniform(15.6, 21.8), rnd.uniform(3.5, 7.8)
    if height(x, y) > 0.35 and math.hypot(x - 18.5, y - 8.0) > 0.9:
        hgt = rnd.uniform(0.7, 1.5)
        cyl(rnd.uniform(0.3, 0.55), hgt, (0.42, 0.38, 0.36), (x, y, gz(x, y) + hgt / 2 - 0.1), r2=0.03, seg=5, rot=(0, 0, rnd.uniform(0, 1)), outline=0.015, name="crag")
tiny_ship(21.9, 8.4, 0.9, sail=(0.4, 0.44, 0.42), wreck=True, ang=-0.5)
tiny_ship(15.4, 6.9, 0.8, sail=(0.4, 0.44, 0.42), wreck=True, ang=0.9)
fx_, fy_ = 18.1, 6.4
cyl(0.03, 1.1, HULL_D, (fx_, fy_, gz(fx_, fy_) + 0.55), seg=5, outline=0.01)
box((0.4, 0.03, 0.26), INKC, (fx_ + 0.2, fy_, gz(fx_, fy_) + 0.95), outline=0.01)
# r4 Sunken Bell Reef: coral on the atoll, the drowned bell tower in the lagoon, a mermaid's rock
ax_, ay_, aR, aw, _ = ATOLL
for i in range(40):
    a = rnd.uniform(0, math.tau); d = aR + rnd.uniform(-0.25, 0.25)
    x, y = ax_ + math.cos(a) * d, ay_ + math.sin(a) * d / 1.1
    col = (0.92, 0.46, 0.38) if i % 3 else (0.62, 0.36, 0.62)
    cyl(0.07, rnd.uniform(0.2, 0.4), col, (x, y, gz(x, y) + 0.12), r2=0.02, seg=5, rot=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 0), outline=0.01, name="coral")
bx, by = 25.2, 16.9
box((0.45, 0.45, 0.9), (0.7, 0.68, 0.62), (bx, by, 0.3), outline=0.015, name="belltower")
cyl(0.42, 0.45, (0.3, 0.42, 0.4), (bx, by, 0.95), r2=0.0, seg=4, rot=(0, 0, 0.785), outline=0.015)
ball(0.15, BRASS, (bx, by - 0.24, 0.62), scale=(1, 1, 1.15), outline=0.015, name="bell")
for k in range(3):
    cyl(0.4 + k * 0.25, 0.01, (0.92, 0.95, 0.88), (bx, by, 0.01 + k * 0.001), seg=24, outline=0.0, name="ripple").data.materials[0] = fmat((0.92, 0.95, 0.88), 0.35)
# r5 Leviathan's Reach: a sea serpent's coils breaking the surface
sx0, sy0 = 25.8, 4.6
for k in range(4):
    x = sx0 + k * 1.05; r_ = 0.42 - 0.04 * k
    pts_ = [(x + r_ * math.cos(a), sy0 + 0.1 * k, r_ * math.sin(a) * 1.15) for a in [math.pi * (1 - i / 10) for i in range(11)]]
    for p, q in zip(pts_, pts_[1:]):
        rod(p, q, 0.13 - 0.01 * k, (0.24, 0.48, 0.46), seg=8, outline=0.014, name="coil")
    spike((x, sy0 + 0.1 * k, r_ * 1.15 + 0.08), (0, 0, 1), 0.2, 0.05, (0.8, 0.62, 0.36), seg=5)
hx, hy = sx0 - 0.75, sy0 - 0.15
rod((hx + 0.25, hy, 0.0), (hx, hy, 0.75), 0.15, (0.24, 0.48, 0.46), seg=8, outline=0.014)
ball(0.24, (0.24, 0.48, 0.46), (hx - 0.12, hy, 0.85), scale=(1.5, 0.9, 0.8), seg=10, outline=0.014, name="shead")
ball(0.05, (0.9, 1.0, 0.6), (hx - 0.2, hy - 0.18, 0.92), glow=1.5, seg=6, outline=0.0)
for k in range(3):
    spike((hx - 0.05 + k * 0.08, hy, 0.98), (0.4, 0, 1), 0.28, 0.05, (0.8, 0.62, 0.36), seg=5)
for i in range(14):
    x, y = rnd.uniform(28.0, 33.6), rnd.uniform(5.2, 7.6)
    if height(x, y) > 0.2 and math.hypot(x - 29.5, y - 8.0) > 0.8:
        box((0.18, 0.16, rnd.uniform(0.1, 0.25)), (0.84, 0.78, 0.66), (x, y, gz(x, y) + 0.08), rot=(0, 0, rnd.uniform(0, 3)), outline=0.012, name="bone")
# r6 The Maelstrom: the great whirlpool (spiral foam arms sinking to a dark eye)
wx, wy, wr = WHIRL
for arm in range(4):
    prev = None
    for i in range(60):
        t_ = i / 59; a = arm * math.pi / 2 + t_ * 3.4 * math.pi; d = wr * (1 - t_) * 0.95 + 0.15
        p = (wx + math.cos(a) * d, wy + math.sin(a) * d * 0.95)
        if prev:
            line(prev, p, 0.16 * (1 - t_) + 0.04, 0.02 + 0.001 * arm, (0.88, 0.94, 0.92), alpha=0.85)
        prev = p
cyl(0.5, 0.02, (0.06, 0.1, 0.14), (wx, wy, 0.015), seg=24, outline=0.0, name="eye")
for i in range(5):
    a = rnd.uniform(0, math.tau); d = rnd.uniform(0.9, 2.2)
    box((0.35, 0.08, 0.06), HULL, (wx + math.cos(a) * d, wy + math.sin(a) * d, 0.05), rot=(0, 0, a + 1.4), outline=0.01, name="flotsam")
for i in range(12):
    x, y = rnd.uniform(30.8, 37.8), rnd.uniform(12.0, 18.4)
    if height(x, y) > 0.2:
        hgt = rnd.uniform(0.4, 0.9)
        cyl(rnd.uniform(0.2, 0.35), hgt, (0.3, 0.3, 0.33), (x, y, gz(x, y) + hgt / 2 - 0.1), r2=0.02, seg=5, outline=0.014, name="crag")
# a little crew ship under way between r1 and r2, gulls
tiny_ship(10.4, 12.6, 0.85, sail=CANVAS, ang=0.9)
flush()

# camera
t = math.radians(TILT)
cd = bpy.data.cameras.new("mapcam"); cd.type = "ORTHO"; cd.ortho_scale = ORTHO; cd.clip_end = 300
cam = bpy.data.objects.new("mapcam", cd); S.collection.objects.link(cam); S.camera = cam
cam.rotation_euler = (t, 0, 0)
cam.location = (CAM_T[0], CAM_T[1] - 60 * math.sin(t), CAM_T[2] + 60 * math.cos(t))
w = S.world.node_tree.nodes.get("Background"); w.inputs[0].default_value = (*lin(PARCH), 1)
S.frame_start = S.frame_end = 1
