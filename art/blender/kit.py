# Siegeline character kit — runs inside Blender 5.x (bpy).
# Chunky toy figures built from shared rounded parts, rigid parts parented to a pivot rig,
# toon 3-band shading with an inverted-hull outline, one fixed orthographic camera.
# A character file defines SPEC (dict) and calls build_and_animate(SPEC) at the bottom.
import bpy, bmesh, math
from mathutils import Vector, Matrix

PPU = 96            # pixels per world unit — same for every character so scale is consistent
ELEV = 8            # camera elevation in degrees (fixed for the whole cast)
ANIMS = [("idle", 6), ("walk", 8), ("attack", 8), ("hit", 4), ("die", 8)]  # order on the timeline
OUTLINE = (0.012, 0.008, 0.01, 1)


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
    # rim light from layer weight
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


def _finish(ob, color, glow=0.0, bevel=0.0, outline=0.022, flat=False):
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


def box(size, color, loc=(0, 0, 0), bevel=0.06, rot=(0, 0, 0), glow=0.0, name="box", taper=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        if taper is not None and v.co.z > 0:   # taper top face (x,y factors)
            v.co.x *= taper[0]; v.co.y *= taper[1]
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    ob = _mesh_obj(name, bm); ob.location = loc; ob.rotation_euler = rot
    return _finish(ob, color, glow, bevel=min(bevel, min(size) * 0.45), flat=True)


def ball(r, color, loc=(0, 0, 0), scale=(1, 1, 1), glow=0.0, name="ball", seg=16):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    ob = _mesh_obj(name, bm); ob.location = loc
    return _finish(ob, color, glow)


def cyl(r, h, color, loc=(0, 0, 0), rot=(0, 0, 0), r2=None, seg=12, glow=0.0, name="cyl", bevel=0.02):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    ob = _mesh_obj(name, bm); ob.location = loc; ob.rotation_euler = rot
    return _finish(ob, color, glow, bevel=bevel)


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


# ---------------------------------------------------------------- humanoid builder
def humanoid(spec):
    """Toy humanoid: big head, short legs. Faces +X. Near side is -Y (camera side)."""
    sc = spec.get("scale", 1.0)
    C = spec["colors"]
    hip_h = 0.62 * sc * spec.get("leg", 1.0)
    torso_h = 0.62 * sc * spec.get("torso", 1.0)
    bw = 0.52 * sc * spec.get("bulk", 1.0)
    head_r = 0.36 * sc * spec.get("head", 1.0)
    rig = {}
    root = empty("root"); rig["root"] = root
    hips = empty("hips", (0, 0, hip_h), root); rig["hips"] = hips
    bpy.context.view_layer.update()
    # legs (pivot at hip joint)
    for side, y in (("L", 0.13 * sc), ("R", -0.13 * sc)):
        lp = empty("leg_" + side, (0, y, hip_h), root); rig["leg_" + side] = lp
        bpy.context.view_layer.update()
        attach(box((0.2 * sc, 0.2 * sc, hip_h * 0.75), C["legs"], (0, y, hip_h * 0.55), name="thigh"), lp)
        attach(box((0.3 * sc, 0.24 * sc, 0.16 * sc), C.get("boots", C["legs"]), (0.04 * sc, y, 0.08 * sc), name="boot"), lp)
    # torso
    tp = empty("torso", (0, 0, hip_h), hips); rig["torso"] = tp
    bpy.context.view_layer.update()
    attach(box((bw * 0.82, bw * 0.72, torso_h), C["body"], (0, 0, hip_h + torso_h * 0.5),
               taper=spec.get("taper", (1.15, 1.05)), name="chest"), tp)
    attach(box((bw * 0.86, bw * 0.76, 0.14 * sc), C.get("belt", C["legs"]), (0, 0, hip_h + 0.05 * sc), name="belt"), tp)
    shoulder_z = hip_h + torso_h * 0.88
    # head
    hp = empty("head", (0, 0, shoulder_z + 0.05 * sc), tp); rig["head"] = hp
    bpy.context.view_layer.update()
    hz = shoulder_z + head_r * 1.05
    attach(ball(head_r, C["skin"], (0.02 * sc, 0, hz), scale=(0.95, 0.95, 1.0), name="headball"), hp)
    rig["head_z"] = hz; rig["head_r"] = head_r
    # eyes
    for ey in (-0.12, 0.12):
        attach(ball(0.055 * sc, C.get("eyes", (0.05, 0.05, 0.05)), (head_r * 0.85 + 0.02 * sc, ey * sc * spec.get("head", 1.0), hz + 0.03 * sc),
                    scale=(0.6, 1, 1.3), glow=C.get("eye_glow", 0.0), name="eye"), hp)
    # arms (pivot at shoulder)
    for side, y in (("L", bw * 0.48), ("R", -bw * 0.48)):
        ap = empty("arm_" + side, (0, y, shoulder_z), tp); rig["arm_" + side] = ap
        bpy.context.view_layer.update()
        al = torso_h * 0.95
        attach(box((0.17 * sc, 0.17 * sc, al), C.get("arms", C["body"]), (0, y, shoulder_z - al * 0.45), name="arm"), ap)
        attach(ball(0.1 * sc, C.get("hands", C["skin"]), (0, y, shoulder_z - al * 0.98), name="hand"), ap)
        hand = empty("hand_" + side, (0, y, shoulder_z - al * 0.98), ap); rig["hand_" + side] = hand
        if spec.get("pauldrons"):
            attach(ball(0.17 * sc, C["trim"], (0, y, shoulder_z - 0.02 * sc), scale=(1.1, 1, 0.75), name="pauldron"), ap)
    rig["sc"] = sc; rig["shoulder_z"] = shoulder_z; rig["hip_h"] = hip_h; rig["bw"] = bw
    return rig


# ---------------------------------------------------------------- props
GRIP = dict(sword=75, axe=70, hammer=70, spear=88, harpoon=88, bow=90, staff=60, lantern=0, claws=0)


def weapon(kind, rig, C, side="R"):
    sc = rig["sc"]; hand = rig["hand_" + side]; p = hand.matrix_world.translation.copy()
    x, y, z = p.x, p.y, p.z
    h = empty("grip_" + side, (x, y, z))   # built upright around the grip, tilted after
    if kind in ("axe", "hammer", "spear", "harpoon", "staff"):
        z = z - 0.25 * sc                   # hold the shaft a little above its butt
    if kind == "sword":
        attach(box((0.07 * sc, 0.05 * sc, 0.9 * sc), C["metal"], (x + 0.05 * sc, y - 0.04, z + 0.5 * sc), name="blade", bevel=0.02), h)
        attach(box((0.3 * sc, 0.08 * sc, 0.06 * sc), C["trim"], (x + 0.05 * sc, y - 0.04, z + 0.05 * sc), name="guard"), h)
    elif kind == "axe":
        attach(cyl(0.035 * sc, 1.1 * sc, C["wood"], (x + 0.04, y - 0.04, z + 0.3 * sc)), h)
        attach(box((0.34 * sc, 0.05 * sc, 0.32 * sc), C["metal"], (x + 0.2 * sc, y - 0.04, z + 0.72 * sc), name="axehead", taper=(1.6, 1)), h)
    elif kind == "spear":
        attach(cyl(0.03 * sc, 1.7 * sc, C["wood"], (x + 0.02, y - 0.04, z + 0.35 * sc)), h)
        attach(cyl(0.07 * sc, 0.28 * sc, C["metal"], (x + 0.02, y - 0.04, z + 1.32 * sc), r2=0.0), h)
    elif kind == "bow":
        attach(cyl(0.03 * sc, 1.1 * sc, C["wood"], (x + 0.1 * sc, y - 0.05, z), rot=(0, 0, 0)), h)
    elif kind == "hammer":
        attach(cyl(0.04 * sc, 1.0 * sc, C["wood"], (x + 0.03, y - 0.04, z + 0.3 * sc)), h)
        attach(box((0.42 * sc, 0.26 * sc, 0.26 * sc), C["metal"], (x + 0.03, y - 0.04, z + 0.82 * sc), name="hammerhead"), h)
    elif kind == "lantern":
        attach(cyl(0.02 * sc, 0.25 * sc, C["metal"], (x, y - 0.03, z - 0.12 * sc)), h)
        attach(box((0.2 * sc, 0.2 * sc, 0.26 * sc), C["metal"], (x, y - 0.03, z - 0.32 * sc), name="lanternbox"), h)
        attach(ball(0.09 * sc, C["flame"], (x, y - 0.03, z - 0.32 * sc), glow=1.5, name="flame"), h)
    elif kind == "staff":
        attach(cyl(0.035 * sc, 1.6 * sc, C["wood"], (x + 0.02, y - 0.04, z + 0.25 * sc)), h)
        attach(ball(0.12 * sc, C["flame"], (x + 0.02, y - 0.04, z + 1.08 * sc), glow=1.5, name="orb"), h)
    elif kind == "claws":
        for dz in (0, 0.07, 0.14):
            attach(cyl(0.03 * sc, 0.3 * sc, C["bone"], (x + 0.14 * sc, y - 0.02, z - 0.05 * sc + dz), rot=(0, math.radians(100), 0), r2=0.0), h)
    elif kind == "flail":
        attach(cyl(0.035 * sc, 0.6 * sc, C["wood"], (x, y - 0.04, z + 0.2 * sc)), h)
        attach(ball(0.16 * sc, C["metal"], (x, y - 0.04, z + 0.62 * sc), name="flailhead", seg=8), h)
    elif kind == "harpoon":
        attach(cyl(0.03 * sc, 1.5 * sc, C["wood"], (x + 0.02, y - 0.04, z + 0.3 * sc)), h)
        attach(cyl(0.08 * sc, 0.22 * sc, C["metal"], (x + 0.02, y - 0.04, z + 1.15 * sc), r2=0.0), h)
        attach(box((0.2 * sc, 0.03 * sc, 0.04 * sc), C["metal"], (x + 0.02, y - 0.04, z + 1.06 * sc), rot=(0, 0.5, 0)), h)
    h.rotation_euler = (0, math.radians(GRIP.get(kind, 0)), 0)
    bpy.context.view_layer.update()
    h.parent = hand
    h.matrix_parent_inverse = hand.matrix_world.inverted()


def shield(rig, C, side="L", shape="round"):
    sc = rig["sc"]; h = rig["hand_" + side]; p = h.matrix_world.translation
    if shape == "round":
        attach(cyl(0.38 * sc, 0.08 * sc, C["shield"], (p.x + 0.16 * sc, p.y + 0.0, p.z + 0.1 * sc), rot=(0, math.radians(90), 0), seg=16), h)
        attach(ball(0.08 * sc, C["trim"], (p.x + 0.21 * sc, p.y, p.z + 0.1 * sc), name="boss"), h)
    else:
        attach(box((0.1 * sc, 0.55 * sc, 0.8 * sc), C["shield"], (p.x + 0.18 * sc, p.y, p.z + 0.12 * sc), name="tower"), h)
        attach(box((0.12 * sc, 0.12 * sc, 0.62 * sc), C["trim"], (p.x + 0.2 * sc, p.y, p.z + 0.12 * sc), name="stripe"), h)


def helmet(rig, C, kind):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]
    if kind == "kettle":
        attach(cyl(r * 1.35, 0.06 * sc, C["metal"], (0, 0, hz + r * 0.35), seg=16), hp)
        attach(ball(r * 1.02, C["metal"], (0, 0, hz + r * 0.3), scale=(1, 1, 0.7), name="dome"), hp)
    elif kind == "great":
        attach(box((r * 1.75, r * 1.7, r * 1.85), C["metal"], (0.01, 0, hz + 0.02), name="greathelm", bevel=0.08), hp)
        attach(box((0.04, r * 1.4, 0.06 * sc), (0.03, 0.03, 0.03), (r * 0.9, 0, hz + 0.05 * sc), name="visor", bevel=0.0), hp)
    elif kind == "hood":
        attach(ball(r * 1.12, C["cloth"], (-0.04 * sc, 0, hz + 0.04 * sc), scale=(1.05, 1.0, 1.08), name="hood"), hp)
    elif kind == "horns":
        for y in (-r * 0.7, r * 0.7):
            attach(cyl(0.07 * sc, 0.4 * sc, C["bone"], (-0.05, y, hz + r * 0.9), rot=(math.radians(-25 if y < 0 else 25), math.radians(-30), 0), r2=0.0), hp)
    elif kind == "crown":
        for i in range(5):
            a = i / 5 * math.tau
            attach(cyl(0.04 * sc, 0.22 * sc, C["trim"], (math.cos(a) * r * 0.75, math.sin(a) * r * 0.75, hz + r * 0.95), r2=0.0, seg=6), hp)
    elif kind == "tricorn":
        attach(cyl(r * 1.3, 0.12 * sc, C["cloth"], (0, 0, hz + r * 0.55), seg=3, rot=(0, 0, math.radians(30))), hp)
    elif kind == "sunhat":
        attach(cyl(r * 1.7, 0.05 * sc, C["cloth"], (0, 0, hz + r * 0.45), seg=16), hp)
        attach(cyl(r * 0.8, 0.32 * sc, C["cloth"], (0, 0, hz + r * 0.6), r2=0.0, seg=16), hp)


def cape(rig, C):
    sc = rig["sc"]; tp = rig["torso"]; z = rig["shoulder_z"]
    attach(box((0.08 * sc, rig["bw"] * 0.9, 0.95 * sc), C["cloth"], (-rig["bw"] * 0.45, 0, z - 0.45 * sc), name="cape", taper=(1, 0.8)), tp)


# ---------------------------------------------------------------- animation
def key(ob, frame, rot=None, loc=None):
    if rot is not None:
        ob.rotation_euler = rot; ob.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        ob.location = loc; ob.keyframe_insert("location", frame=frame)


def pose(rig, f, t, anim, style):
    """Key one frame. t in [0,1). Rotations around Y swing limbs forward/back (toward +X)."""
    R, H, T, Hd = rig["root"], rig["hips"], rig["torso"], rig["head"]
    aL, aR, lL, lR = rig["arm_L"], rig["arm_R"], rig["leg_L"], rig["leg_R"]
    fc = rig.get("facing", 1)
    hb = Vector(rig["hips_base"]); s = math.sin(t * math.tau); c = math.cos(t * math.tau)
    rad = math.radians
    heavy = style.get("heavy", 1.0)
    lean = style.get("lean", 0)
    if anim == "idle":
        key(R, f, (0, 0, 0), (0, 0, 0)); key(H, f, (0, 0, 0), hb + Vector((0, 0, 0.015 * s)))
        key(T, f, (0, rad(lean + 2 * s), 0)); key(Hd, f, (0, rad(-2 * s), 0))
        key(aR, f, (0, rad(-15 + 4 * s), 0)); key(aL, f, (0, rad(10 - 4 * s), 0))
        key(lL, f, (0, 0, 0)); key(lR, f, (0, 0, 0))
    elif anim == "walk":
        sw = 32 / heavy
        key(R, f, (0, 0, 0), (0, 0, 0)); key(H, f, (0, 0, 0), hb + Vector((0, 0, 0.045 * abs(c))))
        key(T, f, (0, rad(lean + 6), 0)); key(Hd, f, (0, rad(-4), 0))
        key(lL, f, (0, rad(-sw * s), 0)); key(lR, f, (0, rad(sw * s), 0))
        key(aL, f, (0, rad(sw * 0.8 * s), 0)); key(aR, f, (0, rad(-20 - sw * 0.5 * s), 0))
    elif anim == "attack":
        # wind-up (0-0.4), strike (0.4-0.6), recover
        if style.get("attack") == "thrust":
            a = 18 if t < 0.4 else (-28 if t < 0.65 else -28 + (t - 0.65) / 0.35 * 28)
            lunge = 0.0 if t < 0.4 else (0.18 if t < 0.65 else 0.18 * (1 - (t - 0.65) / 0.35))
            key(aR, f, (0, rad(a), 0)); key(T, f, (0, rad(lean + 12 * (lunge > 0)), 0))
            key(R, f, (0, 0, 0), (lunge * fc, 0, 0))
        elif style.get("attack") == "shoot":
            a = -80; key(aR, f, (0, rad(a), 0)); key(aL, f, (0, rad(-85 + (8 if 0.4 < t < 0.6 else 0)), 0))
            key(T, f, (0, rad(lean - (6 if 0.4 < t < 0.55 else 0)), 0)); key(R, f, (0, 0, 0), (-0.04 * fc if 0.4 < t < 0.6 else 0, 0, 0))
        elif style.get("attack") == "cast":
            up = math.sin(min(t / 0.5, 1) * math.pi / 2)
            key(aR, f, (0, rad(-40 - 120 * up if t < 0.6 else -160 + (t - 0.6) / 0.4 * 145), 0))
            key(aL, f, (0, rad(-30 - 60 * up), 0)); key(T, f, (0, rad(lean - 8 * up), 0)); key(R, f, (0, 0, 0), (0, 0, 0))
        else:  # swing overhead
            if t < 0.4:
                a = -60 - (t / 0.4) * 110          # raise back
            elif t < 0.6:
                a = -170 + ((t - 0.4) / 0.2) * 210  # chop down
            else:
                a = 40 - ((t - 0.6) / 0.4) * 55
            key(aR, f, (0, rad(a), 0)); key(T, f, (0, rad(lean + (-10 if t < 0.4 else 18 if t < 0.7 else 6)), 0))
            key(R, f, (0, 0, 0), (0.08 * fc if 0.4 <= t < 0.7 else 0, 0, 0))
            key(aL, f, (0, rad(15), 0))
        key(H, f, (0, 0, 0), hb); key(lL, f, (0, rad(18), 0)); key(lR, f, (0, rad(-18), 0)); key(Hd, f, (0, 0, 0))
    elif anim == "hit":
        k = math.sin(t * math.pi)
        key(R, f, (0, 0, 0), (-0.12 * k * fc, 0, 0)); key(H, f, (0, 0, 0), hb)
        key(T, f, (0, rad(lean - 22 * k), 0)); key(Hd, f, (0, rad(-15 * k), 0))
        key(aR, f, (0, rad(30 * k), 0)); key(aL, f, (0, rad(35 * k), 0)); key(lL, f, (0, 0, 0)); key(lR, f, (0, 0, 0))
    elif anim == "die":
        k = min(t / 0.75, 1.0); k = k * k * (3 - 2 * k)
        key(R, f, (0, rad(-88 * k * fc), 0), (0.95 * rig["sc"] * k * fc, 0, 0.3 * k + 0.25 * math.sin(k * math.pi) * 0.4))
        key(H, f, (0, 0, 0), hb); key(T, f, (0, rad(-15 * k), 0)); key(Hd, f, (0, rad(-25 * k), 0))
        key(aR, f, (0, rad(60 * k), 0)); key(aL, f, (0, rad(80 * k), 0)); key(lL, f, (0, rad(20 * k), 0)); key(lR, f, (0, rad(-10 * k), 0))


def animate(rig, style):
    rig["hips_base"] = tuple(rig["hips"].location)
    f = 1
    for name, n in ANIMS:
        for i in range(n):
            pose(rig, f, i / n, name, style)
            f += 1
    for ob in bpy.data.objects:
        if ob.animation_data and ob.animation_data.action:
            for fc in _fcurves(ob.animation_data.action):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = f - 1


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


# ---------------------------------------------------------------- camera + light
def stage(cell=(320, 320), center_z=None, facing=1, cam_x=0.0):
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = cell
    s.render.resolution_percentage = 100
    ortho = max(cell) / PPU
    cam_d = bpy.data.cameras.new("cam"); cam_d.type = "ORTHO"; cam_d.ortho_scale = ortho
    cam = bpy.data.objects.new("cam", cam_d); s.collection.objects.link(cam); s.camera = cam
    h_units = cell[1] / PPU
    cz = center_z if center_z is not None else h_units / 2 - 0.25   # ground 0.25u above bottom edge
    e = math.radians(ELEV)
    cam.location = (cam_x, -30 * math.cos(e), cz + 30 * math.sin(e))
    cam.rotation_euler = (math.radians(90) - e, 0, 0)
    # key light upper-left-front, soft fill from right, all fixed
    sun = bpy.data.lights.new("key", "SUN"); sun.energy = 3.2; sun.angle = math.radians(8)
    so = bpy.data.objects.new("key", sun); s.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(-35 * facing), math.radians(-20))
    fill = bpy.data.lights.new("fill", "SUN"); fill.energy = 0.8
    fo = bpy.data.objects.new("fill", fill); s.collection.objects.link(fo)
    fo.rotation_euler = (math.radians(70), math.radians(60), math.radians(30))
    return cam


def build_and_animate(spec):
    reset()
    rig = spec["builder"](spec) if "builder" in spec else humanoid(spec)
    C = spec["colors"]
    if spec.get("helmet"):
        helmet(rig, C, spec["helmet"])
    if spec.get("cape"):
        cape(rig, C)
    if spec.get("weapon"):
        weapon(spec["weapon"], rig, C, "R")
    if spec.get("offhand"):
        weapon(spec["offhand"], rig, C, "L")
    if spec.get("shield"):
        shield(rig, C, "L", spec["shield"])
    if spec.get("extra"):
        spec["extra"](rig, C)
    if spec.get("facing", 1) < 0:      # enemies face left: mirror around the root
        rig["root"].scale = (-1, 1, 1)
    rig["facing"] = spec.get("facing", 1)
    animate(rig, spec.get("style", {}))
    stage(tuple(spec.get("cell", (320, 320))), facing=spec.get("facing", 1))
    return rig


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
