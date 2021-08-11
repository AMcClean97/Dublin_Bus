from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, SimpleTestCase
from django.shortcuts import reverse


# Create your tests here.

# Haven't trialed this tests, unsure of tables in database as for users but maybe
# first few from https://www.youtube.com/watch?v=UnkayDpqkj8

class LoginTests(SimpleTestCase):
    """ Test Login Page Functionality"""

    def test_status_code(self):
        """check the response of index page"""
        response = self.client.get('login')
        self.assertEquals(response.status_code, 200)

    def test_url_name(self):
        """tests name of home url (seen in urls.py)"""
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)

    def test_template(self):
        """test to see if you go to homepage that index.html is given"""
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')


class RegisterTests(SimpleTestCase):
    """ Test register Page Functionality"""

    def test_status_code(self):
        """check the response of index page"""
        response = self.client.get('register')
        self.assertEquals(response.status_code, 200)

    def test_url_name(self):
        """tests name of home url (seen in urls.py)"""
        response = self.client.get(reverse('register'))
        self.assertEquals(response.status_code, 200)

    def test_template(self):
        """test to see if you go to homepage that index.html is given"""
        response = self.client.get(reverse('register'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')


class FavouritesTests(SimpleTestCase):
    """ Test Favourites Page Functionality"""

    def test_status_code(self):
        """check the response of index page"""
        response = self.client.get('favourites')
        self.assertEquals(response.status_code, 200)

    def test_url_name(self):
        """tests name of home url (seen in urls.py)"""
        response = self.client.get(reverse('favourites'))
        self.assertEquals(response.status_code, 200)

    def test_template(self):
        """test to see if you go to homepage that index.html is given"""
        response = self.client.get(reverse('favourites'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'favourites.html')


# These could be of use
# Gotten from https://www.youtube.com/watch?v=5E_xLmQXOZg
User = get_user_model()


class UserTestCast(TestCase):
    """set up a user login testcase with username and password"""

    def setUP(self):
        user_a = User(username='cfe', email='cfe@invalid.com')
        user_a_pw = 'some_password_123'
        self.user_a_pw = user_a_pw
        user_a.is_staff = True
        user_a.is_superuser = True
        user_a.set_password(user_a_pw)
        self.user_a = user_a

    def test_user_exists(self):
        """test to see if the test user exits"""
        user_count = User.objects.all().count()
        print(user_count)
        self.assertEqual(user_count, 1)
        self.assertNotEqual(user_count, 0)

    def test_user_password(self):
        """test to see if the password is correct"""
        self.assertTrue(self.user_a.check_password(self.user_a_pw))

    def test_login_url(self):
        """test for login functionality """
        # login_url ="users/login"
        # self.assertEqual(settings.LOGIN_URL, login_url)
        login_url = settings.LOGIN_URL  # should be "users/login"
        # response = self.client.post(url, {}, follow=True)
        data = {"username": "cfe", "password": self.user_a_pw}
        response = self.client.post(login_url, data, follow=True)
        # print(dir(response))
        status_code = response.status_code
        redirect_path = response.request.get("PATH_INFO")
        self.assertEqual(redirect_path, settings.LOGIN_REDIRECT_URL)  # such as /index for us??
        # in example he has LOGIN_URL = "/login" and LOGIN_REDIRECT = "/" in the settings.py
        # not sure what is our suss for this
        self.assertEqual(status_code, 200)
