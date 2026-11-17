# Siegeline scenery library (The Ashen Marches) — bundled after kit.py:
#   python3 tools/bundle_blend.py SCRIPT OUT --lib art/blender/scenery.py
# 2D "painted" layers are flat emission polygons standing in the XZ plane (camera looks +Y, smaller y = nearer).
# 3D props (castles, fx) use the kit's toon() + outline primitives.
import bpy, bmesh, math, random
from mathutils import Vector
from kit import *

BG_PX = 66.0                # px per world unit in background renders (44 logical px * 1.5)
BG_H = 810 / BG_PX          # 12.27 u: one layer's height
BG_BOT = -210 / BG_PX       # ground line (y=400 logical) is z=0; image bottom is 140 logical px below it
BG_TOP = BG_BOT + BG_H


# ------------------------------------------------------------------ materials
_fm = {}
def fmat(color, alpha=1.0, glow=0.0, top=None, a_top=None, noise=0.0, nscale=1.2, stops=None, radial=None):
    """Unlit painted material. top: vertical gradient bottom->top (object bbox); a_top: alpha at top;
    noise: +/- value variation; stops: [(pos, color), ...] for multi-stop vertical gradients."""
    key = (tuple(color), alpha, glow, tuple(top) if top else None, a_top, noise, nscale, str(stops), radial)
    if key in _fm:
        return _fm[key]
    m = bpy.data.materials.new("paint"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.0 + glow
    zsock = None
    if top is not None or a_top is not None or stops:
        tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Generated"], sep.inputs[0]); zsock = sep.outputs[2]
    if stops:
        ramp = N.new("ShaderNodeValToRGB"); cr = ramp.color_ramp; cr.interpolation = "EASE"
        cr.elements[0].position = stops[0][0]; cr.elements[0].color = (*lin(stops[0][1]), 1)
        cr.elements[1].position = stops[-1][0]; cr.elements[1].color = (*lin(stops[-1][1]), 1)
        for p, c in stops[1:-1]:
            e = cr.elements.new(p); e.color = (*lin(c), 1)
        L.new(zsock, ramp.inputs[0]); col = ramp.outputs[0]
    elif top is not None:
        ramp = N.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*lin(color), 1); ramp.color_ramp.elements[1].color = (*lin(top), 1)
        L.new(zsock, ramp.inputs[0]); col = ramp.outputs[0]
    else:
        rgb = N.new("ShaderNodeRGB"); rgb.outputs[0].default_value = (*lin(color), 1); col = rgb.outputs[0]
    if noise > 0:
        tc2 = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = nscale; nz.inputs["Detail"].default_value = 4.0
        L.new(tc2.outputs["Object"], nz.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.3; mr.inputs[2].default_value = 0.7
        mr.inputs[3].default_value = 1 - noise; mr.inputs[4].default_value = 1 + noise
        L.new(nz.outputs[0], mr.inputs[0])
        mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1
        L.new(col, mul.inputs[6]); L.new(mr.outputs[0], mul.inputs[7]); col = mul.outputs[2]
    L.new(col, em.inputs[0]); sh = em.outputs[0]
    if alpha < 1 or a_top is not None or radial:
        tr = N.new("ShaderNodeBsdfTransparent"); mix = N.new("ShaderNodeMixShader")
        if radial:
            # soft disc: alpha = alpha * (1 - 2*dist)^radial, dist from the bbox centre in the XZ plane
            tc3 = N.new("ShaderNodeTexCoord"); sp = N.new("ShaderNodeSeparateXYZ"); cb = N.new("ShaderNodeCombineXYZ")
            L.new(tc3.outputs["Generated"], sp.inputs[0]); L.new(sp.outputs[0], cb.inputs[0]); L.new(sp.outputs[2], cb.inputs[2])
            dist = N.new("ShaderNodeVectorMath"); dist.operation = "DISTANCE"; dist.inputs[1].default_value = (0.5, 0, 0.5)
            L.new(cb.outputs[0], dist.inputs[0])
            mr3 = N.new("ShaderNodeMapRange"); mr3.inputs[1].default_value = 0.0; mr3.inputs[2].default_value = 0.5
            mr3.inputs[3].default_value = 1.0; mr3.inputs[4].default_value = 0.0
            L.new(dist.outputs["Value"], mr3.inputs[0])
            pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = radial
            L.new(mr3.outputs[0], pw.inputs[0])
            mu = N.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = alpha
            L.new(pw.outputs[0], mu.inputs[0]); L.new(mu.outputs[0], mix.inputs[0])
        elif a_top is None:
            mix.inputs[0].default_value = alpha
        else:
            mr2 = N.new("ShaderNodeMapRange"); mr2.inputs[3].default_value = alpha; mr2.inputs[4].default_value = a_top
            L.new(zsock, mr2.inputs[0]); L.new(mr2.outputs[0], mix.inputs[0])
        L.new(tr.outputs[0], mix.inputs[1]); L.new(sh, mix.inputs[2]); sh = mix.outputs[0]
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            m.blend_method = "BLEND"
    L.new(sh, out.inputs[0])
    _fm[key] = m
    return m


# ------------------------------------------------------------------ 2D painting
_ord = [0]
_batch = {}
def poly(pts, y, color, alpha=1.0, glow=0.0, own=False, **kw):
    """Filled polygon [(x, z), ...] at depth y. Later calls draw in front (painter's order).
    Plain colours are batched into one mesh per material; gradient/noise materials get their own object."""
    _ord[0] += 1
    yy = y - _ord[0] * 0.0004
    m = fmat(color, alpha, glow, **kw)
    clean = []
    for p in pts:
        if not clean or abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1]) > 1e-5:
            clean.append(p)
    if len(clean) > 2 and abs(clean[0][0] - clean[-1][0]) + abs(clean[0][1] - clean[-1][1]) < 1e-5:
        clean.pop()
    if len(clean) < 3:
        return None
    if own or kw or alpha < 1 or kw.get('radial'):
        cx = sum(p[0] for p in clean) / len(clean); cz = sum(p[1] for p in clean) / len(clean)
        bm = bmesh.new(); vs = [bm.verts.new((x - cx, 0, z - cz)) for x, z in clean]
        try:
            bm.faces.new(vs)
        except ValueError:
            pass
        ob = _mesh_obj("p", bm); ob.data.materials.append(m); ob.location = (cx, yy, cz)
        for p in ob.data.polygons:
            p.use_smooth = False
        return ob
    bm = _batch.setdefault(m.name, (bmesh.new(), m))[0]
    vs = [bm.verts.new((x, yy, z)) for x, z in clean]
    try:
        bm.faces.new(vs)
    except ValueError:
        pass
    return None


def flush():
    for name, (bm, m) in list(_batch.items()):
        ob = _mesh_obj("batch", bm); ob.data.materials.append(m)
    _batch.clear()


def rect(x0, z0, x1, z1, y, color, **kw):
    return poly([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y, color, **kw)


def ellipse_pts(cx, cz, rx, rz, n=20, rot=0.0, wob=0.0, seed=0):
    r = random.Random(seed); out = []
    for i in range(n):
        a = i / n * math.tau; k = 1 + wob * (r.random() - 0.5)
        x, z = math.cos(a) * rx * k, math.sin(a) * rz * k
        out.append((cx + x * math.cos(rot) - z * math.sin(rot), cz + x * math.sin(rot) + z * math.cos(rot)))
    return out


def ellipse(cx, cz, rx, rz, y, color, n=20, rot=0.0, wob=0.0, seed=0, **kw):
    return poly(ellipse_pts(cx, cz, rx, rz, n, rot, wob, seed), y, color, **kw)


def seg(x0, z0, x1, z1, w0, w1, y, color, **kw):
    """Tapered stroke from (x0,z0) width w0 to (x1,z1) width w1."""
    dx, dz = x1 - x0, z1 - z0; l = math.hypot(dx, dz) or 1e-6; nx, nz = -dz / l, dx / l
    return poly([(x0 + nx * w0 / 2, z0 + nz * w0 / 2), (x1 + nx * w1 / 2, z1 + nz * w1 / 2),
                 (x1 - nx * w1 / 2, z1 - nz * w1 / 2), (x0 - nx * w0 / 2, z0 - nz * w0 / 2)], y, color, **kw)


def wave(seed, n=5, base=0.6):
    """Smooth 1D noise in roughly [-1, 1]."""
    r = random.Random(seed)
    comps = [(r.uniform(0.3, 1.0) / (i + 1) ** 0.8, base * (1.7 ** i) * r.uniform(0.8, 1.2), r.uniform(0, math.tau)) for i in range(n)]
    tot = sum(c[0] for c in comps)
    return lambda x: sum(a * math.sin(x * f + p) for a, f, p in comps) / tot


def profile(x0, x1, fn, step=0.25):
    pts = []; x = x0
    while x < x1 + step:
        pts.append((x, fn(x))); x += step
    return pts


def band(prof, bottom_z, y, color, **kw):
    """Polygon under a top profile down to bottom_z."""
    pts = list(prof) + [(prof[-1][0], bottom_z), (prof[0][0], bottom_z)]
    return poly(pts, y, color, own=True, **kw)


def hill_line(x0, x1, base, amp, seed, freq=0.35, jag=0.0, step=0.25):
    w = wave(seed, base=freq); r = random.Random(seed + 99)
    return profile(x0, x1, lambda x: base + amp * w(x) + jag * (r.random() - 0.5), step)


# ------------------------------------------------------------------ painted props (silhouettes)
def ruin_tower(x, z, w, h, y, color, lit=None, win=None, seed=0, crenel=True, broken=0.35, taper=0.12):
    """Watchtower silhouette with a broken top. lit: right-edge light strip colour. win: ember window colour."""
    r = random.Random(seed); hw = w / 2; tw = hw * (1 - taper)
    top = []
    n = 7
    for i in range(n + 1):
        t = i / n; xx = x - tw + 2 * tw * t
        hh = h - (broken * h * r.random() if r.random() < 0.6 else 0) * (0.3 + 0.7 * abs(t - 0.3))
        if crenel and i % 2 == 0 and r.random() < 0.7:
            hh += 0.18 * w
        top.append((xx, z + hh))
    pts = [(x - hw, z - 0.6)] + top + [(x + hw, z - 0.6)]
    poly(pts, y, color)
    if lit:
        poly([(x + hw * 0.55, z - 0.6), (x + tw * 0.55, top[-2][1] - 0.05), (x + tw, top[-1][1] - 0.05), (x + hw, z - 0.6)], y, lit)
    # stone courses (slightly darker lines)
    if win:
        for k in range(r.randint(1, 3)):
            wz = z + h * (0.35 + 0.18 * k)
            if wz < min(t[1] for t in top) - 0.25:
                wx = x + r.uniform(-0.25, 0.15) * w
                poly([(wx - 0.05 * w, wz), (wx + 0.05 * w, wz), (wx + 0.05 * w, wz + 0.16 * w), (wx, wz + 0.21 * w), (wx - 0.05 * w, wz + 0.16 * w)], y, win, glow=0.3)
    return top


def chapel(x, z, s, y, color, lit, win, seed=3):
    """Burnt chapel: nave with broken gable, collapsed roof beams, stub spire, pointed ember windows."""
    r = random.Random(seed)
    L, H = 3.2 * s, 1.6 * s
    poly([(x - L / 2, z - 0.5), (x - L / 2, z + H), (x - L / 2 + 0.5 * s, z + H + 0.25 * s), (x - 0.3 * s, z + H + 0.05 * s),
          (x + 0.1 * s, z + H + 0.35 * s), (x + L / 2 - 0.9 * s, z + H), (x + L / 2 - 0.9 * s, z - 0.5)], y, color)
    # gable end (right) with broken peak
    gx = x + L / 2 - 0.9 * s
    poly([(gx, z - 0.5), (gx, z + H), (gx + 0.45 * s, z + H + 0.95 * s), (gx + 0.62 * s, z + H + 0.7 * s), (gx + 0.7 * s, z + H + 0.8 * s),
          (gx + 0.9 * s, z + H), (gx + 0.9 * s, z - 0.5)], y, color)
    poly([(gx + 0.62 * s, z - 0.5), (gx + 0.62 * s, z + H + 0.2 * s), (gx + 0.7 * s, z + H + 0.8 * s), (gx + 0.9 * s, z + H), (gx + 0.9 * s, z - 0.5)], y, lit)
    # spire stump at left
    sx = x - L / 2 + 0.35 * s
    poly([(sx - 0.35 * s, z - 0.5), (sx - 0.35 * s, z + H + 1.2 * s), (sx - 0.1 * s, z + H + 1.55 * s), (sx + 0.05 * s, z + H + 1.3 * s),
          (sx + 0.35 * s, z + H + 1.45 * s), (sx + 0.35 * s, z - 0.5)], y, color)
    # charred rafters
    for i in range(4):
        bx = x - L / 2 + 0.8 * s + i * 0.55 * s
        seg(bx, z + H, bx + 0.25 * s, z + H + r.uniform(0.35, 0.7) * s, 0.07 * s, 0.05 * s, y, color)
    # pointed windows
    for i in range(3):
        wx = x - L / 2 + 0.9 * s + i * 0.7 * s
        poly([(wx - 0.12 * s, z + 0.5 * s), (wx + 0.12 * s, z + 0.5 * s), (wx + 0.12 * s, z + 1.05 * s), (wx, z + 1.25 * s), (wx - 0.12 * s, z + 1.05 * s)], y, win, glow=0.2)
    poly([(gx + 0.33 * s, z + 0.9 * s), (gx + 0.57 * s, z + 0.9 * s), (gx + 0.57 * s, z + 1.5 * s), (gx + 0.45 * s, z + 1.75 * s), (gx + 0.33 * s, z + 1.5 * s)], y, win, glow=0.2)


def dead_tree(x, z, h, y, color, seed=0, lean=0.0, w=None):
    r = random.Random(seed); w = w or h * 0.07
    def branch(x0, z0, ang, l, wd, depth):
        x1, z1 = x0 + math.sin(ang) * l, z0 + math.cos(ang) * l
        seg(x0, z0, x1, z1, wd, wd * 0.55, y, color)
        if depth > 0:
            for k in range(r.randint(1, 3) if depth < 3 else 2):
                branch(x1, z1, ang + r.uniform(-0.9, 0.9), l * r.uniform(0.5, 0.75), wd * 0.6, depth - 1)
    seg(x - w * 1.3, z - 0.2, x, z + 0.3, w * 0.8, w, y, color)
    seg(x + w * 1.3, z - 0.2, x, z + 0.3, w * 0.8, w, y, color)
    branch(x, z - 0.2, lean, h * 0.45, w, 3)


def pike(x, z, h, y, color, bone=None, seed=0, lean=0.0):
    """Stake with a skull (slightly grim, not gory)."""
    tx, tz = x + math.sin(lean) * h, z + math.cos(lean) * h
    seg(x, z - 0.3, tx, tz, 0.09, 0.05, y, color)
    if bone:
        ellipse(tx, tz + 0.12, 0.15, 0.14, y, bone, n=12)
        rect(tx - 0.08, tz - 0.02, tx + 0.08, tz + 0.06, y, bone)
        ellipse(tx + 0.05, tz + 0.13, 0.04, 0.045, y, color, n=8)


def gibbet(x, z, h, y, color, seed=0):
    seg(x, z - 0.3, x, z + h, 0.14, 0.11, y, color)
    seg(x - 0.05, z + h - 0.05, x + 0.9, z + h - 0.05, 0.1, 0.08, y, color)
    seg(x, z + h - 0.5, x + 0.45, z + h - 0.05, 0.06, 0.06, y, color)
    cx = x + 0.8; seg(cx, z + h - 0.05, cx, z + h - 0.45, 0.025, 0.025, y, color)
    top, bot = z + h - 0.45, z + h - 1.35
    for i in range(5):
        xx = cx - 0.25 + i * 0.125; seg(xx, top, xx, bot, 0.035, 0.035, y, color)
    rect(cx - 0.28, top - 0.05, cx + 0.28, top + 0.03, y, color); rect(cx - 0.28, bot - 0.03, cx + 0.28, bot + 0.05, y, color)
    poly([(cx - 0.28, top + 0.02), (cx, top + 0.2), (cx + 0.28, top + 0.02)], y, color)


def rock(x, z, s, y, color, seed=0, lit=None):
    r = random.Random(seed); n = 9; pts = []
    for i in range(n + 1):
        a = math.pi * i / n; k = r.uniform(0.75, 1.1)
        pts.append((x - math.cos(a) * s * 1.2 * k, z + math.sin(a) * s * 0.75 * k))
    poly(pts, y, color)
    if lit:
        poly([(px, pz) for px, pz in pts[:4]] + [(pts[3][0], pts[3][1] - 0.15 * s), (pts[0][0] + 0.1 * s, pts[0][1])], y, lit)


def tuft(x, z, s, y, color, seed=0):
    r = random.Random(seed)
    for i in range(5):
        a = -0.6 + i * 0.3 + r.uniform(-0.1, 0.1)
        l = s * r.uniform(0.6, 1.0)
        poly([(x - 0.04 * s + i * 0.02 * s, z), (x + math.sin(a) * l, z + math.cos(a) * l), (x + 0.06 * s + i * 0.02 * s, z)], y, color)


def palisade(x0, x1, z, h, y, color, seed=0):
    r = random.Random(seed); x = x0
    while x < x1:
        if r.random() > 0.25:
            hh = h * r.uniform(0.4, 1.0); lean = r.uniform(-0.15, 0.15)
            poly([(x - 0.08, z - 0.2), (x - 0.08 + lean, z + hh), (x + lean, z + hh + 0.15), (x + 0.08 + lean, z + hh), (x + 0.08, z - 0.2)], y, color)
        x += 0.22
    seg(x0, z + h * 0.35, x1, z + h * 0.3 + r.uniform(-0.1, 0.1), 0.06, 0.06, y, color)


def banner_pole(x, z, h, y, color, cloth, seed=0):
    r = random.Random(seed)
    seg(x, z - 0.2, x, z + h, 0.07, 0.05, y, color)
    pts = [(x, z + h - 0.05), (x + 0.6, z + h - 0.1)]
    for i in range(5):
        pts.append((x + 0.6 - i * 0.03 + (0.1 if i % 2 else -0.05), z + h - 0.25 - i * 0.22 + r.uniform(-0.05, 0.05)))
    pts.append((x, z + h - 1.2))
    poly(pts, y, cloth)


def embers(x0, x1, z0, z1, y, n, color, seed=0, size=0.05, alpha=0.9, glow=1.0):
    r = random.Random(seed)
    for i in range(n):
        x, z = r.uniform(x0, x1), r.uniform(z0, z1); s = size * r.uniform(0.5, 1.4); a = r.uniform(0, 1)
        poly([(x - s, z), (x, z + s * 1.6), (x + s, z), (x, z - s * 1.6)], y, color, alpha=alpha, glow=glow)


def smoke(x, z, h, y, color, alpha=0.35, seed=0, r0=0.4, drift=1.2):
    r = random.Random(seed); n = int(h / 0.35)
    for i in range(n):
        t = i / max(n - 1, 1)
        ellipse(x + drift * t * t + r.uniform(-0.15, 0.15), z + h * t, r0 * (0.6 + 1.4 * t), r0 * (0.5 + 1.0 * t), y, color,
                n=14, wob=0.25, seed=seed + i, alpha=alpha * (1 - 0.7 * t))


def crack(x, z, l, y, color, seed=0, glow=1.0, w=0.04):
    r = random.Random(seed); px, pz = x, z
    for i in range(5):
        nx, nz = px + l / 5, pz + r.uniform(-0.12, 0.12)
        seg(px, pz, nx, nz, w, w * 0.8, y, color, glow=glow)
        if r.random() < 0.3:
            seg(nx, nz, nx + r.uniform(-0.2, 0.2), nz - r.uniform(0.1, 0.25), w * 0.7, 0.01, y, color, glow=glow)
        px, pz = nx, nz


# ------------------------------------------------------------------ cameras
def ortho_cam(name="cam"):
    s = bpy.context.scene
    cd = bpy.data.cameras.new(name); cd.type = "ORTHO"; cd.clip_end = 1000
    c = bpy.data.objects.new(name, cd); s.collection.objects.link(c); s.camera = c
    return c


def key_cam(c, frame, loc, rot=None, scale=None):
    c.location = loc; c.keyframe_insert("location", frame=frame)
    if rot is not None:
        c.rotation_euler = rot; c.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        c.data.ortho_scale = scale; c.data.keyframe_insert("ortho_scale", frame=frame)


def const_keys():
    for ob in list(bpy.data.objects) + list(bpy.data.cameras):
        ad = getattr(ob, "animation_data", None)
        if ad and ad.action:
            for fc in _fcurves(ad.action):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def sprite_lights():
    """Same fixed key/fill as the character kit (key upper-left-front)."""
    s = bpy.context.scene
    sun = bpy.data.lights.new("key", "SUN"); sun.energy = 3.2; sun.angle = math.radians(8)
    so = bpy.data.objects.new("key", sun); s.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(-35), math.radians(-20))
    fill = bpy.data.lights.new("fill", "SUN"); fill.energy = 0.8
    fo = bpy.data.objects.new("fill", fill); s.collection.objects.link(fo)
    fo.rotation_euler = (math.radians(70), math.radians(60), math.radians(30))


def sprite_cam_key(c, frame, cx, cz, ortho, elev=ELEV):
    """Kit-style camera (elevation elev) centred on world point (cx, 0, cz)."""
    e = math.radians(elev)
    key_cam(c, frame, (cx, -30 * math.cos(e), cz + 30 * math.sin(e)), (math.radians(90) - e, 0, 0), ortho)


# ------------------------------------------------------------------ 3D castle parts
STONE = (0.56, 0.52, 0.49); STONE_D = (0.42, 0.38, 0.36); STONE_L = (0.68, 0.64, 0.6)
SLATE = (0.27, 0.27, 0.33); WOOD = (0.4, 0.25, 0.13); WOOD_D = (0.26, 0.16, 0.09)
BRASS = (0.86, 0.64, 0.26); IRON = (0.24, 0.24, 0.27); CRIMSON = (0.55, 0.12, 0.1)
GLOW = (1.0, 0.74, 0.36); EMBER = (1.0, 0.45, 0.1); SMOKE = (0.27, 0.25, 0.28); SMOKE_L = (0.4, 0.37, 0.39)
ASH = (0.3, 0.27, 0.29); ASH_D = (0.2, 0.18, 0.2); BONE = (0.84, 0.78, 0.64); BONE_D = (0.62, 0.56, 0.45)


def flame(x, y, z, h, s=1.0, seed=0):
    r = random.Random(seed)
    cyl(0.22 * s, h, EMBER, (x, y, z + h / 2), r2=0.0, seg=7, glow=1.2, name="flame")
    cyl(0.12 * s, h * 0.6, (1.0, 0.86, 0.45), (x + 0.02, y - 0.12 * s, z + h * 0.3), r2=0.0, seg=7, glow=1.6, name="flame_in")
    for k in range(2):
        dx = r.uniform(-0.18, 0.18) * s
        cyl(0.11 * s, h * 0.55, EMBER, (x + dx, y - 0.05, z + h * 0.27), r2=0.0, seg=6, glow=1.2, name="lick")


def smoke_column(x, y, z, n, s=1.0, seed=0, drift=0.35, color=SMOKE):
    r = random.Random(seed)
    for i in range(n):
        t = i / max(n - 1, 1)
        rr = (0.28 + 0.32 * t) * s * r.uniform(0.85, 1.15)
        ball(rr, color if i % 2 else SMOKE_L, (x + drift * i * s + r.uniform(-0.1, 0.1), y + 0.2, z + i * 0.42 * s), scale=(1.15, 1, 0.9), name="smoke")


def rubble(x, y, z, n, spread, seed=0, colors=(STONE, STONE_D)):
    r = random.Random(seed)
    for i in range(n):
        sz = r.uniform(0.15, 0.4)
        box((sz, sz * r.uniform(0.7, 1.2), sz * r.uniform(0.5, 0.9)), colors[i % len(colors)],
            (x + r.uniform(-spread, spread), y + r.uniform(-0.6, 0.6), z + sz * 0.3),
            rot=(r.uniform(-0.5, 0.5), r.uniform(-0.6, 0.6), r.uniform(0, 3)), bevel=0.04, name="rubble")


def keep(ox, state=0):
    """Lantern Keep, faces +X. Origin = ground centre at (ox, 0, 0). state 0 intact, 1 damaged, 2 ruined.
    Ballista pivot: (ox + 2.3, 0, 4.15) when intact/damaged."""
    r = random.Random(11 + state)
    X = lambda dx: ox + dx
    # mound + plinth
    box((5.0, 3.0, 0.5), STONE_D, (X(0.1), 0, 0.25), bevel=0.08, name="plinth")
    box((4.6, 2.8, 0.25), STONE, (X(0.1), 0, 0.6), bevel=0.05, name="plinth2")
    th = (4.0, 4.0, 2.3)[state]
    base = 0.72
    # round tower (left, back)
    rt_h = (5.0, 4.6, 2.6)[state]
    cyl(0.8, rt_h, STONE_D, (X(-1.75), 0.35, base + rt_h / 2), seg=16, name="rtower")
    for k in range(int(rt_h / 0.9)):
        cyl(0.84, 0.1, STONE_L if k % 2 else STONE, (X(-1.75), 0.35, base + 0.6 + k * 0.9), seg=16, name="band")
    if state < 2:
        cyl(0.95, 0.22, STONE, (X(-1.75), 0.35, base + rt_h + 0.1), seg=16, name="rtcap")
        cyl(0.98, 1.35, SLATE, (X(-1.75), 0.35, base + rt_h + 0.85), r2=0.0, seg=16, name="roof")
        box((0.08, 0.08, 0.7), IRON, (X(-1.75), 0.35, base + rt_h + 1.7), name="spire")
        box((0.5, 0.04, 0.32), CRIMSON, (X(-1.5), 0.35, base + rt_h + 1.85), name="pennant", taper=(0.2, 1))
        if state == 1:
            box((0.5, 0.5, 0.4), (0.12, 0.1, 0.12), (X(-1.45), -0.3, base + rt_h + 0.75), rot=(0.3, 0.2, 0.4), name="roofhole")
    else:
        for i in range(6):
            a = i / 6 * math.tau
            box((0.35, 0.35, r.uniform(0.2, 0.7)), STONE_D, (X(-1.75 + math.cos(a) * 0.6), 0.35 + math.sin(a) * 0.6, base + rt_h), rot=(0, 0, a), name="jag")
    box((0.12, 0.06, 0.5), GLOW, (X(-1.75), -0.47, base + 2.6), glow=1.0, name="slit")
    # main keep block
    if state < 2:
        box((3.0, 2.6, th), STONE, (X(0.3), 0, base + th / 2), taper=(0.95, 0.95), bevel=0.06, name="keep")
    else:
        box((3.0, 2.6, th), STONE, (X(0.3), 0, base + th / 2), taper=(0.95, 0.95), bevel=0.06, name="keep")
        for i in range(7):
            box((0.5, 2.4, r.uniform(0.3, 1.1)), STONE, (X(-0.9 + i * 0.4), 0, base + th + 0.15), rot=(0, r.uniform(-0.2, 0.2), 0), name="jag")
    for k in range(1, int(th / 1.2) + 1):
        box((3.04, 2.64, 0.1), STONE_D, (X(0.3), 0, base + k * 1.2), name="course")
    # quoins on visible corners
    for k in range(int(th / 0.42)):
        for sx in (-1.45, 1.45):
            box((0.32 if k % 2 else 0.22, 0.12, 0.2), STONE_L, (X(0.3 + sx), -1.28, base + 0.2 + k * 0.42), bevel=0.03, name="quoin")
    top = base + th
    if state < 2:
        box((3.3, 2.9, 0.3), STONE_L, (X(0.3), 0, top + 0.12), bevel=0.04, name="parapet")
        missing = {1, 4} if state == 1 else set()
        for i in range(6):
            if i in missing:
                continue
            box((0.36, 0.3, 0.4), STONE, (X(-1.05 + i * 0.54), -1.3, top + 0.47), bevel=0.04, name="merlon")
            box((0.36, 0.3, 0.4), STONE, (X(-1.05 + i * 0.54), 1.3, top + 0.47), bevel=0.04, name="merlon")
        # lantern pedestal + lantern
        lt = 1.0 if state == 0 else 0.55
        box((1.25, 1.25, 0.35), STONE_D, (X(0.3), 0, top + 0.45), bevel=0.04, name="pedestal")
        lz = top + 0.62
        if state == 0:
            box((0.82, 0.82, 1.0), (1.0, 0.66, 0.28), (X(0.3), 0, lz + 0.52), glow=1.2, bevel=0.03, name="lanternglow")
            ball(0.26, (1.0, 0.9, 0.62), (X(0.3), -0.3, lz + 0.48), scale=(1, 0.6, 1.35), glow=2.0, name="lanternflame")
            cyl(0.13, 0.32, (1.0, 0.95, 0.75), (X(0.3), -0.38, lz + 0.72), r2=0.0, seg=8, glow=2.2, name="lanterntip")
        else:
            box((0.82, 0.82, 1.0), (0.95, 0.55, 0.25), (X(0.3), 0, lz + 0.52), glow=1.0, bevel=0.03, name="lanternglow")
            box((0.3, 0.1, 0.4), (0.15, 0.1, 0.1), (X(0.15), -0.42, lz + 0.62), rot=(0, 0.4, 0), name="crackglass")
        for sx in (-0.45, 0.45):
            for sy in (-0.45, 0.45):
                box((0.1, 0.1, 1.1), BRASS, (X(0.3 + sx), sy, lz + 0.52), rot=(0, 0.12 if (state == 1 and sx > 0 and sy < 0) else 0, 0), name="post")
        box((1.0, 1.0, 0.1), BRASS, (X(0.3), 0, lz + 0.02), name="plate")
        box((1.0, 1.0, 0.1), BRASS, (X(0.3), 0, lz + 1.06), name="plate")
        box((0.86, 0.06, 0.06), BRASS, (X(0.3), -0.44, lz + 0.52), name="bar")
        cyl(0.75, 0.48, BRASS, (X(0.3), 0, lz + 1.35), r2=0.12, seg=4, rot=(0, 0, math.radians(45)), name="cap")
        ball(0.12, BRASS, (X(0.3), 0, lz + 1.66), name="finial")
        cyl(0.13, 0.03, BRASS, (X(0.3), 0, lz + 1.86), rot=(math.radians(90), 0, 0), seg=12, name="ring")
    # gate (right side of the front face)
    box((1.2, 0.2, 0.9), STONE_L, (X(1.0), -1.28, base + 0.65), bevel=0.04, name="gateframe")
    cyl(0.62, 0.2, STONE_L, (X(1.0), -1.28, base + 1.1), rot=(math.radians(90), 0, 0), seg=16, name="arch")
    box((0.95, 0.2, 0.8), WOOD_D, (X(1.0), -1.34, base + 0.5), bevel=0.02, name="door")
    cyl(0.48, 0.2, WOOD_D, (X(1.0), -1.34, base + 0.95), rot=(math.radians(90), 0, 0), seg=16, name="doorarch")
    for dz in (0.3, 0.75):
        box((0.98, 0.06, 0.07), IRON, (X(1.0), -1.46, base + dz), name="strap")
    # arrow slits / windows
    for wx, wz in ((-0.5, 1.9), (0.35, 2.9), (1.0, 2.05), (-0.5, 3.1)):
        if wz < th - 0.3:
            box((0.13, 0.08, 0.48), GLOW if state == 0 else (0.9, 0.5, 0.2), (X(wx), -1.3, base + wz), glow=1.0, name="window")
    # banner with lantern emblem
    if state < 2:
        bl = 1.5 if state == 0 else 0.9
        box((0.62, 0.05, bl), CRIMSON, (X(-0.45), -1.36, top - bl / 2 - 0.05), taper=(0.7, 1) if state == 0 else (1.2, 1), name="banner")
        box((0.2, 0.03, 0.26), BRASS, (X(-0.45), -1.4, top - 0.55), name="emblem")
        box((0.75, 0.08, 0.08), WOOD_D, (X(-0.45), -1.36, top - 0.02), name="bannerrod")
    # ballista platform (right)
    if state < 2:
        pz = 3.7
        box((1.5, 1.8, 0.18), WOOD, (X(2.3), 0, pz), bevel=0.03, name="deck")
        for sy in (-0.7, 0.7):
            box((0.12, 0.12, 1.2), WOOD_D, (X(2.25), sy, pz - 0.55), rot=(0, math.radians(-38), 0), name="brace")
        for px in (1.75, 2.95):
            box((0.08, 0.08, 0.45), WOOD_D, (X(px), -0.85, pz + 0.3), name="rail")
        box((1.3, 0.06, 0.07), WOOD_D, (X(2.35), -0.85, pz + 0.48), name="railbar")
        cyl(0.2, 0.3, IRON, (X(2.3), 0, pz + 0.25), seg=10, name="mount")
        cyl(0.13, 0.12, BRASS, (X(2.3), 0, pz + 0.42), seg=10, name="mounttop")
    else:
        box((1.4, 1.6, 0.15), WOOD, (X(2.2), 0, 0.45), rot=(0, math.radians(25), 0), name="deckfallen")
        box((0.12, 0.12, 1.1), WOOD_D, (X(2.6), -0.4, 0.5), rot=(0, math.radians(70), 0.3), name="beam")
    # damage
    if state == 1:
        for (cx, cz, a, l) in ((-0.6, 2.5, 0.5, 0.9), (0.9, 3.3, -0.4, 0.8), (0.0, 1.4, 0.2, 0.7), (-1.75, 3.5, 0.3, 0.8)):
            yy = -1.31 if cx > -1.5 else -0.47
            box((0.05, 0.04, l), (0.12, 0.09, 0.09), (X(cx), yy, base + cz), rot=(0, a, 0), name="crackd")
            box((0.04, 0.04, l * 0.6), (0.12, 0.09, 0.09), (X(cx + 0.15), yy, base + cz - l * 0.35), rot=(0, -a, 0), name="crackd")
        for (cx, cz, s) in ((0.9, 3.7, 0.8), (-0.9, 1.0, 0.6)):
            box((s, 0.04, s * 0.7), (0.28, 0.24, 0.24), (X(cx), -1.3, base + cz), rot=(0, 0.3, 0), name="scorch")
        flame(X(1.1), -1.0, top + 0.25, 0.75, 0.9, seed=1)
        smoke_column(X(1.1), 0.2, top + 1.0, 5, 0.9, seed=2)
        smoke_column(X(-1.5), 0.6, base + rt_h + 1.6, 4, 0.7, seed=3, drift=0.25)
        rubble(X(1.8), -0.3, 0.5, 8, 0.6, seed=5)
    if state == 2:
        flame(X(0.0), -1.0, top + 0.1, 1.1, 1.2, seed=1); flame(X(1.1), -0.9, top + 0.25, 0.8, 1.0, seed=4)
        flame(X(-1.7), -0.3, base + rt_h + 0.1, 0.9, 1.0, seed=6); flame(X(2.2), -0.9, 0.6, 0.6, 0.8, seed=7)
        smoke_column(X(0.0), 0.3, top + 1.3, 7, 1.1, seed=2)
        smoke_column(X(-1.7), 0.6, base + rt_h + 1.2, 5, 0.9, seed=3, drift=0.25)
        rubble(X(0.3), -0.8, 0.55, 18, 1.9, seed=5); rubble(X(2.4), -0.5, 0.0, 10, 0.7, seed=8)
        # fallen lantern
        box((0.75, 0.75, 0.9), (0.9, 0.5, 0.22), (X(2.75), -0.4, 0.45), glow=0.8, rot=(0, math.radians(70), 0.2), name="lanternfallen")
        cyl(0.62, 0.4, BRASS, (X(3.25), -0.4, 0.35), r2=0.1, seg=4, rot=(0, math.radians(100), 0.6), name="capfallen")
        for k in range(4):
            box((0.09, 0.09, 1.0), BRASS, (X(2.7 + r.uniform(-0.2, 0.2)), -0.6 + k * 0.3, 0.2), rot=(0, math.radians(85), r.uniform(-0.4, 0.4)), name="postfallen")
        for i in range(4):
            box((0.1, 0.05, 0.7), (0.1, 0.08, 0.08), (X(-0.6 + i * 0.5), -1.31, base + 1.0 + r.uniform(0, 0.8)), rot=(0, r.uniform(-0.6, 0.6), 0), name="crack")


def ballista(ox, oz):
    """Ballista arm pointing +X with its pivot at (ox, 0, oz)."""
    X = lambda dx: ox + dx
    box((2.1, 0.26, 0.2), WOOD, (X(0.55), 0, oz + 0.05), bevel=0.03, name="stock")
    box((1.7, 0.08, 0.06), WOOD_D, (X(0.75), -0.14, oz + 0.12), name="groove")
    for sz in (1, -1):
        box((0.14, 0.18, 0.95), WOOD, (X(1.35), 0, oz + 0.05 + sz * 0.5), rot=(0, math.radians(-20 * sz), 0), bevel=0.03, name="limb")
        box((0.18, 0.2, 0.12), BRASS, (X(1.5), 0, oz + 0.05 + sz * 0.95), name="tip")
        box((0.025, 0.025, 1.25), (0.15, 0.12, 0.1), (X(0.75), -0.03, oz + 0.05 + sz * 0.5), rot=(0, math.radians(-62 * sz), 0), bevel=0.0, name="string")
    box((0.3, 0.3, 0.3), BRASS, (X(1.42), 0, oz + 0.05), bevel=0.04, name="bowhub")
    for dx in (0.2, 0.95):
        box((0.08, 0.3, 0.26), BRASS, (X(dx), 0, oz + 0.05), name="band")
    cyl(0.25, 0.34, IRON, (X(0.0), 0, oz), rot=(math.radians(90), 0, 0), seg=14, name="pivot")
    cyl(0.12, 0.38, BRASS, (X(0.0), 0, oz), rot=(math.radians(90), 0, 0), seg=10, name="pivotcap")
    cyl(0.22, 0.12, WOOD_D, (X(-0.35), -0.2, oz + 0.05), rot=(math.radians(90), 0, 0), seg=8, name="winch")
    box((0.06, 0.06, 0.4), IRON, (X(-0.35), -0.28, oz + 0.05), name="spoke")
    box((0.4, 0.06, 0.06), IRON, (X(-0.35), -0.28, oz + 0.05), name="spoke")


def maw(ox, state=0):
    """Maw Gate, faces -X. Origin = ground centre (ox, 0, 0)."""
    r = random.Random(21 + state)
    X = lambda dx: ox + dx
    box((5.6, 3.0, 0.5), ASH_D, (X(0), 0, 0.25), bevel=0.08, name="plinth")
    lh = (4.4, 4.0, 2.0)[state]; rh = (5.4, 4.9, 2.6)[state]
    # towers
    box((1.6, 2.4, lh), ASH, (X(-1.95), 0, 0.5 + lh / 2), taper=(0.8, 0.85), bevel=0.06, name="ltower")
    box((1.8, 2.5, rh), ASH, (X(1.95), 0.1, 0.5 + rh / 2), taper=(0.75, 0.85), bevel=0.06, name="rtower")
    for tx, hh, w in ((-1.95, lh, 1.6), (1.95, rh, 1.8)):
        for k in range(1, int(hh / 1.1) + 1):
            f = 1 - 0.22 * (k * 1.1 / hh)
            box((w * f + 0.06, 0.1, 0.14), IRON, (X(tx), -1.22, 0.5 + k * 1.1), name="ironband")
        # rib bones across the tower face
        for k in range(3 if hh > 3 else 1):
            box((w * 0.7, 0.12, 0.1), BONE_D if k % 2 else BONE, (X(tx), -1.27, 1.2 + k * 0.45), rot=(0, 0.12 * (1 if tx > 0 else -1), 0), name="rib")
    # back wall + glowing throat
    wall_h = (4.2, 4.0, 1.8)[state]
    box((2.6, 1.8, wall_h), ASH_D, (X(0), 0.4, 0.5 + wall_h / 2), name="wall")
    glow_c = EMBER if state < 2 else (0.95, 0.38, 0.1)
    if state < 2:
        box((2.0, 0.1, 2.5), glow_c, (X(0), -0.55, 0.5 + 1.3), glow=1.6 if state == 0 else 1.1, name="throat")
        box((1.2, 0.08, 1.5), (1.0, 0.85, 0.45), (X(0), -0.6, 0.5 + 1.0), glow=1.8, name="throatcore")
        # upper jaw
        box((3.0, 0.7, 0.55), BONE, (X(0), -0.85, 3.25 - (0.2 if state == 1 else 0)), bevel=0.08, rot=(0, 0.06 if state == 1 else 0, 0), name="upperjaw")
        jz = 3.0 - (0.2 if state == 1 else 0)
        for i, fx in enumerate((-1.1, -0.65, -0.2, 0.25, 0.7, 1.1)):
            l = (0.85, 0.6, 1.0, 0.75, 0.95, 0.6)[i]
            if state == 1 and i in (1, 4):
                l *= 0.35
            cyl(0.17, l, BONE, (X(fx), -0.95, jz - l / 2), r2=0.02, seg=8, rot=(math.radians(180), 0, 0), name="fang")
        # lower jaw
        box((3.0, 0.7, 0.4), BONE_D, (X(0), -0.85, 0.7), bevel=0.06, name="lowerjaw")
        for i, fx in enumerate((-0.9, -0.3, 0.3, 0.9)):
            l = (0.55, 0.7, 0.65, 0.5)[i] * (0.4 if state == 1 and i == 2 else 1)
            cyl(0.15, l, BONE, (X(fx), -0.95, 0.9 + l / 2), r2=0.02, seg=8, name="fang")
        # brow + eyes
        box((2.8, 0.5, 0.35), IRON, (X(0), -0.75, 3.75), rot=(0, 0, 0), bevel=0.05, name="brow")
        for sx in (-1, 1):
            box((0.55, 0.1, 0.2), (1.0, 0.55, 0.15), (X(sx * 0.6), -0.95, 3.75 + 0.35), rot=(0, math.radians(-14 * sx), 0), glow=2.0, name="eye")
            box((0.7, 0.3, 0.12), IRON, (X(sx * 0.6), -0.9, 3.75 + 0.55), rot=(0, math.radians(-14 * sx), 0), name="lid")
        # skull crest + horns
        ball(0.5, BONE, (X(0), -0.4, 4.7), scale=(1, 0.9, 0.9), name="skull")
        for sx in (-0.2, 0.2):
            ball(0.12, (0.08, 0.04, 0.04), (X(sx), -0.85, 4.75), name="socket")
            ball(0.06, EMBER, (X(sx), -0.93, 4.75), glow=2.0, name="spark")
        box((0.5, 0.25, 0.25), BONE_D, (X(0), -0.45, 4.25), name="skulljaw")
        for sx in (-1, 1):
            cyl(0.14, 1.1, BONE, (X(sx * 0.65), -0.35, 5.1), r2=0.0, seg=8, rot=(0, math.radians(-35 * sx), 0), name="horn")
        # chains
        for sx in (-1, 1):
            for k in range(5):
                box((0.1, 0.05, 0.16), IRON, (X(sx * (1.05 + k * 0.03)), -1.2, 2.9 - k * 0.2), rot=(0, 0, (k % 2) * 1.57), name="chain")
    else:
        box((2.0, 0.1, 1.2), glow_c, (X(0), -0.55, 0.9), glow=1.3, name="throat")
        box((3.0, 0.7, 0.5), BONE, (X(-0.4), -0.7, 0.55), rot=(0, math.radians(14), 0.2), bevel=0.08, name="jawfallen")
        for i in range(6):
            cyl(0.15, r.uniform(0.4, 0.9), BONE, (X(r.uniform(-2.2, 2.4)), r.uniform(-1.3, -0.6), 0.6), r2=0.02, seg=8,
                rot=(r.uniform(1.2, 1.9), 0, r.uniform(0, 3)), name="fangfallen")
        ball(0.5, BONE, (X(1.4), -0.9, 0.85), scale=(1, 0.9, 0.9), name="skullfallen")
        flame(X(0), -0.8, 1.0, 1.2, 1.2, seed=3); flame(X(-1.9), -0.6, 0.5 + lh, 0.8, 1.0, seed=5); flame(X(1.9), -0.6, 0.5 + rh, 0.9, 1.0, seed=8)
        smoke_column(X(0), 0.3, 2.4, 7, 1.1, seed=2, drift=-0.3)
        rubble(X(0), -0.6, 0.5, 18, 2.4, seed=4, colors=(ASH, ASH_D, BONE_D))
    # spikes on tower tops + tusks
    for tx, hh, w in ((-1.95, lh, 1.6), (1.95, rh, 1.8)):
        topw = w * (0.8 if tx < 0 else 0.75)
        if state < 2:
            for k in range(4):
                sx = -topw / 2 + 0.15 + k * (topw - 0.3) / 3
                if state == 1 and k == (1 if tx < 0 else 2):
                    continue
                cyl(0.13, 0.6 + 0.2 * (k % 2), IRON, (X(tx + sx), -0.8, 0.5 + hh + 0.3), r2=0.0, seg=6, name="spike")
                cyl(0.13, 0.6, IRON, (X(tx + sx), 0.8, 0.5 + hh + 0.3), r2=0.0, seg=6, name="spike")
            box((topw + 0.2, 2.3, 0.22), IRON, (X(tx), 0, 0.5 + hh), name="towercap")
            # ember slit
            box((0.14, 0.08, 0.55), (1.0, 0.5, 0.12), (X(tx), -1.23, 0.5 + hh * 0.72), glow=1.8, name="slit")
        else:
            for i in range(5):
                box((0.4, 2.0, r.uniform(0.2, 0.7)), ASH, (X(tx - w / 2 + 0.3 + i * (w - 0.5) / 4), 0, 0.5 + hh), rot=(0, r.uniform(-0.3, 0.3), 0), name="jag")
    # big tusks (left tower leans its tusk toward the enemy, facing -X)
    if state < 2:
        cyl(0.26, 1.8, BONE, (X(-2.9), -0.9, 2.2), r2=0.03, seg=10, rot=(0, math.radians(-50), 0), name="tusk")
        cyl(0.24, 1.4 if state == 0 else 0.6, BONE, (X(2.9), -0.9, 2.6), r2=0.03, seg=10, rot=(0, math.radians(40), 0), name="tusk")
        cyl(0.18, 1.3, BONE_D, (X(-2.6), -0.9, 4.1), r2=0.02, seg=8, rot=(0, math.radians(-60), 0), name="tusk2")
    if state == 1:
        for (cx, cz, a) in ((-1.9, 2.7, 0.4), (1.9, 3.6, -0.3), (2.1, 1.6, 0.6)):
            box((0.06, 0.05, 0.9), EMBER, (X(cx), -1.24, cz), rot=(0, a, 0), glow=1.5, name="crack")
            box((0.05, 0.05, 0.5), EMBER, (X(cx + 0.15), -1.24, cz - 0.4), rot=(0, -a, 0), glow=1.5, name="crack")
        flame(X(1.7), -0.9, 0.5 + rh + 0.1, 0.7, 0.9, seed=2)
        smoke_column(X(1.7), 0.2, 0.5 + rh + 1.0, 5, 0.9, seed=4, drift=-0.3)
        rubble(X(-2.6), -0.6, 0.5, 8, 0.6, seed=6, colors=(ASH, ASH_D, BONE_D))
