import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from lxml import etree, objectify
import re 
from datetime import datetime


cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 33.749,
	"longitude": -84.388,
	"hourly":  ["temperature_2m", "weather_code"],
	"current": ["temperature_2m", "weather_code"],
    "daily":   ["temperature_2m_max", "temperature_2m_min"],
	"timezone": "America/New_York",
	"wind_speed_unit": "mph",
	"temperature_unit": "fahrenheit",
	"precipitation_unit": "inch",
    "forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_weather_code = current.Variables(1).Value()

print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}")
print(f"Current weather_code {current_weather_code}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()


hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["weather_code"] = hourly_weather_code

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

high = daily_temperature_2m_max[0]
low = daily_temperature_2m_min[0]

#make svg
xml = etree.parse('template.svg')
svg = xml.getroot()[2]
#print(svg)

for elem in svg:
    currhour = datetime.now().hour
    id = elem.get('id')
    match(id):
        case('currtemp'):
            elem.text = str(int(current_temperature_2m))+'°'
        case('curricon'):
            elem.set('href', f"icons/{int(current_weather_code)}.svg")
        case('hightemp'):
            elem.text = str(int(high))+'°'
        case('lowtemp'):
            elem.text = str(int(low))+'°'
        case _ if (m := re.fullmatch(r"time(\d+)", str(id))):
            num = int(m.group(1))
            hour = hourly_dataframe['date'][num+currhour+1].hour-4
            txt = 'AM'
            if hour <= 0:
                hour += 12
                txt = 'PM'
            if hour > 12: 
                txt = 'PM'
                hour-= 12
            elem.text=str(hour)+txt
        case _ if (m := re.fullmatch(r"icon(\d+)", str(id))):
            num = int(m.group(1))
            elem.set('href', f"icons/{int(hourly_dataframe['weather_code'][num+currhour+1])}.svg")
        case _ if (m := re.fullmatch(r"text(\d+)", str(id))):
            num = int(m.group(1))
            elem.text=str(int(hourly_dataframe['temperature_2m'][num+currhour+1]))+'°'
        
    # print(text.text)
        

xml.write('dash.svg')
