from django.urls import path
from .views import requests_page, get_response, get_artifacts_description


urlpatterns = [
    path("", requests_page, name='requests'),
    path("get-response/", get_response, name="get_response"),
    path("get_artifact_description/", get_artifacts_description, name='get_artifact_description')
]