from django.http import JsonResponse
from django.shortcuts import render
from requests import get
from .models import Stop, Trip, Calendar, StopTime, Route
from django.core import serializers
from datetime import datetime, timedelta
import json
## from config.config import APIKeys
## To be implemented to allow all keys to be hidden!

city = "Dublin"
api_key = "4c249f84329a6c214486be5cdf2e5612"


# Create your views here.
def index(request):
    current_weather()
    bus_stops_dict = bus_stops()
    ##MAP_KEY = APIKeys.MAP_API_KEY
    return render(request, 'Bus/index.html', bus_stops_dict)

#grabs bus stop data (id, name, lat, lon) for map/markers
def bus_stops():
    bus_stops_json = serializers.serialize("json", Stop.objects.all())
    bus_stops_dict = {}
    bus_stops_dict['bus_stops'] = bus_stops_json
    return bus_stops_dict

#handle ajax request
def ajax_view(request):
    if request.method == "POST":
        stop_pk = json.loads(request.body)
        data = get_arrivals(stop_pk)
        return JsonResponse(data)
    else:
        data = {
            "msg": "It worked!!",
        }
        return JsonResponse(data)

#get next 5 arrivals for a given stop
def get_arrivals(stop_pk):
    today_int = datetime.today().weekday()
    if today_int == 0:
        today = 'monday'
    elif today_int == 1:
        today = 'tuesday'
    elif today_int == 2:
        today = 'wednesday'
    elif today_int == 3:
        today = 'thursday'
    elif today_int == 4:
        today = 'friday'
    elif today_int == 5:
        today = 'saturday'
    else:
        today = 'sunday'

    results = {}

    #This can definitely be neater/cleaner - look into refactoring?
    query1 = StopTime.objects.filter(stop_id=stop_pk)
    query2 = query1.filter(arrival_time__gt=datetime.now().time()).order_by('arrival_time')
    query3 = Trip.objects.filter(stoptime__in=query2)
    query4 = Calendar.objects.filter(**{today: 1})
    query5 = query3.filter(service_id__in=query4)
    final_query = query2.filter(trip_id__in=query5)
    arrivals = serializers.serialize("json", final_query)
    results['timetable'] = arrivals
    return results



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
