from django.urls import path

from .views import make_hunts

urlpatterns = [
    path("", make_hunts, name="make_hunts"),

]
