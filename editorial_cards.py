"""Compact match, daily and model-comparison cards in the DIDI visual family."""
from PIL import Image, ImageDraw
import render_lib as R
from club_logos import draw_logo

P = R.P
WIDTH, HEIGHT = 853, 1100


def text(img, label, x, y, size=24, color=R.WHITE, width=760, kind='b', center=False):
    d = ImageDraw.Draw(img)
    f, bb = R.fit_font(d, str(label), P(width), P(size+5), kind, size)
    xx = P(x) - d.textlength(str(label), font=f)/2 if center else P(x)
    d.text((xx, P(y)-bb[1]), str(label), font=f, fill=color)


def base(title, subtitle):
    img = Image.new('RGBA', (P(WIDTH), P(HEIGHT)), (7, 13, 17, 255))
    with Image.open(R.TPL) as src:
        header = src.convert('RGBA').resize((P(853), P(1280)), Image.Resampling.LANCZOS)
    img.alpha_composite(header.crop((0, 0, P(853), P(190))))
    R.ua_subtitle(img)
    text(img, title, 36, 218, 37, R.LIME, kind='k')
    text(img, subtitle, 36, 274, 20, R.MUTED)
    ImageDraw.Draw(img).line((P(36), P(315), P(817), P(315)), fill=(178,255,46,100), width=P(1))
    return img


def footer(img, note):
    R.rrect(img, [P(24),P(990),P(829),P(1078)],P(12),(17,27,31,255),(178,255,46,100),P(1))
    text(img, note, 426.5, 1008, 18, width=755, center=True)
    text(img, '@didi_football_tips · Статистика без прикрас · 18+',426.5,1044,16,R.MUTED,center=True)


def save(img, path):
    img.convert('RGB').save(path, quality=95)


def render_single(e, path):
    L = e['legs'][0]
    img = base('РЕЗУЛЬТАТ МАТЧУ', e['date_long'])
    R.flag(ImageDraw.Draw(img),P(36),P(337),L['flag'])
    text(img,L['league'],84,340,17)
    for cx, side, name, url in [(248,'h',L['home'],L.get('home_logo')),(605,'a',L['away'],L.get('away_logo'))]:
        if not draw_logo(img,P(cx),P(442),P(125),url):
            b=L[side]; R.badge(img,P(cx),P(442),P(52),b[1],b[2],b[3])
        text(img,name,cx,528,27,width=325,center=True,kind='x')
    text(img,L['score'],426.5,592,76,width=750,center=True,kind='k')
    text(img,L['time'],426.5,690,18,R.MUTED,center=True)
    R.rrect(img,[P(36),P(738),P(817),P(832)],P(12),(18,29,33,255))
    text(img,L['mtype'],58,755,17,R.MUTED,width=500)
    text(img,L['market'],58,787,27,width=480)
    R.rrect(img,[P(586),P(748),P(806),P(820)],P(8),(18,29,33,255))
    text(img,'КФ '+L['odds'],696,772,29,R.LIME,width=200,center=True)
    won=e['status'] is True; color=R.GREEN if won else R.RED
    R.rrect(img,[P(36),P(862),P(817),P(954)],P(12),(13,30,23,255) if won else (38,17,22,255),color+(160,),P(1))
    text(img,'ВИГРАШ' if won else 'ПРОГРАШ',58,892,27,color,width=360)
    text(img,e['result'],670,882,45,color,width=250,center=True,kind='k')
    footer(img,'СТАВКА НА МАТЧ · '+e['stake'])
    save(img,path)


def render_daily(data,path):
    img=base('ПІДСУМКИ ДНЯ',data['date']+' · Основна модель · Ординари')
    for i,(label,value) in enumerate([('ЗІГРАЛО',data['won']),('РЕЗУЛЬТАТ',data['profit']),('СТАВОК',data['count'])]):
        x=36+i*264
        R.rrect(img,[P(x),P(350),P(x+250),P(505)],P(12),(18,29,33,255))
        text(img,label,x+18,375,17,R.MUTED,width=215)
        text(img,value,x+18,421,39,R.LIME,width=215,kind='k')
    text(img,'РЕЗУЛЬТАТИ МАТЧІВ',36,552,20,R.MUTED)
    for i,row in enumerate(data['rows']):
        y=601+i*105
        R.rrect(img,[P(36),P(y),P(817),P(y+88)],P(10),(14,23,28,255))
        text(img,row['teams'],54,y+16,24,width=580)
        text(img,row['score'],54,y+52,18,R.MUTED,width=580)
        text(img,row['profit'],715,y+29,28,R.GREEN if row['positive'] else R.RED,width=160,center=True)
    footer(img,'РЕЗУЛЬТАТ СТАВОК · 1 ОД. = ОДНАКОВА СТАВКА')
    save(img,path)


def render_models(data,path):
    img=base('ПОРІВНЯННЯ МОДЕЛЕЙ',data['period'])
    for i,m in enumerate(data['models']):
        y=350+i*200
        R.rrect(img,[P(36),P(y),P(817),P(y+176)],P(14),(18,29,33,255))
        text(img,m['name'],58,y+22,27,R.WHITE,width=725)
        for x,label,value in [(58,'ЗІГРАЛО',m['record']),(320,'РЕЗУЛЬТАТ',m['profit']),(610,'ROI',m['roi'])]:
            text(img,label,x,y+77,16,R.MUTED,width=230)
            text(img,value,x,y+112,32,R.LIME,width=230,kind='k')
    footer(img,'РІЗНА КІЛЬКІСТЬ ПРОГНОЗІВ У МОДЕЛЕЙ')
    save(img,path)
