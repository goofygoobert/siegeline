"""Synth instruments shared by SFX and music. Each returns a mono float64 array."""
import numpy as np
from scipy import signal

from synth import (SR, n_of, tvec, noise, exp_env, adsr, fade, sine, saw, square, tri,
                   mtof, lp, hp, bp, peak_bp, mix_at, sweep_lp)


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
    x = (saw(f0 * 1.003, n) + saw(f0 * 0.997, n, phase0=0.5) + 0.35 * square(f0, n, pw=0.3)) / 2.35
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
    slap = bp(noise(n, seed + 2), 280, 1600) * np.exp(-t / 0.03) * 0.9  # reads on phone speakers
    y = body + thump * skin + slap * skin + click * 0.7
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


# ================================================================== sea / shanty kit (pirate re-theme)
VOWELS["eh"] = [(560, 1.0, 7), (1750, 0.55, 9), (2500, 0.3, 11)]
VOWELS["oh_lo"] = [(420, 1.0, 7), (720, 0.5, 8), (2400, 0.1, 12)]


def accordion(f0, dur, vel=1.0, seed=0, a=0.02, r=0.07, musette=0.0032, bright=1.0, reeds=3,
              bellows=0.0):
    """Free-reed squeezebox: 2-3 detuned narrow-pulse reeds (musette beating), reedy body
    resonances, quick bellows attack. bellows>0 adds a slow push/pull swell."""
    n = n_of(dur + r)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    dets = [0.0, -musette, musette][:reeds]
    x = np.zeros(n)
    for k, d in enumerate(dets):
        pw = 0.26 + 0.05 * k
        x += square(f0 * (1 + d), n, phase0=rr.random(), pw=pw) - (2 * pw - 1)  # remove pulse DC
    x /= len(dets)
    cut = min(800 + f0 * 9 * bright, 8500)
    y = lp(x, cut, 2)
    y = y + 0.6 * peak_bp(y, 1250, 2.2) + 0.35 * peak_bp(y, 2700, 3.0)
    y = y - 0.55 * lp(y, 220, 1)
    env = adsr(n, a, 0.06, 0.82, r)
    if bellows:
        env = env * (1 - bellows + bellows * np.sin(np.pi * np.clip(t / max(dur, 1e-3), 0, 1)))
    env = env * (1 + 0.025 * np.sin(2 * np.pi * rr.uniform(4.5, 6.0) * t))
    return y * env * vel * 0.8


def fiddle(f0, dur, vel=1.0, seed=0, a=0.035, r=0.12, vdepth=0.0055, bright=1.0, scoop=0.012,
           vdelay=None):
    """Bowed fiddle: saw + bow noise through violin body resonances, delayed vibrato."""
    n = n_of(dur + r)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    vd = min(0.2, dur * 0.45) if vdelay is None else vdelay
    p = vib(n, 5.9 + rr.uniform(-0.4, 0.4), vdepth, vd, seed=seed)
    p = p * (1 - scoop * np.exp(-t / 0.025))
    x = saw(f0 * p, n, phase0=rr.random())
    x = x * (1 + 0.08 * lp(rr.standard_normal(n), 40, 1) * 8)  # bow-pressure jitter
    y = 0.25 * x
    for fc, g, q in ((285, 0.9, 4), (470, 0.8, 5), (1050, 0.45, 3), (2900, 0.9, 2.0), (4400, 0.35, 3)):
        y += g * peak_bp(x, fc, q)
    y = lp(y, 6500 * bright + 1000, 2)
    bow = bp(noise(n, seed + 3), 2500, 8000) * 0.05 * (0.4 + np.exp(-t / 0.05))
    env = adsr(n, a, 0.08, 0.82, r)
    return (y + bow) * env * vel * 1.3


def stomp(vel=1.0, seed=0, f=84, dur=0.32, boards=1.0):
    """Boot on a wooden deck: pitched thump (kept above ~70 Hz for phones) + board knock."""
    n = n_of(dur)
    t = tvec(n)
    body = sine(f * (1 + 1.3 * np.exp(-t / 0.012)), n) * np.exp(-t / 0.085)
    thud = lp(noise(n, seed), 500, 2) * np.exp(-t / 0.03) * 1.2
    knock = bp(noise(n, seed + 1), 250, 1600) * np.exp(-t / 0.022) * 0.9 * boards
    plank = metal([196, 331, 517], [0.05, 0.035, 0.025], n, [0.5, 0.35, 0.2], seed=seed) * boards
    y = body + thud + knock + plank
    y[: n_of(0.003)] += hp(noise(n_of(0.003), seed + 2), 1200) * 0.5
    return fade(y, 0.0003, 0.04) * vel


def clap(vel=1.0, seed=0, people=1, dur=0.2):
    """Hand clap(s); people>1 gives a ragged crew clap."""
    n = n_of(dur + 0.03 * (people > 1))
    y = np.zeros(n)
    rr = np.random.default_rng(seed)
    for p in range(people):
        off = n_of(rr.uniform(0, 0.022)) if people > 1 else 0
        for k, (d, tau, g) in enumerate(((0.0, 0.003, 0.6), (0.007, 0.003, 0.7), (0.013, 0.045, 1.0))):
            m = n_of(dur * 0.8)
            tt = tvec(m)
            burst = noise(m, seed * 31 + p * 7 + k) * np.exp(-tt / tau)
            mix_at(y, burst, off + n_of(d), g * rr.uniform(0.7, 1.0))
    y = bp(y, 800, 4500, 2) + 0.8 * peak_bp(y, 1300 + 200 * rr.random(), 3)
    return fade(y, 0.0002, 0.03) * vel / max(1.0, people ** 0.5)


def shout(f0=190, dur=0.28, vel=1.0, voices=6, seed=0, vowel="eh", fall=0.18):
    """Wordless crew shout ('hey!'-like vowel bark): breathy onset, falling pitch, formants."""
    n = n_of(dur + 0.08)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    src = np.zeros(n)
    for k in range(voices):
        fk = f0 * rr.uniform(0.85, 1.25)
        pc = fk * (1 + 0.06 * np.exp(-t / 0.03)) * (1 - fall * np.clip(t / dur, 0, 1))
        src += saw(pc, n, phase0=rr.random()) * rr.uniform(0.7, 1.0)
    src /= voices
    src *= 1 + 0.15 * lp(noise(n, seed + 4), 60, 1) * 10
    breath = hp(noise(n, seed), 1200) * np.exp(-t / 0.03) * 0.5
    src = src + 0.15 * hp(noise(n, seed + 5), 1500)
    y = np.zeros(n)
    for fc, g, q in VOWELS[vowel]:
        y += g * peak_bp(src, fc * rr.uniform(0.95, 1.05), q * 0.6)
    y = y * 2.5 + breath
    env = adsr(n, 0.018, 0.08, 0.6, 0.12) * (1 - 0.4 * np.clip(t / dur, 0, 1))
    return fade(y * env, 0.001, 0.04) * vel


def whale(knots, dur, vel=1.0, seed=0, a=0.4, r=0.6, growl=0.35, formants=((380, 1.0, 5), (820, 0.5, 6), (1650, 0.2, 8))):
    """Deep whale-like moan: smooth gliding pitch (knots = list of Hz across the note), tonal
    sine body + a formant-filtered growl. Fundamental sits >= ~70 Hz; energy is in harmonics."""
    n = n_of(dur + r)
    t = tvec(n)
    kx = np.linspace(0, 1, len(knots))
    u = np.clip(t / (dur + r), 0, 1)
    f = np.interp(u, kx, knots)
    f = lp(np.concatenate([np.full(2000, f[0]), f]), 3.0, 1)[2000:]
    f = f * (1 + 0.004 * np.sin(2 * np.pi * 4.2 * t))
    tone = sine(f, n) + 0.55 * sine(2 * f, n, 0.3) + 0.3 * sine(3 * f, n, 0.7) + 0.12 * sine(5 * f, n)
    src = saw(f, n) * (1 + 0.3 * lp(noise(n, seed), 25, 1) * 10)
    g = np.zeros(n)
    for fc, gg, q in formants:
        g += gg * peak_bp(src, fc, q)
    y = 0.6 * tone + growl * 2.0 * g
    return y * adsr(n, a, 0.3, 0.85, r) * vel


def wave_wash(dur, vel=1.0, seed=0, bright=1.0, peak_at=0.4):
    """One wave rolling in and drawing back: swelling low-passed noise + foam hiss."""
    n = n_of(dur)
    t = tvec(n)
    u = t / dur
    env = np.where(u < peak_at, np.sin(0.5 * np.pi * u / peak_at) ** 2,
                   np.exp(-(u - peak_at) / (0.28 * (1 - peak_at) + 1e-3)))
    body = sweep_lp_local(noise(n, seed), 350, 1800 * bright, peak_at)
    body = hp(body, 90, 2)
    foam = hp(noise(n, seed + 1), 2500 * bright, 2)
    fenv = np.where(u < peak_at * 1.1, (u / (peak_at * 1.1)) ** 3,
                    np.exp(-(u - peak_at * 1.1) / 0.18))
    grit = 1 + 0.5 * lp(noise(n, seed + 2), 18, 1) * 8
    y = body * env * 0.9 + foam * fenv * 0.18 * grit
    return fade(y, 0.01, 0.05) * vel


def sweep_lp_local(x, f_lo, f_hi, peak_at, steps=24):
    """Low-pass that opens up to the wave's crest then closes again."""
    from synth import _sos
    n = len(x)
    out = np.zeros(n)
    edges = np.linspace(0, n, steps + 1).astype(int)
    zi = None
    for i in range(steps):
        u = (i + 0.5) / steps
        w = u / peak_at if u < peak_at else max(0.0, 1 - (u - peak_at) / (1 - peak_at))
        fc = f_lo * (f_hi / f_lo) ** w
        sos = _sos("low", fc, SR, 2)
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        y, zi = signal.sosfilt(sos, x[edges[i]:edges[i + 1]], zi=zi)
        out[edges[i]:edges[i + 1]] = y
    return out


def creak(dur, f0=35, f1=80, vel=1.0, seed=0, res=(520, 980, 1700)):
    """Wood/rope creak: stick-slip pulse train with varying rate through wood resonances."""
    n = n_of(dur)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    u = t / dur
    rate = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(np.pi * u)) * (1 + 0.15 * np.sin(2 * np.pi * rr.uniform(2, 5) * t))
    ph = np.cumsum(rate) / SR
    imp = np.zeros(n)
    idx = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    imp[idx] = rr.uniform(0.6, 1.0, len(idx))
    y = np.zeros(n)
    for k, fc in enumerate(res):
        y += peak_bp(imp, fc * rr.uniform(0.95, 1.05), 12) * (1.0 - 0.25 * k)
    y = y * 6 + 0.3 * bp(imp, 2000, 6000)
    return fade(y * adsr(n, 0.04, 0.1, 0.8, min(0.15, dur * 0.3)), 0.002, 0.03) * vel


def splash(dur=0.7, vel=1.0, seed=0, size=1.0, bubbles=14):
    """Water splash: slap, spray body, bubble chirps, a soft plunge."""
    n = n_of(dur)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    slap = bp(noise(n, seed), 250, 3500) * np.exp(-t / 0.02)
    body = bp(noise(n, seed + 1), 500, 7000) * (1 - np.exp(-t / 0.012)) * np.exp(-t / (0.12 * size))
    spray = hp(noise(n, seed + 2), 3500) * (1 - np.exp(-t / 0.03)) * np.exp(-t / (0.25 * size))
    spray *= 1 + 0.6 * lp(noise(n, seed + 3), 30, 1) * 8
    plunge = sine(140 * (1 - 0.4 * np.clip(t / 0.12, 0, 1)), n) * np.exp(-t / 0.07)
    y = 0.9 * slap + 0.9 * body + 0.35 * spray + 0.5 * plunge
    for k in range(bubbles):
        s = rr.uniform(0.03, 0.65) * dur
        m = n_of(rr.uniform(0.015, 0.04))
        tt = tvec(m)
        f = rr.uniform(500, 2200)
        bub = sine(f * (1 + 2.5 * tt / (m / SR)), m) * np.exp(-tt / (m / SR / 3))
        mix_at(y, bub, n_of(s), 0.25 * rr.uniform(0.4, 1.0) * np.exp(-s / (0.4 * dur)))
    return fade(y, 0.0005, 0.05) * vel


def fizz(dur, vel=1.0, seed=0, rate=900, tau=0.25):
    """Carbonated fizz: dense random micro-crackles over a thin hiss, decaying."""
    n = n_of(dur)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    imp = (rr.random(n) < rate / SR) * rr.uniform(-1, 1, n)
    y = hp(imp, 3000, 2) * 3 + 0.12 * hp(noise(n, seed + 1), 5000)
    return y * np.exp(-t / tau) * vel


def squelch(dur=0.25, vel=1.0, seed=0, f=300, drop=0.6):
    """Wet slimy squelch: AM-gurgled band noise with a falling resonance."""
    n = n_of(dur)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    am = 1 + 0.9 * np.sin(2 * np.pi * (rr.uniform(35, 60) * t + 3 * t * t))
    src = noise(n, seed) * am
    fc = f * (1 - drop * np.clip(t / dur, 0, 1))
    y = np.zeros(n)
    edges = np.linspace(0, n, 13).astype(int)
    for i in range(12):
        a, b = edges[i], edges[i + 1]
        seg = peak_bp(src[max(0, a - 400):b], float(fc[a]) + 1, 3)[min(a, 400):]
        y[a:b] = seg[: b - a]
    y = y * 3 + 0.3 * bp(src, 800, 3000)
    return fade(y * adsr(n, 0.008, 0.05, 0.7, dur * 0.5), 0.001, 0.03) * vel


def wood_crack(vel=1.0, seed=0, size=1.0, snaps=5):
    """Splintering timber: rapid micro-snaps ringing at wood resonances + a body knock."""
    n = n_of(0.25 * size + 0.1)
    t = tvec(n)
    rr = np.random.default_rng(seed)
    y = np.zeros(n)
    pos = 0.0
    for k in range(snaps):
        m = n_of(0.06)
        tt = tvec(m)
        fr = [rr.uniform(700, 1400), rr.uniform(1600, 2800), rr.uniform(3000, 4800)]
        ring = metal(fr, [0.012, 0.008, 0.006], m, [1, 0.7, 0.4], seed=seed + k)
        snap = hp(noise(m, seed * 7 + k), 1500) * np.exp(-tt / 0.002)
        mix_at(y, ring * 0.7 + snap, n_of(pos), rr.uniform(0.5, 1.0))
        pos += rr.uniform(0.004, 0.03) * size
    y += 0.8 * sine(150 * (1 + 0.5 * np.exp(-t / 0.01)), n) * np.exp(-t / 0.05)
    y += 0.5 * bp(noise(n, seed + 99), 300, 1200) * np.exp(-t / 0.04)
    return fade(y, 0.0002, 0.04) * vel


def cannon(vel=1.0, seed=0, size=1.0, dist=0.0, dur=1.2):
    """Black-powder cannon: crack, mid 'blast' body (reads on phone speakers), roar closing down,
    pitched boom (>=70 Hz), rumble. High-passed at 55 Hz."""
    n = n_of(dur)
    t = tvec(n)
    crack = hp(noise(n, seed), 900) * np.exp(-t / 0.007)
    blast = bp(noise(n, seed + 4), 160, 2200) * (1 - np.exp(-t / 0.002)) * np.exp(-t / (0.075 * size))
    roar = sweep_lp(noise(n, seed + 1), 6000 * (1 - 0.6 * dist), 350, curve=0.5) * np.exp(-t / (0.18 * size))
    boom_ = sine(74 * (1 + 1.6 * np.exp(-t / 0.025)), n) * np.exp(-t / (0.22 * size))
    thump = bp(noise(n, seed + 2), 110, 600) * np.exp(-t / 0.1) * 1.4
    rumble = bp(noise(n, seed + 3), 70, 320) * np.exp(-t / (0.45 * size)) * 1.1
    y = (1 - 0.7 * dist) * 1.3 * crack + 1.6 * blast + roar * 1.0 + boom_ * 0.75 + thump + rumble
    y = np.tanh(y * 1.8) / np.tanh(1.8)
    if dist:
        y = lp(y, 7000 * (1 - dist) + 900, 2)
    y = hp(y, 55, 2)
    return fade(y, 0.0002, 0.1) * vel


def bosun_whistle(dur=0.8, vel=1.0, seed=0):
    """Boatswain's pipe: glide up from ~1.1 kHz to ~2.3 kHz, hold, warble trill, fall-off."""
    n = n_of(dur)
    t = tvec(n)
    u = t / dur
    f = np.interp(u, [0, 0.18, 0.62, 0.85, 1.0], [1100, 2300, 2350, 2250, 1700])
    trill = np.where((u > 0.45) & (u < 0.85), 1 + 0.035 * np.sign(np.sin(2 * np.pi * 14 * t)), 1.0)
    trill = lp(trill, 120, 1)
    f = f * trill
    y = sine(f, n) + 0.12 * sine(2 * f, n) + 0.05 * sine(3 * f, n)
    breath = bp(noise(n, seed), 1500, 5000) * 0.12
    env = adsr(n, 0.03, 0.05, 0.9, 0.12)
    return fade((y + breath) * env, 0.002, 0.05) * vel
