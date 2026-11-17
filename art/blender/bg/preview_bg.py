"""Composite parallax preview: preview_bg.py <frames_dir> <out.png> <first_frame> [scroll 0..1]"""
import sys
from PIL import Image
d, out, f0 = sys.argv[1], sys.argv[2], int(sys.argv[3]); t = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
W = {"sky": 1755, "far": 2077, "mid": 2720, "near": 3900}; VIEW = 1755
im = Image.new("RGBA", (VIEW, 810))
for i, (n, w) in enumerate(W.items()):
    L = Image.open(f"{d}/frame_{f0 + i:04d}.png").convert("RGBA").crop((0, 0, w, 810))
    x = int((w - VIEW) * t)
    im.alpha_composite(L.crop((x, 0, x + VIEW, 810)))
im.convert("RGB").resize((VIEW * 2 // 3, 540)).save(out)
