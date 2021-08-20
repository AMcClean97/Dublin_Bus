from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from users.models import favourite
from django.urls import reverse
from django.contrib import auth

User = auth.get_user_model()


class BaseFunctionalTests(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome('functional_tests/chromedriver.exe')
        demo_user = User(username='myname', email='example@gmail.com')
        demo_user.is_staff = True
        demo_user.is_superuser = True
        self.demo_passwd = 'password'
        demo_user.set_password(self.demo_passwd)
        demo_user.save()
        self.demo_user  = demo_user

        self.index_url = self.live_server_url + reverse("index")
        self.login_url = self.live_server_url + reverse("login")
        self.register_url = self.live_server_url + reverse("register")
        self.favourite_url = self.live_server_url + reverse("favourites")
        self.twitter_url = self.live_server_url + reverse("twitter")

    def test_navbar_index(self):
        self.browser.get(self.login_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_id('menuButton').click()

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "indexLink"))
            )
        finally:
            self.browser.find_element_by_id('indexLink').click()

        self.assertEquals(
            self.browser.current_url,
            self.index_url
        )

    def test_navbar_twitter(self):
        self.browser.get(self.index_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_id('menuButton').click()

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "twitterLink"))
            )
        finally:
            self.browser.find_element_by_id('twitterLink').click()

        self.assertEquals(
            self.browser.current_url,
            self.twitter_url
        )

    def test_navbar_login(self):
        self.browser.get(self.index_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_id('menuButton').click()

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "loginLink"))
            )
        finally:
            self.browser.find_element_by_id('loginLink').click()

        self.assertEquals(
            self.browser.current_url,
            self.login_url
        )

    def test_navbar_register(self):
        self.browser.get(self.index_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_id('menuButton').click()

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "registerLink"))
            )
        finally:
            self.browser.find_element_by_id('registerLink').click()

        self.assertEquals(
            self.browser.current_url,
            self.register_url
        )

    def test_navbar_favourites(self):
        self.browser.get(self.index_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_id('menuButton').click()

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "favouritesLink"))
            )
        finally:
            self.browser.find_element_by_id('favouritesLink').click()

        self.assertEquals(
            self.browser.current_url,
            self.login_url + "?next=/users/favourites"
        )

    def test_navbar_favourites_loggedIn(self):
        self.browser.get(self.login_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.find_element_by_id('menuButton').click()

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "favouritesLink"))
            )
        finally:
            self.browser.find_element_by_id('favouritesLink').click()

            self.assertEquals(
                self.browser.current_url,
                self.favourite_url
            )

    def test_navbar_logout(self):
        self.browser.get(self.login_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.find_element_by_id('menuButton').click()

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "logoutLink"))
            )
        finally:
            self.browser.find_element_by_id('logoutLink').click()

            self.assertEquals(
                self.browser.current_url,
                self.login_url
            )

            self.assertTrue(
                self.browser.find_element_by_id('loginButton').is_displayed()
                #idExists(self, 'loginButton')
            )



    def test_loginButton(self):
        self.browser.get(self.index_url)

        self.browser.find_element_by_id('loginButton').click()

        self.assertEquals(
            self.browser.current_url,
            self.login_url
        )

    def test_logoutButton(self):
        self.browser.get(self.login_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        self.browser.find_element_by_id('logoutButton').click()

        self.assertEquals(
            self.browser.current_url,
            self.login_url
        )

        self.assertTrue(
            self.browser.find_element_by_id('loginButton').is_displayed()
            #idExists(self, 'loginButton')
        )

