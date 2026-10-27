# Background for DIDI news cards (1080x1080). n8n writes the league tag and the headline on top of it.
# Text slots (px): tag at x=250,y=262 (lime, ~30px); headline at x=64, y=340..860 (white, ~66px, ~22 chars per line).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
import render_lib as R

S = R.S; W = H = 540 * S
img = R.vgrad(W, H, (0, 0, W, H), [(0, (10, 26, 17)), (.55, (5, 12, 8)), (1, (2, 5, 3))])
d = ImageDraw.Draw(img)
# faint diagonal stripes
st = R.layer(W, H); sd = ImageDraw.Draw(st)
for x in range(-H, W, 34 * S): sd.line([(x, H), (x + H, 0)], fill=(178, 255, 46, 10), width=6 * S)
img.alpha_composite(st)
# faint pitch markings in the lower half (perspective)
pl = R.layer(W, H); pd = ImageDraw.Draw(pl); c = (178, 255, 46, 38); w = 2 * S
pd.line([(0, 430 * S), (W, 430 * S)], fill=c, width=w)
pd.ellipse([180 * S, 390 * S, 360 * S, 470 * S], outline=c, width=w)
pd.ellipse([266 * S, 427 * S, 274 * S, 433 * S], fill=c)
pd.line([(-40 * S, 540 * S), (60 * S, 300 * S)], fill=c, width=w); pd.line([(580 * S, 540 * S), (480 * S, 300 * S)], fill=c, width=w)
img.alpha_composite(pl.filter(ImageFilter.GaussianBlur(0.6 * S)))
# lime glow behind the ball and a soft one bottom-left
for (cx, cy, r, a) in [(470, 95, 150, 70), (40, 540, 200, 35)]:
    g = R.layer(W, H); ImageDraw.Draw(g).ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=R.LIME + (a,))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(70 * S)))
R.ball(img, 478 * S, 92 * S, 66 * S)
# wordmark
R.italic_text(img, (30 * S, 18 * S), 'DIDI', R.font('kd', 58), lambda bb: R.vgrad(W, H, bb, R.CHROME), stroke=3 * S, stroke_fill=(0, 0, 0), glow_col=(120, 255, 60), glow_r=10)
d = ImageDraw.Draw(img)
d.text((36 * S, 86 * S), 'F O O T B A L L', font=R.font('x', 13), fill=R.LIME)
d.text((36 * S, 104 * S), 'прогнози · статистика · результати', font=R.font('m', 10), fill=R.MUTED)
# "НОВИНИ" pill
R.rrect(img, (32 * S, 126 * S, 112 * S, 152 * S), 13 * S, R.LIME + (255,))
d = ImageDraw.Draw(img); f = R.font('k', 13); t = 'НОВИНИ'; tw = d.textlength(t, font=f)
d.text((72 * S - tw / 2, 131 * S), t, font=f, fill=(6, 12, 9))
# accent bar left of the headline
R.rrect(img, (18 * S, 172 * S, 22 * S, 300 * S), 2 * S, R.LIME + (255,))
# bottom bar
d.line([(32 * S, 486 * S), (508 * S, 486 * S)], fill=R.LIME + (120,), width=1 * S)
d.text((32 * S, 498 * S), '@didi_football_tips', font=R.font('s', 15), fill=R.WHITE)
t = 'аналітика · чесна статистика · 18+'; f = R.font('m', 11); tw = d.textlength(t, font=f)
d.text((508 * S - tw, 502 * S), t, font=f, fill=R.MUTED)
img.convert('RGB').save(os.path.join(R.BASE, 'assets', 'news_bg.jpg'), quality=92)
print('ok', img.size)
