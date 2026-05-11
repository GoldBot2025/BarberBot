# ===== ЯЗЫКИ ПОЛЬЗОВАТЕЛЕЙ =====
user_lang = {}


# ===== ВСЕ ТЕКСТЫ =====
texts = {

    "ru": {

        # start
        "start": "💈 Онлайн запись",
        "choose_lang": "🌍 Выбери язык",
        "book": "✂️ Записаться",
        "my": "/my — мои записи",

        # booking
        "choose_services": "Выбери услуги:",
        "done": "✅ Готово",
        "choose_date": "Выбери дату:",
        "choose_time": "Выбери время:",
        "custom_time": "✏️ Свое время",
        "enter_time": "Введи время (12:20)",

        # errors
        "choose_service_error": "❌ Выбери услуги",
        "wrong_format": "❌ Неверный формат",
        "wrong_time": "❌ Неверное время",
        "time_passed": "❌ Это время уже прошло",

        # barber
        "choose_barber": "Выбери барбера:",
        "busy": "❌",
        "all_busy": "❌ Все барберы заняты",

        # request
        "request_sent": "✅ Запись отправлена!",
        "new_booking": "/start — новая запись",

        # statuses
        "accepted": "✅ Запись подтверждена",
        "declined": "❌ Барбер отказал.\nВыбери другое время.",
        "done_visit": "✅ Визит завершен\nСпасибо за посещение!"
    },


    "uz": {

        # start
        "start": "💈 Online yozilish",
        "choose_lang": "🌍 Tilni tanlang",
        "book": "✂️ Yozilish",
        "my": "/my — mening yozuvlarim",

        # booking
        "choose_services": "Xizmatlarni tanlang:",
        "done": "✅ Tayyor",
        "choose_date": "Sanani tanlang:",
        "choose_time": "Vaqtni tanlang:",
        "custom_time": "✏️ O'z vaqtim",
        "enter_time": "Vaqtni kiriting (12:20)",

        # errors
        "choose_service_error": "❌ Xizmat tanlang",
        "wrong_format": "❌ Noto'g'ri format",
        "wrong_time": "❌ Noto'g'ri vaqt",
        "time_passed": "❌ Bu vaqt o'tib ketgan",

        # barber
        "choose_barber": "Barberni tanlang:",
        "busy": "❌",
        "all_busy": "❌ Barcha barberlar band",

        # request
        "request_sent": "✅ Yozuv yuborildi!",
        "new_booking": "/start — yangi yozuv",

        # statuses
        "accepted": "✅ Yozuv tasdiqlandi",
        "declined": "❌ Barber rad etdi.\nBoshqa vaqt tanlang.",
        "done_visit": "✅ Tashrif yakunlandi\nTashrif uchun rahmat!"
    },


    "en": {

        # start
        "start": "💈 Online booking",
        "choose_lang": "🌍 Choose language",
        "book": "✂️ Book now",
        "my": "/my — my bookings",

        # booking
        "choose_services": "Choose services:",
        "done": "✅ Done",
        "choose_date": "Choose date:",
        "choose_time": "Choose time:",
        "custom_time": "✏️ Custom time",
        "enter_time": "Enter time (12:20)",

        # errors
        "choose_service_error": "❌ Choose services",
        "wrong_format": "❌ Wrong format",
        "wrong_time": "❌ Invalid time",
        "time_passed": "❌ This time has already passed",

        # barber
        "choose_barber": "Choose barber:",
        "busy": "❌",
        "all_busy": "❌ All barbers are busy",

        # request
        "request_sent": "✅ Booking sent!",
        "new_booking": "/start — new booking",

        # statuses
        "accepted": "✅ Booking confirmed",
        "declined": "❌ Barber declined.\nChoose another time.",
        "done_visit": "✅ Visit completed\nThank you for visiting!"
    }
}


# ===== ПЕРЕВОД =====
def t(user_id, key):

    lang = user_lang.get(user_id, "ru")

    return texts[lang].get(key, key)