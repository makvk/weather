# ╔════════════════════════════════════════════════╗
# ║           СТАРАЯ ВЕРСИЯ ОБРАБОТЧИКА            ║
# ║                   /subscribe                   ║
# ║                 И ПЛАНИРОВЩИКА                 ║
# ╚════════════════════════════════════════════════╝

from aiogram import types, Router, Bot
from aiogram.filters import Command 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramBadRequest
from old_weather_api import WeatherAPI
from DataBases.work_with_tables import add_to_table, get_all_subscribers, remove_subscriber
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
scheduler = AsyncIOScheduler()
weather_api = WeatherAPI()

@router.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    user_id = message.from_user.id
    # Проверяем, указан ли город и время после команды
    city = message.text.split(maxsplit=2)
    if len(city) > 2:
        city, timerq = city[1], city[2]
        if not (0 <= int(timerq.split(":")[0]) <= 24) or not (0 <= int(timerq.split(":")[1]) <= 60):
            await message.answer("Некорректное время")
            return
        await message.answer("Вы подписались на рассылку!")
        await add_to_table(user_id, city, timerq)
    else:
        await message.answer("Пожалуйста, укажите город и время после команды, например:\n/subscribe Москва 8:00")

@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    user_id = message.from_user.id
    await remove_subscriber(user_id)
    await message.answer(
        "Вы отписались от рассылки"
    )

async def send_weather_update(bot: Bot, user_id, city):
    try:
        print("успех")
        weather_data = await weather_api.get_forecast_weather_city(city)

        if not weather_data:
            await bot.send_message(
                user_id,
                "Не удалось получить данные о погоде"
            )
        location = weather_data['location']
        current = weather_data['current']
        forecast_hours = weather_data['forecast']['forecastday'][0]['hour'][:24]  # Берем первые 24 часа

        weather_text = (
            f"🌦 <b>Погода в {location['name']} ({location['country']})</b>\n"
            f"📍 <i>{location['localtime']}</i>\n\n"
            f"<b>Сейчас:</b>\n"
            f"• {current['condition']['text']} {current['temp_c']}°C (ощущается как {current['feelslike_c']}°C)\n"
            f"• Ветер: {current['wind_kph']} км/ч ({current['wind_dir']})\n"
            f"• Влажность: {current['humidity']}%\n"
            f"• Осадки: {current['precip_mm']} мм\n\n"
            f"<b>Прогноз на 24 часа:</b>\n"
        )

        # Добавляем почасовой прогноз
        for hour in forecast_hours:
            time = hour['time'].split()[1][:5] 
            weather_text += (
                f"\n🕒 <b>{time}</b>: "
                f"{hour['temp_c']}°C, {hour['condition']['text']}, "
                f"🌧 {hour['chance_of_rain']}%"
            )

        await bot.send_message(
            user_id,
            weather_text,
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await remove_subscriber(user_id)
    except Exception as e:
        logger.error(f"Ошибка при получении прогноза погоды: {e}")
        bot.send_message(
            user_id,
            f"Произошла ошибка {e}"
        )

async def check_subscribers(bot: Bot):
    for job in scheduler.get_jobs():
        if job.func == send_weather_update:
            job.remove()

    subscribers = await get_all_subscribers()
    for user in subscribers:
        user_id = user["user_id"]
        city = user["city"]
        send_time = user["send_time"]
        print(user)
        try: 
            hour, minute = map(int, send_time.split(':'))
            scheduler.add_job(
                send_weather_update,
                "cron",
                hour = hour,
                minute = minute,
                args = [bot, user_id, city]
            )
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователей: {e}")
            raise

async def setup_scheduler(bot: Bot):
    await check_subscribers(bot)

    scheduler.add_job(
        check_subscribers,
        "interval",
        hours = 1,
        args = [bot]
    )

    if not scheduler.running:
        scheduler.start()