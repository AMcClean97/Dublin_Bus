from django.shortcuts import render
from requests import get

## from config.config import APIKeys
## To be implemented to allow all keys to be hidden!

city = "Dublin"
api_key = "4c249f84329a6c214486be5cdf2e5612"


# Create your views here.
def index(request):
    current_weather()
    ##MAP_KEY = APIKeys.MAP_API_KEY
    return render(request, 'Bus/index.html')

## Need to come back to ------
def current_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'

    response = get(url).json()
    weather = response["weather"][0]

    city_weather = {
        "Temperature": response['main']['temp'],
        "Feels Like": response['main']['feels_like'],
        "Minimum Temp": response['main']['temp_min'],
        "Maximum Temp": response['main']['temp_max'],
        "Humidity": response['main']['humidity'],
        "Description": weather["description"],
        "icon": weather["icon"]
    }
    return city_weather
