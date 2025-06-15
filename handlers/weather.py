from aiogram import Router, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from weather_api import WeatherAPI
from aiogram.fsm.context import FSMContext

router = Router()
weather_api = WeatherAPI()

def get_inline_kb():
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "Получить погоду на день", callback_data = "forecast_weather:")
            ]
        ],
        resize_keyboard = True,
        one_time_keyboard = True
    )
    return keyboard

@router.callback_query(F.data == "forecast_weather:")
async def get_forecast_weather(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        forecast_hours = (await state.get_data())['forecast']['forecastday'][0]['hour'][:24]
        await state.clear()
        weather_text = f"Погода на 24 часа \n"
        for hour in forecast_hours:
            time = hour['time'].split()[1][:5] 
            weather_text += (
                f"\n🕒 <b>{time}</b>: "
                f"{hour['temp_c']}°C, {hour['condition']['text']}, "
                f"🌧 {hour['chance_of_rain']}%"
            )
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.message.answer(
            weather_text,
            parse_mode="HTML"
        )
    except:
        await callback_query.message.edit_reply_markup(reply_markup=None)

@router.message(Command("weather"))
async def cmd_weather(message: types.Message, state: FSMContext):
    # Проверяем, указан ли город после команды
    city = message.text.split(maxsplit=1)
    if len(city) > 1:
        city = city[1]
        await process_weather_request(message, state, city)
    else:
        await message.answer("Пожалуйста, укажите город после команды, например:\n/weather Москва")

async def process_weather_request(message: types.Message, state: FSMContext, city: str):
    try:
        weather_data = await weather_api.get_current_weather_city(city)

        if not weather_data:
            await message.answer("Не удалось получить данные о погоде")
            return
        
        location = weather_data['location']
        current = weather_data['current']

        weather_text = (
            f"🌦 <b>Погода в {location['name']} ({location['country']})</b>\n"
            f"📍 <i>{location['localtime']}</i>\n\n"
            f"<b>Сейчас:</b>\n"
            f"🌡️ {current['condition']['text']} {current['temp_c']}°C (ощущается как {current['feelslike_c']}°C)\n"
            f"🌬️ Ветер: {current['wind_kph']} км/ч ({current['wind_dir']})\n"
            f"💧 Влажность: {current['humidity']}%\n"
            f"🌧 Осадки: {current['precip_mm']} мм\n\n"
        )

        await message.answer(
            weather_text,
            parse_mode="HTML",
            reply_markup = get_inline_kb()
        )
        await state.clear()
        await state.update_data(**weather_data)
    except Exception as e:
        await message.answer(
            f"Произошла ошибка: {e}"
        )
        raise

# Погода по координатам
@router.message(F.text == "🔴 Отмена")
async def cancellation(message: types.Message):
    await message.answer(
        f"Ладно",
        reply_markup = ReplyKeyboardRemove()
    )

@router.message(lambda message: message.location is not None)
async def handle_location(message: types.Message, state: FSMContext):
    try:
        lat = message.location.latitude
        lon = message.location.longitude
        await message.answer(
            f"ваши координаты: {lat}, {lon}\n\n"
            f"Формирую запрос...",
            reply_markup = ReplyKeyboardRemove()
        )

        weather_data = await weather_api.get_current_weather_location([lat, lon])

        if not weather_data:
            await message.answer("Не удалось получить данные о погоде")
            return

        location = weather_data['location']
        current = weather_data['current']

        weather_text = (
            f"🌦 <b>Погода в городе по координатам {location['lat']} {location['lon']}</b>\n"
            f"📍 <i>{location['localtime']}</i>\n\n"
            f"<b>Сейчас:</b>\n"
            f"🌡️ {current['condition']['text']} {current['temp_c']}°C (ощущается как {current['feelslike_c']}°C)\n"
            f"🌬️ Ветер: {current['wind_kph']} км/ч ({current['wind_dir']})\n"
            f"💧 Влажность: {current['humidity']}%\n"
            f"🌧 Осадки: {current['precip_mm']} мм\n\n"
        )

        await message.answer(
            weather_text,
            parse_mode="HTML",
            reply_markup = get_inline_kb()
        )
        await state.clear()
        await state.update_data(**weather_data)
    except Exception as e:
        await message.answer(
            f"Произошла ошибка: {e}"
        )

@router.message(Command("geo"))
async def request_location(message: types.Message): 

    location_keyboard = ReplyKeyboardMarkup(
        keyboard = [
            [
                KeyboardButton(text="📍 Отправить местоположение", request_location=True),
                KeyboardButton(text="🔴 Отмена")
            ]
        ],
        resize_keyboard = True,
        one_time_keyboard = True
    )

    await message.answer(
        f"Отправьте геолокацию",
        reply_markup = location_keyboard
    )


