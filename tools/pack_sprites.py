"""Pack rendered character frames into WebP atlases + json (docs/asset-contract.md).

Usage: .venv/bin/python tools/pack_sprites.py [--sheets] [atlas ...]     (atlases: units hero enemies boss ui)

Reads art/out/<job>/frame_NNNN.png (whole-job grid renders, see art/blender/cast.py), cuts each id's cell,
downsizes from the render ppu (96) to the atlas ppu (72), trims, dedupes identical frames, shelf-packs into
pages <= 2048x2048 (an id never spans two pages; overflow pages are named <group>2, <group>3, ...), writes
public/assets/<page>.webp (alpha, q82) + <page>.json. Anchor = feet point (fixed cell anchor -> no jitter).
--sheets also writes art/out/review_<page>.png: one row per id on a dusk background, ground line at the anchor.
"""
import sys, os, re, json, hashlib, pathlib
from PIL import Image, ImageDraw, ImageFilter

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
            sides = "".join(k for k, box in (("T", (0, 0, cw, 2)), ("B", (0, ch - 2, cw, ch)), ("L", (0, 0, 2, ch)),
                                              ("R", (cw - 2, 0, cw, ch))) if a.crop(box).getextrema()[1] > 0)
            if sides and not still:
                warn.append("%s %s[%d] touches the cell edge %s (clipped?)" % (sid, name, i, sides))
            nw, nh = round(cw * scale), round(ch * scale)
            small = cell.convert("RGBa").resize((nw, nh), Image.LANCZOS).convert("RGBA")
            if A.get("contour"):    # heavy outer ink line so figures read like stickers (docs/design/art-direction.md)
                ink = (12, 26, 30) if cast.is_enemy(sid) else (34, 21, 43)
                al = small.getchannel("A")
                fat = al.filter(ImageFilter.MaxFilter(2 * int(A["contour"]) + 1)).filter(ImageFilter.GaussianBlur(0.7))
                fat = fat.point(lambda v: min(255, int(v * 1.6)))
                under = Image.new("RGBA", small.size, ink + (0,)); under.putalpha(fat)
                small = Image.alpha_composite(under, small)
            ax, ay = cast.cell_anchor(job, sid)
            ax, ay = ax * scale, ay * scale
            if not still:
                bb = small.getchannel("A").point(lambda v: 255 if v > 6 else 0).getbbox()
                if bb is None:
                    bb = (int(ax), int(ay) - 1, int(ax) + 1, int(ay))
                small = small.crop(bb); ax -= bb[0]; ay -= bb[1]
            num = lambda v: int(round(v)) if abs(v - round(v)) < 0.05 else round(v, 1)
            res[sid].setdefault(name, []).append((small, num(ax), num(ay)))
        im.close()
    return res, warn


class Shelf:
    """MaxRects bin (best-short-side-fit) on a MAX x MAX page; add() returns (x, y) or None."""
    def __init__(self):
        self.free = [(0, 0, MAX, MAX)]; self.w = 0; self.h = 0

    def add(self, w, h):
        w += PAD; h += PAD
        best = None
        for (fx, fy, fw, fh) in self.free:
            if w <= fw and h <= fh:
                score = (min(fw - w, fh - h), max(fw - w, fh - h), fy)
                if best is None or score < best[0]:
                    best = (score, fx, fy)
        if best is None:
            return None
        _, x, y = best
        nf = []
        for (fx, fy, fw, fh) in self.free:
            if x >= fx + fw or x + w <= fx or y >= fy + fh or y + h <= fy:
                nf.append((fx, fy, fw, fh)); continue
            if x > fx: nf.append((fx, fy, x - fx, fh))
            if x + w < fx + fw: nf.append((x + w, fy, fx + fw - x - w, fh))
            if y > fy: nf.append((fx, fy, fw, y - fy))
            if y + h < fy + fh: nf.append((fx, y + h, fw, fy + fh - y - h))
        # prune contained rects
        nf.sort(key=lambda r: -r[2] * r[3])
        keep = []
        for r in nf:
            if not any(r[0] >= k[0] and r[1] >= k[1] and r[0] + r[2] <= k[0] + k[2] and r[1] + r[3] <= k[1] + k[3] for k in keep):
                keep.append(r)
        self.free = keep
        self.w = max(self.w, x + w); self.h = max(self.h, y + h)
        return (x, y)


def pack(atlas, sheets=False):
    A = cast.ATLASES[atlas]
    for ppu in (A["ppu"], 64, 60, 56, 52, 48):
        data, warn = cut_frames(atlas, ppu)
        # unique images per id
        uniq = {}
        for sid in A["ids"]:
            for name, frames in data[sid].items():
                for (img, ax, ay) in frames:
                    hsh = hashlib.md5(img.tobytes() + bytes(str(img.size), "ascii")).hexdigest()
                    uniq.setdefault((sid, hsh), img)
        too_big = False
        byid = {sid: [(k, v) for k, v in uniq.items() if k[0] == sid] for sid in A["ids"]}

        def try_pack(ids):
            items = sorted([kv for i in ids for kv in byid[i]], key=lambda kv: -(kv[1].height * kv[1].width))
            sh = Shelf(); place = {}
            for k, v in items:
                p = sh.add(v.width, v.height)
                if p is None:
                    return None
                place[k] = p
            return dict(shelf=sh, ids=list(ids), place=place)

        pages = []
        for group in A.get("pages", [A["ids"]]):     # pinned page split (stable file names for the engine)
            cur_ids = []; cur = None
            for sid in group:
                nxt = try_pack(cur_ids + [sid])
                if nxt is None:
                    if not cur_ids:
                        too_big = True; break
                    print("  NOTE page overflow: %s starts a new page" % sid)
                    pages.append(cur); cur_ids = [sid]; cur = try_pack(cur_ids)
                    if cur is None:
                        too_big = True; break
                else:
                    cur_ids = cur_ids + [sid]; cur = nxt
            if too_big:
                break
            if cur is not None:
                pages.append(cur)
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
        # write to temp names first; swapped into place once the whole set is written (engine loads live)
        sheet.save(OUT / (name + ".webp.tmp"), "WEBP", quality=82, method=4)
        (OUT / (name + ".json.tmp")).write_text(json.dumps(js, separators=(",", ":")))
        kb = (OUT / (name + ".webp.tmp")).stat().st_size / 1024
        print("%-9s %4dx%-4d ppu %d  %6.0f KB  ids: %s" % (name, W, H, ppu, kb, " ".join(pg["ids"])))
        out.append((name, W, H, ppu, kb, pg["ids"]))
        if sheets:
            review(name, js, sheet)
    names = [o[0] for o in out]
    for n in names:      # webp first, then json, so a json never points at a missing/old image
        os.replace(OUT / (n + ".webp.tmp"), OUT / (n + ".webp"))
        os.replace(OUT / (n + ".json.tmp"), OUT / (n + ".json"))
    pat = re.compile(r"^%s(\d*)\.(json|webp)$" % re.escape(atlas))
    for f in OUT.iterdir():   # stale overflow pages from an older, longer split
        m = pat.match(f.name)
        if m and (atlas + m.group(1)) not in names:
            f.unlink(); print("  removed stale", f.name)
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


def write_size_table():
    """Refresh the 'Atlas sizes' section of docs/art-guide.md from what is in public/assets."""
    rows = []
    for g in cast.ATLASES:
        for f in sorted(OUT.glob(g + "*.json")):
            if not re.match(r"^%s\d*$" % g, f.stem):
                continue
            j = json.loads(f.read_text()); w = OUT / j["image"]
            rows.append("| %s | %dx%d | %d | %.0f KB | %s |" % (j["image"], j["w"], j["h"], j["ppu"], w.stat().st_size / 1024,
                                                        ", ".join(j["sprites"])))
    doc = ROOT / "docs" / "art-guide.md"; t = doc.read_text()
    head = "## Atlas sizes"
    t = t[:t.index(head)] if head in t else t + "\n"
    t += head + " (written by tools/pack_sprites.py)\n| file | size | ppu | bytes | ids |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n"
    doc.write_text(t)


if __name__ == "__main__":
    args = sys.argv[1:]
    sheets = "--sheets" in args
    names = [a for a in args if not a.startswith("--")] or list(cast.ATLASES)
    for n in names:
        if not (ROOT / "art" / "out" / cast.ATLASES[n]["job"]).exists():
            print("skip", n, "(job not rendered)"); continue
        pack(n, sheets)
    write_size_table()
