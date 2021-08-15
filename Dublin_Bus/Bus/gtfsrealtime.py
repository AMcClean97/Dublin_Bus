import json
import requests
from datetime import datetime, date, timedelta
from django.conf import settings
from .serializers import StopTimeSerializer
from .models import Stop, Trip, Calendar, Route, StopTime, CalendarDate



def is_trip_affected(tripid, stopid):
    """when a user clicks on a marker, sends 3 next timetabled arrivals according to GTFS and returns any delays
    reported by GTFS -R """
    with open('json/real_time_data.json') as json_file:
        data = json.load(json_file)
        if 'entity' in data:
            for i in range(0, len(data['entity'])):
                if data['entity'][i]["id"] == tripid:
                    stop_time_update = data['entity'][i]["trip_update"]['stop_time_update']
                    for j in range(0, len(stop_time_update)):
                        if stop_time_update[j]['stop_id'] == stopid:
                            if 'arrival' in stop_time_update[j]['stop_id']:
                                delay_in_seconds = stop_time_update[j]['arrival']['delay']
                                return delay_in_seconds
                            else:
                                if 'departure' in stop_time_update[j]['stop_id']:
                                    delay_in_seconds = stop_time_update[j]['departure']['delay']
                                    return delay_in_seconds
        # if no delay or matching entry in GTFS -R, return 0
        return 0


def get_arrivals(stop_pk):
    """ returns next 3 arrivals for a given stop """
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
    trip = stop_time.values('trip_id')
    if len(trip) < 3:
        upper_range = len(trip)
    else:
        upper_range = 3
    for i in range (0, upper_range):
        delay = is_trip_affected(trip[i]['trip_id'], stop_pk)
        delays.append(delay)

    arrivals = StopTimeSerializer(stop_time[:upper_range], many=True)
    results['timetable'] = arrivals.data
    print(type(arrivals))
    print(type(arrivals.data))
    results['delays'] = delays
    return results