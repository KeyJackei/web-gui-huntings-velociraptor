from django.urls import path
from .views import artifacts_view

urlpatterns = [
    path("", artifacts_view, name="make_hunts"),
    path("api/artifacts/", artifacts_api, name="artifacts_api"),
]
