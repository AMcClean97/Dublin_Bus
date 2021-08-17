from django.http import JsonResponse
from django.shortcuts import render, redirect
from requests import get
from django.core import serializers
import json
from .models import Stop, WeatherPrediction
from .busmodels import get_prediction
from .gtfsrealtime import get_arrivals
from users.models import favourite
from django.conf import settings
from django.db.models import Max


# Create your views here.
def index(request):
    favourites_json = serializers.serialize("json", favourite.objects.filter(user_id=request.user.id))
    bus_stops_json = serializers.serialize("json", Stop.objects.all())
    lastDate = WeatherPrediction.objects.aggregate(Max('dt'))
    context = {
        'bus_stops': bus_stops_json,
        'favourites': favourites_json,
        'last_time': lastDate['dt__max'],
        'MAP_API_KEY': settings.MAP_API_KEY
    }
    if request.method == 'POST':
        favourite_id = request.POST.get('favourite_id')
        try:
            context['journey'] = favourite.objects.get(id=favourite_id)
        except:
            pass
    return render(request, 'Bus/index.html', context)


# handle request for stop_data
def fetch_arrivals(request):
    if request.method == "POST":
        stop_pk = json.loads(request.body)
        data = get_arrivals(stop_pk)
        return JsonResponse(data)
    else:
        return redirect('index')


# handle parameters for predictions
def send_to_model(request):
    if request.method == "POST":
        model_params = json.loads(request.body)
        prediction = {}
        prediction['current_pred'] = get_prediction(model_params)
        return JsonResponse(prediction)
    else:
        return redirect('index')


def twitter(request):
    return render(request, 'Bus/twitter.html')
