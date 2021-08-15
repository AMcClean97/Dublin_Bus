from django.test import TestCase
from Bus.gtfsrealtime import get_arrivals


class TestGtfsrealtime(TestCase):

    """========================= Testing getArrivals ========================="""


    def test_get_arrivals_success(self):
        result = get_arrivals('8220DB000002')
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['delays'], list)
        self.assertLess(len(result['delays']), 4)
        self.assertLess(len(result['delays']), 4)
