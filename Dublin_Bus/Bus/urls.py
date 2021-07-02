from django.urls import path
from . import views

urlpatterns = [
    path('bus/', views.index),
]
