from config import WEATHER_API
from aiohttp_client_cache import SQLiteBackend, CachedSession

class WeatherAPI:
    def __init__(self):
        self.api_key = WEATHER_API
        self.base_url = "http://api.weatherapi.com/v1/"
        self.cache = SQLiteBackend(cache_name = "aiohttp_cache", expire_after = 3600)

    async def _make_request(self, location: str):
        async with CachedSession(cache = self.cache) as session:
            async with session.get(
                f"{self.base_url}/forecast.json?key={self.api_key}&q={location}&lang=ru"
            ) as response:
                if response.status == 200:
                    return await response.json()
                print(response.status)
                return None

    async def get_current_weather_city(self, city):
        return await self._make_request(city)

    async def get_current_weather_location(self, loc):
        return await self._make_request(','.join(map(str, loc)))
            
    async def get_forecast_weather_city(self, city):
        return await self._make_request(city)
