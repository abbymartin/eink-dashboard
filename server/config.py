import os
from dotenv import load_dotenv

load_dotenv()

METEO_URL = "https://api.open-meteo.com/v1/forecast"
METEO_PARAMS = {
    "latitude": os.getenv('COORD_LAT'),
    "longitude": os.getenv('COORD_LONG'),
    "hourly":  ["temperature_2m", "weather_code"],
    "current": ["temperature_2m", "weather_code"],
    "daily":   ["temperature_2m_max", "temperature_2m_min"],
    "timezone": "America/New_York",
    "wind_speed_unit": "mph",
    "temperature_unit": "fahrenheit",
    "precipitation_unit": "inch",
    "forecast_days": 2
}

TIMEZONE = 'America/New_York'
MBTA_URL = 'https://api-v3.mbta.com/predictions?filter[stop]=place-cntsq&include=vehicle,vehicle.stop'
MBTA_PARAMS = {
    "api_key": os.getenv('MBTA_KEY')
}
STATION_NAME = 'CENTRAL'

