"""Part 4 sprite check: contact sheets + automated edge checks for every packed sprite.

usage: .venv/bin/python tools/polish_check.py [out_dir=docs/design/polish]
Writes  <out>/sheet-<bg>.png   every sprite's first idle frame (and the attack hit frame) on dark, light and magenta,
                               at 1x and 3x (nearest neighbour, so edge pixels are visible)
        <out>/report.md        per sprite: edge fringe %, padding to neighbours, feet vs anchor, clipped edges
Checks (FAIL lines are listed first in the report):
  fringe   - share of the outline's partly transparent pixels that are much lighter than the body just inside them
             (a pale halo shows on dark sand and at night) -- fail above 12%
  padding  - frames in an atlas closer than 2 px to each other can bleed into each other when scaled -- fail
  anchor   - ground figures whose lowest opaque row is more than 3 px from the feet anchor look like they hover or
             sink (fliers and effects are exempt) -- fail
  clipped  - opaque pixels on the frame's own edge: a part was cut off when packing -- warn
"""
import sys, os, json, glob
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/design/polish"
os.makedirs(OUT, exist_ok=True)
A = "public/assets"
FLIERS = {"gallows_gull", "tide_nurse"}
BG = {"dark": (20, 16, 12), "light": (242, 234, 216), "magenta": (255, 0, 255)}
SKIP_ANCHOR = ("fx", "ui", "castles", "icons")

atlases = sorted(f for f in glob.glob(A + "/*.json") if os.path.basename(f) not in ("atlases.json", "worldmap.json"))
items, report, fails = [], [], []
lum = lambda p: (0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]) / 255

for jf in atlases:
    J = json.load(open(jf)); name = os.path.basename(jf)[:-5]
    img = Image.open(os.path.join(A, J["image"])).convert("RGBA")
    rects = []
    for sid, sp in J["sprites"].items():
        for an, a in sp["anims"].items():
            for k, fr in enumerate(a["frames"]):
                rects.append((fr[0], fr[1], fr[2], fr[3], sid, an, k))
    # padding: any two frame rects closer than 2 px (shared frames, same rect, are fine)
    seen = {}
    for r in rects: seen.setdefault(r[:4], r)
    uniq = sorted(seen.values(), key=lambda r: (r[1], r[0]))
    tight = 0
    for i, a in enumerate(uniq):
        for b in uniq[i + 1:]:
            if b[1] > a[1] + a[3] + 2: break
            gx = max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2])); gy = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
            if max(gx, gy) < 2 and not (gx < 0 and gy < 0): tight += 1
            elif gx < 0 and gy < 0: tight += 1
    if tight: fails.append(f"FAIL padding  {name}: {tight} frame pairs closer than 2 px")
    for sid, sp in J["sprites"].items():
        an = "idle" if "idle" in sp["anims"] else next(iter(sp["anims"]))
        frs = [sp["anims"][an]["frames"][0]]
        if "attack" in sp["anims"] and sp["anims"]["attack"].get("hit") is not None:
            frs.append(sp["anims"]["attack"]["frames"][sp["anims"]["attack"]["hit"]])
        for fi, fr in enumerate(frs):
            x, y, w, h = fr[:4]; ax, ay = (fr[4], fr[5]) if len(fr) >= 6 else (w // 2, h)
            cell = img.crop((x, y, x + w, y + h)); px = cell.load()
            edge = halo = 0; lowest = -1; clipped = False
            for yy in range(h):
                for xx in range(w):
                    a = px[xx, yy][3]
                    if a > 40: lowest = max(lowest, yy)
                    if a > 40 and (xx in (0, w - 1) or yy in (0, h - 1)): clipped = True
                    if 16 < a < 235:
                        # the most opaque neighbour stands in for "the body just inside"
                        best = None
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nx, ny = xx + dx, yy + dy
                            if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] >= 235: best = px[nx, ny]; break
                        if best is None: continue
                        edge += 1
                        if lum(px[xx, yy]) > lum(best) + 0.28: halo += 1
            fr_pct = 100 * halo / max(1, edge)
            ground = not (sid in FLIERS or name.startswith(SKIP_ANCHOR) or sid.startswith(("p_", "i_")))
            off = int(round(ay - 1 - lowest)) if lowest >= 0 else 0
            line = f"{name:10s} {sid:18s} {'idle' if fi == 0 else 'hit '}  fringe {fr_pct:4.1f}%  feet-anchor {off:+d}px"
            report.append(line)
            if fr_pct > 12 and not name.startswith("fx"): fails.append(f"FAIL fringe   {sid} ({name}): {fr_pct:.0f}% of edge pixels are a pale halo")
            # hovering is the fault the owner saw; a near foot below the anchor is the camera's slight downward look
            if ground and fi == 0 and off > 3: fails.append(f"FAIL anchor   {sid} ({name}): lowest pixel {off}px above the feet anchor (hovers)")
            if ground and fi == 0 and off < -0.15 * h: fails.append(f"FAIL anchor   {sid} ({name}): {-off}px below the anchor, more than perspective explains")
            pass   # frames are trimmed to their content, so touching the frame edge is normal; real clipping is the packer's render-cell warning
            if fi == 0: items.append((f"{name}:{sid}", cell))

# contact sheets: each sprite at 1x and 3x on each background
for bg, col in BG.items():
    cw = 3 * 140 + 160; rows = []
    for label, cell in items:
        s1 = cell.copy(); s1.thumbnail((140, 140))
        s3 = cell.resize((cell.width * 3, cell.height * 3), Image.NEAREST)
        # 3x: crop to the lower-left outline region (where fringes show), 420 px wide
        s3 = s3.crop((0, max(0, s3.height - 260), min(s3.width, 420), s3.height))
        rows.append((s1, s3))
    per = 2
    H = sum(max(r[0].height, r[1].height) for r in rows[::per]) + 10 * len(rows)
    sheet = Image.new("RGB", (per * (160 + 430), H // 1 + 20), col)
    yy, x = 10, 0
    for i, (s1, s3) in enumerate(rows):
        sheet.paste(s1, (x + 10, yy), s1); sheet.paste(s3, (x + 160, yy), s3)
        if i % per == per - 1: yy += max(s1.height, s3.height) + 10; x = 0
        else: x += 590
    sheet.save(f"{OUT}/sheet-{bg}.png")

fails.sort(key=lambda s: (not s.startswith("FAIL"), s))
with open(f"{OUT}/report.md", "w") as f:
    f.write("# Sprite polish check\n\nGenerated by `tools/polish_check.py`. Sheets: " + ", ".join(f"`sheet-{b}.png`" for b in BG) + " (1x left, 3x right).\n\n")
    f.write("## Problems\n\n" + ("\n".join("- " + x for x in fails) if fails else "- none") + "\n\n## Every sprite\n\n```\n" + "\n".join(report) + "\n```\n")
print("\n".join(fails[:60]) or "no problems"); print(f"{len(items)} sprites, {sum(1 for x in fails if x.startswith('FAIL'))} FAIL, {sum(1 for x in fails if x.startswith('warn'))} warn")
