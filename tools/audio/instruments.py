"""Synth instruments shared by SFX and music. Each returns a mono float64 array."""
import numpy as np
from scipy import signal

from synth import (SR, n_of, tvec, noise, exp_env, adsr, fade, sine, saw, square, tri,
                   mtof, lp, hp, bp, peak_bp)


def vib(n, rate=5.0, depth=0.004, delay=0.15, sr=SR, seed=0):
    t = tvec(n, sr)
    r = np.random.default_rng(seed)
    ramp = np.clip((t - delay) / 0.4, 0, 1)
    jitter = lp(r.standard_normal(n), 3.0, 1, sr) * 40
    return 1.0 + depth * ramp * np.sin(2 * np.pi * rate * t + r.uniform(0, 6)) + 0.0015 * jitter


# ------------------------------------------------------------------ brass
def brass(f0, dur, vel=1.0, a=0.06, r=0.18, bright=1.0, seed=0, detune=0.004, scoop=True):
    n = n_of(dur + r)
    t = tvec(n)
    pitch = vib(n, 4.8, 0.003, 0.25, seed=seed)
    if scoop:
        pitch = pitch * (1 - 0.02 * np.exp(-t / 0.04))
    x = np.zeros(n)
    for k, d in enumerate((-detune, 0.0, detune)):
        x += saw(f0 * (1 + d) * pitch, n, phase0=0.37 * k)
    x /= 3
    env = adsr(n, a, 0.12, 0.8, r)
    # brightness follows amplitude (louder = brighter), the classic brass cue
    benv = np.clip(env * (0.55 + 0.45 * vel), 0, 1) ** 1.3
    dark = lp(x, min(f0 * 2.2, 9000), 2)
    brt = lp(x, min(f0 * (3 + 9 * bright * vel), 12000), 2)
    y = dark * (1 - benv) + brt * benv
    y = y + 0.2 * lp(x, f0 * 1.2, 1)
    return y * env * vel


# ------------------------------------------------------------------ strings
def strings(f0, dur, vel=1.0, a=0.25, r=0.5, voices=5, seed=0, cutoff=2600, detune=0.006):
    n = n_of(dur + r)
    rr = np.random.default_rng(seed)
    x = np.zeros(n)
    for k in range(voices):
        d = detune * (k - (voices - 1) / 2) / max(1, (voices - 1) / 2)
        p = vib(n, 5.2 + rr.uniform(-0.6, 0.6), 0.004, 0.2, seed=seed * 31 + k)
        x += saw(f0 * (1 + d) * p, n, phase0=rr.random())
    x /= voices
    x = lp(x, min(cutoff, 11000), 2)
    x = x - 0.6 * lp(x, 180, 1)  # thin out mud
    env = adsr(n, a, 0.2, 0.85, r)
    return x * env * vel


def staccato(f0, dur, vel=1.0, seed=0, cutoff=1800):
    """Short bowed/martelé low-strings note for ostinati."""
    n = n_of(dur + 0.08)
    x = (saw(f0 * 1.003, n) + saw(f0 * 0.997, n, phase0=0.5) + 0.5 * square(f0 * 0.5, n)) / 2.5
    env = adsr(n, 0.006, 0.06, 0.55, 0.06)
    e2 = np.exp(-tvec(n) / 0.05)
    y = lp(x, cutoff, 2) * (1 - 0.6 * e2) + lp(x, cutoff * 2.5, 2) * 0.6 * e2
    return y * env * vel


# ------------------------------------------------------------------ choir
VOWELS = {
    "ah": [(800, 1.0, 9), (1150, 0.6, 10), (2800, 0.25, 14)],
    "oh": [(500, 1.0, 9), (800, 0.45, 10), (2830, 0.12, 14)],
    "oo": [(350, 1.0, 9), (650, 0.3, 10), (2700, 0.08, 14)],
}


def choir(f0, dur, vel=1.0, vowel="ah", a=0.4, r=0.7, voices=6, seed=0):
    n = n_of(dur + r)
    rr = np.random.default_rng(seed)
    src = np.zeros(n)
    for k in range(voices):
        d = 0.009 * (rr.random() - 0.5)
        p = vib(n, 5.5 + rr.uniform(-0.8, 0.8), 0.006, 0.1, seed=seed * 17 + k)
        src += saw(f0 * (1 + d) * p, n, phase0=rr.random())
    src /= voices
    src += 0.03 * hp(noise(n, seed), 2000)
    y = np.zeros(n)
    for fc, g, q in VOWELS[vowel]:
        y += g * peak_bp(src, fc, q)
    y = y * 2.2 + 0.08 * lp(src, 400)
    return y * adsr(n, a, 0.3, 0.9, r) * vel


# ------------------------------------------------------------------ bells & metal
BELL_PARTIALS = [(0.5, 0.55, 3.0), (1.0, 1.0, 2.2), (1.19, 0.55, 1.6), (1.5, 0.45, 1.2),
                 (2.0, 0.5, 0.9), (2.51, 0.32, 0.6), (2.66, 0.25, 0.5), (3.01, 0.2, 0.4),
                 (4.17, 0.14, 0.25), (5.43, 0.08, 0.18)]


def bell(f0, dur, vel=1.0, decay=1.0, seed=0, strike=0.5):
    n = n_of(dur)
    t = tvec(n)
    y = np.zeros(n)
    rr = np.random.default_rng(seed)
    for ratio, amp, tau in BELL_PARTIALS:
        f = f0 * ratio
        if f > SR * 0.45:
            continue
        beat = 1 + 0.15 * np.sin(2 * np.pi * rr.uniform(0.5, 2.5) * t)
        y += amp * beat * np.sin(2 * np.pi * f * t + rr.random() * 6) * np.exp(-t / (tau * decay))
    k = n_of(0.01)
    y[:k] += strike * hp(noise(k, seed), 2500) * np.linspace(1, 0, k)
    return fade(y, 0.0005, 0.05) * vel


def metal(freqs, taus, n, amps=None, seed=0):
    t = tvec(n)
    y = np.zeros(n)
    rr = np.random.default_rng(seed)
    amps = amps or [1.0] * len(freqs)
    for f, tau, a in zip(freqs, taus, amps):
        y += a * np.sin(2 * np.pi * f * t + rr.random() * 6) * np.exp(-t / tau)
    return y


# ------------------------------------------------------------------ plucks
def pluck(f0, dur, vel=1.0, bright=0.5, seed=0, damp=0.996):
    """Karplus-Strong via lfilter (harp / lute / pizzicato)."""
    n = n_of(dur)
    N = max(2, int(round(SR / f0)))
    exc = noise(N, seed)
    exc = lp(exc, 1200 + 6000 * bright, 1)
    x = np.zeros(n)
    x[:N] = exc
    a = np.zeros(N + 2)
    a[0] = 1.0
    a[N] = -0.5 * damp
    a[N + 1] = -0.5 * damp
    y = signal.lfilter([1.0], a, x)
    y = y - np.mean(y[: min(n, 4 * N)])
    return fade(y, 0.0005, 0.03) * vel


# ------------------------------------------------------------------ drums
def taiko(f=58, dur=0.9, vel=1.0, seed=0, skin=1.0):
    n = n_of(dur)
    t = tvec(n)
    pf = f * (1 + 1.4 * np.exp(-t / 0.025))
    body = sine(pf, n) * np.exp(-t / 0.32) + 0.4 * sine(pf * 1.52, n) * np.exp(-t / 0.12)
    thump = lp(noise(n, seed), 700, 2) * np.exp(-t / 0.045) * 1.4
    k = n_of(0.004)
    click = np.zeros(n)
    click[:k] = hp(noise(k, seed + 1), 1500) * np.linspace(1, 0, k)
    y = body + thump * skin + click * 0.7
    return fade(y, 0.0003, 0.05) * vel


def frame_drum(f=110, dur=0.4, vel=1.0, seed=0):
    n = n_of(dur)
    t = tvec(n)
    pf = f * (1 + 0.6 * np.exp(-t / 0.015))
    y = sine(pf, n) * np.exp(-t / 0.12) + bp(noise(n, seed), 200, 2500) * np.exp(-t / 0.03) * 0.8
    return fade(y, 0.0003, 0.03) * vel


def snare(dur=0.25, vel=1.0, seed=0, tone=185, snappy=1.0):
    n = n_of(dur)
    t = tvec(n)
    body = tri(tone * (1 + 0.3 * np.exp(-t / 0.01)), n) * np.exp(-t / 0.05)
    rattle = bp(noise(n, seed), 1500, 8000) * np.exp(-t / 0.09) * snappy
    return fade(0.6 * body + rattle, 0.0002, 0.03) * vel


def field_snare(dur=0.3, vel=1.0, seed=0):
    """Rope-tension military drum: darker, with a woody crack."""
    n = n_of(dur)
    t = tvec(n)
    body = sine(240 * (1 + 0.4 * np.exp(-t / 0.008)), n) * np.exp(-t / 0.06)
    rattle = bp(noise(n, seed), 900, 5000) * np.exp(-t / 0.11)
    return fade(0.7 * body + 0.8 * rattle, 0.0002, 0.03) * vel


def hat(dur=0.08, vel=1.0, seed=0, open_=False):
    n = n_of(dur if not open_ else 0.35)
    t = tvec(n)
    m = square(317, n) + square(437, n) + square(563, n) + square(711, n)
    y = hp(m * 0.15 + noise(n, seed), 6500, 2) * np.exp(-t / (0.025 if not open_ else 0.12))
    return fade(y, 0.0002, 0.01) * vel


def cymbal(dur=2.0, vel=1.0, seed=0, swell=False):
    n = n_of(dur)
    t = tvec(n)
    m = sum(square(f, n) for f in (293, 397, 511, 689, 823, 1033)) / 6
    y = hp(0.4 * m + noise(n, seed), 3500, 2)
    y = lp(y, 12000, 1)
    if swell:
        env = (t / dur) ** 2.5
        env = fade(env, 0, 0.02)
    else:
        env = np.exp(-t / (dur * 0.35))
    return y * env * vel


def boom(f=45, dur=1.0, vel=1.0, seed=0, drop=1.8, tau=0.4):
    n = n_of(dur)
    t = tvec(n)
    pf = f * (1 + drop * np.exp(-t / 0.05))
    y = sine(pf, n) * np.exp(-t / tau)
    y += 0.6 * lp(noise(n, seed), 250, 2) * np.exp(-t / (tau * 0.5))
    return fade(y, 0.0005, 0.05) * vel


def click(n_sec=0.004, hpf=1500, seed=0):
    k = n_of(n_sec)
    return hp(noise(k, seed), hpf) * np.linspace(1, 0, k) ** 2


# ------------------------------------------------------------------ misc tonal
def flute(f0, dur, vel=1.0, seed=0):
    n = n_of(dur + 0.15)
    p = vib(n, 5.0, 0.006, 0.2, seed=seed)
    y = sine(f0 * p, n) + 0.25 * sine(2 * f0 * p, n) + 0.08 * sine(3 * f0 * p, n)
    breath = bp(noise(n, seed), f0 * 0.9, f0 * 3.5) * 0.12
    env = adsr(n, 0.05, 0.1, 0.85, 0.15)
    return (y + breath) * env * vel


def drone(f0, n, seed=0):
    t = tvec(n)
    x = saw(f0 * (1 + 0.002 * np.sin(2 * np.pi * 0.13 * t)), n) + saw(f0 * 1.004, n, 0.3)
    return lp(x, f0 * 4, 2) * 0.5
