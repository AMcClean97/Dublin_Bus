from datetime import date
from django.http import response
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.urls.base import resolve
from django.contrib import auth
from Bus.models import Stop, Trip, Calendar, Route, StopTime, CalendarDate
from users.models import favourite

import json

User = auth.get_user_model()

class TestViews(TransactionTestCase):

    def setUp(self):
        #Set up User
        demo_user = User(username='myname', email='example@gmail.com')
        demo_user.is_staff = True
        demo_user.is_superuser = True
        self.demo_passwd = 'password'
        demo_user.set_password(self.demo_passwd)
        demo_user.save()
        self.demo_user  = demo_user

        #create favourite
        demo_favourite = favourite(user_id = self.demo_user.pk,
            origin_name= 'Shankill, Dublin, Ireland',
            origin_lat = 53.2332663, 
            origin_lon = -6.1237578, 
            destin_name = 'East Wall, Dublin, Ireland', 
            destin_lat = 53.3543216, 
            destin_lon = -6.2341133,
            stops = 0
        )

        demo_favourite.save()
        self.demo_favourite = demo_favourite
        return super().setUp()

    """========================= Testing existence of new demo objects ========================="""

    def test_demo_user_exists(self):
        self.assertEqual(User.objects.all().count(), 1)
        self.assertTrue(self.demo_user.check_password(self.demo_passwd))
        self.assertTrue(self.demo_user.is_staff)
        self.assertTrue(self.demo_user.is_superuser)
        self.assertEqual(self.demo_user.username, 'myname')
        self.assertEqual(self.demo_user.email, 'example@gmail.com')

    # Check demo_favourite was created
    def test_demo_favourite(self):
        self.assertEqual(favourite.objects.all().count(), 1)
        self.assertEqual(self.demo_favourite.user, self.demo_user)
        self.assertEqual(self.demo_favourite.origin_name, 'Shankill, Dublin, Ireland')
        self.assertEqual(self.demo_favourite.origin_lat, 53.2332663)
        self.assertEqual(self.demo_favourite.origin_lon, -6.1237578)
        self.assertEqual(self.demo_favourite.destin_name, 'East Wall, Dublin, Ireland')
        self.assertEqual(self.demo_favourite.destin_lat, 53.3543216)
        self.assertEqual(self.demo_favourite.destin_lon, -6.2341133)
        self.assertEqual(self.demo_favourite.stops, 0)

    """========================= Testing index view ========================="""

    def test_index_GET(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'Bus/index.html')

    def test_index_POST(self):
        response = self.client.post(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'Bus/index.html')

    """========================= Testing twitter view ========================="""

    def test_twitter_GET(self):
        response = self.client.get(reverse('twitter'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'Bus/twitter.html')

    """========================= Testing fetch_arrivals view ========================="""

    def test_arrivalTimes_GET(self):
        response = self.client.get(reverse('arrivaltimes'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))


    """========================= Testing send_to_model view ========================="""

    def test_model_GET(self):
        response = self.client.get(reverse('model'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))

    """========================= Testing registerPage view ========================="""

    def test_register_GET(self):
        response = self.client.get(reverse('register'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_loggedin_GET(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        response = self.client.get(reverse('register'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))

    #Check if a new user can be registered
    def test_register_user(self):
        new_user = {
            'username' : 'newguy',
            'email' : 'new@gmail.com',
            'password1' : 'testing1234',
            'password2' : 'testing1234'
        }
        response = self.client.post(reverse('register'), new_user, follow=True)
        redirect_path = response.request.get("PATH_INFO")

        #check redirected to login page
        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

        #Check new user is created
        self.assertEqual(User.objects.all().count(), 2)

        #Check new account message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Account created for ' + new_user['username'] + '.')

    #Check invalid user inputs fails to register new user
    def test_register_fail(self):
        invalid_user = {
            'username' : 'myname',
            'email' : 'example@gmail.com',
            'password1' : 'testing1234',
            'password2' : 'password9876'
        }
        response = self.client.post(reverse('register'), invalid_user, follow=True)
        redirect_path = response.request.get("PATH_INFO")

        #Check that you are redirected back to register page
        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('register'))

        #Check that a new user is not created
        self.assertEqual(User.objects.all().count(), 1)

        #Check that error messages exist
        messages = list(response.context['messages'])
        self.assertTrue(len(messages) > 0)

    """========================= Testing loginPage view ========================="""

    def test_login_GET(self):
        response = self.client.get(reverse('login'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_loggedin_GET(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        response = self.client.get(reverse('login'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))

    def test_login_user(self):
        login_details = {
            "username" : self.demo_user.username,
            "password" : self.demo_passwd
        }
        response = self.client.post(reverse('login'), login_details, follow= True)
        redirect_path = response.request.get("PATH_INFO")

        #Check successful redirect
        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))

        #check user is now logged in
        user = auth.get_user(self.client)
        assert user.is_authenticated

    #Check failed login attempt
    def test_login_fail(self):
        login_details = {
            "username" : self.demo_user.username,
            "password" : "wrong password"
        }
        response = self.client.post(reverse('login'), login_details, follow=True)
        redirect_path = response.request.get("PATH_INFO")

        #redirected back to login
        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

        #Check that error messages exist
        messages = list(response.context['messages'])
        self.assertTrue(len(messages) > 0)

        #check user is not logged in
        user = auth.get_user(self.client)
        assert not user.is_authenticated


    """========================= Testing logoutUser view ========================="""

    def test_logout_GET(self):
        response = self.client.get(reverse('logout'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

    def test_logout(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        response = self.client.get(reverse('logout'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

        #check user is now logged out
        user = auth.get_user(self.client)
        assert not user.is_authenticated

    """========================= Testing favourites view ========================="""

    def test_favourites_GET(self):
        response = self.client.get(reverse('favourites'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

    def test_favourites_loggedin_GET(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        response = self.client.get(reverse('favourites'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/favourites.html')

    """========================= Testing addFavourites view ========================="""

    def test_addFavourite_GET(self):
        response = self.client.get(reverse('addFavourite'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

    def test_addFavourite_loggedin_GET(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        response = self.client.get(reverse('addFavourite'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))

    # Adding a Favourite
    def test_addFavourite(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        new_favourite = {
            'user' : self.demo_user.pk,
            'origin_name' : 'Dorset Street Lower, stop 14',
            'origin_lat' : 53.358531237878196, 
            'origin_lon' : -6.2627765057086595, 
            'destin_name' : 'Parnell Square West, stop 3', 
            'destin_lat' : 53.352308551434895, 
            'destin_lon' : -6.26381074216821,
            'stops' : 1
        }
        response = self.client.post(reverse('addFavourite'), json.dumps(new_favourite), content_type="json")
        data = json.loads(response.content)
        self.assertEquals(data['success'], True)
        self.assertEquals(data['result'], "Favourite added.")

        #Check new favourite details are correct
        data['favourite'].pop('id')
        data['favourite'].pop('favourite_name')
        self.assertEquals(data['favourite'], new_favourite)

        #Check new favourite is created
        self.assertEqual(favourite.objects.all().count(), 2)

    def test_addFavourite_nonexistent_user(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        bad_favourite = {
            'user' : -10,
            'origin_name' : 'Dorset Street Lower, stop 14',
            'origin_lat' : 53.358531237878196, 
            'origin_lon' : -6.2627765057086595, 
            'destin_name' : 'Parnell Square West, stop 3', 
            'destin_lat' : 53.352308551434895, 
            'destin_lon' : -6.26381074216821,
            'stops' : 1
        }
        response = self.client.post(reverse('addFavourite'), json.dumps(bad_favourite), content_type="json")
        data = json.loads(response.content)

        #Check error message
        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR unable to save new favourite.")

        #Check new favourite is not created
        self.assertEqual(favourite.objects.all().count(), 1)

    def test_addFavourite_wrongFormat(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        bad_favourite = {
            "username" : self.demo_user.username,
            "password" : "wrong password"
        }
        response = self.client.post(reverse('addFavourite'), json.dumps(bad_favourite), content_type="json")
        data = json.loads(response.content)

        #Check error message
        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR unable to save new favourite.")

        #Check new favourite is not created
        self.assertEqual(favourite.objects.all().count(), 1)

    def test_addFavourite_notJson(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        bad_favourite = {
            'user' : self.demo_user.pk,
            'origin_name' : 'Dorset Street Lower, stop 14',
            'origin_lat' : 53.358531237878196, 
            'origin_lon' : -6.2627765057086595, 
            'destin_name' : 'Parnell Square West, stop 3', 
            'destin_lat' : 53.352308551434895, 
            'destin_lon' : -6.26381074216821,
            'stops' : 1
        }
        response = self.client.post(reverse('addFavourite'), bad_favourite)
        data = json.loads(response.content)

        #Check error message
        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR input not in JSON format.")

        #Check new favourite is not created
        self.assertEqual(favourite.objects.all().count(), 1)

    def test_addFavourite_duplicate(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        bad_favourite = {
            'user' : self.demo_user.pk,
            'origin_name' : self.demo_favourite.origin_name,
            'origin_lat' : self.demo_favourite.origin_lat, 
            'origin_lon' : self.demo_favourite.origin_lon, 
            'destin_name' : self.demo_favourite.destin_name, 
            'destin_lat' : self.demo_favourite.destin_lat, 
            'destin_lon' : self.demo_favourite.destin_lon,
            'stops' : self.demo_favourite.stops
        }
        response = self.client.post(reverse('addFavourite'), json.dumps(bad_favourite), content_type="json")
        data = json.loads(response.content)

        #Check error message
        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR Duplicate favourite already exists.")

        #Check new favourite is not created
        self.assertEqual(favourite.objects.all().count(), 1)

    """========================= Testing removeFavourites view ========================="""

    def test_removeFavourite_GET(self):
        response = self.client.get(reverse('removeFavourite'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

    def test_removeFavourite_loggedin_GET(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        response = self.client.get(reverse('removeFavourite'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))

    def test_removeFavourite(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        data = { 'id' : self.demo_favourite.pk }
        response = self.client.post(reverse('removeFavourite'), json.dumps(data), content_type="json")
        data = json.loads(response.content)

        self.assertEquals(data['success'], True)
        self.assertEquals(data['result'], "Favourite dropped.")

        self.assertEqual(favourite.objects.all().count(), 0)

    def test_removeFavourite_fail(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        data = { 'id' : -10 }
        response = self.client.post(reverse('removeFavourite'), json.dumps(data), content_type="json")
        data = json.loads(response.content)

        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR could not delete.")
        self.assertEqual(favourite.objects.all().count(), 1)

    def test_removeFavourite_wrongFormat(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        data = { 'testkey' : "testvalue" }
        response = self.client.post(reverse('removeFavourite'), json.dumps(data), content_type="json")
        data = json.loads(response.content)

        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR could not delete.")
        self.assertEqual(favourite.objects.all().count(), 1)

    """========================= Testing renameFavourites view ========================="""

    #Not logged in GET
    def test_renameFavourite_GET(self):
        response = self.client.get(reverse('renameFavourite'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('login'))

    # Logged in Get

    def test_renameFavourite_loggedin_GET(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        response = self.client.get(reverse('renameFavourite'), follow=True)
        redirect_path = response.request.get("PATH_INFO")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect_path, reverse('index'))


    def test_renameFavourite(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        data = { 
            'id' : self.demo_favourite.pk,
            'new_name' : 'New_Name'
        }
        response = self.client.post(reverse('renameFavourite'), json.dumps(data), content_type="json")
        data = json.loads(response.content)

        self.assertEquals(data['success'], True)
        self.assertEquals(data['result'], "Rename successful.")
        self.assertEquals(data['name'], 'New_Name')

    def test_renameFavourite_fail(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        data = { 
            'id' : -10,
            'new_name' : 'New_Name'
        }
        response = self.client.post(reverse('renameFavourite'), json.dumps(data), content_type="json")
        data = json.loads(response.content)

        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR could not rename.")

    def test_renameFavourite_wrongFormat(self):
        self.client.login(username= self.demo_user.username, password=self.demo_passwd)
        data = { 'testkey' : "testvalue" }
        response = self.client.post(reverse('renameFavourite'), json.dumps(data), content_type="json")
        data = json.loads(response.content)

        self.assertEquals(data['success'], False)
        self.assertEquals(data['result'], "ERROR could not rename.")
