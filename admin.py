from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from config import barbers, ADMIN_IDS


router = Router()


# ===== ВЫХОДНЫЕ =====
off_days = {
    barber_name: []
    for barber_name in barbers
}


# ===== ОТКЛЮЧЕННОЕ ВРЕМЯ =====
# {
#     "Максим": {
#         "10.05": ["15:00", "16:00"]
#     }
# }
disabled_times = {
    barber_name: {}
    for barber_name in barbers
}


# ===== ВРЕМЕННЫЕ ДАННЫЕ =====
admin_temp = {}


# ===== ПРОВЕРКА =====
def is_admin(user_id):

    return user_id in ADMIN_IDS


# ===== ДАТЫ =====
def get_dates():

    return [
        "10.05",
        "11.05",
        "12.05",
        "13.05",
        "14.05",
        "15.05",
        "16.05"
    ]


# ===== ВРЕМЯ =====
def get_times():

    return [
        "00:00",
        "01:00",
        "02:00",
        "03:00",
        "04:00",
        "05:00",
        "06:00",
        "07:00",
        "08:00",
        "09:00",
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


# ===== АДМИНКА =====
@router.message(F.text == "/admin")
async def admin_panel(msg: Message):

    if not is_admin(msg.from_user.id):
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📅 Выходные дни",
                    callback_data="admin_offdays"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⏰ Отключить время",
                    callback_data="admin_time"
                )
            ]

        ]
    )

    await msg.answer(
        "⚙️ Админ-панель",
        reply_markup=kb
    )


# ===== ВЫБОР БАРБЕРА =====
@router.callback_query(F.data == "admin_offdays")
@router.callback_query(F.data == "admin_time")
async def choose_barber(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    mode = call.data

    kb = []

    for barber_name in barbers:

        kb.append([
            InlineKeyboardButton(
                text=barber_name,
                callback_data=f"{mode}|{barber_name}"
            )
        ])

    await call.message.edit_text(
        "👨‍🔧 Выбери барбера:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== ВЫБОР ДАТЫ ДЛЯ ВЫХОДНОГО =====
@router.callback_query(F.data.startswith("admin_offdays|"))
async def offday_dates(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    barber_name = call.data.split("|")[1]

    kb = []

    for day in get_dates():

        mark = ""

        if day in off_days[barber_name]:
            mark = " ✅"

        kb.append([
            InlineKeyboardButton(
                text=day + mark,
                callback_data=f"toggle_off|{barber_name}|{day}"
            )
        ])

    await call.message.edit_text(
        f"📅 Выходные: {barber_name}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== ПЕРЕКЛЮЧЕНИЕ ВЫХОДНОГО =====
@router.callback_query(F.data.startswith("toggle_off|"))
async def toggle_offday(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    _, barber_name, day = call.data.split("|")

    if day in off_days[barber_name]:
        off_days[barber_name].remove(day)
    else:
        off_days[barber_name].append(day)

    await offday_dates(
        CallbackQuery(
            id=call.id,
            from_user=call.from_user,
            chat_instance=call.chat_instance,
            message=call.message,
            data=f"admin_offdays|{barber_name}"
        )
    )


# ===== ВЫБОР ДАТЫ ДЛЯ ВРЕМЕНИ =====
@router.callback_query(F.data.startswith("admin_time|"))
async def choose_time_date(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    barber_name = call.data.split("|")[1]

    admin_temp[call.from_user.id] = barber_name

    kb = []

    for day in get_dates():

        kb.append([
            InlineKeyboardButton(
                text=day,
                callback_data=f"time_date|{day}"
            )
        ])

    await call.message.edit_text(
        f"📅 Выбери дату для {barber_name}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== ВЫБОР ВРЕМЕНИ =====
@router.callback_query(F.data.startswith("time_date|"))
async def choose_time(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    date = call.data.split("|")[1]

    barber_name = admin_temp[call.from_user.id]

    disabled_times.setdefault(barber_name, {})
    disabled_times[barber_name].setdefault(date, [])

    kb = []

    for time in get_times():

        mark = ""

        if time in disabled_times[barber_name][date]:
            mark = " ❌"

        kb.append([
            InlineKeyboardButton(
                text=time + mark,
                callback_data=f"toggle_time|{date}|{time}"
            )
        ])

    await call.message.edit_text(
        f"⏰ {barber_name} | {date}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


# ===== ПЕРЕКЛЮЧЕНИЕ ВРЕМЕНИ =====
@router.callback_query(F.data.startswith("toggle_time|"))
async def toggle_time(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    _, date, time = call.data.split("|")

    barber_name = admin_temp[call.from_user.id]

    disabled_times.setdefault(barber_name, {})
    disabled_times[barber_name].setdefault(date, [])

    if time in disabled_times[barber_name][date]:
        disabled_times[barber_name][date].remove(time)
    else:
        disabled_times[barber_name][date].append(time)

    await choose_time(
        CallbackQuery(
            id=call.id,
            from_user=call.from_user,
            chat_instance=call.chat_instance,
            message=call.message,
            data=f"time_date|{date}"
        )
    )