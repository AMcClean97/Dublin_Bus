from django.http import JsonResponse
from django.shortcuts import render
from requests import get
from django.core import serializers
from datetime import datetime, date, timedelta
import json
from .models import Stop, Trip, Calendar, Route, StopTime, CalendarDate
from .bus_models import get_prediction
from .serializers import StopTimeSerializer
from .gtfs_realtime import is_trip_affected, update_real_time_json
from users.models import favourite
from django.conf import settings


# Create your views here.
def index(request):
    favourites_json = serializers.serialize("json", favourite.objects.filter(user_id= request.user.id))
    bus_stops_json = serializers.serialize("json", Stop.objects.all())
    context = {
        'bus_stops': bus_stops_json,
        'favourites' : favourites_json,
        'MAP_API_KEY': settings.MAP_API_KEY
    }
    if request.method == 'POST':
        favourite_id = request.POST.get('favourite_id')
        try:
            context['journey'] = favourite.objects.get(id=favourite_id)
        except:
            pass
   # update_real_time_json()
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
    stop_time_query = StopTime.objects.filter(stop_id=stop_pk, arrival_time__gt=now, arrival_time__lt=two_hours_from_now)
    calendar_date_query = CalendarDate.objects.only('service_id').filter(date=today_str)
    calendar_query = Calendar.objects.filter(start_date__lt=today_str, end_date__gt=today_str).filter(**{today: 1}).exclude(
        service_id__in=calendar_date_query)
    trip_query = Trip.objects.filter(stoptime__in=list(stop_time_query), service_id__in=list(calendar_query))
    stop_time = stop_time_query.filter(trip_id__in=list(trip_query)).order_by('arrival_time')

    delays = []
    trip = stop_time_query.values('trip_id')
    if len(trip) < 3:
        upper_range = len(trip)
    else:
        upper_range = 3
    for i in range (0, upper_range):
        delay = is_trip_affected(trip[i]['trip_id'], stop_pk)
        delays.append(delay)

    arrivals = StopTimeSerializer(stop_time_query[:3], many=True)
    results['timetable'] = arrivals.data
    results['delays'] = delays
    return results


def twitter(request):
    return render(request, 'Bus/twitter.html')
