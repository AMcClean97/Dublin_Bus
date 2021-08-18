from django.test import TestCase
from Bus.busmodels import get_current_weather, create_weather_df, get_future_weather, encode_time_features, \
    encode_features, get_stop_num, get_stop_num_lat_lng, find_route, read_json, get_proportion_of_route, \
    get_percentage_of_route_by_stops, get_prediction
from Bus.models import CurrentWeather, WeatherPrediction, Stop
from datetime import datetime
from pandas.testing import assert_frame_equal
import pandas as pd
from unittest import mock
import json


class TestBusmodels(TestCase):

    def setUp(self):
        curr_weather_obj = CurrentWeather(dt=1629104293, temp=15.89, feels_like=15.7, temp_min=12.6, temp_max=19.73,
                                          humidity=83, wind_speed=1.34, weather_main="Haze", weather_description="haze",
                                          weather_icon="50n")
        curr_weather_obj.save()
        future_weather_obj = WeatherPrediction(dt=1629104294, temp=16.89, feels_like=16.7, temp_min=6.6, temp_max=25.73,
                                               humidity=65, wind_speed=1.23, weather_main="Rain",
                                               weather_description="light rain", weather_icon="10d")
        future_weather_obj.save()
        stop = Stop(stop_id='8220DB000004', stop_name='Parnell Square West, stop 2', stop_lat=53.3522443611407,
                    stop_lon=-6.263723218918821)
        stop2 = Stop(stop_id='8220DB000757', stop_name='Donnybrook Village, stop 757', stop_lat=53.324081337159,
                     stop_lon=-6.239586509859331)
        stop.save()
        stop2.save()
        self.curr_weather_obj = curr_weather_obj
        self.future_weather_obj = future_weather_obj
        self.stop = stop
        self.stop2 = stop2
        return super().setUp()

    """========================= Testing functions that encode df for model ========================="""

    def test_create_weather_df(self):
        df = create_weather_df(self.curr_weather_obj)
        df_future = create_weather_df(self.future_weather_obj)
        self.assertEqual(df.columns.values.tolist(), df_future.columns.values.tolist())

    def test_encode_time_features(self):
        new_year = datetime(2021, 1, 1, 0, 1, 5)
        result = encode_time_features(new_year)
        self.assertEqual(result, [[65, 4, '2021-01-01', 0]])

    def test_encode_features(self):
        new_year = datetime(2021, 1, 1, 0, 1, 5)
        df = encode_features(new_year)
        test_data = {'actualtime_dep': 65, 'is_term': 0, 'is_holiday': 1, 'is_rush_hour': 0, 'weekday_1': 0,
                     'weekday_2': 0, 'weekday_3': 0, 'weekday_4': 1, 'weekday_5': 0, 'weekday_6': 0}
        test_df = pd.DataFrame([test_data])
        assert_frame_equal(df, test_df)

    """========================= Testing get_stop_num & get_stop_num_lat_lng ========================="""

    def test_get_stop_num(self):
        result_int_false = get_stop_num(self.stop.stop_lat, self.stop.stop_lon, self.stop.stop_name, integer=False)
        result_int_true = get_stop_num(self.stop.stop_lat, self.stop.stop_lon, self.stop.stop_name, integer=True)
        if len(result_int_false) != 0:
            self.assertIsInstance(result_int_false[0], str)
            self.assertRegex(self.stop.stop_name, result_int_false[0])
        if len(result_int_true) != 0:
            self.assertIsInstance(result_int_true[0], int)
        self.assertIsInstance(result_int_false, list)
        self.assertIsInstance(result_int_true, list)

    def test_get_stop_num_lat_lng(self):
        res_int_false = get_stop_num_lat_lng(self.stop.stop_lat, self.stop.stop_lon, integer=False)
        res_int_true = get_stop_num_lat_lng(self.stop.stop_lat, self.stop.stop_lon, integer=True)
        if len(res_int_false) != 0:
            self.assertIsInstance(res_int_false[0], str)
            self.assertRegex(self.stop.stop_name, res_int_false[0])
        if len(res_int_true) != 0:
            self.assertIsInstance(res_int_true[0], int)

    """========================= Testing find_route ========================="""

    def test_find_route(self):
        res = find_route(self.stop.stop_lat, self.stop.stop_lon, self.stop2.stop_lat, self.stop2.stop_lon,
                         self.stop2.stop_name, self.stop.stop_name, '46A')
        self.assertNotEqual(res, None)
        self.assertEqual(res, '46A_67')

    """========================= Testing read_json ========================="""

    def test_read_json(self):
        data = [{"stoppointid": 226, "mean_tt_rush_hour%": 0.0, "progrnumber": 1, "mean_tt%": 0.0},
                {"stoppointid": 228, "mean_tt_rush_hour%": 1.2144524647, "progrnumber": 2, "mean_tt%": 1.3419639823}]
        read_data = json.dumps(data)
        mock_open = mock.mock_open(read_data=read_data)
        with mock.patch('builtins.open', mock_open):
            result = read_json('filename')
        self.assertEqual(data, result)

    """========================= Testing proportion_of_route ========================="""

    def test_get_proportion_of_route_no_ave(self):
        mock_target = 'Bus.busmodels.get_percentage_of_route_by_stops'

        with mock.patch(mock_target, return_value=30):
            # test if we have no averages file will it deafult to get_proportion_of_route_by_stops?
            res_non_rush_hour = get_proportion_of_route('1111', 2, 3, self.stop.stop_lat, self.stop.stop_lon, self.stop2.stop_name, self.stop2.stop_lat, self.stop2.stop_lon)
            res_rush_hour = get_proportion_of_route('1111', 2, 3, self.stop.stop_lat, self.stop.stop_lon, self.stop2.stop_name, self.stop2.stop_lat, self.stop2.stop_lon, True)
            self.assertEqual(res_non_rush_hour, 30)
            self.assertEqual(res_rush_hour, 30)

    def test_get_proportion_of_route_with_ave(self):
        # test for when we do have historical averages
        # mock historical averages and patch check file exists
        mock_target = 'Bus.busmodels.check_file_exists'
        data = [{"stoppointid":381,"mean_tt_rush_hour%":0.0,"progrnumber":1,"mean_tt%":0.0},
                {"stoppointid":382,"mean_tt_rush_hour%":2,"progrnumber":2,"mean_tt%":1.5},
                {"stoppointid":3,"mean_tt_rush_hour%":2,"progrnumber":3,"mean_tt%":1.5},
                {"stoppointid":757,"mean_tt_rush_hour%":2,"progrnumber":4,"mean_tt%":1.5}]
        stop_num_mock_target = 'Bus.busmodels.get_stop_num'
        percentage_by_stops_mock = 'Bus.busmodels.get_percentage_of_route_by_stops'
        with mock.patch(mock_target, return_value=data):
            with mock.patch(stop_num_mock_target, side_effect=[[381], [757], [381], [757], [381], []]):
                with mock.patch(percentage_by_stops_mock, return_value=None):
                    res = get_proportion_of_route('1111', self.stop.stop_name, 3, self.stop.stop_lat, self.stop.stop_lon, self.stop2.stop_name, self.stop2.stop_lat, self.stop2.stop_lon)
                    res_rush_hour = get_proportion_of_route('1111', self.stop.stop_name, 3, self.stop.stop_lat, self.stop.stop_lon, self.stop2.stop_name, self.stop2.stop_lat, self.stop2.stop_lon, True)
                    res_out_of_range = get_proportion_of_route('1111', self.stop.stop_name, 4, self.stop.stop_lat, self.stop.stop_lon, self.stop2.stop_name, self.stop2.stop_lat, self.stop2.stop_lon, True)
                    self.assertEqual(res, 4.5 / 100)
                    self.assertEqual(res_rush_hour, 6 / 100)
                    self.assertEqual(res_out_of_range, None)

                """========================= Testing get_prediction ========================="""

    def test_get_prediction_failure(self):
        # test it returns Google prediction in case of failure
        mock_target = 'Bus.busmodels.find_route'
        mock_API_response = {'departure_time': '2021-08-17T12:28:28.000Z', 'line': '27',
                             'departure_stop': 'Eden Quay, stop 298', 'arrival_stop': 'Portland Row', 'num_stops': 3,
                             'dep_stop_lat': 53.3481866, 'dep_stop_lng': -6.2564106, 'arr_stop_lat': 53.353535,
                             'arr_stop_lng': -6.248092, 'google_pred': 228}

        with mock.patch(mock_target, return_value=None):
            res = get_prediction(mock_API_response)
            self.assertEqual(res, mock_API_response['google_pred'])

    def test_get_prediction(self):
        data = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
        df1 = pd.DataFrame({'actualtime_dep': [1],
            'temp': [2],
            'wind_speed': [3],
            'humidity': [4],
            'weather_main_precipitation':[5],
            'is_term':[6],
            'is_holiday':[7],
            'is_rush_hour':[8],
            'weekday_1':[9],
            'weekday_2':[10],
            'weekday_3':[11],
            'weekday_4':[12],
            'weekday_5':[13],
            'weekday_6':[14]})
        df2 = pd.DataFrame()
        with mock.patch('Bus.busmodels.find_route', return_value='22'):
            with mock.patch('Bus.busmodels.change_timezone', return_value=datetime.now()):
                with mock.patch('Bus.busmodels.encode_features', return_value=df1):
                    with mock.patch('Bus.busmodels.get_current_weather', return_value=df2):
                        with mock.patch('Bus.busmodels.get_future_weather', return_value=df2):
                            with mock.patch('Bus.busmodels.open_model_and_predict', return_value=120):
                                with mock.patch('Bus.busmodels.is_rush_hour_or_not', return_value=.50):
                                    res = get_prediction({'departure_time': '2021-08-17T12:28:28.000Z', 'line': '27',
                                                          'departure_stop': 'Eden Quay, stop 298',
                                                          'arrival_stop': 'Portland Row', 'num_stops': 3,
                                                          'dep_stop_lat': 53.3481866, 'dep_stop_lng': -6.2564106,
                                                          'arr_stop_lat': 53.353535, 'arr_stop_lng': -6.248092,
                                                          'google_pred': 228})
                                    expected_res = json.dumps(str(1.0))
                                    self.assertEqual(res, expected_res)
