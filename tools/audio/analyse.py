"""Spectral balance / stereo width / level-over-time report for shipped music.
Usage: .venv/bin/python tools/audio/analyse.py [id ...]"""
import sys
import numpy as np
from scipy import signal
import audioio as A

BANDS = [(20, 60), (60, 250), (250, 1000), (1000, 4000), (4000, 10000), (10000, 20000)]

for n in sys.argv[1:] or ["menu", "map", "battle", "boss", "victory", "defeat"]:
    y, sr = A.decode(A.OUT + "/" + n + ".m4a")
    m = y.mean(0)
    f, P = signal.welch(m, sr, nperseg=8192)
    tot = P.sum()
    s = " ".join(f"{a}-{b}:{10*np.log10(P[(f>=a)&(f<b)].sum()/tot):6.1f}" for a, b in BANDS)
    side = (y[0] - y[1]) / 2
    width = 10 * np.log10(np.mean(side ** 2) / np.mean(m ** 2))
    corr = np.corrcoef(y[0], y[1])[0, 1]
    w = 2 * sr
    k = len(m) // w
    lv = 20 * np.log10(np.sqrt((m[: k * w].reshape(k, w) ** 2).mean(1)))
    print(f"{n:8s} {s} | side/mid {width:.1f} dB, L/R corr {corr:.2f} | 2s levels {np.round(lv).astype(int).tolist()}")
