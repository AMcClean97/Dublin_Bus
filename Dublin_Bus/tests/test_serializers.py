from django.test import TestCase
from Bus.models import StopTime, Trip, Stop, Route, Calendar
from Bus.serializers import StopTimeSerializer


class TestSerializers(TestCase):

    """========================= Testing serializer ========================="""

    def setUp(self):

        self.calendar = Calendar(service_id='y1008', monday=1, tuesday=0, wednesday=0, thursday=0, friday=0, saturday=0, sunday=1, start_date=20210725, end_date=20211016)
        self.calendar.save()
        self.route = Route(route_id='60-38A-d12-1', agency_id='978', route_short_name='38a', route_long_name=None, route_type=3)
        self.route.save()
        self.trip = Trip(route_id=self.route, service_id=self.calendar, trip_id='14773.y1008.60-38A-d12-1.179.O', shape_id='60-38A-d12-1.179.O', trip_headsign='Burlington Road (Mespil Road) - Damastown Drive', direction_id=0)
        self.trip.save()
        self.stop = Stop(stop_id='8220DB000004', stop_name='Parnell Square West, stop 2', stop_lat=53.3522443611407,stop_lon=-6.263723218918821)
        self.stop.save()
        self.stopTime = StopTime(id=1, trip_id=self.trip, arrival_time='17:47:37',stop_id=self.stop, stop_sequence=10, stop_headsign='Damastown')
        self.stopTime.save()

        self.calendar1 = Calendar(service_id='y1007', monday=1, tuesday=0, wednesday=0, thursday=0, friday=0, saturday=0, sunday=1, start_date=20210725, end_date=20211016)
        self.calendar1.save()
        self.route1 = Route(route_id='60-38A-d12-2', agency_id='978', route_short_name='38a', route_long_name=None, route_type=3)
        self.route1.save()
        self.trip1 = Trip(route_id=self.route1, service_id=self.calendar1 , trip_id='14773.y1008.60-38A-d12-1.179.O1', shape_id='60-38A-d12-1.179.O', trip_headsign='Burlington Road (Mespil Road) - Damastown Drive',direction_id=0)
        self.trip1.save()
        self.stop1 = Stop(stop_id='8220DB000003', stop_name='Parnell Square West, stop 2', stop_lat=53.3522443611407,stop_lon=-6.263723218918821)
        self.stop1.save()
        self.stopTime1 = StopTime(id=2, trip_id=self.trip1, arrival_time='17:47:37', stop_id=self.stop1, stop_sequence=10,stop_headsign='Damastown')
        self.stopTime1.save()

        self.serializer = StopTimeSerializer([self.stopTime1, self.stopTime], many=True)
        return super().setUp()

    #check serializer contains correct fields both at outer and nested layers
    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data[0].keys(), ['arrival_time', 'stop_headsign', 'stop_id', 'stop_sequence', 'trip_id'])

    #check field content is what it should be at all nested layers
    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data[0]['arrival_time'], '17:47:37')
        self.assertEqual(data[1]['stop_id']['stop_id'], '8220DB000004')
        self.assertEqual(data[0]['trip_id']['route_id']['route_short_name'], '38a')


