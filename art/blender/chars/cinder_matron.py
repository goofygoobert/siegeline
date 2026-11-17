from kit import *
# Cinder Matron (boss, 2.6x) — robed hollow matron, tall horned crown, chained censer flail.
# sweep: censer raised and glowing for frames 0-6 (the player's warning), swing lands on frame 8.
def crown(rig, C):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    attach(cyl(r * 0.95, 0.12 * sc, C["bone"], (hx - 0.02 * sc, 0, hz + r * 0.62), seg=12, name="circlet"), hp)
    for i, (a, L) in enumerate(((0, 0.55), (35, 0.42), (-35, 0.42), (70, 0.3), (-70, 0.3), (180, 0.36), (130, 0.3), (-130, 0.3))):
        ra = math.radians(a)
        b = Vector((hx + math.cos(ra) * r * 0.85, math.sin(ra) * r * 0.85, hz + r * 0.65))
        attach(spike(b, (math.cos(ra) * 0.12, math.sin(ra) * 0.12, 1), L * sc, 0.045 * sc, C["bone"]), hp)
    for y in (1, -1):   # big swept-back horns
        p0 = Vector((hx - r * 0.3, y * r * 0.75, hz + r * 0.4))
        p1 = p0 + Vector((-0.12, y * 0.12, 0.22)) * sc
        p2 = p1 + Vector((-0.2, y * 0.05, 0.12)) * sc
        attach(rod(p0, p1, 0.07 * sc, C["bone"], r2=0.05 * sc), hp)
        attach(rod(p1, p2, 0.05 * sc, C["bone"], r2=0.0), hp)
    attach(ball(0.06 * sc, PAL["ember"], (hx + r * 0.6, 0, hz + r * 0.95), glow=2.0, name="gem", outline=0.0), hp)
    # veil / hair hanging behind
    attach(box((0.06 * sc, r * 1.6, r * 1.9), (0.13, 0.11, 0.12), (hx - r * 0.85, 0, hz - r * 0.5), taper=(1, 1.3), name="veil"), hp)

def mask(rig, C):
    """Pale bone face-mask with glowing eye holes: the boss's readable focal point."""
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    attach(ball(r * 0.86, C["bone"], (hx + r * 0.62, -0.02 * sc, hz - r * 0.05), scale=(0.6, 1.0, 1.2), name="mask"), hp)
    for y in (-0.35, 0.35):
        attach(box((0.06 * sc, r * 0.32, r * 0.16), PAL["ember"], (hx + r * 1.12, y * r - 0.02 * sc, hz + r * 0.12),
                   rot=(math.radians(25 if y > 0 else -25), 0, 0), glow=2.0, name="maskeye", outline=0.012), hp)
    attach(box((0.05 * sc, r * 0.5, r * 0.1), PAL["dark"], (hx + r * 1.1, -0.02 * sc, hz - r * 0.45), name="maskmouth", outline=0.0), hp)
    attach(box((0.04 * sc, 0.05 * sc, r * 0.5), PAL["blood"], (hx + r * 1.08, -r * 0.2, hz - r * 0.72), name="maskdrip", outline=0.0), hp)

def throat(rig, C):
    sc = rig["sc"]; z = rig["shoulder_z"]; bw = rig["bw"]
    gp = glow_pivot(rig, "throat", (bw * 0.34, -0.02 * sc, z + 0.02 * sc), rig["torso"])
    attach(ball(0.1 * sc, PAL["ember"], (bw * 0.34, -0.02 * sc, z + 0.02 * sc), scale=(0.8, 1, 1.2), glow=1.6, name="throat", outline=0.0), gp)

def censer(rig, C):
    sc = rig["sc"]; hand = rig["hand_R"]; p = hand.matrix_world.translation.copy()
    x, y, z = p.x, p.y - 0.06 * sc, p.z
    ch = empty("chain", (x, y, z))
    L = 0.17 * sc
    for i in range(5):
        attach(ball(0.03 * sc, C["metal"], (x, y, z - (i + 0.5) * L / 5), scale=(0.7, 0.7, 1.4), name="link", seg=8, outline=0.012), ch)
    cz = z - L - 0.12 * sc
    attach(ball(0.15 * sc, C["metal_dk"], (x, y, cz), seg=12, name="censer"), ch)
    for a in range(4):
        ra = a * math.pi / 2
        attach(spike((x + math.cos(ra) * 0.13 * sc, y + math.sin(ra) * 0.13 * sc, cz), (math.cos(ra), math.sin(ra), 0.2), 0.12 * sc, 0.03 * sc, C["bone"]), ch)
    attach(cyl(0.165 * sc, 0.04 * sc, C["trim"], (x, y, cz), seg=12, name="band"), ch)
    gp = glow_pivot(rig, "censer", (x, y, cz), ch)
    attach(ball(0.1 * sc, PAL["ember"], (x, y - 0.08 * sc, cz), glow=2.0, name="ember", outline=0.0), gp)
    attach(ball(0.05 * sc, (1, 0.85, 0.4), (x, y - 0.15 * sc, cz + 0.02 * sc), glow=2.0, name="core", outline=0.0), gp)
    attach(spike((x, y, cz + 0.12 * sc), (0, 0, 1), 0.1 * sc, 0.05 * sc, C["metal_dk"]), ch)
    bpy.context.view_layer.update()
    ch.parent = hand; ch.matrix_parent_inverse = hand.matrix_world.inverted()
    keyable(rig, "chain", ch, "roty")

def mantle(rig, C):
    """Jagged shoulder mantle + torn hem: makes the silhouette wide and spiky."""
    sc = rig["sc"]; bw = rig["bw"]; z = rig["shoulder_z"]; tp = rig["torso"]
    attach(cyl(bw * 0.62, 0.2 * sc, C["robe"], (0, 0, z - 0.02 * sc), r2=bw * 0.4, seg=14, name="mantle"), tp)
    for i in range(9):
        a = math.radians(-160 + i * 40)
        d = Vector((math.cos(a), math.sin(a), -0.35))
        L = (0.26, 0.18, 0.3, 0.2, 0.28)[i % 5] * sc
        attach(spike((math.cos(a) * bw * 0.55, math.sin(a) * bw * 0.55, z - 0.08 * sc), d, L, 0.07 * sc, C["robe"]), tp)
    for i in range(3):
        attach(spike((-bw * 0.3, (i - 1) * 0.12 * sc, z + 0.02 * sc), (-0.5, (i - 1) * 0.3, 1), (0.3, 0.42, 0.26)[i] * sc, 0.05 * sc, C["bone"]), tp)
    hr = bw * 0.8
    attach(cyl(bw * 0.8, 0.5 * sc, C["robe"], (0, 0, 0.27 * sc), r2=bw * 0.6, seg=16, name="skirt"), rig["hips"])
    attach(cyl(bw * 0.81, 0.08 * sc, C["robe_trim"], (0, 0, 0.1 * sc), seg=16, name="skirt_trim"), rig["hips"])
    for i in range(12):
        a = math.radians(i * 30 + 10)
        attach(spike((math.cos(a) * hr * 0.95, math.sin(a) * hr * 0.95, 0.12 * sc), (math.cos(a) * 0.3, math.sin(a) * 0.3, -1),
                     (0.1 if i % 2 else 0.07) * sc, 0.06 * sc, C["robe"]), rig["hips"])

def hem_cracks(rig, C):
    sc = rig["sc"]; bw = rig["bw"]
    for i, (a, h) in enumerate(((-60, 0.3), (-20, 0.22), (20, 0.34), (-100, 0.2))):
        ra = math.radians(a)
        attach(box((0.03 * sc, 0.03 * sc, h * sc), PAL["ember"], (math.cos(ra) * bw * 0.77, math.sin(ra) * bw * 0.77, 0.2 * sc),
                   rot=(0, math.radians(15 * (i % 2 * 2 - 1)), 0), glow=1.8, name="hcrack", outline=0.0), rig["hips"])


LEAN = 12
def hang(aR, torso):     # chain counter-rotation so the censer hangs straight down
    return -(aR + torso + LEAN)

def m_idle(t, st):
    s = math.sin(t * math.tau)
    aR = -20 + 4 * s; tor = 2 * s
    return dict(bob=0.02 * s, torso=tor, head=-2 * s, aR=aR, aL=10 - 4 * s, k=dict(chain=hang(aR, tor) + 10 * s, censer=1 + 0.08 * s, throat=1))

def m_walk(t, st):
    s = math.sin(t * math.tau); c = math.cos(t * math.tau)
    aR = -20 - 8 * s; tor = 4 + 2 * c
    return dict(bob=0.03 * abs(c), torso=tor, head=-3, lL=-14 * s, lR=14 * s, aL=10 + 10 * s, aR=aR, rx=0.0,
                k=dict(chain=hang(aR, tor) - 18 * s, censer=1.05))

SWEEP = dict(aR=[-20, 40, 100, 140, 150, 150, 150, 60, -100, -110, -60, -20],
             aL=[10, 0, -20, -30, -30, -30, -30, -10, 30, 30, 20, 10],
             torso=[0, -6, -10, -14, -14, -14, -14, -4, 20, 22, 10, 2],
             rx=[0, 0, -0.02, -0.04, -0.04, -0.04, -0.04, 0, 0.1, 0.1, 0.05, 0],
             censer=[1, 1.3, 1.6, 1.9, 2.2, 2.0, 2.2, 1.8, 1.5, 1.2, 1.0, 1.0],
             chainx=[None, None, None, None, None, None, None, -25, 0, 25, 40, None])

def m_sweep(t, st):
    i = min(int(t * 12 + 1e-6), 11)
    aR = SWEEP["aR"][i]; tor = SWEEP["torso"][i]
    cx = SWEEP["chainx"][i]
    chain = hang(aR, tor) + (6 if i % 2 else -6) if cx is None else cx
    return dict(aR=aR, aL=SWEEP["aL"][i], torso=tor, rx=SWEEP["rx"][i], head=-tor * 0.4,
                k=dict(chain=chain, censer=SWEEP["censer"][i]))

SUMMON = dict(a=[-15, -60, -120, -160, -170, -175, -120, -40], ax=[0, 10, 25, 35, 40, 42, 25, 5],
              torso=[0, -4, -8, -12, -14, -14, -8, -2], head=[0, -5, -15, -25, -30, -32, -15, -5],
              throat=[1, 1, 1.3, 1.7, 2.2, 2.4, 1.5, 1])

def m_summon(t, st):
    i = min(int(t * 8 + 1e-6), 7)
    a = SUMMON["a"][i]; tor = SUMMON["torso"][i]
    return dict(aR=a, aL=a, aRx=SUMMON["ax"][i], aLx=SUMMON["ax"][i], torso=tor, head=SUMMON["head"][i],
                k=dict(chain=hang(a, tor), throat=SUMMON["throat"][i], censer=1.3))

SPIT = dict(torso=[0, -8, -16, -22, -24, 22, 12, 2], head=[0, -8, -16, -24, -26, 15, 8, 0],
            throat=[1, 1.3, 1.6, 2.0, 2.3, 0.8, 0.9, 1], aR=[-15, 0, 10, 15, 15, -30, -20, -15],
            aL=[10, 20, 30, 35, 35, -20, 0, 10], rx=[0, -0.02, -0.04, -0.05, -0.05, 0.06, 0.03, 0])

def m_spit(t, st):
    i = min(int(t * 8 + 1e-6), 7)
    aR = SPIT["aR"][i]; tor = SPIT["torso"][i]
    return dict(aR=aR, aL=SPIT["aL"][i], torso=tor, head=SPIT["head"][i], rx=SPIT["rx"][i],
                k=dict(chain=hang(aR, tor), throat=SPIT["throat"][i]))

def m_hit(t, st):
    k = math.sin(t * math.pi + 0.6) if t > 0 else 0.7
    aR = -20 + 25 * k; tor = -14 * k
    return dict(rx=-0.06 * k, torso=tor, head=-12 * k, aR=aR, aL=10 + 30 * k, k=dict(chain=hang(aR, tor) + 20 * k, censer=0.9))

DIE = dict(rr=[0, -4, -8, -6, 0, 8, 20, 36, 54, 70, 80, 84], rx=[0, -0.03, -0.06, -0.1, -0.14, -0.2, -0.3, -0.42, -0.55, -0.65, -0.7, -0.72],
           rz=[0, -0.02, -0.05, -0.08, -0.1, -0.1, -0.06, 0.04, 0.1, 0.18, 0.24, 0.27],
           torso=[0, -10, -16, -12, -5, 5, 10, 15, 15, 15, 15, 15], head=[0, -15, -25, -20, -10, 0, 10, 15, 20, 20, 20, 20],
           aR=[-20, 10, 30, 20, 0, -20, -35, -45, -50, -55, -55, -55], aL=[10, 30, 45, 30, 10, -15, -25, -35, -40, -40, -40, -40],
           censer=[0.9, 0.8, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.3, 0.3])

def m_die(t, st):
    i = min(int(t * 12 + 1e-6), 11)
    return dict(rr=DIE["rr"][i], rx=DIE["rx"][i], rz=DIE["rz"][i], torso=DIE["torso"][i], head=DIE["head"][i],
                aR=DIE["aR"][i], aL=DIE["aL"][i], leanf=max(0, 1 - i / 6),
                k=dict(chain=-(DIE["aR"][i] + DIE["torso"][i] + DIE["rr"][i] + LEAN * max(0, 1 - i / 6)) + 90 * min(1, i / 5), censer=DIE["censer"][i], throat=0.5))

register(dict(id="cinder_matron", facing=-1, eye_style="slit", scale=2.6, bulk=1.0, head=0.8, torso=1.15, leg=1.0, arm=1.0,
              limb=0.6, head_fwd=0.08, taper=(1.35, 1.0), robe=True, weapon=None, offhand="claws",
              extras=[crown, mask, throat, censer, mantle, hem_cracks, lambda r, C: hollow_cracks(r, C, 3)],
              style=dict(lean=LEAN, headc=0.6, anims=dict(idle=m_idle, walk=m_walk, sweep=m_sweep, summon=m_summon, spit=m_spit,
                                                       hit=m_hit, die=m_die)),
              colors=hollow_colors(robe=(0.31, 0.26, 0.28), robe_trim=PAL["blood"], body=(0.3, 0.28, 0.28),
                                   arms=(0.36, 0.34, 0.34), skin=(0.38, 0.36, 0.36), trim=PAL["brass"])))
