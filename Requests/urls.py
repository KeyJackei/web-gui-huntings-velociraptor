from django.urls import path
from .views import requests_page, get_artifacts_description, run_artifact_view


urlpatterns = [
    path("", requests_page, name='requests'),
    path("get_artifact_description/", get_artifacts_description, name='get_artifact_description'),
    path("run_artifact_view/", run_artifact_view, name='run_artifact_view')
]