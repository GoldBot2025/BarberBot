from admin import off_days, disabled_times
from aiogram import Router, F

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from datetime import datetime
import re

from data import (
    services,
    service_translations,
    slots,
    times,
    get_days,
    format_price
)

from config import barbers
from translates import user_lang

router = Router()


# ===== БАЗА =====
user_data = {}
requests_db = {}
req_id_counter = 1


# ===== ТЕКСТЫ =====
def txt(user_id, ru, uz, en):

    lang = user_lang.get(user_id, "ru")

    return {
        "ru": ru,
        "uz": uz,
        "en": en
    }.get(lang, ru)


# ===== КНОПКИ ЯЗЫКА =====
def lang_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data="lang|ru"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇿 O'zbek",
                    callback_data="lang|uz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇸 English",
                    callback_data="lang|en"
                )
            ]
        ]
    )


# ===== ГЛАВНОЕ МЕНЮ =====
def main_kb(user_id):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=txt(
                        user_id,
                        "✂️ Записаться",
                        "✂️ Yozilish",
                        "✂️ Book now"
                    ),
                    callback_data="book"
                )
            ]
        ]
    )


# ===== КНОПКИ УСЛУГ =====
def services_kb(user_id):

    data = user_data[user_id]

    lang = user_lang.get(user_id, "ru")

    kb = []

    for category, items in services.items():

        kb.append([
            InlineKeyboardButton(
                text=service_translations[lang][category],
                callback_data="ignore"
            )
        ])

        for service_id, price in items.items():

            service_name = service_translations[lang][service_id]

            text = f"{service_name} ({price // 1000}k)"

            if service_id in data["services"]:
                text = f"✅ {text}"

            kb.append([
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"add|{service_id}"
                )
            ])

    kb.append([
        InlineKeyboardButton(
            text=txt(
                user_id,
                "✅ Готово",
                "✅ Tayyor",
                "✅ Done"
            ),
            callback_data="done"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


# ===== СТАРТ =====
@router.message(F.text == "/start")
async def start(msg: Message):

    await msg.answer(
        "🌍 Choose language / Tilni tanlang / Выберите язык",
        reply_markup=lang_kb()
    )


# ===== СОХРАНИТЬ ЯЗЫК =====
@router.callback_query(F.data.startswith("lang|"))
async def set_language(call: CallbackQuery):

    lang = call.data.split("|")[1]

    user_lang[call.from_user.id] = lang

    await call.message.edit_text(
        txt(
            call.from_user.id,
            "💈 Онлайн запись",
            "💈 Online yozilish",
            "💈 Online booking"
        ),
        reply_markup=main_kb(call.from_user.id)
    )


# ===== МОИ ЗАПИСИ =====
@router.message(F.text.lower() == "/my")
async def my_requests(msg: Message):

    user_id = msg.from_user.id
    lang = user_lang.get(user_id, "ru")

    barber_name = None

    for name, barber_id in barbers.items():

        if barber_id == user_id:
            barber_name = name
            break


    # ===== ЕСЛИ БАРБЕР =====
    if barber_name:

        found = False

        for req_id, req in requests_db.items():

            if req.get("status") == "done":
                continue

            if req["barber"] != barber_name:
                continue

            found = True

            status = req.get("status", "pending")

            emoji = {
                "pending": "🟡",
                "accepted": "🟢",
                "done": "✅",
                "declined": "❌"
            }.get(status, "⚪️")

            service_names = []

            for service_id in req["services"]:
                service_names.append(
                    service_translations[lang][service_id]
                )

            text = (
                f"{emoji} Заявка #{req_id}\n"
                f"📅 {req['date']} {req['time']}\n"
                f"💇 {', '.join(service_names)}\n"
                f"💰 {format_price(req['total'])}"
            )

            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=txt(
                                user_id,
                                "✅ Закрыть",
                                "✅ Yopish",
                                "✅ Close"
                            ),
                            callback_data=f"close|{req_id}"
                        )
                    ]
                ]
            )

            await msg.answer(
                text,
                reply_markup=kb
            )

        if not found:

            await msg.answer(
                txt(
                    user_id,
                    "❌ У тебя нет записей",
                    "❌ Sizda yozuvlar yo‘q",
                    "❌ You have no bookings"
                )
            )

        return


    # ===== ЕСЛИ КЛИЕНТ =====
    found = []

    for req_id, req in requests_db.items():

        if req.get("status") == "done":
            continue

        if req["user_id"] != user_id:
            continue

        status = req.get("status", "pending")

        emoji = {
            "pending": "🟡",
            "accepted": "🟢",
            "done": "✅",
            "declined": "❌"
        }.get(status, "⚪️")

        service_names = []

        for service_id in req["services"]:
            service_names.append(
                service_translations[lang][service_id]
            )

        found.append(
            f"{emoji} Заявка #{req_id}\n"
            f"📅 {req['date']} {req['time']}\n"
            f"💇 {', '.join(service_names)}\n"
            f"👨‍🔧 {req['barber']}\n"
            f"💰 {format_price(req['total'])}"
        )

    if not found:

        await msg.answer(
            txt(
                user_id,
                "❌ У тебя нет записей",
                "❌ Sizda yozuvlar yo‘q",
                "❌ You have no bookings"
            )
        )

        return

    await msg.answer(
        txt(
            user_id,
            "📋 Мои записи:\n\n",
            "📋 Mening yozuvlarim:\n\n",
            "📋 My bookings:\n\n"
        ) + "\n\n".join(found)
    )


# ===== НАЧАТЬ ЗАПИСЬ =====
@router.callback_query(F.data == "book")
async def booking(call: CallbackQuery):

    user_data[call.from_user.id] = {
        "services": [],
        "await_time": False
    }

    await call.message.edit_text(
        txt(
            call.from_user.id,
            "Выбери услуги:",
            "Xizmatlarni tanlang:",
            "Choose services:"
        ),
        reply_markup=services_kb(call.from_user.id)
    )


# ===== ДОБАВИТЬ УСЛУГУ =====
@router.callback_query(F.data.startswith("add|"))
async def add_service(call: CallbackQuery):

    data = user_data[call.from_user.id]

    service_id = call.data.split("|")[1]

    if service_id in data["services"]:
        data["services"].remove(service_id)
    else:
        data["services"].append(service_id)

    await call.message.edit_reply_markup(
        reply_markup=services_kb(call.from_user.id)
    )


# ===== ИГНОР =====
@router.callback_query(F.data == "ignore")
async def ignore(call: CallbackQuery):

    await call.answer()


# ===== ВЫБОР ДАТЫ =====
@router.callback_query(F.data == "done")
async def choose_date(call: CallbackQuery):

    data = user_data[call.from_user.id]

    if not data["services"]:

        await call.answer(
            txt(
                call.from_user.id,
                "❌ Выбери услуги",
                "❌ Xizmat tanlang",
                "❌ Choose services"
            ),
            show_alert=True
        )

        return

    kb = []

    for day in get_days():

        kb.append([
            InlineKeyboardButton(
                text=day,
                callback_data=f"date|{day}"
            )
        ])

    await call.message.edit_text(
        txt(
            call.from_user.id,
            "Выбери дату:",
            "Sanani tanlang:",
            "Choose date:"
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== ВЫБОР ВРЕМЕНИ =====
@router.callback_query(F.data.startswith("date|"))
async def choose_time(call: CallbackQuery):

    date = call.data.split("|")[1]

    user_data[call.from_user.id]["date"] = date

    kb = []

    now = datetime.now()

    for t in times:

        try:
            selected_datetime = datetime.strptime(
                f"{date} {t}",
                "%d.%m %H:%M"
            )

            selected_datetime = selected_datetime.replace(
                year=now.year
            )

        except:
            continue

        # если время уже прошло
        if selected_datetime <= now:
            continue

        kb.append([
            InlineKeyboardButton(
                text=t,
                callback_data=f"time|{t}"
            )
        ])

    kb.append([
        InlineKeyboardButton(
            text=txt(
                call.from_user.id,
                "✏️ Свое время",
                "✏️ O'z vaqti",
                "✏️ Custom time"
            ),
            callback_data="custom"
        )
    ])

    await call.message.edit_text(
        txt(
            call.from_user.id,
            "Выбери время:",
            "Vaqtni tanlang:",
            "Choose time:"
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== ВРЕМЯ КНОПКОЙ =====
@router.callback_query(F.data.startswith("time|"))
async def pick_time(call: CallbackQuery):

    selected_time = call.data.split("|")[1]

    user_data[call.from_user.id]["time"] = selected_time

    await show_barbers(call.message)


# ===== СВОЕ ВРЕМЯ =====
@router.callback_query(F.data == "custom")
async def custom_time(call: CallbackQuery):

    user_data[call.from_user.id]["await_time"] = True

    await call.message.edit_text(
        txt(
            call.from_user.id,
            "Введи время (12:20)",
            "Vaqt kiriting (12:20)",
            "Enter time (12:20)"
        )
    )


# ===== РУЧНОЕ ВРЕМЯ =====
@router.message(F.text.regexp(r"^\d{1,2}:\d{2}$"))
async def get_time(msg: Message):

    data = user_data.get(msg.from_user.id)

    if not data:
        return

    if not data.get("await_time"):
        return

    custom_value = msg.text

    try:

        t_obj = datetime.strptime(
            custom_value,
            "%H:%M"
        )

    except:

        await msg.answer(
            txt(
                msg.from_user.id,
                "❌ Неверное время",
                "❌ Noto'g'ri vaqt",
                "❌ Wrong time"
            )
        )

        return

    date = data["date"]

    now = datetime.now()

    selected_datetime = datetime.strptime(
        f"{date} {custom_value}",
        "%d.%m %H:%M"
    ).replace(year=now.year)

    if selected_datetime <= now:

        await msg.answer(
            txt(
                msg.from_user.id,
                "❌ Это время уже прошло",
                "❌ Bu vaqt o'tib ketgan",
                "❌ This time already passed"
            )
        )

        return

    data["time"] = custom_value
    data["await_time"] = False

    await show_barbers(msg)


# ===== ПОКАЗ БАРБЕРОВ =====
async def show_barbers(msg):

    data = user_data[msg.chat.id]

    date = data["date"]
    time = data["time"]

    kb = []

    for barber_name in barbers:

        if date in off_days[barber_name]:
            continue

        busy = slots[barber_name].get(date, set())

        disabled = disabled_times.get(
            barber_name,
            {}
        ).get(date, [])

        text = barber_name

        if time in busy or time in disabled:
            text += " ❌"

        kb.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"barber|{barber_name}"
            )
        ])

    await msg.answer(
        txt(
            msg.chat.id,
            "Выбери барбера:",
            "Barberni tanlang:",
            "Choose barber:"
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )

# ===== ПОКАЗ БАРБЕРОВ =====
async def show_barbers(msg):

    data = user_data[msg.chat.id]

    date = data["date"]
    time = data["time"]

    kb = []

    for barber_name in barbers:

        if date in off_days[barber_name]:
            continue

        busy = slots[barber_name].get(date, set())

        disabled = disabled_times.get(
            barber_name,
            {}
        ).get(date, [])

        text = barber_name

        if time in busy or time in disabled:
            text += " ❌"

        kb.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"barber|{barber_name}"
            )
        ])

    await msg.answer(
        txt(
            msg.chat.id,
            "Выбери барбера:",
            "Barberni tanlang:",
            "Choose barber:"
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== СОЗДАНИЕ ЗАЯВКИ =====
@router.callback_query(F.data.startswith("barber|"))
async def create_request(call: CallbackQuery):

    global req_id_counter

    data = user_data.get(call.from_user.id)

    if not data:
        return

    client_lang = user_lang.get(call.from_user.id, "ru")

    barber_name = call.data.split("|")[1]

    barber_id = barbers[barber_name]

    date = data["date"]
    time = data["time"]

    if date in off_days[barber_name]:

        await call.answer(
            "❌ У барбера выходной",
            show_alert=True
        )

        return

    disabled = disabled_times.get(
        barber_name,
        {}
    ).get(date, [])

    if time in disabled:

        await call.answer(
            "❌ Это время отключено",
            show_alert=True
        )

        return

    busy = slots[barber_name].get(date, set())

    if time in busy:

        free_barbers = []

        for other_barber in barbers:

            if other_barber == barber_name:
                continue

            other_busy = slots[other_barber].get(date, set())

            if time not in other_busy:
                free_barbers.append(other_barber)

        if free_barbers:

            await call.answer(
                f"❌ У {barber_name} занято\n"
                f"Свободен: {', '.join(free_barbers)}",
                show_alert=True
            )

        else:

            await call.answer(
                txt(
                    call.from_user.id,
                    "❌ Все барберы заняты",
                    "❌ Barcha barberlar band",
                    "❌ All barbers are busy"
                ),
                show_alert=True
            )

        return

    total = 0

    for service in data["services"]:

        for category in services.values():

            if service in category:
                total += category[service]

    slots[barber_name].setdefault(date, set()).add(time)

    req_id = req_id_counter
    req_id_counter += 1

    requests_db[req_id] = {
        "user_id": call.from_user.id,
        "barber": barber_name,
        "barber_id": barber_id,
        "date": date,
        "time": time,
        "services": data["services"],
        "total": total,
        "status": "pending"
    }

    service_names = []

    for service_id in data["services"]:

        service_names.append(
            service_translations[client_lang][service_id]
        )

    text = (
        f"📥 Заявка #{req_id}\n\n"
        f"💇 {', '.join(service_names)}\n"
        f"📅 {date}\n"
        f"⏰ {time}\n"
        f"👨‍🔧 {barber_name}\n\n"
        f"💰 К оплате: {format_price(total)}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"accept|{req_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отказать",
                    callback_data=f"decline|{req_id}"
                )
            ]
        ]
    )

    await call.message.edit_text(
        txt(
            call.from_user.id,
            f"✅ Запись отправлена!\n\n💰 {format_price(total)}\n\n/start — новая запись\n/my — мои записи",
            f"✅ Yozuv yuborildi!\n\n💰 {format_price(total)}\n\n/start — yangi yozuv\n/my — mening yozuvlarim",
            f"✅ Booking sent!\n\n💰 {format_price(total)}\n\n/start — new booking\n/my — my bookings"
        )
    )

    await call.bot.send_message(
        barber_id,
        text,
        reply_markup=kb
    )

    user_data.pop(call.from_user.id, None)


# ===== СОЗДАНИЕ ЗАЯВКИ =====
@router.callback_query(F.data.startswith("barber|"))
async def create_request(call: CallbackQuery):

    global req_id_counter

    data = user_data.get(call.from_user.id)

    if not data:
        return

    client_lang = user_lang.get(call.from_user.id, "ru")

    barber_name = call.data.split("|")[1]

    barber_id = barbers[barber_name]

    date = data["date"]
    time = data["time"]

    if date in off_days[barber_name]:

        await call.answer(
            "❌ У барбера выходной",
            show_alert=True
        )

        return

    if time in disabled_times[barber_name]:

        await call.answer(
            "❌ Это время отключено",
            show_alert=True
        )

        return

    busy = slots[barber_name].get(date, set())

    if time in busy:

        free_barbers = []

        for other_barber in barbers:

            if other_barber == barber_name:
                continue

            other_busy = slots[other_barber].get(date, set())

            if time not in other_busy:
                free_barbers.append(other_barber)

        if free_barbers:

            await call.answer(
                f"❌ У {barber_name} занято\n"
                f"Свободен: {', '.join(free_barbers)}",
                show_alert=True
            )

        else:

            await call.answer(
                txt(
                    call.from_user.id,
                    "❌ Все барберы заняты",
                    "❌ Barcha barberlar band",
                    "❌ All barbers are busy"
                ),
                show_alert=True
            )

        return

    total = 0

    for service in data["services"]:

        for category in services.values():

            if service in category:
                total += category[service]

    slots[barber_name].setdefault(date, set()).add(time)

    req_id = req_id_counter
    req_id_counter += 1

    requests_db[req_id] = {
        "user_id": call.from_user.id,
        "barber": barber_name,
        "barber_id": barber_id,
        "date": date,
        "time": time,
        "services": data["services"],
        "total": total,
        "status": "pending"
    }

    service_names = []

    for service_id in data["services"]:
        service_names.append(
            service_translations[client_lang][service_id]
        )

    text = (
        f"📥 Заявка #{req_id}\n\n"
        f"💇 {', '.join(service_names)}\n"
        f"📅 {date}\n"
        f"⏰ {time}\n"
        f"👨‍🔧 {barber_name}\n\n"
        f"💰 К оплате: {format_price(total)}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"accept|{req_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отказать",
                    callback_data=f"decline|{req_id}"
                )
            ]
        ]
    )

    await call.message.edit_text(
        txt(
            call.from_user.id,
            f"✅ Запись отправлена!\n\n💰 {format_price(total)}\n\n/start — новая запись\n/my — мои записи",
            f"✅ Yozuv yuborildi!\n\n💰 {format_price(total)}\n\n/start — yangi yozuv\n/my — mening yozuvlarim",
            f"✅ Booking sent!\n\n💰 {format_price(total)}\n\n/start — new booking\n/my — my bookings"
        )
    )

    await call.bot.send_message(
        barber_id,
        text,
        reply_markup=kb
    )

    user_data.pop(call.from_user.id, None)


# ===== ПРИНЯТЬ =====
@router.callback_query(F.data.startswith("accept|"))
async def accept(call: CallbackQuery):

    req_id = int(call.data.split("|")[1])

    req = requests_db.get(req_id)

    if not req:
        return

    req["status"] = "accepted"

    await call.message.edit_text(
        txt(
            req["user_id"],
            "✅ Принято",
            "✅ Qabul qilindi",
            "✅ Accepted"
        )
    )

    await call.bot.send_message(
        req["user_id"],
        txt(
            req["user_id"],
            f"✅ Запись подтверждена\n📅 {req['date']} {req['time']}",
            f"✅ Yozuv tasdiqlandi\n📅 {req['date']} {req['time']}",
            f"✅ Booking confirmed\n📅 {req['date']} {req['time']}"
        )
    )


# ===== ОТКАЗ =====
@router.callback_query(F.data.startswith("decline|"))
async def decline(call: CallbackQuery):

    req_id = int(call.data.split("|")[1])

    req = requests_db.get(req_id)

    if not req:
        return

    req["status"] = "declined"

    slots[req["barber"]][req["date"]].discard(req["time"])

    await call.message.edit_text(
        txt(
            req["user_id"],
            "❌ Отказ",
            "❌ Bekor qilindi",
            "❌ Declined"
        )
    )

    await call.bot.send_message(
        req["user_id"],
        txt(
            req["user_id"],
            "❌ Барбер отказал.\nВыбери другое время.",
            "❌ Barber rad etdi.\nBoshqa vaqt tanlang.",
            "❌ Barber declined.\nChoose another time."
        )
    )


# ===== ЗАКРЫТЬ ЗАПИСЬ =====
@router.callback_query(F.data.startswith("close|"))
async def close_request(call: CallbackQuery):

    req_id = int(call.data.split("|")[1])

    req = requests_db.get(req_id)

    if not req:
        return

    req["status"] = "done"

    slots[req["barber"]][req["date"]].discard(req["time"])

    await call.message.edit_text(
        txt(
            req["user_id"],
            f"✅ Запись завершена\n📅 {req['date']} {req['time']}",
            f"✅ Yozuv yakunlandi\n📅 {req['date']} {req['time']}",
            f"✅ Booking completed\n📅 {req['date']} {req['time']}"
        )
    )

    await call.bot.send_message(
        req["user_id"],
        txt(
            req["user_id"],
            "✅ Визит завершен\nСпасибо за посещение!",
            "✅ Tashrif yakunlandi\nTashrif uchun rahmat!",
            "✅ Visit completed\nThank you for visiting!"
        )
    )

