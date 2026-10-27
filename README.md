# didi-cards

DIDI Football: картки результатів ставок для Telegram-каналу @didi_football_tips.

Як це працює щоночі:
1. n8n (бот «Football · щоденний огляд 12:00 Київ») після підрахунку ставок о 01:30 Київ кладе заготовку дня в таблицю `didi_card_specs`.
2. Нічне завдання Claude о ~02:05 Київ бере заготовку, запускає `python3 cards.py spec.json` і комітить картинки в `cards/<дата>/` та `cards/latest.json`.
3. n8n-процес «DIDI · картки в канал» о 02:40 Київ читає `cards/latest.json` і публікує картки альбомом у канал.

Ставки на картках умовні (100 €), без справжніх грошей. Емблем клубів немає — коди й кольори клубів.
Шрифт Inter (SIL Open Font License), див. `fonts/LICENSE-Inter.txt`.
