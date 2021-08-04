from django.urls import path
from . import views

urlpatterns = [
    path('login', views.loginPage, name='login'),
    path('register', views.registerPage, name ='register'),
    path('logout', views.logoutUser, name='logout'),
    path('favourites', views.favourites, name='favourites'),
    path('favourites/add', views.addFavourite, name = 'addFavourite'),
    path('favourites/remove', views.removeFavourite, name= 'removeFavourite'),
    path('favourites/rename', views.renameFavourite, name= 'renameFavourite'),
]