import json
import requests
from django.conf import settings


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
