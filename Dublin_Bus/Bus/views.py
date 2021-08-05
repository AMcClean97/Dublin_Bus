from django.http import JsonResponse
from django.shortcuts import render
from requests import get
from django.core import serializers
from datetime import datetime, date, timedelta
import json
from .models import Stop, Trip, Calendar, Route, StopTime, CalendarDate
from .bus_models import get_prediction
from .serializers import StopTimeSerializer
from users.models import favourite


# Create your views here.
def index(request):
    favourites_json = serializers.serialize("json", favourite.objects.filter(user_id= request.user.id))
    bus_stops_json = serializers.serialize("json", Stop.objects.all())
    context = { 
        'bus_stops': bus_stops_json,
        'favourites' : favourites_json
    }
    if request.method == 'POST':
        favourite_id = request.POST.get('favourite_id')
        context['journey'] = favourite.objects.get(id=favourite_id)
    return render(request, 'Bus/index.html', context)

# handle request for stop_data
def fetch_arrivals(request):
    if request.method == "POST":
        stop_pk = json.loads(request.body)
        data = get_arrivals(stop_pk)
        return JsonResponse(data)
    else:
        data = {
            "msg": "It worked!!",
        }
        return JsonResponse(data)


# handle parameters for predictions, returns whole journey prediction, currently hardcoded to use model for route 145_102 for all routes
def send_to_model(request):
    if request.method == "POST":
        model_params = json.loads(request.body)
        prediction = {}
        prediction['current_pred'] = get_prediction(model_params)
        return JsonResponse(prediction)
    else:
        data = {
            "msg": "It worked!!",
        }
        return JsonResponse(data)


# get next 5 arrivals for a given stop
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
    now = datetime.now().time()
    two_hours = datetime.now() + timedelta(hours=2)
    two_hours_from_now = two_hours.time()

    # This can probably be neater?
    # NEED TO ACCOUNT FOR TIMES PAST MIDNIGHT?
    # MySQL doesn't optimise nested queries very well, calling list() on queries forces execution
    query = StopTime.objects.filter(stop_id=stop_pk, arrival_time__gt=now, arrival_time__lt=two_hours_from_now)
    query4 = CalendarDate.objects.only('service_id').filter(date=today_str)
    query2 = Calendar.objects.filter(start_date__lt=today_str, end_date__gt=today_str).filter(**{today: 1}).exclude(
        service_id__in=query4)
    query3 = Trip.objects.filter(stoptime__in=list(query), service_id__in=list(query2))
    query = query.filter(trip_id__in=list(query3)).order_by('arrival_time')
    arrivals = StopTimeSerializer(query[:3], many=True)
    results['timetable'] = arrivals.data
    return results


def twitter(request):
    return render(request, 'Bus/twitter.html')
