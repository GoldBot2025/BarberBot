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
    slots,
    times,
    get_days,
    format_price
)

from config import barbers

router = Router()

user_data = {}
requests_db = {}

req_id_counter = 1


# ===== ГЛАВНОЕ МЕНЮ =====
def main_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✂️ Записаться",
                    callback_data="book"
                )
            ]
        ]
    )


# ===== КНОПКИ УСЛУГ =====
def services_kb(user_id):

    data = user_data[user_id]

    kb = []

    for category, items in services.items():

        kb.append([
            InlineKeyboardButton(
                text=category,
                callback_data="ignore"
            )
        ])

        for name, price in items.items():

            text = f"{name} ({price // 1000}k)"

            if name in data["services"]:
                text = f"✅ {text}"

            kb.append([
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"add|{name}"
                )
            ])

    kb.append([
        InlineKeyboardButton(
            text="✅ Готово",
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
        "💈 Онлайн запись",
        reply_markup=main_kb()
    )


# ===== МОИ ЗАПИСИ =====
@router.message(F.text.lower() == "/my")
async def my_requests(msg: Message):

    user_id = msg.from_user.id

    barber_name = None

    for name, barber_id in barbers.items():

        if barber_id == user_id:
            barber_name = name
            break

    # ===== ЕСЛИ БАРБЕР =====
    if barber_name:

        found = False

        for req_id, req in requests_db.items():

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

            text = (
                f"{emoji} Заявка #{req_id}\n"
                f"📅 {req['date']} {req['time']}\n"
                f"💇 {', '.join(req['services'])}\n"
                f"💰 {format_price(req['total'])}"
            )

            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Закрыть",
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
                "❌ У тебя нет записей"
            )

        return

    # ===== ЕСЛИ КЛИЕНТ =====
    found = []

    for req_id, req in requests_db.items():

        if req["user_id"] == user_id:

            status = req.get("status", "pending")

            emoji = {
                "pending": "🟡",
                "accepted": "🟢",
                "done": "✅",
                "declined": "❌"
            }.get(status, "⚪️")

            found.append(
                f"{emoji} Заявка #{req_id}\n"
                f"📅 {req['date']} {req['time']}\n"
                f"💇 {', '.join(req['services'])}\n"
                f"👨‍🔧 {req['barber']}\n"
                f"💰 {format_price(req['total'])}"
            )

    if not found:

        await msg.answer(
            "❌ У тебя нет записей"
        )

        return

    await msg.answer(
        "📋 Мои записи:\n\n" + "\n\n".join(found)
    )


# ===== НАЧАТЬ ЗАПИСЬ =====
@router.callback_query(F.data == "book")
async def booking(call: CallbackQuery):

    user_data[call.from_user.id] = {
        "services": [],
        "await_time": False
    }

    await call.message.edit_text(
        "Выбери услуги:",
        reply_markup=services_kb(call.from_user.id)
    )


# ===== ДОБАВИТЬ УСЛУГУ =====
@router.callback_query(F.data.startswith("add|"))
async def add_service(call: CallbackQuery):

    data = user_data[call.from_user.id]

    name = call.data.split("|")[1]

    if name in data["services"]:
        data["services"].remove(name)

    else:
        data["services"].append(name)

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
            "❌ Выбери услуги",
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
        "Выбери дату:",
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
    today = now.strftime("%d.%m")

    for t in times:

        if date == today:

            t_obj = datetime.strptime(t, "%H:%M")

            if (
                t_obj.hour < now.hour or
                (
                    t_obj.hour == now.hour and
                    t_obj.minute <= now.minute
                )
            ):
                continue

        kb.append([
            InlineKeyboardButton(
                text=t,
                callback_data=f"time|{t}"
            )
        ])

    kb.append([
        InlineKeyboardButton(
            text="✏️ Свое время",
            callback_data="custom"
        )
    ])

    await call.message.edit_text(
        "Выбери время:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== ВЫБОР ВРЕМЕНИ КНОПКОЙ =====
@router.callback_query(F.data.startswith("time|"))
async def pick_time(call: CallbackQuery):

    time = call.data.split("|")[1]

    user_data[call.from_user.id]["time"] = time

    await show_barbers(call.message)


# ===== СВОЕ ВРЕМЯ =====
@router.callback_query(F.data == "custom")
async def custom_time(call: CallbackQuery):

    user_data[call.from_user.id]["await_time"] = True

    await call.message.edit_text(
        "Введи время (12:20)"
    )


# ===== РУЧНОЕ ВРЕМЯ =====
@router.message()
async def get_time(msg: Message):

    data = user_data.get(msg.from_user.id)

    if not data:
        return

    if not data.get("await_time"):
        return

    if not re.match(r"^\d{1,2}:\d{2}$", msg.text):

        await msg.answer(
            "❌ Неверный формат"
        )

        return

    custom_time = msg.text

    try:

        t_obj = datetime.strptime(
            custom_time,
            "%H:%M"
        )

    except:

        await msg.answer(
            "❌ Неверное время"
        )

        return

    date = data["date"]

    now = datetime.now()
    today = now.strftime("%d.%m")

    if date == today:

        if (
            t_obj.hour < now.hour or
            (
                t_obj.hour == now.hour and
                t_obj.minute <= now.minute
            )
        ):

            await msg.answer(
                "❌ Это время уже прошло"
            )

            return

    data["time"] = custom_time
    data["await_time"] = False

    await show_barbers(msg)


# ===== ПОКАЗ БАРБЕРОВ =====
async def show_barbers(msg):

    data = user_data[msg.chat.id]

    date = data["date"]
    time = data["time"]

    kb = []

    for barber_name in barbers:

        busy = slots[barber_name].get(date, set())

        text = barber_name

        if time in busy:
            text += " ❌"

        kb.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"barber|{barber_name}"
            )
        ])

    await msg.answer(
        "Выбери барбера:",
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

    barber_name = call.data.split("|")[1]

    barber_id = barbers[barber_name]

    date = data["date"]
    time = data["time"]

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
                "❌ Все барберы заняты",
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

    text = (
        f"📥 Заявка #{req_id}\n\n"
        f"💇 {', '.join(data['services'])}\n"
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
        f"✅ Запись отправлена!\n\n"
        f"💰 {format_price(total)}\n\n"
        f"/start — новая запись\n"
        f"/my — мои записи"
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
        "✅ Принято"
    )

    await call.bot.send_message(
        req["user_id"],
        f"✅ Запись подтверждена\n"
        f"📅 {req['date']} {req['time']}"
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
        "❌ Отказ"
    )

    await call.bot.send_message(
        req["user_id"],
        "❌ Барбер отказал.\n"
        "Выбери другое время."
    )


# ===== ЗАКРЫТЬ ЗАПИСЬ =====
@router.callback_query(F.data.startswith("close|"))
async def close_request(call: CallbackQuery):

    req_id = int(call.data.split("|")[1])

    req = requests_db.get(req_id)

    if not req:
        return

    req["status"] = "done"

    await call.message.edit_text(
        f"✅ Запись завершена\n"
        f"📅 {req['date']} {req['time']}"
    )

    await call.bot.send_message(
        req["user_id"],
        "✅ Визит завершен\n"
        "Спасибо за посещение!"
    )