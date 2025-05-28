
from django.urls import path
from .views import requests_page, get_artifacts_description, run_artifact_view, get_response


urlpatterns = [
    path("", requests_page, name='requests'),
    path("get-response/", get_response, name='get-response'),
    path("get_artifact_description/", get_artifacts_description, name='get_artifact_description'),
    path("run_artifact_view/", run_artifact_view, name='run_artifact_view')
]