# DIDI result cards: renders the night's settled bets onto the DIDI template.
# Usage: python3 cards.py SPEC.json OUT_DIR   (SPEC.json = {"spec": "<string from n8n>", "hash": "<hex>"})
import os, sys, json, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys

S = 2
BASE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(BASE, 'fonts') + '/'
def font(w, size): return ImageFont.truetype(F + {'b': 'Inter-Bold.otf', 'x': 'Inter-ExtraBold.otf', 'm': 'Inter-Medium.otf', 's': 'Inter-SemiBold.otf', 'k': 'Inter-Black.otf', 'kd': 'InterDisplay-Black.otf'}[w], int(size * S))
WHITE = (245, 250, 245); MUTED = (150, 172, 160); DARK = (6, 12, 9)
LIME = (190, 255, 60); GREEN = (60, 220, 120); RED = (255, 72, 72); GREY = (140, 150, 145)

def rrect(img, box, r, fill, outline=None, width=0):
    l = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(l).rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width); img.alpha_composite(l)

def glow(img, fn, radius, times=1):
    l = Image.new('RGBA', img.size, (0, 0, 0, 0)); fn(ImageDraw.Draw(l))
    g = l.filter(ImageFilter.GaussianBlur(radius * S))
    for _ in range(times): img.alpha_composite(g)
    img.alpha_composite(l)

def flag(d, x, y, code):
    w, h = 34 * S, 24 * S
    def vstripes(cols):
        for i, c in enumerate(cols): d.rectangle([x + i * w / len(cols), y, x + (i + 1) * w / len(cols), y + h], fill=c)
    def hstripes(cols):
        for i, c in enumerate(cols): d.rectangle([x, y + i * h / len(cols), x + w, y + (i + 1) * h / len(cols)], fill=c)
    if code == 'NL': hstripes([(174, 28, 40), (255, 255, 255), (33, 70, 139)])
    elif code == 'DE': hstripes([(0, 0, 0), (221, 0, 0), (255, 206, 0)])
    elif code == 'UA': hstripes([(0, 87, 183), (255, 215, 0)])
    elif code == 'FR': vstripes([(0, 85, 164), (255, 255, 255), (239, 65, 53)])
    elif code == 'IT': vstripes([(0, 146, 70), (255, 255, 255), (206, 43, 55)])
    elif code == 'BE': vstripes([(0, 0, 0), (253, 218, 36), (239, 51, 64)])
    elif code == 'ES':
        d.rectangle([x, y, x + w, y + h], fill=(198, 11, 30)); d.rectangle([x, y + h / 4, x + w, y + 3 * h / 4], fill=(255, 196, 0))
    elif code == 'PT':
        d.rectangle([x, y, x + w * .4, y + h], fill=(0, 102, 0)); d.rectangle([x + w * .4, y, x + w, y + h], fill=(255, 0, 0)); d.ellipse([x + w * .4 - 6 * S, y + h / 2 - 6 * S, x + w * .4 + 6 * S, y + h / 2 + 6 * S], fill=(255, 220, 0))
    elif code == 'EN':
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255)); d.rectangle([x + w / 2 - 3 * S, y, x + w / 2 + 3 * S, y + h], fill=(206, 17, 36)); d.rectangle([x, y + h / 2 - 3 * S, x + w, y + h / 2 + 3 * S], fill=(206, 17, 36))
    elif code == 'EU':
        d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
        for k in range(12):
            a = k * math.pi / 6; cx, cy = x + w / 2 + 7 * S * math.cos(a), y + h / 2 + 7 * S * math.sin(a)
            d.ellipse([cx - 1.4 * S, cy - 1.4 * S, cx + 1.4 * S, cy + 1.4 * S], fill=(255, 204, 0))
    else:
        d.rectangle([x, y, x + w, y + h], fill=(40, 120, 40))
    d.rectangle([x, y, x + w, y + h], outline=(255, 255, 255, 80), width=1 * S)

def shield_poly(cx, cy, r):
    import math
    pts = [(cx - r, cy - r * .95), (cx + r, cy - r * .95), (cx + r, cy + r * .1)]
    for k in range(1, 12):
        a = k / 12 * math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * .1 + r * 1.05 * math.sin(a)))
    pts.append((cx, cy + r * 1.15))
    for k in range(11, 0, -1):
        a = k / 12 * math.pi / 2
        pts.append((cx - r * math.cos(a), cy + r * .1 + r * 1.05 * math.sin(a)))
    pts.append((cx - r, cy + r * .1))
    return pts

def crest(d, cx, cy, r, t, c1, c2):
    # Shield in club colours with a diagonal band and initials (generic emblem, not a club logo).
    img = d._image
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).polygon(shield_poly(cx, cy - r * .08, r), fill=255)
    layer = Image.new('RGBA', img.size, c1 + (255,)); ld = ImageDraw.Draw(layer)
    ld.polygon([(cx - r * 1.4, cy + r * .9), (cx + r * .6, cy - r * 1.3), (cx + r * 1.4, cy - r * 1.3), (cx - r * .6, cy + r * 1.6)], fill=c2 + (255,))
    ld.rectangle([cx - r * 1.2, cy - r * 1.1, cx + r * 1.2, cy - r * .62], fill=tuple(max(0, v - 60) for v in c1) + (255,))
    img.paste(layer, (0, 0), m)
    d.line(shield_poly(cx, cy - r * .08, r) + [shield_poly(cx, cy - r * .08, r)[0]], fill=(255, 255, 255), width=int(2.5 * S), joint='curve')
    f = font('k', r / S * (0.62 if len(t) > 1 else 0.8)); tw = d.textlength(t, font=f); bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - tw / 2, cy - (bb[1] + bb[3]) / 2 + r * .08), t, font=f, fill=WHITE, stroke_width=int(3 * S), stroke_fill=(10, 14, 12))

def icon(d, cx, cy, r, ok):
    c = GREEN if ok is True else RED if ok is False else GREY
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=5 * S)
    if ok is True: d.line([cx - r * .45, cy + r * .02, cx - r * .1, cy + r * .38, cx + r * .5, cy - r * .35], fill=c, width=6 * S, joint='curve')
    elif ok is False:
        k = r * .38; d.line([cx - k, cy - k, cx + k, cy + k], fill=c, width=6 * S); d.line([cx - k, cy + k, cx + k, cy - k], fill=c, width=6 * S)
    else: d.line([cx, cy - r * .5, cx, cy, cx + r * .35, cy + r * .2], fill=c, width=5 * S)



LIME = (178, 255, 46); NEON = (120, 255, 60)

def layer(W, H): return Image.new('RGBA', (W, H), (0, 0, 0, 0))

def italic_text(img, xy, text, f, fill_fn, stroke=0, stroke_fill=(0, 0, 0), shear=0.18, glow_col=None, glow_r=18):
    W, H = img.size
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).text(xy, text, font=f, fill=255, stroke_width=stroke)
    inner = Image.new('L', (W, H), 0); ImageDraw.Draw(inner).text(xy, text, font=f, fill=255)
    bb = m.getbbox()
    if not bb: return
    cy = (bb[1] + bb[3]) / 2
    aff = (1, shear, -shear * cy, 0, 1, 0)
    m = m.transform((W, H), Image.AFFINE, aff, resample=Image.BICUBIC); inner = inner.transform((W, H), Image.AFFINE, aff, resample=Image.BICUBIC)
    if glow_col:
        g = Image.new('RGBA', (W, H), glow_col + (255,)); gl = layer(W, H); gl.paste(g, (0, 0), m)
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(glow_r * S)))
    if stroke:
        sl = layer(W, H); sl.paste(Image.new('RGBA', (W, H), stroke_fill + (255,)), (0, 0), m); img.alpha_composite(sl)
    fl = layer(W, H); fl.paste(fill_fn(bb), (0, 0), inner); img.alpha_composite(fl)

def vgrad(W, H, bb, stops):
    out = layer(W, H); d = ImageDraw.Draw(out); y0, y1 = bb[1], bb[3]
    for y in range(y0, y1 + 1):
        k = (y - y0) / max(1, y1 - y0)
        for i in range(len(stops) - 1):
            a, ca = stops[i]; b, cb = stops[i + 1]
            if a <= k <= b:
                t = (k - a) / max(1e-6, b - a); c = tuple(int(ca[j] + (cb[j] - ca[j]) * t) for j in range(3)); break
        d.line([0, y, W, y], fill=c + (255,))
    return out

CHROME = [(0, (255, 255, 255)), (.42, (225, 230, 228)), (.5, (130, 138, 135)), (.62, (205, 210, 208)), (1, (250, 252, 250))]

def ball(img, cx, cy, r):
    W, H = img.size
    gl = layer(W, H); ImageDraw.Draw(gl).ellipse([cx - r - 50 * S, cy - r - 50 * S, cx + r + 50 * S, cy + r + 50 * S], fill=NEON + (150,))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(55 * S)))
    b = layer(W, H); d = ImageDraw.Draw(b)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 236, 230, 255))
    def pent(px, py, rr, rot): return [(px + rr * math.cos(rot + k * 2 * math.pi / 5), py + rr * math.sin(rot + k * 2 * math.pi / 5)) for k in range(5)]
    d.polygon(pent(cx, cy, r * .33, -math.pi / 2), fill=LIME + (255,))
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        d.line([(cx + r * .33 * math.cos(a), cy + r * .33 * math.sin(a)), (cx + r * .62 * math.cos(a), cy + r * .62 * math.sin(a))], fill=(10, 12, 10, 255), width=4 * S)
        d.polygon(pent(cx + r * .86 * math.cos(a), cy + r * .86 * math.sin(a), r * .27, a), fill=(22, 26, 22, 255))
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    sh = layer(W, H); ImageDraw.Draw(sh).ellipse([cx - r * .1, cy, cx + r * 1.7, cy + r * 1.8], fill=(0, 0, 0, 170)); b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40 * S)))
    hl = layer(W, H); ImageDraw.Draw(hl).ellipse([cx - r * .75, cy - r * .8, cx - r * .1, cy - r * .3], fill=(255, 255, 255, 90)); b.alpha_composite(hl.filter(ImageFilter.GaussianBlur(20 * S)))
    out = layer(W, H); out.paste(b, (0, 0), mask); img.alpha_composite(out)
    t = 'DIDI'; f = font('k', 26); d2 = ImageDraw.Draw(img); tw = d2.textlength(t, font=f)
    d2.text((cx - tw / 2, cy - r * .02), t, font=f, fill=(10, 14, 10))

def crown(d, x, y, w, col):
    h = w * .6
    d.polygon([(x, y + h), (x, y + h * .25), (x + w * .28, y + h * .6), (x + w * .5, y), (x + w * .72, y + h * .6), (x + w, y + h * .25), (x + w, y + h)], fill=col)


TPL = os.path.join(BASE, 'assets', 'template.jpg')
# Base units = pixels of the 853-wide template; S=2 is the working scale.
BW = 853; HEAD = 340; FOOT = 1128
LIME = (178, 255, 46); GOLD = (255, 205, 40)

def P(v): return v * S
_rr = rrect
def rrect(img, box, r, fill, outline=None, width=0): _rr(img, box, r, fill, outline, int(round(width)))

def fit_font(d, text, w, h, kind='kd', start=90):
    s = start
    while s > 10:
        f = font(kind, s); bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= w and bb[3] - bb[1] <= h: return f, bb
        s -= 1
    return font(kind, 10), d.textbbox((0, 0), text, font=font(kind, 10))

def status_icon(d, cx, cy, r, ok, filled=False):
    c = GREEN if ok is True else RED if ok is False else GREY
    if filled:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c); col = (255, 255, 255); w = int(r * .22)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=int(r * .14)); col = c; w = int(r * .16)
    if ok is True: d.line([cx - r * .45, cy + r * .02, cx - r * .1, cy + r * .38, cx + r * .5, cy - r * .35], fill=col, width=w, joint='curve')
    elif ok is False:
        k = r * .36; d.line([cx - k, cy - k, cx + k, cy + k], fill=col, width=w); d.line([cx - k, cy + k, cx + k, cy - k], fill=col, width=w)
    else: d.line([cx, cy - r * .5, cx, cy, cx + r * .35, cy + r * .2], fill=col, width=w)

def plate(img, x, y, w, h, code, c1, c2):
    rrect(img, [x, y, x + w, y + h], P(9), c1 + (255,), (255, 255, 255, 70), P(1.5))
    rrect(img, [x, y + h - P(9), x + w, y + h], P(4), c2 + (255,))
    d = ImageDraw.Draw(img); f, bb = fit_font(d, code, w - P(10), h - P(18), 'k', 22)
    tw = d.textlength(code, font=f)
    d.text((x + (w - tw) / 2, y + (h - P(9)) / 2 - (bb[1] + bb[3]) / 2), code, font=f, fill=(255, 255, 255), stroke_width=P(1.5), stroke_fill=(0, 0, 0))

def coins(d, x, y, col):
    for k in range(3): d.ellipse([x, y + P(14) - k * P(7), x + P(26), y + P(24) - k * P(7)], fill=col, outline=(90, 70, 0), width=int(P(1)))

def render(e, out):
    n = len(e['legs']); won = e['status'] is True; ACC = LIME if won else RED
    RH, GAP = 136, 10
    mid_h = 8 + n * (RH + GAP) + 210
    H = HEAD + mid_h + (1280 - FOOT)
    W = P(BW); img = Image.new('RGBA', (W, P(H)), (3, 6, 6, 255))
    tpl = Image.open(TPL).convert('RGBA').resize((W, P(1280)), Image.LANCZOS)
    img.alpha_composite(tpl.crop((0, 0, W, P(HEAD))), (0, 0))
    # middle background: dark with soft side glows
    g = layer(W, P(H)); gd = ImageDraw.Draw(g)
    gd.ellipse([-P(250), P(HEAD + 40), P(180), P(HEAD + mid_h)], fill=(90, 200, 30, 60))
    gd.ellipse([W - P(160), P(HEAD + 120), W + P(260), P(HEAD + mid_h - 40)], fill=(30, 110, 200, 40))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(P(70))))
    img.alpha_composite(tpl.crop((0, P(FOOT), W, P(1280))), (0, P(HEAD + mid_h)))
    d = ImageDraw.Draw(img)
    # title: repaint the inside of the frame and write the Ukrainian title in chrome
    rrect(img, [P(44), P(203), P(546), P(273)], P(10), (7, 11, 8, 255))
    TITLE = 'ОРДИНАР' if n == 1 else 'ЕКСПРЕС'
    d = ImageDraw.Draw(img); f, bb = fit_font(d, TITLE, P(440), P(66), 'kd', 90)
    tw = d.textlength(TITLE, font=f)
    italic_text(img, (P(295) - tw / 2, P(238) - (bb[1] + bb[3]) / 2), TITLE, f, lambda b: vgrad(W, P(H), b, CHROME), stroke=P(3), stroke_fill=(20, 28, 18), glow_col=(170, 255, 60), glow_r=5, shear=.2)
    d = ImageDraw.Draw(img)
    # chips: replace the text, keep the template's icons and frames
    word = 'ПОДІЯ' if n == 1 else 'ПОДІЇ' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 'ПОДІЙ'
    for (x0, x1, txt) in ((76, 188, f'{n} {word}'), (256, 405, e['date_long'].upper()), (471, 600, 'СТАВКА: ' + e['stake'])):
        bg = tpl.getpixel((P(x1 + 2), P(307)))[:3]
        pl = layer(W, P(H)); ImageDraw.Draw(pl).rounded_rectangle([P(x0), P(292), P(x1), P(322)], radius=P(6), fill=bg + (255,)); img.alpha_composite(pl.filter(ImageFilter.GaussianBlur(P(1.5))))
        d = ImageDraw.Draw(img)
        ff, bb = fit_font(d, txt, P(x1 - x0 - 4), P(20), 'b', 16)
        d.text((P(x0 + 2), P(307) - (bb[1] + bb[3]) / 2), txt, font=ff, fill=WHITE)
    # status badge
    gl = layer(W, P(H)); ImageDraw.Draw(gl).rounded_rectangle([P(621), P(266), P(822), P(331)], radius=P(12), outline=ACC + (255,), width=int(P(5)))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(P(6))))
    rrect(img, [P(621), P(266), P(822), P(331)], P(12), ((18, 50, 10) if won else (60, 6, 10)) + (255,), ACC + (255,), P(2))
    d = ImageDraw.Draw(img); status_icon(d, P(655), P(298.5), P(20), won, filled=True)
    lab = ('ЗАЙШЛО' if n == 1 else 'ЗАЙШОВ') if won else ('НЕ ЗАЙШЛО' if n == 1 else 'НЕ ЗАЙШОВ')
    ff, bb = fit_font(d, lab, P(128), P(24), 'k', 22); d.text((P(684), P(298.5) - (bb[1] + bb[3]) / 2), lab, font=ff, fill=ACC)
    # legs
    y = HEAD + 8
    for i, L in enumerate(e['legs']):
        st = L['ok']; c = GREEN if st is True else RED if st is False else GREY
        rrect(img, [P(16), P(y), P(837), P(y + RH)], P(12), (12, 16, 20, 240), (120, 130, 140, 90), P(1.5))
        rrect(img, [P(16), P(y), P(46), P(y + RH)], P(10), (32, 38, 44, 255))
        d = ImageDraw.Draw(img); f = font('k', 22); tw = d.textlength(str(i + 1), font=f); d.text((P(31) - tw / 2, P(y + RH / 2 - 15)), str(i + 1), font=f, fill=WHITE)
        flag(d, P(58), P(y + 10), L['flag'])
        d.text((P(98), P(y + 11)), L['league'], font=font('s', 12.5), fill=WHITE)
        plate(img, P(58), P(y + 46), P(72), P(52), L['h'][0], L['h'][1], L['h'][2])
        plate(img, P(140), P(y + 46), P(72), P(52), L['a'][0], L['a'][1], L['a'][2])
        d = ImageDraw.Draw(img)
        d.text((P(228), P(y + 40)), L['time'], font=font('m', 12.5), fill=(200, 205, 210))
        d.text((P(228), P(y + 62)), L['home'], font=font('x', 19), fill=WHITE)
        d.text((P(228), P(y + 90)), L['away'], font=font('x', 19), fill=WHITE)
        mx0, mx1 = 446, 690
        rrect(img, [P(mx0), P(y + 10), P(mx1), P(y + 70)], P(8), (8, 10, 14, 230), (120, 130, 140, 80), P(1.5))
        d = ImageDraw.Draw(img); d.text((P(mx0 + 12), P(y + 17)), L['mtype'], font=font('s', 12), fill=(220, 225, 230))
        d.text((P(mx0 + 12), P(y + 36)), L['market'], font=font('k', 19), fill=(255, 200, 40))
        rrect(img, [P(598), P(y + 16), P(682), P(y + 64)], P(7), LIME + (255,))
        d = ImageDraw.Draw(img); f = font('k', 21); tw = d.textlength(L['odds'], font=f); d.text((P(640) - tw / 2, P(y + 27)), L['odds'], font=f, fill=DARK)
        rrect(img, [P(500), P(y + 80), P(mx1), P(y + 122)], P(8), (8, 10, 14, 230), (120, 130, 140, 80), P(1.5))
        d = ImageDraw.Draw(img); f = font('b', 18); tw = d.textlength(L['score'], font=f); d.text((P(595) - tw / 2, P(y + 90)), L['score'], font=f, fill=WHITE)
        rrect(img, [P(702), P(y + 10), P(830), P(y + RH - 10)], P(10), (14, 18, 22, 255))
        gl = layer(W, P(H)); ImageDraw.Draw(gl).ellipse([P(740), P(y + 20), P(796), P(y + 76)], fill=c + (130,)); img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(P(10))))
        d = ImageDraw.Draw(img); status_icon(d, P(768), P(y + 48), P(24), st)
        lab = 'ВИГРАШ' if st is True else 'ПРОГРАШ' if st is False else 'ЧЕКАЄМО'
        f = font('k', 15); tw = d.textlength(lab, font=f); d.text((P(768) - tw / 2, P(y + 86)), lab, font=f, fill=c)
        y += RH + GAP
    # totals
    y += 0; th = 200
    rrect(img, [P(16), P(y), P(837), P(y + th)], P(14), (10, 14, 16, 240), (150, 200, 80, 110), P(1.5))
    d = ImageDraw.Draw(img); cw = (837 - 16) / 3
    labels = [('КОЕФІЦІЄНТ' if n == 1 else 'ЗАГАЛЬНИЙ КФ', e['total'], WHITE), ('СТАВКА', e['stake'], WHITE), ('МОЖЛИВИЙ ВИГРАШ', e['potential'], LIME)]
    for k, (lab, val, col) in enumerate(labels):
        x0 = 16 + cw * k + 18
        if k == 0:
            for j, hh in enumerate((10, 18, 26)): d.rectangle([P(x0 + j * 9), P(y + 46 - hh), P(x0 + j * 9 + 6), P(y + 46)], fill=GOLD)
        elif k == 1: coins(d, P(x0), P(y + 14), GOLD)
        else:
            d.ellipse([P(x0), P(y + 14), P(x0 + 32), P(y + 46)], fill=LIME); f = font('k', 20); d.text((P(x0 + 9), P(y + 17)), '€', font=f, fill=DARK)
        d.text((P(x0 + 44), P(y + 14)), lab, font=font('b', 12.5), fill=WHITE)
        d.text((P(x0 + 44), P(y + 32)), val, font=font('k', 27), fill=col)
        if k: d.line([P(16 + cw * k), P(y + 14), P(16 + cw * k), P(y + 74)], fill=(255, 255, 255, 60), width=int(P(1)))
    by = y + 92; bh = 92
    tint = (16, 60, 12) if won else (70, 6, 10)
    gl = layer(W, P(H)); ImageDraw.Draw(gl).rounded_rectangle([P(30), P(by), P(418), P(by + bh)], radius=P(10), fill=tint + (255,)); img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(P(4))))
    d = ImageDraw.Draw(img); d.text((P(48), P(by + 34)), 'ПІДСУМОК', font=font('k', 17), fill=(255, 220, 210) if not won else (220, 255, 200))
    ff, bb = fit_font(d, e['result'], P(250), P(56), 'kd', 60)
    def res(dd): dd.text((P(160), P(by + bh / 2) - (bb[1] + bb[3]) / 2), e['result'], font=ff, fill=ACC + (255,))
    glow(img, res, 10, 1)
    gl = layer(W, P(H)); ImageDraw.Draw(gl).rounded_rectangle([P(430), P(by), P(823), P(by + bh)], radius=P(10), outline=ACC + (255,), width=int(P(4))); img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(P(5))))
    rrect(img, [P(430), P(by), P(823), P(by + bh)], P(10), tint + (255,), ACC + (255,), P(2))
    d = ImageDraw.Draw(img); status_icon(d, P(482), P(by + bh / 2), P(28), won, filled=True)
    d.text((P(526), P(by + 16)), 'ОРДИНАР' if n == 1 else 'ЕКСПРЕС', font=font('k', 25), fill=ACC)
    d.text((P(526), P(by + 48)), lab if False else (('ЗАЙШЛО' if n == 1 else 'ЗАЙШОВ') if won else ('НЕ ЗАЙШЛО' if n == 1 else 'НЕ ЗАЙШОВ')), font=font('k', 25), fill=ACC)
    # footer: Ukrainian slogans and banner over the template's
    fy = HEAD + mid_h - FOOT  # offset of the footer in base units
    bg = tpl.getpixel((P(390), P(1150)))[:3]
    pl = layer(W, P(H)); ImageDraw.Draw(pl).rectangle([P(206), P(fy + 1158), P(382), P(fy + 1223)], fill=bg + (255,)); img.alpha_composite(pl.filter(ImageFilter.GaussianBlur(P(4))))
    d = ImageDraw.Draw(img)
    for k, s in enumerate(['СТАВ РОЗУМНО', 'СТЕЖ ЗА СТАТИСТИКОЮ', 'БУДЬ У ПЛЮСІ']): d.text((P(208), P(fy + 1162 + k * 20)), s, font=font('m', 13), fill=(225, 230, 235))
    bn = layer(W, P(H)); bd = ImageDraw.Draw(bn)
    bd.polygon([(P(522), P(fy + 1178)), (P(752), P(fy + 1146)), (P(760), P(fy + 1206)), (P(530), P(fy + 1236))], fill=(196, 240, 40, 255))
    img.alpha_composite(bn)
    tl = layer(W, P(H)); td = ImageDraw.Draw(tl); f = font('k', 17)
    for k, s in enumerate(['БІЛЬШЕ ПРОГНОЗІВ', 'У НАШОМУ КАНАЛІ']):
        tw = td.textlength(s, font=f); td.text((P(640) - tw / 2, P(fy + 1170 + k * 24)), s, font=f, fill=(12, 16, 10, 255))
    tl = tl.rotate(8, center=(P(640), P(fy + 1192)), resample=Image.BICUBIC)
    img.alpha_composite(tl)
    d = ImageDraw.Draw(img); d.text((P(26), P(fy + 1258)), 'Умовна ставка · статистика DIDI · 18+', font=font('m', 11), fill=(170, 180, 175))
    img.convert('RGB').save(out, quality=95)

