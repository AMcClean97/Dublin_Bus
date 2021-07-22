import pickle
import pandas as pd
import xgboost
import sklearn
from .models import CurrentWeather, Stop
from datetime import datetime, date
import holidays
import numpy as np
import json

def get_current_weather():
    """ retrieves current weather info
        formats for model and returns dataframe"""
    current_weather = CurrentWeather.objects.first()
    data = [[current_weather.temp, current_weather.wind_speed, current_weather.weather_main]]
    df = pd.DataFrame(data, columns=['temp', 'wind_speed', 'weather_main'])
    df['weather_main_Clouds'] = df['weather_main'].apply(lambda x: 1 if x in ['Clouds'] else 0)
    df['weather_main_Drizzle'] = df['weather_main'].apply(lambda x: 1 if x in ['Drizzle'] else 0)
    df['weather_main_Fog'] = df['weather_main'].apply(lambda x: 1 if x in ['Fog'] else 0)
    df['weather_main_Mist'] = df['weather_main'].apply(lambda x: 1 if x in ['Mist'] else 0)
    df['weather_main_Rain'] = df['weather_main'].apply(lambda x: 1 if x in ['Rain'] else 0)
    df['weather_main_Smoke'] = df['weather_main'].apply(lambda x: 1 if x in ['Smoke'] else 0)
    df['weather_main_Snow'] = df['weather_main'].apply(lambda x: 1 if x in ['Snow'] else 0)
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
    "adds term time flag if date of departure falls within school term"
    df['is_term'] = np.where(
        (df['date'] > '2018-01-07') & (df['date'] <= '2018-02-12') | (df['date'] > '2018-02-16') & (
                    df['date'] <= '2018-03-23') | (df['date'] > '2018-08-04') & (df['date'] < '2018-05-31') | (
                    df['date'] > '2018-09-02') & (df['date'] < '2018-10-29') | (df['date'] > '2018-11-05') & (
                    df['date'] >= '2018-12-21'), 1, 0)
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


def get_proportion_of_route(line, departure_stop, num_stops):
    """import json file with historical averages for relevant line """

    ### THIS IS STILL A WORK IN PROGRESS, NEED TO FIGURE OUT HOW TO RETRIEVE RIGHT JSON FILE? USE LINE and possibly direction?
    with open('145_102.json') as f:
        historical_averages = json.load(f)
        print(historical_averages)

    ## GET STOP NUMBER FROM STOP OBJECT
    start_stop_query = Stop.objects.filter(stop_name__contains=departure_stop).values('stop_name')
    stop_num_list = []
    for i in range(0, len(start_stop_query)):
        current = start_stop_query[i]['stop_name']
        stop_num = [int(j) for j in current.split() if j.isdigit()]
        stop_num_str = ''.join([str(elem) for elem in stop_num])
        stop_num_list.append(stop_num_str)

    ## NOT THE MOST EFFICIENT WAY OF DOING THIS? REFACTOR IF TIME?
    for i in range(0, len(stop_num_list)):
        for j in range(0, len(historical_averages)):
            if historical_averages[j]['stoppointid'] == int(stop_num_list[i]):
                proportion_total = sum([historical_averages[k]['mean_tt_%'] for k in range(j+1, j+num_stops+1)])
                print(proportion_total)
                return proportion_total / 100





def get_prediction(details):
    print(details)
    line = details['line']
    departure_stop = details['departure_stop']
    num_stops = details['num_stops']
    proportion_of_route = get_proportion_of_route(line, departure_stop, num_stops)
    print(proportion_of_route)
    departure_time = details['departure_time']
    df_bus = encode_features(departure_time)
    df_weather = get_current_weather()
    df_all = pd.concat([df_bus, df_weather], axis=1)
    print(df_all)
    # load the model
    f = open('145_102.sav', 'rb')
    model = pickle.load(f)

    # make predictions
    predicted_tt = model.predict(df_all)
    partial_prediction = proportion_of_route * predicted_tt
    prediction = json.dumps(str(partial_prediction))
    return prediction

