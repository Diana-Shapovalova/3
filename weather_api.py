import requests
import pandas as pd
from datetime import datetime

API_KEY = "SlQLdL8V9RaiYUQv8IADktwUWRaX1gAu"

def get_city_coordinates(city_name):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    location_data = response.json()
    if not location_data:
        print("Город не найден")
        return None
    latitude = location_data[0]["GeoPosition"]["Latitude"]
    longitude = location_data[0]["GeoPosition"]["Longitude"]
    return (latitude, longitude)

def get_weather_data(city, days):
    location_key = get_location_key(city, API_KEY)
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/{days}day/{location_key}?apikey={API_KEY}&metric=true&details=true"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    forecast_data = response.json()["DailyForecasts"]
    data = {
        "date": [datetime.strptime(day["Date"][:10], "%Y-%m-%d") for day in forecast_data],
        "temperature": [day["Temperature"]["Maximum"]["Value"] for day in forecast_data],
        "wind_speed": [day["Day"]["Wind"]["Speed"]["Value"] for day in forecast_data],
        "precipitation": [day["Day"].get("PrecipitationProbability", 0) for day in forecast_data]
    }
    return pd.DataFrame(data)

def get_location_key(location, api_key):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={api_key}&q={location}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка поиска города: {response.status_code}")
        return None
    data = response.json()
    return data[0]["Key"] if data else None