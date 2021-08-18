from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from Bus.models import Stop
from users.models import favourite
from django.urls import reverse
from django.contrib import auth
import time


User = auth.get_user_model()

class LoginFunctionalTests(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome('functional_tests/chromedriver.exe')
        demo_user = User(username='myname', email='example@gmail.com')
        demo_user.is_staff = True
        demo_user.is_superuser = True
        self.demo_passwd = 'password'
        demo_user.set_password(self.demo_passwd)
        demo_user.save()
        self.demo_user  = demo_user

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

        self.index_url = self.live_server_url + reverse("index")
        self.login_url = self.live_server_url + reverse("login")
        self.register_url = self.live_server_url + reverse("register")
        self.favourite_url = self.live_server_url + reverse("favourites")

    def tearDown(self) -> None:
        self.browser.close()

    def test_favourite_go(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.get(self.favourite_url)

        self.browser.find_element_by_id('goButton' + str(self.demo_favourite.pk)).click()

        self.assertEquals(
            self.browser.current_url,
            self.index_url
        )

        self.assertEquals(
            self.browser.find_element_by_id('inputOrigin').get_attribute("value"),
            self.demo_favourite.origin_name
        )

        self.assertEquals(
            self.browser.find_element_by_id('inputDestin').get_attribute("value"),
            self.demo_favourite.destin_name
        )

        time.sleep(20)
        
        #Check that mapmarkers exist

    def test_favourite_delete(self):

        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.get(self.favourite_url)

        self.browser.find_element_by_id('deleteButton' + str(self.demo_favourite.pk)).click()

        self.assertFalse(
            idExists(self, str(self.demo_favourite.pk))
        )


    def test_favourite_go_bus(self):

        stop1 = Stop(stop_id="8220DB000003", stop_name="Dorset Street Lower, stop 14", stop_lat=53.358531237878196, stop_lon = -6.2627765057086595)
        stop2 = Stop(stop_id="8220DB000014", stop_name="Parnell Square West, stop 3", stop_lat=53.352308551434895, stop_lon = -6.26381074216821)
        
        stop1.save()
        stop2.save()
        
        bus_favourite = favourite(user_id = self.demo_user.pk,
            origin_name= 'Dorset Street Lower, stop 14',
            origin_lat = 53.358531237878196, 
            origin_lon = -6.2627765057086595, 
            destin_name = 'Parnell Square West, stop 3', 
            destin_lat = 53.352308551434895, 
            destin_lon = -6.26381074216821,
            stops = 1
        )

        bus_favourite.save()



        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.get(self.favourite_url)


        self.browser.find_element_by_id('goButton' + str(bus_favourite.pk)).click()

        self.assertEquals(
            self.browser.current_url,
            self.index_url
        )

        self.assertTrue(
            idExists(self, 'inputFirstStop')
        )

        self.assertTrue(
            idExists(self, 'inputLastStop')
        )

        self.assertEquals(
            self.browser.find_element_by_id('inputFirstStop').get_attribute("value"),
            bus_favourite.origin_name
        )

        self.assertEquals(
            self.browser.find_element_by_id('inputLastStop').get_attribute("value"),
            bus_favourite.destin_name
        )

def idExists(self, id):
    try:
        self.browser.find_element_by_id(id)
        return True
    except NoSuchElementException:
        return False