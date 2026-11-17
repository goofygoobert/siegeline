"""Before/after sheets for docs/design/compare (old-*.png from the live build, new-*.png from the preview build)."""
from PIL import Image, ImageDraw, ImageFont
import sys; sys.path.insert(0, 'art/blender'); import cast
O = 'docs/design/compare/'
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
def pair(name, a, b, title=''):
    A = Image.open(O + a).convert('RGB'); B = Image.open(O + b).convert('RGB')
    w, h = A.size; S = Image.new('RGB', (w * 2 + 24, h + 64), (18, 14, 12)); S.paste(A, (0, 64)); S.paste(B, (w + 24, 64))
    d = ImageDraw.Draw(S); d.text((16, 12), 'BEFORE (live)  ' + title, font=F, fill=(200, 190, 170)); d.text((w + 40, 12), 'AFTER (preview)', font=F, fill=(255, 214, 130))
    S.thumbnail((2400, 2400)); S.save(O + name, quality=88)
pair('2-stage.jpg', 'old-tutorial.png', 'new-tutorial.png', 'fort and cove')
pair('3-menu.jpg', 'old-quartermaster.png', 'new-quartermaster.png', 'Quartermaster')
pair('3b-hud.jpg', 'old-battle.png', 'new-battle.png', 'battle HUD, 0:41')
pair('4-feel.jpg', 'old-impact.png', 'new-impact.png', 'cannon impact')
bg = Image.open('public/assets/bg/r1_near.webp').convert('RGBA'); mid = Image.open('public/assets/bg/r1_mid.webp').convert('RGBA'); sky = Image.open('public/assets/bg/r1_sky.webp').convert('RGBA')
def stage(w=1100, h=520):
    s = Image.new('RGBA', (w, h), (236, 150, 110, 255)); s.paste(sky.resize((1755, 810)).crop((300, 180, 300 + w, 180 + h)), (0, 0))
    s.alpha_composite(mid.crop((900, 810 - h - 110, 900 + w, 810 - 110))); s.alpha_composite(bg.crop((1500, 810 - h - 110, 1500 + w, 810 - 110))); return s
def put(s, job, sid, frame, x, gy=405, ppu_to=120):
    J = cast.JOBS[job]; cw, ch = J['cell']; ids = J['ids']; i = ids.index(sid); cols = min(J['cols'], len(ids))
    im = Image.open('art/out/%s/frame_%04d.png' % (job, frame)).convert('RGBA').crop(((i % cols) * cw, (i // cols) * ch, (i % cols + 1) * cw, (i // cols + 1) * ch))
    k = ppu_to / J['ppu']; im = im.resize((int(cw * k), int(ch * k)), Image.LANCZOS); ax, ay = cast.cell_anchor(job, sid); s.alpha_composite(im, (x - int(ax * k), gy - int(ay * k)))
old = stage(); new = stage()
for x, f in ((190, 1), (430, 19)): put(old, 'units', 'ashguard', f, x)
for x, f in ((700, 1), (930, 19)): put(old, 'field', 'husk', f, x)
for x, f in ((190, 1), (430, 22)): put(new, 'v2', 'ashguard', f, x)
for x, f in ((700, 1), (930, 22)): put(new, 'v2', 'husk', f, x)
S = Image.new('RGB', (2224, 584), (18, 14, 12)); S.paste(old.convert('RGB'), (0, 64)); S.paste(new.convert('RGB'), (1124, 64))
d = ImageDraw.Draw(S); d.text((16, 14), 'BEFORE (live)  Hatchguard and Drowner: standing, striking', font=F, fill=(200, 190, 170)); d.text((1140, 14), 'AFTER (preview)', font=F, fill=(255, 214, 130))
S.save(O + '1-characters.jpg', quality=88)
