from django.test import TestCase
from Bus.gtfsrealtime import get_arrivals, is_trip_affected
from unittest import mock


class TestGtfsrealtime(TestCase):

    """========================= Testing getArrivals ========================="""


    def test_get_arrivals_success(self):
        result = get_arrivals('8220DB000002')
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['delays'], list)
        self.assertLess(len(result['delays']), 4)
        self.assertLess(len(result['delays']), 4)

    """========================= Testing getArrivals ========================="""
    def test_is_trip_affected(self):
        mock_target = 'Bus.gtfsrealtime.read_real_time'
        with mock.patch(mock_target, return_value={"header": {"gtfs_realtime_version": "1.0", "timestamp": 1628859302}, "entity": [{"id": "2720023.y100v.10-64-e19-1.158.I", "trip_update": {"trip": {"trip_id": "2720023.y100v.10-64-e19-1.158.I", "start_time": "08:45:00", "start_date": "20210813", "schedule_relationship": "SCHEDULED", "route_id": "10-64-e19-1"}, "stop_time_update": [{"stop_sequence": 1, "departure": {"delay": 0}, "stop_id": "8460B5550401", "schedule_relationship": "SCHEDULED"}, {"stop_sequence": 2, "arrival": {"delay": 120}, "departure": {"delay": 120}, "stop_id": "8470B551411", "schedule_relationship": "SCHEDULED"}]}}]}):
            res = is_trip_affected("2720023.y100v.10-64-e19-1.158.I", "8470B551411")
            self.assertEqual(res, 120)



    def test_is_trip_affected_failure(self):
        mock_target = 'Bus.gtfsrealtime.read_real_time'
        with mock.patch(mock_target, return_value={"Invalid API"}):
            res = is_trip_affected('1121.y1007.60-27-d12-1.154.O', '8220DB001934')
            self.assertEqual(res, 0)
