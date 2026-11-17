"""Pack rendered character frames into WebP atlases + json (docs/asset-contract.md).

Usage: .venv/bin/python tools/pack_sprites.py [--sheets] [atlas ...]     (atlases: units hero enemies boss ui)

Reads art/out/<job>/frame_NNNN.png (whole-job grid renders, see art/blender/cast.py), cuts each id's cell,
downsizes from the render ppu (96) to the atlas ppu (72), trims, dedupes identical frames, shelf-packs into
pages <= 2048x2048 (an id never spans two pages; overflow pages are named <group>2, <group>3, ...), writes
public/assets/<page>.webp (alpha, q82) + <page>.json. Anchor = feet point (fixed cell anchor -> no jitter).
--sheets also writes art/out/review_<page>.png: one row per id on a dusk background, ground line at the anchor.
"""
import sys, json, hashlib, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "art" / "blender"))
import cast  # noqa: E402

OUT = ROOT / "public" / "assets"
MAX = 2048
PAD = 2


def cell_rects(job):
    J = cast.JOBS[job]; cw, ch = J["cell"]; cols = min(J["cols"], len(J["ids"]))
    return {sid: ((i % cols) * cw, (i // cols) * ch, cw, ch) for i, sid in enumerate(J["ids"])}


def cut_frames(atlas, ppu):
    """Returns {id: {anim: [(img, ax, ay), ...]}} and warnings."""
    A = cast.ATLASES[atlas]; job = A["job"]; J = cast.JOBS[job]
    scale = A.get("out_scale", ppu / J["ppu"])
    still = J["mode"] == "still"
    rects = cell_rects(job)
    # frame number -> list of (id, anim, index)
    want = {}
    for sid in A["ids"]:
        f = 1
        for (name, n, fps, loop, hit) in cast.anims_of(sid):
            for i in range(n):
                want.setdefault(f, []).append((sid, name, i)); f += 1
    res = {sid: {} for sid in A["ids"]}; warn = []
    for fnum in sorted(want):
        path = ROOT / "art" / "out" / job / ("frame_%04d.png" % fnum)
        im = Image.open(path).convert("RGBA")
        for sid, name, i in want[fnum]:
            x, y, cw, ch = rects[sid]
            cell = im.crop((x, y, x + cw, y + ch))
            a = cell.getchannel("A")
            edge = max(a.crop((0, 0, cw, 2)).getextrema()[1], a.crop((0, ch - 2, cw, ch)).getextrema()[1],
                       a.crop((0, 0, 2, ch)).getextrema()[1], a.crop((cw - 2, 0, cw, ch)).getextrema()[1])
            if edge > 0 and not still:
                warn.append("%s %s[%d] touches the cell edge (clipped?)" % (sid, name, i))
            nw, nh = round(cw * scale), round(ch * scale)
            small = cell.convert("RGBa").resize((nw, nh), Image.LANCZOS).convert("RGBA")
            ax, ay = cast.cell_anchor(job, sid)
            ax, ay = ax * scale, ay * scale
            if not still:
                bb = small.getchannel("A").point(lambda v: 255 if v > 6 else 0).getbbox()
                if bb is None:
                    bb = (int(ax), int(ay) - 1, int(ax) + 1, int(ay))
                small = small.crop(bb); ax -= bb[0]; ay -= bb[1]
            res[sid].setdefault(name, []).append((small, round(ax, 1), round(ay, 1)))
        im.close()
    return res, warn


class Shelf:
    def __init__(self):
        self.shelves = []; self.h = 0; self.w = 0

    def fits_all(self, sizes):
        saved = ([s[:] for s in self.shelves], self.h, self.w)
        ok = all(self.add(w, h) is not None for w, h in sizes)
        self.shelves, self.h, self.w = saved
        return ok

    def add(self, w, h):
        w += PAD; h += PAD
        for s in self.shelves:     # s = [y, height, x]
            if h <= s[1] and s[2] + w <= MAX:
                p = (s[2], s[0]); s[2] += w; self.w = max(self.w, s[2]); return p
        if self.h + h > MAX or w > MAX:
            return None
        self.shelves.append([self.h, h, w]); p = (0, self.h); self.h += h; self.w = max(self.w, w)
        return p


def pack(atlas, sheets=False):
    A = cast.ATLASES[atlas]
    for ppu in (A["ppu"], 64, 56, 48):
        data, warn = cut_frames(atlas, ppu)
        # unique images per id
        uniq = {}
        for sid in A["ids"]:
            for name, frames in data[sid].items():
                for (img, ax, ay) in frames:
                    hsh = hashlib.md5(img.tobytes() + bytes(str(img.size), "ascii")).hexdigest()
                    uniq.setdefault((sid, hsh), img)
        too_big = False
        pages = []; cur = None
        for sid in A["ids"]:
            items = sorted([(k, v) for k, v in uniq.items() if k[0] == sid], key=lambda kv: -kv[1].height)
            sizes = [(v.width, v.height) for k, v in items]
            if cur is None or not cur["shelf"].fits_all(sizes):
                cur = dict(shelf=Shelf(), ids=[], place={}); pages.append(cur)
                if not cur["shelf"].fits_all(sizes):
                    too_big = True; break
            for (k, v) in items:
                cur["place"][k] = cur["shelf"].add(v.width, v.height)
            cur["ids"].append(sid)
        if not too_big:
            break
        print("  %s does not fit one page at ppu %d, trying smaller" % (atlas, ppu))
    out = []
    for pi, pg in enumerate(pages):
        name = atlas if pi == 0 else "%s%d" % (atlas, pi + 1)
        W = (pg["shelf"].w + 3) // 4 * 4; H = (pg["shelf"].h + 3) // 4 * 4
        sheet = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        js = {"image": name + ".webp", "w": W, "h": H, "ppu": ppu, "sprites": {}}
        for sid in pg["ids"]:
            anims = {}
            for (aname, n, fps, loop, hit) in cast.anims_of(sid):
                fr = []
                for (img, ax, ay) in data[sid][aname]:
                    hsh = hashlib.md5(img.tobytes() + bytes(str(img.size), "ascii")).hexdigest()
                    x, y = pg["place"][(sid, hsh)]
                    sheet.paste(img, (x, y))
                    fr.append([x, y, img.width, img.height, ax, ay])
                a = {"fps": fps, "loop": loop, "frames": fr}
                if hit is not None:
                    a["hit"] = hit
                anims[aname] = a
            js["sprites"][sid] = {"anims": anims}
        OUT.mkdir(parents=True, exist_ok=True)
        sheet.save(OUT / (name + ".webp"), "WEBP", quality=82, method=6)
        (OUT / (name + ".json")).write_text(json.dumps(js, separators=(",", ":")))
        kb = (OUT / (name + ".webp")).stat().st_size / 1024
        print("%-9s %4dx%-4d ppu %d  %6.0f KB  ids: %s" % (name, W, H, ppu, kb, " ".join(pg["ids"])))
        out.append((name, W, H, ppu, kb, pg["ids"]))
        if sheets:
            review(name, js, sheet)
    for w in warn[:12]:
        print("  WARN", w)
    if len(warn) > 12:
        print("  WARN ... %d more" % (len(warn) - 12))
    return out


def review(name, js, sheet, per=12):
    """Rows of `per` frames per id, at atlas size (= phone-ish size), dusk background, ground line at anchor."""
    rows = []
    for sid, sp in js["sprites"].items():
        frames = [f for a in sp["anims"].values() for f in a["frames"]]
        up = max(f[5] for f in frames); down = max(f[3] - f[5] for f in frames)
        for k in range(0, len(frames), per):
            rows.append((sid if k == 0 else "", frames[k:k + per], int(up) + 4, int(down) + 4))
    colw = max(max(f[2] for f in fr) for _, fr, _, _ in rows) + 6
    H = sum(u + d + 14 for _, _, u, d in rows)
    img = Image.new("RGB", (colw * per, H), (42, 34, 38)); dr = ImageDraw.Draw(img)
    y = 0
    for sid, frames, up, down in rows:
        dr.text((3, y + 1), sid, fill=(255, 220, 120))
        gy = y + 14 + up
        dr.line([(0, gy), (img.width, gy)], fill=(90, 70, 60))
        for i, (x0, y0, w, h, ax, ay) in enumerate(frames):
            cx = i * colw + colw // 2
            im = sheet.crop((x0, y0, x0 + w, y0 + h))
            img.paste(im, (int(cx - ax), int(gy - ay)), im)
        y += up + down + 14
    p = ROOT / "art" / "out" / ("review_%s.png" % name)
    img.save(p); print("  review:", p)


if __name__ == "__main__":
    args = sys.argv[1:]
    sheets = "--sheets" in args
    names = [a for a in args if not a.startswith("--")] or list(cast.ATLASES)
    for n in names:
        if not (ROOT / "art" / "out" / cast.ATLASES[n]["job"]).exists():
            print("skip", n, "(job not rendered)"); continue
        pack(n, sheets)
