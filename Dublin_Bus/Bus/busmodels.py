import pickle
import pandas as pd
import xgboost
import sklearn
from .models import CurrentWeather, Stop, WeatherPrediction
from datetime import datetime, date, timezone
import holidays
import numpy as np
import json
import os.path
from dateparser import parse
import pytz


def get_current_weather():
    """ retrieves current weather info"""
    current_weather = CurrentWeather.objects.first()
    return create_weather_df(current_weather)


def create_weather_df(weather_object):
    """ creates dataframe from weather object """
    data = [[weather_object.temp, weather_object.wind_speed, weather_object.weather_main, weather_object.humidity]]
    df = pd.DataFrame(data, columns=['temp', 'wind_speed', 'weather_main', 'humidity'])
    df['weather_main_precipitation'] = df['weather_main'].apply(
        lambda x: 1 if x in ['Rain', 'Drizzle', 'Snow'] else 0)
    df.drop('weather_main', axis=1, inplace=True)
    return df


def get_future_weather(departure_time):
    """ retrieves future weather info"""
    timestamp_obj = departure_time.timestamp()

    # get nearest matching entry by timestamp, defaulting to nearest timestamp hour behind
    try:
        future_weather = WeatherPrediction.objects.filter(dt__lt=timestamp_obj).order_by('-dt')[0]
        return create_weather_df(future_weather)
    except IndexError as e:
        print(e)


def encode_time_features(departure_time):
    # get time in seconds
    midnight = departure_time.replace(hour=0, minute=0, second=0, microsecond=0)
    time_in_seconds = (departure_time - midnight).seconds

    # get day of week, monday=0, sunday=6
    day_of_week = departure_time.date().weekday()
    date = departure_time.date().strftime('%Y-%m-%d')
    hour = departure_time.hour

    data = [[time_in_seconds, day_of_week, date, hour]]
    return data


def encode_features(departure_time):
    """encodes actualtime_dep, weekday, term, holiday & rush hour features for the model
    returns a dataframe"""

    data = encode_time_features(departure_time)
    df = pd.DataFrame(data, columns=['actualtime_dep', 'weekday', 'date', 'hour'])

    df = term_flag(df)
    df = holiday_flag(df)
    df = rush_hour_flag(df)

    df['weekday_1'] = df['weekday'].apply(lambda x: 1 if x in [1] else 0)
    df['weekday_2'] = df['weekday'].apply(lambda x: 1 if x in [2] else 0)
    df['weekday_3'] = df['weekday'].apply(lambda x: 1 if x in [3] else 0)
    df['weekday_4'] = df['weekday'].apply(lambda x: 1 if x in [4] else 0)
    df['weekday_5'] = df['weekday'].apply(lambda x: 1 if x in [5] else 0)
    df['weekday_6'] = df['weekday'].apply(lambda x: 1 if x in [6] else 0)
    df.drop(['weekday', 'date', 'hour'], axis=1, inplace=True)
    return df


def term_flag(df):
    """ adds term time flag if date of departure falls within school term, need to be manually changed, current dates
    are for 2021/22 school year """
    df['is_term'] = np.where(
        (df['date'] > '2021-09-01') & (df['date'] < '2021-10-25') | (df['date'] > '2021-10-29') & (
                df['date'] < '2021-12-22') | (df['date'] > '2022-01-06') & (df['date'] < '2022-02-15') | (
                df['date'] > '2022-02-19') & (df['date'] <= '2022-03-26') | (df['date'] >= '2022-04-12') & (
                df['date'] <= '2022-07-01'), 1, 0)
    return df


# adapted from here https://towardsdatascience.com/5-minute-guide-to-detecting-holidays-in-python-c270f8479387
def holiday_flag(df):
    """adds holiday flag if date of departure is public holiday"""
    ireland_holidays = []

    for date in holidays.Ireland(years=2021).items():
        ireland_holidays.append(str(date[0]))

    df['is_holiday'] = [1 if str(val).split()[0] in ireland_holidays else 0 for val in df['date']]
    return df


def rush_hour_flag(df):
    """adds rush hour flag if time of departure is during rush hour"""
    rush_hours = [7, 8, 16, 17, 18]
    weekdays = [1, 2, 3, 4, 5]

    conditions = [
        df['weekday'].isin(weekdays) & df['hour'].isin(rush_hours)
    ]

    choices = [1]
    df['is_rush_hour'] = np.select(conditions, choices, default=0)

    return df


def read_json(filename):
    with open(filename) as f:
        historical_averages = json.load(f)
    return historical_averages


def check_file_exists(filename):
    if os.path.exists(filename):
        historical_averages = read_json(filename)
        return historical_averages
    else:
        return None


def get_proportion_of_route(route, departure_stop, num_stops, dep_stop_lat, dep_stop_lng, arrival_stop, arr_stop_lat, arr_stop_lng, rush_hour=False):
    """import json file with historical averages for relevant line """
    filename = 'json/avg' + route + '.json'
    historical_averages = check_file_exists(filename)
    if historical_averages is not None:
        # find departure and arrival stop and slice list of historical averages by stops
        potential_departure_stops = get_stop_num(dep_stop_lat, dep_stop_lng, departure_stop, True)
        potential_arrival_stops = get_stop_num(arr_stop_lat, arr_stop_lng, arrival_stop, True)

        if len(potential_departure_stops) == 0 or len(potential_arrival_stops) == 0:
            # calculate proportion of route by number of stops instead
            proportion_total = get_percentage_of_route_by_stops(route, num_stops)
            return proportion_total
        # find index of list for start and end stop
        for i in range(0, len(potential_departure_stops)):
            start_index = next((index for (index, d) in enumerate(historical_averages) if d["stoppointid"] == potential_departure_stops[i]), None)
            if start_index is not None:
                break
        for i in range(0, len(potential_arrival_stops)):
            end_index = next((index for (index, d) in enumerate(historical_averages) if
                    d["stoppointid"] == potential_arrival_stops[i]), None)
            if end_index is not None:
                break

        if start_index is not None and end_index is not None:
            historical_averages_slice = historical_averages[start_index +1: end_index+1]
            if rush_hour:
                proportion_total = sum(item['mean_tt_rush_hour%'] for item in historical_averages_slice)
            else:
                proportion_total = sum(item['mean_tt%'] for item in historical_averages_slice)

            return proportion_total / 100
        else:
            # calculate proportion of route by stops instead
            proportion_total = get_percentage_of_route_by_stops(route, num_stops)
            return proportion_total

    else:
        proportion_total = get_percentage_of_route_by_stops(route, num_stops)
        # calculate proportion of route by number of stops instead
        return proportion_total


def get_percentage_of_route_by_stops(route, num_stops):
    df = pd.read_csv('df_routes.csv')
    # retrieve records for a particular line
    df = df.loc[(df['routeid'] == route)]
    total_stops = (len(df))
    proportion_total = num_stops / total_stops
    return proportion_total


def get_stop_num_lat_lng(stop_lat, stop_lng, integer=False):
    """function takes stop lat and lng and returns stoppoint id/number match

    called if matching by name doesn't work. If integer flag=True, returns integer otherwise returns string
"""
    # truncate lat & lng to 3 decimal places for matching (Google and GTFS data don't give the exact same lat/lng for
    # stops, but are typically the same within 3 decimal places
    stop_lat = float(int(stop_lat * (10 ** 3)) / 10 ** 3)
    stop_lng = float(int(stop_lng * (10 ** 3)) / 10 ** 3)
    stop_query = Stop.objects.filter(stop_lat__startswith=stop_lat, stop_lon__startswith=stop_lng).values('stop_name')

    stop_num_list = []
    for i in range(0, len(stop_query)):
        current = stop_query[i]['stop_name']
        stop_num = [int(j) for j in current.split() if j.isdigit()]
        stop_num_str = ''.join([str(elem) for elem in stop_num])
        if integer:
            stop_num_list.append(int(stop_num_str))
        else:
            stop_num_list.append(stop_num_str)

    return stop_num_list


def get_stop_num(stop_lat, stop_lng, stop_name, integer=False):
    """function takes stop name string and matches it up to return potential list of stoppoint id/number matches
    if integer flag is true, return stop ids as list of ints, otherwise returns as list of strings"""

    # query stops model (GTFS data in DB) for matches with Google response stop name
    start_stop_query = Stop.objects.filter(stop_name__icontains=stop_name).values('stop_name')
    # add matches to a list
    stop_num_list = []
    for i in range(0, len(start_stop_query)):
        current = start_stop_query[i]['stop_name']
        stop_num = [int(j) for j in current.split() if j.isdigit()]
        stop_num_str = ''.join([str(elem) for elem in stop_num])
        if integer:
            stop_num_list.append(int(stop_num_str))
        else:
            stop_num_list.append(stop_num_str)

    # If we fail to match stop by name, we attempt to match by lat/lng
    if len(stop_num_list) == 0:
        stop_num_list = get_stop_num_lat_lng(stop_lat, stop_lng)

    return stop_num_list


def find_route(arr_stop_lat, arr_stop_lng, dep_stop_lat, dep_stop_lng, departure_stop, arrival_stop, line):
    """takes line, departure stop name/lat/lng, arrival stop name/lat/lng from Google API response and finds a
    matching Dublin Bus route """

    # first retrieve relevant bus stop numbers by matching those in database (GTFS) with the string returned by Google
    potential_departure_stops = get_stop_num(dep_stop_lat, dep_stop_lng, departure_stop, True)
    potential_arrival_stops = get_stop_num(arr_stop_lat, arr_stop_lng, arrival_stop, True)

    # SAVE CSV AGAIN WITHOUT INDEX, read in routes CSV
    df = pd.read_csv('df_routes.csv')

    # retrieve records for a particular line
    df = df.loc[(df['lineid'] == line)]

    # This finds the route by checking which subroute for a line contains both the departure and arrival stops given
    # by Google
    filter1 = df['stoppointid'].isin(potential_departure_stops)
    filter2 = df['stoppointid'].isin(potential_arrival_stops)
    df = df[filter1 | filter2]
    route = df['routeid'].tolist()

    if len(route) == 0:
        route = None
    else:
        route = max(route, key=route.count)
        return route


def change_timezone(departure_time):
    """time sent from frontend is UTC, change timezone to Dublin"""
    dublin = pytz.timezone("Europe/Dublin")
    dublin_time = parse(departure_time)
    departure_time = dublin_time.astimezone(dublin)
    return departure_time


def open_model_and_predict(route, df_all):
    # load the model that corresponds to the route
    f = open('predictive_models/' + route + '_XG_model.sav', 'rb')
    model = pickle.load(f)
    # make predictions
    predicted_tt = model.predict(df_all)
    return predicted_tt


def is_rush_hour_or_not(route, details, df_all):
    if df_all['is_rush_hour'].iat[0]:
        proportion_of_route = get_proportion_of_route(route, details['departure_stop'], details['num_stops'],
                                                      details['dep_stop_lat'], details['dep_stop_lng'], details['arrival_stop'], details['arr_stop_lat'], details['arr_stop_lng'], rush_hour=True)
    else:
        proportion_of_route = get_proportion_of_route(route, details['departure_stop'], details['num_stops'],
                                                      details['dep_stop_lat'], details['dep_stop_lng'], details['arrival_stop'], details['arr_stop_lat'], details['arr_stop_lng'])
    return proportion_of_route


def get_prediction(details):
    """takes journey planner input / Google response and returns predicted travel time """
    # find out which route, and therefore which model is required
    route = find_route(details['arr_stop_lat'], details['arr_stop_lng'], details['dep_stop_lat'],
                       details['dep_stop_lng'], details['departure_stop'], details['arrival_stop'], details['line'])

    # if we don't have a model or matching route, return Google's duration prediction instead
    if route is None:
        predicted_tt = details['google_pred']

    else:
        # change timezone from UTC to Irish
        departure_time = change_timezone(details['departure_time'])
        # encode features for our model
        df_bus = encode_features(departure_time)

        # if departure date and hour is the same, we get the current weather, else we get weather forecast for that time
        now = datetime.now()
        if departure_time.date() == now.date() and departure_time.hour == now.hour:
            df_weather = get_current_weather()

        else:
            df_weather = get_future_weather(departure_time)

        df_all = pd.concat([df_bus, df_weather], axis=1)

        predicted_tt = open_model_and_predict(route, df_all)

        proportion_of_route = is_rush_hour_or_not(route, details, df_all)

        if proportion_of_route is None:
            # In case proportion_of_route_fails, i.e. if the arrival or departure stop was not part of the route in 2018
            predicted_tt = details['google_pred']
        else:
            partial_prediction = proportion_of_route * predicted_tt
            predicted_tt_mins = partial_prediction / 60
            predicted_tt = json.dumps(str(predicted_tt_mins))

    return predicted_tt
