# DIDI channel avatar (1024x1024, safe for Telegram's round crop).
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
import render_lib as R
S = R.S; W = H = 512 * S; C = W // 2
img = Image.new('RGBA', (W, H), (2, 5, 3, 255))
g = R.layer(W, H); ImageDraw.Draw(g).ellipse([C - 230 * S, C - 230 * S, C + 230 * S, C + 230 * S], fill=(30, 90, 20, 255)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(90 * S)))
g = R.layer(W, H); ImageDraw.Draw(g).ellipse([C - 120 * S, C - 170 * S, C + 120 * S, C + 40 * S], fill=R.LIME + (110,)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(70 * S)))
# diagonal speed stripes
st = R.layer(W, H); sd = ImageDraw.Draw(st)
for x in range(-H, W, 30 * S): sd.line([(x, H), (x + H, 0)], fill=(178, 255, 46, 12), width=5 * S)
img.alpha_composite(st)
# neon ring inside the round crop
ring = R.layer(W, H); rd = ImageDraw.Draw(ring); r = 236 * S
rd.ellipse([C - r, C - r, C + r, C + r], outline=R.LIME + (255,), width=6 * S)
img.alpha_composite(ring.filter(ImageFilter.GaussianBlur(10 * S))); img.alpha_composite(ring)
# crown
d = ImageDraw.Draw(img); cw = 92 * S
gl = R.layer(W, H); R.crown(ImageDraw.Draw(gl), C - cw / 2, 92 * S, cw, R.GOLD + (255,)); img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(8 * S))); R.crown(ImageDraw.Draw(img), C - cw / 2, 92 * S, cw, R.GOLD)
# DIDI wordmark
f = R.font('kd', 150); tw = d.textlength('DIDI', font=f); bb = d.textbbox((0, 0), 'DIDI', font=f)
R.italic_text(img, (C - tw / 2 - 6 * S, 250 * S - (bb[1] + bb[3]) / 2), 'DIDI', f, lambda b: R.vgrad(W, H, b, R.CHROME), stroke=6 * S, stroke_fill=(0, 0, 0), glow_col=(120, 255, 60), glow_r=14, shear=.2)
# FOOTBALL
d = ImageDraw.Draw(img); f = R.font('k', 54); t = 'FOOTBALL'; tw = d.textlength(t, font=f); bb = d.textbbox((0, 0), t, font=f)
R.italic_text(img, (C - tw / 2, 352 * S - (bb[1] + bb[3]) / 2), t, f, lambda b: R.vgrad(W, H, b, [(0, (215, 255, 120)), (1, (120, 220, 30))]), stroke=4 * S, stroke_fill=(0, 0, 0), shear=.2)
out = os.path.join(R.BASE, 'assets', 'avatar.jpg'); img.convert('RGB').save(out, quality=94); print(out)
