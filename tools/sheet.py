"""Contact sheet of rendered frames on a sunset-beach backdrop. Usage: sheet.py JOB OUT [frames e.g. 1,9,17,20,22,23,28,36,40] [scale]"""
import sys, pathlib
from PIL import Image
root = pathlib.Path(__file__).resolve().parents[1]
job, out = sys.argv[1], sys.argv[2]
fr = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [1, 9, 17, 21, 22, 23, 27, 31, 36, 40]
sc = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
ims = [Image.open(root / "art" / "out" / job / ("frame_%04d.png" % f)).convert("RGBA") for f in fr]
w, h = ims[0].size; w2, h2 = int(w * sc), int(h * sc)
cols = min(len(ims), 5); rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (w2 * cols, h2 * rows))
for i, im in enumerate(ims):
    bg = Image.new("RGB", (w2, h2))
    px = bg.load()
    for y in range(h2):
        t = y / h2
        c = (int(255 - 90 * abs(t - 0.45)), int(170 - 60 * t), int(110 + 30 * t)) if t < 0.82 else (150, 112, 96)
        for x in range(w2):
            px[x, y] = c
    s = im.resize((w2, h2), Image.LANCZOS)
    bg.paste(s, (0, 0), s)
    sheet.paste(bg, ((i % cols) * w2, (i // cols) * h2))
sheet.save(out)
