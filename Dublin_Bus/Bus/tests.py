from django.test import TestCase, SimpleTestCase, Client
from django.shortcuts import reverse


# Create your tests here.

# Fall Back if SimpleTestCase wont work

# class SimplerTest(TestCase):
#
#     def setUp(self):
#         self.client = Client()
#
#     def test_index_view(self):
#         url = reverse("index")
#         response = self.client.get(url)
#        self.assertEqual(response.status_code, 200)


class HomePageTests(SimpleTestCase):
    """ Test Home Page Functionality"""

    def test_home_status_code(self):
        """check the response of index page"""
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_home_url_name(self):
        """tests name of index url (seen in urls.py)"""
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)

    def test_correct_template(self):
        """test to see if you go to homepage that index.html is given"""
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class TwitterTests(SimpleTestCase):
    """ Test Twitter Page Functionality"""

    def test_home_status_code(self):
        """check the response of twitter page"""
        response = self.client.get(r'^twitter$')
        self.assertEquals(response.status_code, 200)

    def test_home_url_name(self):
        """tests name of twitter url (seen in urls.py)"""
        response = self.client.get(reverse('twitter'))
        self.assertEquals(response.status_code, 200)

    def test_correct_template(self):
        """test to see if you go to homepage that index.html is given"""
        response = self.client.get(reverse('twitter'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'twitter.html')
