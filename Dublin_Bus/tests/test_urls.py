from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Bus.views import index, fetch_arrivals, send_to_model, twitter
from users.views import loginPage, registerPage, logoutUser, favourites, addFavourite, removeFavourite, renameFavourite


#Test that basic URLS are functioning properly
class TestUrls(SimpleTestCase):
    
    # Test Homepage/Map URL
    def test_index(self):
        url = reverse('index')
        self.assertEquals(url, '/')
        self.assertEquals(resolve(url).func, index)

    # Test Twitter Page URL
    def test_twitter(self):
        url = reverse('twitter')
        self.assertEquals(url, '/twitter')
        self.assertEquals(resolve(url).func, twitter)

    # Test Real Time Arrivals URL 
    def test_arrivals(self):
        url = reverse('arrivaltimes')
        self.assertEquals(url, '/fetch_arrivals/')
        self.assertEquals(resolve(url).func, fetch_arrivals)

    # Test Model URL 
    def test_model(self):
        url = reverse('model')
        self.assertEquals(url, '/send_to_model')
        self.assertEquals(resolve(url).func, send_to_model)

    # Test Login Page URL 
    def test_login(self):
        url = reverse('login')
        self.assertEquals(url, '/users/login')
        self.assertEquals(resolve(url).func, loginPage)

    # Test Register Page URL 
    def test_register(self):
        url = reverse('register')
        self.assertEquals(url, '/users/register')
        self.assertEquals(resolve(url).func, registerPage)

    # Test Logout URL 
    def test_logout(self):
        url = reverse('logout')
        self.assertEquals(url, '/users/logout')
        self.assertEquals(resolve(url).func, logoutUser)

    # Test Favourites Page URL
    def test_favourites(self):
        url = reverse('favourites')
        self.assertEquals(url, '/users/favourites')
        self.assertEquals(resolve(url).func, favourites)
    
    # Test Add Favourite URL
    def test_add_favourite(self):
        url = reverse('addFavourite')
        self.assertEquals(url, '/users/favourites/add')
        self.assertEquals(resolve(url).func, addFavourite)

    # Test Remove Favourite URL 
    def test_remove_favourite(self):
        url = reverse('removeFavourite')
        self.assertEquals(url, '/users/favourites/remove')
        self.assertEquals(resolve(url).func, removeFavourite)

    # Test Rename Favourite URL 
    def test_rename_favourite(self):
        url = reverse('renameFavourite')
        self.assertEquals(url, '/users/favourites/rename')
        self.assertEquals(resolve(url).func, renameFavourite)

