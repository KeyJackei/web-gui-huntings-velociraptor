
from django.urls import path
from .views import requests_page, get_response

urlpatterns = [
    path("", requests_page, name='requests.html'),
    path("get-response/", get_response, name="get_response")
]