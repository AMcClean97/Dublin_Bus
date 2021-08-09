import pickle
import pandas as pd
import xgboost
import sklearn
from .models import CurrentWeather, Stop
from datetime import datetime, date
import holidays
import numpy as np
import json
import os.path


def get_current_weather():
    """ retrieves current weather info
        formats for model and returns dataframe"""
    current_weather = CurrentWeather.objects.first()
    data = [[current_weather.temp, current_weather.wind_speed, current_weather.weather_main, current_weather.humidity]]
    df = pd.DataFrame(data, columns=['temp', 'wind_speed', 'weather_main', 'humidity'])
    df['weather_main_precipitation'] = df['weather_main'].apply(
        lambda x: 1 if x in ['Rain', 'Drizzle', 'Snow'] else 0)
    df.drop('weather_main', axis=1, inplace=True)
    return df


def encode_features(departure_time):
    """encodes actualtime_dep, weekday, term, holiday & rush hour features for the model
    returns a dataframe"""
    #get actualtime_dep in seconds
    split_date = departure_time.split('T')
    time = split_date[1][:8]
    time_in_seconds = (int(str(time[0:2])) * 60 * 60) + (int(str(time[3:5])) * 60) + (int(str(time[6:8])))

    #parse as datetime object to get weekday and additional features
    string_date = ' '.join(split_date)[:19]
    datetime_obj = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')
    #get day of week, monday=0, sunday=6
    day_of_week = datetime_obj.date().weekday()
    date = datetime_obj.date().strftime('%Y-%m-%d')
    hour = datetime_obj.hour


    data = [[time_in_seconds, day_of_week, date, hour]]
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
    "adds term time flag if date of departure falls within school term, need to be manually changed, current dates are for 2021/22 school year "
    df['is_term'] = np.where(
        (df['date'] > '2021-09-01') & (df['date'] < '2021-10-25') | (df['date'] > '2021-10-29') & (df['date'] < '2021-12-22') | (df['date'] > '2022-01-06') & (df['date'] < '2022-02-15') | (df['date'] > '2022-02-19') & (df['date'] <= '2022-03-26') | (df['date'] >= '2022-04-12') & (df['date'] <= '2022-07-01'),  1, 0)
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
    rush_hours = [7, 8, 9, 16, 17, 18]
    weekdays = [1, 2, 3, 4, 5]

    conditions = [
        df['weekday'].isin(weekdays) & df['hour'].isin(rush_hours)
    ]

    choices = [1]
    df['is_rush_hour'] = np.select(conditions, choices, default=0)

    return df


def get_proportion_of_route(route, departure_stop, num_stops, dep_stop_lat, dep_stop_lng, rush_hour=False):
    """import json file with historical averages for relevant line """
    if os.path.exists('json/avg' + route + '.json'):
        with open('json/avg' + route + '.json') as f:
            historical_averages = json.load(f)

            stop_num_list = get_stop_num(dep_stop_lat, dep_stop_lng, departure_stop)
            if len(stop_num_list) == 0:
                return None

            ## NOT THE MOST EFFICIENT WAY OF DOING THIS? REFACTOR IF TIME? GOING TO REFACTOR THIS
            for i in range(0, len(stop_num_list)):
                for j in range(0, len(historical_averages)):
                    if historical_averages[j]['stoppointid'] == int(stop_num_list[i]):
                        # MAYBE SLICE THE LIST BASED ON STOPIDS instead???
                        if rush_hour:
                            try:
                                proportion_total = sum([historical_averages[k]['mean_tt_rush_hour%'] for k in range(j+1, j+num_stops+1)])
                            except (IndexError, TypeError) as e:
                                print(e)
                                return None
                        else:
                            try:
                                proportion_total = sum([historical_averages[k]['mean_tt%'] for k in range(j+1, j+num_stops+1)])
                            except (IndexError, TypeError) as e:
                                print(e)
                                return None
                        return proportion_total / 100
    else:
        # calculate proportion of route by number of stops, read in routes csv
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
    ##truncate lat & lng to 3 decimal places for matching (Google and GTFS data don't give the exact same lat/lng for stops, but are typically the same within 3 decimal places
    stop_lat = float(int(stop_lat * (10**3))/10**3)
    stop_lng = float(int(stop_lng * (10**3))/10**3)
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

    #query stops model (GTFS data in DB) for matches with Google response stop name
    start_stop_query = Stop.objects.filter(stop_name__icontains=stop_name).values('stop_name')
    #add matches to a list
    stop_num_list = []
    for i in range(0, len(start_stop_query)):
        current = start_stop_query[i]['stop_name']
        stop_num = [int(j) for j in current.split() if j.isdigit()]
        stop_num_str = ''.join([str(elem) for elem in stop_num])
        if integer:
            stop_num_list.append(int(stop_num_str))
        else:
            stop_num_list.append(stop_num_str)

    ## If we fail to match stop by name, we attempt to match by lat/lng
    if len(stop_num_list) == 0:
        stop_num_list = get_stop_num_lat_lng(stop_lat, stop_lng)

    return stop_num_list


def find_route(arr_stop_lat, arr_stop_lng, dep_stop_lat, dep_stop_lng, departure_stop, arrival_stop, line):
    """takes line, departure stop name/lat/lng, arrival stop name/lat/lng from Google API response and finds a matching Dublin Bus route"""

    #first retrieve relevant bus stop numbers by matching those in database (GTFS) with the string returned by Google
    potential_departure_stops = get_stop_num(dep_stop_lat, dep_stop_lng, departure_stop, True)
    potential_arrival_stops = get_stop_num(arr_stop_lat, arr_stop_lng, arrival_stop, True)


    # SAVE CSV AGAIN WITHOUT INDEX, read in routes CSV
    df = pd.read_csv('df_routes.csv')

    # retrieve records for a particular line
    df = df.loc[(df['lineid'] == line)]

    #This finds the route by checking which subroute for a line contains both the departure and arrival stops given by Google
    #Need to test this to ensure there aren't lines where both routes share 2 stops?
    filter1 = df['stoppointid'].isin(potential_departure_stops)
    filter2 = df['stoppointid'].isin(potential_arrival_stops)
    df = df[filter1 | filter2]
    route = df['routeid'].tolist()

    if len(route) == 0:
        route = None
    else:
        route = max(route, key=route.count)
        return route

def get_prediction(details):
    """takes journey planner input / Google response and returns predicted travel time """
    ## find out which route, and therefore which model is required
    route = find_route(details['arr_stop_lat'], details['arr_stop_lng'], details['dep_stop_lat'], details['dep_stop_lng'], details['departure_stop'], details['arrival_stop'], details['line'])

    #if we don't have a model or matching route, return Google's duration prediction instead
    if route == None:
        predicted_tt = details['google_pred']

    else:
        ## encode features for our model
        departure_time = details['departure_time']
        df_bus = encode_features(departure_time)
        df_weather = get_current_weather()
        df_all = pd.concat([df_bus, df_weather], axis=1)

        # load the model that corresponds to the route
        f = open('predictive_models/' + route + '_XG_model.sav', 'rb')
        model = pickle.load(f)

        # make predictions
        predicted_tt = model.predict(df_all)
        if df_all['is_rush_hour'].item():
            proportion_of_route = get_proportion_of_route(route, details['departure_stop'], details['num_stops'], details['dep_stop_lat'], details['dep_stop_lng'], rush_hour = True)
        else:
            proportion_of_route = get_proportion_of_route(route, details['departure_stop'], details['num_stops'],
                                                          details['dep_stop_lat'], details['dep_stop_lng'])

        if proportion_of_route is None:
            #In case proportion_of_route_fails, i.e. if the arrival or departure stop was not part of the route in 2018
            predicted_tt = details['google_pred']
        else:
            partial_prediction = proportion_of_route * predicted_tt
            predicted_tt_mins = partial_prediction / 60
            predicted_tt = json.dumps(str(predicted_tt_mins))

    return predicted_tt

