from django.urls import path

from .views import make_hunts, get_artifact

urlpatterns = [
    path("", make_hunts, name="make_hunts"),
    path("artifact/<str:name>/", get_artifact, name="artifact"),

]
