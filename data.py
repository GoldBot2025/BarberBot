from datetime import datetime, timedelta


# ===== ДАТЫ =====
def get_days():

    today = datetime.now()

    return [
        (today + timedelta(days=i)).strftime("%d.%m")
        for i in range(7)
    ]


# ===== ВРЕМЯ =====
times = [
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00",
    "22:00",
    "23:00"
]


# ===== СЛОТЫ ПО БАРБЕРАМ =====
slots = {
    "Максим": {},
    "Алишер": {}
}


# ===== УСЛУГИ =====
# Ключи технические.
# НУЖНО для мультиязычности.

services = {

    "haircuts": {

        "mens": 100000,
        "fade": 120000,
        "machine": 70000,
        "kids": 70000,
        "combo": 150000
    },

    "beard": {

        "beard_trim": 70000,
        "royal": 100000,
        "premium": 150000,
        "camouflage": 70000
    },

    "care": {

        "paint": 70000,
        "styling": 50000,
        "cleaning": 150000,
        "highlight": 300000,
        "keratin": 450000
    }
}


# ===== ПЕРЕВОДЫ УСЛУГ =====
service_translations = {

    "ru": {

        # категории
        "haircuts": "💇 СТРИЖКИ",
        "beard": "🧔 БОРОДА",
        "care": "✨ УХОД",

        # услуги
        "mens": "✂️ Мужская",
        "fade": "🔥 Фейд",
        "machine": "⚡ Машинкой",
        "kids": "👶 Детская",
        "combo": "✂️🧔 Стрижка + борода",

        "beard_trim": "🧔 Оформление",
        "royal": "👑 Королевское",
        "premium": "💎 Комплекс",
        "camouflage": "🎭 Камуфляж",

        "paint": "🎨 Краска",
        "styling": "💇 Укладка",
        "cleaning": "🧼 Чистка лица",
        "highlight": "✨ Мелирование",
        "keratin": "🧪 Кератин"
    },


    "uz": {

        # категории
        "haircuts": "💇 SOCH OLISH",
        "beard": "🧔 SOQOL",
        "care": "✨ PARVARISH",

        # услуги
        "mens": "✂️ Erkaklar sochi",
        "fade": "🔥 Feyd",
        "machine": "⚡ Mashinka",
        "kids": "👶 Bolalar",
        "combo": "✂️🧔 Soch + soqol",

        "beard_trim": "🧔 Shakl berish",
        "royal": "👑 Qirollik",
        "premium": "💎 Kompleks",
        "camouflage": "🎭 Kamuflyaj",

        "paint": "🎨 Bo‘yash",
        "styling": "💇 Ukladka",
        "cleaning": "🧼 Yuz tozalash",
        "highlight": "✨ Melirovka",
        "keratin": "🧪 Keratin"
    },


    "en": {

        # категории
        "haircuts": "💇 HAIRCUTS",
        "beard": "🧔 BEARD",
        "care": "✨ CARE",

        # услуги
        "mens": "✂️ Men's haircut",
        "fade": "🔥 Fade",
        "machine": "⚡ Machine cut",
        "kids": "👶 Kids haircut",
        "combo": "✂️🧔 Hair + beard",

        "beard_trim": "🧔 Beard trim",
        "royal": "👑 Royal care",
        "premium": "💎 Premium",
        "camouflage": "🎭 Camouflage",

        "paint": "🎨 Coloring",
        "styling": "💇 Styling",
        "cleaning": "🧼 Face cleaning",
        "highlight": "✨ Highlighting",
        "keratin": "🧪 Keratin"
    }
}


# ===== ФОРМАТ ЦЕН =====
def format_price(price):

    return f"{price:,}".replace(",", " ") + " сум"