"""Current-vs-new sheets and the two-character clip for docs/design/phase4 (inputs: cur-*.png, new-*.png, packed atlases)."""
from PIL import Image, ImageDraw, ImageFont
import json, os
O = 'docs/design/phase4/'
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
def pair(name, a, b, title):
    A = Image.open(O + a).convert('RGB'); B = Image.open(O + b).convert('RGB'); w, h = A.size
    S = Image.new('RGB', (w, h * 2 + 140), (14, 18, 24)); d = ImageDraw.Draw(S)
    d.text((16, 16), 'CURRENT (live)  ' + title, font=F, fill=(190, 200, 210)); S.paste(A, (0, 70))
    d.text((16, h + 86), 'NEW (not published)', font=F, fill=(255, 190, 60)); S.paste(B, (0, h + 140))
    S.save(O + name, quality=88)
pair('battle.jpg', 'cur-battle.png', 'new-battle.png', 'stage 1 at 0:27')
pair('impact.jpg', 'cur-impact.png', 'new-impact.png', 'a cannon hit')
pair('menu.jpg', 'cur-quartermaster.png', 'new-quartermaster.png', 'Quartermaster')
def frames(group, sid):
    out = {}
    for k in [''] + [str(i) for i in range(2, 9)]:
        try: js = json.load(open('public/assets/%s%s.json' % (group, k)))
        except FileNotFoundError: continue
        if sid not in js['sprites']: continue
        im = Image.open('public/assets/' + js['image']).convert('RGBA')
        for an, a in js['sprites'][sid]['anims'].items():
            out[an] = [(im.crop((x, y, x + w, y + h)), ax, ay) for x, y, w, h, ax, ay in a['frames']]
    return out
hg = frames('units', 'ashguard'); dr = frames('enemies', 'husk')
near = Image.open('public/assets/bg/r1_near.webp').convert('RGBA'); mid = Image.open('public/assets/bg/r1_mid.webp').convert('RGBA'); sky = Image.open('public/assets/bg/r1_sky.webp').convert('RGBA')
W, H = 760, 400
base = Image.new('RGBA', (W, H), (236, 150, 110, 255)); base.paste(sky.resize((1755, 810)).crop((500, 260, 500 + W, 260 + H)), (0, 0))
base.alpha_composite(mid.crop((1000, 810 - H - 150, 1000 + W, 810 - 150))); base.alpha_composite(near.crop((1500, 810 - H - 150, 1500 + W, 810 - 150)))
gy = H - 112; lab = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
gif = []; strip = []
for an, rep in (('idle', 2), ('walk', 2), ('attack', 2), ('hit', 2), ('die', 1)):
    n = max(len(hg[an]), len(dr[an]))
    for r in range(rep):
        for i in range(n):
            fr = base.copy()
            for S, x in ((hg, 230), (dr, 540)):
                im, ax, ay = S[an][min(i, len(S[an]) - 1)]
                sh = Image.new('RGBA', (160, 26), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((0, 0, 159, 25), fill=(20, 10, 25, 110)); fr.alpha_composite(sh, (x - 95, gy - 12))
                fr.alpha_composite(im, (int(x - ax), int(gy - ay)))
            ImageDraw.Draw(fr).text((14, 10), an, font=lab, fill=(255, 255, 255, 255))
            gif.append(fr.convert('P', palette=Image.ADAPTIVE, colors=200))
            if r == 0: strip.append((an, i, fr.convert('RGB')))
    if an == 'die': gif += [gif[-1]] * 8
gif[0].save(O + 'two-characters.gif', save_all=True, append_images=gif[1:], duration=83, loop=0)
pick = [s for s in strip if s[0] == 'attack' or (s[0] == 'idle' and s[1] in (0, 4)) or (s[0] == 'die' and s[1] in (2, 5, 9))][:15]
S = Image.new('RGB', (W // 2 * 5, H // 2 * 3))
for k, (an, i, im) in enumerate(pick): S.paste(im.resize((W // 2, H // 2)), ((k % 5) * (W // 2), (k // 5) * (H // 2)))
S.save(O + 'two-characters-strip.jpg', quality=88)
print('gif KB', os.path.getsize(O + 'two-characters.gif') // 1024)
