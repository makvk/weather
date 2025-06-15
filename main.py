import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.common import router as common_router
from handlers.weather import router as weather_router
from handlers.subscribe import router as subscribe_router
from handlers.subscribe import setup_scheduler
from DataBases.clear_table import clear_tb
from DataBases.work_with_tables import create_table_if_not_exists

async def main():
    await create_table_if_not_exists()
    
    bot = Bot(token = BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(common_router)
    dp.include_router(weather_router)
    dp.include_router(subscribe_router)

    # await clear_tb() # Функция очистки таблицы подписчиков
    await setup_scheduler(bot)
    print("Рассылка настроена. Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())