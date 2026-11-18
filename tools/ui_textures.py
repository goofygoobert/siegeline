"""Generate the interface material textures (tileable): tarred deck planks and chart parchment.
Writes public/assets/ui/wood.webp and public/assets/ui/parchment.webp. Run: .venv/bin/python tools/ui_textures.py"""
import pathlib
import numpy as np
from PIL import Image, ImageFilter
root = pathlib.Path(__file__).resolve().parents[1]
out = root / "public" / "assets" / "ui"; out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)


def tile_noise(w, h, blur, sx=1.0, sy=1.0):
    """Tileable smooth noise in 0..1: blur a 3x3 tiled random field, keep the centre."""
    a = rng.random((h, w)).astype(np.float32)
    big = Image.fromarray((np.tile(a, (3, 3)) * 255).astype(np.uint8))
    if sx != 1 or sy != 1:
        big = big.resize((int(big.width / sx), int(big.height / sy)), Image.BILINEAR).resize(big.size, Image.BICUBIC)
    big = big.filter(ImageFilter.GaussianBlur(blur))
    c = np.asarray(big, np.float32)[h:2 * h, w:2 * w] / 255
    return (c - c.min()) / (c.max() - c.min() + 1e-6)


# ---- tarred deck planks, 512x256, planks run horizontally
W, H, P = 512, 256, 64
grain = tile_noise(W, H, 1.5, sx=12, sy=1) * 0.55 + tile_noise(W, H, 5, sx=3, sy=1) * 0.45
base = np.array([46, 31, 21], np.float32)
img = base[None, None, :] * (0.55 + 0.95 * grain[..., None])
for k in range(H // P):            # each plank its own tone, a dark seam between
    y0 = k * P
    img[y0:y0 + P] *= 0.86 + 0.24 * rng.random()
    img[y0:y0 + 2] *= 0.25
    img[y0 + 2:y0 + 3] *= 1.35
    xb = int(rng.random() * W)     # butt joint
    img[y0:y0 + P, xb:xb + 2] *= 0.3
    for nx in (xb - 14, xb + 16):  # treenails either side of the joint
        for ny in (y0 + 16, y0 + P - 16):
            yy, xx = np.ogrid[-5:6, -5:6]; m = (xx * xx + yy * yy) <= 20
            ys = (ny + yy) % H; xs = (nx + xx) % W
            img[ys, xs] = np.where(m[..., None], img[ys, xs] * 0.45 + np.array([20, 14, 10]), img[ys, xs])
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out / "wood.webp", "WEBP", quality=88, method=6)

# ---- chart parchment, 512x512: warm paper, blotches, fibres
W = H = 512
blot = tile_noise(W, H, 22) * 0.6 + tile_noise(W, H, 6) * 0.4
grit = tile_noise(W, H, 0.7)
paper = np.array([244, 232, 200], np.float32)
img = paper[None, None, :] * (0.93 + 0.08 * blot[..., None]) - 7 * (grit[..., None] - 0.5)
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out / "parchment.webp", "WEBP", quality=86, method=6)
for f in ("wood", "parchment"):
    print(f, (out / (f + ".webp")).stat().st_size // 1024, "KB")
