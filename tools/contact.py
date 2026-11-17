"""Contact sheet of rendered frames on a checker background: contact.py <frames_dir> <out.png> [cols]"""
import sys, glob
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 9
fs = sorted(glob.glob(d + "/frame_*.png")); ims = [Image.open(f).convert("RGBA") for f in fs]
w, h = ims[0].size; t = 0.5; tw, th = int(w * t), int(h * t)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGBA", (cols * tw, rows * th), (90, 90, 100, 255)); dr = ImageDraw.Draw(sheet)
for i, im in enumerate(ims):
    x, y = (i % cols) * tw, (i // cols) * th
    dr.rectangle([x, y, x + tw - 1, y + th - 1], fill=(150, 150, 160) if (i // cols + i) % 2 else (130, 130, 140))
    sheet.alpha_composite(im.resize((tw, th)), (x, y)); dr.text((x + 3, y + 2), str(i + 1), fill=(255, 255, 0))
sheet.save(out); print(out, len(ims))
