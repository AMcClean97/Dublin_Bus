from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

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

        self.index_url = self.live_server_url + reverse("index")
        self.login_url = self.live_server_url + reverse("login")
        self.register_url = self.live_server_url + reverse("register")
        self.favourite_url = self.live_server_url + reverse("favourites")

    def tearDown(self) -> None:
        self.browser.close()

    def test_login(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys(self.demo_user.username)
        self.browser.find_element_by_name("password").send_keys(self.demo_passwd)
        self.browser.find_element_by_id('submitButton').click()

        #Goes to index
        self.assertEquals(
            self.browser.current_url,
            self.index_url
        )

        self.assertTrue(
            self.browser.find_element_by_id('logoutButton').is_displayed()
            #idExists(self, 'logoutButton')
        )

        self.assertTrue(
            self.browser.find_element_by_id("fareCalculator").is_displayed()
            #idExists(self, "fareCalculator")
        )


    def test_failed_login(self):
        self.browser.get(self.login_url)
        self.browser.find_element_by_name("username").send_keys("badname")

        self.browser.find_element_by_id('submitButton').click()

        self.assertEquals(
            self.browser.current_url,
            self.login_url
        )

        self.assertTrue(
            self.browser.find_elements_by_class_name("errorBox")[0].is_displayed()
            #classExists(self, "errorBox")
        )

        self.assertEquals(
            self.browser.find_elements_by_class_name("errorBox")[0].text,
            "Username OR Password is incorrect."
        )

    def test_register(self):
        self.browser.get(self.register_url)
        new_user = {
            'username' : 'newguy',
            'email' : 'new@gmail.com',
            'password' : 'testing1234',
        }
        
        self.browser.find_element_by_name("username").send_keys(new_user['username'])
        self.browser.find_element_by_name("email").send_keys(new_user['email'])
        self.browser.find_element_by_name("password1").send_keys(new_user['password'])
        self.browser.find_element_by_name("password2").send_keys(new_user['password'])

        self.browser.find_element_by_id('submitButton').click()

        self.assertEquals(
            self.browser.current_url,
            self.login_url
        )
        self.assertTrue(
            self.browser.find_elements_by_class_name("successBox")[0].is_displayed()
            #classExists(self, "successBox")
        )

        self.assertEquals(
            self.browser.find_elements_by_class_name("successBox")[0].text,
            "Account created for " + new_user['username'] + "."
        )

        self.assertEqual(User.objects.all().count(), 2)

    def test_register_fail(self):
        self.browser.get(self.register_url)
        new_user = {
            'username' : 'newguy',
            'email' : 'new@gmail.com',
            'password1' : 'testing1234',
            'password2' : 'otherpassword',
        }

        self.browser.find_element_by_name("username").send_keys(new_user['username'])
        self.browser.find_element_by_name("email").send_keys(new_user['email'])
        self.browser.find_element_by_name("password1").send_keys(new_user['password1'])
        self.browser.find_element_by_name("password2").send_keys(new_user['password2'])

        self.browser.find_element_by_id('submitButton').click()

        self.assertEquals(
            self.browser.current_url,
            self.register_url
        )
        self.assertTrue(
            self.browser.find_elements_by_class_name("errorBox")[0].is_displayed()
            #classExists(self, "errorBox")
        )

        self.assertEqual(User.objects.all().count(), 1)

    def test_register_password_rules(self):
        self.browser.get(self.register_url)
        wait = WebDriverWait(self.browser, 100)

        self.browser.find_element_by_id('passwordRulesButton').click()

        try: 
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "popover"))
            )
        finally:
            self.assertEquals(
                self.browser.find_element_by_id('PasswordRules').text,
                "Must contain at least 8 characters\nCannot be entirely numeric\nCannot be similar to other info\nCannot be a common password"
            )
