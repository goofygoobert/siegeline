from kit import *
# Mother Fathom (boss, 2.6x) — towering sea hag: hunched crone in rotted sailcloth, fish-scale skin, crown of coral and whale
# bone, stringy kelp hair, a lantern-fish lure glowing over her head, and a TENTACLE right arm for the sweep.
# sweep: tentacle raised and cocked behind her, glowing, for frames 0-6 (the player's warning); lash lands on frame 8.
TN = 7     # tentacle segments t0..t6

def crown(rig, C):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    attach(cyl(r * 0.95, 0.12 * sc, C["bone"], (hx - 0.02 * sc, 0, hz + r * 0.62), seg=12, name="circlet"), hp)
    for i, (a, L, coral) in enumerate(((0, 0.4, False), (40, 0.32, True), (-40, 0.34, True), (80, 0.26, False), (-80, 0.26, False),
                                       (180, 0.28, True), (130, 0.24, False), (-130, 0.26, True))):
        ra = math.radians(a)
        b = Vector((hx + math.cos(ra) * r * 0.85, math.sin(ra) * r * 0.85, hz + r * 0.65))
        if coral:     # branching coral
            e = b + Vector((math.cos(ra) * 0.15, math.sin(ra) * 0.15, 1)).normalized() * L * sc
            attach(rod(b, e, 0.05 * sc, PAL["coral"], r2=0.025 * sc, seg=6), hp)
            attach(spike(tuple(b + (e - b) * 0.55), (math.cos(ra) * 0.8, math.sin(ra) * 0.8, 0.7), L * 0.45 * sc, 0.025 * sc, PAL["coral"]), hp)
            attach(ball(0.035 * sc, PAL["coral"], tuple(e), name="nub", outline=0.008), hp)
        else:         # whale-bone spike
            attach(spike(tuple(b), (math.cos(ra) * 0.12, math.sin(ra) * 0.12, 1), L * sc, 0.05 * sc, C["bone"]), hp)

def crone_face(rig, C):
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    attach(rod((hx + r * 0.85, 0, hz - r * 0.05), (hx + r * 1.45, 0, hz - r * 0.45), 0.08 * sc, C["skin"], r2=0.02 * sc), hp)   # hooked nose
    attach(ball(r * 0.4, C["skin"], (hx + r * 0.75, 0, hz - r * 0.8), scale=(1, 0.8, 0.8), name="chin"), hp)
    for i in range(4):   # scale rows on the cheek
        attach(ball(0.04 * sc, (0.3, 0.44, 0.38), (hx + r * (0.2 + 0.15 * (i % 2)), -r * 0.92, hz - r * (0.05 + 0.18 * i)), scale=(1, 0.5, 0.8), name="scale", outline=0.0), hp)

def lure(rig, C):
    """Lantern-fish lure: a stalk from the back of the crown arching forward, with a glowing bulb ('lure')."""
    sc = rig["sc"]; hp = rig["head"]; hz = rig["head_z"]; r = rig["head_r"]; hx = rig["head_x"]
    pts = [Vector((hx - r * 0.5, 0, hz + r * 0.7)), Vector((hx - r * 0.45, 0, hz + r * 1.6)), Vector((hx + r * 0.25, 0, hz + r * 2.0)),
           Vector((hx + r * 1.05, 0, hz + r * 1.9)), Vector((hx + r * 1.4, 0, hz + r * 1.55))]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        attach(rod(a, b, (0.07 - i * 0.012) * sc, C["skin"], r2=(0.06 - i * 0.012) * sc, seg=8), hp)
    bulb = pts[-1] + Vector((0, 0, -0.1 * sc))
    gp = glow_pivot(rig, "lure", tuple(bulb), hp)
    attach(ball(0.15 * sc, PAL["sick"], tuple(bulb), scale=(1, 1, 1.2), glow=1.6, name="bulb", outline=0.014), gp)
    attach(ball(0.08 * sc, (0.9, 1.0, 0.85), tuple(bulb + Vector((0.02 * sc, -0.1 * sc, 0.02 * sc))), glow=2.0, name="bulbcore", outline=0.0), gp)
    for a in (-50, 0, 50):
        ra = math.radians(a)
        attach(spike(tuple(bulb + Vector((0, 0, -0.12 * sc))), (math.sin(ra), 0, -1), 0.1 * sc, 0.02 * sc, C["bone"], outline=0.006), gp)

def throat(rig, C):
    sc = rig["sc"]; z = rig["shoulder_z"]; bw = rig["bw"]
    gp = glow_pivot(rig, "throat", (bw * 0.34, -0.02 * sc, z + 0.02 * sc), rig["torso"])
    attach(ball(0.12 * sc, PAL["ink"], (bw * 0.34, -0.02 * sc, z + 0.02 * sc), scale=(0.8, 1, 1.2), glow=0.4, name="throat"), gp)
    attach(ball(0.06 * sc, PAL["sick"], (bw * 0.4, -0.08 * sc, z + 0.02 * sc), glow=2.0, name="throatcore", outline=0.0), gp)

def mantle(rig, C):
    """Rotted sailcloth: ragged shoulder cape, torn skirt, patches; hump with barnacles and fin spines."""
    sc = rig["sc"]; bw = rig["bw"]; z = rig["shoulder_z"]; tp = rig["torso"]
    attach(cyl(bw * 0.62, 0.2 * sc, C["robe"], (0, 0, z - 0.02 * sc), r2=bw * 0.4, seg=14, name="mantle"), tp)
    for i in range(9):
        a = math.radians(-160 + i * 40)
        d = Vector((math.cos(a), math.sin(a), -0.6))
        L = (0.3, 0.2, 0.34, 0.22, 0.3)[i % 5] * sc
        attach(spike((math.cos(a) * bw * 0.55, math.sin(a) * bw * 0.55, z - 0.08 * sc), d, L, 0.08 * sc, C["robe"]), tp)
    attach(ball(0.3 * sc, C["robe"], (-bw * 0.3, 0, z - 0.05 * sc), scale=(1, 1.1, 0.9), name="hump"), tp)
    barnacles(rig, C, tp, [(-bw * 0.42, -0.1 * sc + i * 0.07 * sc, z + 0.1 * sc - (i % 2) * 0.12 * sc) for i in range(5)], 1.0)
    for i in range(3):
        attach(spike((-bw * 0.42, (i - 1) * 0.12 * sc, z + 0.12 * sc), (-0.6, (i - 1) * 0.3, 1), (0.3, 0.42, 0.26)[i] * sc, 0.05 * sc, C["fin"]), tp)
    for (dx, dz, w, h) in ((0.44, 0.45, 0.18, 0.22), (0.3, 0.2, 0.14, 0.16)):   # darker patches on the near side
        attach(box((w * sc, 0.03 * sc, h * sc), tuple(v * 0.7 for v in C["robe"]), (bw * (dx - 0.3), -bw * 0.4, rig["hip_h"] + rig["torso_h"] * dz), name="patch", outline=0.0), tp)
    hr = bw * 0.8
    attach(cyl(bw * 0.8, 0.5 * sc, C["robe"], (0, 0, 0.27 * sc), r2=bw * 0.6, seg=16, name="skirt"), rig["hips"])
    attach(cyl(bw * 0.81, 0.08 * sc, C["robe_trim"], (0, 0, 0.1 * sc), seg=16, name="skirt_trim"), rig["hips"])
    for i in range(12):
        a = math.radians(i * 30 + 10)
        attach(spike((math.cos(a) * hr * 0.95, math.sin(a) * hr * 0.95, 0.12 * sc), (math.cos(a) * 0.3, math.sin(a) * 0.3, -1),
                     (0.1 if i % 2 else 0.07) * sc, 0.06 * sc, C["robe"]), rig["hips"])
    for i in range(4):    # kelp hanging off the hem
        a = math.radians(-120 + i * 30)
        b = Vector((math.cos(a) * hr * 0.9, math.sin(a) * hr * 0.9, 0.35 * sc))
        attach(rod(b, b + Vector((0, 0, -0.3 * sc)), 0.035 * sc, C["kelp"], r2=0.01 * sc, seg=6), rig["hips"])

def hem_glow(rig, C):
    sc = rig["sc"]; bw = rig["bw"]
    for i, (a, h) in enumerate(((-60, 0.3), (-20, 0.22), (20, 0.34), (-100, 0.2))):
        ra = math.radians(a)
        attach(box((0.03 * sc, 0.03 * sc, h * sc), PAL["sick"], (math.cos(ra) * bw * 0.77, math.sin(ra) * bw * 0.77, 0.2 * sc),
                   rot=(0, math.radians(15 * (i % 2 * 2 - 1)), 0), glow=1.8, name="hcrack", outline=0.0), rig["hips"])

def tent_arm(rig, C):
    tentacle(rig, C, "R", n=TN, seg=0.095, r0=0.09)


LEAN = 16
def tk(root, curl, wave=0.0, ph=0.0):
    """k dict for the tentacle: root angle, per-segment curl and a travelling wave."""
    d = {"t0": root}
    for i in range(1, TN):
        d["t%d" % i] = curl + wave * math.sin(ph + i * 0.9)
    return d

def m_idle(t, st):
    s = math.sin(t * math.tau)
    aR = -20 + 4 * s; tor = 2 * s
    k = tk(-55 + 5 * s, -15, 5, t * math.tau); k.update(censer=1 + 0.1 * s, throat=1, lure=1 + 0.12 * s)
    return dict(bob=0.02 * s, torso=tor, head=-2 * s, aR=aR, aL=10 - 4 * s, k=k)

def m_walk(t, st):
    s = math.sin(t * math.tau); c = math.cos(t * math.tau)
    aR = -20 - 8 * s; tor = 4 + 2 * c
    k = tk(-50 + 6 * s, -15, 6, t * math.tau); k.update(censer=1.05, lure=1 + 0.1 * c)
    return dict(bob=0.03 * abs(c), torso=tor, head=-3, lL=-14 * s, lR=14 * s, aL=10 + 10 * s, aR=aR, k=k)

SWEEP = dict(aR=[-20, 40, 100, 140, 150, 150, 150, 60, -100, -110, -60, -20],
             aL=[10, 0, -20, -30, -30, -30, -30, -10, 30, 30, 20, 10],
             torso=[0, -6, -10, -14, -14, -14, -14, -4, 20, 22, 10, 2],
             rx=[0, 0, -0.02, -0.04, -0.04, -0.04, -0.04, 0, 0.1, 0.1, 0.05, 0],
             root=[-55, -20, -8, -10, -12, -12, -12, 20, 5, 0, -30, -50],
             curl=[-15, -12, -10, -11, -12, -12, -12, -4, 8, 4, -8, -14],
             censer=[1, 1.4, 1.8, 2.1, 2.4, 2.4, 2.4, 1.8, 1.5, 1.2, 1.0, 1.0],
             lure=[1, 1.1, 1.2, 1.3, 1.4, 1.4, 1.4, 1.25, 1.1, 1.05, 1.0, 1.0])

def m_sweep(t, st):
    i = min(int(t * 12 + 1e-6), 11)
    k = tk(SWEEP["root"][i], SWEEP["curl"][i], 4 if i < 7 else 0, min(i, 4) * 1.3)   # frames 4-6: identical hold
    k.update(censer=SWEEP["censer"][i], lure=SWEEP["lure"][i])
    tor = SWEEP["torso"][i]
    return dict(aR=SWEEP["aR"][i], aL=SWEEP["aL"][i], torso=tor, rx=SWEEP["rx"][i], head=-tor * 0.4, k=k)

SUMMON = dict(a=[-15, -60, -120, -160, -170, -175, -120, -40], ax=[0, 10, 25, 35, 40, 42, 25, 5],
              torso=[0, -4, -8, -12, -14, -14, -8, -2], head=[0, -5, -15, -25, -30, -32, -15, -5],
              lure=[1, 1.1, 1.25, 1.45, 1.6, 1.65, 1.35, 1.1])

def m_summon(t, st):
    i = min(int(t * 8 + 1e-6), 7)
    a = SUMMON["a"][i]
    k = tk(-30, -10, 8, i * 1.1); k.update(lure=SUMMON["lure"][i], censer=1.3 + 0.1 * i, throat=1.2)
    return dict(aR=a, aL=a, aRx=SUMMON["ax"][i], aLx=SUMMON["ax"][i], torso=SUMMON["torso"][i], head=SUMMON["head"][i], k=k)

SPIT = dict(torso=[0, -8, -16, -22, -24, 22, 12, 2], head=[0, -8, -16, -24, -26, 15, 8, 0],
            throat=[1, 1.3, 1.6, 2.0, 2.3, 0.8, 0.9, 1], aR=[-15, 0, 10, 15, 15, -30, -20, -15],
            aL=[10, 20, 30, 35, 35, -20, 0, 10], rx=[0, -0.02, -0.04, -0.05, -0.05, 0.06, 0.03, 0])

def m_spit(t, st):
    i = min(int(t * 8 + 1e-6), 7)
    k = tk(-55, -15, 5, i * 1.2); k.update(throat=SPIT["throat"][i], lure=1.0 + 0.1 * (i < 5))
    return dict(aR=SPIT["aR"][i], aL=SPIT["aL"][i], torso=SPIT["torso"][i], head=SPIT["head"][i], rx=SPIT["rx"][i], k=k)

def m_hit(t, st):
    k_ = math.sin(t * math.pi + 0.6) if t > 0 else 0.7
    k = tk(-55 + 25 * k_, -15 + 8 * k_, 5, t * 5); k.update(censer=0.9, lure=0.8)
    return dict(rx=-0.06 * k_, torso=-14 * k_, head=-12 * k_, aR=-20 + 25 * k_, aL=10 + 30 * k_, k=k)

DIE = dict(rr=[0, -4, -8, -6, 0, 8, 20, 36, 54, 70, 80, 84], rx=[0, -0.03, -0.06, -0.1, -0.14, -0.2, -0.3, -0.42, -0.55, -0.65, -0.7, -0.72],
           rz=[0, -0.02, -0.05, -0.08, -0.1, -0.1, -0.06, 0.04, 0.1, 0.18, 0.24, 0.27],
           torso=[0, -10, -16, -12, -5, 5, 10, 15, 15, 15, 15, 15], head=[0, -15, -25, -20, -10, 0, 10, 15, 20, 20, 20, 20],
           aR=[-20, 10, 30, 20, 0, -20, -35, -45, -50, -55, -55, -55], aL=[10, 30, 45, 30, 10, -15, -25, -35, -40, -40, -40, -40],
           glow=[0.9, 0.8, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.3, 0.3])

def m_die(t, st):
    i = min(int(t * 12 + 1e-6), 11)
    k = tk(-60, -16, 3, i); k.update(censer=DIE["glow"][i], lure=DIE["glow"][i], throat=0.5)
    return dict(rr=DIE["rr"][i], rx=DIE["rx"][i], rz=DIE["rz"][i], torso=DIE["torso"][i], head=DIE["head"][i],
                aR=DIE["aR"][i], aL=DIE["aL"][i], leanf=max(0, 1 - i / 6), k=k)

register(dict(id="cinder_matron", facing=-1, eye_style="slit", scale=2.6, bulk=1.0, head=0.8, torso=1.15, leg=1.0, arm=1.0,
              limb=0.6, head_fwd=0.08, taper=(1.35, 1.0), robe=True, weapon=None, offhand="claws",
              extras=[crown, crone_face, lambda r, C: kelp_hair(r, C, 9, 0.75), hollow_maw, lure, throat, tent_arm, mantle, hem_glow,
                      lambda r, C: hollow_cracks(r, C, 2), gills],
              style=dict(lean=LEAN, headc=0.6, anims=dict(idle=m_idle, walk=m_walk, sweep=m_sweep, summon=m_summon, spit=m_spit,
                                                       hit=m_hit, die=m_die)),
              colors=deep_colors(robe=(0.44, 0.46, 0.38), robe_trim=PAL["ink"], body=(0.36, 0.42, 0.36),
                                 arms=(0.4, 0.44, 0.37), skin=(0.42, 0.58, 0.5), hands=(0.42, 0.58, 0.5), tent=(0.38, 0.5, 0.46),
                                 sucker=(0.82, 0.74, 0.66), kelp=(0.18, 0.3, 0.16))))
