"""Small DSP toolkit for Siegeline audio. Pure numpy/scipy, all sounds synthesised here.

Everything works on float32/float64 mono arrays at SR unless noted.
"""
import numpy as np
from scipy import signal

SR = 44100
rng_global = np.random.default_rng(7)


def n_of(sec, sr=SR):
    return max(1, int(round(sec * sr)))


def tvec(n, sr=SR):
    return np.arange(n) / sr


def noise(n, seed=None):
    r = np.random.default_rng(seed) if seed is not None else rng_global
    return r.uniform(-1.0, 1.0, n)


# ---------------------------------------------------------------- envelopes
def exp_env(n, tau, sr=SR):
    """Exponential decay with time constant tau (seconds)."""
    return np.exp(-tvec(n, sr) / max(tau, 1e-5))


def adsr(n, a=0.005, d=0.05, s=0.7, r=0.1, sr=SR):
    t = tvec(n, sr)
    dur = n / sr
    rel_start = max(dur - r, a + d)
    e = np.where(t < a, t / max(a, 1e-6), 0.0)
    dm = (t >= a) & (t < a + d)
    e = np.where(dm, 1.0 - (1.0 - s) * (t - a) / max(d, 1e-6), e)
    e = np.where((t >= a + d) & (t < rel_start), s, e)
    rm = t >= rel_start
    e = np.where(rm, s * np.clip(1.0 - (t - rel_start) / max(r, 1e-6), 0, 1), e)
    return e


def fade(x, fin=0.002, fout=0.01, sr=SR):
    x = x.copy()
    a = min(len(x), n_of(fin, sr))
    b = min(len(x), n_of(fout, sr))
    if a > 1:
        x[:a] *= np.linspace(0, 1, a)
    if b > 1:
        x[-b:] *= np.linspace(1, 0, b) ** 2
    return x


# ---------------------------------------------------------------- oscillators
def phase_of(freq, n, sr=SR, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    ph = phase0 + np.cumsum(f) / sr
    return ph, f


def sine(freq, n, sr=SR, phase0=0.0):
    ph, _ = phase_of(freq, n, sr, phase0)
    return np.sin(2 * np.pi * ph)


def _polyblep(t, dt):
    out = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    out[m] = x + x - x * x - 1.0
    m2 = t > 1.0 - dt
    x = (t[m2] - 1.0) / dt[m2]
    out[m2] = x * x + x + x + 1.0
    return out


def saw(freq, n, sr=SR, phase0=0.0):
    ph, f = phase_of(freq, n, sr, phase0)
    t = ph % 1.0
    dt = np.clip(np.abs(f) / sr, 1e-9, 0.5)
    return (2.0 * t - 1.0) - _polyblep(t, dt)


def square(freq, n, sr=SR, phase0=0.0, pw=0.5):
    ph, f = phase_of(freq, n, sr, phase0)
    t = ph % 1.0
    dt = np.clip(np.abs(f) / sr, 1e-9, 0.5)
    sq = np.where(t < pw, 1.0, -1.0)
    sq += _polyblep(t, dt)
    sq -= _polyblep((t + 1.0 - pw) % 1.0, dt)
    return sq


def tri(freq, n, sr=SR, phase0=0.0):
    ph, _ = phase_of(freq, n, sr, phase0)
    t = ph % 1.0
    return 4.0 * np.abs(t - 0.5) - 1.0


def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=np.float64) - 69.0) / 12.0)


# ---------------------------------------------------------------- filters
def _sos(kind, fc, sr=SR, order=2, q=None):
    nyq = sr / 2
    if kind == "band":
        lo, hi = fc
        lo = max(lo, 10) / nyq
        hi = min(hi, nyq * 0.98) / nyq
        return signal.butter(order, [lo, hi], btype="band", output="sos")
    fcn = np.clip(fc / nyq, 1e-4, 0.98)
    return signal.butter(order, fcn, btype=kind, output="sos")


def lp(x, fc, order=2, sr=SR):
    return signal.sosfilt(_sos("low", fc, sr, order), x)


def hp(x, fc, order=2, sr=SR):
    return signal.sosfilt(_sos("high", fc, sr, order), x)


def bp(x, lo, hi, order=2, sr=SR):
    return signal.sosfilt(_sos("band", (lo, hi), sr, order), x)


def peak_bp(x, fc, q, sr=SR):
    """Resonant band-pass (RBJ constant 0 dB peak gain)."""
    w0 = 2 * np.pi * min(fc, sr * 0.45) / sr
    al = np.sin(w0) / (2 * q)
    b = np.array([al, 0, -al])
    a = np.array([1 + al, -2 * np.cos(w0), 1 - al])
    return signal.lfilter(b / a[0], a / a[0], x)


def sweep_lp(x, f_start, f_end, sr=SR, steps=24, curve=1.0):
    """Time-varying low-pass approximated by crossfading block-filtered copies."""
    n = len(x)
    out = np.zeros(n)
    edges = np.linspace(0, n, steps + 1).astype(int)
    zi = None
    for i in range(steps):
        a, b = edges[i], edges[i + 1]
        frac = (i / max(steps - 1, 1)) ** curve
        fc = f_start * (f_end / f_start) ** frac
        sos = _sos("low", fc, sr, 2)
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        y, zi = signal.sosfilt(sos, x[a:b], zi=zi)
        out[a:b] = y
    return out


# ---------------------------------------------------------------- dynamics / utils
def db(x):
    return 20 * np.log10(max(x, 1e-12))


def undb(d):
    return 10 ** (d / 20.0)


def peak(x):
    return float(np.max(np.abs(x))) if len(x) else 0.0


def normalize(x, peak_db=-1.0):
    p = peak(x)
    return x * (undb(peak_db) / p) if p > 0 else x


def softclip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def mix_at(buf, x, start, gain=1.0):
    """Add x into buf at sample start (clipped to buffer)."""
    if start >= len(buf):
        return
    end = min(len(buf), start + len(x))
    buf[start:end] += gain * x[: end - start]


def mix_wrap(buf, x, start, gain=1.0):
    """Add x into a circular buffer (for seamless loops)."""
    L = len(buf)
    start %= L
    pos = 0
    while pos < len(x):
        s = (start + pos) % L
        k = min(L - s, len(x) - pos)
        buf[s:s + k] += gain * x[pos:pos + k]
        pos += k


def pan_gains(p):
    """p in [-1, 1] -> equal-power (l, r)."""
    a = (p + 1) * np.pi / 4
    return np.cos(a), np.sin(a)


# ---------------------------------------------------------------- reverb
def make_ir(sec=2.0, decay=0.6, sr=SR, seed=3, damp=4000.0, stereo=True):
    """Synthetic hall IR: early reflections + damped noise tail."""
    n = n_of(sec, sr)
    chans = []
    for c in range(2 if stereo else 1):
        r = np.random.default_rng(seed + c * 11)
        tail = r.standard_normal(n) * np.exp(-tvec(n, sr) * 6.9 / max(decay * 1.0, 1e-3) / 1.0)
        # darker as it decays: blend of bright & dark versions
        dark = lp(tail, damp * 0.35, 1, sr)
        bright = lp(tail, damp, 1, sr)
        w = np.linspace(0, 1, n) ** 0.5
        tail = bright * (1 - w) + dark * w
        pre = n_of(0.012, sr)
        tail[:pre] = 0
        for k in range(8):
            d = n_of(0.008 + 0.009 * k + r.uniform(0, 0.006), sr)
            if d < n:
                tail[d] += r.uniform(0.2, 0.5) * (1 if r.random() > 0.5 else -1)
        tail /= np.sqrt(np.sum(tail ** 2))
        chans.append(tail)
    return np.stack(chans) if stereo else chans[0]


def reverb(x, ir, wet=0.3):
    """Linear (non-circular) convolution reverb. x mono or (2,n); returns (2, n+len(ir)-1)."""
    if x.ndim == 1:
        x = np.stack([x, x])
    out = []
    for c in range(2):
        out.append(signal.oaconvolve(x[c], ir[c % ir.shape[0]]))
    y = np.stack(out)
    dry = np.zeros_like(y)
    dry[:, : x.shape[1]] = x
    return dry * (1 - wet * 0.5) + y * wet


def reverb_circular(x, ir, wet=0.3):
    """Circular convolution: perfect for loops (tail wraps into the head). x (2, L)."""
    L = x.shape[1]
    out = np.empty_like(x)
    for c in range(2):
        h = np.zeros(L)
        k = min(L, ir.shape[1])
        h[:k] = ir[c % ir.shape[0], :k]
        y = np.fft.irfft(np.fft.rfft(x[c]) * np.fft.rfft(h), n=L)
        out[c] = x[c] * (1 - wet * 0.5) + y * wet
    return out


def circular_filter(x, fn, warm=None):
    """Apply an IIR process to a loop seamlessly: run over [loop, loop], keep 2nd copy."""
    L = x.shape[-1]
    if warm is None:
        warm = L
    doubled = np.concatenate([x[..., L - warm:], x], axis=-1)
    y = fn(doubled)
    return y[..., warm:]
