import requests
from typing import Any

BASE_URL = "https://api.open-meteo.com/v1"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1"

class OpenMeteoClient:
    def __init__(self):
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict, base_url: str = None) -> dict[str, Any]:
        url = base_url or BASE_URL
        response = self.session.get(f"{url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast(self, lat: float, lon: float, timezone: str) -> dict:
        return self._get("forecast", {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation,windspeed_10m,relativehumidity_2m",
            "timezone": timezone,
            "forecast_days": 7,
        })

    def get_air_quality(self, lat: float, lon: float, timezone: str) -> dict:
        return self._get("air-quality", {
            "latitude": lat,
            "longitude": lon,
            "hourly": "pm10,pm2_5,ozone,nitrogen_dioxide",
            "timezone": timezone,
        }, base_url=AIR_QUALITY_URL)

    def get_historical(self, lat: float, lon: float, timezone: str, start: str, end: str) -> dict:
        return self._get("archive", {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "timezone": timezone,
            "start_date": start,
            "end_date": end,
        })