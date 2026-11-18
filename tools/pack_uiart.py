"""Crop the interface art renders (art/out/scenery/uiart) to public/assets/icons/{coin,cannon,keg}.webp."""
import pathlib
from PIL import Image
root = pathlib.Path(__file__).resolve().parents[1]
out = root / "public" / "assets" / "icons"; out.mkdir(parents=True, exist_ok=True)
for i, name in enumerate(("coin", "cannon", "keg"), start=1):
    im = Image.open(root / "art" / "out" / "scenery" / "uiart" / ("frame_%04d.png" % i)).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    im = im.crop(bb); s = max(im.size) + 8
    sq = Image.new("RGBA", (s, s)); sq.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    sq.resize((192, 192), Image.LANCZOS).save(out / (name + ".webp"), "WEBP", quality=88, method=6)
    print(name, (out / (name + ".webp")).stat().st_size // 1024, "KB")
