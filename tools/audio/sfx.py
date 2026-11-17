"""All Siegeline sound effects. Run: .venv/bin/python tools/audio/sfx.py [id ...]

Each sound = layered synthesis (transient + filtered noise + pitched body), then a small
room reverb where useful, loudness-normalised with a -1 dBFS peak ceiling.
"""
import sys
import json
import numpy as np

from synth import (SR, n_of, tvec, noise, exp_env, adsr, fade, sine, saw, square, tri, mtof,
                   lp, hp, bp, peak_bp, sweep_lp, normalize, softclip, mix_at, make_ir,
                   reverb, undb, peak, db)
from instruments import (brass, strings, choir, bell, metal, pluck, taiko, frame_drum, snare,
                         hat, cymbal, boom, click, flute)
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


# ================================================================== UI
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


# ================================================================== troops & energy
def unit_send():
    b = buf(0.5)
    h = brass(mtof(50), 0.22, vel=0.9, a=0.03, r=0.12, seed=2)  # D3 horn blip
    h2 = brass(mtof(57), 0.18, vel=0.7, a=0.02, r=0.1, seed=3)
    mix_at(b, h, 0, 0.55)
    mix_at(b, h2, at(0.04), 0.35)
    mix_at(b, frame_drum(95, 0.3, seed=1), 0, 0.8)
    mix_at(b, field_tap(), 0, 0.5)
    return verb(b, ROOM, 0.3, 0.5)


def field_tap():
    n = at(0.06)
    return bp(noise(n, 8), 800, 4000) * exp_env(n, 0.012)


def energy_full():
    b = buf(0.6)
    n = len(b)
    t = tvec(n)
    f = 700 * 2 ** (1.2 * np.clip(t / 0.25, 0, 1))
    sweep = (sine(f, n) + 0.4 * sine(f * 1.5, n)) * adsr(n, 0.02, 0.2, 0.3, 0.3) * 0.35
    b += sweep
    for i, m in enumerate((81, 88)):
        mix_at(b, bell(mtof(m), 0.4, decay=0.3, seed=i, strike=0.1), at(0.18 + 0.08 * i), 0.4)
    b += hp(noise(n, 3), 5000) * adsr(n, 0.2, 0.1, 0.3, 0.25) * 0.06
    return verb(b, ROOM, 0.3, 0.6)


# ================================================================== hits
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


def hit_claw():
    b = buf(0.34)
    for i, (d, f) in enumerate(((0.0, 3200), (0.045, 2600), (0.085, 2100))):
        n = at(0.09)
        tt = tvec(n)
        scr = bp(noise(n, 20 + i), f * 0.6, f * 1.6) * np.exp(-tt / 0.025)
        scr *= 1 + 0.6 * np.sin(2 * np.pi * 90 * tt)  # rasp
        mix_at(b, scr, at(d), 0.7)
    n = len(b)
    t = tvec(n)
    b += 0.7 * sine(130 * (1 + 0.6 * np.exp(-t / 0.02)), n) * np.exp(-t / 0.06)
    b += 0.5 * lp(noise(n, 25), 600) * np.exp(-t / 0.04)
    return verb(fade(b, 0, 0.05), ROOM, 0.15, 0.34)


def arrow_fire():
    b = buf(0.38)
    tw = pluck(98, 0.3, bright=0.3, seed=3, damp=0.985)
    tw *= exp_env(len(tw), 0.08)
    mix_at(b, tw, 0, 0.8)
    n = len(b)
    t = tvec(n)
    wh = noise(n, 31)
    wh = bp(wh, 1200, 6000) * np.exp(-((t - 0.09) / 0.06) ** 2)
    b += 0.5 * wh
    mix_at(b, click(0.002, 3000, 2), 0, 0.5)
    return fade(b, 0, 0.06)


def arrow_hit():
    b = buf(0.22)
    n = len(b)
    t = tvec(n)
    b += 0.8 * bp(noise(n, 40), 900, 3500) * np.exp(-t / 0.012)
    b += 0.6 * sine(420 * (1 + 0.3 * np.exp(-t / 0.005)), n) * np.exp(-t / 0.035)
    b += 0.4 * sine(230, n) * np.exp(-t / 0.06)
    mix_at(b, click(0.0015, 3000, 4), 0, 0.8)
    # quiver of the shaft
    b += 0.12 * sine(180, n) * np.exp(-t / 0.08) * np.sin(2 * np.pi * 28 * t)
    return verb(fade(b, 0, 0.04), ROOM, 0.15, 0.22)


def bolt_fire():
    b = buf(0.62)
    n = len(b)
    t = tvec(n)
    thunk = sine(72 * (1 + 1.2 * np.exp(-t / 0.02)), n) * np.exp(-t / 0.12)
    wood = lp(noise(n, 50), 500, 2) * np.exp(-t / 0.05)
    clack = bp(noise(n, 51), 1200, 4000) * np.exp(-t / 0.008)
    b += 1.0 * thunk + 0.9 * wood + 0.5 * clack
    # whistle: bolt flying away, doppler drop
    st = 0.05
    m = t > st
    tt = np.clip(t - st, 0, None)
    wf = 2600 * (1 - 0.3 * np.clip(tt / 0.5, 0, 1))
    whistle = (sine(wf, n) * 0.5 + bp(noise(n, 52), 1800, 3500)) * m
    whistle *= np.clip(tt / 0.04, 0, 1) * np.exp(-tt / 0.22)
    b += 0.22 * whistle
    mix_at(b, click(0.003, 1500, 6), 0, 0.7)
    return verb(fade(softclip(b, 1.3), 0, 0.08), ROOM, 0.2, 0.62)


def bolt_hit():
    b = buf(0.95)
    n = len(b)
    t = tvec(n)
    b += 1.0 * boom(50, 0.95, drop=2.2, tau=0.28, seed=60)
    roar = sweep_lp(noise(n, 61), 4500, 250, curve=0.6) * np.exp(-t / 0.22)
    b += 0.9 * roar
    # crackle: sparse embers
    r = np.random.default_rng(62)
    for k in range(40):
        s = r.uniform(0.03, 0.8)
        c = click(0.0015, 2500, 70 + k) * r.uniform(0.2, 0.6) * np.exp(-s / 0.4)
        mix_at(b, c, at(s))
    mix_at(b, click(0.004, 800, 63), 0, 1.0)
    return verb(fade(softclip(b, 1.6), 0, 0.15), ROOM, 0.25, 0.95)


def ballista_reload():
    b = buf(0.62)
    for i in range(5):
        s = 0.04 + i * 0.075
        n = at(0.04)
        tt = tvec(n)
        c = bp(noise(n, 80 + i), 1500, 5000) * np.exp(-tt / 0.006)
        c += 0.5 * sine(900 + 60 * i, n) * np.exp(-tt / 0.01)
        mix_at(b, c, at(s), 0.6 + 0.05 * i)
    # rope creak
    n = at(0.4)
    tt = tvec(n)
    creak = bp(saw(70 + 30 * tt, n) * (1 + np.sin(2 * np.pi * 23 * tt)), 600, 2500)
    mix_at(b, creak * adsr(n, 0.05, 0.1, 0.6, 0.15), at(0.03), 0.15)
    # latch clunk
    n = at(0.15)
    tt = tvec(n)
    cl = sine(160 * (1 + np.exp(-tt / 0.01)), n) * np.exp(-tt / 0.04) + lp(noise(n, 88), 900) * np.exp(-tt / 0.02)
    mix_at(b, cl, at(0.46), 0.9)
    return verb(fade(b, 0, 0.04), ROOM, 0.2, 0.62)


# ================================================================== hollows
def spit():
    b = buf(0.32)
    n = len(b)
    t = tvec(n)
    b += bp(noise(n, 90), 700, 3500) * np.exp(-t / 0.04) * 0.8
    b += 0.6 * sine(500 * (1 - 0.5 * np.clip(t / 0.12, 0, 1)), n) * np.exp(-t / 0.05)
    r = np.random.default_rng(91)
    for k in range(5):
        s = 0.05 + r.uniform(0, 0.15)
        m = at(0.03)
        tt = tvec(m)
        bub = sine(400 + r.uniform(0, 600) + 3000 * tt, m) * np.exp(-tt / 0.01)
        mix_at(b, bub, at(s), 0.25)
    return verb(fade(b, 0.001, 0.05), ROOM, 0.15, 0.32)


def bloater_burst():
    b = buf(0.65)
    n = len(b)
    t = tvec(n)
    b += 1.0 * boom(70, 0.65, drop=1.0, tau=0.15, seed=100)
    b += 0.8 * sweep_lp(noise(n, 101), 3500, 300, curve=0.5) * np.exp(-t / 0.12)
    r = np.random.default_rng(102)
    for k in range(10):
        s = r.uniform(0.04, 0.45)
        m = at(0.04)
        tt = tvec(m)
        f0 = r.uniform(150, 500)
        bub = sine(f0 * (1 + 4 * tt / 0.04), m) * np.exp(-tt / 0.012)
        mix_at(b, bub, at(s), 0.3 * np.exp(-s / 0.3))
    return verb(fade(softclip(b, 1.4), 0, 0.1), ROOM, 0.2, 0.65)


def warden_die():
    b = buf(0.65)
    # armour clatter: a few metal hits
    r = np.random.default_rng(110)
    for k, s in enumerate((0.0, 0.11, 0.19)):
        n = at(0.25)
        fs = [r.uniform(900, 1500), r.uniform(1900, 2600), r.uniform(3100, 4200)]
        m = metal(fs, [0.08, 0.06, 0.04], n, [1, 0.6, 0.4], seed=k)
        m += bp(noise(n, 111 + k), 1500, 6000) * exp_env(n, 0.01)
        mix_at(b, m, at(s), 0.35 - 0.06 * k)
    # body fall thud
    n = at(0.4)
    tt = tvec(n)
    th = sine(80 * (1 + 0.8 * np.exp(-tt / 0.02)), n) * np.exp(-tt / 0.12) + lp(noise(n, 115), 400) * np.exp(-tt / 0.06)
    mix_at(b, th, at(0.16), 0.9)
    # lantern goes out: soft falling tone
    n = at(0.4)
    tt = tvec(n)
    lant = sine(660 * (1 - 0.35 * tt / 0.4), n) * adsr(n, 0.01, 0.1, 0.4, 0.25)
    mix_at(b, lant, at(0.22), 0.12)
    return verb(fade(b, 0, 0.08), ROOM, 0.22, 0.65)


def hollow_die():
    b = buf(0.65)
    n = len(b)
    t = tvec(n)
    # hollow moan: formant-filtered saw gliding down
    f = 160 * (1 - 0.4 * np.clip(t / 0.5, 0, 1))
    src = saw(f, n)
    moan = peak_bp(src, 600, 6) + 0.6 * peak_bp(src, 1000, 8)
    b += 0.6 * moan * adsr(n, 0.02, 0.1, 0.6, 0.35)
    # ash crumble: crackle bed
    crum = bp(noise(n, 120), 800, 6000) * adsr(n, 0.01, 0.1, 0.5, 0.4)
    gr = (np.random.default_rng(121).random(n) > 0.985).astype(float)
    b += 0.5 * crum * (0.5 + lp(gr, 2000, 1) * 6)
    b += 0.5 * lp(noise(n, 122), 300) * np.exp(-t / 0.08)
    return verb(fade(b, 0, 0.1), ROOM, 0.25, 0.65)


# ================================================================== castle
def castle_hit():
    b = buf(0.65)
    n = len(b)
    t = tvec(n)
    b += 1.0 * boom(48, 0.65, drop=1.5, tau=0.22, seed=130)
    b += 0.8 * lp(noise(n, 131), 1100, 2) * np.exp(-t / 0.08)
    b += 0.4 * bp(noise(n, 132), 300, 900) * np.exp(-t / 0.15)
    r = np.random.default_rng(133)
    for k in range(14):
        s = r.uniform(0.05, 0.5)
        m = at(0.02)
        mix_at(b, bp(noise(m, 140 + k), 1500, 6000) * exp_env(m, 0.004), at(s), r.uniform(0.1, 0.35))
    mix_at(b, click(0.004, 600, 134), 0, 0.8)
    return verb(fade(softclip(b, 1.5), 0, 0.1), ROOM, 0.25, 0.65)


def castle_crumble():
    b = buf(1.6)
    n = len(b)
    t = tvec(n)
    rumble = lp(noise(n, 150), 180, 2) * adsr(n, 0.05, 0.3, 0.7, 0.9) * 2.5
    b += rumble
    mix_at(b, boom(40, 1.4, drop=1.2, tau=0.5, seed=151), 0, 0.9)
    r = np.random.default_rng(152)
    for k in range(9):  # big chunks falling
        s = r.uniform(0.1, 1.1)
        mix_at(b, boom(r.uniform(55, 90), 0.4, drop=1.0, tau=0.1, seed=160 + k), at(s), r.uniform(0.3, 0.6))
    for k in range(50):  # debris
        s = r.uniform(0.05, 1.4)
        m = at(0.02)
        mix_at(b, bp(noise(m, 200 + k), 1200, 6000) * exp_env(m, 0.005), at(s), r.uniform(0.05, 0.25) * np.exp(-s / 0.9))
    return verb(fade(softclip(b, 1.6), 0, 0.3), HALL, 0.25, 1.6)


# ================================================================== rewards
def coin():
    b = buf(0.3)
    for i, s in enumerate((0.0, 0.045)):
        n = at(0.25)
        g = 1.0 if i == 0 else 0.6
        m = metal([2640 * (1 + 0.03 * i), 4020, 5930, 7400], [0.08, 0.05, 0.035, 0.02], n,
                  [1, 0.6, 0.4, 0.2], seed=i)
        mix_at(b, m, at(s), 0.5 * g)
        mix_at(b, click(0.0015, 5000, i), at(s), 0.4 * g)
    return verb(fade(b, 0, 0.04), ROOM, 0.15, 0.3)


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


def ember_rain():
    b = buf(0.95)
    n = len(b)
    t = tvec(n)
    whoosh = bp(noise(n, 180), 300, 3000) * adsr(n, 0.15, 0.2, 0.6, 0.5)
    b += 0.6 * sweep_lp(whoosh, 1200, 4500, curve=1.0)
    r = np.random.default_rng(181)
    for k in range(70):
        s = r.uniform(0.05, 0.85)
        mix_at(b, click(0.0012, 2000, 300 + k), at(s), r.uniform(0.15, 0.5))
    for k in range(8):  # small impacts landing
        s = r.uniform(0.3, 0.85)
        m = at(0.06)
        tt = tvec(m)
        mix_at(b, lp(noise(m, 400 + k), 1200) * np.exp(-tt / 0.015), at(s), 0.35)
    return verb(fade(b, 0.01, 0.15), ROOM, 0.25, 0.95)


def rally():
    """Hand-bell double strike over a brass hit: the call to rally."""
    b = buf(1.1)
    mix_at(b, bell(mtof(74), 1.0, decay=0.5, seed=1, strike=0.4), 0, 0.5)
    mix_at(b, bell(mtof(74), 0.9, decay=0.5, seed=2, strike=0.4), at(0.16), 0.45)
    mix_at(b, brass(mtof(62), 0.35, vel=0.9, a=0.02, seed=5), 0, 0.35)
    mix_at(b, brass(mtof(69), 0.3, vel=0.8, a=0.02, seed=6), at(0.16), 0.3)
    mix_at(b, taiko(70, 0.6, seed=4), 0, 0.5)
    return verb(fade(b, 0, 0.2), HALL, 0.25, 1.1)


def bell_toll():
    """Keep tower bell: single deep toll."""
    b = buf(1.6)
    mix_at(b, bell(mtof(50), 1.6, decay=1.0, seed=7, strike=0.6), 0, 0.8)
    mix_at(b, bell(mtof(62), 1.2, decay=0.6, seed=8, strike=0.2), 0, 0.2)
    return verb(fade(b, 0, 0.4), HALL, 0.3, 1.6)


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


# ================================================================== hero
def hero_call():
    b = buf(0.95)
    mix_at(b, brass(mtof(62), 0.28, vel=0.95, a=0.03, r=0.1, seed=10), 0, 0.5)
    mix_at(b, brass(mtof(69), 0.45, vel=1.0, a=0.03, r=0.25, seed=11), at(0.26), 0.55)
    mix_at(b, brass(mtof(57), 0.7, vel=0.8, a=0.05, r=0.25, seed=12), 0, 0.25)
    mix_at(b, taiko(60, 0.7, seed=3), 0, 0.5)
    mix_at(b, taiko(60, 0.7, seed=4), at(0.26), 0.45)
    return verb(fade(b, 0, 0.15), HALL, 0.25, 0.95)


def hero_flare():
    b = buf(0.65)
    n = len(b)
    t = tvec(n)
    wh = sweep_lp(noise(n, 210), 400, 8000, curve=1.0) * adsr(n, 0.12, 0.05, 0.5, 0.45)
    b += 0.6 * wh
    st = at(0.12)
    m = n - st
    tt = tvec(m)
    burst = (sine(880, m) + sine(1320, m) * 0.6 + sine(1760, m) * 0.3) * np.exp(-tt / 0.18)
    mix_at(b, burst, st, 0.25)
    mix_at(b, boom(80, 0.4, drop=1.0, tau=0.12, seed=211), st, 0.5)
    return verb(fade(b, 0.005, 0.12), ROOM, 0.3, 0.65)


# ================================================================== boss
def boss_roar():
    b = buf(1.5)
    n = len(b)
    t = tvec(n)
    f = 62 * (1 + 0.25 * np.sin(np.pi * np.clip(t / 1.3, 0, 1))) * (1 + 0.03 * np.sin(2 * np.pi * 13 * t))
    src = saw(f, n) + 0.8 * saw(f * 1.5, n, 0.2) + 0.5 * square(f * 0.5, n)
    src *= 1 + 0.5 * lp(noise(n, 220), 40) * 6  # roughness
    v = peak_bp(src, 450, 4) + 0.8 * peak_bp(src, 900, 5) + 0.3 * peak_bp(src, 2300, 6)
    gr = bp(noise(n, 221), 200, 2500) * 0.6
    env = adsr(n, 0.12, 0.2, 0.8, 0.6)
    b += (v * 1.2 + gr) * env
    b += 0.8 * lp(noise(n, 222), 120, 2) * env * 3
    b = softclip(b * 0.8, 2.0)
    return verb(fade(b, 0.005, 0.3), HALL, 0.3, 1.5)


def boss_warn():
    b = buf(1.3)
    n = len(b)
    t = tvec(n)
    f = mtof(45) * 2 ** (np.clip(t / 1.1, 0, 1) * 1.0)  # rises an octave
    horn = saw(f, n) + saw(f * 1.006, n, 0.4) + 0.5 * saw(f * 1.5, n)
    horn = lp(horn, 1800) * adsr(n, 0.25, 0.1, 0.9, 0.2)
    puls = 0.6 + 0.4 * (np.sin(2 * np.pi * 6 * t) > 0)
    b += 0.5 * horn * lp(puls, 60, 1)
    for i in range(4):
        mix_at(b, taiko(55, 0.5, seed=230 + i), at(0.3 * i), 0.45 + 0.1 * i)
    mix_at(b, cymbal(1.2, swell=True, seed=231), 0, 0.25)
    return verb(fade(b, 0.005, 0.15), HALL, 0.25, 1.3)


def boss_slam():
    b = buf(0.95)
    n = len(b)
    t = tvec(n)
    b += 1.2 * boom(38, 0.95, drop=2.5, tau=0.35, seed=240)
    b += 0.7 * lp(noise(n, 241), 1500) * np.exp(-t / 0.1)
    mix_at(b, cymbal(0.9, seed=242), 0, 0.25)
    r = np.random.default_rng(243)
    for k in range(20):
        s = r.uniform(0.05, 0.7)
        m = at(0.02)
        mix_at(b, bp(noise(m, 250 + k), 1000, 5000) * exp_env(m, 0.005), at(s), r.uniform(0.1, 0.3))
    mix_at(b, click(0.005, 500, 244), 0, 1.0)
    return verb(fade(softclip(b, 1.8), 0, 0.15), HALL, 0.22, 0.95)


# ================================================================== outcome
def win():
    b = buf(1.25)
    seq = [(62, 0.0, 0.14), (66, 0.13, 0.14), (69, 0.26, 0.14), (74, 0.39, 0.6)]
    for i, (m, s, d) in enumerate(seq):
        mix_at(b, brass(mtof(m), d, vel=1.0, a=0.02, r=0.2, seed=20 + i), at(s), 0.45)
    for m in (50, 57, 62):
        mix_at(b, brass(mtof(m), 0.6, vel=0.8, a=0.03, r=0.3, seed=m), at(0.39), 0.2)
    mix_at(b, taiko(60, 0.8, seed=5), at(0.39), 0.6)
    mix_at(b, cymbal(0.9, seed=6), at(0.39), 0.15)
    mix_at(b, bell(mtof(86), 0.8, decay=0.4, seed=8, strike=0.2), at(0.39), 0.15)
    return verb(fade(b, 0, 0.3), HALL, 0.3, 1.25)


def lose():
    b = buf(1.5)
    mix_at(b, brass(mtof(57), 0.4, vel=0.6, a=0.06, r=0.25, seed=30, bright=0.4), 0, 0.45)
    mix_at(b, brass(mtof(53), 0.4, vel=0.55, a=0.06, r=0.25, seed=31, bright=0.4), at(0.38), 0.45)
    mix_at(b, brass(mtof(50), 0.6, vel=0.5, a=0.08, r=0.4, seed=32, bright=0.3), at(0.76), 0.5)
    mix_at(b, strings(mtof(38), 1.0, vel=0.6, a=0.15, r=0.4, seed=1), 0, 0.3)
    mix_at(b, taiko(50, 0.9, seed=7), at(0.76), 0.35)
    return verb(fade(b, 0, 0.35), HALL, 0.3, 1.5)


SFX = {
    "ui_tap": (ui_tap, 0.5), "ui_back": (ui_back, 0.5), "ui_upgrade": (ui_upgrade, 0.6),
    "ui_locked": (ui_locked, 0.5), "unit_send": (unit_send, 0.6), "energy_full": (energy_full, 0.55),
    "hit_blade": (hit_blade, 0.55), "hit_blunt": (hit_blunt, 0.6), "hit_claw": (hit_claw, 0.55),
    "arrow_fire": (arrow_fire, 0.45), "arrow_hit": (arrow_hit, 0.45), "bolt_fire": (bolt_fire, 0.7),
    "bolt_hit": (bolt_hit, 0.75), "ballista_reload": (ballista_reload, 0.45), "spit": (spit, 0.5),
    "bloater_burst": (bloater_burst, 0.7), "warden_die": (warden_die, 0.6), "hollow_die": (hollow_die, 0.55),
    "castle_hit": (castle_hit, 0.75), "castle_crumble": (castle_crumble, 0.9), "coin": (coin, 0.45),
    "star": (star, 0.65), "ember_rain": (ember_rain, 0.6), "rally": (rally, 0.75), "bell": (bell_toll, 0.75),
    "heal": (heal, 0.55), "hero_call": (hero_call, 0.8), "hero_flare": (hero_flare, 0.7),
    "boss_roar": (boss_roar, 0.9), "boss_warn": (boss_warn, 0.8), "boss_slam": (boss_slam, 0.9),
    "win": (win, 0.8), "lose": (lose, 0.75),
}

def limit(x, thr, max_red_db=7.0):
    """Peak limiter: fast envelope follower, gain reduction capped at max_red_db."""
    from scipy.ndimage import maximum_filter1d
    env = maximum_filter1d(np.abs(x), 97)
    env = lp(env, 60, 1)
    env = np.maximum(env, maximum_filter1d(np.abs(x), 33))
    g = np.clip(thr / np.maximum(env, 1e-9), undb(-max_red_db), 1.0)
    g = np.minimum.accumulate(g[::-1])[::-1] if False else g
    return x * g


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
        print(f"{sid:16s} {len(x)/SR:5.2f}s loud {A.short_term_loudness_db(x):6.1f} dB peak {db(peak(x)):5.1f} decoded {dpk:5.1f}")
    return results


if __name__ == "__main__":
    build(sys.argv[1:] or None)
