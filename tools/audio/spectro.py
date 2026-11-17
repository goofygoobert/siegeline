"""Write a log-frequency spectrogram PNG of a shipped file (visual sanity check, no deps beyond numpy).
Usage: .venv/bin/python tools/audio/spectro.py <id> <out.png> [start_s] [dur_s]"""
import sys, zlib, struct
import numpy as np
from scipy import signal
import audioio as A


def png(path, img):
    h, w = img.shape
    raw = b"".join(b"\x00" + img[i].tobytes() for i in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


name, out = sys.argv[1], sys.argv[2]
st = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
du = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
y, sr = A.decode(A.OUT + "/" + name + ".m4a")
m = y.mean(0)[int(st * sr): int((st + du) * sr)]
f, t, S = signal.spectrogram(m, sr, nperseg=2048, noverlap=2048 - max(64, len(m) // 1400))
S = 10 * np.log10(S + 1e-12)
rows = 300
fl = np.geomspace(30, 16000, rows)
idx = np.searchsorted(f, fl).clip(0, len(f) - 1)
img = S[idx][::-1]
img = np.clip((img - (img.max() - 80)) / 80, 0, 1)
png(out, (img * 255).astype(np.uint8))
print(img.shape)
