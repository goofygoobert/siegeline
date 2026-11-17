# Siegeline scenery library (Tales of the Brine; earlier Ashen Marches helpers kept) — bundled after kit.py:
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


# ================================================================== Tales of the Brine: coastal painted props
def gull(x, z, s, y, color, flap=0.0):
    """Tiny gull 'v' silhouette."""
    k = 0.35 + flap
    poly([(x - s, z + s * k), (x - s * 0.45, z + s * 0.15), (x, z), (x + s * 0.45, z + s * 0.15), (x + s, z + s * k),
          (x + s * 0.4, z + s * 0.3), (x, z + s * 0.12), (x - s * 0.4, z + s * 0.3)], y, color)


def glowdot(x, z, r, y, color, alpha=0.7, core=None, glow=0.8, p=2.0):
    """Soft radial glow (lantern, wisp) with an optional solid core."""
    ellipse(x, z, r, r, y, color, n=32, alpha=alpha, radial=p)
    if core:
        ellipse(x, z, r * 0.16, r * 0.16, y - 0.05, core, n=12, glow=glow)


def lighthouse(x, z, h, y, color, lit, lamp, stripe=None, beam=None, beam_a=0.25, beam_dir=1):
    """Tapered lighthouse tower, gallery, lamp room, cap; optional stripes and a light beam."""
    w0, w1 = h * 0.16, h * 0.095
    poly([(x - w0, z - 0.4), (x - w1, z + h), (x + w1, z + h), (x + w0, z - 0.4)], y, color)
    poly([(x + w0 * 0.25, z - 0.4), (x + w1 * 0.25, z + h), (x + w1, z + h), (x + w0, z - 0.4)], y - 0.01, lit)
    if stripe:
        for k in (0.3, 0.62):
            za, zb = z + h * k, z + h * (k + 0.12)
            fa, fb = w0 + (w1 - w0) * k, w0 + (w1 - w0) * (k + 0.12)
            poly([(x - fa, za), (x - fb, zb), (x + fb, zb), (x + fa, za)], y - 0.02, stripe)
    rect(x - w1 * 1.5, z + h, x + w1 * 1.5, z + h + h * 0.035, y - 0.03, color)
    rect(x - w1 * 0.8, z + h + h * 0.035, x + w1 * 0.8, z + h * 1.14, y - 0.03, lamp, glow=1.2)
    for k in (-0.4, 0.3):
        rect(x + w1 * k, z + h + h * 0.035, x + w1 * (k + 0.12), z + h * 1.14, y - 0.04, color)
    poly([(x - w1 * 1.05, z + h * 1.14), (x, z + h * 1.26), (x + w1 * 1.05, z + h * 1.14)], y - 0.03, color)
    if beam:
        lz = z + h * 1.09
        for k, f in enumerate((1.0, 0.75, 0.5, 0.3)):
            seg(x, lz, x + beam_dir * h * 3.4 * f, lz + h * 0.1 * f, 0.06, h * 0.5 * f, y + 0.5 + k * 0.01, beam, alpha=beam_a * 0.4)
        glowdot(x, lz, h * 0.45, y + 0.4, beam, alpha=0.55)


def ship_sil(x, z, s, y, color, sail=None, seed=0, flag=None, masts=3, wreck=False):
    """Three-masted ship silhouette facing right. z = waterline. sail: optional lighter sail colour."""
    r = random.Random(seed)
    L = 3.2 * s
    hull = [(x - L * 0.5, z + 0.75 * s), (x - L * 0.47, z + 0.15 * s), (x - L * 0.3, z - 0.18 * s), (x + L * 0.3, z - 0.18 * s),
            (x + L * 0.48, z + 0.25 * s), (x + L * 0.55, z + 0.55 * s), (x + L * 0.4, z + 0.45 * s), (x - L * 0.25, z + 0.42 * s),
            (x - L * 0.32, z + 0.75 * s)]
    poly(hull, y, color)
    seg(x + L * 0.48, z + 0.5 * s, x + L * 0.78, z + 0.85 * s, 0.07 * s, 0.03 * s, y, color)   # bowsprit
    mx = [x - L * 0.28, x + 0.02 * L, x + L * 0.3][:masts]
    hs = [1.9, 2.5, 2.0][:masts]
    for i, (m, hh) in enumerate(zip(mx, hs)):
        top = z + hh * s
        if wreck and i == 1:
            top = z + hh * s * 0.55
        seg(m, z + 0.3 * s, m + (0.25 * s if wreck and i == 1 else 0), top, 0.08 * s, 0.05 * s, y, color)
        if wreck and i == 1:
            continue
        for k, (zz, ww) in enumerate(((0.95, 0.55), (1.55, 0.45))):
            if z + (zz + 0.45) * s > top:
                continue
            sc = sail or color
            bl = 0.12 * s
            pts = [(m - ww * s, z + (zz + 0.5) * s), (m + ww * s, z + (zz + 0.5) * s), (m + ww * s + bl, z + (zz) * s),
                   (m, z + (zz - 0.08) * s), (m - ww * s + bl, z + zz * s)]
            if wreck and r.random() < 0.5:
                pts = pts[:3] + [(m + 0.1 * s, z + (zz + 0.2) * s)]
            poly(pts, y - 0.01, sc)
        if flag and i == 1:
            poly([(m, top), (m + 0.45 * s, top - 0.08 * s), (m, top - 0.2 * s)], y - 0.01, flag)
    # rigging lines
    seg(mx[0], z + hs[0] * s, x - L * 0.5, z + 0.75 * s, 0.025 * s, 0.025 * s, y, color)
    seg(mx[-1], z + hs[-1] * s, x + L * 0.75, z + 0.83 * s, 0.025 * s, 0.025 * s, y, color)


def jetty(x0, x1, z, y, color, plank=None, seed=0, depth=1.6, broken=True):
    """Rickety jetty: plank deck at height z on uneven stilts, a sag and a broken end."""
    r = random.Random(seed); x = x0
    while x < x1:
        dz = r.uniform(-0.06, 0.06); lean = r.uniform(-0.12, 0.12)
        seg(x, z - depth, x + lean, z + 0.25 + r.uniform(0, 0.25), 0.11, 0.09, y, color)
        if r.random() < 0.5:
            seg(x, z - 0.9, x + 1.0, z - 0.15, 0.05, 0.05, y, color)    # cross brace
        x += r.uniform(0.85, 1.15)
    n = int((x1 - x0) / 0.3); prev = None
    for i in range(n):
        xa = x0 - 0.1 + i * (x1 - x0 + 0.2) / n; xb = xa + (x1 - x0) / n * 0.92
        if broken and i > n - 4 and r.random() < 0.6:
            continue
        sag = -0.08 * math.sin(math.pi * i / n) + r.uniform(-0.03, 0.03)
        poly([(xa, z + sag), (xb, z + sag), (xb, z + sag + 0.12), (xa, z + sag + 0.12)], y - 0.01, plank or color)
    seg(x0 - 0.1, z + 0.1, x1, z + 0.06, 0.04, 0.04, y - 0.02, color)


def hull_wreck(x, z, s, y, color, lit=None, seed=0, flip=False):
    """Beached wrecked hull: keel, broken plank side, ribs sticking up, snapped mast."""
    r = random.Random(seed); f = -1 if flip else 1
    L = 3.4 * s
    X = lambda dx: x + f * dx
    side = [(X(-L * 0.5), z), (X(-L * 0.42), z + 0.75 * s), (X(-L * 0.1), z + 0.9 * s), (X(L * 0.05), z + 0.55 * s),
            (X(L * 0.15), z + 0.8 * s), (X(L * 0.28), z + 0.4 * s), (X(L * 0.5), z + 0.15 * s), (X(L * 0.52), z)]
    poly(side, y, color)
    for k in range(9):
        t = k / 8; bx = X(-L * 0.45 + t * L * 0.9)
        hh = (0.9 + 1.0 * math.sin(math.pi * (0.2 + 0.7 * t))) * s * r.uniform(0.75, 1.15)
        if r.random() < 0.2:
            hh *= 0.5
        lean = f * (0.15 + 0.2 * t) * s
        seg(bx, z + 0.3 * s, bx + lean * 0.5, z + hh * 0.7, 0.13 * s, 0.1 * s, y + 0.01, color)
        seg(bx + lean * 0.5, z + hh * 0.7, bx + lean, z + hh, 0.1 * s, 0.05 * s, y + 0.01, color)
    for k in range(3):
        zz = z + (0.25 + 0.2 * k) * s
        seg(X(-L * 0.47), zz, X(L * (0.1 - 0.12 * k)), zz + 0.06 * s, 0.07 * s, 0.07 * s, y - 0.01, lit or color)
    seg(X(-L * 0.05), z + 0.6 * s, X(L * 0.12), z + 2.7 * s, 0.16 * s, 0.11 * s, y + 0.02, color)   # snapped mast
    poly([(X(L * 0.12) - 0.08 * s, z + 2.7 * s), (X(L * 0.14), z + 3.0 * s), (X(L * 0.12) + 0.09 * s, z + 2.65 * s)], y + 0.02, color)
    seg(X(L * 0.0), z + 2.0 * s, X(L * 0.42), z + 1.75 * s, 0.07 * s, 0.05 * s, y + 0.02, color)  # yard hanging
    seg(X(L * 0.12), z + 2.6 * s, X(L * 0.55), z + 0.1 * s, 0.025, 0.025, y + 0.02, color)


def net(x0, z0, x1, z1, sag, y, color, n=7, m=5, drop=0.8, alpha=0.9):
    """Fishing net hanging between two points, sagging, with a ragged drop below."""
    def P(u, v):
        xx = x0 + (x1 - x0) * u; zz = z0 + (z1 - z0) * u - sag * math.sin(math.pi * u)
        return xx, zz - v * drop * (0.6 + 0.4 * math.sin(math.pi * u))
    for i in range(n + 1):
        u = i / n; a = P(u, 0); b = P(u + 0.03 * ((i % 2) * 2 - 1), 1)
        seg(a[0], a[1], b[0], b[1], 0.025, 0.02, y, color, alpha=alpha)
    for j in range(m + 1):
        v = j / m; pts = [P(i / 12, v) for i in range(13)]
        for a, b in zip(pts, pts[1:]):
            seg(a[0], a[1], b[0], b[1], 0.03 if j == 0 else 0.02, 0.02, y, color, alpha=alpha)
    for k in range(3):   # floats
        u = (k + 0.5) / 3; px, pz = P(u, 0)
        ellipse(px, pz - 0.02, 0.07, 0.06, y - 0.01, color, n=10)


def lantern_post(x, z, h, y, color, glowc, core=(1.0, 0.9, 0.6), r=0.75, arm=1, alpha=0.6):
    """Post with a hooked arm and a hanging lantern + glow."""
    seg(x, z - 0.3, x, z + h, 0.1, 0.08, y, color)
    seg(x, z + h - 0.05, x + arm * 0.45, z + h + 0.05, 0.05, 0.05, y, color)
    lx, lz = x + arm * 0.45, z + h - 0.35
    seg(lx, z + h + 0.05, lx, lz + 0.15, 0.02, 0.02, y, color)
    glowdot(lx, lz, r, y + 0.3, glowc, alpha=alpha)
    rect(lx - 0.09, lz - 0.12, lx + 0.09, lz + 0.12, y - 0.01, core, glow=1.0)
    poly([(lx - 0.12, lz + 0.12), (lx, lz + 0.24), (lx + 0.12, lz + 0.12)], y - 0.02, color)
    rect(lx - 0.11, lz - 0.16, lx + 0.11, lz - 0.11, y - 0.02, color)


def stilt_hut(x, z, s, y, color, lit, win, seed=0):
    """Fisher's shack on stilts, sagging roof, lit window."""
    r = random.Random(seed)
    for dx in (-0.8, -0.25, 0.3, 0.85):
        seg(x + dx * s, z - 1.2 * s, x + dx * s + r.uniform(-0.08, 0.08), z + 0.1, 0.09 * s, 0.08 * s, y, color)
    poly([(x - 1.0 * s, z), (x + 1.0 * s, z), (x + 0.95 * s, z + 1.1 * s), (x - 0.95 * s, z + 1.05 * s)], y, color)
    poly([(x - 1.25 * s, z + 1.0 * s), (x - 0.1 * s, z + 1.75 * s), (x + 0.2 * s, z + 1.6 * s), (x + 1.25 * s, z + 1.05 * s),
          (x + 1.1 * s, z + 0.95 * s), (x - 1.1 * s, z + 0.92 * s)], y - 0.01, color)
    poly([(x + 0.2 * s, z + 1.6 * s), (x + 1.25 * s, z + 1.05 * s), (x + 1.1 * s, z + 0.95 * s), (x + 0.15 * s, z + 1.45 * s)], y - 0.02, lit)
    rect(x + 0.25 * s, z + 0.4 * s, x + 0.6 * s, z + 0.75 * s, y - 0.02, win, glow=0.6)
    seg(x + 0.425 * s, z + 0.4 * s, x + 0.425 * s, z + 0.75 * s, 0.03, 0.03, y - 0.03, color)
    seg(x - 0.4 * s, z + 1.4 * s, x - 0.4 * s, z + 2.0 * s, 0.1 * s, 0.09 * s, y + 0.01, color)   # stovepipe
    rect(x - 1.1 * s, z - 0.08 * s, x + 1.4 * s, z + 0.02, y - 0.01, color)   # porch


def sea_ribs(x, z, s, y, color, lit=None, n=6, seed=0, skull=True):
    """Bones of a huge sea creature: spine with arching ribs, a long skull at the right."""
    r = random.Random(seed)
    L = 1.1 * n * s
    for k in range(n + 2):
        vx = x + k * L / (n + 1)
        ellipse(vx, z + 0.12 * s, 0.16 * s, 0.12 * s, y, color, n=10)
    for k in range(n):
        bx = x + (k + 1) * L / (n + 1); hh = (2.2 - 0.12 * abs(k - n * 0.4)) * s * r.uniform(0.85, 1.05)
        if k == n - 2:
            hh *= 0.5
        pts = []
        for i in range(9):
            t = i / 8; pts.append((bx + math.sin(t * 2.6) * 0.65 * s * (1 - 0.3 * t), z + 0.1 + hh * math.sin(t * 1.5)))
        for (a, b), i in zip(zip(pts, pts[1:]), range(8)):
            w = 0.16 * s * (1 - i / 10)
            seg(a[0], a[1], b[0], b[1], w, w * 0.92, y, color)
            if lit and i < 6:
                seg(a[0] + 0.03 * s, a[1] + 0.03 * s, b[0] + 0.03 * s, b[1] + 0.03 * s, w * 0.35, w * 0.3, y - 0.01, lit)
    if skull:
        sx = x + L + 0.4 * s
        poly([(sx - 0.4 * s, z), (sx - 0.5 * s, z + 0.55 * s), (sx + 0.2 * s, z + 0.7 * s), (sx + 1.6 * s, z + 0.3 * s),
              (sx + 1.7 * s, z + 0.12 * s), (sx + 0.5 * s, z + 0.15 * s), (sx + 1.5 * s, z), ], y, color)
        ellipse(sx + 0.05 * s, z + 0.42 * s, 0.13 * s, 0.1 * s, y - 0.01, lit or (0, 0, 0), n=10)


def crate(x, z, s, y, color, lit, dark, rot=0.0):
    c, sn = math.cos(rot), math.sin(rot)
    R = lambda px, pz: (x + px * c - pz * sn, z + px * sn + pz * c)
    poly([R(-s, 0), R(s, 0), R(s, 2 * s), R(-s, 2 * s)], y, color)
    poly([R(s * 0.6, 0), R(s, 0), R(s, 2 * s), R(s * 0.6, 2 * s)], y - 0.01, lit)
    for a, b in (((-s, 0.1 * s), (s, 1.9 * s)), ((-s, 1.0 * s), (s, 1.0 * s))):
        p, q = R(*a), R(*b); seg(p[0], p[1], q[0], q[1], 0.12 * s, 0.12 * s, y - 0.02, dark)


def barrel(x, z, s, y, color, lit, hoop, lying=False):
    if lying:
        ellipse(x, z + 0.7 * s, 1.1 * s, 0.7 * s, y, color, n=20)
        ellipse(x + 0.95 * s, z + 0.7 * s, 0.3 * s, 0.62 * s, y - 0.01, lit, n=16)
        for dx in (-0.55, 0.45):
            seg(x + dx * s, z + 0.05 * s, x + dx * s, z + 1.35 * s, 0.1 * s, 0.1 * s, y - 0.02, hoop)
        return
    poly([(x - 0.6 * s, z), (x - 0.72 * s, z + 0.8 * s), (x - 0.6 * s, z + 1.6 * s), (x + 0.6 * s, z + 1.6 * s),
          (x + 0.72 * s, z + 0.8 * s), (x + 0.6 * s, z)], y, color)
    poly([(x + 0.25 * s, z), (x + 0.32 * s, z + 0.8 * s), (x + 0.25 * s, z + 1.6 * s), (x + 0.6 * s, z + 1.6 * s),
          (x + 0.72 * s, z + 0.8 * s), (x + 0.6 * s, z)], y - 0.01, lit)
    for zz in (0.3, 1.3):
        seg(x - 0.68 * s, z + zz * s, x + 0.68 * s, z + zz * s, 0.1 * s, 0.1 * s, y - 0.02, hoop)


def rope_coil(x, z, s, y, color, lit):
    for k in range(3):
        ellipse(x, z + 0.12 * s + k * 0.1 * s, (0.6 - 0.1 * k) * s, 0.16 * s, y - k * 0.01, color if k % 2 else lit, n=18)
    seg(x + 0.5 * s, z + 0.12 * s, x + 1.4 * s, z + 0.02, 0.07 * s, 0.07 * s, y + 0.01, color)


def anchor_sil(x, z, s, y, color, lean=0.3):
    c, sn = math.cos(lean), math.sin(lean)
    R = lambda px, pz: (x + px * c + pz * sn, z - px * sn + pz * c)
    a, b = R(0, -0.2 * s), R(0, 2.0 * s); seg(a[0], a[1], b[0], b[1], 0.14 * s, 0.12 * s, y, color)
    a, b = R(-0.45 * s, 1.75 * s), R(0.45 * s, 1.75 * s); seg(a[0], a[1], b[0], b[1], 0.1 * s, 0.1 * s, y, color)
    ring = R(0, 2.15 * s); ellipse(ring[0], ring[1], 0.15 * s, 0.15 * s, y, color, n=12)
    pts = [R(-0.85 * s * math.cos(t), 0.55 * s - 0.6 * s * math.sin(t) + 0.2 * s) for t in [i / 8 * math.pi for i in range(9)]]
    for p, q in zip(pts, pts[1:]):
        seg(p[0], p[1], q[0], q[1], 0.13 * s, 0.13 * s, y, color)
    for side in (-1, 1):
        a = R(side * 0.85 * s, 0.75 * s); poly([(a[0] - 0.12 * s, a[1]), (a[0] + side * 0.08 * s, a[1] + 0.3 * s), (a[0] + 0.12 * s, a[1])], y, color)


def driftwood(x, z, l, y, color, seed=0):
    r = random.Random(seed); a = r.uniform(-0.15, 0.15)
    seg(x, z, x + l * math.cos(a), z + l * math.sin(a), 0.14, 0.08, y, color)
    seg(x + l * 0.6, z + l * 0.6 * math.sin(a), x + l * 0.75, z + 0.35, 0.06, 0.03, y, color)


def wisp(x, z, s, y, color, core=(0.85, 1.0, 0.85), alpha=0.55):
    """Ghost light hovering over water: big soft halo, small bright core, faint reflection streak below."""
    glowdot(x, z, s, y, color, alpha=alpha, core=core, glow=1.6)
    ellipse(x, z - s * 0.9, s * 0.5, s * 0.06, y + 0.05, color, n=16, alpha=alpha * 0.6)


def wave_lines(x0, x1, z0, z1, y, n, color, alpha=0.5, seed=0, lmin=0.3, lmax=1.4, th=0.03):
    """Horizontal glints on water, thinner/shorter towards the horizon (z1)."""
    r = random.Random(seed)
    for i in range(n):
        t = r.random() ** 1.6; zz = z1 - (z1 - z0) * t
        k = 0.35 + 0.65 * t; l = r.uniform(lmin, lmax) * k; xx = r.uniform(x0, x1)
        ellipse(xx, zz, l, th * (0.5 + k), y, color, n=12, alpha=alpha * r.uniform(0.5, 1.0))


# ================================================================== Tales of the Brine: 3D castles
HULL = (0.47, 0.3, 0.17); HULL_D = (0.31, 0.19, 0.12); HULL_L = (0.62, 0.43, 0.26); NAVY = (0.13, 0.24, 0.37)
SEARED = (0.7, 0.2, 0.16); CANVAS = (0.92, 0.87, 0.76); CANVAS_D = (0.76, 0.7, 0.58); TAR = (0.17, 0.15, 0.14)
ROCKC = (0.36, 0.38, 0.4); ROCK_D = (0.25, 0.27, 0.3); BARN = (0.86, 0.83, 0.74); WEED = (0.26, 0.34, 0.2)
LANT = (1.0, 0.7, 0.3); LANT_C = (1.0, 0.92, 0.66)
GR = (0.3, 0.38, 0.37); GR_D = (0.19, 0.25, 0.27); GR_L = (0.45, 0.53, 0.49); TEAL = (0.12, 0.29, 0.31)
SICK = (0.49, 1.0, 0.6); SICK_D = (0.18, 0.55, 0.34); CORAL = (0.92, 0.46, 0.38); CORAL2 = (0.55, 0.3, 0.58)
KELP = (0.26, 0.33, 0.17); INK = (0.23, 0.12, 0.29)


def group(fn, pivot, rot=(0, 0, 0), move=(0, 0, 0)):
    """Build fn() and parent the new top-level objects to an empty at pivot, then rotate/move it."""
    before = set(bpy.data.objects)
    fn()
    e = empty("grp", pivot); bpy.context.view_layer.update()
    for ob in set(bpy.data.objects) - before:
        if ob.parent is None and ob is not e:
            ob.parent = e; ob.matrix_parent_inverse = e.matrix_world.inverted()
    e.rotation_euler = rot; e.location = (pivot[0] + move[0], pivot[1] + move[1], pivot[2] + move[2])
    return e


def boulder(x, y, z, s, seed=0, color=ROCKC, barn=True):
    r = random.Random(seed)
    ball(s, color, (x, y, z), scale=(r.uniform(1.1, 1.5), r.uniform(0.8, 1.1), r.uniform(0.6, 0.85)), seg=9, name="boulder")
    if barn:
        for k in range(r.randint(2, 4)):
            a = r.uniform(-1.2, 1.2)
            cyl(0.07, 0.08, BARN, (x + math.sin(a) * s * 1.1, y - s * 0.75, z + math.cos(a) * s * 0.45), r2=0.035, seg=6,
                rot=(math.radians(-70), 0, 0), name="barnacle", outline=0.012)


def splinter_hole(x, y, z, w, h, seed=0):
    """Dark ragged hole in the hull face (camera side at -Y) with splinters around it."""
    r = random.Random(seed)
    pts = [(math.cos(a) * w * r.uniform(0.6, 1.0), math.sin(a) * h * r.uniform(0.6, 1.0)) for a in [i / 9 * math.tau for i in range(9)]]
    prism(pts, 0.06, (0.07, 0.05, 0.05), (x, y, z), name="hole")
    for k in range(6):
        a = k / 6 * math.tau + r.uniform(-0.3, 0.3)
        p0 = (x + math.cos(a) * w * 0.7, y - 0.04, z + math.sin(a) * h * 0.7)
        p1 = (x + math.cos(a) * w * 1.25, y - 0.12, z + math.sin(a) * h * 1.25)
        rod(p0, p1, 0.035, HULL_L, r2=0.0, seg=5, name="splinter", outline=0.012)


HULL_PROFILE = [(-2.85, 4.55), (-2.55, 2.4), (-2.35, 1.5), (-1.6, 1.05), (0.0, 0.95), (1.4, 1.1), (2.3, 1.6), (2.85, 2.4),
                (3.1, 3.3), (3.05, 3.85), (1.5, 3.75), (1.4, 3.15), (-0.9, 3.0), (-1.0, 4.4)]
STERN_HALF = [(-2.85, 4.55), (-2.55, 2.4), (-2.35, 1.5), (-1.6, 1.05), (0.0, 0.95), (0.15, 1.5), (-0.15, 1.9), (0.2, 2.4),
              (-0.1, 2.7), (0.1, 3.02), (-0.9, 3.0), (-1.0, 4.4)]
BOW_HALF = [(0.45, 1.0), (1.4, 1.1), (2.3, 1.6), (2.85, 2.4), (3.1, 3.3), (3.05, 3.85), (1.5, 3.75), (1.4, 3.15), (0.55, 3.07),
            (0.35, 2.6), (0.62, 2.2), (0.3, 1.7), (0.55, 1.3)]
HD = 2.0     # hull depth (y)


def hull_zrange(prof, x):
    """Lowest / highest profile z at x (approximate, by edge intersection)."""
    zs = []
    for (x0, z0), (x1, z1) in zip(prof, prof[1:] + prof[:1]):
        if (x0 - x) * (x1 - x) <= 0 and x0 != x1:
            zs.append(z0 + (z1 - z0) * (x - x0) / (x1 - x0))
    return (min(zs), max(zs)) if zs else None


def hull_body(ox, prof, xr, state, seed=0):
    """One hull piece (prism) with strakes, navy wale band, red trim and gun ports, between x in xr."""
    r = random.Random(seed)
    X = lambda dx: ox + dx
    prism([(x, z) for x, z in prof], HD, HULL, (X(0), 0, 0), name="hull")
    fy = -HD / 2 - 0.02
    # strakes: dark plank seams following the bottom curve
    for k in range(7):
        pts = []
        for i in range(25):
            x = xr[0] + (xr[1] - xr[0]) * i / 24; zr = hull_zrange(prof, x)
            if not zr:
                continue
            z = zr[0] + 0.28 + k * 0.42
            if z < zr[1] - 0.12:
                pts.append((x, z))
        for a, b in zip(pts, pts[1:]):
            rod((X(a[0]), fy, a[1]), (X(b[0]), fy, b[1]), 0.022, HULL_D, seg=5, name="strake", outline=0.0)
    # navy wale band with sea-red trim (gun deck)
    band = []
    for i in range(31):
        x = xr[0] + (xr[1] - xr[0]) * i / 30; zr = hull_zrange(prof, x)
        if zr and zr[0] < 1.95 + 0.1 * x / 3 and zr[1] > 2.75 + 0.1 * x / 3:
            band.append(x)
    if band:
        b0, b1 = band[0] + 0.05, band[-1] - 0.05
        z0 = lambda x: 1.95 + 0.1 * x / 3
        prism([(b0, z0(b0)), (b1, z0(b1)), (b1, z0(b1) + 0.75), (b0, z0(b0) + 0.75)], HD + 0.06, NAVY, (X(0), 0, 0), name="wale")
        rod((X(b0), fy - 0.03, z0(b0) + 0.8), (X(b1), fy - 0.03, z0(b1) + 0.8), 0.05, SEARED, seg=6, name="trim")
        rod((X(b0), fy - 0.03, z0(b0) - 0.04), (X(b1), fy - 0.03, z0(b1) - 0.04), 0.04, HULL_D, seg=6, name="trim")
        # gun ports
        for gx in (-1.6, -0.55, 0.5, 1.55, 2.4):
            if not (b0 + 0.3 < gx < b1 - 0.3):
                continue
            gz = z0(gx) + 0.38
            box((0.42, 0.08, 0.38), (0.07, 0.05, 0.05), (X(gx), fy - 0.04, gz), bevel=0.02, name="port")
            box((0.46, 0.05, 0.34), SEARED, (X(gx), fy - 0.12, gz + 0.36), rot=(math.radians(-55), 0, 0), bevel=0.02, name="lid")
            if state < 2 or r.random() < 0.4:
                cyl(0.1, 0.42, TAR, (X(gx), fy - 0.2, gz), rot=(math.radians(90), 0, 0), seg=10, name="muzzle")
                cyl(0.125, 0.07, TAR, (X(gx), fy - 0.4, gz), rot=(math.radians(90), 0, 0), seg=10, name="muzzlering")


def brass_lantern(x, y, z, s=1.0, lit=1.0, cracked=False):
    """The Gullwake's big brass lantern standing at (x, y, z)."""
    box((0.95 * s, 0.95 * s, 0.25 * s), HULL_D, (x, y, z + 0.12 * s), bevel=0.04, name="lpedestal")
    lz = z + 0.25 * s
    glass = (1.0, 0.68, 0.3) if lit > 0.5 else (0.85, 0.5, 0.25)
    box((0.78 * s, 0.78 * s, 0.95 * s), glass, (x, y, lz + 0.5 * s), glow=1.2 * lit, bevel=0.03, name="lanternglow")
    if lit > 0.5:
        ball(0.24 * s, LANT_C, (x, y - 0.28 * s, lz + 0.45 * s), scale=(1, 0.6, 1.35), glow=2.0, name="lanternflame")
        cyl(0.12 * s, 0.3 * s, (1.0, 0.95, 0.78), (x, y - 0.36 * s, lz + 0.68 * s), r2=0.0, seg=8, glow=2.2, name="lanterntip")
    if cracked:
        box((0.3 * s, 0.1, 0.4 * s), (0.15, 0.1, 0.1), (x - 0.12 * s, y - 0.4 * s, lz + 0.6 * s), rot=(0, 0.4, 0), name="crackglass")
    for sx in (-0.42, 0.42):
        for sy in (-0.42, 0.42):
            box((0.09 * s, 0.09 * s, 1.05 * s), BRASS, (x + sx * s, y + sy * s, lz + 0.5 * s), name="post")
    box((0.95 * s, 0.95 * s, 0.09 * s), BRASS, (x, y, lz + 0.02 * s), name="plate")
    box((0.95 * s, 0.95 * s, 0.09 * s), BRASS, (x, y, lz + 1.02 * s), name="plate")
    box((0.82 * s, 0.05, 0.05 * s), BRASS, (x, y - 0.42 * s, lz + 0.5 * s), name="bar")
    cyl(0.7 * s, 0.45 * s, BRASS, (x, y, lz + 1.3 * s), r2=0.12 * s, seg=4, rot=(0, 0, math.radians(45)), name="cap")
    ball(0.11 * s, BRASS, (x, y, lz + 1.6 * s), name="finial")
    cyl(0.12 * s, 0.03, BRASS, (x, y, lz + 1.78 * s), rot=(math.radians(90), 0, 0), seg=12, name="ring")


def mast(x, y, z0, z1, r=0.13, crow=True, pennant=True, yards=True, torn=False):
    cyl(r, z1 - z0, HULL_D, (x, y, (z0 + z1) / 2), r2=r * 0.7, seg=10, name="mast")
    for zz in (z0 + 0.6, z0 + 1.6):
        cyl(r + 0.03, 0.08, TAR, (x, y, zz), seg=10, name="mastband")
    if yards:
        yz = z0 + (z1 - z0) * 0.42
        box((2.4, 0.1, 0.1), HULL_D, (x, y - 0.15, yz), name="yard")
        if torn:
            prism([(-1.1, 0), (1.0, 0), (0.6, -0.55), (0.2, -0.3), (-0.2, -0.9), (-0.7, -0.5), (-1.0, -0.85)], 0.05, CANVAS_D, (x, y - 0.2, yz), name="sail")
        else:
            prism([(-1.15, 0), (1.15, 0), (1.05, -0.95), (0.0, -1.05), (-1.05, -0.95)], 0.05, CANVAS, (x, y - 0.22, yz), name="sail")
            box((0.35, 0.03, 0.3), CANVAS_D, (x + 0.45, y - 0.26, yz - 0.5), rot=(0, 0.2, 0), name="patch")
        yz2 = z0 + (z1 - z0) * 0.72
        box((1.8, 0.09, 0.09), HULL_D, (x, y - 0.12, yz2), name="yard")
        cyl(0.11, 1.6, CANVAS_D, (x, y - 0.22, yz2 - 0.06), rot=(0, math.radians(90), 0), seg=8, name="furled")
    if crow:
        cz = z0 + (z1 - z0) * 0.86
        cyl(0.42, 0.42, HULL, (x, y, cz), r2=0.48, seg=12, name="crowsnest")
        cyl(0.5, 0.07, BRASS, (x, y, cz + 0.2), seg=12, name="crowrim")
        for k in range(5):
            box((0.05, 0.02, 0.36), HULL_D, (x - 0.36 + k * 0.18, y - 0.47, cz), name="crowplank", outline=0.0)
    if pennant:
        prism([(0, 0), (0.9, -0.12), (0.75, -0.2), (0.95, -0.3), (0, -0.4)], 0.03, SEARED, (x + 0.05, y, z1 + 0.05), name="pennant")


def gullwake(ox, state=0):
    """The Gullwake: galleon wrecked bow-first on the rocks, rebuilt as a fort. Faces +X, origin = ground centre.
    Long Tom pivot (state 0/1): local (2.3, 0, 4.4)."""
    r = random.Random(31 + state)
    X = lambda dx: ox + dx
    # rocks
    for i, (dx, dy, dz, s) in enumerate(((-2.2, 0.2, 0.35, 0.75), (-0.9, -0.5, 0.3, 0.7), (0.6, 0.1, 0.4, 0.85), (1.9, -0.3, 0.45, 0.8),
                                          (2.9, 0.2, 0.6, 0.85), (3.4, -0.7, 0.25, 0.5), (-3.0, -0.6, 0.2, 0.45), (0.0, -1.2, 0.15, 0.4))):
        boulder(X(dx), dy, dz, s, seed=i + 7 * state, color=ROCKC if i % 2 else ROCK_D)
    if state < 2:
        boulder(X(3.0), -0.55, 1.05, 0.75, seed=99, color=ROCKC)      # the rock she ran onto
    for k in range(6):
        cyl(0.05, r.uniform(0.3, 0.6), WEED, (X(r.uniform(-2.8, 3.2)), -1.0, 0.3), rot=(r.uniform(-0.3, 0.3), r.uniform(-0.5, 0.5), 0), seg=5, name="weed", outline=0.01)
    if state < 2:
        def ship():
            hull_body(ox, HULL_PROFILE, (-2.8, 3.05), state, seed=state)
            # deck planking edge + fort palisade along the waist
            box((2.4, HD - 0.1, 0.06), HULL_L, (X(0.25), 0, 3.06), rot=(0, math.radians(-3.5), 0), name="deck", outline=0.0)
            for k in range(10):
                if state == 1 and k in (3, 4, 7):
                    continue
                px = X(-0.75 + k * 0.22); h = r.uniform(0.55, 0.85)
                box((0.17, 0.08, h), HULL_L if k % 3 else HULL, (px, -HD / 2 + 0.06, 3.0 + 0.04 * k / 3 + h / 2), bevel=0.02, name="pal")
                cyl(0.085, 0.14, HULL_L, (px, -HD / 2 + 0.06, 3.0 + 0.04 * k / 3 + h + 0.06), r2=0.0, seg=4, name="paltip")
            box((2.3, 0.08, 0.09), HULL_D, (X(0.3), -HD / 2 + 0.0, 3.45), name="palbar")
            # stern castle details: lit windows, rail, flag
            for k, wx in enumerate((-2.45, -1.95, -1.45)):
                box((0.3, 0.06, 0.4), LANT if state == 0 else (0.9, 0.52, 0.22), (X(wx), -HD / 2 - 0.03, 3.75), glow=1.1, name="window")
                box((0.38, 0.05, 0.06), BRASS, (X(wx), -HD / 2 - 0.06, 3.98), name="wframe")
                box((0.05, 0.05, 0.42), BRASS, (X(wx), -HD / 2 - 0.07, 3.75), name="wframe")
            rod((X(-2.85), -HD / 2 - 0.03, 4.62), (X(-1.0), -HD / 2 - 0.03, 4.47), 0.05, SEARED, seg=6, name="sterntrim")
            for k in range(6):
                box((0.06, 0.06, 0.35), HULL_D, (X(-2.7 + k * 0.33), -HD / 2 + 0.05, 4.72), name="baluster")
            box((1.95, 0.08, 0.07), HULL_D, (X(-1.9), -HD / 2 + 0.05, 4.9), name="sternrail")
            # bow: forecastle rail, snapped bowsprit, figurehead gull
            for k in range(5):
                box((0.06, 0.06, 0.32), HULL_D, (X(1.6 + k * 0.33), -HD / 2 + 0.05, 3.98), name="baluster")
            box((1.5, 0.08, 0.07), HULL_D, (X(2.3), -HD / 2 + 0.05, 4.13), name="bowrail")
            rod((X(2.95), 0, 3.5), (X(3.75), 0, 3.95), 0.13, HULL_D, r2=0.1, seg=8, name="bowsprit")
            cyl(0.11, 0.06, (0.6, 0.45, 0.3), (X(3.77), 0, 3.96), rot=(0, math.radians(60), 0), seg=8, name="snap")
            # Long Tom's carriage on the forecastle (the barrel is the separate rotating sprite)
            box((0.95, 0.75, 0.32), HULL, (X(2.3), 0, 3.95), bevel=0.04, name="carriage")
            for sy in (-0.3, 0.3):
                prism([(-0.45, 0), (0.45, 0), (0.25, 0.42), (-0.15, 0.48), (-0.45, 0.3)], 0.12, HULL_D, (X(2.3), sy, 4.08), name="cheek")
            for wx in (1.95, 2.65):
                cyl(0.18, 0.1, HULL_D, (X(wx), -0.43, 3.95), rot=(math.radians(90), 0, 0), seg=12, name="wheel")
                cyl(0.06, 0.12, BRASS, (X(wx), -0.45, 3.95), rot=(math.radians(90), 0, 0), seg=8, name="hub")
            for k in range(3):
                ball(0.13, TAR, (X(1.75 + k * 0.05), -0.25 + k * 0.25, 3.9 + (0.2 if k == 2 else 0)), seg=10, name="shot")
            box((0.32, 0.32, 0.4), HULL_L, (X(1.65), 0.45, 3.95), bevel=0.04, name="keg")
            # rope ladder down to the rocks
            for sx in (0.75, 1.15):
                rod((X(sx), -HD / 2 - 0.08, 3.35), (X(sx + 0.15), -HD / 2 - 0.25, 0.75), 0.025, CANVAS_D, seg=4, name="ladder", outline=0.01)
            for k in range(6):
                zz = 3.1 - k * 0.42; dx = 0.15 * (3.35 - zz) / 2.6
                box((0.42, 0.05, 0.05), HULL_D, (X(0.95 + dx), -HD / 2 - 0.1 - 0.17 * (3.35 - zz) / 2.6, zz), name="rung")
            # main mast
            if state == 0:
                mast(X(0.25), 0.0, 3.0, 7.2)
                for (px, pz) in ((X(-2.75), 4.6), (X(3.0), 3.9)):
                    rod((X(0.25), 0, 6.9), (px, 0, pz), 0.02, TAR, seg=4, name="stay", outline=0.0)
                for k in range(4):
                    rod((X(0.25), -0.05, 6.0), (X(-0.55 + k * 0.5), -HD / 2 + 0.05, 3.1), 0.015, TAR, seg=4, name="shroud", outline=0.0)
                brass_lantern(X(-1.9), 0.0, 4.55, 1.0)
            else:
                mast(X(0.25), 0.0, 3.0, 5.6, crow=False, pennant=False, yards=False)
                for k in range(5):     # jagged break
                    cyl(0.04, r.uniform(0.2, 0.45), HULL_L, (X(0.2 + (k - 2) * 0.05), -0.08, 5.65), r2=0.0, seg=4, rot=(0, r.uniform(-0.4, 0.4), 0), name="snapmast")
                def topmast():
                    mast(X(0.25), 0.0, 5.6, 7.2, torn=True, pennant=False)
                group(topmast, (X(0.25), 0, 5.6), rot=(0, math.radians(-66), 0), move=(-0.1, -0.35, -0.35))
                brass_lantern(X(-1.9), 0.0, 4.55, 1.0, lit=1.0, cracked=True)
                splinter_hole(X(-1.5), -HD / 2 - 0.03, 1.8, 0.38, 0.3, seed=1)
                splinter_hole(X(1.2), -HD / 2 - 0.03, 2.95, 0.3, 0.22, seed=2)
                splinter_hole(X(-2.2), -HD / 2 - 0.03, 3.4, 0.25, 0.25, seed=3)
                for (px, pz, a) in ((0.2, 1.5, 0.3), (-0.9, 2.65, -0.2)):
                    box((0.7, 0.05, 0.22), HULL_L, (X(px), -HD / 2 - 0.05, pz), rot=(0, a, 0), name="patchplank")
                flame(X(1.2), -0.75, 3.75, 0.8, 0.9, seed=1)
                smoke_column(X(1.2), 0.2, 4.6, 5, 0.85, seed=2, drift=-0.2)
                smoke_column(X(-1.2), 0.5, 5.4, 4, 0.7, seed=3, drift=-0.25)
        # wrecked bow-first: the whole ship tilts bow-up about Long Tom's pivot (so the pivot does not move)
        group(ship, (X(2.3), 0, 4.4), rot=(0, math.radians(-5), 0))
    else:
        def stern():
            hull_body(ox, STERN_HALF, (-2.8, 0.1), 2, seed=5)
            for k, wx in enumerate((-2.45, -1.95, -1.45)):
                box((0.3, 0.06, 0.4), (0.12, 0.08, 0.07) if k == 1 else (0.95, 0.45, 0.15), (X(wx), -HD / 2 - 0.03, 3.75), glow=0.0 if k == 1 else 1.0, name="window")
            mast(X(-0.5), 0.0, 3.0, 4.3, crow=False, pennant=False, yards=False)
            splinter_hole(X(-1.6), -HD / 2 - 0.03, 2.1, 0.45, 0.35, seed=4)
        group(stern, (X(0.0), 0, 0.95), rot=(0, math.radians(-7), 0), move=(-0.15, 0, -0.35))
        def bow():
            hull_body(ox, BOW_HALF, (0.45, 3.05), 2, seed=6)
            rod((X(2.95), 0, 3.5), (X(3.45), 0, 3.75), 0.13, HULL_D, r2=0.11, seg=8, name="bowsprit")
            splinter_hole(X(1.6), -HD / 2 - 0.03, 2.6, 0.35, 0.3, seed=5)
        group(bow, (X(0.5), 0, 1.0), rot=(0, math.radians(9), 0), move=(0.2, 0, -0.3))
        # splintered break: jagged plank ends + ribs in the gap
        for k in range(7):
            rod((X(0.25 + r.uniform(-0.15, 0.15)), -0.9 + k * 0.3, 0.9), (X(0.25 + r.uniform(-0.4, 0.4)), -0.9 + k * 0.3, r.uniform(2.0, 3.0)),
                0.07, HULL_L if k % 2 else HULL_D, r2=0.0, seg=5, name="splinterplank")
        # fallen mast across the rocks, fallen lantern, rubble of planks
        def fallen():
            mast(X(0.25), 0.0, 1.0, 5.2, crow=True, pennant=False, yards=False)
        group(fallen, (X(0.25), 0, 1.0), rot=(0, math.radians(-74), 0), move=(0.4, -0.9, -0.2))
        def lant():
            brass_lantern(X(2.6), -1.05, 0.3, 0.85, lit=0.0, cracked=True)
        group(lant, (X(2.6), -1.05, 0.3), rot=(0, math.radians(18), 0.3), move=(0.4, 0, 0))
        for k in range(12):
            box((r.uniform(0.4, 0.9), 0.08, 0.16), HULL_L if k % 2 else HULL, (X(r.uniform(-2.6, 3.4)), r.uniform(-1.5, -0.7), 0.2 + r.random() * 0.3),
                rot=(r.uniform(-0.3, 0.3), r.uniform(-0.6, 0.6), r.uniform(-0.8, 0.8)), name="plankdebris")
        flame(X(0.3), -0.6, 1.4, 1.3, 1.25, seed=1); flame(X(-1.7), -0.8, 3.95, 0.9, 1.0, seed=4)
        flame(X(2.0), -0.8, 3.4, 0.8, 0.9, seed=6); flame(X(3.0), -1.0, 0.5, 0.6, 0.8, seed=7)
        smoke_column(X(0.3), 0.3, 3.0, 7, 1.1, seed=2, drift=-0.15)
        smoke_column(X(-1.7), 0.6, 4.9, 4, 0.85, seed=3, drift=-0.25)


def long_tom(ox, oz):
    """Long Tom: the Gullwake's great cannon barrel, pointing +X, pivot (trunnions) at (ox, 0, oz)."""
    X = lambda dx: ox + dx
    R90 = math.radians(90)
    cyl(0.29, 1.15, BRASS, (X(0.0), 0, oz), r2=0.25, rot=(0, R90, 0), seg=18, name="breech")
    cyl(0.25, 1.35, BRASS, (X(1.2), 0, oz), r2=0.19, rot=(0, R90, 0), seg=18, name="chase")
    cyl(0.25, 0.22, BRASS, (X(1.95), 0, oz), r2=0.27, rot=(0, R90, 0), seg=18, name="muzzleswell")
    cyl(0.12, 0.05, (0.08, 0.06, 0.05), (X(2.07), 0, oz), rot=(0, R90, 0), seg=14, name="bore", outline=0.0)
    for bx, rr in ((-0.5, 0.31), (0.2, 0.29), (0.56, 0.27), (1.6, 0.22)):
        cyl(rr, 0.07, (0.66, 0.46, 0.17), (X(bx), 0, oz), rot=(0, R90, 0), seg=18, name="reinforce")
    cyl(0.2, 0.18, BRASS, (X(-0.66), 0, oz), r2=0.12, rot=(0, R90, 0), seg=14, name="cascabel")
    ball(0.12, BRASS, (X(-0.82), 0, oz), seg=12, name="knob")
    box((0.12, 0.05, 0.08), (0.18, 0.15, 0.13), (X(-0.3), 0, oz + 0.29), name="vent")
    cyl(0.11, 0.78, IRON, (X(0.0), 0, oz), rot=(R90, 0, 0), seg=12, name="trunnion")
    cyl(0.07, 0.82, BRASS, (X(0.0), 0, oz), rot=(R90, 0, 0), seg=10, name="trunnioncap")
    box((0.32, 0.08, 0.16), IRON, (X(0.0), -0.33, oz + 0.1), bevel=0.02, name="capsquare")
    # carved gull on the breech (the crew's mark)
    prism([(-0.16, 0), (0.0, 0.07), (0.16, 0), (0.0, 0.03)], 0.02, (0.98, 0.85, 0.5), (X(0.3), -0.27, oz + 0.02), name="mark", outline=0.0)


def grotto(ox, state=0):
    """The Drowned Grotto: a sea-cave/rock arch shaped like a gaping fish skull of coral, bone and barnacles,
    sickly green glow inside. Faces -X (snout and underbite jut left). Origin = ground centre."""
    r = random.Random(41 + state)
    X = lambda dx: ox + dx
    # base reef + green pool
    for i, (dx, dy, dz, s) in enumerate(((-2.4, 0.0, 0.3, 0.8), (-0.8, 0.5, 0.25, 0.9), (0.9, 0.4, 0.3, 0.9), (2.4, 0.1, 0.35, 0.8),
                                          (-3.0, -0.8, 0.15, 0.45), (2.9, -0.8, 0.2, 0.5))):
        boulder(X(dx), dy, dz, s, seed=60 + i, color=GR_D if i % 2 else GR)
    cyl(1.5, 0.06, SICK_D, (X(-0.1), -1.0, 0.08), seg=24, glow=0.8, name="pool")
    cyl(1.0, 0.07, SICK, (X(-0.1), -1.05, 0.09), seg=24, glow=1.2, name="poolcore")
    hgt = (1.0, 0.95, 0.42)[state]
    # skull mass (side profile extruded): cranium dome right, snout left, gaping mouth in the camera face
    skull = [(-2.6, 0.3), (-2.9, 1.4), (-2.7, 2.9), (-2.1, 4.1), (-1.0, 5.0), (0.3, 5.5), (1.6, 5.4), (2.6, 4.7), (3.0, 3.4),
             (2.9, 1.8), (2.6, 0.3)]
    if state == 2:
        skull = [(-2.6, 0.3), (-2.9, 1.0), (-2.4, 1.9), (-1.5, 2.2), (-0.7, 1.7), (0.2, 2.4), (1.0, 2.0), (1.8, 2.7), (2.6, 2.3),
                 (2.9, 1.4), (2.6, 0.3)]
    prism(skull, 2.4, GR, (X(0), 0.15, 0), name="skull")
    # second, smaller lobes to break the slab (barnacled boulders on the shell)
    for (dx, dz, s) in ((-1.7, 3.6, 0.7), (1.8, 4.3, 0.85), (0.4, 5.0, 0.7), (2.5, 2.4, 0.75), (-2.4, 2.0, 0.6)):
        if dz * hgt < 2.4 or state < 2:
            boulder(X(dx), -0.4, dz if state < 2 else min(dz, 2.0), s, seed=int(dx * 10 + dz * 7), color=GR_L if dz > 4 else GR)
    if state < 2:
        # mouth: dark rim + glowing throat
        mouth = [(-2.1, 0.55), (-2.35, 1.6), (-1.6, 3.05), (-0.2, 3.45), (1.3, 3.1), (2.0, 2.1), (1.7, 0.55)]
        prism(mouth, 0.1, (0.05, 0.08, 0.08), (X(0), -1.08, 0), name="mouthrim", outline=0.0)
        inner = [(-1.8, 0.6), (-1.95, 1.6), (-1.35, 2.75), (-0.2, 3.1), (1.1, 2.8), (1.65, 2.0), (1.4, 0.6)]
        prism(inner, 0.1, SICK_D, (X(0), -1.12, 0), glow=0.9 if state == 0 else 0.6, name="throat", outline=0.0)
        core = [(-1.0, 0.6), (-1.1, 1.4), (-0.5, 2.2), (0.3, 2.3), (0.9, 1.6), (0.7, 0.6)]
        prism(core, 0.1, SICK, (X(0), -1.16, 0), glow=1.6 if state == 0 else 1.1, name="throatcore", outline=0.0)
        # upper jaw arch of bone with fangs; lower jaw juts left (underbite)
        jaw = [(-2.5, 1.55), (-1.8, 3.15), (-0.2, 3.65), (1.4, 3.25), (2.2, 2.1), (1.95, 1.95), (1.25, 2.95), (-0.2, 3.3), (-1.55, 2.9), (-2.15, 1.5)]
        prism(jaw, 0.35, BONE, (X(0), -1.25, 0), name="upperjaw")
        fangs = [(-2.0, 2.2, 0.75, 0.6), (-1.55, 2.85, 0.95, 0.35), (-0.95, 3.15, 0.7, 0.15), (-0.3, 3.3, 1.05, 0.0), (0.4, 3.25, 0.8, -0.1),
                 (1.0, 3.0, 0.95, -0.3), (1.55, 2.5, 0.65, -0.6)]
        for i, (fx, fz, l, lean) in enumerate(fangs):
            if state == 1 and i in (1, 4):
                l *= 0.35
            spike((X(fx), -1.3, fz), (math.sin(lean) * 0.4, 0, -1), l, 0.14, BONE if i % 2 else BONE_D, seg=7)
        lower = [(-3.3, 0.4), (-3.4, 0.8), (-3.0, 1.12), (-2.1, 1.0), (-0.2, 0.92), (1.8, 0.9), (2.05, 0.55), (1.7, 0.35), (-0.2, 0.3), (-2.4, 0.3)]
        prism(lower, 0.6, (0.74, 0.67, 0.55), (X(0), -1.15, 0), name="lowerjaw")
        ball(0.32, (0.74, 0.67, 0.55), (X(-3.2), -1.15, 0.72), scale=(1.1, 1.0, 1.0), seg=12, name="chin")
        for k in range(6):     # bone ridges + barnacles along the jaw
            box((0.06, 0.04, 0.4), BONE_D, (X(-2.6 + k * 0.75), -1.47, 0.62), rot=(0, 0.25, 0), name="jawridge", outline=0.0)
        for (bx, bz) in ((-2.9, 0.5), (-1.2, 0.45), (0.9, 0.5), (1.6, 0.6)):
            cyl(0.08, 0.09, BARN, (X(bx), -1.47, bz), r2=0.04, seg=6, rot=(math.radians(-90), 0, 0), name="barnacle", outline=0.012)
        for i, (fx, l) in enumerate(((-3.0, 0.75), (-2.4, 0.95), (-1.6, 0.7), (-0.8, 0.85), (0.1, 0.6), (0.9, 0.75), (1.5, 0.5))):
            if state == 1 and i in (2, 5):
                l *= 0.35
            spike((X(fx), -1.32, 0.92), (0.25 if i == 0 else 0.05, 0, 1), l, 0.13, BONE, seg=7)
        # eye sockets with green glow (big fish-skull orbit on the left, a smaller one right)
        for (ex, ez, er, g) in ((-1.25, 4.15, 0.55, 1.8), (0.95, 4.45, 0.42, 1.5)):
            cyl(er + 0.14, 0.12, BONE_D, (X(ex), -1.25, ez), rot=(math.radians(90), 0, 0), seg=18, name="orbit")
            cyl(er, 0.12, (0.04, 0.07, 0.07), (X(ex), -1.3, ez), rot=(math.radians(90), 0, 0), seg=18, name="socket", outline=0.0)
            ball(er * 0.42, SICK, (X(ex - 0.05), -1.32, ez - 0.05), scale=(1, 0.5, 1), glow=g if state == 0 else g * 0.7, name="eye")
        # dorsal fin rays sweeping back (right) with ragged webbing
        rays = [(-0.6, 5.1, 1.3, 0.5), (0.2, 5.45, 1.7, 0.65), (1.0, 5.45, 1.5, 0.8), (1.8, 5.1, 1.2, 0.95), (2.5, 4.5, 0.9, 1.1)]
        tips = []
        for i, (rx, rz, l, a) in enumerate(rays):
            if state == 1 and i == 2:
                l *= 0.4
            d = (math.sin(a), 0, math.cos(a)); spike((X(rx), 0.1, rz - 0.1), d, l, 0.1, BONE_D, seg=6)
            tips.append((rx + d[0] * l * 0.8, rz - 0.1 + d[2] * l * 0.8))
        web = [(r_[0], r_[1] - 0.1) for r_ in rays] [::-1]
        prism([(t[0], t[1]) for t in tips] + web, 0.04, INK, (X(0), 0.15, 0), name="finweb", outline=0.012)
        # snout horn / whale-rib tusks curving out to the left
        for (bx, bz, l, a, rr) in ((-2.7, 2.6, 1.5, -1.15, 0.17), (-2.6, 0.9, 1.1, -1.4, 0.15)):
            if state == 1 and bz > 2:
                l *= 0.5
            spike((X(bx), -0.9, bz), (math.sin(a), 0, math.cos(a)), l, rr, BONE, seg=8)
    else:
        # collapsed: the jaw has fallen, glow pours from the rubble
        ball(1.1, SICK_D, (X(-0.2), -0.9, 0.55), scale=(1.3, 0.3, 0.75), glow=1.0, name="throat")
        ball(0.5, SICK, (X(-0.2), -1.15, 0.55), scale=(1.3, 0.3, 0.8), glow=1.4, name="throatcore")
        prism([(-2.5, 0), (-1.8, 0.6), (-0.2, 0.9), (1.4, 0.7), (2.1, 0), (1.9, -0.2), (-0.2, 0.5), (-2.3, -0.2)], 0.35, BONE, (X(-0.3), -1.35, 0.4),
              rot=(0, math.radians(8), 0), name="jawfallen")
        for k, fx_ in enumerate((-2.2, -1.5, -0.8, 0.0, 0.8)):
            spike((X(fx_), -1.45, 0.75 + 0.12 * math.sin(k)), (0.15, -0.2, -1), 0.35 + 0.1 * (k % 2), 0.1, BONE, seg=6)
        for i in range(8):
            cyl(0.13, r.uniform(0.4, 0.9), BONE, (X(r.uniform(-2.6, 2.6)), r.uniform(-1.6, -1.0), 0.3), r2=0.0, seg=7,
                rot=(r.uniform(1.2, 1.9), 0, r.uniform(0, 3)), name="fangfallen")
        cyl(0.4, 0.12, BONE_D, (X(1.3), -1.35, 1.6), rot=(math.radians(90), 0, 0), seg=16, name="orbit")
        ball(0.17, SICK, (X(1.3), -1.42, 1.6), scale=(1, 0.5, 1), glow=1.0, name="eye")
        for k in range(3):
            spike((X(-1.0 + k * 1.1), 0.1, 2.0), (0.6, 0, 0.8), 0.6 + 0.2 * k, 0.1, BONE_D, seg=6)
        for (fx, fz, h, s) in ((-1.2, 1.9, 0.9, 1.0), (0.9, 2.1, 0.8, 0.9), (-2.4, 1.5, 0.6, 0.7), (2.4, 2.0, 0.7, 0.8)):
            ghost_flame(X(fx), -0.6, fz, h, s, seed=int(fx * 10))
        smoke_column(X(0.4), 0.3, 2.6, 6, 1.0, seed=9, drift=0.25, color=(0.27, 0.32, 0.31))
        rubble(X(0), -0.8, 0.4, 16, 2.6, seed=4, colors=(GR, GR_D, BONE_D))
    # coral, barnacles and kelp everywhere
    corals = [(-2.3, 3.3, 0.8, -0.5, CORAL), (2.4, 4.0, 0.9, 0.4, CORAL2), (2.7, 1.2, 0.7, 0.6, CORAL), (-2.8, 1.8, 0.6, -0.8, CORAL2),
              (0.2, 5.4, 0.6, 0.1, CORAL), (-0.5, 0.2, 0.55, -0.2, CORAL)]
    for i, (cx, cz, h, a, col) in enumerate(corals):
        if state == 2 and cz > 2.2:
            continue
        coral(X(cx), -1.0, cz * (1 if state < 2 else 1), h, a, col, seed=i)
    for k in range(26 if state < 2 else 12):
        bx, bz = r.uniform(-2.8, 2.9), r.uniform(0.3, 5.2 * hgt)
        if state < 2 and -2.0 < bx < 1.7 and 0.6 < bz < 3.3:
            continue
        cyl(0.09, 0.1, BARN, (X(bx), -1.25, bz), r2=0.045, seg=6, rot=(math.radians(-90), 0, 0), name="barnacle", outline=0.012)
    if state < 2:
        for k in range(7):
            kx = -1.9 + k * 0.6 + r.uniform(-0.1, 0.1); kz = hull_zrange([(-2.5, 1.55), (-1.8, 3.15), (-0.2, 3.65), (1.4, 3.25), (2.2, 2.1)], kx)
            kz = kz[1] if kz else 3.0
            kelp(X(kx), -1.45, kz - 0.1, r.uniform(0.7, 1.3) * (0.6 if state == 1 else 1), seed=k)
    if state == 1:
        for (cx, cz, a) in ((-2.3, 3.9, 0.4), (2.2, 3.5, -0.3), (1.9, 1.4, 0.6), (-0.3, 4.6, 0.2)):
            box((0.07, 0.05, 0.85), SICK, (X(cx), -1.3, cz), rot=(0, a, 0), glow=1.5, name="crack", outline=0.0)
            box((0.05, 0.05, 0.45), SICK, (X(cx + 0.15), -1.3, cz - 0.4), rot=(0, -a, 0), glow=1.5, name="crack", outline=0.0)
        ghost_flame(X(2.2), -0.7, 4.6, 0.8, 0.9, seed=2)
        smoke_column(X(2.2), 0.3, 5.4, 4, 0.8, seed=4, drift=0.25, color=(0.27, 0.32, 0.31))
        rubble(X(-2.9), -0.7, 0.3, 8, 0.6, seed=6, colors=(GR, GR_D, BONE_D))


def coral(x, y, z, h, lean, col, seed=0):
    r = random.Random(seed)
    def br(p, ang, l, rad, d):
        q = (p[0] + math.sin(ang) * l, p[1], p[2] + math.cos(ang) * l)
        rod(p, q, rad, col, r2=rad * 0.75, seg=6, name="coral", outline=0.014)
        if d > 0:
            for k in range(2):
                br(q, ang + (k - 0.5) * r.uniform(0.6, 1.1), l * 0.7, rad * 0.72, d - 1)
        else:
            ball(rad * 1.2, col, q, seg=6, name="coraltip", outline=0.01)
    br((x, y, z), lean, h * 0.45, 0.07, 2)


def kelp(x, y, z, l, seed=0):
    r = random.Random(seed); p = (x, y, z)
    for k in range(4):
        q = (p[0] + r.uniform(-0.1, 0.1), y, p[2] - l / 4)
        rod(p, q, 0.05 - k * 0.008, KELP, seg=5, name="kelp", outline=0.01); p = q


def ghost_flame(x, y, z, h, s=1.0, seed=0):
    """Sickly green flame for the Deep's structures."""
    r = random.Random(seed)
    cyl(0.22 * s, h, SICK_D, (x, y, z + h / 2), r2=0.0, seg=7, glow=1.2, name="gflame")
    cyl(0.12 * s, h * 0.6, (0.82, 1.0, 0.82), (x + 0.02, y - 0.12 * s, z + h * 0.3), r2=0.0, seg=7, glow=1.6, name="gflame_in")
    for k in range(2):
        dx = r.uniform(-0.18, 0.18) * s
        cyl(0.11 * s, h * 0.55, SICK, (x + dx, y - 0.05, z + h * 0.27), r2=0.0, seg=6, glow=1.2, name="glick")
