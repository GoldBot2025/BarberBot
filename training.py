from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_IDS

router = Router()

training_steps = [
    "🎓 Xodimlar uchun o‘quv\n\n"
    "1-qadam\n\n"
    "Mijoz yozilganda sizga xabar keladi.",

    "2-qadam\n\n"
    "Yangi yozuv kelganda:\n\n"
    "✅ Qabul qilish\n"
    "yoki\n"
    "❌ Bekor qilish\n\n"
    "tugmasini bosing.",

    "3-qadam\n\n"
    "Mijoz kelib bo‘lgandan keyin:\n\n"
    "☑️ Tashrif tugadi\n\n"
    "tugmasini bosing.",

    "4-qadam\n\n"
    "/my\n\n"
    "buyrug‘i orqali aktiv yozuvlarni ko‘rishingiz mumkin.",

    "🎉 O‘quv yakunlandi.\n\n"
    "Botdan foydalanishga tayyorsiz."
]


def get_training_keyboard(step: int):
    builder = InlineKeyboardBuilder()

    if step < len(training_steps) - 1:
        builder.button(
            text="➡️ Keyingi",
            callback_data=f"training_{step + 1}"
        )

    return builder.as_markup()


@router.message(Command("training"))
async def start_training(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer(
        training_steps[0],
        reply_markup=get_training_keyboard(0)
    )


@router.callback_query(F.data.startswith("training_"))
async def training_callback(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        return

    step = int(callback.data.split("_")[1])

    await callback.message.edit_text(
        training_steps[step],
        reply_markup=get_training_keyboard(step)
    )

    await callback.answer()