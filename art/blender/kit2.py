from kit import *
# kit2 — carved-figure kit (docs/design/art-direction.md). Bundled after kit.py; reuses its grid render.
# A figure is a tree of pivots (empties) with lofted, painted parts. Limbs have two bones. Lighting is
# computed in the shader from fixed world directions: warm key from the right (the sunset), cool fill from
# the upper left, orange rim from behind. Crew face the key; mirrored monsters have it at their backs.
# A spec with spec["v2"] = make(fig) is built by place() through build_v2().

KEY_DIR = Vector((0.80, -0.42, 0.42)).normalized()
FILL_DIR = Vector((-0.55, -0.60, 0.58)).normalized()
RIM_DIR = Vector((0.62, 0.74, 0.26)).normalized()
INK_CREW = (0.133, 0.082, 0.169)
INK_DEEP = (0.047, 0.102, 0.118)

V2 = dict(
    navy=(0.153, 0.271, 0.431), navy_dk=(0.10, 0.17, 0.30), red=(0.76, 0.227, 0.18), canvas=(0.918, 0.875, 0.769),
    brass=(0.878, 0.663, 0.231), tar=(0.165, 0.141, 0.125), wood=(0.52, 0.36, 0.22), wood_dk=(0.36, 0.24, 0.15),
    iron=(0.34, 0.35, 0.40), steel=(0.80, 0.82, 0.86), skin=(0.87, 0.64, 0.49), skin_dk=(0.62, 0.42, 0.32),
    hair=(0.40, 0.24, 0.13), white=(0.96, 0.94, 0.88), leather=(0.42, 0.27, 0.17),
    teal=(0.184, 0.353, 0.361), deep=(0.09, 0.188, 0.227), bone=(0.847, 0.812, 0.71), ink=(0.227, 0.118, 0.29),
    glow=(0.49, 1.0, 0.66), kelp=(0.17, 0.30, 0.20), kelp_lt=(0.28, 0.42, 0.24), rag=(0.42, 0.44, 0.40),
    barn=(0.72, 0.70, 0.62), gold=(1.0, 0.82, 0.30), cursed=(0.72, 1.0, 0.45),
)


# ---------------------------------------------------------------- material
def paint(fig, color, glow=0.0, metal=False, rough=1.0):
    """Painted-carving material: 3 soft bands from the key light, plum shadows, cool fill, orange rim,
    a height gradient (darker at the feet) and a faint paint mottle. Emission only: what you set is what renders."""
    key = (tuple(round(c, 3) for c in color), glow, metal)
    if key in fig.mats:
        return fig.mats[key]
    c = lin(color)
    m = bpy.data.materials.new("p2"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    L.new(em.outputs[0], out.inputs[0])
    if glow >= 1.0:
        em.inputs[0].default_value = (*c, 1); em.inputs[1].default_value = 1.0 + 0.6 * (glow - 1)
        fig.mats[key] = m
        return m
    geo = N.new("ShaderNodeNewGeometry")

    def dot(vec, lo, hi):
        d = N.new("ShaderNodeVectorMath"); d.operation = "DOT_PRODUCT"; d.inputs[1].default_value = vec
        L.new(geo.outputs["Normal"], d.inputs[0])
        r = N.new("ShaderNodeMapRange"); r.interpolation_type = "SMOOTHSTEP"
        r.inputs[1].default_value = lo; r.inputs[2].default_value = hi
        L.new(d.outputs["Value"], r.inputs[0])
        return r.outputs[0]

    def mix(mode, fac, a, b):
        x = N.new("ShaderNodeMix"); x.data_type = "RGBA"; x.blend_type = mode
        for sock, v in ((x.inputs[0], fac), (x.inputs[6], a), (x.inputs[7], b)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            elif isinstance(v, tuple):
                sock.default_value = (*v[:3], 1)
            else:
                L.new(v, sock)
        return x.outputs[2]

    # paint mottle + height gradient in the figure's own space
    tc = N.new("ShaderNodeTexCoord"); tc.object = fig.root
    noise = N.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 2.0
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    nr = N.new("ShaderNodeMapRange"); nr.inputs[1].default_value = 0.3; nr.inputs[2].default_value = 0.7
    nr.inputs[3].default_value = 0.90; nr.inputs[4].default_value = 1.06
    L.new(noise.outputs[0], nr.inputs[0])
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    hr = N.new("ShaderNodeMapRange"); hr.inputs[1].default_value = 0.0; hr.inputs[2].default_value = fig.h * 0.7
    hr.inputs[3].default_value = 0.74; hr.inputs[4].default_value = 1.0
    L.new(sep.outputs["Z"], hr.inputs[0])
    val = N.new("ShaderNodeMath"); val.operation = "MULTIPLY"
    L.new(nr.outputs[0], val.inputs[0]); L.new(hr.outputs[0], val.inputs[1])
    vcol = N.new("ShaderNodeCombineXYZ")
    for i in range(3):
        L.new(val.outputs[0], vcol.inputs[i])
    base = mix("MULTIPLY", 1.0, c, vcol.outputs[0])

    shadow = mix("MULTIPLY", 1.0, base, lin((0.60, 0.50, 0.74)))        # plum, not black
    lit = mix("MULTIPLY", 1.0, base, (1.08, 1.0, 0.88))
    k1 = dot(KEY_DIR, -0.08, 0.10)                                       # shadow -> lit
    k2 = dot(KEY_DIR, 0.60, 0.72 if not metal else 0.64)                 # lit -> highlight
    col = mix("MIX", k1, shadow, lit)
    hi = mix("ADD", 0.16 if not metal else 0.55, col, lin((1.0, 0.86, 0.62)))
    col = mix("MIX", k2, col, hi)
    f = dot(FILL_DIR, 0.25, 0.9)
    fillc = mix("MULTIPLY", 1.0, base, lin((0.62, 0.66, 0.95)))
    fm = N.new("ShaderNodeMath"); fm.operation = "MULTIPLY"; fm.inputs[1].default_value = 0.30
    L.new(f, fm.inputs[0])
    col = mix("ADD", fm.outputs[0], col, fillc)
    # rim: faces turned away from the camera and toward the sun behind
    r = dot(RIM_DIR, 0.30, 0.52)
    rimc = lin((1.0, 0.60, 0.26))
    rm = N.new("ShaderNodeMath"); rm.operation = "MULTIPLY"; rm.inputs[1].default_value = 0.85 * rough * getattr(fig, "rim", 1.0)
    L.new(r, rm.inputs[0])
    col = mix("ADD", rm.outputs[0], col, rimc)
    if glow > 0:
        col = mix("MIX", min(glow, 0.95), col, c)
    L.new(col, em.inputs[0])
    fig.mats[key] = m
    return m


def ink_mat(fig):
    if "ink" in fig.mats:
        return fig.mats["ink"]
    m = bpy.data.materials.new("ink"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial"); e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*lin(fig.ink), 1)
    nt.links.new(e.outputs[0], o.inputs[0])
    m.use_backface_culling = True
    fig.mats["ink"] = m
    return m


# ---------------------------------------------------------------- figure
class Fig:
    def __init__(self, name, ink=INK_CREW, h=1.9, line=0.022):
        self.name = name; self.ink = ink; self.h = h; self.line = line
        self.mats = {}; self.J = {}; self.W = {}; self.sign = {}; self.rest = {}; self.L = {}; self.vis_default = {}
        self.root = self.joint("root", (0, 0, 0), None)
        self.tails = []          # (joint names chain, sway, phase)
        self.head_c = Vector((0, 0, h * 0.8))    # portrait centre; head builders overwrite it
        self.vis = {}            # name -> object shown/hidden by scale

    def joint(self, name, loc, parent, sign=1, rest=0.0):
        """Pivot at world position loc. sign: +1 for parts that stand up from the pivot, -1 for parts that hang;
        a positive pose angle then always means 'forward'. rest: built-in pitch (deg) added to every pose."""
        e = bpy.data.objects.new(self.name + "_" + name, None)
        bpy.context.scene.collection.objects.link(e)
        e.rotation_mode = "XYZ"; e.empty_display_size = 0.05
        loc = Vector(loc)
        if parent:
            p = self.J[parent]; e.parent = p
            e.location = loc - self.W[parent]
        else:
            e.location = loc
        self.L[name] = e.location.copy()
        self.J[name] = e; self.W[name] = loc; self.sign[name] = sign; self.rest[name] = rest
        return e

    def add(self, ob, joint, color=None, glow=0.0, metal=False, line=None, flat=False, rough=1.0):
        """Parent a part built in WORLD (rest pose) coordinates to a joint, give it paint + ink hull."""
        j = self.J[joint]
        ob.parent = j
        ob.matrix_parent_inverse = Matrix.Translation(-self.W[joint])
        if color is not None:
            ob.data.materials.append(paint(self, color, glow, metal, rough))
            ob.data.materials.append(ink_mat(self))
            for p in ob.data.polygons:
                p.use_smooth = not flat
            ln = self.line if line is None else line
            if ln > 0 and glow < 1.0:
                s = ob.modifiers.new("ol", "SOLIDIFY"); s.thickness = ln; s.offset = 1
                s.use_flip_normals = True; s.material_offset = 1; s.use_rim = False
        return ob


def _obj(name, bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def loft(rings, seg=12, name="loft", round_=(True, True), axis="z", at=(0, 0, 0), rot=None, sq=0.0):
    """Skin through oval rings [(u, ra, rb, da, db)] along an axis. ra = half-size front/back, rb = half-size
    sideways, (da, db) optional centre offsets. Ends are rounded off. sq > 0 squares the ovals (carved look)."""
    rr = []
    for r in rings:
        u, ra, rb = r[0], r[1], r[2]
        da = r[3] if len(r) > 3 else 0.0; db = r[4] if len(r) > 4 else 0.0
        rr.append((u, ra, rb, da, db))
    if round_[0]:
        u, ra, rb, da, db = rr[0]; d = rr[1][0] - u; s = -1 if d > 0 else 1
        rr.insert(0, (u + s * min(ra, rb) * 0.45, ra * 0.62, rb * 0.62, da, db))
        rr.insert(0, (u + s * min(ra, rb) * 0.62, ra * 0.2, rb * 0.2, da, db))
    if round_[1]:
        u, ra, rb, da, db = rr[-1]; d = u - rr[-2][0]; s = 1 if d > 0 else -1
        rr.append((u + s * min(ra, rb) * 0.45, ra * 0.62, rb * 0.62, da, db))
        rr.append((u + s * min(ra, rb) * 0.62, ra * 0.2, rb * 0.2, da, db))
    bm = bmesh.new(); loops = []
    for (u, ra, rb, da, db) in rr:
        lp = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ca, sa = math.cos(a), math.sin(a)
            if sq > 0:   # superellipse
                e = 1.0 - sq * 0.6
                ca = math.copysign(abs(ca) ** e, ca); sa = math.copysign(abs(sa) ** e, sa)
            p = (da + ra * ca, db + rb * sa, u)
            if axis == "x":
                p = (u, db + rb * sa, da + ra * ca)
            elif axis == "y":
                p = (da + ra * ca, u, db + rb * sa)
            lp.append(bm.verts.new(p))
        loops.append(lp)
    for i in range(len(loops) - 1):
        for j in range(seg):
            bm.faces.new((loops[i][j], loops[i][(j + 1) % seg], loops[i + 1][(j + 1) % seg], loops[i + 1][j]))
    bm.faces.new(loops[0]); bm.faces.new(loops[-1])
    if rot is not None:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(rot[0]), 3, rot[1]))
    bmesh.ops.translate(bm, verts=bm.verts, vec=at)
    return _obj(name, bm)


def slab(points, depth, name="slab", at=(0, 0, 0), yaw=0.0, bevel=0.0, plane="xz"):
    """Outline polygon extruded to a thick plate. plane 'xz' faces the camera, 'yz' faces forward."""
    bm = bmesh.new()
    if plane == "xz":
        fr = [bm.verts.new((x, -depth / 2, z)) for x, z in points]; bk = [bm.verts.new((x, depth / 2, z)) for x, z in points]
    else:
        fr = [bm.verts.new((depth / 2, y, z)) for y, z in points]; bk = [bm.verts.new((-depth / 2, y, z)) for y, z in points]
    bm.faces.new(fr); bm.faces.new(list(reversed(bk)))
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((fr[i], fr[j], bk[j], bk[i]))
    if yaw:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(yaw), 3, "Z"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=at)
    ob = _obj(name, bm)
    if bevel > 0:
        b = ob.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"
    return ob


def orb(r, at, scale=(1, 1, 1), seg=14, name="orb"):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0] + at[0], v.co.y * scale[1] + at[1], v.co.z * scale[2] + at[2]))
    return _obj(name, bm)


def cone(p0, p1, r0, r1=0.0, seg=7, name="cone"):
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r0, radius2=max(r1, 1e-4), depth=max(d.length, 1e-4))
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix()
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=q)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(p0 + p1) / 2)
    return _obj(name, bm)


def block(size, at, rot=None, bevel=0.03, name="block", taper=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        if taper and v.co.z > 0:
            v.co.x *= taper[0]; v.co.y *= taper[1]
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if rot is not None:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(rot[0]), 3, rot[1]))
    bmesh.ops.translate(bm, verts=bm.verts, vec=at)
    ob = _obj(name, bm)
    if bevel > 0:
        b = ob.modifiers.new("bev", "BEVEL"); b.width = min(bevel, min(size) * 0.45); b.segments = 2; b.limit_method = "NONE"
    return ob


# ---------------------------------------------------------------- body
def body(fig, P, C):
    """Two-bone-limb humanoid. P: proportions, C: colours. Faces +X, near side -Y. Returns nothing; fills fig.J."""
    g = P.get
    hip = g("hip", 0.62); ch_h = g("chest_h", 0.66); wy = g("wy", 0.36); wx = g("wx", 0.27)
    sh_w = g("shoulder", 0.42); head_r = g("head_r", 0.30); lean = g("lean", 0.0)
    fig.joint("hips", (0, 0, hip), "root", 1)
    fig.joint("chest", (0, 0, hip + 0.06), "hips", 1, rest=lean)
    sh_z = hip + ch_h * 0.92
    neck = (g("neck_x", 0.02), 0, hip + ch_h)
    fig.joint("head", neck, "chest", 1, rest=g("head_rest", -lean * 0.7))
    # pelvis + belt
    fig.add(loft([(hip - 0.14, wx * 0.80, wy * 0.84), (hip + 0.02, wx * 0.95, wy * 0.95), (hip + 0.12, wx * 0.9, wy * 0.9)],
                 name="pelvis", sq=0.3), "hips", C["legs"])
    if C.get("belt"):
        fig.add(loft([(hip + 0.03, wx * 1.02, wy * 1.02), (hip + 0.15, wx * 1.0, wy * 1.0)], name="belt", sq=0.3,
                     round_=(False, False)), "hips", C["belt"])
    # chest: barrel that widens to the shoulders
    belly = g("belly", 1.0); cx = g("chest_x", 0.03)
    fig.add(loft([(hip + 0.10, wx * 0.92 * belly, wy * 0.92), (hip + ch_h * 0.38, wx * 1.05 * belly, wy * 1.02, cx * 0.5),
                  (hip + ch_h * 0.70, wx * 1.12, wy * 1.18, cx), (hip + ch_h * 0.93, wx * 0.86, wy * 1.10, cx * 0.6)],
                 name="chest", sq=0.35), "chest", C["body"])
    # limbs
    ua = g("upper_arm", 0.32); la = g("lower_arm", 0.30); ar = g("arm_r", 0.115)
    th = g("thigh", 0.27); sn = g("shin", 0.25); lr = g("leg_r", 0.14)
    for s, y in (("L", 1), ("R", -1)):
        k = g("arm_k", {}).get(s, 1.0)
        sy = y * sh_w; sz = sh_z + g("sh_up", {}).get(s, 0.0)
        fig.joint("ua" + s, (0, sy, sz), "chest", -1)
        fig.joint("la" + s, (0, sy, sz - ua * k), "ua" + s, -1)
        fig.joint("hand" + s, (0, sy, sz - (ua + la) * k), "la" + s, -1)
        fig.add(orb(ar * 1.25 * k, (0, sy, sz), (1, 1, 0.95), name="shoulder"), "ua" + s, C.get("sleeve", C["body"]))
        fig.add(loft([(sz, ar * 1.1 * k, ar * 1.1 * k), (sz - ua * k, ar * 0.92 * k, ar * 0.92 * k)], seg=9, at=(0, sy, 0),
                     name="uarm"), "ua" + s, C.get("sleeve", C["body"]))
        fig.add(loft([(sz - ua * k, ar * 1.0 * k, ar * 1.0 * k), (sz - ua * k - la * k * 0.55, ar * 1.08 * k, ar * 1.05 * k),
                      (sz - (ua + la) * k, ar * 0.78 * k, ar * 0.78 * k)], seg=9, at=(0, sy, 0), name="larm"), "la" + s, C.get("arm", C["skin"]))
        hy = y * g("hip_w", 0.17)
        fig.joint("th" + s, (0, hy, hip - 0.04), "hips", -1)
        fig.joint("sn" + s, (0, hy, hip - 0.04 - th), "th" + s, -1)
        fig.joint("ft" + s, (0, hy, hip - 0.04 - th - sn), "sn" + s, -1)
        fig.add(loft([(hip - 0.02, lr * 1.12, lr * 1.12), (hip - 0.04 - th, lr * 0.9, lr * 0.9)], seg=9, at=(0, hy, 0), name="thigh", sq=0.2),
                "th" + s, C["legs"])
        fig.add(loft([(hip - 0.04 - th, lr * 0.92, lr * 0.92), (hip - 0.04 - th - sn, lr * g("ankle", 0.78), lr * g("ankle", 0.78))],
                     seg=9, at=(0, hy, 0), name="shin", sq=0.2), "sn" + s, C.get("shin", C["legs"]))
    fig.P = P; fig.C = C; fig.sh_z = sh_z; fig.neck = Vector(neck); fig.head_r = head_r; fig.hip = hip
    fig.hand_z = sh_z - (ua + la); fig.ft_z = hip - 0.04 - th - sn; fig.sh_w = sh_w; fig.hip_w = g("hip_w", 0.17)


def fists(fig, C, size=0.13, claws=False):
    for s, y in (("L", 1), ("R", -1)):
        k = fig.P.get("arm_k", {}).get(s, 1.0)
        p = fig.W["hand" + s]; r = size * k
        fig.add(orb(r, (p.x + 0.01, p.y, p.z - r * 0.55), (1.0, 0.9, 1.1), seg=10, name="fist"), "hand" + s, C.get("hand", C["skin"]))
        if claws:
            for i, (dx, dy) in enumerate(((0.9, -0.6), (1.0, 0.0), (0.9, 0.6))):
                b = Vector((p.x + r * 0.45 * dx, p.y + r * 0.7 * dy, p.z - r * 1.1))
                t = b + Vector((r * 1.1 * dx, r * 0.5 * dy, -r * 1.9))
                fig.add(cone(b, t, r * 0.34, 0.0, seg=6, name="claw"), "hand" + s, C["claw"], line=0.014)
        else:
            fig.add(orb(r * 0.45, (p.x + r * 0.75, p.y - y * r * 0.3, p.z - r * 0.35), seg=8, name="thumb"), "hand" + s, C.get("hand", C["skin"]), line=0.012)


def boots(fig, C, length=0.36, h=0.2, cuff=True):
    for s in ("L", "R"):
        p = fig.W["ft" + s]
        fig.add(loft([(-0.11, h * 0.62, 0.115, h * 0.62), (0.05, h * 0.60, 0.125, h * 0.60), (length * 0.55, h * 0.42, 0.13, h * 0.42),
                      (length - 0.11, h * 0.30, 0.11, h * 0.30)], seg=10, axis="x", at=(p.x, p.y, 0), name="boot", sq=0.4),
                "ft" + s, C["boots"])
        if cuff:
            fig.add(loft([(p.z + 0.10, 0.135, 0.135), (p.z - 0.02, 0.118, 0.118)], seg=10, at=(p.x, p.y, 0), name="cuff", round_=(False, False)),
                    "sn" + s, C.get("cuff", C["boots"]))


def bare_feet(fig, C, length=0.34):
    for s in ("L", "R"):
        p = fig.W["ft" + s]
        fig.add(loft([(-0.08, 0.07, 0.08, 0.07), (0.06, 0.065, 0.10, 0.065), (length - 0.08, 0.035, 0.14, 0.035)], seg=8, axis="x",
                     at=(p.x, p.y, 0), name="foot", sq=0.2), "ft" + s, C["skin"])
        for i in (-1, 0, 1):
            fig.add(cone((p.x + length - 0.10, p.y + i * 0.08, 0.035), (p.x + length + 0.04, p.y + i * 0.11, 0.0), 0.035, 0.0, seg=5),
                    "ft" + s, C["claw"], line=0.012)


def head_crew(fig, C, brow=(0.24, 0.13, 0.08), beard=None, nose=1.0, jaw=1.0):
    """Carved head: skull, jutting jaw, big nose, eye whites with pupils, heavy brow, ear. Mouth shapes switchable."""
    n = fig.neck; r = fig.head_r; cz = n.z + r * 0.92; cx = n.x + 0.03
    fig.add(loft([(cz - r * 0.95, r * 0.70 * jaw, r * 0.72 * jaw, 0.05), (cz - r * 0.35, r * 0.98, r * 0.96, 0.03), (cz + r * 0.30, r * 1.0, r * 1.0),
                  (cz + r * 0.80, r * 0.72, r * 0.74, -0.02)], seg=14, at=(cx, 0, 0), name="skull", sq=0.15), "head", C["skin"])
    fig.add(loft([(n.z - 0.06, 0.12, 0.13), (n.z + 0.08, 0.11, 0.12)], seg=8, at=(n.x, 0, 0), name="neck", round_=(False, False)), "head", C["skin"], line=0)
    ex = cx + r * 0.90
    fig.add(orb(r * 0.26 * nose, (ex + r * 0.12, 0, cz - r * 0.12), (1.15, 0.85, 0.9), seg=10, name="nose"), "head", C.get("nose", C["skin"]), line=0.012)
    for y in (-1, 1):
        fig.add(orb(r * 0.27, (ex - r * 0.12, y * r * 0.40, cz + r * 0.14), (0.5, 0.9, 1.05), seg=10, name="eyewhite"), "head", V2["white"], glow=0.7, line=0.01)
        fig.add(orb(r * 0.135, (ex + r * 0.0, y * r * 0.40 - 0.01, cz + r * 0.11), (0.5, 1, 1.1), seg=8, name="pupil"), "head", (0.07, 0.05, 0.06), glow=0.9, line=0)
        fig.add(orb(r * 0.2, (cx - r * 0.05, y * r * 0.98, cz - r * 0.02), (0.7, 0.4, 1.0), seg=8, name="ear"), "head", C["skin"], line=0.012)
    # brow: one dark bar across both eyes, pivots for expression
    fig.joint("brow", (ex - r * 0.05, 0, cz + r * 0.36), "head", 1)
    fig.add(block((r * 0.32, r * 1.3, r * 0.2), (ex - r * 0.08, 0, cz + r * 0.44), rot=(-12, "Y"), bevel=0.02, name="brow"), "brow", brow, line=0.008)
    if beard:
        fig.add(loft([(cz - r * 1.30, r * 0.26, r * 0.32, 0.16), (cz - r * 0.95, r * 0.62, r * 0.70, 0.12), (cz - r * 0.56, r * 0.86, r * 0.97, 0.09),
                      (cz - r * 0.40, r * 0.80, r * 0.98, 0.06)], seg=12, at=(cx, 0, 0), name="beard", sq=0.2, round_=(True, False)), "head", beard)
        fig.add(orb(r * 0.2, (ex + r * 0.02, 0, cz - r * 0.36), (0.7, 1.6, 0.55), seg=8, name="tache"), "head", beard, line=0.01)
    # mouths: shut line and open shout (shown by scale)
    fig.joint("m_shut", (ex + r * 0.03, 0, cz - r * 0.52), "head", 1); fig.joint("m_open", (ex + r * 0.03, 0, cz - r * 0.56), "head", 1)
    fig.add(block((r * 0.10, r * 0.50, r * 0.07), (ex + r * 0.05, 0, cz - r * 0.52), bevel=0.01, name="mshut"), "m_shut", (0.20, 0.08, 0.08), glow=0.9, line=0)
    fig.add(orb(r * 0.25, (ex + r * 0.02, 0, cz - r * 0.58), (0.5, 1.15, 1.0), seg=10, name="mopen"), "m_open", (0.22, 0.06, 0.07), glow=0.9, line=0.012)
    fig.add(block((r * 0.08, r * 0.36, r * 0.09), (ex + r * 0.11, 0, cz - r * 0.47), bevel=0.01, name="teeth"), "m_open", V2["white"], glow=0.8, line=0)
    fig.vis["m_shut"] = fig.J["m_shut"]; fig.vis["m_open"] = fig.J["m_open"]
    fig.vis_default["m_shut"] = 1; fig.vis_default["m_open"] = 0
    fig.head_c = Vector((cx, 0, cz))


def chain(fig, name, parent, start, links, r0, color, direction=(-1, 0, -0.35), taper=0.75, flat=0.5, sway=1.0, phase=0.0, line=None):
    """A trailing chain of flat leaf-shaped links (bandana tails, sash, kelp). Each link lags the one before."""
    d = Vector(direction).normalized(); p = Vector(start); par = parent; names = []
    r = r0
    for i, ln in enumerate(links):
        jn = "%s%d" % (name, i)
        fig.joint(jn, p, par, -1)
        q = p + d * ln
        ob = cone(p, q, r, r * taper, seg=6, name=name)
        for v in ob.data.vertices:      # flatten sideways into a ribbon
            v.co.y = p.y + (v.co.y - p.y) * flat
        fig.add(ob, jn, color, line=line)
        names.append(jn); par = jn; p = q; r *= taper
    fig.tails.append((names, sway, phase))
    return names


# ---------------------------------------------------------------- posing
def pose(fig, f, d):
    """Key the whole figure at frame f. d: joint -> pitch degrees (forward positive) or (pitch, roll, yaw);
    plus root=(x, z), squash=(sx, sz), rootrot, off={joint: (dx, dy, dz)}, vis={name: 0/1}, tail=(lean, t).
    Feet stay flat and the lower foot stays on the ground unless d['free'] is set."""
    rad = math.radians
    d = dict(d)
    P = getattr(fig, "P", {}); th = P.get("thigh", 0.27); sn = P.get("shin", 0.25); drop = [th + sn]
    for s in (("L", "R") if "thL" in fig.J and "snL" in fig.J else ()):
        a1 = d.get("th" + s, 0.0); a2 = a1 + d.get("sn" + s, 0.0)
        if ("ft" + s) not in d:
            d["ft" + s] = -a2 - (d.get("hips", 0.0) if isinstance(d.get("hips", 0.0), (int, float)) else d["hips"][0])
        drop.append(th * math.cos(rad(a1)) + sn * math.cos(rad(a2)))
    rx, rz = d.get("root", (0, 0)); sx, sz = d.get("squash", (1, 1))
    if not d.get("free"):
        rz += max(drop) - (th + sn)
    key(fig.J["root"], f, (0, rad(d.get("rootrot", 0)), 0), (rx, 0, rz), (sx, sx, sz))
    tailj = set(n for names, _, _ in fig.tails for n in names)
    off = d.get("off", {})
    for name, e in fig.J.items():
        if name == "root" or name in tailj:
            continue
        if name in fig.vis:
            continue
        v = d.get(name, 0.0)
        if isinstance(v, (int, float)):
            v = (v, 0.0, 0.0)
        pitch = (v[0] + fig.rest[name]) * fig.sign[name]
        o = off.get(name, (0, 0, 0))
        key(e, f, (rad(v[1]), rad(pitch), rad(v[2])), fig.L[name] + Vector(o))
    lean, t = d.get("tail", (0.0, 0.0))
    for names, sway, phase in fig.tails:
        for i, jn in enumerate(names):
            a = lean * (0.55 if i == 0 else 0.35) + sway * 13 * math.sin(2 * math.pi * (t + phase) - i * 0.9) * (1 + i * 0.4)
            key(fig.J[jn], f, (0, rad(-a), 0))
    vis = d.get("vis", {})
    for name, e in fig.vis.items():
        s = max(vis.get(name, fig.vis_default.get(name, 1)), 0.001)
        key(e, f, scale=(s, s, s))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    return t * t * (3 - 2 * t)


def blend(A, B, t):
    """Blend two pose dicts (numbers and tuples)."""
    out = {}
    for k in set(A) | set(B):
        a = A.get(k); b = B.get(k)
        if k == "vis":
            out[k] = (b if t >= 0.5 else a) or {}
            continue
        if k == "off":
            a = a or {}; b = b or {}
            out[k] = {j: tuple(lerp(x, y, t) for x, y in zip(a.get(j, (0, 0, 0)), b.get(j, (0, 0, 0)))) for j in set(a) | set(b)}
            continue
        if a is None:
            a = (1, 1) if k == "squash" else (0 if isinstance(b, (int, float)) else tuple(0 for _ in b))
        if b is None:
            b = (1, 1) if k == "squash" else (0 if isinstance(a, (int, float)) else tuple(0 for _ in a))
        if isinstance(a, (int, float)) and isinstance(b, tuple):
            a = (a,) + (0,) * (len(b) - 1)
        if isinstance(b, (int, float)) and isinstance(a, tuple):
            b = (b,) + (0,) * (len(a) - 1)
        out[k] = lerp(a, b, t) if isinstance(a, (int, float)) else tuple(lerp(x, y, t) for x, y in zip(a, b))
    return out


def keys(K, t):
    """K: list of (time 0..1, pose). Eased blend between neighbours; holds before the first / after the last."""
    if t <= K[0][0]:
        return dict(K[0][1])
    for (t0, a), (t1, b) in zip(K, K[1:]):
        if t <= t1:
            return blend(a, b, ease((t - t0) / max(t1 - t0, 1e-6)))
    return dict(K[-1][1])


def run_anims(fig, table, anims):
    """table: anim name -> fn(t 0..1, i, n) -> pose. anims: cast animset rows. Returns frames used."""
    f = 1
    for name, n, *_ in anims:
        fn = table[name]
        for i in range(n):
            t = i / n if name in ("idle", "walk") else i / max(n - 1, 1)
            pose(fig, f, fn(t, i, n)); f += 1
    return f - 1


def turn(ob, deg, axis, cent):
    """Rotate a part's mesh about a world point (used to angle props while building)."""
    c = Vector(cent)
    ob.data.transform(Matrix.Translation(c) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-c))
    return ob


def toggle(fig, name, parent, at, default=0):
    """A pivot whose children are shown/hidden by scale from pose['vis']."""
    fig.joint(name, at, parent, 1); fig.vis[name] = fig.J[name]; fig.vis_default[name] = default
    return name
