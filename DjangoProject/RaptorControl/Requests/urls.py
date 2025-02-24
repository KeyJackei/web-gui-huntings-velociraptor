
from django.urls import path
from .views import requests

urlpatterns = [
    path("", requests, name='requests.html')
]