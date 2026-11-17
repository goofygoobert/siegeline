"""All Siegeline sound effects, pirate re-theme (The Gullwake vs. the Deep).
Run: .venv/bin/python tools/audio/sfx.py [id ...]

Each sound = layered synthesis (transient + filtered noise + pitched body), then a small
room reverb where useful, loudness-normalised with a -1 dBFS peak ceiling. No samples.
"""
import sys
import numpy as np

from synth import (SR, n_of, tvec, noise, exp_env, adsr, fade, sine, saw, square, tri, mtof,
                   lp, hp, bp, peak_bp, sweep_lp, normalize, softclip, mix_at, make_ir,
                   reverb, undb, peak, db)
from instruments import (brass, strings, choir, bell, metal, pluck, taiko, frame_drum, snare,
                         hat, cymbal, boom, click, flute, accordion, fiddle, stomp, clap, shout,
                         whale, wave_wash, creak, splash, fizz, squelch, wood_crack, cannon,
                         bosun_whistle)
import audioio as A

ROOM = make_ir(0.6, 0.35, seed=5, damp=6000, stereo=False)[None, :]
HALL = make_ir(1.8, 1.2, seed=9, damp=5000, stereo=False)[None, :]


def buf(sec):
    return np.zeros(n_of(sec))


def verb(x, ir, wet, keep=None):
    y = reverb(x, ir, wet)[0]
    return y[: n_of(keep)] if keep else y


def env_tail(x, sec):
    """Hard cap length with a smooth fade."""
    x = x[: n_of(sec)]
    return fade(x, 0.0, min(0.08, sec * 0.3))


def at(sec):
    return n_of(sec)


def ui_tap():
    b = buf(0.09)
    t = tvec(len(b))
    b += 0.5 * sine(1650, len(b)) * np.exp(-t / 0.012)
    b += 0.35 * sine(2480, len(b)) * np.exp(-t / 0.006)
    mix_at(b, click(0.003, 3000, 1), 0, 0.6)
    mix_at(b, bp(noise(at(0.02), 2), 2000, 5000) * exp_env(at(0.02), 0.004), 0, 0.4)
    return fade(b, 0, 0.02)


def ui_back():
    b = buf(0.16)
    for i, f in enumerate((1250, 830)):
        n = at(0.07)
        tt = tvec(n)
        tone = (sine(f, n) + 0.3 * sine(f * 2, n)) * np.exp(-tt / 0.018)
        mix_at(b, tone, at(0.055 * i), 0.55)
        mix_at(b, click(0.002, 2500, i), at(0.055 * i), 0.3)
    return fade(b, 0, 0.03)


def ui_upgrade():
    b = buf(0.7)
    for i, m in enumerate((69, 74, 78, 81)):  # A4 D5 F#5 A5
        tone = bell(mtof(m) * 2, 0.55, decay=0.25, seed=i, strike=0.2)
        tone += 0.5 * sine(mtof(m), len(tone)) * exp_env(len(tone), 0.12)
        mix_at(b, tone, at(0.06 * i), 0.35 + 0.05 * i)
    sh = hp(noise(len(b), 4), 6000) * adsr(len(b), 0.15, 0.1, 0.4, 0.35) * 0.08
    b += sh
    return verb(b, ROOM, 0.25, 0.7)


def ui_locked():
    b = buf(0.26)
    for i in range(2):
        n = at(0.09)
        tt = tvec(n)
        x = lp(square(98, n) + 0.5 * saw(147, n), 700) * np.exp(-tt / 0.04)
        mix_at(b, x, at(0.1 * i), 0.6)
        mix_at(b, lp(noise(at(0.03), i), 900) * exp_env(at(0.03), 0.01), at(0.1 * i), 0.5)
    return fade(b, 0, 0.03)


def field_tap():
    n = at(0.06)
    return bp(noise(n, 8), 800, 4000) * exp_env(n, 0.012)


def hit_blade():
    b = buf(0.32)
    n = len(b)
    t = tvec(n)
    # slicing hiss: band sweeping down
    hiss = bp(noise(n, 11), 2500, 9000) * np.exp(-t / 0.035)
    clang = metal([2120, 3390, 4710, 6230, 2870], [0.09, 0.07, 0.05, 0.035, 0.06], n,
                  [1, 0.7, 0.5, 0.3, 0.5], seed=4)
    body = sine(170 * (1 + 0.5 * np.exp(-t / 0.01)), n) * np.exp(-t / 0.05)
    b += 0.6 * hiss + 0.35 * clang + 0.7 * body
    mix_at(b, click(0.002, 4000, 3), 0, 0.8)
    return verb(fade(b, 0, 0.05), ROOM, 0.18, 0.32)


def hit_blunt():
    b = buf(0.32)
    n = len(b)
    t = tvec(n)
    body = sine(105 * (1 + 0.9 * np.exp(-t / 0.015)), n) * np.exp(-t / 0.09)
    thud = lp(noise(n, 12), 450, 2) * np.exp(-t / 0.05)
    wood = bp(noise(n, 13), 400, 1800) * np.exp(-t / 0.015)
    b += 1.0 * body + 1.1 * thud + 0.5 * wood
    mix_at(b, click(0.003, 1200, 5), 0, 0.6)
    return verb(softclip(fade(b, 0, 0.05), 1.5), ROOM, 0.15, 0.32)


def star():
    b = buf(0.7)
    for i, m in enumerate((86, 93)):  # D6 A6
        mix_at(b, bell(mtof(m), 0.6, decay=0.35, seed=i, strike=0.15), at(0.07 * i), 0.4)
    n = len(b)
    t = tvec(n)
    sp = hp(noise(n, 170), 7000) * np.exp(-t / 0.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 30 * t))
    b += 0.12 * sp
    b += 0.2 * sine(mtof(74), n) * adsr(n, 0.01, 0.1, 0.3, 0.4)
    return verb(fade(b, 0, 0.1), ROOM, 0.35, 0.7)


def heal():
    b = buf(0.75)
    n = len(b)
    t = tvec(n)
    for i, m in enumerate((74, 78, 81, 86)):
        k = at(0.5)
        tt = tvec(k)
        tone = (sine(mtof(m), k) + 0.3 * sine(mtof(m) * 2, k)) * adsr(k, 0.04, 0.1, 0.5, 0.3)
        mix_at(b, tone, at(0.06 * i), 0.22)
    mix_at(b, choir(mtof(62), 0.5, vowel="oo", a=0.1, r=0.2, voices=3, seed=1), 0, 0.15)
    b += hp(noise(n, 190), 6000) * adsr(n, 0.2, 0.1, 0.3, 0.3) * 0.05
    return verb(fade(b, 0, 0.12), ROOM, 0.35, 0.75)


def limit(x, thr, max_red_db=7.0):
    """Peak limiter: fast envelope follower, gain reduction capped at max_red_db."""
    from scipy.ndimage import maximum_filter1d
    env = maximum_filter1d(np.abs(x), 97)
    env = lp(env, 60, 1)
    env = np.maximum(env, maximum_filter1d(np.abs(x), 33))
    g = np.clip(thr / np.maximum(env, 1e-9), undb(-max_red_db), 1.0)
    g = np.minimum.accumulate(g[::-1])[::-1] if False else g
    return x * g

# ================================================================== crew & powder
def unit_send():
    """Crew sent out: squeezebox chord squeeze + a deck stomp."""
    b = buf(0.5)
    for k, m in enumerate((50, 57, 62, 66)):
        mix_at(b, accordion(mtof(m), 0.16, seed=k, reeds=3, a=0.006, r=0.08), 0, 0.22)
    mix_at(b, stomp(seed=1, f=86), 0, 0.9)
    mix_at(b, clap(seed=3, people=2), at(0.012), 0.4)
    return verb(b, ROOM, 0.25, 0.5)


def energy_full():
    """Powder keg ready: two hollow keg knocks and a little brass chime."""
    b = buf(0.6)
    for i, s in enumerate((0.0, 0.09)):
        n = at(0.2)
        tt = tvec(n)
        knock = metal([235 * (1 + 0.04 * i), 590, 1130], [0.06, 0.035, 0.02], n, [1, 0.6, 0.3], seed=i)
        knock += 0.8 * bp(noise(n, 30 + i), 300, 2500) * np.exp(-tt / 0.008)
        knock += 0.6 * sine(160 * (1 + 0.4 * np.exp(-tt / 0.01)), n) * np.exp(-tt / 0.04)
        mix_at(b, knock, at(s), 0.6 - 0.1 * i)
    for i, m in enumerate((86, 93)):
        mix_at(b, bell(mtof(m), 0.42, decay=0.3, seed=i, strike=0.1), at(0.2 + 0.07 * i), 0.3)
    n = len(b)
    b += hp(noise(n, 3), 5000) * adsr(n, 0.2, 0.1, 0.3, 0.25) * 0.04
    return verb(b, ROOM, 0.25, 0.6)


# ================================================================== hits
def hit_claw():
    """Wet, slimy claw slash: swish, two raking scratches, squelch, fleshy thump."""
    b = buf(0.34)
    n = len(b)
    t = tvec(n)
    sw = sweep_lp(bp(noise(n, 19), 600, 9000), 7000, 1500, curve=0.7) * np.exp(-((t - 0.03) / 0.03) ** 2)
    b += 0.6 * sw
    for i, (d, f) in enumerate(((0.025, 2800), (0.06, 2200))):
        m = at(0.08)
        tt = tvec(m)
        scr = bp(noise(m, 20 + i), f * 0.6, f * 1.5) * np.exp(-tt / 0.02) * (1 + 0.6 * np.sin(2 * np.pi * 110 * tt))
        mix_at(b, scr, at(d), 0.45)
    mix_at(b, squelch(0.22, seed=21, f=700, drop=0.5), at(0.03), 0.75)
    b += 0.55 * sine(140 * (1 + 0.5 * np.exp(-t / 0.02)), n) * np.exp(-t / 0.05)
    return verb(fade(b, 0, 0.05), ROOM, 0.15, 0.34)


def arrow_fire():
    """Flintlock musket: flint snap, pan-flash fizz, then the bang with a short slap echo."""
    b = buf(0.5)
    mix_at(b, click(0.0015, 3500, 2), 0, 0.5)
    n = at(0.06)
    tt = tvec(n)
    mix_at(b, metal([3100, 4700], [0.006, 0.004], n, [1, 0.6], seed=2), 0, 0.25)
    mix_at(b, hp(noise(n, 31), 2500) * np.exp(-tt / 0.02) * (1 - np.exp(-tt / 0.003)), at(0.008), 0.35)
    s = at(0.045)
    n = len(b) - s
    tt = tvec(n)
    crack = hp(noise(n, 32), 1200) * np.exp(-tt / 0.005)
    blast = sweep_lp(noise(n, 33), 6000, 400, curve=0.4) * np.exp(-tt / 0.05)
    body = sine(150 * (1 + 1.2 * np.exp(-tt / 0.01)), n) * np.exp(-tt / 0.05)
    bang = softclip(1.2 * crack + 1.0 * blast + 0.8 * body, 1.8)
    mix_at(b, bang, s, 1.0)
    mix_at(b, lp(bang, 2500)[: n - at(0.11)], s + at(0.11), 0.18)
    return fade(verb(b, ROOM, 0.2, 0.5), 0, 0.08)


def arrow_hit():
    """Musket ball hits a wet monster: quick thwack, small splat."""
    b = buf(0.24)
    n = len(b)
    t = tvec(n)
    b += 0.8 * bp(noise(n, 40), 700, 3500) * np.exp(-t / 0.01)
    b += 0.7 * sine(190 * (1 + 0.6 * np.exp(-t / 0.006)), n) * np.exp(-t / 0.04)
    mix_at(b, click(0.0012, 3000, 4), 0, 0.7)
    mix_at(b, squelch(0.12, seed=41, f=900, drop=0.5), at(0.01), 0.45)
    r = np.random.default_rng(42)
    for k in range(3):
        m = at(0.02)
        tt = tvec(m)
        mix_at(b, sine(r.uniform(900, 1800) * (1 + 2 * tt / 0.02), m) * np.exp(-tt / 0.006), at(0.04 + 0.03 * k), 0.15)
    return verb(fade(b, 0, 0.04), ROOM, 0.15, 0.24)


def bolt_fire():
    """Long Tom: a big black-powder cannon boom with a coastal slap echo."""
    b = buf(1.1)
    x = cannon(seed=50, size=1.0, dur=1.1)
    b += x
    mix_at(b, lp(x, 1500)[: len(b) - at(0.19)], at(0.19), 0.2)
    mix_at(b, click(0.003, 1500, 6), 0, 0.6)
    return verb(fade(b, 0, 0.15), HALL, 0.15, 1.1)


def bolt_hit():
    """Flaming cannonball lands: impact, splinters, splash and a tar sizzle."""
    b = buf(1.0)
    n = len(b)
    t = tvec(n)
    b += 0.9 * sine(75 * (1 + 1.4 * np.exp(-t / 0.02)), n) * np.exp(-t / 0.18)
    b += 0.8 * sweep_lp(noise(n, 61), 4500, 300, curve=0.6) * np.exp(-t / 0.12)
    mix_at(b, wood_crack(seed=62, size=1.2, snaps=7), 0, 0.7)
    r = np.random.default_rng(63)
    for k in range(18):  # flying splinters
        s = r.uniform(0.03, 0.45)
        m = at(0.03)
        tt = tvec(m)
        sp = metal([r.uniform(900, 3500), r.uniform(3000, 6000)], [0.008, 0.005], m, [1, 0.5], seed=k)
        mix_at(b, sp, at(s), r.uniform(0.1, 0.3) * np.exp(-s / 0.3))
    mix_at(b, splash(0.8, seed=64, size=1.0, bubbles=16), at(0.04), 0.65)
    mix_at(b, fizz(0.9, seed=65, rate=500, tau=0.35), at(0.08), 0.25)
    mix_at(b, click(0.004, 800, 66), 0, 0.9)
    return verb(fade(softclip(b, 1.5), 0, 0.15), ROOM, 0.22, 1.0)


def ballista_reload():
    """Cannon reload: ramrod scrape in and out, two rams, iron clank."""
    b = buf(0.72)
    for i, (s, d, f0, f1) in enumerate(((0.0, 0.16, 1500, 3500), (0.3, 0.14, 3000, 1600))):
        n = at(d)
        tt = tvec(n)
        sc = bp(noise(n, 80 + i), 1200, 6000) * (1 + 0.7 * np.sin(2 * np.pi * (60 + 40 * i) * tt))
        sc = sweep_lp(sc, f0, f1, curve=1.0) * adsr(n, 0.02, 0.03, 0.8, 0.05)
        mix_at(b, sc, at(s), 0.4)
    for i, s in enumerate((0.17, 0.25)):  # rams tamped home
        n = at(0.12)
        tt = tvec(n)
        th = sine(120 * (1 + 0.6 * np.exp(-tt / 0.01)), n) * np.exp(-tt / 0.04)
        th += lp(noise(n, 85 + i), 900) * np.exp(-tt / 0.015)
        th += 0.4 * metal([620, 1380], [0.03, 0.02], n, [1, 0.5], seed=i)
        mix_at(b, th, at(s), 0.7 - 0.15 * i)
    n = at(0.3)
    tt = tvec(n)
    clank = metal([410, 1020, 1760, 2950, 4100], [0.12, 0.08, 0.06, 0.04, 0.03], n, [1, 0.8, 0.6, 0.4, 0.25], seed=7)
    clank += 0.6 * bp(noise(n, 88), 1500, 6000) * np.exp(-tt / 0.006)
    clank += 0.5 * sine(140, n) * np.exp(-tt / 0.04)
    mix_at(b, clank, at(0.5), 0.55)
    return verb(fade(b, 0, 0.05), ROOM, 0.2, 0.72)


# ================================================================== the Deep
def spit():
    """Inkspitter: throat gurgle then a wet ink 'ptoo' launch with droplets."""
    b = buf(0.42)
    n = at(0.14)
    tt = tvec(n)
    g = saw(110 + 200 * tt / 0.14, n) * (1 + 0.9 * np.sin(2 * np.pi * 32 * tt))
    g = peak_bp(g, 450, 3) + 0.5 * peak_bp(g, 900, 4)
    mix_at(b, g * adsr(n, 0.02, 0.03, 0.8, 0.04), 0, 0.5)
    s = at(0.12)
    m = len(b) - s
    t2 = tvec(m)
    burst = bp(noise(m, 90), 500, 4000) * np.exp(-t2 / 0.035) * (1 - np.exp(-t2 / 0.003))
    tone = sine(600 * (1 - 0.5 * np.clip(t2 / 0.1, 0, 1)), m) * np.exp(-t2 / 0.04)
    mix_at(b, burst * 0.9 + 0.5 * tone, s, 1.0)
    mix_at(b, squelch(0.16, seed=91, f=1100, drop=0.6), s, 0.5)
    r = np.random.default_rng(92)
    for k in range(6):
        st = 0.15 + r.uniform(0, 0.2)
        k2 = at(0.025)
        t3 = tvec(k2)
        mix_at(b, sine(r.uniform(600, 1600) * (1 + 3 * t3 / 0.025), k2) * np.exp(-t3 / 0.008), at(st), 0.2)
    return verb(fade(b, 0.001, 0.05), ROOM, 0.15, 0.42)


def bloater_burst():
    """Pufferghast pops: tight pop, wet squelch, spray, long carbonated fizz."""
    b = buf(0.9)
    n = len(b)
    t = tvec(n)
    b += 0.9 * sine(95 * (1 + 1.5 * np.exp(-t / 0.01)), n) * np.exp(-t / 0.07)
    b += 0.8 * hp(noise(n, 100), 800) * np.exp(-t / 0.008)
    b += 0.7 * sweep_lp(noise(n, 101), 4000, 300, curve=0.5) * np.exp(-t / 0.08)
    mix_at(b, squelch(0.3, seed=102, f=600, drop=0.6), at(0.01), 0.7)
    mix_at(b, splash(0.5, seed=103, size=0.6, bubbles=8), at(0.02), 0.4)
    mix_at(b, fizz(0.85, seed=104, rate=1400, tau=0.3), at(0.03), 0.45)
    r = np.random.default_rng(105)
    for k in range(12):
        s = r.uniform(0.06, 0.6)
        m = at(0.03)
        tt = tvec(m)
        bub = sine(r.uniform(300, 1200) * (1 + 3 * tt / 0.03), m) * np.exp(-tt / 0.01)
        mix_at(b, bub, at(s), 0.22 * np.exp(-s / 0.35))
    return verb(fade(softclip(b, 1.3), 0, 0.15), ROOM, 0.2, 0.9)


def warden_die():
    """A crew member falls: short pained 'oof' grunt, body thump on deck/sand, dropped-cutlass clank."""
    b = buf(0.65)
    n = at(0.2)
    tt = tvec(n)
    f = 135 * (1 + 0.12 * np.exp(-tt / 0.02)) * (1 - 0.22 * np.clip(tt / 0.18, 0, 1))
    src = lp(saw(f, n) + 0.5 * saw(f * 1.004, n, 0.4), 900, 2)  # soft glottal source, not buzzy
    src = src + 0.35 * bp(noise(n, 110), 300, 3000)  # breath
    v = peak_bp(src, 620, 6) + 0.6 * peak_bp(src, 1150, 8) + 0.15 * peak_bp(src, 2400, 10) + 0.3 * lp(src, 400)
    v = v * adsr(n, 0.012, 0.05, 0.55, 0.1)
    v[: at(0.03)] += hp(noise(at(0.03), 111), 800) * np.linspace(0.4, 0, at(0.03))  # 'h' burst
    mix_at(b, v, 0, 0.9)
    n2 = at(0.35)
    t2 = tvec(n2)
    thump = sine(95 * (1 + 0.8 * np.exp(-t2 / 0.015)), n2) * np.exp(-t2 / 0.08)
    thump += 0.8 * lp(noise(n2, 112), 700) * np.exp(-t2 / 0.04)
    thump += 0.4 * bp(noise(n2, 113), 300, 1500) * np.exp(-t2 / 0.02)
    mix_at(b, thump, at(0.16), 0.75)
    n3 = at(0.3)
    t3 = tvec(n3)
    clank = metal([1870, 3120, 4650, 6020], [0.09, 0.06, 0.04, 0.03], n3, [1, 0.6, 0.4, 0.2], seed=114)
    clank += 0.5 * hp(noise(n3, 115), 2500) * np.exp(-t3 / 0.004)
    mix_at(b, clank, at(0.27), 0.22)
    mix_at(b, clank * 0.5, at(0.33), 0.12)
    return verb(fade(b, 0, 0.08), ROOM, 0.18, 0.65)


def hollow_die():
    """Drowner dies: gurgling, squelchy moan sinking down, then a splash."""
    b = buf(0.8)
    n = at(0.45)
    t = tvec(n)
    f = 170 * (1 - 0.45 * np.clip(t / 0.4, 0, 1))
    src = saw(f, n) * (1 + 0.8 * np.sin(2 * np.pi * (28 + 20 * t) * t))  # gurgle
    moan = peak_bp(src, 550, 5) + 0.6 * peak_bp(src, 950, 7) + 0.2 * peak_bp(src, 2400, 8)
    mix_at(b, moan * adsr(n, 0.02, 0.1, 0.6, 0.25), 0, 0.6)
    mix_at(b, squelch(0.3, seed=120, f=650, drop=0.6), at(0.05), 0.7)
    mix_at(b, splash(0.5, seed=121, size=0.8, bubbles=12), at(0.3), 0.6)
    n2 = at(0.3)
    t2 = tvec(n2)
    mix_at(b, sine(110 * (1 + 0.6 * np.exp(-t2 / 0.02)), n2) * np.exp(-t2 / 0.07), at(0.3), 0.5)
    return verb(fade(b, 0, 0.1), ROOM, 0.22, 0.8)


# ================================================================== the Gullwake (fort)
def castle_hit():
    """Hull struck: timber crack, a hollow hull boom, and a groaning creak."""
    b = buf(0.8)
    n = len(b)
    t = tvec(n)
    b += 0.9 * sine(88 * (1 + 1.0 * np.exp(-t / 0.015)), n) * np.exp(-t / 0.14)
    b += 0.6 * lp(noise(n, 131), 900, 2) * np.exp(-t / 0.06)
    b += 0.5 * metal([180, 265, 410], [0.12, 0.09, 0.06], n, [1, 0.7, 0.4], seed=3)  # hollow hull body
    mix_at(b, wood_crack(seed=132, size=1.0, snaps=6), 0, 0.8)
    mix_at(b, creak(0.45, 55, 25, seed=133), at(0.2), 1.6)
    r = np.random.default_rng(134)
    for k in range(8):
        s = r.uniform(0.04, 0.35)
        m = at(0.02)
        mix_at(b, bp(noise(m, 140 + k), 1500, 6000) * exp_env(m, 0.004), at(s), r.uniform(0.1, 0.25))
    return verb(fade(softclip(b, 1.4), 0, 0.12), ROOM, 0.22, 0.8)


def castle_crumble():
    """The Gullwake breaks: groaning timbers, a run of cracks, beams crashing down, a final splash."""
    b = buf(1.9)
    n = len(b)
    t = tvec(n)
    b += lp(noise(n, 150), 220, 2) * adsr(n, 0.05, 0.3, 0.7, 1.0) * 1.6
    mix_at(b, creak(1.0, 22, 60, seed=151, res=(380, 760, 1350)), 0, 2.0)
    r = np.random.default_rng(152)
    for k in range(7):  # cracks
        s = 0.05 + k * r.uniform(0.07, 0.14)
        mix_at(b, wood_crack(seed=160 + k, size=1.2, snaps=6), at(s), r.uniform(0.5, 0.8))
    for k in range(6):  # beams crashing
        s = r.uniform(0.35, 1.2)
        m = at(0.45)
        tt = tvec(m)
        beam = sine(r.uniform(75, 110) * (1 + 0.8 * np.exp(-tt / 0.015)), m) * np.exp(-tt / 0.12)
        beam += 0.5 * metal([r.uniform(150, 220), r.uniform(300, 420)], [0.1, 0.07], m, [1, 0.6], seed=k)
        beam += 0.6 * lp(noise(m, 170 + k), 1200) * np.exp(-tt / 0.04)
        mix_at(b, beam, at(s), r.uniform(0.4, 0.7))
    for k in range(40):
        s = r.uniform(0.05, 1.4)
        m = at(0.02)
        mix_at(b, bp(noise(m, 200 + k), 1200, 6000) * exp_env(m, 0.005), at(s), r.uniform(0.05, 0.2) * np.exp(-s / 0.9))
    mix_at(b, splash(0.7, seed=180, size=1.4, bubbles=18), at(1.05), 0.7)
    return verb(fade(softclip(b, 1.5), 0, 0.3), HALL, 0.25, 1.9)


# ================================================================== rewards
def coin():
    """Doubloon clink: heavy gold, two touches and a short spin ring."""
    b = buf(0.32)
    for i, s in enumerate((0.0, 0.05)):
        n = at(0.26)
        g = 1.0 if i == 0 else 0.6
        m = metal([2380 * (1 + 0.025 * i), 3610, 5240, 6890, 8450], [0.09, 0.06, 0.04, 0.025, 0.015], n,
                  [1, 0.7, 0.45, 0.3, 0.15], seed=i)
        mix_at(b, m, at(s), 0.5 * g)
        mix_at(b, click(0.0015, 5000, i), at(s), 0.35 * g)
    return verb(fade(b, 0, 0.04), ROOM, 0.15, 0.32)


def ember_rain():
    """Broadside: a distant ragged volley of cannons rolling along the line."""
    b = buf(1.3)
    r = np.random.default_rng(181)
    s = 0.0
    for k in range(7):
        x = cannon(seed=190 + k, size=0.8, dist=0.55 + 0.05 * (k % 3), dur=0.9)
        mix_at(b, x, at(s), r.uniform(0.45, 0.7) * (1 - 0.05 * k))
        s += r.uniform(0.05, 0.12)
    n = len(b)
    t = tvec(n)
    b += 0.5 * lp(noise(n, 182), 300, 2) * adsr(n, 0.05, 0.2, 0.6, 0.6)
    return verb(fade(softclip(b, 1.3), 0.002, 0.2), HALL, 0.35, 1.3)


def ship_bell(f0=880, dur=1.2, seed=0, strike=0.6):
    """Small brass ship's bell: bright, a little clangy."""
    return bell(f0, dur, decay=0.55, seed=seed, strike=strike)


def rally():
    """Rally: ship's bell 'ding-ding', crew 'hey!' bark with stomps and a clap."""
    b = buf(1.1)
    mix_at(b, ship_bell(mtof(81), 1.0, seed=1), 0, 0.45)
    mix_at(b, ship_bell(mtof(81), 0.9, seed=2), at(0.17), 0.4)
    mix_at(b, stomp(seed=4, f=84), at(0.36), 0.8)
    mix_at(b, stomp(seed=5, f=88), at(0.5), 0.7)
    mix_at(b, shout(f0=185, dur=0.24, voices=8, seed=6, vowel="eh"), at(0.5), 0.55)
    mix_at(b, clap(seed=7, people=5), at(0.5), 0.4)
    return verb(fade(b, 0, 0.2), HALL, 0.22, 1.1)


def bell_toll():
    """Ship's bell, two pairs (ding-ding, ding-ding), a deck stomp and a short crew 'hey'."""
    b = buf(1.6)
    for k, s in enumerate((0.0, 0.16, 0.5, 0.66)):
        mix_at(b, ship_bell(mtof(79), 1.0, seed=7 + k), at(s), 0.45 - 0.03 * (k % 2))
    mix_at(b, stomp(seed=9, f=84), at(0.9), 0.65)
    mix_at(b, shout(f0=175, dur=0.2, voices=6, seed=10, vowel="eh"), at(0.9), 0.35)
    return verb(fade(b, 0, 0.4), HALL, 0.3, 1.6)


# ================================================================== hero
def hero_call():
    """Captain's call: a bosun's pipe, then the crew's cheer swelling up."""
    b = buf(1.25)
    mix_at(b, bosun_whistle(0.62, seed=10), 0, 0.42)
    n = at(0.75)
    tt = tvec(n)
    r = np.random.default_rng(11)
    cheer = np.zeros(n)
    for k in range(10):
        f0 = r.uniform(150, 260)
        x = shout(f0=f0, dur=0.6, voices=2, seed=20 + k, vowel=("ah" if k % 2 else "eh"), fall=-0.08)
        mix_at(cheer, x, at(r.uniform(0, 0.08)), r.uniform(0.5, 1.0))
    cheer = cheer * np.clip(tt / 0.3, 0, 1) ** 1.5
    mix_at(b, cheer, at(0.45), 0.45)
    mix_at(b, stomp(seed=12, f=84), at(0.55), 0.55)
    mix_at(b, clap(seed=13, people=6), at(0.62), 0.35)
    return verb(fade(b, 0, 0.2), HALL, 0.25, 1.25)


def hero_flare():
    """Flare pistol: pop, a fizzing whoosh climbing away, a crackling burst."""
    b = buf(0.85)
    n0 = at(0.15)
    t0 = tvec(n0)
    pop = hp(noise(n0, 209), 900) * np.exp(-t0 / 0.006) + 0.7 * sine(220 * (1 + np.exp(-t0 / 0.008)), n0) * np.exp(-t0 / 0.03)
    mix_at(b, softclip(pop, 1.5), 0, 0.9)
    n = len(b)
    t = tvec(n)
    wh = sweep_lp(bp(noise(n, 210), 500, 9000), 600, 8000, curve=0.8) * adsr(n, 0.06, 0.05, 0.6, 0.4)
    b += 0.5 * wh
    mix_at(b, fizz(0.7, seed=211, rate=1600, tau=0.4), at(0.03), 0.4)
    st = at(0.48)
    m = n - st
    tt = tvec(m)
    burst = hp(noise(m, 212), 1500) * np.exp(-tt / 0.004)
    burst += 0.4 * sine(1320, m) * np.exp(-tt / 0.1) + 0.25 * sine(1980, m) * np.exp(-tt / 0.08)
    mix_at(b, burst, st, 0.4)
    mix_at(b, fizz(0.35, seed=213, rate=2500, tau=0.12), st, 0.4)
    return verb(fade(b, 0.003, 0.12), ROOM, 0.3, 0.85)


# ================================================================== boss
def boss_roar():
    """Mother Fathom bellows: deep, wet, whale-like, with a bubbling throat."""
    b = buf(1.7)
    n = len(b)
    t = tvec(n)
    f = np.interp(t / 1.6, [0, 0.25, 0.6, 1.0], [70, 96, 84, 62]) * (1 + 0.025 * np.sin(2 * np.pi * 9 * t))
    src = saw(f, n) + 0.7 * saw(f * 1.007, n, 0.3) + 0.4 * square(f * 0.5, n)
    src *= 1 + 0.6 * lp(noise(n, 220), 35, 1) * 7
    v = peak_bp(src, 380, 4) + 0.9 * peak_bp(src, 720, 5) + 0.45 * peak_bp(src, 1500, 6) + 0.2 * peak_bp(src, 2600, 7)
    env = adsr(n, 0.15, 0.2, 0.85, 0.6)
    b += 1.2 * v * env
    mix_at(b, whale([140, 190, 165, 120], 1.2, seed=221, a=0.2, r=0.3, growl=0.0), 0, 0.35)
    gurgle = bp(noise(n, 222), 300, 2000) * (1 + np.sin(2 * np.pi * (24 + 8 * t) * t))
    b += 0.35 * gurgle * env
    r = np.random.default_rng(223)
    for k in range(16):
        s = r.uniform(0.1, 1.4)
        m = at(0.035)
        tt = tvec(m)
        mix_at(b, sine(r.uniform(250, 900) * (1 + 2.5 * tt / 0.035), m) * np.exp(-tt / 0.01), at(s), 0.15)
    b = softclip(b * 0.8, 2.0)
    return verb(fade(b, 0.005, 0.35), HALL, 0.32, 1.7)


def boss_warn():
    """Rising eerie warning: a choir cluster and a theremin-like wail climbing, drums accelerating."""
    b = buf(1.5)
    n = len(b)
    t = tvec(n)
    rise = 2 ** (np.clip(t / 1.3, 0, 1) * 7 / 12)
    for k, m in enumerate((57, 58, 64)):  # A, Bb, E: cluster with a tritone
        x = choir(mtof(m), 1.25, vowel="oo", a=0.5, r=0.2, voices=5, seed=k)
        mix_at(b, x[:n], 0, 0.22)
    wf = mtof(76) * rise * (1 + 0.012 * np.sin(2 * np.pi * 6 * t))
    wail = sine(wf, n) + 0.25 * sine(2 * wf, n) + 0.1 * sine(3 * wf, n)
    b += 0.3 * wail * adsr(n, 0.4, 0.1, 0.9, 0.25)
    mix_at(b, whale([110, 150, 220], 1.3, seed=232, a=0.3, r=0.15, growl=0.6), 0, 0.12)
    for i, s in enumerate((0.0, 0.42, 0.72, 0.92, 1.06, 1.16)):
        mix_at(b, taiko(90, 0.45, seed=230 + i), at(s), 0.16 + 0.04 * i)
        mix_at(b, stomp(seed=240 + i, f=88), at(s), 0.16 + 0.03 * i)
    mix_at(b, cymbal(1.3, swell=True, seed=231), 0, 0.2)
    return verb(fade(b, 0.005, 0.15), HALL, 0.3, 1.5)


def boss_slam():
    """Huge tentacle slam: wet whoosh down, a massive slap on the deck, splinters, big splash."""
    b = buf(1.3)
    n = len(b)
    t = tvec(n)
    pre = at(0.12)
    wh = sweep_lp(bp(noise(pre, 239), 200, 4000), 3000, 500, curve=1.0) * np.linspace(0, 1, pre) ** 2
    mix_at(b, wh, 0, 0.5)
    s = pre
    m = n - s
    tt = tvec(m)
    slap = bp(noise(m, 240), 300, 3000) * np.exp(-tt / 0.02) * 1.3
    body = sine(76 * (1 + 2.0 * np.exp(-tt / 0.02)), m) * np.exp(-tt / 0.25)
    thud = bp(noise(m, 241), 120, 900) * np.exp(-tt / 0.08)
    mix_at(b, hp(slap * 1.3 + 0.8 * body + 1.1 * thud, 60, 2), s, 1.0)
    mix_at(b, squelch(0.35, seed=242, f=400, drop=0.5), s, 0.7)
    mix_at(b, wood_crack(seed=243, size=1.3, snaps=7), s + at(0.01), 0.55)
    mix_at(b, splash(1.0, seed=244, size=1.7, bubbles=22), s + at(0.03), 0.85)
    mix_at(b, click(0.005, 500, 245), s, 0.9)
    return verb(fade(softclip(b, 1.8), 0, 0.2), HALL, 0.22, 1.3)


# ================================================================== outcome
def win():
    """Victory sting: ding-ding, a squeezebox + fiddle 'yo-ho' figure, D major chord, crew stomp."""
    b = buf(1.4)
    seq = [(69, 0.0, 0.1), (74, 0.11, 0.1), (78, 0.22, 0.12), (81, 0.36, 0.7)]
    for i, (m, s, d) in enumerate(seq):
        mix_at(b, fiddle(mtof(m), d, seed=20 + i, a=0.008, r=0.12, vdepth=0.003 if d > 0.3 else 0), at(s), 0.32)
        mix_at(b, accordion(mtof(m - 12), d, seed=30 + i, a=0.006, r=0.1), at(s), 0.25)
    for m in (50, 57, 62, 66):
        mix_at(b, brass(mtof(m), 0.6, vel=0.85, a=0.02, r=0.3, seed=m), at(0.36), 0.15)
    mix_at(b, stomp(seed=5, f=82), at(0.36), 0.8)
    mix_at(b, clap(seed=6, people=5), at(0.36), 0.35)
    mix_at(b, shout(f0=150, dur=0.5, voices=8, seed=7, vowel="oh_lo", fall=0.04), at(0.36), 0.3)
    mix_at(b, ship_bell(mtof(86), 0.9, seed=8, strike=0.3), at(0.36), 0.18)
    mix_at(b, ship_bell(mtof(86), 0.8, seed=9, strike=0.3), at(0.52), 0.15)
    return verb(fade(b, 0, 0.3), HALL, 0.28, 1.4)


def lose():
    """Defeat sting: a sagging minor squeezebox line, low creak, a wave washing over."""
    b = buf(1.7)
    for i, (m, s, d) in enumerate(((69, 0.0, 0.35), (65, 0.36, 0.35), (62, 0.72, 0.7))):
        mix_at(b, accordion(mtof(m), d, seed=40 + i, a=0.04, r=0.3, bellows=0.3, bright=0.6), at(s), 0.3)
        mix_at(b, fiddle(mtof(m - 12), d, seed=50 + i, a=0.06, r=0.3, bright=0.5), at(s), 0.18)
    mix_at(b, accordion(mtof(50), 1.2, seed=60, a=0.1, r=0.4, bellows=0.5), 0, 0.12)
    mix_at(b, creak(0.8, 40, 20, seed=61), at(0.6), 1.2)
    mix_at(b, wave_wash(1.0, seed=62, bright=0.7), at(0.7), 0.6)
    mix_at(b, taiko(70, 0.9, seed=7, skin=0.6), at(0.72), 0.35)
    return verb(fade(b, 0, 0.35), HALL, 0.3, 1.7)


SFX = {
    "ui_tap": (ui_tap, 0.5), "ui_back": (ui_back, 0.5), "ui_upgrade": (ui_upgrade, 0.6),
    "ui_locked": (ui_locked, 0.5), "unit_send": (unit_send, 0.6), "energy_full": (energy_full, 0.55),
    "hit_blade": (hit_blade, 0.55), "hit_blunt": (hit_blunt, 0.6), "hit_claw": (hit_claw, 0.55),
    "arrow_fire": (arrow_fire, 0.45), "arrow_hit": (arrow_hit, 0.45), "bolt_fire": (bolt_fire, 0.75),
    "bolt_hit": (bolt_hit, 0.75), "ballista_reload": (ballista_reload, 0.45), "spit": (spit, 0.5),
    "bloater_burst": (bloater_burst, 0.7), "warden_die": (warden_die, 0.45), "hollow_die": (hollow_die, 0.55),
    "castle_hit": (castle_hit, 0.75), "castle_crumble": (castle_crumble, 0.9), "coin": (coin, 0.45),
    "star": (star, 0.65), "ember_rain": (ember_rain, 0.6), "rally": (rally, 0.75), "bell": (bell_toll, 0.75),
    "heal": (heal, 0.55), "hero_call": (hero_call, 0.8), "hero_flare": (hero_flare, 0.7),
    "boss_roar": (boss_roar, 0.9), "boss_warn": (boss_warn, 0.8), "boss_slam": (boss_slam, 0.9),
    "win": (win, 0.8), "lose": (lose, 0.75),
}


TARGET_LOUD_DB = -12.0  # short-term (300 ms) RMS target before the manifest vol


def build(ids=None, bitrate=96000):
    results = {}
    for sid in ids or SFX:
        fn, vol = SFX[sid]
        x = fn().astype(np.float64)
        x = hp(lp(x, 15000, 2), 25, 2)  # tame AAC overshoot, kill DC / sub-rumble
        x = fade(x - np.mean(x), 0.0005, 0.01)
        loud = A.short_term_loudness_db(x)
        x = x * undb(TARGET_LOUD_DB - loud)
        x = limit(x, undb(-1.5), max_red_db=7.0)
        x = x * min(1.0, undb(-1.5) / max(peak(x), 1e-9))
        A.write_wav(x, "sfx_" + sid)
        _, dpk = A.encode_safe(x, sid, bitrate)
        results[sid] = vol
        print(f"{sid:16s} {len(x)/SR:5.2f}s loud {A.short_term_loudness_db(x):6.1f} dB peak {db(peak(x)):5.1f} decoded {dpk:5.1f}", flush=True)
    return results


if __name__ == "__main__":
    build(sys.argv[1:] or None)
