"""DIDI «МАТЧІ ДНЯ»: one picture with today's top matches (ESPN schedule), grouped by tournament.

Usage: python3 matches.py [YYYY-MM-DD] [--from-json FILE]
Writes matches/<date>.jpg and matches/latest.json (read by the n8n workflow «DIDI · матчі дня в канал»).
--from-json renders a saved list instead of calling ESPN (for tests).
"""
import hashlib, io, json, math, os, re, sys, unicodedata, colorsys
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_lib as R
from team_names_uk import DICT

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = 'https://raw.githubusercontent.com/vanjaugach44-star/didi-cards/main/'
KYIV = ZoneInfo('Europe/Kyiv')
P = R.P
MAX_MATCHES = 16

# ESPN code, flag, label, priority
LEAGUES = [
    ('uefa.champions', 'EU', 'ЛІГА ЧЕМПІОНІВ', 100), ('uefa.europa', 'EU', 'ЛІГА ЄВРОПИ', 90),
    ('eng.1', 'EN', 'АНГЛІЯ · АПЛ', 86), ('esp.1', 'ES', 'ІСПАНІЯ · ЛА ЛІГА', 85), ('ita.1', 'IT', 'ІТАЛІЯ · СЕРІЯ A', 84),
    ('ger.1', 'DE', 'НІМЕЧЧИНА · БУНДЕСЛІГА', 83), ('fra.1', 'FR', 'ФРАНЦІЯ · ЛІГА 1', 79), ('ukr.1', 'UA', 'УКРАЇНА · УПЛ', 78),
    ('uefa.europa.conf', 'EU', 'ЛІГА КОНФЕРЕНЦІЙ', 76),
    ('eng.league_cup', 'EN', 'АНГЛІЯ · КУБОК ЛІГИ', 75), ('eng.fa', 'EN', 'АНГЛІЯ · КУБОК АНГЛІЇ', 74),
    ('ger.dfb_pokal', 'DE', 'НІМЕЧЧИНА · КУБОК НІМЕЧЧИНИ', 74), ('ita.coppa_italia', 'IT', 'ІТАЛІЯ · КУБОК ІТАЛІЇ', 73),
    ('esp.copa_del_rey', 'ES', 'ІСПАНІЯ · КУБОК КОРОЛЯ', 73), ('por.1', 'PT', 'ПОРТУГАЛІЯ · ПРІМЕЙРА', 66),
    ('ned.1', 'NL', 'НІДЕРЛАНДИ · ЕРЕДИВІЗІ', 63), ('bel.1', 'BE', 'БЕЛЬГІЯ · ПРО-ЛІГА', 61),
]
BIG = {'Реал Мадрид', 'Барселона', 'Атлетіко Мадрид', 'Манчестер Сіті', 'Ліверпуль', 'Арсенал', 'Челсі', 'Манчестер Юнайтед',
       'Тоттенгем', 'Ньюкасл', 'Баварія', 'Боруссія Дортмунд', 'Баєр Леверкузен', 'ПСЖ', 'Інтер', 'Мілан', 'Ювентус', 'Наполі',
       'Рома', 'Аталанта', 'Бенфіка', 'Порту', 'Спортінг', 'Шахтар', 'Динамо Київ', 'Марсель', 'Аякс', 'ПСВ'}
MONTHS = ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']
DAYS = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П’ятниця', 'Субота', 'Неділя']

# ---- team names -------------------------------------------------------------
STRIP = {'fc', 'cf', 'afc', 'ac', 'sc', 'fk', 'sk', 'tc', 'nk', 'kf', 'cd', 'ud', 'sd', 'rc', 'rcd', 'as', 'ssc', 'sv', 'vfl', 'vfb', 'tsg',
         'fsv', 'ogc', 'losc', 'bk', 'if', 'ff', 'kv', 'krc', 'kaa', 'bsc', 'sl', 'hnk', 'gnk'}

def norm(v):
    s = unicodedata.normalize('NFD', str(v or ''))
    s = ''.join(ch for ch in s if not unicodedata.combining(ch)).lower().replace('ø', 'o').replace('æ', 'ae').replace('ł', 'l').replace('ı', 'i')
    return ''.join(w for w in re.split(r'[^a-z0-9]+', s) if w and w not in STRIP and not w.isdigit())

MAP = {}
for line in DICT.strip().split('\n'):
    if '=' not in line: continue
    uk, rest = line.split('=', 1)
    for a in rest.split(';'):
        if norm(a): MAP.setdefault(norm(a), uk.strip())

PRE = {'č': 'ч', 'ć': 'ч', 'š': 'ш', 'ž': 'ж', 'đ': 'дж', 'ş': 'ш', 'ç': 'ч', 'ğ': 'г', 'ı': 'і', 'ø': 'е', 'æ': 'е', 'å': 'о', 'ä': 'е', 'ö': 'е',
       'ü': 'ю', 'ñ': 'нь', 'ł': 'л', 'ń': 'нь', 'ś': 'ш', 'ź': 'ж', 'ż': 'ж', 'ř': 'рж', 'ě': 'е', 'ů': 'у', 'ý': 'і', 'á': 'а', 'é': 'е',
       'í': 'і', 'ó': 'о', 'ú': 'у', 'à': 'а', 'è': 'е', 'ì': 'і', 'ò': 'о', 'ù': 'у', 'â': 'а', 'ê': 'е', 'î': 'і', 'ô': 'о', 'û': 'у', 'ã': 'ан',
       'õ': 'он', 'ő': 'е', 'ű': 'ю', 'ë': 'е', 'ï': 'і'}
DI = [('shch', 'щ'), ('sch', 'ш'), ('sh', 'ш'), ('ch', 'ч'), ('zh', 'ж'), ('kh', 'х'), ('ts', 'ц'), ('tz', 'ц'), ('ya', 'я'), ('yu', 'ю'),
      ('ye', 'є'), ('yo', 'йо'), ('ou', 'у'), ('oo', 'у'), ('ee', 'і'), ('th', 'т'), ('ph', 'ф'), ('ck', 'к'), ('qu', 'кв'), ('gh', 'г')]
ONE = dict(zip('abcdefghijklmnopqrstuvwxyz', ['а', 'б', 'к', 'д', 'е', 'ф', 'г', 'х', 'і', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'к', 'р', 'с', 'т', 'у', 'в', 'в', 'кс', 'і', 'з']))

def translit(name):
    out = []
    for w in str(name).split():
        if w.lower().replace('.', '') in STRIP or re.fullmatch(r'\d+\.?', w): continue
        s = ''.join(PRE.get(ch, ch) for ch in w.lower()); r = ''; i = 0
        while i < len(s):
            for a, b in DI:
                if s.startswith(a, i): r += b; i += len(a); break
            else:
                c = s[i]
                if c == 'c' and i + 1 < len(s) and s[i + 1] in 'eiy': r += 'ц'
                else: r += ONE.get(c, c)
                i += 1
        out.append(r[:1].upper() + r[1:])
    return ' '.join(out) or str(name)

def uk_name(team):
    for k in ('displayName', 'shortDisplayName', 'name'):
        v = team.get(k)
        if v and norm(v) in MAP: return MAP[norm(v)]
    return translit(team.get('displayName') or team.get('name') or '?')

# ---- data --------------------------------------------------------------------
def fetch(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 DIDI-Football/1.0'})
    with urlopen(req, timeout=20) as r: return json.loads(r.read().decode('utf-8'))

def collect(date):
    out = []
    for code, flag, label, prio in LEAGUES:
        try: data = fetch(f'https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={date.replace("-", "")}')
        except Exception as e:
            print('skip', code, type(e).__name__, file=sys.stderr); continue
        for ev in data.get('events', []):
            comp = (ev.get('competitions') or [{}])[0]
            ko = datetime.fromisoformat(ev['date'].replace('Z', '+00:00')).astimezone(KYIV)
            if ko.strftime('%Y-%m-%d') != date: continue
            if (ev.get('status', {}).get('type', {}).get('state')) == 'post': continue
            cs = comp.get('competitors') or []
            h = next((c for c in cs if c.get('homeAway') == 'home'), None); a = next((c for c in cs if c.get('homeAway') == 'away'), None)
            if not h or not a: continue
            out.append({'league': code, 'flag': flag, 'label': label, 'prio': prio, 'time': ko.strftime('%H:%M'), 'ts': ko.timestamp(),
                        'home': uk_name(h['team']), 'away': uk_name(a['team']), 'home_logo': h['team'].get('logo'), 'away_logo': a['team'].get('logo')})
    return out

def pick(matches):
    for m in matches: m['score'] = m['prio'] + 15 * sum(x in BIG for x in (m['home'], m['away']))
    top = sorted(matches, key=lambda m: -m['score'])[:MAX_MATCHES]
    order = {c: i for i, (c, *_r) in enumerate(LEAGUES)}
    return sorted(top, key=lambda m: (min(x['ts'] for x in top if x['league'] == m['league']), order[m['league']], m['ts']))

# ---- logos --------------------------------------------------------------------
CACHE = os.path.join(BASE, 'assets', 'club_logos')

def logo(url):
    if not isinstance(url, str): return None
    p = urlparse(url)
    if p.scheme != 'https' or p.netloc not in ('a.espncdn.com', 'media.api-sports.io'): return None
    path = os.path.join(CACHE, hashlib.sha256(url.encode()).hexdigest() + '.png')
    try:
        if os.path.isfile(path):
            with Image.open(path) as im: return im.convert('RGBA')
        with urlopen(Request(url, headers={'User-Agent': 'DIDI-Football/1.0'}), timeout=8) as r: data = r.read(2_000_001)
        if len(data) > 2_000_000: return None
        with Image.open(io.BytesIO(data)) as src: im = src.convert('RGBA')
        box = im.getbbox()
        if not box: return None
        im = im.crop(box); os.makedirs(CACHE, exist_ok=True); im.save(path); return im
    except Exception:
        return None

def badge_colors(name):
    h = int(hashlib.md5(name.encode('utf-8')).hexdigest()[:6], 16)
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, 0.7, 0.75)
    return (int(r * 255), int(g * 255), int(b * 255)), (255, 255, 255)

def put_logo(img, cx, cy, size, url, name):
    im = logo(url)
    if im is not None:
        im = ImageOps.contain(im, (int(size), int(size)), Image.Resampling.LANCZOS)
        img.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2))); return
    try:
        from cards import club
        _, c1, c2, style = club(name)
    except Exception:
        (c1, c2), style = badge_colors(name), 'solid'
    R.badge(img, cx, cy, size * 0.42, c1, c2, style)

# ---- drawing ------------------------------------------------------------------
W = 853

def mini_ball(img, cx, cy, r):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(235, 240, 235), outline=(178, 255, 46), width=int(P(1.2)))
    pts = [(cx + r * .42 * math.cos(-math.pi / 2 + k * 2 * math.pi / 5), cy + r * .42 * math.sin(-math.pi / 2 + k * 2 * math.pi / 5)) for k in range(5)]
    d.polygon(pts, fill=(20, 26, 22))

def txt(img, s, x, y, size, color, kind='b', anchor='l', maxw=None):
    d = ImageDraw.Draw(img)
    f, bb = R.fit_font(d, s, P(maxw or W), P(size + 6), kind, size)
    tw = d.textlength(s, font=f)
    xx = P(x) - (tw if anchor == 'r' else tw / 2 if anchor == 'c' else 0)
    d.text((xx, P(y) - (bb[1] + bb[3]) / 2), s, font=f, fill=color)

def render(date, matches, out):
    groups = []
    for m in matches:
        if groups and groups[-1][0] == m['league']: groups[-1][1].append(m)
        else: groups.append((m['league'], [m]))
    HEAD_H, ROW, GH, GAP = 330, 58, 46, 18
    body = sum(GH + len(g) * ROW + GAP for _, g in groups)
    H = HEAD_H + body + 120
    img = Image.new('RGBA', (P(W), P(H)), (7, 13, 17, 255))
    with Image.open(R.TPL) as src: header = src.convert('RGBA').resize((P(853), P(1280)), Image.Resampling.LANCZOS)
    img.alpha_composite(header.crop((0, 0, P(853), P(190))))
    R.ua_subtitle(img)
    dt = datetime.strptime(date, '%Y-%m-%d')
    title_font = R.font('kd', 74)
    R.italic_text(img, (P(36), P(200)), 'МАТЧІ ДНЯ', title_font, lambda bb: R.vgrad(*img.size, bb, [(0, (210, 255, 120)), (1, (150, 235, 30))]),
                  stroke=P(2), glow_col=(150, 255, 40), glow_r=14)
    txt(img, f'{dt.day} {MONTHS[dt.month - 1]} · {DAYS[dt.weekday()]} · час київський'.upper(), 38, 306, 19, R.MUTED, 's')
    y = HEAD_H
    for code, ms in groups:
        R.rrect(img, [P(24), P(y), P(829), P(y + GH - 6)], P(10), (20, 34, 30, 255), (178, 255, 46, 110), P(1))
        R.flag(ImageDraw.Draw(img), P(40), P(y + 8), ms[0]['flag'])
        txt(img, ms[0]['label'], 86, y + (GH - 6) / 2, 19, R.WHITE, 'x', maxw=600)
        mini_ball(img, P(806), P(y + (GH - 6) / 2), P(11))
        y += GH
        for i, m in enumerate(ms):
            if i % 2 == 0: R.rrect(img, [P(24), P(y), P(829), P(y + ROW - 4)], P(8), (14, 22, 26, 255))
            cy = y + (ROW - 4) / 2
            put_logo(img, P(62), P(cy), P(38), m.get('home_logo'), m['home'])
            txt(img, m['home'].upper(), 88, cy, 19, R.WHITE, 'x', maxw=255)
            R.rrect(img, [P(370), P(cy - 17), P(483), P(cy + 17)], P(9), (32, 120, 46, 255), (178, 255, 46, 200), P(1.2))
            txt(img, m['time'], 426.5, cy, 21, R.WHITE, 'k', anchor='c', maxw=100)
            txt(img, m['away'].upper(), 765, cy, 19, R.WHITE, 'x', anchor='r', maxw=255)
            put_logo(img, P(791), P(cy), P(38), m.get('away_logo'), m['away'])
            y += ROW
        y += GAP
    R.rrect(img, [P(24), P(y + 6), P(829), P(y + 96)], P(12), (17, 27, 31, 255), (178, 255, 46, 100), P(1))
    txt(img, 'ПРОГНОЗИ DIDI — ЩОДНЯ О 12:00', 426.5, y + 36, 20, R.LIME, 'x', anchor='c', maxw=760)
    txt(img, '@didi_football_tips · Статистика без прикрас · 18+', 426.5, y + 70, 16, R.MUTED, 'm', anchor='c', maxw=760)
    img.convert('RGB').save(out, quality=92)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    date = args[0] if args else datetime.now(KYIV).strftime('%Y-%m-%d')
    if '--from-json' in sys.argv:
        matches = json.load(open(sys.argv[sys.argv.index('--from-json') + 1], encoding='utf-8'))
    else:
        matches = collect(date)
    chosen = pick(matches)
    os.makedirs(os.path.join(BASE, 'matches'), exist_ok=True)
    meta = {'date': date, 'count': len(chosen), 'images': [], 'caption': ''}
    if chosen:
        name = f'matches/{date}.jpg'
        render(date, chosen, os.path.join(BASE, name))
        meta['images'] = [RAW + name]
        meta['caption'] = '⚽ <b>МАТЧІ НА СЬОГОДНІ</b> 🔥\n\nПрогнози DIDI — сьогодні о 12:00 ⏰ Хто що дивиться? Пиши в коментарях 👇'
    json.dump(meta, open(os.path.join(BASE, 'matches', 'latest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(chosen)} of {len(matches)} matches for {date}')

if __name__ == '__main__':
    main()
