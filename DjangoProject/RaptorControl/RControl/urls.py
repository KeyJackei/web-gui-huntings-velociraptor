from django.urls import path
from .views import login_view, main_view


urlpatterns = [
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main')
]
