from django.urls import path
from . import views

urlpatterns = [
    path('bus/', views.index, name= 'index'),
    path('bus/fetch_arrivals/', views.fetch_arrivals),
    path('bus/send_to_model', views.send_to_model),
]
