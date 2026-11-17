"""WAV writing, AAC (.m4a) encoding/decoding via PyAV (bundled FFmpeg; the system ffmpeg
on this Jetson has no AAC encoder or decoder), and analysis checks."""
import os
import numpy as np
import av
from scipy.io import wavfile

from synth import SR, db, peak

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "public", "assets", "audio")
WAVDIR = os.path.join(HERE, "wav")  # intermediate renders (not shipped)
os.makedirs(OUT, exist_ok=True)
os.makedirs(WAVDIR, exist_ok=True)


def as2d(x):
    x = np.asarray(x, dtype=np.float32)
    return x[None, :] if x.ndim == 1 else x


def write_wav(x, name, sr=SR):
    x = as2d(x)
    path = os.path.join(WAVDIR, name + ".wav")
    wavfile.write(path, sr, (np.clip(x.T, -1, 1) * 32767).astype(np.int16))
    return path


def encode_m4a(x, name, bitrate, sr=SR):
    x = as2d(x)
    ch = x.shape[0]
    path = os.path.join(OUT, name + ".m4a")
    layout = "mono" if ch == 1 else "stereo"
    cont = av.open(path, "w", format="ipod")
    st = cont.add_stream("aac", rate=sr, layout=layout)
    st.bit_rate = int(bitrate)
    fs = 1024
    pts = 0
    for i in range(0, x.shape[1], fs):
        chunk = np.ascontiguousarray(x[:, i:i + fs])
        fr = av.AudioFrame.from_ndarray(chunk, format="fltp", layout=layout)
        fr.sample_rate = sr
        fr.pts = pts
        pts += chunk.shape[1]
        for p in st.encode(fr):
            cont.mux(p)
    for p in st.encode(None):
        cont.mux(p)
    cont.close()
    return path


def decode(path):
    cont = av.open(path)
    st = cont.streams.audio[0]
    sr = st.rate
    chunks = []
    for fr in cont.decode(st):
        a = fr.to_ndarray()
        if a.ndim == 2 and fr.format.is_packed:
            a = a.reshape(-1, len(fr.layout.channels)).T
        chunks.append(a.astype(np.float32))
    cont.close()
    y = np.concatenate(chunks, axis=1)
    return y, sr


def align_offset(ref, dec, search=4096):
    """Lag (samples) of decoded vs reference via cross-correlation on the first second."""
    r = ref[0, : min(ref.shape[1], SR)]
    d = dec[0, : min(dec.shape[1], SR + search)]
    best, lag = -1e18, 0
    for k in range(0, search + 1, 1):
        seg = d[k:k + len(r)]
        if len(seg) < len(r):
            break
        c = float(np.dot(seg, r))
        if c > best:
            best, lag = c, k
    return lag


def analyse(x, sr=SR):
    x = as2d(x)
    return {
        "dur": x.shape[1] / sr,
        "peak_db": db(peak(x)),
        "dc": float(np.max(np.abs(x.mean(axis=1)))),
        "rms_db": db(float(np.sqrt(np.mean(x.astype(np.float64) ** 2)))),
    }


def short_term_loudness_db(x, sr=SR, win=0.3):
    """Max RMS over a sliding window (crude loudness proxy for short SFX)."""
    x = as2d(x).astype(np.float64).mean(axis=0)
    w = max(1, int(win * sr))
    if len(x) <= w:
        return db(np.sqrt(np.mean(x ** 2)))
    c = np.cumsum(np.concatenate([[0], x ** 2]))
    ms = (c[w:] - c[:-w]) / w
    return db(np.sqrt(ms.max()))


def encode_safe(x, name, bitrate, sr=SR, ceiling_db=-1.3, tries=5):
    """Encode, decode, and re-encode scaled down until the DECODED peak is under ceiling_db
    (AAC reconstruction can overshoot the source peak by a few dB on sharp transients)."""
    x = as2d(x).astype(np.float64)
    path = None
    for _ in range(tries):
        path = encode_m4a(x, name, bitrate, sr)
        y, _ = decode(path)
        p = db(peak(y))
        if p <= ceiling_db:
            return path, p
        x = x * 10 ** ((ceiling_db - 0.15 - p) / 20)
    return path, p
