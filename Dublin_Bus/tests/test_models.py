from django.db.models.query_utils import select_related_descend
from django.test.testcases import TestCase
from users.models import favourite
from Bus.models import Stop, Trip, Calendar, Route, StopTime, CalendarDate
from django.contrib import auth

User = auth.get_user_model()


class TestModels(TestCase):
    def setUp(self):
        user1 = User(username='myname', email='example@gmail.com')
        user1.is_staff = True
        user1.is_superuser = True
        self.passwd = 'password'
        user1.set_password(self.passwd)
        user1.save()
        self.user1 = user1

        self.favourite1 = favourite.objects.create(
            user_id=self.user1.pk,
            origin_name='Shankill, Dublin, Ireland',
            origin_lat=53.2332663,
            origin_lon=-6.1237578,
            destin_name='East Wall, Dublin, Ireland',
            destin_lat=53.3543216,
            destin_lon=-6.2341133,
            stops=0
        )

    def test_favourite_given_name(self):
        self.assertEquals(self.favourite1.favourite_name, "Saved Route")
