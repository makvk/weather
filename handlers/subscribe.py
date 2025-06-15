from aiogram import types, Router, Bot
from aiogram.filters import Command 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramBadRequest
from weather_api import WeatherAPI
from DataBases.work_with_tables import add_to_table, get_all_subscribers, remove_subscriber
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
scheduler = AsyncIOScheduler()
weather_api = WeatherAPI()

# Отправка сообщения 
async def send_weather_update(bot: Bot, user_id, city):
    try:
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
        raise

# Обработчик команды /subscribe
@router.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    # Проверяем, указан ли город и время после команды
    city = message.text.split(maxsplit=2)
    if len(city) > 2:
        city, timerq = city[1], city[2]
        if not (0 <= int(timerq.split(":")[0]) <= 24) or not (0 <= int(timerq.split(":")[1]) <= 60):
            await message.answer("Некорректное время")
            return
        hour, minute = map(int, timerq.split(":"))
        if not(await user_in_scheduler(user_id)):
            await add_to_table(user_id, city, timerq)
            scheduler.add_job(
                send_weather_update,
                "cron",
                hour = hour,
                minute = minute,
                args = [bot, user_id, city]
            )
            await message.answer("Вы подписались на рассылку!")
        else: 
            subscribers = await get_all_subscribers()
            for user in subscribers:
                if user["user_id"] == user_id:
                    current_city = user["city"]
                    current_send_time = user["send_time"]
            await message.answer(
                f"Вы уже подписаны на рассылку!\n"
                f"Рассылка назначена на {current_send_time}.\n"
                f"Текущий город - {current_city}.\n"
                f"Чтобы отписаться введите /unsubscribe"
            )
        print(scheduler.get_jobs())
        print(await get_all_subscribers())
    else:
        await message.answer("Пожалуйста, укажите город и время(по МСК, UTC +3) после команды.\n\nНапример: /subscribe Москва 8:00")

# Обработчик команды /unsubscribe
@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    user_id = message.from_user.id
    await remove_subscriber(user_id)
    await message.answer(
        "Вы отписались от рассылки"
    )
    await remove_cheduler_job(user_id)

# Ниже все функции планировщика

# Проверка задач планировщка на наличие задачи для конкретного пользователя(по user_id) 
async def user_in_scheduler(user_id):
    for job in scheduler.get_jobs():
        if job.args[1] == user_id:
            return True
    return False

# Удаление задачи из планирощика по user_id
async def remove_cheduler_job(user_id):
    for job in scheduler.get_jobs():
        print(job)
        if job.args[1] == user_id:
            job.remove()

# Установка планировщика
async def setup_scheduler(bot: Bot):
    subscribers = await get_all_subscribers()
    for user in subscribers:
        user_id = user["user_id"]
        city = user["city"]
        send_time = user["send_time"]
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

        print(f"Текущие задачи: {scheduler.get_jobs()}")

    if not scheduler.running:
        scheduler.start()