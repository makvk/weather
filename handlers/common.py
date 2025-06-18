from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message = types.Message):
    username = message.from_user.username
    await message.answer(
        f"Привет, @{username}! ☀️ Я могу показать погоду!\n\n"
        f"🔹 /weather [город] – погода по названию\n"
        f"🔹 /geo – погода по текущему местоположению\n"
        f"🔹 Или отправь желаемую геолокацию\n"
        f"🔹 Хотите получать уведомления? \n/subscribe – включить рассылку, \n/unsubscribe – выключить.\n\n"
        f"💡 Совет: зажми команду в меню — и она вставится в поле ввода!"
    )

@router.message(Command("help"))
async def cmd_help(message = types.Message):
    username = message.from_user.username
    await message.answer(
        f"Привет, @{username}! ☀️ Я могу показать погоду!\n\n"
        f"🔹 /weather [город] – погода по названию\n"
        f"🔹 /geo – погода по текущему местоположению\n"
        f"🔹 Или отправь желаемую геолокацию\n"
        f"🔹 Хотите получать уведомления? \n/subscribe – включить рассылку, \n/unsubscribe – выключить.\n\n"
        f"💡 Совет: зажми команду в меню — и она вставится в поле ввода!"
    )
