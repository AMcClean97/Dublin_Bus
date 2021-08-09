import json
import requests
import threading
from django.conf import settings

real_time_data_update_frequency = 300


def update_real_time_json():
    """scrapes real time GTFS data and writes to json file"""
    headers = {'x-api-key': settings.GTFS_API_KEY, 'Cache-control': 'no-cache'}
    ploads = {'format': 'json'}

    try:
        r = requests.get('https://gtfsr.transportforireland.ie/v1', headers=headers, params=ploads).json()
    except Exception as e:
        print(e)

    # write data to json file
    with open('json/real_time_data.json', 'w') as f:
        json.dump(r, f)

    # starts timer object again so it will run again in 5 mins
    start_thread()


def start_thread():
    """Creates and starts a timer object that will run the update_real_time_json() function
    The frequency with which the timer is scheduled is controlled by the real_time_data_update_frequency variable
    """
    update_data_thread = threading.Timer(real_time_data_update_frequency, update_real_time_json)
    update_data_thread.daemon = True
    update_data_thread.start()


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
