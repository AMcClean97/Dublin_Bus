from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from users.models import favourite
from django.urls import reverse
from django.contrib import auth
import time


User = auth.get_user_model()

class FunctionalTests(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('functional_tests/chromedriver.exe')
        demo_user = User(username='myname', email='example@gmail.com')
        demo_user.is_staff = True
        demo_user.is_superuser = True
        self.demo_passwd = 'password'
        demo_user.set_password(self.demo_passwd)
        demo_user.save()
        self.demo_user  = demo_user

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

        destinInput.send_keys("Trinity College")#, College Green, Dublin 2, Ireland")
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





