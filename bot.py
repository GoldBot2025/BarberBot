from training import router as training_router
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN

from booking import router as booking_router
from admin import router as admin_router


# ===== BOT =====
bot = Bot(
    token=BOT_TOKEN
)

dp = Dispatcher()
dp.include_router(training_router)

# ===== КОМАНДЫ =====
async def set_commands():

    commands = [

    BotCommand(
        command="start",
        description="Запустить бота"
    ),

    BotCommand(
        command="my",
        description="Мои записи"
    ),

    BotCommand(
        command="admin",
        description="Админ панель"
    ),

    BotCommand(
        command="training",
        description="Обучение сотрудников"
    )

]


# ===== СТАРТ =====
async def main():

    print("Бот запущен")

    # ROUTERS
    dp.include_router(admin_router)
    dp.include_router(booking_router)

    # COMMANDS
    await set_commands()

    # START
    await dp.start_polling(bot)


# ===== RUN =====
if __name__ == "__main__":

    asyncio.run(main())