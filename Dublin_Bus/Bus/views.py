from django.http import JsonResponse
from django.shortcuts import render
from requests import get
from django.core import serializers
from datetime import datetime, date
import json
from .models import Stop, Trip, Calendar, Route, StopTime
import pickle
import pandas as pd
import xgboost
import sklearn
from .bus_models import get_prediction


# Create your views here.
def index(request):
    bus_stops_dict = bus_stops()
    ##MAP_KEY = APIKeys.MAP_API_KEY
    return render(request, 'Bus/index.html', bus_stops_dict)

#grabs bus stop data (id, name, lat, lon) for map/markers
def bus_stops():
    bus_stops_json = serializers.serialize("json", Stop.objects.all())
    bus_stops_dict = {}
    bus_stops_dict['bus_stops'] = bus_stops_json
    return bus_stops_dict


#handle request for stop_data
def fetch_stops(request):
    if request.method == "POST":
        stop_pk = json.loads(request.body)
        data = get_arrivals(stop_pk)
        return JsonResponse(data)
    else:
        data = {
            "msg": "It worked!!",
        }
        return JsonResponse(data)

#handle parameters for predictions, returns whole journey prediction, currently hardcoded to use model for route 145_102 for all routes
def send_to_model(request):
    if request.method =="POST":
        model_params = json.loads(request.body)
        prediction = {}
        prediction['current_pred'] = get_prediction(model_params)
        return JsonResponse(prediction)
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

    today_date = date.today()
    today_str = today_date.strftime("%Y%m%d")


    #This can definitely be neater/cleaner/faster - look into refactoring?
    #ALSO NEED TO TAKE INTO ACCOUNT SERVICE EXCEPTIONS IN CALENDAR_DATES AND TIMES PAST MIDNIGHT?
    query1 = StopTime.objects.filter(stop_id=stop_pk).filter(arrival_time__gt=datetime.now().time())
    query2 = Calendar.objects.filter(start_date__lt=today_str, end_date__gt=today_str).filter(**{today: 1})
    query3 = Trip.objects.filter(stoptime__in=query1).filter(service_id__in=query2)
    final_query = query1.filter(trip_id__in=query3).order_by('arrival_time')
    arrivals = serializers.serialize("json", final_query[:3])
    results['timetable'] = arrivals
    return results


