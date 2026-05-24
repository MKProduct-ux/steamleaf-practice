# -*- coding: utf-8 -*-

import asyncio
import os
import random
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SITE_URL = os.getenv("SITE_URL", "").strip()

if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN. Проверь файл .env")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

quiz_states: dict[int, dict[str, int]] = {}


# =========================
# КНОПКИ
# =========================

def button(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def url_button(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


def keyboard(rows: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("🎮 О чём наша игра", "about")],
        [button("👤 Главный герой", "hero")],
        [button("👥 Персонажи", "characters")],
        [button("🏙 Районы", "districts")],
        [button("🧾 Листовки", "leaflets")],
        [button("⭐ Что такое SR", "sr")],
        [button("🎲 Листовка дня", "leaflet_day")],
        [button("❓ Викторина", "quiz")],
        [button("🔮 Предсказание Лилит", "prediction")],
        [button("🌐 Сайт игры", "site")],
    ])


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("⬅️ В меню", "main")],
    ])


def characters_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("👵 Графиня Мокси", "char:moxy")],
        [button("🎻 Рэй", "char:ray")],
        [button("🔮 Лилит", "char:lilith")],
        [button("🤖 SP-67", "char:sp67")],
        [button("👔 Босс", "char:boss")],
        [button("🏠 Валера", "char:valera")],
        [button("🛒 Форшу", "char:forshu")],
        [button("🏥 Доктор Зуд", "char:doctor_zud")],
        [button("🚪 Консьержка", "char:concierge")],
        [button("⬅️ В меню", "main")],
    ])


def character_detail_keyboard(is_lilith: bool = False) -> InlineKeyboardMarkup:
    rows = []

    if is_lilith:
        rows.append([button("🔮 Получить предсказание", "prediction")])

    rows.extend([
        [button("⬅️ К персонажам", "characters")],
        [button("🏠 В меню", "main")],
    ])

    return keyboard(rows)


def districts_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("🏚 Трущобы", "district:slums")],
        [button("🏙 Средний район", "district:middle")],
        [button("🏛 Богатый район", "district:rich")],
        [button("👑 Элитный район", "district:elite")],
        [button("⬅️ В меню", "main")],
    ])


def district_detail_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("⬅️ К районам", "districts")],
        [button("🏠 В меню", "main")],
    ])


def leaflets_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("🛒 Двоечка", "leaflet:dvoechka")],
        [button("☕ Кофеточка", "leaflet:kofetochka")],
        [button("🎉 Закрытая зона", "leaflet:zakrytaya_zona")],
        [button("🦡 Барсук", "leaflet:barsuk")],
        [button("💈 Гараж", "leaflet:garage")],
        [button("🎲 Случайная листовка", "leaflet_day")],
        [button("❓ Пройти викторину", "quiz")],
        [button("⬅️ В меню", "main")],
    ])


def leaflet_detail_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("⬅️ К листовкам", "leaflets")],
        [button("🏠 В меню", "main")],
    ])


def leaflet_day_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("🎲 Ещё листовку", "leaflet_day")],
        [button("⬅️ В меню", "main")],
    ])


def quiz_start_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("✅ Начать викторину", "quiz_start")],
        [button("⬅️ В меню", "main")],
    ])


def quiz_answer_keyboard(question_index: int) -> InlineKeyboardMarkup:
    return keyboard([
        [button("🛒 Двоечка", f"quiz_answer:{question_index}:dvoechka")],
        [button("☕ Кофеточка", f"quiz_answer:{question_index}:kofetochka")],
        [button("🎉 Закрытая зона", f"quiz_answer:{question_index}:zakrytaya_zona")],
        [button("🦡 Барсук", f"quiz_answer:{question_index}:barsuk")],
        [button("💈 Гараж", f"quiz_answer:{question_index}:garage")],
    ])


def quiz_next_keyboard(is_last_question: bool) -> InlineKeyboardMarkup:
    text = "➡️ Завершить викторину" if is_last_question else "➡️ Следующий вопрос"

    return keyboard([
        [button(text, "quiz_next")],
    ])


def quiz_final_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("🔁 Пройти ещё раз", "quiz_start")],
        [button("⬅️ В меню", "main")],
    ])


def prediction_keyboard() -> InlineKeyboardMarkup:
    return keyboard([
        [button("🔮 Ещё предсказание", "prediction")],
        [button("⬅️ В меню", "main")],
    ])


def site_keyboard() -> InlineKeyboardMarkup:
    rows = []

    if SITE_URL:
        rows.append([url_button("🌐 Перейти на сайт", SITE_URL)])
    else:
        rows.append([button("🌐 Перейти на сайт", "site_no_link")])

    rows.append([button("⬅️ В меню", "main")])

    return keyboard(rows)


# =========================
# ТЕКСТЫ
# =========================

START_TEXT = """
⚙️ Терминал промоутера Steamleaf

Добро пожаловать, гражданин.

Вы подключились к промоутерскому терминалу STEAMLEAF — игры о юном промоутере, городских листовках, странных NPC, социальном рейтинге и городе, где обычная работа может привести к очень необычным историям.

Выберите раздел:
""".strip()


HELP_TEXT = """
ℹ️ Помощь

Терминал промоутера Steamleaf — это промоутерский терминал по игре STEAMLEAF.

С помощью бота можно:
— узнать, о чём наша игра;
— познакомиться с главным героем;
— посмотреть персонажей;
— узнать о районах города;
— изучить листовки;
— понять, что такое SR;
— получить случайную листовку дня;
— пройти викторину по листовкам;
— получить предсказание от Лилит;
— перейти на сайт игры.

Команды:
/start — открыть главное меню
/help — показать помощь

Чтобы вернуться назад, используйте кнопки «⬅️ В меню» или «⬅️ Назад».
""".strip()


ABOUT_TEXT = """
🎮 О чём наша игра?

STEAMLEAF — сюжетная игра с элементами RPG в стимпанк-социалистическом городе.

Главный герой — юноша 18 лет, который начинает свою первую работу промоутером. Его задача — раздавать городские листовки, общаться с прохожими, знакомиться с жителями города и постепенно повышать свой социальный рейтинг SR.

На первый взгляд это история про обычную работу. Но через листовки, диалоги и встречи с NPC игрок узнаёт о городе, его районах, роботах, богатых гражданах, бедных кварталах, странных правилах и системе социального рейтинга.

Главная идея игры — показать большой абсурдный мир через маленькую работу обычного промоутера.
""".strip()


HERO_TEXT = """
👤 Главный герой

Главному герою 18 лет. Он только закончил учёбу и устроился на свою первую работу — промоутером.

Он дружелюбный, общительный, задорный и немного саркастичный. Любит подкалывать, умеет выкручиваться из странных ситуаций и старается не терять чувство юмора даже тогда, когда рабочий день становится слишком странным.

Его работа — раздавать рекламные листовки разных заведений, магазинов и мест города. Через эти листовки герой знакомится с прохожими, запускает диалоги, попадает в необычные ситуации и постепенно узнаёт, как устроен мир STEAMLEAF.

На первый взгляд он просто выполняет обычную работу промоутера. Но каждая листовка может стать началом истории: привести к новому персонажу, странному поручению, конфликту или неожиданному выбору.
""".strip()


CHARACTERS_TEXT = """
👥 Персонажи STEAMLEAF

В игре есть сюжетные и фоновые персонажи. Каждый из них раскрывает мир со своей стороны: кто-то помогает герою, кто-то мешает, а кто-то просто делает рабочий день страннее.

Выберите персонажа:
""".strip()


DISTRICTS_TEXT = """
🏙 Районы города

Город в STEAMLEAF разделён на районы. Доступ к ним зависит от социального рейтинга SR.

Чем выше SR, тем больше возможностей, но тем сильнее контроль и ожидания общества.

Выберите район:
""".strip()


LEAFLETS_TEXT = """
🧾 Листовки

Листовки — главный инструмент промоутера.

Через них герой взаимодействует с NPC, запускает диалоги, получает реакции прохожих и узнаёт город.

В STEAMLEAF листовки не просто рекламируют товары и места. Они показывают жизнь города, его юмор, районы, заведения и социальную атмосферу.

Выберите листовку:
""".strip()


SR_TEXT = """
⭐ SR — социальный рейтинг

SR показывает положение гражданина в обществе.

Он влияет на:
— доступ к районам;
— отношение NPC;
— карьерные возможности;
— проверки полиции;
— доступ к некоторым возможностям города.

Чем выше SR, тем больше возможностей. Но не все способы повысить рейтинг одинаково приятны.

Шкала SR:
0–399 — низкий статус, трущобы
400–599 — гражданин, средний район
600–799 — привилегированный гражданин, богатый район
800–1000 — элита, закрытые места
""".strip()


SITE_TEXT = """
🌐 Сайт игры

На сайте STEAMLEAF можно узнать больше об игре: посмотреть описание мира, персонажей, районы, визуальный стиль, листовки и другие материалы проекта.

Сайт помогает быстро понять атмосферу игры и увидеть, как устроен мир, в котором работает главный герой.

Ссылка:
https://mkproduct-ux.github.io/steamleaf-practice/
""".strip()


QUIZ_INTRO_TEXT = """
❓ Викторина по листовкам

Проверим, насколько хорошо вы ориентируетесь в рекламе города.

За каждый правильный ответ вы получаете +5 SR.

Начинаем?
""".strip()


# =========================
# ПЕРСОНАЖИ
# =========================

CHARACTERS = {
    "moxy": {
        "image": "assets/characters/moxy.jpg",
        "text": """
👵 Графиня Мокси

Возраст: 104 года
SR: 900
Район: Элитный

Богатая пожилая дама, которая устраивает вечеринки для высшего общества.

Мокси считает, что жизнь нужна ради удовольствия, красивых приёмов и полезных знакомств. Она выглядит моложе своих лет и явно знает, как устроен мир богатых граждан.

Встреча с ней показывает герою, что в городе важны не только работа и старание, но и связи, статус и умение оказаться в нужном месте.
""".strip(),
    },
    "ray": {
        "image": "assets/characters/ray.jpg",
        "text": """
🎻 Рэй

Возраст: 27 лет
SR: 450
Район: Средний

Музыкант-киборг с рукой-протезом в виде музыкального инструмента.

Раньше он работал на фабрике, но после несчастного случая лишился прежней жизни. Теперь Рэй играет на улице и надеется добиться чего-то в музыке.

Его история показывает, что в мире STEAMLEAF технологии могут не только помогать, но и менять судьбу человека.
""".strip(),
    },
    "lilith": {
        "image": "assets/characters/lilith.jpg",
        "text": """
🔮 Лилит

Возраст: неизвестен
SR: неизвестен
Район: появляется в разных местах

Гадалка с металлическими картами.

Лилит говорит загадочно, любит театральность и иногда даёт странные предсказания. Её слова могут звучать как шутка, но иногда в них оказывается больше правды, чем хотелось бы.

Лилит может сделать вам предсказание прямо сейчас!
""".strip(),
    },
    "sp67": {
        "image": "assets/characters/sp67.jpg",
        "text": """
🤖 SP-67

Тип: надменный боевой робот
SR: государственный
Район: Средний

SP-67 — большой боевой робот с философским чипом.

Он смотрит на людей свысока и уверен, что роботы однажды заменят промоутеров, потому что выполняют работу качественнее.

Его диалоги подчёркивают конфликт между человеком, машиной и бессмысленной рутиной.
""".strip(),
    },
    "boss": {
        "image": "assets/characters/boss.jpg",
        "text": """
👔 Босс

Имя: Джем Дейвис Джон
Возраст: 42 года
SR: 700

Шумный, напыщенный и гиперактивный начальник.

Для него раздача листовок — не просто работа, а почти искусство. Он требует эффективности, громко мотивирует героя и относится к рабочему дню как к битве за светлое будущее.

Именно босс задаёт герою первые рабочие цели и постоянно напоминает, что хороший промоутер должен быть полезной шестерёнкой общества.
""".strip(),
    },
    "valera": {
        "image": "assets/characters/valera.jpg",
        "text": """
🏠 Валера

Возраст: 23 года
SR: 500
Район: Средний

Сосед главного героя.

Ленивый, весёлый, любит отлынивать от работы и жить сегодняшним днём. Валера не слишком верит в карьеру, высокий SR и светлое будущее.

Он часто предлагает сомнительные идеи, но из-за этого становится одним из самых живых и харизматичных персонажей.
""".strip(),
    },
    "forshu": {
        "image": "assets/characters/forshu.jpg",
        "text": """
🛒 Форшу

Возраст: 38 лет
SR: 560
Район: Средний

Продавец в магазине “Двоечка”.

Громкий, странный, язвительный и немного суетливый. Может поддеть покупателя, резко сменить тон и сделать даже обычную покупку частью абсурдного диалога.

Через Форшу раскрывается бытовая сторона мира STEAMLEAF.
""".strip(),
    },
    "doctor_zud": {
        "image": "assets/characters/doctor_zud.jpg",
        "text": """
🏥 Доктор Зуд

Возраст: 39 лет
SR: 527
Район: Средний

Врач с оптимизмом и чёрным юмором.

Доктор Зуд появляется в больничной линии игры. Он спокойно говорит о неприятных вещах и создаёт ощущение, что медицина в этом мире тоже работает по своим странным правилам.

С ним даже плохое самочувствие может превратиться в абсурдный диалог.
""".strip(),
    },
    "concierge": {
        "image": "assets/characters/concierge.jpg",
        "text": """
🚪 Консьержка

Возраст: 65 лет
SR: 500
Район: Средний

Консьержка знает всё обо всех.

Она ворчливая, наблюдательная, любит порядок и контроль. В подъезде от неё трудно что-то скрыть.

В игре она добавляет бытовой юмор и ощущение, что даже дом главного героя — часть большой социальной системы.
""".strip(),
    },
}


# =========================
# РАЙОНЫ
# =========================

DISTRICTS = {
    "slums": {
        "image": "assets/districts/slums.jpg",
        "text": """
🏚 Трущобы

SR: 0–399

Район бедных, безработных, преступников и тех, кто оказался на дне социальной системы.

Здесь выше преступность, больше странных заданий и меньше доверия. Граждане с высоким SR в трущобах могут вызывать подозрение.

Атмосфера: опасность, абсурд, выживание и сомнительные возможности.
""".strip(),
    },
    "middle": {
        "image": "assets/districts/middle.jpg",
        "text": """
🏙 Средний район

SR: 400–599

Стартовая зона игры.

Здесь живут обычные граждане, рабочие и офисные служащие. В среднем районе находятся дом главного героя, магазин “Двоечка”, офис, метро, улицы с прохожими и первые важные NPC.

Атмосфера: повседневность, рутина, работа и первые странные встречи.
""".strip(),
    },
    "rich": {
        "image": "assets/districts/rich.jpg",
        "text": """
🏛 Богатый район

SR: 600–799

Район успешных граждан, начальников, обеспеченных работников и людей с высоким положением.

Здесь чище, безопаснее и формальнее. NPC относятся к герою иначе, а обычная листовка может вызвать совсем не обычную реакцию.

Атмосфера: порядок, холодная вежливость, статус и скрытое напряжение.
""".strip(),
    },
    "elite": {
        "image": "assets/districts/elite.jpg",
        "text": """
👑 Элитный район

SR: 800–1000

Район политиков, VIP-гостей, богатейших граждан и закрытых мест.

Здесь находятся элитные клубы, дорогие дома и пространства, куда обычному гражданину попасть почти невозможно.

Атмосфера: роскошь, контроль, закрытость и ощущение, что за красивой витриной скрывается совсем другой мир.
""".strip(),
    },
}


# =========================
# ЛИСТОВКИ
# =========================

LEAFLETS = {
    "dvoechka": {
        "image": "assets/leaflets/dvoechka.jpg",
        "text": """
🛒 Двоечка

Одна из городских рекламных листовок и важный магазин в мире STEAMLEAF.

“Двоечка” показывает бытовую сторону города: скидки, продукты, странные акции и привычную рекламу, которую промоутер может раздавать прохожим.

Для одних NPC такая листовка — просто бумажка, для других — повод начать диалог.
""".strip(),
        "day_text": """
🛒 Двоечка

Свежие продукты, честные скидки и всё, что нужно гражданину для бодрого рабочего дня.

“Двоечка” — когда в корзине порядок, а в душе появляется надежда на ужин.

Комментарий босса:
“Вот это реклама! Учись, маленькая шестерёнка.”
""".strip(),
    },
    "kofetochka": {
        "image": "assets/leaflets/kofetochka.jpg",
        "text": """
☕ Кофеточка

Кофейня в стимпанк-городе.

Листовка “Кофеточки” показывает более уютную сторону мира: люди не только работают и повышают SR, но и пытаются отдыхать, пить кофе и делать вид, что всё нормально.

Настроение: пар, кофе, городская усталость и короткая пауза между рабочими днями.
""".strip(),
        "day_text": """
☕ Кофеточка

Кофе, пар и короткая пауза между обязанностями.

Комментарий героя:
“Иногда кажется, что этот город можно пережить только с кофе.”
""".strip(),
    },
    "zakrytaya_zona": {
        "image": "assets/leaflets/zakrytaya_zona.jpg",
        "text": """
🎉 Закрытая зона

Клуб в мире STEAMLEAF.

Листовка “Закрытой зоны” передаёт шумную и закрытую сторону города: вечеринки, музыка, вход по правилам и ощущение места, куда пускают не всех.

Это реклама клуба, где отдых может быть таким же странным, как и работа.
""".strip(),
        "day_text": """
🎉 Закрытая зона

Клуб, где отдых выглядит так, будто на него тоже нужен допуск.

Комментарий Валеры:
“Вот туда я бы пошёл. Вопрос только — помню ли я, как вернулся.”
""".strip(),
    },
    "barsuk": {
        "image": "assets/leaflets/barsuk.jpg",
        "text": """
🦡 Барсук

Бар с грубой и неформальной атмосферой.

“Барсук” выглядит как место, куда идут после полуночи, когда хорошие решения уже закончились.

Настроение: шум, сомнительные знакомства, дешёвое веселье и лёгкий риск.
""".strip(),
        "day_text": """
🦡 Барсук

Бар для тех, кто считает, что хорошие решения заканчиваются до полуночи.

Комментарий Лилит:
“Карты говорят: не все, кто вошёл в Барсук, вышли теми же людьми.”
""".strip(),
    },
    "garage": {
        "image": "assets/leaflets/garage.jpg",
        "text": """
💈 Гараж

Парикмахерская в мире STEAMLEAF.

Название звучит грубо и механически, но за ним скрывается место, где гражданину могут привести в порядок внешний вид.

Листовка “Гаража” хорошо подходит атмосфере игры: немного железа, немного городского юмора и обещание сделать человека презентабельнее перед новым рабочим днём.
""".strip(),
        "day_text": """
💈 Гараж

Парикмахерская для гражданина, который хочет выглядеть лучше, чем чувствует себя после рабочей смены.

Комментарий SP-67:
“Внешний вид человека требует регулярного технического обслуживания.”
""".strip(),
    },
}


# =========================
# ВИКТОРИНА
# =========================

QUIZ_QUESTIONS = [
    {
        "question": """
❓ Вопрос 1

Какая листовка связана с магазином, скидками и городской рекламой продуктов?
""".strip(),
        "correct": "dvoechka",
        "correct_text": """
✅ Верно!

“Двоечка” — это магазин и одна из городских рекламных листовок.

+5 SR
""".strip(),
        "wrong_text": """
❌ Не совсем.

Правильный ответ: “Двоечка”.

Она связана с магазином, товарами, скидками и городской рекламой.
""".strip(),
    },
    {
        "question": """
❓ Вопрос 2

Какая листовка связана с паром, теплом и короткой паузой между рабочими днями?
""".strip(),
        "correct": "kofetochka",
        "correct_text": """
✅ Верно!

“Кофеточка” — это кофейня в мире STEAMLEAF.

+5 SR
""".strip(),
        "wrong_text": """
❌ Не совсем.

Правильный ответ: “Кофеточка”.

Это кофейня, связанная с паром, теплом и короткой паузой между рабочими днями.
""".strip(),
    },
    {
        "question": """
❓ Вопрос 3

Какая листовка рекламирует клуб?
""".strip(),
        "correct": "zakrytaya_zona",
        "correct_text": """
✅ Верно!

“Закрытая зона” — это клуб.

+5 SR
""".strip(),
        "wrong_text": """
❌ Не совсем.

Правильный ответ: “Закрытая зона”.

Это клуб с закрытой, шумной и немного странной атмосферой.
""".strip(),
    },
    {
        "question": """
❓ Вопрос 4

Какая листовка больше всего подходит месту с сомнительными решениями после полуночи?
""".strip(),
        "correct": "barsuk",
        "correct_text": """
✅ Верно!

“Барсук” — это бар с неформальной атмосферой.

+5 SR
""".strip(),
        "wrong_text": """
❌ Не совсем.

Правильный ответ: “Барсук”.

Это бар, где хорошие решения обычно заканчиваются раньше вечера.
""".strip(),
    },
    {
        "question": """
❓ Вопрос 5

Какая листовка связана с парикмахерской?
""".strip(),
        "correct": "garage",
        "correct_text": """
✅ Верно!

“Гараж” — это парикмахерская.

+5 SR
""".strip(),
        "wrong_text": """
❌ Не совсем.

Правильный ответ: “Гараж”.

Несмотря на название, это парикмахерская в мире STEAMLEAF.
""".strip(),
    },
]


PREDICTIONS = [
    "Сегодня листовка найдёт того, кто не должен был её брать.",
    "Не спорь с роботом. Он всё равно произнесёт монолог длиннее твоей смены.",
    "Твой SR колеблется. Возможно, это судьба. Возможно, отчётность.",
    "Третий энергетик — это не ускорение. Это запись к доктору Зуду.",
    "Если прохожий отказался от листовки, значит, он ещё не понял своего счастья.",
    "Карты говорят: сегодня лучше не заходить в Барсук после полуночи.",
    "Босс следит за тобой. Даже когда не следит.",
    "Не всякая бумага — мусор. Иногда это начало истории.",
    "Клуб может открыть дверь. Но не факт, что тебе понравится, что за ней.",
    "Парикмахерская меняет причёску. Город меняет людей.",
]


# =========================
# ОТПРАВКА СООБЩЕНИЙ
# =========================

def image_exists(image_path: str) -> bool:
    return Path(image_path).is_file()


async def answer_text(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await message.answer(text, reply_markup=reply_markup)


async def edit_or_answer(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await callback.answer()

    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=reply_markup)


async def answer_image_page(
    callback: CallbackQuery,
    text: str,
    image_path: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await callback.answer()

    if image_exists(image_path):
        photo = FSInputFile(image_path)

        if len(text) <= 1000:
            await callback.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=reply_markup,
            )
        else:
            await callback.message.answer_photo(photo=photo)
            await callback.message.answer(text, reply_markup=reply_markup)
    else:
        await callback.message.answer(text, reply_markup=reply_markup)


# =========================
# КОМАНДЫ
# =========================

@dp.message(CommandStart())
async def start_command(message: Message) -> None:
    await answer_text(message, START_TEXT, main_menu_keyboard())


@dp.message(Command("help"))
async def help_command(message: Message) -> None:
    await answer_text(message, HELP_TEXT, back_to_main_keyboard())


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

@dp.callback_query(F.data == "main")
async def show_main_menu(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, START_TEXT, main_menu_keyboard())


@dp.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, ABOUT_TEXT, back_to_main_keyboard())


@dp.callback_query(F.data == "hero")
async def show_hero(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, HERO_TEXT, back_to_main_keyboard())


@dp.callback_query(F.data == "sr")
async def show_sr(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, SR_TEXT, back_to_main_keyboard())


@dp.callback_query(F.data == "site")
async def show_site(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, SITE_TEXT, site_keyboard())


@dp.callback_query(F.data == "site_no_link")
async def site_no_link(callback: CallbackQuery) -> None:
    await callback.answer("Ссылка на сайт будет добавлена позже.", show_alert=True)


# =========================
# ПЕРСОНАЖИ
# =========================

@dp.callback_query(F.data == "characters")
async def show_characters(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, CHARACTERS_TEXT, characters_keyboard())


@dp.callback_query(F.data.startswith("char:"))
async def show_character_detail(callback: CallbackQuery) -> None:
    character_key = callback.data.split(":", 1)[1]
    character = CHARACTERS.get(character_key)

    if not character:
        await callback.answer("Персонаж не найден.", show_alert=True)
        return

    await answer_image_page(
        callback=callback,
        text=character["text"],
        image_path=character["image"],
        reply_markup=character_detail_keyboard(is_lilith=(character_key == "lilith")),
    )


# =========================
# РАЙОНЫ
# =========================

@dp.callback_query(F.data == "districts")
async def show_districts(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, DISTRICTS_TEXT, districts_keyboard())


@dp.callback_query(F.data.startswith("district:"))
async def show_district_detail(callback: CallbackQuery) -> None:
    district_key = callback.data.split(":", 1)[1]
    district = DISTRICTS.get(district_key)

    if not district:
        await callback.answer("Район не найден.", show_alert=True)
        return

    await answer_image_page(
        callback=callback,
        text=district["text"],
        image_path=district["image"],
        reply_markup=district_detail_keyboard(),
    )


# =========================
# ЛИСТОВКИ
# =========================

@dp.callback_query(F.data == "leaflets")
async def show_leaflets(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, LEAFLETS_TEXT, leaflets_keyboard())


@dp.callback_query(F.data.startswith("leaflet:"))
async def show_leaflet_detail(callback: CallbackQuery) -> None:
    leaflet_key = callback.data.split(":", 1)[1]
    leaflet = LEAFLETS.get(leaflet_key)

    if not leaflet:
        await callback.answer("Листовка не найдена.", show_alert=True)
        return

    await answer_image_page(
        callback=callback,
        text=leaflet["text"],
        image_path=leaflet["image"],
        reply_markup=leaflet_detail_keyboard(),
    )


@dp.callback_query(F.data == "leaflet_day")
async def show_leaflet_day(callback: CallbackQuery) -> None:
    leaflet_key = random.choice(list(LEAFLETS.keys()))
    leaflet = LEAFLETS[leaflet_key]

    text = f"""
🎲 Листовка дня

Сегодня город рекомендует:

{leaflet["day_text"]}
""".strip()

    await answer_image_page(
        callback=callback,
        text=text,
        image_path=leaflet["image"],
        reply_markup=leaflet_day_keyboard(),
    )


# =========================
# ВИКТОРИНА
# =========================

@dp.callback_query(F.data == "quiz")
async def show_quiz_intro(callback: CallbackQuery) -> None:
    await edit_or_answer(callback, QUIZ_INTRO_TEXT, quiz_start_keyboard())


@dp.callback_query(F.data == "quiz_start")
async def start_quiz(callback: CallbackQuery) -> None:
    quiz_states[callback.from_user.id] = {
        "index": 0,
        "score": 0,
    }

    await show_quiz_question(callback, 0)


async def show_quiz_question(callback: CallbackQuery, question_index: int) -> None:
    if question_index >= len(QUIZ_QUESTIONS):
        await show_quiz_result(callback)
        return

    question = QUIZ_QUESTIONS[question_index]

    await edit_or_answer(
        callback,
        question["question"],
        quiz_answer_keyboard(question_index),
    )


@dp.callback_query(F.data.startswith("quiz_answer:"))
async def handle_quiz_answer(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = quiz_states.get(user_id)

    if not state:
        quiz_states[user_id] = {
            "index": 0,
            "score": 0,
        }
        state = quiz_states[user_id]

    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer("Некорректный ответ.", show_alert=True)
        return

    question_index = int(parts[1])
    chosen_answer = parts[2]

    if question_index != state["index"]:
        await callback.answer("Этот вопрос уже обработан.", show_alert=True)
        return

    question = QUIZ_QUESTIONS[question_index]
    correct_answer = question["correct"]

    if chosen_answer == correct_answer:
        state["score"] += 1
        result_text = question["correct_text"]
    else:
        result_text = question["wrong_text"]

    state["index"] = question_index + 1

    is_last_question = state["index"] >= len(QUIZ_QUESTIONS)
    correct_leaflet = LEAFLETS[correct_answer]

    await answer_image_page(
        callback=callback,
        text=result_text,
        image_path=correct_leaflet["image"],
        reply_markup=quiz_next_keyboard(is_last_question),
    )


@dp.callback_query(F.data == "quiz_next")
async def handle_quiz_next(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = quiz_states.get(user_id)

    if not state:
        await edit_or_answer(callback, QUIZ_INTRO_TEXT, quiz_start_keyboard())
        return

    question_index = state["index"]

    if question_index >= len(QUIZ_QUESTIONS):
        await show_quiz_result(callback)
    else:
        await show_quiz_question(callback, question_index)


async def show_quiz_result(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = quiz_states.get(user_id, {"index": 0, "score": 0})

    score = state["score"]
    sr_points = score * 5

    if score == 5:
        text = f"""
🏆 Отличный результат!

Вы отлично ориентируетесь в листовках города.

Ваш результат: {score}/5
Начислено: +{sr_points} SR

Босс был бы доволен. Возможно, даже не кричал бы первые десять секунд.
""".strip()
    elif score >= 3:
        text = f"""
✅ Хороший результат!

Вы уже почти готовы к рабочей смене промоутера.

Ваш результат: {score}/5
Начислено: +{sr_points} SR

Ещё немного практики — и листовки сами начнут проситься вам в руки.
""".strip()
    else:
        text = f"""
⚠️ Нужно повторить рекламные материалы.

Ваш результат: {score}/5

Босс тяжело вздохнул и молча протянул вам ещё пачку листовок.
""".strip()

    await edit_or_answer(callback, text, quiz_final_keyboard())


# =========================
# ПРЕДСКАЗАНИЕ ЛИЛИТ
# =========================

@dp.callback_query(F.data == "prediction")
async def show_prediction(callback: CallbackQuery) -> None:
    prediction = random.choice(PREDICTIONS)

    text = f"""
🔮 Лилит раскладывает металлические карты...

{prediction}
""".strip()

    await answer_image_page(
        callback=callback,
        text=text,
        image_path=CHARACTERS["lilith"]["image"],
        reply_markup=prediction_keyboard(),
    )


# =========================
# ЗАПАСНЫЕ ОТВЕТЫ
# =========================

@dp.message()
async def unknown_message(message: Message) -> None:
    await message.answer(
        "⚙️ Терминал промоутера Steamleaf активен.\n\n"
        "Используйте /start, чтобы открыть главное меню."
    )


@dp.callback_query()
async def unknown_callback(callback: CallbackQuery) -> None:
    await callback.answer("Раздел не найден.", show_alert=True)


# =========================
# ЗАПУСК
# =========================

async def main() -> None:
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
