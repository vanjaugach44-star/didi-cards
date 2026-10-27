# DIDI result cards: renders one night's settled bets onto the DIDI template.
# Usage: python3 cards.py SPEC.json
#   SPEC.json = {"spec": "<the spec string from n8n table didi_card_specs>", "hash": "<hex>"}
# Writes cards/<date>/NN.jpg and cards/latest.json (read by the n8n workflow "DIDI · картки в канал").
import os, sys, json, hashlib, colorsys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_lib as R

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = 'https://raw.githubusercontent.com/vanjaugach44-star/didi-cards/main/'

# Club codes (TV-scoreboard style) and colours: (code, primary, secondary). No club logos are used.
W, B, K, RD, Y, BL, SK, GR, CL = (255, 255, 255), (20, 40, 110), (25, 25, 25), (210, 20, 40), (255, 210, 0), (30, 80, 200), (100, 170, 230), (20, 140, 70), (120, 20, 50)
CLUBS = {
 'Арсенал': ('АРС', RD, W), 'Астон Вілла': ('АВЛ', CL, SK), 'Борнмут': ('БОР', RD, K), 'Брентфорд': ('БРЕ', RD, W), 'Брайтон': ('БРА', BL, W),
 'Бернлі': ('БЕР', CL, SK), 'Челсі': ('ЧЕЛ', BL, W), 'Крістал Пелас': ('КПЛ', BL, RD), 'Евертон': ('ЕВЕ', B, W), 'Фулгем': ('ФУЛ', W, K),
 'Лідс': ('ЛІД', W, Y), 'Ліверпуль': ('ЛІВ', RD, W), 'Манчестер Сіті': ('МСІ', SK, W), 'Манчестер Юнайтед': ('МЮН', RD, K), 'Ньюкасл': ('НЬЮ', K, W),
 'Ноттінгем Форест': ('НОТ', RD, W), 'Сандерленд': ('САН', RD, W), 'Тоттенгем': ('ТОТ', W, B), 'Вест Гем': ('ВЕС', CL, SK), 'Вулвергемптон': ('ВУЛ', (250, 160, 0), K),
 'Реал Мадрид': ('РМА', W, (200, 160, 40)), 'Барселона': ('БАР', B, RD), 'Атлетіко Мадрид': ('АТЛ', RD, W), 'Атлетік Більбао': ('АТБ', RD, W), 'Реал Сосьєдад': ('РСО', BL, W),
 'Вільярреал': ('ВІЛ', Y, B), 'Бетіс': ('БЕТ', GR, W), 'Севілья': ('СЕВ', W, RD), 'Валенсія': ('ВАЛ', W, K), 'Сельта': ('СЕЛ', SK, RD), 'Осасуна': ('ОСА', RD, B),
 'Хетафе': ('ХЕТ', BL, W), 'Жирона': ('ЖИР', RD, W), 'Райо Вальєкано': ('РАЙ', W, RD), 'Мальорка': ('МАЛ', RD, K), 'Алавес': ('АЛА', BL, W), 'Еспаньол': ('ЕСП', BL, W),
 'Інтер': ('ІНТ', B, K), 'Мілан': ('МІЛ', RD, K), 'Ювентус': ('ЮВЕ', W, K), 'Наполі': ('НАП', SK, W), 'Рома': ('РОМ', CL, Y), 'Лаціо': ('ЛАЦ', SK, W),
 'Аталанта': ('АТА', B, K), 'Фіорентина': ('ФІО', (110, 40, 160), W), 'Болонья': ('БОЛ', RD, B), 'Торіно': ('ТОР', CL, W), 'Комо': ('КОМ', BL, W), 'Кальярі': ('КАЛ', RD, B),
 'Удінезе': ('УДІ', W, K), 'Дженоа': ('ДЖЕ', RD, B), 'Лечче': ('ЛЕЧ', Y, RD), 'Парма': ('ПАР', Y, B), 'Сассуоло': ('САС', GR, K), 'Верона': ('ВЕР', B, Y),
 'Баварія': ('БАВ', RD, W), 'Боруссія Дортмунд': ('БВБ', Y, K), 'Баєр Леверкузен': ('Б04', RD, K), 'Лейпциг': ('РБЛ', W, RD), 'Айнтрахт Франкфурт': ('СГЕ', K, RD),
 'Штутгарт': ('ШТУ', W, RD), 'Фрайбург': ('ФРА', RD, K), 'Вольфсбург': ('ВОЛ', GR, W), 'Боруссія Менхенгладбах': ('БМГ', K, GR), 'Вердер': ('ВЕР', GR, W),
 'Гоффенгайм': ('ГОФ', BL, W), 'Майнц': ('МАЙ', RD, W), 'Аугсбург': ('АУГ', RD, GR), 'Уніон Берлін': ('УНБ', RD, W), 'Гамбург': ('ГАМ', B, W), 'Кельн': ('КЕЛ', W, RD),
 'ПСЖ': ('ПСЖ', B, RD), 'Марсель': ('МАР', SK, W), 'Ліон': ('ЛІО', W, B), 'Монако': ('МОН', RD, W), 'Лілль': ('ЛІЛ', RD, B), 'Ніцца': ('НІЦ', RD, K), 'Ланс': ('ЛАН', Y, RD),
 'Ренн': ('РЕН', RD, K), 'Страсбург': ('СТР', BL, W), 'Нант': ('НАН', Y, GR), 'Тулуза': ('ТУЛ', (110, 40, 160), W), 'Брест': ('БРС', RD, W), 'Париж': ('ПФК', B, RD),
 'Бенфіка': ('БЕН', RD, W), 'Порту': ('ПОР', BL, W), 'Спортінг': ('СПО', GR, W), 'Брага': ('БРГ', RD, W), 'Віторія Гімарайнш': ('ВІТ', W, K), 'Санта-Клара': ('САН', RD, W),
 'Брюгге': ('БРЮ', BL, K), 'Юніон Сент-Жілуаз': ('ЮСЖ', Y, B), 'Андерлехт': ('АНД', (110, 40, 160), W), 'Генк': ('ГЕН', BL, W), 'Гент': ('ГНТ', BL, W),
 'Стандард Льєж': ('СТА', RD, W), 'Антверпен': ('АНТ', RD, W), 'Шахтар': ('ШАХ', (240, 120, 20), K), 'Динамо Київ': ('ДИН', W, BL), 'Аякс': ('АЯК', W, RD), 'ПСВ': ('ПСВ', RD, W),
 'Феєнорд': ('ФЕЄ', RD, W), 'Селтік': ('СЕЛ', GR, W), 'Рейнджерс': ('РЕЙ', BL, W), 'Галатасарай': ('ГАЛ', RD, Y), 'Фенербахче': ('ФЕН', B, Y),
 'Полісся': ('ПОЛ', GR, Y), 'Кривбас': ('КРИ', RD, W), 'Олександрія': ('ОЛЕ', Y, K), 'Карпати': ('КАР', GR, W), 'Зоря': ('ЗОР', K, W), 'Колос': ('КОЛ', Y, GR),
}

def club(name):
    if name in CLUBS: return CLUBS[name]
    letters = [c for c in name.upper() if c.isalpha()]
    code = ''.join(letters[:3]) or '???'
    h = int(hashlib.md5(name.encode('utf-8')).hexdigest()[:6], 16)
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, 0.75, 0.75)
    return (code, (int(r * 255), int(g * 255), int(b * 255)), W)

def djb2(s):
    h = 5381
    for ch in s: h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return format(h, 'x')

def main(path):
    box = json.load(open(path, encoding='utf-8'))
    spec_str, want = box['spec'], box['hash']
    got = djb2(spec_str)
    if got != want:
        sys.exit(f'Checksum mismatch: expected {want}, got {got}. The spec was not copied exactly.')
    spec = json.loads(spec_str)
    date = spec['date']; out_dir = os.path.join(BASE, 'cards', date); os.makedirs(out_dir, exist_ok=True)
    images = []
    for i, c in enumerate(spec['cards'], 1):
        legs = []
        for L in c['legs']:
            legs.append({**L, 'h': club(L['home']), 'a': club(L['away'])})
        e = {'date_long': c['date_long'], 'stake': c['stake'], 'total': c['total'], 'potential': c['potential'],
             'result': c['result'], 'status': c['status'] == 'won', 'legs': legs}
        name = f'{i:02d}-{c["kind"]}.jpg'
        R.render(e, os.path.join(out_dir, name))
        images.append(RAW + f'cards/{date}/{name}')
    d = date.split('-'); won = sum(c['status'] == 'won' for c in spec['cards'])
    caption = f'📊 Результати DIDI за {d[2]}.{d[1]}: {won} з {len(spec["cards"])} зайшло\n<i>Умовні ставки по 100 € · уся статистика без вибірок</i>'
    json.dump({'date': date, 'images': images, 'caption': caption}, open(os.path.join(BASE, 'cards', 'latest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(images)} cards for {date} written to {out_dir}')

if __name__ == '__main__':
    main(sys.argv[1])
