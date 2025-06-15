# ╔════════════════════════════════════════════════╗
# ║             СТАРАЯ ВЕРСИЯ СОЗДАНИЯ             ║
# ║                    ЗАПРОСОВ                    ║
# ╚════════════════════════════════════════════════╝

from config import WEATHER_API
from aiohttp_client_cache import SQLiteBackend, CachedSession

class WeatherAPI:
    def __init__(self):
        self.api_key = WEATHER_API
        self.base_url = "http://api.weatherapi.com/v1/"
        self.cache = SQLiteBackend(cache_name = "aiohttp_cache", expire_after = 3600)

    async def get_current_weather_city(self, city):
        async with CachedSession(cache = self.cache) as session:
            async with session.get(
                    f"{self.base_url}current.json?key={self.api_key}&q={city}&lang=ru"
            ) as response:
                if response.status == 200:
                    return await response.json()
                print(response.status)
                return None

    async def get_current_weather_location(self, *loc):
        lat, lon = loc
        async with CachedSession(cache = self.cache) as session:
            async with session.get(
                f"{self.base_url}current.json?key={self.api_key}&q={lat},{lon}&lang=ru"
            ) as response:
                if response.status == 200:
                    return await response.json()
                print(response.status)
                return None
            
    async def get_forecast_weather_city(self, city):
        async with CachedSession(cache = self.cache) as session:
            async with session.get(
                    f"{self.base_url}/forecast.json?key={self.api_key}&q={city}&lang=ru"
            ) as response:
                if response.status == 200:
                    return await response.json()
                print(response.status)
                return None