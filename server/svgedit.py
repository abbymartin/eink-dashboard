import os
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from lxml import etree
import re 
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import json

load_dotenv()

meteo_url = "https://api.open-meteo.com/v1/forecast"
meteo_params = {
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
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

mbta_url = 'https://api-v3.mbta.com/predictions?filter[stop]=place-cntsq&include=vehicle,vehicle.stop'
mbta_params = {
    "api_key": os.getenv('MBTA_KEY')
}
mbta_session = requests_cache.CachedSession(
    'cache_mbta', 
    backend = 'sqlite',
    expire_after = timedelta(minutes=5)
)
direction_names = ['Ashmont/Braintree', 'Alewife']

# get weather data from openmeto api
def get_weather():
    responses = openmeteo.weather_api(meteo_url, params=meteo_params)
    response = responses[0]

    # current data
    current = response.Current()
    current_temp = current.Variables(0).Value()
    current_weather_code = current.Variables(1).Value() # corresponds to weather type icon

    # daily data: temp/weather for each hour
    hourly = response.Hourly()
    hourly_temp = hourly.Variables(0).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temp
    hourly_data["weather_code"] = hourly_weather_code

    hourly_dataframe = pd.DataFrame(data = hourly_data)

    # daily data: get high/low temp for current day
    daily = response.Daily()
    daily_temp_max = daily.Variables(0).ValuesAsNumpy()
    daily_temp_min = daily.Variables(1).ValuesAsNumpy()

    high = daily_temp_max[0]
    low = daily_temp_min[0]

    return high, low, current_temp, current_weather_code, hourly_dataframe

# return display time string based on timedelta until train prediction
def get_display_time(diff_time, vehicle, stops):
    if diff_time < timedelta(0): # train has already left
        return None

    status = vehicle['attributes']['current_status']
    stop_id = vehicle['relationships']['stop']['data']['id']
    stop_name = stops[stop_id]['attributes']['name']

    if status == 'STOPPED_AT' and stop_name == 'CENTRAL':
        return 'BRD'
    elif diff_time <= timedelta(seconds = 30):
        return 'ARR' # arriving
    elif diff_time <= timedelta(seconds = 60):
        return '1 min' # approaching
    
    minutes = round(diff_time.total_seconds() / 60)

    if minutes > 20:
        return '20+ min'
    
    return str(minutes) + ' min'

# get mbta train times
def get_trains():
    curr_time = datetime.now(ZoneInfo("America/New_York"))

    response = mbta_session.get(mbta_url, params=mbta_params)
    response_json = response.json()

    included = response_json['included']
    stops = {}
    vehicles = {}

    near_trains = [[], []]

    for item in included:
        if item['type'] == 'stop':
            stops[item['id']] = item
        elif item['type'] == 'vehicle':
            vehicles[item['id']] = item

    for pred in response_json['data']:
        if pred is None:
            continue

        departure_str = pred['attributes']['departure_time']
        if departure_str is None: # means train is unable to be boarded
            continue

        arrival_str = pred['attributes']['arrival_time']
        if arrival_str is None:
            continue

        direction = pred['attributes']['direction_id']

        if len(near_trains[direction]) >= 3:
            continue

        arrival_time = datetime.fromisoformat(arrival_str)
        diff_time = arrival_time - curr_time
        vehicle = vehicles[pred['relationships']['vehicle']['data']['id']]

        display_time = get_display_time(diff_time, vehicle, stops)
        if display_time is None:
            continue
        
        near_trains[direction].append(display_time)
    
    return near_trains
            

def update_svg():
    # get weather data
    high, low, current_temp, current_weather_code, hourly_dataframe = get_weather()

    date = datetime.now()

    # modify svg template
    xml = etree.parse('static/template.svg')
    svg = xml.getroot()[2]

    for elem in svg:
        currhour = date.hour
        id = elem.get('id')
        match(id):
            case('weekday'):
                elem.text = date.strftime("%A")
            case('date'): 
                elem.text = date.strftime("%B %d")
            case('currtemp'): 
                elem.text = str(int(current_temp))+'°'
            case('hightemp'):
                elem.text = str(int(high))+'°'
            case('lowtemp'):
                elem.text = str(int(low))+'°'
            case _ if (m := re.fullmatch(r"time(\d+)", str(id))): # next 6 hours
                num = int(m.group(1))
                hour = (hourly_dataframe['date'][num+currhour+1] - timedelta(hours=4)).hour
                txt = 'AM'
                if hour > 12: 
                    txt = 'PM'
                    hour-= 12
                if hour == 0:
                    hour = 12
                elem.text=str(hour)+txt
            case _ if (m := re.fullmatch(r"text(\d+)", str(id))): # temps for next 6 hours
                num = int(m.group(1))
                elem.text=str(int(hourly_dataframe['temperature_2m'][num+currhour+1]))+'°'

    # embed icons because linking file does not work when converting to png

    # current weather icon
    icon_xml = etree.parse(f"static/icons/{int(current_weather_code)}.svg")
    icon = icon_xml.getroot()
    icon.set('x', '94')
    icon.set('y', '2')
    svg.append(icon)

    # next 6 hours
    for i in range(6):
        icon_xml = etree.parse(f"static/icons/{int(hourly_dataframe['weather_code'][i+currhour+1])}.svg")
        icon = icon_xml.getroot()
        icon.set('id', 'icon'+str(i))
        icon.set('x', str(25*i))
        icon.set('y', '76')
        svg.append(icon)
    
    # train info
    near_trains = get_trains()
    y_pos = 145
    for i, trains in enumerate(near_trains):
        for j, time in enumerate(trains):
            text = etree.SubElement(svg, 'text', {
                'x': '10',
                'y': str(y_pos + j * 8 + i * 41),
                'font-style': 'normal',
                'font-weight': 'bold',
                'font-size': '9px',
                'font-family': 'monospace'
            })
            text.text = time       

    # updated svg
    xml.write('static/dash.svg')
