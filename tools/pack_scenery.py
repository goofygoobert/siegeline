"""Pack scenery renders into shipped assets (run with .venv/bin/python).

  tools/pack_scenery.py [castles] [fx] [bg] [title] [worldmap]     (no args = all that have renders)

Inputs (gpu5070 renders):  art/out/scenery/{castles,fx,bg,title,worldmap}/frame_NNNN.png
Outputs: public/assets/castles.{webp,json}, fx.{webp,json}, bg/*.webp + bg/manifest.json, title.webp, worldmap.webp
Sprites are rendered at 96 px/u and downscaled to the contract's 72 ppu, trimmed, shelf-packed (<= 2048 wide).
Anchors are computed from the render camera (constants below mirror art/blender/bg/castles.py and fx.py).
"""
import sys, json, math, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "assets"
SRC = ROOT / "art" / "out" / "scenery"
PPU, RPPU = 72, 96
SCALE = PPU / RPPU
Q = 82
PAD = 2


def frame(d, i):
    return Image.open(SRC / d / f"frame_{i:04d}.png").convert("RGBA")


def shrink(im):
    w, h = im.size
    return im.convert("RGBa").resize((round(w * SCALE), round(h * SCALE)), Image.LANCZOS).convert("RGBA")


def trim(im, anchor):
    """Downscale + trim; returns (image, anchor in the trimmed image)."""
    im = shrink(im); ax, ay = anchor[0] * SCALE, anchor[1] * SCALE
    a = im.getchannel("A").point(lambda v: 255 if v > 3 else 0)
    bb = a.getbbox() or (0, 0, 1, 1)
    return im.crop(bb), (round(ax - bb[0], 1), round(ay - bb[1], 1))


def pack(items, maxw=2048):
    """items: list of (key, img). Shelf packing, tallest first. Returns ({key: (x, y)}, W, H)."""
    order = sorted(items, key=lambda kv: -kv[1].size[1])
    x = y = shelf = 0; pos = {}; W = 0
    for k, im in order:
        w, h = im.size
        if x + w + PAD > maxw:
            x = 0; y += shelf + PAD; shelf = 0
        pos[k] = (x + PAD, y + PAD); x += w + PAD; shelf = max(shelf, h); W = max(W, x + PAD)
    H = y + shelf + 2 * PAD
    return pos, W, H


def write_atlas(group, sprites):
    """sprites: {id: {anim: dict(fps, loop, frames=[(img, anchor)], hit?)}}"""
    items = []
    for sid, anims in sprites.items():
        for an, A in anims.items():
            for fi, (im, _) in enumerate(A["frames"]):
                items.append(((sid, an, fi), im))
    pos, W, H = pack(items)
    assert W <= 2048 and H <= 2048, (group, W, H)
    sheet = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    js = {"image": f"{group}.webp", "w": W, "h": H, "ppu": PPU, "sprites": {}}
    for sid, anims in sprites.items():
        ja = {}
        for an, A in anims.items():
            fr = []
            for fi, (im, (ax, ay)) in enumerate(A["frames"]):
                x, y = pos[(sid, an, fi)]; sheet.paste(im, (x, y))
                fr.append([x, y, im.size[0], im.size[1], ax, ay])
            e = {"fps": A["fps"], "loop": A["loop"], "frames": fr}
            if "hit" in A:
                e["hit"] = A["hit"]
            ja[an] = e
        js["sprites"][sid] = {"anims": ja}
    sheet.save(OUT / f"{group}.webp", "WEBP", quality=Q, method=6)
    (OUT / f"{group}.json").write_text(json.dumps(js, separators=(",", ":")))
    print(group, W, H, (OUT / f"{group}.webp").stat().st_size // 1024, "KB")


def single(img, anchor):
    return {"idle": dict(fps=1, loop=False, frames=[trim(img, anchor)])}


def castles():
    cell, cz, e = 864, 4.0, math.radians(10)   # mirrors castles.py (CAM_ELEV)
    ground = (cell / 2 + cz * math.cos(e) * RPPU)
    sp = {}
    for k in range(3):
        sp[f"keep_{k}"] = single(frame("castles", 1 + k), (cell / 2 - 0.4 * RPPU, ground))
    for k in range(3):
        sp[f"maw_{k}"] = single(frame("castles", 4 + k), (cell / 2, ground))
    sp["ballista"] = single(frame("castles", 7), (cell / 2 - 0.5 * RPPU, cell / 2))
    write_atlas("castles", sp)


def fx():
    c = (192, 192)
    names = ["arrow", "bolt", "spit", "fireball", "ember_stone"]
    sp = {n: single(frame("fx", i + 1), c) for i, n in enumerate(names)}
    sp["fire_patch"] = {"idle": dict(fps=10, loop=True, frames=[trim(frame("fx", 6 + i), c) for i in range(6)])}
    sp["blast"] = {"idle": dict(fps=14, loop=False, frames=[trim(frame("fx", 12 + i), c) for i in range(8)])}
    sp["flare"] = {"idle": dict(fps=14, loop=False, frames=[trim(frame("fx", 20 + i), c) for i in range(6)])}
    write_atlas("fx", sp)


BG = [("sky", 1755, 0.0), ("far", 2077, 0.15), ("mid", 2720, 0.45), ("near", 3900, 1.0)]


def bg():
    d = OUT / "bg"; d.mkdir(parents=True, exist_ok=True); man = {}
    for vi, reg in enumerate(("r1", "r1n")):
        m = {}
        for li, (name, w, par) in enumerate(BG):
            im = frame("bg", 1 + vi * 4 + li).crop((0, 0, w, 810))
            fn = f"{reg}_{name}.webp"
            if name == "sky":
                im.convert("RGB").save(d / fn, "WEBP", quality=Q, method=6); m["sky"] = fn
            else:
                im.save(d / fn, "WEBP", quality=Q, method=6); m[name] = {"file": fn, "parallax": par}
            print(fn, (d / fn).stat().st_size // 1024, "KB")
        man[reg] = m
    (d / "manifest.json").write_text(json.dumps(man, indent=1))


def title():
    im = frame("title", 1).convert("RGB")
    assert im.size == (1920, 1080), im.size
    im.save(OUT / "title.webp", "WEBP", quality=85, method=6)
    print("title.webp", (OUT / "title.webp").stat().st_size // 1024, "KB")


def worldmap():
    im = frame("worldmap", 1).convert("RGB")
    assert im.size == (2048, 1024), im.size
    # soft painted vignette
    from PIL import ImageDraw, ImageFilter, ImageChops
    m = Image.new("L", (256, 128), 0); ImageDraw.Draw(m).ellipse((-30, -24, 286, 152), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(18)).resize(im.size, Image.BICUBIC).point(lambda v: 150 + v * 105 // 255)
    im = ImageChops.multiply(im, Image.merge("RGB", (m, m, m)))
    im.save(OUT / "worldmap.webp", "WEBP", quality=85, method=6)
    sys.path.insert(0, str(ROOT / "art" / "blender" / "bg"))
    import map_lib
    (OUT / "worldmap.json").write_text(json.dumps({"regions": map_lib.markers()}, indent=1))
    print("worldmap.webp", (OUT / "worldmap.webp").stat().st_size // 1024, "KB")


def record_sizes():
    notes = ROOT / "docs" / "scenery-notes.md"
    if not notes.exists():
        return
    files = [OUT / f for f in ("castles.webp", "castles.json", "fx.webp", "fx.json", "title.webp", "worldmap.webp", "worldmap.json")]
    files += sorted((OUT / "bg").glob("*.webp")) + [OUT / "bg" / "manifest.json"]
    rows = ["| file | size |", "|---|---|"]
    tot = 0
    for f in files:
        if f.exists():
            n = f.stat().st_size; tot += n
            rows.append(f"| {f.relative_to(OUT)} | {n / 1024:.1f} KB |")
    rows.append(f"| **total** | **{tot / 1024:.1f} KB** |")
    t = notes.read_text(); a = t.index("<!-- sizes -->") + len("<!-- sizes -->"); b = t.index("<!-- /sizes -->")
    notes.write_text(t[:a] + "\n" + "\n".join(rows) + "\n" + t[b:])


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = sys.argv[1:] or ["castles", "fx", "bg", "title", "worldmap"]
    for j in jobs:
        if not (SRC / j.replace("castles", "castles")).exists():
            print("skip", j, "(no renders)"); continue
        globals()[j]()
    record_sizes()
