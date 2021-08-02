from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fetch_arrivals/', views.fetch_arrivals),
    path('send_to_model', views.send_to_model),
    url(r'^twitter$', views.twitter, name='twitter'),
    url(r'^fare_calculator$', views.fare_calculator, name='fare_calculator')

]
