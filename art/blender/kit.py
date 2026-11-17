# Siegeline character kit — runs inside Blender 5.x (bpy).
# Chunky toy figures built from shared rounded parts, rigid parts parented to a pivot rig,
# toon 3-band shading with an inverted-hull outline, one fixed orthographic camera.
#
# Character files (art/blender/chars/*.py) build SPEC dicts and call register(SPEC).
# A render driver then calls render_job("<job>") (jobs live in cast.py): every character of the job is
# placed on one grid, each in its own cell, and the whole group renders as ONE animation.
# Conventions: a figure is built facing +X with its near side at -Y; a "holder" empty above the rig turns it
# 25 deg toward the camera (3/4 view) and mirrors enemies so they face -X. Ground = local z 0 = feet anchor.
import bpy, bmesh, math, traceback
from mathutils import Vector, Matrix

PPU = 96            # pixels per world unit — same for every character so scale is consistent
ELEV = 10           # camera elevation in degrees (fixed for the whole cast)
ANIMS = [("idle", 6), ("walk", 8), ("attack", 8), ("hit", 4), ("die", 8)]  # legacy single-character order
OUTLINE = (0.012, 0.008, 0.01, 1)
OL = 0.026          # outline thickness (world units)

# shared palette (sRGB) — see docs/art-guide.md
PAL = dict(
    red=(0.549, 0.165, 0.118), red_dk=(0.37, 0.11, 0.08), steel=(0.34, 0.355, 0.39), steel_dk=(0.23, 0.235, 0.27),
    brass=(0.83, 0.60, 0.23), glow=(1.0, 0.70, 0.28), leather=(0.35, 0.23, 0.15), wood=(0.42, 0.29, 0.17),
    ash=(0.85, 0.83, 0.78), skin=(0.79, 0.60, 0.48), hskin=(0.228, 0.22, 0.22), hlimb=(0.30, 0.28, 0.28),
    bone=(0.85, 0.81, 0.71), ember=(1.0, 0.48, 0.10), blood=(0.353, 0.059, 0.07), rust=(0.48, 0.29, 0.165),
    dark=(0.10, 0.09, 0.10), cloth_dk=(0.17, 0.14, 0.15),
)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE"
    s.render.film_transparent = True
    s.view_settings.view_transform = "Standard"
    s.view_settings.look = "None"
    try:
        s.eevee.taa_render_samples = 16
    except Exception:
        pass
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    w = bpy.data.worlds.new("W"); s.world = w; w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.32, 0.30, 0.34, 1); bg.inputs[1].default_value = 1.0
    _mats.clear()
    global _outline
    _outline = None
    return s


def lin(c):
    """Colors in this kit are written as sRGB (what you see); Blender wants linear."""
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(f(v) for v in c[:3])


_mats = {}
def toon(color, name=None, glow=0.0, rim=0.25):
    color = lin(color)
    key = (tuple(round(c, 3) for c in color), glow, rim)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name or "toon")
    m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputMaterial")
    dif = N.new("ShaderNodeBsdfDiffuse"); dif.inputs[0].default_value = (1, 1, 1, 1)
    s2r = N.new("ShaderNodeShaderToRGB")
    bw = N.new("ShaderNodeRGBToBW")
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp; cr.interpolation = "CONSTANT"
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.30, 0.27, 0.36, 1)
    cr.elements[1].position = 0.18; cr.elements[1].color = (0.62, 0.58, 0.66, 1)
    e = cr.elements.new(0.55); e.color = (1.0, 1.0, 1.0, 1)
    mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    mul.inputs[6].default_value = (*color[:3], 1)
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs[0].default_value = 0.12
    rr = N.new("ShaderNodeValToRGB"); rr.color_ramp.interpolation = "CONSTANT"
    rr.color_ramp.elements[0].color = (0, 0, 0, 1); rr.color_ramp.elements[1].position = 0.6
    rr.color_ramp.elements[1].color = (rim, rim, rim * 0.9, 1)
    add = N.new("ShaderNodeMix"); add.data_type = "RGBA"; add.blend_type = "ADD"; add.inputs[0].default_value = 1.0
    em = N.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.0
    L.new(dif.outputs[0], s2r.inputs[0]); L.new(s2r.outputs[0], bw.inputs[0])
    L.new(bw.outputs[0], ramp.inputs[0]); L.new(ramp.outputs[0], mul.inputs[7])
    L.new(lw.outputs[1], rr.inputs[0])
    L.new(mul.outputs[2], add.inputs[6]); L.new(rr.outputs[0], add.inputs[7])
    if glow > 0:
        g = N.new("ShaderNodeMix"); g.data_type = "RGBA"; g.blend_type = "MIX"
        g.inputs[0].default_value = min(glow, 1.0)
        g.inputs[7].default_value = (*color[:3], 1)
        L.new(add.outputs[2], g.inputs[6]); L.new(g.outputs[2], em.inputs[0])
        em.inputs[1].default_value = 1.0 + glow
    else:
        L.new(add.outputs[2], em.inputs[0])
    L.new(em.outputs[0], out.inputs[0])
    _mats[key] = m
    return m


_outline = None
def outline_mat():
    global _outline
    if _outline:
        return _outline
    m = bpy.data.materials.new("outline"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = OUTLINE
    nt.links.new(em.outputs[0], o.inputs[0])
    m.use_backface_culling = True
    _outline = m
    return m


def _mesh_obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _finish(ob, color, glow=0.0, bevel=0.0, outline=None, flat=False):
    outline = OL if outline is None else outline
    ob.data.materials.append(toon(color, glow=glow))
    ob.data.materials.append(outline_mat())
    if bevel > 0:
        b = ob.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "NONE"
    if flat:
        for p in ob.data.polygons:
            p.use_smooth = False
    if outline > 0:
        s = ob.modifiers.new("ol", "SOLIDIFY"); s.thickness = outline; s.offset = 1
        s.use_flip_normals = True; s.material_offset = 1; s.use_rim = False
    return ob


def box(size, color, loc=(0, 0, 0), bevel=0.06, rot=(0, 0, 0), glow=0.0, name="box", taper=None, outline=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        if taper is not None and v.co.z > 0:   # taper top face (x,y factors)
            v.co.x *= taper[0]; v.co.y *= taper[1]
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    ob = _mesh_obj(name, bm); ob.location = loc; ob.rotation_euler = rot
    return _finish(ob, color, glow, bevel=min(bevel, min(size) * 0.45), flat=True, outline=outline)


def ball(r, color, loc=(0, 0, 0), scale=(1, 1, 1), glow=0.0, name="ball", seg=16, outline=None):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    ob = _mesh_obj(name, bm); ob.location = loc
    return _finish(ob, color, glow, outline=outline)


def cyl(r, h, color, loc=(0, 0, 0), rot=(0, 0, 0), r2=None, seg=12, glow=0.0, name="cyl", bevel=0.02, outline=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    ob = _mesh_obj(name, bm); ob.location = loc; ob.rotation_euler = rot
    return _finish(ob, color, glow, bevel=bevel, outline=outline)


def rod(p0, p1, r, color, r2=None, seg=8, glow=0.0, name="rod", outline=None):
    """Cylinder/cone from p0 (radius r) to p1 (radius r2)."""
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=max(d.length, 1e-4))
    ob = _mesh_obj(name, bm)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    ob.location = (p0 + p1) / 2
    return _finish(ob, color, glow, outline=outline)


def spike(base, direction, length, r, color, glow=0.0, seg=6, outline=None):
    d = Vector(direction).normalized()
    return rod(base, Vector(base) + d * length, r, color, r2=0.0, seg=seg, glow=glow, name="spike", outline=outline)


def prism(points, depth, color, loc=(0, 0, 0), rot=(0, 0, 0), glow=0.0, name="prism", outline=None):
    """Polygon (x,z) list extruded along Y (faces the camera)."""
    bm = bmesh.new()
    fr = [bm.verts.new((x, -depth / 2, z)) for x, z in points]
    bk = [bm.verts.new((x, depth / 2, z)) for x, z in points]
    bm.faces.new(fr); bm.faces.new(list(reversed(bk)))
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((fr[i], fr[j], bk[j], bk[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _mesh_obj(name, bm); ob.location = loc; ob.rotation_euler = rot
    return _finish(ob, color, glow, flat=True, outline=outline)


def empty(name, loc=(0, 0, 0), parent=None):
    """Pivot at WORLD position loc, parented without moving."""
    e = bpy.data.objects.new(name, None); e.location = loc
    bpy.context.scene.collection.objects.link(e)
    e.rotation_mode = "XYZ"
    if parent:
        bpy.context.view_layer.update()
        e.parent = parent
        e.matrix_parent_inverse = parent.matrix_world.inverted()
    return e


def attach(ob, pivot):
    """Parent ob to a pivot keeping its world placement (rigid toy joint)."""
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    ob.parent = pivot
    ob.matrix_parent_inverse = pivot.matrix_world.inverted()
    ob.matrix_world = mw
    return ob


def keyable(rig, name, ob, kind="scale", default=None):
    """Register an object whose scale/rotation the anims may key by name (d['k'][name])."""
    base = tuple(ob.scale) if kind == "scale" else tuple(ob.rotation_euler)
    rig["keyables"][name] = (ob, kind, base)
    if default is not None:
        rig.setdefault("kdef", {})[name] = default


def glow_pivot(rig, name, loc, parent):
    """Empty used to scale-pulse glowing parts (attach glow parts to it)."""
    e = empty("glow_" + name, loc, parent)
    keyable(rig, name, e, "scale")
    return e


# ---------------------------------------------------------------- humanoid builder
def humanoid(spec):
    """Toy humanoid: big head, short legs. Faces +X. Near side is -Y (camera side)."""
    sc = spec.get("scale", 1.0)
    C = spec["colors"]
    tier = spec.get("tier", 1) if spec.get("facing", 1) > 0 else 1
    lf = spec.get("limb", 1.0)
    bulk = spec.get("bulk", 1.0) * (1.06 if tier >= 2 else 1.0)
    hip_h = 0.62 * sc * spec.get("leg", 1.0)
    torso_h = 0.62 * sc * spec.get("torso", 1.0)
    bw = 0.52 * sc * bulk
    head_r = 0.36 * sc * spec.get("head", 1.0)
    rig = dict(keyables={}, sc=sc, spec=spec, free=[], tier=tier)
    root = empty("root"); rig["root"] = root
    hips = empty("hips", (0, 0, hip_h), root); rig["hips"] = hips
    legw = 0.2 * sc * lf * spec.get("legw", 1.0)
    plate = C["trim"] if tier >= 3 else C.get("metal", PAL["steel"])
    for side, y in (("L", 0.13 * sc * bulk), ("R", -0.13 * sc * bulk)):
        lp = empty("leg_" + side, (0, y, hip_h), root); rig["leg_" + side] = lp
        attach(box((legw, legw, hip_h * 0.8), C["legs"], (0, y, hip_h * 0.55), name="thigh"), lp)
        attach(box((0.3 * sc * spec.get("foot", 1.0), 0.24 * sc * max(lf, 0.8), 0.16 * sc), C.get("boots", C["legs"]),
                   (0.04 * sc, y, 0.08 * sc), name="boot"), lp)
        if tier >= 2:
            attach(box((legw * 1.3, legw * 1.25, hip_h * 0.36), C.get("metal", PAL["steel"]), (0.02 * sc, y, hip_h * 0.36), name="greave"), lp)
    tp = empty("torso", (0, 0, hip_h), hips); rig["torso"] = tp
    attach(box((bw * 0.82, bw * 0.72, torso_h), C["body"], (0, 0, hip_h + torso_h * 0.5),
               taper=spec.get("taper", (1.15, 1.05)), name="chest"), tp)
    attach(box((bw * 0.86, bw * 0.76, 0.14 * sc), C.get("belt", C["legs"]), (0, 0, hip_h + 0.05 * sc), name="belt"), tp)
    if spec.get("tabard"):
        attach(box((0.06 * sc, bw * 0.52, hip_h * 0.62), C.get("tabard", C["body"]), (bw * 0.43, 0, hip_h * 0.72), name="tabard", taper=(1, 1.1)), tp)
        attach(box((0.06 * sc, bw * 0.52, hip_h * 0.55), C.get("tabard", C["body"]), (-bw * 0.43, 0, hip_h * 0.75), name="tabard_b"), tp)
    if spec.get("robe"):
        rc = C.get("robe", C["body"])
        attach(cyl(bw * 0.5, hip_h * 1.02, rc, (0, 0, hip_h * 0.52), r2=bw * 0.42, seg=14, name="robe"), hips)
        attach(cyl(bw * 0.62, hip_h * 0.55, rc, (0, 0, hip_h * 0.28), r2=bw * 0.5, seg=14, name="robe_hem"), hips)
        if C.get("robe_trim"):
            attach(cyl(bw * 0.635, 0.07 * sc, C["robe_trim"], (0, 0, 0.06 * sc), seg=14, name="robe_trim"), hips)
    if tier >= 2:  # chest plate
        attach(box((0.1 * sc, bw * 0.62, torso_h * 0.5), C.get("metal", PAL["steel"]), (bw * 0.42, 0, hip_h + torso_h * 0.62), name="cplate"), tp)
        if tier >= 3:
            attach(box((0.06 * sc, bw * 0.7, 0.07 * sc), C["trim"], (bw * 0.47, 0, hip_h + torso_h * 0.86), name="cplate_rim"), tp)
            attach(box((0.06 * sc, 0.07 * sc, torso_h * 0.42), C["trim"], (bw * 0.48, 0, hip_h + torso_h * 0.6), name="cplate_bar"), tp)
    shoulder_z = hip_h + torso_h * 0.88
    hx = spec.get("head_fwd", 0.0) * sc
    hp = empty("head", (hx * 0.4, 0, shoulder_z + 0.05 * sc), tp); rig["head"] = hp
    hz = shoulder_z + head_r * 1.0
    if not spec.get("no_face"):
        attach(ball(head_r, C["skin"], (hx + 0.02 * sc, 0, hz), scale=(0.95, 0.95, 1.0), name="headball"), hp)
        es = spec.get("eye_style", "dot")
        for ey in (-0.13, 0.13):
            ex = hx + head_r * 0.86 + 0.02 * sc
            if es == "slit":   # enemy: slanted glowing slit
                attach(box((0.06 * sc, 0.11 * sc * spec.get("head", 1.0), 0.045 * sc), C["eyes"], (ex, ey * sc * spec.get("head", 1.0), hz + 0.02 * sc),
                           rot=(math.radians(22 if ey > 0 else -22), 0, 0), glow=2.0, name="eye", outline=0.012), hp)
            elif es == "dot":
                attach(ball(0.05 * sc, C.get("eyes", (0.05, 0.04, 0.04)), (ex, ey * sc * spec.get("head", 1.0), hz + 0.03 * sc),
                            scale=(0.6, 1, 1.3), name="eye", outline=0.0), hp)
    rig["head_z"] = hz; rig["head_r"] = head_r; rig["head_x"] = hx
    asc = spec.get("arm_scale", {})
    for side, y in (("L", bw * 0.5), ("R", -bw * 0.5)):
        k = asc.get(side, 1.0)
        ap = empty("arm_" + side, (0, y, shoulder_z), tp); rig["arm_" + side] = ap
        al = torso_h * 0.95 * spec.get("arm", 1.0) * (k ** 0.5)
        aw = 0.17 * sc * lf * k
        attach(box((aw, aw, al), C.get("arms", C["body"]), (0, y, shoulder_z - al * 0.45), name="arm"), ap)
        hr = 0.1 * sc * spec.get("hand", 1.0) * k
        attach(ball(hr, C.get("hands", C["skin"]), (0, y, shoulder_z - al * 0.98), name="hand"), ap)
        hand = empty("hand_" + side, (0, y, shoulder_z - al * 0.98), ap); rig["hand_" + side] = hand
        if spec.get("pauldrons") or tier >= 2:
            pc = C["trim"] if (tier >= 3 or spec.get("brass_pauldrons")) else C.get("metal", PAL["steel"])
            ps = spec.get("pauldron_size", 1.0) * (1.12 if tier >= 2 else 1.0)
            attach(box((0.32 * sc * ps, 0.3 * sc * ps, 0.17 * sc * ps), pc, (0, y * 1.08, shoulder_z + 0.01 * sc), bevel=0.05, name="pauldron"), ap)
            attach(box((0.3 * sc * ps, 0.26 * sc * ps, 0.08 * sc), pc, (0, y * 1.12, shoulder_z - 0.12 * sc), bevel=0.03, name="pauldron2"), ap)
    rig["shoulder_z"] = shoulder_z; rig["hip_h"] = hip_h; rig["bw"] = bw; rig["torso_h"] = torso_h
    return rig


# ---------------------------------------------------------------- quadruped builder (crawlers)
def quad(spec):
    """Low four-legged crawler. Faces +X. Body pivot 'hips', head, jaw, legs FL FR BL BR, tail."""
    sc = spec.get("scale", 1.0); C = spec["colors"]
    h = 0.4 * sc; bl = 0.95 * sc
    rig = dict(keyables={}, sc=sc, spec=spec, free=[], tier=1, quad=True)
    root = empty("root"); rig["root"] = root
    body = empty("hips", (0, 0, h), root); rig["hips"] = body
    attach(box((bl, 0.36 * sc, 0.3 * sc), C["body"], (0, 0, h + 0.1 * sc), taper=(0.8, 0.85), name="qbody"), body)
    attach(ball(0.24 * sc, C["body"], (bl * 0.3, 0, h + 0.18 * sc), scale=(1.1, 0.95, 0.85), name="shoulders"), body)
    for i in range(4):   # spine spikes, jagged sizes
        L = (0.24, 0.16, 0.2, 0.12)[i] * sc
        attach(spike((bl * (0.3 - i * 0.2), 0, h + 0.25 * sc), (-0.4, 0, 1), L, 0.05 * sc, C["bone"]), body)
    for i in range(3):   # bone ribs on the flank (near side)
        attach(box((0.04 * sc, 0.03 * sc, 0.2 * sc), C["bone"], (bl * (0.05 - i * 0.12), -0.18 * sc, h + 0.08 * sc), rot=(0.25, 0.2, 0), name="rib"), body)
    attach(box((0.14 * sc, 0.03 * sc, 0.06 * sc), C["eyes"], (-bl * 0.1, -0.185 * sc, h + 0.16 * sc), rot=(0, 0.4, 0), glow=1.6, name="crack", outline=0.0), body)
    hd = empty("head", (bl * 0.48, 0, h + 0.14 * sc), body); rig["head"] = hd
    attach(box((0.34 * sc, 0.3 * sc, 0.22 * sc), C["skin"], (bl * 0.62, 0, h + 0.16 * sc), taper=(0.7, 0.8), name="qhead"), hd)
    for ey in (-0.09, 0.09):
        attach(box((0.06 * sc, 0.08 * sc, 0.04 * sc), C["eyes"], (bl * 0.78, ey * sc, h + 0.21 * sc), rot=(math.radians(25 if ey > 0 else -25), 0, 0), glow=2.0, name="eye", outline=0.01), hd)
    for y in (-0.1, 0.1):   # little horns, asymmetric
        attach(spike((bl * 0.58, y * sc, h + 0.26 * sc), (-0.6, y, 0.8), (0.2 if y < 0 else 0.12) * sc, 0.04 * sc, C["bone"]), hd)
    jaw = empty("jaw", (bl * 0.5, 0, h + 0.07 * sc), hd); rig["jaw"] = jaw
    attach(box((0.34 * sc, 0.24 * sc, 0.07 * sc), C["bone"], (bl * 0.68, 0, h + 0.04 * sc), taper=(0.8, 0.8), name="jaw"), jaw)
    for i in range(3):
        attach(spike((bl * (0.6 + i * 0.07), -0.08 * sc, h + 0.08 * sc), (0, 0, 1), 0.07 * sc, 0.02 * sc, C["bone"], outline=0.01), jaw)
    attach(box((0.06 * sc, 0.2 * sc, 0.03 * sc), C.get("blood", PAL["blood"]), (bl * 0.82, 0, h + 0.075 * sc), name="maw", outline=0.0), jaw)
    for name, x, y in (("FL", bl * 0.33, 0.14), ("FR", bl * 0.33, -0.14), ("BL", -bl * 0.35, 0.14), ("BR", -bl * 0.35, -0.14)):
        lp = empty("leg_" + name, (x, y * sc, h + 0.05 * sc), root); rig["leg_" + name] = lp
        front = name[0] == "F"
        knee = Vector((x + (0.1 if front else -0.12) * sc, y * sc * 1.3, h * 0.45))
        attach(rod((x, y * sc, h + 0.05 * sc), knee, 0.06 * sc, C["legs"], r2=0.045 * sc), lp)
        foot = Vector((x + (0.04 if front else 0.0) * sc, y * sc * 1.3, 0.03 * sc))
        attach(rod(knee, foot, 0.045 * sc, C["legs"], r2=0.03 * sc), lp)
        attach(spike(foot, (1, 0, -0.2), 0.12 * sc, 0.03 * sc, C["bone"], outline=0.012), lp)
        if front:
            attach(spike(knee, (-1, 0, 0.6), 0.12 * sc, 0.03 * sc, C["bone"]), lp)
    tl = empty("tail", (-bl * 0.5, 0, h + 0.12 * sc), body); rig["tail"] = tl
    attach(rod((-bl * 0.5, 0, h + 0.12 * sc), (-bl * 0.95, 0, h + 0.3 * sc), 0.06 * sc, C["body"], r2=0.015 * sc), tl)
    attach(spike((-bl * 0.75, 0, h + 0.24 * sc), (-0.3, 0, 1), 0.1 * sc, 0.03 * sc, C["bone"]), tl)
    rig["head_z"] = h + 0.16 * sc; rig["head_r"] = 0.15 * sc; rig["head_x"] = 0
    rig["hip_h"] = h; rig["shoulder_z"] = h + 0.2 * sc; rig["bw"] = 0.36 * sc
    return rig


# ---------------------------------------------------------------- props
GRIP = dict(sword=75, shortsword=80, knife=95, cleaver=75, boneclub=75, greathammer=150, bellpole=15, lamppole=12,
            bow=0, lantern=0, claws=0, hammer=70, spear=88, staff=10)


def _ember(C):
    return C.get("ember", PAL["ember"])


def weapon(kind, rig, C, side="R", grip=None):
    """Builds the prop upright around the hand, on a grip pivot (keyable as gR/gL) rotated by the grip angle."""
    sc = rig["sc"]; hand = rig["hand_" + side]; p = hand.matrix_world.translation.copy()
    x, z = p.x, p.z
    y = p.y - 0.05 * sc if side == "R" else p.y + 0.02 * sc
    t3 = rig["tier"] >= 3
    M = _ember(C) if t3 else C.get("metal", PAL["steel"]); G = 1.0 if t3 else 0.0
    h = empty("grip_" + side, (x, y, z))
    A = lambda ob: attach(ob, h)
    if kind in ("sword", "shortsword", "knife"):
        L = dict(sword=1.0, shortsword=0.62, knife=0.38)[kind] * sc
        wd = dict(sword=0.11, shortsword=0.1, knife=0.07)[kind] * sc
        A(box((wd, 0.045 * sc, L), M, (x, y, z + 0.08 * sc + L * 0.5), taper=(0.55, 1), glow=G, name="blade", bevel=0.015))
        A(box((0.05 * sc, 0.05 * sc, L * 0.5), C.get("metal_dk", PAL["steel_dk"]) if not t3 else (1.0, 0.85, 0.5), (x, y - 0.012 * sc, z + 0.08 * sc + L * 0.35), glow=G, name="fuller", outline=0.0))
        A(box(((0.32 if kind != "knife" else 0.18) * sc, 0.08 * sc, 0.06 * sc), C["trim"], (x, y, z + 0.07 * sc), name="guard"))
        A(ball(0.055 * sc, C["trim"], (x, y, z - 0.08 * sc), name="pommel"))
    elif kind == "greathammer":
        A(rod((x, y, z - 0.35 * sc), (x, y, z + 1.15 * sc), 0.045 * sc, C["wood"]))
        A(box((0.56 * sc, 0.3 * sc, 0.32 * sc), M, (x, y, z + 1.12 * sc), glow=G * 0.6, name="hammerhead"))
        A(box((0.6 * sc, 0.33 * sc, 0.07 * sc), C["trim"] if rig["tier"] >= 2 else C.get("metal_dk", PAL["steel_dk"]), (x, y, z + 1.12 * sc), name="hband"))
        A(box((0.05 * sc, 0.32 * sc, 0.34 * sc), C.get("metal_dk", PAL["steel_dk"]) if not t3 else (1.0, 0.85, 0.5), (x + 0.29 * sc, y, z + 1.12 * sc), glow=G, name="hface"))
        A(cyl(0.06 * sc, 0.1 * sc, C["trim"], (x, y, z + 0.9 * sc), name="collar"))
    elif kind == "bow":
        pts = []
        for i in range(7):
            u = -1 + i / 3.0
            pts.append(Vector((x + 0.16 * sc - 0.2 * sc * u * u, y, z + 0.62 * sc * u)))
        for a, b in zip(pts, pts[1:]):
            A(rod(a, b, 0.04 * sc, C["wood"] if not t3 else _ember(C), r2=0.04 * sc, glow=G * 0.8))
        A(box((0.09 * sc, 0.07 * sc, 0.18 * sc), C["trim"], (x + 0.16 * sc, y, z), name="bowgrip"))
        A(rod(pts[0], pts[-1], 0.008 * sc, (0.85, 0.8, 0.7), outline=0.008))
    elif kind == "bellpole":
        A(rod((x, y, z - 0.75 * sc), (x, y, z + 1.25 * sc), 0.04 * sc, C["wood"]))
        A(rod((x - 0.05 * sc, y, z + 1.22 * sc), (x + 0.42 * sc, y, z + 1.26 * sc), 0.04 * sc, C["wood"]))
        A(spike((x, y, z + 1.25 * sc), (0, 0, 1), 0.16 * sc, 0.05 * sc, C["trim"]))
        bc = _ember(C) if t3 else C["trim"]
        bs = 1.15 if rig["tier"] >= 2 else 1.0
        A(cyl(0.12 * sc * bs, 0.34 * sc * bs, bc, (x + 0.4 * sc, y, z + 1.0 * sc), r2=0.06 * sc * bs, seg=14, glow=G * 0.5, name="bell"))
        A(cyl(0.16 * sc * bs, 0.06 * sc, bc, (x + 0.4 * sc, y, z + 0.84 * sc), seg=14, glow=G * 0.5, name="bellrim"))
        A(ball(0.06 * sc, C.get("metal_dk", PAL["steel_dk"]) if not t3 else (1, 0.85, 0.4), (x + 0.4 * sc, y, z + 0.78 * sc), glow=G, name="clapper"))
    elif kind == "lamppole":
        A(rod((x, y, z - 0.8 * sc), (x, y, z + 1.35 * sc), 0.035 * sc, C["wood"]))
        A(rod((x, y, z + 1.33 * sc), (x + 0.3 * sc, y, z + 1.45 * sc), 0.03 * sc, C.get("metal_dk", PAL["steel_dk"])))
        A(rod((x + 0.3 * sc, y, z + 1.45 * sc), (x + 0.36 * sc, y, z + 1.3 * sc), 0.025 * sc, C.get("metal_dk", PAL["steel_dk"])))
        lx, lz = x + 0.36 * sc, z + 1.12 * sc
        ls = 1.2 if rig["tier"] >= 3 else 1.0
        A(box((0.24 * sc * ls, 0.24 * sc * ls, 0.06 * sc), C["trim"] if rig["tier"] >= 3 else C.get("metal_dk", PAL["steel_dk"]), (lx, y, lz + 0.17 * sc * ls), name="lampcap"))
        A(spike((lx, y, lz + 0.2 * sc * ls), (0, 0, 1), 0.12 * sc, 0.1 * sc * ls, C["trim"] if rig["tier"] >= 3 else C.get("metal_dk", PAL["steel_dk"])))
        A(box((0.24 * sc * ls, 0.24 * sc * ls, 0.05 * sc), C["trim"] if rig["tier"] >= 3 else C.get("metal_dk", PAL["steel_dk"]), (lx, y, lz - 0.16 * sc * ls), name="lampbase"))
        gp = glow_pivot(rig, "lamp", (lx, y, lz), None); attach(gp, h)
        attach(ball(0.14 * sc * ls, C["flame"], (lx, y, lz), scale=(1, 1, 1.25), glow=1.6, name="lampglow", outline=0.012), gp)
        attach(ball(0.07 * sc * ls, (1, 0.95, 0.75), (lx - 0.03 * sc, y - 0.08 * sc, lz), glow=2.0, name="core", outline=0.0), gp)
    elif kind == "lantern":
        A(rod((x, y, z), (x, y, z - 0.16 * sc), 0.015 * sc, C.get("metal_dk", PAL["steel_dk"])))
        A(box((0.24 * sc, 0.24 * sc, 0.06 * sc), C["trim"], (x, y, z - 0.18 * sc), name="lancap"))
        A(box((0.24 * sc, 0.24 * sc, 0.05 * sc), C["trim"], (x, y, z - 0.5 * sc), name="lanbase"))
        for dx in (-0.1, 0.1):
            A(box((0.03 * sc, 0.03 * sc, 0.3 * sc), C.get("metal_dk", PAL["steel_dk"]), (x + dx * sc, y - 0.1 * sc, z - 0.34 * sc), name="bar", outline=0.008))
        gp = glow_pivot(rig, "lantern", (x, y, z - 0.34 * sc), None); attach(gp, h)
        attach(ball(0.12 * sc, C["flame"], (x, y, z - 0.34 * sc), scale=(1, 1, 1.25), glow=1.6, name="flame", outline=0.0), gp)
        attach(ball(0.06 * sc, (1, 0.95, 0.75), (x, y - 0.06 * sc, z - 0.34 * sc), glow=2.0, name="core", outline=0.0), gp)
    elif kind == "claws":
        for dz, L in ((0.05, 0.3), (-0.02, 0.36), (-0.09, 0.28)):
            A(spike((x + 0.04 * sc, y, z + dz * sc), (1, 0, -0.35), L * sc, 0.035 * sc, C["bone"]))
        A(ball(0.05 * sc, C.get("blood", PAL["blood"]), (x + 0.12 * sc, y - 0.02 * sc, z - 0.04 * sc), name="gore", outline=0.0))
    elif kind == "cleaver":
        A(rod((x, y, z - 0.18 * sc), (x, y, z + 0.32 * sc), 0.045 * sc, C["wood"]))
        A(box((0.4 * sc, 0.05 * sc, 0.85 * sc), C.get("rust", PAL["rust"]), (x + 0.12 * sc, y, z + 0.72 * sc), taper=(1.25, 1), name="cleaver"))
        A(box((0.07 * sc, 0.06 * sc, 0.8 * sc), C.get("blood", PAL["blood"]), (x + 0.33 * sc, y, z + 0.74 * sc), name="edge", outline=0.0))
        A(cyl(0.06 * sc, 0.04 * sc, PAL["dark"], (x + 0.05 * sc, y - 0.03 * sc, z + 0.95 * sc), rot=(math.radians(90), 0, 0), name="hole", outline=0.0))
    elif kind == "boneclub":
        A(rod((x, y, z - 0.15 * sc), (x, y, z + 1.05 * sc), 0.06 * sc, C["bone"], r2=0.13 * sc))
        A(ball(0.17 * sc, C["bone"], (x, y, z + 1.05 * sc), scale=(1.1, 0.9, 0.8), name="knob"))
        A(ball(0.1 * sc, C["bone"], (x, y, z - 0.15 * sc), name="knob2"))
        for a in (0, 70, 140, 220, 290):
            r = math.radians(a)
            A(spike((x, y, z + 0.95 * sc), (math.cos(r), math.sin(r), 0.3), 0.18 * sc, 0.035 * sc, C.get("metal_dk", PAL["steel_dk"])))
        A(ball(0.08 * sc, C.get("blood", PAL["blood"]), (x + 0.12 * sc, y - 0.06 * sc, z + 1.0 * sc), name="gore", outline=0.0))
    g = math.radians(GRIP.get(kind, 0) if grip is None else grip)
    h.rotation_euler = (0, g, 0)
    bpy.context.view_layer.update()
    h.parent = hand
    h.matrix_parent_inverse = hand.matrix_world.inverted()
    keyable(rig, "g" + side, h, "roty")
    rig["grip_" + side] = h
    return h


def tower_shield(rig, C, side="L", tilt=0.0):
    sc = rig["sc"]; hand = rig["hand_" + side]; p = hand.matrix_world.translation.copy()
    t = rig["tier"]
    h = empty("shield", (p.x, p.y, p.z))
    A = lambda ob: attach(ob, h)
    x, y, z = p.x + 0.2 * sc, p.y - 0.04 * sc, p.z + 0.12 * sc
    rim = C["trim"] if t >= 3 else C.get("metal", PAL["steel"])
    A(box((0.1 * sc, 0.58 * sc, 0.88 * sc), C["shield"], (x, y, z), bevel=0.04, name="tower"))
    A(box((0.08 * sc, 0.64 * sc, 0.08 * sc), rim, (x + 0.02 * sc, y, z + 0.42 * sc), name="rimT"))
    A(box((0.08 * sc, 0.64 * sc, 0.08 * sc), rim, (x + 0.02 * sc, y, z - 0.42 * sc), name="rimB"))
    A(box((0.08 * sc, 0.08 * sc, 0.88 * sc), rim, (x + 0.02 * sc, y - 0.29 * sc, z), name="rimL"))
    A(box((0.08 * sc, 0.08 * sc, 0.88 * sc), rim, (x + 0.02 * sc, y + 0.29 * sc, z), name="rimR"))
    # lantern emblem
    A(box((0.05 * sc, 0.2 * sc, 0.26 * sc), C["trim"], (x + 0.06 * sc, y, z + 0.02 * sc), name="emblem"))
    A(ball(0.07 * sc, C["flame"] if t < 3 else (1, 0.85, 0.5), (x + 0.09 * sc, y, z + 0.02 * sc), scale=(0.6, 1, 1.25), glow=1.2 if t < 3 else 2.0, name="emblemglow", outline=0.0))
    if t >= 2:
        for dz in (-0.3, 0.3):
            A(ball(0.05 * sc, rim, (x + 0.07 * sc, y - 0.2 * sc, z + dz * sc), name="stud", outline=0.012))
            A(ball(0.05 * sc, rim, (x + 0.07 * sc, y + 0.2 * sc, z + dz * sc), name="stud", outline=0.012))
    h.rotation_euler = (0, math.radians(tilt), 0)
    bpy.context.view_layer.update()
    h.parent = hand
    h.matrix_parent_inverse = hand.matrix_world.inverted()
    return h


def helmet(rig, C, kind):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig.get("head_x", 0)
    t = rig["tier"]; M = C.get("metal", PAL["steel"])
    if kind == "kettle":
        attach(cyl(r * 1.45, 0.07 * sc, M, (hx, 0, hz + r * 0.32), seg=16), hp)
        attach(ball(r * 1.04, M, (hx, 0, hz + r * 0.3), scale=(1, 1, 0.78), name="dome"), hp)
        if t >= 3:
            attach(cyl(r * 1.06, 0.08 * sc, C["trim"], (hx, 0, hz + r * 0.42), seg=16, name="band"), hp)
        if t >= 2:
            attach(box((r * 1.3, 0.09 * sc, 0.2 * sc), C.get("crest", PAL["red"]), (hx - 0.03 * sc, 0, hz + r * 1.12), bevel=0.04, name="crest"), hp)
            for y in (-1, 1):
                attach(box((r * 0.5, 0.05 * sc, r * 0.7), M, (hx + r * 0.45, y * r * 0.92, hz - r * 0.25), name="cheek"), hp)
    elif kind == "great":
        attach(box((r * 2.2, r * 2.15, r * 2.25), M, (hx + 0.01 * sc, 0, hz + 0.02 * sc), bevel=0.08, name="greathelm", taper=(0.92, 0.92)), hp)
        attach(box((0.05 * sc, r * 1.6, 0.07 * sc), (0.04, 0.03, 0.03), (hx + r * 1.08, 0, hz + 0.06 * sc), name="visor", bevel=0.0, outline=0.0), hp)
        attach(box((0.06 * sc, 0.09 * sc, r * 1.5), C["trim"], (hx + r * 1.1, 0, hz - 0.06 * sc), name="nasal"), hp)
        if spec_get(rig, "crest") or t >= 2:
            attach(box((r * 1.9, 0.1 * sc, 0.26 * sc), C.get("crest", PAL["red"]), (hx - 0.04 * sc, 0, hz + r * 1.2), taper=(0.8, 1), bevel=0.04, name="crest"), hp)
        if t >= 3 or spec_get(rig, "gilded_helm"):
            attach(box((r * 2.26, r * 2.2, 0.08 * sc), C["trim"], (hx + 0.01 * sc, 0, hz + r * 0.95), name="helmband"), hp)
    elif kind == "hood":
        cc = C.get("hood", C.get("cloth", PAL["red_dk"]))
        attach(ball(r * 1.16, cc, (hx - 0.13 * sc, 0, hz + 0.05 * sc), scale=(1.0, 1.0, 1.08), name="hood"), hp)
        attach(spike((hx - 0.3 * sc, 0, hz + r * 0.6), (-1, 0, 0.5), 0.3 * sc, 0.13 * sc, cc), hp)
        attach(cyl(r * 1.05, 0.14 * sc, cc, (0, 0, hz - r * 0.95), seg=14, name="cowl"), hp)
    elif kind == "coif":
        cc = C.get("hood", C.get("cloth", PAL["red_dk"]))
        attach(ball(r * 1.06, cc, (hx - 0.06 * sc, 0, hz + 0.06 * sc), scale=(1, 1, 0.95), name="coif"), hp)
        attach(cyl(r * 0.98, 0.16 * sc, cc, (0, 0, hz - r * 0.95), seg=14, name="collar"), hp)
    elif kind == "hair":
        attach(ball(r * 1.02, C["hair"], (hx - 0.07 * sc, 0, hz + 0.06 * sc), scale=(1, 1, 0.92), name="hair"), hp)
        for i, (dx, dz) in enumerate(((-0.25, 0.25), (-0.3, 0.05), (-0.15, 0.36))):
            attach(spike((hx + dx * sc, 0, hz + dz * sc), (-1, 0, 0.4 - i * 0.2), 0.16 * sc, 0.07 * sc, C["hair"]), hp)


def spec_get(rig, k, d=None):
    return rig["spec"].get(k, d)


def cape(rig, C, length=1.0):
    sc = rig["sc"]; tp = rig["torso"]; z = rig["shoulder_z"]; bw = rig["bw"]
    attach(box((0.08 * sc, bw * 0.95, 0.95 * sc * length), C["cloth"], (-bw * 0.45, 0, z - 0.45 * sc * length), name="cape", taper=(1, 0.75)), tp)
    attach(box((0.1 * sc, bw * 0.4, 0.08 * sc), C["trim"], (-bw * 0.42, 0, z + 0.0), name="clasp"), tp)


def quiver(rig, C):
    sc = rig["sc"]; tp = rig["torso"]; z = rig["shoulder_z"]; bw = rig["bw"]
    t3 = rig["tier"] >= 3
    b = Vector((-bw * 0.48, 0.05 * sc, z - 0.55 * sc)); top = Vector((-bw * 0.6, 0.05 * sc, z + 0.12 * sc))
    attach(rod(b, top, 0.1 * sc, C.get("leather", PAL["leather"]), r2=0.11 * sc), tp)
    attach(rod(b + Vector((0, 0, 0.15 * sc)), b + Vector((0, 0, 0.22 * sc)), 0.115 * sc, C["trim"]), tp)
    for i, dy in enumerate((-0.05, 0.0, 0.05)):
        tip = top + Vector((-0.03 * sc * i, dy * sc, 0.16 * sc))
        attach(rod(top + Vector((0, dy * sc, 0)), tip, 0.015 * sc, C["wood"]), tp)
        attach(ball(0.045 * sc, _ember(C), tip, scale=(1, 1, 1.4), glow=1.8 if not t3 else 2.4, outline=0.0, name="fire"), tp)
        attach(ball(0.025 * sc, (1, 0.9, 0.5), tip + Vector((0, -0.02 * sc, 0.02 * sc)), glow=2.0, outline=0.0, name="firecore"), tp)


def scarf(rig, C):
    sc = rig["sc"]; tp = rig["torso"]; z = rig["shoulder_z"]; bw = rig["bw"]
    attach(cyl(bw * 0.42, 0.14 * sc, C["scarf"], (0, 0, z + 0.04 * sc), seg=14, name="scarf"), tp)
    tl = empty("scarftail", (-bw * 0.3, 0, z + 0.02 * sc), tp)
    attach(box((0.5 * sc, 0.05 * sc, 0.12 * sc), C["scarf"], (-bw * 0.3 - 0.25 * sc, -0.04 * sc, z - 0.02 * sc), rot=(0, -0.35, 0), name="tail1"), tl)
    attach(box((0.38 * sc, 0.05 * sc, 0.1 * sc), C["scarf"], (-bw * 0.3 - 0.2 * sc, 0.05 * sc, z - 0.1 * sc), rot=(0, -0.6, 0), name="tail2"), tl)
    keyable(rig, "scarf", tl, "roty")


def cracks(rig, pivot, pts, C, size=1.0):
    """Glowing ember crack strips. pts: (x, y, z, angle_deg, length) in world space."""
    sc = rig["sc"]
    for (x, y, z, a, L) in pts:
        attach(box((0.03 * sc * size, 0.03 * sc * size, L * sc), C["eyes"], (x, y, z), rot=(0, math.radians(a), 0), glow=1.8, name="crack", outline=0.0), pivot)


# ---------------------------------------------------------------- animation
def key(ob, frame, rot=None, loc=None, scale=None):
    if rot is not None:
        ob.rotation_euler = rot; ob.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        ob.location = loc; ob.keyframe_insert("location", frame=frame)
    if scale is not None:
        ob.scale = scale; ob.keyframe_insert("scale", frame=frame)


def _tab(T, t):
    i = min(int(t * 8 + 1e-6), 7)
    d = {}
    for k, v in T.items():
        if k == "k":
            d["k"] = {n: vv[i] for n, vv in v.items()}
        else:
            d[k] = v[i] if isinstance(v, (list, tuple)) else v
    return d


# attack tables (8 frames, strike on frame 4). Angles in degrees: arm a<0 swings forward/up; weapon dir = arm + grip.
ATTACKS = {
    "swing": dict(aR=[-20, -90, -160, -175, 20, 35, 5, -15], torso=[0, -6, -12, -12, 16, 18, 8, 2],
                  rx=[0, 0, -0.02, -0.02, 0.1, 0.1, 0.04, 0], aL=[15, 15, 20, 20, 25, 25, 20, 15],
                  lL=[0, -6, -12, -15, -18, -18, -10, -4], lR=[0, 6, 10, 12, 15, 15, 8, 3]),
    "heavy": dict(aR=[-20, -70, -140, -175, 0, 30, 10, -20], aL=[10, 0, -10, -10, 30, 30, 20, 10],
                  torso=[0, -8, -14, -14, 18, 22, 10, 2], rx=[0, -0.02, -0.04, -0.04, 0.12, 0.12, 0.05, 0],
                  lL=[0, -6, -12, -15, -20, -20, -10, -4], lR=[0, 6, 10, 12, 15, 15, 8, 3]),
    "thrust": dict(aR=[-60, -45, -30, -30, -78, -78, -68, -60], torso=[0, -4, -8, -8, 14, 14, 6, 0],
                   rx=[0, -0.03, -0.06, -0.06, 0.2, 0.18, 0.08, 0], aL=[-45, -45, -40, -40, -60, -58, -50, -45],
                   lL=[0, 0, 4, 4, -20, -20, -10, 0], lR=[0, 4, 8, 8, 18, 18, 8, 0]),
    "shoot": dict(aL=[-60, -85, -85, -85, -85, -85, -80, -60], aR=[-50, -85, -70, -62, -88, -92, -80, -55],
                  torso=[0, -2, -5, -6, -1, 0, 0, 0], rx=[0, 0, 0, 0, -0.04, -0.03, -0.01, 0],
                  lL=[-10] * 8, lR=[10] * 8, k=dict(gL=[60, 85, 85, 85, 85, 85, 80, 60], arrow=[0, 1, 1, 1, 0, 0, 0, 0])),
    "cast": dict(aR=[-15, -50, -90, -120, -130, -120, -60, -15], aL=[10, -10, -30, -50, -60, -50, -20, 10],
                 torso=[0, -3, -6, -8, -8, -6, -3, 0], lL=[0] * 8, lR=[0] * 8,
                 k=dict(gR=[0, 30, 60, 95, 105, 95, 40, 0], lamp=[1, 1.1, 1.3, 1.7, 2.1, 1.7, 1.2, 1])),
    "ring": dict(aR=[-15, -35, -55, -65, -5, 5, -10, -15], aL=[-25] * 8, torso=[0, -3, -6, -6, 6, 6, 2, 0],
                 lL=[0] * 8, lR=[0] * 8, k=dict(gR=[0, 0, 0, 0, 0, 0, 0, 0])),
    "slam": dict(aR=[-30, -100, -170, -200, -45, -35, -40, -30], aL=[-30, -100, -170, -200, -45, -35, -40, -30],
                 torso=[0, -6, -14, -16, 22, 24, 12, 2], rx=[0, -0.02, -0.04, -0.04, 0.12, 0.12, 0.06, 0],
                 rz=[0, 0, 0.02, 0.03, -0.04, -0.04, -0.02, 0],
                 lL=[0, -5, -10, -12, -24, -24, -12, 0], lR=[0, 5, 8, 10, 18, 18, 8, 0]),
    "slash": dict(aR=[-30, -120, -150, -40, 10, -20, -30, -30], aL=[10, 10, -60, -130, -150, -40, 0, 10],
                  torso=[0, 4, 8, 12, 16, 12, 6, 0], rx=[0, 0.05, 0.1, 0.15, 0.2, 0.15, 0.08, 0],
                  lL=[0, -15, -25, -25, -30, -20, -10, 0], lR=[0, 15, 25, 25, 25, 15, 10, 0]),
    "claw": dict(aR=[-20, -90, -150, -170, -20, 20, 0, -20], aL=[0, -60, -120, -160, -170, -10, 10, 0],
                 torso=[0, -6, -10, -10, 14, 18, 10, 4], rx=[0, -0.02, -0.04, -0.04, 0.12, 0.12, 0.05, 0],
                 lL=[0, -6, -12, -15, -18, -18, -10, -4], lR=[0, 6, 10, 12, 15, 15, 8, 3]),
    "spit": dict(torso=[0, -10, -20, -24, 18, 22, 10, 0], head=[0, -10, -20, -25, 10, 15, 5, 0],
                 rx=[0, -0.03, -0.05, -0.05, 0.08, 0.06, 0.02, 0], aR=[-10, 10, 25, 30, -40, -30, -15, -10],
                 aL=[-10, 10, 25, 30, -40, -30, -15, -10], lL=[0] * 8, lR=[0] * 8,
                 k=dict(sac=[1, 1.15, 1.3, 1.45, 0.75, 0.85, 0.95, 1])),
    "belly": dict(torso=[0, -8, -16, -18, 20, 24, 10, 0], rx=[0, -0.04, -0.08, -0.08, 0.18, 0.16, 0.06, 0],
                  aR=[-20, 10, 30, 35, -60, -50, -30, -20], aL=[-20, 10, 30, 35, -60, -50, -30, -20],
                  lL=[0, 0, 5, 5, -15, -15, -5, 0], lR=[0, 0, -5, -5, 15, 15, 5, 0],
                  k=dict(pyre=[1, 1.05, 1.1, 1.15, 1.3, 1.2, 1.05, 1])),
}


def a_idle(t, st):
    s = math.sin(t * math.tau)
    sway = st.get("sway", 1.0)
    return dict(bob=0.015 * s, torso=2 * s * sway, head=-2 * s * sway, aR=st.get("aR0", -15) + 4 * s * sway,
                aL=st.get("aL0", 10) - 4 * s * sway, k=dict(st.get("idle_k", {})))


def a_walk(t, st):
    s = math.sin(t * math.tau); c = math.cos(t * math.tau)
    sw = st.get("stride", 30) / st.get("heavy", 1.0)
    d = dict(bob=st.get("bounce", 0.045) * abs(c), torso=st.get("walk_lean", 6), head=-4,
             lL=-sw * s, lR=sw * s, aL=st.get("aL0", 10) + (sw * 0.8 * s if st.get("swingL", True) else 2 * s),
             aR=st.get("aR0", -15) - (sw * 0.5 * s if st.get("swingR", True) else 2 * s),
             k=dict(scarf=12 * c))
    return d


def a_hit(t, st):
    k = math.sin(t * math.pi + 0.6) if t > 0 else 0.7
    return dict(rx=-0.12 * k, torso=-22 * k, head=-15 * k, aR=st.get("aR0", -15) + 30 * k, aL=st.get("aL0", 10) + 35 * k)


def a_die(t, st):
    k = min(t / 0.75, 1.0); k = k * k * (3 - 2 * k)
    if st.get("die") == "fwd":   # collapse forward onto the face
        return dict(rr=82 * k, rx=-0.8 * k, rz=0.2 * k, torso=12 * k, head=15 * k, aR=-120 * k, aL=-140 * k,
                    lL=-20 * k, lR=10 * k, leanf=1 - k)
    return dict(rr=-86 * k, rx=0.85 * k, rz=0.2 * k, torso=-15 * k, head=-25 * k, aR=60 * k, aL=80 * k,
                lL=20 * k, lR=-10 * k, leanf=1 - k)


def a_attack(t, st):
    return _tab(ATTACKS[st.get("attack", "swing")], t)


BASE_ANIMS = dict(idle=a_idle, walk=a_walk, hit=a_hit, die=a_die, attack=a_attack)


def apply(rig, f, d, st):
    """Key every rig channel at frame f from pose dict d (degrees / units * scale)."""
    rad = math.radians; sc = rig["sc"]
    lean = st.get("lean", 0) * d.get("leanf", 1.0)
    key(rig["root"], f, (rad(d.get("rx_rot", 0)), rad(d.get("rr", 0)), 0), (d.get("rx", 0) * sc, 0, d.get("rz", 0) * sc))
    rs = d.get("rs", 1.0); key(rig["root"], f, scale=(rs, rs, rs))
    key(rig["hips"], f, (0, rad(d.get("pitch", 0)), 0), Vector(rig["hips_base"]) + Vector((0, 0, d.get("bob", 0) * sc)))
    if rig.get("quad"):
        key(rig["head"], f, (0, rad(d.get("head", 0)), 0)); key(rig["jaw"], f, (0, rad(d.get("jaw", 0)), 0))
        key(rig["tail"], f, (0, rad(d.get("tail", 0)), 0))
        for n in ("FL", "FR", "BL", "BR"):
            key(rig["leg_" + n], f, (0, rad(d.get(n, 0)), 0))
    else:
        key(rig["torso"], f, (0, rad(d.get("torso", 0) + lean), 0))
        key(rig["head"], f, (0, rad(d.get("head", 0) - lean * st.get("headc", 0.6)), 0))
        for s, sgn in (("L", 1), ("R", -1)):
            key(rig["arm_" + s], f, (rad(sgn * d.get("a" + s + "x", 0)), rad(d.get("a" + s, 0)), 0))
            key(rig["leg_" + s], f, (0, rad(d.get("l" + s, 0)), 0))
    kd = d.get("k", {})
    for name, (ob, kind, base) in rig["keyables"].items():
        v = kd.get(name, rig.get("kdef", {}).get(name))
        if kind == "scale":
            v = 1.0 if v is None else v
            key(ob, f, scale=tuple(b * v for b in base))
        else:
            v = 0.0 if v is None else v
            key(ob, f, rot=(base[0], base[1] + rad(v), base[2]))
    if st.get("post"):
        st["post"](rig, f, d, st)


def animate(rig, spec, frame0=1, anims=None):
    st = spec.get("style", {})
    rig["hips_base"] = tuple(rig["hips"].location)
    custom = st.get("anims", {})
    f = frame0
    for name, n, *_ in anims:
        fn = custom.get(name) or BASE_ANIMS[name]
        for i in range(n):
            d = fn(i / n, st)
            d["_anim"] = name; d["_i"] = i; d["_n"] = n
            apply(rig, f, d, st)
            f += 1
    return f - frame0


def _fcurves(action):
    try:
        return list(action.fcurves)
    except Exception:  # layered actions (Blender 4.4+)
        out = []
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out += list(cb.fcurves)
        return out


def constant_interp():
    for ob in bpy.data.objects:
        if ob.animation_data and ob.animation_data.action:
            for fc in _fcurves(ob.animation_data.action):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


# ---------------------------------------------------------------- registry + group render
REG = {}


def register(spec):
    REG[spec["id"]] = spec
    return spec


def build_char(spec):
    rig = spec["builder"](spec) if "builder" in spec else humanoid(spec)
    C = spec["colors"]
    if spec.get("helmet"):
        helmet(rig, C, spec["helmet"])
    if spec.get("cape"):
        cape(rig, C, spec.get("cape_len", 1.0))
    if spec.get("weapon"):
        weapon(spec["weapon"], rig, C, "R", spec.get("grip"))
    if spec.get("offhand"):
        weapon(spec["offhand"], rig, C, "L", spec.get("grip_L"))
    if spec.get("shield"):
        tower_shield(rig, C, "L", -spec.get("style", {}).get("aL0", 10))
    for fn in spec.get("extras", []):
        fn(rig, C)
    return rig


def stage_grid(W, H, ppu):
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = W, H
    s.render.resolution_percentage = 100
    cam_d = bpy.data.cameras.new("cam"); cam_d.type = "ORTHO"; cam_d.ortho_scale = max(W, H) / ppu
    cam_d.clip_start = 0.1; cam_d.clip_end = 200
    cam = bpy.data.objects.new("cam", cam_d); s.collection.objects.link(cam); s.camera = cam
    e = math.radians(ELEV)
    cam.location = (0, -60 * math.cos(e), 60 * math.sin(e))
    cam.rotation_euler = (math.radians(90) - e, 0, 0)
    sun = bpy.data.lights.new("key", "SUN"); sun.energy = 3.2; sun.angle = math.radians(8)
    so = bpy.data.objects.new("key", sun); s.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(-35), math.radians(-20))
    fill = bpy.data.lights.new("fill", "SUN"); fill.energy = 0.8
    fo = bpy.data.objects.new("fill", fill); s.collection.objects.link(fo)
    fo.rotation_euler = (math.radians(70), math.radians(60), math.radians(30))
    return cam


def _parent_keep_local(ob, holder):
    ob.parent = holder
    ob.matrix_parent_inverse = Matrix.Identity(4)


def place(sid, J, pos):
    """Build one cell's content at holder position pos. Returns frames used."""
    holder = empty("H_" + sid, pos)
    if sid.startswith("i_"):
        root = empty("iconroot")
        REG[sid]["icon"](root, REG[sid])
        holder.rotation_euler = (0, 0, math.radians(REG[sid].get("yaw", 0)))
        _parent_keep_local(root, holder)
        return 1
    base = sid[2:] if sid.startswith("p_") else sid
    spec = REG[base]
    rig = build_char(spec)
    facing = spec.get("facing", 1)
    s = 1.0
    if sid.startswith("p_"):
        s = 1.0 / rig["sc"]
        e = math.cos(math.radians(ELEV))
        holder.location.z -= (rig["head_z"] - 0.12 * rig["sc"]) * s
        holder.location.x -= 0.04
    holder.scale = (facing * s, s, s)
    holder.rotation_euler = (0, 0, math.radians(-J["yaw"] * facing))
    _parent_keep_local(rig["root"], holder)
    for ob in rig["free"]:
        _parent_keep_local(ob, holder)
    anims = ANIMSETS["still"] if sid.startswith("p_") else anims_of(sid)
    if sid.startswith("p_"):
        st = spec.get("style", {})
        rig["hips_base"] = tuple(rig["hips"].location)
        apply(rig, 1, a_idle(0.0, st), st)
        return 1
    return animate(rig, spec, 1, anims)


def render_job(job, only=None):
    J = JOBS[job]; ids = only or J["ids"]
    reset()
    cw, ch = J["cell"]; cols = min(J["cols"], len(ids)); rows = (len(ids) + cols - 1) // cols
    ppu = J["ppu"]; W, H = cw * cols, ch * rows
    ce = math.cos(math.radians(ELEV))
    nmax = 1
    for i, sid in enumerate(ids):
        col, row = i % cols, i // cols
        ax, ay = cell_anchor(job, sid)
        px, py = col * cw + ax, row * ch + ay
        X = (px - W / 2) / ppu; Z = (H / 2 - py) / (ppu * ce)
        try:
            nmax = max(nmax, place(sid, J, (X, 0, Z)))
        except Exception:
            print("FAILED", sid); traceback.print_exc()
    constant_interp()
    stage_grid(W, H, ppu)
    sc = bpy.context.scene
    sc.frame_start = 1; sc.frame_end = nmax
    print("JOB", job, "cells", len(ids), "frames", nmax, "size", W, H)


def build_and_animate(spec):
    """Legacy single-character path (old samples)."""
    register(spec)
    JOBS["_one"] = dict(cell=tuple(spec.get("cell", (384, 384))), cols=1, ppu=PPU, ax=0.5, gy=24, yaw=25, mode="anim", ids=[spec["id"]])
    render_job("_one")


# ---------------------------------------------------------------- Hollow Host parts (enemies)
def hollow_horns(rig, C, big=1.0, broken="L"):
    """Asymmetric horns: one long curved, one snapped short."""
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig.get("head_x", 0)
    for side, y in (("L", r * 0.62), ("R", -r * 0.62)):
        p0 = Vector((hx - r * 0.1, y, hz + r * 0.62))
        if side == broken:
            attach(rod(p0, p0 + Vector((-0.06, y * 0.25, 0.16)) * sc * big, 0.075 * sc * big, C["bone"], r2=0.055 * sc * big), hp)
        else:
            p1 = p0 + Vector((-0.12, y * 0.3, 0.26)) * sc * big
            p2 = p1 + Vector((-0.22, y * 0.2, 0.1)) * sc * big
            attach(rod(p0, p1, 0.08 * sc * big, C["bone"], r2=0.06 * sc * big), hp)
            attach(rod(p1, p2, 0.06 * sc * big, C["bone"], r2=0.0), hp)


def hollow_maw(rig, C, w=1.0):
    """Bone teeth row under the eyes + dried blood smear."""
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig.get("head_x", 0)
    x = hx + r * 0.88
    attach(box((0.05 * sc, r * 1.0 * w, 0.08 * sc), PAL["dark"], (x, 0, hz - r * 0.45), name="mouth", outline=0.0), hp)
    for i in range(5):
        y = (-0.4 + i * 0.2) * r * w
        attach(spike((x + 0.02 * sc, y, hz - r * 0.55), (0.2, 0, 1), 0.08 * sc, 0.025 * sc, C["bone"], outline=0.0), hp)
    attach(box((0.03 * sc, 0.08 * sc, 0.16 * sc), C.get("blood", PAL["blood"]), (x + 0.01 * sc, -r * 0.3, hz - r * 0.72), name="drip", outline=0.0), hp)


def hollow_ribs(rig, C, n=3, w=0.8):
    sc = rig["sc"]; z = rig["hip_h"]; bw = rig["bw"]; th = rig["torso_h"]
    for i in range(n):
        attach(box((0.05 * sc, bw * w * (1 - i * 0.08), 0.05 * sc), C["bone"], (bw * 0.44, 0, z + th * (0.45 + i * 0.15)),
                   rot=(0, math.radians(-10), 0), name="rib"), rig["torso"])


def hollow_spikes(rig, C, n=3, size=1.0):
    """Back/shoulder spikes, uneven."""
    sc = rig["sc"]; z = rig["shoulder_z"]; bw = rig["bw"]
    lens = (0.3, 0.2, 0.26, 0.16, 0.22)
    for i in range(n):
        attach(spike((-bw * 0.35, (i - (n - 1) / 2) * 0.08 * sc, z - i * 0.18 * sc), (-0.8, 0, 0.7), lens[i % 5] * sc * size, 0.06 * sc * size, C["bone"]), rig["torso"])
    attach(spike((0, bw * 0.55, z + 0.05 * sc), (-0.3, 0.4, 1), 0.22 * sc * size, 0.06 * sc * size, C["bone"]), rig["arm_L"])


def hollow_elbows(rig, C):
    sc = rig["sc"]; z = rig["shoulder_z"]; bw = rig["bw"]; th = rig["torso_h"]
    for side, y in (("L", bw * 0.5), ("R", -bw * 0.5)):
        attach(spike((-0.04 * sc, y, z - th * 0.5), (-1, 0, 0.3), 0.14 * sc, 0.035 * sc, C["bone"]), rig["arm_" + side])


def hollow_cracks(rig, C, n=4):
    sc = rig["sc"]; z = rig["hip_h"]; bw = rig["bw"]; th = rig["torso_h"]
    pts = [(bw * 0.42, -bw * 0.2, z + th * 0.35, 30, 0.2), (bw * 0.3, -bw * 0.37, z + th * 0.6, -20, 0.18),
           (bw * 0.42, bw * 0.15, z + th * 0.75, 60, 0.12), (-bw * 0.1, -bw * 0.37, z + th * 0.3, -40, 0.2),
           (bw * 0.1, -bw * 0.37, z + th * 0.8, 15, 0.14)]
    cracks(rig, rig["torso"], pts[:n], C)


# ---------------------------------------------------------------- quadruped anims
def q_idle(t, st):
    s = math.sin(t * math.tau)
    return dict(bob=0.012 * s, head=4 * s, jaw=6 + 6 * s, tail=10 * s, pitch=1.5 * s)


def q_walk(t, st):
    s = math.sin(t * math.tau); s2 = math.sin(t * math.tau + 0.9); c = math.cos(t * math.tau)
    return dict(FL=-38 * s, FR=-38 * s2, BL=38 * s, BR=38 * s2, pitch=7 * s, bob=0.06 * abs(c), head=-5 * s,
                jaw=10, tail=18 * c)


Q_ATTACK = dict(rx=[0, -0.06, -0.1, -0.1, 0.38, 0.32, 0.12, 0], pitch=[0, -6, -10, -10, 12, 10, 4, 0],
                head=[0, -10, -15, -15, 20, 15, 5, 0], jaw=[5, 15, 30, 35, 50, 10, 5, 5],
                FL=[0, 10, 15, 15, -40, -30, -10, 0], FR=[0, 10, 15, 15, -40, -30, -10, 0],
                BL=[0, 15, 25, 25, 35, 20, 10, 0], BR=[0, 15, 25, 25, 35, 20, 10, 0],
                bob=[0, -0.03, -0.05, -0.05, 0.06, 0.03, 0, 0])


def q_attack(t, st):
    return _tab(Q_ATTACK, t)


def q_hit(t, st):
    k = math.sin(t * math.pi + 0.6) if t > 0 else 0.7
    return dict(rx=-0.15 * k, pitch=-15 * k, head=-20 * k, jaw=30 * k, FL=-15 * k, FR=-15 * k)


def q_die(t, st):
    k = min(t / 0.75, 1.0); k = k * k * (3 - 2 * k)
    return dict(bob=-0.24 * k, pitch=8 * k, head=30 * k, jaw=35 * k, tail=-25 * k, FL=-60 * k, FR=-45 * k,
                BL=60 * k, BR=48 * k)


QUAD_ANIMS = dict(idle=q_idle, walk=q_walk, attack=q_attack, hit=q_hit, die=q_die)
# ---------------------------------------------------------------- backgrounds (layered dioramas)
import random

def flat(color, glow=0.0):
    """Unlit flat color material for scenery (painted look, layers read by value)."""
    color = lin(color)
    m = bpy.data.materials.new("flat"); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color[:3], 1); em.inputs[1].default_value = 1.0 + glow
    nt.links.new(em.outputs[0], o.inputs[0]); return m


def gradient_plane(w, h, top, bottom, loc):
    top, bottom = lin(top), lin(bottom)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    ob = _mesh_obj("sky", bm); ob.scale = (w, h, 1); ob.rotation_euler = (math.radians(90), 0, 0); ob.location = loc
    m = bpy.data.materials.new("sky"); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB"); em = nt.nodes.new("ShaderNodeEmission"); o = nt.nodes.new("ShaderNodeOutputMaterial")
    ramp.color_ramp.elements[0].color = (*bottom, 1); ramp.color_ramp.elements[1].color = (*top, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs[1], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], o.inputs[0])
    ob.data.materials.append(m); return ob


def ridge(x0, x1, base, peaks, color, y, seed=1, jag=0.5, glow=0.0, step=1.2):
    """Silhouette band: a polygon strip from x0..x1 with random peaks, standing in the XZ plane at depth y."""
    rnd = random.Random(seed); bm = bmesh.new(); top = []; x = x0
    while x <= x1 + step:
        top.append((x, base + peaks * (0.4 + 0.6 * rnd.random()) * (1 if rnd.random() > jag else 0.55)))
        x += step * (0.6 + 0.8 * rnd.random())
    vs = [bm.verts.new((x, y, z)) for x, z in top] + [bm.verts.new((x, y, base - 12)) for x, _ in reversed(top)]
    bm.faces.new(vs)
    ob = _mesh_obj("ridge", bm); ob.data.materials.append(flat(color, glow)); return ob


def prop_obj(parts, x, y, z=0, color=(0, 0, 0), s=1.0, rot=0, face=False):
    """parts: list of (shape, size, offset). Flat-colored scenery props built from primitives."""
    m = flat(color)
    for shape, size, off in parts:
        bm = bmesh.new()
        if shape == "box":
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        elif shape == "cone":
            bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=size[0], radius2=size[1], depth=size[2])
        ob = _mesh_obj("prop", bm); ob.data.materials.append(m)
        ob.location = (x + off[0] * s, y + off[1] * s, z + off[2] * s); ob.scale = (s, s, s); ob.rotation_euler = (math.radians(90) if face else 0, rot, 0)


def bg_camera(width_u, height_u, px_per_u, center_z):
    s = bpy.context.scene
    s.render.resolution_x = int(width_u * px_per_u); s.render.resolution_y = int(height_u * px_per_u)
    cd = bpy.data.cameras.new("bgcam"); cd.type = "ORTHO"; cd.ortho_scale = max(width_u, height_u)
    cd.clip_end = 500
    c = bpy.data.objects.new("bgcam", cd); s.collection.objects.link(c); s.camera = c
    c.location = (width_u / 2, -100, center_z); c.rotation_euler = (math.radians(90), 0, 0)
    return c
