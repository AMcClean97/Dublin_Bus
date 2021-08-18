from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from Bus.models import Stop
from users.models import favourite
from django.urls import reverse
from django.contrib import auth
import time


User = auth.get_user_model()

class IndexFunctionalTests(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('functional_tests/chromedriver.exe')
        demo_user = User(username='myname', email='example@gmail.com')
        demo_user.is_staff = True
        demo_user.is_superuser = True
        self.demo_passwd = 'password'
        demo_user.set_password(self.demo_passwd)
        demo_user.save()
        self.demo_user  = demo_user

        self.login_url = self.live_server_url + reverse("login")

    def tearDown(self) -> None:
        self.browser.close()

    def test_index_noOrigin(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('submitJourneyPlanner').click()
        self.assertEquals(
            self.browser.find_element_by_id('warning').text,
            "Please use a valid starting point."
        )
        self.assertEquals(
            self.browser.find_element_by_id('route_suggestions').text,
            ""
        )

    def test_index_noDestin(self):
        self.browser.get(self.live_server_url)

        wait = WebDriverWait(self.browser, 10)
        originInput = self.browser.find_element_by_id('inputOrigin')

        originInput.send_keys("Rathmines")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()

        time.sleep(3)
        self.browser.find_element_by_id('submitJourneyPlanner').click()

        self.assertEquals(
            self.browser.find_element_by_id('warning').text,
            "Please use a valid destination."
        )
        self.assertEquals(
            self.browser.find_element_by_id('route_suggestions').text,
            ""
        )


    def test_index_submitRoute(self):
        self.browser.get(self.live_server_url)

        wait = WebDriverWait(self.browser, 10)
        originInput = self.browser.find_element_by_id('inputOrigin')
        destinInput = self.browser.find_element_by_id('inputDestin')

        originInput.send_keys("Rathmines")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()

        destinInput.send_keys("Trinity College")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()
            
        time.sleep(3)
        self.browser.find_element_by_id('submitJourneyPlanner').click()
        time.sleep(1)

        self.assertNotEquals(
            self.browser.find_element_by_id('route_suggestions').text,
            ""
        )
        self.assertFalse(
            self.browser.find_element_by_id('warning').is_displayed()
        )

    def test_index_FavouriteButton_noOrigin(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()


        self.browser.find_element_by_id('favouriteButton').click()
        self.assertEquals(
            self.browser.find_element_by_id('warning').text,
            "Please use a valid starting point."
        )
        self.assertEquals(
            self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
            "btn btn-secondary"
        )


        self.assertEqual(favourite.objects.all().count(), 0)

    def test_index_FavouriteButton_noDestin(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        wait = WebDriverWait(self.browser, 10)
        originInput = self.browser.find_element_by_id('inputOrigin')

        originInput.send_keys("Rathmines")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()

        time.sleep(3)
        self.browser.find_element_by_id('favouriteButton').click()

        self.assertEquals(
            self.browser.find_element_by_id('warning').text,
            "Please use a valid destination."
        )
        self.assertEquals(
            self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
            "btn btn-secondary"
        )


        self.assertEqual(favourite.objects.all().count(), 0)


    def test_index_favouriteButton(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        wait = WebDriverWait(self.browser, 10)
        originInput = self.browser.find_element_by_id('inputOrigin')
        destinInput = self.browser.find_element_by_id('inputDestin')

        originInput.send_keys("Rathmines")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()

        destinInput.send_keys("Trinity College")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()
            
        time.sleep(3)
        self.browser.find_element_by_id('favouriteButton').click()
        time.sleep(1)

        self.assertFalse(
            self.browser.find_element_by_id('warning').is_displayed()
        )

        time.sleep(3)
        self.assertEquals(
            self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
            "btn btn-info"
        )

        self.assertEqual(favourite.objects.all().count(), 1)

        self.browser.find_element_by_id('favouriteButton').click()

        time.sleep(3)
        self.assertEquals(
            self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
            "btn btn-secondary"
        )


        self.assertEqual(favourite.objects.all().count(), 0)

    def test_index_alreadyFavourite(self):
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

        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        wait = WebDriverWait(self.browser, 10)
        originInput = self.browser.find_element_by_id('inputOrigin')
        destinInput = self.browser.find_element_by_id('inputDestin')

        originInput.send_keys("Shankill, Dublin,")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()

        destinInput.send_keys("East Wall, Dublin,")
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pac-item"))
            )
        finally:
            self.browser.find_element_by_class_name('pac-item').click()

        time.sleep(3)
        self.assertEquals(
            self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
            "btn btn-info"
        )

class BusIndexFunctionalTests(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('functional_tests/chromedriver.exe')
        demo_user = User(username='myname', email='example@gmail.com')
        demo_user.is_staff = True
        demo_user.is_superuser = True
        self.demo_passwd = 'password'
        demo_user.set_password(self.demo_passwd)
        demo_user.save()
        self.demo_user  = demo_user

        self.login_url = self.live_server_url + reverse("login")

        stop1 = Stop(stop_id="8220DB000003", stop_name="Dorset Street Lower, stop 14", stop_lat=53.358531237878196, stop_lon = -6.2627765057086595)
        stop2 = Stop(stop_id="8220DB000014", stop_name="Parnell Square West, stop 3", stop_lat=53.352308551434895, stop_lon = -6.26381074216821)
        stop1.save()
        stop2.save()

    def tearDown(self) -> None:
        self.browser.close()


    def test_index_noOrigin_stop(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('stops-tab-btn').click()
        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "inputFirstStop"))
            )
        finally:
            self.browser.find_element_by_id('submitJourneyPlanner').click()
            self.assertEquals(
                self.browser.find_element_by_id('warning').text,
                "Please input a valid first stop."
            )
            self.assertEquals(
                self.browser.find_element_by_id('route_suggestions').text,
                ""
            )

    def test_index_noDestin_stop(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('stops-tab-btn').click()

        wait = WebDriverWait(self.browser, 10)

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "inputFirstStop"))
            )
        finally:
            originInput = self.browser.find_element_by_id('inputFirstStop')

            originInput.send_keys("Dorset Street Lower, stop 14")
            self.browser.find_element_by_id('submitJourneyPlanner').click()

            self.assertEquals(
                self.browser.find_element_by_id('warning').text,
                "Please input a valid last stop."
            )
            self.assertEquals(
                self.browser.find_element_by_id('route_suggestions').text,
                ""
            )

    #This one can be somewhat temperamental
    def test_submitRoute_stop(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('stops-tab-btn').click()

        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "inputFirstStop"))
            )
        finally:
            originInput = self.browser.find_element_by_id('inputFirstStop')
            destinInput = self.browser.find_element_by_id('inputLastStop')

            originInput.send_keys("Dorset Street Lower, stop 14")
            destinInput.send_keys("Parnell Square West, stop 3")

            self.browser.find_element_by_id('submitJourneyPlanner').click()

            self.assertFalse(
                self.browser.find_element_by_id('warning').is_displayed()
            )

    def test_index_FavouriteButton_noOrigin_stop(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.find_element_by_id('stops-tab-btn').click()

        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "inputFirstStop"))
            )
        finally:

            self.browser.find_element_by_id('favouriteButton').click()
            self.assertEquals(
                self.browser.find_element_by_id('warning').text,
                "Please input a valid first stop."
            )
            self.assertEquals(
                self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
                "btn btn-secondary"
            )


            self.assertEqual(favourite.objects.all().count(), 0)


    def test_index_FavouriteButton_noDestin_stop(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()
        self.browser.find_element_by_id('stops-tab-btn').click()

        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "inputFirstStop"))
            )
        finally:
            originInput = self.browser.find_element_by_id('inputFirstStop')

            originInput.send_keys("Dorset Street Lower, stop 14")
            self.browser.find_element_by_id('favouriteButton').click()

            self.assertEquals(
                self.browser.find_element_by_id('warning').text,
                "Please input a valid last stop."
            )
            self.assertEquals(
                self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
                "btn btn-secondary"
            )

            self.assertEqual(favourite.objects.all().count(), 0)



    def test_index_favouriteButton_stop(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.find_element_by_id('stops-tab-btn').click()

        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "inputFirstStop"))
            )
        finally:
            originInput = self.browser.find_element_by_id('inputFirstStop')
            destinInput = self.browser.find_element_by_id('inputLastStop')

            originInput.send_keys("Dorset Street Lower, stop 14")
            destinInput.send_keys("Parnell Square West, stop 3")
            
            self.browser.find_element_by_id('favouriteButton').click()

            self.assertFalse(
                self.browser.find_element_by_id('warning').is_displayed()
            )
            time.sleep(3)
            self.assertEquals(
                self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
                "btn btn-info"
            )

            self.assertEqual(favourite.objects.all().count(), 1)

            self.browser.find_element_by_id('favouriteButton').click()

            time.sleep(3)
            self.assertEquals(
                self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
                "btn btn-secondary"
            )


            self.assertEqual(favourite.objects.all().count(), 0)
        

    def test_index_alreadyFavourite_stop(self):
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

        self.browser.find_element_by_id('stops-tab-btn').click()

        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "inputFirstStop"))
            )
        finally:
            originInput = self.browser.find_element_by_id('inputFirstStop')
            destinInput = self.browser.find_element_by_id('inputLastStop')

            originInput.send_keys("Dorset Street Lower, stop 14")
            destinInput.send_keys("Parnell Square West, stop 3")

            time.sleep(1)
            self.assertEquals(
                self.browser.find_element_by_id('favouriteButton').get_attribute('class'),
                "btn btn-info"
            )

    
